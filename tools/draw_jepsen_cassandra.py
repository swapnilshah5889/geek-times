"""Draws the media for "Jepsen: Cassandra" (Kyle Kingsbury, 2013).

Run from the repo root:  python3 tools/draw_jepsen_cassandra.py
Writes standalone SVGs to backups/media/jepsen-cassandra/{lead,story,comic,facts}/. Every media.src in
data/seed/papers/jepsen-cassandra.json must be written, at the width and height the JSON gives.
"""
import json
import math
import re
from pathlib import Path

from media_kit import COMIC_CSS, COMIC_DEFS, INK, RED, bubble, buddy, standalone, t, write

ROOT = Path(__file__).resolve().parent.parent
SLUG = 'jepsen-cassandra'
OUT = ROOT / 'backups' / 'media' / SLUG
SEED = ROOT / 'data' / 'seed' / 'papers' / f'{SLUG}.json'

CREAM, TEAL, GREEN, GOLD, WOOD = '#fbf3dc', '#377675', '#a2c2a7', '#ffe597', '#d9b98a'
PAPER, PURPLE, SAND, ORANGE, GREY, BG = '#fff8e3', '#c3b2d8', '#f7d79b', '#efae78', '#b5ab92', '#f6f0df'
DEFS = COMIC_DEFS + (f'<marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
                     f'<path d="M0 0L10 5L0 10Z" fill="{RED}"/></marker>')
SRC_LBL = 'From the source · reported'
INV_LBL = 'Illustration · numbers invented'


def prune_css(css, body):
    blocks, depth, cur = [], 0, ''
    for ch in css:
        cur += ch
        depth += ch == '{'
        if ch == '}':
            depth -= 1
            if depth == 0:
                blocks.append(cur.strip()); cur = ''
    kept = []
    for b in blocks:
        if b.startswith('@keyframes'):
            continue
        classes = re.findall(r'\.([\w-]+)', b.split('{')[0])
        if not classes or any(re.search(r'(?<![\w-])' + re.escape(c) + r'(?![\w-])', body) for c in classes):
            kept.append(b)
    text = ''.join(kept)
    for b in blocks:
        if b.startswith('@keyframes') and re.search(r'animation:' + re.escape(b.split('{')[0].split()[1]) + r'(?![\w-])', text):
            kept.append(b)
    return '\n'.join(kept)


def svg(vb, body, title):
    return standalone(vb, body, title, css=prune_css(COMIC_CSS, body), defs=DEFS if 'ah)' in body else COMIC_DEFS)


# ---------- pieces ----------
def scene(w, h, body, bg=BG):
    return f'<rect width="{w}" height="{h}" fill="{bg}"/><rect width="{w}" height="{h}" fill="url(#dots)" opacity=".22"/>{body}'


def desk(x, y, s=1, top=WOOD, badge=False, dark=False):
    top = '#8a867a' if dark else top
    g = (f'<g transform="translate({x:.0f} {y:.0f}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round">'
         f'<path d="M-18 6v15M18 6v15" fill="none" stroke-width="3"/><rect x="-25" y="-6" width="50" height="13" rx="3" fill="{top}"/>'
         f'<rect x="-10" y="-16" width="20" height="10" rx="1.5" fill="{PAPER}" stroke-width="2"/>')
    if badge:
        g += f'<circle cx="0" cy="-27" r="8" fill="{GOLD}" stroke-width="2"/><path d="M-4 -27l3 3 5-6" fill="none" stroke-width="2"/>'
    return g + '</g>'


def ring_pts(cx, cy, rx, ry, n, start=-90):
    return [(cx + rx * math.cos(math.radians(start + 360 * i / n)), cy + ry * math.sin(math.radians(start + 360 * i / n))) for i in range(n)]


def ring(cx, cy, rx, ry, w=3):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{INK}" stroke-width="{w}" stroke-dasharray="10 7"/>'


