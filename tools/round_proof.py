"""python tools/round_proof.py FIRST LAST OUT.jpg [--fonts out] [--hant LINE] [--hans LINE]

A round's proof from the built fonts: one line of Taiwan's text and one of the
mainland's in every family and weight, then every character of rows
FIRST..LAST, in the Ballpoint Regular. Labels are set in the built Typewriter.
"""
import argparse
import sys
from pathlib import Path
import _repo
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument('first', type=int)
ap.add_argument('last', type=int)
ap.add_argument('out')
ap.add_argument('--fonts', default=str(_repo.ROOT / 'out'))
ap.add_argument('--hant', default='寒冬的清晨，雲很低，我們登上小島，詩人說這裡的香味最迷人。')
ap.add_argument('--hans', default='寒冬的清晨，云很低，我们登上小岛，诗人说这里的香味最迷人。')
a = ap.parse_args()
fonts = Path(a.fonts)

new = _repo.chars_of(a.first, a.last)
fams = [(f'Pinboard{n}-{w}', n, w) for n in ('Typewriter', 'Ballpoint', 'Marker') for w in ('Regular', 'Bold')]
cmap = TTFont(fonts / 'PinboardBallpoint-Regular.otf').getBestCmap()
miss = [c for c in a.hant + a.hans + ''.join(new) if c.strip() and ord(c) not in cmap]
if miss:
    sys.exit('not in the fonts: ' + ''.join(miss))

INK, PAPER, LABEL = '#2b3a55', '#f7f1e3', '#a5683c'
lab = ImageFont.truetype(str(fonts / 'PinboardTypewriter-Regular.otf'), 20)
SZ, COLS, G = 46, 24, 58
W = max(60 + COLS * G, 1800)
H = 40 + len(fams) * 2 * 64 + 60 + -(-len(new) // COLS) * G + 40
img = Image.new('RGB', (W, H), PAPER)
d = ImageDraw.Draw(img)
y = 30
for stem, n, w in fams:
    f = ImageFont.truetype(str(fonts / f'{stem}.otf'), 40)
    d.text((30, y + 4), f'{n} {w}', fill=LABEL, font=lab)
    d.text((260, y - 6), a.hant, fill=INK, font=f)
    y += 64
    d.text((260, y - 6), a.hans, fill=INK, font=f, language='zh-Hans')
    y += 64
y += 20
d.text((30, y), f'rows {a.first}-{a.last}: {len(new)} characters, Ballpoint Regular', fill=LABEL, font=lab)
y += 40
f = ImageFont.truetype(str(fonts / 'PinboardBallpoint-Regular.otf'), SZ)
for i, ch in enumerate(new):
    d.text((30 + (i % COLS) * G, y + (i // COLS) * G), ch, fill=INK, font=f)
img.save(a.out, quality=88)
print(a.out, img.size, len(new))
