"""Spacing, kerning and alternates test sheet, shaped by a real browser:
writes out/sheet.html and screenshots it to out/<name>.png."""
import subprocess, sys
from pathlib import Path
OUT = Path(__file__).resolve().parent / 'out'
LINES = ['nnnonnnoonnn HHHOHHHOOHHH 000100', 'hamburgefonstiv minimum illicit',
         'To Ty Yo We Av LT P. r. F, “A” (j) f/', 'bookkeeper little coffee 11:00 — ok?',
         'Wave Tavern Lyft “Yes,” said P.J.', '\\ ^ ` { | } ~ … ° • 0O 1lI']
fonts = sorted(OUT.glob('*.woff2'))
css = ''.join(f"@font-face{{font-family:'{f.stem}';src:url({f.name})}}" for f in fonts)
body = ''.join(f"<div style=\"font-family:'{f.stem}'\">" + ''.join(f'<p>{l}</p>' for l in LINES) + '</div>' for f in fonts)
(OUT / 'sheet.html').write_text(f"<!doctype html><meta charset=utf-8><style>{css}body{{margin:14px 24px;background:#f5ecda;color:#2b3a55;font-size:54px;line-height:1.24}}p{{margin:0}}div{{margin-bottom:22px}}</style>{body}")
name = sys.argv[1] if len(sys.argv) > 1 else 'sheet'
subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--headless=new', '--disable-gpu', '--hide-scrollbars',
                '--window-size=1500,1500', '--virtual-time-budget=2000', f'--screenshot={OUT / (name + ".png")}', (OUT / 'sheet.html').as_uri()],
               stderr=subprocess.DEVNULL, check=True)
