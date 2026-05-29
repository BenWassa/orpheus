import { ShieldCheck } from 'lucide-react';
import type { SafetyFlag } from '../../../types';

interface SafetyFlagsProps {
  flags: SafetyFlag[];
}

export function SafetyFlags({ flags }: SafetyFlagsProps) {
  if (flags.length === 0) return null;

  return (
    <section className="safety-stack" aria-label="Safety notices">
      {flags.map((flag, index) => (
        <article className="safety-note" key={`${flag.flag_type}-${index}`}>
          <ShieldCheck size={18} />
          <div>
            <h2>Gentle attention marker</h2>
            <p>{flag.message}</p>
            {flag.recommendation && <small>{flag.recommendation}</small>}
          </div>
        </article>
      ))}
    </section>
  );
}
