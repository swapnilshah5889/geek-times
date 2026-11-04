# Product plan

The target product, as agreed with the owner on 2026-11-04. The reasons behind each part are in `decisions.md`.

## Building blocks

| Term | Meaning |
|---|---|
| **Source** | An original work: a research paper or a company engineering blog post (later talks, RFCs, patents). Has an original year and a trust level. |
| **Story** | Our illustrated explainer of one main source (plus supporting sources). Has its own permanent URL. |
| **Moment** | A bite-size piece of a story (one comic strip, chapter or fact) for front page tiles and the swipe feed. |
| **Issue** | A curated package of stories with a theme and an editor's note. Roles: lead, feature, brief, vault. |
| **Volume** | A year of issues. Volume 0 = launch special editions of classic papers. |
| **Storyline** | A guided path through the graph ("How machines learned to read"). |
| **Graph** | Sources linked by typed relations; the explained ones open as stories. |

## Global navigation

The same bar on every page: **Front page · Explore** (Topics, Storylines, Map) **· Issues · Real world · Snacks ·
Search**. Field names (AI, Biology…) appear inside Explore and Topics, not in the top bar.

## Labels readers see

- Every claim shows exactly one of:
  - **Illustration · numbers invented**
  - **From the paper · model design** (how it's built, e.g. 8 heads)
  - **Measured result**, followed by its source trust: peer-reviewed / preprint / company-reported
- Terms like peer-reviewed, company-reported, storyline and family tree get a one-line explanation the first time they
  appear (a tooltip or an inline sentence, like the family-tree detail panel).
- Story tabs: **The big idea · How it works · Family tree** ("papers before and after this one") **· Evidence ·
  Explore related ideas**.

## Pages (target routes)

| Route | Page |
|---|---|
| `/` | Front page: the current issue (layout D) plus "Keep exploring" |
| `/papers/:slug` | A story (decision 26). Breadcrumb to its issue; family tree; "more in this topic"; next in storyline |
| `/issues/:volume/:number` | Issue: cover, theme, editor's note, table of contents, its stories, previous/next issue |
| `/volumes/:volume` | Wall of issue covers (Volume 0 shows special editions) |
| `/topics/:tag` | All stories for a tag (facet-aware, includes child tags) |
| `/storylines/:slug` | A guided path through related sources, oldest to newest |
| `/companies/:slug` | Index of our explainers of one company's engineering posts (plain names, no logos), plus posts in the review queue |
| `/map` | Explore map of the whole graph by field |
| `/feed` | Snack mode: swipe through moments |
| `/archive` and `/search` | Everything, with filters |

The current build serves stories at `/papers/<slug>` (old `?paper=` links redirect there) and still uses query
parameters for `?feed` and `?search`. Moving the rest to real routes (React Router) is on the roadmap.

## Front page (layout D)

**Above the fold (broadsheet).**
- Masthead: date, title, motto, and a section bar (AI & computers, Biology, Space, Physics, Medicine, Snacks, Search).
- The current issue's lead story across 2/3 of the width.
- A column of 2–3 features, separated by thin rules.

**Below the fold: "Keep exploring"** (a soft bento: light borders, rounded corners, gentle shadows). Eight areas at
launch, in this order. **Each renders only when it has meaningful content:**
1. **More from this issue:** the other features and briefs.
2. **Swipe the snacks:** a rail of moments that opens the feed. Every card carries its claim label.
3. **Topics:** a horizontal shelf per topic, each with "See all".
4. **In the real world:** stories from company engineering blogs.
5. **Numbers from the papers:** structured facts, each labelled model design or measured result plus trust.
6. **Storylines:** "How X evolved" paths.
7. **From the vault and On this day:** classics and anniversaries.
8. **Back issues:** a rail of past issue covers leading to the volume pages.

Then **Get each issue** (newsletter signup). Grown-up words live inside stories and search for now. Rails must be
keyboard-operable, with visible focus.

## Search

- One box everywhere (⌘K).
- Results grouped: Stories · Moments · Topics · Grown-up words · Storylines · Issues · Companies.
- Filters: every tag facet, source type (paper/blog), trust level, company, our volume/issue, original year.
- Every result deep-links to the exact panel or fact.
- Today search runs in the browser over `search-index.json`. Later it becomes Postgres full-text plus tag-ancestor
  queries.

## Graph

- Points (nodes) are sources, explained or not.
- Relation types: builds on, improves on, uses the method of, puts into practice, disagrees with, same problem.
- Each relation has strength, basis and evidence (the citing sentence and section), origin (citation API / AI /
  editor) and review status.
- **Family tree** on each story: a timeline running left to right by year, with ancestors on the left and descendants
  on the right.
- **Explore map:** zoomable, clustered by field, with stacked filters, map and details on small screens. It always has an
  **accessible list view** of every node and real, labelled controls (e.g. the year range). Cytoscape.js or Sigma.js
  once the graph is large. Build it only once enough *verified* relations exist.
- **On mobile,** the family tree becomes a vertical timeline (or a controlled horizontal scroller).

## Publishing pipeline (target)

1. Add a source (arXiv ID / DOI / blog URL), or one arrives from a blog's RSS feed.
2. Fetch metadata, abstract, references and citations (OpenAlex, Semantic Scholar). Archive blog URLs.
3. The AI converter drafts the story (blocks, captions, comic panel briefs), facts, tags (`prompts/tag-paper.md`) and
   relations.
4. Automated checks (`npm run data`, plus fact checks against the source).
5. Editor review queue: approve, edit or reject. Approved stories publish immediately.
6. Every week, an issue is assembled from what went live, plus vault picks suggested by the graph.

## Copyright and trust

- Write our own text and drawings. Short quotes only, attributed and linked.
- Respect robots.txt and each site's terms. Consider asking companies for permission.
- Company-reported numbers are always labelled as such.
- Get legal advice before a commercial launch.
