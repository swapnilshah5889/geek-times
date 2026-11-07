# Routing and prerender map (as of `v1` @ `b49b8ad`)

Read-only audit for the cutover to Supabase-driven route enumeration. Every claim cites `file:line` as read on this commit. Nothing was built or run; the only file written is this one.

## 0. Summary

- **No router library.** `package.json` has no react-router. Routes are parsed by hand in `src/App.tsx` (`currentRoute()`).
- **`/papers/<slug>` is already one dynamic route** at the router level. `site.json` is not involved in matching it.
- **The per-paper list lives in two places:** the prerender enumerator (`scripts/prerender-routes.ts:67-69`) and the runtime lookup `loadEdition` (`src/data/load.ts:98-105`). The runtime lookup still applies in Supabase mode.
- **27 prerendered routes today:** 1 home, 3 real papers, 11 samples, 5 issues, `/issues`, 4 companies, `/companies`, `/map`.
- **The prerender script (`scripts/prerender.ts`) has no Supabase client.** It drives a browser against `vite preview`. The app in that browser does the Supabase reads, because `.env` sets `VITE_DATA_SOURCE=supabase`.

---

## 1. `src/App.tsx`

### How routes are registered

- No route table and no router component. `App()` (`src/App.tsx:90`) holds a `view` state. `currentRoute()` (`:41-58`) reads `window.location` and returns a discriminated union `Route` (`:22-26`).
- Parsing order in `currentRoute()`:
  1. `?paper=<slug>` (legacy): `history.replaceState` to `/papers/<slug>` (`:43-47`), then returns the paper route.
  2. First path segment `head`, second segment `second` (`:48-49`):
     - `papers/<slug>` gives `paper` (`:50`). `/papers` alone with no second segment falls through to the throw at `:54`.
     - `issues[/<id>]` gives `issue` (`:51`).
     - `companies[/<id>]` gives `company` (`:52`).
     - `map` (no second segment) gives `map` (`:53`).
  3. Any other non-empty path throws `There is no page at “/<path>”.` (`:54`).
  4. Empty path: `?feed` gives `feed` (`:55`), `?search`, `?q` or `?tag` gives `search` (`:56`), else `home` (`:57`).
- The path is read via `currentPath()` (`src/lib/routes.ts:14-18`), which strips `import.meta.env.BASE_URL` (`/`).
- Navigation: a document-wide click interceptor (`src/lib/navigation.ts:15-39`), a `popstate` listener (`src/App.tsx:146-148`), and a custom `geekytimes:navigate` event (`src/lib/navigation.ts:11`).

### Static routes and their components

| URL | Route value | Component (`src/App.tsx:244-253`) | Data |
|---|---|---|---|
| `/` | `home` | `HomePage` (`src/pages/HomePage.tsx`) | `archive` |
| `/?feed` | `feed` | `FeedPage` | `archive` |
| `/?search`, `?q=`, `?tag=` | `search` | `SearchPage` | `archive` |
| `/map` | `map` | `MapPage` | `archive` |
| `/issues` and `/issues/<id>` | `issue` (id optional, latest if absent) | `IssuePage` | `archive` |
| `/companies` and `/companies/<id>` | `company` (id optional, first if absent) | `CompanyPage` | `archive` |
| `/papers/<slug>`, library `real: true` | `paper` | `PaperPage` | `archive` + `edition` |
| `/papers/<slug>`, library `real: false` | `sample` | `SamplePage` | `archive` only |
| `/?paper=<slug>` | legacy, rewritten to `/papers/<slug>` | | |

- The sample-versus-paper split is `storyById(archive.library, slug)` plus `story.real` (`src/App.tsx:63-64`, and again in `viewFromInitial` at `:74-75`). A slug not found in the library at all falls through to `loadEdition` and fails there.

### Which routes come from `site.json.papers`

- **None are matched from `site.json`.** `/papers/<slug>` is hard-coded (`src/App.tsx:50`) and accepts any lowercase segment. All other routes are hard-coded.
- **`site.json.papers` is consulted at runtime only inside `loadEdition`** (`src/data/load.ts:98-105`), and by the file source (`src/data/source.ts:23-26`). See section 6.

