"""Draws the media for "Cassandra at Twitter Today" (Twitter engineering blog, 2010).

Run from the repo root:  python3 tools/draw_twitter_cassandra_2010.py
Writes standalone SVGs to backups/media/twitter-cassandra-2010/{lead,story,comic,facts}/ (Git recovery copies).
Every media.src in data/seed/papers/twitter-cassandra-2010.json must be written. No logos or brand art: product
names appear only as plain text labels. The post has no numbers, so nothing numeric is drawn except the "3" count.
"""
import json
import re
from pathlib import Path

from media_kit import COMIC_CSS, COMIC_DEFS, INK, RED, anim, bubble, buddy, standalone, t, write

ROOT = Path(__file__).resolve().parent.parent
SLUG = 'twitter-cassandra-2010'
OUT = ROOT / 'backups' / 'media' / SLUG
SEED = ROOT / 'data' / 'seed' / 'papers' / f'{SLUG}.json'

TEAL, GREEN, GOLD, WOOD, PAPER = '#377675', '#a2c2a7', '#ffe597', '#d9b98a', '#fff8e3'
PURPLE, SAND, ORANGE, GREY, SKY = '#c3b2d8', '#f7d79b', '#efae78', '#b5ab92', '#82acad'

DEFS = COMIC_DEFS + (f'<marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
                     f'<path d="M0 0L10 5L0 10Z" fill="{RED}"/></marker>')
EXTRA = '.rise{animation:ri 4s ease-in-out infinite alternate}@keyframes ri{to{transform:translateY(-6px)}}'


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
    return standalone(vb, body, title, css=prune_css(COMIC_CSS + EXTRA, body), defs=DEFS if 'ah)' in body else COMIC_DEFS)


def bg(color, w, h, body):
    return f'<rect width="{w}" height="{h}" fill="{color}"/><rect width="{w}" height="{h}" fill="url(#dots)" opacity=".22"/>{body}'


def stamp(x, y, s='ILLUSTRATION', anchor='middle'):
    return t(x, y, s, 'micro', anchor, f'fill:{RED}')


# ---------- pieces ----------
def card(x, y, w=26, h=18, c=PAPER, rot=0):
    return (f'<g transform="translate({x:.0f} {y:.0f}) rotate({rot})" stroke="{INK}" stroke-width="1.8" stroke-linejoin="round">'
            f'<rect x="{-w / 2:g}" y="{-h / 2:g}" width="{w}" height="{h}" rx="2" fill="{c}"/>'
            f'<path d="M{-w / 2 + 4:g} {-h / 2 + 6:g}h{w - 8:g}M{-w / 2 + 4:g} {-h / 2 + 11:g}h{w * .5:g}" stroke-width="1.5" opacity=".55" fill="none"/></g>')


def shelf(x, y, w, h, label, cols, rows, fill=WOOD, stuffed=True, cls='w-s'):
    g = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="{INK}" stroke-width="3"/>'
         f'<rect x="{x + 8}" y="{y + 26}" width="{w - 16}" height="{h - 34}" fill="#8a7458" stroke="{INK}" stroke-width="2"/>'
         f'<rect x="{x + w / 2 - 40}" y="{y + 4}" width="80" height="20" rx="3" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>'
         + t(x + w / 2, y + 20, label, cls))
    rh = (h - 34) / rows
    for r in range(1, rows):
        g += f'<path d="M{x + 8} {y + 26 + r * rh:.0f}h{w - 16}" stroke="{INK}" stroke-width="2.5"/>'
    if stuffed:
        cw = (w - 16) / cols
        for r in range(rows):
            for c in range(cols):
                g += card(x + 8 + cw * (c + .5), y + 26 + rh * (r + .5) + 4, min(cw - 6, 30), min(rh - 12, 20), [PAPER, SAND, '#e8f3f0'][(r + c) % 3], (c * 7 % 5) - 2)
    return g


