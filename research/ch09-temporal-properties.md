---
title: "Research note: Chapter 9 — Temporal Properties and Assertions"
date: 2026-11-15
author: research-agent
status: complete (documentation only; nothing executed; IEEE 1800 clause 16 not read); formal-tool parts superseded 2026-11-15, see the revision note below
feeds: Ch. 9 (and Appendix C, the SVA reference)
---

# Chapter 9 — Temporal Properties and Assertions: evidence note

Scope: the theory a property language rests on (linear temporal logic,
regular expressions over traces, safety and liveness, weak and strong,
vacuity); the SystemVerilog assertion language as IEEE 1800 clause 16
defines it; what the book's pinned open tools (Verilator 5.052, Icarus
13.0, Yosys 0.68 with SymbiYosys) document about each construct; how
OpenTitan uses one set of assertions as simulation checkers and as formal
obligations; the Python mirror; and a worked-example proposal on the
Chapter 1 FIFO and the Chapter 11 AXI handshake.

**Nothing in this note was executed.** The research container has no
Verilator, Icarus, Yosys or SymbiYosys. Every statement about a tool is
"documented" (read in the tool's own tagged files) and none is "measured".
The probe list in Part C §5 is what the author runs to turn the documented
column into a measured one, as Chapter 8's Part C did.

Section numbers are local to their part.

The parts are in the order they were written (most decisive first), not
alphabetical: **C** tools, **D** practice, **A** theory and evidence,
**B** language and clause numbers, **E** Python, **F** worked example,
then an addendum to C, one unsourced-claims table, BibTeX suggestions and
confidence notes for the whole note.

## Revision note, 2026-11-15: the book's formal tool is InFormal

After this note was written the author replaced SymbiYosys with InFormal
(https://github.com/mayurkubavat/informal, version 0.1.0, commit
5114330) as the formal tool of Chapter 9 and of the formal chapters. The
note below is left as written, as the record of what was read; this
section says which of its parts still feed the chapter.

- **Still feeds the chapter:** Part A (theory), Part B (language and
  clause numbers), Part D (OpenTitan practice), Part E (Python mirror),
  and in Part C the Verilator and Icarus sections.
- **No longer feeds the chapter:** Part C §3 and the addendum (Yosys
  0.68 and SymbiYosys as documented), the "native" and `read_slang`
  columns of the probe list in Part C §5, and every SymbiYosys step of
  the worked-example proposal in Part F (`mode bmc` / `cover` /
  `prove`, the `.sby` files, the induction-failure trace). The chapter
  names SymbiYosys once, in a comparison table, from its own
  documentation.
- **Finding 1 below is overturned for the book's tools.** "The same
  property as checker and as proof obligation is literally true only
  for clocked booleans with `$past`" was a statement about Yosys.
  InFormal's shell does not collect immediate assertions at all (empty
  table, exit 0), and it takes concurrent assertions with implication,
  fixed and ranged delays, repetition and the sampled-value functions.
  The chapter's common form is therefore `assert property (@(posedge
  clk) disable iff (!rst_n) e);` with `e` restricted to booleans,
  `|->`, `|=>`, fixed `##N`, `$past`, `$rose`, `$fell`, `$stable`,
  which Verilator 5.052 and InFormal were both measured to get right.
- **Finding on the FIFO's induction story is replaced.** `occ <= DEPTH`
  on the repaired FIFO is proved by InFormal's k-induction with no
  helper. The helper-invariant lesson is taught on `empty |-> wr_ptr ==
  rd_ptr` with the helper `count == wr_ptr - rd_ptr`.
- **Where the measurements are:**
  `research/informal-measurements/FINDINGS.md` (the tool, sections A to
  H, with scripts), `research/ch09-formal-log.md` (what was re-run for
  the chapter and what differed), and
  `examples/ch09-temporal-properties/support-matrix/FINDINGS.md` (the
  regenerated matrix: Verilator 5.052 and 5.054, Icarus 13.0, InFormal
  0.1.0).
- **Sources added for the tool change** are listed in section 6 of
  `research/ch09-formal-log.md`; the `refs.bib` keys are
  `informal-tool`, `sby-docs`, `sby-verific`, `cadence-jasper-fpv`,
  `synopsys-vcformal` and `siemens-questa-formal`.

## Which part feeds which chapter section

| Chapter topic | Part | Sections |
|---|---|---|
| Motivation: a monitor is a hand-built automaton; the same rule as one line | E §1; F §4 | Chapter 11's `stable()` |
| LTL, safety and liveness, bounded liveness | A | §1, §2 |
| Sequences as regular expressions; SVA's lineage | A §3; B §3 | |
| Weak and strong; what the end of simulation means | A | §1 (3), §4 |
| Vacuity and covers | A §5; C §1 (6); D §5; F §2 | |
| Immediate, deferred, concurrent | B | §2 |
| Implication, `disable iff`, sampled-value functions | B | §4 |
| `assert` / `assume` / `cover` / `restrict`; assume-guarantee on a bus | B §5; D §3 | |
| `bind` and where assertions live | B §6; D §2 | |
| Clause numbers for every construct | B | §1 |
| **What runs where** (decides every example) | C | §1 to §4, addendum |
| The support matrix to measure | C | §5 (72 probes) |
| One property, two back ends: the macro layer | C §1 (1, 2); D §1 | |
| SymbiYosys modes, engines, `expect`, prep script | C §3, addendum | |
| The Python mirror | E | |
| Worked example: FIFO and AXI, bmc / cover / prove | F | |
| Evidence that assertions find bugs | A | §7 |
| Pitfall catalog | B | §7 |

## Findings that decide the chapter, across the parts

1. **"The same property as checker and as proof obligation" is literally
   true only for clocked booleans with `$past`** (C §1). Open Yosys 0.68
   has no sequence or implication operators in either of its front
   ends: `read_verilog -formal` takes immediate assertions and a bare
   `assert property (expr)`; the bundled sv-elab front end
   (`read_slang`, new since 0.67) takes `assert property (@(posedge clk)
   disable iff (r) <boolean>)` and rejects everything temporal; `|->`,
   `##`, `[*]` are Verific-only (Tabby CAD). The chapter must either
   lower each property by hand for SBY or use a two-bodied macro, as
   OpenTitan does (D §1). **Gate-1 question for the author.**
