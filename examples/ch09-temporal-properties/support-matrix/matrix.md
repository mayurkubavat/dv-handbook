| Construct | Verilator 5.052 | Verilator 5.054 | Icarus 13.0 | InFormal 0.1.0 |
|---|---|---|---|---|
| immediate `assert (e)` in `always_comb` | runs | runs | runs | wrong — no assert in the report, and no message |
| immediate assert with pass and fail action blocks | runs | runs | runs | wrong — no assert in the report, and no message |
| immediate assert in `always_comb` across a zero-time glitch | runs — glitch reported 0 times in 14 ticks | runs — glitch reported 0 times in 14 ticks | runs — glitch reported 14 times in 14 ticks | n/a — no zero-time order in a formal model |
| deferred `assert #0 (e)` | runs | runs | no build — Deferred assertions are not supported. Try -gno-assertio | wrong — no assert in the report, and no message |
| deferred `assert final (e)` | runs | runs | no build — Deferred assertions are not supported. Try -gno-assertio | wrong — no assert in the report, and no message |
| `assert property (@(posedge clk) e)` | runs | runs | no build — concurrent_assertion_item not supported. Try -gno-assert | runs |
| `disable iff (!rst_n)` on a clocked boolean | runs | runs | no build — concurrent_assertion_item not supported. Try -gno-assert | runs |
| `default clocking` and an unclocked `assert property (e)` | runs | runs | no build — syntax error | runs |
| `default disable iff` | runs | runs | no build — syntax error | runs |
| overlapped implication `a \|-> b` | runs | runs | no build — syntax error | runs |
| non-overlapped `a \|=> b`, against `a \|-> ##1 b` | runs — passes \|=> 14, 13; ##1 14, 12 | runs — passes \|=> 14, 12; ##1 14, 12 | no build — syntax error | runs |
| fixed delay `a ##2 b` | runs | runs | no build — syntax error | runs |
| ranged delay `a \|-> ##[1:3] b` | runs | runs | no build — syntax error | runs |
| unbounded delay `a \|-> ##[1:$] b` (weak) | runs — b never comes: 0 failures reported | runs — b never comes: 0 failures reported | no build — syntax error | no build — not supported yet: the delay range [1:$] |
| consecutive repetition `a[*3]` | runs | runs | no build — syntax error | runs |
| ranged repetition `a[*1:3] ##1 b` | wrong — failures good=1 bad=2, want 0 and 1 | wrong — failures good=1 bad=2, want 0 and 1 | no build — syntax error | runs |
| unbounded repetition `a[*1:$]`, `a[+]`, `a[*]` | wrong — failures good=0 bad=0, want 0 and 3 | wrong — failures good=0 bad=0, want 0 and 3 | no build — syntax error | no build — not supported yet: the repetition range [1:$] |
| goto repetition `b[->2]` | wrong — failures good=0 bad=0, want 0 and 1 | wrong — failures good=0 bad=0, want 0 and 1 | no build — syntax error | no build — not supported yet: the goto repetition [->] |
| nonconsecutive repetition `b[=2] ##1 c` | no build — Usage of cycle delays requires default clocking (IEEE 18 | no build — Usage of cycle delays requires default clocking (IEEE 18 | no build — syntax error | no build — not supported yet: the non-consecutive repetition [=] |
| ranged nonconsecutive `b[=1:2]` | no build — Unsupported: [=M:N] nonconsecutive range repetition (IEE | no build — Unsupported: [=M:N] nonconsecutive range repetition (IEE | no build — syntax error | no build — not supported yet: the non-consecutive repetition [=] |
| `en throughout (a ##2 b)` | runs | runs | no build — syntax error | runs |
| `(a ##1 b) within (c ##3 d)` | wrong — failures good=0 bad=0, want 0 and 1 | wrong — failures good=0 bad=0, want 0 and 1 | no build — syntax error | runs |
| `a[*1:3] intersect (b ##2 c)` | no build — Unsupported: intersect with this variable-length operand | no build — Unsupported: intersect with this variable-length operand | no build — syntax error | runs |
| sequence `and`, sequence `or` | wrong — and/or good=0/0 bad=3/0, want 0/0 and 2/1 | wrong — and/or good=0/0 bad=3/0, want 0/0 and 2/1 | no build — syntax error | runs |
| `first_match(a ##[1:3] b) \|-> c` | wrong — failures good=0 bad=0, want 0 and 1 | wrong — failures good=0 bad=0, want 0 and 1 | no build — syntax error | runs |
| named `sequence` with arguments | runs | runs | no build — syntax error | runs |
| named `property` with arguments, used twice | runs | runs | no build — syntax error | runs |
| property-local variable carrying data | runs | runs | no build — syntax error | wrong — no assert in the report, and no message |
| `not (a ##1 b)` | runs | runs | no build — syntax error | no build — not supported yet: property `not` |
| `$past(x)` | runs — first-tick $past: net 0, initial-block 0, initializer 5 | runs — first-tick $past: net 0, initial-block 0, initializer 5 | no build — concurrent_assertion_item not supported. Try -gno-assert | runs |
| `$past(x, 3)` | runs | runs | no build — concurrent_assertion_item not supported. Try -gno-assert | runs |
| gated `$past(x, 1, en)` | no build — Unsupported: $past expr2 and/or clock arguments | no build — Unsupported: $past expr2 and/or clock arguments | no build — concurrent_assertion_item not supported. Try -gno-assert | runs |
| `$rose`, `$fell`, on one bit and on a vector | runs | runs | no build — concurrent_assertion_item not supported. Try -gno-assert | runs |
| `$stable`, `$changed` | runs | runs | no build — concurrent_assertion_item not supported. Try -gno-assert | runs |
| `$sampled(x)` in an action block | runs — t reads 3, $sampled(t) reads 3 | runs — t reads 3, $sampled(t) reads 3 | no build — concurrent_assertion_item not supported. Try -gno-assert | n/a — action blocks are simulation code |
| `$onehot`, `$onehot0`, `$countones`, `$isunknown` | runs | runs | no build — concurrent_assertion_item not supported. Try -gno-assert | wrong — no assert in the report, and no message |
| `disable iff` rising in mid-attempt | runs | runs | no build — syntax error | runs |
| reset as an antecedent term | runs | runs | no build — syntax error | runs |
| `a \|-> s_eventually b` at the end of a run | runs — b never comes: 0 failures reported | runs — b never comes: 0 failures reported | no build — syntax error | runs |
| `assert property (s_eventually e)`, a liveness property | n/a — no finite run decides it | n/a — no finite run decides it | n/a — no finite run decides it | runs |
| `strong(##[1:$] b)` | no build — syntax error, unexpected strong, expecting IDENTIFIER-fo | no build — syntax error, unexpected strong, expecting IDENTIFIER-fo | no build — syntax error | no build — not supported yet: the delay range [1:$] |
| `until`, `s_until`, `until_with` | runs | runs | no build — syntax error | runs |
| `always [2:5] a` | runs | runs | no build — syntax error | runs |
| `nexttime a` | no build — Unsupported: nexttime (in property expression) | no build — Unsupported: nexttime (in property expression) | no build — syntax error | runs |
| property `if (m) p else q` | runs | runs | no build — syntax error | no build — not supported yet: property `if` |
| followed-by `a #=# b`, `a #-# c` | runs | runs | no build — syntax error | no build — not supported yet: followed-by (#-#, #=#) |
| `assume property` in simulation | runs | runs | no build — concurrent_assertion_item not supported. Try -gno-assert | n/a — there it constrains |
| `assume` constraining a free input | n/a — needs a free input | n/a — needs a free input | n/a — needs a free input | runs |
| `cover property (a ##1 b)` | runs | runs | no build — syntax error | runs |
| `cover property (a \|-> b)`, antecedent never true | runs | runs | no build — syntax error | runs |
| `cover sequence` | runs | runs | no build — syntax error | runs |
| antecedent that can never match | runs — warns NEVERMATCH | runs — warns NEVERMATCH | no build — syntax error | no build — not supported yet: an antecedent that has no match |
| pass action block on a vacuous success | runs — pass statement ran 14 times on 14 vacuous successes | runs — pass statement ran 14 times on 14 vacuous successes | no build — syntax error | n/a — action blocks are simulation code |
| `restrict property` | runs | runs | no build — concurrent_assertion_item not supported. Try -gno-assert | runs |
| `bind` to a module, named port connections | runs | runs | no build — concurrent_assertion_item not supported. Try -gno-assert | runs |
| `bind` to one instance | no build — Can't find definition of 'chk' in dotted scope/variable: | no build — Can't find definition of 'chk' in dotted scope/variable: | no build — syntax error | runs |
| `bind` reading internal signals through `.*` | runs | runs | no build — concurrent_assertion_item not supported. Try -gno-assert | runs |
| concurrent assertion inside `always_ff` under `if` | runs | runs | no build — concurrent_assertion_item not supported. Try -gno-assert | runs |
| property with two clocks | no build — syntax error, unexpected '@', expecting IDENTIFIER-for-t | no build — syntax error, unexpected '@', expecting IDENTIFIER-for-t | no build — syntax error | no build — not supported yet: a sequence with its own clock |
| `$assertoff`, `$asserton` | runs | runs | no build — concurrent_assertion_item not supported. Try -gno-assert | n/a — simulation control tasks |
| two failures, default and `+verilator+error+limit+10` | runs — default 1 reported, stops; limit 10: 2, runs on | runs — default 1 reported, stops; limit 10: 2, runs on | n/a — a Verilator run-time switch | n/a — a run-time switch |
| `expect` statement | no build — Unsupported: expect | no build — Unsupported: expect | no build — syntax error | wrong — no assert in the report, and no message |
| `checker ... endchecker` | runs | runs | no build — syntax error | no build — SystemVerilog errors |
| `let` declaration used in a property | runs | runs | no build — let declarations (imp) are not currently supported. | runs |

: What each tool does with the assertion constructs this chapter names, measured by running one probe per row: under the simulators with the flags the book's build uses plus `--assert` and `-Wno-fatal` (Icarus with `-g2012`), and under InFormal with the engine `informal-kind` (`informal-ic3` on the two liveness rows), a limit of 20 s for each property, no reset, and the probe's tick counter assumed to stay below 14. Each probe holds a design that satisfies its assertion and one that violates it, and a row runs only if both verdicts are right. Verilator 5.052: 47 runs, 6 wrong, 9 no build, 2 n/a; Verilator 5.054: 47 runs, 6 wrong, 9 no build, 2 n/a; Icarus 13.0: 3 runs, 58 no build, 3 n/a; InFormal 0.1.0: 39 runs, 7 wrong, 12 no build, 6 n/a. With `-gsupported-assertions`, tried on its 58 no-build rows, Icarus builds 13, and 10 of those give a wrong verdict. Regenerated from the probes on every run. {#tbl-ch09-support}

| Construct | Verilator 5.052 | Verilator 5.054 | Icarus 13.0 | InFormal 0.1.0 |
|---|---|---|---|---|
| immediate `assert (e)` in `always @(posedge clk)` | runs | runs | runs | wrong — no assert in the report, and no message |
| module-level `assert property (e);` with no clock | no build — Concurrent assertion has no clock (IEEE 1800-2023 16.16) | no build — Concurrent assertion has no clock (IEEE 1800-2023 16.16) | no build — concurrent_assertion_item not supported. Try -gno-assert | no build — not supported yet: a property with no clock (no clocking |
| `$past(x)` in a clocked immediate assert | runs | runs | no run — System task/function $past() is not defined by any modul | wrong — no assert in the report, and no message |
| `$rose`, `$fell` in clocked immediate asserts | runs | runs | no run — System task/function $rose() is not defined by any modul | wrong — no assert in the report, and no message |
| `$stable`, `$changed` in clocked immediate asserts | runs | runs | no run — System task/function $changed() is not defined by any mo | wrong — no assert in the report, and no message |
| `$onehot`, `$onehot0`, `$countones` in clocked immediate asserts | runs | runs | runs | wrong — no assert in the report, and no message |
| `bind` with an instance list | no build — Unsupported: Bind with instance list | no build — Unsupported: Bind with instance list | no build — syntax error | runs |
| `disable iff` pulsed between two clock edges | wrong — failures good=1 bad=1, want 0 and 1 | runs | no build — syntax error | n/a — one clock, nothing between its edges |
| `a \|=> b` with overlapping attempts, against `a \|-> ##1 b` | runs — passes \|=> 14, 13; ##1 14, 12 | runs — passes \|=> 14, 12; ##1 14, 12 | no build — syntax error | runs |
| `bind` of a checker written with clocked immediate asserts | runs | runs | no build — syntax error | wrong — no assert in the report, and no message |
| immediate `cover (e)` in a clocked `always` | runs | runs | wrong — hits good=0 bad=0, want 1 and 0 | wrong — no cover in the report, and no message |
| sequence antecedent with a ranged delay `(a ##[1:3] b) \|-> c` | wrong — failures good=0 bad=1, want 0 and 3 | wrong — failures good=0 bad=2, want 0 and 3 | no build — syntax error | runs |
| sequence antecedent with a fixed delay `(a ##2 b) \|-> c` | runs | runs | no build — syntax error | runs |
| `$isunknown` in a clocked immediate assert | runs | runs | runs | wrong — no assert in the report, and no message |
| sequence `or` of two operands that both fail | wrong — failures good=0 bad=0, want 0 and 1 | wrong — failures good=0 bad=0, want 0 and 1 | no build — syntax error | runs |
| `cover property (a ##1 b)`, built without `--coverage` | wrong — hits good=0 bad=0, want 1 and 0 | wrong — hits good=0 bad=0, want 1 and 0 | n/a — as p49 | n/a — as p49 |
| failed immediate assertion with no action block: exit status | runs — failure printed, run stops, exit status 1 | runs — failure printed, run stops, exit status 1 | runs — failure printed, run goes on, exit status 0 | n/a — a simulator's exit status |
| concurrent assertion inside an `interface` | runs | runs | no build — concurrent_assertion_item not supported. Try -gno-assert | runs |
| obligation pending at `$finish`, once per operator | runs — `s_eventually`, `##[1:$]`, `##[1:3]`, `until`: silent, exit status 0; `s_until`: reported after `$finish`, unlabeled, exit status 1; no action block ran | runs — `s_eventually`, `##[1:$]`, `##[1:3]`, `until`: silent, exit status 0; `s_until`: reported after `$finish`, unlabeled, exit status 1; no action block ran | n/a — no concurrent form builds | n/a — a proof has no end of run |

: What each tool does with the second set of assertion probes: the clocked immediate forms, and discriminating probes, measured by running one probe per row: under the simulators with the flags the book's build uses plus `--assert` and `-Wno-fatal` (Icarus with `-g2012`), and under InFormal with the engine `informal-kind` (`informal-ic3` on the two liveness rows), a limit of 20 s for each property, no reset, and the probe's tick counter assumed to stay below 14. Each probe holds a design that satisfies its assertion and one that violates it, and a row runs only if both verdicts are right. Verilator 5.052: 13 runs, 4 wrong, 2 no build; Verilator 5.054: 14 runs, 3 wrong, 2 no build; Icarus 13.0: 4 runs, 1 wrong, 3 no run, 9 no build, 2 n/a; InFormal 0.1.0: 6 runs, 8 wrong, 1 no build, 4 n/a. With `-gsupported-assertions`, tried on its 9 no-build rows, Icarus builds 2, and 2 of those give a wrong verdict. Regenerated from the probes on every run. {#tbl-ch09-support-x}
