type ViewMode = 'state' | 'trait';

interface ViewToggleProps {
  value: ViewMode;
  onChange: (value: ViewMode) => void;
}

export function ViewToggle({ value, onChange }: ViewToggleProps) {
  return (
    <section className="view-toggle" aria-label="Report window">
      <button className={value === 'state' ? 'active' : ''} type="button" onClick={() => onChange('state')}>
        Recent window
      </button>
      <button className={value === 'trait' ? 'active' : ''} type="button" onClick={() => onChange('trait')}>
        Usual pattern
      </button>
      <span>{value === 'state' ? 'Last listening window' : 'Longer-range baseline'}</span>
    </section>
  );
}
