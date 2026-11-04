---
name: publish-issue
description: Add finished stories to The Geeky Times and assemble them into an issue (lead, features, briefs, vault), today with JSON files and later through the review pipeline.
---

# Publish stories and assemble an issue

## Concepts (see `docs/product-plan.md`)

- Stories publish **as soon as they're approved**. Issues are a weekly curated package of what went live, plus
  1–2 "From the vault" classics.
- Issue roles:
  - `lead`: exactly one
  - `feature`: 2–5
  - `brief`: optional, a snack-only explainer
  - `vault`: a classic
- A volume is a year. Volume 0 holds launch special editions of classic papers.
- Keep two dates apart: the source's original year, and our publish date.

## Today (JSON, before content model v2)

1. The story file is at `public/data/papers/<slug>.json` and has passed `explain-source`, `fact-check` and
   `tag-story`.
2. Add `{slug, title, dataUrl}` to `public/data/site.json` → `papers`. Set `defaultPaper` to make it the front-page
   lead.
3. `npm run data` (it must pass), then `npm run build`.
4. Check the front page, the story, the feed and search at 1280px and 375px.
5. Commit on `feature/<slug>` and open a PR. The owner merges. Never push to `main`.

## After content model v2 (roadmap item 3)

Issues become their own records (`volume`, `number`, `title`, `theme`, `editorNote`, `publishedAt`, `stories` with
roles). Assemble one by picking the week's best published stories, choosing the lead (the most visual, broadest
appeal), and adding vault picks suggested by the graph (unexplained or old nodes with many links). Then write a
2–3 sentence editor's note.