def folder(x, y, w=50, h=36, color=SAND, label=''):
    g = (f'<g transform="translate({x} {y})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round">'
         f'<path d="M{-w / 2} {-h / 2 + 4}h18l6 -6h{w - 24}v{h}h{-w}Z" fill="{color}"/>')
    if label:
        g += t(0, 5, label, 'micro', style='stroke:none')
    return g + '</g>'


def pin(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round">'
            f'<path d="M0 22C-14 4 -14 -8 0 -12C14 -8 14 4 0 22Z" fill="{RED}"/><circle cx="0" cy="-2" r="4.5" fill="{PAPER}"/></g>')


def lens(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="3.5" stroke-linecap="round">'
            f'<circle r="11" fill="#e8f3f0"/><path d="M8 8L19 19" stroke-width="6"/></g>')


def bars(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2.2">'
            f'<rect x="-14" y="2" width="9" height="12" fill="{GREEN}"/><rect x="-3" y="-8" width="9" height="22" fill="{TEAL}"/>'
            f'<rect x="8" y="-16" width="9" height="30" fill="{ORANGE}"/></g>')


def plant(x, y, s=1, tall=False):
    th = 34 if tall else 20
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M-14 0h28l-4 26h-20Z" fill="{ORANGE}"/><path d="M0 0V{-th}" fill="none"/>'
            f'<path d="M0 {-th * .5:g}q-16 -4 -18 -14q14 -2 18 14Zm0 {-th * .3:g}q16 -2 18 -14q-14 -2 -18 14Z" fill="{GREEN}"/></g>')


def can_water(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round">'
            f'<rect x="-14" y="-10" width="28" height="22" rx="3" fill="{SKY}"/><path d="M14 -2L30 -14M-14 -2q-12 -4 -14 6" fill="none"/></g>')


def truck(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round">'
            f'<rect x="-48" y="-30" width="62" height="40" rx="3" fill="{SAND}"/><path d="M14 -18h22l12 14v14H14Z" fill="{ORANGE}"/>'
            f'<circle cx="-28" cy="12" r="9" fill="{INK}"/><circle cx="30" cy="12" r="9" fill="{INK}"/></g>')


def mbox(x, y, s=1, sign='', rot=0):
    g = (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round">'
         f'<rect x="-34" y="-22" width="68" height="44" fill="#d9b98a"/><path d="M-34 -10h68M-8 -22v12M8 -22v12" fill="none" stroke-width="2"/>')
    if sign:
        g += f'<rect x="-31" y="2" width="62" height="17" fill="{PAPER}" stroke-width="2"/>' + t(0, 15, sign, 'micro', style='stroke:none')
    return g + '</g>'


def desk(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round">'
            f'<path d="M-30 8v22M30 8v22" fill="none" stroke-width="3"/><rect x="-40" y="-6" width="80" height="15" rx="3" fill="{WOOD}"/>'
            f'<rect x="-14" y="-24" width="28" height="18" rx="2" fill="{PAPER}"/><path d="M-9 -17h18" opacity=".5" fill="none"/></g>')


def arrow(d):
    return f'<path d="{d}" fill="none" stroke="{RED}" stroke-width="3.5" stroke-linecap="round" stroke-dasharray="8 7" marker-end="url(#ah)" class="m-flow"/>'


def floor(y, w, h):
    return f'<rect y="{y}" width="{w}" height="{h - y}" fill="#e3d4b0"/><path d="M0 {y}H{w}" stroke="{INK}" stroke-width="2.5"/>'


PANELS = []


def add(kind, name, vb, title, color, body):
    w, h = map(int, vb.split()[2:])
    PANELS.append((f'{kind}/{name}.svg', vb, title, bg(color, w, h, body)))


C, S, L, F = '0 0 320 220', '0 0 440 215', '0 0 600 340', '0 0 160 100'

