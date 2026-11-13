"""Draws the media for "Apache Hadoop Goes Realtime at Facebook" (Borthakur et al., SIGMOD 2011).

Run from the repo root:  python3 tools/draw_hadoop_realtime_facebook.py
Writes standalone SVGs to backups/media/hadoop-realtime-facebook/{lead,story,comic,facts}/.
Every media.src in data/seed/papers/hadoop-realtime-facebook.json must be written.
Numbers drawn: only those in the JSON (25 -> 3 ms, 40%, 500 million, 10 -> thousands, 20 min). The "3" on the
phone screens is invented and stamped as such.
"""
import json
import math
from pathlib import Path

from media_kit import INK, RED, anim, buddy, standalone, t, write
from draw_cassandra import (CREAM, DEFS, GOLD, GREEN, GREY, ORANGE, PAPER, PURPLE, SAND, TEAL, WOOD, arrow, board,
                            envelope, face, folder, magnifier, notebook, panel_bg, pencil, prune_css)
from media_kit import COMIC_CSS, COMIC_DEFS

ROOT = Path(__file__).resolve().parent.parent
SLUG = 'hadoop-realtime-facebook'
OUT = ROOT / 'backups' / 'media' / SLUG
SEED = ROOT / 'data' / 'seed' / 'papers' / f'{SLUG}.json'
SKY = '#82acad'
PANELS = []
STAMP = 'Illustration · numbers invented'


def svg(vb, body, title):
    return standalone(vb, body, title, css=prune_css(COMIC_CSS, body), defs=DEFS if 'ah)' in body else COMIC_DEFS)


def comic(n, title, bg, body):
    PANELS.append((f'comic/{n}.svg', '0 0 320 220', title, panel_bg(bg, body)))


def story(n, title, bg, body):
    PANELS.append((f'story/{n}.svg', '0 0 440 215', title, panel_bg(bg, body, 440, 215)))


def icon(n, title, body, big, stamp, bg='#f0e3c6'):
    body += t(80, 72, big, 'w', style='font-size:%dpx' % (21 if len(big) < 10 else 16)) + t(80, 93, stamp, 'micro', style='letter-spacing:0;fill:#a13324')
    PANELS.append((f'facts/{n}.svg', '0 0 160 100', title, panel_bg(bg, body, 160, 100)))


def plate(n, title, bg, body, caption):
    PANELS.append((f'lead/{n}.svg', '0 0 600 340', title, panel_bg(bg, body, 600, 340)
                   + f'<rect x="10" y="290" width="580" height="42" fill="{CREAM}" stroke="{INK}" stroke-width="2.5"/>'
                   + t(300, 317, caption, 'b')
                   + f'<path d="M8 10Q300 5 592 9Q596 170 591 332Q300 336 9 331Q4 170 8 10Z" fill="none" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>'))


def sw(w=2.5):
    return f'stroke="{INK}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'


def bell(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})" {sw()}><path d="M-16 8Q-16 -4 -14 -12Q-8 -26 0 -26Q8 -26 14 -12Q16 -4 16 8Z" fill="{GOLD}"/>'
            f'<path d="M-20 8h40" fill="none"/><circle cy="14" r="4" fill="{GOLD}"/></g>')


def badge(x, y, n, r=11):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{RED}" {sw(2)}/>' + t(x, y + 5, n, 'w-s', style='fill:#fff8e3')


def phone(x, y, w=96, h=150, inner=''):
    return (f'<rect x="{x - w / 2:g}" y="{y}" width="{w}" height="{h}" rx="14" fill="{PAPER}" {sw(3)}/>'
            f'<path d="M{x - 12} {y + 8}h24" {sw(3)}/>{inner}')


def rows(x, y, n, w=70, bold=True, gap=26):
    g = ''
    for i in range(n):
        yy = y + i * gap
        g += (f'<circle cx="{x - w / 2 + 8:g}" cy="{yy + 8}" r="7" fill="{[SAND, GREEN, PURPLE][i % 3]}" {sw(1.5)}/>'
              f'<path d="M{x - w / 2 + 22:g} {yy + 8}h{w - 28}" stroke="{INK}" stroke-width="{5 if bold else 2.5}" stroke-linecap="round"/>')
    return g


