"""Draws the media for "How Discord Stores Trillions of Messages" (Discord blog, 2023-03-06).

Run from the repo root:  python3 tools/draw_discord_trillions.py
Writes standalone SVGs to backups/media/discord-trillions/{lead,story,comic,facts}/ (Git recovery copies).
Every media.src in data/seed/papers/discord-trillions.json must be written. Real numbers drawn here are the
ones in the JSON, stamped "From the source / reported". Everything else is illustration without numbers.
"""
import json
import math
import re
from pathlib import Path

from media_kit import COMIC_CSS, COMIC_DEFS, INK, RED, anim, standalone, t, write

ROOT = Path(__file__).resolve().parent.parent
SLUG = 'discord-trillions'
OUT = ROOT / 'backups' / 'media' / SLUG
SEED = ROOT / 'data' / 'seed' / 'papers' / f'{SLUG}.json'

CREAM, TEAL, GREEN, GOLD, WOOD = '#fbf3dc', '#377675', '#a2c2a7', '#ffe597', '#d9b98a'
PAPER, PURPLE, SAND, ORANGE, GREY, BLUE = '#fff8e3', '#c3b2d8', '#f7d79b', '#efae78', '#b5ab92', '#82acad'
FCOL = [SAND, GREEN, PURPLE, ORANGE, BLUE]
DEFS = COMIC_DEFS + (f'<marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
                     f'<path d="M0 0L10 5L0 10Z" fill="{RED}"/></marker>')
SRC_STAMP = ('From the source', 'reported')


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


def squeeze(body):
    """Shrink repeated stroke attributes into classes and round long decimals."""
    used = set()

    def rep(m):
        w = m.group(1).replace('.', '')
        used.add((w, m.group(1)))
        return f'class="k{w}"'
    body = re.sub(r'stroke="#322e24" stroke-width="([\d.]+)" stroke-linejoin="round" stroke-linecap="round"', rep, body)
    body = re.sub(r'(\d+\.\d)\d+', r'\1', body)
    css = ''.join(f'.k{w}{{stroke:#322e24;stroke-width:{v};stroke-linejoin:round;stroke-linecap:round}}' for w, v in sorted(used))
    return body, css


def svg(vb, body, title):
    body, extra = squeeze(body)
    return standalone(vb, body, title, css=prune_css(COMIC_CSS, body) + extra, defs=DEFS if 'ah)' in body else COMIC_DEFS)


# ---------- pieces ----------
def S(w=2.5):
    return f'stroke="{INK}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'


def desk(x, y, s=1, top=WOOD):
    return (f'<g transform="translate({x:.0f} {y:.0f}) scale({s})" {S()}><path d="M-18 6v15M18 6v15" fill="none" stroke-width="3"/>'
            f'<rect x="-25" y="-6" width="50" height="13" rx="3" fill="{top}"/></g>')


def folder(x, y, w=40, h=14, color=SAND, rot=0):
    return (f'<g transform="translate({x:.0f} {y:.0f}) rotate({rot})" {S(2)}><rect x="{-w / 2}" y="{-h / 2}" width="{w}" height="{h}" rx="2" fill="{color}"/>'
            f'<path d="M{-w / 2 + 3} {-h / 2 - 3}h{w * .35:.0f}" fill="none"/></g>')


def pile(x, y, n, w=38, h=11, wob=3):
    """n folders stacked upward, base at y."""
    return ''.join(folder(x + (wob if i % 2 else -wob) * (1 if i % 3 else .3), y - h / 2 - i * (h - 1), w, h, FCOL[i % 5]) for i in range(n))


def face(x, y, hair='#5a3d2b', r=11, mood='smile', skin='#f0c9a0'):
    mouth = {'smile': 'M-4 5q4 3 8 0', 'flat': 'M-4 6h8', 'sad': 'M-4 7q4 -3 8 0', 'o': 'M-2 6q2 -2 4 0q-2 2 -4 0'}[mood]
    return (f'<g transform="translate({x:.0f} {y:.0f})" {S(2)}><circle r="{r}" fill="{skin}"/>'
            f'<path d="M{-r} -1Q{-r} {-r - 3} 0 {-r - 2}Q{r} {-r - 3} {r} -1Q4 -6 {-r} -1Z" fill="{hair}"/>'
            f'<circle cx="-4" cy="1" r="1.3" fill="{INK}" stroke="none"/><circle cx="4" cy="1" r="1.3" fill="{INK}" stroke="none"/><path d="{mouth}" fill="none"/></g>')


