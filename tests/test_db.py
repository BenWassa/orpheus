from __future__ import annotations

from orpheus.db import get_schema_version, get_table_counts, run_migrations


def test_schema_created(tmp_db):
    counts = get_table_counts(tmp_db)
    assert counts["plays"] == 0
    assert counts["tracks"] == 0
    assert counts["audio_features"] == 0
    assert counts["lyrics"] == 0
    assert counts["track_scores"] == 0
    assert counts["artists"] == 0
    assert counts["pipeline_runs"] == 0


def test_schema_version_after_init(tmp_db):
    version = get_schema_version(tmp_db)
    assert version >= 0


def test_migrations_idempotent(tmp_db):
    applied_first = run_migrations(tmp_db)
    applied_second = run_migrations(tmp_db)
    assert applied_second == []


def test_wal_mode(tmp_db):
    row = tmp_db.execute("PRAGMA journal_mode").fetchone()
    assert row[0] == "wal"


def test_foreign_keys_on(tmp_db):
    row = tmp_db.execute("PRAGMA foreign_keys").fetchone()
    assert row[0] == 1


def test_plays_table_columns(tmp_db):
    cursor = tmp_db.execute("PRAGMA table_info(plays)")
    columns = {row[1] for row in cursor.fetchall()}
    expected = {"id", "ts", "ms_played", "track_uri", "track_name", "artist_name",
                "album_name", "reason_start", "reason_end", "shuffle", "skipped",
                "source", "ingested_at"}
    assert expected.issubset(columns)


def test_tracks_table_columns(tmp_db):
    cursor = tmp_db.execute("PRAGMA table_info(tracks)")
    columns = {row[1] for row in cursor.fetchall()}
    expected = {"track_uri", "isrc", "track_name", "primary_artist", "album_name",
                "is_instrumental", "enriched_at", "duration_ms"}
    assert expected.issubset(columns)
