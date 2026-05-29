# Frontend Upgrade Handoff

Generated: 2026-05-29

This flat folder is a focused frontend handoff for assessing style and presentation upgrades in Project Orpheus. It intentionally does not dump every frontend file. The strongest upgrade leverage is in the report reader: the app entry flow, hero summary, emotion map, theme panel, and the CSS system that carries the overall tone.

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

1. Hero/report opening
   - Source copy: `05_dashboard_HeroSummary.tsx`
   - Why: It sets the emotional tone, creates the first impression, and decides whether the product feels personal or generic.

2. Emotion and theme reading surface
   - Source copies: `06_dashboard_EmotionMap.tsx`, `07_dashboard_ThemePanel.tsx`
   - Why: These are the core visualizations. They need to feel inspectable, calm, and clear without looking like a SaaS chart grid.

3. Dashboard composition and progressive disclosure
   - Source copy: `04_dashboard_DashboardScreen.tsx`
   - Why: The current page already separates summary, primary reading, and deeper evidence tabs. Any upgrade should preserve that progressive disclosure.

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
5. `05_dashboard_HeroSummary.tsx` - report hero and primary actions.
6. `06_dashboard_EmotionMap.tsx` - valence/arousal/depth emotion plot.
7. `07_dashboard_ThemePanel.tsx` - theme prevalence rows and comparison deltas.
8. `08_styles.css` - current global styling.
9. `09_types.ts` - report, track, window, and category contracts.
10. `10_sampleReport.ts` - complete sample report used by the demo path.

## Important Omitted Files

These were intentionally omitted to stay within the 10-file limit:

- `frontend/src/lib/reportParser.ts`: important for runtime robustness, but less important for style assessment than the report contract and sample.
- `frontend/src/taxonomy.ts` and `frontend/src/lib/moodColor.ts`: label/color helpers used by the included components. A full implementation pass should inspect them in the repo.
- Evidence components such as `CoOccurrenceMatrix`, `ClusterList`, `EvidenceTracks`, and `TrendEvents`: visible in dashboard composition and styled in CSS, but secondary to the initial presentation upgrade.
- Upload/profile screens: represented through `03_app_flow_App.tsx`, but not copied in full.

If the expert needs implementation-ready coverage rather than assessment coverage, the next best second folder would include parser/taxonomy helpers plus the evidence, upload, and profile components.

## Assessment Notes

- The visual language is already moving toward warm paper, fine borders, serif report headlines, and restrained teal action states.
- The biggest risk is that the interface still reads as a set of bordered panels rather than a cohesive personal reading experience.
- The CSS is compact enough that style upgrades can be made globally, but component-specific class names mean visual polish still needs screen-by-screen review.
- The sample data includes enough emotional, thematic, track, trend, cluster, and co-occurrence material to evaluate dense and sparse states.
