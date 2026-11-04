"""Builds the "How the machine actually works" comic section of site/index.html.

Run from the repo root:  python3 tools/build_machine.py
It replaces everything between the machine:start / machine:end markers (CSS, HTML and JS),
so it is safe to run again after editing the panels below.
"""
import re
from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / 'site' / 'index.html'
INK = '#322e24'
RED = '#a13324'
COL = {'The': '#f7d79b', 'bat': '#efae78', 'flew': '#a2c2a7', 'writer': '#dc9665', 'looker': '#c3b2d8'}


# ---------- drawing helpers ----------

def t(x, y, s, cls='', anchor='middle', style=''):
    c = f' class="{cls}"' if cls else ''
    st = f' style="{style}"' if style else ''
    return f'<text x="{x}" y="{y}"{c} text-anchor="{anchor}"{st}>{s}</text>'


def anim(cls, delay=None, extra=''):
    """class + optional animation-delay attributes for an animated group."""
    st = f'animation-delay:{delay}s;' if delay is not None else ''
    st += extra
    return f' class="{cls}"' + (f' style="{st}"' if st else '')


def buddy(x, y, word='', color='#efae78', s=1, cls='', delay=None, label_cls='w'):
    label = t(0, 12, word, label_cls) if word else ''
    inner = f'<g transform="translate({x} {y}) scale({s})"><use href="#wb" style="color:{color}"/>{label}</g>'
    return f'<g{anim(cls, delay)}>{inner}</g>' if cls else inner


def bubble(x, y, w, h, lines, tip, cls='b'):
    tx, ty = tip
    if ty > y + h:      # tail from the bottom edge
        bc = min(max(tx, x + 22), x + w - 22)
        tail = f'M{bc - 9} {y + h - 2}L{tx} {ty}L{bc + 9} {y + h - 2}'
    elif ty < y:        # tail from the top edge
        bc = min(max(tx, x + 22), x + w - 22)
        tail = f'M{bc - 9} {y + 2}L{tx} {ty}L{bc + 9} {y + 2}'
    else:               # tail from a side
        side = x + 2 if tx < x else x + w - 2
        cy = y + h / 2
        tail = f'M{side} {cy - 8:g}L{tx} {ty}L{side} {cy + 8:g}'
    out = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>'
           f'<path d="{tail}" fill="#fff8e3" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>')
    y0 = y + h / 2 - (len(lines) - 1) * 10 + 6
    for i, line in enumerate(lines):
        out += t(x + w / 2, f'{y0 + i * 20:g}', line, cls)
    return out


def can(x, y, color, rot=0, cls='', delay=None):
    body = (f'<g transform="translate({x} {y}) rotate({rot})"><rect x="-18" y="-16" width="36" height="32" rx="3" fill="{color}" stroke="{INK}" stroke-width="2"/>'
            f'<ellipse cx="0" cy="-16" rx="18" ry="5" fill="#f6f0df" stroke="{INK}" stroke-width="2"/>'
            f'<path d="M-18 -4h36" stroke="{INK}" stroke-width="1.5" opacity=".5"/></g>')
    return f'<g{anim(cls, delay)}>{body}</g>' if cls else body


def gear(x, y, r=10, delay=None):
    return (f'<g{anim("m-spin", delay)}><circle cx="{x}" cy="{y}" r="{r}" fill="#edca75" stroke="{INK}" stroke-width="6" stroke-dasharray="3.2 3"/>'
            f'<circle cx="{x}" cy="{y}" r="{r * .38:g}" fill="{INK}"/></g>')


def mini_bat(x, y, s=1):
    return (f'<path transform="translate({x} {y}) scale({s})" fill="#343444" stroke="#26251f" stroke-width="1.5" stroke-linejoin="round" '
            'd="M-28 0Q-18-15-5-5Q0-11 5-5Q18-15 28 0Q18-4 12 4Q6 0 0 7Q-6 0-12 4Q-18-4-28 0Z"/>')


def stick_bat(x, y, s=1):
    return (f'<g transform="translate({x} {y}) rotate(-28) scale({s})" stroke="{INK}" stroke-width="2">'
            '<path d="M-30 -3L18 -7Q30 -8 30 0Q30 8 18 7L-30 3Z" fill="#e29b52"/><circle cx="-31" cy="0" r="4" fill="#e29b52"/></g>')


def panel(bg, body, caption, label):
    return (f'<figure class="panel"><figcaption>{caption}</figcaption>'
            f'<svg class="cp" viewBox="0 0 320 220" role="img" aria-label="{label}">'
            f'<rect width="320" height="220" fill="{bg}"/><rect width="320" height="220" fill="url(#dots)" opacity=".22"/>'
            f'{body}</svg></figure>')


def strip(n, title, kicker, panels, grown_up):
    return (f'<article class="strip"><header><span class="chapnum">{n:02d}</span><div><h3>{title}</h3>'
            f'<span class="kicker">{kicker}</span></div><span class="label stamp">Illustration · numbers invented</span></header>'
            f'<div class="comic">{"".join(panels)}</div><p class="gw">Grown-up words: {grown_up}</p></article>')


# ---------- strip 1: number codes ----------

