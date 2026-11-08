"""Draws the two lead plates for "Deep Residual Learning" (ResNet).

Run from the repo root:  python3 tools/draw_resnet.py
Writes standalone SVG files to public/media/resnet/lead/.
Plate captions/alt text live in data/seed/papers/resnet.json.
"""
from pathlib import Path

from media_kit import COL, COMIC_DEFS, INK, RED, anim, buddy, standalone, t, write

OUT = Path(__file__).resolve().parent.parent / 'public' / 'media' / 'resnet' / 'lead'
CREAM = '#fbf3dc'
BLUR = ''.join(f'<filter id="bl{i}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="{s}"/></filter>'
               for i, s in enumerate([0, 1.4, 2.8, 4.6]))
DEFS = COMIC_DEFS + BLUR + (
    f'<marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
    f'<path d="M0 0L10 5L0 10Z" fill="{INK}"/></marker>'
    f'<marker id="ahr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
    f'<path d="M0 0L10 5L0 10Z" fill="{RED}"/></marker>')


def plate(bg, tag, body, caption):
    return (f'<rect width="600" height="340" fill="{bg}"/><rect width="600" height="340" fill="url(#dots)" opacity=".22"/>'
            + body
            + f'<rect x="10" y="288" width="580" height="44" fill="{CREAM}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
            + t(300, 317, caption, 'b')
            + t(22, 28, tag, 'micro', 'start', f'fill:{RED}')
            + f'<path d="M8 10Q300 5 592 9Q596 170 591 332Q300 336 9 331Q4 170 8 10Z" fill="none" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>')


def cat(blur=0, fixes=0):
    """A cat sketch on a card, centred on (0,0); card is 104x78."""
    g = (f'<rect x="-52" y="-39" width="104" height="78" rx="4" fill="#fff8e3" stroke="{INK}" stroke-width="2.5"/>'
         f'<g filter="url(#bl{blur})">'
         f'<path d="M-24 -10L-26 -32L-9 -20ZM24 -10L26 -32L9 -20Z" fill="#efae78" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
         f'<ellipse cx="0" cy="2" rx="29" ry="24" fill="#efae78" stroke="{INK}" stroke-width="2.5"/>'
         f'<circle cx="-11" cy="-2" r="3.2" fill="{INK}"/><circle cx="11" cy="-2" r="3.2" fill="{INK}"/>'
         f'<path d="M-3 6h6l-3 4Z" fill="{RED}"/><path d="M0 10q-4 5-8 2M0 10q4 5 8 2" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>'
         f'<path d="M-30 3l-16-3M-30 9l-15 5M30 3l16-3M30 9l15 5" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>'
         '</g>')
    marks = [f'<path d="M-9 25l-6 6 6 3 3-5ZM9 25l6 6-6 3-3-5Z" fill="{RED}" stroke="{INK}" stroke-width="1.5" stroke-linejoin="round"/>',   # bow
             f'<circle cx="-18" cy="6" r="4" fill="{RED}" opacity=".6"/><circle cx="18" cy="6" r="4" fill="{RED}" opacity=".6"/>',            # blush
             f'<path d="M-26 -22l-3-8M26 -22l3-8" stroke="{RED}" stroke-width="2.5" stroke-linecap="round"/>',                                # ear tufts
             f'<use href="#mstar" transform="translate(36 -26) scale(1.3)"/>']
    return g + ''.join(marks[:fixes])


def row(xs, cards, bud_y=240):
    out = ''
    for i, x in enumerate(xs):
        out += f'<g transform="translate({x} 128)">{cards[i]}</g>'
        out += buddy(x, bud_y, 'helper', COL['writer'], .8, label_cls='w-s')
        out += f'<path d="M{x} 168V198" stroke="{INK}" stroke-width="2.5" stroke-dasharray="4 4"/>'
    return out


XS = [90, 230, 370, 510]

# ---- fix-it: the picture rides the shortcut, each helper adds one small fix ----
shortcut = (f'<path d="M62 78Q300 -10 538 78" fill="none" stroke="{RED}" stroke-width="4" stroke-linecap="round" marker-end="url(#ahr)" stroke-dasharray="3 0"/>'
            f'<rect x="240" y="26" width="120" height="24" rx="4" fill="{CREAM}" stroke="{RED}" stroke-width="2"/>'
            + t(300, 43, 'SHORTCUT', 'micro', style=f'fill:{RED}'))
arrows = ''.join(f'<path d="M{x + 56} 128H{x + 84}" stroke="{INK}" stroke-width="3" marker-end="url(#ah)"/>' for x in XS[:3])
fix_body = (shortcut + arrows + row(XS, [cat(0, i + 1) for i in range(4)])
            + f'<g{anim("m-twinkle")}>' + t(548, 208, 'SAME CAT!', 'sfx-s') + '</g>'
            + t(150, 276, '+ fix', 'micro', style=f'fill:{RED}') + t(290, 276, '+ fix', 'micro', style=f'fill:{RED}')
            + t(430, 276, '+ fix', 'micro', style=f'fill:{RED}') + t(570, 276, '+ fix', 'micro', style=f'fill:{RED}'))

# ---- redraw: every helper redraws from scratch, the cat degrades ----
redraw_arrows = ''.join(f'<path d="M{x + 56} 128H{x + 84}" stroke="{INK}" stroke-width="3" marker-end="url(#ah)"/>' for x in XS[:3])
redraw_body = (redraw_arrows + row(XS, [cat(i) for i in range(4)])
               + t(300, 62, 'EACH HELPER REDRAWS FROM SCRATCH', 'micro', style=f'fill:{RED}')
               + f'<g{anim("m-wobble")}>' + t(520, 218, 'BLUR!', 'sfx') + '</g>'
               + t(90, 272, 'clear', 'micro') + t(510, 272, 'a smudge', 'micro'))

if __name__ == '__main__':
    write(OUT, 'fix-it.svg', standalone('0 0 600 340', plate('#b8cec0', 'PLATE 01 / FIX-IT', fix_body, 'The picture rides along. Each helper adds one small fix.'),
          'The same line of helpers, but the cat picture rides along on a shortcut and each helper only adds a small fix. The cat stays clear.', defs=DEFS))
    write(OUT, 'redraw.svg', standalone('0 0 600 340', plate('#efd5b7', 'PLATE 02 / REDRAW', redraw_body, 'Redraw from scratch, again and again, and it blurs.'),
          'A long line of helpers, each redrawing a cat picture. The cat gets blurrier with every helper.', defs=DEFS))
    print(f'wrote 2 lead plates to {OUT}')
