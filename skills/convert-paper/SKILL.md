---
name: convert-paper
description: The start-to-finish runbook for turning one research paper or company blog post into a published Geeky Times story. Start here; it calls the other skills in order and covers the library, graph, claim labels, canvas and branch rules.
---

# Convert a source into a Geeky Times story

One page, in order. Each step names the skill or file that holds the detail. Do not skip a step; do not build UI before
its canvas step is approved.

Rules that apply the whole way through (full text in `AGENTS.md`):
- **Ask the owner before creating any branch.** Never push to `main`. By default stay on the current feature branch.
- **Canvas before code.** Any new visual or layout (cover, hero art, a new section) is shown on the design canvas first,
  with 1–2 options. Build only after the owner picks one. Content that fits the existing layout needs no canvas step.
- **Illustration ≠ evidence.** Invented teaching numbers are labelled; real numbers carry a claim kind and a source.
- **Original work only.** Own words and own drawings. At most one short quote, with attribution.

## 0. Pick and check the source

1. Take the exact arXiv id (or blog URL). **Open the abstract page yourself** and confirm title, authors, submission
   date, subjects, page and figure counts. Titles and ids from chat or from a model's memory are unreliable.
2. Decide the trust level: `peer_reviewed` (published in a reviewed venue; confirm it), `preprint`, or
   `company_reported` (a company blog's own numbers). A preprint is never called peer-reviewed.
3. Note the kind of source, because it changes how you tell it:
   - **Method or result paper** (Transformer): one everyday example carries the story; evidence is measured results.
   - **Theory, review or classroom paper** (scaling laws): there may be no experiment. Evidence cards are the paper's
     own derivations and worked numbers, labelled `model_design` (how it is built or argued), not `measured_result`.
   - **Company blog**: every number is `company_reported`; link the original and an archived copy.

## 1. Write the story JSON (`explain-source`)

Create `public/data/papers/<slug>.json`. Use `attention-is-all-you-need.json` as the shape reference.
- Blocks, in order: `lead`, `story` (4 chapters), `comic` (4–6 strips × 3 panels), `facts` (4–6 numbers).
- Top level: `summary`, `desk`, `hook` (sticker, teaser, cta, readMinutes, optional stat and frames), `paper`, `tags`.
- **No issue, volume or date of ours in the story** (decision 31). Kickers name the desk ("Biology & physics / Picture
  story"), never "The size issue". The only date on a story is the source's own year.
- **Every fact gets `claim`:** `model_design` (how it was built or argued) or `measured_result` (what a test found).
  Never both. Each fact also needs a `source` label and a section link.
- Language: a school kid can follow it; real terms go under "Grown-up words".

## 2. Fact-check (`fact-check`)

Verify every number, name, date, section link and `paper`-basis tag against the source's own text. Record the exact
phrase and anchor for each. Weaken or remove anything unconfirmed; never fill gaps from memory. Keep the list for the
PR description.

## 3. Tag (`tag-story`, `prompts/tag-paper.md`)

Infer tags from the shared vocabulary (13 facets). Propose new tags under `proposed`; the owner approves them into
`public/data/tags.json`. Only approved tags reach readers.

## 4. Show the owner the cover and layout on the canvas

Before drawing final art or changing any UI:
1. Mock the lead art, the front-page tile and the story opening on the canvas (https://claude.ai/artifact/Etbd81Tw6BuFzcKxR7dAhf),
   using the real headline, hook and one real number.
2. Offer 1–2 options with a recommendation. Wait for the owner's pick.
Skip this step only when the story uses existing layouts unchanged and the art follows an already-approved style.

## 5. Draw the media (`draw-illustrations`)

One SVG per panel under `public/media/<slug>/`, from `tools/draw_<slug>.py`. Lead plates 600×340, comic panels 320×220,
story panels 440×215, fact icons 160×100. Resting state must be meaningful; honour reduced motion; alt text on all.

## 6. Wire it into the library (`public/data/library.json`)

The front page, issues, companies and map read the library, not the paper file.
1. `public/data/site.json`: add `{slug, title, dataUrl}` to `papers`.
2. `library.json` → `stories`: add the story with `real: true`, `sample: false`, `role`, `kind`, `fields`, `trust`,
   `minutes`, and its `headline`, `accent`, `dek`, `desk`, `title`, `authors`, `year`. **Replace a sample story
   in its slot** (same id if it was the placeholder for this paper; otherwise remove the sample) rather than adding a
   duplicate.
3. `library.json` → `front`: place it (`lead`, `aside`, `more`, topic rows, vault) only if the owner wants it there.
4. `library.json` → `issues`: when the owner assembles an issue, list the story in that issue's `stories`. Issues collect
   already-published stories; a story may sit in several and never names one itself.
5. **Graph:** add a `nodes` entry (`story` = the id, `field`, map `x`/`y` inside its field's cluster) and `relations`
   to earlier work. Relations point from the earlier idea to the later one and need a `kind`
   (`builds_on` | `improves_on` | `uses_method`) and a one-line `note`. Mark links verified only with a cited source;
   otherwise they stay "to be fact-checked".
6. If the paper's field is new, add it to `fields` with a map `cluster`.

## 7. Validate and look

1. `npm run data` must pass (it checks tags, evidence links and every library reference).
2. `npx tsc -b`, `npm run lint`, `npm run build`.
3. `npm run dev`, then look at the front page, the story (all tabs and the family tree), the issue, the map and the
   feed at 1280px and 375px. No horizontal scroll; labels at least 12px.

## 8. Ship (`publish-issue`)

1. Commit on the branch the owner approved. Include the fact-check list in the PR description.
2. The owner merges. Never push to `main`. Open the PR yourself only if the GitHub CLI is signed in; otherwise give the
   compare link.
3. Update `AGENTS.md` ("Current status") and `docs/roadmap.md` if anything on the roadmap moved.
