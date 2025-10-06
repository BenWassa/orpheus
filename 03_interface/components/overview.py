"""Overview tab content."""

from __future__ import annotations

from typing import Dict

import pandas as pd
import streamlit as st

INSIGHT_MESSAGES = [
    "Your playlists are a living archive of feelings waiting to be decoded.",
    "Notice which artists appear when you need a lift versus when you seek reflection.",
    "Patterns in your listening often mirror patterns in your relationships.",
    "Revisit the songs you overplay—they hold keys to current emotional themes.",
]


def _render_metric(label: str, value: str | int | float) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div style="font-size:0.95rem;color:var(--color-subtle);text-transform:uppercase;letter-spacing:0.08em;">{label}</div>
            <div style="font-size:2rem;font-weight:700;color:var(--color-text);margin-top:0.25rem;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview(df: pd.DataFrame, stats: Dict[str, object], *, is_sample: bool) -> None:
    """Render the overview section with dataset insights."""

    st.header("📊 Dataset Overview")

    if is_sample:
        st.info("Showing insights from the sample dataset. Upload your own Exportify export to personalize the journey.")

    # Metrics row
    metric_cols = st.columns(4)
    total_tracks = stats.get('total_tracks') or len(df)
    unique_artists = stats.get('unique_artists')
    if not unique_artists and 'artist_name' in df.columns:
        unique_artists = df['artist_name'].nunique()

    unique_albums = stats.get('unique_albums')
    if not unique_albums and 'album_name' in df.columns:
        unique_albums = df['album_name'].nunique()
    avg_popularity = stats.get('average_popularity')

    with metric_cols[0]:
        _render_metric("Total Tracks", f"{total_tracks:,}")

    with metric_cols[1]:
        _render_metric("Unique Artists", f"{unique_artists:,}" if unique_artists else "–")

    with metric_cols[2]:
        _render_metric("Unique Albums", f"{unique_albums:,}" if unique_albums else "–")

    with metric_cols[3]:
        popularity_value = f"{avg_popularity:.1f}" if avg_popularity is not None else "–"
        _render_metric("Avg. Popularity", popularity_value)

    # Date range
    date_range = stats.get('date_range')
    if date_range:
        span_cols = st.columns([1, 1, 1])
        with span_cols[0]:
            _render_metric("Earliest Add", date_range['earliest'].strftime('%b %d, %Y'))
        with span_cols[1]:
            _render_metric("Latest Add", date_range['latest'].strftime('%b %d, %Y'))
        with span_cols[2]:
            _render_metric("Listening Span", f"{date_range['span_days']} days")

    st.subheader("📋 First Look")
    st.dataframe(df.head(15), use_container_width=True)

    st.subheader("🔮 Your Music Mirror")
    carousel_container = st.container()
    index_key = "insight_carousel_index"
    if index_key not in st.session_state:
        st.session_state[index_key] = 0

    cols = carousel_container.columns([1, 4, 1])
    with cols[0]:
        if st.button("◀", key="insight_prev"):
            st.session_state[index_key] = (st.session_state[index_key] - 1) % len(INSIGHT_MESSAGES)
    with cols[1]:
        message = INSIGHT_MESSAGES[st.session_state[index_key]]
        st.markdown(
            f"<div class='insight-card'><p style='margin:0;font-size:1.1rem;'>{message}</p></div>",
            unsafe_allow_html=True,
        )
    with cols[2]:
        if st.button("▶", key="insight_next"):
            st.session_state[index_key] = (st.session_state[index_key] + 1) % len(INSIGHT_MESSAGES)
