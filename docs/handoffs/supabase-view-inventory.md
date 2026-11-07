# Supabase view inventory (V1 Supabase-only cutover)

Date: 2026-11-07. Branch `v1`. Read-only audit. No frontend, migration, STATE.md or production-plan.md edits.

**Method.** Read the five files in `supabase/migrations/` in filename order: `20261106085857_init_story_slice.sql`, `20261106100000_core_content_schema.sql`, `20261106100001_editorial_schema.sql`, `20261106100002_public_views_rls.sql`, `20261106120000_patch_v_issue_number.sql`. Cross-checked each surface against `public/data/*.json` and the consumers in `src/` (`src/data/source-supabase.ts`, `src/lib/feed.ts`, `src/lib/tags.ts`, `src/components/FamilyTree.tsx`, `src/pages/MapPage.tsx`, `src/pages/CompanyPage.tsx`) and `scripts/seed-editorial-from-library.ts`. Verified against migration text and JSON only, not against a live database. Types are Postgres types derived from the base columns. "NN" means NOT NULL on the base column, or a column in a non-optional position of the view.

Naming note: the task text refers to `library.json.frontPage`. The actual key is `library.json.front`. There is no moments-of-the-week key in `library.json`. The "moments" shown on the home and feed come from `search-index.json` `papers[].moments`.

---

## 1. Summary

- **23 views and 1 SQL function** (`v_live_story_by_slug(text)`), all defined in `20261106100002_public_views_rls.sql`, plus one drop-and-recreate in the patch. Anon has SELECT on all 23 views, and EXECUTE on the function. Nothing is granted to authenticated.
- **Covered:** all ten surfaces have a view, with gaps listed in section 3.
- **Missing:** site metadata (`site.json`) has no view. Tag lineage (`tags.json` `parent`), facet description, node `blurb`/`short`, and relation `cited`/`crossField` have no column.
- **Blocker for a Supabase-only runtime:** every view filters `story.sample = false`. Eleven of the fourteen `library.json` stories are `sample: true` and have no published version. Seven of them are referenced by the home front page, issue 001 and the company pages. Those references resolve to nothing in the views. See section 3.1.
- **Map edges are empty by default.** `seed-editorial-from-library.ts` inserts every relation with `verified = false`. `v_relation` requires `verified = true`.
- **Grant regression risk** in the patch (section 6.1).
- **Pagination:** nothing reaches the 1000-row default at V1 scale. `v_live_moment` is the only view that could, at roughly 75 or more live papers at the current density. Keyset on `(story_slug, key)` if it ever does.

---

## 2. Gate and grant model

| Group | Security mode | Gate | Anon grant |
|---|---|---|---|
| `v_live_story`, `v_live_library_entry` | `security_invoker = true` | `pv.status = 'live'` and `s.sample = false` | SELECT on view |
| `v_live_moment`, `v_live_fact`, `v_live_story_tag`, `v_live_citation`, `v_live_media_asset`, `v_live_story_field` | owner rights (no security_invoker) | `pv.status = 'live'` and `s.sample = false` (plus `st.status = 'approved'` for tags) | SELECT on view |
| `v_facet`, `v_tag` | owner rights | none (full vocabulary) | SELECT |
| `v_volume`, `v_field` | owner rights | none (no `sample` column on the table) | SELECT |
| `v_issue`, `v_issue_story`, `v_company`, `v_company_post`, `v_company_built_on`, `v_storyline`, `v_storyline_step`, `v_node` | owner rights | `sample = false` on the row, and on joined story/node/company where present | SELECT |
| `v_relation`, `v_relation_evidence` | owner rights | `verified = true` and `sample = false` on the relation, plus `sample = false` on both nodes | SELECT |
| `v_front_placement` | owner rights | `key = 'current'` | SELECT |
| `v_live_story_by_slug(p_slug)` | `security invoker` function over `v_live_story` | same as `v_live_story` | EXECUTE |

Raw tables are not granted to anon except two (section 6.3): `story` (SELECT, policy `using (true)`) and `published_version` (SELECT, policy `status = 'live'`). All other base tables have RLS on, no anon grant, and no policy.

---

## 3. Surface coverage

