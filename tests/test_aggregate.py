from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from orpheus.aggregate.windows import aggregate_window
from orpheus.aggregate.decay import engagement_weight, time_decay_weight
from orpheus.score.emotion import EMOTION_CATEGORIES
from orpheus.score.theme import THEME_CATEGORIES


def _scores():
    return (
        json.dumps({cat: 1.0 / len(EMOTION_CATEGORIES) for cat in EMOTION_CATEGORIES}),
        json.dumps({cat: 1.0 / len(THEME_CATEGORIES) for cat in THEME_CATEGORIES}),
    )


def _insert_track(conn, uri, name, model_version, emotion_scores=None, theme_scores=None):
    if emotion_scores is None or theme_scores is None:
        emotion_scores, theme_scores = _scores()

    conn.execute(
        """INSERT INTO tracks
           (track_uri, track_name, primary_artist, album_name, duration_ms)
           VALUES (?, ?, ?, ?, ?)""",
        (uri, name, "Artist", "Album", 200000),
    )
    conn.execute(
        """INSERT INTO track_scores
           (track_uri, model_version, emotion_scores, theme_scores, depth_score)
           VALUES (?, ?, ?, ?, ?)""",
        (uri, model_version, emotion_scores, theme_scores, 0.5),
    )


def _insert_play(conn, uri, ts, ms_played, reason_end="trackdone", skipped=False):
    conn.execute(
        """INSERT INTO plays
           (ts, ms_played, track_uri, reason_start, reason_end, shuffle, skipped)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (ts, ms_played, uri, "autoplay", reason_end, False, skipped),
    )


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


class TestPrimaryTracks:
    def test_primary_tracks_use_net_signed_engagement(self, tmp_db, tmp_config):
        _insert_track(tmp_db, "spotify:track:a", "Net Demoted", tmp_config.model_version)
        _insert_track(tmp_db, "spotify:track:b", "Partial Positive", tmp_config.model_version)
        _insert_play(tmp_db, "spotify:track:a", "2025-01-01T00:00:00Z", 200000)
        _insert_play(
            tmp_db,
            "spotify:track:a",
            "2025-01-01T00:00:00Z",
            5000,
            reason_end="fwdbtn",
            skipped=True,
        )
        _insert_play(tmp_db, "spotify:track:b", "2025-01-01T00:00:00Z", 100000)
        tmp_db.commit()

        window = aggregate_window(
            tmp_db,
            datetime(2025, 1, 1, tzinfo=timezone.utc),
            half_life_days=3.0,
            config=tmp_config,
        )

        assert [track["uri"] for track in window["top_tracks"][:2]] == [
            "spotify:track:b",
            "spotify:track:a",
        ]
        assert window["top_tracks"][0]["weight"] == pytest.approx(0.7)
        assert window["top_tracks"][1]["weight"] == pytest.approx(0.5)
        assert window["top_tracks"][1]["play_count"] == 2

    def test_primary_tracks_use_current_model_version_once(self, tmp_db, tmp_config):
        _insert_track(tmp_db, "spotify:track:current", "Current", tmp_config.model_version)
        emotion_scores, theme_scores = _scores()
        tmp_db.execute(
            """INSERT INTO track_scores
               (track_uri, model_version, emotion_scores, theme_scores, depth_score)
               VALUES (?, ?, ?, ?, ?)""",
            ("spotify:track:current", "old-model", emotion_scores, theme_scores, 0.5),
        )
        _insert_play(tmp_db, "spotify:track:current", "2025-01-01T00:00:00Z", 200000)
        tmp_db.commit()

        window = aggregate_window(
            tmp_db,
            datetime(2025, 1, 1, tzinfo=timezone.utc),
            half_life_days=3.0,
            config=tmp_config,
        )

        assert len(window["top_tracks"]) == 1
        assert window["top_tracks"][0]["weight"] == pytest.approx(1.0)
        assert window["play_count"] == 1
