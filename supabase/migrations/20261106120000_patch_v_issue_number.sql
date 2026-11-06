-- Lead patch: v_issue was authored before `issue.number` was added. Add `number` to the view so
-- the masthead can render "Special 3" vs. just the url slug "special-3". `create or replace view`
-- cannot rearrange the column list in Postgres, so drop and recreate. Safe here: no stored procedure
-- or other view depends on it.

drop view if exists v_issue;

create view v_issue as
  select
    i.slug,
    i.number,
    i.title,
    i.color,
    i.published,
    i.position,
    v.slug as volume_slug,
    cs.slug as cover_story_slug
  from issue i
  join volume v on v.id = i.volume_id
  left join story cs on cs.id = i.cover_story_id and cs.sample = false
  where i.sample = false;

grant select on v_issue to anon;
