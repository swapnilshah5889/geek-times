"""Draws the media for "Migrating Messenger storage to optimize performance" (Facebook Engineering, 2018).

Run from the repo root:  python3 tools/draw_messenger_myrocks.py
Writes standalone SVGs to backups/media/messenger-myrocks/{lead,story,comic,facts}/. Every media.src in
data/seed/papers/messenger-myrocks.json must be written. Real numbers (90%, 6 to 3 copies, 50x, 99.9%, 10%,
2010) come from the post and are stamped "From the source · reported". Nothing else is numeric.
"""
import json
from pathlib import Path

from media_kit import COMIC_CSS, COMIC_DEFS, INK, RED, anim, bubble, buddy, gear, standalone, t, write
from draw_cassandra import (DEFS, CREAM, GOLD, GREEN, GREY, ORANGE, PAPER, PURPLE,
                            SAND, TEAL, WOOD, arrow, folder, magnifier, panel_bg, prune_css)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'backups' / 'media' / 'messenger-myrocks'
SEED = ROOT / 'data' / 'seed' / 'papers' / 'messenger-myrocks.json'
BLUE = '#82acad'
CSS = COMIC_CSS + ('.st{font:italic 12px Georgia,serif;fill:#5a5242}.big{font:bold 34px Georgia,serif}'
                   '.huge{font:bold 52px Georgia,serif}.red{fill:#a13324}')
STAMP = 'From the source · reported'
BOOKS = [SAND, GREEN, PURPLE, ORANGE, BLUE, '#d98b8b']


def svg(vb, body, title):
    return standalone(vb, body, title, css=prune_css(CSS, body), defs=DEFS if 'ah)' in body else COMIC_DEFS)


# ---------- helpers ----------
def R(x, y, w, h, fill, rx=3, sw=2.5, extra=''):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx}" fill="{fill}" stroke="{INK}" stroke-width="{sw}" {extra}/>'


def L(d, sw=2.5, col=INK, fill='none', extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def C(x, y, r, fill, sw=2.5):
    return f'<circle cx="{x:g}" cy="{y:g}" r="{r:g}" fill="{fill}" stroke="{INK}" stroke-width="{sw}"/>'


def stamp(x, y, text=STAMP, anchor='middle'):
    return t(x, y, text, 'st', anchor)


def shelf(x, y, w, h, rows, top=WOOD, shiny=False, worn=False):
    g = R(x, y, w, h, top, 4, 3)
    rh = h / rows
    for r in range(rows):
        yy = y + r * rh
        n = max(3, int((w - 10) / 17))
        for i in range(n):
            bh = rh - 12 - (i * 7 + r * 3) % 6
            g += R(x + 6 + i * (w - 12) / n, yy + rh - 6 - bh, (w - 12) / n - 2, bh, BOOKS[(i + r) % 6], 1, 1.6)
        g += L(f'M{x} {yy + rh - 4:g}h{w}', 3)
    if shiny:
        g += L(f'M{x + 8} {y + 8}l10 -4M{x + 10} {y + 14}l6 -2', 2, '#fff8e3')
    if worn:
        g += L(f'M{x + w - 14} {y + 4}l8 12M{x + 6} {y + h - 18}l10 -6', 1.6, '#8a6a42')
    return g


def bolt(x, y, s=1):
    return f'<path transform="translate({x} {y}) scale({s})" d="M0 -16L-10 3H-2L-5 16L10 -5H2Z" fill="{GOLD}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'


def phone(x, y, s=1, lines=3, color=GREEN):
    g = f'<g transform="translate({x} {y}) scale({s})">' + R(-28, -48, 56, 96, '#4a463a', 9, 3) + R(-23, -38, 46, 74, PAPER, 3, 1.5)
    for i in range(lines):
        bx = -18 if i % 2 == 0 else -2
        g += R(bx, -33 + i * 20, 24, 14, color if i % 2 else SAND, 6, 1.6)
    return g + '</g>'


def box(x, y, w=44, h=22, fill=ORANGE):
    return R(x, y, w, h, fill, 2, 2.5) + L(f'M{x + w / 2 - 6:g} {y}v6h12v-6', 1.8)


def truck(x, y, s=1, load=True):
    g = f'<g transform="translate({x} {y}) scale({s})">' + R(-28, -18, 38, 26, WOOD, 3) + R(10, -10, 18, 18, TEAL, 3) + C(-16, 10, 6, INK, 1.5) + C(18, 10, 6, INK, 1.5)
    if load:
        g += R(-22, -28, 14, 10, SAND, 1, 2) + R(-8, -28, 14, 10, GREEN, 1, 2)
    return g + '</g>'


def camera(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})">' + R(-26, -16, 52, 34, '#6d695c', 6, 3) + R(-10, -24, 18, 9, GREY, 2, 2)
            + C(0, 2, 11, '#d8e6e3') + C(0, 2, 5, INK, 1.5) + '</g>')


