# Supabase view contract for the Wave 2 loader

Scope: the two public views the loader reads after the cutover from raw `published_version` (decision 49). Derived from `supabase/migrations/20261106100002_public_views_rls.sql`, the lead patch `20261106120000_patch_v_issue_number.sql`, the base tables in `20261106085857_init_story_slice.sql`, `20261106100000_core_content_schema.sql` (story.sample, published_version metadata columns, story.kind CHECK) and `src/data/source-supabase.ts`. Verified against migration text only, not against a live database.

### 1. Views in play

**`v_live_story`** (`security_invoker = true`)

```sql
create view v_live_story with (security_invoker = true) as
select
  s.slug as story_slug, s.kind,
  pv.schema_version, pv.headline, pv.accent, pv.dek, pv.summary, pv.page_title, pv.desk,
  pv.authors, pv.year, pv.trust, pv.minutes, pv.role, pv.note, pv.source_url, pv.source_archived_url,
  pv.document, pv.library_entry, pv.created_at as version_created_at
from story s
join published_version pv on pv.story_id = s.id
where pv.status = 'live' and s.sample = false;
```

Output columns, in order (Postgres type → TypeScript):

| # | Column | Postgres | Source | TypeScript |
|---|---|---|---|---|
| 1 | `story_slug` | text, NOT NULL | `story.slug` | `string` |
| 2 | `kind` | text, NOT NULL, CHECK in (paper, blog, classic) | `story.kind` | `'paper' \| 'blog' \| 'classic'` |
| 3 | `schema_version` | int, NOT NULL | `pv` | `number` |
| 4 | `headline` | text, NOT NULL | `pv` | `string` |
| 5 | `accent` | text, NULL | `pv` | `string \| null` |
| 6 | `dek` | text, NOT NULL | `pv` | `string` |
| 7 | `summary` | text, NOT NULL | `pv` | `string` |
| 8 | `page_title` | text, NOT NULL | `pv` | `string` |
| 9 | `desk` | text, NOT NULL | `pv` | `string` |
| 10 | `authors` | text, NOT NULL | `pv` | `string` |
| 11 | `year` | int, NOT NULL | `pv` | `number` |
| 12 | `trust` | text, NOT NULL, CHECK in (peer_reviewed, preprint, company_reported) | `pv` | `'peer_reviewed' \| 'preprint' \| 'company_reported'` |
| 13 | `minutes` | int, NOT NULL | `pv` | `number` |
| 14 | `role` | text, NULL, CHECK in (lead, feature, brief, vault, real_world) | `pv` | `StoryRole \| null` |
| 15 | `note` | text, NULL | `pv` | `string \| null` |
| 16 | `source_url` | text, NOT NULL | `pv` | `string` |
| 17 | `source_archived_url` | text, NULL | `pv` | `string \| null` |
| 18 | `document` | jsonb, NOT NULL | `pv` | `unknown` (cast to `PaperDoc`) |
| 19 | `library_entry` | jsonb, NOT NULL | `pv` | `unknown` (cast to `LibraryStory`) |
| 20 | `version_created_at` | timestamptz, NOT NULL | `pv.created_at` | `string` (ISO) |

**Cardinality:** at most one row per story. `published_version_one_live_per_story_idx` is a unique index on `(story_id) where status = 'live'`. The view returns one row per live, non-sample story.

**WHERE:** `pv.status = 'live'` and `s.sample = false`. A staging or retired version never appears. A sample story never appears. No other filters.

**Grants:** `grant select ... to anon` on `v_live_story` is present (migration section 6). Anon needs no grant on the base tables for this view to work because the view is `security_invoker`. Anon reads `story` and `published_version` under the existing policies `story_public_read` (using true) and `published_version_public_read_live` (status = 'live'). The init migration's `grant select on story/published_version to anon` is unchanged. Nothing revokes raw `story` or `published_version` access (decision 48 kept). The `revoke all` lists in 100002 name only the new A/B tables and the views. Anon can still read raw `published_version` after the cutover, so the cutover does not tighten security by itself.

**`v_live_library_entry`** (`security_invoker = true`)

```sql
create view v_live_library_entry with (security_invoker = true) as
select story_slug, library_entry
from v_live_story;
```

| # | Column | Postgres | TypeScript |
|---|---|---|---|
| 1 | `story_slug` | text, NOT NULL | `string` |
| 2 | `library_entry` | jsonb, NOT NULL | `unknown` (cast to `LibraryStory`) |

**Cardinality and WHERE:** identical to `v_live_story`. It is a projection of it. Grant: `select` to anon, present.

### 2. TypeScript row types for the Supabase client

