import { categoryLabel, EMOTIONS, THEMES } from '../taxonomy';
import { moodColorRGBA } from '../lib/moodColor';
import type { Track } from '../types';

interface EvidenceTracksProps {
  tracks: Track[];
}

export function EvidenceTracks({ tracks }: EvidenceTracksProps) {
  return (
    <section className="panel wide-panel" aria-labelledby="track-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Listening evidence</p>
          <h2 id="track-title">Primary tracks</h2>
        </div>
      </div>

      {tracks.length === 0 ? (
        <p className="muted-copy">No primary tracks were attached to this report.</p>
      ) : (
        <div className="track-grid-bento">
          {tracks.map((track, index) => (
            <article className="track-card-ranked" key={track.uri}>
              <div className="track-rank">{index + 1}</div>
              <div className="track-content">
                <h3 className="track-title">{track.name || track.uri}</h3>
                {(track.artist || track.album) && (
                  <p className="track-attribution">
                    {[track.artist, track.album].filter(Boolean).join(' — ')}
                  </p>
                )}
                <div className="track-footer">
                  {track.play_count && <span className="track-stat">{track.play_count} plays</span>}
                  {!track.play_count && typeof track.weight === 'number' && (
                    <span className="track-stat">Weight {track.weight.toFixed(2)}</span>
                  )}
                </div>
                <div className="track-badges">
                  <div className="track-emotions">
                    {Object.entries(track.emotion_scores ?? {})
                      .sort(([, a], [, b]) => (b ?? 0) - (a ?? 0))
                      .slice(0, 1)
                      .map(([category, score]) => {
                        const short = (EMOTIONS as Record<string, any>)[category]?.short || (THEMES as Record<string, any>)[category]?.short || categoryLabel(category as never);
                        const { background, border, color } = moodColorRGBA(
                          (EMOTIONS as Record<string, any>)[category]?.valence ?? 0,
                          (EMOTIONS as Record<string, any>)[category]?.arousal ?? 0,
                          0.18
                        );
                        return (
                          <span
                            className="track-emotion-chip"
                            key={category}
                            title={categoryLabel(category as never)}
                            style={{ background, borderColor: border, color }}
                          >
                            {short} {((score ?? 0) * 100).toFixed(0)}%
                          </span>
                        );
                      })}
                  </div>
                  <div className="track-themes">
                    {Object.entries(track.theme_scores ?? {})
                      .sort(([, a], [, b]) => (b ?? 0) - (a ?? 0))
                      .slice(0, 1)
                      .map(([category, score]) => {
                        const short = (THEMES as Record<string, any>)[category]?.short || (EMOTIONS as Record<string, any>)[category]?.short || categoryLabel(category as never);
                        const { background, border, color } = moodColorRGBA(
                          (THEMES as Record<string, any>)[category]?.valence ?? 0,
                          (THEMES as Record<string, any>)[category]?.arousal ?? 0,
                          0.12
                        );
                        return (
                          <span
                            className="track-theme-chip"
                            key={category}
                            title={`${categoryLabel(category as never)} — val:${((THEMES as Record<string, any>)[category]?.valence ?? 0).toFixed(2)}, ar:${((THEMES as Record<string, any>)[category]?.arousal ?? 0).toFixed(2)}`}
                            style={{ background, borderColor: border, color }}
                          >
                            {short} {((score ?? 0) * 100).toFixed(0)}%
                          </span>
                        );
                      })}
                  </div>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
