// Restore drill: rebuilds the database from Git seed + publish into a DISPOSABLE empty Supabase project, then
// exports it and reconciles the export against data/seed/. See docs/handoffs/export-restore-drill.md.
//
//   node --experimental-strip-types --disable-warning=ExperimentalWarning scripts/restore-drill.ts \
//     --target-url "$DRILL_DB_URL" --confirm-disposable [--export-out <dir>]
//
// This is the only script here that writes. It refuses unless ALL of these hold:
//   1. --target-url AND --confirm-disposable are both given (the explicit gate).
//   2. The target is not the live project: its project ref (postgres.<ref> user, or db.<ref>.supabase.co host)
//      differs from the live ref read from .env's SUPABASE_DB_URL, and the URLs are not identical.
//      Localhost targets are allowed. Refs that cannot be read from either URL are refused.
//   3. The target has no rows in any public table (a fresh project, or one with no tables yet).
// Child steps get a clean environment that contains only SUPABASE_DB_URL = target. They never load .env,
// so the live URL cannot be reached by accident. The target URL is never printed; only its hostname is.

import { spawnSync } from 'node:child_process';
import { mkdtemp, readdir, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { parseEnv } from 'node:util';
import pg from 'pg';

const REPO = resolve(import.meta.dirname, '..');
const SCRIPTS = join(REPO, 'scripts');
const NODE_ARGS = ['--experimental-strip-types', '--disable-warning=ExperimentalWarning'];

function die(msg: string, code = 2): never {
  console.error(msg);
  process.exit(code);
}

const USAGE = `usage: restore-drill.ts --target-url <postgres-uri> --confirm-disposable [--export-out <dir>]
  <postgres-uri>  the disposable project's Postgres URI (Dashboard > Project Settings > Database > URI).
                  Pass it from an environment variable, e.g. --target-url "$DRILL_DB_URL", so it stays out of shell history.`;

interface Args { targetUrl: string; confirmed: boolean; exportOut: string | null }

function parseArgs(argv: string[]): Args {
  const args: Args = { targetUrl: '', confirmed: false, exportOut: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--target-url') {
      const v = argv[++i];
      if (!v || v.startsWith('--')) die(`--target-url needs a value\n${USAGE}`);
      args.targetUrl = v.trim();
    } else if (a === '--confirm-disposable') {
      args.confirmed = true;
    } else if (a === '--export-out') {
      const v = argv[++i];
      if (!v || v.startsWith('--')) die(`--export-out needs a directory\n${USAGE}`);
      args.exportOut = resolve(v);
    } else {
      die(`unknown argument "${a}"\n${USAGE}`);
    }
  }
  if (!args.targetUrl) die(`refusing: --target-url is required.\n${USAGE}`);
  if (!args.confirmed) {
    die(`refusing: this drill WRITES to the target (migrations, seed, publish). Pass --confirm-disposable only after you have\n` +
      `confirmed the target is a disposable, empty, non-production Supabase project.\n${USAGE}`);
  }
  return args;
}

/** The project ref: the pooler user "postgres.<ref>", or the host "db.<ref>.supabase.co". Null when neither matches. */
function projectRef(url: URL): string | null {
  const fromUser = /^postgres\.([a-z0-9]{10,})$/.exec(decodeURIComponent(url.username));
  if (fromUser) return fromUser[1];
  const fromHost = /^db\.([a-z0-9]{10,})\.supabase\.co$/.exec(url.hostname);
  return fromHost ? fromHost[1] : null;
}

const isLocal = (url: URL) => ['localhost', '127.0.0.1', '[::1]', '::1'].includes(url.hostname);

async function liveUrlFromEnvFile(): Promise<string | null> {
  // Read .env without loading it into this process's environment. The child steps must not inherit it.
  const fromProcess = process.env.SUPABASE_DB_URL?.trim();
  if (fromProcess) return fromProcess;
  try {
    const parsed = parseEnv(await readFile(join(REPO, '.env'), 'utf8'));
    return parsed.SUPABASE_DB_URL?.trim() || null;
  } catch {
    return null;
  }
}

