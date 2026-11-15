# Chapter 9 formal half: running log

Started 2026-11-15. Tool: InFormal 0.1.0, commit 5114330
(`/opt/dvtools/bin/informal`). Verilator 5.052 and 5.054, Icarus 13.0.
Appended to as the work proceeds; newest entries last.

## 1. Reading

- Read `AGENTS.md`, `STATUS.md` (not edited), and
  `research/informal-measurements/FINDINGS.md` sections 0 and A to H.

## 2. Checkers converted to the concurrent subset (Verilator 5.052)

`fifo_sva.sv`, `hs_check.sv`, `ack_check.sv`, `resp_check.sv` and
`axil_master_sva.sv` rewritten as `assert property (@(posedge clk)
disable iff (!rst_n) ...)` with booleans, `|->`, `|=>`, `$stable`.
`past_ok`/`started`/`ar_w` registers removed; `hs_check` takes `rst_n`
(was `rst`). Each run script re-run on 5.052, outputs compared with the
committed `run.out`:

- fifo-checker: identical (tick 35, 114 failures, cover counts).
- vacuity, bounded-response, axi-rules: identical.
- handshake: same five failures at the same ticks; the two tick-11
  lines swap order; `Waited_C` is 6, was 5 (the cover is now the
  antecedent, so the offer cut off by reset at tick 13 counts).
- An empty `engines.toml` is enough for the in-house engines
  (`informal-bmc`, `informal-kind`, `informal-ic3`); the book's scripts
  use only those, so rIC3 and ABC are not needed by a reader.

## 3. Build integration

- `examples/mk/informal.mk` (EXAMPLE_LANG := informal), `informal.sh`
  (wrapper: engine list beside it, workdir, time column filtered,
  script's exit status passed on, "skipped:" when the program is
  missing), `informal.tcl` (`expect`, `trace`, `finish`),
  `informal-engines.toml` (comments only; in-house engines need no
  entry).
- `scripts/check-examples.sh`: a `REQUIRES` that names a program on the
  PATH is now satisfied, so `REQUIRES := informal` runs here and is
  skipped where the tool is absent. `commercial` and `uvm-systemc`
  behave as before (neither is a command).
- `common/vcdtable.py`: prints a counterexample VCD as one row per
  cycle; reads the first declaration of a name, which steps over the
  duplicate `clk`.

## 4. Formal examples, measured (informal 0.1.0, one engine per prove)

All agree with FINDINGS unless marked DIFFERS.

- fifo-formal (Ch.1 FIFO + `fifo_sva.sv` + `fifo_bind.sv`,
  informal-kind): NoOverflow, FullForward, EmptyExact, PushFull,
  PopEmpty, Sync proven; FullBackward cex depth 16; FullReached_C
  unreachable; PushFull_C covered depth 17 (16 before the cover got its
  `##1 1'b1`), PopEmpty_C, Drained_C covered. Two runs byte-identical
  after the time filter.
- The checker as committed before this session (clocked immediate
  assertions, `git show HEAD:...fifo_sva.sv`): empty table, `proven 0
  cex 0 ...`, exit 0. Confirms FINDINGS A.1.
- fifo-proof (fixed FIFO): all seven assertions proven by informal-kind
  (NoOverflow 0.72 s, FullForward 3.06 s, FullBackward 2.68 s,
  EmptyExact 3.65 s), covers at depth 17/17/1/33. Tcl properties with
  WIDTH left at 8 (FINDINGS used WIDTH 1): informal-bmc undetermined on
  both; informal-kind: EmptyPtrs_A undetermined (limit 15 s then 10 s),
  CountPtrs_A proven 0.02 s; with CountPtrs_M assumed EmptyPtrs_A
  proven 0.02 s; informal-ic3 alone proven 1.96 s.
- vacuity-formal: free inputs Ack_A cex depth 1, Req_C covered depth 0;
  `assume {!req}`: proven / unreachable; plus `assume {req}`: proven /
  unreachable. NEW (not in FINDINGS): assumptions `{req}` and
  `{req |=> !req}` conflict only at the second tick; Ack_A is proven
  and the antecedent cover Req_C is still *covered* (depth 0); only a
  cover that spans the consequent's tick (`req ##1 1'b1`) is
  unreachable. The chapter's covers of `|=>` rules were changed to
  `a ##1 1'b1` for this reason.
- assume-formal (new `hs_sink.sv` + `hs_check.sv` bound): free inputs
  all five assertions cex depth 2; with Held_M and Stable_M assumed by
  Tcl all proven (HeldRaw_A too: a Tcl assumption is not disabled in
  the reset cycle).
