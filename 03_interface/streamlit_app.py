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
    from data_processor import load_csv_data, clean_data
    from pattern_analyzer import analyze_patterns, find_obsessions
    from visualizer import create_timeline, create_top_artists, create_summary_stats
    MODULES_LOADED = True
except ImportError as e:
    st.error(f"❌ Could not import core modules: {e}")
    st.error("Please ensure you're running from the project root directory")
    MODULES_LOADED = False

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
    """Main application entry point"""
    
    if not MODULES_LOADED:
        st.stop()
    
    # Header
    st.markdown('<h1 class="main-header">🎵 Project Orpheus</h1>', unsafe_allow_html=True)
    st.markdown("**Decode your emotional underworld through music**", unsafe_allow_html=True)
    
    # Sidebar for file upload
    st.sidebar.title("📁 Upload Music Data")
    st.sidebar.markdown("Upload your Spotify playlist CSV files")
    
    uploaded_files = st.sidebar.file_uploader(
        "Select CSV files",
        type=['csv'],
        accept_multiple_files=True,
        help="Export playlists using Exportify and upload here"
    )
    
    # Sample data option
    st.sidebar.markdown("---")
    if st.sidebar.button("🎮 Load Sample Data"):
        load_sample_data()
    
    # Main content area
    if 'processed_data' in st.session_state:
        show_dashboard(st.session_state.processed_data)
    elif uploaded_files:
        process_uploaded_files(uploaded_files)
    else:
        show_welcome_screen()


