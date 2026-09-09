---
title: "Research note: Chapter 4, part 1 — the scheduling model"
date: 2026-09-09
author: research-agent
status: draft
feeds: Ch. 4
---

# Chapter 4 research, part 1: the scheduling model

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

## 0. Can this chapter be sourced without the standard?

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

## 1. The simulation cycle and the event queue

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

## 2. The scheduling regions

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

### 2.1 What executes where

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

### 2.2 `$strobe` versus `$display` (part of item C)

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

### 2.3 A naming aside worth one footnote

"Prepone" is a real word meaning to schedule for an earlier time, in common use
in South Asia; the committee groaned but accepted no alternative. The authors'
mnemonic is genuinely useful: Preponed and Postponed are the begin/end regions
bracketing each time slot.
[Cummings and Salz, Rev 1.2, §2.2.12](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

### 2.4 Which revision to cite, and why it matters

There are **two substantively different revisions of the same paper** in the
Internet Archive, and citing the wrong one would put an error in the book.

- **Rev 1.0** (SNUG Boston 2006, 40 pp.,
  [captured 2006-11-11](https://web.archive.org/web/20061111005225id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf))
  describes **eight** statement regions. There is no Re-NBA; its Re-Inactive
  iterates directly with Reactive.
- **Rev 1.2** (42 pp.,
  [captured 2009-04-19](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf))
  describes **nine**, adding Re-NBA and formalizing the Active and Reactive
  *region sets*.

The paper documents its own change, which is what makes this citable rather than
guesswork. Its revision history records that in **April 2007** the SystemVerilog
Standards Group updated the event regions and clocking-block behavior under
**Mantis item 890**; that Mantis 890 added the Re-NBA region and formally defined
the Reactive region set as the testbench dual of the RTL Active region set; and
that these were folded into Rev 1.1 (November 2007) and Rev 1.2 (December 2007).
[Cummings and Salz, Rev 1.2, §10.1](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

**Recommendation: cite Rev 1.2 throughout and teach nine regions.** This closes
what would otherwise have been the chapter's one real gap. Rev 1.0 remains worth
one footnote — a paper revised because the language changed under it is a
concrete, honest illustration for a textbook that the scheduling model is a
committee artifact with a history, not a law of nature.

A caution on dating the citation: Rev 1.2 carries the SNUG Boston 2006 venue on
every page but its content is from December 2007. The BibTeX entry in §7 handles
this with a note field. Do not silently date the nine-region model to 2006.

## 3. Delta cycles

**Terminology warning, and it matters for the chapter.** Cummings and Salz do
**not** use the term "delta cycle." Across both revisions the phrase appears
once, in passing, in an aside about non-unit step delays. The concept the
chapter wants is real and well sourced in their text; the *name* is not theirs.
"Delta cycle" is a VHDL term of art that Verilog practitioners borrowed. See §6
— the chapter should either introduce the term explicitly as borrowed, or use
the sourced vocabulary below.

**The sourced version of the concept.** Cummings and Salz state that execution
of the events in a time slot may require **multiple iterations through the event
regions of that same time slot**, and their region descriptions give the
iteration structure concretely:

1. The **Active region set** iterates internally: Active drains, Inactive
   promotes into it, NBA updates land, and NBA updates can retrigger Active
   work — so the set loops until nothing is left in it.
2. **Observed** evaluates assertions on the Preponed values.
3. The **Reactive region set** iterates the same way: Reactive, Re-Inactive,
   Re-NBA, looping until all Reactive-set events are done.
4. If the Reactive set scheduled anything that can trigger Active-set events,
   **the Active set re-triggers and iterates again**, in the same time slot.
5. Only when nothing remains anywhere does Postponed run and time advance.

[Cummings and Salz, Rev 1.2, §2 and §§2.2.2–2.2.11](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

One pass through that loop — evaluate, update, discover that the update woke
something else, go round again, all at the same simulation time — is what the
chapter means by a delta cycle. It is *not* a unit of time. Two events in
different delta cycles at the same timestep are ordered relative to each other
but are simultaneous as far as `$time` is concerned. This is the single most
useful thing the chapter can teach here, because it explains why a waveform
viewer shows two "simultaneous" values and why `$display` and `$strobe` disagree
(§2.2).

**How a design loops forever without advancing time.** The mechanism follows
from the loop above: if the work done in one iteration always schedules more
work *in the same time slot*, the simulator never reaches the condition — no
events remain — that lets time advance. It is not hung in the operating-system
sense; it is making progress through delta cycles forever. Cummings' related
discussion of self-triggering `always` blocks in the NBA paper is the best
sourced entry point: he explains that a blocking assignment evaluates its
right-hand side and updates its left-hand side without interruption, so the
assignment completes before the `@(clk)` trigger event could be scheduled, and
therefore an oscillator written with blocking assignments cannot trigger itself
— whereas the non-blocking version *can*, because the update is deferred to a
later region and so is still pending when the sensitivity is evaluated.
[Cummings, SNUG San Jose 2000, §7 "Self-triggering always blocks"](https://web.archive.org/web/20061111004954id_/http://www.sunburst-design.com/papers/CummingsSNUG2000SJ_NBA.pdf)
**[primary]**

This is an unusually good worked example for the chapter: a two-line clock
oscillator whose behavior — dead, or a zero-delay infinite loop — flips entirely
on the choice of `=` versus `<=`, with the region model as the only explanation.
**Verify the loop behavior in a real simulator before asserting it**, per §8.

## 4. Races, and the guidelines derived from the regions

### 4.1 What a race is, and the two kinds

Cummings and Salz define a race condition as a flaw characterized by an output
that shows an unexpected dependence on the relative timing or ordering of
events, and note the term comes from the image of two signals racing to
influence an output first. They then draw the distinction the chapter needs:

- **Hardware races** are intrinsic to the physics — finite gate delays mean an
  output may transiently take an unwanted value before settling. Usually
  harmless except on a clock or asynchronous reset. Their example is the classic
  NAND S-R latch: drive both inputs to 0, both outputs are forced to 1,
  overriding the latching action; on release, whichever input stays at 1 longer
  wins, and if both release simultaneously the final state is unpredictable.
- **Simulation-induced races** are *not* intrinsic to the design. They are a
  consequence of the event-driven algorithm: the simulator processes events one
  at a time and so unavoidably serializes events in the same time slot, turning
  concurrent hardware activity into an ordered sequence.

[Cummings and Salz, Rev 1.2, §2.1](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

Two sentences from that section deserve to shape the chapter's framing. First,
the danger is asymmetric: such a race can make the simulator show a fault in a
correct design, or — **more dangerously**, in the authors' words — show a
correct result for a design that is actually flawed. Second, the reason the
language deliberately leaves ordering arbitrary: because designers'
code unwittingly comes to rely on a particular ordering, Verilog specifies that
a region is processed in **arbitrary** order, while every real implementation
exhibits *some* definite order. That is the sharpest available statement of why
"it works on my simulator" is not evidence, and it belongs in a Pitfall callout.

### 4.2 The three race cases the chapter needs

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
This is the pipeline case, and it is the best example in the literature because
the *same* code is correct or incorrect depending only on assignment operator.
Cummings gives a three-stage shift register written four ways with blocking
assignments — including two variants where the three assignments live in three
separate `always @(posedge clk)` blocks, ordered `q1,q2,q3` in one and
`q2,q3,q1` in the other. Because Verilog may execute `always` blocks in any
order, these simulate differently from each other while both synthesize to the
same correct pipeline — a pre- versus post-synthesis mismatch. Rewritten with
non-blocking assignments, *all four orderings* simulate correctly and synthesize
correctly. → **Guidelines #1, #2, #4.**
[Cummings, 2000, §§9–12](https://web.archive.org/web/20061111004954id_/http://www.sunburst-design.com/papers/CummingsSNUG2000SJ_NBA.pdf)
**[primary]**

**(c) The testbench/design read-write race at a clock edge.** This is what the
verification regions exist to solve, and §2.1's isolation mechanism is the
answer: a program block's drives are non-blocking and land in Re-NBA, its own
variables are blocking but invisible to the design, and all program processes
complete before the Active set is re-entered. The chapter should present (c) as
the case that *cannot* be fixed by assignment discipline alone — it needed new
regions — which is exactly why the 2005/2007 revisions happened.

### 4.3 The derivation: each guideline from a region

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

**The derivation the chapter asked for is made explicitly, in two places, and
both should be cited.**

*First,* Cummings states the intent directly in the 2000 paper: the event queues
"will also be referenced to justify the eight coding guidelines," and he tells
readers new to Verilog to memorize the guidelines until the underlying
functionality is understood. The whole paper is structured as queue-based
justification.
[Cummings, 2000, §§5–6](https://web.archive.org/web/20061111004954id_/http://www.sunburst-design.com/papers/CummingsSNUG2000SJ_NBA.pdf)
**[primary]**

*Second,* and more usefully for this chapter, the 2006/2007 paper performs the
derivation **region by region** — each region's description names the guideline
it implies. This is the passage to build the chapter's centerpiece table on:

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

### 4.4 Why `#0` is the fix that is not a fix

Both papers are emphatic and their reasoning is explicit, so this needs no
speculation.

From the 2000 paper: making `#0`-delay assignments is *generally a flawed
practice* employed by designers trying to assign the same variable from two
separate procedural blocks, attempting to beat a race by scheduling one
assignment slightly later in the same time step. It needlessly complicates
analysis of scheduled events, and the author says he knows of **no** condition
requiring a `#0` assignment that could not be replaced by a different and more
efficient coding style.
[Cummings, 2000, §6](https://web.archive.org/web/20061111004954id_/http://www.sunburst-design.com/papers/CummingsSNUG2000SJ_NBA.pdf)
**[primary]**

From the 2006/2007 paper, sharper: most engineers who keep using `#0` are trying
to defeat a race that exists because they assign the same variable from more
than one `always` block — **which is already a violation of guideline #6.** The
authors then delete the Inactive region from the rest of the paper's scheduling
diagrams, on the grounds that engineers following good practice never populate
it (the region still exists; it is simply never used).
[Cummings and Salz, Rev 1.2, §2.2.4](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

That is the chapter's line, and it is a genuinely good one: **`#0` does not
remove the race, it renames it.** The race was "which of two blocks goes first
in Active"; `#0` makes it "which of two blocks goes first in Inactive." Ordering
within a region is still arbitrary. The only thing that changes is that the bug
is now harder to see.

A historical footnote the authors supply, which is worth keeping because it
explains why `#0` exists at all: the Inactive region was necessary in the early
days of Verilog, **before the NBA region was added** — they date that to around
1989 — and proper use of NBA makes it unnecessary. So `#0` is a workaround that
outlived its problem.
[Cummings and Salz, Rev 1.2, §2.2.4 n.2](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

Note the important asymmetry, already covered in §2.1: this condemnation is
about **RTL**. A `#0` in a *program* process, landing in Re-Inactive, is
described as often useful and harmless. The chapter must not flatten this into
"never use `#0`."

## 5. Historical grounding

The event-driven algorithm is decades older than SystemVerilog, and two
peer-reviewed citations are enough to establish it. Both were confirmed through
Crossref with DOIs, so the bibliography entries are solid even though the full
texts sit behind publisher paywalls (the chapter cites them for the *existence
and date* of the technique, not for quoted content).

**Selective trace.** E. G. Ulrich, "Exclusive simulation of activity in digital
networks," *Communications of the ACM* 12(2):102–110, February 1969.
[DOI 10.1145/362848.362870](https://doi.org/10.1145/362848.362870) **[research]**
This is the canonical early statement of the idea that a simulator should
evaluate only the parts of a network where activity is actually occurring,
rather than sweeping every element every timestep. That is precisely the
economic argument behind the event queue, and it lets the chapter say the
event-driven model is a 1960s algorithm rather than a language feature — with a
date and a DOI behind it.

**Table-driven, time-based logic simulation.** S. A. Szygenda and E. W.
Thompson, "Digital Logic Simulation in a Time-Based, Table-Driven Environment,"
*Computer* 8(3), March 1975 — Part 1, pp. 24–36,
[DOI 10.1109/c-m.1975.218898](https://doi.org/10.1109/c-m.1975.218898); Part 2
(Thompson and Szygenda), pp. 38–49,
[DOI 10.1109/c-m.1975.218900](https://doi.org/10.1109/c-m.1975.218900).
**[research]**
A two-part account of how production logic simulators were actually built around
a time-ordered event structure, a decade before Verilog. Useful as the second
citation showing this was engineering practice, not just a proposal.

The chapter's claim should be modest and is fully supported by these two: **the
scheduling regions are a standardization of a long-established algorithm, not an
invention of the language.** SystemVerilog's contribution was to specify
*ordering* precisely enough to make races avoidable — which is Cummings and
Salz's own FAQ #2 answer, that the events were already being scheduled this way
and the standard merely defined where.
[Cummings and Salz, Rev 1.2, FAQ #2](https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf)
**[primary]**

## 6. Commonly repeated but unsourced claims

| Claim | Where repeated | Status |
|---|---|---|
| "A delta cycle is …" as standard Verilog vocabulary | Ubiquitous in blogs, forum answers and training material | **Not sourced from the Verilog/SystemVerilog literature examined.** Cummings and Salz never use the term for this concept; they say "iterations" through the regions. "Delta cycle" is a VHDL term of art. The chapter should introduce it explicitly as borrowed from VHDL, or teach "iteration within a time slot" and mention the borrowed name once. Do **not** present it as SystemVerilog terminology. |
| "The standard requires the regions to execute in this order" | Everywhere | **Forbidden phrasing for this book.** The ordering is real, but attribute it to Cummings and Salz's account. Say "SystemVerilog schedules …", never "the standard requires …". |
| The definition of *simulation time* | Cummings and Salz quote it | Their quoted definition is from a **draft of the standard** (their ref. [9]). Do not reuse their quotation. The chapter must state the idea in its own words. Their definition of *timestep* is their own and is safe to attribute to them. |
| "Following the guidelines eliminates 90–100% of Verilog race conditions" | `cummings2000nba`, repeated by the 2006/2007 paper | **Sourced, but it is the author's own estimate, not a measurement.** No study is cited. If the chapter uses the figure, attribute it explicitly to Cummings as an estimate; do not present it as a measured result. |
| Guideline #5 (don't mix blocking and non-blocking in one block) follows from a specific region | Implied in summaries of the guidelines | **Weakly sourced.** The region-by-region derivation covers #1, #2, #3, #4, #6, #7, #8; #5 is best presented as a corollary of #1 and #3. Do not claim a source derives it from a region. |
| "`#0` is always wrong" | Common shorthand | **Overstated.** True for RTL (guideline #8); the same authors call `#0` in a program process useful and harmless. Keep the distinction. |
| Named simulator behavior ("VCS does X, Questa does Y" at a given region) | Forum lore | **No source found and none sought.** Vendor-specific ordering claims must not appear. The relevant sourced point is the opposite: ordering within a region is arbitrary, and relying on any observed order is the bug. |
| A design "hangs" on a zero-delay loop | Common phrasing | Mechanism is sourced (§3); the *word* is misleading. Prefer "loops forever without advancing simulation time." Behavior should be confirmed in a real simulator before the chapter asserts what the user sees. |

## 7. Suggested BibTeX keys

| Key | Full citation | Used by |
|---|---|---|
| `cummingssalz2007events` | Clifford E. Cummings and Arturo Salz, "SystemVerilog Event Regions, Race Avoidance & Guidelines," SNUG Boston 2006 (Synopsys Users Group Conference, Boston, MA), Rev 1.2, December 2007. 42 pp. Sunburst Design, Inc. and Synopsys. URL: `http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf`; archived at `https://web.archive.org/web/20090419050008id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf`. Accessed 2026-09-08. **Note field must record: presented SNUG Boston 2006; Rev 1.2 (December 2007) adds the Re-NBA region per Mantis 890.** | §§1, 2, 3, 4, 5 — the chapter's spine |
| `cummingssalz2006events` | Same authors and title, **Rev 1.0**, SNUG Boston 2006, 40 pp. Archived at `https://web.archive.org/web/20061111005225id_/http://www.sunburst-design.com/papers/CummingsSNUG2006Boston_SystemVerilog_Events.pdf`. Accessed 2026-09-08. | §2.4 only, for the eight-region footnote. Optional — omit if the chapter does not tell the revision story. |
| `cummings2000nba` | **Already in `refs.bib`.** Clifford E. Cummings, "Nonblocking Assignments in Verilog Synthesis, Coding Styles That Kill!," SNUG San Jose 2000, Rev 1.2. | §§3, 4.2, 4.3, 4.4 — the eight guidelines and the race examples |
| `cummings2002nbadelays` | Clifford E. Cummings, "Verilog Nonblocking Assignments With Delays, Myths & Mysteries," SNUG Boston 2002. `http://www.sunburst-design.com/papers/CummingsSNUG2002Boston_NBAwithDelays.pdf`. **Not retrieved for this note** (Archive rate-limiting); listed because both papers above cite it as the source of worked cases behind guidelines #2 and #4. Retrieve before citing. | §4.3, if the chapter expands #2/#4 |
| `ulrich1969selective` | E. G. Ulrich, "Exclusive simulation of activity in digital networks," *Communications of the ACM*, 12(2):102–110, February 1969. DOI 10.1145/362848.362870. | §5 |
| `szygenda1975timebased` | S. A. Szygenda and E. W. Thompson, "Digital Logic Simulation in a Time-Based, Table-Driven Environment. Part 1," *Computer*, 8(3):24–36, March 1975. DOI 10.1109/c-m.1975.218898. (Part 2, Thompson and Szygenda, 8(3):38–49, DOI 10.1109/c-m.1975.218900 — separate key `thompson1975timebased2` if both are cited.) | §5 |

Style note: existing Sunburst entries in `refs.bib` are `@inproceedings` with the
canonical `sunburst-design.com` URL. Those URLs are now login-walled. Consider
adding the archive URL in a `note` field across all Sunburst entries rather than
replacing the canonical URL — a repo-wide decision worth raising, since
`cummings2000nba`, `cummings2008cdc` and the others have the same problem.

## 8. Confidence notes and gaps

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
3. **The zero-delay infinite-loop example is not verified.** The mechanism is
   sourced; the observable behavior is not. Build it under `examples/` and run
   it before the chapter describes what the user sees. This is also the right
   thing to do under the house rule that simulator output comes from `run.out`.
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
