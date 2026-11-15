# Chapter 9 support matrix: findings for the author

Not for the book. Everything here was measured in this container on
2026-11-15; the tables themselves are in `matrix.md`, the per-row log in
`run.out`. "Note" is `research/ch09-temporal-properties.md`.

## 0. Environment, and what the runner assumes

- Verilator 5.052, Icarus 13.0, Yosys 0.68 with `read_slang` built in
  (`yosys -h read_slang` prints its help), z3 from the pip wheel.
  **`sby --version` prints v0.70, not 0.68** as the note assumes.
  Verilator 5.054 appeared at `/opt/verilator-5.054/bin` during the work
  and is the extra column on the rows marked `v54` in `probes*.txt`.
- `sby` is `#!/usr/bin/env python3` and imports `click`; the venv's
  python has none, so with `/opt/dvtools/venv/bin` early in `PATH` it
  dies with `ModuleNotFoundError: No module named 'click'`. Everything
  here ran with `PATH=/opt/dvtools/bin:$PATH:/opt/dvtools/venv/bin`
  (venv last: the system python runs `sby`, `z3` is still found).
- No `suprove` is installed, so `mode live` cannot run (p40).
- Runner: `matrix.py`, modelled on Chapter 8's, plus a thread pool (one
  probe per core) because every Verilator build costs about 8 s.
  Verilator flags are Chapter 8's with `--assert` in place of
  `--coverage`; the cover rows add `--coverage` (see 3.6). Formal runs
  are `mode bmc`, `depth 12`, `smtbmc z3` unless the row's options say
  otherwise.
- Probe design. Each probe has a `dut` with a free-running 4-bit step
  counter `t` as its stimulus and a parameter `BAD` that makes the
  design violate the assertion at a known tick. Simulation instantiates
  `dut #(0) good` and `dut #(1) bad`, counts failures in action blocks,
  and prints `PROBE pNN PASS|FAIL detail`. Formal makes `dut` the top
  and runs sby twice, expecting PASS for `BAD=0` and FAIL for `BAD=1`,
  so an assertion that a front end drops shows as PASS/PASS.
