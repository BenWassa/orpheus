from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timezone

from orpheus.config import OrpheusConfig
from orpheus.score.depth import score_depth
from orpheus.score.emotion import EmotionScorer
from orpheus.score.theme import ThemeScorer

logger = logging.getLogger(__name__)


def run_scoring(conn: sqlite3.Connection, config: OrpheusConfig) -> dict:
    model_version = config.model_version

    tracks = conn.execute(
        """SELECT t.track_uri
           FROM tracks t
           WHERE t.enriched_at IS NOT NULL
           AND NOT EXISTS (
               SELECT 1 FROM track_scores ts
               WHERE ts.track_uri = t.track_uri AND ts.model_version = ?
           )""",
        (model_version,),
    ).fetchall()

    if not tracks:
        return {"scored": 0, "skipped": 0, "total": 0}

    emotion_scorer = EmotionScorer(config.models.emotion_classifier)
    theme_scorer = ThemeScorer(config.models.semantic_embedding)

    scored = 0
    for i, track_row in enumerate(tracks):
        track_uri = track_row["track_uri"]

        audio_row = conn.execute(
            "SELECT * FROM audio_features WHERE track_uri = ?", (track_uri,)
        ).fetchone()
        audio_features = dict(audio_row) if audio_row else None

        lyrics_row = conn.execute(
            "SELECT cleaned_text, has_lyrics FROM lyrics WHERE track_uri = ?", (track_uri,)
        ).fetchone()
        lyrics_text = lyrics_row["cleaned_text"] if lyrics_row and lyrics_row["has_lyrics"] else None

        artist_row = conn.execute(
            """SELECT a.canonical_themes FROM artists a
               JOIN tracks t ON t.primary_artist = a.artist_name
               WHERE t.track_uri = ?""",
            (track_uri,),
        ).fetchone()
        artist_prior = json.loads(artist_row["canonical_themes"]) if artist_row and artist_row["canonical_themes"] else None

        emotion_result = emotion_scorer.score_track(audio_features, lyrics_text)
        theme_result = theme_scorer.score_track(lyrics_text, artist_prior, audio_features)

        depth_score, depth_label = score_depth(
            audio_features, lyrics_text, theme_result["theme_scores"], config.depth_labels
        )

        confidence = {
            "emotion": emotion_result["confidence"],
            "theme": theme_result["confidence"],
            "depth": 0.5 + 0.3 * (1 if audio_features else 0) + 0.2 * (1 if lyrics_text else 0),
        }

        conn.execute(
            """INSERT OR REPLACE INTO track_scores
               (track_uri, model_version, emotion_scores, theme_scores,
                depth_score, depth_label, confidence, scored_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                track_uri, model_version,
                json.dumps(emotion_result["emotion_scores"]),
                json.dumps(theme_result["theme_scores"]),
                depth_score, depth_label,
                json.dumps(confidence),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        scored += 1

        if (i + 1) % 50 == 0:
            conn.commit()
            logger.info("Scored %d/%d tracks", i + 1, len(tracks))

    conn.commit()
    _update_artist_priors(conn)

    return {"scored": scored, "skipped": 0, "total": len(tracks)}


def _update_artist_priors(conn: sqlite3.Connection) -> None:
    artists = conn.execute(
        """SELECT DISTINCT t.primary_artist
           FROM tracks t
           JOIN track_scores ts ON t.track_uri = ts.track_uri"""
    ).fetchall()

    now = datetime.now(timezone.utc).isoformat()

    for artist_row in artists:
        artist_name = artist_row["primary_artist"]

        scores_rows = conn.execute(
            """SELECT ts.theme_scores
               FROM track_scores ts
               JOIN tracks t ON ts.track_uri = t.track_uri
               WHERE t.primary_artist = ?""",
            (artist_name,),
        ).fetchall()

        if not scores_rows:
            continue

        from orpheus.score.theme import THEME_CATEGORIES
        agg = {cat: 0.0 for cat in THEME_CATEGORIES}
        count = 0
        for row in scores_rows:
            themes = json.loads(row["theme_scores"])
            for cat in THEME_CATEGORIES:
                agg[cat] += themes.get(cat, 0.0)
            count += 1

        if count > 0:
            agg = {k: v / count for k, v in agg.items()}

        play_count = conn.execute(
            "SELECT COUNT(*) FROM plays WHERE artist_name = ?", (artist_name,)
        ).fetchone()[0]

        conn.execute(
            """INSERT OR REPLACE INTO artists
               (artist_name, canonical_themes, play_count, updated_at)
               VALUES (?, ?, ?, ?)""",
            (artist_name, json.dumps(agg), play_count, now),
        )

    conn.commit()
