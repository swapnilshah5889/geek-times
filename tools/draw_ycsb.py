"""Draws the media for "Benchmarking Cloud Serving Systems with YCSB" (Cooper et al., SoCC 2010).

Run from the repo root:  python3 tools/draw_ycsb.py
Writes standalone SVGs to backups/media/ycsb/{lead,story,comic,facts}/. Every media.src in
data/seed/papers/ycsb.json must be written. No logos or brand art; the four stores are plain word-buddies.
Real numbers drawn here come from the JSON and carry a "From the paper" stamp.
"""
import json
import math
import re
from pathlib import Path

from media_kit import COMIC_CSS, COMIC_DEFS, INK, RED, anim, bubble, buddy, standalone, t, write

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'backups' / 'media' / 'ycsb'
SEED = ROOT / 'data' / 'seed' / 'papers' / 'ycsb.json'

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
STORES = [('Cass', ORANGE), ('HBase', GREEN), ('PNUTS', PURPLE), ('MySQL', SAND)]

EXTRA_CSS = ('.grow{transform-box:fill-box;transform-origin:center bottom;animation:gr 5s ease-out infinite}'
             '@keyframes gr{0%{transform:scaleY(.05)}40%,100%{transform:none}}'
             '.hand{transform-origin:center;transform-box:fill-box;animation:hd 3s ease-in-out infinite}'
             '@keyframes hd{0%{transform:rotate(-90deg)}60%,100%{transform:none}}'
             '.slide{animation:sl 3s ease-in-out infinite alternate}@keyframes sl{to{transform:translateY(26px)}}')
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


def svg(vb, body, title):
    return standalone(vb, body, title, css=prune_css(COMIC_CSS + EXTRA_CSS, body), defs=DEFS if 'ah)' in body else COMIC_DEFS)


# ---------- shared pieces ----------

def bg(w, h, color):
    return f'<rect width="{w}" height="{h}" fill="{color}"/><rect width="{w}" height="{h}" fill="url(#dots)" opacity=".22"/>'


def stamp(x, y, text='From the paper · measured', anchor='start'):
    return t(x, y, text, 'micro', anchor, f'fill:{RED}')


def person(x, y, hair='#6a4a3a', shirt=BLUE, s=1, cap=False):
    g = (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round">'
         f'<path d="M-16 50V22Q-16 12 0 12Q16 12 16 22V50Z" fill="{shirt}"/><path d="M-6 50V66M6 50V66" fill="none"/>'
         f'<circle r="13" fill="#f0c9a0"/>')
    if cap:
        g += f'<path d="M-13 -2Q-12 -16 0 -16Q12 -16 13 -2Z" fill="{RED}"/><path d="M5 -3h14" stroke-width="3" fill="none"/>'
    else:
        g += f'<path d="M-13 -2Q-14 -15 0 -15Q14 -15 13 -2Q4 -8 -13 -2Z" fill="{hair}"/>'
    g += (f'<circle cx="-4" cy="1" r="1.6" fill="{INK}" stroke="none"/><circle cx="4" cy="1" r="1.6" fill="{INK}" stroke="none"/>'
          f'<path d="M-4 6q4 3 8 0" fill="none" stroke-width="2"/></g>')
    return g


def qmark(x, y, s=1, cls='m-bob'):
    return f'<g{anim(cls)}><text x="{x}" y="{y}" class="sfx" text-anchor="middle" style="font-size:{int(34 * s)}px">?</text></g>'


def storefront(x, y, color, sign, w=62, h=70, awn=RED):
    """Shop front with a striped awning and a simple sign shape (no brand art). (x,y) = bottom centre."""
    l, top = x - w / 2, y - h
    g = (f'<g stroke="{INK}" stroke-width="2.5" stroke-linejoin="round">'
         f'<rect x="{l}" y="{top}" width="{w}" height="{h}" fill="{color}"/>'
         f'<rect x="{x - 11}" y="{y - 32}" width="22" height="32" fill="{PAPER}"/>'
         f'<rect x="{l + 5}" y="{top + 24}" width="{w / 2 - 20:g}" height="16" fill="#e8f3f0"/>'
         f'<path d="M{l - 4} {top + 4}h{w + 8}l-5 -14h{-w + 2}Z" fill="{awn}"/>'
         f'<path d="M{l + 9} {top - 10}v14M{l + 26} {top - 10}v14M{l + 43} {top - 10}v14" stroke="{PAPER}" stroke-width="3"/>'
         f'<g transform="translate({x} {top - 24})">{sign}</g></g>')
    return g


