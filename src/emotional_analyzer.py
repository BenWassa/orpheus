# Project Structure
orpheus/
├── data/
│   ├── raw/                # user drops Exportify CSVs here
│   └── processed/          # pipeline writes parquet/feather here
├── src/
│   ├── __init__.py
│   ├── config.py           # paths, environment variables
│   ├── data_processing.py  # load / clean / validate
│   ├── pattern_analysis.py # descriptive metrics & repeat-obsession logic
│   ├── emotion_analysis.py # valence & lyric sentiment tagging
│   └── visualization.py    # matplotlib helpers & streamlit hooks
├── ui/
│   └── app.py              # minimal Streamlit dashboard
├── requirements.txt
└── .gitignore

# requirements.txt
pandas>=2.0
numpy>=1.26
spotipy>=2.23
textblob>=0.18
nrclex>=4.0
streamlit>=1.34
matplotlib>=3.8
python-dotenv>=1.0
pyarrow>=12.0

# .gitignore
# Environment variables
.env
.env.local

# Data files
data/raw/*.csv
data/processed/*.parquet
data/processed/*.feather

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Jupyter
.ipynb_checkpoints

# src/__init__.py
"""
Project Orpheus - Music Listening Pattern Analysis

A Python framework for extracting emotional patterns from personal music listening data.
Analyzes Spotify playlist exports to identify recurring musical themes, obsessions, 
and emotional cycles.

See README.md for full documentation and usage instructions.
"""

__version__ = "0.1.0"
__author__ = "Project Orpheus Team"

# src/config.py
"""
Configuration module for Project Orpheus.

Centralizes paths, environment variables, and system settings.
All secrets are pulled from environment variables - never hard-coded.
"""

import os
from pathlib import Path
from typing import Dict, Any

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR_RAW = DATA_DIR / "raw"
DATA_DIR_PROCESSED = DATA_DIR / "processed"

# Ensure data directories exist
DATA_DIR_RAW.mkdir(parents=True, exist_ok=True)
DATA_DIR_PROCESSED.mkdir(parents=True, exist_ok=True)

# Spotify API credentials (from environment)
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Analysis settings
DEFAULT_REPEAT_THRESHOLD = 10
DEFAULT_TOP_N = 10

# Exportify CSV expected columns
EXPORTIFY_REQUIRED_COLUMNS = [
    "Track URI",
    "Track Name", 
    "Artist URI(s)",
    "Artist Name(s)",
    "Album URI",
    "Album Name",
    "Album Artist URI(s)",
    "Album Artist Name(s)",
    "Album Release Date",
    "Album Image URL",
    "Disc Number",
    "Track Number",
    "Track Duration (ms)",
    "Track Preview URL",
    "Explicit",
    "Popularity",
    "ISRC",
    "Added By",
    "Added At"
]

def get_config() -> Dict[str, Any]:
    """
    Get complete configuration dictionary.
    
    Returns:
        Dict containing all configuration values.
    """
    return {
        "paths": {
            "project_root": PROJECT_ROOT,
            "data_dir": DATA_DIR,
            "data_raw": DATA_DIR_RAW,
            "data_processed": DATA_DIR_PROCESSED,
        },
        "spotify": {
            "client_id": SPOTIFY_CLIENT_ID,
            "client_secret": SPOTIFY_CLIENT_SECRET,
        },
        "analysis": {
            "repeat_threshold": DEFAULT_REPEAT_THRESHOLD,
            "top_n": DEFAULT_TOP_N,
        },
        "exportify_columns": EXPORTIFY_REQUIRED_COLUMNS,
    }

# src/data_processing.py
"""
Data processing module for Project Orpheus.

Handles loading, cleaning, and validation of Exportify CSV files.
See 🔍 How It Works, step 1 in README for data pipeline overview.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

from .config import EXPORTIFY_REQUIRED_COLUMNS, DATA_DIR_PROCESSED

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_exportify(csv_path: Path) -> pd.DataFrame:
    """
    Load Exportify CSV file into pandas DataFrame.
    
    Args:
        csv_path: Path to the Exportify CSV file
        
    Returns:
        Raw DataFrame with original column names and data types
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        pd.errors.EmptyDataError: If CSV is empty
        pd.errors.ParserError: If CSV format is invalid
    """
    logger.info(f"Loading Exportify CSV from: {csv_path}")
    
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    try:
        # Load with minimal assumptions, handle various encodings
        df = pd.read_csv(csv_path, encoding='utf-8')
        logger.info(f"Successfully loaded {len(df)} rows from {csv_path.name}")
        return df
    except UnicodeDecodeError:
        # Try alternative encoding
        df = pd.read_csv(csv_path, encoding='latin1')
        logger.info(f"Successfully loaded {len(df)} rows from {csv_path.name} (latin1 encoding)")
        return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and validate Exportify DataFrame.
    
    Performs data type coercion, date parsing, duplicate removal,
    and validates against expected Exportify schema.
    
    Args:
        df: Raw DataFrame from load_exportify()
        
    Returns:
        Cleaned DataFrame with proper data types and no duplicates
        
    Raises:
        ValueError: If required columns are missing
    """
    logger.info("Starting data cleaning process")
    
    # Create a copy to avoid modifying original
    df_clean = df.copy()
    
    # Validate required columns (flexible matching)
    available_columns = set(df_clean.columns)
    
    # Check for essential columns (flexible naming)
    essential_mappings = {
        'track_name': ['Track Name', 'track_name', 'name', 'song'],
        'artist_name': ['Artist Name(s)', 'artist_name', 'artist', 'Artist Name'],
        'album_name': ['Album Name', 'album_name', 'album'],
        'added_at': ['Added At', 'added_at', 'date_added', 'timestamp']
    }
    
    # Map columns to standard names
    column_mapping = {}
    for standard_name, possible_names in essential_mappings.items():
        for col in df_clean.columns:
            if col in possible_names:
                column_mapping[col] = standard_name
                break
    
    # Rename columns
    df_clean = df_clean.rename(columns=column_mapping)
    
    # Data type coercion
    try:
        # Parse dates if 'added_at' column exists
        if 'added_at' in df_clean.columns:
            df_clean['added_at'] = pd.to_datetime(df_clean['added_at'], errors='coerce')
        
        # Convert duration to numeric if present
        duration_cols = ['Track Duration (ms)', 'duration_ms', 'duration']
        for col in duration_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                break
        
        # Convert popularity to numeric if present
        popularity_cols = ['Popularity', 'popularity', 'play_count']
        for col in popularity_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                break
    
    except Exception as e:
        logger.warning(f"Data type coercion warning: {e}")
    
    # Remove duplicates based on track and artist
    initial_count = len(df_clean)
    if 'track_name' in df_clean.columns and 'artist_name' in df_clean.columns:
        df_clean = df_clean.drop_duplicates(subset=['track_name', 'artist_name'])
    else:
        df_clean = df_clean.drop_duplicates()
    
    duplicates_removed = initial_count - len(df_clean)
    if duplicates_removed > 0:
        logger.info(f"Removed {duplicates_removed} duplicate rows")
    
    # Remove rows with missing essential data
    essential_cols = ['track_name', 'artist_name']
    for col in essential_cols:
        if col in df_clean.columns:
            df_clean = df_clean.dropna(subset=[col])
    
    logger.info(f"Data cleaning complete. Final dataset: {len(df_clean)} rows")
    return df_clean


def save_processed(df: pd.DataFrame, out_path: Path) -> None:
    """
    Save processed DataFrame to parquet format.
    
    Args:
        df: Cleaned DataFrame from clean()
        out_path: Path where processed data should be saved
    """
    logger.info(f"Saving processed data to: {out_path}")
    
    # Ensure output directory exists
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save as parquet for efficient storage and fast loading
    df.to_parquet(out_path, engine='pyarrow', index=False)
    logger.info(f"Successfully saved {len(df)} rows to {out_path}")


def validate_exportify_schema(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate DataFrame against expected Exportify schema.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        Dictionary with validation results and recommendations
    """
    validation_results = {
        'is_valid': True,
        'missing_columns': [],
        'extra_columns': [],
        'recommendations': []
    }
    
    available_columns = set(df.columns)
    expected_columns = set(EXPORTIFY_REQUIRED_COLUMNS)
    
    # Check for missing columns
    missing = expected_columns - available_columns
    if missing:
        validation_results['missing_columns'] = list(missing)
        validation_results['is_valid'] = False
        validation_results['recommendations'].append(
            f"Consider updating Exportify or manually adding: {', '.join(missing)}"
        )
    
    # Check for extra columns
    extra = available_columns - expected_columns
    if extra:
        validation_results['extra_columns'] = list(extra)
        validation_results['recommendations'].append(
            f"Extra columns found (may be useful): {', '.join(extra)}"
        )
    
    return validation_results

# src/pattern_analysis.py
"""
Pattern analysis module for Project Orpheus.

Implements descriptive metrics and repeat-obsession detection logic.
See 🔍 How It Works, step 2 in README for pattern detection methodology.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from collections import Counter
import logging

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
        # If no playlist column, create a dummy one
        logger.warning("No playlist column found, creating single 'Mixed' playlist")
        playlist_counts = pd.DataFrame({
            'playlist_name': ['Mixed'],
            'track_count': [len(df)]
        })
    else:
        playlist_counts = df[playlist_col].value_counts().head(n)
        playlist_counts = playlist_counts.reset_index()
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
        most_common_artist = df['artist_name'].value_counts().iloc[0] if len(df) > 0 else None
        stats['most_common_artist'] = {
            'name': df['artist_name'].value_counts().index[0] if len(df) > 0 else None,
            'count': most_common_artist
        }
    
    # Album statistics
    if 'album_name' in df.columns:
        unique_albums = df['album_name'].nunique()
        stats['unique_albums'] = unique_albums
        most_common_album = df['album_name'].value_counts().iloc[0] if len(df) > 0 else None
        stats['most_common_album'] = {
            'name': df['album_name'].value_counts().index[0] if len(df) > 0 else None,
            'count': most_common_album
        }
    
    # Date range analysis
    if 'added_at' in df.columns:
        valid_dates = df['added_at'].dropna()
        if len(valid_dates) > 0:
            stats['date_range'] = {
                'earliest': valid_dates.min(),
                'latest': valid_dates.max(),
                'span_days': (valid_dates.max() - valid_dates.min()).days
            }
    
    # Popularity analysis
    popularity_cols = ['Popularity', 'popularity', 'play_count']
    for col in popularity_cols:
        if col in df.columns:
            avg_popularity = df[col].mean()
            stats['average_popularity'] = avg_popularity
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
                'item': artist,
                'count': count,
                'type': 'artist',
                'intensity': count / threshold  # Relative intensity
            })
    
    # Track obsessions
    if 'track_name' in df.columns:
        track_counts = df['track_name'].value_counts()
        track_obsessions = track_counts[track_counts >= threshold]
        
        for track, count in track_obsessions.items():
            obsessions.append({
                'item': track,
                'count': count,
                'type': 'track',
                'intensity': count / threshold
            })
    
    # Album obsessions
    if 'album_name' in df.columns:
        album_counts = df['album_name'].value_counts()
        album_obsessions = album_counts[album_counts >= threshold]
        
        for album, count in album_obsessions.items():
            obsessions.append({
                'item': album,
                'count': count,
                'type': 'album',
                'intensity': count / threshold
            })
    
    obsessions_df = pd.DataFrame(obsessions)
    
    if len(obsessions_df) > 0:
        # Sort by intensity descending
        obsessions_df = obsessions_df.sort_values('intensity', ascending=False)
        logger.info(f"Found {len(obsessions_df)} obsessions above threshold")
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

# src/emotion_analysis.py
"""
Emotion analysis module for Project Orpheus.

Implements valence analysis and lyric sentiment tagging using Spotify API
and text processing libraries. See 🔍 How It Works, step 3 in README
for emotional mapping methodology.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

# Import libraries with graceful fallbacks
try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    SPOTIPY_AVAILABLE = True
except ImportError:
    SPOTIPY_AVAILABLE = False
    logger.warning("Spotipy not available - audio features will be mocked")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    logger.warning("TextBlob not available - sentiment analysis will be mocked")

try:
    from nrclex import NRCLex
    NRCLEX_AVAILABLE = True
except ImportError:
    NRCLEX_AVAILABLE = False
    logger.warning("NRCLex not available - emotion analysis will be mocked")

from .config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET


def _get_spotify_client() -> Optional[spotipy.Spotify]:
    """
    Get authenticated Spotify client.
    
    Returns:
        Spotify client instance or None if authentication fails
    """
    if not SPOTIPY_AVAILABLE:
        return None
    
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        logger.warning("Spotify credentials not found in environment variables")
        return None
    
    try:
        credentials = SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        )
        return spotipy.Spotify(client_credentials_manager=credentials)
    except Exception as e:
        logger.error(f"Failed to authenticate with Spotify: {e}")
        return None


def add_spotify_audio_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add Spotify audio features to DataFrame.
    
    Audio features include valence, energy, danceability, acousticness,
    instrumentalness, liveness, speechiness, and tempo.
    
    Args:
        df: DataFrame with Spotify track URIs
        
    Returns:
        DataFrame with added audio feature columns
    """
    logger.info("Adding Spotify audio features")
    
    # Create copy to avoid modifying original
    df_with_features = df.copy()
    
    # Initialize audio feature columns
    audio_features = [
        'valence', 'energy', 'danceability', 'acousticness',
        'instrumentalness', 'liveness', 'speechiness', 'tempo'
    ]
    
    for feature in audio_features:
        df_with_features[feature] = np.nan
    
    # Get Spotify client
    spotify_client = _get_spotify_client()
    
    if spotify_client is None:
        logger.warning("Spotify client not available - generating mock audio features")
        # Generate mock features for testing
        np.random.seed(42)  # For reproducible results
        for feature in audio_features:
            if feature == 'tempo':
                df_with_features[feature] = np.random.uniform(60, 200, len(df))
            else:
                df_with_features[feature] = np.random.uniform(0, 1, len(df))
        
        logger.info("Mock audio features added successfully")
        return df_with_features
    
    # Extract track URIs
    track_uri_col = None
    for col in ['Track URI', 'track_uri', 'uri']:
        if col in df.columns:
            track_uri_col = col
            break
    
    if track_uri_col is None:
        logger.error("No track URI column found")
        return df_with_features
    
    # Get track IDs from URIs
    track_ids = []
    for uri in df[track_uri_col]:
        if pd.notna(uri) and uri.startswith('spotify:track:'):
            track_ids.append(uri.split(':')[-1])
        else:
            track_ids.append(None)
    
    # Fetch audio features in batches
    batch_size = 50  # Spotify API limit
    for i in range(0, len(track_ids), batch_size):
        batch_ids = [id for id in track_ids[i:i+batch_size] if id is not None]
        
        if not batch_ids:
            continue
        
        try:
            features = spotify_client.audio_features(batch_ids)
            
            # Map features back to DataFrame
            for j, feature_data in enumerate(features):
                if feature_data is not None:
                    df_idx = i + j
                    for feature in audio_features:
                        if feature in feature_data:
                            df_with_features.loc[df_idx, feature] = feature_data[feature]
            
        except Exception as e:
            logger.error(f"Error fetching audio features for batch {i//batch_size + 1}: {e}")
            continue
    
    feature_count = df_with_features['valence'].notna().sum()
    logger.info(f"Successfully added audio features for {feature_count} tracks")
    return df_with_features


def add_lyric_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add lyric sentiment analysis to DataFrame.
    
    Uses TextBlob for basic sentiment polarity and NRCLex for emotion detection.
    Note: This is a mock implementation as lyric fetching requires additional APIs.
    
    Args:
        df: DataFrame with track information
        
    Returns:
        DataFrame with added sentiment columns
    """
    logger.info("Adding lyric sentiment analysis")
    
    df_with_sentiment = df.copy()
    
    # Initialize sentiment columns
    sentiment_cols = [
        'lyric_polarity', 'lyric_subjectivity', 'lyric_compound',
        'emotion_joy', 'emotion_sadness', 'emotion_anger', 'emotion_fear'
    ]
    
    for col in sentiment_cols:
        df_with_sentiment[col] = np.nan
    
    if not TEXTBLOB_AVAILABLE and not NRCLEX_AVAILABLE:
        logger.warning("Text analysis libraries not available - generating mock sentiment")
        # Generate mock sentiment for testing
        np.random.seed(42)
        for col in sentiment_cols:
            if col.startswith('emotion_'):
                df_with_sentiment[col] = np.random.uniform(0, 1, len(df))
            else:
                df_with_sentiment[col] = np.random.uniform(-1, 1, len(df))
        
        logger.info("Mock sentiment analysis added successfully")
        return df_with_sentiment
    
    # Mock lyric sentiment based on track/artist names
    # In a real implementation, this would fetch and analyze actual lyrics
    for idx, row in df_with_sentiment.iterrows():
        track_name = row.get('track_name', '') or row.get('Track Name', '')
        artist_name = row.get('artist_name', '') or row.get('Artist Name(s)', '')
        
        # Create mock lyric text from track/artist names
        mock_lyric = f"{track_name} {artist_name}".lower()
        
        if TEXTBLOB_AVAILABLE:
            try:
                blob = TextBlob(mock_lyric)
                df_with_sentiment.loc[idx, 'lyric_polarity'] = blob.sentiment.polarity
                df_with_sentiment.loc[idx, 'lyric_subjectivity'] = blob.sentiment.subjectivity
            except Exception as e:
                logger.debug(f"TextBlob error for row {idx}: {e}")
        
        if NRCLEX_AVAILABLE:
            try:
                emotion = NRCLex(mock_lyric)
                df_with_sentiment.loc[idx, 'emotion_joy'] = emotion.affect_frequencies.get('joy', 0)
                df_with_sentiment.loc[idx, 'emotion_sadness'] = emotion.affect_frequencies.get('sadness', 0)
                df_with_sentiment.loc[idx, 'emotion_anger'] = emotion.affect_frequencies.get('anger', 0)
                df_with_sentiment.loc[idx, 'emotion_fear'] = emotion.affect_frequencies.get('fear', 0)
            except Exception as e:
                logger.debug(f"NRCLex error for row {idx}: {e}")
    
    logger.info("Lyric sentiment analysis complete")
    return df_with_sentiment


def compute_emotion_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute overall emotional summary statistics.

    Args:
        df: DataFrame with audio features and sentiment data

    Returns:
        Dictionary with emotion summary statistics
    """
    logger.info("Computing emotion summary statistics")

    summary = {
        'audio_features': {},
        'sentiment': {},
        'emotion_profile': {},
        'recommendations': []
    }

    # Audio feature statistics
    audio_features = ['valence', 'energy', 'danceability', 'acousticness']
    for feature in audio_features:
        if feature in df.columns:
            values = df[feature].dropna()
            if len(values) > 0:
                summary['audio_features'][feature] = {
                    'mean': values.mean(),
                    'std': values.std(),
                    'min': values.min(),
                    'max': values.max(),
                    'median': values.median()
                }

    # Sentiment statistics
    sentiment_cols = ['lyric_polarity', 'lyric_subjectivity']
    for col in sentiment_cols:
        if col in df.columns:
            values = df[col].dropna()
            if len(values) > 0:
                summary['sentiment'][col] = {
                    'mean': values.mean(),
                    'std': values.std(),
                    'distribution': {
                        'positive': int((values > 0.1).sum()),
                        'negative': int((values < -0.1).sum()),
                        'neutral': int(((values >= -0.1) & (values <= 0.1)).sum())
                    }
                }

    # Emotion profile
    emotion_cols = ['emotion_joy', 'emotion_sadness', 'emotion_anger', 'emotion_fear']
    for col in emotion_cols:
        if col in df.columns:
            values = df[col].dropna()
            if len(values) > 0:
                summary['emotion_profile'][col] = values.mean()

    # Generate recommendations based on detected patterns
    avg_valence = summary['audio_features'].get('valence', {}).get('mean')
    avg_energy = summary['audio_features'].get('energy', {}).get('mean')

    if avg_valence is not None:
        if avg_valence > 0.7:
            summary['recommendations'].append(
                "High valence detected — your taste leans upbeat, energetic, and positive."
            )
        elif avg_valence < 0.3:
            summary['recommendations'].append(
                "Low valence detected — your taste tends toward introspective or melancholic moods."
            )

    if avg_energy is not None:
        if avg_energy > 0.7:
            summary['recommendations'].append(
                "High energy detected — you prefer dynamic, lively tracks."
            )
        elif avg_energy < 0.3:
            summary['recommendations'].append(
                "Low energy detected — you enjoy calm, mellow, or acoustic music."
            )

    logger.info("Emotion summary statistics computed successfully")
    return summary
