// Checks the prerendered pages (run after `npm run build && npm run prerender`): `npm run check:prerender`.
// For every route in scripts/prerender-routes.ts it asserts that dist/<route>/index.html exists and carries
// page-specific metadata: a <title> (not the generic site title, except on the home page), a description, and
// og:title, og:description and og:type. An og:image, when present, must not be an SVG (social platforms do not
// render SVG previews). Any failure prints one line per route and exits with code 1.
// Placeholder text such as "[Company name]" and duplicate titles are reported as warnings, not failures.
//
// Inspect the pages through `npx vite preview`, not by opening the files directly: file:// does not resolve /assets
// paths reliably. Use trailing-slash URLs (http://localhost:4173/papers/resnet/): vite preview serves the prerendered
// file only for those, and an extensionless URL gets the SPA shell. Set VITE_HIDE_SAMPLES=1 here too when the build
// used it.
import { existsSync, readFileSync } from 'node:fs';
import { dirname, relative } from 'node:path';
import { DEFERRED, DIST, GENERIC_TITLE, htmlPathFor, prerenderRoutes, type PrerenderRoute } from './prerender-routes.ts';

interface PageHead {
  title?: string;
  metas: Record<string, string>[];
  hasMain: boolean;
  hasLoadError: boolean;
}

const decode = (s: string) =>
  s.replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'").trim();

function parseHead(html: string): PageHead {
  const title = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1];
  const metas = [...html.matchAll(/<meta\b([^>]*)>/gi)].map(m => {
    const attrs: Record<string, string> = {};
    for (const a of m[1].matchAll(/([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*"([^"]*)"/g)) attrs[a[1].toLowerCase()] = decode(a[2]);
    return attrs;
  });
  return {
    title: title === undefined ? undefined : decode(title),
    metas,
    hasMain: /<main[\s>]/i.test(html),
    hasLoadError: /class="load-error"/.test(html),
  };
}

/** The content of <meta name="..."> or <meta property="..."> with that key, if present and non-empty. */
function metaValue(head: PageHead, attr: 'name' | 'property', key: string): string | undefined {
  const tag = head.metas.find(m => m[attr] === key);
  return tag?.content ? tag.content : undefined;
}

const PLACEHOLDER = /\[[^\]]+\]/;

interface RouteResult {
  route: string;
  errors: string[];
  warnings: string[];
  title?: string;
}

function checkRoute({ route, kind }: PrerenderRoute): RouteResult {
  const result: RouteResult = { route, errors: [], warnings: [] };
  const file = htmlPathFor(route);
  if (!existsSync(file)) {
    result.errors.push(`missing ${relative(dirname(DIST), file)} (run npm run prerender)`);
    return result;
  }
  const head = parseHead(readFileSync(file, 'utf8'));
  if (head.hasLoadError) result.errors.push('page shows its load-error message');
  if (!head.hasMain) result.errors.push('no <main> element rendered');

  const title = head.title ?? '';
  result.title = title;
  if (!title) result.errors.push('<title> is missing or empty');
  else if (title === GENERIC_TITLE && kind !== 'home') result.errors.push(`<title> is the generic site title "${GENERIC_TITLE}"; expected a page-specific title`);

  const required: [string, string | undefined][] = [
    ['<meta name="description">', metaValue(head, 'name', 'description')],
    ['<meta property="og:title">', metaValue(head, 'property', 'og:title')],
    ['<meta property="og:description">', metaValue(head, 'property', 'og:description')],
    ['<meta property="og:type">', metaValue(head, 'property', 'og:type')],
  ];
  for (const [label, value] of required) if (!value) result.errors.push(`${label} is missing or empty`);

  const image = metaValue(head, 'property', 'og:image');
  if (image && /\.svg([?#].*)?$/i.test(image)) result.errors.push(`og:image points at an SVG (${image}); omit it instead`);

  for (const [label, value] of [['title', title], ['description', metaValue(head, 'name', 'description') ?? '']] as const) {
    if (PLACEHOLDER.test(value)) result.warnings.push(`${label} contains placeholder text: "${value}"`);
  }
  return result;
}

function main() {
  if (!existsSync(htmlPathFor('/'))) {
    console.error('dist/index.html not found: run `npm run build && npm run prerender` first.');
    process.exitCode = 1;
    return;
  }
  const routes = prerenderRoutes();
  const results = routes.map(checkRoute);
  const failed = results.filter(r => r.errors.length);

  for (const r of failed) {
    console.error(`✗ ${r.route}`);
    for (const e of r.errors) console.error(`    - ${e}`);
  }

  // Duplicate titles are a warning: /issues and /companies show the same content as their first item.
  const byTitle = new Map<string, string[]>();
  for (const r of results) if (r.title) byTitle.set(r.title, [...(byTitle.get(r.title) ?? []), r.route]);
  const duplicates = [...byTitle.entries()].filter(([, list]) => list.length > 1);
  const warnings = results.flatMap(r => r.warnings.map(w => `${r.route}: ${w}`));
  for (const [title, list] of duplicates) warnings.push(`same title on ${list.join(', ')}: "${title}"`);

  if (warnings.length) {
    console.warn(`Warnings (${warnings.length}):`);
    for (const w of warnings) console.warn(`  ! ${w}`);
  }
  console.log('Deferred (not prerendered, no page of their own):');
  for (const d of DEFERRED) console.log(`  - ${d.route}: ${d.reason}`);

  if (failed.length) {
    console.error(`\n${failed.length} of ${results.length} routes failed the prerender check.`);
    process.exitCode = 1;
    return;
  }
  console.log(`\nPrerender check passed: ${results.length} routes, each with its own title and description, og:title, og:description and og:type.`);
  console.log('Inspect with `npx vite preview` at trailing-slash URLs, e.g. /papers/resnet/ (not file:// and not extensionless URLs).');
}

main();
