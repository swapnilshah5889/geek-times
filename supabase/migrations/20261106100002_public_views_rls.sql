-- Public read layer: the views anon reads, and the grants that hold them (decision 49).
-- Contract: docs/handoffs/v1-schema-contract.md, "Public reads (Agent D)". Decisions 34, 38, 42, 48, 49.
--
-- Additive only: creates views and one SQL function, and changes grants. It drops nothing and alters no table.
-- Runs after 20261106085857_init_story_slice.sql, 20261106100000_core_content_schema.sql (Agent A) and
-- 20261106100001_editorial_schema.sql (Agent B).
--
-- How public reads work (read before changing a grant or a view):
-- * Anon reads the normalized tables only through the views below. The raw tables that A and B create stay
--   invisible to anon: no grant, no policy. Authenticated gets nothing from this file.
-- * Most views are NOT security_invoker. A security_invoker view would need anon SELECT on its base tables,
--   which would expose them over REST. These views run with the migration owner's rights, so each view's
--   WHERE clause is the gate. Keep every predicate here in step with the table comments in A and B.
-- * v_live_story and v_live_library_entry are security_invoker = true. They read only story and
--   published_version, and anon already reads those under their own policies.
-- * Live means published_version.status = 'live'. Public means story.sample = false. A story version that is
--   staging or retired never appears, and a sample story never appears.
-- * Existing policies are KEPT, untouched, so the browser keeps working during this transition:
--     story_public_read                 (story, anon, using true)
--     published_version_public_read_live (published_version, anon, status = 'live')
--   src/data/source-supabase.ts reads published_version directly. It moves to v_live_story in a later batch.
--   No new policy is created here.
-- * Numeric ids are not returned by these views (decision 35). Rows are keyed by slug or key, and references
--   resolve to slugs or keys in the view.

-- ---------------------------------------------------------------------------
-- 1. Story views (security_invoker: anon reads story and live published_version under their own policies)
-- ---------------------------------------------------------------------------

create view v_live_story with (security_invoker = true) as
select
  s.slug                  as story_slug,
  s.kind,
  pv.schema_version,
  pv.headline,
  pv.accent,
  pv.dek,
  pv.summary,
  pv.page_title,
  pv.desk,
  pv.authors,
  pv.year,
  pv.trust,
  pv.minutes,
  pv.role,
  pv.note,
  pv.source_url,
  pv.source_archived_url,
  pv.document,
  pv.library_entry,
  pv.created_at           as version_created_at
from story s
join published_version pv on pv.story_id = s.id
where pv.status = 'live' and s.sample = false;

-- Transitional: the home-page overlay (story_slug, library_entry) for every live, non-sample story.
create view v_live_library_entry with (security_invoker = true) as
select story_slug, library_entry
from v_live_story;

-- ---------------------------------------------------------------------------
-- 2. Extracted rows of a live version (owner rights; gate: pv.status = 'live' and s.sample = false)
-- ---------------------------------------------------------------------------

create view v_live_moment as
select
  s.slug        as story_slug,
  m.key,
  m.kind,
  m.position,
  m.claim,
  m.trust,
  m.source_label,
  m.source_url,
  ma.path       as media_path,
  m.headline,
  m.text,
  m.ref
from moment m
join published_version pv on pv.id = m.published_version_id
join story s             on s.id = pv.story_id
left join media_asset ma on ma.id = m.media_asset_id
                        and ma.published_version_id = m.published_version_id
where pv.status = 'live' and s.sample = false;

create view v_live_fact as
select
  s.slug        as story_slug,
  f.block_id,
  f.position,
  f.figure,
  f.claim,
  f.text,
  f.source_label,
  f.source_url,
  ma.path       as media_path
from fact f
join published_version pv on pv.id = f.published_version_id
join story s             on s.id = pv.story_id
left join media_asset ma on ma.id = f.media_asset_id
                        and ma.published_version_id = f.published_version_id
where pv.status = 'live' and s.sample = false;

-- Only approved tags are public (the validator already enforces this on publish; the view checks it again).
create view v_live_story_tag as
select
  s.slug        as story_slug,
  t.key         as tag_key,
  t.label       as tag_label,
  st.relevance,
  st.basis,
  st.evidence,
  st.source_kind
from story_tag st
join published_version pv on pv.id = st.published_version_id
join story s             on s.id = pv.story_id
join tag t               on t.id = st.tag_id
where pv.status = 'live' and s.sample = false and st.status = 'approved';

