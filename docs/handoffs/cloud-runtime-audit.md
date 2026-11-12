# Cloud-runtime and deployment audit (Agent D)

Scope: read-only audit of the browser runtime, Supabase view usage, prerender snapshot, Vercel routing and env names, and a no-rebuild acceptance procedure. No live DB query, no Vercel change, no env value printed, no deploy. Branch `v1`.

## 1. Forbidden runtime reads (seed or local JSON)

Result: **zero runtime reads.** No file in `src/` imports or fetches `data/seed/*.json`, `public/data/*.json`, or any `*.json`.

- Command: `node --experimental-strip-types --disable-warning=ExperimentalWarning scripts/check-runtime-sources.ts`
- Output: `src: scanned 43 files, 0 hit(s).` / `dist: scanned 15 files, 0 hit(s).` / `public/data: absent (ok).` / `OK: no runtime path reads or fetches local story/editorial JSON.` Exit 0.
- Negative test: a planted `fetch('/data/library.json')` at the end of a copy of `src/main.tsx` produced `src/main.tsx:32: ...` and exit 1.
- Comment-only mentions remain and are intentionally ignored: `src/types.ts:102` (`seeded from data/seed/tags.json`), `src/vite-env.d.ts:4` (`site.json`).
- Only network fetch besides Supabase: `src/components/MediaView.tsx:20` fetches SVG media (not JSON).
- `public/data/` does not exist. `vercel.json` still excludes `data/` from the SPA rewrite (harmless with no files there).

## 2. Supabase views read by the runtime (`src/data/source.ts`)

Client: `src/data/source.ts:15-27` (URL and publishable key only). Preview switch: `source.ts:33`.

**Live set (default, `VITE_SHOW_PREVIEW` unset):** `v_live_story` (list and by-slug, `source.ts:35`), `v_live_library_entry` (`:35`), `v_live_moment` (`:35`).

**Preview set (only when `VITE_SHOW_PREVIEW === '1'`):** `v_preview_story`, `v_preview_story_by_slug` (RPC, `source.ts:163`), `v_preview_library_entry`, `v_preview_moment` (`source.ts:37-40`).

**Shared, read in both modes (not status-gated):** `v_site` (`:121`), `v_facet` (`:141`), `v_tag` (`:142`), `v_field` (`:201`), `v_volume` (`:211`), `v_issue` (`:217`), `v_issue_story` (`:218`), `v_company` (`:249`), `v_company_post` (`:250`), `v_company_built_on` (`:251`), `v_storyline` (`:277`), `v_storyline_step` (`:278`), `v_node` (`:301`), `v_relation` (`:318`), `v_front_placement` (`:332`).

`v_live_fact` and the other `v_live_*` views in the migrations (`v_live_story_tag`, `v_live_citation`, `v_live_media_asset`, `v_live_story_field`) are not read by the runtime.

## 3. Inline prerender snapshot vs. seed file

- **Not a file read.** The snapshot is generated in the browser at prerender time from the same Supabase views, then embedded in the HTML.
- Producer: `src/App.tsx:201-202` calls `makeInitialData` and `window.__collect_initial_data__` only when `window.__gt_prerender__` is set. `src/data/initial-snapshot.ts:37-46` builds the envelope (`schemaVersion`, `route`, `source: 'supabase'`, `hideSamples`, `archive`, optional `edition`).
- Embedding: `scripts/prerender.ts:95-105` extracts `window.__initial_data_json__`; `:128-133` escapes `<`, U+2028 and U+2029, rejects `</script` and `<!--`, and inserts `<script id="__initial_data__" type="application/json">…</script>` immediately before `</body>` in `dist/<route>/index.html`.
- Hydration: `src/main.tsx:13` skips reading the snapshot during prerender (`__gt_prerender__`). `:20-27` hydrates when `readInitialData()` returns data, else `:28-30` uses `createRoot`. `window.__mount_mode__` records `'hydrated'` or `'created'` (`main.tsx:21`, `:29`).
- Validation: `src/data/initial-snapshot.ts:58-86` rejects the snapshot unless its route equals the current route, `source === 'supabase'`, `hideSamples` matches the current build flag, and the DOM has one wrapper with a `<main>`.
- Snapshot is first paint only. `src/App.tsx:146-162` runs a fresh `load()` after hydration and replaces the view if it differs. Failures show "Could not check for updates" (`App.tsx:161`).
- Consequence: the snapshot can be stale after a publish. A new story is visible only after the post-hydration read, and a new route with no prerendered file always takes the `createRoot` path.

## 4. Vercel routing and environment

- `vercel.json:3` rewrites every path except `assets/`, `data/`, `media/`, `favicon.ico`, `robots.txt`, `sitemap.xml` to `/index.html`. Deep links such as `/papers/<slug>` fall through to the SPA.
- Static prerendered files are served before the rewrite (Vercel behaviour; not re-verified here).

**Required on Vercel (Production and Preview as needed; values never recorded here):**
- `VITE_SUPABASE_URL`: required. `src/data/source.ts:15-17` throws if empty. Also needed at prerender (`scripts/prerender-routes.ts:65-71`).
- `VITE_SUPABASE_PUBLISHABLE_KEY`: required (same places).

**Optional runtime names:**
- `VITE_MEDIA_BASE_URL` (`src/data/load.ts:19`): overrides `site.mediaBaseUrl`.
- `VITE_HIDE_SAMPLES` (`src/data/initial-snapshot.ts:42`, `:70`): must match between prerender build and runtime, or the snapshot is rejected.

**Must be UNSET on Vercel production:**
- `VITE_SHOW_PREVIEW` (`src/data/source.ts:33`). Only the value `1` enables preview views.

