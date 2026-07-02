"""Experimental perspectives: exploratory report sections.

Everything in here ships under the report's ``experimental`` key and is
labelled as exploratory — the methods are plausible but not yet validated the
way the core windows are. Each perspective states its own evidence base.

Current perspectives:

- **Session arcs** — sessionize plays (gap > 30 min) and compare the
  negative-emotion share at the start vs. the end of each session. If
  sessions consistently end calmer than they start, music is functioning as
  regulation; if they hold or deepen the mood, as amplification. Requires
  scored tracks, so inherits scoring coverage limits (disclosed per run).
- **Novelty** — the share of qualified plays that are first-ever plays of a
  track, overall and per month. Computed from raw plays: full coverage.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone

SESSION_GAP_MINUTES = 30
MIN_SESSION_PLAYS = 5
MIN_SCORED_PLAYS = 3
QUALIFIED_LISTEN_MS = 30_000

# Negative-valence emotions per the T1 taxonomy anchors.
_NEGATIVE_EMOTIONS = ("sadness_melancholy", "tension_anxiety", "anger_defiance")

# Arc classification threshold: change in negative share between the first
# and last third of a session.
_ARC_THRESHOLD = 0.05


def _parse_ts(ts: str) -> datetime:
    parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def compute_perspectives(
    conn: sqlite3.Connection,
    model_version: str,
    t_now: datetime,
    lookback_days: float = 90,
) -> dict:
    return {
        "status": "experimental",
        "note": (
            "Exploratory analyses — methods are plausible but not validated "
            "like the core windows. Read the per-section evidence notes."
        ),
        "session_arcs": _session_arcs(conn, model_version, t_now, lookback_days),
        "novelty": _novelty(conn, t_now, lookback_days),
    }


def _negative_share(emotion_scores: dict) -> float:
    total = sum(emotion_scores.values())
    if total <= 0:
        return 0.0
    return sum(emotion_scores.get(cat, 0.0) for cat in _NEGATIVE_EMOTIONS) / total


def _session_arcs(
    conn: sqlite3.Connection,
    model_version: str,
    t_now: datetime,
    lookback_days: float,
) -> dict:
    window_start = t_now - timedelta(days=lookback_days)
    rows = conn.execute(
        """SELECT p.ts, p.ms_played, ts.emotion_scores
           FROM plays p
           LEFT JOIN track_scores ts ON ts.track_uri = p.track_uri
                                    AND ts.model_version = ?
           ORDER BY p.ts""",
        (model_version,),
    ).fetchall()

    plays = []
    for row in rows:
        t_play = _parse_ts(row["ts"])
        if window_start <= t_play <= t_now:
            scores = json.loads(row["emotion_scores"]) if row["emotion_scores"] else None
            plays.append((t_play, row["ms_played"] or 0, scores))

    # Sessionize: a new session starts when the gap since the previous play's
    # (approximate) end exceeds the threshold.
    sessions: list[list] = []
    gap = timedelta(minutes=SESSION_GAP_MINUTES)
    for play in plays:
        t_play, ms, _ = play
        if sessions:
            prev_t, prev_ms, _ = sessions[-1][-1]
            prev_end = prev_t + timedelta(milliseconds=prev_ms)
            if t_play - prev_end <= gap:
                sessions[-1].append(play)
                continue
        sessions.append([play])

    arcs = {"settling": 0, "deepening": 0, "steady": 0}
    measured = 0
    total_eligible = 0
    session_minutes = []

    for session in sessions:
        if len(session) < MIN_SESSION_PLAYS:
            continue
        total_eligible += 1
        session_minutes.append(sum(ms for _, ms, _ in session) / 60_000)

        scored = [scores for _, _, scores in session if scores]
        if len(scored) < MIN_SCORED_PLAYS:
            continue

        third = max(1, len(scored) // 3)
        start_neg = sum(_negative_share(s) for s in scored[:third]) / third
        end_neg = sum(_negative_share(s) for s in scored[-third:]) / third
        delta = end_neg - start_neg

        measured += 1
        if delta < -_ARC_THRESHOLD:
            arcs["settling"] += 1
        elif delta > _ARC_THRESHOLD:
            arcs["deepening"] += 1
        else:
            arcs["steady"] += 1

    reading = None
    if measured >= 5:
        dominant = max(arcs, key=arcs.get)
        share = arcs[dominant] / measured
        if share >= 0.5:
            descriptions = {
                "settling": "sessions tend to end calmer than they start — "
                "listening reads as regulation",
                "deepening": "sessions tend to end heavier than they start — "
                "listening reads as amplification",
                "steady": "sessions tend to hold one mood — listening reads as "
                "accompaniment, not steering",
            }
            reading = descriptions[dominant]

    return {
        "sessions_total": total_eligible,
        "sessions_measured": measured,
        "arcs": arcs,
        "median_session_minutes": (
            round(sorted(session_minutes)[len(session_minutes) // 2], 1)
            if session_minutes
            else None
        ),
        "reading": reading,
        "evidence_note": (
            f"Arcs measured on {measured} of {total_eligible} sessions "
            f"(≥{MIN_SESSION_PLAYS} plays, ≥{MIN_SCORED_PLAYS} scored plays each); "
            "negative-emotion share compared between first and last third."
        ),
    }


def _novelty(conn: sqlite3.Connection, t_now: datetime, lookback_days: float) -> dict:
    window_start = t_now - timedelta(days=lookback_days)
    rows = conn.execute("SELECT ts, ms_played, track_uri FROM plays ORDER BY ts").fetchall()

    seen: set[str] = set()
    monthly: dict[str, dict] = {}
    total_qualified = 0
    total_new = 0

    for row in rows:
        uri = row["track_uri"]
        t_play = _parse_ts(row["ts"])
        is_first = uri not in seen
        seen.add(uri)

        if not (window_start <= t_play <= t_now):
            continue
        if (row["ms_played"] or 0) < QUALIFIED_LISTEN_MS:
            continue

        total_qualified += 1
        month_key = t_play.strftime("%Y-%m")
        month = monthly.setdefault(month_key, {"qualified_plays": 0, "new_tracks": 0})
        month["qualified_plays"] += 1
        if is_first:
            total_new += 1
            month["new_tracks"] += 1

    months_out = [
        {
            "month": key,
            "qualified_plays": m["qualified_plays"],
            "new_track_plays": m["new_tracks"],
            "novelty_ratio": (
                round(m["new_tracks"] / m["qualified_plays"], 3) if m["qualified_plays"] else 0.0
            ),
        }
        for key, m in sorted(monthly.items())
    ]

    return {
        "qualified_plays": total_qualified,
        "new_track_plays": total_new,
        "novelty_ratio": round(total_new / total_qualified, 3) if total_qualified else 0.0,
        "by_month": months_out,
        "evidence_note": (
            "A play is 'new' when its track appears for the first time in the "
            "entire play history (not just this window). Full coverage — no "
            "scoring involved."
        ),
    }
