"""What the tools share: the repository they sit in, and a round's draft batches.

A batch is a Python file of `K[...] = ...` and `C[...] = ...` lines, written the
way hanzi_strokes.py is. Until a round is merged, batches live in work/ (not
committed) and are run into hanzi_strokes's namespace, so every tool sees the
font as it will be.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def load(batches=''):
    """Import hanzi_strokes with the batches (comma-separated paths) run into it."""
    import hanzi_strokes
    for f in [b for b in batches.split(',') if b]:
        exec(Path(f).read_text(encoding='utf-8'), hanzi_strokes.__dict__)
    return hanzi_strokes


def rows():
    """hanzi_order.tsv as [rank, count, simplified, traditional, level-1 index]."""
    out = []
    for line in (ROOT / 'hanzi_order.tsv').open(encoding='utf-8'):
        if line.startswith('#'):
            continue
        r = line.rstrip('\n').split('\t')
        if r[0].isdigit():
            out.append(r)
    return out


def chars_of(lo, hi):
    """Every form in rows lo..hi, in order, each once."""
    seen = {}
    for r in rows():
        if lo <= int(r[0]) <= hi:
            for ch in r[2] + r[3]:
                if ch != '-':       # no Simplified form in level 1
                    seen.setdefault(ch, None)
    return list(seen)
