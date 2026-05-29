from __future__ import annotations

import json
import logging
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import numpy as np

from orpheus.score.emotion import EMOTION_CATEGORIES
from orpheus.score.theme import THEME_CATEGORIES

logger = logging.getLogger(__name__)

_TREND_WEEKS = 12
_SLOPE_THRESHOLD = 0.02
_SPIKE_THRESHOLD = 0.25
_MIN_BUCKET_PLAYS = 3
_QUALIFIED_LISTEN_MS = 30_000


def _qualified_play_counts(conn: sqlite3.Connection) -> dict[str, int]:
    """Qualified listens (>= 30s) per track_uri across all plays."""
    rows = conn.execute(
        """SELECT track_uri, COUNT(*) AS n
           FROM plays
           WHERE COALESCE(ms_played, 0) >= ?
           GROUP BY track_uri""",
        (_QUALIFIED_LISTEN_MS,),
    ).fetchall()
    return {row["track_uri"]: row["n"] for row in rows}


def detect_trends(conn: sqlite3.Connection) -> list[dict]:
    t_now = datetime.now(timezone.utc)
    buckets = _build_weekly_buckets(conn, t_now, _TREND_WEEKS)

    # Drop weeks with too few plays to yield a trustworthy weekly mean. Without
    # this, an empty or sparse trailing week (e.g. data ends days before "now")
    # collapses every category's latest value toward 0 and false-flags a uniform
    # "decline" across all categories.
    buckets = [b for b in buckets if b["_count"] >= _MIN_BUCKET_PLAYS]

    if len(buckets) < 4:
        return []

    all_categories = [(cat, "emotion") for cat in EMOTION_CATEGORIES] + \
                     [(cat, "theme") for cat in THEME_CATEGORIES]

    trends = []
    for cat, axis in all_categories:
        series = [b.get(cat, 0.0) for b in buckets]
        recent = series[-4:]

        if len(recent) < 4:
            continue

        x = np.arange(len(recent), dtype=float)
        y = np.array(recent)
        if np.std(y) < 1e-6:
            continue

        slope = float(np.polyfit(x, y, 1)[0])
        trailing_avg = np.mean(y[:-1]) if len(y) > 1 else y[0]
        latest = y[-1]

        direction = None
        magnitude = "minor"

        if slope > _SLOPE_THRESHOLD:
            direction = "rising"
        elif slope < -_SLOPE_THRESHOLD:
            direction = "falling"

        if trailing_avg > 0 and abs(latest - trailing_avg) / trailing_avg > _SPIKE_THRESHOLD:
            if latest > trailing_avg:
                direction = "spiking"
                magnitude = "notable"
            else:
                direction = "declining"
                magnitude = "notable"

        if direction:
            if abs(slope) > _SLOPE_THRESHOLD * 3:
                magnitude = "notable"

            trends.append({
                "category": cat,
                "axis": axis,
                "direction": direction,
                "magnitude": magnitude,
                "narrative": _trend_narrative(cat, axis, direction),
            })

    return trends


def detect_co_occurrences(conn: sqlite3.Connection) -> list[dict]:
    # Weight each scored track by how many times it was actually played
    # (qualified listens), so co-occurrence reflects listening behaviour rather
    # than catalog composition. A track played 500 times should count far more
    # than one played once, and tracks never played should not count at all.
    rows = conn.execute(
        """SELECT ts.track_uri, ts.emotion_scores, ts.theme_scores
           FROM track_scores ts"""
    ).fetchall()

    play_counts = _qualified_play_counts(conn)

    co_counts: dict[tuple[str, str], float] = defaultdict(float)
    emotion_counts: dict[str, float] = defaultdict(float)
    theme_counts: dict[str, float] = defaultdict(float)
    total = 0.0
    scored_tracks_played = 0

    for row in rows:
        weight = play_counts.get(row["track_uri"], 0)
        if weight <= 0:
            continue
        scored_tracks_played += 1

        emotions = json.loads(row["emotion_scores"])
        themes = json.loads(row["theme_scores"])

        top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]
        top_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)[:3]

        for e_cat, _ in top_emotions:
            emotion_counts[e_cat] += weight
        for t_cat, _ in top_themes:
            theme_counts[t_cat] += weight

        for e_cat, _ in top_emotions:
            for t_cat, _ in top_themes:
                co_counts[(e_cat, t_cat)] += weight

        total += weight

    # Need a minimum of distinct played-and-scored tracks for the expected-value
    # comparison to mean anything.
    if scored_tracks_played < 10 or total <= 0:
        return []

    results = []
    for (e_cat, t_cat), observed in co_counts.items():
        e_prob = emotion_counts[e_cat] / total
        t_prob = theme_counts[t_cat] / total
        expected = e_prob * t_prob * total

        if expected > 0 and observed / expected > 1.5:
            strength = "strong" if observed / expected > 2.0 else "moderate"
            results.append({
                "pair": [e_cat, t_cat],
                "strength": strength,
                "observed": int(round(observed)),
                "expected": round(expected, 1),
                "narrative": _co_occurrence_narrative(e_cat, t_cat, strength),
            })

    results.sort(key=lambda x: x["observed"] / max(x["expected"], 0.1), reverse=True)
    return results[:10]


