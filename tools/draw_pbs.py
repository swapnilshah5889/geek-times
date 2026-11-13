"""Draws the media for "Probabilistically Bounded Staleness for Practical Partial Quorums" (Bailis et al., VLDB 2012).

Run from the repo root:  python3 tools/draw_pbs.py
Writes standalone SVGs to backups/media/pbs/{lead,story,comic,facts}/. Every media.src in data/seed/papers/pbs.json
must be written. Metaphors follow the Cassandra story: desks (replicas), notes, a helper (coordinator), dials.
Drawn numbers (N=3, R/W defaults) come from the paper; model predictions carry the stamp
"From the paper . model prediction"; everything else is unlabelled shape, not data.
"""
import json
import math
import re
from pathlib import Path

from media_kit import COMIC_CSS, COMIC_DEFS, INK, RED, anim, bubble, standalone, t, write
from media_kit import buddy as _buddy


def buddy(x, y, word='', color='#efae78', s=1):
    return _buddy(x, y, word, color, s, label_cls='w-s')

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'backups' / 'media' / 'pbs'
SEED = ROOT / 'data' / 'seed' / 'papers' / 'pbs.json'

CREAM = '#fbf3dc'; TEAL = '#377675'; GREEN = '#a2c2a7'; GOLD = '#ffe597'; WOOD = '#d9b98a'
PAPER = '#fff8e3'; PURPLE = '#c3b2d8'; SAND = '#f7d79b'; ORANGE = '#efae78'; GREY = '#b5ab92'

EXTRA_CSS = ('.lab{font:bold 12px "Courier New",monospace}.needle{transform-box:view-box;animation:nd 5s ease-out infinite}'
             '@keyframes nd{0%{transform:rotate(-55deg)}60%,100%{transform:rotate(0)}}'
             '.slide{animation:sl 5s ease-in-out infinite}@keyframes sl{0%{transform:translateX(-70px)}60%,100%{transform:none}}')
