# Orpheus Audio-Features Sourcing: Best Free Path in 2026

## TL;DR

- **Best free path: a hybrid of two free sources.** Use a **pre-deprecation static Spotify audio-features dataset on Kaggle** (e.g. *Spotify 1.2M+ Songs* by rodolfofigueroa, keyed by the 22-char Spotify track ID, with both `valence` and `energy` plus the full feature panel) as the bulk backbone loaded via `orpheus archive import`, and fill the gaps with the **free ReccoBeats API** (`GET /v1/audio-features?ids=<spotify_ids>`), which returns Spotify-style `valence`, `energy`, `danceability`, `tempo`, `acousticness`, `instrumentalness`, `loudness`, `liveness`, `speechiness` and accepts Spotify track IDs directly. Both are free; combined they should clear the ≥1,000-row success bar comfortably and likely cover the large majority of 4,243 mainstream tracks.
- **"Arousal" is not a Spotify field and no free per-track API returns it.** Spotify's model exposes `valence` but never "arousal." The pragmatic, well-precedented move is to **derive arousal ≈ energy** (the music-emotion-recognition literature treats energy/tempo/loudness as the arousal axis), populating `audio_features.arousal` from `energy`. True annotated valence/arousal datasets (DEAM, MusAV, Deezer) exist but are tiny (≈2,000 tracks) and keyed by non-Spotify IDs, so they are unsuitable as your primary source.
- **Spotify's own `/audio-features` and `/audio-analysis` remain dead for new apps (403), but metadata endpoints — including ISRC — are alive.** As of the March 2026 changelog, `GET /v1/tracks/{id}` still returns `external_ids.isrc` (it was briefly removed in Feb 2026 then reverted). So your planned one-time re-fetch for ISRC works, but for this project you don't actually need ISRC: every good free source keys on the **Spotify track ID** you already hold in `track_uri`.

## Spotify API Status in 2026 (Confirmed)

**1. Spotify `/audio-features` is permanently off-limits for your app, and so is `/audio-analysis`.** Spotify's November 27, 2024 Web API change blocked `/v1/audio-features`, `/v1/audio-analysis`, `/recommendations`, related-artists, audio previews and several other endpoints for any app without a pre-existing extended-mode quota. Spotify staff confirm new apps get HTTP 403 with no appeal path. As one developer summarized after testing both endpoints: "It seems that both audio-features and audio-analysis are deprecated." There is **no legitimate way** for a freshly-created app to access these. Do not design around them.

**2. Spotify metadata endpoints still work — and ISRC is back.** `GET /v1/tracks/{id}` (single track) remains available and returns `external_ids.isrc`. There was a scare in the **February 2026 dev-mode migration**, which listed `external_ids` as `[REMOVED]` from the track object — but the same changelog annotates it "**Reverted — See March 2026 changelog**," and ISRC is again returned. Three important catches from the Feb/Mar 2026 migration that affect any re-fetch script: (a) the **batch** `GET /v1/tracks?ids=` ("Get Several Tracks") was removed for dev-mode apps — you must fetch tracks **individually**; (b) **search results are now capped at 10 per request** (paginate via `offset`); and (c) dev-mode apps now effectively require a **Spotify Premium** account and a loopback redirect on `127.0.0.1` (not `localhost`). Net: you *can* re-fetch ISRC one track at a time, but for this project ISRC is optional — your `track_uri` already contains the Spotify track ID, which is the key the best free sources use.

**3. The deprecation created a wave of replacements — most are unreliable; ReccoBeats is the standout free one.** Paid "Spotify Extended API" resellers (e.g. Musicae on Medium, various RapidAPI "Track Analysis" listings) advertise restored audio-features access but are commercial, unofficial, and of uncertain longevity. Among free options, **ReccoBeats** is the one repeatedly recommended by developers and actually integrated into real tools (the `spotifyr-reccobeats-R` project, the *lewisdoesdata* hip-hop tutorial, and the MediaMonkey `MMAudioFeatures` addon).

## Source-by-Source Evaluation

### A. ReccoBeats API — leading free *live* option (alive, actively maintained)

