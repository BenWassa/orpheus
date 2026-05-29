from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from typing import Any

from orpheus.enrich.enrich import _has_audio_features, _insert_audio_features


TRACK_ID_COLUMNS = ("id", "track_id", "spotify_id")


def spotify_id_from_track_uri(track_uri: str | None) -> str | None:
    if not track_uri:
        return None
    value = track_uri.strip()
    if not value:
        return None
    if value.startswith("spotify:track:"):
        return value.rsplit(":", 1)[-1]
    if "/track/" in value:
        return value.rstrip("/").rsplit("/", 1)[-1].split("?", 1)[0]
    return value


def _load_tracks_index(conn: sqlite3.Connection) -> dict[str, str]:
    rows = conn.execute("SELECT track_uri FROM tracks WHERE track_uri IS NOT NULL").fetchall()
    index: dict[str, str] = {}
    for row in rows:
        track_uri = row["track_uri"]
        spotify_id = spotify_id_from_track_uri(track_uri)
        if spotify_id:
            index[spotify_id] = track_uri
    return index


def import_from_csv(conn: sqlite3.Connection, path: Path) -> dict:
    tracks_index = _load_tracks_index(conn)
    stats = _empty_stats()

    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        id_column = _find_id_column(reader.fieldnames or [])
        if id_column is None:
            raise ValueError(
                "CSV must include one of these Spotify ID columns: "
                + ", ".join(TRACK_ID_COLUMNS)
            )

        for row in reader:
            stats["total_source_rows"] += 1
            spotify_id = _clean_value(row.get(id_column))
            if not spotify_id:
                stats["unmatched"] += 1
                continue

            track_uri = tracks_index.get(spotify_id)
            if track_uri is None:
                stats["unmatched"] += 1
                continue

            stats["matched"] += 1
            if _has_audio_features(conn, track_uri):
                stats["already_present"] += 1
                continue

            _insert_audio_features(conn, track_uri, _features_from_mapping(row, source="kaggle_static"))
            stats["imported"] += 1

    conn.commit()
    return stats


def import_from_sqlite(conn: sqlite3.Connection, path: Path) -> dict:
    tracks_index = _load_tracks_index(conn)
    stats = _empty_stats()

    archive_conn = sqlite3.connect(str(path))
    archive_conn.row_factory = sqlite3.Row
    try:
        columns = _sqlite_columns(archive_conn, "audio_features")
        id_column = _find_id_column(columns)
        if id_column is None:
            raise ValueError(
                "Archive audio_features table must include one of these Spotify ID columns: "
                + ", ".join(TRACK_ID_COLUMNS)
            )

        for row in archive_conn.execute("SELECT * FROM audio_features"):
            stats["total_source_rows"] += 1
            row_dict = dict(row)
            spotify_id = _clean_value(row_dict.get(id_column))
            if not spotify_id:
                stats["unmatched"] += 1
                continue

            track_uri = tracks_index.get(spotify_id)
            if track_uri is None:
                stats["unmatched"] += 1
                continue

            stats["matched"] += 1
            if _has_audio_features(conn, track_uri):
                stats["already_present"] += 1
                continue

            _insert_audio_features(
                conn,
                track_uri,
                _features_from_mapping(row_dict, source="archive", use_row_source=True),
            )
            stats["imported"] += 1
    finally:
        archive_conn.close()

    conn.commit()
    return stats


def _empty_stats() -> dict:
    return {
        "total_source_rows": 0,
        "matched": 0,
        "imported": 0,
        "already_present": 0,
        "unmatched": 0,
    }


def _find_id_column(columns: list[str]) -> str | None:
    normalized = {c.lower(): c for c in columns}
    for candidate in TRACK_ID_COLUMNS:
        if candidate in normalized:
            return normalized[candidate]
    return None


def _features_from_mapping(row: dict[str, Any], source: str, use_row_source: bool = False) -> dict:
    energy = _as_float(row.get("energy"))
    arousal = _as_float(row.get("arousal"))
    return {
        "valence": _as_float(row.get("valence")),
        "arousal": arousal if arousal is not None else energy,
        "tempo": _as_float(row.get("tempo")),
        "key": _as_int(row.get("key")),
        "mode": _as_int(row.get("mode")),
        "energy": energy,
        "danceability": _as_float(row.get("danceability")),
        "acousticness": _as_float(row.get("acousticness")),
        "instrumentalness": _as_float(row.get("instrumentalness")),
        "loudness": _as_float(row.get("loudness")),
        "spectral_centroid": _as_float(row.get("spectral_centroid")),
        "spectral_complexity": _as_float(row.get("spectral_complexity")),
        "source": (_clean_value(row.get("source")) if use_row_source else None) or source,
    }


def _sqlite_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    if not rows:
        raise ValueError(f"Archive SQLite database does not contain table: {table}")
    return [row["name"] for row in rows]


def _clean_value(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _as_float(value: Any) -> float | None:
    text = _clean_value(value)
    if text is None:
        return None
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def _as_int(value: Any) -> int | None:
    text = _clean_value(value)
    if text is None:
        return None
    try:
        return int(float(text))
    except (TypeError, ValueError):
        return None
