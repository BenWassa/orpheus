"""
Streamlit Dashboard for Project Orpheus - Fixed Version

A minimal web interface for visualizing music listening patterns and emotional analysis.
Run with: streamlit run ui/app_fixed.py
"""
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import logging
import warnings
warnings.filterwarnings('ignore')

# Configure matplotlib for Streamlit
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
plt.ioff()  # Turn off interactive mode

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Try imports with error handling
try:
    from data_processing import load_exportify, clean
    from pattern_analysis import playlist_stats, repeat_obsessions, temporal_patterns
    from emotion_analysis import add_spotify_audio_features, add_lyric_sentiment, compute_emotion_summary
    from visualization import plot_emotion_timeline, plot_top_artists, plot_audio_features_radar
    from config import DATA_DIR_RAW, DATA_DIR_PROCESSED
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error(f"Make sure you're running this from the project root directory: {project_root}")
    st.error("Try: cd to the project directory and run: streamlit run ui/app_fixed.py")
    IMPORTS_SUCCESSFUL = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config - must be first Streamlit command
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
.metric-card {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit application"""
    
    if not IMPORTS_SUCCESSFUL:
        st.stop()
    
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
    
    # Sample data button in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎮 Try Sample Data")
    if st.sidebar.button("Load Sample Dataset", type="secondary"):
        load_sample_data()
    
    # Check for existing processed data in session state
    if 'df_processed' in st.session_state:
        show_analysis_results(st.session_state.df_processed)
    elif uploaded_file is not None:
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
        
        # Check for sample data
        sample_files = list(DATA_DIR_RAW.glob("*.csv")) if DATA_DIR_RAW.exists() else []
        if sample_files:
            st.info(f"💡 Found sample data: {sample_files[0].name} - Use the sidebar to load it!")


def load_sample_data():
    """Load and analyze sample data"""
    try:
        # Look for existing sample data
        sample_files = list(DATA_DIR_RAW.glob("*.csv"))
        
        if sample_files:
            sample_file = sample_files[0]
            st.success(f"Loading sample data: {sample_file.name}")
            
            # Load and process
            with st.spinner("Loading and processing sample data..."):
                df_raw = load_exportify(sample_file)
                df_clean = clean(df_raw)
            
            # Store in session state
            st.session_state.df_processed = df_clean
            st.session_state.sample_data = True
            st.session_state.data_source = sample_file.name
            
            # Rerun to show analysis
            st.rerun()
        else:
            st.error("No sample CSV files found in data/raw/ directory")
            st.info("Please add a CSV file to the data/raw/ directory or upload one using the sidebar")
            
    except Exception as e:
        st.error(f"Error loading sample data: {e}")
        logger.error(f"Sample data loading error: {e}")


def analyze_uploaded_data(uploaded_file):
    """Analyze uploaded CSV data"""
    
    try:
        # Create temp file
        temp_path = DATA_DIR_RAW / f"temp_{uploaded_file.name}"
        
        # Save uploaded file
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Load and process
        with st.spinner("Loading and cleaning data..."):
            df_raw = load_exportify(temp_path)
            df_clean = clean(df_raw)
        
        st.success(f"Successfully processed {len(df_clean)} tracks from {uploaded_file.name}")
        
        # Store in session state
        st.session_state.df_processed = df_clean
        st.session_state.sample_data = False
        st.session_state.data_source = uploaded_file.name
        
        # Clean up temp file
        try:
            temp_path.unlink()
        except:
            pass
        
        # Display analysis
        show_analysis_results(df_clean)
        
    except Exception as e:
        st.error(f"Error processing file: {e}")
        logger.error(f"File processing error: {e}")


def show_analysis_results(df: pd.DataFrame):
    """Display comprehensive analysis results"""
    
    # Show data source
    data_source = st.session_state.get('data_source', 'Unknown')
    st.info(f"📊 Analyzing: **{data_source}** ({len(df)} tracks)")
    
    # Clear data button
    if st.button("🔄 Clear Data & Start Over"):
        for key in ['df_processed', 'sample_data', 'data_source']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
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
    
    try:
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
            if stats.get('average_popularity'):
                st.metric("Avg Popularity", f"{stats['average_popularity']:.1f}")
            else:
                st.metric("Avg Popularity", "N/A")
        
        # Most common artist/album
        col1, col2 = st.columns(2)
        
        with col1:
            if stats.get('most_common_artist'):
                st.info(f"**Most Common Artist:** {stats['most_common_artist']}")
        
        with col2:
            if stats.get('most_common_album'):
                st.info(f"**Most Common Album:** {stats['most_common_album']}")
        
        # Date range
        if stats.get('date_range'):
            date_range = stats['date_range']
            st.info(f"**Date Range:** {date_range['earliest'].strftime('%Y-%m-%d')} to {date_range['latest'].strftime('%Y-%m-%d')} ({date_range['span_days']} days)")
        
        # Data preview
        st.subheader("📋 Data Preview")
        
        # Show available columns
        st.write(f"**Available columns:** {', '.join(df.columns)}")
        
        # Show data
        display_df = df.head(10)
        st.dataframe(display_df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error in overview analysis: {e}")
        logger.error(f"Overview analysis error: {e}")


def show_pattern_analysis(df: pd.DataFrame):
    """Display pattern analysis results"""
    
    st.header("🎵 Listening Patterns")
    
    try:
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
                percentage = row.get('percentage', 0)
                st.markdown(f"- You have a {row['type']} obsession with **{row['name']}** ({row['count']} occurrences, {percentage:.1f}% of library)")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info(f"No obsessions found above threshold of {threshold} occurrences")
        
        # Temporal patterns
        st.subheader("📅 Temporal Patterns")
        temporal_data = temporal_patterns(df)
        
        if temporal_data.get('peak_periods'):
            peak = temporal_data['peak_periods']
            st.info(f"**Peak Activity:** {peak['peak_month']} with {peak['peak_count']} tracks (avg: {peak['average_monthly']:.1f} per month)")
        
    except Exception as e:
        st.error(f"Error in pattern analysis: {e}")
        logger.error(f"Pattern analysis error: {e}")


def show_emotion_analysis(df: pd.DataFrame):
    """Display emotion analysis results"""
    
    st.header("💭 Emotional Analysis")
    
    try:
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
                    mean_val = stats.get('mean', 0)
                    std_val = stats.get('std', 0)
                    st.metric(
                        feature.title(), 
                        f"{mean_val:.3f}",
                        delta=f"±{std_val:.3f}"
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
        
    except Exception as e:
        st.error(f"Error in emotion analysis: {e}")
        logger.error(f"Emotion analysis error: {e}")


def show_visualizations(df: pd.DataFrame):
    """Display visualizations"""
    
    st.header("📈 Visualizations")
    
    try:
        # Prepare data with features
        with st.spinner("Preparing visualizations..."):
            df_with_features = add_spotify_audio_features(df)
            df_with_sentiment = add_lyric_sentiment(df_with_features)
        
        # Timeline
        st.subheader("📅 Emotional Timeline")
        try:
            fig_timeline = plot_emotion_timeline(df_with_sentiment)
            st.pyplot(fig_timeline)
            plt.close(fig_timeline)
        except Exception as e:
            st.error(f"Error creating timeline: {e}")
        
        # Top artists
        st.subheader("🎤 Top Artists")
        n_artists = st.slider("Number of artists to show", min_value=5, max_value=25, value=10)
        try:
            fig_artists = plot_top_artists(df_with_sentiment, n=n_artists)
            st.pyplot(fig_artists)
            plt.close(fig_artists)
        except Exception as e:
            st.error(f"Error creating top artists chart: {e}")
        
        # Audio features radar
        st.subheader("🎵 Audio Features Profile")
        try:
            fig_radar = plot_audio_features_radar(df_with_sentiment)
            st.pyplot(fig_radar)
            plt.close(fig_radar)
        except Exception as e:
            st.error(f"Error creating radar chart: {e}")
        
    except Exception as e:
        st.error(f"Error in visualizations: {e}")
        logger.error(f"Visualization error: {e}")


if __name__ == "__main__":
    main()