DEFS = COMIC_DEFS + ('<marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
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
    return standalone(vb, body, title, css=prune_css(COMIC_CSS + EXTRA_CSS, body), defs=DEFS if 'ah)' in body else COMIC_DEFS)


# ---------- pieces ----------
def card(x, y, txt, color):
    return (f'<rect x="{x - 29}" y="{y - 11}" width="58" height="22" rx="2" fill="{color}" stroke="{INK}" stroke-width="2"/>'
            + t(x, y + 4, txt, 'lab'))


def desk(x, y, state='old', s=1, label=None):
    """A replica desk with a note card. state: old | new | none."""
    g = (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round">'
         f'<path d="M-18 6v16M18 6v16" fill="none" stroke-width="3"/><rect x="-26" y="-6" width="52" height="13" rx="3" fill="{WOOD}"/>')
    if state != 'none':
        txt = label or ('new' if state == 'new' else 'old')
        g += (f'<rect x="-22" y="-30" width="44" height="22" rx="2" fill="{GREEN if state == "new" else SAND}" stroke-width="2"/>'
              f'<text x="0" y="-15" class="lab" text-anchor="middle" style="stroke:none">{txt}</text>')
    return g + '</g>'


def arrow(d, flow=True, color=RED, w=3.5):
    fl = ' stroke-dasharray="8 7" class="m-flow"' if flow else ''
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"{fl} marker-end="url(#ah)"/>'


def envelope(x, y, rot=0, fill=GREEN):
    return (f'<g transform="translate({x} {y}) rotate({rot})" stroke="{INK}" stroke-width="2" stroke-linejoin="round">'
            f'<rect x="-13" y="-9" width="26" height="18" rx="2" fill="{fill}"/><path d="M-13 -9L0 2L13 -9" fill="none"/></g>')


def stopwatch(x, y, r=26, hand=30):
    a = math.radians(hand - 90)
    return (f'<g stroke="{INK}" stroke-width="3" stroke-linecap="round"><rect x="{x - 7}" y="{y - r - 9}" width="14" height="8" rx="2" fill="{GREY}"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{PAPER}"/><path d="M{x} {y}L{x + (r - 7) * math.cos(a):.1f} {y + (r - 7) * math.sin(a):.1f}" stroke="{RED}"/>'
            f'<circle cx="{x}" cy="{y}" r="3" fill="{INK}"/></g>')


def dial(cx, cy, r, angle, lo='unlikely', hi='likely'):
    a = math.radians(angle - 90)
    nx, ny = cx + (r - 10) * math.cos(a), cy + (r - 10) * math.sin(a)
    return (f'<path d="M{cx - r} {cy}A{r} {r} 0 0 1 {cx + r} {cy}Z" fill="{PAPER}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
            f'<path d="M{cx - r + 9} {cy}A{r - 9} {r - 9} 0 0 1 {cx} {cy - r + 9}" fill="none" stroke="{SAND}" stroke-width="8"/>'
            f'<path d="M{cx} {cy - r + 9}A{r - 9} {r - 9} 0 0 1 {cx + r - 9} {cy}" fill="none" stroke="{GREEN}" stroke-width="8"/>'
            f'<g class="needle" style="transform-origin:{cx}px {cy}px"><path d="M{cx} {cy}L{nx:.1f} {ny:.1f}" stroke="{INK}" stroke-width="4" stroke-linecap="round"/></g>'
            f'<circle cx="{cx}" cy="{cy}" r="6" fill="{INK}"/>'
            + t(cx - r / 2, cy + 18, lo, 'lab') + t(cx + r / 2, cy + 18, hi, 'lab'))


def bg(w, h, color, body):
    return f'<rect width="{w}" height="{h}" fill="{color}"/><rect width="{w}" height="{h}" fill="url(#dots)" opacity=".22"/>{body}'


def axes(x0, y0, x1, y1):
    return f'<path d="M{x0} {y1}V{y0}M{x0} {y1}H{x1}" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'


def curve(d, color=RED, w=4, dash=''):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"{dash}/>'


PANELS = []


def comic(name, title, color, body): PANELS.append((f'comic/{name}.svg', '0 0 320 220', title, bg(320, 220, color, body)))
def story(name, title, color, body): PANELS.append((f'story/{name}.svg', '0 0 440 215', title, bg(440, 215, color, body)))
def icon(name, title, body): PANELS.append((f'facts/{name}.svg', '0 0 160 100', title, bg(160, 100, '#f0e3c6', body)))


def plate(name, title, color, tag, body, caption):
    PANELS.append((f'lead/{name}.svg', '0 0 600 340', title, bg(600, 340, color, body)
                   + f'<rect x="10" y="288" width="580" height="44" fill="{CREAM}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
                   + t(300, 317, caption, 'b') + t(22, 28, tag, 'lab', 'start', f'fill:{RED}')
                   + f'<path d="M8 10Q300 5 592 9Q596 170 591 332Q300 336 9 331Q4 170 8 10Z" fill="none" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>'))


# ================= lead plates =================
conv = (f'<rect x="30" y="238" width="250" height="16" rx="8" fill="#8e8672" stroke="{INK}" stroke-width="3"/>'
        + ''.join(f'<circle cx="{x}" cy="246" r="4" fill="{SAND}" stroke="{INK}" stroke-width="1.5"/>' for x in range(52, 270, 36))
        + f'<path d="M50 262v14M260 262v14" stroke="{INK}" stroke-width="4"/>')
plate('old-note', 'A reader holds up an old note while a fresher note rides a conveyor toward the desk.', '#efe6cc', 'DISTRIBUTED SYSTEMS',
      desk(430, 215, 'none', 2.6) + buddy(430, 130, 'reader', ORANGE, 1.4)
      + f'<g transform="translate(430 52)">{card(0, 0, "old", SAND).replace("width=\"58\"", "width=\"58\"")}</g>'
      + f'<path d="M416 62L404 100M444 62L456 100" stroke="{INK}" stroke-width="3"/>'
      + conv + f'<g class="slide">{card(215, 218, "new", GREEN)}</g>' + arrow('M120 205H310', True)
      + t(440, 275, 'stale: still the old note', 'b', style=f'fill:{RED}') + t(155, 190, 'on its way', 'b'),
      'The fresher note is still travelling.')

ring = ''.join(desk(x, y, 'none', .9 * s) for x, y, s in [(150, 90, 1), (80, 195, 1), (225, 195, 1)])
plate('odds-dial', 'Three desks around a ring and a big dial pointing near the likely end.', '#e8e2cc', 'FROM THE PAPER · MODEL PREDICTION',
      f'<ellipse cx="150" cy="170" rx="100" ry="82" fill="none" stroke="{INK}" stroke-width="3" stroke-dasharray="10 7"/>' + ring
      + dial(440, 230, 125, 52) + t(440, 78, 'chance the read is fresh', 'b-s') + t(150, 270, 'three copies', 'b-s'),
      'Not a promise. An odds estimate.')

# ================= story =================
story('01-fast-or-fresh', 'A reader asks one of three desks and gets a quick but slightly old note.', '#eee5cb',
      desk(190, 140, 'old') + desk(270, 140, 'new') + desk(350, 140, 'new')
      + buddy(60, 130, 'reader', ORANGE) + arrow('M100 125Q140 100 168 120') + stopwatch(240, 52)
      + t(240, 100, 'quick, but a bit old', 'b-s') + t(190, 190, 'asked one desk', 'b-s'))
story('02-odds-not-promises', 'Two dials, versions old and time to wait, each pointing at a likely zone.', '#e8e2cc',
      dial(115, 130, 85, 40) + dial(325, 130, 85, 40) + t(115, 185, 'versions old', 'b') + t(325, 185, 'time to wait', 'b')
      + t(220, 24, 'odds, not promises', 'w'))
story('03-four-delays', 'A write note and a read question race along four paths between a coordinator desk and a replica desk.', '#eee5cb',
      desk(50, 110, 'none', 1.3) + t(50, 160, 'helper', 'b-s') + desk(390, 110, 'none', 1.3) + t(390, 160, 'a desk', 'b-s')
      + arrow('M100 50H336', True) + t(218, 44, 'W: write goes out', 'b-s')
      + arrow('M336 90H100', True, TEAL) + t(218, 84, 'A: ack comes back', 'b-s')
      + arrow('M100 130H336', True) + t(218, 124, 'R: read goes out', 'b-s')
      + arrow('M336 170H100', True, TEAL) + t(218, 164, 'S: answer comes back', 'b-s'))
story('04-three-traces', 'Three curves climb toward the top at different speeds: fast, medium, and slow with a long tail.', '#e8e2cc',
      axes(40, 28, 410, 170) + curve('M42 168Q60 40 130 36H400', RED) + curve('M42 168Q110 120 190 60Q260 38 400 36', TEAL, 4, ' stroke-dasharray="1 0"')
      + curve('M42 168Q250 150 330 90T408 50', '#8a5a9a') + t(145, 24, 'very fast', 'lab', 'start', f'fill:{RED}')
      + t(230, 100, 'medium', 'lab', 'start', f'fill:{TEAL}') + t(280, 138, 'long tail', 'lab', 'start', 'fill:#8a5a9a')
      + t(225, 190, 'wait longer', 'b-s') + t(220, 208, 'From the paper · model prediction · shapes only', 'lab'))

# ================= comic =================
def three(y=150, states=('old', 'old', 'old'), xs=(60, 160, 260), s=1):
    return ''.join(desk(x, y, st, s) for x, st in zip(xs, states))


comic('01a-three-copies', 'Three desks each with the same note pinned.', '#efe6cc',
      three(150) + t(160, 40, 'same note, three copies', 'b') + t(160, 200, 'Pizza at 6', 'lab'))
comic('01b-n-is-three', 'A big 3 floats above three desks inside a bracket.', '#e8e2cc',
      t(160, 70, '3', style=f'fill:{RED};font:900 62px Georgia,serif') + three(165)
      + f'<path d="M30 118V108H290V118" fill="none" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>' + t(160, 205, 'N = 3 copies', 'mono-s'))
comic('01c-new-note', 'A helper holds up a new note and three arrows carry copies to the desks.', '#efe6cc',
      buddy(160, 50, 'helper', PURPLE) + card(160, 15, 'new', GREEN).replace('y="4"', 'y="4"')
      + ''.join(arrow(f'M{160 + (x - 160) * .4:.0f} 88Q{x} 100 {x} 128') for x in (60, 160, 260)) + three(175))
comic('02a-first-yes', 'The nearest desk pins the new note and says got it.', '#e8e2cc',
      desk(70, 150, 'new') + desk(160, 150) + desk(250, 150) + bubble(20, 40, 100, 38, ['got it!'], (70, 108))
      + t(160, 205, 'the closest desk answers first', 'b-s'))
comic('02b-w-is-one', 'The helper gives a thumbs up to the writer, with a 1 on a ticket.', '#efe6cc',
      buddy(100, 140, 'helper', PURPLE) + buddy(230, 140, 'writer', SAND) + bubble(40, 30, 120, 38, ['All done!'], (100, 108))
      + f'<g transform="translate(142 112)" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"><rect x="0" y="6" width="16" height="14" rx="3" fill="{ORANGE}"/><rect x="4" y="-8" width="6" height="16" rx="3" fill="{ORANGE}"/></g>'
      + f'<rect x="200" y="38" width="64" height="34" rx="5" fill="{PAPER}" stroke="{INK}" stroke-width="2.5" stroke-dasharray="5 3"/>' + t(232, 62, 'W = 1', 'mono-s'))
comic('02c-others-late', 'Two desks still hold the old note while two arrows with the new note travel toward them.', '#e8e2cc',
      desk(160, 70, 'new') + desk(60, 170) + desk(260, 170) + arrow('M140 90Q90 105 70 125') + arrow('M180 90Q230 105 250 125')
      + envelope(105, 105, -30) + envelope(215, 105, 30) + t(160, 28, 'still on the way', 'b-s'))
comic('03a-ask-one', 'A reader asks the helper and one arrow goes to a single desk.', '#efe6cc',
      buddy(45, 85, 'reader', ORANGE) + bubble(8, 8, 104, 30, ['Pizza time?'], (45, 58), 'b-s') + buddy(190, 85, 'helper', PURPLE)
      + three(185, ('old', 'new', 'new')) + arrow('M190 118Q180 135 162 150') + t(160, 212, 'R = 1: ask just one desk', 'lab'))
comic('03b-stale-desk', 'A desk with the old note speaks to a puzzled reader.', '#e8e2cc',
      desk(70, 160, 'old', 1.3) + bubble(20, 28, 120, 36, ['Pizza at 6'], (70, 118)) + buddy(240, 150, 'reader', ORANGE)
      + t(240, 98, '?', style=f'fill:{RED};font:900 40px Georgia,serif') + t(160, 205, 'a stale read', 'b-s', style=f'fill:{RED}'))
comic('03c-fresh-desk', 'A desk with the new note speaks to a smiling reader.', '#efe6cc',
      desk(70, 160, 'new', 1.3) + bubble(20, 28, 120, 36, ['Pizza at 7'], (70, 118)) + buddy(240, 150, 'reader', ORANGE)
      + f'<use href="#mstar" x="240" y="104" transform="scale(1.6)" style="transform-origin:240px 104px"/>' + t(160, 205, 'a fresh read', 'b-s', style='fill:#377675'))
comic('04a-overlap', 'Two overlapping circles around desks with one desk inside both.', '#e8e2cc',
      f'<circle cx="115" cy="112" r="72" fill="{ORANGE}" fill-opacity=".35" stroke="{INK}" stroke-width="3"/>'
      f'<circle cx="205" cy="112" r="72" fill="{GREEN}" fill-opacity=".45" stroke="{INK}" stroke-width="3"/>'
      + desk(75, 135) + desk(160, 135, 'new') + desk(245, 135) + t(75, 30, 'R', 'mono', style=f'fill:{RED}') + t(245, 30, 'W', 'mono', style=f'fill:{RED}')
      + t(160, 207, 'R + W &gt; N: they overlap', 'mono-s'))
comic('04b-wait-for-slow', 'A reader waits with a stopwatch while a slow desk walks over.', '#efe6cc',
      buddy(55, 150, 'reader', ORANGE) + stopwatch(55, 70, 24, 120) + desk(130, 170, 'new', .9) + desk(270, 80, 'new', .9)
      + arrow('M240 100Q190 130 100 140', True, TEAL) + t(262, 130, 'slow desk', 'lab') + t(160, 207, 'more desks asked = more waiting', 'b-s'))
sign = lambda x, ttl, rw: (f'<path d="M{x + 65} 160v30" stroke="{INK}" stroke-width="5"/><rect x="{x}" y="28" width="130" height="134" rx="6" fill="{PAPER}" stroke="{INK}" stroke-width="3"/>'
                          + t(x + 65, 52, ttl, 'w-s') + ''.join(desk(x + 25 + i * 40, 108, 'none', .55) for i in range(3))
                          + t(x + 65, 138, rw, 'mono-s') + t(x + 65, 154, 'N = 3', 'lab'))
comic('04c-defaults', 'Two signs: three desks with 1 and 1, and three desks with 2 and 2.', '#e8e2cc',
      sign(20, 'Cassandra', 'R=1  W=1') + sign(170, 'Riak', 'R=2  W=2') + t(160, 212, 'From the paper · default settings', 'lab'))
comic('05a-race', 'Two runners race toward a desk, one with a question and one with a new note.', '#efe6cc',
      buddy(70, 95, 'ask', ORANGE, .85) + buddy(40, 160, 'new', GREEN, .85) + desk(270, 130, 'old', 1.2)
      + ''.join(f'<path d="M{x} {y}h22" stroke="{INK}" stroke-width="2.5" stroke-linecap="round"/>' for x, y in [(110, 85), (110, 100), (84, 150), (84, 166)])
      + t(160, 30, 'RACE!', 'sfx') + t(160, 205, 'which messenger arrives first?', 'b-s'))
comic('05b-spreading', 'The new note passes from desk to desk until every desk has it.', '#e8e2cc',
      ''.join(desk(x, 120, 'new') for x in (45, 125, 205, 285)) + ''.join(arrow(f'M{x + 28} 130H{x + 52}', False) for x in (45, 125, 205))
      + t(160, 50, 'the note keeps spreading', 'b') + t(160, 190, 'soon every desk has it', 'b-s'))
comic('05c-waiting', 'A rising line with a marker near the top labelled almost always fresh.', '#efe6cc',
      axes(40, 40, 290, 180) + curve('M42 176Q90 80 170 62T286 46') + f'<circle cx="255" cy="49" r="7" fill="{GOLD}" stroke="{INK}" stroke-width="2.5"/>'
      + t(160, 30, 'almost always fresh', 'b-s', style=f'fill:{RED}') + t(165, 200, 'wait t →', 'b-s') + t(160, 214, 'Illustration · not to scale', 'lab'))
bars = [60, 40, 55, 30, 48, 36, 150, 44, 200]
comic('06a-measure-trips', 'A ruler measures messenger trip times, with a few very long ones.', '#e8e2cc',
      f'<rect x="30" y="26" width="270" height="18" fill="{SAND}" stroke="{INK}" stroke-width="2.5"/>' + ''.join(f'<path d="M{30 + i * 27} 44v-{8 if i % 2 else 12}" stroke="{INK}" stroke-width="2"/>' for i in range(11))
      + ''.join(f'<rect x="30" y="{56 + i * 16}" width="{w}" height="10" rx="3" fill="{RED if w > 100 else TEAL}" stroke="{INK}" stroke-width="1.5"/>' for i, w in enumerate(bars))
      + t(250, 138, 'a few very long trips', 'lab', 'middle', f'fill:{RED}') + t(160, 212, 'time of each messenger trip', 'b-s'))
cells = ''
for i in range(9):
    cx, cy = 14 + (i % 3) * 100, 20 + (i // 3) * 54
    fresh = i not in (1, 5, 7)
    cells += (f'<rect x="{cx}" y="{cy}" width="90" height="44" rx="5" fill="{PAPER}" stroke="{INK}" stroke-width="2"/><path d="M{cx + 8} {cy + 22}H{cx + 60}" stroke="{INK}" stroke-width="2" stroke-dasharray="4 3"/>'
              f'<circle cx="{cx + 74}" cy="{cy + 22}" r="8" fill="{GREEN if fresh else SAND}" stroke="{INK}" stroke-width="2"/>')
comic('06b-replay', 'Many small race tracks in a grid each with a tally mark for fresh or old.', '#efe6cc',
      cells + t(160, 195, 'green = fresh, sand = old', 'b-s') + t(160, 212, 'Illustration · tallies invented', 'lab'))
comic('06c-check-cassandra', 'A predicted line and a measured line lie almost on top of each other.', '#e8e2cc',
      axes(34, 24, 296, 130) + curve('M36 128Q90 50 160 38T292 26', RED, 4, ' stroke-dasharray="9 6"')
      + ''.join(f'<circle cx="{x}" cy="{y}" r="4.5" fill="{TEAL}" stroke="{INK}" stroke-width="1.5"/>' for x, y in [(70, 84), (110, 58), (150, 43), (200, 35), (250, 30)])
      + f'<path d="M14 160h26" stroke="{RED}" stroke-width="4" stroke-dasharray="9 6"/>' + t(48, 164, 'From the paper · model prediction', 'lab', 'start')
      + f'<circle cx="27" cy="186" r="5" fill="{TEAL}" stroke="{INK}" stroke-width="1.5"/>' + t(48, 190, 'From the paper · measured', 'lab', 'start')
      + t(160, 212, 'Cassandra on three servers', 'b-s'))

# ================= fact icons =================
icon('ssd-vs-disk', 'An SSD chip and a spinning disk side by side.',
     f'<rect x="12" y="26" width="52" height="36" rx="4" fill="{TEAL}" stroke="{INK}" stroke-width="3"/><path d="M20 62v8M30 62v8M40 62v8M50 62v8" stroke="{INK}" stroke-width="3"/>'
     + t(38, 49, 'SSD', 'micro', style='fill:#fff8e3') + f'<circle cx="118" cy="46" r="28" fill="{GREY}" stroke="{INK}" stroke-width="3"/><circle cx="118" cy="46" r="8" fill="{INK}"/>'
     f'<path d="M118 46L138 28" stroke="{RED}" stroke-width="4" stroke-linecap="round"/>' + t(118, 90, 'disk', 'micro'))
icon('first-read', 'A reader with a question mark asks a single desk.',
     desk(110, 70, 'old', .9) + buddy(40, 52, '', ORANGE, .7) + arrow('M66 52H92', False) + t(40, 90, '?', style=f'fill:{RED};font:900 22px Georgia,serif') + t(110, 94, '1st read', 'micro'))
icon('yammer-tail', 'A bar chart that falls quickly and then has a long thin tail.',
     axes(14, 14, 148, 80) + ''.join(f'<rect x="{18 + i * 12}" y="{80 - h}" width="9" height="{h}" fill="{RED}" stroke="{INK}" stroke-width="1.5"/>' for i, h in enumerate([56, 34, 18, 9]))
     + f'<path d="M70 79H140" stroke="{RED}" stroke-width="3" stroke-dasharray="2 5" stroke-linecap="round"/>' + t(80, 96, 'long tail', 'micro'))
icon('cassandra-check', 'A predicted line and measured dots lying on top of each other.',
     axes(14, 12, 148, 72) + curve('M16 70Q50 24 140 18', RED, 3, ' stroke-dasharray="7 5"')
     + ''.join(f'<circle cx="{x}" cy="{y}" r="3.5" fill="{TEAL}" stroke="{INK}" stroke-width="1.5"/>' for x, y in [(40, 46), (70, 29), (100, 22), (130, 18)])
     + t(80, 92, 'match', 'micro'))
icon('latency-win', 'A stopwatch with a down arrow showing latency saved.',
     stopwatch(54, 54, 28, 70) + f'<path d="M110 22v46M96 56l14 14 14-14" fill="none" stroke="{TEAL}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>' + t(116, 92, 'faster', 'micro'))
icon('defaults', 'Three small desks and a gear for default settings.',
     ''.join(desk(32 + i * 48, 56, 'none', .75) for i in range(3))
     + f'<circle cx="80" cy="22" r="10" fill="#edca75" stroke="{INK}" stroke-width="5" stroke-dasharray="3.2 3"/><circle cx="80" cy="22" r="4" fill="{INK}"/>' + t(80, 92, 'defaults', 'micro'))


def srcs(doc):
    found = []

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get('src'), str) and o['src'].startswith('pbs/'):
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
    wanted = {s.replace('pbs/', '', 1) for s, _, _ in need}
    assert not wanted - set(made), f'not drawn: {sorted(wanted - set(made))}'
    for s, w, h in need:
        assert f'viewBox="0 0 {w} {h}"' in made[s.replace('pbs/', '', 1)].read_text(), s
    print(f'wrote {len(made)} files ({len(wanted)} required); extra: {sorted(set(made) - wanted)}')
