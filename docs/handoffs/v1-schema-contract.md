# V1 schema contract — frozen for Phase 3b

Lead-authored. Agents A/B/C/D read this before writing anything. Table names, key columns and publish inputs are frozen here; raise an issue in your report, do not rename unilaterally.

Hybrid model (owner's call, clarifies decision 38):
- Keep each complete, immutable story version in `published_version.document jsonb`. The ordered blocks, panels and captions belong there — the document is the source of truth.
- Put data queried across pages or independently into separate tables.
- Reference other rows with indexed `<thing>_id bigint` columns containing their numeric IDs.
- **No `REFERENCES` constraints anywhere.** Public views and functions join explicitly on those id columns. Publishing validates every reference inside the transaction and fails on any missing one.

The initial migration (`20261106085857_init_story_slice.sql`) is **applied remotely**. Do not edit it; add new additive migrations instead.

## Agreed file ownership

| Agent | Owns | New migration file (filename frozen here) |
|---|---|---|
| A — core content | tables for source, media, tag vocabulary, extracted moment/fact/citation; metadata columns on `published_version` | `supabase/migrations/20261106100000_core_content_schema.sql` |
| B — editorial & collections | volume, issue, company, storyline, field, graph node + relation + evidence, front placement | `supabase/migrations/20261106100001_editorial_schema.sql` |
| C — importer | `scripts/publish-to-supabase.ts` rewrite (one `pg` transaction) + content reconciliation report | no SQL files |
| D — history, views, RLS, docs | public views/RPCs that join the normalized tables and expose only live/non-sample/verified rows | `supabase/migrations/20261106100002_public_views_rls.sql` |

Lead applies them in the order A → B → D. Agent C's importer runs after all three are applied.

## Shared conventions (all migrations)

- Primary keys: `bigint generated always as identity primary key`.
- Public keys: `slug` or `key` text columns, unique and NOT NULL where present. Numeric ids are internal only; URLs, exports and cross-table references in files use slug/key (decision 35).
- Reference columns: `<thing>_id bigint NOT NULL` with an index. **No `REFERENCES` clause.**
- Version-owned rows carry `published_version_id bigint NOT NULL` and an index on it. Retiring a version makes those rows drop out of public reads via the view's `WHERE pv.status = 'live'`.
- Sample content: a `sample boolean NOT NULL DEFAULT false` column where the current library carries one.
- Enumerations (status, kind, trust, claim, basis, role, etc.) are `text CHECK (col IN (...))`, not Postgres enums — simpler migrations.
- Timestamps: `created_at timestamptz NOT NULL DEFAULT now()` on every new table.
- All new tables ship with `ENABLE ROW LEVEL SECURITY` and no public policy. Public reads go through Agent D's views only; raw tables stay invisible to `anon`.
- Add a check query per reference (orphan audit) to the migration as a comment block at the end.

## Frozen table names + key columns

### Core (Agent A)

| Table | Key columns | Notes |
|---|---|---|
| `story` (exists) | `id`, `slug UNIQUE`, `kind`, `live_version_id`, **add `sample boolean NOT NULL DEFAULT false`** | A migration altering the existing table is fine; it's additive. |
| `published_version` (exists) | `id`, `story_id`, `story_slug`, `schema_version`, `status`, `document jsonb`, `library_entry jsonb`, `created_at`, **add:** `headline text NOT NULL`, `accent text`, `dek text NOT NULL`, `summary text NOT NULL`, `page_title text NOT NULL`, `desk text NOT NULL`, `authors text NOT NULL`, `year int NOT NULL`, `trust text NOT NULL CHECK IN ('peer_reviewed','preprint','company_reported')`, `minutes int NOT NULL`, `role text CHECK IN ('lead','feature','brief','vault','real_world')`, `note text`, `source_url text NOT NULL`, `source_archived_url text` | `library_entry` is **transitional**: keep it for now; Agent D's views can prefer the explicit columns. |
| `source` | `id`, `kind text CHECK IN ('paper','blog')`, `title`, `authors text`, `year int`, `url text NOT NULL`, `organization text` (blog only), `trust text CHECK IN ('peer_reviewed','preprint','company_reported')`, `created_at` | One row per distinct paper or post. `url` is the canonical identifier within a kind. |
| `source_snapshot` | `id`, `source_id`, `archived_url text NOT NULL`, `retrieved_on date NOT NULL` | For Wayback captures. Zero to many per source. |
| `story_source` | `id`, `published_version_id`, `source_id`, `role text CHECK IN ('primary','secondary')`, position int | Version-owned so a version rewrite may change its sources. |
| `citation` | `id`, `published_version_id`, `source_id`, `anchor text` (e.g. `§3.1` or `#S3.SS2`), `url text NOT NULL`, `label text NOT NULL`, `context text` | Version-owned. One row per source-link appearance in the document. |
| `media_asset` | `id`, `published_version_id`, `path text NOT NULL`, `kind text CHECK IN ('svg','image','video')`, `width int NOT NULL`, `height int NOT NULL`, `alt text` | Version-owned (SVGs live under `public/media/<slug>/`, scoped to story). UNIQUE `(published_version_id, path)`. |
| `facet` | `id`, `key text UNIQUE NOT NULL` (e.g. `field`, `area`, `concept`), `label text NOT NULL`, `position int` | 13 rows, sourced from `tags.json`. |
| `tag` | `id`, `key text UNIQUE NOT NULL` (e.g. `field/computer-science`), `facet_id bigint NOT NULL`, `label text NOT NULL`, `aliases text[]` | ~93 rows. `aliases` as text[] (no join table — small, read-together). |
| `story_tag` | `id`, `published_version_id`, `tag_id`, `relevance numeric`, `basis text CHECK IN ('paper','background','editorial')`, `evidence text`, `source_kind text`, `status text CHECK IN ('approved','proposed','rejected')` | Version-owned. The current validator already enforces `approved`-only in published stories. |
| `moment` | `id`, `published_version_id`, `key text NOT NULL`, `kind text CHECK IN ('lead','hook','chapter','strip_panel','fact')`, `position int`, `claim text CHECK IN ('illustration','model_design','measured_result')`, `trust text` (nullable; illustration has none), `source_label text`, `source_url text`, `media_asset_id bigint`, `headline text`, `text text`, `ref text` (anchor into document) | UNIQUE `(published_version_id, key)`. Replaces the generated `search-index.json` for runtime reads in a later batch. |
| `fact` | `id`, `published_version_id`, `block_id text NOT NULL`, `position int`, `figure text NOT NULL`, `claim text CHECK IN (...)` as above, `text text NOT NULL`, `source_label text`, `source_url text`, `media_asset_id bigint` | Version-owned; one per `facts[].facts[]` item. |

### Editorial (Agent B)

| Table | Key columns | Notes |
|---|---|---|
| `volume` | `id`, `slug text UNIQUE NOT NULL`, `title text NOT NULL`, `kind text CHECK IN ('regular','special')` | 2 rows today. |
| `issue` | `id`, `slug text UNIQUE NOT NULL`, `volume_id bigint NOT NULL`, `title text NOT NULL`, `color text`, `published text` (free-form today; promote to `date` in a later batch), `cover_story_id bigint`, `sample boolean NOT NULL DEFAULT false`, `position int` | 5 rows (1 real, 4 sample). |
| `issue_story` | `id`, `issue_id`, `story_id`, `position int` | Join; preserves order. |
| `company` | `id`, `slug text UNIQUE NOT NULL`, `name text NOT NULL`, `sector text`, `blurb text`, `posts_followed int`, `coming jsonb` (placeholder strings — presentation), `sample boolean NOT NULL DEFAULT false` | 4 rows (1 real: Uber; 3 sample). |
| `company_post` | `id`, `company_id`, `story_id`, `position int` | Join. |
| `company_built_on` | `id`, `company_id`, `node_id`, `position int` | Join — companies claim they are built on graph nodes. |
| `storyline` | `id`, `slug text UNIQUE NOT NULL`, `title text NOT NULL`, `sample boolean NOT NULL DEFAULT false` | 2 rows (both real-ish). |
| `storyline_step` | `id`, `storyline_id`, `position int`, `year text`, `label text`, `current boolean DEFAULT false`, `story_id bigint` (nullable — not every step maps to a story we explain) | |
| `field` | `id`, `slug text UNIQUE NOT NULL`, `label text NOT NULL`, `color text`, `cluster jsonb` (map cluster coords: cx/cy/rx/ry/labelX/labelY) | 5 rows. `cluster` is presentation-only but travels with the field row. |
| `node` | `id`, `slug text UNIQUE NOT NULL`, `title text NOT NULL`, `authors text`, `year int`, `field_id bigint`, `kind text CHECK IN ('paper','blog')`, `x int`, `y int`, `story_id bigint` (nullable), `sample boolean NOT NULL DEFAULT false` | 22 rows. |
| `relation` | `id`, `source_node_id bigint NOT NULL`, `target_node_id bigint NOT NULL`, `kind text CHECK IN ('builds_on','improves_on','uses_method','cited','family')`, `note text`, `verified boolean NOT NULL DEFAULT false`, `sample boolean NOT NULL DEFAULT false` | Add every `kind` value seen in current data. **Unverified / sample relations must be excluded from Agent D's public view.** |
| `relation_evidence` | `id`, `relation_id`, `source_id`, `url text`, `note text` | For `cited: true` relations once we add proper evidence. |
| `front_placement` | **ONE jsonb document** (singleton table or settings row). Columns: `id`, `key text UNIQUE` (always `'current'` for now), `data jsonb NOT NULL`. `data` matches today's `library.json` `front` block shape | Front slots change together editorially; rows-per-slot would be chatty. Document the shape in the migration comment. |
| `story_field` | `id`, `published_version_id`, `field_id`, `position int` | Version-owned since `library.stories[].fields[]` is per-version metadata. |

### Importer / publish transaction (Agent C)

The whole publish unit runs in **one `pg` transaction**, server-side, using the service-role / DB-URL path. No separate HTTP calls to Supabase from the importer; use `pg` directly (`SUPABASE_DB_URL`). Steps inside the single transaction:

1. `SELECT id FROM story WHERE slug = $1 FOR UPDATE`; if absent, `INSERT INTO story (slug, kind, sample) VALUES (...) RETURNING id`.
2. Validate the PaperDoc: `schemaVersion = 2`, every `fact.claim` present, every tag approved, every referenced `source.url` present on the `facts`/`moments`.
3. Upsert sources by `(url, kind)` into `source`; insert `source_snapshot` rows if archived.
4. `INSERT INTO published_version (...)` with `status='staging'`, the full document, the library entry (transitional), and the explicit metadata columns.
5. Extract and insert: `story_source`, `citation`, `media_asset`, `story_tag`, `moment`, `fact`, `story_field` — each row carries this `published_version_id`.
6. Orphan audit on the staged rows: every `_id` in the new rows resolves within staged + existing live rows.
7. Call `publish_version(bigint)` (the existing RPC) to promote: it retires the previous live row, flips this one to live, and updates `story.live_version_id`. A failure anywhere → rollback and old live stays authoritative.
8. Emit a reconciliation report at the end (counts, keys, document hash).

Negative cases the CLI must handle without leaving partial state:
- Missing referenced id (bad tag slug, bad source url format): abort, rollback, keep previous live.
- Mismatched story slug between PaperDoc and library entry: abort.
- Invalid claim/trust/role/basis: abort.
- Unchanged rerun (same document hash): no-op by default; log the skipped version. (Document the rule.)

### Public reads (Agent D)

- Raw tables keep their `ENABLE ROW LEVEL SECURITY` with no public policy.
- `anon` gets `SELECT` only on the views/RPCs below. Revoke `SELECT` on raw tables from `anon`/`authenticated`.
- Views use `security_invoker = true` (Postgres 15+) so RLS and grants apply to the viewer.
- Required views (final names are frozen; Agent D may add more):
  - `v_live_story` — joins `story` + current live `published_version`; returns every non-sample live story's metadata columns + the `document` + `library_entry` (transitional).
  - `v_live_story_by_slug(slug)` — SQL function, `security_invoker`, returns one row.
  - `v_live_library_entry` — returns `(story_slug, library_entry)` across all live non-sample stories (fuels the home-page overlay the frontend already uses).
  - `v_live_moment`, `v_live_fact`, `v_live_story_tag`, `v_live_citation`, `v_live_media_asset`, `v_live_story_field` — join each extracted table to its `published_version` and keep only `status = 'live'` and the parent story non-sample.
  - `v_facet`, `v_tag` — full vocabulary, always readable.
  - `v_volume`, `v_issue`, `v_company`, `v_storyline`, `v_field`, `v_node` — non-sample rows only. For a sample-inclusive design-review mode, add a parallel `_all` view or leave it to a later batch.
  - `v_relation` — `verified = true AND sample = false` only.
  - `v_front_placement` — the current row.
- Migration history: write up ONE path (the repo's `npm run apply:migration` applier; the Supabase CLI path is optional and only used if `supabase link` has been set up). Reconcile the already-applied initial migration by inserting its record into `supabase_migrations.schema_migrations` (on Supabase's own tracking table) if and only if the CLI path is adopted. If not, document that the applier is the record of record.

## Orphan audits (every agent)

Each migration ends with a commented block listing one SQL query per reference column, of the form:

```sql
-- orphan audit: every story_tag.tag_id must resolve
-- select st.id from story_tag st left join tag t on t.id = st.tag_id where t.id is null;
```

Lead runs these after apply. Any hit fails the batch.

## What stays file-backed for now (not a V1 bug)

- `site.json` entirely (site name, motto, mediaBaseUrl, default paper, papers list for file mode).
- `tags.json` as the editorial seed; mirrored into `facet` + `tag` tables by Agent C's importer. Readers can still read the file in file mode.
- `search-index.json` (generated), prerendered HTML, media files — all moved later.
- `library.json` as the shell for front-page layout, sample content and anything not yet written to the DB. Real data imported by Agent C overlays the file-backed shell as today.

## Not in this batch

ResNet conversion, copy / ledger cleanup, archive-page design, media CDN, OG cards, Next.js migration, feed/search runtime loaders. Zero visual changes.

## Acceptance (lead)

1. Back up current remote with `pg_dump` to the session scratchpad.
2. Apply A, B, D in order via `npm run apply:migration`.
3. Run Agent C's importer for `attention-is-all-you-need`, `size-shapes-life`, `h3-hexagons`.
4. Positive: attention still readable; new stories live; views return the right counts; no row leaks.
5. Negative: synthetic bad publish must rollback with old live intact.
6. Orphan audit queries all empty.
7. Browser: `/`, `/papers/<slug>` for all three real stories at 1280 and 375. No console errors; stamps correct.
