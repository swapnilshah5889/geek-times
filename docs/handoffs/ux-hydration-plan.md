# UX hydration plan (Wave 1, Agent B)

Analysis only. No source, script, or data file was changed, and no build, typecheck or lint was run. Governing decision: 50 (`docs/decisions.md`). Interface contract: `docs/handoffs/ux-route-state-interface.md`. Facts were checked by reading the files named below and by inspecting the existing `dist/` output (built 2026-11-06 10:30, not rebuilt).

Route count check: 27 routes = home 1, real papers 3, sample stories 11, `/issues` plus 5 issues = 6, `/companies` plus 4 companies = 5, `/map` 1. This matches `scripts/prerender-routes.ts:61`.

---

## 1. Trace: prerender → initial React mount → runtime read → final paper page

**Prerender (build time).** `npm run prerender` runs `main()` in `scripts/prerender.ts`. It starts `vite preview` (`startPreview`) and launches Puppeteer. For each route from `prerenderRoutes()`, `renderRoute()` (`prerender.ts:101`) opens the route without a trailing slash, so vite preview returns the SPA shell (whatever `dist/index.html` is at that moment). It waits for `networkidle0` and `READY_CHECK` (`prerender.ts:93`), then runs `SNAPSHOT` (`prerender.ts:95-98`), which returns `document.documentElement.outerHTML`. In the browser, `src/main.tsx:7` calls `createRoot(...).render(...)`. `App` (`src/App.tsx:65`) starts with `view === null`, so it shows the loading shell (`App.tsx:85-90`). Its effect (`App.tsx:70-75`) calls `load(currentRoute())`, which awaits `loadArchive()` (`src/data/load.ts:114`) and then `loadEdition()` (`load.ts:98`). The page is rendered, and each `MediaView` (`src/components/MediaView.tsx:44`) fetches its SVG into an open shadow root. The captured DOM has these properties. The `<html>` element has no doctype, so the file starts `<html lang="en"><head>`. The head contains the module script, the stylesheet link, and the `useHead` title and meta tags. The `<main>` holds the full React markup. Every SVG figure is `<div class="media media-svg" style="--ar: …"><div></div></div>` (or `<div class="paused">` inside a figure), because `outerHTML` does not serialize open shadow roots. The masthead date is the build-day text (`dist/index.html` reads "Friday, November 6, 2026"). Reduced-motion buttons read "Pause animations". No snapshot data is present. The HTML is written to `dist/<route>/index.html` (`prerender.ts:137-141`).

**Browser loads the prerendered HTML.** The parser builds the DOM from the prerendered markup. The stylesheet is render-blocking, so the reader sees the full page at first paint: headline, text, masthead, and the blocks. SVG frames are empty boxes, but `--ar` (`MediaView.tsx:82`) reserves their height. The module script is deferred. No webfonts are loaded (no Google Fonts import in `src/styles`), so there is no font swap. Nothing is interactive yet.

**React mounts (`src/main.tsx:7`).** `createRoot` discards the prerendered children of `#root` and does not reuse them. The first committed tree is `App`'s first render, when `view`, `error` and `site` are all null. That renders `<main class="site-main" aria-busy="true">` with no Masthead (`App.tsx:87` needs `site`) and `<p class="loading">Setting the type…</p>` (`App.tsx:85-90`). This is the visible collapse of the page.

**Effects and data (file mode).** The effect at `App.tsx:70-75` runs `currentRoute()` (`App.tsx:36-53`, which may call `history.replaceState` for legacy `?paper=`) and then `load()` (`App.tsx:55-63`). `loadArchive()` (`load.ts:114`) issues four requests in parallel: `site.json`, `tags.json`, `search-index.json` (47.9 KB raw) and `library.json`, with the live-entry map empty in file mode (`source.ts:28-30`). For a paper, `loadEdition()` (`load.ts:98`) then waits for a second, serial request for `papers/<slug>.json`. A separate effect (`App.tsx:79-81`) loads `site.json`, so the Masthead appears first. `setView` (`App.tsx:71`) triggers the `switch` at `App.tsx:91-100`, which renders `PaperPage`.

**Paper page mounts (`src/pages/PaperPage.tsx:13`).** `BlockView` (`src/blocks/index.tsx:20`) renders the lead, story, comic and facts blocks. `LeadBlock`'s slideshow starts at index 0, and its timer effect (`LeadBlock.tsx:18-22`) starts a 5.5 s auto-advance. Each `MediaView` calls `useInView` (`src/lib/motion.ts:29-39`), which starts `false`, so art is paused until an IntersectionObserver fires. Each `InlineSvg` effect (`MediaView.tsx:46-61`) fetches its SVG (`fetchSvg`, `MediaView.tsx:17-27`, cached per URL), sanitizes it (`safeSvg`, `MediaView.tsx:30-42`), and appends it to the shadow root. Until each fetch resolves, the box stays empty. `useHead` (`PaperPage.tsx:20-24`, `src/components/head.ts:30-41`) sets the title and meta, which match the prerendered values. The hash effect (`PaperPage.tsx:26-28`) scrolls to `#hash` after React has replaced the DOM.

