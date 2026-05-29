from __future__ import annotations

import logging
import re
import sqlite3
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class GeniusClient:
    def __init__(self, access_token: str):
        self._token = access_token
        try:
            import lyricsgenius
            self._genius = lyricsgenius.Genius(
                access_token,
                remove_section_headers=False,
                retries=3,
            )
        except ImportError:
            logger.warning("lyricsgenius not installed, lyrics fetching disabled")
            self._genius = None

    def fetch_lyrics(self, track_name: str, artist_name: str) -> dict | None:
        if not self._genius:
            return None

        try:
            song = self._genius.search_song(track_name, artist_name)
            if song is None or song.lyrics is None:
                return {"has_lyrics": False, "raw_text": None, "cleaned_text": None, "annotations": None}

            raw = song.lyrics
            cleaned = clean_lyrics(raw)

            return {
                "has_lyrics": True,
                "raw_text": raw,
                "cleaned_text": cleaned,
                "annotations": None,
            }
        except Exception as e:
            logger.warning("Genius fetch failed for '%s' by '%s': %s", track_name, artist_name, e)
            return None


def clean_lyrics(raw_text: str) -> str:
    text = re.sub(r"\[.*?\]", "", raw_text)
    text = re.sub(r"\d+Embed$", "", text)
    text = re.sub(r"You might also like", "", text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def enrich_lyrics(conn: sqlite3.Connection, access_token: str) -> dict:
    if not access_token:
        return {"total": 0, "fetched": 0, "no_lyrics": 0, "failed": 0}

    tracks_needing_lyrics = conn.execute(
        """SELECT t.track_uri, t.track_name, t.primary_artist
           FROM tracks t
           LEFT JOIN lyrics l ON t.track_uri = l.track_uri
           WHERE l.track_uri IS NULL"""
    ).fetchall()

    if not tracks_needing_lyrics:
        return {"total": 0, "fetched": 0, "no_lyrics": 0, "failed": 0}

    client = GeniusClient(access_token)
    stats = {"total": len(tracks_needing_lyrics), "fetched": 0, "no_lyrics": 0, "failed": 0}

    for i, track in enumerate(tracks_needing_lyrics):
        track_uri = track["track_uri"]

        result = client.fetch_lyrics(track["track_name"], track["primary_artist"])

        if result is None:
            stats["failed"] += 1
            conn.execute(
                """INSERT OR IGNORE INTO lyrics (track_uri, has_lyrics, fetched_at)
                   VALUES (?, ?, ?)""",
                (track_uri, False, datetime.now(timezone.utc).isoformat()),
            )
        elif result["has_lyrics"]:
            stats["fetched"] += 1
            conn.execute(
                """INSERT OR IGNORE INTO lyrics
                   (track_uri, raw_text, cleaned_text, annotations, has_lyrics, fetched_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    track_uri, result["raw_text"], result["cleaned_text"],
                    result["annotations"], True,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
        else:
            stats["no_lyrics"] += 1
            conn.execute(
                """INSERT OR IGNORE INTO lyrics (track_uri, has_lyrics, fetched_at)
                   VALUES (?, ?, ?)""",
                (track_uri, False, datetime.now(timezone.utc).isoformat()),
            )

        if (i + 1) % 50 == 0:
            conn.commit()
            logger.info("Lyrics: %d/%d tracks", i + 1, len(tracks_needing_lyrics))

    conn.commit()
    return stats
