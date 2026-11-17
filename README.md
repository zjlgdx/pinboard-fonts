# Pinboard fonts

Three fonts drawn for [Pinboard](https://github.com/zjlgdx/claude-theme-pinboard), a cork-board theme for Claude: **Ballpoint**, **Marker** and **Typewriter**. All three come from one set of letter skeletons (`skeleton.py`), each written with a different pen.

![Pinboard Ballpoint, Marker and Typewriter: spacing strings, kerning pairs, accented letters, symbols, Bold, and the Typewriter as a terminal](docs/specimen.png)

- **Ballpoint**: a fine round pen leaning about 9°. Three drawings of every lowercase letter take turns, so the words read as written, not set.
- **Marker**: a chisel nib held at 35°, thick on the downstrokes and thin across. Upright, with the same alternates.
- **Typewriter**: the same letters with slab serifs, one width for every glyph, struck through an inked ribbon. The zero has a dot.

For terminals there is a fourth font, **Pinboard Typewriter NF CN**: the Typewriter with Chinese from [LXGW WenKai TC](https://github.com/lxgw/LxgwWenkaiTC) and the icons of [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts) merged in, so a terminal never has to fall back to another font. See [below](#pinboard-typewriter-nf-cn).

Each family comes in **Regular** and **Bold**, style-linked, so an app's Bold button picks the real Bold instead of thickening the Regular.

## Character set

All three fonts cover:

- ASCII, Latin-1 and Windows-1252: every accented letter of Western European languages (`À`–`ÿ`, `Š š Ž ž Ÿ Œ œ`), `Æ Ð Ø Þ ß æ ð ø þ ı`, and the punctuation and signs `¡ ¿ « » ‹ › ‚ „ † ‡ ‰ § ¶ © ® ™ ª º ¹ ² ³ ¼ ½ ¾ ¦ ¤ ƒ`, plus `… ° • ·`, curly quotes, dashes and a no-break space
- Latin Extended-A, the whole block (U+0100–017F), for Central European, Baltic, Turkish, Maltese, Welsh and Esperanto: `Ą Ć Č Ď Ę Ě Ğ Ģ Ħ İ Ķ Ł Ľ Ń Ő Ř Ś Ş Ţ Ů Ű Ź Ż Ŋ Ĳ` and their lowercase, plus Romanian `Ș ș Ț ț` and dotless `ȷ`
- combining marks (U+0300–0328 as Latin uses them: grave, acute, circumflex, tilde, macron, breve, dot, diaeresis, ring, double acute, caron, turned comma, comma below, cedilla, ogonek), placed on any letter by anchors and stacked on each other, with `◌` to show one alone; and the spacing accents `´ ¨ ¯ ¸ ˆ ˜ ˇ ˘ ˙ ˚ ˛ ˝`
- currency: `$ ¢ £ ¥ €`
- math: `+ − × ÷ ± = ≠ ≈ < > ≤ ≥ ¬`, all on one width
- arrows and marks: `← → ↑ ↓ ↔ ↕ ✓ ✗ ● ○`

The Typewriter adds what a terminal draws:

- box drawing, the whole block (U+2500–257F): light, heavy and double lines, rounded corners `╭ ╮ ╰ ╯`, dashes and diagonals
- block elements, the whole block (U+2580–259F): halves, eighths, quadrants and shades `░ ▒ ▓`
- the marks Claude Code prints: `❯ ⏺ ⎿ ✻ ✽ ✶ ✳ ✢ ✓ ✔ ✗ ✘ ⏵ ⏸ ☐ ☒ ☑`, and `■ □ ◼ ◻ ▪ ▫ ◆ ◇ ▶ ◀ ▲ ▼ ▸ ◯ ◉ ⚠ ↵ ⏎ ⌘ ⌥ ⌃ ⇧`

Box drawing and blocks fill the whole cell, 600 units wide and the full 1.24 em line high, so lines join across columns and rows when the terminal's line height is 1.0 (the font's own line). There is no Greek, Cyrillic or CJK (Pinboard Typewriter NF CN adds them), and no Latin beyond Extended-A as precomposed letters (Vietnamese, for one, is built from combining marks); text the fonts lack falls back to another font.

## Use the fonts

The fonts are in `out/`: `.otf` for installing, `.woff2` for the web. On a Mac, double-click an `.otf` and choose Install Font. Install both weights of a family.

```css
@font-face { font-family: 'Pinboard Ballpoint'; src: url(PinboardBallpoint-Regular.woff2) format('woff2'); font-weight: 400; }
@font-face { font-family: 'Pinboard Ballpoint'; src: url(PinboardBallpoint-Bold.woff2) format('woff2'); font-weight: 700; }
```

## Pinboard Typewriter NF CN

One font for a terminal, in Regular and Bold, about 12 MB each (Maple Mono NF CN, for comparison, is 20 MB):

- **Pinboard Typewriter**, every glyph, hint and feature of it.
- **Chinese and more from LXGW WenKai Mono TC**: 22,494 characters that take two cells (CJK ideographs with Extension A and B, Traditional forms, Bopomofo, kana, CJK and full-width punctuation) and 2,373 that take one (Greek, Cyrillic, more Latin, symbols), plus WenKai's ideographic variation sequences. The Bold takes WenKai's Medium, as WenKai has no Bold.
- **10,615 Nerd Fonts icons** (Nerd Fonts 3.5.1): Powerline, Font Awesome, Material Design, Codicons, Devicons, Octicons, Seti and the rest, for prompts like Starship, Powerlevel10k and oh-my-posh.

At about 12 MB a weight it isn't kept in the repository: download it from the [Releases](https://github.com/zjlgdx/pinboard-fonts/releases) page, or build it (below). Install both weights, then pick **Pinboard Typewriter NF CN** as the terminal's font. In iTerm2, turn off *Use a different font for non-ASCII text*, since this font has the non-ASCII text itself; keep the line height at 100%, so box drawing and Powerline segments join.

## Build them

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
brew install potrace
.venv/bin/python build.py      # out/*.otf and out/*.woff2, Regular and Bold
.venv/bin/python audit.py      # overshoot, stems, spacing, contours, metrics
.venv/bin/python sheet.py      # out/sheet.png: spacing, kerning, alternates and the character set, shaped by Chrome
.venv/bin/python sheet.py docs/specimen.png
sh fetch-sources.sh            # WenKai TC 1.530 and Nerd Fonts 3.5.1, checked by SHA-256, into sources/
.venv/bin/python terminal.py   # out/PinboardTypewriterNFCN-{Regular,Bold}.otf, from the Typewriter in out/
```

Two scripts serve the Pinboard theme. Each reads the words to draw as JSON on stdin:

- `outline.py` writes those letters as compact SVG outlines, with the fonts' advances and kerning. Claude's desktop app won't load a font inside a backdrop SVG, so Pinboard draws its labels from these paths.
- `subset.py` cuts the fonts down to those letters, as WOFF2 data URIs, for a surface that does load embedded fonts.

## How a glyph is made

1. `skeleton.py` holds each letter's centre line as an SVG path on a 1000-unit canvas, with y pointing down. An accented letter is its base letter's skeleton plus a mark; a few letters (`Ø Ð Đ Ħ Ł Ŧ Ŀ` and their lowercase, `¢`) are a base letter plus a stroke. The same placement gives the combining marks their anchors.
2. `build.py` draws that line with a pen on a large bitmap: a round pen, a chisel nib, or a round pen plus slab serifs and ribbon ink. A closed path ending in `F` is filled as well as drawn (`● ■ ▶`).
3. potrace traces the bitmap back into curves, which become a CFF outline. The whole font is then lifted by its pen's reach below the skeleton's baseline, so flat letters stand on it.
4. The glyph is spaced from its own profile, kerned against every other glyph, and written out. In the `.otf`, shared runs of outline become CFF subroutines (`cffsubr`); the `.woff2` leaves them out, since Brotli compresses plain outlines smaller.
5. The Bold draws the same skeletons with a wider pen, and goes through steps 3 and 4 again.
6. `cells.py` builds the Typewriter's box drawing and block elements as exact rectangles and quarter circles, with no pen and no ribbon.

## Type-design rules it follows

| Rule | How | Source |
| --- | --- | --- |
| Round shapes overshoot the lines they meet, by 1–3% | Curved parts of a skeleton are pushed 12 units past the baseline, x-height, cap height, ascender and descender. Jitter is kept smaller than that. | [Microsoft: lowercase](https://learn.microsoft.com/en-us/typography/develop/character-design-standards/lowercase), [uppercase](https://learn.microsoft.com/en-us/typography/develop/character-design-standards/uppercase) |
| Flat strokes stand on the baseline | A skeleton's lines are where the pen's centre runs, so the ink of a flat stroke reaches half a stroke past them: below the baseline, above the x-height and cap height. Each font is lifted by how far its own pen reaches below (the median foot of `x z H E I L T n m h u`), so flat feet stand on 0 within the hand's jitter, round ones overshoot below it, and every height is measured from the ink. Spacing, kerning and mark positions are unchanged by the lift. | [Microsoft: lowercase](https://learn.microsoft.com/en-us/typography/develop/character-design-standards/lowercase), [OpenType: OS/2 sxHeight](https://learn.microsoft.com/en-us/typography/opentype/spec/os2#sxheight) |
| Horizontals slightly lighter than verticals | The round pens are 7% flatter than round. The chisel nib does this by its angle. | [Typographica: optics in type design](https://typographica.org/on-typography/is-what-i-see-what-i-get-math-and-optics-in-type-design) |
| Space from shape: straight sides get the most, round sides less, open and diagonal sides least | Each side's average white over the x-height (or cap height) zone, at most 15% of the x-height deep, comes off a per-style target. A straight n side is about a third of n's counter, and o comes out at about 0.8 of n. A slanted letter is measured with its lean taken out. | [Glyphs: spacing](https://glyphsapp.com/learn/spacing) |
| Kern after spacing, only where two shapes leave a hole | Closest approach on the rows both letters share, against their spacing sidebearings, half the excess closed. Lowercase pairs capped at −40. | [Glyphs: spacing](https://glyphsapp.com/learn/spacing) |
| Kerning never makes shapes touch | Over every row both glyphs ink, tails and accents included, a kerned pair keeps at least 12 units of white. A pair that would collide unkerned (`qj`, `jj`) is spaced apart instead. | |
| Accented letters reuse their base letter | `é` is `e`'s own drawing plus an acute: same width, same sidebearings, and `e`'s kerning class. Where the accent alone would collide (`T` over `ï`), a glyph pair overrides the class. `i` and `j` take the dotless form under a mark. | [Glyphs: diacritics](https://glyphsapp.com/learn/diacritics) |
| Marks sit clear of the letter, and scale with the pen | A mark's foot sits a fixed gap above the overshoot, measured from where the pen's ink ends, so a heavier pen lifts it. Capital marks are flatter, so they fit under the line's ascender. Rings and cedillas grow with the pen so their eye and curl stay open. | [Microsoft: diacritics](https://learn.microsoft.com/en-us/typography/develop/character-design-standards/diacritics) |
| Each language's own form of a mark | Latvian `Ģ Ķ Ļ Ņ Ŗ` and Romanian `Ș Ț` take a comma below, Latvian `ģ` a turned comma above; Turkish `Ş Ţ` keep the cedilla. Czech and Slovak `ď ľ ť Ľ` take an apostrophe beside the stem, and the letter widens by what it adds. An ogonek grows from the stem or curve it hangs on, and `į` keeps its dot. | [Diacritics project](https://diacritics.typo.cz/) |
| Combining marks attach by anchors | Every letter has `top`, `bottom`, `cedilla` and `ogonek` anchors where the same code puts its precomposed marks, carried through the hand's own lean and jitter, so `x́` sits as `á` does. Marks have no width and are GDEF marks. `ccmp` drops the dot of `i` and `j` under a mark above and swaps in a flatter `.case` mark over a capital; `mkmk` stacks marks; `calt` and `kern` look through them. | [OpenType: GPOS mark-to-base](https://learn.microsoft.com/en-us/typography/opentype/spec/gpos#lookup-type-4-mark-to-base-attachment-positioning-subtable), [Glyphs: diacritics](https://glyphsapp.com/learn/diacritics) |
| Legacy (spacing) accents are not marks | `´ ¨ ¯ ¸ ˆ ˜ ˇ ˘ ˙ ˚ ˛ ˝` have width and no anchors. | Fontbakery `legacy_accents` |
| A Bold is a weight of the same design | Same skeletons, a wider pen: stems 1.4 to 1.6 times the Regular's (Ballpoint 48 → 77, Marker 88 → 123, Typewriter 62 → 96 units). The handwriting widens 8% so counters stay open, and the Typewriter's serifs give back a little so `m`'s feet stay apart. Spaced and kerned from its own outlines. | |
| Style-linked weights | Regular: `usWeightClass` 400, fsSelection REGULAR. Bold: 700, fsSelection BOLD, `head.macStyle` bold. Both share the family name, with the weight as subfamily (RIBBI), and share vertical metrics and underline, so lines don't jump between weights. | [OpenType: OS/2](https://learn.microsoft.com/en-us/typography/opentype/spec/os2), [Google Fonts: naming](https://googlefonts.github.io/gf-guide/statics.html) |
| Math signs share one width | `+ = < > × ~` are centred in one width. | Fontbakery `math_signs_width` |
| Monospace: one advance for every glyph, narrow letters widened, wide ones squeezed | Typewriter: 600 everywhere, `.notdef` and box drawing included; combining marks are zero width, as a terminal expects, and hang over the cell before them. Symbols keep their proportions and only shrink to fit. `post.isFixedPitch` is set and PANOSE proportion is 9. | [Google Fonts requirements](https://googlefonts.github.io/gf-guide/requirements.html) |
| Box drawing joins | Lines are centred on the cell and run to its edges: 0 and 600 across, the typo descender and ascender up and down. Light lines are as heavy as a stem, heavy lines 1.9 times that. Double lines turn corners on their inner and outer lines. | [Unicode: box drawing](https://www.unicode.org/charts/PDF/U2500.pdf) |
| Symbols read at terminal sizes | In the Typewriter, arrows run nearly the cell's width (`← →`) or the cap height (`↑ ↓`), with heads at 45°; `© ®` are ovals as tall as a capital, since a circle that fits the cell is far shorter; `™` hangs from the cap height and fills the cell; `✗` covers what `✓` covers. Arrows, `✓` and `✗` take a pen 1.2 times as heavy, so `✗` doesn't read as `x`. | |
| Each character takes the cells a terminal gives it | NF CN: Wide and Fullwidth characters (Unicode East Asian Width W and F) advance two cells, 1200 units; everything else one, 600; combining marks none. A glyph drawn wider than its one cell (`※` and other East Asian Ambiguous signs) shrinks about its centre to fit. `xAvgCharWidth` is one cell and `isFixedPitch` is set, as terminals size their cell by them. | [Unicode UAX #11](https://www.unicode.org/reports/tr11/) |
| Chinese sized and centred against the Latin | WenKai's em becomes ours unscaled, centred in the two cells, and moved so the middle of its ideographs' ink sits on the middle of the capitals; scales 0.88 to 1.0 were proofed, and smaller left too much white between characters. Both weights use the Regular's placement, so Chinese doesn't jump when the weight changes. A `BASE` table gives the ideographic baseline and character face (`ideo`, `icfb`, `icft`) for apps that align scripts by them; the `meta` table names the languages. | [OpenType: BASE](https://learn.microsoft.com/en-us/typography/opentype/spec/base), [meta](https://learn.microsoft.com/en-us/typography/opentype/spec/meta) |
| Every letter in both weights, with its capital | NF CN: WenKai draws `ƛ` and `ɤ` but not their capitals, which came in Unicode 16, so they're drawn from WenKai's own strokes. `Ƛ` is a stem crossed by a bar, standing on Λ's legs, as the character was encoded; `Ɤ` is the ram's horn grown to cap height with its loop on the baseline, unlike `Ɣ`, whose loop hangs below. Overlapping strokes are merged into one outline. The Bold's fullwidth `ｌ`, which WenKai's Medium lacks, is the Regular's grown by the 6 units each side that the Medium adds. | [Unicode: Latin Extended-D](https://www.unicode.org/charts/PDF/UA720.pdf), Fontbakery `case_mapping` |
| Icons placed as Nerd Fonts' patcher places them | From Symbols Nerd Font, the variant Nerd Fonts patches into a monospaced font: the source's em becomes ours, each icon starts at its cell's left and may run on over the next one, as prompts leave a space after it; centred on the line. Powerline separators span the line from descender to ascender and their own one or two cells, keeping the source's small overlap so no hairline shows between segments. | [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts/wiki) |
| Light without leaving anything out | CFF outlines with subroutines, which store CJK smaller than TrueType. Quadratic curves merge into fewer cubics (`qu2cu`, within one unit), contours turn to PostScript's direction, coordinates are whole units. WenKai's proportional-width (`halt`, `vhal`) and vertical-writing features are left out: a monospaced font must not change widths, and terminals don't write vertically. | [Adobe: CFF](https://adobe-type-tools.github.io/font-tech-notes/pdfs/5176.CFF.pdf) |
| Tell 0 from O, and 1 from l from I, in a monospace | Typewriter zero has a dot. 1 has a flag and foot, l a tail, I two slabs. | |
| Outer contours counter-clockwise, no overlaps, points at extremes | potrace gives non-overlapping, correctly wound contours, and box-drawing pieces are merged into one outline. `ExtremaPen` splits every curve at its extremes. No contour is under 400 units²: a counter the Bold pen all but closes is filled. | [Adobe Type 1 spec §3.5, §4.1](https://adobe-type-tools.github.io/font-tech-notes/pdfs/T1_SPEC.pdf), [Glyphs: drawing good paths](https://glyphsapp.com/learn/drawing-good-paths) |
| Vertical metrics | `USE_TYPO_METRICS` is on, hhea equals typo, line gap 0. The line is 1.24 em with the caps centred in it, the same in both weights. The typo ascender clears `À`. The win metrics are the family's bounds. | [Google Fonts: vertical metrics](https://googlefonts.github.io/gf-guide/metrics.html), [OpenType: OS/2](https://learn.microsoft.com/en-us/typography/opentype/spec/os2) |
| x-height and cap height | Measured from the flat tops of x (z for Ballpoint) and H, whose feet stand on the baseline, so each is the ink's full height. | [OpenType: OS/2](https://learn.microsoft.com/en-us/typography/opentype/spec/os2) |
| Names and versions | Windows names only, IDs 1–6 plus 13/14 for the OFL. head.fontRevision matches nameID 5. post is 3.0, as CFF fonts use. | [OpenType: name](https://learn.microsoft.com/en-us/typography/opentype/spec/name), [recommendations](https://learn.microsoft.com/en-us/typography/opentype/spec/recom) |
| Slanted handwriting | Ballpoint leans 9° as part of the hand, as other script fonts do. It stays a Regular with italicAngle 0, so it needs no upright partner. | Fontbakery `italic_angle` |

The handwriting fonts carry two alternates of every lowercase letter, accented ones included, cycled by `calt`. In "bookkeeper" the two o's, the two k's and the e's are each drawn differently.

## Checks

`fontbakery check-universal` passes all 76 checks on each Ballpoint and Marker font with no warnings, and all 142 when a family's Regular and Bold are checked together. Fontbakery's `soft_dotted` check (from the Google Fonts profile) passes too: `i`, `j` and `į` lose their dot under any mark above. On each Typewriter font one check errors: fontbakery 1.1's monospace check reads a `glyf` table, which a CFF font doesn't have. `audit.py` and the build cover what that check would test: one advance, `isFixedPitch`, PANOSE proportion 9, and `xAvgCharWidth`.

Pinboard Typewriter NF CN passes the OpenType Sanitizer that browsers use, and 136 of fontbakery's universal checks for its two weights. What it flags is deliberate or out of its hands:

- `monospace` errors, as for the Typewriter.
- `xavgcharwidth`: `xAvgCharWidth` is one cell, not the average of all glyphs (which Chinese pushes toward two), because terminals size their cell by it.
- `cjk_chws_feature`: `chws` and `vchw` close up the space around CJK punctuation, which would break the grid.
- `math_signs_width`: `〒` is a Wide character and takes two cells.
- `file_size`: a font with 22,000 Chinese characters is large; it is still well under half of WenKai's and Nerd Fonts' TrueType files together.

The fonts are hinted with AFDKO's `otfautohint`, from alignment zones and standard stems the build measures from the drawn glyphs (the baseline, x-height, cap height with ascenders, and descender zones; `StdVW`/`StdHW` from `l n H I h` and `H E z Z`). Windows and FreeType use the hints to snap those edges and stems to whole pixels at small sizes; macOS ignores them. Box drawing and block elements are left unhinted, so their edges stay on the cell's and rows keep joining. `subset.py` drops the hints, since the board's SVG has no use for them.

## Licence

The fonts are under the [SIL Open Font License 1.1](OFL.txt). The build scripts are under the [MIT License](LICENSE).

Pinboard Typewriter NF CN is a Modified Version, under the OFL, of LXGW WenKai TC (Copyright 2022–2026 The LXGW WenKai Project Authors, OFL 1.1, no Reserved Font Name). Its icons come from Nerd Fonts (MIT), each set under its own licence (MIT, OFL, Apache 2.0, CC BY 4.0), all of which allow them in a font; see Nerd Fonts' [license audit](https://github.com/ryanoasis/nerd-fonts/blob/master/license-audit.md).