**Runtime read after mount.** In file mode there is no read beyond the static fetches above. In Supabase mode (`VITE_DATA_SOURCE=supabase`) the same effect awaits `pickSource().fetchLiveLibraryEntries()` (`load.ts:82-86`, `source-supabase.ts:85-88`) and then `fetchStoryDoc(slug)` (`load.ts:103`) before any view exists. The loading shell therefore lasts for the Supabase round trips.

**Final paper page.** React owns `#root > main`. The Masthead, blocks, family tree and tag shelf are rendered. The SVG shadow roots are filled, the title and meta are set, and the hash is scrolled to. The result looks like the prerendered page with art added, but only after the collapse and the art fetches.

---

## 2. The flash: root causes

### 2a. Visible interruptions (the flash)

| # | File and line | Cause | Fix |
|---|---|---|---|
| F1 | `src/main.tsx:7` | `createRoot().render()` discards the prerendered DOM. | `hydrateRoot` when the section 6 rules pass. Decision 50. |
| F2 | `src/App.tsx:66`, `:85-90` | `view` starts `null`, so the first paint is the loading shell with `aria-busy`. | Initialize `view` synchronously from the snapshot. Hydrated routes never show the loading shell. |
| F3 | `src/App.tsx:70-75`, `src/data/load.ts:114-117`, `:98-105` | Serial waterfall: `loadArchive` (four requests, including the 47.9 KB index), then `loadEdition` (second round trip). | The snapshot carries archive and edition, so file mode makes no request at mount. |
| F4 | `src/App.tsx:79-81`, `:87` | The Masthead waits for `site.json`, so the header disappears in the shell and reappears later. | Snapshot. |
| F5 | `src/components/MediaView.tsx:44-63` with `scripts/prerender.ts:95-98` | Art is missing from the HTML (`outerHTML` skips shadow roots; `dist/papers/attention-is-all-you-need/index.html` has `<div class="media media-svg" …><div></div></div>` per figure) and is fetched after mount. Attention has 31 SVG media entries, so 31 blank frames fill in one by one. This is the largest visible flash left after F1 to F4. | Spike: serialize each open shadow root into a declarative `<template shadowrootmode="open">` inside its host during prerender, and make `InlineSvg`'s first render accept it. Unverified with React 19.3 (see section 11). Fallback: blank frames remain. Embedding SVG text in the snapshot is rejected: the attention media folder alone is 212 KB on disk. |
| F6 | `src/lib/motion.ts:29-39` | `useInView` starts `false`, so art is paused on first paint and starts after the IntersectionObserver fires. | None needed for hydration. With F5 the paused state is in the HTML. It is visible only as animation starting a moment after load. |
| F7 | `src/components/SitePage.tsx:16` | `window.scrollTo(0, 0)` runs on mount, so it resets the browser's scroll restoration on reload and any `#hash` on issue, company, map and sample pages. | Skip on the hydration mount. Scroll resets belong to `navigate()` (Agent C). |
| F8 | `src/pages/PaperPage.tsx:26-28` | The hash scroll runs after React has replaced the DOM. Under `hydrateRoot` the target exists at mount, so this is fine. The dependency list `[site, doc]` (line 28) re-runs the effect when the runtime read replaces `doc`, which would scroll the reader back to the hash. | Keep the effect for the hash only, or keep `doc` identity when content is unchanged (section 8). |
| F9 | `src/lib/format.ts:3`, used at `src/pages/HomePage.tsx:342`, `src/components/SitePage.tsx:21`, `src/App.tsx:87` | The prerender writes the build-day date. The browser computes the reader's date, which differs after the build day or across time zones. React 19 treats a text mismatch as a recoverable error and re-renders the root from scratch. That recreates every SVG and refetches art, and drops scroll and focus. | Compute the date in an effect, so the prerendered masthead shows no date. `suppressHydrationWarning` is not enough, because React keeps the server text and does not patch it. |
| F10 | `src/lib/motion.ts:6,8-9`, `src/components/motion.tsx:5-12` | `useReducedMotion` reads `matchMedia` during render. The prerender shows "Pause animations". A reduced-motion reader's first hydration render shows "Play animations". That is a text mismatch and triggers the same full re-render as F9. | `useSyncExternalStore` with a server snapshot of `false`. React then updates to the client value. Move `window.matchMedia` out of module scope. |
| F11 | `src/App.tsx:83-84` | Any error replaces the whole page with `load-error`. On a hydrated route a failed live read would blank the snapshot. | Section 9: keep the snapshot and show a banner. |
| F12 | `scripts/prerender.ts:137-141` | The prerendered HTML has no `<!doctype html>` (checked: the file begins `<html lang="en">`). Browsers render it in quirks mode, and the SPA keeps that mode. Layout can differ from the standards-mode CSS the design was tested against. | Prepend `<!doctype html>` when writing. Add a check (section 5). |

