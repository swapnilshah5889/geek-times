import type { PaperDoc, SiteConfig } from '../types';

const BASE = new URL(import.meta.env.BASE_URL, window.location.origin);

/** Resolves a path against the app's base URL (absolute URLs pass through). */
export function appUrl(path: string): string {
  return new URL(path, BASE).href;
}

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(appUrl(url));
  if (!res.ok) throw new Error(`Could not load ${url} (${res.status})`);
  return (await res.json()) as T;
}

function checkVersion(doc: { schemaVersion?: number }, what: string) {
  if (doc.schemaVersion !== 1) throw new Error(`${what} uses schema version ${doc.schemaVersion}; this page reads version 1.`);
}

export interface Edition {
  site: SiteConfig;
  doc: PaperDoc;
  mediaBaseUrl: string;
}

/** Loads the site settings and the requested paper (?paper=<slug>, else the default). */
export async function loadEdition(slug: string | null): Promise<Edition> {
  const site = await getJson<SiteConfig>('data/site.json');
  checkVersion(site, 'site.json');
  const wanted = slug ?? site.defaultPaper;
  const entry = site.papers.find(p => p.slug === wanted);
  if (!entry) throw new Error(`No paper called “${wanted}”.`);
  const doc = await getJson<PaperDoc>(entry.dataUrl);
  checkVersion(doc, entry.dataUrl);
  // A deployment can point media at a CDN without touching the data.
  const mediaBaseUrl = appUrl(import.meta.env.VITE_MEDIA_BASE_URL || site.mediaBaseUrl);
  return { site, doc, mediaBaseUrl };
}
