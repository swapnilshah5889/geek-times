"""Draws the media for "Open-sourcing a 10x reduction in Apache Cassandra tail latency" (Rocksandra).

Run from the repo root:  python3 tools/draw_instagram_rocksandra.py
Writes standalone SVGs to backups/media/instagram-rocksandra/{lead,story,comic,facts}/.
Every media.src in data/seed/papers/instagram-rocksandra.json must be written.
Real numbers are stamped "From the source · reported".
"""
import json
import math
import re
from pathlib import Path

from media_kit import COMIC_CSS, COMIC_DEFS, INK, RED, standalone, t, write, anim, buddy, bubble

SLUG = 'instagram-rocksandra'
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'backups' / 'media' / SLUG
SEED = ROOT / 'data' / 'seed' / 'papers' / f'{SLUG}.json'

CREAM = '#fbf3dc'
TEAL = '#377675'
GREEN = '#a2c2a7'
GOLD = '#ffe597'
WOOD = '#d9b98a'
PAPER = '#fff8e3'
PURPLE = '#c3b2d8'
SAND = '#f7d79b'
ORANGE = '#efae78'
GREY = '#b5ab92'
BLUE = '#82acad'
SKIN = '#f0c9a0'
PEOPLE = ['#efae78', '#a2c2a7', '#c3b2d8', '#f7d79b', '#82acad', '#e7b0a6', '#b9c98a']

EXTRA_CSS = ('.needle{transform-box:view-box;animation:nd 5s ease-out infinite}'
             '@keyframes nd{0%{transform:rotate(-55deg)}60%,100%{transform:rotate(0)}}'
             '.stamp{font:italic 12px Georgia,serif;fill:#5b5646}'
             '.fig{font:bold 20px Georgia,serif}.fig-m{font:bold 18px Georgia,serif}.fig-s{font:bold 15px Georgia,serif}')
DEFS = COMIC_DEFS + (f'<marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
                     f'<path d="M0 0L10 5L0 10Z" fill="{RED}"/></marker>')


def prune_css(css, body):
    """Keep only the CSS rules whose classes (and keyframes) the drawing actually uses."""
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
        sel = b.split('{')[0]
        classes = re.findall(r'\.([\w-]+)', sel)
        if not classes or any(re.search(r'(?<![\w-])' + re.escape(c) + r'(?![\w-])', body) for c in classes):
            kept.append(b)
    text = ''.join(kept)
    for b in blocks:
        if b.startswith('@keyframes'):
            name = b.split('{')[0].split()[1]
            if re.search(r'animation:' + re.escape(name) + r'(?![\w-])', text):
                kept.append(b)
    return '\n'.join(kept)



def desk(x, y, s=1, top=WOOD, badge=False, dark=False):
    top = '#8a867a' if dark else top
    g = (f'<g transform="translate({x:.0f} {y:.0f}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round">'
         f'<path d="M-18 6v15M18 6v15" fill="none" stroke-width="3"/>'
         f'<rect x="-25" y="-6" width="50" height="13" rx="3" fill="{top}"/>'
         f'<rect x="-10" y="-16" width="20" height="10" rx="1.5" fill="{PAPER}" stroke-width="2"/>'
         f'<path d="M-6 -11h12" stroke-width="1.5" opacity=".5" fill="none"/>')
    if badge:
        g += f'<circle cx="0" cy="-27" r="8" fill="{GOLD}" stroke-width="2"/><path d="M-4 -27l3 3 5-6" fill="none" stroke-width="2"/>'
    return g + '</g>'



def envelope(x, y, rot=0, s=1, fill=PAPER):
    return (f'<g transform="translate({x:.0f} {y:.0f}) rotate({rot}) scale({s})" stroke="{INK}" stroke-width="2" stroke-linejoin="round">'
            f'<rect x="-13" y="-9" width="26" height="18" rx="2" fill="{fill}"/><path d="M-13 -9L0 2L13 -9" fill="none"/></g>')



def folder(x, y, w=54, h=40, color=SAND, rot=0, label=''):
    g = (f'<g transform="translate({x:.0f} {y:.0f}) rotate({rot})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round">'
         f'<path d="M{-w / 2} {-h / 2 + 6}V{-h / 2}Q{-w / 2} {-h / 2 - 4} {-w / 2 + 4} {-h / 2 - 4}H{-w / 2 + 18}L{-w / 2 + 24} {-h / 2 + 2}H{w / 2}V{-h / 2 + 6}Z" fill="{color}" opacity=".85"/>'
         f'<rect x="{-w / 2}" y="{-h / 2 + 5}" width="{w}" height="{h - 5}" rx="3" fill="{color}"/>'
         f'<path d="M{-w / 2 + 8} {h / 2 - 12}h{w * .5:.0f}" stroke-width="1.8" opacity=".5" fill="none"/>')
    if label:
        g += t(0, 6, label, 'micro', style='stroke:none')
    return g + '</g>'



