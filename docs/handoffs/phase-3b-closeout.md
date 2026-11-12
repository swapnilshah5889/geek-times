# The Geeky Times — Phase 3b closeout for Codex

Branch `v1` at `a7a2f9c`, pushed. `main` untouched. Preview deploy (`main`) unchanged.

Scope of this batch was Codex's "database migration first" brief: build V1 normalized schema, extract queryable rows out of the version document, keep the immutable document in jsonb, no FK constraints, one-transaction publish. No ResNet, no copy cleanup, no visuals.

## What landed

### Decision 49 (appended to `docs/decisions.md`)

Normalized V1 schema: extracted tables read through views, transactional extraction, one migration path.

Model (clarifies 38):
- Each immutable story version stays in `published_version.document jsonb`. The ordered blocks, panels and captions are the source of truth there.
- Cross-cutting data queried across pages lives in separate tables with `<thing>_id bigint` reference columns, every reference indexed, **no `REFERENCES` constraints**.
- Publishing validates every reference inside the transaction and fails on any missing one.
- `npm run apply:migration` is the canonical migration path for this repo; Supabase CLI is optional with a documented reconciliation step.

### Schema (frozen in `docs/handoffs/v1-schema-contract.md`)

24 tables, 23 views. Live on the hosted dev project at `db.btqiijvuqpdzyvciqpak.supabase.co`.

**Core content (Agent A).** `source`, `source_snapshot`, `story_source`, `citation`, `media_asset`, `facet`, `tag`, `story_tag`, `moment`, `fact`. Plus 15 metadata columns added to `published_version` (headline, dek, summary, page_title, desk, authors, year, trust, minutes, role, note, accent, source_url, source_archived_url; `library_entry jsonb` retained as transitional). `story.sample boolean` added. `story.kind` CHECK expanded to include `classic`.

**Editorial (Agent B).** `volume`, `issue` (+ `issue_story`), `company` (+ `company_post` + `company_built_on`), `storyline` (+ `storyline_step`), `field`, `node`, `relation` (+ `relation_evidence`), `front_placement` (singleton jsonb), `story_field`.

**Views + RLS (Agent D).** `v_live_story`, `v_live_library_entry` (both `security_invoker`; ride on kept policies). 21 other views run owner-side so anon never needs grants on raw tables. All join via the `_id` columns; output uses `story_slug`, `media_path`, `volume_slug` — numeric ids don't leave the server. `v_live_moment`, `v_live_fact`, `v_live_story_tag`, `v_live_citation`, `v_live_media_asset`, `v_live_story_field`, `v_facet`, `v_tag`, `v_volume`, `v_issue`, `v_issue_story`, `v_company`, `v_company_post`, `v_company_built_on`, `v_storyline`, `v_storyline_step`, `v_field`, `v_node`, `v_relation` (verified + non-sample only), `v_relation_evidence`, `v_front_placement`. Function `v_live_story_by_slug(text)`.

### Importer (Agent C, `scripts/publish-to-supabase.ts`, 781 lines)

Full rewrite. Uses `pg` with `SUPABASE_DB_URL` — no `@supabase/supabase-js` in the importer, no service-role in any browser bundle. The whole publish unit is one `pg` transaction:

1. Pre-flight validation before `BEGIN`: `schemaVersion = 2`, every `fact.claim` present, every tag approved, every reference resolves, every citation points at the story's own source, blog `trust` matches library `trust`.
2. `SELECT ... FOR UPDATE` on `story` (insert if absent).
3. SHA-256 idempotency over canonical `{document, library_entry}`. Matching hash exits 0 and writes nothing. `--force` re-publishes anyway (used once in this batch to backfill extraction rows for pre-normalized versions).
4. Upsert sources, insert staged `published_version`, extract all version-owned rows.
5. Set-based orphan audit on staged rows before promote.
6. Call existing `publish_version(bigint)` RPC to retire + flip + update `story.live_version_id`.
7. Reconciliation report: counts by row type, moments by kind, document hash.

Any failure rolls back; previous live version stays authoritative.

### Lead patches (applied during integration)

| Where | What | Why |
|---|---|---|
| A's backfill | `desk = coalesce(library_entry→desk, document→desk)` | Library wins for editorial surface; matches frontend reads |
| A's migration | `story.kind` CHECK → `(paper, blog, classic)` | library.json has `classic` sample stories |
| B's migration | `issue.number text NOT NULL` | Specials need "Special 3" ≠ slug `special-3` |
| C's importer | `data/papers/${slug}.json` path | Was missing the `data/` segment |
| C's importer | `--force` flag | Backfill for pre-v4 versions whose extraction tables didn't exist yet |
| New file | `scripts/seed-editorial-from-library.ts` + `npm run seed:editorial` | One-tx import of library.json + tags.json; placeholder story rows for every library slug (sample=true) so joins resolve |
| 5th migration | `..._patch_v_issue_number.sql` | Drop+recreate `v_issue` to expose the new `number` column |
| AGENTS.md | Repo-map line | Stale "applied with the Supabase CLI" → `npm run apply:migration` |

## Verification

### Migrations applied in order
`20261106100000_core_content_schema.sql` → `20261106100001_editorial_schema.sql` → `20261106100002_public_views_rls.sql` → `20261106120000_patch_v_issue_number.sql`. Each one-transaction, each clean. Pre-apply snapshot of the previous 2-table state saved to the session scratchpad.

