# 02 - Output Schema & Data Contract

## Decision

The frontend must not assume the aspirational schema is already emitted by the Python backend.

Use two explicit contracts:

- `ReportV0`: the current backend JSON produced by `orpheus report`.
- `ReportV1`: the normalized frontend contract consumed by React components.

Upload/parsing code may accept both versions. UI components should consume only `ReportV1`.

---

## ReportV0: Current Backend Output

Current backend reports are shaped by `orpheus/output/assemble.py`.

```typescript
interface ReportV0 {
  generated_at: string
  model_version: string
  windows: {
    state: BackendWindow
    trait: BackendWindow
  }
  shifts: Shift[]
  trends: TrendEvent[]
  co_occurrences: BackendCoOccurrence[]
  clusters: BackendCluster[]
  safety_flags: SafetyFlag[]
}

interface BackendWindow {
  top_emotions: PrevalenceItem[]
  top_themes: PrevalenceItem[]
  depth_label: DepthLabel
  top_artists: Array<{ artist: string; weight: number }>
  top_tracks: TopTrack[]
}

interface PrevalenceItem {
  category: EmotionCategory | ThemeCategory
  prevalence: PrevalenceLabel
}
```

Important limitations:

- No top-level `metadata` object.
- No required `narrative` field.
- No full state/trait score distributions in the emitted report.
- No `depth_distribution`; only `depth_label`.
- No weekly time-series points; `trends` are event summaries.
- Clusters do not include track lists or album art.

---

## ReportV1: Target Frontend Contract

```typescript
interface OrpheusReport {
  metadata: ReportMetadata
  state: WindowScores
  trait: WindowScores
  shifts: Shift[]
  trends: TrendEvent[]
  clusters: ClusterSummary[]
  co_occurrences: CoOccurrence[]
  safety_flags: SafetyFlag[]
  narrative?: NarrativeSummary
}

interface ReportMetadata {
  generated_at: string
  model_version: string
  schema_version: '1.0'
  report_id?: string
  config_sha256?: string
  output_hash?: string
  note?: string
}

interface WindowScores {
  emotion: Partial<Record<EmotionCategory, number>>
  theme: Partial<Record<ThemeCategory, number>>
  top_emotions: PrevalenceItem[]
  top_themes: PrevalenceItem[]
  depth_label: DepthLabel
  top_artists: Array<{ artist: string; weight: number }>
  top_tracks: TopTrack[]
}

interface TopTrack {
  uri: string
  name?: string
  artist?: string
  album?: string
  weight?: number
  play_count?: number
  depth_score?: number
  depth_label?: DepthLabel
  emotion_scores?: Partial<Record<EmotionCategory, number>>
  theme_scores?: Partial<Record<ThemeCategory, number>>
}
```

`emotion` and `theme` are `Partial` during the compatibility period because `ReportV0` does not emit numeric distributions. Once the backend emits the full maps, the frontend can tighten these to complete `Record` types.

`top_tracks` are "Primary tracks": tracks ranked by positive net signed,
time-decayed engagement contribution for the selected window. They are not a raw
play-count list. See `../docs/D1_primary_tracks.md`.

---

## Categories

```typescript
type EmotionCategory =
  | 'joyful_activation'
  | 'triumphant_power'
  | 'peacefulness'
  | 'tenderness'
  | 'nostalgia_longing'
  | 'sadness_melancholy'
  | 'tension_anxiety'
  | 'anger_defiance'

type ThemeCategory =
  | 'interpersonal_devotion'
  | 'heartbreak_loss'
  | 'adversity_resilience'
  | 'identity_autonomy'
  | 'status_ambition'
  | 'hedonism_escape'
  | 'place_heritage'
  | 'existentialism_spirituality'

type DepthLabel = 'surface' | 'engaged' | 'immersive'
type PrevalenceLabel = 'dominant' | 'high' | 'moderate' | 'present' | 'not represented'
```

---

## Shifts

The backend already emits state-vs-trait shifts.

```typescript
interface Shift {
  category: EmotionCategory | ThemeCategory
  axis: 'emotion' | 'theme'
  direction: 'elevated' | 'faded'
  delta: number
  narrative: string
}
```

Usage:

- Summary bullets
- State-vs-trait comparison
- Category detail panels

---

## Trends

Current backend trends are event summaries, not weekly chart series.

```typescript
interface TrendEvent {
  category: EmotionCategory | ThemeCategory
  axis: 'emotion' | 'theme'
  direction: 'rising' | 'falling' | 'spiking' | 'declining'
  magnitude: 'minor' | 'notable'
  narrative: string
}
```

MVP usage:

- Ranked "recent movement" list
- Summary bullets
- Optional category chips

Deferred usage:

- Multi-line 12-week chart, which requires a future `WeeklyTrend[]` contract.

```typescript
interface WeeklyTrend {
  week: number
  week_start: string
  week_end: string
  emotion: Record<EmotionCategory, number>
  theme: Record<ThemeCategory, number>
}
```

---

## Clusters

Current backend clusters are summaries.

```typescript
interface ClusterSummary {
  label: string
  centroid_avd: [number, number, number]
  dominant_emotions: Array<{ category: EmotionCategory; weight: number }>
  dominant_themes: Array<{ category: ThemeCategory; weight: number }>
  share_of_listening?: string
  track_count: number
}
```

Track-level drill-down is deferred until the backend emits cluster members.

Future shape:

