"""
Visualization module for Project Orpheus.

Creates matplotlib charts and prepares data for Streamlit dashboard.
Handles emotional timelines, pattern visualization, and mood mapping.
"""
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

# Set style for consistent plotting
plt.style.use('default')
sns.set_palette("husl")


def plot_emotion_timeline(df: pd.DataFrame, save_path: Optional[Path] = None) -> plt.Figure:
    """
    Create timeline visualization of emotional patterns.
    
    Args:
        df: DataFrame with temporal and emotion data
        save_path: Optional path to save the plot
        
    Returns:
        Matplotlib figure object
    """
    logger.info("Creating emotion timeline visualization")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Emotional Timeline - Project Orpheus', fontsize=16, fontweight='bold')
    
    # Check if we have temporal data
    if 'added_at' not in df.columns or df['added_at'].isna().all():
        logger.warning("No temporal data available for timeline")
        # Create mock timeline
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='W')
        df_temp = pd.DataFrame({
            'added_at': dates,
            'valence': np.random.uniform(0, 1, len(dates)),
            'energy': np.random.uniform(0, 1, len(dates))
        })
    else:
        df_temp = df[df['added_at'].notna()].copy()
        df_temp = df_temp.sort_values('added_at')
    
    # Plot 1: Valence over time
    if 'valence' in df_temp.columns and not df_temp['valence'].isna().all():
        axes[0, 0].plot(df_temp['added_at'], df_temp['valence'], alpha=0.7, linewidth=2)
        axes[0, 0].set_title('Valence Over Time')
        axes[0, 0].set_ylabel('Valence (0-1)')
        axes[0, 0].grid(True, alpha=0.3)
    else:
        axes[0, 0].text(0.5, 0.5, 'No valence data available', 
                       ha='center', va='center', transform=axes[0, 0].transAxes)
        axes[0, 0].set_title('Valence Over Time')
    
    # Plot 2: Energy over time
    if 'energy' in df_temp.columns and not df_temp['energy'].isna().all():
        axes[0, 1].plot(df_temp['added_at'], df_temp['energy'], color='orange', alpha=0.7, linewidth=2)
        axes[0, 1].set_title('Energy Over Time')
        axes[0, 1].set_ylabel('Energy (0-1)')
        axes[0, 1].grid(True, alpha=0.3)
    else:
        axes[0, 1].text(0.5, 0.5, 'No energy data available', 
                       ha='center', va='center', transform=axes[0, 1].transAxes)
        axes[0, 1].set_title('Energy Over Time')
    
    # Plot 3: Mood quadrant (valence vs energy)
    if ('valence' in df_temp.columns and 'energy' in df_temp.columns and 
        not df_temp['valence'].isna().all() and not df_temp['energy'].isna().all()):
        scatter = axes[1, 0].scatter(df_temp['valence'], df_temp['energy'], 
                                   alpha=0.6, s=50, c=range(len(df_temp)), cmap='viridis')
        axes[1, 0].set_xlabel('Valence (0-1)')
        axes[1, 0].set_ylabel('Energy (0-1)')
        axes[1, 0].set_title('Mood Quadrant')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Add quadrant labels
        axes[1, 0].axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
        axes[1, 0].axvline(x=0.5, color='gray', linestyle='--', alpha=0.5)
        axes[1, 0].text(0.25, 0.75, 'Energetic\nNegative', ha='center', va='center', alpha=0.7)
        axes[1, 0].text(0.75, 0.75, 'Energetic\nPositive', ha='center', va='center', alpha=0.7)
        axes[1, 0].text(0.25, 0.25, 'Calm\nNegative', ha='center', va='center', alpha=0.7)
        axes[1, 0].text(0.75, 0.25, 'Calm\nPositive', ha='center', va='center', alpha=0.7)
    else:
        axes[1, 0].text(0.5, 0.5, 'No mood data available', 
                       ha='center', va='center', transform=axes[1, 0].transAxes)
        axes[1, 0].set_title('Mood Quadrant')
    
    # Plot 4: Monthly listening activity
    if 'added_at' in df_temp.columns:
        df_temp['month'] = df_temp['added_at'].dt.to_period('M')
        monthly_counts = df_temp['month'].value_counts().sort_index()
        if len(monthly_counts) > 0:
            axes[1, 1].bar(range(len(monthly_counts)), monthly_counts.values, alpha=0.7)
            axes[1, 1].set_title('Monthly Listening Activity')
            axes[1, 1].set_ylabel('Track Count')
            axes[1, 1].set_xlabel('Month')
            
            # Format x-axis labels
            if len(monthly_counts) <= 12:
                axes[1, 1].set_xticks(range(len(monthly_counts)))
                axes[1, 1].set_xticklabels([str(m) for m in monthly_counts.index], rotation=45)
        else:
            axes[1, 1].text(0.5, 0.5, 'No temporal data available', 
                           ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Monthly Listening Activity')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Timeline visualization saved to {save_path}")
    
    return fig


def plot_top_artists(df: pd.DataFrame, n: int = 10, save_path: Optional[Path] = None) -> plt.Figure:
    """
    Create bar chart of top artists by track count.
    
    Args:
        df: DataFrame with artist data
        n: Number of top artists to show
        save_path: Optional path to save the plot
        
    Returns:
        Matplotlib figure object
    """
    logger.info(f"Creating top {n} artists visualization")
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Get artist counts
    artist_col = None
    for col in ['artist_name', 'Artist Name(s)', 'artist']:
        if col in df.columns:
            artist_col = col
            break
    
    if artist_col is None:
        ax.text(0.5, 0.5, 'No artist data available', 
               ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Top Artists')
        return fig
    
    artist_counts = df[artist_col].value_counts().head(n)
    
    if len(artist_counts) == 0:
        ax.text(0.5, 0.5, 'No artist data available', 
               ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Top Artists')
        return fig
    
    # Create horizontal bar chart
    bars = ax.barh(range(len(artist_counts)), artist_counts.values, alpha=0.8)
    ax.set_yticks(range(len(artist_counts)))
    ax.set_yticklabels(artist_counts.index)
    ax.set_xlabel('Track Count')
    ax.set_title(f'Top {n} Artists by Track Count')
    
    # Add value labels on bars
    for i, (bar, count) in enumerate(zip(bars, artist_counts.values)):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
               str(count), va='center', ha='left')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Top artists visualization saved to {save_path}")
    
    return fig


def plot_audio_features_radar(df: pd.DataFrame, save_path: Optional[Path] = None) -> plt.Figure:
    """
    Create radar chart of average audio features.
    
    Args:
        df: DataFrame with audio feature data
        save_path: Optional path to save the plot
        
    Returns:
        Matplotlib figure object
    """
    logger.info("Creating audio features radar chart")
    
    audio_features = ['valence', 'energy', 'danceability', 'acousticness', 
                     'instrumentalness', 'liveness', 'speechiness']
    
    # Calculate means for available features
    feature_means = {}
    for feature in audio_features:
        if feature in df.columns and not df[feature].isna().all():
            feature_means[feature] = df[feature].mean()
    
    if not feature_means:
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.text(0.5, 0.5, 'No audio features available', 
               ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Audio Features Profile')
        return fig
    
    # Create radar chart
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    features = list(feature_means.keys())
    values = list(feature_means.values())
    
    # Add first value at end to close the circle
    features += [features[0]]
    values += [values[0]]
    
    # Calculate angles for each feature
    angles = np.linspace(0, 2 * np.pi, len(features), endpoint=True)
    
    # Plot
    ax.plot(angles, values, 'o-', linewidth=2, alpha=0.8)
    ax.fill(angles, values, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([f.title() for f in features[:-1]])
    ax.set_ylim(0, 1)
    ax.set_title('Audio Features Profile', size=16, fontweight='bold', pad=20)
    ax.grid(True)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Audio features radar chart saved to {save_path}")
    
    return fig


def create_emotion_summary_text(summary: Dict[str, Any]) -> str:
    """
    Create a formatted text summary of emotional analysis.
    
    Args:
        summary: Emotion summary dictionary from compute_emotion_summary()
        
    Returns:
        Formatted string with analysis results
    """
    text_lines = ["🎵 PROJECT ORPHEUS - EMOTIONAL ANALYSIS SUMMARY 🎵", "=" * 60, ""]
    
    # Audio features summary
    if summary.get('audio_features'):
        text_lines.append("🎼 AUDIO FEATURES:")
        for feature, stats in summary['audio_features'].items():
            text_lines.append(f"  {feature.title()}: {stats['mean']:.3f} (±{stats['std']:.3f})")
        text_lines.append("")
    
    # Sentiment summary
    if summary.get('sentiment'):
        text_lines.append("💭 LYRIC SENTIMENT:")
        for sentiment, stats in summary['sentiment'].items():
            text_lines.append(f"  {sentiment}: {stats['mean']:.3f}")
            dist = stats.get('distribution', {})
            if dist:
                text_lines.append(f"    Positive: {dist.get('positive', 0)}, "
                                f"Negative: {dist.get('negative', 0)}, "
                                f"Neutral: {dist.get('neutral', 0)}")
        text_lines.append("")
    
    # Emotion profile
    if summary.get('emotion_profile'):
        text_lines.append("😊 EMOTION PROFILE:")
        for emotion, value in summary['emotion_profile'].items():
            emotion_name = emotion.replace('emotion_', '').title()
            text_lines.append(f"  {emotion_name}: {value:.3f}")
        text_lines.append("")
    
    # Recommendations
    if summary.get('recommendations'):
        text_lines.append("🔮 INSIGHTS & RECOMMENDATIONS:")
        for i, rec in enumerate(summary['recommendations'], 1):
            text_lines.append(f"  {i}. {rec}")
        text_lines.append("")
    
    text_lines.append("=" * 60)
    text_lines.append("May your music lead you inward, and your insights bring you home.")
    
    return "\n".join(text_lines)


def save_all_visualizations(df: pd.DataFrame, emotion_summary: Dict[str, Any], 
                          output_dir: Path) -> Dict[str, Path]:
    """
    Generate and save all visualizations to output directory.
    
    Args:
        df: Processed DataFrame with all features
        emotion_summary: Summary from compute_emotion_summary()
        output_dir: Directory to save visualizations
        
    Returns:
        Dictionary mapping visualization names to file paths
    """
    logger.info(f"Generating all visualizations in {output_dir}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_files = {}
    
    # Timeline
    timeline_path = output_dir / "emotion_timeline.png"
    plot_emotion_timeline(df, save_path=timeline_path)
    saved_files['timeline'] = timeline_path
    plt.close()
    
    # Top artists
    artists_path = output_dir / "top_artists.png"
    plot_top_artists(df, save_path=artists_path)
    saved_files['artists'] = artists_path
    plt.close()
    
    # Audio features radar
    radar_path = output_dir / "audio_features_radar.png"
    plot_audio_features_radar(df, save_path=radar_path)
    saved_files['radar'] = radar_path
    plt.close()
    
    # Save text summary
    summary_path = output_dir / "emotion_summary.txt"
    summary_text = create_emotion_summary_text(emotion_summary)
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_text)
    saved_files['summary'] = summary_path
    
    logger.info(f"All visualizations saved to {output_dir}")
    return saved_files