p = []
body = (f'<rect x="170" y="34" width="124" height="90" rx="7" fill="#d8cfb8" stroke="{INK}" stroke-width="3"/>'
        f'<rect x="181" y="45" width="102" height="62" fill="#3d4a45" stroke="{INK}" stroke-width="2"/>'
        + t(232, 72, 'b · a · t', 'mono', style='fill:#a2c2a7')
        + f'<g{anim("m-blink")}>' + t(232, 98, '? ? ?', 'mono', style='fill:#f8d065') + '</g>'
        + f'<path d="M222 124h20v14h-20zM202 138h60v8h-60z" fill="#b5ab92" stroke="{INK}" stroke-width="2"/>'
        + buddy(78, 120, 'bat', COL['bat'])
        + f'<g{anim("m-bob")}>' + t(112, 70, '?', 'sfx') + '</g>'
        + bubble(150, 162, 158, 44, ['Letters? Huh?'], (232, 148)))
p.append(panel('#efd5b7', body, 'Computers can’t read letters. They only understand <b>numbers</b>.',
               'A confused computer looks at the word bat and shows question marks.'))

digits = ['3', '8', '1', '6', '4']
squares = ''.join(
    f'<g{anim("m-loop-pop", round(.9 + i * .3, 1))}><rect x="{214 + i * 20}" y="88" width="18" height="22" fill="{c}" stroke="{INK}" stroke-width="1.5"/>'
    + t(223 + i * 20, 104, d, 'mono-s') + '</g>'
    for i, (d, c) in enumerate(zip(digits, ['#d9824f', '#efae78', '#c86f3f', '#f3c39a', '#e89a66'])))
body = (f'<path d="M118 62L134 38H186L202 62Z" fill="#dc9665" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
        f'<rect x="108" y="62" width="104" height="82" rx="5" fill="#719f9d" stroke="{INK}" stroke-width="3"/>'
        + gear(160, 102, 17) + gear(188, 80, 8, .2)
        + f'<path d="M108 100h-8M212 100h6" stroke="{INK}" stroke-width="3"/>'
        + f'<g{anim("m-feed")}><rect x="24" y="86" width="60" height="30" rx="5" fill="{COL["bat"]}" stroke="{INK}" stroke-width="2"/>'
        + t(54, 107, 'bat', 'w') + '</g>'
        + squares + t(262, 130, '…AND MORE', 'micro')
        + t(160, 176, 'CODE MACHINE', 'micro') + t(160, 204, 'whirr… clunk!', 'sfx-s'))
p.append(panel('#f0e3c6', body, 'So every word goes through a code machine and comes out as a long list of numbers: its <b>code</b>. Words with similar meanings get similar codes.',
               'The word bat goes into a machine with spinning gears and comes out as a row of number squares.'))

chairs = ''
for i, (w, x) in enumerate([('The', 60), ('bat', 160), ('flew', 260)]):
    chairs += (f'<path d="M{x - 30} 150v40M{x + 30} 150v40" stroke="#6b4f36" stroke-width="5" stroke-linecap="round"/>'
               f'<rect x="{x - 36}" y="144" width="72" height="11" rx="3" fill="#a27c55" stroke="{INK}" stroke-width="2"/>'
               f'<circle cx="{x}" cy="181" r="14" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>' + t(x, 187, str(i + 1), 'w'))
    chairs += buddy(x, 116, w, COL[w], .82, 'm-hop', round(i * .35, 2))
body = chairs + bubble(70, 12, 180, 40, ['Seats keep us in order!'], (160, 86))
p.append(panel('#b8cec0', body, 'All the words are read at the <b>same time</b>, so each one also gets a seat number. That keeps “The bat flew” from turning into “flew bat The.”',
               'The, bat and flew hop onto chairs numbered 1, 2 and 3.'))
strip1 = strip(1, 'Every word gets a number code', 'How words turn into numbers', p, 'embeddings and positional encoding')

# ---------- strip 2: ask around ----------

p = []
body = (buddy(80, 150, 'bat', COL['bat'])
        + f'<g{anim("m-bob")}>' + t(106, 104, '?', 'sfx') + '</g>'
        + '<circle cx="128" cy="138" r="5" fill="#fff8e3" stroke="#322e24" stroke-width="2"/><circle cx="142" cy="124" r="8" fill="#fff8e3" stroke="#322e24" stroke-width="2"/>'
        + f'<ellipse cx="216" cy="76" rx="94" ry="56" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>'
        + f'<g{anim("m-alt-a")}>' + mini_bat(162, 74, 1) + t(162, 112, 'animal?', 'b-s') + '</g>'
        + t(214, 82, 'or', 'b')
        + f'<g{anim("m-alt-b")}>' + stick_bat(262, 70, .9) + t(262, 112, 'stick?', 'b-s') + '</g>')
p.append(panel('#82acad', body, '“Bat” has a puzzle: is it the <b>animal</b> or the <b>stick</b> you hit a ball with?',
               'Bat wonders whether it is a flying animal or a baseball bat.'))

