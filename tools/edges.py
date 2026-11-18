"""python tools/edges.py [--batch A.py,B.py] [--chars CHARS] [STYLE-WEIGHT ...]

Draws each character in each pen, on the same canvas the build uses
(build.canvas), and lists the ones whose ink reaches the canvas edge: the
build would cut them off. Run it before a build; the build says the same, but
an hour later. With no STYLE-WEIGHT, all six fonts, in parallel. With no
--chars, every character in hanzi_strokes (and the batches).

Common causes: a component that is drawn in place on the full 1000 grid
(爫 雨 宀 冖 罒 ...) squeezed into a flat rect, or a stroke that starts on the
grid's top edge (y < 30). The pens' jitter depends on the canvas, which is a
cell wider in the Typewriter, so only this canvas tells.
"""
import argparse
import sys
from concurrent.futures import ProcessPoolExecutor
import _repo

ALL = [f'{s}-{w}' for s in ('typewriter', 'ballpoint', 'marker') for w in ('regular', 'bold')]


def check(job):
    key, batch, chars = job
    _repo.load(batch)
    import numpy as np
    import build
    import hanzi
    style, weight = key.split('-')
    st = build.STYLES[style](bold=weight == 'bold')
    bad = []
    chars = [ch for ch in chars if ch in hanzi.C] if chars else list(hanzi.C)
    for ch in chars:
        e = np.asarray(st.draw(ch, build.canvas(st, ch), 0))
        if e[:2].any() or e[-2:].any() or e[:, :2].any() or e[:, -2:].any():
            bad.append(ch)
    return key, len(chars), ''.join(bad)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('styles', nargs='*', default=ALL)
    ap.add_argument('--batch', default='')
    ap.add_argument('--chars', default='')
    a = ap.parse_args()
    cut = False
    with ProcessPoolExecutor(len(a.styles)) as ex:
        for key, n, bad in ex.map(check, [(s, a.batch, a.chars) for s in a.styles]):
            print(f'{key}: {n} drawn, cut: {bad or "none"}')
            cut |= bool(bad)
    sys.exit(1 if cut else 0)
