import { RefreshCcw, X, Terminal } from 'lucide-react';

interface AddDataPanelProps {
  profileName: string;
  onReload: () => void;
  onClose: () => void;
}

export function AddDataPanel({ profileName, onReload, onClose }: AddDataPanelProps) {
  return (
    <div className="add-data-overlay" onClick={onClose}>
      <div className="add-data-panel" onClick={(e) => e.stopPropagation()}>
        <header>
          <h2>Add data to {profileName}</h2>
          <button className="close-btn" onClick={onClose} aria-label="Close">
            <X size={20} />
          </button>
        </header>

        <section>
          <p>Run the full pipeline with your updated Spotify export:</p>
          <div className="code-block">
            <Terminal size={14} className="terminal-icon" />
            <code>orpheus run-all --source &lt;path/to/history&gt; --profile {profileName}</code>
          </div>
          <p className="hint">
            The pipeline will ingest new plays, fetch audio features, and re-calculate your emotional state and traits.
          </p>
        </section>

        <footer>
          <button className="primary" onClick={onReload}>
            <RefreshCcw size={16} />
            Reload report
          </button>
          <button className="secondary" onClick={onClose}>
            Close
          </button>
        </footer>
      </div>
    </div>
  );
}
