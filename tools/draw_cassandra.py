"""Draws the media for "Cassandra: A Decentralized Structured Storage System" (Facebook Inbox Search, 2009).

Run from the repo root:  python3 tools/draw_cassandra.py
Writes standalone SVGs to backups/media/cassandra/{lead,story,comic,facts}/ (Git recovery copies; the live
copies are served from Supabase Storage). Every media.src in data/seed/papers/cassandra.json must be written.
"""
import json
import math
import re
from pathlib import Path

from media_kit import COMIC_CSS, COMIC_DEFS, INK, RED, anim, bubble, buddy, standalone, t, write

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'backups' / 'media' / 'cassandra'
SEED = ROOT / 'data' / 'seed' / 'papers' / 'cassandra.json'

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

EXTRA_CSS = ('.needle{transform-box:view-box;animation:nd 5s ease-out infinite}'
             '@keyframes nd{0%{transform:rotate(-55deg)}60%,100%{transform:rotate(0)}}'
             '.slide{animation:sl 5s ease-in-out infinite}@keyframes sl{0%{transform:translateX(-26px)}40%,100%{transform:none}}')
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


# ---------- shared drawing pieces ----------

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


def ring_pts(cx, cy, rx, ry, n, start=-90):
    return [(cx + rx * math.cos(math.radians(start + 360 * i / n)), cy + ry * math.sin(math.radians(start + 360 * i / n))) for i in range(n)]


def ring(cx, cy, rx, ry, w=3):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{INK}" stroke-width="{w}" stroke-dasharray="10 7"/>'


def envelope(x, y, rot=0, s=1, fill=PAPER):
    return (f'<g transform="translate({x:.0f} {y:.0f}) rotate({rot}) scale({s})" stroke="{INK}" stroke-width="2" stroke-linejoin="round">'
            f'<rect x="-13" y="-9" width="26" height="18" rx="2" fill="{fill}"/><path d="M-13 -9L0 2L13 -9" fill="none"/></g>')


def notebook(x, y, s=1, lines=3, open_line=False):
    g = (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round">'
         f'<rect x="-32" y="-42" width="64" height="84" rx="4" fill="{PAPER}"/><path d="M-32 -42v84" stroke="{RED}" stroke-width="3"/>')
    for i in range(lines):
        g += f'<path d="M-22 {-28 + i * 14}h42" stroke-width="1.8" opacity=".55" fill="none"/>'
    return g + '</g>'