create view v_live_citation as
select
  s.slug        as story_slug,
  c.anchor,
  c.url,
  c.label,
  c.context
from citation c
join published_version pv on pv.id = c.published_version_id
join story s             on s.id = pv.story_id
where pv.status = 'live' and s.sample = false;

create view v_live_media_asset as
select
  s.slug        as story_slug,
  ma.path,
  ma.kind,
  ma.width,
  ma.height,
  ma.alt
from media_asset ma
join published_version pv on pv.id = ma.published_version_id
join story s             on s.id = pv.story_id
where pv.status = 'live' and s.sample = false;

create view v_live_story_field as
select
  s.slug        as story_slug,
  f.slug        as field_slug,
  f.label       as field_label,
  sf.position
from story_field sf
join published_version pv on pv.id = sf.published_version_id
join story s             on s.id = pv.story_id
join field f            on f.id = sf.field_id
where pv.status = 'live' and s.sample = false;

-- ---------------------------------------------------------------------------
-- 3. Vocabulary (always readable in full: no sample flag, no version)
-- ---------------------------------------------------------------------------

create view v_facet as
select key, label, position
from facet;

create view v_tag as
select
  t.key,
  t.label,
  t.aliases,
  f.key         as facet_key,
  f.label       as facet_label
from tag t
join facet f on f.id = t.facet_id;

-- ---------------------------------------------------------------------------
-- 4. Editorial and collections (gate: sample = false where the table has the column)
-- ---------------------------------------------------------------------------

-- volume has no sample column, so every volume is public.
create view v_volume as
select slug, title, kind
from volume;

create view v_issue as
select
  i.slug,
  i.title,
  i.color,
  i.published,
  i.position,
  v.slug        as volume_slug,
  cs.slug       as cover_story_slug
from issue i
join volume v            on v.id = i.volume_id
left join story cs       on cs.id = i.cover_story_id and cs.sample = false
where i.sample = false;

create view v_issue_story as
select
  i.slug        as issue_slug,
  s.slug        as story_slug,
  ist.position
from issue_story ist
join issue i on i.id = ist.issue_id and i.sample = false
join story s on s.id = ist.story_id and s.sample = false;

create view v_company as
select slug, name, sector, blurb, posts_followed, coming
from company
where sample = false;

create view v_company_post as
select
  c.slug        as company_slug,
  s.slug        as story_slug,
  cp.position
from company_post cp
join company c on c.id = cp.company_id and c.sample = false
join story s  on s.id = cp.story_id and s.sample = false;

create view v_company_built_on as
select
  c.slug        as company_slug,
  n.slug        as node_slug,
  cb.position
from company_built_on cb
join company c on c.id = cb.company_id and c.sample = false
join node n    on n.id = cb.node_id and n.sample = false;

create view v_storyline as
select slug, title
from storyline
where sample = false;

create view v_storyline_step as
select
  sl.slug       as storyline_slug,
  sst.position,
  sst.year,
  sst.label,
  sst.current,
  s.slug        as story_slug
from storyline_step sst
join storyline sl       on sl.id = sst.storyline_id and sl.sample = false
left join story s       on s.id = sst.story_id and s.sample = false;

-- field has no sample column, so every field is public. Map cluster coordinates travel with it.
create view v_field as
select slug, label, color, cluster
from field;

create view v_node as
select
  n.slug,
  n.title,
  n.authors,
  n.year,
  n.kind,
  n.x,
  n.y,
  f.slug        as field_slug,
  s.slug        as story_slug
from node n
join field f           on f.id = n.field_id
left join story s      on s.id = n.story_id and s.sample = false
where n.sample = false;

-- A public edge never points at a sample node. Both endpoints must be public.
create view v_relation as
select
  sn.slug       as source_node_slug,
  tn.slug       as target_node_slug,
  r.kind,
  r.note
from relation r
join node sn on sn.id = r.source_node_id and sn.sample = false
join node tn on tn.id = r.target_node_id and tn.sample = false
where r.verified = true and r.sample = false;

create view v_relation_evidence as
select
  sn.slug       as source_node_slug,
  tn.slug       as target_node_slug,
  e.url,
  e.note
