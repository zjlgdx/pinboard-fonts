"""Audit Chinese skeleton balance, bounding boxes and composite component gaps.

    .venv/bin/python tools/hz_balance.py [--top 25]

Scans hanzi.C directly (no bitmap rendering needed) and reports:
1. Composite characters ('lr' / 'tb') whose two halves overlap or sit too close.
2. Characters whose stroke centroid drifts furthest from the 500x500 centre.
3. Highest-density characters (stroke count) to guide optical weight checks.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import hanzi

NUM = re.compile(r'-?[\d.]+')


def points_of(strokes):
    pts = []
    for _kind, d in strokes:
        nums = [float(x) for x in NUM.findall(d)]
        for i in range(0, len(nums) - 1, 2):
            pts.append((nums[i], nums[i + 1]))
    return pts


def bbox_and_centroid(strokes):
    pts = points_of(strokes)
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys)), (sum(xs) / len(xs), sum(ys) / len(ys))


def is_cjk(ch):
    cp = ord(ch)
    return 0x3400 <= cp <= 0x9FFF or 0xF900 <= cp <= 0xFAFF


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--top', type=int, default=20, help='rows per section')
    args = ap.parse_args()

    tight_lr, tight_tb, off_center, dense = [], [], [], []
    for ch, item in hanzi.C.items():
        if not is_cjk(ch):
            continue
        flat = hanzi.flatten(item)
        res = bbox_and_centroid(flat)
        if not res:
            continue
        (x0, y0, x1, y1), (cx, cy) = res
        dist = ((cx - 500) ** 2 + (cy - 500) ** 2) ** 0.5
        off_center.append((dist, ch, cx, cy, len(flat)))
        dense.append((len(flat), ch, hanzi.density_scale(ch, flat, False), hanzi.density_scale(ch, flat, True)))

        if isinstance(item, tuple) and item[0] in ('lr', 'tb'):
            op, a, b, r = item[:4]
            gap = item[4] if len(item) > 4 else 0
            mid = 1000 * r
            if op == 'lr':
                ba = bbox_and_centroid(hanzi.flatten(a, (0, 0, mid - gap / 2, 1000)))
                bb = bbox_and_centroid(hanzi.flatten(b, (mid + gap / 2, 0, 1000, 1000)))
                if ba and bb:
                    clearance = bb[0][0] - ba[0][2]
                    tight_lr.append((clearance, ch, r, len(flat)))
            else:
                ba = bbox_and_centroid(hanzi.flatten(a, (0, 0, 1000, mid - gap / 2)))
                bb = bbox_and_centroid(hanzi.flatten(b, (0, mid + gap / 2, 1000, 1000)))
                if ba and bb:
                    clearance = bb[0][1] - ba[0][3]
                    tight_tb.append((clearance, ch, r, len(flat)))

    tight_lr.sort()
    tight_tb.sort()
    off_center.sort(reverse=True)
    dense.sort(reverse=True)

    print(f'Scanned {len(off_center)} CJK characters in hanzi.C\n')

    print(f'=== Tightest left-right (lr) clearances (top {args.top}) ===')
    for clr, ch, r, n in tight_lr[:args.top]:
        print(f'  {ch}  gap={clr:+6.1f}  r={r:.2f}  strokes={n}')

    print(f'\n=== Tightest top-bottom (tb) clearances (top {args.top}) ===')
    for clr, ch, r, n in tight_tb[:args.top]:
        print(f'  {ch}  gap={clr:+6.1f}  r={r:.2f}  strokes={n}')

    print(f'\n=== Furthest optical centroids from (500, 500) (top {args.top}) ===')
    for dist, ch, cx, cy, n in off_center[:args.top]:
        print(f'  {ch}  dist={dist:5.1f}  centre=({cx:5.1f}, {cy:5.1f})  strokes={n}')

    print(f'\n=== Densest characters & optical pen scales (top {args.top}) ===')
    for n, ch, sr, sb in dense[:args.top]:
        print(f'  {ch}  strokes={n:2d}  scale(Reg)={sr:.3f}  scale(Bold)={sb:.3f}')


if __name__ == '__main__':
    main()
