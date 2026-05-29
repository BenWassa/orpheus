# Problem Statement

## What's broken

`orpheus/pattern/cluster.py` loads V/A/D coordinates for each track by joining
`track_scores` with `audio_features`. Currently `audio_features` has **0 rows** against
a corpus of **4,243 tracks**. Every report outputs:

```json
"clusters": [],
"clusters_status": "no_audio_features"
```

The clustering section of the frontend (`frontend/src/components/ClusterList.tsx`) renders
nothing — a blank panel with an explanatory message.

## Why it's empty

Timeline of attempts:
- **Spotify Web API** — `/audio-features` endpoint deprecated November 2024. Dead.
- **RapidAPI "track-analysis" (SoundNet)** — BASIC tier: 5 requests/day. Unusable for
  4K tracks. Removed from codebase (see commit `cd62bba`).
- **Anna's Archive bulk cache** — the *intended* solution. Requires a local dump file.
  No dump has been imported yet. Code for it exists (`orpheus/enrich/archive_lookup.py`,
  `orpheus archive import <path>`).

## Corpus size

```
tracks total:          4,243
audio_features rows:       0     ← the gap
track_scores rows:       550     (scored from lyrics only, no acoustic fusion)
```

## What the pipeline needs

Minimum: `valence` (0–1), `arousal` (0–1), `depth_score` already comes from scoring.
Full schema (see `docs/C3_data_pipeline_spec.md` §2 `audio_features` table):

```
valence REAL        -- 0.0 (negative) to 1.0 (positive)
arousal REAL        -- 0.0 (calm) to 1.0 (energetic)
tempo REAL          -- BPM
key INTEGER         -- 0–11 (pitch class)
mode INTEGER        -- 0 = minor, 1 = major
energy REAL         -- 0.0–1.0
danceability REAL   -- 0.0–1.0
acousticness REAL   -- 0.0–1.0
instrumentalness REAL
loudness REAL       -- dB, typically -60 to 0
spectral_centroid REAL
spectral_complexity REAL
```

Valence and arousal are the only fields strictly required for clustering. The rest improve
the emotion-model acoustic fusion layer.

## Integration point

The `enrich` step calls `ArchiveReader.lookup(track_uri, isrc)` from
`orpheus/enrich/archive_lookup.py`. If that returns `None` the track gets no audio
features. Wiring a new source means either:
- **Option A (bulk import):** Pre-populate the `audio_features` table once via
  `orpheus archive import <path>` before running `enrich`.
- **Option B (live API):** Add a fallback client in `enrich.py` that's called when
  `ArchiveReader.lookup` returns `None`.

## Success criteria

- `audio_features` row count ≥ 1,000 (covers most played tracks)
- `clusters_status` = `"ok"` in the next report
- No ongoing per-report API dependency (one-time import preferred)
- Cost: free or negligible for personal use scale