### How `/papers/<slug>` resolves (fetch or pass-in?)

- **It fetches.** `load(route)` (`src/App.tsx:60-68`) runs `await loadArchive()` (`src/data/load.ts:114-117`: `site.json`, `tags.json`, `search-index.json`, `library.json` plus live overlay, in parallel), then for a real paper `await loadEdition(slug)` (`src/App.tsx:65`, `src/data/load.ts:98-105`). That calls `loadSite()` and `loadVocabulary()` again (both cached by `src/data/fetch-json.ts:14-30`), finds `site.papers.find(p => p.slug === wanted)` (`load.ts:101`), and calls `pickSource().fetchStoryDoc(entry.slug)` (`load.ts:103`).
- **The snapshot path skips the fetch.** `viewFromInitial` (`src/App.tsx:70-81`) takes the edition from `initial` (`editionFromInitial`, `src/data/initial-snapshot.ts:58-62`).
- **Mount behaviour** (`src/App.tsx:150-179`):
  - With `initial` and `source === 'supabase'`: after hydration, re-run `load(currentRoute())` and swap the view only if the JSON differs (`:153-165`). Errors show a live-error banner (`:163`).
  - Without `initial`: the same `load(currentRoute())` runs on mount (`:166-179`).
- **In-app navigation** (`runRoute`, `src/App.tsx:111-143`) calls `load(currentRoute())` as well.
- **Masthead site config** (`src/App.tsx:192-194`): `loadSite()` when no snapshot. This reads `site.json` for name, motto and nav, not for papers.

### Snapshot collection (for prerender)

- `src/App.tsx:198-205`: when `window.__gt_prerender__` is set, the view's `archive` and (for paper pages) `edition.doc` are passed to `window.__collect_initial_data__` through `makeInitialData` (`src/data/initial-snapshot.ts:43-52`).
- `src/main.tsx:12` skips hydration during prerender (`window.__gt_prerender__ ? null : readInitialData()`). The prerender always renders a fresh tree.

---

## 2. `scripts/prerender-routes.ts`

### Exports and return value

- `prerenderRoutes(): PrerenderRoute[]` (`:61-100`) is **synchronous** and returns `{ route: string, kind: RouteKind }[]`. `RouteKind` is `'home' | 'paper' | 'sample' | 'issue' | 'issues' | 'company' | 'companies' | 'map'` (`:25`).
- `htmlPathFor(route)` (`:103-106`) gives `dist/<route>/index.html`, or `dist/index.html` for `/`.
- `DIST` (`:15`), `GENERIC_TITLE` (`:23`: `${site.name} — ${site.motto}`, used by `check-prerender.ts`), `DEFERRED` (`:38-51`), and `site` (`:19`, exported but only used inside this file).

### Routes enumerated (in order, `:63-95`)

1. `/` (`home`), always (`:63`).
2. `/papers/<slug>` (`paper`) for each `site.papers` entry (`:66-69`). `segment()` (`:55-58`) rejects non-lowercase ids.
3. Consistency check (`:64`, `:71-73`): every `library.stories` entry with `real: true` must appear in `site.papers`, or the function throws.
4. `/papers/<id>` (`sample`) for each `library.stories` entry with `real` false. Skipped when `VITE_HIDE_SAMPLES=1` and `story.sample` (`:76-80`).
5. `/issues/<id>` (`issue`) for each `library.issues` entry, skipping `sample` when hidden (`:82-85`).
6. `/issues` (`issues`), only if there is at least one issue (`:87`).
7. `/companies/<id>` (`company`) for each `library.companies` entry, skipping `sample` when hidden (`:89-92`).
8. `/companies` (`companies`), only if there is at least one company (`:93`).
9. `/map` (`map`) (`:95`).

Duplicates are removed by route (`:97-99`).

- **Count today: 27.** That is 1 + 3 + 11 + 5 + 1 + 4 + 1 + 1, matching `dist/` (27 `index.html` files) and the AGENTS.md "27 routes" claim.
- **Count with `VITE_HIDE_SAMPLES=1`: 10** (derived from the data, not run): 1 home, 3 papers, 3 issues (`002`, `001`, `/issues`), 2 companies (`uber`, `/companies`), `/map`.
- **Not enumerated** (`DEFERRED`, `:38-51`): `/?feed`, `/?search` (both share `/`), and `/?paper=<slug>` (legacy, rewritten by the browser).

