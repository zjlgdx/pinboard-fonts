"""Build Pinboard's fonts from the pen skeletons in skeleton.py.

Each glyph's centre line is written with a pen on a large bitmap, traced
back to curves with potrace, spaced from its own shape, kerned, and
assembled into an OpenType (CFF) font and a WOFF2 copy in out/.

    .venv/bin/python build.py            # all fonts
    .venv/bin/python build.py marker     # one font

The pens:
  ballpoint  a fine round pen leaning 9 degrees, with light pressure changes
  marker     a chisel nib held at 35 degrees, upright
  typewriter a round pen with slab serifs, monospaced, struck through an
             inked ribbon: uneven ink, dry patches, letters a little off line

What follows the usual type-design rules (see README.md for sources):
  - round shapes overshoot the baseline, x-height, cap height and figure
    height by about 2% so they look as tall as flat ones
  - the round pens are a little flatter than round, so horizontal strokes
    come out slightly lighter than vertical ones
  - sidebearings come from each letter's own profile: straight sides get
    the full space, round sides less, open and diagonal sides least
  - kerning is measured from the same profiles for every letter pair
  - the two handwriting fonts carry two alternates of each lowercase letter
    and cycle them (`calt`), so a double letter is never drawn twice alike
  - curves get points at their extremes; outer contours run
    counter-clockwise, as CFF expects
  - vertical metrics follow the Google Fonts guide: typo metrics in use,
    a 1.24 em line, caps centred in it, win metrics at the font's bounds
"""

import math
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from fontTools.agl import UV2AGL
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.misc.bezierTools import splitCubicAtT
from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.roundingPen import RoundingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont

from skeleton import ALL, TYPE_SERIFS

HERE = Path(__file__).resolve().parent
OUT = HERE / 'out'

VERSION = 0.200         # head.fontRevision; nameID 5 says the same

S = 2.0                 # bitmap pixels per skeleton unit
X0, Y0 = -200, -100     # bitmap origin, in skeleton units
W, H = 1100, 1250       # bitmap size, in skeleton units
K = 0.86                # skeleton unit -> font unit
BASE = 750              # skeleton baseline

# Skeleton lines that round shapes overshoot, and by how much.
LOWER_LINES = (40, 250, 750, 960)   # ascender, x-height, baseline, descender
UPPER_LINES = (50, 750)             # cap height and figure height, baseline
OVERSHOOT = 12                      # skeleton units: ~10 font units, 2.4% of x-height

# Vertical metrics: a 1.24 em line with the caps centred in it
# (ascender - cap height = |descender|), worked out per font.
LINE = 1240

# ---------------------------------------------------------------- paths

TOKEN = re.compile(r'[MLCZmlcz]|-?(?:\d+\.?\d*|\.\d+)')


def subpaths(d):
    """Flatten an SVG path (M L C Z, absolute or relative) into polylines of
    (x, y, on_curve) points; on_curve marks points sampled from a curve."""
    toks = TOKEN.findall(d)
    out, pts, closed = [], None, False
    i, cmd = 0, None
    cx = cy = sx = sy = 0.0

    def num():
        nonlocal i
        i += 1
        return float(toks[i - 1])

    def flush():
        if pts and len(pts) > 1:
            out.append((pts, closed))

    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]
            i += 1
            if cmd in 'Zz':
                if pts:
                    pts.append((sx, sy, pts[0][2]))
                closed = True
                flush()
                pts, closed = None, False
                cx, cy = sx, sy
                continue
        rel = cmd.islower()
        if cmd in 'Mm':
            flush()
            x, y = num(), num()
            if rel:
                x, y = cx + x, cy + y
            cx, cy, sx, sy = x, y, x, y
            pts, closed = [(x, y, False)], False
            cmd = 'l' if rel else 'L'
        elif cmd in 'Ll':
            x, y = num(), num()
            if rel:
                x, y = cx + x, cy + y
            pts.append((x, y, False))
            cx, cy = x, y
        elif cmd in 'Cc':
            c = [num() for _ in range(6)]
            if rel:
                c = [c[k] + (cx if k % 2 == 0 else cy) for k in range(6)]
            p0, p1, p2, p3 = (cx, cy), (c[0], c[1]), (c[2], c[3]), (c[4], c[5])
            if len(pts) == 1:
                pts[0] = (pts[0][0], pts[0][1], True)
            for k in range(1, 41):
                t = k / 40
                u = 1 - t
                pts.append((
                    u**3 * p0[0] + 3*u*u*t * p1[0] + 3*u*t*t * p2[0] + t**3 * p3[0],
                    u**3 * p0[1] + 3*u*u*t * p1[1] + 3*u*t*t * p2[1] + t**3 * p3[1],
                    True,
                ))
            cx, cy = p3
        else:
            raise ValueError(f'unsupported path command {cmd!r}')
    flush()
    return out