def arrow(d, flow=True, w=3.5):
    return f'<path d="{d}" fill="none" stroke="{RED}" stroke-width="{w}" stroke-linecap="round" {"stroke-dasharray=" + chr(34) + "8 7" + chr(34) if flow else ""} marker-end="url(#ah)"{" class=" + chr(34) + "m-flow" + chr(34) if flow else ""}/>'



def meter(cx, cy, r, angle, past=False):
    """Worry meter dial: half circle, red line, needle drawn at `angle` (deg, 0 = straight up)."""
    a = math.radians(angle - 90)
    nx, ny = cx + (r - 10) * math.cos(a), cy + (r - 10) * math.sin(a)
    ra = math.radians(35 - 90)   # red threshold line at +35 degrees
    g = (f'<path d="M{cx - r} {cy}A{r} {r} 0 0 1 {cx + r} {cy}Z" fill="{PAPER}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
         f'<path d="M{cx - r + 8} {cy}A{r - 8} {r - 8} 0 0 1 {cx} {cy - r + 8}" fill="none" stroke="{GREEN}" stroke-width="7"/>'
         f'<path d="M{cx} {cy - r + 8}A{r - 8} {r - 8} 0 0 1 {cx + r - 8} {cy}" fill="none" stroke="{SAND}" stroke-width="7"/>'
         f'<path d="M{cx + (r - 18) * math.cos(ra):.1f} {cy + (r - 18) * math.sin(ra):.1f}L{cx + (r + 3) * math.cos(ra):.1f} {cy + (r + 3) * math.sin(ra):.1f}" stroke="{RED}" stroke-width="4.5" stroke-linecap="round"/>'
         f'<g class="needle" style="transform-origin:{cx}px {cy}px"><path d="M{cx} {cy}L{nx:.1f} {ny:.1f}" stroke="{INK}" stroke-width="4" stroke-linecap="round"/></g>'
         f'<circle cx="{cx}" cy="{cy}" r="6" fill="{INK}"/>')
    return g




def svg(vb, body, title):
    return standalone(vb, body, title, css=prune_css(COMIC_CSS + EXTRA_CSS, body), defs=DEFS if 'ah)' in body else COMIC_DEFS)


# ---------- characters and props ----------

def person(x, y, col, mood='ok', s=1, watch=False, hair=INK, cls=''):
    """Little customer; (x, y) is the point between the feet."""
    mouth = {'ok': 'M-3 -35h6', 'happy': 'M-4 -36q4 4 8 0', 'sad': 'M-4 -33q4 -4 8 0'}[mood]
    g = (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
         f'<path d="M-4 -6V0M4 -6V0" fill="none"/><rect x="-9" y="-30" width="18" height="24" rx="7" fill="{col}"/>'
         f'<circle cy="-39" r="9" fill="{SKIN}"/><path d="M-9 -41Q-9 -50 0 -50Q9 -50 9 -41Q3 -45 -9 -41Z" fill="{hair}"/>'
         f'<circle cx="-3.5" cy="-39" r="1.3" fill="{INK}" stroke="none"/><circle cx="3.5" cy="-39" r="1.3" fill="{INK}" stroke="none"/>'
         f'<path d="{mouth}" fill="none" stroke-width="1.6"/>')
    if watch:
        g += f'<path d="M9 -24l8 -6" fill="none"/><circle cx="18" cy="-31" r="4" fill="{GOLD}"/>'
    return g + '</g>'


def octagon(cx, cy, r):
    pts = ' '.join(f'{cx + r * math.cos(math.radians(22.5 + 45 * i)):.1f},{cy + r * math.sin(math.radians(22.5 + 45 * i)):.1f}' for i in range(8))
    return f'<polygon points="{pts}" fill="{RED}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'


def janitor(x, y, s=1, sign=True, R=21, cls='m-wobble'):
    g = (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
         f'<path d="M-20 -34L-26 2" fill="none" stroke-width="3"/><path d="M-32 2L-20 2L-22 -8Z" fill="#c9a36a"/>'
         f'<path d="M-4 -6V0M4 -6V0" fill="none"/><rect x="-10" y="-31" width="20" height="25" rx="7" fill="{BLUE}"/>'
         f'<circle cy="-40" r="9.5" fill="{SKIN}"/><path d="M-10 -43Q-10 -55 0 -55Q10 -55 10 -43Z" fill="#5d6aa1"/><path d="M-12 -43h26" />'
         f'<circle cx="-3.5" cy="-39" r="1.3" fill="{INK}" stroke="none"/><circle cx="3.5" cy="-39" r="1.3" fill="{INK}" stroke="none"/>'
         f'<path d="M-3 -35h6" fill="none" stroke-width="1.6"/>')
    if sign:
        g += '<path d="M10 -22L16 -34" fill="none"/>'
    g += '</g>'
    if sign:
        hx, hy = x + 16 * s, y - 34 * s
        top = hy - 40
        sg = (f'<path d="M{hx:.1f} {hy:.1f}V{top:.1f}" stroke="{INK}" stroke-width="3.5"/>' + octagon(hx, top, R)
              + t(f'{hx:.1f}', f'{top + 4:.1f}', 'STOP', 'micro', style='fill:#fff8e3;letter-spacing:0'))
        g += f'<g class="{cls}">{sg}</g>' if cls else sg
    return g


