# PRD.md
## Project Orpheus v2 — Product Requirements Document

| Field | Value |
|---|---|
| Project | Orpheus v2 |
| Owner | Ben Wassa |
| Status | Active development, MVP phase |
| Last updated | 2026-05-25 |
| Repository (v1, deprecated) | https://github.com/BenWassa/orpheus |
| Companion docs | T1_taxonomy_v1.md, C2_methodology_spec.md, C3_data_pipeline_spec.md |

---

## 1. Executive Summary

Orpheus is a personal music listening analysis tool that surfaces emotional and thematic patterns in what someone keeps returning to, and shows how those patterns shift over time. It is built around the idea that what you play repeatedly is data about what you are paying attention to internally.

It is not Spotify Wrapped. It is not a diagnosis. It is an observational mirror: here is where your music clusters, here are the themes those songs share, do with that what you will.

V1 (2024) was a local Streamlit app fed by Exportify CSV exports. It worked but never escaped a small audience because the data pipeline was brittle and the analysis layer was thin. V2 rebuilds around live Spotify API data, a research-grounded taxonomy, and a defensible analysis methodology.

---

## 2. Problem Statement

People have a vague intuition that their music listening reflects something about their inner life, but no rigorous way to see it. Existing tools fail to bridge the gap:

- **Spotify Wrapped** is annual, gamified, marketing-driven. It tells you your top artist, not what you're processing.
- **Last.fm / Receiptify** are flat play-count timelines. No semantic understanding, no time decay, no pattern detection.
- **Academic prototypes** (MoodPlay, etc.) have rigor but no usable interface and don't reach end users.
- **No mainstream tool** surfaces emotional or thematic patterns and shows how they shift between "who I have been" and "what's gripping me right now."

Orpheus targets that gap.

---

## 3. Target Users

**Phase 1: Self.** The project owner tests on personal listening data. Goal: validate that the analysis produces insights that feel real and useful.

**Phase 2: Friends.** A small group of trusted testers run Orpheus on their own data. Goal: validate the analysis works across different listening profiles, gather honest reactions.

**Phase 3: Public consideration.** Only if Phase 2 validates. Public release would require UX work, hosting, multi-user architecture, and active safety layers. Not a foregone conclusion.

The current PRD scopes through Phase 2.

---

## 4. Vision Statement

Orpheus surfaces the emotional and thematic shape of your listening so you can see what you have been sitting with. It treats your music as data, not as an oracle. The user does the interpreting.

The mythology fits: Orpheus descends into the underworld with music as his guide. The tool descends into a listener's library and brings back a map.

---

## 5. Goals

**Primary:**
- Surface dominant emotional categories in a listener's library and current state
- Surface dominant life themes
- Show how those patterns differ between long-term baseline (trait) and recent listening (state)
- Detect shifts: which categories are rising, falling, spiking
- Detect co-occurrences: which themes appear together

**Secondary:**
- Provide a snackable, observational narrative output that the user can read in under five minutes
- Be reproducible: same data + same config = same output
- Be defensible: every analytical choice references research grounding

**Tertiary:**
- Eventually support friend-test phase with safety layer active
- Eventually support a visual frontend (React/TypeScript)

---

## 6. Non-Goals

- **Diagnose mental health states.** The system describes music, not the listener.
- **Replace Spotify Wrapped.** Different shape, different cadence, different audience.
- **Be a social product.** No sharing, leaderboards, or comparison features in MVP.
- **Support real-time streaming analysis.** Run on demand only.
- **Generate music or playlists.** Analysis only, no creation.
- **Cover non-Spotify sources in MVP.** Apple Music, Tidal, YouTube Music are deferred.
- **Support foreign-language lyrics at MVP.** Models are English-trained. Limitation noted in output.
- **Multi-user / shared accounts.** Single-user, local-only for MVP.

---

## 7. User Stories

**Phase 1 (Self):**

> As the owner, I can request my Spotify Extended Streaming History, drop it into the project, run a command, and receive a JSON report identifying my top emotional and thematic categories across state and trait windows.

> As the owner, I can see which themes have intensified or faded in recent weeks compared to my long-term baseline.

> As the owner, I can re-run the analysis and trust I'll get the same output unless data or models change.

**Phase 2 (Friends):**

> As a friend testing Orpheus, I can run the tool on my own data on my own machine without sharing my listening history with anyone.

> As a friend, I can read the output and either nod along (it matches what I felt) or push back (it missed something), and that feedback informs whether Orpheus is worth pursuing further.

> As a project owner running the friend test, I can trust that the safety layer is active so that vulnerable users get gentle counterweights rather than reinforcement.

---

## 8. Functional Requirements

### 8.1 Data Ingestion (per C3)
- Parse Spotify Extended Streaming History JSON files
- Pull supplemental data from Spotify Web API (top tracks/artists, recently played, saved library)
- Persist to local SQLite database

