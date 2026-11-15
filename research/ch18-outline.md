# Outline: Formal Property Verification

Date: 2026-11-15. Status: outline for gate 1. Evidence:
`research/ch18-formal-property-verification.md` (cited below as RN
with a question, measurement, source-row, constraint or pitfall
number: Q1 to Q9, M1 to M14, 2.x, 4.1(n), P1 to P22) and the tool
survey `research/informal-measurements/FINDINGS.md` (FM). Chapter
file `chapters/ch18-formal-property-verification.qmd`, label
`{#sec-ch18}`; second chapter of the proof part, after
`chapters/ch17-logic-and-solvers.qmd`. Design doc section 4, entry
18: "bounded model checking, k-induction, IC3/PDR at reading level,
assumptions and over-constraint, covers and vacuity, liveness and
fairness; three reference tables (SVA forms, shell commands, engine
selection); on InFormal, the author's open formal tool, pinned by
commit".

## 0. The chapter in one paragraph

Chapter 9 printed four report rows for one true property of the
repaired FIFO (`undetermined` by bounded search, `undetermined` by
induction, `proven` once a second property was assumed, `proven` by
IC3 with no help) and gave the reason in a paragraph. Chapter 17
ended on "a bound is not a proof". This chapter opens the engines.
On a FIFO of two entries, small enough that all 32 states fit in one
picture, the reader's own scripts (Chapter 17's unroller and solver,
about 370 more lines) show the induction step fail and print the
unreachable state it started from; show it succeed at k = 7 once
repeated states are forbidden, and why that is no way to work; show
one hand-written helper make the step pass at once; and show a
160-line IC3 arrive at that same helper by itself, as six clauses,
whose allowed states are exactly the reachable ones. The same
property is then given to the tool at 4, 8 and 64 entries, where the
verdict rows change in the way the small picture predicts. The second
half is what decides whether a `proven` means anything: assumptions
as constraints and what an over-constraint does to each engine,
covers as reachability and as the vacuity check, and liveness with
its lasso and its fairness assumption. It closes with a measured
engine guide, a worked proof at 64 entries, and three reference
tables generated from runs.

Every number is from a cited paper or from an example's `run.out`.
No new dependency: Python and `informal`; the Python examples need
no tool (their models are checked in), the tool examples skip where
the tool is absent.

## 1. Decisions taken in this outline (and those left to the author)

| decision | basis |
|---|---|
| The spine is one property (`empty |-> wr_ptr == rd_ptr`) on one design at one parameter, through every engine | RN Q1, Q5: the same design shows induction failing, the helper, IC3 succeeding, and each engine losing at some size |
| The chapter ships three teaching programs: a transition-system library, k-induction (plain and simple-path), IC3; all on Chapter 17's `cdcl.py`, unchanged | RN Q2, M10 to M12: feasible (69, 161 and 139 lines), fuzzed on 2,913 systems with no wrong answer |
| Teaching runs stay at two entries (IC3 also at four); nothing larger in pure Python | RN P19 |
| The tool's answers are shown as report rows, one engine per `prove`; its internals are shown only where it prints them | RN Q3, M9, 4.1(4), 4.1(7) |
| A row that ends at the time limit is worded "did not finish in N s", and the limit is printed in the output | RN 4.1(5), M14 |
| One helper invariant only; assumption, cover, fairness each as the reader's tool for reading a verdict, not as a technique catalog | RN Q9; the next chapter owns the catalog |
| Chapter 9's material is cited by label and not re-run: the reset trap, the delayed contradiction (`vacuity-formal`), the dropped immediate assertions, the tool-kind table `@tbl-ch09-formal-tools` | Chapter 9 as drafted; RN P16 |
| Interpolation is one paragraph of history with no run | RN 2.4, 4.1(10) |
| No two-clock example | RN M8 (three modeling traps, nothing for engine selection) |
| Engine guide from in-house engines; an external engine appears only in a captioned table of dated measurements | RN Q8, section 5.1 option (a) |
| Liveness examples hold one liveness property per session and select `informal-ic3` | RN M6, M7, P11, P12 |
| Epigraph is the book's own sentence | RN 4.1(1): no checked quotation exists |

**Left to the author (RN section 5).** (5.1) whether the book's
engine list and CI gain rIC3; this outline assumes not, and if it is
added, `scaling/`, `engine-guide/` and `fifo-64/` each gain a column
and nothing else moves. (5.2) times in the engine table: assumed as
verdict and "within the limit / not", seconds in a captioned table.
(5.3) whether the chapter keeps its own engines; assumed yes. One
more, smaller: the comparison with other tools (section 3.11) has
almost nothing sourced for the three commercial tools beyond what
`@tbl-ch09-formal-tools` already says (RN 2.10); this outline gives
them one shared column of labelled vendor statements and asks whether
the author would sooner drop them from this chapter's table.

## 2. Front matter

**Epigraph (own words; drafter may improve):**
> A counterexample is a fact about the design. A proof is a fact
> about the design, the assumptions, and the question.

**Learning objectives.** After this chapter you can:

1. say what a safety property asks of a design's state graph, and
   place reachable states, the property, and an inductive invariant
   in one picture;
2. say what a bounded search establishes and what it leaves open,
   and read a depth, a bound and `undetermined` in a report without
   over-reading any of them;
3. write the base case and the step case of k-induction, read a
   counterexample to induction, and tell a property that is false
   from one that is true and not inductive;
4. strengthen a property with a helper invariant, and list what the
   proof then rests on;
5. follow IC3 on a small design: frames, the three queries, blocking
   and generalizing a state, propagation, the fixed point; and check
   the invariant it returns with three satisfiability queries;
6. state what an assumption does to every engine's question, detect
   an over-constraint, and say why the same over-constraint reads
   `proven` under one engine and `undetermined` under another;
7. use covers as reachability questions, and a witness cover per
   property as the vacuity check;
8. read a liveness counterexample as a lasso, write the fairness
   assumption that removes an unfair one, and say what the bounded
   rewrite of the property promises that the eventual form does not;
9. choose an engine for a property from what kind of answer is
   expected, and look up in three tables what the tool accepts, what
   each shell command does, and which engine answered what.

Word budget for title, epigraph and objectives: 250.

## 3. Sections

Budgets sum to 12,600 words (band 11,000 to 13,000). "Reader can" is
the gate-1 outcome. Example paths are under
`examples/ch18-formal-property-verification/`. Figures are written
by `figures/gen_ch18_figures.py`, one function per figure, each
reading an example's `run.out` or a checked-in model; at most
1000 px wide; the palette of `figures/blocks.py`. One new helper is
needed: a grid of state cells with per-cell class (reachable, allowed
by the property, bad, allowed by a frame), used by four figures.

### 3.1 Motivation: four rows nobody opened (~500 words)

- **Content.** The four blocks of
  `examples/ch09-temporal-properties/fifo-proof/run.out` for
  `EmptyPtrs_A` (spliced by include, not re-run): bounded search and
  induction `undetermined`, induction `proven` with `CountPtrs`
  assumed, IC3 `proven` alone. Chapter 9 could not show what happened
  inside, because the shell prints no bound, no k and no invariant
  (`@sec-ch09-formal`). Chapter 17's last sentence. What the chapter
  will do: make the reader produce each of the four rows on a model
  of five state bits, and then predict the rows at 64 entries.
- **Reader can:** say which of the four rows is a statement about
  the design and which is a statement about the engine.
