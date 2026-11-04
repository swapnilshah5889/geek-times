"""Draws the lead plates, story panels, comic panels and fact icons for the scaling story
("Why a bigger deer breaks", from arXiv 2408.04070).

Run from the repo root:  python3 tools/draw_scaling.py
Writes standalone SVG files to public/media/size-shapes-life/{lead,story,comic,facts}/.
Words, captions and which file goes where live in public/data/papers/size-shapes-life.json.
"""
import math
from pathlib import Path

from media_kit import COMIC_CSS, INK, RED, anim, bubble, panel, standalone, t, write

OUT = Path(__file__).resolve().parent.parent / 'public' / 'media' / 'size-shapes-life'
FILES = []   # (relative path, title, viewbox, body, css)

BROWN, FAWN, SAND, MINT, SKY = '#7b5a3c', '#efae78', '#f7d79b', '#a2c2a7', '#82acad'

# Extra look for the lead plates (the comic classes from media_kit are reused everywhere else).
LEAD_CSS = (
    ".cap{font:24px Georgia,serif;fill:#322e24}.cap2{font:19px Georgia,serif;fill:#322e24}.cap2 b{font-weight:700}"
    ".tag{font:700 11px 'Courier New',monospace;letter-spacing:1.5px;fill:#28261e}"
    ".lab{font:700 13px 'Courier New',monospace;letter-spacing:1.5px;fill:#322e24}.kick{font:700 12px 'Courier New',monospace;letter-spacing:2px;fill:#a13324}"
    ".sfx{font:italic 900 30px Georgia,serif;fill:#a13324;stroke:#fff8e3;stroke-width:5px;paint-order:stroke}"
    ".pulse{transform-box:fill-box;transform-origin:center;animation:pulse 1.6s ease-in-out infinite}"
    ".sag{transform-box:fill-box;transform-origin:center bottom;animation:sag 3.2s ease-in-out infinite}"
    ".chop{stroke-dasharray:7 7;animation:dash 1.2s linear infinite}"
    "@keyframes pulse{50%{transform:scale(1.12)}}@keyframes sag{0%,35%{transform:none}55%,85%{transform:scaleY(.94)}100%{transform:none}}"
    "@keyframes dash{to{stroke-dashoffset:-28}}"
    "@media(prefers-reduced-motion:reduce){*{animation:none!important}}"
)


def add(path, title, body, viewbox='0 0 320 220', css=None):
    FILES.append((path, title, viewbox, body, css))


def comic(name, title, bg, body):
    add(f'comic/{name}.svg', title, panel(bg, body))


# ---------- shared drawings ----------

def deer(x, y, s=1.0, buckle=False, legs_px=6.5):
    """A cartoon deer about 200 x 175 units at scale 1. Its feet touch y + 172 * s."""
    if buckle:
        legs = ('<path d="M62 106C48 128 72 146 54 172"/><path d="M84 108C74 130 92 148 80 172"/>'
                '<path d="M128 108C140 130 122 148 134 172"/><path d="M148 106C164 128 140 146 156 172"/>')
    else:
        legs = '<path d="M62 106L60 172"/><path d="M84 108L84 172"/><path d="M128 108L128 172"/><path d="M148 106L150 172"/>'
    crack = (f'<path d="M62 128l8 8l-8 8l8 8" fill="none" stroke="{RED}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
             if buckle else '')
    sw = 3 / s if s < 1 else 3
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="{sw:g}" stroke-linecap="round" stroke-linejoin="round">'
            f'<g fill="none" stroke="{BROWN}" stroke-width="{legs_px / s if s < 1 else legs_px:g}">{legs}</g>'
            f'<ellipse cx="38" cy="78" rx="12" ry="8" fill="{FAWN}"/><ellipse cx="100" cy="82" rx="64" ry="32" fill="{FAWN}"/>'
            f'<path d="M146 68L172 30L186 40L166 84Z" fill="{FAWN}"/>'
            f'<ellipse cx="184" cy="30" rx="19" ry="13" fill="{FAWN}" transform="rotate(-14 184 30)"/>'
            f'<path d="M176 18L172 4M176 18L162 8M190 17L196 3M190 17L204 8" fill="none" stroke="{BROWN}" stroke-width="4"/>'
            f'<path d="M172 22L164 12L178 17Z" fill="{SAND}"/><circle cx="192" cy="28" r="2.6" fill="{INK}" stroke="none"/>{crack}</g>')


