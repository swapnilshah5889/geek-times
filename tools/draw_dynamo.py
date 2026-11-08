"""Draws the two lead plates for "Dynamo: Amazon's Highly Available Key-value Store".

Run from the repo root:  python3 tools/draw_dynamo.py
Writes standalone SVG files to public/media/dynamo/lead/.
Plate captions/alt text live in data/seed/papers/dynamo.json.
"""
import math
from pathlib import Path

from media_kit import COMIC_DEFS, INK, RED, anim, standalone, t, write

OUT = Path(__file__).resolve().parent.parent / 'public' / 'media' / 'dynamo' / 'lead'
CREAM = '#fbf3dc'
DEFS = COMIC_DEFS + (
    f'<marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
    f'<path d="M0 0L10 5L0 10Z" fill="{RED}"/></marker>')


def plate(bg, tag, body, caption):
    return (f'<rect width="600" height="340" fill="{bg}"/><rect width="600" height="340" fill="url(#dots)" opacity=".22"/>'
            + body
            + f'<rect x="10" y="288" width="580" height="44" fill="{CREAM}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
            + t(300, 317, caption, 'b')
            + t(22, 28, tag, 'micro', 'start', f'fill:{RED}')
            + f'<path d="M8 10Q300 5 592 9Q596 170 591 332Q300 336 9 331Q4 170 8 10Z" fill="none" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>')


def shoe(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})"><path d="M-14 -8L-4 -10L2 -2Q14 -2 15 6V9H-14Z" fill="{RED}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
            f'<path d="M-14 6H15" stroke="#f6f0df" stroke-width="2"/></g>')


def hat(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})"><ellipse cx="0" cy="6" rx="17" ry="4" fill="#377675" stroke="{INK}" stroke-width="2"/>'
            f'<path d="M-10 6Q-10 -10 0 -10T10 6Z" fill="#377675" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
            f'<path d="M-10 2H10" stroke="#f7d79b" stroke-width="2.5"/></g>')


def cart(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<path d="M-34 -22H-24L-16 14H22" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M-22 -12H30L24 8H-17Z" fill="#fff8e3" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
            f'<path d="M-6 -12L-4 8M10 -12L9 8" stroke="{INK}" stroke-width="1.5" opacity=".5"/>'
            f'<circle cx="-12" cy="22" r="5" fill="{INK}"/><circle cx="16" cy="22" r="5" fill="{INK}"/>'
            + shoe(-8, -17, .7) + hat(14, -17, .7) + '</g>')


def flame(x, y, s=1, cls='', delay=None):
    g = (f'<g transform="translate({x} {y}) scale({s})"><path d="M0 -50Q22 -22 18 -2Q16 14 0 14Q-18 14 -18 -2Q-18 -14 -8 -24Q-6 -8 2 -12Q-2 -30 0 -50Z" fill="{RED}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
         f'<path d="M0 -24Q12 -8 9 2Q8 10 0 10Q-9 10 -9 2Q-9 -6 0 -24Z" fill="#efae78"/>'
         f'<path d="M0 -8Q5 0 3 5Q2 8 0 8Q-4 8 -4 4Q-4 0 0 -8Z" fill="#f7d79b"/></g>')
    return f'<g{anim(cls, delay)}>{g}</g>' if cls else g


def smoke(x, y):
    return ''.join(f'<circle cx="{x + dx}" cy="{y - dy}" r="{r}" fill="#d8cfb8" stroke="{INK}" stroke-width="2.5"/>'
                   for dx, dy, r in [(0, 0, 12), (12, 22, 15), (-2, 46, 18), (14, 70, 14)])


def server(x, y, burning=True):
    out = f'<rect x="{x}" y="{y}" width="130" height="150" rx="6" fill="#b5ab92" stroke="{INK}" stroke-width="3.5"/>'
    for i in range(4):
        yy = y + 14 + i * 33
        out += (f'<rect x="{x + 12}" y="{yy}" width="106" height="24" rx="3" fill="#8e8672" stroke="{INK}" stroke-width="2"/>'
                f'<circle cx="{x + 28}" cy="{yy + 12}" r="4" fill="{RED if burning else "#a2c2a7"}" stroke="{INK}" stroke-width="1.5"/>'
                f'<path d="M{x + 46} {yy + 12}h54" stroke="{INK}" stroke-width="2" stroke-dasharray="4 4"/>')
    return out


