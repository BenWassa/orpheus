"""Emotional insights component."""

from __future__ import annotations

from typing import Dict, Any

import pandas as pd
import streamlit as st


def _format_feature_block(title: str, stats: Dict[str, Any]) -> str:
    return (
        f"<div style='margin-bottom:1rem;'><div style='font-size:0.85rem;color:var(--color-subtle);text-transform:uppercase;'>{title}</div>"
        f"<div style='font-size:1.5rem;font-weight:700;color:var(--color-text);'>{stats.get('mean', 0):.2f}</div>"
        f"<div style='font-size:0.8rem;color:var(--color-subtle);'>± {stats.get('std', 0):.2f}</div></div>"
    )


def render_emotions(df: pd.DataFrame, emotion_summary: Dict[str, Any]) -> None:
    """Render the emotional insights section."""

    st.header("💜 Emotion Atlas")
    st.caption("A blended view of audio features and lyric sentiment to chart your emotional landscape.")

    st.subheader("🌈 Emotion Profile Summary")
    with st.expander("Explore your emotional fingerprint", expanded=True):
        audio_features = emotion_summary.get('audio_features', {})
        sentiment = emotion_summary.get('sentiment', {})
        emotion_profile = emotion_summary.get('emotion_profile', {})

        feature_cols = st.columns(len(audio_features) or 1)
        for idx, (feature, stats) in enumerate(audio_features.items()):
            with feature_cols[idx]:
                st.markdown(_format_feature_block(feature.title(), stats), unsafe_allow_html=True)

        if sentiment:
            st.markdown("---")
            sentiment_cols = st.columns(len(sentiment))
            for idx, (sentiment_name, stats) in enumerate(sentiment.items()):
                distribution = stats.get('distribution', {})
                positive = distribution.get('positive', 0)
                negative = distribution.get('negative', 0)
                neutral = distribution.get('neutral', 0)
                with sentiment_cols[idx]:
                    st.metric(
                        sentiment_name.replace('_', ' ').title(),
                        f"{stats.get('mean', 0):.2f}",
                        help=f"Positive: {positive} | Neutral: {neutral} | Negative: {negative}",
                    )

        if emotion_profile:
            st.markdown("---")
            emotion_cols = st.columns(len(emotion_profile))
            for idx, (emotion_name, score) in enumerate(emotion_profile.items()):
                with emotion_cols[idx]:
                    st.progress(min(max(score, 0), 1.0))
                    st.caption(f"{emotion_name.replace('emotion_', '').title()} — {score:.2f}")

    recommendations = emotion_summary.get('recommendations', [])
    if recommendations:
        st.subheader("🔮 Interpretive Notes")
        for rec in recommendations:
            st.markdown(f"- {rec}")

    st.subheader("🎚 Raw Emotion Signals")
    feature_columns = [
        'valence', 'energy', 'danceability', 'acousticness',
        'lyric_polarity', 'lyric_subjectivity',
        'emotion_joy', 'emotion_sadness', 'emotion_anger', 'emotion_fear'
    ]
    available_cols = [col for col in feature_columns if col in df.columns]

    if available_cols:
        st.dataframe(df[available_cols].head(20), use_container_width=True)
    else:
        st.info("Audio and lyric features will appear once enrichment finishes or if API credentials are configured.")
