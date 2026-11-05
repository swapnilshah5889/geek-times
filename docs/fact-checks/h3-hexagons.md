# Fact-check: "H3: Uber's Hexagonal Hierarchical Spatial Index" (Uber, 2018)

Source: Uber Engineering blog, "H3: Uber's Hexagonal Hierarchical Spatial Index", by Isaac Brodsky, published June 27, 2018.
Canonical URL used: https://www.uber.com/en-US/blog/h3/ (the page's own path is `/us/en/blog/h3/`).
Fetched and checked on 2026-11-05. Quotes were matched against the archived copy below (grep of the full article text).
Archive: https://web.archive.org/web/20261017041120/https://www.uber.com/en-US/blog/h3 (capture 2026-10-17 04:11:20 UTC; the text matches the live page).
A direct download of the canonical URL from our sandbox returned a "Not Acceptable" body, so the live page was read through the fetch tool instead.
Corroboration only (not a quote source): https://h3geo.org/docs/core-library/overview (resolution 0 has 122 cells; 15 finer resolutions; each hexagon has 1/7 the area of the next coarser hexagon).

**Location convention.** The post has no section anchors or URL fragments. Locations below are the section heading, plus the paragraph or figure they sit under. Section headings: Introduction (untitled), "Analysis using grids", "H3", "Getting started with H3", "Moving forward".

**Result key.** `pass` = the claim as worded is in the post; `weakened` = the post supports a narrower wording, and the narrower wording is what we use; `rejected` = not in the post, or unsupported; removed from the story.

## Measured vs asserted

