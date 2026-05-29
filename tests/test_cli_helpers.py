from __future__ import annotations

from orpheus.cli import _missing_audio_feature_tracks


def test_missing_audio_feature_tracks_lists_only_gaps(tmp_db):
    tmp_db.execute(
        """INSERT INTO tracks (track_uri, track_name, primary_artist, album_name)
           VALUES (?, ?, ?, ?)""",
        ("spotify:track:missing", "Missing Song", "Missing Artist", "Missing Album"),
    )
    tmp_db.execute(
        """INSERT INTO tracks (track_uri, track_name, primary_artist, album_name)
           VALUES (?, ?, ?, ?)""",
        ("spotify:track:present", "Present Song", "Present Artist", "Present Album"),
    )
    tmp_db.execute(
        """INSERT INTO audio_features (track_uri, source, valence, arousal, fetched_at)
           VALUES (?, ?, ?, ?, ?)""",
        ("spotify:track:present", "test", 0.5, 0.5, "2026-05-29T00:00:00Z"),
    )
    tmp_db.commit()

    rows = _missing_audio_feature_tracks(tmp_db)

    assert rows == [{
        "track_uri": "spotify:track:missing",
        "track_name": "Missing Song",
        "primary_artist": "Missing Artist",
        "album_name": "Missing Album",
    }]


def test_missing_audio_feature_tracks_respects_limit(tmp_db):
    for index in range(3):
        tmp_db.execute(
            """INSERT INTO tracks (track_uri, track_name, primary_artist, album_name)
               VALUES (?, ?, ?, ?)""",
            (f"spotify:track:{index}", f"Track {index}", "Artist", "Album"),
        )
    tmp_db.commit()

    rows = _missing_audio_feature_tracks(tmp_db, limit=2)

    assert len(rows) == 2
