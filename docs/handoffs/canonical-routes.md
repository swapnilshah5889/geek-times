# Canonical routes: `/issues` and `/companies`

Status: options only, prepared 2026-11-05 on `v1`. No layout is proposed, no component is touched and no canvas work has
started. This tracks the Phase 2 item "Canonical route pass" in `docs/production-plan.md`.

## The problem

- `/issues` (with no id) shows the latest issue. `/companies` (with no id) shows the first company (`src/App.tsx`, and the
  comment in `scripts/prerender-routes.ts`). So each bare index duplicates a detail page and carries the same title.
- `npm run check:prerender` reports these as duplicate-title warnings. They are warnings, not failures
  (`scripts/check-prerender.ts`, around line 104).
- The bare URLs are not dead ends. They are linked as lists:
  - `Masthead`: "Editions" → `/issues`, "Real world" → `/companies`, and "Weekly edition →" → `/issues`.
  - Footer and front-page sidebar: "Past editions" → `/issues`.
  - Front page: "All companies →" → `/companies`.
  - Breadcrumbs on company pages use `/companies` for both "In the real world" and "Companies".
- So a reader who clicks "Real world" lands on one company, and "Editions" on one issue.
- The "first" company is `streaming`, which is sample content. Under `VITE_HIDE_SAMPLES=1` it is dropped, and `/companies`
  would then show `uber`. Any redirect target chosen by list order depends on that sample flag.

## Option A: build real archive pages

- `/issues` becomes a grid of every issue's cover. `/companies` becomes a grid of every company card. Each has its own title.
- **Pros:** both URLs do what the navigation already promises. The pages stop duplicating a detail page, which removes the
  duplicate-title warnings. The pages grow with the content.
- **Cons:** two new components to build. It needs canvas sign-off first (AGENTS.md, canvas before code). Sample cards show
  until Phase 2 content lands.
- **check:prerender:** adds two distinct prerendered pages, each with its own title and description.

## Option B: 301 the index to the canonical child

- `/issues` → `/issues/<latest>`, and `/companies` → `/companies/<first>`.
- **Pros:** no new UI. The duplicate-title warnings go away. It matches what the pages already render.
- **Cons:**
  - `/issues` and `/companies` stop being pages. The navigation still points at them, so the nav needs changing too, and
    bookmarks may surprise readers.
  - The target moves as issues are added. A 301 is permanent and browsers cache it, so a moving "latest" target fits badly.
  - On static hosting the target is fixed at build time, so it has to be regenerated when a new issue lands.
  - `<first>` depends on list order, which today is a sample company (see above).

## Recommendation: Option A

The navigation, footer and front page already send readers to `/issues` and `/companies` as lists ("Editions", "Past
editions", "Real world", "All companies"). Making them real lists keeps that promise, while Option B would send a reader who
clicks "Real world" to a single company.

If the canvas step slips past the next batch, Option B is an acceptable stopgap, but only after a decision-log entry that
fixes the redirect rule (a fixed target, not "latest").

## Next steps (not started)

- **Option A:** a canvas board with one or two layouts for each index page; the owner picks; then build.
- **Option B:** a decision-log entry, a redirect rule for the moving target, and the nav links updated to match.
- Either way, the duplicate-title warning goes away only once one option lands. The warning itself should not be silenced
  before then.
