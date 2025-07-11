# 🎵 Project Orpheus - Complete User Guide

**Transform your music listening data into emotional insights and patterns**

---

## 🚀 Quick Start Guide

### **Step 1: Verify Installation**
```powershell
cd "c:\Users\benjamin.haddon\Documents\orpheus"
.\orpheus_venv\Scripts\python.exe test_setup.py
```
**Expected Output:**
```
🧪 Testing module imports...
✅ Config module loaded
✅ Data processing module loaded
✅ Pattern analysis module loaded
✅ Emotion analysis module loaded
✅ Visualization module loaded

📊 Testing data loading...
📁 Found 1 CSV file(s)
🔄 Loading: x_rap_x.csv
📈 Loaded 119 rows, 19 columns
🧹 Cleaned data: 119 rows remaining
🎵 Unique tracks: 119
🎤 Unique artists: 82

✅ Tests passed: 2/3 (or 3/3)
🎉 All tests passed! Orpheus is ready to analyze your music!
```

### **Step 2: Run Complete Analysis**
```powershell
.\orpheus_venv\Scripts\python.exe main.py
```
**What Happens:**
1. **Data Loading**: Finds all CSV files in `data/raw/`
2. **Data Cleaning**: Removes duplicates, validates format
3. **Pattern Analysis**: Computes statistics and obsessions
4. **Emotion Analysis**: Analyzes sentiment and audio features
5. **Visualization**: Creates charts saved to `output/visualizations/`
6. **Summary Report**: Prints comprehensive analysis to terminal

### **Step 3: Launch Web Dashboard**
```powershell
.\orpheus_venv\Scripts\streamlit.exe run ui/app.py
```
**Access at:** http://localhost:8501
- Interactive charts and filters
- Upload additional CSV files
- Download analysis results

---

## 📊 Analysis Walkthrough

### **1. Data Processing Module**

**What it does:**
- Loads Exportify CSV files
- Cleans and validates data
- Handles missing/malformed entries
- Standardizes column names

**Manual Usage:**
```python
from src.data_processing import load_exportify, clean
from src.config import DATA_DIR_RAW

# Load a specific CSV
csv_file = DATA_DIR_RAW / "your_playlist.csv"
df_raw = load_exportify(csv_file)
df_clean = clean(df_raw)

print(f"Loaded {len(df_clean)} tracks")
```

**Output Information:**
- Total tracks loaded
- Duplicates removed
- Data quality issues found
- Final dataset size

### **2. Pattern Analysis Module**

**Available Functions:**

**a) Playlist Statistics**
```python
from src.pattern_analysis import playlist_stats

stats = playlist_stats(df_clean)
print(f"Total tracks: {stats['total_tracks']}")
print(f"Unique artists: {stats['unique_artists']}")
print(f"Date range: {stats['date_range']['span_days']} days")
```

**b) Repeat Obsessions**
```python
from src.pattern_analysis import repeat_obsessions

# Find artists/tracks played 5+ times
obsessions = repeat_obsessions(df_clean, threshold=5)
print(f"Found {len(obsessions)} obsessions")
print(obsessions[['item', 'count', 'type', 'intensity']])
```

**c) Temporal Patterns**
```python
from src.pattern_analysis import temporal_patterns

patterns = temporal_patterns(df_clean)
print("Monthly distribution:", patterns['monthly_distribution'])
print("Peak period:", patterns['peak_periods'])
```

### **3. Emotion Analysis Module**

**Audio Features (requires Spotify API):**
```python
from src.emotion_analysis import add_spotify_audio_features

# Add valence, energy, danceability, etc.
df_with_features = add_spotify_audio_features(df_clean)
print("Audio features added:", df_with_features['valence'].notna().sum())
```

**Sentiment Analysis:**
```python
from src.emotion_analysis import add_lyric_sentiment, compute_emotion_summary

# Add sentiment columns
df_with_sentiment = add_lyric_sentiment(df_clean)

# Generate emotional summary
summary = compute_emotion_summary(df_with_sentiment)
print("Recommendations:")
for rec in summary['recommendations']:
    print(f"  - {rec}")
```

### **4. Visualization Module**

**Create Charts:**
```python
from src.visualization import plot_emotion_timeline, save_all_visualizations
from src.config import PROJECT_ROOT

# Create all visualizations
output_dir = PROJECT_ROOT / "output" / "visualizations"
save_all_visualizations(df_clean, output_dir)
```

**Generated Files:**
- `emotion_timeline.png` - Emotional patterns over time
- `top_artists_bar.png` - Most played artists
- `audio_features_radar.png` - Audio feature analysis
- `listening_patterns_heatmap.png` - Temporal activity map

---

## 🌐 Web Dashboard Guide

### **Starting the Dashboard**
```powershell
.\orpheus_venv\Scripts\streamlit.exe run ui/app.py
```

### **Dashboard Features**

**1. File Upload**
- Upload additional CSV files
- Process multiple playlists simultaneously
- Real-time analysis updates

**2. Interactive Charts**
- Filter by date range
- Select specific artists/tracks
- Zoom and pan on timelines

**3. Analysis Sections**
- **Overview**: Summary statistics
- **Patterns**: Obsession detection and trends
- **Emotions**: Mood analysis and recommendations
- **Temporal**: Time-based listening patterns

**4. Export Options**
- Download processed data as CSV
- Save charts as PNG/SVG
- Export analysis summaries

### **Using the Dashboard**

**Step 1: Data Selection**
- Choose from existing CSV files
- Upload new Exportify exports
- Select date ranges to analyze