### 2b. Cosmetic (not the flash)

| # | File and line | Note |
|---|---|---|
| C1 | `src/styles/edition.css:14-18` | `.loading` has 80 px padding and fades in after 0.25 s. It only exists in the loading shell. It disappears under hydration. Delete or keep, but it is not the flash. |
| C2 | `src/blocks/LeadBlock.tsx:18-22` | Slideshow auto-advance starts at mount. It does not check in-view state, which AGENTS.md requires ("animations pause off-screen"). This is an accessibility item, separate from hydration. |
| C3 | `src/components/MediaView.tsx:90-93` | For `image` media, the poster is swapped for the GIF after the first in-view change. No image media exists in current data. |
| C4 | `src/components/head.ts:30-41` | Title and meta are re-set in an effect with identical strings, so nothing visible changes. |

---

## 3. Snapshot shape

The snapshot is `window`-free JSON, serialized by the prerender and parsed by `src/main.tsx`. Name its version `SNAPSHOT_SCHEMA_VERSION = 1`, separate from `STORY_SCHEMA_VERSION = 2` (`src/types.ts:8`), so the two numbers cannot be confused.

```ts
interface InitialData {
  schemaVersion: 1;                    // SNAPSHOT_SCHEMA_VERSION
  route: string;                       // app path, no base, no query, no trailing slash: "/", "/papers/<slug>", "/issues", "/issues/<id>", "/companies", "/companies/<id>", "/map"
  source: 'file' | 'supabase';         // VITE_DATA_SOURCE at build time ('file' when unset)
  hideSamples: boolean;                // VITE_HIDE_SAMPLES === '1' at build time
  archive: Archive;                    // site, vocab, index, library: what loadArchive() returns (library after overlayLive and hideSamples)
  edition?: { doc: PaperDoc };         // paper routes only
}
```

**Snapshot contents are the first view only.** The snapshot is the data used to render the prerendered HTML. Later runtime refreshes never change it.

**Omitted per route kind.** Route counts are in brackets.

| Kind (count) | `archive.site` | `archive.vocab` | `archive.index` | `archive.library` | `edition` |
|---|---|---|---|---|---|
| home `/` (1) | yes | yes | yes | yes | absent |
| paper `/papers/<real>` (3) | yes | yes | yes (phase 1) | yes | `{ doc }` only |
| sample `/papers/<sample>` (11) | yes | yes | yes (phase 1) | yes | absent |
| issues `/issues`, `/issues/<id>` (6) | yes | yes | yes | yes | absent |
| companies `/companies`, `/companies/<id>` (5) | yes | yes | yes | yes | absent |
| map `/map` (1) | yes | yes | yes (phase 1) | yes | absent |

Omissions that apply to every kind:
- `edition.mediaBaseUrl` is never embedded. `mediaBaseFor` (`load.ts:8-10`) resolves against `window.location.origin`, so at build time it holds the local preview origin. The client recomputes it.
- `edition.site` and `edition.vocab` are never embedded. They duplicate `archive.site` and `archive.vocab`, and the client rebuilds `Edition` from the archive. On a paper page this avoids about 18 KB of duplicated tags.

Phase 2 candidates (not in this batch, because `Archive` is typed with required fields):
- `archive.index` can be dropped on paper, sample and map routes. Verified: `realPaper` (`src/lib/library.ts:43-44`) reads the index only when `story.real`; `PaperPage`, `SamplePage` and `MapPage` do not read `archive.index` directly. This would need `index?` in the type.
- `archive.vocab` is read by `SearchPage` and by `TagShelf` through `edition.vocab`. It can be dropped on non-paper kinds after the same check.

Never embedded: SVG text, media bytes, Supabase rows as received, fetch or source caches, and anything derived from `window`.

**Size (measured on the current data, raw / gzip -9).** `site.json` 0.76 KB / 0.38 KB. `tags.json` 18.4 / 3.4 KB. `search-index.json` 47.9 / 8.5 KB. `library.json` 21.7 / 4.7 KB. `papers/attention-is-all-you-need.json` 31.4 / 5.6 KB. A paper snapshot is about 120 KB raw (about 22 KB gzip). A home or other archive-only snapshot is about 90 KB raw. Acceptable for this batch. Measure page weight after the change.

**Supabase mode.** The shape is the same. `archive.library` is the overlaid library, and `edition.doc` is the live document. `source: 'supabase'` tells the client that a runtime read is needed (section 8).

---

## 4. Prerender write path

The changes below are all in `scripts/prerender.ts`, plus the matching `window` declaration in `src/types.ts` and a collector call in `src/App.tsx`.

