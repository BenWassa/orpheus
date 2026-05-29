import { categoryLabel } from '../taxonomy';
import type { Track } from '../types';

interface EvidenceTracksProps {
  tracks: Track[];
}

export function EvidenceTracks({ tracks }: EvidenceTracksProps) {
  if (tracks.length === 0) return null;

  return (
    <section className="panel wide-panel" aria-labelledby="track-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Optional evidence</p>
          <h2 id="track-title">Primary tracks</h2>
        </div>
      </div>

      <div className="track-grid">
        {tracks.map((track) => (
          <article className="track-card" key={track.uri}>
            <span className="track-depth">{track.depth_label ?? 'track'}</span>
            <h3>{track.name ?? track.uri}</h3>
            <p>
              {[track.artist, track.album].filter(Boolean).join(', ') || track.uri}
            </p>
            {track.play_count && <small>{track.play_count} plays in this window</small>}
            {!track.play_count && typeof track.weight === 'number' && <small>Window weight {track.weight.toFixed(2)}</small>}
            <div className="chip-stack">
              {Object.entries(track.emotion_scores ?? {})
                .slice(0, 3)
                .map(([category, score]) => (
                  <span className="chip" key={category}>
                    {categoryLabel(category as never)} {((score ?? 0) * 100).toFixed(0)}%
                  </span>
                ))}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
