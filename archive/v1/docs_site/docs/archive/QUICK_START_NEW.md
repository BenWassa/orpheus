# 🎵 Project Orpheus - Quick Start Guide

**Clean, organized music analysis - now with numbered folders!**

---

## 🚀 **Super Quick Start**

```powershell
# Navigate to project
cd "c:\Users\benjamin.haddon\Documents\orpheus"

# Run complete analysis
.\orpheus_venv\Scripts\python.exe 01_setup\run_analysis.py

# Launch interactive dashboard  
.\01_setup\launch_dashboard.bat
```

**Dashboard URL**: http://localhost:8501

---

## 📁 **New Clean Structure**

```
📂 Project Orpheus/
├── 01_setup/           # Setup scripts & launchers
│   ├── launch_dashboard.bat    # PowerShell launcher
│   ├── run_analysis.py         # Complete analysis runner
│   └── requirements.txt        # Dependencies
│
├── 02_core/            # Core analysis modules  
│   ├── data_processor.py       # CSV loading & cleaning
│   ├── pattern_analyzer.py     # Pattern detection
│   └── visualizer.py          # Chart generation
│
├── 03_interface/       # Web interface
│   └── streamlit_app.py        # Main dashboard
│
├── 04_data/           # All data files
│   ├── raw/           # Original CSV exports
│   ├── processed/     # Cleaned data
│   └── temp/          # Temporary files
│
├── 05_output/         # Generated results
│   ├── visualizations/        # PNG charts
│   ├── reports/              # Analysis summaries
│   └── exports/              # Downloadable data
│
├── 06_docs/           # Documentation
│   ├── README.md              # Project overview
│   ├── USER_GUIDE.md          # Detailed guide
│   └── TECHNICAL_DOCS.md      # Technical details
│
└── orpheus_venv/      # Python environment
```

---

## ⚡ **Quick Commands**

### **🔍 Check Everything Works**
```powershell
.\orpheus_venv\Scripts\python.exe -c "print('✅ Python OK')"
```

### **📊 Run Full Analysis** 
```powershell
.\orpheus_venv\Scripts\python.exe 01_setup\run_analysis.py
```
**Outputs:**
- Processed data → `05_output/processed_music_data.csv`
- Obsessions → `05_output/musical_obsessions.csv`  
- Charts → `05_output/visualizations/`
- Summary → `05_output/analysis_summary.csv`

### **🌐 Launch Dashboard**
```powershell
.\01_setup\launch_dashboard.bat
```
**Features:**
- Upload new CSV files
- Interactive charts
- Real-time filtering
- Download results

### **📁 Add Your Music Data**
1. **Export** playlists using [Exportify](https://github.com/watsonbox/exportify)
2. **Save** CSV files to `04_data/raw/`
3. **Run** analysis: `python 01_setup\run_analysis.py`

---

## 🎯 **What Each Tool Does**

### **01_setup/run_analysis.py**
- **Finds** all CSV files in `04_data/raw/`
- **Cleans** and combines data
- **Analyzes** patterns and obsessions
- **Creates** visualizations  
- **Saves** everything to `05_output/`

### **03_interface/streamlit_app.py** 
- **Interactive** web dashboard
- **Upload** new files instantly
- **Filter** and explore data
- **Download** results
- **Real-time** analysis

### **01_setup/launch_dashboard.bat**
- **One-click** dashboard launcher
- **Error checking** and troubleshooting
- **Automatic** environment activation
- **Clean** PowerShell interface

---

## 🔧 **Configuration**

### **Change Analysis Settings**
Edit `02_core/pattern_analyzer.py`:
```python
# Modify obsession threshold
def find_obsessions(df, threshold=3):  # Was 5, now 3 for more results
```

### **Customize Visualizations**
Edit `02_core/visualizer.py`:
```python  
# Change number of top artists shown
def create_top_artists(df, top_n=20):  # Was 15, now 20
```

---

## 🆘 **Troubleshooting**

### **"Module not found" errors**
```powershell
# Reinstall dependencies
.\orpheus_venv\Scripts\pip.exe install -r requirements.txt
```

### **Dashboard won't start**
```powershell
# Check if port is busy
netstat -an | findstr :8501

# Use different port
.\orpheus_venv\Scripts\streamlit.exe run 03_interface\streamlit_app.py --server.port 8502
```

### **No CSV files found**
- Ensure files are in `04_data/raw/` directory
- Check files have `.csv` extension  
- Verify Exportify format

### **Corporate Network Issues**
- ✅ Core CSV analysis works offline
- ⚠️ Spotify API features may be blocked
- 💡 Use local analysis only

---

## 🎮 **Sample Usage**

### **Quick Test with Sample Data**
```powershell
# If you have sample data in 04_data/raw/
.\orpheus_venv\Scripts\python.exe 01_setup\run_analysis.py
```

### **Upload Your Own Data**
1. **Go to**: [Exportify](https://github.com/watsonbox/exportify) 
2. **Export** your playlists as CSV
3. **Save** to `04_data/raw/your_playlist.csv`
4. **Run**: `python 01_setup\run_analysis.py`

### **Interactive Exploration**
```powershell
.\01_setup\launch_dashboard.bat
```
Then visit: http://localhost:8501

---

## 📈 **Example Output**

```
🎵 Project Orpheus - Complete Music Analysis
===============================================

📁 Found 2 CSV file(s):
  • my_favorites.csv  
  • workout_playlist.csv

🔄 Processing my_favorites.csv...
  ✅ Processed 847 tracks
  
🔄 Processing workout_playlist.csv...
  ✅ Processed 156 tracks

📊 Total combined dataset: 1,003 tracks

🔥 MUSICAL OBSESSIONS (3+ plays):
  • Taylor Swift (artist): 24 plays (2.4%)
  • Bad Habits (track): 8 plays (0.8%)
  • Olivia Rodrigo (artist): 18 plays (1.8%)

📅 TEMPORAL PATTERNS:
  • Peak month: 2024-03 (67 tracks)
  • Average per month: 28.4 tracks
```

---

## 🚀 **Advanced Features**

### **Batch Processing Multiple Users**
```powershell
# Process multiple people's data
mkdir 04_data\raw\user1
mkdir 04_data\raw\user2
# Add CSV files to each folder, then run analysis
```

### **Custom Analysis Scripts**
```python
# Create custom analysis in 02_core/
from data_processor import load_csv_data, clean_data
from pattern_analyzer import find_obsessions

# Your custom analysis here
```

---

## 🎉 **You're All Set!**

**Your Orpheus project is now clean, organized, and ready for serious music analysis!**

1. **Start** with: `python 01_setup\run_analysis.py`
2. **Explore** with: `.\01_setup\launch_dashboard.bat` 
3. **Add data** to: `04_data\raw\`
4. **Find results** in: `05_output\`

**Happy music exploration! 🎵**
