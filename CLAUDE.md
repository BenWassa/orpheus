# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)

## Commands

```bash
# Setup
python scripts/bootstrap.py          # Create dirs, copy config template, init DB

# Development
pip install -e ".[dev]"              # Install with dev dependencies

# Linting
ruff check orpheus/ tests/           # Lint
ruff format orpheus/ tests/          # Format (line length: 100, target: py311)

# Tests
pytest                               # All tests
pytest -m "not slow"                 # Skip transformer-loading tests
pytest tests/test_pipeline_e2e.py   # Full end-to-end with synthetic data
pytest tests/test_score.py -v       # Single test file

# CLI (requires config.yaml to exist)
orpheus config validate
orpheus db migrate
orpheus status
orpheus ingest --source data/raw/<export>.json
orpheus enrich
orpheus score
orpheus analyze
orpheus report [--out data/output/reports/my_report.json]
orpheus run-all --source data/raw/
```

## Architecture

The pipeline runs linearly: **Ingest → Enrich → Score → Aggregate → Pattern → Output**. Each step is independently re-runnable — later steps query the DB for already-processed records and skip re-work. The entire state lives in a SQLite database (`data/cache/orpheus.db`).

### Pipeline steps

| Step | Module | What it does |
|------|--------|--------------|
| Ingest | `orpheus/ingest/spotify_export.py` | Parses Spotify Extended Streaming History JSON; deduplicates by `(ts, track_uri)`; writes `plays` and `tracks` tables |
| Enrich | `orpheus/enrich/` | Fetches audio features (archive DB → SoundNet RapidAPI fallback) and lyrics (Genius); marks `tracks.enriched_at` when done |
| Score | `orpheus/score/` | Runs `facebook/bart-large-mnli` for emotion classification and `sentence-transformers/all-mpnet-base-v2` for theme scoring; writes `track_scores` |
| Aggregate | `orpheus/aggregate/` | Computes **state** (3-day half-life) and **trait** (90-day half-life) windows using engagement weights + exponential time decay |
| Pattern | `orpheus/pattern/` | DBSCAN noise removal → GMM clustering on V/A/D space; weekly trend detection over 12-week lookback |
| Output | `orpheus/output/assemble.py` | Assembles JSON report with all window data, trends, clusters, and safety flags; logs a `pipeline_runs` row with config snapshot + SHA256 hash |

### Key design points

**Config** (`orpheus/config.py`) is a tree of dataclasses loaded from `config.yaml`. All tunable parameters live there — half-lives, engagement weights, clustering params, depth thresholds, model names, API keys. Validated at startup via `validate_config()`.

**Scoring keys** in `track_scores` are composite `(track_uri, model_version)` where `model_version = emotion_classifier + "+" + semantic_embedding`. This allows the table to hold scores across model generations without collisions.

**Engagement weighting** maps play behaviour to `[-0.5, 1.0]`: full play = 1.0, partial = 0.7, early skip = −0.5. These weights combine multiplicatively with exponential time-decay before aggregation, so recent skips can outweigh old full-plays.

**Emotion categories** (8): `joyful_activation`, `triumphant_power`, `peacefulness`, `tenderness`, `nostalgia_longing`, `sadness_melancholy`, `tension_anxiety`, `anger_defiance` — derived from valence/arousal position.

**Theme categories** (8): `interpersonal_devotion`, `heartbreak_loss`, `adversity_resilience`, `identity_autonomy`, `status_ambition`, `hedonism_escape`, `place_heritage`, `existentialism_spirituality`.

**Safety module** (`orpheus/safety/rumination.py`) is opt-in (`config.safety.active: false`). It flags potential rumination when summed negative-valence emotions exceed a density threshold over a configurable duration.

### Database schema

Eight tables: `plays`, `tracks`, `audio_features`, `lyrics`, `track_scores`, `artists`, `pipeline_runs`, `schema_version`. See `orpheus/db/schema.sql` for full DDL and indexes.

### Testing

Tests avoid loading transformer models. The E2E test (`tests/test_pipeline_e2e.py`) inserts synthetic enrichment and scores directly into the DB, then exercises aggregation, clustering, trends, safety, and report assembly without any external API calls.

`tests/conftest.py` excludes `test_streamlit_app.py` and `test_navigation.py` from collection. Core fixtures: `tmp_project` (isolated dir + config), `tmp_config`, `tmp_db` (SQLite with schema applied), `sample_export_path` (→ `tests/fixtures/sample_export.json`).

Mark slow tests (transformer loading) with `@pytest.mark.slow`.
