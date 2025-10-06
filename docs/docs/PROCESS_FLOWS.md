# 🎵 Project Orpheus - Process Flows & New Architecture (Updated)

**Complete guide to the reorganized system with numbered folders**

---

## 📁 **Current Repository Structure (Post-Cleanup)**

```
📂 Project Orpheus/
├── 📁 01_setup/          # 🔧 Installation, testing, launch scripts
│   ├── 📄 requirements.txt       # Python dependencies
│   ├── 📄 test_setup.py         # Validation & health check ✅ WORKING
│   ├── 📄 run_analysis.py       # Batch analysis script  
│   ├── 📄 test_imports.py       # Import testing
│   ├── 📄 launch_dashboard.bat  # Windows launcher
│   └── 📄 .env.template         # Environment variables template
│
├── 📁 02_core/           # 🧠 Core analysis modules (CLEANED UP)
│   ├── 📄 config.py             # Configuration & paths
│   ├── 📄 data_processor.py     # CSV loading & cleaning
│   ├── 📄 pattern_analyzer.py   # Pattern detection & stats
│   ├── 📄 emotion_analyzer.py   # Sentiment & audio features
│   └── 📄 visualizer.py         # Charts & visualizations
│
├── 📁 03_interface/      # 🌐 Web dashboard (CONSOLIDATED)
│   └── 📄 streamlit_app.py      # Single Streamlit app ✅ WORKING
│
├── 📁 04_data/          # 📊 Data storage
│   ├── 📁 raw/                  # Original Exportify CSV files
│   └── 📁 processed/            # Cleaned data (Parquet format)
│
├── 📁 05_output/        # 📈 Analysis results
│   ├── 📁 reports/              # HTML analysis reports
│   ├── 📁 visualizations/       # Generated charts (PNG)
│   └── 📁 exports/              # Data exports
│
├── 📁 06_docs/          # 📚 Documentation (ORGANIZED)
│   ├── 📄 QUICK_START.md        # 30-second start guide
│   ├── 📄 USER_GUIDE.md         # Complete user manual
│   ├── 📄 TECHNICAL_SUMMARY.md  # Technical architecture
│   ├── 📄 PROCESS_FLOWS.md      # This file - workflows
│   ├── 📄 DOCUMENTATION_INDEX.md # All docs index
│   └── 📁 archive/              # Old documentation versions
│
├── 📁 orpheus_venv/     # 🐍 Python virtual environment
├── 📄 launch_orpheus.bat        # 🚀 Quick launch script ✅ WORKING
├── 📄 README.md                 # Clean project overview
└── 📄 __init__.py               # Python package marker
```

**✅ MAJOR CLEANUP COMPLETED:**
- ❌ Removed: `src/` folder → ✅ Moved to `02_core/`
- ❌ Removed: `ui/` folder → ✅ Moved to `03_interface/`  
- ❌ Removed: Duplicate streamlit files → ✅ Single `streamlit_app.py`
- ❌ Removed: Old virtual environments → ✅ Keep only `orpheus_venv/`
- ❌ Removed: Cleanup scripts → ✅ Clean repository

```
📥 Data Input (CSV) 
    ↓
📊 Data Processing (02_core/data_processor.py)
    ↓
🔀 Analysis Branch Split
    ├── 🎵 Pattern Analysis (02_core/pattern_analyzer.py)
    ├── 💭 Emotion Analysis (02_core/emotion_analyzer.py)
    └── 📈 Visualization (02_core/visualizer.py)
    ↓
🌐 User Interface (03_interface/streamlit_app.py)
    ↓
💾 Output Generation (05_output/)
```

---

## 📋 **Detailed Process Flows**

### **1. Data Ingestion Flow**
```
🔄 PROCESS: CSV → Clean DataFrame

INPUT: 04_data/raw/*.csv (Exportify format)
    ↓
[data_processor.load_exportify()]
    ├── ✅ Encoding detection (UTF-8 → latin-1 fallback)
    ├── ✅ DataFrame creation
    └── ✅ Column validation
    ↓
[data_processor.clean()]
    ├── ✅ Remove duplicates
    ├── ✅ Handle missing values
    ├── ✅ Standardize formats
    ├── ✅ Type conversion
    └── ✅ Data validation
    ↓
OUTPUT: Cleaned pandas DataFrame
```

**Key Functions:**
- `load_exportify(csv_path)` → Raw DataFrame
- `clean(df)` → Cleaned DataFrame
- `save_processed(df, path)` → Saves to 04_data/processed/

