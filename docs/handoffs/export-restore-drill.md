# Export and restore drill

Proves that the Git seed (`data/seed/`) can rebuild the Supabase content in a clean non-production project, and that
a read-only export of that project reconciles back to the seed. Covers decisions 35 and 37 and the V1 merge gate item
"export/restore reconciliation". It does not cover media binaries; that is Agent A's Storage work.

## Scope of this proof

- **Proves:** Git seed -> migrations -> `seed:editorial` -> `publish:supabase --status live` (each story) -> read-only
  export -> reconciliation against `data/seed/` with exit 0.
- **Does not prove:** that the live project matches Git. That is a separate read-only check (section "Live check"
  below), run by the owner.

## Scripts

| Script | Writes? | Purpose |
| --- | --- | --- |
| `scripts/export-supabase.ts` | No (one read-only transaction) | Snapshot of the public views plus two base-table queries into a directory, with `manifest.json` and a sha256 per file. |
| `scripts/reconcile-export.ts` | No (reads files only) | Compares a snapshot with `data/seed/`. Exit 0 = match, 1 = mismatches (section and key printed), 2 = unreadable input or tampered files. |
| `scripts/restore-drill.ts` | Yes, only on a disposable target | Runs the whole drill below against `--target-url`. Refuses unless `--confirm-disposable` is given and the target is not the live project and is empty. |

The existing import path (`seed-editorial-from-library.ts`, `publish-to-supabase.ts`, `apply-migration.ts`) is reused
unchanged.

Commands use the Node flags the repo already uses. Add them to `package.json` (orchestrator only):

```json
"export:supabase": "node --experimental-strip-types --disable-warning=ExperimentalWarning --env-file=.env scripts/export-supabase.ts",
"reconcile:export": "node --experimental-strip-types --disable-warning=ExperimentalWarning scripts/reconcile-export.ts",
"restore:drill": "node --experimental-strip-types --disable-warning=ExperimentalWarning scripts/restore-drill.ts"
```

Do not add `--env-file` to `restore:drill`. The drill reads `.env` itself to learn the live URL for its guard, and its
child steps get a clean environment.

## Prerequisites

1. A **new, empty, disposable Supabase project** (not the owner's project). Its name should say it is a drill.
2. Its Postgres URI in the shell only, never in git or in `.env`:
   ```bash
   export DRILL_DB_URL='postgresql://postgres.<drill-ref>:<drill-db-password>@<pooler-host>:6543/postgres'
   ```
   Copy it from the drill project: Dashboard > Project Settings > Database > Connection string > URI.
3. Node 22.13 or later, `npm ci` done. No paid API is used by any step here.
4. Owner confirmation that the target is disposable. The drill writes to it.

## Procedure (one command)

```bash
cd /Users/uchiha/SPL/Projects/geek-times
EXPORT_DIR="$(mktemp -d)"   # OS temp directory, outside the repo
node --experimental-strip-types --disable-warning=ExperimentalWarning scripts/restore-drill.ts \
  --target-url "$DRILL_DB_URL" --confirm-disposable --export-out "$EXPORT_DIR"
```

The drill runs these steps in order and stops at the first failure:

1. Guard: `--target-url` and `--confirm-disposable` present; target project ref differs from the live ref in `.env`;
   target has no rows in any `public` table.
2. Migrations: every `supabase/migrations/*.sql` in filename order, each via `apply-migration.ts`.
3. `seed-editorial-from-library.ts`.
4. `publish-to-supabase.ts <slug> --status live` for each non-sample story in `data/seed/library.json`
   (currently: `attention-is-all-you-need`, `size-shapes-life`, `h3-hexagons`, `resnet`, `google-search`, `dynamo`,
   `einstein-special-relativity`).
5. `export-supabase.ts --out <EXPORT_DIR>` (read only).
6. `reconcile-export.ts --export <EXPORT_DIR>`.

Pass: the last line is `RESTORE DRILL PASSED` and the exit code is 0.

### Same steps by hand (for debugging one step)

Each command sets `SUPABASE_DB_URL` to the drill target for that command only. Do not use `npm run` here, so that
`.env` is never loaded.

```bash
RUN="node --experimental-strip-types --disable-warning=ExperimentalWarning"
export SUPABASE_DB_URL="$DRILL_DB_URL"
for f in supabase/migrations/*.sql; do $RUN scripts/apply-migration.ts "$f" || break; done
$RUN scripts/seed-editorial-from-library.ts
for slug in attention-is-all-you-need size-shapes-life h3-hexagons resnet google-search dynamo einstein-special-relativity; do
  $RUN scripts/publish-to-supabase.ts "$slug" --status live
done
$RUN scripts/export-supabase.ts --out "$EXPORT_DIR"
$RUN scripts/reconcile-export.ts --export "$EXPORT_DIR"; echo "exit=$?"
unset SUPABASE_DB_URL
```

Expected output of `publish-to-supabase.ts`: `Published <slug> (kind ...) as live version <id>.` For a re-run on a
non-empty target it prints `No change` and exits 0, but the drill refuses non-empty targets anyway.

## What the reconciliation checks

Every check reads the seed and the export; the database is not touched by `reconcile-export.ts`.

- `site`: `site.json` name, motto, tagline, navLabel, mediaBaseUrl, defaultPaper, schemaVersion against `v_site`.
- `facets`, `tags`: keys, labels, descriptions, facet of each tag, aliases.
- `fields`, `volumes`, `issues`: slugs, labels/titles, colours, cluster, numbers, volume, cover, published text, and
  ordered issue stories.
- `companies`: slugs, fields, ordered posts and built-on nodes.
- `storylines`, `storyline_steps`: slugs, titles, ordered steps (including steps with no story).
- `nodes`: slugs, titles, authors, year, kind, field, story.
- `relations`: every edge keyed by `source -> target (kind)`, plus its note. Read from the base table, so the
  unverified edges the seed imports are included.
- `front_placement`: the stored `current` row equals the `front` object in `library.json`.
- `stories`: the live, non-sample story set equals the seed's non-sample stories. Each stored `document` equals
  `data/seed/papers/<slug>.json`, and each stored library entry equals its `library.json` entry (canonical JSON, so key
  order does not matter).
- `story_tags`, `story_fields`: per story, the tag keys in the document and the fields in the library entry.
- Integrity: every section file's sha256 matches `manifest.json`, and row counts match.

Each mismatch prints as `[section] "key" field "name": seed X != export Y`, with long values shown as a short hash.

## What the drill covers

- Migrations apply in order to an empty project.
- `seed:editorial` and `publish:supabase --status live` reproduce all seven stories, the vocabulary, fields, volumes,
  issues, companies, storylines, nodes, relations, and the front placement.
- Story documents and library entries are restored exactly (canonical JSON equality against the seed files).
- Story tags and fields per story.
- Publish's derived rows (moments, facts, citations, media rows) are written by the publish transaction; the export
  includes them, but they are not compared row by row. Only "each live story has at least one moment" is checked.

## What the drill does NOT cover

1. **Media objects.** Neither the files under `public/media/` nor the Supabase Storage bucket are exported or
   restored. `media_asset` rows are exported and their paths are in the documents, but a drill target shows no
   images. **Media coverage is out of scope for Agent B and is Agent A's responsibility** (Storage upload and the
   media-presence check). Do not call the restore complete until Agent A's check also passes.
