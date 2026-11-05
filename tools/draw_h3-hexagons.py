"""Draws the media for "A world covered in honeycomb" (Uber's H3 hexagonal index).

Run from the repo root:  python3 tools/draw_h3-hexagons.py
Writes standalone SVG files to public/media/h3-hexagons/{lead,story,comic,facts}/.
Captions, alt text and which file goes where live in public/data/papers/h3-hexagons.json.
All drawings are original. No image from the source post is copied.
"""
import math
from pathlib import Path

from media_kit import COMIC_CSS, COL, INK, RED, anim, bubble, buddy, standalone, t, write

OUT = Path(__file__).resolve().parent.parent / 'public' / 'media' / 'h3-hexagons'
CREAM = '#f6f0df'
HEX = ['#efae78', '#f7d79b', '#a2c2a7', '#c3b2d8', '#82acad', '#f0e3c6']
ROAD = '#fff8e3'
LAND = '#e6d3b0'
WATER = '#9ab9b6'
CAR_A = '#c86f3f'
CAR_B = '#377675'
RIDER = COL['looker']
SQRT3 = math.sqrt(3)

# Only the H3 drawings add their own rules. Shared animations come from COMIC_CSS.
H3_CSS = """
.h-sq{opacity:0;animation:h-sq 10s ease-in-out infinite}
.h-hex{animation:h-hex 10s ease-in-out infinite}
.h-big{opacity:0;transform-box:fill-box;transform-origin:center;animation:h-big 8s ease-in-out infinite}
.h-kids{transform-box:fill-box;transform-origin:center;animation:h-kids 8s ease-in-out infinite}
@keyframes h-sq{0%,45%{opacity:1}55%,90%{opacity:0}100%{opacity:1}}
@keyframes h-hex{0%,45%{opacity:0}55%,90%{opacity:1}100%{opacity:0}}
@keyframes h-big{0%,35%{opacity:1;transform:scale(1)}50%,85%{opacity:0;transform:scale(1.35)}100%{opacity:1;transform:scale(1)}}
@keyframes h-kids{0%,35%{opacity:0;transform:scale(.4)}50%,85%{opacity:1;transform:scale(1)}100%{opacity:0;transform:scale(.4)}}
"""
CSS = COMIC_CSS + H3_CSS

ENTRIES = []   # (relative path, title, viewBox, body)


def add(rel, title, vb, body):
    ENTRIES.append((rel, title, vb, body))


# ---------- drawing helpers ----------

def hexagon(cx, cy, r, fill='none', sw=2, fo=1, stroke=INK, extra=''):
    pts = ' '.join(f'{cx + r * math.cos(math.radians(-90 + 60 * k)):.1f},{cy + r * math.sin(math.radians(-90 + 60 * k)):.1f}'
                   for k in range(6))
    return (f'<polygon points="{pts}" fill="{fill}" fill-opacity="{fo}" stroke="{stroke}" stroke-width="{sw}"'
            f' stroke-linejoin="round"{extra}/>')


def pent(cx, cy, r, fill, sw=2):
    pts = ' '.join(f'{cx + r * math.cos(math.radians(-90 + 72 * k)):.1f},{cy + r * math.sin(math.radians(-90 + 72 * k)):.1f}'
                   for k in range(5))
    return f'<polygon points="{pts}" fill="{fill}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>'


def ring_offsets(r):
    """Centre offsets of the six neighbours of a pointy-top hexagon of radius r (all equally far)."""
    w = SQRT3 * r
    return [(w, 0), (w / 2, 1.5 * r), (-w / 2, 1.5 * r), (-w, 0), (-w / 2, -1.5 * r), (w / 2, -1.5 * r)]


def honeycomb(x0, y0, r, cols, rows, fo=.45, sw=1.8):
    w = SQRT3 * r
    out = ''
    for row in range(rows):
        for col in range(cols):
            cx = x0 + col * w + (row % 2) * w / 2
            cy = y0 + row * 1.5 * r
            out += hexagon(cx, cy, r, HEX[(col + 2 * row) % len(HEX)], sw, fo)
    return out


def cluster7(cx, cy, r, fo=.85, sw=1.6):
    """One cell and its six neighbours: the 'seven smaller cells' picture."""
    out = hexagon(cx, cy, r, HEX[0], sw, fo)
    for k, (dx, dy) in enumerate(ring_offsets(r)):
        out += hexagon(cx + dx, cy + dy, r, HEX[(k + 1) % len(HEX)], sw, fo)
    return out


