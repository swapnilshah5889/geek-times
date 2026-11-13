"""Draws the media for the ACCORD story (CEP-15: Fast General Purpose Transactions, Apache Cassandra draft).

Run from the repo root:  python3 tools/draw_accord.py
Writes standalone SVGs to backups/media/accord/. Every media.src in data/seed/papers/accord.json must be written.
Reuses the Cassandra helpers (desk, ring, envelope, notebook, folder, building, meter, ...).
"""
import json
import math
from pathlib import Path

import draw_cassandra as C
from draw_cassandra import (CREAM, GOLD, GREEN, GREY, ORANGE, PAPER, PURPLE, SAND, TEAL, WOOD, building, desk,
                            envelope, face, folder, meter, notebook, ring, ring_pts, arrow, svg)
from media_kit import INK, RED, anim, buddy, t, write

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'backups' / 'media' / 'accord'
SEED = ROOT / 'data' / 'seed' / 'papers' / 'accord.json'
BLUE = '#a9c4d4'
CLAIM = 'From the paper · design claim'
PANELS = {}   # src -> (viewBox, title, body)


def bg(w, h, col, body):
    return f'<rect width="{w}" height="{h}" fill="{col}"/><rect width="{w}" height="{h}" fill="url(#dots)" opacity=".22"/>{body}'


def add(src, w, h, col, body, title):
    PANELS[src] = (f'0 0 {w} {h}', title, bg(w, h, col, body))


def up(x, y, s=1):
    """A raised hand above a desk centred at (x, y)."""
    return (f'<g transform="translate({x} {y - 17 * s}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linecap="round">'
            f'<path d="M0 0V-14"/><circle cy="-18" r="5" fill="#f0c9a0" stroke-width="2"/></g>')


def card(x, y, txt='', fill=SAND, w=34, h=24, rot=0):
    g = (f'<g transform="translate({x} {y}) rotate({rot})"><rect x="{-w / 2}" y="{-h / 2}" width="{w}" height="{h}" rx="3" fill="{fill}" '
         f'stroke="{INK}" stroke-width="2"/>')
    if txt:
        g += t(0, 5, txt, 'w-s', style='stroke:none')
    return g + '</g>'


def clock(x, y, r=14, hh=-60, mm=30, face_c=PAPER):
    def hand(a, l, w):
        a = math.radians(a - 90)
        return f'<path d="M{x} {y}L{x + l * math.cos(a):.1f} {y + l * math.sin(a):.1f}" stroke="{INK}" stroke-width="{w}" stroke-linecap="round"/>'
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{face_c}" stroke="{INK}" stroke-width="3"/>' + hand(hh, r * .5, 2.5) + hand(mm, r * .75, 2)
            + f'<circle cx="{x}" cy="{y}" r="2" fill="{INK}"/>')


def tick(x, y, r=13):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{GREEN}" stroke="{INK}" stroke-width="2.5"/><path d="M{x - 6} {y}l4 5 8 -10" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'


def cross(x, y, r=11):
    return f'<path d="M{x - r} {y - r}L{x + r} {y + r}M{x + r} {y - r}L{x - r} {y + r}" stroke="{RED}" stroke-width="5" stroke-linecap="round"/>'


