// The data layer. Every read goes through Supabase views (decision 48; runtime cutover, 2026-11-07).
// The Archive shape stays what the UI already consumes; `src/lib/*` sync helpers work against it in memory.

import {
  type Block, type Cover, type Library, type LibraryStory, type Moment, type PaperDoc,
  type SearchEntry, type SearchIndex, type SiteConfig, type StoryDoc, type TagVocabulary,
} from '../types';
import { appUrl } from './fetch-json';
import {
  readCompanies, readFields, readFront, readIssues, readLiveLibraryEntries, readLiveMoments,
  readLiveStories, readLiveStoryBySlug, readNodes, readRelations, readSite, readStorylines,
  readVocabulary, readVolumes,
} from './source';

export { appUrl };

/** A deployment can point media at a CDN without touching the data. */
export function mediaBaseFor(site: SiteConfig): string {
  return appUrl(import.meta.env.VITE_MEDIA_BASE_URL || site.mediaBaseUrl);
}

export const loadSite = (): Promise<SiteConfig> => readSite();
export const loadVocabulary = (): Promise<TagVocabulary> => readVocabulary();

export interface Edition {
  site: SiteConfig;
  doc: PaperDoc;
  vocab: TagVocabulary;
  mediaBaseUrl: string;
}

export interface Archive {
  site: SiteConfig;
  vocab: TagVocabulary;
  index: SearchIndex;
  library: Library;
}

/** Loads the site settings and the requested story. 404 if the slug has no live row. */
export async function loadEdition(slug: string | null): Promise<Edition> {
  const [site, vocab] = await Promise.all([loadSite(), loadVocabulary()]);
  const wanted = slug ?? site.defaultPaper;
  const doc = await readLiveStoryBySlug(wanted);
  return { site, doc, vocab, mediaBaseUrl: mediaBaseFor(site) };
}

/** Keeps its signature for callers; delegates to loadArchive (memoized view reads make this cheap). */
export async function loadLibrary(): Promise<Library> {
  return (await loadArchive()).library;
}

/** Builds SearchEntry[] from v_live_story. Moments come from v_live_moment, merged by slug. */
function buildSearchEntry(row: {
  story_slug: string; document: unknown;
}, momentsByStory: Map<string, Moment[]>): SearchEntry {
  const doc = row.document as StoryDoc;
  const source = doc.kind === 'blog' ? doc.blog : doc.paper;
  const cover = coverOf(doc);
  const moments = momentsByStory.get(row.story_slug) ?? [];
  return {
    slug: doc.slug,
    title: source.title,
    pageTitle: doc.pageTitle,
    summary: doc.summary,
    authors: doc.kind === 'blog' ? doc.blog.organization : doc.paper.authors,
    year: doc.kind === 'blog' ? Number(doc.blog.published.slice(0, 4)) || 0 : doc.paper.year,
    desk: doc.desk,
    cover,
    moments,
    tags: (doc.tags ?? [])
      .filter(t => t.status === 'approved')
      .map(t => ({ id: t.tag, relevance: t.relevance })),
  };
}

/** Same rule as the former scripts/build-index.ts: the paper's cover, or the lead block's first slide. */
function coverOf(doc: StoryDoc): Cover {
  if (doc.cover) {
    const hook = doc.hook ?? doc.cover.hook;
    return hook ? { ...doc.cover, hook } : doc.cover;
  }
  const lead = doc.blocks.find((b): b is Extract<Block, { type: 'lead' }> => b.type === 'lead');
  if (!lead) throw new Error(`Story “${doc.slug}” has no cover and no lead block.`);
  const base: Cover = { kicker: lead.kicker, headline: lead.headline, dek: lead.deck, media: lead.slideshow.slides[0].media };
  return doc.hook ? { ...base, hook: doc.hook } : base;
}

const PROVENANCE_OF = {
  illustration: 'illustration',
  model_design: 'model_design',
  measured_result: 'evidence',
} as const;

