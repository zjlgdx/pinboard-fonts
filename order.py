"""The order Chinese is drawn in: most frequent first, Traditional and
Simplified together.

    python order.py <folder with Unihan's .txt files>  >  hanzi_order.tsv

(work/unihan/ keeps a copy; it isn't committed.)

Source: the Unicode Han Database (Unihan, UAX #38), under the Unicode
License v3 (https://www.unicode.org/terms_of_use.html). Facts about
characters only; no glyphs.

- kHanyuPinlu gives each reading's count in the corpus of 《現代漢語頻率詞典》
  (1,807,389 characters). A character's count is the sum over its readings.
- That corpus is mainland Chinese, in Simplified characters. A Simplified
  character's Traditional forms (kTraditionalVariant) take its place in the
  order, so one row is a character as both scripts write it. Only forms in
  the first plane of CNS 11643 (kIRG_TSource T1, Taiwan's common
  characters) count as Taiwan's.
- kTGH says which characters are in the first level (index 1-3500) of
  mainland China's 通用规范汉字表 (2013).

Each row: rank, count, the Simplified form, its Traditional forms (the same
character where both write it alike), and the 通用规范汉字表 level-1 index or
'-' (a Traditional form in level 1 itself adds its own: 干 乾干幹 23 乾:2215).
A round draws the next rows in order, every form in them.

After the frequency rows come the characters with no count that the fonts
still owe: the rest of level 1, and of Taiwan's 4,808 common characters
(moe_4808.tsv, plus 汨: see that file). Their count is 0 and they are sorted by
kRSUnicode, radical then strokes, so a round draws a radical's family
together. A level-1 character brings its Traditional forms, as above. A
character only Taiwan's list has gets '-' for its Simplified form when the
mainland writes it differently: that form isn't in level 1.
"""
import re
import sys
from pathlib import Path


def fields(folder, name, field):
    out = {}
    for line in (Path(folder) / name).read_text(encoding='utf-8').splitlines():
        if line.startswith('U+'):
            cp, f, value = line.split('\t', 2)
            if f == field:
                out[chr(int(cp[2:], 16))] = value
    return out


def chars(value):
    return [chr(int(u[2:].split('<')[0], 16)) for u in value.split()]


def radical_strokes(value):
    """kRSUnicode '120.6' or "213'.0" -> (120, 0, 6): radical, simplified, strokes."""
    rad, strokes = value.split()[0].split('.')
    return int(rad.rstrip("'")), rad.count("'"), int(strokes)


def moe_4808(path):
    out = [chr(int(line.split('\t')[1][2:], 16)) for line in Path(path).read_text(encoding='utf-8').splitlines()
           if line.startswith('A')]
    assert len(out) == 4808, len(out)
    return out + ['汨']     # A02149: printed 汨, coded 汩; both are drawn


def main(folder, moe_path=Path(__file__).with_name('moe_4808.tsv')):
    pinlu = fields(folder, 'Unihan_Readings.txt', 'kHanyuPinlu')
    trad = fields(folder, 'Unihan_Variants.txt', 'kTraditionalVariant')
    tgh = fields(folder, 'Unihan_OtherMappings.txt', 'kTGH')
    taiwan = {ch for ch, v in fields(folder, 'Unihan_IRGSources.txt', 'kIRG_TSource').items() if v.startswith('T1-')}
    count = {ch: sum(int(n) for n in re.findall(r'\((\d+)\)', v)) for ch, v in pinlu.items()}

    def forms_of(ch):
        """How Taiwan writes ch: its Traditional variants in CNS 11643's
        first plane, Taiwan's common characters (后 -> 后 後, 里 -> 里 裡;
        not 説, Japan's form of 說, nor 裏)."""
        if ch not in trad:
            return [ch]
        return [t for t in chars(trad[ch]) if t in taiwan] or [ch]
    # A Traditional form takes its Simplified character's row, so it's
    # never ranked on its own.
    merged = {t for ch in count for t in forms_of(ch) if t != ch}
    rows = []
    for ch, n in sorted(count.items(), key=lambda kv: (-kv[1], ord(kv[0]))):
        if ch not in merged:
            rows.append((ch, n, forms_of(ch)))

    # Past the frequency list: the rest of level 1 and of Taiwan's 4,808.
    simp = fields(folder, 'Unihan_Variants.txt', 'kSimplifiedVariant')
    rs = fields(folder, 'Unihan_IRGSources.txt', 'kRSUnicode')
    level_1 = {ch for ch, v in tgh.items() if any(int(i) <= 3500 for i in re.findall(r'2013:(\d+)', v))}
    seen = {f for _, _, forms in rows for f in forms} | {ch for ch, _, _ in rows}
    more = []
    for ch in sorted(level_1 - seen, key=ord):
        more.append((ch, 0, forms_of(ch)))
    seen |= {f for _, _, forms in more for f in forms} | {ch for ch, _, _ in more}
    for t in moe_4808(moe_path):
        if t not in seen:
            same = t not in simp or t in chars(simp[t])
            more.append((t if same else '-', 0, [t]))
            seen.add(t)
    more.sort(key=lambda r: (radical_strokes(rs[r[2][0]]), ord(r[2][0])))
    rows += more
    head = (Path(folder) / 'Unihan_Readings.txt').read_text(encoding='utf-8').splitlines()[:6]
    version = next(line[2:] for line in head if line.startswith('# Unicode Version'))
    print(f'# Chinese characters by frequency, from the Unicode Han Database (Unihan), {version}.')
    print('# Made by order.py: kHanyuPinlu counts, kTraditionalVariant and kIRG_TSource T1 forms, kTGH level 1;')
    print('# then, with count 0, the rest of level 1 and of moe_4808.tsv, by kRSUnicode.')
    print('# Unihan: Copyright © 1991-2026 Unicode, Inc. Unicode License v3, https://www.unicode.org/license.txt')
    print('# rank\tcount\tsimplified\ttraditional\ttgh-level-1')
    def index(ch):
        m = re.search(r'2013:(\d+)', tgh.get(ch, ''))
        return m.group(1) if m and int(m.group(1)) <= 3500 else None

    for rank, (ch, n, forms) in enumerate(rows, 1):
        # The Simplified form's level-1 index, then any Traditional form's
        # that is in level 1 itself (干 乾干幹: 23 乾:2215).
        level1 = [index(ch)] if index(ch) else []
        level1 += [f'{t}:{index(t)}' for t in forms if t != ch and index(t)]
        print(f'{rank}\t{n}\t{ch}\t{"".join(forms)}\t{" ".join(level1) or "-"}')


if __name__ == '__main__':
    main(sys.argv[1])