- **Status (2026):** Alive and actively maintained by "LatteBits"; docs carry a 2025 copyright and a changelog. Funded via Ko-fi donations, explicitly marketed as a free Spotify-audio-features replacement. The creator states it is "completely free."
- **Fields returned:** The track audio-features endpoint returns the Spotify-style panel: `acousticness`, `danceability`, `energy`, `instrumentalness`, `liveness`, `loudness`, `speechiness`, `tempo`, `valence`. Confirmed by a documented JSON example (`{"acousticness":0.174, "danceability":0.4004, "energy":0.6899, "instrumentalness":0.0309, "liveness":0.1188, "loudness":-6.0411, "speechiness":0.0566, "tempo":147.7849, "valence":0.2747}`). **Includes `valence` and `energy`** ✓. Does **not** include "arousal", `key`, or `mode` on the by-ID endpoint, and does not return Spotify's `time_signature`.
- **Resolution key — excellent match:** The batch endpoint `GET https://api.reccobeats.com/v1/audio-features?ids=<comma-separated Spotify track IDs>` accepts **Spotify track IDs directly** — exactly the key embedded in your `track_uri`. (Subtlety documented by integrators: responses identify each track by a ReccoBeats internal UUID and a `href` that contains the original Spotify track ID, e.g. `https://open.spotify.com/track/<id>`; map back to your URIs via that `href`.) It can also extract features from an uploaded ≤30s audio file, but that path is irrelevant for you.
- **Coverage:** "Database of over millions" of tracks. Real-world integrations report it as a working drop-in for the dead Spotify endpoint, though obscure/niche tracks miss. Expect strong coverage on mainstream catalog and partial misses on the long tail.
- **Cost / rate limits:** Free, no API key/sign-up required for the read endpoints. Rate limits exist but are **not numerically published** ("configured internally"; exceeding returns `429 Too Many Requests` with a `Retry-After` header). Practitioners report a **batch ceiling around ~40 IDs per request** and throttle with **~0.5 s between calls**; one used a conservative **5 IDs/request** "method that always works." For 4,243 tracks at ~40 IDs/request that's ~106 requests; at 5 IDs/request ~849 requests — both finish in minutes with polite delays.
- **Accuracy caveat:** ReccoBeats values are *not* guaranteed to be Spotify's original numbers; they are its own database/model estimates of the same descriptors. Good enough for GMM clustering, but treat as approximate.
- **Effort to integrate:** Low. Fits your **live per-track fallback client** architecture (option B) as a new module `orpheus/enrich/reccobeats.py`, or can be run once to **build a SQLite db** for `orpheus archive import` (option A — preferred per your success criteria of "no ongoing per-report API dependency").

### B. Static pre-deprecation Spotify datasets (Kaggle/Hugging Face) — leading free *bulk* option

These are CSV/Parquet dumps scraped from Spotify's `/audio-features` endpoint **before** the Nov 2024 deprecation, now shared as research datasets. They are keyed by **Spotify track ID** and contain `valence` + `energy` + the full panel — i.e., they drop straight into an `audio_features` table for `orpheus archive import`, with **zero ongoing API dependency**. The two largest, vetted candidates:

- **"Spotify 1.2M+ Songs" (rodolfofigueroa)** — single CSV `tracks_features.csv`, ~1.2M tracks, **24 columns**. Verbatim columns include `id` (the 22-char Spotify track ID), `name`, `album`, `album_id`, `artists`, `artist_ids`, `track_number`, `disc_number`, `explicit`, `danceability`, `energy`, `key`, `loudness`, `mode`, `speechiness`, `acousticness`, `instrumentalness`, `liveness`, `valence`, `tempo`, `duration_ms`, `time_signature`, `year`, `release_date`. **Both `valence` and `energy` present, plus every optional field you listed except spectral_centroid/spectral_complexity** (no source returns spectral features without local extraction). Spans a wide historical range (early-1900s–2020), so good for older catalog. No `genre`/`popularity` columns. License is **unconfirmed on the data card — verify before redistributing**; using it locally for personal analysis is the low-risk use. (Order-of-magnitude size: a few hundred MB uncompressed; confirm on the data card.)
- **"Spotify_1Million_Tracks" (amitanshjoshi)** — single CSV, **1,159,764 tracks (exact)**, **20 columns**: `artist_name`, `track_name`, `track_id` (Spotify ID), `popularity`, `year`, `genre`, `danceability`, `energy`, `key`, `loudness`, `mode`, `speechiness`, `acousticness`, `instrumentalness`, `liveness`, `valence`, `tempo`, `duration_ms`, `time_signature`. Adds `genre`/`popularity` but is **restricted to 2000–2023**, so it misses pre-2000 tracks. License also unconfirmed on the data card.
- Smaller, cleaner option: **maharshipandya/spotify-tracks-dataset** (114,000 tracks, 20 cols, on both Kaggle and Hugging Face, documented as **CC0** on at least one mirror) — same feature set keyed by `track_id`; good for a quick, clearly-licensed pilot but lower coverage of a personal library.

