# Supabase loader cutover: `published_version` to `v_live_*` views (Wave 2 plan)

Status: plan only. No code changed. Branch `v1`, base `8d05423`.
Owner of the change: Wave 2 B. Decisions in play: 48 (runtime Supabase reads, no silent fallback), 49 (views are the public read layer).

### 1. Current reads (before)

`src/data/source-supabase.ts` makes two REST reads against the raw `published_version` table, both with the publishable key:

- `fetchStoryDoc(slug)` runs `readLiveDoc` (lines 27-44). Query at lines 29-34:
  `from('published_version').select('schema_version, document').eq('story_slug', slug).eq('status', 'live').maybeSingle()`.
  Error wrap at line 35, not-found throw at line 36, schema checks at lines 41-42.
- `fetchLiveLibraryEntries()` runs `readLiveLibrary` (lines 46-63). Query at lines 48-51:
  `from('published_version').select('story_slug, library_entry').eq('status', 'live')`.
  Error wrap at line 52. Per-row checks at lines 56-59, including the duplicate guard `entries.has(row.story_slug)` at line 59.
- Stale comments that describe the old table: header lines 1-2 (RLS on `published_version`), line 8 (`published_version?status=eq.live`), line 27, line 46.
- Per-page-load cache: `docs` Map (line 72) and `library` promise (line 73), wired in `fetchStoryDoc` (lines 77-84) and `fetchLiveLibraryEntries` (lines 85-88).

### 2. Target reads (after)

- `fetchStoryDoc(slug)`: `from('v_live_story').select('schema_version, document').eq('story_slug', slug).maybeSingle()`.
  The `.eq('status', 'live')` line is removed. The view's WHERE already applies `pv.status = 'live' and s.sample = false` (migration `20261106100002_public_views_rls.sql`, `v_live_story`, around lines 50-70).
- `fetchLiveLibraryEntries()`: `from('v_live_library_entry').select('story_slug, library_entry')`. The `.eq('status', 'live')` line is removed.

Columns: confirmed against the migration. `v_live_story` returns `story_slug`, `schema_version`, `document`, `library_entry` and the metadata columns. `v_live_library_entry` returns `(story_slug, library_entry)`.

Contract source: `docs/handoffs/supabase-view-contract.md` does NOT exist (it is not in `docs/handoffs/`, and nothing references it). The contract is the "Public reads (Agent D)" section of `docs/handoffs/v1-schema-contract.md` (lines 93-107), plus the migration itself. The lead should confirm that is the intended contract before Wave 2 B starts. This plan follows the migration, which matches that section. The migration also defines `v_live_story_by_slug(text)` (line 301), which is an alternative to `v_live_story` with `.eq`. This plan does not use it, because the brief asks for `v_live_story`. Using the function would need `.rpc(...)`.

### 3. Shape preservation (the loader's output contract)

The loader still returns `row.document as PaperDoc` and each `library_entry as LibraryStory`, as it does today. UI components are not touched. The `storyVersionMessage` check on `schemaVersion` (lines 41-42) stays, and it checks both `doc.schemaVersion` and the row's `schema_version`. The `hideSamples` and `overlayLive` logic in `src/data/load.ts` is unchanged.

No reshape across the loader boundary. The views expose the same jsonb columns the table does, so no mapping is needed.

### 4. Error paths to preserve

- Unpublished slug (zero rows from the view): throw `Story “<slug>” has no live version in Supabase.` (line 36). The view now returns zero rows for sample stories too, so this message also covers them. This is the correct outcome.
- PostgREST error: keep `Could not read story “<slug>” from Supabase: <error.message>` (line 35) and `Could not read live library entries from Supabase: <error.message>` (line 52).
- Multi-row guard `entries.has(row.story_slug)` (line 59) stays. The view is unique per slug, but the guard is defence in depth.
- Source selection and no-fallback rule (decision 48) are unchanged: `src/data/source.ts` still throws on a Supabase error and never falls back to the file source.

### 5. Cache + sequence token

No changes. The per-slug `docs` cache, the per-page-load `library` cache, and the `sequence` token in `src/App.tsx` (around lines 150-165, the Supabase post-hydration refresh) keep their semantics. The refresh still calls `load(currentRoute())`, which calls `loadArchive()` and `loadEdition()`, so both new reads run in that branch.

### 6. Network-level acceptance

`puppeteer` is already a devDependency (`package.json`, `^25.16.0`). Verification steps for Wave 2 B:

1. Run the dev server with `VITE_DATA_SOURCE=supabase` and the project's `.env` values.
2. With puppeteer, load `/`, `/papers/<real-slug>`, and `/feed`. Record every request whose URL contains `/rest/v1/`.
3. Assert zero matches for `/rest/v1/published_version` (match the path without the `?`, so the check also catches requests with no query string).
4. Assert that `/rest/v1/v_live_story?` and `/rest/v1/v_live_library_entry?` each appear at least once on the paper and home routes.
5. Assert the page renders the same story text as before the cutover (diff the `document` headline against the pre-cutover run).

### 7. Files Wave 2 B will touch

- `src/data/source-supabase.ts` only. Edits: the two `.from(...)` calls, the two `.eq('status', 'live')` removals, and the comments at lines 1-2, 8, 27, 46.

No other file is required:
- `src/data/source.ts`, `src/data/load.ts`, `src/data/initial-snapshot.ts` and `src/App.tsx` consume the loader's return types, which do not change.
- `scripts/publish-to-supabase.ts` writes the table and is out of scope.
- `docs/decisions.md` entry 48 still says "`GET published_version WHERE ...`" (the "Public read contract" bullets). Updating that text would be a docs change, so it needs the lead's sign-off. Flag it, do not edit it in Wave 2 B.
- `STATE.md`, if it names the read path, is also out of scope unless the lead asks.

### Risks

1. **Missing contract doc.** `docs/handoffs/supabase-view-contract.md` does not exist. The lead should confirm `v1-schema-contract.md` lines 93-107 is the contract, or the view contract should be written first.
2. **Sample-story behavior change.** The view filters `sample = false`. A `/papers/<slug>` route for a sample story still goes to the `sample` page in `src/App.tsx` `load()` (line 66) because `story.real` is false in the shell. A story whose shell says `real: true` but whose DB row has `sample = true` would now throw "no live version". This mismatch should not happen, but the lead should confirm `real` and `sample` agree in the seed.
3. **Stale comments.** Leaving the comments at lines 1-2 and 8 would mislead the next reader about which table is read.
4. **Dev-only verification.** Section 6, step 5, compares rendered text, so the baseline must be captured on the pre-cutover commit (`8d05423`) before Wave 2 B changes the file.
5. **Decision 48 text.** The decision describes the old reads. It should be amended by the lead, not silently by the loader change.
