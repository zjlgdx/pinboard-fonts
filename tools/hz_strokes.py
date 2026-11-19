"""python tools/hz_strokes.py OUT.jpg NAMES [--batch A.py,B.py] [--size 260] [--per 6]

Each named part (K) or character (C), drawn as bare centre lines with every
stroke numbered at its start, in the order it is drawn, and the count beside
Unihan's. For telling a part with a stroke too few from one whose turn is
drawn as two items (tools/hz_count.py lists both). NAMES is a string of
characters; a K entry wins over a C entry of the same name, and K names of more
than one character go in as a comma-separated list after a slash: '糸幺弓/鳥上,者T'.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _repo
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument('out')
ap.add_argument('names')
ap.add_argument('--batch', default='')
ap.add_argument('--size', type=int, default=260)
ap.add_argument('--per', type=int, default=6)
a = ap.parse_args()

h = _repo.load(a.batch)
from hanzi import flatten  # noqa: E402

single, _, multi = a.names.partition('/')
names = list(single) + [n for n in multi.split(',') if n]

counts = {}
f = _repo.ROOT / 'work/unihan/Unihan_IRGSources.txt'
if f.exists():
    for line in open(f, encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        if len(p) == 3 and p[1] == 'kTotalStrokes':
            counts[chr(int(p[0][2:], 16))] = p[2]

TOK = re.compile(r'[MLCQZmlcqz]|-?[\d.]+')


def points(d):
    """The path as a polyline, absolute M L C Q only (what S() writes)."""
    out, cur, t = [], [], TOK.findall(d)
    i, cmd, pos = 0, 'M', (0.0, 0.0)
    while i < len(t):
        if t[i].isalpha():
            cmd = t[i]
            i += 1
            if cmd in 'Zz':
                if cur:
                    cur.append(cur[0])
                continue
        n = {'M': 2, 'L': 2, 'C': 6, 'Q': 4}[cmd.upper()]
        v = [float(x) for x in t[i:i + n]]
        i += n
        if cmd == 'M':
            if cur:
                out.append(cur)
            cur, pos = [(v[0], v[1])], (v[0], v[1])
            cmd = 'L'
        elif cmd == 'L':
            pos = (v[0], v[1])
            cur.append(pos)
        else:
            ctrl = [pos] + [(v[k], v[k + 1]) for k in range(0, n, 2)]
            for s in range(1, 17):
                u = s / 16
                pts = ctrl
                while len(pts) > 1:
                    pts = [((1 - u) * p[0] + u * q[0], (1 - u) * p[1] + u * q[1]) for p, q in zip(pts, pts[1:])]
                cur.append(pts[0])
            pos = ctrl[-1]
    if cur:
        out.append(cur)
    return out


COLOURS = ['#c0392b', '#2471a3', '#1e8449', '#b9770e', '#7d3c98', '#117a65', '#a04000', '#2e4053']
Z = a.size


def label_font(size):
    for p in ('/System/Library/Fonts/Hiragino Sans GB.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)


lab, num = label_font(18), label_font(15)
rows = -(-len(names) // a.per)
img = Image.new('RGB', (a.per * (Z + 20) + 20, rows * (Z + 50) + 20), '#ffffff')
d = ImageDraw.Draw(img)
for idx, name in enumerate(names):
    item = h.K.get(name, h.C.get(name))
    x0, y0 = 20 + (idx % a.per) * (Z + 20), 20 + (idx // a.per) * (Z + 50)
    where = 'K' if name in h.K else 'C' if name in h.C else '?'
    if item is None:
        d.text((x0, y0), f"{name}: none", fill='#000', font=lab)
        continue
    strokes = flatten(item)
    want = counts.get(name, '?')
    d.rectangle((x0, y0 + 30, x0 + Z, y0 + 30 + Z), outline='#dddddd')
    d.text((x0, y0), f"{where}['{name}'] {len(strokes)} / {want}", fill='#000' if str(len(strokes)) in want.split() else '#c0392b', font=lab)
    s = Z / 1000
    taken = []                         # label spots: strokes that start together get theirs stacked
    for k, (kind, path) in enumerate(strokes):
        c = COLOURS[k % len(COLOURS)]
        for poly in points(path):
            pts = [(x0 + px * s, y0 + 30 + py * s) for px, py in poly]
            if len(pts) > 1:
                d.line(pts, fill=c, width=3)
            else:
                d.ellipse((pts[0][0] - 3, pts[0][1] - 3, pts[0][0] + 3, pts[0][1] + 3), fill=c)
        sx, sy = points(path)[0][0]
        lx, ly = x0 + sx * s + 3, y0 + 30 + sy * s - 16
        while any(abs(lx - tx) < 24 and abs(ly - ty) < 14 for tx, ty in taken):
            ly += 14
        taken.append((lx, ly))
        d.text((lx, ly), f'{k + 1}{kind}', fill=c, font=num)
img.save(a.out, quality=90)
print(a.out, img.size, len(names))
