# UX navigation plan (Wave 1, Agent C)

Analysis for Wave 2 Agent C. It follows `docs/handoffs/ux-route-state-interface.md` and corrects it where the code says otherwise (see the last section). Before-state evidence is in `docs/handoffs/ux-baseline-qa.md`. No navigation code is written here.

## Where client-side navigation gets installed

| File | Status | Responsibility |
|---|---|---|
| `src/lib/navigation.ts` | new | Owns `navigate(url)`, the single document-level click interceptor, the passthrough check, and the runtime focus-target helper. Holds the pending focus or scroll request that App applies after commit. |
| `src/App.tsx` | minimal edit | Re-exports `navigate` (`export { navigate } from './lib/navigation'`). In one mount effect: installs the interceptor, adds one `popstate` listener and one `geekytimes:navigate` listener, keeps a sequence token for stale loads, and applies the pending focus or scroll after each view commit. |
| Pages, blocks, components | untouched | No edits. The focus target gets `tabindex="-1"` at runtime (below), so no page changes are needed. |

Why `navigate` lives in `navigation.ts` and not `App.tsx`: the interceptor needs `navigate`, and App imports the interceptor. Putting `navigate` in App would create a circular import. App re-exports it so the interface doc's signature still holds.

## Click interceptor spec

Install exactly one listener, from App's mount effect, with cleanup on unmount:

```ts
document.addEventListener('click', onClick); // bubble phase, so component handlers run first
```

`onClick(e: MouseEvent)`, in this order, return early (native behavior) when any is true:
1. `e.defaultPrevented`
2. `e.button !== 0`
3. `e.metaKey || e.ctrlKey || e.shiftKey || e.altKey`
4. No anchor: `const a = (e.target as Element | null)?.closest?.('a[href]')` is null. Use `closest`, because the click target is often a child (a `<span>` inside a card, or an SVG inside `MediaView`).
5. `a.target && a.target !== '_self'`
6. `a.hasAttribute('download')`
7. Protocol is not `http:` or `https:` (covers `mailto:`, `tel:`, `javascript:`)
8. `new URL(a.getAttribute('href')!, location.href).origin !== location.origin` (external or protocol-relative to another origin)
9. Same document, hash only: the target's pathname and search equal the current ones and the target has a hash, including a bare `#`. Native behavior, no `navigate()`.

Otherwise: `e.preventDefault()` and `navigate(target.href)`.

Notes:
- Enter on a focused link fires a `click` with `button: 0`, so keyboard activation is covered by the same rule.
- Same-URL click (target equals `location.href`, no hash): intercept and treat as a push-less refresh, meaning focus rules only, no `pushState`.
- Masthead's own `document` click listener (Masthead.tsx:30) only closes the Explore menu. It does not conflict.

`navigate(url: string)` in `navigation.ts`:
1. Resolve `const next = new URL(url, location.href)`. If `next.href === location.href`, skip the push.
2. Otherwise `history.pushState(null, '', next.href)`. `pushState` does **not** skip equal URLs by itself, so the check above is required.
3. Set the pending request: `{ kind: 'push', hash: next.hash }`.
4. Dispatch `new CustomEvent('geekytimes:navigate')`. App's listener re-resolves the route and loads the view.

## popstate listener spec

Lives in App's mount effect, next to the click listener (`window.addEventListener('popstate', onRoute)`).

`onRoute`:
1. Read `prev = lastRouteKey` (a module-level `pathname + search` string set at the last commit).
2. If `location.pathname + location.search === prev`, it is a hash-only change (back or forward between two hash entries, or a manual `location.hash` write). Do **not** call `load()`. Set the pending request to `{ kind: 'hash', hash: location.hash }` and let the commit effect (or the immediate path) scroll to the target. If the element is missing, do nothing.
3. Otherwise, `const token = ++seq; load(currentRoute()).then(v => { if (token === seq) setView(v); })`. Any older load that finishes late is ignored.
4. Pending request for this path: `{ kind: 'pop' }`. App restores the saved scroll Y for this entry (see the focus and scroll section). It does not scroll to top.