# ================= lead =================
b = floor(255, 600, 340) + shelf(30, 70, 300, 195, 'MySQL', 5, 3) + shelf(385, 110, 190, 155, 'new shelf', 3, 1, stuffed=False, cls='w-s')
for i, (fx, ic) in enumerate([(425, pin(425, 193)), (480, lens(476, 190)), (535, bars(535, 193))]):
    b += folder(fx, 222, 44, 34, [SAND, GREEN, PURPLE][i]) + ic
b += t(180, 45, 'TWEETS STAY HERE', 'micro', style=f'fill:{RED}') + t(480, 92, 'OTHER JOBS', 'micro', style=f'fill:{RED}')
b += buddy(350, 292, 'Eng', ORANGE, .9, 'm-bob', label_cls='w-s') + stamp(120, 300)
add('lead', 'two-shelves', L, 'Two shelves: tweets stay on the big MySQL shelf; a new shelf holds other jobs.', '#cfdcc9', b)

b = floor(255, 600, 340) + shelf(340, 60, 240, 205, 'MySQL', 4, 3)
b += buddy(130, 215, 'Eng', ORANGE, 1.5, label_cls='w') + f'<g{anim("rise")}>' + mbox(255, 238, 1.2, 'not now') + '</g>'
b += bubble(40, 40, 190, 52, ['Not now.', 'Box stays down.'], (120, 160), 'b')
b += t(300, 300, 'NOT NOW', 'sfx', style='') + stamp(300, 328)
add('lead', 'not-now', L, 'An engineer sets a moving box labeled not now down beside the MySQL shelf.', '#e9d9bd', b)

# ================= story =================
b = floor(165, 440, 215) + shelf(300, 40, 120, 125, 'MySQL', 4, 3) + shelf(205, 80, 80, 85, 'Cass.', 2, 1, stuffed=False, cls='w-s') + desk(80, 150, 1)
b += buddy(80, 108, 'Eng', ORANGE, 1, 'm-bob', label_cls='w-s') + bubble(20, 6, 120, 38, ['Wait, what?'], (70, 80), 'b')
b += f'<g{anim("m-pulse")}>' + t(172, 36, '?', 'sfx', style='') + '</g>' + stamp(220, 200)
add('story', '01-misunderstandings', S, 'An engineer wonders what is going on, with a small and a big shelf behind.', '#d7e2dc', b)

b = floor(180, 440, 215) + shelf(100, 40, 240, 140, 'Cassandra', 3, 1, stuffed=False)
for i, (fx, ic, lb, col) in enumerate([(150, pin(150, 148, .9), 'places', SAND), (220, lens(214, 146, .9), 'research', GREEN), (290, bars(290, 148, .9), 'charts', PURPLE)]):
    b += folder(fx, 150, 56, 40, col) + ic + t(fx, 192, lb, 'micro')
b += stamp(220, 208)
add('story', '02-new-jobs', S, 'A Cassandra shelf with three folders: places, research, charts.', '#d9d2e6', b)

b = floor(170, 440, 215) + shelf(40, 30, 210, 140, 'MySQL', 4, 3) + truck(370, 150, 1) + buddy(300, 120, 'Eng', ORANGE, 1, label_cls='w-s')
b += f'<g{anim("m-wiggle")}><path d="M268 105l-22 -8" stroke="{INK}" stroke-width="3" stroke-linecap="round"/></g>' + t(330, 60, 'NO THANKS', 'sfx-s', style='') + stamp(220, 205)
add('story', '03-keep-mysql', S, 'A person waves a moving truck away from the MySQL shelf.', '#ecdcc0', b)

b = f'<rect x="70" y="20" width="150" height="175" rx="4" fill="{PAPER}" stroke="{INK}" stroke-width="3"/>'
for i in range(4):
    y = 55 + i * 34
    b += f'<path d="M110 {y}h90" stroke="{INK}" stroke-width="3" opacity=".55" stroke-linecap="round"/><path d="M85 {y - 3}l7 7 12 -14" fill="none" stroke="{TEAL}" stroke-width="4" stroke-linecap="round"/>'
