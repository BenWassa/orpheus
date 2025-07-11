"""
🎵 Project Orpheus - Pattern Analyzer Module

Analyzes listening patterns, obsessions, and temporal trends.
"""

import pandas as pd
import numpy as np
from collections import Counter


def analyze_patterns(df, threshold=5):
    """
    Analyze listening patterns in the data
    
    Args:
        df: Cleaned DataFrame
        threshold: Minimum count to consider significant
        
    Returns:
        dict: Pattern analysis results
    """
    patterns = {
        'artist_patterns': {},
        'track_patterns': {},
        'temporal_patterns': {},
        'obsessions': []
    }
    
    # Artist patterns
    if 'artist_name' in df.columns:
        artist_counts = df['artist_name'].value_counts()
        patterns['artist_patterns'] = {
            'total_unique': len(artist_counts),
            'top_10': artist_counts.head(10).to_dict(),
            'above_threshold': len(artist_counts[artist_counts >= threshold])
        }
    
    # Track patterns  
    if 'track_name' in df.columns:
        track_counts = df['track_name'].value_counts()
        patterns['track_patterns'] = {
            'total_unique': len(track_counts),
            'top_10': track_counts.head(10).to_dict(),
            'above_threshold': len(track_counts[track_counts >= threshold])
        }
    
    # Temporal patterns
    if 'added_at' in df.columns:
        try:
            df_temp = df.copy()
            df_temp['added_at'] = pd.to_datetime(df_temp['added_at'])
            df_temp['month'] = df_temp['added_at'].dt.to_period('M')
            df_temp['weekday'] = df_temp['added_at'].dt.day_name()
            
            monthly_counts = df_temp['month'].value_counts().sort_index()
            weekday_counts = df_temp['weekday'].value_counts()
            
            patterns['temporal_patterns'] = {
                'monthly_distribution': monthly_counts.to_dict(),
                'weekday_distribution': weekday_counts.to_dict(),
                'peak_month': monthly_counts.idxmax() if len(monthly_counts) > 0 else None,
                'peak_weekday': weekday_counts.idxmax() if len(weekday_counts) > 0 else None
            }
        except Exception as e:
            print(f"Warning: Could not analyze temporal patterns: {e}")
    
    # Find obsessions
    patterns['obsessions'] = find_obsessions(df, threshold)
    
    return patterns


def find_obsessions(df, threshold=5):
    """
    Find artists or tracks that appear frequently (obsessions)
    
    Args:
        df: Cleaned DataFrame
        threshold: Minimum count to consider an obsession
        
    Returns:
        pandas.DataFrame: Obsessions with metadata
    """
    obsessions = []
    
    # Artist obsessions
    if 'artist_name' in df.columns:
        artist_counts = df['artist_name'].value_counts()
        for artist, count in artist_counts.items():
            if count >= threshold:
                obsessions.append({
                    'name': artist,
                    'count': count,
                    'type': 'artist',
                    'intensity': calculate_intensity(count, len(df)),
                    'percentage': (count / len(df)) * 100
                })
    
    # Track obsessions
    if 'track_name' in df.columns:
        track_counts = df['track_name'].value_counts()
        for track, count in track_counts.items():
            if count >= threshold:
                obsessions.append({
                    'name': track,
                    'count': count,
                    'type': 'track',
                    'intensity': calculate_intensity(count, len(df)),
                    'percentage': (count / len(df)) * 100
                })
    
    # Convert to DataFrame and sort by count
    if obsessions:
        obsessions_df = pd.DataFrame(obsessions)
        obsessions_df = obsessions_df.sort_values('count', ascending=False)
        return obsessions_df
    else:
        return pd.DataFrame(columns=['name', 'count', 'type', 'intensity', 'percentage'])


def calculate_intensity(count, total):
    """
    Calculate obsession intensity score
    
    Args:
        count: Number of occurrences
        total: Total items in dataset
        
    Returns:
        str: Intensity level
    """
    percentage = (count / total) * 100
    
    if percentage >= 10:
        return 'Extreme'
    elif percentage >= 5:
        return 'High'
    elif percentage >= 2:
        return 'Moderate'
    else:
        return 'Low'


