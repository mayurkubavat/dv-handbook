# Research note: Formal Property Verification (Chapter 18)

Date: 2026-11-15. Status: research for gate 1; the outline is
`research/ch18-outline.md`. Written section by section, the deciding
questions first. Section numbers are fixed (1 questions, 2 sources,
3 measurements, 4 constraints, 5 open questions) but the sections
were written in the order 1, 3, 2, 4, 5, so section 3 stands before
section 2 in the file, as in the note for the chapter before this
one.

Scope given: design doc section 4, entry 18: "bounded model checking,
k-induction, IC3/PDR at reading level, assumptions and over-constraint,
covers and vacuity, liveness and fairness; three reference tables (SVA
forms, shell commands, engine selection); on InFormal, the author's
open formal tool, pinned by commit". The author's instruction for the
two formal chapters: this material "will serve as golden reference for
Formal Verification and techniques". Readers: DV and RTL engineers.

Machine and pins for every measurement below: 4 cores, 15 GB, Ubuntu
24.04; InFormal 0.1.0 at commit `5114330` (`informal --version` prints
`informal 0.1.0`), CaDiCaL linked, Bitwuzla not built; rIC3 1.5.2 as
`ric3` (used for comparison rows only: the book's engine list,
`examples/mk/informal-engines.toml`, is empty, so no book example can
select it); Python 3.13.18; the `z3-solver` package 5.4.1. Experiments
ran in a scratch directory made with `mktemp -d`; every script that
is worth keeping is under `research/ch18-measurements/`, with the
output it printed under `research/ch18-measurements/out/`.

What already exists and is not repeated here: the tool survey in
`research/informal-measurements/FINDINGS.md` (cited as FM with its
section letter), Chapter 9's research note, and Chapter 17's
(`research/ch17-logic-and-solvers.md`).

## 1. The questions that decide the chapter's shape

Each answer names its evidence: a part of section 3 below (M1 to
M14), FM, or a source row of section 2.

### Q1. Chapter 9 already told the FIFO story (induction stuck, helper, IC3). What is left for this chapter?

**The inside of each engine, on the same property, at a size where
every step fits on a page.** Chapter 9 showed four report rows
(`undetermined`, `proven` with the helper assumed, `proven` by IC3)
and said why in one paragraph. It could not show the failing
induction step, the k, or what IC3 "discovers", because the shell
prints none of them (FM C.1 to C.3; Chapter 9 says so in
`@sec-ch09-formal`). This chapter can, with three short Python
programs that extend Chapter 17's unroller and run on the model the
tool itself writes (M10 to M12):

- On the repaired FIFO at `DEPTH = 2` (5 state bits after
  preprocessing) the step case of induction is satisfiable at every
  k tried, and from k = 1 on it starts in `count = 3` with both
  pointers at 1, a state no run reaches (a push from there wraps the
  two-bit count to 0 with the pointers apart); with the constraint
  that the states of the step case differ pairwise it becomes
  unsatisfiable at k = 7, and that is a proof. Sixteen solver calls,
  0.1 s.
- On the same model the chapter's IC3 ends after five frames with
  six lemmas, and they are the helper invariant of Chapter 9 written
  clause by clause: one says "never `count = 3`", four say
  `count[0] == wr_ptr ^ rd_ptr`, one is subsumed. The set of states
  the six lemmas allow is exactly the reachable set: 22 of 32.
- InFormal on the same property (M3): k-induction proves it in
  0.02 s at `DEPTH = 2`, in 11.3 s at 4, and not within 20 s at 8,
  16, 64 or 256; its IC3 proves it up to 16 and not at 64; the helper,
  assumed, makes every engine finish in 0.02 to 0.04 s at every
  depth. So one design, one property and one parameter carry the
  whole comparison of engines, and the reader has seen at depth 2
  what goes wrong at depth 16.

The spine is therefore: **a bound is not a proof (Chapter 17's last
sentence) -> how far must a bound go (diameter; shown, not usable) ->
induction (base, step, the counterexample to induction) -> making it
complete (simple path) and why that is still too slow -> strengthening
by hand (the helper; one, and only one, here) -> strengthening by
machine (IC3) -> the things that are not engines but decide whether a
proof means anything (assumptions, covers, vacuity) -> liveness ->
choosing an engine.** The catalog of proof techniques is the next
chapter's.

### Q2. Is a readable IC3 feasible, and is it correct?

**Yes to both; recommend it.** The prototype
(`research/ch18-measurements/teach/ic3.py`) is 160 lines including
its docstring, about 140 lines of code, on Chapter 17's `cdcl.py`
with no change to that solver: every query is one copy of the logic
plus frame clauses, solved from nothing. It has the three questions
(is a bad state in the frontier; does this cube have a predecessor
in the frame below; does this lemma survive one more step), blocking
with a list of proof obligations, generalization by dropping
literals, propagation with the fixed-point test, a counterexample
trace, and a certificate check by three fresh queries. It has no
lifting (predecessor cubes are whole states), no unsat cores, no
obligation re-queueing and no incremental solving, and the chapter
must say so.

Fuzzed against explicit-state reachability (breadth-first search
over every state and input, no solver) on 2,913 transition systems
with **no disagreement** (M12): 2,529 random systems of 2 to 8
latches (counters, shift registers, held and random next-state
logic, a conjunction as the bad state, a constraint in three of
ten), and all 384 single-edge mutants of three models. For each
`proven` the returned invariant was checked explicitly (contains
every reachable state, closed under a step, excludes bad) and by the
three queries; for each `cex` the trace was replayed and its length
compared with the shortest. Deepest counterexample 182 steps;
largest invariant 74 lemmas; 15 frames at most on the mutants. The
k-induction prototype (plain and simple-path) agreed on its 429
systems as well. Cost: `DEPTH = 2` 0.12 s (160 queries); `DEPTH = 4`
1.7 s (1,531 queries, 32 lemmas); `DEPTH = 8` 34 s (17,803 queries,
213 lemmas), too slow for an example; the first chapter's buggy FIFO
refuted at depth 16 in 1.1 s. A z3 back end was not needed and was
not written.

### Q3. The shell prints no bound and no k. Is there any way to see one from the tool?

**Partly, and it should be shown once.** `informal engine <name>
<model.btor2>` (the child side of `--isolate`; in
`docs/engines.md` of the tool, not in `informal --help`) prints JSON
progress lines with the bound an engine has reached and then the
verdict (M9). On the shell's own model of the pointer property at
`DEPTH = 4` the k-induction engine printed bounds up to 28 before
`{"result":{"verdict":"safe"}}`; at `DEPTH = 2`, bounds 0 and 6.
Which bounds are printed depends on timing, so only the last one
before a verdict is fit for a `run.out`, and that needs the
determinism check of M9. The decision already taken stands: bounded
proof and the failing step are taught by the chapter's own scripts;
the engine child is one In Practice note ("if you need the depth a
search reached, this is where the tool says it").

### Q4. Can the engine-selection guide be measured and not folklore?

**Yes, on five kinds of row, each with one number** (M1 to M8):
a shallow bug (every engine, 0.02 to 0.04 s); a deep bug (BMC cost
grows faster than depth: 0.02 s at 17, 0.18 s at 65, 3.6 s at 257,
none in 20 s at 1,025; the in-house IC3 found depth 257 in 0.8 s);
an inductive property (k-induction 0.02 to 0.06 s at every size,
IC3 slower with size and lost at `DEPTH = 64`); a true property
that is not inductive (the reverse); a cover that is unreachable
(needs a proving engine; BMC alone `undetermined`); liveness
(in-house engines only). The guide is a table generated from those
runs plus the book's two real designs (the FIFO checker and the DMA
with its AXI rules), where every proving engine finishes and the
only lesson is which is fastest. See Q8 for the one thing the
book's own setup cannot show.

### Q5. Is there one design where IC3 struggles and induction wins, and one for the reverse?

