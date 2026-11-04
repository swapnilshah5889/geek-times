import type { Library, PaperDoc, SearchIndex, SiteConfig, TagVocabulary } from '../types';

const BASE = new URL(import.meta.env.BASE_URL, window.location.origin);

/** Resolves a path against the app's base URL (absolute URLs pass through). */
export function appUrl(path: string): string {
  return new URL(path, BASE).href;
}

const cache = new Map<string, Promise<unknown>>();

/** Fetches a versioned JSON document once per page load. */
function getJson<T extends { schemaVersion?: number }>(url: string): Promise<T> {
  if (!cache.has(url)) {
    cache.set(url, fetch(appUrl(url)).then(async res => {
      if (!res.ok) throw new Error(`Could not load ${url} (${res.status})`);
      const doc = (await res.json()) as T;
      if (doc.schemaVersion !== 1) throw new Error(`${url} uses schema version ${doc.schemaVersion}; this page reads version 1.`);
      return doc;
    }));
  }
  return cache.get(url) as Promise<T>;
}

/** A deployment can point media at a CDN without touching the data. */
export function mediaBaseFor(site: SiteConfig): string {
  return appUrl(import.meta.env.VITE_MEDIA_BASE_URL || site.mediaBaseUrl);
}

export const loadSite = () => getJson<SiteConfig>('data/site.json');
export const loadVocabulary = () => getJson<TagVocabulary>('data/tags.json');
export const loadLibrary = () => getJson<Library>('data/library.json');
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
  const doc = await getJson<PaperDoc>(entry.dataUrl);
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
