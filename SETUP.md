# Orpheus Setup Guide

## Prerequisites

- Python 3.11+
- pip / venv
- Spotify Extended Streaming History export (from [spotify.com/account/privacy](https://www.spotify.com/account/privacy))

## Installation

```bash
# Clone and enter repo
git clone <repo> && cd orpheus

# Create venv
python3.11 -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Initialize database and config
python scripts/bootstrap.py
```

This creates:
- `data/cache/orpheus.db` — SQLite database
- `data/output/reports/` — report output directory
- `config.yaml` — configuration file (from template)

## Data Sources and Credentials

Before running the pipeline, you need a Spotify export and, for best results, an
audio-feature archive CSV. The only API key needed is Genius, for lyrics.
ReccoBeats can fill residual audio-feature gaps without a key.

### 1. Genius Access Token

**Purpose:** Fetch song lyrics.

**How to get it:**
1. Go to [genius.com/api-clients](https://genius.com/api-clients)
2. Sign up / log in
3. Create a new API Client
4. Generate an **access token**
5. Copy the token (begins with `[a-z0-9]+`)

**Config:**
```yaml
genius:
  access_token: "YOUR_TOKEN_HERE"
```

### 2. Audio Features

**Purpose:** Audio features (valence, arousal, tempo, energy) drive the V/A/D
clustering step.

Spotify's `/audio-features` API is retired for new apps, so Orpheus uses a
static-first approach:

1. Bulk import a Kaggle/static CSV or SQLite archive keyed by Spotify track ID.
2. Optionally fill tracks not found in the archive with ReccoBeats.

```bash
orpheus archive import data/raw/tracks_features.csv
orpheus archive fill-gaps
```

The importer accepts CSV files with `id`, `track_id`, or `spotify_id` columns,
plus SQLite archives with an `audio_features` table. If no audio features are
available, the rest of the report still works, but clustering reports
`no_audio_features`.

**Cost estimate:**
- Genius: free, unlimited
- ReccoBeats: free, no API key

### 3. Spotify (Optional)

For Phase 1 (one-time export analysis), you don't need Spotify API credentials — the extended streaming history export is sufficient. Leave blank for now:

```yaml
spotify:
  client_id: ""
  client_secret: ""
  redirect_uri: "http://localhost:8080/callback"
```

This becomes relevant only if you enable live sync (`orpheus live sync`) in Phase 2.

## Run the Pipeline

Once credentials are in place:

```bash
# Recommended data-complete path
orpheus ingest --source path/to/Spotify\ Extended\ Streaming\ History/
orpheus archive import data/raw/tracks_features.csv
orpheus archive fill-gaps
orpheus enrich
orpheus score
orpheus refresh

# Convenience path without an audio-feature archive
orpheus run-all --source path/to/Spotify\ Extended\ Streaming\ History/

# Normal repeat use after data is already loaded
orpheus refresh

# Check status
orpheus status

# Inspect tracks still missing audio features
orpheus archive missing-audio --out data/output/missing_audio_features.json
```

**Expected runtime:**
- Archive import: seconds to minutes, depending on archive size
- Gap fill: rate-limited by ReccoBeats batch delay
- Enrich: fast, lyrics only via Genius
- Score: ~5–10 min (transformer models load once)
- Refresh/report: seconds; recomputes aggregation, clusters, and JSON output

Output JSON will be written to `data/output/reports/YYYYMMDDTHHMMSS.json`.

## Troubleshooting

**"Genius token unauthorized"**
- Regenerate the token at genius.com/api-clients
- Verify it's your access token, not the API base URL

**"clusters: no_audio_features" in the report**
- Run `orpheus archive import <path-to-csv-or-sqlite>` after ingesting tracks
- Then run `orpheus archive fill-gaps` to try ReccoBeats for remaining misses
- Everything else in the report works even without audio features

**"No lyrics found for track"**
- Genius coverage is ~85% of Spotify catalog
- Tracks without lyrics will be marked `has_lyrics: false` in the database

## Config Reference

See `config.yaml` for tunable parameters:

| Setting | Default | Purpose |
|---------|---------|---------|
| `state_half_life_days` | 3 | Recent listening window (decay weight) |
| `trait_half_life_days` | 90 | Long-term baseline window |
| `engagement_weights.*` | varies | Play behavior scoring: full play (1.0) → early skip (-0.5) |
| `dbscan_min_pts` | 5 | Clustering noise threshold |
| `gmm_components` | 3 | Number of emotion/theme clusters |
| `reccobeats.batch_size` | 20 | Spotify IDs per ReccoBeats request |
| `reccobeats.delay` | 0.5 | Delay between ReccoBeats batches, in seconds |
| `safety.active` | false | Rumination detection (experimental) |

Do not modify these without understanding the aggregation model — see `docs/C3_data_pipeline_spec.md`.