def note(x, y, rot=0, s=1, fill=PAPER, txt='', cross=False):
    g = (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})" stroke="{INK}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round">'
         f'<rect x="-18" y="-13" width="36" height="26" rx="2" fill="{fill}"/>')
    if txt:
        g += f'<text y="5" text-anchor="middle" class="w-s" style="stroke:none">{txt}</text>'
    else:
        g += f'<path d="M-11 -4h22M-11 3h14" stroke-width="1.6" opacity=".5" fill="none"/>'
    if cross:
        g += f'<path d="M-16 -11L16 11M16 -11L-16 11" stroke="{RED}" stroke-width="2.5"/>'
    return g + '</g>'


def clk(x, y, a=0, s=1, fill=PAPER):
    """A small clock with no digits; the hand angle says earlier or later."""
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2" stroke-linecap="round">'
            f'<circle r="9" fill="{fill}"/><path d="M0 0V-6" transform="rotate({a})" stroke-width="2"/><path d="M0 0H4" transform="rotate({a * 2 + 80})" stroke-width="2"/></g>')


def stamp(x, y, rot=-8, txt='RECEIVED'):
    w = 14 + 7.4 * len(txt)
    return (f'<g transform="translate({x} {y}) rotate({rot})"><rect x="{-w / 2:g}" y="-10" width="{w:g}" height="20" rx="3" fill="{PAPER}" stroke="{RED}" stroke-width="2.5"/>'
            f'<text y="4" text-anchor="middle" class="micro" style="fill:{RED}">{txt}</text></g>')


def binn(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round">'
            f'<path d="M-22 -18L-17 24H17L22 -18Z" fill="{GREY}"/><rect x="-26" y="-24" width="52" height="8" rx="2" fill="#8a867a"/>'
            f'<path d="M-8 -10V16M0 -10V16M8 -10V16" stroke-width="1.5" opacity=".5"/></g>')


def arrow(d, flow=True):
    return f'<path d="{d}" fill="none" stroke="{RED}" stroke-width="3" stroke-linecap="round" marker-end="url(#ah)"{' class="m-flow"' if flow else ''}/>'


def tray(x, y, w=80, rows=1, per=4, cross=0, tidy=True, fills=(SAND, GREEN, PURPLE)):
    h = 12 + rows * 17
    g = (f'<rect x="{x - w / 2:g}" y="{y}" width="{w}" height="{h}" rx="4" fill="{WOOD}" stroke="{INK}" stroke-width="2.5"/>')
    k = 0
    for r in range(rows):
        for i in range(per):
            nx = x - w / 2 + 8 + i * (w - 16) / per
            g += f'<rect x="{nx:.0f}" y="{y + 5 + r * 17}" width="{(w - 16) / per - 3:.0f}" height="13" fill="{fills[k % 3]}" stroke="{INK}" stroke-width="1.5"/>'
            if k < cross:
                g += f'<path d="M{nx:.0f} {y + 5 + r * 17}l{(w - 16) / per - 3:.0f} 13" stroke="{RED}" stroke-width="2"/>'
            k += 1
    return g


def clip(x, y, ticks=3, s=1):
    g = (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round">'
         f'<rect x="-22" y="-30" width="44" height="60" rx="4" fill="{WOOD}"/><rect x="-17" y="-24" width="34" height="50" fill="{PAPER}" stroke-width="1.5"/>'
         f'<rect x="-8" y="-33" width="16" height="8" rx="2" fill="#8a867a"/>')
    for i in range(ticks):
        g += f'<path d="M-12 {-14 + i * 14}l4 4 7-8M0 {-10 + i * 14}h12" stroke-width="2" fill="none" stroke="{TEAL if i < ticks else INK}"/>'
    return g + '</g>'


def book(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"><rect x="-30" y="-24" width="60" height="48" rx="3" fill="{PURPLE}"/>'
            f'<rect x="-30" y="-24" width="9" height="48" fill="{RED}"/><path d="M-12 -10h28M-12 0h28M-12 10h18" stroke-width="2" opacity=".55"/></g>')


