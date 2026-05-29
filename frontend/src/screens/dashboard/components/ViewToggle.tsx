import type { WindowScores } from '../../../types';

type ViewMode = 'state' | 'trait';

interface ViewToggleProps {
  value: ViewMode;
  onChange: (value: ViewMode) => void;
  stateWindow: WindowScores;
  traitWindow: WindowScores;
}

function formatDateRange(from?: string, to?: string): string {
  if (!from || !to) return '';
  const fmt = (iso: string) => {
    const d = new Date(iso + 'T00:00:00Z');
    return d.toLocaleDateString('en-GB', { month: 'short', year: 'numeric', timeZone: 'UTC' });
  };
  const f = fmt(from);
  const t = fmt(to);
  if (f === t) return f;
  // If same year, drop the year from the first part
  const fromYear = from.slice(0, 4);
  const toYear = to.slice(0, 4);
  if (fromYear === toYear) {
    const fMonth = new Date(from + 'T00:00:00Z').toLocaleDateString('en-GB', { month: 'short', timeZone: 'UTC' });
    const tMonth = new Date(to + 'T00:00:00Z').toLocaleDateString('en-GB', { month: 'short', year: 'numeric', timeZone: 'UTC' });
    return `${fMonth}–${tMonth}`;
  }
  return `${f}–${t}`;
}

export function ViewToggle({ value, onChange, stateWindow, traitWindow }: ViewToggleProps) {
  const stateRange = formatDateRange(stateWindow.from_date, stateWindow.to_date);
  const traitRange = formatDateRange(traitWindow.from_date, traitWindow.to_date);

  return (
    <section className="view-toggle" aria-label="Report window">
      <button className={value === 'state' ? 'active' : ''} type="button" onClick={() => onChange('state')}>
        Recent window
        {stateRange && <span className="view-toggle-range">{stateRange}</span>}
      </button>
      <button className={value === 'trait' ? 'active' : ''} type="button" onClick={() => onChange('trait')}>
        Usual pattern
        {traitRange && <span className="view-toggle-range">{traitRange}</span>}
      </button>
      <span>{value === 'state' ? 'Last listening window' : 'Longer-range baseline'}</span>
    </section>
  );
}
