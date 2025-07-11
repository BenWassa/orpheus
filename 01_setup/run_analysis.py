#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎵 Project Orpheus - Complete Analysis Runner

Processes all CSV files in the data directory and generates comprehensive analysis.
Run from project root: python 01_setup/run_analysis.py
"""

import sys
from pathlib import Path
import pandas as pd

# Add core modules to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "02_core"))

try:
    from data_processor import load_csv_data, clean_data, get_data_summary
    from pattern_analyzer import analyze_patterns, find_obsessions, analyze_temporal_trends
    from visualizer import save_all_visualizations, create_summary_stats
except ImportError as e:
    print(f"❌ Could not import core modules: {e}")
    print("Ensure you're running from the project root directory")
    sys.exit(1)


def main():
    """Main analysis runner"""
    
    print("🎵 Project Orpheus - Complete Music Analysis")
    print("=" * 50)
    
    # Setup directories
    data_dir = project_root / "04_data" / "raw"
    output_dir = project_root / "05_output"
    viz_dir = output_dir / "visualizations"
    
    # Create output directories
    output_dir.mkdir(exist_ok=True)
    viz_dir.mkdir(exist_ok=True)
    
    # Find CSV files
    csv_files = list(data_dir.glob("*.csv"))
    
    if not csv_files:
        print(f"❌ No CSV files found in {data_dir}")
        print("💡 Add your Exportify CSV files to 04_data/raw/")
        return
    
    print(f"📁 Found {len(csv_files)} CSV file(s):")
    for file in csv_files:
        print(f"  • {file.name}")
    print()
    
    # Process all files
    all_data = []
    
    for csv_file in csv_files:
        print(f"🔄 Processing {csv_file.name}...")
        
        try:
            # Load and clean data
            df_raw = load_csv_data(csv_file)
            df_clean = clean_data(df_raw)
            all_data.append(df_clean)
            
            print(f"  ✅ Processed {len(df_clean)} tracks")
            
        except Exception as e:
            print(f"  ❌ Error processing {csv_file.name}: {e}")
            continue
    
    if not all_data:
        print("❌ No data could be processed")
        return
    
    # Combine all data
    print("\n🔗 Combining all datasets...")
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"📊 Total combined dataset: {len(combined_df)} tracks")
    
    # Run analysis
    print("\n📈 Running pattern analysis...")
    patterns = analyze_patterns(combined_df, threshold=3)
    
    print("\n🔍 Finding musical obsessions...")
    obsessions = find_obsessions(combined_df, threshold=3)
    
    print("\n⏰ Analyzing temporal trends...")
    temporal_trends = analyze_temporal_trends(combined_df)
    
    # Generate summary
    print("\n📋 Generating summary statistics...")
    data_summary = get_data_summary(combined_df)
    summary_stats = create_summary_stats(combined_df)
    
    # Create visualizations
    print("\n🎨 Creating visualizations...")
    try:
        save_all_visualizations(combined_df, viz_dir)
        print(f"  ✅ Visualizations saved to {viz_dir}")
    except Exception as e:
        print(f"  ⚠️  Warning: Could not create visualizations: {e}")
    
    # Save results
    print("\n💾 Saving analysis results...")
    
    # Save processed data
    processed_file = output_dir / "processed_music_data.csv"
    combined_df.to_csv(processed_file, index=False)
    print(f"  📁 Processed data: {processed_file}")
    
    # Save obsessions
    if len(obsessions) > 0:
        obsessions_file = output_dir / "musical_obsessions.csv"
        obsessions.to_csv(obsessions_file, index=False)
        print(f"  🔥 Obsessions: {obsessions_file}")
    
    # Save summary
    summary_file = output_dir / "analysis_summary.csv"
    summary_stats.to_csv(summary_file, index=False)
    print(f"  📊 Summary: {summary_file}")
    
    # Print results to console
    print("\n" + "=" * 50)
    print("🎉 ANALYSIS COMPLETE - KEY INSIGHTS")
    print("=" * 50)
    
    print(f"\n📊 DATASET OVERVIEW:")
    print(f"  • Total tracks: {data_summary['total_tracks']:,}")
    print(f"  • Unique artists: {data_summary['unique_artists']:,}")
    print(f"  • Unique albums: {data_summary['unique_albums']:,}")
    
    if data_summary['date_range']:
        dr = data_summary['date_range']
        print(f"  • Date range: {dr['earliest'].strftime('%Y-%m-%d')} to {dr['latest'].strftime('%Y-%m-%d')}")
        print(f"  • Span: {dr['span_days']} days")
    
    if data_summary['most_common_artist']:
        print(f"  • Top artist: {data_summary['most_common_artist']}")
    
    print(f"\n🔥 MUSICAL OBSESSIONS (3+ plays):")
    if len(obsessions) > 0:
        for _, obs in obsessions.head(5).iterrows():
            print(f"  • {obs['name']} ({obs['type']}): {obs['count']} plays ({obs['percentage']:.1f}%)")
    else:
        print("  • No obsessions found with 3+ plays")
    
    if 'temporal_trends' in locals() and 'monthly_trends' in temporal_trends:
        mt = temporal_trends['monthly_trends']
        print(f"\n📅 TEMPORAL PATTERNS:")
        print(f"  • Peak month: {mt['peak_month']} ({mt['peak_count']} tracks)")
        print(f"  • Average per month: {mt['average_monthly']:.1f} tracks")
    
    print(f"\n📁 OUTPUT LOCATION:")
    print(f"  • Main results: {output_dir}")
    print(f"  • Visualizations: {viz_dir}")
    
    print("\n🌐 NEXT STEPS:")
    print("  • Run the Streamlit dashboard for interactive exploration")
    print("  • Use: python 01_setup/launch_dashboard.bat")
    print("  • Or: streamlit run 03_interface/streamlit_app.py")
    
    print("\n🎵 Happy music exploration!")


if __name__ == "__main__":
    main()
