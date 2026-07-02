# STATUS — Project Orpheus

**The single status document.** Everything about where the project *is* and
what to build *next* lives here. Durable specs stay in `docs/`; product
identity in `PRODUCT.md`; setup in `SETUP.md`. This file supersedes the former
`IMPROVEMENT_SPRINTS.md` (data/logic review + sprints, 2026-05-29) and
`UI_UPGRADE_TODO.md` (frontend upgrade checklist, completed) — both are folded
in below and deleted. The dated frontend handoff bundle moved to
`archive/frontend_upgrade_handoff/`.

_Last verified: 2026-07-02 (fresh clone, clean venv, full pipeline run)._

---

## 1. Where the project is

Orpheus v2 is a working local-first pipeline + React dashboard. Verified end
to end on 2026-07-02:

| Check | Result |
|---|---|
| `pip install -e ".[dev]"` on Python 3.11 | ✅ clean |
| `ruff check orpheus/ tests/` | ✅ clean |
| `pytest -m "not slow"` | ✅ 127 passed |
| `orpheus refresh --profile Ben --as-of latest-play` | ✅ report written |
| `npm run build` (frontend) | ✅ builds |

**Data state** (`data/cache/Ben.db`, snapshot in repo): 10,041 plays
(2025-01-27 → 2026-05-22), 4,243 tracks, 1,321 with lyrics, **550 scored
(13%)**, **4 with audio features**. The two low numbers are the whole story of
what limits report quality today — see §3 Level 1.

**Report contract** now includes (added 2026-07-02): `narrative`
(server-composed letter: headline, key insights, archetype, caveats),
`temporal` (full-coverage grounding: hours/plays/months/moments/rhythm),
`as_of` (window anchor), and `experimental` (session mood arcs + novelty
ratio, self-labelled exploratory with per-section evidence notes). `--as-of
latest-play` anchors windows to the newest play so stale exports still
produce a meaningful "recent" window.

## 2. Findings ledger (from the 2026-05-29 data & logic review)

| # | Finding | Status |
|---|---|---|
| F1 | Windows silently dropped ~72% of plays; no coverage disclosure | **Code fixed** — per-window `coverage` emitted; narrative suppresses/caveats thin headlines. **Data half open**: scoring coverage is still 13% (Level 1). |
| F2 | "Arousal" is actually Spotify energy | **Resolved** — documented in `emotion.py`, UI labels the axis energy, narrative caveats it. |
| F3 | Per-track confidence computed but ignored | **Resolved** — per-axis confidence weighting in `aggregate_window`. |
| F4 | Clusters/co-occurrence used the unweighted whole catalog | **Resolved** — play-weighted, window-scoped (`cluster.py`, `trends.py`); `share_of_listening` is a true listening share. |
| F5 | Depth score weakly grounded (tempo/loudness artifact) | **Partially open** — lexical density now MSTTR (length-bias fixed); acoustic "complexity" is still tempo-deviation. Rework or demote (Level 2). |
| F6 | Emotion key leaked into theme scores | **Resolved** — removed from theme heuristic. |
| F7 | No narrative object; "letter" was a headline + bullets | **Resolved (backend)** — `orpheus/output/narrative.py` composes headline/insights/archetype/caveats; frontend already parses `report.narrative`. Archetype + temporal rendering in the UI is Level 2. |
| F8 | Dead `repeat_session` knob; date-range/decay mismatch | Knob **removed**. Date range is now explicitly the evidence span (see `windows.py` docs); displayed-range honesty pass remains in Level 2. |

Sprint history: Sprints 0–2 (trust the data, honest aggregation, signal
repair) ✅ done pre-July. Sprint 3 (narrative engine) and Sprint 4 (temporal &
moments layer) ✅ backend done 2026-07-02. Sprint 5 (share card + coherence
pass) open. The UI upgrade checklist (narrative-first layout, progressive
disclosure, natural language, responsive polish) completed 2026-05-29.

## 3. Build-out roadmap, by level

### Level 1 — Data completeness (highest leverage; needs your machine)

The cloud sandbox blocks `api.reccobeats.com`, `huggingface.co`, and
`api.genius.com`, so these must run locally. This is the single biggest
quality unlock: it takes scoring coverage from 13% toward ~90%+ and turns
clusters back on.