def squares(x0, y0, s, cols, rows, fo=.35):
    return ''.join(f'<rect x="{x0 + c * s}" y="{y0 + q * s}" width="{s}" height="{s}" fill="#fff8e3" fill-opacity="{fo}"'
                   f' stroke="{INK}" stroke-width="1.5"/>' for q in range(rows) for c in range(cols))


def map_base(w, h, ys, xs, river):
    out = f'<rect width="{w}" height="{h}" fill="{LAND}"/>'
    out += f'<path d="{river}" fill="none" stroke="{WATER}" stroke-width="22"/>'
    out += ''.join(f'<path d="M0 {y}H{w}" stroke="{ROAD}" stroke-width="10"/>' for y in ys)
    out += ''.join(f'<path d="M{x} 0V{h}" stroke="{ROAD}" stroke-width="10"/>' for x in xs)
    return out


def car(x, y, s=1, color=CAR_A):
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2" stroke-linejoin="round">'
            f'<path d="M-22 4Q-22 -2 -16 -3L-9 -10Q-7 -12 -3 -12H9Q13 -12 15 -9L19 -3Q22 -2 22 4Z" fill="{color}"/>'
            f'<rect x="-6" y="-9" width="12" height="5" fill="#fff8e3" stroke="none"/>'
            f'<circle cx="-12" cy="8" r="5" fill="{INK}"/><circle cx="12" cy="8" r="5" fill="{INK}"/></g>')


def rider(x, y, s=1, color=RIDER, cls=''):
    return buddy(x, y, '', color, s, cls)


def label(cx, y, s, w=None):
    """Cream sticker with a short micro label, centred on cx."""
    w = w or 12 + 7.6 * len(s)
    return (f'<rect x="{cx - w / 2:.1f}" y="{y}" width="{w:.1f}" height="22" rx="5" fill="#fff8e3" stroke="{INK}" stroke-width="1.5"/>'
            + t(cx, y + 15, s, 'micro'))


def label_w(cx, y, s, w=None):
    """Cream sticker with a bold serif label (readable at 15px)."""
    w = w or 14 + 9 * len(s)
    return (f'<rect x="{cx - w / 2:.1f}" y="{y}" width="{w:.1f}" height="24" rx="6" fill="#fff8e3" stroke="{INK}" stroke-width="1.5"/>'
            + t(cx, y + 17, s, 'w-s'))


def arrow(x1, x2, y, color=RED, cls=''):
    c = f' class="{cls}"' if cls else ''
    return (f'<path{c} d="M{x1} {y}H{x2 - 9}" stroke="{color}" stroke-width="3" fill="none" stroke-dasharray="6 5"/>'
            f'<polygon points="{x2},{y} {x2 - 11},{y - 6} {x2 - 11},{y + 6}" fill="{color}"/>')


def canvas(w, h, bg, body):
    return f'<rect width="{w}" height="{h}" fill="{bg}"/><rect width="{w}" height="{h}" fill="url(#dots)" opacity=".22"/>' + body


# =====================================================================
# LEAD (600 x 340)
# =====================================================================

# Lead plate: the same city, drawn with squares, then with a honeycomb. Slow flip; resting state = honeycomb.
_HX, _HY = -20 + 6 * SQRT3 * 30 + (3 % 2) * SQRT3 * 30 / 2, -10 + 3 * 45
_lead_map = map_base(600, 340, [40, 110, 180, 250, 320], [60, 150, 240, 330, 420, 510],
                     'M0 232C120 196 200 282 320 244S480 196 600 252')
_lead_sq = '<g class="h-sq">' + squares(0, 0, 40, 16, 9) + '</g>'
_lead_hex = ('<g class="h-hex">' + honeycomb(-20, -10, 30, 13, 9)
             + hexagon(_HX, _HY, 30, 'none', 3.5, 1, RED)
             + label(_HX, _HY - 58, 'SAME CELL', 96) + '</g>')
_lead_people = car(_HX + 10, _HY + 8, .55, CAR_A) + rider(_HX - 13, _HY + 4, .42)
add('lead/honeycomb-map.svg',
    'A city map that flips from a square grid to a honeycomb. A rider and a car sit in one hexagon, tagged with the same cell.',
    '0 0 600 340', _lead_map + _lead_sq + _lead_hex + _lead_people)

