# Roadmap

Tick items as they land. Keep the order unless the owner changes priorities.

## Done

- [x] Illustrated prototype for "Attention Is All You Need": lead plate, four-part picture story, BLEU evidence
- [x] Comic-strip "How the machine actually works" (6 strips) and illustrated evidence cards (facts checked on arXiv)
- [x] Data-driven renderer: JSON content, standalone SVG media, swappable `mediaBaseUrl`
- [x] React + TypeScript + Vite
- [x] Renamed to The Geeky Times
- [x] Tags: 13-facet vocabulary, 55 tags on the first story, validator, search page, "Filed under" shelf, AI tagging
      rules and prompt
- [x] Bento front page (first version) and swipe feed (`?feed`)
- [x] Front page layout exploration (A/B/C), with D chosen and softened
- [x] Tool-neutral project knowledge: `AGENTS.md`, `docs/`, `skills/`

## Next (order revised after the Codex design review)

Every item keeps two rules from day one: responsive stacking with no horizontal overflow, and the accessibility
criteria in `decisions.md` #24.

1. [x] **Apply the review to the designs and docs** (design export revision 2):
   - trust labels (claim kind + source trust)
   - stable navigation
   - eight front-page sections
   - plain-language labels and renamed story tabs
   - an accessible map
2. [ ] **Content model v2 + validators + migration from v1** (`docs/data-model.md` → Migrating).
3. [ ] **Two real fixtures that test generality:** one paper from another field, and one real company engineering post.
4. [ ] **Real routes and loaders** (React Router) reading the v2 fixtures.
5. [ ] **Front page D and the issue page.**
6. [ ] **Topic and company pages.**
7. [ ] **Story family tree** using *verified* relations only.
8. [ ] **Explore map**, once enough verified nodes and relations exist. Include the list view.
9. [ ] **Converter + editorial review queue:** papers and blogs, `FeedEntry` states, `RelationEvidence` review.
10. [ ] **Backend and storage:** Postgres, an API serving `PublishedVersion`, S3/CDN media with CORS.
11. [ ] **Mobile polish**, with responsive behaviour tested throughout.
12. [ ] Newsletter, analytics, and legal review (brand, copyright and fair use) before a public launch.
