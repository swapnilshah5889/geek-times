// The Supabase data source (decisions 48, 49). Browser-side: uses only the URL and the publishable key. Reads go
// through the public views (sample = false, status = 'live' already applied). Never read a service-role key here.

import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import {
  STORY_SCHEMA_VERSION, storyVersionMessage,
  type FacetDef, type GraphNode, type GraphRelation,
  type Library, type LibraryCompany, type LibraryField, type LibraryIssue, type LibraryStory,
  type LibraryVolume, type PaperDoc, type SiteConfig, type Storyline,
  type TagDef, type TagFacet, type TagVocabulary,
} from '../types';

// --- Client ---------------------------------------------------------------------------------

function requiredEnv(name: 'VITE_SUPABASE_URL' | 'VITE_SUPABASE_PUBLISHABLE_KEY'): string {
  const value = ((import.meta.env[name] as string | undefined) ?? '').trim();
  if (!value) throw new Error(`${name} is not set. Add it to .env (see .env.example).`);
  return value;
}

let singleton: SupabaseClient | undefined;
function client(): SupabaseClient {
  singleton ??= createClient(requiredEnv('VITE_SUPABASE_URL'), requiredEnv('VITE_SUPABASE_PUBLISHABLE_KEY'), {
    auth: { persistSession: false, autoRefreshToken: false, detectSessionInUrl: false },
  });
  return singleton;
}

/**
 * Dev flag (VITE_SHOW_PREVIEW=1): read the v_preview_* views (status = 'preview') instead of v_live_*. Unset in
 * production so the hosted site only renders live stories. Read once at module load.
 */
const showPreview = import.meta.env.VITE_SHOW_PREVIEW === '1';
const LIVE = {
  story: 'v_live_story', storyBySlug: 'v_live_story', libraryEntry: 'v_live_library_entry', moment: 'v_live_moment',
} as const;
const PREVIEW = {
  story: 'v_preview_story', storyBySlug: 'v_preview_story_by_slug', libraryEntry: 'v_preview_library_entry',
  moment: 'v_preview_moment',
} as const;
const VIEW_BY_KIND: Record<keyof typeof LIVE, string> = showPreview ? PREVIEW : LIVE;
const SET_NAME = showPreview ? 'preview' : 'live';

// Module-level memoization: one fetch per view per page load (same shape as the old getJson cache).
const memo = new Map<string, Promise<unknown>>();
function once<T>(key: string, fn: () => Promise<T>): Promise<T> {
  if (!memo.has(key)) memo.set(key, fn());
  return memo.get(key) as Promise<T>;
}

async function selectAll<T>(view: string, columns = '*'): Promise<T[]> {
  const { data, error } = await client().from(view).select(columns);
  if (error) throw new Error(`Could not read ${view} from Supabase: ${error.message}`);
  return (data ?? []) as unknown as T[];
}

// --- Row shapes (public views) -------------------------------------------------------------

interface SiteRow {
  schema_version: number;
  site_name: string;
  motto: string | null;
  tagline: string | null;
  nav_label: string | null;
  media_base_url: string | null;
  default_story_slug: string | null;
}

interface FacetRow { key: string; label: string; position: number | null; description: string | null }
interface TagRow {
  key: string; label: string; aliases: string[] | null;
  facet_key: string; facet_label: string; parent: string | null;
}

interface LiveStoryRow {
  story_slug: string;
  schema_version: number;
  document: unknown;
  library_entry: unknown;
  trust?: LibraryStory['trust'] | null;
}

interface LiveLibraryEntryRow { story_slug: string; library_entry: unknown }

