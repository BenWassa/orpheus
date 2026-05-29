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
    return {"audio": audio_stats, "lyrics": lyrics_stats}
