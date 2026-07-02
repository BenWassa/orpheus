# Frontend Upgrade Handoff

Generated: 2026-05-29

This flat folder is a focused frontend handoff for assessing style and presentation upgrades in Project Orpheus. It intentionally does not dump every frontend file. This refresh focuses on the report reader and the latest window-scoped evidence changes: app flow, dashboard composition, co-occurrence evidence, parser/runtime data shape, sample data, and the CSS system that carries the overall tone.

## Product Target

Orpheus is a local-first listening mirror for emotional and thematic music analysis. The interface should feel like a quiet, personal reading surface, not a corporate dashboard or analytics product. The user should be able to understand the main report in about five minutes, then inspect evidence if desired.

## Current Frontend Stack

- React 19.1
- TypeScript 5.8
- Vite 6.3
- `lucide-react` for icons
- No charting package in the selected surface; the emotion map and theme bars are hand-built with HTML/CSS.

Main source folder in the repo: `frontend/src/`

## Selected Upgrade Focus

1. Dashboard report flow
   - Source copies: `03_app_flow_App.tsx`, `04_dashboard_DashboardScreen.tsx`
   - Why: These files show how users enter the report, switch recent/usual views, and move into deeper evidence.

2. Window-scoped co-occurrence evidence
   - Source copies: `05_dashboard_CoOccurrenceMatrix.tsx`, `06_dashboard_detailViews.ts`
   - Why: Recent changes make connections respond to the Recent / Usual toggle instead of always using global report-level co-occurrences. This is now the most important interaction contract to assess.

3. Parser and report contract
   - Source copies: `07_reportParser.ts`, `09_types.ts`
   - Why: Window-level `co_occurrences` and optional `lift` are now part of the frontend contract. Presentation changes should respect empty evidence states and scoped comparisons.

4. Global visual system
   - Source copy: `08_styles.css`
   - Why: Most presentation choices are centralized in one CSS file: color tokens, typography, panels, controls, chart layout, responsive behavior, and evidence styling.

5. Data shape and representative sample
   - Source copies: `09_types.ts`, `10_sampleReport.ts`
   - Why: The designer/dev needs realistic categories, windows, tracks, clusters, co-occurrences, and safety flags to assess empty, dense, and emotionally sensitive states.

## Files In This Folder

1. `01_frontend_upgrade_brief.md` - this orientation file.
2. `02_product_design_context.md` - product/design constraints and current improvement notes.
3. `03_app_flow_App.tsx` - current app state flow: profiles, upload fallback, demo, reload.
4. `04_dashboard_DashboardScreen.tsx` - dashboard composition and evidence tabs.
5. `05_dashboard_CoOccurrenceMatrix.tsx` - scoped emotion/theme connection matrix and empty state.
6. `06_dashboard_detailViews.ts` - evidence tab definitions and scope metadata.
7. `07_reportParser.ts` - report normalization, including window-level co-occurrences.
8. `08_styles.css` - current global styling.
9. `09_types.ts` - report, track, window, and category contracts.
10. `10_sampleReport.ts` - complete sample report used by the demo path.

## Important Omitted Files

These were intentionally omitted to stay within the 10-file limit:

- `frontend/src/screens/dashboard/components/HeroSummary.tsx`: important to first impression, but unchanged in the latest source update and partially visible through dashboard composition and CSS.
- `frontend/src/screens/dashboard/components/EmotionMap.tsx` and `ThemePanel.tsx`: core visualizations, but unchanged in the latest source update.
- `frontend/src/taxonomy.ts` and `frontend/src/lib/moodColor.ts`: label/color helpers used by dashboard components. A full implementation pass should inspect them in the repo.
- Evidence components such as `ClusterList`, `EvidenceTracks`, and `TrendEvents`: visible in dashboard composition and styled in CSS, but secondary to the current co-occurrence scope change.
- Upload/profile screens: represented through `03_app_flow_App.tsx`, but not copied in full.

If the expert needs implementation-ready coverage rather than assessment coverage, the next best second folder would include parser/taxonomy helpers plus the evidence, upload, and profile components.

## Assessment Notes

- The visual language is already moving toward warm paper, fine borders, serif report headlines, and restrained teal action states.
- The biggest risk is that the interface still reads as a set of bordered panels rather than a cohesive personal reading experience.
- The CSS is compact enough that style upgrades can be made globally, but component-specific class names mean visual polish still needs screen-by-screen review.
- The sample data includes enough emotional, thematic, track, trend, cluster, and co-occurrence material to evaluate dense and sparse states.
