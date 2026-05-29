import { CalendarClock, Download, RotateCcw, PlusSquare } from 'lucide-react';
import { categoryLabel } from '../taxonomy';
import type { OrpheusReport } from '../types';

interface HeroSummaryProps {
  report: OrpheusReport;
  onExport: () => void;
  onReset: () => void;
  onAddData?: () => void;
}

export function HeroSummary({ report, onExport, onReset, onAddData }: HeroSummaryProps) {
  const topEmotion = report.state.top_emotions[0]?.category;
  const topTheme = report.state.top_themes[0]?.category;
  const headline =
    report.narrative?.headline ??
    `Your recent listening circles around ${topEmotion ? categoryLabel(topEmotion) : 'a dominant feeling'} and ${
      topTheme ? categoryLabel(topTheme) : 'a recurring theme'
    }.`;
  const insights = report.narrative?.key_insights ?? report.shifts.map((shift) => shift.narrative).slice(0, 3);

  return (
    <header className="hero-summary">
      <div className="hero-actions">
        {onAddData && (
          <button type="button" onClick={onAddData} className="accent">
            <PlusSquare size={16} />
            Add data
          </button>
        )}
        <button type="button" onClick={onExport}>
          <Download size={16} />
          Download report
        </button>
        <button type="button" onClick={onReset}>
          <RotateCcw size={16} />
          Back to profiles
        </button>
      </div>
      <p className="eyebrow">Project Orpheus</p>
      <h1>{headline}</h1>
      <div className="metadata-line">
        <CalendarClock size={15} />
        <span>Generated {new Date(report.metadata.generated_at).toLocaleString()}</span>
        <span>{report.metadata.model_version}</span>
      </div>
      <ul className="insight-list">
        {insights.map((insight, index) => (
          <li key={`${insight}-${index}`}>{insight}</li>
        ))}
      </ul>
      {report.narrative?.caveats && <p className="caveat">{report.narrative.caveats.join(' ')}</p>}
    </header>
  );
}