def tick(x, y, s=1, col=TEAL):
    return f'<path transform="translate({x} {y}) scale({s})" d="M-14 0l10 11 20-24" fill="none" stroke="{col}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'


def tag(w, h, txt):
    return f'<text x="{w - 8}" y="{h - 8}" text-anchor="end" class="micro" style="fill:#6b6552">{txt}</text>'


def cap(w, h, txt, y=None):
    return f'<text x="{w / 2:g}" y="{y or h - 26}" text-anchor="middle" class="b-s">{txt}</text>'


def bud(x, y, word, color, s=1, cls=''):
    return buddy(x, y, word, color, s, cls, label_cls='w-s')


def sfx(x, y, txt, small=True, rot=-6):
    return f'<text x="{x}" y="{y}" text-anchor="middle" class="{"sfx-s" if small else "sfx"}" transform="rotate({rot} {x} {y})">{txt}</text>'


PANELS = []   # (src, title, body)


def add(src, title, body):
    PANELS.append((f'{SLUG}/{src}', title, body))


# ============================ LEAD 600x340 ============================
W, H = 600, 340
pts = ring_pts(300, 205, 200, 78, 6, -90)
b = ring(300, 205, 200, 78) + ''.join(desk(x, y, 1.2, badge=(i != 4)) for i, (x, y) in enumerate(pts))
b += ''.join(note(x, y + 36, 0, .8, PAPER) for i, (x, y) in enumerate(pts) if i != 4)
b += stamp(300, 195, -6, 'RECEIVED') + bud(55, 285, 'tester', GREEN, 1.2, 'm-bob') + clip(150, 295, 3, .9)
b += t(300, 40, 'Did the note survive?', 'w', style='font-size:30px') + t(300, 66, 'Six desks said received. A tester checks the folders.', 'b-s')
b += bubble(400, 285, 170, 40, ['Which desk kept it?'], (340, 262), 'b-s')
add('lead/tester-at-the-ring.svg', 'A tester with a clipboard checks a ring of six desks for notes stamped received', scene(W, H, b))

b = bud(100, 100, 'writer', ORANGE, 1.4) + bud(500, 100, 'writer', PURPLE, 1.4)
b += note(160, 140, -10, 1.5, '#fde7b0') + clk(160, 108, -50, 1.3) + note(440, 140, 10, 1.5, '#d9ccea') + clk(440, 108, 60, 1.3)
b += desk(300, 245, 2.0) + bud(300, 150, 'clerk', GREEN, 1.4) + note(300, 232, 0, 1.4, '#fde7b0')
b += binn(520, 275, 1.6) + note(505, 225, 25, 1.3, '#d9ccea', cross=True) + arrow('M470 160Q520 160 515 205') + arrow('M200 130Q250 160 280 200', False)
b += t(300, 44, 'Two versions. One survives.', 'w', style='font-size:28px') + t(240, 310, 'The clerk keeps the later clock stamp.', 'b')
b += sfx(500, 318, 'DROP!', False, -6)
add('lead/note-goes-missing.svg', 'Two versions of one note arrive; the clerk keeps the later stamp and bins the other', scene(W, H, b))

# ============================ STORY 440x215 ============================
W, H = 440, 215
b = bud(60, 90, 'person', ORANGE, 1.1) + note(120, 78, -8, 1.1) + arrow('M140 78H190') + bud(240, 80, 'clerk', GREEN, 1.1) + stamp(300, 40, -10)
b += desk(380, 100, 1.2) + t(380, 150, 'folder', 'b-s')
b += cap(W, H, 'Later: the note is not in the folder.', 192)
b += f'<g transform="translate(380 70)"><circle r="16" fill="{PAPER}" stroke="{RED}" stroke-width="2.5"/><text y="8" text-anchor="middle" class="w">?</text></g>'
b += f'<path d="M80 160l-8 -2m8 2q10 8 28 0" fill="none" stroke="{INK}" stroke-width="2"/>'
add('story/01-does-saved-mean-saved.svg', 'A note is stamped received but later cannot be found in the folder', scene(W, H, b))

