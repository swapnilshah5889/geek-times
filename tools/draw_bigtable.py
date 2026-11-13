"""Draws the media for "Bigtable: A Distributed Storage System for Structured Data" (OSDI 2006).

Run from the repo root:  python3 tools/draw_bigtable.py
Writes standalone SVGs to backups/media/bigtable/{lead,story,comic,facts}/. Every media.src in
data/seed/papers/bigtable.json must be written. Helpers are reused from tools/draw_cassandra.py.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from draw_cassandra import (ORANGE, GREEN, PURPLE, SAND, WOOD, PAPER, GOLD, TEAL, GREY, arrow, board, desk,  # noqa: E402
                            envelope, folder, magnifier, notebook, pencil, svg)
from media_kit import INK, RED, bubble, buddy, t, write  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'backups' / 'media' / 'bigtable'
SEED = ROOT / 'data' / 'seed' / 'papers' / 'bigtable.json'
CREAM = '#f6f0df'


def bg(w, h, col=CREAM):
    return f'<rect width="{w}" height="{h}" fill="{col}"/><rect width="{w}" height="{h}" fill="url(#dots)" opacity=".22"/>'


def R(x, y, w, h, fill=PAPER, rx=3, sw=2):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx}" fill="{fill}" stroke="{INK}" stroke-width="{sw}"/>'


def line(d, w=2, col=INK, op=1, extra=''):
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" opacity="{op}" {extra}/>'


def clock(x, y, r=8):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>'
            + line(f'M{x} {y - r * .6:g}V{y}L{x + r * .5:g} {y + r * .3:g}', 1.6))


def tag(x, y, label, w=None, col=GOLD):
    w = w or 12 + 8.2 * len(label)
    return R(x, y, w, 20, col, 4, 1.8) + t(x + w / 2, y + 15, label, 'micro')


def scissors(x, y, rot=0, s=1):
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linecap="round" fill="none">'
            f'<path d="M0 0L34 -9M0 0L34 9"/><circle cx="-8" cy="-7" r="6" fill="{RED}"/><circle cx="-8" cy="7" r="6" fill="{RED}"/>'
            '<path d="M-3 -4L0 0M-3 4L0 0"/></g>')


def sheet(x, y, w, h, rows=4, fill=PAPER, labels=None):
    g = R(x, y, w, h, fill)
    step = h / (rows + 1)
    for i in range(rows):
        yy = y + step * (i + 1)
        g += line(f'M{x + 8:g} {yy:g}H{x + w - 8:g}', 1.5, INK, .4)
        if labels:
            g += t(x + 10, f'{yy - 4:g}', labels[i], 'mono-s', 'start')
    return g


def pieces(x, y, w, h, n, gap=0, cols=(SAND, GREEN, PURPLE)):
    pw = (w - gap * (n - 1)) / n
    return ''.join(R(x + i * (pw + gap), y, pw, h, cols[i % 3]) +
                   line(f'M{x + i * (pw + gap) + 6:g} {y + h * .35:g}h{pw - 12:g}M{x + i * (pw + gap) + 6:g} {y + h * .65:g}h{pw - 12:g}', 1.5, INK, .4)
                   for i in range(n))


def stamp(x, y, s, anchor='start'):
    return t(x, y, s, 'micro', anchor, 'fill:#a13324')


def cust(x, y, word='you', col=ORANGE, s=.8):
    return buddy(x, y, word, col, s, label_cls='w-s')


PANELS = []


def P(rel, w, h, title, body, back=True):
    PANELS.append((f'bigtable/{rel}', f'0 0 {w} {h}', title, (bg(w, h) if back else '') + body))


# ---------------- lead plates (600x340) ----------------
rows = ['com.bbc.www', 'com.cnn.www', 'com.cnn.edition', 'org.acm.www', 'org.w3.www']
g = t(300, 44, 'One giant table', 'w', style='font-size:28px') + R(70, 70, 460, 230, PAPER, 6, 3)
g += R(70, 70, 460, 34, SAND, 6, 3) + t(120, 93, 'row', 'micro') + t(260, 93, 'contents:', 'mono-s') + t(380, 93, 'anchor:', 'mono-s') + t(480, 93, 'language:', 'mono-s')
g += line('M200 70V300M340 70V300M440 70V300', 2, INK, .5) + line('M70 104H530', 2)
for i, r in enumerate(rows):
    y = 108 + i * 38
    g += line(f'M70 {y + 38}H530', 1.5, INK, .4) + t(78, y + 24, r, 'mono-s', 'start')
    for cx in (210, 350, 450):
        g += R(cx, y + 8, 78 if cx < 440 else 70, 22, '#fffdf0', 2, 1.3)
# stacked older copies in two boxes
for cx, ry in ((210, 1), (350, 3)):
    y = 108 + ry * 38
    g += R(cx + 8, y - 2, 78, 22, GREEN, 2, 1.5) + R(cx + 4, y + 2, 78, 22, SAND, 2, 1.5) + R(cx, y + 6, 78, 24, PAPER, 2, 1.8) + clock(cx + 66, y + 18, 7)
g += t(300, 324, 'Rows in alphabetical order · columns in labelled groups · older copies stacked', 'b-s')
P('lead/giant-table.svg', 600, 340, 'A giant sorted table with column groups and stacked older copies', g)

g = t(300, 34, 'Cut into pieces, one desk each', 'w', style='font-size:24px')
g += R(70, 54, 460, 36, PAPER, 4, 3) + pieces(70, 54, 460, 36, 6, 0) + line('M140 48V96M217 48V96M293 48V96M370 48V96M447 48V96', 2.5, RED, 1, 'stroke-dasharray="6 5"')
g += scissors(293, 100, 90, 1.2) + t(380, 122, 'SNIP!', 'sfx')
g += R(250, 154, 100, 38, '#e8f3f0', 6, 2.5) + t(300, 178, 'manager', 'w-s')
ds = [90, 170, 250, 330, 410, 490]
cols = [SAND, GREEN, PURPLE, SAND, GREEN, PURPLE]
for i, x in enumerate(ds):
    g += desk(x, 270, 1.35, WOOD) + R(x - 16, 224, 32, 14, cols[i], 2, 1.8) + t(x, 322, f'desk {chr(65 + i)}', 'micro')
    g += arrow(f'M{x} 108V196', False, 2.5).replace(f'stroke="{RED}"', f'stroke="{RED}" opacity=".7"') if i in (0, 2, 5) else ''
g += line('M300 192L90 204M300 192L250 204M300 192L490 204', 2, TEAL, .8, 'stroke-dasharray="4 5"')
P('lead/tablets-on-desks.svg', 600, 340, 'A sorted table cut into pieces, each carried to its own desk', g)

# ---------------- story panels (440x215) ----------------
g = t(220, 26, 'Different things, one shelf', 'w')
g += R(30, 48, 62, 24, '#fffdf0', 3) + t(61, 65, 'a URL', 'b-s') + R(30, 86, 62, 50, PAPER, 3) + line('M38 98h46M38 108h46M38 118h30', 1.8, INK, .5) + t(61, 152, 'web page', 'b-s')
g += R(22, 162, 78, 44, '#a2c2a7', 3) + line('M30 196L50 176L64 190L78 180L94 196', 2) + t(61, 204, '', 'b-s')
g += t(61, 211, 'satellite photo', 'micro') if False else ''
for y in (60, 110, 184):
    g += arrow(f'M104 {y}Q190 {y} 250 {110 if y < 150 else 150}', False, 3)
g += R(262, 56, 150, 140, WOOD, 5, 3)
for i in range(3):
    for j in range(3):
        g += R(272 + j * 46, 66 + i * 40, 38, 32, '#fffdf0', 2, 1.8)
g += t(337, 211, 'one big storage shelf', 'b-s')
P('story/01-every-size.svg', 440, 215, 'Small and large things flow to one storage shelf', g)

g = t(220, 26, 'Cut by rows, one piece per desk', 'w')
g += R(40, 42, 360, 34, PAPER, 4, 3) + pieces(40, 42, 360, 34, 3, 0) + line('M160 38V82M280 38V82', 2.5, RED, 1, 'stroke-dasharray="6 5"')
for i, x in enumerate((100, 220, 340)):
    g += arrow(f'M{x} 84V120', False, 2.8) + desk(x, 160, 1.5) + R(x - 15, 120, 30, 12, [SAND, GREEN, PURPLE][i], 2, 1.8) + t(x, 207, f'desk {chr(65 + i)}', 'micro')
g += scissors(160, 94, 90, .9) + scissors(280, 94, 90, .9)
P('story/02-sorted-map.svg', 440, 215, 'A sorted sheet is cut into three pieces, each on its own desk', g)

g = t(220, 24, 'Notebook, whiteboard, folders', 'w')
g += envelope(40, 100, -8, 1.4) + t(40, 140, 'new write', 'b-s')
g += arrow('M62 100H92', False, 3) + notebook(122, 100, .8, 4) + t(122, 160, 'notebook', 'b-s') + pencil(138, 130, -40)
g += arrow('M168 80H196', False, 3) + board(200, 66, 90, 62, 3) + t(245, 160, 'whiteboard', 'b-s')
g += arrow('M296 100H318', False, 3)
for i in range(3):
    g += folder(342, 66 + i * 28, 62, 34, [SAND, GREEN, PURPLE][i])
g += t(350, 160, 'folders', 'b-s') + buddy(402, 150, 'door', ORANGE, .55, label_cls='micro') + line('M392 112l8 8l14 -14', 3.5, TEAL)
g += t(220, 196, 'the doorman checks one folder before you open it', 'b-s')
P('story/03-notebook-whiteboard-folders.svg', 440, 215, 'A write goes to a notebook, a whiteboard, then folders with a doorman', g)

g = t(220, 24, 'Many small machines, one group', 'w') + R(24, 38, 392, 132, '#ece3c8', 6, 2)
for i in range(8):
    for j in range(4):
        hi = 2 <= i <= 5 and 1 <= j <= 2
        g += R(36 + i * 47, 48 + j * 29, 38, 22, '#a2c2a7' if hi else '#fffdf0', 3, 2.4 if hi else 1.5) + line(f'M{42 + i * 47} {59 + j * 29}h26', 1.3, INK, .5)
g += R(126, 73, 190, 64, '', 6, 3).replace('fill=""', 'fill="none"').replace(f'stroke="{INK}"', f'stroke="{RED}"') + t(226, 126, '', 'b-s')
g += t(220, 192, '24,500 tablet servers in all (Aug. 2006)', 'b-s') + stamp(220, 208, 'From the paper · measured', 'middle')
P('story/04-clusters.svg', 440, 215, 'A grid of server boxes, with one group highlighted', g)

# ---------------- comic panels (320x220) ----------------
def cp(rel, title, body, col=CREAM):
    PANELS.append((f'bigtable/comic/{rel}.svg', '0 0 320 220', title, bg(320, 220, col) + body))


g = R(88, 70, 190, 120, PAPER, 4, 3) + line('M88 110H278M88 150H278M150 70V190M214 70V190', 2, INK, .55)
g += R(214, 110, 64, 40, '#a2c2a7', 3, 3) + t(246, 135, 'cell', 'w-s')
g += t(119, 96, 'row', 'micro') + t(119, 136, 'cnn', 'b-s') + t(182, 94, 'column', 'micro') + t(246, 94, 'time', 'micro')
g += R(30, 120, 54, 24, GOLD, 4, 2) + t(57, 137, 'row', 'w-s') + R(120, 30, 90, 24, SAND, 4, 2) + t(165, 47, 'column', 'w-s')
g += clock(268, 40, 14) + line('M268 54V108', 2.2, RED, 1, 'stroke-dasharray="4 4"') + t(160, 208, 'row + column + time = one box', 'b-s')
cp('01a-address', 'A grid cell is found by row, column and time', g)

g = t(160, 28, 'rows sorted a-z', 'w')
rws = ['com.bbc.www', 'com.cnn.www/a', 'com.cnn.www/b', 'org.acm.www']
for i, r in enumerate(rws):
    hi = i in (1, 2)
    g += R(40, 46 + i * 34, 190, 30, '#a2c2a7' if hi else PAPER, 3, 2) + t(52, 67 + i * 34, r, 'mono-s', 'start')
g += line('M240 52q14 0 14 14v34q0 14 -14 14', 3, RED) + t(262, 82, 'same site,', 'b-s', 'start') + t(262, 100, 'side by', 'b-s', 'start') + t(262, 118, 'side', 'b-s', 'start')
g += t(160, 204, 'web addresses are written backwards', 'b-s')
cp('01b-sorted-rows', 'Reversed web addresses sit in alphabetical order, same-site rows together', g)

g = t(160, 28, 'older copies stay', 'w')
for i, (lab, c) in enumerate((('oldest', GREEN), ('older', SAND), ('newest', PAPER))):
    g += R(80 + i * 16, 100 - i * 18 + 40 - 40, 150, 62, c, 4, 2.4) + t(110 + i * 16, 142 - i * 18, lab, 'b-s', 'start') + clock(208 + i * 16, 112 - i * 18 + 6 - 6, 9)
g += R(60, 126, 200, 56, 'none', 5, 3).replace('fill="none"', 'fill="none"') if False else ''
g += t(160, 206, 'one box, newest on top', 'b-s')
cp('01c-versions', 'One box with three stacked sheets, the top one newest', g)

g = R(30, 70, 260, 50, PAPER, 4, 3) + pieces(30, 70, 260, 50, 4, 0) + line('M95 62V128M160 62V128M225 62V128', 2.5, RED, 1, 'stroke-dasharray="6 5"')
g += scissors(160, 140, 90, 1.5) + t(236, 170, 'SNIP!', 'sfx') + t(160, 38, 'cut by row ranges', 'w') + t(70, 190, 'tablets', 'w-s')
cp('02a-cut', 'Scissors cut a long sorted table into pieces', g)

g = desk(160, 140, 3, WOOD) + pieces(110, 80, 100, 30, 3, 4) + R(110, 170, 100, 28, '#fffdf0', 3, 2.5) + t(160, 190, 'desk A', 'w-s')
g += t(160, 40, 'one desk, many pieces', 'w')
cp('02b-one-desk', 'Several small pieces on one desk with a nameplate', g)

g = R(110, 22, 100, 36, '#e8f3f0', 6, 2.5) + t(160, 46, 'manager', 'w-s')
for i, x in enumerate((60, 160, 260)):
    g += desk(x, 130, 1.3) + R(x - 14, 102, 28, 12, [SAND, GREEN, PURPLE][i], 2, 1.8)
g += line('M130 60L70 98M190 60L250 98', 2.2, TEAL, .9, 'stroke-dasharray="4 5"') + cust(100, 192, 'you') + arrow('M130 188Q150 170 156 158', False, 3)
g += bubble(196, 168, 108, 40, ['ask the desk'], (170, 160), 'b-s')
cp('02c-master', 'A manager points pieces to desks while a customer walks straight to a desk', g)

g = notebook(150, 100, 1.6, 6) + pencil(196, 160, -30, 'm-bob') + line('M104 140h94', 3.5, RED) + t(160, 208, 'add a line at the end', 'b-s') + t(160, 24, 'notebook', 'w')
cp('03a-notebook', 'A pencil adds a line at the bottom of a long notebook', g)

g = notebook(60, 110, 1, 4) + arrow('M100 110H150', False, 3) + board(160, 50, 140, 100, 3) + t(230, 176, 'whiteboard', 'w-s') + t(60, 176, 'notebook', 'w-s')
g += R(180, 66, 30, 22, GOLD, 2, 1.8) + t(160, 28, 'same note, kept in order', 'w-s', style='font-size:17px')
cp('03b-whiteboard', 'The same note is pinned in order on a whiteboard beside the notebook', g)

g = desk(80, 100, 1.5) + pieces(40, 48, 80, 22, 3, 3) + line('M120 80Q170 100 214 120', 2.5, RED, 1, 'stroke-dasharray="6 5"') + notebook(250, 130, 1.1, 5)
g += t(80, 160, 'three pieces', 'b-s') + t(250, 200, 'one notebook', 'w-s') + t(160, 28, 'all write to the same one', 'w-s')
cp('03c-one-notebook', 'Three small pieces on a desk send notes into one notebook', g)

g = board(40, 50, 110, 76, 3) + R(48, 60, 12, 12, '#cfe7f0', 2, 1.5) + line('M60 42v20M50 52h20M53 45l14 14M67 45L53 59', 2.5, TEAL) + t(95, 160, 'full: frozen', 'b-s')
g += board(180, 50, 110, 76, blank=True) + t(235, 160, 'fresh and clean', 'b-s') + t(160, 28, 'freeze', 'w') + line('M158 88h16', 3, RED)
cp('04a-freeze', 'A full whiteboard gets a snowflake tag while a clean whiteboard stands beside it', g)

g = board(24, 50, 110, 76, 3) + arrow('M142 90H176', False, 3) + R(188, 160, 108, 12, WOOD, 2, 2.5) + folder(242, 130, 76, 52, SAND) + t(242, 138, 'sorted', 'micro')
g += t(80, 160, 'sorted note board', 'b-s') + t(160, 28, 'copy out, never edit', 'w-s') + t(242, 200, 'shelf', 'micro')
cp('04b-folder', 'A sorted whiteboard is copied into a neat closed folder on a shelf', g)

g = board(150, 50, 110, 76, blank=True) + cust(76, 150, 'you') + arrow('M108 130Q130 112 150 100', False, 3) + R(200, 168, 100, 10, WOOD, 2, 2.5) + folder(250, 148, 60, 38, SAND)
g += t(160, 28, 'service continues', 'w') + t(250, 202, 'filed away', 'b-s')
cp('04c-keep-going', 'A customer is served at the clean whiteboard while the folder is filed away', g)

g = R(40, 186, 240, 10, WOOD, 2, 2.5) + '<g class="m-wobble">'
for i, c in enumerate((SAND, GREEN, PURPLE, ORANGE, SAND, GREEN, PURPLE)):
    g += folder(160 + (i % 2) * 10 - 5 + (i == 5) * 8, 170 - i * 20, 90, 32, c, (i - 3) * 2)
g += '</g>' + t(160, 28, 'too many folders', 'w') + t(250, 90, 'slow reads', 'b-s')
cp('05a-pile', 'A tall wobbly pile of folders on a shelf', g)

g = ''.join(folder(44, 56 + i * 44, 56, 34, c) for i, c in enumerate((SAND, GREEN, PURPLE)))
g += line('M80 56H130M80 100H130M80 144H130', 2.5, RED, 1, 'stroke-dasharray="6 5"') + R(134, 50, 36, 110, '#e8f3f0', 6, 2.5) + line('M152 56v98', 2, INK, .6)
for i in range(7):
    g += line(f'M{138 + (i % 2) * 18} {60 + i * 14}h14', 2.5)
g += arrow('M176 105H210', False, 3.5) + folder(256, 105, 80, 62, SAND) + t(256, 112, 'merged', 'micro') + t(160, 28, 'zip into one', 'w') + t(256, 160, 'bigger folder', 'b-s')
cp('05b-zip', 'Three folders slide into a zipper that outputs one larger folder', g)

g = R(50, 126, 150, 10, WOOD, 2, 2.5) + folder(125, 98, 110, 62, SAND) + t(125, 106, 'all merged', 'micro')
g += f'<path d="M232 130h50l-6 66h-38Z" fill="{GREY}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>' + R(232, 100, 54, 28, PAPER, 2, 2) + t(259, 119, 'old note', 'micro') + line('M236 104l46 20M282 104l-46 20', 3, RED)
g += t(259, 214, 'gone for good', 'b-s') + t(125, 160, 'one folder', 'b-s') + t(160, 28, 'a major compaction', 'w-s', style='font-size:17px')
cp('05c-all-zipped', 'One single folder on the shelf, and a crossed-out note in the bin', g)

g = board(100, 40, 90, 56, 3) + ''.join(folder(120 + i * 60, 122, 56, 34, c) for i, c in enumerate((SAND, GREEN, PURPLE))) + R(70, 140, 180, 8, WOOD, 2, 2)
g += magnifier(130, 80, 1) + t(160, 190, 'looked at as one merged list', 'b-s') + t(160, 24, 'one read, all places', 'w-s', style='font-size:17px')
cp('06a-merged-view', 'A magnifying glass looks over a whiteboard and several folders as one list', g)

g = R(150, 40, 70, 130, WOOD, 4, 3) + R(158, 48, 54, 114, '#e8d6b0', 2, 2) + buddy(120, 128, 'door', ORANGE, .8, label_cls='w-s') + folder(262, 90, 54, 34, SAND) + folder(262, 140, 54, 34, GREEN)
g += bubble(12, 28, 112, 44, ['not here!'], (116, 98), 'b-s') + line('M284 78l14 14M298 78l-14 14', 3.5, RED) + line('M286 142l8 8l14 -16', 3.5, TEAL) + t(160, 204, 'saves a trip to the disk', 'b-s')
cp('06b-doorman', 'A doorman at a folder door shakes his head at one folder and nods at another', g)

g = desk(60, 120, 1.7, GREEN) + t(60, 170, 'second desk', 'b-s') + notebook(160, 90, .9, 4) + arrow('M104 108Q130 96 124 92', False, 3).replace('<path', '<path', 1)
g += arrow('M196 100H228', False, 3) + board(232, 66, 76, 60, 3) + t(270, 150, 'fresh board', 'b-s') + t(160, 168, 'notebook', 'b-s') + t(160, 24, 'a machine died? replay', 'w-s', style='font-size:17px')
cp('06c-rebuild', 'A second desk reads a notebook and rewrites a fresh whiteboard', g)

# ---------------- fact icons (160x100) ----------------
def fi(rel, title, body):
    P(f'facts/{rel}.svg', 160, 100, title, body)


g = ''.join(R(14 + i * 24, 12 + j * 20, 20, 15, '#fffdf0' if (i + j) % 4 else '#a2c2a7', 2, 1.8) for i in range(6) for j in range(4))
fi('servers', 'A big grid of small server boxes', g + t(80, 96, 'many machines', 'micro'))
g = R(10, 20, 44, 52, '#a2c2a7', 4, 2.4) + t(32, 52, 'srv', 'micro') + ''.join(arrow(f'M{138} {26 + i * 22}Q96 {26 + i * 22} 62 {36 + i * 10}', True, 2.5) for i in range(3)) + clock(142, 86, 9) + t(80, 94, 'per second', 'micro', 'start', 'font-size:12px')
fi('requests', 'Many requests flowing to a group of servers each second', g.replace('t(80, 94', 't(40, 94'))
g = R(10, 28, 140, 30, PAPER, 3, 2.4) + R(50, 28, 36, 30, SAND, 3, 2.4) + line('M50 66v8h36v-8M68 74v6', 2, RED) + t(68, 94, 'one tablet', 'micro')
fi('tablet-size', 'One small slice of a long table, marked as one tablet', g)
g = R(10, 14, 140, 18, '#a2c2a7', 3, 2.4) + R(10, 38, 36, 18, SAND, 3, 2.4) + R(10, 62, 24, 18, SAND, 3, 2.4) + t(60, 52, 'gzip: shorter', 'micro', 'start') + t(40, 76, '', 'micro') + t(44, 78, 'this: tiny', 'micro', 'start')
fi('compress', 'A long bar squeezed to a short one, shorter still with neighbours together', g.replace('<rect x="10" y="62" width="24"', '<rect x="10" y="62" width="16"'))
g = R(50, 8, 60, 84, PAPER, 4, 2.5) + ''.join(R(56, 14 + i * 14, 48, 10, '#e8f3f0' if i % 2 else SAND, 2, 1.4) for i in range(6)) + buddy(24, 58, '', ORANGE, .5) + buddy(136, 58, '', GREEN, .5)
fi('click-table', 'A very tall table with one row for each visitor session', g)
g = R(52, 40, 56, 44, GOLD, 5, 2.5) + f'<path d="M64 40v-12a16 16 0 0 1 32 0v12" fill="none" stroke="{INK}" stroke-width="4"/><circle cx="80" cy="60" r="5" fill="{INK}"/>' + R(10, 90, 140, 6, '#a2c2a7', 2, 1.5) + f'<rect x="132" y="90" width="3" height="6" fill="{RED}"/>' + t(80, 16, 'lock service', 'micro')
fi('chubby', 'A padlock, with a hairline sliver of a bar showing the rare downtime', g)

# =====================================================================
def story_srcs(doc):
    found = []

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get('src'), str) and o['src'].startswith('bigtable/'):
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
        made[rel] = write(OUT, rel.replace('bigtable/', '', 1), svg(vb, body, title))
    missing = {w.replace('bigtable/', '', 1) for w in wanted} - {m.replace('bigtable/', '', 1) for m in made}
    assert not missing, f'not drawn: {sorted(missing)}'
    for s, w, h in srcs:
        assert f'viewBox="0 0 {w} {h}"' in made[s].read_text(), f'wrong viewBox for {s}'
    print(f'wrote {len(made)} files to {OUT}; total {sum(p.stat().st_size for p in made.values())} bytes; extra: {sorted(set(made) - wanted)}')
