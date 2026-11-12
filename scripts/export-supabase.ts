// Read-only export of the Supabase content to a snapshot directory (decisions 35, 37; V1 merge gate).
//
//   node --experimental-strip-types --disable-warning=ExperimentalWarning scripts/export-supabase.ts [--out <dir>]
//
// Connects with SUPABASE_DB_URL (the same variable seed and publish use) and runs everything inside one
// READ ONLY transaction, so it cannot write even if a query were wrong. Output goes to a fresh temporary
// directory unless --out is given. The export holds live content; delete it when the check is done.
// Check the snapshot with scripts/reconcile-export.ts.
//
// Never prints the connection string or any key: only the hostname is shown.

import { createHash } from 'node:crypto';
import { mkdir, mkdtemp, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve, sep } from 'node:path';
import pg from 'pg';

// Dates come back as the YYYY-MM-DD text that is stored, not as JS Date objects (time zones would shift them).
pg.types.setTypeParser(pg.types.builtins.DATE, (v: string) => v);

const REPO = resolve(import.meta.dirname, '..');
const FORMAT_VERSION = 1;

/** Each section is one JSON file. Views already apply the live and non-sample gates the app uses. */
const VIEW_SECTIONS: readonly (readonly [section: string, view: string])[] = [
  ['site', 'v_site'],
  ['facets', 'v_facet'],
  ['tags', 'v_tag'],
  ['fields', 'v_field'],
  ['volumes', 'v_volume'],
  ['issues', 'v_issue'],
  ['issue_stories', 'v_issue_story'],
  ['companies', 'v_company'],
  ['company_posts', 'v_company_post'],
  ['company_built_on', 'v_company_built_on'],
  ['storylines', 'v_storyline'],
  ['storyline_steps', 'v_storyline_step'],
  ['nodes', 'v_node'],
  ['front_placement', 'v_front_placement'],
  ['stories', 'v_live_story'],
  ['moments', 'v_live_moment'],
  ['facts', 'v_live_fact'],
  ['story_tags', 'v_live_story_tag'],
  ['story_fields', 'v_live_story_field'],
  ['citations', 'v_live_citation'],
  ['media_assets', 'v_live_media_asset'],
  ['relation_evidence', 'v_relation_evidence'],
];

/**
 * v_relation shows only verified, non-sample edges. The seed imports every relation as verified = false, so the
 * view would hide all of them. This query reads the base table so the export matches the seed.
 */
const RELATIONS_SQL = `
  select sn.slug as source_node_slug, tn.slug as target_node_slug, r.kind, r.note,
         r.cited, r.cross_field, r.verified, r.sample
  from relation r
  join node sn on sn.id = r.source_node_id
  join node tn on tn.id = r.target_node_id
  order by sn.slug, tn.slug, r.kind`;

/** Archived copies of sources (no view exists for this table). */
const SOURCE_SNAPSHOTS_SQL = `
  select s.kind as source_kind, s.url as source_url, ss.archived_url, ss.retrieved_on::text as retrieved_on
  from source_snapshot ss
  join source s on s.id = ss.source_id
  order by s.url, ss.archived_url, ss.retrieved_on`;

function die(msg: string, code = 2): never {
  console.error(msg);
  process.exit(code);
}

function parseArgs(argv: string[]): { out: string | null } {
  let out: string | null = null;
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--out') {
      const v = argv[++i];
      if (!v || v.startsWith('--')) die('--out needs a directory path');
      out = resolve(v);
    } else {
      die(`unknown argument "${a}"\nusage: export-supabase.ts [--out <dir>]`);
    }
  }
  if (out && (out === REPO || out.startsWith(REPO + sep))) {
    die('refusing to export inside the repository: live content must not be written where git can see it. Use a directory outside the repo (or omit --out).');
  }
  return { out };
}

/** Deterministic JSON so output files are stable between runs. */
function canonical(value: unknown): string {
  if (value === null || typeof value !== 'object') return JSON.stringify(value) ?? 'null';
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  const obj = value as Record<string, unknown>;
  return `{${Object.keys(obj).filter(k => obj[k] !== undefined).sort()
    .map(k => `${JSON.stringify(k)}:${canonical(obj[k])}`).join(',')}}`;
}

async function main(): Promise<void> {
  const { out: outArg } = parseArgs(process.argv.slice(2));
  const dbUrl = process.env.SUPABASE_DB_URL?.trim();
  if (!dbUrl) die('SUPABASE_DB_URL is not set. Add it to .env (see .env.example); the export only reads.');
  const host = new URL(dbUrl).hostname;
  console.log(`Source (read only): ${host}`);

  const client = new pg.Client({ connectionString: dbUrl });
  const sections = new Map<string, unknown[]>();
  await client.connect();
  try {
    await client.query('begin read only');
    await client.query("set local statement_timeout = '120s'");
    for (const [section, view] of VIEW_SECTIONS) {
      // View names are constants from this file, never user input.
      const r = await client.query(`select * from ${view}`);
      sections.set(section, r.rows);
    }
    sections.set('relations', (await client.query(RELATIONS_SQL)).rows);
    sections.set('source_snapshots', (await client.query(SOURCE_SNAPSHOTS_SQL)).rows);
    await client.query('rollback'); // nothing to commit; the transaction was read only
  } catch (err) {
    await client.query('rollback').catch(() => undefined);
    die(`export failed; nothing was written: ${(err as Error).message}`, 1);
  } finally {
    await client.end();
  }

  // Write only after every read succeeded, so a failed export never leaves a half-written snapshot.
  const dir = outArg ?? (await mkdtemp(join(tmpdir(), 'geek-times-export-')));
  await mkdir(dir, { recursive: true });
  const manifest: Record<string, unknown> = {
    format: 'geek-times-export',
    formatVersion: FORMAT_VERSION,
    exportedAt: new Date().toISOString(),
    sourceHost: host,
    notes: [
      'Read-only export. Views apply the live and non-sample gates; relations come from the base table.',
      'Preview rows (status = preview), media binaries and numeric ids are not part of this export.',
    ],
    sections: {} as Record<string, { rows: number; file: string; sha256: string }>,
  };
  for (const [section, rows] of [...sections.entries()].sort(([a], [b]) => (a < b ? -1 : 1))) {
    const sorted = [...rows].sort((a, b) => {
      const x = canonical(a);
      const y = canonical(b);
      return x < y ? -1 : x > y ? 1 : 0;
    });
    const text = `${JSON.stringify(sorted, null, 2)}\n`;
    const file = `${section}.json`;
    await writeFile(join(dir, file), text);
    (manifest.sections as Record<string, unknown>)[section] = {
      rows: sorted.length,
      file,
      sha256: createHash('sha256').update(text).digest('hex'),
    };
  }
  await writeFile(join(dir, 'manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`);

  const total = [...sections.values()].reduce((n, rows) => n + rows.length, 0);
  console.log(`Exported ${sections.size} sections, ${total} rows.`);
  console.log(`Snapshot directory: ${dir}`);
  console.log(`Check it: node --experimental-strip-types --disable-warning=ExperimentalWarning scripts/reconcile-export.ts --export "${dir}"`);
  console.log('This directory holds live content. Delete it when the check is finished.');
}

main().catch((err: unknown) => die(`export failed: ${(err as Error).message}`, 1));