b = desk(220, 120, 1.4) + bud(220, 62, 'clerk', GREEN, .9)
b += note(70, 70, -8, 1.2, '#fde7b0') + clk(70, 42, -50, 1.1) + note(70, 140, 6, 1.2, '#d9ccea') + clk(70, 112, 60, 1.1)
b += t(70, 20, 'earlier', 'micro') + t(70, 180, 'later', 'micro')
b += arrow('M100 70Q150 90 180 110', False) + arrow('M100 140Q150 135 185 128', False)
b += binn(370, 150, 1.3) + note(350, 100, 20, 1.2, '#fde7b0', cross=True) + arrow('M275 100Q330 70 345 85') + cap(W, H, 'Later stamp wins. The earlier one is dropped.', 202)
add('story/02-later-stamp-wins.svg', 'Two notes about the same cell; the clerk keeps the later and bins the earlier', scene(W, H, b))

b = f'<rect x="30" y="30" width="380" height="140" rx="6" fill="{WOOD}" stroke="{INK}" stroke-width="3"/><path d="M30 100H410" stroke="{INK}" stroke-width="3"/>'
b += tray(120, 42, 150, 1, 5) + tray(310, 42, 150, 1, 5, cross=3)
b += ''.join(note(100 + i * 24, 130 + (i % 2) * 6, -5 + i * 7, .9, [SAND, GREEN, PURPLE][i % 3], cross=i in (0, 2)) for i in range(5))
b += t(120, 90, 'add-only', 'w-s', style='font-size:17px') + t(310, 90, 'change-in-place', 'w-s', style='font-size:17px')
b += tick(120, 128, .9) + f'<text x="310" y="150" text-anchor="middle" class="sfx-s">scribbled!</text>' + cap(W, H, 'Neat stacks are safe. Overwrites are not.', 198)
add('story/03-safe-and-unsafe.svg', 'A shelf with a neat add-only tray and a scribbled change-in-place tray', scene(W, H, b))

b = tray(130, 62, 170, 3, 10, cross=0) + bud(330, 90, 'tester', GREEN, 1.2) + clip(390, 80, 3, .9)
b += t(130, 40, '1009 stamped notes', 'w-s', style='font-size:19px') + arrow('M215 60Q250 40 290 70')
b += f'<g><rect x="215" y="124" width="170" height="34" rx="6" fill="{PAPER}" stroke="{RED}" stroke-width="2.5"/><text x="300" y="148" text-anchor="middle" class="w-s" style="fill:{RED};font-size:18px">285 gone</text></g>'
b += cap(W, H, 'Count again: some are missing.', 184) + tag(W, H, SRC_LBL)
add('story/04-counting-survivors.svg', 'A tray of 1009 stamped notes is recounted and 285 are gone', scene(W, H, b))

# ============================ COMIC 320x220 ============================
W, H = 320, 220
b = bud(70, 90, 'reader', ORANGE, 1) + bud(250, 90, 'reader', PURPLE, 1)
b += note(70, 140, -4, 1.3, '#fde7b0', 'a') + note(250, 140, 4, 1.3, '#d9ccea', 'a')
b += note(110, 60, 0, .9, SAND, 'b') + note(210, 60, 0, .9, GREEN, 'c') + t(110, 36, '+ b', 'w-s') + t(210, 36, '+ c', 'w-s')
b += cap(W, H, 'Each copy starts as a.', 192)
add('comic/01a-two-readers.svg', 'Two people each hold a copy of note a; one adds b and the other adds c', scene(W, H, b))

b = desk(250, 120, 1.3) + bud(250, 62, 'clerk', GREEN, .9)
b += note(70, 55, -10, 1.1, '#fde7b0') + clk(70, 28, -50, 1) + note(70, 140, 8, 1.1, '#d9ccea') + clk(70, 112, 60, 1)
b += arrow('M105 60Q150 70 195 100') + arrow('M105 140Q150 135 195 125') + cap(W, H, 'Both notes head to one desk.', 192)
add('comic/01b-both-send.svg', 'Two notes with different clock stamps fly toward one desk', scene(W, H, b))

