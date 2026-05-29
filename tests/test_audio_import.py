from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from orpheus.enrich.audio_import import import_from_csv, import_from_sqlite
from orpheus.enrich.reccobeats import ReccoBeatsClient
from orpheus.pattern.cluster import cluster_gmm, clusters_status, filter_noise
from orpheus.score.emotion import EMOTION_CATEGORIES
from orpheus.score.theme import THEME_CATEGORIES


def _insert_track(conn, spotify_id: str) -> str:
    track_uri = f"spotify:track:{spotify_id}"
    conn.execute(
        """INSERT INTO tracks (track_uri, track_name, primary_artist)
           VALUES (?, ?, ?)""",
        (track_uri, f"Track {spotify_id}", "Artist"),
    )
    conn.commit()
    return track_uri


def _write_csv(path, rows: list[dict]) -> None:
    columns = [
        "id", "valence", "energy", "danceability", "key", "loudness", "mode",
        "speechiness", "acousticness", "instrumentalness", "tempo",
    ]
    lines = [",".join(columns)]
    for row in rows:
        lines.append(",".join(str(row.get(column, "")) for column in columns))
    path.write_text("\n".join(lines))


def test_import_csv_matches_tracks(tmp_db, tmp_path):
    _insert_track(tmp_db, "abc123")
    csv_path = tmp_path / "tracks_features.csv"
    _write_csv(csv_path, [{
        "id": "abc123", "valence": 0.7, "energy": 0.8, "danceability": 0.6,
        "key": 5, "loudness": -6.0, "mode": 1, "acousticness": 0.2,
        "instrumentalness": 0.0, "tempo": 123.4,
    }])

    stats = import_from_csv(tmp_db, csv_path)

    assert stats == {
        "total_source_rows": 1,
        "matched": 1,
        "imported": 1,
        "already_present": 0,
        "unmatched": 0,
    }
    row = tmp_db.execute("SELECT * FROM audio_features WHERE track_uri = ?", ("spotify:track:abc123",)).fetchone()
    assert row["source"] == "kaggle_static"
    assert row["arousal"] == 0.8
    assert row["energy"] == 0.8


def test_import_csv_skips_already_present(tmp_db, tmp_path):
    _insert_track(tmp_db, "abc123")
    csv_path = tmp_path / "tracks_features.csv"
    _write_csv(csv_path, [{"id": "abc123", "valence": 0.7, "energy": 0.8}])

    first = import_from_csv(tmp_db, csv_path)
    second = import_from_csv(tmp_db, csv_path)

    assert first["imported"] == 1
    assert second["imported"] == 0
    assert second["already_present"] == 1
    assert tmp_db.execute("SELECT COUNT(*) FROM audio_features").fetchone()[0] == 1


def test_import_csv_unmatched_not_inserted(tmp_db, tmp_path):
    _insert_track(tmp_db, "known")
    csv_path = tmp_path / "tracks_features.csv"
    _write_csv(csv_path, [{"id": "unknown", "valence": 0.7, "energy": 0.8}])

    stats = import_from_csv(tmp_db, csv_path)

    assert stats["unmatched"] == 1
    assert stats["imported"] == 0
    assert tmp_db.execute("SELECT COUNT(*) FROM audio_features").fetchone()[0] == 0


def test_import_sqlite_matches_tracks(tmp_db, tmp_path):
    _insert_track(tmp_db, "abc123")
    archive_path = tmp_path / "archive.sqlite"
    archive_conn = sqlite3.connect(archive_path)
    archive_conn.execute(
        """CREATE TABLE audio_features (
           track_id TEXT, valence REAL, energy REAL, danceability REAL, tempo REAL
        )"""
    )
    archive_conn.execute(
        "INSERT INTO audio_features VALUES (?, ?, ?, ?, ?)",
        ("abc123", 0.4, 0.5, 0.6, 111.0),
    )
    archive_conn.commit()
    archive_conn.close()

    stats = import_from_sqlite(tmp_db, archive_path)

    assert stats["imported"] == 1
    row = tmp_db.execute("SELECT * FROM audio_features WHERE track_uri = ?", ("spotify:track:abc123",)).fetchone()
    assert row["source"] == "archive"
    assert row["arousal"] == 0.5


def test_reccobeats_client_parses_response(monkeypatch):
    class Response:
        status_code = 200
        headers = {}

        def raise_for_status(self):
            return None

        def json(self):
            return [{
                "href": "https://open.spotify.com/track/abc123",
                "valence": 0.7,
                "energy": 0.8,
                "danceability": 0.6,
                "key": 5,
                "mode": 1,
                "tempo": 123.4,
            }]

    def fake_get(url, params, timeout):
        assert url == ReccoBeatsClient.BASE_URL
        assert params == {"ids": "abc123,missing"}
        assert timeout == 20.0
        return Response()

    monkeypatch.setattr("orpheus.enrich.reccobeats.requests.get", fake_get)

    result = ReccoBeatsClient().fetch_features(["abc123", "missing"])

    assert result["abc123"]["source"] == "reccobeats"
    assert result["abc123"]["arousal"] == 0.8
    assert result["abc123"]["energy"] == 0.8
    assert result["missing"] is None


def test_imported_audio_features_allow_cluster_status_ok(tmp_db, tmp_config, tmp_path):
    tmp_config.clustering.gmm_components = 1
    track_uris = [_insert_track(tmp_db, f"id{i}") for i in range(3)]
    csv_path = tmp_path / "tracks_features.csv"
    _write_csv(csv_path, [
        {"id": "id0", "valence": 0.5, "energy": 0.5, "danceability": 0.5},
        {"id": "id1", "valence": 0.5, "energy": 0.5, "danceability": 0.5},
        {"id": "id2", "valence": 0.5, "energy": 0.5, "danceability": 0.5},
    ])
    import_from_csv(tmp_db, csv_path)

    emotion_scores = {category: 1 / len(EMOTION_CATEGORIES) for category in EMOTION_CATEGORIES}
    theme_scores = {category: 1 / len(THEME_CATEGORIES) for category in THEME_CATEGORIES}
    for track_uri in track_uris:
        tmp_db.execute(
            """INSERT INTO track_scores
               (track_uri, model_version, emotion_scores, theme_scores,
                depth_score, depth_label, confidence, scored_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                track_uri,
                tmp_config.model_version,
                json.dumps(emotion_scores),
                json.dumps(theme_scores),
                0.5,
                "engaged",
                json.dumps({}),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
    tmp_db.commit()

    clean_points, clean_tracks, _ = filter_noise(tmp_db, tmp_config)
    clusters = cluster_gmm(clean_points, clean_tracks, tmp_config)

    assert clusters_status(tmp_db, clusters, len(clean_points)) == "ok"
