"""Draws the media for the Netflix post "Benchmarking Cassandra Scalability on AWS: Over a million writes per second".

Run from the repo root:  python3 tools/draw_netflix_cassandra_benchmark.py
Writes standalone SVGs to backups/media/netflix-cassandra-benchmark/{lead,story,comic,facts}/ (Git recovery copies).
Every media.src in data/seed/papers/netflix-cassandra-benchmark.json must be written. Numbers drawn are only those in the
post as reported in the JSON (288, 1.1 million, 3.3 million, 48/96/144/288, 10/20/30/60, 6 to 48, 2 hours, ...).
Original drawings only: no company logos or branding.
"""
import json
import math
import re
from pathlib import Path

from media_kit import COMIC_CSS, COMIC_DEFS, INK, RED, anim, buddy, standalone, t, write

ROOT = Path(__file__).resolve().parent.parent
SLUG = 'netflix-cassandra-benchmark'
OUT = ROOT / 'backups' / 'media' / SLUG
SEED = ROOT / 'data' / 'seed' / 'papers' / f'{SLUG}.json'

CREAM, TEAL, GREEN, GOLD, WOOD = '#fbf3dc', '#377675', '#a2c2a7', '#ffe597', '#d9b98a'
PAPER, PURPLE, SAND, ORANGE, GREY = '#fff8e3', '#c3b2d8', '#f7d79b', '#efae78', '#b5ab92'
ZONES = [TEAL, ORANGE, PURPLE]
SRC_TAG = 'FROM THE SOURCE · REPORTED'

EXTRA_CSS = ('.slide{animation:sl 5s ease-in-out infinite}@keyframes sl{0%{transform:translateX(-26px)}40%,100%{transform:none}}'
             '.slr{animation:sr 5s ease-in-out infinite}@keyframes sr{0%{transform:translateX(70px)}40%,100%{transform:none}}'
             '.fall{animation:fl 5s ease-in infinite}@keyframes fl{0%,20%{transform:none}40%,100%{transform:translateX(0)}}')
DEFS = COMIC_DEFS + (
    f'<g id="dk" stroke="{INK}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round">'
    '<path d="M-18 6v15M18 6v15" fill="none"/><rect x="-25" y="-6" width="50" height="13" rx="3" fill="currentColor"/>'
    f'<rect x="-10" y="-17" width="20" height="11" rx="1.5" fill="#fff8e3" stroke-width="2.5"/></g>'
    f'<marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
    f'<path d="M0 0L10 5L0 10Z" fill="{RED}"/></marker>')


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
        if b.startswith('@keyframes'):
            name = b.split('{')[0].split()[1]
            if re.search(r'animation:' + re.escape(name) + r'(?![\w-])', text):
                kept.append(b)
    return '\n'.join(kept)


def svg(vb, body, title):
    d = DEFS
    if 'href="#dk"' not in body:
        d = d.replace(d[d.index('<g id="dk"'):d.index('<marker')], '')
    if 'ah)' not in body:
        d = d[:d.index('<marker')]
    return standalone(vb, body, title, css=prune_css(COMIC_CSS + EXTRA_CSS, body), defs=d)


# ---------- drawing pieces ----------
def dk(x, y, s=1, col=WOOD, cls='', delay=None):
    g = f'<use href="#dk" transform="translate({x:.0f} {y:.0f}) scale({s})" style="color:{col}"/>'
    return f'<g{anim(cls, delay)}>{g}</g>' if cls else g


def ring_pts(cx, cy, rx, ry, n, start=-90):
    return [(cx + rx * math.cos(math.radians(start + 360 * i / n)), cy + ry * math.sin(math.radians(start + 360 * i / n))) for i in range(n)]


