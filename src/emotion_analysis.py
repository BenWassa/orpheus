"""
Emotion analysis module for Project Orpheus.

Implements valence analysis and lyric sentiment tagging using Spotify API
and text processing libraries. See 🔍 How It Works, step 3 in README
for emotional mapping methodology.
"""
import logging
import warnings
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

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
                    idx = i + j
                    for feature in audio_features:
                        df_with_features.loc[idx, feature] = feature_data.get(feature)
            
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
