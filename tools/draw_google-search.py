"""Draws the two lead plates for "The Anatomy of a Large-Scale Hypertextual Web Search Engine" (Google Search).

Run from the repo root:  python3 tools/draw_google-search.py
Writes standalone SVG files to public/media/google-search/lead/.
Plate captions/alt text live in data/seed/papers/google-search.json.
"""
import math
import random
from pathlib import Path

from media_kit import COL, COMIC_DEFS, EIGHT, INK, RED, anim, bubble, buddy, gear, panel, standalone, t, write

OUT = Path(__file__).resolve().parent.parent / 'public' / 'media' / 'google-search' / 'lead'
CREAM = '#fbf3dc'
DEFS = COMIC_DEFS + (
    f'<marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
    f'<path d="M0 0L10 5L0 10Z" fill="{INK}"/></marker>')


def plate(bg, tag, body, caption):
    return (f'<rect width="600" height="340" fill="{bg}"/><rect width="600" height="340" fill="url(#dots)" opacity=".22"/>'
            + body
            + f'<rect x="10" y="288" width="580" height="44" fill="{CREAM}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
            + t(300, 317, caption, 'b')
            + t(22, 28, tag, 'micro', 'start', f'fill:{RED}')
            + f'<path d="M8 10Q300 5 592 9Q596 170 591 332Q300 336 9 331Q4 170 8 10Z" fill="none" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>')


def page(x, y, rot=0, s=1, fill='#fff8e3', lines=3):
    ls = ''.join(f'<path d="M-12 {-14 + i * 8}h{24 - (i % 2) * 8}" stroke="{INK}" stroke-width="1.8" stroke-linecap="round" opacity=".65"/>' for i in range(lines))
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})">'
            f'<path d="M-18 -24H8L18 -14V24H-18Z" fill="{fill}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
            f'<path d="M8 -24V-14H18" fill="none" stroke="{INK}" stroke-width="2"/>{ls}</g>')


# ---- pile ----
rnd = random.Random(7)
pile = ''
pts = []
for row in range(7):
    n = 14 - row * 2
    y = 262 - row * 24
    for k in range(n):
        x = 300 + (k - (n - 1) / 2) * 38 + rnd.uniform(-8, 8)
        pts.append((x, y + rnd.uniform(-6, 6), rnd.uniform(-35, 35), ['#fff8e3', '#f0e3c6', '#f7d79b', '#e6efe4', '#e5dcef'][rnd.randrange(5)]))
gold_i = 20
for i, (x, y, r, c) in enumerate(pts):
    if i == gold_i:
        pile += page(x, y, r, 1.0, '#f2c14e') + f'<use href="#mstar" transform="translate({x + 4:.0f} {y:.0f}) scale(1.4)"/>'
    else:
        pile += page(x, y, r, 1.05, c, rnd.choice([2, 3, 4]))
pile_body = (pile
             + f'<g{anim("m-twinkle")}><use href="#mstar" transform="translate({pts[gold_i][0] + 4:.0f} {pts[gold_i][1] - 38:.0f}) scale(1.6)"/></g>'
             + f'<path d="M{pts[gold_i][0] + 20:.0f} {pts[gold_i][1] - 44:.0f}Q470 70 440 60" fill="none" stroke="{RED}" stroke-width="2.5" stroke-linecap="round" marker-end="url(#ah)"/>'
             + t(486, 50, 'the good one?', 'w-s', style=f'fill:{RED}')
             + buddy(80, 150, 'me', COL['bat'], .9) + f'<g{anim("m-bob")}>' + t(120, 100, '?', 'sfx') + '</g>'
             + t(500, 258, 'MILLIONS', 'micro') + t(60, 250, 'UNSORTED', 'micro'))

# ---- votes ----
def star_row(cx, cy, n):
    return ''.join(f'<use href="#mstar" transform="translate({cx + (i - (n - 1) / 2) * 24:.0f} {cy}) scale(1.5)"/>' for i in range(n))


def node(x, y, r, fill):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{INK}" stroke-width="3"/>'
            + page(x, y + 1, 0, r / 34, '#fff8e3', 3))


