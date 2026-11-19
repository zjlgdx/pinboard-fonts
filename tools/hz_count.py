"""tools/hz_count.py [--batch A.py,B.py] [--all]

Counts the strokes each drawn character and component has and compares them
with Unihan's kTotalStrokes (work/unihan, as order.py reads it). A component
that is itself a character (K['豕']) is checked too, and comes first: a part
drawn with a stroke too many or too few puts every character that uses it
wrong, so fix the part. Characters whose difference is explained by such a
part are listed under it, not again on their own.

A stroke here is one S() item. A few strokes are drawn as two items (a turn
split in two), so a difference of one is a lead to look at, not a verdict:
look at the character on a sheet and count again before changing it.
"""
import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _repo

ap = argparse.ArgumentParser()
ap.add_argument('--batch', default='')
ap.add_argument('--all', action='store_true', help='also list characters explained by a part')
a = ap.parse_args()

h = _repo.load(a.batch)


def unihan_counts():
    out = {}
    roots = [_repo.ROOT / 'work/unihan']
    for root in roots:
        f = root / 'Unihan_IRGSources.txt'
        if f.exists():
            for line in open(f, encoding='utf-8'):
                p = line.rstrip('\n').split('\t')
                if len(p) == 3 and p[1] == 'kTotalStrokes':
                    out[chr(int(p[0][2:], 16))] = {int(v) for v in p[2].split()}
            return out
    sys.exit('needs Unihan in work/unihan (see order.py)')


def inner(x):
    """The parts a box, an 'lr' or a 'tb' holds."""
    if isinstance(x, tuple) and x and x[0] == 'box':
        return [part for part, _ in x[1]]
    if isinstance(x, tuple) and len(x) == 4 and x[0] in ('lr', 'tb'):
        return [x[1], x[2]]
    return None


def count(x):
    """Strokes in a drawing: S() items, through any boxes."""
    if inner(x) is not None:
        return sum(count(part) for part in inner(x))
    if isinstance(x, list):
        return sum(count(i) for i in x)
    if isinstance(x, tuple) and len(x) == 2 and isinstance(x[0], str) and len(x[0]) == 1:
        return 1
    return 0


def parts(x, seen):
    """The K components a drawing uses, by identity, outermost first."""
    for part in inner(x) or []:
        if id(part) in KNAME:
            seen.append(KNAME[id(part)])
        parts(part, seen)
    return seen


def is_han(s):
    return len(s) == 1 and ('㐀' <= s <= '鿿' or '\U00020000' <= s <= '\U0003ffff')


strokes = unihan_counts()
KNAME = {id(v): k for k, v in h.K.items() if isinstance(v, (list, tuple))}

bad_parts = {}
for k, v in h.K.items():
    if is_han(k) and k in strokes:
        n = count(v)
        if n and n not in strokes[k]:
            bad_parts[k] = (n, strokes[k])

explained = defaultdict(list)
alone = []
for ch, v in h.C.items():
    if not is_han(ch) or ch not in strokes:
        continue
    n = count(v)
    if n in strokes[ch]:
        continue
    used = [p for p in parts(v, []) if p in bad_parts]
    if used:
        explained[used[0]].append((ch, n, strokes[ch]))
    else:
        alone.append((ch, n, strokes[ch]))


def want(s):
    return '/'.join(str(i) for i in sorted(s))


print(f'== parts with a count off Unihan: {len(bad_parts)}')
for k, (n, s) in sorted(bad_parts.items(), key=lambda kv: -len(explained[kv[0]])):
    users = explained[k]
    line = f"  K['{k}'] {n} for {want(s)}; {len(users)} characters off with it"
    if a.all and users:
        line += ': ' + ' '.join(c for c, _, _ in users)
    print(line)
print(f'== characters off on their own: {len(alone)}')
for ch, n, s in sorted(alone, key=lambda t: (abs(t[1] - min(t[2], key=lambda v: abs(v - t[1]))), t[0]), reverse=True):
    print(f'  {ch} U+{ord(ch):04X} {n} for {want(s)}')
