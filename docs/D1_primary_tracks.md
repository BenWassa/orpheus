# D1 - Primary Tracks

## Decision

Primary tracks are the tracks in a report window with the largest positive net
listening contribution from the user's plays in that window.

This is not a raw play-count list. A track becomes primary when repeated,
intentional, recent listening outweighs weak or negative evidence such as early
skips.

## Scoring Rule

Each play receives a base engagement score from `engagement_weight`:

| Play behavior | Base contribution |
|---|---:|
| Full play, at least 80% completion | `+1.0` |
| Partial play, over 30 seconds but under 80% completion | `+0.7` |
| Early skip, under 30 seconds | `-0.5` |
| Boundary skip, skipped near track end | `-0.25` |
| Shuffle source | adds `-0.1` |
| Explicit click/library play | adds `+0.1` |

The base score is multiplied by exponential time decay:

```text
decayed_play_weight = engagement_weight * exp(-ln(2) * age_days / half_life_days)
```

The half-life is window-specific:

| Window | Half-life | Interpretation |
|---|---:|---|
| State | 3 days | Recent mood and current preoccupation |
| Trait | 90 days | Longer-term listening baseline |

For each track:

```text
track_weight = sum(decayed_play_weight for all plays of that track in the window)
```

Tracks are sorted by `track_weight` descending. Only tracks with positive net
weight are eligible for `top_tracks`.

## Deliberation

Raw play count is too blunt for "primary." It treats accidental plays, autoplay,
shuffle, partial sampling, and intentional replays as equivalent. The report is
trying to show listening evidence that plausibly influenced the window's
emotional and thematic profile, so the ranking uses engagement-weighted,
time-decayed contribution instead.

Negative weights matter for ranking. If a user fully played a track once but
then immediately skipped it, that track should be demoted relative to a track
with cleaner positive engagement. This makes "Primary tracks" closer to
"tracks the window is actually supported by" than "tracks that merely appeared."

Negative weights do not subtract a skipped track's emotion or theme profile from
the window mixture. A skip is anti-evidence for that track's importance, not
evidence that the opposite emotion/theme occurred. Emotion, theme, and depth
aggregation therefore uses only positive play weights, while track and artist
ranking uses signed net weights.

## Data Contract

Backend aggregation emits `window.top_tracks` with:

```typescript
interface TopTrack {
  uri: string
  name?: string
  artist?: string
  album?: string
  weight: number
  play_count: number
  depth_score?: number
  depth_label?: 'surface' | 'engaged' | 'immersive'
  emotion_scores?: Partial<Record<EmotionCategory, number>>
  theme_scores?: Partial<Record<ThemeCategory, number>>
}
```

The report assembly layer adds `depth_label`. The frontend renders the list as
"Primary tracks" and displays `play_count` when present, falling back to numeric
`weight` when play count is unavailable.

## Invariants

- Aggregation only joins `track_scores` for the active `config.model_version`.
- One play contributes at most once to a track in a window.
- Signed net track weights determine primary ranking.
- Non-positive net tracks are excluded from `top_tracks`.
- Emotion/theme/depth window mixtures are based on positive weights only.
- Report assembly must not mutate the aggregation result while formatting tracks.

## Implementation

- Engagement and decay: `orpheus/aggregate/decay.py`
- Window aggregation and `top_tracks`: `orpheus/aggregate/windows.py`
- Report formatting and depth labels: `orpheus/output/assemble.py`
- UI rendering: `frontend/src/components/EvidenceTracks.tsx`
- Contract tests: `tests/test_aggregate.py::TestPrimaryTracks`