/** Reconstructs the Moment[] shape from the moment rows (v_live_moment). Kicker is re-derived. */
function momentsFromRows(storyKind: 'paper' | 'blog' | 'classic', rows: Array<{
  key: string; kind: 'lead' | 'hook' | 'chapter' | 'strip_panel' | 'fact';
  position: number | null; claim: string | null; trust: LibraryStory['trust'] | null;
  source_label: string | null; media_path: string | null;
  headline: string | null; text: string | null; ref: string | null;
}>, storySlug: string): Moment[] {
  // Keep only kinds the frontend renders (strip, chapter, fact). Lead/hook moments inform the cover, not the feed.
  const out: Moment[] = [];
  const link = (anchor?: string) => `papers/${storySlug}${anchor ? `#${anchor}` : ''}`;
  const sorted = rows.slice().sort((a, b) => (a.position ?? 0) - (b.position ?? 0));
  // Number strip panels per strip (by ref) so the kicker label matches build-index's "How it works · 01".
  const stripNumbers = new Map<string, number>();
  let stripCounter = 0;
  for (const r of sorted) if (r.kind === 'strip_panel' && r.ref && !stripNumbers.has(r.ref)) {
    stripNumbers.set(r.ref, ++stripCounter);
  }
  for (const r of sorted) {
    if (r.kind === 'lead' || r.kind === 'hook') continue;
    const claim = (r.claim as Moment['claim']) ?? undefined;
    const provenance = claim ? PROVENANCE_OF[claim] : undefined;
    const media = r.media_path ? { type: 'svg' as const, src: r.media_path } : undefined;
    const trust = r.trust ?? undefined;
    if (r.kind === 'chapter') {
      out.push({
        id: r.key, paper: storySlug, kind: 'chapter',
        kicker: r.ref ?? '', title: r.headline ?? '', text: r.text ?? '',
        media, provenance, trust, href: link(r.key),
      });
    } else if (r.kind === 'strip_panel') {
      const n = (r.ref && stripNumbers.get(r.ref)) ?? 0;
      out.push({
        id: r.key, paper: storySlug, kind: 'strip',
        kicker: `How it works · ${String(n).padStart(2, '0')}`,
        title: r.headline ?? '', text: r.text ?? '',
        media, provenance, trust, href: link(r.ref ?? r.key),
      });
    } else {
      out.push({
        id: r.key, paper: storySlug, kind: 'fact',
        kicker: storyKind === 'blog' ? 'From the post' : 'From the paper',
        title: r.headline ?? '', figure: r.headline ?? '',
        text: r.text ?? '', media, claim, provenance, trust,
        sourceLabel: r.source_label ?? undefined, href: link(r.ref ?? r.key),
      });
    }
  }
  return out;
}

export async function loadSearchIndex(): Promise<SearchIndex> {
  const [stories, moments, site] = await Promise.all([readLiveStories(), readLiveMoments(), loadSite()]);
  const byStory = new Map<string, Moment[]>();
  const kindBySlug = new Map<string, 'paper' | 'blog' | 'classic'>();
  for (const s of stories) {
    const d = s.document as StoryDoc;
    kindBySlug.set(s.story_slug, (d.kind ?? 'paper') as 'paper' | 'blog' | 'classic');
  }
  const grouped = new Map<string, Parameters<typeof momentsFromRows>[1]>();
  for (const row of moments) {
    if (!grouped.has(row.story_slug)) grouped.set(row.story_slug, []);
    grouped.get(row.story_slug)!.push(row);
  }
  for (const [slug, rows] of grouped) byStory.set(slug, momentsFromRows(kindBySlug.get(slug) ?? 'paper', rows, slug));
  const papers = stories.map(s => buildSearchEntry(s, byStory));
  return { schemaVersion: 1, featured: site.defaultPaper, papers };
}

