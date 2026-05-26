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


def detect_trends(conn: sqlite3.Connection) -> list[dict]:
    t_now = datetime.now(timezone.utc)
    buckets = _build_weekly_buckets(conn, t_now, _TREND_WEEKS)

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
    rows = conn.execute(
        """SELECT ts.emotion_scores, ts.theme_scores
           FROM track_scores ts"""
    ).fetchall()

    if len(rows) < 10:
        return []

    co_counts: dict[tuple[str, str], int] = defaultdict(int)
    emotion_counts: dict[str, int] = defaultdict(int)
    theme_counts: dict[str, int] = defaultdict(int)
    total = 0

    for row in rows:
        emotions = json.loads(row["emotion_scores"])
        themes = json.loads(row["theme_scores"])

        top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]
        top_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)[:3]

        for e_cat, _ in top_emotions:
            emotion_counts[e_cat] += 1
        for t_cat, _ in top_themes:
            theme_counts[t_cat] += 1

        for e_cat, _ in top_emotions:
            for t_cat, _ in top_themes:
                co_counts[(e_cat, t_cat)] += 1

        total += 1

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
                "observed": observed,
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

    for row in rows:
        ts = datetime.fromisoformat(row["ts"].replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        week_idx = int((ts - start).days / 7)
        if week_idx < 0 or week_idx >= n_weeks:
            continue

        emotions = json.loads(row["emotion_scores"])
        themes = json.loads(row["theme_scores"])
        for cat, val in emotions.items():
            buckets[week_idx][cat].append(val)
        for cat, val in themes.items():
            buckets[week_idx][cat].append(val)

    return [{cat: np.mean(vals) for cat, vals in bucket.items()} for bucket in buckets]


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
