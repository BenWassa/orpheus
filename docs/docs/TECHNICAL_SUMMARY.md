# Project Orpheus - Technical Summary

**A Python-based music listening pattern analysis tool for emotional introspection**

---

## Overview

Project Orpheus is a data analysis framework designed to extract emotional patterns from personal music listening data. The system processes Spotify playlist exports to identify recurring musical themes, obsessions, and emotional cycles, providing users with insights into their psychological patterns through their music consumption.

## Technology Stack

### Core Framework
- **Language**: Python 3.8+
- **Environment**: Jupyter Lab/Notebook for interactive analysis
- **Data Processing**: pandas, numpy, scipy
- **Statistical Analysis**: scikit-learn, statsmodels
- **Visualization**: matplotlib, seaborn, plotly, plotly-dash

### Future Integrations (Planned)
- **Music APIs**: spotipy (Spotify Web API)
- **Audio Analysis**: librosa (audio feature extraction)
- **Text Processing**: nltk (lyrics analysis)
- **Web Interface**: dash (interactive dashboards)

## Architecture

### Modular Design
```
src/
├── config.py            # Configuration and settings management
├── data_processing.py   # Data ingestion, validation, and cleaning
├── pattern_analysis.py  # Pattern recognition and statistics
├── emotion_analysis.py  # Emotional mapping and sentiment analysis
├── visualization.py     # Chart and timeline generation
└── __init__.py         # Package initialization
```

### Data Pipeline
1. **Configuration**: Load settings and API credentials via `config.py`
2. **Ingestion**: Load Spotify Exportify CSV files via `data_processing.py`
3. **Validation**: Verify data integrity and completeness
4. **Processing**: Clean, normalize, and feature engineer
5. **Pattern Analysis**: Apply statistical algorithms via `pattern_analysis.py`
6. **Emotional Mapping**: Correlate patterns with emotional states via `emotion_analysis.py`
7. **Visualization**: Generate interactive charts and reports via `visualization.py`
8. **Web Interface**: Present results through Streamlit dashboard

## Data Model

### Primary Data Source
- **Format**: CSV exports from [Exportify](https://github.com/watsonbox/exportify)
- **Schema**: 19 columns including track metadata, timing, and user context
- **Key Fields**:
  - Track/Artist/Album metadata
  - Release dates and duration
  - Add timestamps (listening chronology)
  - Popularity scores and genre indicators

### Processed Data Structure
```
data/
├── raw/             # Original Exportify CSV files
├── processed/       # Cleaned datasets with features
└── annotations/     # Manual emotional/life event tags
```

## Analysis Methodology

### Pattern Detection Algorithms
- **Temporal Clustering**: Identify listening phases and obsessions
- **Artist/Genre Frequency**: Track musical preference evolution
- **Mood Correlation**: Map audio features to emotional states
- **Repetition Analysis**: Detect recurring themes and cycles

### Emotional Mapping Framework
- **Valence/Energy Analysis**: Audio feature-based mood detection
- **Lyrical Sentiment**: Text analysis of song lyrics (future)
- **Personal Annotations**: User-defined emotional tags
- **Life Event Correlation**: Timeline alignment with significant events

## Workflow

### Notebook-Based Analysis
```
notebooks/
├── 01_data_exploration.ipynb    # Initial data assessment
├── 02_pattern_analysis.ipynb    # Core pattern detection
├── 03_emotional_mapping.ipynb   # Emotional correlation analysis
└── 04_visualization.ipynb       # Report and chart generation
```

### Output Generation
```
output/
├── visualizations/  # PNG/SVG charts and timelines
├── reports/        # HTML analysis summaries
└── exports/        # JSON/CSV processed insights
```

## Current Status

## Current Status

### Implemented
- ✅ Complete project structure and documentation
- ✅ Core Python modules (config, data_processing, pattern_analysis, emotion_analysis, visualization)
- ✅ Data schema definition (Exportify format)
- ✅ Sample dataset processing and analysis
- ✅ Streamlit web interface
- ✅ Comprehensive visualization suite
- ✅ Development environment setup

### Fully Functional
- ✅ Data loading and cleaning pipeline
- ✅ Pattern detection algorithms
- ✅ Emotional analysis framework
- ✅ Interactive visualization dashboard
- ✅ HTML report generation

### Future Enhancements
- 📋 Spotify Web API integration for live data
- 📋 Advanced audio feature analysis with librosa
- 📋 Expanded data source support (Apple Music, Last.fm)
- 📋 Machine learning pattern prediction

## Development Standards

### Code Quality
- **Style**: PEP 8 compliance with black formatter
- **Testing**: pytest framework for unit tests
- **Linting**: flake8 for code quality checks
- **Documentation**: Comprehensive docstrings and type hints

### Data Security
- Raw personal data excluded from version control
- Sensitive files masked with gitignore patterns
- Sample/anonymized data only in repository

## Usage Patterns

### Target Users
- **Primary**: Individual users seeking emotional introspection
- **Secondary**: Researchers studying music-emotion correlation
- **Future**: Mental health professionals (with appropriate data handling)

### Typical Workflow
1. Export Spotify playlists via Exportify
2. Place CSV files in `data/raw/` directory
3. Run data exploration notebook for initial insights
4. Execute pattern analysis for deep insights
5. Generate emotional timeline visualizations
6. Reflect on patterns and correlations

## Extensibility

### Plugin Architecture (Planned)
- Custom pattern detection algorithms
- Additional music streaming service support
- External emotional data integration (mood tracking apps)
- Advanced visualization templates

### API Integration Points
- Spotify Web API for extended metadata
- Apple Music API (future expansion)
- Last.fm scrobbling data
- Mental health app APIs (with permissions)

## Performance Considerations

### Scalability
- **Current**: Optimized for personal datasets (hundreds to thousands of tracks)
- **Future**: Horizontal scaling for larger datasets and multiple users
- **Constraints**: Jupyter-based interactive analysis prioritized over production performance

### Resource Requirements
- **Memory**: Moderate (typical datasets < 100MB)
- **Processing**: CPU-bound for pattern analysis
- **Storage**: Minimal (mostly CSV and visualization files)

---

**Project Repository**: https://github.com/BenWassa/orpheus  
**Status**: Early development phase  
**Last Updated**: January 2025