export async function loadArchive(): Promise<Archive> {
  const [
    site, vocab,
    liveStories, liveMoments, liveLibrary,
    fields, volumes, issues, companies, storylines, nodes, relations, front,
  ] = await Promise.all([
    loadSite(),
    loadVocabulary(),
    readLiveStories(),
    readLiveMoments(),
    readLiveLibraryEntries(),
    readFields(),
    readVolumes(),
    readIssues(),
    readCompanies(),
    readStorylines(),
    readNodes(),
    readRelations(),
    readFront(),
  ]);

  // --- SearchIndex (built from the full live story rows + moment rows) ---
  const kindBySlug = new Map<string, 'paper' | 'blog' | 'classic'>();
  for (const s of liveStories) {
    const d = s.document as StoryDoc;
    kindBySlug.set(s.story_slug, (d.kind ?? 'paper') as 'paper' | 'blog' | 'classic');
  }
  const momentRowsByStory = new Map<string, Parameters<typeof momentsFromRows>[1]>();
  for (const row of liveMoments) {
    if (!momentRowsByStory.has(row.story_slug)) momentRowsByStory.set(row.story_slug, []);
    momentRowsByStory.get(row.story_slug)!.push(row);
  }
  const momentsByStory = new Map<string, Moment[]>();
  for (const [slug, rows] of momentRowsByStory) {
    momentsByStory.set(slug, momentsFromRows(kindBySlug.get(slug) ?? 'paper', rows, slug));
  }
  const papers = liveStories.map(s => buildSearchEntry(s, momentsByStory));
  const index: SearchIndex = { schemaVersion: 1, featured: site.defaultPaper, papers };

  // --- Library (live-entry overlay for the story content; editorial tables supply issues, companies, map, front) ---
  const stories: LibraryStory[] = Array.from(liveLibrary.values());
  const library: Library = {
    schemaVersion: 1,
    fields, volumes, stories,
    front: deriveFront(stories, fields, site, front),
    issues, companies, storylines, nodes, relations,
  };

  return { site, vocab, index, library };
}

/**
 * Builds the front-page slots from the live stories so a newly published paper surfaces on the next load
 * without hand-editing any JSON. Curated bits that need human judgement (storylines, vault, onThisDay) are
 * taken from the DB-stored `front_placement` row as-is.
 *
 * Rules:
 *  - `lead`: site.defaultPaper if that slug is live; else the newest story.
 *  - `aside`: up to 3 other stories, newest first.
 *  - `more`: the rest of the stories, newest first.
 *  - `topics`: one row per field that has at least one live story in it, newest-first within each row.
 *  - `real`: every story (they are all real; the view filters samples out).
 */
function deriveFront(
  stories: LibraryStory[],
  fields: Library['fields'],
  site: SiteConfig,
  stored: Library['front'],
): Library['front'] {
  const byNewest = stories.slice().sort((a, b) => (b.year ?? 0) - (a.year ?? 0));
  const slugs = new Set(byNewest.map(s => s.id));
  const lead = slugs.has(site.defaultPaper) ? site.defaultPaper : (byNewest[0]?.id ?? '');
  const rest = byNewest.filter(s => s.id !== lead).map(s => s.id);
  const aside = rest.slice(0, 3);
  const more = rest.slice(3);

  const labelByField = new Map(fields.map(f => [f.id, f.label]));
  const groupsByField = new Map<string, string[]>();
  for (const story of byNewest) {
    const field = story.fields?.[0];
    if (!field) continue;
    if (!groupsByField.has(field)) groupsByField.set(field, []);
    groupsByField.get(field)!.push(story.id);
  }
  const topics = fields
    .filter(f => groupsByField.has(f.id))
    .map(f => ({ field: f.id, label: labelByField.get(f.id) ?? f.id, stories: groupsByField.get(f.id)! }));

  return {
    lead,
    aside,
    more,
    topics,
    real: byNewest.map(s => s.id),
    storylines: stored.storylines,
    vault: stored.vault,
    onThisDay: stored.onThisDay,
  };
}
