# Project Orpheus

**Decode your emotional underworld through the music that moves you.**

---

## 📜 Vision

Project Orpheus is an introspective exploration of the self through music. By analyzing personal listening patterns — recurring obsessions, sudden fixations, shifting phases — it maps the hidden emotional currents shaping your inner life. Inspired by the myth of Orpheus, who descended into darkness guided by song, this project transforms your listening history into a lantern for self-discovery.

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

### Next Steps
1. Set up Python environment with required packages
2. Run initial data exploration notebook
3. Begin pattern analysis on pilot dataset
4. Develop emotional mapping framework

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

---

## 🤝 Contributing

For now, this is a personal exploration. In the future, collaboration may open for those interested in blending **music**, **myth**, and **introspective tech**.

---

## 📚 License

This project is released under the **MIT License** — see `LICENSE` for details.

---

**May your music lead you inward, and your insights bring you home.**