def rack(x, y, w=44, h=60, units=4):
    g = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{GREY}" {sw(2)}/>'
    for i in range(units):
        yy = y + 5 + i * (h - 8) / units
        g += f'<rect x="{x + 4}" y="{yy:.0f}" width="{w - 8}" height="{(h - 14) / units:.0f}" fill="#8e8672" {sw(1.2)}/><circle cx="{x + w - 9}" cy="{yy + 4:.0f}" r="1.6" fill="{GREEN}"/>'
    return g


def bigbuilding(x, y, w, h, racks=4, label='', ghost=False):
    f = '#d4d0c4' if ghost else '#cfd8d3'
    d = ' stroke-dasharray="6 5"' if ghost else ''
    g = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{f}" {sw(3)}{d}/>'
    if not ghost and racks:
        n = racks
        rw = (w - 16) / n - 6
        for i in range(n):
            g += rack(x + 11 + i * (rw + 6), y + h - 66, rw, 56, 3)
    if label:
        g += f'<rect x="{x + w / 2 - 34:g}" y="{y + 8}" width="68" height="24" rx="4" fill="{PAPER}" {sw(2)}/>' + t(x + w / 2, y + 26, label, 'w-s')
    return g


def machine(x, y, color=ORANGE, w=54, h=44, word=''):
    return (f'<rect x="{x - w / 2:g}" y="{y}" width="{w}" height="{h}" rx="6" fill="{color}" {sw(2.5)}/>'
            f'<circle cx="{x - 10}" cy="{y + 14}" r="2.4" fill="{INK}"/><circle cx="{x + 10}" cy="{y + 14}" r="2.4" fill="{INK}"/>'
            f'<path d="M{x - 5} {y + 21}q5 4 10 0" fill="none" {sw(2)}/>' + (t(x, y + h - 6, word, 'micro', style='letter-spacing:0') if word else ''))


def laptop(x, y):
    return (f'<rect x="{x - 24}" y="{y}" width="48" height="30" rx="3" fill="{PAPER}" {sw()}/><path d="M{x - 32} {y + 34}h64l-6 -4h-52Z" fill="{GREY}" {sw()}/>')


def chat(x, y):
    return f'<path d="M{x - 22} {y}h44a6 6 0 016 6v18a6 6 0 01-6 6h-26l-10 9v-9h-8a6 6 0 01-6-6v-18a6 6 0 016-6Z" fill="{GREEN}" {sw()}/>'


def smile(x, y, happy=True, r=14):
    m = 'M-6 5q6 6 12 0' if happy else 'M-6 8q6 -6 12 0'
    return (f'<g transform="translate({x} {y})" {sw(2)}><circle r="{r}" fill="{GOLD}"/><circle cx="-5" cy="-3" r="1.8" fill="{INK}" stroke="none"/>'
            f'<circle cx="5" cy="-3" r="1.8" fill="{INK}" stroke="none"/><path d="{m}" fill="none"/></g>')


def stamp(x, y, s=STAMP):
    return t(x, y, s, 'micro', style='letter-spacing:0;fill:#a13324')


def person(x, y, hair='#5a4636', s=1):
    return (f'<g transform="translate({x} {y}) scale({s})" {sw()}><path d="M-16 40Q-16 12 0 12Q16 12 16 40Z" fill="{PURPLE}"/>' + face(0, 0, hair, r=13) + '</g>')


def cabinet_small(x, y, w=52, h=60):
    g = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{GREY}" {sw()}/>'
    for i in range(3):
        g += f'<rect x="{x + 6}" y="{y + 6 + i * 18}" width="{w - 12}" height="14" rx="2" fill="#8e8672" {sw(1.5)}/><circle cx="{x + w / 2}" cy="{y + 13 + i * 18}" r="2" fill="{INK}"/>'
    return g


# ------------------------------ lead ------------------------------
def lead1():
    b = f'<path d="M300 100v120" stroke="{INK}" stroke-width="3" stroke-dasharray="6 6"/>'
    b += phone(160, 56, 128, 200, bell(160, 120, 2) + badge(188, 90, 3, 16) + t(160, 232, 'home page', 'w-s'))
    b += phone(440, 56, 128, 200, rows(440, 88, 3, 100, True, 42) + t(440, 232, 'inbox page', 'w-s'))
    b += t(300, 164, '=', 'w', style='font-size:60px') + stamp(300, 276)
    b += t(36, 36, 'ONE ANSWER', 'micro', 'start', 'fill:#a13324')
    plate('two-screens', 'Two phone screens that must show the same three unread messages', SAND, b,
          'Same unread count on both screens')


