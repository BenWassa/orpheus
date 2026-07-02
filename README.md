# 🎵 Project Orpheus

**Decode your emotional underworld through the music that moves you.**

Orpheus is a personal music-analysis tool. It reads your Spotify listening
history and surfaces the emotional and thematic patterns hidden in it — turning
raw play data into a reflective narrative that reads like a letter about
yourself, not a corporate analytics dashboard.

> Just as Orpheus journeyed into the underworld with music as his guide, Project
> Orpheus helps you descend into your emotional depths to retrieve hidden truths
> and fresh self-understanding.

---

## Current stack and approach

Orpheus is now a local-first analysis pipeline with a static-first audio-feature
strategy. It does **not** depend on Spotify's retired `/audio-features` API.

| Layer | Stack |
|-------|-------|
| **CLI and pipeline** | Python 3.11+, Click |
| **Storage** | SQLite at `data/cache/orpheus.db` |
| **Listening data** | Spotify Extended Streaming History JSON |
| **Audio features** | Bulk import from Kaggle/static CSV or SQLite archives, then optional ReccoBeats gap fill |
| **Lyrics** | Genius API via `lyricsgenius` |
| **Scoring** | Hugging Face models: `facebook/bart-large-mnli` and `sentence-transformers/all-mpnet-base-v2` |
| **Patterns** | scikit-learn DBSCAN noise filtering and Gaussian Mixture clustering over valence/arousal/depth |
| **Frontend** | React 19, TypeScript, Vite, lucide-react |
| **Quality** | pytest and Ruff |

The data approach is:

1. Ingest Spotify export files into `plays` and `tracks`.
2. Import audio features by matching Spotify track IDs from `track_uri` against a static archive such as Kaggle's pre-deprecation datasets.
3. Fill any remaining audio-feature gaps through ReccoBeats, which is free, keyless, and Spotify-ID keyed.
4. Fetch lyrics from Genius where available.
5. Score tracks, aggregate state/trait windows, detect patterns, and write the report consumed by the frontend.

This gives the clustering layer real valence/arousal/energy inputs again while
keeping the tool reproducible and mostly offline after the initial data import.

---

## How it works

Orpheus runs a linear, re-runnable pipeline. Each step reads the SQLite database
(`data/cache/orpheus.db`) and skips work already done.

**Ingest → Enrich → Score → Aggregate → Pattern → Output**

| Step | What it does |
|------|--------------|
| **Ingest** | Parses your Spotify Extended Streaming History JSON into `plays` and `tracks`. |
| **Archive** | Imports audio features from CSV/SQLite archives and fills residual gaps with ReccoBeats. |
| **Enrich** | Fetches lyrics from Genius and marks tracks ready for scoring. |
| **Score** | Classifies emotion (`bart-large-mnli`) and themes (`all-mpnet-base-v2`) per track. |
| **Aggregate** | Computes a recent **state** window (3-day half-life) and a long-term **trait** window (90-day half-life). |
| **Pattern** | Clusters listening in valence/arousal/depth space and detects weekly trends. |
| **Output** | Assembles a JSON report with windows, trends, clusters, and safety flags. |

Profile reports land in `data/output/reports/<profile>/YYYYMMDDTHHMMSS.json`.
The React frontend in [`frontend/`](frontend/) renders the newest report for
the selected profile as a readable narrative.

---

## Quick start

Requires **Python 3.11+** and a Spotify Extended Streaming History export
(request it at [spotify.com/account/privacy](https://www.spotify.com/account/privacy)).

```bash
# Install
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Initialize database and config
python scripts/bootstrap.py

# Add your Genius access token to config.yaml (for lyrics)
#   genius:
#     access_token: "YOUR_TOKEN_HERE"

# Recommended data-complete path
orpheus ingest --source "path/to/Spotify Extended Streaming History/"
orpheus archive import data/raw/tracks_features.csv
orpheus archive fill-gaps    # optional: uses ReccoBeats for tracks not found in the archive
orpheus enrich
orpheus score
orpheus refresh --profile Ben

orpheus status   # check progress at any time
orpheus archive missing-audio --out data/output/missing_audio_features.json

# Convenience path if you do not have an audio-feature archive yet
orpheus run-all --source "path/to/Spotify Extended Streaming History/" --profile Ben

# Normal repeat use after data is already in the DB
orpheus refresh --profile Ben

# Static exports always end in the past; anchor the "recent" window to the
# newest play instead of the wall clock:
orpheus refresh --profile Ben --as-of latest-play
```

See **[SETUP.md](SETUP.md)** for credentials, runtimes, and troubleshooting.

### Viewing the report

```bash
cd frontend
npm install
npm run dev      # opens the dashboard locally (Vite)
```

---

## Project layout

- **[`orpheus/`](orpheus/)** — the Python package and CLI (ingest, enrich, score, aggregate, pattern, output).
- **[`frontend/`](frontend/)** — React + Vite dashboard that renders the report JSON.
- **[`scripts/`](scripts/)** — bootstrap and utility scripts.
- **[`docs/`](docs/)** — product requirements, methodology, and data-pipeline specs.
- **[`tests/`](tests/)** — pytest suite, including a synthetic end-to-end test.
- **`config.yaml`** — all tunable parameters (half-lives, weights, clustering, model names, API keys).

---

## Development

```bash
ruff check orpheus/ tests/    # lint
ruff format orpheus/ tests/   # format
pytest                        # all tests
pytest -m "not slow"          # skip transformer-loading tests
```

See [CLAUDE.md](CLAUDE.md) for the full architecture reference and design notes.

---

## Docs map

- **[STATUS.md](STATUS.md)** — **the single status document**: current verified state, findings ledger, and the build-out roadmap. Start here for "where is this project at?".
- **Root docs** — entry points and operating guides: this README, [SETUP.md](SETUP.md), [PRODUCT.md](PRODUCT.md), [CLAUDE.md](CLAUDE.md), and [AGENTS.md](AGENTS.md).
- **[`docs/`](docs/)** — durable product, methodology, data-pipeline, and implementation specs.
- **[`frontend/*.md`](frontend/)** — frontend build commission, QA notes, and numbered implementation briefs.
- **[`orpheus/enrich/README.md`](orpheus/enrich/README.md)** — enrichment-specific setup and behavior notes.
- **[`archive/`](archive/)** — historical material: the v1 Streamlit implementation and the dated frontend-upgrade handoff bundle. Reference only, not live architecture.

---

## Documentation

- **[SETUP.md](SETUP.md)** — installation, API credentials, troubleshooting.
- **[docs/PRD.md](docs/PRD.md)** — product requirements.
- **[docs/C2_methodology_spec.md](docs/C2_methodology_spec.md)** — scoring & aggregation methodology.
- **[docs/C3_data_pipeline_spec.md](docs/C3_data_pipeline_spec.md)** — data pipeline & audio-feature sourcing.
- **[docs/D1_primary_tracks.md](docs/D1_primary_tracks.md)** — primary-track decision rule, rationale, and data contract.

---

## License

Dual-licensed: code under the **MIT License**, creative content under
**CC BY-NC-ND 4.0**. See [LICENSE.md](LICENSE.md).
