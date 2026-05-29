# Orpheus UI Upgrade Todo

## Goal

Make the frontend feel like a personal listening mirror: narrative-first, calm, readable in five minutes, and still transparent enough for skeptical inspection.

## Work Slices

- [x] P0: Replace the six-widget dashboard grid with a narrative-first layout that shows the summary, emotion map, and themes first.
- [x] P0: Move heavy evidence views into progressive disclosure so co-occurrences, trends, clusters, and tracks do not compete on first load.
- [x] P1: Rewrite academic labels into natural report language without hiding the underlying data.
- [x] P1: Reduce generic SaaS visual cues: hard cards, dashed upload treatment, harsh black primary buttons, and uniform widget spacing.
- [x] P2: Improve mobile and tablet behavior for the report reader, especially the emotion plot, matrix, controls, and action buttons.
- [x] P2: Add focused verification: TypeScript build, source-pattern scan, graphify update, and a quick git review before final handoff.

## Commit Plan

- [x] Commit the upgrade checklist and narrative layout changes together once the first usable reader structure is in place.
- [x] Commit terminology and copy cleanup after the UI reads clearly end to end.
- [x] Commit visual polish, responsive hardening, and verification updates as the final frontend fix slice.

## Verification Notes

- `npm run build` passed after the layout slice.
- `npm run build` passed after the language slice.
- `npm run build` passed after the polish slice.
- `npx impeccable --json src` was attempted, but the sandbox could not reach npm. Escalated rerun was rejected because it would execute third-party code with network access.