def lead2():
    b = bigbuilding(250, 70, 310, 190, 6, 'home')
    b += f'<path d="M210 168Q230 150 246 160" fill="none" stroke="{RED}" stroke-width="4" stroke-dasharray="8 7" marker-end="url(#ah)" class="m-flow"/>'
    b += person(92, 150, s=1.5) + phone(140, 168, 40, 70, '').replace('rx="14"', 'rx="6"')
    b += t(92, 270, 'one person', 'w-s') + t(405, 285, '', 'b')
    b += f'<path d="M250 70L405 36L560 70Z" fill="{RED}" {sw(3)}/>'
    plate('one-home', 'One person served from one building full of machine racks, labelled home', '#a2c2a7', b,
          'Each person is served from one data center')


lead1(); lead2()


# ------------------------------ story ------------------------------
def s1():
    b = phone(60, 20, 54, 80, bell(60, 62, .8)) + laptop(60, 120) + chat(60, 166)
    for i, (y, r) in enumerate([(55, -8), (112, 4), (170, 10)]):
        b += f'<g{anim("m-feed", i * .9)}>{envelope(120, y, r)}</g>' + envelope(165 + i * 22, y + (i - 1) * 6, r - 3)
    b += arrow('M215 112H274')
    for i in range(3):
        b += cabinet_small(290 + i * 44, 60 + (i % 2) * 6, 40, 90)
    b += t(350, 186, 'small database machines', 'b-s') + t(150, 205, 'messages never stop', 'b-s')
    story('01-never-stop', 'Envelopes from phones, laptops and chat bubbles pour toward small database cabinets', SAND, b)


def s2():
    b = f'<rect x="40" y="14" width="150" height="190" rx="8" fill="{WOOD}" {sw(3)}/><rect x="52" y="30" width="126" height="164" fill="{PAPER}" {sw(2)}/><rect x="90" y="6" width="50" height="16" rx="4" fill="{GREY}" {sw(2)}/>'
    for i in range(8):
        y = 48 + i * 18
        b += f'<rect x="60" y="{y - 8}" width="10" height="10" fill="none" {sw(1.5)}/><path d="M76 {y - 3}h{[80, 90, 70, 84, 76, 88, 66, 72][i]}" stroke="{INK}" stroke-width="2" opacity=".5"/>'
    for i in (0, 4):
        y = 48 + i * 18
        b += f'<ellipse cx="116" cy="{y - 3}" rx="62" ry="11" fill="none" stroke="{RED}" stroke-width="3" class="m-pulse"/><path d="M61 {y - 3}l3 3 6-7" stroke="{RED}" stroke-width="2.5" fill="none"/>'
    b += arrow('M182 49H228', False) + t(236, 54, 'lots of writes', 'b-s', 'start')
    b += arrow('M182 121H228', False) + t(236, 126, 'agree in one building', 'b-s', 'start')
    b += f'<rect x="240" y="162" width="20" height="20" fill="{PAPER}" {sw(2)}/><path d="M243 165l14 14M257 165l-14 14" stroke="{RED}" stroke-width="3"/>'
    b += t(268, 178, 'not needed', 'b-s', 'start') + t(268, 196, '(split inside a building)', 'micro', 'start', 'letter-spacing:0;font-weight:normal;font-size:12px')
    story('02-needs-list', 'A checklist with two items circled in red and a crossed-out not-needed item', '#f0e3c6', b)


def s3():
    b = f'<rect x="20" y="104" width="400" height="8" fill="{WOOD}" {sw()}/><rect x="20" y="198" width="400" height="8" fill="{WOOD}" {sw()}/>'
    b += notebook(66, 62, .62, 3) + board(120, 20, 96, 64, 3)
    for i in range(3):
        b += folder(300 + i * 30, 86 - i * 0, 56, 36, [SAND, GREEN, PURPLE][i])
    b += t(66, 128, 'notebook', 'micro', style='letter-spacing:0') + t(168, 128, 'whiteboard', 'micro', style='letter-spacing:0') + t(330, 128, 'sorted folders', 'micro', style='letter-spacing:0')
    b += t(60, 24, 'HBase', 'w', 'start', 'font-size:18px;fill:#a13324')
    for k in range(3):
        for i in range(3):
            b += folder(250 + k * 56 + i * 3, 186 - i * 4, 40, 26, [SAND, GREEN, PURPLE][k])
    b += t(110, 170, 'HDFS keeps copies', 'w-s') + t(110, 190, 'of every folder', 'b-s')
    b += f'<path d="M232 118v24" stroke="{RED}" stroke-width="3.5" marker-end="url(#ah)"/>'
    story('03-hbase-on-hdfs', 'A top shelf with notebook, whiteboard and folders; a lower shelf holds copies of each folder', SAND, b)


