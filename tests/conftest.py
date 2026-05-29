from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from orpheus.config import load_config
from orpheus.db import ensure_schema, get_db

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project directory with config and data dirs."""
    for d in ["data/raw", "data/cache", "data/output/reports"]:
        (tmp_path / d).mkdir(parents=True)

    template = Path(__file__).parent.parent / "config.yaml.template"
    shutil.copy(template, tmp_path / "config.yaml")

    return tmp_path


@pytest.fixture
def tmp_config(tmp_project):
    """Load config from a temporary project directory."""
    return load_config(project_root=tmp_project)


@pytest.fixture
def tmp_db(tmp_config):
    """Create and return a connection to a temporary database with schema applied."""
    conn = get_db(tmp_config.db_path)
    ensure_schema(conn)
    yield conn
    conn.close()


@pytest.fixture
def sample_export_path():
    """Path to the sample Spotify export fixture."""
    return FIXTURES_DIR / "sample_export.json"
