"""Cached data utilities to keep the dashboard responsive."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from data_processor import load_exportify, clean
from pattern_analyzer import playlist_stats, repeat_obsessions, temporal_patterns
from emotion_analyzer import (
    add_spotify_audio_features,
    add_lyric_sentiment,
    compute_emotion_summary,
)
from visualizer import create_emotion_summary_text


@st.cache_data(show_spinner=False)
def cached_load_exportify(path_str: str) -> pd.DataFrame:
    """Load CSV data with caching support."""

    return load_exportify(Path(path_str))


@st.cache_data(show_spinner=False)
def cached_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw data with caching."""

    return clean(df)


@st.cache_data(show_spinner=False)
def cached_playlist_stats(df: pd.DataFrame) -> dict[str, Any]:
    """Compute playlist statistics with caching."""

    return playlist_stats(df)


@st.cache_data(show_spinner=False)
def cached_repeat_obsessions(df: pd.DataFrame, threshold: int) -> pd.DataFrame:
    """Detect repeat obsessions with caching."""

    return repeat_obsessions(df, threshold=threshold)


@st.cache_data(show_spinner=False)
def cached_temporal_patterns(df: pd.DataFrame) -> dict[str, Any]:
    """Analyze temporal patterns with caching."""

    return temporal_patterns(df)


@st.cache_data(show_spinner=False)
def cached_add_spotify_audio_features(df: pd.DataFrame) -> pd.DataFrame:
    """Augment tracks with Spotify audio features using caching."""

    return add_spotify_audio_features(df)


@st.cache_data(show_spinner=False)
def cached_add_lyric_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """Add lyric sentiment markers with caching."""

    return add_lyric_sentiment(df)


@st.cache_data(show_spinner=False)
def cached_compute_emotion_summary(df: pd.DataFrame) -> dict[str, Any]:
    """Compute emotional summary statistics with caching."""

    return compute_emotion_summary(df)


@st.cache_data(show_spinner=False)
def cached_emotion_summary_text(summary: dict[str, Any]) -> str:
    """Create the downloadable emotion summary text."""

    return create_emotion_summary_text(summary)
