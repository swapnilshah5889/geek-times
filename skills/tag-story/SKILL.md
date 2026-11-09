---
name: tag-story
description: Infer and review the many tags each Geeky Times story needs for search, topics and the graph, using the shared tag vocabulary.
---

> **Default model:** **small** (Haiku 5.5, Sonnet 4.x, Gemini Flash, GPT-4.1 mini) — prompts/tag-paper.md is deterministic. Fall back to larger only when the task genuinely needs it.

# Tag a story

Full rules: `docs/tagging.md`. Prompt template for automated tagging: `prompts/tag-paper.md`.

## Steps

1. Read `data/seed/tags.json` (facets, tags, parents, aliases). The app reads the approved vocabulary from Supabase; this seed is for the server-side import and recovery workflow.
2. Tag across every facet that applies: field, area, concept, technique, task, dataset, metric, use, impact,
   organization, author, venue, everyday. Aim for 30–60 tags.
3. Prefer existing ids, and match on aliases too. Pick the most specific tag; parents are implied.
4. Each tag needs:
   - `relevance` (1 = what it's about … 0.3 = a detail)
   - `basis`: `paper` with an `evidence` anchor link / `background` / `editorial`
   - `source` and `status`

   AI output is `source: "ai", status: "suggested"`.
5. For a new idea not in the vocabulary, propose it (`proposed: {label, parent, aliases}`). Do not add it to the seed or database until the owner approves it.
6. Always include every author and at least two `everyday` themes ordinary readers might search for. Avoid the literal phrases "kid-friendly" and "for kids" in user-facing labels or descriptions.
7. For blog posts, add the company under `organization` and, where it applies, `use` tags (real-world uses).
8. AI output must use `source: "ai", status: "suggested"`. The publish CLI rejects suggested tags, so the owner must review them and explicitly approve each accepted tag before seeding or publishing. Never auto-approve to make publishing pass.
9. The publisher mirrors owner-approved tags and fields transactionally with the story. Do not run `npm run seed:editorial` for a per-story preview; that global sync is reserved for separately reviewed editorial-table updates, after approval or through a dedicated safe workflow.
