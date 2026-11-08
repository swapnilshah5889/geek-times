"""Draws the two lead plates for "The Anatomy of a Large-Scale Hypertextual Web Search Engine" (Google Search).

Run from the repo root:  python3 tools/draw_google-search.py
Writes standalone SVG files to public/media/google-search/lead/.
Plate captions/alt text live in data/seed/papers/google-search.json.
"""
import math
import random
from pathlib import Path

from media_kit import COL, COMIC_DEFS, EIGHT, INK, RED, anim, buddy, standalone, t, write

OUT = Path(__file__).resolve().parent.parent / 'public' / 'media' / 'google-search' / 'lead'
CREAM = '#fbf3dc'
DEFS = COMIC_DEFS + (
    f'<marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
    f'<path d="M0 0L10 5L0 10Z" fill="{INK}"/></marker>')


def plate(bg, tag, body, caption):
    return (f'<rect width="600" height="340" fill="{bg}"/><rect width="600" height="340" fill="url(#dots)" opacity=".22"/>'
            + body
            + f'<rect x="10" y="288" width="580" height="44" fill="{CREAM}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
            + t(300, 317, caption, 'b')
            + t(22, 28, tag, 'micro', 'start', f'fill:{RED}')
            + f'<path d="M8 10Q300 5 592 9Q596 170 591 332Q300 336 9 331Q4 170 8 10Z" fill="none" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>')


def page(x, y, rot=0, s=1, fill='#fff8e3', lines=3):
    ls = ''.join(f'<path d="M-12 {-14 + i * 8}h{24 - (i % 2) * 8}" stroke="{INK}" stroke-width="1.8" stroke-linecap="round" opacity=".65"/>' for i in range(lines))
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})">'
            f'<path d="M-18 -24H8L18 -14V24H-18Z" fill="{fill}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
            f'<path d="M8 -24V-14H18" fill="none" stroke="{INK}" stroke-width="2"/>{ls}</g>')


# ---- pile ----
rnd = random.Random(7)
pile = ''
pts = []
for row in range(7):
    n = 14 - row * 2
    y = 262 - row * 24
    for k in range(n):
        x = 300 + (k - (n - 1) / 2) * 38 + rnd.uniform(-8, 8)
        pts.append((x, y + rnd.uniform(-6, 6), rnd.uniform(-35, 35), ['#fff8e3', '#f0e3c6', '#f7d79b', '#e6efe4', '#e5dcef'][rnd.randrange(5)]))
gold_i = 20
for i, (x, y, r, c) in enumerate(pts):
    if i == gold_i:
        pile += page(x, y, r, 1.0, '#f2c14e') + f'<use href="#mstar" transform="translate({x + 4:.0f} {y:.0f}) scale(1.4)"/>'
    else:
        pile += page(x, y, r, 1.05, c, rnd.choice([2, 3, 4]))
pile_body = (pile
             + f'<g{anim("m-twinkle")}><use href="#mstar" transform="translate({pts[gold_i][0] + 4:.0f} {pts[gold_i][1] - 38:.0f}) scale(1.6)"/></g>'
             + f'<path d="M{pts[gold_i][0] + 20:.0f} {pts[gold_i][1] - 44:.0f}Q470 70 440 60" fill="none" stroke="{RED}" stroke-width="2.5" stroke-linecap="round" marker-end="url(#ah)"/>'
             + t(486, 50, 'the good one?', 'w-s', style=f'fill:{RED}')
             + buddy(80, 150, 'me', COL['bat'], .9) + f'<g{anim("m-bob")}>' + t(120, 100, '?', 'sfx') + '</g>'
             + t(500, 258, 'MILLIONS', 'micro') + t(60, 250, 'UNSORTED', 'micro'))

# ---- votes ----
def star_row(cx, cy, n):
    return ''.join(f'<use href="#mstar" transform="translate({cx + (i - (n - 1) / 2) * 24:.0f} {cy}) scale(1.5)"/>' for i in range(n))


def node(x, y, r, fill):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{INK}" stroke-width="3"/>'
            + page(x, y + 1, 0, r / 34, '#fff8e3', 3))


def arrow(a, ra, b, rb, color=INK, w=3):
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    x1, y1 = a[0] + math.cos(ang) * (ra + 3), a[1] + math.sin(ang) * (ra + 3)
    x2, y2 = b[0] - math.cos(ang) * (rb + 6), b[1] - math.sin(ang) * (rb + 6)
    mx, my = (x1 + x2) / 2 - math.sin(ang) * 10, (y1 + y2) / 2 + math.cos(ang) * 10
    return f'<path d="M{x1:.0f} {y1:.0f}Q{mx:.0f} {my:.0f} {x2:.0f} {y2:.0f}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" marker-end="url(#ah)"/>'


C = (300, 150); RC = 58
MID = (480, 100); RM = 34
smalls = [(110, 70), (90, 170), (160, 235), (300, 255), (440, 235), (510, 190), (200, 40), (400, 40), (545, 85)]
RS = 20
edges = ''
for s in smalls[:6]:
    edges += arrow(s, RS, C, RC)
edges += arrow(smalls[6], RS, C, RC) + arrow(smalls[7], RS, C, RC)
edges += arrow(smalls[8], RS, MID, RM) + arrow(smalls[5], RS, MID, RM)
edges += arrow(MID, RM, C, RC, RED, 3.5) + arrow(smalls[7], RS, MID, RM)
votes_body = (edges + ''.join(node(x, y, RS, '#f0e3c6') for x, y in smalls)
              + node(*MID, RM, '#a2c2a7') + node(*C, RC, '#f7d79b')
              + f'<g{anim("m-twinkle")}>' + star_row(C[0], C[1] - RC - 16, 3) + '</g>'
              + star_row(MID[0], MID[1] - RM - 14, 1)
              + t(C[0], C[1] + RC + 20, 'MOST VOTES', 'micro', style=f'fill:{RED}')
              + f'<g{anim("m-wiggle")}>' + t(80, 262, 'VOTE!', 'sfx-s') + '</g>')

if __name__ == '__main__':
    write(OUT, 'pile.svg', standalone('0 0 600 340', plate('#b8cec0', 'PLATE 01 / PILE', pile_body, 'So many pages, so few good ones.'),
          'A huge pile of web pages with one tiny gold page buried inside. Below: So many pages, so few good ones.', defs=DEFS))
    write(OUT, 'votes.svg', standalone('0 0 600 340', plate('#efd5b7', 'PLATE 02 / VOTES', votes_body, 'Pages point at the pages they trust.'),
          'Small page circles with arrows pointing at one big circle in the middle. Below: Pages point at the pages they trust.', defs=DEFS))
    print(f'wrote 2 lead plates to {OUT}')