### 8.2 Track Enrichment (per C3)
- Resolve audio features from SoundNet/SoundStat (primary) or Anna's Archive cache
- Fetch lyrics from Genius for tracks with lyrics; flag instrumentals
- Pull artist metadata (genres, popularity) from Spotify Web API

### 8.3 Track Scoring (per C2)
- Score each track against 8 emotion categories (probabilistic, top-n)
- Score each track against 8 life theme categories (probabilistic, top-n)
- Score depth (composite: acoustic complexity + lexical density + topic depth)
- Use specialized NLP stack (BART-MNLI + MPNet + s-VSM), not general LLMs

### 8.4 Aggregation (per C2)
- Compute state window scores (3-day exponential half-life)
- Compute trait window scores (90-day exponential half-life)
- Apply engagement-weighted multipliers (full play, skip, structural-boundary skip, repeat, shuffle, library)
- Maintain artist-level aggregates as priors

### 8.5 Pattern Detection (per C2)
- Run DBSCAN noise filter to exclude background-music sessions
- Run 3-component GMM for soft cluster assignment in AVD space
- Detect trends (rising, falling, spiking, declining categories)
- Detect co-occurrences (theme x emotion pairs appearing together)
- Compare state to trait (deltas, shifts)

### 8.6 Output Assembly (per C2)
- Produce structured JSON per C2 schema
- Apply discrete prevalence labels (dominant / high / moderate / present / not represented)
- Generate observational narrative strings per voice rules in T1
- Write report to disk with timestamp

### 8.7 Safety Layer (scaffolded, inactive in MVP)
- Module implemented but feature-flagged off
- Activated for friend-test phase via config
- Detects sustained negative-valence + high-depth clusters without comforting trajectory
- Adds counterweight to output, never blocks or alarms

---

## 9. Technical Requirements

### 9.1 Stack
- **Language:** Python 3.11+
- **Persistence:** SQLite (single file, local)
- **NLP models:** BART-large-MNLI, MPNet (all-mpnet-base-v2), s-VSM filter
- **Audio features:** Anna's Archive dump (bulk cache) — only working source. The SoundNet/SoundStat RapidAPI primary was removed (5 req/day BASIC tier, unusable) and audio features are deferred pending a replacement; see docs/C3_data_pipeline_spec.md.
- **External APIs:** Spotify Web API, Genius API
- **Output:** JSON files written to disk
- **CLI:** standard Python CLI tool, no web server in engine

### 9.2 Frontend (deferred)
- React + TypeScript expected
- Consumes JSON output from engine
- Renders 2D Valence-Arousal scatter with depth as text label
- Timeline view of category prevalence
- Narrative blocks driven by output JSON

### 9.3 Reproducibility
- Pin all model versions in config
- Record analysis runs with config snapshot, model versions, output hash
- Same data + same config = byte-identical output

### 9.4 Performance Targets (per C3)
- First full run with cold cache: under 4 hours (API-rate-limit bound)
- First full run with Anna's Archive imported: under 1 hour
- Subsequent runs: under 30 minutes

---

## 10. Success Criteria

