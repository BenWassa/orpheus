"""Shared styling utilities for the Streamlit interface."""

import streamlit as st


GLOBAL_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700&display=swap');

    :root {
        --color-primary: #6c63ff;
        --color-accent: #ff6584;
        --color-surface: #ffffff;
        --color-muted: #f5f6ff;
        --color-text: #1f1f2e;
        --color-subtle: #6b7280;
        --card-radius: 1.25rem;
        --shadow-soft: 0 20px 45px rgba(76, 70, 180, 0.12);
    }

    html, body, [class*="css"]  {
        font-family: 'Manrope', sans-serif;
    }

    .main-header {
        font-size: 2.75rem;
        color: var(--color-text);
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 700;
        letter-spacing: -0.01em;
    }

    .subtitle {
        text-align: center;
        color: var(--color-subtle);
        font-size: 1.15rem;
        margin-bottom: 2.5rem;
    }

    .metric-card {
        background: var(--color-surface);
        padding: 1.5rem;
        border-radius: var(--card-radius);
        box-shadow: var(--shadow-soft);
        border: 1px solid rgba(108, 99, 255, 0.08);
    }

    .insight-card {
        /* slightly stronger background and lighter text for better contrast and readability */
        background: linear-gradient(135deg, rgba(108, 99, 255, 0.14), rgba(255, 101, 132, 0.12));
        padding: 1.5rem;
        border-radius: var(--card-radius);
        border: 1px solid rgba(108, 99, 255, 0.12);
        color: var(--color-subtle);
    }

    .insight-card p {
        margin: 0;
        font-size: 1.1rem;
        color: inherit; /* inherit the softer color from the card */
    }

    .emotion-summary {
        background: var(--color-muted);
        border-radius: var(--card-radius);
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.6);
    }

    .stDownloadButton button {
        border-radius: 999px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        background: var(--color-primary);
        color: white;
        border: none;
        box-shadow: var(--shadow-soft);
    }

    .stDownloadButton button:hover {
        background: #5147ff;
        color: white;
    }
</style>
"""


def inject_global_styles() -> None:
    """Inject the shared CSS theme into the Streamlit app."""

    st.markdown(GLOBAL_STYLE, unsafe_allow_html=True)
