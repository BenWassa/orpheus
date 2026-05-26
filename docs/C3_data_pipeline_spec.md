# C3_data_pipeline_spec.md
## Project Orpheus v2 — Data Pipeline and Build Architecture

### Purpose
Define how data physically moves through the system: ingestion, storage, enrichment, processing, output. C2 covered what the engine computes. C3 covers how it's built and orchestrated.

---

### 1. Project Structure

```
orpheus-v2/
├── README.md
├── pyproject.toml          # modern Python packaging
├── config.yaml             # user config (API keys, weights, thresholds)
├── docs/
│   ├── T1_taxonomy_v1.md
│   ├── C2_methodology_spec.md
│   ├── C3_data_pipeline_spec.md
│   └── PRD.md
├── orpheus/                # main package
│   ├── __init__.py
│   ├── ingest/
│   │   ├── spotify_export.py    # parse Extended Streaming History JSON
│   │   └── spotify_live.py      # Web API client
│   ├── enrich/
│   │   ├── soundnet.py          # primary audio features client
│   │   ├── essentia.py          # local fallback extractor
│   │   ├── archive_lookup.py    # Anna's Archive bulk cache reader
│   │   └── genius.py            # lyrics fetcher
│   ├── score/
│   │   ├── emotion.py           # BART-MNLI + acoustic fusion
│   │   ├── theme.py             # MPNet + s-VSM + artist prior
│   │   ├── depth.py             # composite scoring
│   │   └── models/              # cached transformer weights
│   ├── aggregate/
│   │   ├── decay.py             # exponential weight math
│   │   └── windows.py           # state + trait window aggregators
│   ├── pattern/
│   │   ├── cluster.py           # DBSCAN + GMM
│   │   └── trends.py            # trend detection, co-occurrence
│   ├── output/
│   │   └── assemble.py          # JSON output builder
│   ├── safety/
│   │   └── rumination.py        # hook, inactive for MVP
│   ├── db/
│   │   ├── schema.sql
│   │   └── migrations/
│   ├── cli.py                   # entry points
│   └── config.py
├── data/
│   ├── raw/                     # Spotify export JSON drops here
│   ├── cache/
│   │   └── orpheus.db          # SQLite, all persistent state
│   └── output/
│       └── reports/             # JSON reports per run
├── prompts/                     # P# prompts for narrative generation (later)
├── scripts/
│   ├── bootstrap.py             # one-time setup
│   └── archive_bulk_import.py   # pre-populate from Anna's Archive
└── tests/
    └── fixtures/
```

Notable shifts from v1:
- No `01_setup` / `02_core` numbered folders; standard Python package layout instead
- Streamlit gone (no `03_interface`)
- Single SQLite cache instead of CSVs scattered across folders
- Engine decoupled from frontend entirely (frontend lives in a separate repo or `web/` subdirectory later)

---

### 2. Storage Architecture

SQLite database at `data/cache/orpheus.db`. One file, file-based, no server. Backed up by copying.

**Schema:**

