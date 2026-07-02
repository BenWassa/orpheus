# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)

## Project status

`STATUS.md` is the **single status document** — current verified state,
findings ledger, and the build-out roadmap. Read it before assessing "where
the project is"; update it (rather than creating new status/TODO files) when
progress changes.

## Python environment

All CLI commands (`orpheus`, `python`, `pytest`, `ruff`) live in `.venv/bin/`. Always
prefix with `.venv/bin/` or activate first:

```bash
source .venv/bin/activate   # then use orpheus / python / pytest directly
# or call directly:
.venv/bin/orpheus ...
.venv/bin/python ...
```

## Commands

```bash
# Setup
.venv/bin/python scripts/bootstrap.py   # Create dirs, copy config template, init DB

# Development
.venv/bin/pip install -e ".[dev]"        # Install with dev dependencies

# Linting
.venv/bin/ruff check orpheus/ tests/           # Lint
.venv/bin/ruff format orpheus/ tests/          # Format (line length: 100, target: py311)

# Tests
.venv/bin/pytest                               # All tests
.venv/bin/pytest -m "not slow"                 # Skip transformer-loading tests
.venv/bin/pytest tests/test_pipeline_e2e.py   # Full end-to-end with synthetic data
.venv/bin/pytest tests/test_score.py -v       # Single test file

# CLI (requires config.yaml to exist)
.venv/bin/orpheus config validate
.venv/bin/orpheus db migrate
.venv/bin/orpheus status
.venv/bin/orpheus ingest --source data/raw/<export>.json
.venv/bin/orpheus enrich
.venv/bin/orpheus score
.venv/bin/orpheus analyze
.venv/bin/orpheus report [--out PATH | --profile NAME]
.venv/bin/orpheus refresh [--out PATH | --profile NAME]
.venv/bin/orpheus run-all --source data/raw/ [--out PATH | --profile NAME]
.venv/bin/orpheus archive missing-audio --out data/output/missing_audio_features.json
```

## Generating a report (recurring task)

"Make a report" / "remake the report" is a recurring request. It is **not yet a
slash command** — the report output is still evolving (recently added
`clusters_status`, fixed trend detection), so the steps below will keep changing.
Treat this as the living checklist, not a frozen procedure. When the output
stabilizes, promote it to a `/report` skill that owns the interpretation layer.

The action set, as it stands:
1. Decide scope: `orpheus refresh` re-assembles from existing DB state (fast);
   `orpheus run-all --source <Spotify export dir>` re-runs ingest → enrich → score
   → analyze first (use when underlying data or scoring changed).
2. **Always pass `--profile <name>` (e.g. `--profile Ben`).** The report lands in
   `data/output/reports/<profile>/YYYYMMDDTHHMMSS.json`. The dashboard's dev server
   serves each profile's *newest* JSON from its own subdir — a bare `orpheus refresh`
   writes to the reports-dir **root**, which the profile UI never reads, so the
   dashboard won't change. (`--out PATH` still works for a one-off explicit path;
   `--out` and `--profile` are mutually exclusive.)
3. **Pass `--as-of latest-play` for static exports.** Exports always end in the
   past; without the anchor the "recent" window is empty (the CLI warns). The
   report records the anchor in its `as_of` field.
4. Read the JSON and write a human summary. Beyond windows/trends/shifts/
   co-occurrences/clusters, the report carries `narrative` (server-composed
   headline, insights, archetype, caveats) and `temporal` (full-coverage hours/
   months/moments/rhythm from raw plays) — lead the summary with those.
