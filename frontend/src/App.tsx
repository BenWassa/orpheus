import { useEffect, useState } from 'react';
import { Dashboard } from './components/Dashboard';
import { UploadPanel } from './components/UploadPanel';
import { ProfileSelectionView } from './components/ProfileSelectionView';
import { sampleReport } from './data/sampleReport';
import { parseOrpheusReport } from './lib/reportParser';
import type { OrpheusReport, ProfileInfo } from './types';

type AppView =
  | { tag: 'profiles'; profiles: ProfileInfo[] }
  | { tag: 'profile'; profile: ProfileInfo; report: OrpheusReport }
  | { tag: 'upload'; error: string | null };

export function App() {
  const [view, setView] = useState<AppView>({ tag: 'upload', error: null });
  const [loadingProfile, setLoadingProfile] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    async function loadProfiles() {
      try {
        const response = await fetch('/api/profiles', { signal: controller.signal });
        if (!response.ok) return;

        const profiles: ProfileInfo[] = await response.json();
        if (profiles.length > 0) {
          setView({ tag: 'profiles', profiles });
        }
      } catch (error) {
        if (!controller.signal.aborted) {
          console.info('Orpheus profiles were not auto-loaded.', error);
        }
      }
    }

    loadProfiles();
    return () => controller.abort();
  }, []);

  async function handleProfileSelect(profile: ProfileInfo) {
    setLoadingProfile(profile.name);
    try {
      const response = await fetch(`/api/reports/latest?profile=${encodeURIComponent(profile.name)}`);
      if (!response.ok) throw new Error('Failed to load profile report');

      const json = await response.json();
      setView({ tag: 'profile', profile, report: parseOrpheusReport(json) });
    } catch (error) {
      console.error('Error loading latest report for profile:', error);
    } finally {
      setLoadingProfile(null);
    }
  }

  async function handleReloadReport(profile: ProfileInfo) {
    try {
      const response = await fetch(`/api/reports/latest?profile=${encodeURIComponent(profile.name)}`);
      if (!response.ok) throw new Error('Failed to reload report');

      const json = await response.json();
      setView({ tag: 'profile', profile, report: parseOrpheusReport(json) });
    } catch (error) {
      console.error('Error reloading report:', error);
    }
  }

  async function handleReset() {
    // Re-fetch profiles to ensure we have current counts/dates
    try {
      const response = await fetch('/api/profiles');
      if (response.ok) {
        const profiles: ProfileInfo[] = await response.json();
        if (profiles.length > 0) {
          setView({ tag: 'profiles', profiles });
          return;
        }
      }
    } catch (e) {
      console.info('Failed to refresh profiles on reset', e);
    }
    setView({ tag: 'upload', error: null });
  }

  async function handleFile(file: File) {
    try {
      const text = await file.text();
      const json = JSON.parse(text);
      // Dummy profile for manually uploaded files
      const dummyProfile: ProfileInfo = { name: 'Local File', reportCount: 1, latestReportAt: null };
      setView({ tag: 'profile', profile: dummyProfile, report: parseOrpheusReport(json) });
    } catch {
      setView({ tag: 'upload', error: 'This file is not a valid Orpheus JSON report.' });
    }
  }

  if (view.tag === 'profiles') {
    return (
      <ProfileSelectionView
        profiles={view.profiles}
        onSelect={handleProfileSelect}
        loadingProfile={loadingProfile}
      />
    );
  }

  if (view.tag === 'profile') {
    return (
      <Dashboard
        report={view.report}
        profileName={view.profile.name}
        onReset={handleReset}
        onReload={() => handleReloadReport(view.profile)}
      />
    );
  }

  return (
    <UploadPanel
      error={view.error}
      onFile={handleFile}
      onDemo={() =>
        setView({
          tag: 'profile',
          profile: { name: 'Demo', reportCount: 1, latestReportAt: null },
          report: sampleReport,
        })
      }
    />
  );
}
