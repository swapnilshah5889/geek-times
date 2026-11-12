---
name: develop-frontend
description: Make changes to The Geeky Times React + TypeScript + Vite frontend while keeping it data-driven, accessible and on-brand. Use for any UI, routing or styling work.
---

> **Default model:** **large** (Opus 5.5 / Sonnet 5.5 / top-tier equivalent) — design + typed React changes. Drop to a smaller model once the hard part is drafted.

# Develop the frontend

## Rules

- **Content never goes in components.** Pages and blocks render typed data from `src/types.ts`. A new kind of content
  means:
  1. a new member of the `Block` union,
  2. a component in `src/blocks/`,
  3. a registry entry in `src/blocks/index.tsx`.

  TypeScript enforces the registry.
- **Media goes through `MediaView`** (`src/components/MediaView.tsx`): svg/image/video, resolved against
  `mediaBaseUrl`. Never import graphics into the bundle.
- **Captions go through `Rich`.** It only allows b/i/a/sub/sup/br. Never use `dangerouslySetInnerHTML` for content.
- **Motion:** wrap animated sections in `MotionGroup`, with a `MotionButton` to pause. Media pauses off-screen and
  respects reduced motion.
- **Front page and feed layout** come from `src/lib/front.ts`, derived from `search-index.json`. Don't hand-place
  tiles.
- **Styling:** `src/styles/edition.css` holds the design tokens (see `AGENTS.md`). The front page is layout D:
  broadsheet above, soft bento below (light borders, rounded corners, gentle shadows, no hard ink offsets).
- **Accessibility:** real `<a>`/`<button>`, visible focus, alt text from data, ≥44px tap targets on mobile.

## Workflow

1. Branch: `v1` (the long-lived dev branch, decision 40). No new branch unless the owner says so.
2. `npm run dev` (it also validates the data).
3. Change the code. Keep the existing naming and comment style.
4. `npm run build` and `npm run lint` must pass.
5. Check in a browser at 1280px and 375px: no horizontal scroll, no console errors, animations running, links
   working.
6. Commit on `v1` and push. Update `docs/STATE.md` / `AGENTS.md` / `docs/roadmap.md` if you changed direction or finished an item.
