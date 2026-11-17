"""Pinboard's own letterforms, as pen strokes.

Each glyph is an SVG path of the pen's centre line, drawn on a 1000-unit
canvas with y pointing down: the cap line and figures sit at y=50, the
x-height at y=250, the baseline at y=750 and the descender at y=960.
Ascenders reach y=40. A dot is a tiny stroke (`l2 8`), which the round
pen turns into a dot.

The same skeletons are written with different pens (a ballpoint, a chisel
marker) to make different fonts.
"""

LOWER = {
    'a': 'M380 340 C350 270 260 250 200 290 C120 350 115 650 190 725 C260 790 360 720 385 600 M385 255 L390 750',
    'b': 'M110 40 L110 750 M110 520 C140 300 400 260 410 500 C420 740 160 790 112 640',
    'c': 'M390 320 C330 240 180 250 140 380 C100 520 150 740 290 750 C350 755 385 720 400 690',
    'd': 'M390 40 L390 750 M390 480 C350 260 120 280 110 500 C100 740 340 790 390 600',
    'e': 'M120 500 L390 490 C400 330 300 250 230 260 C130 275 105 450 115 560 C130 720 260 770 400 690',
    'f': 'M330 70 C280 20 190 30 180 140 L180 750 M80 280 L320 280',
    'g': 'M390 320 C330 240 150 260 125 420 C105 600 300 680 385 520 M390 260 L390 820 C385 960 200 990 120 900',
    'h': 'M110 40 L110 750 M110 480 C150 300 380 240 390 450 L390 750',
    'i': 'M200 260 L200 750 M200 118 l2 8',
    'j': 'M260 260 L260 850 C255 960 140 980 80 910 M260 118 l2 8',
    'k': 'M110 40 L110 750 M370 270 L120 560 M210 470 L390 750',
    'l': 'M160 40 L160 690 C160 740 200 760 240 745',
    'm': 'M100 260 L100 750 M100 450 C130 270 290 250 300 420 L300 750 M300 430 C330 270 500 250 510 430 L510 750',
    'n': 'M110 260 L110 750 M110 460 C150 280 380 240 390 450 L390 750',
    'o': 'M260 262 C110 262 95 480 110 560 C130 700 190 750 260 750 C380 750 420 620 415 500 C410 360 360 262 260 262 Z',
    'p': 'M110 260 L110 960 M110 500 C140 280 400 250 410 480 C420 740 160 790 112 640',
    'q': 'M390 260 L390 960 L440 920 M390 480 C350 260 120 280 110 500 C100 740 340 790 390 600',
    'r': 'M110 260 L110 750 M110 480 C140 320 250 255 360 290',
    's': 'M370 310 C320 250 160 240 140 340 C120 450 370 470 380 600 C395 740 180 790 110 690',
    't': 'M190 90 L190 690 C190 745 240 765 300 735 M80 270 L330 260',
    'u': 'M110 260 L110 600 C115 780 360 770 390 560 M390 260 L390 750',
    'v': 'M90 260 L240 750 L390 260',
    'w': 'M70 260 L180 750 L300 380 L420 750 L530 260',
    'x': 'M100 260 L390 750 M390 260 L100 750',
    'y': 'M90 260 L245 720 M400 260 L220 870 C190 950 130 960 90 930',
    'z': 'M110 270 L390 265 L100 745 L400 740',
}

UPPER = {
    'A': 'M80 750 L300 50 L520 750 M160 500 L440 500',
    'B': 'M110 750 L110 50 C340 40 450 110 430 230 C410 360 230 380 110 380 C360 375 480 450 470 570 C460 720 280 755 110 750',
    'C': 'M520 160 C440 35 280 15 180 110 C70 220 60 560 160 680 C260 790 440 770 530 650',
    'D': 'M110 50 L110 750 C400 760 510 600 510 400 C510 170 380 50 110 50',
    'E': 'M450 50 L110 50 L110 750 L460 750 M110 390 L390 390',
    'F': 'M450 50 L110 50 L110 750 M110 390 L380 390',
    'G': 'M520 160 C440 35 280 15 180 110 C70 220 60 560 160 680 C260 790 460 770 520 620 L520 450 L360 450',
    'H': 'M110 50 L110 750 M490 50 L490 750 M110 400 L490 400',
    'I': 'M200 50 L200 750 M100 50 L300 50 M100 750 L300 750',
    'J': 'M420 50 L420 580 C420 770 160 790 100 620',
    'K': 'M110 50 L110 750 M470 50 L120 470 M260 300 L490 750',
    'L': 'M110 50 L110 750 L440 750',
    'M': 'M90 750 L110 50 L320 520 L530 50 L550 750',
    'N': 'M110 750 L110 50 L480 750 L480 50',
    'O': 'M310 50 C120 50 70 260 75 420 C80 620 180 755 310 750 C450 745 545 610 540 400 C535 200 450 50 310 50 Z',
    'P': 'M110 750 L110 50 C350 40 470 110 460 240 C450 390 260 420 110 410',
    'Q': 'M310 50 C120 50 70 260 75 420 C80 620 180 755 310 750 C450 745 545 610 540 400 C535 200 450 50 310 50 Z M330 560 L540 790',
    'R': 'M110 750 L110 50 C350 40 470 110 460 240 C450 390 260 420 110 410 M270 410 L480 750',
    'S': 'M480 140 C420 37 220 17 150 110 C70 230 150 330 300 380 C460 430 520 520 470 640 C410 785 180 795 90 670',
    'T': 'M60 50 L520 50 M290 50 L290 750',
    'U': 'M100 50 L100 520 C100 720 210 755 300 755 C420 755 500 690 500 520 L500 50',
    'V': 'M70 50 L300 750 L530 50',
    'W': 'M50 50 L190 750 L340 250 L490 750 L630 50',
    'X': 'M80 50 L500 750 M500 50 L80 750',
    'Y': 'M70 50 L290 400 L510 50 M290 400 L290 750',
    'Z': 'M90 50 L490 50 L80 750 L500 750',
}

