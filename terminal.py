"""Pinboard Typewriter NF CN: the Typewriter as a terminal font, with
Chinese from LXGW WenKai TC and the icons of Nerd Fonts.

    .venv/bin/python terminal.py                 # out/PinboardTypewriterNFCN-{Regular,Bold}.otf
    .venv/bin/python terminal.py --only 永國中… --scale 1.0 --out /tmp/x   # a quick proof

It merges three fonts into one, so a terminal never has to fall back:

- Pinboard Typewriter, as built by build.py, keeps every glyph, hint and
  feature it has.
- LXGW WenKai Mono TC (Regular for Regular, Medium for Bold, as it has no
  Bold) gives everything the Typewriter lacks: CJK ideographs, Bopomofo,
  kana, CJK and full-width punctuation, Greek, Cyrillic and more. Each glyph
  takes the cell its character's East Asian Width gives it: two (1200
  units) for Wide and Fullwidth, one (600) for the rest. Ideographs are
  scaled by SCALE, centred in their cell, and moved so the middle of their
  ink sits on the middle of the Typewriter's capitals.
- Symbols Nerd Font gives its icons, placed as Nerd Fonts' patcher places
  them in a monospaced font: one cell of advance, the icon free to run on
  over the next. Powerline separators are stretched to the full line, so a
  prompt's coloured segments join.

Outlines are converted from TrueType to CFF: quadratic curves become cubic
ones (merged where a single cubic fits within MAX_ERR), contours are turned
to PostScript's direction, coordinates are rounded, and shared runs become
subroutines. The sources are fetched by the README's commands into
sources/, which git ignores.
"""
import argparse
import time
import unicodedata
from pathlib import Path

import cffsubr
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.misc.psCharStrings import T2CharString
from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.qu2cuPen import Qu2CuPen
from fontTools.pens.recordingPen import DecomposingRecordingPen, RecordingPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.teePen import TeePen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

HERE = Path(__file__).resolve().parent
OUT = HERE / 'out'
SRC = HERE / 'sources'
WENKAI = SRC / 'wenkai'
NERD = SRC / 'nerd' / 'unpacked' / 'SymbolsNerdFont-Regular.ttf'
WEIGHTS = {'Regular': 'LXGWWenKaiMonoTC-Regular.ttf', 'Bold': 'LXGWWenKaiMonoTC-Medium.ttf'}

FAMILY = 'Pinboard Typewriter NF CN'
PS_FAMILY = 'PinboardTypewriterNFCN'
CELL = 600
SCALE = 1.0           # WenKai's em to ours
ICF_CENTRE = 348      # the middle of WenKai's ideographs' ink (永國中), moved to our caps' centre
MAX_ERR = 1.0         # how far a merged cubic may stray from the quadratics, in source units

SOURCES = ('LXGW WenKai TC 1.530 (https://github.com/lxgw/LxgwWenkaiTC), '
           'Symbols Nerd Font 3.5.1 (https://github.com/ryanoasis/nerd-fonts)')
COPYRIGHT = ('Copyright 2026 The Pinboard Fonts Project Authors (https://github.com/zjlgdx/pinboard-fonts). '
             'Copyright 2022-2026 The LXGW WenKai Project Authors (https://github.com/lxgw/LxgwWenkaiTC). '
             'Nerd Fonts icons copyright 2014 Ryan L McIntyre and the authors of each icon set '
             '(https://github.com/ryanoasis/nerd-fonts).')


def wide(cp):
    return unicodedata.east_asian_width(chr(cp)) in ('W', 'F')


def private_use(cp):
    return 0xE000 <= cp <= 0xF8FF or cp >= 0xF0000


def skip(cp):
    """Controls and private use never come from WenKai: the icons own the PUA."""
    return private_use(cp) or unicodedata.category(chr(cp)) in ('Cc', 'Cs')


class Cubics(BasePen):
    """Quadratic curves as the exact cubics they are."""

    def __init__(self, out):
        super().__init__(None)
        self.out = out

    def _moveTo(self, p):
        self.out.moveTo(p)

    def _lineTo(self, p):
        self.out.lineTo(p)

    def _curveToOne(self, p1, p2, p3):
        self.out.curveTo(p1, p2, p3)

    def _closePath(self):
        self.out.closePath()

    def _endPath(self):
        self.out.endPath()