- response-formal: correct responder Window_A proven; slow-by-one cex
  depth 4. Waited_C is *covered* (depth 4) on the slow responder, where
  the simulation's 40 random ticks counted 0.
- axi-formal: DIFFERS in engine. informal-kind alone did not finish the
  six DMA rules in about four minutes (stopped by hand; FINDINGS ran
  the portfolio, where IC3 engines won every row). With informal-ic3:
  six rules proven (0.04 to 0.18 s), covers depth 4/7/7 (FINDINGS 5/8/8
  with a different cover text), mutants drop and wander cex depth 5.
  `$past(ARVALID && !ARREADY) |-> ARVALID` cex depth 1 with PRESETn=0,
  ARVALID=1 in cycle 0: confirms B.2.
- NEW: "must not wait for READY". Assuming all three READYs low makes
  AWVALID and WVALID unreachable (the DMA reads before it writes), so
  the check is three covers in the checker, `xVALID && !xREADY && !seen`
  with `seen` = that READY has been high since reset. All three covered
  (depth 4/7/7); a third mutant that waits for ARREADY in R_IDLE makes
  ArFirst_C unreachable with all six assertions still proven. In the
  simulation each of the three counts 1.
- Default portfolio. With the research `engines.toml` (rIC3, ABC
  entries): 6 runs of the opener script gave 6 different reports
  (confirms D.5). DIFFERS with the book's empty engine list: 6 runs
  identical, but FullBackward_A is reported `informal-bmc-65 depth 64`
  and PushFull_C depth 17, PopEmpty_C depth 2: repeatable here, not
  minimal.

## 5. Support matrix (clean build, 6 min on 4 cores)

Columns Verilator 5.052, 5.054 (now every row), Icarus 13.0, InFormal
0.1.0. Rows p00, p65 to p71 dropped (sby/Yosys questions); p40 rewritten
as a clocked liveness probe; p48 rewritten as concurrent assume/assert.
InFormal reads each probe with `+define+FORMAL`, top `dut`, BAD 0 and 1,
`reset -none`, `assume {t < 14}` where `t` exists, informal-kind (ic3
on p39, p40), 20 s.

- Verilator 5.052 main: 47 runs, 6 wrong, 9 no build, 2 n/a; 5.054 the
  same. Extra: 5.052 10/4/2, 5.054 11/3/2 (x08 fixed).
- Icarus main 3 runs, 58 no build; `-gsupported-assertions`: 13 + 1
  build, 10 + 1 wrong.
- InFormal main: 39 runs, 7 wrong, 12 no build, 6 n/a; extra 5 runs, 8
  wrong, 1 no build, 2 n/a. Every "wrong" is an empty report with no
  message: immediate/deferred asserts, immediate cover, `expect`,
  NEW: a property with a local variable (p28), and p36 (the probe has
  `$isunknown`; presumably FINDINGS F.1b, not separated here).
  NEW refusals not in FINDINGS D.1: `[*1:$]`, an antecedent that has
  no match, `checker` ("SystemVerilog errors"), followed-by.
- p36 taken apart: deleting the `$isunknown` assertion from the probe
  brings the other three (`$onehot`, `$onehot0`, `$countones`) back
  into the report, each `cex depth 5` with BAD 1. One `$isunknown`
  assertion removes all RTL properties of the module, silently.

## 6. Sources opened for the comparison table (2026-11-15)

- https://github.com/mayurkubavat/informal (README, NOTICE in the
  clone at commit 5114330): title "InFormal", copyright Mayur Kubavat,
  Apache-2.0, no tags.
- https://yosyshq.readthedocs.io/projects/sby/en/latest/ : "SymbiYosys
  (sby) is a front-end driver program for Yosys-based formal hardware
  verification flows."; `verilog.html`: "SymbiYosys supports three
  basic immediate assertion types"; `verific.html`: "This document
  describes features only available with the commercial Tabby CAD
  Suite and the included Verific frontend."
- https://www.synopsys.com/verification/static-and-formal-verification/vc-formal.html
  (title "VC Formal: Formal Verification Solution | Synopsys"; FPV
  described as verifying SVA properties).
- https://www.siemens.com/en-us/products/ic/questa-one/formal-verification/
  (title "Questa One Formal Verification Suite | Siemens"). The page
  does not use the name "Questa Formal"; the chapter uses the page's
  name.
- Cadence: www.cadence.com refused both fetches; the "Jasper FPV App"
  page was read at the same path on newstaging.cadence.com ("supports
  SystemVerilog Assertion (SVA) or Property Specification Language
  (PSL) properties"). The bib note says so. All three vendor pages
  were read through a fetch tool that summarizes; the chapter
  paraphrases and quotes none of them.
