# Production plan

Where The Geeky Times stands, what a review of the code found, and every step left before a public launch.
Written 2026-11-04 on `feature/convert-scaling-paper`. Keep it current: tick items as they land and move findings into
"Fixed" when they are resolved. Background: `AGENTS.md`, `docs/decisions.md`, `docs/roadmap.md`.

## 1. Review (2026-11-04)

Scope: everything on `main` plus this branch (the second story, the convert-paper runbook, approved tags, the key
decision). Checked by reading the code and by running the site at 1440px and 375px.

### Bugs to fix first

| # | Where | Problem | Fix |
|---|---|---|---|
| B4 | Story pages vs tiles | Tiles lost their shadows (canvas option A), but comic panels and fact cards on story pages still use the hard ink shadow. | Decide on the canvas whether story panels follow option A, then apply it. |

### Gaps against our own rules

- **Unverified graph shown to readers.** The roadmap said the family tree and map ship with *verified* relations only.
  They are built and labelled "to be fact-checked", but every link is still unreviewed.
- **Sample content would ship.** Eleven sample stories, sample companies, sample issues and placeholders such as
  `[Company name]` and `[publish date]` render on the live pages. Fine for design review; not for launch.
- **Data-model diagram is stale.** Board 6 on the canvas still shows `id` where decision 30 says `key`.
- **New tags have no hierarchy.** The 24 new tags dropped their cross-facet parents, so "Biophysics" isn't grouped under
  anything yet.
- **`hook` is unused.** Both stories carry a cover hook that no page shows.

### Engineering risks

- **No tests and no CI.** Only `npm run data`, `tsc`, `oxlint` and `vite build`, run by hand. Nothing stops a broken
  push from merging.
- **No share previews.** It is a client-rendered SPA with one generic `<title>` and no Open Graph tags. Links shared
  on social apps show no headline or picture, which hurts the virality goal most.
- **Hosting fallback.** Paths like `/papers/<slug>` need the host to serve `index.html`. Not configured anywhere yet.
- **Every page loads the whole archive** (site, tags, search index, library). Fine at 2 papers, slow at hundreds.
- **Media from another host.** SVGs are fetched and inlined; a CDN must send CORS headers or the art falls back to
  `<img>` and stops being pausable.
- **Dead code.** Old bento `.tile` styles in `edition.css` and the `front.ts` file name no longer match what they do.
- **Accessibility unverified.** Built to the rules (labels, focus rings, list view for the map), but never run through
  a screen reader or an automated checker. Focus outlines on SVG map nodes may not show in every browser.

### What is solid

- Content is data: stories, library, tags and media paths are JSON, validated on every build.
- Trust labelling is consistent (illustration / model design / measured result, plus source trust).
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

**Content and data**
- [x] Story 1: "One word, two worlds" (Attention Is All You Need, peer-reviewed).
- [x] Story 2: "Why a bigger deer breaks" (arXiv 2408.04070, preprint), with a fact-check record.
- [x] 83-tag vocabulary; `library.json` editorial layer; build-time validation of every reference.
- [x] Claim kinds on facts, and a model-design stamp.

**Process**
- [x] `skills/convert-paper` runbook plus explain, fact-check, tag, draw and publish skills.
- [x] Database plan: content model v2, Postgres auto-increment ids, slugs as public keys, no foreign key constraints.

## 3. Remaining steps to production

Each phase ends in something the owner can see and approve. Phases 1–2 can overlap; 3 needs 2; 5 needs everything.

### Phase 0: Clean up what exists (small, do next)

- [x] Fix B1–B3 (B1 disappeared with the edition redesign; B2 and B3 fixed in the next commit). B4 is on the canvas for a decision.
- [ ] Add parents for the new tags inside their own facets (for example `area/biophysics` under a new `area/physics`).
- [ ] Redraw the data-model board for decision 30.
- [ ] Remove dead CSS and rename `front.ts` to what it holds (feed order).
- [ ] Update `docs/roadmap.md` to match this plan.

### Phase 1: Quality gates

- [ ] Unit tests (Vitest) for the library helpers, search, routes and the data validator.
- [ ] End-to-end smoke tests (Playwright): every route loads at 1440px and 375px with no console errors and no
      horizontal scroll; old links redirect.
- [ ] Automated accessibility checks (axe) on every page, plus one manual screen-reader pass.
- [ ] CI on every pull request: data check, typecheck, lint, tests, build. Block merging on failure.
- [ ] Preview deploy per pull request so the owner can review on a real URL.

### Phase 2: Real content to replace samples

- [ ] One real company engineering post (tests company-reported labels and the company page).
- [ ] Three to five more papers across fields, through `skills/convert-paper`, so every front-page section has real
      stories.
- [ ] Verify family-tree and map relations with citations (`RelationEvidence`); hide unverified links from readers.
- [ ] Real edition metadata: publish dates and at least two real past editions (no editor's note).
- [ ] A switch that hides everything marked `sample` in production builds; remove all `[placeholder]` text.

### Phase 3: Platform

- [ ] Content model v2 and migration (`docs/data-model.md`).
- [ ] Postgres schema per decision 30; an import job from JSON; the orphan-check query on a schedule.
- [ ] An API that serves `PublishedVersion` documents and paged lists (front page, issues, search), so pages stop
      loading the whole archive.
- [ ] Media on S3 behind a CDN with CORS; set `mediaBaseUrl` per environment.
- [ ] Converter and editorial review queue (papers and blogs, `FeedEntry` states, tag and relation review).
- [ ] Router library and route-level code splitting.

### Phase 4: Reach and virality

- [ ] Per-page titles, descriptions and Open Graph / Twitter cards with the story's lead art (needs prerendering or
      server rendering of the head).
- [ ] Share buttons on stories and snacks that produce those previews.
- [ ] Sitemap, `robots.txt`, canonical URLs, structured data for articles.
- [ ] Mobile design pass on the canvas, then build it.
- [ ] Use the cover `hook` somewhere approved on the canvas, or remove it.
- [ ] Newsletter with a real provider, double opt-in and unsubscribe.

### Phase 5: Launch readiness

- [ ] Hosting with the SPA fallback, HTTPS, a custom domain, and security headers (CSP that allows inlined SVG styles).
- [ ] Error tracking, privacy-friendly analytics, uptime checks.
- [ ] Performance budget: fast first load on a mid-range phone; lazy-load below-the-fold art.
- [ ] Legal: trademark check for the name, privacy policy, terms, cookie consent if analytics need it, and a
      per-source copyright check (we use our own words and drawings; record each paper's licence).
- [ ] Editorial: a corrections policy, a contact address, and an "About how we label claims" page.
- [ ] Final review on the canvas and a launch checklist sign-off by the owner.

## Fixed

- B1 "this week" on every back issue: the back-issues row was replaced by one "This week's edition" band (decision 32).
- B2 wrong "Next" link on edition pages: it now links to the real next edition, and only the newest edition says "Out next Friday".
- B3 latest, previous and next depended on file order: they now come from volume and issue number (`issuesInOrder` in `src/lib/library.ts`).
