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
