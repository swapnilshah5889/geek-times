# Route-state interface for Wave 2 (seamless loading + nav)

Lead-authored. `src/App.tsx` is touched by both Agent B (initial render / hydration) and Agent C (navigation). To avoid merge conflicts and keep responsibilities clear, this is the only interface they both work to.

## Current shape (unchanged, as of Wave 1 Agent C read)

`App.tsx` already:
- Has a `view` state at `src/App.tsx:66` (not `route` — my earlier draft was wrong).
- Resolves the view from `pathname + search` once at mount.
- Renders one of: HomePage, PaperPage, FeedPage, SearchPage, etc.
- Calls `load()` with no cancellation. Wave 2 adds a sequence token so an in-flight fetch for the old URL can't overwrite state for the new URL.

## New shape (frozen here)

`src/App.tsx` exports:
```ts
export function App(): React.JSX.Element;              // unchanged
export function navigate(url: string): void;           // new (Agent C)
```

Internally `App.tsx`:
- Keeps the same `view` state + resolver.
- Sets `history.scrollRestoration = 'manual'` once at mount so in-app navigation controls scroll instead of the browser restoring old positions mid-swap.
- On mount, adds **one** `popstate` listener that re-resolves the view from `location.pathname + location.search + location.hash`.
- Adds **one** custom-event listener `window.addEventListener('geekytimes:navigate', ...)` that does the same.
- Each load pass carries a `sequenceToken` (a monotonically increasing counter); when the fetch returns, state is updated only if the token matches `latestToken`. Prevents stale-fetch races on fast back-forward or card-click-another-card.
- The exported `navigate(url)` function:
  1. Compares against `location.href` — if equal, no-op (`pushState` does not deduplicate).
  2. Calls `history.pushState(null, '', url)`.
  3. Dispatches `new CustomEvent('geekytimes:navigate')`.
  4. **Does NOT** touch focus/scroll inline. Those run in a `useEffect` that fires AFTER the new view commits.
- **Keep the previous view on screen during in-app navigation.** No loader flash for in-app transitions. The old view stays painted until the new one's state is ready; swap is instant. (A loader is still shown for the very first cold mount when there's no previous view.)

## Who owns which section of App.tsx

- **Agent B** owns: the initial-render path. On mount, decides hydrate vs createRoot via the snapshot check (`window.__INITIAL_DATA__`, see decision 50). If hydrating, uses the embedded archive/edition for the first render; after hydration, kicks off a runtime read in Supabase mode and sets state when it returns.
- **Agent C** owns: `navigate()`, the `popstate` and custom-event listeners, the click-interceptor module (`src/lib/navigation.ts`), and the focus/scroll handling after each navigation.
- **Lead** owns: merging their edits into App.tsx. Agents B and C write **minimal** App.tsx changes and put everything else into their own files.

## Focus and scroll rules (Agent C — amended after Wave 1)

