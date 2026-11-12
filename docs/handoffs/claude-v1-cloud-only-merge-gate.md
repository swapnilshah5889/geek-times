# Claude Code handoff — cloud-only V1 merge gate

**Branch:** `v1`. Never write or push to `main`; do not create another branch. The owner merges `v1` when ready.
**Goal:** finish the owner's personal-use V1 requirements before `v1` is merged into `main`.
**Read first:** `AGENTS.md`, `docs/STATE.md`, this file, `docs/production-plan.md`, `docs/data-model.md`, and decisions 49–54 in `docs/decisions.md`.

## V1 acceptance definition

- Supabase is the source of truth for every story and editorial datum shown by the app.
- `data/seed/*.json` remains in Git for conversion/import/recovery only. Browser code must not fetch or import those files.
- Prerendered HTML contains a serialized snapshot generated from Supabase for first paint/hydration. Treat it as a generated bootstrap cache, never as the source of truth; client reads and later loads come from Supabase. Do not remove it or redesign loading without asking the owner.
- All story media is served from Supabase Storage. `public/media/` must not be the deployed runtime source.
- No sample, demo, mockup, unverified, or placeholder records/copy/art are visible as site content. Hide unsupported modules or show an honest empty state. Clearly stamped teaching illustrations with invented numbers remain allowed by the product trust rules.
- A live publish appears in home and search after reload and the story URL opens without rebuilding the app.
- The DB can be exported and restored into a clean non-production target with a reconciliation check.

## Orchestrator instructions — Claude lead

Use the lowest-cost capable Claude subagent/model available (Haiku-class for mechanical audits and bounded code edits). Give each agent only its task, relevant acceptance rules, and named files; do not pass the full project history or ask agents to reread the whole repository. Keep agent reports under 10 bullets.

Run Agents A–D in parallel. Agent E may audit in parallel, but its deletion pass depends on Agent A's verified upload and Agent B's verified recovery copy. Agents do not commit, push, merge, alter Vercel settings, or write to the owner's live database. Each agent must report files changed, commands run, results, and unresolved issues.

When all agents return, the orchestrator must inspect every diff itself, check that changes obey the task boundaries, resolve conflicts, connect script commands, and run the integrated gates. Do not accept an agent's “done” summary as verification. If evidence requires a write to the owner's cloud project, stop before that write and report the exact owner action needed; use read-only checks or a disposable local target meanwhile.

## Parallel agent tasks

### Agent A — Supabase Storage media path

**Own only:** the new Storage upload/check utility and its focused migration or Storage policy files. Do not edit `package.json`, `src/data/source.ts`, shared docs, or story data. If a small `MediaView` change is essential, report it to the orchestrator first rather than editing shared UI files.

**Task:** inspect current media paths and the existing Supabase setup; add an idempotent upload command that preserves each `public/media/<story>/...` relative path in a public-read Storage bucket. Keep credentials server-side and out of logs. Add a read-only verification mode that checks every media asset referenced by live story documents exists in the bucket and reports missing paths. Do not delete local media; report a verified manifest for Agent E to use after backup acceptance.

**Acceptance:** repeat upload is safe; URL/path mapping is deterministic; public SVG fetch works cross-origin for `MediaView`; secrets are never printed; no live DB row or bucket is changed by verification mode. Give the orchestrator the exact env names and commands to wire.

### Agent B — export and restore proof

**Own only:** new export/reconciliation/restore-check scripts and their focused documentation under `docs/handoffs/`. Do not edit `package.json`, migrations, importer, or shared `supabase/README.md`.

**Task:** audit the existing `scripts/seed-editorial-from-library.ts` and `scripts/publish-to-supabase.ts`; reuse them rather than replacing the import path. Implement the smallest safe way to export the relevant Supabase content into a temporary location and compare stable slugs/keys/counts/references against `data/seed/`. Add a restore-drill command or exact reproducible procedure for a disposable empty database.

**Acceptance:** no destructive operation can target the configured live project by default; output contains no secrets; mismatch exits non-zero with useful paths/keys; document exactly what is and is not covered, especially media objects and numeric IDs. Do not claim full recovery until both DB rows and media are covered.

### Agent C — remove visible scaffolding and fix accessibility

**Own only:** `src/pages/HomePage.tsx`, `src/pages/FeedPage.tsx`, `src/pages/SearchPage.tsx`, `src/pages/IssuePage.tsx`, `src/pages/CompanyPage.tsx`, `src/pages/MapPage.tsx`, `src/components/FamilyTree.tsx`, `src/pages/SamplePage.tsx`, plus the smallest relevant CSS file if needed. Do not edit database content, route logic, `package.json`, or docs.

