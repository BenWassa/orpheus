# Orpheus — Data & Logic Review + Improvement Sprints

_Reviewed 2026-05-29 against the live DB (`data/cache/orpheus.db`), the pipeline
(`orpheus/`), and the frontend (`frontend/src/`). Report sampled:
`data/output/reports/20260529T153602.json`._

The goal of this document is twofold: (1) establish whether the data and logic
are **reasonable and coherent**, and (2) lay out a sequenced set of sprints that
fix the gaps and borrow the best of Spotify Wrapped — **without** turning the
"letter about yourself" into a corporate dashboard (see `PRODUCT.md`).

---

## 1. Verdict

The pipeline architecture is sound and the code is clean. But the **report
currently overstates its own confidence**: it renders decisive narratives
("Your recent listening circles around…") on top of a small, non-representative
slice of the actual listening data, and labels several derived axes in ways the
underlying numbers don't support.

Three issues are load-bearing — until they're fixed, the rest is polish on an
unreliable signal.

---

## 2. Findings (evidence-backed)

### 🔴 F1 — The windows silently drop ~72% of plays

`aggregate_window` (`orpheus/aggregate/windows.py:36`) `JOIN`s `plays → track_scores`.
Only scored tracks survive the join.

| Measure | Count |
|---|---|
| Total plays | 10,041 |
| Plays that map to a scored track | **2,811 (28%)** |
| Plays in the last 12 days (the "state" lookback) | 194 |
| …of those, scored | **17 (8.8%)** |
| Tracks total / tracks scored | 4,243 / **550 (13%)** |

The **state window headline is computed from ~17 plays.** That isn't a mood
reading; it's noise dressed as a conclusion. The scoring step simply never
finished the catalog (550 of 4,243 tracks scored, even though 3,811 have audio
features and could be acoustic-scored).

**Why it matters:** every downstream claim — top emotions, shifts, trends —
inherits this sampling bias, and nothing in the report discloses it.

### 🔴 F2 — "Arousal" is just energy