def clock(x, y, r=22):
    return C(x, y, r, PAPER, 3) + L(f'M{x} {y}V{y - r * .6:g}M{x} {y}l{r * .45:g} {r * .2:g}', 2.5)


def lines(x, y, n, w=34, gap=10):
    return ''.join(L(f'M{x} {y + i * gap}h{w}', 1.8, INK, extra='opacity=".5"') for i in range(n))


def clip(x, y, s=1):
    g = f'<g transform="translate({x} {y}) scale({s})">' + R(-20, -26, 40, 52, PAPER, 3, 2.5) + R(-8, -31, 16, 9, GREY, 2, 2)
    for i in range(4):
        g += L(f'M-14 {-12 + i * 10}l3 3 5 -6', 1.8, GREEN if False else '#4f7a66') + L(f'M-3 {-10 + i * 10}h13', 1.6, INK, extra='opacity=".5"')
    return g + '</g>'


def letter(x, y, rot=0, s=1):
    return (f'<g transform="translate({x:g} {y:g}) rotate({rot}) scale({s})">' + R(-13, -9, 26, 18, PAPER, 2, 2) + L('M-13 -9L0 2L13 -9', 2) + '</g>')


def snail(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})">' + f'<ellipse cx="6" cy="10" rx="26" ry="7" fill="#c9b99a" stroke="{INK}" stroke-width="2.5"/>'
            + C(2, -2, 14, ORANGE) + L('M2 -2m-6 0a6 6 0 1 1 6 6', 2) + L('M30 6l6-14M26 4l-2-12', 2) + '</g>')


def rabbit(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})">' + f'<ellipse cx="0" cy="6" rx="24" ry="13" fill="#e8e0cc" stroke="{INK}" stroke-width="2.5"/>'
            + C(22, -6, 10, '#e8e0cc') + f'<ellipse cx="22" cy="-26" rx="4" ry="13" fill="#e8e0cc" stroke="{INK}" stroke-width="2.5"/><ellipse cx="30" cy="-24" rx="4" ry="12" fill="#e8e0cc" stroke="{INK}" stroke-width="2.5"/>'
            + f'<circle cx="25" cy="-8" r="1.8" fill="{INK}"/>' + C(-24, 4, 5, '#fff8e3', 2) + '</g>')


def stackbox(cx, base, n, w=50, h=20):
    return ''.join(box(cx - w / 2, base - (i + 1) * h, w, h, [ORANGE, SAND, GREEN][i % 3]) for i in range(n))


def tag(x, y, w, text, cls='w'):
    return R(x - w / 2, y - 16, w, 30, PAPER, 8, 2.5) + t(x, y + 5, text, cls)


def disk(x, y, r=22, spin=True):
    g = C(x, y, r, '#8a867a', 3) + C(x, y, r * .35, PAPER, 2) + L(f'M{x - r * .8:g} {y}a{r * .8:g} {r * .8:g} 0 0 1 {r * .8:g} {-r * .8:g}', 2, '#fff8e3')
    return f'<g class="m-spin">{g}</g>' if spin else g


