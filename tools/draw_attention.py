"""Draws the comic panels and fact icons for "Attention Is All You Need".

Run from the repo root:  python3 tools/draw_attention.py
Writes standalone SVG files to public/media/1706.03762/{comic,facts}/.
Words, captions and which file goes where live in public/data/papers/1706.03762.json.
"""
import math
from pathlib import Path

from media_kit import (COL, EIGHT, INK, RED, anim, bubble, buddy, can, gear, mini_bat, panel, stick_bat,
                       standalone, t, write)

OUT = Path(__file__).resolve().parent.parent / 'public' / 'media' / '1706.03762'
PANELS = []   # (file name, title, body)


def add(name, title, bg, body):
    PANELS.append((f'comic/{name}.svg', title, panel(bg, body)))


# ---------- strip 1: number codes ----------

add('01a-letters', 'A confused computer looks at the word bat and shows question marks.', '#efd5b7',
    f'<rect x="170" y="34" width="124" height="90" rx="7" fill="#d8cfb8" stroke="{INK}" stroke-width="3"/>'
    f'<rect x="181" y="45" width="102" height="62" fill="#3d4a45" stroke="{INK}" stroke-width="2"/>'
    + t(232, 72, 'b · a · t', 'mono', style='fill:#a2c2a7')
    + f'<g{anim("m-blink")}>' + t(232, 98, '? ? ?', 'mono', style='fill:#f8d065') + '</g>'
    + f'<path d="M222 124h20v14h-20zM202 138h60v8h-60z" fill="#b5ab92" stroke="{INK}" stroke-width="2"/>'
    + buddy(78, 120, 'bat', COL['bat'])
    + f'<g{anim("m-bob")}>' + t(112, 70, '?', 'sfx') + '</g>'
    + bubble(150, 162, 158, 44, ['Letters? Huh?'], (232, 148)))

squares = ''.join(
    f'<g{anim("m-loop-pop", round(.9 + i * .3, 1))}><rect x="{214 + i * 20}" y="88" width="18" height="22" fill="{c}" stroke="{INK}" stroke-width="1.5"/>'
    + t(223 + i * 20, 104, d, 'mono-s') + '</g>'
    for i, (d, c) in enumerate(zip('38164', ['#d9824f', '#efae78', '#c86f3f', '#f3c39a', '#e89a66'])))
add('01b-code-machine', 'The word bat goes into a machine with spinning gears and comes out as a row of number squares.', '#f0e3c6',
    f'<path d="M118 62L134 38H186L202 62Z" fill="#dc9665" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
    f'<rect x="108" y="62" width="104" height="82" rx="5" fill="#719f9d" stroke="{INK}" stroke-width="3"/>'
    + gear(160, 102, 17) + gear(188, 80, 8, .2)
    + f'<path d="M108 100h-8M212 100h6" stroke="{INK}" stroke-width="3"/>'
    + f'<g{anim("m-feed")}><rect x="24" y="86" width="60" height="30" rx="5" fill="{COL["bat"]}" stroke="{INK}" stroke-width="2"/>'
    + t(54, 107, 'bat', 'w') + '</g>'
    + squares + t(262, 130, '…AND MORE', 'micro')
    + t(160, 176, 'CODE MACHINE', 'micro') + t(160, 204, 'whirr… clunk!', 'sfx-s'))

chairs = ''
for i, (w, x) in enumerate([('The', 60), ('bat', 160), ('flew', 260)]):
    chairs += (f'<path d="M{x - 30} 150v40M{x + 30} 150v40" stroke="#6b4f36" stroke-width="5" stroke-linecap="round"/>'
               f'<rect x="{x - 36}" y="144" width="72" height="11" rx="3" fill="#a27c55" stroke="{INK}" stroke-width="2"/>'
               f'<circle cx="{x}" cy="181" r="14" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>' + t(x, 187, str(i + 1), 'w'))
    chairs += buddy(x, 116, w, COL[w], .82, 'm-hop', round(i * .35, 2))
add('01c-seats', 'The, bat and flew hop onto chairs numbered 1, 2 and 3.', '#b8cec0',
    chairs + bubble(70, 12, 180, 40, ['Seats keep us in order!'], (160, 86)))

# ---------- strip 2: ask around ----------

