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
  # Makefile variables may carry a trailing comment; strip it first.
  mkvar() { grep -E "^$1\s*:?=" "$d/Makefile" | sed -E 's/#.*//; s/.*=\s*//' \
            | tr -d ' '; }
  requires=$(mkvar REQUIRES)
  expect=$(mkvar EXPECT); expect=${expect:-pass}
  # A bare EXPECT := fail accepts any failure, so a missing tool or a broken
  # import counts as the bug the example exists to find. EXPECT_OUTPUT names
  # a string the run must print for the failure to be the expected one.
  expect_output=$(grep -E "^EXPECT_OUTPUT\s*:?=" "$d/Makefile" \
                  | sed -E 's/.*=[[:space:]]*//')
  lint="pass"; run="pass"
  if ! (cd "$d" && $RUN make -s lint >"$d/lint.log" 2>&1); then
    lint="fail"
  elif grep -q '^skipped' "$d/lint.log"; then
    lint="skipped"
  fi
  if [[ -n "$requires" ]]; then
    run="skipped ($requires)"; ((skip++))
  else
    (cd "$d" && $RUN make -s run >"$d/run.log" 2>&1); rc=$?
    if [[ "$expect" == "fail" ]]; then
      # The example exists to expose a bug: a clean exit would mean it missed.
      if [[ $rc -eq 0 ]]; then run="fail (expected to fail, but passed)"
      elif [[ -n "$expect_output" ]] \
           && ! grep -qF -- "$expect_output" "$d/run.log"; then
        run="fail (failed, but not with '$expect_output')"
      else run="pass (failed as expected)"; fi
    elif [[ $rc -ne 0 ]]; then run="fail"; fi
  fi
  if [[ "$lint" == "fail" || "$run" == fail* ]]; then ((fail++))
  else ((pass++)); fi
  printf '%-38s lint=%-7s run=%s\n' "$rel" "$lint" "$run"
  # A trimmed copy of the run output for the book to include verbatim:
  # simulator banners, make chatter and abort traces removed.
  [[ -f "$d/run.log" ]] && grep -vE '^- |^%Fatal|^%Error|^Aborting|^make:|^\[[0-9]+\] %Fatal|^V e r i l a t i o n|Verilated|Abort trap|conda\.cli|^/bin/sh|Seeding Python random|^$' "$d/run.log" \
    | sed -E 's/(\*\* .*[0-9]+\.[0-9]{2}) +[0-9]+\.[0-9]{2} +[0-9]+\.[0-9]{2} +\*\*$/\1  **/' > "$d/run.out"
  # Show why, so a failure is readable in CI without downloading logs.
  [[ "$lint" == "fail" ]] && sed 's/^/    | /' "$d/lint.log" | tail -12
  [[ "$run" == fail* ]] && sed 's/^/    | /' "$d/run.log" | tail -12
  row="{\"dir\": \"$rel\", \"lint\": \"$lint\", \"run\": \"$run\","
  rows+=("$row \"requires\": \"$requires\", \"expect\": \"$expect\"}")
done

# Merge this run's rows into the status file, so a filtered run (one chapter)
# updates its own examples without erasing the record of the others.
python3 - "$STATUS" "${rows[@]}" <<'PY'
import json, sys, pathlib, datetime
path = pathlib.Path(sys.argv[1]); rows = [json.loads(r) for r in sys.argv[2:]]
old = {}
if path.exists():
    try: old = {e["dir"]: e for e in json.loads(path.read_text())["examples"]}
    except Exception: old = {}
for r in rows: old[r["dir"]] = r
allrows = [old[k] for k in sorted(old)]
summary = {"checked": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "pass": sum(1 for e in allrows if e["lint"] != "fail" and not e["run"].startswith("fail")),
           "fail": sum(1 for e in allrows if e["lint"] == "fail" or e["run"].startswith("fail")),
           "skipped_run": sum(1 for e in allrows if e["run"].startswith("skipped")),
           "examples": allrows}
path.write_text(json.dumps(summary, indent=2) + "\n")
PY
echo "wrote $STATUS  (pass=$pass fail=$fail skipped_run=$skip)"
[[ $fail -eq 0 ]]