body = (t(60, 54, 'NAME TAG', 'micro') + t(260, 54, 'NAME TAG', 'micro') + t(160, 30, 'QUESTION', 'micro', style='fill:#a13324')
        + f'<path d="M60 96v44M260 96v44M160 92v40" stroke="{INK}" stroke-width="3"/>'
        + f'<g{anim("m-swing")}><rect x="12" y="62" width="96" height="34" rx="4" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>' + t(60, 84, 'helper word', 'b-s') + '</g>'
        + f'<g{anim("m-swing", .6)}><rect x="212" y="62" width="96" height="34" rx="4" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>' + t(260, 84, 'about flying', 'b-s') + '</g>'
        + f'<g{anim("m-wiggle")}><rect x="128" y="38" width="64" height="54" rx="6" fill="#fff8e3" stroke="{RED}" stroke-width="3"/>' + t(160, 77, '?', 'sfx') + '</g>'
        + buddy(60, 162, 'The', COL['The'], .85) + buddy(160, 162, 'bat', COL['bat'], .85) + buddy(260, 162, 'flew', COL['flew'], .85))
p.append(panel('#b8cec0', body, 'So “bat” holds up a <b>question</b>. Every word holds up a <b>name tag</b> that says what it is about.',
               'Bat holds a question card. The holds a tag saying helper word; flew holds a tag saying about flying.'))

rows = ''
for i, (w, share, fill) in enumerate([('The', 10, '#cfa64b'), ('bat', 20, '#c86f3f'), ('flew', 70, '#377675')]):
    y = 52 + i * 46
    rows += (t(18, y + 16, w, 'w', 'start')
             + f'<rect x="76" y="{y}" width="170" height="22" fill="#ddcfb0" stroke="{INK}" stroke-width="2"/>'
             + f'<rect class="m-meter" x="76" y="{y}" width="{170 * share / 100:g}" height="22" fill="{fill}" style="animation-delay:{i * .25}s"/>'
             + t(302, y + 18, f'{share}%', 'w', 'end'))
body = (t(160, 30, 'MATCH-O-METER', 'micro') + rows
        + f'<g{anim("m-pulse")}>' + t(160, 204, '“flew” matches best!', 'sfx-s') + '</g>')
p.append(panel('#f0e3c6', body, 'The machine checks how well each tag matches the question. “Flew” matches best, so “bat” will listen to it the most. The shares always add up to <b>100%</b>.',
               'A match meter: The 10 percent, bat 20 percent, flew 70 percent.'))
strip2 = strip(2, '“Bat” asks around', 'How a word decides who to listen to', p,
               'queries, keys and attention weights (scaled dot-product attention)')

# ---------- strip 3: blend it in ----------

p = []
body = ''
for i, (w, x, c) in enumerate([('The', 60, '#e9c46a'), ('bat', 160, '#d9824f'), ('flew', 260, '#5d8c75')]):
    body += buddy(x, 92, w, COL[w], .82) + can(x, 162, c, 0, 'm-wobble', round(i * .4, 1))
body += t(160, 210, 'EACH WORD’S OWN PAINT', 'micro')
p.append(panel('#f0e3c6', body, 'Every word also carries a can of <b>paint</b>: its own meaning, ready to share.',
               'The, bat and flew each hold a paint can: yellow, orange and green.'))

body = (f'<path d="M78 56Q120 70 146 150" class="m-flow" fill="none" stroke="#e9c46a" stroke-width="3"/>'
        f'<path d="M160 64V150" class="m-flow" fill="none" stroke="#d9824f" stroke-width="7"/>'
        f'<path d="M242 56Q200 70 174 150" class="m-flow" fill="none" stroke="#5d8c75" stroke-width="15"/>'
        + can(62, 52, '#e9c46a', 62) + can(160, 44, '#d9824f', 180) + can(258, 52, '#5d8c75', -62)
        + t(60, 126, '10%', 'w') + t(150, 104, '20%', 'w', 'end') + t(250, 120, '70%', 'w')
        + '<clipPath id="m-bucket"><path d="M120 142H200L192 200H128Z"/></clipPath>'
        + f'<g clip-path="url(#m-bucket)"><rect class="m-fill" x="118" y="150" width="84" height="52" fill="#7c9f80"/></g>'
        + f'<path d="M120 142H200L192 200H128Z" fill="none" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
        + t(160, 182, 'bat', 'w', style='fill:#fff8e3'))
p.append(panel('#c2d4cf', body, '“Bat” mixes paint from every word, using the match shares: <b>lots of “flew,”</b> some of itself, a little “The.”',
               'Three paint cans pour into a bucket labelled bat: a thick green stream from flew, thinner ones from bat and The.'))

wings = (f'<g transform="translate(-100 30)"><g{anim("m-flap")} fill="#343444" stroke="#26251f" stroke-width="2" stroke-linejoin="round">'
         '<path d="M228 90Q208 66 182 68Q191 81 187 94Q200 88 205 103Q214 95 228 104Z"/>'
         '<path d="M292 90Q312 66 338 68Q329 81 333 94Q320 88 315 103Q306 95 292 104Z"/></g></g>')
stars = ''.join(f'<g{anim("m-twinkle", d)}><use href="#mstar" x="{x}" y="{y}"/></g>' for x, y, d in [(40, 160, 0), (282, 150, .7), (300, 70, 1.4), (24, 96, 2)])
body = (stars + wings + buddy(160, 126, 'bat', '#b5b98f')
        + bubble(56, 12, 208, 44, ['I’m the one with wings!'], (176, 96)))
p.append(panel('#82acad', body, 'Now “bat” has a bit of “flew” mixed into its code. It knows it’s the <b>animal with wings</b>!',
               'Bat, now tinted green, grows flapping wings and says it is the one with wings.'))