FIGURES = {
    '0': 'M260 50 C120 50 80 250 85 410 C90 620 160 750 260 750 C380 750 440 600 435 400 C430 200 380 50 260 50 Z',
    '1': 'M130 170 L260 50 L260 750 M130 750 L390 750',
    '2': 'M100 200 C120 70 260 30 340 70 C450 130 430 280 340 380 L90 750 L440 750',
    '3': 'M100 130 C180 30 400 40 410 180 C420 320 300 370 210 380 C380 380 450 470 440 590 C420 760 170 790 90 660',
    '4': 'M370 750 L370 50 L70 520 L460 520',
    '5': 'M420 50 L150 50 L120 360 C220 290 420 300 430 500 C440 720 210 790 90 680',
    '6': 'M400 90 C330 30 200 40 140 160 C70 300 80 600 160 700 C240 800 420 760 430 560 C440 400 300 360 200 400 C140 430 110 480 100 540',
    '7': 'M80 50 L440 50 L200 750 M170 400 L380 400',
    '8': 'M260 380 C130 360 110 220 150 130 C200 30 330 30 380 120 C430 220 380 360 260 380 C120 400 80 520 100 620 C130 750 380 770 420 620 C450 500 370 400 260 380 Z',
    '9': 'M420 300 C410 120 300 50 230 55 C110 65 80 200 100 290 C130 420 330 420 420 300 L400 750',
}

MARKS = {
    '.': 'M120 735 l2 8',
    ',': 'M130 725 C145 760 135 805 100 835',
    ':': 'M120 380 l2 8 M120 735 l2 8',
    ';': 'M130 380 l2 8 M130 725 C145 760 135 805 100 835',
    '!': 'M140 50 L140 560 M140 735 l2 8',
    '?': 'M90 170 C110 50 300 30 360 120 C420 220 330 300 260 360 C220 400 210 450 210 560 M210 735 l2 8',
    "'": 'M120 50 L110 220',
    '"': 'M100 50 L95 220 M200 50 L195 220',
    '-': 'M80 450 L300 450',
    '(': 'M260 20 C120 180 110 580 260 820',
    ')': 'M100 20 C240 180 250 580 100 820',
    '[': 'M260 20 L140 20 L140 820 L260 820',
    ']': 'M100 20 L220 20 L220 820 L100 820',
    '/': 'M380 20 L80 820',
    '&': 'M480 750 L180 280 C120 180 170 60 270 60 C370 60 380 190 300 260 L130 420 C40 520 90 760 260 750 C380 745 450 640 480 520',
    '@': 'M470 400 C470 300 380 270 320 300 C230 340 230 520 320 520 C400 520 450 440 460 330 L450 510 C460 560 560 560 580 430 C610 220 450 80 300 90 C140 100 60 280 80 450 C100 650 300 760 500 680',
    '#': 'M180 150 L150 700 M380 150 L350 700 M80 320 L480 320 M60 530 L460 530',
    '+': 'M260 280 L260 640 M80 460 L440 460',
    '=': 'M80 380 L420 380 M80 540 L420 540',
    '*': 'M250 120 L250 360 M140 170 L360 310 M360 170 L140 310',
    '%': 'M480 60 L100 760 M170 70 C90 70 90 260 170 260 C250 260 250 70 170 70 Z M410 560 C330 560 330 750 410 750 C490 750 490 560 410 560 Z',
    '$': 'M420 190 C370 110 200 100 150 180 C90 280 170 340 290 380 C430 420 470 500 430 600 C380 700 190 700 110 610 M270 30 L270 780',
    '_': 'M40 820 L460 820',
    '<': 'M420 250 L100 460 L420 670',
    '>': 'M100 250 L420 460 L100 670',
    '~': 'M80 470 C150 380 220 400 260 450 C300 500 380 520 440 430',
    '·': 'M110 450 l2 8',
    '—': 'M60 450 L640 450',
    '–': 'M60 450 L400 450',
    '’': 'M130 50 C145 90 135 150 100 200',
    '‘': 'M120 200 C100 160 110 100 145 50',
    '“': 'M120 200 C100 160 110 100 145 50 M230 200 C210 160 220 100 255 50',
    '”': 'M130 50 C145 90 135 150 100 200 M240 50 C255 90 245 150 210 200',
    '×': 'M110 330 L390 610 M390 330 L110 610',
    '\\': 'M80 20 L380 820',
    '|': 'M150 0 L150 980',
    '{': 'M280 20 C200 20 180 60 180 140 L180 330 C180 390 150 420 90 420 C150 420 180 450 180 510 L180 700 C180 780 200 820 280 820',
    '}': 'M100 20 C180 20 200 60 200 140 L200 330 C200 390 230 420 290 420 C230 420 200 450 200 510 L200 700 C200 780 180 820 100 820',
    '^': 'M90 330 L250 70 L410 330',
    '`': 'M120 60 L210 170',
    '\u2026': 'M100 735 l2 8 M300 735 l2 8 M500 735 l2 8',
    '\u00b0': 'M200 60 C130 60 110 110 110 150 C110 200 150 240 200 240 C250 240 290 200 290 150 C290 100 260 60 200 60 Z',
    '\u2022': 'M200 380 C170 380 150 400 150 430 C150 460 170 480 200 480 C230 480 250 460 250 430 C250 400 230 380 200 380 Z M200 425 l2 8',
}

ALL = {**UPPER, **LOWER, **FIGURES, **MARKS}

