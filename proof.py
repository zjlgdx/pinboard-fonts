"""A quick proof sheet of the built fonts: out/proof.png."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / 'out'
LINES = [
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    'abcdefghijklmnopqrstuvwxyz 0123456789',
    'The quick brown fox jumps over the lazy dog.',
    '“Pin it!” — 3 notes, 2 tags & a ticket (#42) @ 9:30?',
]
fonts = sorted(OUT.glob('*.otf'))
img = Image.new('RGB', (1800, 330 * len(fonts)), '#f5ecda')
d = ImageDraw.Draw(img)
for i, f in enumerate(fonts):
    y = 330 * i + 20
    d.text((30, y), f.stem, fill='#a5683c', font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Courier New.ttf', 22))
    font = ImageFont.truetype(str(f), 54)
    for j, line in enumerate(LINES):
        d.text((30, y + 40 + j * 68), line, fill='#2b3a55', font=font)
img.save(OUT / 'proof.png')
print(OUT / 'proof.png')