class Builder:
    """Charstrings for glyphs drawn from another font, in our private dict's
    width encoding, with their bounds."""

    def __init__(self, private):
        self.default = private.defaultWidthX
        self.nominal = private.nominalWidthX

    def charstring(self, glyph, glyphset, matrix, advance, max_err):
        pen = T2CharStringPen(None if advance == self.default else advance - self.nominal, None)
        bounds = BoundsPen(None)
        out = TransformPen(TeePen(pen, bounds), matrix)
        # TrueType's outer contours run clockwise, PostScript's counter-clockwise.
        # Components first become outlines (a mirrored one keeps its direction).
        flat = DecomposingRecordingPen(glyphset, reverseFlipped=True)
        glyph.draw(flat)
        try:
            rec = RecordingPen()
            flat.replay(Qu2CuPen(rec, max_err, all_cubic=True, reverse_direction=True))
        except NotImplementedError:
            # A contour with no on-curve point (a TrueType circle): exact cubics.
            rec = RecordingPen()
            flat.replay(ReverseContourPen(Cubics(rec)))
        rec.replay(out)
        cs = pen.getCharString()
        lsb = round(bounds.bounds[0]) if bounds.bounds else 0
        return cs, lsb, bounds.bounds


def wenkai_matrix(src_adv, adv, ink, scale, cap_centre):
    """Scale about the baseline, centre in the cell; shrink a glyph that
    would overrun a one-cell character about its own centre."""
    s = scale
    dx = (adv - s * src_adv) / 2
    if src_adv == 0 and adv and ink:
        dx = adv / 2 - s * (ink[0] + ink[2]) / 2     # a spacing form of a zero-width drawing
    dy = cap_centre - s * ICF_CENTRE
    if ink and adv:
        w = (ink[2] - ink[0]) * s
        room = adv * 0.92
        if w > room:
            f = room / w
            cx = s * (ink[0] + ink[2]) / 2 + dx
            cy = s * (ink[1] + ink[3]) / 2
            return (s * f, 0, 0, s * f, cx - f * cx + f * dx, cy - f * cy + f * dy)
    return (s, 0, 0, s, dx, dy)


def nerd_matrix(cp, ink, src_adv, line):
    """Place an icon as Nerd Fonts' own patcher does for a monospaced font
    (its default variant, as Maple Mono NF uses): the source's em becomes
    ours, the icon starts at the cell's left and may run on over the next
    cell, the way a prompt follows it with a space. Powerline glyphs fill
    the line from descender to ascender: the separators (which span the
    source's whole line) are stretched over their cell, one cell or two,
    keeping the source's small overlap so no hairline shows between
    segments; the branch, line-number and lock marks keep their shape."""
    asc, desc = line
    k = 1000 / 2048
    sy = (asc - desc) / 2048
    if 0xE0B0 <= cp <= 0xE0D7 and ink[3] - ink[1] >= 2000:
        cells = 2 if src_adv > 1600 else 1
        sx = cells * CELL / src_adv
        return (sx, 0, 0, sy, 0, desc + 410 * sy)
    if 0xE0A0 <= cp <= 0xE0A3:
        return (sy, 0, 0, sy, (CELL - (ink[2] + ink[0]) * sy) / 2, desc + 410 * sy)
    return (k, 0, 0, k, 0, (asc + desc) / 2 - 614 * k)


def ink_bounds(glyph, glyphset):
    b = BoundsPen(glyphset)
    glyph.draw(b)
    return b.bounds


