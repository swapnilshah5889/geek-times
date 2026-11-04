# Design exports for review

Desktop mockups for The Geeky Times, exported from the design canvas on 2026-11-04. They're the agreed direction
before building. The reasons behind them are in `../docs/decisions.md` and `../docs/product-plan.md`.

| # | Image | What it shows |
|---|---|---|
| 0 | [exports/0-front-page-d.png](exports/0-front-page-d.png) | Front page layout **D** (chosen): a broadsheet above the fold, a soft bento below |
| 1 | [exports/1-front-page-full.png](exports/1-front-page-full.png) | Front page D with the full "Keep exploring" (ten sections) |
| 2 | [exports/2-issue-page.png](exports/2-issue-page.png) | Issue page: cover, editor's note, contents with roles (lead/feature/brief/vault/real world) |
| 3 | [exports/3-story-family-tree.png](exports/3-story-family-tree.png) | A story page's family tree: a timeline of related papers |
| 4 | [exports/4-company-page.png](exports/4-company-page.png) | Company page for engineering-blog explainers (plain names, company-reported numbers) |
| 5 | [exports/5-explore-map.png](exports/5-explore-map.png) | Explore map of the whole graph, with filters and a detail panel |
| 6 | [exports/6-data-model.png](exports/6-data-model.png) | Target database class diagram (also in Mermaid in `../docs/data-model.md`) |

- `html/` has the same pages as standalone HTML. Open them in a browser to see the animations.
- `canvas-source/` has the original canvas files (`.dc.html` plus `canvas.json`), for reference.

## What's real and what's placeholder

- **Real:**
  - The Transformer story: headline, summary, illustrations and comic panels.
  - Its evidence numbers, all fact-checked: 6 + 6, 8, 512, 12 hours.
- **Samples:** anything marked "Sample", and placeholders like `[Company name]`, `[Year]`, `[n]`. These exist for
  layout only.
- **Not verified:** the family tree's papers are real, but the link types between them haven't been fact-checked yet.
  The page says "Mockup · links to be fact-checked".

## Review brief (for any reviewer, human or AI)

Please comment on:

1. **Reader experience:** is it clear where to start? Can a 10-year-old and an adult both find their way around? Is
   anything confusing or missing?
2. **Front page D:** do the ten "Keep exploring" sections earn their place? Is the order right? Is it too long?
3. **Trust:** are illustration, peer-reviewed and company-reported content always clearly told apart?
4. **Navigation model:** issues/volumes as packaging, plus topics, storylines, the graph and search for discovery. Does it hold
   together?
5. **Data model:** can it support everything in the pages above? Look for missing fields or relations, and things that
   will hurt at scale (for example the generic `Block`/`BlockItem`, and `Relation` between sources).
6. **Accessibility and responsiveness risks** to fix before building (mobile comes after desktop).
7. **Build order:** anything in `../docs/roadmap.md` that should move?

Constraints the designs must keep (from `../AGENTS.md`):
- kid-level language
- illustration ≠ evidence
- the UI renders data
- original work only
- the newspaper look

## Regenerating

The canvas is the editable source. To re-export after it changes:

1. Save the canvas files into a folder.
2. Run `python3 tools/export_canvas.py <canvas project dir> design/html Front Issue …`.
3. Screenshot each page with headless Chrome at 1440px wide (2328px for the data model), using
   `--force-prefers-reduced-motion` so animations show their final frame.
