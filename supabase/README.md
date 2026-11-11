# Supabase

Schema for The Geeky Times lives here as SQL migrations (decisions 34 and 49). Nothing is edited by hand in the
Supabase dashboard. The table names, keys and public-read rules are frozen in
[`docs/handoffs/v1-schema-contract.md`](../docs/handoffs/v1-schema-contract.md).

## Migration order

Files are applied in filename order, one file at a time. Each file runs as one transaction and never edits an earlier one.

1. `20261106085857_init_story_slice.sql`: `story`, `published_version`, their RLS policies, and `publish_version(bigint)`
   (decisions 42 and 48). Applied to the owner's project already. It contains no story content.
2. `20261106100000_core_content_schema.sql`: sources, citations, media assets, the tag vocabulary (`facet`, `tag`),
   story tags, moments, facts and the extra metadata columns on `published_version`.
3. `20261106100001_editorial_schema.sql`: volumes, issues, companies, storylines, fields, graph nodes, relations with
   evidence, front placement and story fields.
4. `20261106100002_public_views_rls.sql`: the `v_*` views that anon reads, their grants, and
   `v_live_story_by_slug(text)`. It drops nothing and alters no table.
5. `20261108120000_preview_status.sql`: preview status, `v_preview_*` views and the service-role-only
   `approve_version(text)` function. Local development selects preview views only when `VITE_SHOW_PREVIEW=1`.
6. `20261110120000_journal_published_trust.sql`: adds `journal_published` to the trust checks for stories,
   sources and moments.

Files 2 to 4 must run after the file before them. The publish importer (`scripts/publish-to-supabase.ts`) runs only after all four.

## Applying (canonical path)

`npm run apply:migration` is the record of record for this repo. It is the only path the repo's docs describe.

1. Add `SUPABASE_DB_URL` to `.env` (one line, from the Supabase dashboard: Project Settings, Database, Connection string,
   URI). The transaction-mode pooler on port 6543 is fine.
2. From the repo root, apply each file in the order above:

   ```bash
   npm run apply:migration -- supabase/migrations/20261106100000_core_content_schema.sql
   npm run apply:migration -- supabase/migrations/20261106100001_editorial_schema.sql
   npm run apply:migration -- supabase/migrations/20261106100002_public_views_rls.sql
   ```

The applier prints the target hostname before it writes. A failed file rolls back and leaves nothing applied from that
file. Fix it and run that file again. Do not re-run a file that already succeeded.

Then run the orphan audits and leak checks at the end of each file by hand. Every audit must return zero rows.

## Supabase CLI (optional)

The CLI is not installed or used by default. Use it only if you want `supabase db push` and you have run
`supabase link` for your own project. Do this once, before the first `db push`:

1. Install and link: `brew install supabase/tap/supabase`, then `supabase link --project-ref <your-project-ref>`.
   If the CLI reports that the project is not initialised, run `supabase init` once from the repo root.
2. Tell the CLI that the migrations are already applied. Run this once in the SQL editor or with `psql`, and only after
   the files above have been applied with `npm run apply:migration`:

   ```sql
   insert into supabase_migrations.schema_migrations (version, name) values
     ('20261106085857', 'init_story_slice'),
     ('20261106100000', 'core_content_schema'),
     ('20261106100001', 'editorial_schema'),
     ('20261106100002', 'public_views_rls'),
     ('20261108120000', 'preview_status'),
     ('20261110120000', 'journal_published_trust');
   ```

   Without these rows, `db push` would try to run all four files again. They are not idempotent, so the push would fail.
3. From then on, `supabase db push` applies only new files.

Do not paste the migration files into the dashboard SQL editor. A partial run there leaves no record.

## Rules

- **Migrations are additive only.** Add new files for new changes. Never edit a migration that has already been applied
  to a project, and never drop or rename a table or column in place.
- **Never run `supabase db reset` against a project the owner uses.** It wipes the database it targets. It is only for a
  throwaway local database.
- **No foreign keys** (decisions 30 and 38). Every `*_id` column holds another row's id and is indexed. Each file ends
  with a commented orphan audit, one query per reference column.
- **Public reads go through views.** The live views from migration 4 exclude previews. The preview views from migration 5
  are also readable by anon and are selected only by a local build with `VITE_SHOW_PREVIEW=1`; this hides drafts from the
  hosted site's UI, but it is not a confidentiality boundary. Raw tables have no anon grant beyond the existing story
  table policies (see the header of migration 4).
- Readers use the publishable key only. The service-role key stays on the server (seed and publish CLI) and never
  carries a `VITE_` prefix.

## Reference

- Schema contract (frozen table names and public-read rules): [`docs/handoffs/v1-schema-contract.md`](../docs/handoffs/v1-schema-contract.md)
- Row-level security: https://supabase.com/docs/guides/database/postgres/row-level-security
- Securing data: https://supabase.com/docs/guides/database/secure-data

## Preview, then approve

`npm run publish:supabase -- <slug>` now writes the version with `status = 'preview'` (default); it is not live. With
`VITE_SHOW_PREVIEW=1` (dev) the site reads the `v_preview_*` views and shows it. `npm run status` lists every version.
`npm run approve -- <slug>` calls `approve_version(slug)` and makes the preview live. `--status live` skips the
preview step and publishes live immediately.