- **Measured results in this post: none.** The post has no speed, latency, accuracy or benchmark numbers. The only numbers are hexagon counts for one worked example (see row 24). The story must not label any H3 fact "Measured result" based on this post.
- **Model design (how H3 is built, as the post states it):** resolutions, base cells, pentagons, projection, 64-bit index.
- **Derivation (geometry and math):** neighbor distances, area ratios, pentagon and face arithmetic. The post states these; we confirmed them as geometry.
- **Company-asserted (Uber's claims about use and rationale):** surge pricing, marketplace analysis, why hexagons are chosen. Label as "Uber says" with the source.

## Structural facts (the six we need)

| Fact | Expected | In the post | Quote | Location | Result |
|---|---|---|---|---|---|
| Resolutions | 16 | 16 (0 to 15) | "H3 supports sixteen resolutions." | H3, paragraph after Figure 8; Getting started (geoToH3: "between 0 and 15") | pass |
| Area ratio per finer level | about 1/7 | 1/7, with caveat | "Each finer resolution has cells with one seventh the area of the coarser resolution." Caveat: "Hexagons cannot be perfectly subdivided into seven hexagons, so the finer cells are only approximately contained within a parent cell." | H3, paragraph after Figure 8 | pass (keep the caveat) |
| Base cells | 122 | 122 | "The H3 grid is constructed by laying out 122 base cells over the Earth, with ten cells per face. Some cells are contained by more than one face." | H3, paragraph after Figure 7 | pass |
| Pentagons | 12 | 12 | "we chose to introduce twelve pentagons, one at each of the icosahedron vertices." | H3, same paragraph as base cells | pass |
| Index width | 64-bit | 64-bit | "a hexagon index is a 64-bit integer." | Getting started with H3, paragraph after Figure 11 | pass |
| Projection | icosahedron | gnomonic projections on icosahedron faces | "For map projection, we chose to use gnomonic projections centered on icosahedron faces." | H3, paragraph after Figure 5 | pass |
| Why hexagons | one neighbor distance (squares 2, triangles 3) | as expected | "hexagons have only one distance between a hexagon centerpoint and its neighbors', compared to two distances for squares or three distances for triangles." | H3, paragraph after Figure 6 | pass (the square count checks out geometrically; the triangle count is the post's claim and we did not check it) |

## Claim ledger

| # | Claim as we would state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 1 | H3 has 16 resolutions | "H3 supports sixteen resolutions." | H3, after Fig. 8 | model_design | pass |
| 2 | Each finer resolution has 1/7 the area of the coarser one (approximately contained) | "Each finer resolution has cells with one seventh the area of the coarser resolution." + "only approximately contained within a parent cell" | H3, after Fig. 8 | derivation | pass |
| 3 | The finest level is about 4.7 trillion times smaller in area than level 0 (7^15 = 4,747,561,509,943) | Not in post. Our arithmetic from row 2. | n/a | derivation (ours) | pass, labelled "our arithmetic" |
| 4 | H3 starts from 122 base cells, 10 per icosahedron face | "laying out 122 base cells over the Earth, with ten cells per face." | H3, after Fig. 7 | model_design | pass |
| 5 | Some base cells belong to more than one face (so 20 x 10 = 200 is not the count) | "Some cells are contained by more than one face." | H3, after Fig. 7 | model_design | pass |
| 6 | At the coarsest level there are 110 hexagons (122 minus 12 pentagons) | Not in post. Assumes all 12 pentagons are level-0 cells, which the post does not say. | n/a | derivation (assumed) | rejected (remove) |
| 7 | H3 has 12 pentagons, one at each icosahedron vertex | "we chose to introduce twelve pentagons, one at each of the icosahedron vertices." | H3, after Fig. 7 | model_design | pass |
| 8 | The grid is laid on an icosahedron (20 faces), with gnomonic projections centred on the faces | "we chose to use gnomonic projections centered on icosahedron faces." + "a twenty-sided platonic solid" | H3, after Fig. 5 | model_design | pass |
| 9 | A hexagon index is a 64-bit integer | "a hexagon index is a 64-bit integer." | Getting started, after Fig. 11 | model_design | pass |
| 10 | Hexagons have one neighbor distance; squares have two, triangles three | "hexagons have only one distance between a hexagon centerpoint and its neighbors', compared to two distances for squares or three distances for triangles." | H3, after Fig. 6 | derivation | pass (triangle count not checked by us) |
| 11 | Squares have two kinds of neighbours (edge and corner) | "squares having two different types of neighbors" | H3, before Fig. 5 | derivation | pass |
| 12 | The Mercator projection has large size distortion, so a plain Mercator square grid is a poor choice | "the Mercator projection has significant size distortion" | H3, before Fig. 5 | company_asserted | pass (Uber's argument) |
| 13 | Uber says hexagons reduce quantization error when people move through a city | "hexagons minimize the quantization error introduced when users move through a city" | Analysis using grids | company_asserted | pass (no measurement given) |
| 14 | Uber says hexagons make radiuses easy to approximate | "Hexagons also allow us to approximate radiuses easily" | Analysis using grids | company_asserted | pass |
| 15 | Neighbouring hexagons approximate circles | "Neighboring hexagons have the useful property of approximating circles using the grid system." | Getting started, after Fig. 10 | company_asserted | pass |
| 16 | Truncating an index to a coarser level adds a fixed amount of shape distortion | "the truncation process produces a fixed amount of shape distortion" | H3, paragraph after Fig. 8 | model_design | pass |
| 17 | Uber calculates surge pricing from supply and demand counted per hexagon | "we calculate surge pricing by measuring supply and demand in hexagons in each city that we serve." | Analysis using grids | company_asserted | weakened: do not say "H3 sets surge prices"; the post does not say that |
| 18 | H3 is used throughout Uber for marketplace analysis | "H3 is used throughout Uber to support quantitative analysis of our marketplace" | Moving forward | company_asserted | pass |
| 19 | Uber built H3 for ride pricing and dispatch | "Uber developed H3, our grid system for efficiently optimizing ride pricing and dispatch" | Introduction | company_asserted | pass |
| 20 | Uber says millions of events happen in its marketplace every day | "Every day, millions of events occur in the Uber marketplace." | Analysis using grids | company_asserted | pass |
| 21 | H3 is open source on GitHub | "The H3 indexing system is open source and available on GitHub." | Getting started | company_asserted | pass (state as of 2018) |
| 22 | The H3 library is written in C, with bindings for several languages | "The H3 library itself is written in C, and bindings are available for a number of languages." | Getting started | company_asserted | pass |
| 23 | Python and Go bindings exist | "Bindings are coming soon for Python and Go." (2018 status only) | Getting started | company_asserted | weakened: say "in 2018 Uber said Python and Go bindings were coming soon" |
| 24 | Worked example: the same area takes 10,633 hexagons uncompacted and 901 compacted (level 6, California) | "The uncompact representation has 10,633 hexagons at resolution 6, but the compact representation has 901 hexagons at resolutions up to 6." | Getting started, after Fig. 11 | derivation (worked example) | pass, labelled "example count, not a benchmark" |
| 25 | Compacting cuts the count about 12 times | Our arithmetic: 10,633 / 901 = 11.8. | n/a | derivation (ours) | weakened: say "for this one example, 901 instead of 10,633" |
| 26 | H3 is fast or accurate (any speed or accuracy number) | Not in post. | n/a | n/a | rejected (remove) |
| 27 | Checking whether a point is in a cluster is as efficient as a set lookup | "Determining membership of a cluster is as efficient as a set lookup operation." | Analysis using grids | company_asserted | rejected (vague, unmeasured; do not use) |
| 28 | Directed edges between cells are stored as 64-bit integers | "Directed edges can be stored as 64-bit integers" | Getting started, after Fig. 12 | model_design | pass |
| 29 | Uber says postal-code zones have shapes and sizes that are not useful for analysis | "such areas have unusual shapes and sizes which are not helpful for analysis" | Analysis using grids | company_asserted | pass (attribute to Uber) |

**Counts (29 rows): 23 pass, 3 weakened, 3 rejected.** Rejected: rows 6, 26, 27. Weakened: rows 17, 23, 25.

## Tag terms (background knowledge vs the post)

| Term we might tag | In the post? | Phrase |
|---|---|---|
| hexagonal grid | yes | "hexagonal, hierarchical indexes" (Introduction) |
| spatial index | yes | title |
| map projection | yes | "For map projection, we chose to use gnomonic projections" (H3) |
| icosahedron | yes | "icosahedron faces" (H3) |
| discrete global grid | yes | "forming a geodesic discrete global grid system" (H3) |
| pentagon (in grid) | yes | "twelve pentagons" (H3) |
| surge pricing | yes | "we calculate surge pricing" (Analysis using grids) |
| dispatch | yes | "ride pricing and dispatch" (Introduction) |
| quantization error | yes | "quantization error" (Analysis using grids) |

## Notes and uncertainty

- The post has no section anchors. Story links can point only at the page URL plus the heading name. This is weaker than the arXiv anchors used for `size-shapes-life`; the lead should decide how to show the location.
- The post is dated 2018. "Open source" and "bindings coming soon" describe that date, so we say so.
- The 1/7 area ratio is approximate: finer cells only approximately fit inside a parent cell. Dropping that caveat would overstate the claim.
- The count of base cells (122) is not the count of faces times cells (200); the post gives the reason only as "Some cells are contained by more than one face." It does not give the arithmetic.
- Row 6 (110 hexagons at level 0) is removed: the post does not state that the 12 pentagons are base cells.