def overshoot(ch):
    """Push the round parts of a letter or figure past the lines they meet."""
    if ch.islower():
        lines = LOWER_LINES
    elif ch.isupper() or ch.isdigit():
        lines = UPPER_LINES
    else:
        return lambda x, y, curved: (x, y)
    reach = 70

    def push(x, y, curved):
        if not curved:
            return x, y
        for line in lines:
            d = abs(y - line)
            if d < reach:
                f = 0.5 + 0.5 * math.cos(math.pi * d / reach)
                # Above the middle of the letter "outward" is up (y down).
                outward = -1 if line < 500 else 1
                y += outward * OVERSHOOT * f
        return x, y
    return push


def resample(pts, step):
    """Points every `step` units along a polyline, with t from 0 to 1."""
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    total = sum(seg)
    if total < 1e-6:
        return [(pts[0][0], pts[0][1], 0.0)], 0.0
    n = max(2, int(total / step) + 1)
    res, j, acc = [], 0, 0.0
    for k in range(n):
        d = total * k / (n - 1)
        while j < len(seg) - 1 and acc + seg[j] < d:
            acc += seg[j]
            j += 1
        f = 0 if seg[j] == 0 else (d - acc) / seg[j]
        a, b = pts[j], pts[j + 1]
        res.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, d / total))
    return res, total


def prepare(ch, d, step, warp):
    strokes = []
    push = overshoot(ch)
    for pts, closed in subpaths(d):
        pts = [warp(*push(x, y, c)) for x, y, c in pts]
        res, length = resample(pts, step)
        strokes.append((res, closed, length))
    return strokes


# ---------------------------------------------------------------- pens

def px(x, y):
    return (x - X0) * S, (y - Y0) * S


def round_pen(draw, strokes, radius, taper=0.0, dot=1.25, flat=0.93):
    """A round pen, slightly flatter than round: horizontal strokes come
    out a few percent lighter than vertical ones, which reads as even."""
    for pts, closed, length in strokes:
        r0 = radius * (dot if length < 30 else 1.0)
        for x, y, t in pts:
            # Ink is lighter where the pen lands and lifts.
            f = 1.0 if closed else 1 - taper * (1 - math.sin(math.pi * t)) ** 2
            rx = r0 * f * S
            ry = rx * flat
            cx, cy = px(x, y)
            draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)


def nib_pen(draw, strokes, half_w, half_t, angle):
    a = math.radians(angle)
    u = (math.cos(a), -math.sin(a))     # along the nib edge
    v = (math.sin(a), math.cos(a))      # across it
    # A rectangle with softened corners: a felt tip, not a steel blade.
    shape = []
    for k in range(24):
        th = 2 * math.pi * k / 24
        c, s = math.cos(th), math.sin(th)
        e = 0.3
        sx = math.copysign(abs(c) ** e, c) * half_w
        sy = math.copysign(abs(s) ** e, s) * half_t
        shape.append((u[0] * sx + v[0] * sy, u[1] * sx + v[1] * sy))
    for pts, _closed, _length in strokes:
        for x, y, _t in pts:
            cx, cy = px(x, y)
            draw.polygon([(cx + dx * S, cy + dy * S) for dx, dy in shape], fill=255)


# ---------------------------------------------------------------- styles

def seed_for(name, ch):
    return sum((i + 1) * ord(c) for i, c in enumerate(name + ch))


def noise(rng, shape, cells):
    small = rng.random((cells, cells)).astype(np.float32)
    img = Image.fromarray((small * 255).astype(np.uint8)).resize(
        (shape[1], shape[0]), Image.BICUBIC)
    a = np.asarray(img, dtype=np.float32) / 255
    return (a - a.mean()) / (a.std() + 1e-6)