# Slab serifs the typewriter adds to the same skeletons.
TYPE_SERIFS = {
    '0': 'M258 395 l2 8',   # a dotted zero, so 0 and O never mix in a terminal
    'a': 'M390 750 L460 750',
    'b': 'M40 40 L110 40',
    'd': 'M320 40 L390 40 M390 750 L460 750',
    'f': 'M80 750 L300 750',
    'g': 'M390 260 L460 260',
    'h': 'M40 40 L110 40 M40 750 L180 750 M320 750 L460 750',
    'i': 'M120 260 L200 260 M100 750 L300 750',
    'j': 'M170 260 L260 260',
    'k': 'M40 40 L110 40 M40 750 L180 750 M300 270 L440 270 M330 750 L450 750',
    'l': 'M80 40 L160 40',
    'm': 'M40 260 L100 260 M40 750 L160 750 M240 750 L360 750 M450 750 L570 750',
    'n': 'M40 260 L110 260 M40 750 L180 750 M320 750 L460 750',
    'p': 'M40 260 L110 260 M40 960 L200 960',
    'q': 'M300 960 L390 960',
    'r': 'M40 260 L110 260 M40 750 L250 750',
    'u': 'M40 260 L110 260 M320 260 L390 260 M390 750 L460 750',
    'v': 'M30 260 L160 260 M320 260 L450 260',
    'w': 'M10 260 L140 260 M460 260 L590 260',
    'x': 'M40 260 L170 260 M320 260 L450 260 M40 750 L170 750 M320 750 L450 750',
    'y': 'M30 260 L160 260 M330 260 L460 260',
    'A': 'M20 750 L160 750 M440 750 L580 750',
    'B': 'M40 50 L110 50 M40 750 L110 750',
    'D': 'M40 50 L110 50 M40 750 L110 750',
    'E': 'M40 50 L110 50 M40 750 L110 750 M450 50 L450 130 M460 750 L460 670',
    'F': 'M40 50 L110 50 M40 750 L220 750 M450 50 L450 130',
    'H': 'M40 50 L180 50 M420 50 L560 50 M40 750 L180 750 M420 750 L560 750',
    'J': 'M330 50 L500 50',
    'K': 'M40 50 L180 50 M40 750 L180 750 M400 50 L540 50 M420 750 L550 750',
    'L': 'M40 50 L200 50 M40 750 L110 750 M440 750 L440 670',
    'M': 'M30 750 L160 750 M480 750 L610 750 M40 50 L110 50 M530 50 L600 50',
    'N': 'M40 50 L110 50 M40 750 L180 750 M410 50 L550 50',
    'P': 'M40 50 L110 50 M40 750 L220 750',
    'R': 'M40 50 L110 50 M40 750 L180 750 M420 750 L540 750',
    'T': 'M60 50 L60 130 M520 50 L520 130 M200 750 L380 750',
    'U': 'M30 50 L170 50 M430 50 L570 50',
    'V': 'M0 50 L140 50 M460 50 L600 50',
    'W': 'M-10 50 L120 50 M560 50 L690 50',
    'X': 'M20 50 L150 50 M430 50 L560 50 M20 750 L150 750 M430 750 L560 750',
    'Y': 'M10 50 L140 50 M440 50 L570 50 M200 750 L380 750',
    'Z': 'M90 50 L90 130 M500 750 L500 670',
}


# ---------------------------------------------------------------- helpers

import math as _m
import re as _re
import unicodedata as _ud

_TOKEN = _re.compile(r'[MLCZFmlczf]|-?(?:\d+\.?\d*|\.\d+)')


def transform(d, f):
    """A skeleton path with every point moved by f((x, y)) -> (x, y), written
    in absolute commands. Dots (`l2 8`) stay dots wherever they land."""
    toks = _TOKEN.findall(d)
    out, i, cmd = [], 0, None
    cx = cy = sx = sy = 0.0
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]
            i += 1
            if cmd in 'ZzFf':
                out.append(cmd.upper())
                cx, cy = sx, sy
                continue
        n = 6 if cmd in 'Cc' else 2
        vals = [float(v) for v in toks[i:i + n]]
        i += n
        rel = cmd.islower()
        pts = [(vals[k] + (cx if rel else 0), vals[k + 1] + (cy if rel else 0)) for k in range(0, n, 2)]
        if cmd == 'l' and abs(vals[0]) + abs(vals[1]) < 20:
            out.append('l2 8')
        else:
            out.append(cmd.upper() + ' '.join(f'{v:.1f}'.rstrip('0').rstrip('.') for p in pts for v in f(p)))
        cx, cy = pts[-1]
        if cmd in 'Mm':
            sx, sy = cx, cy
            cmd = 'l' if rel else 'L'
    return ' '.join(out)


def scale(d, s, ox, oy, tx=0, ty=0):
    """d scaled by s about (ox, oy), then moved by (tx, ty)."""
    return transform(d, lambda p: (ox + (p[0] - ox) * s + tx, oy + (p[1] - oy) * s + ty))


def circle(cx, cy, rx, ry=None, end='Z'):
    """A closed ellipse as four quarter-arcs; end='F' fills it."""
    ry = rx if ry is None else ry
    k = 0.5523
    return (f'M{cx} {cy - ry} C{cx + k * rx:.1f} {cy - ry} {cx + rx} {cy - k * ry:.1f} {cx + rx} {cy} '
            f'C{cx + rx} {cy + k * ry:.1f} {cx + k * rx:.1f} {cy + ry} {cx} {cy + ry} '
            f'C{cx - k * rx:.1f} {cy + ry} {cx - rx} {cy + k * ry:.1f} {cx - rx} {cy} '
            f'C{cx - rx} {cy - k * ry:.1f} {cx - k * rx:.1f} {cy - ry} {cx} {cy - ry} {end}')


def leaves(cx, cy, n, r, w, start=90, hub=0.0, end='F'):
    """n teardrop spokes round (cx, cy): thin at the centre, round at the
    tip, each starting `hub` of the way out so the pen leaves a small eye."""
    import math
    out = []
    for k in range(n):
        a = math.radians(start + 360 * k / n)
        ux, uy = math.cos(a), -math.sin(a)          # outward, y down
        vx, vy = -uy, ux                            # across
        p = lambda t, s: (cx + ux * r * t + vx * w * s, cy + uy * r * t + vy * w * s)
        t0 = hub
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = p(t0, 0), p(t0 + (1 - t0) * 0.45, 0.55), p(1.08, 1.05), p(1.0, 0)
        (x4, y4), (x5, y5) = p(1.08, -1.05), p(t0 + (1 - t0) * 0.45, -0.55)
        out.append(f'M{x0:.1f} {y0:.1f} C{x1:.1f} {y1:.1f} {x2:.1f} {y2:.1f} {x3:.1f} {y3:.1f} '
                   f'C{x4:.1f} {y4:.1f} {x5:.1f} {y5:.1f} {x0:.1f} {y0:.1f} {end}')
    return ' '.join(out)


