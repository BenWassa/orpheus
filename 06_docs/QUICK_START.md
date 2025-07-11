# 🎵 Project Orpheus - Quick Start Guide

**Your music emotional analyzer is ready to use with the new organized structure!**

---

## ⚡ **30-Second Start**

```powershell
cd "c:\Users\benjamin.haddon\Documents\orpheus"

# Method 1: Use the quick launcher
.\launch_orpheus.bat

# Method 2: Manual steps
# Test everything works
.\orpheus_venv\Scripts\python.exe 01_setup\test_setup.py

# Launch web dashboard
.\orpheus_venv\Scripts\streamlit.exe run 03_interface\streamlit_app.py
```

---

## 📁 **New Organized Structure**

### **01_setup/** - Installation & Testing
```
📁 01_setup/
├── 📄 test_setup.py           # Health check & validation
├── 📄 run_analysis.py         # Complete analysis runner
├── 📄 requirements.txt        # Python dependencies
├── 📄 .env.template           # Spotify API template
└── 📄 launch_dashboard.bat    # Alternative launcher
```

### **02_core/** - Analysis Engine
```
📁 02_core/
├── 📄 config.py              # Settings & paths
├── 📄 data_processor.py      # CSV loading & cleaning
├── 📄 pattern_analyzer.py    # Listening patterns & obsessions
├── 📄 emotion_analyzer.py    # Sentiment & audio features
└── 📄 visualizer.py          # Charts & graphs
```

### **03_interface/** - Web Dashboard
```
📁 03_interface/
└── 📄 streamlit_app.py       # Interactive web interface
```

### **04_data/** - Your Music Data
```
📁 04_data/
├── 📁 raw/                   # Your Exportify CSV files
│   └── 📄 x_rap_x.csv       # Sample dataset (119 tracks)
└── 📁 processed/             # Cleaned analysis-ready data
    └── 📄 *.parquet         # Processed datasets
```

### **05_output/** - Results
```
📁 05_output/
├── 📁 reports/               # HTML analysis reports
├── 📁 visualizations/        # Charts & graphs (PNG)
└── 📁 exports/              # Data exports
```

### **06_docs/** - Documentation
```
📁 06_docs/
├── 📄 QUICK_START.md         # This guide
├── 📄 USER_GUIDE.md          # Complete user manual
├── 📄 TECHNICAL_SUMMARY.md   # Technical details
└── 📄 exportify_data_dictionary.md # Data format guide
```

---

## 🎯 **What Each Command Does**

### **1. `.\launch_orpheus.bat` - One-Click Launch**
```
✅ Tests all modules automatically
✅ Launches Streamlit dashboard
✅ Opens at http://localhost:8501
✅ Shows any errors clearly
```
**Use when**: Quick start, everyday use

### **2. `01_setup\test_setup.py` - Health Check**
```
✅ Tests all module imports
✅ Loads sample data (119 tracks)  
✅ Validates analysis pipeline
✅ Shows basic statistics
```
**Use when**: First run, troubleshooting, after changes

### **3. `01_setup\run_analysis.py` - Complete Analysis**
```
📊 Processes all CSV files in 04_data/raw/
🔄 Finds repeat obsessions and patterns
🎭 Analyzes emotional content  
📈 Creates visualizations
💾 Saves results to 05_output/
```
**Use when**: Batch processing, generating reports

### **4. `03_interface\streamlit_app.py` - Web Dashboard**
```
🌐 Interactive web interface
📊 Dynamic charts and filters
📁 Upload additional CSV files
💾 Download analysis results
```
**Access at**: http://localhost:8501

---

## 📊 **Your Data**

### **Current Sample Data**
- **File**: `04_data/raw/x_rap_x.csv`
- **Tracks**: 119 songs
- **Artists**: 82 unique artists
- **Status**: ✅ Ready to analyze

