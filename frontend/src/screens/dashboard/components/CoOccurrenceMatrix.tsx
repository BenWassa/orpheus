import type { CSSProperties } from 'react';
import { EMOTION_ORDER, EMOTIONS, THEME_ORDER, THEMES } from '../../../taxonomy';
import type { CoOccurrence, CoOccurrenceCell, EmotionCategory, ThemeCategory } from '../../../types';

interface CoOccurrenceMatrixProps {
  coOccurrences: CoOccurrence[];
  liftMatrix: CoOccurrenceCell[];
  scopeLabel: string;
  selected: { emotion: EmotionCategory; theme: ThemeCategory } | null;
  onSelect: (value: { emotion: EmotionCategory; theme: ThemeCategory } | null) => void;
}

// Lift saturates the diverging scale at ±30% from baseline. The real signal is
// compressed near 1.0 (the theme classifier is near-uniform), so a tight domain
// keeps the genuine tilts visible rather than washing everything to neutral.
const LIFT_SPREAD = 0.3;

export function CoOccurrenceMatrix({
  coOccurrences,
  liftMatrix,
  scopeLabel,
  selected,
  onSelect,
}: CoOccurrenceMatrixProps) {
  // No matrix means the window had too little data for the lift comparison.
  const isEmpty = liftMatrix.length === 0;

  const liftByCell = new Map<string, number>();
  for (const cell of liftMatrix) liftByCell.set(cellKey(cell.emotion, cell.theme), cell.lift);

  const activePair = selected ? findPair(coOccurrences, selected.emotion, selected.theme) : null;
  const activeLift = selected ? liftByCell.get(cellKey(selected.emotion, selected.theme)) : undefined;

  return (
    <section className="editorial-matrix-section" aria-labelledby="co-title">
      <div className="matrix-editorial-header">
        <p className="eyebrow">Interactive topology</p>
        <h3 id="co-title" className="serif-subhead">Intersecting currents</h3>
        <p className="matrix-context-description">
          Every feeling × theme square, shaded by how much more (or less) they coincide than chance
          predicts, across your <strong>{scopeLabel}</strong>. Most pairings sit near baseline — the
          few that tilt are the real signal.
        </p>
      </div>

      {isEmpty ? (
        <div className="matrix-empty-canvas">
          <p>
            The system hasn't isolated distinct theme intersections within this specific tracking window.
            Continued playback data will populate this landscape over time.
          </p>
        </div>
      ) : (
        <div className="matrix-layout-surface">
          <div className="matrix-interactive-grid" role="grid" aria-label="Pattern intersections">
            <span className="grid-corner-blank" />

            {EMOTION_ORDER.map((emotion) => (
              <span className="matrix-column-axis-label" key={emotion}>
                {EMOTIONS[emotion].short}
              </span>
            ))}

            {THEME_ORDER.map((theme) => (
              <div className="matrix-grid-contents-row" key={theme} role="row">
                <span className="matrix-row-axis-label">{THEMES[theme].short}</span>
                {EMOTION_ORDER.map((emotion) => {
                  const lift = liftByCell.get(cellKey(emotion, theme));
                  const pair = findPair(coOccurrences, emotion, theme);
                  const isSelected = selected?.emotion === emotion && selected.theme === theme;
                  const hasData = lift !== undefined;

                  return (
                    <button
                      key={`${emotion}-${theme}`}
                      className={`matrix-node-cell ${hasData ? '' : 'is-barren'} ${isSelected ? 'is-focused' : ''} ${pair ? 'is-notable' : ''}`}
                      style={isSelected ? undefined : cellStyle(lift)}
                      type="button"
                      disabled={!hasData}
                      onClick={() => onSelect(isSelected ? null : { emotion, theme })}
                      aria-label={
                        hasData
                          ? `${EMOTIONS[emotion].label} with ${THEMES[theme].label}, ${liftDescriptor(lift)}`
                          : undefined
                      }
                    >
                      <span className="node-value-indicator">{pair ? pair.observed : ''}</span>
                    </button>
                  );
                })}
              </div>
            ))}
          </div>

          <aside className="matrix-side-annotation-drawer">
            <div className="matrix-lift-legend" aria-hidden="true">
              <span className="legend-bar" />
              <div className="legend-labels">
                <span>Avoided</span>
                <span>Expected</span>
                <span>Elevated</span>
              </div>
            </div>

            {activePair ? (
              <div className="annotation-content-card">
                <span className="annotation-eyebrow">Observed affinity</span>
                <h4>
                  {EMOTIONS[activePair.emotion].label} <span className="conjunction">&amp;</span>{' '}
                  {THEMES[activePair.theme].label}
                </h4>
                <p className="annotation-narrative-prose">{activePair.narrative}</p>

                <div className="annotation-stats-strip">
                  <div className="stat-datapoint">
                    <span className="stat-label">Co-occurrences</span>
                    <span className="stat-value">{activePair.observed}</span>
                  </div>
                  <div className="stat-datapoint">
                    <span className="stat-label">Expected</span>
                    <span className="stat-value">{activePair.expected.toFixed(1)}</span>
                  </div>
                  {activePair.lift !== undefined && (
                    <div className="stat-datapoint highlighted-lift">
                      <span className="stat-label">vs expected</span>
                      <span className="stat-value">{liftBadge(activePair.lift)}</span>
                    </div>
                  )}
                </div>
              </div>
            ) : selected && activeLift !== undefined ? (
              <div className="annotation-content-card is-baseline">
                <span className="annotation-eyebrow">Around baseline</span>
                <h4>
                  {EMOTIONS[selected.emotion].label} <span className="conjunction">&amp;</span>{' '}
                  {THEMES[selected.theme].label}
                </h4>
                <p className="annotation-narrative-prose">
                  These appear together {liftDescriptor(activeLift)} — not a standout connection in this window.
                </p>
                <div className="annotation-stats-strip">
                  <div className="stat-datapoint highlighted-lift">
                    <span className="stat-label">vs expected</span>
                    <span className="stat-value">{liftBadge(activeLift)}</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="annotation-placeholder-card">
                <p>Select any square to see how often that feeling and theme coincide versus what chance predicts.</p>
              </div>
            )}
          </aside>
        </div>
      )}
    </section>
  );
}

