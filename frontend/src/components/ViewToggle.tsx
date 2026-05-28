type ViewMode = 'state' | 'trait';

interface ViewToggleProps {
  value: ViewMode;
  onChange: (value: ViewMode) => void;
}

export function ViewToggle({ value, onChange }: ViewToggleProps) {
  return (
    <section className="view-toggle" aria-label="Report window">
      <button className={value === 'state' ? 'active' : ''} type="button" onClick={() => onChange('state')}>
        Current state
      </button>
      <button className={value === 'trait' ? 'active' : ''} type="button" onClick={() => onChange('trait')}>
        Baseline trait
      </button>
      <span>{value === 'state' ? 'Recent and contextual' : 'Longer-range pattern'}</span>
    </section>
  );
}