```typescript
interface ClusterWithTracks extends ClusterSummary {
  tracks: Track[]
}

interface Track {
  uri: string
  name?: string
  artist?: string
  album?: string
  album_art_url?: string
  emotion_scores?: Record<EmotionCategory, number>
  theme_scores?: Record<ThemeCategory, number>
  depth_score?: number
  depth_label?: DepthLabel
  play_count?: number
  url?: string
}
```

---

## Co-Occurrences

Current backend co-occurrences use a compact pair format.

```typescript
interface BackendCoOccurrence {
  pair: [EmotionCategory, ThemeCategory]
  strength: 'strong' | 'moderate'
  observed: number
  expected: number
  narrative: string
}

interface CoOccurrence extends BackendCoOccurrence {
  emotion: EmotionCategory
  theme: ThemeCategory
}
```

The parser should derive `emotion` and `theme` from `pair` for easier UI rendering.

---

## Narrative

Narrative is optional in `ReportV1`.

```typescript
interface NarrativeSummary {
  headline: string
  key_insights: string[]
  caveats?: string[]
}
```

MVP can compose this from:

- Top state emotion/theme labels
- Largest `shifts`
- Notable `trends`
- Strong `co_occurrences`

Backend-generated longform narrative can be added later without changing component contracts.

---

## Safety Flags

```typescript
interface SafetyFlag {
  flag_type: 'rumination_alert' | 'other'
  severity: 'warning' | 'caution' | 'info'
  message: string
  recommendation?: string
  triggered_at?: string
}
```

Safety output is optional and should be presented gently.

---

## Zod Strategy

Use separate schemas and a normalizer.

```typescript
const reportV0Schema = z.object({
  generated_at: z.string().datetime(),
  model_version: z.string(),
  windows: z.object({
    state: backendWindowSchema,
    trait: backendWindowSchema,
  }),
  shifts: z.array(shiftSchema).default([]),
  trends: z.array(trendEventSchema).default([]),
  co_occurrences: z.array(backendCoOccurrenceSchema).default([]),
  clusters: z.array(clusterSummarySchema).default([]),
  safety_flags: z.array(safetyFlagSchema).default([]),
})

const reportV1Schema = z.object({
  metadata: reportMetadataSchema,
  state: windowScoresSchema,
  trait: windowScoresSchema,
  shifts: z.array(shiftSchema).default([]),
  trends: z.array(trendEventSchema).default([]),
  co_occurrences: z.array(coOccurrenceSchema).default([]),
  clusters: z.array(clusterSummarySchema).default([]),
  safety_flags: z.array(safetyFlagSchema).default([]),
  narrative: narrativeSummarySchema.optional(),
})

export function parseOrpheusReport(input: unknown): OrpheusReport {
  const v1 = reportV1Schema.safeParse(input)
  if (v1.success) return v1.data

  const v0 = reportV0Schema.parse(input)
  return normalizeReportV0(v0)
}
```

Normalization rule:

```typescript
function normalizeReportV0(report: ReportV0): OrpheusReport {
  return {
    metadata: {
      generated_at: report.generated_at,
      model_version: report.model_version,
      schema_version: '1.0',
    },
    state: normalizeWindow(report.windows.state),
    trait: normalizeWindow(report.windows.trait),
    shifts: report.shifts,
    trends: report.trends,
    co_occurrences: report.co_occurrences.map((item) => ({
      ...item,
      emotion: item.pair[0],
      theme: item.pair[1],
    })),
    clusters: report.clusters,
    safety_flags: report.safety_flags,
    narrative: composeNarrative(report),
  }
}
```

---

## Backend Upgrade Path

The fastest backend improvement is to preserve fields already computed before report formatting:

- Add full `state.emotion` and `state.theme` maps from aggregation output.
- Add full `trait.emotion` and `trait.theme` maps.
- Keep `top_emotions`, `top_themes`, and `depth_label` for quick rendering.
- Add `metadata.schema_version`.

Later upgrades:

- Add depth distribution.
- Add weekly trend series.
- Add cluster member tracks.
- Add backend-generated narrative.

---

## Validation Rules

MVP parser should:

1. Accept valid `ReportV0` and `ReportV1`.
2. Reject non-JSON and unrelated JSON files.
3. Warn, not fail, when optional fields are absent.
4. Validate category strings against known emotion/theme categories.
5. Validate numeric scores are in `[0, 1]` when present.
6. Never require track-level fields for MVP.

---

## Example Minimal ReportV1

```json
{
  "metadata": {
    "generated_at": "2026-05-27T15:30:00Z",
    "model_version": "bart-mnli-v1+mpnet-v1",
    "schema_version": "1.0"
  },
  "state": {
    "emotion": { "nostalgia_longing": 0.35 },
    "theme": { "heartbreak_loss": 0.22 },
    "top_emotions": [{ "category": "nostalgia_longing", "prevalence": "dominant" }],
    "top_themes": [{ "category": "heartbreak_loss", "prevalence": "high" }],
    "depth_label": "engaged",
    "top_artists": [],
    "top_tracks": []
  },
  "trait": {
    "emotion": { "nostalgia_longing": 0.28 },
    "theme": { "heartbreak_loss": 0.15 },
    "top_emotions": [{ "category": "nostalgia_longing", "prevalence": "dominant" }],
    "top_themes": [{ "category": "heartbreak_loss", "prevalence": "high" }],
    "depth_label": "engaged",
    "top_artists": [],
    "top_tracks": []
  },
  "shifts": [],
  "trends": [],
  "clusters": [],
  "co_occurrences": [],
  "safety_flags": []
}
```

---

*Last updated: 2026-05-27*
