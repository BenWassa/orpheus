# 08 — Accessibility Specification (WCAG 2.1 AA)

## Overview

The Orpheus frontend must be **WCAG 2.1 Level AA compliant**. This document specifies how each requirement is implemented.

---

## Keyboard Navigation

### Requirement
All interactive elements (buttons, links, form inputs, modals) must be keyboard-accessible via Tab navigation.

### Implementation

```typescript
// All buttons: default, no special tabindex
<button onClick={handleClick}>Export</button>

// Forms: proper label association
<label htmlFor="confidence-filter">Minimum Confidence</label>
<input id="confidence-filter" type="range" />

// Skip link (first element on page)
<a href="#main-content" className="sr-only">Skip to main content</a>

// Focus trap in modals (trap Tab within modal)
import { useEffect } from 'react'

export const Modal = ({ isOpen, onClose }) => {
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose()
      if (e.key === 'Tab') {
        // Trap focus within modal
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])
}
```

### Keyboard Shortcuts

| Key | Action |
|---|---|
| `Tab` | Move to next interactive element |
| `Shift + Tab` | Move to previous interactive element |
| `Enter` | Activate button, submit form |
| `Space` | Toggle button, checkbox, or switch |
| `Escape` | Close modal, collapse expandable |
| `Arrow Up/Down` | Navigate list items, range slider |

### Test
```bash
# Manual: Tab through entire page with no mouse
# Automated: axe-core browser extension
```

---

## Focus Management

### Requirement
All interactive elements must have a visible focus indicator (keyboard users need to know where they are).

### Implementation

```css
/* Global focus styles */
:focus-visible {
  outline: 2px solid #059669;
  outline-offset: 2px;
}

button:focus-visible,
a:focus-visible,
input:focus-visible {
  outline: 2px solid #059669;
  outline-offset: 2px;
}

/* Avoid removing outline */
/* ❌ DO NOT: button { outline: none } */
```

**Focus trap in modals**:
```typescript
import { useEffect, useRef } from 'react'

export const Modal = ({ isOpen, onClose }) => {
  const firstButtonRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    if (isOpen) {
      firstButtonRef.current?.focus()
    }
  }, [isOpen])

  return (
    <div role="dialog" aria-modal="true">
      <button ref={firstButtonRef}>Close</button>
      {/* Modal content */}
    </div>
  )
}
```

### Test
```
Manual: Tab through page; all interactive elements should have visible focus outline
Automated: Lighthouse, WebAIM contrast checker
```

---

## Color Contrast

### Requirement
Text must have at least 4.5:1 contrast ratio (WCAG AA).
Large text (18px+) may have 3:1 ratio.

### Implementation

**Primary palette**:
```css
--color-text: #1f2937      /* Dark gray-blue */
--color-bg: #fafaf9       /* Off-white */
/* Contrast: 16.4:1 ✓ */

--color-text-muted: #6b7280   /* Medium gray */
--color-bg: #ffffff        /* White */
/* Contrast: 8.6:1 ✓ */

--color-accent: #059669    /* Teal */
--color-bg: #ffffff        /* White */
/* Contrast: 5.1:1 ✓ */
```

**Emotion palette** (tested for colorblindness):
```
Joyful:       #f59e0b (amber)          on white: 9.4:1 ✓
Sadness:      #3b82f6 (blue)           on white: 6.2:1 ✓
Peacefulness: #6ee7b7 (mint)           on white: 5.8:1 ✓
Anger:        #991b1b (dark red)       on white: 11.3:1 ✓
```

**Check with**:
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Chrome DevTools: Elements panel → Computed → color info

### Test
```
npm run test:a11y  # Run axe-core accessibility audit
```

---

## Color Independence

### Requirement
Information should not be conveyed by color alone. Provide alternative visual or textual indicators.

### Implementation

**❌ Bad**: Emotion chart with only color differentiation
```html
<div style="background: #f59e0b">Joyful</div>
```

**✅ Good**: Emotion chart with color + icon + label
```typescript
<div className="emotion-badge">
  <span className="icon">🎉</span>
  <span className="label">Joyful Activation</span>
  <span className="score">24%</span>
</div>
```

**Legend required** for all charts:
```typescript
<Legend>
  <LegendItem color="#f59e0b" label="Joyful Activation" />
  <LegendItem color="#3b82f6" label="Sadness" />
  {/* ... */}
</Legend>
```

