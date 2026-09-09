---
title: "Research note: Chapter 4, part 2 — sampling, X, and time"
date: 2026-09-09
author: research-agent
status: draft
feeds: Ch. 4
---

# Chapter 4 research, part 2: sampling, X, and time

**Scope note.** This note covers the testbench/design boundary at a clock edge,
the constructs added to close it, assertion sampling, four-state versus two-state
simulation, and timescale. It deliberately does not re-derive Turpin's "The
Dangers of Living with an X" (2003), which the book already cites as
`turpin2003x`; it picks up the argument after 2003.

*Reachability.* `sunburst-design.com` now redirects to `paradigm-works.com` and
the paper archive there is behind a login, so Clifford Cummings' SNUG papers were
recovered from Internet Archive captures of the original `sunburst-design.com`
URLs; those capture URLs are the ones cited below. `sutherland-hdl.com` still
serves its site but not its paper archive at the historical paths, so Stuart
Sutherland's DVCon paper was taken from the DVCon proceedings mirror instead.
The IEEE 1800 standard itself is **named only** in this note: it is paywalled and
unread, so every statement about language behavior below is sourced to a
practitioner paper or to open simulator documentation, and anything that could
only be supported from the standard is listed in section 6.

---

## 1. The testbench/design boundary at a clock edge

