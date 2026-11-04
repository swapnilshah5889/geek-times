# Tagging papers

Every paper carries many tags, so readers can find it by what it's about, what it led to, who wrote it, or a
kid-friendly theme. Tags are inferred by the AI when it converts a paper into an issue, then reviewed by an editor.

## The pieces

| Piece | Today | Later (database) |
|---|---|---|
| Shared vocabulary | `public/data/tags.json` | `tag_facets`, `tags` (with `parent_id`, `aliases[]`) |
| A paper's tags | `tags` array in `public/data/papers/<slug>.json` | `paper_tags (paper_id, tag_id, relevance, basis, evidence_url, source, status)` |
| Search index | `public/data/search-index.json`, built by `npm run data` | a query: tag ids plus their ancestors, and full-text on title and summary |
| Rules check | `scripts/build-index.ts`, runs before `dev` and `build` | the same checks at import time, plus database constraints |

Types live in `src/types.ts`: `TagFacet`, `TagDef`, `TagVocabulary`, `PaperTag` and `SearchIndex`.

## Facets: what each tag group answers

| Facet | Question | Examples |
|---|---|---|
| `field` | Which branch of science? | Computer science, Biology |
| `area` | Which part of it? | Machine learning, Natural language processing |
| `concept` | Which ideas does it explain or rely on? | Attention, Embeddings, Recurrent neural networks |
| `technique` | Which named methods or models? | Transformer, Adam optimizer, Beam search |
| `task` | What job is being solved? | Machine translation, Constituency parsing |
| `dataset` | What data was used? | WMT 2014 English–German |
| `metric` | How were results scored? | BLEU score |
| `use` | Where do people meet this today? | Translation apps, Chatbots |
| `impact` | What did it lead to? | Large language models, GPT, BERT |
| `organization` | Where was it done? | Google Brain, University of Toronto |
| `author` | Who wrote it? | One tag per author |
| `venue` | Where was it published? | NeurIPS 2017 |
| `everyday` | What would a kid search for? | Language and words, Smart computers |

## Rules for every tag on a paper

1. **Use the vocabulary.** Reuse an existing tag id whenever one fits, including through its aliases. Only propose a new tag when
   nothing fits. Put it under `proposed` with a `label`, an optional `parent` and `aliases`. An editor adds it to
   `tags.json` before it can go live.
2. **Pick the most specific tag.** Tag `concept/self-attention`, not just `concept/attention`. Parents are found automatically
   (searching "Attention" finds papers tagged Self-attention).
3. **Score `relevance` from 0 to 1.**
   - 1: what the paper is about.
   - 0.7–0.9: a main part.
   - 0.4–0.6: a supporting idea.
   - 0.2–0.3: a detail mentioned in passing.
   Don't tag things that aren't actually there.
4. **Say where it comes from with `basis`.**
   - `paper`: stated in the paper. Needs `evidence`, a link to the exact section (arXiv HTML anchors like `#S3.SS2`,
     `#abstract1`). Use the plain paper URL only for front matter such as authors and affiliations.
   - `background`: well-known context that the paper itself doesn't state, like what it later led to, or a venue that isn't
     printed in this version.
   - `editorial`: our framing for readers (the `everyday` facet).
5. **Cover every facet that applies.** A typical paper gets 30–60 tags. Always include `field`, `area`, the main `concept`s and
   `task`, every `author`, and at least two `everyday` themes. Include `use` and `impact` when they're real and well known.
6. **No hype, no guesses.** Don't add `impact` or `use` tags you can't back up. For a new paper, leave `impact` empty.
7. **Mark AI output for review.** Set `source: "ai"` and `status: "suggested"`. Only `approved` tags are shown or searchable.

`npm run data` enforces the mechanical rules (known ids, relevance range, evidence for `paper` basis, no duplicates,
no approved tags missing from the vocabulary). It prints proposed and suggested tags as warnings, so the editor's queue is
visible.

## Editor review

1. Run `npm run data` and read the warnings.
2. For each proposed tag, either add it to `tags.json` (choose the facet, parent and aliases), or swap it for an existing id.
3. Spot-check `paper`-basis tags by opening their evidence links.
4. Change `status` to `approved`, or delete the tag.

The prompt the converter uses is in [`prompts/tag-paper.md`](../prompts/tag-paper.md).