- Two things the probes had to work around, both findings in themselves:
  1. The native front end rejects any action block (`syntax error,
     unexpected TOK_ELSE` / `TOK_ID`), so probes that it could otherwise
     read hide `else nf++` behind `` `ifndef FORMAL `` (macro `COUNT`).
     p02 leaves the action blocks bare to show it.
  2. `always_comb a1: assert (ok) else nf++;` does not run on Verilator
     5.052: `%Error: ... Active region did not converge after
     '--converge-limit' of 10000 tries`. The block reads `nf` (in
     `nf++`), and Verilator keeps it in the sensitivity although the
     block also writes it. p01 and p03 to p05 count through an event
     (`else -> failed;`) instead. A chapter listing that counts
     failures inside an `always_comb` action block will hang the same
     way.

## 1. Counts per column

88 rows: the note's 72 (`probes.txt`, p00 to p71) and 16 more
(`probes-x.txt`: the forms the native front end documents, and
discriminating probes that the first results asked for). 87 probe files;
the last x row re-runs p49 without `--coverage`.

| Column | runs | wrong | no run | no build | n/a |
|---|---|---|---|---|---|
| Verilator 5.052, main 72 | 50 | 6 | 0 | 9 | 7 |
| Icarus 13.0 `-g2012`, main | 4 | 0 | 1 | 59 | 8 |
| Yosys native via sby, main | 10 | 0 | 2 | 54 | 6 |
| Yosys `read_slang` via sby, main | 19 | 3 | 1 | 43 | 6 |
| Verilator 5.052, extra 16 | 10 | 4 | 0 | 2 | 0 |
| Icarus, extra | 3 | 1 | 3 | 8 | 1 |
| Yosys native, extra | 7 | 2 | 0 | 5 | 2 |
| Yosys `read_slang`, extra | 6 | 0 | 0 | 8 | 2 |

Verilator 5.054 on the eight † rows: p11, p13, p37, x08, x09 run; p19 no
build; **x12 and x15 still wrong**. Scratch runs of p16, p17, p18, p22,
p24, p25 on 5.054 print exactly the 5.052 lines, so none of the six
main-table wrong verdicts is fixed by the next release.

Icarus with `-gsupported-assertions` on its 67 no-build rows: 15 then
build; **12 of them report nothing when the design is wrong** (p06, p07,
p31 to p36, p47, p58, p71, x02), two have nothing to miss (p54, p61),
p30 and p60 fail at vvp load.

Full matrix run time, clean `build/`, 4 cores: **174 s** (218 s with a
z3 job running beside it). A re-run over an existing `build/` takes 11 s
because Verilator skips unchanged builds; `make clean` first for a true
measurement. Run one probe at a time it would take an estimated 11 minutes.

## 2. The three predictions the chapter depends on

Sources for these runs are scratch files, not in the repo. The FIFO
wrapper instantiates `fifo` (Chapter 1's, or a copy with a 5-bit `count`
and `full = (count == 16)`), keeps its own 5-bit `occ` (+1 on
`wr_en && !full`, -1 on `rd_en && !empty`, async reset like the DUT's),
assumes `!rst_n` in the first step through an `init` register, and
writes each property as a clocked immediate assertion guarded by
`if (rst_n)`. Same verdicts through `read -formal` and `read_slang`
unless stated.

### 2(a) Chapter 1 FIFO (the full-flag bug)

- `FullForward_A` (`occ == 16` implies `full`), `mode bmc`, `depth 20`:
  **passes vacuously.**
  `summary: engine_0 (smtbmc z3) returned pass` / `DONE (PASS, rc=0)`
- **Disagreement with the note (finding 4, "passes ... in an unbounded
  proof"):** under `mode prove`, `depth 20`, `smtbmc z3` it is not
  proved: `engine_0.induction: Temporal induction failed!` /
  `Assert failed in top: FullForward_A` / `summary: engine_0 (smtbmc
  z3) returned pass for basecase` / `returned FAIL for induction` /
  `DONE (UNKNOWN, rc=4)`. Under `abc pdr` it is: `engine_0: Property
  proved.  Time =     0.51 sec` / `DONE (PASS, rc=0)`. So the vacuous
  property already needs PDR (or a helper) to "pass unbounded".
- `FullBackward_A` (`full` implies `occ == 16`): `depth 10` passes
  (`DONE (PASS, rc=0)`); `depth 20` fails: `engine_0: BMC failed!` /
  `Assert failed in top: FullBackward_A` / `summary:   failed assertion
  top.FullBackward_A at top.sv:26.16-26.62 step 17` / `DONE (FAIL,
  rc=2)`. Step 17 is one reset step, fifteen pushes, and the one-step
  delay with which a clocked assertion is reported (see 3.4).
- `FullReached_C` (`cover (occ == 16)`), `mode cover`, `depth 20`:
  **unreachable.** `engine_0: Unreached cover statement at top:
  FullReached_C` / `summary: engine_0 (smtbmc z3) returned FAIL` /
  `DONE (FAIL, rc=2)`. On the fixed FIFO: `Reached cover statement in
  step 18 at top: FullReached_C` / `DONE (PASS, rc=0)`. `abc pdr`
  proves `occ != 16` on the buggy FIFO outright.
- Cost warning: the same unreachable cover at `depth 40` ran z3 for
  more than five minutes before it was killed; `depth 20` takes 3 s.

### 2(b) Fixed FIFO, `occ <= DEPTH`

- BMC `depth 20`: `DONE (PASS, rc=0)` (11 s native, 4 s slang).
- `mode prove`, `depth 5`, `smtbmc z3`: **fails induction, as
  predicted.** `engine_0.induction: Temporal induction failed!` /
  `Assert failed in top: NoOverflow_A` / `summary: engine_0 (smtbmc z3)
  returned pass for basecase` / `returned FAIL for induction` /
  `summary: counterexample trace [induction]:
  .../engine_0/trace_induct.vcd` / `DONE (UNKNOWN, rc=4)`. `depth 20`
  gives the same UNKNOWN (10 s): no k fixes it.
- With the helper `Sync_A: assert (occ == dut.count)` beside it,
  `depth 5`, **through `read_slang`**: `engine_0.induction: Temporal
  induction successful.` / `summary: successful proof by k-induction.`
  / `DONE (PASS, rc=0)`. Agreed.
- **Through `read -formal` the helper cannot be written that way.** The
  native front end does not resolve the hierarchical name: `Warning:
  Identifier `\dut.count' is implicitly declared.` / `Warning: Wire
  top.\dut.count is used but has no driver.`, the name becomes a free
  wire, and the run ends `BMC failed!` / `failed assertion top.Sync_A
  ... step 2` / `DONE (FAIL, rc=2)`: a false counterexample. Nor can
  the checker be bound in: the native front end parses `bind` and
  silently drops it (x10: PASS/PASS). On the native front end the
  helper has to live inside `fifo.sv` or `count` has to be a port. This
  decides the worked example's front end: white-box helpers need
  `read_slang`.
