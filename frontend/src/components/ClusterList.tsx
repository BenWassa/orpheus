import { categoryColor, categoryLabel } from '../taxonomy';
import type { ClusterSummary } from '../types';

interface ClusterListProps {
  clusters: ClusterSummary[];
  selected: number | null;
  onSelect: (index: number | null) => void;
}

export function ClusterList({ clusters, selected, onSelect }: ClusterListProps) {
  return (
    <section className="panel" aria-labelledby="cluster-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Detected loops</p>
          <h2 id="cluster-title">Listening clusters</h2>
        </div>
      </div>

      <div className="cluster-list">
        {clusters.length === 0 ? (
          <p className="muted-copy">No clusters were emitted in this report.</p>
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
                    V {cluster.centroid_avd[0]?.toFixed(2)} · A {cluster.centroid_avd[1]?.toFixed(2)} · D{' '}
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
