// Supabase Storage media sync for the cloud-only V1 gate. Server-side only; never bundled into the site.
//
// Maps every file under public/media/<story>/... to the object key with the same relative path in a public-read
// bucket (default "story-media", override with SUPABASE_MEDIA_BUCKET). Story documents already store media as
// relative paths such as "attention-is-all-you-need/comic/01a-letters.svg", so the public URL is
// <media_base_url><src>, where media_base_url = <SUPABASE_URL>/storage/v1/object/public/<bucket>/ (trailing slash
// required, because MediaView resolves src with new URL(src, base)).
//
// Modes:
//   upload  Writes objects to Storage only. Idempotent: objects already present with the same byte size are skipped
//           (use --force to re-upload everything). --dry-run prints the plan and writes nothing.
//           Needs SUPABASE_URL (or VITE_SUPABASE_URL) and SUPABASE_SERVICE_ROLE_KEY.
//   verify  Read-only. Enumerates media referenced by v_live_story documents and v_live_moment.media_path, then
//           HEAD-checks each public URL. Reports missing paths and warns when an SVG lacks CORS headers.
//           Never writes to the database or Storage. Needs SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY.
//
// Usage (see docs/handoffs/claude-v1-cloud-only-merge-gate.md for the npm wiring):
//   node --experimental-strip-types --disable-warning=ExperimentalWarning --env-file=.env scripts/media-storage.ts upload [--dry-run] [--force]
//   node --experimental-strip-types --disable-warning=ExperimentalWarning --env-file=.env scripts/media-storage.ts verify

import { readdir, readFile, stat } from 'node:fs/promises';
import { join, posix } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createClient, type SupabaseClient } from '@supabase/supabase-js';

const ROOT = fileURLToPath(new URL('..', import.meta.url));
const MEDIA_DIR = join(ROOT, 'public', 'media');
const BUCKET = (process.env.SUPABASE_MEDIA_BUCKET ?? '').trim() || 'story-media';
const LIST_PAGE = 1000;
const READ_PAGE = 1000;
const CONCURRENCY = 8;

const CONTENT_TYPES: Record<string, string> = {
  svg: 'image/svg+xml', png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', gif: 'image/gif',
  webp: 'image/webp', mp4: 'video/mp4', webm: 'video/webm', json: 'application/json',
};

const AUTH_OPTS = { auth: { persistSession: false, autoRefreshToken: false, detectSessionInUrl: false } } as const;

function die(msg: string): never {
  console.error(msg);
  process.exit(1);
}

function env(name: string): string | undefined {
  const value = process.env[name]?.trim();
  return value ? value : undefined;
}

function projectUrl(): string {
  // SUPABASE_URL is the server-side name; VITE_SUPABASE_URL is the same public project URL and is what .env holds today.
  const url = env('SUPABASE_URL') ?? env('VITE_SUPABASE_URL');
  if (!url) die('SUPABASE_URL is not set (VITE_SUPABASE_URL also accepted). Add it to .env (see .env.example).');
  return url.replace(/\/+$/, '');
}

/** Public base for the bucket. Store this value (with its trailing slash) in site_settings.media_base_url. */
function mediaBaseUrl(url: string): string {
  return `${url}/storage/v1/object/public/${BUCKET}/`;
}

/** Public URL of one object. Each path segment is encoded so names with spaces or symbols still resolve. */
function publicUrlFor(url: string, key: string): string {
  return mediaBaseUrl(url) + key.split('/').map(encodeURIComponent).join('/');
}

function contentTypeFor(key: string): string {
  const ext = key.slice(key.lastIndexOf('.') + 1).toLowerCase();
  return CONTENT_TYPES[ext] ?? 'application/octet-stream';
}

async function localFiles(dir: string, prefix = ''): Promise<{ key: string; abs: string }[]> {
  const out: { key: string; abs: string }[] = [];
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    if (entry.name.startsWith('.')) continue;
    const abs = join(dir, entry.name);
    const key = prefix ? `${prefix}/${entry.name}` : entry.name;
    if (entry.isDirectory()) out.push(...(await localFiles(abs, key)));
    else if (entry.isFile()) out.push({ key, abs });
  }
  return out.sort((a, b) => (a.key < b.key ? -1 : a.key > b.key ? 1 : 0));
}

/**
 * Maps a `src`/`poster` string from a story document to an object key. Returns null for absolute URLs (external,
 * not ours to check) and undefined for paths that cannot be resolved inside the bucket.
 */
