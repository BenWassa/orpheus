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

Before running the pipeline, you must populate **two** API keys in `config.yaml`:

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

### 2. SoundNet RapidAPI Key

**Purpose:** Fetch audio features (valence, arousal, tempo, energy, etc.) when not cached locally.

**How to get it:**
1. Go to [rapidapi.com/SoundNet-SoundNet/api/SoundNet](https://rapidapi.com/SoundNet-SoundNet/api/SoundNet)
2. Sign up / log in (free tier available)
3. Subscribe to the API
4. Copy your **X-RapidAPI-Key** from the dashboard
5. Paste into config

**Config:**
```yaml
soundnet:
  api_key: "YOUR_RAPIDAPI_KEY_HERE"
  rate_limit_per_minute: 60  # SoundNet free tier: ~1 req/sec
```

**Cost estimate:** 
- Genius: free, unlimited
- SoundNet RapidAPI: free tier allows ~1,500 API calls/month (your 4,243 tracks may need multiple calls depending on cache hits). If you exhaust free tier, paid plans start at ~$5/month.

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
- Enrich: ~10–30 min (API rate-limited by SoundNet; 1 req/sec = ~70 min for 4,243 tracks)
- Score: ~5–10 min (transformer models load once)
- Analyze: < 1 min
- Report: < 1 sec

Output JSON will be written to `data/output/reports/YYYYMMDDTHHMMSS.json`.

## Troubleshooting

**"SoundNet API key invalid"**
- Verify the key is copied correctly (no leading/trailing spaces)
- Check RapidAPI dashboard for active subscription

**"Genius token unauthorized"**
- Regenerate the token at genius.com/api-clients
- Verify it's your access token, not the API base URL

**"Rate limit exceeded"**
- Enrich will retry automatically (exponential backoff)
- Free tier SoundNet: wait 24 hours or upgrade to paid plan

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
