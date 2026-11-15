# Outline: Logic and Solvers for Verifiers

Date: 2026-11-15. Status: outline for gate 1. Evidence:
`research/ch17-logic-and-solvers.md` (cited below as RN with a section
or pitfall number). Chapter file `chapters/ch17-logic-and-solvers.qmd`,
label `{#sec-ch17}`; it opens the proof part and is registered in
`_quarto.yml` before `chapters/ch34-generative-ai-agentic-dv.qmd`.
Design doc section 4, entry 17: "propositional logic, SAT, bit-vector
SMT, BDDs, and-inverter graphs; what the engines under [constrained
random] and [formal property verification] do and why they blow up".

## 0. The chapter in one paragraph

Chapter 9 printed `cex ... depth 16` for the first chapter's FIFO and
did not say where the 16 came from. This chapter makes the reader
produce it. One thread runs through: a full adder becomes clauses by
hand; two adders become a question with a yes/no answer (a miter); a
ninety-line search answers it slowly and a hundred-and-fifty-line
search with clause learning answers it quickly; the same solver is
then shown what it cannot do (pigeons, multipliers, the wrong
variable order), with the theorem or the absence of one beside each
measurement; two other representations (BDDs, and-inverter graphs)
and the word level (bit-vector SMT, the solver Chapter 7 already
called) are placed against it; and a clock is added by copying the
circuit once per cycle, which turns the FIFO into 1,795 variables and
finds the bug at bound 16 with the reader's own solver. The chapter
stops there: a bound is not a proof.

Every number in the chapter is either from a cited paper or printed by
an example's `run.out`. No new dependency: Python, `z3-solver`
(already in CI), and `informal`/Yosys for three examples that skip
when the tool is absent (RN Q1, section 5).

## 1. Decisions taken in this outline (and the one left to the author)

| decision | basis |
|---|---|
| Question-first order, SAT before BDDs | RN Q6: the reader's tools are SAT-based; history goes in citations |
| The chapter ships its own DPLL, CDCL, Tseitin builder and ROBDD | RN Q1, Q4, B, D: they reproduce every curve; their counts are exact and version-proof (RN P3) |
| Production solvers appear in chapter tables with the version in the caption, never in a `run.out` | RN P3, C.3 |
| The FIFO model is a wrapper with reset and occupancy written as hardware, lowered by `informal lower` | RN E.2, P8 |
| "Bound k" means k transitions and k+1 states, state 0 is the reset cycle, as in Chapter 9 | RN P7; `@sec-ch09-formal` defines depth the same way |
| Multiplier hardness is presented as measured, with the BDD theorem and the *existence* of short resolution proofs both stated | RN 2.3, constraint 4.1(1) |
| Epigraph is the book's own sentence, as in the other chapters | no verbatim quotation is needed |

**Left to the author (RN section 5):** whether to add `python-sat` and
`dd` to the book's environment. This outline assumes not. If added,
only the `run.out` of sections 5 and 6 gains a column.

## 2. Front matter

**Epigraph (own words, one line; drafter may improve):**
> A solver answers one question: is there an assignment? Everything
> else is how you ask.

**Learning objectives (the callout; each is tested by a section and an
exercise).** After this chapter you can:

1. turn "is this always true", "are these two circuits the same" and
   "can this state be reached in k cycles" into one question, *is
   this formula satisfiable*, and say what a "yes" and a "no" mean for
   the design;
2. encode a gate-level circuit as clauses by hand, read and write the
   DIMACS file, and predict its size from the gate count;
3. trace unit propagation, a decision, a conflict and a learned clause
   on a small formula, and say what each of DPLL, clause learning and
   an activity heuristic changed in a measured table;
4. build a reduced ordered BDD for a small function, use canonicity to
   decide equivalence, and predict from the variable order whether an
   adder's BDD is linear or exponential;
5. read an and-inverter graph in AIGER and a transition system in
   Btor2, and say which lines are state, which are the property and
   which are the environment;
6. state a bit-vector question in z3's Python interface, say when the
   answer came from rewriting and when from search, and name two
   places where bit-vector semantics differ from SystemVerilog's;
7. unroll a sequential design into one satisfiability query per bound,
   find the first chapter's FIFO bug at its depth, and explain why
   "no counterexample up to k" is not a proof;
8. recognize the four ways these engines blow up (search without
   learning, formulas with only long proofs, structure the solver does
   not see, a bad variable order) and say which is a theorem and which
   is an observation.

Word budget for title, epigraph and objectives: 250.

## 3. Sections

Budgets sum to 11,650 words (target band 9,000 to 12,000).
"Reader can" is the gate-1 outcome for the section. Example paths are
under `examples/ch17-logic-and-solvers/`. Figures are written by
`figures/gen_ch17_figures.py` (one function per figure, reading the
examples' `run.out` and source files; at most 1000 px wide; the
palette of `figures/blocks.py`; gates and registers with
`figures/hw.py`). The script needs one new helper, a line chart with a
logarithmic axis drawn as SVG polylines; it belongs in the generator
or in `blocks.py`, the drafter's choice.

### 3.1 Motivation: the sixteen, and the eleven bits (no label needed beyond the opener; ~600 words)

- **Content.** Two facts the reader already half owns. (a) Chapter 9's
  report line `FullBackward_A assert cex informal-kind depth 16`
  (spliced from `examples/ch09-temporal-properties/fifo-formal/run.out`),
  and Chapter 7's `randomize()` that pipes SMT-LIB to z3
  (`@sec-ch07-solver`): two tools, one kind of engine underneath,
  neither chapter said what it does. (b) The same class of engine that
  disposes of the FIFO in a tenth of a second does not finish an
  11-bit multiplier commutativity check in 100 seconds, while a
  128-bit adder check takes a tenth of a second (RN C.1, G). The
  chapter is the distance between those two facts.
- **Reader can:** say what the chapter will let them reproduce (the
  16) and what it will let them predict (which questions are cheap).
