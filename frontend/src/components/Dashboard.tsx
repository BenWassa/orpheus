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
import type { EmotionCategory, OrpheusReport, ThemeCategory } from '../types';

interface DashboardProps {
  report: OrpheusReport;
  onReset: () => void;
}

type ViewMode = 'state' | 'trait';

export function Dashboard({ report, onReset }: DashboardProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('state');
  const [selectedEmotion, setSelectedEmotion] = useState<EmotionCategory | null>(null);
  const [selectedTheme, setSelectedTheme] = useState<ThemeCategory | null>(null);
  const [selectedCluster, setSelectedCluster] = useState<number | null>(null);
  const [selectedPair, setSelectedPair] = useState<{ emotion: EmotionCategory; theme: ThemeCategory } | null>(null);

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

  return (
    <main className="app-shell">
      <SafetyFlags flags={report.safety_flags} />
      <HeroSummary report={report} onExport={exportReport} onReset={onReset} />
      <ViewToggle value={viewMode} onChange={setViewMode} />

      <div className="dashboard-grid">
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
        <CoOccurrenceMatrix report={report} selected={selectedPair} onSelect={setSelectedPair} />
        <TrendEvents trends={report.trends} />
        <ClusterList
          clusters={report.clusters}
          status={report.clusters_status}
          selected={selectedCluster}
          onSelect={setSelectedCluster}
        />
        <EvidenceTracks tracks={tracks} />
      </div>
    </main>
  );
}