- `abc pdr` (with `aigsmt z3`), no helper: **proves it.** `engine_0:
  Property proved.  Time =     0.23 sec` / `summary: engine_0 (abc
  pdr) returned PASS` / `DONE (PASS, rc=0)`. Agreed.

### 2(c) Verilator 5.052, `a |=> b` against `a |-> ##1 b`

**The verdict is right; the pass action is wrong.** Scratch test, 16
ticks, `a` at t = 3, 6, 10, 11, 12 and `b` at t = 4, 11, 12, every pass
and failure printed:

```
5.052  t=7  |=>  FAIL          t=7  ##1  FAIL
       t=13 |=>  FAIL          t=13 ##1  FAIL
       totals over 16 ticks: |=> pass=14 fail=2; |-> ##1 pass=12 fail=2
       ticks with a |=> pass: 0 1 2 3 4 5 6 8 9 10 11 12 14 15
       ticks with a ##1 pass: 0 1 2 4 4 5 8 9 11 12 14 15
5.054  totals over 16 ticks: |=> pass=12 fail=2; |-> ##1 pass=12 fail=2
       (both lists equal the ##1 list above)
```

Failures are the same in number and tick, including with overlapping
attempts (x09). What differs on 5.052 is that `|=>` runs its pass
statement on the antecedent's own tick (3, 6, 10), before the
consequent is looked at: the attempt that starts at t = 6 gets a pass
at 6 and a FAIL at 7. Matrix rows p11 and x09 are therefore "runs" on
both, with the note `passes |=> 14, 13; ##1 14, 12` on 5.052 and
`14, 12; 14, 12` on 5.054. Consequence for the book: a failure-only
checker with `|=>` is safe on the pin; a pass action block or a pass
count on `|=>` is not.

## 3. Disagreements with the research note, and things it did not predict

### 3.1 Verilator 5.052 (and 5.054 where stated)

The note's list of "supported" constructs is from `Changes`. Six of
them build, run and give a **wrong verdict** in the main table, on both
releases:

| Row | Construct | What was measured |
|---|---|---|
| p16 | `go \|-> a[*1:3] ##1 b` | false failure. `a` at 2, 3 and `b` at 4 match with `[*2]`; Verilator reports a failure at t = 3, when the `[*1]` alternative dies. `a[*1:5] ##1 b` with no `b` fails three times, once per length. `[*2]` alone and the same thing written with `or` pass. A ranged repetition in a consequent is judged as if every length had to match. |
| p17 | `a[*1:$] ##1 b`, `a[+] ##1 b`, `a[*] ##1 b` | missed failure: with `b` never true nothing is reported; the attempt neither passes nor fails. |
| p18 | `a \|-> b[->2] ##1 c` | missed failure; `b[->1] ##1 c` likewise. |
| p22 | `(a ##1 b) within (c ##3 d)` | missed failure when the inner sequence never matches. |
| p24 | sequence `and`, `or` | `or` never fails, even `(##1 b) or (##1 b)` with `b` low (x15, both releases); `and` fails correctly but reports one attempt twice (3 for 2). |
| p25 | `first_match(a ##[1:3] b) \|-> c` | missed failure, and the cause is the antecedent, not `first_match`: see x12. |