interface FieldRow { slug: string; label: string; color: string | null; cluster: unknown }
interface VolumeRow { slug: string; title: string; kind: 'regular' | 'special' }
interface IssueRow {
  slug: string; number: string; title: string; color: string | null; published: string | null;
  position: number; volume_slug: string; cover_story_slug: string | null;
}
interface IssueStoryRow { issue_slug: string; story_slug: string; position: number }
interface CompanyRow {
  slug: string; name: string; sector: string | null; blurb: string | null;
  posts_followed: number | null; coming: string[] | null;
}
interface CompanyPostRow { company_slug: string; story_slug: string; position: number }
interface CompanyBuiltOnRow { company_slug: string; node_slug: string; position: number }
interface StorylineRow { slug: string; title: string }
interface StorylineStepRow {
  storyline_slug: string; position: number;
  year: string | null; label: string | null; current: boolean; story_slug: string | null;
}
interface NodeRow {
  slug: string; title: string; authors: string | null; year: number | null;
  kind: 'paper' | 'blog'; x: number | null; y: number | null;
  field_slug: string; story_slug: string | null;
  blurb: string | null; short: string | null;
}
interface RelationRow {
  source_node_slug: string; target_node_slug: string;
  kind: 'builds_on' | 'improves_on' | 'uses_method' | 'cited' | 'family';
  note: string | null;
  cited: boolean | null; cross_field: boolean | null;
}
interface FrontPlacementRow { key: string; data: Library['front'] }

// --- Memoized view readers ------------------------------------------------------------------

export const readSite = () => once('v_site', async (): Promise<SiteConfig> => {
  const { data, error } = await client()
    .from('v_site')
    .select('schema_version, site_name, motto, tagline, nav_label, media_base_url, default_story_slug')
    .maybeSingle();
  if (error) throw new Error(`Could not read v_site from Supabase: ${error.message}`);
  if (!data) throw new Error('v_site has no row.');
  const row = data as SiteRow;
  return {
    schemaVersion: 1,
    name: row.site_name,
    motto: row.motto ?? '',
    tagline: row.tagline ?? '',
    navLabel: row.nav_label ?? '',
    mediaBaseUrl: row.media_base_url ?? '',
    defaultPaper: row.default_story_slug ?? '',
    papers: [],
  };
});

export const readVocabulary = () => once('v_tag+v_facet', async (): Promise<TagVocabulary> => {
  const [facets, tags] = await Promise.all([
    selectAll<FacetRow>('v_facet', 'key, label, position, description'),
    selectAll<TagRow>('v_tag', 'key, label, aliases, facet_key, facet_label, parent'),
  ]);
  const facetsOut: FacetDef[] = facets
    .slice()
    .sort((a, b) => (a.position ?? 0) - (b.position ?? 0))
    .map(f => ({ id: f.key as TagFacet, label: f.label, description: f.description ?? '' }));
  const tagsOut: TagDef[] = tags.map(t => ({
    id: t.key,
    facet: t.facet_key as TagFacet,
    label: t.label,
    ...(t.parent ? { parent: t.parent } : {}),
    aliases: t.aliases && t.aliases.length ? t.aliases : undefined,
  }));
  return { schemaVersion: 1, facets: facetsOut, tags: tagsOut };
});

/** Fetches one live story's document. 404 if no row. Also validates the document's schemaVersion. */
export async function readLiveStoryBySlug(slug: string): Promise<PaperDoc> {
  const columns = 'schema_version, document';
  // Preview set: v_preview_story_by_slug is an RPC (argument p_slug) returning the same columns as the live view.
  const { data, error } = showPreview
    ? await client().rpc(VIEW_BY_KIND.storyBySlug, { p_slug: slug }).select(columns).maybeSingle()
    : await client().from(VIEW_BY_KIND.storyBySlug).select(columns).eq('story_slug', slug).maybeSingle();
  if (error) throw new Error(`Could not read story “${slug}” from ${VIEW_BY_KIND.storyBySlug} in Supabase: ${error.message}`);
  if (!data) throw new Error(`Story “${slug}” has no ${SET_NAME} version in Supabase.`);
  const row = data as { schema_version: number; document: unknown };
  const doc = row.document as { schemaVersion?: unknown } | null;
  if (!doc || typeof doc !== 'object') throw new Error(`Story “${slug}” in Supabase has no document.`);
  if (doc.schemaVersion !== STORY_SCHEMA_VERSION) throw new Error(storyVersionMessage(slug, doc.schemaVersion));
  if (row.schema_version !== STORY_SCHEMA_VERSION) throw new Error(storyVersionMessage(slug, row.schema_version));
  return doc as PaperDoc;
}

