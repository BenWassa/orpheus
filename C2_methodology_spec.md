# C2_methodology_spec.md
## Project Orpheus v2 — Analysis Methodology

### Purpose
Define the pipeline from raw listening data to user-facing pattern insights. This is the engine spec, not the UI spec. Output format is structured data (JSON), which the frontend will consume separately.

---

### Pipeline Overview

```
Raw listening data
      ↓
[1] Ingestion & cleaning
      ↓
[2] Per-track enrichment (audio features + lyrics)
      ↓
[3] Per-track scoring (emotion + theme + depth)
      ↓
[4] Time-weighted aggregation (parallel state + trait windows)
      ↓
[5] Pattern detection (clustering + trend analysis)
      ↓
[6] Output assembly (discrete user-facing conclusions)
```

Each stage runs independently and writes intermediate artifacts so individual stages can be re-run without reprocessing everything.

---

### 1. Data Sources and Ingestion

**Primary source: Spotify Extended Streaming History**
- Requested via Spotify Settings > Privacy > Download your data (extended version)
- Format: JSON files, one per year approximately
- Key fields: `ts` (ISO timestamp), `ms_played`, `master_metadata_track_name`, `master_metadata_album_artist_name`, `master_metadata_album_album_name`, `spotify_track_uri`, `reason_start`, `reason_end`, `shuffle`, `skipped`
- Provides: timestamps, skip data, completion rates, multi-year history

**Secondary source: Spotify Web API (live)**
- Top tracks and artists (short/medium/long term)
- Recently played
- Currently playing
- Saved tracks and library
- Purpose: supplements static export with up-to-the-minute state

**Enrichment sources (per track):**
- **Audio features**: SoundNet/SoundStat API (primary), Essentia on-prem (fallback for missing tracks)
- **Bulk audio features cache**: Anna's Archive 200GB SQLite dump (Nov 2025, 256M tracks) for offline pre-population
- **Lyrics**: Genius API (preferred for crowd annotations), MusixMatch as backup
- **Artist metadata**: Spotify Web API + MusicBrainz fallback

**Cleaning:**
- Filter out background-listening sessions (sleep playlists, white noise, study lo-fi) via DBSCAN noise classification (step 5)
- Resolve track identity to MBID or ISRC for cross-source consistency
- Tag plays under 30s for downweight, not exclusion (still data, but low confidence)
- De-duplicate within session if exact same track played in rapid succession (likely loop, count as engagement signal)

---

### 2. Per-track Enrichment

For each unique track identified in the listening history, fetch and cache:

| Layer | Source | Output |
|---|---|---|
| Acoustic | SoundNet / Essentia | Valence, Arousal, BPM, key, mode, energy, danceability, acousticness, spectral features |
| Lyrical | Genius API | Raw lyrics text + crowd annotations where available |
| Metadata | Spotify + MusicBrainz | Genre tags, release date, popularity, artist identity |

Cache aggressively. Audio features and lyrics don't change for a given track; pull once, store, reuse.

For tracks missing from SoundNet (rare with 6.7M+ catalog), fall back to Essentia local extraction. For tracks without lyrics (instrumental), flag and let the theme axis confidence drop accordingly.

---

### 3. Per-track Scoring

Each track produces a structured score object:

```json
{
  "track_id": "...",
  "emotion_scores": {
    "joyful_activation": 0.12,
    "triumphant_power": 0.08,
    "peacefulness": 0.04,
    "tenderness": 0.06,
    "nostalgia_longing": 0.31,
    "sadness_melancholy": 0.22,
    "tension_anxiety": 0.09,
    "anger_defiance": 0.08
  },
  "theme_scores": {
    "interpersonal_devotion": 0.05,
    "heartbreak_loss": 0.18,
    "adversity_resilience": 0.24,
    "identity_autonomy": 0.21,
    "status_ambition": 0.07,
    "hedonism_escape": 0.04,
    "place_heritage": 0.13,
    "existentialism_spirituality": 0.08
  },
  "depth_score": 0.62,
  "confidence": {
    "emotion": 0.81,
    "theme": 0.74,
    "depth": 0.69
  }
}
```

