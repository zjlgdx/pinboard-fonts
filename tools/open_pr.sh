#!/bin/bash
# tools/open_pr.sh ISSUE FIRST LAST [FIX]
#
# Run in the round's checkout, after tools/check_fonts.py passes. Pushes the
# branch and opens a pull request on main that closes ISSUE; FIX, if given, is
# one more line for the notes. Prints the pull request's URL. Merging is the
# maintainer's call (AGENTS.md): this script never merges.
set -euo pipefail
ISSUE=$1 FIRST=$2 LAST=$3 FIX=${4:-}
cd "$(dirname "$0")/.."
BR=$(git branch --show-current)
V=$(sed -nE 's/^VERSION = ([0-9.]+).*/\1/p' build.py)
read -r COUNT PCT < <(sed -nE 's/.*The first [0-9,]+ rows are ([0-9,]+) characters across both scripts, and cover ([0-9.]+)% of the corpus.*/\1 \2/p' README.md | tr -d ,)
git fetch -q origin main
BEFORE=$(git show origin/main:README.md | sed -nE 's/.*rows are ([0-9,]+) characters across both scripts.*/\1/p' | tr -d ,)
NEW=$((COUNT - BEFORE))
gitleaks git --no-banner --log-opts="origin/main..HEAD"
git push -q -u origin "$BR"
fixline=""
[ -n "$FIX" ] && fixline=$'\n'"- $FIX"
body="Rows ${FIRST}–${LAST} of \`hanzi_order.tsv\`, in the Typewriter, the Ballpoint and the Marker, Simplified and Traditional together.

- Every character in the first ${LAST} rows is drawn: ${COUNT} hanzi in all (${NEW} new), ${PCT}% of the corpus.${fixline}
- Version ${V}. \`tools/edges.py\` and the build report no glyph cut off.
- Checks (\`tools/check_fonts.py\`): OTS passes on all six fonts, \`fontbakery check-universal\` has no FAIL (the warnings are the known ones: \`file_size\`; the Typewriter's \`xAvgCharWidth\` and CFF \`glyf\` check), and no personal data.

Closes #${ISSUE}

🤖 Generated with [Claude Code](https://claude.com/claude-code)"
gh pr create --base main --head "$BR" --title "Chinese rows ${FIRST}–${LAST} (${V})" --body "$body"