function keyForMediaSrc(raw: string): string | null | undefined {
  if (/^[a-z][a-z0-9+.-]*:/i.test(raw) || raw.startsWith('//')) return null;
  if (raw.startsWith('/')) return undefined;
  const key = posix.normalize(raw.replace(/^\.\//, ''));
  if (key === '.' || key === '..' || key.startsWith('../')) return undefined;
  return key;
}

const MEDIA_TYPES = new Set(['svg', 'image', 'video']);

/** Walks a JSON value and collects `src`/`poster` of every Media-shaped object (has type svg|image|video and a src). */
function collectMedia(node: unknown, found: { src: string; where: string }[], where: string): void {
  if (Array.isArray(node)) {
    for (const item of node) collectMedia(item, found, where);
    return;
  }
  if (!node || typeof node !== 'object') return;
  const obj = node as Record<string, unknown>;
  if (typeof obj.type === 'string' && MEDIA_TYPES.has(obj.type) && typeof obj.src === 'string') {
    found.push({ src: obj.src, where });
  }
  if (typeof obj.type === 'string' && MEDIA_TYPES.has(obj.type) && typeof obj.poster === 'string') {
    found.push({ src: obj.poster, where });
  }
  for (const value of Object.values(obj)) collectMedia(value, found, where);
}

function makeClient(key: string): SupabaseClient {
  return createClient(projectUrl(), key, AUTH_OPTS);
}

// --- upload ---------------------------------------------------------------------------------

async function listRemoteDir(client: SupabaseClient, dir: string): Promise<Map<string, number>> {
  const remote = new Map<string, number>();
  for (let offset = 0; ; offset += LIST_PAGE) {
    const { data, error } = await client.storage.from(BUCKET).list(dir, {
      limit: LIST_PAGE, offset, sortBy: { column: 'name', order: 'asc' },
    });
    if (error) die(`Could not list "${dir || '/'}" in bucket "${BUCKET}": ${error.message}`);
    for (const item of data ?? []) {
      // Folders come back without metadata; files carry metadata.size.
      if (item.metadata) remote.set(item.name, Number((item.metadata as { size?: number }).size ?? -1));
    }
    if ((data ?? []).length < LIST_PAGE) break;
  }
  return remote;
}

async function upload(args: string[]): Promise<void> {
  const dryRun = args.includes('--dry-run');
  const force = args.includes('--force');
  const url = projectUrl();
  const serviceKey = env('SUPABASE_SERVICE_ROLE_KEY');
  if (!serviceKey) die('SUPABASE_SERVICE_ROLE_KEY is not set. Server-side only; add it to .env (see .env.example).');
  const client = makeClient(serviceKey);

  const { data: bucket, error: bucketError } = await client.storage.getBucket(BUCKET);
  if (bucketError || !bucket) {
    die(`Bucket "${BUCKET}" is not available: ${bucketError?.message ?? 'not found'}.\n` +
      `Owner action: in the Supabase dashboard go to Storage → New bucket, name "${BUCKET}", tick "Public bucket", then re-run.`);
  }
  if (!bucket.public) {
    die(`Bucket "${BUCKET}" exists but is not public.\n` +
      `Owner action: Storage → "${BUCKET}" → Edit bucket → turn on "Public bucket" (public read only; no write policy).`);
  }

  const files = await localFiles(MEDIA_DIR);
  if (files.length === 0) die(`No files found under ${MEDIA_DIR}.`);

  const dirs = [...new Set(files.map(f => posix.dirname(f.key)).map(d => (d === '.' ? '' : d)))];
  const remote = new Map<string, number>();
  for (const dir of dirs) {
    for (const [name, size] of await listRemoteDir(client, dir)) {
      remote.set(dir ? `${dir}/${name}` : name, size);
    }
  }

  let uploaded = 0;
  let skipped = 0;
  for (const file of files) {
    const localSize = (await stat(file.abs)).size;
    if (!force && remote.get(file.key) === localSize) {
      skipped++;
      continue;
    }
    if (dryRun) {
      console.log(`would upload ${file.key} (${localSize} bytes)`);
      uploaded++;
      continue;
    }
    const bytes = await readFile(file.abs);
    const { error } = await client.storage.from(BUCKET).upload(file.key, bytes, {
      contentType: contentTypeFor(file.key), upsert: true, cacheControl: '3600',
    });
    if (error) die(`Upload failed for ${file.key}: ${error.message}`);
    console.log(`uploaded ${file.key}`);
    uploaded++;
  }

  const verb = dryRun ? 'would upload' : 'uploaded';
  console.log(`\nBucket "${BUCKET}": ${files.length} local files; ${verb} ${uploaded}; already current ${skipped}.`);
  console.log(`Set site_settings.media_base_url to: ${mediaBaseUrl(url)}`);
  console.log('Local public/media is unchanged and remains the recovery copy.');
}

// --- verify (read-only) ---------------------------------------------------------------------

async function readAll(client: SupabaseClient, view: string, columns: string): Promise<Record<string, unknown>[]> {
  const rows: Record<string, unknown>[] = [];
  for (let from = 0; ; from += READ_PAGE) {
    const { data, error } = await client.from(view).select(columns).range(from, from + READ_PAGE - 1);
    if (error) die(`Could not read ${view} from Supabase: ${error.message}`);
    const page = (data ?? []) as unknown as Record<string, unknown>[];
    rows.push(...page);
    if (page.length < READ_PAGE) break;
  }
  return rows;
}

async function verify(): Promise<void> {
  const url = projectUrl();
  const publishableKey = env('VITE_SUPABASE_PUBLISHABLE_KEY');
  if (!publishableKey) die('VITE_SUPABASE_PUBLISHABLE_KEY is not set. Add it to .env (see .env.example).');
  const client = makeClient(publishableKey);

  const stories = await readAll(client, 'v_live_story', 'story_slug, document, library_entry');
  const moments = await readAll(client, 'v_live_moment', 'story_slug, media_path');

  // key -> story slugs that reference it. Problems are references that cannot map into the bucket.
  const refs = new Map<string, Set<string>>();
  const problems: string[] = [];
  const addRef = (raw: string, slug: string, where: string) => {
    const key = keyForMediaSrc(raw);
    if (key === null) return; // absolute URL: external
    if (key === undefined) {
      problems.push(`${slug}: ${where} has a path that cannot resolve inside the bucket: "${raw}"`);
      return;
    }
    if (!refs.has(key)) refs.set(key, new Set());
    refs.get(key)!.add(slug);
  };

  for (const row of stories) {
    const slug = String(row.story_slug);
    const found: { src: string; where: string }[] = [];
    collectMedia(row.document, found, 'document');
    collectMedia(row.library_entry, found, 'library_entry');
    for (const f of found) addRef(f.src, slug, f.where);
  }
  for (const row of moments) {
    if (typeof row.media_path === 'string' && row.media_path) {
      addRef(row.media_path, String(row.story_slug), 'moment media_path');
    }
  }

  const keys = [...refs.keys()].sort();
  const status = new Map<string, { ok: boolean; detail: string; cors: boolean }>();
  for (let i = 0; i < keys.length; i += CONCURRENCY) {
    await Promise.all(keys.slice(i, i + CONCURRENCY).map(async key => {
      const target = publicUrlFor(url, key);
      try {
        const res = await fetch(target, { method: 'HEAD' });
        const cors = res.headers.has('access-control-allow-origin');
        status.set(key, { ok: res.ok, detail: `HTTP ${res.status}`, cors });
      } catch {
        status.set(key, { ok: false, detail: 'request failed', cors: false });
      }
    }));
  }

  const missing = keys.filter(k => !status.get(k)!.ok);
  const noCors = keys.filter(k => k.endsWith('.svg') && status.get(k)!.ok && !status.get(k)!.cors);

  console.log(`Live stories: ${stories.length}. Live moments with media_path: ${moments.filter(m => m.media_path).length}.`);
  console.log(`Referenced media (relative): ${keys.length}. Present in bucket "${BUCKET}": ${keys.length - missing.length}. Missing: ${missing.length}.`);
  for (const key of missing) {
    const s = status.get(key)!;
    console.log(`  MISSING ${key} (${s.detail}) referenced by: ${[...refs.get(key)!].join(', ')}`);
  }
  for (const p of problems) console.log(`  PROBLEM ${p}`);
  if (noCors.length) {
    console.log(`Warning: ${noCors.length} SVG(s) answer without Access-Control-Allow-Origin; MediaView falls back to <img>. ` +
      'Owner action: check the bucket CORS/project settings if animation is expected.');
  }
  if (missing.length || problems.length) process.exit(1);
  console.log('All referenced media is present in the bucket.');
}

// --- entry ----------------------------------------------------------------------------------

const [mode, ...rest] = process.argv.slice(2);
if (mode === 'upload') await upload(rest);
else if (mode === 'verify') await verify();
else die('Usage: media-storage.ts <upload [--dry-run] [--force] | verify>');