**4.1 SPA signal.** `App`'s `load()` calls `window.__collect_initial_data__?.(initialDataFrom(route, view))` once, after the first view is built and before `setView`. A hydrated page calls it once from its mount effect. It is never called for a refresh. The call is optional, so it is a no-op in normal browsing. The global is typed in `src/types.ts` as an optional `Window` property.

**4.2 Prerender side.** `renderRoute` calls `page.evaluateOnNewDocument` before navigation. That installs `window.__collect_initial_data__ = d => { window.__initial_data_json__ = JSON.stringify(d); }`, so the setter exists before any page script runs. `JSON.stringify` runs in the page, and Node receives a string. After `READY_CHECK`, a route fails with `page did not report its initial data` if `__initial_data_json__` is missing. It also fails if the reported `route` differs from the route being rendered.

**4.3 Strip leftovers.** `SNAPSHOT` (`prerender.ts:95-98`) clones `documentElement`, removes `#__initial_data__` from the clone, and then serializes. The paper and sample routes are loaded from the shell, which is the home page's prerendered HTML once `/` has been written. Without this step, every such page would contain two elements with that id, and `getElementById` would return the home page's snapshot.

**4.4 Doctype.** Prepend `<!doctype html>\n` before writing (`prerender.ts:141`).

**4.5 Escaping.** Take the page's `JSON.stringify` output and apply three replacements:
- every `<` becomes `<`. This covers `</script`, `</body`, `<!--`, and `<script` in one rule. The narrower `</` → `<\/` leaves `<!--` and `<script` able to switch the HTML tokenizer's script-data state.
- U+2028 becomes the JSON escape ` `, and U+2029 becomes ` `. Do not replace them with a space. A space would silently change the text.

The result is still valid JSON, because `<` only occurs inside JSON strings. The escaped text also cannot match the regexes in `check-prerender.ts`.

**4.6 Placement.** Insert the block immediately before `</body>`, using `lastIndexOf('</body>')`:

```html
<script id="__initial_data__" type="application/json">…escaped JSON…</script>
```

Why before `</body>`:
- It stays outside `#root`. React owns `#root`, and `createRoot` would clear the element; `hydrateRoot` would see it as an unexpected child.
- It keeps the head metadata first for crawlers.
- The module script is deferred, so the element exists when `main.tsx` reads it.

**4.7 Order and assertions.** Inject after the `SITE_ORIGIN` split (`prerender.ts:138`), so the snapshot is not rewritten. Before writing, assert the snapshot body contains no `http://localhost` or `127.0.0.1` string, and that the id appears exactly once in the HTML.

**4.8 Behavior on re-run.** A second `npm run prerender` without a rebuild would load prerendered HTML and take the hydrate path. The collector call in 4.1 runs on that path too, so the rerun still produces a snapshot.

---

## 5. check:prerender additions

Add to `scripts/check-prerender.ts`, for every route in `prerenderRoutes()`. Error text is verbatim. The existing checks stay as they are.

1. `html` contains exactly one `<script id="__initial_data__" type="application/json">`. Error: `missing or duplicate __initial_data__ script`.
2. The script body contains no `</` and no `<!--`. Error: `__initial_data__ body has an unescaped "<"`.
3. The body parses with `JSON.parse`. Error: `__initial_data__ is not valid JSON`.
4. `schemaVersion === 1`. Error: `__initial_data__ schemaVersion is ${v}; expected 1`.
5. `route` equals the route the HTML was written to, using "/" for home and the path otherwise. Error: `__initial_data__ route "${r}" does not match "${route}"`.
6. `source` is `'file'` or `'supabase'`, and `hideSamples` is a boolean. Error: `__initial_data__ source or hideSamples is invalid`.
7. `archive` has non-null `site`, `vocab`, `index` and `library`. Error: `__initial_data__ archive is missing ${key}`.
8. Paper routes: `edition.doc` exists and `edition.doc.slug` equals the route's slug. Error: `__initial_data__ edition.doc is missing or for another slug`.
9. Non-paper routes: `edition` is absent. Error: `__initial_data__ has an edition on a ${kind} route`.
10. Paper routes: `edition` has no `site`, `vocab` or `mediaBaseUrl` key. Error: `__initial_data__ edition duplicates ${key}`.
11. The snapshot body and the HTML contain no match for `/https?:\/\/(localhost|127\.0\.0\.1)/`. Error: `local preview origin leaked into the output`.
12. The file starts with `<!doctype html>` (case-insensitive, after optional whitespace). Error: `missing <!doctype html> (the page would render in quirks mode)`.
13. Paper routes: the `<title>` equals `${doc.pageTitle} — ${site.name}` from the snapshot. Error: `title does not match the snapshot document`. This is a sentinel that the prerendered DOM and the snapshot agree.

