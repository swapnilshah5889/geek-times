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
   or "Measured result" plus source trust (peer-reviewed / preprint / company-reported / journal-published without
   established external review). Real claims link to the
   exact section. The labels live in the data and are rendered the same way everywhere.
3. **Fact-check before publishing.** Every evidence number and every `paper`-basis tag is checked against the source.
   See `skills/fact-check/`.
4. **The UI renders data.** No story is hard-coded in components. The app reads Supabase views; JSON under `data/seed/`
   is the Git-tracked editorial backup and input for publish/import commands. The browser never reads the seed. Before V1,
   all story media moves to Supabase Storage and duplicate runtime copies are removed from `public/`. No sample, demo,
   mockup, unverified, or placeholder records/copy/art may render in any mode; show an honest empty state instead.
   Clearly stamped teaching illustrations may use invented numbers, but never count as evidence.
5. **Original work only.** Write our own explanations and drawings. Never copy a source's text, figures or branding
   (blog posts especially). Short quotes only, with attribution.

## Stack and commands

React 19 + TypeScript (strict) + Vite. Node 20.19+ / 22.12+. Python 3 for drawing tools.

```bash
npm ci
npm run dev        # Vite on :5173; the app reads Supabase views
npm run build      # TypeScript + production build to dist/
npm run lint       # oxlint
npm run prerender  # render DB-enumerated routes to dist/<route>/index.html (needs build + Supabase env)
npm run check:prerender
npm run check:hydration
npm run convert -- <arXiv-id-or-URL> [--kind paper|blog] [--trust preprint|peer_reviewed|journal_published]
npm run draw       # regenerate the Attention paper's comic SVGs (tools/draw_attention.py)
```

Before you finish any change: run `npm run build` and `npm run lint`. Look at the result in a browser at
**1280px desktop** and **375px phone** width, and check there's no horizontal scroll and no console errors.

## Repo map

```
AGENTS.md                 you are here (CLAUDE.md / GEMINI.md just point here)
.env.example              env variable names (no values); copy to .env (gitignored) and fill locally
docs/
  decisions.md            every product/tech decision so far, with the reason (read this second)
  product-plan.md         navigation, front page, issues & volumes, graph, blogs, search: the target product
  data-model.md           current Postgres model, Git seed/import shape, and runtime read path
  roadmap.md              what's done, what's next, in order
  tagging.md              tag rules
skills/                   playbooks any agent can follow (open SKILL.md format); start with skills/convert-paper
design/                   exported mockups (PNG + standalone HTML) and the review brief: design/README.md
prompts/                  prompt templates used by the AI converter (tag-paper.md, …)
data/seed/                Git-tracked editorial backup: site.json, tags.json, library.json, papers/<slug>.json
data/intake/              ignored, resumable conversion checkpoints and drafts
public/media/<slug>/      current local media source; moving live assets to Supabase Storage is a V1 merge gate
supabase/                 schema migrations (decisions 34, 48, 49) and README; applied with `npm run apply:migration`
src/
  types.ts                the content model: the contract between data and UI
  App.tsx                 routes: / (front page D), /papers/<slug>, /issues, /companies, /map, ?feed, ?search
  pages/                  HomePage (bento), PaperPage, FeedPage (swipe), SearchPage
  blocks/                 one component per content block type (lead, story, comic, facts)
  components/             MediaView (svg/image/video), Rich (safe captions), TagShelf, Masthead, motion
  lib/                    library.ts (stories, issues, graph helpers), routes.ts (all links), feed.ts (feed order), tags.ts (search), motion.ts, mediaBase.ts
  data/                   load.ts and source.ts (Supabase view reads; decision 51), initial-snapshot.ts (prerender hydration)
  styles/edition.css      the newspaper look
scripts/convert.ts        staged, resumable paper/blog conversion and preview preparation
scripts/convert/model.ts  provider-neutral, per-stage model routing (Anthropic or OpenAI-compatible)
scripts/publish-to-supabase.ts  seed + atomic publish for one story (service-role key; decisions 42, 48)
tools/                    media_kit.py (drawing kit) + draw_attention.py (per-paper drawings)
```

