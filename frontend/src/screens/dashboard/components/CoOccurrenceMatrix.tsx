import { EMOTION_ORDER, EMOTIONS, THEME_ORDER, THEMES } from '../../../taxonomy';
import type { CoOccurrence, EmotionCategory, ThemeCategory } from '../../../types';

interface CoOccurrenceMatrixProps {
  coOccurrences: CoOccurrence[];
  scopeLabel: string;
  selected: { emotion: EmotionCategory; theme: ThemeCategory } | null;
  onSelect: (value: { emotion: EmotionCategory; theme: ThemeCategory } | null) => void;
}

export function CoOccurrenceMatrix({ coOccurrences, scopeLabel, selected, onSelect }: CoOccurrenceMatrixProps) {
  const activePair = selected ? findPair(coOccurrences, selected.emotion, selected.theme) : null;
  const isEmpty = coOccurrences.length === 0;

  return (
    <section className="editorial-matrix-section" aria-labelledby="co-title">
      <div className="matrix-editorial-header">
        <p className="eyebrow">Interactive topology</p>
        <h3 id="co-title" className="serif-subhead">Intersecting currents</h3>
        <p className="matrix-context-description">
          This matrix graphs where distinct feelings meet structural themes during your <strong>{scopeLabel}</strong>.
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
                  const pair = findPair(coOccurrences, emotion, theme);
                  const isSelected = selected?.emotion === emotion && selected.theme === theme;
                  const highLift = pair?.lift !== undefined && pair.lift > 1.2;

                  return (
                    <button
                      key={`${emotion}-${theme}`}
                      className={`matrix-node-cell ${pair ? pair.strength : 'is-barren'} ${isSelected ? 'is-focused' : ''} ${highLift ? 'has-high-lift' : ''}`}
                      type="button"
                      disabled={!pair}
                      onClick={() => onSelect(isSelected ? null : { emotion, theme })}
                      aria-label={
                        pair ? `${EMOTIONS[emotion].label} bounded by ${THEMES[theme].label}` : undefined
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
                      <span className="stat-label">Statistical lift</span>
                      <span className="stat-value">x{activePair.lift.toFixed(2)}</span>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="annotation-placeholder-card">
                <p>Select an intersecting node in the structural grid to isolate evidence telemetry and thematic breakdowns.</p>
              </div>
            )}
          </aside>
        </div>
      )}
    </section>
  );
}

function findPair(items: CoOccurrence[], emotion: EmotionCategory, theme: ThemeCategory): CoOccurrence | undefined {
  return items.find((item) => item.emotion === emotion && item.theme === theme);
}