strip3 = strip(3, 'Blend it in', 'How a word picks up meaning from its neighbors', p, 'a weighted sum of values')

# ---------- strip 4: many lookers ----------

p = []
body = (f'<rect x="150" y="112" width="156" height="48" rx="5" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>'
        + t(228, 143, 'The bat flew', 'w')
        + f'<g{anim("m-scan")}><circle cx="186" cy="136" r="17" fill="#ffffff" fill-opacity=".35" stroke="{INK}" stroke-width="4"/>'
        f'<path d="M198 148l14 14" stroke="{INK}" stroke-width="6" stroke-linecap="round"/></g>'
        + buddy(70, 150, 'looker', COL['looker'], .9, label_cls='w-s')
        + bubble(16, 14, 210, 58, ['I can only watch one', 'clue at a time…'], (78, 120)))
p.append(panel('#efd5b7', body, 'One <b>looker</b> can only hunt for one kind of clue at a time.',
               'A single looker scans the sentence with a magnifying glass.'))

targets = [2, 0, 1, 2, 0, 1, 2, 1]
cols8 = ['#a13324', '#377675', '#b9603a', '#5d6aa1', '#8a5a9a', '#4f7a66', '#b08a2c', '#7a4a3a']
wx = [70, 160, 250]
body = ''
for i, (tg, c) in enumerate(zip(targets, cols8)):
    x = 24 + i * 39
    body += f'<path class="m-dash" d="M{x} 62Q{x} 120 {wx[tg]} 168" fill="none" stroke="{c}" stroke-width="2.5" style="animation-delay:{i * .15:g}s"/>'
for i, c in enumerate(cols8):
    x = 24 + i * 39
    body += buddy(x, 44, '', COL['looker'], .42) + t(x, 16, str(i + 1), 'micro', style=f'fill:{c}')
body += ''.join(t(x, 196, w, 'w') for x, w in zip(wx, ['The', 'bat', 'flew']))
p.append(panel('#f0e3c6', body, 'So the machine uses <b>8 lookers at once</b>. Each one hunts for a different clue, like “who did it?” or “what happened?”',
               'Eight small lookers each draw a dotted line to a different word in The bat flew.'))

notes = ''
import math
for i, c in enumerate(cols8):
    a = math.radians(i * 45 - 90)
    x, y = 160 + 124 * math.cos(a), 112 + 80 * math.sin(a)
    notes += (f'<g class="m-gather" style="--dx:{(160 - x) * .55:.0f}px;--dy:{(112 - y) * .55:.0f}px;animation-delay:{i * .12:.2f}s">'
              f'<rect x="{x - 15:.0f}" y="{y - 12:.0f}" width="30" height="24" fill="{c}" stroke="{INK}" stroke-width="1.5" opacity=".9"/>'
              f'<path d="M{x - 9:.0f} {y - 3:.0f}h18M{x - 9:.0f} {y + 4:.0f}h12" stroke="#fff8e3" stroke-width="2"/></g>')
body = (notes + f'<rect x="112" y="80" width="96" height="64" rx="3" fill="#fff8e3" stroke="{INK}" stroke-width="2.5"/>'
        + t(160, 106, 'all the', 'b-s') + t(160, 126, 'clues', 'w')
        + f'<g{anim("m-pulse")}>' + t(268, 212, 'GLUE!', 'sfx-s') + '</g>')
p.append(panel('#c9d3c0', body, 'Then the 8 lookers <b>glue their notes together</b>, so no clue gets lost.',
               'Eight colored sticky notes fly into one big note labelled all the clues.'))
strip4 = strip(4, 'Many lookers', 'Why one look is not enough', p, 'multi-head attention, with 8 heads')

# ---------- strip 5: six floors ----------

p = []
body = (f'<path class="m-dash" d="M70 120Q110 70 150 120" fill="none" stroke="{RED}" stroke-width="3"/>'
        f'<path class="m-dash" d="M170 120Q210 70 250 120" fill="none" stroke="#377675" stroke-width="3" style="animation-delay:.4s"/>'
        f'<path class="m-dash" d="M60 116Q160 10 260 116" fill="none" stroke="#5d6aa1" stroke-width="3" style="animation-delay:.8s"/>'
        + buddy(60, 156, 'The', COL['The'], .85) + buddy(160, 156, 'bat', COL['bat'], .85) + buddy(260, 156, 'flew', COL['flew'], .85)
        + t(14, 32, 'LISTEN', 'sfx', 'start'))
p.append(panel('#b8cec0', body, 'On each floor, the words first <b>listen</b> to each other. That’s strips 2 to 4.',
               'The, bat and flew are linked by dotted listening lines.'))

body = t(14, 32, 'THINK', 'sfx', 'start')
for i, (w, x) in enumerate([('The', 60), ('bat', 160), ('flew', 260)]):
    body += (f'<ellipse cx="{x}" cy="78" rx="38" ry="26" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>'
             f'<circle cx="{x - 4}" cy="112" r="4" fill="#fff8e3" stroke="{INK}" stroke-width="1.5"/>'
             + gear(x, 78, 12, i * .3) + buddy(x, 156, w, COL[w], .85))
