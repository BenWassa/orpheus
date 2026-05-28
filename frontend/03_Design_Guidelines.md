# 03 — Design Guidelines & Visual Direction

## Design Philosophy

**Tone**: Introspective, calm, human-centered. This is not a corporate analytics dashboard; it's a **personal mirror**.

**Core principle**: Reduce cognitive load through whitespace, generous typography, and progressive disclosure. Let users read the summary in 5 minutes, then explore if they want to.

---

## Color Palette

### Primary Palette (Neutral Foundation)

```
Background:    #fafaf9 (off-white, warm)
Surface:       #ffffff (white)
Text:          #1f2937 (dark gray-blue)
Muted:         #9ca3af (soft gray)
Border:        #e5e7eb (light gray)
Accent:        #059669 (soft teal, approving/positive)
```

### Emotion Category Colors (8-Color Set, Colorblind-Safe)

Use the following palette for emotion categories (tested for protanopia, deuteranopia, tritanopia):

```
Joyful Activation:       #f59e0b (amber)
Triumphant Power:        #8b5cf6 (purple)
Peacefulness:            #6ee7b7 (mint)
Tenderness:              #f472b6 (pink)
Nostalgia & Longing:     #60a5fa (sky-blue)
Sadness & Melancholy:    #3b82f6 (blue)
Tension & Anxiety:       #ef4444 (red)
Anger & Defiance:        #991b1b (dark-red)
```

