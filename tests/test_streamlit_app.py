import importlib


def test_load_sample_data(monkeypatch, tmp_path):
    fake_csv = tmp_path / "fake_export.csv"
    fake_csv.write_text("track_name,artist_name\nSong1,Artist1\nSong2,Artist2\n")

    app_mod = importlib.import_module('03_interface.streamlit_app')
    monkeypatch.setattr(app_mod, 'DATA_DIR_RAW', tmp_path)

    def fake_load(path):
        import pandas as pd

        return pd.read_csv(path)

    def fake_clean(df):
        return df

    monkeypatch.setattr(app_mod, 'cached_load_exportify', fake_load)
    monkeypatch.setattr(app_mod, 'cached_clean', fake_clean)

    class DummySt:
        def __init__(self):
            self.session_state = {}

        def spinner(self, *args, **kwargs):
            class _Ctxt:
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, tb):
                    return False

            return _Ctxt()

        def success(self, *args, **kwargs):
            return None

        def rerun(self):
            self.session_state['__rerun_called__'] = True

    st = DummySt()
    monkeypatch.setattr(app_mod, 'st', st, raising=False)

    app_mod.load_sample_data()

    assert 'df_processed' in st.session_state
    assert st.session_state.get('__rerun_called__') is True
import importlib


def test_load_sample_data(monkeypatch, tmp_path):
    fake_csv = tmp_path / "fake_export.csv"
    fake_csv.write_text("track_name,artist_name\nSong1,Artist1\nSong2,Artist2\n")

    app_mod = importlib.import_module('03_interface.streamlit_app')
    monkeypatch.setattr(app_mod, 'DATA_DIR_RAW', tmp_path)

    def fake_load(path):
        import pandas as pd

        return pd.read_csv(path)

    def fake_clean(df):
        return df

    monkeypatch.setattr(app_mod, 'cached_load_exportify', fake_load)
    monkeypatch.setattr(app_mod, 'cached_clean', fake_clean)

    class DummySt:
        def __init__(self):
            self.session_state = {}

        def spinner(self, *args, **kwargs):
            class _Ctxt:
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, tb):
                    return False

            return _Ctxt()

        def success(self, *args, **kwargs):
            return None

        def rerun(self):
            self.session_state['__rerun_called__'] = True

    st = DummySt()
    monkeypatch.setattr(app_mod, 'st', st, raising=False)

    app_mod.load_sample_data()
    assert 'df_processed' in st.session_state
    assert st.session_state.get('__rerun_called__') is True
import importlib
from types import ModuleType
from pathlib import Path


def test_load_sample_data(monkeypatch, tmp_path):
    # Prepare a fake CSV file in a temporary DATA_DIR_RAW
    fake_csv = tmp_path / "fake_export.csv"
    fake_csv.write_text("track_name,artist_name\nSong1,Artist1\nSong2,Artist2\n")

    # Import the app module and patch DATA_DIR_RAW and the cached functions
    app_mod = importlib.import_module('03_interface.streamlit_app')

    # Patch config DATA_DIR_RAW to point at tmp_path
    monkeypatch.setattr(app_mod, 'DATA_DIR_RAW', tmp_path)

    # Stub cached_load_exportify and cached_clean
    def fake_load(path):
        import pandas as pd
        return pd.read_csv(path)

    import importlib
    from types import ModuleType
    from pathlib import Path


    def test_load_sample_data(monkeypatch, tmp_path):
        # Prepare a fake CSV file in a temporary DATA_DIR_RAW
        fake_csv = tmp_path / "fake_export.csv"
        fake_csv.write_text("track_name,artist_name\nSong1,Artist1\nSong2,Artist2\n")

        # Import the app module and patch DATA_DIR_RAW and the cached functions
        app_mod = importlib.import_module('03_interface.streamlit_app')

        # Patch config DATA_DIR_RAW to point at tmp_path
        monkeypatch.setattr(app_mod, 'DATA_DIR_RAW', tmp_path)

        # Stub cached_load_exportify and cached_clean
        def fake_load(path):
            import pandas as pd
            return pd.read_csv(path)

        def fake_clean(df):
            return df

        monkeypatch.setattr(app_mod, 'cached_load_exportify', fake_load)
        monkeypatch.setattr(app_mod, 'cached_clean', fake_clean)

        # Provide a dummy streamlit object with session_state and rerun
        class DummySt:
            def __init__(self):
                self.session_state = {}

            def spinner(self, *args, **kwargs):
                class _Ctxt:
                    def __enter__(self):
                        import importlib


                        def test_load_sample_data(monkeypatch, tmp_path):
                            # Prepare a fake CSV file in a temporary DATA_DIR_RAW
                            fake_csv = tmp_path / "fake_export.csv"
                            fake_csv.write_text("track_name,artist_name\nSong1,Artist1\nSong2,Artist2\n")

                            # Import the app module and patch DATA_DIR_RAW and the cached functions
                            app_mod = importlib.import_module('03_interface.streamlit_app')

                            # Patch config DATA_DIR_RAW to point at tmp_path
                            monkeypatch.setattr(app_mod, 'DATA_DIR_RAW', tmp_path)

                            # Stub cached_load_exportify and cached_clean
                            def fake_load(path):
                                import pandas as pd

                                return pd.read_csv(path)

                            def fake_clean(df):
                                return df

                            monkeypatch.setattr(app_mod, 'cached_load_exportify', fake_load)
                            monkeypatch.setattr(app_mod, 'cached_clean', fake_clean)

                            # Provide a dummy streamlit object with session_state and rerun
                            class DummySt:
                                def __init__(self):
                                    self.session_state = {}

                                def spinner(self, *args, **kwargs):
                                    class _Ctxt:
                                        def __enter__(self):
                                            return self

                                        def __exit__(self, exc_type, exc, tb):
                                            return False

                                    return _Ctxt()

                                def success(self, *args, **kwargs):
                                    return None

                                def rerun(self):
                                    # indicate rerun called by setting a flag
                                    self.session_state['__rerun_called__'] = True

                            st = DummySt()
                            # Replace the app module's reference to streamlit so load_sample_data uses our dummy
                            monkeypatch.setattr(app_mod, 'st', st, raising=False)

                            # Call load_sample_data and assert session_state updated
                            app_mod.load_sample_data()
                            assert 'df_processed' in st.session_state
                            assert st.session_state.get('__rerun_called__') is True
