import importlib
from types import SimpleNamespace


def make_dummy_st():
    class DummySt:
        def __init__(self):
            class DummySession(dict):
                def __getattr__(self, item):
                    return self.get(item)

                def __setattr__(self, key, value):
                    self[key] = value

            self.session_state = DummySession()

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

        def error(self, *args, **kwargs):
            return None

    return DummySt()


def test_load_sample_dataset(monkeypatch, tmp_path):
    # Prepare a fake CSV file in DATA_DIR_RAW
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

    st = make_dummy_st()
    monkeypatch.setattr(app_mod, 'st', st, raising=False)

    app_mod.load_sample_data()

    assert 'df_processed' in st.session_state
    assert st.session_state.get('__rerun_called__') is True


def test_analyze_uploaded_file(monkeypatch, tmp_path):
    # Create a fake uploaded file object with getbuffer()
    class FakeUploaded:
        def __init__(self, path):
            self.name = path.name

        def getbuffer(self):
            return b"track_name,artist_name\nSongA,ArtistA\n"

    app_mod = importlib.import_module('03_interface.streamlit_app')
    monkeypatch.setattr(app_mod, 'DATA_DIR_RAW', tmp_path)

    def fake_load(path):
        import pandas as pd

        # path may be a str; read_csv works with a Path-like or string
        from pathlib import Path

        p = Path(path)
        return pd.read_csv(p)

    def fake_clean(df):
        return df

    monkeypatch.setattr(app_mod, 'cached_load_exportify', fake_load)
    monkeypatch.setattr(app_mod, 'cached_clean', fake_clean)

    st = make_dummy_st()
    monkeypatch.setattr(app_mod, 'st', st, raising=False)

    uploaded = FakeUploaded(tmp_path / "upload.csv")
    app_mod.analyze_uploaded_data(uploaded)

    assert 'df_processed' in st.session_state
    assert st.session_state.get('__rerun_called__') is True
import importlib


def test_load_sample_data(monkeypatch, tmp_path):
    fake_csv = tmp_path / "fake_export.csv"
    fake_csv.write_text("track_name,artist_name\nSong1,Artist1\nSong2,Artist2\n")

    app_mod = importlib.import_module('03_interface.streamlit_app')
    monkeypatch.setattr(app_mod, 'DATA_DIR_RAW', tmp_path)

    def test_placeholder():
        # Placeholder to keep test collection stable while other tests are being refined
        assert True
        return pd.read_csv(path)
