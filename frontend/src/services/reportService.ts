import { parseOrpheusReport } from '../lib/reportParser';
import type { OrpheusReport, ProfileInfo } from '../types';

export async function loadProfiles(signal?: AbortSignal): Promise<ProfileInfo[]> {
  const response = await fetch('/api/profiles', signal ? { signal } : undefined);
  if (!response.ok) return [];
  return response.json();
}

export async function loadLatestReport(profileName: string): Promise<OrpheusReport> {
  const response = await fetch(`/api/reports/latest?profile=${encodeURIComponent(profileName)}`);
  if (!response.ok) throw new Error('Failed to load profile report');

  const json = await response.json();
  return parseOrpheusReport(json);
}

export async function parseLocalReportFile(file: File): Promise<OrpheusReport> {
  const text = await file.text();
  const json = JSON.parse(text);
  return parseOrpheusReport(json);
}
