import sys
from pathlib import Path

# Ensure project root is on sys.path for imports during tests
# project_root points to repository root
project_root = Path(__file__).resolve().parent.parent
# Ensure repo root is on sys.path
sys.path.insert(0, str(project_root))
# Also add interface and core folders so imports like `components` and `visualizer`
# resolve during tests (app normally mutates sys.path at runtime).
sys.path.insert(0, str(project_root / "03_interface"))
sys.path.insert(0, str(project_root / "02_core"))

import pytest


@pytest.fixture(autouse=True)
def isolate_session_state(monkeypatch):
    """Provide a clean Streamlit session_state for tests that import streamlit.
    We monkeypatch streamlit.session_state if Streamlit is imported.
    """
    try:
        import streamlit as st

        # Provide a poppable dict-like session_state for tests
        class _DummySession(dict):
            def __getattr__(self, item):
                return self.get(item)

        dummy = _DummySession()
        monkeypatch.setattr(st, "session_state", dummy, raising=False)
    except Exception:
        # Streamlit not installed in this environment; tests will mock further as needed
        pass