| # | Surface (current source) | Covered by | Gaps |
|---|---|---|---|
| 1 | Home front-page slots (`library.json.front`: lead, aside, more, topics, real, storylines, vault, onThisDay) | `v_front_placement` (layout, as JSON) + `v_live_library_entry` (card copy) + `v_live_story` (live rows) | (a) Front references seven sample-only slugs with no row in any view: `crispr`, `alphafold`, `penicillin`, `ligo`, `resnet`, `blog-streaming`, `blog-social`. (b) The `front` JSON holds slugs only. Nothing validates them against live stories (the schema comment says the publish validator must). (c) No "moments of the week" key exists. Moments come from `v_live_moment`. |
| 2 | Home discovery + Feed moments (`search-index.json` `papers[].moments`, ordered by `feed.ts`: cover, then chapter, strip, fact in array order) | `v_live_moment` (ordered by `position`) + `v_live_story` (cover data lives in `document`) | (a) Kind mismatch: DB has `lead`, `hook`, `chapter`, `strip_panel`, `fact`. The frontend `Moment['kind']` is `strip \| chapter \| fact`. The loader must map `strip_panel` to `strip` and drop or handle `lead`/`hook`. (b) `position` is nullable. (c) `href` and `paper` are not columns; derive from `story_slug` and `ref`. (d) `featured` (feed and search lead paper) has no column. Candidate: `v_front_placement.data->>'lead'`, which is an assumption, not a verified equivalence. |
| 3 | Search (`tags.ts` over `search-index.json`: title and summary full-text, tag AND-filter with lineage) | `v_live_story` (story_slug, page_title, summary, authors, year, desk, headline, dek, document), `v_live_moment` (headline, text), `v_live_story_tag` + `v_tag` (tag filter and aliases), `v_facet` | (a) The paper's **title** is not a column. `page_title` is "One word, two worlds"; the paper title "Attention Is All You Need" is in `library_entry->>'title'`. (b) Lineage needs `tag.parent` (missing, see 4). (c) No search column or index exists. Matching runs on view text (fine at V1). |
| 4 | Tag vocabulary + facet (`tags.json`: facets {id, label, description}, tags {id, facet, label, aliases, parent}) | `v_facet` (key, label, position), `v_tag` (key, label, aliases, facet_key, facet_label) | (a) **MISSING** `facet.description` (in JSON, not in table or view). (b) **MISSING** `tag.parent` (in JSON, used by `tagLookup.lineage`, not in table or view). `aliases` is covered by `tag.aliases` and `v_tag.aliases`. |
| 5 | Issues list + detail (`library.json.issues`) | `v_issue` (slug, number, title, color, published, position, volume_slug, cover_story_slug), `v_issue_story` (issue_slug, story_slug, position) | (a) Sample issues (`special-1..3`) are excluded, which is intended. (b) Issue 001 references six stories. `v_issue_story` drops the five sample ones silently, so only `attention-is-all-you-need` remains. (c) `classics` (counts on special issues) has no column. Sample only. (d) `published` is free text. No publish date exists anywhere (section 5). |
| 6 | Companies list + detail (`library.json.companies`) | `v_company` (slug, name, sector, blurb, posts_followed, coming), `v_company_post` (company_slug, story_slug, position), `v_company_built_on` (company_slug, node_slug, position) | (a) `streaming`, `social`, `ride` are `sample: true`, so `v_company` drops them. Only `uber` survives, and its post `h3-hexagons` is live. (b) `posts`/`builtOn` ordering is by `position` (fine). |
| 7 | Storylines (`library.json.storylines`) | `v_storyline` (slug, title), `v_storyline_step` (storyline_slug, position, year, label, current, story_slug) | (a) `mold` is sample, so it is dropped. `machines-read` has five steps; step `story_slug` is null for steps with no live story (left join). Verify the frontend handles null. (b) `year` is text, as in JSON. |
| 8 | Map nodes + relations (`library.json.nodes`, `.relations`, `.fields`) | `v_field` (slug, label, color, cluster), `v_node` (slug, title, authors, year, kind, x, y, field_slug, story_slug), `v_relation` (source_node_slug, target_node_slug, kind, note), `v_relation_evidence` | (a) **MISSING** `node.blurb` and `node.short` (used by `FamilyTree.tsx` and `MapPage.tsx`, present on 4 nodes). (b) **MISSING** `relation.cited` and `relation.crossField` (used by `MapPage.tsx` and `FamilyTree.tsx`, on 4 relations). (c) Relation JSON uses `from`/`to`. The view returns `source_node_slug`/`target_node_slug`. Rename in the loader. (d) **Empty at V1**: all relations are seeded `verified = false`, so `v_relation` returns zero rows until someone sets `verified = true`. This is a data step, not a view bug. |
| 9 | Papers list for routing + prerender (`site.json.papers`: slug, title, dataUrl) | `v_live_story` (story_slug, kind, page_title, headline, desk, dek, summary, source_url, version_created_at) | (a) `title` for routing is not a column. Use `library_entry->>'title'` (the paper title), not `page_title`. (b) `dataUrl` is file-only, with no DB equivalent needed. (c) Routing sees only live, non-sample stories. Expected. |
| 10 | Site metadata (`site.json`: name, motto, tagline, navLabel, mediaBaseUrl, defaultPaper, schemaVersion) | **MISSING** | No view, table or column. Proposed: a singleton `site_settings` row (key `'current'`, `data jsonb`, same pattern as `front_placement`) with a `v_site` view (`key`, `data`), granted SELECT to anon. Columns in `data`: name, motto, tagline, nav_label, media_base_url, default_story_slug, schema_version. `defaultPaper` and `search-index.featured` would both come from here. |