add('02a-puzzle', 'Bat wonders whether it is a flying animal or a baseball bat.', '#82acad',
    buddy(80, 150, 'bat', COL['bat'])
    + f'<g{anim("m-bob")}>' + t(106, 104, '?', 'sfx') + '</g>'
    + f'<circle cx="128" cy="138" r="5" fill="#fff8e3" stroke="{INK}" stroke-width="2"/><circle cx="142" cy="124" r="8" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>'
    + f'<ellipse cx="216" cy="76" rx="94" ry="56" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>'
    + f'<g{anim("m-alt-a")}>' + mini_bat(162, 74, 1) + t(162, 112, 'animal?', 'b-s') + '</g>'
    + t(214, 82, 'or', 'b')
    + f'<g{anim("m-alt-b")}>' + stick_bat(262, 70, .9) + t(262, 112, 'stick?', 'b-s') + '</g>')

add('02b-question', 'Bat holds a question card. The holds a tag saying helper word; flew holds a tag saying about flying.', '#b8cec0',
    t(60, 54, 'NAME TAG', 'micro') + t(260, 54, 'NAME TAG', 'micro') + t(160, 30, 'QUESTION', 'micro', style=f'fill:{RED}')
    + f'<path d="M60 96v44M260 96v44M160 92v40" stroke="{INK}" stroke-width="3"/>'
    + f'<g{anim("m-swing")}><rect x="12" y="62" width="96" height="34" rx="4" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>' + t(60, 84, 'helper word', 'b-s') + '</g>'
    + f'<g{anim("m-swing", .6)}><rect x="212" y="62" width="96" height="34" rx="4" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>' + t(260, 84, 'about flying', 'b-s') + '</g>'
    + f'<g{anim("m-wiggle")}><rect x="128" y="38" width="64" height="54" rx="6" fill="#fff8e3" stroke="{RED}" stroke-width="3"/>' + t(160, 77, '?', 'sfx') + '</g>'
    + buddy(60, 162, 'The', COL['The'], .85) + buddy(160, 162, 'bat', COL['bat'], .85) + buddy(260, 162, 'flew', COL['flew'], .85))

rows = ''
for i, (w, share, fill) in enumerate([('The', 10, '#cfa64b'), ('bat', 20, '#c86f3f'), ('flew', 70, '#377675')]):
    y = 52 + i * 46
    rows += (t(18, y + 16, w, 'w', 'start')
             + f'<rect x="76" y="{y}" width="170" height="22" fill="#ddcfb0" stroke="{INK}" stroke-width="2"/>'
             + f'<rect class="m-meter" x="76" y="{y}" width="{170 * share / 100:g}" height="22" fill="{fill}" style="animation-delay:{i * .25}s"/>'
             + t(302, y + 18, f'{share}%', 'w', 'end'))
add('02c-match-meter', 'A match meter: The 10 percent, bat 20 percent, flew 70 percent.', '#f0e3c6',
    t(160, 30, 'MATCH-O-METER', 'micro') + rows
    + f'<g{anim("m-pulse")}>' + t(160, 204, '“flew” matches best!', 'sfx-s') + '</g>')

# ---------- strip 3: blend it in ----------

body = ''
for i, (w, x, c) in enumerate([('The', 60, '#e9c46a'), ('bat', 160, '#d9824f'), ('flew', 260, '#5d8c75')]):
    body += buddy(x, 92, w, COL[w], .82) + can(x, 162, c, 0, 'm-wobble', round(i * .4, 1))
add('03a-paint', 'The, bat and flew each hold a paint can: yellow, orange and green.', '#f0e3c6',
    body + t(160, 210, 'EACH WORD’S OWN PAINT', 'micro'))

add('03b-pour', 'Three paint cans pour into a bucket labelled bat: a thick green stream from flew, thinner ones from bat and The.', '#c2d4cf',
    '<path d="M78 56Q120 70 146 150" class="m-flow" fill="none" stroke="#e9c46a" stroke-width="3"/>'
    '<path d="M160 64V150" class="m-flow" fill="none" stroke="#d9824f" stroke-width="7"/>'
    '<path d="M242 56Q200 70 174 150" class="m-flow" fill="none" stroke="#5d8c75" stroke-width="15"/>'
    + can(62, 52, '#e9c46a', 62) + can(160, 44, '#d9824f', 180) + can(258, 52, '#5d8c75', -62)
    + t(60, 126, '10%', 'w') + t(150, 104, '20%', 'w', 'end') + t(250, 120, '70%', 'w')
    + '<clipPath id="m-bucket"><path d="M120 142H200L192 200H128Z"/></clipPath>'
    + '<g clip-path="url(#m-bucket)"><rect class="m-fill" x="118" y="150" width="84" height="52" fill="#7c9f80"/></g>'
    + f'<path d="M120 142H200L192 200H128Z" fill="none" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
    + t(160, 182, 'bat', 'w', style='fill:#fff8e3'))

