# 05 — Technical Stack & Architecture

## Frontend Framework

### React 18+ (TypeScript)

**Why React:**
- Component-based architecture matches UI decomposition  
- Large ecosystem for data visualization and state management  
- TypeScript support for type safety across large codebase  
- Strong team familiarity (assumed)  

**Why NOT other frameworks:**
- Vue: Smaller ecosystem for data viz; overkill for single-page app  
- Svelte: Smaller community; harder to hire for later phases  
- Angular: Over-engineered for MVP scope  

---

## Build Tooling

### Vite

**Why:**
- **Fast dev server**: HMR (Hot Module Replacement) <100ms  
- **Optimized build**: Tree-shaking, minification, code splitting  
- **Low config**: Works out-of-the-box with React + TypeScript  
- **ESM-native**: Future-proof  

**Setup:**
```bash
npm create vite@latest orpheus-frontend -- --template react-ts
npm install
npm run dev    # Start dev server
npm run build  # Production build
```

---

## State Management

### Zustand (Lightweight)

**Use case**: Client state (uploaded report data, UI toggles, filters)

```typescript
// store.ts
import { create } from 'zustand'

interface AppStore {
  report: OrpheusReport | null
  setReport: (report: OrpheusReport) => void
  filters: FilterState
  setFilters: (filters: FilterState) => void
}

export const useAppStore = create<AppStore>((set) => ({
  report: null,
  setReport: (report) => set({ report }),
  filters: {},
  setFilters: (filters) => set({ filters }),
}))
```

**Why Zustand over Redux:**
- Minimal boilerplate  
- No provider nesting  
- Smaller bundle size (~2KB)  
- Perfect for client-only state (no server sync needed)  

**Why NOT TanStack Query (React Query):**
- Overkill for static JSON file parsing  
- Query (Remote State Management) pattern doesn't apply  
- If backend API added later: can adopt Query then  

---

## Data Validation

### Zod

```typescript
// schemas.ts
import { z } from 'zod'

const emotionCategorySchema = z.enum([
  'joyful_activation',
  'triumphant_power',
  'peacefulness',
  'tenderness',
  'nostalgia_longing',
  'sadness_melancholy',
  'tension_anxiety',
  'anger_defiance',
])

const reportV0Schema = z.object({
  generated_at: z.string().datetime(),
  model_version: z.string(),
  windows: z.object({
    state: backendWindowSchema,
    trait: backendWindowSchema,
  }),
  shifts: z.array(shiftSchema).default([]),
  trends: z.array(trendEventSchema).default([]),
  clusters: z.array(clusterSummarySchema).default([]),
  co_occurrences: z.array(backendCoOccurrenceSchema).default([]),
  safety_flags: z.array(safetyFlagSchema).default([]),
})

const reportV1Schema = z.object({
  metadata: reportMetadataSchema,
  state: windowScoresSchema,
  trait: windowScoresSchema,
  shifts: z.array(shiftSchema).default([]),
  trends: z.array(trendEventSchema).default([]),
  clusters: z.array(clusterSummarySchema).default([]),
  co_occurrences: z.array(coOccurrenceSchema).default([]),
  safety_flags: z.array(safetyFlagSchema).default([]),
  narrative: narrativeSummarySchema.optional(),
})

export const parseOrpheusReport = (input: unknown): OrpheusReport => {
  const v1 = reportV1Schema.safeParse(input)
  if (v1.success) return v1.data

  const v0 = reportV0Schema.parse(input)
  return normalizeReportV0(v0)
}

export type OrpheusReport = z.infer<typeof reportV1Schema>
```

**Why Zod:**
- Runtime validation (JSON → TypeScript type)  
- Produces helpful error messages for users  
- Integrates with React Hook Form (if needed)  
- Supports separate current-backend and target-frontend schemas during the compatibility period  

---

## Visualization Libraries

### Option A: Recharts (Recommended for MVP)

```typescript
// components/EmotionScatter.tsx
import { ScatterChart, Scatter, XAxis, YAxis } from 'recharts'

export const EmotionScatter = ({ data }) => (
  <ScatterChart width={600} height={400}>
    <XAxis dataKey="valence" label={{ value: 'Valence', position: 'insideBottomRight' }} />
    <YAxis dataKey="arousal" label={{ value: 'Arousal', angle: -90 }} />
    <Scatter name="State" data={data.state} fill="#8b5cf6" />
    <Scatter name="Trait" data={data.trait} fill="#d1d5db" />
  </ScatterChart>
)
```

**Pros:**
- React-first, TypeScript support  
- Minimal configuration  
- Responsive by default  
- Active maintenance  
- Good tooltip/hover support  

