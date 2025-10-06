"""Listening pattern analysis component."""

from __future__ import annotations

from typing import Callable, Dict

import pandas as pd
import streamlit as st


RepeatLoader = Callable[[pd.DataFrame, int], pd.DataFrame]
TemporalLoader = Callable[[pd.DataFrame], Dict[str, object]]


def render_patterns(
    df: pd.DataFrame,
    stats: Dict[str, object],
    *,
    load_repeat_obsessions: RepeatLoader,
    load_temporal_patterns: TemporalLoader,
) -> None:
    """Render the listening patterns section."""

    st.header("🎧 Listening Patterns")

    highlight_cols = st.columns(3)
    with highlight_cols[0]:
        st.metric("Most Common Artist", stats.get('most_common_artist', '—'))
    with highlight_cols[1]:
        st.metric("Most Common Album", stats.get('most_common_album', '—'))
    with highlight_cols[2]:
        st.metric("Total Tracks", f"{stats.get('total_tracks', len(df)):,}")

    st.subheader("🔥 Repeat Obsessions")
    threshold = st.slider(
        "Obsession threshold (number of plays)",
        min_value=2,
        max_value=25,
        value=5,
        help="Tracks, artists, or albums appearing at or above this count will be highlighted.",
    )

    with st.spinner("Analyzing repeat plays..."):
        obsessions_df = load_repeat_obsessions(df, threshold)

    if not obsessions_df.empty:
        obsessions_df = obsessions_df.reset_index(drop=True)
        obsessions_df['percentage'] = obsessions_df['percentage'].map(lambda x: f"{x:.1f}%")
        st.dataframe(obsessions_df, use_container_width=True)
    else:
        st.info("No obsessions detected at this threshold. Try lowering it to surface more patterns.")

    st.subheader("🕰 Temporal Rhythms")
    with st.spinner("Mapping your listening timeline..."):
        temporal = load_temporal_patterns(df)

    temporal_cols = st.columns(2)
    monthly_dist = temporal.get('monthly_distribution') or {}
    weekly_dist = temporal.get('weekly_distribution') or {}

    if monthly_dist:
        monthly_series = pd.Series(monthly_dist).sort_index()
        with temporal_cols[0]:
            st.markdown("**Monthly cadence**")
            st.bar_chart(monthly_series)
    else:
        with temporal_cols[0]:
            st.info("Add dates to your Exportify export to unlock monthly trends.")

    if weekly_dist:
        weekly_series = pd.Series(weekly_dist).sort_index()
        with temporal_cols[1]:
            st.markdown("**Weekly cadence**")
            st.line_chart(weekly_series)
    else:
        with temporal_cols[1]:
            st.info("Weekly listening patterns will appear when timestamp data is available.")

    peak = temporal.get('peak_periods')
    if peak:
        st.success(
            f"Your peak month was **{peak['peak_month']}** with **{int(peak['peak_count'])}** tracks — "
            f"about {peak['average_monthly']:.1f} plays on average."
        )