**Coverage reality:** A personal listening history of 4,243 tracks that is mostly mainstream should match a large share against a 1.2M-track table on exact Spotify-ID join; niche/very-new/regional tracks will miss. The 1.2M historical dataset (rodolfofigueroa) is the better single choice for breadth; combine with ReccoBeats to recover misses.

### C. AcousticBrainz bulk dump — viable but high-friction, weak personal-library coverage

- **Status (2026):** **Discontinued / maintenance mode.** No new submissions since the project halted collection (~2022), but historical dumps remain downloadable from `acousticbrainz.org/download`. Organized by **MusicBrainz Recording ID (MBID)**, not Spotify ID.
- **Does it have valence/arousal?** Not as named 0–1 fields. Its Essentia **high-level** models output mood/danceability **probabilities** (`mood_happy`, `mood_sad`, `mood_aggressive`, `mood_acoustic`, `mood_party`, `mood_electronic`, `danceability`, `voice_instrumental`, `tonal_atonal`, plus `moods_mirex`). You'd have to *derive* a valence/arousal proxy (e.g. valence ≈ mood_happy − mood_sad), which is lossy and not comparable to Spotify's valence. The AcousticBrainz authors themselves flagged that high-level model reliability "is under doubt."
- **Resolution chain is the killer:** Spotify URI → ISRC (via `/v1/tracks/{id}`) → MBID (via MusicBrainz API, rate-limited to **1 request/second**) → AcousticBrainz lookup. For 4,243 tracks that's ~70+ minutes just for the MBID step, with significant drop-off because ISRC→MBID mapping is incomplete and AcousticBrainz's per-track coverage of a typical personal library (especially recent or non-Western pop) is patchy.
- **Verdict:** Only worth it if you specifically want Essentia mood/genre/key data and are willing to build the MBID bridge. Not the fastest route to `clusters_status: ok`.

### D. Essentia local extraction (incl. pretrained valence/arousal models) — best *true* valence/arousal, but needs audio

- **Status:** Fully alive and maintained (MTG/UPF). Essentia ships **pretrained TensorFlow models that directly regress arousal and valence on the DEAM dataset** (2-D output, range [1,9]) — e.g. `deam-msd-musicnn-2.pb` on MusiCNN embeddings. This is the only option here that yields *genuine* arousal. Models are CC BY-NC-SA 4.0 (non-commercial — fine for a personal project).
- **Catch:** Requires the **actual audio files**, which you don't have. The "YouTube/ytdl 30s preview → Essentia" path is a legal gray area, slow (per-track download + inference), and brittle. ReccoBeats' upload endpoint internally does something similar but spares you the infrastructure.
- **Verdict:** Last resort. Note it for a future "true VA" upgrade, not the immediate goal.

### E. Last.fm — not useful for raw valence/arousal (confirmed)

Last.fm exposes **tags and listener stats**, not numeric `valence`/`energy`/`danceability`. Useful only as mood-*tag* metadata (e.g. "happy", "chill"), which would need its own tag→VA mapping. Not a substitute for audio features.

### F. Other APIs checked — none beat free ReccoBeats for your need