```ts
import type { LibraryStory, PaperDoc, StoryRole } from '../types';

/** public.v_live_story. One row per live, non-sample story. */
export interface LiveStoryRow {
  story_slug: string;                 // NOT NULL
  kind: 'paper' | 'blog' | 'classic'; // NOT NULL
  schema_version: number;             // NOT NULL
  headline: string;                   // NOT NULL
  accent: string | null;              // NULL
  dek: string;                        // NOT NULL
  summary: string;                    // NOT NULL
  page_title: string;                 // NOT NULL
  desk: string;                       // NOT NULL
  authors: string;                    // NOT NULL
  year: number;                       // NOT NULL
  trust: 'peer_reviewed' | 'preprint' | 'company_reported'; // NOT NULL
  minutes: number;                    // NOT NULL
  role: StoryRole | null;             // NULL
  note: string | null;                // NULL
  source_url: string;                 // NOT NULL
  source_archived_url: string | null; // NULL
  document: unknown;                  // NOT NULL, jsonb; cast to PaperDoc
  library_entry: unknown;             // NOT NULL, jsonb; cast to LibraryStory
  version_created_at: string;         // NOT NULL, timestamptz
}

/** public.v_live_library_entry. Same set of rows as v_live_story. */
export interface LiveLibraryEntryRow {
  story_slug: string;     // NOT NULL
  library_entry: unknown; // NOT NULL, jsonb; cast to LibraryStory
}
```

Supabase's generated types mark every view column nullable. The narrower types above are deliberate and match the DB, since the migration sets NOT NULL on the base columns. Keep runtime guards on `document`, `library_entry` and `schema_version`, as `source-supabase.ts` does today.

### 3. Shape reconciliation with PaperDoc

`PaperDoc` is `StoryDoc = PaperStoryDoc | BlogStoryDoc` in `src/types.ts`. Its top-level fields are `schemaVersion`, `slug`, `pageTitle`, `summary`, `cover?`, `hook?`, `desk`, `tags`, `blocks`, `kind?`, and `paper` or `blog`. `headline` and `dek` are not top-level fields; they live in the lead block.

Columns that overlap `document`:
- `summary` = `document.summary`
- `page_title` = `document.pageTitle`
- `authors`, `year`, `source_url` = from `document.paper` or `document.blog`
- `desk` and `trust` = `library_entry` first, `document` as fallback. They can differ from `document` in principle.

Fields only in `document`: `blocks`, `tags`, `cover`, `hook`, `slug`, `schemaVersion`, `paper`, `blog`.

Fields only in columns (from `library_entry`): `headline`, `accent`, `dek`, `minutes`, `role`, `note`.

**Recommendation: the loader keeps `row.document as PaperDoc` and ignores the scalar columns.** No reshape is needed and the UI contract holds. The `document` column is present in `v_live_story`, so this is not a blocker. Keep the existing `schemaVersion` checks, against `document.schemaVersion` and `row.schema_version`.

### 4. Shape reconciliation with LibraryStory

`v_live_library_entry` returns `(story_slug, library_entry)`. `library_entry` is jsonb and matches `LibraryStory` in `src/types.ts`: `id`, `sample`, `real?`, `headline`, `accent?`, `dek`, `desk`, `fields`, `role`, `kind`, `title`, `authors`, `year`, `trust?`, `art?`, `minutes`, `note?`, `company?`, `builtOn?`, `vaultNote?`. The shape has not changed.

Keep the loader's existing check that `library_entry.id === story_slug`. The view does not enforce it. `story_slug` is the key the overlay map uses.

`LibraryStory.sample` is always `false` for rows from this view, since the view filters `sample = false`.

### 5. Error cases

- **`v_live_story`, slug unpublished:** zero rows. PostgREST `.from('v_live_story').select(...).eq('story_slug', slug).maybeSingle()` returns `{ data: null, error: null }`. The loader must still throw "has no live version" when `data` is null, as it does today. `error` is only set for real failures.
- **`v_live_library_entry`, slug unpublished:** the row is absent from the array. The result is not an error. The overlay map simply has no key for that slug.
- **RPC alternative:** `v_live_story_by_slug(p_slug)` returns `setof v_live_story`. Via `.rpc()` an unpublished slug gives `[]`, not `null`. It is granted to anon, but the plan is to read the view directly.

### 6. Residual risks

1. **Sample-story behavior change.** The current `readLiveLibrary` reads every `published_version` where `status = 'live'`. The view also filters `story.sample = false`. If any sample story has a live version, its overlay entry disappears after the cutover. Check with a query before cutover: `select count(*) from published_version pv join story s on s.id = pv.story_id where pv.status = 'live' and s.sample`. The expected result is 0.
2. **Column authority.** `desk` and `trust` come from `library_entry` first. Use `document` for PaperDoc and `library_entry` for LibraryStory. Do not mix them.
3. **NULL-ability traps.** `role`, `note`, `accent` and `source_archived_url` are NULL-able in the DB. `LibraryStory.role` is required, so a NULL `role` is a data bug. `role` was not given NOT NULL, so the DB will not catch it. Validate it in the loader if it matters.
4. **Raw-table grant still open.** Anon can still read raw `published_version` (decision 48). The view is not the only path. Tightening that is a later step, not Wave 2.
5. **No `id` in the views.** Numeric ids are not returned (decision 35). Join on slug only.
6. **`v_issue` patch.** Adds `number` and re-grants anon SELECT. It does not affect this contract.
