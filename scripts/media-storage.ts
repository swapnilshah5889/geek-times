// Supabase Storage media sync for the cloud-only V1 gate. Server-side only; never bundled into the site.
//
// Maps each LIVE media object (referenced by v_live_story documents/library_entry and v_live_moment.media_path) to the
// object key with the same relative path in a public-read bucket (default "story-media", override with
// SUPABASE_MEDIA_BUCKET). Story documents store media as relative paths such as
// "attention-is-all-you-need/comic/01a-letters.svg", so the public URL is <media_base_url><src>, where
// media_base_url = <SUPABASE_URL>/storage/v1/object/public/<bucket>/ (trailing slash required, because MediaView
// resolves src with new URL(src, base)).
//
// Scope rules:
//   - Only media referenced by live content is inventoried and uploaded. backups/media/samples/** is never uploaded
//     (not live). A live row that points into samples/ is reported as a problem.
//   - Git-tracked backups/media is read-only here. The app never serves or reads this directory.
//   - Placeholder art (see placeholderReason) is never uploaded and is reported.
//
// Hash strategy: idempotency compares SHA-256 of the local bytes with SHA-256 of the remote object. Storage's list
// metadata exposes only size and an MD5-style eTag, not SHA-256, so the remote object is downloaded and hashed when
// its size matches. A size mismatch means the content differs and is uploaded without a download. --force skips the
// check and re-uploads everything.
//
// Modes:
//   upload  Writes objects to Storage only. Needs SUPABASE_URL (or VITE_SUPABASE_URL), SUPABASE_SERVICE_ROLE_KEY and
//           VITE_SUPABASE_PUBLISHABLE_KEY (the last is used only to read the live inventory). --dry-run prints the
//           plan and writes nothing. Exits 1 if any referenced file is missing locally or any live SVG is placeholder
//           art (after uploading the rest). Never writes site_settings.
//   verify  Read-only. Needs SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY only (no service-role key). HEAD-checks
//           each live object's public URL; every object must answer 2xx with Access-Control-Allow-Origin: *.
//           Exits 1 on a missing object, a missing CORS header, a placeholder SVG, or a live-content problem.
//
// Usage (see docs/handoffs/claude-v1-cloud-only-merge-gate.md for the npm wiring):
//   node --experimental-strip-types --disable-warning=ExperimentalWarning --env-file=.env scripts/media-storage.ts upload [--dry-run] [--force] [--preview]
//   node --experimental-strip-types --disable-warning=ExperimentalWarning --env-file=.env scripts/media-storage.ts verify

import { createHash } from 'node:crypto';
import { readdir, readFile } from 'node:fs/promises';
import { join, posix } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createClient, type SupabaseClient } from '@supabase/supabase-js';

const ROOT = fileURLToPath(new URL('..', import.meta.url));
const MEDIA_DIR = join(ROOT, 'backups', 'media');
const SITE_ASSET_KEYS = ['brand/social-card.png'];
const BUCKET = (process.env.SUPABASE_MEDIA_BUCKET ?? '').trim() || 'story-media';
const LIST_PAGE = 1000;
const READ_PAGE = 1000;
const CONCURRENCY = 8;
const PLACEHOLDER_MAX_BYTES = 500;

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

