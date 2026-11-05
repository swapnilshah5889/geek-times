# Current state

A one-page snapshot so any agent (or person) can orient fast without re-reading every doc.
Update it when direction changes or a milestone lands. Longer context lives in `AGENTS.md`,
`docs/decisions.md` and `docs/production-plan.md`.

## Where we are

- Everything through PR #9 (the Supabase plan) is merged into `main`. No feature branch open.
- `main` is at `fba4323`. Work continues on `v1` (decision 40), many commits ahead.
- Last decisions: 41 SSG prerender · 42 publish atomicity (refines 38) · 43 claim + trust on moments · 44 trust on every sourced claim · 45 createRoot not hydrateRoot (clarifies 41) · 46 story `schemaVersion: 2` · 47 single-stamp comic model (reclassify + rewrite; per-panel rejected).

## Real content

- `attention-is-all-you-need` (peer-reviewed paper): first story, reference for tone and style.
- `size-shapes-life` (arXiv 2408.04070, preprint): front-page lead; fact-check in `docs/fact-checks/size-shapes-life.md`.
- `h3-hexagons` (Uber Engineering blog, company-reported): first real engineering post; company page at `/companies/uber`; fact-check in `docs/fact-checks/h3-hexagons.md`.
- Everything else in `public/data/library.json` is `sample: true` (three placeholder companies now explicitly flagged).

## Built

Data-driven React site: front page D, story pages (five tabs, comic strips, family tree, tag shelf),
issue, company and map pages (with list view), swipe feed (`?feed`), search with tag filters.
Path URLs (`/papers/<slug>`). Reduced motion respected; pause switch per section.

## Next

Follow `docs/production-plan.md` (the only maintained launch sequence). Order:

1. **Fix now and Phase 0:** mostly landed on `v1` (see "Fixed" in the production plan). Still open: parents for the other new tags.
2. **Phase 1, rendering (landed, decision 41):** `npm run build && npm run prerender` writes all 27 routes in the default build (home, papers, samples, issues, companies, map) from one list, `scripts/prerender-routes.ts`. `npm run check:prerender` fails if any route lacks a page-specific title, description, `og:title`, `og:description` or `og:type`. Every page type uses `useHead`. `?feed`, `?search` and `?paper=` stay deferred (they share `/`). **Deferred:** client hydration (so readers don't see a loading flash) and Vercel build wiring (the prerender still runs by hand). Preview deploy: https://the-geeky-times.vercel.app/ (tracks `main`; the `vercel.json` SPA rewrite goes live when `v1` merges). Tests, CI and axe stay **deferred to pre-launch** (decision 39).
3. **Phase 2:** the first company engineering post has landed (H3, `h3-hexagons`, with the blog data contract and decision 43's claim and trust labels). Still open: 3–5 more papers to replace samples, plus the rest of the Phase 2 list in the production plan.
4. **Phase 3:** Supabase migrations, import job with orphan checks and transactional publish, media on a CDN with CORS.
5. **Phase 4.5 (pre-launch gate):** Vitest + Playwright + axe + CI, once v1 is reached (DB-backed, no samples, hosted).

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
- Sample stories, companies and placeholders (`[Company name]`, `[Year]`) render on the live
  pages. That is deliberate for design review. Replacing them is Phase 2 work, not a bug.

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
