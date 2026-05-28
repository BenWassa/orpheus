# 07 — API Contract & Data Flow

## Overview

For MVP, the frontend is **completely decoupled from the backend**. Users download a JSON report from the backend CLI, then drag-and-drop it into the frontend. No network calls, no API integration.

**Future phases** may add:
- Live report generation (user logs in with Spotify, backend generates on-demand)  
- Report history / cloud storage  
- Batch analysis  
- Collaborative features  

This document covers MVP (static report) + optional Phase 2 (live API) patterns.

---

## MVP: Static Report Flow

### Step 1: Generate Report (Backend)

User runs backend CLI:
```bash
orpheus run-all --source data/raw/streaming_history.json
orpheus report --out data/output/reports/my_report.json
```

**Output**: `my_report.json` (2–5 MB typical)

**Report schema**: See `02_Output_Schema.md`

---

### Step 2: Upload Report (Frontend)

User drags JSON file into frontend:

```typescript
// src/pages/UploadPage.tsx
const onDrop = async (files: File[]) => {
  const file = files[0]
  const text = await file.text()          // Read file
  const json = JSON.parse(text)           // Parse JSON
  const report = parseOrpheusReport(json) // Validate and normalize to ReportV1
  setReport(report)                       // Store normalized report in Zustand
  navigate('/dashboard')                  // Navigate to dashboard
}
```

**Validation errors** are caught and shown:
```typescript
try {
  const report = parseOrpheusReport(json)
  setReport(report)
} catch (error) {
  if (error instanceof z.ZodError) {
    showError(`Invalid report: ${error.errors[0].message}`)
  }
}
```

---

### Step 3: Render (Frontend)

All charts and views render from the normalized `ReportV1` data in Zustand store.

**No additional API calls**. All state is local.

---

## Phase 2 (Optional): Live API Integration

If backend adds a live API endpoint:

### Report Generation Endpoint

```
POST /api/reports
Content-Type: application/json

{
  "spotify_user_id": "user123",
  "source": "streaming_history.json",
  "config_overrides": {
    "state_half_life_days": 3,
    "trait_half_life_days": 90
  }
}
```

**Response**:
```json
{
  "report_id": "uuid",
  "status": "pending",
  "polling_url": "/api/reports/uuid/status"
}
```

### Polling for Result

```typescript
const pollForReport = async (reportId: string) => {
  const maxAttempts = 60
  let attempts = 0

  while (attempts < maxAttempts) {
    const response = await fetch(`/api/reports/${reportId}/status`)
    const { status, report_url } = await response.json()

    if (status === 'completed') {
      const reportResponse = await fetch(report_url)
      const report = await reportResponse.json()
      return report
    }

    attempts++
    await new Promise((resolve) => setTimeout(resolve, 2000)) // Poll every 2s
  }

  throw new Error('Report generation timeout')
}
```

---

## Error Handling

### File Parsing Errors

```typescript
// src/hooks/useReportUpload.ts
export const useReportUpload = () => {
  const [error, setError] = useState<string | null>(null)

  const upload = async (file: File) => {
    try {
      const text = await file.text()
      const json = JSON.parse(text)
      const report = parseOrpheusReport(json)
      return report
    } catch (err) {
      if (err instanceof SyntaxError) {
        setError('File is not valid JSON')
      } else if (err instanceof z.ZodError) {
        setError(`Invalid report format: ${err.errors[0].path.join('.')}`)
      } else {
        setError('Unknown error during upload')
      }
      return null
    }
  }

  return { upload, error }
}
```

### User-Facing Messages

```typescript
const errorMessages = {
  INVALID_JSON: 'This file is not valid JSON. Did you select the right file?',
  INVALID_SCHEMA: 'This report is missing required fields. Please generate a new report.',
  FILE_TOO_LARGE: 'Report is too large (>100 MB). Please try a smaller dataset.',
  UNKNOWN: 'Something went wrong. Please try again or contact support.',
}
```

---

## Data Transformation Helpers

### Emotion → Scatter Point Mapping

