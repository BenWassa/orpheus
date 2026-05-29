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

## API Credentials

Before running the pipeline, you need **one** API key in `config.yaml` (Genius, for lyrics). Spotify is optional and audio features are deferred — see below:

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

### 2. Audio Features (Deferred — No Live Source)

**Purpose:** Audio features (valence, arousal, tempo, energy) drive the V/A/D
clustering step. There is currently **no working live source** for them.

The RapidAPI "track-analysis" (SoundNet) API was evaluated and removed — its
BASIC tier allows only 5 requests/day, which is unusable for a multi-thousand
track corpus. See [docs/C3_data_pipeline_spec.md](docs/C3_data_pipeline_spec.md)
for the full rationale and candidate replacement sources under consideration.

**Impact:** Everything except clustering works without audio features. Emotion
and theme scoring run off lyrics, so the pipeline produces a full report — the
`clusters` section will simply report `no_audio_features` until a source is wired
up. If you have a local archive cache of audio features, point `orpheus enrich`
at it; otherwise audio features are skipped.

**Cost estimate:**
- Genius: free, unlimited

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
# Full pipeline end-to-end
orpheus run-all --source path/to/Spotify\ Extended\ Streaming\ History/

# Or step-by-step
orpheus ingest --source path/to/Spotify\ Extended\ Streaming\ History/
orpheus enrich
orpheus score
orpheus analyze
orpheus report

# Check status
orpheus status
```

**Expected runtime:**
- Enrich: fast — lyrics only (Genius), plus any local audio-feature archive lookups
- Score: ~5–10 min (transformer models load once)
- Analyze: < 1 min
- Report: < 1 sec

Output JSON will be written to `data/output/reports/YYYYMMDDTHHMMSS.json`.

## Troubleshooting

**"Genius token unauthorized"**
- Regenerate the token at genius.com/api-clients
- Verify it's your access token, not the API base URL

**"clusters: no_audio_features" in the report**
- Expected — there is no live audio-feature source (see section 2 above)
- Everything else in the report is unaffected

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
| `safety.active` | false | Rumination detection (experimental) |

Do not modify these without understanding the aggregation model — see `docs/C3_data_pipeline_spec.md`.