HAIR = ['#5a3d2b', '#27251e', '#b06a2c', '#7a4a3a', '#8a8a8a']
SHIRT = [TEAL, '#b9603a', '#5d6aa1', '#8a5a9a', '#4f7a66']


def person(x, y, i=0, s=1, mood='smile'):
    """Small person: head at (x,y), body below."""
    return (f'<g transform="translate({x:.0f} {y:.0f}) scale({s})"><rect x="-9" y="10" width="18" height="17" rx="6" fill="{SHIRT[i % 5]}" {S(2)}/></g>'
            + face(x, y, HAIR[i % 5], 11 * s, mood))


def crowd(x, y, n, dx=24, mood='smile', s=1):
    return ''.join(person(x + i * dx, y, i, s, mood) for i in range(n))


def worker(x, y, mood='smile', color=ORANGE, s=1, cls=''):
    """Word-buddy style worker, centred at x,y."""
    g = (f'<g transform="translate({x} {y}) scale({s})"><use href="#wb" style="color:{color}"/>'
         f'<circle cx="-7" cy="-14" r="2" fill="{INK}" stroke="none"/></g>')
    return f'<g{anim(cls)}>{g}</g>' if cls else g


def drop(x, y):
    return f'<path d="M{x} {y}q-5 8 0 10q5 -2 0 -10Z" fill="#a8d4e6" {S(1.5)}/>'


def lamp(x, y, on=True):
    g = f'<path d="M{x - 8} {y + 8}v-7q0-10 8-10t8 10v7Z" fill="{RED if on else GREY}" {S(2)}/>'
    if on:
        g += f'<path d="M{x - 14} {y - 8}l-6 -5M{x + 14} {y - 8}l6 -5M{x} {y - 14}v-7" stroke="{RED}" stroke-width="2.5" stroke-linecap="round"/>'
    return f'<g{anim("m-pulse")}>{g}</g>' if on else g


def pager(x, y):
    return (f'<g transform="translate({x} {y})"><rect x="-11" y="-8" width="22" height="16" rx="3" fill="{INK}"/>'
            f'<rect x="-8" y="-5" width="16" height="6" fill="{GREEN}"/></g><path d="M{x + 14} {y - 10}q6 4 0 10M{x + 19} {y - 14}q10 8 0 18" fill="none" stroke="{RED}" stroke-width="2.5" stroke-linecap="round"/>')


def clock(x, y, r=14, a=60):
    h = math.radians(a)
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{PAPER}" {S()}/><path d="M{x} {y}v{-r * .65:.0f}M{x} {y}l{r * .5 * math.sin(h):.0f} {-r * .5 * math.cos(h):.0f}" {S(2)} fill="none"/>')


def shelf(x, y, w=80, h=70, rows=3, full=True, color=GREY):
    g = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#8e8672" {S(3)}/>'
    rh = h / rows
    for i in range(rows):
        g += f'<path d="M{x} {y + (i + 1) * rh - 1:.0f}h{w}" {S(2.5)}/>'
        if full:
            g += ''.join(f'<rect x="{x + 6 + j * (w - 12) / 4:.0f}" y="{y + i * rh + 5:.0f}" width="{(w - 12) / 4 - 3:.0f}" height="{rh - 8:.0f}" fill="{FCOL[(i + j) % 5]}" {S(1.5)}/>' for j in range(4))
    return g


def cabinet(x, y, w=90, h=120, drawers=3, open_i=None, label=''):
    g = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{GREY}" {S(3)}/>'
    dh = (h - 12) / drawers
    for i in range(drawers):
        yy = y + 6 + i * dh
        off = 14 if i == open_i else 0
        g += (f'<rect x="{x + 8 + off}" y="{yy:.0f}" width="{w - 16}" height="{dh - 5:.0f}" rx="3" fill="#8e8672" {S(2.5)}/>'
              f'<rect x="{x + w / 2 - 9 + off}" y="{yy + dh / 2 - 6:.0f}" width="18" height="6" rx="2" fill="{PAPER}" {S(1.5)}/>')
    return g


def truck(x, y, s=1, boxes=3, cls=''):
    g = (f'<g transform="translate({x} {y}) scale({s})" {S()}><rect x="-34" y="-26" width="52" height="34" rx="3" fill="{PAPER}"/>'
         f'<path d="M18 -14h14l9 12v10H18Z" fill="{TEAL}"/><circle cx="-18" cy="10" r="7" fill="{INK}"/><circle cx="28" cy="10" r="7" fill="{INK}"/>'
         + ''.join(f'<rect x="{-30 + i * 16}" y="-22" width="13" height="13" fill="{FCOL[i % 5]}" stroke-width="1.8"/>' for i in range(boxes)) + '</g>')
    return f'<g{anim(cls)}>{g}</g>' if cls else g


