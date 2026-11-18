"""python tools/merge_round.py ROWS VERSION BATCH.py [BATCH.py ...]

Merges a round: puts the batches into hanzi_strokes.py (before the mainland
block), sets VERSION in build.py, and updates the README's counts for the
first ROWS rows of hanzi_order.tsv. Run it in the checkout that gets the round.
"""
import re
import subprocess
import sys
from pathlib import Path
import _repo

R = _repo.ROOT
rows, version, batches = int(sys.argv[1]), sys.argv[2], sys.argv[3:]

hs = R / 'hanzi_strokes.py'
text = hs.read_text(encoding='utf-8')
i = text.index('# Mainland China sets the full-width marks')
add = '\n\n'.join(Path(b).read_text(encoding='utf-8').strip('\n') for b in batches)
hs.write_text(text[:i].rstrip('\n') + '\n\n' + add + '\n\n\n' + text[i:], encoding='utf-8')

bp = R / 'build.py'
b, n = re.subn(r'^VERSION = [0-9.]+(\s+#)', f'VERSION = {version}\\1', bp.read_text(encoding='utf-8'), flags=re.M)
assert n == 1, 'VERSION line not found'
bp.write_text(b, encoding='utf-8')

# Count in a fresh interpreter: hanzi_strokes has just changed on disk.
count = int(subprocess.check_output(
    [sys.executable, '-c', "import hanzi_strokes as h; print(sum('\\u3400' <= c <= '\\u9fff' for c in h.C))"],
    cwd=R, text=True))
order = _repo.rows()
cover = sum(int(r[1]) for r in order[:rows]) / sum(int(r[1]) for r in order) * 100
# Whole percents, but never round up to 100: past 99.5, one decimal.
pct = int(cover + 0.5) if cover < 99.5 else round(cover, 1)

rd = R / 'README.md'
r = rd.read_text(encoding='utf-8')
r, n1 = re.subn(r'every character in the first [0-9,]+ rows of \[`hanzi_order.tsv`\]\(hanzi_order.tsv\): [0-9,]+ in all',
                f'every character in the first {rows} rows of [`hanzi_order.tsv`](hanzi_order.tsv): {count} in all', r)
r, n2 = re.subn(r'The first [0-9,]+ rows are [0-9,]+ characters across both scripts, and cover [0-9.]+% of the corpus.',
                f'The first {rows:,} rows are {count:,} characters across both scripts, and cover {pct}% of the corpus.', r)
assert n1 == 1 and n2 == 1, f'README sentences not found ({n1}, {n2})'
rd.write_text(r, encoding='utf-8')
print(f'rows {rows}, version {version}, {count} hanzi, {cover:.2f}% of the corpus')
