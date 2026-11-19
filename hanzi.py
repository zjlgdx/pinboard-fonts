"""Chinese for Pinboard Typewriter, written with the Typewriter's own pen.

The Latin letters are centre lines (skeleton.py) inked by a pen. Chinese is
drawn the same way, with one more layer, because characters share their
parts:

- A stroke (筆畫) is a centre line plus how the pen moves along it. `E` is
  even, with a slight press where the pen lands (橫, 豎, the turns). `P`
  lifts as it goes, ending lighter (撇, 提). `G` stays even and lifts only
  in its final hook (豎鉤, 橫折鉤, 斜鉤). `N` presses toward its end and
  lifts at the foot (捺). `D` is a dot (點), heavier where it ends.
- A component (部件) is a list of strokes on a 1000-unit grid, y down.
- A character is a component, or components placed in boxes: `lr` (left and
  right, ⿰), `tb` (top and bottom, ⿱), or `box` with explicit boxes for
  enclosures (⿴ ⿵ ⿶ ⿸ ⿹ ⿺) and anything else. A component scales into its
  box; the pen does not, so strokes keep one weight in any part.

Every stroke here was drawn for this font, from what each character is: no
other font's outlines or stroke data. The grid's frame is the character's
face.

Each family writes the same strokes its own way (CUTS): the Typewriter as
仿宋 metal type struck through a ribbon, the Ballpoint as a hand's 楷書, the
Marker with its own chisel nib. Only the pen and the grid's transform
differ, so a character drawn once serves all three.
"""
import math
import random
import re

# Each family's cut of Chinese.
#   em      the character's advance, font units (the Typewriter's two cells)
#   face    how much of it the grid's frame fills, font units
#   pen     the pen against the family's Latin pen: (Regular, Bold). Dense
#           characters stay open under the Bold.
#   nib     the round pen's reach across and along a stroke, against its
#           radius: wider than tall makes verticals heavier than horizontals
#   cut     the pressure profile along each stroke (see profile)
#   rise    degrees horizontals climb to the right; verticals stay upright
#   lean    degrees the whole character leans, to sit with a leaning Latin
#   narrow, tall   the face's width and height, against square
#   hand    how much each stroke strays from its place, as a hand's do
#   inked   times the Typewriter's ribbon is struck over it
CUTS = {
    # 仿宋 type, after the slugs of the Chinese typewriter: rising
    # horizontals, a narrow upright face, a press where the pen lands and
    # stops, a little contrast, and a worn ribbon.
    'typewriter': dict(em=1200, face=1060, pen=(0.92, 0.76), nib=(1.12, 0.70), cut='fang',
                       rise=5.5, lean=0, narrow=0.90, tall=1.03, hand=0, inked=2),
    # A hand's 楷書 in ballpoint: pressure that comes and goes, rising
    # horizontals, the Latin's lean (less of it), each stroke a little astray.
    'ballpoint': dict(em=1000, face=900, pen=(1.0, 0.85), nib=(1.0, 0.93), cut='hand',
                      rise=4.5, lean=4, narrow=1.0, tall=1.0, hand=1.0, inked=0),
    # The Marker's chisel at 35 degrees: thick and thin come from the nib.
    'marker': dict(em=1000, face=940, pen=(0.92, 0.82), nib=None, cut='even',
                   rise=3, lean=0, narrow=1.0, tall=1.0, hand=0.6, inked=0),
}

# ---------------------------------------------------------------- strokes

STROKE_KINDS = 'EPGND'


def ease(a, b, x):
    x = min(1.0, max(0.0, (x - a) / (b - a)))
    return x * x * (3 - 2 * x)


def profile(kind, t, cut='kai'):
    """The pen's radius, as a share of its usual one, at t (0 to 1) along a
    stroke of this kind, in one of the cuts:

    - kai: hard-pen 楷書, one weight with a slight press where the pen lands.
    - fang: 仿宋, a firm press where the pen lands and a small one where it
      stops (頓筆); 撇 thins further.
    - hand: kai with a ballpoint's pressure, lighter where it lands and lifts.
    - even: one weight throughout (a broad nib makes its own thick and thin).
    """
    if cut == 'even':
        return 1.15 if kind == 'D' else 1.0
    if cut == 'hand':
        return profile(kind, t) * (0.86 + 0.14 * math.sin(math.pi * min(1.0, t * 1.1)))
    if cut == 'fang':
        if kind == 'E':
            return 1.0 + 0.32 * (1 - ease(0, .1, t)) + 0.16 * ease(.9, 1, t)
        if kind == 'G':
            return 1.0 + 0.32 * (1 - ease(0, .1, t)) - 0.5 * ease(.86, 1, t)
        if kind == 'P':
            return 1.15 - 0.62 * ease(.35, 1, t)
        if kind == 'N':
            return 0.75 + 0.55 * ease(0, .8, t) - 0.6 * ease(.85, 1, t)
        if kind == 'D':
            return 0.7 + 0.6 * ease(0, .9, t)
        raise ValueError(kind)
    if kind == 'E':
        return 1.0 + 0.14 * (1 - ease(0.0, 0.08, t))
    if kind == 'P':
        return 1.08 - 0.5 * ease(0.45, 1.0, t)
    if kind == 'G':
        return 1.0 + 0.14 * (1 - ease(0.0, 0.06, t)) - 0.45 * ease(0.86, 1.0, t)
    if kind == 'N':
        return 0.82 + 0.38 * ease(0.0, 0.78, t) - 0.55 * ease(0.82, 1.0, t)
    if kind == 'D':
        return 0.7 + 0.5 * ease(0.0, 0.9, t)
    raise ValueError(kind)


