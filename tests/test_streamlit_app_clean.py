import importlib


def test_load_sample_data_clean(monkeypatch, tmp_path):
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
            class DummySession(dict):
                def __getattr__(self, item):
                    return self.get(item)

                def __setattr__(self, key, value):
                    # map attribute set to dict item
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
            # mimic streamlit.error
            return None

    st = DummySt()
    monkeypatch.setattr(app_mod, 'st', st, raising=False)

    app_mod.load_sample_data()

    assert 'df_processed' in st.session_state
    assert st.session_state.get('__rerun_called__') is True