def ring(cx, cy, rx, ry, n, s, cols=(WOOD,), w=2.5, op=1):
    g = f'<g opacity="{op}"><ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{INK}" stroke-width="{w}" stroke-dasharray="9 6"/>'
    for i, (x, y) in sorted(enumerate(ring_pts(cx, cy, rx, ry, n)), key=lambda p: p[1][1]):
        g += dk(x, y, s, cols[i % len(cols)])
    return g + '</g>'


def env(x, y, rot=0, s=1):
    return (f'<g transform="translate({x:.0f} {y:.0f}) rotate({rot}) scale({s})" stroke="{INK}" stroke-width="2" stroke-linejoin="round">'
            f'<rect x="-13" y="-9" width="26" height="18" rx="2" fill="{PAPER}"/><path d="M-13 -9L0 2L13 -9" fill="none"/></g>')


def arrow(d, flow=True, w=3.5):
    f = ' stroke-dasharray="8 7" class="m-flow"' if flow else ''
    return f'<path d="{d}" fill="none" stroke="{RED}" stroke-width="{w}" stroke-linecap="round"{f} marker-end="url(#ah)"/>'


def kid(x, y, s=.5, col=SAND, cls='', delay=None):
    return buddy(x, y, '', col, s, cls, delay)


def building(x, y, s=1, col='#cfd8d3', desks=0, dcol=WOOD):
    g = (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round">'
         f'<rect x="-40" y="-50" width="80" height="100" rx="3" fill="{col}"/><rect x="-40" y="-50" width="80" height="14" fill="{INK}" opacity=".18"/></g>')
    return g


def tag(x, y, txt='', rot=0):
    return (f'<g transform="translate({x} {y}) rotate({rot})"><path d="M-12 0L-4 -9H22V9H-4Z" fill="{GOLD}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
            f'<circle cx="-4" cy="0" r="2" fill="{INK}"/>' + (t(10, 5, txt, 'micro') if txt else '') + '</g>')


def stamp(x, y, txt, w, rot=-4):
    return (f'<g transform="translate({x} {y}) rotate({rot})"><rect x="{-w / 2}" y="-14" width="{w}" height="28" rx="4" fill="{PAPER}" stroke="{RED}" stroke-width="2.5"/>'
            + t(0, 5, txt, 'micro', style=f'fill:{RED}') + '</g>')


def clock(x, y, r=34, hand=60):
    a = math.radians(hand - 90)
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{PAPER}" stroke="{INK}" stroke-width="3.5"/>'
            + ''.join(f'<path d="M{x + (r - 7) * math.cos(math.radians(k * 30)):.1f} {y + (r - 7) * math.sin(math.radians(k * 30)):.1f}L{x + (r - 3) * math.cos(math.radians(k * 30)):.1f} {y + (r - 3) * math.sin(math.radians(k * 30)):.1f}" stroke="{INK}" stroke-width="2"/>' for k in range(12))
            + f'<path d="M{x} {y}L{x + (r - 12) * math.cos(a):.1f} {y + (r - 12) * math.sin(a):.1f}" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'
            f'<path d="M{x} {y}L{x} {y - r + 9}" stroke="{RED}" stroke-width="3" stroke-linecap="round"/><circle cx="{x}" cy="{y}" r="3.5" fill="{INK}"/>')


def coins(x, y, n=3):
    return ''.join(f'<ellipse cx="{x + (i % 2) * 6}" cy="{y - i * 7}" rx="16" ry="6" fill="{GOLD}" stroke="{INK}" stroke-width="2.5"/>' for i in range(n))


def stopwatch(x, y, r=30):
    return (f'<rect x="{x - 8}" y="{y - r - 10}" width="16" height="8" rx="2" fill="{GREY}" stroke="{INK}" stroke-width="2.5"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{PAPER}" stroke="{INK}" stroke-width="3.5"/>'
            f'<path d="M{x} {y}V{y - r + 8}" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/>'
            f'<path d="M{x} {y - r + 3}A{r - 3} {r - 3} 0 0 1 {x + 7} {y - r + 4}" fill="none" stroke="{RED}" stroke-width="5"/><circle cx="{x}" cy="{y}" r="3.5" fill="{INK}"/>')


