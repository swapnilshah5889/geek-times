# UX baseline QA (Wave 1, Agent C)

Before-state of routing and loading on branch `v1`, measured 2026-11-06 before any Wave 2 change. No code changed.

Method and caveats (read these before the numbers):
- **Data mode.** The dev server on :5173 runs in Supabase mode. Confirmed from the network trace: the story document and the live library come from `btqiijvuqpdzyvciqpak.supabase.co/rest/v1/published_version`.
- **Browser pane (`seed` tab).** Used for the route checks, the lead click, keyboard, back, and the Supabase network trace. The pane was hidden when the run started (`innerWidth` 0), so I set 1280x800 and later cleared it. Its tab history also holds unrelated pages from other local servers (`localhost:8765`, `localhost:5178`), so pane back/forward is only partly reliable. `performance.getEntriesByType('paint')` returned `[]` in the pane, so **pane timing numbers are not reported**.
- **Headless Chrome.** Timings, filmstrips, overflow, and modified-click tests run in headless Chrome driven by puppeteer (the repo devDependency that `npm run prerender` already uses). The pane returns screenshots inline and cannot write files, which is why the `/tmp` frames come from puppeteer.
- **Throttle method (no `.env` change).** I did not change `VITE_DATA_SOURCE`, so `.env` was never written. Puppeteer request interception holds every request to `…/data/*.json` on localhost and every `supabase.co` request for **1250 ms** before continuing. Requests are held per call, and the story document read waits behind the archive load, so the stall to the paper is two held rounds (about 4 to 5.4 s in two runs), not one 1.25 s delay.
- **Dev vs production.** The dev server serves unminified modules, so dev numbers overstate load cost. The production bundle is `dist/assets/index-*.js` at 502 KB (142 KB gzip).

## Routes covered

Every URL checked in the pane and again in headless Chrome at 1280 and 375 wide (page title and `h1` read from the DOM).

| Route | What the reader sees |
|---|---|
| `/` | Front page (design D). Lead: "Why a bigger deer breaks" (`size-shapes-life`). Asides: CRISPR, AlphaFold, Penicillin. Edition band. |
| `/papers/attention-is-all-you-need` | "One word, two worlds." Full paper page with story tabs (The big idea, How it works, Family tree, Evidence, Explore related ideas) and the family tree. |
| `/papers/size-shapes-life` | "Why a bigger deer breaks." Preprint, the front-page lead. |
| `/papers/h3-hexagons` | "A world covered in honeycomb." Uber company post. |
| `/papers/resnet` | "Shortcuts that go deeper." Sample page with a Sample badge (not a real paper). |
| `/issues` | Issue 002, "Why size matters" (latest issue). |
| `/issues/002` | Same issue, by id. |
| `/companies` | Shows the first company, `streaming`, which is a sample. Title and `h1` read "[Company name] Engineering: Streaming & entertainment". **Placeholder text in the title and heading.** |
| `/companies/uber` | "Uber Engineering: Maps & rides." |
| `/map` | "The map of ideas." |
| `/?feed` | Snack mode: 44 cards, title "The Geeky Times — Snacks". **No `<main>` landmark** (`mains` = 0). |
| `/?search` | Search page, 3 results, search input has focus (`autoFocus`). |
| `/?paper=attention-is-all-you-need` | Legacy link. Rewritten to `/papers/attention-is-all-you-need` by `replaceState` (App.tsx:38-41) and renders the paper. |
| `/papers/attention-is-all-you-need#evidence` | Direct deep link with a real anchor. Scrolls to Evidence (scroll Y 5343, Evidence top 0). |
| `/papers/attention-is-all-you-need#how-it-works` | This hash does not exist on the page (no element with that id). The page loads at the top with no error. The story tab "How it works" points at `#machine`, which does exist. |
| `/this-page-does-not-exist` | "Sorry, this page could not be loaded. There is no page at “/this-page-does-not-exist”." No masthead, no link back. Title stays "The Geeky Times". |

## Current front→paper behavior

Measured in headless Chrome (dev, warm cache), timeline from the click:

