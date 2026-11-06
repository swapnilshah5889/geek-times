# Decisions

A running log of product and technical decisions, newest last. Don't rewrite old entries; add a new one that
supersedes them. Format: **what**, then **why**. Dates are when the decision was made.

## 2026-11-04

1. **Newspaper look with hand-drawn animated illustrations.** Cream newsprint, serif masthead, Courier labels,
   halftone dots, muted ink colours. Cartoon "word buddy" characters. Inline SVG + CSS keyframes; no video files.
   *Why:* the owner loved the first prototype; it feels trustworthy and playful at once.

2. **Illustration vs evidence are always visibly separate.** Invented numbers are stamped "Illustration · numbers
   invented". Real numbers sit in "Evidence from the paper" cards with links to the exact section.
   *Why:* explaining with simplified numbers must never be mistaken for real results.

3. **"How it works" is told as comic strips.** Six three-panel strips (number codes, ask around, blend it in, many
   lookers, six floors, no peeking). Each ends with "Grown-up words: …". This replaced an earlier step-through
   slideshow.
   *Why:* the owner wanted every technical idea shown with pictures a school kid can read, not text.

4. **The UI renders data.** Content is JSON (a database later); graphics are standalone files referenced by URL
   (a CDN/S3 later). Components stay generic and render typed blocks.
   *Why:* many papers are coming, and layouts will change without rewriting content.

5. **React + TypeScript + Vite.** *Why:* the owner's choice, for a maintainable, typed, fast frontend.

6. **Never push to `main`; always use feature branches and PRs.** *Why:* the owner's rule.

7. **Graphics are self-contained animated SVG files.** They are inlined into a shadow root at runtime (so the page can
   pause them), with an `<img>` fallback. GIF/WebP/MP4 are supported as media types too.
   *Why:* they can live on a CDN, stay sharp, are small, and work with reduced motion.

8. **Many tags per paper from a shared vocabulary.**
   - 13 facets: field, area, concept, technique, task, dataset, metric, use, impact, organization, author, venue,
     everyday.
   - Each tag has relevance 0–1 and a basis (paper with evidence link / background / editorial).
   - AI-suggested tags stay hidden until approved.

   *Why:* readers search by curiosity, and the AI converter infers tags.

9. **Site name: The Geeky Times.**
   - Alternatives considered: Paper Cuts, Big If True, ELI5 Times, Nerd Alert!, Mind Blown Daily, The Curious Times.
   - Paper Cuts was rejected: the "Academic Paper-Cuts" podcast already uses nearly the same concept and name, and
     papercuts.com has been taken since 1997.
   - A USPTO search found no "GEEKY TIMES" mark, and geekytimes.com looked unregistered on 2026-11-04 (not yet
     bought).
   - Neighbours to know about: thegeekytimes.com (an inactive Shopify page) and Geektime (an Israeli tech-news
     site).
   - Get legal clearance before spending on the brand.

10. **The front page is a landing page, separate from story pages.** Desktop is designed first, mobile next. Layout **D**
    was chosen:
    - Above the fold: a broadsheet (full masthead, lead story across 2/3, a column of stories with thin rules).
    - Below the fold: a soft bento of "Keep exploring" tiles (light border, rounded corners, gentle shadow, no hard
      ink offset).

    Rejected: magazine cover (C). Kept as references: pure broadsheet (A) and pure bento (B).

11. **Snack mode.** A full-screen, swipeable feed of bite-size "moments" (comic strips, chapters, facts), each
    deep-linking into the story. *Why:* the "TikTok for intellectuals" goal.

12. **Volumes and issues are the publishing rhythm, not the main navigation.**
    - A volume is a month of weekly issues (decision 33; originally a year).
    - An issue is a curated package of several stories (one lead, features, briefs, a "From the vault" classic), with
      a theme.
    - Discovery runs through topics, storylines, the graph and search.

    *Why:* issues create habit and shareable moments, but nobody searches by issue number.

13. **Publish continuously; curate in issues.** A story goes live as soon as it passes review (library, feed, graph,
    search). The weekly issue packages what went live plus vault picks.
    *Why:* the owner wants to publish fast, and the graph improves with volume.

14. **The old-paper backlog.**
    - Keep two dates: the source's original year, and our publish date.
    - Launch with "Volume 0" themed special editions.
    - After that, every issue gets 1–2 "From the vault" classics, plus occasional new special editions.