### 3.1 Sample-story gap (blocker)

Views exclude `sample = true` by design (`story`, `issue`, `company`, `storyline`, `node`, `relation`). The sample stories are exactly the ones the shell references:

- `library.json` sample stories (11): `resnet`, `alphafold`, `crispr`, `ligo`, `higgs`, `penicillin` (classic), `blog-streaming`, `blog-video`, `blog-artwork`, `blog-social`, `blog-ride`.
- Front references: `aside` (crispr, alphafold, penicillin), `more` (ligo, resnet), `real` (blog-social), `topics` (resnet, alphafold, crispr, penicillin), `storylines` (none sample).
- Issue 001 (`attention-is-all-you-need`, `resnet`, `alphafold`, `blog-social`, `ligo`, `penicillin`): five of six are sample.
- Company social/ride/streaming: sample.

Under the current gate, a Supabase-only runtime renders only the three real stories (`attention-is-all-you-need`, `size-shapes-life`, `h3-hexagons`). The home page loses most of its cards and two issues lose most of their contents. Decision needed before cutover: either (a) publish sample stories with `sample = true` and add a sample-inclusive view (for example `v_live_story_all`), or (b) keep the file shell as the sample layer, which the contract already allows ("library.json as the shell"). The contract says the `_all` variant "or leave it to a later batch".

---

## 4. Per-view column inventory

Each table lists the view's own output columns in order. `Gate` restates the WHERE.

### 4.1 Story views

**`v_live_story`** (security_invoker). Gate: `pv.status='live'` and `s.sample=false`. Reads `story`, `published_version`.

| column | type | null |
|---|---|---|
| story_slug | text | NN |
| kind | text (CHECK paper, blog, classic) | NN |
| schema_version | int | NN |
| headline | text | NN |
| accent | text | null |
| dek | text | NN |
| summary | text | NN |
| page_title | text | NN |
| desk | text | NN |
| authors | text | NN |
| year | int | NN |
| trust | text (CHECK peer_reviewed, preprint, company_reported) | NN |
| minutes | int | NN |
| role | text (CHECK lead, feature, brief, vault, real_world) | null |
| note | text | null |
| source_url | text | NN |
| source_archived_url | text | null |
| document | jsonb (PaperDoc) | NN |
| library_entry | jsonb (LibraryStory, transitional) | NN |
| version_created_at | timestamptz | NN |

**`v_live_library_entry`** (security_invoker). Gate as above. Projection of `v_live_story`.

| column | type | null |
|---|---|---|
| story_slug | text | NN |
| library_entry | jsonb | NN |

**`v_live_story_by_slug(p_slug text)`**. `setof v_live_story`, security invoker, `stable`. Returns zero rows for an unknown slug (not null).

### 4.2 Extracted version rows (owner rights)

**`v_live_moment`**. Gate: live, non-sample. Reads `moment`, `published_version`, `story`, `media_asset`. Unique per live story on `(story_slug, key)`.

