---
name: tag-story
description: Infer and review the many tags each Geeky Times story needs for search, topics and the graph, using the shared tag vocabulary.
---

> **Default model:** **small** (Haiku 5.5, Sonnet 4.x, Gemini Flash, GPT-4.1 mini) — prompts/tag-paper.md is deterministic. Fall back to larger only when the task genuinely needs it.

# Tag a story

Full rules: `docs/tagging.md`. Prompt template for automated tagging: `prompts/tag-paper.md`.

## Steps

1. Read `public/data/tags.json` (facets, tags, parents, aliases).
2. Tag across every facet that applies: field, area, concept, technique, task, dataset, metric, use, impact,
   organization, author, venue, everyday. Aim for 30–60 tags.
3. Prefer existing ids, and match on aliases too. Pick the most specific tag; parents are implied.
4. Each tag needs:
   - `relevance` (1 = what it's about … 0.3 = a detail)
   - `basis`: `paper` with an `evidence` anchor link / `background` / `editorial`
   - `source` and `status`

   AI output is `source: "ai", status: "suggested"`.
5. For a new idea not in the vocabulary, propose it (`proposed: {label, parent, aliases}`). Add it to `tags.json` only
   once it's approved.
6. Always include every author and at least two kid-friendly `everyday` themes.
7. For blog posts, add the company under `organization` and, where it applies, `use` tags (real-world uses).
8. Run `npm run data`. Errors block the build; warnings list what's waiting for review.
9. Approve by setting `status: "approved"`. Only approved tags appear on the site.
