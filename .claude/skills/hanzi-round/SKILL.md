---
name: hanzi-round
description: Draw the next rows of hanzi_order.tsv into the Pinboard fonts and ship them as a release — draft batches, edge check, merge, build, checks, proof, pull request, release. Use for a Chinese round or a milestone of them ("do the next 200 rows", "繼續處理下一批", an issue titled "Chinese rows A–B"). Not for Latin, symbols or the build's pens.
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
`PINBOARD_PRIVATE`). The known warnings: file size, and in the Typewriter
fontbakery's CFF `glyf` error and the double-width `xAvgCharWidth`.

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
Check, proof and ship them in order. Once a PR merges, the next one shows
only its own commit. If one needs a fix, amend that branch (it isn't pushed
yet) and rebuild only it.

## Past the frequency list

`hanzi_order.tsv` has 2,849 rows. The milestone after it asks for the
characters that have no corpus count: Taiwan's 常用國字標準字體表 (4,808) and
the first level of 通用规范汉字表 (3,500, Unihan `kTGH` 1–3500). Their order
and their sources are a decision for the maintainer. Record any new list's
source and licence in the README before using it.
