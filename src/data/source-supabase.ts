// The Supabase source (decisions 48, 49). Browser-side: uses only the URL and the publishable key. Reads go through the
// public views v_live_story and v_live_library_entry, which filter status = 'live' and sample = false. Never read a service-role key here.

import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import { STORY_SCHEMA_VERSION, storyVersionMessage, type LibraryStory, type PaperDoc } from '../types';
import type { StoryDataSource } from './source';

/** Row shape of the public read `v_live_story` (decision 49). */
interface LiveDocRow {
  schema_version: number;
  document: unknown;
}

interface LiveLibraryRow {
  story_slug: string;
  library_entry: unknown;
}

function requiredEnv(name: 'VITE_SUPABASE_URL' | 'VITE_SUPABASE_PUBLISHABLE_KEY'): string {
  const value = ((import.meta.env[name] as string | undefined) ?? '').trim();
  if (!value) {
    throw new Error(`VITE_DATA_SOURCE is "supabase" but ${name} is not set. Add it to .env (see .env.example), or use VITE_DATA_SOURCE=file.`);
  }
  return value;
}

/** GET v_live_story WHERE story_slug = <slug>. At most one live row per story (DB-enforced). */
async function readLiveDoc(client: SupabaseClient, slug: string): Promise<PaperDoc> {
  const { data, error } = await client
    .from('v_live_story')
    .select('schema_version, document')
    .eq('story_slug', slug)
    .maybeSingle();
  if (error) throw new Error(`Could not read story “${slug}” from Supabase: ${error.message}`);
  if (!data) throw new Error(`Story “${slug}” has no live version in Supabase.`);

  const row = data as LiveDocRow;
  const doc = row.document as { schemaVersion?: unknown } | null;
  if (!doc || typeof doc !== 'object') throw new Error(`Story “${slug}” in Supabase has no document.`);
  if (doc.schemaVersion !== STORY_SCHEMA_VERSION) throw new Error(storyVersionMessage(slug, doc.schemaVersion));
  if (row.schema_version !== STORY_SCHEMA_VERSION) throw new Error(storyVersionMessage(slug, row.schema_version));
  return doc as PaperDoc;
}

/** GET v_live_library_entry (story_slug, library_entry). Same set of rows as v_live_story. */
async function readLiveLibrary(client: SupabaseClient): Promise<Map<string, LibraryStory>> {
  const { data, error } = await client
    .from('v_live_library_entry')
    .select('story_slug, library_entry');
  if (error) throw new Error(`Could not read live library entries from Supabase: ${error.message}`);

  const entries = new Map<string, LibraryStory>();
  for (const row of (data ?? []) as LiveLibraryRow[]) {
    const entry = row.library_entry as { id?: unknown } | null;
    if (!entry || typeof entry !== 'object') throw new Error(`Live library entry for “${row.story_slug}” is not an object.`);
    if (entry.id !== row.story_slug) throw new Error(`Live library entry for “${row.story_slug}” has id “${String(entry.id)}”; they must match.`);
    if (entries.has(row.story_slug)) throw new Error(`More than one live library entry for “${row.story_slug}”.`);
    entries.set(row.story_slug, entry as LibraryStory);
  }
  return entries;
}

/** Creates the Supabase source. Throws if VITE_SUPABASE_URL or VITE_SUPABASE_PUBLISHABLE_KEY is missing. */
export function createSupabaseSource(): StoryDataSource {
  const client = createClient(requiredEnv('VITE_SUPABASE_URL'), requiredEnv('VITE_SUPABASE_PUBLISHABLE_KEY'), {
    auth: { persistSession: false, autoRefreshToken: false, detectSessionInUrl: false },
  });

  // One read per slug and one for the library per page load, mirroring the JSON cache. Failures are cached too.
  const docs = new Map<string, Promise<PaperDoc>>();
  let library: Promise<Map<string, LibraryStory>> | undefined;

  return {
    name: 'supabase',
    fetchStoryDoc(slug) {
      let doc = docs.get(slug);
      if (!doc) {
        doc = readLiveDoc(client, slug);
        docs.set(slug, doc);
      }
      return doc;
    },
    fetchLiveLibraryEntries() {
      library ??= readLiveLibrary(client);
      return library;
    },
  };
}