def cube(x, y, s, fills=(MINT, SAND, FAWN), grid=0):
    """An isometric cube whose top-left corner is (x, y); optional n x n x n grid lines."""
    d = s * .5
    w = d * 1.2
    sw = max(1.5, s / 14)
    out = (f'<g stroke="{INK}" stroke-width="{sw:g}" stroke-linejoin="round">'
           f'<path d="M{x} {y}l{w:g} {-d * .6:g}l{w:g} {d * .6:g}l{-w:g} {d * .6:g}z" fill="{fills[0]}"/>'
           f'<path d="M{x} {y}v{s}l{w:g} {d * .6:g}v{-s}z" fill="{fills[1]}"/>'
           f'<path d="M{x + 2 * w:g} {y}v{s}l{-w:g} {d * .6:g}v{-s}z" fill="{fills[2]}"/></g>')
    if grid:
        k = d * .6
        g = ''
        for i in range(1, grid):
            f = i / grid
            g += (f'M{x + w * f:g} {y + k * f:g}v{s}'                                     # left face, vertical cuts
                  f'M{x:g} {y + s * f:g}l{w:g} {k:g}'                                      # left face, horizontal cuts
                  f'M{x + w + w * f:g} {y + k - k * f:g}v{s}'                              # right face, vertical cuts
                  f'M{x + w:g} {y + k + s * f:g}l{w:g} {-k:g}'                             # right face, horizontal cuts
                  f'M{x + w * f:g} {y + k * f:g}l{w:g} {-k:g}'                             # top face, one direction
                  f'M{x + w * f:g} {y - k * f:g}l{w:g} {k:g}')                             # top face, other direction
        out += f'<path d="{g}" fill="none" stroke="{RED}" stroke-width="2" class="m-dash" opacity=".9"/>'
    return out


def cube_grid(x, y, s, n=3, step=None):
    step = step or s * 1.9
    out = ''
    for r in range(n):
        for c in range(n):
            out += cube(x + c * step, y + r * (s * 1.25), s)
    return out


def mouse(x, y, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M0 22Q-26 20 -38 8" fill="none"/><ellipse cx="14" cy="14" rx="26" ry="16" fill="#c9b8a6"/>'
            f'<ellipse cx="38" cy="8" rx="12" ry="9" fill="#c9b8a6"/><circle cx="32" cy="-2" r="7" fill="#e8c9c0"/>'
            f'<circle cx="42" cy="6" r="2" fill="{INK}" stroke="none"/><circle cx="51" cy="9" r="2.4" fill="#a13324" stroke="none"/></g>')


def elephant(x, y, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">'
            f'<rect x="-52" y="20" width="22" height="48" rx="8" fill="#a9a29a"/><rect x="-14" y="22" width="22" height="46" rx="8" fill="#a9a29a"/>'
            f'<rect x="30" y="22" width="22" height="46" rx="8" fill="#a9a29a"/><rect x="62" y="20" width="22" height="48" rx="8" fill="#a9a29a"/>'
            f'<ellipse cx="14" cy="6" rx="78" ry="44" fill="#bdb6ac"/><ellipse cx="82" cy="-6" rx="34" ry="30" fill="#bdb6ac"/>'
            f'<path d="M106 4q22 8 14 44q-2 12 -12 6" fill="none" stroke-width="9"/><path d="M106 4q22 8 14 44q-2 12 -12 6" fill="none" stroke="#bdb6ac" stroke-width="5"/>'
            f'<ellipse cx="62" cy="-8" rx="18" ry="22" fill="#a9a29a"/><circle cx="92" cy="-12" r="3" fill="{INK}" stroke="none"/></g>')


def spark(x, y):
    return f'<use href="#mstar" x="{x}" y="{y}"/>'


# ======================================================================
# LEAD PLATES (600 x 340)
# ======================================================================