# Zoom: one big cell fades out and seven smaller cells take its place. Resting state = the seven.
_zoom_body = (
    '<rect width="600" height="340" fill="' + CREAM + '"/>'
    + '<g class="h-big">' + hexagon(300, 170, 120, '#f7d79b', 3, .6) + label(300, 16, 'ONE CELL', 110) + '</g>'
    + '<g class="h-kids">' + cluster7(300, 170, 45, .85, 2.2) + label(300, 302, 'ABOUT 7 INSIDE', 170) + '</g>'
)
add('lead/zoom-in.svg',
    'One big hexagon zooms in and becomes seven smaller hexagons, like a magnifying glass on honeycomb.',
    '0 0 600 340', _zoom_body)


# =====================================================================
# STORY (440 x 215)
# =====================================================================

# Chapter 1: the nearest car. Checking every car gets slower as the city grows (illustration).
_town = ''
for (x, y), c in zip([(44, 60), (172, 64), (116, 104)], [CAR_A, CAR_B, CAR_A]):
    _town += f'<path class="m-dash" d="M110 150L{x} {y + 10}" fill="none" stroke="{RED}" stroke-width="2"/>'
    _town += car(x, y, .7, c)
_city = ''
for i, (x, y) in enumerate([(x, y) for y in (46, 92, 132) for x in (252, 296, 340, 384)]):
    _city += f'<path class="m-dash" d="M330 176L{x} {y + 10}" fill="none" stroke="{RED}" stroke-width="1.5" style="animation-delay:{i * .1:.1f}s"/>'
    _city += car(x, y, .6, CAR_B if i % 2 else CAR_A)
_nearest = (
    canvas(440, 215, CREAM, '')
    + f'<path d="M220 14V200" stroke="{INK}" stroke-width="1.5" stroke-dasharray="4 5" opacity=".5"/>'
    + _town + rider(110, 168, .6)
    + _city + rider(330, 176, .6)
    + label_w(110, 186, '3 to check', 120)
    + label_w(330, 186, '12 to check', 120)
)
add('story/01-nearest-driver.svg',
    'A rider checks three cars in a small town, then twelve cars in a big city. Checking each car takes longer as the city grows.',
    '0 0 440 215', _nearest)

# Chapter 2: lay a honeycomb over the map.
_tile_map = map_base(440, 215, [40, 120, 190], [70, 170, 280, 380],
                     'M0 150C90 120 170 200 260 160S380 120 440 170')
_tile = (_tile_map + honeycomb(-10, -8, 22, 13, 8, .42, 1.6)
         + label(95, 10, 'EVERY SPOT, ONE CELL', 170)
         + rider(199, 92, .45, RIDER, 'm-hop'))
add('story/02-tile-the-world.svg',
    'A city map with a honeycomb laid over it. Every spot falls into one hexagon, and a rider sits in one of them.',
    '0 0 440 215', _tile)

# Chapter 3: zoom in, each cell splits into about seven.
_split = (
    canvas(440, 215, CREAM, '')
    + hexagon(80, 110, 62, HEX[1], 3, .8)
    + arrow(146, 172, 110) + t(159, 66, 'zoom in', 'micro')
    + cluster7(250, 110, 26, .85, 2) + hexagon(250, 110, 26, 'none', 3.5, 1, RED)
    + arrow(326, 352, 110) + t(340, 66, 'zoom in', 'micro')
    + cluster7(388, 110, 10, .9, 1.4)
    + label(80, 186, 'ONE CELL', 96) + label(250, 186, 'SEVEN INSIDE', 124) + label(388, 186, 'SPLIT AGAIN', 110)
)
add('story/03-zoom-splits.svg',
    'One big hexagon, zoomed in: it splits into seven smaller hexagons. One of those splits again into seven tiny ones.',
    '0 0 440 215', _split)

# Chapter 4: evidence. Two lists of cells for the same map: many small cells, and a compact list of fewer, bigger cells.
# Drawn as a schematic (not to scale). The compact list shows fewer, larger cells than the full list.
_full = honeycomb(120, 36, 7, 12, 2, .6, 1.2)
_compact = hexagon(150, 140, 20, HEX[2], 2.2, .9) + hexagon(200, 140, 20, HEX[2], 2.2, .9)
_evidence = (
    canvas(440, 215, CREAM, '')
    + t(24, 72, 'FULL LIST', 'micro', 'start') + _full
    + t(24, 146, 'COMPACT', 'micro', 'start') + _compact
    + label(340, 124, 'SAME MAP', 110) + label(340, 160, 'TWO LISTS', 110)
    + label(220, 186, 'FEWER, BIGGER CELLS', 180)
)
add('story/04-evidence.svg',
    'Two lists of hexagons for the same map: a full list of many small cells, and a compact list with fewer, bigger cells.',
    '0 0 440 215', _evidence)


