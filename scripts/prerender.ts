// Prerender (decision 41 spike): renders each route in headless Chromium against `vite preview` and writes the
// HTML to dist/<route>/index.html, so crawlers and link previews see the page without running JavaScript.
// Run after `vite build`: `npm run build && npm run prerender`. Choice: full `puppeteer` (downloads its own Chrome,
// ~170 MB, at install); on Vercel set PUPPETEER_SKIP_DOWNLOAD=1 until the Vercel strategy is decided (Vercel does not run this yet).
// Optional SITE_ORIGIN=https://... replaces the local preview origin in the output (og:image URLs).
import { spawn, type ChildProcess } from 'node:child_process';
import { existsSync } from 'node:fs';
import { mkdir, writeFile } from 'node:fs/promises';
import { createServer } from 'node:net';
import { dirname, join } from 'node:path';
import puppeteer, { type Browser } from 'puppeteer';

const ROOT = join(import.meta.dirname, '..');
const DIST = join(ROOT, 'dist');
// Spike: one route. The follow-up extends this to every page.
const ROUTES = ['/papers/attention-is-all-you-need'];
const READY_TIMEOUT_MS = 30_000;

function freePort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const server = createServer();
    server.on('error', reject);
    server.listen(0, () => {
      const address = server.address();
      server.close(() => (typeof address === 'object' && address ? resolve(address.port) : reject(new Error('no free port'))));
    });
  });
}

interface Preview {
  child: ChildProcess;
  origin: string;
}

// Starts `vite preview` on the given port and resolves once it prints its local URL.
function startPreview(port: number): Promise<Preview> {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [join(ROOT, 'node_modules', 'vite', 'bin', 'vite.js'), 'preview', '--port', String(port), '--strictPort'], {
      cwd: ROOT,
      env: { ...process.env, NO_COLOR: '1' },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let output = '';
    const timer = setTimeout(() => fail(new Error(`vite preview did not start within ${READY_TIMEOUT_MS / 1000} s`)), READY_TIMEOUT_MS);

    function fail(err: Error) {
      clearTimeout(timer);
      child.kill('SIGTERM');
      reject(err);
    }

    const onOutput = (chunk: Buffer) => {
      output += chunk.toString();
      const match = output.match(/Local:\s+(https?:\/\/\S+)/);
      if (match) {
        clearTimeout(timer);
        resolve({ child, origin: match[1].replace(/\/$/, '') });
      }
    };
    child.stdout?.on('data', onOutput);
    child.stderr?.on('data', onOutput);
    child.on('error', fail);
    child.on('exit', code => fail(new Error(`vite preview exited early (code ${code})`)));
  });
}

function stopPreview(child: ChildProcess): Promise<void> {
  return new Promise(resolve => {
    if (child.exitCode !== null || child.signalCode !== null) return resolve();
    const force = setTimeout(() => child.kill('SIGKILL'), 3_000);
    child.once('exit', () => {
      clearTimeout(force);
      resolve();
    });
    child.kill('SIGTERM');
  });
}

// Browser-side snippets are strings: this file is typechecked without the DOM lib.
const READY_CHECK = `document.title.length > 0 && !!document.querySelector('main') && !document.querySelector('main[aria-busy="true"]')`;
const SNAPSHOT = `(() => {
  const error = document.querySelector('.load-error');
  return error ? { error: error.textContent || 'load error' } : { html: document.documentElement.outerHTML };
})()`;

// Visits one route and returns its rendered HTML. Fails if the app shows its load-error message.
async function renderRoute(browser: Browser, origin: string, route: string): Promise<string> {
  const page = await browser.newPage();
  try {
    const pageErrors: string[] = [];
    page.on('pageerror', err => pageErrors.push(err instanceof Error ? err.message : String(err)));
    await page.goto(new URL(route, origin).href, { waitUntil: 'networkidle0', timeout: READY_TIMEOUT_MS });
    // Ready when the app has replaced its loading state (<main aria-busy>) and the title is set.
    await page.waitForFunction(READY_CHECK, { timeout: READY_TIMEOUT_MS });
    const result = (await page.evaluate(SNAPSHOT)) as { error: string } | { html: string };
    if ('error' in result) throw new Error(`page reported: ${result.error}`);
    if (pageErrors.length) throw new Error(`uncaught page error: ${pageErrors[0]}`);
    return result.html;
  } finally {
    await page.close();
  }
}

function outputPath(route: string): string {
  const clean = route.replace(/^\/+|\/+$/g, '');
  return clean ? join(DIST, clean, 'index.html') : join(DIST, 'index.html');
}

async function main() {
  if (!existsSync(join(DIST, 'index.html'))) throw new Error('dist/index.html not found: run `npm run build` first');
  const started = performance.now();
  const port = await freePort();
  const preview = await startPreview(port);
  // Last-resort cleanup if the process exits for any reason (including Ctrl-C) while the server is running.
  process.once('exit', () => preview.child.kill('SIGKILL'));
  if (!process.env.SITE_ORIGIN) console.warn(`SITE_ORIGIN not set: absolute URLs in the output use ${preview.origin}`);
  let browser: Browser | undefined;
  const failures: string[] = [];
  let written = 0;
  try {
    browser = await puppeteer.launch({ headless: true });
    for (const route of ROUTES) {
      const t0 = performance.now();
      try {
        let html = await renderRoute(browser, preview.origin, route);
        if (process.env.SITE_ORIGIN) html = html.split(preview.origin).join(process.env.SITE_ORIGIN.replace(/\/$/, ''));
        const file = outputPath(route);
        await mkdir(dirname(file), { recursive: true });
        await writeFile(file, html, 'utf8');
        written++;
        const kb = (Buffer.byteLength(html) / 1024).toFixed(1);
        console.log(`✓ ${route} → ${file.slice(ROOT.length + 1)} (${kb} KB, ${((performance.now() - t0) / 1000).toFixed(1)} s)`);
      } catch (err) {
        failures.push(route);
        console.error(`✗ ${route}: ${err instanceof Error ? err.message : String(err)}`);
      }
    }
  } finally {
    await browser?.close();
    await stopPreview(preview.child);
  }
  const seconds = ((performance.now() - started) / 1000).toFixed(1);
  console.log(`Prerendered ${written}/${ROUTES.length} routes in ${seconds} s.`);
  if (failures.length) {
    console.error(`Failed: ${failures.join(', ')}`);
    process.exitCode = 1;
  }
}

main().catch(err => {
  console.error(err instanceof Error ? err.message : err);
  process.exitCode = 1;
});