### Phase 1 (Self test)
- Pipeline runs end-to-end without manual intervention after initial setup
- Output is reproducible (same input + same config → same output)
- Owner reads the report and reports at least one finding that feels genuinely insightful (not just descriptive)
- Output is observationally accurate (no statements the data doesn't support)
- Output voice matches T1 rules (observational, not interpretive)

### Phase 2 (Friend test)
- 3-5 friends successfully run Orpheus on their own data
- At least 60% of testers report at least one "I didn't realize that" moment
- No tester reports the analysis as harmful, invasive, or wrong-feeling
- Safety layer activates appropriately (validated through synthetic test cases)
- Honest qualitative feedback gathered: what worked, what missed

### Phase 3 (Public consideration)
- Phase 2 validates the core hypothesis
- Hosting, multi-user, and UX work are deemed worth investing in
- Decision is "yes" or "no", not "maybe"

---

## 11. Phasing and Milestones

### Phase 0 — Specs (current)
- [x] T1 taxonomy
- [x] C2 methodology
- [x] C3 data pipeline
- [x] PRD
- [ ] P1 narrative prompts (when output assembly needs them)

### Phase 1 — MVP Build (self test)
- [ ] Project scaffold (package layout per C3)
- [ ] Spotify export ingestion
- [ ] Spotify Web API live sync
- [ ] Audio features enrichment (SoundNet + Archive fallback)
- [ ] Lyrics fetching (Genius)
- [ ] Emotion classifier
- [ ] Theme classifier
- [ ] Depth scoring
- [ ] Time-decay aggregation (state + trait windows)
- [ ] DBSCAN + GMM clustering
- [ ] Trend and co-occurrence detection
- [ ] JSON output assembly
- [ ] CLI commands wired up
- [ ] Run end-to-end on owner's data
- [ ] Validate output quality, iterate

### Phase 2 — Friend Test
- [ ] Safety layer activated and tested
- [ ] Onboarding documentation (how to request Spotify export, install, run)
- [ ] Frontend MVP (React/TS, consumes JSON output)
- [ ] Recruit 3-5 friend testers
- [ ] Gather structured feedback
- [ ] Iterate based on findings

### Phase 3 — Public Consideration
- Decision gate based on Phase 2 results
- If yes: hosting, multi-user, UX investment plan
- If no: Orpheus stays a personal/small-group tool

---

## 12. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Anna's Archive bulk dump disappears | Medium | Medium | Use as one-time hydration only; SoundNet stays as live fallback |
| Genius API hostility to scrapers | Medium | Medium | Monitor; switch to MusixMatch if Genius becomes unreliable |
| Spotify further restricts API | Medium | High | Lean into Extended Streaming History (user-owned data, not API-dependent) |
| SoundNet/SoundStat shuts down | Low | High | Essentia local extraction as ultimate fallback for power users |
| Model output feels generic or wrong | Medium | High | Iterative tuning against real data in Phase 1; the engagement weight table is deliberately tunable |
| Users misinterpret observational output as diagnosis | Medium | Medium | T1 voice rules + explicit disclaimer in output |
| Safety layer mis-triggers on healthy listeners | Low | Medium | Conservative thresholds, tested against synthetic cases before friend test |
| Privacy concerns from testers | Low | High | Local-only architecture, no data leaves user's machine in MVP |

---

## 13. Open Decisions

These are flagged for resolution before or during Phase 1 build:

- **Depth labels:** "surface / engaged / immersive" vs alternatives. Easy to swap, tune against output.
- **Engagement weight tuning:** Initial values from C2 are starting points. Tune against owner's data before declaring v1 stable.
- **Genius vs MusixMatch:** Genius for MVP, watch for issues, switch if needed.
- **Output cadence:** On-demand only for MVP. Scheduled runs (weekly, monthly) deferred.

---

## 14. Out of Scope (explicit)

These were considered and explicitly deferred:

- **Foreign-language lyric support.** English-only at MVP.
- **Multi-user / shared accounts.** Single-user, local.
- **Hosted version.** Local install only.
- **Live audio playback of clusters.** Frontend may revisit.
- **Apple Music / Tidal / YouTube Music ingestion.** Spotify-only at MVP.
- **Mobile app.** Desktop / web only.
- **Social features / sharing / leaderboards.** Not part of vision.
- **AI playlist generation.** Orpheus analyzes, does not create.
- **Real-time scrobbling-style updates.** On-demand runs only.

---

## 15. Glossary

- **AVD space**: 3D coordinate space of Arousal, Valence, Depth. Emotion categories anchor in this space.
- **State window**: Short-term listening aggregation (3-day exponential half-life). Captures current preoccupations.
- **Trait window**: Long-term listening aggregation (90-day half-life). Captures stable identity.
- **Perceived vs Induced emotion**: Music expresses emotion (perceived). Listener feels something (induced). Orpheus maps perceived only.
- **Rumination loop**: Sustained listening to negative-valence/high-depth content without trajectory toward relief. The safety layer's trigger condition.
- **Engagement weight (W_0)**: Multiplier on a play event based on completion, skip, repeat, source. See C2.
- **Top-n classification**: Multi-label scoring where a song gets the n strongest category assignments rather than one.
- **MUSIC model**: Rentfrow/Greenberg five-style preference taxonomy (Mellow, Urban, Sophisticated, Intense, Unpretentious). Used as a sanity-check layer.

---

## 16. References

- **R1_emotion_research.md**: Music emotion taxonomy research synthesis
- **R2_theme_research.md**: Lyrical life themes research synthesis
- **R3_methodology_research.md**: Listening data analysis methodology synthesis
- **T1_taxonomy_v1.md**: Schema and taxonomy
- **C2_methodology_spec.md**: Analysis engine spec
- **C3_data_pipeline_spec.md**: Data pipeline and build architecture
- **v1 codebase**: https://github.com/BenWassa/orpheus (archived; design lessons only, not technical reference)

Key empirical sources behind the design (full citations in R1, R2, R3):
- Zentner et al. (2008) GEMS
- Cowen & Keltner (2020) 13-D model
- Russell (1980) Circumplex Model
- Juslin's BRECVEMA framework
- Rentfrow, Goldberg, Levitin MUSIC model
- Saarikallio MMR taxonomy
- Kwon et al. (2021) Billboard content analysis
- Eerola & Vuoskoski dimensional-discrete synthesis