def board(x, y, w=110, h=76, lines=True):
    g = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="#fbfaf0" {S(3)}/>'
         f'<path d="M{x + 14} {y + h + 12}L{x + 20} {y + h}M{x + w - 14} {y + h + 12}L{x + w - 20} {y + h}" {S(3)}/>')
    if lines:
        g += f'<path d="M{x + 14} {y + 22}q20 -8 40 0t30 6M{x + 14} {y + 46}q22 -8 48 2" fill="none" stroke="#bdb59c" stroke-width="4" stroke-linecap="round"/>'
    return g


def sweeper(x, y, s=1, cls=''):
    g = (f'<g transform="translate({x} {y}) scale({s})" {S(2)}><rect x="-12" y="-12" width="24" height="18" rx="5" fill="{BLUE}"/>'
         f'<circle cx="-4" cy="-4" r="2" fill="{INK}" stroke="none"/><circle cx="4" cy="-4" r="2" fill="{INK}" stroke="none"/>'
         f'<path d="M12 -2l14 10M20 6l12 4M24 2l12 6" fill="none"/><circle cx="-7" cy="9" r="3" fill="{INK}"/><circle cx="7" cy="9" r="3" fill="{INK}"/></g>')
    return f'<g{anim(cls)}>{g}</g>' if cls else g


def counter(x, y, w=120, h=46, doors=('read', 'write')):
    g = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{WOOD}" {S(3)}/><rect x="{x - 6}" y="{y - 8}" width="{w + 12}" height="10" rx="3" fill="#c79f6b" {S(2.5)}/>'
    n = len(doors)
    for i, d in enumerate(doors):
        cx = x + (i + .5) * w / n
        g += f'<rect x="{cx - w / n / 2 + 6:.0f}" y="{y + 10}" width="{w / n - 12:.0f}" height="{h - 14}" rx="10" fill="{PAPER}" {S(2)}/>' + t(f'{cx:.0f}', y + h / 2 + 8, d, 'micro', style='letter-spacing:0')
    return g


def arrow(d, flow=True):
    return f'<path d="{d}" fill="none" stroke="{RED}" stroke-width="3.5" stroke-linecap="round" {"stroke-dasharray=" + chr(34) + "8 7" + chr(34) if flow else ""} marker-end="url(#ah)"{" class=" + chr(34) + "m-flow" + chr(34) if flow else ""}/>'


def note(x, y, rot=0, s=1):
    return (f'<g transform="translate({x:.0f} {y:.0f}) rotate({rot}) scale({s})" {S(1.8)}><rect x="-9" y="-7" width="18" height="14" fill="{GOLD}"/>'
            f'<path d="M-5 -2h10M-5 3h6" fill="none" opacity=".6"/></g>')


def sign(x, y, inner):
    return (f'<g transform="translate({x} {y})"><path d="M0 -22L24 18H-24Z" fill="{PAPER}" stroke="{RED}" stroke-width="4" stroke-linejoin="round"/>{inner}</g>')


def stamp(x, y, lines=SRC_STAMP, anchor='middle', color=RED):
    return ''.join(t(x, y + i * 14, ln, 'micro', anchor, f'fill:{color};letter-spacing:0') for i, ln in enumerate(lines))


def tag(x, y, text='From the source · reported'):
    return t(x, y, text, 'micro', 'start', f'fill:{RED};letter-spacing:.5px')


ILLU = ('Illustration', 'numbers invented')
PANELS = []


def add(kind, name, w, h, bg, body, title):
    PANELS.append((f'{kind}/{name}.svg', f'0 0 {w} {h}', title,
                   f'<rect width="{w}" height="{h}" fill="{bg}"/><rect width="{w}" height="{h}" fill="url(#dots)" opacity=".22"/>{body}'))


def comic(n, title, bg, body): add('comic', n, 320, 220, bg, body, title)
def story(n, title, bg, body): add('story', n, 440, 215, bg, body, title)
def icon(n, title, body): add('facts', n, 160, 100, '#f0e3c6', body, title)


def plate(n, title, bg, tg, body, caption):
    add('lead', n, 600, 340, bg, body
        + f'<rect x="10" y="288" width="580" height="44" fill="{CREAM}" {S()}/>' + t(300, 317, caption, 'b') + tag(22, 28, tg)
        + f'<path d="M8 10Q300 5 592 9Q596 170 591 332Q300 336 9 331Q4 170 8 10Z" fill="none" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>', title)


