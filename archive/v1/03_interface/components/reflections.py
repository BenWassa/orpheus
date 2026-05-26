"""Reflection space component."""

from __future__ import annotations

from typing import Dict, Any

import streamlit as st


def render_reflections(emotion_summary: Dict[str, Any], summary_text: str) -> None:
    """Render the reflective journaling section."""

    st.header("🪞 Reflections Studio")
    st.caption("Translate sonic data into self-knowledge and intentional rituals.")

    st.subheader("📝 Download & Reflect")
    st.download_button(
        label="Download Emotion Report",
        data=summary_text,
        file_name="orpheus_emotion_report.txt",
        mime="text/plain",
    )

    st.text_area(
        "What patterns surprised you?",
        placeholder="Jot down the memories, moods, or relationships these songs point you toward...",
        key="reflection_notes",
        height=160,
    )

    if emotion_summary.get('recommendations'):
        st.subheader("✨ Suggested Rituals")
        for recommendation in emotion_summary['recommendations']:
            st.markdown(f"- {recommendation}")
    else:
        st.info("Emotional recommendations will unlock once your dataset includes audio features or lyric sentiment.")

    st.subheader("📬 Share the Journey")
    st.write(
        "Consider revisiting this dashboard each month. Capture how your emotional soundtrack evolves and what it asks of you."
    )
