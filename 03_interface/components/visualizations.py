"""Visualization gallery component."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from visualizer import (
    plot_emotion_timeline,
    plot_top_artists,
    plot_audio_features_radar,
)


def render_visualizations(df: pd.DataFrame) -> None:
    """Render key visualizations for the dashboard."""

    st.header("📈 Visual Narratives")

    st.subheader("📅 Music Timeline")
    with st.spinner("Painting your emotional timeline..."):
        fig_timeline = plot_emotion_timeline(df)
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
        fig_artists = plot_top_artists(df, n=n_artists)
    st.pyplot(fig_artists, use_container_width=True)

    st.subheader("🎵 Audio Features")
    with st.spinner("Mapping your sonic palette..."):
        fig_radar = plot_audio_features_radar(df)
    st.pyplot(fig_radar, use_container_width=True)