def scrap(x, y, rot=0, col=PAPER):
    return (f'<g transform="translate({x} {y}) rotate({rot})" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round">'
            f'<rect x="-8" y="-6" width="16" height="12" fill="{col}"/><path d="M-4 -1h8M-4 3h5" opacity=".5"/></g>')


def parcel(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2" stroke-linejoin="round">'
            f'<rect x="-11" y="-9" width="22" height="18" fill="{WOOD}"/><path d="M0 -9V9" stroke="{RED}" stroke-width="3"/></g>')


def counter(x, y, w, h=42):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="8" rx="2" fill="{WOOD}" stroke="{INK}" stroke-width="2.5"/>'
            f'<rect x="{x + 4}" y="{y + 8}" width="{w - 8}" height="{h}" fill="#c9a36a" stroke="{INK}" stroke-width="2.5"/>'
            f'<path d="M{x + 14} {y + 22}h{w - 28}" stroke="{INK}" stroke-width="1.5" opacity=".4"/>')


def engine(x, y, s=1, col=GREY, label='', old=False, shiny=False):
    g = (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round">'
         f'<path d="M-42 -4h-12v10h12" fill="{col}" stroke-width="2"/>'
         + ''.join(f'<rect x="{px - 7}" y="-30" width="14" height="12" rx="2" fill="{col}" stroke-width="2"/>' for px in (-22, 0, 22))
         + f'<rect x="-42" y="-20" width="84" height="44" rx="7" fill="{col}"/>'
         f'<circle cx="28" cy="2" r="9" fill="#edca75" stroke-width="2"/><circle cx="28" cy="2" r="3" fill="{INK}" stroke="none"/>')
    if shiny:
        g += '<path d="M-36 -12h30M-36 -6h14" stroke="#fff8e3" stroke-width="3" opacity=".8" fill="none"/>'
    if old:
        g += f'<circle cx="-30" cy="14" r="2.5" fill="#7a4a3a" stroke="none"/><circle cx="-12" cy="-8" r="2" fill="#7a4a3a" stroke="none"/><circle cx="6" cy="16" r="2.5" fill="#7a4a3a" stroke="none"/>'
    g += '</g>'
    if label:
        g += (f'<rect x="{x - 28:g}" y="{y + 4 * s:g}" width="52" height="17" rx="3" fill="{PAPER}" stroke="{INK}" stroke-width="1.6"/>'
              + t(f'{x - 2:g}', f'{y + 4 * s + 13:g}', label, 'micro', style='letter-spacing:0'))
    return g


def machine(x, y, w, h, lid=True):
    g = ''
    if lid:
        g += (f'<path d="M{x + 6} {y}L{x + 22} {y - 28}H{x + w - 22}L{x + w - 6} {y}Z" fill="#b8c4be" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>')
    g += (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#cfd8d3" stroke="{INK}" stroke-width="3"/>'
          f'<rect x="{x + w * .15:g}" y="{y + 8}" width="{w * .7:g}" height="{min(44, h - 30):g}" rx="4" fill="#6e6a5e" stroke="{INK}" stroke-width="2"/>'
          f'<circle cx="{x + 10}" cy="{y + h - 10}" r="2.5" fill="{INK}"/><circle cx="{x + w - 10}" cy="{y + h - 10}" r="2.5" fill="{INK}"/>')
    return g


def hand(x, y, rot=0):
    return (f'<g transform="translate({x} {y}) rotate({rot})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round">'
            f'<rect x="-10" y="-70" width="20" height="60" fill="#e7b0a6"/><ellipse cy="0" rx="20" ry="16" fill="{SKIN}"/>'
            f'<path d="M-12 8v8M-4 10v9M4 10v9M12 8v8" fill="none" stroke-width="3"/></g>')


def stamp(cx, y, w=172):
    return (f'<rect x="{cx - w / 2:g}" y="{y}" width="{w}" height="18" rx="9" fill="{PAPER}" stroke="{INK}" stroke-width="1.5"/>'
            + t(cx, y + 13, 'From the source · reported', 'stamp'))


def floor(y, w):
    return f'<path d="M0 {y}H{w}" stroke="{INK}" stroke-width="2" opacity=".35"/>'


def clock(cx, cy, r, slice_deg=0):
    g = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{PAPER}" stroke="{INK}" stroke-width="3"/>'
    for i in range(12):
        a = math.radians(i * 30)
        g += f'<path d="M{cx + (r - 6) * math.sin(a):.1f} {cy - (r - 6) * math.cos(a):.1f}L{cx + (r - 2) * math.sin(a):.1f} {cy - (r - 2) * math.cos(a):.1f}" stroke="{INK}" stroke-width="2"/>'
    if slice_deg:
        a = math.radians(slice_deg)
        g += f'<path d="M{cx} {cy}V{cy - r + 3}A{r - 3} {r - 3} 0 0 1 {cx + (r - 3) * math.sin(a):.1f} {cy - (r - 3) * math.cos(a):.1f}Z" fill="{RED}" stroke="{RED}" stroke-width="1"/>'
    return g + f'<circle cx="{cx}" cy="{cy}" r="3" fill="{INK}"/>'


