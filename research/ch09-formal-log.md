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

## 7. Round 1 fixes (gate-2 reviews of 2026-11-15)

Inputs: `docs/reviews/ch09-gate2a-2026-11-15.md` (text, "A") and
`docs/reviews/ch09-gate2b-2026-11-15.md` (code, "B"). One line per
finding, appended as each is done.

- code B5: `informal.tcl` `expect` now checks every property whose name
  ends in the label and reports each mismatch by its full name; a label
  that matches nothing is reported "missing". Verified on the review's
  two-instance design (`u_bad`/`u_good` `Same_A`, `expect proven
  Same_A`): before, rc 0; now `unexpected: two.u_bad.Same_A is cex`,
  rc 1. A full name (`two.u_good.Same_A`) still selects one (rc 0); a
  wrong name gives "missing", rc 1.
- code B5 hardening (non-blocking): `informal.sh` exits 1 when the report
  has an `unexpected:` line, whatever the script's last command. Same
  design with `finish` deleted: rc 1 (before: 0).
- code B2: `run_checker.sh`, `run_vacuity.sh` and `run_axi.sh` now test
  what their verdict lines say, through a `need` helper added to
  `common/sim.sh`, and exit 1 otherwise. `run_checker.sh`: every cover
  of the repaired FIFO non-zero, the original's default run stops on
  `FullBackward_A` alone, its long run names no other label, and
  `FullReached_C=0`. `run_vacuity.sh`: the count is of `Ack_A` failures
  only; the quiet run must be 0 failures with `Req_C=0`, the traffic
  run more than 0 with `Req_C` above 0. `run_axi.sh`: the as-is run
  must print `result: PASS` with all six covers non-zero; each mutant
  is given its label, and the first failure of the bound checker must
  be that label (`failures` reads only `%Error ... Assertion failed in
  <hier>.<label>:`, so the testbench's own `$fatal` cannot count).
  Outputs unchanged (diffed against the committed `run.out`). Neutered
  in a scratch copy (`cp -r` of `examples/`, repository untouched):
  `FullBackward_A` -> `full |-> 1'b1`: `make run` rc 2, "the original
  did not stop on FullBackward_A alone"; `Ack_A` -> `req |=> 1'b1`:
  rc 2, "Ack_A did not fail"; `ArHeld_A` antecedent `&& 1'b0`: rc 2,
  "mutant drop did not fail ArHeld_A"; `ArStable_A` consequent `1'b1`:
  rc 2, "mutant wander did not fail ArStable_A"; FIFO bind file
  emptied: rc 2, "FullReached_C read zero on the repaired FIFO".
- text B1: L43 rewritten as a forward pointer: @sec-ch11 builds the DMA;
  AXI VALID/READY and the two source rules introduced in place and cited
  to Arm IHI 0022C, not to @sec-ch11-waves. @sec-ch09-axi opens with what
  the section needs of the DMA (APB-programmed, AXI4-Lite master, drives
  AR/AW/W, receives R/B, a random test against a memory model with four
  READY styles picked per round; read off `tb_v2.sv:186` and
  `dma_tb_pkg.sv`). "case study" removed throughout; exercise 7 names the
  testbench of @sec-ch09-axi.
- text B2: splice `lines="199-209"` (the function through `endfunction`,
  same as ch11 line 142).
- text B3 (a)-(e) / code B4: caption "four times it passed"; "the first
  row"; "the last line of that run's report"; "two from the plan ... and
  a third the plan does not have"; "No verdict changes; the only new row
  is the second assumption's".
- text B4: Definition box, the paragraph after it and the Summary bullet
  now say: a finite run never refutes liveness, settles F p for the run
  once p is seen, and decides nothing for G F p. Bauer et al.'s sentence
  checked against TUM-I0724 (fetched 2026-11-15): verbatim, Section
  III.A, said of GFp; the text now names G F p beside it.
- text B5: until now reflexive: q here or later, p from here to the one
  before.
- text B6: NOT CHANGED. `clause 20.12` kept: slang's
  `docs/language-support.dox` (local copy, "complete support for ... IEEE
  1800-2023") lists 20.11 Assertion control tasks and 20.12 Sampled value
  system functions. The reviewer's numbering (20.12 = assertion control)
  is the 1800-2017 one. The PDF itself was not readable.
- text B7: "three verbs that this chapter uses ..., and a fourth,
  `restrict`, that constrains a formal tool's inputs like an assumption
  and is not checked in simulation".
- text B8: the four suffixes the formal README gives (`_A`, `_M`, `_P`,
  `_S`), and `_C` attributed to the TL-UL checker.
- text B9: sentence now says the command names are the ones InFormal's
  README describes as JasperGold / VC Formal style, and that the book has
  not run them on either tool.
- text B10: L454 states the rule's form ("for every offer there is a
  run ...") and that the cover witnesses the first offer only; L466 says
  the master is able to offer first, not that it always does; Summary
  bullet reworded. No new assertion added.
- text B11: (1) `matrix.py` now writes the Icarus `-gsupported-assertions`
  counts into each caption (main: tried 58, 13 build, 10 wrong; extra:
  tried 9, 2 build, 2 wrong); the prose cites the captions. (2) new probe
  `x16_imm_status.sv` (mode `sim=status`): failed immediate assertion, no
  action block: Verilator "failure printed, run stops, exit status 1",
  Icarus "failure printed, run goes on, exit status 0". (3) new probe
  `x17_interface.sv`: concurrent assertion in an interface: Verilator
  runs (both), InFormal runs. (4) portfolio sentence now rests on the
  README ("The first definitive verdict wins, and contradicting engines
  are flagged"); "where two engines could be compared they agreed",
  "its depth is not always the shortest", the IC3 timing comparison and
  the k-induction-on-AXI minutes all removed.
- text B12: refs.bib `pnueli1977temporal` -> @inproceedings, FOCS 1977,
  pp. 46-57, DOI 10.1109/SFCS.1977.32 (record at
  people.irisa.fr/Nicolas.Markey/biblio/focs1977-Pnu, and the research
  note's copy showing pp. 46-57); `beer2001vacuity` + number 2, DOI
  10.1023/A:1008779610539 (scilit record); `kantrowitznoack1996done` +
  pp. 325-330, DOI 10.1145/240518.240580, publisher ACM (bibtex.github.io
  DAC-1996-KantrowitzN, DBLP-derived). The paper itself (UCI compendium
  23_5.pdf) was read again: title "I'm Done Simulating; Now What?",
  Figure 2 Assertion Checkers 34%, Self-Checking Test 11%; it prints no
  page numbers. `cocotb-docs` citation removed: the sentence now says
  only what the monitor does (appends failures, the test asserts at its
  end). Further-reading lines carry venue / volume.
- text B13: "a large open-source user".
- code B3: `p30_past1.sv` now prints first-tick `$past` of a net, of a
  variable set in an `initial` block and of one with a declaration
  initializer: "net 0, initial-block 0, initializer 5" on 5.052 and
  5.054 alike (matrix.md row). Chapter L135, L297 and the Pitfall say
  exactly that.
- code B6: the falling-edge sentence is restricted to the
  bounded-response, vacuity and FIFO testbenches; the handshake and goto
  listings are described as counter-driven through a nonblocking
  assignment, and why that is race-free.
- non-blocking done: text N3 (disable iff acts on current values), N5/
  code N10 (exit-status wording), N6 (`load` and `clear -all`), N9
  ("explicit"), N10 (depth and engine column defined at first use), N11
  (quotation as written in fifo.sv), N14 (labels for "the first
  chapter"), N17 (forward pointer to the zero); code N3 (contradiction
  Pitfall), N4 (constant `initial` register), N6 (5.054 "not always in
  the same way"), N7 (glitch count depends on source order).
- non-blocking not done: text N2 (`$rose` on a vector: no probe measures
  bit 0), N4, N8 (upstream reporting is the author's call), N12, N13
  (cocotb log width: the filter is shared with ch01), N15 (length), N16;
  code N5, N11, N12.
- code N8 (non-blocking, done): `check-examples.sh` tests REQUIRES with
  `type -P`, and a skipped example's `run.out` is no longer rewritten
  from a stale `run.log`.
- code B1: `matrix.py` removes each probe's Verilator `Mdir` before
  building it, so the NEVERMATCH note no longer depends on whether
  Verilator re-ran. Verified: `make clean`, `make run` (5 min 33 s),
  copy of `matrix.md`; then `make run` again over the kept `build/`:
  `cmp` of the two `matrix.md` files reports identical. The clean-run
  table now carries "warns NEVERMATCH" on the never-matching antecedent
  row (the committed table, a re-run variant, did not).
- code N1 (non-blocking): the example's own `clean::` rule is gone;
  `make clean` left `matrix.md` in place (git status clean for it).
- code N2 (non-blocking): `matrix.py` stops with status 1 and leaves
  `matrix.md` untouched when verilator, iverilog, vvp, the next
  Verilator or informal is missing; the Makefile declares REQUIRES :=
  informal so a machine without it records a skip (as CI does).
  Verified with VERILATOR_NEXT=/nonexistent: rc 1, matrix.md unchanged.
- Final check (2026-11-15): `make clean` in all fourteen examples, then
  `scripts/check-examples.sh ch09`: 14 of 14 lint=pass run=pass. Every
  `run.out` except `support-matrix/run.out` is byte-identical to the
  committed one; `matrix.md` identical to the earlier clean run.
  `scripts/check-structure.sh` and `scripts/check-citations.sh` pass.
  Build directories removed.

## 8. Round 2 fixes (gate-2 reviews C and D of 2026-11-15)

Inputs: `docs/reviews/ch09-gate2c-2026-11-15.md` (text, "C") and
`docs/reviews/ch09-gate2d-2026-11-15.md` (code, "D"). One line per
finding id, appended as each is done.

- text C1: @tbl-ch09-ltl liveness row now "A FIFO that stops being
  written and keeps being read drains | **G** (**G** (rd ∧ ¬wr) → **F**
  empty)", as the reviewer proposed. The argument after the table now
  reads "because the writes may stop and the reads that follow may still
  drain it" (a FIFO of sixteen entries needs sixteen reads, so "the next
  read" was no longer right). Checked by hand: the one-entry trace with
  rd and wr every tick no longer satisfies the antecedent.
- text C2: "every rule with a reset term holds at least once and fails
  exactly once"; `HeldRaw_A` fails at 11 and 14 in `handshake/run.out`,
  the other three once each. The run script now also checks the label at
  each tick (see M1).
- code M1: `run_handshake.sh` checks the five failures by tick and label
  and `Waited_C=5`; `run_response.sh` checks `Waited_C=0` on the slow
  responder and `Waited_C=[1-9]` on the correct one. Outputs unchanged
  (diffed). Mutation in a scratch copy, both covers `disable iff (1'b1)`:
  handshake rc 1 "Waited_C did not count five"; bounded-response rc 1
  "the correct responder never granted on the last permitted tick".
- text C3: prose now gives the script's expression,
  `count[3:0] == wr_ptr - rd_ptr`, says both sides are four bits (count
  modulo sixteen against the pointer distance) and why the unsliced
  five-bit comparison is false (wrapped pointers, full FIFO). Widths read
  off `rtl/fifo_fixed.sv` (count `[PTR_W:0]`, pointers `[PTR_W-1:0]`,
  PTR_W 4); `fifo-proof/run.out` still shows `CountPtrs_A` proven.
- text C4: the claim of a comparison is gone. The sentence now says what
  `check-examples.sh` does (rewrites each `run.out` from `run.log`; the
  book splices `run.out`) and what was measured: "two runs in a row
  print the same report. The outputs printed in this chapter are
  regenerated on every check of the examples, so a change in the tool's
  report changes the page." Read against `scripts/check-examples.sh`
  lines 101-107. Repeatability: round 1's final check and reviewer D's
  two parallel clean runs gave byte-identical `run.out` files.
- text C5: "Michael Kantrowitz" in the Further-reading line, as in
  `refs.bib`. Byline checked 2026-11-15 against the paper itself (UCI
  compendium websrv.cecs.uci.edu/~papers/compendium94-03/papers/1996/
  dac96/pdffiles/23_5.pdf: "Michael Kantrowitz and Lisa M. Noack",
  Digital Equipment Corporation) and the DBLP-derived record
  bibtex.github.io/DAC-1996-KantrowitzN (same author field, pp. 325-330,
  DOI 10.1145/240518.240580). doi.org and Crossref were not reachable
  from here.
- text C6: `axi-formal/axi.tcl` line 3 "modeled" (also
  `support-matrix/FINDINGS.md`, not spliced). Grep of every file under
  `examples/ch09-temporal-properties/` (build directories and logs
  excluded) for modelled, behaviour, initialis-, -our, -lled/-lling,
  -ise/-ised/-isation, -tre, -ogue, whilst, amongst, judgement: no other
  hit. "afterwards" (two comments in `fifo_sva.sv`) left: it is American
  usage too and the book's prose uses it in five chapters.
- text N2: "case study" gone from `run_axi.sh` (header, and the echo that
  prints `run.out` line 1, now "its random test"), `axi-formal/axi.tcl`
  line 1 and `axi-formal/Makefile` line 1 ("the DMA engine").
  `axi-rules/run.out` regenerated by the final check.
- text N1: L133 now cites clause 16.9.3 for what the sampled-value
  functions do and keeps clause 20.12 only for where the standard lists
  them, as reviewer C recommends (16.9.3 is the same number in 2009,
  2012, 2017 and, per Verilator's 1800-2023 message, 2023).
- code D1: new probe `support-matrix/probes/x18_pending_end.sv`, a row
  of @tbl-ch09-support-x (`sim=pending` in `matrix.py`): one build per
  operator (`s_eventually`, `##[1:$]`, `##[1:3]`, `until`, `s_until`),
  `a` at tick 12 of 14, `b` never; and a GOOD build with `b` at 13. The
  runner reads the action-block count before `$finish` and in a `final`
  block, any "Assertion failed" printed after `$finish`, whether it
  carries the label, and the exit status. Measured on 5.052 and 5.054
  alike: four operators silent, exit 0, no action block; `s_until`
  reported after `$finish` and after the final block ("Assertion failed
  in top", file and line, no label), action block not run, exit 1; every
  GOOD build silent, exit 0. Agrees with reviewer D's `su.sv`/`end.sv`.
  L82 rewritten to say exactly that (and that `strong(...)` does not
  build); L297 restricted the same way.
- code M5: `matrix.py` now prints "skipped: missing <tool>; not
  measured, and matrix.md left as it is" and exits 0 when a column's
  tool is missing; `scripts/check-examples.sh` records a run whose
  output has a line beginning "skipped" (and exit 0) as skipped, as it
  already did for lint, and so leaves that example's `run.out` alone.
  Makefile comment updated. Verified: `VERILATOR_NEXT=/nonexistent
  scripts/check-examples.sh ch09-temporal-properties/support-matrix`:
  `run=skipped (missing /nonexistent ...)`, `matrix.md` and `run.out`
  byte-identical to before. No other example's run output begins
  "skipped" (grep of every `run.out`).
- code D2: `fifo-cocotb` `make run` now runs the test twice: on the
  repaired FIFO (must pass, as before) and then, with FIFO_EXPECT=bug,
  in its own build directory `build/original` (code M6) on
  `ch01-what-is-dv/rtl/fifo.sv`, where the test passes only if the
  monitor reports at least one failure, every failure is
  `FullBackward_A`, and `FullReached_C` is 0. The Makefile prints the
  second run's monitor lines (sim time and timing columns stripped, so
  `run.out` stays deterministic) and EXPECT_OUTPUT is the final line
  "the monitor failed the original FIFO, as required". Measured: 118
  failures, first three FullBackward_A at samples 28, 29, 31,
  FullReached_C 0. Mutations in a scratch copy of the example tree:
  `check()` a no-op (`if not ok and False`): rc 2, "the monitor passed
  the original FIFO"; FullBackward_A weakened to `occ >= DEPTH - 1`:
  rc 2, same message; ORIGINAL pointed at the repaired FIFO: rc 2. Prose
  after the listing says what the second run requires and why.
- text N5: "and less the `Drained_C` cover" added.
- text N11 (half): exercise 8 no longer asks for the sample number in
  advance; it now reads the second run's output. Exercise 10 left as is
  (the reader is expected to see that no row warns; the author may want
  to say so).
- `scripts/check-examples.sh` is spliced whole by
  `appendices/appF-building-examples.qmd` (@sec-appF-checking); the new
  block is five lines with its comment, and nothing that appendix says
  about the script is changed by it (it describes EXPECT, EXPECT_OUTPUT,
  LINT_ONLY and the status file).
- non-blocking not done, and why: text N3 (the reset-cycle sentence
  needs a claim about the tool's check start with a probe behind it;
  reviewer D's own d5 probe supports it, but the wording is the
  author's), N4 (the exit-status claim would need another matrix row;
  reviewer D's d4 probe agrees with the text), N6, N8, N9, N10 (no probe
  measures `$rose` on a vector's bit 0), N12, N13, N14 (length: a cut
  is a structural edit), N15, N16, N17, and exercise 10 of N11: each is
  wording that no reviewer called wrong, left for the third round so
  this round changes only what was found to be false. N7 (fairness to
  InFormal; upstream reporting) stays the author's call. Code M2
  (`expect` glob matching: fails closed today), M3 (typed counts: still
  agree with the regenerated captions, checked again after the final
  run), M4 (`run.out` widths: the house rule covers source files; the
  cocotb filter is shared with ch01), M6 (handled for D2 only: the
  shared `cocotb.mk` is unchanged).
- Final check (2026-11-15): `make clean` in all fourteen ch09 examples,
  then `scripts/check-examples.sh ch09`: 14 of 14 lint=pass run=pass,
  rc 0. Compared with the committed files: `axi-rules/run.out` differs
  only in its first line (N2); `fifo-cocotb/run.out` gains the nine
  lines of the second run (D2); `matrix.md` gains the x18 row and its
  caption counts (Verilator 13/14 runs, wrong counts unchanged at 4 and
  3, so the typed counts of L295, L481 and L494 still hold); every other
  `run.out` is byte-identical, including `handshake` and
  `bounded-response` after the M1 checks. `scripts/check-structure.sh`
  and `scripts/check-citations.sh` pass. Build directories removed.