Handled in a `useEffect` in App.tsx that fires AFTER the new view commits (NOT inside `navigate()`):
- If the new URL has a hash → **PaperPage keeps ownership** of the hash scroll (it's already there at `src/pages/PaperPage.tsx:26-28`). The App-level effect does nothing for hash navigations. One owner only.
- Otherwise → scroll to top via `window.scrollTo(0, 0)`, then `document.querySelector('main')?.focus()`. **`<main>` needs `tabindex="-1"`** (added to App.tsx) or `focus()` is a no-op.
- `/?feed` has no `<main>` landmark today (confirmed by C). Wave 2 wraps it in a `<main tabindex="-1">` so focus has somewhere to land.
- `popstate` does NOT re-run the scroll effect (browser's own scroll restoration would double-up with manual mode off). Since we set `history.scrollRestoration = 'manual'`, back/forward just updates `view`; the scroll is wherever the reader was when they navigated away. If they actually want top, they scroll.

## Native-anchor passthrough (Agent C)

The click interceptor skips when any of the following is true, so these behave as plain anchors:
- `e.defaultPrevented`, `e.button !== 0`
- `metaKey || ctrlKey || shiftKey || altKey` modifiers
- `a.target && a.target !== '_self'`
- `a.hasAttribute('download')`
- `a.getAttribute('href')` is missing, external origin, `mailto:`, `tel:`, `#` anchor to the same page, or protocol-relative to another origin

## Hydration data contract (Agent B — amended after Wave 1 analysis)

Snapshot shape (frozen after Wave 1 Agent B review; `docs/handoffs/ux-hydration-plan.md` is the authority for everything below):

```ts
interface Snapshot {
  schemaVersion: typeof SNAPSHOT_SCHEMA_VERSION;  // SNAPSHOT_SCHEMA_VERSION, SEPARATE from STORY_SCHEMA_VERSION=2
  route: string;           // the resolved route key (pathname + search as the router sees it), not raw location.href
  source: 'file' | 'supabase';  // which source produced this snapshot
  hideSamples: boolean;         // the build-time VITE_HIDE_SAMPLES value
  archive: { site; vocab; index; library };
  edition?: { doc };            // paper pages only; just the doc. Never site/vocab/mediaBase.
}
```

- **No `window.__INITIAL_DATA__` global.** `src/main.tsx` reads the `<script id="__initial_data__">`, parses it, and passes it to `<App initial={snapshot} />` as a prop. The App threads it to a new `loadInitial(route, snapshot)` helper in `src/data/load.ts` that returns it synchronously when the route + schemaVersion + source match.
- **Route match compares resolved page kind + relevant query**, not just pathname. Matching `/` vs `/?feed` as the same snapshot is wrong.
- **Snapshot NEVER seeds `getJson` / source caches.** After hydration completes, the post-hydration refresh re-reads the two Supabase calls + `library.json` fresh (so `overlayLive` can remove an unpublished story). The snapshot was only ever the markup's source; the caches are built from live reads.
- On any mismatch (missing script, bad JSON, schema mismatch, source mismatch, route mismatch) → fall back to `createRoot` + async fetch (today's path). Log once for diagnostics.
- JSON is escaped safely at write time: every `<` → `<`, every `U+2028` → ` `, every `U+2029` → ` `. (Correction to decision 50's loose paraphrase: `U+2028 → space` would silently corrupt text; use the escape.)

## Snapshot is NOT a cache

After hydration:
- File mode: a runtime re-read of `library.json` still runs (sample-hiding + overlay correctness require it). Story docs are not re-fetched in file mode — the snapshot's `edition.doc` matches the file byte-for-byte.
- Supabase mode: a runtime fetch runs for story docs + live library entries, same as today. If it returns different content, state updates and the page re-renders (small parts only — no root remount).
- If the runtime read fails: an inline error banner is shown, the snapshot stays visible. Not "pretend the snapshot is live."
- The snapshot itself never writes into the `getJson` / `Promise` caches. Caches are seeded only by live reads.

## check:prerender additions (Agent B)

`scripts/check-prerender.ts` additionally asserts for every route:
- `<script id="__initial_data__" type="application/json">` exists.
- Parses as JSON.
- `schemaVersion === 1`.
- `route` equals the route the HTML was written to.
- `archive` has the expected top-level keys.
- Paper pages carry `edition`.

## Hydration-mismatch audit (findings from Wave 1 Agent B)

Real mismatches found across the 27 prerendered routes (full detail in `docs/handoffs/ux-hydration-plan.md`):

- **Masthead date** (`src/lib/format.ts:3` → every page via `HomePage`, `SitePage`, `App`). Rendered as `Friday, 6 November 2026` from `new Date()`. On any visit after the build day the server/client text differs, which triggers a **full-root re-render** in React 19, recreating every SVG and re-firing fetches. Highest-impact single fix. Wave 2 approach: prerender writes a blank date; the real date fills in client-side in `useEffect`. (Confirmed by lead.)
- **Reduced-motion label** (`src/lib/motion.ts`, `src/components/motion.tsx`). Reads `matchMedia('(prefers-reduced-motion)')` at render time. Same fix: compute in `useEffect`.
- **Doctype missing** on prerendered HTML — pages render in quirks mode. Wave 2 adds `<!doctype html>` to the prerender template.
- Query-only routes (`?feed`, `?search`, `?focus`) are not prerendered; they go through `createRoot`.
- Clean (checked, nothing to fix): FamilyTree, Rich, Masthead, head.ts, LeadBlock slideshow (index starts at 0; timer is in an effect), MediaView's empty host, all random/time/localStorage guards. No surprises here.

Use `suppressHydrationWarning` only where the mismatch is cosmetic and intentional (none planned).

## Small in-scope bug fixes bundled into Wave 2 (from Agent C's QA)

These touch navigation / loading UX directly and ship with this batch:
- **Error page gets a masthead + home link.** Today a bad URL shows a bare message; Wave 2 renders the full frame so the reader can navigate out.
- **`/?feed` gets a `<main tabindex="-1">` wrapper.** Focus target for in-app nav.
- **SearchPage `autoFocus` stops stealing focus on client navigation.** Guard: only autoFocus on cold mount, not after `navigate()`.
- **Favicon 404.** Add a minimal SVG favicon in `public/` and a `<link>` in `index.html` (same batch; cheap, stops the 404 noise).

Documented but NOT fixed this batch (owner's call, not nav-shaped):
- `/companies` defaults to the `[Company name] Engineering` sample. Content/library fix, not a nav fix.
- The check:prerender duplicate-title warning on `/companies` is downstream of the same content issue.

## What Wave 2 does NOT touch

- `src/pages/*`, `src/blocks/*`, `src/components/*` unless a hydration mismatch is uncovered OR the small bundled bugs above require it. Each such touch is reported with the before/after snippet.
- Any data model, SQL, importer, or `src/data/source-supabase.ts` behavior.
