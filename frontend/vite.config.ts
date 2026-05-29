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

async function latestReportPathForProfile(profile?: string) {
  let dir = reportsDir();
  if (profile) {
    if (!/^[a-zA-Z0-9_\- ]+$/.test(profile)) {
      throw new Error('INVALID_PROFILE');
    }
    dir = path.join(dir, profile);
  }

  try {
    const entries = await fs.readdir(dir, { withFileTypes: true });
    const candidates = await Promise.all(
      entries
        .filter((entry) => entry.isFile() && entry.name.endsWith('.json'))
        .map(async (entry) => {
          const filePath = path.join(dir, entry.name);
          const stat = await fs.stat(filePath);
          return { filePath, mtimeMs: stat.mtimeMs, name: entry.name };
        }),
    );

    candidates.sort((a, b) => b.mtimeMs - a.mtimeMs || b.filePath.localeCompare(a.filePath));
    return candidates[0];
  } catch (err) {
    if ((err as NodeJS.ErrnoException).code === 'ENOENT') return null;
    throw err;
  }
}

function sendJson(res: ServerResponse, statusCode: number, payload: unknown) {
  res.statusCode = statusCode;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify(payload));
}

function reportApiMiddleware(): Connect.HandleFunction {
  return async (req: IncomingMessage, res: ServerResponse, next: () => void) => {
    if (!req.url?.startsWith('/api/')) {
      next();
      return;
    }

    const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);

    if (url.pathname === '/api/profiles') {
      try {
        const dir = reportsDir();
        const entries = await fs.readdir(dir, { withFileTypes: true });
        const profiles = [];

        for (const entry of entries) {
          if (entry.isDirectory()) {
            const profileDir = path.join(dir, entry.name);
            const files = await fs.readdir(profileDir);
            const jsonFiles = files.filter((f) => f.endsWith('.json')).sort();
            const latest = jsonFiles[jsonFiles.length - 1] || null;

            profiles.push({
              name: entry.name,
              reportCount: jsonFiles.length,
              latestReportAt: latest ? latest.replace('.json', '') : null,
            });
          }
        }

        profiles.sort((a, b) => a.name.localeCompare(b.name));
        sendJson(res, 200, profiles);
      } catch (error) {
        if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
          sendJson(res, 200, []);
        } else {
          sendJson(res, 500, { error: 'Unable to list profiles.' });
        }
      }
      return;
    }

    if (url.pathname === '/api/reports/latest') {
      try {
        const profile = url.searchParams.get('profile') || undefined;
        const latest = await latestReportPathForProfile(profile);

        if (!latest) {
          sendJson(res, 404, {
            error: profile
              ? `No reports found for profile "${profile}".`
              : 'No Orpheus reports found.',
          });
          return;
        }

        res.statusCode = 200;
        res.setHeader('Content-Type', 'application/json');
        res.setHeader('X-Orpheus-Report-Path', path.relative(repoRoot, latest.filePath));
        res.end(await fs.readFile(latest.filePath, 'utf8'));
      } catch (error) {
        if ((error as Error).message === 'INVALID_PROFILE') {
          sendJson(res, 400, { error: 'Invalid profile name.' });
          return;
        }
        sendJson(res, 500, { error: 'Unable to load latest Orpheus report.' });
      }
      return;
    }

    next();
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