def merge(weight, scale, only=None, out=OUT):
    t0 = time.time()
    ours = TTFont(OUT / f'PinboardTypewriter-{weight}.otf')
    cffsubr.desubroutinize(ours)
    top = ours['CFF '].cff.topDictIndex[0]
    private = top.Private
    build = Builder(private)
    asc, desc = ours['OS/2'].sTypoAscender, ours['OS/2'].sTypoDescender
    # Both weights place CJK by the Regular's capitals, so text doesn't jump between them.
    cap_centre = TTFont(OUT / 'PinboardTypewriter-Regular.otf', lazy=True)['OS/2'].sCapHeight / 2

    order = list(ours.getGlyphOrder())
    charstrings, metrics = {}, {}
    for name in order:
        cs = top.CharStrings[name]
        cs.decompile()
        charstrings[name] = T2CharString(program=list(cs.program))
        metrics[name] = ours['hmtx'][name]
    cmap = dict(ours.getBestCmap())
    have = set(cmap)
    added = {'cjk': 0, 'other': 0, 'icons': 0}

    def wanted(cp):
        return cp not in have and (only is None or chr(cp) in only)

    # WenKai: whatever the Typewriter lacks, one glyph per (source glyph, cell).
    wk = TTFont(WENKAI / WEIGHTS[weight])
    wgs, wcmap = wk.getGlyphSet(), wk.getBestCmap()
    made, marks = {}, set()
    for cp in sorted(wcmap):
        if not wanted(cp) or skip(cp):
            continue
        src = wcmap[cp]
        src_adv = wk['hmtx'][src][0]
        # Only a combining mark (or a format character) takes no cell.
        mark = unicodedata.category(chr(cp)) in ('Mn', 'Me', 'Cf')
        adv = 0 if (src_adv == 0 and mark) else (2 * CELL if wide(cp) else CELL)
        key = (src, adv)
        if key not in made:
            name = f'u{cp:04X}'
            matrix = wenkai_matrix(src_adv, adv, ink_bounds(wgs[src], wgs), scale, cap_centre)
            cs, lsb, _ = build.charstring(wgs[src], wgs, matrix, adv, MAX_ERR)
            charstrings[name], metrics[name] = cs, (adv, lsb)
            order.append(name)
            made[key] = name
            if adv == 0:
                marks.add(name)
            added['cjk' if adv == 2 * CELL else 'other'] += 1
        cmap[cp] = made[key]
    # Variation sequences (IVS) whose base and glyph made it in.
    uvs = {}
    for sub in wk['cmap'].tables:
        if sub.format != 14:
            continue
        for vs, pairs in sub.uvsDict.items():
            for base, g in pairs:
                if base not in cmap or (g is not None and (g, 2 * CELL if wide(base) else CELL) not in made):
                    continue
                target = None if g is None else made[(g, 2 * CELL if wide(base) else CELL)]
                uvs.setdefault(vs, []).append((base, target))

    # Nerd Fonts: every icon the two lack.
    nf = TTFont(NERD)
    ngs, ncmap = nf.getGlyphSet(), nf.getBestCmap()
    for cp in sorted(ncmap):
        if not wanted(cp) or cp in cmap:
            continue
        src = ncmap[cp]
        ink = ink_bounds(ngs[src], ngs)
        if not ink:
            continue
        name = f'u{cp:04X}'
        matrix = nerd_matrix(cp, ink, nf['hmtx'][src][0], (asc, desc))
        adv = CELL
        if wide(cp):
            # An icon on a Wide character (⚡) gets two cells, centred in them.
            adv = 2 * CELL
            matrix = matrix[:4] + (matrix[4] + CELL / 2, matrix[5])
        cs, lsb, _ = build.charstring(ngs[src], ngs, matrix, adv, 2 * MAX_ERR)
        charstrings[name], metrics[name] = cs, (adv, lsb)
        order.append(name)
        cmap[cp] = name
        added['icons'] += 1

    # The new font: our tables, a bigger glyph set.
    fb = FontBuilder(1000, isTTF=False)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap, uvs=[(b, v, g) for v, pairs in uvs.items() for b, g in pairs] or None)
    fb.setupHorizontalMetrics(metrics)
    style = weight
    ps = f'{PS_FAMILY}-{style}'
    version = ours['head'].fontRevision
    fb.setupNameTable({
        'copyright': COPYRIGHT,
        'familyName': FAMILY,
        'styleName': style,
        'uniqueFontIdentifier': f'{version:.3f};{ps}',
        'fullName': f'{FAMILY} {style}',
        'psName': ps,
        'version': f'Version {version:.3f}',
        'description': f'Pinboard Typewriter for terminals, with Chinese and icons merged from {SOURCES}.',
        'vendorURL': 'https://github.com/zjlgdx/pinboard-fonts',
        'licenseDescription': 'This Font Software is licensed under the SIL Open Font License, Version 1.1.',
        'licenseInfoURL': 'https://openfontlicense.org',
    }, mac=False)
    info = {k: getattr(top, k) for k in ('version', 'Notice', 'UnderlinePosition', 'UnderlineThickness', 'Weight')
            if hasattr(top, k)}
    info.update(FullName=f'{FAMILY} {style}', FamilyName=FAMILY, isFixedPitch=1)
    keep = ('BlueValues', 'OtherBlues', 'FamilyBlues', 'FamilyOtherBlues', 'StdHW', 'StdVW', 'StemSnapH',
            'StemSnapV', 'BlueScale', 'BlueShift', 'BlueFuzz', 'ForceBold', 'LanguageGroup', 'defaultWidthX',
            'nominalWidthX')
    fb.setupCFF(ps, info, charstrings, {k: getattr(private, k) for k in keep if getattr(private, k, None) is not None})
    font = fb.font
    for tag in ('head', 'hhea', 'OS/2', 'post', 'GDEF', 'GSUB', 'GPOS'):
        if tag in ours:
            font[tag] = ours[tag]
    # WenKai's combining marks join ours in GDEF's mark class.
    classes = font['GDEF'].table.GlyphClassDef.classDefs
    for name in marks:
        classes[name] = 3
    font['maxp'] = newTable('maxp')
    font['maxp'].tableVersion = 0x00005000
    font['maxp'].numGlyphs = len(order)
    font['post'].isFixedPitch = 1
    os2 = font['OS/2']
    # A terminal sizes its cell from the average width: keep it one cell.
    os2.xAvgCharWidth = CELL
    os2.usFirstCharIndex = min(cmap)
    os2.usLastCharIndex = min(max(cmap), 0xFFFF)
    os2.recalcUnicodeRanges(font)
    os2.recalcCodePageRanges(font)
    # The meta table names the languages the font is designed for and supports.
    if 'meta' in wk:
        font['meta'] = wk['meta']
    font['head'].recalcBBoxes = True
    font['hhea'].advanceWidthMax = max(a for a, _ in metrics.values())

    # BASE: where ideographs sit relative to Latin, for apps that align scripts.
    ideo = round(-120 * scale + cap_centre - scale * ICF_CENTRE)
    tops, bots = [], []
    for cp in (0x6C38, 0x570B, 0x4E2D, 0x9F98, 0x9EBC):   # 永國中龘麼
        if cp in cmap:
            b = ink_bounds_cs(charstrings[cmap[cp]], font)
            if b:
                bots.append(b[1]); tops.append(b[3])
    icfb = min(bots) if bots else ideo
    icft = max(tops) if tops else round(ideo + 1000 * scale)
    fea = f"""table BASE {{
  HorizAxis.BaseTagList icfb icft ideo romn;
  HorizAxis.BaseScriptList
    DFLT romn {icfb} {icft} {ideo} 0,
    latn romn {icfb} {icft} {ideo} 0,
    hani ideo {icfb} {icft} {ideo} 0,
    kana ideo {icfb} {icft} {ideo} 0;
}} BASE;
"""
    addOpenTypeFeaturesFromString(font, fea, tables={'BASE'})

    # Win metrics: the font's whole ink, so nothing is clipped on Windows.
    font.save(out / f'{ps}.tmp.otf')
    font = TTFont(out / f'{ps}.tmp.otf')
    font['OS/2'].usWinAscent = max(font['OS/2'].usWinAscent, font['head'].yMax)
    font['OS/2'].usWinDescent = max(font['OS/2'].usWinDescent, -font['head'].yMin)
    cffsubr.subroutinize(font)
    path = out / f'{ps}.otf'
    font.save(path)
    (out / f'{ps}.tmp.otf').unlink()
    print(f'{FAMILY} {style}: {len(order)} glyphs, {len(cmap)} characters '
          f'(+{added["cjk"]} wide, +{added["other"]} one-cell from WenKai, +{added["icons"]} icons), '
          f'{sum(len(v) for v in uvs.values())} variation sequences, '
          f'{path.stat().st_size // 1024} KB, {time.time() - t0:.0f} s')
    return path


def ink_bounds_cs(cs, font):
    b = BoundsPen(None)
    cs.draw(b)
    return b.bounds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scale', type=float, default=SCALE)
    ap.add_argument('--only', help='only these characters (a quick proof)')
    ap.add_argument('--out', type=Path, default=OUT)
    ap.add_argument('--weights', default='Regular,Bold')
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    paths = [merge(w, a.scale, set(a.only) if a.only else None, a.out) for w in a.weights.split(',')]
    # The family shares its win metrics, so neither weight clips the other's glyphs.
    fonts = [TTFont(p) for p in paths]
    asc = max(f['OS/2'].usWinAscent for f in fonts)
    desc = max(f['OS/2'].usWinDescent for f in fonts)
    for f, p in zip(fonts, paths):
        if (f['OS/2'].usWinAscent, f['OS/2'].usWinDescent) != (asc, desc):
            f['OS/2'].usWinAscent, f['OS/2'].usWinDescent = asc, desc
            f.save(p)


if __name__ == '__main__':
    main()