b = bud(100, 70, 'clerk', GREEN, 1.1) + desk(100, 130, 1.4) + note(100, 112, 0, 1.2, '#d9ccea') + clk(122, 98, 60, 1)
b += binn(230, 135, 1.2) + note(225, 85, 20, 1.1, '#fde7b0', cross=True) + arrow('M160 90Q215 60 225 70')
b += bud(270, 60, 'sender', ORANGE, .6) + sfx(255, 30, 'oh no!') + cap(W, H, 'Later stamp kept. The other note falls.', 192)
add('comic/01c-later-wins.svg', 'The clerk keeps the later note and the other falls in the bin', scene(W, H, b))

b = desk(250, 100, 1.4) + bud(60, 100, 'runner', ORANGE, 1.0)
b += arrow('M100 80Q175 40 220 70') + arrow('M220 105Q175 125 105 105', False) + t(165, 36, 'trip 1: read', 'b-s') + t(165, 140, 'back with the answer', 'b-s')
b += arrow('M100 160Q180 185 225 140') + t(120, 190, 'trip 2: write', 'b-s') + cap(W, H, 'Read, then write: two trips.', 210)
add('comic/02a-two-trips.svg', 'A runner goes to the desk to read, comes back, then goes again to write', scene(W, H, b))

b = desk(250, 110, 1.5) + bud(60, 110, 'runner', ORANGE, 1.1) + note(110, 95, 0, 1) + arrow('M125 100Q185 70 215 95')
b += t(165, 40, 'one trip', 'w') + cap(W, H, 'Drop the note off and done.', 192)
add('comic/02b-one-trip.svg', 'A runner makes one trip to the desk and drops a note off', scene(W, H, b))

b = bud(70, 75, 'runner', ORANGE, 1.1) + f'<g transform="translate(70 150)"><path d="M-30 -14h60l10 14l-10 14h-60z" fill="{PAPER}" stroke="{INK}" stroke-width="2.5"/><text y="6" text-anchor="middle" class="w-s">1 trip</text></g>'
b += desk(235, 140, 1.7) + note(235, 112, 0, 1.4) + f'<path d="M225 100h20v-8a10 10 0 0 0 -20 0z" fill="none"/>'
b += f'<g transform="translate(262 92)" stroke="{INK}" stroke-width="2.5"><rect x="-10" y="0" width="20" height="16" rx="2" fill="{GOLD}"/><path d="M-6 0v-6a6 6 0 0 1 12 0v6" fill="none"/></g>'
b += f'<g transform="translate(205 98)" stroke="{RED}" stroke-width="3" stroke-linecap="round"><path d="M-8 -8L8 8M8 -8L-8 8"/></g>' + cap(W, H, 'The price: a locked note can\'t be edited.', 200)
add('comic/02c-the-price.svg', 'A one-trip runner holds a price tag; a note on the desk is locked and cannot be edited', scene(W, H, b))

pts = ring_pts(210, 112, 80, 40, 5, -90)
b = ring(210, 112, 80, 40, 2.5) + ''.join(desk(x, y, .7) for x, y in pts) + bud(60, 110, 'tester', GREEN, 1.0) + clip(110, 130, 3, .7)
b += f'<g transform="translate(210 112)" stroke="{INK}" stroke-width="2.5"><rect x="-10" y="-4" width="20" height="16" rx="2" fill="{GOLD}"/><path d="M-6 -4v-6a6 6 0 0 1 12 0v6" fill="none"/></g>'
b += ''.join(clk(x, y + 168 - 112 + 0, 30 * i, .9) for i, (x, y) in enumerate(ring_pts(210, 112, 80, 0, 5, 180)[:0])) + ''.join(clk(150 + i * 30, 178, 25 * i, 1) for i in range(5))
b += cap(W, H, 'Easy test: clocks synced, a lock in place.', 208)
add('comic/03a-easy-test.svg', 'A tester sets up a ring of desks with a lock on a door and a row of matching clocks', scene(W, H, b))

