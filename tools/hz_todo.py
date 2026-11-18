"""python tools/hz_todo.py FIRST LAST [BATCH.py,...]

The characters of rows FIRST..LAST of hanzi_order.tsv not drawn yet (with the
batches added), in order: what a round still has to draw.
"""
import sys
import _repo

lo, hi = int(sys.argv[1]), int(sys.argv[2])
h = _repo.load(sys.argv[3] if len(sys.argv) > 3 else '')
todo = [ch for ch in _repo.chars_of(lo, hi) if ch not in h.C]
print(len(todo), ''.join(todo))