**Cons:**
- Bundle size: ~50KB gzipped  
- Limited customization vs D3  
- Performance may degrade on 5000+ data points (unlikely for MVP)  

### Option B: Plotly.js (More Control)

```typescript
import Plotly from 'plotly.js-dist'

Plotly.newPlot('chart-div', [{
  x: data.valence,
  y: data.arousal,
  mode: 'markers',
  type: 'scatter',
}])
```

**Pros:**
- Highly customizable  
- Great for complex interactions  
- Excellent hover/tooltip control  

**Cons:**
- Larger bundle (~2MB uncompressed)  
- More manual configuration  
- Steeper learning curve  

### Option C: Visx (Lowest-Level Flexibility)

```typescript
import { scaleLinear } from '@visx/scale'
import { Circle } from '@visx/shape'

// Visx provides building blocks; you compose them
// Best for custom, highly specific visualizations
```

**Pros:**
- Tiny bundle  
- Full control  
- Built by Airbnb (battle-tested)  

**Cons:**
- Requires manual chart composition  
- Much more code for standard charts  
- Not recommended for MVP timeline  

**Recommendation for MVP**: **Recharts** (balance of ease + flexibility)

---

## UI Component Library

### Radix UI + Tailwind CSS + shadcn/ui

**Radix UI** (Unstyled Accessible Components):
```typescript
import * as Dialog from '@radix-ui/react-dialog'

export const Modal = ({ open, onClose, children }) => (
  <Dialog.Root open={open} onOpenChange={onClose}>
    <Dialog.Portal>
      <Dialog.Overlay />
      <Dialog.Content>
        {children}
        <Dialog.Close />
      </Dialog.Content>
    </Dialog.Portal>
  </Dialog.Root>
)
```

**Tailwind CSS** (Utility-First Styling):
```css
.hero {
  @apply text-4xl font-bold text-slate-900 leading-tight mb-8;
}

.card {
  @apply bg-white rounded-lg shadow-sm border border-gray-200 p-6;
}
```

**shadcn/ui** (Pre-built Radix + Tailwind components):
```typescript
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogTrigger } from '@/components/ui/dialog'

// Use immediately; customize as needed
<Button onClick={handleClick}>Export</Button>
```

**Why this stack:**
- Radix UI: Accessible foundations (keyboard nav, focus mgmt, ARIA)  
- Tailwind: Fast styling, consistent spacing/colors, responsive  
- shadcn/ui: Pre-built but customizable (copy source into project)  

**Alternative**: Material-UI (less flexible, more opinionated)

---

## File Handling & Parsing

### React Dropzone + Native File API

```typescript
import { useDropzone } from 'react-dropzone'

const { getRootProps, getInputProps } = useDropzone({
  accept: { 'application/json': ['.json'] },
  onDrop: async (files) => {
    const file = files[0]
    const text = await file.text()
    const json = JSON.parse(text)
    const report = parseOrpheusReport(json)  // Zod validation + ReportV0 normalization
    setReport(report)
  },
})

return (
  <div {...getRootProps()}>
    <input {...getInputProps()} />
    <p>Drag and drop your report here...</p>
  </div>
)
```

**Why React Dropzone:**
- Handles browser file API differences  
- Built-in drag-and-drop  
- Keyboard accessible  

**No need for backend file upload**: All parsing happens in browser (faster, privacy-respecting).

---

## Testing Strategy

### Unit Tests (Vitest)

```typescript
// src/__tests__/schemas.test.ts
import { describe, it, expect } from 'vitest'
import { parseOrpheusReport, reportV1Schema } from '../schemas'

describe('parseOrpheusReport', () => {
  it('should parse valid normalized report', () => {
    const report = { /* valid report object */ }
    const result = reportV1Schema.safeParse(report)
    expect(result.success).toBe(true)
  })

  it('should normalize current backend reports', () => {
    const report = parseOrpheusReport(validBackendReportV0)
    expect(report.metadata.schema_version).toBe('1.0')
    expect(report.state.top_emotions[0].category).toBe('nostalgia_longing')
  })
})
```

### Component Tests (React Testing Library)

```typescript
import { render, screen } from '@testing-library/react'
import { EmotionScatter } from './EmotionScatter'

describe('EmotionScatter', () => {
  it('renders chart title', () => {
    render(<EmotionScatter data={mockData} />)
    expect(screen.getByText('Emotion Distribution')).toBeInTheDocument()
  })
})
```

### E2E Tests (Playwright)

```typescript
// e2e/upload-and-summarize.spec.ts
import { test, expect } from '@playwright/test'

test('user can upload report and see summary', async ({ page }) => {
  await page.goto('http://localhost:5173')
  await page.locator('[data-testid="file-input"]').setInputFiles('fixtures/sample_report.json')
  await expect(page.locator('h1')).toContainText('Your listening clusters around')
})
```

