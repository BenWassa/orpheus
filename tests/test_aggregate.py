from __future__ import annotations

import math
from datetime import datetime, timezone

import pytest

from orpheus.aggregate.decay import engagement_weight, time_decay_weight


class TestTimeDecay:
    def test_at_time_zero(self):
        t = datetime(2025, 1, 1, tzinfo=timezone.utc)
        w = time_decay_weight(t, t, half_life_days=3.0, w0=1.0)
        assert abs(w - 1.0) < 0.001

    def test_at_half_life(self):
        t_play = datetime(2025, 1, 1, tzinfo=timezone.utc)
        t_now = datetime(2025, 1, 4, tzinfo=timezone.utc)  # 3 days later
        w = time_decay_weight(t_play, t_now, half_life_days=3.0, w0=1.0)
        assert abs(w - 0.5) < 0.001

    def test_at_two_half_lives(self):
        t_play = datetime(2025, 1, 1, tzinfo=timezone.utc)
        t_now = datetime(2025, 1, 7, tzinfo=timezone.utc)  # 6 days later
        w = time_decay_weight(t_play, t_now, half_life_days=3.0, w0=1.0)
        assert abs(w - 0.25) < 0.001

    def test_w0_scales(self):
        t_play = datetime(2025, 1, 1, tzinfo=timezone.utc)
        t_now = datetime(2025, 1, 4, tzinfo=timezone.utc)
        w = time_decay_weight(t_play, t_now, half_life_days=3.0, w0=2.0)
        assert abs(w - 1.0) < 0.001

    def test_trait_window_decays_slower(self):
        t_play = datetime(2025, 1, 1, tzinfo=timezone.utc)
        t_now = datetime(2025, 2, 1, tzinfo=timezone.utc)  # 31 days
        w_state = time_decay_weight(t_play, t_now, half_life_days=3.0)
        w_trait = time_decay_weight(t_play, t_now, half_life_days=90.0)
        assert w_trait > w_state


class TestEngagementWeight:
    def test_full_play(self):
        w = engagement_weight(200000, 210000, "trackdone", False, False)
        assert w > 0.9

    def test_early_skip(self):
        w = engagement_weight(5000, 210000, "fwdbtn", False, True)
        assert w < 0

    def test_boundary_skip(self):
        w = engagement_weight(209000, 210000, "fwdbtn", False, True)
        assert w == pytest.approx(-0.25, abs=0.01)

    def test_shuffle_penalty(self):
        w_no_shuffle = engagement_weight(200000, 210000, "trackdone", False, False)
        w_shuffle = engagement_weight(200000, 210000, "trackdone", True, False)
        assert w_shuffle < w_no_shuffle

    def test_library_bonus(self):
        w_click = engagement_weight(200000, 210000, "trackdone", False, False, reason_start="clickrow")
        w_auto = engagement_weight(200000, 210000, "trackdone", False, False, reason_start="autoplay")
        assert w_click > w_auto
