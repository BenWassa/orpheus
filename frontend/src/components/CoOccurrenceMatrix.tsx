import { EMOTION_ORDER, EMOTIONS, THEME_ORDER, THEMES } from '../taxonomy';
import type { CoOccurrence, EmotionCategory, OrpheusReport, ThemeCategory } from '../types';

interface CoOccurrenceMatrixProps {
  report: OrpheusReport;
  selected: { emotion: EmotionCategory; theme: ThemeCategory } | null;
  onSelect: (value: { emotion: EmotionCategory; theme: ThemeCategory } | null) => void;
}

export function CoOccurrenceMatrix({ report, selected, onSelect }: CoOccurrenceMatrixProps) {
  const activePair = selected ? findPair(report.co_occurrences, selected.emotion, selected.theme) : null;

  return (
    <section className="panel wide-panel" aria-labelledby="co-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Emotion × theme</p>
          <h2 id="co-title">Co-occurrence evidence</h2>
        </div>
      </div>

      <div className="matrix-layout">
        <div className="matrix-grid">
          <span />
          {EMOTION_ORDER.map((emotion) => (
            <span className="matrix-label" key={emotion}>
              {EMOTIONS[emotion].short}
            </span>
          ))}
          {THEME_ORDER.map((theme) => (
            <div className="matrix-row" key={theme}>
              <span className="matrix-label theme-axis">{THEMES[theme].short}</span>
              {EMOTION_ORDER.map((emotion) => {
                const pair = findPair(report.co_occurrences, emotion, theme);
                const isSelected = selected?.emotion === emotion && selected.theme === theme;
                return (
                  <button
                    key={`${emotion}-${theme}`}
                    className={pair ? `matrix-cell ${pair.strength} ${isSelected ? 'selected' : ''}` : 'matrix-cell empty'}
                    type="button"
                    disabled={!pair}
                    onClick={() => onSelect(isSelected ? null : { emotion, theme })}
                    aria-label={pair ? `${EMOTIONS[emotion].label} with ${THEMES[theme].label}` : undefined}
                  >
                    {pair ? pair.observed : ''}
                  </button>
                );
              })}
            </div>
          ))}
        </div>

        <aside className="detail-well matrix-detail">
          {activePair ? (
            <>
              <h3>
                {EMOTIONS[activePair.emotion].label} + {THEMES[activePair.theme].label}
              </h3>
              <p>{activePair.narrative}</p>
              <dl className="metric-grid">
                <div>
                  <dt>Observed</dt>
                  <dd>{activePair.observed}</dd>
                </div>
                <div>
                  <dt>Expected</dt>
                  <dd>{activePair.expected}</dd>
                </div>
              </dl>
            </>
          ) : (
            <p>Select a populated cell to read the relationship behind the count.</p>
          )}
        </aside>
      </div>
    </section>
  );
}

function findPair(items: CoOccurrence[], emotion: EmotionCategory, theme: ThemeCategory): CoOccurrence | undefined {
  return items.find((item) => item.emotion === emotion && item.theme === theme);
}