```typescript
// src/lib/chart-utils.ts
const EMOTION_COORDINATES = {
  joyful_activation: { valence: 0.8, arousal: 0.6, label: 'Joyful Activation' },
  triumphant_power: { valence: 0.6, arousal: 0.8, label: 'Triumphant Power' },
  peacefulness: { valence: 0.8, arousal: -0.7, label: 'Peacefulness' },
  tenderness: { valence: 0.7, arousal: -0.3, label: 'Tenderness' },
  nostalgia_longing: { valence: 0.2, arousal: -0.4, label: 'Nostalgia & Longing' },
  sadness_melancholy: { valence: -0.8, arousal: -0.6, label: 'Sadness' },
  tension_anxiety: { valence: -0.6, arousal: 0.5, label: 'Tension & Anxiety' },
  anger_defiance: { valence: -0.7, arousal: 0.8, label: 'Anger & Defiance' },
}

export const transformEmotionToScatter = (windowScores: WindowScores) => {
  const scoredEntries = Object.entries(windowScores.emotion)
  const fallbackEntries = windowScores.top_emotions.map((item) => [item.category, 0] as const)

  return (scoredEntries.length > 0 ? scoredEntries : fallbackEntries).map(([emotion, score]) => {
    const coords = EMOTION_COORDINATES[emotion]
    return {
      x: coords.valence,
      y: coords.arousal,
      size: Math.max(score * 100, 12),
      emotion,
      label: coords.label,
      score,
    }
  })
}
```

### Theme → Bar Chart Data

```typescript
export const transformThemeToBar = (windowScores: WindowScores) => {
  const scoredEntries = Object.entries(windowScores.theme)

  if (scoredEntries.length === 0) {
    return windowScores.top_themes.map((item) => ({
      theme: THEME_LABELS[item.category],
      score: null,
      color: THEME_COLORS[item.category],
      prevalence: item.prevalence,
    }))
  }

  return scoredEntries
    .map(([theme, score]) => ({
      theme: THEME_LABELS[theme],
      score,
      color: THEME_COLORS[theme],
      prevalence: computePrevalence(score),
    }))
    .sort((a, b) => b.score - a.score)
}
```

### Trend Event Data

```typescript
export const transformTrendEvents = (trends: TrendEvent[]) => {
  return trends.map((trend) => ({
    id: `${trend.axis}-${trend.category}`,
    label: CATEGORY_LABELS[trend.category],
    axis: trend.axis,
    direction: trend.direction,
    magnitude: trend.magnitude,
    narrative: trend.narrative,
  }))
}
```

---

## Export Formats

### JSON Export

```typescript
// src/lib/export.ts
export const exportAsJSON = (report: OrpheusReport) => {
  const safeReport = {
    metadata: report.metadata,
    state: report.state,
    trait: report.trait,
    shifts: report.shifts,
    trends: report.trends,
    clusters: report.clusters,
    co_occurrences: report.co_occurrences,
    safety_flags: report.safety_flags,
  }

  const blob = new Blob([JSON.stringify(safeReport, null, 2)], {
    type: 'application/json',
  })
  downloadBlob(blob, `orpheus_report_${new Date().toISOString().split('T')[0]}.json`)
}
```

### CSV Export

```typescript
export const exportAsCSV = (report: OrpheusReport) => {
  const rows = [
    ['Category', 'Type', 'Score', 'Prevalence'],
  ]

  // Emotions
  Object.entries(report.state.emotion).forEach(([emotion, score]) => {
    rows.push([emotion, 'emotion', score.toFixed(3), computePrevalence(score)])
  })

  // Themes
  Object.entries(report.state.theme).forEach(([theme, score]) => {
    rows.push([theme, 'theme', score.toFixed(3), computePrevalence(score)])
  })

  const csv = rows.map((r) => r.map((v) => `"${v}"`).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  downloadBlob(blob, `orpheus_report_${new Date().toISOString().split('T')[0]}.csv`)
}
```

### PNG Export (Chart Screenshot)

```typescript
import html2canvas from 'html2canvas'

export const exportChartAsPNG = async (elementId: string) => {
  const element = document.getElementById(elementId)
  const canvas = await html2canvas(element)
  const link = document.createElement('a')
  link.href = canvas.toDataURL()
  link.download = `orpheus_chart_${new Date().toISOString().split('T')[0]}.png`
  link.click()
}
```