def cross(x, y, s=1):
    return L(f'M{x - 14 * s:g} {y - 14 * s:g}L{x + 14 * s:g} {y + 14 * s:g}M{x + 14 * s:g} {y - 14 * s:g}L{x - 14 * s:g} {y + 14 * s:g}', 6, RED)


def sparkle(x, y, s=1):
    return f'<use href="#mstar" transform="translate({x} {y}) scale({s})" class="m-twinkle"/>'


def building(x, y, w, h, fill, label=''):
    g = R(x, y, w, h, fill, 3, 3) + R(x + w / 2 - 12, y + h - 34, 24, 34, '#8a6a42', 2, 2.5)
    for i in range(2):
        g += R(x + 10 + i * (w - 36), y + 12, 16, 14, '#f7e9b5', 1, 2)
    if label:
        g += t(x + w / 2, y - 8, label, 'w-s')
    return g


PANELS = []


def add(kind, name, title, bg, body, w, h):
    PANELS.append((f'{kind}/{name}.svg', f'0 0 {w} {h}', title, panel_bg(bg, body, w, h)))


def lead(n, title, bg, body): add('lead', n, title, bg, body, 600, 340)
def story(n, title, bg, body): add('story', n, title, bg, body, 440, 215)
def comic(n, title, bg, body): add('comic', n, title, bg, body, 320, 220)
def icon(n, title, body, bg='#f0e3c6'): add('facts', n, title, bg, body, 160, 100)


# =================== lead ===================
def ghost(x, y, w, h, k):
    return ''.join(R(x + j * 9, y - j * 8, w, h, '#cdc4ab', 4, 2.5) for j in range(k, 0, -1))


lead('old-shelf-new-shelf', 'An old shelf with six copies behind it and a smaller new shelf with three copies.', '#f0e3c6',
     ghost(60, 110, 210, 170, 5) + shelf(60, 110, 210, 170, 4, WOOD, worn=True)
     + t(165, 308, 'Old shelf: six copies', 'w') + t(445, 308, 'New shelf: three copies', 'w')
     + ghost(350, 150, 120, 130, 2) + shelf(350, 150, 120, 130, 3, '#cfd8d3', shiny=True) + bolt(505, 140, 1.3) + sparkle(520, 190, 1.3)
     + arrow('M285 175Q315 140 345 170') + folder(315, 138, 40, 28, SAND, -8)
     + t(300, 30, 'Same books. Fewer, quicker shelves.', 'w') + stamp(300, 330, STAMP + ' · six copies down to three'))

lead('ninety-percent', 'A tall stack of boxes shrinks to a short stack tagged 90 percent less.', '#f0e3c6',
     stackbox(170, 290, 10, 90, 24).replace('width="90"', 'width="90"') + t(170, 322, 'Before', 'w')
     + stackbox(430, 290, 1, 90, 24) + t(430, 322, 'After', 'w')
     + arrow('M240 150Q300 90 380 190') + tag(300, 110, 130, '90% less', 'w')
     + buddy(540, 250, 'ok', SAND, 1.2) + stamp(300, 40, STAMP + ' · storage use'))

# =================== story ===================
story('01-open-library', 'A busy library stays open while movers carry boxes to a new building across the road.', '#e8e8d2',
      building(20, 58, 130, 110, '#e5cfa2', 'Open library') + building(300, 58, 120, 110, '#cfd8d3', 'New building')
      + R(0, 172, 440, 43, '#bdb7a4', 0, 0) + L('M0 172H440', 3) + L('M0 194h440', 2, '#f6f0df', extra='stroke-dasharray="12 10"')
      + buddy(60, 190, 'reader', GREEN, .6) + buddy(110, 190, 'reader', PURPLE, .6)
      + truck(215, 188, 1.1) + arrow('M170 150H285') + t(228, 38, 'Doors never close', 'w'))

