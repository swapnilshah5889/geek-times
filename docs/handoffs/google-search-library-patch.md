# Library patch: `google-search`

Status: spec for the lead to apply. Prepared 2026-11-07 on `v1`. Nothing in `data/seed/library.json` or `data/seed/tags.json` has been edited. Story file: `data/seed/papers/google-search.json`. Fact-check: `docs/fact-checks/google-search.md`. Media: `public/media/google-search/` (27 placeholder SVGs).

## 1. `stories[]` entry

```json
{
  "id": "google-search",
  "real": true,
  "sample": false,
  "kind": "paper",
  "trust": "peer_reviewed",
  "role": "lead",
  "fields": ["sw"],
  "headline": "The web's biggest",
  "accent": "popularity vote.",
  "dek": "The web had millions of pages and no good way to sort them. Two students at Stanford had an idea: a page matters if other pages point to it. This paper describes the search engine they built around it.",
  "desk": "Computer science / Search and the web",
  "title": "The Anatomy of a Large-Scale Hypertextual Web Search Engine",
  "authors": "Sergey Brin, Lawrence Page",
  "year": 1998,
  "minutes": 10,
  "note": "comic + facts"
}
```

Notes for the lead:
- `trust: "peer_reviewed"` follows the brief. The paper's text does not print a venue line or say it was reviewed (fact-check rows 4 and 5). Confirm against the WWW7 proceedings before release, or set `preprint` if it cannot be confirmed.
- `role`: existing stories use `lead` (Transformer, size-shapes-life) and `real_world` (H3). `lead` is my guess; change it if the slot is taken.
- `desk` uses the same string as the story file's `desk`. The existing library desks are "AI & language", "Biology & physics" and "Real world  /  Maps & rides", so shorten to "Search & the web" if you prefer that style.
- `fields`: the library has no `cs` field. Its fields are `ai`, `bio`, `space`, `physics`, `sw` ("Software & systems"). I recommend `sw`. `ai` is the alternative but PageRank is not machine learning. If you want a dedicated "Computer science" field, add it to `fields[]` with a cluster instead.
- `data/seed/papers/google-search.json` is not yet in `site.json` equivalents. In the Supabase-only flow the lead publishes it; I ran no npm script.

## 2. `nodes[]` entry

```json
{
  "id": "google-search",
  "title": "The Anatomy of a Large-Scale Hypertextual Web Search Engine",
  "short": "Google & PageRank",
  "authors": "Brin and Page",
  "year": 1998,
  "field": "sw",
  "type": "paper",
  "story": "google-search",
  "x": 640,
  "y": 480,
  "blurb": "Ranks web pages by who links to them, and answers searches from a word-to-pages index. The first detailed public description of a large web search engine, by its own account."
}
```

Notes:
- The task asked for `slug`; the existing nodes use `id` plus `story`, so I followed the existing shape.
- Map coordinates: the `sw` cluster is centred at (620, 460) with radii 120 by 80, so (640, 480) sits inside it. The `sw` and `physics` clusters overlap on the map (centres 20 px apart, physics is 160 by 110). Pick coordinates on the right-hand side of `sw` (x of 660 to 700) if you want to stay clear of the physics nodes at (560, 450) and (620, 430). H3 has no node yet, so the cluster is empty.
- The blurb's "by its own account" comes from the abstract: "the first such detailed public description we know of to date". It is a claim by the authors, so it is worded that way.

## 3. `relations[]` edges

**Verified from this paper: none involve an existing node.**

No node in the current library is a plausible, citable relative of this paper from the paper's own text. Nodes in the library today are ML, biology, physics and space papers.

**Unverified candidates (do NOT add as verified):**

| from | to | kind | note | status |
|---|---|---|---|---|
| `google-search` | `transformer` | none | Search and large language models are both used to find answers, but there is no citation link in either direction | do not add |
| `google-search` | `bert` | uses_method | Later search products use BERT-style models; this is background knowledge, not in the Google paper or the Transformer fact-check | **unverified**, to be fact-checked against the BERT paper or a Google source, not against this paper |

I recommend adding no edges now. A descendant edge such as "PageRank to a later link-analysis paper" can only be cited from the later paper, so its fact-check belongs in that paper's story.

**Edges that point INTO this paper, which the Google paper itself can verify (nodes do not exist yet):**

| from (new node needed) | to | kind | note | cited |
|---|---|---|---|---|
| `pagerank-citation-ranking` ("The PageRank Citation Ranking: Bringing Order to the Web", Page, Brin, Motwani, Winograd, 1998 manuscript) | `google-search` | `builds_on` | The Google paper says PageRank "is described in detail in [Page 98]" | true; §2 and reference [Page 98] |
| `wwww` ("GENVL and WWWW: Tools for Taming the Web", McBryan, 1994) | `google-search` | `builds_on` | "This idea of propagating anchor text to the page it refers to was implemented in the World Wide Web Worm" (§2.2, `#anchor`) | true |
| `hits-kleinberg` ("Authoritative Sources in a Hyperlinked Environment", Kleinberg, 1998) | `google-search` | `builds_on` | Cited only as one of several works showing "optimism that the use of more hypertextual information can help improve search" (§1.3.1); a weak link, so prefer to leave it out | true, but weak |