wings = (f'<g transform="translate(-100 30)"><g{anim("m-flap")} fill="#343444" stroke="#26251f" stroke-width="2" stroke-linejoin="round">'
         '<path d="M228 90Q208 66 182 68Q191 81 187 94Q200 88 205 103Q214 95 228 104Z"/>'
         '<path d="M292 90Q312 66 338 68Q329 81 333 94Q320 88 315 103Q306 95 292 104Z"/></g></g>')
stars = ''.join(f'<g{anim("m-twinkle", d)}><use href="#mstar" x="{x}" y="{y}"/></g>' for x, y, d in [(40, 160, 0), (282, 150, .7), (300, 70, 1.4), (24, 96, 2)])
add('03c-wings', 'Bat, now tinted green, grows flapping wings and says it is the one with wings.', '#82acad',
    stars + wings + buddy(160, 126, 'bat', '#b5b98f') + bubble(56, 12, 208, 44, ['I’m the one with wings!'], (176, 96)))

# ---------- strip 4: many lookers ----------

add('04a-one-looker', 'A single looker scans the sentence with a magnifying glass.', '#efd5b7',
    f'<rect x="150" y="112" width="156" height="48" rx="5" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>'
    + t(228, 143, 'The bat flew', 'w')
    + f'<g{anim("m-scan")}><circle cx="186" cy="136" r="17" fill="#ffffff" fill-opacity=".35" stroke="{INK}" stroke-width="4"/>'
    f'<path d="M198 148l14 14" stroke="{INK}" stroke-width="6" stroke-linecap="round"/></g>'
    + buddy(70, 150, 'looker', COL['looker'], .9, label_cls='w-s')
    + bubble(16, 14, 210, 58, ['I can only watch one', 'clue at a time…'], (78, 120)))

targets = [2, 0, 1, 2, 0, 1, 2, 1]
wx = [70, 160, 250]
body = ''
for i, (tg, c) in enumerate(zip(targets, EIGHT)):
    x = 24 + i * 39
    body += f'<path class="m-dash" d="M{x} 62Q{x} 120 {wx[tg]} 168" fill="none" stroke="{c}" stroke-width="2.5" style="animation-delay:{i * .15:g}s"/>'
for i, c in enumerate(EIGHT):
    x = 24 + i * 39
    body += buddy(x, 44, '', COL['looker'], .42) + t(x, 16, str(i + 1), 'micro', style=f'fill:{c}')
body += ''.join(t(x, 196, w, 'w') for x, w in zip(wx, ['The', 'bat', 'flew']))
add('04b-eight-lookers', 'Eight small lookers each draw a dotted line to a different word in The bat flew.', '#f0e3c6', body)

notes = ''
for i, c in enumerate(EIGHT):
    a = math.radians(i * 45 - 90)
    x, y = 160 + 124 * math.cos(a), 112 + 80 * math.sin(a)
    notes += (f'<g class="m-gather" style="--dx:{(160 - x) * .55:.0f}px;--dy:{(112 - y) * .55:.0f}px;animation-delay:{i * .12:.2f}s">'
              f'<rect x="{x - 15:.0f}" y="{y - 12:.0f}" width="30" height="24" fill="{c}" stroke="{INK}" stroke-width="1.5" opacity=".9"/>'
              f'<path d="M{x - 9:.0f} {y - 3:.0f}h18M{x - 9:.0f} {y + 4:.0f}h12" stroke="#fff8e3" stroke-width="2"/></g>')
add('04c-glue', 'Eight colored sticky notes fly into one big note labelled all the clues.', '#c9d3c0',
    notes + f'<rect x="112" y="80" width="96" height="64" rx="3" fill="#fff8e3" stroke="{INK}" stroke-width="2.5"/>'
    + t(160, 106, 'all the', 'b-s') + t(160, 126, 'clues', 'w')
    + f'<g{anim("m-pulse")}>' + t(268, 212, 'GLUE!', 'sfx-s') + '</g>')

