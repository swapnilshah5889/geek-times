# Production plan

Where The Geeky Times stands, what a review of the code found, and every step left before a public launch.
Written 2026-11-04 on `feature/convert-scaling-paper`; updated 2026-11-06 on `v1` (decisions 40, 48 and 49). Keep it current: tick items as they land and move findings into
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

Each phase ends in something the owner can see and approve. Phases 1–2 can overlap. Phase 3a (the Supabase runtime slice, decision 48) runs before more Phase 2 story work. Phase 5 needs everything.

### Fix now (from the Codex review; small, before Phase 1)

Landed on `v1` in `fd67461` (shared claim label, unique keys, "Swipe all snacks"). See "Fixed" at the end.

- [~] Family tree: kept as demo content by the owner's decision. The current nodes and links are placeholders for layout review; don't invent or reshuffle them. The real build lands with Phase 2 (verified relations). See `src/components/FamilyTree.tsx` banner and `docs/STATE.md` "Known gaps kept on purpose".

### Phase 0: Clean up what exists (small, do next)

- [x] Fix B1–B4 (B1 disappeared with the edition redesign; B4 approved on the canvas).
- [x] Area facet parents added (`area/physics`, `area/biology`, `fd67461`). Remaining tag-parent work moves to Phase 2: a parent is useful only when it expresses a real "is a kind of" link, so the ~60 new concept / technique / use / dataset / metric tags get parents as the papers that use them land, not in one checklist pass. Some should stay top-level in their facet.
- [ ] Redraw the data-model board for decision 30.
- [x] Dead CSS removed (old bento tiles, hooked cover); `front.ts` renamed to `feed.ts`.
- [x] `docs/roadmap.md` now points here: this file is the only maintained launch sequence.
- [ ] Redraw the data-model board again for decisions 34–37.

### Phase 1: Rendering + preview path