- **x12, sequence antecedent with a ranged delay** `(a ##[1:3] b) |-> c`:
  matches are lost. Of three attempts that match at +1, +2, +3 and must
  each fail, 5.052 reports one (+3 only) and 5.054 two (+2, +3). With
  `b` at +1 and again at +3 neither release reports anything. A
  fixed-delay antecedent `(a ##2 b) |-> c` is right (x13). The note
  flagged the "sequence expression as antecedent" message as believed
  unreachable; the path is reachable in effect and silent.
- p19 `a |-> b[=2] ##1 c`: no build on both releases, `Usage of cycle
  delays requires default clocking (IEEE 1800-2023 14.11)`; `b[=2]`
  alone builds. The note lists `[=N]` as supported since 5.048 and
  expects #8612 (5.054) to matter; it does not for this form.
- p41 `strong(...)`: the documented `Unsupported: strong property in
  assert.` appears only for a top-level `strong(a ##[1:$] b)`; inside a
  consequent it is `syntax error, unexpected strong`.
- p56 `bind` to an instance: not only the instance-list form (x07,
  `Unsupported: Bind with instance list`, as documented). A hierarchical
  target (`bind dut.u1 ...`, `bind top.good.u1 ...`) is `syntax error,
  unexpected '.'`, and a simple instance name is taken for a module
  name and binds nothing. Verilator binds to modules only.
- p63 `checker`: not on either of the note's lists. A checker with
  ordinary arguments and a concurrent assertion works; an `event`
  formal with a `posedge clk` actual is a syntax error.