/** All live stories (full rows) in one fetch. Validates each document's schemaVersion. */
export const readLiveStories = () => once(VIEW_BY_KIND.story, async (): Promise<LiveStoryRow[]> => {
  const rows = await selectAll<LiveStoryRow>(VIEW_BY_KIND.story, 'story_slug, schema_version, document, library_entry, trust');
  for (const row of rows) {
    const doc = row.document as { schemaVersion?: unknown } | null;
    if (!doc || typeof doc !== 'object') throw new Error(`Story “${row.story_slug}” in Supabase has no document.`);
    if (doc.schemaVersion !== STORY_SCHEMA_VERSION) throw new Error(storyVersionMessage(row.story_slug, doc.schemaVersion));
    if (row.schema_version !== STORY_SCHEMA_VERSION) throw new Error(storyVersionMessage(row.story_slug, row.schema_version));
  }
  return rows;
});

export const readLiveLibraryEntries = () => once(VIEW_BY_KIND.libraryEntry, async (): Promise<Map<string, LibraryStory>> => {
  const rows = await selectAll<LiveLibraryEntryRow>(VIEW_BY_KIND.libraryEntry, 'story_slug, library_entry');
  const entries = new Map<string, LibraryStory>();
  for (const row of rows) {
    const entry = row.library_entry as { id?: unknown } | null;
    if (!entry || typeof entry !== 'object') throw new Error(`Live library entry for “${row.story_slug}” is not an object.`);
    if (entry.id !== row.story_slug) throw new Error(`Live library entry for “${row.story_slug}” has id “${String(entry.id)}”; they must match.`);
    if (entries.has(row.story_slug)) throw new Error(`More than one live library entry for “${row.story_slug}”.`);
    entries.set(row.story_slug, entry as LibraryStory);
  }
  return entries;
});

export const readFields = () => once('v_field', async (): Promise<LibraryField[]> => {
  const rows = await selectAll<FieldRow>('v_field', 'slug, label, color, cluster');
  return rows.map(r => ({
    id: r.slug,
    label: r.label,
    color: r.color ?? '',
    cluster: (r.cluster as LibraryField['cluster']) ?? { cx: 0, cy: 0, rx: 0, ry: 0, labelX: 0, labelY: 0 },
  }));
});

export const readVolumes = () => once('v_volume', async (): Promise<LibraryVolume[]> => {
  const rows = await selectAll<VolumeRow>('v_volume', 'slug, title, kind');
  return rows.map(r => ({ id: r.slug, title: r.title, kind: r.kind }));
});

export const readIssues = () => once('v_issue+v_issue_story', async (): Promise<LibraryIssue[]> => {
  const [issues, joins] = await Promise.all([
    selectAll<IssueRow>('v_issue', 'slug, number, title, color, published, position, volume_slug, cover_story_slug'),
    selectAll<IssueStoryRow>('v_issue_story', 'issue_slug, story_slug, position'),
  ]);
  const byIssue = new Map<string, IssueStoryRow[]>();
  for (const j of joins) {
    if (!byIssue.has(j.issue_slug)) byIssue.set(j.issue_slug, []);
    byIssue.get(j.issue_slug)!.push(j);
  }
  return issues
    .slice()
    .sort((a, b) => a.position - b.position)
    .map(i => {
      const stories = (byIssue.get(i.slug) ?? [])
        .slice()
        .sort((a, b) => a.position - b.position)
        .map(j => j.story_slug);
      return {
        id: i.slug,
        volume: i.volume_slug,
        number: i.number,
        title: i.title,
        color: i.color ?? '',
        sample: false,
        published: i.published ?? undefined,
        stories: stories.length ? stories : undefined,
        covers: i.cover_story_slug ?? undefined,
      };
    });
});

export const readCompanies = () => once('v_company+posts+builtOn', async (): Promise<LibraryCompany[]> => {
  const [companies, posts, builtOn] = await Promise.all([
    selectAll<CompanyRow>('v_company', 'slug, name, sector, blurb, posts_followed, coming'),
    selectAll<CompanyPostRow>('v_company_post', 'company_slug, story_slug, position'),
    selectAll<CompanyBuiltOnRow>('v_company_built_on', 'company_slug, node_slug, position'),
  ]);
  const postsByCompany = new Map<string, CompanyPostRow[]>();
  for (const p of posts) {
    if (!postsByCompany.has(p.company_slug)) postsByCompany.set(p.company_slug, []);
    postsByCompany.get(p.company_slug)!.push(p);
  }
  const builtByCompany = new Map<string, CompanyBuiltOnRow[]>();
  for (const b of builtOn) {
    if (!builtByCompany.has(b.company_slug)) builtByCompany.set(b.company_slug, []);
    builtByCompany.get(b.company_slug)!.push(b);
  }
  return companies.map(c => ({
    id: c.slug,
    name: c.name,
    sector: c.sector ?? '',
    blurb: c.blurb ?? '',
    postsFollowed: c.posts_followed ?? 0,
    posts: (postsByCompany.get(c.slug) ?? []).slice().sort((a, b) => a.position - b.position).map(p => p.story_slug),
    builtOn: (builtByCompany.get(c.slug) ?? []).slice().sort((a, b) => a.position - b.position).map(b => b.node_slug),
    coming: c.coming ?? [],
  }));
});