story('02-swap-shelves', 'An old slow shelf with spinning wheels beside a new fast shelf with a lightning bolt; a librarian points at the new one.', '#f0e3c6',
      shelf(30, 50, 130, 120, 3, WOOD, worn=True) + gear(50, 38, 11) + gear(142, 38, 9, 1) + t(95, 192, 'Old: slow', 'w')
      + shelf(280, 50, 130, 120, 3, '#cfd8d3', shiny=True) + bolt(345, 30, 1.2) + t(345, 192, 'New: fast', 'w')
      + buddy(220, 130, 'pick', PURPLE, 1.1) + L('M236 124L270 108', 3) + bubble(180, 24, 100, 34, ['This one.'], (222, 98), 'b-s'))

story('03-two-lanes', 'Two lanes into a new building: a short lane to a quiet door for most people, and a long lane with a waiting room of queued messages.', '#e8e8d2',
      building(300, 50, 120, 120, '#cfd8d3', 'New building')
      + R(0, 74, 292, 34, '#d6cfb8', 0, 0) + L('M0 74H292M0 108H292', 2.5) + arrow('M60 91H296', False)
      + t(120, 66, 'Short lane: most people', 'b-s') + buddy(50, 91, 'user', GREEN, .5)
      + R(0, 140, 215, 34, '#d6cfb8', 0, 0) + L('M0 140H215M0 174H215', 2.5)
      + R(215, 124, 84, 66, '#f7d79b', 4, 2.5) + t(257, 119, 'Waiting room', 'micro')
      + ''.join(letter(18 + i * 30, 157, 0, .8) for i in range(6)) + letter(257, 157, 0, .9) + arrow('M280 157H300', False)
      + t(120, 206, 'Long lane: messages queue', 'b-s'))

story('04-evidence', 'A scoreboard of three boards: 90 percent less storage, six copies down to three, and reads 50 times faster.', '#f0e3c6',
      ''.join(R(14 + i * 140, 24, 128, 150, PAPER, 8, 3) for i in range(3))
      + t(78, 70, '90%', 'big') + t(78, 92, 'less storage', 'b-s') + ''.join(R(58, 168 - j * 6, 40, 6, '#e6dcc2', 1, 1.2) for j in range(1, 10)) + R(58, 168, 40, 6, ORANGE, 1, 2)
      + t(218, 70, '6 to 3', 'big') + t(218, 92, 'copies', 'b-s') + folder(190, 134, 30, 22, SAND) + folder(246, 134, 30, 22, GREEN) + arrow('M206 134H232', False)
      + t(358, 70, '50x', 'big') + t(358, 92, 'faster reads', 'b-s') + snail(330, 140, .7) + rabbit(388, 136, .7)
      + stamp(220, 200))

# =================== comics ===================
comic('01a-old-shelf', 'A big wooden shelf full of folders with a worn label that says since 2010.', '#f0e3c6',
      shelf(40, 30, 240, 150, 3, WOOD, worn=True) + R(110, 184, 100, 28, PAPER, 5, 2.5) + t(160, 204, 'Since 2010', 'w-s') + stamp(160, 18, 'From the source · reported', 'middle'))

comic('01b-busy-disk', 'A tired librarian runs between shelves with a long queue of folders; a bubble says too slow to search.', '#e8e8d2',
      shelf(20, 70, 90, 110, 2, WOOD) + shelf(210, 70, 90, 110, 2, WOOD) + buddy(160, 150, 'tired', PURPLE, 1) + L('M138 160l-14 14M182 160l14 14', 2.5)
      + ''.join(folder(60 + i * 34, 198, 26, 18, SAND) for i in range(5)) + bubble(70, 8, 180, 34, ['Too slow to search!'], (150, 118), 'b-s'))

comic('01c-new-shelf', 'A neat new shelf with a lightning bolt; a phone beside it shows a magnifying glass finding a message.', '#e8eee2',
      shelf(24, 40, 150, 140, 3, '#cfd8d3', shiny=True) + bolt(180, 40, 1.2) + phone(250, 110, 1, 3) + magnifier(262, 82, .5) + t(98, 204, 'New shelf', 'w-s'))

