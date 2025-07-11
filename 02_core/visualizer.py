"""
🎵 Project Orpheus - Visualizer Module

Creates charts and visualizations for music listening patterns.
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime


def create_timeline(df):
    """
    Create a timeline visualization of music additions
    
    Args:
        df: DataFrame with 'added_at' column
        
    Returns:
        matplotlib.figure.Figure: Timeline chart
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    try:
        if 'added_at' not in df.columns:
            ax.text(0.5, 0.5, 'No date information available', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Timeline - No Data Available')
            return fig
        
        # Convert to datetime and create monthly counts
        df_temp = df.copy()
        df_temp['added_at'] = pd.to_datetime(df_temp['added_at'])
        df_temp['month'] = df_temp['added_at'].dt.to_period('M')
        
        monthly_counts = df_temp['month'].value_counts().sort_index()
        
        if len(monthly_counts) == 0:
            ax.text(0.5, 0.5, 'No valid dates found', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Timeline - No Valid Data')
            return fig
        
        # Plot timeline
        dates = [period.to_timestamp() for period in monthly_counts.index]
        counts = monthly_counts.values
        
        ax.plot(dates, counts, marker='o', linewidth=2, markersize=6, color='#2E86AB')
        ax.fill_between(dates, counts, alpha=0.3, color='#2E86AB')
        
        # Formatting
        ax.set_title('Music Addition Timeline', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Tracks Added', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Rotate dates for better readability
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Add stats text
        total_months = len(monthly_counts)
        avg_monthly = monthly_counts.mean()
        peak_month = monthly_counts.idxmax()
        peak_count = monthly_counts.max()
        
        stats_text = f"Total months: {total_months} | Avg: {avg_monthly:.1f}/month | Peak: {peak_count} ({peak_month})"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
    except Exception as e:
        ax.text(0.5, 0.5, f'Error creating timeline: {str(e)}', 
               ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Timeline - Error')
        print(f"Error in create_timeline: {e}")
    
    return fig


def create_top_artists(df, top_n=15):
    """
    Create a horizontal bar chart of top artists
    
    Args:
        df: DataFrame with 'artist_name' column
        top_n: Number of top artists to show
        
    Returns:
        matplotlib.figure.Figure: Top artists chart
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    try:
        if 'artist_name' not in df.columns:
            ax.text(0.5, 0.5, 'No artist information available', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Top Artists - No Data Available')
            return fig
        
        # Get top artists
        artist_counts = df['artist_name'].value_counts().head(top_n)
        
        if len(artist_counts) == 0:
            ax.text(0.5, 0.5, 'No artist data found', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Top Artists - No Valid Data')
            return fig
        
        # Create horizontal bar chart
        y_pos = np.arange(len(artist_counts))
        colors = plt.cm.viridis(np.linspace(0, 1, len(artist_counts)))
        
        bars = ax.barh(y_pos, artist_counts.values, color=colors)
        
        # Formatting
        ax.set_yticks(y_pos)
        ax.set_yticklabels(artist_counts.index, fontsize=10)
        ax.invert_yaxis()  # Top artist at the top
        ax.set_xlabel('Number of Tracks', fontsize=12)
        ax.set_title(f'Top {len(artist_counts)} Artists by Track Count', fontsize=16, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels on bars
        for i, (bar, value) in enumerate(zip(bars, artist_counts.values)):
            ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                   str(value), va='center', fontsize=10)
        
        plt.tight_layout()
        
        # Add summary stats
        total_tracks = len(df)
        top_artist_pct = (artist_counts.iloc[0] / total_tracks) * 100
        total_artists = df['artist_name'].nunique()
        
        stats_text = f"Total artists: {total_artists} | Top artist: {top_artist_pct:.1f}% of library"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
    except Exception as e:
        ax.text(0.5, 0.5, f'Error creating top artists chart: {str(e)}', 
               ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Top Artists - Error')
        print(f"Error in create_top_artists: {e}")
    
    return fig


def create_obsessions_chart(obsessions_df):
    """
    Create a chart showing musical obsessions
    
    Args:
        obsessions_df: DataFrame from find_obsessions function
        
    Returns:
        matplotlib.figure.Figure: Obsessions chart
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    try:
        if len(obsessions_df) == 0:
            for ax in [ax1, ax2]:
                ax.text(0.5, 0.5, 'No obsessions found', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax1.set_title('Artist Obsessions - No Data')
            ax2.set_title('Track Obsessions - No Data')
            return fig
        
        # Separate artist and track obsessions
        artist_obs = obsessions_df[obsessions_df['type'] == 'artist'].head(10)
        track_obs = obsessions_df[obsessions_df['type'] == 'track'].head(10)
        
        # Artist obsessions chart
        if len(artist_obs) > 0:
            y_pos = np.arange(len(artist_obs))
            colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(artist_obs)))
            
            bars1 = ax1.barh(y_pos, artist_obs['count'], color=colors)
            ax1.set_yticks(y_pos)
            ax1.set_yticklabels(artist_obs['name'], fontsize=10)
            ax1.invert_yaxis()
            ax1.set_xlabel('Track Count')
            ax1.set_title('Artist Obsessions', fontweight='bold')
            ax1.grid(axis='x', alpha=0.3)
            
            # Add value labels
            for bar, value in zip(bars1, artist_obs['count']):
                ax1.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                        str(value), va='center', fontsize=10)
        else:
            ax1.text(0.5, 0.5, 'No artist obsessions found', 
                    ha='center', va='center', transform=ax1.transAxes)
            ax1.set_title('Artist Obsessions - No Data')
        
        # Track obsessions chart
        if len(track_obs) > 0:
            y_pos = np.arange(len(track_obs))
            colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(track_obs)))
            
            bars2 = ax2.barh(y_pos, track_obs['count'], color=colors)
            ax2.set_yticks(y_pos)
            # Truncate long track names
            track_names = [name[:30] + '...' if len(name) > 30 else name for name in track_obs['name']]
            ax2.set_yticklabels(track_names, fontsize=10)
            ax2.invert_yaxis()
            ax2.set_xlabel('Play Count')
            ax2.set_title('Track Obsessions', fontweight='bold')
            ax2.grid(axis='x', alpha=0.3)
            
            # Add value labels
            for bar, value in zip(bars2, track_obs['count']):
                ax2.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                        str(value), va='center', fontsize=10)
        else:
            ax2.text(0.5, 0.5, 'No track obsessions found', 
                    ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Track Obsessions - No Data')
        
        plt.tight_layout()
        
    except Exception as e:
        for ax in [ax1, ax2]:
            ax.text(0.5, 0.5, f'Error: {str(e)}', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
        print(f"Error in create_obsessions_chart: {e}")
    
    return fig


def create_monthly_heatmap(df):
    """
    Create a heatmap showing listening activity by month and day
    
    Args:
        df: DataFrame with 'added_at' column
        
    Returns:
        matplotlib.figure.Figure: Monthly heatmap
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    try:
        if 'added_at' not in df.columns:
            ax.text(0.5, 0.5, 'No date information available', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Monthly Activity Heatmap - No Data Available')
            return fig
        
        df_temp = df.copy()
        df_temp['added_at'] = pd.to_datetime(df_temp['added_at'])
        df_temp['month'] = df_temp['added_at'].dt.month
        df_temp['weekday'] = df_temp['added_at'].dt.dayofweek
        
        # Create pivot table for heatmap
        heatmap_data = df_temp.groupby(['month', 'weekday']).size().unstack(fill_value=0)
        
        # Create heatmap
        im = ax.imshow(heatmap_data.values, cmap='YlOrRd', aspect='auto')
        
        # Set ticks and labels
        ax.set_xticks(range(7))
        ax.set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
        ax.set_yticks(range(len(heatmap_data.index)))
        ax.set_yticklabels([f'Month {i}' for i in heatmap_data.index])
        
        ax.set_title('Listening Activity Heatmap\n(Month vs Day of Week)', fontweight='bold', pad=20)
        ax.set_xlabel('Day of Week')
        ax.set_ylabel('Month')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Tracks Added', rotation=270, labelpad=20)
        
        # Add value annotations
        for i in range(len(heatmap_data.index)):
            for j in range(7):
                if j < len(heatmap_data.columns):
                    value = heatmap_data.iloc[i, j]
                    ax.text(j, i, str(value), ha='center', va='center', 
                           color='white' if value > heatmap_data.values.max()/2 else 'black')
        
        plt.tight_layout()
        
    except Exception as e:
        ax.text(0.5, 0.5, f'Error creating heatmap: {str(e)}', 
               ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Monthly Activity Heatmap - Error')
        print(f"Error in create_monthly_heatmap: {e}")
    
    return fig


def create_summary_stats(df):
    """
    Create a summary statistics DataFrame for export
    
    Args:
        df: Cleaned DataFrame
        
    Returns:
        pandas.DataFrame: Summary statistics
    """
    try:
        summary_data = []
        
        # Basic stats
        summary_data.append(['Total Tracks', len(df)])
        
        if 'artist_name' in df.columns:
            summary_data.append(['Unique Artists', df['artist_name'].nunique()])
            top_artist = df['artist_name'].value_counts().index[0]
            top_artist_count = df['artist_name'].value_counts().iloc[0]
            summary_data.append(['Top Artist', f"{top_artist} ({top_artist_count} tracks)"])
        
        if 'album_name' in df.columns:
            summary_data.append(['Unique Albums', df['album_name'].nunique()])
        
        if 'added_at' in df.columns:
            try:
                dates = pd.to_datetime(df['added_at'])
                date_range = (dates.max() - dates.min()).days
                summary_data.append(['Date Range (days)', date_range])
                summary_data.append(['Earliest Track', dates.min().strftime('%Y-%m-%d')])
                summary_data.append(['Latest Track', dates.max().strftime('%Y-%m-%d')])
            except:
                pass
        
        if 'popularity' in df.columns:
            avg_popularity = df['popularity'].mean()
            summary_data.append(['Average Popularity', f"{avg_popularity:.1f}"])
        
        # Create DataFrame
        summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
        
        return summary_df
        
    except Exception as e:
        print(f"Error creating summary stats: {e}")
        return pd.DataFrame({'Metric': ['Error'], 'Value': [str(e)]})


def save_all_visualizations(df, output_dir):
    """
    Save all visualizations to files
    
    Args:
        df: Cleaned DataFrame
        output_dir: Directory to save visualizations
    """
    from pathlib import Path
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Timeline
        fig_timeline = create_timeline(df)
        fig_timeline.savefig(output_dir / 'listening_timeline.png', dpi=300, bbox_inches='tight')
        plt.close(fig_timeline)
        
        # Top artists
        fig_artists = create_top_artists(df)
        fig_artists.savefig(output_dir / 'top_artists.png', dpi=300, bbox_inches='tight')
        plt.close(fig_artists)
        
        # Monthly heatmap
        fig_heatmap = create_monthly_heatmap(df)
        fig_heatmap.savefig(output_dir / 'monthly_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close(fig_heatmap)
        
        print(f"✅ Visualizations saved to {output_dir}")
        
    except Exception as e:
        print(f"❌ Error saving visualizations: {e}")
