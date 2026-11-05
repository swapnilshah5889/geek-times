---
name: draw-illustrations
description: Create Geeky Times illustrations (lead plates, comic panels, fact icons) as self-contained animated SVG files in the house cartoon-newspaper style.
---

> **Default model:** **large** (Opus 5.5 / Sonnet 5.5 / top-tier equivalent) — style and composition decisions. Drop to a smaller model once the hard part is drafted.

# Draw illustrations

## Style

- **Palette:**
  - cream `#f6f0df` / `#fbf3dc`
  - ink `#27251e` / `#322e24`
  - red `#a13324`
  - teal `#377675`
  - muted cartoon fills: `#efae78`, `#f7d79b`, `#a2c2a7`, `#c3b2d8`, `#82acad`, `#f0e3c6`
- **Linework:** 2–3px ink strokes with round joins. A halftone dot pattern over panel backgrounds (opacity about .22).
- **Type inside art:** Georgia for words, bold Courier for small labels, and bold-italic red "sound effect" words with
  a cream outline (SNIP!, TA-DA!).
- **Characters:** the word-buddy (a rounded rectangle body, two dot eyes, a small smile, stick arms and legs) with the
  word on its belly. Speech bubbles have tails pointing at the speaker.
- **Motion:** short loops (2–8s) that teach something: a meter filling, paint pouring, a cover sliding away. Avoid
  decorative jitter.

## Technical rules

- One standalone SVG per graphic: its own `<style>` and `<defs>`, no scripts, no external references, and a
  `<title>` describing it.
- Include `@media (prefers-reduced-motion: reduce) { * { animation: none !important } }`.
- **The resting state must be meaningful:** when animation is off, show the finished picture (meters full, cover
  slid away).
- Never animate an element that also has a positioning `transform` attribute. Wrap it in a `<g>` and animate the
  wrapper.
- Comic panels are 320×220. Story panels are 440×215. Lead plates are 600×340. Fact icons are 160×100.
- Keep text at 15px or more inside a 320-wide panel, so it stays readable on phones.

## Tools

- `tools/media_kit.py`: helpers (`buddy`, `bubble`, `can`, `gear`, `panel`, `standalone`) and the shared CSS
  animations (`m-pop`, `m-meter`, `m-flow`, `m-ride`, …).
- Copy `tools/draw_attention.py` as `tools/draw_<slug>.py` for a new story. It writes into `public/media/<slug>/`.
- Run `python3 tools/draw_<slug>.py`, then reference each file from the story JSON as
  `{type: "svg", src, width, height, alt}`.
- Illustrator-made GIF/WebP/MP4/Lottie files also work as media types. Keep the same palette.