# ---------- strip 5: six floors ----------

add('05a-listen', 'The, bat and flew are linked by dotted listening lines.', '#b8cec0',
    f'<path class="m-dash" d="M70 120Q110 70 150 120" fill="none" stroke="{RED}" stroke-width="3"/>'
    '<path class="m-dash" d="M170 120Q210 70 250 120" fill="none" stroke="#377675" stroke-width="3" style="animation-delay:.4s"/>'
    '<path class="m-dash" d="M60 116Q160 10 260 116" fill="none" stroke="#5d6aa1" stroke-width="3" style="animation-delay:.8s"/>'
    + buddy(60, 156, 'The', COL['The'], .85) + buddy(160, 156, 'bat', COL['bat'], .85) + buddy(260, 156, 'flew', COL['flew'], .85)
    + t(14, 32, 'LISTEN', 'sfx', 'start'))

body = t(14, 32, 'THINK', 'sfx', 'start')
for i, (w, x) in enumerate([('The', 60), ('bat', 160), ('flew', 260)]):
    body += (f'<ellipse cx="{x}" cy="78" rx="38" ry="26" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>'
             f'<circle cx="{x - 4}" cy="112" r="4" fill="#fff8e3" stroke="{INK}" stroke-width="1.5"/>'
             + gear(x, 78, 12, i * .3) + buddy(x, 156, w, COL[w], .85))
add('05b-think', 'Each word has its own thought bubble with a spinning gear.', '#f0e3c6', body)

body = f'<path d="M84 200H236" stroke="{INK}" stroke-width="3"/><path d="M96 26H224" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
for k in range(1, 7):
    y = 200 - k * 28
    body += (f'<rect x="104" y="{y}" width="112" height="28" fill="{"#f6ead0" if k % 2 else "#ead9b6"}" stroke="{INK}" stroke-width="2"/>'
             + t(112, y + 18, f'FLOOR {k}', 'micro', 'start'))
body += (f'<g class="m-ride"><rect x="106" y="31" width="108" height="24" rx="3" fill="none" stroke="{RED}" stroke-width="3"/>'
         + ''.join(f'<rect x="{222 + j * 12}" y="38" width="10" height="10" fill="{c}" stroke="{INK}" stroke-width="1.5"/>' for j, c in enumerate([COL['The'], COL['bat'], COL['flew']]))
         + '</g>' + t(40, 70, 'listen', 'b-s') + t(40, 90, '+ think', 'b-s') + t(40, 110, 'on every', 'b-s') + t(40, 130, 'floor', 'b-s')
         + f'<g{anim("m-twinkle")}><use href="#mstar" x="280" y="40"/></g>' + t(280, 70, 'smarter!', 'b-s'))
add('05c-six-floors', 'The three words ride an elevator up a six-floor building.', '#e6d3b0', body)

# ---------- strip 6: no peeking ----------

add('06a-read', 'The writer looks at a page that says The bat flew.', '#c9d3c0',
    f'<rect x="20" y="34" width="150" height="86" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>'
    + t(95, 58, 'ENGLISH', 'micro') + t(95, 90, 'The bat flew.', 'w')
    + f'<path class="m-dash" d="M214 114L170 86M214 114L170 104" fill="none" stroke="{RED}" stroke-width="2.5"/>'
    + buddy(244, 128, 'writer', COL['writer'], 1, label_cls='w-s')
    + bubble(16, 150, 196, 52, ['I can read all', 'of the English!'], (212, 140)))

add('06b-no-peeking', 'The writer has written Die; a cover marked no peeking hides the rest.', '#efd5b7',
    f'<rect x="110" y="66" width="196" height="54" fill="#fcf0cb" stroke="{INK}" stroke-width="2"/>'
    + t(142, 100, 'Die', 'w')
    + f'<g{anim("m-shake")}><rect x="172" y="60" width="140" height="66" fill="#6e6253" stroke="{INK}" stroke-width="2"/>'
    '<rect x="172" y="60" width="140" height="66" fill="url(#m-hatch)"/>'
    '<rect x="190" y="82" width="104" height="22" fill="#6e6253"/>' + t(242, 98, 'NO PEEKING', 'micro', style='fill:#f6f0df') + '</g>'
    + f'<path d="M96 156l18-38" stroke="{RED}" stroke-width="4" stroke-linecap="round"/>'
    + buddy(64, 160, 'writer', COL['writer'], 1, label_cls='w-s')
    + f'<g{anim("m-bob")}>' + t(242, 46, '?', 'sfx') + '</g>'
    + bubble(132, 152, 176, 44, ['What comes next?'], (100, 168)))