- **Splices:** the Chapter 9 `run.out`; nothing new.
- **Figure `fig-ch18-map`:** the chapter's map: one question (can a
  bad state be reached?) and three ways of answering (search
  forward to a bound; show that no step leaves the property;
  build a set that contains the reachable states and no bad one),
  with the engine names of the tool under each. `blocks.py`.
- **Sources:** `@sec-ch09-example`, `@sec-ch17-example`.
- **Constraints:** RN 4.1(5): the Chapter 9 rows are at that
  example's limit; say "did not finish in the limit set there".

### 3.2 States, reachability and invariants {#sec-ch18-reach} (~800 words)

- **Content.** A design under a clock is the three formulas of
  `@sec-ch17-example` (initial, step, bad). The state graph;
  reachable states; a safety property as a set of states that must
  contain the reachable ones; a counterexample as a path. Done by
  brute force on the two-entry FIFO: 5 state bits, 32 states, 22
  reachable (16 are the reset cycle, 6 after reset), 2 bad, the rest
  allowed by the property and never reached. The deepest reachable
  state and the longest shortest path (the diameter), printed by the
  same enumeration. Then the two words the rest of the chapter needs:
  an *invariant* (holds in every reachable state) and an *inductive
  invariant* (holds initially, and no step leaves it). Every proof
  engine of the chapter is a way of finding an inductive invariant
  inside the property; enumeration is the one that does not scale (2
  to the 146 states for the FIFO of the first chapter before
  reduction; arithmetic, not a run).
- **Definition callouts (2):** reachable state, diameter; invariant,
  inductive invariant.
- **Reader can:** enumerate the reachable states of a three-register
  design by hand; say of a given set of states whether it is an
  invariant, inductive, both or neither.
- **Example `reach/`** (python, no tool): `run_reach.py` uses
  `common/ts.py` (`explicit`) on `common/fifo_ptrs2.aag`; prints the
  model line, the counts (32 / 22 / 16 + 6 / 2 bad), the six
  post-reset states by name, the depth of the deepest one, and for
  three candidate sets (the property; the helper; the reachable set)
  the answers to "contains the initial states / closed under a step
  / excludes bad".
- **Figure `fig-ch18-sets`:** the 16 post-reset states as a 4 x 4
  grid (`count` against the pointer pair), each cell classed
  reachable / allowed by the property / bad, with the step edges
  among reachable states. Generated from `reach/run.out`. This grid
  returns in 3.4, 3.5 and 3.6.
- **Sources:** `@sec-ch17-example` (the three formulas); Clarke and
  Emerson 1981 and Queille and Sifakis 1982 for "model checking", one
  sentence at title level (RN 2.1).
- **Constraints:** RN P1 (latch order established by the sidecar
  file, with a check line that fails if it changes); RN 4.1(11) (the
  diameter is computed here, attributed to nobody); RN P22 (the
  six states, depth 4, at most 3 steps between any two).

### 3.3 Bounded model checking as a method {#sec-ch18-bmc} (~800 words)