def show_welcome_screen():
    """Display welcome screen with instructions"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 🌙 Welcome to Your Musical Journey")
        
        st.markdown("""
        Project Orpheus analyzes your Spotify listening patterns to reveal:
        
        - **🎵 Musical Obsessions**: Songs and artists you play repeatedly
        - **📈 Listening Trends**: How your taste evolves over time  
        - **💭 Emotional Patterns**: Mood analysis through music choices
        - **🔮 Personal Insights**: AI-generated recommendations
        """)
        
        st.markdown("### 🚀 Getting Started")
        st.markdown("""
        1. **Export** your Spotify data using [Exportify](https://github.com/watsonbox/exportify)
        2. **Upload** CSV files using the sidebar
        3. **Explore** your musical patterns and insights
        """)
        
        # Check for sample data
        sample_path = project_root / "04_data" / "raw"
        if sample_path.exists() and list(sample_path.glob("*.csv")):
            st.info("💡 Sample data available! Click 'Load Sample Data' in the sidebar to try it out.")


def load_sample_data():
    """Load sample data for demonstration"""
    
    try:
        sample_path = project_root / "04_data" / "raw"
        csv_files = list(sample_path.glob("*.csv"))
        
        if csv_files:
            st.success(f"Loading sample data: {csv_files[0].name}")
            
            with st.spinner("Processing sample data..."):
                df = load_csv_data(csv_files[0])
                df_clean = clean_data(df)
                
                st.session_state.processed_data = df_clean
                st.session_state.data_source = f"Sample: {csv_files[0].name}"
            
            st.rerun()
        else:
            st.error("No sample data found in 04_data/raw/")
            
    except Exception as e:
        st.error(f"Error loading sample data: {e}")


def process_uploaded_files(uploaded_files):
    """Process uploaded CSV files"""
    
    try:
        all_data = []
        
        with st.spinner(f"Processing {len(uploaded_files)} file(s)..."):
            for file in uploaded_files:
                # Save temporarily
                temp_path = project_root / "04_data" / "temp" / file.name
                temp_path.parent.mkdir(exist_ok=True)
                
                with open(temp_path, "wb") as f:
                    f.write(file.getbuffer())
                
                # Load and clean
                df = load_csv_data(temp_path)
                df_clean = clean_data(df)
                all_data.append(df_clean)
                
                # Clean up temp file
                temp_path.unlink()
        
        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)
        
        st.success(f"✅ Processed {len(combined_df)} total tracks from {len(uploaded_files)} file(s)")
        
        # Store in session
        st.session_state.processed_data = combined_df
        st.session_state.data_source = f"{len(uploaded_files)} uploaded file(s)"
        
        # Show dashboard
        show_dashboard(combined_df)
        
    except Exception as e:
        st.error(f"Error processing files: {e}")


def show_dashboard(df):
    """Display main analysis dashboard"""
    
    # Data source info
    data_source = st.session_state.get('data_source', 'Unknown')
    st.info(f"📊 **Analyzing**: {data_source} | **{len(df):,} tracks**")
    
    # Clear data button
    if st.button("🔄 Clear Data & Upload New"):
        for key in ['processed_data', 'data_source']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    # Analysis tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🎵 Patterns", "📈 Trends", "🔍 Deep Dive"])
    
    with tab1:
        show_overview_tab(df)
    
    with tab2:
        show_patterns_tab(df)
    
    with tab3:
        show_trends_tab(df)
    
    with tab4:
        show_deep_dive_tab(df)


def show_overview_tab(df):
    """Display overview statistics"""
    
    st.header("📊 Dataset Overview")
    
    try:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Tracks", f"{len(df):,}")
        
        with col2:
            unique_artists = df['artist_name'].nunique() if 'artist_name' in df.columns else 0
            st.metric("Unique Artists", f"{unique_artists:,}")
        
        with col3:
            unique_albums = df['album_name'].nunique() if 'album_name' in df.columns else 0
            st.metric("Unique Albums", f"{unique_albums:,}")
        
        with col4:
            date_span = "N/A"
            if 'added_at' in df.columns:
                try:
                    dates = pd.to_datetime(df['added_at'])
                    span = (dates.max() - dates.min()).days
                    date_span = f"{span} days"
                except:
                    pass
            st.metric("Date Range", date_span)
        
        # Top items
        st.subheader("🏆 Top Items")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'artist_name' in df.columns:
                top_artists = df['artist_name'].value_counts().head(10)
                st.markdown("**Top Artists:**")
                for artist, count in top_artists.items():
                    st.write(f"• {artist}: {count} tracks")
        
        with col2:
            if 'track_name' in df.columns:
                top_tracks = df['track_name'].value_counts().head(10)
                st.markdown("**Most Added Tracks:**")
                for track, count in top_tracks.items():
                    st.write(f"• {track}: {count}x")
        
        # Data preview
        st.subheader("📋 Data Sample")
        st.dataframe(df.head(10), use_container_width=True)
        
    except Exception as e:
        st.error(f"Error in overview analysis: {e}")


def show_patterns_tab(df):
    """Display pattern analysis"""
    
    st.header("🎵 Listening Patterns")
    
    try:
        # Obsession analysis
        st.subheader("🔥 Musical Obsessions")
        
        threshold = st.slider("Minimum plays to consider 'obsession'", 2, 20, 5)
        
        obsessions = find_obsessions(df, threshold)
        
        if len(obsessions) > 0:
            st.dataframe(obsessions, use_container_width=True)
            
            # Insights
            st.markdown('<div class="insight-box">', unsafe_allow_html=True)
            st.markdown("**🔮 Pattern Insights:**")
            
            for _, row in obsessions.head(3).iterrows():
                obsession_type = row.get('type', 'item')
                name = row.get('name', 'Unknown')
                count = row.get('count', 0)
                pct = (count / len(df)) * 100
                
                st.markdown(f"• **{name}** appears {count} times ({pct:.1f}% of your library)")
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info(f"No obsessions found with threshold of {threshold}+ plays")
        
        # Pattern visualization
        if 'artist_name' in df.columns:
            fig = create_top_artists(df, top_n=15)
            st.pyplot(fig)
        
    except Exception as e:
        st.error(f"Error in pattern analysis: {e}")


def show_trends_tab(df):
    """Display temporal trends"""
    
    st.header("📈 Listening Trends")
    
    try:
        if 'added_at' in df.columns:
            # Timeline visualization
            fig = create_timeline(df)
            st.pyplot(fig)
            
            # Monthly breakdown
            st.subheader("📅 Monthly Activity")
            
            df_dates = df.copy()
            df_dates['added_at'] = pd.to_datetime(df_dates['added_at'])
            df_dates['month'] = df_dates['added_at'].dt.to_period('M')
            
            monthly_counts = df_dates['month'].value_counts().sort_index()
            
            if len(monthly_counts) > 0:
                peak_month = monthly_counts.idxmax()
                peak_count = monthly_counts.max()
                avg_monthly = monthly_counts.mean()
                
                st.info(f"**Peak Activity**: {peak_month} with {peak_count} tracks (avg: {avg_monthly:.1f}/month)")
                
                # Show monthly chart
                fig, ax = plt.subplots(figsize=(12, 6))
                monthly_counts.plot(kind='bar', ax=ax)
                ax.set_title("Tracks Added Per Month")
                ax.set_xlabel("Month")
                ax.set_ylabel("Number of Tracks")
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
        else:
            st.warning("No date information available for trend analysis")
        
    except Exception as e:
        st.error(f"Error in trends analysis: {e}")


def show_deep_dive_tab(df):
    """Display detailed analysis"""
    
    st.header("🔍 Deep Dive Analysis")
    
    try:
        # Artist exploration
        st.subheader("🎤 Artist Deep Dive")
        
        if 'artist_name' in df.columns:
            artists = sorted(df['artist_name'].unique())
            selected_artist = st.selectbox("Select an artist to analyze:", artists)
            
            if selected_artist:
                artist_data = df[df['artist_name'] == selected_artist]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Tracks", len(artist_data))
                
                with col2:
                    albums = artist_data['album_name'].nunique() if 'album_name' in artist_data.columns else 0
                    st.metric("Unique Albums", albums)
                
                with col3:
                    pct_library = (len(artist_data) / len(df)) * 100
                    st.metric("% of Library", f"{pct_library:.1f}%")
                
                # Track list
                st.markdown(f"**Tracks by {selected_artist}:**")
                if 'track_name' in artist_data.columns:
                    tracks = artist_data['track_name'].value_counts()
                    for track, count in tracks.items():
                        st.write(f"• {track}" + (f" ({count}x)" if count > 1 else ""))
        
        # Data export
        st.subheader("💾 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Download Analysis Summary"):
                summary = create_summary_stats(df)
                st.download_button(
                    label="Download Summary CSV",
                    data=summary.to_csv(index=False),
                    file_name="orpheus_analysis_summary.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📁 Download Full Dataset"):
                st.download_button(
                    label="Download Data CSV",
                    data=df.to_csv(index=False),
                    file_name="orpheus_processed_data.csv",
                    mime="text/csv"
                )
        
    except Exception as e:
        st.error(f"Error in deep dive analysis: {e}")


if __name__ == "__main__":
    main()
