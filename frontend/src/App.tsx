import { useState } from 'react';
import { Dashboard } from './components/Dashboard';
import { UploadPanel } from './components/UploadPanel';
import { sampleReport } from './data/sampleReport';
import { parseOrpheusReport } from './lib/reportParser';
import type { OrpheusReport } from './types';

export function App() {
  const [report, setReport] = useState<OrpheusReport | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  async function handleFile(file: File) {
    try {
      const text = await file.text();
      const json = JSON.parse(text);
      setReport(parseOrpheusReport(json));
      setUploadError(null);
    } catch {
      setUploadError('This file is not a valid Orpheus JSON report.');
    }
  }

  if (!report) {
    return <UploadPanel error={uploadError} onFile={handleFile} onDemo={() => setReport(sampleReport)} />;
  }

  return <Dashboard report={report} onReset={() => setReport(null)} />;
}