### Data sources

- Two direct `readFileSync` + `JSON.parse` calls (`:17`, `:19-20`), at **module load**:
  - `public/data/site.json` (`site.papers` only, here).
  - `public/data/library.json` (`stories`, `issues`, `companies`).
- Not read here: `tags.json`, `papers/<slug>.json`, `search-index.json`, `public/data/*` beyond these two.
- `process.env.VITE_HIDE_SAMPLES` (`:62`) is read directly. The `.env` file is not loaded by Node (see section 7).

### Per-route metadata attached

- **None.** Each entry is only `{ route, kind }`. There is no title, description or snapshot input in this file.
- `kind` is used only by `check-prerender.ts` (`:79-84`) for shape checks, and by nobody else.
- The page title, description and Open Graph tags come from each page's `useHead` call at runtime:
  - `src/pages/PaperPage.tsx:20-21`: `` `${doc.pageTitle} — ${site.name}` ``.
  - `src/pages/SamplePage.tsx:15-16`: `` `${headlineOf(story)} — ${site.name}` `` or `site.name`.
  - `src/pages/HomePage.tsx:332-333`: `` `${site.name} — ${site.motto}` ``.
  - `src/pages/IssuePage.tsx:46`: `head?.title ?? archive.site.name`.
  - `src/pages/CompanyPage.tsx:10` and `src/pages/MapPage.tsx:14`: `useHead` calls (not read in detail).
- `useHead` (`src/components/head.ts:30-41`) writes these into `document`, and `prerender.ts` captures the DOM after that.

---

## 3. `scripts/prerender.ts`

### Driving puppeteer

- Entry `main()` (`:140-183`). It first requires `dist/index.html` (`:141`), then calls `prerenderRoutes()` (`:142`) and prints the `DEFERRED` list (`:144`).
- `freePort()` (`:31-40`) and `startPreview(port)` (`:48-77`) spawn `node node_modules/vite/bin/vite.js preview --port N --strictPort` and wait for a `Local: http…` line (`:66`). `stopPreview` (`:79-89`) cleans up.
- `puppeteer.launch({ headless: true })` (`:156`). The full `puppeteer` package is a devDependency (package.json), so it downloads Chromium.
- Routes are rendered **serially** (`:157-172`), one new page per route (`renderRoute`, `:108-138`).
- Output: `htmlPathFor(route)` (`:162`), written with `mkdir` and `writeFile` (`:163-164`). `SITE_ORIGIN`, if set, replaces the local origin (`:161`). A failure is recorded and sets `process.exitCode = 1` (`:169-182`).

### Per-route snapshot (`__initial_data__`)

- `renderRoute` (`:108-138`):
  1. `evaluateOnNewDocument` (`:114-120`) sets `window.__gt_prerender__ = true` and installs `window.__collect_initial_data__`. That function stores `JSON.stringify(data)` in `window.__initial_data_json__` and `data.route` in `window.__initial_route__`.
  2. `goto(route, { waitUntil: 'networkidle0', timeout: 30s })` (`:121`).
  3. `waitForFunction(READY_CHECK, 30s)` (`:122`).
  4. `evaluate(SNAPSHOT)` (`:123`).
  5. Throws on: the app's load-error element (`:124`), an uncaught page error (`:125`), missing `initialData` (`:126`), or a `route` mismatch (`:127`).
  6. Escapes `<`, U+2028 and U+2029 in the JSON (`:128`), refuses `</script` or `<!--` (`:129`).
  7. Inserts `<script id="__initial_data__" type="application/json">…</script>` before the last `</body>` (`:130-134`) and prefixes `<!doctype html>` (`:134`).
- `SNAPSHOT` (`:95-105`) clones `documentElement`, removes any existing `#__initial_data__`, and returns `{ error }` if `.load-error` is present, else `{ html, initialData, route }`.
- The collector is called from `App.tsx:198-205`, only after `view` is set. So the snapshot is written only once the page has its data.