def analyze_temporal_trends(df):
    """
    Analyze temporal listening trends
    
    Args:
        df: Cleaned DataFrame with date information
        
    Returns:
        dict: Temporal analysis results
    """
    if 'added_at' not in df.columns:
        return {'error': 'No date information available'}
    
    try:
        df_temp = df.copy()
        df_temp['added_at'] = pd.to_datetime(df_temp['added_at'])
        
        # Monthly trends
        df_temp['month'] = df_temp['added_at'].dt.to_period('M')
        monthly_counts = df_temp['month'].value_counts().sort_index()
        
        # Yearly trends
        df_temp['year'] = df_temp['added_at'].dt.year
        yearly_counts = df_temp['year'].value_counts().sort_index()
        
        # Day of week trends
        df_temp['weekday'] = df_temp['added_at'].dt.day_name()
        weekday_counts = df_temp['weekday'].value_counts()
        
        # Hour of day trends (if time info available)
        df_temp['hour'] = df_temp['added_at'].dt.hour
        hourly_counts = df_temp['hour'].value_counts().sort_index()
        
        trends = {
            'monthly_trends': {
                'data': monthly_counts.to_dict(),
                'peak_month': monthly_counts.idxmax(),
                'peak_count': monthly_counts.max(),
                'average_monthly': monthly_counts.mean()
            },
            'yearly_trends': {
                'data': yearly_counts.to_dict(),
                'active_years': len(yearly_counts),
                'peak_year': yearly_counts.idxmax(),
                'peak_count': yearly_counts.max()
            },
            'weekday_trends': {
                'data': weekday_counts.to_dict(),
                'peak_day': weekday_counts.idxmax(),
                'peak_count': weekday_counts.max()
            },
            'hourly_trends': {
                'data': hourly_counts.to_dict(),
                'peak_hour': hourly_counts.idxmax(),
                'peak_count': hourly_counts.max()
            },
            'date_range': {
                'start': df_temp['added_at'].min(),
                'end': df_temp['added_at'].max(),
                'span_days': (df_temp['added_at'].max() - df_temp['added_at'].min()).days
            }
        }
        
        return trends
        
    except Exception as e:
        return {'error': f'Error analyzing temporal trends: {e}'}


def find_artist_evolution(df):
    """
    Analyze how artist preferences evolve over time
    
    Args:
        df: Cleaned DataFrame with date and artist information
        
    Returns:
        dict: Artist evolution analysis
    """
    if 'added_at' not in df.columns or 'artist_name' not in df.columns:
        return {'error': 'Missing required columns'}
    
    try:
        df_temp = df.copy()
        df_temp['added_at'] = pd.to_datetime(df_temp['added_at'])
        df_temp['month'] = df_temp['added_at'].dt.to_period('M')
        
        # Artist discovery timeline
        first_appearance = df_temp.groupby('artist_name')['added_at'].min()
        
        # Artists by discovery period
        discovery_periods = {}
        for artist, first_date in first_appearance.items():
            period = first_date.to_period('Y')
            if period not in discovery_periods:
                discovery_periods[period] = []
            discovery_periods[period].append(artist)
        
        # Artist consistency (how often they appear)
        artist_monthly_counts = df_temp.groupby(['month', 'artist_name']).size().unstack(fill_value=0)
        
        evolution = {
            'discovery_timeline': {str(k): v for k, v in discovery_periods.items()},
            'first_appearances': {artist: str(date) for artist, date in first_appearance.items()},
            'total_discovery_periods': len(discovery_periods),
            'artists_per_period': {str(k): len(v) for k, v in discovery_periods.items()}
        }
        
        return evolution
        
    except Exception as e:
        return {'error': f'Error analyzing artist evolution: {e}'}


def calculate_diversity_metrics(df):
    """
    Calculate diversity metrics for the music library
    
    Args:
        df: Cleaned DataFrame
        
    Returns:
        dict: Diversity metrics
    """
    metrics = {}
    
    # Artist diversity
    if 'artist_name' in df.columns:
        artist_counts = df['artist_name'].value_counts()
        total_artists = len(artist_counts)
        
        # Simpson's diversity index for artists
        n = len(df)
        simpson_index = sum((count * (count - 1)) / (n * (n - 1)) for count in artist_counts)
        simpson_diversity = 1 - simpson_index
        
        metrics['artist_diversity'] = {
            'total_unique_artists': total_artists,
            'simpson_diversity_index': simpson_diversity,
            'most_common_percentage': (artist_counts.iloc[0] / len(df)) * 100,
            'top_10_percentage': (artist_counts.head(10).sum() / len(df)) * 100
        }
    
    # Album diversity
    if 'album_name' in df.columns:
        album_counts = df['album_name'].value_counts()
        total_albums = len(album_counts)
        
        metrics['album_diversity'] = {
            'total_unique_albums': total_albums,
            'most_common_percentage': (album_counts.iloc[0] / len(df)) * 100,
            'single_track_albums': len(album_counts[album_counts == 1])
        }
    
    return metrics
