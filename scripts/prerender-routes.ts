// The one list of routes that `npm run prerender` writes and `npm run check:prerender` verifies (decision 41).
// It is generated from Supabase at build time: v_live_story for papers, v_issue for issues, v_company for companies.
// Add a story (via `npm run publish:supabase`), issue or company to the database and its page appears here on the
// next prerender without editing any script.
//
// Supabase reads use the publishable (anon) key, matching src/data/source-supabase.ts. Row-level security on the
// public views limits the read to non-sample, live rows, so no sample paper routes are emitted.
//
// Query-string views (?feed, ?search) share "/" with the front page, so they cannot each have their own
// dist/<path>/index.html. They are listed in DEFERRED with a reason, and both scripts print that list.
import { join } from 'node:path';
import { createClient, type SupabaseClient } from '@supabase/supabase-js';

const ROOT = join(import.meta.dirname, '..');
export const DIST = join(ROOT, 'dist');

/** Site name + motto from v_site. Used to build the generic page title the home page carries. */
export async function loadSiteMeta(): Promise<{ name: string; motto: string; genericTitle: string }> {
  const { data, error } = await makeClient()
    .from('v_site')
    .select('site_name, motto')
    .maybeSingle();
  if (error) throw new Error(`Could not read v_site: ${error.message}`);
  if (!data) throw new Error('v_site has no row.');
  const row = data as { site_name: string; motto: string | null };
  const motto = row.motto ?? '';
  return { name: row.site_name, motto, genericTitle: `${row.site_name} — ${motto}` };
}

export type RouteKind = 'home' | 'paper' | 'issue' | 'issues' | 'company' | 'companies' | 'map';

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

function requiredEnv(name: 'VITE_SUPABASE_URL' | 'VITE_SUPABASE_PUBLISHABLE_KEY'): string {
  const value = (process.env[name] ?? '').trim();
  if (!value) {
    throw new Error(`${name} is not set. Run the script with --env-file=.env (see package.json), or export it in the shell.`);
  }
  return value;
}

let clientSingleton: SupabaseClient | undefined;
function makeClient(): SupabaseClient {
  clientSingleton ??= createClient(requiredEnv('VITE_SUPABASE_URL'), requiredEnv('VITE_SUPABASE_PUBLISHABLE_KEY'), {
    auth: { persistSession: false, autoRefreshToken: false, detectSessionInUrl: false },
  });
  return clientSingleton;
}

/** Every route to prerender, in a stable order, with duplicates removed. */
export async function prerenderRoutes(): Promise<PrerenderRoute[]> {
  const client = makeClient();
  const out: PrerenderRoute[] = [{ route: '/', kind: 'home' }];

  // Real papers: every live story in v_live_story. The view filters status = 'live' and sample = false (decision 48/49),
  // so sample stories never appear here.
  const { data: stories, error: storiesError } = await client
    .from('v_live_story')
    .select('story_slug')
    .order('story_slug', { ascending: true });
  if (storiesError) throw new Error(`Could not read v_live_story: ${storiesError.message}`);
  for (const row of stories ?? []) {
    out.push({ route: `/papers/${segment(row.story_slug as string, 'paper')}`, kind: 'paper' });
  }

  const { data: issues, error: issuesError } = await client
    .from('v_issue')
    .select('slug, position')
    .order('position', { ascending: true });
  if (issuesError) throw new Error(`Could not read v_issue: ${issuesError.message}`);
  for (const row of issues ?? []) {
    out.push({ route: `/issues/${segment(row.slug as string, 'issue')}`, kind: 'issue' });
  }
  // With no id, /issues shows the latest issue and /companies the first company, so these need at least one.
  if ((issues ?? []).length) out.push({ route: '/issues', kind: 'issues' });

  const { data: companies, error: companiesError } = await client
    .from('v_company')
    .select('slug')
    .order('slug', { ascending: true });
  if (companiesError) throw new Error(`Could not read v_company: ${companiesError.message}`);
  for (const row of companies ?? []) {
    out.push({ route: `/companies/${segment(row.slug as string, 'company')}`, kind: 'company' });
  }
  if ((companies ?? []).length) out.push({ route: '/companies', kind: 'companies' });

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
