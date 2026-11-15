# InFormal measurements for the book's formal chapters

Measured 2026-11-15 on InFormal 0.1.0, commit 5114330, binary
`/opt/dvtools/bin/informal`, with `abc` (77875a3b6) and `ric3` (4d63899) on
PATH, CaDiCaL c607304 linked, **Bitwuzla not built**. 4 cores, 15 GB.
Every script here is run as `./run.sh <dir>/<script>.tcl` from this
directory (the wrapper passes `--engines config/engines.toml` and a
per-script `--workdir build/<name>`; `build/` was deleted afterwards and
is recreated by any run). Outputs kept are in `out/`. The two DMA
mutants are in `dma/mutants/`. Times are wall-clock on 4 cores and vary
by a few hundredths of a second between runs.

## 0. Summary (written last)

**Works, and well.** JasperGold/VC Formal style Tcl in a real Tcl 8.6;
a wide concurrent-SVA subset (sequences, ranges, repetition, `until`,
sampled-value functions, `default clocking`/`disable iff`); properties
by Tcl command, in the RTL, in an instantiated checker and through
`bind`; sub-instance signals; parameters; cut points; black boxes;
liveness with fairness (in-house engines only); cover reachable and
unreachable as an unbounded proof; BMC, k-induction (complete, simple
path) and IC3 selectable by name; VCD per counterexample; verdicts
certified. Small designs answer in 0.02 to 0.3 s. The repository's 49
known-answer designs all agree on this build, and sby agrees on the DMA.

**Book designs.** Chapter 1 FIFO: forward property proven (vacuous, not
flagged), backward property cex at depth 16 (reset + 15 pushes), cover
`occ == 16` unreachable by kind 0.26 s / IC3 0.08 s / rIC3 0.04 s. The
occupancy model must be RTL (a bound module); the properties can be Tcl
text naming `u_occ.occ`, or concurrent assertions in the bound module.
Fixed FIFO: `occ <= DEPTH` is proved by kind without a helper (0.5 s),
so the sby "induction fails" story does not reproduce on that property;
it does on `empty |-> wr_ptr == rd_ptr` (kind undetermined in 20 s;
helper `count == wr_ptr - rd_ptr` proved in 0.02 s; with it assumed
0.02 s; IC3 alone 1.75 s, rIC3 0.16 s). DMA v2 elaborates unchanged
(647 state bits, 9,665 ANDs); six AXI rules proved in 0.08 to 0.32 s
each, both Chapter 9 mutants refuted at depth 5; `dma_v1.v` is rejected
for its multi-driven `ctrl`/`status`, correctly.