def compare_state_trait(state: dict, trait: dict) -> list[dict]:
    shifts = []

    for cat in EMOTION_CATEGORIES:
        s = state["emotions"].get(cat, 0.0)
        t = trait["emotions"].get(cat, 0.0)
        delta = s - t
        if abs(delta) > 0.03:
            direction = "elevated" if delta > 0 else "faded"
            shifts.append({
                "category": cat,
                "axis": "emotion",
                "direction": direction,
                "delta": round(delta, 3),
                "narrative": _shift_narrative(cat, "emotion", direction),
            })

    for cat in THEME_CATEGORIES:
        s = state["themes"].get(cat, 0.0)
        t = trait["themes"].get(cat, 0.0)
        delta = s - t
        if abs(delta) > 0.03:
            direction = "elevated" if delta > 0 else "faded"
            shifts.append({
                "category": cat,
                "axis": "theme",
                "direction": direction,
                "delta": round(delta, 3),
                "narrative": _shift_narrative(cat, "theme", direction),
            })

    shifts.sort(key=lambda x: abs(x["delta"]), reverse=True)
    return shifts


def _build_weekly_buckets(
    conn: sqlite3.Connection, t_now: datetime, n_weeks: int
) -> list[dict]:
    start = t_now - timedelta(weeks=n_weeks)

    rows = conn.execute(
        """SELECT p.ts, ts.emotion_scores, ts.theme_scores
           FROM plays p
           JOIN track_scores ts ON p.track_uri = ts.track_uri
           WHERE p.ts >= ?
           ORDER BY p.ts""",
        (start.isoformat(),),
    ).fetchall()

    buckets: list[dict[str, list[float]]] = [
        defaultdict(list) for _ in range(n_weeks)
    ]
    counts = [0] * n_weeks

    for row in rows:
        ts = datetime.fromisoformat(row["ts"].replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        week_idx = int((ts - start).days / 7)
        if week_idx < 0 or week_idx >= n_weeks:
            continue

        counts[week_idx] += 1
        emotions = json.loads(row["emotion_scores"])
        themes = json.loads(row["theme_scores"])
        for cat, val in emotions.items():
            buckets[week_idx][cat].append(val)
        for cat, val in themes.items():
            buckets[week_idx][cat].append(val)

    result = []
    for i, bucket in enumerate(buckets):
        agg = {cat: float(np.mean(vals)) for cat, vals in bucket.items()}
        agg["_count"] = counts[i]
        result.append(agg)
    return result


_READABLE = {
    "joyful_activation": "joyful activation",
    "triumphant_power": "triumphant power",
    "peacefulness": "peacefulness",
    "tenderness": "tenderness",
    "nostalgia_longing": "nostalgia and longing",
    "sadness_melancholy": "sadness and melancholy",
    "tension_anxiety": "tension and anxiety",
    "anger_defiance": "anger and defiance",
    "interpersonal_devotion": "interpersonal devotion",
    "heartbreak_loss": "heartbreak and loss",
    "adversity_resilience": "adversity and resilience",
    "identity_autonomy": "identity and autonomy",
    "status_ambition": "status and ambition",
    "hedonism_escape": "hedonism and escape",
    "place_heritage": "place and heritage",
    "existentialism_spirituality": "existentialism and spirituality",
}


def _trend_narrative(cat: str, axis: str, direction: str) -> str:
    name = _READABLE.get(cat, cat.replace("_", " "))
    if direction == "rising":
        return f"{name.capitalize()} has intensified across recent listening."
    elif direction == "falling":
        return f"{name.capitalize()} has faded in recent weeks."
    elif direction == "spiking":
        return f"{name.capitalize()} has spiked sharply in the most recent listening."
    else:
        return f"{name.capitalize()} has been declining steadily."


def _co_occurrence_narrative(e_cat: str, t_cat: str, strength: str) -> str:
    e_name = _READABLE.get(e_cat, e_cat.replace("_", " "))
    t_name = _READABLE.get(t_cat, t_cat.replace("_", " "))
    return f"{e_name.capitalize()} and {t_name} co-occur {'frequently' if strength == 'strong' else 'more often than separately'} in your listening."


def _shift_narrative(cat: str, axis: str, direction: str) -> str:
    name = _READABLE.get(cat, cat.replace("_", " "))
    if direction == "elevated":
        return f"{name.capitalize()} is elevated in recent listening compared to the long-term baseline."
    else:
        return f"{name.capitalize()} has faded from recent listening relative to the long-term pattern."
