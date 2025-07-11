"""
🎵 Project Orpheus - Data Processor Module

Handles loading and cleaning of Spotify playlist CSV data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')


def load_csv_data(file_path):
    """
    Load CSV data from Exportify format
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        pandas.DataFrame: Raw loaded data
    """
    try:
        # Handle both string and Path objects
        file_path = Path(file_path)
        
        # Load with flexible encoding
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin-1')
        
        print(f"✅ Loaded {len(df)} rows from {file_path.name}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
        raise


def clean_data(df):
    """
    Clean and standardize the loaded data
    
    Args:
        df: Raw DataFrame from load_csv_data
        
    Returns:
        pandas.DataFrame: Cleaned data
    """
    try:
        df_clean = df.copy()
        
        # Standardize column names (handle different Exportify formats)
        column_mapping = {
            'Track Name': 'track_name',
            'Artist Name(s)': 'artist_name',
            'Album Name': 'album_name',
            'Added At': 'added_at',
            'Track URI': 'track_uri',
            'Artist URI(s)': 'artist_uri',
            'Album URI': 'album_uri',
            'Duration (ms)': 'duration_ms',
            'Popularity': 'popularity',
            'Preview URL': 'preview_url',
            'Spotify ID': 'spotify_id'
        }
        
        # Apply column mapping
        for old_name, new_name in column_mapping.items():
            if old_name in df_clean.columns:
                df_clean = df_clean.rename(columns={old_name: new_name})
        
        # Ensure essential columns exist
        essential_columns = ['track_name', 'artist_name']
        for col in essential_columns:
            if col not in df_clean.columns:
                # Try to find similar columns
                similar_cols = [c for c in df_clean.columns if col.split('_')[0].lower() in c.lower()]
                if similar_cols:
                    df_clean = df_clean.rename(columns={similar_cols[0]: col})
                else:
                    df_clean[col] = 'Unknown'
        
        # Clean data quality issues
        initial_count = len(df_clean)
        
        # Remove rows with missing essential data
        df_clean = df_clean.dropna(subset=['track_name', 'artist_name'])
        
        # Remove duplicates based on track and artist
        df_clean = df_clean.drop_duplicates(subset=['track_name', 'artist_name'])
        
        # Clean text fields
        text_columns = ['track_name', 'artist_name', 'album_name']
        for col in text_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip()
                df_clean[col] = df_clean[col].replace('nan', 'Unknown')
        
        # Handle date column
        if 'added_at' in df_clean.columns:
            try:
                df_clean['added_at'] = pd.to_datetime(df_clean['added_at'], errors='coerce')
            except:
                pass
        
        # Handle numeric columns
        if 'popularity' in df_clean.columns:
            df_clean['popularity'] = pd.to_numeric(df_clean['popularity'], errors='coerce')
        
        if 'duration_ms' in df_clean.columns:
            df_clean['duration_ms'] = pd.to_numeric(df_clean['duration_ms'], errors='coerce')
        
        cleaned_count = len(df_clean)
        removed_count = initial_count - cleaned_count
        
        print(f"🧹 Cleaned data: {cleaned_count} rows remaining ({removed_count} removed)")
        
        return df_clean
        
    except Exception as e:
        print(f"❌ Error cleaning data: {e}")
        raise


def validate_data_quality(df):
    """
    Validate data quality and return report
    
    Args:
        df: Cleaned DataFrame
        
    Returns:
        dict: Quality report
    """
    report = {
        'total_rows': len(df),
        'columns': list(df.columns),
        'missing_data': {},
        'data_types': {},
        'quality_score': 0
    }
    
    # Check for missing data
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        missing_pct = (missing_count / len(df)) * 100
        report['missing_data'][col] = {
            'count': missing_count,
            'percentage': missing_pct
        }
    
    # Check data types
    for col in df.columns:
        report['data_types'][col] = str(df[col].dtype)
    
    # Calculate quality score
    essential_cols = ['track_name', 'artist_name']
    quality_score = 100
    
    for col in essential_cols:
        if col in df.columns:
            missing_pct = report['missing_data'][col]['percentage']
            quality_score -= missing_pct * 2  # Penalty for missing essential data
    
    report['quality_score'] = max(0, quality_score)
    
    return report


def get_data_summary(df):
    """
    Generate a summary of the dataset
    
    Args:
        df: Cleaned DataFrame
        
    Returns:
        dict: Data summary
    """
    summary = {
        'total_tracks': len(df),
        'unique_artists': 0,
        'unique_albums': 0,
        'date_range': None,
        'most_common_artist': None,
        'most_common_album': None,
        'average_popularity': None
    }
    
    # Artist stats
    if 'artist_name' in df.columns:
        summary['unique_artists'] = df['artist_name'].nunique()
        artist_counts = df['artist_name'].value_counts()
        if len(artist_counts) > 0:
            summary['most_common_artist'] = artist_counts.index[0]
    
    # Album stats  
    if 'album_name' in df.columns:
        summary['unique_albums'] = df['album_name'].nunique()
        album_counts = df['album_name'].value_counts()
        if len(album_counts) > 0:
            summary['most_common_album'] = album_counts.index[0]
    
    # Date range
    if 'added_at' in df.columns:
        try:
            dates = pd.to_datetime(df['added_at'])
            summary['date_range'] = {
                'earliest': dates.min(),
                'latest': dates.max(),
                'span_days': (dates.max() - dates.min()).days
            }
        except:
            pass
    
    # Popularity
    if 'popularity' in df.columns:
        summary['average_popularity'] = df['popularity'].mean()
    
    return summary