Two points the interface doc does not cover:
- **Keep the old view on screen while the new one loads.** Do not `setView(null)` on in-app navigation. The loader is for the first load only. Otherwise every card click brings back the I3 flash inside the app.
- **`history.scrollRestoration = 'manual'`**, set once in the mount effect. Otherwise the browser restores scroll before async content exists and the position is lost.

`SearchPage` already has its own `popstate` listener (SearchPage.tsx:24-28) that re-reads `q` and `tag`. Keep it. A query-only change (`?search&q=a` to `?search&q=b`) makes App reload the view with the same cached archive objects, so SearchPage stays mounted and its own listener updates the query.

## Focus + scroll rules

Confirm the interface doc's rules, with three corrections:

1. **Apply after commit, not inside `navigate()`.** `navigate()` runs before the new view exists (the load is async). Scrolling there moves the old content. The pending request is applied from App after `setView` commits (an effect keyed on `view`, cleared once applied).
2. **Non-hash navigation:** `window.scrollTo(0, 0)` for kind `push`, and focus the focus target (below). For kind `pop`, restore the saved scroll Y instead.
3. **Hash navigation:** `document.getElementById(id)?.scrollIntoView()` (same behavior as PaperPage.tsx:26-28). Focus the element only if it is focusable. Otherwise focus the focus target.
4. **PaperPage's mount-time hash scroll (PaperPage.tsx:26-28) must not run as well.** Its effect deps are `[site, doc]`, so a hash-only change does not re-run it, but a push to another paper would run it on mount and double the scroll. Remove it in Wave 2, or make `navigate()` the only place that scrolls. Pick one; the interface doc currently says "same as current useEffect", which leaves both alive.

**Focus target (exact element).** `navigation.ts` resolves it at runtime, in this order:
1. `document.querySelector('main')`. Set `tabindex="-1"` on it first (a `<main>` without a tabindex cannot take focus), then `focus({ preventScroll: true })`. This matches HomePage.tsx:341, PaperPage.tsx:46, SearchPage.tsx:35, and the loader and error `<main>` in App.tsx:84 and 86.
2. Fallback for `/?feed`, which has no `<main>` (FeedPage.tsx:52, `div.feed`): `document.querySelector('.feed')`, with `tabindex="-1"` set the same way.
3. Last resort: `document.querySelector('h1')`.

`SearchPage` sets `autoFocus` on its input (SearchPage.tsx:42). Under these rules a client navigation to `/?search` would move focus to the input, which is the one exception to "focus main". Decide before Wave 2: keep it (it is a deliberate exception for search) or remove it. Recommendation: keep `autoFocus` only on a full load, and skip the focus-target step when the route is search.

## Legacy `/?paper=<slug>` redirect behavior

Today: `currentRoute()` (App.tsx:37-42) reads `?paper=`, rewrites the URL with `history.replaceState(null, '', paperHref(legacy) + window.location.hash)`, and returns the paper route. Baseline: the redirect works on a direct load (see the routes table).

How it stays working in Wave 2:
- Keep the redirect inside `currentRoute()`. Both the first load and every `popstate` call it, so the legacy URL works on each path.
- `navigate('/?paper=x')` pushes the legacy URL, then `currentRoute()` rewrites that entry in place with `replaceState`. Result: one history entry, pointing at `/papers/x`. Good.
- The redirect runs before the pending focus or scroll request is applied, so the focus target and hash are computed from the final path.
- The hash is kept (`+ window.location.hash`). Do not drop it when rewriting.
- The prerender deferral stays: `/?paper=<slug>` is not prerendered (`scripts/prerender-routes.ts` DEFERRED).

## Tests you'd expect lead to run before accepting Wave 2

Run on the built app (`npm run build`, then `npx vite preview`) and on `npm run dev`. Desktop 1280 and phone 375.

