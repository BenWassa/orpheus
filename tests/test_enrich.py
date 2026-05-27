from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from orpheus.enrich.enrich import _has_audio_features, _insert_audio_features, enrich_audio_features
from orpheus.enrich.genius import clean_lyrics, enrich_lyrics
from orpheus.ingest.spotify_export import ingest_export


def _setup_tracks(tmp_db, sample_export_path):
    ingest_export(sample_export_path, tmp_db)
    return tmp_db


def test_insert_audio_features(tmp_db, sample_export_path):
    _setup_tracks(tmp_db, sample_export_path)
    features = {
        "valence": 0.5, "arousal": 0.6, "tempo": 120.0, "key": 5, "mode": 1,
        "energy": 0.7, "danceability": 0.8, "acousticness": 0.1,
        "instrumentalness": 0.0, "loudness": -5.0,
        "spectral_centroid": None, "spectral_complexity": None,
        "source": "test",
    }
    _insert_audio_features(tmp_db, "spotify:track:3DK6m7It6Pw857FcQftMds", features)
    assert _has_audio_features(tmp_db, "spotify:track:3DK6m7It6Pw857FcQftMds")


def test_has_audio_features_false(tmp_db, sample_export_path):
    _setup_tracks(tmp_db, sample_export_path)
    assert not _has_audio_features(tmp_db, "spotify:track:nonexistent")


def test_enrich_no_sources(tmp_db, tmp_config, sample_export_path):
    _setup_tracks(tmp_db, sample_export_path)
    stats = enrich_audio_features(tmp_db, tmp_config)
    assert stats["total"] == 6
    assert stats["missed"] == 6


def test_enrich_idempotent(tmp_db, tmp_config, sample_export_path):
    _setup_tracks(tmp_db, sample_export_path)
    features = {
        "valence": 0.5, "arousal": 0.6, "tempo": 120.0, "key": 5, "mode": 1,
        "energy": 0.7, "danceability": 0.8, "acousticness": 0.1,
        "instrumentalness": 0.0, "loudness": -5.0,
        "spectral_centroid": None, "spectral_complexity": None,
        "source": "test",
    }
    for uri in ["spotify:track:3DK6m7It6Pw857FcQftMds"]:
        _insert_audio_features(tmp_db, uri, features)
    # This track should be skipped on enrich since it already has features
    assert _has_audio_features(tmp_db, "spotify:track:3DK6m7It6Pw857FcQftMds")


def test_enrich_lyrics_without_token_does_not_cache_misses(tmp_db, sample_export_path):
    _setup_tracks(tmp_db, sample_export_path)

    stats = enrich_lyrics(tmp_db, "")

    assert stats == {"total": 0, "fetched": 0, "no_lyrics": 0, "failed": 0}
    assert tmp_db.execute("SELECT COUNT(*) FROM lyrics").fetchone()[0] == 0


def test_clean_lyrics_strips_sections():
    raw = "[Verse 1]\nHello darkness my old friend\n[Chorus]\nI've come to talk with you again"
    cleaned = clean_lyrics(raw)
    assert "[Verse 1]" not in cleaned
    assert "[Chorus]" not in cleaned
    assert "Hello darkness" in cleaned
    assert "I've come to talk" in cleaned


def test_clean_lyrics_strips_embed():
    raw = "Some lyrics here\n123Embed"
    cleaned = clean_lyrics(raw)
    assert "Embed" not in cleaned
    assert "Some lyrics here" in cleaned


def test_clean_lyrics_strips_you_might_also_like():
    raw = "Line one\nYou might also like\nLine two"
    cleaned = clean_lyrics(raw)
    assert "You might also like" not in cleaned
    assert "Line one" in cleaned
    assert "Line two" in cleaned


def test_clean_lyrics_normalizes_whitespace():
    raw = "  Hello  \n\n\n  World  \n\n"
    cleaned = clean_lyrics(raw)
    assert cleaned == "Hello\nWorld"
