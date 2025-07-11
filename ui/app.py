"""
Streamlit Dashboard for Project Orpheus

A minimal web interface for visualizing music listening patterns and emotional analysis.
Run with: streamlit run ui/app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import logging

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from src.data_processing import load_exportify, clean
    from src.pattern_analysis import playlist_stats, repeat_obsessions, temporal_patterns
    from src.emotion_analysis import add_spotify_audio_features, add_lyric_sentiment, compute_emotion_summary
    from src.visualization import plot_emotion_timeline, plot_top_artists, plot_audio_features_radar
    from src.config import DATA_DIR_RAW, DATA_DIR_PROCESSED
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Make sure you're running this from the project root directory")
    st.stop()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Project Orpheus",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    color: #1f1f2e;
    text-align: center;
    margin-bottom: 2rem;
}
.sub-header {
    font-size: 1.5rem;
    color: #4a4a6a;
    text-align: center;
    margin-bottom: 1rem;
}
.insight-box {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 5px solid #ff6b6b;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🎵 Project Orpheus</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Decode your emotional underworld through the music that moves you</p>', 
               unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("📁 Data Upload")
    st.sidebar.markdown("Upload your Exportify CSV file to begin analysis")
    
    uploaded_file = st.sidebar.file_uploader(
        "Choose CSV file",
        type=['csv'],
        help="Export your Spotify playlists using Exportify and upload the CSV here"
    )
    
    # Main content
    if uploaded_file is not None:
        analyze_uploaded_data(uploaded_file)
    else:
        show_welcome_page()


def show_welcome_page():
    """Display welcome page with instructions"""
    
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
        
        st.markdown("### 📊 What You'll Learn")
        st.markdown("""
        - **Emotional Patterns**: Valence, energy, and mood analysis
        - **Listening Obsessions**: Artists and tracks you can't stop playing
        - **Temporal Trends**: How your music taste evolves over time
        - **Personal Insights**: AI-generated recommendations based on your patterns
        """)
        
        # Sample data option
        st.markdown("### 🎮 Try with Sample Data")
        if st.button("Load Sample Dataset", type="secondary"):
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
            st.error("No sample CSV files found in data/raw/ directory")
            
    except Exception as e:
        st.error(f"Error loading sample data: {e}")


def analyze_uploaded_data(uploaded_file):
    """Analyze uploaded CSV data"""
    
    try:
        # Save uploaded file
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
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🎵 Patterns", "💭 Emotions", "📈 Visualizations"])
    
    with tab1:
        show_overview_analysis(df)
    
    with tab2:
        show_pattern_analysis(df)
    
    with tab3:
        show_emotion_analysis(df)
    
    with tab4:
        show_visualizations(df)


def show_overview_analysis(df: pd.DataFrame):
    """Display basic statistics and overview"""
    
    st.header("📊 Dataset Overview")
    
    # Basic stats
    stats = playlist_stats(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tracks", stats['total_tracks'])
    
    with col2:
        st.metric("Unique Artists", stats['unique_artists'])
    
    with col3:
        st.metric("Unique Albums", stats['unique_albums'])
    
    with col4:
        if stats['average_popularity']:
            st.metric("Avg Popularity", f"{stats['average_popularity']:.1f}")
        else:
            st.metric("Avg Popularity", "N/A")
    
    # Most common artist/album
    col1, col2 = st.columns(2)
    
    with col1:
        if stats['most_common_artist']:
            st.info(f"**Most Common Artist:** {stats['most_common_artist']}")
    
    with col2:
        if stats['most_common_album']:
            st.info(f"**Most Common Album:** {stats['most_common_album']}")
    
    # Date range
    if stats['date_range']:
        date_range = stats['date_range']
        st.info(f"**Date Range:** {date_range['earliest'].strftime('%Y-%m-%d')} to {date_range['latest'].strftime('%Y-%m-%d')} ({date_range['span_days']} days)")
    
    # Data preview
    st.subheader("📋 Data Preview")
    st.dataframe(df.head(10), use_container_width=True)


def show_pattern_analysis(df: pd.DataFrame):
    """Display pattern analysis results"""
    
    st.header("🎵 Listening Patterns")
    
    # Obsessions
    st.subheader("🔥 Repeat Obsessions")
    threshold = st.slider("Obsession Threshold", min_value=2, max_value=20, value=5)
    
    obsessions_df = repeat_obsessions(df, threshold=threshold)
    
    if len(obsessions_df) > 0:
        st.dataframe(obsessions_df, use_container_width=True)
        
        # Insights
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("**🔮 Pattern Insights:**")
        for _, row in obsessions_df.head(3).iterrows():
            st.markdown(f"- You have a {row['type']} obsession with **{row['name']}** ({row['count']} occurrences, {row['percentage']:.1f}% of library)")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info(f"No obsessions found above threshold of {threshold} occurrences")
    
    # Temporal patterns
    st.subheader("📅 Temporal Patterns")
    temporal_data = temporal_patterns(df)
    
    if temporal_data['peak_periods']:
        peak = temporal_data['peak_periods']
        st.info(f"**Peak Activity:** {peak['peak_month']} with {peak['peak_count']} tracks (avg: {peak['average_monthly']:.1f} per month)")


def show_emotion_analysis(df: pd.DataFrame):
    """Display emotion analysis results"""
    
    st.header("💭 Emotional Analysis")
    
    # Add features
    with st.spinner("Computing emotional features..."):
        df_with_audio = add_spotify_audio_features(df)
        df_with_sentiment = add_lyric_sentiment(df_with_audio)
        emotion_summary = compute_emotion_summary(df_with_sentiment)
    
    # Display summary
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎼 Audio Features")
        if emotion_summary.get('audio_features'):
            for feature, stats in emotion_summary['audio_features'].items():
                st.metric(
                    feature.title(), 
                    f"{stats['mean']:.3f}",
                    delta=f"±{stats['std']:.3f}"
                )
    
    with col2:
        st.subheader("😊 Emotion Profile")
        if emotion_summary.get('emotion_profile'):
            for emotion, value in emotion_summary['emotion_profile'].items():
                emotion_name = emotion.replace('emotion_', '').title()
                st.metric(emotion_name, f"{value:.3f}")
    
    # Recommendations
    if emotion_summary.get('recommendations'):
        st.subheader("🔮 Personal Insights")
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        for i, rec in enumerate(emotion_summary['recommendations'], 1):
            st.markdown(f"**{i}.** {rec}")
        st.markdown('</div>', unsafe_allow_html=True)


def show_visualizations(df: pd.DataFrame):
    """Display visualizations"""
    
    st.header("📈 Visualizations")
    
    # Prepare data with features
    with st.spinner("Preparing visualizations..."):
        df_with_features = add_spotify_audio_features(df)
        df_with_sentiment = add_lyric_sentiment(df_with_features)
    
    # Timeline
    st.subheader("📅 Emotional Timeline")
    fig_timeline = plot_emotion_timeline(df_with_sentiment)
    st.pyplot(fig_timeline)
    
    # Top artists
    st.subheader("🎤 Top Artists")
    n_artists = st.slider("Number of artists to show", min_value=5, max_value=25, value=10)
    fig_artists = plot_top_artists(df_with_sentiment, n=n_artists)
    st.pyplot(fig_artists)
    
    # Audio features radar
    st.subheader("🎵 Audio Features Profile")
    fig_radar = plot_audio_features_radar(df_with_sentiment)
    st.pyplot(fig_radar)


if __name__ == "__main__":
    main()
