#!/usr/bin/env bash
# ======================================================================
#  scripts/check-citations.sh -- every citation must reach the page
# ======================================================================
#  A citation key that resolves is not the same as a citation that prints.
#  Written as `@sec-foo [@key]`, pandoc reads the bracket as a suffix to an
#  in-text citation and silently drops it: the source disappears from the
#  built book, the key still "resolves", and nothing warns. That happened
#  twice in this book and three reviews checked resolution without checking
#  appearance.
#
#  Two checks:
#    1. the swallowing construction, by pattern, in the sources
#    2. every key cited in a source appears in the rendered bibliography
#
#  Usage: scripts/check-citations.sh [rendered.txt]
#  With no argument only check 1 runs, which needs no build.
# ======================================================================
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
fail=0

# 1. A cross-reference immediately followed by a bracketed citation.
if hits=$(grep -rnE '@(sec|fig|tbl)-[A-Za-z0-9-]+ +\[@' chapters/ appendices/ \
          index.qmd 2>/dev/null); then
  echo "citations swallowed by an adjacent cross-reference:"
  echo "$hits" | sed 's/^/  /'
  echo "  fix: put the citation before the cross-reference, or separate them"
  fail=1
fi

# 2. Every cited key reaches the rendered text.
if [[ $# -ge 1 && -f "$1" ]]; then
  keys=$(grep -rhoE '\[@[A-Za-z0-9_.:-]+' chapters/ appendices/ index.qmd \
         2>/dev/null | sed 's/^\[@//' | sort -u)
  missing=""
  for k in $keys; do
    author=$(awk -v k="$k" '
      $0 ~ "^@[a-zA-Z]+\\{"k"," {found=1}
      found && /author|title/ {print; exit}' refs.bib \
      | sed -E 's/.*= *\{+//; s/[},].*//' | head -1)
    [[ -z "$author" ]] && continue
    first=$(echo "$author" | awk '{print $NF}' | tr -d '{}')
    [[ -z "$first" ]] && continue
    grep -qF "$first" "$1" || missing="$missing $k"
  done
  if [[ -n "$missing" ]]; then
    echo "cited but not found in the rendered text:$missing"
    echo "  check each by hand: a name may simply differ in the bibliography"
  fi
fi

[[ $fail -eq 0 ]] && echo "citations: no swallowed references"
exit $fail