def ring_pts(cx, cy, rx, ry, n, start=-90):
    return [(cx + rx * math.cos(math.radians(start + 360 * i / n)), cy + ry * math.sin(math.radians(start + 360 * i / n))) for i in range(n)]


def ring(cx, cy, rx, ry):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{INK}" stroke-width="3" stroke-dasharray="10 7"/>'


def ring_desk(x, y, s, n, mood, lampon=False, ghost=False):
    g = desk(x, y, s) + pile(x, y - 6 * s, n, 36 * s, 10 * s) + face(x, y - 12 * s - n * 9 * s - 8, '#5a3d2b', 9 * s, mood)
    if lampon:
        g += lamp(x + 30 * s, y - 14 * s)
    return f'<g opacity=".25">{g}</g>' if ghost else g


# =============== Lead ===============
pts = ring_pts(300, 140, 215, 88, 7)
body = ring(300, 140, 215, 88) + ''.join(ring_desk(x, y + 14, .85, 3 + i % 3, 'sad', lampon=i == 2) for i, (x, y) in enumerate(pts))
plate('pile-up', 'Many desks on a ring, each buried in folders, one with a red lamp', '#e9dfc3', 'FROM THE SOURCE · REPORTED',
      body, 'Machines for messages: 12 in 2017, 177 by early 2022')
pts = ring_pts(300, 150, 120, 66, 5)
ghosts = ring_pts(300, 150, 250, 100, 8, -80)
body = ring(300, 150, 120, 66) + ''.join(ring_desk(x, y + 12, .6, 1, 'smile', ghost=True) for x, y in ghosts if abs(x - 300) > 160)
body += ''.join(desk(x, y + 14, 1.1) + shelf(x - 20, y - 52, 40, 42, 2) + face(x, y - 64, '#5a3d2b', 9, 'smile') for x, y in pts)
plate('smaller-room', 'A smaller ring of desks with big shelves and calm workers', '#e4ecd9', 'FROM THE SOURCE · REPORTED',
      body, 'After the switch: 72 machines, each holding 9 TB')

# =============== Story ===============
pts = ring_pts(220, 106, 170, 62, 6)
body = ring(220, 106, 170, 62) + ''.join(ring_desk(x, y + 10, .7, 3 + i % 3, 'sad', lampon=i == 3) for i, (x, y) in enumerate(pts))
body += pager(220, 90) + t(220, 118, 'BEEP!', 'sfx-s')
story('01-pile-up', 'Many desks on a ring buried in folders, a beeping pager', '#e9dfc3', body)

body = (sign(50, 30, f'<rect x="-9" y="-2" width="18" height="10" fill="{WOOD}" {S(2)}/>') + t(50, 62, 'one busy spot', 'b-s')
        + sign(50, 100, pile(0, 14, 4, 24, 6, 2)) + t(50, 132, 'tidying late', 'b-s')
        + sign(50, 168, clock(0, 6, 9, 130)) + t(50, 200, 'pauses', 'b-s')
        + arrow('M100 50Q170 30 250 44') + arrow('M104 120Q190 130 252 146')
        + desk(300, 76, 1.5, TEAL) + face(300, 40, '#27251e', 12) + t(300, 116, 'new desk', 'b')
        + f'<g transform="translate(372 148)"><rect x="-40" y="-8" width="80" height="34" rx="4" fill="{WOOD}" {S()}/>' + f'<rect x="-46" y="-16" width="92" height="10" rx="3" fill="#c79f6b" {S()}/></g>'
        + t(372, 192, 'front counter', 'b'))
story('02-two-moves', 'Three warning signs and two fixes: a new desk and a front counter', '#f3e7ca', body)

body = (counter(30, 70, 120, 40, ('one ask',)) + face(90, 40, '#27251e', 12) + crowd(190, 50, 5, 30, 'smile')
        + arrow('M150 56H178') + folder(165, 42, 24, 9, SAND)
        + shelf(20, 150, 70, 52, 2) + shelf(350, 150, 70, 52, 2, full=False) + truck(220, 178, .9, 3, 'm-bob')
        + arrow('M100 170H180') + t(220, 128, 'old shelf to new shelf', 'b-s'))
story('03-front-desk-and-move', 'A front counter shares one folder with a crowd while a truck moves boxes', '#e4ecd9', body)

cx0 = 70
body = t(125, 28, 'before', 'w') + t(335, 28, 'after', 'w')
for i in range(9):
    body += f'<rect x="{cx0 + 15}" y="{160 - i * 13}" width="80" height="11" rx="2" fill="{FCOL[i % 5]}" {S(2)}/>'
for i in range(4):
    body += f'<rect x="{285 + 0}" y="{160 - i * 34}" width="100" height="30" rx="3" fill="{FCOL[i % 5]}" {S(2.5)}/>'