def strokes(spec):
    """'E M100 200 L900 200; P M…' -> [(kind, path)]."""
    out = []
    for part in spec.split(';'):
        part = part.strip()
        if part:
            out.append((part[0], part[1:].strip()))
    return out


from hanzi_strokes import C, TONES, VERTICAL, VZHS, ZHS   # noqa: E402,F401  (the characters, kept apart from the engine)


def flatten(item, box=(0, 0, 1000, 1000)):
    """A character or component as [(kind, path)] in the 1000 grid of `box`."""
    from skeleton import transform
    x0, y0, x1, y1 = box
    sx, sy = (x1 - x0) / 1000, (y1 - y0) / 1000

    def into(b):
        return (x0 + b[0] * sx, y0 + b[1] * sy, x0 + b[2] * sx, y0 + b[3] * sy)
    if isinstance(item, list):
        return [(k, transform(d, lambda p: (x0 + p[0] * sx, y0 + p[1] * sy))) for k, d in item]
    op = item[0]
    if op == 'lr':
        _, a, b, r = item
        return flatten(a, into((0, 0, 1000 * r, 1000))) + flatten(b, into((1000 * r, 0, 1000, 1000)))
    if op == 'tb':
        _, a, b, r = item
        return flatten(a, into((0, 0, 1000, 1000 * r))) + flatten(b, into((0, 1000 * r, 1000, 1000)))
    if op == 'box':
        return [s for part, b in item[1] for s in flatten(part, into(b))]
    raise ValueError(op)


_START = re.compile(r'M\s*(-?[\d.]+)[\s,]+(-?[\d.]+)')


def by_hand(strokes, rng, amount):
    """Each stroke shifted, turned and sized a little about where it starts,
    as a hand's strokes stray: the character stays itself, the parts loosen."""
    from skeleton import transform
    if not amount:
        return strokes
    out = []
    for kind, d in strokes:
        sx, sy = map(float, _START.search(d).groups())
        dx, dy = rng.gauss(0, 9 * amount), rng.gauss(0, 9 * amount)
        a = math.radians(rng.gauss(0, 2.2 * amount))
        c, s = math.cos(a), math.sin(a)
        f = 1 + rng.gauss(0, 0.035 * amount)

        def m(p, sx=sx, sy=sy, c=c, s=s, dx=dx, dy=dy, f=f):
            x, y = (p[0] - sx) * f, (p[1] - sy) * f
            return sx + x * c - y * s + dx, sy + x * s + y * c + dy
        out.append((kind, transform(d, m)))
    return out


def placed(ch, family, cell, K, seed, form=0):
    """A character's strokes, and the warp from its 1000 grid onto the
    skeleton canvas: the family's cut, its face centred in `cell` (skeleton
    units, K of them to a font unit) and on the capitals (y 400), struck or
    written a little off. `form` 1 is the form mainland China sets in a line
    (ZHS), 2 the one it sets in a column (VZHS)."""
    cut = CUTS[family]
    rng = random.Random(seed)
    sc = cut['face'] / K / 1000
    rise = math.tan(math.radians(cut['rise']))
    lean = math.tan(math.radians(cut['lean']))
    nx, ty = cut['narrow'], cut['tall']
    dy = rng.uniform(-10, 10)
    rot = math.radians(rng.uniform(-1.1, 1.1))
    cr, sr = math.cos(rot), math.sin(rot)

    def warp(x, y):
        y = y - rise * (x - 500)
        x, y = 500 + (x - 500) * nx, 500 + (y - 500) * ty
        x = x - lean * (y - 500)
        x, y = (x - 500) * sc, (y - 500) * sc
        return x * cr - y * sr + cell / 2, x * sr + y * cr + 400 + dy
    return by_hand(flatten((C, ZHS, VZHS)[form][ch]), rng, cut['hand']), warp, rng
