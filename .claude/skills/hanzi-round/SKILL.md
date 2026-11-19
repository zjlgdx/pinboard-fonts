---
name: hanzi-round
description: Draw the next rows of hanzi_order.tsv into the 一粟 (Yisu) fonts and ship them as a release — draft batches, edge check, merge, build, checks, proof, pull request, release. Use for a Chinese round or a milestone of them ("do the next 200 rows", "繼續處理下一批", an issue titled "Chinese rows A–B"). Not for Latin, symbols or the build's pens.
---

# A Chinese round

A round draws every form in a range of rows of `hanzi_order.tsv` (Simplified
and Traditional together) and ships it as one release. AGENTS.md's rules hold
throughout: everything original, the design board first, gitleaks before each
commit, no personal data in anything published, never force-push main, and the
maintainer decides merges.

The tools are in `tools/`; run them with `.venv/bin/python` from the checkout.
Drafts go in `work/` (ignored by git), never in a temp folder that a reboot
clears. `work/unihan/` keeps the Unihan files `order.py` reads.

## 1. Draft

1. `tools/hz_todo.py FIRST LAST` lists what the rows still need.
2. Write batches `work/rLAST_1.py`, `_2.py`, … (about 70 characters each). The
   first starts with `# ---- rows FIRST-LAST of hanzi_order.tsv`. Write them
   in hanzi_strokes.py's own terms: `C['字'] = lr(L['亻'], K['...'])`,
   `box((part, (x0, y0, x1, y1)), ...)`, `S('E M.. L..')`.
3. Reuse before drawing: `tools/hz_have.py CHARS work/rN_1.py,...` says what
   exists. `tools/hz_fixrefs.py work/rN_2.py work/rN_1.py` fixes K/C mix-ups
   and lists unknown parts.
4. Look at them: `tools/hz_sheet.py work/sheet.jpg --batch work/rN_1.py` (all
   three pens, and the Ballpoint large). Fix what looks wrong and look again.
5. Draw each in its own standard's form: 教育部 standard forms for
   Traditional, 通用规范汉字表 for Simplified.
6. Before drawing one, check its parts and stroke count against Unihan
   (`kTotalStrokes` in `Unihan_IRGSources.txt`, `kRSUnicode`). Where the
   教育部 字樣說明 gives another count for a Traditional form, follow it. Give a
   Traditional character Taiwan's form of every part, a Simplified one the
   mainland's: 䍃 is `K['䍃TW']` (𠂊 and a dot) in 搖 謠 瑤, `K['䍃']` (爫) in
   谣 瑶; 糸, 言, 貝 against 纟, 讠, 贝.

### What goes wrong, and the fix

- **`box()` maps a part's whole 1000 grid into the rect, not its ink.** Parts
  drawn in place on the grid need the full frame or a stretched rect, or they
  come out tiny and flat: 爫 (y 30–290), 尚, 雨, 罒 (60–300), 冖 (80–220),
  宀, 穴, 广, 门, 門, ⺈, ⺮, 灬, 亍, 乚 (x 760), 乞 (x 560–940).
  Some are partial: K['甘'] is the top half, K['弗'] the top half, K['幺']
  y 40–570. To scale one up, give a rect bigger than the frame:
  甘 `(0, -60, 1000, 2000)`, 弗 `(0, 0, 1000, 1700)`, 幺 `(0, 0, 1000, 1700)`,
  乞 `(-375, 0, 1046, 1000)`.
