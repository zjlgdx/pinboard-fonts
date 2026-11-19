"""Box drawing and block elements for Yinni, drawn to the cell.

These are not written with a pen: a terminal sets them edge to edge, so
every line has to meet the next cell's exactly. Each glyph fills the whole
monospace cell, 0 to the advance across and the typo descender to the typo
ascender up and down (the line box, as terminals lay out lines), so lines
join across both columns and rows.

The box-drawing glyphs come from their Unicode names: which arms a glyph
has (left, right, up, down) and how heavy each one is (light, heavy or
double), plus dashes, arcs, diagonals and half lines.
"""

import math
import unicodedata

from booleanOperations import BooleanOperationManager
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.pointPen import PointToSegmentPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.reverseContourPen import ReverseContourPen

KAPPA = 0.5523


class Poly:
    """A closed polygon that booleanOperations can read."""

    def __init__(self, pts):
        self.pts = [(round(x), round(y)) for x, y in pts]

    def __len__(self):
        return len(self.pts)

    def drawPoints(self, pen):
        pen.beginPath()
        for p in self.pts:
            pen.addPoint(p, 'line')
        pen.endPath()


def rect(x0, y0, x1, y1):
    return Poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def contours(rec):
    out, cur = [], []
    for op, args in rec.value:
        cur.append((op, args))
        if op in ('closePath', 'endPath'):
            out.append(cur)
            cur = []
    return out


def area(contour):
    r = RecordingPen()
    r.value = contour
    a = AreaPen()
    r.replay(a)
    return a.value


def inside(pt, contour):
    """Even-odd test of pt against a contour's on-curve polygon."""
    pts = [args[-1] for op, args in contour if args]
    x, y = pt
    hit = False
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            hit = not hit
    return hit


def oriented(rec):
    """Outer contours counter-clockwise, holes clockwise, as CFF expects."""
    cs = contours(rec)
    out = RecordingPen()
    for i, c in enumerate(cs):
        probe = next(args[-1] for op, args in c if args)
        depth = sum(1 for j, o in enumerate(cs) if j != i and inside(probe, o))
        want_positive = depth % 2 == 0
        r = RecordingPen()
        r.value = c
        if (area(c) > 0) == want_positive:
            r.replay(out)
        else:
            r.replay(ReverseContourPen(out))
    return out


def union(polys, subtract=()):
    rec = RecordingPen()
    pen = PointToSegmentPen(rec)
    if subtract:
        BooleanOperationManager.difference(list(polys), list(subtract), pen)
    else:
        BooleanOperationManager.union(list(polys), pen)
    return oriented(rec)


# ---------------------------------------------------------------- box drawing

DIRS = ('LEFT', 'RIGHT', 'UP', 'DOWN')
WEIGHTS = {'LIGHT': 'L', 'SINGLE': 'L', 'HEAVY': 'H', 'DOUBLE': 'D'}


def parse(name):
    """'DOWN LIGHT AND RIGHT HEAVY' -> {'DOWN': 'L', 'RIGHT': 'H'}, plus how
    many dashes, and whether the corner is an arc."""
    words = name.split()
    dashes = 0
    if 'DASH' in words:
        k = words.index('DASH')
        dashes = {'DOUBLE': 2, 'TRIPLE': 3, 'QUADRUPLE': 4}[words[k - 1]]
        del words[k - 1:k + 1]
    arc = 'ARC' in words
    words = [w for w in words if w not in ('ARC', 'AND')]
    arms, pending, prefix = {}, [], None
    # 'LIGHT LEFT AND HEAVY RIGHT' (U+257C-257F): each weight leads its arm.
    leading = len(words) == 4 and words[0] in WEIGHTS and words[2] in WEIGHTS
    if leading:
        return {words[1]: WEIGHTS[words[0]], words[3]: WEIGHTS[words[2]]}, dashes, arc
    for w in words:
        if w in WEIGHTS:
            if pending:
                for d in pending:
                    arms[d] = WEIGHTS[w]
                pending = []
            else:
                prefix = WEIGHTS[w]
        elif w == 'HORIZONTAL':
            pending += ['LEFT', 'RIGHT']
        elif w == 'VERTICAL':
            pending += ['UP', 'DOWN']
        elif w in DIRS:
            pending.append(w)
        else:
            raise ValueError(f'unknown word {w!r} in {name!r}')
    for d in pending:
        arms[d] = prefix
    return arms, dashes, arc


