"""Draws the media for "How Discord Stores Billions of Messages" (Discord blog, 2017).

Run from the repo root:  python3 tools/draw_discord_billions.py
Writes standalone SVGs to backups/media/discord-billions/{lead,story,comic,facts}/. Every media.src in
data/seed/papers/discord-billions.json must be written. Helpers are reused from draw_cassandra.py.
"""
import json
import xml.dom.minidom
from pathlib import Path

from draw_cassandra import (CREAM, GREEN, GREY, ORANGE, PAPER, PURPLE, SAND, TEAL, GOLD, WOOD,
                            board, desk, envelope, folder, meter, panel_bg, ring, ring_pts, svg)
from media_kit import INK, RED, anim, buddy, t, write

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'backups' / 'media' / 'discord-billions'
SEED = ROOT / 'data' / 'seed' / 'papers' / 'discord-billions.json'
SRC = 'From the source · reported'
PANELS = {}
S = f'stroke="{INK}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"'


def put(rel, w, h, title, bg, body):
    PANELS[rel] = (f'0 0 {w} {h}', title, panel_bg(bg, body, w, h))


def lab(x, y, s, cls='w-s', anchor='middle', fill=None):
    return t(x, y, s, cls, anchor, f'fill:{fill}' if fill else '')


def src(x=8, y=214, two=False):
    if two:
        return t(x, y - 14, 'From the source', 'micro', 'start', f'fill:{RED}') + t(x, y, '· reported', 'micro', 'start', f'fill:{RED}')
    return t(x, y, SRC, 'micro', 'start', f'fill:{RED}')


def slip(x, y, w=34, h=44, rot=0, fill=PAPER, lines=2, tab=True):
    g = f'<g transform="translate({x} {y}) rotate({rot})" {S}><rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" rx="2" fill="{fill}"/>'
    if tab:
        g += f'<rect x="{-w/2+4}" y="{-h/2+4}" width="{w*.4:.0f}" height="6" fill="{TEAL}" stroke-width="1"/>'
    for i in range(lines):
        g += f'<path d="M{-w/2+5} {-h/2+17+i*8}h{w-10}" stroke-width="1.5" opacity=".5"/>'
    return g + '</g>'


def flag(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})"><path d="M0 0V-22" stroke="{INK}" stroke-width="2.5" stroke-linecap="round"/>'
            f'<path d="M0 -22L15 -17L0 -11Z" fill="{RED}" stroke="{INK}" stroke-width="1.5" stroke-linejoin="round"/>'
            f'<path d="M4 -17l5 3m0 -3l-5 3" stroke="{PAPER}" stroke-width="1.2"/></g>')


def bub(x, y, w=44, h=28, fill=PAPER, rot=0):
    return (f'<g transform="translate({x} {y}) rotate({rot})" {S}><rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" rx="9" fill="{fill}"/>'
            f'<path d="M{-w/2+8} {h/2-1}l-4 8l13 -8" fill="{fill}"/><path d="M{-w/2+9} -4h{w-18}M{-w/2+9} 4h{w*.5:.0f}" stroke-width="1.8" opacity=".5"/></g>')


def cal(x, y, n, cw=14, ch=14, color=SAND, hl=None):
    g = ''
    for i in range(n):
        g += f'<rect x="{x+i*cw}" y="{y}" width="{cw}" height="{ch}" fill="{GOLD if i == hl else color}" stroke="{INK}" stroke-width="1.5"/>'
    return g


def clock(x, y, r=26, hand=-60):
    return (f'<g transform="translate({x} {y})" {S}><circle r="{r}" fill="{PAPER}" stroke-width="3"/>'
            f'<path d="M0 0V{-r+7}" /><path d="M0 0L{r*.6:.0f} {-r*.3:.0f}" stroke="{RED}"/><circle r="2.5" fill="{INK}"/></g>')