5. **Sanity-check before presenting** — flag likely artifacts rather than
   reporting them as signal. Known ones: `clusters_status` other than `ok` means
   no/insufficient audio features (clusters legitimately empty); a stale trailing
   week can still skew trends; low `coverage` ratios mean the mood mixture reads
   a thin slice (the narrative's `caveats` already enumerate these — reuse them).
   Call these out explicitly.
6. To view in the dashboard: hard-reload the browser (no rebuild needed — reports
   are fetched at runtime via `/api/reports/latest`) with the profile selected.

## Architecture

The pipeline runs linearly: **Ingest → Enrich → Score → Aggregate → Pattern → Output**. Each step is independently re-runnable — later steps query the DB for already-processed records and skip re-work. The entire state lives in a SQLite database (`data/cache/orpheus.db`).

### Pipeline steps

| Step | Module | What it does |
|------|--------|--------------|
| Ingest | `orpheus/ingest/spotify_export.py` | Parses Spotify Extended Streaming History JSON; deduplicates by `(ts, track_uri)`; writes `plays` and `tracks` tables |
| Enrich | `orpheus/enrich/` | Fetches audio features (local archive DB only — no live audio API; RapidAPI removed, see docs/C3_data_pipeline_spec.md) and lyrics (Genius); marks `tracks.enriched_at` when done |
| Score | `orpheus/score/` | Runs `facebook/bart-large-mnli` for emotion classification and `sentence-transformers/all-mpnet-base-v2` for theme scoring; writes `track_scores` |
| Aggregate | `orpheus/aggregate/` | Computes **state** (3-day half-life) and **trait** (90-day half-life) windows using engagement weights + exponential time decay |
| Pattern | `orpheus/pattern/` | DBSCAN noise removal → GMM clustering on V/A/D space; weekly trend detection over 12-week lookback |
| Output | `orpheus/output/assemble.py` | Assembles JSON report with all window data, trends, clusters, and safety flags; logs a `pipeline_runs` row with config snapshot + SHA256 hash |

### Key design points

**Config** (`orpheus/config.py`) is a tree of dataclasses loaded from `config.yaml`. All tunable parameters live there — half-lives, engagement weights, clustering params, depth thresholds, model names, API keys. Validated at startup via `validate_config()`.

**Scoring keys** in `track_scores` are composite `(track_uri, model_version)` where `model_version = emotion_classifier + "+" + semantic_embedding`. This allows the table to hold scores across model generations without collisions.

**Engagement weighting** maps play behaviour to `[-0.5, 1.0]`: full play = 1.0, partial = 0.7, early skip = −0.5. These weights combine multiplicatively with exponential time-decay before aggregation, so recent skips can outweigh old full-plays.

**Window evidence span vs. decay** (`orpheus/aggregate/windows.py`): the mood mixture is decay-weighted by half-life (state 3-day, trait 90-day), but the *evidence* shown alongside it — the date range, frequency tracks, and coverage — spans a separate lookback. The trait window derives this from the half-life (`half_life × 4`), but the state ("Recent") window uses a fixed `RECENT_EVIDENCE_LOOKBACK_DAYS = 30` so the headline stays reactive to the last few days while the listening evidence reads as "the past month". Frequency tracks carry `emotion_scores`/`theme_scores` (attached regardless of decay weight) so the frontend renders the same mood chips as the influence view.

**Emotion categories** (8): `joyful_activation`, `triumphant_power`, `peacefulness`, `tenderness`, `nostalgia_longing`, `sadness_melancholy`, `tension_anxiety`, `anger_defiance` — derived from valence/arousal position.

**Theme categories** (8): `interpersonal_devotion`, `heartbreak_loss`, `adversity_resilience`, `identity_autonomy`, `status_ambition`, `hedonism_escape`, `place_heritage`, `existentialism_spirituality`.

**Safety module** (`orpheus/safety/rumination.py`) is opt-in (`config.safety.active: false`). It flags potential rumination when summed negative-valence emotions exceed a density threshold over a configurable duration.

### Database schema

Eight tables: `plays`, `tracks`, `audio_features`, `lyrics`, `track_scores`, `artists`, `pipeline_runs`, `schema_version`. See `orpheus/db/schema.sql` for full DDL and indexes.

### Testing

Tests avoid loading transformer models. The E2E test (`tests/test_pipeline_e2e.py`) inserts synthetic enrichment and scores directly into the DB, then exercises aggregation, clustering, trends, safety, and report assembly without any external API calls.

`tests/conftest.py` excludes `test_streamlit_app.py` and `test_navigation.py` from collection. Core fixtures: `tmp_project` (isolated dir + config), `tmp_config`, `tmp_db` (SQLite with schema applied), `sample_export_path` (→ `tests/fixtures/sample_export.json`).

Mark slow tests (transformer loading) with `@pytest.mark.slow`.