**The same design gives both.** `CountPtrs_A` (`count[k-1:0] ==
wr_ptr - rd_ptr`) is inductive at k = 1: k-induction 0.06 s at
`DEPTH = 64`, the in-house IC3 `undetermined` at 20 s (three of its
four variants; `informal-kind-ic3` 11 s). `EmptyPtrs_A` (`empty |->
wr_ptr == rd_ptr`) is true and not inductive: IC3 2.7 s at `DEPTH =
16`, k-induction `undetermined`. The reason is the same in both
directions and is the chapter's best single paragraph: the invariant
is an arithmetic relation; induction checks a relation it is handed
in one query, IC3 has to assemble it from clauses over single bits,
and their number grows with the depth (6, 32, 213 lemmas at depth 2,
4, 8 in the chapter's own IC3).

### Q6. Does liveness work well enough to carry a section?

**Yes, on one four-state design, with one engine, one property per
session.** `s_eventually` under an implication is refuted with a
lasso whose loop the trace names in its first line, is proved under
a fairness assumption (`assume {s_eventually !stall}`) by
`informal-ic3` in 0.08 to 0.10 s, and the bounded rewrite
(`##[1:4] gnt`) is refuted without an environment assumption and
proved with a bounded one (`assume {stall |=> !stall}`) by
k-induction in 0.02 s (M7). Three limits shape the examples:
k-induction and BMC do not finish a true liveness property here in
30 s; rIC3 returns `undetermined` at once on any liveness property;
and a second property in the session changes the lasso (depth 4
alone, depth 7 beside a `##[1:4]` property). Fairness does not
rescue the bounded form, which is a point worth a sentence: the
bounded property is false under fairness, because fairness promises
"eventually" and the property asks for "within four".

### Q7. How are the three reference tables generated and not typed?

- **SVA forms accepted.** From a probe run in the chapter's own
  example directory: one Tcl script that tries each form on a small
  design, catches the rejection text, runs `prove`, and a Python
  script that turns the report into the table. The 55 forms and
  their expected rows exist (FM D.1, `research/informal-measurements/
  forms/`); Chapter 9's `support-matrix` example already has the
  machinery for a subset. The chapter's table is the complete one for
  the formal tool, and it must add the forms FM did not try.
- **Shell commands.** From `informal shell --check` on a script that
  uses every command of the table once (it lists per line what the
  shell honours, rejects or ignores, and exits non-zero on anything
  but "ignored"), plus a real run of the same script for the
  commands whose effect is a verdict. The table's "effect" column is
  the script's printed evidence, row by row.
- **Engine selection.** From `tab.py`-style reduction of one run per
  engine on six situations (M1 to M8). Times do not go into a
  `run.out`; the generated table carries verdicts and "answered
  within the limit / did not", and the seconds appear in a captioned
  chapter table as dated measurements. A three-way class with a
  "slow" band was considered and dropped as unstable under machine
  load. This needs the author's nod: see section 5.2.

### Q8. What can the book's own setup not show?

**rIC3.** The engine list the book's examples use
(`examples/mk/informal-engines.toml`) is empty, so every example is
in-house engines only. In these measurements rIC3 was the only
engine that proved the pointer property at `DEPTH = 64`, the only
one that found the 1,025- and 4,097-step bugs within 20 s, and the
fastest prover on most rows. A measured engine guide without it
understates what "try another engine" can buy; with it, the book's
CI needs one more tool. This is the open question of section 5.

### Q9. Where is the line to the techniques chapter?

**This chapter owns the engines and the four things a reader needs
to read their answers; the next owns every way of changing the
problem.** Here: one helper invariant (because it is what makes
induction's failure and IC3's success one idea), assumptions as
constraints with over-constraint and contradiction measured, covers
as reachability with the witness cover as the vacuity check, and
fairness as the assumption that makes a liveness property provable.
There: black boxes and cut points (FM C.6 stays there), abstraction
of counters and memories, symbolic constants (FM H), case splitting,
assume-guarantee as a method, mutation of the property set, cone-of-
influence coverage. The pointer property's scaling table is shown
here once as a motive for the next chapter ("at 256 entries no
engine finishes without help, and the help is one line") and is not
developed.

## 3. Measurements (run 2026-11-15; section 2, the source table, follows below)

How to read them. Every InFormal script is in
`research/ch18-measurements/` and is run as `./run.sh <script>.tcl`
from that directory (the wrapper sets `BOOK` to the repository root,
uses the engine list `engines.toml` beside it, which adds rIC3 to the
in-house engines, and a fresh temporary work directory). The output
kept is `out/<script>.out`. One engine is selected for each `prove`,
so the engine column says who answered; the limit is per property.
`tab.py out/<file>` reduces an output to the tables below, in which
a cell is a verdict letter and seconds: P proven, C*n* counterexample
at depth *n*, V*n* covered at depth *n*, U unreachable, - undetermined
at the limit. Engine names drop their `informal-` prefix in the
tables. Times are wall-clock on 4 cores; **the two pointer scripts
(M3) ran two at a time and the times in M3 are therefore a little
higher than a quiet machine gives** (FM C.3 has 1.75 s where M3 has
2.71 s); every other script ran alone. Verdicts did not differ
between this run and FM anywhere both measured the same thing.

### M1. A bug at increasing depth (`bmc_depth.tcl`, `deep.sv`; 6 min 51 s, most of it limits)

A 16-bit counter with an enable; the assertion forbids the value
`BUG`, so the shortest counterexample has `BUG` enabled steps after
the reset cycle. Limit 20 s.

| design | property | bmc | bmc-10 | bmc-65 | ric3-bmc | kind | ic3 | ic3-cadical | kind-ic3 | ic3-mt | ric3-ic3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BUG=16 | a_never | C17 0.02 | C17 0.02 | C17 0.02 | C17 0.04 | C17 0.02 | C17 0.02 | C17 0.02 | C17 0.02 | C17 0.04 | C17 0.04 |
| BUG=64 | a_never | C65 0.18 | C66 0.12 | C77 0.26 | C65 0.10 | C65 0.22 | C65 0.08 | C65 0.16 | C65 0.16 | C65 0.08 | C65 0.06 |
| BUG=256 | a_never | C257 3.56 | C259 1.53 | C258 1.51 | C257 1.95 | C257 4.50 | C257 0.84 | C257 6.95 | C257 5.89 | C257 1.92 | C257 0.10 |
| BUG=1024 | a_never | - | - | - | - | - | - | - | - | - | C1025 0.38 |
| BUG=4096 | a_never | - | - | - | - | - | - | - | - | - | C4097 1.25 |

- Every engine finds a bug, not only BMC: the proving engines are
  searches that also end in a counterexample.
- BMC's cost grows faster than the depth: four times the depth costs
  nine times the time from 17 to 65 and twenty times from 65 to 257.
  This is the unrolling of Chapter 17 getting longer; say so, and do
  not give an exponent.
- The stepped engines report depths that are not minimal (66, 77,
  259, 258). Only `informal-bmc` (and the proving engines in this
  table) report the shortest.
- The in-house IC3 on its own small solver found depth 257 four times
  faster than BMC; the same IC3 on CaDiCaL was twice slower than BMC.
  One design: an observation, not a rule.
- On the Chapter 3 design rIC3 reported depth 46 for a counterexample
  every other engine reported at 40 (M8): an IC3 counterexample is
  not always the shortest.

### M2. Bounded model checking on a true property (`fifo_ptr.tcl`, `certify.sh`)

`informal-bmc` on the two true pointer properties: `undetermined`,
`no engine reached a verdict`, after the whole limit, at every depth,
with nothing in the report about how far it looked. The engine child
(M9) says how far: in 3 s it reached bound 909 to 920 at `DEPTH = 2`
and 310 to 321 at `DEPTH = 4` (three runs each; the number differs
from run to run).

### M3. True but not inductive; the helper; IC3; scaling (`fifo_ptr.tcl`, `DEPTH` from the environment)

The repaired FIFO with `WIDTH = 1`. `EmptyPtrs_A`: `empty |-> wr_ptr
== rd_ptr`. `CountPtrs_A`: `count[$clog2(DEPTH)-1:0] == wr_ptr -
rd_ptr`. Third row of each block: `CountPtrs_A` disabled and the same
expression assumed. Limit 20 s. `DEPTH = 2` (from a separate run of
the same properties): kind 0.02 s, IC3 0.02 s.

| design | property | bmc | kind | ic3 | ic3-cadical | kind-ic3 | ic3-mt | ric3-ic3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEPTH=4 | EmptyPtrs_A | - | P 11.32 | P 0.02 | P 0.06 | P 0.06 | P 0.04 | P 0.04 |
| DEPTH=4 | CountPtrs_A | - | P 0.02 | P 0.02 | P 0.06 | P 0.04 | P 0.04 | P 0.04 |
| DEPTH=4, the helper assumed | EmptyPtrs_A |  | P 0.02 | P 0.02 | P 0.02 | P 0.02 | P 0.04 | P 0.02 |
| DEPTH=8 | EmptyPtrs_A | - | - | P 0.24 | P 0.52 | P 0.50 | P 0.16 | P 0.06 |
| DEPTH=8 | CountPtrs_A | - | P 0.02 | P 0.10 | P 0.22 | P 0.36 | P 0.18 | P 0.06 |
| DEPTH=8, the helper assumed | EmptyPtrs_A |  | P 0.02 | P 0.02 | P 0.02 | P 0.02 | P 0.04 | P 0.04 |
| DEPTH=16 | EmptyPtrs_A | - | - | P 2.71 | P 10.65 | P 8.65 | P 3.71 | P 0.39 |
| DEPTH=16 | CountPtrs_A | - | P 0.06 | P 0.99 | P 3.48 | P 2.67 | P 0.91 | P 0.24 |
| DEPTH=16, the helper assumed | EmptyPtrs_A |  | P 0.03 | P 0.02 | P 0.03 | P 0.03 | P 0.04 | P 0.04 |
| DEPTH=64 | EmptyPtrs_A | - | - | - | - | - | - | P 2.03 |
| DEPTH=64 | CountPtrs_A | - | P 0.06 | - | - | P 11.09 | - | P 0.44 |
| DEPTH=64, the helper assumed | EmptyPtrs_A |  | P 0.02 | P 0.02 | P 0.02 | P 0.02 | P 0.04 | P 0.04 |
| DEPTH=256 | EmptyPtrs_A | - | - | - | - | - | - | - |
| DEPTH=256 | CountPtrs_A | - | P 0.06 | - | - | P 11.14 | - | P 1.27 |
| DEPTH=256, the helper assumed | EmptyPtrs_A |  | P 0.02 | P 0.02 | P 0.02 | P 0.02 | P 0.04 | P 0.04 |

Read down a column and across a row:

- k-induction on the property that is not inductive: 0.02 s at depth
  2, 11.3 s at depth 4 (last bound printed by the engine child: 28),
  nothing at 8 and above. The failure appears only as `undetermined`.
- IC3 on it: grows with depth and is lost at 64 for the in-house
  variants, at 256 for rIC3.
- k-induction on the helper: 0.02 to 0.06 s at every depth.
- IC3 on the helper: slower at every depth, lost at 64 for three of
  the four in-house variants; `kind-ic3` proves it in 11 s, which is
  its IC3 share of the budget followed by its induction.
- With the helper assumed every engine answers in 0.02 to 0.04 s at
  every depth, 256 included. This row is the argument for the next
  chapter.
- A proven assertion is not used as a lemma for another (FM A.4):
  `CountPtrs_A` proven in the same `prove -all` does not help
  `EmptyPtrs_A`. The move from assertion to assumption is by hand.

### M4. Covers as reachability (`cover.tcl`; 22 s, 20 of them the one BMC limit)

`FullReached_C` (`occ == 16`) of Chapter 9's checker, alone, on the
original and on the repaired FIFO.

| design | bmc | kind | ic3 | ic3-cadical | kind-ic3 | ic3-mt | ric3-ic3 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| original (cannot fill) | - | U 0.40 | U 0.23 | U 0.40 | U 0.34 | U 0.08 | U 0.04 |
| repaired | V17 0.02 | V17 0.08 | V17 0.22 | V17 0.26 | V17 0.16 | V17 0.04 | V17 0.04 |

`unreachable` is a proof of the negated cover and needs a proving
engine; BMC alone is `undetermined`. `covered` is a trace, and every
engine finds it. With `prove -property <one name>` the table still
lists every property, the others as `unprocessed`; the name must be
the full hierarchical one (`fifo.u_sva.FullReached_C`; the short name
is `no property matches`).

### M5. Assumptions, over-constraint, contradiction (`assume.tcl`, `handshake.sv`; 27 s)

A request/grant block with a 200-cycle timer. `informal-ic3`, then
the last case again under BMC. Properties: `a_gnt_after_busy` (true),
`a_false` (`!gnt`, false), covers `c_gnt`, `c_busy`, `c_true`
(`1'b1`).

| assumptions | a_gnt_after_busy | a_false | c_gnt | c_busy | c_true |
| --- | --- | --- | --- | --- | --- |
| none | proven | cex depth 202 | covered 202 | covered 2 | covered 1 |
| `!req` | proven | **proven** | unreachable | unreachable | covered 1 |
| `d < 8` and `d > 9` | proven | **proven** | unreachable | unreachable | **unreachable** |
| `req` and `busy |-> !req` | proven | **proven** | unreachable | unreachable | covered 1 |
| the same, BMC only, 5 s | undetermined | undetermined | undetermined | undetermined | covered 1 |

- A false assertion is `proven` under each of the three constraint
  sets and nothing in the report says why. Assumptions are listed as
  `assume unprocessed`: they are never checked.
- `cover {1'b1}` detects only the contradiction that kills every
  trace in its first cycle. The third set contradicts itself only in
  the second cycle after a request (the first request sets `busy`,
  and then `req` must be both 1 and 0), so one-cycle traces exist and
  `c_true` is covered at depth 1 while every property that needs a
  second cycle is vacuous. **A cover of "true" is not a sanity check
  of the assumptions; the witness cover of each property is.**
- Under BMC alone the vacuous properties are `undetermined` rather
  than `proven`: the engine that only searches for traces finds
  none, and cannot say that there are none.

### M6. Liveness: the lasso (`live_alone.tcl`, `live_small.sv`; 0.05 s)

One property in the session, `req && n == 2'd0 |-> s_eventually
gnt`, on a four-state design whose `stall` input can hold state 2 for
ever. `cex informal-bmc depth 4`. The trace file's first line and the
table made from it:

```
$comment liveness: frame 4 has the state of frame 3 again; the frames from 3 on repeat for ever $end
cycle    rst    req  stall      n    gnt
    0      1      0      0      0      0
    1      0      1      0      0      0
    2      0      0      0      1      0
    3      0      0      1      2      0
    4      0      0      0      2      0
```

The loop is closed by the *state* of frame 4 equaling that of frame
3. The inputs printed in the last row are not part of the loop (it is
`stall = 1` in frame 3 that holds `n`); a reader who replays row 4's
`stall = 0` leaves the loop. The chapter must say this beside the
table.

### M7. Liveness: fairness, engines, the bounded rewrite (`live.tcl`; 6 min, nearly all of it limits)

Three properties in one session: `a_live` as above, `a_step`
(`n == 1 |-> s_eventually n == 2`, true), `a_bound4` (`req && n == 0
|-> ##[1:4] gnt`). Limit 30 s.

| assumptions | property | bmc | kind | ic3 | kind-ic3 | ic3-mt | ric3-ic3 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| none | a_live | C7 0.02 | C7 0.02 | C7 0.02 | C7 0.09 | C7 0.04 | - |
| none | a_step | - | - | P 0.04 | P 0.12 | P 0.05 | - |
| none | a_bound4 | C5 0.02 | C5 0.02 | C5 0.01 | C5 0.04 | C5 0.04 | C5 0.02 |
| `s_eventually !stall` | a_live | - | - | P 0.08 |  |  |  |
| `s_eventually !stall` | a_step | - | - | P 0.04 |  |  |  |
| `s_eventually !stall` | a_bound4 | C5 0.02 | C5 0.02 | C5 0.02 |  |  |  |
| `stall |=> !stall` | a_live | - | - | P 0.10 |  |  |  |
| `stall |=> !stall` | a_step | - | - | P 0.06 |  |  |  |
| `stall |=> !stall` | a_bound4 | - | P 0.02 | P 0.02 |  |  |  |
| `stall |=> !stall` | a_bound5 | - | P 0.02 | P 0.02 |  |  |  |

- rIC3 gives `undetermined` at once on the two liveness properties
  (wall 45 ms for the three): the tool does not run external engines
  on them, as its shell document says.
- k-induction did not finish either true liveness property in 30 s
  in this session; `informal-ic3` did in under 0.1 s. FM C.7 measured
  10.34 s for k-induction on `a_step` in a session without the
  bounded property. A liveness example selects `informal-ic3`.
- `a_live` is depth 7 here and depth 4 alone (M6): the bounded
  property's cycle counter is part of the state the loop must repeat
  (FM F.4). One liveness property per session in the examples.
- Fairness proves the eventual form and leaves the bounded form
  refuted; the bounded environment assumption proves both. Two
  different promises, and the table shows the difference.

### M8. Engine selection on the book's designs (`engines_book.tcl`, 5 min 56 s; `two_clock.tcl`, 2.7 s)

Limit 20 s; the BMC column's limits are most of the run time.

| design | property | bmc | kind | ic3 | ic3-cadical | kind-ic3 | ic3-mt | ric3-ic3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| repaired FIFO 16 x 8 | NoOverflow_A | - | P 0.66 | P 0.24 | P 0.22 | P 0.16 | P 0.08 | P 0.06 |
| repaired FIFO 16 x 8 | FullForward_A | - | P 2.98 | P 0.34 | P 0.60 | P 0.42 | P 0.06 | P 0.04 |
| repaired FIFO 16 x 8 | FullBackward_A | - | P 2.54 | P 0.12 | P 0.10 | P 0.10 | P 0.06 | P 0.04 |
| repaired FIFO 16 x 8 | EmptyExact_A | - | P 3.52 | P 0.02 | P 0.04 | P 0.04 | P 0.04 | P 0.04 |
| repaired FIFO 16 x 8 | PushFull_A | - | P 0.02 | P 0.02 | P 0.02 | P 0.02 | P 0.04 | P 0.02 |
| repaired FIFO 16 x 8 | PopEmpty_A | - | P 0.02 | P 0.02 | P 0.02 | P 0.02 | P 0.04 | P 0.02 |
| repaired FIFO 16 x 8 | Sync_A | - | P 0.02 | P 0.02 | P 0.06 | P 0.04 | P 0.04 | P 0.04 |
| repaired FIFO 16 x 8 | FullReached_C | V17 0.02 | V17 0.08 | V17 0.18 | V17 0.24 | V17 0.16 | V17 0.06 | V17 0.04 |
| repaired FIFO 16 x 8 | PushFull_C | V18 0.02 | V18 0.02 | V18 0.02 | V18 0.04 | V18 0.02 | V18 0.04 | V18 0.02 |
| repaired FIFO 16 x 8 | PopEmpty_C | V2 0.02 | V2 0.02 | V2 0.02 | V2 0.02 | V2 0.02 | V2 0.04 | V2 0.02 |
| repaired FIFO 16 x 8 | Drained_C | V33 0.10 | V33 0.24 | V33 0.12 | V33 0.12 | V33 0.12 | V33 0.12 | V33 0.04 |
| DMA version 2 | ArHeld_A | - | P 0.06 | P 0.04 | P 0.04 | P 0.04 | P 0.04 | P 0.06 |
| DMA version 2 | ArStable_A | - | **-** | P 0.16 | P 1.23 | P 1.15 | P 0.18 | P 0.12 |
| DMA version 2 | AwHeld_A | - | P 0.04 | P 0.04 | P 0.04 | P 0.04 | P 0.04 | P 0.08 |
| DMA version 2 | AwStable_A | - | **-** | P 0.16 | P 1.39 | P 1.25 | P 0.16 | P 0.14 |
| DMA version 2 | WHeld_A | - | P 0.04 | P 0.04 | P 0.04 | P 0.04 | P 0.04 | P 0.06 |
| DMA version 2 | WStable_A | - | **-** | P 0.12 | P 0.91 | P 0.81 | P 0.10 | P 0.08 |
| DMA version 2 | ArWait_C | V5 0.02 | V5 0.04 | V5 0.04 | V5 0.06 | V5 0.08 | V5 0.06 | V5 0.08 |
| DMA version 2 | AwWait_C | V8 0.04 | V8 0.04 | V8 0.06 | V8 0.12 | V8 0.08 | V8 0.06 | V8 0.08 |
| DMA version 2 | WWait_C | V8 0.06 | V8 0.04 | V8 0.04 | V8 0.10 | V8 0.10 | V8 0.06 | V8 0.08 |
| DMA version 2 | ArFirst_C | V4 0.02 | V4 0.04 | V4 0.04 | V4 0.08 | V4 0.08 | V4 0.06 | V4 0.08 |
| DMA version 2 | AwFirst_C | V7 0.04 | V7 0.06 | V7 0.04 | V7 0.08 | V7 0.06 | V7 0.06 | V7 0.08 |
| DMA version 2 | WFirst_C | V7 0.04 | V7 0.06 | V7 0.04 | V7 0.08 | V7 0.06 | V7 0.06 | V7 0.08 |

- **The real-design finding: the three `Stable` rules of the DMA are
  not proved by k-induction in 20 s and are proved by IC3 in 0.12 to
  0.16 s.** The `Held` rules are proved by both in 0.04 s. Chapter 9
  chose `informal-ic3` for that example without saying why; this is
  why, and it is the same reason as the pointer property: "the
  address does not change while waiting" needs a fact about which
  states the address register can be in while VALID is up.
- On the FIFO checker every proving engine finishes; k-induction is
  the slowest on four of seven (0.66 to 3.52 s against 0.02 to
  0.34 s).
- A reachable cover is fastest by BMC or equal, on every row.
- `informal-ic3-mt` (four workers) was the fastest in-house prover
  on the slower rows; it uses four cores.

The Chapter 3 two-clock design (`two_clock.tcl`): tractable, every
engine under 0.5 s; cover of the synchronized enable at depth 22,
`count != 3` refuted at depth 40 (rIC3: 46), depths in model steps of
half a `bclk` period. It adds nothing to engine selection and three
modeling traps: (1) with two reset pins the expression must hold both
(`!brst_n && !crst_n`); with `||` the tool held one low and left the
other domain unreset, and a counter "reached 3" at depth 8 by starting
there; (2) after the reset cycle the expression is only *false*, so
with `&&` either pin may still fall alone later, and a property that
ignores reset is refuted by it (`a_gated`, depth 38); (3) depth is in
half-periods. **Recommendation: no two-clock example in this chapter.**

### M9. What can be seen of certificates, replay, and depth reached (`certify.sh`, `ptr_one.tcl`, `cex_one.tcl`)

Documented (the tool's `docs/engines.md`, "Verdict trust"; `README.md`
"Checked results"): every SAFE and UNSAFE of an in-house engine is
checked on the model as loaded before it is reported, "an invariant
by three fresh SAT queries, a k-induction proof by its base and step,
a counterexample by simulation"; a verdict that fails is withdrawn to
unknown; external engines "are only as trustworthy as they are";
engines that contradict each other are reported as a conflict.

Observable at this commit:

- With `INFORMAL_IC3_STATS=1` in the environment (listed in
  `docs/engines.md` among the "environment switches of the in-house
  IC3 (experiments)") a proof prints on stderr
  `certificate: Ok(()) in <t> s <model path>`, and IC3 prints its
  size: `informal-ic3: frames 5 lemmas 15 ctps 0 queries 146` for the
  pointer property at `DEPTH = 2`, `frames 9 lemmas 66 ... queries
  1226` at `DEPTH = 4`. Without the variable a passed check prints
  nothing; a failed one prints `informal: verdict withdrawn,
  certificate ...` (from the source, `crates/informal-bmc/src/lib.rs`;
  not provoked here).
- `INFORMAL_IC3_TRACE=<file>` writes one JSON line per event: 80
  lines at depth 2 (15 lemma events), 535 at depth 4 (66 lemma
  events).
- The chapter's own IC3 on the corresponding wrapper models: 5 frames
  and 153 queries at depth 2; 11 frames and about 1,500 at depth 4.
  Same order as the tool's 146 and 1,226. The models are not the
  same file (the shell adds its own reset and history state), so the
  numbers must not be printed as "the same".
- `informal engine informal-kind <shell model>`: last progress bound
  6 then `safe` at `DEPTH = 2`, three runs of three identical; at
  `DEPTH = 4` bound 28 and then `safe` after 11 s (with
  `--timeout-ms 3000`: bound 28 and `unknown ... timeout`, three of
  three). The chapter's k-induction script proves the wrapper model
  at k = 7 and the shell's own model (through `simp --aag`) at k = 8.
  **The tool's bound and the script's k are not the same number**
  (different models after preprocessing, and the tool's convention is
  not documented); print neither as the other.
- A refuted property leaves `<name>.vcd`, `prop_N.btor2` and
  `prop_N.trace.btor2` in the work directory. The last is a second
  model with the design's named nets as outputs, used to re-simulate
  the trace for the waveform (`docs/ui/trace-format.md`); it is not
  a witness in the Btor2 witness format. The counterexample replay is
  not otherwise visible: a failed replay prints `... reported a
  counterexample that does not replay (...); verdict withdrawn`
  (source: `crates/informal-fpv/src/session.rs`; not provoked).
- Certificates in the competition's formats are not produced: "
  Certifaiger certificates and AIGER witnesses in the competition's
  formats are still to do" (`docs/engines.md`).

### M10. The teaching k-induction (`teach/kind.py`, `teach/ts.py`; 69 lines and 139)

On `teach/models/fifo_ptrs2.aag`: the repaired FIFO at `DEPTH = 2`,
`WIDTH = 1`, in a wrapper (`fifo_ptrs2.sv`) that writes the reset
cycle as hardware in the way Chapter 17's `fifo_bmc.sv` does and
asserts the pointer property by hierarchical name; lowered by
`informal lower`, preprocessed by `informal simp --aag`: `aag 48 3 5
0 40 1 1`. Latch order, checked against explicit reachability:
`started`, `wr_ptr`, `rd_ptr`, `count[0]`, `count[1]`.

```
$ python3 kind.py models/fifo_ptrs2.aag 8
k=0: base case UNSAT, step case SAT: induction fails from state (1, 1, 0, 0, 0)
k=1: base case UNSAT, step case SAT: induction fails from state (1, 1, 1, 1, 1)
...  (the same line for k = 2 to 8)
undetermined k = 8 queries 18
$ python3 kind.py models/fifo_ptrs2.aag 8 --simple
k=0 ... k=6: base case UNSAT, step case SAT (start states vary)
k=7: base case UNSAT, step case UNSAT: proven
proven k = 7 queries 16
```

The counterexample to induction at k = 3, decoded, plain and with
simple-path constraints:

```
plain    step 0  wr_ptr=1 rd_ptr=1 count=3
         step 1  wr_ptr=0 rd_ptr=0 count=3
         step 2  wr_ptr=1 rd_ptr=1 count=3
         step 3  wr_ptr=0 rd_ptr=1 count=0     <- empty, pointers apart
simple   step 0  wr_ptr=1 rd_ptr=0 count=2
         step 1  wr_ptr=1 rd_ptr=1 count=1
         step 2  wr_ptr=0 rd_ptr=0 count=1
         step 3  wr_ptr=0 rd_ptr=1 count=0
```

Both start outside the reachable set and every state on the way
satisfies the property. (The wrapper's reachable set at depth 2 is
22 of 32 states: 16 are the reset cycle, `started = 0` with the four
other bits free, and 6 are states after reset. At depth 4 it is 148
of 256: 128 and 20, and all 20 satisfy `count[1:0] == wr_ptr -
rd_ptr` and `count <= 4`.) The plain path revisits a state (steps 0
and 2), which is what the simple-path constraint forbids. The helper
`CountPtrs_A` alone (`count_ptrs2.aag`): step unsatisfiable at k = 1.
With the helper as a constraint (`fifo_ptrs_h.aag`, depth 4): step
unsatisfiable at k = 0, that is, the property holds in every state
that satisfies the helper, with no step needed.

Limits: the simple-path run at `DEPTH = 4` did not finish in two
minutes on Chapter 17's solver (the tool needs 11 s and bound 28);
the example stays at depth 2. Determinism: two runs byte-identical.
Fuzz: section M12.

### M11. The teaching IC3 (`teach/ic3.py`, 160 lines)

`python3 ic3.py models/fifo_ptrs2.aag` prints each lemma as it is
learned and the frame sizes after each frontier is cleared:

```
frame 1: no bad state left; sizes [2, 0]
frame 2: no bad state left; sizes [3, 2, 0]
frame 3: no bad state left; sizes [2, 4, 2, 0]
frame 4: no bad state left; sizes [2, 4, 3, 2, 0]
frame 5: no bad state left; sizes [2, 4, 1, 3, 3, 0]
proven: invariant of 6 lemmas; checks (True, True, True)
queries 160
```

The six lemmas, decoded (every one also has `started = 1`):

```
never count[0]=1 and count[1]=1                       (count is never 3)
never wr_ptr=1 and rd_ptr=0 and count[0]=0
never wr_ptr=0 and rd_ptr=1 and count[0]=0
never wr_ptr=1 and rd_ptr=0 and count[0]=0 and count[1]=0   (subsumed by the second)
never wr_ptr=0 and rd_ptr=0 and count[0]=1
never wr_ptr=1 and rd_ptr=1 and count[0]=1
```

Lines 2, 3, 5 and 6 are `count[0] == wr_ptr ^ rd_ptr`, the helper of
Chapter 9 at this depth. The states the lemmas allow are exactly the
22 reachable ones (checked by enumeration). This is the chapter's
central exhibit: **IC3 found the helper, as clauses.**

| model | latches | verdict | frames | lemmas in the invariant | queries | time |
| --- | --- | --- | --- | --- | --- | --- |
| `counter.aag` (Chapter 17) | 3 | cex depth 6 | 5 | | 92 | 0.06 s |
| `fifo_bmc.aag` (Chapter 17, the original FIFO) | 10 | cex depth 16 | | | 1,462 | 1.1 s |
| `fifo_ptrs2.aag` | 5 | proven | 5 | 6 | 160 | 0.12 s |
| `count_ptrs2.aag` (the helper alone) | 5 | proven | | 5 | 125 | 0.1 s |
| `fifo_ptrs.aag` (depth 4) | 8 | proven | 11 | 32 | 1,531 | 1.7 s |
| `fifo_ptrs_h.aag` (depth 4, helper as constraint) | 8 | proven | 1 | 0 | 3 | 0.01 s |
| `fifo_ptrs8.aag` (depth 8) | 11 | proven | | 213 | 17,803 | 34 s |

(Query counts include the certificate's.) What the prototype has:
frames as lists of blocked cubes stored once at the highest frame
where they hold; the three queries; a list of proof obligations taken
lowest frame first; generalization by dropping one literal at a time
while the cube stays disjoint from reset and has no predecessor;
propagation, with termination when a frame's own list empties; a
counterexample as the chain of obligations; `certify`, the three
checks. What it lacks, and the chapter must say: lifting of
predecessors (ternary simulation), unsat cores, re-queueing an
obligation at the next frame, incremental solving, subsumption. Two
runs print the same text.

### M12. Fuzzing the teaching engines (`teach/fuzz.py`, `teach/mutfuzz.py`; outputs in `teach/out/`)

Referee: `explicit()` in `ts.py`, breadth-first search over every
state and every input value by evaluating the and-inverter graph; no
solver in it.

| run | cases | proven | cex | wrong | notes |
| --- | --- | --- | --- | --- | --- |
| `fuzz.py 700 11 ic3` | 700 | 216 | 484 | 0 | 2 to 8 latches; deepest counterexample 182; largest invariant 9 lemmas |
| `fuzz.py 700 12 ic3` | 700 | 229 | 471 | 0 | deepest 77; 22 lemmas |
| `fuzz.py 700 13 ic3` | 700 | 234 | 466 | 0 | deepest 95; 24 lemmas |
| `fuzz.py 600 21 ic3,kind` | 429 (2 to 6 latches) | 127 | 302 | 0 | plain k-induction to k = 12: 108 proven, 20 undetermined, 301 cex; simple-path to k = 20: 127 proven, 302 cex |
| `mutfuzz.py fifo_ptrs.aag` | 153 | 37 | 116 | 0 | invariants to 74 lemmas, 15 frames |
| `mutfuzz.py counter.aag` | 42 | 9 | 33 | 0 | |
| `mutfuzz.py fifo_ptrs_h.aag` | 189 | 168 | 21 | 0 | |
| total | 2,913 | | | **0** | |

Checks per case. Proven: the invariant contains every reachable
state, is closed under every constrained step, contains no bad
state (all three by enumeration), and passes the three solver
queries. Counterexample: the trace starts in a reset state, each
step exists under some input that satisfies the constraints, the
last state is bad under such an input, and (every case) its length
is the shortest. k-induction: verdict and, for a counterexample, the
depth. The random generator's first version produced nothing deeper
than 2 steps and was replaced; the outputs kept are from the second.
What the fuzz does not cover: more than 8 latches, more than 3
inputs, more than one constraint or bad literal. The three runs of
700 took 10 to 25 minutes each because IC3 with whole-state cubes
needs one frame per step of a deep counterexample (35 s for one at
depth 120); a CI example of the fuzz must cap the latch count at 6
and the case count at about 200 (the 429-case run took about two
minutes including k-induction).

### M13. `set_engine_mode` and `set_prove_time_limit` (`modes.tcl`; 32 s)

`set_engine_mode` maps JasperGold engine letters to InFormal engine
sets, keeps the ones this build has, and the set then runs as a race
(source: `crates/informal-fpv/src/compat.rs` at the pinned commit):
`Ht Hp Hps Hts Mp AM AD M L R` to `informal-kind-ic3`,
`informal-ic3-mt`, `ric3-ic3`, `abc-pdr`; `B Bm K C C2 I Tri Q3 U`
to `informal-bmc`, `informal-wbmc`, `ric3-bmc`; `N D G G2` to
`informal-kind`, `ric3`. Measured: `{Ht}`, `{Hp}` and `{AM}` proved
and refuted (answers by `informal-kind-ic3`); `{B}`, `{Tri}`, `{K}`
and `{I}` found the bug and left the true assertion and the
unreachable cover `undetermined`; `{N}` proved by `informal-kind`;
`{Ht B}` had two different engines answer in one table. The shell
document's map (`Ht/Hp` to `ric3-ic3`, `abc-pdr`; `B` to `ric3-bmc`;
`N` to `ric3`) is older than the source. **The chapter must not say
what these letters mean in the vendor's tool; no vendor document was
read.** Because the mapped set is a race, a script that uses
`set_engine_mode` is not repeatable; the book's scripts use
`informal::set_engines <one name>`.

`set_prove_time_limit`: `5` and `5s` are five seconds, `0.5s`, `2m`,
`1h` accepted; `500ms` is `bad time unit`, `-1` and `abc` are `bad
time`; `0` returns at once with `undetermined` (wall 23 ms). The limit
is per property (a two-property BMC run at 20 s took 40 s). No
command reads the limit back. Default 3600 s (FM D.5).

### M14. Determinism and run time for CI

- One engine per `prove`: the report minus the time column repeats
  (FM D.5, 6 of 6 runs; the book's `informal.sh` strips times). Every
  verdict and depth in M1 to M8 that FM had measured was the same
  here.
- Not repeatable and therefore never in a `run.out`: anything from
  the default portfolio or `set_engine_mode`; progress bounds of the
  engine child except the last one before a verdict (M9); the bound
  BMC reaches in a fixed time (M2); the depth of a stepped-BMC or
  rIC3 counterexample (M1, M8) (those are repeatable per engine in
  FM's test but not minimal, so they contradict the prose).
- The teaching scripts are pure Python on Chapter 17's solver and
  printed identical text twice; Chapter 17's note (its pitfall P1)
  records that counts were produced under one Python version, and
  the same caution applies: `min()` over tuples and list order decide
  which lemma is found first.
- Time. An example with one `undetermined` row costs its limit, per
  property. Chapter 9's `fifo-proof` spends about 30 s that way. The
  budget of a minute per example allows at most two such rows at
  20 s; the scaling table (M3) cannot be one example at 20 s limits
  (it took about 20 minutes here). Plan it as an example with a 5 s
  limit and depths 2, 4, 16 and 64, in-house engines `informal-kind`
  and `informal-ic3` only: 2 properties x 2 engines x 4 depths with
  at most 7 `undetermined` rows is 35 s of limits. At a 5 s limit
  the row "k-induction at depth 4" changes from proven (11 s) to
  undetermined; the example must state the limit in its output, and
  the prose must not say "k-induction cannot" where the output only
  says "did not in 5 s".
- Memory was not an issue anywhere (the designs are small).


## 2. Source table

Marks, as in the note for the chapter before this one. **[V-CR]**:
authors, title, venue, volume and pages checked against the
publisher's Crossref record on 2026-11-15 (metadata only). Crossref
gives initials only for some records; where it did, the row says so
and the given names are not verified. **[V-TEXT: what]**: the named
passage was read in a copy of the document (the copy's host is
named). **[U]**: not verified in this session. **Every text was read
through a fetch tool that returns extracted text, not the page
image: a wording given below is a pointer to the passage, not a
checked quotation. No sentence may be printed in quotation marks
until it has been read in the PDF itself.** `refs.bib` keys that
already exist are given in code font; rows without a key need a new
entry.

### 2.1 Model checking, safety and liveness

| topic | source | status |
|---|---|---|
| Model checking, first paper (US) | Edmund M. Clarke, E. Allen Emerson, "Design and synthesis of synchronization skeletons using branching time temporal logic", in *Logics of Programs*, LNCS 131, Springer, pp. 52-71. DOI 10.1007/BFb0025774. `clarke1981modelchecking` | [V-CR] authors, title, pages 52-71 (the bib entry lacks the pages; add them). Crossref has no issue date; the workshop was 1981, the volume is dated 1982 in most citations [U]. Text not read: cite for "introduced model checking" at title level only. |
| Model checking, first paper (France) | J. P. Queille, J. Sifakis, "Specification and verification of concurrent systems in CESAR", in *International Symposium on Programming*, LNCS 137, Springer, 1982, pp. 337-351. DOI 10.1007/3-540-11494-7_22 | [V-CR], initials only (Jean-Pierre, Joseph are [U]). Text not read. |
| Safety and liveness defined | Bowen Alpern, Fred B. Schneider, "Defining Liveness", *Information Processing Letters* 21(4):181-185, 1985. `alpernschneider1985liveness` | verified for Chapter 9 (its note, section on safety and liveness: text read in the author-hosted PDF). Not re-read here. This chapter needs only: a safety violation has a finite witness, a liveness violation does not; cite Chapter 9 by label and this paper once. |
| "Safety" and "liveness" as terms | Leslie Lamport, 1977. `lamport1977proving` | as Chapter 9; not needed again unless the drafter wants the origin of the words. |
| Standard text | Edmund M. Clarke, Orna Grumberg, Daniel Kroening, Doron Peled, Helmut Veith, *Model Checking*, 2nd ed., MIT Press, 2018 | [U] not opened; authors and edition from memory. Further reading only, after the record is checked. |
| Standard text | Christel Baier, Joost-Pieter Katoen, *Principles of Model Checking*, MIT Press, 2008 | [U] as above. |
| Handbook chapter on the SAT-based engines | Armin Biere, Daniel Kroening, "SAT-Based Model Checking", in *Handbook of Model Checking* (Clarke, Henzinger, Veith, Bloem, eds.), Springer, 2018, pp. 277-303. DOI 10.1007/978-3-319-10575-8_10 | [V-CR]. Text not read. Further reading; the natural "read next" for sections 3 to 6 of the outline. |

### 2.2 Bounded model checking and its bound

| topic | source | status |
|---|---|---|
| BMC; the unrolled formula; bounded liveness as a loop | Armin Biere, Alessandro Cimatti, Edmund Clarke, Yunshan Zhu, "Symbolic Model Checking without BDDs", TACAS 1999, LNCS 1579, pp. 193-207. DOI 10.1007/3-540-49059-0_14. `biere1999symbolic` | verified and read for Chapter 17 (its Definition 10 is the unrolled formula). **Not re-read here for the diameter**: the passage that bounds k by the diameter of the state graph ("completeness threshold" is a later word) is [U]. Before the chapter says "BCCZ observe that a bound equal to the diameter suffices", read section 5 of the paper. |
| The term "completeness threshold" and its size for general properties | Edmund Clarke, Daniel Kroening, Joel Ouaknine, Ofer Strichman, "Completeness and Complexity of Bounded Model Checking", VMCAI 2004, LNCS 2937, pp. 85-96. DOI 10.1007/978-3-540-24622-0_9 | [V-CR]. Text not read. Cite for the term only. |
| Handbook chapter | Armin Biere, "Bounded Model Checking", in *Handbook of Satisfiability*, 2nd ed. `biere2021handbook` is the whole handbook | chapter number and pages [U]; cited at book level in Chapter 17. |

### 2.3 Induction

| topic | source | status |
|---|---|---|
| k-induction with a SAT solver; the unique-states (loop-free) constraint; completeness | Mary Sheeran, Satnam Singh, Gunnar Stalmarck, "Checking Safety Properties Using Induction and a SAT-Solver", FMCAD 2000, LNCS 1954, pp. 127-144. DOI 10.1007/3-540-40922-X_8 | [V-CR]; [V-TEXT: sections 2 to 4 in a university-hosted copy]. Section 2.1 defines `path` and `loopFree` (all states of the path differ); section 3 gives the first algorithm (for increasing i: is there a loop-free path of length i from an initial state, or to a bad state; if neither, stop; otherwise check for a counterexample of length i); section 4 states the induction form and says that without the loop-free constraint induction with depth is incomplete. The paper's tool was built on Stalmarck's method, not on a clause-learning solver. The formulas in the chapter must be the chapter's own, checked against its script, not copied. |
| The same idea presented independently in the BMC line | Per Bjesse, Koen Claessen, "SAT-based verification without state space traversal", FMCAD 2000 | [U] not looked up. Do not cite unless checked. |
| Incremental formulation, the form tools implement ("temporal induction") | Niklas Een, Niklas Sorensson, "Temporal induction by incremental SAT solving", *Electronic Notes in Theoretical Computer Science* 89(4):543-560, 2003. DOI 10.1016/S1571-0661(05)82542-3 | [V-CR]; abstract read on the publisher page; body not read. Cite for "one solver kept across k, base and step interleaved, unique-state constraints added only when violated" **only after the body is read**; the abstract supports "incremental" and "temporal induction" as the paper's words. |
| Counterexample to induction as a term | no single origin found | [U]. Bradley 2011 does not use the abbreviation "CTI" in the copy read; Bradley and Manna 2007 (below) is where the phrase is usually traced, not read. **Define the term in the chapter's own words and attribute it to no one.** |

### 2.4 Interpolation (one paragraph in the chapter)

| topic | source | status |
|---|---|---|
| Interpolants from refutations as over-approximate images; first SAT-based unbounded engine that learns from proofs | K. L. McMillan, "Interpolation and SAT-Based Model Checking", CAV 2003, LNCS 2725, pp. 1-13. DOI 10.1007/978-3-540-45069-6_1 | [V-CR], initials only (Kenneth is [U]); [V-TEXT: abstract and section 3 in a university-hosted copy]. Enough for: "from the refutation of a bounded unrolling one can extract a formula over the state after one step that contains every state reachable in one step and still cannot reach a bad state within the bound; iterating gives a fixed point". InFormal has no interpolation engine at this commit (its `docs/engines.md` engine list), so the chapter says what the idea is and where it sits in history, with no run. |

### 2.5 IC3 / PDR

| topic | source | status |
|---|---|---|
| IC3 | Aaron R. Bradley, "SAT-Based Model Checking without Unrolling", VMCAI 2011, LNCS 6538, pp. 70-87. DOI 10.1007/978-3-642-18275-4_7 | [V-CR]; [V-TEXT: sections 2 to 4 in the author-hosted copy]. Section 3 gives the informal walk through; "inductive relative to" is defined there. Section 4 states the four properties of the frame sequence: the initial states imply F0; each Fi implies Fi+1; each Fi implies the property; Fi and one step imply Fi+1 primed. Termination when two adjacent frames are equal. The copy read uses neither "CTI" nor "proof obligation". The name IC3 is expanded in the paper ("Incremental Construction of Inductive Clauses for Indubitable Correctness") [U: the expansion was returned by the fetch; confirm in the PDF before printing]. |
| The predecessor (inductive generalization of a single state's negation; "counterexample to induction") | Aaron R. Bradley, Zohar Manna, "Checking Safety by Inductive Generalization of Counterexamples to Induction", FMCAD 2007, pp. 173-180. DOI 10.1109/FAMCAD.2007.15 | [V-CR]. Text not read. One sentence of history at most. |
| PDR: the name, proof obligations, ternary simulation, a simpler implementation | Niklas Een, Alan Mishchenko, Robert Brayton, "Efficient Implementation of Property Directed Reachability", FMCAD 2011, pp. 125-134. ISBN 978-1-4673-0896-0 | pages from the proceedings' contents list (paper starts at 125, the next at 135); **no DOI found in Crossref**; [V-TEXT: sections I to III in an author-hosted copy]. The paper says the name "property directed reachability" is theirs for Bradley's algorithm; section III-B defines a proof obligation as a pair of a cube and a frame; the trace is R0 .. RN; ternary simulation shrinks a predecessor cube; lemmas are stored once at the highest frame where they hold (the "delta" encoding the chapter's own IC3 also uses); a last frame "at infinity" holds proved clauses. Use for the vocabulary the chapter adopts: *frame, cube, lemma (blocked cube), proof obligation, generalization, propagation*. |
| An IC3 written for reading | Aaron Bradley's reference implementation `IC3ref` (GitHub) | [U] not opened. Mention in further reading only after its license and URL are checked. |
| Understanding IC3 (tutorial) | Aaron R. Bradley, "Understanding IC3", SAT 2012, LNCS 7317, pp. 1-14 | [U] not looked up; pages from memory. The best single "read next"; check, then list in further reading. |
| IC3 for bit-vectors/word level; CTP and later refinements | not surveyed | out of scope; the tool's own literature list (`docs/literature-2026-11.md` in the tool's repository) names its sources and is the tool author's reading, not a source for the book. |
| The engine the tool can call | Yuheng Su, Qiusong Yang, Yiwei Ci, Yingcheng Li, Tianjun Bu, Ziyu Huang, "Deeply Optimizing the SAT Solver for the IC3 Algorithm", CAV 2025, LNCS, pp. 237-257. DOI 10.1007/978-3-031-98668-0_12. Preprint arXiv 2502.13605 (v2 lists five authors, without Yingcheng Li). Tool: rIC3, version 1.5.2 here | [V-CR] for the CAV record (found by title search on 2026-11-15); the arXiv abstract page read; body not read. LNCS volume number [U]. Cite only to identify the engine; no claim about what is inside it. |

### 2.6 Liveness

| topic | source | status |
|---|---|---|
| Liveness to safety: remember a state, detect the loop | Armin Biere, Cyrille Artho, Viktor Schuppan, "Liveness Checking as Safety Checking", *Electronic Notes in Theoretical Computer Science* 66(2):160-177, 2002. DOI 10.1016/S1571-0661(04)80410-9 | [V-CR]; [V-TEXT: sections 1 to 3 in a university-hosted copy]. The construction: an oracle input chooses when to save the current state in a copy of the registers; a flag records that the awaited event has (not) happened since; the bad state is "back in the saved state with the event not seen". The paper says the translation handles fairness. The doubling of the state bits is in the paper; give the count from the chapter's own run, not from the paper. |
| k-liveness | Koen Claessen, Niklas Sorensson, "A Liveness Checking Algorithm that Counts", FMCAD 2012, pp. 52-59 | pages from the proceedings; abstract read in the proceedings PDF; body not read; DOI [U]. One sentence: "another reduction bounds how many times the bad condition can recur and raises the bound". The tool's `docs/fpv-shell.md` (the SVA subset section) says it reduces `s_eventually` to a safety property by liveness to safety with a shadow copy of the state; state that from the tool's document, pinned, not from this paper. The tool's `README.md` still lists liveness under "not there yet": the shell document and the measurements (M6, M7) are the evidence, and the chapter does not quote the README line. |
| Fairness, strong and weak | no primary source read | [U]. The chapter uses the SVA-level notion only (an `assume` with `s_eventually`), defined in its own words; for the temporal-logic distinction cite the standard text once it has been checked, or leave it to further reading. |

### 2.7 Vacuity and coverage of the property set

| topic | source | status |
|---|---|---|
| Vacuity, witnesses | Ilan Beer, Shoham Ben-David, Cindy Eisner, Yoav Rodeh, "Efficient Detection of Vacuity in Temporal Model Checking", *Formal Methods in System Design* 18(2):141-163, 2001. `beer2001vacuity` | verified and read for Chapter 9 (see its note). Not re-read. Chapter 9's note lists two wordings from this paper that still need a check in the PDF; the same holds here. |
| Vacuity generalized | Orna Kupferman, Moshe Y. Vardi, "Vacuity detection in temporal model checking", *International Journal on Software Tools for Technology Transfer* 4(2):224-233, 2003. DOI 10.1007/s100090100062. Conference version CHARME 1999 | journal record [V-CR]; the conference version is the one Chapter 9's note read. Use one, consistently with Chapter 9. |
| Over-constraint in industrial practice | Erik Seligman, Tom Schubert, M V Achutha Kiran Kumar, *Formal Verification: An Essential Toolkit for Modern VLSI Design*, Morgan Kaufmann/Elsevier; 1st ed. 2015, ISBN 9780128007273; 2nd ed. 2023, ISBN 9780323956123 | editions and ISBNs from Crossref chapter records [V-CR]; **the book's text was not opened**. Chapter numbers and any statement of what the book recommends are [U]. Further reading, with the edition; no paraphrase of its advice. |

### 2.8 Abstraction (forward pointer only)

| topic | source | status |
|---|---|---|
| CEGAR | Edmund Clarke, Orna Grumberg, Somesh Jha, Yuan Lu, Helmut Veith, "Counterexample-Guided Abstraction Refinement", CAV 2000, LNCS 1855, pp. 154-169. DOI 10.1007/10722167_15 | [V-CR]. Text not read. Belongs to the next chapter; here at most one sentence in future directions or none. |

### 2.9 Competition, formats, certificates

| topic | source | status |
|---|---|---|
| The competition, most recent edition with a report | Armin Biere, Nils Froleyks, Mathias Preiner, "Hardware Model Checking Competition 2024", in *Proc. FMCAD 2024*, TU Wien Academic Press (DOI prefix 10.34727/2024/isbn.978-3-85448-065-5); results page hwmcc.github.io/2024 | results page [V-TEXT]: three tracks; 319, 319 and 321 benchmarks; 16 cores, 120 GB, one hour; certificates mandatory in the bit-level tracks; the bit-level table has `ric3` first with 248 solved and `pavy` second with 217. The FMCAD record's page number and full DOI [U]. **Use at most: "certificates were mandatory in 2024" and the limits; no ranking sentence** (a ranking is a claim about tools on benchmarks the book did not run, and the entry list changes yearly). |
| AIGER, AIGER 1.9 (bad, constraint, justice, fairness sections) | `biere2007aiger`, `biere2011aiger19` | verified for Chapter 17. The witness format (the `1`/`b0` header, one input line per step, `.`) is described in the 1.9 report [U: that section was not re-read]. The chapter does not print a witness in this format, because the tool does not write one (M9). |
| Btor2 and its witness format | Aina Niemetz, Mathias Preiner, Clifford Wolf, Armin Biere, "Btor2, BtorMC and Boolector 3.0", CAV 2018. `niemetz2018btor2` | verified for Chapter 17 for the model format; the witness section was not read [U]. Same handling. |
| Certificates for safe verdicts | Emily Yu, Armin Biere, Keijo Heljanko, "Progress in Certifying Hardware Model Checking Results", CAV 2021, LNCS 12760, pp. 363-386. DOI 10.1007/978-3-030-81688-9_17. Earlier: Emily Yu, Armin Biere, Keijo Heljanko, "Certifying Hardware Model Checking Results", ICFEM 2019, LNCS 11852, pp. 498-502. DOI 10.1007/978-3-030-32409-4_32 | [V-CR] both (LNCS volume numbers from memory, [U]). Text not read. The chapter's statement "an inductive invariant is checked by three satisfiability queries" is shown by its own script (`certify` in `ic3.py`) and by the tool's document; cite these papers for "the competition's certificate format" at title level. |
| ABC | Robert Brayton, Alan Mishchenko, "ABC: An Academic Industrial-Strength Verification Tool", CAV 2010, LNCS 6174, pp. 24-40. DOI 10.1007/978-3-642-14295-6_5 | [V-CR]. Named once as the home of PDR and of the engine SymbiYosys calls. |

### 2.10 Tools (documents, pinned by date)

| topic | source | status |
|---|---|---|
| InFormal | repository at commit `5114330`, tag v0.1.0: `README.md`, `docs/fpv-shell.md`, `docs/engines.md`, `docs/decisions.md`, `docs/ui/trace-format.md`; source files named in M9 and M13. `informal-tool` | read in a clone at that commit. Every statement about the tool in the chapter is either a `run.out` or one of these files, named. |
| SymbiYosys | reference page of the documentation (modes `bmc`, `prove`, `live`, `cover`; `depth` default 20; engines `smtbmc`, `btor`, `aiger`, `abc`; in `prove` mode the depth is the induction depth). `sby-docs`, `sby-verific` | [V-TEXT] read 2026-11-15 on the documentation host. Version of the page not stated on it: cite with the access date. |
| JasperGold FPV | vendor product page. `cadence-jasper-fpv` | [V-TEXT] on the vendor's staging host on 2026-11-15, as for Chapter 9 (the main host refused). It speaks of formal engines that exhaustively prove assertions, of a manager that distributes engines over machines, and of adding constraints from a counterexample view. **It does not mention bounded proofs, covers, liveness, vacuity or over-constraint.** |
| VC Formal | vendor product page. `synopsys-vcformal` | [V-TEXT] 2026-11-15: a list of applications (property verification among them) and a general claim about engines and their orchestration. Nothing on bounded proofs or vacuity. |
| Questa formal | vendor product page. `siemens-questa-formal` | [V-TEXT] 2026-11-15: general claims only. |
| Engine letters, proof-status vocabulary, vacuity and over-constraint features of the three commercial tools | their user guides | **not public; not read.** Nothing may be said about them. The comparison table has, for those three columns, only what the product pages say, each cell labelled as the vendor's statement, and "not stated on the page read" elsewhere. |

### 2.11 What could not be opened or was not read, in one list

1. The text of Clarke and Emerson 1981, Queille and Sifakis 1982,
   Bradley and Manna 2007, Clarke et al. 2004 (completeness
   threshold), Clarke et al. 2000 (CEGAR), Biere and Kroening 2018,
   Yu et al. 2019 and 2021, Brayton and Mishchenko 2010: metadata
   only.
2. The body of Een and Sorensson 2003 and of Claessen and Sorensson
   2012: abstract only.
3. The diameter passage of Biere et al. 1999; the witness sections of
   the AIGER 1.9 report and of the Btor2 paper.
4. Seligman, Schubert and Kumar; Clarke et al., *Model Checking*;
   Baier and Katoen: not opened.
5. "Understanding IC3", Bjesse and Claessen 2000, `IC3ref`: not
   looked up.
6. The main Cadence host (refused; staging host read). Every vendor
   user guide.
7. The page number and DOI suffix of the HWMCC 2024 report; LNCS
   volume numbers given from memory (marked above).
8. All wordings: read as extracted text. None is a checked quotation.

## 4. Constraints for the drafter

### 4.1 Claims that must not be made (or only in the form given)

1. **No quotation from any paper of section 2** until the sentence
   has been read in the PDF. The epigraph is the book's own sentence.
2. **Bradley's paper does not say "CTI" or "proof obligation"** in
   the copy read. Use "counterexample to induction" as a defined
   term without attribution; attribute "proof obligation" and "PDR"
   to Een, Mishchenko and Brayton.
3. **"k-induction is complete" only with its conditions**: with the
   constraint that the states of the step case differ pairwise, on a
   finite-state system, and "complete" means "some k exists", not
   that the k is practical. The chapter's own measurement is the
   evidence for the second half (k = 7 on five state bits; no answer
   in two minutes on eight).
4. **The script's k and the tool's bound are different numbers** (7
   or 8 against 6; M9). Never print one as the other; never say what
   the tool's progress number counts, because its convention is not
   documented.
5. **No "cannot" from a time limit.** `undetermined` means "no
   verdict within the limit set in the script". Every row of that
   kind is worded "did not finish in N s". The limit is printed in
   the example's output.
6. **No rule from one design.** "IC3 is slower than induction on
   inductive properties", "IC3 on the small solver beats IC3 on
   CaDiCaL", "the multi-threaded IC3 is fastest" are single
   measurements (M1, M3, M8). Word them as observations on a named
   design, with the reason where there is one (Q5).
7. **No claim about the inside of InFormal's engines** beyond what
   its documents say (named, pinned) and what the statistics line
   prints. In particular not "the tool's IC3 found the same six
   lemmas": the tool prints a count (15 lemmas at depth 2 on its own
   model), not the lemmas, and the model is not the script's.
8. **No statement about a commercial tool beyond its product page**
   (2.10). No engine letters explained (M13). No "JasperGold calls
   this X". No disparagement of any tool, InFormal included: limits
   are stated as measurements at a commit.
9. **No competition ranking**; no "state of the art" sentence about
   any engine.
10. **Interpolation is described, not run.** The tool has no such
    engine at this commit.
11. **The diameter**: the chapter may compute it for its own five-bit
    model by explicit search (the referee in `ts.py` gives the
    deepest state) and say that for a design of real size nobody can
    compute it; it may not attribute a statement about it to Biere et
    al. 1999 until the passage is read.
12. **Liveness reduction**: describe the construction of Biere, Artho
    and Schuppan in the chapter's own words; say which reduction the
    tool uses only from the tool's `docs/fpv-shell.md`.
13. **"Proved" is relative to the model**: reset as modeled by the
    shell, two-valued logic, the assumptions, the clock as declared.
    Chapter 9 measured the reset trap; refer to it by label and do
    not re-tell it.
14. **Certificates**: the tool checks its in-house verdicts before
    reporting them (its document); it does not write a certificate
    file in a competition format (its document says this is still to
    do). Both halves or neither.
15. Nothing about X-propagation, multiple clocks, or asynchronous
    reset in formal beyond one pointer each (M8's recommendation).

### 4.2 Pitfalls found while measuring (P1 to P22)

- **P1. Latch order and names.** `simp --aag` writes no symbol table
  the scripts can rely on; the latch order of each checked-in `.aag`
  was established against explicit reachability (M10). Each model
  gets a small sidecar (`fifo_ptrs2.names`) checked in beside it, and
  the example prints a line that fails if the order changes (for
  instance the count of reachable states with the property and the
  helper evaluated by name).
- **P2. Regenerated models.** As in Chapter 17: the `.aag` is checked
  in so that the Python examples need no tool, and a tool-dependent
  example regenerates it and compares.
- **P3. Depth conventions.** Depth counts states with the reset cycle
  as state 0 in the shell's report (Chapter 9, Chapter 17 P7); the
  scripts' k counts transitions. A cover at "depth 17" is 16 pushes.
- **P4. Stepped engines.** `informal-bmc-10`, `-bmc-65` and rIC3
  report counterexample depths that are not minimal (M1, M8). The
  examples use `informal-bmc` where the prose says "shortest".
- **P5. `prove -property`** needs the full hierarchical name; the
  report still lists the others as `unprocessed` (M4).
- **P6. Assumptions are `unprocessed` in the report**: nothing checks
  them. A false assertion is `proven` under a contradiction (M5).
- **P7. `cover {1'b1}`** finds only a contradiction that kills the
  first cycle (M5). The chapter teaches the witness cover per
  property.
- **P8. BMC under a contradiction** answers `undetermined`, not
  `proven` (M5): the same script looks healthy with one engine and
  wrong with another.
- **P9. A proven assertion is not reused** as a lemma for the next
  (M3, FM A.4). Assertion to assumption is a manual step and is a
  proof obligation of its own: the helper must itself be proved, in
  the same example.
- **P10. Lasso.** The loop is defined by states; the inputs printed
  in the last row of the trace are not part of it (M6).
- **P11. One liveness property per session**, and no bounded-delay
  property beside it: other properties' bookkeeping state changes
  the lasso depth (M7).
- **P12. Liveness engine.** Select `informal-ic3`; BMC and
  k-induction do not prove a true liveness property within 30 s
  here; external engines are not run on liveness (M7).
- **P13. `set_engine_mode`** maps to a race and is not repeatable;
  the shell document's letter map is older than the source (M13).
  The command appears in the command table with its measured effect
  and in no example that has a `run.out`.
- **P14. `set_prove_time_limit`** is per property; `500ms` is
  rejected; `0` returns at once (M13).
- **P15. Exit status.** The shell exits 0 with failed properties (FM
  D.4); the book's wrapper is what a CI job must test.
- **P16. Immediate assertions are dropped** by the tool's front end
  (FM D.1); the SVA-forms table must have the row and the chapter
  must say it once in a Pitfall.
- **P17. Environment switches** (`INFORMAL_IC3_STATS`,
  `INFORMAL_IC3_TRACE`) are listed by the tool as experiments. Use
  the statistics line in one example at most, filtered to the fields
  that repeated (frames, lemmas, queries; check three runs before
  fixing the `run.out`), and say they are not a stable interface.
- **P18. The engine child** (`informal engine`) is documented but not
  in `--help`; only the last bound before a verdict repeated (M9).
- **P19. Pure-Python cost.** Simple-path induction at depth 4 and the
  teaching IC3 at depth 8 are too slow for an example (M10, M11).
  All teaching runs stay at depth 2, plus IC3 at depth 4 (1.7 s) for
  the lemma count. The fuzz example is capped (M12).
- **P20. Python version.** Lemma order and counts depend on
  tie-breaking in the scripts; the `run.out` is fixed under the
  book's Python (3.13) and the scripts sort wherever a set is
  iterated (the prototype already does; keep it so).

- **P21. Chapter 9 already ran the delayed contradiction.** Its
  `vacuity-formal` example has a block "a contradiction that takes a
  tick to bite" (a cover of the first cycle is covered, the cover of
  the next is unreachable, the assertion is `proven`), and its
  `assume-formal` example proves a sink under two assumed source
  rules. This chapter's assumption section must cite those by label
  and add only what M5 has beyond them: an over-constraint that is
  not a contradiction and hides a bug 202 cycles deep, and the
  dependence of the vacuous verdict on the engine (`proven` under a
  prover, `undetermined` under bounded search).
- **P22. Numbers of the two-entry model added after M10** (explicit
  search, same script): the six post-reset reachable states are
  `(wr_ptr, rd_ptr, count)` = (0,0,0), (1,0,1), (1,1,0), (0,1,1),
  (0,0,2), (1,1,2); the deepest is first reached 4 steps after the
  first state (the reset cycle is step 0); among the six, any state
  reaches any other in at most 3 steps; of the 16 post-reset states 2
  are bad ((1,0,0) and (0,1,0)) and 8 satisfy the property without
  being reachable. `kind.py` on Chapter 17's bugged `fifo_bmc.aag`:
  base case satisfiable at k = 16, 33 queries, 0.8 s.

### 4.3 Version pins and dates

| what | pin |
|---|---|
| InFormal | 0.1.0, commit `5114330`; CaDiCaL linked; Bitwuzla not built |
| rIC3 | 1.5.2 (comparison rows of this note only; see section 5) |
| Python | 3.13.18; `z3-solver` 5.4.1 (not used by this chapter's scripts) |
| Chapter 17 files reused | `examples/ch17-logic-and-solvers/common/aiger.py`, `cdcl/cdcl.py`, `fifo-unroll/bmc_aag.py`, `fifo-unroll/fifo_bmc.aag`, `counter.aag` (by path, not copied) |
| machine | 4 cores, 15 GB; all seconds in this note are of this machine on 2026-11-15 |
| web documents | accessed 2026-11-15 |

Seconds never enter a `run.out`. Where the chapter prints seconds
they are in a table whose caption names the tool version, the
machine class and the date.

## 5. Open questions for the author

**5.1 Should the book's engine list gain rIC3? (changes the engine
guide and the CI)** Today `examples/mk/informal-engines.toml` is
empty and every example runs in-house engines only. Measured here
with rIC3 added in a private list: it alone proved the pointer
property at 64 entries and found the 1,025- and 4,097-step bugs
within 20 s, and it was the fastest prover on most rows; it does
nothing on liveness. Three ways to go:

- (a) *Keep the list empty.* The engine-selection table is generated
  from in-house engines; the chapter says in one sentence that the
  tool can call external engines and that this note measured one,
  with the numbers in a captioned table (as Chapter 17 did for
  production SAT solvers). No CI change. **The outline assumes
  this.**
- (b) *Add rIC3 to the list and to CI.* One more pinned tool to build
  (Rust); the generated table gains two columns and the scaling
  example gains its strongest row. Examples that name `ric3-*` must
  skip where it is absent, as they do for the tool itself.
- (c) *A second list used by one example only.* The engine guide's
  example carries its own list; the rest of the book is unchanged.

**5.2 How do times enter the engine-selection table?** `run.out`
cannot hold seconds. The outline assumes: the generated table holds
verdicts and "answered within the limit / did not", from limits of
5 s; a second, captioned table in the chapter holds this note's
seconds, dated. The alternative (a three-way class with a "slow"
band) was judged too close to a threshold to be stable in CI (the
11.3 s row would flip with machine load).

**5.3 The chapter's own engines are about 370 lines of Python in
three files beside Chapter 17's solver.** They were fuzzed (M12)
and the outline plans a capped fuzz as an example so that CI keeps
them honest. If the author would sooner have the chapter rest on the
tool alone, sections 4 and 6 of the outline shrink to report rows
and the chapter loses the failing step and the lemmas, which the
shell does not print. The outline assumes the scripts stay.
