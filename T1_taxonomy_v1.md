# T1_taxonomy_v1.md
## Project Orpheus v2 — Taxonomy and Schema

### Purpose
Three-dimensional schema for analyzing listening data and surfacing patterns in a listener's emotional and thematic preoccupations over time.

- **Emotion axis**: 8 discrete categories anchored in continuous Valence-Arousal-Depth (AVD) space
- **Life themes axis**: 8 discrete categories, multi-label classification (top-n, n ≥ 3 per track)
- **Time architecture**: dual exponential windows (state vs trait)

Tracks get scored against both axes. Listener patterns emerge from density clustering across time.

### Theoretical Grounding
Synthesized from R1 (emotion), R2 (themes), R3 (methodology):
- Emotion taxonomy: hybrid of Russell's circumplex + GEMS + Cowen-Keltner 13-D model, anchored in music-specific empirical research
- Theme taxonomy: validated against Kwon et al. (2021) Billboard content analysis across 5 major genres
- Methodology: MUSIC model (Rentfrow/Greenberg) + Saarikallio's MMR strategies + Juslin's BRECVEMA mechanisms

---

### Emotion Axis (8 categories)

Coordinates: Valence (V) and Arousal (A). Depth tracked separately.

| # | Category | V | A | Acoustic markers | Lyric markers |
|---|---|---|---|---|---|
| 1 | **Joyful Activation** | +0.8 | +0.6 | Fast tempo, major mode, consonant, bright timbres | Celebration, sensory pleasure, optimism |
| 2 | **Triumphant / Power** | +0.6 | +0.8 | Brassy, sharp attack, stable harmony | "Rise", "stronger", "unbroken" |
| 3 | **Peacefulness / Serenity** | +0.8 | -0.7 | Slow tempo, drone-like, no percussion | Solitary, nature, breathing, release |
| 4 | **Tenderness** | +0.7 | -0.3 | Vibrato, mellow timbres, soft dynamics | Interpersonal pronouns, "you and I" |
| 5 | **Nostalgia / Longing** | +0.2 | -0.4 | Minor-to-major resolutions, sighing intervals | Interrogative, future-oriented ("where are you") |
| 6 | **Sadness / Melancholy** | -0.8 | -0.6 | Minor third intervals, descending contours | Finality, absolute loss ("nothing left") |
| 7 | **Tension / Anxiety** | -0.6 | +0.5 | Irregular rhythms, dissonance, dynamic spikes | Paranoia, confinement, loss of control |
| 8 | **Anger / Defiance** | -0.7 | +0.8 | Distortion, harsh articulation, harmonic dissonance | "Burn", "destroy", direct confrontation |

### Diagnostic boundaries (resolving similar pairs)

- **Longing vs Sadness**: Longing is interrogative and future-oriented; Sadness is final and resigned. Acoustically, Longing keeps higher pitch variability and uses minor-to-major transitions; Sadness stays narrow-range, descending.
- **Power vs Anger**: Power is consonant, stable, clean vocals. Anger is dissonant, distorted, rough articulation.
- **Tenderness vs Peace**: Tenderness is interpersonal ("you and I") with vibrato. Peace is solitary with flat, drone-like structure.

---

### Life Themes Axis (8 categories)

Empirically validated against Kwon et al. (2021) content analysis (n=1,052 songs across Hip-Hop/R&B, Pop, Country, Rock/Metal, Latin).