- **GetSongBPM / Tunebat / Songstats / Soundcharts / Musixmatch / Cyanite.ai:** mostly BPM+key only, or paid/enterprise, or chart/streaming-stats focused. None offer a free tier returning `valence`+`energy` keyed by Spotify ID at 4K scale. **Cyanite.ai** has rich mood/VA-like analysis but is a paid B2B product; **Musixmatch** is lyrics-centric. None displace ReccoBeats.
- **Consumer apps (e.g. "Orphea")** infer features with an LLM/heuristic model ("typically within 0.1 of ground truth for well-known tracks") — useful as validation of the "approximate features are fine for clustering" thesis, but they're apps, not bulk-importable data.
- **Million Song Dataset / Deezer mood dataset / DEAM / MusAV:** academic VA resources but small (DEAM ≈1,802; MusAV ≈2,092; Deezer keyed by Deezer/MSD IDs) and **not keyed by Spotify ID**, so impractical as your primary table. MusAV and Deezer are the right references if you later want to *train* your own VA model.

## Decision Matrix

The decision turns on your ranked criteria: (1) coverage, (2) free, (3) low effort, (4) maintained.

| Source | Status 2026 | valence | arousal | Key | Est. coverage of 4,243 | Cost | Effort | Maintained |
|---|---|---|---|---|---|---|---|---|
| **Static Kaggle dataset (1.2M)** | static dump | ✓ | ✗ (derive from energy) | **Spotify track ID** | High for mainstream; misses niche/new | Free | **Lowest** (one CSV → SQLite → import) | n/a (frozen) |
| **ReccoBeats API** | **alive, maintained** | ✓ | ✗ (derive from energy) | **Spotify track ID** | High mainstream; some misses | Free | Low (1 client module) | Yes |
| AcousticBrainz dump | discontinued, downloadable | ✗ (derive from moods) | ✗ (derive) | MBID (needs ISRC→MBID) | Low–moderate for personal lib | Free | High (resolution chain) | No |
| Essentia + audio | alive | ✓ (model) | **✓ (DEAM model)** | local files | depends on having audio | Free | Very high (need audio) | Yes |
| Last.fm | alive | ✗ | ✗ | name/MBID | n/a (tags only) | Free | n/a | Yes |
| Paid resellers (Musicae etc.) | alive | ✓ | ✗ | Spotify ID | High | **Paid** | Low | Uncertain |

**Why the hybrid wins:** No single free source maximizes both coverage and effort. The static 1.2M dataset gives you the largest one-shot, zero-API-dependency match on the exact key you already have (Spotify track ID) — directly satisfying "no ongoing per-report API dependency" and "one-time import strongly preferred." ReccoBeats then mops up the long-tail misses live, and is also free and Spotify-ID-keyed. Together they should put `audio_features` row count far above the 1,000-row threshold and flip `clusters_status` to `ok`. Paid options (Musicae, RapidAPI resellers) do **not** dramatically outperform this for a personal 4K corpus, so paid is not justified.

## Recommendations

**Stage 0 — Extract your Spotify track IDs (no API needed).** Your `track_uri` values are of the form `spotify:track:<22-char-id>`. Parse the trailing ID into a `spotify_id` column. This is the join key for both primary sources. (You do **not** need the ISRC/Spotify re-fetch for the recommended path; keep it only as an optional enhancement — see Stage 3.)

