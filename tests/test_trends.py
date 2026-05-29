from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from orpheus.pattern.trends import detect_trends
from orpheus.score.emotion import EMOTION_CATEGORIES
from orpheus.score.theme import THEME_CATEGORIES

_TRACK = "spotify:track:trendtest"


def _insert_score(conn, track_uri, emotion_val, theme_val):
    conn.execute(
        "INSERT OR IGNORE INTO tracks (track_uri, track_name) VALUES (?, 'test')",
        (track_uri,),
    )
    conn.execute(
        """INSERT OR REPLACE INTO track_scores
           (track_uri, model_version, emotion_scores, theme_scores,
            depth_score, depth_label, confidence, scored_at)
           VALUES (?, 'test', ?, ?, 0.5, 'engaged', '{}', ?)""",
        (
            track_uri,
            json.dumps({c: emotion_val for c in EMOTION_CATEGORIES}),
            json.dumps({c: theme_val for c in THEME_CATEGORIES}),
            datetime.now(timezone.utc).isoformat(),
        ),
    )


def _add_plays(conn, track_uri, week_idx, count, start):
    ts = (start + timedelta(weeks=week_idx, days=1)).isoformat()
    for _ in range(count):
        conn.execute(
            "INSERT INTO plays (ts, ms_played, track_uri) VALUES (?, 200000, ?)",
            (ts, track_uri),
        )


def test_empty_trailing_week_does_not_force_uniform_decline(tmp_db):
    """An empty most-recent week must not collapse every category to a decline.

    Regression: data ending days before "now" left the latest weekly bucket at
    0.0, tripping the spike-decline check for all 16 categories at once.
    """
    start = datetime.now(timezone.utc) - timedelta(weeks=12)
    _insert_score(tmp_db, _TRACK, emotion_val=0.4, theme_val=0.4)

    # Weeks 0..10 populated with constant scores; the most recent week (11) is empty.
    for week in range(11):
        _add_plays(tmp_db, _TRACK, week, count=5, start=start)
    tmp_db.commit()

    trends = detect_trends(tmp_db)

    # Constant scores → no real movement → no trends (and crucially not 16 declines).
    assert all(t["direction"] != "declining" for t in trends)
    assert len(trends) < len(EMOTION_CATEGORIES) + len(THEME_CATEGORIES)


def test_sparse_weeks_are_ignored(tmp_db):
    """Weeks with too few plays are dropped rather than read as ~0 prevalence."""
    start = datetime.now(timezone.utc) - timedelta(weeks=12)
    _insert_score(tmp_db, _TRACK, emotion_val=0.4, theme_val=0.4)

    for week in range(11):
        _add_plays(tmp_db, _TRACK, week, count=5, start=start)
    # A single-play sparse trailing week should be ignored, not flagged.
    _add_plays(tmp_db, _TRACK, 11, count=1, start=start)
    tmp_db.commit()

    trends = detect_trends(tmp_db)
    assert all(t["direction"] != "declining" for t in trends)


def test_real_decline_still_detected(tmp_db):
    """The sparse-week filter must not suppress a genuine downward trend."""
    start = datetime.now(timezone.utc) - timedelta(weeks=12)
    # Distinct score per week, decreasing over the recent window, all well-populated.
    for week in range(12):
        uri = f"{_TRACK}:{week}"
        val = max(0.05, 0.6 - week * 0.05)
        _insert_score(tmp_db, uri, emotion_val=val, theme_val=val)
        _add_plays(tmp_db, uri, week, count=5, start=start)
    tmp_db.commit()

    trends = detect_trends(tmp_db)
    assert any(t["direction"] in ("declining", "falling") for t in trends)
