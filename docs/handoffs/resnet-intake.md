# ResNet intake (read-only)

Status: intake only, prepared 2026-11-05 on `v1`. No conversion, drawing, JSON edit or fact-check record has been started.
The facts in section 1 come from the brief for this pass and still need confirming in `docs/fact-checks/resnet.md`.

## 1. Source

- **Title:** Deep Residual Learning for Image Recognition (to confirm in the fact-check; the sample uses the short name "ResNet").
- **Authors:** Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun (Microsoft Research).
- **Peer-reviewed publication:** CVPR 2016.
  <https://openaccess.thecvf.com/content_cvpr_2016/html/He_Deep_Residual_Learning_CVPR_2016_paper.html>
- **Preprint:** arXiv 1512.03385 (December 2015).
- **Results cited in the brief:** winner of ImageNet 2015 and COCO 2015.
- **Trust level:** `peer_reviewed` (decision 44 labels every sourced claim with it).

## 2. Date

**Use 2016** (the CVPR publication year), not 2015 (the arXiv preprint year).

- Sample data currently says 2015 in two places, and both change when the real story replaces the sample:
  - `public/data/library.json` → `stories[]` `resnet`: `year: 2015`.
  - `public/data/library.json` → `nodes[]` `resnet`: `year: 2015`.
- The `Paper from <year>` text on the story follows the story's `year`.
- `size-shapes-life` uses its preprint year because it is a preprint. ResNet is peer-reviewed, so the venue year applies.
- Decision 31 says "the source's own year" but does not say which year to use when a source has both a preprint and a venue
  version. This pass follows the brief (venue year for peer-reviewed sources). If the owner agrees, record that as a rule.

## 3. Slug

**`resnet`.** It matches the sample id for both the story and the graph node, so the real story replaces the placeholder in
place. The route becomes `/papers/resnet`, and the new file is `public/data/papers/resnet.json`.

Story fields that are still sample values and need replacing: `headline`, `dek`, `desk`, `role` (feature), `art` (stairs),
`minutes`, `sample: true`. The story has no `trust` field yet (add `peer_reviewed`), and `real: true` is missing too.
The node has no `short` field; the Transformer node sets one (`"short": "The Transformer"`), so ResNet can get one as well.

## 4. Graph edges touching the resnet node

Node: `nodes[]` `resnet` (ResNet, He and colleagues, 2015, field `ai`, `story: "resnet"`).

Edges in `relations[]` that touch it: **1 in total, and it is unverified.**

| From → to | kind | note | flags | status |
|---|---|---|---|---|
| resnet → transformer | uses_method | "Shortcut connections keep deep stacks trainable." | no `cited`, no `crossField` | **unverified** |

**Direction looks inverted.** In this file, `from` is the later work and `to` is the thing it uses: `transformer → bert`,
`transformer → gpt3`, `transformer → vit` and `transformer → alphafold` all read "X uses the Transformer". Under that
convention, `resnet → transformer` reads "ResNet uses the Transformer's method", which the note does not say. The note
describes ResNet's own contribution. The likely real link runs the other way (the Transformer's blocks use residual
shortcuts), but that has to be checked in the paper. The kind (`uses_method` or something else) also needs an editor's
decision. Both go through `RelationEvidence` review.

Status: this edge has no `RelationEvidence` and no review. A real ResNet story does not verify it. Verifying relations is the
separate Phase 2 item in `docs/production-plan.md` ("Verify family-tree and map relations with citations").

## 5. Samples that reference resnet (clean up during conversion)

| Where in `library.json` | Reference | Action at conversion |
|---|---|---|
| `nodes[]` `resnet` | `story: "resnet"`, `year: 2015` | Keep the story link; set year 2016; add `short`. |
| `relations[]` | `resnet → transformer` (above) | Verify or remove (see section 4). |
| `stories[]` `blog-artwork` | `builtOn: "resnet"` | Sample blog claims it is built on ResNet. Unsourced; remove or re-check when that sample is replaced. Not evidence. |
| `companies[]` `streaming` | `builtOn` includes `resnet` (with `transformer`, `lstm`) | Sample company. Same treatment as above. |
| `companies[]` `ride` | `builtOn: ["resnet"]` | Sample company. Same treatment as above. |
| `front` `more` | `resnet` | Real story keeps its slot; check the order when it goes live. |
| `front` `topics` (`ai`) | `resnet` | Keep. This is the AI topic's second real story. |
| `issues[]` `001` | `resnet` in the "How machines learned to read" issue | Editorial question: ResNet is a vision paper. Issue membership lives only in `library.json` (decision 31). |

Not referenced: `storylines` (the `machines-read` steps do not include ResNet), `public/data/papers/` (no `resnet.json` yet)
and `search-index.json` (generated). The prerender scripts use `/papers/resnet/` only as an example URL in comments.
`design/canvas-source/Main.dc.html` shows "ResNet · He and colleagues, 2015" as a mockup. That is design material, not data,
so it is left alone.

## 6. Why ResNet now

- It fills the `ai` field's second real story. Today `ai` has one real story (Attention); `size-shapes-life` is biology and
  physics, and H3 is software.
- It exercises the Transformer family-tree edge honestly once relations are verified (see the direction problem in section 4).
- It tests `paper` trust `peer_reviewed` on a second story. Today the three real stories are Attention (peer-reviewed),
  `size-shapes-life` (preprint) and H3 (company-reported). A second peer-reviewed story strengthens the trust-label sample
  from decision 44.

## 7. Before any conversion (not started)

- Create `docs/fact-checks/resnet.md` for the title, authors, venue, year and result claims in section 1.
- Owner or lead to confirm: the 2016 year rule (section 2), the relation direction and kind (section 4), and the issue
  placement (section 5).
- Licence check on the CVPR open-access paper. Our own words and drawings only (Phase 5 per-source copyright check).
- Conversion goes through `skills/convert-paper`, after this intake is accepted.