**Stage 1 — Bulk import from the static 1.2M dataset (do this first; biggest, fastest win).**
1. Download *Spotify 1.2M+ Songs* (`tracks_features.csv`, rodolfofigueroa) for breadth, or start with the clearly-CC0 `maharshipandya/spotify-tracks-dataset` for a licensing-clean pilot.
2. Build a SQLite db with an `audio_features` table whose schema matches what `ArchiveReader.lookup(track_uri, isrc)` expects. Map columns: dataset `id`/`track_id` → `spotify_id`; copy `valence, energy, danceability, tempo, acousticness, instrumentalness, loudness, key, mode`. **Populate `arousal := energy`** (document this as a deliberate proxy). Leave `spectral_centroid`/`spectral_complexity` NULL (no free source provides them; they're optional and your GMM can run without them).
3. Run `orpheus archive import <path-to-sqlite>`. 
4. **Benchmark:** check `audio_features` row count and the % of your 4,243 tracks now matched. If matched rows ≥ ~1,000 (success threshold) and `clusters_status` flips to `ok`, you may stop here.

**Stage 2 — Fill gaps with ReccoBeats (only the unmatched track IDs).**
1. Add `orpheus/enrich/reccobeats.py`: a client that batches unmatched `spotify_id`s into `GET https://api.reccobeats.com/v1/audio-features?ids=<…>`. Use **≤40 IDs per request** (start conservative at ~20–40), sleep **~0.5 s** between calls, and on HTTP 429 honor the `Retry-After` header.
2. Parse each result, recover the Spotify ID from the response `href` (strip `https://open.spotify.com/track/`), and upsert into the same `audio_features` table (again setting `arousal := energy`). 
3. Wire this as the `ArchiveReader.lookup` fallback (option B) **or** run it once to extend the SQLite db and re-`archive import` (option A — preferred to avoid per-report API calls).

**Stage 3 — Optional ISRC enhancement (only if you want it).** If you later want ISRC for cross-referencing or MusicBrainz/AcousticBrainz, run a one-time re-fetch with `GET /v1/tracks/{id}` **one track at a time** (batch tracks endpoint is gone for dev-mode apps), read `external_ids.isrc`, and store it in your existing `isrc`/MBID columns. Requires a Premium dev-mode app with a `127.0.0.1` loopback redirect.

**Benchmarks / thresholds that should change the plan:**
- If Stage 1 match rate is **< 25%** (your library is niche/recent), lean harder on ReccoBeats in Stage 2 and consider adding the 2000–2023 `amitanshjoshi` dataset for newer pop.
- If combined coverage after Stages 1–2 is still **< 1,000 rows**, your corpus is genuinely long-tail: escalate to Essentia-on-previews (Stage D) for the residual, accepting the legal/effort cost — this is the only remaining free way to get features for tracks absent from every database.
- If you ever need **true arousal** (not energy-as-proxy) for research validity, switch the arousal source to Essentia's `deam-msd-musicnn` model on local/preview audio; until then, keep `arousal = energy` and label it as such in your data dictionary.

## Caveats

- **"Arousal" is synthesized, not measured.** Every free Spotify-compatible source lacks a true arousal field; the recommended `arousal := energy` (optionally blended with tempo/loudness) is a standard MER proxy but is an approximation. Document it so downstream interpretation of clusters isn't over-read. The only genuine VA source here is Essentia's DEAM model, which needs audio you don't have.
- **ReccoBeats numbers are estimates, not Spotify's originals.** They reproduce Spotify's *schema* and are widely used as a drop-in, but values may differ from the historical Spotify API. For GMM clustering this is acceptable; for any claim of "Spotify's official valence," it is not.
- **Mixing two sources introduces a consistency risk.** Static-dataset values (real pre-2024 Spotify numbers) and ReccoBeats values (model estimates) live on slightly different scales. For cleaner clusters, prefer the static dataset where both have a track, use ReccoBeats only for gaps, and consider a `source` column in `audio_features` so you can later normalize or audit.
- **Licensing is unconfirmed for the two largest Kaggle datasets.** rodolfofigueroa (1.2M) and amitanshjoshi (1M) did not have a verifiable license on their data cards in this research — confirm before redistributing. Personal, local analysis is low-risk; publishing the derived table is not. The 114k `maharshipandya` set is documented CC0 on at least one mirror and is the safest if licensing matters. Avoid any pirated/illicitly-scraped sources entirely.
- **Spotify dev-mode terms tightened again in Feb/Mar 2026.** Batch `/tracks`, artist top-tracks, several browse/contains endpoints were removed; search is capped at 10/request; Premium + loopback-IP redirect are now effectively required. These only matter if you pursue the optional ISRC re-fetch; the core recommended path avoids the Spotify API entirely.
- **Coverage of a personal library is genuinely uncertain.** Public "millions of tracks" claims don't translate to a guaranteed match rate for *your* specific 4,243 tracks. The Stage-1 benchmark (match %) is the real test — treat the staged plan as adaptive, driven by that measured number rather than the headline catalog sizes.
- **Spectral features are unavailable for free at scale.** `spectral_centroid`/`spectral_complexity` require local audio analysis (Essentia). Treat them as optional/NULL; they are not needed for the minimum-viable valence+arousal clustering.