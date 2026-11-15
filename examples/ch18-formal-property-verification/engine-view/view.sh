#!/usr/bin/env bash
# view.sh -- what the tool shows of an engine's work.
#
# 1. The report rows of view.tcl: the pointer property at two and four
#    entries, by induction and by IC3.
# 2. The same IC3 proofs with INFORMAL_IC3_STATS=1, a switch the tool's
#    engine document lists among its experiments: the line with the
#    number of frames, lemmas and queries, and the line of the check
#    made on the invariant before the verdict is reported. Times and
#    paths are cut; each proof is run twice and the two must agree.
# 3. The induction engine as a child process on the model the shell
#    wrote for two entries: the last bound it reports, and its verdict.
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v informal >/dev/null 2>&1; then
  echo "skipped: informal is not on the PATH"
  exit 0
fi
MK=../../mk
"$MK/informal.sh" view.tcl build/informal

# stats DEPTH -- one IC3 proof with the statistics switch, filtered.
stats() {
  local head='informal-ic3: frames [0-9]+ lemmas [0-9]+'
  DEPTHS=$1 ENGINES=informal-ic3 INFORMAL_IC3_STATS=1 \
    informal shell --engines "$MK/informal-engines.toml" \
      --workdir "build/stats$1" -c "set ::workdir build/stats$1" \
      -c "source $MK/informal.tcl" view.tcl 2>&1 |
    sed -nE "s/^($head) ctps [0-9]+ (queries [0-9]+).*/\\1 \\2/p;
             s/^certificate: Ok\(\(\)\).*/certificate: Ok/p"
}
for depth in 2 4; do
  echo "=== $depth entries, informal-ic3 with INFORMAL_IC3_STATS=1"
  first=$(stats $depth)
  [[ "$first" == "$(stats $depth)" ]] || {
    echo "unexpected: two runs printed different statistics"; exit 1; }
  echo "$first"
  grep -q '^certificate: Ok$' <<<"$first" || {
    echo "unexpected: no certificate line"; exit 1; }
done

echo "=== 2 entries, the induction engine as a child process"
echo "\$ informal engine informal-kind build/stats2/prop_0.btor2"
child=$(informal engine informal-kind build/stats2/prop_0.btor2 2>&1)
last=$(grep -o '"bound":[0-9]*' <<<"$child" | tail -1 | cut -d: -f2)
echo "last bound reported before the verdict: $last"
grep '"result"' <<<"$child"
grep -q '"verdict":"safe"' <<<"$child" || {
  echo "unexpected: the child did not report safe"; exit 1; }
echo "verdict: a count of frames and lemmas, a checked certificate," \
     "and a bound; no lemma and no failing step"
