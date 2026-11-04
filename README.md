# Geek Times

Research papers explained in pictures, for anyone, kids included. The first edition, *The Paper Lantern*, covers
"Attention Is All You Need" (Vaswani et al., 2017).

## How it fits together

The page is a renderer. Words live in **data**, drawings live in **media files**, and the layout lives in **code**.

```
site/
  index.html                 empty shell: loads the CSS and js/app.js
  data/site.json             site settings + list of papers + mediaBaseUrl
  data/papers/<slug>.json    one paper: metadata and an ordered list of blocks
  media/<slug>/...           standalone animated SVGs (later: GIF, WebP, MP4 on a CDN)
  js/app.js                  loads the data and builds the page
  js/blocks.js               one renderer per block type (lead, story, comic, facts)
  js/media.js                one renderer per media type (svg, image, video)
  js/motion.js               plays animations only on screen; pause buttons; reduced motion
  js/rich.js                 safe inline markup for captions (b, i, a, sub, sup, br)
  css/edition.css            the newspaper look
tools/
  media_kit.py               shared drawing kit (word buddies, bubbles, panel frame, SVG wrapper)
  draw_attention.py          draws this paper's comic panels and fact icons
```

Open a paper with `?paper=<slug>`. Without it you get `defaultPaper` from `site.json`.

## The data

A paper file is `{ schemaVersion, slug, pageTitle, issue, paper, blocks: [...] }`. Each block has a `type`.
The page renders blocks in order and skips types it doesn't know.

| type    | what it shows | main fields |
|---------|---------------|-------------|
| `lead`  | headline and a slideshow plate | `kicker`, `headline {text, accent}`, `deck`, `slideshow {intervalMs, slides[{label, caption, media}]}` |
| `story` | picture story (problem, idea, solution, evidence) | `title`, `kicker`, `nav`, `chapters[{part, title, provenance, caption, media}]` |
| `comic` | comic strips explaining how it works | `title`, `deck`, `howTo`, `strips[{title, kicker, provenance, grownUpWords, panels[{caption, media}]}]` |
| `facts` | evidence cards with sources | `kicker`, `facts[{figure, text, source {label, url}, media}]` |

`media` is always `{ type, src, width, height, alt, poster? }`:

- `type` is one of `svg`, `image` (gif, webp, png, jpg) or `video` (mp4/webm, plays muted and looped like a GIF).
- `src` is relative to `mediaBaseUrl`.
- `width` and `height` set the aspect ratio, so the layout doesn't jump while the file loads.
- `alt` is read by screen readers. Leave it empty for decorative icons.

`provenance` is `illustration` (numbers made up to explain) or `evidence` (real results, cite them).
It keeps the two visibly apart on the page.

Captions may use `<b> <i> <a href> <sub> <sup> <br>`. Everything else is stripped.

### Moving to a database and a CDN

- **Database:** the JSON shape is the API contract. Serve the same documents from an endpoint and point
  `dataUrl` (in `site.json`) at it.
- **CDN / S3:** upload `site/media/` as-is and set `mediaBaseUrl` to the bucket or CDN URL,
  e.g. `https://cdn.example.com/geek-times/`.
- **CORS for SVGs:** animated SVGs are fetched and inlined so the page can pause them, so the bucket must send
  CORS headers for the site's origin. Without them the page falls back to a plain `<img>`, which still animates
  but ignores the pause buttons.

## Making a new paper

1. Read the paper. Write the story in plain words a school kid can follow.
2. Draw panels with `tools/media_kit.py` helpers (copy `tools/draw_attention.py`), or add GIF/MP4 files.
   Each SVG must be self-contained: its own `<style>` and `<defs>`, no scripts.
3. Write `site/data/papers/<slug>.json` and add the paper to `site/data/site.json`.
4. Check every evidence number against the paper and link the exact section (arXiv HTML anchors like `#S3.SS1`).

## Run locally

```bash
python3 -m http.server 8417 --directory site
```

Then open http://localhost:8417. The page loads its data with `fetch`, so opening `index.html` as a file won't work.
To redraw the comic media:

```bash
python3 tools/draw_attention.py
```
