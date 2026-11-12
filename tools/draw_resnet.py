"""Draws the lead plates, comic panels, story panels and fact icons for "Deep Residual Learning" (ResNet).

Run from the repo root:  python3 tools/draw_resnet.py
Writes standalone SVG files to public/media/resnet/lead/.
Plate captions/alt text live in data/seed/papers/resnet.json.
"""
from pathlib import Path

from media_kit import COL, COMIC_DEFS, INK, RED, anim, buddy, standalone, t, write

OUT = Path(__file__).resolve().parent.parent / 'public' / 'media' / 'resnet' / 'lead'
CREAM = '#fbf3dc'
BLUR = ''.join(f'<filter id="bl{i}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="{s}"/></filter>'
               for i, s in enumerate([0, 1.4, 2.8, 4.6]))
DEFS = COMIC_DEFS + BLUR + (
    f'<marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
    f'<path d="M0 0L10 5L0 10Z" fill="{INK}"/></marker>'
    f'<marker id="ahr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
    f'<path d="M0 0L10 5L0 10Z" fill="{RED}"/></marker>')


def plate(bg, tag, body, caption):
    return (f'<rect width="600" height="340" fill="{bg}"/><rect width="600" height="340" fill="url(#dots)" opacity=".22"/>'
            + body
            + f'<rect x="10" y="288" width="580" height="44" fill="{CREAM}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
            + t(300, 317, caption, 'b')
            + t(22, 28, tag, 'micro', 'start', f'fill:{RED}')
            + f'<path d="M8 10Q300 5 592 9Q596 170 591 332Q300 336 9 331Q4 170 8 10Z" fill="none" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>')


def cat(blur=0, fixes=0):
    """A cat sketch on a card, centred on (0,0); card is 104x78."""
    g = (f'<rect x="-52" y="-39" width="104" height="78" rx="4" fill="#fff8e3" stroke="{INK}" stroke-width="2.5"/>'
         f'<g filter="url(#bl{blur})">'
         f'<path d="M-24 -10L-26 -32L-9 -20ZM24 -10L26 -32L9 -20Z" fill="#efae78" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
         f'<ellipse cx="0" cy="2" rx="29" ry="24" fill="#efae78" stroke="{INK}" stroke-width="2.5"/>'
         f'<circle cx="-11" cy="-2" r="3.2" fill="{INK}"/><circle cx="11" cy="-2" r="3.2" fill="{INK}"/>'
         f'<path d="M-3 6h6l-3 4Z" fill="{RED}"/><path d="M0 10q-4 5-8 2M0 10q4 5 8 2" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>'
         f'<path d="M-30 3l-16-3M-30 9l-15 5M30 3l16-3M30 9l15 5" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>'
         '</g>')
    marks = [f'<path d="M-9 25l-6 6 6 3 3-5ZM9 25l6 6-6 3-3-5Z" fill="{RED}" stroke="{INK}" stroke-width="1.5" stroke-linejoin="round"/>',   # bow
             f'<circle cx="-18" cy="6" r="4" fill="{RED}" opacity=".6"/><circle cx="18" cy="6" r="4" fill="{RED}" opacity=".6"/>',            # blush
             f'<path d="M-26 -22l-3-8M26 -22l3-8" stroke="{RED}" stroke-width="2.5" stroke-linecap="round"/>',                                # ear tufts
             f'<use href="#mstar" transform="translate(36 -26) scale(1.3)"/>']
    return g + ''.join(marks[:fixes])


def row(xs, cards, bud_y=240):
    out = ''
    for i, x in enumerate(xs):
        out += f'<g transform="translate({x} 128)">{cards[i]}</g>'
        out += buddy(x, bud_y, 'helper', COL['writer'], .8, label_cls='w-s')
        out += f'<path d="M{x} 168V198" stroke="{INK}" stroke-width="2.5" stroke-dasharray="4 4"/>'
    return out


XS = [90, 230, 370, 510]

# ---- fix-it: the picture rides the shortcut, each helper adds one small fix ----
shortcut = (f'<path d="M62 78Q300 -10 538 78" fill="none" stroke="{RED}" stroke-width="4" stroke-linecap="round" marker-end="url(#ahr)" stroke-dasharray="3 0"/>'
            f'<rect x="240" y="26" width="120" height="24" rx="4" fill="{CREAM}" stroke="{RED}" stroke-width="2"/>'
            + t(300, 43, 'SHORTCUT', 'micro', style=f'fill:{RED}'))
