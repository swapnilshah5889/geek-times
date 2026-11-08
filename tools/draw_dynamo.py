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
                   for dx, dy, r in [(0, 0, 14), (14, 26, 18), (-4, 56, 22), (18, 90, 16)])


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
fire_body = (smoke(fx + 70, fy - 6)
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
cx, cy, R = 300, 150, 92
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
             + t(cx, cy + 6, 'ONE CART', 'w-s') + t(cx, cy + 24, 'THREE COPIES', 'micro')
             + f'<g{anim("m-wiggle")}>' + t(500, 150, 'NO PROBLEM!', 'sfx-s') + '</g>')

if __name__ == '__main__':
    write(OUT, 'fire.svg', standalone('0 0 600 340', plate('#efd5b7', 'PLATE 01 / FIRE',
          fire_body, 'The machine is on fire. Your cart does not care.'),
          'A server box with a small flame and smoke. A shopping cart on a screen next to it still shows a sneaker and a hat.', defs=DEFS))
    write(OUT, 'cart-safe.svg', standalone('0 0 600 340', plate('#b8cec0', 'PLATE 02 / CART-SAFE', safe_body, 'Three copies on a ring. One house goes dark. Nobody notices.'),
          'Three houses on a ring each hold a copy of the same cart. One house is dark; the other two glow.', defs=DEFS))
    print(f'wrote 2 lead plates to {OUT}')
