from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timezone

from orpheus.aggregate.decay import engagement_weight, time_decay_weight
from orpheus.config import OrpheusConfig
from orpheus.score.emotion import EMOTION_CATEGORIES
from orpheus.score.theme import THEME_CATEGORIES

logger = logging.getLogger(__name__)


def aggregate_window(
    conn: sqlite3.Connection,
    t_now: datetime,
    half_life_days: float,
    config: OrpheusConfig,
) -> dict:
    rows = conn.execute(
        """SELECT p.ts, p.ms_played, p.track_uri, p.reason_start, p.reason_end,
                  p.shuffle, p.skipped,
                  t.duration_ms, t.track_name, t.primary_artist, t.album_name,
                  ts.emotion_scores, ts.theme_scores, ts.depth_score
           FROM plays p
           JOIN tracks t ON p.track_uri = t.track_uri
           JOIN track_scores ts ON p.track_uri = ts.track_uri
           ORDER BY p.ts DESC"""
    ).fetchall()

    emotion_agg = {cat: 0.0 for cat in EMOTION_CATEGORIES}
    theme_agg = {cat: 0.0 for cat in THEME_CATEGORIES}
    depth_weighted_sum = 0.0
    total_weight = 0.0

    artist_weights: dict[str, float] = {}
    track_weights: dict[str, float] = {}
    track_info: dict[str, dict] = {}

    ew_dict = {
        "full_play": config.engagement_weights.full_play,
        "partial_play": config.engagement_weights.partial_play,
        "early_skip": config.engagement_weights.early_skip,
        "boundary_skip": config.engagement_weights.boundary_skip,
        "shuffle_source": config.engagement_weights.shuffle_source,
        "library_play": config.engagement_weights.library_play,
    }

    for row in rows:
        t_play = datetime.fromisoformat(row["ts"].replace("Z", "+00:00"))
        if t_play.tzinfo is None:
            t_play = t_play.replace(tzinfo=timezone.utc)

        w0 = engagement_weight(
            ms_played=row["ms_played"],
            duration_ms=row["duration_ms"],
            reason_end=row["reason_end"],
            shuffle=bool(row["shuffle"]),
            skipped=bool(row["skipped"]),
            reason_start=row["reason_start"],
            engagement_weights=ew_dict,
        )

        w = time_decay_weight(t_play, t_now, half_life_days, w0)

        if w <= 0:
            continue

        emotions = json.loads(row["emotion_scores"])
        themes = json.loads(row["theme_scores"])

        for cat in EMOTION_CATEGORIES:
            emotion_agg[cat] += w * emotions.get(cat, 0.0)

        for cat in THEME_CATEGORIES:
            theme_agg[cat] += w * themes.get(cat, 0.0)

        depth = row["depth_score"] or 0.5
        depth_weighted_sum += w * depth
        total_weight += w

        artist = row["primary_artist"]
        if artist:
            artist_weights[artist] = artist_weights.get(artist, 0.0) + w

        track_uri = row["track_uri"]
        track_weights[track_uri] = track_weights.get(track_uri, 0.0) + w

        if track_uri not in track_info:
            track_info[track_uri] = {
                "uri": track_uri,
                "name": row["track_name"],
                "artist": row["primary_artist"],
                "album": row["album_name"],
                "depth_score": row["depth_score"],
                "emotion_scores": emotions,
                "theme_scores": themes,
            }

    emotion_total = sum(emotion_agg.values())
    if emotion_total > 0:
        emotion_agg = {k: v / emotion_total for k, v in emotion_agg.items()}

    theme_total = sum(theme_agg.values())
    if theme_total > 0:
        theme_agg = {k: v / theme_total for k, v in theme_agg.items()}

    avg_depth = depth_weighted_sum / total_weight if total_weight > 0 else 0.5

    top_emotions = sorted(emotion_agg.items(), key=lambda x: x[1], reverse=True)
    top_themes = sorted(theme_agg.items(), key=lambda x: x[1], reverse=True)
    top_artists = sorted(artist_weights.items(), key=lambda x: x[1], reverse=True)[:10]
    top_tracks = sorted(track_weights.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "emotions": dict(top_emotions),
        "themes": dict(top_themes),
        "avg_depth": avg_depth,
        "top_artists": [{"artist": a, "weight": w} for a, w in top_artists],
        "top_tracks": [
            {**track_info[t], "weight": w} for t, w in top_tracks
        ],
        "total_weight": total_weight,
        "play_count": len(rows),
    }


def compute_state_and_trait(conn: sqlite3.Connection, config: OrpheusConfig) -> dict:
    t_now = datetime.now(timezone.utc)

    state = aggregate_window(conn, t_now, config.windows.state_half_life_days, config)
    trait = aggregate_window(conn, t_now, config.windows.trait_half_life_days, config)

    return {"state": state, "trait": trait, "computed_at": t_now.isoformat()}