def star(cx, cy, n, r_out, r_in, end='F'):
    import math
    pts = []
    for k in range(2 * n):
        a = math.radians(90 + 180 * k / n)
        r = r_out if k % 2 == 0 else r_in
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
    return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + ' ' + end


def _rot180(d, cx, cy):
    return transform(d, lambda p: (2 * cx - p[0], 2 * cy - p[1]))


def _mirror(d, cx):
    return transform(d, lambda p: (2 * cx - p[0], p[1]))


# ---------------------------------------------------------------- accents

# Each mark's centre line, with the origin at the middle of its foot and y
# pointing down: (over a lowercase letter, over a capital). Capital marks are
# flatter, so they fit between the cap line and the line above.
MARK_SHAPES = {
    'grave':      ('M-50 -112 L34 0', 'M-72 -92 L38 0'),
    'acute':      ('M50 -112 L-34 0', 'M72 -92 L-38 0'),
    'circumflex': ('M-88 0 L0 -96 L88 0', 'M-100 0 L0 -74 L100 0'),
    'caron':      ('M-88 -96 L0 0 L88 -96', 'M-100 -74 L0 0 L100 -74'),
    'tilde':      ('M-100 -12 C-78 -78 -36 -82 -4 -50 C28 -18 72 -14 100 -84',
                   'M-108 -8 C-84 -64 -40 -68 -6 -40 C26 -12 76 -10 108 -66'),
    'dieresis':   ('M-76 -44 l2 8 M72 -44 l2 8', 'M-86 -34 l2 8 M82 -34 l2 8'),
    'ring':       (circle(0, -54, 50, 54), circle(0, -46, 52, 46)),
    'macron':     ('M-96 -40 L96 -40', 'M-110 -30 L110 -30'),
    'breve':      ('M-80 -96 C-70 28 70 28 80 -96', 'M-90 -72 C-80 22 80 22 90 -72'),
    'dotaccent':  ('M-1 -44 l2 8', 'M-1 -34 l2 8'),
    'hungarumlaut': ('M-30 -112 L-78 0 M78 -112 L30 0', 'M-30 -92 L-84 0 M86 -92 L32 0'),
    # Latvian ģ: a comma turned over the letter, foot down.
    'commaturned': ('M0 0 C-13 -30 -4 -68 26 -94',) * 2,
    # Hang from the foot of the letter, origin on the baseline.
    'cedilla':    ('M2 -12 L-8 58 C58 50 88 88 66 124 C46 154 -14 156 -56 134',) * 2,
    'ogonek':     ('M0 -6 C-36 40 -52 108 -2 126 C22 134 44 128 60 116',) * 2,
    # Hangs clear under the letter, origin at its top: the comma's own curve.
    'commabelow': ('M0 0 C13 30 4 68 -26 94',) * 2,
    # Czech and Slovak ď ľ ť Ľ: an apostrophe beside the ascender, origin at its top.
    'caronvert':  ('M0 0 C12 32 4 80 -24 120',) * 2,
}
COMBINING = {'\u0300': 'grave', '\u0301': 'acute', '\u0302': 'circumflex', '\u0303': 'tilde',
             '\u0304': 'macron', '\u0306': 'breve', '\u0307': 'dotaccent', '\u0308': 'dieresis',
             '\u030A': 'ring', '\u030B': 'hungarumlaut', '\u030C': 'caron',
             '\u0326': 'commabelow', '\u0327': 'cedilla', '\u0328': 'ogonek'}
BELOW = {'cedilla', 'ogonek', 'commabelow'}

# Combining marks (zero width, placed by GPOS anchors) and the class each
# attaches by. Over a capital, a mark above takes its flatter `.case` form.
COMBINING_MARKS = {**COMBINING, '\u0312': 'commaturned'}
ANCHOR = {name: ('bottom' if name == 'commabelow' else name if name in BELOW else 'top')
          for name in COMBINING_MARKS.values()}
STACK = 26      # skeleton units between two stacked marks


def _accent(ch):
    """(base letter, mark) for a letter made of one letter and one mark, as
    each language writes it: Latvian and Romanian cedillas are commas, and
    the caron beside an ascender is an apostrophe."""
    d = _ud.normalize('NFD', ch)
    if len(d) != 2 or d[1] not in COMBINING:
        return None
    base, mark = d[0], COMBINING[d[1]]
    if mark == 'cedilla' and base in 'GKLNRgklnr':
        mark = 'commaturned' if base == 'g' else 'commabelow'
    if mark == 'caron' and base in 'dltL':
        mark = 'caronvert'
    return base, mark


# Latin-1, Windows-1252 and Latin Extended-A letters made of a letter and one
# mark, plus Romanian ș ț.
ACCENTED = {}
for _cp in list(range(0xC0, 0x100)) + list(range(0x100, 0x180)) + [0x218, 0x219, 0x21A, 0x21B]:
    _a = _accent(chr(_cp))
    if _a:
        ACCENTED[chr(_cp)] = _a

# A mark over i or j sits on the dotless letter.
DOTLESS = {'i': 'M200 260 L200 750', 'j': 'M260 260 L260 850 C255 960 140 980 80 910'}

# Where a cedilla or ogonek hangs: under the foot of the curve or stem it
# grows from, not the middle of the box.
CEDILLA_X = {'c': 270, 'C': 330, 's': 240, 'S': 290, 't': 235, 'T': 290}
OGONEK_X = {'a': 390, 'A': 512, 'e': 300, 'E': 410, 'i': 202, 'I': 250, 'u': 390, 'U': 372}

# The stem an apostrophe caron stands beside.
CARON_STEM = {'d': 390, 'l': 160, 't': 190, 'L': 110}