class Ballpoint:
    family = 'Pinboard Ballpoint'
    mono = False
    alternates = 2
    # Degrees of lean, part of the handwriting as in other script fonts: the
    # font stays a Regular with post.italicAngle 0, but is spaced upright.
    lean = 9
    space = 250
    # A straight lowercase stem's sidebearing: about a third of n's counter.
    lower_side = 64
    upper_side = 80
    panose = (3, 0, 0, 0, 0, 0, 0, 0, 0, 0)     # Latin hand written
    speck = 24
    smooth = (3.0, '1.2')       # blur in pixels before tracing, potrace -O

    def draw(self, ch, img, variant=0):
        rng = random.Random(seed_for('ballpoint', ch + '#' * variant))
        # Each letter leans, sits and sizes a little differently, kept small
        # enough that no one letter jumps out of a word.
        k = math.tan(math.radians(self.lean + rng.uniform(-1.5, 1.5)))
        dy = rng.uniform(-3, 3)
        sz = rng.uniform(0.99, 1.01)
        ax, ay = rng.uniform(0, 6), rng.uniform(0, 6)

        def warp(x, y):
            x += 8 * math.sin(y * 0.012 + ax)
            y += 3 * math.sin(x * 0.010 + ay)
            y = BASE + (y - BASE) * sz + dy
            return x + (BASE - y) * k, y

        strokes = prepare(ch, ALL[ch], 1.0, warp)
        round_pen(ImageDraw.Draw(img), strokes, radius=27, taper=0.15)
        return img