class Cell:
    def __init__(self, adv, asc, desc, light):
        self.adv, self.asc, self.desc = adv, asc, desc
        self.c = adv // 2
        self.m = round((asc + desc) / 2)
        light = round(light / 2) * 2
        self.w = {'L': light, 'H': round(light * 1.9 / 2) * 2}
        self.dw = round(light * 0.8 / 2) * 2           # each line of a double
        self.g = round(light * 1.3)                     # its offset from centre

    # Each arm's extent along its own axis, from the cell edge to `end`.
    def span(self, d, end):
        if d == 'LEFT':
            return 0, end
        if d == 'RIGHT':
            return end, self.adv
        if d == 'DOWN':
            return self.desc, end
        return end, self.asc

    def toward(self, d, base, by):
        """base moved `by` past the centre line, away from arm d's edge."""
        return base + by if d in ('LEFT', 'DOWN') else base - by

    def box(self, arms):
        c, m, g, dw = self.c, self.m, self.g, self.dw
        horiz = {'LEFT', 'RIGHT'}
        polys = []
        for d, wt in arms.items():
            vertical = d in ('UP', 'DOWN')
            centre = m if vertical else c                  # where this arm meets the cross axis
            opposite = {'LEFT': 'RIGHT', 'RIGHT': 'LEFT', 'UP': 'DOWN', 'DOWN': 'UP'}[d]
            perp = [p for p in (('LEFT', 'RIGHT') if vertical else ('UP', 'DOWN')) if p in arms]
            if wt == 'D':
                # Two lines, at -g and +g across the arm.
                for side in (-1, 1):
                    # The perpendicular arm on this line's side, and the other one.
                    if vertical:
                        side_arm = 'LEFT' if side < 0 else 'RIGHT'
                        other_arm = 'RIGHT' if side < 0 else 'LEFT'
                    else:
                        side_arm = 'DOWN' if side < 0 else 'UP'
                        other_arm = 'UP' if side < 0 else 'DOWN'
                    sw, ow = arms.get(side_arm), arms.get(other_arm)
                    if sw == 'D':           # turn the corner on the near line
                        end = self.toward(d, centre - (g if d in ('LEFT', 'DOWN') else -g), dw / 2)
                    elif sw:                # a single line on this side: run into it
                        end = self.toward(d, centre, self.w[sw] / 2)
                    elif opposite in arms:  # straight through
                        end = centre
                    elif ow == 'D':         # outer corner: out to the far line
                        end = self.toward(d, centre + (g if d in ('LEFT', 'DOWN') else -g), dw / 2)
                    elif ow:
                        end = self.toward(d, centre, self.w[ow] / 2)
                    else:
                        end = centre
                    a, b = self.span(d, end)
                    off = (c if vertical else m) + side * g
                    polys.append(rect(off - dw / 2, a, off + dw / 2, b) if vertical
                                 else rect(a, off - dw / 2, b, off + dw / 2))
            else:
                w = self.w[wt]
                doubles = [p for p in perp if arms[p] == 'D']
                if doubles and opposite not in arms:
                    # Into double lines: stop on the near one if they run
                    # straight across, reach the far one if they turn here.
                    if len(doubles) == 2:
                        end = self.toward(d, centre - (g if d in ('LEFT', 'DOWN') else -g), dw / 2)
                    else:
                        end = self.toward(d, centre + (g if d in ('LEFT', 'DOWN') else -g), dw / 2)
                else:
                    reach = max([self.w[arms[p]] / 2 for p in perp if arms[p] != 'D']
                                + [g + dw / 2 for p in doubles] + [0])
                    end = self.toward(d, centre, reach)
                a, b = self.span(d, end)
                axis = c if vertical else m
                polys.append(rect(axis - w / 2, a, axis + w / 2, b) if vertical
                             else rect(a, axis - w / 2, b, axis + w / 2))
        return union(polys)

    def dashes(self, arms, n):
        (d, wt), = [(d, w) for d, w in arms.items() if d in ('LEFT', 'UP')]
        w = self.w[wt]
        polys = []
        if d == 'LEFT':             # horizontal dashes
            seg = self.adv / n
            gap = seg * 0.32
            for i in range(n):
                polys.append(rect(i * seg + gap / 2, self.m - w / 2, (i + 1) * seg - gap / 2, self.m + w / 2))
        else:
            h = self.asc - self.desc
            seg = h / n
            gap = seg * 0.32
            for i in range(n):
                polys.append(rect(self.c - w / 2, self.desc + i * seg + gap / 2,
                                  self.c + w / 2, self.desc + (i + 1) * seg - gap / 2))
        return union(polys)

    def arc(self, arms):
        """A rounded corner: a quarter circle of half the cell's width, its
        straight run reaching the cell edge."""
        w = self.w['L']
        r = self.c
        sx = 1 if 'RIGHT' in arms else -1      # which way the horizontal arm goes
        sy = 1 if 'UP' in arms else -1         # which way the vertical arm goes
        c, m = self.c, self.m
        ey = self.asc if sy > 0 else self.desc
        ex = self.adv if sx > 0 else 0
        cx, cy = c + sx * r, m + sy * r         # the arc's centre
        rec = RecordingPen()
        # Outer edge: from the vertical arm's far side round to the horizontal arm's far side.
        ro, ri = r + w / 2, r - w / 2
        def quarter(rad, start_vertical):
            # From the vertical tangent point to the horizontal one (or back).
            p_v = (cx - sx * rad, cy)
            p_h = (cx, cy - sy * rad)
            if start_vertical:
                return p_v, (p_v[0], p_v[1] - sy * KAPPA * rad), (p_h[0] - sx * KAPPA * rad, p_h[1]), p_h
            return p_h, (p_h[0] - sx * KAPPA * rad, p_h[1]), (p_v[0], p_v[1] - sy * KAPPA * rad), p_v
        o0, o1, o2, o3 = quarter(ro, True)
        i0, i1, i2, i3 = quarter(ri, False)
        rec.moveTo((o0[0], ey))
        rec.lineTo(o0)
        rec.curveTo(o1, o2, o3)
        rec.lineTo((ex, o3[1]))
        rec.lineTo((ex, i0[1]))
        rec.lineTo(i0)
        rec.curveTo(i1, i2, i3)
        rec.lineTo((i3[0], ey))
        rec.closePath()
        rounded, last = RecordingPen(), None
        for op, args in rec.value:
            args = [(round(x), round(y)) for x, y in args]
            if op == 'lineTo' and args[0] == last:
                continue                # the straight run is empty when r is half the cell
            getattr(rounded, op)(*args)
            last = args[-1] if args else last
        return oriented(rounded)

    def diagonal(self, which):
        w = self.w['L']
        h = self.asc - self.desc
        # Half the stroke, measured along the row.
        dx = w / 2 * math.hypot(self.adv, h) / h
        a, b, w_, d_ = self.asc, self.desc, self.adv, dx
        up = [(-d_, b), (d_, b), (w_ + d_, a), (w_ - d_, a)]
        down = [(-d_, a), (d_, a), (w_ + d_, b), (w_ - d_, b)]
        if which != 'CROSS':
            return union([Poly(up if which == 'UP' else down)])
        # Clipper splits a crossing into two touching halves; draw the X as
        # one outline, its four inner corners where the edges cross.
        e = d_ * h / w_
        f = d_
        x = [(-d_, b), (d_, b), (self.c, self.m - e), (w_ - d_, b), (w_ + d_, b), (self.c + f, self.m),
             (w_ + d_, a), (w_ - d_, a), (self.c, self.m + e), (d_, a), (-d_, a), (self.c - f, self.m)]
        return union([Poly(x)])

    # ------------------------------------------------------------ blocks

    def block(self, name):
        x0, x1, y0, y1 = 0, self.adv, self.desc, self.asc
        h = y1 - y0
        eighths = {'ONE': 1, 'TWO': 2, 'THREE': 3, 'FOUR': 4, 'FIVE': 5, 'SIX': 6, 'SEVEN': 7}
        words = name.split()
        if name == 'FULL BLOCK':
            return union([rect(x0, y0, x1, y1)])
        if name.startswith('QUADRANT'):
            q = {'UPPER LEFT': (x0, self.m, self.c, y1), 'UPPER RIGHT': (self.c, self.m, x1, y1),
                 'LOWER LEFT': (x0, y0, self.c, self.m), 'LOWER RIGHT': (self.c, y0, x1, self.m)}
            parts = name[len('QUADRANT '):].split(' AND ')
            return union([rect(*q[p]) for p in parts])
        if words[-1] == 'SHADE':
            return self.shade(words[0])
        frac = 0.5 if 'HALF' in words else eighths[words[1]] / 8
        side = words[0]
        if side == 'LOWER':
            return union([rect(x0, y0, x1, y0 + round(h * frac))])
        if side == 'UPPER':
            return union([rect(x0, y1 - round(h * frac), x1, y1)])
        if side == 'LEFT':
            return union([rect(x0, y0, x0 + round(self.adv * frac), y1)])
        if side == 'RIGHT':
            return union([rect(x1 - round(self.adv * frac), y0, x1, y1)])
        raise ValueError(name)

    def shade(self, kind):
        """Staggered dots that tile across cells: light 25%, medium 49%, dark
        the light pattern cut out of a full block."""
        px, rows = self.adv / 6, 10
        py = (self.asc - self.desc) / rows
        size = {'LIGHT': 0.5, 'MEDIUM': 0.7, 'DARK': 0.5}[kind]
        dots = []
        for r in range(rows):
            off = 0 if r % 2 == 0 else px / 2
            for k in range(6):
                x = k * px + off + (px * (1 - size)) / 2
                y = self.desc + r * py + (py * (1 - size)) / 2
                w = px * size
                if x + w > self.adv + 0.5:      # wraps: split at the edge
                    dots.append(rect(x, y, self.adv, y + py * size))
                    dots.append(rect(0, y, x + w - self.adv, y + py * size))
                else:
                    dots.append(rect(x, y, x + w, y + py * size))
        if kind == 'DARK':
            return union([rect(0, self.desc, self.adv, self.asc)], subtract=dots)
        return union(dots)