# Marks over an ascender centre on its stem, not on the letter's body.
MARK_X = {('h', 'circumflex'): 150, ('L', 'acute'): 190}

# Spacing (legacy) accents: the same marks standing alone.
SPACING_MARKS = {'¨': 'dieresis', '´': 'acute', '¯': 'macron', '¸': 'cedilla',
                 'ˆ': 'circumflex', '˜': 'tilde', 'ˇ': 'caron', '˘': 'breve', '˙': 'dotaccent',
                 '˚': 'ring', '˛': 'ogonek', '˝': 'hungarumlaut'}


def mark_centre(d, lower):
    """The x a mark centres on: the middle of the letter's own body (x-height
    or cap height), so tails and ascenders don't pull it sideways."""
    lo, hi = (250, 750) if lower else (50, 750)
    xs = [x for x, y in _points(d) if lo - 1 <= y <= hi + 1]
    return (min(xs) + max(xs)) / 2


def _points(d):
    """The absolute points of a skeleton path (letters use relative commands
    only for dots, whose 2-unit step doesn't move anything)."""
    d = _re.sub(r'l-?[\d.]+ -?[\d.]+', '', d)
    nums = [float(t) for t in _TOKEN.findall(d) if not t.isalpha()]
    return list(zip(nums[0::2], nums[1::2]))


# ---------------------------------------------------------------- Latin-1 and Windows-1252

_FIG_SUP = lambda c, w=0.58, x=30: scale(FIGURES[c], w, 0, 50, x, 0)


def _frac(num, den):
    top = scale(FIGURES[num], 0.44, 0, 50, 30, 0)
    bottom = scale(FIGURES[den], 0.44, 0, 50, 330, 385)
    return f'{top} {bottom} M520 60 L170 740'


LATIN = {
    '¡': 'M140 265 l2 8 M140 440 L140 955',
    '¿': _rot180(MARKS['?'], 225, 500),
    '£': 'M420 150 C392 70 322 40 262 45 C172 55 146 140 156 240 L180 470 C190 600 162 690 90 750 L450 750 M80 410 L340 410',
    '¤': circle(250, 440, 140) + ' M151 341 L95 285 M349 341 L405 285 M151 539 L95 595 M349 539 L405 595',
    '¥': 'M70 50 L270 390 L470 50 M270 390 L270 750 M110 450 L430 450 M110 590 L430 590',
    '¦': 'M150 0 L150 410 M150 570 L150 980',
    '§': 'M370 120 C330 45 160 40 152 140 C142 250 372 280 372 400 C372 480 300 512 252 518 '
         'M252 282 C200 288 128 320 128 400 C128 520 350 552 350 660 C350 772 168 782 110 700',
    '©': circle(340, 400, 330) + ' ' + scale(UPPER['C'], 0.5, 295, 400, 50, 0),
    '®': circle(340, 400, 330) + ' ' + scale(UPPER['R'], 0.48, 295, 400, 50, 0),
    'ª': scale(LOWER['a'], 0.6, 0, 250, 20, -200) + ' M75 430 L265 430',
    'º': scale(LOWER['o'], 0.6, 0, 250, 20, -200) + ' M70 430 L275 430',
    '«': 'M230 310 L110 480 L230 650 M380 310 L260 480 L380 650',
    '»': 'M110 310 L230 480 L110 650 M260 310 L380 480 L260 650',
    '‹': 'M230 310 L110 480 L230 650',
    '›': 'M110 310 L230 480 L110 650',
    '¬': 'M80 400 L420 400 L420 570',
    '±': 'M260 200 L260 520 M80 360 L440 360 M80 650 L440 650',
    '²': _FIG_SUP('2'), '³': _FIG_SUP('3'), '¹': _FIG_SUP('1'),
    'µ': 'M110 260 L110 960 M110 600 C115 780 360 770 390 560 M390 260 L390 750',
    '¶': 'M310 60 L310 750 M440 60 L440 750 M460 60 L250 60 C130 60 80 140 80 230 C80 330 150 400 310 400',
    '¼': _frac('1', '4'), '½': _frac('1', '2'), '¾': _frac('3', '4'),
    '÷': 'M80 460 L440 460 M258 300 l2 8 M258 612 l2 8',
    'Æ': 'M50 750 L320 50 L620 50 M320 50 L320 750 L630 750 M320 390 L570 390 M150 500 L320 500',
    'Þ': 'M110 50 L110 750 M110 200 C350 190 470 260 460 380 C450 520 260 550 110 540',
    'ß': 'M110 750 L110 220 C110 90 180 40 262 40 C352 40 400 100 395 180 C390 262 320 292 262 322 '
         'C400 332 452 442 442 562 C432 702 332 762 222 737',
    'æ': 'M370 340 C340 270 260 250 200 290 C120 350 115 650 190 725 C260 790 350 720 370 600 '
         'M362 500 L630 490 C640 330 540 250 470 260 C370 275 345 450 355 560 C370 720 500 770 640 690',
    'ð': 'M260 300 C110 300 95 490 110 565 C130 700 190 750 260 750 C380 750 420 630 415 510 '
         'C410 330 340 160 190 50 M190 170 L380 95',
    'þ': 'M110 40 L110 960 M110 500 C140 280 400 250 410 480 C420 740 160 790 112 640',
    'ı': DOTLESS['i'],
    # What a lone combining mark is shown on.
    '◌': ' '.join(f'M{250 + 210 * _m.sin(_m.pi * k / 5) - 1:.0f} {500 - 210 * _m.cos(_m.pi * k / 5) - 4:.0f} l2 8'
                  for k in range(10)),
    'ȷ': DOTLESS['j'],
    # Latin Extended-A letters of their own
    'ĸ': 'M110 260 L110 750 M370 270 L120 560 M210 470 L390 750',
    'ŉ': "M80 50 C95 90 85 150 50 200 " + scale(LOWER['n'], 1, 0, 0, 90, 0),
    'Ŋ': 'M110 750 L110 50 L480 750 L480 50 M480 750 L480 830 C476 930 392 956 322 916',
    'ŋ': 'M110 260 L110 750 M110 460 C150 280 380 240 390 450 L390 850 C385 955 270 975 210 920',
    'ſ': 'M330 70 C280 20 190 30 180 140 L180 750',
    'Ĳ': UPPER['I'] + ' ' + scale(UPPER['J'], 1, 0, 0, 250, 0),
    'ĳ': LOWER['i'] + ' ' + scale(LOWER['j'], 1, 0, 0, 170, 0),
    # Windows-1252
    '€': 'M480 160 C420 70 340 45 280 50 C150 60 100 240 100 400 C100 590 170 750 300 750 '
         'C380 750 440 710 480 650 M40 330 L380 330 M40 470 L360 470',
    '‚': MARKS[','],
    '„': MARKS[','] + ' M240 725 C255 760 245 805 210 835',
    '†': 'M220 50 L220 820 M80 230 L360 230',
    '‡': 'M220 50 L220 820 M80 210 L360 210 M80 610 L360 610',
    '‰': MARKS['%'] + ' M600 560 C520 560 520 750 600 750 C680 750 680 560 600 560 Z',
    'Œ': 'M630 50 L330 50 L330 750 L640 750 M330 390 L570 390 M330 50 C140 45 70 230 75 410 C80 610 190 755 330 750',
    'œ': 'M240 262 C110 262 95 480 110 560 C130 700 180 750 240 750 C340 750 372 640 372 500 C372 360 330 262 240 262 Z '
         'M372 500 L640 490 C650 330 550 250 480 260 C385 275 360 450 370 560 C385 720 510 770 650 690',
    'ƒ': 'M400 90 C350 30 270 40 260 140 L210 860 C200 950 130 970 80 920 M120 300 L360 300',
    '™': 'M40 50 L280 50 M160 50 L160 330 M340 330 L350 50 L460 270 L570 50 L580 330',
    # Math signs, on the axis of + and =
    '−': 'M80 460 L440 460',
    '≠': MARKS['='] + ' M360 250 L160 670',
    '≤': 'M420 200 L100 370 L420 540 M100 650 L420 650',
    '≥': 'M100 200 L420 370 L100 540 M100 650 L420 650',
    '≈': 'M80 395 C150 305 220 325 260 375 C300 425 380 445 440 355 '
         'M80 565 C150 475 220 495 260 545 C300 595 380 615 440 525',
}

