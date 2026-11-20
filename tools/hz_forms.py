"""tools/hz_forms.py [--batch A.py,B.py]

Checks that each character is drawn in its own script's form of the parts
Taiwan and the mainland write differently (hanzi_strokes._TW_PARTS: 艹 as
十十 or 一 across, 敖 with or without the 點, 戶 or 户, 阝 in three strokes or two):

- a character both scripts write (shared) that uses a Taiwan part has a ZHS
  form, and that form is the drawing with the mainland's parts;
- a Simplified-only character uses no Taiwan part.

Which script has a character: hanzi_order.tsv's columns, and Unihan's kTGH
(in 通用规范汉字表 at any level, so the mainland writes it too: 著 and 藉 sit
in the Traditional column of 着's and 借's rows) when work/unihan is there.
Exits 1 on any problem; check_fonts.py runs it.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _repo

ap = argparse.ArgumentParser()
ap.add_argument('--batch', default='')
a = ap.parse_args()
h = _repo.load(a.batch)
from hanzi import flatten  # noqa: E402  (after the batches are in)

simp, trad = set(), set()
for r in _repo.rows():
    simp.update(c for c in r[2] if c != '-')
    trad.update(c for c in r[3] if c != '-')

# Past the rows: in 通用规范汉字表 means the mainland writes it too.
common = subprocess.check_output(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'],
                                 cwd=_repo.ROOT, text=True).strip()
places = [Path(p) for p in (os.environ.get('UNIHAN'),) if p] + [_repo.ROOT / 'work/unihan', Path(common).parent / 'work/unihan']
unihan = next((p for p in places if (p / 'Unihan_OtherMappings.txt').exists()), None)
tgh = set()
if unihan:
    for line in open(unihan / 'Unihan_OtherMappings.txt', encoding='utf-8'):
        p = line.split('\t')
        if len(p) == 3 and p[1] == 'kTGH':
            tgh.add(chr(int(p[0][2:], 16)))


def han(c):
    return len(c) == 1 and ('㐀' <= c <= '鿿' or '\U00020000' <= c <= '\U0003ffff')


bad = []
for ch, v in h.C.items():
    if not han(ch):
        continue
    mainland = flatten(h._mainland(v))
    if mainland == flatten(v):
        continue                       # no Taiwan part
    in_simp = ch in simp or ch in tgh   # 著 藉 are Traditional on their rows, and the mainland's too
    in_trad = ch in trad or ch not in simp
    if in_simp and not in_trad:
        bad.append(f'{ch} is Simplified only but draws a Taiwan part')
    elif in_simp:
        if ch not in h.ZHS:
            bad.append(f'{ch} is shared and has a Taiwan part, but no ZHS form')
        elif flatten(h.ZHS[ch]) != mainland:
            bad.append(f"{ch}'s ZHS form is not its drawing with the mainland's parts")
print(f'  {len(bad)} problems' + (': ' + '; '.join(bad) if bad else ''))
sys.exit(1 if bad else 0)
