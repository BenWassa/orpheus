"""
Main test script for Project Orpheus

Runs the complete analysis pipeline on sample data and prints results to console.
Use this to test that everything is working correctly.
"""
import sys
from pathlib import Path
import logging

project_root = Path(__file__).parent.parent
# Add project root and core modules directory so imports work when run from project root
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "02_core"))

from data_processor import load_exportify, clean, save_processed
from pattern_analyzer import playlist_stats, repeat_obsessions, temporal_patterns
from emotion_analyzer import add_spotify_audio_features, add_lyric_sentiment, compute_emotion_summary
from visualizer import save_all_visualizations, create_emotion_summary_text
from config import DATA_DIR_RAW, DATA_DIR_PROCESSED, PROJECT_ROOT

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Run complete analysis pipeline"""
    
    print("🎵" * 20)
    print("PROJECT ORPHEUS - EMOTIONAL MUSIC ANALYSIS")
    print("🎵" * 20)
    print()
    
    try:
        # Step 1: Find and load data
        print("📁 STEP 1: Loading data...")
        csv_files = list(DATA_DIR_RAW.glob("*.csv"))
        
        if not csv_files:
            print("❌ No CSV files found in data/raw/ directory")
            print("Please add an Exportify CSV file to data/raw/ and try again")
            return
        
        # Use first CSV file found
        csv_file = csv_files[0]
        print(f"Found CSV file: {csv_file.name}")
        
        # Load and clean data
        df_raw = load_exportify(csv_file)
        print(f"Loaded {len(df_raw)} raw rows")
        
        df_clean = clean(df_raw)
        print(f"Cleaned to {len(df_clean)} rows")
        
        # Save processed data
        processed_file = DATA_DIR_PROCESSED / f"{csv_file.stem}_processed.parquet"
        save_processed(df_clean, processed_file)
        print(f"Saved processed data to {processed_file}")
        print()
        
        # Step 2: Basic statistics
        print("📊 STEP 2: Computing statistics...")
        stats = playlist_stats(df_clean)
        
        print(f"Total tracks: {stats['total_tracks']}")
        print(f"Unique artists: {stats['unique_artists']}")
        print(f"Unique albums: {stats['unique_albums']}")
        print(f"Most common artist: {stats['most_common_artist']}")
        print(f"Average popularity: {stats['average_popularity']}")
        
        if stats['date_range']:
            date_range = stats['date_range']
            print(f"Date range: {date_range['earliest']} to {date_range['latest']} ({date_range['span_days']} days)")
        print()
        
        # Step 3: Pattern analysis
        print("🔍 STEP 3: Analyzing patterns...")
        obsessions_df = repeat_obsessions(df_clean, threshold=3)
        
        if len(obsessions_df) > 0:
            print(f"Found {len(obsessions_df)} obsessions:")
            for _, row in obsessions_df.head(5).iterrows():
                print(f"  - {row['type'].title()}: {row['name']} ({row['count']} times, {row['percentage']:.1f}%)")
        else:
            print("No repeat obsessions found")
        
        # Temporal patterns
        temporal_data = temporal_patterns(df_clean)
        if temporal_data['peak_periods']:
            peak = temporal_data['peak_periods']
            print(f"Peak listening period: {peak['peak_month']} with {peak['peak_count']} tracks")
        print()
        
        # Step 4: Emotion analysis
        print("💭 STEP 4: Analyzing emotions...")
        df_with_audio = add_spotify_audio_features(df_clean)
        print(f"Added audio features for {df_with_audio['valence'].notna().sum()} tracks")
        
        df_with_sentiment = add_lyric_sentiment(df_with_audio)
        print(f"Added sentiment analysis for {df_with_sentiment['lyric_polarity'].notna().sum()} tracks")
        
        emotion_summary = compute_emotion_summary(df_with_sentiment)
        print("Computed emotion summary")
        print()
        
        # Step 5: Generate visualizations
        print("📈 STEP 5: Creating visualizations...")
        output_dir = PROJECT_ROOT / "output" / "visualizations"
        saved_files = save_all_visualizations(df_with_sentiment, emotion_summary, output_dir)
        
        print("Generated visualizations:")
        for name, path in saved_files.items():
            print(f"  - {name}: {path}")
        print()
        
        # Step 6: Display summary
        print("🔮 STEP 6: Emotional analysis summary")
        print("-" * 60)
        summary_text = create_emotion_summary_text(emotion_summary)
        print(summary_text)
        
        print("\n✅ Analysis complete! Check the output/ directory for visualizations.")
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        print(f"\n❌ Error: {e}")
        print("Check the logs above for more details.")


if __name__ == "__main__":
    main()
