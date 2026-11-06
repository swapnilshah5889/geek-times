-- Story slice: `story` and `published_version` (decisions 30, 34, 38, 42, 48).
--
-- Additive only: this migration creates new objects and never drops or alters existing ones.
-- No foreign keys, by design (decisions 30 and 38): `*_id` columns hold another row's id and
-- queries join on them. Integrity comes from the publish function, the seed/publish CLI and
-- the orphan checks, not from REFERENCES clauses.
-- No seed data: stories are published by the seed/publish CLI with the service-role key.

-- Ids are `bigint generated always as identity` per decision 30; `serial` is deprecated in
-- Postgres for new work. Identity values are not externally meaningful (decision 35):
-- cross-table references travel as `slug` / `key` in exports and the publish CLI remaps them.
create table story (
  id              bigint generated always as identity primary key,
  slug            text not null unique,
  kind            text not null check (kind in ('paper', 'blog')),
  live_version_id bigint  -- nullable; points at published_version.id (no FK)
);

create table published_version (
  id             bigint generated always as identity primary key,
  story_id       bigint      not null,
  story_slug     text        not null,  -- denormalized so public reads need no join
  schema_version int         not null,
  status         text        not null default 'staging'
                 check (status in ('staging', 'live', 'retired')),
  document       jsonb       not null,  -- the full PaperDoc
  library_entry  jsonb       not null,  -- the live LibraryStory for this slug
  created_at     timestamptz not null default now()
);

-- `story.slug` is covered by its unique constraint.
create index published_version_story_slug_status_idx on published_version (story_slug, status);
create index published_version_story_id_status_idx on published_version (story_id, status);
create index story_live_version_id_idx on story (live_version_id);

-- One live version per story, enforced by the database.
create unique index published_version_one_live_per_story_idx
  on published_version (story_id) where status = 'live';

-- Row-level security: readers hold only the publishable (anon) key.
-- The service role bypasses RLS and is the only writer.
alter table story enable row level security;
alter table published_version enable row level security;

create policy story_public_read on story
  for select to anon
  using (true);

create policy published_version_public_read_live on published_version
  for select to anon
  using (status = 'live');

-- Defence in depth: Supabase's default grants give anon and authenticated full table
-- privileges. Remove them and grant back only the reads the policies above allow.
revoke all on story, published_version from anon, authenticated;
grant select on story to anon;
grant select on published_version to anon;

-- Atomic publish (decision 42): retire the current live version, promote the new one and
-- point the story at it, in one transaction. Only the seed/publish CLI calls this.
create or replace function publish_version(p_version_id bigint)
returns void
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
  v_story_id bigint;
  v_status   text;
begin
  select story_id, status into v_story_id, v_status
    from published_version where id = p_version_id for update;
  if v_story_id is null then raise exception 'no such version: %', p_version_id; end if;
  if v_status <> 'staging' then
    raise exception 'version % is %, not staging; only a staging version may be promoted', p_version_id, v_status;
  end if;
  update published_version set status = 'retired' where story_id = v_story_id and status = 'live';
  update published_version set status = 'live'    where id = p_version_id;
  update story set live_version_id = p_version_id where id = v_story_id;
end;
$$;

-- Postgres grants EXECUTE to PUBLIC by default, and Supabase grants it to anon and
-- authenticated as well. Revoke all of them; only service_role may publish.
revoke all on function publish_version(bigint) from public, anon, authenticated;
grant execute on function publish_version(bigint) to service_role;