```bash
.venv/bin/orpheus archive fill-gaps          # ReccoBeats: audio features for ~4,200 tracks (keyless, ~10 min)
# optional, better coverage: orpheus archive import <kaggle CSV/SQLite archive>
.venv/bin/orpheus score                      # rescore; acoustic-only tracks are fast, lyric tracks load BART
.venv/bin/orpheus refresh --profile Ben --as-of latest-play
```

Notes: `score` only processes unscored tracks. To re-fuse the 550
already-scored tracks with new audio features, delete their `track_scores`
rows first (`DELETE FROM track_scores` and rerun). Track scoring progress with
`orpheus status`.

### Level 2 — Product polish (buildable anywhere)

1. **Render the new layers in the dashboard**: archetype card, grounding
   stats, months-in-sound, moments (biggest day / song of season / comeback),
   rhythm. The JSON is already in every new report; only frontend work.
2. **Sprint 5 share card**: one exportable reflection card (archetype + one
   mood line + top song/artist + season), restrained styling per `DESIGN.md`.
3. **Depth axis decision (F5)**: either source real complexity features or
   demote depth from a clustering axis to an optional detail.
4. **Date-range honesty (F8)**: label window ranges as "evidence span"
   in the UI.
5. **Promote report generation to a `/report` skill** once the output
   stabilizes (per CLAUDE.md).

### Level 3 — Experimental perspectives

Ordered by insight-per-effort; all are additive report sections that can ship
behind the same honest-caveat pattern:

1. ~~**Session arcs.**~~ ✅ **Shipped 2026-07-02** (`orpheus/output/perspectives.py`,
   report key `experimental.session_arcs`): sessionize plays (gap > 30 min),
   compare negative-emotion share at session start vs. end, and only emit a
   "regulation/amplification" reading when a majority pattern exists. On
   current data: 23/76 sessions measurable, no dominant arc — honest null.
2. ~~**Novelty ratio.**~~ ✅ **Shipped 2026-07-02**
   (`experimental.novelty`): share of qualified plays that are first-ever
   plays, overall + per month, full coverage. Current season: ~35%.
3. **Listening seasons.** Change-point detection on the weekly emotion/theme
   series to segment the year into named "chapters" (e.g. the hip-hop
   winter, the ambient March, the country spring) — the month-level story the
   temporal layer already hints at, made first-class.
4. **Artist affinity drift.** Per-artist engagement over time: who's rising,
   who quietly left the rotation, artist tenure distribution.
5. **Skip-language.** Skips are already engagement-weighted; surface them as
   their own signal — what moods/themes do you *refuse* lately?
6. **LLM-composed letter (opt-in).** Feed the deterministic report JSON to
   Claude to write the five-minute letter in full prose, with the template
   narrative as the guaranteed fallback. Keeps determinism for the data,
   spends model quality on the language. Needs an API key + a config flag.
7. **Local audio-feature extraction.** Long-shot replacement for dead APIs:
   compute valence/arousal proxies from 30s previews with librosa/Essentia
   (see `audio-features-research/` for the groundwork already done).

## 4. Operating notes

- **Environment**: `python3.11 -m venv .venv && .venv/bin/pip install -e ".[dev]"`,
  then `python scripts/bootstrap.py`. Set `paths.db_path` in `config.yaml` to
  `data/cache/Ben.db` to use the committed sample data.
- **Cloud/CI sandboxes**: pypi + npm are reachable; ReccoBeats, Hugging Face,
  and Genius are not. Everything except enrichment/scoring runs fine there.
- **Reports**: always `--profile <name>` (dashboard reads
  `data/output/reports/<profile>/`), and `--as-of latest-play` for any static
  export. A bare `refresh` warns when the recent window is empty.
- **graphify**: CLAUDE.md references a `graphify-out/` knowledge graph that is
  not currently in the repo, and the `graphify` CLI is not installed in the
  cloud environment. Regenerate it locally or drop the reference.
- **Human summary**: the latest written profile is
  `data/output/reports/MUSIC_PROFILE_REPORT.md` (season ending 2026-05-22).