### **Add Your Own Data**
1. **Export playlists**: Use [Exportify](https://github.com/watsonbox/exportify)
2. **Save to**: `04_data/raw/your_playlist.csv`
3. **Re-run analysis**: Any command automatically finds new files

---

## 🔧 **Key Features**

### **📊 Analysis Types**
- **Playlist Stats**: Track counts, artists, date ranges
- **Repeat Obsessions**: Songs/artists you play most (configurable threshold)
- **Temporal Patterns**: When you add music over time
- **Emotional Analysis**: Mood patterns and recommendations

### **📈 Visualizations**
- **Timeline charts**: Emotional patterns over time
- **Bar charts**: Top artists and tracks
- **Radar plots**: Audio feature analysis
- **Summary metrics**: Key statistics

### **🌐 Interactive Features**
- **File upload**: Drag & drop CSV files
- **Live analysis**: Real-time pattern detection
- **Adjustable parameters**: Customize thresholds
- **Export results**: Download insights

---

## ⚙️ **Configuration**

### **Basic Settings** (02_core/config.py)
```python
REPEAT_THRESHOLD = 10         # Obsession detection
TOP_N = 10                   # Top results to show
```

### **Spotify API** (Optional - Enhanced Features)
1. **Copy template**: `copy 01_setup\.env.template .env`
2. **Get credentials**: [developer.spotify.com](https://developer.spotify.com/dashboard)
3. **Edit .env**: Add your Client ID and Secret
4. **Re-run analysis**: Get real audio features (valence, energy, etc.)

---

## 🆘 **Troubleshooting**

### **Import Errors**
```powershell
# Re-install dependencies
.\orpheus_venv\Scripts\pip.exe install -r 01_setup\requirements.txt

# Test imports
.\orpheus_venv\Scripts\python.exe 01_setup\test_setup.py
```

### **Streamlit Won't Start**
```powershell
# Try different port
.\orpheus_venv\Scripts\streamlit.exe run 03_interface\streamlit_app.py --server.port 8502

# Check if already running
netstat -an | findstr :8501
```

### **No Data Found**
- Ensure CSV files are in `04_data/raw/` folder
- Verify `.csv` file extension
- Check Exportify format compatibility

### **Empty Analysis Results**
- Verify CSV has track/artist columns
- Check for valid date formats
- Lower obsession threshold in dashboard

---

## 🎯 **Common Workflows**

### **Quick Analysis**
```powershell
# One command does everything
.\launch_orpheus.bat
```

### **Manual Step-by-Step**
```powershell
# 1. Health check
.\orpheus_venv\Scripts\python.exe 01_setup\test_setup.py

# 2. Run analysis
.\orpheus_venv\Scripts\python.exe 01_setup\run_analysis.py

# 3. Launch dashboard
.\orpheus_venv\Scripts\streamlit.exe run 03_interface\streamlit_app.py
```

### **Add New Playlist**
1. Export from Spotify using Exportify
2. Save to `04_data/raw/new_playlist.csv`
3. Refresh dashboard or re-run analysis

### **Custom Analysis**
```python
# Python interactive session
.\orpheus_venv\Scripts\python.exe

import sys
sys.path.append('02_core')
from data_processor import load_exportify, clean
from pattern_analyzer import playlist_stats, repeat_obsessions

# Load your data
df = clean(load_exportify('04_data/raw/your_file.csv'))
stats = playlist_stats(df)
obsessions = repeat_obsessions(df, threshold=3)

print(f"Analyzed {stats['total_tracks']} tracks!")
```

---

## 📚 **Documentation Index**

### **Getting Started**
- **This Guide**: Quick setup and basic usage
- **User Guide**: `06_docs/USER_GUIDE.md` - Complete feature walkthrough
- **Setup Guide**: `06_docs/SETUP_COMPLETE.md` - Installation details

### **Technical Reference**
- **Technical Summary**: `06_docs/TECHNICAL_SUMMARY.md` - Architecture & algorithms
- **Data Dictionary**: `06_docs/exportify_data_dictionary.md` - CSV format guide
- **API Reference**: Code documentation in each module

### **Process Flows**
1. **Data Ingestion**: CSV → `data_processor.py` → Cleaned DataFrame
2. **Pattern Analysis**: DataFrame → `pattern_analyzer.py` → Statistics & Obsessions
3. **Emotion Analysis**: DataFrame → `emotion_analyzer.py` → Sentiment & Audio Features
4. **Visualization**: Results → `visualizer.py` → Charts & Reports
5. **Interface**: All modules → `streamlit_app.py` → Interactive Dashboard

---

## 🚀 **Next Steps**

### **First Time Users**
1. **Test**: `.\orpheus_venv\Scripts\python.exe 01_setup\test_setup.py`
2. **Explore**: `.\launch_orpheus.bat`
3. **Upload**: Add your Exportify CSV files
4. **Analyze**: Discover your musical patterns

### **Power Users**
1. **Setup Spotify API**: Enhanced audio features
2. **Customize**: Modify analysis parameters
3. **Extend**: Add new analysis modules
4. **Export**: Generate reports for sharing

---

## 💡 **Tips for Best Results**

### **Data Quality**
- Use recent Exportify exports (more complete data)
- Include multiple playlists for broader analysis
- Ensure playlists have diverse time ranges

### **Analysis Tuning**
- Adjust obsession thresholds based on library size
- Use date filters for temporal analysis
- Compare different playlists/time periods

### **Performance**
- Large datasets (>1000 tracks) may take time to process
- Spotify API features require internet connection
- Save processed data to avoid re-cleaning

---

**🎉 Your organized musical emotional journey awaits! Start with `.\launch_orpheus.bat` 🎉**
