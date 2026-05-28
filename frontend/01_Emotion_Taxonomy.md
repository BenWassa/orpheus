# 01 — Emotion & Theme Taxonomy

## Emotion Axis (8 Categories)

Emotions are anchored in a continuous 2D space: **Valence (V)** × **Arousal (A)** with **Depth (D)** tracked separately as a third dimension.

### Category Definitions

| # | Category | V | A | Description |
|---|---|---|---|---|
| 1 | **Joyful Activation** | +0.8 | +0.6 | Uplifting, energetic joy; peak happiness meets motion |
| 2 | **Triumphant Power** | +0.6 | +0.8 | Confident, striving forward; winning, overcoming, solid ground |
| 3 | **Peacefulness / Serenity** | +0.8 | −0.7 | Calm, still, meditative; safe release, no tension |
| 4 | **Tenderness** | +0.7 | −0.3 | Intimate, soft, vulnerable connection; love without urgency |
| 5 | **Nostalgia / Longing** | +0.2 | −0.4 | Wistful, questioning, future-oriented; "where are you?" |
| 6 | **Sadness / Melancholy** | −0.8 | −0.6 | Deep sorrow, acceptance of loss; resigned, defeated |
| 7 | **Tension / Anxiety** | −0.6 | +0.5 | Unsettled, constricted, out of control; panic without release |
| 8 | **Anger / Defiance** | −0.7 | +0.8 | Raw confrontation, destructive energy; righteous or destructive rage |

### Acoustic Markers (Detection Cues)

| Emotion | Tempo | Mode | Harmony | Timbre | Rhythm | Vocal |
|---|---|---|---|---|---|---|
| Joyful | Fast (120+) | Major | Consonant, bright | Bells, synths, horns | Regular, energetic | Clean, soaring |
| Triumph | Fast (100–120) | Major | Stable | Brassy, orchestral | Steady, powerful | Clear, powerful |
| Peace | Slow (60–80) | Major/ambiguous | Drone-like | Pads, strings | Minimal | Soft or absent |
| Tender | Slow–Moderate | Major/minor | Consonant, warm | Vibrato, mellow | Gentle, flowing | Intimate, breathy |
| Longing | Moderate (80–100) | Minor→Major | Unresolved | Minor-third sighs, string swoops | Irregular, hesitant | Questioning inflection |
| Sadness | Slow (60–80) | Minor | Descending, narrow-range | Dark, muted | Sparse, heavy | Low register, aspirant |
| Tension | Irregular | Ambiguous | Dissonant, unstable | Harsh, distorted | Syncopated, jagged | Strained, stuttering |
| Anger | Fast (100+) | Minor or dissonant | Harsh, unstable | Distorted, aggressive | Irregular, aggressive | Shouted, growled, distorted |

### Lyric Markers (Content Cues)

| Emotion | Lyric Patterns | Vocabulary | Grammar | Pronouns |
|---|---|---|---|---|
| Joyful | Celebration, sensory delight, triumph, optimism | "fly", "dance", "bright", "high", "alive" | Exclamation, imperatives | 1st/2nd person plural |
| Triumph | Victory, overcoming, unbroken, resilience | "rise", "stronger", "unbreakable", "conquer" | Declarative, assertion | 1st person singular |
| Peace | Solitude, nature, breathing, release, letting go | "still", "breathe", "drift", "rest", "dissolve" | Stative, passive | 1st person or imperative |
| Tender | Intimacy, connection, "you and I", vulnerability | "you", "hold", "soft", "close", "heart" | Intimate address, conditional | 2nd person, "we" |
| Longing | Interrogative, future-oriented, absence | "where", "when", "will you", "if only" | Questions, conditionals | 2nd person absent (questions to phantom) |
| Sadness | Finality, absolute loss, resignation | "nothing left", "over", "never", "gone", "end" | Past-tense reflection, passive | 1st person singular, isolated |
| Tension | Paranoia, confinement, loss of control, threat | "trapped", "can't breathe", "breaking", "falling" | Fragment, repetition, broken | Impersonal or 1st person victim |
| Anger | Confrontation, blame, destruction, raw accusation | "burn", "destroy", "fuck", "hate", "kill" | Imperative, direct address | 2nd person accusation or 1st defiant |

### Diagnostic Boundaries (Resolving Similar Pairs)

**Longing vs Sadness:**
- **Longing** = interrogative, future-oriented, keeps hope alive  
- **Sadness** = resigned, final, the hope is gone  
- Acoustically: Longing uses minor-to-major transitions and pitch movement; Sadness stays narrow-range, descending  

**Power vs Anger:**
- **Power** = consonant, stable, clean vocals; confidence in winning  
- **Anger** = dissonant, distorted, rough articulation; rage for its own sake  

**Tenderness vs Peacefulness:**
- **Tenderness** = interpersonal (addresses "you"), vibrato, emotional intensity  
- **Peacefulness** = solitary, drone-like, flat emotional surface  

---

## Life Themes Axis (8 Categories)

Themes are discrete **semantic domains** that appear in lyrics and can be inferred from track context. Each track gets **multi-label** scoring (top-n, n ≥ 3).

### Category Definitions

