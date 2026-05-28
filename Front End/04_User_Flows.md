# 04 — User Flows & Interaction Patterns

## Primary User Flows

### Flow 1: Upload & Summarize (First-Time User)

```
Start
  ↓
[Landing Page]
  - Welcome message: "Upload your Orpheus report to begin"
  - Drag-and-drop zone OR file picker button
  ↓
[User drops/selects JSON file]
  ↓
[Frontend: Validate schema]
  - If invalid: Show error modal with helpful message
  - If valid: Parse and store in state
  ↓
[Auto-navigate to Dashboard]
  ↓
[Summary View (Hero)]
  - Headline: "Your listening clusters around [top emotion] & [top theme]"
  - State-vs-trait comparison cards (with delta badges)
  - Key insights bullets (generated narrative from backend)
  - Preview chart (small emotion scatter plot)
  ↓
[User reads 2–3 min, then decides:]
  - "That's it" → Export & done
  - "Tell me more" → Scroll down or click into drill-downs
```

**Key UX points**:
- Validation happens silently (no loading spinner if < 2s)  
- Error messages are friendly, not technical ("This doesn't look like an Orpheus report. Did you select the right file?")  
- Auto-scroll to summary so user doesn't need to click or navigate  

---

### Flow 2: Explore Emotions (Curious User)

```
[Dashboard Summary]
  ↓
[User clicks "View emotion breakdown" or scrolls to chart]
  ↓
[Emotion Scatter Plot (VA × D)]
  - Bubbles colored by category
  - X-axis: Valence (−1 to +1)
  - Y-axis: Arousal (−1 to +1)
  - Size: Depth
  ↓
[User hovers bubble]
  - Tooltip shows: emotion name, prevalence, and score when available
  ↓
[User clicks bubble]
  - Detail panel opens
  - Shows: prevalence, state-vs-trait movement, related shifts, related clusters
  - Shows top tracks only if the report includes them
  ↓
[User reviews evidence]
  - Backend narratives explain why the category is moving or co-occurring
  - Track-level score breakdown is deferred until backend emits cluster members
  ↓
[User closes and returns to chart]
  - State preserved; can explore another bubble
```

**Key UX points**:
- Hover feedback is immediate (no loading)  
- Click → drill-down should be smooth (fade in or slide)  
- Back button or overlay close brings user back to chart  
- Chart zoom/pan optional (nice-to-have for MVP)  

---

### Flow 3: Spot-Check Evidence (Skeptical User)

```
[Dashboard]
  ↓
[User clicks a cluster or category detail]
  ↓
[Evidence Panel]
  - Current vs baseline prevalence
  - Shift direction and delta when available
  - Trend narrative when available
  - Co-occurrence observed vs expected values
  - Cluster centroid and dominant emotion/theme weights
  ↓
[User reads and decides:]
  - "This makes sense" → Close modal
  - "This doesn't match my intuition" → Skip track, explore next
```

**Key UX points**:
- Transparency is trust  
- Show numeric evidence where backend provides it  
- Use backend narrative fields to explain trends and co-occurrences  
- Easy dismissal (close button, Escape key)  
- Full per-track scoring belongs in a later flow once the report includes track-level scores  

---

### Flow 4: Analyze Trends (Time-Conscious User)

```
[Dashboard]
  ↓
[User navigates to "Trends" section]
  ↓
[Recent Movement List]
  - One row per backend trend event
  - Category, axis, direction, magnitude, narrative
  ↓
[User filters categories]
  - Toggle emotion/theme axes
  - Filter to notable movement only
  ↓
[User expands event]
  - Shows trend narrative and related shifts or co-occurrences
  ↓
[Future line chart]
  - Requires backend weekly series output
```

**Key UX points**:
- Filtering is immediate and reversible  
- Event copy should make direction and magnitude clear  
- Do not render fake weekly lines from event-only data  

---

### Flow 5: Export & Share (Data-Conscious User)

```
[Dashboard]
  ↓
[User clicks "Export" button (bottom right/footer)]
  ↓
[Export Modal]
  - MVP option: JSON
  - Future options: CSV | PNG
  ↓
[User selects JSON]
  ↓
[Download button]
  - File named: `orpheus_report_[date]_[type].json`
  - Contains: metadata, state, trait, shifts, trends, clusters, co_occurrences, safety_flags
  ↓
[File downloaded to user's computer]
  ↓
[Modal closes]
```