comic('02a-flash', 'A spinning disk crossed out on the left and a small flat flash card with a sparkle on the right.', '#f0e3c6',
      disk(80, 100, 44) + cross(80, 100, 2) + R(184, 70, 90, 62, '#6d9a9a', 6, 3) + L('M204 70v-16M224 70v-16M244 70v-16', 4, GREY)
      + sparkle(268, 66, 1.6) + sparkle(190, 142, 1.1) + t(80, 176, 'Spinning disk', 'b-s') + t(229, 176, 'Flash card', 'b-s'))

comic('02b-squeeze', 'A folder gets squeezed by a clamp into a thin folder with a small zip on it.', '#e8e8d2',
      folder(64, 110, 76, 60, SAND) + R(110, 80, 14, 60, GREY, 3, 3) + R(166, 80, 14, 60, GREY, 3, 3) + L('M124 110h-0M180 110h0', 3)
      + arrow('M132 110H160', False) + folder(250, 110, 30, 60, SAND) + L('M250 88v44', 2, INK, extra='stroke-dasharray="3 3"') + t(250, 168, 'zip', 'mono-s')
      + t(160, 36, 'Squeeze it small', 'w'))

comic('02c-three-copies', 'Six stacked folders on the left, three on the right, with a happy accountant holding a clipboard.', '#e8eee2',
      ''.join(folder(60, 168 - i * 22, 66, 26, [SAND, GREEN, PURPLE][i % 3]) for i in range(6)) + t(60, 204, '6 copies', 'w-s')
      + arrow('M110 110H150', False) + ''.join(folder(200, 168 - i * 22, 66, 26, [SAND, GREEN, PURPLE][i % 3]) for i in range(3)) + t(200, 204, '3 copies', 'w-s')
      + buddy(278, 150, 'ok', GREEN, .55) + clip(286, 100, .7) + stamp(160, 22, 'From the source · reported'))

comic('03a-states', 'Three signs on a path: Not moved, Both shelves, Done. A small figure walks along it carrying a folder.', '#e8e8d2',
      L('M20 150H300', 4, '#a08a60') + ''.join(R(18 + i * 100, 40 + (i % 2) * 6, 86, 54, PAPER, 5, 2.5) + L(f'M{61 + i * 100} {94 + (i % 2) * 6}V150', 3)
                                              + t(61 + i * 100, 72 + (i % 2) * 6, ['Not moved', 'Both shelves', 'Done'][i], 'w-s') for i in range(3))
      + buddy(150, 170, 'you', GREEN, .6) + folder(172, 148, 26, 18, SAND) + t(160, 16, 'Three states', 'w-s').replace('Three states', 'Each account in a state'))

comic('03b-check-again', 'A librarian compares a counter before and after copying; the numbers differ, so the librarian shakes a head and sweeps the new copy away.', '#f0e3c6',
      buddy(70, 110, 'check', PURPLE, 1.1) + R(140, 40, 62, 40, PAPER, 5, 2.5) + t(171, 66, 'before', 'b-s') + R(242, 40, 62, 40, PAPER, 5, 2.5) + t(273, 66, 'after', 'b-s')
      + t(222, 68, '≠', 'big', style='fill:#a13324') + folder(200, 150, 50, 34, SAND, 0) + arrow('M265 190Q230 170 175 190', False)
      + t(228, 120, 'Differ? Start again.', 'b-s'))

comic('03c-compare', 'Two shelves side by side with a folder going into each and a magnifying glass comparing them; a big undo arrow sits below.', '#e8eee2',
      shelf(24, 40, 110, 80, 2, WOOD) + shelf(186, 40, 110, 80, 2, '#cfd8d3', shiny=True) + folder(80, 20, 28, 18, SAND) + folder(240, 20, 28, 18, SAND)
      + magnifier(160, 84, .55) + L('M250 170Q160 215 70 170', 5, RED, extra='marker-end="url(#ah)"') + t(160, 205, 'Easy to undo', 'w-s'))

