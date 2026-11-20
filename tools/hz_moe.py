"""tools/hz_moe.py COUNTS.json [--batch A.py,B.py]

Compares each Taiwan-form drawing's stroke count with 教育部's: COUNTS.json is
{character: strokes}, the number of frames 教育部《常用國字標準字體筆順學習網》
shows for each character, counted while viewing its frames in a browser (the
images themselves are never saved). It is the authority for Traditional
characters where Unihan's kTotalStrokes is not: Unihan counts 辶 as 4 and 阝
as 3 for both scripts, 都 as 12 and 這 as 8, and Taiwan's 者 has no 點.

Prints the characters whose count differs, then the parts most of whose users
differ: fix a part once rather than each character. A frame count is one too
high where the last frame of a tall character spills into the next slot or
repeats the finished character (煎 寓 絮 榻 製 劍 慰 裝 奘 瞞 窯): look at the
frames before changing a drawing.
"""
import argparse
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _repo

ap = argparse.ArgumentParser()
ap.add_argument('counts')
ap.add_argument('--batch', default='')
a = ap.parse_args()
moe = json.load(open(a.counts, encoding='utf-8'))
h = _repo.load(a.batch)
from hanzi import flatten  # noqa: E402  (after the batches are in)

NAME = {}
for prefix, table in (('L', h.L), ('K', h.K)):
    for k, v in table.items():
        NAME.setdefault(id(v), f"{prefix}['{k}']")


def inner(x):
    if isinstance(x, tuple) and x and x[0] == 'box':
        return [p for p, _ in x[1]]
    if isinstance(x, tuple) and len(x) == 4 and x[0] in ('lr', 'tb'):
        return [x[1], x[2]]
    return None


def parts(x, seen):
    for p in inner(x) or []:
        if id(p) in NAME:
            seen.add(NAME[id(p)])
        parts(p, seen)
    return seen


off, users = {}, collections.defaultdict(list)
for ch, m in moe.items():
    if not isinstance(m, int) or ch not in h.C:
        continue
    v = h.C[ch]
    d = len(flatten(v)) - m
    if d:
        off[ch] = d
    for p in parts(v, {NAME[id(v)]} if id(v) in NAME else set()):
        users[p].append(ch)

print(f'== characters off 教育部: {len(off)} of {sum(isinstance(m, int) and c in h.C for c, m in moe.items())}')
for ch, d in sorted(off.items(), key=lambda x: (-abs(x[1]), x[0])):
    print(f'  {ch} {len(flatten(h.C[ch]))} for {moe[ch]}')
print('== parts most of whose users are off')
for p, us in sorted(users.items(), key=lambda x: -len(x[1])):
    o = [c for c in us if c in off]
    if len(o) >= 2 and len(o) / len(us) >= 0.4:
        print(f'  {p}: {len(o)} of {len(us)} off: {"".join(o[:20])}')