**Emotion scoring:**
1. Acoustic V/A coordinates from SoundNet/Essentia
2. Lyrical zero-shot classification via BART-large-MNLI over the 8 emotion categories
3. Late fusion with cross-modal attention: lyrical signal dominates negative-valence detection, acoustic dominates arousal
4. Output: probability distribution across all 8 categories; top 3 used downstream

**Theme scoring:**
1. Lyrics → s-VSM filter to extract sentiment-bearing units (removes chorus repetition noise)
2. MPNet embeddings (768-D semantic vectors) for the filtered text
3. Classifier over 8 theme categories with artist-level prior (Bayesian)
4. For instrumental tracks: rely on artist prior + acoustic-to-theme heuristic mapping (e.g., dark/minor/slow → existentialism prior)

**Depth scoring:**
Composite metric, 0-1 scale. Three input signals, equally weighted in v1:
- Acoustic complexity (Essentia structural variance)
- Lexical density (unique words / total words, weighted by syllable count)
- Topic coherence depth (hLDA tree position if available, else default)

Bucketed for output: 0.0-0.33 = surface, 0.34-0.66 = engaged, 0.67-1.0 = immersive.

**Why not use general LLMs (Claude, GPT-4o) for theme coding:**
R3 surfaced that general LLMs achieve 15-17% accuracy on surface-level music classification (era, culture) but drop to **0.88-1.5% accuracy on deep psychological theme classification**. Use specialized stack (BART-MNLI + MPNet + s-VSM) for theme work. General LLMs are fine for narrative generation in output assembly, not for classification.

---

### 4. Time-Weighted Aggregation

Two parallel windows run on the same per-track scores.

**Weight formula per play:**
```
W(t) = W_0 × exp(-λ × (t_now - t_play))
```
where `λ = ln(2) / T_half`.

**Engagement weight `W_0`:**

| Play event | W_0 |
|---|---|
| Full play (≥80% completion) | 1.0 |
| Played >30s but <80% | 0.7 |
| Skipped <30s | -0.5 |
| Skip within ±1.5s of structural boundary | -0.25 (mitigated) |
| Repeat play within same session | adds 0.3 stack (active engagement) |
| Shuffle source | -0.1 (less intentional) |
| Explicit replay or library play | +0.1 |

**Windows:**

| Window | T_half | Captures |
|---|---|---|
| State | 3 days | Active mood, current preoccupation |
| Trait | 90 days | Stable identity baseline |