def arrow(a, ra, b, rb, color=INK, w=3):
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    x1, y1 = a[0] + math.cos(ang) * (ra + 3), a[1] + math.sin(ang) * (ra + 3)
    x2, y2 = b[0] - math.cos(ang) * (rb + 6), b[1] - math.sin(ang) * (rb + 6)
    mx, my = (x1 + x2) / 2 - math.sin(ang) * 10, (y1 + y2) / 2 + math.cos(ang) * 10
    return f'<path d="M{x1:.0f} {y1:.0f}Q{mx:.0f} {my:.0f} {x2:.0f} {y2:.0f}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" marker-end="url(#ah)"/>'


C = (300, 150); RC = 58
MID = (480, 100); RM = 34
smalls = [(110, 70), (90, 170), (160, 235), (300, 255), (440, 235), (510, 190), (200, 40), (400, 40), (545, 85)]
RS = 20
edges = ''
for s in smalls[:6]:
    edges += arrow(s, RS, C, RC)
edges += arrow(smalls[6], RS, C, RC) + arrow(smalls[7], RS, C, RC)
edges += arrow(smalls[8], RS, MID, RM) + arrow(smalls[5], RS, MID, RM)
edges += arrow(MID, RM, C, RC, RED, 3.5) + arrow(smalls[7], RS, MID, RM)
votes_body = (edges + ''.join(node(x, y, RS, '#f0e3c6') for x, y in smalls)
              + node(*MID, RM, '#a2c2a7') + node(*C, RC, '#f7d79b')
              + f'<g{anim("m-twinkle")}>' + star_row(C[0], C[1] - RC - 16, 3) + '</g>'
              + star_row(MID[0], MID[1] - RM - 14, 1)
              + f'<g{anim("m-wiggle")}>' + t(80, 262, 'VOTE!', 'sfx-s') + '</g>')


# =====================================================================
# Comic panels (320x220), story panels (440x215) and fact icons (160x100)
# =====================================================================
ROOT = OUT.parent
PANELS = []   # (path, title, body)
STORY = []
ICONS = []
TEAL = '#377675'


def add(name, title, bg, body):
    PANELS.append((f'comic/{name}.svg', title, panel(bg, body)))


def kid(x, y, s=1.0, fill='#fff8e3', face='smile'):
    """A page with a face and legs: the 'page as a kid' character."""
    mouth = 'M-6 6q6 6 12 0' if face == 'smile' else 'M-5 9h10'
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<path d="M-10 24v12M10 24v12M-10 36h-6M10 36h6" stroke="{INK}" stroke-width="2.5" stroke-linecap="round" fill="none"/>'
            f'<path d="M-18 -24H8L18 -14V24H-18Z" fill="{fill}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
            f'<path d="M8 -24V-14H18" fill="none" stroke="{INK}" stroke-width="2"/>'
            f'<circle cx="-6" cy="-4" r="2.4" fill="{INK}"/><circle cx="6" cy="-4" r="2.4" fill="{INK}"/>'
            f'<path d="{mouth}" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round"/></g>')


def star(x, y, sc=1.2):
    return f'<use href="#mstar" transform="translate({x} {y}) scale({sc})"/>'


