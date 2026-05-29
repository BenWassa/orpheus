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

## How it works

Orpheus runs a linear, re-runnable pipeline. Each step reads the SQLite database
(`data/cache/orpheus.db`) and skips work already done.

**Ingest → Enrich → Score → Aggregate → Pattern → Output**

| Step | What it does |
|------|--------------|
| **Ingest** | Parses your Spotify Extended Streaming History JSON into `plays` and `tracks`. |
| **Enrich** | Fetches lyrics (Genius) and audio features (local archive only — see note below). |
| **Score** | Classifies emotion (`bart-large-mnli`) and themes (`all-mpnet-base-v2`) per track. |
| **Aggregate** | Computes a recent **state** window (3-day half-life) and a long-term **trait** window (90-day half-life). |
| **Pattern** | Clusters listening in valence/arousal/depth space and detects weekly trends. |
| **Output** | Assembles a JSON report with windows, trends, clusters, and safety flags. |

The report lands in `data/output/reports/YYYYMMDDTHHMMSS.json`. The React
frontend in [`frontend/`](frontend/) renders it as a readable narrative.

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

# Run the full pipeline
orpheus run-all --source "path/to/Spotify Extended Streaming History/"

# ...or step by step
orpheus ingest --source "path/to/Spotify Extended Streaming History/"
orpheus enrich
orpheus score
orpheus analyze
orpheus report

orpheus status   # check progress at any time
```

See **[SETUP.md](SETUP.md)** for credentials, runtimes, and troubleshooting.

### Viewing the report

```bash
cd frontend
npm install
npm run dev      # opens the dashboard locally (Vite)
```

---

## Audio features (note)

Audio features (valence, arousal, tempo, energy) drive the clustering step.
There is currently **no working live source** — the RapidAPI option was removed
for being too rate-limited to use. Everything else works without them: emotion
and theme scoring run off lyrics, so you still get a full report. The `clusters`
section simply reports `no_audio_features` until a source is wired up (or a local
archive cache is supplied). See
[docs/C3_data_pipeline_spec.md](docs/C3_data_pipeline_spec.md) for details.

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

## Documentation

- **[SETUP.md](SETUP.md)** — installation, API credentials, troubleshooting.
- **[docs/PRD.md](docs/PRD.md)** — product requirements.
- **[docs/C2_methodology_spec.md](docs/C2_methodology_spec.md)** — scoring & aggregation methodology.
- **[docs/C3_data_pipeline_spec.md](docs/C3_data_pipeline_spec.md)** — data pipeline & audio-feature sourcing.

---

## License

Dual-licensed: code under the **MIT License**, creative content under
**CC BY-NC-ND 4.0**. See [LICENSE.md](LICENSE.md).
