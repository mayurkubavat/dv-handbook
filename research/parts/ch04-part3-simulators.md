---
title: "Research note: Chapter 4, part 3 — simulator implementations"
date: 2026-09-09
author: research-agent
status: draft
feeds: Ch. 4
---

# Chapter 4 research, part 3: simulator implementations

**Scope note.** This note gathers primary documentation for the two open
simulators the book's examples run on (Verilator and Icarus Verilog), the
evidence that licenses Chapter 4's central worked example (two simulators
disagreeing on race-sensitive source), a short survey of other maintained open
simulators, and what can and cannot be sourced about performance.

Constraint observed throughout: **no clause text of IEEE 1364 or IEEE 1800 is
quoted or paraphrased here.** The standards are named; statements about their
content come from secondary sources that are themselves cited.

Reachable: the Verilator user guide and its in-repository developer
documentation (`docs/internals.rst`), the Icarus Verilog documentation sources,
the cocotb simulator-support page, the CHIPS Alliance `sv-tests` repository, and
one freely available SNUG paper. **Not** reachable: the Sunburst Design archive
(sunburst-design.com now 301-redirects to paradigm-works.com, whose PDF library
is behind a login), so the Cummings SNUG papers are not cited below; and
Verilator's `Changes` file could not be read far enough back to date `--timing`
(§8).

---

## 1. Verilator: what it is, and what it is not

### 1.1 Not a simulator in the usual sense

