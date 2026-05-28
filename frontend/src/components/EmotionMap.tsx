import { EMOTION_ORDER, EMOTIONS } from '../taxonomy';
import type { EmotionCategory, OrpheusReport, WindowScores } from '../types';

interface EmotionMapProps {
  report: OrpheusReport;
  activeWindow: WindowScores;
  comparisonWindow: WindowScores;
  selected: EmotionCategory | null;
  onSelect: (category: EmotionCategory | null) => void;
}

export function EmotionMap({ report, activeWindow, comparisonWindow, selected, onSelect }: EmotionMapProps) {
  return (
    <section className="panel emotion-panel" aria-labelledby="emotion-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Valence × arousal</p>
          <h2 id="emotion-title">Emotion coordinates</h2>
        </div>
        <span className="depth-pill">{activeWindow.depth_label}</span>
      </div>

      <div className="emotion-plot" role="img" aria-label="Emotion categories plotted by valence and arousal">
        <svg viewBox="-112 -112 224 224">
          <line x1="-100" y1="0" x2="100" y2="0" />
          <line x1="0" y1="-100" x2="0" y2="100" />
          <text x="-100" y="8">low valence</text>
          <text x="66" y="8">high valence</text>
          <text x="4" y="-94">high energy</text>
          <text x="4" y="100">low energy</text>

          {EMOTION_ORDER.map((category) => {
            const emotion = EMOTIONS[category];
            const score = activeWindow.emotion[category] ?? 0;
            const comparisonScore = comparisonWindow.emotion[category] ?? 0;
            const radius = 5 + score * 22;
            const cx = emotion.valence * 92;
            const cy = -emotion.arousal * 92;
            const isSelected = selected === category;

            return (
              <g key={category}>
                <circle className="comparison-dot" cx={cx + comparisonScore * 12} cy={cy} r={3 + comparisonScore * 14} />
                <button onClick={() => onSelect(isSelected ? null : category)} aria-label={`Inspect ${emotion.label}`}>
                  <circle
                    className={isSelected ? 'emotion-dot selected' : 'emotion-dot'}
                    cx={cx}
                    cy={cy}
                    r={radius}
                    style={{ '--dot-color': emotion.color } as React.CSSProperties}
                  />
                </button>
                <text className="dot-label" x={cx} y={cy - radius - 5} textAnchor="middle">
                  {emotion.short}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      <div className="detail-well">
        {selected ? (
          <>
            <h3>{EMOTIONS[selected].label}</h3>
            <p>{EMOTIONS[selected].description}</p>
            <dl className="metric-grid">
              <div>
                <dt>Current window</dt>
                <dd>{((activeWindow.emotion[selected] ?? 0) * 100).toFixed(1)}%</dd>
              </div>
              <div>
                <dt>Comparison</dt>
                <dd>{((comparisonWindow.emotion[selected] ?? 0) * 100).toFixed(1)}%</dd>
              </div>
            </dl>
            {report.shifts
              .filter((shift) => shift.category === selected)
              .map((shift) => (
                <p className="evidence-copy" key={shift.narrative}>
                  {shift.narrative}
                </p>
              ))}
          </>
        ) : (
          <p>Select an emotion point to inspect state, baseline, and related narrative evidence.</p>
        )}
      </div>
    </section>
  );
}