def table(x, y, cw=26, rh=18, cols=3, rows=4):
    g = f'<g stroke="{INK}" stroke-width="2">'
    for r in range(rows):
        for c in range(cols):
            g += f'<rect x="{x + c * cw}" y="{y + r * rh}" width="{cw}" height="{rh}" fill="{TEAL if r == 0 else PAPER}"/>'
    return g + '</g>'


def doorway(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})" fill="none" stroke="{INK}" stroke-linecap="round">'
            f'<path d="M-34 44V-6Q-34 -42 0 -42Q34 -42 34 -6V44" stroke-width="9" stroke="#8b6b45"/>'
            f'<path d="M-34 44V-6Q-34 -42 0 -42Q34 -42 34 -6V44" stroke-width="2.5"/></g>')


def cloud(cx, cy, fill='#e8f3f0'):
    circ = [(-70, 10, 30), (-30, -12, 38), (20, -18, 40), (62, 0, 34), (0, 14, 36), (-40, 22, 28), (36, 24, 28)]
    g = ''.join(f'<circle cx="{cx + dx}" cy="{cy + dy}" r="{r + 3}" fill="{INK}"/>' for dx, dy, r in circ)
    return g + ''.join(f'<circle cx="{cx + dx}" cy="{cy + dy}" r="{r}" fill="{fill}"/>' for dx, dy, r in circ)


def checkbox(x, y, on=True):
    g = f'<rect x="{x}" y="{y}" width="18" height="18" rx="3" fill="{PAPER}" stroke="{INK}" stroke-width="2.5"' + ('' if on else ' stroke-dasharray="4 3"') + '/>'
    if on:
        g += f'<path d="M{x + 3} {y + 9}l5 5 8-11" fill="none" stroke="{RED}" stroke-width="3.5" stroke-linecap="round"/>'
    return g


PANELS = []


def bg(w, h, col, body):
    return f'<rect width="{w}" height="{h}" fill="{col}"/><rect width="{w}" height="{h}" fill="url(#dots)" opacity=".22"/>{body}'


def comic(name, title, col, body):
    PANELS.append((f'comic/{name}.svg', '0 0 320 220', title, bg(320, 220, col, body)))


def story(name, title, col, body):
    PANELS.append((f'story/{name}.svg', '0 0 440 215', title, bg(440, 215, col, body)))


def icon(name, title, body, fig, cls='fig'):
    body += t(80, 71, fig, cls) + t(80, 91, 'From the source · reported', 'stamp')
    PANELS.append((f'facts/{name}.svg', '0 0 160 100', title, bg(160, 100, '#f0e3c6', body)))


def plate(name, title, col, tag, body, caption):
    PANELS.append((f'lead/{name}.svg', '0 0 600 340', title,
                   bg(600, 340, col, body)
                   + f'<rect x="10" y="288" width="580" height="44" fill="{CREAM}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
                   + t(300, 317, caption, 'b') + t(22, 30, tag, 'micro', 'start', f'fill:{RED}')
                   + f'<path d="M8 10Q300 5 592 9Q596 170 591 332Q300 336 9 331Q4 170 8 10Z" fill="none" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>'))


def line_up(xs, y, moods, s=1, watches=()):
    return ''.join(person(x, y, PEOPLE[i % 7], moods[i], s, watch=i in watches) for i, x in enumerate(xs))


# ===================== Lead plates =====================
b = floor(266, 600) + counter(30, 196, 120, 62) + person(90, 204, '#e7b0a6', 'ok')
b += janitor(205, 266, 1.4, True, 26)
for i, x in enumerate(range(290, 570, 40)):
    b += person(x, 266, PEOPLE[i % 7], 'sad', 1.2, watch=i % 2 == 0)
b += scrap(240, 262, 15) + scrap(262, 258, -20, '#f7d79b') + scrap(168, 260, 30)
b += f'<g class="m-pulse">' + t(470, 120, 'FREEZE!', 'sfx') + '</g>'
plate('pause-the-line', 'A janitor holds a stop sign at the counter while the whole line waits.', '#f0e3c6', 'THE LINE FREEZES', b,
      'Everyone waits while the janitor works.')

b = floor(266, 600) + machine(210, 170, 190, 98)
b += engine(120, 232, 1.3, '#a89c85', 'Java', old=True) + scrap(60, 262, 20) + scrap(170, 258, -15) + scrap(190, 266, 40, SAND)
b += '<g class="m-bob">' + hand(310, 104) + engine(310, 148, 1.2, TEAL, 'RocksDB', shiny=True) + '</g>'
b += '<g class="m-pulse">' + t(500, 120, 'SWAP!', 'sfx') + '</g>' + t(120, 176, 'old engine', 'b-s')
plate('swap-the-engine', 'A hand lowers a new engine into an open machine while the old engine rests on the floor.', '#e8e2cc', 'SWAP THE ENGINE', b,
      'The rest of the machine stays put.')

