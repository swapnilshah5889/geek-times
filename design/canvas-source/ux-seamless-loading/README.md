# Seamless loading: two options (Wave 1, design only)

Open each HTML file in a browser. Each shows the desktop page at 1280px and a 375px phone frame, looping every 12 seconds: loading (about 5 s), arrival (about 1.7 s), the paper (about 5 s), then a quiet reset. Buttons: **Replay** and **Motion** (follow system, force reduced, force full). The black chip in each frame labels the phase; it is an annotation, not design. The masthead and page frame never change.

## Option 1: Column rule unfurl (`option-1.html`)

**Editorially:** the page is a form being filled. Rules, column edges and card outlines are already printed. In the headline column the reader sees "Setting the type…" in italic over a double rule that slowly breathes. Nothing pretends to be content.
**Transition:** when data lands the cue fades and each column's type is set in from the top in coarse line-by-line steps, left to right (headline, side column, three cards). Height is reserved, so nothing moves.
**Reduced motion:** the rule stays still, the words stay, and the columns appear in the same order as instant swaps, with no movement.

## Option 2: Halftone proof (`option-2.html`)

**Editorially:** a proof before the run. The whole page is visible through a fine halftone screen (the headline is already legible), with a "Going to press" slug and a slow-pulsing red ink dot.
**Transition:** the dots open together across the page until the screen is gone. Pure CSS (a registered custom property drives the dot radius).
**Reduced motion:** the dot stays solid, the slug stays, and the screen is removed instantly when data lands.

## Tradeoffs

- **Hydration fit (decision 50).** With `hydrateRoot` the prerendered page is already on screen. Option 2 can sit over that real HTML until the live read confirms it. Option 1 needs a hidden type layer, so it suits routes with no snapshot (`?feed`, `?search`, schema mismatch) or a slow Supabase swap.
- Option 1 says "not ready" more explicitly. Option 2 is more continuous, but its ghost text is low-contrast and not meant to be read.
- Option 2 needs `mask-composite` and `@property` (current Chrome, Safari 16.4+, Firefox 128+). Older browsers snap, which is acceptable.
- The mockups size the masthead with container units (`cqi`) so fixed-width frames render correctly. The app uses `vw`; keep the app's own sizes.
- No new fonts or files. Inline SVG is about 1.1 KB per file.