def s4():
    b = f'<path d="M40 180h360" {sw(3)}/>'
    h25, h3 = 130, 130 * 3 / 25
    b += f'<rect x="100" y="{180 - h25}" width="70" height="{h25}" fill="{ORANGE}" {sw(3)}/><rect x="270" y="{180 - h3:.0f}" width="70" height="{h3:.0f}" fill="{GREEN}" {sw(3)}/>'
    b += t(135, 168 - h25 + 50 - 18, '25', 'w', style='font-size:30px') + t(135, 168 - h25 + 70, 'ms', 'b-s') + t(305, 180 - h3 - 8, '3 ms', 'w')
    b += arrow('M178 80Q220 60 262 150', False) + t(215, 56, 'after the fix', 'b-s')
    b += t(135, 200, 'before', 'b-s') + t(305, 200, 'after', 'b-s') + t(40, 18, 'From the paper · measured', 'micro', 'start', 'fill:#a13324')
    story('04-latency', 'A tall bar marked 25 and a short bar marked 3 with an arrow pointing down between them', '#f0e3c6', b)


s1(); s2(); s3(); s4()


# ------------------------------ comics ------------------------------
comic('01a-two-screens', 'A phone with a bell and badge beside a phone with an inbox list', SAND,
      phone(86, 36, 104, 150, bell(86, 92, 1.6) + badge(110, 64, '3', 13)) + phone(234, 36, 104, 150, rows(234, 66, 3, 80, True, 36))
      + t(86, 206, 'bell', 'b-s') + t(234, 206, 'list', 'b-s') + t(160, 112, '=?', 'w', style='font-size:26px') + stamp(160, 18))
comic('01b-mismatch', 'The bell shows 3 but the list only has two rows, with a frowning face', '#c9d8d6',
      phone(100, 22, 120, 180, bell(100, 62, 1.2) + badge(120, 40, '3', 12) + rows(100, 90, 2, 90, True, 36)) + smile(252, 84, False, 22)
      + t(252, 138, 'huh?', 'sfx-s') + t(100, 214, 'bell 3, list 2', 'b-s') + stamp(160, 14).replace('y="14"', 'y="14"'))
comic('01c-agree', 'Bell and list both show three with a smile between them', GREEN,
      phone(62, 36, 88, 140, bell(62, 80, 1.2) + badge(80, 58, '3', 11)) + phone(258, 36, 88, 140, rows(258, 66, 3, 68, True, 34))
      + smile(160, 100, True, 24) + t(160, 160, 'agree!', 'sfx-s') + t(160, 204, 'same answer everywhere', 'b-s') + stamp(160, 18))
comic('02a-building', 'A big building with rows of tiny machine racks inside', SKY,
      bigbuilding(40, 36, 240, 150, 5, 'data center') + t(160, 208, 'a building full of machines', 'b-s'))
comic('02b-sticky', 'A person with a string tied to one of two buildings', '#f0e3c6',
      person(54, 80, s=1.3) + f'<path d="M74 100Q110 120 140 84" fill="none" stroke="{RED}" stroke-width="3.5" stroke-dasharray="6 5"/>'
      + bigbuilding(130, 40, 80, 70, 2, '', False) + bigbuilding(230, 70, 70, 60, 2, '', True)
      + t(170, 132, 'home', 'w-s') + t(265, 150, 'not mine', 'b-s') + t(160, 206, 'one person, one data center', 'b-s'))
comic('02c-agree-inside', 'Machines nod together inside one building while a far building on a globe is grey', GREEN,
      bigbuilding(14, 40, 170, 120, 0, '') + ''.join(machine(50 + i * 50, 92, ['#f7d79b', ORANGE, PURPLE][i], 40, 40) + f'<g{anim("m-bob", i * .3)}>{t(50 + i * 50, 80, "yes", "micro", style="letter-spacing:0")}</g>' for i in range(3))
      + f'<circle cx="256" cy="110" r="46" fill="{SKY}" {sw()}/><ellipse cx="256" cy="110" rx="20" ry="46" fill="none" {sw(1.5)}/><path d="M210 110h92" {sw(1.5)}/>'
      + bigbuilding(238, 82, 36, 30, 0, '', True) + t(256, 178, 'far away', 'b-s') + t(100, 190, 'agree in the room', 'b-s') + t(160, 18, 'whole world: too hard', 'b-s'))
