# Fact-check: "Deep Residual Learning for Image Recognition" (He, Zhang, Ren, Sun, 2016)

Source: Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun (Microsoft Research), "Deep Residual Learning for Image Recognition", arXiv:1512.03385. The version checked is **v1** (stamp "10 Dec 2015"), the PDF at https://arxiv.org/pdf/1512.03385. No later arXiv version was compared.
Fetched and checked on 2026-11-07. The PDF text was extracted with `pdftotext -layout` and every quote below was matched by eye against that text. Quotes are trimmed (and "[..]" marks a cut). The story quotes at most one short phrase from the paper; the quotes in this record are for checking only.
Venue and year: the brief and the intake doc say CVPR 2016 (peer-reviewed). **The arXiv text does not print the venue**, and the CVPR open-access page (https://openaccess.thecvf.com/content_cvpr_2016/html/He_Deep_Residual_Learning_CVPR_2016_paper.html) returned HTTP 403, so the venue, the year 2016 and the `peer_reviewed` trust level are carried from the intake and **not verified here**. Please confirm them by hand. The CVPR camera-ready may differ in small ways from arXiv v1 (for example the abstract of v1 says "CIFAR-10 with 100 and 1000 layers", while its Section 4.2 uses 110 and 1202; the story uses the Section 4.2 numbers).

**Page anchors.** The paper has no HTML version, so evidence links are `https://arxiv.org/pdf/1512.03385#page=N` (PDF page numbers of v1). Pages: 1 abstract and intro, 2 intro and related work, 3 sections 3.1 to 3.3 start, 4 section 3.3 to 4.1 start, 5 Table 1, Fig. 4, Table 2, 6 Tables 3 to 5 and bottleneck, 7 deeper nets and CIFAR-10 start, 8 CIFAR-10 end, section 4.3, 10 appendix A.

**What is in the paper:** the degradation problem, the residual block (y = F(x) + x), identity shortcuts, 18 to 152 layer architectures, ImageNet, CIFAR-10 and COCO/PASCAL results, and the contest wins.
**What is not in the paper:** the "line of helpers" and cat-picture analogy, the "five guesses" explanation of top-5 error, and any claim about what later systems did with residual connections (the Transformer link lives in the library graph and needs the Transformer paper, not this one).

**Result key.** `pass` = the claim as worded is in the paper, or is a plain restatement. `weakened` = the wording went beyond the paper; the Result column says what was done. `weak` = could not be confirmed from the source available; left as background or flagged.

## Facts, story text, strips and hook

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 1 | Title is “Deep Residual Learning for Image Recognition” | Deep Residual Learning for Image Recognition | p. 1 (title) | name | pass |
| 2 | Authors: Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun, Microsoft Research | Kaiming He  Xiangyu Zhang  Shaoqing Ren  Jian Sun / Microsoft Research | p. 1 (title block) | name | pass |
| 3 | arXiv id 1512.03385, first posted December 2015, category cs.CV | arXiv:1512.03385v1 [cs.CV] 10 Dec 2015 | p. 1 (margin stamp) | name | pass |
| 4 | Published at CVPR 2016 (story year 2016, tag venue/cvpr-2016) | Not printed in the arXiv text. The CVPR open-access page returned HTTP 403 to the fetch tool. | n/a | venue | weak: year 2016 and the venue tag rest on the intake doc only; tag kept as basis background; confirm on the CVPR page by hand |
| 5 | Trust level peer_reviewed | Same as the row above: depends on the CVPR 2016 publication | n/a | trust | weak: same dependency; not verifiable from the arXiv text |
| 6 | Intake claim “winner of ImageNet 2015 and COCO 2015” | “we also won the 1st places on the tasks of ImageNet detection, ImageNet localization, COCO detection, and COCO segmentation”; ILSVRC 2015 classification: “won the 1st place” | Abstract, p. 1; §4.1, p. 7 | measured_result | weakened: the story names the contest wins only where the paper does (classification, detection, localization, COCO tracks); it never says “won COCO 2015” as a whole |
| 7 | Fact 1: up to 152 layers, 8 times deeper than VGG, still lower complexity | “residual nets with a depth of up to 152 layers—8× deeper than VGG nets [41] but still having lower complexity” | Abstract, p. 1 | model_design | pass |
| 8 | Strip 5c: the 152-layer net has 11.3 billion FLOPs (multiply-adds); VGG-16/19 have 15.3 / 19.6 billion | “the 152-layer ResNet (11.3 billion FLOPs) still has lower complexity than VGG-16/19 nets (15.3/19.6 billion FLOPs)”; “FLOPs (multiply-adds)” | §4.1, p. 7; §3.3, p. 3; Table 1, p. 5 | model_design | pass |
| 9 | Fact 2: identity shortcuts add no extra parameters and no extra computation | “Identity shortcut connections add neither extra parameter nor computational complexity.” | §1, p. 2; §3.2, p. 3 | model_design | pass |
| 10 | Fact 3: 34-layer plain 28.54, 34-layer ResNet 25.03 (top-1 error %, ImageNet validation) | Table 2: “34 layers 28.54 25.03”; “Top-1 error (%, 10-crop testing) on ImageNet validation” | §4.1, Table 2, p. 5 | measured_result | pass |
| 11 | Chapter 4: the two 34-layer machines match in depth, width and number of settings | “the ResNets have no extra parameter compared to their plain counterparts”; “plain/residual networks that simultaneously have the same number of parameters, depth, width, and computational cost” | Table 2 caption, p. 5; §3.2, p. 3 | measured_result | pass |
| 12 | Fact 4: ensemble top-5 error 3.57% on the ImageNet test set; first place in ILSVRC 2015 | “This leads to 3.57% top-5 error on the test set (Table 5). This entry won the 1st place in ILSVRC 2015.” | §4.1, Table 5, p. 7 and p. 6 | measured_result | pass |
| 13 | Fact 5: 28% relative improvement on COCO, 6.0 points of mAP@[.5, .95], VGG-16 to ResNet-101 in the same detector | “we obtain a 6.0% increase in COCO’s standard metric (mAP@[.5, .95]), which is a 28% relative improvement”; Table 8: 21.2 to 27.2 | §4.3, p. 8; Appendix A, p. 10 | measured_result | pass |
| 14 | Fact 5: the detector is the same for both backbones | “The detection implementation (see appendix) of using both models is the same” | §4.3, p. 8 | measured_result | pass |
| 15 | Fact 6: a 1202-layer net trained on CIFAR-10 with no optimization difficulty | “Our method shows no optimization difficulty” | §4.2, p. 8 | measured_result | pass |
| 16 | Fact 6: its test error is 7.93%, worse than the 110-layer net’s 6.43% | Table 6: “ResNet 110 1.7M 6.43”, “ResNet 1202 19.4M 7.93”; “The testing result of this 1202-layer network is worse than that of our 110-layer network” | §4.2, Table 6, p. 7; text p. 8 | measured_result | pass |
| 17 | Fact 6: the authors argue overfitting explains it | “We argue that this is because of overfitting. The 1202-layer network may be unnecessarily large (19.4M) for this small dataset.” | §4.2, p. 8 | measured_result | pass (worded “suspect”; the paper hedges with “argue”) |
| 18 | Chapter 1: a deeper plain net gets higher training error (real result) | “adding more layers to a suitably deep model leads to higher training error”; Fig. 1: 20-layer vs 56-layer plain nets on CIFAR-10 | §1, p. 1; Fig. 1, p. 1 | measured_result | pass |
| 19 | Chapter 1: this is not memorising (overfitting) | “such degradation is not caused by overfitting” | §1, p. 1 | measured_result | pass |
| 20 | Chapter 1: a long line of helpers redrawing a cat; mistakes pile up | Invented analogy | n/a | scenario | pass as scenario (provenance illustration) |
| 21 | Chapter 2: layers learn a correction (residual) instead of the whole mapping | “we explicitly let these layers fit a residual mapping”; “F(x) := H(x) − x” | §1, p. 2; §3.1, p. 3 | model_design | pass |
| 22 | Chapter 2: if no change is best, the correction can go to zero | “if an identity mapping were optimal, it would be easier to push the residual to zero than to fit an identity mapping by a stack of nonlinear layers” | §1, p. 2 | model_design | pass |
| 23 | Chapter 3: shortcut output is added to the stacked layers’ output | “their outputs are added to the outputs of the stacked layers” | §1, p. 2; §3.2, p. 3 | model_design | pass |
| 24 | Chapter 3: blocks are stacked to dozens or over a hundred layers | Networks of 34, 50, 101 and 152 layers | §3.3, §4.1, Table 1, p. 5 | model_design | pass |
| 25 | Strip 1a: 1,000 possible answers | “the ImageNet 2012 classification dataset … that consists of 1000 classes” | §4.1, p. 4 | model_design | pass |
| 26 | Strip 1b: top-5 error counts photos where the right answer is not in five guesses; top-1 uses only the first | The paper says “We evaluate both top-1 and top-5 error rates.” It does not define them. | §4.1, p. 4 | metric definition | weakened: standard definition, background only; strip 1 is provenance illustration |
| 27 | Strip 1c: lower error is better | Not stated; follows from “error” | n/a | metric definition | pass as background (strip 1 is illustration) |
| 28 | Strip 2a: extra layers that pass the input along unchanged make a deeper net at least as good | “There exists a solution by construction to the deeper model: the added layers are identity mapping” | §1, p. 1 | model_design | pass |
| 29 | Strip 2b: deeper plain nets had higher training error; the authors call it the degradation problem | “a degradation problem has been exposed” | §1, p. 1 | measured_result | pass |
| 30 | Strip 2c: the authors guess that learning identity through many layers is hard | “The degradation problem suggests that the solvers might have difficulties in approximating identity mappings by multiple nonlinear layers.” | §3.1, p. 3 | model_design | pass (the paper hedges with “might”; the strip says “guess”) |
| 31 | Strip 3a/3b: the block learns F = H − x and outputs F(x) + x | “The original mapping is recast into F(x)+x.” | §1, p. 2; §3.1, p. 3 | model_design | pass |
| 32 | Strip 3c: the authors hypothesise this is easier | “We hypothesize that it is easier to optimize the residual mapping than to optimize the original, unreferenced mapping.” | §1, p. 2 | model_design | pass |
| 33 | Strip 4a: the shortcut is a plain copy (identity) that skips layers | “Shortcut connections [..] are those skipping one or more layers. In our case, the shortcut connections simply perform identity mapping” | §1, p. 2 | model_design | pass |
| 34 | Strip 4b: identity shortcuts allow a fair plain-vs-residual comparison | “We can fairly compare plain/residual networks that simultaneously have the same number of parameters, depth, width, and computational cost” | §3.2, p. 3 | model_design | pass |
| 35 | Strip 4c: when sizes change, pad with zeros or use a projection | “(A) The shortcut still performs identity mapping, with extra zero entries padded for increasing dimensions … (B) The projection shortcut in Eqn.(2)” | §3.3, p. 4 | model_design | pass |
| 36 | Strip 5a: nets of 34, 50, 101 and 152 layers | Table 1 columns: 18-layer, 34-layer, 50-layer, 101-layer, 152-layer | Table 1, p. 5; §4.1, p. 7 | model_design | pass |
| 37 | Strip 5b: bottleneck block reduces then restores the size around a 3×3 layer | “The three layers are 1×1, 3×3, and 1×1 convolutions, where the 1×1 layers are responsible for reducing and then increasing (restoring) dimensions” | §4.1, p. 6 | model_design | pass |
| 38 | Hook: stat “152 layers deep” | Same as the 152-layer row | Abstract, p. 1 | model_design | pass |
| 39 | Hook teaser: more layers made a plain net worse, and a shortcut fixed it | “the situation is reversed with residual learning – the 34-layer ResNet is better than the 18-layer ResNet” | §4.1, p. 5 | measured_result | pass |
| 40 | Summary: networks over a hundred layers deep became trainable | “We present successfully trained models on this dataset with over 100 layers”; 152 layers on ImageNet | §1, p. 2; §4.1, p. 7 | measured_result | pass |
| 41 | Summary: an ensemble won the 2015 ImageNet classification contest | Same as the 3.57% row | §4.1, p. 7 | measured_result | pass |
| 42 | Grown-up words: residual learning, identity shortcut, parameter-free, bottleneck, degradation problem, FLOPs, top-5 error, ImageNet | Each appears in the paper (see rows above); “parameter-free” in §2, p. 2 | various | name | pass |

**Counts (42 rows): 38 pass, 2 weakened, 2 weak, 0 fail.** Weakened: row 6 (contest wins) and row 26 (top-5 definition). Weak (unverified here): rows 4 and 5 (CVPR 2016 venue, year and trust). Fail: none.

## Paper-basis tags

All `paper`-basis tags use evidence links that start with the paper url (`https://arxiv.org/pdf/1512.03385`), as `scripts/publish-to-supabase.ts` requires.

| Tag(s) | Evidence page | Section and phrase | Result |
|---|---|---|---|
| area/computer-vision | p. 1 | Abstract: “image recognition” in the title, “object detection” in §4.3 | pass |
| concept/residual-connection, technique/resnet | p. 3 | §3.1–§3.2: “Residual Learning”, “Identity Mapping by Shortcuts” | pass |
| concept/degradation-problem | p. 1 | §1: “a degradation problem has been exposed” | pass |
| concept/convolutional-neural-network | p. 4 | §3.3: “The convolutional layers mostly have 3×3 filters” | pass |
| concept/bottleneck-block | p. 6 | §4.1: “we modify the building block as a bottleneck design” | pass |
| concept/batch-normalization | p. 4 | §3.4: “We adopt batch normalization (BN) [16] right after each convolution” | pass |
| concept/softmax | p. 4 | §3.3: “a 1000-way fully-connected layer with softmax” | pass |
| technique/faster-r-cnn | p. 8 | §4.3: “We adopt Faster R-CNN [32] as the detection method” | pass |
| task/image-classification, dataset/imagenet, metric/top-1-error, metric/top-5-error | p. 4 | §4.1: “We evaluate our method on the ImageNet 2012 classification dataset”; “both top-1 and top-5 error rates” | pass |
| dataset/cifar-10 | p. 7 | §4.2: “the CIFAR-10 dataset [20]” | pass |
| task/object-detection, dataset/ms-coco | p. 8 | §4.3: “Object Detection on PASCAL and MS COCO” | pass |
| organization/microsoft-research, author/* (4) | p. 1 | Title block | pass |
| venue/cvpr-2016 | n/a | Not in the arXiv text | weak (basis background, not checked here) |

Note: the story file lists several tags that are not yet in `data/seed/tags.json` (see `docs/handoffs/resnet-library-patch.md`). `publish:supabase` aborts until the lead adds them.

## Claim kind and trust

- `model_design`: facts 1 (152 layers) and 2 (no extra parameters), plus strips 2 to 5. These describe how the network is built or argued.
- `measured_result`: facts 3 (25.03% vs 28.54%), 4 (3.57%), 5 (28%) and 6 (1202 layers, 7.93%). These are test results.
- Fact 1's "lower complexity than VGG" is a FLOP count the authors computed from the architecture, so it is kept as `model_design`.
- Each fact is labelled with the story's source trust (`peer_reviewed`) by the loader. Because the venue is unconfirmed (rows 4 and 5), that label should be treated as pending until checked.

## Not checked

- The CVPR 2016 camera-ready text.
- Whether later arXiv versions changed any number (only v1 was read).
- Every comparison table beyond the ones cited above (Tables 3, 4, 7, 9 to 14).