### The `READY_CHECK` and the loader

- `READY_CHECK` (`:93-94`) is true when: `document.title` is non-empty, `<main>` exists, no `main[aria-busy="true"]`, no `.book-loader` element, and `meta[name=description]` and `meta[property="og:type"]` both exist.
- It does **not** check `og:title` or `og:description`; `check-prerender.ts` does.
- The `.book-loader` class belongs to `src/components/BookLoader.tsx`. The check depends on that class name.

### How the route list is consumed

- Line `:142` calls `prerenderRoutes().map(r => r.route)`. Only `route` is used; `kind` is ignored here.
- Also `DEFERRED` (`:144`) and `htmlPathFor` (`:162`).

### Supabase

- **`scripts/prerender.ts` has no Supabase client.** It imports only `puppeteer`, Node built-ins, and `prerender-routes.ts`.
- **`scripts/prerender-routes.ts` has no Supabase client either.** It reads two JSON files.
- The Supabase reads happen in the browser, inside the app being prerendered. The bundle picks up `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY` at build time, and `.env` sets `VITE_DATA_SOURCE=supabase` (value confirmed, not printed).
- Consequence: a paper's snapshot is a live Supabase read, made during prerender, by the same code path as runtime. There is no separate snapshot fetch in Node.

---

## 4. `scripts/build-index.ts`

**Not dead code.** It is the only writer of `public/data/search-index.json`, and every page loads that file through `loadArchive`.

- **Reads:**
  - `data/site.json` (`:214`): `defaultPaper` (`:219`) and `papers` (`:221-222`).
  - Each `papers[].dataUrl` (`:222`), checking `schemaVersion` (`:223`) and that `doc.slug` matches the entry (`:224`).
  - `data/tags.json` (`:215`).
  - `data/library.json` (`:216`): cross-checks `real` stories against `site.papers` (`:252-256`), plus every reference (front page, issues, companies, nodes, relations, storylines) (`:260-272`).
- **Emits:** `public/data/search-index.json` (`:219` builds it with `featured: site.defaultPaper`, `:280` writes it). It is gitignored (`.gitignore:11`).
- **Errors:** collected (`:14`, `:274-279`); if any exist, nothing is written and the process exits 1.
- **Runs:** `npm run data`, via `predev` and `prebuild` (package.json).
- **Consumed by:**
  - `src/data/load.ts:88` (`loadSearchIndex`) and `:115` (`loadArchive`), which every page uses.
  - `src/pages/HomePage.tsx:141-146`, `:240`.
  - `src/pages/SearchPage.tsx:37` (count) and its search.
  - `src/lib/feed.ts:6` (`index.featured` orders the feed).
  - `src/lib/tags.ts:67`, `:102`.
- **After the cutover:** the `site.papers` loop (`:221-245`) and `featured` (`:219`) need a new source. The header (`:5-6`) says the database will enforce the same rules later, so the checks remain the import-time validator for AI-generated content.

---

## 5. `scripts/check-prerender.ts` and `scripts/check-hydration.ts`

### `check-prerender.ts`

- Reads only `dist/` files. Calls `prerenderRoutes()` synchronously (`:119`) and iterates the result (`:120`).
- Per route (`checkRoute`, `:56-111`):
  - `dist/<route>/index.html` exists (`:58-62`).
  - `<!doctype html>` present (`:65`).
  - Exactly one `__initial_data__` script (`:66-67`), unescaped `<` absent (`:71`), valid JSON (`:72-73`).
  - `schemaVersion === 1` (`:75`), `data.route === route` (`:76`), `source` is `file` or `supabase` and `hideSamples` is a boolean (`:77`).
  - `archive` has `site`, `vocab`, `index`, `library` (`:78`).
  - For `kind === 'paper'`: `edition.doc.slug` equals the route slug (`:80-81`), and the title equals `${edition.doc.pageTitle} — ${archive.site.name}` (`:83`). For other kinds: no `edition` (`:84`).
  - No `localhost` or `127.0.0.1` origin in output (`:85`). No `.load-error` (`:88`). A `<main>` exists (`:89`).
  - Title non-empty (`:93`) and not `GENERIC_TITLE` unless `kind === 'home'` (`:94`).
  - `meta[name=description]`, `og:title`, `og:description`, `og:type` non-empty (`:96-102`). `og:image` must not be `.svg` (`:104-105`).
