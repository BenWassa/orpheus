import { Music2, Clock, BarChart3, Loader2 } from 'lucide-react';
import type { ProfileInfo } from '../../../types';

interface ProfileCardProps {
  profile: ProfileInfo;
  isLoading: boolean;
  onSelect: () => void;
}

export function ProfileCard({ profile, isLoading, onSelect }: ProfileCardProps) {
  const formatDate = (at: string | null) => {
    if (!at) return 'Never';
    // Format "20260529T004730" to friendly date
    const y = at.substring(0, 4);
    const m = at.substring(4, 6);
    const d = at.substring(6, 8);
    const date = new Date(`${y}-${m}-${d}`);
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <button
      className={`profile-card ${isLoading ? 'is-loading' : ''}`}
      onClick={onSelect}
      disabled={isLoading}
      aria-busy={isLoading}
    >
      <div className="profile-icon" aria-hidden="true">
        {isLoading ? <Loader2 className="animate-spin" size={24} /> : <Music2 size={24} />}
      </div>
      <div className="profile-info">
        <h3>{profile.name}</h3>
        <div className="profile-stats">
          <span title="Report count">
            <BarChart3 size={14} />
            {profile.reportCount} {profile.reportCount === 1 ? 'report' : 'reports'}
          </span>
          <span title="Last updated">
            <Clock size={14} />
            {formatDate(profile.latestReportAt)}
          </span>
        </div>
      </div>
    </button>
  );
}