- **Splices:** `ch09.../fifo-formal/run.out` (first rows only, by an
  include of the existing file); nothing new.
- **Figure `fig-ch17-map`:** one diagram for the whole chapter: three
  questions (always true? equal? reachable in k?) into one formula;
  three representations (CNF, BDD, AIG) and the word level above them;
  the tools of the book attached where measured (Verilator's
  `randomize()` to z3; InFormal to Btor2 and AIGER). Drawn with
  `blocks.py`.
- **Sources:** `@sec-ch09`, `@sec-ch07-solver`; no external claim.
- **Constraint:** the 11-bit and 128-bit figures are measurements of
  named solver versions and are introduced as such (RN C.1, G).

### 3.2 Propositional logic in the amount a verifier needs {#sec-ch17-logic} (~900 words)

- **Content.** Variables, connectives, assignment, truth table;
  satisfiable, valid, equivalent, and the two reductions every later
  section uses: *F is valid iff not-F is unsatisfiable*; *F and G are
  equivalent iff F xor G is unsatisfiable*. A SystemVerilog expression
  over one-bit signals is a formula; an `assign` is a definition.
  Literal, clause, conjunctive normal form; why CNF (a clause is a
  constraint that can be violated in exactly one way). Why not
  truth tables: 2^n rows, shown by running one. Boole and Shannon in
  two sentences (Shannon 1938 is the paper that made switching
  circuits an algebra).
- **Definition callouts (2):** satisfiable / valid / equivalent;
  literal / clause / CNF.
- **Reader can:** rewrite a validity or equivalence question as a
  satisfiability question; say what the satisfying assignment *is* in
  each case (a counterexample, a distinguishing input).
- **Example `truth-table/`** (python): `full_adder.sv` (the five-gate
  column of RN A), `truth.py` enumerates the 8 rows from a Python
  transcription and checks two forms of the carry equal by exhaustion;
  prints the table and the row count for 2, 16, 32, 64 inputs
  (arithmetic, not run).
- **Figure:** none (the truth table is the `run.out`).
- **Sources:** Shannon 1938 [V-CR]; Boole 1854 named only in further
  reading unless opened (RN 2.1: unverified); Kroening and Strichman
  ch. 1-2 for the definitions.
- **Constraints:** no quotation from Boole or Shannon (RN 4.1(12)).

### 3.3 From gates to clauses {#sec-ch17-tseitin} (~1,000 words)

- **Content.** The naive route (distribute to CNF) explodes; the fix
  is to name every wire: one variable per gate output, a few clauses
  per gate that say "output equals function of inputs". The three
  clauses of an AND, the four of an XOR, derived from the implication
  both ways, not memorized. The full adder by hand: 8 variables, 17
  clauses. The question as unit clauses. Equisatisfiable is not
  equivalent (the new variables). DIMACS in six lines of explanation.
  Then the same circuit through tools: sizes differ (17, 100, 10
  clauses) and all answer alike. Size rule: 3 clauses per AND gate.
- **Definition callout:** equisatisfiable; Tseitin encoding.
- **Pitfall callout:** an encoding is only as good as the pipeline
  that made it: the one-clause export that calls a false formula
  satisfiable (RN P6), told as a caution against hand-rolled tactic
  chains, with no z3 internals claimed.
- **Reader can:** encode a netlist of AND/OR/XOR/NOT by hand; write
  the DIMACS file; predict clause count from gate count; say why the
  encoded formula has more variables than the circuit has inputs.
- **Examples.**
  - `tseitin/` (python): `full_adder.cnf` (hand-written, commented,
    as in RN appendix), `tseitin.py` (the gate-by-gate builder, 37
    code lines), `encode.py` builds the same adder with the builder
    and compares it with the hand file. The research builder makes an
    OR by De Morgan from an AND, so its variable for `cout` has the
    opposite polarity and the clause sets match only after that
    renaming; either give the builder a direct `or_` so the files are
    equal as sets of clauses, or print "equal after renaming one
    variable". Measure, then word the `run.out` line.
  - `tseitin-tools/` (bash, `REQUIRES := yosys`): Yosys `aigmap` and
    `write_aiger -ascii` (9 ANDs), `yosys-abc` `strash` (7 ANDs, 8
    variables, 17 clauses), Yosys `sat -dump_cnf` (40 variables, 100
    clauses). Skips where Yosys is absent.
- **Figure `fig-ch17-tseitin`:** the full adder drawn with `hw.py`,
  every wire carrying its DIMACS number, and beside each gate its
  clause group; generated from `full_adder.cnf`'s comments.