- Warnings (not failures): placeholder text `[…]` (`:107-109`) and duplicate titles across routes (`:128-133`).
- Prints `DEFERRED` (`:139-140`).
- **Assumptions that break if slugs come from the database:**
  - Slug parsing is `route.slice('/papers/'.length)` (`:80`). Works for any lowercase slug.
  - `prerenderRoutes()` is called synchronously at `:119`. It must become awaited.
  - `GENERIC_TITLE` (`prerender-routes.ts:23`) is built from `site.name` and `site.motto`. Those values must stay available.
  - If the enumerator queries Supabase, this check also needs Supabase at check time. A written manifest avoids that (section 7).

### `check-hydration.ts`

- Imports `prerenderRoutes` (`:10`) and loops over it synchronously (`:40`). Needs `await` after the change.
- Fixed `PORT = 4179` (`:13`). Spawns `vite preview` with `stdio: 'ignore'` (`:33`), polls `/` for 20 s (`:17-29`).
- For each route (`:40-56`): a new page, console `warn`/`error` and `pageerror` messages matching `/hydrat/i` are counted (`:43-50`), `goto` with trailing-slash URL (`:52`), `networkidle0`, then a 1 s wait (`:53`).
- Does not read `__initial_data__`. It only watches for hydration noise.
- Under `source === 'supabase'`, the browser makes a live read after hydration (`src/App.tsx:153-165`). Its effect on this check was not examined.
- **Assumption that breaks:** the route list is read once, synchronously, at `:40`. Same fix as above.

---

## 6. `site.json` consumers

Grep: `site\.json|site\.papers|\.papers\b|papers\?\.|defaultPaper|SiteConfig|loadSite|loadEdition|dataUrl` across the repo, excluding `node_modules` and `dist`.

**Code (the cutover must touch these):**

| File:line | Uses | Survives the cutover? |
|---|---|---|
| `src/data/load.ts:12` | `loadSite` definition (`getJson('data/site.json')`) | Only if site settings stay in a file |
| `src/data/load.ts:98-105` | `loadEdition`: `defaultPaper` (`:100`), `papers.find` and throw `No paper called` (`:101-102`), `fetchStoryDoc(entry.slug)` (`:103`) | **Blocker.** Runs in Supabase mode too (`src/App.tsx:65`). A slug missing from `site.json` fails even when live in the DB. |
| `src/data/load.ts:8-10` | `mediaBaseFor` reads `site.mediaBaseUrl` | Keep the setting, move the file |
| `src/data/load.ts:115` | `loadArchive` loads `site.json` for `archive.site` | Keep the setting, move the file |
| `src/data/source.ts:23-26` | file source: finds `site.papers` entry, reads its `dataUrl` | File source only; the cutover can drop it or derive `papers/<slug>.json` |
| `src/data/source-supabase.ts` | none | Good: no `site.json` dependency |
| `src/App.tsx:193` | `loadSite()` for Masthead (site name, nav, motto) | Keep the setting, move the file |
| `src/App.tsx:98`, `:132`, `:158`, `:171` | `archive.site` into React state | Follows `archive.site` |
| `src/types.ts:16-33` | `SiteConfig` (`defaultPaper`, `papers`, `mediaBaseUrl`, `name`, `motto`, `tagline`, `navLabel`), `PaperEntry` | Split the type: site settings without `papers` |
| `src/lib/feed.ts:6` | `index.featured` (from `defaultPaper` via `build-index.ts:219`) | Source of `featured` must move |
| `src/components/Masthead.tsx:4`, `:9` | type only | Follows `SiteConfig` |
| `src/vite-env.d.ts:4` | comment only | Update comment |
| `scripts/build-index.ts:214`, `:219`, `:221-224`, `:254` | read `site.json`, `defaultPaper`, `papers` loop, error text | `:221-245` must be replaced; `:219` needs a new source |
| `scripts/prerender-routes.ts:19`, `:23`, `:66-69`, `:70-73` | read `site.json`, `GENERIC_TITLE`, paper enumeration, real-vs-site check | Replace `:66-73`; `:19`, `:23` need a site settings file |

