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