p.append(panel('#f0e3c6', body, 'Then each word <b>thinks</b> quietly on its own for a moment, polishing its code.',
               'Each word has its own thought bubble with a spinning gear.'))

body = f'<path d="M84 200H236" stroke="{INK}" stroke-width="3"/><path d="M96 26H224" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
for k in range(1, 7):
    y = 200 - k * 28
    body += (f'<rect x="104" y="{y}" width="112" height="28" fill="{"#f6ead0" if k % 2 else "#ead9b6"}" stroke="{INK}" stroke-width="2"/>'
             + t(112, y + 18, f'FLOOR {k}', 'micro', 'start'))
body += (f'<g class="m-ride"><rect x="106" y="31" width="108" height="24" rx="3" fill="none" stroke="{RED}" stroke-width="3"/>'
         + ''.join(f'<rect x="{222 + j * 12}" y="38" width="10" height="10" fill="{c}" stroke="{INK}" stroke-width="1.5"/>' for j, c in enumerate([COL['The'], COL['bat'], COL['flew']]))
         + '</g>' + t(40, 70, 'listen', 'b-s') + t(40, 90, '+ think', 'b-s') + t(40, 110, 'on every', 'b-s') + t(40, 130, 'floor', 'b-s')
         + f'<g{anim("m-twinkle")}><use href="#mstar" x="280" y="40"/></g>' + t(280, 70, 'smarter!', 'b-s'))
p.append(panel('#e6d3b0', body, 'The reader stacks <b>6 floors</b> of listen-and-think. Each floor makes the codes a little smarter. The writer has 6 floors too.',
               'The three words ride an elevator up a six-floor building.'))
strip5 = strip(5, 'Six floors', 'Doing it again and again', p,
               'a stack of 6 layers, each with self-attention and a feed-forward network')

# ---------- strip 6: no peeking ----------

p = []
body = (f'<rect x="20" y="34" width="150" height="86" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>'
        + t(95, 58, 'ENGLISH', 'micro') + t(95, 90, 'The bat flew.', 'w')
        + f'<path class="m-dash" d="M214 114L170 86M214 114L170 104" fill="none" stroke="{RED}" stroke-width="2.5"/>'
        + buddy(244, 128, 'writer', COL['writer'], 1, label_cls='w-s')
        + bubble(16, 150, 196, 52, ['I can read all', 'of the English!'], (212, 140)))
p.append(panel('#c9d3c0', body, 'The <b>writer</b> makes the German sentence. It can read the whole English sentence whenever it likes.',
               'The writer looks at a page that says The bat flew.'))

body = (f'<rect x="110" y="66" width="196" height="54" fill="#fcf0cb" stroke="{INK}" stroke-width="2"/>'
        + t(142, 100, 'Die', 'w')
        + f'<g{anim("m-shake")}><rect x="172" y="60" width="140" height="66" fill="#6e6253" stroke="{INK}" stroke-width="2"/>'
        f'<rect x="172" y="60" width="140" height="66" fill="url(#m-hatch)"/>'
        f'<rect x="190" y="82" width="104" height="22" fill="#6e6253"/>' + t(242, 98, 'NO PEEKING', 'micro', style='fill:#f6f0df') + '</g>'
        + f'<path d="M96 156l18-38" stroke="{RED}" stroke-width="4" stroke-linecap="round"/>'
        + buddy(64, 160, 'writer', COL['writer'], 1, label_cls='w-s')
        + f'<g{anim("m-bob")}>' + t(242, 46, '?', 'sfx') + '</g>'
        + bubble(132, 152, 176, 44, ['What comes next?'], (100, 168)))
p.append(panel('#efd5b7', body, 'But it writes <b>one word at a time</b>, and a cover hides the words still to come. It has to guess the next word, like on a spelling test.',
               'The writer has written Die; a cover marked no peeking hides the rest.'))

body = (t(160, 34, 'The bat flew.', 'w') + t(160, 56, 'ENGLISH → GERMAN', 'micro')
        + f'<rect x="20" y="76" width="280" height="58" fill="#fcf0cb" stroke="{INK}" stroke-width="2"/>'
        + f'<path d="M30 122H290" stroke="#b9a98b" stroke-dasharray="2 4"/>'
        + t(60, 112, 'Die', 'w m-ink1') + t(156, 112, 'Fledermaus', 'w m-ink2') + t(264, 112, 'flog.', 'w m-ink3')
        + '<g clip-path="url(#m-paper6)"><g class="m-cover6">'
        f'<rect x="20" y="70" width="284" height="70" fill="#6e6253"/><rect x="20" y="70" width="284" height="70" fill="url(#m-hatch)"/></g></g>'
        + buddy(70, 176, 'writer', COL['writer'], .8, label_cls='w-s')
        + f'<g class="m-ink3">' + t(220, 192, 'TA-DA!', 'sfx') + '</g>')
p.append(panel('#b8cec0', body, 'Word by word: “Die Fledermaus flog.” That’s German for “The bat flew.” <i>Fledermaus</i> means “flutter-mouse”!',
               'The cover slides away one word at a time, revealing Die Fledermaus flog.'))
strip6 = strip(6, 'Write in order. No peeking.', 'How the translation gets written', p, 'masked self-attention in the decoder')

# ---------- evidence cards ----------

ARXIV = 'https://arxiv.org/html/1706.03762'