arrows = ''.join(f'<path d="M{x + 56} 128H{x + 84}" stroke="{INK}" stroke-width="3" marker-end="url(#ah)"/>' for x in XS[:3])
fix_body = (shortcut + arrows + row(XS, [cat(0, i + 1) for i in range(4)])
            + f'<g{anim("m-twinkle")}>' + t(440, 222, 'SAME CAT!', 'sfx-s') + '</g>'
            + t(90, 278, '+ fix', 'micro', style=f'fill:{RED}') + t(230, 278, '+ fix', 'micro', style=f'fill:{RED}')
            + t(370, 278, '+ fix', 'micro', style=f'fill:{RED}') + t(510, 278, '+ fix', 'micro', style=f'fill:{RED}'))

# ---- redraw: every helper redraws from scratch, the cat degrades ----
redraw_arrows = ''.join(f'<path d="M{x + 56} 128H{x + 84}" stroke="{INK}" stroke-width="3" marker-end="url(#ah)"/>' for x in XS[:3])
redraw_body = (redraw_arrows + row(XS, [cat(i) for i in range(4)])
               + t(300, 62, 'EACH HELPER REDRAWS FROM SCRATCH', 'micro', style=f'fill:{RED}')
               + f'<g{anim("m-wobble")}>' + t(440, 222, 'BLUR!', 'sfx') + '</g>'
               + t(90, 80, 'clear', 'micro') + t(510, 80, 'a smudge', 'micro'))

# =====================================================================================================
# Comic panels (320x220), story panels (440x215) and fact icons (160x100)
# Alt text below is copied verbatim from data/seed/papers/resnet.json (fact icons are decorative there).
# =====================================================================================================
ROOT = OUT.parent
PANELS = []   # (path, viewBox, alt/title, body)
HELP = COL['writer']
GREY = '#f0e3c6'
SW = f'stroke="{INK}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"'


def add(path, vb, alt, bg, body):
    w, h = vb.split()[2:]
    base = f'<rect width="{w}" height="{h}" fill="{bg}"/><rect width="{w}" height="{h}" fill="url(#dots)" opacity=".22"/>'
    PANELS.append((path, vb, alt, base + body))


def kitten(x, y, s=1, blur=0, fixes=0, card=True):
    """The cat card from the lead plates, placed and scaled."""
    c = cat(blur, fixes)
    if not card:
        c = c.split('<g filter', 1)[1]
        c = '<g filter' + c
    return f'<g transform="translate({x} {y}) scale({s})">{c}</g>'


def slabs(x, y, w, n, h=10, color='#f7d79b', gap=0):
    """A stack of layer slabs, bottom edge at y, centred on x."""
    return ''.join(f'<rect x="{x - w / 2:g}" y="{y - (i + 1) * (h + gap):g}" width="{w}" height="{h}" fill="{color if i % 2 else "#efae78"}" '
                   f'stroke="{INK}" stroke-width="1.8" stroke-linejoin="round"/>' for i in range(n))


def arrow(d, color=INK, w=3, mark='ah', extra=''):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" marker-end="url(#{mark})"{extra}/>'


def note(x, y, w, h, text, rot=-3, cls='w', size=None):
    st = f'font-size:{size}px' if size else ''
    return (f'<g transform="translate({x} {y}) rotate({rot})"><rect x="{-w / 2:g}" y="{-h / 2:g}" width="{w}" height="{h}" fill="#ffe597" stroke="{INK}" stroke-width="2"/>'
            f'<path d="M{-w / 2 + 6:g} {-h / 2 + 8:g}h{w - 12:g}" stroke="{INK}" stroke-width="1" opacity=".3"/>'
            + t(0, f'{h / 4:g}', text, cls, style=st) + '</g>')


def bridge(x1, x2, y, lift=26, color=RED):
    return (f'<path d="M{x1} {y}Q{(x1 + x2) / 2:g} {y - lift * 2}  {x2} {y}" fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round" marker-end="url(#ahr)"/>')


def tiny_cat(x, y, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})"><rect x="-15" y="-11" width="30" height="22" rx="2" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>'
            f'<path d="M-7 -2L-8 -8L-3 -5ZM7 -2L8 -8L3 -5Z" fill="#efae78" stroke="{INK}" stroke-width="1.2"/>'
            f'<ellipse cx="0" cy="1" rx="8" ry="7" fill="#efae78" stroke="{INK}" stroke-width="1.5"/></g>')


# ---------- strip 1: guess what is in the photo ----------