SIGNS = [f'<circle r="8" fill="{GOLD}"/>', f'<path d="M0 -9L9 7H-9Z" fill="{GREEN}"/>',
         f'<rect x="-8" y="-8" width="16" height="16" fill="{PURPLE}"/>', f'<path d="M0 -9L2.5 -3 9 -3 4 1 6 8 0 4 -6 8 -4 1 -9 -3 -2.5 -3Z" fill="{ORANGE}"/>']


def pie(cx, cy, r, fracs, colors):
    out, a0 = '', -90.0
    for f, c in zip(fracs, colors):
        a1 = a0 + 360 * f
        if f >= .999:
            out += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" stroke="{INK}" stroke-width="2.5"/>'
        else:
            p = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in (a0, a1)]
            out += (f'<path d="M{cx} {cy}L{p[0][0]:.1f} {p[0][1]:.1f}A{r} {r} 0 {1 if f > .5 else 0} 1 {p[1][0]:.1f} {p[1][1]:.1f}Z" '
                    f'fill="{c}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>')
        a0 = a1
    return out


def clock(x, y, r=22, frac=.25, color=RED, cls=''):
    a = math.radians(-90 + 360 * frac)
    hx, hy = x + (r - 6) * math.cos(a), y + (r - 6) * math.sin(a)
    hand = f'<path d="M{x} {y}L{hx:.1f} {hy:.1f}" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
    return (f'<rect x="{x - 4}" y="{y - r - 8}" width="8" height="7" fill="{GREY}" stroke="{INK}" stroke-width="2"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{PAPER}" stroke="{INK}" stroke-width="3"/>'
            f'<path d="M{x} {y}L{x} {y - r + 5}A{r - 5} {r - 5} 0 {1 if frac > .5 else 0} 1 {x + (r - 5) * math.sin(2 * math.pi * frac):.1f} {y - (r - 5) * math.cos(2 * math.pi * frac):.1f}Z" fill="{color}" opacity=".55"/>'
            + hand + f'<circle cx="{x}" cy="{y}" r="3" fill="{INK}"/>')


def clipboard(x, y, w=86, h=100, ticks=4, big=False):
    g = (f'<g stroke="{INK}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round">'
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{WOOD}"/>'
         f'<rect x="{x + 6}" y="{y + 12}" width="{w - 12}" height="{h - 18}" fill="{PAPER}" stroke-width="2"/>'
         f'<rect x="{x + w / 2 - 14}" y="{y - 4}" width="28" height="14" rx="3" fill="{GREY}"/>')
    gap = (h - 34) / max(ticks, 1)
    for i in range(ticks):
        yy = y + 28 + i * gap
        g += (f'<path d="M{x + 12} {yy:.0f}l4 4 7 -8" stroke="{RED}" stroke-width="2.5" fill="none"/>'
              f'<path d="M{x + 30} {yy:.0f}h{w - 44}" stroke-width="2" opacity=".5" fill="none"/>')
    return g + '</g>'


def finger(x, y, rot=0, s=1):
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round">'
            f'<rect x="-5" y="-4" width="10" height="26" rx="5" fill="#f0c9a0"/><rect x="-14" y="-24" width="28" height="22" rx="9" fill="#f0c9a0"/>'
            f'<path d="M-6 -10v6M0 -10v6M6 -10v6" stroke-width="1.5" fill="none"/></g>')


def card_list(x, y, n=4, w=60, h=16, gap=4, colors=None):
    g = ''
    for i in range(n):
        c = (colors or [PAPER, SAND, GREEN, PURPLE])[i % 4]
        g += f'<rect x="{x}" y="{y + i * (h + gap)}" width="{w}" height="{h}" rx="3" fill="{c}" stroke="{INK}" stroke-width="2"/>'
        g += f'<path d="M{x + 6} {y + i * (h + gap) + h / 2:g}h{w - 24}" stroke="{INK}" stroke-width="1.5" opacity=".5"/>'
    return g


def bars(x0, base, w, gap, vals, vmax, hmax, colors, names=None, labels=None, short=None, ncls='b-s'):
    """Vertical bars. vals can be None for an unlabeled very short bar (height `short`)."""
    g = ''
    for i, v in enumerate(vals):
        x = x0 + i * (w + gap)
        h = short if v is None else hmax * v / vmax
        g += (f'<rect x="{x}" y="{base - h:.1f}" width="{w}" height="{h:.1f}" fill="{colors[i]}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>')
        if labels and labels[i]:
            g += t(x + w / 2, f'{base - h - 6:.1f}', labels[i], 'micro')
        if names:
            g += t(x + w / 2, base + 17, names[i], ncls)
    return g + f'<path d="M{x0 - 8} {base}H{x0 + len(vals) * (w + gap) - gap + 8}" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'


