"""Visualization gallery component."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from visualizer import (
    plot_emotion_timeline,
    plot_top_artists,
    plot_audio_features_radar,
)
from components.data_pipeline import (
    cached_add_spotify_audio_features,
    cached_compute_emotion_summary,
)


def render_visualizations(df: pd.DataFrame) -> None:
    """Render key visualizations for the dashboard."""

    st.header("📈 Visual Narratives")

    st.subheader("📅 Music Timeline")
    # Enrich dataframe with audio features (cached) so plots can use valence/energy
    with st.spinner("Enriching data with audio features..."):
        df_enriched = cached_add_spotify_audio_features(df)

    # compute a lightweight emotion summary (cached) which may be used by other components
    with st.spinner("Computing emotion summary..."):
        _ = cached_compute_emotion_summary(df_enriched)

    with st.spinner("Painting your emotional timeline..."):
        fig_timeline = plot_emotion_timeline(df_enriched)
    st.pyplot(fig_timeline, use_container_width=True)

    st.subheader("🎤 Top Artists")
    n_artists = st.slider(
        "Number of artists to spotlight",
        min_value=5,
        max_value=25,
        value=10,
        key="top_artists_slider",
    )
    with st.spinner("Highlighting your most played artists..."):
        fig_artists = plot_top_artists(df_enriched, n=n_artists)
    st.pyplot(fig_artists, use_container_width=True)

    st.subheader("🎵 Audio Features")
    with st.spinner("Mapping your sonic palette..."):
        fig_radar = plot_audio_features_radar(df_enriched)
    st.pyplot(fig_radar, use_container_width=True)
