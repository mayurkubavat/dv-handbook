# Chapter 3 research, part 1: RTL and synthesis, state machines, lint and X

Source access: `sunburst-design.com/papers/` now 301-redirects to
`paradigm-works.com`, whose index requires registration and exposes no PDF
links. The Cummings/Mills papers were therefore read from Internet Archive
captures of the original URLs; canonical URL and capture date are both given.
IEEE 1800 and IEEE 1364.1 clause text is paywalled and was **not** read — §6.

---

## 1. What RTL is, and what synthesis makes of it

### 1.1 The synthesizable subset and the IEEE definition

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

### 1.2 `always_ff` / `always_comb` / `always_latch` as checked intent

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

### 1.3 Simulation/synthesis mismatch: the classic causes

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

## 2. State machines

### 2.1 Coding styles and encodings

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

### 2.2 Unreachable, illegal, deadlock: the verifier's reading

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

### 2.3 Coverage and formal

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

## 3. Lint and X

### 3.1 Verilator warning classes

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

### 3.2 Verible rules

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

### 3.3 What lint structurally cannot find

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

### 3.4 X-propagation, X-optimism and X-pessimism

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

## 4. Commonly repeated but unsourced claims

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

## 5. Suggested BibTeX keys

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

## 6. Confidence notes and gaps

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