**Does not work / decides the chapter.**
1. Clocked *immediate* assertions (Chapter 9's whole checker style) are
   dropped silently by the shell: empty table, exit 0.
2. RTL properties also vanish silently when the design has any
   unsupported construct (e.g. `$anyconst`).
3. Async reset is modelled as sync: the reset cycle holds free values
   and `$past(...)` antecedents fail spuriously at depth 1.
4. No BMC bound, no k, no induction-step trace; contradictory
   assumptions pass silently; exit status always 0; no equivalence
   checking; no word-level engine or arrays without Bitwuzla (memories
   of 4096 words and up: undetermined); ABC unusable from the shell.
5. Default portfolio output is not reproducible (engine, depth, VCD);
   one selected engine is, apart from the time column.
6. No tagged release; pre-release 0.1.0.

Sections: A FIFO, B DMA and book RTL, C techniques, D shell reference,
E against SymbiYosys, F bugs for the author, G practicalities.

## A. Book FIFO (task 3a, 3b): measured first because it decides the chapter

Scripts: `fifo/ch09_asis.tcl`, `fifo/buggy_rtl.tcl`, `fifo/buggy_tcl.tcl`,
`fifo/fixed.tcl`; full output in `out/fifo_*.out`.

### A.1 Chapter 9's checker as shipped gives an EMPTY property table

`fifo_sva.sv` writes every check as a clocked immediate assertion
(`always @(posedge clk) if (rst_n) begin NoOverflow_A: assert (...);`),
bound with `fifo_bind.sv`. `./run.sh fifo/ch09_asis.tcl`:

```
property                     type    status        engine     detail
prove returned: proven 0 cex 0 covered 0 unreachable 0 undetermined 0 error 0
exit=0
```

No note, no warning, exit 0. `informal shell` does not collect immediate
assertions at all (also `where/imm.tcl`: a false `a_false: assert (q != 9)`
in an `always_ff` and a true one in `always_comb` give `"props": []`).
Only `informal lower` turns labelled immediate assertions into Btor2 `bad`
lines, and that path has no clock/reset setup (see B.2). **Consequence:
the "one text for Verilator and formal" form of Chapter 9 (clocked
immediate assert) is exactly the form the InFormal shell drops; the
common text has to become `assert property (@(posedge clk) disable iff
(!rst_n) e)`.** Also a tool bug to report (silent drop contradicts D13
"rejected with a message, never guessed").

### A.2 Where the occupancy model can live

A Tcl property is one SVA property expression; it cannot declare state.
`occ` (5 bits; the buggy design's `count` has only 4) must be RTL. Two
arrangements both work, and `bind` works although `docs/fpv-shell.md`
says "No `bind` yet":

- `fifo/occ_model.sv`: a bound module with only the `occ` register;
  properties in Tcl name it by instance path: `assert -name
  FullForward_A {u_occ.occ == 5'd16 |-> full}`.
- `fifo/fifo_props.sv`: bound module with `occ` and concurrent
  `assert property` / `cover property`; listed as
  `fifo.u_props.NoOverflow_A` etc. The bind port expression
  `.count(5'(count))` is accepted.

### A.3 Chapter 1 FIFO (full-flag bug), default portfolio

`./run.sh fifo/buggy_rtl.tcl`:

```
fifo.u_props.NoOverflow_A    assert  proven        ric3       0.12 s
fifo.u_props.FullForward_A   assert  proven        ric3-ic3   0.07 s
fifo.u_props.FullBackward_A  assert  cex           informal-bmc depth 16 in 0.06 s
fifo.u_props.EmptyExact_A    assert  proven        informal-ic3 0.04 s
fifo.u_props.FullReached_C   cover   unreachable   ric3-ic3   0.06 s
```

- "occ == 16 implies full": **proven, vacuously**; nothing in the report
  says vacuous (no automatic precondition cover; `informal: elaborate:
  ignoring -create_related_covers (vendor engine/GUI option)`).
- "full implies occ == 16": **cex, depth 16** = 16 cycles: the reset
  cycle plus 15 pushes (sby reported "step 17" for the same trace).
- cover `occ == 16`: **unreachable**, an unbounded proof, by every
  proving engine alone (`fifo/buggy_tcl.tcl`, per-engine):
  informal-kind 0.26 s, informal-ic3 0.08 s, informal-kind-ic3 0.28 s,
  ric3-ic3 0.04 s. BMC alone: `undetermined   no engine reached a
  verdict` after the whole time limit.
- In the portfolio the cex depth is not always minimal: one run printed
  `FullBackward_A  assert  cex  informal-bmc-10 depth 19 in 0.07 s`
  (stepped BMC, 10 frames per call, won the race); single-engine runs
  all say depth 16. On the fixed FIFO `FullReached_C` was `depth 17`
  from every single engine and `depth 18` from informal-bmc-10 in the
  portfolio.

### A.4 Fixed FIFO, `occ <= DEPTH` (30 s limit, one engine at a time)

```
--- defs {} engines: {informal-bmc}
fifo.u_props.NoOverflow_A    assert  undetermined             no engine reached a verdict
--- defs {} engines: {informal-kind}
fifo.u_props.NoOverflow_A    assert  proven        informal-kind 0.50 s
fifo.u_props.FullForward_A   assert  proven        informal-kind 2.62 s
fifo.u_props.FullBackward_A  assert  proven        informal-kind 2.18 s
fifo.u_props.EmptyExact_A    assert  proven        informal-kind 3.39 s
--- defs {} engines: {informal-ic3}
fifo.u_props.NoOverflow_A    assert  proven        informal-ic3 0.10 s
--- defs {} engines: {ric3-ic3}
fifo.u_props.NoOverflow_A    assert  proven        ric3-ic3   0.06 s
--- defs {+define+HELPER} engines: {informal-kind}
fifo.u_props.NoOverflow_A    assert  proven        informal-kind 0.54 s
fifo.u_props.Sync_A          assert  proven        informal-kind 0.02 s
```

- **The sby story ("induction fails, no k fixes it, the helper does")
  does not reproduce.** `informal-kind` adds simple-path constraints, so
  it is complete on a finite design and proves `NoOverflow_A` without a
  helper in 0.5 s. It prints no k, has no option to set k or turn the
  simple-path constraints off, and never shows an induction-step
  counterexample. The shell cannot show "induction failed" at all; the
  only failure mode is `undetermined` at the time limit.
- A proven assertion is **not** used as a lemma for the others: with
  `Sync_A` present as an assertion, `NoOverflow_A` takes the same 0.54 s.
  To use a helper it must be an assumption (`assume`, `assert -env`),
  proved separately by hand (see C.3 for a design where that matters).
- IC3 without helper: informal-ic3 0.10 s, informal-ic3-mt 0.04 s,
  ric3-ic3 0.06 s. Agrees with sby `abc pdr`.

## B. Chapter 11 DMA version 2 (task 3c) and the book's other RTL

Scripts `dma/*.tcl`, `book-rtl/*.tcl`; outputs `out/dma*.out`, `out/book_rtl.out`.

### B.1 dma_v2 elaborates and all six AXI rules are proved; both mutants refuted

svlang takes `dma_v2.sv` + `dma_regs_pkg.sv` unchanged (package import in
the module header, unpacked arrays of registers `src [NCH]`, enum FSMs,
`$clog2` localparams, async reset). Model of one property
(`informal simp build/dma2/prop_0.btor2`):

```
loaded    inputs 421 latches 647 ands 9665 bads 1 constraints 1 (3.3 ms)
simplified inputs 94 latches 127 ands 2668 bads 1 constraints 1 (0.5 ms, 0 constant latches)
```

`./run.sh dma/dma2.tcl` (checker `dma/axi_props2.sv`, concurrent
assertions, bound with the book's bind text; whole run 1.8 s wall):

```
dma_v2.u_axi.ArHeld_A        assert  proven        informal-ic3-cadical 0.14 s
dma_v2.u_axi.ArStable_A      assert  proven        ric3       0.32 s
dma_v2.u_axi.AwHeld_A        assert  proven        informal-ic3 0.08 s
dma_v2.u_axi.AwStable_A      assert  proven        ric3-ic3   0.28 s
dma_v2.u_axi.WHeld_A         assert  proven        informal-ic3 0.09 s
dma_v2.u_axi.WStable_A       assert  proven        informal-ic3 0.12 s
dma_v2.u_axi.ArHeld_reg_A    assert  proven        informal-kind-ic3 0.10 s
dma_v2.u_axi.ArStable_reg_A  assert  proven        ric3-ic3   0.29 s
dma_v2.u_axi.ArWait_C        cover   covered       informal-bmc depth 5 in 0.06 s
dma_v2.u_axi.AwWait_C        cover   covered       informal-bmc depth 8 in 0.09 s
dma_v2.u_axi.WWait_C         cover   covered       ric3-bmc   depth 8 in 0.15 s
```

Chapter 9's two mutants (`dma/mutants.tcl`, same sed as `run_axi.sh`):

```
=== mutant drop
dma_v2.u_axi.ArHeld_A        assert  cex           ric3-bmc   depth 5 in 0.08 s
dma_v2.u_axi.ArHeld_reg_A    assert  cex           informal-bmc depth 5 in 0.09 s
=== mutant wander
dma_v2.u_axi.ArStable_A      assert  cex           informal-bmc depth 5 in 0.32 s
dma_v2.u_axi.ArStable_reg_A  assert  cex           informal-bmc depth 5 in 0.12 s
```

(all other rules stay proven in both). No AXI slave or APB master
assumptions were needed: inputs are free and the rules still hold.

### B.2 Two traps met on the way (both are tool findings)

1. **Chapter 9's `axil_master_sva.sv` as shipped: empty table** (same
   reason as A.1). `./run.sh dma/dma_asis.tcl` prints `prove returned:
   proven 0 cex 0 covered 0 unreachable 0 undetermined 0 error 0`.
2. **`$past` in an antecedent looks into the reset cycle, where
   registers are arbitrary, even with an asynchronous reset.** The
   natural spelling `$past(arvalid && !arready) |-> arvalid` under
   `default disable iff (!rst_n)` (`dma/axi_props.sv`) fails for all six
   rules:
   `dma_v2.u_axi.ArHeld_A  assert  cex  informal-ic3-cadical depth 1 in 0.06 s`.
   The VCD has `PRESETn=0, ARVALID=1` at #0 and `PRESETn=1, ARVALID=0`
   at #10: in cycle 0 reset is asserted but the flops still hold free
   values (reset is modelled as a synchronous load that shows one step
   later), and cycle 1's `$past` reads them. In hardware an
   `always_ff @(posedge clk or negedge rst_n)` register is at its reset
   value while `rst_n` is low, so this counterexample is spurious.
   `docs/fpv-shell.md` documents the rule ("with a reset the reset cycle
   counts, so checks start right after it") but not this consequence.
   Spellings that are proved: `a |=> b` / `a |=> $stable(x)`, or the
   book's own waiting register (`ar_w`, reset with the design) as the
   antecedent. Same effect on a plain counter: `$fell(done) |-> 1'b0`
   and `$changed(q) |-> $past(en)` fail at the first cycle after reset
   (`forms/forms.tcl` p5, p6).

### B.3 Every book design tried (`book-rtl/`, `informal lower`)

| design | result |
| --- | --- |
| ch01 `fifo.sv`, ch09 `fifo_fixed.sv` | lowered; `mem [DEPTH]` (16x8) becomes registers |
| ch11 `dma_v2.sv` + pkg | lowered |
| ch11 `dma_v1.v` (top `dma_engine`) | **rejected**: `svlang: .../dma_v1.v:184: overlapping drivers on 'dma_engine.ctrl[31:0]': driven by clocked procedural block and clocked procedural block (first driven at ...:127:17)`; same for `status[31:0]` (line 189). This is the multi-driver finding Chapter 11 already reports, so the rejection is right; every property gets status `error` |
| ch03 `top.sv` (two clock domains) | shell: accepted with `clock bclk` + `clock cclk -factor 3` (`informal: svlang: the design has 2 clocks: one model step is 1/2 of the fastest clock's cycle`); `informal lower`: `Error: not modelled: more than one clock (top.u_regs.en, top.u_sync_en.q)` (the names printed are not the clocks) |
| appF `counter.sv`, ch04 `safe.sv`/`racy.sv`/`dut_unreset.sv`, ch09 `responder.sv` (both), `ack_check.sv`, `resp_check.sv`, `hs_check.sv` | lowered without error |
| ch09 `fifo_sva.sv`, `axil_master_sva.sv` | lowered, but in the shell all their (immediate) assertions and covers are dropped silently |

Constructs in the book's property text that the shell does not take:
clocked immediate `assert`/`cover` (dropped, no message), immediate
covers under `informal lower` (`note: 4 cover(s) in the RTL are not
written`). Nothing else in the book's RTL was refused.

## C. Techniques (task 2)

All on designs in `tech/`; outputs in `out/tech_*.out`. Times are this
machine's (4 cores); "limit" is `set_prove_time_limit`.

### C.1 Bounded model checking

`informal::set_engines informal-bmc` (shortest counterexample first).
`tech/induction.tcl`, 32-bit wrapping counter:

```
a_never20                    assert  cex           informal-bmc depth 21 in 0.04 s
a_small                      assert  undetermined             no engine reached a verdict
```

- There is **no bound**: no `-bound`/depth option anywhere (`assert
  -bound` is `-bound is not supported yet`); BMC runs until the time
  limit, and a true property ends `undetermined` with no depth reached
  in the report. "Proved to depth N" cannot be stated from the shell.
  (The hidden `informal engine informal-kind <model>` child prints
  `{"progress":{"bound":47,"note":""}}` lines; the shell does not.)
- `depth N` is the index of the failing cycle counting the reset cycle
  as 0; the VCD has N+1 cycles. sby's "step" for the same trace is N+1.
- `informal-bmc-10`/`-65` (stepped) report non-minimal depths (A.3).

### C.2 k-induction succeeding

`informal-kind`: `a_small  assert  proven  informal-kind 0.02 s`
(`cnt < 1000000`, 1-inductive). No k is printed.

### C.3 k-induction failing on a true property, the helper, and IC3

Best demonstration found is on the book's own fixed FIFO
(`tech/fifo_ptr.tcl`, DEPTH=16, WIDTH=1, limit 20 s): "empty implies
wr_ptr == rd_ptr" is true but inductive only with
`count == wr_ptr - rd_ptr`.

```
=== DEPTH=16 engine informal-kind
a_empty_ptrs                 assert  undetermined             no engine reached a verdict
h_count                      assert  proven        informal-kind 0.02 s
=== DEPTH=16 engine informal-ic3
a_empty_ptrs                 assert  proven        informal-ic3 1.75 s
h_count                      assert  proven        informal-ic3 0.73 s
=== DEPTH=16 engine ric3-ic3
a_empty_ptrs                 assert  proven        ric3-ic3   0.16 s
h_count                      assert  proven        ric3-ic3   0.10 s
=== DEPTH=16 informal-kind with the helper assumed
a_empty_ptrs                 assert  proven        informal-kind 0.02 s
h_count                      assert  disabled      ric3-ic3   0.10 s
m_count                      assume  unprocessed
```

So all four steps exist: kind fails (as a timeout, not as a shown
induction counterexample), helper is proved alone by kind, helper
assumed makes kind succeed in 0.02 s, IC3 needs no helper. The
assume-guarantee step is by hand (`assert -disable h_count; assume
-name m_count {...}`); a proven assert is never reused automatically.
Scaling the same script is a lesson in itself:

| DEPTH | kind, no helper | informal-ic3 | ric3-ic3 | kind + helper |
| --- | --- | --- | --- | --- |
| 16 | undetermined (20 s) | 1.75 s | 0.16 s | 0.02 s |
| 64 | undetermined | undetermined | 1.89 s | 0.02 s |
| 256 | undetermined | undetermined | undetermined | 0.02 s |

(informal-ic3 also fails the 1-inductive `h_count` at DEPTH 64 and 256
in 20 s; kind proves it in 0.04/0.06 s.)

Second design, `tech/wrap.sv` (counter wraps at LIMIT, property
`cnt != BAD`, unreachable states walk into BAD), `tech/induction*.tcl`:
kind `undetermined` at 20 s for every size; with `assume {cnt <
32'd1000000}` `proven informal-kind 0.02 s`. IC3 without helper is weak
on it: LIMIT=1000/BAD=1400 `proven informal-ic3 17.34 s`, `proven
ric3-ic3 0.10 s`; LIMIT=1000/BAD=5000 only `ric3-ic3 0.81 s`;
LIMIT=10^6 or 2^20: no engine in 20 s (informal-ic3, -cadical, -mt,
kind-ic3, ric3-ic3, ric3 all `undetermined`).

### C.4 Cover: reachable and unreachable

Counter (`ex-counter/`): `c_done cover covered informal-bmc-10 depth 10`,
`c_10 cover unreachable informal-ic3 0.04 s`. A cover is checked as an
assertion of its negation, so `unreachable` is an unbounded proof and
needs a proving engine; BMC alone gives `undetermined`.

### C.5 Assumptions and over-constraint (`tech/assume.tcl`)

```
--- no assumptions
a_false                      assert  cex           ric3-ic3   depth 202 in 0.32 s
c_gnt                        cover   covered       ric3-ic3   depth 202 in 0.28 s
--- partial over-constraint: assume {!req}
a_false                      assert  proven        informal-ic3-cadical 0.04 s
c_gnt                        cover   unreachable   informal-ic3-cadical 0.02 s
c_busy                       cover   unreachable   informal-kind 0.02 s
m_noreq                      assume  unprocessed
--- contradiction: assume {d < 4'd8} and {d > 4'd9}
a_gnt_after_busy             assert  proven        informal-ic3 0.05 s
a_false                      assert  proven        informal-ic3 0.04 s
c_gnt                        cover   unreachable   informal-ic3-cadical 0.04 s
c_busy                       cover   unreachable   informal-ic3 0.04 s
```

- **Contradictory assumptions are a silent vacuous pass**: a false
  assertion is `proven`. There is no satisfiability check of the
  assumptions (sby: `Assumptions are unsatisfiable!` / `PREUNSAT` /
  ERROR). Only the covers going `unreachable` reveal it, for total and
  for partial over-constraint alike. Assumptions are never checked or
  reported (`assume unprocessed`), and an assumption added after an
  assertion still constrains it (all assumptions apply to every
  property of the session).
- `assume -remove name ...` works; `assert -disable/-enable` works.

### C.6 Cut points and black boxes (`tech/cuts.tcl`)

```
--- stopat u_timer.expired
informal: 1 cut point(s) (stopat) are free in this model: u_timer.expired. A proof holds for the design; a counterexample may use values the design cannot produce there
a_hold_q                     assert  proven        informal-kind 0.04 s
a_gnt_once                   assert  proven        informal-kind-ic3 0.04 s
a_no_early                   assert  cex           informal-ic3-cadical depth 3 in 0.04 s
c_gnt                        cover   covered       informal-bmc-65 depth 64 in 0.04 s
--- black box: elaborate -bbox_m {timer}
informal: black boxes in this model (outputs free, contents not modelled): timer. A proof holds for the design; a counterexample may use output values the boxed logic cannot produce
a_no_early                   assert  cex           informal-kind depth 3 in 0.04 s
c_gnt                        cover   covered       informal-bmc depth 3 in 0.04 s
```

Both work as documented (proofs that survive the abstraction, a
spurious counterexample that does not, a cover that gets shallower:
202 -> 3). `stopat -list`, `stopat -clear`, cutting a register
(`u_timer.t`) and `-bbox_i` (repo test) work. Naming a signal inside a
black box is accepted by `assert` and only fails later.

### C.7 Liveness (`tech/live_small.tcl`, `tech/live.tcl`, `tech/live_alone.tcl`)

Present and working for the in-house engines, although README says
"Not there yet: liveness". `s_eventually`, `s_until`, `s_until_with`
and fairness (`assume {s_eventually e}`):

```
a_live                       assert  cex           informal-bmc depth 5 in 0.04 s
a_idle                       assert  cex           informal-bmc depth 3 in 0.02 s
a_step                       assert  proven        informal-ic3 0.06 s
a_until                      assert  cex           informal-bmc depth 5 in 0.04 s
a_wuntil                     assert  proven        informal-ic3 0.02 s
--- fairness: assume {s_eventually !stall}
a_live                       assert  proven        informal-ic3 0.09 s
a_until                      assert  proven        informal-ic3 0.07 s
```

The trace's first line names the loop: `$comment liveness: frame 5 has
the state of frame 4 again; the frames from 4 on repeat for ever $end`.
Limits measured:

- ric3 is not run on them: `informal::set_engines ric3-ic3` gives
  `undetermined` at once for every liveness property.
- Slow beyond toys. `a_step` (a 2-bit FSM): `proven informal-kind
  10.34 s` against `informal-ic3 0.02 s`. With the 200-cycle timer
  (`handshake.sv`) `req && !busy |-> s_eventually gnt` is true and
  `undetermined` after 40 s and 60 s with every engine; the bounded
  form `|-> ##[1:201] gnt` is `proven informal-kind 0.72 s` (and
  `undetermined` for informal-ic3 and ric3-ic3 in 60 s), `##[1:200]`
  is `cex informal-bmc depth 201 in 0.06 s`.
- **Another property in the session changes a liveness counterexample**
  (bug, section F).

### C.8 Equivalence checking

None. No `sec`/equivalence command in the shell or CLI. A hand-built
miter (two instances, `assert {y1 == y2}`) is the only way.

### C.9 The other subcommands, one line each (run in `build/tools`)

- `informal lower f.sv [--top T]`: prints the Btor2 of the design with
  labelled immediate assertions as `bad` lines; no clock/reset setup, so
  registers start free unless an `initial` gives them a value (a false
  assertion on the counter is `UNSAFE ... depth 0` without `initial q =
  0`, depth 9 with it); immediate covers are dropped with a note.
- `informal check m.btor2|.aag|.aig [--only e1,e2] [--timeout s]`: runs
  the portfolio on one model; prints one line per engine, `SAFE`/`UNSAFE
  (by E, depth N)` and a text witness (`@3 imm.rst=0 imm.en=1`); exit 20
  safe, 10 unsafe, 0 unknown. Does not say which `bad` failed.
- `informal simp m`: size before/after preprocessing, e.g. `loaded
  inputs 28 latches 148 ands 1048 ...` / `simplified inputs 3 latches 12
  ands 116` for the FIFO's `NoOverflow_A`; `--aag` prints ASCII AIGER.
- `informal split m.aag`: proves an OR-of-terms bad output term by term
  (`split: round 1 (10 s per term): 3 of 3 terms proved` / `SAFE (by
  informal-ic3, 3 terms)`); on a shell-made model: `Error: the bad
  output of fifo_p0.aag is not an OR of several terms; nothing to
  split`. Takes no `--engines`. A research tool, not a user feature.
- `informal reduce m.aag --test CMD -o small.aag` (or `--disagree A,B`):
  delta-debugs an AIGER model (`reduced: 1 inputs, 0 latches, 0 ANDs
  after 2 tests`). For reporting engine bugs.
- `informal bench DIR --each --only ...`: every engine on every model,
  a table with solved counts and PAR-2, appended to `bench/runs.jsonl`.
- `informal info m.btor2` (JSON of sizes and operators), `informal fmt`.

## D. What the shell accepts (task 1)

### D.1 Property forms (`forms/forms.tcl`, 55 forms on `forms/probe.sv`)

Accepted and given a verdict: boolean; `|->`, `|=>`; `$past(x)`,
`$past(x,2)`, `$rose`, `$fell`, `$stable`, `$changed`; `@(posedge clk)`,
`@(negedge clk)`, `disable iff`; `##N`, `##[M:N]`, `##0`; `[*N]`,
`[*M:N]`; sequence `and`, `or`, `intersect`, `within`, `throughout`,
`first_match`; `until`, `until_with`, `s_until`; `s_eventually`,
`s_eventually [1:3]`; `nexttime`, `nexttime [2]`; `always [0:2]`;
`strong(...)`; `$onehot0`, `$countones`, `$bits`, `inside`; parameter
names (`q <= LIM`); sub-instance signals by path from the top
(`u_leaf.hid`).

Rejected at the command (exact messages):

```
REJECT p30 assert {a [->2] |-> b}: `[->` is not supported yet in a property
REJECT p31 assert {a [=2] |-> b}: `[=` is not supported yet in a property
REJECT p32 assert {not (a ##1 b)}: `not` is not supported yet in a property
REJECT p33 assert {accept_on (b) a |=> y}: `accept_on` is not supported yet in a property
REJECT p34 assert {a #-# b}: `#-#` is not supported yet in a property
REJECT p35 assert {a #=# b}: `#=#` is not supported yet in a property
REJECT p38 assert {a implies b}: unknown name(s) in module probe: implies
REJECT p44 assert {probe.u_leaf.hid == y}: unknown name(s) in module probe: probe
REJECT p45 assert {nosuch == 1'b0}: unknown name(s) in module probe: nosuch
```

Accepted by the command, status `error` at `prove`:

```
p29  assert  error   not supported yet: the delay range [1:$]
p36  assert  error   not supported yet: `always` with no upper bound
p37  assert  error   not supported yet: property `iff`
p39  assert  error   not supported yet: property `if`
p42  assert  error   not supported yet: $isunknown requires allow_four_state_ops
```

Not tried: local variables, named sequences/properties with arguments,
`let`, `checker`, `restrict`, `expect`, recursive properties.

One `@(negedge clk)` property puts the **whole session** on the
half-cycle model (`informal: svlang: the design uses both edges of its
clock: one model step is half a clock cycle`): the depth of every other
property doubles (cover `q == 9`: depth 20 instead of 10).

### D.2 Where properties may live (`where/*.tcl`)

| place | result |
| --- | --- |
| Tcl `assert/assume/cover -name N {expr}` | yes |
| concurrent `assert/assume/cover property` in the RTL, labelled or not | yes: `top.u_cnt.a_rtl`, unlabelled `top._assert_1` |
| the same in a checker module instantiated beside the DUT | yes: `top.u_chk.a_bound` |
| the same in a module attached with `bind` | **yes**: `top.u_cnt.u_bound.a_bound` (docs say no) |
| action block `else $error(...)` on a concurrent assertion | accepted, ignored |
| `default clocking`, `default disable iff` | honoured |
| concurrent assertion under `if`/`case` in a clocked block | yes (repo test `rtl_procedural`) |
| immediate `assert`/`cover` (clocked block or `always_comb`) | **shell: dropped silently**; `informal lower` + `informal check`: asserts only, no reset |

`elaborate -top cnt -parameter LIM 5` overrides a parameter (`t_five
proven`, `c_six unreachable`). `elaborate -top <name that does not
exist>` succeeds; the error comes at the next command naming a signal.

### D.3 Clock and reset (`shell/rst.tcl`, `shell/async.tcl`)

- `clock clk` is required (`error ... no clock: declare one with
  `clock` / `create_clock``; the message names the first property on
  every row). A wrong clock or reset name is an error at the command.
- `reset -expression {!rst_n}`: the expression holds in cycle 0 and is
  false for ever after (`cover {rst_n ##1 !rst_n}`: `unreachable`).
  Registers are **free in cycle 0** and take their reset value in
  cycle 1; a register with no reset stays free (`a_nr_zero cex depth
  1`); `initial iv = 4'd5` gives a start value (`a_iv proven`).
- Without `reset` (or `reset -none`) the reset pin is a free input and
  the state starts free.
- Asynchronous resets are modelled as synchronous: with `rst_n` free,
  `$past(rst_n) && !rst_n |-> a == 4'd0` is `cex informal-kind depth 1`
  on an `always_ff @(posedge clk or negedge rst_n)` register, while
  `$past(!rst_n) |-> a == 4'd0` is proven. See B.2 for where this bites.
- Two clocks: `clock bclk`, `clock cclk -factor 3` accepted on ch03's
  `top.sv`.

### D.4 Report, exit status, counterexamples

- Report: the table printed by `prove`/`report` on stdout, columns
  `property type status engine detail`; engine names longer than 10
  characters push the detail column. Notes go to stderr with an
  `informal:` prefix. `prove` returns a Tcl dict (`proven 1 cex 1
  covered 0 unreachable 0 undetermined 0 error 0`); `get_status name`,
  `get_property_list -include {status cex}`, `informal::session` (JSON
  with per-property status, depth, ms, trace path, source line).
- **Exit status is 0 whatever the verdicts** (cex, error rows,
  undetermined, empty table); 1 on a Tcl error (unknown name, SV syntax
  error, missing file). A Makefile must grep, or the script must end
  with e.g. `if {[dict get $r cex] > 0} {exit 3}` (Tcl `exit N` is
  honoured: measured exit=3).
- Counterexample / cover trace: `<workdir>/<property>.vcd` (plus
  `prop_N.btor2` and `prop_N.trace.btor2`). No text trace is printed by
  the shell and no viewer is bundled; the desktop app and Surfer are the
  intended viewers. The VCD has every design signal, the instances
  below, and an `informal` scope with the property's monitor state.
  Three rough edges in it (section F): `clk` is declared twice, the
  design scope appears twice, cycle 0 shows pre-reset garbage. The
  book's `vcd2wave.py` dies on it (`IndexError` in `period = rises[1] -
  rises[0]`: it resolves `fifo.clk` to the second, constant `clk`).
- SV errors carry file:line:col (`syntax.sv:2:33: error: expected an
  expression, found `;``).

### D.5 Engines, time limits, determinism

- `informal::set_engines name ...` picks engines; with none given all
  run as a race. Names available here: `informal-bmc`, `informal-bmc-10`,
  `informal-bmc-65`, `informal-kind`, `informal-ic3`,
  `informal-ic3-cadical`, `informal-kind-ic3`, `informal-ic3-mt`,
  `ric3-ic3`, `ric3-bmc`, `ric3` (and config entries for tools not
  installed: `pono-*`, `btormc`). `informal-wbmc` is `unknown engine`
  (no Bitwuzla).
- **ABC never runs from the shell.** `informal::set_engines abc-pdr`
  (also `abc-bmc3`, `abc-pdr-pp`): `informal: none of the selected
  engines (abc-pdr) reads Btor2; using all engines`, and the whole
  portfolio runs instead. From `informal check` ABC reads binary `.aig`
  only; on the `.aag` that `informal simp --aag` writes all three ABC
  entries are `unknown`. Installing ABC buys the shell nothing.
- `set_engine_mode {Ht}` and `{B}` are accepted; `{Ht}` proved with
  informal-kind-ic3, `{B}` left the true properties undetermined (BMC
  only).
- `set_prove_time_limit 5s|2m|1h|0.5s|5` (per property; `500ms` is `bad
  time unit`). Default 3600 s, so a BMC-only script on a true property
  hangs for an hour per property unless a limit is set.
- **Determinism** (`shell/determ.tcl`, 6 runs each): with one engine
  selected the report minus the time column and the VCD bytes are
  identical in 6 of 6 runs for `informal-bmc`, `informal-kind` and
  `informal-ic3` (and the VCD is the same file across the three). With
  the default portfolio 6 runs gave 6 different reports (engine column,
  and for covers/cex the depth) and 4 different VCDs. The time column
  always varies (0.02/0.04/0.06 s). For a spliced `run.out`: select one
  engine per `prove` and filter the times.

### D.6 Without Bitwuzla

No `informal-wbmc`: no word-level BMC and no array theory. Memories are
bit-blasted into registers (`shell/bigmem.tcl`, 30 s limit): 256x8
`a_rw proven informal-kind 23.52 s`, and the depth-2 bug `cex ric3-bmc
depth 2 in 4.00 s`; 4096x8, 8192x8 and 65536x8: `undetermined` for both,
even the depth-2 counterexample, and the 65536-word run got a process
OOM-killed on this 15 GB machine. The book's 16-entry FIFO is fine
(`a_first_word proven ric3 2.90 s`, `fifo/data.tcl`).

## E. Against SymbiYosys (task 4; sby numbers from Chapter 9's FINDINGS 2 and 3.5)

Better in InFormal:

- Concurrent SVA is real: sequences, ranges, repetition, `until`,
  `throughout`, `$rose/$fell/$stable/$changed`, `default clocking`,
  `default disable iff` (read_slang ignores it silently), named in the
  report by hierarchy. sby open-source takes only clocked booleans.
- `bind` and hierarchical names both work in one front end (sby: native
  drops `bind` and turns `dut.count` into a free wire; only read_slang
  works).
- Liveness with fairness runs out of the box (sby `mode live` needs
  `suprove`, not installed).
- One run does assert, cover and prove per property with a portfolio;
  no mode/depth/engine file per task. Unreachable cover is a proof in
  0.04-0.3 s (sby `mode cover`: bounded, 3 s at depth 20, >5 min at 40).
- Reset by command instead of a hand-written `init` register; cut
  points and black boxes by command; parameters by command.
- k-induction is complete (simple path): the vacuous `FullForward_A`
  that sby's `smtbmc` could not prove by induction is `proven
  informal-kind 0.28 s`; `NoOverflow_A` needs no helper.
- Proofs are certificate-checked and counterexamples replayed before
  being reported; engines that disagree are reported as a conflict.
- Verdict cross-check on dma_v2 with the book's own immediate-assert
  checker under sby `abc pdr`: `DONE (PASS, rc=0)`; drop: `Assert failed
  in dma_v2: u_axi_sva.ArHeld_A ... step 6`; wander: `...ArStable_A ...
  step 6` (`sby/*.sby`, `out/sby_*.out`). Same verdicts as B.1 (InFormal
  depth 5 = sby step 6).

Lacking or worse:

- **Immediate assertions** (the only form common to Verilator, Icarus
  and both Yosys front ends) are dropped silently.
- No bound/depth control, no "bounded proof to depth N" result, no k,
  no induction-step counterexample: the classic BMC and induction
  lessons cannot be shown as such (sby prints `Temporal induction
  failed!` and writes `trace_induct.vcd`).
- No satisfiability check of assumptions (sby: PREUNSAT).
- Exit status always 0; sby's rc distinguishes PASS/FAIL/UNKNOWN/ERROR.
- No word-level engine here, no arrays; no SMT solver choice.
- `$anyconst` is `not supported yet: ... formal intrinsic '$anyconst'
  requires consumer harness or free input` (a free input of a wrapper,
  held stable by an assumption, or `stopat`, stands in).
- Async reset modelled as sync; `$past` reads the free reset cycle.
- Pre-release: no tag, no packages, API may change.
- Equivalence checking: neither tool has a command (Yosys has `equiv_*`
  passes outside sby).

## F. Bugs and rough edges, for the tool's author (task 6)

No wrong verdict against a second engine was found: all 49 designs of
the repository's `tests/sv` give their recorded answers on this build
(`known/run_known.py`: `49 agree, 0 differ`), sby agrees on the DMA,
and single engines agree with each other everywhere they finished. The
items below are ordered by how much they can mislead.

1. **Immediate assertions and covers are dropped by `informal shell`
   with no message** (A.1, B.2, `where/imm.tcl`). An all-immediate
   checker gives an empty table and exit 0. Either collect them (as
   `lower` does) or print a note with the count.
1b. **RTL properties vanish when the design has an unsupported
   construct.** `shell/misc.sv` has `assign k = $anyconst;` and one
   labelled `assert property`; `prove -all` prints an empty table,
   `proven 0 cex 0 ... error 0`, exit 0. Only after adding a property by
   command does the reason show, on that property: `t assert error
   svlang: not supported yet: .../misc.sv:3: formal intrinsic
   '$anyconst' requires consumer harness or free input`. With the
   `$anyconst` removed the same file lists `misc.a_k`. So a file whose
   properties are all in the RTL can "pass" with nothing checked.
   (`$anyconst` itself: not supported.)
2. **Async reset is modelled as synchronous, so the reset cycle shows
   free register values** and `$past`/`$fell`/`$changed` read them in
   the first checked cycle: spurious counterexamples at depth 1 for
   `$past(valid && !ready) |-> valid` on dma_v2 (B.2), and
   `$past(rst_n) && !rst_n |-> a == 0` fails (D.3). Either apply an
   `always_ff @(... or negedge rst_n)` reset in the same step, or start
   sampled-value history after the reset cycle.
3. **Contradictory assumptions pass everything silently** (C.5). A
   one-line "assumptions are unsatisfiable" check per session would do.
4. **A liveness counterexample depends on unrelated properties in the
   session.** `tech/live_small.tcl`: `a_idle cex informal-bmc depth 3
   in 0.02 s`; after only *adding* `assert -name a_wide {... ##[1:300]
   ...}` (not proved in that run): `a_idle cex informal-bmc depth 302
   in 1.86 s`, trace comment `frame 302 has the state of frame 301
   again`. Same on `handshake.sv`: `s_eventually gnt` is depth 4 alone
   (`tech/live_alone.tcl`) and depth 203 next to a `##[1:201]`
   property. The shared `_sva_tick` counter (8 or 9 bits here) is part
   of the state the loop must repeat.
5. **Portfolio results are not minimal or repeatable**: stepped BMC
   wins races and reports depth 19 for a depth-16 bug, 18 for 17, 64
   for 3, 209 for 201 (A.3, C.6, C.7). Engine name, depth and VCD
   differ from run to run (D.5).
6. **ABC cannot be used from the shell** and selecting it silently
   (stderr note) falls back to *all* engines (D.5).
7. `informal shell --check` on a script with `informal::set_engines
   informal-kind`: `error: set_engines: unknown engine(s)
   informal-kind; available: ` (empty list; false alarm, exit 1).
8. Exit status 0 with cex/error/undetermined rows (D.4).
9. `config/engines.toml` is read from the current directory: the
   installed binary run anywhere else dies with `Error: reading
   config/engines.toml ... No such file or directory` and a Rust
   backtrace. Needs a built-in default or a search path. Every CLI
   error prints a backtrace.
10. VCD: `$var wire 1 ! clk` and `$var reg 1 " clk` in one scope (the
    second stays 0); sub-instances are in a second top-level `$scope
    module <top>` after the `informal` scope instead of nested in the
    first.
11. `elaborate -top nosuch` succeeds (D.2). `assert` on a signal inside
    a black box is accepted (C.6).
12. `a implies b` is reported as `unknown name(s) in module probe:
    implies`; a path that starts with the top module's name
    (`probe.u_leaf.hid`) is `unknown name(s) ...: probe`, although the
    report itself prints names that way.
13. A disabled property keeps its old engine and time in the table
    (`h_count assert disabled ric3-ic3 0.10 s`). With `prove -property
    X` the table still lists every property with stale results.
14. The "no clock" error names the first property on every row.
15. `informal lower` on two clocks prints `more than one clock
    (top.u_regs.en, top.u_sync_en.q)`: those are not the clocks.
16. `informal split` has no `--engines`; `informal check` on a model
    with several `bad` lines does not say which one failed.
17. Engine weaknesses worth a benchmark: informal-ic3 cannot prove a
    1-inductive property (`count[5:0] == wr_ptr - rd_ptr`, DEPTH=64) in
    20 s that kind proves in 0.04 s; informal-kind takes 10.34 s on a
    liveness property of a 2-bit FSM; no engine proves `cnt != 3145728`
    on a counter wrapping at 2^20; a depth-2 counterexample through a
    4096x8 memory is not found in 30 s.
18. Docs out of date: fpv-shell.md "No `bind` yet" (works); README "Not
    there yet: liveness" (works); README "Tested on Ubuntu 26.04" (this
    build is 24.04.5).

## G. Practicalities (task 5)

- Build as done here on Ubuntu 24.04.5 (the session's own
  build script `binf.sh` and its log, in the scratchpad `build/` directory, not copied here): `apt-get install tcl8.6-dev` (plus build-essential, git;
  meson/gmp/mpfr only for Bitwuzla), CaDiCaL `c607304` (`./configure
  -fPIC && make`), ABC `77875a3b6` (`make ABC_USE_NO_READLINE=1 abc`),
  rIC3 `4d63899` (`git submodule update --init --recursive; cargo build
  --release`), then `cargo build --release` in informal with
  `INFORMAL_TOOLS_DIR` pointing at the directory holding `cadical/`.
  InFormal itself: `Finished `release` profile [optimized] target(s) in
  1m 11s` on 4 cores; the whole script, three dependencies included,
  ran 06:46:28 to 06:55:48, about 9.5 minutes (ABC is most of it).
- Rust: `rust-toolchain.toml` pins `1.99.1` (rustup fetches it); svlang
  is a Cargo git dependency at rev `ef5c09e` (needs network at build).
- No tagged release (`git tag` is empty; version 0.1.0; README:
  "pre-release ... no binary releases yet ... Do not rely on it for
  sign-off"). The book must pin commit `5114330`.
- Binaries: `informal` 9,566,520 bytes, dynamically linked to
  `libtcl8.6.so`, libstdc++, libz (so `tcl8.6` is a run-time package
  too); `ric3` 8.6 MB; `abc` 209 MB unstripped.
- Runs without the external engines: with only `informal` on PATH the
  counter example gives the same verdicts and exit 0; missing engines
  are skipped silently in the shell (`informal check` prints `error:
  pono-ic3ia: starting 'pono' ...` lines for each missing one). ABC adds
  nothing to the shell; rIC3 is worth having (it was the only prover on
  several rows above), CaDiCaL is mandatory (without it "every property
  comes back undetermined", README).
- `--engines <path>` is needed unless the cwd has `config/engines.toml`;
  `--workdir` defaults to `./informal_work`.
- Nondeterministic: engine column, time column, cex/cover depth and VCD
  under the portfolio (D.5). Deterministic with one engine selected,
  apart from times.
- Memory: the 65536x8 memory probe had a process killed by the kernel
  on 15 GB; keep `--mem-gb` in mind for CI.

## H. Symbolic constant and one tracked word (added after the first run)

`tech/sym_fifo.sv`, `tech/sym_fifo.tcl`: a wrapper adds a free input
`sd` held constant by `assume {$stable(sd)}` (the stand-in for
`$anyconst`), and ghost logic that tracks one nondeterministically
picked push of that value and counts the words ahead of it. Property:
`in_q && ahead == 0 |-> rd_data == sd` on the fixed FIFO (16x8), 60 s
limit: `informal-kind` undetermined, `informal-ic3` undetermined,
`ric3-ic3` proven in 32.06 s; cover of the tracked word leaving with
nine words in the FIFO covered at depth 10. Mutant (read pointer steps
by 2, `tech/sym_fifo_mut.tcl`): see the output line below.
a_integrity                  assert  cex           informal-bmc depth 3 in 0.02 s
