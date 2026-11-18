"""python tools/hz_have.py CHARS [BATCH.py,...]

Which of CHARS are already drawn, and where: L (left-hand forms), K
(components), C (characters). Look before drawing a component again.
"""
import sys
import _repo

h = _repo.load(sys.argv[2] if len(sys.argv) > 2 else '')
out = {'none': ''}
for ch in sys.argv[1]:
    tag = ''.join(t for t, d in (('L', h.L), ('K', h.K), ('C', h.C)) if ch in d) or 'none'
    out[tag] = out.get(tag, '') + ch
for k, v in out.items():
    print(k, v)
