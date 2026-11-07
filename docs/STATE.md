# Current state

A one-page snapshot so any agent (or person) can orient fast without re-reading every doc.
Update it when direction changes or a milestone lands. Longer context lives in `AGENTS.md`,
`docs/decisions.md` and `docs/production-plan.md`.

## Where we are

- Everything through PR #9 (the Supabase plan) is merged into `main`. No feature branch open.
- `main` is at `fba4323`. Work continues on `v1` (decision 40), many commits ahead.
- **Phase 3b landed in code on `v1` (decision 49):** the normalized V1 schema is in SQL migrations (core, editorial, public views and RLS, applied in filename order after the init migration). The `v_*` views expose only live, non-sample, approved or verified rows to anon. The importer writes one version and its extracted rows in one `pg` transaction. Migration history is one path: `npm run apply:migration` (see `supabase/README.md`). Acceptance (applying A, B and D to the owner's project, importing the three real stories, orphan audit, leak check) is the lead's run and is not recorded as done here yet.
- **Supabase-only runtime landed (decision 51):** every frontend read goes through Supabase views. File mode is gone (`VITE_DATA_SOURCE` removed, `src/data/source-file.ts` deleted). `data/seed/` holds the editorial seed (no sample content); `public/data/` is empty. The prerender walker enumerates routes from `v_live_story` / `v_issue` / `v_company` at build time via a Node Supabase client reading the publishable key. The new migration `20261107120000_runtime_cutover.sql` adds `v_site` + `site_settings`, `tag.parent`, `facet.description`, `node.blurb`/`short`, `relation.cited`/`cross_field`, and normalizes the `v_issue` grant regression.
- **Hydration and in-app navigation landed (decision 50):** `hydrateRoot` with an embedded snapshot per route; `npm run check:hydration` is the smoke gate; in-app navigation uses the approved slide-up (Phase 4 UX).
- Last decisions: 42 publish atomicity (refines 38) · 43 claim + trust on moments · 44 trust on every sourced claim · 45 createRoot not hydrateRoot (clarifies 41) · 46 story `schemaVersion: 2` · 47 single-stamp comic model (reclassify + rewrite; per-panel rejected) · 48 runtime Supabase reads, RLS required (refines 34) · 49 normalized V1 schema, transactional extraction, one migration path · 50 hydrateRoot with embedded data (supersedes 45 for prerendered routes) · 51 Supabase-only runtime (supersedes 48; file mode removed, samples stripped from the seed and from the DB references).

## Real content

- `attention-is-all-you-need` (peer-reviewed paper): first story, reference for tone and style.
- `size-shapes-life` (arXiv 2408.04070, preprint): front-page lead; fact-check in `docs/fact-checks/size-shapes-life.md`.
- `h3-hexagons` (Uber Engineering blog, company-reported): first real engineering post; company page at `/companies/uber`; fact-check in `docs/fact-checks/h3-hexagons.md`.
- Fact-check records for all three real stories now exist under `docs/fact-checks/` (attention-is-all-you-need.md added 2026-11-05: 47 rows, 39 pass).
- Sample stories, companies, storylines, nodes and relations were stripped from `data/seed/library.json` on 2026-11-07 and no longer appear in the DB-driven site (decision 51). Only the three real stories render.

## Built

Data-driven React site: front page D, story pages (five tabs, comic strips, family tree, tag shelf),
issue, company and map pages (with list view), swipe feed (`?feed`), search with tag filters.
Path URLs (`/papers/<slug>`). Reduced motion respected; pause switch per section.

## Runtime data: what's live, what's static

**Every frontend read comes from Supabase (decision 51).** On app mount, `src/data/load.ts` does one `Promise.all` of view fetches that assemble the in-memory Archive:

- Site metadata → `v_site`
- Tag vocabulary → `v_tag` + `v_facet`
- Story documents + library entries → `v_live_story`, `v_live_library_entry`
- Moments (home discovery, feed, search) → `v_live_moment`
- Library shell → `v_field`, `v_volume`, `v_issue` + `v_issue_story`, `v_company` + `v_company_post` + `v_company_built_on`, `v_storyline` + `v_storyline_step`, `v_node`, `v_relation`, `v_front_placement`

Search runs client-side against the loaded Archive (the prebuilt `search-index.json` was deleted — `scripts/build-index.ts` is gone). `/papers/:slug` is a single dynamic route; the client fetches the story from `v_live_story_by_slug` on mount.

The prerender script (`npm run prerender`) enumerates routes from `v_live_story` / `v_issue` / `v_company` at build time using a Node Supabase client (`--env-file=.env`), writes 10 routes today (home · 3 real papers · 2 issues + `/issues` · 1 company + `/companies` · `/map`), and inlines the per-route snapshot. 27-route baseline is gone with the samples.

Still file-backed (not read at runtime):
- `data/seed/*.json`: the editorial seed consumed by `scripts/seed-editorial-from-library.ts` and `scripts/publish-to-supabase.ts`. Sample content was stripped on 2026-11-07.
- Media under `public/media/<slug>/`: moving to Supabase Storage in a later batch.

## Next

Follow `docs/production-plan.md` (the only maintained launch sequence). Order:

1. **Supabase-only runtime landed (decision 51).** Frontend reads come entirely from views; file mode removed; samples stripped from the seed and DB references; prerender enumerates from the DB (10 routes today). `tsc`, `lint`, `build`, `prerender`, `check:prerender` and `check:hydration` all pass.
2. **More real stories** — 3 landed (`attention-is-all-you-need`, `size-shapes-life`, `h3-hexagons`). Target: 3–5 more papers and a second company post, so Home, Issues, Companies and Map fill out without placeholder content.
3. **Media to Supabase Storage** (deferred to a separate batch): bucket + upload CLI, `VITE_MEDIA_BASE_URL` cutover. Media still served from `public/media/`.
4. **Seed + export reconciliation / backup restore** (pre-launch gate, decisions 35, 37, 38): scripts, restore drill, backup location.
5. **Phase 4.5 (pre-launch gate):** Vitest + Playwright + axe + CI, once v1 is reached (DB-backed, hosted, media on CDN).

## Pre-launch gates (not started)

- **Seed and export reconciliation (decisions 35, 37):** `npm run seed` and `npm run export` must exist, and every release runs the export
  against the files. It fails on lost or divergent changes. A restore drill (seed an empty Supabase, export, diff against the files) must pass
  before launch. Details: production plan, Phase 3 backup table.
- **Publish atomicity (decision 38):** a story version goes live in one transaction or not at all. See `docs/data-model.md`.

## Known gaps kept on purpose (do not "fix")

- **Family tree / explore map** are demo content. The current nodes and links are placeholders
  so the layout can be reviewed. Don't invent, reshuffle or "verify" links to fill the tree.
  The pages carry a "Mockup · links to be fact-checked" badge and `src/components/FamilyTree.tsx`
  carries a DEMO CONTENT banner at the top. We will properly build the screen once there are
  enough verified relations (see decisions 15, 24; production plan section 4).
- Short lists on Home, Issues, Companies and Map until more real stories land. Decision 51 removed samples from the DB; sparse slots are expected, and components render empty states rather than placeholders.

## Build flags

- `VITE_HIDE_SAMPLES=1 npm run build` hides all sample content for production. `src/data/load.ts` drops every
  `sample: true` story, issue, storyline, company, node and relation at load time, and removes any reference to a
  dropped id (front page slots, topics, issue lists, company posts, node story links). Unset (the default), dev and
  the sample-heavy design review look exactly as before. Components are not changed by the flag.

## Copy rule

Don't literally say "kid-friendly" or "for kids" in user-facing copy (page text, blurbs, tag
descriptions, hooks). The USP is that anyone can follow it — show it with the plain language and
the illustrations; don't state it. Internal docs (`AGENTS.md`, `skills/`, decision log, commit
messages) may still describe the audience that way.

## Rules that bite most often

- Work on the long-lived **`v1`** branch (decision 40). Commit often, push often, no PR per change. The owner
  merges `v1` into `main` when they want to release. Never commit or push to `main`.
- Canvas before code for any new visual or layout.
- Illustration (invented numbers, stamped) vs evidence (real, cited, trust-labelled) are always visibly separate.
- Accessibility is an acceptance criterion per component, not a later pass.

## Model routing (to control cost)

Default to **Haiku** (or the cheapest capable model in whatever family) for mechanical steps:
builds, lints, git ops, data validation, tag inference (`prompts/tag-paper.md`), fact-check
lookups, JSON edits, PR descriptions. Reserve **Opus / Sonnet 5.5** (or equivalent large model)
for writing kid-level explanations, design decisions, and tricky debugging. Each `SKILL.md`
names its own default.