15. **A knowledge graph of related work.**
    - Nodes are sources, including important ones not explained yet (greyed out, "not explained yet").
    - Typed edges: builds on, improves on, uses the method of, puts into practice, disagrees with, same problem.
    - Each edge has strength, basis and evidence.
    - Edges come from citation APIs (OpenAlex, Semantic Scholar), AI classification and editors.
    - Reader views: a timeline-style family tree on each story, guided storylines ("How X evolved"), and an explore
      map.
    - Unexplained nodes with many links decide what to explain next.

16. **Sources are more than papers.** Company engineering blogs (Netflix, LinkedIn, Meta, Uber, …) are sources too:
    `source.type` = paper | blog | (later) talk, rfc, patent.
    - Trust levels: peer-reviewed / preprint / company-reported.
    - Blogs are followed through RSS and archived when published (Wayback) so evidence links survive edits.
    - Company pages use plain names, never logos.
    - Copyright: write our own explanations and drawings; short quotes only; respect robots.txt and terms; consider
      asking companies for permission; get legal advice before launch.

17. **Project knowledge lives in tool-neutral files.** `AGENTS.md`, `docs/`, `skills/` and `prompts/` are all plain
    markdown, so any model or person can resume the project. Nothing essential lives only in a vendor-specific folder.

## 2026-11-04 · after the first design review (Codex)

18. **Every claim gets a kind and its source gets a trust level.**
    - Kind of claim:
      - *Illustration · numbers invented*
      - *From the paper · model design*: how the system is built, e.g. 8 heads
      - *Measured result*: what an experiment found, e.g. 28.4 BLEU
    - Source trust: peer-reviewed / preprint / company-reported.

    Both are stored in the data and shown the same way everywhere: story panels, snacks, front-page cards, issue
    pages, search.

    *Why:* "Real result" was wrongly used for model settings, and invented numbers appeared on snack cards with no label.

19. **Plain-language labels.** Terms like peer-reviewed, company-reported, storyline and family tree get a one-line
    explanation the first time they appear.
    - Story tabs: The big idea · How it works · Family tree ("papers before and after this one") · Evidence ·
      Explore related ideas.

20. **One stable global navigation:** Front page · Explore (Topics, Storylines, Map) · Issues · Real world · Snacks
    · Search. Field names (AI, Biology…) live inside Explore and Topics, not the top bar.

21. **The front page launches with eight "Keep exploring" areas**, in this order:
    1. More from this issue
    2. Swipe the snacks
    3. Topics
    4. In the real world
    5. Numbers from the papers
    6. Storylines
    7. From the vault and On this day
    8. Back issues

    The newsletter comes after these. Grown-up words live inside stories and search for now. A section renders only
    when it has meaningful content.

22. **Stories stay typed documents; queryable parts are extracted into tables.** The published story is a versioned,
    typed JSON document (the discriminated block union), not generic recursive `Block`/`BlockItem` rows. Moments, facts,
    tags and media are extracted into their own tables for search, the front page and the feed. This supersedes the
    generic block tables in decision 4's database sketch.

23. **Schema additions:**
    - `Moment`
    - `IssueStory.role` gains `real_world`, plus a `presentation` field (full | brief | snack)
    - `FeedEntry` (the review queue for discovered blog posts)
    - `RelationEvidence[]` (several citations per relation, each reviewed)
    - `SourceSnapshot` (paper revisions, blog edits, archive copies)
    - structured facts (value, unit, metric, dataset, comparison)
    - richer `MediaAsset` (MIME type, duration, captions, reduced-motion fallback, rights)
    - `PublishedVersion.schemaVersion` and `PublishedVersion.contentHash`

24. **Accessibility is an acceptance criterion for every component**, not a later pass:
    - essential labels ≥12–13px
    - 44px tap targets
    - keyboard-operable rails with visible focus
    - the map always has an accessible list view and real controls
    - no horizontal overflow at phone width
    - reduced motion respected, and animations paused off-screen

25. **Prove generality early.** One real paper from another field and one real company engineering post become fixtures
    *before* building more pages, so the model isn't shaped only around the Transformer story.

26. **A paper's page lives at `/papers/<slug>`** (chosen by the owner, replacing the planned `/stories/:slug`).
    - Links are built only through `src/lib/routes.ts`, so they work at any page depth and under any deploy base.
    - `Moment.href` in the data is base-relative (`papers/<slug>#<anchor>`).
    - Old `?paper=<slug>` links redirect to the new path.
    - The host must serve `index.html` for unknown paths (SPA fallback); Vite's dev server already does.

