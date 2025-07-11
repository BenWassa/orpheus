# Notebooks Directory

This directory is planned for Jupyter notebooks that provide interactive analysis and exploration.

## 🎯 Current Status: **Planned Feature**

While Jupyter notebooks are not yet implemented, you can achieve interactive analysis using:

### **✅ Available Now:**
1. **Web Dashboard**: `streamlit run ui/app.py` - Interactive browser-based analysis
2. **Python Scripts**: `python main.py` - Complete command-line analysis
3. **Direct Module Usage**: Import and use analysis functions directly

### **📓 Planned Notebooks:**

**`01_data_exploration.ipynb`** - Interactive data discovery
- Load and examine your CSV files
- Explore data quality and completeness
- Visualize basic statistics and distributions

**`02_pattern_analysis.ipynb`** - Pattern detection playground
- Experiment with different obsession thresholds
- Interactive temporal pattern exploration
- Custom pattern detection algorithms

**`03_emotional_mapping.ipynb`** - Emotion analysis deep dive
- Audio feature analysis and visualization
- Sentiment pattern exploration
- Custom emotional mapping techniques

**`04_visualization.ipynb`** - Chart creation workshop
- Create custom visualizations
- Export high-quality plots
- Design emotional timeline variations

## 🚀 **Quick Alternatives**

### **Interactive Analysis (Available Now)**
```powershell
# Launch web dashboard for interactive exploration
.\orpheus_venv\Scripts\streamlit.exe run ui/app.py
```

### **Python Interactive Session**
```python
# Start Python and explore your data
.\orpheus_venv\Scripts\python.exe

# In Python:
import sys
sys.path.append('src')
from src.data_processing import load_exportify, clean
from src.pattern_analysis import playlist_stats, repeat_obsessions
from src.config import DATA_DIR_RAW

# Load your data
csv_files = list(DATA_DIR_RAW.glob('*.csv'))
df = clean(load_exportify(csv_files[0]))

# Explore interactively
stats = playlist_stats(df)
obsessions = repeat_obsessions(df, threshold=3)
print(f"Found {len(obsessions)} obsessions!")
```

### **Custom Script Creation**
Create your own analysis scripts in the notebooks directory:

```python
# notebooks/my_analysis.py
import sys
sys.path.append('../src')

from src.data_processing import load_exportify, clean
from src.pattern_analysis import *
from src.emotion_analysis import *

# Your custom analysis here
```

## 🔮 **Future Development**

When notebooks are implemented, they will include:
- Pre-loaded data and modules
- Interactive widgets for parameter adjustment
- Rich visualizations with plotly/matplotlib
- Step-by-step guided analysis
- Export capabilities for charts and insights

## 🛠️ **Contributing**

If you'd like to create Jupyter notebooks for this project:
1. Install jupyter: `pip install jupyter jupyterlab`
2. Create notebooks following the planned structure
3. Include clear documentation and examples
4. Test with the sample data provided

**For now, the Streamlit dashboard provides excellent interactive analysis capabilities!**
