from types import ModuleType
import importlib
import sys


def test_sidebar_radio_key_default(monkeypatch):
    # Minimal stub of streamlit.sidebar used by navigation renderer
    st_mod = ModuleType('streamlit')

    class Sidebar:
        def markdown(self, *args, **kwargs):
            return None

        def radio(self, label, options, format_func=None, label_visibility=None, disabled=False, key=None):
            return list(options)[0]

        def file_uploader(self, *args, **kwargs):
            return None

    setattr(st_mod, 'sidebar', Sidebar())
    monkeypatch.setitem(sys.modules, 'streamlit', st_mod)

    nav_mod = importlib.import_module('03_interface.components.navigation')
    choice, uploaded = nav_mod.render_sidebar(data_available=False)
    assert choice == 'Overview'
    assert uploaded is None