function guardAgainstLive(target: URL, liveRaw: string | null): void {
  if (isLocal(target)) return;
  if (!liveRaw) {
    console.warn('warning: no live SUPABASE_DB_URL found in .env to compare with; the --confirm-disposable flag is the only gate.');
    return;
  }
  const live = new URL(liveRaw);
  if (target.href === live.href || (target.hostname === live.hostname && target.username === live.username && target.pathname === live.pathname)) {
    die('refusing: the target URL is the live project URL (same host, user and database). Use a different, disposable project.');
  }
  const targetRef = projectRef(target);
  const liveRef = projectRef(live);
  if (!targetRef || !liveRef) {
    die('refusing: cannot read the project ref from the target or the live URL, so the target cannot be shown to be different from live. ' +
      'Use the Supabase pooler or direct URL from the dashboard.');
  }
  if (targetRef === liveRef) die('refusing: the target is the live Supabase project (same project ref).');
}

async function assertEmpty(client: pg.Client): Promise<void> {
  const tables = await client.query<{ table_name: string }>(
    "select table_name from information_schema.tables where table_schema = 'public' and table_type = 'BASE TABLE' order by 1");
  const filled: string[] = [];
  for (const { table_name } of tables.rows) {
    // Table names come from information_schema, not user input.
    const r = await client.query<{ has: boolean }>(`select exists (select 1 from "${table_name}") as has`);
    if (r.rows[0].has) filled.push(table_name);
  }
  if (filled.length) {
    die(`refusing: the target is not empty (rows in: ${filled.join(', ')}). A drill needs a fresh project.`);
  }
  console.log(`Target check: ${tables.rows.length} public table(s), all empty.`);
}

function runStep(label: string, script: string, args: string[], env: NodeJS.ProcessEnv): void {
  console.log(`\n== ${label}`);
  const r = spawnSync(process.execPath, [...NODE_ARGS, join(SCRIPTS, script), ...args], { env, stdio: 'inherit', cwd: REPO });
  if (r.status !== 0) die(`drill stopped at "${label}" (exit ${r.status ?? 'signal'}). Nothing after it ran.`, r.status ?? 1);
}

async function main(): Promise<void> {
  const args = parseArgs(process.argv.slice(2));
  const target = new URL(args.targetUrl);
  guardAgainstLive(target, await liveUrlFromEnvFile());
  console.log(`Drill target (disposable, must be empty): ${target.hostname}`);

  const client = new pg.Client({ connectionString: args.targetUrl });
  await client.connect();
  try {
    await assertEmpty(client);
  } finally {
    await client.end();
  }

  // Clean environment: only the target. PATH is needed to find node's own helpers; nothing else from .env.
  const env: NodeJS.ProcessEnv = { PATH: process.env.PATH ?? '', HOME: process.env.HOME ?? '', SUPABASE_DB_URL: args.targetUrl };
  const migrations = (await readdir(join(REPO, 'supabase', 'migrations'))).filter(f => f.endsWith('.sql')).sort();
  for (const m of migrations) {
    runStep(`migration ${m}`, 'apply-migration.ts', [join('supabase', 'migrations', m)], env);
  }
  runStep('seed:editorial', 'seed-editorial-from-library.ts', [], env);

  const library = JSON.parse(await readFile(join(REPO, 'data', 'seed', 'library.json'), 'utf8')) as { stories: { id: string; sample?: boolean }[] };
  const slugs = library.stories.filter(s => s.sample !== true).map(s => s.id);
  for (const slug of slugs) {
    // --status live: the drill must produce live rows, which is what the export and the app read.
    runStep(`publish ${slug} (live)`, 'publish-to-supabase.ts', [slug, '--status', 'live'], env);
  }

  const exportDir = args.exportOut ?? (await mkdtemp(join(tmpdir(), 'geek-times-drill-export-')));
  runStep('export (read only)', 'export-supabase.ts', ['--out', exportDir], env);
  runStep('reconcile against data/seed', 'reconcile-export.ts', ['--export', exportDir], env);

  console.log(`\nRESTORE DRILL PASSED: ${migrations.length} migrations, seed, ${slugs.length} stories published live, export reconciled.`);
  console.log(`Export kept at ${exportDir}. Delete it when finished; it holds content.`);
  console.log('Not covered by this drill: media objects (Agent A / Storage), numeric ids, preview rows, site.json papers list. See docs/handoffs/export-restore-drill.md.');
}

main().catch((err: unknown) => die(`restore drill failed: ${(err as Error).message}`, 1));