2. **Verilator's SVA engine is new and the pin matters** (C §1, §2).
   Sequences, repetition, `throughout`/`within`/`intersect` arrived in
   5.048, `s_eventually` and friends in 5.050, `[*N:$]` and `NEVERMATCH`
   in 5.052; 5.054 then fixes `|=>` ("Support non-overlapped property
   implications correctly"), overlapping-attempt multiplicity, bounded
   delays and `disable iff` between ticks. The chapter's commonest
   operator has a correctness fix one release after the pin. This
   strengthens STATUS next-action 3.
3. **Icarus 13.0 is out for concurrent SVA, and silently so under one
   flag** (C §1 (4)): every concurrent assertion is "sorry: not
   supported", and `-gsupported-assertions` drops them without a word.
   The cocotb monitor is what runs on Icarus.
4. **The book's own FIFO bug yields the vacuity example for free**
   (F §2). "When sixteen entries are held, `full` is high" passes on
   Chapter 1's FIFO, in simulation and in an unbounded proof, because the
   design can never hold sixteen; the converse fails with a 15-push
   trace; a cover of occupancy 16 is unreachable. Forward and backward
   assertions are how OpenTitan's FIFO checker is organized (D §4).
5. **The induction-failure example is the checker's own counter**
   (F §3): `occ <= DEPTH` on the fixed FIFO is true, passes BMC, and
   should fail k-induction until `occ == count` is added; SBY's tutorial
   FIFO carries the same helper. Prediction, not measurement.
6. **Theory has primary, openly readable sources for every term the
   design-doc line uses** (A §1): Pnueli 1977, Lamport 1977, Alpern and
   Schneider 1985, Eisner et al. 2003 (weak/strong on truncated paths),
   Beer et al. 2001 and Kupferman and Vardi 1999 (vacuity), Bauer et al.
   (why a finite run decides only safety), Vardi (SVA "is based, in
   essence, on that regular layer").
7. **One measured datum on effectiveness, from 1996** (A §7): assertion
   checkers found 34% of the bugs on the Alpha 21164, the largest single
   mechanism, with the caveat in the paper's own words that a checker
   "can only detect a problem after the test has stimulated a particular
   condition". No controlled study exists; print no other percentage.
8. **Liveness is theory plus a bounded form in this chapter** (C §1 (5)):
   SBY's `live` mode has one engine (`aiger suprove`) the book does not
   have; Verilator refuses `strong(...)` in an assert; SBY deletes
   liveness and cover properties from `bmc`/`prove` runs before solving
   (addendum).
9. **IEEE 1800 clause 16 was not read in any edition** (B). Clause
   numbers are established from three open sources (slang's 2023 table,
   YosysHQ's Property IR table, Verilator's source comments, which
   contradict themselves on two numbers). Every unquoted semantic
   statement in Part B needs the PDF; add clause 16, 20.10 to 20.12 and
   23.11 to the clause sweep.
10. **OpenTitan runs no assertions under Verilator and has no SymbiYosys
    flow** (D §1, §5): its `VERILATOR` branch selects empty macros and
    its FPV runs on two commercial tools. The book's flow is not
    OpenTitan's; OpenTitan is the model for the *methodology* (macros,
    bind files, assert/assume role swap, forward/backward, a "vacuous"
    column in sign-off), not evidence about the open tools.

---

# Part C — What the open tools document about assertions (not measured)

Written first because it decides the shape of every example. Sources are
the tools' own tagged files, read on 2026-11-15: Verilator `v5.052` and
`v5.054` (git clone of the tags), Icarus `v13_0` (`parse.y`,
`Documentation/usage/command_line_flags.rst`), Yosys `v0.68`
(`frontends/verilog/*`, `frontends/verific/verific.cc`, `CHANGELOG`,
`.gitmodules`), sv-elab at the commit Yosys 0.68 pins
(`3dddccd478618d68f8a5e160fb4b5783c4da35d4`, `src/sva.cc`), and SymbiYosys
`v0.68` (`docs/source/*.rst`, `docs/examples/fifo/*`; the `v0.68`
`reference.rst` is byte-identical to `main` on the day it was read).

### 1. Findings that decide the chapter

1. **The one SVA text that all the open tools accept is a clocked
   boolean with `$past`, not a sequence.** Verilator 5.052 has an
   NFA-based engine for sequences and properties (below). Open-source
   Yosys does not: `read_verilog -formal` parses `assert property (expr)`
   with a bare expression only, and the SymbiYosys manual's section
   "SystemVerilog Concurrent Assertions" reads in full "TBD, see
   :ref:`sva`", which points at the page headed "This document describes
   features only available with the commercial Tabby CAD Suite and the
   included Verific frontend"
   [SBY verilog.rst, v0.68](https://github.com/YosysHQ/sby/blob/v0.68/docs/source/verilog.rst);
   [SBY verific.rst, v0.68](https://github.com/YosysHQ/sby/blob/v0.68/docs/source/verific.rst).
   The chapter's promise, "the same property as a simulation checker and
   as a proof obligation", therefore holds literally only for the subset
   in §3 below, or through a macro layer that expands one name two ways,
   which is exactly what OpenTitan's `prim_assert.sv` does (Part D §1).
   **This is a chapter-shape question for gate 1**: either (a) teach full
   SVA on Verilator and prove a restricted, hand-lowered form on SBY,
   saying so, or (b) add the macro layer and make "one property, two
   back ends" the worked example's subject. The note recommends (b)
   with (a)'s honesty: it mirrors industrial practice and it makes the
   lowering of `|=>` to `$past` a thing the reader does once by hand.
2. **Yosys 0.68 ships a second SystemVerilog front end, and it accepts a
   clocked concurrent assertion.** Since 0.67 the changelog says "For
   SystemVerilog support now using sv-elab, built on top of slang
   library" [Yosys CHANGELOG, v0.68](https://github.com/YosysHQ/yosys/blob/v0.68/CHANGELOG),
   `frontends/slang/lib` is a submodule of `povik/sv-elab`, and the build
   option is `YOSYS_WITHOUT_SLANG` (default OFF). sv-elab's `sva.cc`
   lowers `assert|assume|cover property (@(posedge|negedge clk)
   [disable iff (c)] <boolean>)` to a `$check` cell; anything that is not
   a "simple assertion expression" is `UnsupportedSVAFeature`, a
   repetition is `RepetitionsUnsupported`, a both-edges clock and a
   clock `iff` are rejected, and `$past(expr[, n])` is implemented
   (first two arguments only)
   [sv-elab src/sva.cc at 3dddccd](https://github.com/povik/sv-elab/blob/3dddccd478618d68f8a5e160fb4b5783c4da35d4/src/sva.cc).
   So `|->`, `|=>`, `##` and `[*]` are refused there too, but
   `assert property (@(posedge clk) disable iff (!rst_n) !(full &&
   empty));` is one line that Verilator simulates and `read_slang` can
   hand to SBY. `read -sv` and `read -formal` still dispatch to
   `read_verilog` in a non-Verific build (`verific.cc`, `ReadPass`), so
   the SBY script must call `read_slang` by name. **Whether the author's
   brew Yosys 0.68 and the CI source build include `read_slang` is not
   known and is probe 0.**
3. **Verilator's SVA engine is new, moving fast, and the pin matters
   more here than in any earlier chapter.** `##` delays, `[*N]`,
   `[->N]`, `[=N]`, `throughout`, `within`, `intersect`, `first_match`,
   named sequences and property-local variables all arrived in 5.048
   (2026-04-26); `s_eventually`, `always[m:n]`, `until` family,
   `accept_on`/`reject_on`, `#-#`/`#=#`, property `if`/`case`,
   `cover sequence` and `default disable iff` on properties in 5.050
   (2026-07-01); `[*N:$]`, `weak`/`strong` keywords, `s_until` and the
   `NEVERMATCH` warning in 5.052 (2026-09-05). 5.054 (2026-11-01) then
   lists "Support non-overlapped property implications correctly
   (#8268)", "Support multiplicity in SVA shapes that use NFA rings
   (#8267)", "Fix disable iff not aborting pending SVA attempts between
   clock ticks (#8733)", "Fix NFA rings for bounded SVA delays (#8371)"
   and "Fix crash on nonconsecutive repetition in implication
   consequent (#8612)"
   [Verilator Changes, v5.054](https://github.com/verilator/verilator/blob/v5.054/Changes).
   The #8268 commit (cd2475fb, 2026-09-07) is a one-line change that
   makes a non-overlapped implication count as a multi-cycle property,
   with a regression test that requires `a |=> b` and `a |-> ##1 b` to
   produce equal pass and fail counts. **So on 5.052 `|=>` is a prime
   suspect for a silent wrong result** (pass-action counts at least;
   whether a failure is missed is for the probe). This reopens STATUS
   next-action 3 (the Verilator pin) with a stronger reason than
   Chapter 8 gave: the chapter's most-used operator has a correctness
   fix one release after the pin.
4. **Icarus 13.0 runs simple immediate assertions and nothing else.**
   Its grammar's `property_expr` is a plain `expression`; every
   concurrent assertion is `sorry: concurrent_assertion_item not
   supported. Try -gno-assertions or -gsupported-assertions to turn this
   message off`, deferred immediates (`assert #0`, `assert final`) are
   `sorry: Deferred assertions are not supported`, and an immediate
   `cover` is dropped under the comment "Coverage collection is not
   currently supported"
   [Icarus parse.y, v13_0](https://github.com/steveicarus/iverilog/blob/v13_0/parse.y);
   [command_line_flags.rst, v13_0](https://github.com/steveicarus/iverilog/blob/v13_0/Documentation/usage/command_line_flags.rst).
   `-gsupported-assertions` makes Icarus *silently skip* every
   concurrent assertion: a testbench that "passes on Icarus" under that
   flag has checked none of them. That is a Pitfall with a sourced
   mechanism. The chapter is Verilator-only for concurrent SVA, as
   Chapter 8 was for covergroups; the cocotb monitor (Part E) is what
   runs on Icarus.
5. **Liveness in the open flow is narrow and needs a solver the book
   does not have.** SBY's `live` mode has exactly one engine, `aiger
   suprove`; the native front end accepts `assert property (eventually
   expr)` / `s_eventually`; the manual's "Liveness and Fairness" section
   is "TBD" [SBY reference.rst and verilog.rst, v0.68]. `suprove` is in
   the OSS CAD Suite binaries, not in brew Yosys. Verilator 5.052
   supports `s_eventually` in simulation but rejects `strong(...)` in an
   `assert`/`assume` ("Unsupported: strong property in assert") and a
   cycle delay inside `s_eventually`. The chapter should teach liveness
   as theory, show the bounded form (`req |-> ##[1:N] gnt`) as the
   practical one on both back ends, and treat an unbounded `live` run as
   optional or as Chapter 18's.
6. **A cover is the open flow's vacuity check, and SBY documents the
   semantics exactly.** `mode cover` passes when every `cover()` is
   reached within `depth` and fails if one is not, or if "an assertion
   needs to be broken in order to reach the covered state" [SBY
   verilog.rst]. Verilator 5.050 fixed "`cover property` of an
   implication counting vacuous matches (#7789)", so on 5.052 a `cover
   property (a |-> b)` should count only non-vacuous matches (probe).
   Neither tool reports vacuity on an `assert` by itself; the reader
   must write the cover.

### 2. Verilator 5.052 (documented)

- **Manual.** The whole of the language manual's section on the subject
  is "Verilator partially supports assertions and assertion-driven
  functional coverage"
  [languages.rst, v5.052](https://github.com/verilator/verilator/blob/v5.052/docs/guide/languages.rst).
  Nothing lists what "partially" means; the list below is from `Changes`,
  the source's `Unsupported:` messages and the regression suite's
  `*_unsup.out` golden files.
- **Flags.** Assertions are on by default since 5.038 ("Change
  `--assert` to be the default; use `--no-assert` for legacy behavior and
  faster runtimes"); `--no-assert` disables all, `--no-assert-case` the
  `unique`/`priority` checks; `--assert-unroll-limit` is "Deprecated and
  has no effect" in 5.052
  [exe_verilator.rst, v5.052](https://github.com/verilator/verilator/blob/v5.052/docs/guide/exe_verilator.rst).
  Runtime: `+verilator+noassert` disables checking,
  `+verilator+assert+lock` (new in 5.052) stops RTL `$assertoff` /
  `$asserton` / `$assertcontrol` from changing it, and
  `+verilator+error+limit+<n>` sets the "number of non-fatal errors
  (e.g. assertion failures) before exiting simulation runtime ...
  Defaults to 1"
  [exe_sim.rst, v5.052](https://github.com/verilator/verilator/blob/v5.052/docs/guide/exe_sim.rst).
  The book's `sv.mk` flags must be checked for `--no-assert` (none
  expected) and the chapter must say that a default failing assertion
  with no action block **stops the run at the first failure**.
- **Failure text.** `V3Assert.cpp` builds the default message as
  `[<time>] %Error: <file>:<line>: Assertion failed in <%m>[: <message>]`
  followed by a stop; the exact printed form is for `run.out`.
  `cover property` hits are counted only under `--coverage-user`
  (Chapter 8's research note, Part C §3.3, measured this on 5.052).
- **Supported, by `Changes` release line** (5.042 to 5.052): simple
  `##N` in properties (5.042); multi-expression sequences, constant
  delays (5.044); `disable iff` with sequences (5.046); `##0`, `##[*]`,
  `##[+]`, `##[M:N]`, `[*N]`, `[*N:M]`, `[+]`, `[*]`, `[->N]`, `[=N]`,
  `and`/`or` in sequences, `intersect`, `throughout`, `within`,
  `first_match`, named sequences, property-local variables and match
  items, `until`/`until_with`, procedural concurrent assertions (simple
  cases) (5.048); `default disable iff` on `assert property`, weak
  `until`, `s_eventually`, `always`/`always[m:n]`/`s_always[m:n]`,
  `#-#`/`#=#`, `[->M:N]`, `accept_on`/`reject_on`, inferred-clock
  procedural assertions, clocking event in a sequence body, property
  `if`/`case`, `s_until`/`s_until_with`, `$assertcontrol`, `cover
  sequence`, variable-length `intersect` (5.050); sequence as event
  control, `[*N:$]`, `weak`/`strong` keywords, overlong `within` as
  never-matching, `NEVERMATCH` (5.052). `default disable iff` and
  `$inferred_disable` date from 5.032; `bind` is long-standing (tests
  `t_bind`, `t_bind2`).
- **Refused in 5.052, from source messages and golden files**
  (`E_UNSUPPORTED` unless noted): `[=M:N]` ranged nonconsecutive
  repetition; a multi-cycle sequence inside `[*...]`; zero repetition
  count; `strong(...)` in `assert`/`assume`; cycle delay inside
  `s_eventually`; `nexttime`, `s_nexttime`, `eventually[m:n]`,
  `s_eventually[m:n]`; nested or sequence-operand `until` family;
  multiclocked sequences and properties; a clocking event inside a
  sequence expression; a non-edge clock on a sequence; `intersect` with
  two variable-length operands or a non-boolean operand; `within` with a
  ranged-delay operand; ranged delay in an operand of property `and`;
  a property instance inside a multi-cycle property; property-local
  variable across some constructs; `$past` with the gating-expression or
  clock arguments ("Unsupported: $past expr2 and/or clock arguments");
  `$sampled` inside a `disable iff` condition; `expect`; `bind` with an
  instance list; assertion items in clocking blocks; recursive
  properties (the standard forbids some forms; Verilator refuses all);
  `first_match` with match items; property port `local`, property
  variable default values
  [V3AssertNfa.cpp, V3AssertPre.cpp, verilog.y, test_regress/t/*_unsup.out, v5.052](https://github.com/verilator/verilator/tree/v5.052).
  One message, "Unsupported: Implication with sequence expression as
  antecedent", sits behind a coverage-exclusion marker in
  `V3AssertPre.cpp`, i.e. the maintainers believe it unreachable now
  that the NFA path handles sequence antecedents; probe it.
- **`NEVERMATCH`** (5.052): "Warns that an SVA sequence is statically
  known to never match ... using the sequence as the antecedent of an
  implication causes the implication to pass vacuously"
  [warnings.rst, v5.052](https://github.com/verilator/verilator/blob/v5.052/docs/guide/warnings.rst).
  Under the book's `-Wall` this is a build error: a *static* vacuity
  check the chapter can show beside the dynamic cover.
- **5.054 changes that touch the chapter** (finding 3): `|=>`
  correctness (#8268), NFA-ring multiplicity (#8267: overlapping
  attempts counted once), bounded-delay rings (#8371), `disable iff`
  between clock ticks (#8733; the new test's comment: "A disable
  condition pulsing between clock ticks aborts pending attempts, and its
  value is not sampled (IEEE 1800-2023 16.12)"), nonconsecutive
  repetition in a consequent (#8612), stale expression after
  `s_eventually` (#8614), sampled-value function in `cover sequence`
  (#8682), `$past` of an unpacked array element (#8834), nested property
  instance (#8295), `NOTIMING` for properties needing procedural timing
  (#8613).

### 3. Yosys 0.68 and SymbiYosys 0.68 (documented)

**Native front end (`read_verilog -formal`, what `read -formal` calls
without Verific).** `-formal`: "enable support for SystemVerilog
assertions and some Yosys extensions; replace the implicit -D SYNTHESIS
with -D FORMAL". Also `-noassert`, `-noassume`, `-norestrict`,
`-assume-asserts`, `-assert-assumes`
[verilog_frontend.cc, v0.68](https://github.com/YosysHQ/yosys/blob/v0.68/frontends/verilog/verilog_frontend.cc).
What the grammar accepts
[verilog_parser.y, v0.68](https://github.com/YosysHQ/yosys/blob/v0.68/frontends/verilog/verilog_parser.y):

| Form | Native `read_verilog -formal` |
|---|---|
| `assert(e)`, `assume(e)`, `cover(e)`, `restrict(e)` inside `always @(posedge clk)` or `always @*` | yes (the documented style) |
| labels `name: assert (...)` | yes |
| `assert final (e)` | parsed (keyword accepted in place of `property`) |
| module-level `assert property (e);` `assume property (e);` `cover property (e);` `restrict property (e);` with a bare expression | yes |
| `assert property (eventually e)` / `s_eventually` (both spellings lex to one token) | yes; consumed only by `mode live` |
| `@(posedge clk)` inside `assert property (...)`, `disable iff`, `\|->`, `\|=>`, `##`, `[*]`, `sequence`/`property` declarations with bodies | **no grammar rule**; expected syntax error (probe) |
| `$past(e[, N])`, `$stable`, `$changed`, `$rose`, `$fell` | yes, "only ... within a clocked always block"; `$past` has no initial value, so it is unconstrained in the first cycle |
| `$countones`, `$onehot`, `$onehot0`, `$isunknown`, `$countbits` | yes (`simplify.cc`) |
| `$initstate` | yes (true in the initial state; the usual guard for `$past`) |
| `bind` | parsed since 0.10 ("Added support for parsing the 'bind' construct"); the SBY manual still says `bind` "can also be used when using the Verific front end". Probe. |
| `(* anyconst *)`, `(* anyseq *)`, `(* allconst *)`, `(* allseq *)`, `(* gclk *)` | yes; Yosys extensions, not SystemVerilog |
| `checker ... endchecker`, `rand`/`const` in formal mode | tokens exist; not documented for the native path |

**sv-elab front end (`read_slang`)**: finding 2. Adds clocked concurrent
`assert`/`assume`/`cover property` with `disable iff` over a boolean,
full slang elaboration (so `bind`, packages, interfaces should elaborate;
probe), and `--ignore-assertions`. No temporal operators.

**Verific-only (Tabby CAD Suite), i.e. excluded from the book's flow.**
`default clocking`, `default disable iff`, `property`/`sequence`/`checker`
declarations with arguments, `bind` with deep hierarchical references,
`.triggered`, `##N`, `##[N:M]`, `##[N:$]`, `[*...]`, `[+]`, `or`, `and`,
`throughout`, `intersect`, `within`, `first_match`, `[=...]`, `[->...]`,
`|->`, `|=>`, `not`, `until`/`s_until`/`until_with`/`s_until_with`,
`@(posedge clk iff en)`, `disable iff`. Even there "only a certain set of
patterns are supported for SVA properties" and "properties spanning
multiple different clock domains are currently unsupported"
[SBY verific.rst, v0.68]. The SBY tutorial's FIFO wraps its four
`assert property (@(posedge clk) disable iff (rst) ren |=>
$changed(raddr))`-style properties in `` `ifdef VERIFIC `` and
hand-writes the non-Verific equivalent with a `past_nwen` register "since
[`!$past(wen)`] will always trigger in the first cycle"
[sby docs/examples/fifo/fifo.sv, v0.68](https://github.com/YosysHQ/sby/blob/v0.68/docs/examples/fifo/fifo.sv).
That file is the closest published model for the chapter's worked
example and must not be copied (ISC-licensed; the book writes its own).

**SymbiYosys modes** [reference.rst, v0.68](https://github.com/YosysHQ/sby/blob/v0.68/docs/source/reference.rst):

| Mode | The manual's description |
|---|---|
| `bmc` | "Bounded model check to verify safety properties (`assert(...)` statements)" |
| `prove` | "Unbounded model check to verify safety properties" |
| `live` | "Unbounded model check to verify liveness properties (`assert(s_eventually ...)` statements)" |
| `cover` | "Generate set of shortest traces required to reach all cover() statements" |
| `prep` | prepare and write the model, no solver |

Options the chapter will use: `depth` (default 20; in `prove` it is "Depth
for the k-induction performed by the `smtbmc` engine. Other engines ignore
this option in `prove` mode"), `expect` (comma list of `pass`, `fail`,
`unknown`, `error`, `timeout`; "Unexpected results yield a nonzero return
code"; this is the book's `EXPECT := fail` for SBY), `multiclock`,
`append`, `vcd`, `cover_assert`, `timeout`. Tasks (`[tasks]`) let one
`.sby` hold the bmc, prove and cover runs.

**Engines by mode**: `bmc`: `smtbmc` (any solver), `btor btormc|pono|rIC3`,
`abc bmc3`, `abc sim3`, `aiger aigbmc|rIC3`. `prove`: `smtbmc`,
`abc pdr`, `aiger avy|suprove|rIC3`, `btor rIC3`. `cover`: `smtbmc`,
`btor btormc`. `live`: `aiger suprove` only. `smtbmc` solvers: yices,
boolector, bitwuzla, z3, mathsat, cvc4, cvc5. `abc pdr` takes
`--keep-going` for per-property results; in `prove` mode smtbmc's
`--keep-going` is not supported. An `itp` engine (interpolation, external
`itp-bmc`) is listed for `prove`/`bmc` and "does not currently produce
counterexample witness traces". The install page calls Boolector
"recommended to install but not required"; the tutorial `.sby` uses
`smtbmc boolector`. **The book has z3 (in `dvbook`) and Yosys's bundled
ABC, so `smtbmc z3` for bmc/prove/cover and `abc pdr` for the
"needs-no-helper-invariant" contrast are the two engines available with
no new install; the default engine when `[engines]` is omitted was not
found in the manual (probe: the log names it).**

**What a failed induction looks like, per the manual**: in `prove` mode
"the proof may also yield an UNKNOWN result if an assertion can be made
to fail during the induction step" [verilog.rst]. That sentence is the
sourced anchor for the worked example's helper-invariant step.

### 4. Icarus Verilog 13.0 (documented)

Finding 4. `-g` flags: "assertions/supported-assertions/no-assertions:
Enable or disable SystemVerilog assertions. When enabled, assertion
statements are elaborated. When disabled, assertion statements are parsed
but ignored. The supported-assertions option only enables assertions that
are currently supported by the compiler." A simple immediate `assert (e)
[stmt] [else stmt]` is lowered to an `if` whose default else is `$error`;
`assume (e)` shares the rule. A concurrent assertion whose body is more
than an expression (anything with `|->` or `##`) cannot match
`property_expr: expression` and is reported as "error: Error in
property_spec of concurrent assertion item" (expected; probe), which
`-gno-assertions` may not silence because it is a parse error, not a
`sorry`. `bind` is a reserved token with no grammar rule.

### 5. Candidate probe list for the support matrix (one construct each)

Columns to measure: **V52** Verilator 5.052 (`--binary --assert`, the
book's `-Wall` set, one passing and one failing stimulus per probe so a
silently ignored assertion shows as a missed failure), **V54** Verilator
5.054 for the rows marked †, **IV** Icarus 13.0 (`-g2012`, then
`-gsupported-assertions`), **YN** Yosys native via `sby` (`read -formal`),
**YS** Yosys `read_slang` via `sby`. Verdicts as in Chapter 8: runs and
right / runs and wrong / no build, with the message.

| # | Probe | Construct | Why it is on the list |
|---|---|---|---|
| p00 | toolchain | `yosys -h read_slang`; `sby --version`; default engine with no `[engines]` | decides the YS column and the engines text |
| p01 | imm_assert | `assert (e) else $error` in `always_comb` | baseline, all tools |
| p02 | imm_action | pass and fail action blocks, `$error`/`$fatal`/`$warning` severities, exit code | what "failure" does to the run |
| p03 | imm_glitch | immediate assert in `always_comb` firing on a zero-time glitch | motivates deferred |
| p04 | deferred_0 | `assert #0 (e)` | Icarus "sorry" |
| p05 | deferred_final | `assert final (e)` | Yosys parses `final`; meaning differs |
| p06 | conc_bool | `assert property (@(posedge clk) e)` | the common subset |
| p07 | conc_disable | `... disable iff (!rst_n) e` | common subset with reset |
| p08 | default_clk | `default clocking` + unclocked `assert property (e)` | |
| p09 | default_disable | `default disable iff` | 5.032/5.050 |
| p10 | impl_ov | `a \|-> b` | |
| p11 | impl_nov † | `a \|=> b`, compared against `a \|-> ##1 b`, pass/fail counts and a must-fail stimulus | #8268 |
| p12 | delay_n | `a ##2 b` | |
| p13 | delay_range † | `a ##[1:3] b` | #8371 |
| p14 | delay_unb | `a \|-> ##[1:$] b` (weak: never fails in simulation) | weak/strong Pitfall |
| p15 | rep_cons | `a[*3]` | |
| p16 | rep_range | `a[*1:3] ##1 b` | |
| p17 | rep_unb | `a[*1:$] ##1 b`, `a[+]`, `a[*]` | 5.052 |
| p18 | rep_goto | `a \|-> b[->2]` | |
| p19 | rep_noncons † | `a \|-> b[=2] ##1 c` | #8612 |
| p20 | rep_noncons_rng | `b[=1:2]` | documented unsupported |
| p21 | throughout | `en throughout (a ##2 b)` | |
| p22 | within | `(a ##1 b) within (c ##3 d)` | |
| p23 | intersect | `(a[*1:3]) intersect (b ##2 c)` | varlen limits |
| p24 | seq_and_or | sequence `and`, `or` | |
| p25 | first_match | `first_match(a ##[1:3] b) \|-> c` | |
| p26 | named_seq | `sequence ... endsequence` with arguments | |
| p27 | named_prop | `property ... endproperty` with arguments, instantiated twice | |
| p28 | local_var | property-local variable carrying data (`(v, x = d) ##3 q == x`) | FIFO data ordering |
| p29 | not_prop | `not (a ##1 b)` | |
| p30 | past1 | `$past(x)` first-cycle value in each tool | X / 0 / unconstrained |
| p31 | past_n | `$past(x, 3)` | |
| p32 | past_gate | `$past(x, 1, en)` | documented unsupported in V52 and sv-elab |
| p33 | rose_fell | `$rose`, `$fell` on 1-bit and on a vector (LSB rule) | |
| p34 | stable_changed | `$stable`, `$changed` | |
| p35 | sampled | `$sampled(x)` in an action block | action-block race from Chapter 4 |
| p36 | onehot | `$onehot`, `$onehot0`, `$countones`, `$isunknown` | 2-state in Yosys |
| p37 | disable_mid † | `disable iff` asserted mid-attempt, and pulsed between clock edges | #8733, #7792 |
| p38 | disable_sync | reset as an antecedent term instead of `disable iff` | lowRISC-style contrast |
| p39 | s_eventually | `assert property (a \|-> s_eventually b)` at end of simulation | does a pending strong obligation fail at `$finish`? |
| p40 | eventually_yosys | `assert property (eventually e)` under `mode live` | needs `suprove` |
| p41 | strong_kw | `strong(a ##[1:$] b)` | documented unsupported in assert |
| p42 | until | `a until b`, `a s_until b`, `until_with` | |
| p43 | always_rng | `always [2:5] a` | |
| p44 | nexttime | `nexttime a` | documented unsupported |
| p45 | if_else_prop | `if (m) p1 else p2` | |
| p46 | followed_by | `a #=# b` | |
| p47 | assume_sim | `assume property` in simulation (checked like assert?) | |
| p48 | assume_formal | `assume` constraining an input in SBY; over-constraint making an assert vacuous | cover catches it |
| p49 | cover_prop | `cover property (a ##1 b)` hit count, `--coverage-user` | |
| p50 | cover_impl | `cover property (a \|-> b)` with antecedent never true | #7789 |
| p51 | cover_seq | `cover sequence` | 5.050 |
| p52 | nevermatch | antecedent that can never match | `NEVERMATCH` under `-Wall` |
| p53 | vacuous_pass | implication whose antecedent never fires: pass action block runs? | vacuity |
| p54 | restrict | `restrict property` | formal-only statement |
| p55 | bind_mod | `bind fifo fifo_sva u (.*);` | every tool |
| p56 | bind_inst | `bind` to one instance path; `bind` with instance list | documented unsupported in V52 |
| p57 | bind_internal | bound module reading an internal signal (`count`) via port `.*` | white-box access |
| p58 | proc_conc | concurrent assertion inside `always_ff` under `if` | inferred enable |
| p59 | multiclock | property with two clocks | documented unsupported everywhere open |
| p60 | assertctl | `$assertoff`/`$asserton`, `+verilator+noassert`, `+verilator+assert+lock` | |
| p61 | error_limit | two failing assertions, default and `+verilator+error+limit+10` | how many failures a run reports |
| p62 | expect | `expect (...)` | documented unsupported |
| p63 | checker | `checker ... endchecker` | |
| p64 | let | `let` declaration used in a property | SBY example uses it under Verific |
| p65 | anyconst | `(* anyconst *)` in a file Verilator also reads | attribute ignored by simulators? |
| p66 | initstate | `$initstate` guarded by `` `ifdef FORMAL `` | |
| p67 | sby_prove_unknown | a true property that fails induction at `depth 5` | the log text for "UNKNOWN" |
| p68 | sby_pdr | same property under `abc pdr` | proves without the helper? |
| p69 | sby_cover_fail | unreachable cover | log text, exit code, `expect fail` |
| p70 | sby_expect | `expect fail` and the process exit status | fits `EXPECT := fail` |
| p71 | macro_two_way | one `` `ASSERT(name, prop) `` macro expanding to concurrent SVA for Verilator and to a clocked immediate for Yosys | the worked example's mechanism |

72 probes (p00 to p71). The † rows are re-run on 5.054.


---

# Part D — Practice: one set of assertions as checker and as proof obligation

Sources read 2026-11-15: lowRISC/opentitan at commit `0d2b191a` (2026-11-08;
sparse clone of `hw/formal`, `hw/ip/prim`, `hw/ip/tlul`, `hw/ip/uart`,
`hw/ip/dma`, `doc/contributing/dv/methodology`), and lowRISC/style-guides
`master` (`VerilogCodingStyle.md`, `DVCodingStyle.md`).

### 1. OpenTitan's macro layer is the "same property, two back ends" mechanism

`hw/ip/prim/rtl/prim_assert.sv` defines the names; the bodies come from one
of three "implementation headers" chosen by the tool
[prim_assert.sv](https://github.com/lowRISC/opentitan/blob/0d2b191a4a78d4c3fcb487e116eb2e7b54223841/hw/ip/prim/rtl/prim_assert.sv):

```
`ifdef VERILATOR   -> prim_assert_dummy_macros.svh     (every macro empty)
`elsif SYNTHESIS   -> prim_assert_dummy_macros.svh
`elsif YOSYS       -> prim_assert_yosys_macros.svh     (+ `define INC_ASSERT)
`else              -> prim_assert_standard_macros.svh  (+ `define INC_ASSERT)
```

Its own comment: "The macros should do the same thing in each case (except
for the dummy flavour), but in a way that the respective tools support."

| Macro | Standard header (commercial simulators and FPV) | Yosys header |
|---|---|---|
| `ASSERT(name, prop, clk, rst)` | `name: assert property (@(posedge clk) disable iff ((rst) !== '0) (prop)) else` error | `always_ff @(posedge clk) if (!(rst !== '0)) name: assert (prop);` |
| `ASSERT_NEVER` | same with `not (prop)` | `assert (!(prop))` |
| `ASSERT_I` | immediate `assert (prop)` | `always_comb assert (prop)` |
| `ASSERT_INIT` | `initial assert`; under `FPV_ON` an elaboration-time `$fatal` | `initial assert` |
| `ASSERT_FINAL` | `final assert`; empty under `FPV_ON` | empty: "This doesn't make much sense for a formal tool (we never get to the final block!)" |
| `ASSERT_KNOWN(name, sig)` | `ASSERT(name, !$isunknown(sig))`; empty under `FPV_ON` | empty: "Yosys uses 2-state logic, so this doesn't make sense here" |
| `ASSERT_AT_RESET` | `assert property (@(posedge rst) ...)` | empty ("requires an event scheduler, which Yosys may or may not implement") |
| `COVER` | `cover property (@(posedge clk) disable iff (...) (prop))` | `always_ff ... cover ((!(rst !== '0)) && (prop))` |
| `ASSUME` | `assume property (...)` | clocked immediate `assume` |

Derived macros are built on those: `ASSERT_PULSE` (`$rose(sig) |=> !sig`),
`ASSERT_IF` (`enable |-> prop`), `ASSERT_KNOWN_IF`, and FPV-only
`ASSUME_FPV`, `ASSUME_I_FPV`, `COVER_FPV` (bodies exist only under
`` `ifdef FPV_ON ``). The header's rule for the split: "the existing set of
ASSERT macros specified above shall be used for FPV, thereby ensuring that
the assertions are evaluated during DV simulations as well."

Three facts the chapter can use, each read in the files:

1. **The Yosys expansion cannot carry a temporal operator.** The Yosys
   `ASSERT` puts `prop` inside an immediate `assert (...)`, so a call like
   `` `ASSERT(x, req |-> ##2 ack) `` is not valid there. The macro layer
   gives one *name* two bodies; it does not translate sequences. This
   is Part C finding 1 seen from the user's side.
2. **OpenTitan turns its assertions off under Verilator.** `VERILATOR`
   selects the dummy header, and `tlul_assert.sv` wraps its whole body in
   `` `ifndef VERILATOR ``. The file history was not examined, so *why* is
   unsourced (the obvious reading is that the choice predates Verilator's
   5.048 engine). The book's example would be doing something the largest
   open user of SVA does not do; say so, and do not claim OpenTitan
   validates Verilator's SVA.
3. **The reset term is `(rst) !== '0`, not `rst`.** The header's comment:
   "This properly disables the assertion in cases when reset is X at the
   beginning of a simulation. For that case, (reset == '1) does not
   disable the assertion." A two-line Pitfall for 4-state simulators, with
   a named source. (On Verilator, which is 2-state by default, the
   distinction is invisible: probe p37/p38.)

Usage, measured by `grep` at 0d2b191a over `hw/ip/{prim,tlul,uart,dma}/rtl`
only (four directories, not the repository): `` `ASSERT`` 295,
`` `ASSERT_INIT`` 105, `` `ASSERT_KNOWN`` 84, `` `ASSUME`` 30,
`` `ASSERT_I`` 8, `` `ASSUME_FPV`` 7, `` `COVER`` 3, `` `ASSERT_NEVER`` 3,
`` `ASSERT_FINAL`` 1. Prefix-counted (`` `ASSERT`` includes none of the
longer names; the regex took the longest match). The shape, mostly plain
concurrent asserts, then parameter checks, then X checks, is the finding;
the numbers are not a repository total and should not be printed as one.

### 2. Where assertions live, and `bind`

- lowRISC Verilog style: "It is encouraged to use SystemVerilog assertions
  (SVAs) throughout the design to check functional correctness and flag
  invalid conditions", and, in the section on X, "Instead of assigning
  and propagating `X` in order to flag and detect invalid conditions, it
  is encouraged to make **extensive use of SVAs**", with the listed
  benefit that "Simulation fails quickly and less signal backtracking is
  needed to root-cause bugs" and that "formal property verification
  (FPV) can be used to prove whether these SVAs can always be fulfilled"
  [lowRISC Verilog Coding Style, "Assertion Macros" and the X section](https://github.com/lowRISC/style-guides/blob/master/VerilogCodingStyle.md).
  RTL "must place `ASSERT_KNOWN` assertions on all" module outputs (the
  sentence continues in the guide; quote from the file when drafting).
- lowRISC DV style, "SystemVerilog Assertions": "Most, if not all design
  properties are captured as in-line assertions within the RTL itself";
  behaviors "too complex to embed within the RTL" go into "a separate
  SystemVerilog assertion (SVA) module" under five rules: ports "must all
  be inputs only. Since they are passive checkers, they must not drive or
  force internal signals"; use the macros; "Do not instantiate the SVA
  module in the testbench. Instead, `bind` it to the RTL module"; no
  absolute hierarchical paths; bind to "the closest common ancestor RTL
  module"; and "Consolidate all SVA binds in a dedicated bindfile". Also:
  "`bind` statements are the preferred approach for using assertion-based
  monitors"
  [lowRISC DV Coding Style](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).
  The same guide forbids side effects inside `assert()`: "Do not use
  `assert()`" around `randomize()` or a function with side effects,
  because a tool may compile assertions out. That is the Chapter 7
  material and a one-line cross-reference here.
- `hw/formal/README.md`, "Implementation Guidelines": "Basic assertions
  should be implemented directly in the RTL file. These basic functional
  assertions are often inserted by designers to act as a smoke check";
  testbench-goal assertions go under `fpv/vip`; "Portable assertions
  written for common interfaces or submodules ... can be easily reused by
  other testbench via a bind file". Naming: "postfix `_A` for assertions,
  `_M` for assumptions, `_P` for properties, and `_S` for sequences"
  [OpenTitan hw/formal/README.md](https://github.com/lowRISC/opentitan/blob/0d2b191a4a78d4c3fcb487e116eb2e7b54223841/hw/formal/README.md).
- DV methodology: "Wherever possible, the assertion monitors developed for
  FPV are reused in UVM testbenches when running dynamic simulations";
  "in DV assertions are typically created within SV interfaces bound to
  the DUT. This way assertions and any collateral code don't affect the
  design, and can reach any internal design signal if needed"; and for
  coverage, "an assertion precondition counts as a cover point" (already
  `[@opentitan-dv-methodology]` in `refs.bib`).

**A real bind file** (`hw/ip/uart/dv/sva/uart_bind.sv`): a module
`uart_bind` whose body is two `bind uart ...` statements, one of them
`tlul_assert #(.EndpointType("Device")) tlul_assert_device (.clk_i,
.rst_ni, .h2d(tl_i), .d2h(tl_o));`. The FIFO's FPV bind file notes "need
to instantiate by hand since bind statements inside generate blocks are
currently not supported". The chapter writes its own; these are the
models.

### 3. Assert on one side, assume on the other: the protocol checker

`tlul_assert.sv` is one module with a string parameter `EndpointType`.
For `"Host"` every host-to-device rule is `assert property` and every
device-to-host rule is `assume property`; for `"Device"` the roles swap,
under the comments "in this case all signals coming from the device side
have an assumed property" and the converse
[tlul_assert.sv](https://github.com/lowRISC/opentitan/blob/0d2b191a4a78d4c3fcb487e116eb2e7b54223841/hw/ip/tlul/rtl/tlul_assert.sv).
Label suffixes switch with them (`legalAParam_A` / `legalAParam_M`). In
simulation an `assume` is checked like an `assert` (the standard's rule;
Part B); in FPV it constrains the inputs. This is the assume-guarantee
idea in forty lines, on the bus Chapter 11 already cites, and it is the
model for the AXI checker in the worked example: the DMA is an AXI
*master*, so VALID-stability is an `assert` on the DMA's outputs and the
slave's behavior is an `assume`. It also uses `default clocking` and
`default disable iff disable_sva || !rst_ni`, with a testbench-controlled
`disable_sva` bit so error-injection tests can turn the checker off.

### 4. An industrial FIFO property set to compare with the chapter's

`hw/ip/prim/fpv/vip/prim_fifo_sync_assert_fpv.sv` ("Assertions for
prim_fifo_sync. Intended to be used with a formal tool"), 232 lines,
bound by `prim_fifo_sync_bind_fpv.sv` to FIFOs of depth 0, 1, 7, 8, 15,
16 in pass-through and non-pass-through form. What it checks, in the
file's own grouping:

- **Assumption (data abstraction)**: `` `ASSUME(WdataValues_M, wdata_i
  inside {0, 1, all-ones}) `` under "no need to consider all possible
  input words; 2-3 different values suffice".
- **Reference model**: a small behavioral FIFO in the checker, then
  `DataCheck_A: rvalid_o |-> rdata_o == ref_rdata` and `DepthCheck_A`.
  Data ordering is proved against a model, not written as a temporal
  formula, and the parameter comment says the data check "can be
  disabled for deeper FIFOs".
- **Forward assertions** (cause to effect): `FullIffFullDepth_A:
  (depth_o == Depth) <-> (full_o)`; `Depth_A: depth_o <= Depth`;
  `WriteFull_A`, `ReadEmpty_A`, `WriteOnly_A`, `ReadOnly_A` as `|=>` with
  `$past(depth_o)`.
- **Backward assertions** (effect to cause): `wready_o |-> depth_o <
  Depth || rready_i`, `rvalid_o |-> depth_o > 0 || wvalid_i`.

`FullIffFullDepth_A` is, word for word in intent, the property that
catches Chapter 1's bug (`full` raised at 15 of 16). The
forward/backward split is a reusable teaching device: a forward property
alone passes on a design that also does the thing at other times.

### 5. OpenTitan's FPV flow, and what it shows about vacuity

`dvsim` drives JasperGold or VC Formal (`hw/formal/tools/{jaspergold,
vcformal,dvsim,csr_assert_gen}`); there is no SymbiYosys flow in
`hw/formal`, and the Yosys macro header is the only trace of an open
formal path. Per the README, the tool "will then report which assertions
have been proven or disproven, and whether or not there are any
unreachable assertions or coverpoints", and the batch report "lists the
total number of assertions and the number of proven, vacuous, covered and
failing assertions for each block". *Vacuous* and *covered* are columns
of the sign-off report. The security flow ("FpvSecCm") proves that a
countermeasure's error output raises an alert by injecting the fault
with `stopat` and black-boxing, because those assertions "are expected
to be unreachable in normal design environment": an industrial case of
an assertion that is vacuous by construction until the environment is
changed. (Vendor tool names appear as OpenTitan's choices, not as
recommendations.)

### 6. Evidence on assertion effectiveness

See Part A §7 (appended later in this file) for the papers; none is
OpenTitan's. OpenTitan publishes no bug-per-assertion data in the files
read.


---

# Part A — Theory: what a temporal property is

Every source in this part was fetched and read on 2026-11-15 through a
fetch tool that returns extracted text; where the PDF's text layer was
OCR, formulas came back garbled and are paraphrased, and the prose
quotations are as returned. **Quotations marked † must be re-read in the
PDF before they are printed**, because the extraction tool splits and
sometimes trims long sentences.

### 1. Findings that decide the chapter

1. **Safety and liveness have one-sentence primary definitions, and the
   chapter should quote Lamport and build on Alpern and Schneider.**
   Lamport 1977: "A safety property is one which states that something
   will not happen" and "A liveness property is one which states that
   something must happen" †. Alpern and Schneider 1985 give the formal
   split: a property is *safety* when every execution that violates it has
   a finite prefix no extension of which satisfies it, *liveness* when
   every finite partial execution can be extended to one that satisfies
   it, and "Theorem 1. Every property P is the intersection of a safety
   property and a liveness property." They credit the terms: "Safety and
   liveness were first described in [2]", Lamport's paper.
2. **The reason simulation can refute a safety property and can never
   confirm or refute a liveness property is a theorem, not folklore.**
   A simulation is a finite prefix. Bauer, Leucker and Schallhart give a
   monitor three verdicts over a finite prefix: true if every
   continuation satisfies the formula (a *good prefix*), false if none
   does (a *bad prefix*), and inconclusive otherwise; for "infinitely
   often p" they note "Any finite word can be extended to an infinite one
   satisfying the formula as well as to one falsifying the formula", so
   no finite run decides it. This is the sourced backbone of the
   chapter's "checker versus proof obligation" contrast: the simulator
   reports bad prefixes of safety properties; only the model checker
   says "holds".
3. **What a simulator does with an obligation still pending at the end of
   the trace is a design decision with a name: the weak, neutral and
   strong views of a truncated path** (Eisner, Fisman, Havlicek, Lustig,
   McIsaac and Van Campenhout, CAV 2003). "Truncated paths arise
   naturally in incomplete verification methods such as simulation or
   bounded model checking"; "We term a decision to return true when
   there is doubt the weak view" and "a decision to return false when
   there is doubt the strong view"; "in the weak view the formula Fp
   holds for any finite path". SVA's `weak`/`strong` sequence operators
   and the `s_` prefix on `s_eventually`, `s_until`, `s_always`,
   `s_nexttime` are this distinction in syntax, and the same paper ties
   it to reset: "we tend to think of a reset as somehow cutting the path
   into two disjoint parts", which is what `disable iff` does. Two of
   the six authors (Havlicek, and Fisman on PSL) worked on the standards.
4. **SVA's lineage is regular expressions first, temporal logic second,
   and Vardi's history says so in a sentence.** Pnueli 1977 proposed
   temporal logic for programs ("A unified approach to program
   verification is suggested ... The main proof method suggested is that
   of temporal reasoning in which the time dependence of events is the
   basic concept" †); plain LTL is strictly weaker than the regular
   properties, which led to Wolper's ETL and then to industrial languages
   that add regular expressions: Intel's ForSpec (LTL plus "dynamic"
   regular modalities, clocks and resets), IBM's Sugar, and Accellera's
   PSL, which Vardi describes as "LTL, extended with dynamic modalities
   (referred to as the regular layer), clocks, and resets (called
   aborts)". SVA "is based, in essence, on that regular layer" †
   (Vardi, "From Church and Prior to PSL"). That is the chapter's
   organizing idea in a citable form: a *sequence* is a regular
   expression over cycles; a *property* wraps sequences in a small set of
   temporal operators (implication, `always`, `until`, `eventually`,
   added in the 2009 revision).
5. **Vacuity has a primary definition, a primary number, and a named
   precursor.** Beer, Ben-David, Eisner and Rodeh (FMSD 2001; conference
   version CAV 1997): "The problem of a trivially valid formula was first
   noted by Beatty and Bryant, who termed it antecedent failure"; their
   Definition 2, "Formula ϕ is vacuous in model M if there is a
   sub-formula ψ of ϕ such that ψ does not affect ϕ in M"; an
   *interesting witness* is "a trace which shows a non-trivial example of
   the validity of a formula"; and, from IBM's experience, "typically 20%
   of formulas are found to be trivially valid" in the first formal runs
   on a new design †. Kupferman and Vardi (CHARME 1999) generalize: ψ
   "does not affect" ϕ in M when replacing ψ by any formula leaves the
   verdict unchanged, and they report IBM's experience that "vacuous
   passes always point to a real problem in either the design or its
   specification or environment" †. An SVA `cover` on the antecedent is
   the practitioner's interesting witness. The 20% is an experience
   report from one company's 1990s flow, to be printed as that.

### 2. LTL in the amount the chapter needs

Pnueli's paper defines two property kinds by name, *invariance* ("a
property holding throughout all states of all possible execution
sequences") and *eventuality*, and introduces the unary operators F and
G, glossing G(p ⊃ Fq) as "Whenever p is true, it will eventually be
followed by a state in which q will be true" †. The words "safety" and
"liveness" both occur in it (liveness "termed liveness in [16]"), so the
chapter must not say Pnueli lacked the terms; Lamport's paper is from the
same year. The paper is about programs, not circuits.

For the chapter: X (next), G (always), F (eventually), U (until) over an
infinite sequence of states; `req |-> ##[1:$] gnt` under an implicit
`always` is G(req → F gnt) only in the strong reading (finding 3).
The mapping table the chapter needs (the SVA column is this note's
reading of clause 16, **not read in the standard**; see Part B):

| LTL | SVA property form | Class |
|---|---|---|
| G p | `assert property (@(posedge clk) p)` (the assertion statement supplies the outer always) | safety |
| G (a → X b) | `a \|=> b` | safety |
| G (a → b) | `a \|-> b` | safety |
| G (a → F b) | `a \|-> s_eventually b` or `a \|-> strong(##[0:$] b)` | liveness |
| G (a → (b U c)) | `a \|-> b s_until c` | liveness (the U); `until` is the weak form (W) and is safety |
| G (a → F≤n b) | `a \|-> ##[0:n] b` | safety (bounded liveness) |
| regular, not LTL: "p at every even cycle" | `(1 ##1 1)[*] ##1 p`-style repetition | needs the regular layer |

The last row is the reason for sequences. *The note did not find the
even-cycle example in Vardi's text* (the fetch reported it under the
section on Church, as a monadic second-order formula); Wolper's 1983
paper "Temporal logic can be more expressive" is the primary source and
was not fetched. Cite Vardi for "LTL is strictly weaker than the regular
properties" and leave the example unattributed or find Wolper.

Bounded liveness is the practical point: a liveness property with a
bound is a safety property (its violation is a finite prefix), so it can
be simulated, bounded-model-checked and proved by induction. The
Alpern-Schneider definitions make that a two-line argument the chapter
can give in its own words.

### 3. Sequences as regular expressions

No fetched source defines SERE (the PSL term, "sequential extended
regular expression") in a quotable sentence; Vardi's text calls it "the
regular layer". The chapter can state the correspondence itself and cite
Vardi for the lineage: concatenation is `##1`, fusion (overlap of one
cycle) is `##0`, union is `or`, Kleene star is `[*]`, bounded repetition
is `[*m:n]`, and the non-regular-expression operators (`intersect`,
`and`, `within`, `throughout`, `first_match`) are still regular because
regular languages are closed under intersection. `[->n]` and `[=n]` are
sugar: `b[->1]` is `(!b)[*] ##1 b`. An NFA is the natural implementation,
which is what Verilator's source calls its engine (`V3AssertNfa.cpp`).
The primary complexity and automata-construction papers (Bustan and
Havlicek, CAV 2006; Armoni et al., TACAS 2002 for ForSpec) were not
fetched; they belong in further reading only if the author reads them.

### 4. Weak, strong, and the end of simulation

From finding 3. What the chapter can say with the sources read: a
*weak* obligation that is still pending when the trace ends is counted as
satisfied; a *strong* one is counted as failed. SVA sequences used as
properties are weak by default in `assert` (so `a |-> ##[1:$] b` never
fails in simulation however long `b` stays low; this is Sutherland's and
every trainer's gotcha, and the note's reading of the standard, not a
quotation), and the `s_` operators are strong. Verilator's source cites
the strong reading directly, "a liveness failure (IEEE 1800-2023
16.12.11 strong semantics)", and its 5.052 refuses `strong(...)` in an
assert (Part C §2). Whether Verilator reports a pending `s_eventually`
as a failure at `$finish` is probe p39; the 5.052 `Changes` line "Fix
$past in final blocks on a sampling-tick finish" shows end-of-simulation
semantics were being worked on in that release.

### 5. Vacuity

From finding 5. Three levels for the chapter, each with its source:

- *Antecedent failure* (Beatty and Bryant, via Beer et al.): `a |-> b`
  where `a` never happens. The example in Beer et al. is AG(request →
  AX ack) in a model where no request is ever made.
- *Vacuity in general* (Beer et al. Definition 2; Kupferman and Vardi):
  some subformula can be replaced by anything without changing the
  verdict. An over-constrained environment (`assume`) is the common
  industrial cause; OpenTitan's FPV report has a "vacuous" column (Part D
  §5).
- *Detection*: Beer et al. generate an interesting witness; in SVA
  practice a `cover property` on the antecedent (or on the whole
  sequence) is that witness, and SBY's `cover` mode produces it as a
  trace. IEEE 1800 has a notion of nonvacuous evaluation (clause 16.14.8
  "Nonvacuous evaluations" per the YosysHQ table in Part B; text not
  read) and system tasks `$assertvacuousoff`, `$assertnonvacuouson`
  (clause 20.11 region; names from the same table and from memory, to be
  confirmed).

Purandare and Somenzi (CAV 2002, "Vacuum Cleaning CTL Formulae") is the
follow-up that calls Beer et al. "the seminal paper"; abstract read only.

### 6. What was not found

- An openly readable copy of IEEE 1800 clause 16 or Annex F (formal
  semantics): the two public PDFs the Chapter 8 note used refuse
  automated fetches, and the 3.1a LRM copy at Southampton truncates
  before Section 17 in extraction. See Part B.
- The CAV 1997 paper of Beer et al. (only the journal version was read).
- Wolper 1983; Bustan and Havlicek 2006; Armoni et al. 2002; Kupferman
  and Vardi's "Model checking of safety properties" (2001), which is the
  usual citation for *bad prefix*. Bauer et al. define the term and were
  read, so the chapter can cite them.

### 7. Measured evidence on assertion effectiveness

- **Kantrowitz and Noack, DAC 1996** (DECchip 21164 Alpha). Figure 2,
  "Effectiveness of Bug Detection Mechanisms": assertion checkers 34%,
  self-checking test 11%, cache coherency checkers 9%, register file
  trace compare 8%, memory state compare 7%, manual inspection 7%,
  end-of-run state compare 6%, simulation hang 6%, PC trace compare 4%,
  other 8%. "As can be seen, the assertion checkers were the most
  effective techniques." Also: "The team continually added new checkers
  to the model, since this was a very effective bug-finding mechanism",
  and the limit that decides this chapter's link to Chapter 8: "In all
  cases, the assertion checkers can only detect a problem after the test
  has stimulated a particular condition." † The total bug count was not
  in the extracted text. These were hand-coded checkers in a C/behavioral
  environment, a decade before SVA; the figure is evidence for
  *assertions as a technique*, not for SVA.
- **Taylor et al., DAC 1998** (Alpha 21264; DOI 10.1145/277044.277208,
  pp. 638-643) is the usual companion citation. **Not read**: only the
  bibliographic record was fetched. The figure commonly attached to it
  must not be printed until the paper is read.
- **Foster's Wilson Research Group studies** (in `refs.bib`) report
  assertion *adoption*, not effectiveness. The chapter may cite adoption
  from the edition already in `refs.bib`; this note did not re-read them.
- No controlled study comparing bug yield with and without assertions on
  the same design was found. Same conclusion as Chapter 8's note reached
  for coverage: attach no percentage to the benefit beyond the DEC
  figure, labelled with its year and method.
- Sutherland (SNUG 2015) and Cummings (2016) give no measurements; both
  say so implicitly by offering experience only. Cummings' log-volume
  example (400 lines of messages for 2 errors across 100 flip-flops
  under an `$error`-per-assertion style) is an illustration, not data.


---

# Part B — The assertion language (IEEE 1800 clause 16), from open material

**Clause 16 was not read in any edition.** IEEE 1800-2023 cannot be
downloaded here; the public copies of 1800-2012 and 1800-2017 that the
Chapter 8 note used (UAH, MIT 6.205) return `robots_disallowed` to this
session's fetch tool and are blocked for `curl`; the Accellera 3.1a LRM
at Southampton extracts only to Section 3.10. What follows is assembled
from open material that *cites* the clause structure, plus practitioner
papers. Every semantic statement in §2 to §6 that is not inside
quotation marks is this note's reading and **must be confirmed against
the PDF in the clause sweep (STATUS next-action 2), which should now
include clause 16, 20.10 to 20.12, 23.11 and Annex F.**

### 1. Clause numbers that can be established without the PDF

Three independent open sources give clause numbers:

- **S** slang's language-support table, which "has complete support for
  the entirety of the IEEE 1800-2023 SystemVerilog language" and lists
  the clauses by number and title
  [slang docs/language-support.dox, master, read 2026-11-15](https://github.com/MikePopoloski/slang/blob/master/docs/language-support.dox).
- **Y** YosysHQ's "Property IR" documentation, "SVA Table", which maps
  each SVA construct to a clause number, title and page (edition not
  stated on the page; the Annex F page numbers near 1235 to 1247 suggest
  a recent edition)
  [YosysHQ Property IR, SVA table, read 2026-11-15](https://yosyshq.readthedocs.io/projects/property-ir/en/latest/sva_table.html).
- **V** Verilator's source comments and error messages, which cite "IEEE
  1800-2023 x.y.z" [verilator v5.052 and v5.054 `src/`]. These are
  programmers' comments and are **not self-consistent**: `not` is cited
  as both 16.12.1 and 16.12.3, and implication as 16.12.6 in 5.052 and
  16.12.7 in 5.054 (the #8268 commit changed the comment). Where V
  disagrees with Y, Y is taken.
- **C** a page on systemverilog.us (Ben Cohen's site; author not named
  on the page) quoting 1800-2023 text for 16.7, 16.9.2.1 and 16.12.22.

| Construct | Clause | Title as given by the source | Source |
|---|---|---|---|
| Immediate assertions | 16.3 | Immediate assertions | S |
| Deferred assertions (`#0`, `final`) | 16.4 | Deferred assertions | S, V ("Deferred assertions must use '#0' (IEEE 1800-2023 16.4)") |
| Concurrent assertions, sampling | 16.5 | Concurrent assertions overview | S |
| Boolean expressions in assertions | 16.6 | Boolean expressions | S |
| `##` delays, sequence syntax | 16.7 | Sequences | S, Y (pp. 399-401), C |
| `sequence ... endsequence` | 16.8 | Declaring sequences | S, Y (p. 402) |
| Sequence operators | 16.9 | Sequence operations | S |
| `[*]`, `[->]`, `[=]` | 16.9.2 | Repetition in sequences | Y (p. 410), V; C cites 16.9.2.1 "Repetition, concatenation, and empty matches" |
| `$past`, `$rose`, `$fell`, `$stable`, `$changed`, `$sampled` | 16.9.3 | (Sampled value functions; title from memory) | V ("$past tick value must be >= 1 (IEEE 1800-2023 16.9.3)") |
| `$future_gclk`, global-clock sampled functions | 16.9.4 | — | Y (p. 418), V |
| sequence `and` | 16.9.5 | AND operation | Y (p. 421), V |
| `intersect` | 16.9.6 | Intersection | Y (p. 423), V, Verilator `warnings.rst` |
| sequence `or` | 16.9.7 | OR operation | Y (p. 424), V |
| `first_match` | 16.9.8 | First_match operation | Y (p. 427) |
| `throughout` | 16.9.9 | Conditions over sequences | Y (p. 428), V |
| `within` | 16.9.10 | Sequence contained within another sequence | Y (p. 430), V |
| property-local variables | 16.10 | Local variables | S, V |
| subroutine on match | 16.11 | Calling subroutines on match of sequence | S |
| `property ... endproperty`, `disable iff` in a property spec | 16.12 | Declaring properties | S, Y (pp. 439, 441) |
| sequence used as property, `strong`/`weak` | 16.12.2, 16.12.15 | Sequence property; Weak and strong operators | Y (pp. 443, 458) |
| property `not` | 16.12.3 | Negation property | Y (p. 444) |
| property `or`, `and` | 16.12.4, 16.12.5 | Disjunction property; Conjunction property | Y |
| property `if`/`else`, `case` | 16.12.6, 16.12.16 | If-else property; Case | Y |
| `\|->`, `\|=>` | 16.12.7 | Implication | Y (p. 445), V in 5.054 |
| `implies`, `iff` | 16.12.8 or 16.12.9 | Implies and iff properties | Y prints 16.12.9 for both this and followed-by; one of the two is a typo. **Unresolved.** |
| `#-#`, `#=#` | 16.12.9 | Followed-by property | Y, V |
| `nexttime`, `s_nexttime` | 16.12.10 | Nexttime property | Y (p. 450) |
| `always`, `s_always` | 16.12.11 | Always property | Y (p. 452), V |
| `until` family | 16.12.12 | Until property | Y (p. 453), V |
| `eventually`, `s_eventually` | 16.12.13 | Eventually property | Y (p. 454) |
| `accept_on`, `reject_on`, `sync_` forms | 16.12.14 | Abort properties | Y, V |
| recursive properties | 16.12.17 | Recursive properties | Y (p. 459) |
| degenerate antecedents | 16.12.22 | Nondegeneracy | S, C |
| multiclock | 16.13 | Multiclock support | S |
| `assert property` | 16.14.1 | Assert statement | Y (p. 476) |
| `assume property` | 16.14.2 | Assume statement | Y (p. 477) |
| `cover property`, `cover sequence` | 16.14.3 | Cover statement | Y (p. 479), V |
| `restrict property` | 16.14.4 | Restrict statement | Y (p. 480) |
| concurrent assertion in procedural code | 16.14.6 | (Embedding concurrent assertions in procedural code; title from memory) | Y (p. 481), V |
| `$inferred_clock`, `$inferred_disable` | 16.14.7 | Inferred value functions | S |
| vacuity bookkeeping | 16.14.8 | Nonvacuous evaluations | Y |
| `default disable iff` | 16.15 | Disable iff resolution | S, V |
| `default clocking` use by assertions, clock inference | 16.16 (and 14.12 Default clocking) | Clock resolution | S, V ("Concurrent assertion has no clock (IEEE 1800-2023 16.16)") |
| `expect` | 16.17 | Expect statement | S |
| `$error`, `$fatal`, `$warning`, `$info` | 20.10 | Severity tasks | S |
| `$asserton`, `$assertoff`, `$assertkill`, `$assertcontrol` | 20.11 | Assertion control tasks | S, V, Y |
| sampled value system functions (the function list) | 20.12 | Sampled value system functions | S |
| `bind` | 23.11 | Binding auxiliary code to scopes or instances | S |
| regions (Preponed sampling, Observed evaluation, Reactive action blocks) | 4.4 | (Chapter 4 of the book cites Cummings and Salz; clause title not established here) | — |
| formal semantics | Annex F (F.3.1, F.3.4.4, F.5.3.1 "Neutral satisfaction", F.5.3.3 "Vacuity") | — | Y |

The chapter may print a second-level clause number from column S with
confidence that it is the 2023 number. Third-level numbers are from Y,
whose edition is unstated; print them only after the PDF confirms them.

### 2. Three kinds of assertion

*Immediate* (16.3). Sutherland: an immediate assertion "executes in zero
simulation time", like an `if`, with an optional pass statement and an
automatic error when there is no `else`
[Sutherland, SNUG 2015](https://sutherland-hdl.com/papers/2015-SNUG-SV_SVA-for-RTL-Designers_paper.pdf) †.
The glitch problem: "A combinational RTL procedure can trigger multiple
times within a moment of simulation time", so an immediate assert in
`always_comb` "might have seen more than one bit set, and reported a
false assertion failure" †. OpenTitan's header says the same in one
line: "immediate assertions are sensitive to simulation glitches".

*Deferred* (16.4), `assert #0 (e)` and `assert final (e)`. Sutherland:
`assert final` defers the action "until the activity in the current
simulation time is stable"; `assert #0` "can still result in an assertion
glitches" †; "The assert final construct is the preferred construct" for
immediate checks in combinational RTL †. (Reading, to confirm: `#0`
matures in the Observed region and can be flushed and re-fired if the
Reactive region re-triggers the Active set; `final` matures in
Postponed. Verilator's parser names them `OBSERVED_DEFERRED_IMMEDIATE`
and `FINAL_DEFERRED_IMMEDIATE`, which supports the reading.) Icarus
refuses both forms.

*Concurrent* (16.5). Sutherland: "Concurrent assertions only sample
values on their specified clock edge" and "cannot evaluate or execute
between clock cycles"; a new evaluation attempt starts every clock
tick †. Chapter 4 of the book already states the region model (sampled
in Preponed, evaluated in Observed, action block in Reactive) with
`[@cummingssalz2007events]` and `[@bromley2012clocking]`; this chapter
should point back with `@sec-` references rather than restate it, and
add the one consequence Chapter 4 leaves for here: `$display` of a
signal in an action block prints the *current* value, not the sampled
one that failed the property, unless `$sampled()` is used (reading;
probe p35).

The teams disagree on who uses which, and the chapter can show the
disagreement because both positions are published. Sutherland: designers
"should embed assertions directly within RTL modules", and immediate
assertions are "the most useful for design engineers". Cummings:
"Use concurrent assertions - avoid immediate assertions" (his guideline
9), "Inline SVA code - avoid it!" (guideline 3), bind instead
[Cummings, "SystemVerilog Assertions - Bindfiles & Best Known Practices for Simple SVA Usage", DVCon-hosted slides](https://dvcon-proceedings.org/wp-content/uploads/SW_5A_2_SVA_BindFiles.pdf) †.
lowRISC: most properties in-line in the RTL, complex ones in a bound
module (Part D §2).

### 3. Sequences

Operators and the reading to confirm (all 16.7 to 16.9):

| Operator | Reading | Typical use |
|---|---|---|
| `a ##n b` | b holds n ticks after a; `##0` is same-tick fusion | fixed latency |
| `a ##[m:n] b`, `##[m:$]` | a window; `$` is unbounded and weak | bounded response |
| `s[*n]`, `s[*m:n]`, `[*]`, `[+]` | consecutive repetition; `[*]` is `[*0:$]`, `[+]` is `[*1:$]` | hold for n cycles |
| `b[->n]` | goto: n-th occurrence of b, match ends *at* that occurrence | "until the n-th ack" |
| `b[=n]` | nonconsecutive: n occurrences, match may extend past the last | counting within a window |
| `e throughout s` | boolean e holds at every tick of s | "enable stays high during the burst" |
| `s1 within s2` | s1 matches somewhere inside a match of s2 | containment |
| `s1 intersect s2` | both match with the same start and end | length-constrain a sequence |
| `s1 and s2` | both match from the same start; ends may differ | |
| `s1 or s2` | either | |
| `first_match(s)` | only the earliest-ending match | cut a `##[m:n]` antecedent to one attempt |

Sourced fragments: Verilator's `NEVERMATCH` text gives the `intersect`
rule in the standard's terms ("ensure its operands can match over a
common length (IEEE 1800-2023 16.9.6)"); its source glosses `intersect`
as "both operands match over one window, equal start and end" and `and`
as "both operand sequences must match"; the systemverilog.us page quotes
"A sequence that admits only empty matches is referred to as an empty
sequence" (16.7) and "(empty ##0 seq) does not result in a match"
(16.9.2.1).

Pitfalls worth a callout, each a reading to confirm and a probe:
a ranged antecedent (`a ##[1:3] b |-> c`) spawns one obligation per
match, not one per attempt; `b[=n]` versus `b[->n]` differ only in where
the match may end; an unbounded `##[1:$]` in a *consequent* of an
`assert` can never fail in simulation (weak).

### 4. Properties: implication, `disable iff`, sampled-value functions

- `s |-> p`: p is checked starting at the tick where s *ends*; `s |=> p`
  one tick later; `a |=> b` is `a |-> ##1 b` (Cummings prints the
  equivalence and recommends writing the `|-> ##1` form: "Use |-> ##1
  implications and not |=> implications", his guideline 10, on the
  grounds that it "Does reduce assertion coding errors" †; Verilator
  5.054's regression test checks exactly this equivalence, Part C
  finding 3).
- No match of the antecedent means the attempt succeeds vacuously.
  Verilator's source states it as the standard's rule: "Antecedent-miss
  is vacuous-pass for implication and non-vacuous-fail for followed-by".
  The standard also constrains antecedents: "Any sequence that is used
  as the antecedent of an overlapping implication (|->) shall be
  nondegenerate" and for `|=>` "shall admit at least one match"
  (16.12.22, quoted on systemverilog.us †).
- `disable iff (e)`: asynchronous abort of the attempt; the condition is
  *not* sampled. Verilator's 5.054 test states the rule it implements:
  "A disable condition pulsing between clock ticks aborts pending
  attempts, and its value is not sampled (IEEE 1800-2023 16.12)". A
  disabled attempt is neither pass nor fail (reading). `default disable
  iff` (16.15) sets it for a scope; OpenTitan's `tlul_assert.sv` uses
  `default disable iff disable_sva || !rst_ni;` with `default clocking`.
  The reset expression OpenTitan uses, `(rst) !== '0`, is the documented
  answer to X-at-time-zero (Part D §1).
- Sampled-value functions (16.9.3, 20.12): `$past(e[, n[, gate[,
  clk]]])`, `$rose`, `$fell`, `$stable`, `$changed`, `$sampled`.
  Sourced: "`$rose`, `$fell`, and `$changed` compare the previous
  sampled value with the current one ... These functions are not
  triggers that are watching for transitions" (Sutherland †); `$rose` is
  "True if LSB of expression changed to 1" (OpenTitan `hw/formal`
  README; the SBY manual says the same of Yosys: "only the least
  significant bits will be examined"). First-tick value of `$past`: the
  SBY manual says it is "undefined" in the first clock period (so the
  solver may pick anything); in simulation the reading is "the default
  initial value of the expression's type" (X for 4-state, 0 for
  2-state). That difference is the single most likely cause of a
  property that passes in simulation and fails in BMC at step 1, and it
  is probe p30.

### 5. `assert`, `assume`, `cover`, `restrict`

- `assert property` (16.14.1): checked in simulation; proof obligation in
  formal.
- `assume property` (16.14.2): in formal, a constraint on the
  environment (SBY: "In any solver generated trace, all of the
  assumptions will always be true"); in simulation checked like an
  assertion (reading; OpenTitan's `tlul_assert` relies on it by giving
  every `assume` an `else` error action; probe p47).
- `cover property` (16.14.3): reports that a sequence or property was
  matched; for an implication it counts non-vacuous matches only
  (Verilator source: "cover counts non-vacuous matches only (IEEE
  1800-2023 16.15.2)" — the clause number in that comment looks wrong,
  16.14.3 or 16.14.8 is expected; confirm). `cover sequence` counts
  every end-of-match (Verilator source, citing 16.14.3).
- `restrict property` (16.14.4): a formal-only constraint; "Restrict
  property is ignored by simulators" (Verilator source comment; the
  clause it cites, 16.12.2, disagrees with Y's 16.14.4).

### 6. `bind` (23.11)

Forms (reading): `bind <module> <checker_module> <inst> (ports);` binds
into every instance of the module; `bind <module> : <inst_path_list>
...` or `bind <hier.inst> ...` binds into named instances. Port
connections are resolved in the *target's* scope, which is why `.*`
works and why a bound checker can see internals. Sourced practice:
Cummings recommends the module form (`bind fifo1 fifo1_asserts p1
(.*);`, his guideline 4) and marks the per-instance form "NOT
RECOMMENDED", gives the non-technical reasons for a separate bind file
("Some EDA tools do not recognize assertion code"; editing the RTL
"changes the file time-stamp") †; lowRISC allows `.*` only "when binding
a module whose ports are all inputs" and wants all binds in "a dedicated
bindfile" (Part D §2). Tool limits: Verilator refuses "Bind with
instance list"; Yosys native parses `bind` since 0.10; Icarus has no
rule for it. OpenTitan's own note: "bind statements inside generate
blocks are currently not supported" (tool unnamed).

### 7. Catalog of what goes wrong (for the chapter's Pitfalls)

| # | Symptom | Mechanism | Source | Probe |
|---|---|---|---|---|
| 1 | Assertion never fails, never passes | antecedent never matches; vacuous | Beer et al.; 16.12.22; Verilator `NEVERMATCH` | p50, p52, p53 |
| 2 | Liveness-looking property never fails in simulation | `##[1:$]` / `until` are weak | Eisner et al.; reading | p14, p39 |
| 3 | False failure in `always_comb` | immediate assertion sees a glitch | Sutherland 2015; `prim_assert.sv` | p03 |
| 4 | Passes in simulation, fails at step 1 in BMC | `$past` in the first tick; no reset assumption; registers unconstrained | SBY manual | p30, p66 |
| 5 | Fails during reset, or is silent during X reset | `disable iff (rst)` vs `(rst) !== '0`; reset as antecedent | `prim_assert.sv` | p37, p38 |
| 6 | "Passes on Icarus" | concurrent assertions skipped under `-gsupported-assertions` | Icarus `parse.y` | p06 on IV |
| 7 | `\|=>` off by a cycle or miscounted | written for `\|->`; and Verilator 5.052 vs 5.054 | Cummings guideline 10; Verilator #8268 | p11 |
| 8 | Error message shows the wrong value | action block runs in Reactive on current values | Chapter 4; reading | p35 |
| 9 | Proven in formal, false in silicon | over-constraining `assume` | SBY manual; Kupferman and Vardi; OpenTitan "vacuous" column | p48 |
| 10 | BMC passes, property is false | bound shorter than the bug's depth (the FIFO needs 15 pushes) | SBY `depth` default 20 | worked example |
| 11 | True property, `prove` says UNKNOWN | not inductive; needs a helper invariant | SBY manual | p67 |
| 12 | Side effect disappears | `assert(randomize())` compiled out | lowRISC DV style | cross-ref to the constrained-random chapter |
| 13 | Checker stops the run at first failure | Verilator error limit defaults to 1 | Verilator `exe_sim.rst` | p61 |
| 14 | One flop's X prints hundreds of lines | `$error` per assertion per instance | Cummings 2016 | — |


---

# Part E — The Python mirror

### 1. Findings

1. **The book already contains the non-SVA mirror, in SystemVerilog and
   in Python, and neither is called a temporal property.** Chapter 11's
   monitor (`examples/ch11-architecture-to-verification/tb/dma_tb_pkg.sv`)
   has a `stable()` function and three `*_w` "was waiting" bits updated
   on every clocking-block edge: `ar_w = arvalid && !arready; ar_v =
   araddr;` then, next edge, fail "dropped VALID before READY" if `ar_w
   && !arvalid`, or "payload changed while waiting" if the saved value
   differs. That is a hand-built two-state automaton for
   `arvalid && !arready |=> arvalid && $stable(araddr)`: one state bit
   and one saved payload per channel, written three times. The chapter's
   most persuasive listing is that function beside the one-line property,
   and its honest caveat is that the function runs on Icarus and the
   property does not.
2. **A cocotb monitor is a coroutine that keeps the automaton's state in
   local variables and samples once per edge.** The sampling point is
   the whole of the semantics. cocotb's timing-model page: "`ReadOnly`
   allows users to jump to the end of the time step; allowing them to
   read the final values of signals or variables before more simulated
   time is consumed. This may be necessary if they wish to sample a
   signal or variable whose value glitches"
   [cocotb docs, timing_model.rst, v2.1.0](https://github.com/cocotb/cocotb/blob/v2.1.0/docs/source/timing_model.rst).
   An SVA property samples *before* the edge (Preponed); a cocotb
   monitor that does `await RisingEdge(clk); await ReadOnly()` samples
   *after* the edge's non-blocking updates. Both are consistent views of
   one cycle but they are shifted by one edge for registered outputs,
   which is the reason Chapter 11's cocotb testbench samples on
   `FallingEdge` then `ReadOnly` ("reads what the next rising edge will
   see", its header comment). The chapter must pick one convention for
   the mirror and show the same trace failing at the same cycle number
   in both; that is a measured claim for the examples, not for this
   note.
3. **Failure is a Python `assert`.** A cocotb test "fails an `assert`
   statement" or raises `AssertionError`
   [cocotb docs, writing_testbenches.rst, v2.1.0](https://github.com/cocotb/cocotb/blob/v2.1.0/docs/source/writing_testbenches.rst).
   An `assert` raised inside a *background* monitor task, not the test
   coroutine, is the case to probe: whether cocotb 2.1 fails the test at
   once, at the next `await`, or only when the task is joined (the same
   page's early-ending example, "this would fail, but it isn't run
   because the test was ended early", shows a check can be skipped
   silently when the test coroutine returns first). A monitor whose
   failure is swallowed is the Python form of the silently skipped
   Icarus assertion.
4. **No cocotb SVA layer exists on PyPI under the obvious names.**
   `cocotb-sva`, `pysva`, `cocotbext-assertions` and `cocotb-assert` are
   not registered (PyPI JSON API, 2026-11-15); the name `sva` belongs to
   an unrelated document tool. General-purpose runtime-verification
   libraries do exist (below), built for cyber-physical signals, not
   RTL. The recommendation is that the chapter write the monitor by hand
   (ten to fifteen lines), because the point is to see the state the
   SVA engine hides, and mention one library in Future Directions.

### 2. Libraries (PyPI metadata and README read; none installed or run)

| Package | Version, last upload | What its README says | Fit |
|---|---|---|---|
| `rtamt` | 0.4.10, 2026-09-19 | "a Python 3 library for monitoring of Signal Temporal Logic (STL) ... offline and online monitoring of discrete-time and dense-time STL. The online monitors support the bounded future fragment of STL"; `prev`/`next` only in discrete time; "supports Python 3.8 through 3.12" | closest: discrete-time online monitor with an `update()` per sample; bounded-future only, which is the safety fragment the chapter argues a simulator can decide. Works on `dvbook`'s Python 3.12 by its own statement, not on 3.13 |
| `reelay` | 25.0.0, 2025-11-30 | "A runtime verification library for real-time systems"; C++ and Python; past temporal logic and regular expressions per its paper list | past-time monitors; built from source per its README |
| `metric-temporal-logic` | 0.4.1, 2023-02-20 | MIT; `until`, `weak_until`, `timed_until`; evaluates over `DiscreteSignals` | offline evaluation of a recorded trace; unmaintained since 2023 |
| `ltlf2dfa` | 2.0.0, 2026-07-25 | LTLf and pure-past LTL on finite traces to a DFA "using MONA"; LGPLv3+; needs the MONA binary | the theory-matching one (finite traces, automaton out) but a heavy dependency |
| `flloat` | 0.3.0, 2020-03-24 | LTLf/LDLf evaluation | stale |
| `cocotb-coverage` | 2.0, 2025-10-03 | already in the book (the functional-coverage chapter) | its `CoverCheck` is the cover side of the mirror |

An environment change (installing `rtamt` into `dvbook`) is the author's
decision, as `z3` and `cocotb-coverage` were.

### 3. Proposed mirror, in prose (the author writes the code)

`stable_until_ready(clk, valid, ready, payload, name)`: a coroutine with
two locals, `waiting` and `held`. Each sampled cycle: if `waiting` then
require `valid` and `payload == held`; then set `waiting = valid and not
ready` and `held = payload`. It is Chapter 11's `stable()` in Python.
The second mirror, for a bounded-liveness property (`req |-> ##[1:N]
gnt`), needs a *list* of pending deadlines, one per outstanding request,
which shows why an SVA engine spawns an attempt per tick and why
Verilator's 5.054 "multiplicity" fix (#8267) matters: overlapping
attempts are the hard part. The third, optional: the same check through
`rtamt`'s discrete-time `update()`.

---

# Part F — Worked-example proposal

Nothing here has been run. Code fragments are sketches for the outline,
to be rewritten as files under `examples/ch09-temporal-properties/` and
measured. The restriction from Part C finding 1 shapes all of it: each
property exists as full SVA for Verilator and as a lowered clocked
boolean for SBY, joined by a macro or by `` `ifdef FORMAL ``.

### 1. Targets

- **FIFO** (`examples/ch01-what-is-dv/rtl/fifo.sv`, 16 by 8, async
  active-low reset). The bug, read in the RTL: `count` is `PTR_W` = 4
  bits wide and `full = (count == LAST)` with `LAST = 15`, so `full`
  rises at 15 entries and the sixteenth slot is never used. The chapter
  needs a *fixed* FIFO beside the buggy one (5-bit count, `full = count
  == DEPTH`); Chapter 1's file says it holds "one deliberate bug" and
  must not be edited (it is spliced there). A parameter or a second file
  under the chapter's own directory; the author decides.
- **AXI4-Lite master side of the DMA** (`examples/ch11-.../rtl/dma_v2.sv`,
  and `dma_v1.v` as the version with handshake findings). Chapter 11
  quotes the rules from `[@arm-ihi0022c]`: a source "must not wait" for
  READY before VALID; VALID and payload hold until the handshake.

### 2. FIFO properties

A bound checker module `fifo_sva` (ports all inputs, per lowRISC's rule),
with its own 5-bit occupancy model `occ` that counts accepted pushes
minus accepted pops (`wr_en && !full`, `rd_en && !empty`, the contract's
words), so the checker does not trust the DUT's `count`.

| Name | Property (SVA form) | Class | Expected on buggy / fixed |
|---|---|---|---|
| `NoOverflow_A` | `occ <= DEPTH` | safety invariant | pass / pass |
| `FullBackward_A` | `full \|-> occ == DEPTH` | safety | **fail** (full at 15) / pass |
| `FullForward_A` | `occ == DEPTH \|-> full` | safety | **vacuous pass** (occ never reaches 16) / pass |
| `FullReached_C` | `cover property (occ == DEPTH)` | cover | **unreachable** / reached |
| `EmptyIff_A` | `empty == (occ == 0)` | safety | pass / pass |
| `NotBoth_A` | `!(full && empty)` | safety | pass / pass |
| `PushWhenFullIgnored_A` | `wr_en && full && !rd_en \|=> $stable(occ) && full` | safety, uses `\|=>` | pass / pass |
| `Order_A` | data read equals data written, in order (three variants below) | safety | pass / pass |
| `Drain_A` | `!empty \|-> s_eventually empty` under a fairness assumption, or bounded: `!empty && rd_en[*DEPTH]`-style | liveness / bounded | theory only, or bounded |

The pair `FullBackward_A` / `FullForward_A` is the centerpiece and came
out of reading OpenTitan's FIFO checker, which separates "Forward" and
"Backward" assertions and states the equivalence as `FullIffFullDepth_A`
(Part D §4). On Chapter 1's FIFO the forward half *passes*, in
simulation with any stimulus and in an unbounded proof, because the
design can never hold sixteen entries: a property that sounds like the
specification ("when all sixteen entries are occupied, full is
asserted") is satisfied vacuously by a design that violates the
specification. The cover `FullReached_C` is what catches it: unhit in
the Verilator coverage database, and a hard `FAIL` in `sby` cover mode.
The backward half fails outright, with a 15-push counterexample. That
gives the task's "one vacuous pass caught by a cover" on the book's own
bug, with no contrived environment. A second, conventional vacuity case
for the exercises: add `assume (!(wr_en && full))` "to be polite" and
watch `PushWhenFullIgnored_A` pass vacuously (catalog row 9).

**BMC depth is a second lesson in the same example.** The shortest
counterexample to `FullBackward_A` is reset plus fifteen pushes, about
seventeen steps. SBY's default `depth` is 20, so default BMC finds it;
`depth 10` passes. Show both runs. (Exact step count is a measurement.)

**Data ordering, three ways, in rising order of formal fitness:**
1. *Simulation, SVA local variable*: `(wr_en && !full, d = wr_data, n =
   occ) |-> ...` tracking `n` pops then `rd_data == d`. Needs
   property-local variables and a variable-length wait; Verilator 5.052
   supports local variables with limits (Part C §2); not expressible in
   either open Yosys front end. Probe p28 decides whether the chapter
   can show it running.
2. *Reference model in the checker* (OpenTitan's choice): a shadow
   memory and `rd_en && !empty |-> rd_data == ref_mem[ref_rd]`. Runs
   everywhere; in formal the shadow memory doubles the state.
3. *One symbolic slot* (the formal idiom): `(* anyconst *)` address
   `f_addr`; a register `f_data` and flag `f_valid` capture the write
   that lands on `wr_ptr == f_addr`; assert `rd_data == f_data` when a
   read is taken from `rd_ptr == f_addr` while `f_valid`. The solver's
   free choice of `f_addr` covers all sixteen slots with one slot's
   worth of state. This is white-box (it reads `wr_ptr`, `rd_ptr`
   through the bind) and uses a Yosys attribute a simulator ignores
   (probe p65); under Verilator the same module needs `f_addr` driven
   as a random constant. OpenTitan's "2-3 different values suffice"
   assumption on `wdata_i` is the complementary data abstraction.

### 3. The property that fails induction and its helper invariant

On the **fixed** FIFO, `NoOverflow_A` (`occ <= DEPTH`) is true and BMC
passes at any depth, but `mode prove` with `smtbmc` should fail the
induction step: induction starts from an *arbitrary* state satisfying
the assertions for k cycles, and a state with `occ == 16` in the checker
but `count == 3` in the DUT satisfies `occ <= 16` for as long as the
solver likes, then one more accepted push breaks it. No k fixes it,
because the two counters can drift apart forever in unreachable states.
The helper invariant is the relation between them:

- `Sync_A`: `occ == count` (checker model equals DUT occupancy), and
- `Ptrs_A`: `count == (wr_ptr - rd_ptr) mod DEPTH`, with the `count ==
  DEPTH` case stated separately, which the data-ordering proof needs.

With `Sync_A` asserted alongside, both become inductive at small k. The
SBY tutorial's FIFO carries the same invariant under the name
`a_count_diff` ("count should be equal to the difference between writer
and reader address"), which is independent evidence that this is the
natural helper, and the manual's sentence "the proof may also yield an
UNKNOWN result if an assertion can be made to fail during the induction
step" is the anchor for what the reader will see. Then run the original
property alone under `abc pdr`, which searches for the strengthening
itself (probe p68); if it proves, the chapter has "k-induction needs the
invariant from you; PDR finds one" in two log files, and hands the
*why* to the formal chapter. **Every expectation in this subsection is a
prediction**; the induction trace (the unreachable start state) is the
figure to draw from the measured VCD.

Formal environment the example needs, each a possible Pitfall: reset
must be assumed in the initial state (`$initstate |-> !rst_n`, or an
`initial assume`), otherwise registers start unconstrained in BMC; the
FIFO's reset is asynchronous, and how SBY's default (non-`multiclock`)
flow treats `negedge rst_n` was not found in the manual pages read
(probe; the tutorial FIFO uses `posedge rst` and `initial` values);
`$past` must be guarded in the first cycle (the tutorial's `past_nwen`
register is the hand-made guard).

### 4. AXI handshake properties (DMA as master)

Checker bound to the DMA, in the style of `tlul_assert` (Part D §3):
*assert* on what the master drives (AR, AW, W, RREADY, BREADY),
*assume* on what the slave drives (R, B, the READY inputs).

| Name | Property | Role |
|---|---|---|
| `ArValidHeld_A` | `ARVALID && !ARREADY \|=> ARVALID` | assert |
| `ArStable_A` | `ARVALID && !ARREADY \|=> $stable(ARADDR)` | assert |
| same for AW (`AWADDR`) and W (`WDATA`, `WSTRB`) | | assert |
| `RValidHeld_M`, `RStable_M` | `RVALID && !RREADY \|=> RVALID && $stable({RDATA, RRESP})` | assume in formal, assert in simulation |
| `BValidHeld_M` | same for B | assume |
| `ArNoWaitReady_C` | `cover property (ARVALID && !ARREADY)` and, in formal, a cover of `ARVALID` under `assume (!ARREADY)` held low | cover |
| `ArHandshakeBounded_A` (optional) | `ARVALID \|-> ##[0:N] ARREADY` | a bounded-liveness *assumption* on the slave if any liveness is proved |

Three points for the outline:

1. **"A source must not wait for READY before asserting VALID" is not a
   property of one trace.** A single run in which READY happened to be
   high first does not violate it; the rule says a run with READY held
   low must still reach VALID. That is an existence statement: a
   reachability cover in formal (`cover(ARVALID)` with READY assumed
   low), or a directed test in simulation, never a plain `assert`.
   Chapter 11's version 1 finding, "ARVALID high for 0 cycles, 0 AR ...
   handshakes" under some slave styles, is the deadlock that rule
   exists to prevent. This is a clean example of the limits of
   trace properties and belongs in the chapter.
2. **The lowered form** for SBY of `ArStable_A`: in `always @(posedge
   PCLK)`, `if (PRESETn && $past(PRESETn) && $past(ARVALID &&
   !ARREADY)) assert (ARVALID && ARADDR == $past(ARADDR));`. Writing
   this once by hand, next to the `|=>` form, is the lesson of Part C
   finding 1; whether to hide it in a macro afterwards follows
   OpenTitan.
3. **Risk.** Proving handshake stability on a 270-line FSM by
   k-induction may need helper invariants about the FSM encoding that
   are not obvious, and the DMA has an APB side that must be assumed
   well-formed first. Time-box it: BMC to a stated depth plus covers is
   an honest result for this chapter ("no violation within N cycles of
   reset; the proof is the formal chapter's"), and `abc pdr` may close
   it unaided. Version 1 (`dma_v1.v`) is the refutation target only if
   one of its findings is a stability violation; the `v1-findings`
   output read here shows deadlocks, length and register bugs, not a
   dropped VALID, so **the refuted AXI property may need a seeded
   mutant** (a one-line change that drops VALID after one cycle),
   which the mutation-testing chapter can reuse.

### 5. Example list for the outline (candidate)

1. `immediate` — an immediate assert glitching in `always_comb`, then
   `assert final` (Verilator; Icarus for the simple form).
2. `handshake` — Chapter 11's `stable()` beside the one-line property,
   same failing trace, `run.out` spliced.
3. `sequences` — delay, repetition, goto, `throughout` on one waveform.
4. `vacuity` — FIFO forward/backward pair with the cover; `NEVERMATCH`.
5. `weak-strong` — a pending `##[1:$]` at end of simulation.
6. `bind` — `fifo_sva` bound to buggy and fixed FIFO; the bind file.
7. `sby-bmc` — refute `FullBackward_A`; depth 10 versus 20.
8. `sby-cover` — `FullReached_C` unreachable.
9. `sby-prove` — induction failure, helper invariant, `abc pdr`.
10. `axi` — assert/assume split on the DMA; BMC and covers.
11. `cocotb-monitor` — the Python mirror on both simulators.
12. `matrix` — the probe list as a measured support table.

Toolchain additions the examples need: `sby` (not in the STATUS tool
list; it is a separate repository and install from Yosys), a decision on
`read_slang` availability, optionally Boolector. The build system needs
an SBY recipe (`examples/mk/`) with `expect` mapped onto the book's
`EXPECT := fail` / `EXPECT_OUTPUT` convention, and CI needs `sby`
pinned at `v0.68` to match Yosys.


---

# Addendum to Part C §3 — three things read in SBY's source after the parts above

[sby v0.68 `sbysrc/sby_core.py`, `sby_mode_bmc.py`, `sby_engine_smtbmc.py`](https://github.com/YosysHQ/sby/tree/v0.68/sbysrc)

1. **Asynchronous resets.** In the default (non-`multiclock`) flow the
   generated `design_prep.ys` runs `async2sync` (and `clk2fflogic` only
   under `multiclock on`), then `formalff -setundef -clk2ff -ff2anyinit
   -hierarchy` and `setundef -undriven -anyseq`. So the Chapter 1 FIFO's
   `negedge rst_n` flop is converted to a synchronous-reset model
   without the author doing anything, registers without an `initial`
   value start as free ("anyinit"), and undriven nets are free every
   cycle. This answers Part F §3's open question in documentation;
   the behavior at the first edge is still a probe.
2. **Mode filtering of property kinds.** In `bmc` and `prove` the prep
   script runs `chformal -live -fair -cover -remove`: covers and
   liveness properties are *deleted*, silently, before the solver runs.
   In `cover` mode asserts are removed unless `cover_assert on`. In
   `live` mode asserts become assumptions. A `.sby` with only `mode
   prove` therefore never looks at a `cover`; the chapter's example
   needs the `[tasks]` form with a cover task, and this is the
   mechanism behind catalog row 1 on the formal side.
3. **No default engine; induction is a separate process.**
   `engine_list()` returns only what `[engines]` holds; nothing in the
   source supplies one when the section is empty (probe p00 records
   what `sby` prints). In `prove` mode the smtbmc engine starts two
   processes, logged as `engine_0.basecase` and `engine_0.induction`,
   and accepts `--basecase` / `--induction` to run one alone. Those log
   prefixes are what the reader will see when the helper-invariant
   example fails in induction and passes in the base case. `aigsmt`
   defaults to `yices` (used to turn an `abc pdr` AIGER witness into a
   trace): with only z3 installed the `.sby` needs `aigsmt z3` or
   `aigsmt none`.

---

# Unsourced-claims table (all parts)

| Claim | Status |
|---|---|
| Every semantic reading of clause 16 in Part B §2 to §6 not inside quotation marks (deferred-assertion regions, what a disabled attempt counts as, `assume` checked in simulation, first-tick `$past` value in simulation, weak default for sequence properties in `assert`, `bind` name resolution) | From the note-writer's knowledge of the standard, **not read in any edition this session**. Confirm in the PDF before printing. |
| Third-level clause numbers (16.9.x, 16.12.x, 16.14.x) | From YosysHQ's Property IR table (edition unstated) and Verilator comments (self-inconsistent). `implies`/`iff` number unresolved (16.12.8 or 16.12.9). Titles marked "from memory" are that. |
| Clause 4.4 as the scheduling-regions clause | From memory; Chapter 4 of the book cites Cummings and Salz instead and that is safer. |
| Every tool behavior in Part C | Documented (tagged source, manuals), **none measured**. The probe list exists to measure them. |
| `\|=>` gives a wrong result on Verilator 5.052 | Inferred from the 5.054 `Changes` line and the one-line fix commit; not reproduced. Could be pass-count only. |
| OpenTitan disables assertions under Verilator "because the choice predates Verilator's SVA engine" | The mechanism is read in the file; the reason is a guess and must not be printed. |
| OpenTitan macro counts (295 / 105 / 84 / ...) | Measured by `grep` at commit 0d2b191a over four RTL directories only. Not a repository total. |
| "Typically 20% of formulas are found to be trivially valid" (Beer et al.) | Returned by the fetch tool as a partial quotation from the FMSD 2001 text; re-read the sentence and its qualifiers in the PDF. |
| Kupferman and Vardi's "vacuous passes always point to a real problem..." | Reported by the fetch as a quotation of IBM experience inside their paper; confirm wording and attribution (it may be quoting Beer et al.). |
| Vardi's sentence that SVA "is based, in essence, on that regular layer" | Returned as a quotation; venue and pages of the chapter (25 Years of Model Checking, LNCS 5000, 2008) are from memory and a search-result title, not printed in the fetched copy. |
| Kantrowitz and Noack percentages | Read from the extracted text of Figure 2; they sum to 100. Page range and total bug count not in the extraction. |
| Taylor et al. 1998 (Alpha 21264) | Bibliographic record only. Do not cite a number. |
| Wolper's even-positions example as the reason LTL needs regular expressions | Not found in the fetched Vardi text under Wolper's name; Wolper 1983 not fetched. |
| Pnueli's paper as FOCS 1977, pp. 46-57 | The fetched copy shows page numbers 46-57 and no venue line; venue from Vardi's reference list ("FOCS 1977, pp. 46-57"). |
| Lamport's and Alpern-Schneider's bibliographic details | As returned from the fetched PDFs; consistent with the known records. |
| Expected verdicts in Part F (which property fails, vacuous, unreachable; that `NoOverflow_A` fails induction and `Sync_A` repairs it; that `abc pdr` proves it unaided; "about seventeen steps") | Predictions from reading the RTL. None run. |
| Chapter 11's version 1 has no VALID-stability violation | Inferred from `v1-findings/run.out` (deadlocks, length and register findings); the RTL was not analyzed for it. |
| The `rtamt` fit for RTL monitoring | From its README only; not installed. |
| cocotb's behavior when a background task raises `AssertionError` | Not established; the docs page read shows only that a check can be skipped when the test ends early. |
| Cummings slides' venue and year | The DVCon-proceedings file prints neither; SNUG 2016 is inferred from the companion paper's filename and a search-result title naming DAC 2016 Verification Academy. Confirm before citing a venue. |

# Key sources and BibTeX suggestions

Existing `refs.bib` keys to reuse: `ieee1800-2023`, `ieee1800-2017`,
`cummingssalz2007events`, `bromley2012clocking`, `sutherland2006gotchas`,
`sutherland2007gotchas`, `lowrisc-dv-style`, `lowrisc-verilog-style`,
`opentitan-dv-methodology`, `opentitan-tlul-checker`, `opentitan-prim-fifo`,
`verilator-languages`, `verilator-changes`, `verilator-warnings`,
`verilator-exe-verilator`, `verilator-exe-sim`, `icarus-release-13`,
`yosys-verilog`, `cocotb-docs`, `cocotb-coverage`, `arm-ihi0022c`,
`foster2024wrg` (adoption only). Check each existing entry's URL and
note against what this chapter cites from it (the Verilator keys should
point at the `v5.052` tag for anything quoted as 5.052 behavior).

New entries. **Fields marked `% CHECK` were not verified against the
document itself** and AGENTS.md requires that before the entry lands.

```bibtex
@inproceedings{pnueli1977temporal,
  author    = {Amir Pnueli},
  title     = {The Temporal Logic of Programs},
  booktitle = {18th Annual Symposium on Foundations of Computer Science
               (FOCS)},  % CHECK venue string
  year      = {1977},
  pages     = {46--57},
  doi       = {10.1109/SFCS.1977.32}  % CHECK doi (from memory)
}

@article{lamport1977proving,
  author  = {Leslie Lamport},
  title   = {Proving the Correctness of Multiprocess Programs},
  journal = {IEEE Transactions on Software Engineering},
  volume  = {SE-3},
  number  = {2},
  pages   = {125--143},
  year    = {1977},
  doi     = {10.1109/TSE.1977.229904},  % CHECK doi (from memory)
  note    = {Read at https://lamport.azurewebsites.net/pubs/proving.pdf}
}

@article{alpernschneider1985liveness,
  author  = {Bowen Alpern and Fred B. Schneider},
  title   = {Defining Liveness},
  journal = {Information Processing Letters},
  volume  = {21},
  number  = {4},
  pages   = {181--185},
  year    = {1985},
  doi     = {10.1016/0020-0190(85)90056-0},  % CHECK doi (from memory)
  note    = {Read at
             https://www.cs.cornell.edu/fbs/publications/DefLiveness.pdf}
}

@incollection{vardi2008church,
  author    = {Moshe Y. Vardi},
  title     = {From {Church} and {Prior} to {PSL}},
  booktitle = {25 Years of Model Checking: History, Achievements,
               Perspectives},  % CHECK
  series    = {Lecture Notes in Computer Science},
  volume    = {5000},  % CHECK
  publisher = {Springer},
  year      = {2008},
  pages     = {150--171},  % CHECK (from memory)
  note      = {Read in a copy hosted by Sapienza University of Rome}
}

@inproceedings{eisner2003truncated,
  author    = {Cindy Eisner and Dana Fisman and John Havlicek and
               Yoad Lustig and Anthony McIsaac and
               {Van Campenhout}, David},
  title     = {Reasoning with Temporal Logic on Truncated Paths},
  booktitle = {Computer Aided Verification (CAV 2003)},
  series    = {Lecture Notes in Computer Science},
  volume    = {2725},  % CHECK
  publisher = {Springer},
  year      = {2003},
  doi       = {10.1007/978-3-540-45069-6_3}
}

@article{beer2001vacuity,
  author  = {Ilan Beer and Shoham Ben-David and Cindy Eisner and
             Yoav Rodeh},
  title   = {Efficient Detection of Vacuity in Temporal Model Checking},
  journal = {Formal Methods in System Design},
  volume  = {18},
  number  = {2},  % CHECK
  pages   = {141--163},
  year    = {2001},
  doi     = {10.1023/A:1008779610539}  % CHECK doi (from memory)
}

@inproceedings{kupfermanvardi1999vacuity,
  author    = {Orna Kupferman and Moshe Y. Vardi},
  title     = {Vacuity Detection in Temporal Model Checking},
  booktitle = {Correct Hardware Design and Verification Methods
               (CHARME'99)},
  series    = {Lecture Notes in Computer Science},
  volume    = {1703},
  pages     = {82--98},
  publisher = {Springer},
  year      = {1999}
}

@techreport{bauer2007rvltl,
  author      = {Andreas Bauer and Martin Leucker and
                 Christian Schallhart},
  title       = {Runtime Verification for {LTL} and {TLTL}},
  institution = {Technische Universit{\"a}t M{\"u}nchen, Institut f{\"u}r
                 Informatik},
  number      = {TUM-I0724},
  year        = {2007},
  url         = {https://www.isp.uni-luebeck.de/sites/default/files/publications/TUM-I0724_1.pdf},
  note        = {Journal version: ACM TOSEM 20(4), 2011 (not read; cite
                 the report unless the journal text is checked).
                 Accessed 2026-11-15}
}

@inproceedings{kantrowitznoack1996done,
  author    = {Michael Kantrowitz and Lisa M. Noack},
  title     = {I'm Done Simulating; Now What? {Verification} Coverage
               Analysis and Correctness Checking of the {DECchip} 21164
               {Alpha} Microprocessor},
  booktitle = {Proceedings of the 33rd Design Automation Conference
               (DAC)},
  year      = {1996},
  note      = {Pages not in the copy read (the UCI DAC compendium,
               file 23\_5.pdf)}  % CHECK pages, doi
}

@inproceedings{sutherland2015assertions,
  author    = {Stuart Sutherland},
  title     = {Who Put Assertions In My {RTL} Code? {And} Why? {How RTL}
               Design Engineers Can Benefit from the Use of
               {SystemVerilog} Assertions},
  booktitle = {SNUG Silicon Valley},
  year      = {2015},
  url       = {https://sutherland-hdl.com/papers/2015-SNUG-SV_SVA-for-RTL-Designers_paper.pdf},
  note      = {Accessed 2026-11-15}
}

@misc{cummings2016bindfiles,
  author = {Clifford E. Cummings},
  title  = {{SystemVerilog} Assertions -- Bindfiles \& Best Known
            Practices for Simple {SVA} Usage},
  year   = {2016},  % CHECK year and venue
  url    = {https://dvcon-proceedings.org/wp-content/uploads/SW_5A_2_SVA_BindFiles.pdf},
  note   = {Slides. Accessed 2026-11-15}
}

@misc{sby-docs,
  author = {{YosysHQ}},
  title  = {{SymbiYosys} ({sby}) Documentation, release 0.68},
  year   = {2026},
  url    = {https://github.com/YosysHQ/sby/tree/v0.68/docs/source},
  note   = {Pages reference.rst, verilog.rst, verific.rst, install.rst,
            quickstart.rst. Accessed 2026-11-15}
}

@misc{sby-fifo-example,
  author = {{YosysHQ}},
  title  = {{SymbiYosys} example: docs/examples/fifo (fifo.sv, fifo.sby)},
  year   = {2026},
  url    = {https://github.com/YosysHQ/sby/tree/v0.68/docs/examples/fifo},
  note   = {Accessed 2026-11-15}
}

@misc{sby-source,
  author = {Claire Xenia Wolf and {YosysHQ contributors}},
  title  = {{SymbiYosys} source, v0.68: sbysrc/sby\_core.py},
  year   = {2026},
  url    = {https://github.com/YosysHQ/sby/blob/v0.68/sbysrc/sby_core.py},
  note   = {Accessed 2026-11-15}
}

@misc{yosys-read-verilog,
  author = {{YosysHQ}},
  title  = {Yosys 0.68: frontends/verilog (read\_verilog help text and
            grammar)},
  year   = {2026},
  url    = {https://github.com/YosysHQ/yosys/tree/v0.68/frontends/verilog},
  note   = {Accessed 2026-11-15}
}

@misc{yosys-changelog,
  author = {{YosysHQ}},
  title  = {Yosys CHANGELOG, v0.68},
  year   = {2026},
  url    = {https://github.com/YosysHQ/yosys/blob/v0.68/CHANGELOG},
  note   = {Accessed 2026-11-15}
}

@misc{svelab-sva,
  author = {Martin Povi{\v{s}}er and {sv-elab contributors}},  % CHECK author
  title  = {sv-elab (formerly yosys-slang): src/sva.cc at the commit
            pinned by Yosys 0.68},
  year   = {2026},
  url    = {https://github.com/povik/sv-elab/blob/3dddccd478618d68f8a5e160fb4b5783c4da35d4/src/sva.cc},
  note   = {Accessed 2026-11-15}
}

@misc{yosyshq-property-ir,
  author = {{YosysHQ}},
  title  = {Property {IR} 0.1 Documentation: {SVA} Table},
  year   = {2026},
  url    = {https://yosyshq.readthedocs.io/projects/property-ir/en/latest/sva_table.html},
  note   = {Accessed 2026-11-15}
}

@misc{verilator-changes-5054,
  author = {Wilson Snyder and {Verilator contributors}},
  title  = {Verilator Changes, v5.054},
  year   = {2026},
  url    = {https://github.com/verilator/verilator/blob/v5.054/Changes},
  note   = {Accessed 2026-11-15}
}

@misc{verilator-commit-8268,
  author = {Artur Bieniek},
  title  = {Support non-overlapped property implications correctly
            (\#8268), commit cd2475fb},
  year   = {2026},
  url    = {https://github.com/verilator/verilator/commit/cd2475fbd4ee3ed9f167da1f2dfd02f9a33bffdc},
  note   = {Accessed 2026-11-15}
}

@misc{icarus-parse-y,
  author = {Stephen Williams and {Icarus Verilog contributors}},
  title  = {Icarus Verilog v13\_0: parse.y (assertion grammar)},
  year   = {2026},  % CHECK release year of v13_0 against icarus-release-13
  url    = {https://github.com/steveicarus/iverilog/blob/v13_0/parse.y},
  note   = {Accessed 2026-11-15}
}

@misc{opentitan-prim-assert,
  author = {{lowRISC contributors}},
  title  = {{OpenTitan}: hw/ip/prim/rtl/prim\_assert.sv and its macro
            headers},
  year   = {2026},
  url    = {https://github.com/lowRISC/opentitan/blob/0d2b191a4a78d4c3fcb487e116eb2e7b54223841/hw/ip/prim/rtl/prim_assert.sv},
  note   = {Commit 0d2b191a of 2026-11-08. Accessed 2026-11-15}
}

@misc{opentitan-formal-readme,
  author = {{lowRISC contributors}},
  title  = {{OpenTitan} Assertions (hw/formal/README.md)},
  year   = {2026},
  url    = {https://github.com/lowRISC/opentitan/blob/0d2b191a4a78d4c3fcb487e116eb2e7b54223841/hw/formal/README.md},
  note   = {Accessed 2026-11-15}
}

@misc{opentitan-fifo-sync-fpv,
  author = {{lowRISC contributors}},
  title  = {{OpenTitan}: hw/ip/prim/fpv/vip/prim\_fifo\_sync\_assert\_fpv.sv},
  year   = {2026},
  url    = {https://github.com/lowRISC/opentitan/blob/0d2b191a4a78d4c3fcb487e116eb2e7b54223841/hw/ip/prim/fpv/vip/prim_fifo_sync_assert_fpv.sv},
  note   = {Accessed 2026-11-15}
}

@misc{opentitan-tlul-assert,
  author = {{lowRISC contributors}},
  title  = {{OpenTitan}: hw/ip/tlul/rtl/tlul\_assert.sv},
  year   = {2026},
  url    = {https://github.com/lowRISC/opentitan/blob/0d2b191a4a78d4c3fcb487e116eb2e7b54223841/hw/ip/tlul/rtl/tlul_assert.sv},
  note   = {May duplicate the existing key opentitan-tlul-checker;
            check before adding. Accessed 2026-11-15}
}

@misc{cocotb-timing-model,
  author = {{cocotb contributors}},
  title  = {cocotb 2.1 Documentation: Timing Model},
  year   = {2026},
  url    = {https://github.com/cocotb/cocotb/blob/v2.1.0/docs/source/timing_model.rst},
  note   = {Accessed 2026-11-15}
}

@misc{rtamt,
  author = {Dejan Ni{\v{c}}kovi{\'c} and Tomoya Yamaguchi},  % CHECK authors
  title  = {{RTAMT}: Signal Temporal Logic monitoring library, 0.4.10},
  year   = {2026},
  url    = {https://github.com/nickovic/rtamt},
  note   = {Accessed 2026-11-15}
}
```

Not for `refs.bib` until read: Taylor et al. DAC 1998
(10.1145/277044.277208); Purandare and Somenzi CAV 2002
(10.1007/3-540-45657-0_39, abstract only); Wolper 1983; Kupferman and
Vardi 2001 (safety, bad prefixes); Bustan and Havlicek CAV 2006; Armoni
et al. TACAS 2002; Cerny, Dudani, Havlicek and Korchemny's book (the
standard reference for SVA semantics; a copy surfaced in search on a
file-sharing host and was deliberately not opened).

# Confidence notes

- **High**: everything in Part C attributed to a tagged file (Verilator
  5.052/5.054 `Changes`, `docs/guide`, `src/`, golden `.out` files;
  Icarus `parse.y`; Yosys 0.68 parser, lexer, `verific.cc`, CHANGELOG,
  `.gitmodules`; sv-elab `sva.cc` at the pinned commit; SBY 0.68 docs,
  example and `sbysrc`). These were cloned or downloaded and read
  directly, not through a summarizing tool. Likewise Part D: the
  OpenTitan and lowRISC files were read directly at a named commit, and
  Part E's cocotb pages and library READMEs.
- **Medium**: Part A's quotations. The papers were fetched from the
  URLs given, but through a tool that returns a model's extraction of
  the page, splits long quotations and can trim them. The definitions
  and theorem statements agree with the literature as the note-writer
  knows it; the exact wording of each † quotation must be re-read.
  `Changes` attributions to a release are by position under the version
  header, as in the Chapter 6 to 8 notes.
- **Low / open**: every semantic statement about clause 16 that is not a
  quotation (the standard was not read in any edition); third-level
  clause numbers; all predictions in Part F; whether the author's Yosys
  build has `read_slang` and whether `sby` is installed at all; whether
  Verilator 5.052's `|=>` defect affects pass/fail or only counts.
- **Scope boundary kept**: how BMC, k-induction and PDR work is the
  formal chapter's; this note uses them as black boxes with three
  observable verdicts. Assertion *coverage* as a closure metric is the
  functional-coverage chapter's (its research note, Part B §1, has the
  OpenTitan and UCIS material); here `cover` appears only as the vacuity
  witness. Multiclock properties, checkers, `let`, recursive properties
  and the formal semantics of Annex F are listed in the probe table for
  completeness and are candidates for the SVA appendix rather than the
  chapter.
- **A chapter-shape question for gate 1** (AGENTS.md: raise it with the
  author instead of choosing): Part C findings 1 to 3. (i) Teach full
  SVA on a simulator whose engine is two releases old and prove only a
  lowered subset, or build the chapter around the macro layer; (ii)
  re-pin Verilator to 5.054 before measuring, because `|=>` changed;
  (iii) add `sby` and possibly Boolector and `suprove` to the toolchain
  and CI.
