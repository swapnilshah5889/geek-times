-- Preview/live status gate (branch v1).
-- Context: stories are published to the DB as `preview` (visible in local dev only, via an env flag in the
-- loader) and later approved to `live` (visible on the hosted site). The hosted site keeps reading v_live_*;
-- dev reads a parallel set of v_preview_* views. This migration adds:
--
--   1. 'preview' to the allowed values of published_version.status.
--   2. v_preview_* views mirroring v_live_* (same projection, same sample = false gate), with the status
--      gate widened from 'live' to 'preview' + 'live'.
--   3. v_preview_story_by_slug(text), mirroring v_live_story_by_slug(text).
--   4. approve_version(text): flips the newest preview version of a slug to live (service_role only).
--   5. Grants hardening for every new object, following 20261106100002 / 20261107120000.
--
-- Additive only. Idempotent: drop constraint if exists, create or replace view, drop function if exists then
-- create or replace function, drop policy if exists then create. Drops no existing view, table or column.
-- Does NOT change any v_live_* view, filter or grant. Does NOT alter published_version columns.
--
-- Design notes:
-- * One version per story is shown. If a story has both a preview and a live version, only the winning one
--   (preview first, then newest id) feeds every v_preview_* view, so extracted rows (moments, facts, ...)
--   never mix two versions of the same story.
-- * Preview rows are visible to anon through these views by design (dev reads with the publishable key; the
--   gate is client-side). v_preview_story and v_preview_library_entry are security_invoker, so anon needs a
--   SELECT policy on preview rows of published_version; it is added below.
-- * The one-live-per-story unique index only covers status = 'live', so several preview rows may coexist.

-- ---------------------------------------------------------------------------
-- 1. Status check constraint: ('staging', 'live', 'retired') -> ('staging', 'preview', 'live', 'retired')
--    The init migration declared the check inline, so Postgres named it published_version_status_check.
-- ---------------------------------------------------------------------------

alter table published_version drop constraint if exists published_version_status_check;
alter table published_version
  add constraint published_version_status_check
  check (status in ('staging', 'preview', 'live', 'retired'));

-- Anon may read preview rows too (live is already covered by published_version_public_read_live, which is kept).
drop policy if exists published_version_public_read_preview on published_version;
create policy published_version_public_read_preview on published_version
  for select to anon
  using (status = 'preview');

-- ---------------------------------------------------------------------------
-- 2. Preview views
--    "Winning version" predicate used by every view below: the preview version if one exists, else the live
--    one; newest id breaks ties.
-- ---------------------------------------------------------------------------

create or replace view v_preview_story with (security_invoker = true) as
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
where pv.status in ('preview', 'live') and s.sample = false
  and pv.id = (
    select w.id from published_version w
    where w.story_id = s.id and w.status in ('preview', 'live')
    order by (w.status = 'preview') desc, w.id desc
    limit 1
  );

create or replace view v_preview_library_entry with (security_invoker = true) as
select story_slug, library_entry
from v_preview_story;

create or replace view v_preview_moment as
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
where pv.status in ('preview', 'live') and s.sample = false
  and pv.id = (
    select w.id from published_version w
    where w.story_id = s.id and w.status in ('preview', 'live')
    order by (w.status = 'preview') desc, w.id desc
    limit 1
  );

create or replace view v_preview_fact as
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
where pv.status in ('preview', 'live') and s.sample = false
  and pv.id = (
    select w.id from published_version w
    where w.story_id = s.id and w.status in ('preview', 'live')
    order by (w.status = 'preview') desc, w.id desc
    limit 1
  );

-- Mirrors v_live_media_asset (the live view is named v_live_media_asset; the preview twin is v_preview_media).
create or replace view v_preview_media as
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
where pv.status in ('preview', 'live') and s.sample = false
  and pv.id = (
    select w.id from published_version w
    where w.story_id = s.id and w.status in ('preview', 'live')
    order by (w.status = 'preview') desc, w.id desc
    limit 1
  );

