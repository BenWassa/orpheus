#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎵 Project Orpheus - Streamlit Dashboard

A clean web interface for music listening pattern analysis.
Run from project root: streamlit run 03_interface/streamlit_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
import warnings
import logging

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Configure matplotlib for web
plt.style.use('default')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 10

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add core modules to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "02_core"))

# Import core modules with error handling
try:
    from data_processor import load_exportify, clean
    from pattern_analyzer import playlist_stats, repeat_obsessions, temporal_patterns
    from emotion_analyzer import add_spotify_audio_features, add_lyric_sentiment, compute_emotion_summary
    from visualizer import plot_emotion_timeline, plot_top_artists, plot_audio_features_radar
    from config import DATA_DIR_RAW, DATA_DIR_PROCESSED
    MODULES_LOADED = True
except ImportError as e:
    MODULES_LOADED = False
    st.error(f"❌ Could not import core modules: {e}")
    st.error("🔧 Ensure you're running from the project root directory")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="🎵 Project Orpheus",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f1f2e;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        border: 1px solid #e9ecef;
    }
    .insight-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🎵 Project Orpheus</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Decode your emotional underworld through music</p>', 
               unsafe_allow_html=True)
    
    # Sidebar for file upload
    st.sidebar.title("📁 Data Upload")
    uploaded_file = st.sidebar.file_uploader(
        "Choose CSV file",
        type=['csv'],
        help="Upload your Exportify CSV file"
    )
    
    # Main content
    if uploaded_file is not None:
        analyze_uploaded_data(uploaded_file)
    elif 'df_processed' in st.session_state:
        show_analysis_results(st.session_state.df_processed)
    else:
        show_welcome_screen()


def show_welcome_screen():
    """Display welcome screen with sample data option"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 🌙 Welcome to Your Musical Journey")
        
        st.markdown("""
        Just as Orpheus journeyed into the underworld with music as his guide, 
        Project Orpheus helps you descend into your emotional depths — not to dwell 
        in darkness, but to retrieve hidden truths, lost memories, and fresh self-understanding.
        """)
        
        st.markdown("### 🔍 How It Works")
        st.markdown("""
        1. **Export** your Spotify playlists using [Exportify](https://github.com/watsonbox/exportify)
        2. **Upload** the CSV file using the sidebar
        3. **Discover** patterns, obsessions, and emotional themes in your music
        4. **Reflect** on your musical journey and what it reveals about you
        """)
        
        st.markdown("### 🎮 Try with Sample Data")
        if st.button("Load Sample Dataset", type="primary"):
            load_sample_data()


def load_sample_data():
    """Load and analyze sample data"""
    try:
        # Look for existing sample data
        sample_files = list(DATA_DIR_RAW.glob("*.csv"))
        
        if sample_files:
            sample_file = sample_files[0]
            st.success(f"Loading sample data: {sample_file.name}")
            
            # Load and process
            df_raw = load_exportify(sample_file)
            df_clean = clean(df_raw)
            
            # Store in session state
            st.session_state.df_processed = df_clean
            st.session_state.sample_data = True
            
            # Rerun to show analysis
            st.rerun()
        else:
            st.error("No sample CSV files found in 04_data/raw/ directory")
            
    except Exception as e:
        st.error(f"Error loading sample data: {e}")


def analyze_uploaded_data(uploaded_file):
    """Analyze uploaded CSV data"""
    
    try:
        # Save uploaded file temporarily
        temp_path = DATA_DIR_RAW / uploaded_file.name
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Load and process
        with st.spinner("Loading and cleaning data..."):
            df_raw = load_exportify(temp_path)
            df_clean = clean(df_raw)
        
        st.success(f"Successfully processed {len(df_clean)} tracks")
        
        # Store in session state
        st.session_state.df_processed = df_clean
        st.session_state.sample_data = False
        
        # Display analysis
        show_analysis_results(df_clean)
        
    except Exception as e:
        st.error(f"Error processing file: {e}")


def show_analysis_results(df: pd.DataFrame):
    """Display comprehensive analysis results"""
    
    # Tabs for different analysis sections
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "🎵 Patterns", "📈 Visualizations"])
    
    with tab1:
        show_overview_analysis(df)
    
    with tab2:
        show_pattern_analysis(df)
    
    with tab3:
        show_visualizations(df)


def show_overview_analysis(df: pd.DataFrame):
    """Display basic statistics and overview"""
    
    st.header("📊 Dataset Overview")
    
    # Basic metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tracks", len(df))
    
    with col2:
        if 'artist_name' in df.columns:
            unique_artists = df['artist_name'].nunique()
            st.metric("Unique Artists", unique_artists)
        else:
            st.metric("Unique Artists", "N/A")
    
    with col3:
        if 'album_name' in df.columns:
            unique_albums = df['album_name'].nunique()
            st.metric("Unique Albums", unique_albums)
        else:
            st.metric("Unique Albums", "N/A")
    
    with col4:
        if 'popularity' in df.columns:
            avg_popularity = df['popularity'].mean()
            st.metric("Avg Popularity", f"{avg_popularity:.1f}")
        else:
            st.metric("Avg Popularity", "N/A")
    
    # Data preview
    st.subheader("📋 Data Preview")
    st.dataframe(df.head(10), use_container_width=True)


def show_pattern_analysis(df: pd.DataFrame):
    """Display pattern analysis results"""
    
    st.header("🎵 Listening Patterns")
    
    try:
        # Get basic stats
        stats = playlist_stats(df)
        
        # Obsessions
        st.subheader("🔥 Musical Obsessions")
        threshold = st.slider("Obsession Threshold", min_value=2, max_value=20, value=5)
        
        obsessions_df = repeat_obsessions(df, threshold=threshold)
        
        if len(obsessions_df) > 0:
            st.dataframe(obsessions_df, use_container_width=True)
            
            # Insights
            st.markdown('<div class="insight-box">', unsafe_allow_html=True)
            st.markdown("**🔮 Pattern Insights:**")
            for _, row in obsessions_df.head(3).iterrows():
                st.markdown(f"- You have a {row['type']} obsession with **{row['name']}** ({row['count']} occurrences)")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info(f"No obsessions found above threshold of {threshold} occurrences")
            
    except Exception as e:
        st.error(f"Error in pattern analysis: {e}")


def show_visualizations(df: pd.DataFrame):
    """Display visualizations"""
    
    st.header("📈 Visualizations")
    
    try:
        # Timeline
        st.subheader("📅 Music Timeline")
        fig_timeline = plot_emotion_timeline(df)
        st.pyplot(fig_timeline)
        
        # Top artists
        st.subheader("🎤 Top Artists")
        n_artists = st.slider("Number of artists to show", min_value=5, max_value=25, value=10)
        fig_artists = plot_top_artists(df, n=n_artists)
        st.pyplot(fig_artists)
        
        # Audio features radar
        st.subheader("🎵 Audio Features")
        fig_radar = plot_audio_features_radar(df)
        st.pyplot(fig_radar)
        
    except Exception as e:
        st.error(f"Error creating visualizations: {e}")


if __name__ == "__main__":
    if MODULES_LOADED:
        main()
    else:
        st.error("Cannot start application - core modules failed to load")