Browser-only check, not in `check:prerender` (it needs a browser): after a fresh load of each route, `window.__mount_mode__ === 'hydrated'` with no `onRecoverableError` calls. This can run as a second pass in `prerender.ts`.

---

## 6. Mount path in `src/main.tsx`

Resolve the route with the pure resolver before any history mutation. The `?paper=` `replaceState` in `App.tsx:40` must not run first.

```
el  = document.getElementById('__initial_data__')
snap = el ? parse(el.textContent) : null          // any parse error → null

hydrate only if ALL of:
  a. snap is not null
  b. snap.schemaVersion === SNAPSHOT_SCHEMA_VERSION (1)
  c. snap.source === (VITE_DATA_SOURCE trimmed, default 'file')
  d. snap.hideSamples === (VITE_HIDE_SAMPLES === '1')
  e. snap.route === the resolved route key for location.pathname
  f. the resolved page kind equals the snapshot's kind
  g. location.search carries no query that changes the page:
       "/" with feed, search, q, tag or paper → createRoot
       "/map" with focus → createRoot
  h. #root has exactly one element child, a <main>

if all pass:
  window.__mount_mode__ = 'hydrated'
  hydrateRoot(root, <StrictMode><App initial={snap} /></StrictMode>, { onRecoverableError: report })
else:
  window.__mount_mode__ = 'created'
  createRoot(root).render(<StrictMode><App /></StrictMode>)
```

**Snapshot or URL mismatch.** Use `createRoot`, which is today's path. Log a `console.info` line with the reason. The reader sees no difference. Routes this covers include `/?feed`, `/?search`, `/?q=`, `/?tag=`, `/?paper=`, `/map?focus=` (the links from `FamilyTree.tsx:84` always take this path), and any URL served by the SPA fallback from `dist/index.html`.

**schemaVersion mismatch.** Use `createRoot` and log a `console.warn` naming both versions. This happens when HTML from one build is served with JavaScript from another. Story documents at the wrong `schemaVersion` are not affected here; they fail at prerender, as today.

**Recoverable errors.** `report` logs with `console.error`. A hydration mismatch that React reports is not silent: the root re-renders on the client, and the browser check above catches it.

**App signature.** `App` takes an optional `initial?: InitialData` prop and uses it for the first state. The interface doc says `App(): JSX.Element // unchanged`, so this must be amended (section 11).

---

## 7. 27-route hydration-mismatch audit

Verdict key: **MISMATCH** means a server and client difference that React reports as recoverable, so the whole root re-renders. **CLEAN** means the first render is identical. **LATENT** means no current data triggers it.