export const readStorylines = () => once('v_storyline+steps', async (): Promise<Storyline[]> => {
  const [lines, steps] = await Promise.all([
    selectAll<StorylineRow>('v_storyline', 'slug, title'),
    selectAll<StorylineStepRow>('v_storyline_step', 'storyline_slug, position, year, label, current, story_slug'),
  ]);
  const byLine = new Map<string, StorylineStepRow[]>();
  for (const s of steps) {
    if (!byLine.has(s.storyline_slug)) byLine.set(s.storyline_slug, []);
    byLine.get(s.storyline_slug)!.push(s);
  }
  return lines.map(l => ({
    id: l.slug,
    title: l.title,
    sample: false,
    steps: (byLine.get(l.slug) ?? [])
      .slice()
      .sort((a, b) => a.position - b.position)
      .map(st => ({
        year: st.year ?? '',
        label: st.label ?? '',
        ...(st.current ? { current: true } : {}),
      })),
  }));
});

export const readNodes = () => once('v_node', async (): Promise<GraphNode[]> => {
  const rows = await selectAll<NodeRow>('v_node', 'slug, title, authors, year, kind, x, y, field_slug, story_slug, blurb, short');
  return rows.map(r => ({
    id: r.slug,
    title: r.title,
    authors: r.authors ?? '',
    year: r.year ?? 0,
    field: r.field_slug,
    type: r.kind,
    x: r.x ?? 0,
    y: r.y ?? 0,
    ...(r.story_slug ? { story: r.story_slug } : {}),
    ...(r.short ? { short: r.short } : {}),
    ...(r.blurb ? { blurb: r.blurb } : {}),
  }));
});

export const readRelations = () => once('v_relation', async (): Promise<GraphRelation[]> => {
  const rows = await selectAll<RelationRow>('v_relation', 'source_node_slug, target_node_slug, kind, note, cited, cross_field');
  // The frontend GraphRelation.kind is narrower than v_relation.kind; the extra kinds (`cited`, `family`) are not
  // consumed by any current UI. Pass them through unchanged — unknown kinds fall through the kind-specific labels.
  return rows.map(r => ({
    from: r.source_node_slug,
    to: r.target_node_slug,
    kind: r.kind as GraphRelation['kind'],
    note: r.note ?? '',
    ...(r.cited ? { cited: true } : {}),
    ...(r.cross_field ? { crossField: true } : {}),
  }));
});

export const readFront = () => once('v_front_placement', async (): Promise<Library['front']> => {
  const { data, error } = await client().from('v_front_placement').select('key, data').eq('key', 'current').maybeSingle();
  if (error) throw new Error(`Could not read v_front_placement from Supabase: ${error.message}`);
  if (!data) throw new Error('v_front_placement has no "current" row.');
  return (data as FrontPlacementRow).data;
});

/** Exposed so loadArchive can parallelize the editorial fetches together with v_live_moment. */
export const readLiveMoments = () => once(VIEW_BY_KIND.moment, () =>
  selectAll<{
    story_slug: string; key: string; kind: 'lead' | 'hook' | 'chapter' | 'strip_panel' | 'fact';
    position: number | null; claim: string | null; trust: LibraryStory['trust'] | null;
    source_label: string | null; source_url: string | null; media_path: string | null;
    headline: string | null; text: string | null; ref: string | null;
  }>(VIEW_BY_KIND.moment, 'story_slug, key, kind, position, claim, trust, source_label, source_url, media_path, headline, text, ref'),
);
