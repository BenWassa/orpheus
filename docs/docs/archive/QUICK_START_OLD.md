# 🎵 Project Orpheus - Quick Start Reference

**Your music emotional analyzer is ready to use!**

---

## ⚡ **30-Second Start**

```powershell
cd "c:\Users\benjamin.haddon\Documents\orpheus"

# Test everything works
.\orpheus_venv\Scripts\python.exe test_setup.py

# Analyze your music  
.\orpheus_venv\Scripts\python.exe main.py

# Launch web dashboard
cd "c:\Users\benjamin.haddon\Documents\orpheus"
.\orpheus_venv\Scripts\streamlit.exe run ui/app.py

# OR use the launcher script
.\launch_streamlit.bat
```

---

## 🎯 **What Each Command Does**

### **1. `test_setup.py` - Health Check**
```
✅ Tests all module imports
✅ Loads sample data (119 tracks)  
✅ Validates analysis pipeline
✅ Shows basic statistics
```
**Use when**: First run, troubleshooting, after changes

### **2. `main.py` - Complete Analysis**
```
📊 Processes all CSV files in data/raw/
🔄 Finds repeat obsessions and patterns
🎭 Analyzes emotional content  
📈 Creates visualizations
💾 Saves results to output/
```
**Use when**: Analyzing your music data

### **3. `streamlit run ui/app.py` - Web Dashboard**
```
🌐 Interactive web interface
📊 Dynamic charts and filters
📁 Upload additional CSV files
💾 Download analysis results
```
**Access at**: http://localhost:8501

---

## 📁 **Your Data**

### **Current Sample Data**
- **File**: `data/raw/x_rap_x.csv`
- **Tracks**: 119 songs
- **Artists**: 82 unique artists
- **Status**: ✅ Ready to analyze

### **Add Your Own Data**
1. **Export playlists**: Use [Exportify](https://github.com/watsonbox/exportify)
2. **Save to**: `data/raw/your_playlist.csv`
3. **Re-run analysis**: Any command automatically finds new files

---

## 🔧 **Key Features**

### **📊 Analysis Types**
- **Playlist Stats**: Track counts, artists, date ranges
- **Repeat Obsessions**: Songs/artists you play most
- **Temporal Patterns**: When you add music over time
- **Emotional Analysis**: Mood patterns and recommendations

### **📈 Visualizations**
- **Timeline charts**: Emotional patterns over time
- **Bar charts**: Top artists and tracks
- **Radar plots**: Audio feature analysis
- **Heatmaps**: Listening activity patterns

### **🌐 Interactive Features**
- **Filter by date range**
- **Search artists/tracks**
- **Adjust analysis parameters**
- **Export results**

---

## ⚙️ **Configuration**

### **Basic Settings** (src/config.py)
```python
DEFAULT_REPEAT_THRESHOLD = 10  # Obsession detection
DEFAULT_TOP_N = 10            # Top results to show
```

### **Spotify API** (Optional)
1. **Copy template**: `copy .env.template .env`
2. **Get credentials**: [developer.spotify.com](https://developer.spotify.com/dashboard)
3. **Edit .env**: Add your Client ID and Secret
4. **Re-run analysis**: Get real audio features (valence, energy, etc.)

---

## 🆘 **Quick Troubleshooting**

### **"No module named 'src'"**
```powershell
# Make sure you're in the project directory
cd "c:\Users\benjamin.haddon\Documents\orpheus"

# Then run streamlit
.\orpheus_venv\Scripts\streamlit.exe run ui/app.py

# Or use the launcher
.\launch_streamlit.bat
```

### **"No module named pandas"**
```powershell
.\orpheus_venv\Scripts\activate
pip install -r requirements.txt
```

### **"No CSV files found"**
- Check files are in `data/raw/` folder
- Ensure `.csv` file extension
- Verify Exportify format

### **Streamlit won't start**
```powershell
# Try different port
.\orpheus_venv\Scripts\streamlit.exe run ui/app.py --server.port 8502
```

### **Empty results**
- Verify CSV has track/artist data
- Check date formats
- Lower obsession threshold in config

---

## 📚 **Full Documentation**

- **Complete Guide**: `USER_GUIDE.md`
- **Setup Details**: `SETUP_COMPLETE.md`  
- **Technical Info**: `docs/TECHNICAL_SUMMARY.md`
- **Data Format**: `docs/exportify_data_dictionary.md`
- **What's New**: `CHANGELOG.md`

---

## 🎯 **Common Use Cases**

### **Analyze Current Data**
```powershell
.\orpheus_venv\Scripts\python.exe main.py
```

### **Interactive Exploration**
```powershell
.\orpheus_venv\Scripts\streamlit.exe run ui/app.py
```

### **Add New Playlist**
1. Export from Spotify using Exportify
2. Save to `data/raw/new_playlist.csv`
3. Run `python main.py`

### **Compare Playlists**
1. Add multiple CSV files to `data/raw/`
2. Use web dashboard to switch between files
3. Compare statistics and patterns

### **Custom Analysis**
```python
# Python interactive session
.\orpheus_venv\Scripts\python.exe

import sys; sys.path.append('src')
from src.pattern_analysis import repeat_obsessions
from src.data_processing import load_exportify, clean
from src.config import DATA_DIR_RAW

df = clean(load_exportify(list(DATA_DIR_RAW.glob('*.csv'))[0]))
obsessions = repeat_obsessions(df, threshold=3)
print(f"Found {len(obsessions)} obsessions!")
```

---

## 🚀 **Next Steps**

1. **Run test**: Verify everything works
2. **Analyze sample**: See what insights emerge
3. **Add your data**: Export your playlists
4. **Explore dashboard**: Interactive analysis
5. **Setup Spotify API**: Get real audio features
6. **Customize**: Modify thresholds and add features

---

**🎉 Your musical emotional journey awaits! Start with `python test_setup.py` 🎉**