comic('04a-no-quiet', 'A bot at a desk with a never-ending stream of letters flowing in; a clock has no quiet hour.', '#e8e8d2',
      R(120, 130, 90, 14, WOOD, 3, 3) + buddy(165, 105, 'bot', BLUE, 1) + ''.join(letter(20 + i * 22, 70 + (i % 2) * 14, 0, .7) for i in range(5)) + L('M20 90H110', 3, RED, extra='stroke-dasharray="8 7"')
      + clock(262, 60, 26) + t(262, 106, 'no quiet hour', 'b-s'))

comic('04b-snapshot', 'A camera flashes at a pile of folders; the photo goes into a holding room.', '#f0e3c6',
      camera(66, 90, 1.2) + sparkle(110, 66, 1.6) + ''.join(folder(40 + i * 24, 175 - (i % 2) * 8, 30, 22, BOOKS[i]) for i in range(4))
      + arrow('M110 96H180', False) + R(188, 60, 108, 90, '#d6cfb8', 6, 3) + t(242, 112, 'Holding', 'w-s') + t(242, 132, 'room', 'w-s'))

comic('04c-queue', 'A long line of letters waits in a tube marked Iris; a new shelf at the end takes them one by one.', '#e8eee2',
      R(14, 80, 196, 44, '#cfd8d3', 20, 3) + ''.join(letter(40 + i * 32, 102, 0, .8) for i in range(5)) + t(112, 150, 'Iris', 'w')
      + arrow('M214 102H236', False) + shelf(240, 60, 66, 90, 2, '#cfd8d3', shiny=True) + t(112, 190, 'one by one', 'b-s'))

comic('05a-scheduler', 'A traffic officer with a dial from slow to fast directing small trucks of folders.', '#e8e8d2',
      buddy(160, 100, 'go', ORANGE, 1.1) + L('M190 90l30 -14', 3) + truck(60, 180, .8) + truck(160, 190, .8) + truck(260, 180, .8)
      + L('M60 52a40 40 0 0 1 80 0', 5, '#a2c2a7') + t(54, 68, 'slow', 'b-s', 'end') + t(146, 68, 'fast', 'b-s', 'start').replace('x="146"', 'x="146"')
      + L('M100 52l16 -24', 4, INK))

comic('05b-stop-writing', 'A row of old shelves with the lights going off one by one while new accounts walk to the new shelf.', '#f0e3c6',
      ''.join(shelf(14 + i * 44, 50, 38, 70, 2, '#a8a08a' if i > 0 else WOOD) for i in range(4)) + ''.join(L(f'M{33 + i * 44} 36v8', 3) + C(33 + i * 44, 30, 6, GOLD if i == 0 else '#8a867a', 2) for i in range(4))
      + shelf(214, 50, 90, 90, 2, '#cfd8d3', shiny=True) + buddy(120, 170, 'new', GREEN, .6) + arrow('M148 170H212') + t(160, 206, 'New accounts go new', 'b-s'))

comic('05c-accounting', 'A librarian ticks a long checklist; the old building has a closed sign on the door.', '#e8eee2',
      clip(70, 100, 1.5) + buddy(140, 150, 'tick', PURPLE, .9) + building(200, 60, 100, 110, '#cfd8d3') + R(226, 112, 50, 22, PAPER, 3, 2) + t(251, 128, 'Closed', 'micro')
      + t(160, 206, 'All ticked, doors shut', 'b-s'))

comic('06a-scroll', 'A phone with a scrolling chat and little speed lines; a happy user thumbs up.', '#f0e3c6',
      phone(110, 110, 1.5, 4) + ''.join(L(f'M{60 - i * 6} {70 + i * 22}h-26', 3, TEAL) for i in range(3)) + buddy(246, 150, 'user', GREEN, 1) + L('M262 128l10 -22', 4)
      + t(246, 196, 'Smooth!', 'w'))

