"""Draws the media for "The Underlying Technology of Messages" (Facebook Engineering blog, 2010).

Run from the repo root:  python3 tools/draw_facebook_messages_hbase.py
Writes standalone SVGs to backups/media/facebook-messages-hbase/{lead,story,comic,facts}/ (recovery copies only).
Every media.src in data/seed/papers/facebook-messages-hbase.json must be written. Reuses the Cassandra drawing
helpers (desk, ring, folder, face, ...) so the metaphors match: desks on a ring, notes, folders.
"""
import json
from pathlib import Path

import draw_cassandra as C
from draw_cassandra import (GOLD, GREEN, GREY, ORANGE, PAPER, PURPLE, SAND, TEAL, WOOD, CREAM,
                            arrow, desk, envelope, folder, ring_pts, ring)
from media_kit import INK, RED, bubble, buddy, t, write

ROOT = Path(__file__).resolve().parent.parent
SLUG = 'facebook-messages-hbase'
OUT = ROOT / 'backups' / 'media' / SLUG
SEED = ROOT / 'data' / 'seed' / 'papers' / f'{SLUG}.json'
C.PANELS.clear()
OKG = '#3d7a4e'
BLUE = '#82acad'
BRICK = '#c9a27a'
S = f'stroke="{INK}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"'


def box(x, y, w=22, h=16, c=SAND, dust=False):
    g = (f'<rect x="{x:.0f}" y="{y:.0f}" width="{w}" height="{h}" rx="1.5" fill="{c}" {S.replace("2.5", "1.8")}/>'
         f'<path d="M{x + w / 2:.0f} {y:.0f}v{h * .4:.0f}" stroke="{INK}" stroke-width="1.5" opacity=".5"/>')
    if dust:
        g += f'<path d="M{x + 2:.0f} {y + 2:.0f}h{w - 4}" stroke="#fff" stroke-width="2.5" opacity=".55"/>'
    return g


