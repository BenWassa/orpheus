from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


class ArchiveReader:
    def __init__(self, db_path: Path):
        if not db_path.exists():
            raise FileNotFoundError(f"Archive database not found: {db_path}")
        self._conn = sqlite3.connect(str(db_path))
        self._conn.row_factory = sqlite3.Row

    def lookup(self, track_uri: str | None = None, isrc: str | None = None) -> dict | None:
        if track_uri:
            spotify_id = track_uri.split(":")[-1] if ":" in track_uri else track_uri
            row = self._conn.execute(
                "SELECT * FROM audio_features WHERE spotify_id = ? OR track_id = ?",
                (spotify_id, spotify_id),
            ).fetchone()
            if row:
                return self._row_to_dict(row)

        if isrc:
            row = self._conn.execute(
                "SELECT * FROM audio_features WHERE isrc = ?", (isrc,)
            ).fetchone()
            if row:
                return self._row_to_dict(row)

        return None

    def _row_to_dict(self, row: sqlite3.Row) -> dict:
        cols = {k: row[k] for k in row.keys()}
        return {
            "valence": cols.get("valence"),
            "arousal": cols.get("arousal", cols.get("energy")),
            "tempo": cols.get("tempo"),
            "key": cols.get("key"),
            "mode": cols.get("mode"),
            "energy": cols.get("energy"),
            "danceability": cols.get("danceability"),
            "acousticness": cols.get("acousticness"),
            "instrumentalness": cols.get("instrumentalness"),
            "loudness": cols.get("loudness"),
            "spectral_centroid": cols.get("spectral_centroid"),
            "spectral_complexity": cols.get("spectral_complexity"),
            "source": "archive",
        }

    def close(self):
        self._conn.close()