| # | Where | Server vs client difference | Routes | Proposed fix | Verdict |
|---|---|---|---|---|---|
| M1 | `src/lib/format.ts:3` in `src/pages/HomePage.tsx:342`, `src/components/SitePage.tsx:21`, `src/App.tsx:87` | Build-day date text vs reader's date (day or time zone). | 13: `/`, `/issues` and 5 issues, `/companies` and 4 companies, `/map` | Effect-based date (blank in prerender). Not `suppressHydrationWarning`. | MISMATCH, almost every visit after the build day |
| M2 | `src/lib/motion.ts:6,8-9` and `src/components/motion.tsx:5-21` (label at `MotionButton`) | `Pause` vs `Play` label for reduced-motion readers. | 15: `/` (`HomePage.tsx:343`), 3 papers (`LeadBlock.tsx:37`, `:56`, `StoryBlock.tsx:13`, `ComicBlock.tsx:34`), 6 issues and 5 companies (`SitePage.tsx:22`) | `useSyncExternalStore` with server snapshot `false`; move `matchMedia` into a function. | MISMATCH for reduced-motion readers only |
| M3 | `src/pages/MapPage.tsx:19,25` | `window.location.search` read in render. `?focus=` picks a different node than the prerender. | `/map?focus=…` only (linked from `FamilyTree.tsx:84`) | Gate by rule 6g (section 6). Later: pass focus as a prop. | MISMATCH on that URL only, gated |
| M4 | `src/components/MediaView.tsx:44-63` | Both sides render an empty host `<div>`, so structure matches. The art is missing from the prerender, which is the flash F5. | every route that renders art | Declarative shadow DOM spike (F5). | CLEAN for hydration; visible flash |
| M5 | `src/components/MediaView.tsx:90-93`, `src/lib/motion.ts:29-39` | The `paused` and poster choice starts identically on both sides. | routes with image media (none today) | None now. | CLEAN |
| M6 | `src/lib/mediaBase.ts:4`, `src/data/fetch-json.ts:1`, `src/data/load.ts:8-10,94,104` | `Edition.mediaBaseUrl` is an absolute URL built from `window.location.origin`. Attributes built from it carry the build origin. | none today; latent for any `image` or `video` media | Never embed (section 3). For attributes, render a relative URL or resolve on the client only. Assertion 11 in section 5. | LATENT |
| M7 | `src/components/Rich.tsx:24-29` | DOM work (`createElement('template')`) in render, with identical output on both sides. | all routes with captions | None. Note for any future server rendering. | CLEAN |
| M8 | `src/components/FamilyTree.tsx:21-27,44` | No randomness or time. The "Sample links" chip is static (`:49`). | `/papers/*`, sample routes with nodes | None. | CLEAN |
| M9 | `src/components/Masthead.tsx:22-33` | Document listeners are added in effects; the Explore `<details>` starts closed on both sides. | all | None. | CLEAN |
| M10 | `src/components/head.ts:30-41` | Effects only. The title is set by the page's own `useHead` after SitePage's effect, so the page wins on both sides. | all | None. | CLEAN |
| M11 | `src/components/SitePage.tsx:16` | `scrollTo(0,0)` on mount. Not a mismatch, but resets scroll (F7). | issues, companies, map, samples | Skip on the hydration mount. | CLEAN for hydration; behavior fix |
| M12 | `src/blocks/LeadBlock.tsx:11-44` | Slide index 0 on both sides; the timer runs in an effect. | 3 papers | None for hydration. C2 is separate. | CLEAN |
| M13 | `src/pages/PaperPage.tsx:26-28` | Hash effect runs after mount. | 3 papers | Dependency change, see F8 and section 8. | CLEAN for hydration |
| M14 | `src/components/motion.tsx:23-27` (`MotionContext` default) and `src/lib/motion.ts:23` | Defaults are constant. | all | None. | CLEAN |
| M15 | `src/data/source.ts:37-44` | Reads the env only; no network, no client creation. | all | Do not call `pickSource()` on the hydration path. | CLEAN |
| M16 | `src/pages/SearchPage.tsx:8,16,24`, `src/pages/FeedPage.tsx:19-47` | Read `window` in render or effects. Not prerendered. | `/?search`, `/?feed` only | Gated by rule 6g. | Excluded |
| M17 | `src/App.tsx:36-53` (`currentRoute`) | `replaceState` for `?paper=` runs on the create path only. | `/?paper=…` | Decide before any replaceState (section 6). | Excluded |
| M18 | `src/pages/IssuePage.tsx`, `CompanyPage.tsx`, `SamplePage.tsx`, `src/components/common.tsx`, `TagShelf.tsx`, `src/blocks/StoryBlock.tsx`, `ComicBlock.tsx`, `FactsBlock.tsx` | Deterministic; `<details>` closed; `CompanyPage.tsx:15` throws on an unknown id, which the prerender already rejects. | their routes | None. | CLEAN |
| M19 | `src/pages/HomePage.tsx` `Newsletter` (`useState(false)`) | Constant initial state. | `/` | None. | CLEAN |
| M20 | `src/main.tsx` `StrictMode` | Double effects in dev only. Source caches dedupe the requests. | dev | None. | CLEAN |

**Headline.** 27 routes: 11 sample routes are clean for hydration (their art still flashes, F5). 16 routes have at least one real mismatch source. Of those, 12 (home, 6 issues, 5 companies) have both the date mismatch (M1, almost every reader after the build day) and the reduced-motion label mismatch (M2, reduced-motion readers only). `/map` has only M1. The 3 papers have only M2. Three URL forms (`?focus`, `?feed`, `?search`) are excluded by the route gate and never hydrate.

Notes on what was ruled out: no `Math.random`, no `Date.now` in render, no carousel other than the lead slideshow, no `localStorage` or `sessionStorage` anywhere under `src/`, and no webfonts.

---

## 8. Runtime read after hydration

**File mode.** No runtime read. The snapshot is the data, and no change is needed.

**Supabase mode.** The hydrated page starts with `view` from the snapshot. One effect then refreshes the live data:

```
useEffect (mount only, when initial.source === 'supabase'):
  live = pickSource().fetchLiveLibraryEntries()           // one request: all live rows
  doc  = paper ? pickSource().fetchStoryDoc(slug) : skip   // one request
  shell = getJson('data/library.json')                    // static, HTTP-cached
  library = overlayLive(shell, live), then hideSamples if the flag is set
  setView(prev => keepIdentity(prev, library, doc))
  if the route changed before this resolves, ignore the result (cancel flag)
```

Hook changes, in pseudo-code only:
- `App.tsx:66`: `view` starts as `initial ? viewFromInitial(initial) : null`.
- `App.tsx:70-75`: the existing `load()` effect runs only when there is no `initial`.
- `App.tsx:79-81`: the `loadSite()` effect runs only when there is no `initial`, because the site is already in the archive.
- New effect with `[]` deps: runs the refresh above when `initial.source === 'supabase'`. Failures go to `liveError` (section 9).
- `error` stays for pre-mount failures. `liveError` is new.