def line(d, color=INK, w=3, extra=''):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def rect(x, y, w, h, fill='#fff8e3', sw=2, rx=0, extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{INK}" stroke-width="{sw}" {extra}/>'


def sample(cx, cy, w=1.0):
    """Tiny text-line decoration for page-like boxes."""
    return ''.join(f'<path d="M{cx - 9 * w:g} {cy + i * 7}h{18 * w - (i % 2) * 6 * w:g}" stroke="{INK}" stroke-width="1.6" stroke-linecap="round" opacity=".6"/>' for i in range(3))


# ---------- strip 1: the web is a web of friends ----------

add('01a-pages-as-kids', 'Four page-kids stand apart; one points an arrow at another and says go meet my friend.', '#b8cec0',
    kid(48, 112, 1.15, '#f7d79b') + kid(122, 130, 1.15, '#e6efe4') + kid(206, 108, 1.15, '#e5dcef') + kid(278, 132, 1.15, '#f0e3c6')
    + line('M70 96Q96 66 112 96', RED, 3.5, 'marker-end="url(#ah)"')
    + f'<path d="M60 108Q66 106 74 100" stroke="{INK}" stroke-width="3" stroke-linecap="round" fill="none"/>'
    + bubble(14, 14, 200, 38, ['Go meet my friend!'], (68, 92))
    + t(160, 210, 'PAGES, LIKE KIDS', 'micro'))

smalls1 = [(40, 50), (46, 150), (110, 190), (270, 50), (280, 150), (206, 190), (160, 30)]
body = ''.join(arrow(s_, 17, (160, 108), 46) for s_ in smalls1)
body += ''.join(node(x, y, 17, '#f0e3c6') for x, y in smalls1) + node(160, 108, 46, '#f7d79b')
body += f'<g{anim("m-twinkle")}>' + star(160, 56, 1.3) + star(138, 62, 1) + star(182, 62, 1) + '</g>'
add('01b-everybody-points', 'Seven small page circles all point arrows at one big circle in the middle.', '#efd5b7',
    body + rect(70, 198, 180, 18, CREAM, 2) + t(160, 211, 'EVERYBODY POINTS HERE', 'micro'))

add('01c-famous-kid', 'A big starry circle sends a thick arrow to a page; a small plain circle sends a thin arrow to the same page.', '#c3b2d8',
    arrow((70, 70), 40, (240, 130), 28, RED, 7) + arrow((70, 180), 14, (240, 130), 28, INK, 2)
    + node(70, 70, 40, '#f7d79b') + node(70, 180, 14, '#f0e3c6') + page(246, 130, 0, 1.3, '#a2c2a7', 3)
    + star(52, 20, 1.3) + star(70, 14, 1.5) + star(88, 20, 1.3)
    + t(70, 128, 'famous', 'w-s') + t(116, 196, 'nobody', 'b-s', 'start')
    + f'<g{anim("m-pulse")}>' + t(220, 60, 'COUNTS MORE!', 'sfx-s') + '</g>')

# ---------- strip 2: PageRank ----------

outs = [(50, 170), (125, 190), (195, 190), (270, 170)]
body = ''.join(arrow((160, 62), 30, o, 20, INK, 3) for o in outs)
for (ox, oy), lx in zip(outs, [78, 134, 192, 252]):
    body += page(ox, oy, 0, .85, '#f0e3c6', 3)
for (lx, ly) in [(80, 112), (130, 128), (198, 128), (248, 112)]:
    body += f'<circle cx="{lx}" cy="{ly}" r="15" fill="#fff8e3" stroke="{RED}" stroke-width="2"/>' + t(lx, ly + 6, '¼', 'w', style=f'fill:{RED}')
add('02a-share-the-vote', 'One page hands out its vote through four arrows, each marked one quarter.', '#efd5b7',
    body + page(160, 54, 0, 1.4, '#f7d79b', 3) + star(160, 18, 1.2) + t(268, 40, '4 links', 'b-s') + t(268, 58, '= 4 shares', 'b-s'))

tri = [(160, 62), (86, 150), (234, 150)]
cyc = ''.join(arrow(tri[i], 24, tri[(i + 1) % 3], 24, INK, 3) for i in range(3))
add('02b-again-and-again', 'Two circular arrows loop around a small group of three pages that pass votes to each other.', '#82acad',
    f'<g{anim("m-spin-slow")}><g style="transform-origin:160px 118px">' + line('M160 14A92 92 0 0 1 252 106', RED, 4, 'marker-end="url(#ah)"')
    + line('M160 214A92 92 0 0 1 68 122', RED, 4, 'marker-end="url(#ah)"') + '</g></g>'
    + cyc + ''.join(page(x, y, 0, 1.0, c, 3) for (x, y), c in zip(tri, ['#f7d79b', '#e6efe4', '#e5dcef']))
    + t(40, 200, 'again!', 'sfx-s'))

row = [(40, 150), (100, 150), (160, 150)]
body = ''.join(arrow(row[i], 19, row[i + 1], 19, INK, 2.5) for i in range(2))
body += ''.join(page(x, y, 0, .8, '#f0e3c6', 3) for x, y in row) + page(268, 60, 0, .95, '#a2c2a7', 3)
body += line('M168 126Q214 40 252 56', RED, 3, 'marker-end="url(#ah)" stroke-dasharray="7 6"')
body += (f'<g{anim("m-hop")}><g transform="translate(160 118)"><rect x="-8" y="-14" width="16" height="22" rx="4" fill="{COL["bat"]}" stroke="{INK}" stroke-width="2"/>'
         f'<circle cx="-3" cy="-7" r="1.5" fill="{INK}"/><circle cx="3" cy="-7" r="1.5" fill="{INK}"/><path d="M-12 12h24" stroke="{RED}" stroke-width="4" stroke-linecap="round"/></g></g>')
add('02c-bored-surfer', 'A tiny surfer clicks along three linked pages, then jumps to a faraway page.', '#b8cec0',
    body + t(60, 50, 'click, click…', 'b-s') + f'<g{anim("m-wiggle")}>' + t(190, 38, 'BORED!', 'sfx-s') + '</g>' + t(200, 200, 'd = 0.85', 'mono-s'))

# ---------- strip 3: the librarian who walks the web ----------

add('03a-address-list', 'A librarian with glasses holds a clipboard listing web addresses.', '#efd5b7',
    buddy(90, 128, 'lib', COL['looker'], 1.15, label_cls='w-s')
    + f'<circle cx="83" cy="113" r="6" fill="none" stroke="{INK}" stroke-width="2"/><circle cx="97" cy="113" r="6" fill="none" stroke="{INK}" stroke-width="2"/>'
    + f'<g{anim("m-swing")}>' + rect(178, 40, 112, 150, '#fff8e3', 2.5, 6) + rect(210, 32, 48, 14, '#a27c55', 2, 3)
    + ''.join(t(188, 78 + i * 28, f'www.{n}', 'mono-s', 'start') for i, n in enumerate(['a.com', 'b.org', 'c.net', 'd.edu']))
    + '</g>' + bubble(14, 14, 138, 36, ['Visit these!'], (88, 100)))

body = ''
for i, x in enumerate([60, 160, 260]):
    body += buddy(x, 52, '', COL['looker'], .62)
    for j, dx in enumerate([-34, -12, 12, 34]):
        px = x + dx * 1.3 + (j - 1.5) * 4
        body += f'<path class="m-dash" d="M{x} 78L{px:g} 168" fill="none" stroke="{EIGHT[(i * 3 + j) % 8]}" stroke-width="2" style="animation-delay:{(i + j) * .2:g}s"/>' + page(px, 184, 0, .5, '#fff8e3', 2)
add('03b-many-librarians', 'Three librarians each hold many threads that lead down to different web pages.', '#c2d4cf',
    body + t(160, 20, '~300 connections each', 'b-s') + t(160, 214, '100+ PAGES A SECOND', 'micro', style=f'fill:{RED}'))

add('03c-the-shelf', 'A page is squeezed in a press, given a docID number tag, and placed on a shelf.', '#f0e3c6',
    rect(38, 58, 22, 70, '#b5ab92', 2.5) + rect(110, 58, 22, 70, '#b5ab92', 2.5)
    + f'<g{anim("m-pulse")}>' + page(85, 94, 0, .9, '#fff8e3', 3) + '</g>'
    + line('M72 24v30M98 24v30', INK, 3) + t(85, 150, 'squeeze!', 'b-s')
    + line('M140 94h26', RED, 3.5, 'marker-end="url(#ah)"')
    + f'<path d="M190 66h72v26h-72z" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>' + t(226, 85, 'docID 42', 'mono-s')
    + line('M226 92v14', INK, 2)
    + rect(184, 176, 124, 8, '#a27c55', 2.5)
    + ''.join(f'<rect x="{192 + i * 22}" y="{132 - (i % 2) * 6}" width="17" height="{44 + (i % 2) * 6}" fill="{c}" stroke="{INK}" stroke-width="2"/>' for i, c in enumerate(['#f7d79b', '#a2c2a7', '#c3b2d8', '#efae78', '#82acad']))
    + rect(207, 106, 20, 26, '#fff8e3', 2) + t(250, 208, 'THE REPOSITORY', 'micro'))

# ---------- strip 4: a book index for the web ----------

words = [('the', 0, 0), ('web', 1, 1), ('is', 0, 2), ('big', 1, 3)]
body = rect(24, 30, 150, 150, '#fff8e3', 2.5)
for i, (w, hl, _) in enumerate(words):
    y = 48 + i * 34
    if hl:
        body += f'<rect x="34" y="{y}" width="64" height="24" fill="#ffe597" stroke="{INK}" stroke-width="1.5"/>'
    body += t(40, y + 19, w, 'w' if hl else 'b', 'start')
    body += line(f'M104 {y + 12}H196', RED if hl else INK, 1.5) if hl else ''
body += rect(196, 60, 112, 36, '#f7d79b', 2) + t(252, 83, 'pos 2 · BIG', 'b-s') + rect(196, 126, 112, 36, '#a2c2a7', 2) + t(252, 149, 'pos 4 · small', 'b-s')
body += line('M98 94H196', RED, 2) + line('M98 150H196', RED, 2)
add('04a-write-down-words', 'A page with two highlighted words, each with a small note beside it giving position and size.', '#efd5b7',
    body + t(100, 200, 'each note = a "hit"', 'b-s') )

left = rect(16, 40, 118, 110, '#fff8e3', 2.5) + t(75, 30, 'PAGE → WORDS', 'micro') + ''.join(t(26, 70 + i * 32, tx, 'w-s', 'start') for i, tx in enumerate(['P1 → cat', 'P2 → dog', 'P3 → cat']))
right = rect(186, 40, 118, 110, '#fff8e3', 2.5) + t(245, 30, 'WORD → PAGES', 'micro', style=f'fill:{RED}') + ''.join(t(196, 70 + i * 32, tx, 'w-s', 'start') for i, tx in enumerate(['cat → P1 P3', 'dog → P2', '']))
add('04b-flip-it', 'A page-to-words table flips over into a word-to-pages table.', '#b8cec0',
    left + right + f'<g{anim("m-wiggle")}>' + line('M146 70Q160 36 176 70', RED, 4, 'marker-end="url(#ah)"')
    + line('M176 124Q160 158 146 124', RED, 4, 'marker-end="url(#ah)"') + '</g>' + t(160, 104, 'FLIP', 'sfx-s')
    + t(160, 200, 'like the index in a book', 'b-s'))

cells = ''.join(f'<rect x="{80 + i * 80}" y="80" width="80" height="60" fill="{c}" stroke="{INK}" stroke-width="3"/>' for i, c in enumerate(['#f7d79b', '#a2c2a7']))
segs = ''.join(f'<path d="M{80 + k * 20} 80v60" stroke="{INK}" stroke-width="1" opacity=".5"/>' for k in range(1, 8) if k != 4)
add('04c-two-bytes', 'A tiny package made of two boxes, labelled hit.', '#c3b2d8',
    cells + segs + t(120, 116, 'byte 1', 'b-s') + t(200, 116, 'byte 2', 'b-s')
    + f'<g{anim("m-bob")}>' + rect(120, 24, 80, 32, '#fff8e3', 2.5, 8) + t(160, 47, 'a hit', 'w') + '</g>'
    + t(160, 176, '2 BYTES, THAT’S ALL', 'micro') + t(80, 70, 'tiny!', 'sfx-s', style=''))

# ---------- strip 5: answering one search ----------

add('05a-type-words', 'A search box with the words bill clinton, and two lists of pages coming out beneath it.', '#efd5b7',
    rect(30, 20, 260, 44, '#fff8e3', 3, 22) + t(160, 50, 'bill clinton', 'w') + f'<g{anim("m-blink")}><rect x="236" y="30" width="3" height="24" fill="{INK}"/></g>'
    + line('M110 70L80 98', INK, 2.5, 'marker-end="url(#ah)"') + line('M210 70L240 98', INK, 2.5, 'marker-end="url(#ah)"')
    + t(80, 118, 'bill', 'w', style=f'fill:{RED}') + t(240, 118, 'clinton', 'w', style=f'fill:{TEAL}')
    + ''.join(page(52 + i * 28, 168, 0, .7, '#e6efe4', 2) for i in range(3)) + ''.join(page(212 + i * 28, 168, 0, .7, '#e5dcef', 2) for i in range(3))
    + t(160, 212, 'each word has a list of pages', 'micro'))

cards = ''
for i, (x, a, b) in enumerate([(54, 30, 32), (160, 14, 20), (266, 22, 56)]):
    cards += page(x, 62, 0, 1.0, '#fff8e3', 3)
    cards += (f'<rect x="{x - 40}" y="116" width="80" height="16" fill="#ddcfb0" stroke="{INK}" stroke-width="1.5"/>'
              f'<rect class="m-meter" x="{x - 40}" y="116" width="{a}" height="16" fill="{TEAL}" style="animation-delay:{i * .2:g}s"/>'
              f'<rect class="m-meter" x="{x - 40 + a}" y="116" width="{b}" height="16" fill="{RED}" style="animation-delay:{i * .2 + .1:g}s"/>')
add('05b-find-and-score', 'Three matching pages, each with a score bar made of a teal words part and a red PageRank part.', '#f0e3c6',
    cards + t(108, 170, 'words', 'b-s', style=f'fill:{TEAL}') + t(160, 170, '+', 'w') + t(222, 170, 'PageRank', 'b-s', style=f'fill:{RED}')
    + t(160, 28, 'ALL YOUR WORDS?', 'micro') + t(160, 204, 'score = both added up', 'b-s'))

rows = ''
for i, (w, c) in enumerate([(150, '#f7d79b'), (124, '#e6efe4'), (96, '#e5dcef')]):
    y = 26 + i * 52
    rows += rect(20, y, 170, 42, c, 2.5, 4) + t(42, y + 29, f'{i + 1}', 'w') + f'<rect x="58" y="{y + 12}" width="{w - 50}" height="8" fill="{INK}" opacity=".55"/><rect x="58" y="{y + 26}" width="{(w - 50) * .6:g}" height="6" fill="{INK}" opacity=".3"/>'
rows += star(172, 30, 1.2)
watch = (f'<g transform="translate(252 104)"><rect x="-6" y="-56" width="12" height="9" fill="#a27c55" stroke="{INK}" stroke-width="2"/>'
         f'<circle r="38" fill="#fff8e3" stroke="{INK}" stroke-width="3.5"/><path d="M0 -30v6M30 0h-6M0 30v-6M-30 0h6" stroke="{INK}" stroke-width="2.5"/>'
         f'<g class="m-spin-slow"><path d="M0 0L0 -26" stroke="{RED}" stroke-width="3" stroke-linecap="round"/></g><circle r="4" fill="{INK}"/></g>')
add('05c-top-results', 'A ranked results list, numbers one to three, beside a stopwatch.', '#b8cec0',
    rows + watch + t(252, 176, '0.06 s', 'mono') + t(252, 198, 'cached', 'b-s'))

# ---------- story panels (440x215) ----------

def story_plate(bg, body, caption):
    return (f'<rect width="440" height="215" fill="{bg}"/><rect width="440" height="215" fill="url(#dots)" opacity=".22"/>' + body
            + f'<rect x="90" y="172" width="260" height="32" fill="{CREAM}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
            + t(220, 195, caption, 'b-s')
            + f'<path d="M4 6Q220 1 436 5Q440 108 435 210Q220 214 5 210Q1 108 4 6Z" fill="none" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>')


def add_story(name, title, bg, body, caption):
    STORY.append((f'story/{name}.svg', title, story_plate(bg, body, caption)))


shelves = ''
rr = random.Random(3)
for r, y in enumerate([60, 112, 160]):
    shelves += rect(20, y, 400, 7, '#a27c55', 2.5)
    for k in range(13):
        x = 36 + k * 30 + rr.uniform(-4, 4)
        shelves += page(x, y - 22 + rr.uniform(-2, 2), rr.uniform(-22, 22), .85, ['#fff8e3', '#f7d79b', '#e6efe4', '#e5dcef', '#f0e3c6'][(k + r) % 5], 2)
spill = f'<g{anim("m-bob")}>' + page(392, 176, 28, .9, '#fff8e3', 3) + '</g>' + page(32, 190, -40, .8, '#f0e3c6', 3)
add_story('01-too-many', 'Three messy shelves overflowing with tilted pages, with pages spilling onto the floor.', '#efd5b7',
          shelves + spill + rect(130, 8, 180, 22, CREAM, 2) + t(220, 24, 'NEW PAGES EVERY MINUTE', 'micro', style=f'fill:{RED}') + f'<g{anim("m-wiggle")}>' + t(396, 40, '!?', 'sfx') + '</g>',
          'Shelves that nobody sorted.')

voters = [(60, 40, 14, 2), (50, 110, 20, 3), (110, 150, 12, 2), (130, 30, 34, 6)]
body = ''
for (x, y, r, w) in voters:
    body += arrow((x, y), r, (330, 90), 36, RED if w == 6 else INK, w)
body += ''.join(node(x, y, r, '#f0e3c6' if r < 30 else '#a2c2a7') for x, y, r, _ in voters)
body += page(330, 90, 0, 1.5, '#f7d79b', 3) + f'<g{anim("m-twinkle")}>' + star(330, 36, 1.5) + star(304, 46, 1.1) + star(356, 46, 1.1) + '</g>'
add_story('02-link-is-a-vote', 'Four page circles of different sizes send arrows to one page; the arrow from the biggest circle is the thickest.', '#c3b2d8',
          body + t(130, 80, 'BIG', 'micro') + t(396, 148, 'top of the list', 'b-s', 'end'), 'Big votes and small votes.')

boxes = ''
for i, (x, lab, c) in enumerate([(30, 'CRAWL', '#a2c2a7'), (160, 'INDEX', '#f7d79b'), (290, 'ANSWER', '#c3b2d8')]):
    boxes += rect(x, 40, 120, 100, c, 3, 8) + t(x + 60, 132, lab, 'micro')
    if i < 2:
        boxes += line(f'M{x + 122} 90h6', RED, 3.5, 'marker-end="url(#ah)"')
boxes += (buddy(90, 76, '', COL['looker'], .55) + page(70, 100, 0, .45, '#fff8e3', 2) + page(110, 100, 0, .45, '#fff8e3', 2)
          + t(220, 88, 'cat → P1 P3', 'mono-s', style='') + t(220, 108, 'dog → P2', 'mono-s')
          + ''.join(f'<rect x="{318 + i * 0}" y="{60 + i * 22}" width="64" height="16" fill="#fff8e3" stroke="{INK}" stroke-width="1.5"/>' for i in range(3)) + star(398, 68, .9))
add_story('03-walk-file-lookup', 'Three boxes in a row joined by arrows: crawl, index, answer.', '#b8cec0', boxes + t(220, 28, 'FETCH → FILE → LOOK UP', 'micro', style=f'fill:{RED}'),
          'Fetch it, file it, look it up.')

res = ''
for i, (w, c) in enumerate([(210, TEAL), (176, TEAL), (150, TEAL), (118, TEAL)]):
    y = 40 + i * 30
    res += rect(60, y, 320, 24, '#fff8e3', 2.2, 3) + t(76, y + 18, f'{i + 1}', 'w-s', 'start') + f'<rect class="m-meter" x="100" y="{y + 6}" width="{w}" height="12" fill="{c}" style="animation-delay:{i * .15:g}s"/>'
res += star(366, 52, 1.1)
add_story('04-first-test', 'A short list of four search results, each with a bar beside it.', '#efd5b7',
          res + t(220, 26, 'SEARCH: “bill clinton”', 'micro', style=f'fill:{RED}') + f'<g{anim("m-pulse")}>' + t(380, 164, '24M', 'sfx-s') + '</g>',
          '24 million pages, one first test.')

# ---------- fact icons (160x100) ----------

def icon(name, title, body):
    ICONS.append((f'facts/{name}.svg', title, f'<rect width="160" height="100" fill="#f6f0df"/><rect width="160" height="100" fill="url(#dots)" opacity=".22"/>' + body))


rr = random.Random(11)
icon('pages', 'A small heap of web pages with the label 24 million.',
     ''.join(page(40 + (k % 5) * 20 + rr.uniform(-3, 3), 70 - (k // 5) * 13 + rr.uniform(-2, 2), rr.uniform(-25, 25), .5, ['#fff8e3', '#f7d79b', '#e6efe4', '#e5dcef'][k % 4], 2) for k in range(15))
     + star(100, 28, 1.1) + t(80, 94, '24 MILLION PAGES', 'micro'))

pts = [(30, 30), (70, 20), (120, 28), (40, 66), (92, 56), (136, 64)]
ed = [(0, 1), (1, 2), (0, 3), (1, 4), (2, 4), (3, 4), (4, 5), (2, 5), (0, 4)]
icon('links', 'A web of dots joined by many lines, labelled 518 million links.',
     ''.join(line(f'M{pts[a][0]} {pts[a][1]}L{pts[b][0]} {pts[b][1]}', INK, 2) for a, b in ed)
     + ''.join(f'<circle cx="{x}" cy="{y}" r="7" fill="{c}" stroke="{INK}" stroke-width="2"/>' for (x, y), c in zip(pts, ['#f7d79b', '#a2c2a7', '#c3b2d8', '#efae78', '#82acad', '#f0e3c6']))
     + t(80, 94, '518 MILLION LINKS', 'micro'))

icon('damping', 'A dial whose needle points near the top end at 0.85.',
     f'<path d="M24 76A56 56 0 0 1 136 76" fill="none" stroke="{INK}" stroke-width="3"/><path d="M24 76A56 56 0 0 1 126 46" fill="none" stroke="{TEAL}" stroke-width="8" opacity=".6"/>'
     + ''.join(f'<path d="M{80 - 56 * math.cos(math.radians(a)):.0f} {76 - 56 * math.sin(math.radians(a)):.0f}L{80 - 48 * math.cos(math.radians(a)):.0f} {76 - 48 * math.sin(math.radians(a)):.0f}" stroke="{INK}" stroke-width="2"/>' for a in range(0, 181, 30))
     + f'<g transform="translate(80 76) rotate(52)"><path d="M0 0L-46 0" stroke="{RED}" stroke-width="3.5" stroke-linecap="round"/></g><circle cx="80" cy="76" r="5" fill="{INK}"/>'
     + t(80, 96, 'd = 0.85', 'mono-s'))

icon('bytes', 'Two small boxes side by side labelled 2 bytes.',
     rect(24, 26, 56, 40, '#f7d79b', 3) + rect(80, 26, 56, 40, '#a2c2a7', 3)
     + ''.join(f'<path d="M{24 + k * 7} 26v40" stroke="{INK}" stroke-width="1" opacity=".4"/>' for k in range(1, 16) if k != 8)
     + t(52, 52, 'B1', 'w-s') + t(108, 52, 'B2', 'w-s') + t(80, 90, '2 BYTES = 1 HIT', 'micro'))

icon('storage', 'A big box of 147.8 gigabytes squeezed into a smaller box of 53.5 gigabytes.',
     rect(10, 18, 62, 52, '#efae78', 3) + t(41, 50, '147.8', 'w-s') + line('M78 44h24', RED, 3.5, 'marker-end="url(#ah)"')
     + rect(108, 34, 40, 34, '#a2c2a7', 3) + t(128, 56, '53.5', 'w-s') + t(80, 90, 'GB: SQUEEZED', 'micro'))

icon('seconds', 'A stopwatch with a range from 1 to 10 seconds.',
     f'<rect x="38" y="6" width="12" height="9" fill="#a27c55" stroke="{INK}" stroke-width="2"/><circle cx="44" cy="50" r="32" fill="#fff8e3" stroke="{INK}" stroke-width="3"/>'
     f'<path d="M44 24v6M70 50h-6M44 76v-6M18 50h6" stroke="{INK}" stroke-width="2.5"/><g class="m-spin-slow"><path d="M44 50V28" stroke="{RED}" stroke-width="3" stroke-linecap="round"/></g><circle cx="44" cy="50" r="3.5" fill="{INK}"/>'
     + t(112, 48, '1–10', 'mono') + t(112, 68, 'SECONDS', 'micro'))

if __name__ == '__main__':
    write(OUT, 'pile.svg', standalone('0 0 600 340', plate('#b8cec0', 'PLATE 01 / PILE', pile_body, 'So many pages, so few good ones.'),
          'A huge pile of web pages with one tiny gold page buried inside. Below: So many pages, so few good ones.', defs=DEFS))
    write(OUT, 'votes.svg', standalone('0 0 600 340', plate('#efd5b7', 'PLATE 02 / VOTES', votes_body, 'Pages point at the pages they trust.'),
          'Small page circles with arrows pointing at one big circle in the middle. Below: Pages point at the pages they trust.', defs=DEFS))
    print(f'wrote 2 lead plates to {OUT}')

    import json
    seed = json.loads((ROOT.parent.parent.parent / 'data' / 'seed' / 'papers' / 'google-search.json').read_text())
    ALT = {}

    def walk(o):
        if isinstance(o, dict):
            if 'src' in o and o.get('alt'):
                ALT[o['src'].replace('google-search/', '', 1)] = o['alt']
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(seed)   # media.alt in the story JSON is the single source of truth for <title>
    PANELS[:] = [(n, ALT.get(n, ti), b) for n, ti, b in PANELS]
    STORY[:] = [(n, ALT.get(n, ti), b) for n, ti, b in STORY]
    ICONS[:] = [(n, ALT.get(n, ti), b) for n, ti, b in ICONS]
    for name, title, body in PANELS:
        write(ROOT, name, standalone('0 0 320 220', body, title, defs=DEFS))
    for name, title, body in STORY:
        write(ROOT, name, standalone('0 0 440 215', body, title, defs=DEFS))
    for name, title, body in ICONS:
        write(ROOT, name, standalone('0 0 160 100', body, title, defs=DEFS))
    print(f'wrote {len(PANELS)} comic panels, {len(STORY)} story panels and {len(ICONS)} icons to {ROOT}')
