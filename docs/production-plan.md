# Production plan

Where The Geeky Times stands, what a review of the code found, and every step left before a public launch.
Written 2026-11-04 on `feature/convert-scaling-paper`; updated 2026-11-05 on `v1` (decision 40). Keep it current: tick items as they land and move findings into
"Fixed" when they are resolved. Background: `AGENTS.md`, `docs/decisions.md`, `docs/roadmap.md`.

## 1. Review (2026-11-04)

Scope: everything on `main` plus this branch (the second story, the convert-paper runbook, approved tags, the key
decision). Checked by reading the code and by running the site at 1440px and 375px.

### Bugs to fix first

None open. B1–B4 are resolved (see "Fixed" at the end); the Codex review's small fixes are under "Fix now" in section 3.

### Gaps against our own rules

- **Unverified graph shown to readers.** The roadmap said the family tree and map ship with *verified* relations only.
  They are built and labelled "to be fact-checked", but every link is still unreviewed.
- **Sample content would ship.** Eleven sample stories, sample companies, sample issues and placeholders such as
  `[Company name]` and `[publish date]` render on the live pages. Fine for design review; not for launch.
- **Data-model diagram is stale.** Board 6 on the canvas still shows `id` where decision 30 says `key`.
- **New tags have no hierarchy.** The 24 new tags dropped their cross-facet parents. The area facet is fixed on `v1`;
  other new tags still have none (Phase 0).
- **`hook` is unused.** Both stories carry a cover hook that no page shows.

### Engineering risks

- **No tests and no CI.** Only `npm run data`, `tsc`, `oxlint` and `vite build`, run by hand. Nothing stops a broken
  push from merging.
- **No share previews.** It is a client-rendered SPA with one generic `<title>` and no Open Graph tags. Links shared
  on social apps show no headline or picture, which hurts the virality goal most.
- **Hosting fallback.** Paths like `/papers/<slug>` need the host to serve `index.html`. Configured in `vercel.json` on `v1`; live once `v1` merges to `main`.
- **Every page loads the whole archive** (site, tags, search index, library). Fine at 2 papers, slow at hundreds.
- **Media from another host.** SVGs are fetched and inlined; a CDN must send CORS headers or the art falls back to
  `<img>` and stops being pausable.
- **Dead code.** Fixed on `v1`: `front.ts` is now `feed.ts`, and the old bento CSS is gone.
- **Accessibility unverified.** Built to the rules (labels, focus rings, list view for the map), but never run through
  a screen reader or an automated checker. Focus outlines on SVG map nodes may not show in every browser.

### What is solid, and what is only intended

- Content is data: stories, library, tags and media paths are JSON. The build checks tags, hooks and library references.
  It does **not** yet check the trust rules (fact claim kind, sources, anchors, alt text, duplicate ids).
- Trust labels are on the front page, comic strips, story fact cards, the feed and evidence cards (one shared `Stamp`, `fd67461`).
- Two real stories from different fields prove the model isn't AI-only.
- Tool-neutral knowledge (`AGENTS.md`, `docs/`, `skills/`) lets any model resume the work.
- No horizontal overflow at 375px on every page checked.

## 2. Achieved

**Product and design**
- [x] Name: The Geeky Times. Newspaper look, cartoon illustrations, kid-level language.
- [x] Design canvas with front page options A–D (D chosen), issue, story, company, map and data-model boards; Codex
      review applied (revision 2); calmer covers, section heads and shadow-free tiles (revisions 3–5).
- [x] Canvas-before-code and ask-before-branching rules recorded in `AGENTS.md`.

**Site (React + TypeScript + Vite)**
- [x] Front page D: lead, aside, and Keep exploring (more from the issue, snacks, topics, real world, numbers,
      storylines, vault and on this day, back issues, newsletter placeholder).
- [x] Story pages with five tabs, picture story, comic strips, evidence cards, family tree and tag shelf.
- [x] Issue, company and map pages (with list view), swipe feed, search with stemming and tag filters.
- [x] Path URLs (`/papers/<slug>`, `/issues`, `/companies`, `/map`); old `?paper=` links redirect.
- [x] Same navigation on every page; reduced motion and a pause switch for animations.
- [x] `VITE_HIDE_SAMPLES=1` build flag: hides every `sample` item at load time (`src/data/load.ts`, `048ad1d`).
- [x] `vercel.json` SPA rewrite so `/papers/<slug>` deep links load directly (on `v1`, `b3b2cb8`).
- [x] SSG prerender spike for one route (decision 41, `e4996af`).

