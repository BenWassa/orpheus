#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify Streamlit app imports work correctly.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

try:
    print("Testing imports...")
    from src.data_processing import load_exportify, clean
    print("✅ data_processing imports OK")
    
    from src.pattern_analysis import playlist_stats, repeat_obsessions, temporal_patterns
    print("✅ pattern_analysis imports OK")
    
    from src.emotion_analysis import add_spotify_audio_features, add_lyric_sentiment, compute_emotion_summary
    print("✅ emotion_analysis imports OK")
    
    from src.visualization import plot_emotion_timeline, plot_top_artists, plot_audio_features_radar
    print("✅ visualization imports OK")
    
    from src.config import DATA_DIR_RAW, DATA_DIR_PROCESSED
    print("✅ config imports OK")
    
    print(f"✅ All imports successful!")
    print(f"📁 Data directory: {DATA_DIR_RAW}")
    
    # Check for sample data
    sample_files = list(DATA_DIR_RAW.glob("*.csv"))
    print(f"📊 Sample files: {[f.name for f in sample_files]}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"📁 Project root: {project_root}")
    print(f"📂 Current working directory: {Path.cwd()}")
    print(f"🔍 Python path: {sys.path[:3]}")