The best worked treatment found is Cummings and Salz, *SystemVerilog Event
Regions, Race Avoidance & Guidelines*, SNUG Boston 2006 (rev. 1.2, December
2007) — 42 pages, co-authored by a Synopsys simulator architect, and the closest
thing to a canonical account outside the standard.
[Cummings & Salz, SNUG Boston, 2006-09-01](https://web.archive.org/web/20240110182353id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

Its framing is the one the chapter should adopt. The paper separates *hardware
races* — intrinsic to the physics, such as the NAND S-R latch whose final state
is unpredictable when both inputs release simultaneously — from *simulation-induced
races*, which it describes as "not intrinsic to the design or its physics, but
... a natural, although undesirable, consequence of the event-driven simulation
algorithm." The mechanism: the simulator processes events one at a time and
therefore serializes activity that is concurrent in hardware. The paper's warning
is the sentence the chapter should build its motivation on — such a race "can
cause the simulator to simulate a faulty design when in fact the design is
correct, or more dangerously, simulate a seemingly correct design when in fact
the design is flawed." Cummings and Salz add that the language deliberately
leaves the order within an event region arbitrary, but that every implementation
in fact exhibits *some* fixed order; this is why a race can be invisible on one
simulator and fatal on the next. (§2.1.)

- **Terminology.** *Simulation time* is the time value the simulator maintains;
  a *time slot* holds all activity processed at one simulation time, and may
  require several iterations through the regions without time advancing. Note for
  the chapter: the earlier term *timestep* was dropped during the 2008 revision.
  (§2.)
- **Region structure.** The paper counts 17 ordered regions per time slot in the
  2005 revision, of which nine execute language statements and eight execute PLI
  code. The nine are: Preponed; the *Active region set* (Active, Inactive, NBA);
  Observed; the *Reactive region set* (Reactive, Re-Inactive, Re-NBA); and
  Postponed. Cummings and Salz group them by intent, which is the framing the
  chapter wants: Active-set regions implement RTL, Preponed/Reactive/Postponed
  implement verification, and Preponed/Observed/Reactive implement assertion
  checking. They recommend avoiding the Inactive region entirely — `#0`
  procedural assignments in RTL are a symptom of a race being papered over rather
  than fixed. (§2.2, §2.2.4.)
- **The read-write race concretely.** A design's clocked logic uses nonblocking
  assignments and therefore updates in the NBA region; a testbench written as
  module code that reads those signals in the Active region of the same edge sees
  the *old* value, while one that reads after the NBA update sees the new one, and
  nothing in the language fixes which happens if both are in the Active region.
  Cummings' older nonblocking-assignment guidelines — cited in the 2006 paper as
  removing "90-100%" of induced races on RTL — are the design-side half of the
  fix: clocked logic in nonblocking assignments, combinational logic in blocking
  assignments, and never two `always` blocks assigning one variable.
  [Cummings, SNUG San Jose, 2000-03-01](https://web.archive.org/web/2020/http://www.sunburst-design.com/papers/CummingsSNUG2000SJ_NBA.pdf)
  **[primary]** (URL recorded from the 2006 paper's reference list; see §8 for its
  verification status.)
- **The pre-SystemVerilog workarounds, and why they were bad.** §6.1 is directly
  usable. Applying stimulus *on* the active edge required driving every input with
  a nonblocking assignment, which mimics a zero-delay register transfer from
  testbench to design — and then breaks on a gate-level netlist with real hold
  times, because all inputs change in zero time. Engineers reached for
  `<= #1` right-hand-side delays to fix that, which Cummings had already shown to
  be "a potential source for serious simulator performance degradation." The
  Sunburst house style instead applied stimulus on the *inactive* edge, far from
  setup and hold windows, which lets the same testbench drive RTL and a
  back-annotated netlist unchanged. This is the practical argument for why a
  driver and a monitor should not both live on the same edge.

## 2. Clocking blocks and program blocks: the problem they solve

**Why skews exist at all.** The clearest published statement of the underlying
motivation is Bromley and Johnston, *Taming Testbench Timing: Time's Up for
Clocking Block Confusions*, SNUG Austin 2012 (Verilab), §2: a synchronous
testbench must "sample signals one setup time before the clock event" and
"update signals one clock-to-output delay after the clock event," because that is
what the DUT's own flip-flops do. Input skew is the testbench's t<sub>SU</sub>;
output skew is its t<sub>CO</sub>. Their §2 heading "A Clocking Block Is Not A
Time Machine" is the pitfall in one line: at a clock edge a testbench can see
current and past values but never future ones, and can schedule future drives but
never alter the past. They also note the construct "has proved to be surprisingly
error-prone, despite nearly a decade of application experience."
[Bromley & Johnston, SNUG Austin, 2012-09-01](https://web.archive.org/web/2020id_/http://www.verilab.com/files/paper51_taming_tb_timing_FINAL_fixes.pdf)
**[primary]** (recovered from an Internet Archive capture of `verilab.com`; the
paper is no longer listed on Verilab's current papers page.)

Their eleven guidelines are the most citable practical distillation found. The
four that matter most to Chapter 4: access only the clockvars, never the raw
signal (#1); synchronize on the clocking block's own event, not the raw clock
(#2); drive output clockvars with `<=`, never `=` (#3); and **use `input #1step`
unless you have a special reason not to, because it guarantees the testbench sees
sampled values consistent with what SystemVerilog assertions see** (#4). Guideline
#4 is the direct citation for the Chapter 4 → Chapter 9 link. Also useful:
guideline #5 recommends non-zero output skew so waveforms are readable and gate-level
clock-network delay does not bite, and #9-#11 put the clocking block in an
interface reached through a virtual interface modport — the UVM-shaped pattern.

**Clocking blocks.** Cummings and Salz describe the construct as a way to state
sampling and driving timing once, declaratively, instead of scattering delays
through the stimulus code (§5, §6.2). The load-bearing facts for the chapter:

- Signals get clocking-block timing **only when referenced through the clocking
  block's name**; the bare signal name still refers to the raw, untimed signal.
  Mixing the two accidentally is the failure mode, and the paper recommends
  interfaces with modports as the structural guard against it (§5, §5.2.1).
- Default skews: input skew defaults to one step (see §3 below) and output skew
  to zero — inputs are therefore sampled at the steady-state value immediately
  *before* the clock event, outputs driven *at* it (§2.2.13). A `default output
  negedge` clocking block drives stimulus on the opposite edge, implementing the
  inactive-edge methodology declaratively (§6.2, Example 16).
- The `##` cycle-delay notation is defined against the clocking block's event, so
  `##1` in a block clocked on `@(posedge clk)` is equivalent to waiting for that
  edge (§5.1, Example 12/13). Worked example 12 in the paper traces a program
  block that mixes a plain assignment to a signal with `##1 cb1.d <= ...` through
  an `output #2 d` skew, and its event-by-event figures (Figures 12-18) show the
  assignment landing 2 ns after each posedge. This is the cleanest published
  demonstration of "the skew is the point" and is worth citing even though the
  chapter will not reproduce it.
- Cummings and Salz explicitly answer the performance objection: driving on the
  inactive edge does not cost extra events, because the combinational logic must
  ripple to quiescence either way — it merely does so between clock edges rather
  than before one (§6.2).

**Program blocks.** The paper's own account of the intent (§2.2.7-2.2.8) is that
the Reactive region set is the "dual" of the Active region set, one time slot
later in the ordering, and that program code scheduled there has access to three
things a module-based testbench does not: the steady-state values at the start of
the slot, the settled values after clock and signal propagation, and the
disposition of every concurrent assertion that triggered in the slot. Cummings
and Salz recommend putting testbench code in programs "to isolate RTL design code
execution from testbench code execution." They also note a legitimate use for
`#0` in the Re-Inactive region that they reject in RTL: letting `fork ... join_none`
subprocesses start before the parent continues (Example 1).

**The disagreement — and it is unusually well documented, because it is Cummings
against himself.** Ten years later, in *Applying Stimulus & Sampling Outputs —
UVM Verification Testing Techniques*, SNUG 2016, he reverses.
[Cummings, SNUG, 2016-09-01](https://web.archive.org/web/2023id_/http://www.sunburst-design.com/papers/CummingsSNUG2016AUS_VerificationTimingTesting.pdf)
**[primary]**

His 2016 argument (§10, §10.1) runs: the program block "essentially made it
possible to drive stimulus on the active clock edge and avoid RTL-stimulus race
conditions," but stimulus should not be driven on the active clock edge in the
first place — and "as long as the verification engineer does not drive stimulus on
the active clock edge, there is no RTL-stimulus race condition and a program is
not needed." He adds a list of restrictions he considers gratuitous (a program may
contain `initial` but not `always` procedures; a program may hierarchically
reference module signals but not the reverse; a program may call module tasks and
functions but not the reverse; simulators have not consistently checked and
executed program code), and concludes "The SystemVerilog program statement should
just die and never be used in your code!"

The §10.1 passage titled "Cliff's confession" is the piece worth citing, because
it records the committee's reasoning as well as his own: he voted to keep programs
in the 2015 revision after advocates argued that programs would let engineers
write race-free stimulus *without* having to understand his drive-off-the-active-edge
technique; he says he now regrets the vote and would remove programs if backward
compatibility allowed. Two defensible positions are therefore on the record from
the same author — programs as a guard rail for engineers who have not internalized
the timing discipline, versus programs as unnecessary once that discipline is in
place. The chapter should present both and not adjudicate.

Corroborating context, not a second opinion: the 2006 paper itself flags in §1.2
that "there are some ambiguities that are currently being clarified by the IEEE
SystemVerilog committee" and that those clarifications "might change some of the
restrictions of programs, clocking blocks, event regions" — the authors treated the
rules as unsettled even then. Bromley and Johnston's 2012 guidelines make no use of
program blocks at all, putting the clocking block in an interface instead. That is
suggestive but is *not* a stated position against programs, and the chapter should
not report it as one.

## 3. Assertion sampling

This is the fact Chapter 9 depends on, so it is worth stating precisely and
sourcing carefully.

Cummings and Salz (§2.2.1, §2.2.6, §2.2.13) describe the mechanism as follows.
Values used by concurrent assertions are sampled in the **Preponed** region — the
first region of a time slot, executed once, immediately after simulation time
advances, with no feedback path back into it — and the assertions themselves are
*evaluated* later, in the **Observed** region, after the design's Active-set
activity has settled. An assertion therefore reads the value that was stable
*before* the edge, not the value the edge produced. That is exactly why an
assertion is immune to the read-write race described in §1: the race is a question
of Active-versus-NBA ordering, and the assertion is not reading in either region.

Three refinements the chapter should keep straight:

- **Preponed versus the previous Postponed.** Cummings and Salz argue the
  distinction is unobservable: both regions are read-only, so signal values in a
  contiguous Postponed-Preponed pair are identical and only the timestamp differs.
  Their words: "it is not observable in which region the simulator actually
  samples a value." A simulator may implement either. The chapter should not
  claim a simulator "must" sample in Preponed.
- **The implementation picture.** The paper's mental model (Figure 7) is that the
  simulator keeps two values per sampled signal — its current value and its
  Preponed value — and the sampling construct reads the second when the clocking
  expression fires. Sampling need not happen in every time slot, only in slots
  where the clocking expression triggers, and the simulator does not need to
  predict that in advance. Cummings and Salz describe this as behaving like an
  intra-time-slot delay gate whose delay can be varied to sample an arbitrary
  distance before the clocking event — which is the general mechanism that input
  skew is a special case of.
- **Assertions are monitors, not drivers.** Concurrent assertions cannot modify
  design state; a pass or fail action block is scheduled into the *Reactive*
  region, not Observed (§2.2.6). Useful for the chapter's framing of assertions as
  passive.
- **`#1step`.** The default clocking-block input skew is one *step*, where a step
  is the global time precision — the smallest precision declared anywhere in the
  design (§2.2.13, and see §5 below). Cummings and Salz's summary is that "all
  values used by assertions, whether sampled with clocking block timing or
  without ... occur at `#1step` before the current time slot", and that because
  nothing can happen between one step and the edge, this is indistinguishable from
  sampling in Preponed. Worth stating in the chapter because it explains *why* the
  default skew is a step rather than a real delay: it is the largest skew that
  provably cannot skip an event.

**`$strobe` versus `$display` versus `$monitor`** (§2.2.3, §2.2.11):

| Task | Region | What it therefore shows |
|---|---|---|
| `$display` | Active | the value at the moment the statement executes — before NBA updates land |
| `$strobe` | Postponed | the final settled value for the time slot |
| `$monitor` | Postponed | same, re-triggered on any change in its argument list |

Cummings and Salz note there is no feedback path out of Postponed, so values
printed there are final for the slot, and that this matches the behavior of the
older Verilog Monitor region. They also record that Postponed is where
strobe-sampled functional coverage is collected. This table is the single most
directly usable finding in the note: a `$display` in a clocked `always` block
printing "stale" values is the classic first encounter with the scheduler, and
`$strobe` is the one-line fix.