**Artist vs track signal:**
- Primary artist credit: 1.0
- Featured artist credit: 0.3 (matches Spotify's logic)
- Artist-level aggregate computed in parallel to track-level for artist-as-prior layer

**Aggregate computation per category:**
```
category_score(c) = Σ over all plays p of [ W(p) × P(c | track of p) ]
```
Normalize across categories per window to produce ratios suitable for ranking and comparison.

---

### 5. Pattern Detection

**Clustering cascade per R3:**

Step A: **DBSCAN** on tracks in 3D AVD space.
- Parameters: ε tuned per user dataset density, MinPts = 5
- Purpose: isolate and filter outlier streams (background music, accidental plays, functional listening)
- Output: cleaned core dataset

Step B: **3-component Gaussian Mixture Model** on cleaned dataset.
- Soft probabilistic clustering
- Output: 3 primary clusters representing the user's dominant listening regions in AVD space
- Each track gets a probability distribution across clusters

**Temporal pattern detection:**
- Bin time-weighted scores into weekly buckets
- Per category, compute prevalence ratio per bucket
- Identify trends: rising (slope >0 over last 4 weeks), falling (slope <0), spiking (>25% deviation from trailing average), declining (steady downward)
- Co-occurrence analysis: which emotion x theme pairs appear together more than chance

**Comparison layer:**
- State vs Trait: which categories are elevated in state relative to trait baseline (the "going through something" signal)
- Recent vs Historical: month-over-month deltas

---

### 6. Output Assembly

The analysis engine produces a structured JSON output. The frontend will render it; voice rules from T1 apply when content is presented to user.

**Output schema (v1):**

```json
{
  "generated_at": "ISO timestamp",
  "windows": {
    "state": {
      "top_emotions": [
        {"category": "nostalgia_longing", "prevalence": "high"},
        {"category": "sadness_melancholy", "prevalence": "moderate"},
        {"category": "tenderness", "prevalence": "moderate"}
      ],
      "top_themes": [...same shape...],
      "depth_label": "engaged",
      "top_artists": [...],
      "top_tracks": [...]
    },
    "trait": {...same shape...}
  },
  "shifts": [
    {
      "category": "anger_defiance",
      "axis": "emotion",
      "direction": "falling",
      "magnitude": "notable",
      "narrative": "Anger and defiance recurred heavily across your long-term listening but have faded in the last few weeks."
    }
  ],
  "co_occurrences": [
    {
      "pair": ["nostalgia_longing", "heartbreak_loss"],
      "strength": "strong",
      "narrative": "Longing and heartbreak appear together more often than separately in your current listening."
    }
  ],
  "clusters": [
    {
      "label": "introspective core",
      "centroid_avd": [0.2, -0.4, 0.7],
      "dominant_emotions": ["nostalgia_longing", "sadness_melancholy"],
      "dominant_themes": ["heartbreak_loss", "identity_autonomy"],
      "share_of_listening": "approximately 40%"
    }
  ],
  "safety_flags": []
}
```

**Prevalence labels (no numbers in user-facing text):**

| Internal score range | User-facing label |
|---|---|
| > 0.25 normalized | dominant |
| 0.15 - 0.25 | high |
| 0.08 - 0.15 | moderate |
| 0.03 - 0.08 | present |
| < 0.03 | not represented |

**Narrative phrasing rules (per T1 voice):**
- Subject is the music, not the person
- Observational verbs: cluster, recur, dominate, co-occur, intensify, fade
- Selective quantification: "roughly a third", "more often than not"
- No causation claims, no diagnoses, no second-guessing the listener

---

### 7. Safety Hook (architecture present, inactive for MVP)

Module exists in pipeline but feature-flagged off until friend-test phase.

**Trigger conditions (when active):**
- State window shows sustained density (>48 hours) in negative-valence + high-depth quadrant (V ≤ 0.3, D ≥ 0.7)
- No trajectory toward higher-valence or comforting tracks in the same window
- Threshold confirmed across at least 20 distinct plays (avoids tripping on a single album)

**Action (when active):**
- Add entry to `safety_flags` in output
- Add gentle counterweight to output narrative (e.g., surfacing comforting tracks the user has historically returned to)
- No alarm, no diagnosis, no resource directory pushed unsolicited

For MVP (personal use only), this module compiles but does not write to output.

---

### 8. Implementation Notes

**Stack recommendation (subject to revision in C3 data pipeline spec):**
- Python 3.11+ for the analysis engine (pandas, scikit-learn for DBSCAN/GMM, transformers for BART/MPNet)
- SoundNet/SoundStat API client
- Essentia local extractor as fallback (Docker container for portability)
- SQLite for cached track scores and audio features (lightweight, file-based, no server)
- JSON output to disk, consumed by frontend separately
- No web framework in the engine layer. Engine is a CLI tool or scriptable module.

**Frontend (deferred to a later component):**
- React + TypeScript expected
- Consumes the JSON output from the engine
- Renders 2D Valence-Arousal scatter with Depth as label
- Timeline view with category prevalence over time
- Discrete narrative blocks driven by the `narrative` fields in output JSON

---

### 9. Open Questions for C3 and Beyond

- Cadence: does the engine run on demand or on a schedule? Personal use says on demand.
- Storage: where does the cache and history live? Local SQLite is the simplest answer.
- Onboarding: how does a user get from "I requested my Spotify data" to "I have results"? UX flow needs designing.
- Cost: SoundNet API has paid usage. Worth pricing the cost of analyzing a typical user's library (probably under $5 one-time per user).
- Reproducibility: same data should always produce same scores. Pin model versions, document seed handling.