add('comic/01a-photo.svg', '0 0 320 220', 'A photo of a cat with a question mark and a list of many labels.', '#efd5b7',
    f'<g transform="rotate(-4 90 110)">' + kitten(92, 112, 1.1) + '</g>'
    + f'<g{anim("m-bob")}>' + t(92, 52, '?', 'sfx') + '</g>'
    + arrow('M150 112H178', INK)
    + f'<rect x="184" y="34" width="122" height="152" rx="5" fill="#fff8e3" stroke="{INK}" stroke-width="2.5"/>'
    + ''.join(f'<rect x="194" y="{46 + i * 30}" width="102" height="22" rx="3" fill="{c}" stroke="{INK}" stroke-width="1.8"/>' + t(245, 62 + i * 30, w, 'b-s')
              for i, (w, c) in enumerate([('tabby cat', '#efae78'), ('teapot', '#a2c2a7'), ('toaster', '#c3b2d8'), ('+ 997 more', '#f7d79b')]))
    + t(245, 205, '1,000 ANSWERS', 'micro', style=f'fill:{RED}'))

add('comic/01b-five-guesses.svg', '0 0 320 220', 'A machine holds up five guess cards beside a photo.', '#b8cec0',
    f'<g transform="rotate(-5 58 66)">' + kitten(58, 70, .85) + '</g>'
    + buddy(76, 160, 'robot', COL['looker'], 1.1, label_cls='w-s')
    + ''.join(f'<g transform="translate({138 + i * 36} {104 - (i == 2) * 8}) rotate({(i - 2) * 7})">'
              f'<rect x="-16" y="-30" width="32" height="60" rx="3" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>'
              + t(0, 8, str(i + 1), 'w', style=f'fill:{RED}' if i == 2 else '') + '</g>' for i in range(5))
    + f'<path d="M104 150L134 118M104 150L190 124" stroke="{INK}" stroke-width="2.5" stroke-linecap="round"/>'
    + t(222, 176, '5 GUESSES', 'sfx-s') + t(222, 198, 'top-5 error', 'micro'))

add('comic/01c-lower-better.svg', '0 0 320 220', 'A scoreboard with a small number highlighted as better.', '#efd5b7',
    f'<rect x="28" y="30" width="108" height="100" rx="6" fill="#5d5846" stroke="{INK}" stroke-width="3"/>'
    f'<rect x="184" y="24" width="108" height="112" rx="6" fill="#3d4a45" stroke="{RED}" stroke-width="4"/>'
    + t(82, 94, '21%', 'w', style='font-size:34px;fill:#f8d065') + t(82, 52, 'OLD', 'micro', style='fill:#f6f0df')
    + t(238, 98, '7%', 'w', style='font-size:40px;fill:#f8d065') + t(238, 48, 'NEW', 'micro', style='fill:#f6f0df')
    + '<use href="#mstar" transform="translate(284 26) scale(2.2)"/>'
    + f'<g{anim("m-pulse")}>' + t(238, 168, 'BETTER!', 'sfx-s') + '</g>'
    + t(82, 160, 'error', 'micro') + t(160, 205, 'LOWER IS BETTER', 'micro', style=f'fill:{RED}'))

# ---------- strip 2: the more-layers puzzle ----------


def line(y, n_help, n_pass):
    out = tiny_cat(26, y, 1.0) + tiny_cat(296, y, 1.0)
    total = n_help + n_pass
    xs = [66 + i * (190 / (total - 1)) for i in range(total)]
    out += f'<path d="M42 {y}H280" stroke="{INK}" stroke-width="2.5" stroke-dasharray="4 4"/>'
    for i, x in enumerate(xs):
        if i < n_help:
            out += buddy(x, y, '', HELP, .42)
        else:
            out += buddy(x, y, '', GREY, .42)
            out += f'<path d="M{x - 12:g} {y + 24}h24" stroke="{RED}" stroke-width="3" stroke-linecap="round"/>'
    return out


add('comic/02a-copy-trick.svg', '0 0 320 220', 'A short line of helpers and a longer line whose extra helpers simply pass the picture along.', '#82acad',
    t(160, 28, 'SHALLOW', 'micro', style='fill:#fff8e3') + line(66, 3, 0)
    + t(160, 118, 'DEEPER: EXTRA HELPERS JUST PASS IT ON', 'micro', style='fill:#fff8e3') + line(164, 3, 3)
    + t(160, 206, 'same cat out = just as good', 'b-s', style='fill:#fff8e3'))

