# Candidate Audio Feature Sources

Status key: ✅ viable  ⚠️ uncertain  ❌ ruled out

---

## ❌ Spotify Web API — `/audio-features`
- **Status:** Deprecated November 2024. Returns 403 for all apps created after that date.
- **Resolution key:** Spotify URI (perfect match for our corpus)
- **Verdict:** Dead. Do not attempt.

---

## ❌ RapidAPI "track-analysis" (SoundNet)
- **Status:** Removed from codebase.
- **Why removed:** BASIC tier = 5 req/day. 4,243 tracks would take ~2.3 years.
  PREMIUM pricing not evaluated, but quota model is unsuitable for a one-time bulk import.
- **Verdict:** Ruled out.

---

## ✅ AcousticBrainz (bulk data dump)
- **What:** Community-contributed acoustic analysis for ~6M tracks, keyed by MusicBrainz ID (MBID).
- **Data:** Full Essentia feature vectors including valence, arousal, tempo, key, mode, BPM, spectral features.
- **Access:** Downloadable dataset at https://acousticbrainz.org/download
  (project in maintenance mode — data still available, no new submissions accepted since 2022)
- **Resolution path:** `track_uri` → `ISRC` → `MBID` via MusicBrainz lookup API or local mirror.
  - `tracks.isrc` and `tracks.mbid` columns exist in the schema but may be unpopulated.
  - Need to check: how many of 4,243 tracks have ISRC set in our DB?
- **Size:** ~500 GB full dump. High-level features only: ~50 GB.
- **Effort:** Medium — download dump, write an MBID-keyed lookup, run resolution.
- **Cost:** Free.
- **Risk:** MBID resolution may fail for ~30–40% of tracks. Project dormant.
- **Verdict:** Viable if MBID coverage is acceptable. Best free bulk path after Anna's Archive.

---

## ✅ Anna's Archive bulk cache
- **What:** The *intended* primary source in the current architecture. A local SQLite or
  CSV dump of audio features keyed by Spotify ID and/or ISRC.
- **Access:** Requires finding/obtaining the dump. The `orpheus archive import <path>`
  CLI command already exists and is ready to consume it.
- **Resolution path:** Direct `spotify_id` match in `ArchiveReader.lookup()` — highest
  resolution rate expected.
- **Effort:** Low once the dump is obtained (the import pipeline is built).
- **Cost:** Free (gray area legally; personal use).
- **Risk:** Source may be hard to locate; legality is gray area.
- **Verdict:** Preferred solution. Research needed: where to obtain the dump, what format
  it takes, and whether it matches the `ArchiveReader` expected schema.
  See `archive_lookup_spec.md` for the full schema contract.

---

## ⚠️ ReccoBeats API
- **What:** Commercial API exposing Spotify-style audio features (valence, energy,
  danceability, tempo, etc.) for tracks by ISRC.
- **Access:** https://reccobeats.com — free tier unclear; requires sign-up.
- **Resolution key:** ISRC (need ISRC population in our `tracks` table first).
- **Effort:** Low to medium — standard REST client, similar to the removed SoundNet client.
- **Cost:** Unknown free tier. Evaluate before committing.
- **Verdict:** Research needed. If free tier allows ~5K requests or more, viable as
  a one-time import via the `probe_api.py` test harness.

---

## ⚠️ Last.fm Audio Features / Tags
- **What:** Last.fm provides community tags and some acoustic signals per track.
- **Limitation:** Does not expose raw valence/arousal floats. Tag-based data would need
  mapping to V/A space — lossy and unreliable.
- **Verdict:** Unlikely to provide usable V/A values directly. Useful as a fallback for
  genre/mood tags only.

---

## ⚠️ Essentia local extraction
- **What:** Open-source audio analysis library. Produces all required fields.
- **Limitation:** Requires the actual audio file. Spotify does not provide audio.
  Only viable if the user has local MP3/FLAC files for the same tracks.
- **Verdict:** Ruled out for most users. Worth noting as an option if local files exist.

---

## ⚠️ Essentia-MusicExtractor via YouTube audio
- **What:** Fetch a 30s preview from YouTube Music / ytdl, run Essentia locally.
- **Limitation:** Legal gray area; slow (30s per track × 4K tracks = ~35 hours);
  requires ytdl + Essentia installed.
- **Verdict:** Last resort. Not recommended for primary path.

---

## Research questions to resolve

1. **Anna's Archive dump:** Does a Spotify-keyed audio feature dump exist? What is its
   format (SQLite / Parquet / CSV)? Where is it distributed?
2. **AcousticBrainz MBID coverage:** Run `SELECT COUNT(*) FROM tracks WHERE mbid IS NOT NULL`
   — if coverage is low, MBID resolution is needed before this source is viable.
3. **ReccoBeats free tier:** What are the rate limits and pricing? Is ISRC the only
   resolution key or does it also accept track name + artist?
4. **ISRC population:** `SELECT COUNT(*) FROM tracks WHERE isrc IS NOT NULL AND isrc != ''`
   — determines whether ISRC-keyed sources (AcousticBrainz, ReccoBeats) are immediately
   usable or require a Spotify metadata re-fetch first.
