# ResNet library patch (for the lead to apply)

Status: spec only. `data/seed/library.json` and `data/seed/tags.json` were **not** edited. Story file: `data/seed/papers/resnet.json`. Fact-check: `docs/fact-checks/resnet.md`.
Nothing here has been published (`publish:supabase` was not run). The paths below use `data/seed/`; the older `public/data/` paths in `skills/convert-paper` are stale.

## 0. Order of work

1. Add the tags in section 4 to `data/seed/tags.json` (the story's tags must exist and be `approved` or the publish aborts at step 7).
2. Replace the sample `resnet` story and node in `library.json` (sections 1 and 2).
3. Add the `site.json` papers entry (section 5).
4. Check section 3 (relations) and section 6 (open questions), then publish.

## 1. `stories[]`: replace the sample entry with this one

Same id `resnet`, so the route stays `/papers/resnet`. Drop the sample-only fields (`art`, `sample: true`, old `headline`, `dek`, `desk`, `role`, `minutes`, and any `builtOn`).

```json
{
  "id": "resnet",
  "real": true,
  "sample": false,
  "headline": "Don’t start over.",
  "accent": "Just fix it.",
  "dek": "A photo-reading machine got worse when it was given more layers. A small shortcut, a copy of the picture added back at the end of each block, fixed that, and let networks grow past a hundred layers.",
  "desk": "AI & vision",
  "fields": ["ai"],
  "role": "feature",
  "kind": "paper",
  "title": "Deep Residual Learning for Image Recognition",
  "authors": "He and colleagues",
  "year": 2016,
  "trust": "peer_reviewed",
  "minutes": 10,
  "note": "comic + facts"
}
```

Notes: `year: 2016` follows the intake (venue year for peer-reviewed sources). The CVPR venue and year are **not confirmed** in the fact-check (the arXiv text omits them and the CVPR page returned 403), so please confirm before publishing. `role: "feature"` keeps the sample's role; change it if the front page wants something else. `minutes: 10` mirrors `size-shapes-life`; the story's own `hook.readMinutes` is 4.

## 2. `nodes[]`: replace the sample node

```json
{
  "id": "resnet",
  "title": "Deep Residual Learning for Image Recognition",
  "short": "ResNet",
  "authors": "He and colleagues",
  "year": 2016,
  "field": "ai",
  "type": "paper",
  "x": 300,
  "y": 300,
  "story": "resnet",
  "blurb": "Made very deep photo-reading networks trainable by letting each block learn only a small fix on top of its input. The Transformer’s residual links use the same idea."
}
```

Notes:
- `x: 300, y: 300` is the sample's existing position; it sits inside the `ai` cluster (cx 250, cy 220, rx 210, ry 160) between `vit` (170, 300) and `blog-social` (425, 300), clear of the other ai nodes.
- Slug/id and `story` stay `resnet` (the node `id` doubles as the relation key).
- The blurb's last sentence points at the Transformer link. The ResNet paper cannot support it (see section 3). If you want only paper-backed text in the blurb, use: "Made very deep photo-reading networks trainable by letting each block learn only a small fix on top of its input."

## 3. `relations[]`

Existing edge (keep as is, do not add anything new):

```json
{ "from": "resnet", "to": "transformer", "kind": "uses_method", "note": "Shortcut connections keep deep stacks trainable." }
```

- Direction is correct (`from` = earlier idea, `to` = later work), per the intake.
- **The ResNet paper cannot verify this edge.** It is a statement about the Transformer paper (that it uses residual connections around sub-layers), so the evidence is a quote and location in *Attention Is All You Need* (the existing story's tag `concept/residual-connection` points at its §3.1, `#S3.SS1`; that is the place to cite), plus an editor review. The ResNet paper predates the Transformer and says nothing about it. Leave the edge **without** `cited: true` until the Transformer-side `RelationEvidence` exists.
- The ResNet paper does not introduce a relation to any other node in the library. Its own related work cites Highway networks, VGG, GoogLeNet and others, none of which are nodes. No new relation edges are proposed.
- The note text is a statement about the Transformer's design, not about this paper; keep it editorial.

Other `library.json` references to clean up, from the intake section 5 (not done here):
- `stories[]` `blog-artwork` (`builtOn: "resnet"`) and `companies[]` `streaming` / `ride` (`builtOn` includes `resnet`) are unsourced sample claims; a real ResNet story is not evidence for them.
- `front`: the intake says `front.more` and `front.topics` list `resnet`, but the current `library.json` lists only `attention-is-all-you-need` there. Add `resnet` to `front.topics` (`ai`) if the owner wants it on the front page.
- `issues[]` `001` membership is an editorial call (ResNet is a vision paper, the issue is "How machines learned to read").

## 4. `tags.json`: proposed new tags

22 tags are used by the story and are not in the vocabulary. Exact shape (matches `TagDef`): append to `tags[]`. Parents that exist today: `area/artificial-intelligence`, `concept/neural-network`. `concept/residual-connection` already exists and already carries the aliases "skip connections" and "shortcut connections", so no new tag is needed for shortcuts.

```json
[
    {"id": "area/computer-vision", "facet": "area", "label": "Computer vision", "parent": "area/artificial-intelligence", "aliases": ["vision", "image recognition", "machine vision"]},
    {"id": "concept/degradation-problem", "facet": "concept", "label": "Degradation problem", "aliases": ["deeper is worse", "accuracy degradation"]},
    {"id": "concept/bottleneck-block", "facet": "concept", "label": "Bottleneck block", "parent": "concept/neural-network", "aliases": ["bottleneck design", "bottleneck architecture"]},
    {"id": "concept/batch-normalization", "facet": "concept", "label": "Batch normalization", "parent": "concept/neural-network", "aliases": ["batchnorm", "BN"]},
    {"id": "technique/resnet", "facet": "technique", "label": "ResNet", "aliases": ["residual network", "residual networks", "deep residual learning"]},
    {"id": "technique/faster-r-cnn", "facet": "technique", "label": "Faster R-CNN", "aliases": ["faster rcnn"]},
    {"id": "task/image-classification", "facet": "task", "label": "Image classification", "aliases": ["image recognition", "photo classification"]},
    {"id": "task/object-detection", "facet": "task", "label": "Object detection", "aliases": ["detecting objects"]},
    {"id": "dataset/imagenet", "facet": "dataset", "label": "ImageNet", "aliases": ["ILSVRC", "ImageNet 2012"]},
    {"id": "dataset/cifar-10", "facet": "dataset", "label": "CIFAR-10", "aliases": ["CIFAR10"]},
    {"id": "dataset/ms-coco", "facet": "dataset", "label": "MS COCO", "aliases": ["COCO", "Microsoft COCO"]},
    {"id": "metric/top-5-error", "facet": "metric", "label": "Top-5 error", "aliases": ["top5 error"]},
    {"id": "metric/top-1-error", "facet": "metric", "label": "Top-1 error", "aliases": ["top1 error"]},
    {"id": "organization/microsoft-research", "facet": "organization", "label": "Microsoft Research", "aliases": ["Microsoft", "MSR"]},
    {"id": "author/kaiming-he", "facet": "author", "label": "Kaiming He"},
    {"id": "author/xiangyu-zhang", "facet": "author", "label": "Xiangyu Zhang"},
    {"id": "author/shaoqing-ren", "facet": "author", "label": "Shaoqing Ren"},
    {"id": "author/jian-sun", "facet": "author", "label": "Jian Sun"},
    {"id": "venue/cvpr", "facet": "venue", "label": "CVPR", "aliases": ["Computer Vision and Pattern Recognition"]},
    {"id": "venue/cvpr-2016", "facet": "venue", "label": "CVPR 2016", "parent": "venue/cvpr"},
    {"id": "everyday/seeing-pictures", "facet": "everyday", "label": "Seeing pictures", "aliases": ["photos", "recognising things", "vision"]},
    {"id": "everyday/teamwork", "facet": "everyday", "label": "Teamwork", "aliases": ["helpers", "passing it along"]}
]
```

Story-side status: the new tags appear in `resnet.json` with `source: "editor", status: "approved"` so the file can publish as soon as these exist in `tags.json`. If you would rather review them first, change those entries to `suggested` and drop them from the file until approved. `venue/cvpr-2016` is `basis: background` (no evidence link) because the venue is not in the arXiv text.

Existing tags reused (already in `tags.json`): `field/computer-science`, `area/artificial-intelligence`, `area/machine-learning`, `area/deep-learning`, `concept/neural-network`, `concept/residual-connection`, `concept/convolutional-neural-network`, `concept/softmax`, `everyday/smart-computers`.

## 5. `site.json`

Add to `papers` (it only exists as a list of slugs today):

```json
{ "slug": "resnet", "title": "Deep Residual Learning for Image Recognition", "dataUrl": "data/papers/resnet.json" }
```

## 6. Open items for the lead

- Confirm CVPR 2016 on the CVPR open-access page (403 from the fetch tool) before the year 2016 and `peer_reviewed` go live. Fact-check rows 4 and 5 are marked weak.
- The paper has no HTML version, so fact links and tag evidence are `https://arxiv.org/pdf/1512.03385#page=N`. The validator's prefix rule is satisfied because `paper.url` is the same PDF address.
- Cover/hook: the file has a `hook` (like the other stories) and no separate `cover` block. Canvas step: the lead art, tile and story opening still need the owner’s pick per `skills/convert-paper` step 4. All 27 media files are grey placeholder plates in `public/media/resnet/`; real art is a follow-up.
- The intake says the 2016-vs-2015 rule is not yet recorded as a decision.
- Comic strips are tagged `model_design`; the invented "helpers" scenario is in the lead and chapters 1 to 3 only (`illustration`).
