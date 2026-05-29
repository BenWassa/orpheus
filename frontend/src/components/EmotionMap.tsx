import { EMOTION_ORDER, EMOTIONS } from '../taxonomy';
import { moodColorRGBA } from '../lib/moodColor';
import type { EmotionCategory, OrpheusReport, WindowScores } from '../types';

interface EmotionMapProps {
  report: OrpheusReport;
  activeWindow: WindowScores;
  comparisonWindow: WindowScores;
  selected: EmotionCategory | null;
  onSelect: (category: EmotionCategory | null) => void;
}

function fmtDateRange(from?: string, to?: string): string {
  if (!from || !to) return '';
  const fmt = (iso: string) =>
    new Date(iso + 'T00:00:00Z').toLocaleDateString('en-GB', { month: 'short', year: 'numeric', timeZone: 'UTC' });
  const f = fmt(from);
  const t = fmt(to);
  if (f === t) return f;
  const fromYear = from.slice(0, 4);
  const toYear = to.slice(0, 4);
  if (fromYear === toYear) {
    const fMonth = new Date(from + 'T00:00:00Z').toLocaleDateString('en-GB', { month: 'short', timeZone: 'UTC' });
    return `${fMonth}–${t}`;
  }
  return `${f}–${t}`;
}

export function EmotionMap({ report, activeWindow, comparisonWindow, selected, onSelect }: EmotionMapProps) {
  const activeRange = fmtDateRange(activeWindow.from_date, activeWindow.to_date);
  const comparisonRange = fmtDateRange(comparisonWindow.from_date, comparisonWindow.to_date);
  function handleKeyDown(e: React.KeyboardEvent<SVGGElement>, category: EmotionCategory) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onSelect(selected === category ? null : category);
    }
  }

  return (
    <section className="panel emotion-panel" aria-labelledby="emotion-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Mood shape</p>
          <h2 id="emotion-title">Emotional weather</h2>
        </div>
        <span className="depth-pill">{activeWindow.depth_label}</span>
      </div>

      <div className="emotion-plot" role="group" aria-label="Emotion categories — select to inspect">
        <svg viewBox="-112 -112 224 224" aria-hidden="true" focusable="false">
          <defs>
            <radialGradient id="grad-tr" cx="100%" cy="0%" r="100%" gradientUnits="objectBoundingBox">
              <stop offset="0%"  stopColor="rgb(255,204,0)"  stopOpacity="0.28" />
              <stop offset="55%" stopColor="rgb(255,204,0)"  stopOpacity="0.06" />
              <stop offset="100%" stopColor="rgb(255,204,0)" stopOpacity="0" />
            </radialGradient>
            <radialGradient id="grad-tl" cx="0%" cy="0%" r="100%" gradientUnits="objectBoundingBox">
              <stop offset="0%"  stopColor="rgb(255,71,71)"  stopOpacity="0.28" />
              <stop offset="55%" stopColor="rgb(255,71,71)"  stopOpacity="0.06" />
              <stop offset="100%" stopColor="rgb(255,71,71)" stopOpacity="0" />
            </radialGradient>
            <radialGradient id="grad-br" cx="100%" cy="100%" r="100%" gradientUnits="objectBoundingBox">
              <stop offset="0%"  stopColor="rgb(74,222,128)"  stopOpacity="0.28" />
              <stop offset="55%" stopColor="rgb(74,222,128)"  stopOpacity="0.06" />
              <stop offset="100%" stopColor="rgb(74,222,128)" stopOpacity="0" />
            </radialGradient>
            <radialGradient id="grad-bl" cx="0%" cy="100%" r="100%" gradientUnits="objectBoundingBox">
              <stop offset="0%"  stopColor="rgb(59,130,246)"  stopOpacity="0.28" />
              <stop offset="55%" stopColor="rgb(59,130,246)"  stopOpacity="0.06" />
              <stop offset="100%" stopColor="rgb(59,130,246)" stopOpacity="0" />
            </radialGradient>
          </defs>

          {/* Quadrant colour wash */}
          <rect x="-112" y="-112" width="224" height="224" fill="url(#grad-tr)" />
          <rect x="-112" y="-112" width="224" height="224" fill="url(#grad-tl)" />
          <rect x="-112" y="-112" width="224" height="224" fill="url(#grad-br)" />
          <rect x="-112" y="-112" width="224" height="224" fill="url(#grad-bl)" />

          {/* Axis lines */}
          <line x1="-100" y1="0" x2="100" y2="0" />
          <line x1="0" y1="-100" x2="0" y2="100" />

          {/* Axis labels */}
          <text x="-96" y="-4" textAnchor="start" className="axis-label">heavier</text>
          <text x="96" y="-4" textAnchor="end" className="axis-label">brighter</text>
          <text x="0" y="-104" textAnchor="middle" className="axis-label">high energy</text>
          <text x="0" y="112" textAnchor="middle" className="axis-label">low energy</text>

          {EMOTION_ORDER.map((category) => {
            const emotion = EMOTIONS[category];
            const score = activeWindow.emotion[category] ?? 0;
            const radius = 5 + score * 22;
            const cx = emotion.valence * 92;
            const cy = -emotion.arousal * 92;
            const isSelected = selected === category;
            const { solid } = moodColorRGBA(emotion.valence, emotion.arousal, 0.22);

            return (
              <g
                key={category}
                role="button"
                tabIndex={0}
                aria-pressed={isSelected}
                aria-label={`${emotion.label}: ${(score * 100).toFixed(0)}%`}
                onClick={() => onSelect(isSelected ? null : category)}
                onKeyDown={(e) => handleKeyDown(e, category)}
                style={{ cursor: 'pointer' }}
              >
                <circle
                  className={isSelected ? 'emotion-dot selected' : 'emotion-dot'}
                  cx={cx}
                  cy={cy}
                  r={radius}
                  style={{ fill: solid } as React.CSSProperties}
                />
                {/* Invisible hit-area so small dots are easier to tap */}
                <circle cx={cx} cy={cy} r={Math.max(radius, 14)} fill="transparent" />
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
                <dt>Recent window{activeRange && <> · <span style={{ fontWeight: 400 }}>{activeRange}</span></>}</dt>
                <dd>{((activeWindow.emotion[selected] ?? 0) * 100).toFixed(1)}%</dd>
              </div>
              <div>
                <dt>Usual pattern{comparisonRange && <> · <span style={{ fontWeight: 400 }}>{comparisonRange}</span></>}</dt>
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
          <p>Select an emotion above to inspect it. The larger marks show which feelings were most present in this report.</p>
        )}
      </div>
    </section>
  );
}
