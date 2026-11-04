# Prompt: infer tags for a paper

Used by the paper-to-issue converter. Fill in the `{{…}}` placeholders. Validate the model's output with
`npm run data` after writing it into the paper's JSON. The rules are in [`docs/tagging.md`](../docs/tagging.md).

---

You are tagging a research paper for The Geeky Times, a site that explains research to anyone, kids included.
Readers will find papers by searching and browsing these tags, so be thorough, specific and honest.

## Inputs

**Paper URL (arXiv HTML):** {{paper_url}}

**Paper text, with section anchors** (each heading is marked `[#anchor]`):

```
{{paper_text_with_anchors}}
```

**Tag vocabulary** (facets, then tags with ids, labels, parents and aliases):

```json
{{tags_json}}
```

## What to do

1. Read the whole paper. Note the field and area, the ideas it introduces or depends on, named techniques, tasks, datasets,
   metrics, authors and their affiliations.
2. For each idea, find the best tag in the vocabulary. Match on label **and** aliases. Prefer the most specific tag; parents
   are implied.
3. Only when nothing fits, propose a new tag. Put an id `<facet>/<lowercase-slug>` in `tag`, and a `proposed` object with
   `label`, optional `parent` (an existing id in the same facet) and `aliases`.
4. Give each tag:
   - `relevance` (0–1):
     - 1: what the paper is about.
     - 0.7–0.9: a main part.
     - 0.4–0.6: a supporting idea.
     - 0.2–0.3: a detail.
   - `basis`:
     - `paper`, with `evidence` = `{{paper_url}}#<anchor>` for the section that supports it. The bare URL is only
       for authors and affiliations.
     - `background`, for well-known context the paper doesn't state (later impact, real-world uses, a venue not printed).
     - `editorial`, for kid-friendly `everyday` themes only.
5. Cover these facets when they apply: field, area, concept, technique, task, dataset, metric, use, impact,
   organization, author, venue, everyday.
   - Always include every author.
   - Always include at least two `everyday` themes a child might search for.
   - Aim for 30–60 tags.
6. Don't invent anything. Leave out `impact` and `use` unless they're widely known and true. If unsure, leave it out.

## Output

Return **only** a JSON array, no commentary. Every item has this shape:

```json
{
  "tag": "concept/self-attention",
  "relevance": 1,
  "basis": "paper",
  "evidence": "{{paper_url}}#S4",
  "source": "ai",
  "status": "suggested"
}
```

A proposed new tag adds:

```json
"proposed": { "label": "Sparse attention", "parent": "concept/attention", "aliases": ["sparse transformer"] }
```

Before answering, check that:
- No tag id appears twice.
- Every `paper` tag has an evidence link to a real section anchor.
- `relevance` is between 0 and 1.
- `source` is `"ai"` and `status` is `"suggested"` on every item.