27. **The front page grid has exactly one tile per paper.**
    - Comic panels, chapters and facts are bite-size *moments* of one paper; they appear in snack mode (`?feed`) and
      search, never as grid tiles that look like separate stories.
    - The page is a hero for the featured paper, the snacks tile, a topics tile, then one tile per other paper.
    - It is fine for the page to be short while there is only one paper.

28. **Every paper ships a cover `hook`.** The front-page tile is built to stop a scroll: flipping art with a shout on
    each frame, a sticker, one real-number badge, a one-line question in highlighter, and a verb-phrase button. It is
    data (`hook` in the paper JSON, validated by `scripts/build-index.ts`), written by the converter.
    - Virality comes from curiosity and clarity, not deception: every hook line must be true and answered by the
      issue (see `skills/explain-source`).
    - Motion obeys the same pause switch and reduced-motion setting as every other graphic.

29. **The front page is design D, built from data.** (Supersedes the grid rule in decision 27; the owner picked D and asked
    for it, and the pages around it, to be built.)
    - `public/data/library.json` is the editorial layer: stories, front-page picks, issues, companies, storylines and the
      idea graph (`nodes` + `relations`). Real papers still live in `papers/<slug>.json`.
    - Everything in the library that is not a converted paper has `sample: true`, is labelled "Sample" on screen, and
      links to a placeholder page with no findings. Samples hold the layout until real stories replace them.
    - New routes: `/issues[/<id>]`, `/companies[/<id>]`, `/map` (with a list view), plus a family tree on story pages.
    - `npm run data` checks that every library reference points at something that exists.
    - The cover `hook` (decision 28) stays in the data but the front page does not use it yet.