# ===================== Story panels =====================
b = floor(165, 440) + f'<path d="M388 100V165" stroke="{INK}" stroke-width="3" stroke-dasharray="6 4"/>' + t(388, 90, 'finish', 'b-s')
for i, x in enumerate((250, 280, 310, 340, 368)):
    b += person(x, 165, PEOPLE[i], 'happy', .85)
b += person(60, 165, PEOPLE[5], 'sad', .85, watch=True) + janitor(150, 165, .9, True, 20)
b += t(310, 195, 'most reads: quick', 'b-s') + t(70, 195, 'a few: stuck', 'b-s') + t(220, 30, 'The slowest reads', 'b')
story('01-slow-tail', 'Most runners cross the line together while one stuck runner is stopped by a janitor with a stop sign.', '#f0e3c6', b)

b = machine(150, 78, 150, 96) + t(225, 150, 'Cassandra', 'w-s', style='font-size:16px')
b += engine(70, 70, 1, '#a89c85', 'Java', old=True) + arrow('M105 70Q130 30 160 50', False)
b += scrap(60, 120, 20) + scrap(95, 125, -10)
b += '<g class="m-bob">' + engine(375, 84, 1, TEAL, 'RocksDB', shiny=True) + '</g>' + arrow('M335 90Q320 110 305 108')
b += t(375, 128, 'C++', 'mono-s') + t(70, 150, 'out', 'b-s') + t(220, 200, 'same machine, new engine', 'b-s')
story('02-swap-engine', 'A machine labeled Cassandra with its old engine lifted out and a RocksDB engine ready.', '#e8e2cc', b)

b = table(24, 52, 28, 18) + t(66, 138, 'table', 'b-s')
b += buddy(180, 90, 'rules', PURPLE, .95) + arrow('M112 90H138') + arrow('M222 90H262')
b += doorway(375, 100, 1.2) + engine(375, 112, .75, TEAL, 'new', shiny=True)
b += ''.join(f'<rect x="{250 + i * 2}" y="{128 + 0}" width="0" height="0"/>' for i in range(0)) + t(375, 168, 'doorway', 'b-s') + t(225, 205, 'plain boxes: key + value', 'b-s')
for i, w in enumerate(('key', 'value')):
    b += f'<rect x="{266 + i * 0}" y="{52 + i * 26}" width="46" height="20" rx="3" fill="{[SAND, GREEN][i]}" stroke="{INK}" stroke-width="2"/>' + t(289, 67 + i * 26, w, 'micro', style='letter-spacing:0')
story('03-fit-engine', 'A translator hands plain labeled boxes made from a table to a new engine behind a doorway.', '#dfe9e2', b)

def bars(x, vals, cols, labels, h):
    g = ''
    for i, (v, c) in enumerate(zip(vals, cols)):
        bx = x + i * 66
        g += (f'<rect x="{bx}" y="{165 - h[i]:g}" width="46" height="{h[i]:g}" rx="3" fill="{c}" stroke="{INK}" stroke-width="2.5"/>'
              + t(bx + 23, f'{159 - h[i]:g}', v, 'w-s', style='font-size:18px') + t(bx + 23, 183, labels[i], 'b-s'))
    return g
b = floor(165, 440) + t(110, 28, 'P99 read, ms', 'b-s') + t(330, 28, 'GC stall', 'b-s')
b += bars(55, ['60', '20'], [ORANGE, TEAL], ['before', 'after'], [96, 32]) + bars(275, ['2.5%', '0.3%'], [ORANGE, TEAL], ['before', 'after'], [96, 11.5])
b += stamp(220, 192)
story('04-evidence', 'Two pairs of bars: P99 read 60 down to 20 ms, GC stall 2.5 percent down to 0.3 percent.', '#f0e3c6', b)

# ===================== Comic panels =====================
cl = counter(18, 128, 92, 44) + person(64, 136, '#e7b0a6', 'ok') + counter(18, 128, 92, 44) + floor(178, 320)
b = cl + line_up((150, 195, 240, 285), 176, ['happy'] * 4) + parcel(168, 152) + bubble(150, 30, 100, 38, ['Thanks!'], (152, 126))
comic('01a-quick-line', 'A counter with a short line; each person gets a parcel quickly and smiles.', '#f0e3c6', b)

b = cl + line_up([140 + i * 24 for i in range(7)], 176, ['ok'] * 4 + ['sad'] * 3, .9, watches=(4, 5, 6)) + bubble(150, 30, 150, 40, ['Still waiting…'], (290, 128))
comic('01b-slow-few', 'A line of people where the three at the back check watches and frown.', '#f0e3c6', b)

