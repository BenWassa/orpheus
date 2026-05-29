from __future__ import annotations

from datetime import datetime, timezone

from orpheus.pattern.cluster import clusters_status


def _insert_audio_feature(conn, track_uri):
    conn.execute(
        "INSERT OR IGNORE INTO tracks (track_uri, track_name) VALUES (?, 'test')",
        (track_uri,),
    )
    conn.execute(
        """INSERT OR IGNORE INTO audio_features
           (track_uri, source, valence, arousal, fetched_at)
           VALUES (?, 'test', 0.5, 0.5, ?)""",
        (track_uri, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()


def test_clusters_status_no_audio_features(tmp_db):
    assert clusters_status(tmp_db, clusters=[], n_clean_points=0) == "no_audio_features"


def test_clusters_status_insufficient_audio_data(tmp_db):
    _insert_audio_feature(tmp_db, "spotify:track:a")
    assert clusters_status(tmp_db, clusters=[], n_clean_points=0) == "insufficient_audio_data"


def test_clusters_status_no_clusters_found(tmp_db):
    _insert_audio_feature(tmp_db, "spotify:track:a")
    assert clusters_status(tmp_db, clusters=[], n_clean_points=10) == "no_clusters_found"


def test_clusters_status_ok(tmp_db):
    _insert_audio_feature(tmp_db, "spotify:track:a")
    assert clusters_status(tmp_db, clusters=[{"label": "x"}], n_clean_points=10) == "ok"