def box_machine(x, y, color, s=1, word=''):
    return buddy(x, y, word, color, s, label_cls='w-s')


def eye(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round">'
            f'<path d="M-16 0Q0 -16 16 0Q0 16 -16 0Z" fill="{PAPER}"/><circle r="6" fill="{TEAL}"/><circle r="2.5" fill="{INK}"/></g>')


def pencil(x, y, rot=-40, s=1):
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})" stroke="{INK}" stroke-width="2" stroke-linejoin="round">'
            f'<rect x="0" y="-5" width="34" height="10" fill="{ORANGE}"/><path d="M0 -5L-12 0L0 5Z" fill="{SAND}"/>'
            f'<rect x="34" y="-5" width="7" height="10" fill="#d98b8b"/></g>')


def arrow(d, flow=True, w=3.5):
    fl = ' stroke-dasharray="8 7" class="m-flow"' if flow else ''
    return f'<path d="{d}" fill="none" stroke="{RED}" stroke-width="{w}" stroke-linecap="round"{fl} marker-end="url(#ah)"/>'


def crate(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2" stroke-linejoin="round">'
            f'<rect x="-10" y="-9" width="20" height="18" fill="{WOOD}"/><path d="M-10 -9L10 9M10 -9L-10 9" opacity=".5"/></g>')


# ---------- registry ----------
PANELS = []


def add(rel, vb, title, body):
    PANELS.append((rel, vb, title, body))


def comic(name, title, color, body):
    add(f'comic/{name}.svg', '0 0 320 220', title, bg(320, 220, color) + body)


def story(name, title, color, body):
    add(f'story/{name}.svg', '0 0 440 215', title, bg(440, 215, color) + body)


def icon(name, title, body, color='#f0e3c6'):
    add(f'facts/{name}.svg', '0 0 160 100', title, bg(160, 100, color) + body)


def plate(name, title, color, tag, body, caption):
    add(f'lead/{name}.svg', '0 0 600 340', title,
        bg(600, 340, color) + body
        + f'<rect x="10" y="288" width="580" height="44" fill="{CREAM}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
        + t(300, 317, caption, 'b') + t(22, 28, tag, 'micro', 'start', f'fill:{RED}')
        + f'<path d="M8 10Q300 5 592 9Q596 170 591 332Q300 336 9 331Q4 170 8 10Z" fill="none" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>')


# =====================================================================
# Lead plates (600 x 340)
# =====================================================================
b = ''
for i, (cx, (nm, col)) in enumerate(zip([85, 215, 385, 515], STORES)):
    b += storefront(cx, 225, col, SIGNS[i], 96, 100)
    b += t(cx, 255, nm, 'w-s')
b += person(300, 175, shirt=GREEN, s=1.1) + qmark(300, 160, 1.4) + qmark(340, 195, 1)
b += f'<path d="M20 268H580" stroke="{INK}" stroke-width="3" stroke-dasharray="10 7"/>'
plate('many-stores', 'Four different shops in a row and a shopper who cannot choose', '#d8ead9', 'WHICH ONE?', b,
      'Every store is built differently. Which one fits my job?')

b = ''
for i, (nm, col) in enumerate(STORES):
    lx = 150 + i * 80
    b += f'<rect x="{lx}" y="70" width="80" height="190" fill="{["#f0e3c6", PAPER][i % 2]}" stroke="{INK}" stroke-width="2.5"/>'
    b += box_machine(lx + 40, 215, col, 1, nm)
b += f'<path d="M150 232H470" stroke="{RED}" stroke-width="5"/>'
b += (f'<path d="M110 270V70" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'
      f'<g class="m-wobble"><path d="M110 74h70v34h-70Z" fill="{RED}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
      f'<path d="M122 74v34M146 74v34M170 74v34" stroke="{PAPER}" stroke-width="6" opacity=".7"/></g>')
b += clock(530, 160, 36, .22, RED) + t(530, 222, 'same timer', 'b-s')
b += t(310, 62, 'GO!', 'sfx')
plate('same-race', 'Four runners on the same track under one starting flag', '#e9e1c8', 'SAME RACE!', b,
      'One test, one track, one stopwatch for every store.')