**What is re-read, and what is not.**
- Re-read: `pickSource().fetchLiveLibraryEntries()` (one request), `pickSource().fetchStoryDoc(slug)` (one request, paper only), and `data/library.json` (static, served from the HTTP cache).
- Not re-read: `site.json`, `tags.json`, `search-index.json` (static, decision 48), and nothing is re-run through `loadArchive` or `loadEdition`.

**Why `library.json` is fetched again.** `overlayLive` (`load.ts:69-80`) can only replace or append. If a story is unpublished after the build, a snapshot-based overlay would keep its entry forever. Overlaying the shell again gives the correct result. Decision 48 does not say this, so the lead should confirm (section 11).

**Cache rules.**
- Do not seed `getJson`'s cache or the source caches (`fetch-json.ts:8`, `source-supabase.ts:72-73`) from the snapshot. Seeding would make the live read return stale data. The source caches memoize promises, so the first call after hydration makes a live request.
- The source caches dedupe the two calls, so the StrictMode double effect is safe.

**Identity rules, so the page does not remount or jump.**
- `keepIdentity` keeps `archive.site`, `archive.vocab`, `archive.index`, and `edition.site` and `edition.vocab` by reference.
- It replaces `archive.library` and `edition.doc` only when the JSON differs. A string comparison is enough at this size.
- Without this, `PaperPage`'s `[site, doc]` effect (`PaperPage.tsx:28`) would re-run and scroll to the hash, and `SitePage`'s `[site, title]` effect (`SitePage.tsx:16`) would scroll to the top.
- The update is a functional `setView` that keeps `view.page` and `slug`, so React keeps the same component instances. Block keys (`block.id`) are unchanged, so `LeadBlock` keeps its slide index and `FamilyTree` keeps its picked node.

---

## 9. Error-state handling

**Before hydration (no snapshot, for example a client-only route).** Keep today's behavior: `App.tsx:84` replaces the page with the `load-error` `<main>`. There is no content to keep.

**After hydration (the live read fails, returns a non-matching schemaVersion, or a row is missing).**
- Keep `view`. The snapshot stays visible. The page must not show `load-error` and must not be replaced.
- Set `liveError` to a short message and `console.error` the cause.
- Render a banner from `App.tsx`, as a sibling after `content` in a fragment, and only when `liveError` is set. Because it is set after mount, it never appears in hydration markup.
- Banner: `role="status"`, fixed to the bottom of the viewport with `inset-inline: 16px` so the layout does not move. Its text states that the page could not check for updates and that the version shown was built on the build date, and may be out of date. It must not say the content is live. Styles go in `src/styles/site.css`. Class name `live-error`, not `load-error`, so the prerender check still means what it means today.
- Clear the banner on a successful refresh.
- Retry: not in this batch. A retry needs the source to drop a cached failure, which means changing `src/data/source-supabase.ts`, which is out of scope. The reader can reload the page.

**File mode.** The banner never appears. There is no runtime read.

**Prerender.** Prerender takes the create path (its shell has either no snapshot or a home snapshot that fails the route gate), so the refresh never runs during prerender. A live read failure during prerender still fails the route through `load-error`, as it does today.

---

## 10. Files touched by Wave 2 Agent B

Conservative list. Every file has one reason.

| File | Reason |
|---|---|
| `src/main.tsx` | Hydrate or create decision (section 6), `hydrateRoot` with `onRecoverableError`, `window.__mount_mode__`. |
| `src/App.tsx` | Optional `initial` prop, initial state from the snapshot, the one refresh effect (section 8), `liveError` banner (section 9), collector call in `load()` (section 4.1), and the pure route resolver shared with `main.tsx`. |
| `src/data/load.ts` | Export `overlayLive`, add `loadInitial` (builds the first view from a snapshot), and export the snapshot builder used by the collector. No change to fetching behavior. |
| `src/types.ts` | `SNAPSHOT_SCHEMA_VERSION`, the `InitialData` type, and the optional `window.__collect_initial_data__` declaration. |
| `src/lib/motion.ts` | Reduced-motion through `useSyncExternalStore` with a server snapshot of `false` (F10). Remove module-level `matchMedia`. |
| `src/lib/format.ts` | An effect-based `useToday()` hook for the masthead date (F9). `todayLabel` stays for any other caller. |
| `src/pages/HomePage.tsx` | One line at `:342`: use `useToday()`. |
| `src/components/SitePage.tsx` | Use `useToday()` at `:21`, and skip `scrollTo(0,0)` on the hydration mount at `:16` (F7). Coordinate with Agent C, who owns navigation scroll. |
| `src/styles/site.css` | Banner styles for `live-error` (section 9). |
| `scripts/prerender.ts` | Collector setter, leftover-id strip, doctype, escaping, injection before `</body>`, origin assertion (section 4). |
| `scripts/check-prerender.ts` | Assertions in section 5. |
| `src/components/MediaView.tsx` (conditional) | Only if the declarative shadow DOM spike passes (F5). Otherwise not touched. |