def glyphs(adv, asc, desc, light):
    """{char: RecordingPen} for U+2500-257F, U+2580-259F and U+23BF."""
    cell = Cell(adv, asc, desc, light)
    out = {}
    for cp in range(0x2500, 0x2580):
        ch = chr(cp)
        name = unicodedata.name(ch)[len('BOX DRAWINGS '):]
        if 'DIAGONAL' in name:
            which = 'CROSS' if 'CROSS' in name else ('UP' if 'UPPER RIGHT' in name else 'DOWN')
            out[ch] = cell.diagonal(which)
            continue
        arms, dashes, arc = parse(name)
        if arc:
            out[ch] = cell.arc(arms)
        elif dashes:
            out[ch] = cell.dashes(arms, dashes)
        else:
            out[ch] = cell.box(arms)
    for cp in range(0x2580, 0x25A0):
        out[chr(cp)] = cell.block(unicodedata.name(chr(cp)))
    # Claude Code's result marker: a light corner that joins the line above.
    out['⎿'] = cell.box({'UP': 'L', 'RIGHT': 'L'})
    out.update(powerline(adv, asc, desc, light))
    return out


def powerline(adv, asc, desc, light):
    """Powerline's separators (U+E0B0-E0B3): solid and outline arrowheads
    from the bottom of the line to its top, one cell wide, so a prompt's
    coloured segments meet edge to edge."""
    mid = (asc + desc) / 2
    solid = Poly([(0, desc), (adv, mid), (0, asc)])

    def chevron():
        # The outline: two strips of the light line's weight along the edges
        # the solid one has, meeting in a point at the cell's right side.
        t = light / 2
        k = math.hypot(adv, mid - desc) / adv      # vertical half-width of a slanted strip
        return [Poly([(0, desc - t * k), (adv, mid - t * k), (adv, mid + t * k), (0, desc + t * k)]),
                Poly([(0, asc - t * k), (adv, mid - t * k), (adv, mid + t * k), (0, asc + t * k)])]

    def flipped(polys):
        return [Poly([(adv - x, y) for x, y in reversed(p.pts)]) for p in polys]

    return {'\ue0b0': union([solid]), '\ue0b1': clipped(chevron(), adv, asc, desc),
            '\ue0b2': union(flipped([solid])), '\ue0b3': clipped(flipped(chevron()), adv, asc, desc)}


def clipped(polys, adv, asc, desc):
    """The polygons' union, cut to the cell."""
    rec = RecordingPen()
    BooleanOperationManager.intersection(list(polys), [rect(0, desc, adv, asc)], PointToSegmentPen(rec))
    return oriented(rec)