### **2. Pattern Analysis Flow**
```
🔄 PROCESS: DataFrame → Listening Patterns

INPUT: Cleaned DataFrame
    ↓
[pattern_analyzer.playlist_stats()]
    ├── 📊 Track count analysis
    ├── 🎤 Artist frequency counting
    ├── 💿 Album analysis
    ├── 📅 Date range computation
    └── 📈 Popularity metrics
    ↓
[pattern_analyzer.repeat_obsessions()]
    ├── 🔢 Frequency thresholding
    ├── 📊 Percentage calculations
    ├── 🏷️ Type classification (artist/track/album)
    └── 📋 Ranking & sorting
    ↓
[pattern_analyzer.temporal_patterns()]
    ├── 📅 Date grouping
    ├── 📊 Monthly/weekly aggregation
    ├── 🔍 Peak period detection
    └── 📈 Trend analysis
    ↓
OUTPUT: Statistics dictionaries & DataFrames
```

**Key Functions:**
- `playlist_stats(df)` → Summary statistics
- `repeat_obsessions(df, threshold)` → Obsession analysis
- `temporal_patterns(df)` → Time-based patterns

### **3. Emotion Analysis Flow**
```
🔄 PROCESS: DataFrame → Emotional Insights

INPUT: Cleaned DataFrame
    ↓
[emotion_analyzer.add_spotify_audio_features()]
    ├── 🔑 Spotify API authentication
    ├── 🎵 Track ID extraction from URIs
    ├── 🎧 Audio feature retrieval (valence, energy, etc.)
    ├── 📊 Feature normalization
    └── 🔄 Batch processing (50 tracks/request)
    ↓
[emotion_analyzer.add_lyric_sentiment()]
    ├── 📝 Mock lyric generation (from track/artist names)
    ├── 🧠 TextBlob sentiment analysis
    ├── 😊 NRCLex emotion classification
    └── 📊 Sentiment scoring
    ↓
[emotion_analyzer.compute_emotion_summary()]
    ├── 📊 Feature aggregation
    ├── 📈 Statistical summaries (mean, std, etc.)
    ├── 🎯 Emotion profiling
    └── 💡 Insight generation
    ↓
OUTPUT: Enhanced DataFrame + Emotion Summary
```

**Key Functions:**
- `add_spotify_audio_features(df)` → Audio feature enhancement
- `add_lyric_sentiment(df)` → Sentiment analysis
- `compute_emotion_summary(df)` → Overall emotional profile

### **4. Visualization Flow**
```
🔄 PROCESS: Analysis Results → Visual Charts

INPUT: Enhanced DataFrame + Analysis Results
    ↓
[visualizer.plot_emotion_timeline()]
    ├── 📅 Date-based grouping
    ├── 📊 Emotion aggregation over time
    ├── 📈 Trend line generation
    └── 🎨 Matplotlib chart creation
    ↓
[visualizer.plot_top_artists()]
    ├── 🎤 Artist frequency ranking
    ├── 📊 Bar chart generation
    ├── 🎨 Color coding
    └── 📝 Label formatting
    ↓
[visualizer.plot_audio_features_radar()]
    ├── 🎵 Feature normalization
    ├── 📊 Radar chart coordinates
    ├── 🎨 Polar plot creation
    └── 🏷️ Feature labeling
    ↓
[visualizer.create_emotion_summary_text()]
    ├── 📊 Statistical analysis
    ├── 💡 Insight generation
    ├── 📝 Natural language formatting
    └── 🎯 Recommendation creation
    ↓
OUTPUT: Matplotlib figures + Text summaries
```

**Key Functions:**
- `plot_emotion_timeline(df)` → Time-series emotional chart
- `plot_top_artists(df, n)` → Artist ranking chart
- `plot_audio_features_radar(df)` → Feature radar plot
- `create_emotion_summary_text(summary)` → Text insights

### **5. User Interface Flow**
```
🔄 PROCESS: User Interaction → Real-time Analysis

INPUT: User actions (file upload, parameter changes)
    ↓
[streamlit_app.main()]
    ├── 🎨 Page layout rendering
    ├── 📁 File upload handling
    ├── ⚙️ Parameter input
    └── 🔄 Session state management
    ↓
[streamlit_app.analyze_uploaded_data()]
    ├── 💾 Temporary file saving
    ├── 🔄 Processing pipeline execution
    ├── 📊 Real-time progress display
    └── 💾 Session state updating
    ↓
[streamlit_app.show_analysis_results()]
    ├── 📑 Tab-based organization
    ├── 📊 Interactive metric display
    ├── 📈 Chart rendering
    └── 📝 Insight presentation
    ↓
OUTPUT: Interactive web dashboard
```

**Key Components:**
- `main()` → App entry point
- `show_welcome_screen()` → Landing page
- `analyze_uploaded_data()` → File processing
- `show_analysis_results()` → Results display

---

## 🔧 **Configuration Management**

### **Central Configuration (02_core/config.py)**
```python
# File paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR_RAW = PROJECT_ROOT / "04_data" / "raw"
DATA_DIR_PROCESSED = PROJECT_ROOT / "04_data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "05_output"

# Analysis parameters
REPEAT_THRESHOLD = 10
TOP_N = 10

# API credentials
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
```

