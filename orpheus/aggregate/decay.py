from __future__ import annotations

import math
from datetime import datetime


LN2 = math.log(2)


def time_decay_weight(
    t_play: datetime,
    t_now: datetime,
    half_life_days: float,
    w0: float = 1.0,
) -> float:
    delta_days = (t_now - t_play).total_seconds() / 86400
    if delta_days < 0:
        delta_days = 0
    lam = LN2 / half_life_days
    return w0 * math.exp(-lam * delta_days)


def engagement_weight(
    ms_played: int,
    duration_ms: int | None,
    reason_end: str | None,
    shuffle: bool,
    skipped: bool,
    reason_start: str | None = None,
    engagement_weights: dict | None = None,
) -> float:
    if engagement_weights is None:
        engagement_weights = {}

    w_full = engagement_weights.get("full_play", 1.0)
    w_partial = engagement_weights.get("partial_play", 0.7)
    w_early_skip = engagement_weights.get("early_skip", -0.5)
    w_boundary_skip = engagement_weights.get("boundary_skip", -0.25)
    w_shuffle = engagement_weights.get("shuffle_source", -0.1)
    w_library = engagement_weights.get("library_play", 0.1)

    w0 = 0.0

    if skipped:
        if duration_ms and abs(ms_played - duration_ms) < 1500:
            w0 = w_boundary_skip
        elif ms_played < 30000:
            w0 = w_early_skip
        else:
            w0 = w_partial
    elif duration_ms and duration_ms > 0:
        completion = ms_played / duration_ms
        if completion >= 0.8:
            w0 = w_full
        else:
            w0 = w_partial
    else:
        if ms_played >= 30000:
            w0 = w_partial
        else:
            w0 = w_early_skip

    if shuffle:
        w0 += w_shuffle

    if reason_start in ("clickrow", "playbtn"):
        w0 += w_library

    return w0