add('06c-ta-da', 'The cover slides away one word at a time, revealing Die Fledermaus flog.', '#b8cec0',
    t(160, 34, 'The bat flew.', 'w') + t(160, 56, 'ENGLISH → GERMAN', 'micro')
    + f'<rect x="20" y="76" width="280" height="58" fill="#fcf0cb" stroke="{INK}" stroke-width="2"/>'
    + '<path d="M30 122H290" stroke="#b9a98b" stroke-dasharray="2 4"/>'
    + t(60, 112, 'Die', 'w m-ink1') + t(156, 112, 'Fledermaus', 'w m-ink2') + t(264, 112, 'flog.', 'w m-ink3')
    + '<clipPath id="m-paper6"><rect x="21" y="77" width="278" height="56"/></clipPath>'
    + '<g clip-path="url(#m-paper6)"><g class="m-cover6">'
    '<rect x="20" y="70" width="284" height="70" fill="#6e6253"/><rect x="20" y="70" width="284" height="70" fill="url(#m-hatch)"/></g></g>'
    + buddy(70, 176, 'writer', COL['writer'], .8, label_cls='w-s')
    + '<g class="m-ink3">' + t(220, 192, 'TA-DA!', 'sfx') + '</g>')

# ---------- fact icons (160x100) ----------

ICONS = []


def building(x, label):
    out = ''.join(f'<rect x="{x}" y="{12 + k * 11}" width="40" height="11" fill="{"#f6ead0" if k % 2 else "#ead9b6"}" stroke="{INK}" stroke-width="1.5"/>' for k in range(6))
    return out + t(x + 20, 92, label, 'micro')


ICONS.append(('facts/layers.svg', 'Two buildings of six floors each, labelled reader and writer.', building(28, 'READER') + building(92, 'WRITER')))
ICONS.append(('facts/heads.svg', 'Eight magnifying glasses in different colors.', ''.join(
    f'<g transform="translate({28 + (i % 4) * 34} {30 + (i // 4) * 36})"><circle r="10" fill="#fff8e3" stroke="{c}" stroke-width="3.5"/>'
    f'<path d="M7 7l8 8" stroke="{c}" stroke-width="4" stroke-linecap="round"/></g>' for i, c in enumerate(EIGHT))))
ICONS.append(('facts/d-model.svg', 'A grid of exactly 512 small squares.',
              f'<rect x="16" y="14" width="128" height="64" fill="url(#m-grid)" stroke="{INK}" stroke-width="1.5"/>' + t(80, 94, '512 SQUARES', 'micro')))
ICONS.append(('facts/waves.svg', 'A sine wave and a cosine wave.',
              f'<path d="M8 50C24 14 40 14 56 50S88 86 104 50 136 14 152 50" fill="none" stroke="{RED}" stroke-width="3"/>'
              '<path d="M8 22C24 22 40 78 56 78S88 22 104 22 136 78 152 78" fill="none" stroke="#377675" stroke-width="3" stroke-dasharray="6 4"/>'
              + t(80, 96, 'SINE + COSINE', 'micro')))
ICONS.append(('facts/training.svg', 'A clock and eight graphics chips.',
              f'<circle cx="46" cy="48" r="32" fill="#fff8e3" stroke="{INK}" stroke-width="2.5"/>'
              f'<path d="M46 48V26" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
              f'<g class="m-spin-slow"><path d="M46 48h20" stroke="{RED}" stroke-width="3" stroke-linecap="round"/></g>'
              + ''.join(f'<rect x="{96 + (i % 2) * 28}" y="{12 + (i // 2) * 19}" width="22" height="14" rx="2" fill="#377675" stroke="{INK}" stroke-width="1.5"/>' for i in range(8))
              + t(123, 96, '8 CHIPS', 'micro')))

if __name__ == '__main__':
    for name, title, body in PANELS:
        write(OUT, name, standalone('0 0 320 220', body, title))
    for name, title, body in ICONS:
        write(OUT, name, standalone('0 0 160 100', body, title))
    print(f'wrote {len(PANELS)} panels and {len(ICONS)} icons to {OUT}')