**Content and data**
- [x] Story 1: "One word, two worlds" (Attention Is All You Need, peer-reviewed).
- [x] Story 2: "Why a bigger deer breaks" (arXiv 2408.04070, preprint), with a fact-check record.
- [x] 83-tag vocabulary; `library.json` editorial layer; build-time validation of every reference.
- [x] Claim kinds on facts, and a model-design stamp.

**Process**
- [x] `skills/convert-paper` runbook plus explain, fact-check, tag, draw and publish skills.
- [x] Database plan: content model v2, Postgres auto-increment ids, slugs as public keys, no foreign key constraints.
      Hosting decided: Supabase (decision 34).

## 3. Remaining steps to production

Each phase ends in something the owner can see and approve. Phases 1–2 can overlap; 3 needs 2; 5 needs everything.

### Fix now (from the Codex review; small, before Phase 1)

Landed on `v1` in `fd67461` (shared claim label, unique keys, "Swipe all snacks"). See "Fixed" at the end.

- [~] Family tree: kept as demo content by the owner's decision. The current nodes and links are placeholders for layout review; don't invent or reshuffle them. The real build lands with Phase 2 (verified relations). See `src/components/FamilyTree.tsx` banner and `docs/STATE.md` "Known gaps kept on purpose".

### Phase 0: Clean up what exists (small, do next)

- [x] Fix B1–B4 (B1 disappeared with the edition redesign; B4 approved on the canvas).
- [~] Add parents for the new tags inside their own facets. Done for the area facet (`area/physics`, `area/biology` and their children, `fd67461`). Still open: several new concept, technique and use tags have no parent (for example `concept/heat-loss`, `concept/diffusion`).
- [ ] Redraw the data-model board for decision 30.
- [x] Dead CSS removed (old bento tiles, hooked cover); `front.ts` renamed to `feed.ts`.
- [x] `docs/roadmap.md` now points here: this file is the only maintained launch sequence.
- [ ] Redraw the data-model board again for decisions 34–37.

### Phase 1: Rendering + preview path