# ---- fire: the machine burns, the cart carries on ----
fx, fy = 70, 100
fire_body = (smoke(fx + 120, fy - 10)
             + server(fx, fy)
             + flame(fx + 30, fy + 8, 1.5, 'm-pulse') + flame(fx + 95, fy + 20, 1.9, 'm-pulse', .5) + flame(fx + 62, fy + 70, 1.3, 'm-pulse', .9)
             + f'<g{anim("m-shake")}>' + t(fx + 65, fy + 180, 'FWOOSH!', 'sfx') + '</g>'
             + t(fx + 65, fy + 198, 'SERVER', 'micro')
             # monitor with the safe cart
             + f'<path d="M386 224h120v14h-120zM430 206h32v20h-32z" fill="#b5ab92" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
             + f'<rect x="352" y="76" width="188" height="132" rx="10" fill="#d8cfb8" stroke="{INK}" stroke-width="3.5"/>'
             + f'<rect x="364" y="88" width="164" height="108" rx="4" fill="#3d4a45" stroke="{INK}" stroke-width="2"/>'
             + f'<rect x="372" y="96" width="148" height="92" rx="3" fill="#f6ead0"/>'
             + cart(446, 148, 1.45)
             + t(446, 112, 'YOUR CART', 'micro')
             + f'<g{anim("m-bob")}>' + f'<circle cx="518" cy="82" r="20" fill="#a2c2a7" stroke="{INK}" stroke-width="3"/><path d="M509 82l7 8 12-15" fill="none" stroke="{INK}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></g>'
             + f'<path d="M262 160H338" stroke="{RED}" stroke-width="3.5" stroke-dasharray="6 6" stroke-linecap="round" marker-end="url(#ah)"/>'
             + t(446, 262, 'still there', 'w-s', style=f'fill:{RED}'))

# ---- cart-safe: three houses on a ring, each with a copy of the cart; one dark ----
cx, cy, R = 300, 164, 92
ring = f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{INK}" stroke-width="3" stroke-dasharray="10 7"/>'
houses = ''
for i, ang in enumerate([-90, 30, 150]):
    x = cx + R * math.cos(math.radians(ang)); y = cy + R * math.sin(math.radians(ang))
    dark = i == 2
    wall = '#5d5a52' if dark else '#f7d79b'
    roof = '#3b3932' if dark else RED
    glow = '' if dark else f'<circle cx="{x:.0f}" cy="{y:.0f}" r="52" fill="#ffe597" opacity=".45"/>'
    houses += (glow + f'<g transform="translate({x:.0f} {y:.0f})">'
               f'<rect x="-40" y="-16" width="80" height="52" fill="{wall}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
               f'<path d="M-48 -14L0 -48L48 -14Z" fill="{roof}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
               + ('' if dark else '<rect x="-30" y="-8" width="60" height="38" rx="2" fill="#fff8e3" opacity=".7"/>')
               + cart(0, 8, .62 if not dark else .62).replace('#fff8e3', '#8a867a' if dark else '#fff8e3')
               + ('<path d="M-30 -8L30 32M30 -8L-30 32" stroke="#a13324" stroke-width="4" stroke-linecap="round" opacity=".0"/>' if dark else '')
               + '</g>')
    if dark:
        houses += (f'<g transform="translate({x - 8:.0f} {y - 70:.0f})">' + t(0, 0, 'z z z', 'micro') + '</g>'
                   + t(x, y + 54, 'DARK', 'micro', style=f'fill:{RED}'))
    else:
        houses += t(x, y + 54, 'SAFE', 'micro', style='fill:#377675')
safe_body = (ring + houses
             + t(cx, cy + 6, 'ONE CART', 'w-s')
             + f'<g{anim("m-wiggle")}>' + t(500, 150, 'NO PROBLEM!', 'sfx-s') + '</g>')

# =====================================================================
# Comic panels (320x220), story panels (440x215), fact icons (160x100)
# =====================================================================
from media_kit import COL, EIGHT, bubble, buddy, gear, panel  # noqa: E402

OUT_ROOT = OUT.parent
PANELS = []   # (path under public/media/dynamo, viewBox, alt/title, body)
ICONS = []

TEAL = '#377675'
GREEN = '#a2c2a7'
GOLD = '#ffe597'
WOOD = '#a27c55'


def add(name, alt, bg, body):
    PANELS.append((f'comic/{name}.svg', '0 0 320 220', alt, panel(bg, body)))


def story(name, alt, bg, body):
    PANELS.append((f'story/{name}.svg', '0 0 440 215', alt,
                   f'<rect width="440" height="215" fill="{bg}"/><rect width="440" height="215" fill="url(#dots)" opacity=".22"/>{body}'))


def icon(name, alt, body, bg='#f0e3c6'):
    ICONS.append((f'facts/{name}.svg', '0 0 160 100', alt,
                  f'<rect width="160" height="100" fill="{bg}"/><rect width="160" height="100" fill="url(#dots)" opacity=".22"/>{body}'))


def pt(cx, cy, r, deg):
    return cx + r * math.cos(math.radians(deg)), cy + r * math.sin(math.radians(deg))


def arc(cx, cy, r, a0, a1):
    """Clockwise (on screen) arc along a circle."""
    x0, y0 = pt(cx, cy, r, a0)
    x1, y1 = pt(cx, cy, r, a1)
    large = 0 if (a1 - a0) % 360 <= 180 else 1
    return f'M{x0:.1f} {y0:.1f}A{r} {r} 0 {large} 1 {x1:.1f} {y1:.1f}'


