import { THEME_ORDER, THEMES } from '../../../taxonomy';
import { moodColorRGBA } from '../../../lib/moodColor';
import type { ThemeCategory, WindowScores } from '../../../types';

interface ThemePanelProps {
  activeWindow: WindowScores;
  comparisonWindow: WindowScores;
  selected: ThemeCategory | null;
  onSelect: (category: ThemeCategory | null) => void;
}

export function ThemePanel({ activeWindow, comparisonWindow, selected, onSelect }: ThemePanelProps) {
  return (
    <section className="panel" aria-labelledby="theme-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Life themes</p>
          <h2 id="theme-title">What keeps appearing</h2>
        </div>
      </div>

      <div className="theme-list">
        {THEME_ORDER.map((category) => {
          const theme = THEMES[category];
          const score = activeWindow.theme[category] ?? 0;
          const baseline = comparisonWindow.theme[category] ?? 0;
          const isSelected = selected === category;

          const mc = moodColorRGBA(theme.valence ?? 0, theme.arousal ?? 0, 0.22);
          return (
            <button
              className={isSelected ? 'theme-row selected' : 'theme-row'}
              key={category}
              type="button"
              onClick={() => onSelect(isSelected ? null : category)}
            >
              <span
                className="theme-swatch"
                style={{ background: mc.background, border: `1px solid ${mc.border}` }}
              />
              <span className="theme-main">
                <strong>{theme.label}</strong>
                <span>{isSelected ? theme.description : `${(score * 100).toFixed(0)}% of recent listening`}</span>
                <span className="theme-bar">
                  <span style={{ width: `${Math.max(4, score * 100)}%`, background: mc.solid }} />
                </span>
              </span>
              <span className={score >= baseline ? 'delta up' : 'delta down'}>
                {formatDelta(score - baseline)}
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}

function formatDelta(delta: number) {
  const value = (delta * 100).toFixed(1);
  return delta > 0 ? `+${value}%` : `${value}%`;
}
