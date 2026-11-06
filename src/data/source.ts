// The data-source boundary (decision 48). Story documents and live library entries come from either the JSON files
// (default) or Supabase (VITE_DATA_SOURCE=supabase). There is no fallback between them: a Supabase failure is an error.

import { STORY_SCHEMA_VERSION, storyVersionMessage, type LibraryStory, type PaperDoc, type SiteConfig } from '../types';
import { getJson } from './fetch-json';
import { createSupabaseSource } from './source-supabase';

export { createSupabaseSource } from './source-supabase';

export interface StoryDataSource {
  readonly name: 'file' | 'supabase';
  /** The story document for a published slug. Rejects if the slug is unknown, unpublished, or at another schemaVersion. */
  fetchStoryDoc(slug: string): Promise<PaperDoc>;
  /** Live library entries keyed by slug. The file source returns an empty Map (no overlay). */
  fetchLiveLibraryEntries(): Promise<Map<string, LibraryStory>>;
}

/** Reads the story from public/data/papers/<slug>.json, as listed in site.json. */
export function createFileSource(): StoryDataSource {
  return {
    name: 'file',
    async fetchStoryDoc(slug) {
      const site = await getJson<SiteConfig>('data/site.json');
      const entry = site.papers.find(p => p.slug === slug);
      if (!entry) throw new Error(`No paper called “${slug}”.`);
      return getJson<PaperDoc>(entry.dataUrl, STORY_SCHEMA_VERSION, found => storyVersionMessage(slug, found));
    },
    async fetchLiveLibraryEntries() {
      return new Map();
    },
  };
}

let active: StoryDataSource | undefined;

/** Chooses the source from VITE_DATA_SOURCE: "file" (default when unset) or "supabase". Any other value throws. */
export function pickSource(): StoryDataSource {
  if (active) return active;
  const mode = ((import.meta.env.VITE_DATA_SOURCE as string | undefined) ?? '').trim() || 'file';
  if (mode === 'file') active = createFileSource();
  else if (mode === 'supabase') active = createSupabaseSource();
  else throw new Error(`VITE_DATA_SOURCE must be "file" or "supabase", not "${mode}".`);
  return active;
}
