# common.sh -- sourced by the chapter's run scripts. The book's
# Verilator flags (examples/mk/sv.mk) and the two testbench builds.
VFLAGS="--binary --timing --timescale 1ns/1ps -Wall -Wno-DECLFILENAME \
  -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT"
TB=../tb
RTL=../rtl
V1_SRC="$TB/lint.vlt $RTL/dma_regs_pkg.sv $TB/dma_ifs.sv \
  $TB/dma_tb_pkg.sv $RTL/dma_v1.v $TB/tb_v1.sv"
V2_SRC="$TB/lint.vlt $RTL/dma_regs_pkg.sv $TB/dma_ifs.sv \
  $TB/dma_tb_pkg.sv $RTL/dma_v2.sv $TB/tb_v2.sv"

# Covergroup bins from a coverage .dat, one line per coverpoint or
# cross ("<point>: bin=count ..."), as Chapter 8 reads them: a record
# is C '<key>' <count>, the key \001<tag>\002<value> fields, the h tag
# the path <group>.<point>.<bin>.
bins() {
  awk -F'\001' '/^C /{ if (index($0,"\001t\002covergroup")==0) next;
    split($NF, a, "\047 "); h = substr(a[1], 3);
    n = split(h, p, "."); item = p[2]; bin = p[n];
    if (!(item in seen)) { seen[item] = 1; order[++k] = item }
    line[item] = line[item] " " bin "=" a[2] }
    END { for (i = 1; i <= k; i++) print order[i] ":" line[order[i]] }' \
    "$1" | fold -s -w 78
}
zero_bins() {
  awk -F'\001' '/^C /{ if (index($0,"\001t\002covergroup")==0) next;
    split($NF, a, "\047 "); h = substr(a[1], 3); sub(/^[^.]*\./, "", h);
    if (a[2] == 0) z = z " " h }
    END { print "zero bins:" (z == "" ? " none" : z) }' "$1" | fold -s -w 78
}