add('comic/02b-but-worse.svg', '0 0 320 220', 'A graph where the line for the deeper machine sits above the line for the shallower one.', '#f0e3c6',
    f'<path d="M50 24V180H300" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round" marker-end="url(#ah)"/>'
    f'<path d="M50 180V20" stroke="{INK}" stroke-width="3" stroke-linecap="round" marker-end="url(#ah)"/>'
    + t(176, 204, 'TRAINING TIME', 'micro') + f'<g transform="translate(24 100) rotate(-90)">{t(0, 0, "ERROR", "micro")}</g>'
    + f'<path d="M58 60Q90 110 140 118T290 122" fill="none" stroke="{RED}" stroke-width="4.5" stroke-linecap="round"/>'
    f'<path d="M58 80Q90 140 140 148T290 150" fill="none" stroke="#377675" stroke-width="4.5" stroke-linecap="round"/>'
    + t(228, 108, 'deeper', 'w-s', style=f'fill:{RED}') + t(228, 172, 'shallower', 'w-s', style='fill:#377675')
    + f'<g{anim("m-pulse")}>' + t(120, 50, 'WORSE?!', 'sfx') + '</g>')

add('comic/02c-hard-to-learn.svg', '0 0 320 220', 'A helper struggling to hold still, with a thought bubble that says do nothing.', '#efd5b7',
    f'<g{anim("m-shake")}>' + buddy(100, 150, 'helper', HELP, 1.1, label_cls='w-s')
    + slabs(100, 108, 76, 4, 11, '#f7d79b') + '</g>'
    + f'<path d="M62 100l-12-8M138 100l12-8" stroke="{INK}" stroke-width="2.5" stroke-linecap="round"/>'
    + f'<path d="M144 112q8 8 2 16q-8-6-2-16ZM58 120q-8 8-2 14q8-6 2-14Z" fill="#82acad" stroke="{INK}" stroke-width="1.5"/>'
    + f'<circle cx="150" cy="86" r="5" fill="#fff8e3" stroke="{INK}" stroke-width="2"/><circle cx="166" cy="64" r="8" fill="#fff8e3" stroke="{INK}" stroke-width="2"/>'
    + f'<ellipse cx="240" cy="50" rx="68" ry="34" fill="#fff8e3" stroke="{INK}" stroke-width="2.5"/>'
    + t(240, 46, 'do', 'w') + t(240, 68, 'nothing…', 'w')
    + f'<g{anim("m-wobble")}>' + t(240, 148, 'WOBBLE!', 'sfx') + '</g>' + t(240, 188, 'hard to learn', 'micro'))

# ---------- strip 3: learn the fix, not the picture ----------

add('comic/03a-whole-picture.svg', '0 0 320 220', 'A helper draws a whole cat from scratch.', '#b8cec0',
    f'<path d="M180 190L204 52M262 190L240 52M200 120H246" stroke="#6b4f36" stroke-width="6" stroke-linecap="round"/>'
    + f'<rect x="170" y="42" width="116" height="92" fill="#fff8e3" stroke="{INK}" stroke-width="3"/>'
    + kitten(228, 88, .95, card=False) + t(296, 40, 'H', 'sfx')
    + buddy(80, 150, 'helper', HELP, 1.05, label_cls='w-s')
    + f'<path d="M112 138L168 98" stroke="{INK}" stroke-width="2.5" stroke-linecap="round"/>'
    + t(80, 204, 'every line, from scratch', 'b-s') + t(60, 60, 'WHOLE ANSWER', 'micro', style=f'fill:{RED}'))

add('comic/03b-fix-only.svg', '0 0 320 220', 'A helper writes only a small difference note while the input picture waits beside it.', '#82acad',
    f'<g transform="rotate(-4 58 74)">' + kitten(58, 78, .9) + '</g>' + t(58, 134, 'x', 'sfx-s') + t(58, 154, 'waits here', 'micro', style='fill:#fff8e3')
    + buddy(168, 128, 'helper', HELP, 1.05, label_cls='w-s')
    + f'<path d="M202 118L246 92" stroke="{INK}" stroke-width="2.5" stroke-linecap="round"/>'
    + note(262, 82, 76, 50, 'F = H−x', -5, 'w-s') + t(266, 124, 'the fix', 'micro', style='fill:#fff8e3')
    + f'<rect x="64" y="172" width="192" height="34" rx="17" fill="#fff8e3" stroke="{INK}" stroke-width="2.5"/>' + t(160, 196, 'F(x) + x', 'w'))

