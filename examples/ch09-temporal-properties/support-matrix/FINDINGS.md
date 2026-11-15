# Chapter 9 support matrix: findings for the author

Not for the book. Everything here was measured in this container on
2026-11-15; the tables themselves are in `matrix.md`, the per-row log in
`run.out`. "Note" is `research/ch09-temporal-properties.md`; the formal
tool's measurements are in `research/informal-measurements/FINDINGS.md`
and `research/ch09-formal-log.md`.

Revised the same day when the book's formal tool became InFormal: the
two formal-front-end columns of the first version are gone, with the
eight rows that asked questions only about them (p00, p65 to p71); the
second Verilator release is now run on every row; and there is an
InFormal column. Sections 3.1 and 3.2 keep the detail behind the
simulator cells from the first version's scratch runs; every cell of
both tables was re-measured for this revision and none of the simulator
cells changed.

## 0. Environment, and what the runner assumes

- Verilator 5.052 (`/opt/dvtools/bin`), Verilator 5.054
  (`/opt/verilator-5.054/bin`), Icarus 13.0, InFormal 0.1.0 at commit
  5114330 (`/opt/dvtools/bin/informal`, CaDiCaL linked, no Bitwuzla).
  `PATH=/opt/dvtools/bin:$PATH:/opt/dvtools/venv/bin`.
- Runner: `matrix.py`, with a thread pool (one probe per core) because
  every Verilator build costs about 8 s. Verilator flags are the
  book's with `--assert`, `-Wno-fatal`; the cover rows add `--coverage`.
- Probe design. Each probe has a `dut` with a free-running 4-bit step
  counter `t` as its stimulus and a parameter `BAD` that makes the
  design violate the assertion at a known tick. Simulation instantiates
  `dut #(0) good` and `dut #(1) bad`, counts failures in action blocks,
  and prints `PROBE pNN PASS|FAIL detail`.
- InFormal runs. `dut` is the top, read with `+define+FORMAL` (which
  removes the simulation top and the event-based failure counters of
  p01 to p05 and the x rows), once with `-parameter BAD 0` and once
  with 1; `clock clk`, `reset -none` (the counter has an initializer),
  `informal::set_engines informal-kind` (`informal-ic3` on the two
  liveness rows, where k-induction is slow), `set_prove_time_limit
  20s`, engine list `examples/mk/informal-engines.toml` (no external
  engine). A row runs when every assertion is `proven` with BAD 0 and
  one is `cex` with BAD 1 (cover rows: all `covered`, then one
  `unreachable`). A property with status `error` is "no build" with
  the tool's message; a report with no property of the kind the row
  asks about is "wrong".
- The tool has no depth bound and the probes' counter wraps after 16
  ticks, so an unbounded proof would judge behavior the simulation's 14
  ticks never reach. Where `t` exists the script adds `assume {t <
  4'd14}`: every trace ends where the simulation ends. This is a
  bounded check by construction and the table's caption says so. The
  two liveness rows do not get the assumption.
- `always_comb a1: assert (ok) else nf++;` does not run on Verilator
  5.052: `%Error: ... Active region did not converge after
  '--converge-limit' of 10000 tries`. p01 and p03 to p05 count through
  an event (`else -> failed;`) instead.

## 1. Counts per column

80 rows: 64 in `probes.txt` (p01 to p64) and 16 in `probes-x.txt`. 79
probe files; the last x row re-runs p49 without `--coverage`.

| Column | runs | wrong | no run | no build | n/a |
|---|---|---|---|---|---|
| Verilator 5.052, main 64 | 47 | 6 | 0 | 9 | 2 |
| Verilator 5.054, main | 47 | 6 | 0 | 9 | 2 |
| Icarus 13.0 `-g2012`, main | 3 | 0 | 0 | 58 | 3 |
| InFormal 0.1.0, main | 39 | 7 | 0 | 12 | 6 |
| Verilator 5.052, extra 16 | 10 | 4 | 0 | 2 | 0 |
| Verilator 5.054, extra | 11 | 3 | 0 | 2 | 0 |
| Icarus, extra | 3 | 1 | 3 | 8 | 1 |
| InFormal, extra | 5 | 8 | 0 | 1 | 2 |

Verilator 5.054 differs from 5.052 in one verdict (x08, now right) and
in the pass counts printed for p11 and x09 (section 2). None of the six
main-table wrong verdicts is fixed by the next release.