def scarf(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})"><path d="M-14 -5H14V6H-14Z" fill="{TEAL}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
            f'<path d="M-7 -5V6M0 -5V6M7 -5V6" stroke="#f6f0df" stroke-width="2"/>'
            f'<path d="M-9 6v7M-1 6v7M7 6v7" stroke="{INK}" stroke-width="2" stroke-linecap="round"/></g>')


def mcart(x, y, s=1, items=(), tag=None):
    """A shopping cart. items: (kind, dx, scale) with kind in shoe / hat / scarf."""
    out = (f'<g transform="translate({x} {y}) scale({s})">'
           f'<path d="M-34 -22H-24L-16 14H22" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
           f'<path d="M-22 -12H30L24 8H-17Z" fill="#fff8e3" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
           f'<path d="M-6 -12L-4 8M10 -12L9 8" stroke="{INK}" stroke-width="1.5" opacity=".5"/>'
           f'<circle cx="-12" cy="22" r="5" fill="{INK}"/><circle cx="16" cy="22" r="5" fill="{INK}"/>')
    for kind, dx, sc in items:
        out += {'shoe': shoe, 'hat': hat, 'scarf': scarf}[kind](dx, -17, sc)
    if tag:
        out += (f'<rect x="-8" y="-3" width="30" height="13" rx="2" fill="{GOLD}" stroke="{INK}" stroke-width="1.5"/>'
                + t(7, 7, tag, 'micro', style='font-size:9px'))
    return out + '</g>'


def house(x, y, s=1, dark=False, label=None, with_cart=True, glow=True):
    wall, roof = ('#5d5a52', '#3b3932') if dark else ('#f7d79b', RED)
    g = f'<circle cx="{x}" cy="{y}" r="{52 * s:.0f}" fill="{GOLD}" opacity=".45"/>' if (glow and not dark) else ''
    g += (f'<g transform="translate({x} {y}) scale({s})">'
          f'<rect x="-40" y="-16" width="80" height="52" fill="{wall}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
          f'<path d="M-48 -14L0 -48L48 -14Z" fill="{roof}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>')
    if with_cart:
        g += ('' if dark else '<rect x="-30" y="-8" width="60" height="38" rx="2" fill="#fff8e3" opacity=".7"/>')
        g += mcart(0, 8, .62).replace('#fff8e3', '#8a867a' if dark else '#fff8e3')
    if label:
        g += t(0, -20, label, 'w-s', style='fill:#fff8e3;font-size:17px')
    return g + '</g>'


def note(x, y, lines, rot=0, w=64, cls='w-s'):
    h = 12 + 19 * len(lines)
    out = (f'<g transform="translate({x} {y}) rotate({rot})"><rect x="{-w / 2}" y="{-h / 2}" width="{w}" height="{h}" fill="{GOLD}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
           f'<path d="M{w / 2 - 10} {h / 2}l10 -10v10z" fill="#e8c860" stroke="{INK}" stroke-width="1.5" stroke-linejoin="round"/>')
    y0 = -h / 2 + 22
    for i, ln in enumerate(lines):
        out += t(0, f'{y0 + i * 19:g}', ln, cls)
    return out + '</g>'


def fingerprint(x, y, r=22, color=TEAL):
    out = f'<g transform="translate({x} {y})"><circle r="{r}" fill="#fff8e3" stroke="{INK}" stroke-width="2.5"/>'
    for k in (.3, .55, .8):
        rr = r * k
        out += f'<path d="M{-rr:.1f} {rr * .5:.1f}A{rr:.1f} {rr:.1f} 0 0 1 {rr:.1f} {rr * .5:.1f}" fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round"/>'
    return out + f'<circle cy="{r * .1:.1f}" r="1.8" fill="{color}"/></g>'


def check(x, y, r=11, color=GREEN):
    return (f'<g transform="translate({x} {y})"><circle r="{r}" fill="{color}" stroke="{INK}" stroke-width="2"/>'
            f'<path d="M{-r * .45:.1f} 0l{r * .35:.1f} {r * .4:.1f} {r * .6:.1f} {-r * .8:.1f}" fill="none" stroke="{INK}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></g>')


def ring_with_houses(cx, cy, r, s, angles=(270, 342, 54, 126, 198), dark=(), with_cart=False):
    out = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{INK}" stroke-width="3" stroke-dasharray="10 7"/>'
    for a in angles:
        px, py = pt(cx, cy, r, a)
        out += house(round(px), round(py), s, dark=a in dark, with_cart=with_cart)
    return out


