from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from orpheus.config import OrpheusConfig
from orpheus.enrich.soundnet import SoundNetClient

logger = logging.getLogger(__name__)


def _insert_audio_features(conn: sqlite3.Connection, track_uri: str, features: dict) -> None:
    conn.execute(
        """INSERT OR IGNORE INTO audio_features
           (track_uri, source, valence, arousal, tempo, key, mode, energy,
            danceability, acousticness, instrumentalness, loudness,
            spectral_centroid, spectral_complexity, fetched_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            track_uri, features.get("source"),
            features.get("valence"), features.get("arousal"),
            features.get("tempo"), features.get("key"), features.get("mode"),
            features.get("energy"), features.get("danceability"),
            features.get("acousticness"), features.get("instrumentalness"),
            features.get("loudness"), features.get("spectral_centroid"),
            features.get("spectral_complexity"),
            datetime.now(timezone.utc).isoformat(),
        ),
    )


def _has_audio_features(conn: sqlite3.Connection, track_uri: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM audio_features WHERE track_uri = ?", (track_uri,)
    ).fetchone()
    return row is not None


def enrich_audio_features(
    conn: sqlite3.Connection,
    config: OrpheusConfig,
    archive_db_path: Path | None = None,
) -> dict:
    tracks = conn.execute(
        "SELECT track_uri, isrc FROM tracks WHERE enriched_at IS NULL"
    ).fetchall()

    if not tracks:
        return {"total": 0, "archive_hits": 0, "soundnet_hits": 0, "missed": 0}

    archive_reader = None
    if archive_db_path and archive_db_path.exists():
        from orpheus.enrich.archive_lookup import ArchiveReader
        try:
            archive_reader = ArchiveReader(archive_db_path)
            logger.info("Archive reader initialized from %s", archive_db_path)
        except Exception as e:
            logger.warning("Failed to open archive DB: %s", e)

    soundnet_client = None
    if config.soundnet.api_key:
        soundnet_client = SoundNetClient(
            api_key=config.soundnet.api_key,
            rate_limit_per_minute=config.soundnet.rate_limit_per_minute,
        )

    stats = {"total": len(tracks), "archive_hits": 0, "soundnet_hits": 0, "missed": 0}

    # Collect URIs not already in archive, then batch-fetch from Spotify
    remaining = []
    for track in tracks:
        track_uri = track["track_uri"]
        isrc = track["isrc"]

        if _has_audio_features(conn, track_uri):
            continue

        features = None

        if archive_reader:
            features = archive_reader.lookup(track_uri=track_uri, isrc=isrc)
            if features:
                _insert_audio_features(conn, track_uri, features)
                stats["archive_hits"] += 1
                continue

        remaining.append(track_uri)

    if soundnet_client and remaining:
        for i, track_uri in enumerate(remaining):
            features = soundnet_client.fetch_audio_features(track_uri)
            if features:
                _insert_audio_features(conn, track_uri, features)
                stats["soundnet_hits"] += 1
            else:
                stats["missed"] += 1
                logger.debug("No audio features found for %s", track_uri)

            if (i + 1) % 100 == 0:
                conn.commit()
                logger.info("SoundNet enrichment: %d/%d tracks", i + 1, len(remaining))

        conn.commit()

    elif not soundnet_client:
        stats["missed"] += len(remaining)

    # Mark all tracks as enriched even if audio features weren't found,
    # so we can proceed to scoring with lyrics-only data
    for track in tracks:
        conn.execute(
            "UPDATE tracks SET enriched_at = ? WHERE track_uri = ? AND enriched_at IS NULL",
            (datetime.now(timezone.utc).isoformat(), track["track_uri"]),
        )
    conn.commit()

    if archive_reader:
        archive_reader.close()

    return stats
