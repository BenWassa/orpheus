"""Tests for the experimental perspectives (session arcs, novelty)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from orpheus.output.perspectives import compute_perspectives

T_NOW = datetime(2026, 5, 22, 23, 59, tzinfo=timezone.utc)
MODEL = "test-model"

NEGATIVE = {
    "sadness_melancholy": 0.5,
    "tension_anxiety": 0.3,
    "anger_defiance": 0.1,
    "peacefulness": 0.05,
    "joyful_activation": 0.05,
}
POSITIVE = {
    "peacefulness": 0.5,
    "joyful_activation": 0.3,
    "tenderness": 0.1,
    "sadness_melancholy": 0.05,
    "tension_anxiety": 0.05,
}


def _insert_track(conn, uri, scores=None):
    conn.execute(
        """INSERT OR IGNORE INTO tracks (track_uri, track_name, primary_artist)
           VALUES (?, ?, ?)""",
        (uri, uri.split(":")[-1], "Artist"),
    )
    if scores is not None:
        conn.execute(
            """INSERT OR REPLACE INTO track_scores
               (track_uri, model_version, emotion_scores, theme_scores,
                depth_score, depth_label, confidence, scored_at)
               VALUES (?, ?, ?, '{}', 0.5, 'engaged', '1.0', ?)""",
            (uri, MODEL, json.dumps(scores), T_NOW.isoformat()),
        )


def _insert_session(conn, start, uris, ms=200_000):
    """Insert plays 4 minutes apart (continuous session)."""
    for i, uri in enumerate(uris):
        ts = start + timedelta(minutes=4 * i)
        conn.execute(
            "INSERT INTO plays (ts, track_uri, ms_played) VALUES (?, ?, ?)",
            (ts.strftime("%Y-%m-%dT%H:%M:%SZ"), uri, ms),
        )


def test_settling_sessions_detected(tmp_db):
    for i in range(3):
        _insert_track(tmp_db, f"spotify:track:neg{i}", NEGATIVE)
        _insert_track(tmp_db, f"spotify:track:pos{i}", POSITIVE)

    # Six sessions that start negative and end positive, on separate days.
    uris = [f"spotify:track:neg{i}" for i in range(3)] + [f"spotify:track:pos{i}" for i in range(3)]
    for d in range(6):
        _insert_session(tmp_db, T_NOW - timedelta(days=d + 1), uris)
    tmp_db.commit()

    result = compute_perspectives(tmp_db, MODEL, T_NOW)
    arcs = result["session_arcs"]
    assert arcs["sessions_measured"] == 6
    assert arcs["arcs"]["settling"] == 6
    assert "regulation" in arcs["reading"]


def test_sessions_split_on_gap(tmp_db):
    _insert_track(tmp_db, "spotify:track:a", NEGATIVE)
    # Two bursts of 5 plays separated by 3 hours → 2 sessions.
    _insert_session(tmp_db, T_NOW - timedelta(days=1, hours=6), ["spotify:track:a"] * 5)
    _insert_session(tmp_db, T_NOW - timedelta(days=1, hours=2), ["spotify:track:a"] * 5)
    tmp_db.commit()

    result = compute_perspectives(tmp_db, MODEL, T_NOW)
    assert result["session_arcs"]["sessions_total"] == 2


def test_novelty_ratio(tmp_db):
    _insert_track(tmp_db, "spotify:track:old")
    _insert_track(tmp_db, "spotify:track:new")

    # "old" first played long before the window; "new" first played inside it.
    _insert_session(tmp_db, T_NOW - timedelta(days=200), ["spotify:track:old"])
    _insert_session(tmp_db, T_NOW - timedelta(days=10), ["spotify:track:old"])
    _insert_session(tmp_db, T_NOW - timedelta(days=5), ["spotify:track:new"])
    tmp_db.commit()

    novelty = compute_perspectives(tmp_db, MODEL, T_NOW)["novelty"]
    assert novelty["qualified_plays"] == 2  # only the in-window plays
    assert novelty["new_track_plays"] == 1
    assert novelty["novelty_ratio"] == 0.5


def test_empty_db(tmp_db):
    result = compute_perspectives(tmp_db, MODEL, T_NOW)
    assert result["status"] == "experimental"
    assert result["session_arcs"]["sessions_measured"] == 0
    assert result["novelty"]["qualified_plays"] == 0