1. **0 ms.** Click on the lead card. The lead link is a plain `<a href>` (HomePage.tsx:89, 92, 97), so the browser starts a **full document navigation**. The front page stays on screen until the new document paints.
2. **~42 ms.** The new document starts. `#root` is empty (`index.html:9`).
3. **~73 ms.** React mounts (`main.tsx:7`, `createRoot`). The first view is the loader: "Setting the type…" inside `<main aria-busy="true">`, with no masthead (App.tsx:83-90).
4. **~93 ms.** Masthead appears. It waits for `site.json` (App.tsx:79-81, 87).
5. **~246 ms.** The paper (headline, lead, and sections) appears in one commit. The view is set only after the archive and the edition load (App.tsx:55-63, 71). Scroll resets to the top, and focus lands on `BODY`.

Throttled (1250 ms hold per data and Supabase request), same timeline:

1. **0 to 121 ms.** Old front page, then the new document parses.
2. **132 ms.** Loader, still with no masthead.
3. **1391 ms.** Masthead appears under the loader.
4. **4115 ms (run A) and 5377 ms (run B).** Paper appears. Both are after the 3 s filmstrip window.

Visible interruptions, front→paper (IDs are used in the cause table below):
- **I1.** Full document swap. The front page is replaced by a new document, not a route change.
- **I2.** Blank page before the bundle runs (`#root` empty).
- **I3.** The loader replaces the page. Content is replaced by "Setting the type…" for the whole load (about 170 ms warm, about 4 s throttled).
- **I4.** Masthead pops in late, after the loader text is already on screen.
- **I5.** Two serial loads keep the loader up: the archive (`library.json`, `search-index.json`, and the live library overlay) first, then the story document. The paper does not need the archive, but it waits for it.
- **I6.** Focus and scroll reset to `BODY` and the top after the swap. No focus management exists.

## Filmstrip, dev server at full speed

Files: `/tmp/ux-baseline-fast-01.png` through `/tmp/ux-baseline-fast-20.png`. Method: `/` → click the lead link → 20 screenshots at a 150 ms target interval, 1280x800. Actual spacing was about 150 ms, screenshot time included. Timeline captured in the same run.

| Frame | t (ms) | State |
|---|---|---|
| 01 | 1 | Old front page, lead card visible |
| 02 | 150 | Expected loader and masthead (timeline: loader 73 ms, masthead 93 ms). Not inspected visually |
| 03 | 301 | Full paper (inspected) |
| 04 to 20 | 451 to 2851 | Full paper, unchanged |

The first full-speed run gave the same result (paper at about 413 ms). The loader lasts about 170 ms and the full paper appears at about 246 ms.

## Filmstrip, throttled

Files: `/tmp/ux-baseline-throttled-01.png` through `/tmp/ux-baseline-throttled-20.png`. Method: same as above, with the 1250 ms per-request hold described in the caveats.

| Frame | t (ms) | State |
|---|---|---|
| 01 | 0 | Old front page |
| 02 to 10 | 150 to 1351 | Loader "Setting the type…" with no masthead. Frame 08 (1051 ms) inspected: italic loader text on a blank cream page |
| 11 to 20 | 1501 to 2850 | Loader plus masthead, no paper yet |

The paper headline arrives after the window, at 4115 ms in one run and 5377 ms in another. The reader sees the loader for about 4 s on a slow connection.

## Direct-load FCP

Fresh navigation, headless Chrome, 3 runs each. First Contentful Paint and Largest Contentful Paint are from `PerformanceObserver` with `buffered: true`. "Headline" is the time the `h1` first exists in the DOM.

| Page | FCP (ms) | LCP (ms) | Headline (ms) | What FCP and LCP are |
|---|---|---|---|---|
| Dev `:5173`, `/papers/attention-is-all-you-need` | 96 / 80 / 68 | 120 / 120 / 100 | 576 / 308 / 217 | FCP is the loader text. LCP is the masthead brand (`DIV.mast`) |
| Prerendered `:5174`, `/papers/attention-is-all-you-need/` (after `npm run build && npm run prerender`) | 40 / 44 / 40 | 76 / 80 / 108 | 11 / 12 / 12 | FCP is the prerendered paper. LCP is the masthead brand. The loader replaces the paper at 53 to 61 ms |