**Key UX points**:
- Safe export: Never include raw listening history  
- File naming: Clear, timestamped  
- Multiple formats can be added after MVP; JSON is enough for friend testing  
- Confirmation toast: "Report exported successfully"  

---

## Secondary Flows

### Flow 6: View Co-Occurrences (Pattern-Seeker)

```
[Dashboard]
  ↓
[User navigates to "Patterns" or "Co-Occurrences" section]
  ↓
[Heatmap / Network Graph / Matrix]
  - Rows: Emotions
  - Columns: Themes
  - Cell color intensity: Co-occurrence ratio (0.0–1.0)
  ↓
[User hovers or clicks cell]
  - Tooltip/modal: observed count, expected count, strength, narrative
  ↓
[User explores related evidence]
  - Links to related clusters or category details when available
```

**Key UX points**:
- Heatmap is read-only; clicking brings data, not actions  
- Color intensity should be consistent with palette (same as emotion/theme colors)  

---

### Flow 7: Compare State vs Trait (Baseline Checker)

```
[Dashboard → Summary section]
  ↓
[Toggle: "Compare State vs Trait"]
  ↓
[If toggled OFF: Show only State (current)]
  ↓
[If toggled ON: Show both side-by-side]
  - State cards on left (3-day window, more recent/volatile)
  - Trait cards on right (90-day window, stable baseline)
  - Delta badge: "↑ +18%" if State > Trait, "↓ −8%" if State < Trait
  ↓
[User can toggle back/forth]
  - Toggle state preserved in URL (optional for MVP)
  - Smooth transition (300ms)
```

**Key UX points**:
- Toggle is binary and obvious (not a hidden setting)  
- Delta badges use color-coded arrows (up = positive change, down = negative)  
- Transition smoothness aids comprehension  

---

## Interaction Patterns

### Pattern A: Evidence Drill-Down (Expandable Section)

**When**: User clicks category or cluster header to inspect supporting evidence

```
Collapsed:
┌──────────────────┐
│ [+] Nostalgia    │ elevated
└──────────────────┘

Expanded:
┌──────────────────┐
│ [−] Nostalgia    │ elevated
├──────────────────┤
│ Delta: +0.08     │
│ Trend: rising    │
│ Pair: heartbreak │
└──────────────────┘
```

**UX details**:
- Chevron icon rotates (↓ → ↑)  
- Status or strength visible in header  
- Smooth expand/collapse (300ms)  
- Track list appears only when report data includes track members  

---

### Pattern B: Modal Overlay (Detail View)

**When**: User needs full detail for a category, cluster, trend, or co-occurrence

```
Background (dimmed)
  ↓
[Modal overlay]
  ┌─────────────────────────┐
  │ [×] Close button        │
  ├─────────────────────────┤
  │ Category / Cluster      │
  │ Direction + strength    │
  │ Evidence narrative      │
  ├─────────────────────────┤
  │ [Related view] [Export] │
  └─────────────────────────┘
```

**UX details**:
- Click outside modal → close  
- Escape key → close  
- Close button (X) in top-right  
- Smooth fade-in/out (200ms)  
- Modal doesn't scroll page behind it (overflow: hidden on body)  

---

### Pattern C: Filtering & Sorting

**When**: User views categories, clusters, trends, or co-occurrences and wants to filter/sort

```
[Evidence List Header]
  ┌─────────────────────────────────────┐
  │ Filter: [Axis ▼] [Strength ▼]       │
  │ Sort by: [Magnitude ▼]              │
  │                                     │
  │ Clear filters                       │
  └─────────────────────────────────────┘

[Evidence List]
  (Filtered and sorted)
```

**UX details**:
- Dropdowns open on click (not hover)  
- Selected value shown in button label  
- "Clear filters" button appears only if filters active  
- List updates immediately on filter change (no "Apply" button)  
- URL query params updated (optional for deep-linking)  

---

### Pattern D: Toggle Switch (Binary Choice)

**When**: State vs Trait, or Show/Hide Legend

```
Default (State only):
┌──────────────────────┐
│ Show trait baseline? ◯ │ Off
└──────────────────────┘

Active (State + Trait):
┌──────────────────────┐
│ Show trait baseline? ◐ │ On
└──────────────────────┘
```

