import { categoryColor, categoryLabel } from '../../../taxonomy';
import type { ClusterSummary } from '../../../types';

interface ClusterListProps {
  clusters: ClusterSummary[];
  status?: string;
  selected: number | null;
  onSelect: (index: number | null) => void;
}

function clusterStatusCopy(status?: string) {
  if (status === 'no_audio_features') return 'This report does not include the audio details needed to find loops yet.';
  if (status === 'insufficient_audio_data') return 'There was not enough listening detail to form stable loops.';
  if (status === 'no_clusters_found') return 'No stable listening loops stood out in this report.';
  return 'No listening loops were included in this report.';
}

export function ClusterList({ clusters, status, selected, onSelect }: ClusterListProps) {
  return (
    <section className="panel" aria-labelledby="cluster-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Detected loops</p>
          <h2 id="cluster-title">Listening loops</h2>
        </div>
      </div>

      <div className="cluster-list">
        {clusters.length === 0 ? (
          <p className="muted-copy">{clusterStatusCopy(status)}</p>
        ) : (
          clusters.map((cluster, index) => {
            const isSelected = selected === index;
            return (
              <button
                className={isSelected ? 'cluster-card selected' : 'cluster-card'}
                key={`${cluster.label}-${index}`}
                type="button"
                onClick={() => onSelect(isSelected ? null : index)}
              >
                <span className="cluster-number">{index + 1}</span>
                <span className="cluster-body">
                  <strong>{cluster.label}</strong>
                  <span>
                    {cluster.track_count} tracks{cluster.share_of_listening ? `, ${cluster.share_of_listening}` : ''}
                  </span>
                  <span className="cluster-metrics">
                    Feeling {cluster.centroid_avd[0]?.toFixed(2)}, energy {cluster.centroid_avd[1]?.toFixed(2)}, depth{' '}
                    {cluster.centroid_avd[2]?.toFixed(2)}
                  </span>
                  {isSelected && (
                    <span className="chip-stack">
                      {[...cluster.dominant_emotions, ...cluster.dominant_themes].map((item) => (
                        <span className="chip" key={`${item.category}-${item.weight}`}>
                          <span style={{ background: categoryColor(item.category) }} />
                          {categoryLabel(item.category)} {(item.weight * 100).toFixed(0)}%
                        </span>
                      ))}
                    </span>
                  )}
                </span>
              </button>
            );
          })
        )}
      </div>
    </section>
  );
}
