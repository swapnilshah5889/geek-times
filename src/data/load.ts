import { type Library, type LibraryStory, type PaperDoc, type SearchIndex, type SiteConfig, type TagVocabulary } from '../types';
import { appUrl, getJson } from './fetch-json';
import { pickSource } from './source';

export { appUrl };

/** A deployment can point media at a CDN without touching the data. */
export function mediaBaseFor(site: SiteConfig): string {
  return appUrl(import.meta.env.VITE_MEDIA_BASE_URL || site.mediaBaseUrl);
}

export const loadSite = () => getJson<SiteConfig>('data/site.json');
export const loadVocabulary = () => getJson<TagVocabulary>('data/tags.json');
/**
 * Build flag VITE_HIDE_SAMPLES=1: removes every sample:true item and every reference to a removed id.
 * Returns new objects; the cached document is never mutated.
 */
function hideSamples(lib: Library): Library {
  const stories = lib.stories.filter(s => !s.sample);
  const storyIds = new Set(stories.map(s => s.id));
  const firstStory = stories[0]?.id ?? '';
  const keepStories = (ids: string[]) => ids.filter(id => storyIds.has(id));
  const storylines = lib.storylines.filter(s => !s.sample);
  const storylineIds = new Set(storylines.map(s => s.id));
  const nodes = lib.nodes
    .filter(n => !n.sample)
    .map(n => ({ ...n, story: n.story && storyIds.has(n.story) ? n.story : undefined }));
  const nodeIds = new Set(nodes.map(n => n.id));
  const { front } = lib;

  return {
    ...lib,
    stories,
    front: {
      ...front,
      lead: storyIds.has(front.lead) ? front.lead : firstStory,
      aside: keepStories(front.aside),
      more: keepStories(front.more),
      topics: front.topics.map(t => ({ ...t, stories: keepStories(t.stories) })),
      real: keepStories(front.real),
      storylines: front.storylines.filter(id => storylineIds.has(id)),
      vault: storyIds.has(front.vault) ? front.vault : '',
      onThisDay: { ...front.onThisDay, story: storyIds.has(front.onThisDay.story) ? front.onThisDay.story : firstStory },
    },
    issues: lib.issues
      .filter(i => !i.sample)
      .map(i => ({
        ...i,
        stories: i.stories && keepStories(i.stories),
        covers: i.covers && storyIds.has(i.covers) ? i.covers : undefined,
      })),
    companies: lib.companies
      .filter(c => !c.sample)
      .map(c => ({
        ...c,
        posts: keepStories(c.posts),
        builtOn: c.builtOn.filter(id => nodeIds.has(id)),
      })),
    storylines,
    nodes,
    relations: lib.relations.filter(r => !r.sample && nodeIds.has(r.from) && nodeIds.has(r.to)),
  };
}

/**
 * Replaces each shell story whose id matches a live library entry (the file source has none, so this is a no-op there).
 * A live entry with no matching shell story is appended to `stories`; the front-page layout slots still come from the shell.
 */
function overlayLive(lib: Library, live: Map<string, LibraryStory>): Library {
  if (live.size === 0) return lib;
  const placed = new Set<string>();
  const stories = lib.stories.map(s => {
    const entry = live.get(s.id);
    if (!entry) return s;
    placed.add(s.id);
    return entry;
  });
  for (const [slug, entry] of live) if (!placed.has(slug)) stories.push(entry);
  return { ...lib, stories };
}

export async function loadLibrary(): Promise<Library> {
  const [lib, live] = await Promise.all([getJson<Library>('data/library.json'), pickSource().fetchLiveLibraryEntries()]);
  const merged = overlayLive(lib, live);
  return import.meta.env.VITE_HIDE_SAMPLES === '1' ? hideSamples(merged) : merged;
}

export const loadSearchIndex = () => getJson<SearchIndex>('data/search-index.json');

export interface Edition {
  site: SiteConfig;
  doc: PaperDoc;
  vocab: TagVocabulary;
  mediaBaseUrl: string;
}

/** Loads the site settings and the requested paper (/papers/<slug>, else the default). */
export async function loadEdition(slug: string | null): Promise<Edition> {
  const [site, vocab] = await Promise.all([loadSite(), loadVocabulary()]);
  const wanted = slug ?? site.defaultPaper;
  const entry = site.papers.find(p => p.slug === wanted);
  if (!entry) throw new Error(`No paper called “${wanted}”.`);
  const doc = await pickSource().fetchStoryDoc(entry.slug);
  return { site, doc, vocab, mediaBaseUrl: mediaBaseFor(site) };
}

export interface Archive {
  site: SiteConfig;
  vocab: TagVocabulary;
  index: SearchIndex;
  library: Library;
}

export async function loadArchive(): Promise<Archive> {
  const [site, vocab, index, library] = await Promise.all([loadSite(), loadVocabulary(), loadSearchIndex(), loadLibrary()]);
  return { site, vocab, index, library };
}