### Seed
13 facets · 93 tags · 5 fields · 14 story rows (3 real + 11 placeholders, sample=true) · 5 issues · 7 issue_story · 4 companies · 6 company_post · 5 built_on · 2 storylines · 9 storyline_step · 22 nodes · 12 relations (all unverified; `v_relation` empty until backfill) · 1 front_placement.

### Three real stories published via the new importer

| Story | Live version | moments | facts | media | citations | tags |
|---|---|---|---|---|---|---|
| attention-is-all-you-need | v4 | 29 | 5 | 29 | 6 | 55 |
| size-shapes-life | v5 | 23 | 5 | 23 | 4 | 24 |
| h3-hexagons | v6 | 20 | 5 | 20 | 6 | 9 |

Moment breakdown: 1 lead + 1 hook + 4 chapter + N strip_panel + 5 fact per story. Each comic panel is its own `strip_panel` row (richer than the file-mode search-index which emitted one row per strip).

### Orphan audit
24 reference columns, each left-joined to its target. **0 orphans.**

### Negative publish test
Deleted `.claim` on size-shapes fact "5×", ran `npm run publish:supabase -- size-shapes-life`. Aborted at the pre-flight check with the correct message (`fact "5×" in evidence claim must be one of illustration, model_design, measured_result; found "undefined"`). Live v5 stayed live, still 23 moments. File reverted.

### Anon reads via publishable key
- `v_live_story` → 3 rows (samples filtered)
- `v_live_library_entry` → 3 rows
- `v_live_moment` where kind='lead' → 3 rows
- `v_live_fact` → 15 rows
- `v_issue` → 2 rows with `number` column populated
- `v_facet` → 13, `v_tag` populated, `v_relation` → 0 (expected)
- Raw `moment` read → `permission denied for table moment` (RLS working)

### Build / lint / browser
`npm run data` · `tsc -b` · `npm run lint` · `npm run build` · `npm run prerender` (27/27) · `check:prerender` (same 6 known warnings) — all green.

Browser at localhost:5173 in Supabase mode, `/papers/<slug>` for all three real stories: correct titles (`One word, two worlds`, `Why a bigger deer breaks`, `A world covered in honeycomb`) and the right stamp mix (`Illustration · numbers invented` / `From the paper · model design · preprint` / `From the post · model design · company-reported`). Owner confirmed.

## What's still file-backed (explicit)

- `public/data/search-index.json` (feed, search, home-page moments)
- `public/data/site.json` (site name, mediaBaseUrl, default paper, file-mode papers list)
- `public/data/library.json` shell (overlaid from `v_live_library_entry` at runtime; true source is now the DB)
- Prerendered HTML in `dist/<route>/index.html` (build-time; live data arrives on mount)
- Media files under `public/media/<slug>/`

## Residuals / flagged

1. **21 views are security-definer by design.** Supabase advisor will flag them; this is the deliberate public-read-encapsulation pattern (decision 49).
2. **12 relations unverified by default** → `v_relation` returns 0 rows until the owner backfills with evidence.
3. **Frontend still reads `published_version` directly** via the kept `published_version_public_read_live` / `story_public_read` policies. The `v_live_*` views are ready for the loader to switch; that's a natural next batch.
4. **Placeholder story rows carry `kind='paper'`** as a default (sample=true). Revise if sample content gets real kinds.
5. **Pre-v4 versions (1, 2, 3) have no extracted rows.** They are retired now; live reads are clean. New publishes always extract.
6. **Desk mismatches** (attention library "AI & language" vs doc "Machine learning"; h3 library "Real world / Maps & rides" vs doc "Maps & rides"). Importer stores the library value with a warning. If this should be one-source-of-truth, the next pass picks a rule.

## Open questions from Agent B (for later pass)

- `node.short`, `node.blurb`, `issue.classics`, `relation.cited`, `relation.crossField` — present in data, not in the contract. Not storing them for now; follow-up migration if the frontend starts to need them.
- `tag` has no parent column; aliases stored as `text[]`, hierarchy flattened.

## Not in this batch (per the brief)

ResNet conversion, Transformer/H3 copy or ledger cleanup, archive-page redesign, media CDN, OG cards, Next.js migration, feed/search runtime loaders. **Zero visual changes.**

## Next pass options (ranked)

1. **Flip the frontend to the `v_live_*` views.** Removes the direct `published_version` policies and makes the normalized tables the only path. Needed before any normalized-table-only guarantee; ~1 day with the current boundary in `src/data/source-supabase.ts`.
2. **Backfill verified relations + RelationEvidence rows** for the paper↔paper edges we already know (Transformer ↔ ResNet, Transformer ↔ LSTM, etc.). Lights up `v_relation` for the family-tree view.
3. **ResNet conversion.** Intake doc is accurate (`docs/handoffs/resnet-intake.md`). A ResNet story does not by itself verify the ResNet → Transformer relation; that still needs evidence.
4. **Canonical archive routes.** `/issues`, `/companies`, `/map` listing pages. Option A drafted in `docs/handoffs/canonical-routes.md`.
5. **Transformer strip 1 rewrite** (last residual from Phase 2 — background framing panels still blocking reclassification).

Pick one; everything else stays queued.
