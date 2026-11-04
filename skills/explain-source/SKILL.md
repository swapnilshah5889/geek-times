---
name: explain-source
description: Turn a research paper or a company engineering blog post into a Geeky Times story (plain-language summary, picture story, comic strips, evidence cards) that a school kid can follow. Use when adding any new story.
---

# Explain a source as a Geeky Times story

The reference example is `public/data/papers/attention-is-all-you-need.json`. Match its tone, structure and honesty.

## 1. Read and understand

- Get the best readable version: arXiv HTML (`https://arxiv.org/html/<id>`), which has section anchors, the
  publisher page, or the blog post itself (also save a Wayback archive link for blogs).
- Write down, privately:
  - the problem
  - the key idea
  - how it works, in 4–6 steps
  - the evidence, with exact numbers and their section anchors
  - who wrote it, where, and when
- Note the trust level: peer-reviewed, preprint, or company-reported (a company blog's own numbers).

## 2. Find the one everyday example

Pick one concrete, visual example that carries the whole story. The Transformer story uses "The bat flew" (a bat
with wings vs a baseball bat). Reuse the **word-buddy** characters when words are involved. Invent new characters in
the same style otherwise.

## 3. Write the blocks (in this order)

1. **`lead`:** kicker, headline (`text` plus a red `accent` phrase), one-question deck, and a 1–2 slide slideshow of
   the everyday example.
2. **`story`:** four chapters with `part` set to *The problem / The idea / The solution / The evidence*. Chapters 1–3
   are `provenance: illustration`. Chapter 4 is `evidence`, with a real number and a section link.
3. **`comic`:** "How the machine actually works". 4–6 strips × 3 panels. Each strip:
   - a title and a kicker
   - panel captions of 1–2 short sentences, with one bold key word each
   - `grownUpWords`: the paper's real terms
   - `provenance: illustration`
4. **`facts`:** 4–6 real numbers. Each needs `figure`, `claim` (`model_design` or `measured_result`), a kid-level `text`, `source {label: "Paper §x.y", url: …#anchor}`,
   and an icon.
5. **`hook`** (top-level, beside `summary`): the scroll-stopper on the front-page tile. It is what makes a stranger
   open the issue, so spend real effort on it. Fields: `sticker` (2–3 loud words, "Wait, what?"), `teaser` (one
   question or surprising claim in kid words that the paper answers), `cta` (the payoff as a verb phrase, "Crack the
   bat puzzle"), `readMinutes`, optional `stat` (one real number from the facts block, ≤3 words of label), and
   optional `frames` (the lead's two slides with a one-word shout each, "Wings!" / "Swing!", so the cover art flips).
   Hook rules:
   - Create a curiosity gap, never a false promise. The issue must answer the teaser.
   - Every number is a verified fact. The sticker, teaser and CTA make no claim the paper does not support.
   - No fake urgency, no "you won't believe". Surprise and a clear question are enough.
   - Keep it short enough to read in one second at tile size.

Also set `summary` (1–2 sentences for search and the front page), `pageTitle`, `paper` (title, authors, year, url) and
`tags` (see `tag-story`).

## 4. Writing rules

- Short sentences. Everyday words. One idea per caption.
- Every technical idea gets its real name somewhere ("Grown-up words").
- Never present an invented number as real. Invented numbers live only in `illustration` blocks.
- Company blog numbers are always called company-reported ("Netflix says…").
- Write in our own words. Quote at most one short line, with attribution. Never copy figures or text.
- Avoid hype ("revolutionary"). Say what changed and how we know.

## 5. Make the media

Follow `draw-illustrations`. One file per panel under `public/media/<slug>/…`. Write alt text that describes
what the panel shows.

## 6. Check and publish

1. `fact-check` every evidence number and `paper`-basis tag.
2. Add the story to `public/data/site.json` and `public/data/library.json` (see `convert-paper` step 6), then run `npm run data` and fix every error.
3. `npm run dev`, then look at the story, the front page tiles and the feed at 1280px and 375px.
4. Commit on the branch the owner approved (ask before creating one) and open a PR. Never push to `main`.
