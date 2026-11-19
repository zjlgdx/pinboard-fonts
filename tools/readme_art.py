"""The README's logo and specimen, drawn from the built fonts.

    .venv/bin/python tools/readme_art.py [FONTS]

FONTS is out/ (the default), or the `full/` folder the website's tools/webfonts.py
writes, where the fonts are cut into slices (it has an index.json). Writes, in docs/:

    logo-light.svg, logo-dark.svg   the mark (the Marker's bold 一, a grain above it)
                                    with 一粟 and Yisu, as outlines: GitHub shows an
                                    SVG as an image, which can't load a font
    hero-light.png, hero-dark.png   one line of 《前赤壁賦》 and its English in each family

Light and dark differ only in colour; the README picks one with <picture>.
"""
import json
import sys
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'out'
DOCS = ROOT / 'docs'
# The website's colours (zjlgdx/yisu): ink and the accent, by day and by night.
THEMES = {'light': dict(ink='#1d1c1b', hot='#b3362b', soft='#6b6760'),
          'dark': dict(ink='#ece8da', hot='#d9b45a', soft='#9a968c')}
FAMILIES = [('Yinni', '印泥', 'the Typewriter'), ('Huasha', '畫沙', 'the Ballpoint'), ('Louhen', '漏痕', 'the Marker')]
WEB = {'Yinni': 'yinni', 'Huasha': 'huasha', 'Louhen': 'louhen'}

SLICED = (FONTS / 'index.json').exists()
INDEX = json.loads((FONTS / 'index.json').read_text(encoding='utf-8')) if SLICED else None


def files(family, weight):
    """Font files for a family and weight, and which one holds a character."""
    if not SLICED:
        f = FONTS / f'Yisu{family}-{weight}.otf'
        return lambda ch: f
    # The page's own subsets (one folder up) hold what the page shows, which the slices skip.
    stem = f"{WEB[family]}-{400 if weight == 'Regular' else 700}"
    where = {ch: i // INDEX['size'] for i, ch in enumerate(INDEX['order'])}

    def pick(ch):
        tries = [FONTS.parent / f'{stem}.woff2', FONTS.parent / f'{stem}-t.woff2', FONTS / f'{stem}-a.woff2']
        if ch in where:
            tries.insert(0, FONTS / f'{stem}-{where[ch]:02d}.woff2')
        for f in tries:
            if f.exists() and ord(ch) in _cmap(f):
                return f
        raise KeyError(f'{ch} not in {stem}')
    return pick


_cmaps = {}


def _cmap(path):
    if path not in _cmaps:
        _cmaps[path] = TTFont(path)['cmap'].getBestCmap()
    return _cmaps[path]


_tt = {}


def outline(family, weight, text, x, base, size):
    """SVG path data for text set from (x, baseline) at a size in px, and the x after it."""
    pick, d = files(family, weight), []
    for ch in text:
        path = pick(ch)
        font = _tt.setdefault(path, TTFont(path))
        gs, upm = font.getGlyphSet(), font['head'].unitsPerEm
        name = font.getBestCmap()[ord(ch)]
        s = size / upm
        pen = SVGPathPen(gs, ntos=lambda v: f'{v:.1f}'.rstrip('0').rstrip('.'))
        gs[name].draw(TransformPen(pen, Transform(s, 0, 0, -s, x, base)))
        d.append(pen.getCommands())
        x += gs[name].width * s
    return ' '.join(d), x


def fitted(family, weight, ch, cx, cy, w=None, h=None):
    """One glyph scaled to a width or height, its ink centred on (cx, cy): the mark."""
    path = files(family, weight)(ch)
    font = _tt.setdefault(path, TTFont(path))
    gs = font.getGlyphSet()
    g = gs[font.getBestCmap()[ord(ch)]]
    b = BoundsPen(gs)
    g.draw(b)
    x0, y0, x1, y1 = b.bounds
    s = w / (x1 - x0) if w else h / (y1 - y0)
    pen = SVGPathPen(gs, ntos=lambda v: f'{v:.1f}'.rstrip('0').rstrip('.'))
    g.draw(TransformPen(pen, Transform(s, 0, 0, -s, cx - (x0 + x1) / 2 * s, cy + (y0 + y1) / 2 * s)))
    return pen.getCommands()


def logo(theme):
    c = THEMES[theme]
    # The mark on a square of 260, as the site draws it on 1000 (tools/mark.py, design K).
    k = 0.26
    one = fitted('Louhen', 'Bold', '一', 500 * k, 700 * k, w=900 * k)
    grain = fitted('Huasha', 'Bold', '、', 640 * k, 340 * k, h=360 * k)
    name, x = outline('Huasha', 'Regular', '一粟', 300, 205, 170)
    latin, x2 = outline('Huasha', 'Regular', 'Yisu', x + 34, 205, 92)
    motto, _ = outline('Huasha', 'Regular', '立於一畫', x + 38, 98, 40)
    width = int(max(x2, x) + 20)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 260" width="{width}" height="260">'
            f'<title>一粟 Yisu</title>'
            f'<path fill="{c["ink"]}" d="{one}"/><path fill="{c["hot"]}" d="{grain}"/>'
            f'<path fill="{c["ink"]}" d="{name}"/><path fill="{c["ink"]}" d="{latin}"/>'
            f'<path fill="{c["hot"]}" d="{motto}"/></svg>\n')