# Letters made from another letter plus a stroke: same hand, own spacing.
BUILT = {
    'Ð': ('D', 'M30 400 L250 400'),
    'Ø': ('O', 'M530 20 L90 785'),
    'ø': ('o', 'M445 225 L75 790'),
    '¢': ('c', 'M268 165 L252 835'),
    'Đ': ('D', 'M30 400 L250 400'),
    'đ': ('d', 'M290 140 L470 140'),
    'Ħ': ('H', 'M40 215 L560 215'),
    'ħ': ('h', 'M30 140 L250 140'),
    'Ł': ('L', 'M30 480 L250 300'),
    'ł': ('l', 'M70 480 L260 300'),
    'Ŧ': ('T', 'M150 400 L430 400'),
    'ŧ': ('t', 'M100 470 L290 470'),
    'Ŀ': ('L', 'M300 395 l2 8'),
    'ŀ': ('l', 'M330 445 l2 8'),
}

# Typewriter slabs for those letters, from the letters they grow from.
TYPE_SERIFS.update({
    'ı': TYPE_SERIFS['i'], 'ȷ': TYPE_SERIFS['j'], 'ſ': TYPE_SERIFS['f'],
    'ĸ': 'M40 260 L110 260 M40 750 L180 750 M300 270 L440 270 M330 750 L450 750',
    'ŉ': scale(TYPE_SERIFS['n'], 1, 0, 0, 90, 0),
    'Ŋ': 'M40 50 L110 50 M40 750 L180 750 M410 50 L550 50',
    'ŋ': 'M40 260 L110 260 M40 750 L180 750',
    'Ĳ': scale(TYPE_SERIFS['J'], 1, 0, 0, 250, 0),
    'ĳ': TYPE_SERIFS['i'] + ' ' + scale(TYPE_SERIFS['j'], 1, 0, 0, 170, 0),
})

# Pen weight per glyph, where a smaller drawing needs a finer line.
LIGHTER = {c: 0.8 for c in '¹²³ª º¼½¾™'}
LIGHTER.update({'©': 0.85, '®': 0.85, '◌': 0.6})

# ---------------------------------------------------------------- symbols

SYMBOLS = {
    '←': 'M540 460 L80 460 M235 315 L80 460 L235 605',
    '→': 'M80 460 L540 460 M385 315 L540 460 L385 605',
    '↑': 'M300 750 L300 170 M155 325 L300 170 L445 325',
    '↓': 'M300 170 L300 750 M155 595 L300 750 L445 595',
    '↔': 'M80 460 L640 460 M225 315 L80 460 L225 605 M495 315 L640 460 L495 605',
    '↕': 'M300 110 L300 810 M165 245 L300 110 L435 245 M165 675 L300 810 L435 675',
    '✓': 'M80 470 C130 520 180 600 220 690 C300 480 400 300 540 150',
    '✗': 'M110 200 C230 370 340 540 460 720 M460 190 C340 360 230 540 110 730',
    '●': circle(300, 460, 215, end='F'),
    '○': circle(300, 460, 215),
}

