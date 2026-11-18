#!/bin/bash
# tools/stack.sh WORKTREES BASE BATCHDIR [--build] < SPEC
#
# Several rounds at once: one branch per issue, each in its own worktree under
# WORKTREES, each one commit on top of the one before (BASE first). SPEC lines:
#
#     ISSUE FIRST LAST VERSION PREFIX      e.g.  31 1201 1400 0.530 r1400
#
# PREFIX picks the round's batches, BATCHDIR/PREFIX_*.py, merged in name order.
# With --build, every worktree then builds at once (about two hours for seven
# on 18 cores); each log goes to WORKTREES/build-LAST.log and the exit codes to
# WORKTREES/builds-done.txt. Merge the pull requests in order: once one is in
# main, the next one shows only its own commit.
set -euo pipefail
WT=$1 BASE=$2 BATCH=$3 BUILD=${4:-}
REPO=$(cd "$(dirname "$0")/.." && pwd)
PY=${PY:-$REPO/.venv/bin/python}
mkdir -p "$WT"
# Absolute, as git -C and each build's cd would read a relative one elsewhere.
WT=$(cd "$WT" && pwd)
prev=$BASE
built=()
while read -r issue first last version prefix; do
  [ -z "${issue:-}" ] && continue
  br="hanzi-$last"
  git -C "$REPO" worktree add -q "$WT/$br" -b "$br" "$prev"
  "$PY" "$WT/$br/tools/merge_round.py" "$last" "$version" $(ls "$BATCH/${prefix}"_*.py | sort)
  n=$(cd "$WT/$br" && "$PY" -c "import hanzi_strokes as h; print(sum('\u3400' <= c <= '\u9fff' for c in h.C))")
  git -C "$WT/$br" add -A
  (cd "$WT/$br" && gitleaks git --staged --no-banner)
  # COMMIT_TRAILER, if set, ends each message (a Co-Authored-By line, say).
  printf 'Chinese: rows %s-%s of hanzi_order.tsv (%s hanzi), %s\n\nDraws the characters of rows %s-%s, Simplified and Traditional, in all\nthree families.\n\nCloses #%s.\n%s' \
    "$first" "$last" "$n" "$version" "$first" "$last" "$issue" "${COMMIT_TRAILER:+$'\n'$COMMIT_TRAILER$'\n'}" | git -C "$WT/$br" commit -q -F -
  prev=$br
  built+=("$last")
done
git -C "$REPO" worktree list
if [ "$BUILD" = --build ]; then
  : > "$WT/builds-done.txt"
  for last in "${built[@]}"; do
    (cd "$WT/hanzi-$last" && "$PY" build.py > "$WT/build-$last.log" 2>&1; echo "hanzi-$last exit $?" >> "$WT/builds-done.txt") &
  done
  wait
  cat "$WT/builds-done.txt"
  grep -l "cut off" "$WT"/build-*.log || echo "no glyph cut off"
fi
