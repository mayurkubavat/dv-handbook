---
title: "Research note: Chapter 4 — Simulation Fundamentals"
date: 2026-09-09
author: research-agent
status: complete
feeds: Ch. 4
---

# Chapter 4 — Simulation Fundamentals: evidence note

Scope: what a simulator does with a design and a testbench. The event queue and
the simulation timestep, the scheduling regions and the iteration within one
timestep, races and the assignment guidelines derived from the regions, the
testbench/design boundary at a clock edge, four-state and two-state semantics,
time and timescale, and how far two real open simulators implement the model.

Gathered in three independent passes and kept in three parts. **Section numbers
are local to their part**: "§2.3" inside Part A means Part A's §2.3. Each part
carries its own unsourced-claims table, BibTeX suggestions and confidence notes.

## Which part feeds which chapter section

| Chapter topic | Part | Sections |
|---|---|---|
| The event queue and the timestep | A | §1 |
| The scheduling regions | A | §2 |
| Iteration within a timestep | A | §3 |
| Races, and the guidelines derived from the regions | A | §4 |
| The testbench/design boundary at a clock edge | B | §1 |
| Clocking blocks and program blocks | B | §2 |
| Assertion sampling | B | §3 |
| Four-state and two-state | B | §4 |
| Time, timescale and precision | B | §5 |
| What a real simulator implements | C | §1, §2 |
| Why two simulators may disagree | C | §3 |

## The two questions that decided the chapter, both answered

**Can the scheduling model be taught without quoting the standard? Yes.**
Cummings and Salz, "SystemVerilog Event Regions, Race Avoidance & Guidelines",
was retrieved in full from an Internet Archive capture of the now login-walled
original. It gives the timestep, the regions one section each, a race taxonomy
and the guidelines with their rationale, as its own exposition rather than as
paraphrase of clause text.

**Cite revision 1.2, and mind the date.** Revision 1.0 describes eight regions;
revision 1.2 describes nine, after Re-NBA was added and the Reactive set
formally defined. Revision 1.2 is the one to cite, and every page of it still
carries the "SNUG Boston 2006" venue although its content is from late 2007, so
the citation needs the revision as well as the venue or a reader counting
regions will find a different number.

**May two conforming simulators disagree on the same source? Yes, and the tool
authors say so themselves.** Verilator documents that its identity comparisons
"may make the expression yield a different result than a four-state simulator",
and that it "simulates events as Synopsys's Design Compiler would" where "a
compliant simulator will only calculate y if x changes". Icarus documents that
it "slightly modifies time 0 scheduling". Two tools, two documented departures,
one source file. See Part C §3.

## What the chapter must not assert

1. **No IEEE 1800 clause text, quoted or paraphrased, and never "the standard
   requires...".** Say "SystemVerilog schedules..." and attribute the account to
   Cummings and Salz. **Beware the second-hand trap**: the paper itself quotes
   the standard and a draft of it in several places, including its definition of
   *simulation time*, so paraphrasing those passages would reproduce clause text
   at one remove. Paraphrase only the authors' own exposition. Their definition
   of *timestep* is their own and is safe.
2. **"Delta cycle" is used in this literature but not established by it.**
   Cummings and Salz say "iterations" through the regions throughout, and use
   "delta-cycle" once, naturally and without ever defining it. So the concept is
   fully sourced and the name is not: teach iteration within a timestep, and
   mention the borrowed term once so a reader meeting it elsewhere is not lost.
   Do not present it as this language's defined vocabulary. The design doc's own
   chapter line used it and is corrected.
3. **Verilator is not a cycle-based simulator.** It schedules statically at
   compile time and implements the Active and NBA regions, iterating to
   convergence; `--timing` adds coroutine suspension for delays and event
   controls but leaves ordinary clocked blocks statically scheduled.
4. **No speed ratio for compiled versus event-driven simulation.** The only
   figures found are project self-claims with no methodology.
5. **No claim that two-state simulation is much faster.** The one measurement
   reached puts it near six percent on a multi-million-gate model, which is the
   opposite of the folklore and is worth saying.
6. **Do not say Verilator's two-state nature makes it useless for reset bugs.**
   Its documentation claims randomized initialization finds many a four-state
   simulator misses. What it cannot do is propagate X or compare against it.
7. **"Icarus Verilog supports SystemVerilog" is overstated**; its README says
   the unsupported list is too large to enumerate.
8. **Three mechanisms make two simulators disagree, and the sources separate
   them, so the chapter must too.** Permitted ordering freedom, which is a real
   race and the only one the guidelines protect against: a region's events may be
   processed in arbitrary order, and scheduling freedom lets tools optimize the
   order of concurrent events differently. Implementation and ambiguity
   divergence, which the same source is explicit is *not* a defect in the
   language. And plain non-compliance. **The inference to block is the inverse
   one**: two simulators disagreeing does not prove a race, and the chapter's
   worked example must not be read that way.
9. **Cummings' race-removal figure is his estimate, not a measurement**, and
   guideline 5 is a corollary of guidelines 1 and 3 rather than something a
   source derives from a region.
10. **No rounding rule for delays finer than the declared precision.** No open
    source states one; say that simulators round, without a rule.
11. **Do not say a simulator "must" sample in the Preponed region.** The source
    is explicit that Preponed and the previous timestep's Postponed are
    indistinguishable: same values, different timestamp.
12. **Do not say assertions "cannot" race.** Preponed sampling removes the
    read-write race on *sampled values* only; an assertion's action block runs in
    the Reactive region as ordinary procedural code and races like any other.
13. **Do not say a clocking block "fixes" testbench timing.** The one paper
    devoted to using them calls them "surprisingly error-prone", mostly through
    confusing a clocking variable with the signal and through using the wrong
    assignment operator.
14. **Program blocks are not obsolete because UVM does not use them.** That
    non-use is real but no source makes it the reason; the argument on record is
    a different one, about not driving on the active edge.



# Part A — The scheduling model

Scope: the SystemVerilog simulation cycle, the ordered event regions, delta
cycles, the race conditions the regions exist to prevent, and the derivation of
the standard assignment guidelines from the region ordering. Historical
grounding for the event-driven algorithm is covered briefly in §5.

**What was reachable.** The primary source this chapter depends on was
recovered in full: the 40-page Cummings and Salz SNUG Boston 2006 paper, via
the Internet Archive's capture of the original `sunburst-design.com` URL. Two
companion Cummings papers (the 2000 non-blocking-assignment paper already in
`refs.bib` as `cummings2000nba`, and the 2002 paper on non-blocking assignments
with delays) were reachable by the same route. Open simulator documentation
(Verilator, Icarus Verilog) was reachable.

**What was not reachable.** The live `sunburst-design.com` host now redirects to
`paradigm-works.com` and puts its PDF library behind a login, so all Sunburst
citations below resolve through `web.archive.org`; the note gives both the
canonical URL and the archive URL. IEEE 1800 itself is paywalled and, per this
book's standing rule, is named but never quoted or paraphrased. Verilator and
cocotb documentation pages were attempted for §3 and returned 404 at the URLs
tried; §3 is therefore sourced from the Cummings and Salz account of region
iteration rather than from simulator documentation, and §6 flags the one term
this leaves unsourced.

### 0. Can this chapter be sourced without the standard?

**Yes.** This was the first question settled, and the answer is unambiguous.

The paper exists, its bibliographic details are confirmed from the document
itself, and the full text was retrieved:

> Clifford E. Cummings (Sunburst Design, Inc.) and Arturo Salz (Synopsys),
> "SystemVerilog Event Regions, Race Avoidance & Guidelines", SNUG Boston 2006,
> Rev 1.0, 40 pages.

- Canonical URL (now login-walled):
  `http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf`