comic('03a-save-all', 'Envelopes drop into a mailbox that keeps getting taller', '#f0e3c6',
      ''.join(f'<rect x="120" y="{150 - i * 28}" width="80" height="28" rx="3" fill="{[SAND, GREEN, PURPLE, ORANGE][i]}" {sw()}/>' for i in range(4))
      + f'<rect x="110" y="30" width="100" height="14" rx="3" fill="{GREY}" {sw()}/>'
      + envelope(160, 22, -10) + f'<g{anim("m-feed")}>{envelope(80, 70, 10)}</g>' + envelope(250, 60, 14)
      + arrow('M260 160V70', False) + t(160, 196, 'every message is kept', 'b-s') + t(160, 214, 'taller and taller', 'micro', style='letter-spacing:0'))
comic('03b-copies', 'One envelope splits into three copies, each flying to a different person folder', SAND,
      envelope(46, 110, 0, 1.6) + ''.join(arrow(f'M76 {110 + (i - 1) * 12}Q150 {50 + i * 55} 214 {50 + i * 55}', True, 3) + face(236, 50 + i * 55, ['#5a4636', '#a13324', '#27251e'][i], r=12) + folder(280, 52 + i * 55, 50, 32, [SAND, GREEN, PURPLE][i]) for i in range(3))
      + t(60, 160, 'one message', 'b-s') + t(160, 14, '', 'b'))
comic('03c-keep-up', 'A slow cabinet with a snail shell on the left and a fast runner with a notebook on the right', '#c9d8d6',
      f'<ellipse cx="78" cy="168" rx="46" ry="8" fill="#27251e" opacity=".15"/>' + cabinet_small(52, 70, 52, 94)
      + f'<circle cx="50" cy="150" r="22" fill="{ORANGE}" {sw()}/><path d="M50 150a12 12 0 1112 12" fill="none" {sw(2)}/>'
      + t(78, 196, 'slow', 'w-s') + buddy(238, 100, 'new', GREEN, 1.2, 'm-hop') + notebook(280, 94, .42)
      + '<path d="M180 80h-30M184 100h-40M180 120h-30" ' + f'stroke="{INK}" stroke-width="3" stroke-linecap="round"/>' + t(238, 196, 'keeps up', 'w-s'))
comic('04a-notebook', 'A pencil writes a new line at the bottom of a notebook', '#f0e3c6',
      notebook(150, 100, 2, 5) + f'<path d="M116 148h48" stroke="{RED}" stroke-width="4" stroke-linecap="round" class="m-meter"/>' + pencil(150, 160, -35, 'm-bob')
      + t(250, 80, 'notebook', 'w-s') + t(250, 100, 'written first', 'b-s') + t(250, 124, 'a crash', 'b-s') + t(250, 144, 'cannot lose it', 'b-s'))
comic('04b-whiteboard-folder', 'A full whiteboard sends a stack of cards into a new folder', SAND,
      board(20, 36, 130, 96, 6) + t(85, 160, 'board is full', 'b-s') + arrow('M158 84H214')
      + ''.join(f'<rect x="{166 + i * 4}" y="{66 + i * 5}" width="30" height="18" fill="{[SAND, GREEN, PURPLE][i]}" {sw(1.6)}/>' for i in range(3))
      + folder(262, 92, 80, 54, GREEN) + t(262, 140, 'sorted folder', 'b-s') + t(262, 168, '', 'b'))
comic('04c-zip-doorman', 'Several folders squeeze into one larger folder and a doorman guards a folder door', '#c9d8d6',
      ''.join(folder(40 + i * 8, 40 + i * 18, 50, 32, [SAND, GREEN, PURPLE][i]) for i in range(3)) + arrow('M92 80H146', False)
      + folder(194, 80, 90, 60, ORANGE) + t(190, 28, 'zip folders together', 'b-s')
      + f'<rect x="224" y="144" width="60" height="62" rx="4" fill="{WOOD}" {sw()}/><circle cx="270" cy="178" r="3" fill="{INK}"/>'
      + buddy(190, 176, 'door', SAND, .7) + f'<path d="M170 150h40l-4 -8h-32Z" fill="{RED}" {sw(2)}/>'
      + f'<rect x="96" y="112" width="90" height="28" rx="12" fill="{PAPER}" {sw(2)}/><path d="M150 140l22 22" fill="none" {sw(2)}/>' + t(141, 132, '“not here”', 'b-s'))