def plate(label, bg, art, c1, c2, c3, ground=''):
    return (f'<rect width="600" height="215" fill="{bg}"/><rect width="600" height="215" fill="url(#dots)" opacity=".22"/>{ground}'
            f'<rect x="12" y="12" width="176" height="22" fill="#f6f0df" stroke="{INK}"/><text x="22" y="27" class="tag">{label}</text>{art}'
            f'<rect y="215" width="600" height="125" fill="#f0e6c8"/><path d="M0 215H600" stroke="{INK}" stroke-width="2"/>'
            f'<text x="300" y="253" text-anchor="middle" class="cap">{c1}</text>'
            f'<text x="300" y="287" text-anchor="middle" class="cap2">{c2}</text>'
            f'<text x="300" y="320" text-anchor="middle" class="kick">{c3}</text>')


add('lead/deer.svg', 'A small deer next to a deer five times bigger whose thin legs are cracking under its weight. '
    'Below: make a deer 5 times bigger and it weighs 125 times more, but its leg bones get only 25 times thicker.',
    plate('PLATE 01 / SIZE', '#c9d3c0',
          f'<path d="M0 200C120 170 220 190 330 180S520 170 600 190V215H0Z" fill="{MINT}"/>'
          + deer(46, 104, .5) + f'<text x="76" y="196" text-anchor="middle" class="lab">1×</text>'
          + f'<g class="sag">{deer(300, 10, 1.1, True)}</g>'
          + '<text x="560" y="160" text-anchor="end" class="sfx pulse">CRACK!</text>',
          'Make a deer 5 times bigger…',
          'it weighs <tspan font-weight="700">125×</tspan> more. Its leg bones get only <tspan font-weight="700">25×</tspan> thicker.',
          'SO THE LEGS GIVE WAY'), viewbox='0 0 600 340', css=LEAD_CSS, )

add('lead/cube.svg', 'One big cube chopped into 125 little cubes. The outside surface gets 5 times bigger while the total amount of stuff stays the same.',
    plate('PLATE 02 / SURFACE', '#e4ecdd',
          f'<g transform="translate(40 -6)">{cube(70, 70, 100)}</g>'
          f'<text x="170" y="206" text-anchor="middle" class="lab">1 BIG CUBE</text>'
          f'<path d="M255 115h60" stroke="{RED}" stroke-width="5" stroke-linecap="round"/><path d="M315 115l-12 -9v18z" fill="{RED}"/>'
          '<text x="285" y="98" text-anchor="middle" class="sfx pulse">CHOP!</text>'
          + cube_grid(350, 60, 26, 3, 50)
          + '<text x="420" y="206" text-anchor="middle" class="lab">125 LITTLE CUBES</text>',
          'Same stuff. Chopped up.',
          'The outside gets <tspan font-weight="700">5×</tspan> bigger. The inside stays the same.',
          'MORE OUTSIDE, SAME INSIDE'), viewbox='0 0 600 340', css=LEAD_CSS)

# ======================================================================
# STORY PANELS (440 x 215)
# ======================================================================

def story(name, title, bg, body):
    add(f'story/{name}.svg', title, f'<rect width="440" height="215" fill="{bg}"/><rect width="440" height="215" fill="url(#dots)" opacity=".22"/>{body}',
        viewbox='0 0 440 215')


story('01-too-big', 'A small deer and a deer five times bigger stand side by side. The big one is not five times stronger, only five times taller.', '#c9d3c0',
      f'<path d="M0 190C100 170 200 188 300 178S400 175 440 188V215H0Z" fill="{MINT}"/>'
      + deer(24, 108, .42) + deer(170, 18, 1.2)
      + t(70, 200, '1×', 'micro') + t(320, 207, '5× bigger every way', 'micro')
      + bubble(18, 14, 132, 44, ['Taller, longer,', 'wider!'], (60, 104)))

story('02-the-chop', 'A big cube is chopped into 125 little cubes, and every little cube has its own outside.', '#e4ecdd',
      f'<g transform="translate(24 40)">{cube(20, 40, 76)}</g>' + t(100, 188, '1 big cube', 'micro')
      + f'<path d="M175 100h50" stroke="{RED}" stroke-width="5" stroke-linecap="round"/><path d="M225 100l-12 -9v18z" fill="{RED}"/>'
      + t(200, 84, 'CHOP!', 'sfx-s')
      + cube_grid(262, 40, 22, 3, 44) + t(330, 188, '125 little cubes', 'micro'))

