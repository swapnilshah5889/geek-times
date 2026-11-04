---
name: fact-check
description: Verify every real number, quote, section anchor and paper-basis tag in a Geeky Times story against the original source before it is published.
---

# Fact-check a story

Nothing marked as evidence ships unchecked. Invented teaching numbers (illustration blocks) aren't fact-checked, but
they must be labelled as invented.

## What to check

| Item | Where it is | Pass when |
|---|---|---|
| Evidence numbers | `facts[]`, the evidence chapter, any figure in captions | The exact value appears in the source at the linked section |
| Section links | `source.url`, tag `evidence` | The anchor exists (e.g. `#S3.SS2.SSS2`) and that section supports the claim |
| Paper-basis tags | `tags[]` with `basis: "paper"` | The linked section states it |
| Names | authors, affiliations, venue, year | They match the source's title page / metadata |
| Trust level | source and facts | Blog numbers are marked company-reported; preprints aren't called peer-reviewed |

## How

1. Fetch the source's readable version (arXiv HTML has anchors in its table-of-contents links). For blogs, use the
   live page and its archived copy.
2. For each claim, find the sentence. Record the short exact phrase and the anchor id.
3. If something can't be confirmed, change it: weaken the wording, mark it `background`, or remove it. Don't fill
   gaps from memory.
   - Example from the first story: the current arXiv version doesn't print "NIPS 2017", so the venue tag is
     `background`.
4. Re-run `npm run data`. It checks that `paper`-basis tags have evidence links into the source URL.

## Output

A short list for the PR description: each claim, its exact phrase, its anchor, and pass/changed/removed.
