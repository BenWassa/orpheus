"""Sidebar navigation and data controls for the dashboard."""

from __future__ import annotations

from typing import Any, Optional, Tuple

import streamlit as st

NAV_ITEMS = {
    "Overview": "📊 Overview",
    "Patterns": "🎧 Patterns",
    "Visualizations": "📈 Visualizations",
    "Emotions": "💜 Emotions",
    "Reflections": "🪞 Reflections",
}


def render_sidebar(data_available: bool) -> Tuple[str, Optional[Any]]:
    """Render the sidebar with navigation and upload controls."""

    st.sidebar.markdown("### 🎛️ Navigation")
    nav_choice = st.sidebar.radio(
        "Navigation",
        options=list(NAV_ITEMS.keys()),
        format_func=lambda key: NAV_ITEMS[key],
        label_visibility="collapsed",
        disabled=not data_available,
        key="nav_choice",
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📁 Data Upload")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Exportify CSV",
        type=["csv"],
        help="Drop your Spotify Exportify CSV here to begin the analysis.",
    )

    return nav_choice, uploaded_file