```sql
-- Raw listening events
CREATE TABLE plays (
    id INTEGER PRIMARY KEY,
    ts TEXT NOT NULL,                  -- ISO timestamp
    ms_played INTEGER NOT NULL,
    track_uri TEXT,                    -- spotify URI
    track_name TEXT,
    artist_name TEXT,
    album_name TEXT,
    reason_start TEXT,
    reason_end TEXT,
    shuffle BOOLEAN,
    skipped BOOLEAN,
    source TEXT,                       -- 'export' or 'live_api'
    ingested_at TEXT
);
CREATE INDEX idx_plays_ts ON plays(ts);
CREATE INDEX idx_plays_track ON plays(track_uri);

-- Unique tracks (canonical identity)
CREATE TABLE tracks (
    track_uri TEXT PRIMARY KEY,
    isrc TEXT,                         -- for cross-source matching
    mbid TEXT,                         -- MusicBrainz ID
    track_name TEXT,
    primary_artist TEXT,
    featured_artists TEXT,             -- JSON array
    album_name TEXT,
    release_date TEXT,
    popularity INTEGER,
    duration_ms INTEGER,
    is_instrumental BOOLEAN,
    enriched_at TEXT
);

-- Cached audio features (immutable per track)
CREATE TABLE audio_features (
    track_uri TEXT PRIMARY KEY,
    source TEXT,                       -- 'soundnet' | 'essentia' | 'archive'
    valence REAL,
    arousal REAL,
    tempo REAL,
    key INTEGER,
    mode INTEGER,
    energy REAL,
    danceability REAL,
    acousticness REAL,
    instrumentalness REAL,
    loudness REAL,
    spectral_centroid REAL,
    spectral_complexity REAL,
    fetched_at TEXT,
    FOREIGN KEY(track_uri) REFERENCES tracks(track_uri)
);

-- Cached lyrics (immutable per track)
CREATE TABLE lyrics (
    track_uri TEXT PRIMARY KEY,
    raw_text TEXT,
    cleaned_text TEXT,
    annotations TEXT,                  -- JSON: Genius crowd annotations
    has_lyrics BOOLEAN,
    fetched_at TEXT,
    FOREIGN KEY(track_uri) REFERENCES tracks(track_uri)
);

-- Per-track scores (versioned by model)
CREATE TABLE track_scores (
    track_uri TEXT,
    model_version TEXT,                -- e.g., 'bart-mnli-v1+mpnet-v1'
    emotion_scores TEXT,               -- JSON, 8 categories
    theme_scores TEXT,                 -- JSON, 8 categories
    depth_score REAL,
    depth_label TEXT,
    confidence TEXT,                   -- JSON
    scored_at TEXT,
    PRIMARY KEY(track_uri, model_version),
    FOREIGN KEY(track_uri) REFERENCES tracks(track_uri)
);

-- Artist-level aggregates (priors)
CREATE TABLE artists (
    artist_name TEXT PRIMARY KEY,
    spotify_id TEXT,
    mbid TEXT,
    genres TEXT,                       -- JSON array
    canonical_themes TEXT,             -- JSON: aggregated theme prior
    play_count INTEGER,
    updated_at TEXT
);

-- Pipeline run records (reproducibility)
CREATE TABLE pipeline_runs (
    run_id TEXT PRIMARY KEY,
    started_at TEXT,
    finished_at TEXT,
    config_snapshot TEXT,              -- JSON of full config at run time
    model_versions TEXT,               -- JSON
    play_count_processed INTEGER,
    track_count_processed INTEGER,
    output_path TEXT,
    output_hash TEXT                   -- for reproducibility verification
);
```

**Migration strategy:**
- Schema version tracked in a `schema_version` table
- Migrations live in `orpheus/db/migrations/NNN_description.sql`
- CLI command `orpheus db migrate` applies pending migrations idempotently

---

### 3. CLI Commands

The engine is a CLI tool. No daemon, no server. Run on demand.

```
orpheus ingest --source <path>     # parse export JSON, write to plays + tracks
orpheus enrich                     # fetch audio features + lyrics for new tracks
orpheus score                      # run scoring on enriched tracks
orpheus analyze                    # aggregate + cluster + detect trends
orpheus report [--out <path>]      # write JSON output
orpheus run-all                    # convenience: full pipeline end-to-end
orpheus status                     # show DB state, missing enrichments, last run

orpheus live sync                  # pull latest from Spotify Web API into plays
orpheus archive import <path>      # bulk-import from Anna's Archive dump

orpheus db migrate                 # apply schema migrations
orpheus config validate            # check config.yaml has required keys
```

Each command is idempotent. Re-running `enrich` skips already-enriched tracks. Re-running `score` skips already-scored tracks for the current model version.

---

### 4. API Integrations

**SoundNet/SoundStat API**
- Auth: RapidAPI key from `config.yaml`
- Endpoint: track lookup by Spotify ID or ISRC
- Batching: batch requests where the API supports it; rate limit per their tier
- Retry: exponential backoff on 429/503 (1s, 2s, 4s, 8s, 16s, max 5 retries)
- Cost: paid pay-per-use. Budget approximately $0.001-0.003 per track. For a typical 5K-track library, first run cost is under $15. Subsequent runs hit cache.