b = desk(160, 130, 1.8) + note(160, 98, 0, 1.2, SAND) + ''.join(bud(x, 50, w, c, .6) for x, w, c in [(50, 'hand', ORANGE), (115, 'hand', PURPLE), (205, 'hand', GREEN), (270, 'hand', SAND)])
b += ''.join(arrow(f'M{x} 80Q{(x + 160) / 2:g} 85 {160 + (x - 160) * .2:g} 92', False) for x in (50, 115, 205, 270))
b += f'<rect x="12" y="150" width="130" height="38" rx="4" fill="{PAPER}" stroke="{INK}" stroke-width="2.5"/><path d="M22 163h110M22 177h80" stroke="{INK}" stroke-width="2" opacity=".45"/>' + t(185, 172, 'tally of stamps', 'b-s', 'start')
b += cap(W, H, 'Many hands edit one cell.', 208)
add('comic/03b-keep-changing.svg', 'One cell with many hands taking turns changing it while a tally sheet counts stamps', scene(W, H, b))

b = f'<rect x="20" y="30" width="170" height="120" rx="4" fill="{PAPER}" stroke="{INK}" stroke-width="2.5"/>'
b += tray(105, 58, 140, 2, 8, cross=0) + t(105, 52, '1009 stamped', 'w-s') + f'<rect x="40" y="108" width="130" height="30" rx="4" fill="{PAPER}" stroke="{RED}" stroke-width="2.5"/><text x="105" y="129" text-anchor="middle" class="w-s" style="fill:{RED}">285 crossed out</text>'
b += bud(250, 110, 'tester', GREEN, 1.0) + f'<path d="M238 98q12 -6 24 0" fill="none" stroke="{INK}" stroke-width="2.5"/>' + t(250, 160, 'hmm.', 'w-s')
b += cap(W, H, 'Count them again.', 178) + tag(W, H, SRC_LBL)
add('comic/03c-count-lost.svg', 'A tally sheet with 1009 stamped notes and 285 crossed out; the tester frowns', scene(W, H, b))

b = tray(160, 55, 230, 2, 6, tidy=True) + bud(60, 150, 'writer', ORANGE, .9) + bud(260, 150, 'writer', PURPLE, .9)
b += arrow('M80 120Q110 100 120 85', False) + arrow('M240 120Q215 100 205 85', False) + cap(W, H, 'Each add gets its own slot. None touch.', 206)
add('comic/04a-set-adds.svg', 'A tray where each new note gets its own slot and none touch', scene(W, H, b))

b = ''.join(f'<rect x="{30 + c * 19}" y="{30 + r * 22}" width="15" height="17" fill="{[SAND, GREEN, PURPLE][(r + c) % 3]}" stroke="{INK}" stroke-width="1.2"/>' for r in range(4) for c in range(14))
b += tick(160, 150, 2.2) + t(160, 184, '2000 of 2000 survived', 'w-s') + cap(W, H, 'drawn as a few small rows', 206).replace('class="b-s"', 'class="micro"') + tag(W, H, SRC_LBL)
add('comic/04b-all-survived.svg', 'A big tick across a block of 2000 small notes, drawn as a few rows', scene(W, H, b))

b = bud(70, 100, 'reader', ORANGE, 1.1) + book(70, 160, .8) + tray(215, 90, 130, 2, 5) + tick(215, 160, 1.2)
b += bud(70, 60, 'reader', ORANGE, 0) if False else ''
b += cap(W, H, 'Read the rules: the neat tray is fine.', 202)
add('comic/04c-read-the-rules.svg', 'A person reading a thick rulebook beside a tray of neatly stacked notes', scene(W, H, b))

