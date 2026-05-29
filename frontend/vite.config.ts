import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'node:fs/promises';
import type { IncomingMessage, ServerResponse } from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import type { Connect } from 'vite';

const frontendRoot = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(frontendRoot, '..');

function reportsDir() {
  const configured = process.env.ORPHEUS_REPORTS_DIR;
  if (!configured) return path.join(repoRoot, 'data/output/reports');
  return path.isAbsolute(configured) ? configured : path.resolve(repoRoot, configured);
}

async function latestReportPath() {
  const dir = reportsDir();
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const candidates = await Promise.all(
    entries
      .filter((entry) => entry.isFile() && entry.name.endsWith('.json'))
      .map(async (entry) => {
        const filePath = path.join(dir, entry.name);
        const stat = await fs.stat(filePath);
        return { filePath, mtimeMs: stat.mtimeMs };
      }),
  );

  candidates.sort((a, b) => b.mtimeMs - a.mtimeMs || b.filePath.localeCompare(a.filePath));
  return candidates[0]?.filePath;
}

function sendJson(res: ServerResponse, statusCode: number, payload: unknown) {
  res.statusCode = statusCode;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify(payload));
}

function reportApiMiddleware(): Connect.HandleFunction {
  return async (req: IncomingMessage, res: ServerResponse, next: () => void) => {
    if (req.url !== '/api/reports/latest') {
      next();
      return;
    }

    try {
      const filePath = await latestReportPath();
      if (!filePath) {
        sendJson(res, 404, { error: 'No Orpheus reports found.' });
        return;
      }

      res.statusCode = 200;
      res.setHeader('Content-Type', 'application/json');
      res.setHeader('X-Orpheus-Report-Path', path.relative(repoRoot, filePath));
      res.end(await fs.readFile(filePath, 'utf8'));
    } catch (error) {
      const code = (error as NodeJS.ErrnoException).code;
      if (code === 'ENOENT') {
        sendJson(res, 404, { error: 'Report directory was not found.' });
        return;
      }
      sendJson(res, 500, { error: 'Unable to load latest Orpheus report.' });
    }
  };
}

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'orpheus-report-api',
      configureServer(server) {
        server.middlewares.use(reportApiMiddleware());
      },
      configurePreviewServer(server) {
        server.middlewares.use(reportApiMiddleware());
      },
    },
  ],
});