Not touched: `src/data/source.ts`, `src/data/source-supabase.ts`, `src/data/fetch-json.ts`, `scripts/prerender-routes.ts`, `supabase/`, `public/`, the other pages, blocks, and `Masthead`. `PaperPage.tsx` is not touched if `keepIdentity` preserves `doc` identity; otherwise its dependency list needs one change.

---

## 11. Risks and open questions

**Risks, most serious first.**

1. **The masthead date (M1) fires on 13 routes for almost every visit after the build day.** React 19 handles a text mismatch by re-rendering the root from scratch, which recreates every SVG and refetches the art. That brings the flash back in a different form, and it drops scroll and focus. This is the riskiest mismatch.
2. **The spike for the SVG art (F5) may fail.** It is unverified whether React 19.3 accepts a declarative shadow root as the existing children of a host it renders empty. If it does not, the art still flashes on every route that has art, and the fix is partial.
3. **Leftover snapshot from the shell (section 4.3).** If the strip is missed, every non-home page carries the home snapshot's id. The route gate then sends them all to `createRoot`. The fix would silently do nothing, and the browser check would be the only signal.
4. **Escaping.** The brief's "U+2028 → space" would change text silently. Use ` ` and ` `. `</` → `<\/` is weaker than `<` (section 4.5).
5. **Un-publish after build (section 8).** Overlaying a snapshot can keep a stale live entry. Re-overlaying the shell avoids this, but only if the shell is fetched after hydration. This needs the lead's confirmation.
6. **Origin leakage (M6).** No current media uses an attribute built from the base URL, so the HTML has no localhost URL today. Any future `image` or `video` media would leak it. The assertion in section 5 catches this.
7. **Quirks mode (F12).** Confirmed in the existing `dist/`. Adding the doctype changes the first paint of every page. Re-check the layout at 1280 px and 375 px.
8. **Snapshot size.** About 120 KB raw per paper page. Acceptable, but duplicated fields should stay out (section 3).
9. **Gated URLs keep the flash.** `/map?focus=` (from `FamilyTree`), `/?search` and `/?feed` always create the root. Direct visits to those URLs still show the flash. This is accepted for this batch.
10. **Deploy skew.** HTML from one build with JavaScript from another. The schema check catches shape changes but not content changes. Deploy HTML and assets together.
11. **Date label is blank in prerendered HTML.** A crawler sees no date. The reader sees the date appear after JavaScript runs. Both are acceptable, but this is a visible change.
12. **The collector global ships in production.** It is a no-op unless prerender installs it. The lead may prefer to gate it.

**Open questions for the lead.**

- Q1: Keep `window.__INITIAL_DATA__` (interface doc) or use the prop only? This plan recommends the prop only, which avoids two sources of truth.
- Q2: Approve the declarative shadow DOM spike before Wave 2 starts, since it decides whether F5 can be fixed in this batch.
- Q3: Date label: blank in prerender (recommended), or keep the build-day text and accept a stale date after midnight?
- Q4: Keep the full archive on every kind in this batch (recommended), with phase 2 pruning after measurement?
- Q5: Include `kind` in the snapshot? Not needed, since `route` resolves it. This plan omits it.

**Proposed amendments to decision 50 and the route-state interface (lead to confirm before Wave 2).**

- A1. Escaping (decision 50): replace every `<` with `<`. Replace U+2028 and U+2029 with JSON escapes, not spaces. Decision 50 currently says `</` → `<\/`.
- A2. Snapshot shape (decision 50): `edition` is `{ doc }` only. Add `source` and `hideSamples`. Name the version `SNAPSHOT_SCHEMA_VERSION`. Decision 50 says `schemaVersion` without naming it.
- A3. Route match (decision 50): compare the resolved page kind and the query, not only the pathname. Decision 50 says "whose `route` matches the current pathname", which does not cover `/?search`, `/map?focus=`, or the legacy `?paper=`.
- A4. Interface doc: drop the `window.__INITIAL_DATA__` global (Q1). Declare `App` as taking `initial?: InitialData`. Move `loadInitial` to `src/data/load.ts`.
- A5. Interface doc, "Snapshot is NOT a cache": add that the snapshot never seeds `getJson` or the source caches, and that the post-hydration refresh re-reads only the two Supabase calls and `library.json`.
- A6. Interface doc: state that the collector is called once per page load, for the first view only.
- A7. Decision 50's "prerendered HTML" section: add that the HTML carries `<!doctype html>` and that the snapshot is injected before `</body>`.
- A8. Decision 50 says the snapshot's `archive` is "the same objects `loadArchive()` / `loadEdition()` return". That is no longer true for `edition` (A2), so reword it.

No code, data, or tracked file was changed. Nothing was committed or pushed.