add('comic/03c-push-to-zero.svg', '0 0 320 220', 'A fix note shrinking to zero while the picture passes through untouched.', '#efd5b7',
    note(52, 66, 64, 44, 'F', -4, 'w', 24) + note(142, 70, 38, 28, 'F', 3, 'w-s', 15) + note(212, 72, 18, 14, '', -2)
    + f'<circle cx="272" cy="70" r="22" fill="#fff8e3" stroke="{RED}" stroke-width="3"/>' + t(272, 80, '0', 'w', style=f'fill:{RED};font-size:28px')
    + arrow('M90 68H112', INK) + arrow('M168 70H192', INK) + arrow('M228 70H246', INK)
    + t(160, 28, 'PUSH THE FIX TOWARD ZERO', 'micro', style=f'fill:{RED}')
    + f'<path d="M20 160H300" stroke="{INK}" stroke-width="4" stroke-linecap="round" marker-end="url(#ah)"/>'
    + kitten(46, 160, .42) + kitten(274, 160, .42) + t(160, 150, 'picture passes through', 'b-s') + t(160, 200, 'untouched', 'micro'))

# ---------- strip 4: a shortcut that costs nothing ----------

LAYERS = (slabs(160, 190, 110, 5, 14, '#f7d79b') + t(160, 212, 'LAYERS', 'micro'))
add('comic/04a-bridge.svg', '0 0 320 220', 'A bridge carries a copy of the picture over a block of layers.', '#b8cec0',
    LAYERS + f'<path d="M0 190H105M215 190H320" stroke="{INK}" stroke-width="3"/>'
    + f'<path d="M26 112Q160 -10 294 112" fill="none" stroke="{RED}" stroke-width="7" stroke-linecap="round"/>'
    + f'<path d="M26 112Q160 -10 294 112" fill="none" stroke="#fbf3dc" stroke-width="2" stroke-dasharray="3 7" stroke-linecap="round"/>'
    + f'<path d="M26 112V190M294 112V190" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
    + kitten(52, 96, .45) + kitten(268, 96, .45)
    + t(160, 92, 'COPY', 'sfx') + t(160, 112, 'identity shortcut', 'micro'))

add('comic/04b-no-extra.svg', '0 0 320 220', 'A tag reading zero extra settings on the bridge.', '#efd5b7',
    f'<path d="M20 150Q160 70 300 150" fill="none" stroke="{RED}" stroke-width="7" stroke-linecap="round"/>'
    f'<path d="M20 150V196M300 150V196" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
    + f'<path d="M160 110V74" stroke="{INK}" stroke-width="2"/>'
    + f'<g transform="translate(160 60) rotate(3)"><path d="M-62 -28H50L66 0L50 28H-62Z" fill="#fbf3dc" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
    f'<circle cx="52" cy="0" r="4" fill="#efd5b7" stroke="{INK}" stroke-width="2"/>'
    + t(-12, 2, '+0', 'sfx', style='font-size:36px') + t(-12, 20, 'extra settings', 'micro') + '</g>'
    + f'<g transform="translate(70 166)"><circle r="14" fill="#edca75" stroke="{INK}" stroke-width="5" stroke-dasharray="3 3"/><circle r="5" fill="{INK}"/>'
    f'<path d="M-20 -20L20 20" stroke="{RED}" stroke-width="5" stroke-linecap="round"/></g>'
    + t(222, 188, 'no gears added', 'b-s'))

