# AGENTS.md: start here

This file is for any AI coding agent (or person) picking up **The Geeky Times**. It's tool-neutral: nothing here
depends on a specific model or vendor. Read this first, then follow the links. Keep it up to date when you change
direction (see "Keeping this file true").

## What we're building

**The Geeky Times** explains research to anyone, kids included, with no background knowledge needed. Each story turns a
research paper or a company engineering blog post into:

- a newspaper-style page with a plain-language summary,
- animated, hand-drawn illustrations and comic strips (no stock video),
- clearly separated **illustrations** (invented teaching numbers) and **evidence** (real, cited results).

Product goal: "TikTok/Instagram, but for intellectuals". Fast, visual, swipeable, and still trustworthy.
The first story is "Attention Is All You Need" (Vaswani et al., 2017). It's the reference for tone and style.

## Non-negotiable principles

1. **Kid-level language.** Short sentences and everyday metaphors. Every technical idea also gets its real name
   ("Grown-up words: …").
2. **Every claim is labelled.** Exactly one of: "Illustration · numbers invented", "From the paper · model design",
   or "Measured result" plus source trust (peer-reviewed / preprint / company-reported). Real claims link to the
   exact section. The labels live in the data and are rendered the same way everywhere.
3. **Fact-check before publishing.** Every evidence number and every `paper`-basis tag is checked against the source.
   See `skills/fact-check/`.
4. **The UI renders data.** No story is hard-coded in components. Content lives in JSON now and a database later;
   media lives in files now and a CDN/S3 later.
5. **Original work only.** Write our own explanations and drawings. Never copy a source's text, figures or branding
   (blog posts especially). Short quotes only, with attribution.

## Stack and commands

React 19 + TypeScript (strict) + Vite. Node 20.19+ / 22.12+. Python 3 for drawing tools.

```bash
npm install
npm run dev        # runs `npm run data` first, then Vite on :5173
npm run data       # validate all content + tags, build public/data/search-index.json
npm run build      # data check + typecheck + production build to dist/
npm run lint       # oxlint
npm run draw       # regenerate the Attention paper's comic SVGs (tools/draw_attention.py)
```

Before you finish any change: run `npm run build` and `npm run lint`. Look at the result in a browser at
**1280px desktop** and **375px phone** width, and check there's no horizontal scroll and no console errors.

## Repo map

```
AGENTS.md                 you are here (CLAUDE.md / GEMINI.md just point here)
docs/
  decisions.md            every product/tech decision so far, with the reason (read this second)
  product-plan.md         navigation, front page, issues & volumes, graph, blogs, search: the target product
  data-model.md           current JSON model + target database schema (class diagram)
  roadmap.md              what's done, what's next, in order
  tagging.md              tag rules
skills/                   step-by-step playbooks any agent can follow (open SKILL.md format)
design/                   exported mockups (PNG + standalone HTML) and the review brief: design/README.md
prompts/                  prompt templates used by the AI converter (tag-paper.md, …)
public/data/              content: site.json, tags.json, papers/<slug>.json (search-index.json is generated)
public/media/<slug>/      standalone animated SVGs (moving to a CDN later)
src/
  types.ts                the content model: the contract between data and UI
  App.tsx                 routes: / (front page), /papers/<slug>, ?feed, ?search
  pages/                  HomePage (bento), PaperPage, FeedPage (swipe), SearchPage
  blocks/                 one component per content block type (lead, story, comic, facts)
  components/             MediaView (svg/image/video), Rich (safe captions), TagShelf, Masthead, motion
  lib/                    front.ts (front page layout), tags.ts (search), motion.ts, mediaBase.ts
  styles/edition.css      the newspaper look
scripts/build-index.ts    content validator + search index builder
tools/                    media_kit.py (drawing kit) + draw_attention.py (per-paper drawings)
```

## How the content works (short version)

- `public/data/site.json` lists papers. `papers/<slug>.json` = metadata + `summary` + `tags` + ordered `blocks`.
- Block types: `lead`, `story`, `comic`, `facts` (see `src/types.ts`). Adding one means: a type, a component in
  `src/blocks/`, and a registry entry.
- Media entry = `{type: svg|image|video, src, width, height, alt}`, with `src` relative to `mediaBaseUrl`.
- `npm run data` turns each paper into **moments** (comic strips, chapters, facts) for the front page and feed.
- Tags come from a shared vocabulary (`public/data/tags.json`) with 13 facets, parent tags and aliases.

Full details: `docs/data-model.md`, `docs/tagging.md`, `README.md`.

## Working agreements

- **Git:** never commit or push to `main`. Work on a `feature/<topic>` branch, push it, and open a PR. The owner
  merges.
- **Canvas before code (owner's rule):** show any visual or layout change on the design canvas first, with 1–2
  options, and build it into the app only after the owner picks one. Keep tiles calm: one illustration, real data in a
  line or two, no stacked gimmicks.
- **Don't break data compatibility silently.** Bump `schemaVersion` for breaking changes.
- **Accessibility:** real buttons and links, alt text on media, `prefers-reduced-motion` respected, animations
  pause off-screen.
- **Design language:** cream newsprint (`#f6f0df`), ink (`#27251e`), red accent (`#a13324`), Georgia serif
  headlines, Courier labels, halftone dots, muted cartoon colours, word-buddy characters. Front page = layout **D**
  (broadsheet above the fold, soft bento below). Desktop first, mobile next.
- **Navigation is the same on every page:** Front page · Explore (Topics, Storylines, Map) · Issues · Real world ·
  Snacks · Search.
- **Every component ships responsive and accessible:** no horizontal overflow at 375px, labels ≥12px, 44px tap
  targets, keyboard rails, reduced motion respected.
- **Ask before** anything public or irreversible (publishing, pushing to main, contacting companies, buying domains).

## Current status (keep updated)

- Done: data-driven React site, Attention story with comic strips, tags + search, bento front page + swipe feed
  (branches `feature/paper-tags` → `feature/home-bento` → `feature/project-knowledge`, stacked and not yet merged).
- Designing: front page **D**, issue page, story family tree, company page, explore map, data model. The
  exported images are in `design/exports/`, with a review brief in `design/README.md`; the editable source is a
  claude.ai design canvas (copied into `design/canvas-source/`).
- Design review by Codex (2026-11-04) accepted. Changes are recorded as decisions 18–25.
- Next: see `docs/roadmap.md`. Fixtures from a second field and a real company blog come before more pages.

## Keeping this file true

When a decision changes, update `docs/decisions.md` (add a new entry; don't rewrite history) and the matching
section here. When you finish a roadmap item, tick it in `docs/roadmap.md`. A future agent should be able to resume from
these files alone, without the chat history.