### **Environment Variables (.env)**
```
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

---

## 🚀 **Execution Paths**

### **Path 1: Quick Launch (`launch_orpheus.bat`)**
```
1. Change to project directory
2. Execute test_setup.py for validation
3. If tests pass → Launch Streamlit app
4. If tests fail → Show error and pause
5. Open browser to http://localhost:8501
```

### **Path 2: Manual Testing (`01_setup/test_setup.py`)**
```
1. Test module imports (config, data_processor, etc.)
2. Test data loading with sample CSV
3. Test analysis pipeline execution
4. Display validation results
5. Provide next step recommendations
```

### **Path 3: Batch Analysis (`01_setup/run_analysis.py`)**
```
1. Scan 04_data/raw/ for CSV files
2. Process each file through full pipeline
3. Generate comprehensive reports
4. Save results to 05_output/
5. Create visualization files
```

### **Path 4: Interactive Dashboard (`03_interface/streamlit_app.py`)**
```
1. Initialize Streamlit interface
2. Load existing session state (if any)
3. Handle user file uploads
4. Execute analysis pipeline on demand
5. Display results in interactive format
6. Allow parameter adjustment and re-analysis
```

---

## 📊 **Data Flow Diagram**

```
📁 04_data/raw/
    ├── playlist_1.csv ──┐
    ├── playlist_2.csv ──┤
    └── playlist_n.csv ──┤
                         ├──► [data_processor] ──► Clean DataFrame
                         │
📱 Upload Interface ─────┘                           │
                                                     ▼
                                            ┌─────────────────┐
                                            │  Analysis Hub   │
                                            └─────────────────┘
                                                     │
                    ┌────────────────────────────────┼────────────────────────────────┐
                    ▼                                ▼                                ▼
            [pattern_analyzer]              [emotion_analyzer]              [visualizer]
                    │                                │                                │
                    ▼                                ▼                                ▼
            📊 Patterns & Stats           💭 Emotions & Features           📈 Charts & Graphs
                    │                                │                                │
                    └────────────────────────────────┼────────────────────────────────┘
                                                     ▼
                                            🌐 Streamlit Interface
                                                     │
                                                     ▼
                                            📁 05_output/
                                            ├── reports/
                                            ├── visualizations/
                                            └── exports/
```

---

## 🧪 **Testing & Validation**

### **Unit Testing Structure**
```
🧪 test_setup.py
├── test_imports() → Module loading validation
├── test_data_loading() → CSV processing validation  
├── test_analysis() → Pipeline execution validation
└── main() → Comprehensive test runner
```

### **Error Handling Strategy**
```
1. Import Level: Graceful fallbacks for optional dependencies
2. Data Level: Validation with clear error messages
3. Processing Level: Exception catching with user-friendly output
4. Interface Level: Progressive enhancement with fallbacks
```

### **Validation Checkpoints**
- ✅ Module imports successful
- ✅ Sample data loads without errors
- ✅ Analysis pipeline completes
- ✅ Visualizations generate correctly
- ✅ Streamlit interface renders

---

## 🔄 **Development Workflow**

### **Adding New Analysis Features**
1. **Create function** in appropriate `02_core/` module
2. **Add tests** to `01_setup/test_setup.py`
3. **Update interface** in `03_interface/streamlit_app.py`
4. **Document changes** in `06_docs/`

### **Modifying Data Pipeline**
1. **Update `data_processor.py`** for data changes
2. **Validate with `test_setup.py`**
3. **Test with sample data**
4. **Update documentation**

### **Interface Improvements**
1. **Modify `streamlit_app.py`**
2. **Test with `launch_orpheus.bat`**
3. **Validate all features work**
4. **Update user guides**

---

## 📚 **Documentation Hierarchy**

```
📚 Documentation Structure
├── 🚀 QUICK_START.md → Getting started guide
├── 👤 USER_GUIDE.md → Complete user manual
├── 🔧 TECHNICAL_SUMMARY.md → Architecture details
├── 🔄 PROCESS_FLOWS.md → This document
├── 📊 exportify_data_dictionary.md → Data format reference
└── 📝 README.md → Project overview
```

---

## 🎯 **Performance Considerations**

### **Memory Management**
- DataFrames are cleaned to remove unnecessary columns
- Large datasets processed in chunks where possible
- Session state management for Streamlit efficiency

### **Processing Speed**
- Spotify API requests batched (50 tracks per call)
- Caching of processed results
- Lazy loading of visualizations

### **Scalability**
- Modular design allows easy extension
- Configuration-driven parameters
- Separate concerns (data/analysis/visualization)

---

**This process flow guide ensures you understand exactly how your musical data journeys from raw CSV to emotional insights! 🎵**
