-- Editorial and collections layer: volumes, issues, companies, storylines, the map graph
-- (fields, nodes, relations, their evidence), front-page placement and field tags on versions.
-- Contract: docs/handoffs/v1-schema-contract.md (Agent B). Decisions 15, 16, 24, 30, 31, 34, 38, 48.
--
-- Additive only: this migration creates new tables and never alters or drops existing objects.
-- Depends on the init migration (story, published_version) and on Agent A's migration (source).
--
-- No foreign keys (decisions 30 and 38). Every *_id column holds another row's id and is indexed.
-- Integrity comes from the publish transaction, the unique / check / not-null constraints here,
-- and the orphan audit at the end of this file. Public reads go through Agent D's views only.
-- No seed data: the importer (Agent C) fills these tables from public/data/library.json.
-- Primary keys are `bigint generated always as identity`; enumerations are text + CHECK.

-- ---------------------------------------------------------------------------
-- Collections: volume > issue > issue_story (stories carry no issue or date of ours, decision 31)
-- ---------------------------------------------------------------------------

create table volume (
  id          bigint generated always as identity primary key,
  slug        text not null unique,
  title       text not null,
  kind        text not null check (kind in ('regular', 'special')),
  created_at  timestamptz not null default now()
);

create table issue (
  id              bigint generated always as identity primary key,
  slug            text not null unique,   -- the url key, e.g. "002" or "special-3"
  number          text not null,          -- the display label on the masthead: "002" or "Special 3"
  volume_id       bigint not null,   -- volume.id
  title           text not null,
  color           text,
  published       text,              -- free-form today; promote to date in a later batch
  cover_story_id  bigint,            -- story.id, nullable
  sample          boolean not null default false,
  position        int not null,      -- order within the volume (importer uses array order)
  created_at      timestamptz not null default now()
);
create index issue_volume_id_idx on issue (volume_id);
create index issue_cover_story_id_idx on issue (cover_story_id);

create table issue_story (
  id          bigint generated always as identity primary key,
  issue_id    bigint not null,       -- issue.id
  story_id    bigint not null,       -- story.id
  position    int not null,
  created_at  timestamptz not null default now(),
  unique (issue_id, story_id),
  unique (issue_id, position)
);
create index issue_story_issue_id_idx on issue_story (issue_id);
create index issue_story_story_id_idx on issue_story (story_id);

-- ---------------------------------------------------------------------------
-- Companies: a company publishes posts (stories) and claims to be built on graph nodes
-- ---------------------------------------------------------------------------

create table company (
  id              bigint generated always as identity primary key,
  slug            text not null unique,
  name            text not null,     -- plain name, never a logo (decision 16)
  sector          text,
  blurb           text,
  posts_followed  int,
  -- Placeholder strings for not-yet-written posts. Presentation only; kept as jsonb on purpose.
  coming          jsonb,
  sample          boolean not null default false,
  created_at      timestamptz not null default now()
);

create table company_post (
  id          bigint generated always as identity primary key,
  company_id  bigint not null,       -- company.id
  story_id    bigint not null,       -- story.id
  position    int not null,
  created_at  timestamptz not null default now(),
  unique (company_id, story_id),
  unique (company_id, position)
);
create index company_post_company_id_idx on company_post (company_id);
create index company_post_story_id_idx on company_post (story_id);

create table company_built_on (
  id          bigint generated always as identity primary key,
  company_id  bigint not null,       -- company.id
  node_id     bigint not null,       -- node.id
  position    int not null,
  created_at  timestamptz not null default now(),
  unique (company_id, node_id),
  unique (company_id, position)
);
create index company_built_on_company_id_idx on company_built_on (company_id);
create index company_built_on_node_id_idx on company_built_on (node_id);

-- ---------------------------------------------------------------------------
-- Storylines: guided "How X evolved" paths through the graph
-- ---------------------------------------------------------------------------

create table storyline (
  id          bigint generated always as identity primary key,
  slug        text not null unique,
  title       text not null,
  sample      boolean not null default false,
  created_at  timestamptz not null default now()
);

create table storyline_step (
  id            bigint generated always as identity primary key,
  storyline_id  bigint not null,     -- storyline.id
  position      int not null,
  year          text,                -- text: "1997", "2018 →"
  label         text,
  current       boolean not null default false,
  story_id      bigint,              -- story.id, nullable: not every step is a story we explain
  created_at    timestamptz not null default now(),
  unique (storyline_id, position)
);
create index storyline_step_storyline_id_idx on storyline_step (storyline_id);
create index storyline_step_story_id_idx on storyline_step (story_id);