def thumb(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round" fill="#f0c9a0">'
            '<rect x="-14" y="-4" width="28" height="22" rx="6"/><rect x="-8" y="-24" width="10" height="24" rx="5"/></g>')


def notebook(x, y, s=1):
    g = (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round">'
         f'<rect x="-32" y="-42" width="64" height="84" rx="4" fill="{PAPER}"/><path d="M-32 -42v84" stroke="{RED}" stroke-width="3"/>')
    for i in range(5):
        g += f'<path d="M-22 {-28 + i * 14}h42" stroke-width="1.8" opacity=".55" fill="none"/>'
    return g + '</g>'


def pencil(x, y, rot=-40, cls=''):
    g = (f'<g transform="translate({x} {y}) rotate({rot})" stroke="{INK}" stroke-width="2" stroke-linejoin="round">'
         f'<rect x="0" y="-5" width="34" height="10" fill="{ORANGE}"/><path d="M0 -5L-12 0L0 5Z" fill="{SAND}"/><rect x="34" y="-5" width="7" height="10" fill="#d98b8b"/></g>')
    return f'<g{anim(cls)}>{g}</g>' if cls else g


def folder(x, y, w=54, h=40, color=SAND):
    return (f'<g transform="translate({x:.0f} {y:.0f})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round">'
            f'<path d="M{-w / 2} {-h / 2}h{w * .4:.0f}l6 6h{w * .6 - 6:.0f}V{h / 2}H{-w / 2}Z" fill="{color}"/>'
            f'<path d="M{-w / 2 + 8} {h / 2 - 10}h{w * .5:.0f}" stroke-width="1.8" opacity=".5" fill="none"/></g>')


def board(x, y, w=110, h=76):
    g = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="#fbfaf0" stroke="{INK}" stroke-width="3"/>'
         f'<path d="M{x + 14} {y + h + 12}L{x + 20} {y + h}M{x + w - 14} {y + h + 12}L{x + w - 20} {y + h}" stroke="{INK}" stroke-width="3"/>')
    for i in range(3):
        nx = x + 10 + i * (w - 20) / 3
        g += f'<rect x="{nx:.0f}" y="{y + 12}" width="{(w - 30) / 3:.0f}" height="26" fill="{[SAND, GREEN, PURPLE][i]}" stroke="{INK}" stroke-width="1.8"/>'
        g += f'<rect x="{nx:.0f}" y="{y + 44}" width="{(w - 30) / 3:.0f}" height="20" fill="{[GREEN, PURPLE, SAND][i]}" stroke="{INK}" stroke-width="1.8"/>'
    return g


def chart(x0, y0, x1, y1, pts, lab=True, dots=True):
    """Axes plus a straight line through the origin. pts are (x, y) dot positions."""
    g = (f'<path d="M{x0} {y1 - 8}V{y0}M{x0} {y1 - 8}H{x1}" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
         f'<path d="M{x0} {y1 - 8}L{pts[-1][0] + 14} {pts[-1][1] - 14 * (y1 - 8 - pts[-1][1]) / (pts[-1][0] - x0):.0f}" stroke="{RED}" stroke-width="3.5" stroke-linecap="round" fill="none"/>')
    for i, (x, y) in enumerate(pts):
        g += f'<g{anim("m-loop-pop", i * .5)}><circle cx="{x:.0f}" cy="{y:.0f}" r="7" fill="{GOLD}" stroke="{INK}" stroke-width="3"/></g>'
    return g


PANELS = []


def bgp(bg, body, w, h):
    return f'<rect width="{w}" height="{h}" fill="{bg}"/><rect width="{w}" height="{h}" fill="url(#dots)" opacity=".22"/>{body}'


def comic(name, title, bg, body):
    PANELS.append((f'comic/{name}.svg', '0 0 320 220', title, bgp(bg, body, 320, 220)))