comic('05a-pipeline', 'A block passes along a line of three machines', '#f0e3c6',
      ''.join(machine(50 + i * 110, 90, [SAND, ORANGE, PURPLE][i], 60, 52) for i in range(3)) + arrow('M82 112H128', False) + arrow('M192 112H238', False)
      + f'<g{anim("m-ride")}><rect x="40" y="52" width="20" height="20" fill="{GOLD}" {sw()}/></g>'
      + t(160, 36, 'a block goes down the line', 'b-s') + t(160, 190, 'one write, every copy', 'b-s'))
comic('05b-all-ack', 'Three machines raise thumbs-up flags and a fourth with a red cross is skipped', GREEN,
      ''.join(machine(44 + i * 68, 100, [SAND, ORANGE, PURPLE][i], 50, 46) + f'<path d="M{44 + i * 68} 100v-26" {sw()}/><path d="M{44 + i * 68} 74h22l-5 8 5 8h-22Z" fill="{PAPER}" {sw(2)}/><path d="M{50 + i * 68} 81l3 4 6-6" fill="none" stroke="{TEAL}" stroke-width="2.5"/>' for i in range(3))
      + machine(266, 100, '#d4d0c4', 50, 46) + f'<path d="M244 94l44 52M288 94l-44 52" stroke="{RED}" stroke-width="5" stroke-linecap="round"/>'
      + t(110, 40, 'wait for every “got it”', 'b-s') + t(250, 170, 'fails: new', 'b-s') + t(250, 188, 'notebook', 'b-s') + t(160, 204, 'skip the broken one', 'micro', style='letter-spacing:0'))
comic('05c-checksum', 'A magnifying glass checks a block while a torn block goes in a bin and two good blocks stay', SAND,
      magnifier(86, 80, 1.3) + f'<rect x="64" y="64" width="40" height="32" fill="{GOLD}" {sw()}/><path d="M72 76h24M72 86h14" stroke="{INK}" stroke-width="2"/>'
      + f'<path d="M170 140l22 -22 12 12 22 -18 14 14" fill="none" stroke="{RED}" stroke-width="3" stroke-dasharray="5 4"/>'
      + f'<path d="M220 124l12 10 14 -6 10 18h-50Z" fill="{PAPER}" {sw(2)}/><path d="M236 170h50l-6 30h-38Z" fill="{GREY}" {sw()}/><path d="M232 170h58" {sw(4)}/>'
      + ''.join(f'<rect x="{150 + i * 36}" y="52" width="28" height="24" fill="{GREEN}" {sw()}/><path d="M{156 + i * 36} 64l5 5 9-10" fill="none" stroke="{TEAL}" stroke-width="3"/>' for i in range(2))
      + t(160, 26, 'check each block', 'b-s') + t(80, 196, 'good: keep', 'b-s') + t(262, 212, 'bad: bin', 'b-s'))
comic('06a-boss', 'One desk labelled boss holds a big map with arrows to many machines', '#c9d8d6',
      f'<rect x="100" y="30" width="120" height="44" rx="4" fill="{WOOD}" {sw()}/><rect x="124" y="14" width="72" height="40" fill="{PAPER}" {sw(2)}/><path d="M134 28q12 -8 24 4t26 -6M134 42h40" fill="none" stroke="{TEAL}" stroke-width="3"/>'
      + t(160, 68, 'boss', 'w-s') + ''.join(arrow(f'M{160 + (i - 2) * 24} 76L{40 + i * 60} 134', False, 2.5) + machine(40 + i * 60, 136, [SAND, ORANGE, PURPLE, GREEN, SAND][i], 40, 36) for i in range(5))
      + t(160, 202, 'one boss knows where every block is', 'b-s'))