comic('06b-switch', 'Two buildings joined by a bridge, a big switch flips by itself while a worker sips tea.', '#e8e8d2',
      building(20, 60, 80, 90, '#e5cfa2') + building(220, 60, 80, 90, '#cfd8d3') + R(100, 112, 120, 12, WOOD, 2, 3)
      + R(138, 22, 44, 30, PAPER, 6, 3) + R(152, 28, 16, 18, GREEN, 4, 2.5) + t(160, 76, 'switch', 'mono-s') + buddy(160, 180, 'tea', PURPLE, .7) + t(160, 208, 'sip', 'b-s').replace('sip', 'Flips by itself'))

comic('06c-search', 'A phone with a search box and a magnifying glass finding one message in a long chat.', '#e8eee2',
      phone(100, 112, 1.5, 4) + R(60, 54, 80, 14, PAPER, 6, 2) + magnifier(212, 100, 1) + letter(252, 70, 8, 1) + t(220, 196, 'Found it!', 'w'))

# =================== facts (160x100) ===================
icon('storage-90', 'A tall stack of boxes next to a very short stack.',
     stackbox(44, 66, 5, 40, 12) + stackbox(116, 66, 1, 40, 12) + t(80, 36, '90% less', 'w-s') + stamp(80, 92))
icon('copies', 'Six folders in a stack, an arrow, and three folders.',
     ''.join(folder(36, 62 - i * 6, 40, 14, BOOKS[i], 0) for i in range(6)) + arrow('M66 48H92', False)
     + ''.join(folder(122, 62 - i * 8, 40, 14, BOOKS[i], 0) for i in range(3)) + t(80, 20, '6 to 3 copies', 'w-s') + stamp(80, 92))
icon('read-50x', 'A slow snail beside a fast rabbit with a stopwatch.',
     snail(34, 56, .8) + rabbit(110, 52, .8) + t(80, 22, '50x faster reads', 'w-s') + stamp(80, 92))
icon('accounts', 'A big crowd walking through a wide door and a few through a small side door.',
     R(14, 40, 80, 36, '#cfd8d3', 3, 2.5) + ''.join(C(26 + i * 14, 58, 5, [GREEN, PURPLE, ORANGE][i % 3], 2) for i in range(5))
     + R(112, 40, 34, 36, '#f7d79b', 3, 2.5) + C(129, 58, 5, GREEN, 2) + t(54, 34, '99.9% normal', 'b-s').replace('class="b-s"', 'class="b-s" style="font-size:12px"')
     + t(129, 34, 'rest', 'micro') + stamp(80, 92))
icon('snapshot', 'A camera and a small slice of a pie chart.',
     camera(42, 48, .75) + sparkle(70, 28, .9) + C(116, 48, 24, PAPER, 2.5) + f'<path d="M116 48V24A24 24 0 0 1 133 31Z" fill="{RED}" stroke="{INK}" stroke-width="2"/>'
     + t(116, 86, '10% of time', 'b-s', style='font-size:12px') + stamp(80, 98).replace('y="98"', 'y="98"'))
icon('since-2010', 'A worn shelf with a small calendar page.',
     shelf(14, 24, 80, 56, 2, WOOD, worn=True) + R(106, 22, 42, 46, PAPER, 4, 2.5) + R(106, 22, 42, 12, RED, 4, 2.5) + t(127, 58, '2010', 'w-s') + stamp(80, 92))


def srcs(doc):
    found = []
    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get('src'), str) and o['src'].startswith('messenger-myrocks/'):
                found.append((o['src'], o['width'], o['height']))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(doc)
    return found


if __name__ == '__main__':
    need = {s: (w, h) for s, w, h in srcs(json.loads(SEED.read_text()))}
    made = {}
    for rel, vb, title, body in PANELS:
        made[rel] = write(OUT, rel, svg(vb, body, title))
    missing = {s.split('/', 1)[1] for s in need} - set(made)
    assert not missing, f'not drawn: {sorted(missing)}'
    for s, (w, h) in need.items():
        assert f'viewBox="0 0 {w} {h}"' in made[s.split('/', 1)[1]].read_text(), s
    print(f'wrote {len(made)} files ({len(need)} unique srcs required); extra: {sorted(set(made) - {s.split("/", 1)[1] for s in need})}')
