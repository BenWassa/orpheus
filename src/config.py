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
