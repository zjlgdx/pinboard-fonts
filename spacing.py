"""Spacing and kerning test sheet for the built fonts: out/spacing.png."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
OUT = Path(__file__).resolve().parent / 'out'
LINES = ['nnnonnnoonnn  HHHOHHHOOHHH  000100', 'hamburgefonstiv  minimum  illicit',
         'To Ty Yo We Av LT P. r. F, "A" (j) f/',  'bookkeeper little coffee 11:00 — ok?',
         "\\ ^ ` { | } ~ … °"]
fonts = sorted(OUT.glob('*.otf'))
img = Image.new('RGB', (1800, 400 * len(fonts)), '#f5ecda'); d = ImageDraw.Draw(img)
for i, f in enumerate(fonts):
    font = ImageFont.truetype(str(f), 62)
    for j, line in enumerate(LINES):
        d.text((24, 400 * i + 14 + j * 76), line, fill='#2b3a55', font=font)
img.save(OUT / (sys.argv[1] if len(sys.argv) > 1 else 'spacing.png'))