`arousal == energy` for **all 3,809** audio-feature rows (`audio_import.py:144`
falls back to `energy` when `arousal` is absent — and it's always absent;
ReccoBeats doesn't supply it).

The entire emotion model places tracks on a valence/**arousal** plane
(`emotion.py:_VA_ANCHORS`), but that second axis is literally Spotify energy.
"Peacefulness" (arousal −0.7) vs "tension/anxiety" (arousal +0.5) is decided
purely by energy. That's a defensible *proxy*, but it's currently presented as
arousal, which it is not.

### 🟠 F3 — Per-track confidence is computed, then ignored

`track_scores.confidence` exists and is populated (0.85 fused, 0.5 acoustic-only,
0.3 acoustic-theme, **0.1 uniform fallback**). `aggregate_window` never reads it
(`windows.py:123-131`). A track that scored a flat `1/8` across every emotion
(confidence 0.1) contributes the same mass as a confidently-classified track.
Low-confidence tracks drag every window toward uniform.

### 🟠 F4 — Clusters & co-occurrences use the whole catalog, narrated as "your listening"

- `cluster._load_avd_data` (`cluster.py:31`) selects **all** `track_scores` — no
  time decay, no engagement weight, no play counts.
- `detect_co_occurrences` (`trends.py:86`) iterates **all** `track_scores`, once
  per *track*, ignoring how many times each was played.
- `share_of_listening` (`cluster.py:141`) is the mean GMM membership across
  *tracks* — it's share of the **catalog**, not of listening.

So the report fuses three different temporal scopes — state (≈12 days), trait
(≈360 days), and clusters/co-occurrence (**all time, unweighted**) — and narrates
them all as "your listening." A track you played once and a track you played 500
times count equally.

### 🟡 F5 — Depth score is weakly grounded

`score_depth` (`score/depth.py`) averages three signals, but:
- `spectral_complexity` is **NULL for every row** → silently absent.
- "Acoustic complexity" then reduces to `|tempo − 120|/120` and a single
  loudness value treated as "dynamic range" — neither measures complexity.
- `_lexical_density` (type/token ratio) is length-biased: short lyrics score as
  more "dense."

Depth is presented as a meaningful axis (it's the third clustering dimension and
a per-track label) but is mostly a tempo/loudness artifact.

### 🟡 F6 — An emotion key leaks into theme scores

`theme.py:145` writes `scores["anger_defiance"]` inside the acoustic theme
heuristic. `anger_defiance` is an **emotion** category, not a theme. It gets
normalized into the theme distribution and then dropped downstream — harmless
output, but a real logic bug and a sign the heuristic wasn't reviewed.

### 🟡 F7 — The narrative layer is thinner than the product promises

`PRODUCT.md` sells a "read-in-five-minutes letter about yourself." But
`assemble.py` emits **no `narrative` object** (confirmed: report top-level keys
have no `narrative`). The frontend `HeroSummary` falls back to one templated
sentence + a bullet list of shift/trend strings (`HeroSummary.tsx:17-22`). The
"letter" is currently a headline and some bullets.

### ⚪ F8 — Minor

- `engagement_weights.repeat_session` (config + `record_run` snapshot) is **never
  applied** in `engagement_weight()`. Dead knob.
- Window `from_date`/`to_date` use a hard `4 × half_life` cutoff
  (`windows.py:188`) that doesn't match the exponential decay actually used for
  weighting — the displayed range and the math disagree.
- `config.yaml` holds real-looking Spotify/Genius credentials. It **is**
  gitignored and untracked (verified), so not committed — but rotate them if the
  file has ever been shared.

---

## 3. Spotify Wrapped — what's worth borrowing

Wrapped works because of **sequenced storytelling, concrete grounding stats, a
listening identity, and a shareable artifact.** Orpheus should borrow the
*mechanics*, not the confetti — the brand is reflective and observational, not
celebratory.

| Wrapped element | Orpheus adaptation (on-brand) |
|---|---|
| Top songs/artists with counts | Already have frequency tracks — surface real play counts + **minutes listened** as grounding |
| "Audio aura" / listening personality | Name the dominant cluster as a **listening archetype** ("introspective core") woven into the letter |
| Minutes listened headline stat | A single honest total ("You spent ~X hours here this season") |
| Sequenced reveal | A paced, scrollable **narrative** (intro → mood → themes → people/songs → movement → close) |
| Months/seasons recap | **Temporal layer**: time-of-day, day-of-week, "your months in sound" |
| Shareable card | One tasteful, exportable **reflection card** |

---

## 4. Sprints

Ordered foundation → polish. Each sprint is independently shippable.

### Sprint 0 — Trust the data
> Make the report honest about what it's actually based on. Nothing else matters
> until the signal is trustworthy.

- **Finish scoring coverage (F1).** Make `orpheus score` cover the full catalog
  (or at least every track with audio features). Acoustic-only scoring needs no
  lyrics, so 3,811 tracks are scorable today. Add progress + a coverage summary
  to `orpheus status`.
- **Surface coverage in the report (F1).** Add `coverage` to each window:
  `scored_plays / total_plays` for the window's lookback. Frontend shows it
  ("Based on 17 of 194 recent plays") and **suppresses or caveats** the state
  headline when coverage is below a threshold (e.g. <40%).
- **Relabel the arousal axis (F2).** Either (a) rename to `valence/energy`
  throughout, or (b) keep "arousal" but document it as energy-derived in
  `02_methodology` and the UI tooltip. Pick one and be consistent.
- **Acceptance:** state/trait windows report coverage; low-coverage windows can't
  produce an unqualified headline; the V/A → energy substitution is documented in
  one place and reflected in axis labels.

### Sprint 1 — Honest aggregation
> Make every number mean what its label says.

- **Confidence-weight aggregation (F3).** Multiply each track's contribution in
  `aggregate_window` by `confidence` (or drop tracks below a floor). Verify
  windows shift away from the uniform pull.
- **Make clusters & co-occurrence recency/engagement-aware (F4).** Feed
  `cluster._load_avd_data` and `detect_co_occurrences` the same play-weighted,
  time-decayed sample the windows use — or scope them to the trait window
  explicitly. Weight co-occurrence counts by plays, not distinct tracks.
- **Fix `share_of_listening` (F4).** Compute it from play-weighted membership and
  rename if it can't be made a true listening share.
- **Acceptance:** no report field is narrated as "listening" while computed over
  the unweighted catalog; cluster shares sum to ≈100% of weighted plays.

### Sprint 2 — Repair the depth & theme signals
> Stop presenting artifacts as axes.

- **Rebuild or retire depth (F5).** Either source real features (spectral
  complexity, true dynamic range) or replace the depth axis with something the
  data supports (e.g. lyrical themes entropy + acousticness), and fix the
  length-bias in lexical density. If it can't be grounded, demote it from a
  headline axis to an optional detail.
- **Fix the theme heuristic leak (F6).** Remove `anger_defiance` from
  `theme.py:145`; audit the rest of `_acoustic_heuristic` against
  `THEME_CATEGORIES`.
- **Apply or remove `repeat_session` (F8).** Implement repeat detection in
  `engagement_weight`, or delete the knob from config + `record_run`.
- **Acceptance:** every depth/theme input is either grounded in present data or
  removed; theme scores only ever contain theme keys; no dead config knobs.

### Sprint 3 — The narrative engine (Wrapped's storytelling, Orpheus's voice)
> Deliver the "letter about yourself" the product promises.

- **Generate a `narrative` object in `assemble.py` (F7).** Server-side, compose:
  `headline`, ordered `key_insights` (mood → themes → people/songs → movement),
  a `listening_archetype` from the dominant cluster, honest `caveats` (low
  coverage, energy-as-arousal, stale trailing week). Frontend already reads
  `report.narrative` — wire it through.
- **Paced reveal.** Restructure the frontend hero/reader into a sequenced,
  scroll-paced read (intro → state → trait → evidence) rather than a single
  dump.
- **Acceptance:** the report opens with a coherent multi-beat letter that reads
  in five minutes, names a listening archetype, and states its own caveats.

### Sprint 4 — Temporal & moments layer (Wrapped recap mechanics)
> Add the time-shaped stories Wrapped is loved for — grounded, not gamified.

- **Grounding stats.** Total hours listened, distinct tracks/artists, in the
  window — computed from raw `plays.ms_played` (no scoring needed, so full
  coverage).
- **Temporal patterns.** Time-of-day and day-of-week mood/volume; "your months in
  sound" arc. The `plays` table already has timestamps and `ms_played`.
- **Moments.** Biggest listening day, song of the season (most-played qualified
  track), a returning song you keep coming back to.
- **Acceptance:** a temporal/moments section that draws on **all** plays (not the
  scored subset), so it's reliable even while scoring coverage catches up.

### Sprint 5 — The shareable reflection card + polish
> One tasteful artifact, plus final coherence pass.

- **Reflection card.** A single exportable image/card: archetype + one mood line
  + top song/artist + season. Restrained, on-brand (no Wrapped neon).
- **Date-range honesty (F8).** Reconcile displayed `from/to` with the decay math,
  or relabel as "effective lookback."
- **Coherence QA pass.** Re-run the full pipeline, confirm every label matches
  its computation, and run the existing checklist in `CLAUDE.md` §"Generating a
  report."
- **Acceptance:** shareable card ships; a reviewer can trace every visible number
  back to a computation whose label matches its meaning.

---

## 5. Suggested ordering rationale

- **0 → 1 → 2** repair trust in the signal (coverage, weighting, grounded axes).
  Do these before any storytelling, or you'll narrate noise more beautifully.
- **3 → 4** add the Wrapped-style narrative and temporal stories. Sprint 4
  deliberately leans on raw plays so it's reliable regardless of scoring backlog.
- **5** packages it for sharing and does the final coherence sweep.