comic('06b-standby', 'Two bosses at two desks and the second reads along over the first', SAND,
      f'<rect x="20" y="110" width="110" height="36" rx="4" fill="{WOOD}" {sw()}/><rect x="190" y="110" width="110" height="36" rx="4" fill="{WOOD}" {sw()}/>'
      + buddy(75, 80, 'boss', ORANGE, .9) + buddy(245, 80, 'standby', GREEN, .9, label_cls='w-s') + f'<rect x="52" y="100" width="46" height="12" fill="{PAPER}" {sw(2)}/>'
      + f'<path d="M136 96Q160 70 190 92" fill="none" stroke="{RED}" stroke-width="3" stroke-dasharray="6 5" class="m-flow"/>' + t(160, 60, 'same diary', 'b-s')
      + t(75, 176, 'writes the diary', 'b-s') + t(245, 176, 'reads along', 'b-s'))
comic('06c-signpost', 'A signpost swings its arrow from one desk to the other while a stopwatch ticks', '#f0e3c6',
      f'<path d="M160 60V190" stroke="{INK}" stroke-width="7" stroke-linecap="round"/><g{anim("m-wobble")}><path d="M160 52h58l16 14 -16 14h-58Z" fill="{GOLD}" {sw()}/></g>'
      + f'<rect x="14" y="140" width="76" height="30" rx="4" fill="#d4d0c4" {sw()} stroke-dasharray="6 4"/><rect x="236" y="140" width="76" height="30" rx="4" fill="{WOOD}" {sw()}/>'
      + t(52, 192, 'old boss', 'b-s') + t(274, 192, 'new boss', 'b-s') + f'<circle cx="62" cy="68" r="22" fill="{PAPER}" {sw()}/><path d="M62 68V54M62 68l10 6M56 44h12" fill="none" {sw()}/>'
      + t(62, 108, 'quick', 'b-s'))

# ------------------------------ facts ------------------------------
M, S = 'paper · measured', 'paper · stated'
icon('people', 'A crowd of people icons', ''.join(face(30 + (i % 4) * 33, 20 + (i // 4) * 24, ['#5a4636', '#a13324', '#27251e', '#b08a2c'][i % 4], r=9) for i in range(8)), '500 million', S)
icon('needs', 'A short checklist with two items ticked', ''.join(f'<rect x="40" y="{6 + i * 15}" width="9" height="9" fill="{PAPER}" {sw(1.5)}/><path d="M56 {11 + i * 15}h{[60, 50, 56][i]}" stroke="{INK}" stroke-width="2" opacity=".5"/>' for i in range(3))
     + f'<path d="M41 12l3 3 5-6M41 42l3 3 5-6" fill="none" stroke="{RED}" stroke-width="2.5"/>', '8 needs', S)
icon('put-latency', 'A tall bar and a short bar', f'<rect x="40" y="6" width="28" height="44" fill="{ORANGE}" {sw(2)}/><rect x="96" y="43" width="28" height="7" fill="{GREEN}" {sw(2)}/><path d="M72 20Q88 22 98 40" fill="none" stroke="{RED}" stroke-width="3" marker-end="url(#ah)"/>', '25 → 3 ms', M)
icon('network-io', 'Network arrows shrinking', f'<path d="M24 22h80M24 38h40" stroke="{INK}" stroke-width="6" stroke-linecap="round"/><path d="M110 18v28" stroke="{RED}" stroke-width="3.5" marker-end="url(#ah)"/>', '40%', M)
icon('cluster-growth', 'One machine growing into many', machine(34, 20, SAND, 28, 26) + arrow('M52 33H72', False) + ''.join(f'<rect x="{80 + (i % 4) * 16}" y="{10 + (i // 4) * 14}" width="12" height="10" fill="{GREY}" {sw(1.5)}/>' for i in range(12)), '10 → thousands', M)
icon('failover', 'A stopwatch', f'<circle cx="80" cy="28" r="22" fill="{PAPER}" {sw()}/><path d="M80 28V14M80 28l11 7M74 3h12" fill="none" {sw()}/>', '20 min', S)


# ------------------------------ write ------------------------------
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
    wanted = {s.split('/', 1)[1] for s, _, _ in need}
    made = {rel: write(OUT, rel, svg(vb, body, title)) for rel, vb, title, body in PANELS}
    assert not wanted - set(made), f'not drawn: {sorted(wanted - set(made))}'
    for s, w, h in need:
        assert f'viewBox="0 0 {w} {h}"' in made[s.split('/', 1)[1]].read_text()
    print(f'wrote {len(made)} files ({len(wanted)} required); extra: {sorted(set(made) - wanted)}')
