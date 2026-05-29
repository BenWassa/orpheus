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

    # Within-group pairing scores high on the same tracks far more than its
    # marginals predict (lift ~2.0) → reported as a strong connection.
    assert ("joyful_activation", "hedonism_escape") in by_pair
    assert by_pair[("joyful_activation", "hedonism_escape")]["strength"] == "strong"
    assert by_pair[("joyful_activation", "hedonism_escape")]["lift"] > 1.5
    # Cross-group pairing only present via the never-played ghost (weight 0), so
    # it accumulates no mass → excluded.
    assert ("joyful_activation", "heartbreak_loss") not in by_pair


def _add_plays_at(conn, track_uri, when: datetime, count: int):
    ts = when.isoformat()
    for _ in range(count):
        conn.execute(
            "INSERT INTO plays (ts, ms_played, track_uri) VALUES (?, 200000, ?)",
            (ts, track_uri),
        )


def test_co_occurrence_since_scopes_play_universe(tmp_db):
    """`since` restricts the play universe to a window's evidence span: the same
    pairing is observed fewer times when older plays fall outside the window."""
    from orpheus.pattern.trends import detect_co_occurrences

    # Two distinct groups so the expected-vs-observed lift is meaningful in both
    # scopes (a single uniform group would have every category at prob 1.0).
    group_a_emo = {"joyful_activation": 0.9, "triumphant_power": 0.6, "peacefulness": 0.3}
    group_a_thm = {"hedonism_escape": 0.9, "status_ambition": 0.6, "identity_autonomy": 0.3}
    group_b_emo = {"sadness_melancholy": 0.9, "tension_anxiety": 0.6, "anger_defiance": 0.3}
    group_b_thm = {"heartbreak_loss": 0.9, "adversity_resilience": 0.6, "existentialism_spirituality": 0.3}

    def vec(base, keys):
        return {c: base.get(c, 0.0) for c in keys}

    now = datetime.now(timezone.utc)
    recent = now - timedelta(days=5)
    old = now - timedelta(days=200)

    # Each track is played both recently and long ago. The recent window should
    # only count the recent plays; all-time counts both.
    for i in range(6):
        a = f"spotify:track:a{i}"
        b = f"spotify:track:b{i}"
        _insert_distinct_score(tmp_db, a, vec(group_a_emo, EMOTION_CATEGORIES), vec(group_a_thm, THEME_CATEGORIES))
        _insert_distinct_score(tmp_db, b, vec(group_b_emo, EMOTION_CATEGORIES), vec(group_b_thm, THEME_CATEGORIES))
        for track in (a, b):
            _add_plays_at(tmp_db, track, recent, count=10)
            _add_plays_at(tmp_db, track, old, count=10)
    tmp_db.commit()

    pair = ("joyful_activation", "hedonism_escape")
    recent_by_pair = {tuple(p["pair"]): p for p in detect_co_occurrences(tmp_db, since=now - timedelta(days=30))}
    all_by_pair = {tuple(p["pair"]): p for p in detect_co_occurrences(tmp_db)}

    assert pair in recent_by_pair
    assert pair in all_by_pair
    # Recent counts only the recent plays; all-time counts recent + old (2x), so
    # the all-time co-occurrence mass is ~double the recent mass for the same pair.
    recent_obs = recent_by_pair[pair]["observed"]
    all_obs = all_by_pair[pair]["observed"]
    assert all_obs > recent_obs
    assert abs(all_obs - 2 * recent_obs) <= 2  # equal recent/old play counts → 2x mass


def test_co_occurrence_since_below_floor_returns_empty(tmp_db):
    """A window with too few distinct played-and-scored tracks returns [] rather
    than borrowing all-time connections."""
    from orpheus.pattern.trends import detect_co_occurrences

    now = datetime.now(timezone.utc)
    # Only 3 distinct tracks in the recent window — below the min_tracks floor.
    for i in range(3):
        uri = f"spotify:track:thin{i}"
        _insert_distinct_score(
            tmp_db, uri,
            {c: 0.5 for c in EMOTION_CATEGORIES},
            {c: 0.5 for c in THEME_CATEGORIES},
        )
        _add_plays_at(tmp_db, uri, now - timedelta(days=2), count=5)
    tmp_db.commit()

    assert detect_co_occurrences(tmp_db, since=now - timedelta(days=30)) == []
