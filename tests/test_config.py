from __future__ import annotations


import pytest

from orpheus.config import load_config, validate_config


def test_load_config_from_template(tmp_project):
    cfg = load_config(project_root=tmp_project)
    assert cfg.windows.state_half_life_days == 3.0
    assert cfg.windows.trait_half_life_days == 90.0
    assert cfg.clustering.gmm_components == 3
    assert cfg.safety.active is False


def test_load_config_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="config.yaml"):
        load_config(project_root=tmp_path)


def test_validate_config_valid(tmp_config):
    errors = validate_config(tmp_config)
    assert errors == []


def test_validate_config_bad_half_life(tmp_config):
    tmp_config.windows.state_half_life_days = -1
    errors = validate_config(tmp_config)
    assert any("state_half_life_days" in e for e in errors)


def test_validate_config_bad_dbscan(tmp_config):
    tmp_config.clustering.dbscan_min_pts = 1
    errors = validate_config(tmp_config)
    assert any("dbscan_min_pts" in e for e in errors)


def test_depth_labels_loaded(tmp_config):
    assert len(tmp_config.depth_labels) == 3
    assert tmp_config.depth_labels[0].label == "surface"
    assert tmp_config.depth_labels[2].label == "immersive"


def test_model_version_string(tmp_config):
    assert "bart-large-mnli" in tmp_config.model_version
    assert "mpnet" in tmp_config.model_version


def test_path_resolution(tmp_config):
    assert tmp_config.db_path.name == "orpheus.db"
    assert tmp_config.reports_dir.name == "reports"