function hostOf(url: string): string {
  try { return new URL(url).host; } catch { return '(unparseable URL)'; }
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

function sha256(bytes: Uint8Array): string {
  return createHash('sha256').update(bytes).digest('hex');
}

function isSampleKey(key: string): boolean {
  return key === 'samples' || key.startsWith('samples/');
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

// --- live inventory -------------------------------------------------------------------------

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

interface Inventory {
  storySlugs: string[];
  liveMomentsWithMedia: number;
  external: number;
  problems: string[];
  /** bucket key -> story slugs whose live content references it */
  refs: Map<string, Set<string>>;
}

/** Reads live content through the publishable key only (the views are the public contract). */
async function liveInventory(publishableKey: string, includePreview = false): Promise<Inventory> {
  const client = makeClient(publishableKey);
  const stories = await readAll(client, 'v_live_story', 'story_slug, document, library_entry');
  const moments = await readAll(client, 'v_live_moment', 'story_slug, media_path');
  if (includePreview) {
    // --preview: also upload art for stories published as preview, so they render in local dev before approval.
    stories.push(...await readAll(client, 'v_preview_story', 'story_slug, document, library_entry'));
    moments.push(...await readAll(client, 'v_preview_moment', 'story_slug, media_path'));
  }

  const inv: Inventory = {
    storySlugs: stories.map(r => String(r.story_slug)).sort(),
    liveMomentsWithMedia: 0, external: 0, problems: [], refs: new Map(),
  };
  const addRef = (raw: string, slug: string, where: string) => {
    const key = keyForMediaSrc(raw);
    if (key === null) { inv.external++; return; }
    if (key === undefined) {
      inv.problems.push(`${slug}: ${where} path cannot resolve inside the bucket: "${raw}"`);
      return;
    }
    if (isSampleKey(key)) {
      inv.problems.push(`${slug}: ${where} points at samples/ (not live): "${raw}"`);
      return;
    }
    if (!inv.refs.has(key)) inv.refs.set(key, new Set());
    inv.refs.get(key)!.add(slug);
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
      inv.liveMomentsWithMedia++;
      addRef(row.media_path, String(row.story_slug), 'moment media_path');
    }
  }
  return inv;
}

// --- local files and placeholder detection --------------------------------------------------

/**
 * Returns a reason when an SVG looks like placeholder art rather than real drawing: under PLACEHOLDER_MAX_BYTES, or
 * exactly one <rect> and no <text> or <path>. Any other shape (including a single raster <image>) passes.
 */
function placeholderReason(svg: string, size: number): string | null {
  if (size < PLACEHOLDER_MAX_BYTES) return `only ${size} bytes (under ${PLACEHOLDER_MAX_BYTES})`;
  if (/<text[\s>]/i.test(svg) || /<path[\s>]/i.test(svg)) return null;
  const shapes = [...svg.matchAll(/<(rect|circle|ellipse|line|polyline|polygon|image|use)\b/gi)]
    .map(m => m[1].toLowerCase());
  if (shapes.length === 1 && shapes[0] === 'rect') return 'single rectangle with no <text> or <path>';
  return null;
}

interface Placeholder { key: string; reason: string; slugs: string[] }

/**
 * Checks each live-referenced SVG that exists locally. Missing local files are not an error here: after the local
 * copies are removed (after backup), verify must still work from the bucket alone.
 */
async function scanLocalSvgs(inv: Inventory, byKey: Map<string, string>): Promise<{ placeholders: Placeholder[]; notLocal: string[] }> {
  const placeholders: Placeholder[] = [];
  const notLocal: string[] = [];
  for (const key of [...inv.refs.keys()].sort()) {
    if (!key.toLowerCase().endsWith('.svg')) continue;
    const abs = byKey.get(key);
    if (!abs) { notLocal.push(key); continue; }
    const bytes = await readFile(abs);
    const reason = placeholderReason(bytes.toString('utf8'), bytes.length);
    if (reason) placeholders.push({ key, reason, slugs: [...inv.refs.get(key)!].sort() });
  }
  return { placeholders, notLocal };
}

async function loadLocal(): Promise<Map<string, string>> {
  const files = await localFiles(MEDIA_DIR);
  if (files.length === 0) die(`No files found under ${MEDIA_DIR}.`);
  return new Map(files.map(f => [f.key, f.abs]));
}

function printInventory(inv: Inventory, byKey: Map<string, string>): void {
  const bySlug = new Map<string, number>(inv.storySlugs.map(s => [s, 0]));
  for (const slugs of inv.refs.values()) for (const s of slugs) bySlug.set(s, (bySlug.get(s) ?? 0) + 1);
  const samples = [...byKey.keys()].filter(isSampleKey).length;
  const siteAssets = SITE_ASSET_KEYS.filter(k => byKey.has(k)).length;
  const unreferenced = [...byKey.keys()].filter(k => !isSampleKey(k) && !SITE_ASSET_KEYS.includes(k) && !inv.refs.has(k)).length;

  console.log(`Live stories: ${inv.storySlugs.length}. Live moments with media: ${inv.liveMomentsWithMedia}. ` +
    `External URLs skipped: ${inv.external}.`);
  console.log(`Live media objects to check: ${inv.refs.size}. Inventory by story slug (media referenced):`);
  console.log(`Required site media assets: ${siteAssets}/${SITE_ASSET_KEYS.length}.`);
  for (const [slug, n] of [...bySlug].sort((a, b) => (a[0] < b[0] ? -1 : 1))) console.log(`  ${slug}: ${n}`);
  console.log(`Excluded, not live: ${samples} file(s) under backups/media/samples/.`);
  console.log(`Local media not referenced by live content (not uploaded): ${unreferenced}.`);
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
  const preview = args.includes('--preview');
  const url = projectUrl();
  const serviceKey = env('SUPABASE_SERVICE_ROLE_KEY');
  if (!serviceKey) die('SUPABASE_SERVICE_ROLE_KEY is not set. Server-side only; add it to .env (see .env.example).');
  const publishableKey = env('VITE_SUPABASE_PUBLISHABLE_KEY');
  if (!publishableKey) die('VITE_SUPABASE_PUBLISHABLE_KEY is not set (needed to read the live inventory). See .env.example.');

  const inv = await liveInventory(publishableKey, preview);
  const byKey = await loadLocal();
  printInventory(inv, byKey);

  const { placeholders, notLocal } = await scanLocalSvgs(inv, byKey);
  const missingSiteAssets = SITE_ASSET_KEYS.filter(k => !byKey.has(k));
  if (notLocal.length || missingSiteAssets.length || inv.problems.length) {
    for (const k of notLocal) console.error(`BLOCKER referenced media not found under backups/media: ${k}`);
    for (const k of missingSiteAssets) console.error(`BLOCKER required site asset not found under backups/media: ${k}`);
    for (const p of inv.problems) console.error(`BLOCKER ${p}`);
    die('Nothing uploaded. Fix the blockers above (live content must resolve to local files) and re-run.');
  }

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

  const badKeys = new Set(placeholders.map(p => p.key));
  const uploadKeys = [...new Set([...inv.refs.keys(), ...SITE_ASSET_KEYS])].filter(k => !badKeys.has(k)).sort();
  const dirs = [...new Set(uploadKeys.map(k => posix.dirname(k)).map(d => (d === '.' ? '' : d)))];
  const remote = new Map<string, number>();
  for (const dir of dirs) {
    for (const [name, size] of await listRemoteDir(client, dir)) {
      remote.set(dir ? `${dir}/${name}` : name, size);
    }
  }

  let uploaded = 0;
  let identical = 0;
  for (const key of uploadKeys) {
    const bytes = await readFile(byKey.get(key)!);
    if (!force && remote.get(key) === bytes.length) {
      // Same size: only a content hash can prove the object is current.
      const { data, error } = await client.storage.from(BUCKET).download(key);
      if (error || !data) die(`Could not download ${key} for the hash check: ${error?.message ?? 'no data'}`);
      const remoteHash = sha256(new Uint8Array(await data.arrayBuffer()));
      if (remoteHash === sha256(bytes)) {
        identical++;
        continue;
      }
    }
    if (dryRun) {
      console.log(`would upload ${key} (${bytes.length} bytes)`);
      uploaded++;
      continue;
    }
    const { error } = await client.storage.from(BUCKET).upload(key, bytes, {
      contentType: contentTypeFor(key), upsert: true, cacheControl: '3600',
    });
    if (error) die(`Upload failed for ${key}: ${error.message}`);
    console.log(`uploaded ${key}`);
    uploaded++;
  }

  const verb = dryRun ? 'would upload' : 'uploaded';
  console.log(`\nBucket "${BUCKET}" on ${hostOf(url)}: ${inv.refs.size} live story object(s) + ${SITE_ASSET_KEYS.length} site asset(s); ${verb} ${uploaded}; ` +
    `already identical by SHA-256 ${identical}.`);
  for (const p of placeholders) {
    console.error(`PLACEHOLDER not uploaded: ${p.key} (${p.reason}); stories: ${p.slugs.join(', ')}`);
  }
  console.log(`Owner action: set site_settings.media_base_url to: ${mediaBaseUrl(url)}`);
  console.log('This script does not write site_settings. Git-tracked backups/media remains unchanged as the recovery copy.');
  if (placeholders.length) {
    die(`${placeholders.length} live SVG(s) look like placeholder art. Replace them with real art, then re-run.`);
  }
}

// --- verify (read-only) ---------------------------------------------------------------------

async function verify(): Promise<void> {
  const url = projectUrl();
  const publishableKey = env('VITE_SUPABASE_PUBLISHABLE_KEY');
  if (!publishableKey) die('VITE_SUPABASE_PUBLISHABLE_KEY is not set. Add it to .env (see .env.example).');

  const inv = await liveInventory(publishableKey);
  const byKey = await loadLocal();
  printInventory(inv, byKey);
  const { placeholders, notLocal } = await scanLocalSvgs(inv, byKey);

  const keys = [...new Set([...inv.refs.keys(), ...SITE_ASSET_KEYS])].sort();
  const status = new Map<string, { ok: boolean; detail: string; acao: string | null }>();
  for (let i = 0; i < keys.length; i += CONCURRENCY) {
    await Promise.all(keys.slice(i, i + CONCURRENCY).map(async key => {
      try {
        const res = await fetch(publicUrlFor(url, key), { method: 'HEAD' });
        status.set(key, { ok: res.ok, detail: `HTTP ${res.status}`, acao: res.headers.get('access-control-allow-origin') });
      } catch {
        status.set(key, { ok: false, detail: 'request failed', acao: null });
      }
    }));
  }

  const missing = keys.filter(k => !status.get(k)!.ok);
  const noCors = keys.filter(k => status.get(k)!.ok && status.get(k)!.acao !== '*');
  const present = keys.length - missing.length;

  console.log(`Bucket "${BUCKET}" on ${hostOf(url)}: ${inv.refs.size} story object(s) + ${SITE_ASSET_KEYS.length} site asset(s); ` +
    `present ${present}; missing ${missing.length}; without ACAO "*" ${noCors.length}.`);
  for (const key of missing) {
    const refs = inv.refs.get(key);
    console.error(`BLOCKER MISSING ${key} (${status.get(key)!.detail}); ${refs ? `stories: ${[...refs].join(', ')}` : 'site asset'}`);
  }
  for (const key of noCors) {
    const acao = status.get(key)!.acao ?? 'absent';
    const refs = inv.refs.get(key);
    console.error(`BLOCKER NO CORS ${key} (Access-Control-Allow-Origin: ${acao}); ${refs ? `stories: ${[...refs].join(', ')}` : 'site asset'}`);
  }
  for (const p of placeholders) {
    console.error(`BLOCKER PLACEHOLDER ${p.key} (${p.reason}); stories: ${p.slugs.join(', ')}`);
  }
  for (const p of inv.problems) console.error(`BLOCKER ${p}`);
  if (notLocal.length) {
    console.log(`Note: ${notLocal.length} referenced SVG(s) not in backups/media; placeholder check skipped for them.`);
  }

  if (missing.length || noCors.length || placeholders.length || inv.problems.length) process.exit(1);
  console.log('All live story media and required site assets are present in the bucket and readable cross-origin (ACAO "*").');
}

// --- entry ----------------------------------------------------------------------------------

const [mode, ...rest] = process.argv.slice(2);
if (mode === 'upload') await upload(rest);
else if (mode === 'verify') await verify();
else die('Usage: media-storage.ts <upload [--dry-run] [--force] [--preview] | verify>');