b = floor(176, 320) + t(160, 28, 'P99: the wait 99 in 100 beat', 'b-s') + line_up([36 + i * 30 for i in range(6)], 176, ['happy'] * 6, .9)
b += f'<path d="M210 176V104" stroke="{INK}" stroke-width="3.5"/><path d="M212 104H252L242 116L252 128H212Z" fill="{RED}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
b += t(228, 121, 'P99', 'micro', style='fill:#fff8e3;letter-spacing:0') + person(280, 176, PEOPLE[5], 'sad', .9, watch=True)
b += f'<path d="M26 190Q110 206 196 190" fill="none" stroke="{INK}" stroke-width="2.5"/>' + t(110, 212, 'served by here', 'b-s') + t(282, 200, 'slowest', 'b-s')
comic('01c-p99-mark', 'A line with a P99 flag after the 99th person and one person waiting behind it.', '#e8e2cc', b)

b = floor(180, 320) + desk(160, 140, 1.6) + buddy(160, 74, 'Java', BLUE, .85)
for x, y, r, c in [(40, 160, 20, PAPER), (80, 190, -30, SAND), (118, 176, 50, PAPER), (210, 192, 10, GREEN), (250, 168, -20, PAPER), (284, 192, 40, SAND), (60, 120, -10, PAPER), (270, 120, 30, PAPER), (30, 196, 5, PAPER), (190, 204, -40, PAPER)]:
    b += scrap(x, y, r, c)
b += t(160, 208, 'scraps of paper everywhere', 'b-s')
comic('02a-scraps', 'A messy floor covered in scraps of paper around a busy desk.', '#f0e3c6', b)

b = floor(186, 320) + janitor(80, 186, 1.05, True, 20) + scrap(40, 180, 15) + scrap(120, 182, -20) + desk(236, 150, 1.5)
b += f'<g transform="translate(236 104)" stroke="{INK}" stroke-width="2" stroke-linejoin="round"><rect x="-17" y="-12" width="34" height="24" rx="3" fill="{PAPER}"/><path d="M-17 -12L0 2L17 -12" fill="none"/>'
b += f'<path d="M17 0l10 -14" fill="none"/><circle cx="28" cy="-17" r="4" fill="{SKIN}"/><circle cx="-5" cy="-2" r="1.5" fill="{INK}" stroke="none"/><circle cx="5" cy="-2" r="1.5" fill="{INK}" stroke="none"/></g>'
b += '<g class="m-pulse">' + t(200, 44, 'PAUSE!', 'sfx') + '</g>' + t(236, 214, 'a request waits', 'b-s')
comic('02b-janitor-stops', 'A janitor sweeps and holds a stop sign while a request waits at the desk with its hand up.', '#e8e2cc', b)

b = clock(86, 96, 46, 9) + t(86, 166, 'time stalled', 'b-s')
b += meter(238, 124, 56, -62) + t(238, 156, '2.5%', 'w', style='font-size:22px') + t(238, 176, 'at busy times', 'b-s') + stamp(160, 194)
comic('02c-stall-meter', 'A clock with a thin slice shaded, next to a meter pointing at a small mark.', '#f0e3c6', b)

b = floor(200, 320) + machine(70, 54, 180, 100) + engine(160, 100, 1.15, '#a89c85', 'Java', old=True)
b += ''.join(scrap(x, y, r) for x, y, r in [(120, 176, 20), (160, 188, -30), (200, 178, 45)]) + t(160, 34, 'the old engine', 'b-s') + t(160, 214, 'drops scraps', 'b-s')
comic('03a-old-engine', 'A machine with an old engine in the middle, dropping scraps of paper.', '#e8e2cc', b)

b = floor(196, 320) + f'<rect x="50" y="146" width="190" height="14" rx="3" fill="{WOOD}" stroke="{INK}" stroke-width="3"/><path d="M66 160v36M224 160v36" stroke="{INK}" stroke-width="4"/>'
b += engine(145, 112, 1.35, TEAL, 'C++', shiny=True) + f'<g class="m-twinkle"><use href="#mstar" x="210" y="70"/></g>'
b += janitor(285, 196, .62, False) + t(285, 214, 'far away', 'b-s') + t(145, 34, 'a new engine in C++', 'b-s')
comic('03b-new-engine', 'A shiny new engine with a C++ label on a workbench while the janitor watches from far away.', '#dfe9e2', b)

stone = (f'<rect x="60" y="136" width="200" height="60" rx="4" fill="{GREY}" stroke="{INK}" stroke-width="3.5"/>'
         f'<path d="M60 166H260M120 136V166M200 166V196M160 166V196" stroke="{INK}" stroke-width="2" opacity=".5"/>')
b = stone + t(160, 186, 'RocksDB', 'w', style='font-size:22px') + engine(160, 100, 1.3, TEAL, 'new', shiny=True) + t(160, 34, 'a sturdy base', 'b-s') + t(160, 214, 'open source database', 'b-s')
comic('03c-rocksdb-base', 'A new engine sitting on a sturdy block labeled RocksDB.', '#f0e3c6', b)

