"""
Data processing module for Project Orpheus.

Handles loading, cleaning, and validation of Exportify CSV files.
See 🔍 How It Works, step 1 in README for data pipeline overview.
"""
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Any

from config import EXPORTIFY_REQUIRED_COLUMNS, DATA_DIR_PROCESSED

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
        df = pd.read_csv(csv_path, encoding='utf-8')
    except UnicodeDecodeError:
        logger.warning("UTF-8 encoding failed, trying latin-1")
        df = pd.read_csv(csv_path, encoding='latin-1')
    
    logger.info(f"Successfully loaded {len(df)} rows from {csv_path.name}")
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
        for possible_name in possible_names:
            if possible_name in available_columns:
                column_mapping[possible_name] = standard_name
                break
    
    # Rename columns
    df_clean = df_clean.rename(columns=column_mapping)
    
    # Data type coercion
    try:
        # Parse dates
        if 'added_at' in df_clean.columns:
            df_clean['added_at'] = pd.to_datetime(df_clean['added_at'], errors='coerce')
        
        # Clean string columns
        string_cols = ['track_name', 'artist_name', 'album_name']
        for col in string_cols:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip()
    
    except Exception as e:
        logger.warning(f"Data type coercion failed: {e}")
    
    # Remove duplicates based on track and artist
    initial_count = len(df_clean)
    if 'track_name' in df_clean.columns and 'artist_name' in df_clean.columns:
        df_clean = df_clean.drop_duplicates(subset=['track_name', 'artist_name'], keep='first')
    else:
        df_clean = df_clean.drop_duplicates()
    
    duplicates_removed = initial_count - len(df_clean)
    if duplicates_removed > 0:
        logger.info(f"Removed {duplicates_removed} duplicate rows")
    
    # Remove rows with missing essential data
    essential_cols = ['track_name', 'artist_name']
    for col in essential_cols:
        if col in df_clean.columns:
            initial_len = len(df_clean)
            df_clean = df_clean[df_clean[col].notna() & (df_clean[col] != '')]
            removed = initial_len - len(df_clean)
            if removed > 0:
                logger.info(f"Removed {removed} rows with missing {col}")
    
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
            f"Missing {len(missing)} expected columns. Check Exportify export settings."
        )
    
    # Check for extra columns
    extra = available_columns - expected_columns
    if extra:
        validation_results['extra_columns'] = list(extra)
        validation_results['recommendations'].append(
            f"Found {len(extra)} unexpected columns. These will be preserved."
        )
    
    return validation_results