| column | type | null |
|---|---|---|
| story_slug | text | NN |
| key | text | NN |
| kind | text (CHECK lead, hook, chapter, strip_panel, fact) | NN |
| position | int | null |
| claim | text (CHECK illustration, model_design, measured_result) | null |
| trust | text (CHECK peer_reviewed, preprint, company_reported) | null |
| source_label | text | null |
| source_url | text | null |
| media_path | text | null (left join) |
| headline | text | null |
| text | text | null |
| ref | text | null |

**`v_live_fact`**. Gate: live, non-sample. Reads `fact`, `published_version`, `story`, `media_asset`.

| column | type | null |
|---|---|---|
| story_slug | text | NN |
| block_id | text | NN |
| position | int | null |
| figure | text | NN |
| claim | text (CHECK illustration, model_design, measured_result) | NN |
| text | text | NN |
| source_label | text | null |
| source_url | text | null |
| media_path | text | null |

**`v_live_story_tag`**. Gate: live, non-sample, `st.status='approved'`. Reads `story_tag`, `tag`, `published_version`, `story`.

| column | type | null |
|---|---|---|
| story_slug | text | NN |
| tag_key | text | NN |
| tag_label | text | NN |
| relevance | numeric (0..1) | NN |
| basis | text (CHECK paper, background, editorial) | NN |
| evidence | text | null |
| source_kind | text (CHECK ai, editor) | null |

**`v_live_citation`**. Gate: live, non-sample. Reads `citation`, `published_version`, `story`.

| column | type | null |
|---|---|---|
| story_slug | text | NN |
| anchor | text | null |
| url | text | NN |
| label | text | NN |
| context | text | null |

**`v_live_media_asset`**. Gate: live, non-sample. Reads `media_asset`, `published_version`, `story`.

| column | type | null |
|---|---|---|
| story_slug | text | NN |
| path | text | NN |
| kind | text (CHECK svg, image, video) | NN |
| width | int | NN |
| height | int | NN |
| alt | text | null |

**`v_live_story_field`**. Gate: live, non-sample. Reads `story_field`, `field`, `published_version`, `story`.

| column | type | null |
|---|---|---|
| story_slug | text | NN |
| field_slug | text | NN |
| field_label | text | NN |
| position | int | NN |

### 4.3 Vocabulary

**`v_facet`**. No gate. Reads `facet`.

| column | type | null |
|---|---|---|
| key | text | NN |
| label | text | NN |
| position | int | null |

**`v_tag`**. No gate. Reads `tag`, `facet`.

| column | type | null |
|---|---|---|
| key | text | NN |
| label | text | NN |
| aliases | text[] | NN (default `'{}'`) |
| facet_key | text | NN |
| facet_label | text | NN |

### 4.4 Editorial

**`v_volume`**. No gate (table has no sample column). Reads `volume`.

| column | type | null |
|---|---|---|
| slug | text | NN |
| title | text | NN |
| kind | text (CHECK regular, special) | NN |

**`v_issue`**. Gate: `i.sample=false`. `cover_story_slug` is null unless the cover story is non-sample. Reads `issue`, `volume`, `story`. Patched (see 6.1).

| column | type | null |
|---|---|---|
| slug | text | NN |
| number | text | NN |
| title | text | NN |
| color | text | null |
| published | text | null (free text) |
| position | int | NN |
| volume_slug | text | NN |
| cover_story_slug | text | null |

**`v_issue_story`**. Gate: `issue.sample=false` and `story.sample=false` (inner joins, silent drop). Not gated on live version. Reads `issue_story`, `issue`, `story`.

| column | type | null |
|---|---|---|
| issue_slug | text | NN |
| story_slug | text | NN |
| position | int | NN |

**`v_company`**. Gate: `sample=false`. Reads `company`.

| column | type | null |
|---|---|---|
| slug | text | NN |
| name | text | NN |
| sector | text | null |
| blurb | text | null |
| posts_followed | int | null |
| coming | jsonb | null |

**`v_company_post`**. Gate: company and story `sample=false` (inner joins). Not gated on live version. Reads `company_post`, `company`, `story`.

| column | type | null |
|---|---|---|
| company_slug | text | NN |
| story_slug | text | NN |
| position | int | NN |

**`v_company_built_on`**. Gate: company and node `sample=false`. Reads `company_built_on`, `company`, `node`.

| column | type | null |
|---|---|---|
| company_slug | text | NN |
| node_slug | text | NN |
| position | int | NN |

**`v_storyline`**. Gate: `sample=false`. Reads `storyline`.

