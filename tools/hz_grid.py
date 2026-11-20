"""python tools/hz_grid.py OUT.jpg --batch A.py,B.py [CHARS] [--pen huasha] [--size 72] [--per 20]

A review grid: many characters in one pen, small, numbered by row, to read a
whole round at a glance. With no CHARS, every character the batches define.
"""
import argparse
import re
from pathlib import Path
import _repo
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument('out')
ap.add_argument('chars', nargs='?', default='')
ap.add_argument('--batch', default='')
ap.add_argument('--pen', default='huasha')
ap.add_argument('--bold', action='store_true')
ap.add_argument('--size', type=int, default=72)
ap.add_argument('--per', type=int, default=20)
a = ap.parse_args()

hs = _repo.load(a.batch)
import build
import hanzi

chars = a.chars or ''.join(dict.fromkeys(re.findall(
    r"^C\['(.)'\]\s*=", ''.join(Path(f).read_text(encoding='utf-8') for f in a.batch.split(',') if f), re.M)))
chars = [c for c in chars if c in hs.C]
st = build.STYLES[a.pen](bold=a.bold)
em = hanzi.CUTS[st.key]['em']


def tile(ch):
    img = build.canvas(st, ch)
    st.draw(ch, img)
    w = em / build.K * build.S
    cx0, cy = -build.X0 * build.S, (400 - build.Y0) * build.S
    c = img.crop((int(cx0), int(cy - w / 2), int(cx0 + w), int(cy + w / 2)))
    return c.resize((a.size, a.size), Image.LANCZOS)


G = a.size + 12
rows = -(-len(chars) // a.per)
im = Image.new('RGB', (a.per * G + 40, rows * (G + 14) + 20), (251, 248, 240))
d = ImageDraw.Draw(im)
lab = ImageFont.load_default()
for i, ch in enumerate(chars):
    x, y = 20 + (i % a.per) * G, 10 + (i // a.per) * (G + 14)
    d.text((x, y), str(i + 1), font=lab, fill=(170, 150, 130))
    im.paste(Image.new('RGB', (a.size, a.size), (43, 58, 85)), (x, y + 12), tile(ch))
    d.rectangle((x, y + 12, x + a.size, y + 12 + a.size), outline=(232, 222, 208))
im.save(a.out, quality=88)
print(a.out, im.size, len(chars))