body += (t(125, 184, '177 machines', 'b-s') + t(335, 184, '72 machines', 'b-s') + t(125, 44 + 0, 'avg 4 TB each', 'micro', style='letter-spacing:0')
         + t(335, 44, '9 TB each', 'micro', style='letter-spacing:0') + arrow('M200 100H262', False) + stamp(220, 206, ('From the source · reported',)))
story('04-before-after', 'A tall column of small boxes before and a short column of bigger boxes after', '#f3e7ca', body)

# =============== Comic ===============
body = cabinet(20, 50, 90, 124, 3, 0) + t(65, 40, 'chat room + time window', 'micro', style='letter-spacing:0') + t(65, 196, 'one drawer', 'w-s')
for i, y in enumerate((50, 115, 180)):
    body += desk(250, y, 1) + f'<rect x="235" y="{y - 24}" width="30" height="14" rx="2" fill="#8e8672" {S(2)}/>' + arrow(f'M118 {112} Q180 {y - 10} 220 {y - 10}', False)
body += t(160, 28, 'three copies', 'b-s')
comic('01a-one-drawer', 'One labeled drawer with three copies on three desks', '#f0e3c6', body)

body = (cabinet(18, 90, 56, 70, 2) + folder(46, 74, 30, 10, SAND) + folder(46, 64, 30, 10, GREEN) + t(46, 180, 'friends', 'w-s')
        + cabinet(110, 30, 100, 130, 3, 0) + ''.join(folder(150 + (i % 2) * 8, 28 - i * 10, 50, 12, FCOL[i % 5], (-1) ** i * 6) for i in range(4))
        + t(160, 180, 'huge server', 'w-s') + crowd(238, 80, 1) + ''.join(person(250 + (i % 2) * 6, 70 + i * 26, i + 1, .9, 'sad') for i in range(5)) + t(160, 208, 'a very busy drawer', 'b-s'))
comic('01b-busy-drawer', 'A tiny drawer next to a huge overflowing drawer with a long line', '#f9dfc0', body)

body = ''.join(desk(x, 100, 1.1) + (pile(x, 94, 5, 40, 10) + drop(x + 20, 38) + face(x, 36, '#5a3d2b', 10, 'o') if x == 160 else pile(x, 94, 1, 40, 10) + face(x, 70, '#27251e', 10)) for x in (60, 160, 260))
body += ''.join(person(60 + i * 40, 168, i, .9, 'flat') for i in range(6)) + t(160, 30, 'WAIT!', 'sfx') + t(160, 212, 'everyone behind waits too', 'b-s')
comic('01c-everyone-waits', 'Three desks, the middle one sweating under a pile, a line of people waiting', '#e6dcef', body)