| column | type | null |
|---|---|---|
| slug | text | NN |
| title | text | NN |

**`v_storyline_step`**. Gate: storyline `sample=false`. Story is a left join, filtered by `story.sample=false` in the join, so it can be null. Reads `storyline_step`, `storyline`, `story`.

| column | type | null |
|---|---|---|
| storyline_slug | text | NN |
| position | int | NN |
| year | text | null |
| label | text | null |
| current | boolean | NN |
| story_slug | text | null |

**`v_field`**. No gate (table has no sample column). Reads `field`.

| column | type | null |
|---|---|---|
| slug | text | NN |
| label | text | NN |
| color | text | null |
| cluster | jsonb | null |

**`v_node`**. Gate: `n.sample=false`. Story is a left join filtered by `story.sample=false`. Reads `node`, `field`, `story`.

| column | type | null |
|---|---|---|
| slug | text | NN |
| title | text | NN |
| authors | text | null |
| year | int | null |
| kind | text (CHECK paper, blog) | NN |
| x | int | null |
| y | int | null |
| field_slug | text | NN |
| story_slug | text | null |

**`v_relation`**. Gate: `r.verified=true` and `r.sample=false`, both nodes `sample=false`. Reads `relation`, `node`.

| column | type | null |
|---|---|---|
| source_node_slug | text | NN |
| target_node_slug | text | NN |
| kind | text (CHECK builds_on, improves_on, uses_method, cited, family) | NN |
| note | text | null |

**`v_relation_evidence`**. Gate: the relation gate of `v_relation` (joined). Reads `relation_evidence`, `relation`, `node`.

| column | type | null |
|---|---|---|
| source_node_slug | text | NN |
| target_node_slug | text | NN |
| url | text | null |
| note | text | null |

**`v_front_placement`**. Gate: `key='current'`. Reads `front_placement`. `data` holds slugs, not ids, and is not validated against live stories.

| column | type | null |
|---|---|---|
| key | text | NN |
| data | jsonb | NN |

---

## 5. Needed by the frontend but not exposed

| Where | Field | Current source | Status |
|---|---|---|---|
| story | paper title (for search and routing) | `library_entry->>'title'` | Inside jsonb only. Add a `title` column or document the jsonb path. |
| story | publish date | none | Not stored. `version_created_at` is when the live version row was inserted (changes on every republish), so it is not a publish date. Ordering today uses array order in `front` and `issue_story.position`, so no date is needed for V1. |
| story | ordering column | none | Not a column. Use `issue_story.position`, `company_post.position`, `storyline_step.position`, or the `front_placement.data` arrays. |
| story | numeric id | `story.id` | Withheld by design (decision 35). Join on slug. |
| story | `cover` (kicker, headline, dek, media, hook.stat, frames) | `search-index` `papers[].cover` | Only in `document` (PaperDoc `cover?`). Confirm with the loader, which is not verified here. |
| story | `tags` (id, relevance) | `search-index` `papers[].tags` | Available as `v_live_story_tag` (tag_key, relevance). |
| moment | ordering inside a story | array order in `search-index` | `position` is nullable. Use `NULLS LAST` or make it NOT NULL. |
| moment | `href` / `paper` | derived in JSON | Derive from `story_slug` and `ref`. |
| tag | `parent` (lineage) | `tags.json` | **MISSING** from `tag` and `v_tag`. |
| facet | `description` | `tags.json` | **MISSING** from `facet` and `v_facet`. |
| site | all keys | `site.json` | **MISSING** entirely (section 3, row 10). |
| site/search | `featured` paper | `search-index.json` | **MISSING**. Derive or store in site settings. |
| node | `blurb`, `short` | `library.json` | **MISSING** from `node` and `v_node`. Used by `FamilyTree.tsx` and `MapPage.tsx`. |
| relation | `cited`, `crossField` | `library.json` | **MISSING** from `relation` and `v_relation`. Used by `MapPage.tsx` and `FamilyTree.tsx`. Relation evidence exists in `v_relation_evidence` but is not the same thing. |
| relation | `verified` | seed (`false` by default) | Set to `true` by a data step, or no edges show. |
| issue | `classics` | `library.json` (sample issues only) | No column. Sample only. |
| issue | publish date | `issue.published` (free text) | Free text by design. No date. |

---

## 6. Findings and risks