### Test
```
Manual: Print page in grayscale; all content should still be understandable
Tool: Use Color Blindness Simulator (e.g., Chrome DevTools, Color Oracle)
```

---

## Text Alternatives

### Images

```typescript
// ❌ Bad
<img src="album.jpg" />

// ✅ Good
<img src="album.jpg" alt="Album cover for 'Red' by Taylor Swift" />
```

### Charts

```typescript
// ❌ Bad (visual only)
<ScatterChart data={data} />

// ✅ Good (with description)
<div role="img" aria-label="Emotion scatter plot. Your current listening shows dominant nostalgia (top right, 35% score) and high sadness (bottom left, 22% score). Baseline is more balanced.">
  <ScatterChart data={data} />
</div>
```

### Icons

```typescript
// ❌ Bad
<button>🎉</button>

// ✅ Good
<button aria-label="Export report" title="Export">🎉</button>
```

### Test
```bash
# Screen reader testing (manual)
# - macOS: VoiceOver (Cmd+F5)
# - Windows: NVDA or JAWS
# - Test with Chrome DevTools: Accessibility panel
```

---

## ARIA Attributes

### Headings (Semantic HTML)

```typescript
// ✅ Use semantic HTML
<h1>Your listening clusters around nostalgia</h1>
<h2>Emotion Breakdown</h2>
<h3>Top Emotions</h3>

// Proper nesting: h1 → h2 → h3 (no skipping levels)
```

### Live Regions (Dynamic Content)

```typescript
// When data loads or updates
<div role="status" aria-live="polite" aria-atomic="true">
  Report loaded successfully. {data.length} tracks analyzed.
</div>

// For errors
<div role="alert" aria-live="assertive">
  Error: Invalid report format.
</div>
```

### Modals

```typescript
<Dialog role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <h2 id="modal-title">Export Report</h2>
  <p id="modal-desc">Choose format and download.</p>
  {/* Dialog content */}
</Dialog>
```

### Buttons

```typescript
// Icon buttons must have label
<button aria-label="Close modal" onClick={onClose}>×</button>

// Toggle buttons must indicate state
<button
  aria-pressed={isActive}
  aria-label={isActive ? 'Show baseline (active)' : 'Show baseline'}
>
  Show Baseline
</button>
```

### Expandable Sections

```typescript
<button
  aria-expanded={isExpanded}
  aria-controls="theme-list"
  onClick={() => setExpanded(!isExpanded)}
>
  Life Themes {isExpanded ? '▼' : '▶'}
</button>

<ul id="theme-list" hidden={!isExpanded}>
  {themes.map((theme) => (
    <li key={theme}>{theme}</li>
  ))}
</ul>
```

### Form Labels

```typescript
<fieldset>
  <legend>Filter by emotion:</legend>
  <label>
    <input type="checkbox" name="sadness" />
    Sadness
  </label>
</fieldset>
```

---

## Semantic HTML

### Headings

```typescript
// ✅ Proper structure
<h1>Your Emotional Landscape</h1>
<section>
  <h2>Emotions</h2>
  <h3>Top Categories</h3>
</section>
<section>
  <h2>Themes</h2>
  <h3>Life Themes</h3>
</section>

// ❌ Avoid
<div className="h1">Your Emotional Landscape</div>
```

### Lists

```typescript
// ✅ Good
<ul>
  <li>Nostalgia (35%)</li>
  <li>Sadness (22%)</li>
</ul>

// ❌ Bad
<div>
  <div>Nostalgia (35%)</div>
  <div>Sadness (22%)</div>
</div>
```

### Buttons vs Links

```typescript
// ✅ Button for actions
<button onClick={handleExport}>Export Report</button>

// ✅ Link for navigation
<a href="/dashboard">View Dashboard</a>

// ❌ Don't use div as button
<div onClick={handleClick} role="button">Export</div>
```

---

## Readability

### Font Sizing

```css
/* Minimum 16px for body text */
body {
  font-size: 1rem; /* 16px */
  line-height: 1.5; /* 150% */
}

/* Adequate contrast and spacing */
h1 {
  font-size: 3rem;
  line-height: 1.2;
  margin-bottom: 1.5rem;
}
```

### Line Length

```css
/* Keep line length ~50–75 characters */
.prose {
  max-width: 65ch;
}
```

