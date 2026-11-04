# The Geeky Times

Research papers explained in pictures, for anyone, kids included. Issue 001 covers
"Attention Is All You Need" (Vaswani et al., 2017).

Built with **React + TypeScript + Vite**. The UI only renders data. Words live in JSON (a database later),
drawings live in media files (a CDN or S3 later), and layout lives in React components.

## Run it

```bash
npm install
npm run dev
```

Other scripts:

- `npm run build`: typecheck, then build static files into `dist/`.
- `npm run preview`: serve the built `dist/` folder.
- `npm run lint`: run oxlint.
- `npm run draw`: redraw the comic SVGs with Python.

Needs Node 20.19+ or 22.12+.

## Layout

```
index.html                     Vite entry
src/
  main.tsx, App.tsx            load the edition, render masthead + blocks + footer
  types.ts                     the content model (the contract with the data / future API)
  data/load.ts                 fetches site.json and one paper; checks schemaVersion
  edition.ts                   React context with the loaded edition
  blocks/                      one component per block type: Lead, Story, Comic, Facts (+ registry in index.tsx)
  components/MediaView.tsx     one renderer per media type: svg, image, video
  components/Rich.tsx          safe caption markup → React elements (b, i, a, sub, sup, br only)
  components/motion.tsx        MotionGroup (a section's pause switch) and MotionButton
  lib/motion.ts                on-screen detection, reduced-motion hook, motion context
  styles/edition.css           the newspaper look
public/
  data/site.json               site settings, list of papers, mediaBaseUrl
  data/papers/<slug>.json      one paper: metadata + an ordered list of blocks
  media/<slug>/...             standalone animated SVGs (later: GIF, WebP, MP4 on a CDN)
tools/
  media_kit.py                 drawing kit: word buddies, bubbles, panel frame, standalone-SVG wrapper
  draw_attention.py            draws this paper's comic panels and fact icons into public/media
```

Open a paper with `?paper=<slug>`. Without it you get `defaultPaper` from `site.json`.

## The data

The types in `src/types.ts` are the reference. A paper is `{ schemaVersion, slug, pageTitle, issue, paper, blocks }`.
Each block has a `type`, and the page renders blocks in order. Unknown types are skipped, so newer data can't break
an older build.

| type    | what it shows | main fields |
|---------|---------------|-------------|
| `lead`  | headline + slideshow plate | `kicker`, `headline {text, accent}`, `deck`, `slideshow {intervalMs, slides[{label, caption, media}]}` |
| `story` | picture story (problem, idea, solution, evidence) | `title`, `kicker`, `nav`, `chapters[{part, title, provenance, caption, media}]` |
| `comic` | comic strips explaining how it works | `title`, `deck`, `howTo`, `strips[{title, kicker, provenance, grownUpWords, panels[{caption, media}]}]` |
| `facts` | evidence cards with sources | `kicker`, `facts[{figure, text, source {label, url}, media}]` |

`media` is `{ type: 'svg' | 'image' | 'video', src, width, height, alt, poster? }`:

- `src` is relative to `mediaBaseUrl`.
- `width` and `height` set the aspect ratio, so the layout doesn't jump while the file loads.
- `alt` is read by screen readers. Leave it empty for decorative icons.

`provenance` is `illustration` (numbers made up to explain) or `evidence` (real results, cite them).
It keeps the two visibly apart on the page.

To add a block type, add its interface to the `Block` union in `types.ts`, write a component in `src/blocks/`,
and register it in `src/blocks/index.tsx`. TypeScript makes sure every type has a component.

### Moving to a database and a CDN

- **Database:** serve the same JSON shapes from an API and point each paper's `dataUrl` (in `site.json`) at it.
- **CDN / S3:** upload `public/media/` as-is and set `mediaBaseUrl` in `site.json`. You can also set
  `VITE_MEDIA_BASE_URL` per environment, for example in `.env.production`.
- **CORS for SVGs:** animated SVGs are fetched and inlined (in a shadow root) so the pause buttons work, so the bucket
  must send CORS headers for the site's origin. Without them the page falls back to `<img>`, which still animates but
  can't be paused.

## Making a new paper

1. Read the paper. Write the story in plain words a school kid can follow.
2. Draw panels with the `tools/media_kit.py` helpers (copy `tools/draw_attention.py`), or add GIF/MP4 files.
   Each SVG must be self-contained: its own `<style>` and `<defs>`, no scripts.
3. Write `public/data/papers/<slug>.json` and add the paper to `public/data/site.json`.
4. Check every evidence number against the paper and link the exact section (arXiv HTML anchors like `#S3.SS1`).