story('03-the-fixes', 'Three fixes bodies use: thick legs, folded lungs and a long folded gut.', '#f0e3c6',
      f'<rect x="12" y="14" width="130" height="150" rx="10" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>'
      + f'<g stroke="{INK}" stroke-width="2.5"><rect x="48" y="30" width="26" height="112" rx="9" fill="#a9a29a"/><rect x="86" y="30" width="26" height="112" rx="9" fill="#a9a29a"/></g>'
      + t(77, 160, 'thicker legs', 'b-s')
      + f'<rect x="155" y="14" width="130" height="150" rx="10" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>'
      + f'<path d="M220 34v40M220 74q-18 6-30 26M220 74q18 6 30 26M190 100q-6 14 4 28M250 100q6 14-4 28M200 94q-4 8 0 16M240 94q4 8 0 16" fill="none" stroke="#c86f3f" stroke-width="5" stroke-linecap="round"/>'
      + t(220, 160, 'folded lungs', 'b-s')
      + f'<rect x="298" y="14" width="130" height="150" rx="10" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>'
      + f'<path d="M318 40h90q14 0 14 14t-14 14h-80q-14 0-14 14t14 14h80q14 0 14 14t-14 14h-80" fill="none" stroke="#c9826a" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>'
      + t(363, 160, 'a long, folded gut', 'b-s')
      + t(220, 198, 'More inside needs more outside.', 'b'))


def bird_plot():
    # Real data from the paper's Table 1: (wing loading N/m2, cruising speed m/s) for 14 species.
    data = [(23, 7.8), (37, 9.9), (31, 9.0), (34, 9.4), (32, 9.2), (39, 10.1), (44, 10.7), (66, 13.2), (52, 11.7),
            (63, 12.9), (71, 13.6), (82, 14.7), (106, 16.7), (140, 19.2)]
    x0, x1, y0, y1 = 70, 380, 180, 40
    lx = lambda w: x0 + (math.log(w) - math.log(20)) / (math.log(150) - math.log(20)) * (x1 - x0)
    ly = lambda v: y0 + (math.log(v) - math.log(7)) / (math.log(21) - math.log(7)) * (y1 - y0)
    pts = ''.join(f'<circle cx="{lx(w):.1f}" cy="{ly(v):.1f}" r="6" fill="{["#a13324", "#377675", "#b9603a"][i % 3]}" stroke="{INK}" stroke-width="2"/>'
                  for i, (w, v) in enumerate(data))
    # The paper's fit y = 0.50x + 0.48 uses natural logs of wing loading (N/m2) and speed (m/s); it gives 7.8 m/s at 23 N/m2.
    fit = lambda w: math.exp(0.50 * math.log(w) + 0.48)
    line = f'M{lx(20):.1f} {ly(fit(20)):.1f}L{lx(150):.1f} {ly(fit(150)):.1f}'
    return (f'<path d="M{x0} 30V{y0}H{x1 + 20}" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
            f'<path d="{line}" fill="none" stroke="{RED}" stroke-width="3" class="m-dash"/>{pts}'
            + t(225, 205, 'wing loading (weight per wing area) →', 'micro') + t(38, 112, 'speed', 'micro', style='') + t(38, 126, '↑', 'micro'))


story('04-birds', 'A chart of 14 bird species: birds with more weight per wing area cruise faster, along a straight line.', '#e3d5c4', bird_plot()
      + bubble(96, 34, 128, 44, ['14 real birds,', 'one neat line'], (170, 120)))

# ======================================================================
# COMIC PANELS (320 x 220)
# ======================================================================

