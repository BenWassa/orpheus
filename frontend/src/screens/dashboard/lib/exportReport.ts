import type { OrpheusReport } from '../../../types';

export function exportReport(report: OrpheusReport) {
  const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');

  anchor.href = url;
  anchor.download = `orpheus_report_${report.metadata.generated_at.split('T')[0]}.json`;
  anchor.click();
  URL.revokeObjectURL(url);
}
