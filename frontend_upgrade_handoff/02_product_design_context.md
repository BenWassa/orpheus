# Product And Design Context

This file summarizes the repo's product and design documentation for a frontend expert. It is a synthesis of `PRODUCT.md`, `DESIGN.md`, `UI_UPGRADE_TODO.md`, and frontend design docs.

## Product Purpose

Project Orpheus helps individuals analyze their own Spotify listening history to reflect on emotional state and life themes. The output should feel like a personal mirror: observational, intuitive, explorable, minimal, and reflective.

The desired feel is closer to reading a thoughtful letter about yourself than using a corporate analytics dashboard.

## Design Principles

- Observational, not judgmental.
- Readable in five minutes.
- Personal and letter-like.
- Data as a mirror, not a spreadsheet.
- Calm first, inspectable second.
- Progressive disclosure over dense first-load dashboards.

## Anti-References

Avoid:

- Corporate analytics tools.
- Dense spreadsheets.
- Generic SaaS dashboards.
- Overwhelming widget grids.
- Hero metric cards as the first impression.
- Decorative glassmorphism or decorative teal usage.

## Current Visual Direction

The active visual system uses:

- Warm paper-like neutrals.
- Botanical green/teal accents.
- Serif display headlines with practical sans-serif UI text.
- Flat panels, fine borders, tonal fills, and minimal shadow.
- Teal for actions, selection, comparison, and evidence, not decoration.
- Plum sparingly for a secondary annotation layer.

Key active tokens are in `08_styles.css`:

- `--paper`
- `--paper-strong`
- `--ink`
- `--muted`
- `--line`
- `--panel`
- `--panel-soft`
- `--accent`
- `--accent-strong`
- `--accent-soft`
- `--plum`
- `--warn`
- `--danger`

## Component Intent

Hero summary:

- Should establish a personal, narrative report tone.
- Should not lead with generic metrics or a corporate dashboard header.
- Should keep actions available but visually secondary to the report content.

Emotion map:

- Should show the current emotion profile as a calm exploratory map.
- Should make selected state obvious through tone, opacity, border, or position.
- Should preserve accessibility through labels, focus states, and text equivalents.

Theme panel:

- Should read like ranked interpretive evidence, not a data table.
- Should make state-versus-trait deltas visible without requiring chart expertise.
- Should keep category language human and scan-friendly.

Evidence tabs:

- Should remain progressive disclosure.
- Co-occurrences, trends, clusters, tracks, and frequency tracks should not compete with the main report on first load.

## Current Upgrade Status From Repo

Completed checklist items in `UI_UPGRADE_TODO.md`:

- Replaced the six-widget dashboard grid with a narrative-first layout.
- Moved heavy evidence into progressive disclosure.
- Rewrote academic labels into more natural report language.
- Reduced generic SaaS visual cues.
- Improved mobile/tablet behavior for the report reader.
- Verified previous slices with `npm run build`.

Known note:

- `npx impeccable --json src` was attempted previously, but npm network access was unavailable in the sandbox at that time.

## Suggested Assessment Questions

- Does the hero feel personal enough, or does it still feel like a styled analytics summary?
- Are the emotion map and theme panel understandable within a few seconds?
- Does the warm paper system feel intentional, or too flat/monochrome?
- Are selected/focused states obvious without becoming visually loud?
- Does mobile preserve the report's reading rhythm?
- Are emotionally sensitive states, especially safety flags, presented calmly and responsibly?
