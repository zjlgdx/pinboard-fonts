"""python tools/hz_dupes.py BATCH.py [BATCH.py ...]

Rounds drafted side by side may each define the same component. Lists every
K[...] or C[...] that a batch defines again, after hanzi_strokes.py or an
earlier batch (in the order given) already has it. A later definition
replaces the earlier one for everything after it, so keep one: drop the
later one if the earlier serves, or move the better one up.
"""
import re
import sys
from pathlib import Path
import _repo

DEF = re.compile(r"^([KCL])\['([^']+)'\]\s*=", re.M)
first = {}
for m in DEF.finditer((_repo.ROOT / 'hanzi_strokes.py').read_text(encoding='utf-8')):
    first.setdefault((m.group(1), m.group(2)), 'hanzi_strokes.py')
dupes = 0
for b in sys.argv[1:]:
    for m in DEF.finditer(Path(b).read_text(encoding='utf-8')):
        key = (m.group(1), m.group(2))
        if key in first:
            print(f'{b}: {key[0]}[{key[1]!r}] again (first in {first[key]})')
            dupes += 1
        else:
            first[key] = b
print(dupes, 'defined again')