**Task:** remove or hide user-visible sample/demo/placeholder UI and the records that feed it; replace it only with an honest empty state. Audit at least the disabled newsletter / “Sign-ups open soon” module, “Out next Friday”, SamplePage and sample snack/storyline/vault paths, `[Company name]` / `[year]` branches, placeholder grey story art, and Map/FamilyTree mockup nodes and unverified links. Also add one meaningful `<h1>` to home/feed/search; correct issue/company card heading levels; raise undersized mobile header, pause-animation, and issue TOC hit areas to 44px.

**Acceptance:** no fabricated facts, demo records, sample copy, fake dates, or placeholder art render in local preview or live mode. A page with no real records communicates that truthfully. Genuine unpublished stories may appear in local preview; sample/demo records may not. Clearly stamped invented teaching illustrations remain allowed. Semantic changes preserve visual appearance; hit-area changes cause no wrapping/overflow at 375px. Get canvas approval before visible redesign.

### Agent D — cloud-runtime, content, and deployment audit

**Own only:** a new read-only checker under `scripts/` (if a useful deterministic check is possible) and a concise audit report under `docs/handoffs/`. Do not edit source runtime loaders, Vercel configuration, environment values, or `package.json`.

**Task:** verify the browser has no import/fetch path to local story/editorial JSON; enumerate runtime Supabase views; distinguish inline prerender snapshot JSON from seed files; inspect route fallback and identify required Vercel env variable names. Audit public routes/views for sample flags, placeholder copy/art, unverified graph rows, fake dates, and local media. Provide a no-rebuild publish procedure and network assertions distinguishing DB reads, inline snapshot, and media requests.

**Acceptance:** report facts with file/line references and exact commands. No credentials, database writes, deployment setting changes, or invented success claims.

### Agent E — remove local runtime copies from Git/build

**Own only:** inventory and cleanup of obsolete runtime copies under `public/data/` and `public/media/`, plus references in Vite/public asset configuration if required. Do not edit page components, Storage upload code, `package.json`, or `data/seed/`.

**Task:** first inventory every static data/art file tracked in Git and classify it as runtime copy, unused sample, generator/source, design reference, or recovery backup. After Agent A verifies every live media object exists in Storage and Agent B proves a complete restorable backup, remove local runtime copies and unused sample art from Git and ensure Vite no longer ships or requests them. Keep source-generation tools and design references. Keep `data/seed/` in Git as the full recovery/import source, per the owner's confirmation; the browser must never read it.

**Acceptance:** no browser request for story/editorial JSON or live story media is served from the app origin; all live media resolves from Storage; the Git recovery copy remains complete. Report each removed path and why it was safe to remove. If an asset is still referenced, do not delete it.

## Orchestrator integration and release checklist

1. Review each agent's diff and report. Reject broad refactors or unrelated content edits. Run Agent E's deletion pass only after A and B evidence is accepted.
2. Wire stable script commands in `package.json` yourself (only the orchestrator edits it) and add checks to the V1 plan. Keep commands safe by default.
3. Run typecheck, lint, build, prerender, `check:prerender`, `check:hydration`, the media URL check, the seed/export reconciliation, and a public-content placeholder scan. Re-run the 17-route desktop/phone smoke sweep after accessibility/content cleanup.
4. Verify Storage URL configuration and deployment environment names without printing values. Do not modify Vercel project settings or deploy production.
5. Confirm the target Supabase project has expected migrations, RLS/view behavior, and live stories using read-only queries. Do not create, approve, overwrite, or delete a live story for testing. If the no-rebuild proof needs a cloud write, report the exact safe preview action for the owner.
6. Update `docs/STATE.md` and `docs/production-plan.md` from evidence only. Verify the old sample object in Supabase `front_placement.onThisDay` is hidden or null. No demo relations, placeholder art, or placeholder copy may remain visible.
7. Return a concise closeout: accepted/rejected agent changes, changed files, checks and results, remaining owner actions, and whether every V1 merge gate is evidenced. Do not merge `v1` into `main`.

## Out of scope

More story conversions or illustration redesign; family-tree/map fact-checking; admin UI; newsletter, share cards, analytics, custom domain, legal/public-launch work; Next.js/router migration; committing secrets; paid model/provider calls. No visible visual redesign without canvas approval.