def warehouse(x, y, w, h, cobweb=True, door=True):
    g = (f'<path d="M{x - 8} {y}L{x + w / 2} {y - 34}L{x + w + 8} {y}Z" fill="#a8927a" {S}/>'
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{BRICK}" {S}/>')
    if door:
        g += f'<rect x="{x + w / 2 - 20:.0f}" y="{y + h - 46}" width="40" height="46" fill="#5a4c3a" {S}/>'
    cols = max(2, int((w - 20) // 26))
    for r in range(2):
        for c in range(cols):
            bx = x + 10 + c * 26
            if door and abs(bx + 11 - (x + w / 2)) < 30 and r == 1:
                continue
            g += box(bx, y + 12 + r * 26, 22, 16, [SAND, ORANGE, GREEN][(r + c) % 3], True)
    if cobweb:
        g += (f'<path d="M{x + 2} {y + 2}l30 4M{x + 2} {y + 2}l22 20M{x + 2} {y + 2}l4 30M{x + 14} {y + 4}q4 8 10 16" '
              f'fill="none" stroke="#fff" stroke-width="1.8" opacity=".9"/>')
    return g


def sign(x, y, lines, w=120, fill=PAPER, cls='b-s', rot=0):
    h = 12 + 19 * len(lines)
    g = f'<g transform="rotate({rot} {x + w / 2:.0f} {y + h / 2:.0f})"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" {S}/>'
    for i, ln in enumerate(lines):
        g += t(x + w / 2, y + 22 + 19 * i, ln, cls)
    return g + '</g>'


def person(x, y, hair='#5b3a29', shirt=BLUE, s=1, arms='down'):
    a = {'down': 'M-12 6L-22 24M12 6L22 24', 'up': 'M-12 6L-24 -8M12 6L24 -8', 'out': 'M-12 6L-30 12M12 6L30 12',
         'hold': 'M-12 6L-16 22M12 6L16 22'}[arms]
    return (f'<g transform="translate({x} {y}) scale({s})" {S}><path d="M-6 30v16M6 30v16" fill="none"/><path d="{a}" fill="none"/>'
            f'<rect x="-12" y="-2" width="24" height="34" rx="7" fill="{shirt}"/>{C.face(0, -14, hair)}</g>')


def clipboard(x, y, rot=0, ticks=3):
    g = (f'<g transform="translate({x} {y}) rotate({rot})" {S}><rect x="-16" y="-22" width="32" height="44" rx="3" fill="{WOOD}"/>'
         f'<rect x="-12" y="-17" width="24" height="35" fill="{PAPER}" stroke-width="1.5"/><rect x="-6" y="-25" width="12" height="7" rx="2" fill="{GREY}"/>')
    for i in range(ticks):
        g += f'<path d="M-9 {-9 + i * 11}l3 3 5-6M0 {-6 + i * 11}h8" fill="none" stroke-width="1.6"/>'
    return g + '</g>'


def check(x, y, s=1):
    return f'<path transform="translate({x} {y}) scale({s})" d="M-12 0l8 9 16-20" fill="none" stroke="{OKG}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'


def cross(x, y, s=1, w=7):
    return f'<path transform="translate({x} {y}) scale({s})" d="M-14 -14l28 28M14 -14l-28 28" fill="none" stroke="{RED}" stroke-width="{w}" stroke-linecap="round"/>'


def machine(x, y, label, color=SAND):
    return (f'<rect x="{x - 24}" y="{y - 30}" width="48" height="34" rx="4" fill="{color}" {S}/>'
            f'<rect x="{x - 18}" y="{y - 25}" width="36" height="20" rx="2" fill="{PAPER}" stroke="{INK}" stroke-width="1.5"/>'
            f'<path d="M{x - 12} {y - 18}h16M{x - 12} {y - 12}h24" stroke="{INK}" stroke-width="1.5" opacity=".5"/>'
            + t(x, y + 22, label, 'b-s'))


def shelf_folders(x, y, n, colors=(SAND, GREEN, ORANGE, PURPLE), w=22, h=34, gap=3):
    g = ''
    for i in range(n):
        g += f'<rect x="{x + i * (w + gap)}" y="{y}" width="{w}" height="{h}" rx="2" fill="{colors[i % len(colors)]}" {S.replace("2.5", "1.8")}/>'
    return g


def sweat(x, y):
    return f'<path d="M{x} {y}q-5 8 0 11q5-3 0-11Z" fill="#9fd0d6" stroke="{INK}" stroke-width="1.4"/>'


def sfx(x, y, s, size=22, rot=-6):
    return f'<g transform="rotate({rot} {x} {y})">{t(x, y, s, "sfx-s")}</g>'


def tag(x, y, s):
    return t(x, y, s, 'micro', 'start', f'fill:{RED}')


# =====================================================================  Lead plates
C.plate('two-piles', 'A small busy desk of new letters beside a huge quiet warehouse of dusty old boxes.', '#efe2c0', 'FIG. 1 · ILLUSTRATION',
        desk(150, 195, 3.2, WOOD)
        + ''.join(envelope(110 + i * 24, 108 - (i % 2) * 6, -14 + i * 10, 1.5, [PAPER, '#ffe9a8', '#e6f0d8'][i % 3]) for i in range(4))
        + envelope(78, 60, 25, 1.4) + envelope(214, 52, -20, 1.4) 
        + person(60, 190, '#5b3a29', BLUE, 1.5)
        + t(150, 281, 'small and busy', 'b', 'middle')
        + warehouse(330, 120, 240, 130)
        + t(450, 281, 'huge and quiet', 'b')
        + '<path d="M215 206Q270 215 330 218" fill="none" stroke="#a13324" stroke-width="3" stroke-dasharray="3 9" stroke-linecap="round"/>'
        + sfx(278, 190, 'rarely!', rot=-6),
        'Messages fall into two piles: a busy small one, a big quiet one')

C.plate('the-lineup', 'Three desks labeled MySQL, Cassandra and HBase, with a tester holding a clipboard walking along them.', '#efe2c0', 'FIG. 2 · ILLUSTRATION',
        ''.join(desk(x, 200, 2.2, WOOD) + sign(x - 55, 100, [n], 110, PAPER, 'w')
                for x, n in [(165, 'MySQL'), (340, 'Cassandra'), (505, 'HBase')])
        + f'<g transform="translate(396 160) scale(1.6)"><use href="#mstar"/></g>' + t(396, 124 + 0, '', 'b-s')
        + tag(340, 255, 'OPEN-SOURCED BY THEM').replace('text-anchor="start"', 'text-anchor="middle"')
        + person(50, 180, '#27251e', '#c3b2d8', 1.5, 'hold') + clipboard(85, 205, 8, 3)
        + '<path d="M20 268H580" stroke="#a13324" stroke-width="3" stroke-dasharray="3 9" stroke-linecap="round"/>',
        'Same test, three candidates, one they open-sourced')

# =====================================================================  Story panels
C.story('01-two-piles', 'A busy desk with fresh letters, a big warehouse behind, and a long dotted walk that is rarely taken.', '#f0e3c6',
        desk(95, 130, 2.4) + ''.join(envelope(66 + i * 22, 66 - (i % 2) * 6, -12 + i * 12, 1.2) for i in range(4))
        + person(30, 110, '#5b3a29', BLUE, 1.1)
        + warehouse(250, 66, 170, 100) + t(95, 196, 'busy desk', 'b-s') + t(335, 196, 'big quiet warehouse', 'b-s')
        + '<path d="M140 160Q200 178 250 160" fill="none" stroke="#a13324" stroke-width="3" stroke-dasharray="3 9" stroke-linecap="round"/>'
        + sfx(196, 192, 'rarely', 18, -4))

C.story('02-test-bench', 'A test bench with three machines in a row and a person with a clipboard ticking boxes.', '#f0e3c6',
        f'<rect x="20" y="108" width="300" height="12" rx="3" fill="{WOOD}" {S}/><path d="M40 120v50M300 120v50" {S}/>'
        + machine(70, 100, 'MySQL', SAND) + machine(170, 100, 'Cassandra', ORANGE) + machine(270, 100, 'HBase', GREEN)
        + person(370, 100, '#27251e', PURPLE, 1.3, 'hold') + clipboard(396, 128, 10, 3)
        + sign(30, 14, ['switching is costly'], 170, '#fff4c8') + '<path d="M60 56l-8 12M180 56l8 12" stroke="#27251e" stroke-width="2"/>'
        + sfx(278, 170, 'tick, tick', 18, -4) + t(170, 200, 'a few weeks of testing', 'micro').replace('micro"', 'micro" style="fill:#27251e"'))

C.story('03-choose-hbase', 'Two desks crossed out with red marks and a third desk with a green check and a ribbon reading simpler rules.', '#f0e3c6',
        ''.join(desk(x, 100, 1.9, WOOD) + t(x, 170, n, 'b-s') for x, n in [(70, 'MySQL'), (210, 'Cassandra'), (350, 'HBase')])
        + cross(70, 92, 1.3) + cross(210, 92, 1.3) + check(350, 62, 1.5)
        + f'<path d="M296 184h108l-12 12 12 12H296l12-12z" fill="{RED}" {S}/>'
        + t(350, 202, 'simpler rules', 'b-s', style='fill:#fff8e3')
        + t(70, 195, 'long tail', 'micro', style='fill:#a13324').replace('x="70"', 'x="70"')
        + t(210, 195, 'eventual consistency', 'micro', style='fill:#a13324').replace('font', 'font'))

C.story('04-own-account', 'A company badge stamped on a report page with a short list of reasons, no charts, and a question mark where numbers would go.', '#f0e3c6',
        f'<g transform="rotate(-3 150 110)"><rect x="60" y="14" width="200" height="186" rx="5" fill="{PAPER}" {S}/>'
        + ''.join(f'<circle cx="82" cy="{48 + i * 24}" r="4" fill="{INK}"/><path d="M96 {48 + i * 24}h{[110, 90, 120][i]}" stroke="{INK}" stroke-width="3" stroke-linecap="round" opacity=".45"/>' for i in range(3))
        + f'<rect x="82" y="122" width="150" height="62" rx="4" fill="none" stroke="{INK}" stroke-width="2" stroke-dasharray="6 5"/>'
        + t(157, 168, '?', 'sfx')
        + '</g>' + f'<g transform="rotate(12 300 60)"><circle cx="300" cy="62" r="40" fill="{RED}" opacity=".9" {S}/><circle cx="300" cy="62" r="32" fill="none" stroke="#fff8e3" stroke-width="2"/>'
        + t(300, 58, 'OUR OWN', 'micro', style='fill:#fff8e3') + t(300, 74, 'ACCOUNT', 'micro', style='fill:#fff8e3') + '</g>'
        + sign(290, 138, ['reasons,', 'no benchmarks'], 140, '#fff4c8', 'b-s', 3))

# =====================================================================  Comic panels
C.comic('01a-busy-desk', 'New letters land on a desk while a few are swept away and the worker looks busy.', '#f0e3c6',
        desk(150, 150, 2.5) + ''.join(envelope(100 + i * 36, 58 + (i % 2) * 18, -10 + i * 9, 1.3) for i in range(3))
        + envelope(250, 130, 20, 1.2) + arrow('M262 150l40 10', False, 3)
        + person(60, 110, '#5b3a29', BLUE, 1.3) + sweat(82, 100) + sweat(40, 98)
        + sfx(160, 30, 'busy!', 30) + t(160, 208, 'new letters in, old ones out', 'b-s'))

C.comic('01b-warehouse', 'A big dusty warehouse with rows of boxes and cobwebs, with one tiny visitor in the doorway.', '#f0e3c6',
        warehouse(28, 62, 264, 126) + person(160, 142, '#27251e', PURPLE, .5)
        + sfx(160, 38, 'rarely opened', 22, -3) + t(160, 210, 'only grows', 'b-s'))

C.comic('01c-both-piles', 'A single desk joined to a warehouse by a long hallway with a person holding a checklist.', '#f0e3c6',
        f'<rect x="70" y="118" width="190" height="44" fill="#e4d6b0" {S}/>'
        + desk(44, 120, 1.3) + warehouse(240, 52, 72, 110, False, False)
        + person(160, 100, '#27251e', GREEN, .9, 'hold') + clipboard(176, 124, 6, 3)
        + t(160, 40, 'one system, both piles', 'b') + t(160, 196, 'how to pick a store?', 'b-s'))

C.comic('02a-test-bench', 'Three clusters of little desks labeled MySQL, Cassandra and HBase on a test bench, with a person taking notes.', '#f0e3c6',
        f'<rect x="10" y="130" width="300" height="12" rx="3" fill="{WOOD}" {S}/>'
        + ''.join(t(x, 54, n, 'b-s') + ''.join(desk(x - 20 + (i % 2) * 40, 95 + (i // 2) * 0, .5, c) for i, c in enumerate([SAND, GREEN])) + desk(x, 118, .5, ORANGE)
                  for x, n in [(50, 'MySQL'), (150, 'Cassandra'), (250, 'HBase')])
        + person(230, 140, '#5b3a29', BLUE, .9, 'hold') + clipboard(250, 170, 8, 2) + t(90, 200, 'a few weeks of tests', 'b-s'))

C.comic('02b-sticky-habits', 'Two workers hugging a MySQL desk and a Cassandra desk while a thought bubble shows moving boxes.', '#f0e3c6',
        desk(80, 150, 1.8) + t(80, 206, 'MySQL', 'b-s') + desk(240, 150, 1.8, ORANGE) + t(240, 206, 'Cassandra', 'b-s')
        + person(36, 110, '#5b3a29', BLUE, 1, 'out') + person(284, 110, '#27251e', PURPLE, 1, 'out')
        + bubble(100, 10, 120, 56, [], (160, 80)) + box(122, 28, 24, 18, SAND) + box(156, 28, 24, 18, ORANGE) + arrow('M148 56h56', False, 3)
        + t(190, 44, '?', 'w'))

C.comic('02c-two-roads', 'A fork in the road with one sign that says leave Cassandra and another that says learn a new system.', '#f0e3c6',
        f'<path d="M135 220L150 130Q158 112 120 82M185 220L170 130Q162 112 200 82" fill="none" stroke="{GREY}" stroke-width="22" stroke-linecap="round"/>'
        + f'<path d="M135 220L150 130Q158 112 120 82M185 220L170 130Q162 112 200 82" fill="none" stroke="{INK}" stroke-width="2" stroke-dasharray="8 8" opacity=".5"/>'
        + sign(8, 12, ['leave', 'Cassandra'], 120, '#fff4c8', rot=-3) + sign(192, 12, ['learn a', 'new system'], 120, '#fff4c8', rot=3)
        + person(160, 150, '#5b3a29', BLUE, .7) + sfx(160, 108, 'hmm', 24, 0))

C.comic('03a-small-shelf', 'A tidy small shelf with a few folders and a hand pulling one out quickly.', '#f0e3c6',
        f'<rect x="60" y="96" width="150" height="8" fill="{WOOD}" {S}/>' + shelf_folders(70, 60, 5) + f'<path d="M60 200h150" {S}/>'
        + f'<g transform="translate(262 96)" {S}><circle r="14" fill="#f0c9a0"/><path d="M-10 -22L-14 -40h28L10 -22" fill="#f0c9a0"/></g>'
        + f'<path d="M262 120v70" {S}/><path d="M250 60L214 58" stroke="{RED}" stroke-width="3" stroke-dasharray="3 6" stroke-linecap="round"/>'
        + sfx(130, 36, 'zip!', 28) + t(135, 138, 'any folder, fast', 'b-s'))

C.comic('03b-shelf-grows', 'The shelf grows into a towering wall of folders and a giant index book while a person climbs a ladder, sweating.', '#f0e3c6',
        ''.join(shelf_folders(14, 20 + r * 38, 6, ((SAND, GREEN, ORANGE, PURPLE) if r % 2 else (ORANGE, PURPLE, SAND, GREEN)), 22, 34, 3) for r in range(5))
        + f'<g transform="translate(236 100)" {S}><rect x="-44" y="-30" width="88" height="86" rx="4" fill="{PURPLE}"/><rect x="-36" y="-22" width="72" height="70" fill="{PAPER}" stroke-width="1.5"/>'
        + ''.join(f'<path d="M-28 {-10 + i * 12}h56" stroke-width="1.5" opacity=".5"/>' for i in range(5)) + '</g>' + t(236, 54, 'index', 'w-s')
        + f'<path d="M168 30V200M200 30V200M168 60h32M168 100h32M168 140h32M168 180h32" {S}/>' + person(184, 90, '#5b3a29', BLUE, .55, 'up')
        + sweat(150, 120) + sfx(110, 212, 'slower…', 20, -3))

C.comic('03c-verdict', 'A red cross over the MySQL desk and a very long tail of shrinking boxes with a tiny person at the end looking up.', '#f0e3c6',
        desk(56, 62, 1.5) + cross(56, 56, 1.3) + t(56, 106, 'MySQL', 'b-s')
        + ''.join(box(110 + i * 24, 188 - h, 20, h, [SAND, ORANGE, GREEN][i % 3]) for i, h in enumerate([84, 60, 42, 30, 22, 16, 12, 9]))
        + t(190, 34, 'the long tail', 'b') + person(300, 160, '#27251e', BLUE, .55, 'up') + f'<path d="M104 196H312" {S}/>')

C.comic('04a-different-notes', 'Three desks on a ring each holding a slightly different note about the same message, with a little clock showing catching up.', '#f0e3c6',
        ring(160, 120, 100, 62) + ''.join(desk(x, y, .9) + f'<rect x="{x - 15:.0f}" y="{y - 46:.0f}" width="30" height="22" fill="{c}" {S.replace("2.5", "1.8")}/><path d="M{x - 9:.0f} {y - 38:.0f}h{w}" stroke="{INK}" stroke-width="1.6"/>'
                                      for (x, y), c, w in zip(ring_pts(160, 120, 100, 62, 3, -90), [SAND, GREEN, PURPLE], [18, 12, 15]))
        + f'<circle cx="160" cy="130" r="18" fill="{PAPER}" {S}/><path d="M160 130v-11M160 130l8 4" {S}/>'
        + t(160, 28, 'slightly different notes', 'b-s') + t(160, 208, 'they catch up soon', 'b-s'))

C.comic('04b-reconcile', 'A person with a puzzled face holding two different notes with a question mark.', '#f0e3c6',
        person(160, 90, '#5b3a29', BLUE, 1.5, 'up')
        + f'<g {S}><rect x="82" y="46" width="44" height="54" fill="{SAND}" transform="rotate(-10 104 73)"/><rect x="194" y="46" width="44" height="54" fill="{GREEN}" transform="rotate(10 216 73)"/></g>'
        + '<path d="M92 66h20M92 80h26M204 66h26M204 80h14" stroke="#27251e" stroke-width="2" opacity=".6"/>'
        + t(160, 54, '?', 'sfx') + t(160, 206, 'which note is right?', 'b'))

C.comic('04c-simple-rules', 'One desk with one clean note and a green check while a person nods.', '#f0e3c6',
        desk(190, 140, 2.4) + f'<rect x="168" y="62" width="44" height="34" fill="{SAND}" {S}/><path d="M176 74h28M176 86h18" stroke="{INK}" stroke-width="2" opacity=".5"/>'
        + check(238, 60, 1.6) + person(70, 120, '#27251e', GREEN, 1.4) + sfx(70, 78, 'yes', 22, -6) + t(160, 208, 'one clear answer', 'b'))

C.comic('05a-features', 'A desk with a checklist of ticked boxes: balance, failover, compress, shards.', '#f0e3c6',
        desk(70, 156, 1.6) + f'<rect x="130" y="16" width="170" height="156" rx="6" fill="{PAPER}" {S}/>'
        + ''.join(f'<rect x="144" y="{34 + i * 34}" width="20" height="20" fill="#fff" stroke="{INK}" stroke-width="2"/>'
                  + check(154, 46 + i * 34, .7) + t(176, 51 + i * 34, w, 'b-s', 'start')
                  for i, w in enumerate(['balance', 'failover', 'compress', 'shards'])) + t(160, 204, 'features it needed', 'b-s'))

C.comic('05b-hdfs-folders', 'A basement of folders being copied, stamped with checkmarks and slid around evenly by little arms.', '#e4d9bd',
        f'<rect x="0" y="170" width="320" height="50" fill="#cdbf9b"/>'
        + ''.join(shelf_folders(30, 40 + r * 54, 3, (c,), 26, 36, 8) + shelf_folders(150, 40 + r * 54, 3, (c,), 26, 36, 8) + check(268, 58 + r * 54, .9)
                  for r, c in enumerate([SAND, GREEN, PURPLE]))
        + arrow('M124 60h22', False, 3) + arrow('M124 114h22', False, 3) + arrow('M124 168h22', False, 3)
        + t(80, 24, 'copy', 'b-s') + t(200, 24, 'copy', 'b-s') + t(268, 24, 'checked', 'b-s') + t(160, 210, 'copies, checks, tidy-up', 'b-s'))

C.comic('05c-share-back', 'A team passing a wrapped package back to a crowd of waving helpers.', '#f0e3c6',
        ''.join(person(30 + i * 38, 120, h, c, .8, 'out') for i, (h, c) in enumerate([('#5b3a29', BLUE), ('#27251e', PURPLE)]))
        + f'<g {S}><rect x="116" y="96" width="44" height="34" fill="{SAND}"/><path d="M138 96v34M116 113h44" stroke="{RED}" stroke-width="4"/></g>' + arrow('M166 110h32', False, 3)
        + ''.join(person(220 + (i % 2) * 44, 60 + (i // 2) * 62 + 0, h, c, .6, 'up') for i, (h, c) in enumerate([('#5b3a29', GREEN), ('#27251e', SAND), ('#7a4a3a', PURPLE), ('#b08a2c', BLUE)]))
        + t(160, 208, 'changes sent back', 'b'))

# =====================================================================  Fact icons
def fact(name, title, fig, line, ico, size=22):
    body = (ico + t(80, 49, fig, 'w', style=f'font-size:{size}px') + t(80, 64, line, 'b-s', style='font-size:12px')
            + t(80, 83, 'From the source', 'b-s', style='font-size:12px;font-style:italic;fill:#a13324')
            + t(80, 95, '· reported', 'b-s', style='font-size:12px;font-style:italic;fill:#a13324'))
    C.icon(name, title, body)


fact('messages-per-month', 'The figure 15 billion with a stack of letters.', '15 billion', 'or more messages a month',
     ''.join(envelope(66 + i * 14, 18 - (i % 2) * 2, -8 + i * 8, .7) for i in range(3)))
fact('chat-volume', 'The figure 120 billion with a chat bubble.', '120 billion', 'or more chat messages',
     f'<rect x="64" y="6" width="32" height="20" rx="8" fill="{PAPER}" {S.replace("2.5", "1.8")}/><path d="M74 26l-4 7 12-7" fill="{PAPER}" {S.replace("2.5", "1.8")}/><path d="M71 16h18" stroke="{INK}" stroke-width="2"/>')
fact('cassandra-2008', 'The year 2008 with a desk that has a small gold badge.', '2008', 'Cassandra open-sourced',
     desk(80, 24, .55, WOOD, True).replace('translate(80 24)', 'translate(80 24)'), 26)
fact('test-weeks', 'A few weeks, shown as a calendar page.', 'A few weeks', 'building a test setup',
     f'<g {S.replace("2.5", "1.8")}><rect x="62" y="6" width="36" height="24" rx="3" fill="{PAPER}"/><path d="M62 13h36M72 4v5M88 4v5" /></g>'
     + ''.join(f'<rect x="{67 + c * 9}" y="{17 + r * 7}" width="5" height="4" fill="{INK}" opacity=".5"/>' for r in range(2) for c in range(3)))
fact('new-services', 'The figure 20 with three small desks.', '20', 'or more new services',
     ''.join(desk(52 + i * 28, 20, .4, c) for i, c in enumerate([SAND, GREEN, ORANGE])), 28)


# =====================================================================  Write and verify
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
    wanted = {s.split('/', 1)[1] for s, _, _ in srcs}
    made = {}
    for rel, vb, title, body in C.PANELS:
        made[rel] = write(OUT, rel, C.svg(vb, body, title))
    missing = wanted - set(made)
    assert not missing, f'not drawn: {sorted(missing)}'
    for s, w, h in srcs:
        assert f'viewBox="0 0 {w} {h}"' in made[s.split('/', 1)[1]].read_text(), f'wrong viewBox for {s}'
    print(f'wrote {len(made)} files to {OUT} ({len(wanted)} required); extra: {sorted(set(made) - wanted)}')