**Not `site.json`, but easily confused (the name `papers` is overloaded):**
- `archive.index.papers` (the search index) is a different list. Hits: `src/pages/HomePage.tsx:141`, `:142`, `:146`, `:240`; `src/pages/SearchPage.tsx:37`; `src/lib/feed.ts:6`; `src/lib/tags.ts:67`, `:102`; `scripts/build-index.ts:219-244`.
- `src/lib/source.ts` (view helper, `sourceOf`) and `src/data/source.ts` (data source picker) are different files. `src/lib/source.ts` is imported by `src/components/common.tsx` and `src/pages/PaperPage.tsx`, not by `src/data/source.ts`.

**Docs and skills (they describe `site.json.papers` as the way to add a story, so they will go stale):**
- `AGENTS.md:65`, `:90`.
- `README.md:47`, `:63`, `:101`, `:102`, `:113`.
- `skills/convert-paper/SKILL.md:73`, `:145`.
- `skills/publish-issue/SKILL.md:31`.
- `skills/explain-source/SKILL.md:74`.
- `docs/STATE.md:46`, `docs/data-model.md:22`, `docs/production-plan.md:159`, `:224`.
- `docs/handoffs/phase-3b-closeout.md:97`, `docs/handoffs/v1-schema-contract.md:122`.

**Not a consumer:** `scripts/publish-to-supabase.ts` and `scripts/seed-editorial-from-library.ts` do not read `site.json`.

---

## 7. Risks for the cutover

### What breaks if `site.json.papers` disappears

1. **Every paper page fails in Supabase mode.** `loadEdition` (`src/data/load.ts:101-102`) throws `No paper called “<slug>”` when the slug is not in `site.papers`. A live Supabase story would still be blocked. This is the biggest surprise: site.json is a **runtime gate in Supabase mode**, not only a build-time list.
2. **The archive fails for every page, home included.** `loadArchive` (`load.ts:115`) fetches `search-index.json`, which only `build-index.ts` writes, and only from `site.papers` (`:221-224`). The build validator (`npm run data`) also gates `dev` and `build` (`predev`, `prebuild`).
3. **Site settings go with it.** `name`, `motto`, `navLabel`, `mediaBaseUrl`, `defaultPaper` (`src/types.ts:16-25`) feed the Masthead (`App.tsx:193`), `GENERIC_TITLE` (`prerender-routes.ts:23`), `mediaBaseFor` (`load.ts:8-10`) and `featured` (`build-index.ts:219`). Only `papers` should go. The rest needs a new home.
4. **The real-versus-sample coupling** (`App.tsx:64`, `prerender-routes.ts:64-73`, `build-index.ts:252-256`, `initial-snapshot.ts:91-92`) is decided by `library.json` `real`. `prerenderRoutes` throws if a real library story is missing from `site.papers` (`prerender-routes.ts:71-73`). That throw is replaced by the DB enumeration, but the `real` flag still has to come from somewhere.

### What needs to become async at build time

- `prerenderRoutes()` (`prerender-routes.ts:61`) is **sync** today and is called from three places: `prerender.ts:142`, `check-prerender.ts:119`, `check-hydration.ts:40`. All three must `await` it, and `check-hydration.ts:40` is a `for…of` loop.
- Top-level reads in `prerender-routes.ts:19-20` and `build-index.ts:214-216` run at import time. They become `await` inside an async function. The `.ts` files are ESM (`"type": "module"`), so top-level await works if the enumerator is written at top level.
- `GENERIC_TITLE` (`prerender-routes.ts:23`) is a top-level constant derived from `site`. It needs site settings loaded first.

### Does the prerender script have a Supabase client?

- **No.** Neither `scripts/prerender.ts` nor `scripts/prerender-routes.ts` creates one, and neither imports anything Supabase. The only Supabase-related scripts are the separate CLIs `publish-to-supabase.ts` (service-role, per `.env.example`; not read in detail) and `apply-migration.ts`.
- `@supabase/supabase-js` is a runtime dependency (package.json), used only by `src/data/source-supabase.ts`. It is plain ESM and can be imported in Node, but this has not been tested here.