**Step 2: Configure Analysis**
- Set obsession threshold (default: 10)
- Choose chart types
- Enable/disable Spotify API features

**Step 3: Explore Results**
- Navigate between analysis tabs
- Interact with charts and filters
- Read generated insights and recommendations

**Step 4: Export Insights**
- Download processed data
- Save visualizations
- Share summary reports

---

## 🔧 Advanced Usage

### **Spotify API Setup**

**1. Get Credentials**
- Visit [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
- Create new app
- Copy Client ID and Client Secret

**2. Configure Environment**
```powershell
# Copy template
copy .env.template .env

# Edit .env file
notepad .env
```

**Add your credentials:**
```
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

**3. Test API Connection**
```python
from src.emotion_analysis import _get_spotify_client

client = _get_spotify_client()
if client:
    print("✅ Spotify API connected!")
else:
    print("❌ API connection failed")
```

### **Custom Analysis**

**Modify Settings:**
Edit `src/config.py`:
```python
# Change obsession threshold
DEFAULT_REPEAT_THRESHOLD = 5  # Default: 10

# Modify top N results
DEFAULT_TOP_N = 20  # Default: 10
```

**Add Custom Visualizations:**
Extend `src/visualization.py`:
```python
def plot_custom_analysis(df, save_path=None):
    """Your custom visualization logic"""
    fig, ax = plt.subplots(figsize=(12, 8))
    # Custom plotting code
    return fig
```

### **Batch Processing**

**Process Multiple Files:**
```python
from pathlib import Path
from src.data_processing import load_exportify, clean
from src.pattern_analysis import playlist_stats

csv_files = Path("data/raw").glob("*.csv")
all_stats = []

for csv_file in csv_files:
    df = clean(load_exportify(csv_file))
    stats = playlist_stats(df)
    stats['source_file'] = csv_file.name
    all_stats.append(stats)

# Compare playlists
for stat in all_stats:
    print(f"{stat['source_file']}: {stat['total_tracks']} tracks")
```

---

## 📁 Data Management

### **Adding New Music Data**

**1. Export from Spotify**
- Use [Exportify](https://github.com/watsonbox/exportify)
- Export individual playlists or entire library
- Save as CSV files

**2. Organize Files**
```
data/raw/
├── my_favorites_2024.csv
├── workout_playlist.csv
├── chill_vibes.csv
└── x_rap_x.csv  # Sample data
```

**3. Run Analysis**
```powershell
# Processes all CSV files automatically
.\orpheus_venv\Scripts\python.exe main.py
```

### **Data Quality Tips**

**Ensure Good Results:**
- Use complete playlist exports (not partial)
- Include date information ("Added At" column)
- Verify CSV encoding (UTF-8 preferred)
- Check for duplicate playlists

**Troubleshooting Data Issues:**
```python
from src.data_processing import validate_exportify_schema

# Check data quality
validation = validate_exportify_schema(df)
print("Validation results:", validation)
```

---

## 🎯 Use Case Examples

### **1. Musical Journey Analysis**
**Goal**: Track how your music taste evolved over time

**Process:**
1. Export all playlists chronologically
2. Run temporal pattern analysis
3. Look for genre shifts and artist obsessions
4. Create timeline visualization

**Insights:**
- Musical phase transitions
- Artist discovery periods
- Genre exploration patterns

### **2. Mood Tracking**
**Goal**: Correlate music choices with emotional states

**Process:**
1. Enable Spotify API for audio features
2. Analyze valence/energy patterns
3. Add manual mood annotations
4. Generate emotional recommendations

**Insights:**
- Happy vs. melancholic periods
- Energy level preferences
- Emotional music triggers

### **3. Obsession Detection**
**Goal**: Identify artists/songs you play repeatedly

**Process:**
1. Set appropriate obsession threshold
2. Run repeat obsession analysis
3. Examine intensity patterns
4. Track obsession duration

**Insights:**
- Musical fixation cycles
- Artist attachment patterns
- Song replay behaviors

---

## 🆘 Troubleshooting

### **Common Issues**

**Error: "No module named pandas"**
```powershell
# Ensure virtual environment is activated
.\orpheus_venv\Scripts\activate
# Reinstall packages
pip install -r requirements.txt
```

**Error: "No CSV files found"**
- Check files are in `data/raw/` directory
- Verify CSV file format
- Ensure files have `.csv` extension

**Streamlit won't start**
```powershell
# Check if port is in use
netstat -an | findstr :8501
# Use different port
.\orpheus_venv\Scripts\streamlit.exe run ui/app.py --server.port 8502
```

**Empty analysis results**
- Verify CSV contains valid Exportify data
- Check date columns are properly formatted
- Ensure track/artist names are present

### **Performance Tips**

**For Large Datasets:**
- Process files individually first
- Use date range filtering
- Increase obsession thresholds
- Monitor memory usage

**Spotify API Limits:**
- API has rate limits (requests per second)
- Large playlists may take time to process
- Consider processing in batches

---

## 📚 Next Steps

### **Expand Your Analysis**
1. **Add more playlists**: Export your entire Spotify library
2. **Set up Spotify API**: Get real audio features
3. **Create custom insights**: Modify analysis parameters
4. **Share discoveries**: Export and share your musical patterns

### **Advanced Projects**
1. **Comparative Analysis**: Compare multiple users' patterns
2. **Predictive Modeling**: Predict future music preferences
3. **Integration**: Connect with mood tracking apps
4. **Automation**: Set up automated playlist analysis

---

**🎉 You're now ready to explore the emotional depths of your musical soul with Project Orpheus! 🎉**
