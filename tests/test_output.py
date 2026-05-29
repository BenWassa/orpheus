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
