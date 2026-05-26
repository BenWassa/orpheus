from __future__ import annotations

import json
from pathlib import Path

import pytest

from orpheus.ingest.spotify_export import ingest_export


def test_ingest_fixture(tmp_db, sample_export_path):
    stats = ingest_export(sample_export_path, tmp_db)
    # 8 entries in fixture, 1 is podcast (null uri) → 7 valid plays
    assert stats["plays_inserted"] == 7
    assert stats["duplicates_skipped"] == 0


def test_ingest_unique_tracks(tmp_db, sample_export_path):
    ingest_export(sample_export_path, tmp_db)
    track_count = tmp_db.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]
    # 6 unique track URIs in fixture (Runaway appears twice but same URI, podcast filtered)
    assert track_count == 6


def test_ingest_idempotent(tmp_db, sample_export_path):
    stats1 = ingest_export(sample_export_path, tmp_db)
    stats2 = ingest_export(sample_export_path, tmp_db)
    assert stats2["plays_inserted"] == 0
    assert stats2["duplicates_skipped"] == stats1["plays_inserted"]


def test_ingest_play_fields(tmp_db, sample_export_path):
    ingest_export(sample_export_path, tmp_db)
    row = tmp_db.execute(
        "SELECT * FROM plays WHERE track_name = 'Runaway' ORDER BY ts LIMIT 1"
    ).fetchone()
    assert row["artist_name"] == "Kanye West"
    assert row["album_name"] == "My Beautiful Dark Twisted Fantasy"
    assert row["ms_played"] == 245000
    assert row["source"] == "export"
    assert row["shuffle"] == 0  # False stored as 0
    assert row["skipped"] == 0


def test_ingest_skipped_track(tmp_db, sample_export_path):
    ingest_export(sample_export_path, tmp_db)
    row = tmp_db.execute(
        "SELECT * FROM plays WHERE track_name = 'Bodak Yellow'"
    ).fetchone()
    assert row["skipped"] == 1
    assert row["shuffle"] == 1
    assert row["ms_played"] == 15000


def test_ingest_filters_podcasts(tmp_db, sample_export_path):
    ingest_export(sample_export_path, tmp_db)
    null_uri = tmp_db.execute(
        "SELECT COUNT(*) FROM plays WHERE track_uri IS NULL"
    ).fetchone()[0]
    assert null_uri == 0


def test_ingest_directory(tmp_db, tmp_path, sample_export_path):
    import shutil
    dest = tmp_path / "exports"
    dest.mkdir()
    shutil.copy(sample_export_path, dest / "export_2025.json")

    stats = ingest_export(dest, tmp_db)
    assert stats["plays_inserted"] == 7
    assert stats["files_processed"] == 1


def test_ingest_bad_json(tmp_db, tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not valid json {{{")

    stats = ingest_export(bad_file, tmp_db)
    assert stats["plays_inserted"] == 0


def test_ingest_empty_array(tmp_db, tmp_path):
    empty_file = tmp_path / "empty.json"
    empty_file.write_text("[]")

    stats = ingest_export(empty_file, tmp_db)
    assert stats["plays_inserted"] == 0


def test_ingest_track_upsert(tmp_db, sample_export_path):
    ingest_export(sample_export_path, tmp_db)
    row = tmp_db.execute(
        "SELECT * FROM tracks WHERE track_uri = 'spotify:track:3DK6m7It6Pw857FcQftMds'"
    ).fetchone()
    assert row["track_name"] == "Runaway"
    assert row["primary_artist"] == "Kanye West"