def hat(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"><path d="M-14 0L-12 -14L-5 -7L0 -17L5 -7L12 -14L14 0Z" fill="{GOLD}"/></g>')


def stamp(w, h, txt=CLAIM):
    return t(w / 2, h - 8, txt, 'micro', style=f'fill:{RED}')


def label(x, y, s, cls='b-s'):
    return t(x, y, s, cls)


def plate(src, title, col, tag, body, cap):
    body = (bg(600, 340, col, body)
            + f'<rect x="10" y="288" width="580" height="44" fill="{CREAM}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
            + t(300, 317, cap, 'b') + t(22, 28, tag, 'micro', 'start', f'fill:{RED}')
            + f'<path d="M8 10Q300 5 592 9Q596 170 591 332Q300 336 9 331Q4 170 8 10Z" fill="none" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>')
    PANELS[src] = ('0 0 600 340', title, body)


# ============================ lead plates ============================
CX, CY, RX, RY = 300, 150, 215, 92
pts = ring_pts(CX, CY, RX, RY, 6, -90)
b = ring(CX, CY, RX, RY, 3)
for i, (x, y) in enumerate(pts):
    b += desk(x, y, 1.15, top=WOOD)
b += hat(pts[0][0], pts[0][1] - 24, 1.2)
# queue at the captain desk (inside the ring, lining up under it)
for i in range(5):
    b += face(CX - 6 + (i % 2) * 8, 80 + i * 24, ['#5a3a28', '#a13324', '#27251e', '#8a5a9a', '#b08a2c'][i], r=10)
b += f'<path d="M{CX + 24} 84v100" stroke="{RED}" stroke-width="3" stroke-dasharray="3 7" stroke-linecap="round"/>'
fx, fy = pts[3]
b += face(fx + 30, fy - 34, '#4f7a66', r=12) + f'<g{anim("m-wiggle")}><path d="M{fx + 40} {fy - 26}l12 -10" stroke="{INK}" stroke-width="3" stroke-linecap="round"/></g>'
b += t(fx + 74, fy - 44, 'wait…', 'b-s') + t(CX + 62, 100, 'long line', 'b-s', 'start')
plate('accord/lead/many-captains.svg', 'Six desks on a ring: one captain desk with a long line, a far-away person waving.', '#f0e3c6',
      'GEEKY TIMES · LEAD PLATE', b, 'One captain orders everything')

b = ring(CX, CY, RX, RY, 3)
for i, (x, y) in enumerate(pts):
    b += desk(x, y, 1.15, top=GREEN if i in (1, 3, 5) else WOOD)
b += clock(CX, CY, 34, -30, 60) + f'<g{anim("m-spin-slow")}></g>'
for i, (px, py) in enumerate([(CX - 60, CY - 24), (CX + 60, CY - 24), (CX + 95, CY + 46)]):
    tx, ty = pts[[0, 2, 4][i]] if False else [pts[5], pts[1], pts[2]][i]
    b += face(px, py, ['#5a3a28', '#a13324', '#27251e'][i], r=11)
    dx, dy = tx - px, ty - py
    n = math.hypot(dx, dy)
    b += arrow(f'M{px + dx / n * 18:.0f} {py + dy / n * 18:.0f}L{tx - dx / n * 34:.0f} {ty - dy / n * 34:.0f}')
plate('accord/lead/no-captain.svg', 'Six desks on a ring, no hats; three people walk to their nearest desk; a clock in the middle.', '#e8e2cc',
      'GEEKY TIMES · LEAD PLATE', b, 'No captain: a clock decides the order')

# ============================ story panels ============================
b = ''
for i, x in enumerate((80, 220, 360)):
    b += desk(x, 130, 1.5) + folder(x, 88, 50, 36, SAND) + f'<path d="M{x - 14} 90h26M{x - 14} 98h18" stroke="{INK}" stroke-width="1.8" opacity=".5"/>'
b += t(150, 50, '?', 'sfx', style='font-size:44px') + t(290, 50, '?', 'sfx', style='font-size:44px')
b += label(220, 200, 'Every copy must agree on the order of changes', 'b-s')
add('accord/story/01-agree.svg', 440, 215, '#f0e3c6', b, 'Three folders on three desks hold the same page, and a question mark floats between them.')

b = (f'<path d="M20 70H260" stroke="{INK}" stroke-width="30" stroke-linecap="round" opacity=".18"/><path d="M20 70H190" stroke="{GREY}" stroke-width="22" stroke-linecap="round"/>'
     f'<path d="M20 70H190" stroke="#f6f0df" stroke-width="2" stroke-dasharray="10 9"/>'
     f'<rect x="196" y="48" width="8" height="44" rx="2" fill="{RED}" stroke="{INK}" stroke-width="2.5"/>'
     f'<path d="M190 70Q230 70 230 110Q230 145 190 150Q130 155 110 175Q200 200 400 180" fill="none" stroke="{GREY}" stroke-width="22" stroke-linecap="round"/>'
     f'<path d="M190 70Q230 70 230 110Q230 145 190 150Q130 155 110 175Q200 200 400 180" fill="none" stroke="#f6f0df" stroke-width="2" stroke-dasharray="10 9"/>')
b += '<g stroke="%s" stroke-width="2" stroke-linejoin="round">' % INK
for x, y, c in ((60, 63, ORANGE), (110, 63, BLUE), (150, 63, GREEN)):
    b += f'<rect x="{x - 14}" y="{y - 8}" width="28" height="15" rx="5" fill="{c}"/>'
b += '</g>' + f'<g{anim("m-ride")}></g>'
b += label(208, 30, 'gate shut', 'micro').replace('<text', '<text style="fill:#a13324"', 1) + label(345, 150, 'long way round', 'b-s') + label(110, 114, 'fast road', 'b-s')
b += f'<g stroke="{INK}" stroke-width="2" stroke-linejoin="round"><rect x="250" y="168" width="26" height="14" rx="5" fill="{ORANGE}"/><rect x="330" y="176" width="26" height="14" rx="5" fill="{BLUE}"/></g>'
add('accord/story/02-wobble.svg', 440, 215, '#f6f0df', b, 'A fast road with a closed gate beside a long winding road, with cars turning onto the winding one.')

b = ''
for i, x in enumerate((36, 76, 116, 156)):
    b += desk(x, 120, .85) + up(x, 120, .85)
b += f'<ellipse cx="96" cy="115" rx="86" ry="46" fill="none" stroke="{TEAL}" stroke-width="3" stroke-dasharray="8 6"/>'
b += label(96, 62, 'SHRINK THE VOTERS', 'micro') + label(96, 186, 'fewer desks must agree', 'b-s')
b += f'<path d="M216 40V190" stroke="{INK}" stroke-width="2.5" stroke-dasharray="4 6"/>'
for i, c in enumerate((SAND, GREEN, PURPLE, SAND)):
    b += envelope(262 + i * 44 - (i % 2) * 6, 135 - (i % 2) * 6, -8 + i * 6, 1.15, c)
b += clock(350, 90, 22, -50, 20)
b += f'<path d="M244 156H410" stroke="{RED}" stroke-width="3" stroke-linecap="round"/>'
b += label(330, 62, 'HOLD UNTIL THE TIME', 'micro') + label(330, 186, 'a clock sets the order', 'b-s')
b = b.replace('<text x="96" y="62"', '<text style="fill:#a13324" x="96" y="62"').replace('<text x="330" y="62"', '<text style="fill:#a13324" x="330" y="62"')
add('accord/story/03-two-tricks.svg', 440, 215, '#f0e3c6', b, 'A small group of desks raising hands on the left, and a waiting line of envelopes ordered by a clock on the right.')

b = (f'<g stroke="{INK}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"><rect x="40" y="62" width="150" height="100" rx="6" fill="{PAPER}"/>'
     f'<path d="M58 88h110M58 108h96M58 128h110M58 148h60" stroke-width="2" opacity=".5" fill="none"/>'
     f'<circle cx="46" cy="76" r="14" fill="{SAND}"/><circle cx="184" cy="150" r="14" fill="{SAND}"/></g>')
b += label(115, 190, 'reasons and proofs', 'b-s')
b += (f'<circle cx="320" cy="108" r="46" fill="{PAPER}" stroke="{INK}" stroke-width="4"/><rect x="308" y="50" width="24" height="10" rx="2" fill="{GREY}" stroke="{INK}" stroke-width="3"/>'
      f'<circle cx="320" cy="108" r="4" fill="{INK}"/>' + ''.join(f'<path d="M{320 + 38 * math.cos(math.radians(a)):.0f} {108 + 38 * math.sin(math.radians(a)):.0f}l{6 * math.cos(math.radians(a)):.0f} {6 * math.sin(math.radians(a)):.0f}" stroke="{INK}" stroke-width="2"/>' for a in range(0, 360, 30))
      + f'<path d="M296 84L344 132M344 84L296 132" stroke="{RED}" stroke-width="5" stroke-linecap="round" opacity=".0"/>')
b += label(320, 190, 'no benchmark in the paper', 'b-s')
add('accord/story/04-no-benchmark.svg', 440, 215, '#e8e2cc', b, 'A scroll of written reasoning on a desk, and next to it an empty stopwatch with no needle.')

# ============================ comic panels ============================
W, H = 320, 220
b = (face(48, 100, '#5a3a28', r=14) + envelope(84, 104, -10, 1.2) + buddy(160, 100, 'helper', SAND, 1, label_cls='w-s')
     + ''.join(desk(268, y, .9) for y in (50, 110, 170)) + arrow('M200 92L238 58') + arrow('M204 104L238 108') + arrow('M200 118L238 164')
     + label(160, 205, 'Ask the desks to order this job', 'b-s'))
add('accord/comic/01a-ask.svg', W, H, '#f0e3c6', b, 'A person hands an envelope to a helper, who points at three desks.')

b = ''.join(desk(x, 120, 1.1) + card(x, 78, '', SAND) + clock(x, 78, 8, -30, 60) for x in (70, 160, 250))
b += tick(160, 36, 15) + label(160, 176, 'same answer', 'w-s') + label(160, 196, 'one trip', 'w-s') + stamp(W, H)
add('accord/comic/01b-same-answer.svg', W, H, '#e8e2cc', b, 'Three desks hold up the same card with a clock time, and a green tick appears.')

b = ''.join(desk(x, 60, .85) + card(x, 22, '', c) for x, c in ((70, SAND), (160, GREEN), (250, PURPLE)))
b += label(160, 100, 'round one: they differ', 'b-s') + arrow('M160 108V122', False)
b += ''.join(desk(x, 160, .85) + card(x, 122, '', GOLD) + clock(x, 122, 7, -30, 60) for x in (70, 160, 250))
b += label(160, 192, 'round two: one shared card', 'b-s') + stamp(W, H, 'At most two trips · design claim')
add('accord/comic/01c-extra-round.svg', W, H, '#f0e3c6', b, 'Desks hold up different cards, then a second round of one shared card is held up.')

b = ''.join(desk(26 + i * 33, 100, .62) + up(26 + i * 33, 100, .62) for i in range(9))
b += label(160, 150, 'nine desks, nine raised hands', 'w-s') + label(160, 176, "the paper's example", 'b-s') + stamp(W, H)
add('accord/comic/02a-nine.svg', W, H, '#e8e2cc', b, 'Nine small desks in a row, all with raised hands.')

b = ''
for i in range(9):
    x = 26 + i * 33
    b += desk(x, 100, .62, dark=i >= 7) + (up(x, 100, .62) if i < 7 else cross(x, 96, 10))
b += label(160, 150, 'two desks break: the vote group shrinks', 'b-s') + card(160, 182, 'fewer', GOLD, 70, 28) + stamp(W, 220, 'Paper example: nine to seven')
add('accord/comic/02b-shrink.svg', W, H, '#f0e3c6', b, 'Two desks crossed out, a smaller row of raised hands, and a smaller number card.')

b = (f'<ellipse cx="160" cy="100" rx="140" ry="76" fill="{PAPER}" fill-opacity=".6" stroke="{INK}" stroke-width="3" stroke-dasharray="10 6"/>'
     f'<ellipse cx="160" cy="100" rx="108" ry="52" fill="{SAND}" fill-opacity=".5" stroke="{TEAL}" stroke-width="3.5"/>')
b += ''.join(desk(70 + i * 45, 104, .8) for i in range(5)) + label(160, 54, 'fast-path circle', 'micro') + label(160, 188, 'normal circle: the same desks inside', 'b-s')
b = b.replace('<text x="160" y="54"', '<text style="fill:#377675" x="160" y="54"')
add('accord/comic/02c-same-group.svg', W, H, '#e8e2cc', b, 'The same five desks sit inside both a fast-path circle and a normal circle.')

b = ''.join(building(x, 62, .6, False) for x in (36, 284)) + envelope(36, 108, 0, 1.2, '#d98b8b') + envelope(284, 108, 0, 1.2, BLUE)
b += label(36, 140, 'city A', 'micro') + label(284, 140, 'city B', 'micro')
for x, c in ((96, '#d98b8b'), (140, '#d98b8b'), (180, BLUE), (224, BLUE)):
    b += desk(x, 170, .75) + envelope(x, 150, 0, .8, c)
b += label(160, 70, 'each city is near its own desks', 'b-s') + label(160, 210, 'the two ends see different first jobs', 'b-s')
add('accord/comic/03a-two-cities.svg', W, H, '#f0e3c6', b, 'Two cities at the edges with an envelope each, and desks near each city holding a different envelope first.')

b = ''.join(envelope(60 + i * 34, 110, 0, 1.2, c) for i, c in enumerate((SAND, GREEN, PURPLE)))
b += envelope(180, 110, 0, 1.4, GOLD) + f'<path d="M168 96h24" stroke="{RED}" stroke-width="3" opacity="0"/>'
b += (f'<g stroke="{INK}" stroke-width="3" stroke-linecap="round"><path d="M215 140V90M255 140V90"/><path d="M215 94Q235 112 255 94" fill="none" stroke="{RED}" stroke-width="4"/></g>'
      + clock(235, 64, 15, -40, 40, '#fff8e3') + envelope(290, 112, 8, 1.2, ORANGE) + label(290, 150, 'later', 'b-s') + label(120, 150, 'in line', 'b-s')
      + label(160, 190, 'held behind a rope until its time', 'b-s'))
add('accord/comic/03b-waiting-line.svg', W, H, '#e8e2cc', b, 'An envelope sits in a line of envelopes behind a rope and a small alarm clock.')

b = ''
for x in (60, 160, 260):
    b += desk(x, 150, 1) + envelope(x, 100, 0, 1.2, SAND) + t(x - 2, 105, '1', 'w-s', style='stroke:none') + envelope(x, 126, 0, 1.2, GREEN) + t(x - 2, 131, '2', 'w-s', style='stroke:none')
b += label(160, 40, 'same stack at every desk', 'w-s') + label(160, 205, 'job one on top of job two', 'b-s')
add('accord/comic/03c-same-order.svg', W, H, '#f0e3c6', b, 'Three desks each hold the same stack with job one on top of job two.')

b = (clock(90, 100, 40, -60, 20) + clock(230, 100, 40, -55, 20)
     + f'<path d="M137 62h46M137 56v12M183 56v12" stroke="{RED}" stroke-width="3" stroke-linecap="round" fill="none"/>'
     + label(160, 50, 'tiny gap', 'b-s') + label(160, 176, 'jobs wait as long as the gap between clocks', 'b-s'))
add('accord/comic/04a-delay.svg', W, H, '#e8e2cc', b, 'Two clocks showing slightly different times with a tiny gap marked between them.')

b = (f'<path d="M24 60h12M24 54v12M36 54v12" stroke="{RED}" stroke-width="3" stroke-linecap="round"/>' + label(60, 84, 'tiny clock gap', 'b-s')
     + f'<rect x="12" y="110" width="296" height="40" fill="{BLUE}" stroke="{INK}" stroke-width="3"/>'
     + ''.join(f'<path d="M{30 + i * 46} 124q12 -10 24 0t24 0" fill="none" stroke="#f6f0df" stroke-width="3"/>' for i in range(6))
     + f'<path d="M12 106H308" stroke="{INK}" stroke-width="5" stroke-dasharray="14 8"/>' + arrow('M60 98H280', False) + label(160, 176, 'a long trip across the ocean', 'b-s')
     + label(160, 200, 'the gap is small beside it', 'b-s') + stamp(W, 220, 'Argued by the paper · not a test').replace('y="212"', 'y="216"'))
add('accord/comic/04b-tiny-gap.svg', W, H, '#f0e3c6', b, 'A tiny gap beside a long road crossing the ocean.')

b = ''
for x in (52, 160, 268):
    b += building(x, 120, .95, True) + f'<path d="M{x - 8} 80q8 -14 16 0Z" fill="{GREY}" stroke="{INK}" stroke-width="2.5"/>' + clock(x, 70, 8, -30, 60)
    b += f'<g transform="translate({x} 176)" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"><path d="M-12 12L-8 -6H8L12 12Z" fill="{GREY}"/><circle cy="-10" r="5" fill="none"/></g>'
b += label(160, 22, 'each place has its own clock', 'b-s') + label(160, 210, 'same small weight everywhere', 'b-s')
add('accord/comic/04c-fixed-cost.svg', W, H, '#e8e2cc', b, 'Several buildings each with a small clock dish on the roof and the same small weight.')

b = (f'<g stroke="{INK}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none"><path d="M60 110v40M60 150h36M72 150V190M96 150V190M60 110h-8"/><rect x="48" y="80" width="14" height="30" rx="3" fill="{WOOD}"/></g>'
     + desk(200, 150, 1.3) + envelope(200, 112, -12, 1.5, SAND) + f'<path d="M188 112l12 -8l12 6" stroke="{RED}" stroke-width="2.5" fill="none"/>'
     + label(60, 205, 'empty chair', 'b-s') + label(200, 205, 'job left half-done', 'b-s') + t(120, 70, '?', 'sfx', style='font-size:46px'))
add('accord/comic/05a-helper-gone.svg', W, H, '#f0e3c6', b, 'An empty chair with a half-finished envelope left on the desk.')

b = meter(90, 100, 52, 50) + label(90, 124, 'worry meter', 'micro') + desk(190, 130, 1.3) + face(190, 74, '#5a3a28', r=13) + envelope(235, 120, -8, 1.3, SAND)
b += label(160, 200, 'a desk that saw the job steps up', 'b-s') + t(250, 60, 'I’ll do it', 'b-s', style='font-style:italic')
add('accord/comic/05b-takeover.svg', W, H, '#e8e2cc', b, 'A desk with a worry meter pointing high steps up and picks up the envelope.')

b = (desk(160, 140, 1.4) + envelope(160, 96, 0, 1.5, SAND) + notebook(52, 90, .6, 3) + notebook(268, 90, .6, 3)
     + arrow('M86 90Q120 80 138 94') + arrow('M234 90Q200 80 182 94')
     + f'<g{anim("m-pulse")}>' + t(160, 60, 'DONE!', 'sfx') + '</g>' + label(160, 200, 'checks two neighbours’ notes, then stamps it', 'b-s'))
add('accord/comic/05c-finish.svg', W, H, '#f0e3c6', b, 'The desk checks notes from two neighbours and stamps the envelope done.')

row = ''.join(desk(150 + i * 50, 140, .9) for i in range(4))
b = (row + f'<g{anim("m-bob")}>' + desk(50, 140, .9, top=GREEN) + f'<g transform="translate(26 120)" stroke="{INK}" stroke-width="3" stroke-linecap="round" fill="none"><path d="M0 0v-18h16M0 0h16"/></g></g>'
     + arrow('M80 118H122', True) + label(160, 190, 'a new desk carries its chair over', 'b-s') + label(50, 80, 'new', 'micro'))
add('accord/comic/06a-new-desk.svg', W, H, '#e8e2cc', b, 'A new desk carries its chair toward a row of desks.')

b = ''.join(desk(60 + i * 50, 70, .8) for i in range(3)) + desk(160, 170, 1.1, top=GREEN)
b += notebook(160, 118, .55, 3) + arrow('M100 94Q130 108 148 110') + arrow('M220 94Q190 108 172 110')
b += label(160, 205, 'old desks hand over the notebook', 'b-s').replace('y="205"', 'y="208"') + label(250, 170, 'new', 'micro')
add('accord/comic/06b-catch-up.svg', W, H, '#f0e3c6', b, 'Old desks hand a notebook to the new desk.')

b = ''.join(desk(40 + i * 50, 120, .85) + up(40 + i * 50, 120, .85) for i in range(4))
b += desk(262, 120, .85, top=GREEN) + up(262, 120, .85) + tick(262, 50) + label(160, 170, 'the new desk votes too', 'w-s') + label(262, 154, 'new', 'micro')
add('accord/comic/06c-vote.svg', W, H, '#e8e2cc', b, 'The new desk raises a hand beside the others with a green tick.')

# ============================ fact icons ============================
def fic(name, body, title, col='#f0e3c6'):
    add(f'accord/facts/{name}.svg', 160, 100, col, body, title)


def fstamp(txt='paper · claimed'):
    return t(80, 94, txt, 'micro', style=f'fill:{RED}')


fic('trips', desk(30, 46, .8) + desk(130, 46, .8) + arrow('M52 36Q80 18 108 36', False) + arrow('M108 56Q80 70 52 56', False)
    + t(80, 50, '1', 'mono', style=f'fill:{RED}') + t(80, 80, 'trip', 'w-s') + fstamp(), 'One round trip between desks.')
fic('one-failure', ''.join(desk(18 + i * 31, 40, .55) for i in range(5)) + cross(18 + 2 * 31, 36, 9)
    + t(80, 72, 'one lost: fast path stops', 'micro') + fstamp(), 'A row of five desks, one crossed out.')
fic('shrink-nine', ''.join(desk(14 + i * 16, 36, .32) for i in range(9)) + t(80, 66, '9 → 7 or 5', 'mono-s') + fstamp(), 'Nine desks shrink to seven.')
fic('clock-gap', clock(40, 40, 20, -60, 20) + clock(120, 40, 20, -55, 20) + f'<path d="M64 24h32M64 18v12M96 18v12" stroke="{RED}" stroke-width="2.5" stroke-linecap="round"/>'
    + t(80, 72, '&lt; 1 ms', 'mono-s') + fstamp(), 'Two clocks with a very small gap.')
fic('phases', ''.join(f'<circle cx="{20 + i * 30}" cy="38" r="11" fill="{[SAND, GREEN, PURPLE, ORANGE, BLUE][i]}" stroke="{INK}" stroke-width="2.5"/>' + t(20 + i * 30, 43, str(i + 1), 'w-s', style='stroke:none') for i in range(5))
    + f'<path d="M50 30Q80 8 110 30" fill="none" stroke="{RED}" stroke-width="2.5" stroke-dasharray="5 5"/>' + t(80, 72, '5 phases', 'w-s') + fstamp(), 'Five steps in a row, one can be skipped.')
fic('no-benchmark', f'<circle cx="80" cy="46" r="30" fill="{PAPER}" stroke="{INK}" stroke-width="3.5"/><rect x="72" y="8" width="16" height="8" rx="2" fill="{GREY}" stroke="{INK}" stroke-width="2.5"/>'
    f'<circle cx="80" cy="46" r="3.5" fill="{INK}"/>' + t(80, 94, '0 tests · no needle', 'micro', style=f'fill:{RED}'), 'An empty stopwatch with no needle.')


def srcs(doc):
    out = {}

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get('src'), str) and o['src'].startswith('accord/'):
                out[o['src']] = (o.get('width'), o.get('height'))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(doc)
    return out


if __name__ == '__main__':
    want = srcs(json.loads(SEED.read_text()))
    missing = set(want) - set(PANELS)
    assert not missing, f'not drawn: {sorted(missing)}'
    total = 0
    for src, (w, h) in want.items():
        vb, title, body = PANELS[src]
        assert vb == f'0 0 {w} {h}', f'wrong viewBox for {src}'
        p = write(OUT, src.replace('accord/', '', 1), svg(vb, body, title))
        total += p.stat().st_size
    print(f'wrote {len(want)} files, {total} bytes to {OUT}')
