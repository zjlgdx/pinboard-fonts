"""Spacing, kerning, alternates and character-set test sheet, shaped by a
real browser: writes out/sheet.html and screenshots it.

    .venv/bin/python sheet.py                      # out/sheet.png
    .venv/bin/python sheet.py docs/specimen.png    # the README's specimen
"""
import html
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'out'
FAMILIES = ['YisuHuasha', 'YisuLouhen', 'YisuYinni']
SIZE = 40
# Spacing strings, kerning pairs, alternates, then the wider character set.
LINES = ['nnnonnnoonnn HHHOHHHOOHHH 000100 hamburgefonstiv',
         'To Ty Yo We Av LT P. r. F, “A” (j) f/ bookkeeper 11:00',
         'Ça déjà vu? Zürich, São Paulo, Ærøskøbing, Œuvre, Ñandú',
         'Łódź, Křižík, Győr, İstanbul, Ţară, Ģirts, ďaleký, Ĳssel ◌̂',
         '€12 £3 ¥5 ¢ © ® ™ ± ÷ ≠ ≤ ¿¡ «oui» ½ ¾ § ¶ ← → ✓ ✗',
         '\\ ^ ` { | } ~ … ° • 0O 1lI']
BOLD = 'Bold: hamburgefonstiv, Zürich €12 ✓'
# Yinni as a terminal: box drawing, blocks and Claude Code's marks.
TERMINAL = ['╭───────────────────────────────╮ ┌──┬──┐ ╔══╗ ▛▀▜',
            '│ ✻ Welcome to Claude Code      │ ├──┼──┤ ║░▒║ ▌█▐',
            '╰───────────────────────────────╯ └──┴──┘ ╚══╝ ▙▄▟',
            '❯ build the fonts  ⏺ Bash(build.py) ✓ ✗ ● ○',
            '  ⎿  0 FAIL ·✢✳✶✻✽ ⏵⏵ ⏸ ☐ ☒ ░▒▓█ ▁▂▃▄▅▆▇█ ←→↑↓']


def para(text, family, bold=False):
    weight = 'Bold' if bold else 'Regular'
    return f"<p style=\"font-family:'{family}-{weight}'\">{html.escape(text)}</p>"


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT / 'sheet.png'
    css = ''.join(f"@font-face{{font-family:'{f.stem}';src:url({f.name})}}" for f in sorted(OUT.glob('*.woff2')))
    body, rows = '', 0
    for fam in FAMILIES:
        lines = LINES + (TERMINAL if fam == 'YisuYinni' else [])   # Yinni
        body += '<div>' + ''.join(para(l, fam) for l in lines) + para(BOLD, fam, bold=True) + '</div>'
        rows += len(lines) + 1
    page = OUT / 'sheet.html'
    page.write_text(f'<!doctype html><meta charset=utf-8><style>{css}'
                    f'body{{margin:14px 24px;background:#f5ecda;color:#2b3a55;font-size:{SIZE}px;line-height:1.24}}'
                    f'p{{margin:0;white-space:pre}}div{{margin-bottom:22px}}</style>{body}')
    # Box drawing joins only when the line is exactly the font's 1.24 em.
    height = round(rows * SIZE * 1.24 + 28 + 22 * len(FAMILIES))
    subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--headless=new', '--disable-gpu',
                    '--hide-scrollbars', f'--window-size=1500,{height}', '--virtual-time-budget=2000',
                    f'--screenshot={target.resolve()}', page.as_uri()], stderr=subprocess.DEVNULL, check=True)
    print(target)


if __name__ == '__main__':
    main()