- **Nothing starts on the top edge.** A stroke at y < 30, or a part whose rect
  starts at y 0 with ink at its own top, is cut off by the Typewriter and
  the Marker (懼's 瞿 did this). Start at 30, or the rect at 40–50.
- **Stacked parts crowd.** 疊, 寧, 憋 needed their top parts smaller and the
  lower ones given more of the height.
- **A part boxed twice shrinks.** `K['髟']` drew its 镸 on the left of the
  grid and then boxed it into the left half again, so 鬆 髭 鬢 got a 镸 a
  quarter wide. Before boxing a part into part of the frame, look where its
  ink already sits.
- **A shared part's mistake spreads.** 豕 lacked its short right 丿, 罙 took
  穴's dot, 龠 lacked the 一 under 人, 奥 closed its 冂 and lost 米's lower
  strokes: each was found when a new character used the part and its count
  came out wrong. Count the part itself and fix it where it is defined: a
  `work/rLAST_fix.py` whose definitions replace the old ones in place at
  merge, and a before/after sheet of every character that uses the part.
- **Look-alike parts are different characters.** 夐 ends in 夂 (14 strokes,
  觼); 敻 ends in 攵 (15, 瓊). Check the code point, not the look.
- **A shell pipe can mangle the characters.** `grep | cut -c` on macOS cuts
  bytes, not characters; pull a batch's characters out with Python.
  `edges.py` fails when none of `--chars` is drawn, so a mangled list can't
  pass as clean.

## 2. Check the edges, then merge

```
.venv/bin/python tools/edges.py --batch work/rN_1.py,work/rN_2.py,...
```

It draws every character in all six fonts on the build's own canvas
(`build.canvas`) and lists any whose ink reaches the edge; fix them first.
The pens' jitter depends on the canvas, and the Typewriter's is a cell wider,
so a check on any other canvas misses cuts.

Then in a branch `hanzi-LAST` from main:

```
.venv/bin/python tools/merge_round.py LAST NEW_VERSION work/rN_*.py
```

It adds the batches before the mainland block of hanzi_strokes.py, sets
`VERSION` (0.010 a round), and updates the README's counts. Coverage is whole
percents but one decimal past 99.5, so it never shows 100%.

## 3. Build and check

```
.venv/bin/python build.py              # about an hour; must print no "cut off"
.venv/bin/python audit.py
.venv/bin/python tools/check_fonts.py  # versions, OTS, fontbakery, personal data
```

`check_fonts.py` fails on a stale font, an OTS failure, a fontbakery FAIL, or
anything that looks personal (add your own name with `--private` or
`YISU_PRIVATE`). The known results, explained in the README, are printed
but pass: file size (the WARN past 1 MB, and `massive-font`'s FAIL past 9 MB,
marked `(known)`), and in the Typewriter fontbakery's CFF `glyf` error and the
double-width `xAvgCharWidth`. A new FAIL code is fixed, or explained in the
README and added to `KNOWN_FAIL` in `check_fonts.py`, once the maintainer agrees.

## 4. Proof and design board

`tools/round_proof.py FIRST LAST work/proofN.jpg` sets a line of Taiwan's
text and one of the mainland's in every font, then the round's characters.
Look at it. It goes on the design board (the Pinboard theme project) before
the pull request.

## 5. Pull request and release

```
tools/open_pr.sh ISSUE FIRST LAST ["one line on anything fixed"]
```

It runs gitleaks on the branch, pushes it, and opens the PR. Merge only when
the maintainer says so (with a merge commit). Then, from the checkout that
built the fonts:

```
tools/release.sh FIRST LAST ["the same fix line"]
```

It refuses unless main has this VERSION and every font in out/ says it, then
makes the tag `vVERSION` with the fonts and their SHA-256.

## Many rounds at once

`tools/stack.sh WORKTREES main work --build < spec`. Each line of the spec is
`ISSUE FIRST LAST VERSION PREFIX`. It makes one worktree per round, each
branch one commit on the one before, and builds them all at once (seven take
about two hours on 18 cores). Set `COMMIT_TRAILER` for a Co-Authored-By line.
Check, proof and ship them in order.

- Before stacking rounds drafted side by side, run `tools/hz_dupes.py` on all
  their batches in row order and keep one definition of each part (the
  earliest, as a rule). Then check that the one kept means the same thing to
  every user: one round's `K['贰']` had its 贝 and another's didn't, so the
  second's 贰 would have drawn 贝 twice. Redraw everything that uses a part
  you removed.
- Once a PR merges, merge `origin/main` into the next branch (a merge commit;
  never rebase a branch others stack on), then run `check_fonts.py` there.
- Drafting the next round while one builds: load the earlier round's batches
  and fix file first, in every tool's batch list
  (`r5184_1.py,…,r5184_fix.py,r5364_1.py`), so the new batches use its parts.
- Other work can ship while a stack builds. Before opening a PR, look at
  main's `VERSION` and the latest tag: 0.730 was once taken by another
  branch's release while a round built as 0.730, and the round merged with no
  release of its own. `open_pr.sh` now refuses a version main has reached or
  a tag has; take the next free one. If main gained glyph changes, the fonts
  you built lack them: rebuild after merging.
- A worktree has no `work/`: write its proof into the main checkout's
  (`round_proof.py FIRST LAST /path/to/fontkit/work/proofV.jpg`).
  `release.sh` finds the main checkout's `.venv` and fetches the tags itself.
- A fix that later rounds need (a part redrawn in `hanzi_strokes.py`): commit
  it on its round's branch, then merge that branch into the later ones, and
  rebuild only what changed.

## Past the frequency list

The corpus counts end at row 2,849. Rows 2,850–4,823 (count 0) are the rest
of Taiwan's 常用國字標準字體表 (4,808, `moe_4808.tsv`, from Wikisource and
checked against the MOE's PDF; the README has the source and licence) and of
level 1 of 通用规范汉字表 (3,500, the last column of `hanzi_order.tsv`),
sorted by radical so a round draws whole families. Rows 4,824–5,364 are the
rest of Big5's first level (5,401, Unihan `kBigFive` A440–C67E), sorted the
same way, with the mainland's form where 通用规范汉字表 has it at any level.
Draw their Traditional forms as Taiwan's 次常用國字標準字體表 writes them. A `-`
in a column means that script has nothing to draw on that row.
`merge_round.py` keeps the README's "Drawn so far" line for the three lists. Any new list needs its source
and licence checked and recorded in the README first.

## Past both lists

A text set in the fonts can need a character neither list has (《滕王閣序》's
`鶩`, say). Draw it the same way: a batch in `work/`, the sheet beside
characters of the same structure, `edges.py`, the design proof agreed first.
Check its form against its own standard, looked at, never traced. Merge with
the same ROWS as the last round (`merge_round.py 4823 NEW_VERSION batch.py`):
the rows' counts stay as they are, since they count only the rows' own
characters, and the README's "Past both lists" paragraph names each one and
the text it is for. `round_proof.py` and `open_pr.sh` are for rows; write
this proof and pull request by hand.
