// Prerender (decision 41): renders each route in headless Chromium against `vite preview` and writes the HTML to
// dist/<route>/index.html, so crawlers and link previews see the page without running JavaScript.
// Run after `vite build`: `npm run build && npm run prerender`, then `npm run check:prerender`.
//
// Routes come from scripts/prerender-routes.ts (generated from Supabase). Query-string views (?feed, ?search)
// are not prerendered; they are listed as deferred there and printed below.
//
// Inspect the generated pages through `npx vite preview`, not by opening the files directly (file:// does not
// resolve /assets paths reliably). Use URLs with a trailing slash, e.g. http://localhost:4173/papers/resnet/: vite
// preview returns the prerendered file only for those (and /index.html). An extensionless URL gets the SPA shell.
//
// Absolute URLs built from the local preview origin (for example app links) are affected by SITE_ORIGIN:
//   - SITE_ORIGIN unset: the local preview origin (http://localhost:<port>) stays in the output. That makes it obvious
//     these are local files, not production share URLs.
//   - SITE_ORIGIN=https://... set: the local origin is replaced by it. Use this for a real release build only.
// Supabase-only enumeration: v_live_story filters status = 'live' and sample = false, so sample stories are never routes.
//
// Browser: full `puppeteer` (downloads its own Chrome, ~170 MB, at install). On Vercel set PUPPETEER_SKIP_DOWNLOAD=1
// until the Vercel strategy is decided (Vercel does not run this yet).
import { spawn, type ChildProcess } from 'node:child_process';
import { existsSync } from 'node:fs';
import { mkdir, writeFile } from 'node:fs/promises';
import { createServer } from 'node:net';
import { dirname, join } from 'node:path';
import puppeteer, { type Browser } from 'puppeteer';
import { DEFERRED, DIST, htmlPathFor, prerenderRoutes } from './prerender-routes.ts';

const ROOT = join(import.meta.dirname, '..');
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
// Ready = the app replaced its loading state, set the title, and has run useHead (description and og:type exist).
const READY_CHECK = `document.title.length > 0 && !!document.querySelector('main') && !document.querySelector('main[aria-busy="true"]') && !document.querySelector('.book-loader')
  && !!document.querySelector('meta[name="description"]') && !!document.querySelector('meta[property="og:type"]')`;
const SNAPSHOT = `(() => {
  const error = document.querySelector('.load-error');
  const root = document.getElementById('root');
  const clone = document.documentElement.cloneNode(true);
  clone.querySelector('#__initial_data__')?.remove();
  return error ? { error: error.textContent || 'load error' } : {
    html: clone.outerHTML,
    initialData: window.__initial_data_json__ || null,
    route: window.__initial_route__ || null,
  };
})()`;

// Visits one route and returns its rendered HTML. Fails if the app shows its load-error message.
async function renderRoute(browser: Browser, origin: string, route: string): Promise<string> {
  const page = await browser.newPage();
  try {
    const pageErrors: string[] = [];
    page.on('pageerror', err => pageErrors.push(err instanceof Error ? err.message : String(err)));
    // Passed as a string so Node's tsc doesn't try to typecheck `window` in a browser-eval callback.
    await page.evaluateOnNewDocument(`
      window.__gt_prerender__ = true;
      window.__collect_initial_data__ = function(data) {
        window.__initial_data_json__ = JSON.stringify(data);
        window.__initial_route__ = data.route;
      };
    `);
    await page.goto(new URL(route, origin).href, { waitUntil: 'networkidle0', timeout: READY_TIMEOUT_MS });
    await page.waitForFunction(READY_CHECK, { timeout: READY_TIMEOUT_MS });
    const result = (await page.evaluate(SNAPSHOT)) as { error: string } | { html: string; initialData: string | null; route: string | null };
    if ('error' in result) throw new Error(`page reported: ${result.error}`);
    if (pageErrors.length) throw new Error(`uncaught page error: ${pageErrors[0]}`);
    if (!result.initialData) throw new Error('page did not report its initial data');
    if (result.route !== route) throw new Error(`reported route "${result.route}" does not match "${route}"`);
    const json = result.initialData.replace(/</g, '\\u003c').replace(/\u2028/g, '\\u2028').replace(/\u2029/g, '\\u2029');
    if (/<\/script|<!--/i.test(json)) throw new Error('unsafe initial data JSON');
    const script = `<script id="__initial_data__" type="application/json">${json}</script>`;
    const bodyClose = result.html.toLowerCase().lastIndexOf('</body>');
    if (bodyClose < 0) throw new Error('rendered document has no </body>');
    const html = `${result.html.slice(0, bodyClose)}${script}${result.html.slice(bodyClose)}`;
    return `<!doctype html>\n${html}`;
  } finally {
    await page.close();
  }
}

async function main() {
  if (!existsSync(join(DIST, 'index.html'))) throw new Error('dist/index.html not found: run `npm run build` first');
  const routes = (await prerenderRoutes()).map(r => r.route);
  console.log(`Routes: ${routes.length} (generated from Supabase).`);
  for (const d of DEFERRED) console.log(`Deferred (not prerendered): ${d.route}: ${d.reason}.`);

  const started = performance.now();
  const port = await freePort();
  const preview = await startPreview(port);
  // Last-resort cleanup if the process exits for any reason (including Ctrl-C) while the server is running.
  process.once('exit', () => preview.child.kill('SIGKILL'));
  if (!process.env.SITE_ORIGIN) console.warn(`SITE_ORIGIN not set: absolute URLs in the output use ${preview.origin} (local only).`);
  let browser: Browser | undefined;
  const failures: string[] = [];
  let written = 0;
  try {
    browser = await puppeteer.launch({ headless: true });
    for (const route of routes) {
      const t0 = performance.now();
      try {
        let html = await renderRoute(browser, preview.origin, route);
        if (process.env.SITE_ORIGIN) html = html.split(preview.origin).join(process.env.SITE_ORIGIN.replace(/\/$/, ''));
        const file = htmlPathFor(route);
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
  console.log(`Prerendered ${written}/${routes.length} routes in ${seconds} s.`);
  if (failures.length) {
    console.error(`Failed: ${failures.join(', ')}`);
    process.exitCode = 1;
  }
}

main().catch(err => {
  console.error(err instanceof Error ? err.message : err);
  process.exitCode = 1;
});
