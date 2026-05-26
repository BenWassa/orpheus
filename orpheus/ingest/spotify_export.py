from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

_FIELD_MAP = {
    "ts": "ts",
    "ms_played": "ms_played",
    "master_metadata_track_name": "track_name",
    "master_metadata_album_artist_name": "artist_name",
    "master_metadata_album_album_name": "album_name",
    "spotify_track_uri": "track_uri",
    "reason_start": "reason_start",
    "reason_end": "reason_end",
    "shuffle": "shuffle",
    "skipped": "skipped",
}


def _parse_export_file(path: Path) -> list[dict]:
    with open(path) as f:
        raw = json.load(f)

    if not isinstance(raw, list):
        logger.warning("Expected JSON array in %s, skipping", path)
        return []

    plays = []
    for entry in raw:
        track_uri = entry.get("spotify_track_uri")
        if not track_uri:
            continue

        play = {}
        for src_key, dst_key in _FIELD_MAP.items():
            play[dst_key] = entry.get(src_key)

        play["source"] = "export"
        play["ingested_at"] = datetime.now(timezone.utc).isoformat()
        plays.append(play)

    return plays


def _play_exists(conn: sqlite3.Connection, ts: str, track_uri: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM plays WHERE ts = ? AND track_uri = ?", (ts, track_uri)
    ).fetchone()
    return row is not None


def _upsert_track(conn: sqlite3.Connection, play: dict) -> None:
    existing = conn.execute(
        "SELECT 1 FROM tracks WHERE track_uri = ?", (play["track_uri"],)
    ).fetchone()
    if existing:
        return

    conn.execute(
        """INSERT INTO tracks (track_uri, track_name, primary_artist, album_name)
           VALUES (?, ?, ?, ?)""",
        (play["track_uri"], play["track_name"], play["artist_name"], play["album_name"]),
    )


def ingest_export(source: Path, conn: sqlite3.Connection) -> dict:
    if source.is_file():
        files = [source]
    elif source.is_dir():
        files = sorted(source.glob("*.json"))
    else:
        raise FileNotFoundError(f"Source not found: {source}")

    if not files:
        raise FileNotFoundError(f"No JSON files found in {source}")

    plays_inserted = 0
    duplicates_skipped = 0
    tracks_resolved = 0
    tracks_seen: set[str] = set()

    for file_path in files:
        logger.info("Parsing %s", file_path.name)
        try:
            plays = _parse_export_file(file_path)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning("Skipping %s: %s", file_path.name, e)
            continue

        for play in plays:
            if _play_exists(conn, play["ts"], play["track_uri"]):
                duplicates_skipped += 1
                continue

            conn.execute(
                """INSERT INTO plays (ts, ms_played, track_uri, track_name, artist_name,
                   album_name, reason_start, reason_end, shuffle, skipped, source, ingested_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    play["ts"], play["ms_played"], play["track_uri"],
                    play["track_name"], play["artist_name"], play["album_name"],
                    play["reason_start"], play["reason_end"],
                    play["shuffle"], play["skipped"],
                    play["source"], play["ingested_at"],
                ),
            )
            plays_inserted += 1

            if play["track_uri"] not in tracks_seen:
                before = conn.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]
                _upsert_track(conn, play)
                after = conn.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]
                if after > before:
                    tracks_resolved += 1
                tracks_seen.add(play["track_uri"])

    conn.commit()

    return {
        "plays_inserted": plays_inserted,
        "tracks_resolved": tracks_resolved,
        "duplicates_skipped": duplicates_skipped,
        "files_processed": len(files),
    }