b += f'<rect x="260" y="40" width="130" height="110" fill="#fbfaf0" stroke="{INK}" stroke-width="3"/><path d="M275 60V135H380" fill="none" stroke="{INK}" stroke-width="3"/>'
b += t(325, 175, 'no tests,', 'b-s') + t(325, 193, 'no chart', 'b-s') + t(145, 14, 'FROM THE SOURCE', 'micro', style=f'fill:{RED}')
add('story', '04-evidence', S, 'A page with four checked lines beside an empty chart frame.', '#f0e3c6', b)

# ================= comic =================
b = floor(180, 320, 220) + shelf(70, 40, 180, 140, 'Cassandra', 3, 1, stuffed=False)
for i, (fx, lb, col) in enumerate([(115, 'places', SAND), (160, 'research', GREEN), (205, 'analytics', PURPLE)]):
    b += f'<path d="M{fx + 10} 66v22" stroke="{INK}" stroke-width="2"/><rect x="{fx - 26}" y="88" width="72" height="22" rx="3" fill="{col}" stroke="{INK}" stroke-width="2" transform="rotate({(-3, 2, -2)[i]} {fx + 10} 99)"/>' + t(fx + 10, 104, lb, 'micro')
b += buddy(285, 160, '', ORANGE, .8) + stamp(160, 208)
add('comic', '01a-three-jobs', C, 'A Cassandra shelf with three signs hanging from it.', '#d9e2d2', b)

b = floor(185, 320, 220) + shelf(160, 60, 140, 125, 'Cassandra', 2, 1, stuffed=False) + pin(60, 55, 1.4) + lens(60, 125, 1.3)
b += f'<g{anim("m-feed")}>' + folder(100, 60, 40, 30, SAND) + '</g>' + f'<g{anim("m-feed", 1.2)}>' + folder(100, 125, 40, 30, GREEN) + '</g>'
b += folder(205, 150, 44, 32, SAND) + folder(255, 150, 44, 32, GREEN) + bubble(155, 8, 120, 34, ['top tweets'], (110, 125), 'b-s') + stamp(160, 210)
add('comic', '01b-places-research', C, 'A map pin and a magnifying glass drop folders onto the shelf.', '#f0e3c6', b)

b = f'<rect x="85" y="25" width="150" height="100" rx="6" fill="#26332f" stroke="{INK}" stroke-width="3"/>'
for i, hgt in enumerate([30, 50, 40, 68]):
    b += f'<g class="m-fill" style="animation-delay:{i * .3}s"><rect x="{105 + i * 33}" y="{110 - hgt}" width="22" height="{hgt}" fill="{[GREEN, SAND, ORANGE, '#e8f3f0'][i]}"/></g>'
b += floor(190, 320, 220) + buddy(55, 160, '', GREEN, .9) + buddy(160, 160, '', SAND, .9) + buddy(265, 160, '', PURPLE, .9) + stamp(160, 210)
add('comic', '01c-analytics', C, 'Three people building a live bar chart on a big screen.', '#d4dde3', b)

b = floor(185, 320, 220) + shelf(70, 10, 180, 175, 'MySQL', 5, 4) + stamp(160, 208) + buddy(285, 160, '', ORANGE, .8)
add('comic', '02a-tweet-pile', C, 'A tall stack of tweet cards on a MySQL shelf.', '#ecdcc0', b)