def form(x, y, n=16, filled=4, cell=17, flags=True):
    g = ''
    for i in range(n):
        cx, cy = x + (i % 4) * (cell + 3), y + (i // 4) * (cell + 3)
        f = i < filled
        g += f'<rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" fill="{GREEN if f else PAPER}" stroke="{INK}" stroke-width="1.8"/>'
        if f:
            g += f'<path d="M{cx+4} {cy+9}l4 4 6 -8" fill="none" stroke="{INK}" stroke-width="2"/>'
        elif flags:
            g += flag(cx + 6, cy + cell - 2, .5)
    return g


def zig(x, y, w):  # lightning-style crack
    return f'<path d="M{x} {y}l{w/4:.0f} 10l-{w/6:.0f} 8l{w/4:.0f} 10" fill="none" stroke="{RED}" stroke-width="3" stroke-linecap="round"/>'


def ringdesks(cx, cy, rx, ry, n, s, dark=None, tops=None):
    g = ring(cx, cy, rx, ry, 2.5)
    cols = tops or [WOOD, '#c9d9c8', PURPLE, SAND, ORANGE, GREEN, WOOD, SAND, GREEN, PURPLE, ORANGE, '#c9d9c8']
    for i, (x, y) in enumerate(ring_pts(cx, cy, rx, ry, n, -90)):
        g += desk(x, y, s, cols[i % len(cols)], dark=(i == dark))
    return g


def tick(x, y, s=1):
    return f'<path d="M{x} {y}l{8*s:g} {8*s:g}l{16*s:g} -{18*s:g}" fill="none" stroke="#2f7d4f" stroke-width="{4*s:g}" stroke-linecap="round" stroke-linejoin="round"/>'


def wallboard(x, y, w, h, notes, cols=4, rot=None):
    g = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="#fbfaf0" stroke="{INK}" stroke-width="3"/>'
    cw, chh = (w - 12) / cols, 22
    for i in range(notes):
        nx, ny = x + 6 + (i % cols) * cw, y + 8 + (i // cols) * (chh + 6)
        g += (f'<rect x="{nx:.0f}" y="{ny:.0f}" width="{cw-5:.0f}" height="{chh}" fill="{[SAND, GREEN, PURPLE, ORANGE][i % 4]}" stroke="{INK}" stroke-width="1.6"/>'
              f'<path d="M{nx+4:.0f} {ny+9:.0f}h{cw-14:.0f}" stroke="{INK}" stroke-width="1.4" opacity=".5"/>')
    return g


# ============================== lead plates ==============================
def plate(name, title, bg, tag, body, caption):
    put(f'lead/{name}.svg', 600, 340, title, bg, body
        + f'<rect x="10" y="288" width="580" height="44" fill="{CREAM}" {S}/>' + t(300, 317, caption, 'b') + t(22, 28, tag, 'micro', 'start', f'fill:{RED}')
        + f'<path d="M8 10Q300 5 592 9Q596 170 591 332Q300 336 9 331Q4 170 8 10Z" fill="none" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>')


b = ''
for i in range(14):
    b += f'<g{anim("m-bob", i * .12)}>' + bub(60 + (i % 7) * 60 + (i // 7) * 24, 50 + (i // 7) * 46 + (i % 3) * 8, 50, 30, [PAPER, SAND, GREEN][i % 3], -14 + (i * 23) % 28) + '</g>'
b += (f'<path d="M300 150V196" stroke="{RED}" stroke-width="4" stroke-dasharray="8 7" class="m-flow" fill="none"/>'
      + wallboard(190, 205, 220, 70, 8, 4) + buddy(500, 236, 'help', ORANGE, 1.1) + f'<path d="M472 190q-26 -20 -40 -55" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="3 6"/>'
      + t(470, 120, 'too many!', 'sfx-s', 'middle'))
plate('message-flood', 'A tall pile of chat bubbles drops onto a small, already full whiteboard.', '#efd5b7', 'PLATE 01 / THE PILE', b, 'Every message is kept forever, so the pile only grows.')

cx, cy = 300, 160
b = ringdesks(cx, cy, 190, 78, 6, 1.3, tops=[WOOD, '#c9d9c8', PURPLE, SAND, ORANGE, GREEN])
for i, (x, y) in enumerate(ring_pts(cx, cy, 190, 78, 6, -90)):
    b += folder(x + 36, y + 4, 22, 16, [SAND, GREEN, PURPLE][i % 3]) + f'<rect x="{x-44}" y="{y-12}" width="14" height="18" fill="{PAPER}" {S}/>'
b += f'<g{anim("m-bob")}>' + bub(cx + 190, 52, 52, 32, SAND, 8) + '</g>' + buddy(cx + 232, 168, 'hi!', GREEN, .9, 'm-hop') + lab(cx, cy + 6, 'ONE MORE DESK?', 'w-s')
plate('ring-of-desks', 'A ring of desks with notebooks, whiteboards and folders. A new bubble lands on one desk.', '#b8cec0', 'PLATE 02 / THE RING', b, 'A ring of desks that can always take one more.')

# ============================== story panels ==============================
def story(name, title, bg, body):
    put(f'story/{name}.svg', 440, 215, title, bg, body)


story('01-whiteboard-full', 'A small whiteboard crammed with notes, some falling off. A worker frowns.', '#efd5b7',
      wallboard(40, 36, 200, 110, 12, 4) + lab(140, 28, '100 million messages', 'micro', fill=INK)
      + ''.join(f'<g{anim("m-feed", i * .5)}>' + slip(250 + i * 6, 70 + i * 22, 24, 18, 20 - i * 10, SAND, 1, False) + '</g>' for i in range(3))
      + buddy(350, 150, 'hmm', ORANGE, 1.1)
      + ''.join(slip(405, 150 - i * 5, 30, 22, i * 6 - 6, [PAPER, GREEN, SAND][i], 1, False) for i in range(3)) + src(8, 205))

story('02-checklist', 'A pinned checklist with four ticks beside a ring of desks.', '#c9d9c8',
      f'<rect x="28" y="24" width="190" height="168" rx="4" fill="{PAPER}" {S}/><circle cx="123" cy="24" r="6" fill="{RED}" {S}/>'
      + ''.join(f'<rect x="44" y="{52+i*34}" width="20" height="20" fill="#fff" stroke="{INK}" stroke-width="2"/>' + tick(46, 62 + i * 34, .6) + lab(76, 69 + i * 34, w, 'b', 'start')
                for i, w in enumerate(['Grows', 'Heals', 'Low upkeep', 'Steady speed']))
      + ringdesks(335, 108, 80, 56, 6, .75) + lab(335, 112, 'ring', 'w-s'))

story('03-ten-day-folders', 'One long folder is cut into short folders with calendar strips.', '#f0e3c6',
      folder(62, 100, 100, 50, SAND) + lab(62, 106, '100MB+', 'micro', fill=INK) + zig(58, 84, 40)
      + f'<path d="M118 100h44" fill="none" stroke="{RED}" stroke-width="3.5" stroke-dasharray="8 7" class="m-flow"/>'
      + ''.join(folder(205 + i * 56, 100, 46, 40, [SAND, GREEN, PURPLE, ORANGE][i]) + cal(185 + i * 56, 132, 3, 13, 10, SAND, 2 if i == 3 else None) for i in range(4))
      + lab(395, 62, 'newest', 'w-s') + f'<path d="M395 68v14" stroke="{RED}" stroke-width="3" fill="none"/>' + buddy(370, 175, 'new!', GOLD, .8)
      + lab(300, 30, 'a new folder every 10 days', 'b') + src(8, 205))

story('04-evidence', 'A stopwatch beside a worry meter that swings high, and a stack of delete markers.', '#c9d9c8',
      f'<g {S}><circle cx="82" cy="100" r="42" fill="{PAPER}" stroke-width="3"/><rect x="72" y="46" width="20" height="9" fill="{GREY}"/><path d="M82 100V72" stroke-width="3"/><path d="M82 100l14 8" stroke="{RED}" stroke-width="3"/></g>'
      + lab(82, 170, 'writes &lt; 1 ms', 'mono-s') + lab(82, 188, 'reads &lt; 5 ms', 'mono-s')
      + meter(250, 130, 62, 52) + lab(250, 160, '6 months later:', 'micro', fill=INK) + lab(250, 176, 'channel stalls', 'micro', fill=INK)
      + desk(380, 150, 1.1, WOOD) + ''.join(flag(358 + i * 12, 106 + (i % 2) * 4, .9) for i in range(5)) + src(8, 205))

# ============================== comic panels ==============================
def comic(name, title, bg, body):
    put(f'comic/{name}.svg', 320, 220, title, bg, body)


comic('01a-mongo-start', 'A single whiteboard with a few notes. A worker smiles and sticks one more on.', '#f0e3c6',
      wallboard(30, 30, 150, 90, 4, 3) + buddy(240, 150, 'ok!', GREEN, 1.1) + slip(190, 112, 24, 18, -10, SAND, 1, False) + lab(105, 150, 'one old database', 'b'))
comic('01b-board-full', 'A whiteboard covered with notes. A worker holds one more with nowhere to put it.', '#efd5b7',
      wallboard(24, 24, 180, 130, 15, 4) + lab(114, 176, '100 million', 'w') + buddy(260, 140, 'hmm', ORANGE, 1.05) + slip(256, 178, 32, 22, 8, SAND, 1, False) + src(8, 212))
comic('01c-unpredictable', 'A worry meter swinging low and high. A worker shrugs by a box labeled new database.', '#c3b2d8',
      meter(110, 120, 70, 52) + f'<path d="M110 120L55 85" stroke="{INK}" stroke-width="3" opacity=".25" stroke-linecap="round"/>' + lab(110, 150, 'speed? who knows', 'b')
      + f'<g {S}><path d="M205 120l30 -14l50 0l-20 14z" fill="#e4c898"/><rect x="205" y="120" width="60" height="50" fill="#d9b98a"/><path d="M265 120l20 -14v50l-20 14z" fill="#c6a375"/></g>'
      + lab(235, 150, 'new', 'micro', fill=INK) + lab(235, 163, 'database', 'micro', fill=INK) + buddy(250, 200, 'meh', GREEN, .7))
comic('02a-add-desks', 'A ring of desks with one new desk wheeled in; the ring stretches to include it.', '#c9d9c8',
      ringdesks(120, 110, 90, 62, 5, .9) + f'<g>' + desk(262, 120, 1.1, GOLD, badge=True) + '</g>'
      + f'<g {S}><circle cx="248" cy="148" r="6" fill="{GREY}"/><circle cx="276" cy="148" r="6" fill="{GREY}"/></g>'
      + f'<path d="M240 110Q205 100 195 112" fill="none" stroke="{RED}" stroke-width="3.5" stroke-dasharray="8 7" class="m-flow"/>' + lab(160, 200, 'add a desk, no fuss', 'b'))
comic('02b-self-heal', 'One desk goes dark and its neighbours cover for it. A worker sleeps happily.', '#b8cec0',
      ringdesks(130, 108, 100, 62, 5, .9, dark=0) + f'<path d="M95 70Q112 52 130 56M165 70Q148 52 130 56" fill="none" stroke="{RED}" stroke-width="3" stroke-dasharray="8 7" class="m-flow"/>'
      + buddy(262, 150, 'zzz', GREEN, .95) + lab(262, 190, 'sleeps well', 'b') + lab(130, 30, 'this desk is dark', 'micro', fill=INK))
comic('02c-all-ticks', 'A checklist with every box ticked and a ring of desks with a green tick.', '#f0e3c6',
      f'<rect x="20" y="24" width="140" height="150" rx="4" fill="{PAPER}" {S}/>'
      + ''.join(f'<rect x="34" y="{40+i*34}" width="18" height="18" fill="#fff" stroke="{INK}" stroke-width="2"/>' + tick(36, 50 + i * 34, .55) + f'<path d="M62 {50+i*34}h70" stroke="{INK}" stroke-width="2.5" opacity=".4"/>' for i in range(4))
      + ringdesks(240, 100, 62, 46, 5, .65) + tick(222, 106, 1.3) + lab(240, 190, 'all four!', 'w'))
comic('03a-one-folder', 'A desk with one folder labeled with a channel name, stuffed with message slips.', '#f0e3c6',
      desk(160, 150, 2.2, WOOD) + folder(160, 88, 90, 56, SAND) + ''.join(slip(130 + i * 18, 52, 16, 22, i * 8 - 8, PAPER, 1, False) for i in range(5)) + lab(160, 96, '#channel', 'mono-s', fill=INK) + lab(160, 30, 'one channel, one folder', 'b'))
comic('03b-fat-folder', 'A very fat folder that will not fit through a door. A worker pulls at it.', '#efd5b7',
      f'<g {S}><rect x="200" y="40" width="80" height="140" fill="{WOOD}"/><rect x="220" y="60" width="40" height="120" fill="{CREAM}"/></g>'
      + folder(130, 120, 130, 90, SAND) + ''.join(slip(88 + i * 22, 70, 16, 22, i * 10 - 20, PAPER, 1, False) for i in range(5))
      + lab(130, 128, '100MB+', 'w', fill=INK) + buddy(40, 150, 'pull', ORANGE, .9) + f'<path d="M62 160L90 150" stroke="{INK}" stroke-width="3"/>' + src(8, 212))
comic('03c-ten-day-slices', 'Slim folders on a shelf, each with a calendar tab. A worker reaches for the newest.', '#c9d9c8',
      f'<path d="M20 150H300" stroke="{INK}" stroke-width="4"/>' + ''.join(folder(50 + i * 42, 120, 32, 50, [SAND, GREEN, PURPLE, ORANGE, GOLD][i]) + cal(37 + i * 42, 82 + 0, 2, 13, 10, SAND, 1 if i == 4 else None) for i in range(5))
      + buddy(250, 190, 'ah!', GREEN, .8) + f'<path d="M232 170Q215 150 214 144" fill="none" stroke="{RED}" stroke-width="3" marker-end="url(#ah)"/>' + lab(160, 30, 'new folder every 10 days', 'b') + src(8, 212))
comic('04a-edit-delete', 'Two workers at two desks reach for the same slip, one with a pen, one with scissors.', '#f0e3c6',
      desk(60, 150, 1.5, WOOD) + desk(260, 150, 1.5, GREEN) + buddy(60, 90, 'edit', SAND, .8) + buddy(260, 90, 'cut', PURPLE, .8) + slip(160, 70, 34, 44, 0, PAPER, 2)
      + f'<g transform="translate(98 100) rotate(-30)" {S}><rect width="32" height="7" fill="{ORANGE}"/><path d="M0 0l-9 3.5l9 3.5z" fill="{SAND}"/></g>'
      + f'<g transform="translate(222 98)" {S}><path d="M0 0l-24 10M0 8l-24 -6" fill="none"/><circle cx="4" cy="-1" r="4" fill="none"/><circle cx="4" cy="9" r="4" fill="none"/></g>' + lab(160, 30, 'same moment!', 'sfx-s'))
comic('04b-half-slip', 'A message slip mostly blank, with only a name tab and a few words left.', '#efd5b7',
      f'<rect x="100" y="25" width="120" height="160" rx="3" fill="{PAPER}" {S}/><rect x="110" y="35" width="50" height="14" fill="{TEAL}" stroke="{INK}" stroke-width="1.5"/>'
      + f'<path d="M112 70h60" stroke="{INK}" stroke-width="2.5"/>' + f'<path d="M112 100h90M112 124h70M112 148h80" stroke="#d8cfb8" stroke-width="6" stroke-dasharray="4 8" stroke-linecap="round"/>' + lab(160, 205, 'half a message', 'b'))
comic('04c-clean-up', 'A worker spots a half-empty slip, shakes his head and drops it in a bin.', '#c9d9c8',
      buddy(90, 140, 'no', ORANGE, 1.1) + slip(160, 90, 34, 44, -12, PAPER, 0) + f'<path d="M150 100h18" stroke="#d8cfb8" stroke-width="5"/>'
      + f'<g {S}><path d="M222 118h56l-6 62h-44z" fill="{GREY}"/><path d="M216 118h68" stroke-width="4"/></g>' + f'<path d="M168 96Q195 70 250 104" fill="none" stroke="{RED}" stroke-width="3" stroke-dasharray="8 7" class="m-flow"/>' + lab(250, 200, 'broken? bin it', 'b'))
comic('05a-marker', 'A worker puts a small flag on a message slip instead of tearing it up.', '#f0e3c6',
      buddy(80, 140, 'flag', SAND, 1.1) + slip(200, 120, 56, 74, 0, PAPER, 3) + flag(230, 96, 1.6) + lab(160, 30, 'a delete leaves a marker', 'b') + lab(160, 200, 'a tombstone', 'micro', fill=RED))
comic('05b-empty-boxes', 'A form with sixteen boxes. Four are filled, twelve are blank with flags.', '#c3b2d8',
      f'<rect x="30" y="24" width="140" height="150" rx="4" fill="{PAPER}" {S}/>' + form(42, 38, 16, 4, 28 // 2 + 1) + lab(240, 80, '16 boxes', 'w') + lab(240, 112, '4 filled', 'b') + lab(240, 140, '12 flags', 'b') + src(8, 212))
comic('05c-only-filled', 'A worker fills in only four boxes and leaves the rest bare. A tidy desk.', '#c9d9c8',
      f'<rect x="30" y="24" width="140" height="150" rx="4" fill="{PAPER}" {S}/>' + form(42, 38, 16, 4, 14, False) + buddy(245, 130, 'tidy', GREEN, 1.05) + lab(240, 190, 'only what has a value', 'b') + src(8, 212))
comic('06a-long-pause', 'A worker frozen mid-step beside a big clock, with paper scraps piling up.', '#efd5b7',
      buddy(90, 130, 'wait', PURPLE, 1.2) + clock(220, 90, 42) + lab(220, 160, '10 seconds', 'w') + f'<path d="M40 190q20 -14 36 -4t30 2q20 -12 40 0" fill="{PAPER}" {S}/>' + src(8, 212))
comic('06b-marker-heap', 'A huge heap of tiny flags with one lonely slip at the bottom. A worker digs.', '#f0e3c6',
      f'<path d="M30 190Q100 40 200 190Z" fill="#e4c898" {S}/>' + ''.join(flag(80 + (i * 29) % 90 + (i // 4) * 5, 170 - (i % 4) * 26 - (i // 4) * 4, .8) for i in range(10))
      + slip(130, 184, 30, 24, 4, PAPER, 0) + buddy(262, 140, 'dig', GREEN, 1) + lab(160, 30, 'millions of flags', 'micro', fill=INK))
comic('06c-skip-empty', 'A worker stamps an empty folder skip. A shorter calendar strip and a smaller heap.', '#c9d9c8',
      folder(70, 70, 70, 46, SAND) + f'<g transform="rotate(-12 70 74)">' + lab(70, 80, 'SKIP', 'sfx-s') + '</g>' + buddy(240, 80, 'skip', ORANGE, .95)
      + cal(40, 135, 10, 14, 12, SAND) + lab(110, 175, '10 days', 'micro', fill=INK) + f'<path d="M185 141h26" stroke="{RED}" stroke-width="3" marker-end="url(#ah)"/>'
      + cal(222, 135, 2, 14, 12, GREEN) + lab(236, 175, '2 days', 'micro', fill=INK) + src(8, 212))

# ============================== fact icons ==============================
def icon(name, title, body):
    put(f'facts/{name}.svg', 160, 100, title, '#f0e3c6', body)


icon('messages-100m', 'A whiteboard stuffed with notes and a small label reading full.', wallboard(20, 10, 120, 62, 8, 4) + lab(80, 90, 'FULL', 'micro', fill=RED))
icon('partition-100mb', 'A fat folder with a warning triangle.', folder(70, 56, 90, 56, SAND)
     + f'<path d="M120 12l16 28h-32z" fill="{GOLD}" {S}/>' + lab(120, 36, '!', 'w-s', fill=INK) + src(6, 96, True).replace('y="82"', 'y="82"'))
icon('ten-day-bucket', 'A slim folder with a ten-day calendar strip on its tab.', folder(80, 42, 60, 50, GREEN) + cal(10, 74, 10, 14, 12, SAND) + lab(80, 66, '10 days', 'micro', fill=INK))
icon('empty-boxes', 'A form with sixteen boxes, twelve of them blank with flags.', form(8, 6, 16, 4, 14) + lab(108, 40, '12 of 16', 'w-s') + lab(108, 58, 'blank', 'micro', fill=INK) + src(6, 96, True))
icon('tombstone-life', 'A short calendar strip beside a long one with an arrow between them.', cal(6, 20, 10, 8, 12, SAND) + f'<path d="M50 46V62H118" fill="none" stroke="{RED}" stroke-width="3" marker-end="url(#ah)"/>'.replace('marker-end="url(#ah)"', '')
     + f'<path d="M110 56l8 6l-8 6" fill="none" stroke="{RED}" stroke-width="3"/>' + cal(122, 20, 2, 16, 12, GREEN) + lab(46, 16, '10 days', 'micro', fill=INK) + lab(130, 16, '2 days', 'micro', fill=INK)
     + lab(80, 12, '', 'micro') + src(6, 96, True))
icon('twelve-desks', 'A ring of twelve desks, each with a small stack of folders.', ringdesks(80, 36, 60, 24, 12, .34) + lab(80, 42, '12', 'w-s') + src(6, 96, True))


# ============================== write and check ==============================
def srcs(doc):
    found = []

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get('src'), str) and o['src'].startswith('discord-billions/'):
                found.append((o['src'], o.get('width'), o.get('height')))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(doc)
    return found


if __name__ == '__main__':
    found = srcs(json.loads(SEED.read_text()))
    wanted = {s.split('/', 1)[1] for s, _, _ in found}
    made = {}
    for rel, (vb, title, body) in PANELS.items():
        made[rel] = write(OUT, rel, svg(vb, body, title))
    assert not wanted - set(made), f'not drawn: {sorted(wanted - set(made))}'
    for s, w, h in found:
        txt = made[s.split('/', 1)[1]].read_text()
        assert f'viewBox="0 0 {w} {h}"' in txt, s
    total = 0
    for rel, p in made.items():
        xml.dom.minidom.parse(str(p))
        total += p.stat().st_size
        assert '<script' not in p.read_text() and 'http' not in p.read_text().replace('http://www.w3.org/2000/svg', '')
    print(f'wrote {len(made)} files, {total} bytes; extra: {sorted(set(made) - wanted)}')
    print('largest:', sorted(((p.stat().st_size, r) for r, p in made.items()))[-3:])
