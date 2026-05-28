# 06 — Component Architecture

## Component Hierarchy

```
<App>
  ├── <Router>
  │   ├── <UploadPage>
  │   └── <DashboardPage>
  │       ├── <Header>
  │       ├── <HeroSummary>
  │       │   ├── <StateVsTraitComparison>
  │       │   ├── <KeyInsightsBullets>
  │       │   └── <NarrativeText>
  │       ├── <MainContent>
  │       │   ├── <EmotionScatter>
  │       │   ├── <ThemePrevalence>
  │       │   └── <TrendEvents>
  │       ├── <CoOccurrenceMatrix>
  │       ├── <ClusterSummaryList>
  │       │   └── <ClusterSummaryCard>
  │       ├── <TrackDrillDown> (deferred until backend emits cluster tracks)
  │       ├── <ExportModal>
  │       └── <Footer>
  └── <Providers> (Zustand store, theme)
```

---

## Core Components

### 1. App (Root)

```typescript
// src/App.tsx
import { useAppStore } from './store'
import Router from './Router'
import { useEffect } from 'react'

export const App = () => {
  const { report } = useAppStore()

  useEffect(() => {
    // Initialize app state, check for persisted data
  }, [])

  return <Router reportReady={!!report} />
}
```

**Responsibilities**:
- Mount Zustand store provider  
- Initialize app state  
- Route between pages  

---

### 2. UploadPage

```typescript
// src/pages/UploadPage.tsx
import { useDropzone } from 'react-dropzone'
import { useAppStore } from '../store'
import { parseOrpheusReport } from '../schemas'

export const UploadPage = () => {
  const setReport = useAppStore((s) => s.setReport)
  const navigate = useNavigate()

  const onDrop = async (files: File[]) => {
    try {
      const text = await files[0].text()
      const json = JSON.parse(text)
      const report = parseOrpheusReport(json)
      setReport(report)
      navigate('/dashboard')
    } catch (error) {
      // Show error modal
    }
  }

  const { getRootProps, getInputProps } = useDropzone({
    accept: { 'application/json': ['.json'] },
    onDrop,
  })

  return (
    <div className="hero-upload">
      <h1>Decode Your Emotional Underworld</h1>
      <p>Upload your Orpheus analysis report to begin exploring your listening patterns.</p>
      <div {...getRootProps()} className="dropzone">
        <input {...getInputProps()} />
        <p>Drag your report here, or click to select</p>
      </div>
    </div>
  )
}
```

**Props**: None  
**State**: Upload progress (loading, error)  
**Actions**: Navigate to dashboard on success  

---

### 3. DashboardPage (Container)

```typescript
// src/pages/DashboardPage.tsx
import { useAppStore } from '../store'
import { HeroSummary } from '../components/HeroSummary'
import { EmotionScatter } from '../components/EmotionScatter'
import { ThemePrevalence } from '../components/ThemePrevalence'
import { TrendEvents } from '../components/TrendEvents'
import { ClusterSummaryList } from '../components/ClusterSummaryList'

export const DashboardPage = () => {
  const report = useAppStore((s) => s.report)

  if (!report) return <Navigate to="/" />

  return (
    <div className="dashboard">
      <Header />
      <HeroSummary report={report} />
      <MainContent>
        <EmotionScatter report={report} />
        <ThemePrevalence report={report} />
        <TrendEvents report={report} />
      </MainContent>
      <CoOccurrenceMatrix report={report} />
      <ClusterSummaryList report={report} />
      <Footer />
    </div>
  )
}
```

**Props**: None (data from Zustand store)  
**Responsibilities**:
- Assemble all dashboard components  
- Pass report data down  
- Manage modal states (export, drill-down)  

---

### 4. HeroSummary

```typescript
// src/components/HeroSummary.tsx
import { OrpheusReport } from '../schemas'

interface HeroSummaryProps {
  report: OrpheusReport
}

export const HeroSummary: React.FC<HeroSummaryProps> = ({ report }) => {
  const topEmotion = report.state.top_emotions[0]?.category
  const topTheme = report.state.top_themes[0]?.category
  const headline = report.narrative?.headline ?? composeHeadline(report)

  return (
    <section className="hero">
      <h1>{headline}</h1>

      <div className="state-vs-trait">
        <StateCard
          label="Current (3 days)"
          emotion={topEmotion}
          theme={topTheme}
          shifts={report.shifts.slice(0, 3)}
        />
        <StateCard
          label="Baseline (90 days)"
          emotion={report.trait.top_emotions[0]?.category}
          theme={report.trait.top_themes[0]?.category}
        />
      </div>

      <div className="insights">
        {getKeyInsights(report).map((insight) => (
          <InsightBullet key={insight.id} insight={insight} />
        ))}
      </div>
    </section>
  )
}
```

