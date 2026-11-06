// Apply a SQL migration file to the Supabase Postgres as one transaction. Any error rolls back.
// Needs SUPABASE_DB_URL in .env — Supabase dashboard → Project Settings → Database →
// Connection string → URI (transaction-mode pooler on port 6543 is fine for migrations).
//
// Usage: npm run apply:migration -- <path-to-sql>

import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import pg from 'pg';

function die(msg: string): never {
  console.error(msg);
  process.exit(1);
}

const migrationPath = process.argv[2]?.trim();
if (!migrationPath) die('usage: npm run apply:migration -- <path-to-sql>');

const dbUrl = process.env.SUPABASE_DB_URL?.trim();
if (!dbUrl) {
  die(
    'SUPABASE_DB_URL is not set. Add one line to .env:\n' +
    '  SUPABASE_DB_URL=postgresql://postgres.<project-ref>:<db-password>@aws-0-<region>.pooler.supabase.com:6543/postgres\n' +
    'Copy it from Supabase dashboard → Project Settings → Database → Connection string → URI.',
  );
}

const target = new URL(dbUrl);
console.log(`Target: ${target.hostname}${target.port ? ':' + target.port : ''}`);

const sql = await readFile(resolve(migrationPath), 'utf8');

const client = new pg.Client({ connectionString: dbUrl });
await client.connect();
try {
  await client.query('begin');
  await client.query(sql);
  await client.query('commit');
  console.log(`Applied ${migrationPath}`);
} catch (err) {
  await client.query('rollback').catch(() => {});
  die(`Failed to apply migration: ${(err as Error).message}`);
} finally {
  await client.end();
}
