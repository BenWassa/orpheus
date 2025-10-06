# 🎵 Project Orpheus - Setup Guide

## ✅ **Ready to Run Checklist**

Your Project Orpheus installation is now complete! Here's what you can do:

### **1. 🧪 Test the Setup**
```powershell
# Navigate to project directory
cd "c:\Users\benjamin.haddon\Documents\orpheus"

# Test basic functionality
.\orpheus_venv\Scripts\python.exe test_setup.py
```

### **2. 🏃‍♂️ Run Complete Analysis**
```powershell
# Run the full analysis pipeline on your sample data
.\orpheus_venv\Scripts\python.exe main.py
```

### **3. 🌐 Launch Web Dashboard**
```powershell
# Start the Streamlit web interface
.\orpheus_venv\Scripts\streamlit.exe run ui/app.py
```
*The dashboard will open in your browser at: http://localhost:8501*

### **4. 📊 Add Your Own Music Data**

1. **Export your Spotify playlists** using [Exportify](https://github.com/watsonbox/exportify)
2. **Save CSV files** in `data/raw/` directory
3. **Re-run the analysis** with `python main.py`

---

## 🔧 **What's Been Set Up**

### **Project Structure**
```
orpheus/
├── data/
│   ├── raw/                # ✅ Your Exportify CSV files
│   │   └── x_rap_x.csv    # ✅ Sample data (119 tracks)
│   └── processed/          # ✅ Processed analysis results
├── src/                    # ✅ Core Python modules
│   ├── config.py          # ✅ Configuration and paths
│   ├── data_processing.py # ✅ CSV loading and cleaning
│   ├── pattern_analysis.py# ✅ Playlist statistics
│   ├── emotion_analysis.py# ✅ Mood and sentiment analysis
│   └── visualization.py   # ✅ Charts and plots
├── ui/
│   └── app.py             # ✅ Streamlit web dashboard
├── orpheus_venv/          # ✅ Python virtual environment
├── requirements.txt       # ✅ Package dependencies
├── .gitignore            # ✅ Version control settings
└── main.py               # ✅ Complete analysis pipeline
```

### **Installed Packages**
- ✅ **pandas, numpy** - Data processing
- ✅ **matplotlib, seaborn, plotly** - Visualizations
- ✅ **streamlit** - Web dashboard
- ✅ **spotipy** - Spotify API integration
- ✅ **textblob, nrclex** - Text sentiment analysis
- ✅ **pyarrow** - Fast data storage
- ✅ **python-dotenv** - Environment variables

### **Sample Data Analyzed**
- ✅ **119 tracks** from `x_rap_x.csv`
- ✅ **82 unique artists**
- ✅ **Data cleaning** completed successfully
- ✅ **Pattern analysis** ready to run

---

## 🚀 **Next Steps**

### **Basic Usage**
1. **Analyze your current data**: `python main.py`
2. **View results in browser**: `streamlit run ui/app.py`
3. **Add more playlists**: Drop CSV files in `data/raw/`

### **Advanced Features**
1. **Spotify API Setup** (optional):
   - Copy `.env.template` to `.env`
   - Add your Spotify API credentials
   - Get real audio features (valence, energy, etc.)

2. **Custom Analysis**:
   - Modify thresholds in `src/config.py`
   - Add custom visualizations in `src/visualization.py`
   - Extend pattern detection in `src/pattern_analysis.py`

### **Data Collection**
1. **Export more playlists** from Spotify using Exportify
2. **Add Apple Music** or other streaming service exports
3. **Manual tagging** of emotional events or life periods

---

## 🆘 **Troubleshooting**

### **If you see import errors:**
```powershell
# Ensure virtual environment is activated
.\orpheus_venv\Scripts\activate
# Re-install packages if needed
pip install -r requirements.txt
```

### **If Streamlit won't start:**
```powershell
# Check if port 8501 is available
netstat -an | findstr :8501
# Try a different port
streamlit run ui/app.py --server.port 8502
```

### **If data loading fails:**
- Check that CSV files are in `data/raw/`
- Verify CSV format matches Exportify schema
- Check file permissions and encoding

---

## 📞 **Support**

- **Documentation**: Check `docs/` directory
- **Technical details**: See `docs/TECHNICAL_SUMMARY.md`
- **Data format**: See `docs/exportify_data_dictionary.md`

---

**🎉 Congratulations! Project Orpheus is now ready to reveal the emotional patterns hidden in your music! 🎉**
