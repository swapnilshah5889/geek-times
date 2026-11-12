-- Supabase-only runtime cutover (branch v1).
-- Context: the browser already reads v_live_story / v_live_library_entry from Supabase. The frontend is being
-- cut over to read every other surface — home slots, feed, search, library shell, site metadata — from Supabase
-- views. File-backed content is going away. This migration closes the remaining gaps flagged by
-- docs/handoffs/supabase-view-inventory.md:
--
--   1. Normalize the v_issue grant regression left by 20261106120000_patch_v_issue_number.sql.
--   2. Add a singleton `site_settings` table + `v_site` view to carry site.json fields.
--   3. Add the small columns the frontend needs that no table currently has:
--        tag.parent, facet.description, node.blurb, node.short, relation.cited, relation.cross_field.
--      For each, CREATE OR REPLACE the public view that surfaces the base table and re-apply the standard
--      revoke-on-public / grant-select-to-anon grants defensively — as the audit flagged, the patch that
--      dropped+recreated v_issue did not re-apply the revoke.
--
-- Additive only. Idempotent where Postgres allows (add column if not exists, create table if not exists,
-- create or replace view, insert ... on conflict do nothing). Drops no view, table or column.
-- Does NOT change any `sample = false` or `verified = true` filter on existing views.
-- Does NOT grant anything to authenticated.

-- ---------------------------------------------------------------------------
-- 0. Grant hardening for v_issue (regression from 20261106120000_patch_v_issue_number.sql).
--    The patch dropped v_issue, which removed the batched revoke from 20261106100002, and re-granted only
--    select to anon. Default privileges in Supabase otherwise give anon/authenticated full access on new
--    relations in `public`. Normalize by re-running revoke on public,anon,authenticated and grant select
--    to anon.
-- ---------------------------------------------------------------------------

revoke all on v_issue from public, anon, authenticated;
grant select on v_issue to anon;

-- ---------------------------------------------------------------------------
-- 1. Site metadata: singleton `site_settings` + `v_site`.
--    Columns derived from public/data/site.json and the frontend's SiteConfig (src/types.ts):
--      schema_version, site_name, motto, tagline, nav_label, media_base_url, default_story_slug.
--    `papers` from site.json is not stored here: the live paper list comes from v_live_story.
-- ---------------------------------------------------------------------------

create table if not exists site_settings (
  id                  int primary key default 1 check (id = 1),  -- singleton
  schema_version      int  not null default 1,
  site_name           text not null,
  motto               text,
  tagline             text,
  nav_label           text,
  media_base_url      text,
  default_story_slug  text,
  created_at          timestamptz not null default now(),
  updated_at          timestamptz not null default now()
);

alter table site_settings enable row level security;

-- Seed the one row from public/data/site.json. Idempotent via the singleton PK.
insert into site_settings (
  id, schema_version, site_name, motto, tagline, nav_label, media_base_url, default_story_slug
) values (
  1,
  1,
  'The Geeky Times',
  'Research, in pictures.',
  'An independent illustrated science edition',
  '✦   The illustrated paper',
  'media/',
  'attention-is-all-you-need'
) on conflict (id) do nothing;

-- Public view: every field is read-only to anon. security_invoker=true: anon reads site_settings under
-- the policy we add below, matching the pattern on v_live_story / v_live_library_entry.
create or replace view v_site with (security_invoker = true) as
select
  schema_version,
  site_name,
  motto,
  tagline,
  nav_label,
  media_base_url,
  default_story_slug
from site_settings
where id = 1;

-- Anon read policy on the base table so the security_invoker view can resolve for anon.
-- Idempotent via `drop policy if exists` then create.
drop policy if exists site_settings_public_read on site_settings;
create policy site_settings_public_read on site_settings for select to anon using (true);

revoke all on site_settings from public, anon, authenticated;
grant select on site_settings to anon;

revoke all on v_site from public, anon, authenticated;
grant select on v_site to anon;

-- ---------------------------------------------------------------------------
-- 2. Missing columns, with view re-definitions.
--    After every CREATE OR REPLACE VIEW we re-apply revoke-on-public / grant-select-to-anon defensively,
--    even though CREATE OR REPLACE VIEW normally keeps privileges — this is the same hardening pattern
--    the audit asked for after the v_issue regression.
-- ---------------------------------------------------------------------------

-- 2a. tag.parent (text, nullable) — tag lineage used by src/lib/tags.ts (tagLookup.lineage).
alter table tag add column if not exists parent text;

create or replace view v_tag as
select
  t.key,
  t.label,
  t.aliases,
  f.key         as facet_key,
  f.label       as facet_label,
  t.parent
from tag t
join facet f on f.id = t.facet_id;

revoke all on v_tag from public, anon, authenticated;
grant select on v_tag to anon;

-- 2b. facet.description (text, nullable) — present in tags.json, currently nowhere in the DB.
alter table facet add column if not exists description text;

create or replace view v_facet as
select key, label, position, description
from facet;

revoke all on v_facet from public, anon, authenticated;
grant select on v_facet to anon;

-- 2c. node.blurb, node.short (text, nullable) — used by FamilyTree.tsx and MapPage.tsx.
alter table node add column if not exists blurb text;
alter table node add column if not exists short text;

create or replace view v_node as
select
  n.slug,
  n.title,
  n.authors,
  n.year,
  n.kind,
  n.x,
  n.y,
  f.slug        as field_slug,
  s.slug        as story_slug,
  n.blurb,
  n.short
from node n
join field f           on f.id = n.field_id
left join story s      on s.id = n.story_id and s.sample = false
where n.sample = false;

revoke all on v_node from public, anon, authenticated;
grant select on v_node to anon;

-- 2d. relation.cited, relation.cross_field (bool, default false) — used by MapPage.tsx and FamilyTree.tsx.
-- The `verified = true` gate on v_relation is kept exactly as-is.
alter table relation add column if not exists cited        boolean not null default false;
alter table relation add column if not exists cross_field  boolean not null default false;

create or replace view v_relation as
select
  sn.slug       as source_node_slug,
  tn.slug       as target_node_slug,
  r.kind,
  r.note,
  r.cited,
  r.cross_field
from relation r
join node sn on sn.id = r.source_node_id and sn.sample = false
join node tn on tn.id = r.target_node_id and tn.sample = false
where r.verified = true and r.sample = false;

revoke all on v_relation from public, anon, authenticated;
grant select on v_relation to anon;

-- ---------------------------------------------------------------------------
-- 3. Checks after apply (run by hand; each must return zero rows unless noted).
-- ---------------------------------------------------------------------------

-- Singleton row check (must return exactly one row):
-- select id, site_name from site_settings;

-- Grant hardening check for every public view touched here (should report only anon):
-- select grantee, privilege_type from information_schema.role_table_grants
--  where table_schema = 'public' and table_name in ('v_site', 'v_issue', 'v_tag', 'v_facet', 'v_node', 'v_relation')
--  order by table_name, grantee;

-- Leak check: no sample node or unverified relation surfaces on v_relation (gate is unchanged).
-- select * from v_relation r
--  where not exists (select 1 from v_node n where n.slug = r.source_node_slug)
--     or not exists (select 1 from v_node n where n.slug = r.target_node_slug);
