"""Flatten Design-canvas artboards (.dc.html) into standalone HTML pages for screenshots.

Usage: python3 tools/export_canvas.py <canvas project dir> <out dir> Board1 Board2 ...
Inlines <dc-import> children (with their styles), resolves SampleArt's kind, drops the canvas runtime.
"""
import re
import sys
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)

SAMPLE = {
    'dna': ('#e8d0c4', 'isDna'), 'protein': ('#c9d3c0', 'isProtein'), 'waves': ('#3d4a5a', 'isWaves'),
    'stairs': ('#f0e3c6', 'isStairs'), 'particle': ('#ead9b6', 'isParticle'), 'mold': ('#e4ecdd', 'isMold'),
}


def parts(name):
    text = (src / f'{name}.dc.html').read_text()
    body = re.search(r'<x-dc>(.*)</x-dc>', text, re.S).group(1)
    styles = ''.join(re.findall(r'<style>(.*?)</style>', body, re.S))
    body = re.sub(r'<helmet>.*?</helmet>', '', body, flags=re.S)
    title = re.search(r'<title>(.*?)</title>', text).group(1)
    return title, styles, body


def sample_art(body, kind):
    bg, flag = SAMPLE[kind]
    body = body.replace('{{bg}}', bg).replace('{{label}}', f'Sample art: {kind}')

    def keep(m):
        return m.group(2) if m.group(1) == flag else ''
    return re.sub(r'<sc-if value="\{\{(\w+)\}\}"[^>]*>(.*?)</sc-if>', keep, body, flags=re.S)


def flatten(body, styles_seen):
    def child(m):
        attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(1)))
        name = attrs['name']
        _, styles, inner = parts(name)
        styles_seen.setdefault(name, styles)
        if name == 'SampleArt':
            inner = sample_art(inner, attrs.get('kind', 'dna'))
        return flatten(inner, styles_seen)
    return re.sub(r'<dc-import([^>]*)>\s*</dc-import>', child, body)


for board in sys.argv[3:]:
    title, styles, body = parts(board)
    seen = {}
    body = flatten(body, seen)
    all_styles = styles + ''.join(seen.values())
    html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{title}</title>'
            f'<style>{all_styles}</style></head><body>{body}</body></html>\n')
    assert '{{' not in html, f'{board}: unresolved template hole'
    (out / f'{board}.html').write_text(html)
    print('wrote', board)
