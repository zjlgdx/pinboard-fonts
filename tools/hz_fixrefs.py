"""python tools/hz_fixrefs.py BATCH.py [EARLIER.py,...]

Rewrites BATCH.py in place: K['x'] becomes C['x'] (or the other way) where only
the other one exists, and lists references to anything not defined anywhere.
"""
import re
import sys
from pathlib import Path
import _repo

p = Path(sys.argv[1])
src = p.read_text(encoding='utf-8')
h = _repo.load(sys.argv[2] if len(sys.argv) > 2 else '')
own_k = set(re.findall(r"^K\['([^']+)'\]\s*=", src, re.M))
own_c = set(re.findall(r"^C\['([^']+)'\]\s*=", src, re.M))


def fix(m):
    d, k = m.group(1), m.group(2)
    has_k, has_c = k in h.K or k in own_k, k in h.C or k in own_c
    if d == 'K' and not has_k and has_c:
        return f"C['{k}']"
    if d == 'C' and not has_c and has_k:
        return f"K['{k}']"
    if d == 'L' and k not in h.L:
        print('unknown L', k)
    if d in 'KC' and not has_k and not has_c:
        print('unknown', d, k)
    return m.group(0)


p.write_text(re.sub(r"\b([KCL])\['([^']+)'\](?!\s*=)", fix, src), encoding='utf-8')