Icarus with `-gsupported-assertions` on its 66 no-build rows: 14 then
build; **11 of them report nothing when the design is wrong**.

Full matrix run time, clean `build/`, 4 cores: **6 min** (360 s wall,
most of it the second Verilator release on every row). A re-run over an
existing `build/` is much shorter because Verilator skips unchanged
builds; `make clean` first for a true measurement.

## 2. Verilator 5.052, `a |=> b` against `a |-> ##1 b`

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

## 3. What the cells rest on

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
- p11 `|=>`: see section 2. The note's "prime suspect for a silent wrong
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
- `-gsupported-assertions`: section 1. Eleven silent passes.
- **A failing assertion does not change Icarus's exit status.** Default
  action and `$error` print `ERROR: file:line:` and the run continues to
  `$finish` with exit 0; only `$fatal` exits 1.
- x11: an immediate `cover (e) stmt;` compiles and its statement never
  runs (documented as dropped; measured as silent).
- `$past`, `$rose`, `$fell`, `$stable`, `$changed` compile and then
  fail at vvp load: `Error: System task/function $past() is not defined
  by any module.` (x03 to x05). `$onehot`, `$onehot0`,
  `$countones`, `$isunknown` work (x06, x14). `let` is refused.
- p03: Icarus is the only tool that shows the zero-time glitch, 14
  times in 14 ticks, and only when the second signal is produced by
  another `always_comb`; with a continuous assignment it shows none.
  Verilator shows none in any form. The motivating listing for
  deferred assertions has to be an Icarus listing, and Icarus cannot
  then run the deferred fix.

### 3.3 InFormal 0.1.0 (commit 5114330)

- **Right on the whole chapter subset**: clocked boolean, `disable
  iff`, `default clocking`, `default disable iff`, `|->`, `|=>`,
  `##N`, `$past(x)`, `$past(x, n)`, `$rose`/`$fell`,
  `$stable`/`$changed`, `bind` in every form tried (module, one
  instance, instance list, `.*` to internal signals), a concurrent
  assertion under `if` in `always_ff`, `assume property` on a free
  input, `restrict property`, `cover property`, `cover sequence`,
  `let`, named sequences and properties with arguments.
- **Right where Verilator is wrong**: p16 ranged repetition, p22
  `within`, p24 sequence `and`/`or`, p25 `first_match`, x12 ranged
  delay in an antecedent, x15 `or` of two failing operands. Also
  builds and is right where Verilator refuses: p23 `intersect` with a
  variable-length operand, p32 gated `$past`, p44 `nexttime`, p56 and
  x07 `bind` to instances.
- **Refused with a message** (status `error` on the property, which
  the runner records as "no build"): `##[1:$]` (p14), `[*1:$]`, `[+]`,
  `[*]` (p17, "the repetition range [1:$]"), `[->]` (p18), `[=]` (p19,
  p20), `not` (p29), `strong(##[1:$] b)` (p41, for its delay range),
  property `if` (p45), followed-by (p46), an antecedent that has no
  match (p52), a sequence with its own clock (p59), a property with no
  clock and no default clocking (x02). `checker ... endchecker` (p63)
  stops the script: `SystemVerilog errors`.
- **Silently absent** (the report has no row for the property and
  nothing is printed; exit 0). Every "wrong" cell in the column is
  this: immediate assertions in `always_comb` and in clocked blocks
  (p01, p02, x01, x03 to x06, x14), deferred assertions (p04, p05), a
  bound checker written with clocked immediate assertions (x10), an
  immediate `cover` (x11), the `expect` statement (p62), **a property
  with a local variable (p28)**, and p36, whose module has `$onehot`,
  `$onehot0`, `$countones` and `$isunknown` assertions together.
  Taken apart in a scratch run: with the `$isunknown` line deleted the
  other three assertions are listed and refuted (`cex ... depth 5`), so
  one `$isunknown` assertion removes every RTL property of its module
  from the report, without a message (research FINDINGS F.1b).
- Liveness: `a |-> s_eventually b` (p39) and `s_eventually e` (p40)
  are proven on the good design and refuted on the bad one by
  `informal-ic3`.
- Not in this table, measured in the chapter's examples: asynchronous
  reset modelled as synchronous (`axi-formal`), contradictory
  assumptions (`vacuity-formal`), exit status (`examples/mk/informal.tcl`).
