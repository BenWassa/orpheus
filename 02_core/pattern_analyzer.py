"""
Pattern analysis module for Project Orpheus.

Implements descriptive metrics and repeat-obsession detection logic.
See 🔍 How It Works, step 2 in README for pattern detection methodology.
"""
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from collections import Counter

logger = logging.getLogger(__name__)


def top_playlists(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Get top N playlists by track count.
    
    Args:
        df: Processed DataFrame with playlist data
        n: Number of top playlists to return
        
    Returns:
        DataFrame with playlist names and track counts, sorted by count
    """
    logger.info(f"Analyzing top {n} playlists by track count")
    
    # Try different possible playlist column names
    playlist_cols = ['Playlist Name', 'playlist_name', 'playlist']
    playlist_col = None
    
    for col in playlist_cols:
        if col in df.columns:
            playlist_col = col
            break
    
    if playlist_col is None:
        logger.warning("No playlist column found - creating mock data")
        return pd.DataFrame({'playlist_name': ['Unknown'], 'track_count': [len(df)]})
    else:
        playlist_counts = df[playlist_col].value_counts().head(n).reset_index()
        playlist_counts.columns = ['playlist_name', 'track_count']
    
    logger.info(f"Found {len(playlist_counts)} playlists")
    return playlist_counts


def playlist_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute comprehensive playlist statistics.
    
    Args:
        df: Processed DataFrame with music data
        
    Returns:
        Dictionary with various playlist statistics
    """
    logger.info("Computing playlist statistics")
    
    stats = {
        'total_tracks': len(df),
        'unique_artists': 0,
        'unique_albums': 0,
        'date_range': None,
        'most_common_artist': None,
        'most_common_album': None,
        'average_popularity': None
    }
    
    # Artist statistics
    if 'artist_name' in df.columns:
        unique_artists = df['artist_name'].nunique()
        stats['unique_artists'] = unique_artists
        most_common_artist = df['artist_name'].value_counts().index[0] if len(df) > 0 else None
        stats['most_common_artist'] = most_common_artist
    
    # Album statistics
    if 'album_name' in df.columns:
        unique_albums = df['album_name'].nunique()
        stats['unique_albums'] = unique_albums
        most_common_album = df['album_name'].value_counts().index[0] if len(df) > 0 else None
        stats['most_common_album'] = most_common_album
    
    # Date range analysis
    if 'added_at' in df.columns:
        date_series = df['added_at'].dropna()
        if len(date_series) > 0:
            stats['date_range'] = {
                'earliest': date_series.min(),
                'latest': date_series.max(),
                'span_days': (date_series.max() - date_series.min()).days
            }
    
    # Popularity analysis
    popularity_cols = ['Popularity', 'popularity', 'play_count']
    for col in popularity_cols:
        if col in df.columns:
            pop_values = df[col].dropna()
            if len(pop_values) > 0:
                stats['average_popularity'] = pop_values.mean()
                break
    
    logger.info(f"Statistics computed for {stats['total_tracks']} tracks")
    return stats


def repeat_obsessions(df: pd.DataFrame, threshold: int = 10) -> pd.DataFrame:
    """
    Detect repeat obsessions - artists/tracks that exceed play threshold.
    
    Args:
        df: Processed DataFrame with music data
        threshold: Minimum occurrence count to be considered an obsession
        
    Returns:
        DataFrame with obsession details (artist/track, count, type)
    """
    logger.info(f"Detecting repeat obsessions with threshold: {threshold}")
    
    obsessions = []
    
    # Artist obsessions
    if 'artist_name' in df.columns:
        artist_counts = df['artist_name'].value_counts()
        artist_obsessions = artist_counts[artist_counts >= threshold]
        for artist, count in artist_obsessions.items():
            obsessions.append({
                'name': artist,
                'count': count,
                'type': 'artist',
                'percentage': (count / len(df)) * 100
            })
    
    # Track obsessions
    if 'track_name' in df.columns:
        track_counts = df['track_name'].value_counts()
        track_obsessions = track_counts[track_counts >= threshold]
        for track, count in track_obsessions.items():
            obsessions.append({
                'name': track,
                'count': count,
                'type': 'track',
                'percentage': (count / len(df)) * 100
            })
    
    # Album obsessions
    if 'album_name' in df.columns:
        album_counts = df['album_name'].value_counts()
        album_obsessions = album_counts[album_counts >= threshold]
        for album, count in album_obsessions.items():
            obsessions.append({
                'name': album,
                'count': count,
                'type': 'album',
                'percentage': (count / len(df)) * 100
            })
    
    obsessions_df = pd.DataFrame(obsessions)
    
    if len(obsessions_df) > 0:
        obsessions_df = obsessions_df.sort_values('count', ascending=False)
        logger.info(f"Found {len(obsessions_df)} obsessions above threshold {threshold}")
    else:
        logger.info("No obsessions found above threshold")
    
    return obsessions_df


def temporal_patterns(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze temporal listening patterns.
    
    Args:
        df: Processed DataFrame with timestamp data
        
    Returns:
        Dictionary with temporal pattern analysis
    """
    logger.info("Analyzing temporal listening patterns")
    
    patterns = {
        'monthly_distribution': None,
        'weekly_distribution': None,
        'listening_streaks': None,
        'peak_periods': None
    }
    
    if 'added_at' not in df.columns:
        logger.warning("No timestamp column found for temporal analysis")
        return patterns
    
    # Filter valid dates
    df_with_dates = df[df['added_at'].notna()].copy()
    
    if len(df_with_dates) == 0:
        logger.warning("No valid dates found for temporal analysis")
        return patterns
    
    # Monthly distribution
    df_with_dates['month'] = df_with_dates['added_at'].dt.to_period('M')
    monthly_counts = df_with_dates['month'].value_counts().sort_index()
    patterns['monthly_distribution'] = monthly_counts.to_dict()
    
    # Weekly distribution
    df_with_dates['week'] = df_with_dates['added_at'].dt.to_period('W')
    weekly_counts = df_with_dates['week'].value_counts().sort_index()
    patterns['weekly_distribution'] = weekly_counts.to_dict()
    
    # Peak periods (months with highest activity)
    if len(monthly_counts) > 0:
        peak_month = monthly_counts.idxmax()
        patterns['peak_periods'] = {
            'peak_month': str(peak_month),
            'peak_count': monthly_counts.max(),
            'average_monthly': monthly_counts.mean()
        }
    
    logger.info("Temporal pattern analysis complete")
    return patterns