def story(name, title, bg, body):
    PANELS.append((f'story/{name}.svg', '0 0 440 215', title, bgp(bg, body, 440, 215)))


def icon(name, title, body, bg='#f0e3c6'):
    PANELS.append((f'facts/{name}.svg', '0 0 160 100', title, bgp(bg, body, 160, 100)))


def plate(name, title, bg, tagtxt, body, caption):
    PANELS.append((f'lead/{name}.svg', '0 0 600 340', title, bgp(bg, body, 600, 340)
                   + f'<rect x="10" y="288" width="580" height="44" fill="{CREAM}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
                   + t(300, 317, caption, 'b') + t(22, 28, tagtxt, 'micro', 'start', f'fill:{RED}')
                   + f'<path d="M8 10Q300 5 592 9Q596 170 591 332Q300 336 9 331Q4 170 8 10Z" fill="none" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>'))


def src(x=12, y=20):
    return t(x, y, SRC_TAG, 'micro', 'start', f'fill:{RED}')


def foot(s, y=208):
    return t(160, y, s, 'b-s')


def senders(xs, y, col=SAND, s=.45):
    return ''.join(kid(x, y, s, col, 'm-bob', i * .25) for i, x in enumerate(xs))


# =====================================================================
# Lead plates
# =====================================================================
b = (ring(120, 150, 62, 38, 7, .5) + arrow('M205 150H255', False, 4) + ring(420, 132, 150, 84, 28, .42)
     + senders([270, 300, 340, 400, 450, 500, 550], 268, SAND, .5)
     + ''.join(env(x, 232 - (i % 2) * 14, -10 + i * 4, .8) for i, x in enumerate([300, 400, 500])))
b += t(120, 232, 'a small ring', 'b-s') + t(420, 262 - 52, '', 'b-s')
plate('many-desks', 'A small ring of desks grows into a very large ring while little senders toss notes at it.', '#efe6cd', SRC_TAG, b,
      'The biggest test ring: 288 machines')

pts = [(80 + n * 1.55, 215 - n * .55) for n in (48, 96, 144, 288)]
b = chart(80, 40, 570, 223, pts)
for (x, y), n, r in zip(pts, (48, 96, 144, 288), (16, 22, 30, 46)):
    b += t(x - 4, y - 16, str(n), 'mono-s') + ring(x, 252, r, r * .32, {48: 4, 96: 6, 144: 8, 288: 12}[n], .2)
b += t(30, 66, 'speed', 'b-s', 'middle', 'writing-mode:horizontal-tb') + t(570, 240, '', 'b-s')
plate('straight-line', 'Four dots climbing one straight line, with a small ring of desks growing under each.', '#efe6cd', SRC_TAG, b,
      'Speed grew in a straight line as machines were added')

# =====================================================================
# Story panels (440x215)
# =====================================================================
b = (src() + ring(330, 105, 95, 55, 18, .45, (GREY,), 2, .5) + t(330, 28 + 14, '', 'b-s')
     + t(330, 180, 'a much bigger ring?', 'b-s')
     + ring(120, 150, 62, 30, 7, .5) + t(120, 196, 'Netflix today: 6 to 48 machines', 'b-s')
     + buddy(60, 70, '', '#c3b2d8', .85, 'm-wobble')
     + '<rect x="96" y="34" width="52" height="42" rx="14" fill="#fff8e3" stroke="#322e24" stroke-width="2"/><path d="M104 74L92 90L116 76" fill="#fff8e3" stroke="#322e24" stroke-width="2" stroke-linejoin="round"/>'
     + t(122, 66, '?', 'sfx'))
story('01-will-it-keep-up', 'A small ring of desks and a worried engineer with a question mark; a bigger ring waits behind.', '#e8e2cc', b)

