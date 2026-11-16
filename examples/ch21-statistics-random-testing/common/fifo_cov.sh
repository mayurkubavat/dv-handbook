# fifo_cov.sh -- sourced by the chapter's runners: builds the coverage
# chapter's FIFO testbench once and runs it under many seeds, one
# coverage database per seed. Both files are read by path from their
# own chapters and never copied: tb_fifo_cov.sv and its lint.vlt from
# the coverage chapter, fifo.sv (the buggy FIFO) from the first.
CH08=../../ch08-functional-coverage/fifo-coverage
FIFO_RTL=../../ch01-what-is-dv/rtl/fifo.sv

# The book's flags from examples/mk/sv.mk, plus --coverage, as the
# coverage chapter's runner builds it.
build_fifo_cov() {   # build_fifo_cov <dir>
  mkdir -p "$1"
  verilator --binary --timing --timescale 1ns/1ps -Wall -Wno-DECLFILENAME \
      -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT --coverage \
      --top-module tb_fifo_cov -Mdir "$1" $CH08/lint.vlt $FIFO_RTL \
      $CH08/tb_fifo_cov.sv >/dev/null
}

# Seeds first..last under one generator; writes <dir>/<tag>_<seed>.dat
# and appends "<seed> <0|1>" to <dir>/<tag>.trig, 1 when the run
# printed the testbench's "covered: push while full" line.
run_fifo_cov() {     # run_fifo_cov <dir> <bias> <n> <first> <last> <tag>
  local dir=$1 bias=$2 n=$3 first=$4 last=$5 tag=$6 s hit
  : > "$dir/$tag.trig"
  for s in $(seq "$first" "$last"); do
    hit=$("$dir/Vtb_fifo_cov" +bias="$bias" +n="$n" +verilator+seed+"$s" \
          +verilator+coverage+file+"$dir/${tag}_$s.dat" \
          | grep -c '^covered: push while full' || true)
    echo "$s $hit" >> "$dir/$tag.trig"
  done
}