30. **Database keys: auto-increment `id`, our key under another name, no foreign key constraints.** (The owner's call.)
    - Every table's `id` is the Postgres auto-increment (`bigint identity`) and is what other tables store, as
      `<thing>_id` columns.
    - Readable keys keep their own columns: `Story.slug` stays the public key and the URL (`/papers/<slug>`; the
      title-based slugs were kept on purpose); `Tag.key`, `Moment.key`, `Facet.key`, `Source.arxivId`.
    - `_id` columns are indexed but have no `REFERENCES`. Integrity comes from the import validator, the app and a
      scheduled orphan check. Rows are retired by `status`, never deleted.
    - Why: imports, re-publishing and moving content between environments never fight constraint order, and ids stay
      meaningless and stable while slugs can be corrected.

31. **Issues and volumes are collections; stories carry none of our dates.** (The owner's call.)
    - A story is published on its own. An issue (and a volume, a month of issues) is a curated collection of stories
      that are already published, and the same story can appear in more than one.
    - So a story's data has no `issue` field, and story pages, snacks, search results and the feed never show an
      issue number, a volume or a date of ours. They show the desk and the source's own year ("Paper from 2017").
    - Issue membership lives only in `library.json` → `issues[].stories`. Our dates (`published`) live only on issues
      and volumes. The front page and issue pages may name the issue, because they *are* the issue.

32. **Editions are a quiet, hand-made extra, not the focus of the app.** (The owner's call; builds on 12 and 31.)
    - The owner assembles an issue by hand every week and a volume every month, to give readers a newspaper feel.
    - Stories are the product. The front page is not "the current issue": the lead says "Lead story", the masthead has
      no issue number, and the main row is "More top stories".
    - Where editions show: a small "Editions" link in the nav (after Snacks), a "Weekly edition →" link in the
      masthead's top-right corner, a "This week's edition" card in the front-page sidebar, one slim band near the
      bottom, and "Editions / Past editions" links in the footer. The old row of back-issue covers is gone.
    - Issue pages don't promise an editor's note or any other text we haven't written. They show the cover, the
      contents with roles, the story cards and previous/next.

33. **A volume is a month.** (The owner's call, confirming 32.)
    - Volumes are monthly groupings of the weekly issues: Volume 1 is November 2026, the launch month. Volume 0 stays the
      launch special editions. Issue numbers keep counting up across volumes (001, 002 …).
    - Volumes are records in `library.json` → `volumes` (`id`, `title`, `kind`); each issue names its volume by id, and
      `npm run data` rejects an issue with an unknown volume.
    - Volume numbers are plain digits, not Roman numerals.

34. **The database is Supabase (managed Postgres).** (The owner's call.)
    - Postgres stays the data model of record (decision 30 and `docs/data-model.md`). Supabase adds hosting, backups,
      row-level security, auto-generated REST access and optional file storage.
    - Rules that follow from it:
      - Schema changes are SQL migrations kept in the repo (`supabase/migrations/`), applied by the Supabase CLI to a
        local, a staging and a production project. Nothing is edited by hand in the dashboard.
      - Readers use only the public (anon) key, and row-level security lets them see only published stories, approved
        tags and verified relations. The service-role key lives only in the import job and server code, never in the
        browser or the repo.
      - JSON files stay the source of truth until the import job exists; the import job writes to Supabase.
    - To decide before building: whether media lives in Supabase Storage or S3 behind a CDN (it needs CORS either way),
      and whether pages read from Supabase at build time (prerendering) or at run time.
    - Flag for decision 30: Supabase's auto-generated REST API finds relationships through foreign key constraints.
      Without them, nested queries ("a story with its tags") need views or database functions instead.

35. **The files in git are the full backup and the seed for the database.** (The owner's call.)
    - Everything needed to rebuild the database lives in the repo and on the owner's laptop: stories, the library, tags,
      site settings and all media. If the Supabase project is lost, paused for good or corrupted, an empty project is
      brought back by running the seed job (`npm run seed`, to be built in the platform phase).
    - The seed job is idempotent: it validates the files, then upserts by `slug` / `key`, never by numeric id, so it can be
      re-run safely. Postgres assigns fresh auto-increment ids each time, so **nothing outside the database may store a
      numeric id** (URLs, the newsletter list, analytics and exports use the slug or key).
    - Once editors approve tags or verify relations inside the database, the files fall behind. So the reverse job
      (`npm run export`) writes those changes back to the files, and it runs on a schedule and before any risky
      change. The export is committed to git; until it has run, the database may hold newer review decisions than the files.
    - Besides GitHub, keep a dated off-repo copy on the laptop (`npm run backup`: data, media and a database dump,
      with no keys inside). A restore drill (seed an empty local Supabase and compare row counts) must pass before launch.

36. **The launch data path is: editor / import → Supabase → build-time render → static host.** (From the Codex review.)
    - Readers get prerendered static pages and never query the database. So the public-reader row-level security policies and
      a paged runtime API are **not** on the launch path. They become work only when a runtime feature needs them (for
      example live search or accounts), and then they are listed as their own item.
    - Supabase is the back office: the import job, the review queue and editing. Search at launch is a static index.
    - The rendering choice (static generation, edge prerendering or server rendering) is made in Phase 1 with one
      representative story preview, before any platform API work. Phase 4 builds metadata, cards and the sitemap on it.

37. **Backup guarantees, and what counts as a restore.** (From the Codex review; refines 35.)
    - **Export is a required, checked release step.** Before every release the export runs and is compared with the tracked
      files. If it would lose a database-side change, or if the same record changed differently in the database and in
      the files, the release **fails**. Divergence is never overwritten silently; a person resolves it.
    - **A restore drill compares content, not only counts:** after seeding an empty local Supabase, export again and diff
      against the files, and check key relationships (a story's tags, a relation's two ends, an edition's stories).
    - **Numeric ids:** they must not be used as external identifiers or relied on across re-seeds. Database-native dumps,
      migration records and audit logs may hold them as internal references. The seed and the portable export resolve
      records by slug or key and remap references on import.
    - **When to pay for Supabase Pro:** when the project becomes operationally critical, meaning the first time anything
      the owner cares about exists only there (review decisions not yet exported, or editorial work that depends on it
      being awake), not only when user data arrives. Before that point there must be a tested backup path and a written
      recovery procedure for a paused project.
    - **Authoritative state:** until the export has run, the database is authoritative for review decisions; after it, the
      committed files are. The owner decides which project is production editorial state.

38. **Final: no foreign key constraints; relate rows by joining on the primary keys.** (The owner's call, after the Codex
    review argued for foreign keys. Confirms decision 30.)
    - Tables relate through plain `<thing>_id bigint` columns that hold the other row's `id`. Queries join on those columns.
      There is no `REFERENCES` or other database-level foreign key.
    - The replacement controls are now **required**, not optional: transactional import and publish, unique, check and
      not-null constraints, an orphan check before every publish, orphan monitoring with alerts, and tests proving that
      every import and export reference remaps correctly.
    - Because Supabase's auto-generated REST API can't infer relationships without foreign keys, nested reads (a story with
      its tags) use SQL views or database functions, or are assembled in server code. Indexes on every `_id` column are
      mandatory so the joins stay fast.

## 2026-11-05

39. **Defer tests, CI and axe to the pre-launch gate.** (The owner's call.)
    - Until v1 — every page reads from Supabase through the static-build path, no `sample` content ships, and the app is ready
      to host — we don't invest in Vitest, Playwright, axe or a CI pipeline. Daily checks remain the manual ones: `npm run data`,
      `npm run build`, `npm run lint` and a look at 1280px and 375px.
    - Why: the app is still changing shape fast, with demo tiles and a JSON data layer that will be rewritten against the
      database. Tests written now would be rewritten with the rendering choice and the data path; they would slow iteration
      without catching the kind of regressions that matter at this stage.
    - Pre-launch, once v1 is reached, run everything in Phase 4.5 of `docs/production-plan.md` as a single hardening gate:
      unit tests, smoke tests, axe, CI blocking merges, and RLS policy tests if RLS has landed.
    - **Rendering decision and preview deploys stay in Phase 1,** because the rendering choice shapes everything downstream
      (OG cards, hosting, Phase 3 import job) and preview deploys speed up — rather than slow down — review.

40. **One long-lived `v1` branch, no PR per change.** (The owner's call.)
    - All day-to-day work commits to `v1` and is pushed there. No per-topic feature branches, no PR per change: the review and
      merge overhead was slowing the pre-v1 iteration more than it was catching mistakes. `main` stays protected: never commit
      or push to it. The owner merges `v1` into `main` when they want to release.
    - Agents stop running `git switch -c feature/...` and stop asking for a branch name, unless the owner explicitly asks for
      another branch for an experiment or a risky change.
    - This is a pre-v1 choice. When v1 is reached (DB-backed, no `sample` content, hosted), the pre-launch gate (Phase 4.5)
      lands, and from the first production release onward we go back to per-feature branches and PRs with CI as that gate.

40 added above; continuing on 2026-11-05.

41. **Rendering: static generation (SSG) by a prerender step after `vite build`; Next.js migration later.** (The owner's call.)
    - Pre-v1: a prerender script (`npm run prerender`) run after `npm run build` visits every known route with a
      headless browser and writes the rendered HTML into `dist/<route>/index.html`. It is NOT chained into `npm run
      build` yet; the Vercel build wiring is a separate deferred item. The React SPA hydrates on top. Smallest change
      to the current Vite + React 19 stack; validates the SSG path (decision 36) end to end.
    - Pages must carry per-page `<title>`, meta description and Open Graph / Twitter tags so the SEO and share-preview
      goals (Phase 4) are met on the prerendered HTML.
    - Long term: migrate to Next.js once the spike validates traffic and we want file-based routing, ISR and the
      framework's built-in SEO tooling. The spike's route-list script carries over as the migration's smoke test.

42. **Publish is atomic per story version.** (From the 2026-11-05 Codex review; refines decision 38.)
    - **The unit:** one `PublishedVersion` together with every derived row it owns — the extracted `Moment`, `Fact`,
      `StoryTag` rows, and any `Relation` / `RelationEvidence` rows added or changed by this version. Media and
      source records are referenced, not re-owned.
    - **Staging and promote:** import writes the version document and its derived rows to staging keyed by
      `published_version_id`. The orphan check runs across the staging rows (every `_id` resolves to a non-retired
      row, no duplicate `Moment.key` within the version, every media and source reference resolves, every tag is
      approved). Promotion then flips `PublishedVersion.status` to `live` and updates `Story.liveVersion` inside one
      transaction.
    - **Failure:** staging rows are discarded; the previous live `PublishedVersion` stays authoritative; the owner
      sees a reconciliation diff.
    - **Reference remap on import:** references come across as `slug` or `key`, never numeric id (decisions 35 and 37).
      The import step resolves them to the new ids on this database. Remap is tested as part of decision 38's required
      controls.
    - Full shape in `docs/data-model.md` → "Publish and import atomicity".

43. **Claim and trust travel with moments; one shared renderer for every claim label.** (From the 2026-11-05 Codex label-correctness review; builds on decision 18 and decision 42.)
    - `scripts/build-index.ts` no longer hard-codes `provenance: 'evidence'` on fact moments. Each `Moment` now carries
      `claim: ClaimKind` (illustration | model_design | measured_result) and `trust?: 'peer_reviewed' | 'preprint' |
      'company_reported'`, both read from the story's data. Old clients ignore the new optional fields, so
      `schemaVersion` stays at 1.
    - `src/lib/claimLabel.ts` is the single source of wording: `claimLabel(claim, trust, sourceKind)` returns
      "Illustration · numbers invented", "From the paper · model design" / "From the post · model design · company-reported",
      or "Measured result · <trust>". `ClaimStamp` in `src/components/common.tsx` renders it, reading the source's kind
      from `SourceKindContext` (provided by the story page).
    - This replaces the inlined `CLAIM_LABEL` constants and the `trustLabel(...).split(' ')[0].toLowerCase()`
      lookups that had crept into `HomePage.tsx`; feed, front-page snacks, front-page number cards and story facts
      all now read the same rules. "Company-reported" describes the SOURCE, never a model design turned into a
      measurement.

44. **Every sourced claim carries source trust; illustrations stay bare.** (From the 2026-11-05 Codex label closeout; tightens decision 43.)
    - Trust describes the source's publication status; claim kind describes the assertion. They are independent, and
      both appear on every sourced claim. The shared `claimLabel` now renders:
      - `illustration` → `Illustration · numbers invented` (no source, no trust).
      - `model_design` + paper + trust → `From the paper · model design · peer-reviewed` (or · preprint).
      - `model_design` + blog + trust → `From the post · model design · company-reported`.
      - `measured_result` + trust → `Measured result · <trust>`.
    - Every fact now requires an explicit `claim` on its JSON row; `scripts/build-index.ts` rejects a missing claim
      with a per-fact error. The old silent fallback ("sourced with no claim = model_design") is gone; it had let
      the feed label a fact "From the paper · model design" while the story-page `FactsBlock` rendered no stamp.
    - "Company-reported" names the source. It does NOT mean the company measured something itself; a company-reported
      claim may still be design, a worked example, or a measurement, depending on the fact's `claim` kind.

45. **Correction to 41: the SPA replaces the prerendered DOM; it does not hydrate.** (Supersedes one sentence of 41 only.)
    - Entry 41 says "The React SPA hydrates on top" of the prerendered HTML. That is wrong. `src/main.tsx` calls
      `createRoot(...).render(...)`, not `hydrateRoot`, so on mount React clears the prerendered markup and renders the
      page again. The rest of 41 stands as written.
    - Consequences: crawlers index the prerendered HTML. Readers see that HTML until the script runs, then React replaces
      it, which can show a flash. The production plan already lists this under deferred client hydration.
    - Proper hydration (`hydrateRoot`, with the data embedded so the existing markup can be reused) stays deferred to a
      later batch (`docs/production-plan.md`, Phase 1).
    - *Why a new entry and not a note inside 41:* the log is append-only, so the original wording stays on record and this
      entry says what changed.

46. **Story documents bump to `schemaVersion: 2`.** (Required by decision 44 making `Fact.claim` mandatory.)
    - `src/types.ts` exports `STORY_SCHEMA_VERSION = 2`; `StoryDocBase.schemaVersion: typeof STORY_SCHEMA_VERSION`.
    - `src/data/load.ts` rejects any story document at another version with a clear error:
      `"story <slug> is at schemaVersion 1; required version is 2. Migrate the file to schemaVersion 2 (every fact needs a claim) or re-export it from the editor."`
    - The three real stories (`attention-is-all-you-need`, `size-shapes-life`, `h3-hexagons`) were migrated one-line (every fact already carried an explicit `claim`).
    - Site, tags, library and search-index versions stay at 1 — their contracts did not break.

47. **Comic claim stamps: single-stamp model with reclassify + rewrite.** (From the 2026-11-05 Codex comic audit; closes the open content-model question raised in Phase 2.)
    - A comic strip carries one `provenance` stamp. When a strip's drawing is schematic (illustration) but one or more of its panels state a claim lifted from the source, the strip's provenance moves to `model_design` and the panel captions explicitly name the source ("the post says …", "the paper's name for this is …"). The drawing stays schematic; the caption carries the honesty.
    - A strip reclassifies to `model_design` only once a fact-check row records every claim it names. Without the row, the strip stays `illustration` AND the attributing wording is removed from the caption, so the comic never attributes an unrecorded claim to the source.
    - **Rejected: per-panel provenance.** It would give exact labels but requires a content-model change (types + validator + `ComicBlock` renderer + every story file + search-index moments). After rewriting every strip across the three real stories, no strip needs it.
    - Applied in this batch: H3 strips 1 and 2 reclassified to `model_design` with the caption-attribution rewrite; strip 3 stays `illustration` with the attribution dropped; `coverPanel: 1` on strip 2 so the feed moment shows the "about seven" panel. Size-shapes-life strip 1 ("Chop the cube") and chapter 2 ("Chop a cube") reclassified `model_design → illustration` because the 5× figure is our arithmetic on an invented scale (fact-check record already said so).
    - **Deferred, blocked on a new fact-check record for `attention-is-all-you-need`:** Transformer strips 4 and 5 carry the paper's own numbers (8 heads, 6 layers) but cannot reclassify yet. New Phase 2 item records this.

48. **Runtime Supabase reads for story documents + live library entries; the rest stays static for now.** (From the 2026-11-05 Codex Supabase runtime brief.)
    - **What moves to Supabase at runtime:** the story document (`PaperDoc`) and the live library entry fields
      (`LibraryStory`) for any story that has been published. Readers see a change on the next full page reload,
      without `npm run build` and without a redeploy. Open-tab live updates and cache invalidation are out of scope.
    - **What stays static for this batch:** `tags.json`, the `library.json` shell (front-page layout slots, issues,
      companies, storylines, nodes, relations, map), `search-index.json` (feed, search, home-page moments),
      prerendered HTML, media files. Each one is called out in STATE.md so no one claims "the site is dynamic."
    - **Public read contract:** readers hit Supabase with the URL + publishable key only. Two reads:
      (1) `GET published_version WHERE story_slug = <slug> AND status = 'live'` returns `{document, library_entry}`;
      (2) `GET published_version WHERE status = 'live'` returns every live `{story_slug, library_entry}` pair, which
      the home page overlays on `library.json`'s shell before it renders cards.
    - **RLS is required, not deferred.** Readers have the publishable key in the browser, so row-level security is the
      only line between them and staging rows. `published_version` has RLS enabled with one SELECT policy
      (`status = 'live'`). `story` has SELECT allowed to anon; all writes are blocked for anon. Service-role keys
      stay server-side (seed/publish CLI only); nothing prefixed `VITE_` holds a secret key. This refines decision 34
      and supersedes the "RLS deferred" line in the production plan.
    - **Atomic publish (decision 42) in Supabase:** one SQL function `publish_version(version_id)` flips the current
      live row to `retired`, flips the new row to `live`, and updates `story.live_version_id` in one transaction. The
      seed/publish CLI (server-side, service-role key) stages a version, runs orphan checks on the staged document,
      then calls `publish_version`.
    - **Data-source boundary (`src/data/source.ts`):** a small typed layer in front of `loadEdition`/`loadLibrary` that
      chooses `file` or `supabase` by `VITE_DATA_SOURCE`. On a Supabase failure the loader surfaces an error — it never
      silently falls back to JSON. The explicit JSON mode stays for local comparison and the design-review flow.
    - **Decisions 36 and 41 stand as written.** They described the static build-time path. This entry is the runtime
      addition on top, not a rewrite. The prerendered HTML continues to carry build-time content until a later batch
      wires live data into prerender; readers see the live data as soon as React mounts.
    - **Env vars (names only, never values in git or chat):** `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`,
      `VITE_DATA_SOURCE` in the browser; `SUPABASE_SERVICE_ROLE_KEY` on the server for the publish CLI. `.env.example`
      lives in the repo with the names; `.env` is gitignored.

## 2026-11-06

49. **Normalized V1 schema: extracted tables read through views, transactional extraction, one migration path.** (From the Phase 3b schema contract, `docs/handoffs/v1-schema-contract.md`; builds on decisions 30, 34, 38, 42 and 48.)
    - **Shape.** A published story version stays one immutable `published_version.document` (jsonb, the `PaperDoc`). Its queryable parts move into version-owned tables with `published_version_id`: moments, facts, story tags, citations, media assets and field tags. Editorial data moves into tables too: volumes, issues, companies, storylines, fields, graph nodes, relations with their evidence, and one front-placement row. Every row is keyed by `slug` or `key`. Numeric ids stay internal, and references are plain `<thing>_id` columns with no foreign keys (decisions 30 and 38).
    - **Transactional extraction.** The importer (`scripts/publish-to-supabase.ts`) writes a `staging` version and all of its extracted rows in one `pg` transaction, runs the orphan audit on them, and then calls `publish_version`. Any failure rolls the whole transaction back, and the previous live version stays authoritative (decision 42).
    - **Public reads.** Anon reads only through views. Every view keeps `live`, non-sample, approved or verified rows. The raw tables get no anon grant. Two story views (`v_live_story`, `v_live_library_entry`) run as `security_invoker`, because they read only tables anon can already read. The other views run with owner rights, so their WHERE clauses are the gate. The init migration's policies on `story` and `published_version` stay in place, so the browser's current reads keep working until it moves to the views.
    - **One migration path.** `npm run apply:migration -- <file>` is the record of record. Files are applied in filename order, one transaction each: init, then A, B and D. The Supabase CLI (`db push`) is optional and only for owners who run `supabase link`. Those owners must insert the already-applied versions into `supabase_migrations.schema_migrations` first, or `db push` would try to run them again. The steps are in `supabase/README.md`.
    - **Still file-backed:** `site.json`, `tags.json` as the seed, `search-index.json`, prerendered HTML, media, and the `library.json` shell for front-page layout, issues, companies and the map. Runtime loaders for the new views are the next batch.

50. **Hydration via `hydrateRoot` with route-specific embedded data, superseding decision 45's `createRoot` choice for prerendered routes.** (From the 2026-11-06 Codex UX brief; fixes the flash from decision 41's prerender + 45's createRoot combination.)
    - **The rule.** `src/main.tsx` uses `hydrateRoot` for a route that has (a) prerendered HTML in `dist/<route>/index.html` AND (b) a `<script id="__initial_data__" type="application/json">` block for that route, whose `route` matches the current pathname and whose `schemaVersion` matches the compiled one. Any other case — missing snapshot, route mismatch, schema mismatch, or an unprerendered route (`?feed`, `?search`, legacy `?paper=`) — falls back to `createRoot`. This matches [React's hydration guidance](https://react.dev/reference/react-dom/client/hydrateRoot): hydration requires the first render to match the existing markup, so partial-hydration setups are refused.
    - **What the snapshot is.** The archive and, for a paper page, the edition — the same objects `loadArchive()` / `loadEdition()` return. On a prerendered load the loader reads the snapshot synchronously instead of fetching. The snapshot is for hydration only: it is not a cache that bypasses runtime reads. In Supabase mode the runtime read **still runs after hydration**, and if it comes back different the page updates in place. A failed live read surfaces a visible error, never a silent "old snapshot presented as current."
    - **Prerender writes the snapshot.** `scripts/prerender.ts` captures the data its headless render used (via a `window.__collect_initial_data__` hook the SPA sets while prerendering) and injects an escaped `<script id="__initial_data__" type="application/json">` into the HTML before saving. JSON is serialized with `</` replaced by `<\/` (per [OWASP JSON-in-HTML guidance](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)) so story text containing `</script>` cannot terminate the block. `U+2028` / `U+2029` are JSON-escaped too.
    - **Snapshot schema and validation.** The snapshot carries `{ schemaVersion: 1, route: string, archive: Archive, edition?: Edition }`. `scripts/check-prerender.ts` asserts the script exists, parses as JSON, matches the route the HTML was written to, matches the compiled schema version, and does not re-serialize obviously differently (DOM mismatch sentinel values).
    - **Hydration-mismatch audit.** All 27 prerendered routes go through a mismatch audit: anything whose render depends on `Date.now()`, animation progress, reduced-motion state, viewport state, or in-browser DOM interactions is wrapped in `suppressHydrationWarning` or moved inside `useEffect`. Lists captured in the prerender report.
    - **Navigation stays with the custom router.** `src/App.tsx` keeps its single `route` state and the switch over `App.routeFor(pathname+search)`. Agent C adds a `popstate` listener and exports a `navigate(url)` that updates `history.pushState` plus the route state, since `pushState` does not fire `popstate` on its own (per [MDN's History API guidance](https://developer.mozilla.org/en-US/docs/Web/API/History_API/Working_with_the_History_API)). Modified clicks (⌘/ctrl/shift/alt + click, middle-click, in-page hashes, anchors to other origins, `download`) stay native.
    - **Measured by filmstrip, not paint count.** Direct-load FCP + a 10-frame screenshot sequence across the prerender → hydration transition and the front → paper transition. Animated SVGs can trigger phantom paints; the honest signal is "what does the reader see." Numbers recorded in the closeout.