b = floor(185, 320, 220) + shelf(160, 50, 150, 135, 'MySQL', 4, 3) + f'<g{anim("m-bob")}>'
b += f'<path d="M20 60h60l25 18" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/><rect x="18" y="35" width="52" height="24" rx="4" fill="{PAPER}" stroke="{INK}" stroke-width="2.5"/>' + t(44, 52, 'Cass.', 'micro') + '</g>'
b += f'<path d="M110 185V138" stroke="{INK}" stroke-width="5"/><rect x="84" y="96" width="52" height="40" rx="6" fill="{RED}" stroke="{INK}" stroke-width="2.5"/>' + t(110, 122, 'STOP', 'micro', style='fill:#fff8e3') + f'<circle cx="110" cy="150" r="9" fill="{ORANGE}" stroke="{INK}" stroke-width="2.5"/>' + stamp(160, 208)
add('comic', '02b-no-move', C, 'A robot arm with a Cassandra tag reaches for the pile; a hand holds a stop sign.', '#e9d9bd', b)

b = floor(185, 320, 220) + shelf(80, 45, 160, 140, 'MySQL', 4, 3) + f'<g{anim("m-wiggle")}>' + f'<g transform="translate(270 130) rotate(-30)" stroke="{INK}" stroke-width="2.5"><rect x="-26" y="-6" width="52" height="12" rx="6" fill="{GREY}"/></g></g>'
b += buddy(40, 160, '', GREEN, .8) + t(160, 28, 'tidy and keep', 'b') + stamp(160, 208)
add('comic', '02c-maintain', C, 'A worker tidies the MySQL shelf with a little wrench.', '#d9e2d2', b)

b = floor(180, 320, 220) + f'<path d="M150 180V90L220 40L290 90V180Z" fill="{SAND}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/><rect x="205" y="130" width="30" height="50" fill="#8a7458" stroke="{INK}" stroke-width="2.5"/>'
b += ''.join(mbox(120 + (i % 2) * 8, 165 - i * 22, .7) for i in range(3)) + buddy(45, 148, '', ORANGE, .7) + t(160, 18, 'a whole house', 'b') + stamp(160, 208)
add('comic', '03a-big-move', C, 'A tiny person stares at a huge house with boxes piled around it.', '#ecdcc0', b)

b = f'<rect x="30" y="25" width="100" height="110" rx="5" fill="{PAPER}" stroke="{INK}" stroke-width="3"/><rect x="30" y="25" width="100" height="26" fill="{RED}" stroke="{INK}" stroke-width="3"/>' + t(80, 112, '?', 'sfx', style='')
b += f'<ellipse cx="225" cy="85" rx="72" ry="48" fill="{PAPER}" stroke="{INK}" stroke-width="3"/><circle cx="150" cy="140" r="7" fill="{PAPER}" stroke="{INK}" stroke-width="2.5"/><circle cx="136" cy="156" r="4" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>'
b += mbox(225, 85, .9) + f'<path d="M190 55L260 115M260 55L190 115" stroke="{RED}" stroke-width="7" stroke-linecap="round"/>' + t(160, 190, 'not the time', 'b') + stamp(160, 210)
add('comic', '03b-not-the-time', C, 'A calendar page and a thought bubble with a moving box crossed out.', '#d4dde3', b)

b = floor(185, 320, 220) + f'<rect x="100" y="30" width="120" height="155" rx="4" fill="#8a7458" stroke="{INK}" stroke-width="3"/><circle cx="205" cy="115" r="5" fill="{GOLD}" stroke="{INK}" stroke-width="2"/>'
b += f'<rect x="114" y="52" width="92" height="46" rx="4" fill="{PAPER}" stroke="{INK}" stroke-width="2.5"/>' + t(160, 72, 'this isn\'t', 'b-s') + t(160, 90, 'the time', 'b-s') + stamp(160, 208)
add('comic', '03c-only-reason', C, 'One sign on a door reading: this isn\'t the time. No other signs.', '#f0e3c6', b)

b = floor(185, 320, 220) + shelf(40, 15, 140, 170, 'Cassandra', 2, 1, stuffed=False)
for i in range(3):
    b += f'<rect x="{205 + i * 38}" y="{140 - i * 6}" width="34" height="40" rx="3" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="6 5"/>' + t(222 + i * 38, 166 - i * 6, 'new', 'micro')