# =====================================================================
# COMIC PANELS (320 x 220)
# =====================================================================

# Strip 1: why hexagons, not squares?
_sq_body = ''
for dx in (-1, 0, 1):
    for dy in (-1, 0, 1):
        if dx == 0 and dy == 0:
            fill, stroke, sw = '#fff8e3', RED, 3
        elif dx == 0 or dy == 0:
            fill, stroke, sw = '#a2c2a7', INK, 2
        else:
            fill, stroke, sw = '#f7d79b', INK, 2
        _sq_body += (f'<rect x="{160 + dx * 40 - 20}" y="{108 + dy * 40 - 20}" width="40" height="40" fill="{fill}"'
                     f' stroke="{stroke}" stroke-width="{sw}"/>')
add('comic/01a-squares.svg',
    'Nine squares. The four sides are green and the four corners are yellow. A corner neighbor sits further away.',
    '0 0 320 220', _sq_body + t(160, 206, 'GREEN = SIDE   YELLOW = CORNER', 'micro'))

add('comic/01b-hexagons.svg',
    'One hexagon in the middle with six green neighbors, all the same distance away.',
    '0 0 320 220',
    hexagon(160, 112, 30, '#fff8e3', 3, 1, RED)
    + ''.join(hexagon(160 + dx, 112 + dy, 30, '#a2c2a7', 2, .9) for dx, dy in ring_offsets(30))
    + t(160, 206, 'ALL SIX: SAME DISTANCE', 'micro'))

_mini = 95, 118
add('comic/01c-one-distance.svg',
    'A small honeycomb with arrows of equal length to each neighbor. A looker says: same distance, every neighbor.',
    '0 0 320 220',
    hexagon(_mini[0], _mini[1], 20, HEX[0], 2, .5)
    + ''.join(f'<path class="m-dash" d="M{_mini[0]} {_mini[1]}L{_mini[0] + dx:.1f} {_mini[1] + dy:.1f}" stroke="{INK}" stroke-width="1.6"/>'
              for dx, dy in ring_offsets(20))
    + ''.join(hexagon(_mini[0] + dx, _mini[1] + dy, 20, '#a2c2a7', 2, .9) for dx, dy in ring_offsets(20))
    + rider(240, 172, .8)
    + bubble(150, 14, 160, 52, ['Same distance,', 'every neighbor!'], (240, 142))
    + t(160, 206, 'FAIR CHECK, EVERY WAY', 'micro'))

# Strip 2: zoom in, it splits in seven.
add('comic/02a-one-cell.svg',
    'One big hexagon cell. A looker asks what is inside it.',
    '0 0 320 220',
    hexagon(180, 122, 52, '#f7d79b', 3, .9)
    + label(180, 112, 'CELL', 66)
    + bubble(16, 12, 190, 56, ['What’s inside', 'this cell?'], (74, 170))
    + rider(74, 196, .6, COL['looker']))

add('comic/02b-split-seven.svg',
    'A faded big hexagon becomes seven smaller hexagons after an arrow.',
    '0 0 320 220',
    hexagon(96, 118, 44, 'none', 2.5, 1, INK, ' stroke-dasharray="6 5"')
    + arrow(146, 178, 118)
    + cluster7(236, 118, 19, .85, 1.8)
    + label(160, 184, 'ONE → SEVEN', 120))

add('comic/02c-zoom-again.svg',
    'A magnifying glass shows seven tiny hexagons inside one small cell. A looker says: zoom in again.',
    '0 0 320 220',
    '<circle cx="110" cy="100" r="54" fill="#fff8e3" fill-opacity=".55" stroke="none"/>'
    + cluster7(110, 100, 12, .9, 1.4)
    + f'<path d="M150 140L184 178" stroke="{INK}" stroke-width="10" stroke-linecap="round"/>'
    + f'<circle cx="110" cy="100" r="54" fill="none" stroke="{INK}" stroke-width="4"/>'
    + bubble(190, 22, 110, 54, ['Zoom in', 'again!'], (258, 140))
    + rider(258, 178, .7, COL['looker'])
    + label(160, 194, 'EVERY SMALL CELL SPLITS', 196))

