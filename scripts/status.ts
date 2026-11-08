// List every published_version with its status. Needs SUPABASE_DB_URL in .env.
// Usage: npm run status

import { createHash } from 'node:crypto';
import pg from 'pg';

/** Same canonical JSON + sha256 as scripts/publish-to-supabase.ts, so document_sha matches the publish report. */
function canonical(value: unknown): string {
  if (value === null || typeof value !== 'object') return JSON.stringify(value) ?? 'null';
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  const obj = value as Record<string, unknown>;
  const keys = Object.keys(obj).filter(k => obj[k] !== undefined).sort();
  return `{${keys.map(k => `${JSON.stringify(k)}:${canonical(obj[k])}`).join(',')}}`;
}
const sha256 = (s: string) => createHash('sha256').update(s).digest('hex');

function die(msg: string): never {
  console.error(msg);
  process.exit(1);
}

const dbUrl = process.env.SUPABASE_DB_URL?.trim();
if (!dbUrl) die('SUPABASE_DB_URL is not set. Add the Postgres URI to .env (see .env.example).');

const client = new pg.Client({ connectionString: dbUrl });
await client.connect();
try {
  const { rows } = await client.query<{
    slug: string; status: string; version: string; published_at: Date | string | null; document: unknown;
  }>(
    `select s.slug as slug, pv.status as status, pv.id::text as version, pv.created_at as published_at,
            pv.document as document
       from published_version pv join story s on s.id = pv.story_id
      order by s.slug asc, pv.id desc`);
  console.table(rows.map(r => ({
    slug: r.slug,
    status: r.status,
    version: r.version,
    published_at: r.published_at instanceof Date ? r.published_at.toISOString() : (r.published_at ?? ''),
    document_sha: sha256(canonical(r.document)).slice(0, 8),
  })));
  const stories = new Set(rows.map(r => r.slug)).size;
  const live = rows.filter(r => r.status === 'live').length;
  const preview = rows.filter(r => r.status === 'preview').length;
  console.log(`${stories} stories, ${live} live, ${preview} preview`);
} catch (err) {
  die(`Failed to read published_version: ${(err as Error).message}`);
} finally {
  await client.end();
}