### 6.1 Grant regression in the patch (verify before cutover)

`20261106120000_patch_v_issue_number.sql` drops and recreates `v_issue`. The drop removes the revoke applied in `20261106100002` (`revoke all on ... v_issue ... from public, anon, authenticated`). The patch re-grants only `select to anon`. Supabase's default privileges normally give anon and authenticated full privileges on new relations in `public`, so `v_issue` may now carry write privileges for anon and authenticated. Check with `\dp v_issue` in psql. Fix: re-run `revoke all on v_issue from public, anon, authenticated;` before `grant select on v_issue to anon;`. This could not be verified without a database.

### 6.2 Views that do not gate on live status

These check only `sample`, not `status='live'`:

- `v_issue_story`, `v_company_post`, `v_storyline_step`, `v_node` (story_slug), `v_issue` (cover_story_slug), `v_front_placement` (slug values).

A story with no live version, or only a staging version, would still show its slug there. The frontend then links to a page that has no live row (`readLiveDoc` throws "has no live version"). Low risk at V1 if every referenced story has a live version. Add a live-status join if that is not guaranteed.

### 6.3 Raw tables still readable by anon

`story` (SELECT, `using (true)`) and `published_version` (SELECT, `status='live'`) are granted to anon. A sample story's slug, kind and `live_version_id` are readable from `story`, and any live `published_version` document is readable, bypassing the sample gate on the views. The contract acknowledges this (residual risk 4). It is out of scope for the cutover but should be decided before the views are the only documented path.

### 6.4 Contract drift

- `docs/handoffs/v1-schema-contract.md` gives `story_tag.status` as `approved, proposed, rejected`. The migration has `suggested, approved`. `v_live_story_tag` filters on `approved`, so it is unaffected, but the contract doc is stale.
- Moment `kind`: the DB uses `strip_panel`, the frontend uses `strip` (section 3, row 2).
- The `v_live_story_by_slug` function is in the contract. The frontend reads the view directly, as the contract's Section 5 allows.

### 6.5 Relations and verification

Nothing in `library.json` sets `verified`. The seed writes `false` for every relation, and `v_relation` requires `true`. Until a step sets it, the map has nodes and no edges.

---

## 7. Row counts and pagination

Counts are from the current JSON and the three paper files (`public/data/papers/*.json`). These are estimates for V1 (three real stories).

| View | V1 estimate | Notes |
|---|---|---|
| v_live_story | 3 | attention, size-shapes-life, h3-hexagons once live. |
| v_live_library_entry | 3 | Projection of `v_live_story`. |
| v_live_moment | 40 | Sum of `search-index` `papers[].moments`. |
| v_live_story_tag | up to 88 | Approved tags only. `search-index` tags sum to 88. |
| v_live_media_asset | about 78 | `.svg` references across the three paper files. |
| v_live_citation | about 18 | Roughly six `url` keys per paper file. Rough count. |
| v_live_fact | about 18 | Roughly six `figure` keys per paper file. Rough count. |
| v_tag | 93 | |
| v_facet | 13 | |
| v_node | 22 | |
| v_relation | 0 today, 12 max | Gated on `verified`. |
| all others | under 25 each | Editorial tables are small. |

**None reaches the default 1000-row PostgREST limit at V1.** `v_live_moment` is the only view that could, at about 13 moments per paper, which needs roughly 75 live papers.

If it ever does: paginate with keyset on `(story_slug, key)`, which is unique for live rows because a story has one live version and `(published_version_id, key)` is unique. Use `position` as the display sort with `NULLS LAST`, and add `key` as the tiebreaker. Use `range` only for a one-off full read. Do not paginate the other views at V1 scale.

---

## 8. Open decisions

1. Sample-story path (section 3.1): publish samples with `sample = true` and add a sample-inclusive view, or keep the file shell for samples.
2. Site metadata: add a `site_settings` singleton and `v_site`, or keep `site.json` as a file.
3. Tag lineage and facet description: add `tag.parent` and `facet.description` columns, or derive lineage in the loader from `aliases`/`facet` (not possible for `parent`, which is not in any other column).
4. Node `blurb`/`short` and relation `cited`/`crossField`: add columns, or drop the UI that uses them.
5. Relation verification: who sets `verified = true`, and when.
6. Whether to re-apply the `v_issue` revoke (section 6.1) in a new patch migration.