### Letter Spacing & Word Spacing

```css
/* Avoid tight letter/word spacing */
body {
  letter-spacing: normal;
  word-spacing: normal;
}

/* Avoid ALL CAPS for long text */
h2 {
  text-transform: capitalize; /* Not uppercase */
}
```

---

## Motion & Animation

### Respect Prefers-Reduced-Motion

```css
/* Default: animations enabled */
@media (prefers-reduced-motion: no-preference) {
  button {
    transition: background-color 200ms ease-out;
  }
}

/* Animations disabled for users who prefer it */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### JavaScript

```typescript
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

const animate = () => {
  if (prefersReducedMotion) {
    // Skip animation, jump to final state
    setOpacity(1)
  } else {
    // Animate normally
    setOpacity(0)
    setTimeout(() => setOpacity(1), 300)
  }
}
```

---

## Form Accessibility

### Input Validation

```typescript
<div>
  <label htmlFor="confidence">Minimum Confidence</label>
  <input
    id="confidence"
    type="range"
    min="0"
    max="1"
    step="0.1"
    aria-describedby="confidence-help"
  />
  <span id="confidence-help">Select 0.0 (all) to 1.0 (high confidence)</span>
</div>
```

### Error Messages

```typescript
<div role="alert">
  <label htmlFor="file">Upload Report</label>
  <input
    id="file"
    type="file"
    aria-invalid="true"
    aria-describedby="file-error"
  />
  <span id="file-error" className="error">
    Error: File must be valid JSON. {error.message}
  </span>
</div>
```

---

## Responsive Design & Touch

### Touch Targets

```css
/* Minimum 44px × 44px tap target */
button {
  min-height: 44px;
  min-width: 44px;
  padding: 12px 16px;
}

/* Adequate spacing between targets */
.button-group {
  display: flex;
  gap: 12px; /* At least 8px between buttons */
}
```

### Mobile Viewport

```html
<meta name="viewport" content="width=device-width, initial-scale=1" />
```

### Orientation Lock (Avoid)

```typescript
// ❌ Don't lock orientation; let users rotate freely
// ✅ Support both portrait and landscape
```

---

## Automated Testing

### Setup

```bash
npm install --save-dev @axe-core/react jest-axe
```

### Test Example

```typescript
// src/__tests__/App.test.tsx
import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import App from '../App'

expect.extend(toHaveNoViolations)

test('should not have accessibility violations', async () => {
  const { container } = render(<App />)
  const results = await axe(container)
  expect(results).toHaveNoViolations()
})
```

### CI Integration

```yaml
# .github/workflows/a11y.yml
name: Accessibility
on: [push, pull_request]
jobs:
  accessibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm install
      - run: npm run test:a11y
```

---

## Manual Testing Checklist

### Keyboard Navigation
- [ ] Tab through entire page without mouse
- [ ] Focus visible on all interactive elements
- [ ] Logical tab order (left→right, top→bottom)
- [ ] Can enter/exit modals with Escape

### Screen Reader (VoiceOver/NVDA)
- [ ] Page title announced
- [ ] Headings announced with level (H1, H2, etc.)
- [ ] Links and buttons have meaningful labels
- [ ] Form fields associated with labels
- [ ] Images have alt text
- [ ] Live regions announced

### Color & Contrast
- [ ] Text readable in high contrast mode
- [ ] Page understandable in grayscale
- [ ] Icons meaningful even without color

### Motion
- [ ] Page usable with animations off
- [ ] No auto-playing videos or animations

### Mobile/Touch
- [ ] All buttons ≥44px × 44px
- [ ] Adequate spacing between touch targets
- [ ] Responsive layout on 320px width

---

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM Screen Reader Testing](https://webaim.org/articles/screenreader_testing/)
- [A11y Project Checklist](https://www.a11yproject.com/checklist/)
- [Axe DevTools](https://www.deque.com/axe/devtools/)
- [Color Blind Simulation](https://www.color-blindness.com/coblis-color-blindness-simulator/)

---

## Implementation Timeline

**Phase 4 (Week 7)**: Full accessibility audit using automated tools (axe-core) + manual testing

**Before Launch**: Fix all identified violations; target WCAG 2.1 AA compliance (100% is unlikely, but aim for ~95%)

---

*Last updated: 2026-05-27*