b += f'<g{anim("m-feed")}>' + folder(110, 120, 44, 32, GREEN) + '</g>' + t(250, 28, 'new projects', 'b') + stamp(160, 208)
add('comic', '04a-new-projects', C, 'A row of blank project boxes in front of the Cassandra shelf.', '#d9d2e6', b)

b = floor(185, 320, 220) + f'<path d="M20 120h90M210 120h90" stroke="{INK}" stroke-width="8"/><path d="M20 130h90M210 130h90" stroke="{INK}" stroke-width="3" opacity=".5"/>'
b += f'<g{anim("m-bob")}><rect x="110" y="112" width="100" height="14" fill="{WOOD}" stroke="{INK}" stroke-width="2.5" stroke-dasharray="8 6"/></g>' + t(160, 100, 'new project', 'b-s') + t(160, 160, 'big data store plank', 'b-s') + t(160, 30, 'needs a big store', 'b') + stamp(160, 208)
add('comic', '04b-needs-big-store', C, 'A bridge labeled new project cannot be finished until a big store plank is laid.', '#e9d9bd', b)

b = floor(185, 320, 220) + plant(130, 130, 1.5, True) + can_water(235, 70, 1.2) + f'<g{anim("m-flow")}><path d="M205 78l-20 40" stroke="{SKY}" stroke-width="3" fill="none"/></g>'
b += f'<path d="M150 186h120l-50 -12Z" fill="{INK}" opacity=".22"/>' + t(130, 126, 'Cassandra', 'micro') + t(160, 30, 'around a long time', 'b') + stamp(160, 208)
add('comic', '04c-long-time', C, 'A small plant labeled Cassandra gets watered and has a taller shadow.', '#d9e2d2', b)

# ================= facts =================
SRC = lambda: t(80, 94, 'From the source · reported', 'micro')
b = card(60, 45, 56, 38, PAPER) + folder(110, 52, 40, 30, GREEN, 'Cass.') + f'<path d="M30 20L145 78M145 20L30 78" stroke="{RED}" stroke-width="6" stroke-linecap="round"/>'
add('facts', 'not-for-tweets', F, 'A tweet card with a cross over a Cassandra tag.', '#f0e3c6', b)
b = shelf(35, 8, 90, 70, 'MySQL', 3, 2) + f'<path d="M110 60l10 12 24 -30" fill="none" stroke="{TEAL}" stroke-width="7" stroke-linecap="round"/>'
add('facts', 'mysql-stays', F, 'A shelf labeled MySQL with a check mark.', '#f0e3c6', b)
b = f'<rect x="14" y="40" width="132" height="44" rx="3" fill="{WOOD}" stroke="{INK}" stroke-width="2.5"/>' + folder(40, 62, 36, 28, SAND) + folder(80, 62, 36, 28, GREEN) + folder(120, 62, 36, 28, PURPLE) + pin(40, 24, .55) + lens(76, 24, .6) + bars(120, 26, .6)
add('facts', 'three-uses', F, 'A shelf with three folders: a map pin, a magnifying glass, a bar chart.', '#f0e3c6', b)
b = plant(60, 40, .9, True) + can_water(115, 30, .8) + f'<path d="M104 38l-12 22" stroke="{SKY}" stroke-width="3" stroke-dasharray="4 4"/>'
add('facts', 'every-day', F, 'A plant in a pot with a watering can.', '#f0e3c6', b)


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
    made = {rel: write(OUT, rel, svg(vb, body, title)) for rel, vb, title, body in PANELS}
    for s, w, h in srcs:
        rel = s.replace(SLUG + '/', '', 1)
        assert rel in made, f'not drawn: {rel}'
        assert f'viewBox="0 0 {w} {h}"' in made[rel].read_text(), f'wrong viewBox for {rel}'
    print(f'wrote {len(made)} files to {OUT} ({len(srcs)} required)')
