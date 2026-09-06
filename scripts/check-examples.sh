#!/usr/bin/env bash
# ======================================================================
#  scripts/check-examples.sh -- lint and run every example, write a status file
# ======================================================================
#  Usage:
#      scripts/check-examples.sh              check every example directory
#      scripts/check-examples.sh --changed    only directories changed in git
#      scripts/check-examples.sh ch07         only paths containing ch07
#
#  For each directory containing a Makefile under examples/<chapter>/:
#      make lint          always
#      make run           unless the Makefile declares REQUIRES := <something>
#                         that this machine cannot satisfy (commercial
#                         simulator, UVM-SystemC library, ...)
#
#  Results go to examples/status.json, which CI and STATUS.md both read.
#  Exit code is non-zero if any lint or run failed.
# ======================================================================
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STATUS="$ROOT/examples/status.json"
FILTER="${1:-}"

# Pick the Python environment that has cocotb (used by cocotb/pyuvm examples).
RUN=""
if ! command -v cocotb-config >/dev/null 2>&1 \
   && conda env list 2>/dev/null | grep -q '^dvbook '; then
  RUN="conda run -n dvbook --no-capture-output"
fi

if [[ "$FILTER" == "--changed" ]]; then
  DIRS=$( (git -C "$ROOT" diff --name-only HEAD -- examples;
           git -C "$ROOT" diff --cached --name-only -- examples) \
         | xargs -n1 dirname 2>/dev/null | sort -u | sed "s|^|$ROOT/|")
else
  DIRS=$(find "$ROOT/examples" -mindepth 3 -maxdepth 3 -name Makefile \
         -exec dirname {} \; | sort)
  [[ -n "$FILTER" ]] && DIRS=$(echo "$DIRS" | grep -- "$FILTER" || true)
fi

pass=0; fail=0; skip=0; rows=()
for d in $DIRS; do
  [[ -f "$d/Makefile" ]] || continue
  rel="${d#$ROOT/}"
  requires=$(grep -E '^REQUIRES\s*:?=' "$d/Makefile" \
             | sed -E 's/.*=\s*//' | tr -d ' ')
  lint="pass"; run="pass"
  if ! (cd "$d" && $RUN make -s lint >"$d/lint.log" 2>&1); then
    lint="fail"
  elif grep -q '^skipped' "$d/lint.log"; then
    lint="skipped"
  fi
  if [[ -n "$requires" ]]; then
    run="skipped ($requires)"; ((skip++))
  elif ! (cd "$d" && $RUN make -s run >"$d/run.log" 2>&1); then
    run="fail"
  fi
  if [[ "$lint" == "fail" || "$run" == "fail" ]]; then ((fail++))
  else ((pass++)); fi
  printf '%-38s lint=%-7s run=%s\n' "$rel" "$lint" "$run"
  row="{\"dir\": \"$rel\", \"lint\": \"$lint\", \"run\": \"$run\","
  rows+=("$row \"requires\": \"$requires\"}")
done

{
  echo "{"
  echo "  \"checked\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
  echo "  \"pass\": $pass, \"fail\": $fail,"
  echo "  \"skipped_run\": $skip,"
  echo "  \"examples\": ["
  for i in "${!rows[@]}"; do
    sep=","; [[ $i -eq $((${#rows[@]}-1)) ]] && sep=""
    echo "    ${rows[$i]}$sep"
  done
  echo "  ]"
  echo "}"
} > "$STATUS"
echo "wrote $STATUS  (pass=$pass fail=$fail skipped_run=$skip)"
[[ $fail -eq 0 ]]