| # | Theme | Definition | Primary Markers |
|---|---|---|---|
| 1 | **Interpersonal Devotion** | Romantic, familial, friendship celebration; attachment and bonding | "you and I", "forever", "together", intimate pronouns, family terms |
| 2 | **Heartbreak, Loss, Betrayal** | Relational dissolution, unrequited love, infidelity, grief | "lost you", "betrayed", "gone", past-tense intimacy, accusation, absence |
| 3 | **Adversity & Resilience** | Survival, depression, trauma, overcoming, endurance, mental health | "struggle", "broken", "rise up", dual trauma + recovery vocabulary |
| 4 | **Identity & Autonomy** | Self-actualization, anti-conformity, authenticity, rebellion, independence | "I am", "not who you think", "break free", first-person singular power, refusal |
| 5 | **Status & Ambition** | Wealth, fame, dominance, competitive hierarchy, material ambition | "rich", "famous", "boss", "win", luxury nouns, victory assertions, hierarchical language |
| 6 | **Hedonism & Escapism** | Sensory pleasure, party, substance use, release, living in the moment | "party", "dance", "high", "escape", kinetic verbs, substance references, temporal urgency |
| 7 | **Place & Heritage** | Geographic grounding, family, past, cultural roots, nostalgia, memory | Place nouns (city, south, home), family terms, memory markers, ancestral language |
| 8 | **Existentialism & Spirituality** | Death, meaning, mortality, faith, cosmic purpose, transience, the void | "death", "god", "meaning", "why", metaphysical vocabulary, cosmic imagery, the infinite |

### Content Validation (Cross-Reference Kwon et al. 2021)

Themes were validated against content analysis of 1,052 songs across Hip-Hop/R&B, Pop, Country, Rock/Metal, Latin (Kwon, 2021). Coverage >85% across genres; some genre skew (Status dominates Hip-Hop, Heritage dominates Country).

---

## Classification Rules & Constraints

### Multi-Label, Top-N
- Each track gets **at least 3 theme scores** (can be higher)  
- Scores are **probabilistic** (0.0–1.0), not binary  
- Don't collapse to single strongest theme; capture nuance  

### Multimodal Late Fusion
- **Lyrics dominate** negative-valence detection (words matter more for sadness)  
- **Acoustics dominate** arousal detection (rhythm/tempo signals energy)  
- **Conflict resolution**: If lyrics say "sad" but acoustics say "energetic", use dynamic weighting rather than averaging  

### Instrumental Fallback
- Tracks without lyrics (instrumentals) get **acoustic-only classification**  
- **Theme axis confidence is lowered** (abstract or metaphorical content can't be inferred)  
- Crowd-sourced annotations (Genius, Songfacts) used where available to resolve ambiguity  

### Artist Prior Layer
- Artist-level aggregate scores provide **baseline signal** (stable identity layer)  
- Song-level data **refines or overrides** (state-specific layer)  
- Artist with 100 plays of "sad" establishes prior; one new "happy" song doesn't flip it  

---

## Frontend Integration Notes

### Vocabulary for UI Labels
Use consistent, user-facing language:

| Backend | Frontend (User Label) |
|---|---|
| `joyful_activation` | Joyful Activation |
| `triumphant_power` | Triumphant Power |
| `peacefulness` | Peacefulness |
| `tenderness` | Tenderness |
| `nostalgia_longing` | Nostalgia & Longing |
| `sadness_melancholy` | Sadness |
| `tension_anxiety` | Tension & Anxiety |
| `anger_defiance` | Anger & Defiance |
| `interpersonal_devotion` | Connection & Devotion |
| `heartbreak_loss` | Heartbreak & Loss |
| `adversity_resilience` | Resilience |
| `identity_autonomy` | Identity & Autonomy |
| `status_ambition` | Ambition |
| `hedonism_escape` | Pleasure & Escapism |
| `place_heritage` | Place & Heritage |
| `existentialism_spirituality` | Meaning & Spirituality |

### Visual Encoding Recommendation
- **Emotion categories**: Use 8-color palette (one per category); ensure colorblind-safe  
- **Theme categories**: Use secondary palette (8 colors or grayscale + icons)  
- **Depth**: Encode as bubble size (small = surface, large = immersive)  
- **Confidence/Strength**: Encode as opacity (faint = low confidence, solid = high confidence)  

### Hover/Tooltip Content
When user hovers over emotion or theme cluster, show:
- Category name  
- Prevalence label (Dominant / High / Moderate / Present)  
- Top 2–3 associated tracks  
- Score (e.g., 0.34)  

---

## Reference: Emotion Space Visualization

The Valence-Arousal-Depth (VAD) 3D space maps as:

```
                     High Arousal (+0.8)
                            ↑
                    ╔═══════╩═══════╗
                    ║               ║
    Anger/Defiance  ║   Triumph     ║  Joyful Activation
      (−0.7, +0.8) ║   (+0.6, +0.8)║  (+0.8, +0.6)
                    ║               ║
   Low Valence ←────╫───────o───────╫────→ High Valence
    (Negative)      ║               ║        (Positive)
                    ║               ║
   Tension/Anxiety  ║  Longing      ║  Peacefulness/Serenity
      (−0.6, +0.5)  ║  (+0.2, −0.4) ║  (+0.8, −0.7)
                    ║               ║
   Sadness/Melancholy║ Tenderness   ║
      (−0.8, −0.6)  ║ (+0.7, −0.3) ║
                    ║               ║
                    ╚═══════╥═══════╝
                        ↓
                    Low Arousal (−0.7)

Depth (D) = Third dimension (size/glyph encoding)
  Small = Surface (D < 0.33)
  Medium = Engaged (0.33 ≤ D < 0.66)
  Large = Immersive (D ≥ 0.66)
```

---

## Additional Resources

- Full methodology: See `../docs/C2_methodology_spec.md` in repo  
- Research grounding: See `../docs/C2_methodology_spec.md` (references R1–R3)  
- Example report: Generated during backend test runs; see `../tests/fixtures/sample_export.json`  

---

*Last updated: 2026-05-27*
