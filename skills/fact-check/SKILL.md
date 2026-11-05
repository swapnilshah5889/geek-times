---
name: fact-check
description: Verify every real number, quote, section anchor and paper-basis tag in a Geeky Times story against the original source before it is published.
---

> **Default model:** **small** (Haiku 5.5, Sonnet 4.x, Gemini Flash, GPT-4.1 mini) — find a phrase, match a number. Fall back to larger only when the task genuinely needs it.

# Fact-check a story

Nothing marked as evidence ships unchecked. Invented teaching numbers (illustration blocks) aren't fact-checked, but
they must be labelled as invented.

## What to check

| Item | Where it is | Pass when |
|---|---|---|
| Evidence numbers | `facts[]`, the evidence chapter, any figure in captions | The exact value appears in the source at the linked section |
| Section links | `source.url`, tag `evidence` | The anchor exists (e.g. `#S3.SS2.SSS2`) and that section supports the claim. Blog posts: see Blog branch |
| Paper-basis tags | `tags[]` with `basis: "paper"` | The linked section states it |
| Names | authors, affiliations, venue, year | They match the source's title page / metadata |
| Claim kind | `facts[].claim` | `measured_result` only for what a test or experiment found; `model_design` for how something was built or argued (a derivation, a design choice, a definition) |
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

## Blog branch (company engineering posts)

Use this when the story's `kind` is `blog` (see `skills/convert-paper`, Blog branch). The same checks apply, with these
differences.

1. **Which version.** Check against the archived copy (`blog.archivedUrl`), because that is the version we record. Also
   open the live post. If the two differ in any number, name, or date, stop and re-check against the live post
   before you change the story.
2. **Anchors.** A blog has no arXiv paragraph anchors. A link's `#fragment` must match a heading or element id in the
   post. Confirm it exists and that the section supports the claim. If the post has no usable anchor, the link is only
   the post, so the fact's label must name the section and quote a short phrase (under 15 words). Record the phrase.
3. **Organization and date.** `blog.organization` matches the byline or blog name the post shows. `blog.published`
   matches the date printed on the post. If the post prints no date, say so in the list and use the archive's capture
   date as a last resort; do not guess.
4. **Trust.** `blog.trust` is `company_reported` every time. Never write "peer-reviewed", "independently verified" or
   "checked by" for a blog. Remove any such wording.
5. **Numbers.** Every `measured_result` must appear in the post with the same value, unit and comparison. Rewrite
   it as the company's own claim ("the company reports…"). A number the post does not state is removed, not estimated.
6. **Paper-basis tags.** The tag's `evidence` must point into the post (or its archive) and the section must state the
   tag. A `background` tag is not checked against the post.
7. **Footer.** The story page's footer line ("every number is company-reported") must stay in the blog layout.

The validator (`npm run data`) only checks structure: the blog block, the trust value, link prefixes and the presence of
a `source.url` on each measured result. It does not confirm any number. Only this check does.

## Output

A short list for the PR description: each claim, its exact phrase, its anchor, and pass/changed/removed. For a blog, also
the archive URL and the retrieval date.