-- ---------------------------------------------------------------------------
-- Map: fields (clouds), graph nodes (sources), relations (typed edges) and their evidence
-- ---------------------------------------------------------------------------

create table field (
  id          bigint generated always as identity primary key,
  slug        text not null unique,  -- short code, the public key (ai, bio, space, physics, sw)
  label       text not null,
  color       text,
  -- Map cluster coordinates on the 800 x 600 map: { cx, cy, rx, ry, labelX, labelY }.
  -- Presentation only, kept together with the field row on purpose.
  cluster     jsonb,
  created_at  timestamptz not null default now()
);

create table node (
  id          bigint generated always as identity primary key,
  slug        text not null unique,  -- library node id, e.g. 'transformer', 'lstm'
  title       text not null,
  authors     text,
  year        int,
  field_id    bigint not null,       -- field.id
  kind        text not null check (kind in ('paper', 'blog')),
  x           int,
  y           int,
  story_id    bigint,                -- story.id when we have explained it, nullable
  sample      boolean not null default false,
  created_at  timestamptz not null default now()
);
create index node_field_id_idx on node (field_id);
create index node_story_id_idx on node (story_id);

create table relation (
  id              bigint generated always as identity primary key,
  source_node_id  bigint not null,   -- node.id
  target_node_id  bigint not null,   -- node.id
  kind            text not null check (kind in ('builds_on', 'improves_on', 'uses_method', 'cited', 'family')),
  note            text,
  -- Public view (Agent D) shows only verified = true and sample = false.
  verified        boolean not null default false,
  sample          boolean not null default false,
  created_at      timestamptz not null default now(),
  unique (source_node_id, target_node_id, kind)
);
create index relation_source_node_id_idx on relation (source_node_id);
create index relation_target_node_id_idx on relation (target_node_id);

create table relation_evidence (
  id           bigint generated always as identity primary key,
  relation_id  bigint not null,      -- relation.id
  source_id    bigint,               -- source.id (Agent A), nullable: a bare url is allowed
  url          text,
  note         text,
  created_at   timestamptz not null default now()
);
create index relation_evidence_relation_id_idx on relation_evidence (relation_id);
create index relation_evidence_source_id_idx on relation_evidence (source_id);

-- ---------------------------------------------------------------------------
-- Front page: one settings row. Slots change together editorially, so they live in one jsonb document.
-- Shape of `data` (matches library.json.front). Story and field values are SLUGS, not ids,
-- and are not covered by the orphan audit; the publish validator must check them.
--   {
--     "lead":        "<story slug>",
--     "aside":       ["<story slug>", ...],
--     "more":        ["<story slug>", ...],
--     "topics":      [{ "field": "<field slug>", "label": "...", "stories": ["<story slug>", ...] }, ...],
--     "real":        ["<story slug>", ...],
--     "storylines":  ["<storyline slug>", ...],
--     "vault":       "<story slug>",
--     "onThisDay":   { "year": "...", "text": "...", "story": "<story slug>" }
--   }
-- ---------------------------------------------------------------------------

create table front_placement (
  id          bigint generated always as identity primary key,
  key         text not null unique default 'current',  -- always 'current' for now
  data        jsonb not null,
  created_at  timestamptz not null default now()
);

comment on column front_placement.data is
  'Front-page layout (library.json.front). Story and field references are slugs. Shape is documented in the migration header.';

-- ---------------------------------------------------------------------------
-- Field tags on a published version (library.stories[].fields[] is per-version metadata)
-- ---------------------------------------------------------------------------

create table story_field (
  id                    bigint generated always as identity primary key,
  published_version_id  bigint not null,  -- published_version.id
  field_id              bigint not null,  -- field.id
  position              int not null,
  created_at            timestamptz not null default now(),
  unique (published_version_id, field_id),
  unique (published_version_id, position)
);
create index story_field_published_version_id_idx on story_field (published_version_id);
create index story_field_field_id_idx on story_field (field_id);

comment on column field.cluster is
  'Map cluster coordinates { cx, cy, rx, ry, labelX, labelY }. Presentation only; kept with the field row on purpose.';

-- ---------------------------------------------------------------------------
-- Row-level security: on for every new table, with no public policy.
-- Public reads go through Agent D's views (security_invoker). Raw tables stay invisible to anon.
-- ---------------------------------------------------------------------------

alter table volume enable row level security;
alter table issue enable row level security;
alter table issue_story enable row level security;
alter table company enable row level security;
alter table company_post enable row level security;
alter table company_built_on enable row level security;
alter table storyline enable row level security;
alter table storyline_step enable row level security;
alter table field enable row level security;
alter table node enable row level security;
alter table relation enable row level security;
alter table relation_evidence enable row level security;
alter table front_placement enable row level security;
alter table story_field enable row level security;

