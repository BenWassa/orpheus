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
├── data_loader.py       # Data ingestion and validation
├── pattern_detector.py  # Pattern recognition algorithms
├── emotional_analyzer.py # Emotional mapping and correlation
├── visualizer.py        # Chart and timeline generation
└── utils.py            # Shared utilities and helpers
```

### Data Pipeline
1. **Ingestion**: Load Spotify Exportify CSV files
2. **Validation**: Verify data integrity and completeness
3. **Processing**: Clean, normalize, and feature engineer
4. **Analysis**: Apply pattern detection algorithms
5. **Mapping**: Correlate patterns with emotional states
6. **Visualization**: Generate interactive timelines and reports

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

### Implemented
- ✅ Project structure and documentation
- ✅ Data schema definition (Exportify format)
- ✅ Sample dataset (37-track hip-hop playlist)
- ✅ Development environment setup

### In Development
- 🔄 Core Python modules (data_loader, pattern_detector)
- 🔄 Initial data exploration notebook
- 🔄 Pattern detection algorithms

### Planned
- 📋 Emotional analysis framework
- 📋 Interactive visualization dashboard
- 📋 Spotify Web API integration
- 📋 Audio feature analysis
- 📋 Expanded data source support

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
