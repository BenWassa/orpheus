# Output Directory

This directory contains generated outputs from Project Orpheus analysis.

## 📁 **Structure**

```
output/
├── visualizations/     # 📊 Generated charts and plots
├── reports/           # 📋 Analysis summaries (planned)
└── exports/           # 💾 Processed data exports (planned)
```

## 📊 **Generated Visualizations**

When you run `python main.py` or use the visualization functions, charts are automatically saved here:

### **Current Output Files**
- **`emotion_timeline.png`** - Emotional patterns over time
- **`top_artists_bar.png`** - Most played artists chart
- **`audio_features_radar.png`** - Audio feature analysis
- **`listening_patterns_heatmap.png`** - Temporal activity patterns
- **`playlist_overview.png`** - General playlist statistics

### **Chart Types**

**📈 Timeline Charts**
- Emotional valence over time
- Energy levels throughout listening history
- Mood progression visualization

**📊 Bar Charts**
- Top 10 most played artists
- Track frequency analysis
- Genre distribution (when available)

**🎯 Radar Plots**
- Audio feature comparison (valence, energy, danceability, etc.)
- Multi-dimensional music preference mapping
- Emotional profile visualization

**🔥 Heatmaps**
- Listening activity by time period
- Monthly/weekly patterns
- Peak listening periods

## 🎨 **File Formats**

### **Image Formats**
- **PNG**: High-quality charts for sharing
- **SVG**: Vector graphics for scaling (planned)
- **PDF**: Print-ready visualizations (planned)

### **Resolution & Quality**
- **Default**: 300 DPI for clear printing
- **Web optimized**: Smaller file sizes for sharing
- **Customizable**: Modify in `src/visualization.py`

## 🔄 **How Files Are Generated**

### **Automatic Generation**
```powershell
# Run complete analysis - generates all visualizations
.\orpheus_venv\Scripts\python.exe main.py
```

### **Manual Generation**
```python
from src.visualization import save_all_visualizations
from src.config import PROJECT_ROOT

output_dir = PROJECT_ROOT / "output" / "visualizations"
save_all_visualizations(df, output_dir)
```

### **Individual Charts**
```python
from src.visualization import plot_emotion_timeline, plot_top_artists

# Create specific visualizations
fig1 = plot_emotion_timeline(df, save_path="output/visualizations/timeline.png")
fig2 = plot_top_artists(df, save_path="output/visualizations/artists.png")
```

## 📋 **Reports (Planned)**

### **Future Report Types**
- **HTML Summary**: Interactive analysis report
- **PDF Report**: Printable insights summary  
- **JSON Export**: Machine-readable analysis results
- **CSV Summary**: Tabular insights for spreadsheet import

### **Report Content**
- Analysis parameters used
- Key insights and recommendations
- Statistical summaries
- Embedded visualizations
- Timestamp and data source info

## 💾 **Exports (Planned)**

### **Data Export Formats**
- **Processed CSV**: Cleaned data with analysis columns
- **JSON**: Complete analysis results
- **Parquet**: Efficient binary format for large datasets
- **Excel**: Spreadsheet-friendly format

### **Export Content**
- Original data with cleaning applied
- Added audio features (from Spotify API)
- Sentiment analysis results
- Pattern detection results
- Obsession analysis outcomes

## 🛠️ **Customization**

### **Modify Chart Appearance**
Edit `src/visualization.py`:
```python
# Change color schemes
plt.style.use('seaborn-darkgrid')  # Or other styles

# Modify figure sizes
fig, ax = plt.subplots(figsize=(15, 10))  # Larger charts

# Custom color palettes
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Custom colors
```

### **Add Custom Visualizations**
```python
def plot_custom_analysis(df, save_path=None):
    """Create your own visualization"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Your custom plotting logic here
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    return fig
```

### **Output Directory Management**
```python
# Organize outputs by date
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_subdir = f"output/visualizations/{timestamp}"
```

## 📊 **Chart Interpretation**

### **Reading the Visualizations**

**Emotion Timeline**
- X-axis: Time (when tracks were added)
- Y-axis: Emotional metrics (valence, energy)
- Trends: Rising lines = more positive/energetic music

**Top Artists Bar Chart**
- X-axis: Artist names
- Y-axis: Track count
- Height: How many tracks by each artist

**Audio Features Radar**
- Multiple axes: Different audio features
- Distance from center: Feature intensity
- Shape: Your music preference profile

**Listening Heatmap**
- X-axis: Time periods (months/weeks)
- Y-axis: Activity level
- Color intensity: Amount of music added

## 🔄 **File Management**

### **Automatic Cleanup**
- Old files are overwritten by default
- Manual backup if you want to preserve previous analyses

### **Version Control**
- Outputs are gitignored by default (personal data)
- Enable versioning by modifying `.gitignore` if desired

### **Storage Space**
- Typical chart files: 100KB - 2MB each
- Full analysis output: < 10MB typically
- Monitor space if analyzing very large libraries

---

**📊 All your musical insights, beautifully visualized and ready to explore! 📊**
