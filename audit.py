"""Measure the built fonts against type-design rules: overshoot, stems,
spacing, contours, metrics. Prints a report; changes nothing."""
import sys
from pathlib import Path
from statistics import median
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.areaPen import AreaPen

OUT = Path(__file__).resolve().parent / 'out'

def glyph_info(gs, name):
    bp = BoundsPen(gs); gs[name].draw(bp)
    rec = RecordingPen(); gs[name].draw(rec)
    return bp.bounds, rec.value

def contours(rec):
    cs, cur = [], []
    for op, args in rec:
        cur.append((op, args))
        if op in ('closePath', 'endPath'):
            cs.append(cur); cur = []
    return cs

def scanline(gs, name, y):
    """x spans of ink along a horizontal line, by sampling."""
    from fontTools.pens.pointInsidePen import PointInsidePen
    b, _ = glyph_info(gs, name)
    spans, inside, start = [], False, None
    x = b[0] - 5
    while x <= b[2] + 5:
        p = PointInsidePen(gs, (x, y)); gs[name].draw(p)
        if p.getResult() != inside:
            inside = not inside
            if inside: start = x
            else: spans.append((start, x))
        x += 2
    return spans

for path in sorted(OUT.glob('*.otf')):
    f = TTFont(path); gs = f.getGlyphSet(); cmap = f.getBestCmap(); hm = f['hmtx']
    g = lambda c: cmap[ord(c)]
    print(f'\n===== {path.stem}')
    os2, hhea, post = f['OS/2'], f['hhea'], f['post']
    # vertical extremes vs metrics
    ys = [glyph_info(gs, n)[0] for n in f.getGlyphOrder() if glyph_info(gs, n)[0]]
    ymax, ymin = max(b[3] for b in ys), min(b[1] for b in ys)
    print(f'metrics: typo {os2.sTypoAscender}/{os2.sTypoDescender}/{os2.sTypoLineGap} hhea {hhea.ascent}/{hhea.descent} win {os2.usWinAscent}/{os2.usWinDescent}; ink {ymax:.0f}/{ymin:.0f}; fsSelection {os2.fsSelection:#x}; italicAngle {post.italicAngle}; caret {hhea.caretSlopeRise}/{hhea.caretSlopeRun}')
    print(f'xHeight {os2.sxHeight} capHeight {os2.sCapHeight}')
    # overshoot: flat vs round letters
    def top(c): return glyph_info(gs, g(c))[0][3]
    def bot(c): return glyph_info(gs, g(c))[0][1]
    feet = sorted(round(bot(c)) for c in 'xzHEILTnmhu')    # build.py's FLAT_FEET
    print('baseline: flat feet', feet, 'median', feet[len(feet) // 2])
    print('baseline: flat x', round(bot('x')), 'z', round(bot('z')), 'H', round(bot('H')), '| round o', round(bot('o')), 'O', round(bot('O')), 's', round(bot('s')), 'c', round(bot('c')))
    print('x-height: flat x', round(top('x')), 'z', round(top('z')), 'v', round(top('v')), '| round o', round(top('o')), 'c', round(top('c')), 's', round(top('s')), 'n', round(top('n')))
    print('cap: flat H', round(top('H')), 'E', round(top('E')), 'T', round(top('T')), '| round O', round(top('O')), 'C', round(top('C')), 'S', round(top('S')), '| asc b', round(top('b')), 'd', round(top('d')), 'h', round(top('h')), 'l', round(top('l')), 'k', round(top('k')))
    print('figures: 0', round(top('0')), '1', round(top('1')), '8', round(top('8')), '| desc p', round(bot('p')), 'q', round(bot('q')), 'g', round(bot('g')), 'y', round(bot('y')), 'j', round(bot('j')))
    # stems: vertical (n, H, l) at mid height; horizontals (H bar, E arms, t bar)
    xh = os2.sxHeight
    def vstem(c, y): s = scanline(gs, g(c), y); return [round(b - a) for a, b in s]
    print('vertical stems  n@', xh//2, vstem('n', xh//2), ' H@', os2.sCapHeight//4, vstem('H', os2.sCapHeight//4), ' l@', xh//2, vstem('l', xh//2), ' o@', xh//2, vstem('o', xh//2))
    # horizontal: sample along x through E middle
    from fontTools.pens.pointInsidePen import PointInsidePen
    def hstem(c, xf):
        b = glyph_info(gs, g(c))[0]; x = b[0] + (b[2] - b[0]) * xf
        spans, inside, start, y = [], False, None, b[1] - 5
        while y <= b[3] + 5:
            p = PointInsidePen(gs, (x, y)); gs[g(c)].draw(p)
            if p.getResult() != inside:
                inside = not inside
                if inside: start = y
                else: spans.append(round(y - start))
            y += 2
        return spans
    print('horizontal stems E@0.6', hstem('E', 0.6), ' o@0.5', hstem('o', 0.5), ' z@0.5', hstem('z', 0.5))
    # spacing
    def sb(c):
        n = g(c); b = glyph_info(gs, n)[0]; adv = hm[n][0]
        return round(b[0]), round(adv - b[2]), adv
    print('sidebearings (lsb, rsb, adv):', {c: sb(c) for c in 'HOnoilvxAT'})
    # contours
    nodes, dirs, small = 0, {'ccw': 0, 'cw': 0}, 0
    worst = []
    for n in f.getGlyphOrder():
        rec = glyph_info(gs, n)[1]
        cnt = sum(1 for op, a in rec if op in ('lineTo', 'curveTo', 'qCurveTo'))
        nodes += cnt; worst.append((cnt, n))
        for c in contours(rec):
            ap = AreaPen(); RecordingPen.replay(type('R', (), {'value': c})(), ap) if False else None
            r = RecordingPen(); r.value = c; ap = AreaPen(); r.replay(ap)
            dirs['ccw' if ap.value > 0 else 'cw'] += 1
            if abs(ap.value) < 400: small += 1
    worst.sort(reverse=True)
    print(f'segments total {nodes}, most: {worst[:5]}; contour dirs {dirs}; tiny contours (<400 u²) {small}')
    if f['post'].isFixedPitch:
        # Combining marks (GDEF class 3) have no width in any font.
        gdef = f['GDEF'].table.GlyphClassDef.classDefs if 'GDEF' in f else {}
        widths = {hm[n][0] for n in f.getGlyphOrder() if n != '.notdef' and gdef.get(n) != 3}
        marks = {hm[n][0] for n in f.getGlyphOrder() if gdef.get(n) == 3}
        print('monospace advances:', widths, '| combining marks:', marks or '-')
