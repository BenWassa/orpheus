import { useEffect, useState } from 'react';
import { sampleReport } from '../data/sampleReport';
import { DashboardScreen } from '../screens/dashboard/DashboardScreen';
import { ProfileSelectionScreen } from '../screens/profiles/ProfileSelectionScreen';
import { UploadScreen } from '../screens/upload/UploadScreen';
import { loadLatestReport, loadProfiles, parseLocalReportFile } from '../services/reportService';
import type { OrpheusReport, ProfileInfo } from '../types';

type AppView =
  | { tag: 'profiles'; profiles: ProfileInfo[]; loadError: string | null }
  | { tag: 'profile'; profile: ProfileInfo; report: OrpheusReport; reloadError: string | null }
  | { tag: 'upload'; error: string | null };

export function App() {
  const [view, setView] = useState<AppView>({ tag: 'upload', error: null });
  const [loadingProfile, setLoadingProfile] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    async function loadAvailableProfiles() {
      try {
        const profiles = await loadProfiles(controller.signal);
        if (profiles.length > 0) {
          setView({ tag: 'profiles', profiles, loadError: null });
        }
      } catch (error) {
        if (!controller.signal.aborted) {
          console.info('Orpheus profiles were not auto-loaded.', error);
        }
      }
    }

    loadAvailableProfiles();
    return () => controller.abort();
  }, []);

  async function handleProfileSelect(profile: ProfileInfo) {
    setLoadingProfile(profile.name);

    // Clear any previous load error on the profiles view
    setView((prev) => prev.tag === 'profiles' ? { ...prev, loadError: null } : prev);

    try {
      const report = await loadLatestReport(profile.name);
      setView({ tag: 'profile', profile, report, reloadError: null });
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
      const report = await loadLatestReport(profile.name);
      setView({ tag: 'profile', profile, report, reloadError: null });
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
      const profiles = await loadProfiles();
      if (profiles.length > 0) {
        setView({ tag: 'profiles', profiles, loadError: null });
        return;
      }
    } catch (e) {
      console.info('Failed to refresh profiles on reset', e);
    }
    setView({ tag: 'upload', error: null });
  }

  async function handleFile(file: File) {
    try {
      const report = await parseLocalReportFile(file);
      const dummyProfile: ProfileInfo = { name: 'Local File', reportCount: 1, latestReportAt: null };
      setView({ tag: 'profile', profile: dummyProfile, report, reloadError: null });
    } catch {
      setView({ tag: 'upload', error: 'This file is not a valid Orpheus JSON report.' });
    }
  }

  if (view.tag === 'profiles') {
    return (
      <ProfileSelectionScreen
        profiles={view.profiles}
        onSelect={handleProfileSelect}
        loadingProfile={loadingProfile}
        loadError={view.loadError}
      />
    );
  }

  if (view.tag === 'profile') {
    return (
      <DashboardScreen
        report={view.report}
        profileName={view.profile.name}
        onReset={handleReset}
        onReload={() => handleReloadReport(view.profile)}
        reloadError={view.reloadError}
      />
    );
  }

  return (
    <UploadScreen
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