- [ ] Lead card click (`/` to `/papers/size-shapes-life`): no document reload (check `performance.getEntriesByType('navigation')` count or a `window` marker survives), no loader flash, old view stays until the new one commits.
- [ ] Every card, link, and tab on `/`, `/issues`, `/companies`, `/map`, `/papers/*`: intercepted, same-origin, lands on the right route.
- [ ] Modified clicks (Cmd, Ctrl, Shift, Alt) and middle-click: native, new tab, current page unchanged.
- [ ] `target="_blank"`, `download`, `mailto:`, `tel:`, external origin: native.
- [ ] Hash-only links (story tabs `#evidence`, `#machine`, `#tree`): no full navigation, scroll correct, URL correct.
- [ ] Back and forward between two papers: correct page, scroll Y restored (test at a scrolled position, not just the top).
- [ ] Back and forward across a hash-only change: no refetch (count network requests), scroll correct.
- [ ] Back and forward from `/?search&q=a` to `/?search&q=b`: query updates, SearchPage state correct.
- [ ] Enter on a focused lead link: navigates; focus lands on `main` (or `.feed` on `/?feed`), not on `BODY`.
- [ ] Focus does not move to `BODY` after a push; `autoFocus` on search only where decided.
- [ ] Legacy `/?paper=attention-is-all-you-need#evidence` direct load and as a navigate target: lands on `/papers/attention-is-all-you-need#evidence`, one history entry.
- [ ] Bad URL (`/this-page-does-not-exist`): error page, and after Wave 2 a way home (today there is none).
- [ ] Supabase mode and file mode (`VITE_DATA_SOURCE`): same behavior. A failed live read shows the error banner, not a silent old page.
- [ ] `npm run build`, `npm run lint`, `npm run prerender`, `npm run check:prerender` all pass.
- [ ] No console errors on any route (except the expected bad-URL error), no `[Company name]` placeholder regression, no horizontal page scroll at 375 (family-tree scroller excepted).
- [ ] Filmstrip repeat: fast and throttled, same method as the baseline. The paper must not show a blank loader after an in-app click.

## Corrections to `docs/handoffs/ux-route-state-interface.md`

1. **No `route` state exists.** App's state is `view` (App.tsx:66), with `error` and `site` alongside it. The route is resolved once inside a mount effect (App.tsx:70-75) and is not held in state. Fix the "Current shape" section and say that navigation sets `view` through `load()`.
2. **`load()` has no cancellation.** Two quick navigations can resolve out of order and the older one wins. Add the sequence token described in the popstate section.
3. **`navigate()` step 1 is wrong as written.** `history.pushState` does not no-op on an equal URL. The equality check has to be in `navigate()` itself.
4. **Focus and scroll cannot run inside `navigate()`.** They must run after the new view commits (see the focus section). The interface's ordering (step 3 after step 2) is correct only for the immediate parts (`scrollRestoration`, the pending request), not for the scroll itself.
5. **The focus target needs `tabindex="-1"`.** Without it, `focus()` on `<main>` does nothing. The interface's "or the first `<h1>`" fallback does not cover `/?feed`, which has no `<h1>` either. The target list is in the focus section.
6. **Passthrough list is incomplete.** Add: use `closest('a[href]')` (the click target is often a child element); and clarify that a hash-only link to the **same** document passes through, but a hash link to a **different** path is intercepted and must scroll after the commit.
7. **Hash scroll has two owners.** PaperPage.tsx:26-28 already scrolls to the hash on mount. Pick one owner (see the focus section) to avoid a double scroll.
8. **Popstate and hash-only changes are not specified.** Add the hash-only branch, which skips `load()`, and the rule to keep the old view on screen.
9. **Legacy `?paper=` is not mentioned.** Add that `currentRoute()` keeps the redirect, and that `navigate()` to a legacy URL ends with one history entry.
10. **`geekytimes:navigate` and `navigate()` overlap.** `navigate()` should dispatch the event, and App should be the only listener that loads. The interface lists both roles without saying which does what.
11. **Naming mismatch with decision 50.** The interface uses `window.__INITIAL_DATA__`. Decision 50 uses `<script id="__initial_data__">` and a `window.__collect_initial_data__` hook while prerendering. Reconcile before Agent B and Agent C both write App.tsx.
12. **Ownership of `main.tsx`.** Agent B owns the hydration path, and decision 50 says the prerendered loader and mount are changed there. Agent C's navigation does not depend on that choice, but the first-load logic in App must not be changed by both.