function cellKey(emotion: EmotionCategory, theme: ThemeCategory): string {
  return `${emotion}|${theme}`;
}

function findPair(items: CoOccurrence[], emotion: EmotionCategory, theme: ThemeCategory): CoOccurrence | undefined {
  return items.find((item) => item.emotion === emotion && item.theme === theme);
}

// Diverging color centered at lift 1.0: green for elevated, cool slate for
// avoided, near-neutral at baseline. Background only — text color is handled by
// CSS reacting to the data-tone attribute would be overkill, so dark elevated
// cells just keep ink text (numbers only appear on notable cells, which sit in
// the lighter-to-mid range).
function cellStyle(lift: number | undefined): CSSProperties | undefined {
  if (lift === undefined) return undefined;
  const dev = lift - 1;
  if (Math.abs(dev) < 0.01) return { background: 'var(--paper-strong)' };
  const t = Math.min(Math.abs(dev) / LIFT_SPREAD, 1);
  if (dev > 0) {
    const L = 0.95 - 0.46 * t;
    const C = 0.025 + 0.1 * t;
    return { background: `oklch(${L.toFixed(3)} ${C.toFixed(3)} 172)`, borderColor: 'transparent' };
  }
  const L = 0.95 - 0.14 * t;
  const C = 0.01 + 0.045 * t;
  return { background: `oklch(${L.toFixed(3)} ${C.toFixed(3)} 248)`, borderColor: 'transparent' };
}

function liftBadge(lift: number): string {
  const pct = Math.round((lift - 1) * 100);
  return pct >= 0 ? `+${pct}%` : `${pct}%`;
}

function liftDescriptor(lift: number | undefined): string {
  if (lift === undefined) return 'no data';
  const pct = Math.round((lift - 1) * 100);
  if (Math.abs(pct) < 3) return 'about as often as expected';
  return pct > 0 ? `${pct}% more than expected` : `${Math.abs(pct)}% less than expected`;
}