### Environment

- `npm run prerender`, `check:prerender`, `check:hydration` and `data` run `node --experimental-strip-types` **without `--env-file=.env`** (package.json). Only `publish:supabase`, `apply:migration` and `seed:editorial` pass it. Node does not read `.env`. An enumerator therefore needs `--env-file=.env` added to these scripts, or the values must come from the shell.
- The read path should use the publishable key against the public views (`v_live_story`, decision 48/49). The views are `security_invoker = true` (`supabase/migrations/20261106100002_public_views_rls.sql:30`, `:57`), and the service-role key is not needed. Verify RLS grants before relying on it.

### Sample routes stay file-driven

- Supabase views exclude samples (`v_live_story` has `where ... s.sample = false`, `public_views_rls.sql:54`). So sample routes (`prerender-routes.ts:76-80`) must keep reading `library.json` unless the enumerator asks the DB for samples, which it does not do today.
- `VITE_HIDE_SAMPLES` still affects the file-based samples, issues and companies. For papers in Supabase mode, sample papers never reach the list.

### Consistency between enumeration and render

- The enumerator and the browser both read live rows. A story live at enumeration but unpublished before the render will make `renderRoute` fail, because the app shows the load-error element (`App.tsx:163` and `:234-238`) and `SNAPSHOT` returns `{ error }` (`prerender.ts:100`). That is a route-level failure (`prerender.ts:169-170`) with `process.exitCode = 1`. Acceptable, but worth a note.
- Slugs from the DB must match `SAFE_SEGMENT` (`prerender-routes.ts:53`, `^[a-z0-9][a-z0-9-]*$`), or `segment()` throws (`:55-58`).

### Other things seen

- `dist/papers/` holds directories that no current data produces (`alphafold`, `blog-artwork`, `blog-ride`, `blog-social`, `blog-streaming`, `blog-video`, `crispr`, `higgs`, `ligo`, `penicillin`, `resnet`), left over from an earlier build. `dist/` is gitignored (`.gitignore:2`). Vite empties `outDir` by default, so the next `npm run build` should clear them. Not verified by running.
- `vercel.json:4` rewrites every path except `assets/`, `data/`, `media/` and two files to `/index.html`. Prerendered files are expected to be served before the rewrite, but the prerender header says Vercel does not run `prerender` yet (`scripts/prerender.ts:18-19`). Not verified.
- `/?paper=` is handled entirely in `currentRoute()` (`App.tsx:43-47`) and needs no change.

---

## 8. Dead-code candidates (verify before deleting)

- `src/data/initial-snapshot.ts:54-56`: `setPrerenderCollector`. No callers. `App.tsx:204` calls `window.__collect_initial_data__` directly.
- `src/lib/navigation.ts:48-52`: `takePendingNavigation`. No callers. `pendingNavigation` (`:2`, set at `:10`, `:33`, `:44`) is only read by this function.
- `src/App.tsx:20`: `export { navigate } from './lib/navigation'`. No file imports `navigate` from `App`. The function itself is live (`navigation.ts:35` calls it), so only the re-export is dead.
- `scripts/prerender-routes.ts:19`: `export const site`. Exported but used only inside the file (`:23`). Harmless.

**Not dead:** `scripts/build-index.ts` (section 4), `src/edition.ts` (imported by `src/blocks/LeadBlock.tsx` and `src/pages/PaperPage.tsx`), `src/lib/source.ts` (used by `src/data/source.ts`, `src/components/common.tsx`, `src/pages/PaperPage.tsx`), `loadSearchIndex`, `SNAPSHOT_SCHEMA_VERSION`.

---

## 9. Not verified

- No `npm`, build, prerender or check was run (per the brief).
- RLS and grants for `v_live_story` with the publishable key were not checked against the live database.
- `CompanyPage.tsx` and `MapPage.tsx` `useHead` values were not read in detail.
- Whether `vite build` empties `dist/` on this Vite version was not confirmed by running it.
- Whether Vercel serves prerendered static files ahead of the `vercel.json` rewrite was not checked.
