from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone

from orpheus.config import OrpheusConfig
from orpheus.enrich.enrich import enrich_audio_features
from orpheus.enrich.genius import enrich_lyrics

logger = logging.getLogger(__name__)


def run_enrichment(conn: sqlite3.Connection, config: OrpheusConfig) -> dict:
    audio_stats = enrich_audio_features(conn, config)
    lyrics_stats = enrich_lyrics(conn, config.genius.access_token)

    _mark_enriched(conn)

    return {"audio": audio_stats, "lyrics": lyrics_stats}


def _mark_enriched(conn: sqlite3.Connection) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """UPDATE tracks SET enriched_at = ?
           WHERE enriched_at IS NULL
           AND track_uri IN (SELECT track_uri FROM audio_features)""",
        (now,),
    )
    conn.commit()