def fence(x0, x1, y):
    out = f'<path d="M{x0} {y - 10}H{x1}M{x0} {y + 6}H{x1}" stroke="{INK}" stroke-width="2.5"/>'
    for xx in range(x0, x1 + 1, 12):
        out += f'<path d="M{xx} {y + 22}V{y - 18}" stroke="{INK}" stroke-width="5" stroke-linecap="round"/><path d="M{xx} {y + 22}V{y - 18}" stroke="#f6f0df" stroke-width="2" stroke-linecap="round"/>'
    return out


def arrow(d, color=RED, w=3.5, dash='', extra=''):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"{da} marker-end="url(#ah)" {extra}/>'


# ---------- strip 1: the ring ----------

ringA = f'<circle cx="250" cy="112" r="50" fill="none" stroke="{INK}" stroke-width="3" stroke-dasharray="10 7"/>'
add('01a-name-to-spot', 'A cart name tag goes into a machine and comes out as a dot on a circle.', '#efd5b7',
    f'<g{anim("m-feed")}><path d="M28 96l12-12h46l0 28h-46z" fill="{GOLD}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/><circle cx="38" cy="98" r="3" fill="{INK}"/>'
    + t(66, 103, 'cart-42', 'micro', style='font-size:12px') + '</g>'
    + f'<path d="M96 52L108 34H152L164 52Z" fill="#dc9665" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
    f'<rect x="92" y="52" width="76" height="76" rx="5" fill="#719f9d" stroke="{INK}" stroke-width="3"/>'
    + gear(130, 90, 15) + gear(152, 70, 7, .2)
    + f'<path d="M168 100H198" stroke="{INK}" stroke-width="3" stroke-dasharray="6 5" marker-end="url(#ah)"/>'
    + ringA + f'<g{anim("m-pulse")}><circle cx="{pt(250,112,50,-35)[0]:.0f}" cy="{pt(250,112,50,-35)[1]:.0f}" r="9" fill="{RED}" stroke="{INK}" stroke-width="2.5"/></g>'
    + t(250, 118, 'CIRCLE', 'micro') + t(130, 152, 'HASH MACHINE', 'micro')
    + t(160, 196, 'name → spot', 'sfx-s'))

hx = ring_with_houses(160, 118, 70, .42)
add('01b-walk-clockwise', 'An arrow walks clockwise from a dot to the nearest house on the circle.', '#b8cec0',
    hx + arrow(arc(160, 118, 70, 225, 253), RED, 5)
    + f'<circle cx="{pt(160,118,70,225)[0]:.0f}" cy="{pt(160,118,70,225)[1]:.0f}" r="8" fill="{RED}" stroke="{INK}" stroke-width="2.5"/>'
    + t(160, 114, 'CLOCKWISE', 'w-s') + t(160, 134, 'first house wins', 'micro')
    + t(46, 40, 'START', 'micro', style=f'fill:{RED}') + t(266, 40, 'STOP!', 'micro', style=f'fill:{RED}'))

body = f'<circle cx="104" cy="112" r="62" fill="none" stroke="{INK}" stroke-width="3" stroke-dasharray="10 7"/>'
cols = [EIGHT[0], EIGHT[1], EIGHT[3]]
for i in range(9):
    px, py = pt(104, 112, 62, 270 + i * 40)
    body += f'<circle cx="{px:.0f}" cy="{py:.0f}" r="8" fill="{cols[i % 3]}" stroke="{INK}" stroke-width="2"/>'
for i, a in enumerate([290, 10, 90]):
    px, py = pt(104, 112, 62, a)
    body += f'<g{anim("m-twinkle", i * .5)}><use href="#mstar" x="{px:.0f}" y="{py:.0f}" transform="translate(0 0) scale(1)"/></g>'
body += (buddy(256, 150, 'new', COL['looker'], .9, label_cls='w-s')
         + bubble(190, 24, 122, 62, ['A little from', 'each neighbor!'], (256, 120))
         + t(104, 116, 'MANY SPOTS', 'micro'))
add('01c-many-spots', 'One machine has several spots around the circle. A new machine takes a little from each neighbor.', '#f0e3c6', body)

# ---------- strip 2: three copies ----------

body = mcart(160, 52, 1.2, [('shoe', -8, .7), ('hat', 14, .7)])
for i, x in enumerate([60, 160, 260]):
    body += arrow(f'M{160 + (x - 160) * .25} 84Q{x} 90 {x} 116', RED, 3, '6 5') + house(x, 154, .72) + t(x, 208, f'COPY {i + 1}', 'micro')
body += t(160, 20, 'ONE CART  →  THREE HOUSES', 'micro')
add('02a-three-copies', 'A cart is copied onto three houses in a row.', '#c9d3c0', body)

body = ''
for i, x in enumerate([55, 160, 265]):
    body += house(x, 140, .66)
    if i < 2:
        body += (f'<path d="M{x} 104V52" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
                 f'<path d="M{x} 54h46l-10 14l10 14h-46Z" fill="{GREEN}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
                 + t(x + 20, 74, 'GOT IT', 'micro', style='font-size:11px'))
    else:
        body += f'<g{anim("m-blink")}>' + t(x, 80, '…', 'sfx') + '</g>' + t(x, 54, 'writing', 'b-s')
body += t(160, 208, '2 OF 3 IS ENOUGH', 'sfx-s')
add('02b-two-say-got-it', 'Two of three houses wave a got-it flag; the third is still writing.', '#efd5b7', body)

body = ''
for i, x in enumerate([55, 160, 265]):
    body += house(x, 62, .5, with_cart=False)
    if i < 2:
        body += (arrow(f'M{x + 8} 94Q{(x + 232) / 2} 112 222 140', TEAL, 2.5, '6 5')
                 + f'<g{anim("m-bob", i * .3)}>' + mcart(x - 10, 106, .4) + '</g>')
    else:
        body += t(x, 108, '…', 'w')
body += (buddy(240, 160, 'reader', COL['looker'], .9, label_cls='w-s')
         + bubble(14, 138, 150, 44, ['Who has it?'], (200, 156)) + t(100, 206, '2 replies = done', 'sfx-s'))
add('02c-two-answers', 'A reader asks three houses and two reply with the cart.', '#b8cec0', body)

# ---------- strip 3: neighbors hold your mail ----------

body = (house(96, 116, 1.25, dark=True, label='A', glow=False)
        + f'<path d="M62 150V132M130 150V132" stroke="{INK}" stroke-width="2"/>'
        + f'<g{anim("m-swing")}><rect x="58" y="146" width="76" height="26" rx="3" fill="{RED}" stroke="{INK}" stroke-width="2.5"/>' + t(96, 165, 'CLOSED', 'micro', style='fill:#fff8e3;font-size:13px') + '</g>'
        + '<rect x="78" y="122" width="22" height="26" fill="#1c1b17" stroke="#f6f0df" stroke-width="2"/>'
        + buddy(246, 144, 'you', COL['The'], .9, label_cls='w-s') + mcart(270, 178, .8, [('shoe', -8, .7)])
        + bubble(176, 14, 130, 44, ['Please save it!'], (246, 114)))
add('03a-house-down', 'House A has a dark window and a closed sign. A shopper holds a cart.', '#82acad', body)

body = (house(106, 118, 1.25, label='D')
        + note(236, 70, ['for A'], -8, 78, 'w')
        + mcart(236, 138, 1.3, [('shoe', -8, .7)])
        + arrow('M236 100V104', RED, 3)
        + house(284, 186, .4, dark=True, label=None, with_cart=False, glow=False) + t(284, 212, 'A (away)', 'micro', style='font-size:10px'))
add('03b-note-for-a', 'House D holds a cart copy with a note that says for A.', '#efd5b7', body)

body = (house(64, 124, 1.0, label='D') + house(262, 124, 1.0, label='A') + fence(142, 186, 150)
        + f'<g{anim("m-bob")}>' + mcart(164, 70, 1.0, [('shoe', -8, .7)]) + '</g>'
        + arrow('M104 80Q164 22 224 80', RED, 4)
        + t(164, 196, 'BACK HOME!', 'sfx-s') + t(164, 214, 'like holding your mail', 'micro'))
add('03c-hand-back', 'House D passes the cart copy over the fence to House A.', '#c9d3c0', body)

# ---------- strip 4: sticky notes ----------

body = (house(62, 128, 1.0, label='X') + arrow('M108 120Q140 90 168 100', INK, 3)
        + mcart(204, 130, 1.8, [('shoe', -8, .7), ('hat', 14, .7)])
        + f'<g{anim("m-wiggle")}>' + note(244, 62, ['X · 1'], 8, 70, 'w') + '</g>'
        + t(160, 208, 'STICK ON A NOTE', 'sfx-s'))
add('04a-sticky-note', 'A house sticks a note reading X 1 on a cart.', '#f0e3c6', body)

body = (mcart(80, 130, 1.5, [('shoe', -8, .7)]) + mcart(240, 130, 1.5, [('hat', 14, .7)])
        + note(84, 54, ['X 2'], -6, 70, 'w') + note(244, 54, ['X 1', 'Y 1'], 6, 70, 'w')
        + t(160, 130, '≠', 'sfx') + t(80, 194, 'COPY ONE', 'micro') + t(240, 194, 'COPY TWO', 'micro')
        + t(160, 212, 'same cart, different notes', 'b-s'))
add('04b-two-versions', 'Two copies of one cart carry different sticky notes.', '#efd5b7', body)


def chips(x, y, labels, color=GOLD):
    return ''.join(f'<rect x="{x + i * 34}" y="{y}" width="30" height="24" fill="{color}" stroke="{INK}" stroke-width="2"/>' + t(x + i * 34 + 15, y + 18, lb, 'b-s')
                   for i, lb in enumerate(labels))


fork = (f'<path d="M0 22V6M0 6L-12 -10M0 6L12 -10" fill="none" stroke="{RED}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
body = (chips(14, 34, ['X1', 'X2']) + t(88, 52, 'vs', 'b-s') + chips(108, 34, ['X1', 'X2', 'X3'])
        + check(236, 46, 14) + t(256, 51, 'UPDATE', 'micro', 'start', 'font-size:10px')
        + t(160, 100, '↑ just newer: drop the old one', 'b-s', style='font-size:14px')
        + chips(14, 128, ['X1', 'X2']) + t(88, 146, 'vs', 'b-s') + chips(108, 128, ['X1', 'Y1'], '#f3c39a')
        + f'<g transform="translate(262 136)">{fork}</g>' + t(262, 168, 'BRANCH', 'micro', style='font-size:10px')
        + t(160, 206, '↑ forked: keep both', 'b-s', style='font-size:14px'))
add('04c-compare-notes', 'Two sticky-note stacks are compared side by side. A tick for update, a fork for branch.', '#c9d3c0', body)

# ---------- strip 5: merge ----------

body = (mcart(80, 112, 1.6, [('shoe', 0, 1.3)]) + mcart(240, 112, 1.6, [('hat', 6, 1.3)])
        + t(80, 176, 'CART 1', 'micro') + t(240, 176, 'CART 2', 'micro') + t(160, 120, 'and', 'w')
        + t(160, 208, 'Neither is wrong.', 'b'))
add('05a-sneaker-hat', 'Cart one holds a sneaker. Cart two holds a hat.', '#b8cec0', body)

body = (mcart(56, 46, .8, [('shoe', 0, 1)]) + mcart(264, 46, .8, [('hat', 6, 1)])
        + arrow('M70 78Q110 110 138 124', RED, 3.5, '7 5') + arrow('M250 78Q210 110 182 124', RED, 3.5, '7 5')
        + mcart(160, 150, 1.6, [('shoe', -10, 1), ('hat', 16, 1)])
        + t(160, 40, 'MERGE!', 'sfx') + t(160, 210, 'sneaker + hat', 'b-s'))
add('05b-merge', 'The two carts pour into one cart with a sneaker and a hat.', '#efd5b7', body)

body = (buddy(52, 160, 'you', COL['The'], .9, label_cls='w-s')
        + bubble(12, 14, 144, 44, ['I removed that!'], (52, 130))
        + mcart(200, 152, 1.5, [('shoe', -10, 1), ('hat', 16, 1)])
        + f'<g{anim("m-hop")}>' + scarf(260, 66, 1.5) + f'<path d="M232 50L288 84" stroke="{RED}" stroke-width="4" stroke-linecap="round"/></g>'
        + arrow('M262 96Q272 118 240 132', RED, 3, '6 5') + t(264, 40, 'BOING!', 'sfx-s'))
add('05c-item-returns', 'A crossed-out scarf pops back into the merged cart.', '#c9d3c0', body)

# ---------- strip 6: gossip and fingerprints ----------

body = (house(64, 128, .95) + house(196, 128, .95) + fence(116, 142, 140)
        + bubble(10, 10, 112, 40, ['A left!'], (64, 78)) + bubble(150, 10, 124, 40, ['E joined!'], (196, 78))
        + house(284, 150, .5, with_cart=False, glow=False) + f'<g{anim("m-blink")}>' + t(284, 100, '…', 'w') + '</g>' + t(284, 192, 'WAITING', 'micro')
        + t(130, 208, 'GOSSIP', 'sfx-s'))
add('06a-gossip', 'Two houses chat over a fence while a third waits its turn.', '#efd5b7', body)


def shelf(x, y, w):
    out = f'<rect x="{x}" y="{y}" width="{w}" height="10" fill="{WOOD}" stroke="{INK}" stroke-width="2.5"/><path d="M{x + 8} {y + 10}v14M{x + w - 8} {y + 10}v14" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'
    for i in range(3):
        out += mcart(x + 24 + i * 34, y - 14, .42)
    return out


body = (shelf(16, 130, 120) + shelf(184, 130, 120)
        + fingerprint(76, 70, 24) + fingerprint(244, 70, 24)
        + f'<g{anim("m-pulse")}>' + t(160, 84, '=', 'sfx') + '</g>'
        + t(160, 190, 'same stamp', 'b') + t(160, 210, 'same shelf', 'b'))
add('06b-fingerprint', 'Two shelves each show a single fingerprint stamp; the stamps match.', '#b8cec0', body)

lines = ''.join(f'<path d="M{a} {b}L{c} {d}" stroke="{INK}" stroke-width="2.5"/>' for a, b, c, d in
                [(160, 44, 90, 84), (160, 44, 230, 84), (90, 96, 50, 126), (90, 96, 130, 126), (230, 96, 190, 126), (230, 96, 270, 126)])
nodes = ''
for x, y, bad, r in [(160, 32, 1, 14), (90, 90, 0, 12), (230, 90, 1, 12), (50, 140, 0, 11), (130, 140, 0, 11), (190, 140, 1, 11), (270, 140, 0, 11)]:
    nodes += fingerprint(x, y, r, RED if bad else TEAL)
    nodes += f'<circle cx="{x + r - 3}" cy="{y - r + 3}" r="4" fill="{RED if bad else GREEN}" stroke="{INK}" stroke-width="1.5"/>'
body = (lines + nodes + arrow('M190 162V178', RED, 3.5) + mcart(190, 196, .55, [('hat', 14, 1)])
        + t(222, 200, 'copy only this', 'b-s', 'start', 'font-size:14px') + t(60, 196, 'halve, halve…', 'b-s', style='font-size:14px'))
add('06c-find-the-odd-one', 'A tree of fingerprints narrows down to one mismatched cart.', '#f0e3c6', body)

# ---------- story chapter panels (440x215) ----------

body = (f'<rect x="60" y="150" width="320" height="16" fill="{WOOD}" stroke="{INK}" stroke-width="3"/>'
        f'<path d="M78 166v34M362 166v34" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>')
for row, n in enumerate([5, 4, 3, 2]):
    for k in range(n):
        body += f'<g{anim("m-wobble", round((row + k) * .15, 2)) if row == 3 else ""}>' + mcart(220 + (k - (n - 1) / 2) * 52, 128 - row * 34, .72) + '</g>'
body += (f'<path d="M222 150L214 158L228 162L218 170" fill="none" stroke="{RED}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
         + t(70, 56, 'CRACK!', 'sfx', 'start') + t(380, 56, 'ONE SHELF', 'micro', 'end') + t(220, 208, 'every cart on the same spot', 'b-s'))
story('01-one-shelf', 'One shelf holds a pile of carts. A crack runs through the shelf.', '#efd5b7', body)

cx, cy, R = 250, 108, 78
dx, dy = pt(cx, cy, R, 225)
body = (ring_with_houses(cx, cy, R, .5) + arrow(arc(cx, cy, R, 225, 254), RED, 5)
        + f'<circle cx="{dx:.0f}" cy="{dy:.0f}" r="8" fill="{RED}" stroke="{INK}" stroke-width="2.5"/>'
        + f'<g{anim("m-feed")}><path d="M34 72l12-12h56l0 32h-56z" fill="{GOLD}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/><circle cx="46" cy="76" r="3" fill="{INK}"/>' + t(76, 82, 'cart-42', 'micro') + '</g>'
        + f'<path d="M104 80Q150 70 {dx - 8:.0f} {dy - 4:.0f}" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="6 5"/>'
        + t(cx, cy + 4, 'CLOCKWISE', 'w-s') + t(60, 150, 'name → spot', 'b-s') + t(60, 172, 'walk to the house', 'b-s'))
story('02-ring-of-houses', 'Houses sit around a circle. A cart tag lands on the circle and an arrow walks clockwise to the nearest house.', '#b8cec0', body)

body = (mcart(80, 54, 1.2, [('shoe', -8, .8)]) + mcart(80, 158, 1.2, [('hat', 14, .8)])
        + arrow('M130 58Q220 60 262 98', RED, 4, '8 6') + arrow('M130 154Q220 150 262 118', RED, 4, '8 6')
        + mcart(340, 112, 2.0, [('shoe', -12, 1.1), ('hat', 16, 1.1)])
        + t(190, 108, 'MERGE', 'sfx-s') + t(340, 192, 'keep both', 'b-s') + t(80, 26, 'EDIT 1', 'micro') + t(80, 118, 'EDIT 2', 'micro'))
story('03-merge-the-carts', 'Two carts, one with a sneaker and one with a hat, pour into a single cart holding both.', '#efd5b7', body)

body = (t(40, 20, 'VERSIONS', 'micro', 'start'))
for i, (lab, w, col) in enumerate([('1', 330, TEAL), ('2', 3, RED), ('3', 2, RED), ('4', 1.5, RED)]):
    y = 34 + i * 40
    body += (t(36, y + 22, lab, 'w') + f'<rect x="60" y="{y}" width="340" height="28" fill="#fff8e3" stroke="{INK}" stroke-width="1.5" opacity=".7"/>'
             f'<rect{" class=\"m-meter\"" if i == 0 else ""} x="60" y="{y}" width="{w}" height="28" fill="{col}" stroke="{INK}" stroke-width="2"/>')
body += (t(230, 54, '99.94%', 'w', style='fill:#fff8e3') + t(80, 98, 'tiny', 'b-s', 'start') + t(80, 138, 'tiny', 'b-s', 'start')
         + t(80, 178, 'tiny', 'b-s', 'start') + t(230, 207, 'almost every cart: one version', 'b-s'))
story('04-one-version', 'A big bar for one version of the cart, 99.94 percent of requests, and tiny marks for two, three and four versions.', '#c9d3c0', body)

# ---------- fact icons (160x100) ----------

body = ''.join(house(32 + i * 48, 52, .32, with_cart=False, glow=False) for i in range(3))
body += check(32, 22, 8) + check(80, 22, 8) + f'<circle cx="128" cy="22" r="8" fill="none" stroke="{INK}" stroke-width="2" stroke-dasharray="3 3"/>'
body += t(80, 92, '3 · 2 · 2', 'w')
icon('copies-3-2-2', 'Three houses, two of them ticked: three copies, two answers.', body)

body = (f'<circle cx="62" cy="54" r="30" fill="#fff8e3" stroke="{INK}" stroke-width="3"/><rect x="55" y="14" width="14" height="8" fill="{INK}"/>'
        f'<path d="M62 54V32" stroke="{INK}" stroke-width="3" stroke-linecap="round"/><g class="m-spin-slow"><path d="M62 54h18" stroke="{RED}" stroke-width="3" stroke-linecap="round"/></g>'
        f'<path d="M62 54L62 24A30 30 0 0 1 90 44Z" fill="{GREEN}" opacity=".6"/>'
        + t(124, 56, '300', 'w') + t(124, 74, 'ms', 'w-s') + t(80, 94, '99.9% of requests', 'micro', style='font-size:9px'))
icon('promise-300ms', 'A stopwatch with a green slice and the number 300 ms.', body)

body = (''.join(f'<path d="M{10 + k * 6} {40 + k * 12}h22" stroke="{INK}" stroke-width="2" stroke-linecap="round" opacity=".5"/>' for k in range(3))
        + f'<g{anim("m-bob")}>' + mcart(70, 48, 1.1, [('shoe', -8, .8), ('hat', 14, .8)]) + '</g>'
        + t(124, 58, '3M+', 'w') + t(80, 92, 'CHECKOUTS IN A DAY', 'micro', style='font-size:10px'))
icon('checkouts', 'A shopping cart rolling past with the number 3 million plus.', body)

hs = [58, 46, 30, 18, 10, 6, 4, 3, 2.5, 2]
body = ''.join(f'<rect x="{12 + i * 13}" y="{78 - h}" width="11" height="{h}" fill="{RED if i >= 7 else TEAL}" stroke="{INK}" stroke-width="1.5"/>' for i, h in enumerate(hs))
body += f'<path d="M10 80H146" stroke="{INK}" stroke-width="2"/>' + t(118, 28, '1 in 1,000', 'micro', style='font-size:10px;fill:#a13324') + t(80, 94, 'THE SLOW TAIL', 'micro', style='font-size:10px')
icon('slowest-tail', 'A bar chart with a long thin tail on the right in red.', body)

body = (mcart(52, 50, 1.3, [('shoe', -8, .8), ('hat', 14, .8)]) + check(84, 24, 11)
        + f'<g opacity=".4">' + mcart(114, 36, .45) + mcart(136, 36, .45) + mcart(125, 62, .45) + '</g>'
        + t(122, 84, '1', 'sfx-s') + t(60, 92, 'ONE VERSION', 'micro'))
icon('one-version', 'One big ticked cart with a few faint ghost carts beside it.', body)

body = ''
for i in range(8):
    x, y = 24 + (i % 4) * 36, 28 + (i // 4) * 28
    body += (f'<rect x="{x - 12}" y="{y - 8}" width="24" height="16" fill="#fff8e3" stroke="{INK}" stroke-width="1.5"/><path d="M{x - 12} {y - 8}L{x} {y + 2}L{x + 12} {y - 8}" fill="none" stroke="{INK}" stroke-width="1.5"/>'
             + check(x + 10, y + 8, 5))
body += t(80, 92, '99.9995% answered', 'micro', style='font-size:10px')
icon('answered', 'A grid of mailed envelopes, each one ticked as answered.', body)


if __name__ == '__main__':
    write(OUT, 'fire.svg', standalone('0 0 600 340', plate('#efd5b7', 'PLATE 01 / FIRE',
          fire_body, 'The machine is on fire. Your cart does not care.'),
          'A server box with a small flame and smoke. A shopping cart on a screen next to it still shows a sneaker and a hat.', defs=DEFS))
    write(OUT, 'cart-safe.svg', standalone('0 0 600 340', plate('#b8cec0', 'PLATE 02 / CART-SAFE', safe_body, 'Three copies on a ring. One house goes dark. Nobody notices.'),
          'Three houses on a ring each hold a copy of the same cart. One house is dark; the other two glow.', defs=DEFS))
    print(f'wrote 2 lead plates to {OUT}')
    for name, vb, alt, body in PANELS + ICONS:
        write(OUT_ROOT, name, standalone(vb, body, alt, defs=DEFS))
    print(f'wrote {len(PANELS)} comic/story panels and {len(ICONS)} icons to {OUT_ROOT}')