- Retrieved from: [Cummings and Salz, 2006-11-11](https://web.archive.org/web/20061111005225id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
  **[primary]** (the timestamp is the Archive's first capture; the paper is
  dated by its venue, SNUG Boston 2006)

The paper is exactly the secondary route the chapter needs. It is written by a
member of the community that produced the language — Salz was at Synopsys and
the paper itself describes the standard's committee structure — and it covers,
in the book's required territory: the definition of simulation time and
timestep, the Verilog-2001 four-region model, the eight SystemVerilog statement
regions with a section per region, a taxonomy of races, the eight race-avoidance
guidelines with their rationale, `#1step` semantics, clocking-block timing, and
when to apply stimulus. Its own §2.1 and §2.2 are self-contained expositions,
not paraphrases of clause text.

**Consequence for the chapter: it can be written as planned.** Every claim in
§§1–4 below carries a non-standard citation. The standard is named twice in the
chapter's likely prose — once to say the regions are normatively defined there,
once for the Re-NBA gap — and quoted nowhere.

One caveat that shapes the citation, not the plan. The paper exists in two
materially different revisions: the original 2006 text describes **eight**
regions, and a later revision describes **nine**, adding Re-NBA. **Cite the
later revision** — §2.4 gives both URLs, the reason for the change, and the
dating trap to avoid.

**Sutherland was checked as an alternative route and is not one for the
regions.** Because `sutherland-hdl.com` hosts its papers openly, its index was
reviewed in full: **no Sutherland paper covers event scheduling, event regions
or the stratified event queue as a primary topic.** Cummings and Salz remain the
chapter's single citable route for the region model, and nothing rests on a
preference between authors — the Cummings paper was recovered in full, so no
substitute was needed.

Two Sutherland, Mills and Spear papers *are* openly hosted, were retrieved in
full, and are valuable as **independent corroboration on specific points** —
notably the permitted-nondeterminism question (§4.1), the zero-delay lock-up
(§3), time-zero ordering (§4.2), and a useful counterpoint on `#0` (§4.4):

- "Standard Gotchas: Subtleties in Verilog and SystemVerilog," SNUG Boston 2006,
  59 pp. [Sutherland, Mills and Spear, 2006](http://sutherland-hdl.com/papers/2006-SNUG-Boston_standard_gotchas_paper.pdf)
  **[primary]**
- "More Standard Gotchas: Subtleties in Verilog and SystemVerilog," SNUG San
  Jose 2007, 44 pp. [Sutherland, Mills and Spear, 2007](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf)
  **[primary]**

### 1. The simulation cycle and the event queue

**Simulation time and the timestep.** Cummings and Salz define *simulation time*
as the time value the simulator maintains to model the time the circuit being
simulated would actually take, and they attribute that definition to the Verilog
standards lineage rather than coining it. On top of it they define a *timestep*
as the simulation time at which simulation activity is processed, and state the
rule that makes the whole model work: all activity for a given simulation time
executes until no further activity remains for that timestep, *without advancing
simulation time*. They add the point the chapter most needs — executing the
events within one timestep may require **multiple iterations** through the event
regions of that same timestep. They also note that IEEE 1800 sometimes calls a
timestep a *time slot*, which is useful for the chapter because it lets the book
use one term while acknowledging the other.
[Cummings and Salz, 2006, §2](https://web.archive.org/web/20061111005225id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

This gives the chapter its central claim in a sourceable form: **time is not a
loop counter.** The simulator advances to the next time at which something is
scheduled, drains everything scheduled there — including work that scheduling
itself creates — and only then moves on. Nothing forces the clock forward; the
emptiness of the current time does.

**The predecessor model.** IEEE 1364-2001 divided Verilog's event regions into
four ordered regions: Active, Inactive, Nonblocking Assign Update, and Monitor.
The 2001 standard also defined *Future* Inactive and *Future* Nonblocking
Assignment Update events, which Cummings and Salz describe as nothing more than
Inactive and NBA regions pre-built for a later timestep.
[Cummings and Salz, 2006, §2](https://web.archive.org/web/20061111005225id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**
This is a good pedagogical on-ramp: four regions are teachable in a paragraph,
and the SystemVerilog set is then motivated as *additions with a purpose* rather
than as a list to memorize.

**Why the additional regions exist.** The paper is explicit that the new regions
were added to support constructs that would otherwise have created new
simulation-induced races between the design and the verification code, and that
the assertion regions make race-free assertion-based verification possible. Two
FAQ answers pre-empt the reader's obvious objections: the new regions do **not**
make simulation slower (the events were already being scheduled; the standard
merely described where), and the model stays backward compatible with
Verilog-2001 but for one deliberate exception.
[Cummings and Salz, Rev 1.2, §§1–2.2](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

**That one incompatibility** is a cheap, concrete illustration of the chapter's
thesis that scheduling rules are race policy. In Verilog-2001 a variable
initialized at its declaration was scheduled as if assigned in an `initial`
block, in nondeterministic order, and so *caused a time-0 event* — a standing
source of time-0 races, since nothing ordered variable initialization against
`always` blocks, `initial` blocks and continuous assignments. In SystemVerilog
such variables are initialized *before* time 0 and cause no time-0 event.
[Cummings and Salz, Rev 1.2, FAQ #4](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

### 2. The scheduling regions

**Cite Rev 1.2 of the paper, not Rev 1.0.** See §2.4 — the later revision covers
all nine regions and supersedes the original on this point. Both are cited below
where the distinction matters; where it does not, Rev 1.2 is the citation to
use.

Cummings and Salz group the regions by *purpose*, and the chapter should adopt
this grouping rather than presenting a flat ordered list, because it is what
makes the set memorable:

- **RTL functionality:** the Active region set — Active, Inactive, NBA — while
  avoiding Inactive events.
- **Verification execution:** Preponed, the Reactive region set (Reactive,
  Re-Inactive, Re-NBA), and Postponed.
- **Concurrent assertion checking:** Preponed, Observed, Reactive.
- **A region to avoid:** Inactive.

[Cummings and Salz, Rev 1.2, 2007-12](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

The structural insight the chapter should lead with is the authors' own: the
**Reactive region set is the testbench dual of the Active region set.** Reactive
is the dual of Active, Re-Inactive of Inactive, Re-NBA of NBA. Three regions for
the design, then assertions, then the same three regions again for the
testbench, then the strobe. That symmetry turns nine names into one idea, and
the authors state it in exactly those terms.
[Cummings and Salz, Rev 1.2, §§2.2.7–2.2.10 and §10.1](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

#### 2.1 What executes where

All of the following is from Cummings and Salz Rev 1.2, §§2.2.1–2.2.11,
[same URL](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf),
**[primary]**.

**Preponed.** Samples the values concurrent assertions will use. Runs **once per
time slot**, immediately after time advances, with no feedback path into itself.
Two useful details: because Preponed and the previous slot's Postponed are both
read-only, the sampled values are identical in either, so which one the
simulator really used is not observable — only the simulation time differs. And
the simulator needs no knowledge of the future: it can keep two values per
signal, current and Preponed, and hand over the Preponed one when the clocking
expression eventually triggers. The paper draws this as a delay element inside
the slot (Figure 7 — *describe, do not reproduce*).

**Active.** Evaluates and executes current module activity in **arbitrary
order** among these categories (statements between `begin`/`end` still run in
written order): module blocking assignments; evaluation of the *right-hand side*
of non-blocking assignments, scheduling the update into NBA; continuous
assignments; evaluation of inputs and update of outputs of primitives; and
`$display` and `$finish`.

**Inactive.** Where `#0` blocking assignments are scheduled. The authors
recommend against using it in RTL at all and omit it from the paper's later
scheduling diagrams, since well-written code never populates it. Their footnote
gives the reason it exists, worth a sentence in the chapter: Inactive was needed
in early Verilog *before the NBA region was added* (they date that to circa
1989), and proper use of NBA makes it unnecessary.

**NBA.** Executes updates to the left-hand-side variables whose right-hand sides
were evaluated in Active. Second role, needed for §4: the verification regions
also schedule stimulus into NBA, so it runs again later in the same slot, after
the first NBA pass has already updated the design's sequential state.

**Observed.** Evaluates the concurrent assertions on the Preponed values.
Assertion pass/fail action blocks do **not** run here — they schedule a process
into Reactive — because concurrent assertions are designed to be strictly
monitors and may not modify design state. The Observed-to-Active feedback path
exists for an `expect` statement at module scope (an `expect` inside a program
schedules into Reactive instead); the authors call this rare and know of no
methodology that puts such statements in a module.

**The Reactive region set (Reactive, Re-Inactive, Re-NBA).** Its stated purpose
is to schedule testbench stimulus drivers and checking *in the same time slot,
after the RTL has settled to a semi-steady state* — while allowing that the
stimulus may itself cause further combinational activity in that slot. It
schedules the blocking, `#0` blocking and non-blocking assignments in program
code, plus any task or function called from a program. The authors note
testbench code can be (and historically was) written as module code, but
encourage programs so the design is isolated from testbench execution.

- **Reactive** — dual of Active. Executes current *program* activity in any
  order: program blocking assignments; **the pass/fail code from concurrent
  assertions**; evaluation of the right-hand side of program non-blocking
  assignments, scheduling updates into **Re-NBA**; program continuous
  assignments; `$exit`. The authors' justification for placing verification late
  in the slot is the clearest available: a process here sees three things at
  once — the steady-state Active-set values from the *start* of the slot, the
  *next* steady-state values after clock and signal propagation, and the
  disposition of every concurrent assertion triggered in that slot.
- **Re-Inactive** — dual of Inactive, reached by a `#0` in a program process.
  The authors are careful here and the chapter should be too: this is the dual
  of the region they recommend avoiding, **but that recommendation does not
  extend to verification code**, where a `#0` is often useful and harmless for
  adding determinism. Their example is `fork ... join_none` followed by `#0`, so
  the children start before the parent continues. (Describe; write your own.)
- **Re-NBA** — dual of NBA. Executes updates to left-hand-side variables whose
  right-hand sides were evaluated in Reactive.

The three iterate together until all Reactive-set events are done. *Then*, if
program execution scheduled anything that can trigger Active-set events in the
same slot, the Active set re-triggers and iterates until it too completes. One
detail worth a sentence: on that second entry the Active and Inactive regions
are typically empty and the work is in NBA, and a second NBA pass can trigger
further combinational activity — but only if the testbench drives with zero
delay, which is why some engineers deliberately drive away from the clock edge.

**Isolation — why a program block cannot race the design.** This is the
load-bearing claim for §4. Program processes may modify design signals only via
non-blocking assignments, whose updates land in a later region. Assignments to
*program* variables are blocking and take effect immediately during
Reactive/Re-Inactive, but because they touch only program variables they
schedule nothing in Active. Add the rule that all program processes complete
before the Active set is re-entered, and the testbench cannot interleave with
the design.

**Postponed.** Executes `$strobe` and `$monitor`, showing the final updated
values for the timestep, and collects functional coverage that uses strobe
sampling. There is **no feedback path** from Postponed back into the RTL or
Reactive regions, which is precisely why the values it reports are final. The
paper notes this is generally the behavior of the Monitor region of IEEE
1364-2001 — a clean way for the chapter to connect old and new.

#### 2.2 `$strobe` versus `$display` (part of item C)

This falls straight out of the above and needs no extra source: `$display`
executes in **Active**, alongside blocking assignments and *before* the NBA
updates for that timestep; `$strobe` and `$monitor` execute in **Postponed**,
after everything else, with no path back. So `$display` in a clocked block shows
a variable's value *before* the non-blocking updates land, while `$strobe` shows
the settled end-of-timestep value. Both facts are in Cummings and Salz §2.2.2
and §2.2.8. This is the single cheapest demonstration in the chapter that
regions are observable behavior and not bookkeeping trivia, and it makes an
excellent worked example: one `always @(posedge clk)` block, one `$display` and
one `$strobe` on the same variable, printing different values.

#### 2.3 A naming aside worth one footnote

"Prepone" is a real word meaning to schedule for an earlier time, in common use
in South Asia; the committee groaned but accepted no alternative. The authors'
mnemonic is genuinely useful: Preponed and Postponed are the begin/end regions
bracketing each time slot.
[Cummings and Salz, Rev 1.2, §2.2.12](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

#### 2.4 Which revision to cite, and why it matters

There are **two substantively different revisions of the same paper** in the
Internet Archive, and citing the wrong one would put an error in the book.
**Rev 1.0** (SNUG Boston 2006, 40 pp.,
[captured 2006-11-11](https://web.archive.org/web/20061111005225id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf))
describes **eight** regions, with no Re-NBA and Re-Inactive iterating directly
with Reactive. **Rev 1.2** (42 pp.,
[captured 2009-04-19](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf))
describes **nine**, adding Re-NBA and formalizing the two *region sets*.

The paper documents its own change, which makes this citable rather than
guesswork: its revision history records that in **April 2007** the SystemVerilog
Standards Group updated the event regions and clocking-block behavior under
**Mantis item 890**, that Mantis 890 added Re-NBA and formally defined the
Reactive region set as the testbench dual of the Active region set, and that
these were folded into Rev 1.1 (November 2007) and Rev 1.2 (December 2007).
[Cummings and Salz, Rev 1.2, §10.1](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

**Recommendation: cite Rev 1.2 throughout and teach nine regions.** Rev 1.0 is
worth one footnote — a paper revised because the language changed under it is an
honest illustration that the scheduling model is a committee artifact with a
history, not a law of nature. Dating trap: Rev 1.2 carries the SNUG Boston 2006
venue on every page but its content is from December 2007 (see the §7 note
field). Do not date the nine-region model to 2006.

### 3. Delta cycles

**Terminology warning, and it matters for the chapter.** Cummings and Salz do
**not** use the term "delta cycle." Across both revisions the phrase appears
once, in passing, in an aside about non-unit step delays. The concept the
chapter wants is real and well sourced in their text; the *name* is not theirs.
"Delta cycle" is a VHDL term of art that Verilog practitioners borrowed. See §6
— the chapter should either introduce the term explicitly as borrowed, or use
the sourced vocabulary below.

**The sourced version of the concept.** Cummings and Salz state that executing
the events in a time slot may require **multiple iterations through the event
regions of that same slot**, and their region descriptions give the structure:

1. The **Active region set** iterates internally — Active drains, Inactive
   promotes into it, NBA updates land, and those updates can retrigger Active
   work — until nothing is left in the set.
2. **Observed** evaluates assertions on the Preponed values.
3. The **Reactive region set** iterates the same way until all its events
   are done.
4. If the Reactive set scheduled anything that can trigger Active-set events,
   **the Active set re-triggers and iterates again**, in the same slot.
5. Only when nothing remains anywhere does Postponed run and time advance.

[Cummings and Salz, Rev 1.2, §2 and §§2.2.2–2.2.11](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

One pass through that loop — evaluate, update, find the update woke something
else, go round again, all at the same simulation time — is what the chapter
means by a delta cycle. It is *not* a unit of time: two events in different
delta cycles at one timestep are ordered relative to each other yet simultaneous
as far as `$time` is concerned. That is the most useful thing to teach here,
since it explains both the waveform viewer's two "simultaneous" values and the
`$display`/`$strobe` disagreement (§2.2).

**How a design loops forever without advancing time.** If the work done in one
iteration always schedules more work *in the same slot*, the simulator never
reaches the condition — no events remain — that lets time advance. It is not
hung in the operating-system sense; it is making progress through delta cycles
forever. The best sourced entry point is Cummings on self-triggering `always`
blocks: a blocking assignment evaluates its right-hand side and updates its
left-hand side without interruption, so it completes before the `@(clk)` trigger
event could be scheduled, and an oscillator written with blocking assignments
therefore cannot trigger itself — whereas the non-blocking version *can*,
because the update is deferred to a later region and is still pending when the
sensitivity is evaluated.
[Cummings, 2000, §7](https://web.archive.org/web/20061111004954id_/http://www.sunburst-design.com/papers/CummingsSNUG2000SJ_NBA.pdf)
**[primary]**

That makes an unusually good worked example: a two-line clock oscillator whose
behavior — dead, or a zero-delay infinite loop — flips entirely on `=` versus
`<=`, with the region model as the only explanation.

**Independently corroborated, with the reader's symptom named.** Sutherland,
Mills and Spear document this as a gotcha phrased exactly as a user would report
it — RTL simulation locks up and time stops advancing — and give the mechanism
for a *different* and simpler case than Cummings': a non-blocking assignment in
a **combinational** block, where the block returns to its sensitivity list
without blocking, the deferred update then lands and retriggers that same
sensitivity list, and so long as the value keeps changing the simulator stays
locked in the current simulation time. They note there are really two faults
here — the lock-up, and the fact that the model describes combinational logic
with a zero-delay feedback path, which would be unstable in gates — and that
Verilog permits it deliberately, on the philosophy that engineers should be able
to model hardware that does not work in order to analyze it.
[Sutherland, Mills and Spear, 2007, §2.4](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf)
**[primary]**

This is the better example for the chapter: it is two lines, the symptom is
stated in the reader's own words, and the fix (a clock edge in the sensitivity
list, or `always_ff`) is given by the source. It also upgrades §8 item 3 from
"mechanism sourced, behavior not" to sourced on both counts — though the example
should still be **built and run** under `examples/` so the chapter reports real
output rather than predicted output.

### 4. Races, and the guidelines derived from the regions

#### 4.1 What a race is, and the two kinds

Cummings and Salz define a race condition as a flaw characterized by an output
that shows an unexpected dependence on the relative timing or ordering of
events, and note the term comes from the image of two signals racing to
influence an output first. They then draw the distinction the chapter needs:

- **Hardware races** are intrinsic to the physics — finite gate delays mean an
  output may transiently take an unwanted value before settling; usually
  harmless except on a clock or asynchronous reset. Their example is the NAND
  S-R latch: drive both inputs to 0, both outputs go to 1, overriding the
  latching action; on release, whichever input stays at 1 longer wins, and if
  both release simultaneously the final state is unpredictable.
- **Simulation-induced races** are *not* intrinsic to the design. The simulator
  processes events one at a time and so unavoidably serializes events in the
  same time slot, turning concurrent hardware activity into an ordered sequence.

[Cummings and Salz, Rev 1.2, §2.1](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

Two points from that section should shape the chapter's framing. The danger is
**asymmetric**: such a race can make the simulator show a fault in a correct
design, or — more dangerously, in the authors' words — show a correct result for
a design that is actually flawed. And the language leaves ordering arbitrary
*on purpose*: because code unwittingly comes to rely on a particular order,
Verilog specifies that a region is processed in **arbitrary** order while every
real implementation exhibits *some* definite order. That is the sharpest
available statement of why "it works on my simulator" is not evidence, and it
belongs in a Pitfall callout.

**Permitted nondeterminism versus tool divergence — do not conflate these.**
These are different mechanisms with different consequences, and both are now
sourced, so the chapter can state them separately rather than hedging.

*Nondeterminism is permitted by the language*, and two independent primary
sources say so. Cummings and Salz state that a particular event region must be
processed in an arbitrary order while every implementation will exhibit a
certain order
([Rev 1.2, §2.1](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf),
**[primary]**). Sutherland, Mills and Spear, listing why the languages permit
these mistakes at all, give as one reason that Verilog and SystemVerilog event
scheduling **allows tools to optimize the order of concurrent events
differently**, which can lead to races in a poorly written model
([2006, §1](http://sutherland-hdl.com/papers/2006-SNUG-Boston_standard_gotchas_paper.pdf),
**[primary]**).

*Tool divergence has other causes too*, and the same Sutherland list separates
them cleanly — which is what makes it worth citing here. Alongside the
scheduling-freedom reason it gives, as distinct items: that the languages
provide freedom in **how they are implemented**, because simulation, synthesis
and formal analysis work differently; and that **some tools are not 100 percent
standards compliant**, which the authors explicitly say is *not* a gotcha in the
standards even though it still produces unexpected results. A fourth listed
reason is philosophical rather than mechanical: the languages deliberately allow
modeling both what will and will not work in hardware.

So the chapter has a defensible three-way split for two simulators disagreeing:
**permitted ordering freedom** (the design has a race), **implementation
differences and standard ambiguity** (legitimate divergence), and
**non-compliance** (a tool bug). Only the first is what this chapter's guidelines
protect against. Do not let the chapter imply that every disagreement between
simulators is evidence of a race — nor that permitted nondeterminism is merely
an ambiguity in the standard.

#### 4.2 The race cases the chapter needs

**(a) Two processes assigning one variable.** Cummings' `badcode1` shows two
`always @(posedge clk or negedge rst_n)` blocks both assigning the same output
`q`, one from `d1` and one from `d2` — *both using non-blocking assignments*.
The point that makes this worth teaching: non-blocking assignments do **not**
save you. The blocks can be scheduled in either order, so the result is a race
regardless. He notes synthesis flags it as a multiple-driver net and infers two
flip-flops feeding an AND gate, so pre- and post-synthesis simulation do not
even closely match. → **Guideline #6.**
[Cummings, 2000, §14](https://web.archive.org/web/20061111004954id_/http://www.sunburst-design.com/papers/CummingsSNUG2000SJ_NBA.pdf)
**[primary]** (write the book's own version of this module)

**(b) A value read in one process and written in another at the same edge.**
The pipeline case, and the best example in the literature because the *same*
code is correct or incorrect depending only on the assignment operator. Cummings
gives a three-stage shift register written four ways with blocking assignments,
including two variants where the three assignments live in three separate
`always @(posedge clk)` blocks, ordered `q1,q2,q3` in one and `q2,q3,q1` in the
other. Since `always` blocks may execute in any order, these simulate
differently from each other while both synthesize to the same correct pipeline —
a pre- versus post-synthesis mismatch. Rewritten with non-blocking assignments,
*all four orderings* simulate and synthesize correctly.
→ **Guidelines #1, #2, #4.**
[Cummings, 2000, §§9–12](https://web.archive.org/web/20061111004954id_/http://www.sunburst-design.com/papers/CummingsSNUG2000SJ_NBA.pdf)
**[primary]**

**(c) The testbench/design read-write race at a clock edge.** What the
verification regions exist to solve; §2.1's isolation mechanism is the answer.
Present this as the case that *cannot* be fixed by assignment discipline alone —
it needed new regions, which is why the 2005/2007 revisions happened.

**(d) Time-zero ordering — a fourth case, independently sourced, and cheap.**
Sutherland, Mills and Spear document the belief that `initial` blocks run before
`always` blocks (or, held just as confidently by other engineers, after them) as
a common gotcha for new users, and state that all procedural blocks regardless
of type become active at time zero **in any order**, with neither kind taking
precedence — and that as each block is activated a simulator *may, but is not
required to*, execute its statements until a timing control is reached. Their
point about the consequence is the one the chapter wants: this false assumption
leads engineers to write stimulus that does not give the same results on
different simulators.
[Sutherland, Mills and Spear, 2006, §5](http://sutherland-hdl.com/papers/2006-SNUG-Boston_standard_gotchas_paper.pdf)
**[primary]**

Worth including because it is the race a reader is most likely to have already
hit (a reset released in an `initial` block), it needs no clock, and it pairs
directly with the time-0 variable-initialization change in §1.

#### 4.3 The derivation: each guideline from a region

The eight guidelines, verbatim as Cummings numbers them
([Cummings, 2000, §5](https://web.archive.org/web/20061111004954id_/http://www.sunburst-design.com/papers/CummingsSNUG2000SJ_NBA.pdf),
**[primary]**; already in `refs.bib` as `cummings2000nba`):

1. When modeling sequential logic, use non-blocking assignments.
2. When modeling latches, use non-blocking assignments.
3. When modeling combinational logic with an `always` block, use blocking
   assignments.
4. When modeling both sequential and combinational logic within the same
   `always` block, use non-blocking assignments.
5. Do not mix blocking and non-blocking assignments in the same `always` block.
6. Do not make assignments to the same variable from more than one `always`
   block.
7. Use `$strobe` to display values that have been assigned using non-blocking
   assignments.
8. Do not make assignments using `#0` delays.

**The derivation is made explicitly in two places; cite both.** In the 2000
paper Cummings states the intent directly — the event queues "will also be
referenced to justify the eight coding guidelines" — and the whole paper is
structured as queue-based justification
([Cummings, 2000, §§5–6](https://web.archive.org/web/20061111004954id_/http://www.sunburst-design.com/papers/CummingsSNUG2000SJ_NBA.pdf),
**[primary]**). More usefully, the 2006/2007 paper performs the derivation
**region by region**: each region's description names the guideline it implies.
That is the passage to build the chapter's centerpiece table on:

| Guideline | Region that explains it | The argument, as the paper makes it |
|---|---|---|
| #1 (sequential → NBA) | **NBA** | Clocked logic coded with non-blocking assignments executes in the NBA region, which correctly models the pipelined nature of sequential elements. |
| #2, #4 (latches; mixed logic → NBA) | **NBA** | Same region, same reason; the paper points to its refs [3] and [5] for the worked cases rather than repeating them. |
| #3 (combinational → blocking) | **Active** | Combinational logic in an `always` block coded with blocking assignments executes in the Active region, which correctly models real combinational hardware. |
| #6 (one writer per variable) | **Active** (arbitrary order) | Two blocks assigning one variable can be ordered either way; the language guarantees no order. |
| #7 (`$strobe` for NBA values) | **Postponed** vs **Active** | `$display` runs in Active, before NBA updates; `$strobe` runs in Postponed, after everything, with no feedback path. |
| #8 (no `#0`) | **Inactive** | `#0` assignments are exactly what populates the Inactive region — the one region the authors say to avoid. |

[Cummings and Salz, Rev 1.2, §§2.2.2–2.2.4 and §2.2.11](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

Guideline #5 (do not mix) is the one the sources justify least directly; treat
it as a corollary of #1 and #3 — a single block cannot be both — rather than
claiming a source derives it from a region. Flagged in §6.

#### 4.4 Why `#0` is the fix that is not a fix

Both papers are emphatic and their reasoning is explicit, so this needs no
speculation. From the 2000 paper: `#0`-delay assignments are a *generally flawed
practice* used by designers trying to assign the same variable from two separate
procedural blocks, attempting to beat a race by scheduling one assignment
slightly later in the same time step; it needlessly complicates analysis of
scheduled events, and Cummings says he knows of **no** condition requiring a
`#0` that could not be replaced by a better coding style
([Cummings, 2000, §6](https://web.archive.org/web/20061111004954id_/http://www.sunburst-design.com/papers/CummingsSNUG2000SJ_NBA.pdf),
**[primary]**). The later paper is sharper: most engineers who keep using `#0`
are defeating a race that exists only because they assign one variable from more
than one `always` block — **already a violation of guideline #6** — and the
authors then drop the Inactive region from their diagrams entirely, since good
code never populates it
([Cummings and Salz, Rev 1.2, §2.2.4](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf),
**[primary]**).

That yields the chapter's line: **`#0` does not remove the race, it renames
it.** The race was "which of two blocks goes first in Active"; `#0` makes it
"which goes first in Inactive." Ordering within a region is still arbitrary —
the only change is that the bug is now harder to see.

Their footnote explains why `#0` exists at all, and is worth keeping: Inactive
was necessary in early Verilog **before the NBA region was added** (circa 1989),
and proper use of NBA makes it unnecessary. `#0` is a workaround that outlived
its problem.
[Cummings and Salz, Rev 1.2, §2.2.4 n.2](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

Do not flatten this into "never use `#0`": the condemnation is about **RTL**. A
`#0` in a *program* process, landing in Re-Inactive, is described by the same
authors as often useful and harmless (§2.1).

**A second, independent exception — worth including, because it stops the rule
from being folklore.** Sutherland, Mills and Spear reach the same general
verdict by a different route: `#0` is easily abused and does **not** truly
guarantee the delayed statement runs after everything else in the time step;
they note many Verilog trainers have said never to use it, and that alternatives
based on non-blocking assignments give more reliable ordering. But they name a
real exception — **event data types**, where in Verilog there was no way to
defer an event trigger to the non-blocking queue, so `#0` was the only tool for
a time-zero event-trigger race. SystemVerilog removes even that need with the
non-blocking event trigger `->>`, which schedules the trigger in the
non-blocking queue so all procedural blocks are active before it fires.
[Sutherland, Mills and Spear, 2006, §7.2](http://sutherland-hdl.com/papers/2006-SNUG-Boston_standard_gotchas_paper.pdf)
**[primary]**

Their phrasing that `#0` "does not truly ensure" ordering is a sharper statement
of the same point as Cummings' — it does not remove the race — and having two
independent sources converge on it makes the chapter's claim safe. The honest
summary for the chapter: **`#0` is not an ordering primitive.** It was used as
one, it never reliably was one, and the constructs that *are* ordering
primitives (non-blocking assignments, `->>`, clocking blocks) postdate the
habit.

### 5. Historical grounding

Two peer-reviewed citations are enough to establish that the event-driven
algorithm long predates SystemVerilog. Both were confirmed through Crossref with
DOIs; the full texts are behind publisher paywalls, so cite them for the
*existence and date* of the technique, not for quoted content.

**Selective trace.** E. G. Ulrich, "Exclusive simulation of activity in digital
networks," *Communications of the ACM* 12(2):102–110, February 1969.
[DOI 10.1145/362848.362870](https://doi.org/10.1145/362848.362870) **[research]**
The canonical early statement that a simulator should evaluate only the parts of
a network where activity is occurring rather than sweeping every element every
timestep — precisely the economic argument behind the event queue, and enough to
let the chapter date the model to the 1960s.

**Table-driven, time-based logic simulation.** S. A. Szygenda and E. W.
Thompson, "Digital Logic Simulation in a Time-Based, Table-Driven Environment,"
*Computer* 8(3), March 1975 — Part 1, pp. 24–36,
[DOI 10.1109/c-m.1975.218898](https://doi.org/10.1109/c-m.1975.218898); Part 2
(Thompson and Szygenda), pp. 38–49,
[DOI 10.1109/c-m.1975.218900](https://doi.org/10.1109/c-m.1975.218900).
**[research]** How production logic simulators were actually built around a
time-ordered event structure, a decade before Verilog — the second citation
showing this was engineering practice, not just a proposal.

The chapter's claim should stay modest and is fully supported: **the scheduling
regions standardize a long-established algorithm rather than inventing one.**
SystemVerilog's contribution was to specify *ordering* precisely enough to make
races avoidable — which is the authors' own FAQ #2 answer, that the events were
already being scheduled this way and the standard merely defined where.
[Cummings and Salz, Rev 1.2, FAQ #2](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

### 6. Commonly repeated but unsourced claims

| Claim | Where repeated | Status |
|---|---|---|
| "A delta cycle is …" as standard Verilog vocabulary | Ubiquitous in blogs, forum answers and training material | **Weakly attested — corrected on re-check.** Cummings and Salz do use "delta-cycle" once (Rev 1.2 §5.3), naturally and in exactly this sense: a pass through the Active region, "in any arbitrary delta-cycle". But they never define it and otherwise say "iterations". So the term is *used* in the literature, not *established* by it; it remains a VHDL import. The chapter's plan — teach "iteration within a timestep" and mention the borrowed name once — is still right, but the note should not claim the term is absent from the sources. |
| "Two simulators disagree, therefore there is a race" | Common inference | **Sourced, and more precisely than expected — see §4.1.** Sutherland, Mills and Spear separate permitted scheduling freedom, implementation/tool-class differences, and outright non-compliance. Only the first implies a race. Do not conflate them. |
| "The standard permits nondeterministic ordering within a region" | Widely repeated | **Now sourced twice, independently** (§4.1): Cummings and Salz on arbitrary ordering within a region, and Sutherland et al. on scheduling allowing tools to optimize concurrent-event order differently. Safe to assert, attributed to those authors rather than to the standard. |
| "The standard requires the regions to execute in this order" | Everywhere | **Forbidden phrasing for this book.** The ordering is real, but attribute it to Cummings and Salz's account. Say "SystemVerilog schedules …", never "the standard requires …". |
| The definition of *simulation time* | Cummings and Salz quote it | Their quoted definition is from a **draft of the standard** (their ref. [9]). Do not reuse their quotation. The chapter must state the idea in its own words. Their definition of *timestep* is their own and is safe to attribute to them. |
| "Following the guidelines eliminates 90–100% of Verilog race conditions" | `cummings2000nba`, repeated by the 2006/2007 paper | **Sourced, but it is the author's own estimate, not a measurement.** No study is cited. If the chapter uses the figure, attribute it explicitly to Cummings as an estimate; do not present it as a measured result. |
| Guideline #5 (don't mix blocking and non-blocking in one block) follows from a specific region | Implied in summaries of the guidelines | **Weakly sourced.** The region-by-region derivation covers #1, #2, #3, #4, #6, #7, #8; #5 is best presented as a corollary of #1 and #3. Do not claim a source derives it from a region. |
| "`#0` is always wrong" | Common shorthand | **Overstated.** True for RTL (guideline #8); the same authors call `#0` in a program process useful and harmless. Keep the distinction. |
| Named simulator behavior ("VCS does X, Questa does Y" at a given region) | Forum lore | **No source found and none sought.** Vendor-specific ordering claims must not appear. The relevant sourced point is the opposite: ordering within a region is arbitrary, and relying on any observed order is the bug. |
| A design "hangs" on a zero-delay loop | Common phrasing | Mechanism is sourced (§3); the *word* is misleading. Prefer "loops forever without advancing simulation time." Behavior should be confirmed in a real simulator before the chapter asserts what the user sees. |

### 7. Suggested BibTeX keys

| Key | Full citation | Used by |
|---|---|---|
| `cummingssalz2007events` | Clifford E. Cummings and Arturo Salz, "SystemVerilog Event Regions, Race Avoidance & Guidelines," SNUG Boston 2006 (Synopsys Users Group Conference, Boston, MA), Rev 1.2, December 2007. 42 pp. Sunburst Design, Inc. and Synopsys. URL: `http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf`; archived at `https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf`. Accessed 2026-09-08. **Note field must record: presented SNUG Boston 2006; Rev 1.2 (December 2007) adds the Re-NBA region per Mantis 890.** | §§1, 2, 3, 4, 5 — the chapter's spine |
| `cummingssalz2006events` | Same authors and title, **Rev 1.0**, SNUG Boston 2006, 40 pp. Archived at `https://web.archive.org/web/20061111005225id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf`. Accessed 2026-09-08. | §2.4 only, for the eight-region footnote. Optional — omit if the chapter does not tell the revision story. |
| `cummings2000nba` | **Already in `refs.bib`.** Clifford E. Cummings, "Nonblocking Assignments in Verilog Synthesis, Coding Styles That Kill!," SNUG San Jose 2000, Rev 1.2. | §§3, 4.2, 4.3, 4.4 — the eight guidelines and the race examples |
| `cummings2002nbadelays` | Clifford E. Cummings, "Verilog Nonblocking Assignments With Delays, Myths & Mysteries," SNUG Boston 2002. `http://www.sunburst-design.com/papers/CummingsSNUG2002Boston_NBAwithDelays.pdf`. **Not retrieved for this note** (Archive rate-limiting); listed because both papers above cite it as the source of worked cases behind guidelines #2 and #4. Retrieve before citing. | §4.3, if the chapter expands #2/#4 |
| `sutherland2006gotchas` | Stuart Sutherland, Don Mills and Chris Spear, "Standard Gotchas: Subtleties in the Verilog and SystemVerilog Standards That Every Engineer Should Know," SNUG Boston 2006, 59 pp. Sutherland HDL, LCDM Engineering, Synopsys. `http://sutherland-hdl.com/papers/2006-SNUG-Boston_standard_gotchas_paper.pdf`. Accessed 2026-09-08. **Openly hosted — no archive URL needed.** | §§4.1, 4.2, 4.4 |
| `sutherland2007gotchas` | Same authors, "More Standard Gotchas: Subtleties in the Verilog and SystemVerilog Standards That Every Engineer Should Know," SNUG San Jose 2007, 44 pp. `http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf`. Accessed 2026-09-08. Note the title differs between the paper's own cover ("Gotcha Again") and the publisher index ("More Standard Gotchas"); cite the index form. | §3 |
| `ulrich1969selective` | E. G. Ulrich, "Exclusive simulation of activity in digital networks," *Communications of the ACM*, 12(2):102–110, February 1969. DOI 10.1145/362848.362870. | §5 |
| `szygenda1975timebased` | S. A. Szygenda and E. W. Thompson, "Digital Logic Simulation in a Time-Based, Table-Driven Environment. Part 1," *Computer*, 8(3):24–36, March 1975. DOI 10.1109/c-m.1975.218898. (Part 2, Thompson and Szygenda, 8(3):38–49, DOI 10.1109/c-m.1975.218900 — separate key `thompson1975timebased2` if both are cited.) | §5 |

Style note: existing Sunburst entries in `refs.bib` are `@inproceedings` with the
canonical `sunburst-design.com` URL. Those URLs are now login-walled. Consider
adding the archive URL in a `note` field across all Sunburst entries rather than
replacing the canonical URL — a repo-wide decision worth raising, since
`cummings2000nba`, `cummings2008cdc` and the others have the same problem.

### 8. Confidence notes and gaps

**High confidence — safe to draft from.**

- The nine regions, their names, order, grouping into Active and Reactive
  region sets, and what executes in each. Directly and repeatedly sourced.
- The iteration structure within a time slot, and that time advances only when
  no events remain.
- The race taxonomy, the three worked race cases, and the eight guidelines.
- The region-by-region derivation of guidelines #1, #2, #3, #4, #6, #7, #8.
- The `#0` argument, including the RTL/program asymmetry.
- `$display` in Active versus `$strobe` in Postponed.
- The time-0 variable-initialization change between Verilog-2001 and
  SystemVerilog.

**Must not be asserted without more work.**

1. **No clause-level claims about IEEE 1800.** Never "the standard says," never
   "clause 4 defines." Cummings and Salz's own quotations of the LRM and of the
   P1800 draft must not be passed through into the book — that would reproduce
   standard text at one remove. Paraphrase their *exposition*, which is their
   own writing.
2. **"Delta cycle" is not sourced as SystemVerilog vocabulary** (§6). Decide how
   to introduce the term before drafting.
3. **The zero-delay infinite-loop example** is now sourced for both mechanism
   *and* reported symptom (§3, Sutherland et al. 2007), so this is no longer a
   gap in the evidence — only in the artifact. Still build it under `examples/`
   and run it, per the house rule that simulator output comes from `run.out`.
4. **The `$display`/`$strobe` worked example must be run, not reasoned about.**
   It is the chapter's best demonstration and therefore the worst place to be
   wrong. `examples/ch04-*/` with captured output.
5. **Figures must be redrawn.** The papers' Figures 1, 4, 5, 6, 7 and 9 (event
   regions, the sampling mechanism, the Reactive region set) are exactly the
   diagrams the chapter wants and **must not be reproduced**. Draw the book's
   own from the region list, and do not credit them as adapted, since the
   underlying content is the region ordering rather than data.
6. **All code listings must be written from scratch.** Cummings' `pipeb3`,
   `pipen1`, `badcode1` and the `fork/join_none` snippet are described above so
   the chapter can build equivalent examples; do not transcribe them.
7. **The "90–100%" figure** is an author estimate; attribute or omit (§6).
8. **`cummings2002nbadelays` was not retrieved.** If the chapter leans on
   guidelines #2 or #4 in depth, fetch it first.
9. **Simulator-specific behavior is out of scope** on this note's evidence.
   Anything about how a named simulator orders events needs its own source.

**One gap that does not change the plan but is worth knowing.** Open-simulator
documentation (Verilator, Icarus, cocotb) was not successfully retrieved for
this note — the URLs tried returned 404 or redirected. If the chapter wants to
say how an open-source tool implements or diverges from this model (Verilator's
handling of NBA and its scheduling is a known point of divergence worth a
callout), that needs a separate pass. Nothing in §§1–5 depends on it.


# Part B — Sampling, X, and time

**Scope.** Testbench/design boundary at a clock edge; clocking and program blocks;
assertion sampling; four-state vs two-state; timescale. Does not re-derive Turpin
2003 (`turpin2003x`).

**Reachability.** `sunburst-design.com` redirects to `paradigm-works.com` with its
papers behind a login, so every Cummings paper here came from an Internet Archive
capture of the original URL, and those capture URLs are what is cited; same route
for `sutherland-hdl.com` and `verilab.com`. IEEE 1800 is **named only** — paywalled
and unread. Every behavioral statement below is attributed to a practitioner paper
or to open simulator docs; where a source describes the standard I relay that
source's description and credit it. Claims supportable only from the standard are in
§6. Web search was unavailable (§8).

---

### 1. The boundary at a clock edge

Cummings & Salz, *SystemVerilog Event Regions, Race Avoidance & Guidelines*, SNUG
Boston 2006 (rev. 1.2, Dec 2007), 42 pp., co-authored by a Synopsys simulator
architect.
[Cummings & Salz, SNUG Boston, 2006-09-01](https://web.archive.org/web/20240110182353id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

- **The distinction to open the chapter with** (§2.1). *Hardware races* are
  intrinsic to the physics (their example: the NAND S-R latch whose final state is
  unpredictable when both inputs release together). *Simulation-induced races* are
  "not intrinsic to the design or its physics, but ... a natural, although
  undesirable, consequence of the event-driven simulation algorithm" — the simulator
  processes events one at a time and so serializes what hardware does concurrently.
  The motivating sentence: such a race "can cause the simulator to simulate a faulty
  design when in fact the design is correct, or more dangerously, simulate a
  seemingly correct design when in fact the design is flawed." Order within a region
  is arbitrary by the language but fixed in any implementation — which is why a race
  is invisible on one simulator and fatal on the next.
- **Structure** (§2, §2.2). A *time slot* holds all activity at one simulation time
  and may iterate through the regions several times without time advancing (the older
  term *timestep* was dropped in 2008). 17 ordered regions in the 2005 revision — nine
  for language statements, eight for PLI. The nine: Preponed; *Active set* (Active,
  Inactive, NBA); Observed; *Reactive set* (Reactive, Re-Inactive, Re-NBA); Postponed.
  Grouped by intent: Active set for RTL, Preponed/Reactive/Postponed for verification,
  Preponed/Observed/Reactive for assertions. Never use Inactive — `#0` in RTL papers
  over a race instead of fixing it (§2.2.4).
- **The race concretely.** Clocked design logic updates in NBA. A module-based
  testbench reading in Active on the same edge sees the *old* value; reading after
  NBA sees the new; nothing decides which if both sit in Active. The design-side half
  of the fix is Cummings' earlier nonblocking guidelines, credited in the 2006 paper
  with removing "90-100%" of induced RTL races: clocked logic nonblocking,
  combinational blocking, never two `always` blocks writing one variable.
  [Cummings, SNUG San Jose, 2000-03-01](https://web.archive.org/web/2020/http://www.sunburst-design.com/papers/CummingsSNUG2000SJ_NBA.pdf)
  **[primary]** (URL from the 2006 reference list; not fetched — §8.)
- **Why not to drive on the active edge** (§6.1). Driving *on* it required
  nonblocking assignments on every input — a zero-delay register transfer that breaks
  on a netlist with real hold times, since all inputs change at once. The `<= #1`
  workaround is "a potential source for serious simulator performance degradation."
  Driving on the *inactive* edge, away from setup and hold, lets one testbench serve
  RTL and a back-annotated netlist unchanged.

### 2. Clocking blocks and program blocks

**Why skews exist.** Bromley & Johnston, *Taming Testbench Timing: Time's Up for
Clocking Block Confusions*, SNUG Austin 2012 (Verilab), §2: a synchronous testbench
must "sample signals one setup time before the clock event" and "update signals one
clock-to-output delay after the clock event," because that is what the DUT's
flip-flops do. Input skew is the testbench's t<sub>SU</sub>, output skew its
t<sub>CO</sub>. Their heading "A Clocking Block Is Not A Time Machine" is the pitfall
in one line: at an edge a testbench sees current and past values, never future ones.
They report the construct "has proved to be surprisingly error-prone, despite nearly
a decade of application experience."
[Bromley & Johnston, SNUG Austin, 2012-09-01](https://web.archive.org/web/2020id_/http://www.verilab.com/files/paper51_taming_tb_timing_FINAL_fixes.pdf)
**[primary]**

Four of their eleven guidelines matter here: access only the clockvars, never the raw
signal (#1); synchronize on the clocking block's own event, not the raw clock (#2);
drive output clockvars with `<=`, never `=` (#3); and **use `input #1step` unless you
have a special reason not to, because it guarantees the testbench sees sampled values
consistent with what assertions see** (#4) — the direct citation for the Chapter 4 →
Chapter 9 link. Also #5 (non-zero output skew, for readable waveforms and gate-level
clock-network delay) and #9–#11 (clocking block in an interface, reached through a
virtual-interface modport).

Cummings & Salz (§5, §6.2) add: signals get clocking-block timing **only when
referenced through the block's name** — the bare name is still the raw signal, and
mixing the two is the failure mode. Default input skew is one *step*, default output
skew zero (§2.2.13). `##` is defined against the block's event, so `##1` in a
`@(posedge clk)` block waits for that edge; their Example 12 and Figures 12–18 trace
a program block mixing a plain assignment with `##1 cb1.d <= ...` through an
`output #2 d` skew, event by event. Driving on the inactive edge costs no extra
events, since combinational logic must ripple to quiescence anyway.

**Program blocks: the intent** (Cummings & Salz §2.2.7–2.2.8). The Reactive set is
the dual of the Active set, later in the same slot, so program code sees three things
module code does not: steady-state values at the start of the slot, settled values
after propagation, and the disposition of every concurrent assertion that fired. They
recommend programs "to isolate RTL design code execution from testbench code
execution."

**The disagreement — and it is Cummings against himself.** In *Applying Stimulus &
Sampling Outputs — UVM Verification Testing Techniques*, SNUG 2016, he reverses.
[Cummings, SNUG, 2016-09-01](https://web.archive.org/web/2023id_/http://www.sunburst-design.com/papers/CummingsSNUG2016AUS_VerificationTimingTesting.pdf)
**[primary]**

His §10: the program block "essentially made it possible to drive stimulus on the
active clock edge and avoid RTL-stimulus race conditions," but stimulus should not be
driven there at all — "as long as the verification engineer does not drive stimulus on
the active clock edge, there is no RTL-stimulus race condition and a program is not
needed." He lists restrictions he calls gratuitous (`initial` but not `always` inside
a program; a program may hierarchically reference module signals but not the reverse;
a program may call module tasks but not the reverse; simulators have not consistently
checked program code) and concludes: "The SystemVerilog program statement should just
die and never be used in your code!"

§10.1, "Cliff's confession," is the passage to cite, because it records the other
side's reasoning: he voted to keep programs in the 2015 revision after advocates
argued they let engineers write race-free stimulus *without* learning his
drive-off-the-active-edge technique; he now regrets the vote. Two defensible
positions from one author — programs as a guard rail for engineers who have not
internalized the timing discipline, versus programs as unnecessary once they have.
**Present both; do not adjudicate.** Context only: the 2006 paper already warned
(§1.2) that committee clarifications "might change some of the restrictions of
programs, clocking blocks, event regions"; Bromley & Johnston use no program blocks
at all, which is suggestive but is not a stated position and must not be reported as
one.

### 3. Assertion sampling

Cummings & Salz (§2.2.1, §2.2.6, §2.2.13): values used by concurrent assertions are
sampled in the **Preponed** region — first in the slot, executed once immediately
after time advances, no feedback path back into it — and the assertions are
*evaluated* in the **Observed** region, after Active-set activity settles. An
assertion therefore reads the value that was stable *before* the edge, not the value
the edge produced. That is why it is immune to the §1 race: the race is
Active-versus-NBA ordering and the assertion reads in neither.

- **Preponed vs. the previous Postponed is unobservable.** Both are read-only, so
  values in a contiguous pair are identical and only the timestamp differs — "it is
  not observable in which region the simulator actually samples a value." Do not claim
  a simulator *must* sample in Preponed.
- **Model** (Figure 7): keep two values per sampled signal, current and Preponed;
  read the second when the clocking expression fires. Only slots where that expression
  triggers need sampling, and the simulator need not predict it. They describe an
  intra-slot delay gate whose delay can vary — input skew is the same mechanism.
- **Assertions are monitors**: they cannot modify design state, and pass/fail action
  blocks are scheduled into *Reactive*, not Observed.
- **`#1step`** is the *global time precision*, the smallest precision declared
  anywhere in the design (§5). All values used by assertions, with or without
  clocking-block timing, effectively come from one step before the current slot, and
  since nothing can happen in that interval this is indistinguishable from Preponed
  sampling. This explains *why* the default skew is a step rather than a real delay:
  it is the largest skew that provably cannot skip an event.

**`$strobe` vs. `$display` vs. `$monitor`** (§2.2.3, §2.2.11):

| Task | Region | What it shows |
|---|---|---|
| `$display` | Active | value when the statement executes — before NBA updates land |
| `$strobe` | Postponed | the final settled value for the time slot |
| `$monitor` | Postponed | same, re-triggered on changes in its argument list |

No feedback path leaves Postponed, so those values are final for the slot (matching
the old Verilog Monitor region); Postponed is also where strobe-sampled functional
coverage is collected. A `$display` in a clocked block printing stale values is the
classic first encounter with the scheduler; `$strobe` is the one-line fix.

### 4. Four-state and two-state simulation

[Sutherland, DVCon, 2013-02-25](https://dvcon-proceedings.org/wp-content/uploads/im-still-in-love-with-my-x.pdf)
**[primary]** — *I'm Still In Love With My X! (but, do I want my X to be an optimist,
a pessimist, or eliminated?)*, written as the successor to Turpin 2003 and Mills 2004.
[Piper & Vimjam, DVCon, 2012-02-28](https://dvcon-proceedings.org/wp-content/uploads/x-propagation-woes-masking-bugs-at-rtl-and-unnecessary-debug-at-the-netlist-presentation.pdf)
**[vendor]** — *X-propagation Woes*; this is the presentation deck (the paper is not
on the proceedings site), its author is a Real Intent technical marketing manager, and
its last third pitches a Real Intent flow. Taxonomy usable; proposed solution is a
vendor claim.

**The four values.** Sutherland's framing beats the usual list: 0, 1 and Z are
*abstractions of values that exist in silicon* (abstract because they carry no
voltage, current or slope), whereas **X is not an abstraction of anything in
silicon** — it is the simulator saying it cannot predict whether the real value would
be 0, 1 or Z. Piper & Vimjam's tool-disagreement table is worth redrawing: to
simulation X means *unknown, not 0 or 1*; to synthesis, *don't care, either 0 or 1*;
to formal, *both 0 and 1*. Sutherland's sources of X (§2): uninitialized 4-state
variables, registers and latches; low-power shutdown/power-up; unconnected input
ports; bus contention; operations with unknown results; out-of-range bit-selects and
indices; gates with unknown outputs; setup/hold violations; deliberate assignment;
testbench injection.

**X-optimism, mechanically** (§3.1). If an `if...else` control condition is unknown,
the `else` branch executes. A `case` with an X selector matches nothing and falls to
`default`; `casex`/`casez` are worse, because the wildcard *masks out* an X in the
selector and picks a branch. Operators do the same per bit: X AND 0 is 0. **Sometimes
optimism is right** — his Figure 1 is a flip-flop with synchronous active-low reset:
at power-up `d` is ambiguous, but with `rstN` at 0 the AND output is 0 in silicon
regardless, so pessimistic propagation would fail to reset in simulation a design that
resets fine in silicon. His Table 1 shows the other side: for `if (sel) y = a; else
y = b;` with `sel` unknown, the RTL yields a known value for every combination, while
both MUX-gate and NAND-gate netlists yield X where silicon is genuinely
undeterminable.

**X-pessimism, mechanically.** Piper & Vimjam's reconvergence example:
`out = a*sel + b*!sel` with `a = b = 1` and `sel = X` evaluates to `X + !X`, which the
simulator must call X, though the real circuit outputs 1 either way — it cannot know
the two `sel` references are one signal. Their summary: "X-optimism = unknown reduced
to known ... can result in the masking of a functional bug"; "X-pessimism = more X
than necessary ... false negatives mean more debug." Sutherland adds *X lock-up*: a
state element that captures an X can never leave it, because every decision that would
clear it is itself unknown.

**Since Turpin 2003, four strands:**

1. **`xprop` modes** (Sutherland §7). Some simulators offer a non-standard,
   deliberately more pessimistic algorithm for `if...else`, `case` and edge
   sensitivity, aiming at a balance rather than either extreme; he names the Synopsys
   VCS `-xprop` option and its "T-merge" algorithm as the example, and is clear this
   **breaks the language's rules by design**. Two objections to carry into the chapter:
   an xprop mode makes a bug propagate *downstream* to become visible, which forces
   tracing an X backward through many lines and clock cycles to its cause; and the
   added pessimism risks false failures and X lock-up. Name the vendor option once as
   an example, never as a recommendation.
2. **Formal and static** (Piper & Vimjam's "point solutions"): structural analysis
   (finds X-susceptible constructs, "can be very noisy," no sequential reasoning);
   simulation with manual diffing ("slow and painful"; "random initialization to
   eliminate X's can hide issues"); hand-written X-accurate models using `===`, which
   they show is "error prone" and does not scale past a toy; model checking (X
   exercised as both 0 and 1 exhaustively, but capacity-limited, and intent must first
   be written as assertions); and symbolic simulation, exhaustive but producing false
   failures.
3. **Turpin's follow-up**, *Solving Verilog X-issues by sequentially comparing a
   design with itself*, SNUG Boston 2005 — **not read** (§8).
4. **Reducing X at the source** (Sutherland §9) — the recommendation to actually give
   a reader. Trap the X where it appears, with immediate assertions on module input
   ports and every selection control: `assert (!$isknown(sel)) else $error(...)`. This
   "solves the problems of both X-optimism and X-pessimism" at once, since neither
   matters if the X never leaves its origin; and assertions can be disabled during
   reset and low-power windows where X is expected, which no propagation mode does
   selectively. Assertions are ignored by synthesis.

**Two-state, what is gained: folklore vs. evidence.** Sutherland §5 lists the
theoretical gains (no X lock-up, closer agreement with synthesis and with silicon,
smaller memory footprint, faster run time). Cummings & Bening measured them.
[Cummings & Bening, SNUG Boston, 2004-09-01](https://web.archive.org/web/2023id_/http://www.sunburst-design.com/papers/CummingsSNUG2004Boston_2StateSims.pdf)
**[primary]**

The ceiling (§5.1): a 4-state value needs ≥2 bits, and a net may carry 3 more for
logic-1 strength and 3 for logic-0, so up to 8 bits of storage per simulated bit;
two-state gives a one-to-one mapping and lets native machine operations replace table
lookups. The measurement (§7): on a ~2.4-million-gate-equivalent RTL chip model at
Hewlett-Packard, March 2001, VCS 6.0 — **2045.96 CPU seconds without the two-state
option, 1928.97 with it: about 6%.** They add that they have "heard of some design
teams that claim upwards of 15%" but "have not seen this level of performance
improvement," and did not consider speed a compelling reason to switch; the compelling
reason was the *methodology*. Two cautions: one 2001 measurement on one simulator and
design, and §6.4 warns "it would be a mistake to quote the performance figures from
this paper even 6 months from now." Use it to puncture the folklore, not as a current
figure. Their §8 makes a good callout: HP's large server projects kept a two-state
*design style* — enforced by lint rules, random initialization and assertions — while
still running on four-state commercial simulators. Two-state as a discipline, not a
simulator switch.

**Two-state, what is lost** (Sutherland §5–§6). Uninitialized state stops announcing
itself; X and Z checks silently stop working (`assert (data === 'Z)` and
`assert (^data !== 'X)` can never fire); a deliberate `default: result = 'X;`
don't-care becomes a concrete value the simulator picks, so the don't-care claim is
never tested; and the mapping rule is blunt — assigning a 4-state value to a 2-state
variable turns every X or Z bit into **0**, which "does not accurately mimic silicon
behavior where each ambiguous bit might be either a 0 or a 1." His §6 example is the
one to adapt: a program counter instantiated with `loadN` and `new_count` left
unconnected. Four-state shows X and the bug is visible; two-state makes `loadN` a
constant 0, `if (!loadN)` always true, and the counter sits in load state forever,
looking like a bug somewhere else.

**Randomized two-state initialization is a different technique** — keep it apart from
plain two-state and from xprop. It traces to Bening, *A two-state methodology for RTL
logic simulation*, DAC 1999 (from Sutherland's reference list; not read — §8): start
each register bit at a *random* 0 or 1 and run many seeds, so reset coverage samples
power-up states instead of pinning to all-zeros. Sutherland's objection to plain
two-state is exactly that all-zeros "verifies only one extreme and unlikely hardware
condition." Cummings & Bening add the catch (§6.5, §10): the randomization must be
*reproducible*, and in 2004 neither the language nor VCS offered seeded repeatable
initialization — the preferred method was covered by an HP patent and "might not be
available for public use."

Verilator is the open realization, and therefore the citable one.
[Verilator manual, accessed 2026-09-08](https://verilator.org/guide/latest/exe_verilator.html)
**[docs]** ·
[Verilator language support, accessed 2026-09-08](https://verilator.org/guide/latest/languages.html)
**[docs]**

- It states it is "mostly a two-state simulator, not a four-state simulator";
  `--fourstate` is "Experimental, for developer use only," and `--no-fourstate` is the
  default. That makes it a usable classroom demonstration of what two-state costs.
- `--x-initial` controls variables not otherwise initialized: `0` zeroes everything;
  `unique` (default) calls a function per initialization and "allows for finding reset
  bugs"; `fast` optimizes and "will likely hide any code bugs relating to missing
  resets." With `unique`, `+verilator+rand+reset+2` and `+verilator+seed+<value>` give
  exactly the seeded randomization Cummings & Bening could not get in 2004 — and the
  manual tells you to print the seed so a failure can be reproduced.
- `--x-assign` is the *separate* control for X values written explicitly in source:
  `0`, `1` ("more likely to find reset bugs as active high logic will fire"), `fast`
  (default), `unique` ("the slowest, but safest for finding reset bugs"). Two knobs,
  two populations of X — preserve the distinction.
- Its recommended procedure is a ready-made exercise: run initialized to all zeros,
  then all ones, then random, and check reset reaches the same state.

**Reset and initialization — the link back to Chapter 3.** Sutherland §2.1–§2.2:
4-state variables begin simulation at X, so register and latch outputs start at X; a
register output "will remain an X until the register is either reset or a known input
value is clocked into" it, and a latch stays X until both enabled and fed a known
value, in RTL and gate-level alike. That is why four-state simulation of an unreset
design shows X, and why the X is *informative*. Two-state shows 0 (or a seeded random
value), the design proceeds, and nothing announces that reset was never connected.
The argument cuts a way worth stating: **the reset test is what makes two-state
simulation safe**, and without it two-state hides precisely the bug class the test
exists to find.

Two Verilator details bear on reset tests: uninitialized *clocks* get 0 rather than a
random value; and by default X→0 does not produce a negedge, so a reset sequence that
(badly) relies on the X→0 edge of an uninitialized `rst_n` will not fire.
`--x-initial-edge` emulates event-driven simulators that do generate it, with the
manual's caveat that needing it "may be another indication of problems with the
modeled design that should be addressed." Its suggested fix — declare
`logic rst_n = 1;` at construction, drive it to 0 in an `initial` block at time zero —
is the same trick as Cummings & Salz's recommended clock oscillator, which assigns
`clk <= '0` at time zero for a deterministic, race-free X→0 negedge (§4, Example 5).

### 5. Time, timescale and precision

Sutherland, *Gotcha Again: More Subtleties in the Verilog and SystemVerilog Standards
That Every Engineer Should Know*, SNUG San Jose 2007, §8.1 — written symptom-first and
adaptable directly.
[Sutherland, SNUG San Jose, 2007-03-01](https://web.archive.org/web/2020id_/http://www.sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf)
**[primary]**

His symptom is exactly the "plausible rather than obviously wrong" failure: *"My
design outputs do not change at the same time in different simulators."* Nothing
errors; the waveform is merely shifted.

- **Mechanism.** A `#` delay is a bare number with no unit. The unit comes from a
  `` `timescale `` directive with two arguments — the module's time *unit* and time
  *precision*, each an increment of 1, 10 or 100 in units from seconds to femtoseconds.
  Precision lets a module express a non-whole delay and is relative to the unit; within
  a simulation "all delays are scaled to the smallest precision used by the design."
  So `` `timescale 1ns/100ps `` makes `#2.3` mean 2.3 ns, `` `timescale 1ps/1ps ``
  makes `#7` mean 7 ps.
- **Gotcha one: file order.** The directive "is not bound to modules or files"; it
  applies to everything after it until the next one. If some files declare a timescale
  and others do not, reordering the file list changes what a delay means in the files
  that do not — "radically different simulation results, even with the same simulator."
- **Gotcha two: no portable default.** A compiler reading a file with no timescale in
  effect "might, or might not, apply a default time unit," so the same design behaves
  differently on different simulators. (His characterization — cite him, not the
  standard.)
- **His fix.** Old-style: a `` `timescale `` at the top of every file.
  SystemVerilog-style: `timeunit` and `timeprecision` as *keywords inside* a module,
  interface, program or package, local to that scope and so immune to file order; plus
  an explicit unit on the delay itself (`#1ms`).

**Two open simulators, two different answers to the same missing declaration** —
which is the point:

- Icarus ships `-Wtimescale`, for "inconsistent use of the timescale directive. It
  detects if some modules have no timescale, or if modules inherit timescale from
  another file," with the consequence in Sutherland's own terms: both "probably mean
  that timescales are inconsistent, and simulation timing can be confusing and
  dependent on compilation order." Included in `-Wall`. A dedicated warning in a
  mainstream open simulator is itself evidence the mistake is common.
  [Icarus Verilog documentation, accessed 2026-09-08](https://steveicarus.github.io/iverilog/usage/command_line_flags.html)
  **[docs]**
- Verilator instead supplies a default: `--timescale <timeunit>/<timeprecision>`
  "sets default timeunit and timeprecision when `timescale` does not occur before a
  given module," defaulting to **1ps/1ps** to match SystemC. `--timescale-override`
  overrides every timescale in the sources and may set precision alone (`/1fs`); the
  manual notes precision must be consistent with SystemC's `sc_set_time_resolution()`,
  and since 1fs is finest "it may be desirable always to use a precision of 1fs."
- Precision is global, which links back to §3: Cummings & Salz define the *global time
  precision* as the minimum over every precision declared anywhere, and `#1step` as
  exactly that. **Adding one module with a finer precision changes the meaning of
  `#1step` everywhere.** Timescale is not a local decision.

**Why it looks plausible** (my synthesis, not a source claim — §6): a wrong timescale
produces no error, no X, no missing edge. Every delay in a file is scaled by the same
wrong factor, so waveforms keep the right shape and take the wrong duration. It
surfaces only where two differently-scaled regions meet — a clock generator in one
file, a model delay from another, a protocol timeout now expiring 1000× too early —
and then looks like a functional bug in whichever block is on the wrong side.

### 6. Commonly repeated but unsourced claims

| Claim | Status |
|---|---|
| "IEEE 1800 requires X" in any form | Out of bounds by the book's rule; every statement above is attributed to a paper or to simulator docs. |
| Delays finer than the precision round to the nearest precision unit | Universally taught; no open source found stating the rule. Sutherland 2007 says only that delays are "scaled to the smallest precision used by the design." Write "simulators round" without a rule, or find a source. |
| Two-state simulation is "roughly 2× faster" | Contradicted by the only measurement reached: ~6% (Cummings & Bening §7). |
| Program blocks are obsolete because UVM does not use them | UVM's non-use is real; no source makes it the *reason*. Cummings' 2016 argument is a different one. |
| `$display` in a clocked block "shows the old value" | True as a consequence of Active-vs-NBA ordering, but ordering *within* Active is arbitrary. Say "may show" beyond the NBA case. |
| Assertions "cannot" have race conditions | Overstated. Preponed sampling removes the race on sampled values; action blocks run in Reactive as ordinary procedural code. |
| A clocking block "fixes" testbench timing | Bromley & Johnston are the counter-evidence: "surprisingly error-prone," chiefly clockvar-vs-signal confusion and `=` where `<=` is required. |
| The X→0 negedge at time zero behaves the same everywhere | It does not: Verilator suppresses it by default; `--x-initial-edge` restores it. |

### 7. Suggested BibTeX keys

`cummings2006events` (Cummings & Salz, SNUG Boston 2006, rev. 1.2 2007) ·
`cummings2016stimulus` (Cummings, "Applying Stimulus & Sampling Outputs," SNUG 2016) ·
`bromley2012clocking` (Bromley & Johnston, "Taming Testbench Timing," SNUG Austin
2012) · `sutherland2013x` (DVCon 2013) · `piper2012xprop` (Piper & Vimjam, DVCon
2012) · `cummings2004twostate` (Cummings & Bening, SNUG Boston 2004) ·
`sutherland2007gotcha` (SNUG San Jose 2007) · `verilatormanual` and `iverilogdocs`
(cite page + access date).

Already present: `turpin2003x`. Only if the chapter reaches the papers:
`mills2004assertive`, `bening1999twostate`, `turpin2005sequential`, `cummings2000nba`.

### 8. Confidence notes and gaps

**High confidence — full text read from the PDF in this session:** Cummings & Salz
2006; Cummings 2016; Bromley & Johnston 2012; Sutherland 2013; Sutherland 2007 §8.1;
Cummings & Bening 2004; Piper & Vimjam 2012 (deck). Every figure, guideline and
section number cited was read from the document, not recalled. Same for the Verilator
option text and the Icarus `-Wtimescale` description.

**Cited but not read — attribute nothing specific to these:** Mills, "Being Assertive
with Your X," SNUG San Jose 2004; Bening, DAC 1999; Turpin, SNUG Boston 2005; the
three SNUG San Jose 2012 X-propagation papers Sutherland cites (Greene tutorial;
Evans, Yam & Forward; Greene, Salz & Booth); Cummings, SNUG San Jose 2000.

**One correction to the brief.** It expected Mills material on xprop. Mills'
contribution is the 2004 *assertion-based X-detection* argument, carried forward by
Sutherland 2013 §9 and sourced here to Sutherland. The DVCon 2012 X-propagation paper
is by **Piper and Vimjam**, not Mills.

**Gaps.** (1) No source for the timescale rounding rule — the one factual hole in §5.
(2) The `$strobe`/`$display`/`$monitor` table rests on a single source; authoritative,
but uncorroborated. (3) All two-state performance evidence is from 2001–2004 on a
simulator two decades old; a current number would have to come from the book's own
Verilator and Icarus examples — an original contribution rather than a citation.
(4) No post-2013 source on xprop, so the chapter should not characterize current
practice. (5) This session's web-search allowance was exhausted before the task began,
so discovery ran on known URLs, Internet Archive capture enumeration and
reference-list chasing, biasing the note toward the practitioner canon. A follow-up
pass with search available should look for post-2015 material on X-propagation and on
whether clocking-block guidance has changed.

# Part C — Simulator implementations

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

### 1. Verilator: what it is, and what it is not

#### 1.1 Not a simulator in the usual sense

Verilator's own overview refuses the word: it is "not a traditional simulator
but a compiler," which "reads the specified SystemVerilog code, lints it,
optionally adds coverage and waveform tracing support, and compiles the design
into a source-level multithreaded C++ or SystemC 'model'"
([Verilator user guide, overview, 5.052, accessed 2026-09-08](https://verilator.org/guide/latest/overview.html))
**[docs]**. What you run is a compiled C++ program, not a design loaded into a
simulation kernel.

#### 1.2 Scheduling: static, and modeled on two of the standard's regions

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

#### 1.3 `--timing` changes the answer, partially

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

#### 1.4 Two-state, and what that costs

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

#### 1.5 Documented divergences from an event-driven simulator

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

#### 1.6 Does Verilator guarantee the same answer as an event-driven simulator?

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

### 2. Icarus Verilog

#### 2.1 What it is

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

#### 2.2 SystemVerilog coverage — the honest version

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

#### 2.3 A documented, deliberate scheduling deviation

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

### 3. Do conforming simulators disagree? (the answer to C)

**Yes — and it is documented from two directions: by tool authors describing
their own divergence, and by conference-paper authors describing the class of
problem. What could not be obtained is a single peer-reviewed study that runs
race-sensitive source on multiple simulators and tabulates the disagreement.**

#### 3.1 The strongest general citable statement

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

#### 3.2 Tool documentation admitting divergence

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

#### 3.3 A conformance test suite exists

`sv-tests` is "a test suite designed to check compliance with the SystemVerilog
standard," maintained by CHIPS Alliance. It runs a large corpus across tools
including Yosys, Verilator, Icarus Verilog, slang, sv2v, sv-parser, moore,
verible, circt-verilog and yosys-slang, and reports which features each supports
([CHIPS Alliance `sv-tests`, accessed 2026-09-08](https://github.com/chipsalliance/sv-tests))
**[primary]**. Important limitation to state honestly: it is predominantly a
*parsing and elaboration* support matrix, not a runtime-semantics differential
tester, so it evidences "tools support different subsets," not "tools compute
different values."

#### 3.4 What is missing

No published differential-testing study of simulator *runtime* semantics on
race-sensitive RTL was located. If the chapter wants a claim of the form "study
X ran N simulators on racy code and found disagreement in M cases," that claim
currently has no source and must not be made (§6).

---

### 4. Other open simulators

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

### 5. Performance, as far as it is sourced

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

### 6. Commonly repeated but unsourced claims

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

### 7. Suggested BibTeX keys

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

### 8. Confidence notes and gaps

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
