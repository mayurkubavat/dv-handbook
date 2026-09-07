---
title: "Research note: Chapter 3 — Digital Design for Verifiers"
date: 2026-09-07
author: research-agent
status: complete
feeds: Ch. 3
---

# Chapter 3 — Digital Design for Verifiers: evidence note

Scope: RTL and synthesis, clocks and resets, metastability and crossings, state
machines, pipelines and handshakes and queues, block-boundary interfaces, the
verifier's reading of RTL (lint and X), and the structural facts a tool can
extract from RTL without a simulator. Every claim is cited as
`[Source, YYYY-MM-DD](URL)`; the date is the source's own where it has one and
the access date otherwise. Sources are labelled **[standard]**, **[primary]**,
**[vendor]**, **[research]**, **[industry paper]** or **[docs]**. Vendor claims
are kept separate from measured or peer-reviewed results. The AI-assistant
vendor's own materials are not cited, per the repository publication rule.

The note was gathered in three independent passes and is kept in three parts.
**Section numbers are local to their part**: a reference to "§2.3" inside Part A
means Part A's §2.3. Each part carries its own unsourced-claims table, BibTeX
suggestions and confidence notes, because each was assembled against different
sources and the confidence differs accordingly.

## Which part feeds which chapter section

| Chapter section | Part | Sections there |
|---|---|---|
| 3.1 What RTL is, and what synthesis makes of it | A | §1 |
| 3.2 Clocks | B | §1, §2 |
| 3.3 Resets | B | §3 |
| 3.4 State machines | A | §2 |
| 3.5 Pipelines, handshakes and queues | C | §1 |
| 3.6 Interfaces | C | §2 |
| 3.7 The verifier's reading, as a procedure | A | §3 (lint, X) |
| 3.8 Worked example: reading a design with a tool | C §3, B §4 | extraction formats; limits of static analysis |

## What the chapter must not assert

Collected from all three parts. Each is a gap in the evidence, not a matter of
style.

1. **No IEEE clause numbers or clause paraphrases.** IEEE 1800 (all editions),
   IEEE 1364.1-2002, ISO 26262 and DO-254 are paywalled and were not read. Name
   them; do not quote them, describe their contents, or write "the standard
   requires...". For `always_ff` / `always_comb` / `always_latch` semantics cite
   Cummings 2016 instead (Part A §1.2).
2. **No ARM AXI clause number or ARM wording.** Every route to IHI 0022 and
   IHI 0024 failed (Part C §6). Use the SiFive TileLink specification's flow
   control rules as the quotable open-standard anchor, and say plainly that
   TileLink beats are revocable where AXI's are not, or the chapter teaches the
   wrong rule.
3. **No numbers for lint yield or CDC waiver volume.** Neither is sourced.
   The *existence* of CDC false violations is sourced; no count is.
4. **"Simulation cannot reproduce an unsynchronized crossing" needs its exact
   wording.** Sourced five ways, but as "does not model metastability and
   diverges from silicon in both directions", never as "simulation always passes
   a broken crossing" (Part B §7).
5. **Two flip-flops are not unconditionally adequate.** The same structure gives
   4x10^29 years or about a minute depending on the technology and data rate
   (Part B §2.1). Never state the rule without its conditions.
6. **Verible corresponds to the lowRISC style guide; it does not claim to
   implement it** (Part A §4).
7. **The Cummings SNUG papers' author line is unverified** for the FIFO papers
   at the successor site (Part C §6); Part A read the same papers from archived
   captures and does have the author. Prefer Part A's citation.

What the chapter *may* now assert, which it previously could not: that these
linters do not check clock-domain crossings. Verilator documents `CDCRSTLOGIC`
as "Historical, never issued since version 5.008" and `CLKDATA` likewise, and
Verible's rule list contains no crossing rules at all (Part A §3.1, §3.3). That
is positive documentation, not an absence of evidence, and it is what makes the
worked example's contrast honest.



# Part A — RTL and synthesis, state machines, lint and X

Source access: `sunburst-design.com/papers/` now 301-redirects to
`paradigm-works.com`, whose index requires registration and exposes no PDF
links. The Cummings/Mills papers were therefore read from Internet Archive
captures of the original URLs; canonical URL and capture date are both given.
IEEE 1800 and IEEE 1364.1 clause text is paywalled and was **not** read — §6.

---

### 1. What RTL is, and what synthesis makes of it

#### 1.1 The synthesizable subset and the IEEE definition

