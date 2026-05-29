import { useMemo } from 'react';
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
  const orderedThemes = useMemo(
    () =>
      [...THEME_ORDER].sort((left, right) => {
        const rightScore = activeWindow.theme[right] ?? 0;
        const leftScore = activeWindow.theme[left] ?? 0;

        if (rightScore !== leftScore) {
          return rightScore - leftScore;
        }

        return THEME_ORDER.indexOf(left) - THEME_ORDER.indexOf(right);
      }),
    [activeWindow.theme]
  );

  return (
    <section className="panel" aria-labelledby="theme-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Life themes</p>
          <h2 id="theme-title">What keeps appearing</h2>
        </div>
      </div>

      <div className="theme-list">
        {orderedThemes.map((category) => {
          const theme = THEMES[category];
          const score = activeWindow.theme?.[category] ?? 0;
          const baseline = comparisonWindow.theme?.[category] ?? 0;
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