class Marker:
    family = 'Pinboard Marker'
    mono = False
    alternates = 2
    lean = 0
    space = 270
    lower_side = 56
    upper_side = 70
    panose = (3, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    speck = 24
    smooth = (2.5, '1.2')

    def draw(self, ch, img, variant=0):
        rng = random.Random(seed_for('marker', ch + '#' * variant))
        ax = rng.uniform(0, 6)
        dy = rng.uniform(-3, 3)
        rot = math.radians(rng.uniform(-0.8, 0.8))
        cr, sr = math.cos(rot), math.sin(rot)

        def warp(x, y):
            x += 4 * math.sin(y * 0.01 + ax)
            x, y = x - 300, y - 450
            x, y = x * cr - y * sr, x * sr + y * cr
            return x + 300, y + 450 + dy

        # A chisel dot is a short dab, not a touch.
        strokes = prepare(ch, ALL[ch].replace('l2 8', 'l16 26'), 1.0, warp)
        nib_pen(ImageDraw.Draw(img), strokes, half_w=56, half_t=13, angle=35)
        return img


class Typewriter:
    family = 'Pinboard Typewriter'
    mono = True
    alternates = 0
    lean = 0
    advance = 600               # font units, every glyph
    space = 600
    panose = (2, 0, 0, 9, 0, 0, 0, 0, 0, 0)     # Latin text; proportion 9 = monospaced
    # Specks and dry patches smaller than ~20 x 20 font units would only cost
    # outline points: they vanish at any size the font is read at.
    speck = 2200
    smooth = (1.2, '0.8')

    def draw(self, ch, img, variant=0):
        rng = random.Random(seed_for('typewriter', ch))
        d = ALL[ch] + ' ' + TYPE_SERIFS.get(ch, '')
        raw = [p for pts, _ in subpaths(d) for p in pts]
        lo = min(p[0] for p in raw)
        hi = max(p[0] for p in raw)
        mid = (lo + hi) / 2
        room = self.advance / K - 160          # the cell, less the pen and a gap
        # Typewriter letters fill their cell: narrow ones widen, wide ones squeeze.
        sq = min(1.45 if hi - lo > 150 else 1.0, room / max(hi - lo, 1))
        # Each key strikes a little off: a touch high or low, a hair rotated.
        dy = rng.uniform(-10, 10)
        rot = math.radians(rng.uniform(-1.1, 1.1))
        cr, sr = math.cos(rot), math.sin(rot)

        def warp(x, y):
            x = mid + (x - mid) * sq
            x, y = x - mid, y - 400
            x, y = x * cr - y * sr, x * sr + y * cr
            return x + mid, y + 400 + dy

        strokes = prepare(ch, d, 2.0, warp)
        round_pen(ImageDraw.Draw(img), strokes, radius=36, dot=1.6)
        return self.ink(img, rng)

    def ink(self, img, rng):
        nrng = np.random.default_rng(rng.randrange(1 << 30))
        shape = (img.height, img.width)
        soft = np.asarray(img.filter(ImageFilter.GaussianBlur(4 * S)), np.float32) / 255
        low = noise(nrng, shape, 10)
        mid = noise(nrng, shape, 36)
        strike = rng.uniform(-0.05, 0.05)       # some keys hit harder
        level = 0.5 + strike + 0.10 * low + 0.05 * mid
        ink = soft > level
        # Where the ribbon is dry, small patches don't take ink.
        dry = noise(nrng, shape, 40)
        ink &= ~((dry > 1.7) & (low > -0.3))
        return Image.fromarray((ink * 255).astype(np.uint8))


STYLES = {'ballpoint': Ballpoint, 'marker': Marker, 'typewriter': Typewriter}

# ---------------------------------------------------------------- tracing

TRANSFORM = re.compile(r'translate\(([-\d.]+),([-\d.]+)\)\s*scale\(([-\d.]+),([-\d.]+)\)')
D_ATTR = re.compile(r'\sd="([^"]+)"')


def trace(img, tmp, speck, smooth):
    """Bitmap (white ink on black) -> RecordingPen in font units."""
    # A light blur before the threshold smooths the stamped pen's edge, so
    # potrace fits long curves instead of many short ones.
    soft = np.asarray(img.filter(ImageFilter.GaussianBlur(smooth[0])))
    bw = Image.fromarray(np.where(soft > 127, 0, 255).astype(np.uint8)).convert('1')
    pbm, svg = tmp / 'g.pbm', tmp / 'g.svg'
    bw.save(pbm)
    subprocess.run(['potrace', '-b', 'svg', '-t', str(speck), '-a', '1.0', '-O', smooth[1],
                    '-o', str(svg), str(pbm)], check=True)
    text = svg.read_text()
    rec = RecordingPen()
    m = TRANSFORM.search(text)
    if not m:
        return rec
    tx, ty, sx, sy = map(float, m.groups())
    # svg (x, y) = (tx + sx*X, ty + sy*Y); skeleton = svg/S + origin;
    # font = (x * K, (BASE - y) * K)
    pen = TransformPen(rec, (sx / S * K, 0, 0, -sy / S * K,
                             (tx / S + X0) * K, (BASE - Y0 - ty / S) * K))
    for d in D_ATTR.findall(text):
        parse_path(d, pen)
    return rec


def bounds(rec):
    bp = BoundsPen(None)
    rec.replay(bp)
    return bp.bounds


class ExtremaPen(BasePen):
    """Splits each cubic at its horizontal and vertical extremes, so every
    curve spans at most a quarter turn and has points where rasterisers and
    hinting expect them."""

    def __init__(self, out):
        super().__init__(None)
        self.out = out

    def _moveTo(self, p):
        self.out.moveTo(p)

    def _lineTo(self, p):
        self.out.lineTo(p)

    def _curveToOne(self, p1, p2, p3):
        p0 = self._getCurrentPoint()
        ts = set()
        for i in (0, 1):
            a = -p0[i] + 3 * p1[i] - 3 * p2[i] + p3[i]
            b = 2 * (p0[i] - 2 * p1[i] + p2[i])
            c = p1[i] - p0[i]
            if abs(a) < 1e-9:
                if abs(b) > 1e-9:
                    ts.add(-c / b)
                continue
            disc = b * b - 4 * a * c
            if disc >= 0:
                r = math.sqrt(disc)
                ts.update(((-b + r) / (2 * a), (-b - r) / (2 * a)))
        ts = sorted(t for t in ts if 0.02 < t < 0.98)
        for seg in (splitCubicAtT(p0, p1, p2, p3, *ts) if ts else [(p0, p1, p2, p3)]):
            self.out.curveTo(seg[1], seg[2], seg[3])

    def _closePath(self):
        self.out.closePath()

    def _endPath(self):
        self.out.endPath()


# ---------------------------------------------------------------- spacing

ROWS = np.arange(-320, 820, 8)      # font-unit rows the profiles sample


def profile(img, slant):
    """Leftmost and rightmost ink on each row, in font units, measured with
    the lean taken out (as type designers space an italic)."""
    a = np.asarray(img) > 127
    left = np.full(ROWS.shape, np.nan)
    right = np.full(ROWS.shape, np.nan)
    mid_y = (BASE - 250) * K / 2
    for i, y in enumerate(ROWS):
        r = int(round((BASE - y / K - Y0) * S))
        if 0 <= r < a.shape[0]:
            cols = np.flatnonzero(a[r])
            if cols.size:
                shift = slant * (y - mid_y)
                left[i] = (cols[0] / S + X0) * K - shift
                right[i] = (cols[-1] / S + X0) * K - shift
    return left, right


def zone_for(ch, left, x_height, cap_height):
    """The rows a letter is spaced over: x-height for lowercase, cap height
    for capitals and figures, a mark's own height for marks."""
    if ch.islower():
        return (ROWS >= 0) & (ROWS <= x_height)
    if ch.isupper() or ch.isdigit():
        return (ROWS >= 0) & (ROWS <= cap_height)
    ink = ~np.isnan(left)
    return ink if ink.any() else (ROWS >= 0) & (ROWS <= x_height)


def side_white(edge, zone, depth, sign):
    """How far, on average, the ink sits in from the letter's outermost
    point over its zone, each row counted at most `depth` deep."""
    ink = edge[zone]
    extreme = np.nanmin(ink) if sign < 0 else np.nanmax(ink)
    d = (ink - extreme) * -sign
    d = np.where(np.isnan(d), depth, np.minimum(d, depth))
    return float(d.mean()), float(extreme)


# ---------------------------------------------------------------- font

def glyph_name(ch):
    cp = ord(ch)
    return UV2AGL.get(cp, f'uni{cp:04X}')


def notdef(width):
    pen = T2CharStringPen(width, None)
    for (x0, y0, x1, y1), outer in (((60, 0, width - 60, 600), True), ((110, 50, width - 110, 550), False)):
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        if not outer:
            pts.reverse()
        pen.moveTo(pts[0])
        for p in pts[1:]:
            pen.lineTo(p)
        pen.closePath()
    return pen.getCharString()


def kerning(glyphs, strength=0.55, floor=80):
    """Pair adjustments where two shapes leave a hole or can tuck together:
    on the rows where both letters have ink inside both spacing zones (so an
    ascender beside a short letter doesn't count), the closest the two come is
    compared with the gap their spacing sidebearings give (two straight
    stems meet at exactly that; tails and hooks outside the spacing zone,
    like j's, don't count). A hole wider than that (T o, L T, P ., r ., " A)
    is closed by half its excess; pairs that already meet are left alone."""
    kernable = [c for c in glyphs if c.isalnum() or c in '.,:;\'"\u2018\u2019\u201c\u201d-\u2013\u2014()?!/&']
    pairs = {}
    for a in kernable:
        ga = glyphs[a]
        ra = ga['adv'] - ga['right']                # white right of a, per row
        for b in kernable:
            gb = glyphs[b]
            lb = gb['left']                         # white left of b, per row
            both = ~np.isnan(ra) & ~np.isnan(lb) & ga['zone'] & gb['zone']
            if both.sum() < 3:
                continue
            closest = float((ra + lb)[both].min())
            usual = ga['zsbR'] + gb['zsbL']
            excess = closest - usual
            # Over a short shared band (a period beside an o) every round
            # shape looks like a hole; ask for a deeper one before kerning.
            short = both.sum() * 8 < 0.33 * 430
            if excess < (floor * 1.75 if short else floor):
                continue
            k = -int(round(excess * strength / 5) * 5)
            # Between two lowercase letters a hole is never as deep as under
            # a T or after an r before a period, so keep those pairs gentle.
            pairs[(a, b)] = max(-40 if a.islower() and b.islower() else -160, k)
    return pairs


def build(key):
    style = STYLES[key]()
    family = style.family
    ps = family.replace(' ', '') + '-Regular'
    slant = math.tan(math.radians(style.lean))

    glyphs = {}          # name -> dict(rec, adv, left, right, ...)
    by_char = {}         # char -> its default glyph's entry
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        for ch in ALL:
            variants = style.alternates if ch.islower() else 0
            for v in range(variants + 1):
                img = Image.new('L', (int(W * S), int(H * S)), 0)
                img = style.draw(ch, img, v)
                rec = trace(img, tmp, style.speck, style.smooth)
                if bounds(rec) is None:
                    print(f'  {ch!r}: empty, skipped')
                    continue
                left, right = profile(img, slant)
                name = glyph_name(ch) + (f'.alt{v}' if v else '')
                glyphs[name] = {'ch': ch, 'rec': rec, 'left': left, 'right': right, 'variant': v}
                if v == 0:
                    by_char[ch] = glyphs[name]

    # Measure the flat tops of x and H for the x-height and cap height.
    def top(ch):
        return bounds(by_char[ch]['rec'])[3]
    x_height = round(top('x') if not slant else top('z'))
    cap_height = round(top('H'))

    if style.mono:
        for g in glyphs.values():
            xmin, _, xmax, _ = bounds(g['rec'])
            g['adv'] = style.advance
            g['dx'] = (style.advance - (xmax - xmin)) / 2 - xmin
    else:
        depth = 0.15 * x_height
        for g in glyphs.values():
            ch = g['ch']
            zone = zone_for(ch, g['left'], x_height, cap_height)
            target = style.lower_side if (ch.islower() or not ch.isalnum()) else style.upper_side
            wl, xl = side_white(g['left'], zone, depth, -1)
            wr, xr = side_white(g['right'], zone, depth, +1)
            # Straight sides keep the full space; round and open ones give
            # back what their own shape already leaves.
            sbl, sbr = target - wl * 0.6, target - wr * 0.6
            if ch in '\'"‘’“”':
                sbl, sbr = max(sbl, 25), max(sbr, 25)
            g['dx'] = sbl - xl
            g['adv'] = round(xr - xl + sbl + sbr)
            g['zsbL'], g['zsbR'], g['zone'] = sbl, sbr, zone
        # Math signs share one width, centred, so sums line up.
        math_signs = [g for g in glyphs.values() if g['ch'] in '+=<>\u00d7~-']
        cell = max(g['adv'] for g in math_signs if g['ch'] != '-')
        for g in math_signs:
            if g['ch'] == '-':
                continue
            xmin, _, xmax, _ = bounds(g['rec'])
            g['dx'] = (cell - (xmax - xmin)) / 2 - xmin
            g['adv'] = cell
    for g in glyphs.values():
        g['left'] = g['left'] + g['dx']
        g['right'] = g['right'] + g['dx']
        g['sbL'] = np.nanmin(g['left']) if not np.all(np.isnan(g['left'])) else 0
        g['sbR'] = g['adv'] - (np.nanmax(g['right']) if not np.all(np.isnan(g['right'])) else g['adv'])

    pairs = {}
    if not style.mono:
        chars = {g['ch']: g for g in glyphs.values() if g['variant'] == 0}
        pairs = kerning(chars)

    # ---- outlines
    order = ['.notdef', 'space', 'uni00A0'] + sorted(glyphs, key=lambda n: (ord(glyphs[n]['ch']), glyphs[n]['variant']))
    charstrings, metrics, cmap = {}, {}, {32: 'space', 160: 'uni00A0'}
    nd = style.advance if style.mono else 500    # monospace: every glyph one width
    charstrings['.notdef'] = notdef(nd)
    metrics['.notdef'] = (nd, 60)
    for sp in ('space', 'uni00A0'):
        charstrings[sp] = T2CharStringPen(style.space, None).getCharString()
        metrics[sp] = (style.space, 0)
    y_min, y_max = 0, 0
    for name, g in glyphs.items():
        pen = T2CharStringPen(g['adv'], None)
        moved = RecordingPen()
        g['rec'].replay(TransformPen(moved, (1, 0, 0, 1, g['dx'], 0)))
        moved.replay(ExtremaPen(RoundingPen(pen)))
        charstrings[name] = pen.getCharString()
        b = bounds(moved)
        metrics[name] = (g['adv'], math.floor(b[0]))
        y_min, y_max = min(y_min, b[1]), max(y_max, b[3])
        if g['variant'] == 0:
            cmap[ord(g['ch'])] = name

    TYPO_ASC = round((LINE + cap_height) / 2)
    TYPO_DESC = TYPO_ASC - LINE
    fb = FontBuilder(1000, isTTF=False)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupCFF(ps, {'FullName': family, 'FamilyName': family, 'Weight': 'Regular'}, charstrings, {})
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(
        ascent=TYPO_ASC, descent=TYPO_DESC, lineGap=0, caretSlopeRise=1, caretSlopeRun=0)
    fb.setupNameTable({
        'familyName': family,
        'styleName': 'Regular',
        'uniqueFontIdentifier': f'{VERSION:.3f};{ps}',
        'fullName': f'{family} Regular',
        'psName': ps,
        'version': f'Version {VERSION:.3f}',
        'copyright': 'Copyright 2026 The Pinboard Fonts Project Authors (https://github.com/zjlgdx/pinboard-fonts)',
        'vendorURL': 'https://github.com/zjlgdx/pinboard-fonts',
        'licenseDescription': 'This Font Software is licensed under the SIL Open Font License, Version 1.1.',
        'licenseInfoURL': 'https://openfontlicense.org',
    }, mac=False)
    us = glyphs['underscore']
    ub = bounds(us['rec'])
    thick = round(ub[3] - ub[1])
    fb.setupOS2(
        version=4, usWeightClass=400, usWidthClass=5,
        fsSelection=(1 << 6) | (1 << 7),          # REGULAR, USE_TYPO_METRICS
        sTypoAscender=TYPO_ASC, sTypoDescender=TYPO_DESC, sTypoLineGap=0,
        usWinAscent=math.ceil(y_max), usWinDescent=math.ceil(-y_min),
        sxHeight=x_height, sCapHeight=cap_height,
        yStrikeoutSize=thick, yStrikeoutPosition=round(x_height * 0.55),
        achVendID='    ', fsType=0,
        usDefaultChar=0, usBreakChar=32, usMaxContext=2,
    )
    fb.setupPost(keepGlyphNames=False, isFixedPitch=1 if style.mono else 0,
                 italicAngle=0, underlinePosition=round(ub[3]), underlineThickness=thick)
    font = fb.font
    font['head'].fontRevision = VERSION
    from fontTools.ttLib.tables.O_S_2f_2 import Panose
    p = Panose()
    (p.bFamilyType, p.bSerifStyle, p.bWeight, p.bProportion, p.bContrast, p.bStrokeVariation,
     p.bArmStyle, p.bLetterForm, p.bMidline, p.bXHeight) = style.panose
    os2 = font['OS/2']
    os2.panose = p
    os2.recalcUnicodeRanges(font)
    os2.recalcCodePageRanges(font)
    os2.recalcAvgCharWidth(font)

    # ---- features: alternates, then kerning
    fea = ['languagesystem DFLT dflt;', 'languagesystem latn dflt;']
    if style.alternates:
        lower = [glyph_name(c) for c in ALL if c.islower()]
        fea += [f'@cycle0 = [{" ".join(lower)}];']
        for v in range(1, style.alternates + 1):
            fea += [f'@cycle{v} = [{" ".join(n + f".alt{v}" for n in lower)}];',
                    f'lookup to_alt{v} {{ sub @cycle0 by @cycle{v}; }} to_alt{v};']
        # Each lowercase letter after another takes the next drawing in turn:
        # "book" is written o, o.alt1 -- never the same o twice in a row.
        rules = [f"  sub @cycle{v} @cycle0' lookup to_alt{v + 1};" for v in range(style.alternates - 1, 0, -1)]
        rules.append("  sub @cycle0 @cycle0' lookup to_alt1;")
        fea += ['feature calt {'] + rules + ['} calt;']
    if pairs:
        variants = {}
        for name, g in glyphs.items():
            variants.setdefault(g['ch'], []).append(name)
        fea.append('feature kern {')
        for (a, b), k in sorted(pairs.items()):
            fea.append(f'  pos [{" ".join(variants[a])}] [{" ".join(variants[b])}] {k};')
        fea.append('} kern;')
    addOpenTypeFeaturesFromString(font, '\n'.join(fea))

    OUT.mkdir(exist_ok=True)
    otf = OUT / f'{ps}.otf'
    font.save(otf)
    w = TTFont(otf)
    w.flavor = 'woff2'
    w.save(OUT / f'{ps}.woff2')
    print(f'{family}: {len(order)} glyphs, {len(pairs)} kerning pairs, '
          f'x-height {x_height}, cap height {cap_height} -> {otf.name}, {otf.stat().st_size // 1024} KB')


if __name__ == '__main__':
    for key in (sys.argv[1:] or list(STYLES)):
        build(key)