b = machine(14, 60, 124, 96, False) + engine(76, 92, .8, '#a89c85', old=True)
for gx, gy in [(40, 94), (112, 92), (60, 112), (92, 110)]:
    b += f'<ellipse cx="{gx}" cy="{gy}" rx="5" ry="3.5" fill="{GOLD}" stroke="{INK}" stroke-width="1.5"/>'
b += t(76, 190, 'old: glued in', 'b-s') + doorway(236, 100, 1.25) + engine(236, 112, .75, TEAL, '', shiny=True) + t(236, 190, 'new: a doorway', 'b-s')
comic('04a-glued', 'An old engine glued into a machine next to a new engine with a doorway frame.', '#e8e2cc', b)

b = table(14, 50, 24, 18) + t(50, 150, 'table', 'b-s') + buddy(154, 100, 'rules', PURPLE, .85) + arrow('M92 100H116') + arrow('M194 100H222')
for i, (w, c) in enumerate((('key', SAND), ('value', GREEN), ('key', SAND))):
    b += f'<rect x="232" y="{52 + i * 28}" width="56" height="22" rx="3" fill="{c}" stroke="{INK}" stroke-width="2"/>' + t(260, 68 + i * 28, w, 'micro', style='letter-spacing:0')
b += t(260, 160, 'plain boxes', 'b-s') + t(160, 205, 'translate between them', 'b-s')
comic('04b-translate', 'A table with columns on the left, plain labeled boxes on the right, a translator between them.', '#f0e3c6', b)

b = floor(182, 320) + f'<rect x="20" y="120" width="130" height="26" rx="4" fill="{WOOD}" stroke="{INK}" stroke-width="3"/>'
b += f'<g class="m-spin"><circle cx="46" cy="158" r="12" fill="{GREY}" stroke="{INK}" stroke-width="3"/></g><g class="m-spin"><circle cx="124" cy="158" r="12" fill="{GREY}" stroke="{INK}" stroke-width="3"/></g>'
b += folder(55, 104, 40, 30, SAND) + folder(100, 104, 40, 30, GREEN) + folder(78, 80, 40, 30, PURPLE) + folder(124, 82, 40, 30, SAND)
b += arrow('M158 112H196') + desk(250, 150, 1.5) + buddy(250, 70, 'load', ORANGE, .85) + t(85, 205, 'files on a cart', 'b-s') + t(250, 205, 'loaded in one go', 'b-s')
comic('04c-streaming', 'Several files stacked on a cart rolling toward a desk where a worker loads them in at once.', '#e8e2cc', b)

b = cloud(160, 100) + ''.join(desk(x, 112, 1.3, top=c) for x, c in ((95, WOOD), (160, WOOD), (225, WOOD))) + t(160, 206, 'three machines in the cloud', 'b')
comic('05a-three-machines', 'Three desks in a row inside a cloud-shaped room.', '#dfe9e2', b)

b = buddy(48, 62, 'load', ORANGE, .85) + parcel(104, 62) + parcel(128, 88, .9) + parcel(150, 112, .8)
b += ''.join(desk(x, 170, 1.1) for x in (70, 125, 180))
b += f'<g transform="translate(270 100) rotate(4)" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"><rect x="-38" y="-62" width="76" height="124" rx="6" fill="{PAPER}"/><rect x="-14" y="-70" width="28" height="12" rx="3" fill="{GREY}"/>'
b += t(0, -38, 'NDBench', 'micro', style='letter-spacing:0;stroke:none')
for i in range(3):
    b += f'<path d="M-24 {-12 + i * 28}l6 6 12 -14" fill="none" stroke="{RED}" stroke-width="3.5"/><path d="M0 {-8 + i * 28}h22" opacity=".5"/>'
b += '</g>' + t(150, 210, 'fill with data, then test', 'b-s')
comic('05b-load-test', 'A worker pours boxes into three desks while a clipboard checks results.', '#f0e3c6', b)

b = floor(112, 320) + floor(190, 320) + desk(36, 90, 1.1, top=GREY, dark=True) + line_up((90, 120), 112, ['ok', 'ok'], .85, watches=(1,))
b += t(20, 30, 'old desk: slow', 'b-s', 'start') + desk(36, 168, 1.1, top=GREEN, badge=True) + line_up([90 + i * 28 for i in range(8)], 190, ['happy'] * 8, .85)
b += t(20, 128, 'new desk: fast', 'b-s', 'start') + '<g class="m-pulse">' + t(252, 62, '10X', 'sfx') + '</g>' + t(252, 90, 'same P99: 2 ms', 'b-s') + stamp(160, 198)
comic('05c-more-reads', 'Two lines: a short line moves slowly at the old desk, a long line moves fast at the new desk.', '#e8e2cc', b)