b = bud(55, 60, 'writer', ORANGE, .9) + bud(265, 60, 'writer', PURPLE, .9)
b += note(60, 140, -4, 1.5, '#fde7b0', '1 | -1') + note(260, 140, 4, 1.5, '#d9ccea', '2 | -2') + t(60, 172, 'a pair', 'micro') + t(260, 172, 'a pair', 'micro')
b += t(160, 90, 'same moment', 'w-s') + arrow('M115 100Q160 120 120 125', False)
b += cap(W, H, 'Two-part notes, handed in together.', 198) + tag(W, H, INV_LBL)
add('comic/05a-mixed-writes.svg', 'Two writers hand in two-part notes at the same moment', scene(W, H, b))

b = bud(70, 80, 'clerk', GREEN, 1.1) + note(160, 55, -6, 1.2, '#fde7b0', '1 | -1') + note(160, 110, 6, 1.2, '#d9ccea', '2 | -2')
b += arrow('M185 55Q225 50 250 90') + arrow('M185 110Q225 125 250 105') + note(265, 140, 0, 1.6, GREEN, '2 | -1')
b += cap(W, H, 'Picks the bigger of each part: a new note.', 196) + tag(W, H, INV_LBL)
add('comic/05b-pick-bigger.svg', 'A clerk picks one number from each note and pastes them into a new note', scene(W, H, b))

b = f'<g transform="translate(90 90)"><circle r="52" fill="{PAPER}" stroke="{INK}" stroke-width="3"/><path d="M0 0V-30M0 0L22 12" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
b += f'<text y="-60" text-anchor="middle" class="micro">…000</text></g>'
b += ''.join(f'<rect x="{180 + (i % 5) * 26}" y="{50 + (i // 5) * 22}" width="20" height="16" fill="{SAND}" stroke="{INK}" stroke-width="1.5"/>' for i in range(20) if i != 7)
b += f'<rect x="{180 + 2 * 26}" y="{50 + 22}" width="20" height="16" fill="{PAPER}" stroke="{RED}" stroke-width="2.5"/><path d="M{184 + 2 * 26} {56 + 22}l12 6" stroke="{RED}" stroke-width="2"/>'
b += t(240, 148, '1 in 200 corrupt', 'w-s') + t(240, 168, '58 of 10000', 'b-s') + cap(W, H, 'Clock ends in 000? One row went wrong.', 200) + tag(W, H, SRC_LBL)
add('comic/05c-one-in-200.svg', 'A clock face whose last digits are zeroes, next to a row of notes with one scribbled red', scene(W, H, b))

pts = ring_pts(230, 120, 64, 40, 4, -90)
b = ring(230, 120, 64, 40, 2.5) + ''.join(desk(x, y, .7, dark=(i != 0)) for i, (x, y) in enumerate(pts))
b += bud(60, 100, 'clerk', GREEN, 1.0) + note(110, 100, 0, 1.0) + t(60, 150, 'old = ?', 'w-s')
b += ''.join(arrow(f'M{230 + (x - 230) * .5:g} {120 + (y - 120) * .5:g}L{x:g} {y:g}', False) for x, y in pts[1:]) + arrow('M120 96Q160 60 215 80', False)
b += cap(W, H, 'Check the old note, then swap. 4 trips.', 198)
add('comic/06a-compare-and-set.svg', 'A clerk checks the old note before swapping, with arrows to and from the other desks', scene(W, H, b))

b = f'<g transform="translate(90 105)" stroke="{INK}" stroke-width="3" stroke-linejoin="round"><rect x="-40" y="-55" width="80" height="110" fill="{WOOD}"/><circle cx="24" cy="5" r="5" fill="{GOLD}"/></g>'
b += f'<path d="M70 70l-10 12l-4 -10l-8 6" stroke="{RED}" stroke-width="4" fill="none" stroke-linecap="round"/>' + sfx(70, 38, 'JAM!', True, -10)
b += bud(230, 100, 'helper', GREEN, 1.2) + f'<g transform="translate(190 140) rotate(-30)" stroke="{INK}" stroke-width="2.5"><circle r="9" fill="{GOLD}"/><rect x="8" y="-3" width="30" height="6" fill="{GOLD}"/></g>'
b += arrow('M185 150Q150 150 125 120') + cap(W, H, 'A patched key frees the stuck door.', 198)
add('comic/06b-deadlock-fix.svg', 'A stuck door with a jam; a helper hands over a patched key', scene(W, H, b))

