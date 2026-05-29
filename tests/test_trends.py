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


def _insert_distinct_score(conn, track_uri, emotions: dict, themes: dict):
    conn.execute(
        "INSERT OR IGNORE INTO tracks (track_uri, track_name) VALUES (?, 'test')",
        (track_uri,),
    )
    conn.execute(
        """INSERT OR REPLACE INTO track_scores
           (track_uri, model_version, emotion_scores, theme_scores,
            depth_score, depth_label, confidence, scored_at)
           VALUES (?, 'test', ?, ?, 0.5, 'engaged', '0.85', ?)""",
        (track_uri, json.dumps(emotions), json.dumps(themes),
         datetime.now(timezone.utc).isoformat()),
    )


def test_co_occurrence_weighted_by_play_count(tmp_db):
    """Co-occurrence is weighted by qualified plays, and scored-but-never-played
    tracks must not contribute at all."""
    from orpheus.pattern.trends import detect_co_occurrences

    # Graded vectors give each group a deterministic top-3.
    group_a_emo = {"joyful_activation": 0.9, "triumphant_power": 0.6, "peacefulness": 0.3}
    group_a_thm = {"hedonism_escape": 0.9, "status_ambition": 0.6, "identity_autonomy": 0.3}
    group_b_emo = {"sadness_melancholy": 0.9, "tension_anxiety": 0.6, "anger_defiance": 0.3}
    group_b_thm = {"heartbreak_loss": 0.9, "adversity_resilience": 0.6, "existentialism_spirituality": 0.3}

    def vec(base, keys):
        return {c: base.get(c, 0.0) for c in keys}

    start = datetime.now(timezone.utc) - timedelta(weeks=1)

    for i in range(6):
        a = f"spotify:track:a{i}"
        b = f"spotify:track:b{i}"
        _insert_distinct_score(tmp_db, a, vec(group_a_emo, EMOTION_CATEGORIES), vec(group_a_thm, THEME_CATEGORIES))
        _insert_distinct_score(tmp_db, b, vec(group_b_emo, EMOTION_CATEGORIES), vec(group_b_thm, THEME_CATEGORIES))
        _add_plays(tmp_db, a, 0, count=10, start=start)
        _add_plays(tmp_db, b, 0, count=10, start=start)

    # A track scored but never played — must be ignored entirely.
    _insert_distinct_score(
        tmp_db, "spotify:track:ghost",
        vec({"joyful_activation": 0.9}, EMOTION_CATEGORIES),
        vec({"heartbreak_loss": 0.9}, THEME_CATEGORIES),
    )
    tmp_db.commit()

    pairs = detect_co_occurrences(tmp_db)
    by_pair = {tuple(p["pair"]): p for p in pairs}

    # Within-group pairing is over-represented and play-weighted (observed
    # reflects the 60 qualified plays, not the 6 distinct tracks).
    assert ("joyful_activation", "hedonism_escape") in by_pair
    assert by_pair[("joyful_activation", "hedonism_escape")]["observed"] >= 60
    # Cross-group pairing only present via the never-played ghost → excluded.
    assert ("joyful_activation", "heartbreak_loss") not in by_pair