def board(x, y, w=110, h=76, notes=3, blank=False):
    g = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="#fbfaf0" stroke="{INK}" stroke-width="3"/>'
         f'<path d="M{x + 14} {y + h + 12}L{x + 20} {y + h}M{x + w - 14} {y + h + 12}L{x + w - 20} {y + h}" stroke="{INK}" stroke-width="3"/>')
    if blank:
        g += f'<path d="M{x + 18} {y + 24}q22 -10 46 0t30 12M{x + 22} {y + 52}q24 -8 50 2" fill="none" stroke="#d8cfb8" stroke-width="5" stroke-linecap="round"/>'
    else:
        for i in range(notes):
            nx = x + 10 + (i % 3) * (w - 20) / 3; ny = y + 10 + (i // 3) * 30
            g += (f'<rect x="{nx:.0f}" y="{ny:.0f}" width="{(w - 30) / 3:.0f}" height="24" fill="{[SAND, GREEN, PURPLE][i % 3]}" stroke="{INK}" stroke-width="1.8"/>'
                  f'<path d="M{nx + 5:.0f} {ny + 9:.0f}h{(w - 30) / 3 - 10:.0f}M{nx + 5:.0f} {ny + 16:.0f}h14" stroke="{INK}" stroke-width="1.5" opacity=".6"/>')
    return g


def folder(x, y, w=54, h=40, color=SAND, rot=0, label=''):
    g = (f'<g transform="translate({x:.0f} {y:.0f}) rotate({rot})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round">'
         f'<path d="M{-w / 2} {-h / 2 + 6}V{-h / 2}Q{-w / 2} {-h / 2 - 4} {-w / 2 + 4} {-h / 2 - 4}H{-w / 2 + 18}L{-w / 2 + 24} {-h / 2 + 2}H{w / 2}V{-h / 2 + 6}Z" fill="{color}" opacity=".85"/>'
         f'<rect x="{-w / 2}" y="{-h / 2 + 5}" width="{w}" height="{h - 5}" rx="3" fill="{color}"/>'
         f'<path d="M{-w / 2 + 8} {h / 2 - 12}h{w * .5:.0f}" stroke-width="1.8" opacity=".5" fill="none"/>')
    if label:
        g += t(0, 6, label, 'micro', style='stroke:none')
    return g + '</g>'


def pencil(x, y, rot=-40, cls=''):
    g = (f'<g transform="translate({x} {y}) rotate({rot})" stroke="{INK}" stroke-width="2" stroke-linejoin="round">'
         f'<rect x="0" y="-5" width="34" height="10" fill="{ORANGE}"/><path d="M0 -5L-12 0L0 5Z" fill="{SAND}"/><path d="M-12 0l-3 0" stroke-width="3"/>'
         f'<rect x="34" y="-5" width="7" height="10" fill="#d98b8b"/></g>')
    return f'<g{anim(cls)}>{g}</g>' if cls else g


def arrow(d, flow=True, w=3.5):
    return f'<path d="{d}" fill="none" stroke="{RED}" stroke-width="{w}" stroke-linecap="round" {"stroke-dasharray=" + chr(34) + "8 7" + chr(34) if flow else ""} marker-end="url(#ah)"{" class=" + chr(34) + "m-flow" + chr(34) if flow else ""}/>'


def magnifier(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="4" stroke-linecap="round">'
            f'<circle r="26" fill="#e8f3f0" fill-opacity=".45"/><path d="M19 19L46 46" stroke-width="8"/></g>')


def building(x, y, s=1, windows=True):
    g = (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round">'
         f'<rect x="-36" y="-34" width="72" height="68" rx="3" fill="#cfd8d3"/>')
    for i in range(3 if windows else 0):
        for j in range(2):
            g += f'<rect x="{-26 + j * 36}" y="{-26 + i * 14}" width="12" height="8" fill="#f7e9b5" stroke-width="1.5"/>'
    return g + '</g>'


def cabinet(x, y, drawers, w=96, h=34, opened=None, offset=0):
    g = ''
    for i, lab in enumerate(drawers):
        yy = y + i * (h + 4)
        dx = offset if i == opened else 0
        g += (f'<rect x="{x - w / 2 + dx}" y="{yy}" width="{w}" height="{h}" rx="4" fill="{GREY}" stroke="{INK}" stroke-width="3"/>')
        g += lab(x + dx, yy + h / 2) if callable(lab) else t(x + dx, yy + h / 2 + 6, lab, 'w-s')
    return g


def panel_bg(bg, body, w=320, h=220):
    return f'<rect width="{w}" height="{h}" fill="{bg}"/><rect width="{w}" height="{h}" fill="url(#dots)" opacity=".22"/>{body}'


def face(x, y, hair, skin='#f0c9a0', r=11):
    return (f'<g transform="translate({x} {y})" stroke="{INK}" stroke-width="2"><circle r="{r}" fill="{skin}"/>'
            f'<path d="M{-r} -1Q{-r} {-r - 3} 0 {-r - 2}Q{r} {-r - 3} {r} -1Q4 -6 {-r} -1Z" fill="{hair}"/>'
            f'<circle cx="-4" cy="1" r="1.3" fill="{INK}" stroke="none"/><circle cx="4" cy="1" r="1.3" fill="{INK}" stroke="none"/>'
            f'<path d="M-4 5q4 3 8 0" fill="none"/></g>')


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


PANELS = []   # (relative path, viewBox, title, body)


def comic(name, title, bg, body):
    PANELS.append((f'comic/{name}.svg', '0 0 320 220', title, panel_bg(bg, body)))


def story(name, title, bg, body):
    PANELS.append((f'story/{name}.svg', '0 0 440 215', title, panel_bg(bg, body, 440, 215)))


def icon(name, title, body, bg='#f0e3c6'):
    PANELS.append((f'facts/{name}.svg', '0 0 160 100', title, panel_bg(bg, body, 160, 100)))


def plate(name, title, bg, tag, body, caption):
    PANELS.append((f'lead/{name}.svg', '0 0 600 340', title,
                   panel_bg(bg, body, 600, 340)
                   + f'<rect x="10" y="288" width="580" height="44" fill="{CREAM}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
                   + t(300, 317, caption, 'b') + t(22, 28, tag, 'micro', 'start', f'fill:{RED}')
                   + f'<path d="M8 10Q300 5 592 9Q596 170 591 332Q300 336 9 331Q4 170 8 10Z" fill="none" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>'))


# =====================================================================
# Lead plates
# =====================================================================
def cabinet_big(x, y, burst=True):
    g = f'<rect x="{x}" y="{y}" width="100" height="150" rx="6" fill="{GREY}" stroke="{INK}" stroke-width="3.5"/>'
    for i in range(3):
        yy = y + 10 + i * 46
        g += (f'<rect x="{x + 10}" y="{yy}" width="80" height="38" rx="3" fill="#8e8672" stroke="{INK}" stroke-width="2.5"/>'
              f'<rect x="{x + 38}" y="{yy + 14}" width="24" height="7" rx="2" fill="{INK}"/>')
        if burst:
            g += f'<g transform="translate({x + 18 + i * 28} {yy - 6}) rotate({-15 + i * 14})" stroke="{INK}" stroke-width="2"><rect x="-9" y="-6" width="18" height="12" fill="{PAPER}"/></g>'
    if burst:
        g += f'<path d="M{x + 50} {y}L{x + 42} {y + 30}L{x + 56} {y + 52}L{x + 44} {y + 80}" fill="none" stroke="{RED}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
    return g


flood_body = ''
for i in range(18):
    row, col = i % 3, i // 3
    flood_body += envelope(40 + col * 55 + (row % 2) * 20, 70 + row * 62 + (col % 2) * 14, -18 + (i * 37) % 36, 1.15, [PAPER, SAND, GREEN][i % 3])
flood_body += (f'<path d="M20 100Q200 60 380 140M20 160Q200 140 380 170M20 215Q200 230 380 190" fill="none" stroke="{TEAL}" stroke-width="3" stroke-dasharray="9 8" opacity=".6" class="m-flow"/>'
               + cabinet_big(430, 100)
               + f'<g{anim("m-shake")}>' + t(480, 82, 'CREAK!', 'sfx-s') + '</g>'
               + buddy(558, 232, 'help', ORANGE, .85))
plate('flood', 'A flood of envelopes pours toward one small filing cabinet that is about to burst.', '#efd5b7',
      'PLATE 01 / FLOOD', flood_body, 'One cabinet cannot catch billions of messages.')

cx, cy = 300, 142
ring_body = ring(cx, cy, 175, 85)
pts = ring_pts(cx, cy, 175, 85, 6, -90)
for i, (x, y) in enumerate(pts):
    ex, ey = (x, y - 34) if i == 0 else (x + (46 if x > cx + 5 else -46), y)
    ring_body += desk(x, y, 1.25, ['#d9b98a', '#c9d9c8', '#c3b2d8', '#f7d79b', '#efae78', '#a2c2a7'][i])
    ring_body += envelope(ex, ey, -10 + i * 8, .9, PAPER)
ring_body += t(cx, cy + 6, 'A RING OF', 'w-s') + t(cx, cy + 26, 'ORDINARY DESKS', 'w-s')
ring_body += f'<g{anim("m-wiggle")}>' + t(cx, 272, 'JOT JOT JOT', 'sfx-s') + '</g>'
plate('ring-of-desks', 'Six calm desks sit around a ring. Each catches some envelopes and writes them in a notebook.', '#b8cec0',
      'PLATE 02 / RING', ring_body, 'Six desks share the flood. Each one jots in its notebook.')

# =====================================================================
# Story panels
# =====================================================================
body = t(220, 16, 'MANY PHONES', 'micro', style=f'fill:{RED}')
for i in range(5):
    x = 51 + i * 84
    body += (f'<rect x="{x - 14}" y="26" width="28" height="48" rx="6" fill="{TEAL}" stroke="{INK}" stroke-width="2.5"/>'
             f'<rect x="{x - 10}" y="32" width="20" height="30" fill="{PAPER}"/><circle cx="{x}" cy="68" r="2" fill="{INK}"/>')
    body += (f'<path d="M{x} 84V138" stroke="{TEAL}" stroke-width="3" stroke-dasharray="8 7" class="m-flow" fill="none"/>'
             + envelope(x + 18, 98 + (i % 2) * 12, 12, .8) + envelope(x - 18, 112 - (i % 2) * 10, -10, .8, SAND))
for i in range(5):
    x = 20 + i * 84
    body += (f'<rect x="{x}" y="150" width="62" height="52" rx="5" fill="{GREY}" stroke="{INK}" stroke-width="3"/>'
             f'<rect x="{x + 8}" y="158" width="46" height="12" rx="2" fill="#8e8672" stroke="{INK}" stroke-width="1.5"/>'
             f'<circle cx="{x + 16}" cy="184" r="4" fill="{RED if i == 3 else GREEN}" stroke="{INK}" stroke-width="1.5"/>')
body += f'<path d="M{20 + 3 * 84 + 30} 150L{20 + 3 * 84 + 22} 172L{20 + 3 * 84 + 36} 186L{20 + 3 * 84 + 28} 202" fill="none" stroke="{RED}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
body += f'<g{anim("m-shake")}>' + t(370, 142, 'CRACK!', 'sfx-s') + '</g>'
body_m = ''
story('01-flood', 'Envelopes stream from many phones toward a row of machines; one machine has a crack.', '#efd5b7', body)

# 02 two ideas
rc = (95, 105)
b = ring(rc[0], rc[1], 62, 48, 2.5)
for k, (x, y) in enumerate(ring_pts(rc[0], rc[1], 62, 48, 5, -90)):
    b += (f'<g transform="translate({x:.0f} {y:.0f})" stroke="{INK}" stroke-width="2" stroke-linejoin="round"><rect x="-11" y="-5" width="22" height="16" fill="{SAND}"/>'
          f'<path d="M-14 -4L0 -17L14 -4Z" fill="{RED}"/></g>')
b += t(95, 188, 'RING OF HOUSES', 'micro') + t(160, 112, '+', 'w', style='font-size:34px') 
tx = 190
b += f'<rect x="{tx}" y="62" width="90" height="82" fill="{PAPER}" stroke="{INK}" stroke-width="3"/>'
for r in range(4):
    for c in range(3):
        b += f'<rect x="{tx + 4 + c * 28}" y="{66 + r * 19}" width="26" height="16" fill="{[GREEN, SAND, PURPLE][c]}" stroke="{INK}" stroke-width="1.5"/>'
b += t(235, 188, 'TIDY TABLE OF ROWS', 'micro')
b += t(300, 112, '=', 'w', style='font-size:34px')
b += (f'<rect x="322" y="68" width="92" height="76" rx="6" fill="{GREY}" stroke="{INK}" stroke-width="3.5"/>'
      f'<circle cx="368" cy="106" r="22" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="6 5"/>'
      f'<rect x="355" y="100" width="26" height="14" fill="{SAND}" stroke="{INK}" stroke-width="2"/><path d="M352 101L368 90L384 101Z" fill="{RED}" stroke="{INK}" stroke-width="2"/>'
      + t(368, 188, 'CASSANDRA', 'micro', style=f'fill:{RED}'))
story('02-two-ideas', 'A ring of houses on the left and a tidy table of rows on the right join together into one machine.', '#b8cec0', b)

# 03 jot then sort
b = envelope(40, 100, -8, 1.5)
b += arrow('M66 100H112')
b += notebook(150, 100, .85, 4) + t(150, 168, 'NOTEBOOK', 'micro') + t(150, 186, 'jot first', 'b-s')
b += arrow('M190 100H222')
b += board(236, 66, 84, 60, 3) + t(278, 168, 'WHITEBOARD', 'micro') + t(278, 186, 'then in memory', 'b-s')
b += arrow('M334 100H356')
for i in range(3):
    b += folder(388 + (i - 1) * 6, 78 + i * 22, 56, 36, [SAND, GREEN, PURPLE][i])
b += t(390, 168, 'SORTED FILES', 'micro') + t(390, 186, 'finally', 'b-s')
story('03-jot-then-sort', 'An envelope goes into a notebook, then onto a whiteboard, then into a neat stack of sorted files.', '#f0e3c6', b)

# 04 measured numbers (from the paper)
x0, sc = 178, 5.0          # ms -> px
b = t(18, 22, 'FROM THE PAPER · MEASURED', 'micro', 'start', f'fill:{RED}')
rows = [('Search Interactions', 15.69, 7.69, 26.13, TEAL, 62), ('Term Search', 18.27, 7.78, 44.41, ORANGE, 132)]
b += f'<path d="M{x0} 46V186" stroke="{INK}" stroke-width="2"/>'
for v in range(0, 51, 10):
    b += f'<path d="M{x0 + v * sc:.0f} 46V186" stroke="{INK}" stroke-width="1" opacity=".22"/>' + t(x0 + v * sc, 204, str(v), 'micro')
for name, med, lo, hi, col, y in rows:
    b += t(14, y + 5, name, 'w-s', 'start')
    b += t(14, y + 23, f'median {med} ms', 'micro', 'start', 'font-size:12px')
    b += (f'<rect x="{x0}" y="{y - 12}" width="{med * sc:.1f}" height="24" fill="{col}" stroke="{INK}" stroke-width="2.5"/>'
          f'<path d="M{x0 + lo * sc:.1f} {y + 30}H{x0 + hi * sc:.1f}M{x0 + lo * sc:.1f} {y + 24}v12M{x0 + hi * sc:.1f} {y + 24}v12" stroke="{RED}" stroke-width="3" stroke-linecap="round" fill="none"/>'
          + t(x0 + lo * sc, y + 48, f'min {lo}', 'micro') + t(x0 + hi * sc + (8 if hi > 40 else 0), y + 48, f'max {hi}', 'micro', 'end' if hi > 40 else 'middle'))
b += t(14, 204, 'milliseconds', 'micro', 'start')
story('04-search-speed', 'Two bars show the median search time, 15.69 and 18.27 milliseconds, with min and max marks. From the paper, measured.', '#f6f0df', b)

# =====================================================================
# Comic panels
# =====================================================================
C = (160, 128)
pts6 = ring_pts(C[0], C[1], 112, 58, 6, -60)
ringbase = ring(*C, 112, 58)


def six(badge=None, hl=None):
    return ''.join(desk(x, y, .9, badge=(i == badge)) for i, (x, y) in enumerate(pts6))


spot = (C[0] + 112 * math.cos(math.radians(-100)), C[1] + 58 * math.sin(math.radians(-100)))
spot_mark = f'<circle cx="{spot[0]:.0f}" cy="{spot[1]:.0f}" r="7" fill="{RED}" stroke="{INK}" stroke-width="2"/>'

tag = (f'<g transform="translate({spot[0]:.0f} 30)" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"><path d="M-26 -12H18L30 0L18 12H-26Z" fill="{SAND}"/>'
       f'<circle cx="20" cy="0" r="3" fill="{PAPER}"/></g>' + t(spot[0] - 4, 36, 'KEY', 'mono-s'))
comic('01a-key-to-spot', 'A key tag drops onto a spot on a ring of desks.', '#f0e3c6',
      ringbase + six() + f'<g{anim("m-bob")}>{tag}</g>'
      + f'<path d="M{spot[0]:.0f} 52V{spot[1] - 12:.0f}" stroke="{RED}" stroke-width="3" stroke-dasharray="6 6" marker-end="url(#ah)" fill="none"/>'
      + spot_mark + t(245, 40, 'a spot on', 'b-s') + t(245, 58, 'the circle', 'b-s'))

pt = pts6[0]
comic('01b-walk-clockwise', 'An arrow walks clockwise from the spot to the nearest desk, which wears a small badge.', '#f0e3c6',
      ringbase + six(badge=0) + spot_mark
      + arrow(f'M{spot[0] + 8:.0f} {spot[1] + 2:.0f}Q{pt[0] - 10:.0f} {pt[1] - 40:.0f} {pt[0] - 6:.0f} {pt[1] - 22:.0f}')
      + t(255, 196, 'CLOCKWISE', 'micro', style=f'fill:{RED}') + t(70, 42, 'first desk', 'b-s') + t(70, 60, 'wears a badge', 'b-s'))

bx = 224
b = building(pts6[1][0], pts6[1][1] + 12, 1.05, False) + ringbase + six(badge=0)
b += t(272, 214, 'FAR AWAY', 'micro')
b += arrow(f'M{pts6[0][0] + 24:.0f} {pts6[0][1] + 4:.0f}Q{pts6[0][0] + 50:.0f} {pts6[0][1] + 6:.0f} {pts6[1][0] - 10:.0f} {pts6[1][1] - 26:.0f}')
b += arrow(f'M{pts6[0][0] - 14:.0f} {pts6[0][1] + 14:.0f}Q{pts6[0][0] - 50:.0f} {pts6[0][1] + 70:.0f} {pts6[2][0] - 20:.0f} {pts6[2][1] - 10:.0f}')
b += t(60, 40, 'copies', 'w') + t(60, 60, 'to neighbors', 'b-s')
comic('01c-copies', 'The badge desk passes copies to two neighbors; one neighbor sits in a building far away.', '#f0e3c6', b)

# 02 notebook / whiteboard / flush
note = f'<rect width="46" height="26" fill="{SAND}" stroke="{INK}" stroke-width="2"/><path d="M6 10h34M6 18h18" stroke="{INK}" stroke-width="2" opacity=".6"/>'
b = notebook(110, 112, 1.45, 6)
b += f'<path d="M80 184h60" stroke="{INK}" stroke-width="2" stroke-dasharray="3 4" opacity=".7"/><path d="M82 168h56" stroke="{RED}" stroke-width="3" stroke-linecap="round" class="m-flow"/>'
b += pencil(172, 168, -36, 'm-bob') + t(250, 100, 'NEW LINE', 'micro', style=f'fill:{RED}') + t(250, 120, 'at the end', 'b-s') + t(250, 138, 'of the notebook', 'b-s')
comic('02a-notebook', 'A pencil adds a line at the bottom of a long notebook.', '#e8e2cc', b)

b = notebook(60, 120, .95, 4) + board(120, 52, 176, 110, 3) + arrow('M92 112H114', False)
b += f'<g transform="translate(212 84) rotate(-4)">{note}</g>' + t(208, 36, 'WHITEBOARD (MEMORY)', 'micro') + t(60, 190, 'NOTEBOOK', 'micro') + t(208, 200, 'same note, easy to find', 'b-s')
comic('02b-whiteboard', 'The same note is pinned to a whiteboard next to the notebook.', '#e8e2cc', b)

b = board(26, 50, 120, 84, blank=True) + t(86, 36, 'NOW BLANK', 'micro')
b += arrow('M150 92H206') + folder(246, 92, 80, 62, GREEN) + f'<path d="M222 96h48M222 110h48M222 124h48" stroke="{INK}" stroke-width="2" opacity=".45"/>'
b += f'<g{anim("m-wiggle")}>' + t(196, 40, 'FLUSH!', 'sfx-s') + '</g>' + t(246, 150, 'SORTED FOLDER', 'micro') + t(160, 196, 'never changed after this', 'b-s')
comic('02c-flush', 'The whiteboard pours its notes into a neat folder; the board is now blank.', '#e8e2cc', b)

# 03 read path
b = board(60, 62, 200, 100, 3).replace('<rect x="60"', '<rect x="60"', 1)
b += f'<g{anim("m-scan")}>' + magnifier(98, 100, 1) + '</g>' + t(160, 36, 'CHECK THE BOARD FIRST', 'micro') + t(160, 200, 'newest notes live here', 'b-s')
comic('03a-check-board', 'A magnifying glass looks over the whiteboard.', '#f0e3c6', b)

b = ''
for i in range(5):
    b += folder(48 + i * 56, 96 + (i % 2) * 6, 50, 62, [SAND, GREEN, PURPLE, ORANGE, '#a9c4d4'][i], rot=-6 + i * 3)
b += t(48, 150, 'NEWEST', 'micro', style=f'fill:{RED}') + buddy(160, 178, 'ugh', SAND, .8) + t(260, 190, 'so many!', 'b-s')
b += f'<path d="M190 150q4 8 0 12" stroke="{TEAL}" stroke-width="3" fill="none" stroke-linecap="round"/>'
comic('03b-many-files', 'A row of folders, newest at the front, with a tired word buddy in front of them.', '#f0e3c6', b)

b = folder(95, 100, 88, 72, SAND) + folder(250, 100, 88, 72, GREEN)
b += buddy(95, 150, 'door', PURPLE, .8, 'm-bob') + f'<path d="M72 126l-12 -22" stroke="{INK}" stroke-width="2" stroke-linecap="round"/><circle cx="58" cy="100" r="6" fill="#f0c9a0" stroke="{INK}" stroke-width="2"/>'
b += bubble(14, 8, 100, 34, ['Not here!'], (84, 60), 'b-s') + arrow('M126 78Q172 50 214 76') + t(170, 40, 'skip', 'w-s') + t(160, 206, 'a tiny doorman per folder', 'b-s')
comic('03c-doorman', 'A small doorman in front of a folder holds up a hand; the search skips to the next folder.', '#f0e3c6', b)

# 04 compaction
b = ''
for i, (x, y, r) in enumerate([(70, 130, -20), (120, 150, 12), (170, 124, -6), (224, 152, 22), (96, 100, 14), (200, 96, -14), (150, 176, 4), (260, 120, 8)]):
    b += folder(x, y, 52, 36, [SAND, GREEN, PURPLE, ORANGE][i % 4], r)
b += t(160, 36, 'LOTS OF SMALL FILES', 'micro', style=f'fill:{RED}') + t(160, 206, 'a messy pile', 'b-s')
comic('04a-pile', 'A messy pile of small folders.', '#e8e2cc', b)

b = folder(100, 100, 86, 66, SAND) + folder(220, 100, 86, 66, SAND)
b += f'<path d="M160 52V152" stroke="{INK}" stroke-width="3" stroke-dasharray="3 4"/>'
b += f'<g{anim("m-bob")}><rect x="152" y="46" width="16" height="22" rx="4" fill="{GOLD}" stroke="{INK}" stroke-width="2.5"/></g>'
b += f'<g{anim("m-pulse")}>' + t(160, 190, 'ZIP!', 'sfx') + '</g>' + t(160, 28, 'two similar folders', 'b-s')
comic('04b-merge', 'Two similar folders zip together into one bigger folder.', '#e8e2cc', b)

b = folder(130, 116, 150, 110, GREEN) + f'<path d="M90 100h80M90 120h80M90 140h80" stroke="{INK}" stroke-width="2.5" opacity=".4"/>'
b += (f'<g transform="translate(248 130) rotate(18)" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"><path d="M0 -60V10" stroke-width="5" stroke-linecap="round"/>'
      f'<path d="M-18 10H18L24 44H-24Z" fill="{ORANGE}"/><path d="M-8 14L-10 44M0 14V44M8 14L10 44" stroke-width="1.5"/></g>')
b += t(130, 206, 'one big, tidy file', 'b-s') + f'<g{anim("m-twinkle")}><use href="#mstar" x="50" y="50"/></g>'
comic('04c-tidy', 'One big neat folder stands where the pile was, with a broom beside it.', '#e8e2cc', b)

# 05 failure detector
pts5 = ring_pts(160, 112, 112, 56, 6, -90)
b = ring(160, 112, 112, 56) + ''.join(desk(x, y, .85) for x, y in pts5)
for i in range(6):
    a, c = pts5[i], pts5[(i + 1) % 6]
    b += f'<path d="M{(a[0] + c[0]) / 2 - 10:.0f} {(a[1] + c[1]) / 2 - 6 + (6 if i in (2, 3, 4) else 0):.0f}h20" stroke="{RED}" stroke-width="3" stroke-dasharray="6 5" class="m-flow" fill="none"/>'
b += envelope(160, 112, 0, .8, SAND) + t(160, 196, 'gossip around the ring', 'b-s') + t(160, 28, 'who is awake?', 'w-s')
comic('05a-gossip', 'Desks pass small notes to each other around the ring.', '#f0e3c6', b)

b = desk(46, 160, 1.2) + buddy(46, 112, 'me', GREEN, .6) + desk(274, 160, 1.2, dark=True) + t(274, 130, 'z z z', 'mono-s') + t(274, 205, 'silent', 'b-s')
b += meter(160, 160, 62, -35) + t(160, 190, 'WORRY METER', 'micro') + t(160, 40, 'quiet for a while...', 'b-s')
b += f'<path d="M70 150Q110 120 160 110" fill="none" stroke="{INK}" stroke-width="2" stroke-dasharray="4 5" opacity="0"/>'
comic('05b-worry-meter', 'A desk watches a silent neighbor while a meter needle slowly rises.', '#f0e3c6', b)

b = desk(46, 160, 1.2) + desk(274, 160, 1.2, dark=True)
b += f'<g transform="translate(274 132)" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"><path d="M-14 0Q-12 -22 6 -22L20 -2Z" fill="{RED}"/><circle cx="22" cy="-3" r="4" fill="{PAPER}"/></g>'
b += t(262, 205, 'marked down', 'b-s') + meter(160, 160, 62, 55) + t(160, 190, 'PAST THE RED LINE', 'micro', style=f'fill:{RED}') + t(160, 40, 'too worried!', 'w-s')
comic('05c-threshold', 'The meter needle passes a red line and the silent desk is marked with a sleeping cap.', '#f0e3c6', b)

# 06 inbox index
def lab(word):
    return lambda x, y: t(x, y + 6, word, 'w-s')


def cards(x, y):
    return ''.join(f'<rect x="{x + i * 20 - 30}" y="{y - 12 + (i % 2) * 4}" width="18" height="24" fill="{[SAND, GREEN, PURPLE][i]}" stroke="{INK}" stroke-width="1.8" transform="rotate({-8 + i * 8} {x + i * 20 - 21} {y})"/>' for i in range(3))


b = (cabinet(110, 46, [lab('movie'), lab('trip'), lab('pizza')], 140, 40, opened=2, offset=24)
     + cards(250, 144)
     + t(160, 30, 'ROW = YOUR USER ID', 'micro', style=f'fill:{RED}') + t(160, 210, 'under a word: message ids', 'b-s'))
comic('06a-word-drawers', 'A cabinet with drawers labelled with words; the pizza drawer holds message cards.', '#e8e2cc', b)

b = ''
for i, (h, s) in enumerate([('#5a3a28', '#f0c9a0'), ('#a13324', '#e0b088'), ('#27251e', '#f0c9a0')]):
    yy = 50 + i * 44
    b += f'<rect x="60" y="{yy}" width="170" height="40" rx="4" fill="{GREY}" stroke="{INK}" stroke-width="3"/>' + face(100, yy + 20, h, s) + envelope(180, yy + 20, 0, .8, SAND)
b += t(160, 30, 'SECOND FAMILY: PEOPLE', 'micro', style=f'fill:{RED}') + t(160, 208, 'under a friend: your messages', 'b-s')
comic('06b-people-drawers', 'A second cabinet with drawers labelled with friends faces.', '#e8e2cc', b)

b = (f'<rect x="30" y="20" width="170" height="34" rx="17" fill="{PAPER}" stroke="{INK}" stroke-width="3"/><circle cx="52" cy="37" r="7" fill="none" stroke="{INK}" stroke-width="2.5"/>'
     f'<path d="M57 42l6 6" stroke="{INK}" stroke-width="2.5"/>'
     f'<g transform="translate(212 40)" stroke="{INK}" stroke-width="2" stroke-linejoin="round"><path d="M0 0L0 22L6 17L10 26L14 24L10 16L18 16Z" fill="{PAPER}"/></g>')
b += f'<g{anim("slide")}>' + cabinet(150, 84, [lab('pizza'), lab('movie'), lab('trip')], 150, 34, opened=None) + '</g>'
b += f'<g{anim("m-pulse")}>' + t(260, 90, 'READY!', 'sfx-s') + '</g>' + t(160, 212, 'warmed up while you type', 'b-s')
comic('06c-warm-up', 'A cursor clicks a search box while a cabinet slides its drawers forward, ready.', '#e8e2cc', b)

# =====================================================================
# Fact icons (decorative)
# =====================================================================
def stack(x, y, n=3, w=60):
    g = ''
    for i in range(n):
        yy = y + i * 18
        g += (f'<path d="M{x - w / 2} {yy}v14a{w / 2} 6 0 0 0 {w} 0v-14" fill="{[GREY, '#a9c4d4', GREY][i % 3]}" stroke="{INK}" stroke-width="2.5"/>'
              f'<ellipse cx="{x}" cy="{yy}" rx="{w / 2}" ry="6" fill="#d8cfb8" stroke="{INK}" stroke-width="2.5"/>')
    return g


icon('terabytes', 'A stack of disks standing for terabytes of data.', stack(80, 28, 3, 64) + f'<circle cx="104" cy="66" r="2.5" fill="{GREEN}"/><circle cx="96" cy="66" r="2.5" fill="{RED}"/>')
icon('search-ms', 'A stopwatch for a very quick search.',
     f'<circle cx="80" cy="56" r="30" fill="{PAPER}" stroke="{INK}" stroke-width="3.5"/><rect x="72" y="14" width="16" height="8" rx="2" fill="{GREY}" stroke="{INK}" stroke-width="2.5"/>'
     f'<path d="M80 56V38" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/><path d="M80 56L94 62" stroke="{RED}" stroke-width="3.5" stroke-linecap="round"/><circle cx="80" cy="56" r="3.5" fill="{INK}"/>'
     f'<path d="M24 46h18M20 58h20M26 70h14" stroke="{TEAL}" stroke-width="3.5" stroke-linecap="round"/>')
icon('detect-15s', 'A worry meter needle crossing a red line.', meter(80, 74, 50, 40).replace('class="needle" ', '') + f'<g{anim("m-twinkle")}><use href="#mstar" x="132" y="26"/></g>')
icon('seven-tb', 'A big crate of data moving from an old database into a ring.',
     stack(34, 30, 2, 40) + arrow('M60 48H92').replace(' class="m-flow"', '') + ring(122, 50, 28, 22, 2.5) + ''.join(
         f'<rect x="{x - 4:.0f}" y="{y - 3:.0f}" width="9" height="7" fill="{SAND}" stroke="{INK}" stroke-width="1.5"/>' for x, y in ring_pts(122, 50, 28, 22, 5, -90)))
icon('handover', 'One desk hands a folder to a new desk joining the ring.',
     desk(36, 58, 1.1) + desk(124, 58, 1.1, top=GREEN) + folder(80, 28, 30, 22, SAND) + arrow('M56 80Q80 92 104 80', False))
icon('notebook-128mb', 'A notebook whose page is nearly full.',
     notebook(80, 50, .95, 5).replace('<g transform', '<g transform', 1) + pencil(110, 78, -36) + f'<path d="M62 70h30" stroke="{RED}" stroke-width="2.5" stroke-linecap="round"/>')

# =====================================================================
# Write everything and check it against the story
# =====================================================================
def story_srcs(doc):
    found = []

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get('src'), str) and o['src'].startswith('cassandra/'):
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
        made[rel] = write(OUT, rel.replace('cassandra/', '', 1), svg(vb, body, title))
    missing = {w.replace('cassandra/', '', 1) for w in wanted} - set(made)
    assert not missing, f'not drawn: {sorted(missing)}'
    for s, w, h in srcs:
        rel = s.replace('cassandra/', '', 1)
        assert f'viewBox="0 0 {w} {h}"' in made[rel].read_text(), f'wrong viewBox for {rel}'
    extra = set(made) - {w.replace('cassandra/', '', 1) for w in wanted}
    print(f'wrote {len(made)} files to {OUT} ({len(wanted)} required in the story); extra: {sorted(extra)}')