def building(x, label):
    out = ''.join(f'<rect x="{x}" y="{12 + k * 11}" width="40" height="11" fill="{"#f6ead0" if k % 2 else "#ead9b6"}" stroke="{INK}" stroke-width="1.5"/>' for k in range(6))
    return out + t(x + 20, 92, label, 'micro')


icon_layers = building(28, 'READER') + building(92, 'WRITER')
icon_heads = ''.join(
    f'<g transform="translate({28 + (i % 4) * 34} {30 + (i // 4) * 36})"><circle r="10" fill="#fff8e3" stroke="{c}" stroke-width="3.5"/>'
    f'<path d="M7 7l8 8" stroke="{c}" stroke-width="4" stroke-linecap="round"/></g>' for i, c in enumerate(cols8))
icon_width = f'<rect x="16" y="14" width="128" height="64" fill="url(#m-grid)" stroke="{INK}" stroke-width="1.5"/>' + t(80, 94, '512 SQUARES', 'micro')
icon_waves = (f'<path d="M8 50C24 14 40 14 56 50S88 86 104 50 136 14 152 50" fill="none" stroke="{RED}" stroke-width="3"/>'
              f'<path d="M8 22C24 22 40 78 56 78S88 22 104 22 136 78 152 78" fill="none" stroke="#377675" stroke-width="3" stroke-dasharray="6 4"/>'
              + t(80, 96, 'SINE + COSINE', 'micro'))
icon_time = (f'<circle cx="46" cy="48" r="32" fill="#fff8e3" stroke="{INK}" stroke-width="2.5"/>'
             f'<path d="M46 48V26" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
             f'<g class="m-spin-slow"><path d="M46 48h20" stroke="{RED}" stroke-width="3" stroke-linecap="round"/></g>'
             + ''.join(f'<rect x="{96 + (i % 2) * 28}" y="{12 + (i // 2) * 19}" width="22" height="14" rx="2" fill="#377675" stroke="{INK}" stroke-width="1.5"/>' for i in range(8))
             + t(123, 96, '8 CHIPS', 'micro'))
FACTS = [
    (icon_layers, '6 + 6', 'The reader has 6 floors and the writer has 6 floors. The paper calls them encoder and decoder layers.', '§3.1', 'S3.SS1'),
    (icon_heads, '8', 'lookers work side by side in every attention step. The paper calls them attention heads.', '§3.2.2', 'S3.SS2.SSS2'),
    (icon_width, '512', 'numbers make up one word’s code in the base model. The grid above has exactly 512 squares. Paper name: d<sub>model</sub>.', '§3.1', 'S3.SS1'),
    (icon_waves, 'sin + cos', 'Seat numbers are made from smooth sine and cosine waves, then added to each word’s code.', '§3.5', 'S3.SS5'),
    (icon_time, '12 hours', 'to train the base model on one computer with 8 NVIDIA P100 graphics chips (100,000 steps). The big model took 3.5 days.', '§5.2', 'S5.SS2'),
]
cards = ''.join(
    f'<li><svg class="cp icon" viewBox="0 0 160 100" aria-hidden="true">{icon}</svg><b class="fig">{big}</b><p>{text}</p>'
    f'<a href="{ARXIV}#{anchor}">Paper {sec} ↗</a></li>'
    for icon, big, text, sec, anchor in FACTS)

defs = (f'<svg class="defs" width="0" height="0" aria-hidden="true"><defs>'
        f'<g id="wb" stroke="{INK}" stroke-width="2" stroke-linecap="round">'
        '<path d="M-14 25v10l-8 2M14 25v10l8 2M-34 2l-10-5M34 2l10-6" fill="none"/>'
        '<rect x="-34" y="-25" width="68" height="50" rx="10" fill="currentColor"/>'
        f'<circle cx="-7" cy="-14" r="2" fill="{INK}" stroke="none"/><circle cx="7" cy="-14" r="2" fill="{INK}" stroke="none"/>'
        '<path d="M-3 -9q3 3 6 0" fill="none"/></g>'
        f'<path id="mstar" d="M0 -10L3 -3 10 0 3 3 0 10 -3 3 -10 0 -3 -3Z" fill="#ffe597" stroke="{INK}" stroke-width="1"/>'
        '<pattern id="m-hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><path d="M0 0V7" stroke="#f6f0df" stroke-width="2" opacity=".3"/></pattern>'
        '<pattern id="m-grid" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="3" height="3" fill="#377675"/></pattern>'
        '<clipPath id="m-paper6"><rect x="21" y="77" width="278" height="56"/></clipPath>'
        '</defs></svg>')

html = (
    '<section id="machine" class="section machine">' + defs
    + '<div class="label">Science desk &nbsp; / &nbsp; Under the hood &nbsp; / &nbsp; A comic in six strips</div>'
    '<div class="story-intro"><h2>How the machine actually works</h2><button type="button" id="comic-motion">Pause the comics</button></div>'
    '<p class="machine-deck">Read each strip from left to right. The pictures move, like little GIFs. '
    'Our sentence is “The bat flew,” and the machine will turn it into German.</p>'
    '<p class="howto"><span class="label">How to read it</span> Drawings and numbers inside the strips are <b>made up</b> to explain the idea. '
    'Real numbers from the paper are in the box at the end.</p>'
    + strip1 + strip2 + strip3 + strip4 + strip5 + strip6
    + '<div class="facts"><div class="label">Evidence from the paper &nbsp; / &nbsp; Real numbers, with sources</div>'
    f'<ul>{cards}</ul></div></section>')