**Essentia (local fallback)**
- Triggered when SoundNet returns no match
- Requires the audio file, which Spotify does not provide. So Essentia only works if user has local audio files matching tracks (less common).
- In practice: most tracks resolved via SoundNet or Anna's Archive cache. Essentia is rarely needed for typical Spotify-only users.
- Keep it scaffolded for non-mainstream tracks but expect <5% of catalog needs it.

**Anna's Archive bulk cache**
- One-time import via `orpheus archive import <path>`
- Pre-populates `audio_features` table for the 256M tracks in the dump
- For a personal library, expect 80-95% of tracks resolved from this single source
- Removes most of the SoundNet API spend

**Spotify Web API**
- Auth: OAuth 2.0 Authorization Code flow
- Scopes: `user-read-recently-played`, `user-top-read`, `user-library-read`, `playlist-read-private`
- Note: audio-features and recommendations endpoints are dead (Nov 2024). Do not call them.
- Endpoints in use:
  - `GET /me/top/tracks?time_range={short|medium|long}_term`
  - `GET /me/top/artists?time_range={short|medium|long}_term`
  - `GET /me/player/recently-played`
  - `GET /me/tracks` (saved library, paginated)
  - `GET /me/playlists`
  - `GET /artists/{id}` (genre tags)
  - `GET /tracks/{id}` (metadata only, no audio features)
- Token refresh handled silently; refresh token stored in `data/cache/spotify_tokens.json` with 0600 perms.

**Genius API**
- Auth: client access token from `config.yaml`
- Lyrics retrieval: Genius API search returns song URL; raw lyrics require scraping the song page (Genius removed direct lyrics endpoint years ago)
- Library: `lyricsgenius` Python package handles this; or roll a minimal scraper if dependency is undesirable
- Cache forever per track. Lyrics don't change.

---

### 5. Pipeline Orchestration

End-to-end run flow:

```
[1] orpheus ingest --source ./data/raw/spotify_export
      → parse all JSON files, dedupe, insert into plays
      → resolve unique tracks, insert into tracks
      → log run start

[2] orpheus live sync
      → pull current top tracks/artists, recently played
      → augment plays table with recent events
      → tag source='live_api'

[3] orpheus enrich
      → for each track in tracks where enriched_at IS NULL:
          → check audio_features cache (Anna's Archive import)
          → if miss: call SoundNet API
          → if miss: try Essentia (requires local audio)
          → fetch lyrics from Genius
          → update tracks.enriched_at

[4] orpheus score
      → for each enriched track where score missing for current model_version:
          → run emotion classifier (BART-MNLI + acoustic fusion)
          → run theme classifier (MPNet + s-VSM + artist prior)
          → compute depth score
          → insert into track_scores
      → recompute artist-level priors

[5] orpheus analyze
      → apply time-decay weights, compute state + trait window scores
      → run DBSCAN noise filter
      → run GMM clustering
      → detect trends, co-occurrences, shifts
      → store intermediate results in run-scoped temp tables

[6] orpheus report --out ./data/output/reports/{timestamp}.json
      → assemble JSON per C2 schema
      → write to disk
      → record run in pipeline_runs
```

Each step writes its own artifacts. Failures at step N do not require redoing steps 1 to N-1.

---

### 6. Caching and Reproducibility

**What's cached:**
- Audio features: cached forever per track. No expiration.
- Lyrics: cached forever per track.
- Track scores: cached per (track, model_version) pair. New model version triggers re-scoring.

**What's regenerated each run:**
- Aggregations (cheap, depend on time of run)
- Clusters (depend on aggregations)
- Trends, co-occurrences, shifts
- Final report

