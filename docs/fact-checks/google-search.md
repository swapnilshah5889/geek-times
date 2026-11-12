# Fact-check: "The Anatomy of a Large-Scale Hypertextual Web Search Engine" (Brin and Page, 1998)

Source: Sergey Brin and Lawrence Page, "The Anatomy of a Large-Scale Hypertextual Web Search Engine", Computer Science Department, Stanford University, Stanford, CA 94305. Canonical URL used in the story: http://infolab.stanford.edu/~backrub/google.html (the original Stanford-hosted page).
Fetched and checked on 2026-11-07. The live Stanford host refused connections from the check environment, so the text was read from the Wayback Machine copy of the same URL (https://web.archive.org/web/2020/http://infolab.stanford.edu/~backrub/google.html, 78,863 bytes). Quotes were matched against that text. The page's own note says there are two versions of the paper (a longer web and CD-ROM version, and a shorter printed version); this check covers the web version only.
Authors in the order printed: Sergey Brin, then Lawrence Page.

**What is in the paper:** the PageRank definition and its "random surfer" picture, anchor text, the architecture (distributed crawlers, repository, indexer, sorter, barrels, lexicon, inverted index, searcher), the data structures, storage and timing results, one example query, and a discussion of advertising bias.
**What is not in the paper:** the "web of friends", "vote", "librarian" and "book index" metaphors; any claim about what Google later became; any PageRank iteration count; any query time in milliseconds.

**Location convention.** The page has only a few named anchors: `#pr` (starts at §2.1), `#anchor` (§2.2), `#data` (§4.2), `#hits` (§4.2.5), `#a` (Appendix A), `#ref`. Other sections have no anchor, so their links point at the page and the fact's label names the section. Abstract and §5 tables are located by section number and table name.

**Result key.** `pass` = the claim as worded is in the paper, or is a plain-language restatement. `weakened` = the wording went beyond the paper or could not be confirmed; the Result column says what was done. `rejected` = not in the paper and not supported; the Result column says what was done.

## Bibliographic claims

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 1 | Full title is "The Anatomy of a Large-Scale Hypertextual Web Search Engine" | Same, in the page heading | Title | metadata | pass |
| 2 | Authors, in order: Sergey Brin, Lawrence Page | "Sergey Brin and Lawrence Page" | Title | metadata | pass |
| 3 | Authors were at Stanford University, Computer Science Department | "Computer Science Department, Stanford University, Stanford, CA 94305" | Title | metadata | pass |
| 4 | Published at WWW7, 1998 | The paper text prints no venue line or year. The page carries the meta tag `WWW7-SIN`, and its note refers to "the conference CD-ROM". The reference list cites sibling papers at the "Seventh International Web Conference (WWW 98). Brisbane, Australia, April 14-18, 1998" | `<meta name="WWW7-SIN">`; note before §1; References | metadata | weakened: year 1998 and the WWW7 venue come from the brief and the page metadata, not from a printed venue line. The venue tag is `background`, not `paper` |
| 5 | Trust level is peer-reviewed | The text never says it was reviewed. The only hints are the conference CD-ROM note and the WWW7 meta tag | n/a | metadata | weakened: `peer_reviewed` is kept per the brief, but this check could not confirm the review from the paper itself. Lead should confirm against the WWW7 proceedings before release |
| 6 | Page count | Not given in the web version | n/a | metadata | weakened: no page count is stated anywhere in the story |

## Facts, hook, summary (`facts[]`, `hook`, `summary`)

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 7 | Fact 1 and hook stat: the prototype had at least 24 million pages | "a full text and hyperlink database of at least 24 million pages"; Table 1: "Number of Web Pages Fetched 24 million" | Abstract; §5.1 Table 1 | measured_result | pass. Note: §5.2 says "roughly 9 days to download the 26 million pages (including errors)". The story uses the Table 1 figure of fetched pages, 24 million |
| 8 | Fact 2: the authors built link maps with as many as 518 million links | "We have created maps containing as many as 518 million of these hyperlinks" | §2.1, `#pr` | measured_result | pass. This is a different count from the "322 million link dataset" in §4.2.3; the story only uses 518 million, with "as many as" |
| 9 | Fact 3: the damping factor d is usually 0.85 | "We usually set d to 0.85." | §2.1.1, `#pr` | model_design | pass |
| 10 | Fact 4: one hit takes 2 bytes and holds position, letter size and capitalization; hit lists take most of the space | "Our compact encoding uses two bytes for every hit"; "Hit lists account for most of the space used in both the forward and the inverted indices" | §4.2.5, `#hits` | model_design | pass |
| 11 | Fact 5: fetched pages total 147.8 GB; the compressed repository is 53.5 GB | Table 1: "Total Size of Fetched Pages 147.8 GB"; "Compressed Repository 53.5 GB" | §5.1 Table 1 | measured_result | pass |
| 12 | Fact 6: most searches took 1 to 10 seconds, mostly disk reading | "The current version of Google answers most queries in between 1 and 10 seconds. This time is mostly dominated by disk IO over NFS" | §5.3 | measured_result | pass. The brief expected milliseconds; the paper reports seconds, so the story says seconds |
| 13 | Comic 5c: a repeat of "al gore" took 0.06 seconds | Table 2: "al gore ... Same Query Repeated (IO mostly cached) ... Total Time(s) 0.06" | §5.3 Table 2 | measured_result | pass |
| 14 | Summary: keyword matching returned a lot of junk and people can't sort the web by hand | "Automated search engines that rely on keyword matching usually return too many low quality matches"; human lists "cannot cover all esoteric topics" | §1 | model_design | pass (restated) |
| 15 | Summary: pages are ranked by who links to them (PageRank) | "it makes use of the link structure of the Web to calculate a quality ranking for each web page. This ranking is called PageRank" | §2, §2.1 | model_design | pass |
| 16 | Summary: searches are answered from a big word-to-pages index | "The searcher ... uses the lexicon ... together with the inverted index and the PageRanks to answer queries" | §4.1 | model_design | pass |
| 17 | Hook teaser: the question "which page is best" is the one the paper answers | PageRank is "an objective measure of its citation importance that corresponds well with people's subjective idea of importance" | §2.1, `#pr` | model_design | pass (a question, not a claim of certainty) |

## Story chapters

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 18 | Ch. 1: in 1997 search engines returned a lot of junk | "'Junk results' often wash out any results that a user is interested in"; the paper dates this to "the Web of 1997" | §1.3.1 | background | pass |
| 19 | Ch. 1: people only look at the first few results | "People are still only willing to look at the first few tens of results." | §1.3.1 | background | pass |
| 20 | Ch. 1: a library where new books arrive every minute | Metaphor | n/a | scenario | pass as scenario (chapter is `illustration`) |
| 21 | Ch. 2: a vote from a well-liked page counts for more | PageRank "extends this idea by not counting links from all pages equally" | §2.1.1, `#pr` | model_design | pass (the paper says "citation", not "vote"; "vote" is our word) |
| 22 | Ch. 2: a page that links to many pages splits its vote | "normalizing by the number of links on a page"; formula term PR(T)/C(T) | §2.1.1, `#pr` | model_design | pass |
| 23 | Ch. 2: pages cited from many places, or from a few important ones, rise | "pages that are well cited from many places around the web are worth looking at" and a page with one citation from the Yahoo! homepage is "also generally worth looking at" | §2.1.2, `#pr` | model_design | pass |
| 24 | Ch. 3: names crawler, repository, inverted index | "distributed crawlers"; "repository"; "the inverted index" | §4.1 | model_design | pass |
| 25 | Ch. 3: after matching all words, results are ranked by word match and PageRank | "Scan through the doclists until there is a document that matches all the search terms"; "the IR score is combined with PageRank to give a final rank" | §4.5, §4.5.1 | model_design | weakened: first draft said "puts the high-PageRank ones first", which drops the word-match score. Fixed in the JSON |
| 26 | Ch. 4: many top results for "bill clinton" were from the White House site | "A number of results are from the whitehouse.gov domain which is what one may reasonably expect" | §5 (Figure 4 caption area) | measured_result | weakened: first draft said "mostly". Fixed in the JSON to "Many of" |
| 27 | Ch. 4: none of the results were broken links | "All of the results are reasonably high quality pages and, at last check, none were broken links." | §5 | measured_result | pass |
| 28 | Ch. 4: this is largely because they have high PageRank | "This is largely because they all have high PageRank." | §5 | measured_result | pass |
| 29 | Ch. 4: no full user study; this is the authors' own experience | "a complete user evaluation is beyond the scope of this paper, our own experience with Google has shown it to produce better results"; "an extensive user study ... we do not have room for here" | §5 | measured_result | pass |
| 30 | Ch. 4: prototype with at least 24 million pages | See row 7 | Abstract | measured_result | pass |
| 31 | The brief's arc "the first results real humans trusted" | Not in the paper. The paper reports only the authors' own judgement | n/a | claim | rejected: not used. Ch. 4 reports only what the authors say, with the no-user-study caveat |

## Comic strips (per panel)

Strip 1 "The web is a web of friends" (illustration), strip 2 "A popularity vote that keeps updating", strip 3 "The librarian who walks the web", strip 4 "A book index for the whole web", strip 5 "Answering one search" (strips 2 to 5 are `model_design`).

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 32 | Strip 1a: pages are like kids; a link is "go meet my friend" | Metaphor | n/a | scenario | pass as scenario |
| 33 | Strip 1b: the authors treated links like citations; maps of as many as 518 million links | "The citation (link) graph of the web is an important resource"; row 8 | §2.1, `#pr` | model_design | pass |
| 34 | Strip 1c: a link from a famous page should count more | "not counting links from all pages equally" | §2.1.1, `#pr` | model_design | pass |
| 35 | Strip 2a: a page's score is shared equally among its links; four links give a quarter each | Formula term PR(T1)/C(T1), where C is "the number of links going out of page A". The 4-link page is invented and said to be "made-up" | §2.1.1, `#pr` | model_design | pass (example is a scenario) |
| 36 | Strip 2b: scores can be found with a simple repeating calculation | "PageRank or PR(A) can be calculated using a simple iterative algorithm" | §2.1.1, `#pr` | model_design | pass. The paper gives no iteration count, and the story gives none |
| 37 | Strip 2b: PageRank is passed on again and again | "recursively propagating weights through the link structure of the web" | §2.1.2, `#pr` | model_design | pass |
| 38 | Strip 2c: the random surfer clicks links and sometimes gets bored and jumps to a random page | "keeps clicking on links, never hitting 'back' but eventually gets bored and starts on another random page" | §2.1.2, `#pr` | model_design | pass |
| 39 | Strip 2c: d is the damping factor, usually 0.85 | Row 9 | §2.1.1, `#pr` | model_design | pass |
| 40 | Strip 2c: how d relates to boredom | The text says d "is the probability at each page the 'random surfer' will get bored", but the formula multiplies the link term by d and gives (1-d) to the jump term, so the two statements disagree | §2.1.1 vs §2.1.2, `#pr` | model_design | weakened: the story names the surfer and d but does not say which is the boredom chance |
| 41 | Not used: "the PageRanks sum to one" | "the sum of all web pages' PageRanks will be one" | §2.1.1, `#pr` | model_design | rejected for use: as printed, the formula (1-d) + d(...) does not give a sum of one, so the story leaves it out |
| 42 | Strip 3a: the URLserver sends lists of URLs to the crawlers | "There is a URLserver that sends lists of URLs to be fetched to the crawlers" | §4.1 | model_design | pass |
| 43 | Strip 3b: about 3 crawlers, about 300 connections each, over 100 pages per second with four crawlers | "we typically ran about 3"; "Each crawler keeps roughly 300 connections open at once"; "can crawl over 100 web pages per second using four crawlers" | §4.3 | model_design | pass (peak speed; the sustained rate of 48.5 pages per second in §5.2 is not used) |
| 44 | Strip 3c: the storeserver compresses pages and files them in the repository with a docID | "The storeserver then compresses and stores the web pages into a repository. Every web page has an associated ID number called a docID" | §4.1 | model_design | pass |
| 45 | Strip 3c: the repository keeps the full page | "The repository contains the full HTML of every web page." | §4.2.2 | model_design | pass |
| 46 | Strip 4a: the indexer writes down each word with position, rough letter size and capitalization | "Each document is converted into a set of word occurrences called hits. The hits record the word, position in document, an approximation of font size, and capitalization." | §4.1 | model_design | pass |
| 47 | Strip 4b: the sorter flips the lists to word-to-pages, the inverted index | "The sorter takes the barrels ... and resorts them by wordID to generate the inverted index." | §4.1 | model_design | pass (book-index comparison is ours) |
| 48 | Strip 4c: each hit is two bytes; hits in a title, address or link text get special treatment | "Fancy hits include hits occurring in a URL, title, anchor text, or meta tag." Fancy hits are encoded differently and the title and anchor barrels are searched first | §4.2.5 `#hits`; §4.2.7 | model_design | pass |
| 49 | Strip 5a: the searcher turns words into word IDs and looks up each word's list | "Parse the query. Convert words into wordIDs. Seek to the start of the doclist" | §4.5 (Figure 4 steps) | model_design | pass |
| 50 | Strip 5b: pages must match all the words; score uses where words appear and PageRank | "a document that matches all the search terms"; hit types "title, anchor, URL, plain text large font, plain text small font"; "hits occurring close together ... weighted higher"; "the IR score is combined with PageRank" | §4.5, §4.5.1 | model_design | pass |
| 51 | Strip 5c: the best are shown first | "Sort the documents that have matched by rank and return the top k." | §4.5 | model_design | pass |
| 52 | Strip 5c: most searches 1 to 10 seconds, mostly disk reading | Row 12 | §5.3 | measured_result | pass |
| 53 | Strip 5c: repeat of "al gore" 0.06 seconds once cached | Row 13 | §5.3 Table 2 | measured_result | pass |

## Paper-basis tags (spot-check of `tags[]`)

Evidence anchors used: the page root, `#pr`, `#anchor`. All three exist as `<a name>` anchors on the page. Tags with no section anchor point at the page root and are supported by the section named below.

| Tag | Evidence | Section and phrase | Result |
|---|---|---|---|
| `field/computer-science` | page | Department of Computer Science, Stanford | pass |
| `area/information-retrieval` (proposed) | page | Keywords: "Information Retrieval"; §3.1 "Information Retrieval" | pass |
| `concept/pagerank` (proposed) | `#pr` | "PageRank: Bringing Order to the Web" | pass |
| `concept/link-analysis` (proposed) | `#pr` | "makes use of the link structure of the Web to calculate a quality ranking" | pass |
| `concept/hyperlink-graph` (proposed) | `#pr` | "The citation (link) graph of the web" | pass |
| `concept/anchor-text` (proposed) | `#anchor` | "Anchor Text"; "we associate it with the page the link points to" | pass |
| `concept/inverted-index` (proposed) | page | §4.2.7 "Inverted Index" | pass |
| `concept/random-surfer` (proposed) | `#pr` | §2.1.2 "random surfer" | pass |
| `technique/web-crawler` (proposed) | page | §4.3 "Crawling the Web" | pass |
| `task/web-search` (proposed) | page | Title and abstract | pass |
| `organization/stanford-university` (proposed) | page | Title block | pass |
| `author/sergey-brin`, `author/lawrence-page` (proposed) | page | Title block | pass |
| `use/search-engines` | none | `background` only | background |
| `organization/google` | none | `background` only. The paper names the system Google; the company is not in the paper | background |
| `venue/www7-1998` (proposed) | none | `background` only; see row 4 | background |
| `everyday/*` | none | `editorial` | editorial |

**Counts (53 rows): 45 pass, 6 weakened, 2 rejected.** Weakened: rows 4, 5, 6, 25, 26, 40. Rejected: rows 31 and 41.

## Safe to use now

Facts 1 to 6 (rows 7 to 12); the hook stat (24 million pages); chapter 4 as corrected (rows 26 to 30); all comic panels except for the d-and-boredom link (row 40) and the sum-to-one line (row 41), which are not in the story.

## Open items for the lead

1. Peer-review status of the WWW7 paper is not stated in the text (rows 4 and 5). Confirm against the conference proceedings before the story ships as `peer_reviewed`.
2. The paper prints no PageRank iteration count, so none appears in the story.
3. The live Stanford host was unreachable from the check environment; re-open it once to confirm it matches the Wayback copy.