b = f'<rect x="20" y="25" width="170" height="130" rx="4" fill="{PAPER}" stroke="{INK}" stroke-width="2.5"/>' + tray(105, 52, 140, 2, 8) + t(105, 46, '829 stamped', 'w-s')
b += f'<rect x="38" y="108" width="134" height="30" rx="4" fill="{PAPER}" stroke="{RED}" stroke-width="2.5"/><text x="105" y="129" text-anchor="middle" class="w-s" style="fill:{RED}">3 crossed out</text>'
b += f'<g transform="translate(250 100) rotate(40)" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"><path d="M-8 -45h16v50a10 10 0 1 1 -16 0z" fill="{GREY}"/><circle cy="-45" r="14" fill="{GREY}"/></g>'
b += t(260, 170, 'fixes', 'w-s') + cap(W, H, 'Far fewer lost, but not zero.', 198) + tag(W, H, SRC_LBL)
add('comic/06c-three-lost.svg', 'A tally sheet of 829 stamped notes with 3 crossed out, beside a wrench', scene(W, H, b))

# ============================ FACTS 160x100 ============================
def fact(src, title, icon, fig, label=SRC_LBL):
    b = icon + t(80, 62, fig, 'w-s', style='font-size:19px')
    parts = label.split(' · ')
    b += t(80, 78, parts[0], 'micro') + t(80, 91, '· ' + parts[1], 'micro')
    add(f'facts/{src}.svg', title, scene(160, 100, b, CREAM))


fact('lock-test-loss', 'Lock test: 285 of 1009 acknowledged writes lost',
     tray(80, 12, 70, 1, 4, cross=2) , '285 of 1009')
fact('set-adds', 'Set adds: 2000 of 2000 survived', tray(60, 14, 60, 1, 4) + tick(122, 28, .8), '2000 of 2000')
fact('counter-drift', 'Counters drifted by up to 50%', f'<g transform="translate(80 30)"><path d="M-26 14A28 28 0 0 1 26 14" fill="none" stroke="{INK}" stroke-width="3"/><path d="M0 14L14 -8" stroke="{RED}" stroke-width="3" stroke-linecap="round"/><circle cy="14" r="4" fill="{INK}"/></g>', 'up to 50%')
fact('corrupt-rows', 'Corrupt rows: 58 of 10000, about 1 in 200',
     ''.join(f'<rect x="{34 + i * 18}" y="14" width="14" height="18" fill="{SAND if i != 3 else PAPER}" stroke="{RED if i == 3 else INK}" stroke-width="2"/>' for i in range(5)), '1 in 200')
fact('lwt-lost', 'Lightweight transactions: 3 of 829 writes lost',
     tray(80, 12, 70, 1, 4) + f'<path d="M72 17l12 13" stroke="{RED}" stroke-width="2.5"/>', '3 of 829')
fact('four-trips', 'Four round trips for each write',
     desk(120, 26, .7) + bud(30, 24, '', ORANGE, .45) + arrow('M50 18Q85 8 108 20', False) + arrow('M108 32Q85 40 52 32', False), '4 trips')


# ============================ write + check ============================
def story_srcs(doc):
    found = []

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get('src'), str) and o['src'].startswith(SLUG + '/'):
                found.append((o['src'], o.get('width'), o.get('height')))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(doc)
    return found


if __name__ == '__main__':
    srcs = story_srcs(json.loads(SEED.read_text()))
    made = {}
    for rel, title, body in PANELS:
        w, h = next(((w, h) for s, w, h in srcs if s == rel), (None, None))
        assert w, f'not in story: {rel}'
        made[rel] = write(OUT, rel.replace(SLUG + '/', '', 1), svg(f'0 0 {w} {h}', body, title))
    missing = {s for s, _, _ in srcs} - set(made)
    assert not missing, f'not drawn: {sorted(missing)}'
    print(f'wrote {len(made)} files to {OUT}')
