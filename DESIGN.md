---
name: Project Orpheus
description: A local-first listening mirror for emotional and thematic music analysis.
colors:
  paper: "oklch(0.982 0.007 116)"
  paper-strong: "oklch(0.952 0.011 122)"
  panel: "oklch(0.992 0.006 116)"
  panel-soft: "oklch(0.944 0.014 124)"
  ink: "oklch(0.245 0.025 142)"
  muted: "oklch(0.51 0.024 152)"
  line: "oklch(0.862 0.018 128)"
  accent: "oklch(0.46 0.105 172)"
  accent-strong: "oklch(0.36 0.09 172)"
  accent-soft: "oklch(0.915 0.045 172)"
  plum: "oklch(0.46 0.105 316)"
  warn-soft: "oklch(0.93 0.038 82)"
  warn: "oklch(0.46 0.09 72)"
  danger-soft: "oklch(0.925 0.036 28)"
  danger: "oklch(0.51 0.145 28)"
typography:
  display:
    fontFamily: "Georgia, Times New Roman, serif"
    fontSize: "clamp(2.2rem, 6vw, 5rem)"
    fontWeight: 400
    lineHeight: 0.98
    letterSpacing: "0"
  headline:
    fontFamily: "Georgia, Times New Roman, serif"
    fontSize: "1.42rem"
    fontWeight: 400
    lineHeight: 1.2
  title:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "1.05rem"
    fontWeight: 600
    lineHeight: 1.35
  body:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "0"
  label:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "0.72rem"
    fontWeight: 750
    lineHeight: 1.2
    letterSpacing: "0.08em"
rounded:
  xs: "3px"
  sm: "6px"
  md: "8px"
  lg: "12px"
  pill: "999px"
  circle: "50%"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "22px"
  xxl: "28px"
  section: "48px"
components:
  button-primary:
    backgroundColor: "{colors.accent-strong}"
    textColor: "{colors.paper}"
    rounded: "{rounded.md}"
    height: "42px"
    padding: "0 16px"
  button-primary-hover:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.paper}"
    rounded: "{rounded.md}"
    height: "42px"
    padding: "0 16px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.muted}"
    rounded: "{rounded.md}"
    height: "42px"
    padding: "0 16px"
  panel:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "22px"
  chip:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.muted}"
    rounded: "{rounded.pill}"
    padding: "4px 8px"
---

# Design System: Project Orpheus

## 1. Overview

**Creative North Star: "The Listening Journal"**

Project Orpheus should feel like a quiet personal reading surface for data that can be emotionally loaded. The product has analytic depth, but the interface should receive the user gently: warm paper, restrained borders, clear reading hierarchy, and interaction patterns that invite exploration without turning the experience into a corporate dashboard.

The system is product UI, so design serves comprehension. It should make a report readable in five minutes, then make deeper evidence available through tabs, maps, rows, and ranked tracks. The surface rejects dense spreadsheets, generic SaaS dashboards, and visual spectacle that competes with the user's own listening story.

**Key Characteristics:**
- Warm, paper-like neutrals with a botanical green cast.
- Serif narrative headlines paired with practical sans-serif UI text.
- Flat panels, fine borders, and tonal fills instead of heavy elevation.
- One primary teal accent for action and selection, with plum reserved for cluster identity.
- Progressive disclosure over modal-first explanation.

## 2. Colors

The palette is restrained and reflective: tinted neutrals carry most of the surface, while teal marks action, selection, and proof of focus.

### Primary
- **Deep Listening Teal** (`oklch(0.46 0.105 172)`): Used for primary hover states, active evidence, chart emphasis, and affirmative movement.
- **Grounded Teal** (`oklch(0.36 0.09 172)`): Used for primary button resting states and high-contrast teal text.
- **Mist Teal** (`oklch(0.915 0.045 172)`): Used for selected rows, drag targets, positive deltas, and soft active backgrounds.

### Secondary
- **Cluster Plum** (`oklch(0.46 0.105 316)`): Used sparingly for cluster numbers and emotion chips. It should feel like a second annotation layer, not a competing brand accent.

### Neutral
- **Warm Paper** (`oklch(0.982 0.007 116)`): The primary page background and light text on dark accents.
- **Pressed Paper** (`oklch(0.952 0.011 122)`): Segmented controls, quiet strips, and nested tonal zones.
- **Panel Light** (`oklch(0.992 0.006 116)`): Main panels, cards, chips, and raised reading surfaces.
- **Panel Soft** (`oklch(0.944 0.014 124)`): Dropzones, chart backgrounds, icon wells, and subdued component fills.
- **Botanical Ink** (`oklch(0.245 0.025 142)`): Primary text, outlines for selected matrix cells, and terminal-like code backgrounds.
- **Sage Muted** (`oklch(0.51 0.024 152)`): Secondary text, metadata, captions, and inactive controls.
- **Paper Line** (`oklch(0.862 0.018 128)`): Borders, dividers, grid strokes, and low-emphasis control outlines.

### Tertiary
- **Ochre Warning** (`oklch(0.46 0.09 72)`): Safety messages and cautionary notes.
- **Clay Danger** (`oklch(0.51 0.145 28)`): File errors, negative deltas, and destructive-adjacent feedback.

### Named Rules

**The Teal Is Evidence Rule.** Teal is for action, selection, and meaningful comparison. Do not spread it across decorative surfaces.

**The Paper Carries the Mood Rule.** Most pages should read as warm paper and ink before they read as color.

## 3. Typography

**Display Font:** Georgia, Times New Roman, serif  
**Body Font:** Inter, ui-sans-serif, system-ui, Segoe UI, sans-serif  
**Label/Mono Font:** ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace

