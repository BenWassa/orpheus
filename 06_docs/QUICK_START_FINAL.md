# 🎵 Project Orpheus - Complete Quick Start Guide

**Clean, organized music analysis with numbered folders - Corporate network friendly!**

---

## 🚀 **Super Quick Start (30 seconds)**

```powershell
# Navigate to project
cd "c:\Users\benjamin.haddon\Documents\orpheus"

# Test everything works
.\orpheus_venv\Scripts\python.exe 01_setup\test_setup.py

# Launch dashboard
.\launch_orpheus.bat
```

**Dashboard opens at**: http://localhost:8501

---

## 📁 **New Clean Structure (Post-Cleanup)**

```
📂 Project Orpheus/
├── 📁 01_setup/           # ⚙️ Setup & Launch Scripts
│   ├── 📄 test_setup.py           # Health check & validation
│   ├── 📄 run_analysis.py         # Complete analysis runner
│   ├── 📄 test_imports.py         # Import testing
│   ├── 📄 launch_dashboard.bat    # Streamlit launcher (old ui path)
│   ├── 📄 launch_dashboard_simple.bat # Simple launcher
│   └── 📄 requirements.txt        # All dependencies
│
├── 📁 02_core/            # 🧠 Core Analysis Engine
│   ├── 📄 config.py               # Settings & paths
│   ├── 📄 data_processor.py       # CSV loading & cleaning
│   ├── 📄 pattern_analyzer.py     # Pattern detection
│   ├── 📄 emotion_analyzer.py     # Mood & sentiment analysis
│   └── 📄 visualizer.py          # Chart generation
│
├── 📁 03_interface/       # 🌐 Web Interface
│   └── 📄 streamlit_app.py        # Main dashboard
│
├── 📁 04_data/           # 📊 All Data Files
│   ├── 📁 raw/           # Original CSV exports
│   │   └── 📄 x_rap_x.csv         # Sample data (119 tracks)
│   ├── 📁 processed/     # Cleaned datasets
│   │   └── 📄 x_rap_x_processed.parquet # Fast loading format
│   └── 📁 temp/          # Temporary processing files
│
├── 📁 05_output/         # 📈 Generated Results
│   ├── 📁 visualizations/        # PNG charts & plots
│   ├── 📁 reports/              # HTML analysis reports
│   └── 📁 exports/              # Downloadable CSV files
│
├── 📁 06_docs/           # 📚 Documentation Hub
│   ├── 📄 QUICK_START_NEW.md     # This guide (updated)
│   ├── 📄 USER_GUIDE.md          # Complete user manual
│   ├── 📄 TECHNICAL_SUMMARY.md   # Technical architecture
│   ├── 📄 CHANGELOG.md           # Version history
│   ├── 📄 README_ORIGINAL.md     # Original README (preserved)
│   └── 📄 exportify_data_dictionary.md # Data format reference
│
├── 📁 orpheus_venv/      # 🐍 Python Environment
│   └── 📄 Scripts/streamlit.exe   # Streamlit executable
│
├── 📄 launch_orpheus.bat         # 🚀 Main launcher (NEW)
├── 📄 README.md                  # Clean project overview
└── 📄 __init__.py               # Python package marker
```

---

## ⚡ **Command Reference**

### **🔍 Health Check (Always run first)**
```powershell
.\orpheus_venv\Scripts\python.exe 01_setup\test_setup.py
```
**What it does:**
- ✅ Tests all module imports
- ✅ Loads sample data (119 tracks)
- ✅ Validates analysis pipeline
- ✅ Shows basic statistics

### **🚀 Main Launcher (Recommended)**
```powershell
.\launch_orpheus.bat
```
**What it does:**
- 🔧 Runs health check automatically
- 🌐 Launches Streamlit dashboard
- 📊 Opens web interface at localhost:8501
- ⚠️ Shows clear error messages if issues

