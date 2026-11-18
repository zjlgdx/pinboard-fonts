"""python tools/check_fonts.py [OUT_DIR] [--private REGEX]

The checks before a pull request, on the built fonts in OUT_DIR (default out/):

- every font's head.fontRevision is build.py's VERSION (the fonts are fresh);
- the OpenType Sanitizer passes every .otf;
- fontbakery check-universal, per family, has no FAIL or FATAL (its full
  report goes to OUT_DIR/fontbakery-FAMILY.txt, one file per checkout, so
  checks can run side by side);
- no personal data: emails, home or temp paths, or anything --private matches
  (or the PINBOARD_PRIVATE environment variable), in the .otf files or the
  .woff2 files decompressed.

Exits 1 if any of them fails. The known warnings (file size; in the
Typewriter, the CFF fonts' glyf error and the double-width xAvgCharWidth) are
printed, not failed.
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
import _repo

ap = argparse.ArgumentParser()
ap.add_argument('out', nargs='?', default=str(_repo.ROOT / 'out'))
ap.add_argument('--private', default=os.environ.get('PINBOARD_PRIVATE', ''))
a = ap.parse_args()
out = Path(a.out)
otfs = sorted(out.glob('*.otf'))
bad = []

from fontTools.ttLib import TTFont
import ots

version = float(re.search(r'^VERSION = ([0-9.]+)', (_repo.ROOT / 'build.py').read_text(), re.M).group(1))
print('== versions', version)
for f in otfs:
    rev = round(TTFont(f)['head'].fontRevision, 3)
    if rev != version:
        bad.append(f'{f.name} is {rev}, not {version}')
        print(' ', f.name, rev)

print('== OTS')
for f in otfs:
    p = ots.sanitize(str(f), os.devnull, capture_output=True)
    print(f'  {f.name}: {"pass" if p.returncode == 0 else "FAIL " + (p.stderr or b"").decode()[:200]}')
    if p.returncode:
        bad.append(f'OTS {f.name}')

print('== fontbakery check-universal')
fb = Path(sys.executable).with_name('fontbakery')
for fam in sorted({f.name.split('-')[0] for f in otfs}):
    log = out / f'fontbakery-{fam}.txt'
    with log.open('w') as fh:
        subprocess.run([str(fb), 'check-universal', *map(str, sorted(out.glob(f'{fam}-*.otf')))], stdout=fh, stderr=subprocess.STDOUT)
    txt = log.read_text(errors='replace')
    counts = dict(re.findall(r'\b(ERROR|FATAL|FAIL|WARN): (\d+)', txt))
    print(f'  {fam}: ' + ' '.join(f'{k} {v}' for k, v in counts.items()))
    for line in txt.splitlines():
        if re.match(r'^\s*(?:[^\w\s]+\s*)?(FAIL|FATAL|ERROR|WARN)\s', line):   # not the legend's 'A FAIL is ...'
            print('     ' + line.strip()[:100])
    if int(counts.get('FAIL', 0)) or int(counts.get('FATAL', 0)):
        bad.append(f'fontbakery {fam}')

print('== personal data')
pat = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z.]{2,}|/Users/|/home/|/private/tmp|/tmp/|C:\\\\Users'
if a.private:
    pat += '|' + a.private
rx = re.compile(pat.encode(), re.I)
with tempfile.TemporaryDirectory() as t:
    files = list(otfs)
    for w in sorted(out.glob('*.woff2')):
        f = TTFont(w)
        f.flavor = None
        f.save(Path(t) / (w.name + '.sfnt'))
        files.append(Path(t) / (w.name + '.sfnt'))
    hits = [f.name for f in files if rx.search(f.read_bytes())]
print('  hits:', ', '.join(hits) or 'none', f'({len(files)} files)')
if hits:
    bad.append('personal data in ' + ', '.join(hits))

print('== ' + ('FAILED: ' + '; '.join(bad) if bad else 'all passed'))
sys.exit(1 if bad else 0)