# Typewriter only: what a terminal (and Claude Code) prints. Box drawing and
# block elements are not drawn with a pen; build.py makes them to fill the cell.
TERMINAL = {
    '⏺': circle(300, 460, 160, end='F'),
    '◯': circle(300, 460, 250),
    '◉': circle(300, 460, 230) + ' ' + circle(300, 460, 110, end='F'),
    '■': 'M110 270 L490 270 L490 650 L110 650 F',
    '□': 'M110 270 L490 270 L490 650 L110 650 Z',
    '◼': 'M150 310 L450 310 L450 610 L150 610 F',
    '◻': 'M150 310 L450 310 L450 610 L150 610 Z',
    '⏹': 'M160 320 L440 320 L440 600 L160 600 F',
    '▪': 'M210 370 L390 370 L390 550 L210 550 F',
    '▫': 'M210 370 L390 370 L390 550 L210 550 Z',
    '◆': 'M300 220 L520 460 L300 700 L80 460 F',
    '◇': 'M300 220 L520 460 L300 700 L80 460 Z',
    '▶': 'M130 250 L510 460 L130 670 F',
    '◀': 'M470 250 L90 460 L470 670 F',
    '▲': 'M300 240 L520 650 L80 650 F',
    '▼': 'M80 270 L520 270 L300 680 F',
    '▸': 'M200 340 L420 460 L200 580 F',
    '⏵': 'M170 300 L450 460 L170 620 F',
    '⏸': 'M215 290 L215 630 M385 290 L385 630',
    '❯': 'M160 220 L440 460 L160 700',
    '✔': SYMBOLS['✓'],
    '✘': SYMBOLS['✗'],
    '☐': 'M100 220 L500 220 L500 700 L100 700 Z',
    '☒': 'M100 220 L500 220 L500 700 L100 700 Z M180 310 L420 610 M420 310 L180 610',
    '☑': 'M100 220 L500 220 L500 700 L100 700 Z M170 470 C200 500 230 550 255 610 C300 480 360 380 440 300',
    '⚠': 'M300 120 L560 720 L40 720 Z M300 330 L300 545 M298 630 l2 8',
    '↵': 'M500 240 L500 530 L120 530 M245 405 L120 530 L245 655',
    '⏎': 'M500 240 L500 530 L120 530 M245 405 L120 530 L245 655',
    '⇧': 'M300 170 L530 420 L410 420 L410 710 L190 710 L190 420 L70 420 Z',
    '⌃': 'M110 420 L300 230 L490 420',
    '⌥': 'M50 300 L210 300 L390 640 L550 640 M350 300 L550 300',
    '⌘': ' '.join(circle(x, y, 62) for x, y in ((158, 318), (442, 318), (158, 602), (442, 602)))
         + ' M220 318 L220 602 M380 318 L380 602 M158 380 L442 380 M158 540 L442 540',
    # Claude Code's spinner, from small to full: · ✢ ✳ ✶ ✻ ✽
    '✢': leaves(300, 460, 4, 230, 50, hub=0.28),
    '✳': 'M300 230 L300 690 M70 460 L530 460 M137 297 L463 623 M463 297 L137 623',
    '✶': star(300, 460, 6, 250, 125),
    '✻': leaves(300, 460, 8, 235, 30, hub=0.36),
    '✽': leaves(300, 460, 8, 240, 52, hub=0.3),
}

# A terminal symbol stands about as tall as a capital, centred on the math axis.
TERMINAL = {c: scale(d, 1.2, 300, 460) for c, d in TERMINAL.items()}

# Pen weight for the heavy forms.
LIGHTER.update({'❯': 1.55, '✔': 1.6, '✘': 1.6, '⏸': 1.5, '✢': 0.75, '✳': 0.85, '✶': 0.75, '✻': 0.7, '✽': 0.75})

# The Typewriter's own forms of symbols that, drawn as in the proportional
# fonts, came out small in a terminal cell. Arrows run nearly the cell's
# width (← →) or the cap height (↑ ↓), with heads at 45°; © and ® are ovals
# as tall as a capital, since a circle that fits the cell's width is far
# shorter; ™ hangs from the cap height and fills the cell; ✗ covers what ✓
# covers.
MONO = {
    '←': 'M580 460 L60 460 M260 260 L60 460 L260 660',
    '→': 'M60 460 L580 460 M380 260 L580 460 L380 660',
    '↑': 'M320 765 L320 35 M120 235 L320 35 L520 235',
    '↓': 'M320 35 L320 765 M120 565 L320 765 L520 565',
    '↔': 'M50 460 L590 460 M225 285 L50 460 L225 635 M415 285 L590 460 L415 635',
    '↕': 'M320 20 L320 780 M150 190 L320 20 L490 190 M150 610 L320 780 L490 610',
    '©': circle(320, 400, 265, 335) + ' ' + scale(UPPER['C'], 0.6, 295, 400, 25, 0),
    '®': circle(320, 400, 265, 335) + ' ' + scale(UPPER['R'], 0.56, 295, 400, 25, 0),
    '™': 'M30 50 L270 50 M150 50 L150 410 M330 410 L340 50 L450 330 L560 50 L570 410',
    '✗': 'M100 170 C230 360 360 560 500 740 M500 160 C370 350 230 560 90 750',
}
MONO['✘'] = MONO['✗']
# ...and a heavier pen for them, so they don't read as letters (✗ as x).
MONO_WEIGHT = {c: 1.2 for c in '←→↑↓↔↕✓✗'}

# Glyphs whose shape must not be stretched to fill the typewriter's cell.
KEEP_SHAPE = set(SYMBOLS) | set(TERMINAL) | set('©®¤°•◌') | set(COMBINING_MARKS)


def charset(mono=False):
    """Every character a font draws with its pen, in order."""
    chars = list(ALL) + [c for c in LATIN if c not in ALL] + list(BUILT) + list(SPACING_MARKS) + list(ACCENTED)
    chars += list(SYMBOLS) + list(COMBINING_MARKS)
    if mono:
        chars += list(TERMINAL)
    return chars


