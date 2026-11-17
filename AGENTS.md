# AGENTS.md

Notes for anyone, human or agent, changing the Pinboard fonts. The [README](README.md) says what the fonts are and how they're built; this file says how to work on them.

## The one rule: everything is original

Every outline in these fonts comes from this repository: the centre lines in `skeleton.py`, written with the pens in `build.py`, or the cell geometry in `cells.py`. Nothing is copied, traced, measured or converted from another font. That covers outlines, stroke data, metrics and kerning.

- **Not allowed, even as a starting point:** another font's glyphs, or data made from them. That includes LXGW WenKai, Klee One, Noto and Source Han, GNU Unifont, Nerd Fonts and the icon sets it collects, and stroke or median datasets drawn from fonts (Make Me a Hanzi, hanzi-writer and Animated CJK all come from Arphic fonts).
- **Allowed:** facts about characters. That means the Unicode Character Database and Unihan (names, East Asian Width, case pairs, radicals and stroke counts), character lists, frequency counts, structure descriptions (which components a character has and how they sit) written here or taken from a source whose licence allows it, and published type-design guidance.
- **Looking is fine; tracing is not.** You may look at a reference glyph, a code chart or a photo to learn what a character is (Ƛ's shape, a stroke's direction or order). Draw it again yourself in the skeleton's own terms. Don't measure a reference font's coordinates.
- **Check the licence of any new data source** before using it, and record the source in the README.

Releases 0.430 and 0.431 shipped a terminal build, Pinboard Typewriter NF CN, which merged LXGW WenKai and Nerd Fonts. It was retired in *Round 1 · Original only*. Chinese and the terminal's icons are now drawn here, a slice at a time.

## Where things are

| File | What it does |
| --- | --- |
| `skeleton.py` | Every glyph's centre line as an SVG path. The canvas is 1000 units with y pointing down: the cap line and figures sit at 50, the x-height at 250, the baseline at 750, the descender at 960 and ascenders at 40. |
| `build.py` | The pens, the bitmap, potrace, spacing, kerning, features, hinting and the OpenType writer. `VERSION` is head.fontRevision and nameID 5. |
| `cells.py` | The Typewriter's box drawing, block elements and Powerline separators, drawn exactly to the 600-unit cell. |
| `hanzi.py`, `hanzi_strokes.py` | Chinese: the stroke kinds, how the pen moves along them, and each family's cut (`CUTS`: pen, pressure, rise, lean, hand); then the characters as strokes and components on a 1000 grid (y down). Add a round's characters to `hanzi_strokes.py`, reusing the components already there; a character drawn once serves all three families. |
| `order.py`, `hanzi_order.tsv` | The order Chinese is drawn in, most frequent first, Traditional and Simplified on one row, made from Unihan (see the README). Run `order.py` on a newer Unihan to refresh it. A round takes the next rows not yet drawn. |
| `audit.py`, `proof.py`, `spacing.py`, `sheet.py` | Checks and proof sheets. `sheet.py docs/specimen.png` makes the README's specimen. |
| `outline.py`, `subset.py` | Letters for the Pinboard theme's board: SVG outlines, or WOFF2 subsets. |
| `out/` | The built fonts, committed. Merged builds over a few MB go to GitHub Releases, not git. |

## How to work

- **Design first.** Any change to how glyphs look starts as a proof image: the new glyphs beside the old ones and the letters they sit with, at text and display sizes, in both weights. Get it agreed before changing the build. The Pinboard theme project keeps the design board.
- **One slice per pull request.** Work is split into GitHub milestones and issues; a PR closes the issues it finishes. Chinese grows by frequency, a few hundred characters per round, Traditional and Simplified together, reusing the strokes and components already drawn. Draw each in the form its own standard writes (Taiwan's 教育部 standard forms for Traditional, mainland China's 通用规范汉字表 for Simplified), and add a mainland form of a shared mark to `ZHS` when it sits differently.
- **Keep the README true.** The character set, the rules table and the check results must match what the build gives.
- **Bump `VERSION`** in `build.py` for each release, then rebuild every font so they all carry it.

## Before a pull request

```
.venv/bin/python build.py
.venv/bin/python audit.py
.venv/bin/python sheet.py docs/specimen.png
.venv/bin/fontbakery check-universal out/PinboardTypewriter-Regular.otf out/PinboardTypewriter-Bold.otf
```

- Run the OpenType Sanitizer over every `.otf` (`python -c "import ots; ots.sanitize(path, '/dev/null')"`); every font must pass.
- fontbakery's results should match what the README says. A new FAIL is fixed, or explained in the README as deliberate.
- Scan for secrets with `gitleaks git --staged` before committing. Published files must contain no personal data: no names, emails or local paths.
- Never force-push or rewrite `main`. The maintainer merges.

## Licence

The fonts are under the SIL Open Font License 1.1 (`OFL.txt`); the code is under MIT (`LICENSE`).
