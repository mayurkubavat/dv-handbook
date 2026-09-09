---
title: "Research note: Chapter 4, part 2 — sampling, X, and time"
date: 2026-09-09
author: research-agent
status: draft
feeds: Ch. 4
---

# Chapter 4 research, part 2: sampling, X, and time

**Scope.** The testbench/design boundary at a clock edge, the constructs added to
close it, assertion sampling, four-state versus two-state simulation, and
timescale. It does not re-derive Turpin 2003 (`turpin2003x`); it picks the
argument up after 2003.

**Reachability.** `sunburst-design.com` redirects to `paradigm-works.com` with its
paper archive behind a login, so all Cummings papers here were recovered from
Internet Archive captures of the original URLs, and those capture URLs are what is
cited. The same route was needed for `sutherland-hdl.com` and `verilab.com`. IEEE
1800 is **named only**: it is paywalled and unread, so every behavioral statement
below is attributed to a practitioner paper or to open simulator documentation.
Where a source describes the standard, I relay the source's description and
attribute it to that source. Anything supportable only from the standard is in §6.

---

## 1. The testbench/design boundary at a clock edge

Primary source: Cummings and Salz, *SystemVerilog Event Regions, Race Avoidance &
Guidelines*, SNUG Boston 2006 (rev. 1.2, Dec 2007), 42 pp., co-authored by a
Synopsys simulator architect.
[Cummings & Salz, SNUG Boston, 2006-09-01](https://web.archive.org/web/20240110182353id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

Its framing is the one to adopt. It separates *hardware races* — intrinsic to the
physics, like the NAND S-R latch whose final state is unpredictable when both
inputs release together — from *simulation-induced races*, "not intrinsic to the
design or its physics, but ... a natural, although undesirable, consequence of the
event-driven simulation algorithm": the simulator processes events one at a time
and so serializes what hardware does concurrently. The motivating sentence for the
chapter: such a race "can cause the simulator to simulate a faulty design when in
fact the design is correct, or more dangerously, simulate a seemingly correct
design when in fact the design is flawed." The order within a region is left
arbitrary by the language but every implementation exhibits *some* fixed order —
which is why a race can be invisible on one simulator and fatal on the next (§2.1).

- **Terminology** (§2): *simulation time* is the value the simulator maintains; a
  *time slot* holds all activity at one simulation time and may need several
  iterations through the regions without time advancing. The older term *timestep*
  was dropped in the 2008 revision.
- **Structure** (§2.2): 17 ordered regions per time slot in the 2005 revision —
  nine for language statements, eight for PLI. The nine: Preponed; the *Active
  region set* (Active, Inactive, NBA); Observed; the *Reactive region set*
  (Reactive, Re-Inactive, Re-NBA); Postponed. Grouped by intent: Active-set for
  RTL, Preponed/Reactive/Postponed for verification, Preponed/Observed/Reactive for
  assertions. They recommend never using the Inactive region — `#0` in RTL papers
  over a race rather than fixing it (§2.2.4).
- **The race concretely.** Clocked design logic updates in NBA; a module-based
  testbench reading in the Active region of the same edge sees the *old* value, one
  reading after NBA sees the new, and nothing fixes which if both are in Active.
  Cummings' earlier nonblocking-assignment guidelines — credited in the 2006 paper
  with removing "90-100%" of induced RTL races — are the design-side half of the
  fix: clocked logic nonblocking, combinational blocking, never two `always` blocks
  writing one variable.
  [Cummings, SNUG San Jose, 2000-03-01](https://web.archive.org/web/2020/http://www.sunburst-design.com/papers/CummingsSNUG2000SJ_NBA.pdf)
  **[primary]** (URL from the 2006 reference list; not fetched — see §8.)
- **The pre-SystemVerilog workarounds** (§6.1). Driving stimulus *on* the active
  edge required nonblocking assignments on every input, mimicking a zero-delay
  register transfer — which then breaks on a netlist with real hold times, because
  all inputs change in zero time. Engineers reached for `<= #1` right-hand-side
  delays, which Cummings had already shown to be "a potential source for serious
  simulator performance degradation." The Sunburst style drove on the *inactive*
  edge instead, far from setup and hold, letting one testbench serve RTL and a
  back-annotated netlist unchanged. This is the practical argument for keeping
  driver and monitor off the same edge.

## 2. Clocking blocks and program blocks: the problem they solve

**Why skews exist.** Best statement found: Bromley and Johnston, *Taming Testbench
Timing: Time's Up for Clocking Block Confusions*, SNUG Austin 2012 (Verilab), §2 —
a synchronous testbench must "sample signals one setup time before the clock event"
and "update signals one clock-to-output delay after the clock event," because that
is what the DUT's own flip-flops do. Input skew is the testbench's t<sub>SU</sub>,
output skew its t<sub>CO</sub>. Their heading "A Clocking Block Is Not A Time
Machine" is the pitfall in one line: at an edge a testbench sees current and past
values, never future ones. They note the construct "has proved to be surprisingly
error-prone, despite nearly a decade of application experience."
[Bromley & Johnston, SNUG Austin, 2012-09-01](https://web.archive.org/web/2020id_/http://www.verilab.com/files/paper51_taming_tb_timing_FINAL_fixes.pdf)
**[primary]**

Their eleven guidelines are the most citable distillation found. The four that
matter here: access only the clockvars, never the raw signal (#1); synchronize on
the clocking block's own event, not the raw clock (#2); drive output clockvars with
`<=`, never `=` (#3); and **use `input #1step` unless you have a special reason
not to, because it guarantees the testbench sees sampled values consistent with
what assertions see** (#4) — the direct citation for the Chapter 4 → Chapter 9 link.
Also: #5 recommends non-zero output skew for readable waveforms and gate-level
clock-network delay; #9–#11 put the clocking block in an interface reached through
a virtual-interface modport.

From Cummings and Salz (§5, §6.2): signals get clocking-block timing **only when
referenced through the block's name** — the bare name is still the raw, untimed
signal, and mixing the two accidentally is the failure mode (interfaces with
modports are the structural guard). Default input skew is one *step*, default
output skew zero (§2.2.13). `##` cycle delay is defined against the block's event,
so `##1` in a `@(posedge clk)` block waits for that edge (§5.1). Their Example 12
traces a program block mixing plain assignment with `##1 cb1.d <= ...` through an
`output #2 d` skew, event by event (Figures 12–18) — the cleanest published
demonstration that the skew is the point. They also answer the performance
objection: driving on the inactive edge costs no extra events, since combinational
logic must ripple to quiescence either way (§6.2).

**Program blocks: what they were for.** Cummings and Salz (§2.2.7–2.2.8) describe
the Reactive region set as the dual of the Active set, later in the same time slot,
so program code has access to three things module code does not — steady-state
values at the start of the slot, settled values after propagation, and the
disposition of every concurrent assertion that fired. They recommend programs "to
isolate RTL design code execution from testbench code execution," and note one
legitimate use of `#0` (Re-Inactive) they reject in RTL: letting `fork ...
join_none` children start before the parent continues.

**The disagreement — unusually well documented, because it is Cummings against
himself.** Ten years later he reverses, in *Applying Stimulus & Sampling Outputs —
UVM Verification Testing Techniques*, SNUG 2016.
[Cummings, SNUG, 2016-09-01](https://web.archive.org/web/2023id_/http://www.sunburst-design.com/papers/CummingsSNUG2016AUS_VerificationTimingTesting.pdf)
**[primary]**

His §10 argument: the program block "essentially made it possible to drive stimulus
on the active clock edge and avoid RTL-stimulus race conditions," but stimulus
should not be driven there at all — and "as long as the verification engineer does
not drive stimulus on the active clock edge, there is no RTL-stimulus race
condition and a program is not needed." He adds restrictions he calls gratuitous
(`initial` but not `always` inside a program; a program may hierarchically
reference module signals but not the reverse; a program may call module tasks but
not the reverse; simulators have not consistently checked program code) and
concludes: "The SystemVerilog program statement should just die and never be used
in your code!"

§10.1, "Cliff's confession," is the passage to cite, because it records the other
side's reasoning too: he voted to keep programs in the 2015 revision after
advocates argued they let engineers write race-free stimulus *without* having to
learn his drive-off-the-active-edge technique; he now regrets the vote. Two
defensible positions, from one author: programs as a guard rail for engineers who
have not internalized the timing discipline, versus programs as unnecessary once
that discipline is in place. **Present both; do not adjudicate.** Corroborating
context only: the 2006 paper already warned (§1.2) that committee clarifications
"might change some of the restrictions of programs, clocking blocks, event
regions"; and Bromley and Johnston use no program blocks at all — suggestive, but
not a stated position, and not to be reported as one.

## 3. Assertion sampling

Cummings and Salz (§2.2.1, §2.2.6, §2.2.13): values used by concurrent assertions
are sampled in the **Preponed** region — first in the time slot, executed once
immediately after time advances, with no feedback path back into it — and the
assertions are *evaluated* later, in the **Observed** region, after Active-set
activity has settled. An assertion therefore reads the value that was stable
*before* the edge, not the value the edge produced. That is precisely why it is
immune to the §1 race: the race is Active-versus-NBA ordering, and the assertion
reads in neither.

Four refinements to keep straight:

- **Preponed vs. the previous Postponed is unobservable.** Both are read-only, so
  values in a contiguous Postponed–Preponed pair are identical and only the
  timestamp differs — "it is not observable in which region the simulator actually
  samples a value." Do not claim a simulator *must* sample in Preponed.
- **Implementation model** (Figure 7): keep two values per sampled signal, current
  and Preponed, and read the second when the clocking expression fires. Sampling is
  needed only in slots where that expression triggers, and the simulator need not
  predict it. They describe it as an intra-slot delay gate whose delay can be
  varied to sample an arbitrary distance before the clocking event — input skew is
  the special case.
- **Assertions are monitors.** They cannot modify design state; a pass/fail action
  block is scheduled into the *Reactive* region, not Observed (§2.2.6).
- **`#1step`.** A step is the *global time precision*: the smallest precision
  declared anywhere in the design (§2.2.13; see §5). Their summary is that all
  values used by assertions, with or without clocking-block timing, effectively
  come from one step before the current slot, and since nothing can happen in that
  interval this is indistinguishable from Preponed sampling. Worth stating because
  it explains *why* the default skew is a step and not a real delay: it is the
  largest skew that provably cannot skip an event.

**`$strobe` vs. `$display` vs. `$monitor`** (§2.2.3, §2.2.11) — the single most
directly usable finding in this note:

| Task | Region | What it therefore shows |
|---|---|---|
| `$display` | Active | the value when the statement executes — before NBA updates land |
| `$strobe` | Postponed | the final settled value for the time slot |
| `$monitor` | Postponed | same, re-triggered on any change in its argument list |

There is no feedback path out of Postponed, so those values are final for the slot;
this matches the older Verilog Monitor region. Postponed is also where
strobe-sampled functional coverage is collected. A `$display` in a clocked block
printing stale values is the classic first encounter with the scheduler, and
`$strobe` is the one-line fix.

## 4. Four-state and two-state simulation

Carried by Sutherland, *I'm Still In Love With My X! (but, do I want my X to be an
optimist, a pessimist, or eliminated?)*, DVCon 2013 — written explicitly as the
successor to Turpin 2003 and Mills 2004 — and by Piper and Vimjam, *X-propagation
Woes*, DVCon 2012.
[Sutherland, DVCon, 2013-02-25](https://dvcon-proceedings.org/wp-content/uploads/im-still-in-love-with-my-x.pdf)
**[primary]** ·
[Piper & Vimjam, DVCon, 2012-02-28](https://dvcon-proceedings.org/wp-content/uploads/x-propagation-woes-masking-bugs-at-rtl-and-unnecessary-debug-at-the-netlist-presentation.pdf)
**[vendor]** — the latter is the presentation deck (the paper PDF is not on the
proceedings site); its author is a Real Intent technical marketing manager and its
last third pitches a Real Intent flow, so the taxonomy is usable and the proposed
solution is a vendor claim.

**The four values.** Sutherland's framing is sharper than the usual list: 0, 1 and
Z are *abstractions of values that exist in silicon* (abstract because they carry
no voltage, current or slope), whereas **X is not an abstraction of anything in
silicon** — it is the simulator saying it cannot predict whether the real value
would be 0, 1 or Z. Piper and Vimjam make the same point as a tool-disagreement
table worth redrawing: to simulation X means *unknown, not 0 or 1*; to synthesis,
*don't care, either 0 or 1*; to formal, *both 0 and 1*. Sutherland's list of
sources of X (§2): uninitialized 4-state variables; uninitialized registers and
latches; low-power shutdown/power-up; unconnected input ports; bus contention;
operations with unknown results; out-of-range bit-selects and array indices; gates
with unknown outputs; setup/hold violations; deliberate assignment; testbench
injection.

**X-optimism, mechanically.** If the control condition of `if...else` evaluates to
unknown, the `else` branch executes (§3.1). A `case` with an X selector matches
nothing and falls to `default`; `casex`/`casez` are worse, because the wildcard
*masks out* an X in the selector and picks a branch. Operators do the same at the
bit level: X AND 0 is 0, not X. The nuance the chapter must keep — **sometimes
optimism is right.** Sutherland's Figure 1 is a flip-flop with synchronous
active-low reset: at power-up `d` is ambiguous, but with `rstN` at 0 the AND output
is 0 in real silicon regardless, so pessimistic propagation would fail to reset in
simulation a design that resets fine in silicon. His Table 1 shows the other side:
for `if (sel) y = a; else y = b;` with `sel` unknown, the RTL yields a known value
for every combination while both MUX-gate and NAND-gate netlists yield X where
silicon is genuinely undeterminable.

**X-pessimism, mechanically.** Piper and Vimjam's reconvergence example:
`out = a*sel + b*!sel` with `a = b = 1` and `sel = X` evaluates to `X + !X`, which
the simulator must call X, though the real circuit outputs 1 either way — it cannot
know the two `sel` references are the same signal. Their summary is quotable:
"X-optimism = unknown reduced to known ... can result in the masking of a functional
bug"; "X-pessimism = more X than necessary ... false negatives mean more debug."
Sutherland adds the operational consequence: *X lock-up*, where a state element that
has captured an X can never leave it, because every decision that would clear it is
itself now unknown.

**What has been written since Turpin 2003.** Four strands:

1. **X-propagation modes (`xprop`).** Sutherland §7 is the honest account: some
   simulators offer a non-standard, deliberately more pessimistic algorithm for
   `if...else`, `case` and edge sensitivity, aiming at a balance rather than either
   extreme. He names the Synopsys VCS `-xprop` option and its "T-merge" algorithm as
   the example, and is clear that this **breaks the language's rules by design**.
   His two objections should carry into the chapter: an xprop mode makes a bug
   propagate *downstream* to become visible, which then forces tracing an X backward
   through many lines and clock cycles to its cause; and the added pessimism risks
   false failures and X lock-up. Name the vendor option once as an example, not a
   recommendation.
2. **Formal and static approaches.** Piper and Vimjam's survey of "point solutions"
   is the usable taxonomy: structural analysis (finds X-susceptible constructs, "can
   be very noisy," no sequential reasoning); simulation with manual diffing ("slow
   and painful," and "random initialization to eliminate X's can hide issues");
   hand-written X-accurate models using `===`, which they show is "error prone" and
   does not scale past a toy; model checking, where X is exercised as both 0 and 1
   exhaustively but capacity is limited and intent must first be written as
   assertions; and symbolic simulation, exhaustive but producing false failures.
   Their combined flow is the vendor claim.
3. **Turpin's own follow-up**, *Solving Verilog X-issues by sequentially comparing a
   design with itself*, SNUG Boston 2005 — cited from Sutherland's reference list,
   **not read** (§8).
4. **Reducing X at the source.** Sutherland §9 is the recommendation to actually
   give a reader: trap the X where it appears, with immediate assertions on module
   input ports and every selection control — `assert (!$isknown(sel)) else
   $error(...)`. His argument is that this "solves the problems of both X-optimism
   and X-pessimism" at once, since neither matters if the X never leaves its origin;
   and that assertions can be disabled during reset and low-power windows where X is
   expected, which no propagation mode does selectively. Assertions are ignored by
   synthesis, so nothing needs hiding behind `ifdef`.

**Two-state: what is gained — folklore versus evidence.** Sutherland §5 lists the
theoretical gains: no X lock-up, closer agreement with synthesis and with silicon
(which never holds an X), smaller memory footprint, faster run time. Cummings and
Bening set out to quantify exactly that and found much less.
[Cummings & Bening, SNUG Boston, 2004-09-01](https://web.archive.org/web/2023id_/http://www.sunburst-design.com/papers/CummingsSNUG2004Boston_2StateSims.pdf)
**[primary]**

The ceiling (§5.1): a 4-state value needs at least 2 bits, and a net may also carry
3 bits of drive strength for 0 and 3 for 1, so a simulator may spend up to 8 bits of
storage per simulated bit; two-state gives a one-to-one mapping and lets native
machine operations replace table lookups. The measurement (§7): on a roughly
2.4-million-gate-equivalent RTL chip model at Hewlett-Packard, benchmarked in March
2001 on VCS 6.0, the run took **2045.96 CPU seconds without the two-state option and
1928.97 with it — about a 6% improvement.** They add that they have "heard of some
design teams that claim upwards of 15%" but "have not seen this level of performance
improvement," and did not consider speed a compelling reason to switch; the
compelling reason was the *methodology*. Two cautions: it is one 2001 measurement on
one simulator and design, and §6.4 warns "it would be a mistake to quote the
performance figures from this paper even 6 months from now." Use it to puncture the
folklore, not as a current figure. Their §8 is a good callout: HP's large server
projects kept a two-state *design style* enforced by lint rules, random
initialization and assertions, while still running on four-state commercial
simulators — two-state as a discipline, not a simulator switch.

**Two-state: what is lost.** Sutherland §5–§6: uninitialized state stops announcing
itself; X and Z checks silently stop working (`assert (data === 'Z)` and
`assert (^data !== 'X)` can never fire); a deliberate `default: result = 'X;`
don't-care becomes a concrete value the simulator picks, so the "don't care" claim
is never tested; and the mapping rule is blunt — assigning a 4-state value to a
2-state variable turns every X or Z bit into **0**, which "does not accurately mimic
silicon behavior where each ambiguous bit might be either a 0 or a 1." His §6 worked
example is the one to adapt: a program counter instantiated with `loadN` and
`new_count` left unconnected. Four-state shows X and the bug is visible; two-state
makes `loadN` a constant 0, `if (!loadN)` always true, and the counter sits in load
state forever, looking like a bug somewhere else.

**Randomized two-state initialization is a different technique** and should be kept
separate from both plain two-state and from xprop. It traces to Bening, *A two-state
methodology for RTL logic simulation*, DAC 1999 (from Sutherland's reference list;
not read — §8): start each register bit at a *random* 0 or 1 and run many seeds, so
reset coverage samples power-up states instead of pinning to all-zeros. Sutherland's
objection to plain two-state is exactly that all-zeros "verifies only one extreme and
unlikely hardware condition." Cummings and Bening add the catch (§6.5, §10): the
randomization must be *reproducible*, and in 2004 neither the language nor VCS
offered seeded repeatable initialization — the preferred method was covered by an HP
patent and "might not be available for public use."

The open realization is now Verilator's, which makes it citable and inspectable.
[Verilator manual, accessed 2026-09-08](https://verilator.org/guide/latest/exe_verilator.html)
**[docs]** ·
[Verilator language support, accessed 2026-09-08](https://verilator.org/guide/latest/languages.html)
**[docs]**

- Verilator states it is "mostly a two-state simulator, not a four-state
  simulator"; `--fourstate` is documented as "Experimental, for developer use only,"
  and `--no-fourstate` is the default. That makes it a usable classroom demonstration
  of what two-state costs, which suits the book's open-tool constraint.
- `--x-initial` controls variables not otherwise initialized: `0` zeroes everything;
  `unique` (default) calls a function per initialization and "allows for finding reset
  bugs"; `fast` picks whatever enables the most optimization and "will likely hide any
  code bugs relating to missing resets." With `unique`, the runtime options
  `+verilator+rand+reset+2` and `+verilator+seed+<value>` give exactly the seeded
  randomization Cummings and Bening could not get in 2004 — and the manual tells you
  to print the seed so a failure can be reproduced.
- `--x-assign` is the *separate* control for X values written explicitly in source:
  `0`, `1` ("more likely to find reset bugs as active high logic will fire"), `fast`
  (default), `unique` ("the slowest, but safest for finding reset bugs"). Two knobs,
  two populations of X — preserve the distinction.
- The language page's recommended procedure is a ready-made exercise: run initialized
  to all zeros, then all ones, then random, and check reset reaches the same state.

**Reset and initialization — the link back to Chapter 3.** Sutherland §2.1–§2.2
gives the mechanism: 4-state variables begin simulation at X, so register and latch
outputs start at X; a register output "will remain an X until the register is either
reset or a known input value is clocked into" it, and a latch stays X until both
enabled and fed a known value — in RTL and gate-level alike. That is why four-state
simulation of an unreset design shows X, and why the X is *informative*. Two-state
shows 0 (or a seeded random value), the design proceeds, and nothing announces that
reset was never connected. The sharpest available argument for Chapter 3's reset
tests, and it cuts both ways worth stating: **the reset test is what makes two-state
simulation safe**, and without it two-state hides precisely the bug class the test
exists to find.

Two Verilator details bearing on reset tests: uninitialized *clocks* get 0 rather
than a random value; and by default X→0 does not produce a negedge, so a reset
sequence that (badly) relies on the X→0 edge of an uninitialized `rst_n` simply will
not fire. `--x-initial-edge` emulates event-driven simulators that do generate it,
with the manual's own caveat that needing it "may be another indication of problems
with the modeled design that should be addressed." Its suggested fix — declare
`logic rst_n = 1;` at construction and drive it to 0 in an `initial` block at time
zero, creating a real edge — is the same trick as Cummings and Salz's recommended
clock oscillator, which assigns `clk <= '0` at time zero for a deterministic,
race-free X→0 negedge (§4, Example 5).

## 5. Time, timescale and precision

Best source: Sutherland, *Gotcha Again: More Subtleties in the Verilog and
SystemVerilog Standards That Every Engineer Should Know*, SNUG San Jose 2007, §8.1,
written symptom-first and adaptable directly.
[Sutherland, SNUG San Jose, 2007-03-01](https://web.archive.org/web/2020id_/http://www.sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf)
**[primary]**

His symptom is exactly the "plausible rather than obviously wrong" failure the
chapter wants: *"My design outputs do not change at the same time in different
simulators."* Nothing errors; the waveform is merely shifted.

- **Mechanism.** A `#` delay is a bare number with no unit. The unit comes from a
  `` `timescale `` directive carrying two arguments — the module's time *unit* and
  time *precision*, each an increment of 1, 10 or 100 in units from seconds to
  femtoseconds. Precision is what lets a module express a non-whole delay and is
  relative to the unit; within a simulation "all delays are scaled to the smallest
  precision used by the design." So `` `timescale 1ns/100ps `` makes `#2.3` mean
  2.3 ns while `` `timescale 1ps/1ps `` makes `#7` mean 7 ps.
- **Gotcha one: file-order dependence.** The directive "is not bound to modules or
  files"; it applies to everything after it until the next one. If some files
  declare a timescale and others do not, reordering the file list changes what a
  delay means in the files that do not — "radically different simulation results,
  even with the same simulator."
- **Gotcha two: no portable default.** Sutherland reports that a compiler reading a
  file with no timescale in effect "might, or might not, apply a default time unit,"
  so the same design behaves differently on different simulators. (His
  characterization; cite him, not the standard.)
- **His fix, two parts.** Old-style: a `` `timescale `` at the top of every file.
  SystemVerilog-style: `timeunit` and `timeprecision` as *keywords inside* a module,
  interface, program or package, local to that scope and therefore immune to file
  order; plus an explicit unit on the delay itself (`#1ms`), which documents intent
  and removes the dependency entirely.

**Corroboration from open simulator documentation** — two simulators giving
different answers to the same missing declaration, which is the whole point:

- Icarus Verilog ships a warning, `-Wtimescale`, for "inconsistent use of the
  timescale directive. It detects if some modules have no timescale, or if modules
  inherit timescale from another file," stating the consequence in Sutherland's own
  terms: both "probably mean that timescales are inconsistent, and simulation timing
  can be confusing and dependent on compilation order." It is included in `-Wall`.
  That a mainstream open simulator ships a dedicated warning is itself evidence the
  mistake is common.
  [Icarus Verilog documentation, accessed 2026-09-08](https://steveicarus.github.io/iverilog/usage/command_line_flags.html)
  **[docs]**
- Verilator instead supplies a default: `--timescale <timeunit>/<timeprecision>`
  "sets default timeunit and timeprecision when `timescale` does not occur before a
  given module," defaulting to **1ps/1ps** to match SystemC. `--timescale-override`
  overrides every timescale in the sources and may set precision alone (`/1fs`); the
  manual notes precision must be consistent with SystemC's
  `sc_set_time_resolution()`, and since 1fs is finest "it may be desirable always to
  use a precision of 1fs."
- Precision is global, which connects back to §3: Cummings and Salz define the
  *global time precision* as the minimum over every precision declared anywhere, and
  `#1step` as exactly that. Consequence worth a sentence: **adding one module with a
  finer precision changes the meaning of `#1step` everywhere.** Timescale is not a
  local decision.

**Why it looks plausible** (my synthesis, not a source claim — see §6): a wrong
timescale produces no error, no X, no missing edge. Every delay in a given file is
scaled by the same wrong factor, so waveforms keep the right shape and take the
wrong duration. It surfaces only where two differently-scaled regions meet — a clock
generator in one file, a model delay from another, a protocol timeout now expiring
1000× too early — and then looks like a functional bug in whichever block sits on
the wrong side of the boundary.

## 6. Commonly repeated but unsourced claims

Widely asserted in practice; **not** supportable from a citable, reachable,
non-standard source. The chapter must not state these as fact.

| Claim | Status |
|---|---|
| Any statement of the form "IEEE 1800 requires X" | Out of bounds by the book's rule. Every behavioral statement above is attributed to a practitioner paper or to simulator docs; where a source describes the standard, I relay the source's description. |
| Delays finer than the declared precision are rounded to the nearest precision unit | Almost certainly true and universally taught, but I found no open source stating the rounding rule. Sutherland 2007 says only that delays are "scaled to the smallest precision used by the design." Either find a source or write "simulators round" without stating a rule. |
| Two-state simulation is "roughly 2× faster" | Contradicted by the only measurement reached: ~6% on a 2.4M-gate model (Cummings & Bening §7). Do not repeat the folklore figure. |
| Program blocks are obsolete because UVM does not use them | UVM's non-use is real; no primary source makes it the *reason*. Cummings' 2016 argument is different (do not drive on the active edge → no race → no program). Attribute to him, not to UVM. |
| `$display` in a clocked block "shows the old value" | True as a consequence of Active-vs-NBA ordering, but ordering *within* Active is explicitly arbitrary. Say "may show" for anything beyond the NBA case. |
| Assertions "cannot" have race conditions | Overstated. Preponed sampling removes the read-write race on sampled values; it does not remove races in assertion *action blocks*, which run in the Reactive region as ordinary procedural code. |
| A clocking block "fixes" testbench timing | Bromley & Johnston's whole paper is the counter-evidence: "surprisingly error-prone," chiefly via clockvar-vs-signal confusion and using `=` where `<=` is required. |
| The X→0 negedge at time zero behaves the same everywhere | It does not: Verilator suppresses it by default; `--x-initial-edge` restores it. |

## 7. Suggested BibTeX keys

| Key | Work |
|---|---|
| `cummings2006events` | Cummings & Salz, "SystemVerilog Event Regions, Race Avoidance & Guidelines," SNUG Boston 2006 (rev. 1.2, 2007) |
| `cummings2016stimulus` | Cummings, "Applying Stimulus & Sampling Outputs — UVM Verification Testing Techniques," SNUG 2016 |
| `bromley2012clocking` | Bromley & Johnston, "Taming Testbench Timing: Time's Up for Clocking Block Confusions," SNUG Austin 2012 |
| `sutherland2013x` | Sutherland, "I'm Still In Love With My X!," DVCon 2013 |
| `piper2012xprop` | Piper & Vimjam, "X-propagation Woes: Masking Bugs at RTL and Unnecessary Debug at the Netlist," DVCon 2012 |
| `cummings2004twostate` | Cummings & Bening, "SystemVerilog 2-State Simulation Performance and Verification Advantages," SNUG Boston 2004 |
| `sutherland2007gotcha` | Sutherland, "Gotcha Again: More Subtleties in the Verilog and SystemVerilog Standards," SNUG San Jose 2007 |
| `verilatormanual` | Verilator user guide (cite page + access date) |
| `iverilogdocs` | Icarus Verilog documentation (ditto) |

Already present: `turpin2003x`. Only if the chapter reaches the underlying papers:
`mills2004assertive`, `bening1999twostate`, `turpin2005sequential`, `cummings2000nba`.

## 8. Confidence notes and gaps

**High confidence — full text read from the PDF in this session:** Cummings & Salz
2006; Cummings 2016; Bromley & Johnston 2012; Sutherland 2013; Sutherland 2007 §8.1;
Cummings & Bening 2004; Piper & Vimjam 2012 (deck). Every figure, guideline number
and section number cited above was read from the document, not recalled. Same for
the Verilator option text and the Icarus `-Wtimescale` description.

**Cited but not read — attribute nothing specific to these:** Mills, "Being
Assertive with Your X," SNUG San Jose 2004; Bening, DAC 1999; Turpin, SNUG Boston
2005; the three SNUG San Jose 2012 X-propagation papers Sutherland cites (Greene
tutorial; Evans, Yam & Forward; Greene, Salz & Booth); Cummings, SNUG San Jose 2000.
All appear in reference lists I read; none were fetched.

**One correction to the brief.** It expected Mills material on xprop. What I found
is that Mills' contribution is the 2004 *assertion-based X-detection* argument,
carried forward by Sutherland 2013 §9 and sourced here to Sutherland. The DVCon 2012
X-propagation paper is by **Piper and Vimjam**, not Mills.

**Gaps.**

1. **No source for the timescale rounding rule** (§6) — the one factual hole in §5.
2. **The `$strobe`/`$display`/`$monitor` table rests on a single source.** Cummings
   & Salz is authoritative and nothing else I reached corroborates it. Unlikely to be
   wrong, but it is one source.
3. **All two-state performance evidence is from 2001–2004** on a commercial simulator
   two decades out of date. For a current number the book could measure its own
   Verilator and Icarus examples — an original contribution rather than a citation.
4. **No post-2013 source on xprop.** Sutherland 2013 is the most recent substantive
   treatment reached; the chapter should not characterize current practice.
5. **Search budget.** This session's web-search allowance was exhausted before the
   task began, so discovery ran on known URLs, Internet Archive capture enumeration
   and reference-list chasing. That biases the note toward the practitioner canon and
   away from anything recent not linked from it. A follow-up pass with search
   available should look for post-2015 material on X-propagation and on whether
   clocking-block guidance has changed.