# ---- strip 1: chop the cube ----
comic('01a-one-cube', 'One big cube. Its faces are the outside, and the stuff in the middle is the inside.', '#e4ecdd',
      cube(104, 58, 92) + t(160, 28, 'OUTSIDE', 'micro') + f'<path d="M160 33v14" stroke="{INK}" stroke-width="2"/>'
      + '<rect x="112" y="118" width="54" height="20" rx="4" fill="#fff8e3" stroke="#322e24" stroke-width="1.5"/>' + t(139, 132, 'INSIDE', 'micro') + t(160, 204, '1 BIG CUBE', 'micro'))
comic('01b-chop', 'Red dashed cut lines show a big cube being chopped into five slices each way.', '#f0e3c6',
      cube(96, 54, 100, grid=5) + t(262, 62, 'CHOP!', 'sfx') + t(160, 206, '5 cuts each way → 125 cubes', 'micro'))
comic('01c-many-cubes', 'Many little cubes together: the same amount of stuff, five times more outside.', '#e4ecdd',
      cube_grid(84, 26, 22, 3, 42) + t(160, 166, '125 little cubes', 'w') + t(160, 192, '5× the outside · same inside', 'micro'))

# ---- strip 2: the deer that got too big ----
comic('02a-two-deer', 'A small deer and a deer five times bigger in every direction.', '#c9d3c0',
      f'<path d="M0 190C80 176 160 186 240 180S300 178 320 186V220H0Z" fill="{MINT}"/>'
      + deer(16, 118, .32) + deer(112, 36, .96) + t(48, 204, '1×', 'micro') + t(215, 212, '5× every way', 'micro'))


def block_grid(x, y, n, size, color):
    return ''.join(f'<rect x="{x + c * size}" y="{y + r * size}" width="{size - 1.5}" height="{size - 1.5}" fill="{color}" stroke="{INK}" stroke-width="1"/>'
                   for r in range(n) for c in range(n))


comic('02b-125-vs-25', 'Weight grows like a cube of blocks, 125 of them. The leg bone slice grows like a flat square, only 25 of them.', '#f0e3c6',
      cube(34, 40, 66, fills=('#d9824f', '#efae78', '#c86f3f'), grid=5)
      + t(86, 140, 'weight', 'w-s') + t(86, 162, '5×5×5 = 125', 'mono-s')
      + block_grid(190, 56, 5, 20, '#d4cbb9') + t(240, 170, 'bone slice', 'w-s') + t(240, 192, '5×5 = 25', 'mono-s'))
comic('02c-crack', 'The big deer’s thin legs buckle and crack under its weight.', '#efd5b7',
      f'<path d="M0 196C80 186 160 194 240 188S300 188 320 194V220H0Z" fill="{MINT}"/>'
      + f'<g class="m-shake">{deer(70, 22, .9, True)}</g>' + t(250, 74, 'CRACK!', 'sfx')
      + bubble(10, 12, 104, 34, ['Too heavy!'], (96, 62)))

# ---- strip 3: breathing through skin ----
def oxy(x, y, delay=0):
    return f'<g{anim("m-bob", delay)}><circle cx="{x}" cy="{y}" r="5" fill="#82acad" stroke="{INK}" stroke-width="1.5"/></g>'


comic('03a-rotifer', 'A tiny rotifer breathes air straight through its skin; little oxygen dots drift in.', '#b8cec0',
      f'<ellipse cx="160" cy="112" rx="62" ry="34" fill="#f7d79b" stroke="{INK}" stroke-width="3"/>'
      f'<path d="M104 96q-14-10-10-26M114 84q-8-16 0-26M216 96q14-10 10-26" fill="none" stroke="{INK}" stroke-width="2.5" stroke-linecap="round"/>'
      f'<circle cx="188" cy="104" r="3" fill="{INK}"/>'
      + oxy(60, 60) + oxy(100, 38, .4) + oxy(250, 66, .8) + oxy(280, 120, .2) + oxy(70, 150, .6)
      + f'<path d="M84 150l14-14M254 148l-14-14M160 188v-30" fill="none" stroke="{RED}" stroke-width="3" class="m-flow" stroke-linecap="round"/>'
      + t(160, 28, 'skin is enough!', 'w-s') + t(160, 206, 'TINY ROTIFER', 'micro'))
