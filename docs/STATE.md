# Current state

A one-page snapshot so any agent (or person) can orient fast without re-reading every doc.
Update it when direction changes or a milestone lands. Longer context lives in `AGENTS.md`,
`docs/decisions.md` and `docs/production-plan.md`.

## Where we are

- Everything through PR #9 (the Supabase plan) is merged into `main`. No feature branch open.
- `main` is at `fba4323`. Work continues on `v1` (decision 40), many commits ahead.
- **Phase 3b landed in code on `v1` (decision 49):** the normalized V1 schema is in SQL migrations (core, editorial, public views and RLS, applied in filename order after the init migration). The `v_*` views expose only live, non-sample, approved or verified rows to anon. The importer writes one version and its extracted rows in one `pg` transaction. Migration history is one path: `npm run apply:migration` (see `supabase/README.md`). Acceptance (applying A, B and D to the owner's project, importing the three real stories, orphan audit, leak check) is the lead's run and is not recorded as done here yet.
- **Supabase-only runtime landed (decision 51):** every frontend data read goes through Supabase views. File mode is gone (`VITE_DATA_SOURCE` removed, `src/data/source-file.ts` deleted). `data/seed/` is the Git recovery/import copy; it still contains legacy demo graph records that must never render. `public/data/` is empty. The prerender walker enumerates routes from `v_live_story` / `v_issue` / `v_company` at build time via a Node Supabase client reading the publishable key.
- **Dynamic front page landed:** `src/data/load.ts` derives `lead`, `aside`, `more`, `topics` and `real` from live stories on mount; publishing a new paper surfaces it on the home page on the next load. Curated bits (storylines, vault, onThisDay) still come from `front_placement`.
- **On this day is intentionally empty** until a real, dated anniversary with a source is curated. The seed now stores `null`, and the UI hides absent or placeholder entries. Supabase still holds the old sample object; sync it to `null` only after all deployed clients accept the nullable value, since older clients dereference it directly.
- **Preview / live status gate landed (decision 52):** stories can be published as `preview` (visible only when `VITE_SHOW_PREVIEW=1` is set, i.e. local dev) and approved to `live` with `npm run approve -- <slug>`. The hosted site (no flag) only renders `live` rows. Migration `20261108120000_preview_status.sql` adds `v_preview_*` twin views, the `approve_version(slug)` RPC (service_role only), and the preview-status addition to the check constraint. `npm run status` lists every published_version row with its status.
- **Conversion pipeline is provider-neutral:** `scripts/convert/model.ts` supports Anthropic and OpenAI-compatible providers, with optional per-stage provider/model overrides for `convert`, `fact-check`, and `illustrate`. A non-arXiv paper URL requires explicit `--kind paper --trust ...`; ambiguous URLs never silently become paper sources. Einstein's 1905 story is now Supabase `live` version 15 with `journal_published` trust. The trust migration is applied. No paid provider API call has been made.
- **Hydration and in-app navigation landed (decision 50):** `hydrateRoot` with an embedded snapshot per route; `npm run check:hydration` is the smoke gate; in-app navigation uses the approved slide-up (Phase 4 UX).
- Last decisions: 44 trust on every sourced claim · 45 createRoot not hydrateRoot (clarifies 41) · 46 story `schemaVersion: 2` · 47 single-stamp comic model · 48 runtime Supabase reads, RLS required (refines 34) · 49 normalized V1 schema, transactional extraction, one migration path · 50 hydrateRoot with embedded data · 51 Supabase-only runtime (supersedes 48) · 52 preview/live status gate for publishes · 53 provider-neutral conversion and explicit paper URL classification · 54 journal-published trust without claiming external peer review.

## Real content

- `attention-is-all-you-need` (peer-reviewed paper): first story, reference for tone and style.
- `size-shapes-life` (arXiv 2408.04070, preprint): front-page lead; fact-check in `docs/fact-checks/size-shapes-life.md`.
- `h3-hexagons` (Uber Engineering blog, company-reported): first real engineering post; company page at `/companies/uber`; fact-check in `docs/fact-checks/h3-hexagons.md`.
- `resnet` (He et al., CVPR 2016 / arXiv 1512.03385, peer-reviewed): added 2026-11-07; fact-check 42 rows, 38 pass. CVPR 2016 venue still needs manual confirmation.
- `google-search` (Brin & Page, WWW7 1998, peer-reviewed): added 2026-11-07; fact-check 53 rows, 45 pass. WWW7 peer-review status needs manual confirmation.
- `dynamo` (DeCandia et al., SOSP 2007, peer-reviewed): added 2026-11-07; fact-check 36 rows, 29 pass. SOSP 2007 peer-review status needs manual confirmation.
- All 7 fact-check records live under `docs/fact-checks/`. Real hand-drawn art is in place for every live story (84 SVGs for `resnet`/`google-search`/`dynamo` landed in commit `86f75aa`, Nov 7). No placeholder art may be visible in V1.
- Seven real stories are live. The Git seed still contains legacy demo graph rows and a `[Company name]` graph entry; runtime views and page logic must keep these from appearing. Audit and clean the visible site before V1; do not treat a sample/demo badge as a substitute for removing fabricated data.

## Recent publication

- `einstein-special-relativity` (Einstein, 1905, `journal_published`): Supabase live version 15, 23 moments, 5 facts, 18 media assets, 2 approved tags. Verified in `v_live_story`; local development also reads it.

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

The prerender script (`npm run prerender`) enumerates routes from `v_live_story` / `v_issue` / `v_company` at build time using a Node Supabase client (`--env-file=.env`), writes 14 routes today (home · 7 stories · 2 issues + `/issues` · 1 company + `/companies` · `/map`), and inlines the per-route snapshot. Query-mode routes (`/?feed`, `/?search`) are client routes and are not separate prerender outputs. 27-route baseline is gone with the samples.

The embedded snapshot is serialized JSON in generated HTML for hydration. It is built from Supabase and is not a frontend read of `data/seed/*.json`; once the client starts, Supabase remains authoritative. The user's V1 requirement is cloud-hosted story/editorial data and media, with Git seed files retained only for import and recovery.

Still file-backed (not read at runtime):
- `data/seed/*.json`: the editorial seed consumed by `scripts/seed-editorial-from-library.ts` and `scripts/publish-to-supabase.ts`. Sample content was stripped on 2026-11-07.
- Media under `public/media/<slug>/`: moving to Supabase Storage in a later batch.

## Next

Follow the **V1 merge gate** in `docs/production-plan.md`. Current blockers/verification items are: remove all visible sample/demo/placeholder records, copy, dates and art; move `public/media/` assets to Supabase Storage and remove local runtime copies after backup verification; record target-project schema/RLS/data acceptance; prove publish → home/search/story URL without a site rebuild; complete a non-production export/restore reconciliation; verify Vercel environment/build/deep-link behavior; close the page-review heading and touch-target gaps; then run final gates. Do not merge `v1` into `main` until those checks have evidence and the owner chooses to release.

The browser review checked 17 route variants at 1280px and 375px with no site console errors or horizontal overflow. Remaining accessibility findings: home/feed/search need an `<h1>`; issue/company card headings skip a level; several mobile tap targets are under 44px.

## Deferred to next weekend (weekly-usage window)

- **Admin page, dev-only.** A `/admin` route (or similar) visible only when `VITE_SHOW_PREVIEW=1` (so it never ships to Vercel). Lists every story with slug, status, version, publish date; buttons to open in dev, approve preview → live, and eventually trigger the conversion pipeline for a new URL. Replaces today's CLI (`npm run status`, `npm run approve`) with a browser view.

## Pre-launch gates (not started)

- **Seed and export reconciliation (decisions 35, 37):** `npm run seed` and `npm run export` must exist, and every release runs the export
  against the files. It fails on lost or divergent changes. A restore drill (seed an empty Supabase, export, diff against the files) must pass
  before launch. Details: production plan, Phase 3 backup table.
- **Publish atomicity (decision 38):** a story version goes live in one transaction or not at all. See `docs/data-model.md`.

## Content visibility rule for V1

- No sample, mockup, unverified, or placeholder records, copy, dates, or art may appear on any route in local or live mode. Remove/hide demo map and family-tree records until their relations are verified. A clear empty state is acceptable; a demo badge is not a substitute for removing fabricated data.
- Short lists are acceptable when they contain only real records. On This Day should be absent or show an honest empty state until a real, dated anniversary with a source is curated; the old sample value in Supabase must not render.
- Original teaching illustrations may contain invented numbers only when visibly stamped `Illustration · numbers invented`.

## Build flags

- `VITE_HIDE_SAMPLES=1 npm run build` is a defense-in-depth filter, not the V1 content rule. V1 must show no sample or
  placeholder content in any mode; database views and page empty states must enforce that independently.

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

The conversion prompts and runbook are model-neutral. Route mechanical stages—source extraction, tag inference
(`prompts/tag-paper.md`), fact-check lookup, JSON validation and SVG checks—to a low-cost capable model. Use a
stronger model only for difficult science explanations, design decisions and tricky debugging. The CLI supports
Anthropic and OpenAI-compatible providers through `CONVERT_MODEL_PROVIDER`; provider credentials and model names
stay in ignored `.env`. Do not make paid model calls unless the owner has authorized that run.