create or replace view v_preview_citation as
select
  s.slug        as story_slug,
  c.anchor,
  c.url,
  c.label,
  c.context
from citation c
join published_version pv on pv.id = c.published_version_id
join story s             on s.id = pv.story_id
where pv.status in ('preview', 'live') and s.sample = false
  and pv.id = (
    select w.id from published_version w
    where w.story_id = s.id and w.status in ('preview', 'live')
    order by (w.status = 'preview') desc, w.id desc
    limit 1
  );

create or replace view v_preview_story_field as
select
  s.slug        as story_slug,
  f.slug        as field_slug,
  f.label       as field_label,
  sf.position
from story_field sf
join published_version pv on pv.id = sf.published_version_id
join story s             on s.id = pv.story_id
join field f            on f.id = sf.field_id
where pv.status in ('preview', 'live') and s.sample = false
  and pv.id = (
    select w.id from published_version w
    where w.story_id = s.id and w.status in ('preview', 'live')
    order by (w.status = 'preview') desc, w.id desc
    limit 1
  );

-- ---------------------------------------------------------------------------
-- 3. Preview by-slug function (same signature and security as v_live_story_by_slug)
--    v_preview_story already yields one winning version per story (preview wins over live).
-- ---------------------------------------------------------------------------

drop function if exists v_preview_story_by_slug(text) cascade;

create or replace function v_preview_story_by_slug(p_slug text)
returns setof v_preview_story
language sql
stable
security invoker
set search_path = public, pg_temp
as $$
  select * from v_preview_story
  where story_slug = p_slug
  order by version_created_at desc
  limit 1;
$$;

-- ---------------------------------------------------------------------------
-- 4. approve_version(target_slug): preview -> live
--    security invoker; runs from the CLI with the service role, never from the browser. A function body is
--    one transaction, so any failure rolls everything back.
--    Mirrors publish_version: the current live version is retired first (the one-live-per-story unique index
--    would otherwise reject the flip) and story.live_version_id is pointed at the approved version.
-- ---------------------------------------------------------------------------

drop function if exists approve_version(text) cascade;

create or replace function approve_version(target_slug text)
returns bigint
language plpgsql
volatile
security invoker
set search_path = public, pg_temp
as $$
declare
  v_id       bigint;
  v_story_id bigint;
begin
  select id, story_id into v_id, v_story_id
    from published_version
   where story_slug = target_slug and status = 'preview'
   order by id desc
   limit 1
     for update;

  if v_id is null then
    raise exception 'approve_version: no preview version exists for slug %', target_slug;
  end if;

  update published_version set status = 'retired' where story_id = v_story_id and status = 'live';
  update published_version set status = 'live'    where id = v_id;
  update story set live_version_id = v_id where id = v_story_id;

  return v_id;
end;
$$;

-- ---------------------------------------------------------------------------
-- 5. Grants hardening
-- ---------------------------------------------------------------------------

revoke all on
  v_preview_story, v_preview_library_entry,
  v_preview_moment, v_preview_fact, v_preview_media, v_preview_citation, v_preview_story_field
  from public, anon, authenticated;

grant select on
  v_preview_story, v_preview_library_entry,
  v_preview_moment, v_preview_fact, v_preview_media, v_preview_citation, v_preview_story_field
  to anon;

revoke all on function v_preview_story_by_slug(text) from public, anon, authenticated;
grant execute on function v_preview_story_by_slug(text) to anon;

-- Service role only: never anon, never authenticated.
revoke all on function approve_version(text) from public, anon, authenticated;
grant execute on function approve_version(text) to service_role;

-- ---------------------------------------------------------------------------
-- Checks after apply (run by hand).
-- ---------------------------------------------------------------------------

-- constraint (must show all four statuses):
-- select pg_get_constraintdef(oid) from pg_constraint where conname = 'published_version_status_check';

-- no story appears twice in the preview view (must return zero rows):
-- select story_slug from v_preview_story group by story_slug having count(*) > 1;

-- every live story is also in the preview view (must return zero rows):
-- select story_slug from v_live_story except select story_slug from v_preview_story;