# Strip 3: finding a ride.
_ring_centre = (160, 96)
_ring = ''.join(f'<g{anim("m-pulse", round(i * .3, 1))}>' + hexagon(160 + dx, 96 + dy, 26, '#a2c2a7', 2, .9) + '</g>'
                for i, (dx, dy) in enumerate(ring_offsets(26)))
add('comic/03a-same-cell.svg',
    'A rider and a car stand in the same hexagon, which is tagged with one cell ID.',
    '0 0 320 220',
    honeycomb(66, 44, 24, 4, 3, .45)
    + hexagon(128.4, 80, 24, '#fff8e3', 3.5, 1, RED)
    + rider(118, 84, .36) + car(140, 88, .4, CAR_A)
    + label(160, 166, 'SAME CELL, SAME ID', 180))

add('comic/03b-ring-search.svg',
    'A rider stands in an empty hexagon. Its six neighbors pulse one by one, and a car is in one of them.',
    '0 0 320 220',
    hexagon(160, 96, 26, '#fff8e3', 3, 1, RED) + _ring
    + car(182.5, 136, .4, CAR_B)
    + rider(160, 100, .4)
    + label(160, 182, 'NOT HERE? CHECK THE RING', 210))

add('comic/03c-found.svg',
    'A rider waves at a car in a neighboring hexagon. A bubble says: found one, and the car goes VROOM.',
    '0 0 320 220',
    f'<g{anim("m-twinkle", 0)}><use href="#mstar" x="50" y="48"/></g>'
    + f'<g{anim("m-twinkle", .8)}><use href="#mstar" x="276" y="62"/></g>'
    + f'<g{anim("m-twinkle", 1.6)}><use href="#mstar" x="284" y="150"/></g>'
    + hexagon(222, 140, 40, '#a2c2a7', 2, .6)
    + car(222, 140, 1.1, CAR_A)
    + rider(96, 150, .9, COL['The'], 'm-hop')
    + bubble(146, 18, 150, 46, ['Found one!'], (222, 108))
    + t(160, 206, 'VROOM!', 'sfx'))


# =====================================================================
# FACT ICONS (160 x 100)
# =====================================================================

add('facts/resolutions.svg', 'One big hexagon next to seven small ones: levels of detail.', '0 0 160 100',
    hexagon(40, 50, 26, HEX[1], 2.5, .9) + cluster7(120, 50, 10, .9, 1.4))

add('facts/one-seventh.svg', 'A big hexagon and seven smaller hexagons that together take up about the same space.', '0 0 160 100',
    hexagon(40, 50, 30, HEX[1], 2.5, .9) + cluster7(120, 50, 11.3, .9, 1.4))

add('facts/base-cells.svg', 'A globe covered in a honeycomb of hexagons.', '0 0 160 100',
    '<clipPath id="h-globe"><circle cx="80" cy="50" r="42"/></clipPath>'
    + f'<circle cx="80" cy="50" r="42" fill="#82acad"/>'
    + '<g clip-path="url(#h-globe)">' + honeycomb(44, 18, 9, 7, 7, .85, 1.2) + '</g>'
    + f'<circle cx="80" cy="50" r="42" fill="none" stroke="{INK}" stroke-width="2.5"/>')

add('facts/pentagons.svg', 'A grid of twelve pentagons among the hexagons.', '0 0 160 100',
    ''.join(pent(24 + c * 34, 24 + q * 26, 10, HEX[(c + q) % len(HEX)]) for q in range(3) for c in range(4)))

add('facts/index-bits.svg', 'A square of 64 small boxes, some filled in. Each box is one bit of a cell ID.', '0 0 160 100',
    ''.join(f'<rect x="{40 + (i % 8) * 10}" y="{10 + (i // 8) * 10}" width="9" height="9" fill="'
            f'{"#377675" if (i * 37 + 11) % 5 < 2 else "#fff8e3"}" stroke="{INK}" stroke-width="1"/>'
            for i in range(64)))


if __name__ == '__main__':
    for rel, title, vb, body in ENTRIES:
        write(OUT, rel, standalone(vb, body, title, css=CSS))
    print(f'wrote {len(ENTRIES)} SVGs to {OUT}')
