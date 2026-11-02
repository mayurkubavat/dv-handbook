#!/usr/bin/env bash
# ======================================================================
#  scripts/check-structure.sh -- every chapter keeps the template
# ======================================================================
#  The house rules in AGENTS.md fix a chapter's shape so that a reader
#  looking something up knows where to find it. This checks the parts
#  of that shape a script can see:
#
#    1. the title carries a {#sec-...} label
#    2. the first line after the title is a one-line epigraph ("> ...")
#    3. a "Learning objectives" callout follows
#    4. the closer is Summary, Exercises, Further reading, in that order
#    5. no chapter, section, table, figure or listing is referred to by
#       a hard-coded number anywhere in the book; use @sec-/@tbl-/@fig-
#
#  Usage: scripts/check-structure.sh
# ======================================================================
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
fail=0
report() { echo "  $1: $2"; fail=1; }

for f in chapters/*.qmd; do
  head -1 "$f" | grep -qE '^# .+\{#sec-[A-Za-z0-9-]+\}' \
    || report "$f" "title has no {#sec-...} label"
  first=$(sed -n '2,$p' "$f" | grep -m1 -v '^[[:space:]]*$')
  [[ "$first" == "> "* ]] \
    || report "$f" "first line after the title is not a '> ' epigraph"
  grep -q 'title="Learning objectives"' "$f" \
    || report "$f" "no Learning objectives callout"
  order=$(grep -nE '^## (Summary|Exercises|Further reading)\b' "$f" \
          | sed -E 's/^[0-9]+:## //; s/ *\{.*//' | tr '\n' '|')
  [[ "$order" == "Summary|Exercises|Further reading|" ]] \
    || report "$f" "closer is '${order%|}', expected Summary|Exercises|Further reading"
done

# A number in prose goes stale the day a chapter is added or moved.
if hits=$(grep -nE '\b(Chapter|Section|Table|Figure|Listing)s? [0-9]+(\.[0-9]+)*\b' \
          chapters/*.qmd appendices/*.qmd index.qmd 2>/dev/null); then
  echo "hard-coded cross-references (use a label instead):"
  echo "$hits" | cut -c1-160 | sed 's/^/  /'
  fail=1
fi

if [[ $fail -eq 0 ]]; then
  echo "structure: every chapter keeps the template"
fi
exit $fail