comic('03b-too-big', 'If a rotifer were twice as wide, its body would need 8 times more air but its skin would grow only 4 times.', '#e3d5c4',
      f'<ellipse cx="86" cy="86" rx="34" ry="20" fill="{SAND}" stroke="{INK}" stroke-width="3"/>'
      f'<ellipse cx="86" cy="150" rx="68" ry="40" fill="{SAND}" stroke="{INK}" stroke-width="3" stroke-dasharray="6 5"/>'
      + t(86, 44, '1×', 'micro') + t(86, 206, '2× wider', 'micro')
      + f'<rect x="180" y="40" width="26" height="128" fill="{RED}" stroke="{INK}" stroke-width="2"/>' + t(193, 186, 'air', 'micro') + t(193, 30, '8×', 'mono-s')
      + f'<rect x="250" y="104" width="26" height="64" fill="#377675" stroke="{INK}" stroke-width="2"/>' + t(263, 186, 'skin', 'micro') + t(263, 94, '4×', 'mono-s'))
comic('03c-folds', 'Big animals grow folded surfaces: branching lungs, comb-like gills and a coiled, folded gut.', '#f0e3c6',
      f'<path d="M62 40v46M62 86q-18 6-30 28M62 86q18 6 30 28M32 114q-6 14 4 30M92 114q6 14-4 30M42 106q-4 8 0 16M82 106q4 8 0 16" fill="none" stroke="#c86f3f" stroke-width="5" stroke-linecap="round"/>'
      + t(62, 176, 'lungs', 'w-s')
      + f'<path d="M160 56v80" stroke="{INK}" stroke-width="3" fill="none" stroke-linecap="round"/>'
      + ''.join(f'<path d="M160 {62 + i * 14}q18 -6 26 4" fill="none" stroke="#e08b86" stroke-width="5" stroke-linecap="round"/>' for i in range(5))
      + t(172, 176, 'gills', 'w-s')
      + f'<path d="M236 50h54q12 0 12 12t-12 12h-46q-12 0 -12 12t12 12h46q12 0 12 12t-12 12h-54" fill="none" stroke="#c9826a" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>'
      + t(264, 176, 'gut', 'w-s') + t(160, 206, 'more fold = more outside', 'micro'))

# ---- strip 4: why tiny animals snack all day ----
def heat(x, y, n, delay=0):
    return ''.join(f'<g{anim("m-bob", round(delay + i * .25, 2))}><path d="M{x + i * 14} {y}q-5 -8 0 -16q5 -8 0 -16" fill="none" stroke="{RED}" stroke-width="3" stroke-linecap="round"/></g>' for i in range(n))


comic('04a-heat', 'A mouse with many heat waves rising off it, next to an elephant with only a few.', '#e3d5c4',
      mouse(26, 120, 1.15) + heat(34, 100, 5) + elephant(212, 94, .62) + heat(176, 62, 2) + heat(228, 60, 1)
      + t(70, 202, 'LOTS of outside', 'micro') + t(232, 202, 'less outside', 'micro'))
comic('04b-snacks', 'The mouse nibbles seeds and a hummingbird sips sugary nectar: small animals eat rich food again and again.', '#f0e3c6',
      mouse(40, 128, 1.2)
      + f'<g{anim("m-bob")}><circle cx="140" cy="126" r="5" fill="#8a5a3a" stroke="{INK}" stroke-width="1.5"/><circle cx="152" cy="132" r="5" fill="#a27c55" stroke="{INK}" stroke-width="1.5"/></g>'
      + f'<g{anim("m-flap")}><path d="M210 78l22 -22l8 20z" fill="#377675" stroke="{INK}" stroke-width="2"/></g>'
      + f'<ellipse cx="226" cy="90" rx="22" ry="12" fill="#377675" stroke="{INK}" stroke-width="2.5"/><circle cx="244" cy="84" r="9" fill="#a2c2a7" stroke="{INK}" stroke-width="2.5"/>'
      + f'<path d="M252 84l34 10" stroke="{INK}" stroke-width="3" stroke-linecap="round"/><circle cx="292" cy="108" r="12" fill="#e89a66" stroke="{INK}" stroke-width="2.5"/><path d="M292 120v60" stroke="#4f7a66" stroke-width="4"/>'
      + t(80, 196, 'seeds and nuts', 'b-s') + t(250, 196, 'sugary nectar', 'b-s'))
