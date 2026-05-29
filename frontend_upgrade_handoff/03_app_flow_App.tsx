import { useEffect, useState } from 'react';
import { DashboardScreen } from '../screens/dashboard/DashboardScreen';
import { ProfileSelectionScreen } from '../screens/profiles/ProfileSelectionScreen';
import { loadLatestReport, loadProfiles } from '../services/reportService';
import type { OrpheusReport, ProfileInfo } from '../types';

type AppView =
  | { tag: 'loading' }
  | { tag: 'profiles'; profiles: ProfileInfo[]; loadError: string | null }
  | { tag: 'profile'; profile: ProfileInfo; report: OrpheusReport; reloadError: string | null };

export function App() {
  const [view, setView] = useState<AppView>({ tag: 'loading' });
  const [loadingProfile, setLoadingProfile] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    async function loadAvailableProfiles() {
      try {
        const profiles = await loadProfiles(controller.signal);
        setView({ tag: 'profiles', profiles, loadError: null });
      } catch (error) {
        if (!controller.signal.aborted) {
          console.info('Orpheus profiles were not auto-loaded.', error);
          setView({
            tag: 'profiles',
            profiles: [],
            loadError: 'Could not load profiles. Run the local server and try again.',
          });
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
    setView({ tag: 'profiles', profiles: [], loadError: null });
  }

  if (view.tag === 'loading' || view.tag === 'profiles') {
    return (
      <ProfileSelectionScreen
        profiles={view.tag === 'profiles' ? view.profiles : []}
        onSelect={handleProfileSelect}
        loadingProfile={loadingProfile}
        loadError={view.tag === 'profiles' ? view.loadError : null}
        isLoadingProfiles={view.tag === 'loading'}
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

  return null;
}