The synthesizable subset is fixed not by the simulation language but by a
separate standard: IEEE Std 1364.1-2002, *IEEE Standard for Verilog Register
Transfer Level Synthesis*. Cummings, who sat on the working group, calls it "the
IEEE Std. 1364.1-2002 standard (RTL synthesis standard)" **[primary]**
([Cummings, *SystemVerilog Logic Specific Processes for Synthesis*, SNUG Silicon
Valley 2016, ref. [6]](http://www.sunburst-design.com/papers/CummingsSNUG2016SV_SVLogicProcs.pdf);
capture 2018-02-19).

Mills and Cummings state the governing principle: "any coding style that gives
the HDL simulator information about the design that cannot be passed on to the
synthesis tool is a bad coding style. Additionally, any synthesis switch that
provides information to the synthesis tool that is not available to the
simulator is bad." The consequence is silicon risk, not style: "Frequently,
these mismatches are not discovered until after silicon has been generated, and
thus require the design to be re-submitted for a second spin" **[primary]**
([Mills & Cummings, *RTL Coding Styles That Yield Simulation and Synthesis
Mismatches*, SNUG San Jose 1999](http://www.sunburst-design.com/papers/CummingsSNUG1999SJ_SynthMismatch.pdf);
capture 2006-01-12).

#### 1.2 `always_ff` / `always_comb` / `always_latch` as checked intent

SystemVerilog's three logic-specific processes exist to make designer intent
machine-checkable. Cummings: these processes "were intended to show designer
intent and to enable tools to help RTL coders identify problems earlier in the
design flow" **[primary]**
([Cummings, SNUG SV 2016, §5](http://www.sunburst-design.com/papers/CummingsSNUG2016SV_SVLogicProcs.pdf)).

From the same paper (§5.1–5.3, §7.4) **[primary]**:

- `always_comb` "automatically builds the proper sensitivity list required by
  the simulator ... builds a better sensitivity list than the Verilog-2001
  `always @*`", is "sensitive to changes within the contents of a function",
  and "triggers once automatically at the end of time-0".
- `always_ff` "is used to describe clocked logic but it does NOT automatically
  build the proper sensitivity list" — the information is not in the body.
- "always_comb variables cannot be assigned from another process."
- "always_comb cannot include blocking delays."

Two limits the chapter should carry:

1. **The checks are compile-time simulator checks, not synthesis contracts.**
   "synthesis behavior regarding the implementation of always_type processes is
   not defined by any IEEE Standard" (§9.4) **[primary]**.
2. **Tools warn where they should error.** The paper's own subtitle for §8 is
   "Simulators can warn of incorrectly inferred logic - they don't", and it
   states that IEEE Std 1800-2012 "permits simulators the option to warn users
   if the RTL coding style would not infer the intended and requested logic when
   synthesized. This action is purely optional and there are no known simulators
   that issue these useful warnings" **[primary]**. Cummings' stated preference
   is "that vendors change the always_type warnings to errors" (§9.4).

Verilator does implement one half of the check pair: `NOLATCH` "Warns that no
latch was detected in an `always_latch` block" **[vendor]**
([Verilator warnings, accessed 2026-09-07](https://verilator.org/guide/latest/warnings.html)).

#### 1.3 Simulation/synthesis mismatch: the classic causes

All of the following are documented, with worked examples, in Mills & Cummings
1999 **[primary]** (section numbers theirs):

- **§2.1 Incomplete sensitivity list.** "The synthesized logic described by the
  equations in an always block will always be implemented as if the sensitivity
  list were complete. However, the pre-synthesis simulation functionality of
  this same always block will be quite different." A block with an empty
  sensitivity list "will lock up the simulator into an infinite loop", while the
  synthesized result is still an AND gate.
- **§2.2 Complete sensitivity list with mis-ordered assignments** (the blocking-
  assignment ordering hazard in combinational blocks).
- **§3.0 Functions.** "Since there are no synthesis tool warnings when function
  code simulates latch behavior, the practice of using functions to model
  synthesizable combinational logic is dangerous."
- **§4.1–4.2 `full_case` / `parallel_case`.**
- **§4.3 `casex`.** "A casex treats 'X's as 'don't cares' if they are in either
  the case expression or the case items ... The pre-synthesis simulation will
  treat the unknown input as a 'don't care' when evaluated in the casex
  statement. The equivalent post-synthesis simulation will propagate 'X's
  through the gate-level model." The paper reports a company whose design
  "erroneously initialized ... to a working state" in RTL simulation this way.
- **§4.4 `casez`** — same failure mode, triggered by `z`, judged less likely to
  be missed.
- **§5.1 Assigning `X`.** "The 'X' assignment is interpreted as an unknown by the
  Verilog simulator ... but is interpreted as a 'don't care' by synthesis tools."
- **§5.2, §6.0 `translate_off` / `translate_on`**; **§7.0 Timing delays.**

On blocking vs non-blocking, the canonical statement is Cummings' eight
guidelines **[primary]**
([*Nonblocking Assignments in Verilog Synthesis, Coding Styles That Kill!*, SNUG
San Jose 2000](http://www.sunburst-design.com/papers/CummingsSNUG2000SJ_NBA.pdf);
capture 2025-07-17), quoted verbatim:

> Guideline #1: When modeling sequential logic, use nonblocking assignments.
> Guideline #2: When modeling latches, use nonblocking assignments.
> Guideline #3: When modeling combinational logic with an always block, use
> blocking assignments.
> Guideline #4: When modeling both sequential and combinational logic within the
> same always block, use nonblocking assignments.
> Guideline #5: Do not mix blocking and nonblocking assignments in the same
> always block.
> Guideline #6: Do not make assignments to the same variable from more than one
> always block.
> Guideline #7: Use $strobe to display values that have been assigned using
> nonblocking assignments.
> Guideline #8: Do not make assignments using #0 delays.

He claims, without measurement, that "Adherence to these guidelines will also
remove 90-100% of the Verilog race conditions encountered by most Verilog
designers" — an expert estimate, not a measurement (see §4). His definition of
the hazard: "A Verilog race condition occurs when two or more statements that
are scheduled to execute in the same simulation time-step ... would give
different results" (§2.0), grounded in the standard's "Nondeterminism" and "Race
conditions" clauses.

On `full_case`/`parallel_case` **[primary]** ([*"full_case parallel_case", the
Evil Twins of Verilog Synthesis*, SNUG Boston 1999](http://www.sunburst-design.com/papers/CummingsSNUG1999Boston_FullParallelCase.pdf);
capture 2022-12-04): "the 'full_case parallel_case' switches frequently make
designs larger and slower and can obscure the fact that latches have been
inferred. These switches can also change the functionality of a design causing a
mismatch between pre-synthesis and post-synthesis simulation." And: "these
directives are always most dangerous when they work!" His guidelines include
"Do not use casex for synthesizable code" and "In general, do not use 'full_case
parallel_case' directives with any Verilog case statement", with one exception:
"only use full_case parallel_case to optimize onehot FSM designs."

### 2. State machines

#### 2.1 Coding styles and encodings

The oldest widely cited treatment is Golson's, which introduces both the two-
block (Figure 1) and one-block (Figure 2) organizations and surveys encodings
including one-hot and "almost one-hot" **[industry paper]**
([Golson, *State machine design techniques for Verilog and VHDL*, Synopsys
Journal of High-Level Design, 1994](https://www.trilobyte.com/pdf/golson_snug94.pdf)).
He records why one-hot is chosen: "One-hot state machines are typically faster",
and decode is simplified because a single bit indicates the state.

Cummings 1998 enumerates the encodings in use — "highly-encoded binary (or
binary-sequential), gray-code, Johnson, one-hot, almost one-hot and one-hot with
zero-idle" **[primary]** ([*State Machine Coding Styles for Synthesis*, SNUG San
Jose 1998](http://www.sunburst-design.com/papers/CummingsSNUG1998SJ_FSM.pdf);
capture 2006-06-22).

The modern style comparison is Cummings & Chambers, describing "at least seven
different Finite State Machine (FSM) design techniques ... one with combinatorial
outputs and six with registered outputs" and benchmarking four **[primary]**
([*Finite State Machine (FSM) Design & Synthesis using SystemVerilog - Part I*,
SNUG Silicon Valley 2019](http://www.sunburst-design.com/papers/CummingsSNUG2019SV_FSM1.pdf);
capture 2025-09-11). Measured on four benchmark FSMs synthesized for ASIC: "The
1-always block and 4-always block coding styles typically gave slightly better
synthesis area and timing performance over the 3-always block style, but we
recommend using the efficient 3-always block style and then converting it to a
4-always block style if slightly better synthesis performance is needed." On
coding effort, for the larger `prep4` design the 1-always style "was more than
twice as hard as coding the 3-always block style."

The lowRISC/OpenTitan style guide mandates a narrower rule: "State machines use
an enum to define states, and must be implemented with two process blocks: a
combinational block and a clocked block", with the next-state default set to the
current state before the `unique case` **[industry paper]**
([lowRISC Verilog Coding Style Guide, accessed 2026-09-07](https://github.com/lowRISC/style-guides/blob/master/VerilogCodingStyle.md)).

#### 2.2 Unreachable, illegal, deadlock: the verifier's reading

Cummings 1998 names the three default next-state assignments and when each is
wrong **[primary]**: "(1) `next` is set to all x's, (2) `next` is set to a
predetermined recovery state such as IDLE, or (3) `next` is just set to the
value of the state register." The `x` default is a *debug* device — "pre-
synthesis simulation models will cause the state machine outputs to go unknown
if not all state transitions have been explicitly assigned" — but "the x's will
be treated as 'don't cares' by the synthesis tool", i.e. it deliberately creates
the §1.3 mismatch. He names the domains where that is unacceptable: "Examples
include: satellite applications, medical applications, designs that use the FSM
flip-flops as part of a diagnostic scan chain and designs that are equivalence
checked with formal verification tools."

The lowRISC guide's example marks the `default:` arm "may be empty or used to
catch parasitic states", assigning `StIdle` **[industry paper]** (same URL).

For security- and safety-hardened FSMs, OpenTitan's guidance is to "Use a
sparsely populated state encoding, with all others marked invalid" and to "Have
a minimum Hamming distance for state machine transitions, to make single bit
faults non-effective" **[industry paper]**
([OpenTitan Secure Hardware Design Guidelines, accessed 2026-09-07](https://opentitan.org/book/doc/security/implementation_guidelines/hardware/index.html)).
Note the limit: that page prescribes *detection* (alerts, "clearing/randomizing
state, cease processing") but does not mandate a specific recovery action on
invalid state.

#### 2.3 Coverage and formal

The natural coverage model is state plus transition. OpenTitan defines both
**[industry paper]**
([OpenTitan DV methodology, accessed 2026-09-07](https://opentitan.org/book/doc/contributing/dv/methodology/index.html)):
FSM state coverage "measures which finite state machine states were executed
during a simulation"; FSM transition coverage "measures which arcs were
traversed for each finite state machine in the design." They also observe the
overlap with branch coverage: "FSM states and transitions not covered almost
always shows up as branches not covered as well."

An open-source tool implements exactly this pair: "With `--coverage` or
`--coverage-fsm`, Verilator can instrument a conservative subset of FSMs and
report both state coverage (`fsm_state`) and transition coverage (`fsm_arc`)"
**[vendor]**
([Verilator, Simulating, accessed 2026-09-07](https://verilator.org/guide/latest/simulating.html)).
"Conservative subset" is the caveat, enforced by a warning: `FSMMULTI` "Warns
that the same always block contains multiple enum-typed case statements that
look like FSM candidates ... Verilator's FSM coverage instruments only the first
such candidate in source order" **[vendor]**
([Verilator warnings](https://verilator.org/guide/latest/warnings.html)).

That formal, not simulation, is the tool for unreachability is stated plainly in
practice: "VCS UNR (Unreachability) is a formal solution that determines the
unreachable coverage objects automatically from simulation ... Instead of
manually reviewing coverage reports to find unreachable code, we use VCS UNR to
generate a UNR exclusion file" **[industry paper]** (OpenTitan DV methodology,
same URL). The underlying algorithm is symbolic FSM reachability analysis
**[research]** ([Coudert, Berthet & Madre, LNCS, Springer,
1990](https://doi.org/10.1007/3-540-52148-8_30)); the frame for deadlock and
liveness properties is model checking **[research]** ([Clarke & Emerson, LNCS
131, Springer-Verlag](https://doi.org/10.1007/BFb0025774)). For coverage metrics
as a research subject, the standard survey is **[research]** ([Tasiran &
Keutzer, IEEE Design & Test of Computers,
2001](https://doi.org/10.1109/54.936247)).

### 3. Lint and X

#### 3.1 Verilator warning classes

Verilator's warning list carries 136 named warning identifiers, 18 of which are
marked "Disabled by default" **[vendor]** (counted from
[Verilator warnings, accessed 2026-09-07](https://verilator.org/guide/latest/warnings.html)).
`--lint-only` "Check the files for lint violations only, do not create any other
output. You may also want the `-Wall` option to enable messages considered
stylistic and not enabled by default"; `-Wall` is documented as "Enable all
style warnings" **[vendor]**
([Verilator, verilator command, accessed 2026-09-07](https://verilator.org/guide/latest/exe_verilator.html)).

Verbatim descriptions of the classes the chapter uses **[vendor]** (same
warnings page):

| Warning | Documented description (verbatim, abridged where marked) |
|---|---|
| `WIDTH` | "Two operands have different widths, e.g., adding a 2-bit and 5-bit number." |
| `WIDTHEXPAND` | "A more granular WIDTH warning, for when a value is zero expanded." |
| `WIDTHTRUNC` | "A more granular WIDTH warning, for when a value is truncated." |
| `LATCH` | "Warns that a signal is not assigned in all control paths of a combinational always block, resulting in the inference of a latch. For intentional latches, consider using the always_latch (SystemVerilog) keyword instead." |
| `NOLATCH` | "Warns that no latch was detected in an always_latch block." |
| `ALWCOMBORDER` | "Warns that an always_comb block reads a variable before assigning it later in the same block ... This can imply latch/state-like behavior and is not purely combinational." |
| `BLKSEQ` | "This indicates that a blocking assignment (=) is used in a sequential block ... Disabled by default as this is a code-style warning; it will simulate correctly." |
| `COMBDLY` | "Warns that there is a delayed assignment inside of a combinatorial block ... may lead to the simulator not matching synthesis." |
| `CASEINCOMPLETE` | "Warns that inside a case statement, there is a stimulus pattern for which no case item is provided. This is bad style; if a case is impossible, it's better to have a `default: $stop;` ..." |
| `CASEX` | "Warns that it is better style to use casez, and '?' in place of 'x's." |
| `CASEWITHX` | "Warns that a case statement contains a constant with an x. Verilator is two-state so interpret such items as always false." |
| `MULTIDRIVEN` | "Warns that the specified signal has multiple procedural drivers. One case is when the signal comes from multiple always blocks, each with different clocking. This warning does not look at individual bits ... This is considered bad style, as the consumer of a given signal may be unaware of the inconsistent clocking, causing clock domain crossing or timing bugs." |
| `UNOPTFLAT` | "Warns that due to some construct, optimization of the specified signal is disabled ... Often UNOPTFLAT is caused by logic that isn't truly circular as viewed by synthesis, which analyzes interconnection per bit, but is circular to the IEEE event model which analyzes per-signal." |
| `SYNCASYNCNET` | "Warns that the specified net is used in at least two different always statements with posedge/negedges ... Mixing sync and async resets is usually a mistake. Disabled by default as this is a code-style warning; it will simulate correctly." |

Two of these entries cite Cummings' SNUG papers by URL inside Verilator's own
documentation (`CASEX` → the `full_case parallel_case` paper; `COMBDLY` → the
nonblocking-assignments paper): a useful line on how the primary literature
became tool policy **[vendor]**.

#### 3.2 Verible rules

Verible's published SystemVerilog lint rule list contains 61 rules, of which 42
are marked "Enabled by default: true" and 19 "false" **[vendor]** (counted from
[chipsalliance/verible `lint.md` (gh-pages), accessed 2026-09-07](https://github.com/chipsalliance/verible/blob/gh-pages/lint.md);
rendered at <https://chipsalliance.github.io/verible/lint.html>).

The rules relevant to §1 are `always-comb` ("Checks that there are no
occurrences of `always @*`. Use `always_comb` instead. See [Style:
combinational-logic]"), `always-comb-blocking`, `always-ff-non-blocking`, and
`case-missing-default` **[vendor]** (same file). Verilator's `BLKSEQ` entry
cross-references the Verible rule explicitly: "Other tools with similar
warnings: Verible's always-ff-non-blocking" **[vendor]**.

On style-guide basis: Verible's README says the linter "identifies constructs or
patterns in code that are deemed undesirable according to a style guide"
**[vendor]** ([chipsalliance/verible README, accessed 2026-09-07](https://github.com/chipsalliance/verible/blob/master/README.md)),
and the tool README adds "Ideally, each lint rule should reference a passage
from an authoritative style guide" **[vendor]**
([verible/verilog/tools/lint/README.md, accessed 2026-09-07](https://github.com/chipsalliance/verible/blob/master/verible/verilog/tools/lint/README.md)).
The open-source citation helper emits only a bare topic tag — `GetStyleGuideCitation`
returns `absl::StrCat("[Style: ", topic, "]")` with no URL **[vendor]**
([verible/common/analysis/citation.cc, accessed 2026-09-07](https://github.com/chipsalliance/verible/blob/master/verible/common/analysis/citation.cc)).
So the guide is **not named in the open-source distribution**. The topic tags
(`combinational-logic`, `sequential-logic`, `constants`, `generate-constructs`,
…) match section names in the lowRISC style guide, but I found no statement in
Verible's own repository asserting that mapping — see §4.

#### 3.3 What lint structurally cannot find

The cleanest source for lint's scope limits is Verible's own tool README, which
states them as design properties rather than bugs **[vendor]**
([verible/verilog/tools/lint/README.md](https://github.com/chipsalliance/verible/blob/master/verible/verilog/tools/lint/README.md)),
quoted verbatim:

> The style linter operates on *single unpreprocessed files* in isolation.
>
> The style linter excels at:
> * Finding patterns in code that can be expressed in terms of syntax tree or
>   token matching rules.
>
> Currrent limitations:
> * No attempt to understand preprocessing conditional branches.
> * No semantic analysis (such as connectivity). This requires:
>   * preprocessing
>   * multi-file analysis
>   * abstract syntax tree

That is the chapter's argument in the tool's own words: single file, no
connectivity, syntax-tree pattern matching. The README also states the rules
"use syntax tree pattern matching to find style violations."

**Neither tool claims CDC checking.** Verible: no rule in the 61-rule list
mentions clock domain crossing, synchronizers or metastability (grep over
`lint.md` returns zero matches) **[vendor]**. Verilator once had a CDC option
and removed it: `CDCRSTLOGIC` is "Historical, never issued since version 5.008.
Warned with a no longer supported clock domain crossing option that asynchronous
flop reset terms came from other than primary inputs or flopped outputs,
creating the potential for reset glitches" **[vendor]**; the sibling `CLKDATA`
is likewise "Historical, never issued since version 5.000." `MULTIDRIVEN` and
`SYNCASYNCNET` *mention* clock domain crossing as a possible consequence of a
local pattern, but they are single-block structural checks, not domain analysis
— and `SYNCASYNCNET` is off by default.

The gap is physical, not architectural: "In a multi-clock design, metastability
cannot be avoided but the detrimental effects of metastability can be
neutralized" **[primary]**
([Cummings, *Clock Domain Crossing (CDC) Design & Verification Techniques Using
SystemVerilog*, SNUG Boston 2008](http://www.sunburst-design.com/papers/CummingsSNUG2008Boston_CDC.pdf);
capture 2009-08-24), quoting Dally and Poulton: "When sampling a changing data
signal with a clock ... the order of the events determines the outcome ... the
decision process can take longer than the time allotted, and a synchronization
failure occurs." Cummings assumes dedicated tooling and still warns that "there
is always the danger that the CDC analysis tool might not be setup correctly."

#### 3.4 X-propagation, X-optimism and X-pessimism

The primary source is Turpin **[primary]**
([*The Dangers of Living with an X (bugs hidden in your Verilog)*, v1.1,
2003-10-14, ARM Ltd.](https://www.averant.com/assets/pdf/Verilog_X_Bugs.pdf)).
His framing sentence: "The semantics of X in Verilog RTL are extremely dangerous
as RTL bugs can be masked, allowing RTL simulations to incorrectly pass where
netlist simulations can fail."

He separates the meanings X carries per tool — synthesis: don't-care;
simulation: unknown; `casex`/`casez`: wildcard; equivalence checking: 2-state
consistency or strict 2-state equality; formal property checking: 2-state
sequential (§2). The two effects, verbatim:

> 1. X-Pessimism: ambiguous results lead to more X-assignments than are really
>    necessary
> 2. X-Optimism: interpretation of X will take just one if/case branch when many
>    should be considered

His pessimism example is `assign b = a & ~a;`, identically zero in hardware but
`X` in simulation because "the unary negation operator propagates the X,
throwing away information that the new result should be a symbolic '~X'." His
optimism example is a clock-enable: "According to the Verilog LRM the second
branch is only executed if `CountEnable` is `1'b1`, so no update occurs when
`CountEnable` is X." Optimism "can also occur in a case default that terminates
X's with a 2-state (i.e. 0 or 1) assignment", and the effects corrupt code
coverage (§4.3). His ideal semantics — "can be either 0 or 1" — is what formal
tools use; he attributes earlier description of the two effects to Lionel
Bening. His remedies include X-propagation modes, replacing X-insertion with
assertions, and "Automatic formal proofs of unreachable (deadcode) assignments"
(§6.5), tying X handling back to §2.3.

The two-state counterexample matters for the chapter's tooling: "Verilator is
mostly a two-state simulator, not a four-state simulator"; assigning X "will
assign a constant value as determined by the `--x-assign` option. This allows
runtime randomization; thus, if the value is used, the random value should cause
downstream errors"; and "An `===` comparison to X will always be false"
**[vendor]** ([Verilator, Language Limitations, accessed 2026-09-07](https://verilator.org/guide/latest/languages.html)).
Randomized two-state initialization is a *different* technique from X
propagation, and a chapter running its examples on Verilator must say so.

### 4. Commonly repeated but unsourced claims

| Claim | Where it is repeated | Status |
|---|---|---|
| "Following the eight NBA guidelines removes 90–100% of Verilog race conditions" | Cummings SNUG 2000 §5.0, and everywhere downstream | **Author's estimate, no measurement.** Quote as his opinion or drop the number. |
| "Lint finds N% of RTL bugs" / "lint catches the cheap bugs" | Common in DV blog posts and vendor slides | **No source found.** Do not state a percentage. |
| "one-hot FSMs are faster / smaller in FPGAs" | Golson 1994 §3.2.2, repeated widely | Golson gives it as design rationale ("One-hot state machines are typically faster"), not as a measurement on a named library. Attribute, don't assert. |
| "Verilator/Verible do CDC checks" | Occasionally assumed | **False, and now positively documented as false**: `CDCRSTLOGIC` is "Historical, never issued since version 5.008"; Verible's rule list has zero CDC rules. |
| "Verible implements the lowRISC Verilog style guide" | Widely assumed | **Not stated in Verible's repo.** Topic tags match lowRISC section names; the code emits `[Style: <topic>]` with no URL. Low confidence — chapter should say "rule topics correspond to", not "implements". |
| "always_comb makes latch inference an error" | Common shorthand | **Overstated.** Cummings 2016 §9.4: synthesis behavior for these processes "is not defined by any IEEE Standard" and vendors issue warnings, not errors. |
| "Simulators warn when always_comb won't synthesize as combinational" | Implied by "checked intent" language | Cummings 2016 §8: permitted by IEEE 1800-2012 but "purely optional and there are no known simulators that issue these useful warnings" (as of 2016). Needs re-checking against 2026 tools. |
| "ISO 26262 / DO-254 require illegal-state recovery in FSMs" | Frequently asserted | **Not verified.** Both standards are paywalled and were not read. See §6. |

### 5. Suggested BibTeX keys

| Key | Full citation | Section |
|---|---|---|
| `cummings2000nba` | Cummings, Clifford E. "Nonblocking Assignments in Verilog Synthesis, Coding Styles That Kill!" SNUG San Jose, 2000. <http://www.sunburst-design.com/papers/CummingsSNUG2000SJ_NBA.pdf> (accessed 2026-09-07 via Internet Archive capture 2025-07-17) | §1.3 |
| `millscummings1999mismatch` | Mills, Don, and Clifford E. Cummings. "RTL Coding Styles That Yield Simulation and Synthesis Mismatches." SNUG San Jose, 1999. <http://www.sunburst-design.com/papers/CummingsSNUG1999SJ_SynthMismatch.pdf> | §1.1, §1.3 |
| `cummings1999fullparallel` | Cummings, Clifford E. "'full_case parallel_case', the Evil Twins of Verilog Synthesis." SNUG Boston, 1999. <http://www.sunburst-design.com/papers/CummingsSNUG1999Boston_FullParallelCase.pdf> | §1.3 |
| `cummings2016logicprocs` | Cummings, Clifford E. "SystemVerilog Logic Specific Processes for Synthesis — Benefits and Proper Usage." SNUG Silicon Valley, 2016. <http://www.sunburst-design.com/papers/CummingsSNUG2016SV_SVLogicProcs.pdf> | §1.1, §1.2 |
| `cummings1998fsm` | Cummings, Clifford E. "State Machine Coding Styles for Synthesis." SNUG San Jose, 1998. <http://www.sunburst-design.com/papers/CummingsSNUG1998SJ_FSM.pdf> | §2.1, §2.2 |
| `cummingschambers2019fsm` | Cummings, Clifford E., and Heath Chambers. "Finite State Machine (FSM) Design & Synthesis using SystemVerilog — Part I." SNUG Silicon Valley, 2019. <http://www.sunburst-design.com/papers/CummingsSNUG2019SV_FSM1.pdf> | §2.1 |
| `cummings2008cdc` | Cummings, Clifford E. "Clock Domain Crossing (CDC) Design & Verification Techniques Using SystemVerilog." SNUG Boston, 2008. <http://www.sunburst-design.com/papers/CummingsSNUG2008Boston_CDC.pdf> | §3.3 |
| `golson1994fsm` | Golson, Steve. "State machine design techniques for Verilog and VHDL." *Synopsys Journal of High-Level Design*, 1994. <https://www.trilobyte.com/pdf/golson_snug94.pdf> | §2.1 |
| `turpin2003x` | Turpin, Mike. "The Dangers of Living with an X (bugs hidden in your Verilog)." Version 1.1, ARM Ltd., Cambridge, UK, 2003-10-14. <https://www.averant.com/assets/pdf/Verilog_X_Bugs.pdf> | §3.4 |
| `verilator-warnings` | Verilator Manual, "Warnings." Veripool. <https://verilator.org/guide/latest/warnings.html> (accessed 2026-09-07) | §3.1, §3.3 |
| `verilator-languages` | Verilator Manual, "Language Limitations." <https://verilator.org/guide/latest/languages.html> (accessed 2026-09-07) | §3.4 |
| `verilator-simulating` | Verilator Manual, "Simulating (Coverage)." <https://verilator.org/guide/latest/simulating.html> (accessed 2026-09-07) | §2.3 |
| `verible-lint-rules` | CHIPS Alliance. "Verible SystemVerilog lint rule list." <https://chipsalliance.github.io/verible/lint.html> (accessed 2026-09-07) | §3.2 |
| `verible-lint-readme` | CHIPS Alliance. "SystemVerilog Style Linter" (verible/verilog/tools/lint/README.md). <https://github.com/chipsalliance/verible/blob/master/verible/verilog/tools/lint/README.md> (accessed 2026-09-07) | §3.3 |
| `lowrisc-verilogstyle` | lowRISC. "Verilog Coding Style Guide." <https://github.com/lowRISC/style-guides/blob/master/VerilogCodingStyle.md> (accessed 2026-09-07) | §2.1, §2.2 |
| `opentitan-dv-methodology` | OpenTitan Project. "Design Verification Methodology." <https://opentitan.org/book/doc/contributing/dv/methodology/index.html> (accessed 2026-09-07) | §2.3 |
| `opentitan-secure-hw` | OpenTitan Project. "Secure Hardware Design Guidelines." <https://opentitan.org/book/doc/security/implementation_guidelines/hardware/index.html> (accessed 2026-09-07) | §2.2 |
| `ieee1800-2023` | IEEE Std 1800-2023, *IEEE Standard for SystemVerilog — Unified Hardware Design, Specification, and Verification Language*. IEEE, published 2024-02-28. <https://standards.ieee.org/ieee/1800/7743/> | §1.2 |
| `ieee1364.1-2002` | IEEE Std 1364.1-2002, *IEEE Standard for Verilog Register Transfer Level Synthesis*. IEEE, 2002. (Record page not reachable at time of writing; cited from `cummings2016logicprocs` ref. [6].) | §1.1 |
| `coudert1990reachability` | Coudert, Olivier, Christian Berthet, and Jean Christophe Madre. "Verification of synchronous sequential machines based on symbolic execution." LNCS, Springer, 1990. <https://doi.org/10.1007/3-540-52148-8_30> | §2.3 |
| `clarke1981modelchecking` | Clarke, Edmund M., and E. Allen Emerson. "Design and synthesis of synchronization skeletons using branching time temporal logic." LNCS 131, Springer-Verlag. <https://doi.org/10.1007/BFb0025774> | §2.3 |
| `tasiran2001coverage` | Tasiran, Serdar, and Kurt Keutzer. "Coverage metrics for functional validation of hardware designs." *IEEE Design & Test of Computers*, 2001. <https://doi.org/10.1109/54.936247> | §2.3 |

### 6. Confidence notes and gaps

**High confidence.** Everything sourced to Verilator's and Verible's own
documentation and repository (§2.3, §3.1–§3.3) was read at the URLs given on
2026-09-07, and the rule and warning counts were counted mechanically.
Everything sourced to the Cummings/Mills/Turpin/Golson papers was read from the
PDFs and quoted verbatim.

**Gaps the chapter must not assert without more work:**

1. **IEEE 1800 clause language** — the biggest gap. IEEE 1800-2017/2023 is
   paywalled and no legitimate full text was reachable. Do not quote or
   paraphrase a clause number for `always_comb`, `always_latch` or `always_ff`,
   and do not write "the LRM requires tools to report X" until the author checks
   a copy. Safely sourceable today: Cummings 2016 on the semantics and on the
   optional-warning permission in 1800-2012.
2. **IEEE 1364.1-2002.** Same problem, and the IEEE record page 404s. Name the
   standard (citing Cummings 2016); do not describe its contents.
3. **Safety-critical illegal-state guidance.** ISO 26262 and RTCA DO-254 are
   paywalled and were not read. The chapter has good *industry* sourcing
   (OpenTitan sparse encoding and Hamming distance; Cummings 1998 on
   satellite/medical) but no normative sourcing. Do not write "ISO 26262
   requires…".
4. **Verible's style-guide lineage.** Asserted everywhere, stated nowhere in the
   repository. Phrase as correspondence, not implementation.
5. **Currency of "simulators don't warn."** Cummings' §8 finding is from 2016;
   it may now be false for some simulators. Date it explicitly if used.
6. **Web search was unavailable**, so discovery was by direct URL and archive
   index. A better peer-reviewed source for FSM state-space coverage than
   Tasiran & Keutzer 2001 may exist; only its DOI metadata was read, not the
   full text.


# Part B — Clocks, resets and crossings

Scope: clock domains, metastability and synchronizers, resets, and the limits of
static clock/reset analysis. Citation convention: `[Source, YYYY-MM-DD](URL)`,
where the date is the source's own publication date when it has one and the
access date (2026-09-07) otherwise. Sources are labelled **[standard]**,
**[primary]**, **[vendor]**, **[research]** or **[industry paper]**. Vendor
claims are kept separate from peer-reviewed or measured results.

**Fetch note.** `sunburst-design.com` now issues a 301 to
`paradigm-works.com`, whose technical library serves only metadata and requires
registration for the PDFs. All Cummings papers below were therefore read from
the Internet Archive's captures of the original `sunburst-design.com` files, and
the archive URL is the one cited. `verilab.com/files/sva_cdc_paper_dvcon2006.pdf`
returns 404 and was likewise read from the Internet Archive. Ginosar's ASYNC
2003 paper could not be retrieved in full text from any reachable host; it is
cited by DOI only and **nothing is quoted from it**.

### 1. Clocks and clock domains

A clock, for analysis purposes, is "a periodic binary signal, used to indicate
the sampling point of sequential operators. It is characterized by a period,
duty cycle and phase"
[Plassan, *Conclusive formal verification of clock domain crossing properties*, PhD thesis, Université Grenoble Alpes, 2018-06](https://theses.hal.science/tel-01870205/document)
**[research]**, §3.1.2. Between the primary clock inputs and the flip-flops sits
a network that the same source decomposes into exactly four operations
(§3.1.2, verbatim):

> "Selection: choosing to propagate one clock or another; Blending: combining
> two clocks to generate a new one; Gating: propagating or stopping a clock;
> Shaping: modifying the period, duty cycle or phase of a clock."

and it names the two kinds of node the verifier must tell apart: "A clock is
called a primary clock when it is a primary input of the design or an output of
internal analog modules (e.g. a PLL or a crystal, which is then seen as a
blackbox) ... the signals after selection, blending, gating or shaping, are
called derived clocks" (§3.1.2). The same section warns that "'clock tree' is
misleading, as its formal representation is a directed graph" (footnote 1).

**Gating and glitch hazards.** A clock gate is built sequentially for a reason:
"Note that the gating stage of this example is sequential as it includes a
latch. This is a common clock-gate structure which avoids propagating a glitch
on the clock rising edge (indeed, here the clock can only be disabled when it is
low). Using two clock-gates with inverted control signals, a sequential mux
could easily be implemented (with the same intent of glitch avoidance)"
[Plassan 2018](https://theses.hal.science/tel-01870205/document) §3.1.2. The
enable itself is a crossing: "Clock-gating signals are synchronized to eliminate
clock glitches when the clocks are gated or when a domain switches from one
clock to another"
[Ginosar, *Metastability and Synchronizers: A Tutorial*, IEEE Design & Test of Computers, 2011-09](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf)
(DOI [10.1109/MDT.2011.113](https://doi.org/10.1109/MDT.2011.113))
**[primary]**, p. 30.

The distinction the chapter wants — a gated clock does not create a new domain,
a muxed clock may — follows from those definitions rather than from a sentence
in either source: gating only propagates or stops one source clock, so the
derived clock keeps that source's period and phase, whereas selection can hand
the same derived node the timing of either input. See §5, row 1: the reasoning
is sound but the exact claim is not quoted anywhere and should be stated as the
book's own inference.

**Scale.** On the OpenSPARC case study, the clock/reset control module drives
"the whole system among its 38 primary clocks and 17 primary resets ... The
clock propagation leads to a global clock path of 450 sequential elements (most
of them covered by 2 mission clocks). 134 configuration signals are identified"
[Plassan 2018](https://theses.hal.science/tel-01870205/document) §3.5.3. Crucially
for the verifier's reading: "Because this control module was reused from previous
projects, and because an exhaustive specification was not available, the clock
configurations and clock tree components were not perfectly understood by the
verification engineers" (ibid.).

**Domain relationships the specification must state.** Ginosar's tutorial names
them: two *mesochronous* domains "tick to the same frequency, but their relative
phase is unknown in advance"; drift makes them *multisynchronous* — "domains
operating at the same frequency but at slowly changing relative phases";
*periodic* clocks "are unrelated to each other — they are neither mesochronous
nor are their frequencies an integral multiple of each other"; and for *rational*
clocks "the two frequencies are related by a ratio known at design time (e.g.
1:3 or 5:6)"
[Ginosar 2011](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf),
pp. 31–33. These are the categories a verifier should demand from the spec,
because the correct synchronizer differs for each.

**Partitioning.** The practitioner guideline is one clock per module: "Guideline:
Only allow one clock per module ... Reason: Static timing analysis and creating
synthesis scripts is more easily accomplished on single-clock modules ...
Exception: The top-level module that connects together the signals from all of
the different clock domains will naturally have all of the clocks as inputs"
[Cummings, *Clock Domain Crossing (CDC) Design & Verification Techniques Using SystemVerilog*, SNUG Boston 2008 (archived capture 2020-11-12)](http://web.archive.org/web/20201112023511id_/http://www.sunburst-design.com/papers/CummingsSNUG2008Boston_CDC.pdf)
**[industry paper]**, §6.3.

### 2. Metastability and synchronizers

#### 2.1 The physics and the MTBF formula

All of §2.1 is from
[Ginosar 2011](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf)
**[primary]**, pp. 24–28, unless noted.

Metastability is indecision, not oscillation: "In flip-flops, metastability
means indecision as to whether the output should be 0 or 1" (p. 24), and "one
popular definition says that if the output of a flip-flop changes later than the
nominal clock-to-Q propagation delay [it was metastable]" (p. 24). The tutorial
is explicit that the folk picture is wrong: the claim that the two nodes "get
stuck in the middle and would eventually get out of there by some random
process ... should be taken lightly" (p. 27); probabilistically, "if a latch is
metastable at time zero, the probability it will remain metastable at time
t > 0 is e^(−t/τ), which diminishes exponentially fast" (p. 27).

*Entering.* "We can define a short window T_W around the clock's sampling edge
(sort of 'setup-and-hold time') such that if data changes during that window,
the latch could become metastable" (p. 25). If the data changes at rate F_D,
"the rate of entering metastability becomes Rate = F_D·F_C·T_W. For instance, if
F_C = 1 GHz, F_D = 100 MHz, and T_W = 20 ps, then Rate = 2,000,000 times/sec"
(p. 25).

*Failing.* "Failure means that a flip-flop became metastable after the clock's
sampling edge, and that it is still metastable S time later. The two events are
independent, so we can multiply their probabilities" (p. 28):

```
p(failure)      = p(enter MS) x p(time to exit > S) = T_W * F_C * e^(-S/tau)
Rate(failures)  = T_W * F_C * F_D * e^(-S/tau)

                    e^(S/tau)
MTBF          =  ---------------
                 T_W * F_C * F_D
```

Variables, as the source names them: **T_W** is the window around the sampling
edge inside which a data change can drive the latch metastable; **F_C** is the
clock (sampling) frequency; **F_D** is the rate at which the data input changes;
**S** is the synchronization (resolution) period allowed before the value is
sampled again; **τ** is the resolution time constant of the latch, estimated as
τ = C/g_m, where C is the capacitive load on the master-latch nodes and g_m the
inverter transconductance — "higher capacitive load on the master nodes and
lower inverter gain impede the resolution of metastability" (p. 27).

*Worked numbers, both directions.* For 28 nm high-performance CMOS with
τ = 10 ps, T_W = 20 ps, F_C = 1 GHz, data changing every ten clock cycles and
S = T_C, the tutorial obtains "4 × 10^29 years. (This figure should be quite safe
— the universe is believed to be only 10^10 years old.)" (p. 28). But at low
voltage and high temperature, with S = T_C, F_C = 1 GHz, F_D = 1 kHz,
τ = 100 ps and T_W = 200 ps, "the MTBF is about one minute. Three flip-flops ...
would increase the MTBF a bit, to about one month. But if we use four flip-flops,
S = 3·T_C and the MTBF jumps to 1,000 years" (p. 30). This pair of results is the
single most useful teaching fact in the note: the same two-flop structure is
either astronomically safe or fails in a minute depending on τ, T_W and S.

*Budgeting S.* "Actually, any logic and wire delays along the path from FF1 to
FF2 are subtracted from the resolution time: S = T_C − t_pCQ(FF1) − t_SETUP(FF2)
− t_PD(wire), and so on" (p. 28) — hence "the two flip-flops should be placed
near each other, or else the wire delay between them would detract from the
resolution time S. Missing this seemingly minor detail has made quite a few
synchronizers fail unexpectedly" (p. 29).

*System budget.* "MTBF decreases roughly linearly with the number of
synchronizers. Thus, if your system uses 1,000 synchronizers, you should be sure
to design each one for MBTF [sic] at least three orders of magnitude higher than
your reliability target for the entire system" (p. 30).

#### 2.2 The two-flop synchronizer and its rules

The structure: "The first flip-flop samples the asynchronous input signal into
the new clock domain and waits for a full clock cycle to permit any metastability
on the stage-1 output signal to decay, then the stage-1 signal is sampled by the
same clock into a second stage flip-flop"
[Cummings SNUG 2008](http://web.archive.org/web/20201112023511id_/http://www.sunburst-design.com/papers/CummingsSNUG2008Boston_CDC.pdf)
§3.2. What it buys: "The bottom line is that Q2 is never metastable (except,
maybe, once every MTBF years) ... The synchronization circuit exchanges the
'analog' uncertainty of metastability ... for a simpler 'digital' uncertainty ...
of whether the output switches one or two cycles later"
[Ginosar 2011](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf)
p. 29. Where two stages are not enough, "a third flop is added to increase the
MTBF"
[Cummings SNUG 2008](http://web.archive.org/web/20201112023511id_/http://www.sunburst-design.com/papers/CummingsSNUG2008Boston_CDC.pdf)
§3.4.

The three rules the chapter states, each with its source:

1. **Register in the source domain — no combinational logic driving the
   crossing.** "the combinational output from the sending clock domain could
   experience combinational settling at the CDC boundary. This combinational
   settling effectively increases the data-change frequency potentially creating
   small bursts of oscillating data and thereby increasing the number of edges
   that could be sampled while changing"
   [Cummings SNUG 2008](http://web.archive.org/web/20201112023511id_/http://www.sunburst-design.com/papers/CummingsSNUG2008Boston_CDC.pdf)
   §3.5. The paper's own summary rule is "register the signal in the sending
   clock domain to remove combinational settling" (§8.1). Note the mechanism is
   the F_D term of the MTBF formula, not a separate effect.

2. **No fan-out from the first stage — one synchronizer per signal.** "Another
   forbidden practice is to synchronize the same asynchronous input by two
   different parallel synchronizers; one might resolve to 1 while the other
   resolves to 0, leading to an inconsistent state. In fact, that was the problem
   that grounded the J spacecraft"
   [Ginosar 2011](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf)
   p. 30. See §5, row 2: this sources the *divergence* rule; the narrower
   statement "the first stage must not fan out to anything but the second stage"
   is a stricter, standard formulation not quoted verbatim in these sources
   (Litterick, below, gives the equivalent design rule: instantiate synchronizer
   modules so that "metastable nets are not abused").

3. **Single bit only.** See §2.3.

Litterick adds the assumption a verifier should check when nothing is known
about the two clocks: "If no assumptions are made about the relationship between
the source and destination clock domains ... input data values must be stable
for three destination clock edges"
[Litterick, *Pragmatic Simulation-Based Verification of Clock Domain Crossing Signals and Jitter using SystemVerilog Assertions*, Verilab & DVCon 2006 (archived capture 2018)](http://web.archive.org/web/2018id_/http://www.verilab.com/files/sva_cdc_paper_dvcon2006.pdf)
**[industry paper]**, §4.2 — the "three edge" idea also appears as Cummings'
§4.1.1 "three edge requirement".

#### 2.3 Multi-bit crossings and the correct structures

**Why per-bit synchronizers are wrong.** The primary statement:

> "Note that the synchronizer doesn't synchronize the data — rather, it
> synchronizes the control signals. Attempts to synchronize the data bit by bit
> usually lead to catastrophic results; even if all data lines toggle
> simultaneously, some bits might pass through after one cycle, while others
> might take two cycles because of metastability. Beware: that's a complete loss
> of data."
> — [Ginosar 2011](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf) p. 30

The same failure stated structurally: "if some bits of a bus have separate
multi-flop synchronizers, it cannot be guaranteed that all these synchronizers
require a strictly identical latency to output a stable value"
[Plassan 2018](https://theses.hal.science/tel-01870205/document) §1.2.3
("Bus Incoherency"). And in control terms: "If both the load and enable signals
are driven on the same sending clock edge, there is a chance that a small skew
between the control signals could cause the two signals to be synchronized into
different clock cycles within the receiving clock domain. Under these
conditions, the data would not be loaded into the register"
[Cummings SNUG 2008](http://web.archive.org/web/20201112023511id_/http://www.sunburst-design.com/papers/CummingsSNUG2008Boston_CDC.pdf)
§5.3. Cummings is blunt about the tempting fix: "Simply using synchronizers on
all of the CDC bits is not always good enough" (§5.2).

A related structural hazard, worth a callout because it survives correct
per-signal synchronization: **convergence**. "Whenever two signals converge on a
combinational gate, a transient inconsistent value (glitch) may appear. While on
a synchronous path, static timing analysis ensures that this glitch is resolved
within a clock period, in the context of a CDC, the glitch may be captured and
its value propagated ... To guarantee that a glitch cannot appear on this gate,
the two input signals should never toggle in the same cycle"
[Plassan 2018](https://theses.hal.science/tel-01870205/document) §1.2.2.

**The correct structures.** Cummings' taxonomy (§5.1) is three strategies, and
his summary (§8.2) is four bullets, verbatim:

> "Consolidate — first attempt to combine multiple signals into a 1-bit
> representation in the sending clock domain before synchronizing the signal
> into the receiving domain. Use Multi-Cycle Path (MCP) formulations to pass
> multiple signals across clock domains. Use FIFOs to pass multi-bit buses,
> either data or control buses. Use gray code counters."

- *Gray codes.* "Gray codes only allow one bit to change for each clock
  transition, eliminating the problem associated with trying to synchronize
  multiple changing CDC bits across a clock domain"
  [Cummings SNUG 2008](http://web.archive.org/web/20201112023511id_/http://www.sunburst-design.com/papers/CummingsSNUG2008Boston_CDC.pdf)
  §5.7.2; the code is Frank Gray's, US Patent 2,632,058 (1953), per the same
  paper's reference [4]. Gray coding is what the CDC checker can then assert:
  "Coherency: stable(DATA_CDC) or onehot(DATA_CDC xor prev(DATA_CDC))"
  [Plassan 2018](https://theses.hal.science/tel-01870205/document) §1.3.2.

- *MCP / data-with-valid ("MUX recirculation").* "An MCP formulation refers to
  sending unsynchronized data to a receiving clock domain paired with a
  synchronized control signal. The data and control signals are sent
  simultaneously allowing the data to setup on the inputs of the destination
  register while the control signal is synchronized for two receiving clock
  cycles before it arrives at the load input of the destination register" —
  and therefore "Because the unsynchronized data is passed and held stable for
  multiple clock cycles before being sampled, there is no danger that the sampled
  value will go metastable"
  [Cummings SNUG 2008](http://web.archive.org/web/20201112023511id_/http://www.sunburst-design.com/papers/CummingsSNUG2008Boston_CDC.pdf)
  §5.6. The checkable property is stability: "EN -> stable(DATA_CDC)"
  [Plassan 2018](https://theses.hal.science/tel-01870205/document) §1.3.2.

- *Handshake (req/ack).* "The sender sends req ..., req is synchronized by the
  top synchronization circuits, the receiver sends ack ..., ack is synchronized
  by the sender, and only then is the sender allowed to change req again. This
  round-trip handshake is the key to correct synchronization"
  [Ginosar 2011](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf)
  p. 30. Cost: "It may take two cycles of the receiver clock to receive req, two
  more cycles of the sender clock to receive ack, and possibly one more on each
  side ... If req and ack must be lowered before new data can be transferred,
  consider another penalty of 3 + 3 cycles" (ibid.).

- *Asynchronous FIFO.* "The most common fast synchronizer uses a two-clock FIFO
  buffer ... the write pointer has to be synchronized with rclk (read clock) when
  compared ... That's where the synchronization is; it's applied to the pointers,
  rather than to the data ... Incidentally, the pointers are usually maintained
  in Gray code so that only a single bit at a time changes in the synchronizer"
  [Ginosar 2011](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf)
  p. 31. The practitioner reference design is
  [Cummings, *Simulation and Synthesis Techniques for Asynchronous FIFO Design*, SNUG San Jose 2002 (archived capture 2020)](http://web.archive.org/web/2020id_/http://www.sunburst-design.com/papers/CummingsSNUG2002SJ_FIFO1.pdf)
  **[industry paper]**, which is also Ginosar's cited practical reference
  (his ref. 19). Cummings' own warning about FIFOs is the sharpest sentence in
  the paper: "Most incorrectly implemented FIFO designs still function properly
  90% of the time. Most almost-correct FIFO designs function properly 99%+ of the
  time" (§1.0).

- *1-deep / 2-register FIFO.* A cheap multi-bit crossing where "the gray code
  counters used to detect full and empty are simple toggle flip-flops"
  [Cummings SNUG 2008](http://web.archive.org/web/20201112023511id_/http://www.sunburst-design.com/papers/CummingsSNUG2008Boston_CDC.pdf)
  §5.8.2.

Ginosar's caution for FIFO users is worth a Pitfall callout: "The key question
for the user of a library FIFO buffer is how large the RAM should be ... an FPGA
has occasionally failed in mission because of a too-short FIFO buffer"
[Ginosar 2011](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf)
p. 31.

#### 2.4 Why simulation does not reproduce this class of bug

This is the chapter's motivating argument, so five independent sources are given.

1. **The direct statement.** "The issues are related to analogue effects in the
   real-world transistor-level circuits and do not typically manifest themselves
   in standard RTL simulation flows"
   [Litterick, DVCon 2006](http://web.archive.org/web/2018id_/http://www.verilab.com/files/sva_cdc_paper_dvcon2006.pdf)
   §1 **[industry paper]**.

2. **What the simulator does instead — with the mechanism.** Litterick's Figure 3
   walks three cases where zero-delay RTL simulation and silicon disagree, in
   *both* directions: "if the signal changes just before the clock edge (a
   setup-time violation) then the simulation will propagate the new value, but
   the real circuit might become metastable and decay to original low value";
   and for a two-cycle pulse, "the simulation will propagate a 2-clock wide pulse
   but the real circuit may filter it out completely" (§4.2). So RTL simulation
   is not merely optimistic; it is a *different* circuit.

3. **CDC jitter is invisible.** "Even when all signals are properly synchronized
   into the destination clock domain, the actual arrival time in real life is
   subject to uncertainty if the signal goes metastable in the first stage
   synchronizing flip-flop ... Normally this jitter would not show up on a
   simulation but must be considered to conclude the analysis" (§6, ibid.).

4. **The FIFO case, from the designer's side.** "Testing a FIFO design for subtle
   design problems is nearly impossible to do. The problem is rooted in the fact
   that FIFO pointers in an RTL simulation behave ideally, even though, if
   incorrectly implemented, they can cause catastrophic failures if used in a
   real design. In an RTL simulation, if binary-count FIFO pointers are included
   in the design all of the FIFO pointer bits will change simultaneously; there
   is no chance to observe synchronization and comparison problems"
   [Cummings, SNUG San Jose 2002](http://web.archive.org/web/2020id_/http://www.sunburst-design.com/papers/CummingsSNUG2002SJ_FIFO1.pdf)
   §2.4. He adds that gate-level simulation only helps a little, and less as
   speeds rise: "the probability of detecting problems also diminishes" (ibid.).

5. **Peer-reviewed restatements.** "CDC issues are by nature very rare since they
   depend on physical timing constraints ... A simulation environment, even with
   good coverage, is then very likely to miss a glitch or metastability.
   Consequently, in the functional verification of CDC, using model checking
   prevails"
   [Plassan 2018](https://theses.hal.science/tel-01870205/document) §1.3.2. And,
   for CDC and RDC together: "We need to take precautions at the RTL level even
   though our simulator is unable to verify or observe these problems"
   [Sundriyal & Gupta, *Clock & Reset Domain Crossing Issues and Verification Techniques for SoC Design*, ASIANCON, 2024-08-23](https://doi.org/10.1109/ASIANCON62057.2024.10837784)
   **[research]** (abstract).

**What gate-level simulation shows, and why teams suppress it.** "Digital
simulation models typically generate X's when synchronizers recognize setup and
hold time violations on CDC signals. This can frequently cause gate-level
simulations to fail"; ASIC libraries "typically model flip-flops to drive X's
(unknowns) on the flip-flop outputs when a timing violation occurs ... These
X-values propagate to the rest of the design"
[Cummings SNUG 2008](http://web.archive.org/web/20201112023511id_/http://www.sunburst-design.com/papers/CummingsSNUG2008Boston_CDC.pdf)
§7.0–7.1. Section 7.2 then lists the standard countermeasures — turn off timing
checks, zero the setup/hold times, edit the flip-flop models, use multiple SDF
files — i.e. the industry's usual response is to *remove* the one signal a
simulator does give. This is a strong Pitfall for the chapter.

**What simulation can be made to do.** The accepted substitute is to replace the
synchronizer with a randomized-latency model: "we can facilitate logic
verification by replacing the synchronizer with a special synchronous delay block
that inserts a delay of either k or k + 1 cycles at random. Although this
approach leads to a design space of at least 2^n cases if there are n
synchronization circuits, it is still widely used and is effective in detecting
many logic errors (but not all of them — it wouldn't have helped the J spacecraft
designers, for instance)"
[Ginosar 2011](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf)
p. 33. Litterick's concrete RTL implementation of the same idea uses `randcase`
to pick between `$past(d_in)` and `d_in`, and between `m2` and `m3`, so that
"the jitter emulation can cause the d_out transition to randomly appear one clock
early ..., at the nominal position, or one clock late ... This circuit is also
capable of filtering one and two-clock wide pulses"
[Litterick, DVCon 2006](http://web.archive.org/web/2018id_/http://www.verilab.com/files/sva_cdc_paper_dvcon2006.pdf)
§6. Note the honest limit both authors state: this covers *logic* consequences of
jitter, not the metastability event itself.

### 3. Resets

The reference for §3.1–§3.3 is
[Cummings & Mills, *Asynchronous & Synchronous Reset Design Techniques — Part Deux*, SNUG Boston 2003, rev 1.3 (archived capture 2020)](http://web.archive.org/web/2020id_/http://www.sunburst-design.com/papers/CummingsSNUG2003Boston_Resets.pdf)
**[industry paper]** unless noted.

#### 3.1 Synchronous vs asynchronous

*Synchronous reset, what it costs and assumes.* "Synchronous reset logic will
synthesize to smaller flip-flops, particularly if the reset is gated with the
logic generating the d-input. But in such a case, the combinational logic gate
count grows, so the overall gate count savings may not be that significant"
(§4.2). The honest verdict on area in modern nodes, from the same paragraph: "in
today's technology of huge die sizes, the savings of a gate or two per flip-flop
is generally irrelevant". The real advantages are behavioral: "Synchronous resets
insure that reset can only occur at an active clock edge. The clock works as a
filter for small reset glitches" (§4.2), and where reset is generated internally,
"A synchronous reset is recommended for these types of designs because it will
filter the logic equation glitches between clocks" (§4.2).

Its environmental assumptions are the disadvantages: "Synchronous resets may need
a pulse stretcher to guarantee a reset pulse width wide enough to ensure reset is
present during an active edge of the clock" (§4.3); "By its very nature, a
synchronous reset will require a clock in order to reset the circuit ... if you
have a gated clock to save power, the clock may be disabled coincident with the
assertion of reset. Only an asynchronous reset will work in this situation"
(§4.3); and for internal tristate buses, "In order to prevent bus contention on
an internal tristate bus when a chip is powered up, the chip should have a
power-on asynchronous reset" (§4.3).

*Asynchronous reset.* "The biggest advantage to using asynchronous resets is
that, as long as the vendor library has asynchronously reset-able flip-flops, the
data path is guaranteed to be clean. Designs that are pushing the limit for data
path timing, can not afford to have added gates and additional net delays in the
data path" (§5.3); and "the circuit can be reset with or without a clock present"
(§5.3). The cost: "The biggest problem with asynchronous resets is that they are
asynchronous, both at the assertion and at the de-assertion of the reset. The
assertion is a non issue, the de-assertion is the issue. If the asynchronous
reset is released at or near the active clock edge of a flip-flop, the output of
the flip-flop could go metastable and thus the reset state of the ASIC could be
lost" (§5.4). Also: DFT — "if the asynchronous reset is not directly driven from
an I/O pin, then the reset net from the reset driver must be disabled for DFT
scanning and testing" (§5.4) — and timing: "The reset tree must be timed for both
synchronous and asynchronous resets to ensure that the release of the reset can
occur within one clock period" (§5.4).

*Recovery and removal.* "Reset recovery time refers to the time between when
reset is de-asserted and the time that the clock signal goes high again. The
Verilog-2001 Standard has three built-in commands to model and test recovery time
and signal removal timing checks: `$recovery`, `$removal` and `$recrem` (the
latter is a combination of recovery and removal timing checks)" (§6.1); "Recovery
time is also referred to as a t_su setup time of the form, 'PRE or CLR inactive
setup time before CLK↑'" (§6.1, crediting the TI *ALS/AS Logic Data Book*, 1986,
p. 2-78). The second, distinct hazard is skew: "When reset removal is
asynchronous to the rising clock edge, slight differences in propagation delays
in either or both the reset signal and the clock signal can cause some registers
or flip-flops to exit the reset state before others" (§6.2). *(The `$recovery` /
`$removal` / `$recrem` system timing checks are normative in IEEE Std 1364 and
carried into IEEE Std 1800 **[standard]**; the LRM itself is paywalled and was
not fetched — see §7.)*

#### 3.2 Reset synchronizers and release ordering

The rule, in the paper's own capitals: "Guideline: EVERY ASIC USING AN
ASYNCHRONOUS RESET SHOULD INCLUDE A RESET SYNCHRONIZER CIRCUIT!! Without a reset
synchronizer, the usefulness of the asynchronous reset in the final system is
void even if the reset works during simulation" (§7.0).

Mechanism — asynchronous assert, synchronous de-assert: "An external reset signal
asynchronously resets a pair of master reset flip-flops, which in turn drive the
master reset signal asynchronously through the reset buffer tree ... Reset removal
is accomplished by de-asserting the reset signal, which then permits the d-input
of the first master reset flip-flop (which is tied high) to be clocked through a
reset synchronizer. It typically takes two rising clock edges after reset removal
to synchronize removal of the master reset" (§7.0). These flops must be kept off
the scan chain (§7.0).

A point worth a Pitfall, because it is a common misconception: the second stage
is *not* at risk. "The second flip-flop of the reset synchronizer is not subject
to recovery time metastability because the input and output of the flip-flop are
both low when reset is removed. There is no logic differential between the input
and output of the flip-flop so there is no chance that the output would oscillate"
(§7.1). And the assertion edge is never the problem: "There is no reset
metastability issue when reset is asserted because the reset signal bypasses the
clock signal in a flip-flop circuit to cleanly force the output low. The
metastability issue is always related to reset removal" (§7.3).

*Reset domains and ordering.* "For a multi-clock design, a separate asynchronous
reset synchronizer circuit and reset distribution tree should be used for each
clock domain. This is done to insure that reset signals can indeed be guaranteed
to meet the reset recovery time for each register in each clock domain ... The
problem is graceful removal of reset and synchronized startup of all logic after
reset is removed" (§11.0). Two legitimate schemes follow. Non-coordinated:
"exactly when reset is removed within one clock domain compared to when it is
removed in another clock domain is not important. Typically in these designs, any
control signals crossing clock boundaries are passed through some type of
request-acknowledge handshaking sequence" (§11.1). Sequenced: "For some
multi-clock designs, reset removal must be ordered ... only the highest priority
asynchronous reset synchronizer input is tied high. The other asynchronous reset
synchronizer inputs are tied to the master resets from higher priority clock
domains" (§11.2). Which of the two applies is a **specification** question, and
therefore a question the verifier must ask.

The reset trailing edge is a clock-domain crossing like any other: "The trailing
edge of the reset signal and of any asynchronous inputs to flip-flops are
typically synchronized to each clock domain in a chip"
[Ginosar 2011](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf)
p. 30.

An open-source house convention that matches all of this, useful as a real-world
example: "Chip wide all resets are defined as active low and asynchronous. Thus
they are defined as tied to the asynchronous reset input of the associated
standard cell registers. The default name is `rst_n`. If they must be
distinguished by their clock, the clock name should be included in the reset name
like `rst_domain_n`"
[lowRISC Verilog Coding Style Guide, accessed 2026-09-07](https://raw.githubusercontent.com/lowRISC/style-guides/master/VerilogCodingStyle.md)
**[primary]** ("Resets"). The same guide requires clock names to carry the domain:
"If a module contains multiple clocks, the clocks that are not the system clock
should be named with a unique identifier, preceded by the `clk_` prefix ... Note
that this prefix will be used to identify other signals in that clock domain"
(ibid., "Clocks") — the same naming-as-metadata idea as Cummings §6.1.

#### 3.3 Registers without a reset

The legitimate case named in the literature is the follower flip-flop: "a designer
should not mix resetable flip-flops with follower flip-flops (flops with no
resets) in the same procedural block or process. Follower flip-flops are
flip-flops that are simple data shift registers" (§3.1). Mixing them has a
concrete cost: in the bad-style example "the second stage is a follower flip-flop
and is not reset, but because the two flip-flops were inferred in the same
procedural block/process, the reset signal `rst_n` will be used as a data enable
for the second flop. This coding style will generate extraneous logic" (§3.1).

That reset-less sequential elements are numerous enough to be treated as a class
is confirmed, as a vendor statement, by the "Low-Noise Methodology" bullet "Skip
the reset-less sequential elements"
[Synopsys, VC SpyGlass RDC product page, accessed 2026-09-07](https://www.synopsys.com/verification/static-and-formal-verification/vc-spyglass/vc-spyglass-rdc.html)
**[vendor]**. The broader engineering rationale the chapter will want — datapath
pipeline stages and storage arrays need no reset because their contents are
qualified by a valid bit or by a reset control path — is **not** directly quoted
in any source fetched here; see §5, row 4.

#### 3.4 Reset-domain crossing

The definition, and the reason it is a distinct class:

> "A well known source of metastability is caused by clock domain crossings;
> however, asynchronous reset crossings within the same clock domain can also
> cause metastability."
> — [Synopsys VC SpyGlass RDC, accessed 2026-09-07](https://www.synopsys.com/verification/static-and-formal-verification/vc-spyglass/vc-spyglass-rdc.html) **[vendor]**

That sentence is the crux: an RDC path can lie entirely **inside one clock
domain** — a flop reset by `rst_a_n` feeding a flop reset by `rst_b_n`, both on
`clk`. A structural analysis that enumerates crossings by comparing the *clocks*
of source and destination registers sees no crossing at all. The peer-reviewed
framing of the problem:

> "Reset architecture of a digital design can be quite complex. Typically, SoC
> designs have multiple sources of reset, such as power-on reset, hardware
> resets, debug resets, software resets, and watchdog timer reset. These multiple
> reset domains make the design potentially exposed to metastability issues, so
> the designer must perform the reset domain crossing (RDC) analysis and resolve
> any RDC issues in the early stages of designing. This can quite be challenging,
> because of the effort needed for this analysis and how noisy it can be."
> — [Fawzy, Elgohary & Ibrahim, *Noise Reduction in Reset Domain Crossings Verification Using Formal Verification*, IEEE EWDTS, 2020-09](https://doi.org/10.1109/EWDTS50664.2020.9224763) **[research]** (abstract)

Also peer-reviewed, and confirming that RDC is treated as its own RTL-quality
check alongside CDC: "The goal of this paper is to check for RTL Quality checks
such as CDC and RDC to ensure such faults do not occur at later stages of chip
development"
[Sundriyal & Gupta, ASIANCON, 2024-08-23](https://doi.org/10.1109/ASIANCON62057.2024.10837784)
**[research]**. A further peer-reviewed venue treatment, not fetched in full:
Yeung & Mandel, *Multi-Domain Verification of Power, Clock and Reset Domains*,
LNCS 9434 (HVC 2015), DOI
[10.1007/978-3-319-26287-1_15](https://doi.org/10.1007/978-3-319-26287-1_15)
**[research]** — see §7.

#### 3.5 Reset tests that blocks usually lack

"Reset testing is a crucial element of functional sign-off for any chip", but
"There has been no standard method for making scoreboards, drivers and monitors
enter and exit reset states cleanly, or kill complex stimulus generation processes
gracefully; it is common to see reset testing that does not achieve self-checking
autonomy forcing engineers to rely on inefficient techniques such as visual
inspection"
[Hunter, Chen & Lipon, *Reset Testing Made Simple with UVM Phases*, SNUG 2013 (archived capture 2020)](http://web.archive.org/web/2020id_/http://www.sunburst-design.com/papers/HunterSNUGSV_UVM_Resets_paper.pdf)
**[industry paper]**, abstract. That paper is also the source for the four test
classes the chapter should name:

- **Idle reset.** "The simplest form of reset testing is idle testing. When all
  stimulus has drained out of the device, all scoreboards are quiet, and
  everything has quiesced, send the device back into reset and do it all over
  again ... the manner in which the DUT reacts should be highly predictable."
- **Active reset** (mid-traffic). "Applying a reset signal while stimulus traffic
  is flying throughout the DUT is also fairly straightforward ... The complexity
  lies in how each UVM component reacts to reset."
- **Soft reset** (partial). "typically it involves register writes that are meant
  to clear the device under test in some way ... Perhaps packets that are in
  flight continue to their completion; or interrupts continue to be serviced; or
  state machines are forced to idle but buffers are not emptied. There are so many
  ways that a soft reset might differentiate itself from a hard reset that it is
  impossible to provide a foolproof design pattern for all occasions."
- **Multi-domain reset.** "Just as the RTL can have multiple reset domains, so too
  can testbench components. By establishing different domains and assigning them
  to different components, you can jump one domain's phases without changing
  others."

Reset with the clock stopped is sourced indirectly, from the design side: a
gated clock "may be disabled coincident with the assertion of reset. Only an
asynchronous reset will work in this situation, as the reset might be removed
prior to the resumption of the clock"
[Cummings & Mills, SNUG Boston 2003](http://web.archive.org/web/2020id_/http://www.sunburst-design.com/papers/CummingsSNUG2003Boston_Resets.pdf)
§4.3 — i.e. the clock-stopped case is a real design scenario, so it is a real test
scenario; but no source fetched here states "test reset with the clock stopped" as
a testbench guideline (see §5, row 5).

Two testbench guidelines the chapter can quote directly. First: "In a simulation,
if reset is removed on a posedge clock, there is usually no guarantee what the
simulation result will be. Even if the RTL code behaves as expected, the
gate-level simulation may behave differently due to event scheduling race
conditions and different IEEE-Verilog compliant simulators may even yield
different RTL simulation results ... Guideline: In general, change the testbench
reset signal on the inactive clock edge using blocking assignments" (§7.4).
Second, on time-zero initialization: "making the first testbench assignment to
reset using a nonblocking assignment ... forces all procedural blocks to become
active before the reset signal is asserted, which means all reset-sensitive
procedural blocks are guaranteed to trigger at time 0 (no Verilog race issues)"
(§7.4). Note the tension the chapter should flag: this guideline deliberately
keeps the testbench *away* from the recovery-time corner, which is exactly the
corner that fails in silicon — one more reason the bug is not a simulation bug.

### 4. What a static tool can and cannot decide

**What is structurally easy.** "From a netlist design, it is fairly easy to
structurally detect two registers receiving different clocks, and even to detect
a multi-flop"
[Plassan 2018](https://theses.hal.science/tel-01870205/document) §1.3.1
**[research]**. That is the whole of what an RTL-only derivation can honestly
claim.

**Where structural recognition breaks down.** "In contrast, for complex FIFO
protocols, identifying the correct control logic is non-trivial. If a single
synchronizer structure was used, it could be stored in a pattern library and
identified by a proper pattern matching. Unfortunately, in industry, many
designers create their own synchronizing structures, and the structural library
used for pattern matching would never be exhaustive on complex structures such as
FIFOs" (ibid.). And the decisive limit: "a structural approach cannot check
protocols and assumptions on the control signal. A functional check must then be
run" (ibid.). Industrial tools bridge this by generating formal properties from
recognized patterns — coherency (Gray one-hot) and stability (enable implies
stable data), quoted in §2.3 above — "In practice, most industrial CDC tools
reuse structural information to run functional checks" (§1.3.2).

**Constraints are not derivable from RTL.** This is the point the chapter's own
tool must concede. "reusing predefined modules, designers do not know the exact
clock configuration components. Thus, they typically miss some assumptions on
configuration signals. As a consequence, the design is verified in a pessimistic
mixed-mode, where controls toggle incoherently and unrealistically. With this
incomplete setup, protocols may behave spuriously, leading to worthless
verification results. The verification of protocols then requires a realistic and
complete clock setup"
[Plassan 2018](https://theses.hal.science/tel-01870205/document) §3.1.1. He
quantifies the cost on one FIFO overflow property: with the clock-gate enables
constrained, "a model checker takes 13 seconds to guarantee that the FIFO cannot
overflow"; with the assumption removed, "The same overflow property now takes 192
seconds to be proven (15 times more)" — and "When we consider that modern designs
include thousands of clock-gating structures along with complex clock switching,
running formal checks with an incomplete setup sounds intractable" (ibid.). His
own contribution explicitly targets "verification of so-called generated clocks in
the Synopsys Design Constraints (SDC) format" (§3.5), i.e. the clock declarations
come from outside the RTL.

The corollary for the chapter's tool: **domains derived from RTL alone give you
the crossing list, not the sign-off.** They cannot tell you which mode the chip
is in, which mux select is constant in mission mode, which of two clocks are
declared asynchronous, or what the intended ratio is. Say so.

**Vendor claims (labelled, not adopted).** A commercial CDC product page claims
"Comprehensive CDC analysis using formal and simulation-based solutions",
"Support for UPF and SDC based CDC analysis", "Synchronizers and auto-detection
of quasi-static signals for lower false violations", "Protocol-Independent
Analysis", and "VC SpyGlass CDC correlates control and data signals resulting in
a good understanding of the design intent for the lowest possible noise"
[Synopsys, VC SpyGlass CDC product page, accessed 2026-09-07](https://www.synopsys.com/verification/static-and-formal-verification/vc-spyglass/vc-spyglass-cdc.html)
**[vendor]**. The corresponding RDC page claims coverage of "intricate reset
relationships, reset to clock relationships, RDC qualifiers", a "Low-Noise
Methodology" that skips "the reset-less sequential elements", and "SDC support for
RDC analysis" and "Constraints-Driven CDC and RDC Verification Including UPF Aware
Analysis"
[Synopsys, VC SpyGlass RDC product page, accessed 2026-09-07](https://www.synopsys.com/verification/static-and-formal-verification/vc-spyglass/vc-spyglass-rdc.html)
**[vendor]**. These are marketing statements, not measurements; the chapter must
present them as claims. Their evidentiary value here is narrow but real: two
independent product pages both foreground *noise* and *false violations* as the
thing they compete on, and both list SDC/UPF constraint input as a required
feature — corroborating Plassan on constraints and Fawzy et al. on noise.

**The noise problem, from a peer-reviewed source.** "the designer must perform
the reset domain crossing (RDC) analysis and resolve any RDC issues in the early
stages of designing. This can quite be challenging, because of the effort needed
for this analysis and how noisy it can be. In this paper, we present some of the
challenges in the existing methodology for RDC analysis and propose a new
methodology to reduce RDC results noisiness and achieve more accurate results.
This leads to faster verification closure"
[Fawzy, Elgohary & Ibrahim, EWDTS, 2020-09](https://doi.org/10.1109/EWDTS50664.2020.9224763)
**[research]** (abstract). On the CDC side, the equivalent statement is about
false violations from metastability-injection flows: "This approach, however
correct, combines a pessimistic random generation of X-value, and an
over-approximating ternary execution. Many false violations are then expected to
be reported by this methodology"
[Plassan 2018](https://theses.hal.science/tel-01870205/document) §1.3.2.

**I could not source a published waiver *count*.** No paper reachable in this
session gives a number for waivers per design or a percentage of CDC violations
waived. Do not assert one — see §5, row 6, and §7.

### 5. Commonly repeated but unsourced claims

| Claim | Where it is repeated | Status |
|---|---|---|
| "A gated clock is not a new clock domain, but a muxed clock may be." | Design lore; CDC training material | **Inference, not quoted.** Follows from Plassan's gating vs selection definitions (§1) but no source states it. Present as the book's reasoning, or drop the aphorism and give the definitions. |
| "No fan-out from the first synchronizer stage." | Universal coding rule; lint rules | **Partly sourced.** Ginosar (p. 30) forbids *two parallel synchronizers on the same input* (divergence). The narrower "stage-1 Q may feed only stage-2" is standard but not quoted in any source fetched here. |
| "Two flip-flops give an adequate MTBF." | Very widely | **Sourced but conditional.** Ginosar shows the same structure giving 4x10^29 years and ~1 minute depending on tau, T_W, S (§2.1). Never state it unconditionally. |
| "Datapath pipeline stages and RAM/register arrays legitimately have no reset." | Design guidelines | **Not sourced.** Only the follower-flip-flop case is quoted (Cummings §3.1) plus a vendor bullet acknowledging reset-less elements exist. Needs a further source before the chapter asserts the general rule. |
| "Blocks are rarely tested with reset asserted mid-traffic, with the clock stopped, or with partial reset." | Verification folklore | **Half-sourced.** Hunter et al. name idle/active/soft/multi-domain reset testing and say reset testing often lacks self-checking autonomy; nobody fetched here measures how many blocks skip these, and no source gives a clock-stopped reset test guideline. |
| "CDC sign-off produces thousands of violations, most of them waived." | Conference hallways, tool marketing | **Not sourced numerically.** Noise/false-violation *existence* is sourced (Fawzy et al.; Plassan; two vendor pages). No count was found. Do not put a number in the chapter. |
| "Reset removal must be synchronized to every clock domain separately." | Reset design lore | **Sourced.** Cummings & Mills §11.0, verbatim. |
| "RTL simulation cannot reproduce an unsynchronized CDC." | The chapter's motivating argument | **Sourced five ways** (§2.4). Phrase it as "does not model metastability, and diverges from silicon in both directions", not "always misses it" — Litterick's Figure 3 shows simulation can also propagate values silicon would filter. |

### 6. Suggested BibTeX keys

| Key | Citation | Used by |
|---|---|---|
| `ginosar2011metastability` | R. Ginosar, "Metastability and Synchronizers: A Tutorial," *IEEE Design & Test of Computers*, vol. 28, no. 5, Sept/Oct 2011, pp. 23–35. DOI 10.1109/MDT.2011.113. PDF: webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf (accessed 2026-09-07). | §1, §2.1–§2.4, §3.2 |
| `ginosar2003fourteen` | R. Ginosar, "Fourteen Ways to Fool Your Synchronizer," *Proc. 9th IEEE Int'l Symp. Asynchronous Circuits and Systems (ASYNC 03)*, IEEE CS Press, 2003, pp. 89–96. DOI 10.1109/ASYNC.2003.1199169. | §2.2 (cite only; full text not obtained — see §7) |
| `cummings2008cdc` | C. E. Cummings, "Clock Domain Crossing (CDC) Design & Verification Techniques Using SystemVerilog," SNUG Boston, 2008, rev 1.0. | §1, §2.1–§2.4 |
| `cummings2002fifo` | C. E. Cummings, "Simulation and Synthesis Techniques for Asynchronous FIFO Design," SNUG San Jose, 2002, rev 1.2. | §2.3, §2.4 |
| `cummings2003resets` | C. E. Cummings and D. Mills, "Asynchronous & Synchronous Reset Design Techniques — Part Deux," SNUG Boston, 2003, rev 1.3. | §3.1–§3.3, §3.5 |
| `litterick2006cdcsva` | M. Litterick, "Pragmatic Simulation-Based Verification of Clock Domain Crossing Signals and Jitter using SystemVerilog Assertions," DVCon, 2006. | §2.2, §2.4 |
| `hunter2013resettesting` | B. Hunter, B. Chen (Cavium) and R. Lipon (Synopsys), "Reset Testing Made Simple with UVM Phases," SNUG, 2013. | §3.5 |
| `plassan2018cdc` | G. Plassan, "Conclusive formal verification of clock domain crossing properties," PhD thesis, Université Grenoble Alpes, 2018. HAL tel-01870205. | §1, §2.3, §2.4, §4 |
| `fawzy2020rdcnoise` | M. Fawzy, A. Elgohary and H. Ibrahim, "Noise Reduction in Reset Domain Crossings Verification Using Formal Verification," *IEEE East-West Design & Test Symposium (EWDTS)*, 2020. DOI 10.1109/EWDTS50664.2020.9224763. | §3.4, §4 |
| `sundriyal2024cdcrdc` | A. Sundriyal and V. Gupta, "Clock & Reset Domain Crossing Issues and Verification Techniques for SoC Design," *4th Asian Conf. on Innovation in Technology (ASIANCON)*, 2024. DOI 10.1109/ASIANCON62057.2024.10837784. | §2.4, §3.4 |
| `yeung2015multidomain` | P. Yeung and E. Mandel, "Multi-Domain Verification of Power, Clock and Reset Domains," *LNCS* 9434 (HVC 2015), Springer. DOI 10.1007/978-3-319-26287-1_15. | §3.4 (metadata only — see §7) |
| `lowrisc-verilog-style` | lowRISC, *Verilog Coding Style Guide*, GitHub `lowRISC/style-guides`, accessed 2026-09-07. | §3.2 |
| `dally1998digital` | W. J. Dally and J. W. Poulton, *Digital Systems Engineering*, Cambridge University Press, 1998. | §2.1 (Cummings' MTBF and synchronizer definitions come from here; the book itself was not consulted — see §7) |
| `ieee1800` | IEEE Std 1800, *IEEE Standard for SystemVerilog*, IEEE. | §3.1 ($recovery/$removal/$recrem — not fetched) |
| `synopsys-vcspyglass-cdc` / `synopsys-vcspyglass-rdc` | Synopsys VC SpyGlass CDC and RDC product pages, accessed 2026-09-07. **Vendor.** | §4 |

### 7. Confidence notes and gaps

**High confidence.** The MTBF formula and every variable in it, the two worked
numeric cases, the multi-bit prohibition, the four correct multi-bit structures,
the reset-synchronizer mechanism, recovery/removal definitions, per-domain reset
synchronizers, and the four reset-test classes. All are verbatim from primary or
practitioner sources read in full.

**The motivating claim is safe, with one wording caution.** "An unsynchronized CDC
is a bug that ordinary RTL simulation cannot reliably reproduce" is supported by
Litterick (analogue effects "do not typically manifest themselves in standard RTL
simulation flows"), Cummings 2002 (RTL FIFO pointers "behave ideally"), Plassan
("very likely to miss a glitch or metastability"), Sundriyal & Gupta ("our
simulator is unable to verify or observe these problems"), and Ginosar (the
random k / k+1 delay substitute is "effective in detecting many logic errors (but
not all of them)"). Caution: do **not** write "simulation always passes a broken
crossing". Litterick's Figure 3 shows simulation diverging from silicon in both
directions — it can also propagate a pulse the real circuit filters away.

**Gaps the chapter must not paper over.**

1. **No waiver or false-positive *numbers*.** Noise is sourced qualitatively only.
   If the chapter wants "CDC sign-off is dominated by waivers", it needs a fresh
   source — likely a DVCon paper behind a proceedings site that was unreachable
   here. State the problem qualitatively or cite nothing.
2. **Ginosar's ASYNC 2003 "Fourteen Ways" was not obtained.** Every reachable copy
   404s and web.archive.org is not fetchable through the standard fetch path
   (it was reachable only via `curl` for other files). The DOI is verified via
   Crossref; nothing is quoted from it. If the chapter wants its taxonomy of
   synchronizer mistakes, someone must obtain the paper. The 2011 tutorial covers
   the same ground and is quoted here instead.
3. **RDC rests on a thinner evidence base than CDC.** The clean definitional
   sentence ("asynchronous reset crossings within the same clock domain can also
   cause metastability") is **vendor**. The peer-reviewed sources (Fawzy et al.;
   Sundriyal & Gupta) confirm RDC exists, matters and is noisy, but the abstracts
   are all that was obtained; neither full text was read. Yeung & Mandel (HVC
   2015) is the most promising academic treatment and was not obtained at all.
   The chapter's explanation of *why* CDC tools miss RDC (the path can lie inside
   a single clock domain, so a clock-comparison structural analysis finds no
   crossing) is the book's own reasoning built on the vendor sentence — flag it
   as such or get the Yeung & Mandel paper.
4. **Standards not fetched.** IEEE Std 1800 / 1364 for `$recovery`, `$removal`,
   `$recrem` are paywalled; the definitions here are Cummings' restatement of
   Verilog-2001. Dally & Poulton (1998) is the ultimate source of the
   synchronizer definition and MTBF analysis Cummings leans on, and was not
   consulted; Ginosar's formula is used instead and is self-contained.
5. **`sunburst-design.com` is effectively gone.** Cite the archive URLs. If the
   book prefers live links, the redirect target requires registration, which is
   worse for readers.


# Part C — Pipelines, interfaces, and structural extraction

Scope: flow-control contracts (valid/ready, back-pressure, FIFOs), the block
boundary as a specification, and what open tools can extract from RTL. Every
factual claim carries a URL. Fetch failures are recorded verbatim in §6.

Access date for undated pages: 2026-09-07.

---

### 1. Pipelines, handshakes and queues

#### 1.1 The valid/ready contract, as specified

The chapter's central claim is that a two-wire handshake is a *contract with
normative rules*, not a convention. The cleanest openly-readable statement of
those rules is the SiFive TileLink specification, §4.1 "Flow Control Rules"
[SiFive TileLink Specification, Version 1.7-draft, 2017-08-21](https://static.dev.sifive.com/docs/tilelink/tilelink-spec-1.7-draft.pdf)
**[standard]**. Quoting the specification directly:

> "To regulate the flow of beats in TileLink channels, receivers raise the
> channel ready signal to indicate their ability to accept a beat. The receiver
> lowers the ready signal to indicate that they are busy and are not accepting a
> beat. Conversely, the sender of a beat raises the channel valid signal to
> indicate the presence of a beat on the channel. Only when both ready and valid
> are raised is the beat exchanged."

And the rules themselves, verbatim from §4.1:

> "In order to implement correct ready-valid handshaking, these rules must be
> followed:
> - If ready is LOW, the receiver must not process the beat and the sender must
>   not consider the beat processed.
> - If valid is LOW, the receiver must not expect the control or data signals to
>   be a syntactically correct TileLink beat.
> - valid must never depend on ready. If a sender wishes to send a beat, it must
>   assert valid independently of whether the receiver signals that it is ready.
> - As a consequence, there must be no combinational path from ready to valid or
>   any of the control and data signals.
> - A receiver may only hold ready LOW in accordance with the deadlock freedom
>   rules in Section 4.2."

The asymmetry the chapter needs — the *destination* may look at valid, the
*source* may not look at ready — is stated explicitly in the same section:

> "Anything not forbidden is allowed. In particular, it is acceptable for a
> receiver to drive ready in response to valid or any of the control and data
> signals. For example, an arbiter may lower ready if a valid request is made for
> an address which is busy. However, whenever possible, it is recommended that
> ready be driven independently so as to reduce the handshaking circuit depth."

One important difference from AXI that the chapter must not blur: TileLink beats
are *revocable* at the channel level.

> "Note that a sender may raise valid and then lower it on the following cycle,
> even if the message was not accepted on the previous cycle. ... Furthermore,
> the sender may change the contents of the control and data signals when a
> message was not accepted."

AXI takes the opposite position (VALID, once asserted, must stay asserted and the
payload must remain stable until the transfer completes). See §6 for why the ARM
wording could not be fetched in this session; do not paraphrase ARM clause text
into the chapter until it is quoted from the specification itself.

Burst atomicity is also specified, which matters for stream-style pipelines:

> "It is forbidden in TileLink to interleave the beats of different messages on a
> channel. Once a burst has begun, the sender must not send beats for any other
> message until the last beat of the burst has been accepted by the receiver."

#### 1.2 The same contract elsewhere

That the contract is ecosystem-independent is supported by OpenTitan, which
adopts TileLink-UL as the mandatory boundary for every peripheral
[OpenTitan Comportability Definition and Specification, accessed 2026-09-07](https://opentitan.org/book/doc/contributing/hw/comportability/index.html)
**[primary]**: "All peripherals use TileLink-UL (TileLink-Uncached-Lite, aka
TL-UL) as their interface to the framework." OpenTitan's own bus documentation
restates the handshake and adds throughput restrictions — "Only one request (read
or write) per cycle" and "Only one response (read or write) per cycle"
[OpenTitan TL-UL bus documentation, accessed 2026-09-07](https://opentitan.org/book/hw/ip/tlul/index.html)
**[primary]** — and notes a deliberate deviation from the specification's reset
requirement, which is itself a good chapter example of a project documenting
where it departs from a standard.

A practitioner restatement of the AXI form of the rules, usable as a cited source
in place of the ARM text, is
[ZipCPU, "AXI Handshaking Rules", 2021-08-28](https://zipcpu.com/blog/2021/08/28/axi-rules.html)
**[primary]**, which gives them as: "Nothing happens unless `xVALID && xREADY`";
"Something _always_ happens anytime `xVALID && xREADY`"; and "Nothing can change
unless `!xVALID || xREADY`" — the last being the payload-stability rule, which the
article also expresses as the formal property `assert($stable(M_AXIS_TDATA))`
under a stall.

#### 1.3 Back-pressure and skid buffers

The skid buffer is the standard answer to "I must register my ready output and
still not drop data."
[ZipCPU, "Building a skid buffer for AXI processing", 2019-05-22](http://zipcpu.com/blog/2019/05/22/skidbuffer.html)
**[primary]** states the handshake obligation as "any time `VALID & !READY`, the
respective data values must remain constant into the next clock cycle" and "Once
o_valid goes high, the data cannot change until the clock after i_ready."

The two-slot argument, in the article's terms: when a stage registers its stall
signal, the upstream stage does not learn about back-pressure until it has already
launched a beat, so "the data needs to go somewhere or get dropped." The buffer
therefore holds an output register plus one internal register (`o_data` and
`r_data`) — one slot for the beat being presented downstream, one for the beat
already in flight. The performance argument is in the same source: the author
reports 100% throughput on both read and write channels for his AXI slave,
against "just less than a 50% read throughput" for a vendor demonstration core
without the technique. That is a practitioner measurement of one design, not a
general benchmark, and the chapter should say so.

#### 1.4 FIFOs: pointer width, full/empty, and the off-by-one

The canonical treatment is
["Simulation and Synthesis Techniques for Asynchronous FIFO Design", SNUG San Jose 2002 (rev. 1.3, Nov 2005)](https://www.paradigm-works.com/papers/)
**[industry paper]**, with a companion paper "…with Asynchronous Pointer
Comparisons" (rev. 1.3, Aug 2020). Both are listed as "Voted Best Paper 1st
Place." The sunburst-design.com paper URLs now 301-redirect to
paradigm-works.com and the PDFs sit behind a login, so the paper text could not
be quoted here (see §6).

The technique itself is quotable from
[ZipCPU, "Crossing clock domains with an Asynchronous FIFO", 2018-07-06](https://zipcpu.com/blog/2018/07/06/afifo.html)
**[primary]**, which describes the Cummings design as using `N+1` address bits for
a pointer into a `2^N`-element FIFO, and gives the full condition as: "It is full
when wbin-rbin = 2^N. In that case, the bottom AW address bits are identical, but
the top bit is different." Empty is pointer equality across all bits. The same
article states the capacity consequence the chapter wants — "his FIFO holds a
full `2^N` elements. The FIFO I presented earlier only holds `(2^N)-1` elements" —
and the Gray-code motivation: "if you want to check whether or not two pointers
are identical, you only need to check whether the two Gray coded pointers are
identical", because "only one bit will ever change at any time."

The chapter's framing — *a counter's width is an assumption about capacity* — has
a live example in OpenTitan, where the occupancy output width is computed as
`DepthW = prim_util_pkg::vbits(Depth+1)`, i.e. wide enough for the values 0
through Depth inclusive, not 0 through Depth-1
[lowRISC/opentitan, `hw/ip/prim/rtl/prim_fifo_sync.sv`, accessed 2026-09-07](https://raw.githubusercontent.com/lowRISC/opentitan/master/hw/ip/prim/rtl/prim_fifo_sync.sv)
**[primary]**. The `+1` is exactly the off-by-one under discussion.

#### 1.5 Occupancy invariants as assertions and coverage

The same file is the best evidence that occupancy invariants are written as
assertions in production RTL. Quoted verbatim:

- `` `ASSERT(depthShallNotExceedParamDepth, !empty |-> depth_o <= DepthW'(Depth)) ``
- `` `ASSERT(OnlyRvalidWhenNotUnderRst_A, rvalid_o -> ~under_rst) ``
- `` `ASSERT_KNOWN_IF(DataKnown_A, rdata_o, rvalid_o) ``

The first is the occupancy bound; the second and third are reset-behavior and
X-propagation obligations on the same boundary. A pre-built checker library also
exists: the Accellera Open Verification Library is "a library of assertion
checkers intended to be used by design, integration, and verification engineers
to check for good/bad behavior in simulation, emulation, and formal
verification", latest version 2.8.1 released 2014-04-08
[Accellera, Open Verification Library, accessed 2026-09-07](https://www.accellera.org/downloads/standards/ovl)
**[standard]**.

---

### 2. Interfaces and the block boundary

#### 2.1 SystemVerilog interface and modport

The normative home of interfaces is IEEE Std 1800, "IEEE Standard for
SystemVerilog--Unified Hardware Design, Specification, and Verification
Language", current edition IEEE 1800-2023, published 2024-02-28
[IEEE 1800-2023, 2024-02-28](https://standards.ieee.org/ieee/1800/7743/)
**[standard]**. Clause 25 of the LRM is the interfaces clause: the ChipsAlliance
conformance suite indexes its interface tests under "Chapter 25: Interface
syntax" [sv-tests results, accessed 2026-09-07](https://chipsalliance.github.io/sv-tests-results/)
**[docs]**. The LRM itself is paywalled, so the chapter should cite the clause by
name and number but must not quote LRM text that has not been read.

Second-hand confirmation that modports are direction contracts comes from the
Yosys manual, which lists among supported constructs "SystemVerilog interfaces
(SVIs), including modports for specifying whether ports are inputs"
[Yosys manual, "Verilog support", accessed 2026-09-07](https://yosyshq.readthedocs.io/projects/yosys/en/latest/using_yosys/verilog.html)
**[docs]**.

Worth reporting honestly: interfaces are not universally embraced in RTL. The
lowRISC coding style guide lists "Interfaces" among discouraged language features
[lowRISC Verilog Coding Style Guide, accessed 2026-09-07](https://raw.githubusercontent.com/lowRISC/style-guides/master/VerilogCodingStyle.md)
**[primary]**; OpenTitan instead names the contract with packed structs
(`tl_h2d_t`, `tl_d2h_t`) per the TL-UL documentation cited above. The chapter can
use this as a real disagreement rather than presenting interfaces as settled
practice.

#### 2.2 What a boundary specification contains

An openly citable, complete example of "everything a block boundary must declare"
is OpenTitan's comportability specification **[primary]** (URL above). It requires,
per peripheral: at least one device interface on the chip bus, using TL-UL; a
declared primary clock plus any secondary clocks; reset behavior, stated
normatively as "Resets within the design are **asynchronous active low**" with
deassertion synchronized to the associated clock; a register map — "Each
peripheral must define its collection of registers in the specified register
format" — from which "hardware, software, and documentation collateral" are
generated; and a declaration of interrupts versus alerts, with three
auto-generated registers `INTR_STATE`, `INTR_ENABLE`, `INTR_TEST`. Error
responses are part of the bus contract: TL-UL responses carry `d_error`, and the
response opcode is determined by the request — "If the original request was Get,
then the corresponding response must be AccessAckData. Otherwise, the response
must be AccessAck"
[OpenTitan TL-UL Protocol Checker specification, accessed 2026-09-07](https://opentitan.org/book/hw/ip/tlul/doc/TlulProtocolChecker.html)
**[primary]**.

This gives the chapter the full list — signals, protocol, clocking, reset,
register map, optionality, error responses — from one source that a reader can
open. ARM's APB and AXI-Lite would be the more familiar small examples; they are
not cited here because the specification text could not be retrieved (§6).

#### 2.3 Protocol monitors and assertion-based contracts

OpenTitan's `tlul_assert.sv` is a working, readable protocol monitor and the best
citation for "the boundary is checked by assertions" **[primary]** (URL above).
Two details are directly useful to the chapter:

1. It validates opcodes, size and address alignment, mask contiguity, data
   validity, source-ID uniqueness ("preventing multiple pending requests per
   source"), X-values on control signals, and that no requests are outstanding at
   end of simulation. Sample rule: "Only the following 3 opcodes are legal: Get,
   PutFullData, PutPartialData."
2. The same property is an *assumption* or an *assertion* depending on which side
   of the boundary the monitor is bound to — device mode uses an `_M` suffix,
   host mode an `_A` suffix — because formal verification needs the environment
   constrained rather than checked. Simulation behavior is identical. This is a
   genuinely instructive point for a verification textbook.

The standard trade reference is Foster, Krolnik and Lacey, *Assertion-Based
Design* (Springer). The Springer catalog page redirected to an authentication
endpoint in this session, so full bibliographic details (edition, year, ISBN)
must be confirmed before the book is cited (§6).

---

### 3. Structural extraction from RTL

#### 3.1 Yosys: JSON schema and the flip-flop cell library

Flow: `read_verilog -sv` → `hierarchy -check -top <top>` → `proc` → optionally
`flatten` → `opt_clean` → `write_json`.

- `hierarchy` "check, expand and clean up design hierarchy"; `-check` "generates
  an error when an unknown module is used as cell type"; `-top <module>` means
  "Modules outside this tree (unused modules) are removed"; `-auto-top`
  "automatically determine the top of the design hierarchy". `flatten` "flattens
  the design by replacing cells by their implementation", and "Cells and/or
  modules with the 'keep_hierarchy' attribute set will not be flattened"
  [Yosys manual, hierarchy passes, accessed 2026-09-07](https://yosyshq.readthedocs.io/projects/yosys/en/latest/cmd/index_passes_hierarchy.html)
  **[docs]**.
- `proc` "translate[s] processes to netlists", running `proc_clean`, `proc_rmdead`,
  `proc_prune`, `proc_init`, `proc_arst`, `proc_rom`, `proc_mux`, `proc_dlatch`,
  `proc_dff`, `proc_memwr`, `proc_clean`, `opt_expr -keepdc`
  [Yosys manual, proc passes, accessed 2026-09-07](https://yosyshq.readthedocs.io/projects/yosys/en/latest/cmd/index_passes_proc.html)
  **[docs]**. This step is mandatory before register extraction: RTLIL processes
  are not cells, and "Some passes refuse to operate on modules that still contain
  `RTLIL::Process` objects"
  [Yosys manual, RTL Intermediate Language, accessed 2026-09-07](https://yosyshq.readthedocs.io/projects/yosys/en/latest/yosys_internals/formats/rtlil_rep.html)
  **[docs]**. The same page gives the hierarchy Design → Module →
  cells/wires/processes/memories, the `\`-vs-`$` identifier convention (user names
  vs. auto-generated), and that "Busses (signal vectors) are represented using a
  single wire object with a width more than 1."

**JSON schema** [Yosys manual, backends / `write_json`, accessed 2026-09-07](https://yosyshq.readthedocs.io/projects/yosys/en/latest/cmd/index_backends.html#write-json-write-design-to-a-json-file)
**[docs]**. Top level: `creator`, `modules`, and `models` (with `-aig`). Each
module has `attributes`, `parameter_default_values`, `ports`, `cells`,
`memories`, `netnames`. A port is `{"direction": "input"|"output"|"inout",
"bits": <bit_vector>, "offset": …, "upto": …, "signed": …}`. A cell is
`{"hide_name": 1|0, "type": …, "model": …, "parameters": {…}, "attributes": {…},
"port_directions": {…}, "connections": {…}}`. Critically for a Python extractor:
signal bits are unique integers, and constant-driven bits appear as the *strings*
`"0"`, `"1"`, `"x"`, `"z"` in the same array — so a bit vector is a mixed
list of ints and strings, and net identity is integer identity.

**Register cells.** All are in the "Registers" section of the word-level cell
library [Yosys manual, word-level register cells, accessed 2026-09-07](https://yosyshq.readthedocs.io/projects/yosys/en/latest/cell/word_reg.html)
**[docs]**, with parameters and ports as follows:

| Cell | Parameters | Extra control ports |
|---|---|---|
| `$dff` | WIDTH, CLK_POLARITY | — |
| `$dffe` | + EN_POLARITY | EN |
| `$adff` | + ARST_POLARITY, ARST_VALUE | ARST |
| `$adffe` | + EN_POLARITY, ARST_POLARITY, ARST_VALUE | ARST, EN |
| `$sdff` | + SRST_POLARITY, SRST_VALUE | SRST |
| `$sdffe` | + EN_POLARITY, SRST_POLARITY, SRST_VALUE | SRST, EN |
| `$sdffce` | + EN_POLARITY, SRST_POLARITY, SRST_VALUE | SRST, EN |
| `$aldff` | + ALOAD_POLARITY | ALOAD, AD |
| `$aldffe` | + EN_POLARITY, ALOAD_POLARITY | ALOAD, EN, AD |
| `$dffsr` | + SET_POLARITY, CLR_POLARITY | SET[W-1:0], CLR[W-1:0] |
| `$dffsre` | + SET_POLARITY, CLR_POLARITY, EN_POLARITY | SET, CLR, EN |

All have `D` input and `Q` output of WIDTH bits. Note `SET`/`CLR` on `$dffsr` are
per-bit vectors, not scalars — a per-bit set/reset structure a naive extractor
will get wrong. The `$adlatch`, `$dlatch`, `$dlatchsr` and `$sr` cells are in the
same section and are what an unintended latch shows up as.

**Front-end limits.** With `-sv`, Yosys supports `assert`/`assume`/`restrict`/
`cover`, `always_comb`/`always_ff`/`always_latch`, `logic`/`bit`, `rand` free
variables, packages (not nested), typedefs, enums, packed structs/unions,
multidimensional arrays, interfaces with modports, and `unique`/`unique0`/
`priority`. Unsupported: type casts, structure literals, array literals, and
array assignment of unpacked arrays; on the Verilog-2005 side, `tri`/`triand`/
`trior`, `config` and `disable` (URL above, **[docs]**). Anything using the
unsupported constructs will not reach the JSON at all.

#### 3.2 pyslang / slang: the AST route

slang is "a C++ library and command-line tool" for "lexing, parsing, type
checking, and elaboration" of SystemVerilog, offering "Full type checking,
cross-module elaboration, semantic verification, and data-flow analysis" and
targeting "the 1800-2023 LRM"
[sv-lang.com, accessed 2026-09-07](https://sv-lang.com/) **[docs]**. It claims to
be "the fastest and most compliant SystemVerilog frontend according to the open
source chipsalliance test suite" — a project self-claim, though the sv-tests
comparison cited in §2.1 is the independent scoreboard behind it. The driver has
`--ast-json` for dumping the elaborated AST; Python bindings install with
`pip install pyslang`; license MIT
[MikePopoloski/slang, accessed 2026-09-07](https://github.com/MikePopoloski/slang)
**[docs]**. Packaging note the chapter's example must respect: the standalone
pyslang repository was **archived 2025-01-18** and is read-only, its packaging
having moved into the upstream slang repository
[MikePopoloski/pyslang, accessed 2026-09-07](https://github.com/MikePopoloski/pyslang)
**[docs]**.

What it gives that a netlist does not: source locations, the unelaborated syntax
tree, declarations that synthesis erases (typedefs, parameters, generate
structure, assertions), and errors with diagnostics. What it does not give: a
synthesized netlist — no inferred flip-flop cells, no post-optimization net
identity, no answer to "which registers actually exist."

#### 3.3 Verilator: AST dump and SARIF diagnostics

`--json-only`: "Create JSON output only, do not create any other output" — the
elaborated AST as `.tree.json` plus `.tree.meta.json`, with
`--json-only-output`, `--json-only-meta-output`, `--no-json-edit-nums` (for
run-to-run stability) and `--no-json-ids`. `--lint-only`: "Check the files for
lint violations only, do not create any other output". `--diagnostics-sarif`:
"Enables diagnostics output into a Static Analysis Results Interchange Format
(SARIF) file, a standard, JSON-based format for the output of static analysis
tools such as linters", with `--diagnostics-sarif-output <filename>`
[Verilator manual, verilator arguments, accessed 2026-09-07](https://veripool.org/guide/latest/exe_verilator.html)
**[docs]**. The manual itself flags that the JSON format evolves across versions.

**`--xml-only` is gone.** The changelog records "Add DEPRECATED warning on
`--xml-only` and `--xml-output`" in Verilator 5.036 (2025-04-27) and "Remove
deprecated `--xml-only`" in 5.044 (2026-01-01); `--diagnostics-sarif` arrived in
5.038 (2025-07-08)
[Verilator Changes, accessed 2026-09-07](https://raw.githubusercontent.com/verilator/verilator/master/Changes)
**[docs]**. The chapter must describe the JSON route, not the XML route.

#### 3.4 Other routes

- **Verible**: `verible-verilog-syntax` exports the concrete syntax tree with
  `--export_json`, which "Uses JSON for output. Intended to be used as an input
  for other tools", plus `--printtree`
  [Verible, verilog_syntax, accessed 2026-09-07](https://chipsalliance.github.io/verible/verilog_syntax.html)
  **[docs]**. Syntax only — no elaboration.
- **Surelog / UHDM**: "a complete SystemVerilog 2017 front-end: a preprocessor, a
  parser, an elaborator for both design and testbench", emitting UHDM databases
  that follow "the Standard VPI API", consumable from C/C++ or through a Python
  wrapper; Apache 2.0
  [chipsalliance/Surelog, accessed 2026-09-07](https://github.com/chipsalliance/Surelog)
  **[docs]**.

#### 3.5 What no structural tool can decide without a specification

The following are *inferences from what the formats above contain*, not sourced
claims, and are labeled as such in §4. None of the four routes emits: which
clocks are asynchronous to which (Yosys JSON carries cells, nets, parameters and
attributes — no clock-relationship or timing information; that lives in an SDC or
equivalent constraints file, outside every format described here); the intended
reset sequence and release order; which clock-domain crossings have been reviewed
and waived; whether a register array is a FIFO, a scoreboard or a lookup table;
or which of two structurally identical counters is a capacity bound and which is
an index. A netlist answers *what exists*; it never answers *what was meant*. The
chapter's worked example should therefore be framed as producing a **candidate
list requiring a specification to interpret**, not an answer.

---

### 4. Commonly repeated but unsourced claims

| Claim | Where it is repeated | Status |
|---|---|---|
| "A source must not wait for READY before asserting VALID; VALID must remain asserted until the transfer completes" (AXI wording) | Universally attributed to ARM IHI 0022 §A3.2 | **Not verified here.** The rule is confirmed for TileLink §4.1 and paraphrased by ZipCPU for AXI; the ARM clause number and wording were not retrievable (§6). Do not print a clause number. |
| `$sdffce` gates the synchronous reset with EN while `$sdffe` does not | Yosys community usage | Plausible from the identical parameter lists, but the cell page prose was not captured. Verify against the `word_reg.html` text before asserting. |
| Cliff Cummings is the author of the SNUG 2002 FIFO papers | Ubiquitous | Almost certainly correct, but the fetched paradigm-works listing gave title/venue/year without an author line. Confirm from the PDF before citing an author. |
| "A skid buffer costs zero throughput" | Practitioner blogs | Supported only as a single-design measurement (§1.3); state as such. |
| Avalon-ST states the same valid/ready rules | Common in the FPGA world | Unverified — the Intel documentation URL redirected to a 404 redirector. Use TileLink/OpenTitan instead. |
| Structural extraction cannot recover clock relationships | This note, §3.5 | Inference from the documented contents of the four formats, not a cited claim. Present as reasoning. |

---

### 5. Suggested BibTeX keys

| Key | Citation | Used by |
|---|---|---|
| `sifive2017tilelink` | SiFive, Inc. *SiFive TileLink Specification, Version 1.7-draft*, 2017-08-21. https://static.dev.sifive.com/docs/tilelink/tilelink-spec-1.7-draft.pdf | §1.1, §1.2 |
| `opentitan2026comportability` | lowRISC. *Comportability Definition and Specification*, OpenTitan documentation, accessed 2026-09-07. https://opentitan.org/book/doc/contributing/hw/comportability/index.html | §1.2, §2.2 |
| `opentitan2026tlul` | lowRISC. *TileLink-UL bus*, OpenTitan documentation, accessed 2026-09-07. https://opentitan.org/book/hw/ip/tlul/index.html | §1.2, §2.2 |
| `opentitan2026tlulchecker` | lowRISC. *TL-UL Protocol Checker Specification*, accessed 2026-09-07. https://opentitan.org/book/hw/ip/tlul/doc/TlulProtocolChecker.html | §2.3 |
| `opentitan2026primfifo` | lowRISC. `hw/ip/prim/rtl/prim_fifo_sync.sv`, OpenTitan, accessed 2026-09-07. https://raw.githubusercontent.com/lowRISC/opentitan/master/hw/ip/prim/rtl/prim_fifo_sync.sv | §1.4, §1.5 |
| `lowrisc2026style` | lowRISC. *Verilog Coding Style Guide*, accessed 2026-09-07. https://github.com/lowRISC/style-guides/blob/master/VerilogCodingStyle.md | §2.1 |
| `gisselquist2019skid` | Gisselquist, D. "Building a skid buffer for AXI processing", ZipCPU, 2019-05-22. http://zipcpu.com/blog/2019/05/22/skidbuffer.html | §1.3 |
| `gisselquist2021axirules` | Gisselquist, D. "AXI Handshaking Rules", ZipCPU, 2021-08-28. https://zipcpu.com/blog/2021/08/28/axi-rules.html | §1.2 |
| `gisselquist2018afifo` | Gisselquist, D. "Crossing clock domains with an Asynchronous FIFO", ZipCPU, 2018-07-06. https://zipcpu.com/blog/2018/07/06/afifo.html | §1.4 |
| `cummings2002fifo` | *Simulation and Synthesis Techniques for Asynchronous FIFO Design*, SNUG San Jose, 2002 (rev. 1.3, Nov 2005). https://www.paradigm-works.com/papers/ | §1.4 |
| `ieee2023sv` | IEEE Std 1800-2023, *IEEE Standard for SystemVerilog — Unified Hardware Design, Specification, and Verification Language*, 2024-02-28. https://standards.ieee.org/ieee/1800/7743/ | §2.1 |
| `chipsalliance2026svtests` | ChipsAlliance. *sv-tests results*, accessed 2026-09-07. https://chipsalliance.github.io/sv-tests-results/ | §2.1, §3.2 |
| `accellera2014ovl` | Accellera. *Open Verification Library*, v2.8.1, 2014-04-08. https://www.accellera.org/downloads/standards/ovl | §1.5 |
| `yosys2026json` | YosysHQ. *Yosys manual: backends (`write_json`)*, accessed 2026-09-07. https://yosyshq.readthedocs.io/projects/yosys/en/latest/cmd/index_backends.html | §3.1 |
| `yosys2026regcells` | YosysHQ. *Yosys manual: word-level register cells*, accessed 2026-09-07. https://yosyshq.readthedocs.io/projects/yosys/en/latest/cell/word_reg.html | §3.1 |
| `yosys2026rtlil` | YosysHQ. *Yosys manual: RTL Intermediate Language*, accessed 2026-09-07. https://yosyshq.readthedocs.io/projects/yosys/en/latest/yosys_internals/formats/rtlil_rep.html | §3.1 |
| `yosys2026verilog` | YosysHQ. *Yosys manual: Verilog support*, accessed 2026-09-07. https://yosyshq.readthedocs.io/projects/yosys/en/latest/using_yosys/verilog.html | §2.1, §3.1 |
| `slang2026` | Popoloski, M. *slang — SystemVerilog compiler and language services*, accessed 2026-09-07. https://sv-lang.com/ and https://github.com/MikePopoloski/slang | §3.2 |
| `verilator2026manual` | Verilator developers. *Verilator manual: verilator arguments*, accessed 2026-09-07. https://veripool.org/guide/latest/exe_verilator.html | §3.3 |
| `verilator2026changes` | Verilator developers. *Changes*, accessed 2026-09-07. https://raw.githubusercontent.com/verilator/verilator/master/Changes | §3.3 |
| `verible2026syntax` | ChipsAlliance. *Verible: verilog_syntax*, accessed 2026-09-07. https://chipsalliance.github.io/verible/verilog_syntax.html | §3.4 |
| `surelog2026` | ChipsAlliance. *Surelog*, accessed 2026-09-07. https://github.com/chipsalliance/Surelog | §3.4 |

---

### 6. Confidence notes and gaps

**High confidence** (text quoted from the source in this session): TileLink §4.1
flow-control rules; OpenTitan comportability, TL-UL and protocol-checker
requirements; `prim_fifo_sync` assertions and `DepthW` computation; all Yosys
command, cell and JSON-schema details; Verilator option text and the `--xml-only`
removal timeline; Verible, Surelog, slang and pyslang facts; OVL version and date.

**Fetch failures, recorded honestly.**

1. **ARM specifications could not be read.** `developer.arm.com/documentation/
   ihi0022/latest/` 301-redirects to `support.arm.com`, which returns a
   JavaScript shell with no document text; `static.docs.arm.com` no longer
   resolves (DNS failure); the AMD/Xilinx AXI reference-guide PDFs redirect to
   `adaptivesupport.amd.com`; `web.archive.org` is not reachable from this
   session's fetch tool; and the browser-automation extension was not connected.
   The session's web-search quota was also exhausted before this work began, so
   no alternative mirror could be located. **Consequence: the chapter must not
   state an ARM clause number or quote ARM wording for the AXI or APB handshake
   until someone reads IHI 0022 / IHI 0024 directly.** §1.1 and §1.2 give
   equivalent, fully quotable material from TileLink and OpenTitan, which is
   arguably better for an open textbook.
2. **Cummings SNUG papers**: sunburst-design.com now redirects to
   paradigm-works.com and the PDFs require login. Title, venue, year, revision
   and award are sourced; author is not (§4).
3. **Avalon-ST**: the Intel documentation URL redirected into a 404 redirector.
4. **Foster/Krolnik/Lacey, *Assertion-Based Design***: the Springer catalog page
   redirected to an authentication endpoint; edition/year/ISBN unconfirmed. §2.3
   substitutes OpenTitan's `tlul_assert.sv` as the citable example.
5. **IEEE 1800 clause text**: paywalled. Clause 25 is confirmed as the interfaces
   clause only indirectly, via the sv-tests chapter index. Cite by number and
   name; do not quote.

**Deliberate scope choice.** §1.1 uses TileLink rather than AXI as the normative
anchor. This is defensible on its merits — the rules are stated more explicitly
and the document is freely readable — but the chapter should still name AXI as
the industrially dominant instance, and should flag TileLink's revocable-valid
divergence from AXI so a reader does not carry the wrong rule into an AXI review.