b = (src() + ring(270, 120, 115, 58, 12, .55, ZONES) + senders([30, 62, 30, 62, 30, 62], 0, SAND, .5)[:0])
for i in range(6):
    b += kid(34 + (i % 2) * 34, 58 + (i // 2) * 42, .5, SAND, 'm-bob', i * .2)
b += arrow('M96 105H140', True, 3.5) + t(270, 24, '', 'b-s')
for i, c in enumerate(ZONES):
    b += f'<rect x="{150 + i * 90}" y="190" width="14" height="14" rx="3" fill="{c}" stroke="{INK}" stroke-width="2"/>' + t(170 + i * 90, 203, f'zone {"ABC"[i]}', 'b-s', 'start')
b += t(72, 190, 'a crowd of senders', 'b-s', 'middle')
b += t(270, 40, '3 zones, 3 copies of every write', 'w-s')
story('02-rent-a-ring', 'A ring of desks in three colour groups, one per building, with a crowd of senders waiting outside.', '#e8e2cc', b)

b = src()
for x, n, c in zip((55, 165, 275, 385), (48, 96, 144, 288), (10, 20, 30, 60)):
    r = {48: 20, 96: 28, 144: 34, 288: 48}[n]
    b += ring(x, 150, r, r * .4, {48: 5, 96: 7, 144: 9, 288: 14}[n], .22)
    b += arrow(f'M{x} 128V{128 - n * .3:.0f}', False, 4) + t(x, 190, f'{n} machines', 'b-s') + t(x, 207, f'{c} clients', 'b-s')
b += t(220, 38, '', 'b-s')
story('03-add-machines', 'Four rings of growing size, each with longer arrows in steady steps.', '#e8e2cc', b)

b = (src() + f'<rect x="20" y="60" width="190" height="74" rx="8" fill="{INK}"/><rect x="26" y="66" width="178" height="62" rx="4" fill="{SAND}"/>'
     + t(115, 108, '1.1 million', 'mono', style='font-size:23px') + t(115, 154, 'client writes a second', 'b-s')
     + f'<rect x="236" y="48" width="190" height="94" rx="8" fill="{INK}"/><rect x="242" y="54" width="178" height="82" rx="4" fill="{GREEN}"/>'
     + t(331, 104, '3.3 million', 'mono', style='font-size:23px') + t(331, 164, 'writes a second in total', 'b-s')
     + t(331, 180, '(each write kept 3 times)', 'b-s')
     + f'<path d="M210 98h16" stroke="{RED}" stroke-width="4" marker-end="url(#ah)"/>' + t(120, 190, '', 'b-s')
     + stamp(100, 195, 'NETFLIX REPORTS THIS', 190, -3))
story('04-evidence', 'A counter reading 1.1 million beside a bigger counter reading 3.3 million, with a tag saying Netflix reports this.', '#e8e2cc', b)

# =====================================================================
# Comic panels (320x220)
# =====================================================================
B = '#e8e2cc'
b = (src() + buddy(48, 100, '', '#c3b2d8', 1, 'm-hop') + f'<rect x="20" y="150" width="56" height="26" rx="6" fill="{RED}" stroke="{INK}" stroke-width="3"/>'
     + t(48, 168, 'GO', 'w-s', style='fill:#fff8e3'))
for i, (x, y) in enumerate([(130, 70), (200, 70), (270, 70), (130, 130), (200, 130), (270, 130)]):
    b += dk(x, y, .85, WOOD, 'm-loop-pop', i * .5)
b += foot('a ring in about an hour')
comic('01a-order', 'An engineer clicks one big button and empty desks pop up one by one.', B, b)

b = src()
for i, c in enumerate(ZONES):
    x = 62 + i * 98
    b += building(x, 100, 1, '#cfd8d3') + dk(x - 12, 88, .5, c) + dk(x + 14, 88, .5, c) + dk(x - 12, 126, .5, c) + dk(x + 14, 126, .5, c)
b += t(160, 176, 'about 1 ms apart', 'b-s') + foot('same number in each zone')
comic('01b-three-buildings', 'Three buildings in a row, each with the same number of desks.', B, b)

b = (dk(80, 140, 1.1, GREY) + '<g transform="translate(80 140)"><path d="M-20-20L20 20M20-20L-20 20" stroke="#a13324" stroke-width="5" stroke-linecap="round"/></g>'
     + '<g class="slr">' + dk(215, 120, 1.3, GREEN) + '</g>' + f'<path d="M150 150h130" stroke="{INK}" stroke-width="3" stroke-dasharray="4 6" opacity=".5"/>'
     + foot('a new desk takes its place'))
comic('01c-replacement', 'One desk falls with a cross on it and a new desk slides into the same spot.', B, b)

b = (kid(40, 100, .9, SAND, 'm-bob') + env(90, 80, -12, 1) + arrow('M110 85H150', True, 3))
for i, (x, y) in enumerate([(190, 60), (270, 80), (170, 150), (250, 160)]):
    b += dk(x, y, .8, WOOD)
b += dk(220, 110, 1, GREEN) + f'<circle cx="220" cy="78" r="9" fill="{GOLD}" stroke="{INK}" stroke-width="2.5"/>' + t(220, 83, 'H', 'micro', style='font-size:12px')
b += foot('any desk can be the helper')
comic('02a-pick-any', 'A sender hands a note to one desk wearing a small helper badge.', B, b)

b = dk(60, 110, 1.2, GREEN) + f'<circle cx="60" cy="78" r="9" fill="{GOLD}" stroke="{INK}" stroke-width="2.5"/>' + t(60, 83, 'H', 'micro')
for i, c in enumerate(ZONES):
    y = 45 + i * 52
    b += (f'<rect x="196" y="{y - 24}" width="100" height="46" rx="6" fill="#cfd8d3" stroke="{INK}" stroke-width="2.5"/>' + dk(246, y + 4, .7, c)
          + arrow(f'M92 {110 + (i - 1) * 12}Q150 {y} 190 {y}', True, 3))
b += foot('3 copies, one per building')
comic('02b-three-copies', 'The helper desk sends three arrows, one to a desk in each of three buildings.', B, b)

b = (kid(34, 80, .9, SAND, 'm-bob') + dk(130, 110, 1.3, GREEN) + thumb(130, 55, 1.3) + t(130, 160, '', 'b-s')
     + dk(235, 90, .8, WOOD) + dk(235, 150, .8, WOOD) + pencil(255, 70, -30, 'm-wiggle') + pencil(255, 130, -30, 'm-wiggle')
     + foot('thumbs-up after just one'))
comic('02c-one-thumbs-up', 'One desk raises a thumbs-up to the sender while two others are still writing.', B, b)

b = (env(100, 24, 0, 1.1) + arrow('M100 40V80', True, 3.5) + dk(100, 100, 1.4, WOOD) + arrow('M100 125V160', True, 3.5)
     + '<rect x="190" y="150" width="110" height="14" fill="#d9b98a" stroke="#322e24" stroke-width="3"/>'
     + folder(215, 128, 40, 30) + folder(260, 128, 40, 30, '#a2c2a7') + foot('writes go all the way to disk', 200))
comic('03a-writes-to-disk', 'A note travels down through a desk and ends in a folder on a shelf.', B, b)

b = (kid(40, 90, .9, SAND, 'm-bob') + '<rect x="14" y="20" width="52" height="30" rx="10" fill="#fff8e3" stroke="#322e24" stroke-width="2"/>' + t(40, 42, '?', 'w')
     + board(120, 40, 150, 100) + arrow('M114 92H78', True, 3)
     + '<rect x="30" y="160" width="260" height="14" fill="#b5ab92" opacity=".5"/>' + folder(80, 150, 40, 28, '#b5ab92') + folder(160, 150, 40, 28, '#b5ab92') + folder(240, 150, 40, 28, '#b5ab92')
     + foot('reads can come from memory', 205))
comic('03b-reads-from-memory', 'A whiteboard answers a question without anyone opening a folder.', B, b)

b = (src() + dk(80, 130, 1.4, WOOD) + notebook(80, 78, .6) + pencil(100, 100, -30, 'm-wiggle') + stopwatch(235, 100, 34)
     + t(235, 160, 'tiny time', 'b-s') + foot('the notebook jot is quick', 206))
comic('03c-notebook', 'A desk quickly scribbles in a notebook with a stopwatch showing a tiny time.', B, b)

b = src()
for x, n, r in zip((55, 160, 265), (48, 96, 144), (20, 28, 36)):
    b += ring(x, 82, r, r * .45, n // 12 + 2, .25) + t(x, 128, f'{n} machines', 'b-s') + t(x, 146, f'{n // 4.8:.0f} clients', 'b-s')
    b += ''.join(kid(x - 30 + j * 22, 175, .4, SAND, 'm-bob', j * .2) for j in range(int(n / 48 * 2)))
comic('04a-three-sizes', 'Three rings of growing size, with senders in growing crowds beside each.', B, b + foot('same test, bigger ring', 214))

b = src() + ring(160, 90, 122, 56, 24, .38) + ''.join(kid(18 + i * 21, 178, .4, SAND, 'm-bob', i * .15) for i in range(15))
b += t(160, 160, '288 machines, 60 clients', 'b-s') + foot('the biggest ring of all', 214)
comic('04b-biggest', 'One huge ring with a very big crowd of senders.', B, b)

pts = [(40 + n * .6, 165 - n * .3) for n in (48, 96, 144, 288)]
b = chart(40, 40, 230, 180, pts)
for (x, y), n in zip(pts, (48, 96, 144, 288)):
    b += t(x, 192, str(n), 'micro')
b += (buddy(270, 150, '', PURPLE, .8, 'm-bob') + '<rect x="238" y="30" width="76" height="56" rx="16" fill="#fff8e3" stroke="#322e24" stroke-width="2"/>'
      '<path d="M275 86L278 112L262 86" fill="#fff8e3" stroke="#322e24" stroke-width="2" stroke-linejoin="round"/>' + t(276, 55, 'still', 'b') + t(276, 75, 'even', 'b') + foot('speed grew in a straight line', 214))
comic('04c-straight-line', 'A chart with four dots on one straight line and a looker saying still even.', B, b)

b = ''
for i, (x, y) in enumerate([(70, 80), (160, 60), (250, 80), (110, 150), (210, 150)]):
    r = 40
    b += (f'<g class="m-bob" style="animation-delay:{i * .3}s"><circle cx="{x}" cy="{y}" r="{r}" fill="#c9e3e2" fill-opacity=".45" stroke="{INK}" stroke-width="2.5"/>'
          f'<path d="M{x - 26} {y - 14}a28 28 0 0 1 14 -14" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/></g>' + dk(x, y + 2, .8, WOOD))
comic('05a-pop-up', 'Desks inside soap bubbles pop into existence for the test, then vanish.', B, src() + b + foot('here for the test, then gone', 212))

b = src() + clock(90, 100, 44, 60) + t(90, 168, '2 hours', 'w-s') + coins(235, 120, 4) + coins(205, 130, 2) + t(220, 168, 'a few hundred dollars', 'b-s') + foot('the whole test, start to finish', 206)
comic('05b-two-hours', 'A clock showing two hours beside a small pile of coins.', B, b)

b = (f'<rect x="20" y="40" width="80" height="110" rx="4" fill="#cfd8d3" stroke="{INK}" stroke-width="3"/><rect x="220" y="40" width="80" height="110" rx="4" fill="#cfd8d3" stroke="{INK}" stroke-width="3"/>'
     + dk(60, 110, .8, TEAL) + dk(260, 110, .8, ORANGE) + arrow('M104 80H214', True, 3.5) + arrow('M216 120H106', True, 3.5)
     + tag(160, 62, '$', -8) + tag(160, 142, '$', 6) + t(60, 30, 'zone A', 'b-s') + t(260, 30, 'zone B', 'b-s')
     + foot('crossing zones costs money', 204))
comic('05c-cross-zone', 'Arrows between two buildings, each with a tiny price tag.', B, b)

b = src()
for x, r, q in zip((60, 150, 250), (22, 30, 44), (False, False, True)):
    b += ring(x, 100, r, r * .4, 6, .24) + f'<path d="M{x - 11} 142l7 8 15 -17" fill="none" stroke="{GREEN}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'
    b += f'<path d="M{x - 11} 142l7 8 15 -17" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity=".6"/>'
b += t(250, 62, '?', 'sfx') + foot('each size was run only once', 208)
comic('06a-one-run', 'A single check mark beside each ring, with a small question mark over the biggest.', B, b)

b = (src() + dk(80, 105, 1.4, WOOD) + tag(80, 60, '1.0', 0).replace('class="micro"', 'class="micro"') + t(80, 160, 'new version', 'b-s')
     + f'<rect x="170" y="45" width="130" height="100" rx="6" fill="#d9e7c9" stroke="{INK}" stroke-width="3"/><path d="M180 130Q220 70 290 60" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="3 6" opacity=".6"/>'
     + ring(235, 100, 28, 14, 6, .2) + f'<path d="M285 50l8 14h-16z" fill="{RED}" stroke="{INK}" stroke-width="1.5"/>' + t(235, 160, 'a faraway region', 'b-s') + foot('next: Cassandra 1.0, more regions', 206))
comic('06b-next', 'A new version tag on a desk and a second ring on a faraway map.', B, b)

b = (src() + buddy(80, 110, '', GREEN, 1.3, 'm-bob') + f'<path d="M120 100H292" stroke="{RED}" stroke-width="5" stroke-linecap="round" marker-end="url(#ah)"/>'
     + stamp(220, 60, 'NETFLIX REPORTS', 150, -5) + t(205, 130, 'a very long straight line', 'b-s') + foot('Netflix’s own view', 206))
comic('06c-takeaway', 'A happy engineer pointing at a very long straight line, with a Netflix reports tag.', B, b)

# =====================================================================
# Fact icons (decorative, 160x100)
# =====================================================================
icon('machines', 'A big ring of desks.', ring(80, 50, 58, 30, 14, .3))
icon('writes', 'One note becoming three notes.', env(30, 50, 0, 1.3) + arrow('M52 50H80', False, 3) + env(112, 24, 0, 1) + env(112, 50, 0, 1) + env(112, 76, 0, 1))
icon('sizes', 'Four rings of growing size.',
     ''.join(ring(x, 55, r, r * .5, k, .15) for x, r, k in ((22, 12, 4), (60, 18, 5), (106, 24, 6), (138, 0, 0))) + ring(138, 55, 0.1, .1, 1, 0.01)[:0])
icon('existing', 'A small ring and a ring six times as large.', ring(30, 50, 18, 9, 5, .2) + arrow('M52 50H72', False, 3) + ring(116, 50, 38, 24, 16, .24))
icon('latency', 'A stopwatch with a quick sliver.', stopwatch(80, 56, 32))
icon('time', 'A clock beside a few coins.', clock(52, 50, 34, 60) + coins(124, 70, 3))

# =====================================================================
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
    wanted = {s for s, _, _ in srcs}
    made = {}
    for rel, vb, title, body in PANELS:
        made[f'{SLUG}/{rel}'] = write(OUT, rel, svg(vb, body, title))
    missing = wanted - set(made)
    assert not missing, f'not drawn: {sorted(missing)}'
    for s, w, h in srcs:
        assert f'viewBox="0 0 {w} {h}"' in made[s].read_text(), f'wrong viewBox for {s}'
    print(f'wrote {len(made)} files to {OUT} ({len(wanted)} required); extra: {sorted(set(made) - wanted)}')