**Headline numbers for the attention paper:** direct-load FCP **40 to 44 ms** on the prerendered HTML (68 to 96 ms in dev), LCP **76 to 108 ms** (masthead brand), in both cases before the paper's content is re-rendered by React.

The pane could not report these (paint entries came back empty).

## Prerender preview behavior

- `npm run build`: passes.
- `npm run prerender`: **27 of 27 routes**, 24.8 s. Deferred by design: `/?feed`, `/?search`, `/?paper=<slug>`.
- `npm run check:prerender`: **passes**, with one warning: `/companies` and `/companies/streaming` share the title "[Company name] Engineering: Streaming & entertainment".
- Static preview: `npx vite preview --port 5174`, stopped after the run. `curl` on `/papers/attention-is-all-you-need/` returns 200 with a 30 KB HTML file that contains the masthead and the `h1` "One word, two worlds." It has **no** `__initial_data__` script (decision 50 is not implemented yet).

What the reader sees, from the first byte (headless, plain, timeline in ms):
- **10 ms.** The prerendered paper, with headline and masthead, is in the DOM before any script runs.
- **52 ms.** React's `createRoot` (main.tsx:7) clears it and renders the loader inside `main[aria-busy]` (App.tsx:83-90).
- **68 ms.** Masthead returns (after `site.json`).
- **364 ms.** The paper returns (after the archive and the story document).

So: the prerendered HTML **does show first**, then **it is replaced**. The reader sees the paper for about 40 ms, a blank loader for about 300 ms, and then the paper again. Throttled: the paper disappears at 70 ms, the masthead appears at 1354 ms, and the paper at 5377 ms.

## Keyboard + back/forward + direct URL + modified clicks

| Check | Result today | Evidence |
|---|---|---|
| Tab order from top | Works. Order: Weekly edition, brand, Front page, Explore, Real world, Snacks, Editions, Search, Pause animations. The lead link is further down. | Pane, one Tab per step |
| Enter on a focused lead link | Works, but a **full page load**. Focus lands on `BODY` afterwards. | Pane and puppeteer (`focusAfterLoad` = BODY) |
| Back from a paper to the front page | Works. The front page reloads and the lead is present. Scroll is at the top (only tested from the top). | Puppeteer `goBack` → `/` with lead |
| Forward | Works in puppeteer (`goForward` → paper). Not reliable in the pane (history contaminated by other localhost pages). | Puppeteer |
| Direct URL | Works for every route in the table above. Unknown URL shows the error page (dead end: no masthead). | Route sweep |
| Hash deep link to a real anchor (`#evidence`) | Works. Scrolls to the section after the page renders (PaperPage.tsx:26-28). | Pane and headless |
| Hash deep link to a missing anchor (`#how-it-works`) | No scroll, no error. Acceptable. | Pane |
| Same-page hash click (story tab `#evidence`) | Works natively: URL changes, no reload, scroll moves. | Puppeteer: `urlChanged` true, scroll Y 5357 |
| Middle-click on a card | Opens a **new tab** natively (`newTab` = true). The current page stays on `/`. | Puppeteer `button: 'middle'` |
| Cmd-click on a card | Opens a **new tab** natively (`newTab` = true). The current page stays on `/`. | Puppeteer `Meta` + click |
| Shift-click (dispatched) | Not prevented (`defaultPrevented` false). | Pane |

No click handler on any anchor calls `preventDefault` today. Masthead's document-level `click` listener (Masthead.tsx:30) only closes the Explore menu and does not prevent default.

## Console errors, hydration warnings, horizontal overflow

Route sweep at 1280 and 375 (headless, each route 2.5 s after load). Results per route:

| Route | Console errors | Hydration warnings | Page horizontal overflow (`scrollWidth` > width) |
|---|---|---|---|
| `/` | `404 /favicon.ico` (once per browser session, no icon anywhere) | 0 | 0 at 1280 and 375 |
| `/papers/attention-is-all-you-need` | 0 | 0 | 0 page-level. Family-tree boxes overflow **inside `.ft-board`** (25 at 1280; 60 at 375), which is a contained scroller |
| `/papers/size-shapes-life` | 0 | 0 | 0 page-level. Tree boxes inside `.ft-board` (11 at 375) |
| `/papers/h3-hexagons` | 0 | 0 | 0 |
| `/papers/resnet` | 0 | 0 | 0 page-level. Tree boxes inside `.ft-board` (7 at 375) |
| `/issues`, `/issues/002`, `/companies/uber`, `/map` | 0 | 0 | 0 |
| `/companies` | 0 (but the title and `h1` are placeholder text) | 0 | 0 |
| `/?feed` | 0 | 0 | 0 (note: no `<main>`) |
| `/?search` | 0 | 0 | 0 |
| `/?paper=attention-is-all-you-need` | 0 | 0 | 0 |
| `/this-page-does-not-exist` | `Error: There is no page at “/this-page-does-not-exist”.` (App.tsx:49, logged at App.tsx:72) | 0 | 0 |

**Non-zero, named:**
1. `404 /favicon.ico` on the first page load in a session. Cause: `index.html` has no icon link, and `public/` has only `data/` and `media/`.
2. The bad-URL error is logged on purpose. It is still a console error.
3. Family-tree overflow is inside a deliberate horizontal scroller (`.ft-board`), not page scroll. It is listed so the AGENTS.md "no horizontal scroll at 375px" rule has a clear answer.
4. Placeholder text on `/companies`: title and `h1` read "[Company name] Engineering" (sample company data).

No React dev warnings were captured in any route. That is expected, because the app uses `createRoot`, not `hydrateRoot`, so there is no hydration step to mismatch.

## Observed causes of each interruption

| ID | Interruption | File and line | Evidence |
|---|---|---|---|
| I1 | Full document swap on card click | HomePage.tsx:89, 92, 97, 117, 157, 163, 170, 192, 221, 251, 272, 292, 306 (plain `<a href>`); no click interceptor exists | Network: a `GET /papers/size-shapes-life` document request, then all modules re-requested |
| I2 | Blank page before the bundle runs | index.html:9 (`<div id="root"></div>`); main.tsx:7 | Timeline: `rootKids` = 0 until 73 ms |
| I3 | Loader replaces content for the whole load | App.tsx:83-90 (`else if (!view)` loader); App.tsx:70-75 (the load starts in an effect, after first render) | Frame 08 throttled: loader only |
| I4 | Masthead appears late, under the loader | App.tsx:79-81 (`site` loaded in its own effect); App.tsx:87 (`site &&`) | Timeline: masthead at 93 ms warm, 1391 ms throttled |
| I5 | Serial waterfall: archive, then story document | App.tsx:55-63 (`await loadArchive()` before `loadEdition`); load.ts:114-117 (archive loads `library.json`, `search-index.json`, live overlay); load.ts:98-105 (edition waits for `fetchStoryDoc`) | Supabase trace: live library at 39 to 101 ms, story doc at 103 to 168 ms (warm). Throttled: paper at 4.1 to 5.4 s |
| I6 | Focus and scroll reset after swap | No focus or scroll handling anywhere. PaperPage.tsx:26-28 only scrolls to a hash on mount | Pane and puppeteer: `focused` = BODY |
| P1 | Prerendered paper replaced by React on mount | main.tsx:7 (`createRoot`, decision 45) | Timeline: paper removed at 52 ms |
| P2 | Loader and masthead-only frame in place of the paper | App.tsx:83-90 and App.tsx:87 | Timeline: loader at 52 ms, masthead at 68 ms |
| P3 | Paper re-rendered after the waterfall | App.tsx:55-63 (same waterfall as I5) | Timeline: headline back at 364 ms |

**Count.** Nine distinct visible interruptions: six for front→paper (I1 to I6) and three for prerender→mount (P1 to P3). P3 is the same waterfall as I5, seen on a direct load. P1 and P2 come from the same two lines as I2 and I3.