1. **Interpersonal Devotion and Bonds** — romantic, familial, friendship celebration. 2nd-person pronouns, attachment imagery.
2. **Heartbreak, Loss, and Betrayal** — relational dissolution, unrequited love, infidelity. Past-tense intimacy, betrayal vocabulary.
3. **Adversity, Mental Health, and Resilience** — survival, depression, trauma, endurance. Distress + recovery vocabulary.
4. **Identity, Anti-Conformity, and Autonomy** — self-actualization, rejection of pressure. 1st-person singular, authenticity, rebellion imagery.
5. **Status, Ambition, and Material Dominance** — wealth, fame, competitive dominance. Luxury nouns, victory assertions.
6. **Hedonism, Party, and Substance Escapism** — sensory pleasure, chemical escape, release. Substance references, kinetic movement, temporal urgency.
7. **Place, Heritage, and Nostalgia** — geographic grounding, family, past. Spatial/travel nouns, memory markers, familial terms.
8. **Existentialism, Mortality, and Spirituality** — death, meaning, faith, transience. Metaphysical vocabulary, cosmic purpose questions.

---

### Classification Rules

- **Multi-label, top-n (n ≥ 3) per axis per track.** Single-label classifiers fail because lyrics traverse multiple semantic domains within one song.
- **Layered priors:** Artist-level signal provides baseline (stable identity layer). Song-level data refines or overrides (state-specific layer).
- **Multimodal late fusion with cross-modal attention.** Lyrics dominate negative-valence detection. Acoustic features dominate arousal calculation. Conflicting signals (upbeat track, dark lyrics) get dynamic weighting, not averaging.
- **Instrumental fallback:** Acoustic-only classification with theme axis confidence lowered. Use crowd-sourced annotations (Genius, Songfacts) where available to resolve abstract or metaphorical content.

---

### Time Architecture (dual exponential decay)

Two parallel processing windows on the same data:

| Window | Half-life | Captures | Use |
|---|---|---|---|
| **State** | 3 days | Active mood regulation, situational focus | Current preoccupations |
| **Trait** | 90 days | Stable preference baseline, identity | Long-term portrait |

Weight formula: `W = W_0 × exp(-λ(t - t_i))` where λ = ln(2) / T_half.

Raw interaction weight W_0 adjusted by engagement: full play = 1.0, played >30s = 0.7, skipped pre-30s = -0.5 (penalty), skipped within ±1.5s of structural boundary = -0.25 (mitigated, low-friction drop-off).

---

### Critical Distinction: Perceived vs Induced

The system maps **perceived** emotion (expressed in the music) not **induced** emotion (felt by listener). Outputs must reflect this constraint linguistically.

✓ "Your listening clusters around longing"
✗ "You are feeling longing"

The same sad song can produce induced relief in a reflector and induced despair in a ruminator. The system cannot know which from acoustic and lyrical features alone.

---

### Safety Layer: Rumination Detection

Per R3, the system must distinguish healthy reflection from maladaptive rumination.

**Trigger condition**: state window (3-day) shows a high-density cluster in negative-valence, high-depth quadrant (V ≤ 0.3, D ≥ 0.7), sustained for >48 hours, with no trajectory toward higher-valence or comforting tracks.

**Action**: flag the state as potential rumination loop, downweight further reinforcement of negative-valence vectors in any recommendation surface, and gently surface lower-arousal positive-valence (Mellow/Tenderness) content as counterweight.

This is non-negotiable for any version released beyond personal testing.

---

### Open Questions

- **Operationalize Depth.** Research uses AVD but doesn't fully specify how Depth gets computed. Candidates: acoustic complexity score from Essentia, lexical density of lyrics, hLDA topic depth, or composite. Decide in C2.
- **2D vs 3D commitment.** Visualization is harder in 3D. Could ship v1 in 2D (V/A only) and add Depth in v2.
- **Theme granularity.** Should "Love" be one slot or split (Devotion vs Heartbreak vs Longing)? Current taxonomy splits Devotion and Heartbreak. Longing lives under emotion axis as a state, not a theme.
- **Multi-cultural calibration.** All grounding research is Western. If users include non-Western music, priors need adjustment.

---

### What This Schema Doesn't Promise

- It does not diagnose. It does not infer mental state. It does not claim to know the listener.
- It surfaces where music clusters, with what themes, and how that shifts over time.
- The interpretation is the user's to make.