- **Content.** Chapter 17 built the query; this section is about what
  the answer is worth. (a) A counterexample is final: found at depth
  17, 65 and 129 on a counter whose bug is placed at a chosen depth,
  and the time grows faster than the depth (the unrolling of
  `@sec-ch17-example` gets longer and each bound re-asks). (b) On a
  true property a bounded search ends at the time limit with
  `undetermined` and the report does not say how far it looked. (c)
  How far is far enough: the diameter of 3.2 would do, and for the
  five-bit model it is a small number the reader has just computed;
  for a real design nobody can compute it, and a bound chosen by
  feel is a statement about the search. The honest sentence for a
  bounded result ("no counterexample of up to k cycles after reset,
  and the deepest cover of the property set was reached at depth
  c"), which 3.9 completes. (d) Depth as reported: the shortest by
  `informal-bmc`; the stepped engines report a depth at or beyond it.
- **Definition callout:** bounded proof (and "completeness
  threshold" as the name used in the literature, with its source).
- **Pitfall callout:** `undetermined` after a bounded search is not
  "probably true"; the same row is printed for a bug one cycle beyond
  where the search stopped.
- **In Practice callout:** where the tool says how deep a search
  went: the engine child process, documented in the tool's
  `docs/engines.md`, prints the bound reached; shown once (3.7).
- **Reader can:** state a bounded result in one sentence that claims
  no more than it shows; predict the depth of a counterexample for a
  counter bug; say why doubling the limit does not double the bound.
- **Example `bmc-depth/`** (informal): `deep.sv` (from
  `research/ch18-measurements/deep.sv`), `bmc_depth.tcl`:
  `informal-bmc` with `BUG` = 16, 64, 128 (expected `cex` at depth
  17, 65, 129; the 128 row is new and must be timed), `informal-bmc-10`
  on `BUG` = 64 (a depth at or beyond 65; the script prints "not
  below 65", not the number, RN P4), and the true property
  `count != 16'hFFFF` with enable tied low, limit 5 s
  (`undetermined`). About 7 s.
- **Figure:** none (the chapter table of dated seconds from RN M1
  carries the growth: 0.02 s, 0.18 s, 3.6 s, none in 20 s; caption
  with tool version, machine class, date).
- **Sources:** Biere et al. 1999 (`biere1999symbolic`); Clarke,
  Kroening, Ouaknine and Strichman 2004 for the term (RN 2.2).
- **Constraints:** RN 4.1(5), 4.1(11); RN M1 ("do not give an
  exponent"); RN M2 (the bound reached in a fixed time differs from
  run to run and never enters a `run.out`).

### 3.4 Induction {#sec-ch18-induction} (~1,400 words)

- **Content.** The idea in one line: if the property holds in the
  reset state, and no step leads from a state where it holds to one
  where it fails, it holds for ever, and both halves are single
  satisfiability questions about one copy of the logic. Base case
  and step case written as formulas over Chapter 17's frames; the
  step case has **no reset** in it, which is the whole difficulty:
  it starts from any state that satisfies the property, reachable or
  not. Run on the two-entry FIFO: base unsatisfiable, step
  satisfiable, and the model of the step case is a path the reader
  can decode: it starts in `count = 3` with both pointers at 1, a
  state outside the reachable six, and one push takes it to "empty
  with the pointers apart". That path is a *counterexample to
  induction*: not a bug, a state the engine could not rule out.
  Placed on the grid of 3.2. Then k: assume the property for k
  consecutive states. On this design it does not help at any k tried
  (the unreachable states form a loop the path can walk for as long
  as it likes: the printed path at k = 3 visits one state twice).
  The repair: require the states of the step case to differ
  pairwise. Now the step case is unsatisfiable at k = 7, and the
  method is complete on any finite design, since a path without
  repeats cannot be longer than the number of states. The price: 16
  solver calls and k = 7 for five state bits; no answer in two
  minutes for eight; and the tool's own induction engine, on its own
  model, 0.02 s at two entries, 11 s at four, no answer at eight
  (dated table). Completeness is not practicality. What does work is
  3.5.
- **Definition callouts (2):** k-induction (base case, step case);
  counterexample to induction.
- **Pitfall callout:** three different things print as "no verdict"
  or "step failed": the property is false and the bug is deeper than
  the base case went; the property is true and not inductive; the
  limit was too short. Only the first is about the design. The
  counterexample to induction tells them apart: ask whether its
  first state is reachable (a cover, 3.9).
- **Reader can:** write both cases for a given small design; decode
  a step-case model and say whether its first state is reachable;
  explain why the unique-states constraint makes the method complete
  and why that does not make it fast.
- **Example `kind/`** (python, no tool): `kind.py` (spliced whole,
  69 lines), `common/ts.py` (spliced in part: `Frame`, `solve`),
  `run_kind.py`: plain induction for k = 0 to 8 on
  `fifo_ptrs2.aag` (one line per k: base UNSAT, step SAT, first state
  of the path), the k = 3 path decoded by name in both forms, the
  simple-path run (proven at k = 7, 16 queries), and Chapter 17's
  bugged `fifo_bmc.aag` to show the base case catching a real bug at
  its depth. Under 2 s.
- **Figure `fig-ch18-cti`:** the grid of 3.2 with the two decoded
  paths drawn on it (plain: the revisited state marked; simple:
  four distinct states), from `kind/run.out`.
- **Sources:** Sheeran, Singh and Stalmarck 2000, sections 2 to 4
  (the unique-states constraint and the completeness remark); Een
  and Sorensson 2003 for the incremental form, at title level unless
  its body is read (RN 2.3).
- **Constraints:** RN 4.1(2), 4.1(3), 4.1(4) (the script's k is not
  the tool's bound; print neither as the other), 4.1(5); RN M10
  (plain k from 1 on starts at `count = 3`; k = 0 starts elsewhere);
  formulas are the chapter's own, checked against the script.

### 3.5 Strengthening by hand: one helper {#sec-ch18-helper} (~600 words)

- **Content.** The counterexample to induction names what is
  missing: nothing told the engine that `count` and the pointers move
  together. Say it as a second property (`count[0] == wr_ptr ^
  rd_ptr` at this size; Chapter 9's `CountPtrs_A` in general). Three
  runs: the helper alone is inductive (step unsatisfiable at k = 1);
  with the helper as a constraint, the original property needs no
  step at all (every state that satisfies the helper satisfies it);
  the conjunction is an inductive invariant in the sense of 3.2, and
  the grid shows it: the helper's states are a strict subset of the
  property's that still contains the reachable six. What the proof
  now rests on, as a list the reader keeps: the helper was proved,
  not only assumed; it was proved without assuming the property it
  helps; the tool does not reuse a proved assertion by itself, so
  the move from `assert` to `assume` is the engineer's and goes in
  the proof's record. One helper is all this chapter writes; finding
  them for real designs is the next chapter.
- **Definition callout:** helper invariant (strengthening).
- **Reader can:** read a counterexample to induction and propose a
  helper that excludes its first state; state the two obligations a
  helper brings.
- **Example `helper/`** (python, no tool): `run_helper.py` on
  `common/count_ptrs2.aag` (helper alone: proven at k = 1) and
  `common/fifo_ptrs4_h.aag` (property with the helper as constraint:
  step unsatisfiable at k = 0), plus the three set-questions of
  `reach/` for the conjunction. Under 1 s.
- **Figure:** the helper's region added to the grid, as a second
  panel of `fig-ch18-cti`.
- **Sources:** `@sec-ch09-example` for the property pair; no
  external claim.
- **Constraints:** RN P9 (a proven assertion is not reused; FM A.4);
  RN Q9 (one helper, no method).

### 3.6 Strengthening by machine: IC3 {#sec-ch18-ic3} (~1,800 words)

- **Content.** The question IC3 asks in place of "is the property
  inductive": *which* states must be excluded for it to become so,
  found one state at a time and generalized. The parts, each on the
  two-entry FIFO with the script's printed trace beside it:
  1. *Frames.* F0 is reset; Fi is a set of clauses that every state
     reachable in at most i steps satisfies. Four properties hold
     throughout (reset inside F0; each frame inside the next; every
     frame inside the property; one step from Fi lands in Fi+1).
  2. *Three questions,* each one copy of the logic (never an
     unrolling): is there a bad state in the last frame; does this
     state have a predecessor in the frame below; does this clause
     survive one more step.
  3. *Blocking.* A bad state in the last frame becomes a proof
     obligation (state, frame). If it has a predecessor one frame
     down, that is a new obligation; if a chain of obligations
     reaches F0, the chain is a counterexample; if it has none, the
     state is excluded by a clause.
  4. *Generalization.* The clause is shortened literal by literal
     while it still has no predecessor and does not cut into reset:
     one excluded state becomes a whole region. This is where "never
     `count = 3`" appears, from one state.
  5. *Propagation and the fixed point.* Clauses that also hold one
     frame up are moved up; when a frame hands all its clauses on,
     two frames are equal, and that frame is an inductive invariant.
  6. *The result.* After five frames, six clauses; decoded, one is
     "never `count = 3`", four are `count[0] == wr_ptr ^ rd_ptr`,
     one is subsumed: **the helper of 3.5, found by the machine, as
     clauses.** The states they allow are exactly the 22 reachable
     ones. The invariant is checked by three fresh queries
     (contains reset, closed under a step, excludes bad), which is a
     certificate anyone can re-check without trusting the search.
  Then the other verdict: on Chapter 17's bugged FIFO the chain of
  obligations is the depth-16 counterexample. Then scale, honestly:
  6, 32 and 213 clauses at 2, 4 and 8 entries: the helper is one
  arithmetic relation, and IC3 has to assemble it from clauses over
  single bits. That sentence explains both directions of the engine
  table in 3.11. What the 160 lines leave out and production engines
  have, named with one clause each: shrinking a predecessor before
  blocking it (ternary simulation or unsat cores), re-queueing an
  obligation at the next frame, incremental solving, subsumption.
  History in one paragraph: interpolation (McMillan 2003) as the
  first SAT-based engine that learned an over-approximation from a
  refutation; IC3 (Bradley 2011) doing it without unrolling; PDR as
  the name and the simpler implementation (Een, Mishchenko and
  Brayton 2011) from which the vocabulary used here comes.
- **Definition callouts (3):** frame; cube, lemma and proof
  obligation; relative induction (a clause is inductive relative to
  a frame).
- **In Practice callout:** an IC3 counterexample is not always the
  shortest, and the engine prints nothing while it works; what a
  user sees is a verdict or a limit.
- **Reader can:** given a frame sequence and a bad state, carry out
  one blocking step by hand (predecessor query, clause, one
  generalization); check a proposed invariant with the three
  queries; say what "frames 5, lemmas 6" in a statistics line means.
- **Examples.**
  - `ic3/` (python, no tool): `ic3.py` (spliced in four parts:
    queries, `block`, `generalize`, `propagate`/`run`),
    `run_ic3.py`: the full trace on `fifo_ptrs2.aag` (each
    obligation, each clause before and after generalization, frame
    sizes after each frontier), the six lemmas decoded by name, "the
    lemmas allow 22 states; 22 are reachable; equal sets", the three
    certificate checks; `counter.aag` and `fifo_bmc.aag` of Chapter
    17 (cex depth 6; cex depth 16); `fifo_ptrs4.aag` summary line
    only (11 frames, 32 lemmas). About 3 s.
  - `ic3-fuzz/` (python, no tool): `fuzz.py` capped (150 random
    systems of 2 to 6 latches, fixed seed) against `explicit`;
    prints counts of proven / cex / disagreements (0) and the deepest
    counterexample and largest invariant. To be timed; target under
    45 s; cut the case count until it is.
- **Figures.** `fig-ch18-frames`: the grid of 3.2 drawn once per
  frontier (five small panels), each frame's allowed region shaded,
  from the trace in `ic3/run.out`. `fig-ch18-lemmas`: the six lemmas
  as excluded regions on the grid, beside the helper's region: the
  same picture twice.
- **Sources:** Bradley 2011 sections 3 and 4; Een, Mishchenko and
  Brayton 2011 section III; McMillan 2003; Bradley and Manna 2007 at
  title level (RN 2.4, 2.5).
- **Constraints:** RN 4.1(1), 4.1(2), 4.1(6), 4.1(7), 4.1(10); RN
  M11 (what the prototype has and lacks, to be stated); RN P19, P20
  (sizes fixed under the book's Python; scripts sort every iterated
  set); query counts in `run.out` include the certificate's and the
  text must say so.

### 3.7 What the tool shows of all this {#sec-ch18-trust} (~400 words)

- **Content.** The same property through the tool, small: verdict
  rows at two and four entries by induction and by IC3. What the
  tool's documents say it does before printing a verdict (an
  invariant re-checked by three fresh queries, an induction proof by
  its base and step, a counterexample by simulation; a verdict that
  fails the check is withdrawn), cited to the pinned file. What can
  be seen: with the documented statistics switch, one line with
  frames, lemmas and queries and one with the certificate check;
  from the engine child, the last bound before the verdict. Two
  cautions in the text: the tool's model is not the script's (its
  own reset and history state), so its counts are of the same order
  and not the same; and its bound is not the script's k.
- **Reader can:** find, for a `proven` row, what was checked and by
  what; say why the tool's "lemmas 15" and the script's 6 do not
  contradict each other.
- **Example `engine-view/`** (informal): `view.tcl` (two and four
  entries, `informal-kind` then `informal-ic3`, limit 5 s; the
  induction row at four entries is expected `undetermined` at this
  limit and the output says "limit 5 s"), `view.sh` (the statistics
  line filtered to frames/lemmas/queries and `certificate: Ok`; the
  engine child's last bound at two entries). **Condition:** three
  consecutive runs identical before the `run.out` is fixed; any
  field that moves is dropped from the output (RN P17, P18). About
  6 s.
- **Sources:** the tool's `docs/engines.md` ("Verdict trust") and
  `README.md`, pinned; Yu, Biere and Heljanko 2021 at title level
  for certificate formats.
- **Constraints:** RN 4.1(4), 4.1(7), 4.1(14) (both halves: checked
  before reporting; no certificate file in a competition format).

### 3.8 Assumptions are part of the question {#sec-ch18-assume} (~900 words)

- **Content.** Where an assumption goes: it is a constraint on every
  step of every query the engines above ask (each frame of the
  unrolling, both cases of induction, every one of IC3's three
  questions), so the "reachable set" becomes "reachable while the
  environment keeps its promise". Chapter 9 showed assumptions on an
  interface and the contradiction that takes a tick to bite
  (`@sec-ch09-vacuity`, by label; not repeated). Three things are
  new here, on a request/grant block with a 200-cycle timer:
  (a) an over-constraint that is not a contradiction: `assume
  !req` leaves plenty of traces and turns a false assertion (`cex`
  at depth 202 without it) into `proven`; (b) the report offers no
  defense: assumptions are listed `unprocessed`, nothing checks them;
  (c) the engine changes what the mistake looks like: under a
  proving engine the vacuous assertions are `proven`, under bounded
  search alone they are `undetermined`, because a search for traces
  that finds none cannot say there are none. The discipline that
  follows, as a list: every assumption is a claim about another
  block, to be proved there or checked in simulation (the same text
  as an `assert`, as Chapter 9's bind files do); every proof is
  re-read with its witness covers (3.9); an assumption on an internal
  signal or an output is a cut of the design, which is a technique
  and belongs to the next chapter.
- **Definition callout:** over-constraint.
- **Pitfall callout:** `cover {1'b1}` as a "sanity check of the
  assumptions" passes on an environment that dies in its second
  cycle (measured in Chapter 9 and again here); it detects only an
  environment with no first cycle.
- **Reader can:** say what set of traces a given assumption removes;
  predict the report rows for an over-constrained run under a
  proving engine and under bounded search; list what must be recorded
  for each assumption.
- **Example `over-constraint/`** (informal): `handshake.sv`,
  `assume.tcl` (from `research/ch18-measurements/`): four blocks
  under `informal-ic3` (no assumption; `!req`; `d < 8` with `d > 9`;
  `req` with `busy |-> !req`), then the last block under
  `informal-bmc` with a 2 s limit. Expected rows as RN M5's table.
  About 12 s.
- **Figure:** none; the `run.out` is the exhibit.
- **Sources:** `@sec-ch09-vacuity`, `@sec-ch09-where`; Beer et al.
  2001 and Kupferman and Vardi as cited in Chapter 9 (RN 2.7).
- **Constraints:** RN P6, P7, P8, P21; RN 4.1(8); nothing here on
  assume-guarantee as a method (section 6).

### 3.9 Covers: reachability, and the check on every proof {#sec-ch18-cover} (~700 words)

- **Content.** A cover is the reachability question asked the other
  way round, and its two answers are different kinds of object.
  `covered` is a trace, and any engine that searches finds it, with
  a depth. `unreachable` is a proof (of the negated cover) and needs
  a proving engine; bounded search alone reports `undetermined`.
  Three uses, each tied to an earlier section: (1) the witness cover
  of a property (its antecedent, or the event it talks about)
  re-run under the proof's assumptions is the vacuity check of 3.8;
  (2) a cover of the first state of a counterexample to induction
  tells "false" from "not inductive" (3.4); (3) the depth of the
  deepest cover of interest is the least bound at which a bounded
  result means anything: Chapter 9's "the FIFO can fill" is covered
  at depth 17, so a bounded search to depth 10 has not seen a full
  FIFO. And the case that pays for the habit: on the first chapter's
  FIFO the same cover is `unreachable`, which is the bug, found
  without writing the assertion that catches it.
- **Definition callout:** witness cover.
- **Reader can:** predict which engines can return each of the two
  answers; write the witness cover for an implication; state a
  bounded result together with the cover depth that qualifies it.
- **Example `cover-engines/`** (informal): `cover.tcl` (from
  `research/ch18-measurements/`): `fifo.u_sva.FullReached_C` alone,
  on the original and the repaired FIFO, under `informal-bmc` (limit
  5 s), `informal-kind`, `informal-ic3`. Expected: original `-`
  (undetermined) / unreachable / unreachable; repaired covered at
  depth 17 three times. About 7 s.
- **Figure `fig-ch18-cover`:** a two-by-two of answer kind (trace /
  proof) against property kind (assert / cover): `cex` and `covered`
  are traces, `proven` and `unreachable` are proofs; under each, the
  engines that returned it in the chapter's runs. Generated from the
  `run.out` files of `cover-engines/` and `engine-guide/`.
- **Sources:** `@sec-ch09-vacuity`; `@sec-ch09-example`.
- **Constraints:** RN P5 (full hierarchical name with `prove
  -property`; the others print as `unprocessed`); RN M4.

### 3.10 Liveness and fairness {#sec-ch18-liveness} (~1,200 words)

- **Content.** Everything so far was "nothing bad happens", refuted
  by a finite path. "Something good eventually happens" cannot be
  refuted by a finite path (the good thing might be next); its
  counterexample is a path that goes round for ever without it: a
  stem and a loop, a *lasso* (safety and liveness by label from
  `@sec-ch09-what`; Alpern and Schneider once). On a four-state
  requester whose `stall` input can hold it in one state: `req && n
  == 0 |-> s_eventually gnt` is refuted, and the trace's first line
  names the frames that repeat; the table is read row by row, with
  the one trap marked: the loop is closed by equal *states*, and the
  inputs printed in the last row are not part of it. How an engine
  for safety finds a loop: give the design a shadow copy of its
  registers, a free choice of the moment to save the state into it,
  and a flag for "the awaited event has happened since"; "back in
  the saved state with the flag down" is then a bad state like any
  other, and every engine of this chapter applies (Biere, Artho and
  Schuppan 2002; the tool's shell document says this is what it
  does). The cost is visible in the construction: the state bits
  double. Then the reading of the counterexample: is the loop
  something the environment may do? Holding `stall` for ever is not
  a design bug. *Fairness* is the assumption that rules such loops
  out, written `assume {s_eventually !stall}`; under it the property
  is proved. Finally the engineer's alternative: replace "eventually"
  by "within four cycles". That is a safety property, any engine
  handles it, and it is a different promise: fairness does not prove
  it (it is refuted at depth 5 under the fairness assumption, since
  "eventually not stalled" allows a stall of five), and a bounded
  environment assumption (`stall |=> !stall`) proves both forms. The
  two-row table of which assumption proves which form is the
  section's summary. One sentence that other reductions exist
  (counting recurrences; Claessen and Sorensson 2012).
- **Definition callouts (2):** lasso; fairness assumption.
- **Pitfall callout:** a liveness proof under a fairness assumption
  the environment does not keep, and a bounded property proved under
  an environment bound nobody checked, are both over-constraints of
  3.8; and keep one liveness property to a session, because other
  properties' bookkeeping state lengthens the loop that is printed.
- **In Practice callout:** at the commit the book pins, select
  `informal-ic3` for a liveness property: in the chapter's runs the
  other in-house engines found the lasso and did not finish the
  proofs within the limit, and external engines are not run on
  liveness (the tool's shell document).
- **Reader can:** read a lasso and say which input choice sustains
  the loop; decide whether a loop is unfair and write the fairness
  assumption; choose between the eventual and the bounded form and
  say what each needs from the environment.
- **Examples.**
  - `lasso/` (informal): `live_small.sv`, `live_alone.tcl` (from
    `research/ch18-measurements/`): one property, `informal-bmc`;
    `cex ... depth 4`, the trace's comment line and the five-row
    table as in RN M6. Under 1 s.
  - `fairness/` (informal): four sessions, one property each:
    eventual form under no assumption / fairness / bounded
    environment with `informal-ic3`; bounded form (`##[1:4] gnt`)
    under the same three with `informal-kind`. Expected from RN M7:
    cex, proven, proven; cex depth 5, cex depth 5, proven. **To be
    re-measured in this one-property form** (RN M7 ran three
    properties in a session; depths of the eventual form's lasso
    will be 4, not 7). No `undetermined` row; about 2 s.
- **Figure `fig-ch18-lasso`:** left, the trace of `lasso/run.out` as
  stem and loop over the four states; right, the shadow-register
  construction (design, saved copy, save choice, flag, the new bad
  condition), with `hw.py` registers.
- **Sources:** Alpern and Schneider 1985; Biere, Artho and Schuppan
  2002 sections 1 to 3; Claessen and Sorensson 2012 (abstract
  level); the tool's `docs/fpv-shell.md`, pinned (RN 2.6).
- **Constraints:** RN 4.1(12); RN P10, P11, P12; strong and weak
  fairness are not distinguished unless a source is read (RN 2.6);
  the number of state bits with and without the reduction is given
  only if `informal info` on the dumped model prints it (to be
  tried; otherwise "doubles" stays a statement about the
  construction).

### 3.11 Choosing an engine {#sec-ch18-engines} (~700 words)

- **Content.** The guide as questions about the expected answer, not
  about engine names. Is a trace expected (a bug, a reachable
  cover)? Bounded search first: it was fastest or equal on every such
  row. Is a proof expected of something that is plainly a one-step
  fact (a flag follows a counter, a handshake holds its value)?
  Induction. Is a proof expected of something that depends on which
  states are reachable (the pointer property; the three "address
  stable while waiting" rules of Chapter 11's DMA, which induction
  did not finish and IC3 did)? IC3. Liveness: IC3 here. Then what to
  do with `undetermined`: change the engine before raising the
  limit; ask for the cover that would settle which of the three
  causes of 3.4 it is; then help the engine (next chapter). Why the
  default is a portfolio, and why the book's scripts select one
  engine all the same (a race is not repeatable). The generated
  table `tbl-ch18-engines` (3.13) is referred to here; a second,
  captioned table gives this chapter's dated seconds, including one
  external engine the tool can call (RN M1, M3: it alone finished the
  64-entry proof and the 1,025-step bug within 20 s), marked as a
  measurement outside the book's examples. A third, short table
  `tbl-ch18-tools` places the vocabulary beside other tools: InFormal
  (measured), SymbiYosys (its documentation: modes `bmc`, `prove`,
  `cover`, `live`; a `depth` option that is the bound in `bmc` and
  the induction depth in `prove`; engines chosen per task), and the
  commercial tools in one column of statements from their product
  pages, labelled as vendor statements, with "not stated on the page
  read" where that is the case.
- **Pitfall callout:** an engine table is a table of measurements on
  named designs. The same design gave "induction wins" and "IC3
  wins" for two properties a line apart.
- **Reader can:** pick the first engine for a property from the kind
  of answer expected; say what to try, in order, after
  `undetermined`.
- **Example `engine-guide/`** (informal): `guide.tcl` runs seven
  situations under `informal-bmc`, `informal-kind`, `informal-ic3`,
  limit 4 s: shallow bug (`deep.sv`, `BUG` = 16); deeper bug (`BUG`
  = 64); one-step fact (`CountPtrs_A`, 8 entries); reachability
  fact (`EmptyPtrs_A`, 8 entries); reachable cover and unreachable
  cover (`FullReached_C`); liveness under fairness; a real design's
  rule (`ArStable_A` of the DMA). `guide.py` reduces the reports to
  `tbl-engines.md`. Expected `undetermined` cells: bounded search on
  the five proof rows, induction on the reachability fact, the
  liveness proof and the DMA rule: eight cells, about 32 s; 35 s in
  all.
- **Figure `fig-ch18-choose`:** the decision path above as a flow,
  each leaf carrying the row of `tbl-engines.md` that supports it
  (leaf labels read from the generated table, so a changed verdict
  breaks the figure's build rather than leaving it stale).
- **Sources:** RN M1, M3, M4, M7, M8 via the examples; SymbiYosys
  documentation; vendor pages (RN 2.10); the tool's `docs/engines.md`
  for the portfolio.
- **Constraints:** RN 4.1(5), 4.1(6), 4.1(8), 4.1(9); RN P13
  (`set_engine_mode` in the command table only, no engine letters
  explained); RN section 5.1, 5.2.

### 3.12 Worked example: the pointer property at 64 entries {#sec-ch18-example} (~900 words)

- **Content.** The chapter's steps as one procedure on a design size
  where no in-house engine proves the property unaided within the
  limit. (1) Covers first: the FIFO can fill and can drain (depths
  reported). (2) Bounded search for bugs: none within the limit, and
  the sentence that result supports. (3) Induction: `did not finish
  in 5 s`. Which of the three causes? (4) IC3: also not within the
  limit, where at 8 entries it took a quarter of a second: the
  clause count of 3.6 at work. (5) The helper, from the
  counterexample to induction the reader saw at two entries; proved
  by induction at once at every size. (6) The helper assumed: the
  property is proved by each engine in a few hundredths of a second.
  (7) The witness covers again under the assumption: still reached.
  (8) The record: what was proved, by which engine, under which
  assumptions, each assumption with where it is discharged, each
  cover with its depth; the limits that ended without a verdict and
  what was done about them. The scaling picture closes it: verdicts
  by size and engine at 2, 4, 8 and 64 entries, and the one row
  that stays green at every size is "with the helper". That row is
  the reason for the next chapter.
- **Worked Example callout:** the eight steps as a numbered recipe.
- **Reader can:** take a true property from `undetermined` to
  `proven` on a design of their own and write the record that goes
  with the proof.
- **Examples.**
  - `fifo-64/` (informal): `fifo64.tcl`, the repaired FIFO with
    `DEPTH = 64`, `WIDTH = 1`, the steps above as blocks, limit 5 s,
    `informal-kind` and `informal-ic3`. Expected: two `undetermined`
    rows (`EmptyPtrs_A` under each), `CountPtrs_A` proven by
    induction, `EmptyPtrs_A` proven with the helper assumed; covers
    and their depths **to be measured** at this size (a fill cover
    at depth 65 by the pattern of depth 17 at 16 entries; say
    nothing until run). About 12 s.
  - `scaling/` (informal): `scaling.tcl` with `DEPTH` = 2, 4, 8, 64,
    two properties, two engines, plus the helper-assumed row, limit
    5 s; `scaling.py` prints the grid. Expected `undetermined`:
    induction on `EmptyPtrs_A` at 4, 8, 64; IC3 on both properties
    at 64: five cells, about 27 s. (RN M14 planned depths 2, 4, 16,
    64; 16 is replaced by 8 because IC3 took 2.7 s there, too close
    to a 5 s limit on a loaded machine.)
- **Figure `fig-ch18-scale`:** the grid of `scaling/run.out`: size
  across, property-and-engine down, cells proven / not within 5 s,
  the helper-assumed row beneath.
- **Sources:** RN M3, M14; `@sec-ch09-example`.
- **Constraints:** RN 4.1(5) (the induction row at 4 entries is a
  proof at 11 s and `undetermined` at 5 s: the output prints the
  limit and the prose says "in 5 s"); RN 4.1(6); RN P9.

### 3.13 Reference {#sec-ch18-reference} (~400 words of prose around three generated tables)

Each table is a Markdown file written by its example's `run` step
and included in the chapter by
`{{< include /examples/ch18-formal-property-verification/<dir>/<file>.md >}}`,
as Chapter 9's `support-matrix/matrix.md` and Chapter 17's
`production/tbl-*.md` are. The `run.out` of each example is the
table's rows in plain text, so the regression check covers the
table. Nothing in a table is typed by hand except the fixed
"construct" or "command" label of each probe, which lives in the
probe list.

- **`tbl-ch18-sva`: property forms the formal tool accepts.**
  `sva-forms/`: `probe.sv` and `forms.tcl` grown from
  `research/informal-measurements/forms/` (55 forms, FM D.1), one
  probe per form with a design on which the form is true and one on
  which it is false; `forms.py` writes `tbl-sva.md` with columns
  *form*, *accepted* (yes / refused, with the tool's message cut to
  a fixed width / dropped without a message), *verdict where true*,
  *verdict where false*, *note* (liveness; needs `informal-ic3`).
  Row groups: boolean and sampled-value functions; implication and
  delay; repetition; sequence operators; `until` family, `nexttime`,
  bounded `always` and `s_eventually`; unbounded `s_eventually`;
  `disable iff` and default clocking; where a property may live
  (module, bound checker, shell command; FM D.2); immediate and
  deferred assertions (dropped: RN P16). A check line compares the
  *accepted* column with the InFormal column of Chapter 9's
  `matrix.md` for the constructs both list and fails on a
  difference. Limit 3 s per property, `informal-kind` except the
  liveness rows. Time to be measured; the FM run of 55 forms took
  seconds.
- **`tbl-ch18-shell`: shell commands.** `shell-commands/`:
  `commands.tcl` uses each command of the tool's `docs/fpv-shell.md`
  once, with the variants measured in RN M13 (`set_prove_time_limit`
  forms; `set_engine_mode` with one letter set; `prove -all`,
  `-property`; `assert`/`assume`/`cover` with `-name`, `-disable`
  where the shell has them). `commands.sh` runs `informal shell
  --check` on it (which reports per line what is honoured, rejected
  or ignored) and then the script itself; `commands.py` joins the
  two into `tbl-shell.md`: *command*, *status from `--check`*,
  *measured effect* (a fixed phrase chosen by the script from the
  report: "verdict rows printed", "property listed as disabled",
  "error: bad time unit", and so on). The `set_engine_mode` row
  records that a set was selected and prints no verdict rows (a
  race: RN P13).
- **`tbl-ch18-engines`: engine selection.** `engine-guide/` of 3.11:
  `tbl-engines.md`, rows the seven situations, columns the three
  in-house engines, cells the verdict with depth where there is one,
  or "no verdict in 4 s"; a last column "first choice", computed
  (the engines that answered; among them the one the guide's rule
  names), not typed.

Reader can: find in under a minute whether a form is accepted, what
a command does, and which engine answered a kind of question.
Constraints: RN Q7; RN 4.1(5); the tables carry the tool version and
commit in their captions; times appear in none of them.

### 3.14 Future directions (~250 words; one Future Directions callout)

Labelled as open or recent, no result claimed: certificates as a
required output (mandatory in the bit-level tracks of the 2024
hardware model checking competition, RN 2.9) and what it would mean
for a sign-off record to carry a checkable invariant; word-level
IC3 that learns the arithmetic relation as one fact instead of 213
clauses (named as a research direction, no tool claim); liveness
engines beyond the reduction shown; abstraction refinement as the
automatic version of the next chapter's manual techniques (Clarke
et al. 2000, one sentence, forward pointer). One sentence pointing
at the book's last part for learned invariants, with no claim.

### 3.15 Summary (~300 words)

Nine bullets mirroring the objectives, each with its measured fact
(22 of 32 states; a bug at depth 129 and a true property with no
bound reported; step fails from `count = 3`; k = 7 with unique
states; six clauses equal to the helper; a false assertion `proven`
under `!req`; `unreachable` needs a prover; a lasso of depth 4 and
the fairness assumption; the engine table), and the picture of 3.2
once more with all three regions.

### 3.16 Exercises (~550 words; list in section 5 below)

### 3.17 Further reading (~150 words)

Names, authors, editions only: Bradley 2011; Een, Mishchenko and
Brayton 2011; Sheeran, Singh and Stalmarck 2000; Biere, Artho and
Schuppan 2002; Biere and Kroening, "SAT-Based Model Checking", in
the *Handbook of Model Checking*; Seligman, Schubert and Kumar,
*Formal Verification: An Essential Toolkit for Modern VLSI Design*,
2nd ed. (for practice at industrial scale; edition verified, text
not: no paraphrase); "Understanding IC3" and the standard texts only
after their records are checked (RN 2.11).

### Budget

| section | words |
|---|---|
| title, epigraph, objectives | 250 |
| 3.1 motivation | 500 |
| 3.2 states, reachability, invariants | 800 |
| 3.3 bounded model checking | 800 |
| 3.4 induction | 1,400 |
| 3.5 helper | 600 |
| 3.6 IC3 | 1,800 |
| 3.7 what the tool shows | 400 |
| 3.8 assumptions | 900 |
| 3.9 covers | 700 |
| 3.10 liveness and fairness | 1,200 |
| 3.11 choosing an engine | 700 |
| 3.12 worked example | 900 |
| 3.13 reference tables (prose) | 400 |
| 3.14 future, 3.15 summary, 3.16 exercises, 3.17 further reading | 250 + 300 + 550 + 150 = 1,250 |
| **total** | **12,600** |

Callout census (six kinds only): Definition x 13 (two each in 3.2,
3.4, 3.10; three in 3.6; one each in 3.3, 3.5, 3.8, 3.9); Pitfall x
5 (3.3, 3.4, 3.8, 3.10, 3.11); In Practice x 3 (3.3, 3.6, 3.10);
Worked Example x 1 (3.12); Future Directions x 1; Exercise x 1.
Thirteen definitions is high: if the draft runs long, "bounded
proof" and "witness cover" become defined terms in running text.

## 4. Example directories

All under `examples/ch18-formal-property-verification/`. Python
files at most 80 columns; every example has `lint` (byte-compile, or
Verilator on the `.sv`) and `run`; `run.out` is written by
`scripts/check-examples.sh`; `EXPECT_OUTPUT` names a line only a
real run prints. Tool examples set `EXAMPLE_LANG := informal`,
`REQUIRES := informal`, and select one engine per `prove` with
`informal::set_engines`. Chapter 17's `cdcl/cdcl.py` and
`common/aiger.py` are imported by path, not copied. Research
prototypes are in `research/ch18-measurements/` (`teach/` for the
Python, the `.tcl` and `.sv` files beside it); they are the starting
point, not the final text: each needs the 80-column pass, names by
sidecar file, and the output format fixed.

| directory | language | needs | files | `run.out` (expected, from RN) | time |
|---|---|---|---|---|---|
| `common/` | python | — | `ts.py`; checked-in models `fifo_ptrs2.aag`, `count_ptrs2.aag`, `fifo_ptrs4.aag`, `fifo_ptrs4_h.aag`, each with a `.names` sidecar; wrappers `fifo_ptrs2.sv`, `fifo_ptrs4.sv` | (library; no run) | — |
| `models/` | informal | `informal` | `run_models.sh`: `informal lower`, `simp --aag` on the wrappers; compares with the checked-in files | `aag 48 3 5 0 40 1 1` for two entries; "equal to the checked-in model" per file | 2 s |
| `reach/` | python | — | `run_reach.py` | 32 states, 22 reachable (16 + 6), 2 bad; six states by name; deepest state's depth (from the run); three candidate sets with three yes/no each | < 1 s |
| `bmc-depth/` | informal | `informal` | `deep.sv`, `bmc_depth.tcl` | `cex informal-bmc depth 17`, `65`, `129`; stepped engine "not below 65"; `undetermined` at "limit 5 s" | 7 s |
| `kind/` | python | — | `kind.py`, `run_kind.py` | k = 0 to 8: base UNSAT, step SAT, first state; k = 3 paths decoded (RN M10); simple path: proven at k = 7, 16 queries; `fifo_bmc.aag`: base case SAT at its depth | 2 s |
| `helper/` | python | — | `run_helper.py` | helper alone: proven at k = 1; property with helper as constraint: step UNSAT at k = 0; conjunction: contains reset, closed, excludes bad | < 1 s |
| `ic3/` | python | — | `ic3.py`, `run_ic3.py` | trace; frame sizes as RN M11; six lemmas decoded; "22 allowed, 22 reachable, equal"; checks `(True, True, True)`; `counter.aag` cex depth 6; `fifo_bmc.aag` cex depth 16; four entries: 11 frames, 32 lemmas | 3 s |
| `ic3-fuzz/` | python | — | `fuzz.py` | "150 systems: N proven, M counterexamples, 0 disagreements" plus deepest and largest (from the run) | to be timed, target < 45 s |
| `engine-view/` | informal | `informal` | `view.tcl`, `view.sh` | four report rows; statistics fields that repeat; last bound at two entries (6) | 6 s |
| `over-constraint/` | informal | `informal` | `handshake.sv`, `assume.tcl` | five blocks as RN M5's table | 12 s |
| `cover-engines/` | informal | `informal` | `cover.tcl` (uses Chapter 9's FIFO, checker and bind files by path) | original: undetermined / unreachable / unreachable; repaired: covered depth 17 x 3 | 7 s |
| `lasso/` | informal | `informal` | `live_small.sv`, `live_alone.tcl` | `cex informal-bmc depth 4`; the comment line; five-row table | 1 s |
| `fairness/` | informal | `informal` | `fair.tcl` | six one-property sessions; verdicts as 3.10 (re-measure) | 2 s |
| `engine-guide/` | informal | `informal` | `guide.tcl`, `guide.py`, writes `tbl-engines.md` | seven rows by three engines | 35 s |
| `fifo-64/` | informal | `informal` | `fifo64.tcl` | the eight steps' rows (cover depths to be measured) | 12 s |
| `scaling/` | informal | `informal` | `scaling.tcl`, `scaling.py` | grid of four sizes | 27 s |
| `sva-forms/` | informal | `informal` | `probe.sv`, `forms.tcl`, `forms.py`, writes `tbl-sva.md` | one row per form | to be timed |
| `shell-commands/` | informal | `informal` | `commands.tcl`, `commands.sh`, `commands.py`, writes `tbl-shell.md` | one row per command | to be timed |

Eighteen directories, seventeen with a run; six need only Python.
About two and a half minutes in all, none over a minute; the three
longest are limits (`engine-guide/`, `scaling/`, `ic3-fuzz/`).

To be measured again because the example form differs from the
research form: `bmc-depth/` at 128; `fairness/` in one-property
sessions; `fifo-64/` covers; `engine-view/` repeatability;
`scaling/` at a 5 s limit (the research run used 20 s); `ic3-fuzz/`
case count against time; every script's output layout; the deepest
state and diameter printed by `reach/`.

## 5. Exercises (each has one determinate answer; solutions go to the solutions appendix)

1. **Count the picture.** From `reach/run.out`: of the 16 states
   after the reset cycle, how many are reachable, how many are bad,
   and how many satisfy the property without being reachable? *(6,
   2, 8.)* Which of the three kinds can be the first state of a
   counterexample to induction? *(Only the third.)*
2. **Which check fails?** Take the property itself as a candidate
   inductive invariant of the two-entry FIFO. Which of the three
   checks of 3.6 fails, and what is the witness? *(Closed under a
   step fails; the witness is the counterexample to induction of
   `kind/run.out` at k = 0.)* Which fails for the candidate "the six
   reachable post-reset states plus one bad state"? *(Excludes bad.)*
3. **Read a failing step.** In the plain path at k = 3 printed by
   `kind/run.out`, which two steps are the same state? *(Steps 0 and
   2.)* Which of the six IC3 lemmas excludes that state? *(The
   first: never `count = 3`.)*
4. **Why some k must work.** With the unique-states constraint the
   two-entry model is proved at k = 7. Give a k, from the model size
   alone, at which the step case must be unsatisfiable for any true
   property of this model. *(31: a path of pairwise different states
   has at most 32 states.)* Why is that bound useless at 146 state
   bits?
5. **Decode the invariant.** Rewrite the six lemmas of `ic3/run.out`
   as two SystemVerilog expressions and name the lemma that adds
   nothing. *(`count != 3` and `count[0] == (wr_ptr ^ rd_ptr)`; the
   fourth is subsumed by the second.)* How many of the 16 post-reset
   states do the two expressions allow? *(6.)*
6. **One blocking step.** Given the frame sizes after the first
   frontier in `ic3/run.out` and the bad state `wr_ptr = 0, rd_ptr =
   1, count = 0`, say which query IC3 asks next and what each of its
   two answers leads to. *(Predecessor in the frame below: a model
   becomes a new obligation one frame down; unsatisfiable lets the
   state be excluded and generalized.)*
7. **A bound and a depth.** `deep.sv` with `BUG = 100`: at what
   depth does `informal-bmc` report the counterexample? *(101.)* May
   `informal-bmc-10` report 101? May it report 100? *(It may report
   101 or more; never less: no shorter trace exists.)*
8. **Over-constraint.** In `over-constraint/run.out`, under `assume
   !req`, which rows show that `a_false` is proved vacuously, and
   which row does not? *(The two covers `c_gnt` and `c_busy` are
   unreachable; `c_true` is covered.)* Why is the last block
   `undetermined` where the one before it says `proven`?
9. **Trace or proof.** For each of `cex`, `proven`, `covered`,
   `unreachable`, say whether a bounded search can return it and
   cite the row of `cover-engines/run.out` or `engine-guide/run.out`
   that shows it. *(Yes, no, yes, no.)*
10. **Two promises.** Using `fairness/run.out`: under `assume
    {s_eventually !stall}`, is `##[1:4] gnt` proved? *(No: refuted
    at depth 5.)* Give the stall pattern that satisfies the fairness
    assumption and violates the bounded property *(stall held for at
    least four cycles and then released)*, and the assumption that
    proves both forms *(`stall |=> !stall`)*.
11. **Read a lasso.** In `lasso/run.out`, which frames repeat, which
    input value sustains the loop, and in which row is it printed?
    *(The state of frame 3 recurs at frame 4; `stall = 1`; row 3,
    not the last row.)*
12. **Pick the engine.** For each property say which engine you try
    first and what bounded search alone would print: (a) a cover you
    believe reachable; (b) `count <= DEPTH`; (c) "the address is
    stable while VALID waits"; (d) a cover you believe unreachable;
    (e) `req |-> s_eventually gnt` under fairness. *((a) bounded
    search, `covered`; (b) induction, `undetermined`; (c) IC3,
    `undetermined`; (d) a proving engine, `undetermined`; (e)
    `informal-ic3`, `undetermined`; each by a row of
    `tbl-ch18-engines`.)*

Answers that cite a `run.out` are fixed when the examples are
written; (b) of exercise 12 needs the `engine-guide/` row for a
one-step fact to be the one it cites. Exercise 7's 101 follows from
the design (shortest trace is `BUG` enabled steps after the reset
cycle) and is confirmed by a run before the solutions appendix
records it.

## 6. Deliberately left to later chapters

**To Formal Techniques (the catalog of 31 techniques in six
families):** every way of changing the problem so that an engine
finishes. Finding helper invariants as a method (this chapter
writes one); assume-guarantee and decomposition (this chapter says
only that an assumption is a claim to be discharged elsewhere);
black boxes and cut points (FM C.6), including assumptions on
internal signals; abstraction of counters and memories; symbolic
constants and data independence (FM H); case splitting; property
mutation and formal coverage, cone-of-influence and proof-core
coverage; bounded-proof sign-off criteria beyond the one sentence
of 3.3 and 3.9; reset and initial-value abstraction; liveness
techniques beyond one fairness assumption; abstraction refinement
done by a tool. This chapter hands over three things by label: the
scaling grid of 3.12 as the motive, the counterexample to induction
as the diagnostic every technique starts from, and the proof record
of 3.12 as the place where each technique's side conditions are
written down.

**To Equivalence, Structural and Static Verification:** equivalence
checking as a flow and its commands; sequential equivalence as a
safety property of a product machine (one sentence there can cite
3.4 and 3.6); connectivity, X-propagation, clock-domain and reset
checks; multi-clock formal modeling (RN M8's three traps go there
or to the techniques chapter, not here).

**Already stated earlier and cited by label, not repeated:** SVA
syntax and semantics, vacuity defined, assert/assume/cover roles,
the reset model and its spurious `$past` counterexample, immediate
assertions dropped by the formal tool, the tool-kind table (Chapter
9); CNF, the solver, AIGER and Btor2, the unrolled formula, depth
conventions (Chapter 17).

**Stated here and not again:** reachable set, invariant, inductive
invariant; bounded proof; base and step case, counterexample to
induction, unique-states completeness; frames, lemmas, proof
obligations, generalization, propagation, certificate by three
queries; assumption as constraint, over-constraint; cover as
reachability, witness cover; lasso, liveness-to-safety, fairness;
the three reference tables.

## 7. Gate-1 checklist

| requirement (AGENTS.md) | where met |
|---|---|
| every section names what the reader must be able to do | "Reader can" in 3.1 to 3.13; objectives 1 to 9 map to 3.2, 3.3, 3.4, 3.5, 3.6-3.7, 3.8, 3.9, 3.10, 3.11-3.13 |
| the research note's constraints are folded in | each section's "Constraints" line cites RN 4.1 items and pitfalls; section 1 records the decisions they forced |
| house template | epigraph, objectives, motivation (3.1), concepts (3.2-3.11), worked example (3.12), reference (3.13), callouts (census above, six kinds), future directions, summary, exercises, further reading |
| every listing a file under `examples/` | section 4; no code in prose; tables included from example directories |
| every number sourced | cited paper (RN section 2 status marks) or `run.out` (section 4); seconds only in captioned, dated tables |
| the three reference tables are generated | 3.13: `sva-forms/`, `shell-commands/`, `engine-guide/`, each writing a Markdown file the chapter includes, each with its rows in `run.out` |
| 8 to 12 exercises with determinate answers | section 5: twelve |
| no overlap with Chapters 9 and 17 or with the techniques chapter | section 6; 3.1 and 3.8 cite Chapter 9's runs by label |
| a question that changes the shape is raised, not chosen | RN section 5 and section 1 here: rIC3 in the book's engine list; times in the engine table; keeping the teaching engines; the commercial column |
| new glossary terms for the glossary appendix | reachable state, diameter, invariant, inductive invariant, bounded proof, completeness threshold, k-induction, base case, step case, counterexample to induction, simple path (unique-states) constraint, helper invariant, frame, cube, lemma, proof obligation, relative induction, generalization, propagation, IC3, PDR, interpolant, certificate, over-constraint, witness cover, lasso, liveness-to-safety, fairness, portfolio |
| new `refs.bib` entries (about 14) | Queille and Sifakis 1982; Sheeran, Singh and Stalmarck 2000; Een and Sorensson 2003; McMillan 2003; Bradley 2011; Bradley and Manna 2007; Een, Mishchenko and Brayton 2011; Biere, Artho and Schuppan 2002; Claessen and Sorensson 2012; Clarke, Kroening, Ouaknine and Strichman 2004; Clarke, Grumberg, Jha, Lu and Veith 2000; Yu, Biere and Heljanko 2021; Biere and Kroening 2018; Seligman, Schubert and Kumar (2nd ed.); the 2024 competition report; the rIC3 paper if section 5.1 keeps the captioned table. Add pages 52-71 to `clarke1981modelchecking`. Each author field to be checked against the document where Crossref gave initials (RN 2.x) |

Open items that do not block gate 1 but block specific sentences:
the sources marked [U] in RN section 2 (list in RN 2.11). A sentence
that needs one of them waits until it is read or is cut. No
quotation is planned anywhere in the chapter.