- [~] **Rendering decision and spike (decisions 36 and 41):** decided as static generation (SSG) by prerender postbuild. One story
      is prerendered and checked (`e4996af`). **In progress:** extending `ROUTES` in `scripts/prerender.ts` to every page.
      **Deferred:** client hydration (`hydrateRoot` with embedded data, so readers don't see a loading flash) and Vercel build wiring.
- [x] Preview deploy per push so the owner can review on a real URL. Vercel at https://the-geeky-times.vercel.app/ (tracks `main`); `vercel.json` adds the SPA rewrite so `/papers/<slug>` and other deep links don't 404 on direct load once `v1` merges. Still unticked at Phase 5: HTTPS / custom domain / CSP.

> **Automated tests, CI and axe checks are deferred to the pre-launch gate (decision 39).** They aren't in Phase 1 while
> the app is pre-v1 (still showing demo tiles and reading JSON files) because they slow iteration. See the
> "Pre-launch hardening" section below, which runs right before Phase 5.

### Phase 2: Real content to replace samples

- [ ] One real company engineering post (tests company-reported labels and the company page).
- [ ] Three to five more papers across fields, through `skills/convert-paper`, so every front-page section has real
      stories.
- [ ] Verify family-tree and map relations with citations (`RelationEvidence`); hide unverified links from readers.
- [ ] Real edition metadata: publish dates and at least two real past editions (no editor's note).
- [ ] A switch that hides everything marked `sample` in production builds; remove all `[placeholder]` text.

### Phase 3: Platform

- [ ] Content model v2 and migration (`docs/data-model.md`).
- [ ] **Supabase** projects: local, staging and production (decision 34). Schema per decision 30 as SQL migrations in
      `supabase/migrations/`, applied with the Supabase CLI. Keys only in environment variables.
- [x] Foreign keys: decided, none (decision 38). Tables join on `<thing>_id` primary-key columns; every `_id` column is indexed;
      nested reads use SQL views, database functions or server code, not the auto-generated REST embedding.
- [ ] Prerequisite schema before any row-level security: relation `status` with evidence, and immutable published versions
      that own their derived rows (`published_version_id`).
- [ ] Row-level security and a paged runtime API: **only when a runtime feature needs them** (decision 36). Not on the launch
      path, which is static pages.
- [ ] Import job from JSON into Supabase with the integrity checks, **required** because there are no foreign keys (decision 38):
      transactional publish, unique, check and not-null constraints, an orphan check before every publish, orphan monitoring
      with alerts, and tests that every import and export reference remaps. Publish rules: `docs/data-model.md`, "Publish and import atomicity".
- [ ] Media on a CDN with CORS (Supabase Storage or S3: decide); set `mediaBaseUrl` per environment.

**Backup deliverables (decisions 35 and 37)**, each with an owner and cadence:

| Deliverable | What it is | Owner | When |
|---|---|---|---|
| Seed | `npm run seed`: files in git → empty Supabase, idempotent, upserts by slug or key | Claude / owner | on demand |
| Export and reconciliation | `npm run export`: database changes → files; fails on lost or divergent changes | Claude, committed by owner | before every release and weekly |
| Database dump | A native dump (may contain numeric ids) | owner | weekly |
| Off-repo laptop copy | `npm run backup`: data, media and the dump in a dated folder, no keys | owner | weekly |
| Restore drill | Seed an empty local Supabase, export again, diff against the files, check key relationships | Claude | before launch and each quarter |
| Environments and secrets | Separate local, staging and production projects; keys in environment variables; recovery procedure for a paused project | owner | before staging goes live |

- [ ] Converter and editorial review queue (papers and blogs, `FeedEntry` states, tag and relation review).
- [ ] Router library and route-level code splitting.

### Phase 4: Reach and virality

- [ ] Per-page titles, descriptions and Open Graph / Twitter cards with the story's lead art, built on the rendering choice
      made in Phase 1.
- [ ] Share buttons on stories and snacks that produce those previews.
- [ ] Sitemap, `robots.txt`, canonical URLs, structured data for articles.
- [ ] Mobile design pass on the canvas, then build it.
- [ ] Use the cover `hook` somewhere approved on the canvas, or remove it.
- [ ] Newsletter with a real provider, double opt-in and unsubscribe.

### Phase 4.5: Pre-launch hardening (gate before Phase 5)

Runs once v1 is reached: every page reads from Supabase through the static-build path, no `sample` content ships, and the app is
ready to host. These were originally in Phase 1 and were moved here by decision 39 so they don't slow pre-v1 iteration.

- [ ] Unit tests (Vitest) for the library helpers, search, routes and the data validator.
- [ ] End-to-end smoke tests (Playwright): every route loads at 1440px and 375px with no console errors and no
      horizontal scroll; old links redirect.
- [ ] Automated accessibility checks (axe) on every page, plus one manual screen-reader pass.
- [ ] CI on every pull request: data check, typecheck, lint, tests, build. Block merging on failure.
- [ ] When the policy migration exists: row-level security policy tests (only if a runtime feature needs RLS).

### Phase 5: Launch readiness

- [ ] Hosting with the SPA fallback, HTTPS, a custom domain, and security headers (CSP that allows inlined SVG styles).
- [ ] Error tracking, privacy-friendly analytics, uptime checks.
- [ ] Performance budget: fast first load on a mid-range phone; lazy-load below-the-fold art.
- [ ] Legal: trademark check for the name, privacy policy, terms, cookie consent if analytics need it, and a
      per-source copyright check (we use our own words and drawings; record each paper's licence).
- [ ] Editorial: a corrections policy, a contact address, and an "About how we label claims" page.
- [ ] Final review on the canvas and a launch checklist sign-off by the owner.

## 4. Known gaps kept on purpose until launch

These are visual-prototype scaffolding, not defects: unverified relations visible on the family tree and map, hard-coded
sample wording on company pages ("Sample page", `[year]`), "Out next Friday" with no schedule data, and all sample
stories, issues and companies. Each becomes a launch gate in Phase 2.

## 5. Decisions waiting on the owner

- Media host: Supabase Storage or S3 behind a CDN (CORS needed either way).
- Which Supabase project is production editorial state, and when the project counts as operationally critical (decision 37).

## Fixed

- B1 "this week" on every back issue: the back-issues row was replaced by one "This week's edition" band (decision 32).
- B2 wrong "Next" link on edition pages: it now links to the real next edition, and only the newest edition says "Out next Friday".
- B4 hard ink shadows on story pages, the search box and snack art: replaced by the same hairline outlines as the tiles (canvas option A, approved). Dead bento and hooked-cover CSS removed at the same time.
- B3 latest, previous and next depended on file order: they now come from volume and issue number (`issuesInOrder` in `src/lib/library.ts`).
- Shared claim label: fact cards, the feed and evidence cards use one `Stamp` with the source trust (`fd67461`, decision 18).
- Unique React keys on front-page snacks (keyed by moment link, not local id) and on map filter chips (`fd67461`).
- "Swipe this issue" is now "Swipe all snacks"; the feed is not filtered to the edition (`fd67461`, decision 32).
- Area facet parents: `area/physics` and `area/biology` added, with biophysics and physics education under physics and evolutionary biology under biology (`fd67461`).
- Claim label wording fixed (`048ad1d`).
- `src/lib/front.ts` renamed to `src/lib/feed.ts` (`fd67461`).
