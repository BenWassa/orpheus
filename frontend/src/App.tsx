import { useEffect, useState } from 'react';
import { Dashboard } from './components/Dashboard';
import { UploadPanel } from './components/UploadPanel';
import { ProfileSelectionView } from './components/ProfileSelectionView';
import { sampleReport } from './data/sampleReport';
import { parseOrpheusReport } from './lib/reportParser';
import type { OrpheusReport, ProfileInfo } from './types';

type AppView =
  | { tag: 'profiles'; profiles: ProfileInfo[]; loadError: string | null }
  | { tag: 'profile'; profile: ProfileInfo; report: OrpheusReport; reloadError: string | null }
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
          setView({ tag: 'profiles', profiles, loadError: null });
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

    // Clear any previous load error on the profiles view
    setView((prev) => prev.tag === 'profiles' ? { ...prev, loadError: null } : prev);

    try {
      const response = await fetch(`/api/reports/latest?profile=${encodeURIComponent(profile.name)}`);
      if (!response.ok) throw new Error('Failed to load profile report');

      const json = await response.json();
      setView({ tag: 'profile', profile, report: parseOrpheusReport(json), reloadError: null });
    } catch {
      setView((prev) =>
        prev.tag === 'profiles'
          ? { ...prev, loadError: `Could not load "${profile.name}". Check that the pipeline has run and try again.` }
          : prev,
      );
    } finally {
      setLoadingProfile(null);
    }
  }

  async function handleReloadReport(profile: ProfileInfo) {
    // Clear prior error
    setView((prev) => prev.tag === 'profile' ? { ...prev, reloadError: null } : prev);

    try {
      const response = await fetch(`/api/reports/latest?profile=${encodeURIComponent(profile.name)}`);
      if (!response.ok) throw new Error('Failed to reload report');

      const json = await response.json();
      setView({ tag: 'profile', profile, report: parseOrpheusReport(json), reloadError: null });
    } catch {
      setView((prev) =>
        prev.tag === 'profile'
          ? { ...prev, reloadError: 'Could not reload the report. Run the pipeline again and retry.' }
          : prev,
      );
    }
  }

  async function handleReset() {
    try {
      const response = await fetch('/api/profiles');
      if (response.ok) {
        const profiles: ProfileInfo[] = await response.json();
        if (profiles.length > 0) {
          setView({ tag: 'profiles', profiles, loadError: null });
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
      const dummyProfile: ProfileInfo = { name: 'Local File', reportCount: 1, latestReportAt: null };
      setView({ tag: 'profile', profile: dummyProfile, report: parseOrpheusReport(json), reloadError: null });
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
        loadError={view.loadError}
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
        reloadError={view.reloadError}
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
          reloadError: null,
        })
      }
    />
  );
}