**Rationale**: Palette tested in [Color Universal Design](https://jfly.uni-koeln.de/color/); no red/green only contrasts.

### Theme Category Colors (Secondary Palette)

Use grayscale + icons to differentiate themes:

```
Interpersonal Devotion:  #60a5fa (blue, ♥)
Heartbreak & Loss:       #ef4444 (red, ⚔)
Resilience:              #8b5cf6 (purple, 🛡)
Identity & Autonomy:     #f59e0b (amber, ⚡)
Ambition:                #6366f1 (indigo, 🎯)
Pleasure & Escapism:     #f472b6 (pink, 🎉)
Place & Heritage:        #84cc16 (lime, 📍)
Meaning & Spirituality:  #d946ef (magenta, 🔮)
```

**Rationale**: Icons (or emojis for MVP) provide secondary affordance for accessibility and rapid scanning.

---

## Typography

### Font Stack

**Headings** (Serif, warm, introspective):
```
font-family: "Crimson Text", "Fraunces", Georgia, serif
font-weight: 600–700 (semibold–bold)
line-height: 1.2
letter-spacing: −0.01em
```

**Body text** (Clean sans-serif, readable):
```
font-family: "Inter", "Helvetica Neue", sans-serif
font-weight: 400–500
line-height: 1.6
letter-spacing: 0
```

**Monospace** (Code, labels):
```
font-family: "Fira Code", "Menlo", monospace
font-weight: 400
font-size: 0.875rem
```

### Scale

```
H1 (Hero headline):       3.0 rem   (48px)   600 weight
H2 (Section title):       2.0 rem   (32px)   600 weight
H3 (Subsection):          1.5 rem   (24px)   600 weight
H4 (Card title):          1.25 rem  (20px)   600 weight
Body (Default):           1.0 rem   (16px)   400 weight
Body (Small):             0.875 rem (14px)   400 weight
Caption:                  0.75 rem  (12px)   400 weight
```

---

## Spacing & Rhythm

### Spacing Scale (Base: 4px increment)

```
xs:    4px
sm:    8px
md:   16px
lg:   24px
xl:   32px
2xl:  48px
3xl:  64px
4xl:  96px
```

### Layout Rhythm

- **Page horizontal padding**: 16px (mobile), 24px (tablet), 32px (desktop)  
- **Section vertical spacing**: 48px (between major sections)  
- **Card vertical spacing**: 32px (between card groups)  
- **Element vertical spacing**: 16px (between paragraphs, list items)  
- **Whitespace ratio**: ~40–50% of viewport should be empty space (generous margins)  

---

## Layout Patterns

### Layout 1: Hero Summary (Top)

```
┌─────────────────────────────────────────┐
│                                         │
│  [Headline]                             │
│  Your listening clusters around...      │
│                                         │
│  ┌──────────────┬──────────────────┐   │
│  │ Top Emotion  │ vs Baseline      │   │
│  │              │ [Badge Rising]   │   │
│  └──────────────┴──────────────────┘   │
│                                         │
│  [Key Insights Bullets]                 │
│                                         │
└─────────────────────────────────────────┘
```

**Design notes**:
- Large serif headline (H1, 48px)  
- State-vs-trait cards with delta arrows  
- Bullet insights in body sans-serif  
- Generous vertical padding (32px top/bottom)  

### Layout 2: Three-Column Content (Middle)

```
┌─────────────────────────────────────────┐
│                                         │
│  ┌───────────┐  ┌──────────┐  ┌──────┐ │
│  │ Emotion   │  │  Theme   │  │Trends│ │
│  │ VA Scatter│  │ Bars/List│  │ Line │ │
│  │           │  │          │  │Chart │ │
│  │           │  │          │  │      │ │
│  └───────────┘  └──────────┘  └──────┘ │
│                                         │
└─────────────────────────────────────────┘
```

**Responsive breakpoints**:
- **Desktop** (≥1024px): 3 equal columns, 16px gaps  
- **Tablet** (640–1023px): 2 columns stacked, first 2 items side-by-side, third below  
- **Mobile** (<640px): Full-width stack, 100% width each  

### Layout 3: Expandable Evidence Detail

```
┌─────────────────────────────────────────┐
│ [Expand/Collapse] "Nostalgia & Longing" │
├─────────────────────────────────────────┤
│                                         │
│  Direction: Elevated                    │
│  Delta: +0.08 vs baseline               │
│  Trend: Rising, notable                 │
│  Related theme: Heartbreak & Loss       │
│  Cluster: Introspective core            │
│                                         │
└─────────────────────────────────────────┘
```

**Design notes**:
- Use compact evidence rows with clear labels and values  
- Keep backend narrative copy close to the numbers it explains  
- Show track rows only when the report includes track-level data  

---

## Component Patterns

### Chart Styling

**Scatter plot (Emotion VA × D)**:
- Background: transparent or light grid  
- Gridlines: #e5e7eb, opacity 0.5  
- Axis labels: Body text (14px)  
- Tooltip: White background, dark text, 4px border-radius, shadow  
- Hover: Bubble glow (outer shadow, 2px, color = category color at 30% opacity)  

**Bar chart (Themes)**:
- Color: One color per theme (from secondary palette)  
- Hover: Slight shift right + shadow lift  
- Labels: Right-aligned or inside bar (if space)  
- Tooltip: Show name + percentage + track count  

**Trend events**:
- Display as a recent movement list for MVP  
- Show direction, magnitude, category, and short narrative  
- Do not synthesize line charts from event-only data  

**Line chart (Trends, future)**:
- Stroke width: 2px (default), 3px (hover/focus)  
- Markers: Small circles at data points (3px radius)  
- Legend: Right side, clickable to toggle series  
- Area under line (optional): Fill at 10% opacity of line color  

### Interactive Feedback

**Buttons**:
- Default: Solid background, white text  
- Hover: 10% darker background  
- Active/Pressed: 20% darker background  
- Disabled: 50% opacity, cursor not-allowed  
- Transition: 150ms ease-out  

**Inputs (text, select)**:
- Border: 1px solid #e5e7eb  
- Focus: 2px solid #059669, outline-offset 2px  
- Transition: 150ms ease-out  

**Toggles (State/Trait switch)**:
- Pill-shaped, two options  
- Inactive: white background, gray text  
- Active: accent color background, white text  
- Transition: 200ms ease-out  

### Cards

- Background: #ffffff  
- Border: 1px solid #e5e7eb  
- Border-radius: 8px  
- Padding: 16px–24px (depends on content)  
- Shadow: 0 1px 3px rgba(0,0,0,0.1) (subtle)  
- Hover: 0 4px 6px rgba(0,0,0,0.1) (on clickable cards)  

---

## Motion & Transitions

### Philosophy
Keep motion subtle and purposeful. Avoid gratuitous animation.

### Recommended Values

```
Fast feedback (micro-interactions):     100–150ms, ease-out
Medium feedback (chart redraws):        300–400ms, ease-in-out
Slow feedback (page transitions):       500–600ms, ease-in-out
```

### Examples

**Chart transitions**: When toggling State/Trait, bubbles should smoothly move to new positions (300–400ms, ease-in-out).

**Drill-down expand**: When clicking an emotion category, track list should slide in from left or fade in (250–300ms).

**Hover feedback**: When hovering a bubble, it should glow with a subtle shadow (100ms, ease-out).

### Avoid
- Parallax scrolling (can cause nausea)  
- Auto-playing animations (respect prefers-reduced-motion)  
- Bouncy/elastic easing (too playful for introspective tool)  

---

## Visual Hierarchy Example

```
┌─────────────────────────────────────────────┐
│                                             │
│  "Your listening clusters around             │  <- H1, 48px, serif, 600
│   nostalgia and heartbreak"                  │     Weight: 600
│                                             │     Color: #1f2937
│  Last 3 days analysis                        │     Margin-bottom: 48px
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Current Mood                        │   │  <- Card, subtle shadow
│  │ Dominant: Nostalgia & Longing       │   │     Typography: H4 + body
│  │ vs Baseline: ↑ +18%                 │   │     Chips for delta
│  └─────────────────────────────────────┘   │
│                                             │
│  Key Insights                               │  <- H2, 24px, serif, 600
│  • Rising longing + loss themes             │     Margin-top: 32px
│  • Depth increasing (moving into immersive) │
│  • Co-occurring with resilience signals     │  <- Bullets, body sans-serif
│                                             │     Color: #4b5563
│                                             │
└─────────────────────────────────────────────┘
```

---

## Responsive Behavior

### Breakpoints

```
Mobile:      0–639px   (single column, stacked cards)
Tablet:      640–1023px (2 columns, touch-friendly)
Desktop:     1024px+   (3 columns, mouse interactions)
Large:       1280px+   (increased spacing, larger fonts)
```

### Mobile Considerations

- **Touch targets**: Minimum 44×44px (tap-friendly)  
- **Font sizes**: Increase body text to 18px  
- **Spacing**: Increase vertical spacing slightly  
- **Charts**: Full-width, may need to hide some details or use tabs  
- **Modal/drawer**: Full-screen modals for drill-down instead of side panels  

---

## Dark Mode (Future, Not MVP)

If dark mode added later:
- Background: #0f1419  
- Surface: #1a1f2e  
- Text: #f3f4f6  
- Muted: #6b7280  
- Emotion colors: Increase saturation +10–15%, slightly lighter  
- Contrast ratio: Maintain WCAG AA (4.5:1 for text)  

---

## Accessibility Considerations

### Color Contrast

- All text: ≥4.5:1 contrast with background (WCAG AA)  
- Labels: ≥3:1 contrast (WCAG AA for large text)  
- Emotion chart: Legend + icon combo (not color alone)  

### Focus Indicators

- All interactive elements: Visible focus ring (2px solid #059669)  
- Keyboard navigation: Tab order follows visual flow (left→right, top→bottom)  
- Skip link: "Skip to main content" (hidden but accessible via Tab)  

### Iconography

- Icons should have `aria-label` or `title` attribute  
- Complex icons (network graphs): Provide text alternative or legend  

### Screen Readers

- Chart descriptions: Use ARIA roles (`role="img"`) + `aria-label` describing key insights  
- Headings: Proper semantic nesting (H1 → H2 → H3)  
- Lists: Use `<ul>`, `<ol>`, `<li>` elements (not divs)  

---

## File Organization & Deliverables

```
src/
├── styles/
│   ├── variables.css (colors, spacing, fonts)
│   ├── global.css
│   └── components.css
├── components/
│   ├── Hero.tsx (headline + state-vs-trait)
│   ├── EmotionScatter.tsx (VA plot)
│   ├── ThemeBars.tsx (theme prevalence)
│   ├── TrendChart.tsx (line chart)
│   ├── TrackCard.tsx (individual track)
│   └── CoOccurrenceMatrix.tsx
├── pages/
│   ├── Upload.tsx (drag-and-drop)
│   ├── Dashboard.tsx (main view)
│   └── DrillDown.tsx (track details)
└── lib/
    ├── colors.ts (emotion/theme color mapping)
    ├── labels.ts (emotion/theme display names)
    └── chart-utils.ts (positioning, encoding)
```

---

## References & Tools

- **Figma**: Create design system with component library matching React component structure  
- **Storybook**: Document component variants (light/dark, hover/active states, sizes)  
- **Contrast checker**: WebAIM Contrast Checker tool  
- **Color palette**: Colorblind simulator for PDF (Color Oracle)  

---

*Last updated: 2026-05-27*