fence = f'<g stroke="{INK}" stroke-width="2.5" stroke-linejoin="round">' + ''.join(f'<rect x="{138 + i * 14}" y="128" width="10" height="52" fill="{WOOD}"/>' for i in range(5)) + f'<path d="M134 142H214M134 164H214" fill="none"/></g>'
b = floor(182, 320) + person(52, 182, PEOPLE[0], 'happy', 1.1) + fence + person(250, 182, PEOPLE[1], 'happy', 1.1) + person(292, 182, PEOPLE[2], 'happy', 1.1)
b += bubble(14, 26, 130, 40, ['Take the code!'], (50, 124)) + arrow('M82 120Q130 70 168 92')
b += f'<g class="m-bob"><rect x="160" y="82" width="44" height="34" rx="4" fill="{PAPER}" stroke="{INK}" stroke-width="2.5"/>' + t(182, 106, '{ }', 'mono-s') + '</g>'
comic('06a-share-code', 'A box of code handed over a fence to waiting neighbors.', '#dfe9e2', b)

b = f'<rect x="44" y="20" width="232" height="184" rx="8" fill="{PAPER}" stroke="{INK}" stroke-width="3"/><rect x="132" y="12" width="56" height="16" rx="4" fill="{GREY}" stroke="{INK}" stroke-width="2.5"/>'
for i, (w, on) in enumerate((('reads', 1), ('writes', 1), ('streaming', 1), ('secondary indexes', 0), ('repair', 0))):
    b += checkbox(62, 44 + i * 32, bool(on)) + t(92, 59 + i * 32, w, 'b', 'start')
comic('06b-more-features', 'A checklist with a few items ticked and a few still empty.', '#f0e3c6', b)

b = floor(196, 320) + machine(150, 62, 140, 134, False) + f'<rect x="138" y="96" width="24" height="50" rx="4" fill="#6e6a5e" stroke="{INK}" stroke-width="3"/><path d="M146 108h8M146 118h8M146 128h8" stroke="{CREAM}" stroke-width="3"/>'
b += '<g class="m-bob">' + hand(58, 112, -90) + engine(70, 124, .8, TEAL, '', shiny=True) + f'<path d="M104 118h22M104 130h22" stroke="{INK}" stroke-width="4" stroke-linecap="round"/></g>'
b += t(220, 40, 'a plug-in slot', 'b') + t(220, 214, 'engines slide in', 'b-s')
comic('06c-plug-slot', 'A machine with an empty slot on its side and a hand holding a plug-in engine ready.', '#e8e2cc', b)

# ===================== Fact icons =====================
bar = lambda x, h, c: f'<rect x="{x}" y="{50 - h}" width="22" height="{h}" fill="{c}" stroke="{INK}" stroke-width="2.5"/>'
icon('p99-drop', 'A tall bar and a short bar with a down arrow, standing for latency dropping.', bar(44, 38, ORANGE) + bar(94, 13, TEAL) + arrow('M72 18Q80 24 90 40', False), '60 → 20 ms')
icon('gc-stall', 'A clock with a thin slice shaded for time lost to garbage collection.', clock(80, 30, 21, 9), '2.5% → 0.3%', 'fig-m')
icon('before-numbers', 'A steady line for the average and a spiky line for the slowest reads.',
     f'<path d="M20 46H140" stroke="{TEAL}" stroke-width="3.5" stroke-dasharray="6 4"/><path d="M20 38L36 20L52 40L68 14L84 36L100 18L116 40L140 22" fill="none" stroke="{RED}" stroke-width="3" stroke-linejoin="round"/>',
     '5 ms, 25 to 60 ms', 'fig-s')
icon('throughput', 'A desk with a stream of envelopes flowing out, standing for many reads.', desk(32, 34, 1.1, top=GREEN) + ''.join(envelope(70 + i * 15, 22 + (i % 2) * 18, 0, .7) for i in range(6)), '10X')
icon('benchmark-setup', 'Three small desks standing for three servers, with a table of rows.', ''.join(desk(34 + i * 46, 38, .85) for i in range(3)), '250M rows')
icon('year-of-work', 'A calendar page.',
     f'<rect x="52" y="8" width="56" height="42" rx="4" fill="{PAPER}" stroke="{INK}" stroke-width="2.5"/><rect x="52" y="8" width="56" height="12" rx="4" fill="{RED}" stroke="{INK}" stroke-width="2.5"/>'
     + ''.join(f'<circle cx="{62 + c * 12}" cy="{29 + r * 9}" r="2" fill="{INK}"/>' for r in range(2) for c in range(4)), 'About a year', 'fig-m')


# ===================== Write and check =====================
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
    wanted = {s.replace(SLUG + '/', '', 1) for s, _, _ in srcs}
    made = {}
    for rel, vb, title, body in PANELS:
        made[rel] = write(OUT, rel, svg(vb, body, title))
    missing = wanted - set(made)
    assert not missing, f'not drawn: {sorted(missing)}'
    for s, w, h in srcs:
        rel = s.replace(SLUG + '/', '', 1)
        assert f'viewBox="0 0 {w} {h}"' in made[rel].read_text(), f'wrong viewBox for {rel}'
    print(f'wrote {len(made)} files to {OUT} ({len(wanted)} required); extra: {sorted(set(made) - wanted)}')
