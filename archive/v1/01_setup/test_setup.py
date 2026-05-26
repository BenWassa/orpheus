"""
Simple test script for Project Orpheus

A quick validation that all modules load correctly and basic functionality works.
"""
import sys
from pathlib import Path

# Add core modules to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "02_core"))

def test_imports():
    """Test that all main modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        from config import PROJECT_ROOT, DATA_DIR_RAW, DATA_DIR_PROCESSED
        print("✅ Config module loaded")
        
        from data_processor import load_exportify, clean
        print("✅ Data processing module loaded")
        
        from pattern_analyzer import playlist_stats, repeat_obsessions
        print("✅ Pattern analysis module loaded")
        
        from emotion_analyzer import add_spotify_audio_features, compute_emotion_summary
        print("✅ Emotion analysis module loaded")
        
        from visualizer import plot_emotion_timeline, create_emotion_summary_text
        print("✅ Visualization module loaded")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_data_loading():
    """Test loading the sample CSV file"""
    print("\n📊 Testing data loading...")
    
    try:
        from data_processor import load_exportify, clean
        from config import DATA_DIR_RAW
        
        # Find CSV files
        csv_files = list(DATA_DIR_RAW.glob("*.csv"))
        
        if not csv_files:
            print("⚠️  No CSV files found in data/raw/")
            return False
            
        print(f"📁 Found {len(csv_files)} CSV file(s)")
        
        # Load first file
        csv_file = csv_files[0]
        print(f"🔄 Loading: {csv_file.name}")
        
        df_raw = load_exportify(csv_file)
        print(f"📈 Loaded {len(df_raw)} rows, {len(df_raw.columns)} columns")
        
        # Clean data
        df_clean = clean(df_raw)
        print(f"🧹 Cleaned data: {len(df_clean)} rows remaining")
        
        # Show basic stats
        if 'track_name' in df_clean.columns:
            unique_tracks = df_clean['track_name'].nunique()
            print(f"🎵 Unique tracks: {unique_tracks}")
            
        if 'artist_name' in df_clean.columns:
            unique_artists = df_clean['artist_name'].nunique()
            print(f"🎤 Unique artists: {unique_artists}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return False

def test_analysis():
    """Test basic analysis functions"""
    print("\n🔍 Testing analysis functions...")
    
    try:
        from data_processor import load_exportify, clean
        from pattern_analyzer import playlist_stats
        from config import DATA_DIR_RAW
        
        # Load and clean data
        csv_files = list(DATA_DIR_RAW.glob("*.csv"))
        if not csv_files:
            print("⚠️  No data for analysis test")
            return False
            
        df_raw = load_exportify(csv_files[0])
        df_clean = clean(df_raw)
        
        # Run pattern analysis
        stats = playlist_stats(df_clean)
        print(f"📊 Analysis complete - {stats['total_tracks']} tracks processed")
        
        if stats.get('unique_artists', 0) > 0 and stats.get('most_common_artist'):
            artist_name = stats['most_common_artist']
            print(f"🎤 Most common artist: {artist_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🎵" * 30)
    print("PROJECT ORPHEUS - SETUP VALIDATION")
    print("🎵" * 30)
    
    tests_passed = 0
    total_tests = 3
    
    if test_imports():
        tests_passed += 1
        
    if test_data_loading():
        tests_passed += 1
        
    if test_analysis():
        tests_passed += 1
    
    print("\n" + "="*50)
    print(f"✅ Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Orpheus is ready to analyze your music!")
        print("\nNext steps:")
        print("1. Run: .\\launch_orpheus.bat (quick start)")
        print("2. Run: .\\orpheus_venv\\Scripts\\streamlit.exe run 03_interface\\streamlit_app.py (dashboard)")
        print("3. Add your own CSV files to 04_data/raw/ directory")
        print("4. Read: 06_docs/QUICK_START.md for complete guide")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        print("💡 Try: .\\orpheus_venv\\Scripts\\pip.exe install -r 01_setup/requirements.txt")
    
    print("="*50)

if __name__ == "__main__":
    main()
