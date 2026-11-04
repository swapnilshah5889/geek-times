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

## Today (JSON files; the library drives the site)

Follow `convert-paper` steps 6–8. In short:
1. The story file is at `public/data/papers/<slug>.json` and has passed `explain-source`, `fact-check` and
   `tag-story`.
2. Add `{slug, title, dataUrl}` to `public/data/site.json` → `papers`.
3. Add or replace the story in `public/data/library.json` (`stories`, its issue's `stories`, optionally `front`, and its
   `nodes` and `relations`). The front page reads the library, not `defaultPaper`.
4. `npm run data` (it must pass), then `npm run build`.
5. Check the front page, the story, the issue, the map, the feed and search at 1280px and 375px.
6. Commit on the branch the owner approved (ask before creating one) and open a PR, or give the compare link if the
   GitHub CLI is not signed in. The owner merges. Never push to `main`.

## After content model v2 (roadmap item 3)

Issues become their own records (`volume`, `number`, `title`, `theme`, `editorNote`, `publishedAt`, `stories` with
roles). Assemble one by picking the week's best published stories, choosing the lead (the most visual, broadest
appeal), and adding vault picks suggested by the graph (unexplained or old nodes with many links). Then write a
2–3 sentence editor's note.
