# Enrichment API Notes

## ReccoBeats audio features

`orpheus.enrich.reccobeats.ReccoBeatsClient` calls:

```text
https://api.reccobeats.com/v1/audio-features?ids=<spotify_id,...>
```

The endpoint is keyless and returns Spotify-style audio features. Orpheus maps
`energy` to `arousal`, so a useful response must include at least `valence` and
`energy`.

## Operational policy

- Use `orpheus archive fill-gaps` instead of calling the client directly.
- Start with a limited probe before any large fill because track IDs are sent to
  a third-party API.
- Keep batch sizes small. The working probe used `--batch-size 5`.
- Keep a delay between batches. The working probe used `--delay 3`.
- Re-run safely: existing rows in `audio_features` are skipped by the SQL query.
- On HTTP 429, the client honors `Retry-After`; if the header is missing, it
  waits 5 seconds and retries up to 3 times.

## Known probe results

Initial local probes on 2026-05-29:

```text
limit 5, batch-size 1, delay 2:
  fetched   4
  not_found 1
  errors    0

limit 100, batch-size 5, delay 3:
  fetched   88
  not_found 12
  errors    0
```

After the 100-track run, the local database had 92 ReccoBeats rows and 4,151
tracks still missing audio features.

## Recommended commands

Small smoke test:

```bash
.venv/bin/orpheus archive fill-gaps --limit 10 --batch-size 1 --delay 2
```

Conservative larger batch:

```bash
.venv/bin/orpheus archive fill-gaps --limit 500 --batch-size 5 --delay 3
```

Check coverage:

```bash
.venv/bin/orpheus status
```
