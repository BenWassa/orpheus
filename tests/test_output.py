from __future__ import annotations

import json


from orpheus.output.assemble import assemble_report, prevalence_label, write_report
from orpheus.score.emotion import EMOTION_CATEGORIES
from orpheus.score.theme import THEME_CATEGORIES


def test_prevalence_dominant():
    assert prevalence_label(0.30) == "dominant"


def test_prevalence_high():
    assert prevalence_label(0.20) == "high"


def test_prevalence_moderate():
    assert prevalence_label(0.10) == "moderate"


def test_prevalence_present():
    assert prevalence_label(0.05) == "present"


def test_prevalence_not_represented():
    assert prevalence_label(0.01) == "not represented"


def test_prevalence_boundary():
    assert prevalence_label(0.25) == "high"
    assert prevalence_label(0.251) == "dominant"


def _make_window():
    emotions = {cat: 1.0 / len(EMOTION_CATEGORIES) for cat in EMOTION_CATEGORIES}
    themes = {cat: 1.0 / len(THEME_CATEGORIES) for cat in THEME_CATEGORIES}
    return {
        "emotions": emotions,
        "themes": themes,
        "avg_depth": 0.5,
        "top_artists": [{"artist": "Test", "weight": 1.0}],
        "top_tracks": [{"track_uri": "spotify:track:test", "weight": 1.0}],
        "top_frequency_tracks": [
            {"uri": "spotify:track:freq", "qualified_play_count": 3, "play_count": 3}
        ],
    }


def test_assemble_report_structure(tmp_config):
    state = _make_window()
    trait = _make_window()
    report = assemble_report(state, trait, [], [], [], tmp_config)
    assert "generated_at" in report
    assert "windows" in report
    assert "state" in report["windows"]
    assert "trait" in report["windows"]
    assert "shifts" in report
    assert "co_occurrences" in report
    assert "clusters" in report
    assert "clusters_status" in report
    assert report["clusters_status"] == "ok"
    assert "safety_flags" in report
    assert report["safety_flags"] == []


def test_assemble_report_attaches_per_window_co_occurrences(tmp_config):
    state_co = [{"pair": ["joyful_activation", "hedonism_escape"], "strength": "strong",
                 "observed": 60, "expected": 30.0, "narrative": "recent"}]
    trait_co = [{"pair": ["nostalgia_longing", "heartbreak_loss"], "strength": "moderate",
                 "observed": 40, "expected": 25.0, "narrative": "usual"}]
    report = assemble_report(
        _make_window(), _make_window(), [], [{"pair": ["x", "y"]}], [], tmp_config,
        state_co_occurrences=state_co, trait_co_occurrences=trait_co,
    )
    # Per-window connections live inside each window and are independent.
    assert report["windows"]["state"]["co_occurrences"] == state_co
    assert report["windows"]["trait"]["co_occurrences"] == trait_co
    # Top-level remains the global set (backward compatible).
    assert report["co_occurrences"] == [{"pair": ["x", "y"]}]


def test_assemble_report_window_co_occurrences_default_empty(tmp_config):
    report = assemble_report(_make_window(), _make_window(), [], [], [], tmp_config)
    assert report["windows"]["state"]["co_occurrences"] == []
    assert report["windows"]["trait"]["co_occurrences"] == []


def test_assemble_report_clusters_status_passthrough(tmp_config):
    report = assemble_report(
        _make_window(), _make_window(), [], [], [], tmp_config,
        clusters_status="no_audio_features",
    )
    assert report["clusters"] == []
    assert report["clusters_status"] == "no_audio_features"


def test_assemble_report_prevalence_labels(tmp_config):
    state = _make_window()
    state["emotions"]["nostalgia_longing"] = 0.35
    report = assemble_report(state, _make_window(), [], [], [], tmp_config)
    top_emotions = report["windows"]["state"]["top_emotions"]
    nostalgia = [e for e in top_emotions if e["category"] == "nostalgia_longing"]
    assert len(nostalgia) == 1
    assert nostalgia[0]["prevalence"] == "dominant"


def test_assemble_report_emits_numeric_score_maps(tmp_config):
    report = assemble_report(_make_window(), _make_window(), [], [], [], tmp_config)
    window = report["windows"]["state"]

    # Full numeric maps are present for every category, not just the top slice.
    assert set(window["emotion"]) == set(EMOTION_CATEGORIES)
    assert set(window["theme"]) == set(THEME_CATEGORIES)
    # Proportions pass through verbatim (not quantized into prevalence buckets).
    assert window["theme"]["heartbreak_loss"] == round(1.0 / len(THEME_CATEGORIES), 6)
    # Aggregation normalizes the maps, so they sum to ~1.0.
    assert abs(sum(window["theme"].values()) - 1.0) < 1e-6
    assert abs(sum(window["emotion"].values()) - 1.0) < 1e-6


def test_assemble_report_copies_tracks_and_defaults_missing_depth(tmp_config):
    state = _make_window()
    source_track = {"uri": "spotify:track:test", "weight": 1.0, "depth_score": None}
    state["top_tracks"] = [source_track]

    report = assemble_report(state, _make_window(), [], [], [], tmp_config)

    assert source_track == {"uri": "spotify:track:test", "weight": 1.0, "depth_score": None}
    assert report["windows"]["state"]["top_tracks"][0]["depth_label"] == "engaged"


def test_assemble_report_includes_frequency_tracks(tmp_config):
    report = assemble_report(_make_window(), _make_window(), [], [], [], tmp_config)

    assert report["windows"]["state"]["top_frequency_tracks"] == [
        {"uri": "spotify:track:freq", "qualified_play_count": 3, "play_count": 3}
    ]


def test_write_report_deterministic(tmp_path, tmp_config):
    state = _make_window()
    report = assemble_report(state, _make_window(), [], [], [], tmp_config)

    path1 = tmp_path / "report1.json"
    path2 = tmp_path / "report2.json"

    report_copy = json.loads(json.dumps(report))
    hash1 = write_report(report, path1)
    hash2 = write_report(report_copy, path2)
    assert hash1 == hash2


def test_write_report_creates_file(tmp_path, tmp_config):
    report = assemble_report(_make_window(), _make_window(), [], [], [], tmp_config)
    path = tmp_path / "reports" / "test.json"
    write_report(report, path)
    assert path.exists()
    data = json.loads(path.read_text())
    assert "generated_at" in data