css = """
.machine-deck{font-size:clamp(18px,1.8vw,22px);line-height:1.35;margin:0 0 10px;max-width:40em}
.howto{font-size:16px;line-height:1.45;margin:0 0 22px;padding:10px 12px;border:1px dashed var(--line);max-width:46em}.howto .label{margin-right:8px}
.defs{position:absolute}
.strip{border-top:1px solid;padding-top:12px;margin-bottom:34px}
.strip header{display:flex;align-items:center;gap:12px;margin-bottom:12px}.strip header>div{flex:1}
.strip h3{font-size:clamp(25px,2.7vw,35px);letter-spacing:-.04em;margin:0}.kicker{font-style:italic;font-size:16px;color:#5e5748}
.stamp{border:1px solid var(--red);padding:2px 7px;white-space:nowrap}
.comic{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}
.panel{margin:0;display:flex;flex-direction:column}
.panel figcaption{position:relative;z-index:1;background:#f6e3a1;border:2px solid var(--ink);padding:8px 11px;font-size:17px;line-height:1.38;margin:0 14px -12px 0;align-self:flex-start;box-shadow:2px 2px 0 var(--ink)}
.panel svg{display:block;width:100%;height:auto;border:3px solid var(--ink);box-shadow:5px 5px 0 var(--ink);margin-top:auto}
.strip .gw{margin:16px 0 0;font:700 12px/1.5 'Courier New',monospace;text-transform:uppercase;letter-spacing:.06em;color:var(--red)}
.cp text{fill:#28261e;font:17px Georgia,serif}.cp .w{font:bold 20px Georgia,serif}.cp .w-s{font:bold 15px Georgia,serif}
.cp .b{font:18px Georgia,serif}.cp .b-s{font:15px Georgia,serif}.cp .micro{font:bold 12px 'Courier New',monospace;letter-spacing:1px}
.cp .mono{font:bold 20px 'Courier New',monospace}.cp .mono-s{font:bold 14px 'Courier New',monospace}
.cp .sfx,.cp .sfx-s{font:italic 900 30px Georgia,serif;fill:#a13324;stroke:#fff8e3;stroke-width:5px;paint-order:stroke;letter-spacing:-.02em}.cp .sfx-s{font-size:22px}
.facts{border-top:4px double;padding-top:12px;margin-bottom:34px}.facts ul{list-style:none;margin:12px 0 0;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px}
.facts li{border:2px solid var(--ink);background:#fbf3dc;padding:12px;display:flex;flex-direction:column;gap:6px;box-shadow:4px 4px 0 var(--ink)}
.facts .icon{width:100%;max-width:200px;height:auto;margin:0 auto 4px}.facts .fig{font-size:34px;letter-spacing:-.04em;color:var(--red);line-height:1}
.facts p{margin:0;font-size:16px;line-height:1.45;flex:1}.facts a{font:700 12px 'Courier New',monospace;letter-spacing:.06em}
:where(.machine [class*="m-"]){transform-box:fill-box;transform-origin:center}
.m-blink{animation:m-blink 1.2s steps(2) infinite}.m-bob{animation:m-bob 1.6s ease-in-out infinite alternate}
.m-spin{animation:m-spin 3s linear infinite}.m-spin-slow{transform-origin:left center;animation:m-spin 4s linear infinite}
.m-feed{animation:m-feed 4.5s ease-in-out infinite}.m-loop-pop{animation:m-loop-pop 4.5s ease-out infinite}
.m-hop{animation:m-hop 2.4s ease-in-out infinite}
.m-alt-a{animation:m-alt 3.6s ease-in-out infinite}.m-alt-b{animation:m-alt 3.6s ease-in-out -1.8s infinite}
.m-swing{transform-origin:center top;animation:m-swing 2.2s ease-in-out infinite alternate}.m-wiggle{animation:m-wiggle 1.4s ease-in-out infinite}
.m-meter{transform-origin:left center;animation:m-meter 6s ease-out infinite}.m-pulse{animation:m-pulse 1.8s ease-in-out infinite}
.m-wobble{animation:m-wobble 1.8s ease-in-out infinite alternate}.m-flow{stroke-dasharray:10 8;animation:m-flow .9s linear infinite}
.m-fill{transform-origin:center bottom;animation:m-fill 6s ease-in-out infinite}.m-flap{animation:flap .45s ease-in-out infinite alternate}
.m-twinkle{animation:m-twinkle 2.4s ease-in-out infinite}.m-scan{animation:m-scan 3s ease-in-out infinite alternate}
.m-dash{stroke-dasharray:6 9;animation:trace 1.4s linear infinite}.m-gather{animation:m-gather 4s ease-in-out infinite}
.m-ride{animation:m-ride 8s ease-in-out infinite}.m-shake{animation:m-shake 2.6s ease-in-out infinite}
.m-cover6{transform:translateX(284px);animation:m-cover6 8s ease-in-out infinite}
.m-ink1{animation:m-ink1 8s infinite}.m-ink2{animation:m-ink2 8s infinite}.m-ink3{animation:m-ink3 8s infinite}
@keyframes m-blink{50%{opacity:0}}@keyframes m-bob{to{transform:translateY(-7px)}}@keyframes m-spin{to{transform:rotate(360deg)}}
@keyframes m-feed{0%{transform:none;opacity:0}10%,45%{opacity:1}60%{transform:translateX(70px);opacity:0}100%{transform:translateX(70px);opacity:0}}
@keyframes m-loop-pop{0%{transform:scale(0)}10%{transform:scale(1.2)}16%,88%{transform:scale(1)}100%{transform:scale(0)}}
@keyframes m-hop{0%,40%,100%{transform:none}20%{transform:translateY(-14px)}}
@keyframes m-alt{0%,100%{opacity:1;transform:scale(1.08)}50%{opacity:.35;transform:scale(.92)}}
@keyframes m-swing{from{transform:rotate(-4deg)}to{transform:rotate(4deg)}}@keyframes m-wiggle{0%,60%,100%{transform:none}70%{transform:rotate(-8deg)}80%{transform:rotate(8deg)}90%{transform:rotate(-4deg)}}
@keyframes m-meter{0%{transform:scaleX(0)}35%,100%{transform:scaleX(1)}}@keyframes m-pulse{50%{transform:scale(1.1)}}
@keyframes m-wobble{from{transform:rotate(-5deg)}to{transform:rotate(5deg)}}@keyframes m-flow{to{stroke-dashoffset:-36}}
@keyframes m-fill{0%{transform:scaleY(.05)}60%,100%{transform:scaleY(1)}}
@keyframes m-twinkle{50%{transform:scale(.5);opacity:.4}}@keyframes m-scan{to{transform:translateX(84px)}}
@keyframes m-gather{0%,15%{transform:none;opacity:1}55%,70%{transform:translate(var(--dx),var(--dy));opacity:0}100%{transform:none;opacity:1}}
@keyframes m-ride{0%,6%{transform:translateY(140px)}14%,20%{transform:translateY(112px)}28%,34%{transform:translateY(84px)}42%,48%{transform:translateY(56px)}56%,62%{transform:translateY(28px)}70%,96%{transform:none}100%{transform:translateY(140px)}}
@keyframes m-shake{0%,80%,100%{transform:none}84%{transform:translateX(-3px)}88%{transform:translateX(3px)}92%{transform:translateX(-2px)}}
@keyframes m-cover6{0%,10%{transform:none}16%,34%{transform:translateX(70px)}40%,58%{transform:translateX(198px)}64%,94%{transform:translateX(284px)}100%{transform:none}}
@keyframes m-ink1{0%,14%{opacity:0}18%,95%{opacity:1}100%{opacity:0}}@keyframes m-ink2{0%,38%{opacity:0}42%,95%{opacity:1}100%{opacity:0}}@keyframes m-ink3{0%,62%{opacity:0}66%,95%{opacity:1}100%{opacity:0}}
.js .machine .strip:not(.in) *,.js .machine .facts:not(.in) *,.m-hold *{animation-play-state:paused!important}
@media(prefers-reduced-motion:reduce){.machine *{animation:none!important}}
@media(max-width:760px){.strip header{flex-wrap:wrap}.stamp{order:3}.comic{gap:22px}.facts ul{grid-template-columns:1fr 1fr;gap:12px}.facts li{padding:9px}.facts p{font-size:15px}.facts .fig{font-size:27px}}
"""