def mark_origin(name, base, reach, ring=50, hook=1.0, d=None):
    """Where mark `name` goes on letter `base` for a pen that inks `reach`
    units each side of its centre line: (shape, x, y, line). The shape is
    drawn about (x, y); `line` is the height the placement is measured from
    (the letter's top, or the baseline for a mark below), so a combining
    mark's anchor and a letter's anchor meet at the same distance.

    A mark above clears the letter's overshoot (or its ascender) by a gap and
    centres on the letter's body. A heavier or broader pen gets a larger ring
    (radius `ring`) and a larger cedilla and ogonek (`hook` times), so the eye
    and the curl stay open."""
    lower = base.islower() or base == '◌'
    if d is None:
        d = DOTLESS.get(base, ALL[base])
    top = min(y for _x, y in _points(d))
    # Over an ascender a mark takes the flatter capital form.
    tall = not lower or top < 200
    shape = MARK_SHAPES[name][1 if tall else 0]
    x = MARK_X.get((base, name), mark_centre(d, lower))
    if name in ('cedilla', 'ogonek'):
        shape = scale(shape, hook, 0, 0)
        x = (CEDILLA_X if name == 'cedilla' else OGONEK_X).get(base, x)
        return shape, x, 748, 750
    if name == 'commabelow':
        return shape, x + 6, 750 + 12 + 2 * reach + 16, 750
    if name == 'caronvert':
        # Clear of the stem by the same gap a mark keeps above a letter.
        y = 40 if lower else 50
        return shape, CARON_STEM[base] + 2 * reach + 54, y, y
    gap = 30 if tall else 40
    if name == 'ring':
        # Over a capital the ring is smaller and sits close to the apex.
        shape = scale(shape, ring / 50 * (1 if lower else 0.8), 0, 0)
        gap = 40 if lower else 18
    line = top if lower and tall else (250 if lower else 50)
    return shape, x, line - 12 - 2 * reach - gap, line


def mark_path(name, base, reach, ring=50, hook=1.0, d=None):
    shape, x, y, _line = mark_origin(name, base, reach, ring, hook, d)
    return transform(shape, lambda p: (p[0] + x, p[1] + y))


def mark_parts(ch, reach, ring, hook, case):
    name = COMBINING_MARKS[ch]
    return [('mark', mark_path(name, 'H' if case else 'x', reach, ring, hook), 1.0)]


def mark_anchors(ch, reach, ring=50, hook=1.0, case=False):
    """A combining mark's own anchor (where it attaches), and for a mark
    above, the anchor the next mark stacks on: {class: (x, y)}, {class: (x, y)}."""
    name = COMBINING_MARKS[ch]
    shape, x, y, line = mark_origin(name, 'H' if case else 'x', reach, ring, hook)
    own = {ANCHOR[name]: (x, line)}
    stack = {}
    if ANCHOR[name] == 'top':
        stack['top'] = (x, _stack_line(shape, y, reach, case))
    return own, stack


def _stack_line(shape, y, reach, upper):
    """The `line` for the next mark above, so that it clears this one's top
    by STACK units: its foot sits at line - 12 - 2*reach - gap, and its ink
    a reach below that."""
    top = min(py for _x, py in _points(shape)) + y
    return top - STACK + 12 + (30 if upper else 40)


def base_anchors(ch, reach, ring=50, hook=1.0):
    """Where combining marks attach to a letter: {class: (x, y)}."""
    if ch in ACCENTED:
        base, own = ACCENTED[ch]
        d = parts(ch, reach)[0][1]
    elif ch in BUILT:
        base, own = BUILT[ch][0], None
        d = ALL[base]
    else:
        base, own = ch, None
        d = ALL.get(ch) or LATIN.get(ch)
    if d is None:
        return {}
    upper = not (base.islower() or base == '◌')
    out = {}
    for name, cls in (('circumflex', 'top'), ('commabelow', 'bottom'), ('cedilla', 'cedilla'), ('ogonek', 'ogonek')):
        _s, x, _y, line = mark_origin(name, base, reach, ring, hook, d)
        out[cls] = (x, line)
    if own and own not in BELOW and own != 'caronvert':
        # Over a mark already there: stack on it.
        shape, x, y, _line = mark_origin(own, base, reach, ring, hook, d)
        out['top'] = (x, _stack_line(shape, y, reach, upper))
    return out


def parts(ch, reach, mono=False, ring=50, hook=1.0, variant=0):
    """A glyph as pen strokes: [(role, path, weight)]. role is the character
    whose overshoot rules apply, or 'mark', 'serif', 'extra' or '' for
    strokes that keep their place; weight scales the pen. A combining mark's
    variant 1 is its capital form."""
    if ch in COMBINING_MARKS:
        return mark_parts(ch, reach, ring, hook, variant == 1)
    if ch in ACCENTED:
        base, mark = ACCENTED[ch]
        # A mark over i or j replaces its dot; one under it keeps it (į).
        d = ALL[base] if mark in BELOW else DOTLESS.get(base, ALL[base])
        out = [(base, d, 1.0)]
        if mono and base in TYPE_SERIFS:
            out.append(('serif', TYPE_SERIFS[base], 1.0))
        out.append(('mark', mark_path(mark, base, reach, ring, hook, d), 1.0))
        return out
    if ch in SPACING_MARKS:
        return [('mark', mark_path(SPACING_MARKS[ch], 'x', reach, ring, hook), 1.0)]
    if ch in BUILT:
        base, extra = BUILT[ch]
        role = base if ch.isalpha() else ''
        out = [(role, ALL[base], 1.0), ('extra', extra, 1.0)]
        if mono and base in TYPE_SERIFS:
            out.append(('serif', TYPE_SERIFS[base], 1.0))
        return out
    w = MONO_WEIGHT.get(ch, LIGHTER.get(ch, 1.0)) if mono else LIGHTER.get(ch, 1.0)
    if mono and ch in MONO:
        d = MONO[ch]
    elif ch in ALL:
        d = ALL[ch]
    elif ch in LATIN:
        d = LATIN[ch]
    elif ch in SYMBOLS:
        d = SYMBOLS[ch]
    else:
        d = TERMINAL[ch]
    role = ch if _ud.category(ch) in ('Ll', 'Lu', 'Nd') else ''
    out = [(role, d, w)]
    if mono and ch in TYPE_SERIFS:
        out.append(('serif', TYPE_SERIFS[ch], 1.0))
    return out


def base_of(ch):
    """The letter whose drawing (and random hand) a glyph reuses."""
    if ch in ACCENTED:
        return ACCENTED[ch][0]
    if ch in BUILT:
        return BUILT[ch][0]
    return ch
