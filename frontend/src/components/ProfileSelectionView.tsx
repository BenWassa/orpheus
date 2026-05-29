import { Music2, Plus, AlertCircle } from 'lucide-react';
import type { ProfileInfo } from '../types';
import { ProfileCard } from './ProfileCard';

interface ProfileSelectionViewProps {
  profiles: ProfileInfo[];
  onSelect: (profile: ProfileInfo) => void;
  loadingProfile: string | null;
  loadError: string | null;
}

export function ProfileSelectionView({ profiles, onSelect, loadingProfile, loadError }: ProfileSelectionViewProps) {
  return (
    <main className="profiles-shell">
      <header className="brand-header">
        <div className="brand-mark" aria-hidden="true">
          <Music2 size={32} />
        </div>
        <div className="brand-copy">
          <p className="eyebrow">Project Orpheus</p>
          <h1>Listening Profiles</h1>
          <p>Select a profile to explore its latest reports.</p>
        </div>
      </header>

      {loadError && (
        <div className="inline-error" role="alert" aria-live="polite">
          <AlertCircle size={16} aria-hidden="true" />
          <span>{loadError}</span>
        </div>
      )}

      <div className="profile-grid">
        {profiles.map((profile) => (
          <ProfileCard
            key={profile.name}
            profile={profile}
            isLoading={loadingProfile === profile.name}
            onSelect={() => onSelect(profile)}
          />
        ))}

        <div className="profile-card new-profile">
          <div className="profile-icon" aria-hidden="true">
            <Plus size={24} />
          </div>
          <div className="profile-info">
            <h3>New profile</h3>
            <p className="instruction">
              Run <code>orpheus run-all --profile &lt;name&gt;</code> in your terminal to create a new profile.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