js = """document.documentElement.classList.add('js');
const comicIO=new IntersectionObserver(es=>es.forEach(e=>e.target.classList.toggle('in',e.isIntersecting)),{rootMargin:'80px'});
document.querySelectorAll('.machine .strip,.machine .facts').forEach(s=>comicIO.observe(s));
let comicHeld=motion.matches;
function updateComic(){el('machine').classList.toggle('m-hold',comicHeld);el('comic-motion').textContent=comicHeld?'Play the comics':'Pause the comics'}
el('comic-motion').onclick=()=>{comicHeld=!comicHeld;updateComic()};
motion.addEventListener('change',()=>{comicHeld=motion.matches;updateComic()});
updateComic();
"""

page = PAGE.read_text()


def put(page, start, end, content, anchor):
    """Replace the marked block, or insert it before `anchor` the first time."""
    pat = re.compile(re.escape(start) + '.*?' + re.escape(end), re.S)
    block = start + content + end
    if pat.search(page):
        return pat.sub(lambda m: block, page, count=1)
    return page.replace(anchor, block + anchor, 1)


# One-time cleanup of the earlier step-through version (unmarked).
if '/* machine:start */' not in page and 'id="machine"' in page:
    page = page[:page.index('\n.machine-deck{')] + page[page.index('</style>'):]
    page = page[:page.index('<section id="machine"')] + page[page.index('<footer>'):]
    page = page[:page.index("document.documentElement.classList.add('js');")] + page[page.index('</script>'):]

page = put(page, '/* machine:start */', '/* machine:end */', css, '</style>')
page = put(page, '<!-- machine:start -->', '<!-- machine:end -->', html, '<footer>')
page = put(page, '/* machine-js:start */\n', '/* machine-js:end */\n', js, '</script>')
PAGE.write_text(page)
print('wrote', PAGE, len(page))
