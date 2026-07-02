export type DetailView = 'connections' | 'movement' | 'loops' | 'tracks' | 'frequency';

// `window` views re-render against the active Recent/Usual window. `global`
// views are computed across all listening (or a fixed lookback) and do NOT
// respond to the window toggle — we say so explicitly so the toggle doesn't
// silently appear to do nothing here. `scopeNote` is the rendered caveat.
export type DetailScope = 'window' | 'global';

export const DETAIL_VIEWS: Array<{
  id: DetailView;
  label: string;
  scope: DetailScope;
  scopeNote?: string;
}> = [
  { id: 'connections', label: 'Connections', scope: 'window' },
  {
    id: 'movement',
    label: 'Movement',
    scope: 'global',
    scopeNote: "Across the last 12 weeks — the Recent / Usual toggle doesn't change this view.",
  },
  {
    id: 'loops',
    label: 'Loops',
    scope: 'global',
    scopeNote: "Across all your listening — the Recent / Usual toggle doesn't change this view.",
  },
  { id: 'tracks', label: 'Influence', scope: 'window' },
  { id: 'frequency', label: 'Frequency', scope: 'window' },
];

export function detailViewForKey(key: string, currentView: DetailView): DetailView | null {
  const idx = DETAIL_VIEWS.findIndex((view) => view.id === currentView);

  if (key === 'ArrowRight') return DETAIL_VIEWS[(idx + 1) % DETAIL_VIEWS.length].id;
  if (key === 'ArrowLeft') return DETAIL_VIEWS[(idx - 1 + DETAIL_VIEWS.length) % DETAIL_VIEWS.length].id;
  if (key === 'Home') return DETAIL_VIEWS[0].id;
  if (key === 'End') return DETAIL_VIEWS[DETAIL_VIEWS.length - 1].id;

  return null;
}