**Reproducibility guarantees:**
- Same input data + same config + same model versions = byte-identical output
- `output_hash` recorded in `pipeline_runs` allows verification
- Model versions pinned in `config.yaml`:
  ```yaml
  models:
    emotion_classifier: "facebook/bart-large-mnli@v1"
    semantic_embedding: "sentence-transformers/all-mpnet-base-v2@v1"
    sentiment_filter: "s-VSM-v1"
  ```
- Seed values for any stochastic components (GMM init) stored per run

---

### 7. Configuration

Single `config.yaml` at project root:

```yaml
# API credentials
spotify:
  client_id: "..."
  client_secret: "..."
  redirect_uri: "http://localhost:8080/callback"

soundnet:
  api_key: "..."
  rate_limit_per_minute: 60

genius:
  access_token: "..."

# Pipeline parameters
windows:
  state_half_life_days: 3
  trait_half_life_days: 90

engagement_weights:
  full_play: 1.0
  partial_play: 0.7
  early_skip: -0.5
  boundary_skip: -0.25
  repeat_session: 0.3
  shuffle_source: -0.1
  library_play: 0.1

clustering:
  dbscan_min_pts: 5
  gmm_components: 3

depth_labels:
  - threshold: 0.33
    label: "surface"
  - threshold: 0.66
    label: "engaged"
  - threshold: 1.0
    label: "immersive"

safety:
  active: false                     # MVP off; flip true for friend-test phase
  rumination_density_threshold: 0.7
  rumination_duration_hours: 48

# Model versions
models:
  emotion_classifier: "facebook/bart-large-mnli"
  semantic_embedding: "sentence-transformers/all-mpnet-base-v2"
```

Validated by `orpheus config validate` before any other command runs.

---

### 8. Error Handling

**API failures:**
- 429 Too Many Requests: exponential backoff, max 5 retries
- 5xx: same as above
- 4xx (not 429): log and skip that track; mark in tracks table as `enrichment_failed=true`
- Persistent failures recorded in a `failed_enrichments` log for manual review

**Missing data:**
- Instrumental track (no lyrics): proceed with acoustic-only theme scoring, lower confidence
- Track not in any audio features source: skip scoring for that track, exclude from analysis with a count of skipped tracks in report
- Empty windows (e.g., user has <30 days of data for trait): degrade gracefully, surface a note in output

**Schema mismatches:**
- Old data with new schema: migrate
- New data with old schema: refuse to run, prompt migration

---

### 9. Performance Targets (personal-use scale)

Assumptions: typical user, 3-5 years of listening history, 30K-100K plays, 3K-10K unique tracks.

| Step | Expected runtime |
|---|---|
| Ingest (parse JSON) | <30 seconds |
| Live sync | <30 seconds (rate-limited by Spotify) |
| Enrich (cold, no Anna's Archive cache) | 1-3 hours (API rate limits dominate) |
| Enrich (warm, with Archive cache) | 5-15 minutes |
| Score (5K tracks) | 10-30 minutes (transformer inference) |
| Analyze | <1 minute |
| Report | <5 seconds |

First full run: under 4 hours worst case. Subsequent runs: under 30 minutes once cache is populated.

GPU not required but speeds up scoring step 5-10x.

---

### 10. What's Deferred to Later Components

- **Frontend / UX (C4):** how the JSON output gets rendered to users
- **Onboarding flow (C5):** how a user goes from zero to first report
- **Multi-user / sharing (post-MVP):** the current spec is single-user, local-only
- **Real-time updates:** no streaming pipeline. Re-run on demand.
- **Hosted version (post-friend-test):** if Orpheus goes public, the engine probably stays local with hosted version optional

---

### 11. Open Questions

- **Genius API stability:** Genius has been hostile to scrapers historically. Worth pricing MusixMatch as alternative if Genius proves brittle.
- **Anna's Archive legality / longevity:** the 200GB dump is gray-area. Depending on a single source that may disappear. Worth using it for cache hydration but not as a runtime dependency.
- **Local-only assumption:** does the engine assume single-user, or do we design for multi-user from day one? Current spec is single-user.
- **Lyrics in non-English:** the BART-MNLI and MPNet models are English-trained. Foreign-language lyrics will score poorly. Note as limitation in output.
