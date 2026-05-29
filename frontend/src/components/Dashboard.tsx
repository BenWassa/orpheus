import { useMemo, useState } from 'react';
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
}

type ViewMode = 'state' | 'trait';
type DetailView = 'connections' | 'movement' | 'loops' | 'tracks';

const DETAIL_VIEWS: Array<{ id: DetailView; label: string }> = [
  { id: 'connections', label: 'Connections' },
  { id: 'movement', label: 'Movement' },
  { id: 'loops', label: 'Loops' },
  { id: 'tracks', label: 'Tracks' },
];

export function Dashboard({ report, onReset, profileName, onReload }: DashboardProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('state');
  const [detailView, setDetailView] = useState<DetailView>('connections');
  const [selectedEmotion, setSelectedEmotion] = useState<EmotionCategory | null>(null);
  const [selectedTheme, setSelectedTheme] = useState<ThemeCategory | null>(null);
  const [selectedCluster, setSelectedCluster] = useState<number | null>(null);
  const [selectedPair, setSelectedPair] = useState<{ emotion: EmotionCategory; theme: ThemeCategory } | null>(null);
  const [showAddData, setShowAddData] = useState(false);

  const activeWindow = viewMode === 'state' ? report.state : report.trait;
  const comparisonWindow = viewMode === 'state' ? report.trait : report.state;
  const tracks = useMemo(() => activeWindow.top_tracks, [activeWindow.top_tracks]);

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

  return (
    <main className="app-shell">
      {showAddData && profileName && (
        <AddDataPanel
          profileName={profileName}
          onReload={handleReload}
          onClose={() => setShowAddData(false)}
        />
      )}
      <SafetyFlags flags={report.safety_flags} />
      <HeroSummary
        report={report}
        onExport={exportReport}
        onReset={onReset}
        onAddData={profileName ? () => setShowAddData(true) : undefined}
      />
      <ViewToggle value={viewMode} onChange={setViewMode} />

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

        <div className="detail-tabs" role="tablist" aria-label="Evidence view">
          {DETAIL_VIEWS.map((item) => (
            <button
              aria-selected={detailView === item.id}
              className={detailView === item.id ? 'active' : ''}
              key={item.id}
              onClick={() => setDetailView(item.id)}
              role="tab"
              type="button"
            >
              {item.label}
            </button>
          ))}
        </div>

        <div className="detail-stage">
          {detailView === 'connections' && (
            <CoOccurrenceMatrix report={report} selected={selectedPair} onSelect={setSelectedPair} />
          )}
          {detailView === 'movement' && <TrendEvents trends={report.trends} />}
          {detailView === 'loops' && (
            <ClusterList
              clusters={report.clusters}
              status={report.clusters_status}
              selected={selectedCluster}
              onSelect={setSelectedCluster}
            />
          )}
          {detailView === 'tracks' && <EvidenceTracks tracks={tracks} />}
        </div>
      </section>
    </main>
  );
}