- [x] **Rendering decision and spike (decisions 36 and 41):** SSG by prerender postbuild. 27 routes prerender locally from one
      source of truth (`scripts/prerender-routes.ts`); `npm run check:prerender` fails if any route is missing a page-specific
      title, description, `og:title`, `og:description` or `og:type`. Every page type (`Home`, `Paper`, `Issue`, `Company`, `Map`,
      `Sample`) uses `useHead`. `/?feed`, `/?search` and the legacy `/?paper=<slug>` are explicitly deferred (query views share
      `/`; need distinct paths first). **Deferred to a later batch:** client hydration (`hydrateRoot` with embedded data, so
      readers don't see a loading flash), the Vercel build wiring, and the raster OG card.
- [x] Preview deploy per push so the owner can review on a real URL. Vercel at https://the-geeky-times.vercel.app/ (tracks `main`); `vercel.json` adds the SPA rewrite so `/papers/<slug>` and other deep links don't 404 on direct load once `v1` merges. Still unticked at Phase 5: HTTPS / custom domain / CSP.

> **Automated tests, CI and axe checks are deferred to the pre-launch gate (decision 39).** They aren't in Phase 1 while
> the app is pre-v1 (still showing demo tiles and reading JSON files) because they slow iteration. See the
> "Pre-launch hardening" section below, which runs right before Phase 5.

### Phase 3a: Supabase runtime slice (in flight, decision 48; before more Phase 2 stories)

Readers get the story document and the live library entry from Supabase for any published slug. Everything else stays
static (list under Phase 3, "Remaining static reads"). Row-level security is **required** for this slice, not deferred.
The slice ships with its RLS and its policy tests, not at the Phase 4.5 gate.

- [ ] Migration `supabase/migrations/<timestamp>_init_story_slice.sql`: `story` and `published_version` tables with no
      foreign key constraints (decisions 30 and 38), indexes, RLS on both tables (anon may `SELECT` `story`; anon may
      `SELECT` `published_version` only where `status = 'live'`), and `publish_version(version_id)` (security definer,
      granted to `service_role` only). `supabase/README.md` explains applying it; `npm run apply:migration` is the record of record (decision 49).
- [ ] `src/data/source.ts` boundary: `file` (default) or `supabase` by `VITE_DATA_SOURCE`. A Supabase error throws; no
      silent fallback to JSON. Adds `@supabase/supabase-js` as a dependency (check its current API before use).
- [ ] `scripts/publish-to-supabase.ts` (service-role key, server-side only): validates `schemaVersion: 2` and every
      reference, upserts `story` by slug, inserts a `staging` version, then calls `publish_version`. Prints the target
      hostname, never a key.
- [x] `.env.example` with names only; `.env` added to `.gitignore`.
- [ ] Proof, no rebuild: dev server with `VITE_DATA_SOURCE=supabase`; note the headline on `/` and
      `/papers/attention-is-all-you-need`; publish a changed headline; reload both. The new text shows with no
      `npm run build` and no redeploy. Open-tab live updates and cache invalidation are out of scope.

Phase 2 story production resumes after the proof passes.

### Phase 3b: Normalized V1 schema and public views (decision 49): landed in code

The story document stays one immutable jsonb per version. Its queryable parts and the editorial layer move into
normalized tables, and anon reads them only through `v_*` views. Contract: `docs/handoffs/v1-schema-contract.md`.

- [x] Core content tables (`20261106100000_core_content_schema.sql`, Agent A): sources, snapshots, story sources, citations,
      media assets, vocabulary (`facet`, `tag`), story tags, moments, facts. Extra metadata columns on `published_version`.
- [x] Editorial tables (`20261106100001_editorial_schema.sql`, Agent B): volumes, issues, companies, storylines, fields, nodes,
      relations and evidence, front placement, story fields. Every table has RLS on and no anon grant.
- [x] Public views, grants and `v_live_story_by_slug` (`20261106100002_public_views_rls.sql`, Agent D). Live, non-sample,
      approved or verified rows only. The init migration's policies on `story` and `published_version` are kept.
- [x] Transactional importer (`scripts/publish-to-supabase.ts`, Agent C): one `pg` transaction per publish, a staging version,
      extracted rows, the orphan audit, then `publish_version`. A failure rolls back and the old live version stays.
- [x] One migration path: `npm run apply:migration` is the record of record. The Supabase CLI is optional (`supabase/README.md`).
- [ ] Acceptance run by the lead: apply A, B and D to the owner's project; import the three real stories; orphan audits and
      leak checks return zero rows; `/` and `/papers/<slug>` checked at 1280px and 375px. Tick this, and the phase, after it passes.
- [ ] Browser loader moves from `published_version` to `v_live_story`. Not in this batch; the direct reads keep working meanwhile.

**Moved to the database:** story documents and live library entries (decision 48), moments, facts, story tags, citations,
media asset paths, story fields, the vocabulary (`facet`, `tag`), volumes, issues, companies, storylines, fields, graph nodes,
verified relations with evidence, and the front-placement row.

**Still file-backed:** the feed and search index (`search-index.json`), prerendered HTML, media files (`public/media/`, moving
to a CDN in batch 2), the `library.json` shell for anything the views do not cover yet, `tags.json` as the editorial seed,
and `site.json` (site name, papers list, `mediaBaseUrl`).

### Phase 2: Real content to replace samples

- [x] One real company engineering post: Uber Engineering, "H3: Uber's Hexagonal Hierarchical Spatial Index" (Isaac Brodsky, 2018-06-27). Slug `h3-hexagons`; real company `uber`; 5 facts all `model_design` (the post has no measured results); fact-check in `docs/fact-checks/h3-hexagons.md` (archive URL at `web/20261104162659`). Added the blog data contract (additive: `kind: 'paper' | 'blog'` + `blog` block); made `CompanyPage` sample wording conditional on `sample: true`; three placeholder companies now carry `sample: true`. Follow-up label-correctness pass (decision 43) carries `claim` + `trust` on every `Moment` and renders them through one shared `ClaimStamp` on the feed, front page, and story facts — so an H3 design fact says "From the post · model design · company-reported" and a Transformer measured result says "Measured result · peer-reviewed".
- [ ] Three to five more papers across fields, through `skills/convert-paper`, so every front-page section has real
      stories.
- [ ] Verify family-tree and map relations with citations (`RelationEvidence`); hide unverified links from readers.
- [ ] Real edition metadata: publish dates and at least two real past editions (no editor's note).
- [ ] A switch that hides everything marked `sample` in production builds; remove all `[placeholder]` text.
- [ ] Add parents for remaining new tags (concept / technique / use / dataset / metric) as paper conversions use them. Only
      where there is a real "is a kind of" relationship; some tags stay top-level in their facet. Moved here from Phase 0.
- [ ] Canonical route pass for the archive-style pages. Today `/issues` and `/companies` render the latest / first item,
      duplicating `/issues/<id>` and `/companies/<id>`. Either make them genuine archive lists (grid of covers / companies) or
      301 them to the canonical detail URL. The duplicate-title warnings from `npm run check:prerender` surface this.
      Options and a recommendation (Option A, pending canvas sign-off): `docs/handoffs/canonical-routes.md`.
- [~] Comic-strip provenance (decision 47): single-stamp model with reclassify + rewrite.
      - **Landed on H3 (`h3-hexagons`):** strips 1 and 2 reclassified to `model_design`; captions name the post for the
        sourced claims ("the post says squares have two distances", "the post says it splits into about seven smaller
        hexagons"); strip 3 stays `illustration` with the attribution dropped from p2; `coverPanel: 1` on strip 2 so the
        feed moment shows the "about seven" panel.
      - **Landed on size-shapes-life:** strip 1 ("Chop the cube") and chapter 2 ("Chop a cube") reclassified
        `model_design → illustration` because the 5× figure is our arithmetic on an invented scale (fact-check record
        already said "changed"). Fact card "5×" `claim` moves `model_design → illustration` for the same reason.
      - **Landed on Transformer (`attention-is-all-you-need`):** a 47-row fact-check ledger landed
        (`docs/fact-checks/attention-is-all-you-need.md`: 39 pass / 7 weakened / 1 rejected). Strips 2–6 reclassified to
        `model_design` after small caption rewrites that dropped the ledger's weakened / rejected phrases ("so no clue
        gets lost", "a little smarter", "it knows it's the animal with wings") and named the paper and section for the
        sourced claims (query / key §3.2.1, weighted sum of values §3.2.1, multi-head attention with 8 heads §3.2.2,
        6-layer encoder/decoder stack §3.1, feed-forward §3.3, masked self-attention §3.2.3). The Fledermaus etymology
        is marked as a language note, not from the paper. Strip 1 stays `illustration` because two framing panels
        ("computers only understand numbers", "words with similar meanings get similar codes") are background, not
        paper claims.
      - **Rejected: per-panel provenance** (decision 47): after the rewrites above no strip needs it.
      - **Also landed in this pass:** H3 strip 3 kept `illustration` after a two-option fork (the post does not
        describe ring-by-ring car search or state "six neighbors"); captions dropped the attribution. H3 strips 1 and 2
        now name the post's H3 section inline so a reader can find the source without a URL fragment. The
        H3 "about seven" is re-presented as arithmetic on the post's one-seventh area (the post never says "splits
        into seven"). Size-shapes "5×" fact card stripped of its paper source link to match its new `illustration`
        claim kind.

### Phase 3: Platform

- [ ] Content model v2 and migration (`docs/data-model.md`).
- [ ] **Supabase** projects: local, staging and production (decision 34). Schema per decision 30 as SQL migrations in
      `supabase/migrations/`, applied with `npm run apply:migration` (the Supabase CLI is optional). Keys only in environment variables.
- [x] Foreign keys: decided, none (decision 38). Tables join on `<thing>_id` primary-key columns; every `_id` column is indexed;
      nested reads use SQL views, database functions or server code, not the auto-generated REST embedding.
- [ ] Prerequisite schema before row-level security on the rest of the tables: relation `status` with evidence, and immutable
      published versions that own their derived rows (`published_version_id`). The Phase 3a slice needs neither (decision 48).
- [ ] RLS for the remaining tables and a paged runtime API: **only when a runtime feature needs them** (decisions 36 and 48).
      RLS for the story slice is required now (Phase 3a). The launch path is still static pages with a runtime story read.
- [ ] Import job from JSON into Supabase with the integrity checks, **required** because there are no foreign keys (decision 38):
      transactional publish, unique, check and not-null constraints, an orphan check before every publish, orphan monitoring
      with alerts, and tests that every import and export reference remaps. Publish rules: `docs/data-model.md`, "Publish and import atomicity".
- [ ] Media on a CDN with CORS (Supabase Storage or S3: decide); set `mediaBaseUrl` per environment.

**Later batches (each lands with its own proof, after Phase 3a):**

1. Seed and export reconciliation (`npm run seed`, `npm run export`) and the restore drill (see the backup table below).
2. Media on a CDN with CORS, covering `public/media/<slug>/`.
3. Migrate the remaining static reads, one batch each. Until a batch lands, the file stays the source:
   - Feed, search and home-page moments: `public/data/search-index.json`.
   - Issues, companies, map, front-page slots, storylines, nodes and relations: the `public/data/library.json` shell.
   - Tag vocabulary: `public/data/tags.json`.
   - Site name, papers list and `mediaBaseUrl`: `public/data/site.json`.
   - Prerendered HTML: build-time content. Decision 48 defers wiring live data into prerender to a later batch.
   - Media files under `public/media/`: covered by batch 2.

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
- [ ] RLS policy tests for every table with a policy. The story slice's tests land with Phase 3a; this gate covers the rest.

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