# =====================================================================
# Story panels (440 x 215)
# =====================================================================
b = person(50, 100, shirt=GREEN, s=1.2) + qmark(50, 82, 1.4)
for i, (nm, col) in enumerate(STORES):
    b += storefront(140 + i * 82, 175, col, SIGNS[i], 66, 78)
b += f'<path d="M10 190H430" stroke="{INK}" stroke-width="3" stroke-dasharray="10 7"/>'
story('01-many-stores', 'A shopper in front of four different stores', '#d8ead9', b)

b = clipboard(18, 45, 96, 124, 4)
for i, (nm, col) in enumerate(STORES):
    x = 190 + i * 75
    b += box_machine(x, 105, col, .9, nm)
    b += arrow(f'M118 107C150 107 150 {105 + (i - 1.5) * 4:.0f} {x - 42} 105', True, 3)
b += t(66, 190, 'same chores', 'b-s') + t(300, 178, 'one test, four stores', 'b')
story('02-one-test', 'One clipboard feeding the same chores to four machines', '#e9e1c8', b)

b = f'<rect x="30" y="122" width="380" height="12" fill="{WOOD}" stroke="{INK}" stroke-width="3"/>'
b += f'<rect x="60" y="176" width="240" height="14" rx="4" fill="{GREY}" stroke="{INK}" stroke-width="3"/>'
for i, (nm, col) in enumerate(STORES):
    x = 75 + i * 70
    b += box_machine(x, 80, col, .85, nm)
    b += f'<path d="M{x} 134V176" stroke="{INK}" stroke-width="3"/><circle cx="{x}" cy="176" r="5" fill="{INK}"/>'
b += person(370, 100, shirt=BLUE, s=.9, cap=True)
b += f'<g class="m-wobble"><path d="M335 125L316 100" stroke="{INK}" stroke-width="5" stroke-linecap="round"/><circle cx="314" cy="97" r="5" fill="{GREY}" stroke="{INK}" stroke-width="2"/></g>'
b += t(180, 206, 'same shelf, same power', 'b-s')
story('03-same-track', 'Four identical machines on one shelf and one power strip', '#d8ead9', b)

vals = [11978, 7904, 7448, 7283]
b = stamp(14, 18)
b += bars(14, 170, 38, 10, vals, 11978, 110, [ORANGE, GREEN, PURPLE, SAND], ['Cass', 'HBase', 'PNUTS', 'MySQL'], ['11978', '7904', '7448', '7283'], ncls='micro')
b += t(107, 204, 'update-heavy test', 'b-s')
v2 = [1519, 1440, None]
b += bars(250, 170, 44, 14, v2, 1519, 110, [GREEN, PURPLE, ORANGE], ['HBase', 'PNUTS', 'Cass'], ['1519', '1440', 'much worse'], short=8, ncls='micro')
b += t(342, 204, 'range scans', 'b-s')
b += f'<path d="M222 40V175" stroke="{INK}" stroke-width="2" stroke-dasharray="4 6"/>' + t(222, 30, 'two tests, not to scale', 'micro')
story('04-results', 'Two bar groups: Cassandra tallest in updates, shortest in scans', '#e9e1c8', b)

# =====================================================================
# Comic panels (320 x 220)
# =====================================================================
b = ''
for i, (nm, col) in enumerate(STORES):
    b += storefront(46 + i * 76, 160, col, SIGNS[i], 62, 84, awn=[RED, TEAL, '#b9603a', '#5d6aa1'][i])
b += f'<path d="M8 172H312" stroke="{INK}" stroke-width="3" stroke-dasharray="10 7"/>' + t(160, 202, 'each built a bit differently', 'b-s')
comic('01a-many-stores', 'A row of different storefronts', '#d8ead9', b)

