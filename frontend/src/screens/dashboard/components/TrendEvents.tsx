import { ArrowDownRight, ArrowUpRight } from 'lucide-react';
import { categoryColor, categoryLabel } from '../../../taxonomy';
import type { TrendEvent } from '../../../types';

interface TrendEventsProps {
  trends: TrendEvent[];
}

export function TrendEvents({ trends }: TrendEventsProps) {
  return (
    <section className="panel" aria-labelledby="trend-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Recent movement</p>
          <h2 id="trend-title">What changed</h2>
        </div>
      </div>
      <div className="event-list">
        {trends.length === 0 ? (
          <p className="muted-copy">This report did not find a clear recent shift.</p>
        ) : (
          trends.map((trend) => {
            const isRising = trend.direction === 'rising' || trend.direction === 'spiking';
            const Icon = isRising ? ArrowUpRight : ArrowDownRight;
            return (
              <article className="event-row" key={`${trend.axis}-${trend.category}-${trend.direction}`}>
                <span className="event-icon" style={{ color: categoryColor(trend.category) }}>
                  <Icon size={18} />
                </span>
                <div>
                  <h3>{categoryLabel(trend.category)}</h3>
                  <p>{trend.narrative}</p>
                </div>
                <span className="event-badge">{trend.magnitude}</span>
              </article>
            );
          })
        )}
      </div>
    </section>
  );
}