-- Supabase's default grants give anon and authenticated full privileges on new tables. Remove them.
revoke all on volume, issue, issue_story, company, company_post, company_built_on,
  storyline, storyline_step, field, node, relation, relation_evidence,
  front_placement, story_field
  from public, anon, authenticated;

-- Only the service role (publish CLI / importer, server side) writes these tables.
grant select, insert, update, delete on volume, issue, issue_story, company, company_post, company_built_on,
  storyline, storyline_step, field, node, relation, relation_evidence,
  front_placement, story_field
  to service_role;

-- Identity sequences: the service role needs them to insert. Anon and authenticated get none.
revoke all on sequence volume_id_seq, issue_id_seq, issue_story_id_seq, company_id_seq,
  company_post_id_seq, company_built_on_id_seq, storyline_id_seq, storyline_step_id_seq,
  field_id_seq, node_id_seq, relation_id_seq, relation_evidence_id_seq,
  front_placement_id_seq, story_field_id_seq
  from public, anon, authenticated;

grant usage, select on sequence volume_id_seq, issue_id_seq, issue_story_id_seq, company_id_seq,
  company_post_id_seq, company_built_on_id_seq, storyline_id_seq, storyline_step_id_seq,
  field_id_seq, node_id_seq, relation_id_seq, relation_evidence_id_seq,
  front_placement_id_seq, story_field_id_seq
  to service_role;

-- ---------------------------------------------------------------------------
-- Orphan audit (decision 38). Run after every apply and before every publish.
-- Each query must return zero rows. Nullable reference columns are filtered with IS NOT NULL.
-- Run these by hand against the database; they are comments so the migration itself stays additive.
-- ---------------------------------------------------------------------------

-- orphan audit: issue.volume_id must resolve
-- select i.id from issue i left join volume v on v.id = i.volume_id where v.id is null;

-- orphan audit: issue.cover_story_id must resolve when set
-- select i.id from issue i left join story s on s.id = i.cover_story_id where i.cover_story_id is not null and s.id is null;

-- orphan audit: issue_story.issue_id must resolve
-- select x.id from issue_story x left join issue i on i.id = x.issue_id where i.id is null;

-- orphan audit: issue_story.story_id must resolve
-- select x.id from issue_story x left join story s on s.id = x.story_id where s.id is null;

-- orphan audit: company_post.company_id must resolve
-- select x.id from company_post x left join company c on c.id = x.company_id where c.id is null;

-- orphan audit: company_post.story_id must resolve
-- select x.id from company_post x left join story s on s.id = x.story_id where s.id is null;

-- orphan audit: company_built_on.company_id must resolve
-- select x.id from company_built_on x left join company c on c.id = x.company_id where c.id is null;

-- orphan audit: company_built_on.node_id must resolve
-- select x.id from company_built_on x left join node n on n.id = x.node_id where n.id is null;

-- orphan audit: storyline_step.storyline_id must resolve
-- select x.id from storyline_step x left join storyline s on s.id = x.storyline_id where s.id is null;

-- orphan audit: storyline_step.story_id must resolve when set
-- select x.id from storyline_step x left join story s on s.id = x.story_id where x.story_id is not null and s.id is null;

-- orphan audit: node.field_id must resolve
-- select n.id from node n left join field f on f.id = n.field_id where f.id is null;

-- orphan audit: node.story_id must resolve when set
-- select n.id from node n left join story s on s.id = n.story_id where n.story_id is not null and s.id is null;

-- orphan audit: relation.source_node_id must resolve
-- select r.id from relation r left join node n on n.id = r.source_node_id where n.id is null;

-- orphan audit: relation.target_node_id must resolve
-- select r.id from relation r left join node n on n.id = r.target_node_id where n.id is null;

-- orphan audit: relation_evidence.relation_id must resolve
-- select e.id from relation_evidence e left join relation r on r.id = e.relation_id where r.id is null;

-- orphan audit: relation_evidence.source_id must resolve when set
-- select e.id from relation_evidence e left join source s on s.id = e.source_id where e.source_id is not null and s.id is null;

-- orphan audit: story_field.published_version_id must resolve
-- select x.id from story_field x left join published_version pv on pv.id = x.published_version_id where pv.id is null;

-- orphan audit: story_field.field_id must resolve
-- select x.id from story_field x left join field f on f.id = x.field_id where f.id is null;