**Props**:
- `report: OrpheusReport`  

**Sub-components**:
- `<StateCard>`  
- `<InsightBullet>`  

**Helpers**:
- `getTopEmotion()`  
- `getTopTheme()`  
- `computeDelta()`  

---

### 5. EmotionScatter

```typescript
// src/components/EmotionScatter.tsx
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'
import { OrpheusReport } from '../schemas'
import { useAppStore } from '../store'

interface EmotionScatterProps {
  report: OrpheusReport
}

export const EmotionScatter: React.FC<EmotionScatterProps> = ({ report }) => {
  const [showTrait, setShowTrait] = useAppStore((s) => [s.showTrait, s.setShowTrait])

  // Transform report data into scatter points
  const stateData = transformToScatterData(report.state, 'state')
  const traitData = transformToScatterData(report.trait, 'trait')

  const data = showTrait ? [...stateData, ...traitData] : stateData

  return (
    <div className="emotion-scatter-container">
      <div className="header">
        <h2>Emotion Distribution</h2>
        <Toggle
          label="Show Baseline"
          checked={showTrait}
          onChange={setShowTrait}
        />
      </div>

      <ScatterChart width={600} height={400} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="valence" />
        <YAxis dataKey="arousal" />
        <Tooltip content={<EmotionTooltip />} />
        <Scatter name="Current" data={stateData} fill="#8b5cf6" />
        {showTrait && <Scatter name="Baseline" data={traitData} fill="#d1d5db" />}
      </ScatterChart>

      <Legend emotions={getVisibleEmotionKeys(report.state)} />
    </div>
  )
}

// Helper to map emotion -> scatter point
function transformToScatterData(windowScores, windowType) {
  const scoredEntries = Object.entries(windowScores.emotion)
  const fallbackEntries = windowScores.top_emotions.map((item) => [item.category, 0] as const)

  return (scoredEntries.length > 0 ? scoredEntries : fallbackEntries).map(([emotion, score]) => ({
    valence: EMOTION_COORDS[emotion].valence,
    arousal: EMOTION_COORDS[emotion].arousal,
    depth: Math.max(score, 0.12),
    emotion,
    windowType,
  }))
}

const EMOTION_COORDS = {
  joyful_activation: { valence: 0.8, arousal: 0.6 },
  // ... etc
}
```

**Props**:
- `report: OrpheusReport`  

**State**:
- `showTrait: boolean`  

**Sub-components**:
- `<EmotionTooltip>`  
- `<Toggle>`  
- `<Legend>`  

---

### 6. ThemePrevalence

```typescript
// src/components/ThemePrevalence.tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts'
import { OrpheusReport, PrevalenceLabel } from '../schemas'

interface ThemePrevalenceProps {
  report: OrpheusReport
}

export const ThemePrevalence: React.FC<ThemePrevalenceProps> = ({ report }) => {
  const data = Object.entries(report.state.theme)
    .map(([theme, score]) => ({
      theme: THEME_LABELS[theme],
      score,
      prevalence: computePrevalence(score),
      icon: THEME_ICONS[theme],
    }))
    .sort((a, b) => b.score - a.score)

  return (
    <div className="theme-prevalence">
      <h2>Life Themes</h2>

      <BarChart width={400} height={300} data={data} layout="vertical">
        <XAxis type="number" />
        <YAxis dataKey="theme" type="category" width={150} />
        <Tooltip content={<ThemeTooltip />} />
        <Bar dataKey="score" fill="#6ee7b7" />
      </BarChart>

      <ThemeGrid themes={data} />
    </div>
  )
}

// Sub-component: Grid alternative to bar chart
function ThemeGrid({ themes }) {
  return (
    <div className="grid grid-cols-2 gap-4">
      {themes.map((theme) => (
        <ThemeCard key={theme.theme} theme={theme} />
      ))}
    </div>
  )
}

// Sub-component: Individual theme card
function ThemeCard({ theme }) {
  return (
    <div className="card">
      <div className="icon">{theme.icon}</div>
      <div className="label">{theme.theme}</div>
      <div className="badge">{theme.prevalence}</div>
    </div>
  )
}
```