## How the content works (short version)

- Backup: the files in git are the full seed for the database (decision 35); numeric ids are not external identifiers (URLs, files, analytics use slug/key); export must pass reconciliation before a release (decision 37).
- Database: Supabase (managed Postgres, decision 34), schema as SQL migrations in the repo, secrets never in git.
- Database plan (decisions 30 and 38, final): `id` is Postgres auto-increment and the only reference between tables, with no foreign key
  constraints; our readable key is `slug` (stories) or `key` (tags, moments). URLs use the slug: `/papers/<slug>`.
- Stories carry no issue, volume or date of ours (decision 31). Issues and volumes are collections of published stories
  and the only place our dates appear.
- `data/seed/site.json` and `data/seed/papers/<slug>.json` are the Git backup and publish inputs; the browser does not read them.
  Paper JSON = metadata + `summary` + `tags` + ordered `blocks`.
- Block types: `lead`, `story`, `comic`, `facts` (see `src/types.ts`). Adding one means: a type, a component in
  `src/blocks/`, and a registry entry.
- Media entry = `{type: svg|image|video, src, width, height, alt}`, with `src` relative to `mediaBaseUrl`.
- The publisher extracts **moments** (comic strips, chapters, facts) into Supabase rows for the front page, feed and search.
- Tags come from the shared vocabulary in `data/seed/tags.json` and its Supabase views, with 13 facets, parent tags and aliases.

Full details: `docs/data-model.md`, `docs/tagging.md`, `README.md`.

## Working agreements

- **Git:** commit to the long-lived **`v1`** branch and push. No per-topic feature branches, no PR per change
  (decision 40). Push often; the owner merges `v1` into `main` when they want to release. Never commit or push
  directly to `main`. Only create another branch if the owner explicitly asks.
- **Canvas before code (owner's rule):** show any visual or layout change on the design canvas first, with 1–2
  options, and build it into the app only after the owner picks one. Keep tiles calm: one illustration, real data in a
  line or two, no stacked gimmicks.
- **Don't break data compatibility silently.** Bump `schemaVersion` for breaking changes.
- **Accessibility:** real buttons and links, alt text on media, `prefers-reduced-motion` respected, animations
  pause off-screen.
- **Design language:** cream newsprint (`#f6f0df`), ink (`#27251e`), red accent (`#a13324`), Georgia serif
  headlines, Courier labels, halftone dots, muted cartoon colours, word-buddy characters. Front page = layout **D**
  (broadsheet above the fold, soft bento below). Desktop first, mobile next.
- **Navigation is the same on every page:** Front page · Explore (Topics, Storylines, Map) · Real world · Snacks · Editions ·
  Search (decision 32: editions are a quiet extra).
- **Every component ships responsive and accessible:** no horizontal overflow at 375px, labels ≥12px, 44px tap
  targets, keyboard rails, reduced motion respected.
- **Ask before** anything public or irreversible (publishing, pushing to main, contacting companies, buying domains).

## Current status

**Read [docs/STATE.md](docs/STATE.md) first** — a one-page snapshot of where we are, the real content,
what's next, and the model-routing default. The paragraphs below are kept for context; `STATE.md` is the
single source of truth for status.

The app reads story and editorial data from Supabase views (decision 51); there is no file-backed frontend mode.
`data/seed/*.json` is retained for publish/import and recovery only. Media is still local under `public/media/` and
must move to Supabase Storage before the owner's cloud-only V1 merge gate is complete. See `docs/production-plan.md`.

## Status detail (kept for background)

This status detail is intentionally omitted so it cannot drift from the live snapshot. Use `docs/STATE.md` for current
counts and `docs/production-plan.md` for the authoritative V1 merge gate and remaining work.

## Keeping this file true

When a decision changes, update `docs/decisions.md` (add a new entry; don't rewrite history) and the matching
section here. When you finish a roadmap item, tick it in `docs/roadmap.md`. A future agent should be able to resume from
these files alone, without the chat history.
