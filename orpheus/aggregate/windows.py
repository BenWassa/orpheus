from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timedelta, timezone

from orpheus.aggregate.decay import engagement_weight, time_decay_weight
from orpheus.config import OrpheusConfig
from orpheus.score.emotion import EMOTION_CATEGORIES
from orpheus.score.theme import THEME_CATEGORIES

logger = logging.getLogger(__name__)

FREQUENCY_WINDOW_HALF_LIVES = 4
QUALIFIED_LISTEN_MS = 30_000


def _parse_ts(ts: str) -> datetime:
    t_play = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if t_play.tzinfo is None:
        t_play = t_play.replace(tzinfo=timezone.utc)
    return t_play


def _is_qualified_frequency_play(ms_played: int | None) -> bool:
    return (ms_played or 0) >= QUALIFIED_LISTEN_MS


def _parse_confidence(value) -> float:
    """Coerce the TEXT confidence column to a [0,1] multiplier.

    Missing or unparseable confidence is treated as neutral (1.0) so legacy
    rows without a confidence value are not silently penalised.
    """
    if value is None:
        return 1.0
    try:
        c = float(value)
    except (TypeError, ValueError):
        return 1.0
    return max(0.0, min(1.0, c))


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
                  ts.emotion_scores, ts.theme_scores, ts.depth_score, ts.confidence
           FROM plays p
           JOIN tracks t ON p.track_uri = t.track_uri
           JOIN track_scores ts ON p.track_uri = ts.track_uri
                              AND ts.model_version = ?
           ORDER BY p.ts DESC""",
        (config.model_version,),
    ).fetchall()
    play_rows = conn.execute(
        """SELECT p.ts, p.ms_played, p.track_uri,
                  t.track_name, t.primary_artist, t.album_name
           FROM plays p
           JOIN tracks t ON p.track_uri = t.track_uri
           ORDER BY p.ts DESC"""
    ).fetchall()

    emotion_agg = {cat: 0.0 for cat in EMOTION_CATEGORIES}
    theme_agg = {cat: 0.0 for cat in THEME_CATEGORIES}
    depth_weighted_sum = 0.0
    total_weight = 0.0

    artist_weights: dict[str, float] = {}
    track_weights: dict[str, float] = {}
    track_play_counts: dict[str, int] = {}
    track_info: dict[str, dict] = {}
    frequency_counts: dict[str, int] = {}
    frequency_latest: dict[str, str] = {}
    frequency_info: dict[str, dict] = {}

    ew_dict = {
        "full_play": config.engagement_weights.full_play,
        "partial_play": config.engagement_weights.partial_play,
        "early_skip": config.engagement_weights.early_skip,
        "boundary_skip": config.engagement_weights.boundary_skip,
        "shuffle_source": config.engagement_weights.shuffle_source,
        "library_play": config.engagement_weights.library_play,
    }

    for row in rows:
        t_play = _parse_ts(row["ts"])

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

        if w == 0:
            continue

        emotions = json.loads(row["emotion_scores"])
        themes = json.loads(row["theme_scores"])

        artist = row["primary_artist"]
        if artist:
            artist_weights[artist] = artist_weights.get(artist, 0.0) + w

        track_uri = row["track_uri"]
        track_weights[track_uri] = track_weights.get(track_uri, 0.0) + w
        track_play_counts[track_uri] = track_play_counts.get(track_uri, 0) + 1

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

        # Negative engagement is anti-evidence for ranking tracks/artists, but
        # should not subtract a skipped track's profile from the mood mixture.
        if w <= 0:
            continue

        # Down-weight the mood mixture by per-track classification confidence so
        # that low-confidence scores (e.g. the 0.1 uniform fallback when neither
        # audio features nor lyrics were available) don't drag every window
        # toward uniform. Track/artist *ranking* stays on pure engagement (w) —
        # how much you engaged is independent of how sure we are about the mood.
        wm = w * _parse_confidence(row["confidence"])

        for cat in EMOTION_CATEGORIES:
            emotion_agg[cat] += wm * emotions.get(cat, 0.0)

        for cat in THEME_CATEGORIES:
            theme_agg[cat] += wm * themes.get(cat, 0.0)

        depth = row["depth_score"] or 0.5
        depth_weighted_sum += wm * depth
        total_weight += wm

    emotion_total = sum(emotion_agg.values())
    if emotion_total > 0:
        emotion_agg = {k: v / emotion_total for k, v in emotion_agg.items()}

    theme_total = sum(theme_agg.values())
    if theme_total > 0:
        theme_agg = {k: v / theme_total for k, v in theme_agg.items()}

    avg_depth = depth_weighted_sum / total_weight if total_weight > 0 else 0.5

    top_emotions = sorted(emotion_agg.items(), key=lambda x: x[1], reverse=True)
    top_themes = sorted(theme_agg.items(), key=lambda x: x[1], reverse=True)
    positive_artist_weights = {
        artist: weight for artist, weight in artist_weights.items() if weight > 0
    }
    positive_track_weights = {
        track_uri: weight for track_uri, weight in track_weights.items() if weight > 0
    }
    top_artists = sorted(
        positive_artist_weights.items(),
        key=lambda x: (-x[1], x[0]),
    )[:10]
    top_tracks = sorted(
        positive_track_weights.items(),
        key=lambda x: (-x[1], track_info[x[0]].get("name") or x[0]),
    )[:10]

    frequency_start = t_now - timedelta(days=half_life_days * FREQUENCY_WINDOW_HALF_LIVES)
    for row in play_rows:
        t_play = _parse_ts(row["ts"])
        if t_play < frequency_start or not _is_qualified_frequency_play(row["ms_played"]):
            continue

        track_uri = row["track_uri"]
        frequency_counts[track_uri] = frequency_counts.get(track_uri, 0) + 1
        frequency_latest[track_uri] = max(frequency_latest.get(track_uri, row["ts"]), row["ts"])
        if track_uri not in frequency_info:
            frequency_info[track_uri] = {
                "uri": track_uri,
                "name": row["track_name"],
                "artist": row["primary_artist"],
                "album": row["album_name"],
            }

    top_frequency_tracks = sorted(
        frequency_counts.items(),
        key=lambda x: (
            -x[1],
            -_parse_ts(frequency_latest[x[0]]).timestamp(),
            frequency_info[x[0]].get("name") or x[0],
        ),
    )[:10]

    # Date range spans *all* plays within the window's effective lookback (the
    # span of actual listening), not just scored plays — otherwise low coverage
    # would make the displayed range collapse to whatever handful of tracks
    # happen to be scored. Effective lookback = 4 half-lives, beyond which a
    # play's decayed weight is <~6%; same cutoff as frequency_start so state and
    # trait show distinct ranges.
    window_start = t_now - timedelta(days=half_life_days * FREQUENCY_WINDOW_HALF_LIVES)
    window_play_ts: list[str] = [
        row["ts"] for row in play_rows if _parse_ts(row["ts"]) >= window_start
    ]
    from_date: str | None = None
    to_date: str | None = None
    if window_play_ts:
        sorted_plays = sorted(window_play_ts)
        from_date = sorted_plays[0][:10]
        to_date = sorted_plays[-1][:10]

    # Coverage: how much of the actual listening in this window backs the mood
    # mixture. The emotion/theme windows are built only from plays of *scored*
    # tracks; if most plays are unscored, the headline is built on a thin,
    # possibly biased slice and the report should say so rather than imply
    # authority.
    total_window_plays = len(window_play_ts)
    scored_window_plays = sum(
        1 for row in rows if _parse_ts(row["ts"]) >= window_start
    )
    coverage = {
        "scored_plays": scored_window_plays,
        "total_plays": total_window_plays,
        "ratio": (scored_window_plays / total_window_plays) if total_window_plays else 0.0,
    }

    return {
        "emotions": dict(top_emotions),
        "themes": dict(top_themes),
        "avg_depth": avg_depth,
        "top_artists": [{"artist": a, "weight": w} for a, w in top_artists],
        "top_tracks": [
            {**track_info[t], "weight": w, "play_count": track_play_counts[t]}
            for t, w in top_tracks
        ],
        "top_frequency_tracks": [
            {
                **frequency_info[t],
                "qualified_play_count": count,
                "play_count": count,
                "last_played": frequency_latest[t],
                "frequency_window_days": half_life_days * FREQUENCY_WINDOW_HALF_LIVES,
            }
            for t, count in top_frequency_tracks
        ],
        "total_weight": total_weight,
        "play_count": len(rows),
        "from_date": from_date,
        "to_date": to_date,
        "coverage": coverage,
    }


def compute_state_and_trait(conn: sqlite3.Connection, config: OrpheusConfig) -> dict:
    t_now = datetime.now(timezone.utc)

    state = aggregate_window(conn, t_now, config.windows.state_half_life_days, config)
    trait = aggregate_window(conn, t_now, config.windows.trait_half_life_days, config)

    return {"state": state, "trait": trait, "computed_at": t_now.isoformat()}
