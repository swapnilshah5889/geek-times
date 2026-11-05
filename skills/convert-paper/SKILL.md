---
name: convert-paper
description: The start-to-finish runbook for turning one research paper or company blog post into a published Geeky Times story. Start here; it calls the other skills in order and covers the library, graph, claim labels, canvas and branch rules.
---

> **Default model:** **medium** (Sonnet 5.5 or equivalent) — orchestrates smaller mechanical steps. Fall back to larger only when the task genuinely needs it.

# Convert a source into a Geeky Times story

One page, in order. Each step names the skill or file that holds the detail. Do not skip a step; do not build UI before
its canvas step is approved.

Rules that apply the whole way through (full text in `AGENTS.md`):
- **Commit to the `v1` branch and push** (decision 40). Never commit or push to `main`. No new branches unless the owner says so.
- **Canvas before code.** Any new visual or layout (cover, hero art, a new section) is shown on the design canvas first,
  with 1–2 options. Build only after the owner picks one. Content that fits the existing layout needs no canvas step.
- **Illustration ≠ evidence.** Invented teaching numbers are labelled; real numbers carry a claim kind and a source.
- **Original work only.** Own words and own drawings. At most one short quote, with attribution.

## 0. Pick and check the source

1. Take the exact arXiv id (or blog URL). **Open the abstract page yourself** and confirm title, authors, submission
   date, subjects, page and figure counts. Titles and ids from chat or from a model's memory are unreliable.
   For a company engineering post, open the post itself and follow the **Blog branch** at the end of this file.
2. Decide the trust level: `peer_reviewed` (published in a reviewed venue; confirm it), `preprint`, or
   `company_reported` (a company blog's own numbers). A preprint is never called peer-reviewed.
3. Note the kind of source, because it changes how you tell it:
   - **Method or result paper** (Transformer): one everyday example carries the story; evidence is measured results.
   - **Theory, review or classroom paper** (scaling laws): there may be no experiment. Evidence cards are the paper's
     own derivations and worked numbers, labelled `model_design` (how it is built or argued), not `measured_result`.
   - **Company blog**: every number is `company_reported`; link the original and an archived copy.

## 1. Write the story JSON (`explain-source`)

Create `public/data/papers/<slug>.json`. Use `attention-is-all-you-need.json` as the shape reference. Set `"schemaVersion": 2` (decision 46); the loader rejects any other version. Every fact must carry an explicit `claim` (decision 44).
- Blocks, in order: `lead`, `story` (4 chapters), `comic` (4–6 strips × 3 panels), `facts` (4–6 numbers).
- Top level: `summary`, `desk`, `hook` (sticker, teaser, cta, readMinutes, optional stat and frames), `paper`, `tags`.
  A paper story leaves out `kind` (it defaults to `paper`). A blog story sets `"kind": "blog"` and has a `blog` block
  instead of `paper` (see the Blog branch).
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

1. Commit on `v1` with the fact-check list in the commit message. Push `v1`.
2. The owner merges `v1` into `main` when ready to release (decision 40). Don't open a PR per story.
3. Update `AGENTS.md` ("Current status") and `docs/roadmap.md` if anything on the roadmap moved.

## Blog branch: a company engineering post

Use this branch when the source is a company's own engineering blog post (decision 16). Everything else in this
runbook still applies (original words, labels, fact-check, validation, ship). Only the parts below change.

### B0. Pick and check the source
1. Take the post's URL and open it yourself. Confirm the title, the organization as the post names it (the blog or
   team name), the publication date, and that the numbers you plan to use appear in the post.
2. The post is the source. Not a press release about it, not a news article, not a third-party summary.
3. Trust is always `company_reported` (decision 18). The numbers are the company's own measurements. Never call them
   peer-reviewed or independently verified.
4. Write your own explanation. Quote at most one short phrase, under 15 words, with attribution.

### B1. Snapshot and archive
1. On the day you check the post, save an archived copy with an archive service (for example the Wayback Machine).
2. Put the archived copy's URL in `blog.archivedUrl`. Record the retrieval date in the fact-check list.
3. If the company edits the post later, the archive still shows the version we checked. Re-check the facts against the
   new version before changing the story, then update `archivedUrl` to the new copy.

### B2. The data shape
- Root: `"kind": "blog"`. Leave out the `paper` block; the validator rejects a `paper` block on a blog story.
- `blog`: `title`, `organization`, `published` (YYYY-MM-DD, a real date), `url` (the live post), `archivedUrl` (expected),
  `trust: "company_reported"`.
- `summary`, `desk`, `hook`, `blocks`, `tags` and the file name (`public/data/papers/<slug>.json`) work exactly as for a paper.
- The story page shows "The engineering post", the organization and the date, and a footer line saying every number is
  company-reported.

### B3. Evidence links
- A blog has no arXiv paragraph anchors (`#S3.SS2.SSS2`). Do not copy that form.
- Link to the post's own heading as a fragment: `https://<post-url>#<heading-slug>`, where the slug is the way the
  page writes that heading's anchor (lowercase, hyphens). The fact-check step confirms the anchor exists.
- If the post has no usable heading anchor, link the post itself and name the section in the label, with a short
  quoted phrase (under 15 words), e.g. `Post, “p99 latency under load”`.
- A paper-basis tag's `evidence` must start with the post's `url` or its `archivedUrl`. The validator checks that prefix.

### B4. Numbers and claim kinds
- Every number carries the company's trust. A blog's `measured_result` is what the company measured and reported. A
  `model_design` fact is how the post says the system is built (for example, the architecture it describes).
- Every `measured_result` needs a `source.url` (the validator enforces it). For a blog, the validator also prints a
  warning on each one as a reminder that the number is company-reported. The warning is a reminder, not a check.
- Write results as the company's claims: "the company reports a 30% drop in…", not "…drops 30%". Keep the unit and the
  comparison exactly as the post states them.
- Illustration numbers stay labelled illustration (invented).

### B5. Library wiring
1. `public/data/site.json`: add the story to the `papers` list (the name is historical; every story goes there).
2. `public/data/library.json` → `stories`: add the story with `kind: "blog"` (it must match the file's `kind`; the
   validator checks it), `real: true`, `sample: false`, `trust: "company_reported"`, `company` (the company's id in
   `companies`), `authors` set to the organization and `year` to the published year, plus the usual `headline`,
   `accent`, `dek`, `desk`, `title`, `role`, `fields` and `minutes`. Replace the sample placeholder in its slot.
3. `builtOn`: the id of the story this post puts into practice, if we have explained it (for example the paper it uses).
4. Company page: add the story id to that company's `posts`. A real company has no `sample` flag. Only the placeholder
   companies carry `sample: true`, and only those show "Sample page" wording.
5. Graph: a blog is a node with `type: "blog"` and `story` set to the story id, added the same way as a paper node.
6. The library's owner writes these entries. This section describes the entry they write; the validator checks it.

### B6. Validate
- `npm run data` checks: `kind` is `paper` or `blog`; a blog has a `blog` block with `url`, `organization`, a real
  `published` date and `trust: "company_reported"`, and no `paper` block; each paper-basis tag links into the post or its
  archive; every `measured_result` has a `source.url`; a real library entry's `kind` matches its file.
- The validator does not check that a number is true. That is the fact-check step (`skills/fact-check`).
