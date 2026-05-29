# Anna's Archive Bulk Cache — Spec

This is the preferred path. The import pipeline is already built; only the source data file
is missing.

---

## What the existing code expects

`orpheus/enrich/archive_lookup.py` → `ArchiveReader` opens a SQLite database and queries:

```python
# By Spotify ID (stripped from track_uri)
"SELECT * FROM audio_features WHERE spotify_id = ? OR track_id = ?"

# By ISRC
"SELECT * FROM audio_features WHERE isrc = ?"
```

So the dump database must have a table called `audio_features` with at minimum:

| Column | Type | Notes |
|--------|------|-------|
| `spotify_id` | TEXT | Spotify track ID (22-char alphanumeric, no `spotify:track:` prefix) |
| `track_id` | TEXT | Alias — same value or alternative ID |
| `isrc` | TEXT | Optional but useful fallback |
| `valence` | REAL | 0.0–1.0 |
| `arousal` | REAL | 0.0–1.0 (may be stored as `energy` — see `_row_to_dict`) |
| `energy` | REAL | Used as arousal proxy if `arousal` is absent |
| `tempo` | REAL | BPM |

The `_row_to_dict` method handles the `arousal`/`energy` fallback:
```python
"arousal": cols.get("arousal", cols.get("energy")),
```

---

## CLI import command

```bash
orpheus archive import /path/to/archive_audio_features.db
```

Implemented in `orpheus/cli.py` → calls `ArchiveReader` then bulk-inserts rows into the
project's `data/cache/orpheus.db` `audio_features` table.

---

## What to research

1. **Does a Spotify-keyed audio features SQLite dump exist in Anna's Archive?**
   - Search terms: "spotify audio features dataset", "spotify valence arousal dump"
   - The archive at https://annas-archive.org may have a music metadata dataset

2. **Alternative: AcousticBrainz bulk export**
   - Dataset at: https://acousticbrainz.org/download
   - Fields include `valence`, `arousal` (MoodStrands model), tempo, key, mode
   - Keyed by MBID, not Spotify ID — requires a resolution step
   - Resolution: Spotify URI → ISRC (via Spotify API) → MBID (via MusicBrainz API)
   - Our corpus currently has 0 ISRC and 0 MBID rows, so this requires enriching the
     `tracks` table first with a Spotify metadata re-fetch

3. **Format alternatives accepted by ArchiveReader**
   - Currently only reads SQLite. If the source is CSV/Parquet/JSON, a small conversion
     script is needed, or `ArchiveReader` needs a new adapter.

---

## Schema mapping template

If you find a source with different column names, this is the mapping target:

```python
# In ArchiveReader._row_to_dict(), map source columns → Orpheus fields:
{
    "valence":            cols.get("valence"),           # or "danceability_proxy"
    "arousal":            cols.get("arousal") or cols.get("energy"),
    "tempo":              cols.get("tempo") or cols.get("bpm"),
    "key":                cols.get("key") or cols.get("pitch_class"),
    "mode":               cols.get("mode"),              # 0=minor, 1=major
    "energy":             cols.get("energy"),
    "danceability":       cols.get("danceability"),
    "acousticness":       cols.get("acousticness"),
    "instrumentalness":   cols.get("instrumentalness"),
    "loudness":           cols.get("loudness"),
    "spectral_centroid":  cols.get("spectral_centroid"),
    "spectral_complexity":cols.get("spectral_complexity"),
}
```

---

## Minimum viable result

A file (any format) where each row contains:
- a Spotify track ID **or** ISRC
- `valence` (0–1) and at least one of `arousal`/`energy` (0–1)

covering a reasonable fraction of popular tracks (Spotify top-streamed catalog coverage
should hit ~60–80% of a typical listening history).
