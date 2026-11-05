// The one list of routes that `npm run prerender` writes and `npm run check:prerender` verifies (decision 41).
// It is generated from the approved data in public/data (site.json and library.json), so adding a paper, issue or
// company to the data adds its page here without editing any script.
//
// Build flag: set VITE_HIDE_SAMPLES=1 for prerender and check too when the build used it. Sample routes are then
// left out, because the build no longer contains those stories.
//
// Query-string views (?feed, ?search) share "/" with the front page, so they cannot each have their own
// dist/<path>/index.html. They are listed in DEFERRED with a reason, and both scripts print that list.
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import type { Library, SiteConfig } from '../src/types.ts';

const ROOT = join(import.meta.dirname, '..');
export const DIST = join(ROOT, 'dist');
const PUBLIC = join(ROOT, 'public');
const read = <T>(path: string): T => JSON.parse(readFileSync(join(PUBLIC, path), 'utf8')) as T;

export const site = read<SiteConfig>('data/site.json');
const library = read<Library>('data/library.json');

/** The title every page had before it got its own (the home page keeps it). */
export const GENERIC_TITLE = `${site.name} — ${site.motto}`;

export type RouteKind = 'home' | 'paper' | 'sample' | 'issue' | 'issues' | 'company' | 'companies' | 'map';

export interface PrerenderRoute {
  /** URL path, e.g. "/papers/attention-is-all-you-need". */
  route: string;
  kind: RouteKind;
}

export interface DeferredRoute {
  route: string;
  reason: string;
}

export const DEFERRED: DeferredRoute[] = [
  {
    route: '/?feed',
    reason: 'snack mode shares "/" with the front page, so it has no dist/ page of its own; it needs a distinct path first',
  },
  {
    route: '/?search',
    reason: 'the archive search (also ?q= and ?tag=) shares "/" with the front page; it needs a distinct path first',
  },
  {
    route: '/?paper=<slug>',
    reason: 'legacy link that the browser rewrites to /papers/<slug>; the target page is prerendered',
  },
];

const SAFE_SEGMENT = /^[a-z0-9][a-z0-9-]*$/;

function segment(id: string, what: string): string {
  if (!SAFE_SEGMENT.test(id)) throw new Error(`${what} id "${id}" is not a lowercase slug; it cannot be a route.`);
  return id;
}

/** Every route to prerender, in a stable order, with duplicates removed. */
export function prerenderRoutes(): PrerenderRoute[] {
  const hideSamples = process.env.VITE_HIDE_SAMPLES === '1';
  const out: PrerenderRoute[] = [{ route: '/', kind: 'home' }];
  const realStories = new Set(library.stories.filter(s => s.real).map(s => s.id));

  // Real papers: every entry in site.json has its own page (App loads papers/<slug>.json for it).
  for (const paper of site.papers) {
    out.push({ route: `/papers/${segment(paper.slug, 'paper')}`, kind: 'paper' });
    realStories.delete(paper.slug);
  }
  if (realStories.size) {
    throw new Error(`library.json marks ${[...realStories].join(', ')} as real, but site.json does not list ${realStories.size > 1 ? 'them' : 'it'}; the page would fail to load.`);
  }

  // Sample stories: App renders any story that is not real as a labelled sample page.
  for (const story of library.stories) {
    if (story.real) continue;
    if (hideSamples && story.sample) continue;
    out.push({ route: `/papers/${segment(story.id, 'story')}`, kind: 'sample' });
  }

  for (const issue of library.issues) {
    if (hideSamples && issue.sample) continue;
    out.push({ route: `/issues/${segment(issue.id, 'issue')}`, kind: 'issue' });
  }
  // With no id, /issues shows the latest issue and /companies the first company, so these need at least one.
  if (library.issues.length) out.push({ route: '/issues', kind: 'issues' });

  for (const company of library.companies) {
    if (hideSamples && company.sample) continue;
    out.push({ route: `/companies/${segment(company.id, 'company')}`, kind: 'company' });
  }
  if (library.companies.length) out.push({ route: '/companies', kind: 'companies' });

  out.push({ route: '/map', kind: 'map' });

  const unique = new Map<string, PrerenderRoute>();
  for (const r of out) if (!unique.has(r.route)) unique.set(r.route, r);
  return [...unique.values()];
}

/** Where a route's prerendered HTML is written (and checked): dist/<route>/index.html. */
export const htmlPathFor = (route: string): string => {
  const clean = route.replace(/^\/+|\/+$/g, '');
  return clean ? join(DIST, clean, 'index.html') : join(DIST, 'index.html');
};
