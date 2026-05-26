# Project Orpheus

**Decode your emotional underworld through the music that moves you.**

---

## 📜 Vision

Project Orpheus is an introspective exploration of the self through music. By ---

## 📁 Project Structure

```
orpheus/                    # 🎵 FULLY OPERATIONAL 🎵
├── data/
│   ├── raw/               # ✅ Your CSV exports (x_rap_x.csv: 119 tracks)
│   └── processed/         # ✅ Analysis outputs (auto-generated)
├── src/                   # ✅ Core analysis modules
│   ├── config.py         # Settings, paths, API config
│   ├── data_processing.py# CSV loading and cleaning
│   ├── pattern_analysis.py# Pattern detection algorithms  
│   ├── emotion_analysis.py# Sentiment and mood analysis
│   └── visualization.py  # Charts and plotting
├── ui/
│   └── app.py            # ✅ Streamlit web dashboard
├── orpheus_venv/         # ✅ Python virtual environment
├── main.py              # ✅ Complete analysis pipeline
├── test_setup.py        # ✅ Validation and testing
├── requirements.txt     # ✅ All dependencies
├── .env.template        # Spotify API template
└── SETUP_COMPLETE.md    # Detailed setup guide
```

**Ready-to-use components:**
- ✅ **119 sample tracks** analyzed and ready
- ✅ **Complete analysis pipeline** working
- ✅ **Web dashboard** functional
- ✅ **All dependencies** installed
- ✅ **Documentation** comprehensive

---

## 🆘 Troubleshooting

### **Common Issues**

**Import Errors:**
```powershell
# Ensure virtual environment is active
.\orpheus_venv\Scripts\activate
# Re-install if needed
pip install -r requirements.txt
```

**Streamlit Won't Start:**
```powershell
# Try different port
.\orpheus_venv\Scripts\streamlit.exe run ui/app.py --server.port 8502
```

**No Data Found:**
- Check CSV files are in `data/raw/`
- Verify CSV format matches Exportify schema
- See `docs/exportify_data_dictionary.md`

### **Getting Help**
- 📖 **Full setup guide**: `SETUP_COMPLETE.md`
- 🔧 **Technical details**: `docs/TECHNICAL_SUMMARY.md`
- 📊 **Data format**: `docs/exportify_data_dictionary.md`
- 🧪 **Test validation**: Run `test_setup.py` listening patterns — recurring obsessions, sudden fixations, shifting phases — it maps the hidden emotional currents shaping your inner life. Inspired by the myth of Orpheus, who descended into darkness guided by song, this project transforms your listening history into a lantern for self-discovery.

---

## 🎻 Core Idea

- **Reveal Emotional Patterns:** Discover recurring moods, fixations, and subconscious themes.
- **Trace Life Narratives:** Connect musical phases to pivotal life events and hidden transitions.
- **Deepen Self-Awareness:** Use your own music history as a profound tool for reflection and growth.

---

## 🔍 How It Works

1. **Collect:** Gather listening data (e.g., streaming history, playlists).
2. **Analyze:** Detect repeat patterns, emotional spikes, sudden obsessions.
3. **Map:** Visualize musical phases as an emotional timeline.
4. **Reflect:** Interpret patterns through mythic symbolism and guided prompts.

---

## ⚙️ Project Structure

```
orpheus/
├── data/                    # All data files
│   ├── raw/                # Original exports (Exportify CSV, etc.)
│   └── processed/          # Cleaned data ready for analysis
├── src/                    # Core Python modules
├── notebooks/              # Jupyter notebooks for analysis
├── docs/                   # Documentation and references
├── output/                 # Generated visualizations and reports
│   ├── visualizations/     # Charts and timelines
│   ├── reports/           # Analysis summaries
│   └── exports/           # Processed data exports
└── README.md              # This file
```

**Current Data:**
- Sample playlist: `x_rap_x` (37 tracks, hip-hop/rap focus)
- Timeframe: Various releases from 2013-2022, added January 2025
- Data source: Spotify via Exportify tool

**Pilot Phase:**
- Small dataset testing with single playlist
- Method refinement and insight validation
- Foundation for larger listening history analysis

---

## 🌙 Metaphor

Just as Orpheus journeyed into the underworld with music as his guide, Project Orpheus helps you descend into your emotional depths — not to dwell in darkness, but to retrieve hidden truths, lost memories, and fresh self-understanding.

---

## � Getting Started

### Prerequisites
- Python 3.8+
- Jupyter Lab or Jupyter Notebook
- Music streaming data (Spotify export recommended)

