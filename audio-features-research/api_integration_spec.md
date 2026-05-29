# Live API Integration Spec

Use this if the bulk-import path (Anna's Archive / AcousticBrainz) doesn't pan out and
you need to wire in a live per-track API.

---

## Integration point

File: `orpheus/enrich/enrich.py`

The relevant section (simplified):

```python
# Current: only tries archive lookup
features = archive_reader.lookup(track_uri=row["track_uri"], isrc=row["isrc"])

# After wiring a live API fallback:
features = archive_reader.lookup(track_uri=row["track_uri"], isrc=row["isrc"])
if features is None:
    features = live_api_client.lookup(track_uri=row["track_uri"], isrc=row["isrc"])
```

A new client module would live at `orpheus/enrich/<source_name>.py` and expose:

```python
class <SourceName>Client:
    def __init__(self, api_key: str): ...
    def lookup(self, track_uri: str | None, isrc: str | None) -> dict | None:
        """Returns a dict matching audio_features schema, or None if not found."""
```

---

## Required output schema

```python
{
    "valence": float,           # 0.0–1.0, REQUIRED for clustering
    "arousal": float,           # 0.0–1.0, REQUIRED for clustering
    "tempo": float | None,
    "key": int | None,          # 0–11
    "mode": int | None,         # 0=minor, 1=major
    "energy": float | None,
    "danceability": float | None,
    "acousticness": float | None,
    "instrumentalness": float | None,
    "loudness": float | None,
    "spectral_centroid": float | None,
    "spectral_complexity": float | None,
    "source": str,              # e.g. "reccobeats"
}
```

---

## Config wiring

Add to `config.yaml`:

```yaml
audio_features:
  sources:
    - type: archive
      db_path: data/cache/archive_audio.db   # existing path
    - type: reccobeats                        # new
      api_key: "YOUR_KEY"
      rate_limit_per_second: 5
```

And in `orpheus/config.py`, a corresponding dataclass:

```python
@dataclass
class AudioFeatureSourceConfig:
    type: str
    db_path: str | None = None
    api_key: str | None = None
    rate_limit_per_second: int = 5
```

---

## Rate limiting considerations

Corpus: 4,243 tracks. If doing a one-time import:

| Rate limit | Time for full corpus |
|-----------|---------------------|
| 5 req/s   | ~14 minutes         |
| 1 req/s   | ~71 minutes         |
| 1 req/min | ~70 hours           |
| 5 req/day | ~2.3 years (useless)|

Anything ≥ 1 req/s is acceptable for a one-time run. After initial population,
the cache means the API is never called again for the same track.

---

## Error handling (matches existing pattern)

```python
# 429 → exponential backoff, max 5 retries
# 4xx (not 429) → log, mark enrichment_failed=True, skip
# 5xx → backoff + retry
# None response → treat as miss, proceed without audio features
```

This is already implemented in `enrich.py` — the new client just needs to raise
`requests.HTTPError` on non-200 responses and the existing retry logic handles it.