class Line:
    """Text in one family and weight, drawn run by run from whichever file holds each character."""

    def __init__(self, family, weight, size):
        self.pick, self.size, self.fonts = files(family, weight), size, {}

    def runs(self, text):
        out = []
        for ch in text:
            f = self.pick(ch)
            if out and out[-1][0] == f:
                out[-1][1] += ch
            else:
                out.append([f, ch])
        return [(self.fonts.setdefault(f, ImageFont.truetype(str(f), self.size)), t) for f, t in out]

    def width(self, text):
        return sum(f.getlength(t) for f, t in self.runs(text))

    def draw(self, d, x, base, text, fill):
        for f, t in self.runs(text):
            d.text((x, base), t, font=f, fill=fill, anchor='ls')
            x += f.getlength(t)
        return x


HANZI = '寄蜉蝣於天地，渺滄海之一粟。'
LATIN = 'A mayfly lodged between heaven and earth, one grain of millet in the vast sea.'


def hero(theme):
    c, W, pad = THEMES[theme], 2000, 40
    rows = []
    for fam, zh, en in FAMILIES:
        big = 108 if fam != 'Yinni' else 92        # the Typewriter's hanzi take 1.2 em
        rows.append((fam, zh, en, Line(fam, 'Regular', big), Line(fam, 'Regular', 46), Line(fam, 'Bold', 34)))
    H = pad + len(rows) * 300
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = pad
    for fam, zh, en, big, small, label in rows:
        x = label.draw(d, 0, y + 34, f'{zh} {fam}', c['hot'])
        Line(fam, 'Regular', 30).draw(d, x + 18, y + 34, en, c['soft'])
        end = big.draw(d, 0, y + 170, HANZI, c['ink'])
        # The English as wide as the Chinese above it, or narrower.
        small = Line(fam, 'Regular', min(46, int(46 * end / small.width(LATIN))))
        small.draw(d, 0, y + 250, LATIN, c['ink'])
        y += 300
    box = img.getbbox()
    img = img.crop((0, 0, min(W, box[2] + 8), box[3] + 12))
    return img


DOCS.mkdir(exist_ok=True)
for theme in THEMES:
    (DOCS / f'logo-{theme}.svg').write_text(logo(theme), encoding='utf-8')
    h = hero(theme)
    h.save(DOCS / f'hero-{theme}.png', optimize=True)
    print(theme, 'logo', (DOCS / f'logo-{theme}.svg').stat().st_size, 'bytes; hero', h.size)
