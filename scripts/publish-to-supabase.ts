// Seed + atomic publish for one story (decision 42, 48). Server-side only: uses the service-role key,
// which bypasses RLS. Never import this from the browser. Run with:
//
//   npm run publish:supabase -- <slug>
//
// It reads public/data/papers/<slug>.json and the matching entry in public/data/library.json, stages a
// published_version row, then calls the publish_version(bigint) SQL function to promote it in one transaction.

import { createClient } from '@supabase/supabase-js';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

interface PaperDocLike { schemaVersion?: number; kind?: 'paper' | 'blog'; slug?: string }
interface LibraryStoryLike { id: string }

function die(msg: string): never {
  console.error(msg);
  process.exit(1);
}

const slug = process.argv[2]?.trim();
if (!slug) die('usage: npm run publish:supabase -- <slug>');

const url = process.env.VITE_SUPABASE_URL?.trim();
const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY?.trim();
if (!url) die('VITE_SUPABASE_URL is not set. Copy .env.example to .env and fill it in.');
if (!serviceKey) die('SUPABASE_SERVICE_ROLE_KEY is not set. Copy .env.example to .env and fill it in.');
if (serviceKey.startsWith('eyJ') === false) die('SUPABASE_SERVICE_ROLE_KEY does not look like a JWT. Check the value.');

// Show which project we're hitting so the owner can confirm before anything writes.
console.log(`Target: ${new URL(url).hostname}`);

const admin = createClient(url, serviceKey, { auth: { persistSession: false, autoRefreshToken: false } });

const docPath = resolve('public/data/papers', `${slug}.json`);
const doc = JSON.parse(await readFile(docPath, 'utf8')) as PaperDocLike;
if (doc.schemaVersion !== 2) die(`${slug} is schemaVersion ${String(doc.schemaVersion)}; need 2 (decision 46).`);

const libraryPath = resolve('public/data/library.json');
const library = JSON.parse(await readFile(libraryPath, 'utf8')) as { stories: LibraryStoryLike[] };
const entry = library.stories.find(s => s.id === slug);
if (!entry) die(`No library entry for “${slug}” in library.json. The front-page card needs one.`);

const kind = doc.kind ?? 'paper';

// Upsert the story row by slug. If it exists we only rewrite the columns passed in; live_version_id is
// untouched (publish_version flips it after the promote).
const { data: story, error: storyErr } = await admin
  .from('story')
  .upsert({ slug, kind }, { onConflict: 'slug' })
  .select('id')
  .single();
if (storyErr || !story) die(`story upsert failed: ${storyErr?.message ?? 'no row returned'}`);
console.log(`Story id ${String(story.id)} (${slug}, kind=${kind})`);

// Stage a new version. RLS does not block the service-role key.
const { data: version, error: verErr } = await admin
  .from('published_version')
  .insert({
    story_id: story.id,
    story_slug: slug,
    schema_version: doc.schemaVersion,
    status: 'staging',
    document: doc,
    library_entry: entry,
  })
  .select('id')
  .single();
if (verErr || !version) die(`version insert failed: ${verErr?.message ?? 'no row returned'}`);
console.log(`Staged version ${String(version.id)}`);

// Promote atomically. The function retires the current live row, flips this one to live, and points the story at it.
const { error: promoteErr } = await admin.rpc('publish_version', { p_version_id: version.id });
if (promoteErr) die(`publish_version failed: ${promoteErr.message}`);

console.log(`Published ${slug} as version ${String(version.id)}`);