body = desk(70, 150, 1.5) + ''.join(folder(30 + (i % 3) * 22, 100 - (i // 3) * 12, 20, 9, FCOL[i % 5], i * 9 - 18) for i in range(6))
body += arrow('M110 110H190') + f'<path d="M150 90v40" stroke="{INK}" stroke-width="3" stroke-dasharray="3 4"/>' + folder(235, 110, 60, 24, GREEN) + folder(235, 134, 60, 24, GREEN) + t(235, 176, 'merge', 'w') + t(70, 30, 'many small piles', 'b-s') + t(235, 30, 'one tidy one', 'b-s')
comic('02a-small-piles', 'Many small folders zipping into one neat folder', '#dbe7e5', body)

body = (desk(70, 160, 1.4) + pile(66, 150, 7, 44, 10, 5) + face(70, 56, '#5a3d2b', 11, 'o') + drop(90, 50) + clock(170, 50, 22, 200) + crowd(130, 150, 7, 28, 'sad', .85) + t(160, 20, 'running behind', 'w') + t(160, 205, 'reads wait', 'b-s'))
comic('02b-behind', 'A worker with a messy stack, a clock, and impatient people', '#f9dfc0', body)

body = ''
for i, (lbl, n, out) in enumerate((('1 step out', 4, True), ('2 tidy up', 2, False), ('3 step back', 1, False))):
    x = 55 + i * 105
    body += f'<rect x="{x - 48}" y="40" width="96" height="120" rx="6" fill="{PAPER}" {S(2)} opacity=".7"/>'
    body += f'<path d="M{x - 40} 120q40 -30 80 0" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="7 6"/>'
    dy = 34 if i == 1 else 0
    body += desk(x, 112 - (34 if i == 1 else 0) + 0, .8) + pile(x, 106 - dy, n, 30, 9) + face(x, 94 - dy - n * 8, '#5a3d2b', 8, 'smile' if i else 'sad')
    body += t(x, 182, lbl, 'w-s')
body += arrow('M100 36q6 -8 14 0', False)
comic('02c-dance', 'A desk steps out of the ring, tidies, steps back with a smaller pile', '#e4ecd9', body)

body = (board(150, 40, 130, 90) + worker(70, 140, 'smile', ORANGE, .9) + f'<path d="M95 130l45 -48" {S(4)}/>' + sweeper(200, 150, 1.2, 'm-bob') + t(60, 30, 'writing...', 'b-s') + t(210, 196, 'tidying', 'b-s'))
comic('03a-sweeper', 'A tiny sweeper robot tidies a whiteboard while a worker writes', '#dbe7e5', body)

body = (worker(90, 120, 'smile', '#a2c2a7', 1.1) + f'<path d="M90 60v20M78 66l24 8M102 66l-24 8" stroke="#6fb0d6" stroke-width="3" stroke-linecap="round"/>'
        + f'<rect x="130" y="30" width="150" height="40" rx="14" fill="{PAPER}" {S()}/><path d="M138 66l-20 20l30 -14" fill="{PAPER}" {S()}/>' + t(205, 56, 'So I was say-', 'b-s')
        + sweeper(230, 130, 1.4, 'm-bob') + crowd(60, 190, 8, 30, 'flat', .8) + t(250, 170, 'sweep sweep', 'b-s'))
comic('03b-freeze', 'The worker freezes mid-sentence with a snowflake while the sweeper sweeps', '#e6dcef', body)

body = (desk(70, 130, 1.4, GREY) + face(70, 82, '#8a8a8a', 11, 'flat') + t(104, 60, 'Zzz', 'sfx-s') + f'<circle cx="70" cy="176" r="16" fill="{RED}" {S(3)}/><path d="M63 176a7 7 0 1 1 3 6" fill="none" stroke="{PAPER}" stroke-width="2.5"/>'
        + person(116, 150, 2, .9) + f'<path d="M124 168l-36 8" {S(3)}/>'
        + desk(240, 130, 1.4, TEAL) + face(240, 82, '#27251e', 11) + sweeper(240, 176, .9) + f'<path d="M218 156l44 40M262 156l-44 40" stroke="{RED}" stroke-width="4" stroke-linecap="round"/>' + t(240, 40, 'no cleaner', 'w') + t(70, 40, 'press restart', 'w-s'))
comic('03c-reboot', 'A person presses a big restart button on a sleepy desk; a new desk has no sweeper', '#f0e3c6', body)

body = (counter(100, 100, 120, 50, ('read', 'write')) + crowd(36, 90, 2, 30, 'smile', .9) + crowd(36, 150, 2, 30, 'smile', .9) + shelf(236, 48, 70, 110, 4) + t(160, 36, 'front counter', 'w') + t(271, 180, 'back room', 'b-s') + arrow('M72 112Q86 126 94 126') + arrow('M226 124H234'))
comic('04a-front-desk', 'A front counter between a crowd and shelves, with labeled doorways', '#dbe7e5', body)

body = (shelf(14, 70, 60, 80, 3) + person(104, 100, 3, 1.1) + note(104, 140, -10) + arrow('M80 112H130', False) + arrow('M126 150H82', False)
        + ''.join(person(190 + (i % 3) * 40, 60 + (i // 3) * 56, i, .9) + note(190 + (i % 3) * 40 + 18, 96 + (i // 3) * 56, 12, .8) for i in range(6)) + t(60, 175, 'one trip', 'b-s') + t(240, 28, 'everyone gets the note', 'b-s'))
comic('04b-one-helper', 'One helper fetches one note and many people receive a copy', '#f9dfc0', body)

body = counter(180, 80, 120, 50, ('same desk',)) + face(240, 56, '#27251e', 12) + ''
for i in range(4):
    y = 36 + i * 42
    body += person(34, y, i, .85) + f'<rect x="52" y="{y - 8}" width="42" height="16" rx="8" fill="{GOLD}" {S(2)}/>' + t(73, y + 5, '#chat', 'micro', style='letter-spacing:0') + arrow(f'M98 {y} Q140 {y} 172 {104 + (i - 1.5) * 8}', False)
comic('04c-same-desk', 'Arrows from many people with the same channel badge point to one calm counter', '#e6dcef', body)

body = (person(160, 50, 1, 1.2) + note(160, 98, 0, 1.4)
        + f'<rect x="40" y="130" width="90" height="56" rx="5" fill="{GREY}" {S(3)}/>' + t(85, 164, 'old box', 'w-s')
        + f'<rect x="190" y="130" width="90" height="56" rx="5" fill="{TEAL}" {S(3)}/>' + f'<text x="235" y="164" text-anchor="middle" class="w-s" style="fill:{PAPER}">new box</text>'
        + arrow('M150 112Q110 110 98 126') + arrow('M170 112Q210 110 232 126') + t(160, 20, 'write to both', 'w'))
comic('05a-write-both', 'A person drops a note into both an old box and a new box', '#f0e3c6', body)

body = (f'<g {S()}><rect x="20" y="96" width="60" height="30" fill="{WOOD}"/><circle cx="36" cy="134" r="8" fill="{GREY}"/><circle cx="66" cy="134" r="8" fill="{GREY}"/></g>' + t(50, 80, 'old: months', 'b-s')
        + truck(220, 110, 1.5) + f'<g transform="translate(220 52)"><rect x="-20" y="-16" width="40" height="30" rx="3" fill="{PAPER}" {S(2)}/><path d="M-12 -6l4 4 7 -8M-12 6l4 4 7 -8" fill="none" stroke="{TEAL}" stroke-width="2.5"/></g>'
        + t(220, 28, 'notebook of checks', 'micro', style='letter-spacing:0') + t(230, 172, 'new: days', 'b-s') + t(50, 172, 'slow cart', 'b-s'))
comic('05b-new-mover', 'A slow cart labeled months next to a fast truck labeled days', '#dbe7e5', body)

body = (f'<path d="M0 150h320" stroke="{INK}" stroke-width="3"/><path d="M0 168h320" stroke="{INK}" stroke-width="2" stroke-dasharray="14 10"/>'
        + truck(140, 130, 1.6, 3, 'm-bob') + f'<path d="M20 110h40M10 126h40M24 142h30" {S(2.5)} opacity=".5"/>' + shelf(250, 100, 56, 50, 2)
        + f'<path d="M20 70A40 40 0 0 1 100 70" fill="{PAPER}" {S(3)}/><path d="M60 70l24 -22" stroke="{RED}" stroke-width="4" stroke-linecap="round"/>'
        + t(160, 200, 'up to 3.2 million messages a second', 'b-s') + t(160, 218, 'From the source · reported', 'micro', style=f'fill:{RED};letter-spacing:0'))
comic('05c-truck-runs', 'A truck racing boxes to a new shelf with a speed gauge', '#f9dfc0', body)

body = f'<rect x="20" y="60" width="280" height="26" rx="13" fill="{PAPER}" {S(3)}/><rect x="24" y="64" width="232" height="18" rx="9" fill="{GREEN}"/>'
body += t(160, 50, 'almost done', 'w') + ''.join(f'<g transform="translate({262 + i * 12} {160 - i * 2})" {S(2)}><path d="M-9 20v-22a9 9 0 0 1 18 0v22Z" fill="{GREY}"/><path d="M0 -4v10M-4 0h8" fill="none"/></g>' for i in range(4))
body += ''.join(f'<g transform="translate({40 + i * 30} 178)" {S(2)}><path d="M-9 20v-22a9 9 0 0 1 18 0v22Z" fill="{GREY}"/></g>' for i in range(3)) + t(160, 128, 'grey markers pile up at the end', 'b-s') + arrow('M236 100Q250 100 260 120')
comic('06a-stuck', 'A nearly full progress bar blocked by a pile of grey markers', '#e6dcef', body)

body = (person(36, 60, 0) + shelf(14, 110, 50, 60, 2) + person(284, 60, 2) + shelf(256, 110, 50, 60, 2, color=TEAL)
        + note(80, 100, 0) + note(240, 100, 0) + arrow('M70 100H100', False) + arrow('M250 100H220', False)
        + person(160, 70, 1, 1.2) + f'<rect x="120" y="118" width="80" height="34" rx="6" fill="{PAPER}" {S()}/>' + t(160, 142, '=  =', 'mono') + t(160, 188, 'checker nods', 'b-s') + t(160, 28, 'same note?', 'w'))
comic('06b-compare', 'Two readers read notes from different shelves and a checker compares them', '#dbe7e5', body)

body = (f'<rect x="120" y="120" width="80" height="22" rx="11" fill="{PAPER}" {S(3)}/><circle cx="184" cy="131" r="12" fill="{TEAL}" {S(3)}/>' + t(160, 112, 'switch: new', 'w-s')
        + shelf(14, 70, 56, 70, 2, False) + t(42, 160, 'old: quiet', 'b-s') + t(42, 60, 'Zzz', 'sfx-s')
        + f'<path d="M230 170h70" stroke="{INK}" stroke-width="3"/><circle cx="265" cy="160" r="14" fill="#f3b6a0" {S(2.5)}/><path d="M265 146v-12" {S(3)}/><circle cx="265" cy="132" r="3" fill="{RED}"/>'
        + crowd(215, 120, 1, 0, 'smile', .9) + crowd(300, 120, 1, 0, 'smile', .9) + crowd(244, 196, 1, 0, 'smile', .9) + crowd(286, 196, 1, 0, 'smile', .9) + t(265, 36, 'TA-DA!', 'sfx'))
comic('06c-cake', 'A big switch flipped to the new shelf, a team with a cake, old shelf quiet', '#f3e7ca', body)

# =============== Facts ===============
def fact(figure, lines):
    return t(80, 66, figure, 'w', style='font-size:17px') + (t(80, 80, lines[0], 'micro', style='letter-spacing:0;font-size:12px') if lines[0] else '') + stamp(80, 92 if lines[0] else 84, ('From the source · reported',), color=RED)[:0]


def facts_foot(figure, sub=None):
    st = f'fill:{RED};letter-spacing:0'
    y = 52 if sub else 58
    out = t(80, y, figure, 'w', style='font-size:17px')
    if sub:
        out += t(80, y + 14, sub, 'micro', style='letter-spacing:0')
    y2 = 82 if sub else 80
    return out + t(80, y2, 'From the source', 'micro', style=st) + t(80, y2 + 13, '· reported', 'micro', style=st)


body = ''.join(desk(18 + i * 18, 34, .35) for i in range(3)) + arrow('M70 26H92', False) + ''.join(f'<rect x="{98 + (i % 8) * 7}" y="{8 + (i // 8) * 7}" width="5" height="5" fill="{FCOL[i % 5]}" stroke="{INK}" stroke-width="1"/>' for i in range(40))
icon('nodes', 'From 12 to 177 machines', body + facts_foot('12 to 177'))

body = (f'<rect x="14" y="10" width="132" height="12" rx="3" fill="{ORANGE}" {S(2)}/><rect x="14" y="28" width="12" height="12" rx="3" fill="{GREEN}" {S(2)}/>'
        + t(80, 18, 'months', 'micro', style='letter-spacing:0') + t(46, 38, 'days', 'micro', style='letter-spacing:0;font-size:12px'))
icon('estimate', 'Estimated move time from three months to nine days', body + facts_foot('3 months to 9 days'))

body = truck(50, 30, .6) + f'<path d="M96 28h50M100 18h40M104 38h36" {S(2.5)} opacity=".5"/>'
icon('speed', 'A fast truck, 3.2 million messages per second', body + facts_foot('3.2 million', 'messages / second'))

body = f'<g transform="translate(34 4)">' + shelf(0, 0, 30, 30, 2) + '</g>' + arrow('M76 20H98', False) + shelf(104, 8, 40, 24, 1)
icon('machines', 'From 177 to 72 machines, each holding more', body + facts_foot('177 to 72', '9 TB each, was 4'))


def rangebar(y, lo, hi, scale, label, new):
    x0 = 14
    return (f'<rect x="{x0 + lo * scale:.0f}" y="{y}" width="{(hi - lo) * scale:.0f}" height="11" rx="3" fill="{ORANGE}" {S(2)}/>'
            f'<rect x="{x0}" y="{y + 15}" width="{new * scale:.0f}" height="11" rx="3" fill="{TEAL}" {S(2)}/>')


icon('fetch-p99', 'Fetch time p99: 40 to 125 ms before, 15 ms after',
     rangebar(6, 40, 125, 1.0, '', 15) + facts_foot('40-125 to 15 ms', 'p99 fetch time'))
icon('insert-p99', 'Save time p99: 5 to 70 ms before, 5 ms after',
     rangebar(6, 5, 70, 1.8, '', 5) + facts_foot('5-70 to 5 ms', 'p99 save time'))


# =============== Write ===============
def srcs(doc):
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
    need = srcs(json.loads(SEED.read_text()))
    made = {rel: write(OUT, rel, svg(vb, body, title)) for rel, vb, title, body in PANELS}
    for s, w, h in need:
        rel = s.replace(SLUG + '/', '', 1)
        assert rel in made, f'not drawn: {rel}'
        assert f'viewBox="0 0 {w} {h}"' in made[rel].read_text(), f'wrong viewBox for {rel}'
    print(f'wrote {len(made)} files ({len({s for s, _, _ in need})} required) to {OUT}; total {sum(p.stat().st_size for p in made.values())} bytes; max {max(p.stat().st_size for p in made.values())}')
