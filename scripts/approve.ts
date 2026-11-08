// Promote a story's preview version to live via the approve_version(slug) DB function.
// Needs SUPABASE_DB_URL in .env. Usage: npm run approve -- <slug>

import pg from 'pg';

function die(msg: string): never {
  console.error(msg);
  process.exit(1);
}

const slug = process.argv[2]?.trim();
if (!slug) die('usage: npm run approve -- <slug>');

const dbUrl = process.env.SUPABASE_DB_URL?.trim();
if (!dbUrl) die('SUPABASE_DB_URL is not set. Add the Postgres URI to .env (see .env.example).');

const client = new pg.Client({ connectionString: dbUrl });
await client.connect();
try {
  const { rows } = await client.query<{ version_id: string }>('select approve_version($1) as version_id', [slug]);
  console.log(`Approved ${slug}: version ${rows[0]?.version_id} is now live.`);
} catch (err) {
  die(`Could not approve ${slug}: ${(err as Error).message}`);
} finally {
  await client.end();
}
