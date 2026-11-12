// Hydration check (run after `npm run build && npm run prerender`): `npm run check:hydration`.
// Loads every prerendered route in headless Chromium through `vite preview` and fails on any hydration error:
// main.tsx logs onRecoverableError as "Hydration mismatch: ...", and a hard failure is a page error. Both must
// match /hydrat/i. Production React only prints minified codes, so this checks for the signal, not the detail.
// Use `DEV_REACT=1`-style builds (see the hydration notes in AGENTS.md) to see the mismatching element.
import { spawn, type ChildProcess } from 'node:child_process';
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import puppeteer from 'puppeteer';
import { DIST, prerenderRoutes } from './prerender-routes.ts';

const ROOT = join(import.meta.dirname, '..');
const PORT = 4179;
const ORIGIN = `http://localhost:${PORT}`;
const HYDRATION = /hydrat/i;

async function waitForPreview(child: ChildProcess): Promise<void> {
  const deadline = Date.now() + 20_000;
  while (Date.now() < deadline) {
    try {
      if ((await fetch(`${ORIGIN}/`)).ok) return;
    } catch {
      // not listening yet
    }
    await new Promise(r => setTimeout(r, 250));
  }
  child.kill('SIGKILL');
  throw new Error(`vite preview did not start on ${ORIGIN} within 20 s`);
}

async function main(): Promise<number> {
  if (!existsSync(join(DIST, 'index.html'))) throw new Error('dist/index.html not found: run `npm run build && npm run prerender` first');
  const preview = spawn(process.execPath, [join(ROOT, 'node_modules', 'vite', 'bin', 'vite.js'), 'preview', '--port', String(PORT), '--strictPort'], { cwd: ROOT, stdio: 'ignore' });
  process.once('exit', () => preview.kill('SIGKILL'));
  await waitForPreview(preview);

  const browser = await puppeteer.launch({ headless: true });
  const rows: { route: string; count: number; first: string }[] = [];
  try {
    for (const { route } of await prerenderRoutes()) {
      const page = await browser.newPage();
      const hits: string[] = [];
      page.on('console', m => {
        const type: string = m.type();
        if ((type === 'warn' || type === 'warning' || type === 'error') && HYDRATION.test(m.text())) hits.push(m.text());
      });
      page.on('pageerror', (e: unknown) => {
        const msg = e instanceof Error ? e.message : String(e);
        if (HYDRATION.test(msg)) hits.push(msg);
      });
      // vite preview serves the prerendered file only for trailing-slash URLs (see check-prerender.ts).
      await page.goto(route.endsWith('/') ? ORIGIN + route : `${ORIGIN}${route}/`, { waitUntil: 'networkidle0' });
      await new Promise(r => setTimeout(r, 1000));
      rows.push({ route, count: hits.length, first: (hits[0] ?? '').slice(0, 90) });
      await page.close();
    }
  } finally {
    await browser.close();
    preview.kill('SIGKILL');
  }

  const failing = rows.filter(r => r.count > 0);
  console.table(rows.map(r => ({ route: r.route, hydrationErrors: r.count, first: r.first })));
  console.log(failing.length ? `${failing.length} of ${rows.length} routes report hydration errors.` : `All ${rows.length} routes hydrate cleanly.`);
  return failing.length ? 1 : 0;
}

main().then(code => { process.exitCode = code; }, err => {
  console.error(err instanceof Error ? err.message : err);
  process.exitCode = 1;
});