Verilator's own overview refuses the word: it is "not a traditional simulator
but a compiler," which "reads the specified SystemVerilog code, lints it,
optionally adds coverage and waveform tracing support, and compiles the design
into a source-level multithreaded C++ or SystemC 'model'"
([Verilator user guide, overview, 5.052, accessed 2026-09-08](https://verilator.org/guide/latest/overview.html))
**[docs]**. What you run is a compiled C++ program, not a design loaded into a
simulation kernel.

### 1.2 Scheduling: static, and modeled on two of the standard's regions

The question "is Verilator event-driven or cycle-based?" has a documented
answer, and it is neither of the textbook alternatives. Verilator's developer
documentation states that "the static (Verilation time) scheduling of
SystemVerilog processes is performed by code in the `V3Sched` namespace" — that
is, the evaluation order is decided **at compile time**, not by a runtime event
queue ([Verilator `docs/internals.rst`, master, accessed 2026-09-08](https://github.com/verilator/verilator/blob/master/docs/internals.rst))
**[docs]**.

The same document is explicit about which of the standard's scheduling regions
it implements: "Verilator implements the Active and NBA regions of the
SystemVerilog scheduling model as described in IEEE 1800-2023 chapter 4, and in
particular sections 4.5 and Figure 4.1" (ibid.) **[docs]**. Two regions, not the
full stratified set — the chapter should say this plainly, because it is the
crispest statement available of what a compiled model gives up.

The generated model exposes region entry points that the runtime loop iterates
to convergence — `_eval_ico` (input combinational), then `_eval_act` (Active),
then `_eval_nba` — where "a region entry point evaluates one iteration of its
region, and returns whether it did any work, meaning the region has not
converged yet and must be evaluated again" (ibid.) **[docs]**. Combinational
loops are broken by a "hybrid" logic class, and at startup an `_eval_stl` settle
function evaluates all combinational logic (ibid.) **[docs]**.

So: **compile-time-scheduled, iterated-to-convergence evaluation of two
scheduling regions**, not a runtime event queue. Calling it "cycle-based" would
be wrong; calling it "event-driven" would also be wrong.

### 1.3 `--timing` changes the answer, partially

Verilator gained the ability to execute delays and event controls. The option
`--timing` / `--no-timing` "enables or disables support for timing constructs
such as delays, event controls (unless it's at the top of a process), wait
statements, and joins," and "requires a C++ compiler with coroutine support
(GCC 10, Clang 5, or newer)"
([Verilator user guide, `verilator` arguments, 5.052, accessed 2026-09-08](https://verilator.org/guide/latest/exe_verilator.html))
**[docs]**. The implementation is described in the developer docs: "Timing
support in Verilator utilizes C++ coroutines, which is a new feature in C++20.
The basic idea is to represent processes and tasks that await a certain event or
simulation time as coroutines" ([`docs/internals.rst`](https://github.com/verilator/verilator/blob/master/docs/internals.rst))
**[docs]**. Note the parenthesis in the option text: an event control **at the
top of a process** (the ordinary `always @(posedge clk)`) is still handled by
static scheduling, not by a coroutine. `--timing` adds dynamic suspension for
constructs inside processes; it does not convert Verilator into an event-driven
kernel.

With `--no-timing`, delay statements "are ignored (as they are in synthesis)"
([Verilator user guide, language limitations, 5.052, accessed 2026-09-08](https://verilator.org/guide/latest/languages.html))
**[docs]**; the user guide notes elsewhere that this issues a `STMTDLY` warning.

### 1.4 Two-state, and what that costs

The user guide's "Unknown States" section: "Verilator is mostly a two-state
simulator, not a four-state simulator. However, it has two features that uncover
most initialization bugs (including many that a four-state simulator will
miss.)" (ibid.) **[docs]**.

The two features are the X options, documented in
[`docs/guide/exe_verilator.rst`, master, accessed 2026-09-08](https://github.com/verilator/verilator/blob/master/docs/guide/exe_verilator.rst)
**[docs]**:

- `--x-assign <value>` — "Assign non-initial Xs to this value": `0` "converts all
  Xs to 0s, and is also fast"; `1` "converts all Xs to 1s"; `fast` (default)
  "converts all Xs to whatever is best for performance"; `unique` replaces
  explicit Xs with "a constant value determined at runtime."
- `--x-initial <value>` — "Assign initial Xs to this value": `0` zeroes all
  otherwise-uninitialized variables; `unique` (the default) randomizes per run to
  expose reset bugs; `fast` picks whatever Verilator judges optimal.
- `--x-initial-edge` — "Enable initial X->0 and X->1 edge triggers."

What is lost is stated directly, and this is the sentence the chapter should
quote: "Identity comparisons (=== or !==) are converted to standard ==/!= when
neither side is a constant. **This may make the expression yield a different
result than a four-state simulator**"
([language limitations](https://verilator.org/guide/latest/languages.html))
**[docs]**. And: "An === comparison to X will always be false, so that Verilog
code which checks for uninitialized logic will not fire" (ibid.) **[docs]**.
The practical consequence: an X-check written `if (sig === 1'bx) $error(...)`
is dead code under Verilator.

### 1.5 Documented divergences from an event-driven simulator

These are the specifics from the "Language Limitations" page, and each is a
place where Verilator and Icarus can legitimately print different things:

1. **Initial edges.** "Event-driven simulators will generally trigger an edge on
   a transition from X to 1 (posedge) or X to 0 (negedge). However, by default,
   since clocks are initialized to zero, Verilator will not trigger an initial
   negedge" (ibid.) **[docs]**.
2. **Sensitivity-list semantics follow a synthesis tool, not a simulator.**
   "Verilator also simulates events as Synopsys's Design Compiler would, namely
   given a block of the form: `always @(x) y = x & z;` This will recompute y
   when there is a potential for change in x or a change in z... **A compliant
   simulator will only calculate y if x changes**" (ibid.) **[docs]**. This is
   Verilator's documentation stating outright that its behavior differs from a
   compliant simulator's for an incomplete sensitivity list.
3. **Timing constructs discarded.** "All specify blocks and timing checks are
   ignored. All min:typ:max delays use the typical value" (ibid.) **[docs]**.
4. **Primitives.** UDP tables are supported, but "the 3-state and MOS gate
   primitives are not supported," and "tristate drivers are not supported inside
   functions and tasks" (ibid.) **[docs]**.

### 1.6 Does Verilator guarantee the same answer as an event-driven simulator?

For race-free code the guarantee is implicit rather than stated: Verilator
implements the Active and NBA regions (§1.2), and race-free RTL is by definition
code whose result does not depend on ordering within a region. The documentation
makes **no blanket promise of equivalence**, and items 1, 2 and 4 in §1.5 are
counterexamples even for code many engineers would call race-free.

For racy code, Verilator does not resolve the race the way a queue-based
simulator does — it has no queue. It picks one order at Verilation time and
takes it every run. The safe formulation for the chapter: **Verilator is
deterministic across runs, and that determinism is not the same thing as
correctness.** A race resolved identically every time is still a race.

---

## 2. Icarus Verilog

### 2.1 What it is

Icarus Verilog describes itself in the same "compiler, not simulator" terms, but
with a different back end: "Icarus Verilog is not aimed at being a simulator in
the traditional sense, but a compiler that generates code employed by back-end
tools." The default back end produces `vvp` code that is then executed by the
`vvp` runtime — so the *tool* is a compiler, but the *runtime* is a conventional
event-driven interpreter.

On standards: it targets "ALL of the Verilog HDL, as described in the IEEE 1364
standard" and additionally "a (slowly growing) subset of the SystemVerilog
language, as described in the IEEE 1800 standard"
([Icarus Verilog `README.md`, master, accessed 2026-09-08](https://github.com/steveicarus/iverilog/blob/master/README.md))
**[docs]**.

### 2.2 SystemVerilog coverage — the honest version

The README is unusually frank, and the chapter should not oversell Icarus:
Icarus Verilog "is in development" and "still only supports a (growing) subset
of Verilog," and on SystemVerilog specifically, "**the list of unsupported
SystemVerilog constructs is too large to enumerate here**" (ibid.) **[docs]**.

Operational consequence for the book: Icarus is a reliable four-state,
event-driven Verilog-2005 simulator with partial SystemVerilog. Chapter 4's
worked example must be written in the intersection — Verilog-2005-style RTL plus
whatever SystemVerilog the example genuinely needs — and must be verified to run
on both tools rather than assumed to.

cocotb states its floor as "cocotb supports Icarus 11.0+"
([cocotb, simulator support, accessed 2026-09-08](https://docs.cocotb.org/en/stable/simulator_support.html))
**[docs]**. The documentation site currently points at Release V13.0
([Icarus Verilog documentation, accessed 2026-09-08](https://steveicarus.github.io/iverilog/))
**[docs]**.

### 2.3 A documented, deliberate scheduling deviation

This is the most valuable single fact in the Icarus documentation for Chapter 4,
because it is a maintainer stating in writing that the tool departs from the
standard scheduling order to avoid a race:

> "Icarus Verilog slightly modifies time 0 scheduling by arranging for always
> statements with ANYEDGE sensitivity lists to be scheduled before any other
> threads."

([Icarus Verilog, "Icarus Verilog Quirks," `Documentation/usage/icarus_verilog_quirks.rst`, master, accessed 2026-09-08](https://github.com/steveicarus/iverilog/blob/master/Documentation/usage/icarus_verilog_quirks.rst))
**[docs]**. The stated purpose is to ensure combinational `always` blocks trigger
when their sensitivity-list values are initialized by `initial` threads.

The same page documents further intentional deviations, useful as evidence that
tools diverge in ordinary, non-exotic places: unsized numeric constants are not
truncated ("Icarus Verilog does not truncate at all. It will make the unsized
constant as big as it needs to be to hold the value accurately"), unsized
expressions are widened to avoid overflow with `-gstrict-expr-width` restoring
standard behavior, and macro scope across library modules is restricted so that
results do not depend on load order (ibid.) **[docs]**. Note the shape of that
last one: a deliberate deviation whose *purpose* is to remove an order
dependence — the phenomenon Chapter 4 is about, admitted by a tool author.

---

## 3. Do conforming simulators disagree? (the answer to C)

**Yes — and it is documented from two directions: by tool authors describing
their own divergence, and by conference-paper authors describing the class of
problem. What could not be obtained is a single peer-reviewed study that runs
race-sensitive source on multiple simulators and tabulates the disagreement.**

### 3.1 The strongest general citable statement

From a SNUG conference paper by three well-known practitioners (one of them then
at Synopsys), under the heading "Not all tools implement the Verilog and
SystemVerilog standards in the same way":

> "Software tools do not always execute Verilog and SystemVerilog code in the
> same way. This is not a problem with the definition of the Verilog and
> SystemVerilog languages; it is a problem with software tools. Nevertheless,
> these differences can result in unexpected simulation and synthesis
> differences."

and, under "Ambiguities in the IEEE standards":

> "Two types of ambiguities occasionally occur in these complex documents: the
> rule for a corner case usage of the language is not covered, or different
> sections of the LRMs describe conflicting rules. These ambiguities in the
> standards can lead to differences in tool behavior."

Stuart Sutherland (Sutherland HDL), Don Mills (LCDM Engineering) and Chris Spear
(Synopsys), *Gotcha Again: More Subtleties in the Verilog and SystemVerilog
Standards That Every Engineer Should Know*, SNUG San Jose, 2007, pp. 3–4
([PDF, accessed 2026-09-08](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf))
**[primary]**. The paper is a continuation of *Standard Gotchas: Subtleties in
the Verilog and SystemVerilog Standards That Every Engineer Should Know*, SNUG
Boston, 2006, by the first two authors.

A caution the chapter must respect: this paper attributes divergence to *tool
implementations and standard ambiguities*, not to the standard's deliberate
scheduling nondeterminism. Those are different mechanisms and the chapter should
not conflate them.

### 3.2 Tool documentation admitting divergence

Two first-party admissions, both quoted in full above, are the load-bearing
citations:

- Verilator: "This may make the expression yield a different result than a
  four-state simulator," and "A compliant simulator will only calculate y if x
  changes" ([language limitations](https://verilator.org/guide/latest/languages.html))
  **[docs]**.
- Icarus Verilog: "Icarus Verilog slightly modifies time 0 scheduling…"
  ([quirks](https://github.com/steveicarus/iverilog/blob/master/Documentation/usage/icarus_verilog_quirks.rst))
  **[docs]**.

These two together are sufficient to license the chapter's worked example
without any appeal to the LRM: one tool documents that it is two-state and
follows synthesis event semantics; the other documents that it reorders time-0
scheduling. Two tools, two documented departures, one source file.

### 3.3 A conformance test suite exists

`sv-tests` is "a test suite designed to check compliance with the SystemVerilog
standard," maintained by CHIPS Alliance. It runs a large corpus across tools
including Yosys, Verilator, Icarus Verilog, slang, sv2v, sv-parser, moore,
verible, circt-verilog and yosys-slang, and reports which features each supports
([CHIPS Alliance `sv-tests`, accessed 2026-09-08](https://github.com/chipsalliance/sv-tests))
**[primary]**. Important limitation to state honestly: it is predominantly a
*parsing and elaboration* support matrix, not a runtime-semantics differential
tester, so it evidences "tools support different subsets," not "tools compute
different values."

### 3.4 What is missing

No published differential-testing study of simulator *runtime* semantics on
race-sensitive RTL was located. If the chapter wants a claim of the form "study
X ran N simulators on racy code and found disagreement in M cases," that claim
currently has no source and must not be made (§6).

---

## 4. Other open simulators

- **GHDL** — VHDL simulator. cocotb supports "GHDL 2.0+," with a caveat worth
  quoting because it is the same class of limitation as Verilator's two-state
  model: GHDL "implements the VPI interface. This prevents cocotb from accessing
  some VHDL-specific constructs, like 9-value signals"
  ([cocotb simulator support, accessed 2026-09-08](https://docs.cocotb.org/en/stable/simulator_support.html))
  **[docs]**. Actively maintained.
- **NVC** — "VHDL compiler and simulator" that compiles VHDL to native machine
  code via LLVM. Default standard VHDL-2008, with full VHDL-1993/2000/2002 and
  experimental Verilog and VHDL-2019 support; latest release 1.22.1
  ([NVC repository, accessed 2026-09-08](https://github.com/nickg/nvc))
  **[docs]**. Actively maintained; cocotb requires "NVC version 1.19.1 or later."
- **Surelog / UHDM** — **not a simulator.** Surelog is a "SystemVerilog 2017
  Pre-processor, Parser, Elaborator, UHDM Compiler," producing a UHDM database
  that third-party synthesis, simulation, linting and formal tools read through
  the standard VPI API; maintained by CHIPS Alliance
  ([Surelog repository, accessed 2026-09-08](https://github.com/chipsalliance/Surelog))
  **[docs]**. The chapter should describe it as a front end that other tools sit
  behind, never as a simulator.
- **CXXRTL** — a Yosys back end (`write_cxxrtl`) that emits C++ from a
  synthesized netlist; it lives in the Yosys tree at `backends/cxxrtl` and is
  maintained with Yosys
  ([YosysHQ/yosys `backends/cxxrtl`, accessed 2026-09-08](https://github.com/YosysHQ/yosys/tree/main/backends/cxxrtl))
  **[docs]**. Because it simulates a netlist rather than RTL source, it is even
  further from the standard's process semantics than Verilator. No first-party
  prose description of its value semantics was retrievable (§8).
- **cocotb's full supported list**, a snapshot of what a Python testbench can
  drive: Icarus Verilog (11.0+), Verilator (5.036+), GHDL (2.0+), NVC (1.19.1+),
  Synopsys VCS, Aldec Riviera-PRO and Active-HDL, Siemens EDA Questa, ModelSim
  and DSim (experimental), Cadence Incisive and Xcelium, and Tachyon DA CVC
  (ibid.) **[docs]**.

---

## 5. Performance, as far as it is sourced

There is **no independent measured comparison** of event-driven versus
compiled-code simulator performance that could be retrieved. What exists is the
Verilator project's own claim, on its project page, which the chapter must
present as a project claim and never as a result:

> "compiled Verilog model that executes even on a single thread over 10x faster
> than standalone SystemC"; "on a single thread is about 100 times faster than
> interpreted Verilog simulators"; "Another 2-10x speedup might be gained from
> multithreading (yielding 200-1000x total over interpreted simulators)";
> "Verilator has typically similar or better performance versus closed-source
> Verilog simulators."

([Verilator project page, veripool.org, accessed 2026-09-08](https://www.veripool.org/verilator))
**[vendor]**.

No benchmark, design, workload or methodology accompanies these numbers. If
Chapter 4 uses them at all, they must be attributed in the text as the Verilator
project's own claims, per the house rule on vendor figures. The defensible
sourced statement is qualitative: Verilator compiles to C++ and schedules
statically, which removes per-event runtime dispatch (§1.2); the magnitude of
the resulting speedup is unsourced.

---

## 6. Commonly repeated but unsourced claims

| Claim often repeated | Status |
|---|---|
| "Verilator is a cycle-based simulator." | **False as stated.** It schedules statically and iterates Active/NBA regions to convergence (§1.2), and with `--timing` it suspends processes on delays and event controls (§1.3). |
| "Compiled simulation is 10–100x faster than event-driven." | **Unsourced.** Only the Verilator project's own unbenchmarked figures were found (§5). |
| "Verilator is two-state, so it cannot find reset bugs." | **Contradicted by the docs**, which claim `--x-initial unique` finds "many that a four-state simulator will miss" (§1.4). What it cannot do is propagate X or evaluate `===` against X. |
| "Study X showed N simulators disagree on racy code." | **No such study located** (§3.4). Do not make this claim. |
| "Icarus Verilog supports SystemVerilog." | **Overstated.** Its README says the unsupported list "is too large to enumerate here" (§2.2). |
| "`--timing` makes Verilator event-driven." | **Overstated.** It adds coroutine-based suspension; event controls at the top of a process remain statically scheduled (§1.3). |
| "Two conforming simulators may disagree because the standard permits nondeterminism." | **Plausible but not sourced here.** The sourced mechanisms are tool-implementation differences and LRM ambiguities (§3.1) plus documented deliberate deviations (§3.2). Do not attribute the disagreement to LRM clause text without a citable secondary source. |

---

## 7. Suggested BibTeX keys

- `verilator-guide` — Verilator User's Guide, version 5.052, `https://verilator.org/guide/latest/`
- `verilator-languages` — Verilator User's Guide, "Language Limitations," 5.052
- `verilator-internals` — Verilator developer documentation, `docs/internals.rst`, master branch
- `verilator-project` — Verilator project page, Veripool, `https://www.veripool.org/verilator`
- `iverilog-readme` — Icarus Verilog, project README, master branch
- `iverilog-quirks` — Icarus Verilog, "Icarus Verilog Quirks," `Documentation/usage/icarus_verilog_quirks.rst`
- `sutherland2007gotcha` — Sutherland, Mills and Spear, *Gotcha Again: More Subtleties in the Verilog and SystemVerilog Standards That Every Engineer Should Know*, SNUG San Jose, 2007
- `sutherland2006gotcha` — Sutherland and Mills, *Standard Gotchas: Subtleties in the Verilog and SystemVerilog Standards That Every Engineer Should Know*, SNUG Boston, 2006
- `chipsalliance-svtests` — CHIPS Alliance, `sv-tests`
- `chipsalliance-surelog` — CHIPS Alliance, Surelog
- `cocotb-simulators` — cocotb documentation, "Simulator Support"
- `nvc` — Gunning, NVC VHDL compiler and simulator

---

## 8. Confidence notes and gaps

**High confidence.** All of §1 and §2 is first-party documentation quoted
directly. The Verilator Active/NBA statement (§1.2) and the Icarus time-0
scheduling statement (§2.3) are the best-evidenced facts here and are strong
enough to carry the chapter's worked example on their own.

**Medium confidence.**

- **Which Verilator release introduced `--timing`.** Not verified — `Changes`
  could not be read back far enough. Say "Verilator 5.x," or check `Changes`
  locally before naming a version.
- **C++17 vs C++20 for `--timing`.** The option page gives the compiler floor as
  "GCC 10, Clang 5, or newer"; the developer docs call coroutines "a new feature
  in C++20." Quote the compiler versions, not a standard year.
- **Version currency.** Docs read here render as Verilator 5.052 ("5.053 devel"
  at the top of `Changes`); Icarus documentation points at Release V13.0.
  Re-check at publication and always state the version.

**Gaps.**

1. **The Cummings SNUG papers could not be obtained** (sunburst-design.com now
   redirects to a login-walled library). They are the canonical practitioner
   references on nonblocking assignments and SystemVerilog event regions;
   someone with access should retrieve *SystemVerilog Event Regions, Race
   Avoidance & Guidelines* (SNUG Boston, 2006).
2. **No differential-testing study** of simulator runtime semantics (§3.4).
3. **CXXRTL** has no retrievable first-party prose description; its value
   semantics were not verified and are not asserted above.
4. **Icarus `vvp` runtime internals** are not documented in
   `Documentation/usage/`. Its four-state event-queue behavior is inferred from
   its IEEE 1364 conformance claim, not from a page describing the queue —
   describing that queue concretely needs a source this note lacks.
5. **Verilator's `Changes`** and the **`sv-tests` results dashboard** were not
   read in full; both deserve a local pass before drafting.