### Data Collection
1. **Spotify Data**: Use [Exportify](https://github.com/watsonbox/exportify) to export playlists as CSV
2. **Place raw data** in `data/raw/` directory
3. **Reference** `docs/exportify_data_dictionary.md` for column definitions

---

## 🚀 Usage Walkthrough

### **Quick Start (2 minutes)**
```powershell
cd "c:\Users\benjamin.haddon\Documents\orpheus"

# 1. Test everything works
.\orpheus_venv\Scripts\python.exe test_setup.py

# 2. Run complete analysis
.\orpheus_venv\Scripts\python.exe main.py

# 3. Launch web dashboard
.\orpheus_venv\Scripts\streamlit.exe run ui/app.py
```

### **1. 🧪 Validation Test**
Run this first to ensure everything is working:
```powershell
.\orpheus_venv\Scripts\python.exe test_setup.py
```
**What it does:**
- ✅ Tests all module imports
- ✅ Loads and cleans your sample data (119 tracks)
- ✅ Runs basic analysis functions
- ✅ Shows: unique tracks (119), unique artists (82)

### **2. 📊 Complete Analysis Pipeline**
```powershell
.\orpheus_venv\Scripts\python.exe main.py
```
**What you get:**
- 📈 **Playlist Statistics**: Track counts, date ranges, popularity
- 🔄 **Repeat Obsessions**: Artists/tracks you play most
- 📅 **Temporal Patterns**: When you added music over time
- 🎭 **Emotional Analysis**: Mood patterns and recommendations
- 📊 **Visualizations**: Charts saved to `output/visualizations/`

### **3. 🌐 Interactive Web Dashboard**
```powershell
.\orpheus_venv\Scripts\streamlit.exe run ui/app.py
```
**Opens at: http://localhost:8501**
- 🎵 **Upload/Select** different CSV files
- 📊 **Interactive charts** for all analysis types
- 🔍 **Filter and explore** your data dynamically
- 💾 **Download** processed results

### **4. 📁 Add Your Own Music Data**
1. **Export playlists** using [Exportify](https://github.com/watsonbox/exportify)
2. **Save CSV files** in `data/raw/` directory
3. **Re-run any analysis** - automatically processes all CSV files

### **5. ⚙️ Advanced Features**

**Spotify API Integration:**
```powershell
# Copy template and add your credentials
copy .env.template .env
# Edit .env file with your Spotify Client ID/Secret
# Re-run analysis for real audio features (valence, energy, etc.)
```

**Custom Analysis:**
- **Modify thresholds**: Edit `src/config.py`
- **Add visualizations**: Extend `src/visualization.py`
- **Custom patterns**: Modify `src/pattern_analysis.py`

---

## 📈 What You Can Analyze

### **📊 Listening Patterns**
- Most played artists, albums, tracks
- Listening activity over time
- Peak periods and quiet phases
- Musical diversity measurements

### **🔄 Repeat Obsessions**
- Artists/tracks played repeatedly (configurable threshold)
- Obsession intensity analysis
- Timeline of musical fixations
- Genre obsession patterns

### **🎭 Emotional Analysis**
- Audio feature analysis (valence, energy, danceability)
- Sentiment patterns from track/artist names
- Mood recommendations based on listening patterns
- Emotional timeline visualization

### **📅 Temporal Patterns**
- Monthly/weekly listening distribution
- Music discovery phases
- Listening streak detection
- Activity pattern correlation

---

## ✅ **FULLY OPERATIONAL STATUS**

**Environment Setup:**  
- ✅ Python virtual environment (`orpheus_venv`)
- ✅ All dependencies installed (pandas, streamlit, spotipy, etc.)
- ✅ Sample data loaded (119 tracks, 82 artists)
- ✅ All modules tested and working

**Analysis Pipeline:**  
- ✅ Data processing (load, clean, validate)
- ✅ Pattern analysis (stats, obsessions, temporal)
- ✅ Emotion analysis (sentiment, audio features)
- ✅ Visualization (charts, timelines, dashboards)

**Ready for:**
- 🎯 **Immediate analysis** of sample data
- 🎯 **Your own music exports** 
- 🎯 **Advanced Spotify API features**
- 🎯 **Custom analysis and extensions**

---

## �🚧 Status

**Currently:**  
- [x] Repository initialized  
- [x] Project structure organized
- [x] Sample data collected (x_rap_x playlist)
- [x] Data dictionary documented  
- [ ] Local environment setup  
- [ ] Core modules scoped  
- [ ] Pilot data analysis pending  
- [ ] Initial mapping tool in design

**Recent Progress:**
- ✅ Organized file structure with dedicated directories
- ✅ Added sample Spotify playlist data (37 tracks)
- ✅ Created comprehensive data dictionary for Exportify CSV format

## 📚 Documentation

### **📖 Complete Guide Library**
- **`QUICK_START.md`** - 30-second start guide and command reference
- **`USER_GUIDE.md`** - Complete user manual with detailed walkthroughs  
- **`SETUP_COMPLETE.md`** - Installation guide and troubleshooting
- **`DOCUMENTATION_INDEX.md`** - Navigate all documentation
- **`CHANGELOG.md`** - Version history and what's new

### **🔧 Technical References**
- **`docs/TECHNICAL_SUMMARY.md`** - Architecture and system design
- **`docs/exportify_data_dictionary.md`** - Data format specifications
- **`src/README.md`** - Code modules and development guide

### **📁 Directory Guides**
- **`data/README.md`** - Data organization and management
- **`output/README.md`** - Generated files and visualizations
- **`notebooks/README.md`** - Interactive analysis (planned)

---

## 🤝 Contributing

For now, this is a personal exploration. In the future, collaboration may open for those interested in blending **music**, **myth**, and **introspective tech**.

---

## 📚 License

This project is released under the **MIT License** — see `LICENSE` for details.

---

**May your music lead you inward, and your insights bring you home.**