- **Sources:** Tseitin (cite the 1983 reprint, "first published in
  Russian in 1968"; RN 2.1); Plaisted and Greenbaum 1986 for the
  one-direction refinement, one sentence, only if read; Handbook 2nd
  ed. chapter on CNF encodings in further reading.
- **Constraints:** RN 4.1(4) (no claim about the contents of
  Tseitin's paper beyond "introduced the naming of subformulas", and
  that only if the reprint is read); RN P10 (Yosys prints 9, the 7
  needs ABC or InFormal); tool sizes are of Yosys 0.68.

### 3.4 Search: assign, propagate, backtrack {#sec-ch17-dpll} (~900 words)

- **Content.** Unit propagation as the one inference rule (a clause
  with all literals false but one forces the last). The full-adder
  question with `a = 0` falls to propagation alone: 0 decisions,
  walked literal by literal. Then decisions and chronological
  backtracking: DPLL in 85 lines. The miter: two adders, XOR the
  outputs, OR the XORs, ask for 1. Run it: 15, 63, 255, 1,023, 4,095,
  16,383 decisions for 2 to 7 bits, exactly 4^N - 1. Explanation: the
  inputs are numbered first, so the search enumerates every input
  pair; DPLL in this order *is* exhaustive simulation. That sentence
  ties the chapter to the reader's daily tool.
- **Definition callout:** unit propagation; miter (no attribution of
  the coinage, RN 4.1(4)).
- **Reader can:** carry out unit propagation by hand on ten clauses;
  build a miter for two combinational blocks; explain the 4^N - 1.
- **Example `dpll/`** (python): `dpll.py`, shared `common/dimacs.py`,
  `common/gen.py` (adder miter, pigeonhole, multiplier miter, random
  3-SAT), `run_dpll.py` prints the adder-miter table for 2..7 bits
  plus the full-adder trace (the assignment order under propagation).
  3.9 s at 7 bits (RN B); 8 bits (17.6 s) is left to an exercise.
- **Figure `fig-ch17-search`:** the search tree of `dpll.py` on the
  2-bit miter (15 decisions), drawn from a trace the example writes;
  conflicts as leaves.
- **Sources:** Davis and Putnam 1960; Davis, Logemann and Loveland
  1962 [both V-CR; contents not read: attribute the procedure by name
  only].
- **Constraints:** RN P12 (cost of the pure-Python propagation), P13
  (the result depends on the numbering, and the text must say so).

### 3.5 Learning from conflicts {#sec-ch17-cdcl} (~1,400 words)

- **Content.** What DPLL throws away: the *reason* for a conflict.
  The trail with decision levels and a reason clause per implied
  literal; the implication graph; resolving the conflict clause
  backwards along the trail to the first unique implication point;
  the learned clause; jumping back to the level where it becomes
  unit. Each step shown on one conflict from the 3-bit miter, taken
  from a trace the example prints. Two watched literals in one
  paragraph (why propagation is cheap), restarts and clause deletion
  named and not implemented. Then the table: same instances, same
  order, learning on: 12, 27, 54, 106, 208, 410, 812 conflicts: 2^N
  in place of 4^N. Then the 35-line subclass that changes only which
  variable is picked: 476, 493, 553, 1,075, 1,723 conflicts at 8, 10,
  12, 16, 32 bits. Three ideas, three curves. Learning also wins on
  the bugged (satisfiable) miters: 263 against 15 decisions/conflicts
  at 8 bits. An "unsat" is a proof: the learned clauses, in order, are
  a derivation of the empty clause, which is why a solver's "no bug"
  can be checked by a second program (one sentence, with DRAT-trim
  cited, tied to the "verdicts certified" of the book's formal tool).
- **Definition callouts (2):** implication graph and first UIP;
  learned clause.
- **In Practice callout:** what a production solver adds beyond these
  150 lines (preprocessing, restarts, clause deletion, inprocessing),
  with a chapter table of CaDiCaL's conflicts on the same files,
  captioned with the solver version (147 at 8 bits to 883 at 32 with
  CaDiCaL 1.9.5; RN B).
- **Reader can:** given a trail and a conflict, derive the first-UIP
  clause and the backjump level by hand; read the solver's statistics
  line; say which of the three curves each idea produced.
- **Example `cdcl/`** (python): `cdcl.py` (149 code lines; spliced in
  three parts: `propagate`, `analyze`, `solve`), `cdcl_vsids.py`,
  `selftest.py` (agreement with z3 on 3,000 random formulas of up to
  25 variables; the research run used MiniSat for this, so re-measure
  with z3 as the referee), `run_cdcl.py` prints the three-solver
  table: adder 2..8, 10, 12 for `cdcl.py` (12 bits: 4.6 s), and to 32
  for `cdcl_vsids.py`; plus one fully printed conflict analysis.
- **Figures.** `fig-ch17-implication`: the implication graph of that
  conflict, decision levels as columns, the first-UIP cut marked,
  generated from the printed trace. `fig-ch17-learning`: decisions or
  conflicts against width on a log axis, three curves, from
  `dpll/run.out` and `cdcl/run.out`.
- **Sources:** Marques-Silva and Sakallah 1996/1999 (clause learning,
  non-chronological backtracking); Moskewicz et al. 2001 (watched
  literals, VSIDS; the authors' own "one to two orders of magnitude"
  may be quoted as their claim, RN 2.2); Zhang et al. 2001 (first
  UIP); Een and Sorensson 2004 (the small solver as a genre); Wetzler,
  Heule and Hunt 2014 (proof checking); Handbook 2nd ed. ch. 4.
- **Constraints:** RN 4.1(2), 4.1(4) (attribute ideas at title level
  unless the papers are read; the statement "CDCL corresponds to
  resolution" needs Beame, Kautz, Sabharwal 2004 or the Handbook
  chapter read first); RN P14 (line counts); the heuristic in
  `cdcl_vsids.py` is "an activity heuristic in the style of VSIDS",
  not VSIDS itself.

### 3.6 Why it is sometimes hard {#sec-ch17-hard} (~1,100 words)

- **Content.** Four different reasons, kept apart.
  1. *Worst case.* Cook 1971 in today's terms: every problem whose
     answers can be checked quickly reduces to this one; nobody knows
     a method that is fast on all formulas. What that does not say:
     that *your* formula is hard (the FIFO is not).
  2. *Formulas with only long proofs.* Pigeons and holes: 56 variables
     at 7 holes, and every solver in the chapter multiplies its work
     per added hole (table from `run.out`; chapter table with MiniSat
     and CaDiCaL to 10 holes: 10.7 million and 2.2 million conflicts,
     versions in the caption). Haken 1985: resolution proofs of these
     formulas are exponentially long, and a clause-learning run that
     ends in "unsat" has written a resolution proof. Hardware reading:
     counting arguments (a FIFO cannot hold more than it holds, an
     arbiter grants at most one) are what search is bad at, which is
     why the techniques chapter will hand the solver an invariant.
  3. *Structure the solver does not see.* `a*b` against `b*a`:
     conflicts multiply by about four per bit with a production solver
     (36 thousand at 8 bits, 573 thousand at 10; chapter table) and by
     about 3.6 with the book's (3,655 at 7 bits in `run.out`), while
     the adder stays linear. Here the activity heuristic *loses* to
     the fixed order (7,232 against 3,655): a heuristic is a bet. And
     the careful statement: this is not a theorem. Short resolution
     proofs of multiplier commutativity exist (Beame and Liew);
     solvers do not find them.
  4. *Density.* Random 3-SAT: easy when clauses are few (almost any
     assignment works) or many (a contradiction is found at once),
     hardest near 4.3 clauses per variable, where half the formulas
     are satisfiable (Mitchell, Selman, Levesque 1992; the chapter's
     own 60-variable run peaks between 4.2 and 4.6). Verification
     formulas are not random; the point is that hardness is a property
     of the formula, not of its size.
- **Pitfall callout:** "it timed out, so it is hard" and "it is small,
  so it is easy" are both wrong: 110 variables took 2.2 million
  conflicts; 1,795 variables took 195.
- **Reader can:** look at a property and name which of the four risks
  it carries (arithmetic, counting, neither); explain to a colleague
  why NP-completeness does not make formal verification hopeless;
  state exactly what is proved and what is observed about multipliers.
- **Example `hard/`** (python): `run_hard.py` with the book solvers:
  pigeonhole 4..7 (37, 145, 602, 2,384 conflicts with `cdcl.py`),
  multiplier miter 2..7 beside adder miter 2..7, random 3-SAT at 60
  variables, 30 seeds per ratio, 8 ratios (satisfiable fraction and
  median conflicts). About 8 s in total (RN J, K).
- **Figure `fig-ch17-hard`:** two panels from `hard/run.out`: conflicts
  against width for adder and multiplier (log axis); satisfiable
  fraction and median conflicts against clause/variable ratio.
- **Sources:** Cook 1971 (Theorem 1 as printed is about DNF
  tautologies; RN 2.1); Haken 1985; Mitchell, Selman and Levesque
  1992; Beame and Liew (arXiv 1705.04302, and the venue once
  verified); Bryant 1991 is held for 3.7; Kaufmann, Biere and Kauers
  2019 in one forward sentence at most.
- **Constraints:** RN 4.1(1), (2), (6), (7); RN P3 (production counts
  in captioned tables only); RN F (z3's SAT core is ten times better
  than MiniSat on pigeons: do not say "all solvers take the same").

### 3.7 A canonical form: binary decision diagrams {#sec-ch17-bdd} (~1,100 words)

- **Content.** A different bargain: spend the effort building a
  representation in which every question is then trivial. Decision
  tree from Shannon's expansion; fix a variable order; merge equal
  subgraphs, drop tests whose branches agree; the result is unique
  for the function and the order. Consequences: equivalence is "same
  node", satisfiability is "not the 0 node", counting solutions is a
  walk. `apply` with a memo table in twenty lines. Then the cost: the
  carry of an n-bit adder is 3n - 1 nodes with the operands
  interleaved and 2^(n+1) - 2 with them separated (both closed forms
  fit every measured row to n = 12), with the reason in one picture:
  the separated order must remember all of `a` before it sees any of
  `b`. Multiplication: the middle product bit grows about 2.4 times
  per bit in every order tried, and here there is a theorem (Bryant
  1991: exponential for every order; Woelfel 2005 sharpens it). Why
  BDDs still matter: the first model checkers that handled real
  designs were BDD-based (Burch et al.), and the contrast explains
  the next two sections: SAT gives up canonicity to avoid the size.
- **Definition callout:** reduced ordered BDD; canonical form.
- **Pitfall callout:** node counts depend on the package's conventions
  (terminals counted or not, complement edges); the chapter's counts
  are decision nodes of its own package (RN P4).
- **In Practice callout:** a BDD answers "how many" and "all
  solutions" where a SAT solver answers "one": the link to Chapter
  7's uniform-sampling discussion (`@sec-ch07-solver`), by pointer.
- **Reader can:** build the ROBDD of a three-variable function by
  hand under a given order; decide equivalence of two small circuits
  by building both; predict linear or exponential for an adder from
  the order; say why a multiplier defeats the method.
- **Example `bdd/`** (python): `robdd.py` (67 lines), `run_bdd.py`:
  (i) the two carry circuits of 3.4 give the same node (equivalence
  by canonicity, no search); (ii) carry size for n = 1..10 under two
  orders; (iii) multiplier bit n-1 for n = 2..10 under three orders.
  Under 1 s (RN D).
- **Figure `fig-ch17-bdd`:** the BDD of the 3-bit carry under both
  orders (8 and 14 decision nodes), laid out by level, generated by
  walking `robdd.py`'s node table.
- **Sources:** Bryant 1986; Akers 1978 (one clause of history, only if
  wanted); Brace, Rudell and Bryant 1990 (unique and computed tables);
  Bryant 1991 and Woelfel 2005 (the bound, as stated in Woelfel's
  abstract until Bryant 1991 is read); Bollig and Wegener 1996 (best
  order is NP-complete to improve); Burch et al. 1990/1992.
- **Constraints:** RN 4.1(3), (4), (5): the growth is "consistent
  with", not "confirms"; no attribution of the adder example to
  Bryant 1986 unless read; 10^20 only as a title.

### 3.8 And-inverter graphs, and the files tools exchange {#sec-ch17-aig} (~800 words)

- **Content.** One gate type and inverted edges: every circuit as
  two-input ANDs. Not canonical, but cheap: equal ANDs are shared as
  they are built (structural hashing), so the full adder is 9 ANDs as
  Yosys writes it and 7 after hashing. An AIG is one step from CNF
  (three clauses per AND), which is why it sits between RTL and the
  solver. The AIGER text format read line by line on the full adder:
  header `aag M I L O A`, a literal is twice the variable plus a sign
  bit, 0 and 1 are the constants. Latches make it sequential; AIGER
  1.9 adds bad-state and constraint lines and a reset value per latch.
  One level up, the same idea with words: Btor2, read line by line on
  a 3-bit counter (20 lines: `sort`, `input`, `state`, `init`, `next`,
  `bad`). This is the model the book's formal tool builds from
  SystemVerilog, and the reader can now print it and count it.
- **Definition callout:** and-inverter graph; structural hashing.
- **Reader can:** decode an `aag` file by hand; identify state,
  property and environment lines in a Btor2 file; obtain both from a
  SystemVerilog file with the book's tools and read the size line.
- **Examples.**
  - `tseitin-tools/` (from 3.3) supplies `fa.aag`.
  - `counter-model/` (informal; `REQUIRES := informal`):
    `counter.sv` (stops at 6, asserts at most 5), `run_model.sh`:
    `informal lower` (20 lines of Btor2, checked in as
    `counter.btor2` so the chapter can splice it where the tool is
    absent), `informal info`, `informal simp` (23 to 19 ANDs),
    `informal simp --aag`, `informal check --only informal-bmc`
    (`UNSAFE ... depth 6`). The `(x ms)` fields are filtered.
- **Figure `fig-ch17-aig`:** the full adder as an AIG, drawn from
  `fa.aag`, inverted edges dotted, the two duplicated ANDs marked.
- **Sources:** Kuehlmann et al. 2002; Biere, AIGER report 07/1;
  Biere, Heljanko and Wieringa, report 11/2; Niemetz et al. 2018
  (Btor2); the InFormal repository entry already in `refs.bib`.
- **Constraints:** RN P2 (`--engines`), P8, P9, P10, P11; RN 4.1(11):
  describe `simp` by the sizes it prints.

### 3.9 Words, not bits: bit-vector SMT {#sec-ch17-smt} (~1,000 words)

- **Content.** Chapter 7 met this solver as a black box behind
  `randomize()`: constraints out in SMT-LIB, a model back. Here it is
  asked the other kind of question, where the hoped-for answer is
  *unsat* (no counterexample). The theory of fixed-size bit-vectors:
  sorts by width, arithmetic modulo 2^m, unsigned and signed versions
  of comparison, division and shift as different operators. In z3's
  Python interface: declare, assert the negation, `check()`. Two
  routes inside the solver, shown by measurement, not by description:
  `a*b != b*a` is decided at 64 bits in no measurable time because
  the two sides rewrite to the same term; the same theorem about a
  shift-and-add multiplier written with word-level operators has no
  such rewrite and its time multiplies per bit (0.8 s at 8 bits; the
  chapter table goes to 11 with the version in its caption). Reducing
  words to bits is the Tseitin encoding of 3.3 applied to an adder or
  multiplier circuit per operator ("bit-blasting"); the chapter's
  `gen.py` did exactly that by hand. The word level helps when
  algebra applies and costs nothing when it does not.
- **Definition callout:** satisfiability modulo theories; bit-blasting.
- **Pitfall callout (two bit-vector/SystemVerilog differences):**
  division by zero is defined in SMT-LIB (`bvudiv` gives all ones,
  `bvurem` the dividend) where SystemVerilog gives X; and there is no
  X or Z at all: a two-valued model, the same boundary Chapter 5 drew
  for testbench types (by label).
- **In Practice callout:** which engine sits under which tool of the
  book, as measured in the book: Verilator's `randomize()` and z3
  (`@sec-ch07-solver`); InFormal lowering to Btor2 and bit-blasting to
  an AIG for its in-house engines (RN E; the findings note records
  that its word-level path was not built).
- **Reader can:** state and check an 8-bit identity or find a
  counterexample to a false one in z3py; tell from timing-by-width
  whether rewriting or search answered; name the two semantic traps.
- **Example `bitvector/`** (python, needs `z3`; prints `skipped: ` if
  the import fails): `word_vs_bits.py` reduced to verdicts for widths
  4..8 on the three routes, `z3.simplify(a*b != b*a)` printing
  `False`, a false identity (`a - b == b - a`) with its model checked
  by evaluation, and `bvudiv` by zero. No times in `run.out`.
- **Figure:** none new; the chapter table of seconds against width
  (RN G) carries it.
- **Sources:** SMT-LIB 2.6 (in `refs.bib`) and the
  `FixedSizeBitVectors` theory page; de Moura and Bjorner 2008;
  Kroening and Strichman ch. 6; Handbook ch. 33; Niemetz and Preiner
  2023 named as the bit-vector solver the formal tool can use.
- **Constraints:** RN 4.1(8), (9), (10); RN P1 (which Python), P6 (no
  sizes from z3's CNF export).

### 3.10 Worked example: adding a clock {#sec-ch17-example} (~1,400 words)

- **Content.** A sequential design is three formulas: which states
  are initial, which pairs of states are one step, which states are
  bad. "Reachable in k steps" is their conjunction over k+1 copies of
  the variables: copy the circuit once per cycle and wire each
  frame's next-state outputs to the next frame's registers. First on
  the counter of 3.8 (bound 6, 141 variables). Then the FIFO:
  1. `fifo_bmc.sv`: the first chapter's FIFO, a reset held for one
     cycle, the contract's occupancy counter and one assertion, all
     as hardware, because a formula has no reset unless one is
     written (the shell of Chapter 9 wrote it for the reader).
  2. `informal lower` then `info` and `simp`: 146 state bits and 992
     ANDs become 10 latches and 102 ANDs once only the logic the
     property depends on is kept; the memory is gone.
  3. `bmc_aag.py`: 97 lines that read the AIGER file and write one
     CNF per bound: 105 variables and 307 clauses per frame. Solved by
     the chapter's own `cdcl.py`: unsatisfiable for bounds 0 to 15,
     satisfiable at 16, 1,795 variables, 195 conflicts, a tenth of a
     second. The model, read back frame by frame, is Chapter 9's
     table: reset, then fifteen pushes, `count` at 15, `full` high,
     `occ` at 15.
  4. The same at the word level, by hand: `unroll_z3.py`, state
     `(count, occ)` after reset, satisfiable at bound 15. One cycle
     fewer, because state 0 is after reset here and is the reset cycle
     there; the chapter fixes the convention.
  5. The repaired FIFO: no counterexample at any bound tried, and each
     further bound costs more (20 bounds in 0.6 s, 40 in 9 s with z3).
     How many bounds are enough? That question is the next chapter.
- **Worked Example callout:** the five steps as a numbered recipe the
  reader can apply to another design (exercise 9 does).
- **Pitfall callout:** "depth", "bound" and "step" differ by one
  between tools and between a model with a reset cycle and one
  without (RN P7).
- **Reader can:** write the unrolled formula for a small counter by
  hand; run the five steps on the FIFO and explain each number in the
  output; say precisely what "UNSAT at bound k" does and does not
  establish.
- **Examples.**
  - `fifo-model/` (informal; `REQUIRES := informal`): `fifo_bmc.sv`
    (includes the first chapter's `fifo.sv` by path), `run_model.sh`:
    lower, info, simp, `--aag`, `check --only informal-bmc` (depth
    16), and a comparison of the regenerated AIGER with the checked-in
    `fifo_bmc.aag`. Lint with Verilator.
  - `fifo-unroll/` (python, no tool needed): checked-in
    `fifo_bmc.aag`, `bmc_aag.py` (unroller; solves with
    `../cdcl/cdcl.py`), `run.out`: the model size line, one verdict
    line per bound with variables, clauses and the book solver's
    conflicts, and the per-frame `count`, `occ`, `full` read from the
    model (forced values only, RN P5). Also runs the counter's
    checked-in AIGER (bound 6).
  - `fifo-unroll-z3/` (python, needs `z3`): `unroll_z3.py bug` and
    `fixed 20`; verdict lines only.
- **Figures.** `fig-ch17-unroll`: three frames of a two-register
  circuit, the latch-to-next-state wires shared between frames, the
  bad output taken from the last frame. `fig-ch17-bound`: per bound,
  the verdict and the book solver's conflicts on the bugged FIFO
  (from `fifo-unroll/run.out`).
- **Sources:** Biere, Cimatti, Clarke and Zhu 1999 (the unrolled
  formula, its Definition 10; the DAC 1999 companion); Chapter 9 by
  label; the InFormal entry in `refs.bib`.
- **Constraints:** RN P5, P7, P8, P9; RN 4.1(11); nothing about
  induction, completeness thresholds or IC3 beyond the closing
  question (section 6 below); the 9 s figure is z3 5.4.1 on the
  research machine and goes in prose as a dated measurement or stays
  out of the text (times never in `run.out`).

### 3.11 Future directions (~250 words; one Future Directions callout)

Clearly labelled as open or recent, with no result claimed: solvers
that find the short multiplier proofs that are known to exist, and
the algebraic methods used meanwhile (Kaufmann, Biere, Kauers 2019,
only if read); proof-producing solving as the norm, so that an
"unsat" is an artifact a small checker validates; word-level model
checking on Btor2 without bit-blasting. One sentence pointing at the
book's last part for learned heuristics, with no claim.

### 3.12 Summary (~300 words)

Eight bullets mirroring the objectives, each with its measured number
(17 clauses; 4^N - 1 against 2^N against linear; 3n - 1 against
2^(n+1) - 2; four times per bit; 4.3; bound 16), and a closing table
`tbl-ch17-engines`: representation (CNF + search, BDD, AIG, word
level) by "canonical?", "what is cheap", "what blows up", "where the
book's tools use it".

### 3.13 Exercises (~500 words; list in section 5 below)

### 3.14 Further reading (~150 words)

Names, authors, editions only (house rule): Handbook of
Satisfiability, 2nd ed. (chapters on CDCL, CNF encodings, proof
complexity, bounded model checking, SMT); Kroening and Strichman,
*Decision Procedures*, 2nd ed.; Knuth, *The Art of Computer
Programming*, Volume 4B (only if the bibliographic details are
verified); Bryant 1986; Biere et al. 1999; Een and Sorensson 2004 as
the next solver to read after the chapter's; Boole 1854 if opened.

### Budget

| section | words |
|---|---|
| title, epigraph, objectives | 250 |
| 3.1 motivation | 600 |
| 3.2 logic | 900 |
| 3.3 gates to clauses | 1,000 |
| 3.4 DPLL | 900 |
| 3.5 clause learning | 1,400 |
| 3.6 why hard | 1,100 |
| 3.7 BDDs | 1,100 |
| 3.8 AIGs and formats | 800 |
| 3.9 bit-vector SMT | 1,000 |
| 3.10 worked example | 1,400 |
| 3.11 future directions, 3.12 summary, 3.13 exercises, 3.14 further reading | 250 + 300 + 500 + 150 = 1,200 |
| **total** | **11,650** |

Callout census (six kinds only): Definition x 9 (two each in 3.2 and
3.5, one each in 3.3, 3.4, 3.7, 3.8, 3.9); Pitfall x 5 (3.3, 3.6,
3.7, 3.9, 3.10); In Practice x 3 (3.5, 3.7, 3.9); Worked Example x 1
(3.10); Future Directions x 1; Exercise x 1 (the list).

## 4. Example directories

All under `examples/ch17-logic-and-solvers/`. Every Python file at
most 80 columns; every example has `lint` (byte-compile, or Verilator
on the `.sv`) and `run`; `run.out` is written by
`scripts/check-examples.sh`. `EXPECT_OUTPUT` names a line that only a
real run prints.

| directory | language | needs | files | `run.out` (expected content, from RN) | time |
|---|---|---|---|---|---|
| `common/` | python | — | `dimacs.py`, `tseitin.py`, `gen.py` | (library; no run) | — |
| `truth-table/` | python | — | `full_adder.sv`, `truth.py` | 8-row truth table of `sum`, `cout`; "two carry forms agree on 8 of 8 rows"; rows needed at 16, 32, 64 inputs | < 1 s |
| `tseitin/` | python | — | `full_adder.cnf`, `encode.py` | "8 variables, 17 clauses"; the comparison line of 3.3 (wording fixed after measuring); "sum=1 cout=1 a=0: UNSATISFIABLE, 0 decisions, 8 propagations"; "sum=1 cout=1: SATISFIABLE a=1 b=1 cin=1" | < 1 s |
| `tseitin-tools/` | bash | `yosys` | `run_tools.sh` (reads `../truth-table/full_adder.sv`) | `aag 12 3 0 2 9` and the nine AND lines; ABC: `and = 7`, `Vars = 8. Clauses = 17.`; Yosys SAT: `p cnf 40 100`; ANSI color codes of ABC stripped | 2 s |
| `dpll/` | python | — | `dpll.py`, `run_dpll.py` | propagation trace of the full-adder query; table width / variables / clauses / decisions: 15, 63, 255, 1,023, 4,095, 16,383 for 2..7 bits; "4^N - 1 in every row" | 5 s |
| `cdcl/` | python | `z3` for `selftest.py` only | `cdcl.py`, `cdcl_vsids.py`, `selftest.py`, `run_cdcl.py` | one conflict analyzed step by step (trail, conflict clause, resolvents, learned clause, backjump level); table adder 2..12: conflicts 12, 27, 54, 106, 208, 410, 812, 3,216 (10), 12,820 (12) for `cdcl.py`; 13 .. 1,723 to 32 bits for `cdcl_vsids.py`; bugged miters 8 and 12 bits: 263/15 and 4,107/23 | 8 s |
| `hard/` | python | — | `run_hard.py` | pigeonhole 4..7: DPLL decisions 51, 374, 3,245, 32,780; `cdcl.py` conflicts 37, 145, 602, 2,384; multiplier miter 2..7: 8, 25, 87, 282, 1,014, 3,655 (`cdcl.py`) and 8, 27, 125, 452, 2,008, 7,232 (`cdcl_vsids.py`); 3-SAT at 60 variables: satisfiable 30, 30, 29, 21, 6, 0, 0, 0 of 30 and medians 1, 4, 18, 79, 105, 83, 74, 58 | 12 s |
| `bdd/` | python | — | `robdd.py`, `run_bdd.py` | "ripple carry and majority carry: same node" for n = 4; carry sizes 2, 5, 8, ... 29 and 2, 6, 14, ... 2,046 for n = 1..10; multiplier bit n-1: 7, 14, 34, 71, 167, 379, 926, 2,186, 5,246 (interleaved), with the two other orders | 1 s |
| `counter-model/` | informal | `informal` | `counter.sv`, `counter.btor2` (checked in), `run_model.sh` | the 20 Btor2 lines; `"state_bits": 3`, `"bad": 1`; `loaded inputs 2 latches 3 ands 23 ...` / `simplified inputs 1 latches 3 ands 19 ...`; `UNSAFE (by informal-bmc, depth 6)`; "regenerated Btor2 equals the checked-in file" | 1 s |
| `bitvector/` | python | `z3` | `word_vs_bits.py` | per width 4..8: `unsat unsat unsat` for the three routes; `simplify(a*b != b*a) = False`; `a - b == b - a: counterexample found, checked by evaluation` (values not printed); `bvudiv(x, 0) = 255` at 8 bits | 3 s |
| `fifo-model/` | informal | `informal` | `fifo_bmc.sv`, `run_model.sh` | `"state_bits": 146`, `"bad": 1`, `"constraints": 1`; `loaded inputs 28 latches 146 ands 992 bads 1 constraints 1`; `simplified inputs 3 latches 10 ands 102 bads 1 constraints 1`; `aag 115 3 10 0 102 1 1`; `UNSAFE (by informal-bmc, depth 16)`; "AIGER equals `../fifo-unroll/fifo_bmc.aag`" | 1 s |
| `fifo-unroll/` | python | — | `fifo_bmc.aag`, `counter.aag` (checked in), `bmc_aag.py` | counter: bounds 0..5 UNSAT, 6 SAT (141 variables, 400 clauses); FIFO: `model: 3 inputs, 10 latches, 102 ANDs`; bounds 0..15 UNSAT, bound 16 SAT at 1,795 variables and 5,220 clauses plus the property unit; `cdcl.py` conflicts per bound (to be re-measured in this non-incremental form; 185 at bound 15 and 195 at 16 in RN B); frame table with `count`, `occ`, `full` | 2 s |
| `fifo-unroll-z3/` | python | `z3` | `unroll_z3.py` | `bound 0: unsat` .. `bound 14: unsat`, `bound 15: sat`; fixed: `no counterexample within 20 cycles of reset` | 1 s |

Thirteen directories, twelve with a run; nine need nothing beyond
Python (plus `z3` for three scripts), three need a tool and skip
without it. Whole set under 40 s.

Things the drafter must measure again because the example form
differs from the research form (RN is evidence for the shape, not for
these exact strings): `selftest.py` with z3 as referee; `bmc_aag.py`
solving with `cdcl.py` per bound and decoding `count`/`occ` from the
model (needs the latch order of the `.aag`, RN P9); the `run_*.py`
drivers' table layout; `truth.py`.

## 5. Exercises (each has one determinate answer; solutions go to the solutions appendix)

1. **Encode by hand.** Write the DIMACS file for a 2-to-1 multiplexer
   `y = s ? a : b` built from two ANDs, one OR and one inverter, one
   variable per wire. How many variables and clauses? *(7 variables
   and 11 clauses when the inverter's output has its own variable; 6
   variables and 9 clauses when the inverter is folded into a negated
   literal, as the chapter's builder does. The answer key gives
   both.)*
2. **Propagate.** On `full_adder.cnf` with the units `sum`, `cout`
   and `-a`, list the literals unit propagation assigns, in the order
   `dpll.py` assigns them, and name the clause that becomes empty.
   *(Checked against the trace in `dpll/run.out`.)*
3. **Predict, then run.** Without running it, how many decisions will
   `dpll.py` make on the 8-bit adder miter? Run it. *(65,535.)* Then
   renumber so that the miter's outputs come first and report the new
   count *(a number the solutions appendix records from a run)*.
4. **Analyze a conflict.** Given a printed trail with levels and
   reasons (taken from `cdcl/run.out`), derive the first-UIP clause
   and the backjump level by hand. *(The clause and level the run
   prints.)*
5. **A heuristic is a bet.** From `hard/run.out`, at which width does
   `cdcl_vsids.py` first need more conflicts than `cdcl.py` on the
   multiplier miter, and by what factor at 7 bits? *(3 bits; 7,232 /
   3,655 = 1.98.)*
6. **BDD by hand.** Draw the reduced ordered BDD of the majority of
   `a, b, c` under the order `a < b < c`; how many decision nodes?
   *(4.)* Is there an order with fewer? *(No: the function is
   symmetric, every order gives the same diagram.)*
7. **Order.** Using `robdd.py`, find the size of the 6-bit adder
   carry under the order `a0 a1 a2 b0 b1 b2 a3 a4 a5 b3 b4 b5` and
   place it between the two measured extremes *(a number from a run;
   between 17 and 126)*.
8. **Equivalence three ways.** Show that `(a & b) | (c & (a ^ b))`
   and `(a & b) | (a & c) | (b & c)` are equal by truth table, by a
   miter with `cdcl.py` *(UNSATISFIABLE)*, and by `robdd.py` *(same
   node)*. Which of the three would still work at 64 inputs, and why?
9. **Unroll another design.** Change `counter.sv` to stop at 5 as its
   comment says; show the unrolling is unsatisfiable to bound 20.
   Then widen the counter to 6 bits with the assertion at 50 and the
   stop at 51: at which bound is the first counterexample? *(51.)*
   What does that say about choosing a bound?
10. **Read a model.** In `fifo-model/run.out`, 146 state bits become
    10 latches. Which 10? *(count 4, occ 5, started 1.)* Which
    property of the first chapter's FIFO would keep the memory in the
    model? *(Any property over `rd_data`, i.e. data integrity; the
    techniques chapter returns to it.)*
11. **Word level.** In z3's Python interface, check `x & (x - 1) == 0`
    "iff x is a power of two" for 8-bit `x`; it is false. Give the
    one counterexample *(x = 0)* and repair the statement.
12. **Theorem or observation?** For each sentence say which it is and
    cite the source or the `run.out`: (a) pigeonhole formulas have no
    short resolution proofs; (b) multiplier commutativity has no
    short resolution proofs; (c) the middle bit of a multiplier has no
    small BDD under any order; (d) random 3-SAT is hardest near 4.3.
    *((a) theorem, Haken; (b) false: short proofs exist, Beame and
    Liew, and the slowness is an observation; (c) theorem, Bryant;
    (d) observation, Mitchell et al. and `hard/run.out`.)*

Answers marked "from a run" are fixed when the examples are written
and recorded in the solutions appendix; the question is determinate
either way.

## 6. Deliberately left to the two later formal chapters

**To Formal Property Verification:** how a bound becomes a proof
(k-induction, the failing induction step, completeness of simple-path
induction); IC3/PDR; interpolation; incremental SAT across bounds;
liveness, fairness and their encodings; assumptions, over-constraint
and vacuity as method; covers as reachability; engine selection and
portfolios; the reset model and its spurious `$past` counterexample
(already measured in Chapter 9); proof certificates beyond the one
sentence here; the three reference tables.

**To Formal Techniques:** every way of making the formula smaller or
the proof shorter: cone of influence as a named technique (this
chapter only prints the before/after sizes), black boxes, cut points,
counter and memory abstraction, symbolic constants and data
independence, helper invariants and decomposition (this chapter says
only that counting arguments are what search is bad at), case
splitting, assume-guarantee.

**To Equivalence, Structural and Static Verification:** equivalence
checking as a flow (matching, sequential equivalence, the tool
command); this chapter builds one combinational miter by hand and
uses the word.

**Stated here and not again:** propositional logic, CNF and DIMACS,
Tseitin encoding, DPLL and clause learning, BDD canonicity and
ordering, AIG and AIGER, Btor2 line reading, bit-vector semantics,
the unrolled formula. Later chapters cite these by label.

## 7. Gate-1 checklist

| requirement (AGENTS.md) | where met |
|---|---|
| every section names what the reader must be able to do | "Reader can" in 3.1 to 3.10; objectives 1 to 8 map to 3.2/3.4, 3.3, 3.4-3.5, 3.7, 3.8, 3.9, 3.10, 3.6 |
| the research note's constraints are folded in | each section's "Constraints" line cites RN 4.1 items and pitfalls P1 to P15; section 1 records the decisions they forced |
| house template | epigraph, objectives, motivation (3.1), concepts (3.2-3.9), worked example (3.10), callouts (census above, six kinds), future directions, summary, exercises, further reading |
| every listing a file under `examples/` | section 4; no code in prose |
| every number sourced | cited paper (RN section 2 status marks) or `run.out` (section 4); production-solver numbers in captioned tables |
| a question that changes the shape is raised, not chosen | RN section 5 and section 1 here: new Python dependencies or none |
| new glossary terms for the glossary appendix | satisfiable, valid, CNF, literal, clause, DIMACS, Tseitin encoding, equisatisfiable, unit propagation, DPLL, CDCL, learned clause, miter, BDD, variable order, AIG, structural hashing, AIGER, Btor2, SMT, bit-vector, bit-blasting, transition system, unrolling, bound |
| new `refs.bib` entries (about 30) | RN section 2; each needs the whole author field and title checked against the document, since Crossref gives initials for IEEE records |

Open items that do not block gate 1 but block drafting specific
sentences: the sources marked [U] in RN section 2 (Boole; the
contents of Bryant 1986, Haken 1985, GRASP, MiniSat, Kuehlmann et
al.; Rudell; Mishchenko et al.; Knuth; the venues of Beame and Liew).
A sentence that needs one of them waits until it is read or is cut.