2. **Numeric bigint IDs.** `id` columns are database-assigned and are not in the export or in the seed. The
   reconciliation matches slugs, keys and ordered positions only. Nothing external refers to numeric ids (URLs and
   files use slugs), but any future feature keyed on an id would not survive a restore.
3. **Preview rows and user-generated rows.** The drill publishes `live` only. Rows with `status = 'preview'` are not
   in any `v_live_*` view and are not exported. The schema has no other user-generated content today; any table
   added later is not covered until this script's section list is updated.
4. **`relation_evidence`.** Exported (DB-only), but the seed has no evidence data, so a seed restore loses it. The
   reconciliation prints a note when the export has evidence rows. This is a known gap, not a passing check.
5. **Positions that the seed and publish number differently.** Facet positions are 0-based in the seed and 1-based
   in the publish mirror. Positions are not compared. Node `x` and `y` are not compared.
6. **`site_settings`** is written by a migration, not from Git. The drill checks it against `site.json`, but the
   `papers` list in `site.json` is not restored or reconciled (the runtime does not read it).
7. **Derived-row detail.** Moments, facts, citations and media rows are not compared one by one; they come from the
   document through publish's transform.
8. **Auth, RLS and grants.** Users, policies and grants are created by the migrations, not checked against a live
   project by this drill. Live RLS and view-grant checks are the V1 merge gate's "target project schema/RLS" item.
9. **The live project itself.** The drill proves Git -> DB -> export consistency in a clean project. It does not prove
   that the live project matches Git. Use the live check below for that.

## Live check (owner, read-only)

This reads the live project and writes nothing to it. It writes a snapshot, which contains live content, to a
directory outside the repo:

```bash
EXPORT_DIR="$(mktemp -d)"
node --experimental-strip-types --disable-warning=ExperimentalWarning --env-file=.env scripts/export-supabase.ts --out "$EXPORT_DIR"
node --experimental-strip-types --disable-warning=ExperimentalWarning scripts/reconcile-export.ts --export "$EXPORT_DIR"
rm -rf "$EXPORT_DIR"   # the snapshot holds live content
```

Items the seed does not carry (such as `relation_evidence`) are printed as notes, not failures. Treat any mismatch
as a finding to read, not something to suppress. This check has not yet been run against the live project.

## Safety rules (built into the scripts)

- `export-supabase.ts` opens `begin read only`, uses only views and `select` queries, and refuses an `--out` inside the
  repository.
- `restore-drill.ts` refuses without **both** `--target-url` and `--confirm-disposable`. It refuses when the target's
  project ref (pooler user `postgres.<ref>` or host `db.<ref>.supabase.co`) equals the live ref from `.env`, or when
  the two URLs match on host, user and database. It refuses if either ref cannot be read, unless the target is
  localhost. It refuses if any `public` table has rows. Its child steps receive only `SUPABASE_DB_URL` set to the target.
- No script prints a connection string, password or key. Only hostnames are printed.
- `reconcile-export.ts` verifies file sha256 values, so an edited snapshot cannot pass silently.

## Cleanup

- Delete the drill project, or pause it, when the drill is finished.
- Delete the export directories: they hold content.
