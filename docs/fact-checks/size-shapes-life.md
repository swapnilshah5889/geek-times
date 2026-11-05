# Fact-check: "Why a bigger deer breaks" (`size-shapes-life`)

Source: arXiv 2408.04070, Das, Gonick and Al Mosleh, submitted 7 Aug 2024 (HTML: https://arxiv.org/html/2408.04070).
Checked against the arXiv HTML text and abstract page on 2026-11-04. Anchors below were confirmed to exist.

| Claim in the story | Source phrase / anchor | Result |
|---|---|---|
| Authors Kausik S Das (University of Maryland Eastern Shore), Larry Gonick (San Francisco), Salem Al Mosleh (UMES); 2024 | Title page; abs page "Submitted on 7 Aug 2024" | pass |
| Preprint, no venue | arXiv only; abs page lists "31 page, 17 figures", no journal reference | pass (labelled Preprint) |
| Deer 5× bigger: weight 125×, leg-bone cross-section 25×, load 5× | Fig. 11 (`#S3.F11`): "weight would become 125 times its original weight, while the cross-sectional area of its leg bones would increase only 25 times … five times more pressure" | pass |
| Chopping a cube into 125 pieces makes the outside 5× bigger | Fig. 2 (`#S2.F2`) caption says "5³ = 125 times". Our arithmetic: 125 cubes of side 1 have area 125 × 6 = 750; one cube of side 5 has area 6 × 25 = 150; ratio 5. | **changed** (now `illustration`, was `model_design`): the story uses 5× as our arithmetic on a made-up cube (chapter 2, comic strip 1 and the 5× fact card are all `illustration`). The paper's caption looks like a slip; the fact card says so and carries no paper link |
| A person loses about 1,250 Calories a day to cooler surroundings (2 m² skin, ε = 0.98, 305 K vs 300 K) | §III.3 (`#S3.SS3`): "equivalent to 1250 Calories" | pass (recomputed with Stefan–Boltzmann: about 1,270 kcal; stated as the paper's estimate) |
| Wing loading 4× → cruising speed 2× | §IV.1 (`#S4.E8`): "four times … twice as fast" | pass |
| 14 bird species; fit slope 0.50 | Table 1 (`#S4.T1`) lists 14 species; Fig. 12 (`#S4.F12`) "y = 0.50x + 0.48". The fit uses natural logs: at 23 N/m² it gives 7.8 m/s, matching Table 1 | pass (plot line drawn from the fit) |
| Kittiwake 0.41 kg, dove prion 0.20 kg; speeds 10.1 and 9.9 m/s | Table 1 | pass |
| Rotifer breathes through its skin; volume grows with the cube, area with the square | §III.1 (`#S3.SS1`) | pass |
| "Twice as wide → body needs 8× the air, skin only 4×" | Follows from the cube/square rule above | **our arithmetic**, labelled model design |
| Lungs, gills and folded intestines add surface; thicker legs as in elephants | §III.1, §III.2, §III.4 | pass |
| Small animals eat rich food; elephants eat low-calorie plants; blue whales eat krill | §III.3 (`#S3.SS3`) | pass (seeds and nuts are the paper's examples for small rodents; caption wording softened to "mice and hummingbirds … nuts and nectar") |

Claim kinds: the 125-vs-25, 1,250 and 4×→2× numbers are `model_design` (derivations and estimates). The 5× cube figure is `illustration`: our arithmetic on an invented cube, not a number the paper states. Only the 0.50 slope
across 14 species is a `measured_result`, from data the authors collected from their Ref. [27].

Tags: 24 new vocabulary entries were approved by the owner on 2026-11-04; all 27 tags on the story are approved.