- p49 to p51, x11 **covers need `--coverage`**. The note says cover
  hits are *counted* only under `--coverage-user`. More than that:
  without `--coverage` or `--coverage-user` the pass statement of a
  `cover property`, `cover sequence` or immediate `cover` never runs
  (last row of the x table: hits 0). With either flag all three count
  correctly, `coverage.dat` has `top.good.c1' 1` / `top.bad.c1' 0`, and
  a `cover property` of an implication does not count vacuous successes
  (#7789, agreed). The book's `sv.mk` has neither flag.
- p11 `|=>`: see 2(c). The note's "prime suspect for a silent wrong
  result" is half right: wrong pass count, right verdict.
- x08 `disable iff` pulsed between edges: wrong on 5.052 (the failure
  is reported), right on 5.054, as #8733 says. A reset that is high
  across a clock edge aborts correctly on both (p37).
- p13 `##[1:3]` with overlapping attempts: right on both; #8371 makes
  no difference to this stimulus.
- p30: on the first tick `$past` returns 0, not X.
- p35: in an action block `t` and `$sampled(t)` both read 3 (the
  sampled value). The Chapter 4 race the note wanted to show with
  `$sampled` does not exist on Verilator; nothing to demonstrate.
- p14, p39: an attempt still pending at `$finish` is reported by
  neither a weak `##[1:$]` nor `s_eventually`. Nothing is printed at
  the end of the run.
- p53: the pass statement runs on every vacuous success (14 of 14).
- p52 `NEVERMATCH`: warns, as documented; `-Wall` without `-Wno-fatal`
  makes it an error.
- p61: default, the first failure ends the run with exit status 1 after
  one `[35000] %Error: file:line: Assertion failed in top.a1: 'assert'
  failed.` line; with `+verilator+error+limit+10` both failures are
  reported and the run reaches its `$finish`. Agreed.
- p60 extras: `+verilator+assert+lock` makes `$assertoff` a no-op (2
  failures instead of 1, as documented). `+verilator+noassert` silences
  p06 (0 failures), but a later `$asserton` in the testbench turns
  assertions back on (p60 still passes under it). `--no-assert` at
  build time: 0 failures.
- Agreed as documented: gated `$past` (p32), `nexttime` (p44), `expect`
  (p62), `[=M:N]` (p20), `intersect` with a variable-length operand
  (p23), two clocks (p59, as a syntax error).
- Severity, immediate assert at one failing tick: no action block and
  `$error` both print `%Error: ... Assertion failed in top.a1` and exit
  1; `$fatal` prints `%Fatal:` and exits 1; `$warning` and `$info`
  print and run on, exit 0.

### 3.2 Icarus 13.0

- Agreed: concurrent assertions are `sorry: concurrent_assertion_item
  not supported. Try -gno-assertions or -gsupported-assertions ...`;
  deferred are `sorry: Deferred assertions are not supported.`
- Disagreement: the note expects `error: Error in property_spec of
  concurrent assertion item` for temporal bodies. Measured: a bare
  `syntax error` (p10 and every other temporal row).
- `-gsupported-assertions`: section 1. Twelve silent passes.
- **A failing assertion does not change Icarus's exit status.** Default
  action and `$error` print `ERROR: file:line:` and the run continues to
  `$finish` with exit 0; only `$fatal` exits 1.
- x11: an immediate `cover (e) stmt;` compiles and its statement never
  runs (documented as dropped; measured as silent).
- `$past`, `$rose`, `$fell`, `$stable`, `$changed` compile and then
  fail at vvp load: `Error: System task/function $past() is not defined
  by any module.` (x03 to x05, p66). `$onehot`, `$onehot0`,
  `$countones`, `$isunknown` work (x06, x14). `let` is refused.
- p03: Icarus is the only tool that shows the zero-time glitch, 14
  times in 14 ticks, and only when the second signal is produced by
  another `always_comb`; with a continuous assignment it shows none.
  Verilator shows none in any form. The motivating listing for
  deferred assertions has to be an Icarus listing, and Icarus cannot
  then run the deferred fix.

### 3.3 Yosys native front end (`read -formal`)

- Agreed: clocked immediate `assert`/`assume`/`cover` (x01, p48, p69),
  module-level `assert property (e);` (x02), `assert final` (p05),
  `$past`, `$rose`, `$fell`, `$stable`, `$changed`, `$onehot`,
  `$onehot0`, `$countones` in a clocked `always` (x03 to x06),
  `$initstate`, `(* anyconst *)`, and a syntax error at `@` for every
  clocked concurrent form.
- **Any action block is a syntax error** (p02, p58): `unexpected
  TOK_ELSE` / `unexpected TOK_ID, expecting ';'`. Not in the note.
- **`bind` is parsed and silently ignored** (x10: PASS/PASS, no
  warning in the design log). The note left this as a probe.
- **`$isunknown` is wrong** (x14): `assert (!$isunknown(v))` fails and
  `assert ($isunknown(v))` passes. The note lists it as supported.
- Hierarchical references become free wires: 2(b).
- `assert #0` is a syntax error (p04); `let`, `default clocking`,
  `default disable iff`, `checker`, named properties: syntax errors.

### 3.4 Yosys `read_slang`

- Agreed: clocked boolean with `disable iff`, `$past(e)` and
  `$past(e, n)`, `bind` in all three forms (p55 to p57, x07), `let`,
  procedural concurrent assertion (p58), immediate and deferred
  assertions, action blocks accepted and ignored. A module-level
  `assert property (e)` with no clock is accepted too (x02).
- **`default disable iff` is silently ignored** (p09: FAIL/FAIL; the
  in-reset violation is reported, no warning). A file that relies on
  it gets false failures in formal.
- **`(* anyconst *)` is not honoured** (p65): a `logic` so marked is
  free in every step (stability assert fails), a `bit` is constant 0.
  `$anyconst` and `$initstate` are `unknown system name`. The note's
  "one symbolic slot" data-ordering idiom needs the native front end or
  another spelling.
- **`expect` is dropped** with only a warning in the design log
  (`expect statement will not be synthesized`): PASS/PASS (p62).
- `$rose`, `$fell`, `$stable`, `$changed`, `$onehot`, `$isunknown`:
  `unsupported system task`. Only `$past` of the sampled-value
  functions exists. `restrict property`: `unsupported assertion
  statement`. `default clocking`: `unsynthesizable timing control
  (ignore with '--ignore-timing')`. Named sequences and checkers:
  `Feature unimplemented (slang_frontend.cc:2936)`. Everything
  temporal: `encountered unsupported SVA feature`, as predicted.
- slang's own diagnostics are in `model/design.log`; sby's output only
  says `Design elaboration failed; see full log for details`.

**The common subset, measured** (the note's finding 1 says "a clocked
boolean with `$past`"): no single assertion text with a failure count
is accepted by all of Verilator, native and slang, because of the
action-block rule. Without an action block, the text all three accept
is the *clocked immediate* form, `always @(posedge clk) a1: assert
(e);`, with `$past` (x01, x03); Icarus takes it too, without `$past`.
The concurrent form `assert property (@(posedge clk) [disable iff (r)]
e)` is common to Verilator and `read_slang` only. p71's two-way macro
runs on Verilator and both front ends.

### 3.5 SymbiYosys

- Version 0.70. No default engine, as the addendum read from the
  source: `ERROR: Config file is lacking engine configuration.` (p00).
- `abc pdr` without `aigsmt`: a passing proof is fine; a failing one
  ends `engine_0: Could not determine aigsmt status.` /
  `DONE (ERROR, rc=16)`, because the default is yices. `aigsmt z3`
  fixes it. Agreed with the addendum.
- p67: `DONE (UNKNOWN, rc=4)` with `summary: engine_0 (smtbmc z3)
  returned FAIL for induction`; p68: PASS under `abc pdr`. Agreed.
- p69: `Unreached cover statement at dut: c1` / `DONE (FAIL, rc=2)`.
- p70: with `expect fail`, a failing task ends `DONE (FAIL, rc=0)` and
  a passing one `DONE (PASS, rc=1)`.
- p40: `mode live` needs `suprove`: `engine_0: COMMAND NOT FOUND.
  ERROR.` Liveness cannot be run here.
- **Contradictory assumptions are not a vacuous pass** (a refinement of
  p48's premise). With `assume (d < 8); assume (d > 9);` and a false
  assertion, `mode bmc` and `mode prove` end `Assumptions are
  unsatisfiable!` / `Status: PREUNSAT` / `DONE (ERROR, rc=16)`, because
  sby runs smtbmc with `--presat`; `mode cover` ends `Unreached cover
  statement` / FAIL. The vacuity a cover has to catch is the partial
  kind (an antecedent made unreachable), not total contradiction.
- `$past` in the first step is unconstrained in **both** front ends:
  each of `$past(x) == 0`, `== 15` and `!= 7` at t = 0 fails.
- A clocked assertion is reported one step after the state that
  violates it (a violation at t = 5 is "step 6").

## 4. What this changes for the chapter (for gate 1)

1. Verilator's sequence engine cannot be trusted beyond fixed delays,
   `##[m:n]` in a consequent, `[*N]`, `throughout`, the `until` family,
   `always [m:n]`, `not`, property `if`, followed-by, local variables
   and named sequences and properties. Ranged and unbounded repetition,
   goto, `within`, sequence `or`, `first_match` and ranged-delay
   antecedents give wrong verdicts on 5.052 **and 5.054**; moving the
   pin does not help. These want upstream bug reports.
2. Covers need `--coverage` in the example's flags.
3. The FIFO worked example works as designed: vacuous forward
   property, 15-push backward counterexample at step 17, unreachable
   cover, induction failure and its helper, PDR without the helper. It
   needs `read_slang` if the helper is to reach `count` from outside.
4. `default disable iff` must not be used in a file `read_slang` reads.
