"""Shared drawing kit for Geeky Times media.

Every graphic is written as a standalone, self-contained animated SVG file: its own <style>, <defs> and
reduced-motion rule, no scripts and no outside references. The same file therefore works as an <img>,
inlined by the site renderer, or served from a CDN / S3 bucket.
"""
import html
from pathlib import Path

INK = '#322e24'
RED = '#a13324'
COL = {'The': '#f7d79b', 'bat': '#efae78', 'flew': '#a2c2a7', 'writer': '#dc9665', 'looker': '#c3b2d8'}
EIGHT = ['#a13324', '#377675', '#b9603a', '#5d6aa1', '#8a5a9a', '#4f7a66', '#b08a2c', '#7a4a3a']

# Styles and animations used by comic panels and fact icons.
COMIC_CSS = """
text{fill:#28261e;font:17px Georgia,serif}.w{font:bold 20px Georgia,serif}.w-s{font:bold 15px Georgia,serif}
.b{font:18px Georgia,serif}.b-s{font:15px Georgia,serif}.micro{font:bold 12px 'Courier New',monospace;letter-spacing:1px}
.mono{font:bold 20px 'Courier New',monospace}.mono-s{font:bold 14px 'Courier New',monospace}
.sfx,.sfx-s{font:italic 900 30px Georgia,serif;fill:#a13324;stroke:#fff8e3;stroke-width:5px;paint-order:stroke;letter-spacing:-.02em}.sfx-s{font-size:22px}
:where([class*="m-"]){transform-box:fill-box;transform-origin:center}
.m-blink{animation:m-blink 1.2s steps(2) infinite}.m-bob{animation:m-bob 1.6s ease-in-out infinite alternate}
.m-spin{animation:m-spin 3s linear infinite}.m-spin-slow{transform-origin:left center;animation:m-spin 4s linear infinite}
.m-feed{animation:m-feed 4.5s ease-in-out infinite}.m-loop-pop{animation:m-loop-pop 4.5s ease-out infinite}
.m-hop{animation:m-hop 2.4s ease-in-out infinite}
.m-alt-a{animation:m-alt 3.6s ease-in-out infinite}.m-alt-b{animation:m-alt 3.6s ease-in-out -1.8s infinite}
.m-swing{transform-origin:center top;animation:m-swing 2.2s ease-in-out infinite alternate}.m-wiggle{animation:m-wiggle 1.4s ease-in-out infinite}
.m-meter{transform-origin:left center;animation:m-meter 6s ease-out infinite}.m-pulse{animation:m-pulse 1.8s ease-in-out infinite}
.m-wobble{animation:m-wobble 1.8s ease-in-out infinite alternate}.m-flow{stroke-dasharray:10 8;animation:m-flow .9s linear infinite}
.m-fill{transform-origin:center bottom;animation:m-fill 6s ease-in-out infinite}.m-flap{animation:m-flap .45s ease-in-out infinite alternate}
.m-twinkle{animation:m-twinkle 2.4s ease-in-out infinite}.m-scan{animation:m-scan 3s ease-in-out infinite alternate}
.m-dash{stroke-dasharray:6 9;animation:m-trace 1.4s linear infinite}.m-gather{animation:m-gather 4s ease-in-out infinite}
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
@keyframes m-fill{0%{transform:scaleY(.05)}60%,100%{transform:scaleY(1)}}@keyframes m-flap{to{transform:scaleY(.8)}}
@keyframes m-twinkle{50%{transform:scale(.5);opacity:.4}}@keyframes m-scan{to{transform:translateX(84px)}}@keyframes m-trace{to{stroke-dashoffset:-30}}
@keyframes m-gather{0%,15%{transform:none;opacity:1}55%,70%{transform:translate(var(--dx),var(--dy));opacity:0}100%{transform:none;opacity:1}}
@keyframes m-ride{0%,6%{transform:translateY(140px)}14%,20%{transform:translateY(112px)}28%,34%{transform:translateY(84px)}42%,48%{transform:translateY(56px)}56%,62%{transform:translateY(28px)}70%,96%{transform:none}100%{transform:translateY(140px)}}
@keyframes m-shake{0%,80%,100%{transform:none}84%{transform:translateX(-3px)}88%{transform:translateX(3px)}92%{transform:translateX(-2px)}}
@keyframes m-cover6{0%,10%{transform:none}16%,34%{transform:translateX(70px)}40%,58%{transform:translateX(198px)}64%,94%{transform:translateX(284px)}100%{transform:none}}
@keyframes m-ink1{0%,14%{opacity:0}18%,95%{opacity:1}100%{opacity:0}}@keyframes m-ink2{0%,38%{opacity:0}42%,95%{opacity:1}100%{opacity:0}}@keyframes m-ink3{0%,62%{opacity:0}66%,95%{opacity:1}100%{opacity:0}}
"""

REDUCED_MOTION = '@media(prefers-reduced-motion:reduce){*{animation:none!important}}'

COMIC_DEFS = (
    f'<g id="wb" stroke="{INK}" stroke-width="2" stroke-linecap="round">'
    '<path d="M-14 25v10l-8 2M14 25v10l8 2M-34 2l-10-5M34 2l10-6" fill="none"/>'
    '<rect x="-34" y="-25" width="68" height="50" rx="10" fill="currentColor"/>'
    f'<circle cx="-7" cy="-14" r="2" fill="{INK}" stroke="none"/><circle cx="7" cy="-14" r="2" fill="{INK}" stroke="none"/>'
    '<path d="M-3 -9q3 3 6 0" fill="none"/></g>'
    f'<path id="mstar" d="M0 -10L3 -3 10 0 3 3 0 10 -3 3 -10 0 -3 -3Z" fill="#ffe597" stroke="{INK}" stroke-width="1"/>'
    '<pattern id="dots" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#26251f" opacity=".24"/></pattern>'
    '<pattern id="m-hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><path d="M0 0V7" stroke="#f6f0df" stroke-width="2" opacity=".3"/></pattern>'
    '<pattern id="m-grid" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="3" height="3" fill="#377675"/></pattern>'
)


def standalone(viewbox, body, title, css=COMIC_CSS, defs=COMIC_DEFS):
    """Wrap drawing markup into a self-contained SVG document."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}" role="img">'
            f'<title>{html.escape(title)}</title><style>{css.strip()}\n{REDUCED_MOTION}</style>'
            f'<defs>{defs}</defs>{body}</svg>\n')


def write(out_dir, name, svg):
    path = Path(out_dir) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg)
    return path


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
    """A word-buddy character. Animated wrappers stay separate from the positioning transform."""
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


def panel(bg, body):
    """Body of a 320x220 comic panel: background, halftone dots, then the drawing."""
    return f'<rect width="320" height="220" fill="{bg}"/><rect width="320" height="220" fill="url(#dots)" opacity=".22"/>{body}'