add('comic/04c-sizes.svg', '0 0 320 220', 'Two adapters on the bridge: one pads with zeros, one reshapes the picture.', '#82acad',
    f'<path d="M0 40Q160 -20 320 40" fill="none" stroke="{RED}" stroke-width="6" stroke-linecap="round"/>'
    f'<rect x="12" y="62" width="144" height="138" rx="6" fill="#fff8e3" stroke="{INK}" stroke-width="2.5"/>'
    f'<rect x="164" y="62" width="144" height="138" rx="6" fill="#fff8e3" stroke="{INK}" stroke-width="2.5"/>'
    + t(84, 84, 'PAD WITH ZEROS', 'micro') + t(236, 84, 'RESHAPE', 'micro')
    + ''.join(f'<rect x="{34 + (i % 4) * 24}" y="{100 + (i // 4) * 24}" width="22" height="22" fill="{"#efae78" if (i % 4 < 2 and i // 4 < 2) else "#f6f0df"}" stroke="{INK}" stroke-width="1.8"/>'
              + (t(45 + (i % 4) * 24, 117 + (i // 4) * 24, '0', 'mono-s') if not (i % 4 < 2 and i // 4 < 2) else '') for i in range(16))
    + f'<rect x="182" y="102" width="34" height="62" fill="#efae78" stroke="{INK}" stroke-width="2.5"/>'
    + arrow('M222 133H238', INK)
    + f'<rect x="244" y="118" width="54" height="30" fill="#efae78" stroke="{INK}" stroke-width="2.5"/>'
    + t(236, 186, 'projection', 'b-s'))

# ---------- strip 5: stacking it high ----------

add('comic/05a-stack.svg', '0 0 320 220', 'Four towers of different heights labelled 34, 50, 101 and 152.', '#f0e3c6',
    f'<path d="M12 176H308" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'
    + ''.join(slabs(x, 176, 46, max(2, round(n / 12)), 10, c) .replace('height="10"', 'height="10"') + t(x, 198, str(n), 'w', style=f'fill:{RED}' if n == 152 else '')
              for x, n, c in [(52, 34, '#f7d79b'), (127, 50, '#f7d79b'), (202, 101, '#f7d79b'), (277, 152, '#f7d79b')])
    + t(160, 30, 'LAYERS', 'micro', style=f'fill:{RED}') + f'<g{anim("m-bob")}><use href="#mstar" transform="translate(277 30) scale(1.6)"/></g>')

add('comic/05b-bottleneck.svg', '0 0 320 220', 'A block that narrows in the middle like an hourglass.', '#b8cec0',
    f'<g {SW}>'
    '<rect x="50" y="16" width="120" height="22" fill="#f7d79b"/><path d="M50 38H170L120 70H100Z" fill="#efae78"/>'
    '<rect x="100" y="70" width="20" height="30" fill="#c3b2d8"/>'
    '<path d="M100 100H120L170 132H50Z" fill="#efae78"/><rect x="50" y="132" width="120" height="22" fill="#f7d79b"/></g>'
    + tiny_cat(110, 176, 1.3) + t(110, 208, 'back to full size', 'micro')
    + t(236, 36, 'SQUEEZE', 'sfx-s') + t(236, 56, 'make it small', 'b-s')
    + t(236, 92, 'WORK', 'sfx-s') + t(236, 112, 'cheaply', 'b-s')
    + t(236, 150, 'EXPAND', 'sfx-s') + t(236, 170, 'again', 'b-s'))

add('comic/05c-lighter.svg', '0 0 320 220', 'A 152-layer tower on a scale that tips lighter than a shorter VGG tower.', '#efd5b7',
    f'<path d="M160 74V190M118 192H202" stroke="{INK}" stroke-width="6" stroke-linecap="round"/><circle cx="160" cy="72" r="7" fill="#edca75" stroke="{INK}" stroke-width="2.5"/>'
    + f'<g transform="rotate(7 160 72)"><path d="M54 72H266" stroke="{INK}" stroke-width="6" stroke-linecap="round"/></g>'
    + f'<g transform="translate(51 80)"><path d="M0 -6L-28 44M0 -6L28 44" stroke="{INK}" stroke-width="2"/><path d="M-30 44H30" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'
    + slabs(0, 44, 22, 5, 8, '#f7d79b') + '</g>'
    + f'<g transform="translate(269 98)"><path d="M0 -6L-34 46M0 -6L34 46" stroke="{INK}" stroke-width="2"/><path d="M-38 46H38" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'
    + slabs(0, 46, 52, 3, 10, '#c3b2d8') + '</g>'
    + t(51, 156, 'ResNet-152', 'w-s') + t(51, 178, '11.3 billion', 'b-s', style=f'fill:{RED}')
    + t(269, 176, 'VGG-16', 'w-s') + t(269, 198, '15.3 billion', 'b-s', style=f'fill:{RED}')
    + t(160, 30, 'LIGHTER!', 'sfx'))

# ---------- story panels (440x215) ----------

blur_chain = ''
for i, (x, b) in enumerate(zip([48, 136, 224, 312, 400], [0, 1, 1, 2, 3])):
    blur_chain += kitten(x, 62, .62, b) + buddy(x, 160, '', HELP, .7)
    blur_chain += f'<path d="M{x} 96V126" stroke="{INK}" stroke-width="2" stroke-dasharray="4 4"/>'
    if i < 4:
        blur_chain += arrow(f'M{x + 34} 62H{x + 56}', INK, 2.5)
add('story/01-too-many-helpers.svg', '0 0 440 215', 'A line of helpers redraws a cat; each copy is a little blurrier than the last.', '#efd5b7',
    blur_chain + t(224, 22, 'EACH HELPER REDRAWS FROM SCRATCH', 'micro', style=f'fill:{RED}')
    + t(48, 205, 'clear', 'micro') + t(400, 205, 'a smudge', 'micro') + f'<g{anim("m-wobble")}>' + t(300, 206, 'BLUR!', 'sfx-s') + '</g>')

add('story/02-write-the-fix.svg', '0 0 440 215', 'A helper holds the incoming cat picture and a small sticky note labelled fix.', '#b8cec0',
    f'<g transform="rotate(-4 90 100)">' + kitten(92, 102, 1.25) + '</g>' + t(92, 176, 'keeps the picture', 'b-s')
    + buddy(220, 130, 'helper', HELP, 1.5, label_cls='w-s')
    + note(354, 86, 96, 66, 'fix', -6, 'w', 30)
    + t(354, 150, 'adds only a note', 'b-s') + t(220, 30, 'IF THE PICTURE IS FINE, THE NOTE IS TINY', 'micro', style=f'fill:{RED}'))

add('story/03-the-shortcut.svg', '0 0 440 215', 'The picture rides a bridge over a block of helpers and meets their fix at the far side.', '#82acad',
    kitten(40, 156, .5)
    + f'<path d="M40 128Q170 -30 308 130" fill="none" stroke="{RED}" stroke-width="6" stroke-linecap="round" marker-end="url(#ahr)"/>'
    + f'<path d="M40 128Q170 -30 308 130" fill="none" stroke="#fbf3dc" stroke-width="2" stroke-dasharray="3 7"/>'
    + t(170, 48, 'SHORTCUT', 'sfx-s')
    + f'<rect x="92" y="122" width="164" height="78" rx="8" fill="#fff8e3" stroke="{INK}" stroke-width="2.5"/>'
    + ''.join(buddy(x, 164, '', HELP, .52) for x in (130, 174, 218))
    + t(174, 212, 'the helpers', 'micro', style='fill:#fff8e3')
    + arrow('M256 170H286', INK) + note(272, 148, 34, 22, 'fix', -4, 'w-s', 15)
    + f'<circle cx="310" cy="164" r="17" fill="#fff8e3" stroke="{INK}" stroke-width="2.5"/>' + t(310, 174, '+', 'w', style='font-size:28px')
    + arrow('M328 164H350', INK) + kitten(392, 164, .62, 0, 2) + t(392, 204, 'clear again', 'micro', style='fill:#fff8e3'))

add('story/04-scorecard.svg', '0 0 440 215', 'Plain 34-layer network: 28.54 percent top-1 error. Residual 34-layer network: 25.03 percent. Same ImageNet validation test.', '#efd5b7',
    t(220, 26, 'TOP-1 ERROR ON IMAGENET (LOWER IS BETTER)', 'micro', style=f'fill:{RED}')
    + f'<path d="M96 40V176H420" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
    + f'<rect x="97" y="52" width="285" height="44" fill="#efae78" stroke="{INK}" stroke-width="2.5"/><rect x="97" y="52" width="285" height="44" fill="url(#m-hatch)"/>'
    + f'<rect x="97" y="112" width="250" height="44" fill="#377675" stroke="{INK}" stroke-width="2.5"/><rect x="97" y="112" width="250" height="44" fill="url(#m-hatch)"/>'
    + t(88, 72, 'Plain', 'w-s', 'end') + t(88, 90, '34 layers', 'micro', 'end') + t(88, 132, 'Residual', 'w-s', 'end') + t(88, 150, '34 layers', 'micro', 'end')
    + t(364, 82, '28.54%', 'w', 'end', 'fill:#28261e;font-size:22px') + t(329, 142, '25.03%', 'w', 'end', 'fill:#fff8e3;font-size:22px')
    + '<use href="#mstar" transform="translate(372 134) scale(2)"/>'
    + t(220, 202, 'same ImageNet validation test, same size and settings', 'b-s'))

# ---------- fact icons (160x100) ----------

ICONS = []
ICONS.append(('facts/layers.svg', 'A very tall tower of 152 thin layers next to a short tower of 19 layers.',
              slabs(112, 84, 36, 25, 2.6, '#f7d79b') + slabs(40, 84, 32, 3, 2.6, '#c3b2d8')
              + t(112, 14, '152', 'w', style=f'fill:{RED}') + t(40, 68, '19', 'w-s') + t(40, 97, 'VGG', 'micro') + t(112, 97, 'RESNET', 'micro')
              + f'<path d="M20 84H150" stroke="{INK}" stroke-width="2"/>'))
ICONS.append(('facts/no-extra.svg', 'A shortcut bridge with a plus zero tag and a crossed-out gear.',
              f'<path d="M10 70Q80 18 150 70" fill="none" stroke="{RED}" stroke-width="5" stroke-linecap="round"/><path d="M10 70V92M150 70V92" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'
              + t(80, 60, '+0', 'sfx', style='font-size:34px') + t(80, 92, 'EXTRA SETTINGS', 'micro')
              + f'<g transform="translate(130 28)"><circle r="9" fill="#edca75" stroke="{INK}" stroke-width="4" stroke-dasharray="3 3"/><path d="M-13 -13L13 13" stroke="{RED}" stroke-width="3.5" stroke-linecap="round"/></g>'))
ICONS.append(('facts/plain-vs-res.svg', 'Two bars: the plain 34-layer machine has a longer error bar than the residual one.',
              f'<path d="M12 12V78H152" fill="none" stroke="{INK}" stroke-width="2.5" stroke-linecap="round"/>'
              f'<rect x="13" y="18" width="126" height="22" fill="#efae78" stroke="{INK}" stroke-width="2"/><rect x="13" y="46" width="110" height="22" fill="#377675" stroke="{INK}" stroke-width="2"/>'
              + t(20, 34, '28.54', 'mono-s', 'start') + t(20, 62, '25.03', 'mono-s', 'start', 'fill:#fff8e3')
              + t(80, 95, 'PLAIN VS RESIDUAL', 'micro')))
ICONS.append(('facts/top5.svg', 'A gold trophy cup with a first place ribbon.',
              f'<g {SW}><path d="M52 14H108V44Q108 66 80 66Q52 66 52 44Z" fill="#edca75"/><path d="M52 22H38Q36 42 56 46M108 22H122Q124 42 104 46" fill="none"/>'
              '<path d="M80 66V78M60 78H100V88H60Z" fill="#a27c55"/></g>'
              + t(80, 46, '1st', 'w-s', style='font-size:17px') + f'<g{anim("m-twinkle")}><use href="#mstar" transform="translate(126 16) scale(1.2)"/></g>'
              + t(80, 98, '3.57% TOP-5', 'micro', style=f'fill:{RED}')))
ICONS.append(('facts/coco.svg', 'A photo with a red box drawn around a cat and a plus 28 percent tag.',
              f'<rect x="10" y="8" width="140" height="74" fill="#fff8e3" stroke="{INK}" stroke-width="2.5"/>'
              + kitten(52, 46, .5, card=False)
              + f'<rect x="22" y="22" width="62" height="48" fill="none" stroke="{RED}" stroke-width="3" stroke-dasharray="6 3"/>'
              + f'<rect x="96" y="22" width="48" height="26" rx="4" fill="{RED}" stroke="{INK}" stroke-width="2"/>' + t(120, 41, '+28%', 'w-s', style='fill:#fff8e3')
              + t(80, 97, 'OBJECT DETECTION', 'micro')))
ICONS.append(('facts/1202.svg', 'An enormous, dense tower of 1202 layers that wobbles at the top.',
              slabs(80, 94, 46, 36, 2, '#f7d79b') + f'<rect x="57" y="22" width="46" height="72" fill="url(#m-hatch)"/>'
              + f'<g{anim("m-wobble")}>' + t(80, 14, '1202', 'sfx-s') + '</g>'
              + t(26, 54, 'too', 'b-s') + t(26, 72, 'big?', 'b-s') + t(134, 62, '7.93', 'mono-s', style=f'fill:{RED}') + t(134, 80, '> 6.43', 'micro')))


def write_all():
    for path, vb, alt, body in PANELS:
        write(ROOT, path, standalone(vb, body, alt, defs=DEFS))
    for path, alt, body in ICONS:
        write(ROOT, path, standalone('0 0 160 100', body, alt, defs=DEFS))
    return len(PANELS), len(ICONS)


if __name__ == '__main__':
    write(OUT, 'fix-it.svg', standalone('0 0 600 340', plate('#b8cec0', 'PLATE 01 / FIX-IT', fix_body, 'The picture rides along. Each helper adds one small fix.'),
          'The same line of helpers, but the cat picture rides along on a shortcut and each helper only adds a small fix. The cat stays clear.', defs=DEFS))
    write(OUT, 'redraw.svg', standalone('0 0 600 340', plate('#efd5b7', 'PLATE 02 / REDRAW', redraw_body, 'Redraw from scratch, again and again, and it blurs.'),
          'A long line of helpers, each redrawing a cat picture. The cat gets blurrier with every helper.', defs=DEFS))
    print(f'wrote 2 lead plates to {OUT}')
    n_panels, n_icons = write_all()
    print(f'wrote {n_panels} panels and {n_icons} icons to {ROOT}')
