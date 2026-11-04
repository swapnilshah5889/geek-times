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

## Pages (target routes)

| Route | Page |
|---|---|
| `/` | Front page: the current issue (layout D) plus "Keep exploring" |
| `/stories/:slug` | A story. Breadcrumb to its issue; family tree; "more in this topic"; next in storyline |
| `/issues/:volume/:number` | Issue: cover, theme, editor's note, table of contents, its stories, previous/next issue |
| `/volumes/:volume` | Wall of issue covers (Volume 0 shows special editions) |
| `/topics/:tag` | All stories for a tag (facet-aware, includes child tags) |
| `/storylines/:slug` | A guided path through related sources, oldest to newest |
| `/companies/:slug` | Index of our explainers of one company's engineering posts (plain names, no logos) |
| `/map` | Explore map of the whole graph by field |
| `/feed` | Snack mode: swipe through moments |
| `/archive` and `/search` | Everything, with filters |

The current build uses query parameters (`?paper=`, `?feed`, `?search`). Moving to real routes (React Router) is on
the roadmap.

## Front page (layout D)

**Above the fold (broadsheet).**
- Masthead: date, title, motto, and a section bar (AI & computers, Biology, Space, Physics, Medicine, Snacks, Search).
- The current issue's lead story across 2/3 of the width.
- A column of 2–3 features, separated by thin rules.

**Below the fold: "Keep exploring"** (a soft bento: light borders, rounded corners, gentle shadows), with sections in
this order:
1. **More from this issue:** the other features and briefs.
2. **Swipe the snacks:** a rail of moments that opens the feed.
3. **In the real world:** stories from company engineering blogs.
4. **Topic shelves:** a horizontal rail per topic, each with "See all".
5. **Storylines:** "How X evolved" paths.
6. **Numbers from the papers:** real, cited facts, each with a trust badge.
7. **Grown-up words:** a glossary hub; each term links to every story that uses it.
8. **From the vault / On this day:** classics and anniversaries.
9. **Back issues:** a rail of past issue covers leading to the volume pages.
10. **Get each issue:** newsletter signup.
11. Later, with analytics: most read this week; picked for younger readers.

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
- **Explore map:** zoomable, clustered by field. Cytoscape.js or Sigma.js once the graph is large.

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
