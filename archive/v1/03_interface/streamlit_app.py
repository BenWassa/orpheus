#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🎵 Project Orpheus - Streamlit Dashboard"""

import logging
import sys
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# Configure environment noise
warnings.filterwarnings('ignore')
plt.style.use('default')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 10

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add core modules to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "02_core"))

# Import core modules with error handling
try:  # pragma: no cover - handled at runtime
    from config import DATA_DIR_RAW
    MODULES_LOADED = True
except ImportError as exc:  # pragma: no cover - handled at runtime
    MODULES_LOADED = False
    st.error(f"❌ Could not import core modules: {exc}")
    st.error("🔧 Ensure you're running from the project root directory")
    st.stop()

from components import (  # noqa: E402  (import after sys.path adjustment)
    inject_global_styles,
    render_emotions,
    render_overview,
    render_patterns,
    render_reflections,
    render_sidebar,
    render_visualizations,
)
from components.data_pipeline import (  # noqa: E402
    cached_add_lyric_sentiment,
    cached_add_spotify_audio_features,
    cached_clean,
    cached_compute_emotion_summary,
    cached_emotion_summary_text,
    cached_load_exportify,
    cached_playlist_stats,
    cached_repeat_obsessions,
    cached_temporal_patterns,
)

st.set_page_config(
    page_title="🎵 Project Orpheus",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    """Run the Streamlit application."""

    inject_global_styles()
    st.markdown('<h1 class="main-header">🎵 Project Orpheus</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Decode your emotional underworld through music</p>',
        unsafe_allow_html=True,
    )

    # Apply pending navigation choice (set by callbacks) before widgets are created
    if 'nav_choice_pending' in st.session_state:
        st.session_state['nav_choice'] = st.session_state.pop('nav_choice_pending')

    if 'nav_choice' not in st.session_state:
        st.session_state['nav_choice'] = 'Overview'

    data_available = 'df_processed' in st.session_state
    nav_choice, uploaded_file = render_sidebar(data_available=data_available)

    if uploaded_file is not None and uploaded_file.name:
        analyze_uploaded_data(uploaded_file)
        return

    if 'df_processed' in st.session_state:
        show_analysis_results(st.session_state.df_processed, nav_choice)
    else:
        show_welcome_screen()


def show_welcome_screen() -> None:
    """Display welcome content with sample data option."""

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 🌙 Welcome to Your Musical Journey")
        st.write(
            "Just as Orpheus journeyed into the underworld with music as his guide, "
            "Project Orpheus helps you descend into your emotional depths — not to dwell "
            "in darkness, but to retrieve hidden truths, lost memories, and fresh self-understanding."
        )

        st.markdown("### 🔍 How It Works")
        st.markdown(
            "1. **Export** your Spotify playlists using [Exportify](https://github.com/watsonbox/exportify)\n"
            "2. **Upload** the CSV file using the sidebar\n"
            "3. **Discover** patterns, obsessions, and emotional themes in your music\n"
            "4. **Reflect** on your musical journey and what it reveals about you"
        )

        st.markdown("### 🎮 Try with Sample Data")
        if st.button("Load Sample Dataset", type="primary"):
            load_sample_data()


def load_sample_data() -> None:
    """Load and analyze bundled sample data."""
    try:
        sample_files = list(DATA_DIR_RAW.glob("*.csv"))
        if not sample_files:
            st.error("No sample CSV files found in 04_data/raw/ directory")
            return

        sample_file = sample_files[0]
        st.success(f"Loading sample data: {sample_file.name}")

        with st.spinner("Preparing sample data..."):
            df_raw = cached_load_exportify(str(sample_file))
            df_clean = cached_clean(df_raw)

        # Persist processed data and schedule nav change for next run
        st.session_state.df_processed = df_clean
        st.session_state.sample_data = True
        # Defer changing the widget-backed nav_choice until the next run
        st.session_state['nav_choice_pending'] = 'Overview'
        st.rerun()
    except Exception as exc:  # pragma: no cover - runtime feedback
        st.error(f"Error loading sample data: {exc}")


def analyze_uploaded_data(uploaded_file) -> None:
    """Persist and analyze the uploaded Exportify CSV."""
    try:
        temp_path = DATA_DIR_RAW / uploaded_file.name
        with open(temp_path, "wb") as handle:
            handle.write(uploaded_file.getbuffer())

        with st.spinner("Loading and cleaning data..."):
            df_raw = cached_load_exportify(str(temp_path))
            df_clean = cached_clean(df_raw)

        st.success(f"Successfully processed {len(df_clean)} tracks")
        st.session_state.df_processed = df_clean
        st.session_state.sample_data = False
        # Defer changing the widget-backed nav_choice until the next run
        st.session_state['nav_choice_pending'] = 'Overview'
        st.rerun()
    except Exception as exc:  # pragma: no cover - runtime feedback
        st.error(f"Error processing file: {exc}")


def show_analysis_results(df: pd.DataFrame, nav_choice: str) -> None:
    """Display the chosen analysis section."""

    is_sample = st.session_state.get('sample_data', False)

    if nav_choice == 'Overview':
        with st.spinner("Crunching playlist statistics..."):
            stats = cached_playlist_stats(df)
        render_overview(df, stats, is_sample=is_sample)
        return

    if nav_choice == 'Patterns':
        with st.spinner("Crunching playlist statistics..."):
            stats = cached_playlist_stats(df)
        render_patterns(
            df,
            stats,
            load_repeat_obsessions=cached_repeat_obsessions,
            load_temporal_patterns=cached_temporal_patterns,
        )
        return

    if nav_choice == 'Visualizations':
        render_visualizations(df)
        return

    # Emotions and Reflections require enriched data
    with st.spinner("Enriching tracks with audio features..."):
        df_with_audio = cached_add_spotify_audio_features(df)

    with st.spinner("Analyzing lyric sentiment..."):
        emotion_ready_df = cached_add_lyric_sentiment(df_with_audio)

    with st.spinner("Synthesizing emotional summary..."):
        emotion_summary = cached_compute_emotion_summary(emotion_ready_df)

    summary_text = cached_emotion_summary_text(emotion_summary)

    if nav_choice == 'Emotions':
        render_emotions(emotion_ready_df, emotion_summary)
    elif nav_choice == 'Reflections':
        render_reflections(emotion_summary, summary_text)
    else:
        st.info("Select a section from the sidebar to continue your exploration.")


if __name__ == "__main__":
    if MODULES_LOADED:
        main()
    else:  # pragma: no cover - runtime guard
        st.error("Cannot start application - core modules failed to load")