**Server-side only, must never be on the static site build or prefixed `VITE_`:** `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_DB_URL`, the `CONVERT_*`/provider keys.

**Stale local entry:** `.env` (gitignored) contains `VITE_DATA_SOURCE`. Nothing in `src/` reads it. Do not copy it to Vercel.

Build inputs to remember: `.env` is local only (Vercel builds do not see it). Vite inlines every `VITE_` name it finds at build time.

## 5. Preview-status leak analysis

- **Bundle level: no leak when the flag is unset.** `source.ts:33` evaluates false, so only `v_live_*` names are reached. The preview view names remain as dead strings in the bundle, which is harmless.
- **Snapshot level: depends on the build flag.** The snapshot is produced by the same bundle during prerender (`App.tsx:201`). A prerender built with `VITE_SHOW_PREVIEW=1` embeds preview rows into the HTML. A flag-off build embeds only live rows.
- **Current local bundle is a dev build.** `dist/assets/index-DgiRncnE.js` contains `VITE_SHOW_PREVIEW:\`1\`` (grep of the bundle). The current `dist/` must not be deployed. Rebuild with the flag unset before any production deploy, and make sure the local `.env` flag is not used for that build.
- **Database level: preview rows are readable by anyone with the publishable key.** `supabase/migrations/20261108120000_preview_status.sql:37-38` adds an anon SELECT policy on `published_version` where `status = 'preview'`. Lines `:255-266` grant anon SELECT on `v_preview_story`, `v_preview_library_entry`, `v_preview_moment`, `v_preview_fact`, `v_preview_media`, `v_preview_citation`, `v_preview_story_field`, and EXECUTE on `v_preview_story_by_slug`. The migration header says this is "by design". So the statement "preview rows cannot leak" holds for the built site only. It does not hold for the API. This is a decision for the owner, not changed here.
- `v_preview_moment` (and `v_live_moment`) are owner-rights views without `security_invoker`. Their status and sample filters are the only gate.

## 6. No-rebuild acceptance procedure (owner runs; not executed by this agent)

Preconditions: a deployed build with `VITE_SHOW_PREVIEW` unset, env names from section 4 set, and a snapshot strategy confirmed (see section 7). Use a disposable test story slug. Do not change Vercel settings during the procedure.

1. **Publish as preview (owner write).** `npm run publish:supabase` for the test story. Confirm it is `preview` with `npm run status`. Before this, record the baseline: home lead/aside/more, search results for a term unique to the story, and the story URL returning the SPA shell.
2. **Negative check.** Load the deployed `/`, `/?search&q=<term>`, and `/papers/<slug>/`. The story must be absent. Network must show no `v_preview_*` request.
3. **Approve (owner write).** `npm run approve <slug>` (service role, `approve_version`). Do not rebuild or redeploy.
4. **Positive check after a hard reload.** The story appears in home (front-page derivation in `src/data/load.ts:225-260`), in `/?search&q=<term>`, and at `/papers/<slug>/` (direct load; the SPA rewrite serves `index.html`, so `window.__mount_mode__` should be `'created'`).
5. **Network assertions.** Record every request during each load and assert:
   - **DB reads (Supabase REST, `<project>.supabase.co/rest/v1/`):** `v_site`, `v_live_story` (list, and `story_slug=eq.<slug>` for the direct URL), `v_live_library_entry`, `v_live_moment`, plus the shared views in section 2. All return 200. The `v_live_story` response contains the new slug. Zero requests to `v_preview_*`. Note: the post-hydration request (`App.tsx:148-162`) must appear as a second `v_live_story` read.
   - **Inline bootstrap (no network):** the first HTML response for a prerendered route contains `id="__initial_data__"`. Confirm `window.__mount_mode__` via the browser (`hydrated` for prerendered routes, `created` for the new story route). No request is made for the snapshot.
   - **Media:** requests under `media/` (or the Storage origin if `site.media_base_url` / `VITE_MEDIA_BASE_URL` points there, e.g. `<project>.supabase.co/storage/v1/object/public/...`). All return 200 and none go to `/rest/v1/`. Zero `*.json` requests on the origin or `/data/`.
6. **Cleanup (owner write).** Retire or unpublish the test story and confirm it disappears on reload. Note the owner-only actions in the release log.

## 7. Unresolved issues

1. **Preview rows readable via the API** (section 5). Owner decision: revoke anon on `v_preview_*` (and the RPC), or accept the migration's "by design" note and rely on the bundle gate.
2. **Local `dist/` is a dev build** with `VITE_SHOW_PREVIEW=1` inlined. Rebuild with the flag unset before any production deploy.
3. **Vercel build command not visible from the repo.** There is no `.vercel/` config and `vercel.json` has no `buildCommand`. `dist/` is gitignored and prerender needs a local Chromium (puppeteer). `codex-2026-11-09.md` says the build must run `npm run build && npm run prerender`. Unless Vercel does, there is no inline snapshot and the step-5 bootstrap assertion will show the `created` path. Owner must confirm.
4. **Media base unverified.** `data/seed/site.json:7` sets `mediaBaseUrl: "media/"` (local, relative). The live `site_settings.media_base_url` cannot be checked without a live read, which this audit did not do. Until it points at Storage, criterion 12 (media from Supabase Storage) is not met. Agent A's scope.
5. **Nothing was run against the live DB, Vercel, or a browser.** The checker was tested only locally (clean run and planted hit). Section 6 is a procedure, not evidence.

## Checker wiring (for the orchestrator)

`scripts/check-runtime-sources.ts` needs no env file. Suggested `package.json` entry (not added by this agent):
`"check:runtime": "node --experimental-strip-types --disable-warning=ExperimentalWarning scripts/check-runtime-sources.ts"`.
Run it after `npm run build` so the `dist/` pass is included.