### **📊 Manual Analysis (CLI)**
```powershell
.\orpheus_venv\Scripts\python.exe 01_setup\run_analysis.py
```
**Outputs:**
- 📄 Processed data → `05_output/`
- 📈 Charts → `05_output/visualizations/`
- 📋 Reports → `05_output/reports/`

### **🌐 Manual Dashboard Launch**
```powershell
.\orpheus_venv\Scripts\streamlit.exe run 03_interface\streamlit_app.py
```

---

## 🎯 **How to Use Your Music Data**

### **📁 Add Your Playlists**
1. **Export** from Spotify using [Exportify](https://github.com/watsonbox/exportify)
2. **Save** CSV files to `04_data/raw/`
3. **Upload** via dashboard or run analysis directly

### **💡 Corporate Network Friendly**
- ✅ **Works completely offline** 
- ✅ **No external API calls required**
- ✅ **All processing local**
- ✅ **Spotify API optional** for enhanced features

---

## 🔧 **Updated Features**

### **🌐 Streamlit Dashboard**
- **📊 Interactive charts** with filtering
- **📁 Drag & drop file upload**
- **🎵 Sample data exploration**
- **💾 Download analysis results**
- **📈 Real-time processing**

### **📊 Analysis Types**
- **🔥 Obsession Detection**: Most played artists/tracks
- **📅 Temporal Patterns**: Music discovery timeline
- **🎭 Emotional Analysis**: Mood trends and insights
- **📈 Statistics**: Comprehensive playlist metrics

### **📈 Visualizations**
- **📊 Timeline charts**: Listening patterns over time
- **📊 Bar charts**: Top artists and tracks
- **🌐 Radar plots**: Audio feature analysis
- **📊 Summary stats**: Key metrics and insights

---

## 🆘 **Troubleshooting**

### **❌ "Could not import core modules"**
```powershell
# Check virtual environment
.\orpheus_venv\Scripts\python.exe -c "print('✅ Python OK')"

# Reinstall dependencies if needed
.\orpheus_venv\Scripts\pip.exe install -r 01_setup\requirements.txt
```

### **❌ "No CSV files found"**
- Check files are in `04_data/raw/` (not old `data/raw/`)
- Ensure `.csv` file extension
- Verify Exportify format using data dictionary

### **❌ Streamlit connection error**
```powershell
# Try different port
.\orpheus_venv\Scripts\streamlit.exe run 03_interface\streamlit_app.py --server.port 8502
```

### **❌ Import path errors**
- Always run from project root: `c:\Users\benjamin.haddon\Documents\orpheus`
- Check working directory: `echo %CD%`

---

## 📚 **Documentation Index**

| **Guide** | **Purpose** | **When to Use** |
|-----------|-------------|-----------------|
| **This Guide** | Quick start & commands | First time setup, daily use |
| **USER_GUIDE.md** | Complete manual | Understanding all features |
| **TECHNICAL_SUMMARY.md** | Architecture details | Development, customization |
| **CHANGELOG.md** | Version history | What's new, troubleshooting |
| **exportify_data_dictionary.md** | Data format reference | CSV upload issues |

---

## 🎯 **What's New in This Structure**

### **✅ Improvements**
- ✅ **Numbered folders** for clear organization
- ✅ **Consolidated documentation** in `06_docs/`
- ✅ **Centralized data** in `04_data/`
- ✅ **Clean module structure** in `02_core/`
- ✅ **Simple launch script** (`launch_orpheus.bat`)
- ✅ **Updated import paths** throughout
- ✅ **Removed duplicates** and cleanup files

### **🗑️ Removed**
- ❌ Old `src/`, `ui/`, `data/`, `docs/`, `output/` folders
- ❌ Duplicate virtual environments
- ❌ Cleanup scripts (no longer needed)
- ❌ Broken import statements

---

## 🎉 **Ready to Go!**

Your Project Orpheus is now **fully organized**, **thoroughly tested**, and **comprehensively documented**. 

**Start exploring your musical soul:**
```powershell
.\launch_orpheus.bat
```

🎵 **Happy analyzing!** 🎵
