# Production plan

Current launch sequence for The Geeky Times. Updated 2026-11-11 to make the owner's V1 merge bar explicit. `docs/STATE.md` is the current implementation snapshot; this file is the authoritative order of remaining work. Decisions live in `docs/decisions.md`.

## V1 definition

V1 means the owner can use the site to read and explore personally curated stories, with Supabase as the source of truth for all story and editorial data and Supabase Storage serving story media. Git-tracked `data/seed/*.json` remains an import/backup source only; the frontend must not fetch or import it. No sample, demo, mockup, unverified, or placeholder records, copy, or art may be presented as real content. Hide a section or show an honest empty state until real sourced content exists. Original teaching illustrations may use invented numbers only when clearly stamped `Illustration · numbers invented`, per the product's trust model.

Prerendered HTML currently embeds a JSON snapshot built from Supabase to hydrate the first paint. This is a generated bootstrap/cache, not a seed-file read or source of truth. After startup, Supabase view reads are authoritative. Keep this unless the owner explicitly requires every first paint to make a live request.

## V1 merge gate — complete before merging `v1` into `main`

| Gate | Status | Acceptance evidence |
|---|---|---|
| Frontend story/editorial data comes only from Supabase views; seed JSON is not imported/fetched by browser code | **Implemented; re-audit** | Source audit or a small guard confirms no runtime file-backed loader; browser network shows Supabase reads and no local JSON data requests. |
| No fabricated/sample/placeholder content is visible | **Pending audit and cleanup** | Audit every route in local and live modes. No sample stories/companies/issues, demo graph nodes or unverified relations, placeholder art, fake dates, disabled newsletter signup, "Out next Friday", or `[Company name]`/`[year]` copy. Hide unsupported modules or show a truthful empty state. Genuine preview drafts may appear only in the local preview mode. Explicitly stamped teaching illustrations remain allowed. |
| Cloud media | **Pending** | Upload referenced assets to Supabase Storage, set the cloud media base URL, and confirm every live story asset loads from Storage in the deployed build with no `/media/` requests. |
| Remove duplicate local runtime assets | **Pending; after media and backup verification** | Remove obsolete `public/media/` and any `public/data/` runtime copies from Git/build after Storage verification and restore proof. Keep `data/seed/` in Git as the complete import/recovery copy; the app must not read it. |
| Database/schema acceptance on the V1 project | **Needs recorded verification** | Migrations are applied in order; intended live stories are present; public views expose only live/non-sample content; no orphan or unintended anon-readable rows. Never print secrets. |
| Publish-to-read flow without a site rebuild | **Implemented by design; verify end to end** | Publish/approve one story using the normal workflow; after reload it appears in home and search and its direct URL loads, without a code change or site rebuild. Preview remains hidden from the live deployment. |
| Backup and restore | **Pending** | Export cloud data and media, restore into a clean non-production target, and reconcile restored records/assets against the Git seed. Do not run destructive restore steps against the owner's live project. |
| Deployment configuration | **Needs verification** | Vercel has the correct Supabase URL and publishable key, builds and deep-link fallback work, and a preview deploy can read live data and cloud media. Vercel currently tracks `main`; do not change that or deploy to production as part of this gate without the owner's direction. |
| Accessibility fixes from the page sweep | **Pending** | Home/feed/search have one `<h1>`; issue/company card heading levels are sequential; mobile header, pause, and issue TOC controls meet the 44px target without a visible layout redesign. |
| Final release checks | **Pending for merge** | `npx tsc -b`, `npm run lint`, `npm run build`, `npm run prerender`, `npm run check:prerender`, `npm run check:hydration`; route smoke check at 1280px and 375px with no console errors or horizontal overflow. |
| Documentation matches the shipped behavior | **This update in progress** | `STATE.md`, this plan, and the Claude handoff agree on runtime source, media, backup, deployment, and intentional gaps. |

Do not merge to `main` until the gates above have evidence and the owner chooses to release. Work stays on `v1`; no feature branch and no direct write to `main`.

## Implemented foundations

- **Supabase-only runtime (decision 51):** frontend reads site settings, vocabulary, live story documents, library entries, moments, search inputs, and editorial collections from public Supabase views. File mode and `public/data/` runtime reads are removed.
- **Dynamic discovery:** home feed and search are derived from live story/moment rows. Newly published stories are included on the next page load; no app rebuild is required for the client data path.
- **Preview/live workflow (decision 52):** preview stories use preview views in local development; the live site reads live views. CLI tools support status and approval.
- **Normalized schema and importer (decision 49):** SQL migrations, public views/RLS, and transactional publishing with extracted rows are implemented. The target-project acceptance evidence still needs to be recorded.
- **Prerender/hydration:** routes are enumerated from Supabase at build time; HTML embeds a Supabase-generated initial snapshot and hydrates via `hydrateRoot`. This improves initial rendering but means the first HTML is a build-time copy until the client refreshes from Supabase.
- **Conversion workflow:** provider-neutral conversion and fact-check tooling exist; data changes are published to Supabase through the import workflow.
- **Page coverage:** home, stories, issues, companies, map, feed and search are implemented. The current sweep checked 17 route variants at 1280px and 375px without runtime errors or horizontal overflow.

## Remaining work after the merge gate

These are useful, but are not required for the owner's personal-use V1 unless they become a blocker during use:

- Build real, sourced family-tree/map relationships. Until then, hide demo nodes and unverified links or show a truthful empty state; do not expose mockup data in V1.
- Add more real stories and company posts; short lists are expected until then.
- Curate an anniversary for On This Day; the tile is intentionally hidden while no sourced entry exists.
- Add new original illustrations for stories when ready. A real story may use a truthful text-only/empty-art treatment; grey placeholder plates are not allowed in V1.
- Make `/issues` and `/companies` proper archive pages or redirect them to canonical detail routes; current index routes can duplicate their first detail page.
- Add the dev-only admin page, stronger automated test suite, CI, and automated/manual accessibility sweep beyond the focused fixes above.
- Add social share cards, sitemap/structured metadata, newsletter, custom domain, analytics, legal pages, and public-launch operations.

## Non-goals for this V1

- Moving the story seed out of Git. The seed is the recovery/import artifact, not a frontend data source.
- Replacing the initial prerender snapshot with a blank screen while data loads. The snapshot is generated from the cloud database; client Supabase reads remain authoritative after startup.
- Inventing graph evidence to make the map look complete. Demo graph data must be hidden; a warning badge does not make fabricated records acceptable for V1.
- Merging or deploying to `main` without the owner's release decision.

## Prior plan items superseded by the current architecture

The old Phase 3a/3b checklists and the JSON-backed runtime plan are historical. They are superseded by decisions 49–53 and the V1 merge gate above. In particular, do not restart work on `VITE_DATA_SOURCE`, a file-backed frontend loader, `public/data/*.json` runtime reads, or the old story-only Supabase slice. `docs/STATE.md` records the current table/view map and known content gaps.