**Props**:
- `report: OrpheusReport`  

**Sub-components**:
- `<ThemeTooltip>`  
- `<ThemeGrid>`  
- `<ThemeCard>`  

---

### 7. TrendEvents

```typescript
// src/components/TrendEvents.tsx
import { OrpheusReport } from '../schemas'

interface TrendEventsProps {
  report: OrpheusReport
}

export const TrendEvents: React.FC<TrendEventsProps> = ({ report }) => {
  const trends = report.trends
    .filter((trend) => trend.magnitude === 'notable' || trend.direction === 'spiking')
    .slice(0, 6)

  return (
    <section className="trend-events">
      <h2>Recent Movement</h2>
      <ul>
        {trends.map((trend) => (
          <TrendEventItem key={`${trend.axis}-${trend.category}`} trend={trend} />
        ))}
      </ul>
    </section>
  )
}
```

**Props**:
- `report: OrpheusReport`  

**Sub-components**:
- `<TrendEventItem>`  

**Deferred**:
- `<TrendTimeline>` with line charts once the backend emits weekly time-series data.  

---

### 8. ClusterSummaryList

```typescript
// src/components/ClusterSummaryList.tsx
import { OrpheusReport } from '../schemas'

interface ClusterSummaryListProps {
  report: OrpheusReport
}

export const ClusterSummaryList: React.FC<ClusterSummaryListProps> = ({ report }) => {
  return (
    <section className="cluster-summary-list">
      <h2>Listening Clusters</h2>
      <div className="cluster-grid">
        {report.clusters.map((cluster) => (
          <ClusterSummaryCard key={cluster.label} cluster={cluster} />
        ))}
      </div>
    </section>
  )
}
```

**Props**:
- `report: OrpheusReport`  

**Sub-components**:
- `<ClusterSummaryCard>`  

---

### 9. TrackDrillDown (Deferred Modal)

Do not implement this for MVP unless the backend report includes cluster member tracks.

```typescript
// src/components/TrackDrillDown.tsx
import { Dialog, DialogContent } from '@radix-ui/react-dialog'
import { TrackList } from './TrackList'
import { OrpheusReport } from '../schemas'

interface TrackDrillDownProps {
  isOpen: boolean
  onClose: () => void
  emotion?: string
  theme?: string
  report: OrpheusReport
}

export const TrackDrillDown: React.FC<TrackDrillDownProps> = ({
  isOpen,
  onClose,
  emotion,
  theme,
  report,
}) => {
  const tracks = filterTracks(report.clusters, emotion, theme)

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <h2>
          {emotion} + {theme}
        </h2>
        <TrackList tracks={tracks} />
      </DialogContent>
    </Dialog>
  )
}
```

**Props**:
- `isOpen: boolean`  
- `onClose: () => void`  
- `emotion?: string`  
- `theme?: string`  
- `report: OrpheusReport`  

**Sub-components**:
- `<TrackList>`  

---

### 9. TrackCard

```typescript
// src/components/TrackCard.tsx
import { Track } from '../schemas'
import { Dialog, DialogTrigger } from '@radix-ui/react-dialog'
import { ScoreBreakdown } from './ScoreBreakdown'

interface TrackCardProps {
  track: Track
  onSpotifyClick: (uri: string) => void
}

export const TrackCard: React.FC<TrackCardProps> = ({ track, onSpotifyClick }) => {
  return (
    <div className="track-card">
      <img src={track.album_art_url} alt={track.album} className="album-art" />

      <div className="content">
        <h3>{track.name}</h3>
        <p className="artist">{track.artist}</p>
        <p className="album">{track.album}</p>

        <div className="tags">
          {Object.entries(track.emotion_scores)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 2)
            .map(([emotion, score]) => (
              <Tag key={emotion} emotion={emotion} score={score} />
            ))}
        </div>
      </div>

      <div className="actions">
        <Dialog>
          <DialogTrigger asChild>
            <Button>View Scores</Button>
          </DialogTrigger>
          <ScoreBreakdown track={track} />
        </Dialog>

        <Button onClick={() => onSpotifyClick(track.uri)}>Play</Button>
      </div>
    </div>
  )
}
```