**Coverage target**: 70% (focus on critical paths: parsing, chart rendering, export)

---

## Performance Optimization

### Code Splitting

```typescript
// Router with lazy-loaded components
const Dashboard = lazy(() => import('./pages/Dashboard'))
const DrillDown = lazy(() => import('./pages/DrillDown'))

// Fallback component
const Loading = () => <div>Loading...</div>

// Usage
<Suspense fallback={<Loading />}>
  <Dashboard />
</Suspense>
```

### Image Optimization

- **Album art**: Serve via Spotify's CDN (already optimized)  
- **Static assets**: Vite auto-optimizes during build  
- **Lazy-load images** in track lists (intersection observer)  

### Bundle Analysis

```bash
npm install --save-dev vite-plugin-visualizer

# In vite.config.ts
import { visualizer } from 'vite-plugin-visualizer'

export default {
  plugins: [visualizer()],
}

npm run build  # Generates stats.html
```

**Target bundle size**: <200KB gzipped (core app), <50KB per route

---

## TypeScript Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

**Strict mode**: Enables all type-checking flags (no `any` unless justified)

---

## Linting & Formatting

### ESLint

```javascript
// .eslintrc.cjs
module.exports = {
  extends: ['eslint:recommended', 'plugin:@typescript-eslint/recommended', 'prettier'],
  parser: '@typescript-eslint/parser',
  rules: {
    'no-console': 'warn',
    '@typescript-eslint/explicit-function-return-types': 'warn',
  },
}
```

### Prettier

```json
// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "arrowParens": "always"
}
```

### Pre-commit Hooks (Husky)

```bash
npm install husky lint-staged --save-dev
npx husky install

# .husky/pre-commit
npx lint-staged
```

```json
// package.json
{
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"]
  }
}
```

---

## Dependencies Checklist

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "zustand": "^4.4.0",
    "recharts": "^2.8.0",
    "zod": "^3.22.0",
    "react-dropzone": "^14.2.3",
    "radix-ui": "^1.0.0",
    "@tailwindcss/tailwindcss": "^3.3.0",
    "clsx": "^2.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "vite": "^4.4.0",
    "@vitejs/plugin-react": "^4.0.0",
    "vitest": "^0.34.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.1.0",
    "@playwright/test": "^1.39.0",
    "eslint": "^8.51.0",
    "@typescript-eslint/parser": "^6.7.0",
    "prettier": "^3.0.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.30"
  }
}
```

**Total bundle (core + deps)**: ~150KB gzipped

---

## Deployment

### Vercel (Recommended)

```bash
npm i -g vercel
vercel deploy
```

**Benefits:**
- Zero-config for Vite  
- Automatic preview deploys on PR  
- Edge Functions for serverless  
- CDN caching  
- Free tier sufficient for MVP  

**Environment setup**:
```bash
# vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "env": {
    "VITE_API_URL": "@api_url"
  }
}
```

### Netlify (Alternative)

Similar to Vercel; also zero-config.

### Self-Hosted (Static)

```bash
npm run build
# dist/ folder contains static files
# Deploy to S3 + CloudFront, or any static host
```

---

## Development Workflow

```bash
# Setup
git clone <repo>
cd orpheus-frontend
npm install

# Development
npm run dev      # Runs Vite dev server (localhost:5173)
npm run lint     # ESLint
npm run format   # Prettier
npm run test     # Vitest
npm run test:e2e # Playwright

# Build
npm run build    # Production build
npm run preview  # Test production build locally

# Deploy
npm run deploy   # (if using Vercel/Netlify)
```

---

## Browser Support

- Chrome 90+  
- Firefox 88+  
- Safari 14+  
- Edge 90+  

**Polyfills**: Not needed (modern APIs used)

---

## Accessibility Tools Integration

```typescript
// vite.config.ts
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  define: {
    'process.env.DEV': true,
  },
  server: {
    // Enable axe-core DevTools in dev
    middleware: (req, res, next) => {
      if (req.url === '/__axe__') {
        // Inject axe-core for accessibility testing
      }
      next()
    },
  },
})
```

**Manual checks**:
- WebAIM Contrast Checker  
- Lighthouse Accessibility Audit  
- Manual keyboard navigation  

---

## Documentation

```
src/
├── README.md              # Getting started
├── ARCHITECTURE.md        # System overview
├── CONTRIBUTING.md        # Code guidelines
├── COMPONENT_LIBRARY.md   # Storybook reference
└── API_INTEGRATION.md     # Backend contract
```

---

*Last updated: 2026-05-27*