None of these three papers has a story yet. The lead can add them as nodes later, or skip them.

## 4. Proposed tags

All of these are already attached to the story with `source: "ai"`, `status: "suggested"` and a `proposed` block (the owner approves them into `tags.json`). The exact `tags.json` shape is `{ "id", "facet", "label", "parent"?, "aliases"?, "description"? }`.

```json
[
  { "id": "area/information-retrieval", "facet": "area", "label": "Information retrieval", "aliases": ["IR", "finding documents"], "description": "Finding the documents that answer a question." },
  { "id": "concept/pagerank", "facet": "concept", "label": "PageRank", "aliases": ["page rank", "link ranking"], "description": "A score for how important a page is, based on who links to it." },
  { "id": "concept/link-analysis", "facet": "concept", "label": "Link analysis", "aliases": ["hyperlink analysis", "citation graph"], "description": "Using the links between pages to learn about them." },
  { "id": "concept/hyperlink-graph", "facet": "concept", "label": "Hyperlink graph", "aliases": ["link graph", "web graph"], "description": "The web seen as pages (dots) joined by links (lines)." },
  { "id": "concept/anchor-text", "facet": "concept", "label": "Anchor text", "aliases": ["link text"], "description": "The clickable words of a link." },
  { "id": "concept/inverted-index", "facet": "concept", "label": "Inverted index", "aliases": ["search index", "word-to-pages index"], "description": "A list that says, for each word, which documents contain it." },
  { "id": "concept/random-surfer", "facet": "concept", "label": "Random surfer", "parent": "concept/pagerank", "aliases": ["random walk"], "description": "An imaginary web user who keeps clicking links; used to explain PageRank." },
  { "id": "technique/web-crawler", "facet": "technique", "label": "Web crawler", "aliases": ["spider", "bot", "crawling"], "description": "A program that visits web pages and copies them for later use." },
  { "id": "task/web-search", "facet": "task", "label": "Web search", "aliases": ["search engine", "searching the web"], "description": "Finding web pages that answer what someone typed." },
  { "id": "use/search-engines", "facet": "use", "label": "Search engines", "aliases": ["Google Search", "web search engines"], "description": "Sites you type a question into to find web pages." },
  { "id": "organization/stanford-university", "facet": "organization", "label": "Stanford University", "aliases": ["Stanford"] },
  { "id": "author/sergey-brin", "facet": "author", "label": "Sergey Brin" },
  { "id": "author/lawrence-page", "facet": "author", "label": "Lawrence Page", "aliases": ["Larry Page"] },
  { "id": "venue/world-wide-web-conference", "facet": "venue", "label": "World Wide Web Conference", "aliases": ["WWW", "The Web Conference"] },
  { "id": "venue/www7-1998", "facet": "venue", "label": "WWW7 (1998)", "parent": "venue/world-wide-web-conference", "aliases": ["Seventh International World Wide Web Conference", "WWW 1998"] },
  { "id": "everyday/finding-things", "facet": "everyday", "label": "Finding things", "aliases": ["googling", "looking things up"] },
  { "id": "everyday/the-internet", "facet": "everyday", "label": "The internet", "aliases": ["websites", "the web"] }
]
```

Notes:
- `venue/world-wide-web-conference` is the parent of `venue/www7-1998` (like `venue/neurips` and `venue/neurips-2017`). It has no `proposed` block in the story file, because a parent only needs to exist in `tags.json`. Add it before the child.
- Existing tags used as-is: `field/computer-science`, `organization/google`, `everyday/smart-computers`.
- `concept/random-surfer` has `parent: concept/pagerank` (same facet, as the vocabulary requires).
- The story's `proposed` block for `venue/www7-1998` lists parent `venue/world-wide-web-conference`.
- Expect the validator to warn about suggested tags until they are approved. If any proposal is rejected, remove its tag line from the story file.
- `organization/google` is `background` (the paper names the system "Google", but the paper's authors are at Stanford).

## 5. Other things to apply

- `front` / `issues`: not touched; the owner decides placement.
- `storylines`: "machines-read" exists; this story does not belong in it. A "search and the web" storyline is optional.
- After applying, run `npm run data` (not run here) and look at the story at 1280px and 375px. The SVGs are grey placeholders in the 600x340, 440x215, 320x220 and 160x100 sizes the runbook names, with the short caption drawn inside each one.