**UX details**:
- Pill-shaped button  
- Left side = Off, Right side = On  
- Smooth slide transition (200ms)  
- Label and icon (if space permits)  

---

### Pattern E: Tooltip (Hover Hint)

**When**: User hovers over data point or icon

```
[Bubble in scatter plot]
  ↓ (hover 300ms)
[Tooltip appears above bubble]
  ┌─────────────────────┐
  │ Nostalgia & Longing │
  │ 0.35 (current)      │
  │ • All Too Well      │
  │ • Exile             │
  │ • Soon You'll Get…  │
  └─────────────────────┘
  ↓
Tooltip disappears when mouse leaves
```

**UX details**:
- Delay before appear: 300ms (prevent hover noise)  
- Fade-in: 150ms  
- Positioned above (or below if near top of viewport)  
- Max width: 250px (wrap long text)  
- Pointer arrow pointing to target element  
- Text: 12px, readable contrast  

---

### Pattern F: Loading State (Async Operations)

**When**: File parsing, large data load, API call

```
[Uploading...]
  ┌─────────────────────┐
  │    [spinner]        │
  │  Validating report… │
  └─────────────────────┘
```

**UX details**:
- Spinner animation (optional; can use indeterminate progress bar)  
- Loading text below spinner  
- Duration: typically <2s for JSON parsing  
- If >2s, show progress or allow cancel  

---

## Keyboard Navigation

All interactive elements should be keyboard-accessible:

| Key | Action |
|---|---|
| `Tab` | Move focus to next element |
| `Shift + Tab` | Move focus to previous element |
| `Enter` | Activate button, toggle, or open modal |
| `Space` | Toggle checkbox, toggle switch |
| `Escape` | Close modal, collapse section |
| `Arrow Up/Down` | Navigate list items, chart categories |
| `Arrow Left/Right` | Change chart view (state/trait), filter value |

**Visible focus indicators**: 2px solid outline (teal) with 2px offset

---

## Accessibility: Screen Reader Notes

### Headings
```html
<h1>Your listening clusters around nostalgia and heartbreak</h1>
<h2>Current Mood</h2>
<h3>Emotion Breakdown</h3>
```

### Charts
```html
<div role="img" aria-label="Emotion scatter plot showing distribution of nostalgia (top right), sadness (bottom left), and peacefulness (top left). Nostalgias is dominant (35% of listening).">
  [SVG chart goes here]
</div>
```

### Links
```html
<a href="https://open.spotify.com/track/..." aria-label="Listen on Spotify">
  [Spotify logo or link text]
</a>
```

### Form Labels
```html
<label for="confidence-filter">Minimum Confidence</label>
<input id="confidence-filter" type="range" min="0" max="1" step="0.1" />
```

---

## Error Handling

### Invalid File
```
[Error Modal]
┌───────────────────────────────────┐
│ ⚠ Invalid Report                  │
├───────────────────────────────────┤
│ This doesn't look like an Orpheus  │
│ report. Make sure you're uploading │
│ the JSON file generated by the     │
│ backend analysis.                  │
│                                   │
│ [Try Again] [View Help]           │
└───────────────────────────────────┘
```

### Network Timeout (if future backend integration)
```
[Error Toast]
┌──────────────────────────────┐
│ ⚠ Connection timeout         │
│ Please check your network    │
│ [Retry] [Dismiss]            │
└──────────────────────────────┘
```

---

## Success Confirmations

### Export Complete
```
[Toast (bottom right, 3s auto-dismiss)]
┌──────────────────────────────┐
│ ✓ Report exported (JSON)     │
│   Downloaded to Downloads/   │
│   orpheus_2026-05-27.json    │
└──────────────────────────────┘
```

---

## Edge Cases

### Empty Report
If report has 0 clusters or no emotion data:
```
[Friendly message]
"This report doesn't have enough data to analyze.
Try uploading a report with more listening history."
```

### Very Large Report (50+ MB)
- Warn user: "This report is large and may take a moment to load"  
- Show progress bar during parsing  
- Virtualize track lists (lazy-load)  

### Missing Track-Level Data
If report lacks `album_art_url`, `play_count`, score breakdowns, or track members:
- Gracefully degrade  
- Show cluster/category evidence instead  
- Omit unavailable table columns  
- Never error or crash  

---

*Last updated: 2026-05-27*
