import { useEffect, useRef } from 'react';
import { RefreshCcw, X, Terminal } from 'lucide-react';

interface AddDataPanelProps {
  profileName: string;
  onReload: () => void;
  onClose: () => void;
}

export function AddDataPanel({ profileName, onReload, onClose }: AddDataPanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);

  // Focus the close button on mount
  useEffect(() => {
    closeRef.current?.focus();
  }, []);

  // Trap focus within the dialog
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        onClose();
        return;
      }
      if (e.key !== 'Tab') return;

      const panel = panelRef.current;
      if (!panel) return;

      const focusable = panel.querySelectorAll<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
      );
      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault();
          last?.focus();
        }
      } else {
        if (document.activeElement === last) {
          e.preventDefault();
          first?.focus();
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  return (
    <div className="add-data-overlay" onClick={onClose} aria-hidden="true">
      <div
        ref={panelRef}
        className="add-data-panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="add-data-title"
        onClick={(e) => e.stopPropagation()}
      >
        <header>
          <h2 id="add-data-title">Add data to {profileName}</h2>
          <button ref={closeRef} className="close-btn" onClick={onClose} aria-label="Close dialog">
            <X size={20} />
          </button>
        </header>

        <section>
          <p>Run the full pipeline with your updated Spotify export:</p>
          <div className="code-block">
            <Terminal size={14} className="terminal-icon" aria-hidden="true" />
            <code>orpheus run-all --source &lt;path/to/history&gt; --profile {profileName}</code>
          </div>
          <p className="hint">
            The pipeline will ingest new plays, fetch audio features, and re-calculate your emotional state and traits.
          </p>
        </section>

        <footer>
          <button className="primary" onClick={onReload}>
            <RefreshCcw size={16} aria-hidden="true" />
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
