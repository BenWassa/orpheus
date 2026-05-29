import { useMemo, useRef, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { ClusterList } from './ClusterList';
import { CoOccurrenceMatrix } from './CoOccurrenceMatrix';
import { EmotionMap } from './EmotionMap';
import { EvidenceTracks } from './EvidenceTracks';
import { HeroSummary } from './HeroSummary';
import { SafetyFlags } from './SafetyFlags';
import { ThemePanel } from './ThemePanel';
import { TrendEvents } from './TrendEvents';
import { ViewToggle } from './ViewToggle';
import { AddDataPanel } from './AddDataPanel';
import type { EmotionCategory, OrpheusReport, ThemeCategory } from '../types';

interface DashboardProps {
  report: OrpheusReport;
  onReset: () => void;
  profileName?: string;
  onReload?: () => void;
  reloadError?: string | null;
}

type ViewMode = 'state' | 'trait';
type DetailView = 'connections' | 'movement' | 'loops' | 'tracks' | 'frequency';

const DETAIL_VIEWS: Array<{ id: DetailView; label: string }> = [
  { id: 'connections', label: 'Connections' },
  { id: 'movement', label: 'Movement' },
  { id: 'loops', label: 'Loops' },
  { id: 'tracks', label: 'Influence' },
  { id: 'frequency', label: 'Frequency' },
];

export function Dashboard({ report, onReset, profileName, onReload, reloadError }: DashboardProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('state');
  const [detailView, setDetailView] = useState<DetailView>('connections');
  const [selectedEmotion, setSelectedEmotion] = useState<EmotionCategory | null>(null);
  const [selectedTheme, setSelectedTheme] = useState<ThemeCategory | null>(null);
  const [selectedCluster, setSelectedCluster] = useState<number | null>(null);
  const [selectedPair, setSelectedPair] = useState<{ emotion: EmotionCategory; theme: ThemeCategory } | null>(null);
  const [showAddData, setShowAddData] = useState(false);

  // Ref to the "Add data" trigger so we can restore focus when the dialog closes
  const addDataTriggerRef = useRef<HTMLButtonElement>(null);

  const activeWindow = viewMode === 'state' ? report.state : report.trait;
  const comparisonWindow = viewMode === 'state' ? report.trait : report.state;
  const tracks = useMemo(() => activeWindow.top_tracks, [activeWindow.top_tracks]);
  const frequencyTracks = useMemo(
    () => activeWindow.top_frequency_tracks,
    [activeWindow.top_frequency_tracks]
  );

  function exportReport() {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `orpheus_report_${report.metadata.generated_at.split('T')[0]}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function handleReload() {
    setShowAddData(false);
    onReload?.();
  }

  function handleCloseAddData() {
    setShowAddData(false);
    // Return focus to the trigger that opened the dialog
    addDataTriggerRef.current?.focus();
  }

  function handleTabKeyDown(e: React.KeyboardEvent<HTMLDivElement>) {
    const idx = DETAIL_VIEWS.findIndex((v) => v.id === detailView);
    if (e.key === 'ArrowRight') {
      e.preventDefault();
      const next = DETAIL_VIEWS[(idx + 1) % DETAIL_VIEWS.length];
      setDetailView(next.id);
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      const prev = DETAIL_VIEWS[(idx - 1 + DETAIL_VIEWS.length) % DETAIL_VIEWS.length];
      setDetailView(prev.id);
    } else if (e.key === 'Home') {
      e.preventDefault();
      setDetailView(DETAIL_VIEWS[0].id);
    } else if (e.key === 'End') {
      e.preventDefault();
      setDetailView(DETAIL_VIEWS[DETAIL_VIEWS.length - 1].id);
    }
  }

  return (
    <main className="app-shell">
      {showAddData && profileName && (
        <AddDataPanel
          profileName={profileName}
          onReload={handleReload}
          onClose={handleCloseAddData}
        />
      )}
      {reloadError && (
        <div className="inline-error" role="alert" aria-live="polite">
          <AlertCircle size={16} aria-hidden="true" />
          <span>{reloadError}</span>
        </div>
      )}
      <SafetyFlags flags={report.safety_flags} />
      <HeroSummary
        report={report}
        onExport={exportReport}
        onReset={onReset}
        onAddData={profileName ? () => setShowAddData(true) : undefined}
        addDataTriggerRef={profileName ? addDataTriggerRef : undefined}
      />
      <ViewToggle value={viewMode} onChange={setViewMode} stateWindow={report.state} traitWindow={report.trait} />

      <div className="reader-layout">
        <EmotionMap
          report={report}
          activeWindow={activeWindow}
          comparisonWindow={comparisonWindow}
          selected={selectedEmotion}
          onSelect={setSelectedEmotion}
        />
        <ThemePanel
          activeWindow={activeWindow}
          comparisonWindow={comparisonWindow}
          selected={selectedTheme}
          onSelect={setSelectedTheme}
        />
      </div>

      <section className="evidence-section" aria-labelledby="evidence-title">
        <div className="section-heading evidence-heading">
          <div>
            <p className="eyebrow">Deeper evidence</p>
            <h2 id="evidence-title">Look closer</h2>
          </div>
        </div>

        <div
          className="detail-tabs"
          role="tablist"
          aria-label="Evidence view"
          onKeyDown={handleTabKeyDown}
        >
          {DETAIL_VIEWS.map((item) => (
            <button
              aria-controls={`tabpanel-${item.id}`}
              aria-selected={detailView === item.id}
              className={detailView === item.id ? 'active' : ''}
              id={`tab-${item.id}`}
              key={item.id}
              onClick={() => setDetailView(item.id)}
              role="tab"
              tabIndex={detailView === item.id ? 0 : -1}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </div>

        <div className="detail-stage">
          {DETAIL_VIEWS.map((item) => (
            <div
              key={item.id}
              id={`tabpanel-${item.id}`}
              role="tabpanel"
              aria-labelledby={`tab-${item.id}`}
              hidden={detailView !== item.id}
            >
              {item.id === 'connections' && detailView === 'connections' && (
                <CoOccurrenceMatrix report={report} selected={selectedPair} onSelect={setSelectedPair} />
              )}
              {item.id === 'movement' && detailView === 'movement' && (
                <TrendEvents trends={report.trends} />
              )}
              {item.id === 'loops' && detailView === 'loops' && (
                <ClusterList
                  clusters={report.clusters}
                  status={report.clusters_status}
                  selected={selectedCluster}
                  onSelect={setSelectedCluster}
                />
              )}
              {item.id === 'tracks' && detailView === 'tracks' && (
                <EvidenceTracks tracks={tracks} />
              )}
              {item.id === 'frequency' && detailView === 'frequency' && (
                <EvidenceTracks tracks={frequencyTracks} variant="frequency" />
              )}
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
