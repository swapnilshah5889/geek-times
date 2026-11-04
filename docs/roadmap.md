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

## Next

1. [ ] **Design sign-off on the canvas.**
   - Pages: front page D with full "Keep exploring", issue page, story family tree, company page, explore map.
   - Class diagram of the target schema.
2. [ ] **Routing:** React Router with real paths (`/stories/:slug`, `/issues/:v/:n`, `/topics/:tag`, `/feed`,
       `/search`). Static hosting with an SPA fallback; consider pre-rendering for search engines.
3. [ ] **Content model v2 in JSON:** sources vs stories, issues/volumes as their own files, `issue_stories` roles,
       trust levels, relations, storylines. Keep the validator in step.
4. [ ] **Build front page D** from data (lead/features from the current issue; the Keep exploring sections).
5. [ ] **Issue, volume, topic and company pages.**
6. [ ] **Family tree view** on story pages (timeline) and a first explore map.
7. [ ] **Second and third real stories:** one paper from another field, and one company engineering blog post. They
       test that the model is general.
8. [ ] **Converter pipeline v1:** arXiv/DOI/blog URL in, draft story + tags + facts + relations out, review queue.
9. [ ] **Backend:** Postgres schema from `data-model.md`, an API serving `PublishedVersion` documents, media on S3 +
       CDN (with CORS for SVG inlining).
10. [ ] **Mobile UI pass** (after desktop is settled).
11. [ ] Newsletter, analytics ("most read"), and legal review (brand, copyright and fair use) before a public launch.