from relation_evidence e
join relation r on r.id = e.relation_id and r.verified = true and r.sample = false
join node sn    on sn.id = r.source_node_id and sn.sample = false
join node tn    on tn.id = r.target_node_id and tn.sample = false;

-- Front page: one settings row (decision 49, contract). Its data holds slugs, not ids.
create view v_front_placement as
select key, data
from front_placement
where key = 'current';

-- ---------------------------------------------------------------------------
-- 5. Public function: one live story by slug (contract: v_live_story_by_slug)
-- ---------------------------------------------------------------------------

create or replace function v_live_story_by_slug(p_slug text)
returns setof v_live_story
language sql
stable
security invoker
set search_path = public, pg_temp
as $$
  select * from v_live_story where story_slug = p_slug;
$$;

-- ---------------------------------------------------------------------------
-- 6. Grants
-- ---------------------------------------------------------------------------

grant usage on schema public to anon;

-- Targeted revokes on the NEW tables only (A and B). The init migration's tables are not touched.
-- Supabase's default privileges give anon and authenticated full access to new tables and views.
-- Tables from A are listed here by the names in the contract; a rename there fails this file.
revoke all on
  source, source_snapshot, story_source, citation, media_asset, facet, tag, story_tag, moment, fact,
  volume, issue, issue_story, company, company_post, company_built_on,
  storyline, storyline_step, field, node, relation, relation_evidence,
  front_placement, story_field
  from public, anon, authenticated;

-- Views: revoke the default grants, then grant SELECT to anon only.
revoke all on
  v_live_story, v_live_library_entry,
  v_live_moment, v_live_fact, v_live_story_tag, v_live_citation, v_live_media_asset, v_live_story_field,
  v_facet, v_tag,
  v_volume, v_issue, v_issue_story, v_company, v_company_post, v_company_built_on,
  v_storyline, v_storyline_step, v_field, v_node, v_relation, v_relation_evidence,
  v_front_placement
  from public, anon, authenticated;

grant select on
  v_live_story, v_live_library_entry,
  v_live_moment, v_live_fact, v_live_story_tag, v_live_citation, v_live_media_asset, v_live_story_field,
  v_facet, v_tag,
  v_volume, v_issue, v_issue_story, v_company, v_company_post, v_company_built_on,
  v_storyline, v_storyline_step, v_field, v_node, v_relation, v_relation_evidence,
  v_front_placement
  to anon;

revoke all on function v_live_story_by_slug(text) from public, anon, authenticated;
grant execute on function v_live_story_by_slug(text) to anon;

-- The init migration's grants and policies on story and published_version are NOT changed here.

-- ---------------------------------------------------------------------------
-- Checks after apply (run by hand; each must return zero rows unless noted).
-- A view's inner join drops a row silently when its reference does not resolve, so these list what a view hides.
-- ---------------------------------------------------------------------------

-- orphan audit (views): moment.published_version_id must resolve
-- select m.id from moment m left join published_version pv on pv.id = m.published_version_id where pv.id is null;

-- orphan audit (views): story_tag.tag_id must resolve
-- select st.id from story_tag st left join tag t on t.id = st.tag_id where t.id is null;

-- orphan audit (views): tag.facet_id must resolve
-- select t.id from tag t left join facet f on f.id = t.facet_id where f.id is null;

-- orphan audit (views): moment.media_asset_id resolves in the same version when set
-- select m.id from moment m where m.media_asset_id is not null and not exists (select 1 from media_asset ma where ma.id = m.media_asset_id and ma.published_version_id = m.published_version_id);

-- orphan audit (views): fact.media_asset_id resolves in the same version when set
-- select f.id from fact f where f.media_asset_id is not null and not exists (select 1 from media_asset ma where ma.id = f.media_asset_id and ma.published_version_id = f.published_version_id);

-- orphan audit (views): story_field.field_id must resolve
-- select sf.id from story_field sf left join field f on f.id = sf.field_id where f.id is null;

-- orphan audit (views): node.field_id must resolve (v_node joins field)
-- select n.id from node n left join field f on f.id = n.field_id where f.id is null;

-- leak check (must return zero rows): no sample story or non-live version is visible to anon
-- select story_slug from v_live_story where story_slug in (select slug from story where sample);

-- leak check (must return zero rows): every moment in the public view belongs to a story visible in v_live_story
-- select m.story_slug from v_live_moment m where not exists (select 1 from v_live_story s where s.story_slug = m.story_slug);
