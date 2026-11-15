# sim.sh -- sourced by this chapter's run scripts.
#
# The book's simulator flags, and three small readers of a run's
# output: the assertions that failed, by clock tick; the cover
# statements in a coverage database, with their counts.
VFLAGS="--binary --timing --timescale 1ns/1ps -Wall -Wno-DECLFILENAME \
  -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT"

# covers FILE -- every cover statement in a coverage database with its
# count, on one line; the record's last field is the hierarchical name.
covers() {
  awk -F"' " '/\001t\002user/ { n = split($1, p, "."); c = c "  " p[n] "=" $2 }
    END { print "covers:" c }' "$1" | fold -s -w 78 | sed 's/ *$//'
}

# failures -- reads a simulation's output and prints one line per
# failed assertion: the clock tick (10 ns period, first edge at 5 ns)
# and the assertion's label.
failures() {
  local pat='^\[([0-9]+)\] %Error: .*Assertion failed in '
  pat="$pat"'[^ ]*\.([A-Za-z_0-9]+): .*'
  sed -nE "s/$pat/\1 \2/p" \
    | awk '{ printf "  tick %2d: %s failed\n", ($1 - 5000) / 10000, $2 }'
}
