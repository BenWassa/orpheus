import { FileJson, Music2, Upload } from 'lucide-react';
import { useRef, useState } from 'react';

interface UploadScreenProps {
  error: string | null;
  onFile: (file: File) => void;
  onDemo: () => void;
}

export function UploadScreen({ error, onFile, onDemo }: UploadScreenProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  function handleDrop(event: React.DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    const file = event.dataTransfer.files[0];
    if (file) onFile(file);
  }

  return (
    <main className="upload-shell">
      <section className="upload-panel" aria-labelledby="upload-title">
        <div className="brand-mark" aria-hidden="true">
          <Music2 size={26} />
        </div>
        <div className="upload-copy">
          <p className="eyebrow">Project Orpheus</p>
          <h1 id="upload-title">Open your listening mirror</h1>
          <p>
            Upload an Orpheus JSON report to read the emotional and thematic structure of a recent listening window.
          </p>
        </div>

        <div
          className={isDragging ? 'dropzone is-dragging' : 'dropzone'}
          onClick={() => inputRef.current?.click()}
          onDragOver={(event) => {
            event.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          role="button"
          tabIndex={0}
          onKeyDown={(event) => {
            if (event.key === 'Enter' || event.key === ' ') inputRef.current?.click();
          }}
        >
          <input
            ref={inputRef}
            type="file"
            accept="application/json,.json"
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) onFile(file);
            }}
          />
          <Upload size={24} />
          <span>Drop report JSON here, or choose a file</span>
          <small>All parsing happens locally in this browser.</small>
        </div>

        {error && (
          <div className="error-message" role="alert">
            <FileJson size={16} />
            <span>{error}</span>
          </div>
        )}

        <button className="primary-action" type="button" onClick={onDemo}>
          Read sample report
        </button>
      </section>
    </main>
  );
}
