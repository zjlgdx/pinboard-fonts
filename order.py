"""The order Chinese is drawn in: most frequent first, Traditional and
Simplified together.

    python order.py <folder with Unihan's .txt files>  >  hanzi_order.tsv

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
'-'. A round draws the next rows in order, every form in them.
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


def main(folder):
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
    head = (Path(folder) / 'Unihan_Readings.txt').read_text(encoding='utf-8').splitlines()[:6]
    version = next(line[2:] for line in head if line.startswith('# Unicode Version'))
    print(f'# Chinese characters by frequency, from the Unicode Han Database (Unihan), {version}.')
    print('# Made by order.py: kHanyuPinlu counts, kTraditionalVariant and kIRG_TSource T1 forms, kTGH level 1.')
    print('# Unihan: Copyright © 1991-2026 Unicode, Inc. Unicode License v3, https://www.unicode.org/license.txt')
    print('# rank\tcount\tsimplified\ttraditional\ttgh-level-1')
    for rank, (ch, n, forms) in enumerate(rows, 1):
        level1 = '-'
        m = re.search(r'2013:(\d+)', tgh.get(ch, ''))
        if m and int(m.group(1)) <= 3500:
            level1 = m.group(1)
        print(f'{rank}\t{n}\t{ch}\t{"".join(forms)}\t{level1}')


if __name__ == '__main__':
    main(sys.argv[1])