**Props**:
- `track: Track`  
- `onSpotifyClick: (uri: string) => void`  

**Sub-components**:
- `<ScoreBreakdown>`  
- `<Tag>`  

---

### 10. ScoreBreakdown (Modal Content)

```typescript
// src/components/ScoreBreakdown.tsx
import { Track, EmotionCategory, ThemeCategory } from '../schemas'
import { EMOTION_LABELS, THEME_LABELS } from '../lib/labels'

interface ScoreBreakdownProps {
  track: Track
}

export const ScoreBreakdown: React.FC<ScoreBreakdownProps> = ({ track }) => {
  const topEmotions = Object.entries(track.emotion_scores)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3)

  const topThemes = Object.entries(track.theme_scores)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3)

  return (
    <div className="score-breakdown">
      <h3>Why did this score high?</h3>

      <section>
        <h4>Emotions</h4>
        {topEmotions.map(([emotion, score]) => (
          <ScoreRow key={emotion} label={EMOTION_LABELS[emotion]} score={score} />
        ))}
      </section>

      <section>
        <h4>Themes</h4>
        {topThemes.map(([theme, score]) => (
          <ScoreRow key={theme} label={THEME_LABELS[theme]} score={score} />
        ))}
      </section>

      <section>
        <h4>Depth</h4>
        <p>{track.depth_label} listening ({(track.depth_score * 100).toFixed(0)}%)</p>
      </section>
    </div>
  )
}

function ScoreRow({ label, score }) {
  return (
    <div className="score-row">
      <span>{label}</span>
      <ProgressBar value={score} />
      <span className="value">{(score * 100).toFixed(0)}%</span>
    </div>
  )
}
```

**Props**:
- `track: Track`  

**Sub-components**:
- `<ScoreRow>`  
- `<ProgressBar>`  

---

## State Management

### Zustand Store

```typescript
// src/store.ts
import { create } from 'zustand'
import { OrpheusReport } from './schemas'

export interface AppState {
  // Data
  report: OrpheusReport | null
  setReport: (report: OrpheusReport) => void

  // UI State
  showTrait: boolean
  setShowTrait: (show: boolean) => void

  // Modals
  activeModal: 'export' | 'drilldown' | null
  setActiveModal: (modal: AppState['activeModal']) => void
  drilldownEmotion?: string
  drilldownTheme?: string
  setDrilldown: (emotion?: string, theme?: string) => void

  // Filters
  filters: {
    minConfidence: number
    selectedTheme?: string
  }
  setFilters: (filters: AppState['filters']) => void
}

export const useAppStore = create<AppState>((set) => ({
  report: null,
  setReport: (report) => set({ report }),

  showTrait: false,
  setShowTrait: (show) => set({ showTrait: show }),

  activeModal: null,
  setActiveModal: (modal) => set({ activeModal: modal }),
  drilldownEmotion: undefined,
  drilldownTheme: undefined,
  setDrilldown: (emotion, theme) => set({ drilldownEmotion: emotion, drilldownTheme: theme }),

  filters: { minConfidence: 0 },
  setFilters: (filters) => set({ filters }),
}))
```

---

## Data Flow Diagram

```
User uploads JSON
  ↓
[File → Text → JSON parse → Zod validate → normalize to ReportV1]
  ↓
Store in Zustand (report state)
  ↓
All child components subscribe to store
  ↓
Components render via derived data:
  - EmotionScatter reads report.state emotion/theme maps when available
  - ThemePrevalence reads top themes and numeric theme scores when available
  - TrendEvents reads report.trends event summaries
  - ClusterSummaryList reads report.clusters
  ↓
User interacts (click, toggle, filter)
  ↓
Update Zustand state (filters, modals, etc.)
  ↓
Components re-render with new derived data
```

---

## Styling Approach

All components use **Tailwind utility classes** + **CSS modules** for scoped styles.

```typescript
// src/components/EmotionScatter.tsx
import styles from './EmotionScatter.module.css'

export const EmotionScatter = () => {
  return (
    <div className={`${styles.container} flex flex-col gap-4`}>
      <h2 className="text-2xl font-semibold">Emotion Distribution</h2>
      {/* ... */}
    </div>
  )
}
```

```css
/* src/components/EmotionScatter.module.css */
.container {
  background: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
```

---

*Last updated: 2026-05-27*
