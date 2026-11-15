| Construct | Verilator 5.052 | Verilator 5.054 | Icarus 13.0 | Yosys 0.68 native | Yosys 0.68 `read_slang` |
|---|---|---|---|---|---|
| toolchain: `sby` with no `[engines]` section | n/a — an sby question | n/a — an sby question | n/a — an sby question | no run — Config file is lacking engine configuration | no run — Config file is lacking engine configuration |
| immediate `assert (e)` in `always_comb` | runs | — | runs | runs | runs |
| immediate assert with pass and fail action blocks | runs | — | runs | no build — syntax error, unexpected TOK_ID, expecting ';' | runs |
| immediate assert in `always_comb` across a zero-time glitch | runs — glitch reported 0 times in 14 ticks | — | runs — glitch reported 14 times in 14 ticks | n/a — no zero-time order in a formal model | n/a — no zero-time order in a formal model |
| deferred `assert #0 (e)` | runs | — | no build — Deferred assertions are not supported. Try -gno-assertio | no build — syntax error, unexpected '#', expecting TOK_FINAL or TOK | runs |
| deferred `assert final (e)` | runs | — | no build — Deferred assertions are not supported. Try -gno-assertio | runs | runs |
| `assert property (@(posedge clk) e)` | runs | — | no build — concurrent_assertion_item not supported. Try -gno-assert | no build — syntax error, unexpected '@' | runs |
| `disable iff (!rst_n)` on a clocked boolean | runs | — | no build — concurrent_assertion_item not supported. Try -gno-assert | no build — syntax error, unexpected '@' | runs |
| `default clocking` and an unclocked `assert property (e)` | runs | — | no build — syntax error | no build — syntax error, unexpected TOK_DEFAULT | no build — unsynthesizable timing control (ignore with '--ignore-ti |
| `default disable iff` | runs | — | no build — syntax error | no build — syntax error, unexpected TOK_DEFAULT | wrong — FAIL/FAIL, want PASS/FAIL |
| overlapped implication `a \|-> b` | runs | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| non-overlapped `a \|=> b`, against `a \|-> ##1 b` | runs — passes \|=> 14, 13; ##1 14, 12 | runs — passes \|=> 14, 12; ##1 14, 12 | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| fixed delay `a ##2 b` | runs | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| ranged delay `a \|-> ##[1:3] b` | runs | runs | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| unbounded delay `a \|-> ##[1:$] b` (weak) | runs — b never comes: 0 failures reported | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| consecutive repetition `a[*3]` | runs | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| ranged repetition `a[*1:3] ##1 b` | wrong — failures good=1 bad=2, want 0 and 1 | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| unbounded repetition `a[*1:$]`, `a[+]`, `a[*]` | wrong — failures good=0 bad=0, want 0 and 3 | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| goto repetition `b[->2]` | wrong — failures good=0 bad=0, want 0 and 1 | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| nonconsecutive repetition `b[=2] ##1 c` | no build — Usage of cycle delays requires default clocking (IEEE 18 | no build — Usage of cycle delays requires default clocking (IEEE 18 | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| ranged nonconsecutive `b[=1:2]` | no build — Unsupported: [=M:N] nonconsecutive range repetition (IEE | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| `en throughout (a ##2 b)` | runs | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| `(a ##1 b) within (c ##3 d)` | wrong — failures good=0 bad=0, want 0 and 1 | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| `a[*1:3] intersect (b ##2 c)` | no build — Unsupported: intersect with this variable-length operand | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| sequence `and`, sequence `or` | wrong — and/or good=0/0 bad=3/0, want 0/0 and 2/1 | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| `first_match(a ##[1:3] b) \|-> c` | wrong — failures good=0 bad=0, want 0 and 1 | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| named `sequence` with arguments | runs | — | no build — syntax error | no build — syntax error, unexpected '#', expecting '(' | no build — Feature unimplemented (slang_frontend.cc:2936) |
| named `property` with arguments, used twice | runs | — | no build — syntax error | no build — syntax error, unexpected TOK_PROPERTY | no build — SVA unsupported (ignore all assertions with '--ignore-as |
| property-local variable carrying data | runs | — | no build — syntax error | no build — syntax error, unexpected TOK_PROPERTY | no build — SVA unsupported (ignore all assertions with '--ignore-as |
| `not (a ##1 b)` | runs | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| `$past(x)` | runs — on the first tick $past reads 0000 | — | no build — concurrent_assertion_item not supported. Try -gno-assert | no build — syntax error, unexpected '@' | runs |
| `$past(x, 3)` | runs | — | no build — concurrent_assertion_item not supported. Try -gno-assert | no build — syntax error, unexpected '@' | runs |
| gated `$past(x, 1, en)` | no build — Unsupported: $past expr2 and/or clock arguments | — | no build — concurrent_assertion_item not supported. Try -gno-assert | no build — syntax error, unexpected '@' | no build — $past gating_expr (3rd argument) and clocking_event (4th |
| `$rose`, `$fell`, on one bit and on a vector | runs | — | no build — concurrent_assertion_item not supported. Try -gno-assert | no build — syntax error, unexpected '@' | no build — unsupported system task '$rose' |
| `$stable`, `$changed` | runs | — | no build — concurrent_assertion_item not supported. Try -gno-assert | no build — syntax error, unexpected '@' | no build — unsupported system task '$changed' |
| `$sampled(x)` in an action block | runs — t reads 3, $sampled(t) reads 3 | — | no build — concurrent_assertion_item not supported. Try -gno-assert | n/a — action blocks are simulation code | n/a — action blocks are simulation code |
| `$onehot`, `$onehot0`, `$countones`, `$isunknown` | runs | — | no build — concurrent_assertion_item not supported. Try -gno-assert | no build — syntax error, unexpected '@' | no build — unsupported system task '$onehot' |
| `disable iff` rising in mid-attempt | runs | runs | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| reset as an antecedent term | runs | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| `a \|-> s_eventually b` at the end of a run | runs — b never comes: 0 failures reported | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| `assert property (s_eventually e)` under `mode live` | n/a — an sby mode | n/a — an sby mode | n/a — an sby mode | no run — the engine's solver is not installed | no build — encountered unsupported SVA feature |
| `strong(##[1:$] b)` | no build — syntax error, unexpected strong, expecting IDENTIFIER-fo | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| `until`, `s_until`, `until_with` | runs | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| `always [2:5] a` | runs | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| `nexttime a` | no build — Unsupported: nexttime (in property expression) | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| property `if (m) p else q` | runs | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| followed-by `a #=# b`, `a #-# c` | runs | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| `assume property` in simulation | runs | — | no build — concurrent_assertion_item not supported. Try -gno-assert | n/a — there it constrains | n/a — there it constrains |
| `assume` constraining a free input | n/a — needs a free input | n/a — needs a free input | n/a — needs a free input | runs | runs |
| `cover property (a ##1 b)` | runs | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| `cover property (a \|-> b)`, antecedent never true | runs | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| `cover sequence` | runs | — | no build — syntax error | no build — syntax error, unexpected TOK_ID, expecting TOK_PROPERTY | no build — encountered unsupported SVA feature |
| antecedent that can never match | runs — warns NEVERMATCH | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| pass action block on a vacuous success | runs — pass statement ran 14 times on 14 vacuous successes | — | no build — syntax error | n/a — action blocks are simulation code | n/a — action blocks are simulation code |
| `restrict property` | runs | — | no build — concurrent_assertion_item not supported. Try -gno-assert | no build — syntax error, unexpected '@' | no build — unsupported assertion statement |
| `bind` to a module, named port connections | runs | — | no build — concurrent_assertion_item not supported. Try -gno-assert | no build — syntax error, unexpected '@' | runs |
| `bind` to one instance | no build — Can't find definition of 'chk' in dotted scope/variable: | — | no build — syntax error | no build — syntax error, unexpected '@' | runs |
| `bind` reading internal signals through `.*` | runs | — | no build — concurrent_assertion_item not supported. Try -gno-assert | no build — syntax error, unexpected '@' | runs |
| concurrent assertion inside `always_ff` under `if` | runs | — | no build — concurrent_assertion_item not supported. Try -gno-assert | no build — syntax error, unexpected TOK_ELSE, expecting ';' | runs |
| property with two clocks | no build — syntax error, unexpected '@', expecting IDENTIFIER-for-t | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| `$assertoff`, `$asserton` | runs | — | no build — concurrent_assertion_item not supported. Try -gno-assert | n/a — simulation control tasks | n/a — simulation control tasks |
| two failures, default and `+verilator+error+limit+10` | runs — default 1 reported, stops; limit 10: 2, runs on | — | n/a — a Verilator run-time switch | n/a — a run-time switch | n/a — a run-time switch |
| `expect` statement | no build — Unsupported: expect | — | no build — syntax error | no build — syntax error, unexpected '@' | wrong — PASS/PASS, want PASS/FAIL |
| `checker ... endchecker` | runs | — | no build — syntax error | no build — syntax error, unexpected TOK_INT | no build — Feature unimplemented (slang_frontend.cc:2936) |
| `let` declaration used in a property | runs | — | no build — let declarations (imp) are not currently supported. | no build — syntax error, unexpected '=', expecting ',' or ';' | runs |
| `(* anyconst *)` in a file simulators also read | runs — k reads 0000 | — | runs — k reads xxxx | runs | wrong — FAIL/FAIL, want PASS/FAIL |
| `$initstate` behind `` `ifdef FORMAL `` | runs | — | no run — System task/function $past() is not defined by any modul | runs | no build — unknown system name '$initstate' [-Wunknown-sys-name] |
| `mode prove`, `depth 5`: a true property that is not inductive | n/a — an sby result | n/a — an sby result | n/a — an sby result | runs — UNKNOWN/FAIL | runs — UNKNOWN/FAIL |
| the same property under `abc pdr` | n/a — an sby result | n/a — an sby result | n/a — an sby result | runs | runs |
| `mode cover`: an unreachable `cover` | n/a — an sby result | n/a — an sby result | n/a — an sby result | runs | runs |
| `expect fail` and the exit status of `sby` | n/a — an sby option | n/a — an sby option | n/a — an sby option | runs — exit 1 and 0 | runs — exit 1 and 0 |
| one `` `ASSERT `` macro, two expansions | runs | — | no build — concurrent_assertion_item not supported. Try -gno-assert | runs | runs |

: What each open tool does with the assertion constructs this chapter teaches, measured by running one probe per row: under the simulators with the flags the book's build uses plus `--assert` and `-Wno-fatal` (Icarus with `-g2012`), and under SymbiYosys 0.70 through `read -formal` and through `read_slang`, bounded model checking to depth 12 with `smtbmc z3` unless the row names another mode. Each probe holds a design that satisfies its assertion and one that violates it, and a row runs only if both verdicts are right. A dash is a row the newer Verilator was not asked about. Verilator 5.052: 50 runs, 6 wrong, 9 no build, 7 n/a; Verilator 5.054: 3 runs, 1 no build, 7 n/a; Icarus 13.0: 4 runs, 1 no run, 59 no build, 8 n/a; Yosys 0.68 native: 10 runs, 2 no run, 54 no build, 6 n/a; Yosys 0.68 `read_slang`: 19 runs, 3 wrong, 1 no run, 43 no build, 6 n/a. Regenerated from the probes on every run. {#tbl-ch09-support}

| Construct | Verilator 5.052 | Verilator 5.054 | Icarus 13.0 | Yosys 0.68 native | Yosys 0.68 `read_slang` |
|---|---|---|---|---|---|
| immediate `assert (e)` in `always @(posedge clk)` | runs | — | runs | runs | runs |
| module-level `assert property (e);` with no clock | no build — Concurrent assertion has no clock (IEEE 1800-2023 16.16) | — | no build — concurrent_assertion_item not supported. Try -gno-assert | runs | runs |
| `$past(x)` in a clocked immediate assert | runs | — | no run — System task/function $past() is not defined by any modul | runs | runs |
| `$rose`, `$fell` in clocked immediate asserts | runs | — | no run — System task/function $rose() is not defined by any modul | runs | no build — unsupported system task '$rose' |
| `$stable`, `$changed` in clocked immediate asserts | runs | — | no run — System task/function $changed() is not defined by any mo | runs | no build — unsupported system task '$changed' |
| `$onehot`, `$onehot0`, `$countones` in clocked immediate asserts | runs | — | runs | runs | no build — unsupported system task '$onehot' |
| `bind` with an instance list | no build — Unsupported: Bind with instance list | — | no build — syntax error | no build — syntax error, unexpected '@' | runs |
| `disable iff` pulsed between two clock edges | wrong — failures good=1 bad=1, want 0 and 1 | runs | no build — syntax error | n/a — one clock, nothing between its edges | n/a — one clock, nothing between its edges |
| `a \|=> b` with overlapping attempts, against `a \|-> ##1 b` | runs — passes \|=> 14, 13; ##1 14, 12 | runs — passes \|=> 14, 12; ##1 14, 12 | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| `bind` of a checker written with clocked immediate asserts | runs | — | no build — syntax error | wrong — PASS/PASS, want PASS/FAIL | runs |
| immediate `cover (e)` in a clocked `always` | runs | — | wrong — hits good=0 bad=0, want 1 and 0 | runs | runs |
| sequence antecedent with a ranged delay `(a ##[1:3] b) \|-> c` | wrong — failures good=0 bad=1, want 0 and 3 | wrong — failures good=0 bad=2, want 0 and 3 | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| sequence antecedent with a fixed delay `(a ##2 b) \|-> c` | runs | — | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| `$isunknown` in a clocked immediate assert | runs | — | runs | wrong — FAIL/FAIL, want PASS/FAIL | no build — unsupported system task '$isunknown' |
| sequence `or` of two operands that both fail | wrong — failures good=0 bad=0, want 0 and 1 | wrong — failures good=0 bad=0, want 0 and 1 | no build — syntax error | no build — syntax error, unexpected '@' | no build — encountered unsupported SVA feature |
| `cover property (a ##1 b)`, built without `--coverage` | wrong — hits good=0 bad=0, want 1 and 0 | — | n/a — as p49 | n/a — as p49 | n/a — as p49 |

: What each open tool does with the second set of assertion probes: the forms the native Yosys front end documents, and discriminating probes, measured by running one probe per row: under the simulators with the flags the book's build uses plus `--assert` and `-Wno-fatal` (Icarus with `-g2012`), and under SymbiYosys 0.70 through `read -formal` and through `read_slang`, bounded model checking to depth 12 with `smtbmc z3` unless the row names another mode. Each probe holds a design that satisfies its assertion and one that violates it, and a row runs only if both verdicts are right. A dash is a row the newer Verilator was not asked about. Verilator 5.052: 10 runs, 4 wrong, 2 no build; Verilator 5.054: 2 runs, 2 wrong; Icarus 13.0: 3 runs, 1 wrong, 3 no run, 8 no build, 1 n/a; Yosys 0.68 native: 7 runs, 2 wrong, 5 no build, 2 n/a; Yosys 0.68 `read_slang`: 6 runs, 8 no build, 2 n/a. Regenerated from the probes on every run. {#tbl-ch09-support-x}