comic('04c-big-eaters', 'An elephant eats low-calorie leaves while a huge blue whale eats tiny krill: big bodies lose less heat for their size.', '#c9d3c0',
      elephant(76, 98, .6)
      + f'<path d="M140 40q14 -8 22 4q-2 16 -22 6zM156 30q14 -8 22 4q-2 16 -22 6z" fill="#4f7a66" stroke="{INK}" stroke-width="2"/>'
      + f'<ellipse cx="236" cy="132" rx="64" ry="26" fill="#5d6aa1" stroke="{INK}" stroke-width="3"/><path d="M172 132q-18 -22 -4 -36q6 14 18 18" fill="#5d6aa1" stroke="{INK}" stroke-width="3"/>'
      + ''.join(f'<circle cx="{286 + (i % 3) * 8}" cy="{104 + i * 7}" r="2.4" fill="{RED}"/>' for i in range(6))
      + t(80, 196, 'leaves', 'b-s') + t(246, 196, 'tiny krill', 'b-s'))

# ======================================================================
# FACT ICONS (160 x 100)
# ======================================================================

def fact(name, title, body):
    add(f'facts/{name}.svg', title, body, viewbox='0 0 160 100')


fact('chop', 'A big cube next to many little cubes.',
     cube(12, 24, 40) + f'<path d="M72 50h16" stroke="{RED}" stroke-width="3" stroke-linecap="round"/>' + cube_grid(100, 20, 11, 3, 20))
fact('deer', 'A deer with thick leg bones marked 25 and a heavy body marked 125.',
     deer(26, 4, .44) + t(80, 94, '125 vs 25', 'mono-s'))
fact('heat', 'A person-shaped flame for the heat the body gives off.',
     f'<path d="M80 12q22 22 8 40q14-4 10 22q-6 14 -18 14q-24 0 -22-24q0-14 10-22q0 12 8 12q-4-22 4-42z" fill="#e08b2c" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
     f'<path d="M80 52q10 12 2 26q-12 0 -8-14z" fill="#f7d79b"/>')
def bird(x, y, k, color):
    return (f'<g transform="translate({x} {y}) scale({k})" stroke="{INK}" stroke-width="{2.6 / k:g}" stroke-linejoin="round" stroke-linecap="round">'
            f'<ellipse cx="0" cy="0" rx="22" ry="11" fill="{color}"/><circle cx="20" cy="-6" r="8" fill="{color}"/><path d="M27 -6l9 3l-9 3z" fill="{SAND}"/>'
            f'<circle cx="22" cy="-8" r="1.8" fill="{INK}" stroke="none"/><path d="M-4 -2L-18 -30L12 -4z" fill="{color}"/><path d="M-22 0l-14 -4l2 8z" fill="{color}"/></g>')


fact('wings', 'A small bird with small wings and a big bird with big wings.', bird(36, 66, .9, '#377675') + bird(106, 56, 1.35, '#b9603a'))
fact('line', 'A line through fourteen dots, sloping up at one half.',
     f'<path d="M14 84L148 20" stroke="{RED}" stroke-width="3" stroke-dasharray="6 5" fill="none"/>'
     + ''.join(f'<circle cx="{18 + i * 9.4:.1f}" cy="{80 - i * 4.6 + (3 if i % 2 else -3):.1f}" r="4" fill="{["#a13324", "#377675", "#b9603a"][i % 3]}" stroke="{INK}" stroke-width="1.5"/>' for i in range(14)))


def main():
    for path, title, viewbox, body, css in FILES:
        svg = standalone(viewbox, body, title, **({'css': css, 'defs': COMIC_DEFS_FOR_LEAD} if css else {}))
        write(OUT, path, svg)
    print(f'wrote {len(FILES)} files to {OUT}')


# Lead plates need the dot pattern and star only; the rest of the comic defs are not used there.
COMIC_DEFS_FOR_LEAD = ('<pattern id="dots" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#26251f" opacity=".24"/></pattern>')

if __name__ == '__main__':
    main()