**Character:** The serif display voice gives the report a letter-like, reflective quality. The sans-serif layer keeps controls, metadata, and evidence rows efficient enough for repeated use.

### Hierarchy
- **Display** (400, `clamp(2.2rem, 6vw, 5rem)`, 0.98): Hero report headlines and first-run upload headline only.
- **Headline** (400, `1.42rem`, 1.2): Section headings inside panels and evidence areas.
- **Title** (600, `1.05rem`, 1.35): Track titles, profile names, row titles, and compact card headings.
- **Body** (400, `1rem`, 1.6): Narrative copy, summaries, explanations, and readable report prose. Keep prose lines around 65 to 75 characters.
- **Small Body** (400 to 500, `0.82rem` to `0.9rem`, 1.45 to 1.5): Metadata, stats, captions, and helper text.
- **Label** (750, `0.72rem`, `0.08em`, uppercase): Eyebrows, small pills, axis labels, and category labels.

### Named Rules

**The Headline Has To Read Like A Sentence Rule.** Hero text should be human and specific. Avoid metric-led headline formulas.

**The UI Text Stays Quiet Rule.** Controls and labels use the sans-serif stack, compact sizes, and clear verbs.

## 4. Elevation

The system is flat by default. Depth comes from tonal layers, fine borders, inset dividers, and selected states. Shadows are reserved for temporary overlays and hover feedback on profile cards; they should never become a general card style.

### Shadow Vocabulary
- **Profile Hover** (`0 4px 12px rgba(24, 35, 29, 0.05)`): A light response for clickable profile cards only.
- **Overlay Panel** (`0 20px 40px rgba(24, 35, 29, 0.15)`): Used for the add-data overlay panel because it sits above the reading surface.

### Named Rules

**The Flat-At-Rest Rule.** Panels, rows, charts, tabs, and cards should sit flat until interaction gives them a reason to move.

## 5. Components

### Buttons
- **Shape:** 8px radius for standard actions; 6px inside overlay footers.
- **Primary:** Grounded Teal background, Warm Paper text, 42px minimum height, 16px horizontal padding, inline icon plus text.
- **Hover / Focus:** Primary buttons shift to Deep Listening Teal. Ghost buttons use Pressed Paper or Panel Soft fills and Botanical Ink text. Focus states must be visible through border, outline, or color shift.
- **Secondary / Ghost:** Transparent at rest with Sage Muted text; never style as another saturated button unless it is the current active segment.

### Chips
- **Style:** Pill radius, 4px by 8px padding, Panel Light fill, Paper Line border, Sage Muted text.
- **State:** Emotion chips can tint with Cluster Plum. Theme chips can tint with teal. Small swatches are circular and should remain secondary to the text label.

### Cards / Containers
- **Corner Style:** 8px for panels, upload surfaces, row cards, controls, and chart frames. 12px is reserved for ranked track cards and overlay panels.
- **Background:** Main panels use Panel Light. Chart and upload interiors use Panel Soft. Selected rows blend Mist Teal with Panel Light.
- **Shadow Strategy:** No shadows at rest. Use borders and tonal layering first.
- **Border:** Paper Line at 1px. Selected and hover states may mix Paper Line with Deep Listening Teal.
- **Internal Padding:** 18px on mobile, 22px for standard panels, and 24px to 48px for hero or upload reading surfaces.

### Inputs / Fields
- **Style:** Dropzones use Panel Soft fill, an 8px radius, centered content, and a teal-mixed border.
- **Focus:** Drag, hover, and keyboard focus shift to Mist Teal and translate up by 1px.
- **Error / Disabled:** Error messages use Clay Danger on Clay Mist with a compact icon. Disabled loading cards reduce opacity and use wait cursor.

### Navigation
- **Style:** View toggles and detail tabs are segmented controls on Pressed Paper with 8px outer radius.
- **Active State:** Active options use Panel Light, Botanical Ink, and a teal-mixed border.
- **Mobile Treatment:** Controls wrap instead of shrinking text. On narrow screens, tabs and primary actions stretch to full width when needed.

### Charts And Evidence
- **Emotion Map:** Square plot, Panel Soft background, Paper Line frame, dashed low-contrast grid, and dots with 180ms opacity transitions.
- **Theme Rows:** Full-width selectable rows with swatches, compact labels, and a 6px pill bar.
- **Co-occurrence Matrix:** Fixed grid cells, 6px radius, tonal intensity for strength, and a 2px Botanical Ink outline for selected cells.
- **Ranked Tracks:** Three-column bento grid on desktop, two columns under 920px, one column under 620px. Large rank numerals use teal at reduced opacity.

## 6. Do's and Don'ts

### Do:
- **Do** keep Project Orpheus observational, not judgmental.
- **Do** make report screens readable in five minutes before asking the user to inspect details.
- **Do** use Warm Paper, Panel Light, and Sage Muted as the dominant visual field.
- **Do** use Georgia for narrative headlines and Inter for interface work.
- **Do** preserve 1px borders, 8px radii, and flat tonal layering as the default component language.
- **Do** use icons inside buttons when the action benefits from quick recognition.
- **Do** keep motion to 180ms ease-out transitions on opacity, transform, background, or border color.

### Don't:
- **Don't** make this feel like a corporate analytics tool, overwhelming data dashboard, dense spreadsheet, or generic SaaS app.
- **Don't** use colored side-stripe borders on cards, list items, callouts, or alerts.
- **Don't** use gradient text.
- **Don't** use decorative glassmorphism.
- **Don't** lead with hero metrics or big-number stat blocks.
- **Don't** turn every evidence item into identical icon, heading, and paragraph cards.
- **Don't** use pure black or pure white for new tokens. Tint neutrals toward the existing botanical paper system.
- **Don't** use teal as decoration. Teal means action, selection, or evidence.