b = person(48, 75, shirt=GREEN, s=1.1) + qmark(48, 60, 1.2)
for i, (w, col) in enumerate(zip([50, 80, 122, 150], [ORANGE, GREEN, PURPLE, SAND])):
    y = 40 + i * 36
    b += (f'<g stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"><rect x="92" y="{y}" width="{w}" height="14" fill="#fff8e3"/>'
          + ''.join(f'<path d="M{92 + k * 12} {y}v{6 if k % 2 else 9}" fill="none" stroke-width="1.8"/>' for k in range(1, w // 12 + 1))
          + f'<rect x="258" y="{y - 8}" width="34" height="30" rx="3" fill="{col}"/></g>')
b += t(160, 202, 'four rulers, no fair answer', 'b-s')
comic('01b-no-ruler', 'A shopper holding four rulers of different lengths', '#ece3cb', b)

b = clipboard(115, 14, 90, 78, 3)
b += f'<path d="M160 10v-6" stroke="{INK}" stroke-width="3"/>'
for i, (nm, col) in enumerate(STORES):
    x = 42 + i * 79
    b += box_machine(x, 145, col, .85, nm) + arrow(f'M160 94Q{x} 100 {x} 112', False, 2.5)
b += t(160, 205, 'one test for all four', 'b-s')
comic('01c-one-test', 'One clipboard checklist in front of four boxes', '#d8ead9', b)

b = f'<rect x="15" y="72" width="290" height="70" rx="8" fill="{PAPER}" stroke="{INK}" stroke-width="3"/>'
for i in range(10):
    b += f'<rect x="{25 + i * 28}" y="86" width="23" height="42" rx="3" fill="{[SAND, GREEN][i % 2]}" stroke="{INK}" stroke-width="2"/>'
b += t(160, 58, 'one record = 10 fields', 'w-s') + t(160, 172, '100 bytes each, about 1,000 in all', 'b-s')
b += stamp(10, 210, 'From the paper · setup')
comic('02a-record', 'A long record card with ten small boxes', '#e9e1c8', b)

b = ''
labs = [('INSERT', lambda x: f'<path d="M{x - 12} 82h24M{x} 70v24" stroke="{RED}" stroke-width="6" stroke-linecap="round"/>'),
        ('UPDATE', lambda x: pencil(x - 14, 90, -40, .8)),
        ('READ', lambda x: eye(x, 82, 1.1)),
        ('SCAN', lambda x: card_list(x - 14, 64, 3, 28, 9, 4) + finger(x + 10, 100, 180, .55))]
for i, (lab, fn) in enumerate(labs):
    x = 44 + i * 77
    b += f'<rect x="{x - 33}" y="48" width="66" height="76" rx="8" fill="{PAPER}" stroke="{INK}" stroke-width="2.5"/>' + fn(x) + t(x, 148, lab, 'micro')
b += t(160, 190, 'four kinds of work', 'b')
comic('02b-four-chores', 'Four icons: insert, update, read, scan', '#d8ead9', b)

hs = [118, 98, 80, 40, 34, 30, 26, 22, 20, 18, 16, 14]
b = ''
for i, h in enumerate(hs):
    x = 18 + i * 24
    b += f'<rect x="{x}" y="{180 - h}" width="20" height="{h}" rx="3" fill="{GOLD if i < 3 else SAND}" stroke="{INK}" stroke-width="2.5"/>'
    if i < 3:
        b += f'<path d="M{x + 10} {180 - h - 6}l0 -8M{x + 2} {180 - h - 4}l-5 -5M{x + 18} {180 - h - 4}l5 -5" stroke="{RED}" stroke-width="2.5" stroke-linecap="round"/>'
b += f'<path d="M12 180H308" stroke="{INK}" stroke-width="3"/>' + t(160, 205, 'a few records get most requests', 'b-s')
b += t(215, 80, 'most records: quiet', 'b-s')
comic('02c-popular', 'A line of cards where the first few are tall and glowing', '#ece3cb', b)

b = pie(100, 105, 62, [.5, .5], [GREEN, ORANGE]) + t(100, 190, 'A: 50 / 50', 'w-s')
b += t(100, 56, 'read', 'b-s', style='fill:#27251e') if False else ''
b += f'<rect x="196" y="62" width="14" height="14" fill="{GREEN}" stroke="{INK}" stroke-width="2"/>' + t(218, 75, 'reads', 'b-s', 'start')
b += f'<rect x="196" y="90" width="14" height="14" fill="{ORANGE}" stroke="{INK}" stroke-width="2"/>' + t(218, 103, 'updates', 'b-s', 'start')
b += clock(250, 160, 22, .3, TEAL) + t(250, 205, 'session store', 'micro') + stamp(10, 212, 'From the paper · setup')
comic('03a-mix-a', 'A pie split half and half next to a small clock', '#d8ead9', b)

b = ''
b += pie(55, 95, 40, [.95, .05], [GREEN, ORANGE]) + t(55, 160, 'B: 95 / 5', 'b-s')
b += pie(160, 95, 40, [1.0], [GREEN]) + t(160, 160, 'C: reads only', 'b-s')
b += pie(265, 95, 40, [1.0], [GREEN]) + t(265, 160, 'D: newest', 'b-s')
b += f'<g class="m-twinkle"><use href="#mstar" transform="translate(290 62) scale(2)"/></g>' + t(265, 95, 'new', 'w-s')
b += t(55, 38, 'photo tags', 'micro') + stamp(10, 205, 'From the paper · setup')
comic('03b-mix-bcd', 'Three pies: mostly reads, all reads, newest records', '#ece3cb', b)

b = card_list(60, 36, 6, 150, 18, 6, [PAPER, SAND, GREEN, PURPLE, SAND, PAPER])
b += f'<g class="slide">{finger(215, 55, 180, 1.3)}</g>'
b += f'<path d="M50 36V172M44 36h8M44 172h8" stroke="{RED}" stroke-width="3" fill="none" stroke-linecap="round"/>'
b += t(236, 150, 'one thread', 'w-s') + t(236, 172, 'E: scan a run', 'b-s', style='') + t(160, 207, 'a few inserts too', 'b-s')
comic('03c-mix-e', 'A finger sliding down a short stack of cards labelled as one thread', '#d8ead9', b)

b = ''
for i in range(6):
    x, y = 45 + (i % 3) * 62, 62 + (i // 3) * 74
    b += box_machine(x, y, BLUE, .75)
b += (f'<g stroke="{INK}" stroke-width="2.5">' + ''.join(f'<rect x="235" y="{152 - k * 18}" width="62" height="16" rx="3" fill="{[SAND, GREEN, PURPLE][k % 3]}"/>' for k in range(8)) + '</g>')
b += t(266, 30, 'tall stack', 'b-s') + t(110, 200, '6 machines', 'w-s') + t(266, 178, '120 M records', 'micro') + t(266, 193, '120 GB', 'micro')
b += stamp(10, 214, 'From the paper · setup')
comic('04a-six-machines', 'Six identical machines and a tall stack of cards', '#e9e1c8', b)

b = box_machine(110, 130, ORANGE, 1.5)
b += (f'<circle cx="110" cy="52" r="16" fill="{PAPER}" stroke="{INK}" stroke-width="3"/><g class="m-wobble"><path d="M110 52v-12" stroke="{RED}" stroke-width="4" stroke-linecap="round"/></g>'
      '<path d="M110 80v-12" stroke="#27251e" stroke-width="3"/>')
b += person(205, 85, shirt=BLUE, s=.9, cap=True) + f'<path d="M190 95L132 60" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
b += person(272, 90, hair='#3a2a20', shirt=GREEN, s=.8)
b += t(160, 200, 'tuned with the stores\' own helpers', 'b-s')
comic('04b-tuning', 'A helper in a cap turns a dial on a machine', '#d8ead9', b)

b = f'<rect x="90" y="14" width="140" height="48" rx="6" fill="{PAPER}" stroke="{INK}" stroke-width="3"/><path d="M90 30h140" stroke="{INK}" stroke-width="3"/><path d="M110 14v-7M210 14v-7" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'
b += t(160, 54, '2010', 'w')
for i, (nm, col) in enumerate(STORES):
    x = 42 + i * 79
    b += box_machine(x, 125, col, .85, nm)
    ver = ['0.5.0', '0.20.3', '', '5.1'][i]
    if ver:
        b += (f'<g transform="translate({x} 175)"><rect x="-27" y="-11" width="54" height="22" rx="4" fill="{GOLD}" stroke="{INK}" stroke-width="2"/>'
              + t(0, 5, ver, 'micro') + '</g>')
b += t(160, 211, 'versions change; results can too', 'b-s')
comic('04c-versions', 'A calendar page and four boxes with version tags', '#ece3cb', b)

vals = [11978, 7904, 7283, 7448]
b = stamp(10, 16) + bars(26, 178, 52, 20, vals, 11978, 120, [ORANGE, GREEN, SAND, PURPLE], ['Cass', 'HBase', 'MySQL', 'PNUTS'], ['11978', '7904', '7283', '7448'])
b += t(160, 211, 'operations a second, workload A', 'micro')
comic('05a-top-bar', 'Four bars with the first clearly tallest', '#d8ead9', b)

b = f'<g transform="translate(95 100)">' + (f'<rect x="-50" y="-70" width="100" height="140" rx="5" fill="{PAPER}" stroke="{INK}" stroke-width="3"/>'
    f'<path d="M-50 -70v140" stroke="{RED}" stroke-width="4"/>' + ''.join(f'<path d="M-36 {-52 + i * 16}h74" stroke="{INK}" stroke-width="2" opacity=".5"/>' for i in range(7))
    + f'<path d="M-36 60h40" stroke="{INK}" stroke-width="2.5"/>') + '</g>'
b += f'<g class="m-bob">{pencil(100, 178, -30, .9)}</g>'
b += (f'<g stroke="{INK}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"><rect x="236" y="150" width="56" height="22" rx="4" fill="{GREY}"/>'
      f'<path d="M264 150L250 108L212 92" fill="none" stroke-width="6"/><path d="M212 92l-8 12M212 92l-14 4" fill="none"/></g>')
b += t(150, 36, 'one long line', 'w-s') + t(264, 195, 'disk head waits', 'b-s') + t(160, 213, 'writes go at the end', 'micro')
comic('05b-notebook', 'A pencil adds lines to a long notebook while a robot arm waits', '#e9e1c8', b)

b = clock(80, 85, 38, .12, GREEN) + clock(240, 85, 38, .55, RED)
b += f'<rect x="56" y="138" width="48" height="32" rx="4" fill="{PAPER}" stroke="{INK}" stroke-width="2.5"/><path d="M62 150h30M62 158h20" stroke="{INK}" stroke-width="2" opacity=".5"/>'
for k in range(4):
    b += f'<rect x="{208 + k * 9}" y="{140 + (k % 2) * 5}" width="44" height="28" rx="3" fill="{PAPER}" stroke="{INK}" stroke-width="2" transform="rotate({k * 6 - 9} 230 155)"/>'
b += t(80, 195, 'PNUTS, MySQL', 'b-s') + t(240, 195, 'Cass, HBase', 'b-s') + t(160, 18, 'workload B: reads', 'micro')
comic('05c-reads-slower', 'Two stopwatches, a fast one beside a card and a slower one beside loose pages', '#ece3cb', b)

b = stamp(10, 16) + bars(24, 170, 40, 12, [1519, 1440, None], 1519, 110, [GREEN, PURPLE, ORANGE], ['HBase', 'PNUTS', 'Cass'], ['1519', '1440', ''], short=8)
b += t(60, 200, '', 'b-s')
b += card_list(228, 60, 5, 66, 16, 4) + f'<g class="slide">{finger(260, 52, 180, 1.1)}</g>'
b += t(88, 128, 'much worse', 'w-s', style='fill:#a13324') if False else t(100, 207, 'Cass: much worse', 'micro')
b += t(260, 200, 'workload E', 'micro')
comic('06a-scans', 'Two tall bars and one very short bar beside a finger sliding down a list', '#d8ead9', b)

b = (f'<g stroke="{INK}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round">'
     f'<path d="M62 150L88 70" stroke-width="9" fill="none"/><rect x="62" y="48" width="48" height="26" rx="5" fill="#dfe9ea" transform="rotate(-6 86 60)"/>'
     f'<path d="M232 160L238 82" stroke-width="12" fill="none" stroke="#7a5a3a"/><rect x="204" y="52" width="62" height="34" rx="5" fill="#a9a396" transform="rotate(-3 235 70)"/>'
     f'<path d="M214 60l6 10M240 56l5 12" stroke-width="2" fill="none"/></g>')
b += f'<path d="M88 100q4 -8 22 -4" stroke="{INK}" stroke-width="2" fill="none"/><use href="#mstar" transform="translate(116 52) scale(1.3)"/>'
b += (f'<g class="m-wobble"><path d="M60 118h-16" stroke="{INK}" stroke-width="2"/><g transform="translate(28 126)"><path d="M0 -14h46l8 14-8 14h-46Z" fill="{GOLD}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
      + t(26, 5, 'new 0.5.0', 'micro') + '</g></g>')
b += t(235, 130, 'worn and tuned', 'b-s') + t(160, 205, 'scans: new, not yet polished', 'b-s')
comic('06b-new-feature', 'A small new tool with a price tag beside a worn one', '#e9e1c8', b)

b = ''
pos = [(36, 60), (96, 60), (156, 60), (66, 130), (126, 130)]
for (x, y) in pos:
    b += box_machine(x, y, BLUE, .6) + arrow(f'M{x + 20} {y} Q{(x + 255) / 2:.0f} {y + (95 - y) / 2 - 15:.0f} 232 {80 + (y - 60) * .5:.0f}', True, 2.5)
b += box_machine(262, 105, GREEN, .9) + f'<use href="#mstar" transform="translate(300 70) scale(1.4)"/>'
b += crate(190, 78, .8) + crate(185, 118, .8) + clock(222, 38, 22, .5, RED) + t(262, 175, 'new machine', 'b-s')
b += t(262, 74 if False else 22, '', 'micro') + t(105, 190, 'heavy data moves', 'b-s')
b += f'<rect x="212" y="26" width="0" height="0"/>' + t(272, 44, '5.5 h', 'w-s', 'middle') + stamp(10, 212)
comic('06c-moving-boxes', 'Five machines pass heavy boxes to a sixth new machine while a clock shows a long wait', '#ece3cb', b)

# =====================================================================
# Fact icons (160 x 100)
# =====================================================================
b = bars(18, 84, 28, 10, [1, .68, .62, .6], 1, 62, [ORANGE, GREEN, SAND, PURPLE])
b += f'<use href="#mstar" transform="translate(32 14) scale(1.6)"/>'
icon('peak-throughput', 'One tall bar and three shorter bars', b)

b = f'<path d="M30 78A50 50 0 0 1 130 78" fill="{PAPER}" stroke="{INK}" stroke-width="3"/><path d="M30 78A50 50 0 0 1 48 40" fill="none" stroke="{RED}" stroke-width="8"/>'
b += f'<path d="M80 78L40 66" stroke="{INK}" stroke-width="4" stroke-linecap="round"/><circle cx="80" cy="78" r="6" fill="{INK}"/>'
b += card_list(110, 50, 3, 34, 9, 4) + finger(127, 90, 180, .5) + t(80, 96, 'scans', 'micro')
icon('scans', 'A gauge pointing to very slow beside a list', b)

b = clock(60, 54, 30, .62, RED) + box_machine(125, 44, GREEN, .5)
b += f'<path d="M110 76h30M125 64v24" stroke="{RED}" stroke-width="5" stroke-linecap="round"/>'
icon('elastic-hours', 'A clock with a long sweep beside a machine being added', b)

b = ''
for i in range(6):
    b += box_machine(26 + (i % 3) * 38, 28 + (i // 3) * 42, BLUE, .42)
b += ''.join(f'<rect x="108" y="{78 - k * 14}" width="40" height="12" rx="2" fill="{[SAND, GREEN, PURPLE][k % 3]}" stroke="{INK}" stroke-width="2"/>' for k in range(5))
icon('setup', 'Six small machines and a tall stack of data cards', b)

b = ''
for i, n in enumerate([2, 4, 6]):
    for k in range(n):
        b += f'<rect x="{12 + i * 52 + (k % 2) * 16}" y="{70 - (k // 2) * 14}" width="13" height="11" rx="2" fill="{BLUE}" stroke="{INK}" stroke-width="2"/>'
b += f'<path d="M14 24H146" stroke="{RED}" stroke-width="4" stroke-linecap="round" stroke-dasharray="9 6"/>' + t(80, 16, 'flat', 'micro')
b += f'<path d="M12 86H148" stroke="{INK}" stroke-width="3"/>'
icon('scaleup', 'A row of machines growing in number under a flat line', b)

b = pie(52, 50, 30, [.95, .05], [GREEN, ORANGE]) + eye(114, 40, 1.2) + f'<path d="M96 70h36" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>' + t(114, 90, 'reads', 'micro')
icon('read-heavy', 'A pie that is almost all reads beside an eye', b)


# =====================================================================
# Write everything and check it against the story
# =====================================================================
def story_srcs(doc):
    found = []

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get('src'), str) and o['src'].startswith('ycsb/'):
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
    wanted = {s for s, _, _ in srcs}
    made = {}
    for rel, vb, title, body in PANELS:
        made[rel] = write(OUT, rel, svg(vb, body, title))
    missing = {w.replace('ycsb/', '', 1) for w in wanted} - set(made)
    assert not missing, f'not drawn: {sorted(missing)}'
    for s, w, h in srcs:
        rel = s.replace('ycsb/', '', 1)
        assert f'viewBox="0 0 {w} {h}"' in made[rel].read_text(), f'wrong viewBox for {rel}'
    extra = set(made) - {w.replace('ycsb/', '', 1) for w in wanted}
    print(f'wrote {len(made)} files to {OUT} ({len(wanted)} required in the story); extra: {sorted(extra)}')