---

## Caching & Performance

### Local Storage (Optional)

For user convenience, cache the last uploaded report:

```typescript
// src/hooks/useLocalCache.ts
export const useLocalCache = () => {
  const saveReport = (report: OrpheusReport) => {
    try {
      localStorage.setItem('orpheus_last_report', JSON.stringify(report))
    } catch (err) {
      // Storage full or disabled; silently fail
    }
  }

  const loadReport = (): OrpheusReport | null => {
    try {
      const cached = localStorage.getItem('orpheus_last_report')
      return cached ? JSON.parse(cached) : null
    } catch {
      return null
    }
  }

  return { saveReport, loadReport }
}
```

**Usage**:
```typescript
// UploadPage.tsx
useEffect(() => {
  const cached = loadReport()
  if (cached) {
    setReport(cached)
    navigate('/dashboard')
  }
}, [])
```

---

## Request/Response Patterns (Future API)

### Retry Logic

```typescript
export const fetchWithRetry = async (url: string, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url)
      if (!response.ok) throw new Error(response.statusText)
      return response
    } catch (err) {
      if (i === maxRetries - 1) throw err
      await new Promise((resolve) => setTimeout(resolve, 1000 * Math.pow(2, i)))
    }
  }
}
```

### Timeout Handler

```typescript
export const fetchWithTimeout = (url: string, timeout = 30000) => {
  return Promise.race([
    fetch(url),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Fetch timeout')), timeout)
    ),
  ])
}
```

---

## Versioning & Compatibility

### Report Version Check

```typescript
// src/lib/validation.ts
const SUPPORTED_VERSIONS = ['2.0.0-alpha', '2.0.0', '2.1.0']

export const checkVersionCompatibility = (reportVersion: string): boolean => {
  const [major, minor] = reportVersion.split('.').map(Number)
  const [supportedMajor] = SUPPORTED_VERSIONS[0].split('.').map(Number)

  if (major < supportedMajor) {
    console.warn(`Report version ${reportVersion} is outdated. Features may be missing.`)
    return false
  }

  return true
}
```

**In UploadPage**:
```typescript
if (!checkVersionCompatibility(report.metadata.model_version)) {
  showWarning('This report was generated with an older version. Some features may not work.')
}
```

---

## CORS (If Backend API Added Later)

Backend should include CORS headers:

```
Access-Control-Allow-Origin: https://orpheus-frontend.vercel.app
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

Frontend handles CORS errors gracefully:

```typescript
try {
  const response = await fetch('/api/reports')
} catch (error) {
  if (error instanceof TypeError && error.message.includes('fetch')) {
    showError('Network error. Please check your connection.')
  }
}
```

---

## Rate Limiting (Future)

If backend adds API, implement rate limiting on frontend:

```typescript
import { RateLimiter } from 'limiter'

const limiter = new RateLimiter({ tokensPerInterval: 10, interval: 'minute' })

export const fetchReport = async (reportId: string) => {
  await limiter.removeTokens(1)
  return fetch(`/api/reports/${reportId}`)
}
```

---

## Testing API Contracts

### Mock Responses

```typescript
// src/__tests__/mocks/handlers.ts
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.post('/api/reports', () => {
    return HttpResponse.json({
      report_id: 'test-uuid',
      status: 'completed',
    })
  }),
]
```

### Test Setup

```typescript
// src/__tests__/setup.ts
import { setupServer } from 'msw/node'
import { handlers } from './mocks/handlers'

export const server = setupServer(...handlers)
```

---

## Security Considerations

### Input Validation

All user-provided data (file uploads) validated with Zod before use.

### Data Privacy

- No tracking or analytics of report contents  
- No sending data to external services  
- Local-only processing (no network calls for MVP)  

### XSS Prevention

- React auto-escapes JSX content  
- No `dangerouslySetInnerHTML` unless absolutely necessary  
- Sanitize any user-provided text (though MVP doesn't have that)  

---

*Last updated: 2026-05-27*
