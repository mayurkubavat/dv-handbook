# Outline: Formal Techniques: Abstraction, Symbolic Reasoning and Decomposition

Date: 2026-11-16. Status: outline for gate 1. Evidence:
`research/ch19-formal-techniques.md` (cited as RN with a question,
measurement, catalog or recipe number: Q1 to Q4, M1 to M11, T1 to
T31, R1 to R6, section 7 item n as RN 7(n)), its measurement scripts
and outputs under `research/ch19-measurements/<name>/` (cited as
`<name>/run.out:<lines>`), and the tool survey
`research/informal-measurements/FINDINGS.md` (FM). Chapter file
`chapters/ch19-formal-techniques.qmd`, label `{#sec-ch19}`; third
chapter of the proof part, after
`chapters/ch18-formal-property-verification.qmd`, registered in
`_quarto.yml` under "Part IV · Proof and Probability", before the
generative-AI chapter. Design doc section 4, entry 19: "a catalog of
31 techniques in six families (shrinking the problem: black box, cut
point, counter and memory abstraction; symbolic constants and data
independence; modeling code; decomposition and helper invariants;
constraining and bug hunting; trusting the result), each entry with
the same six parts and a runnable example on InFormal".

Section 1 records the decisions and, in 1.2, **the places where the
measured evidence contradicts or qualifies a decision handed to this
outline**. Read 1.2 before anything else.

## 0. The chapter in one paragraph

The previous chapter ended on a grid: the pointer property of the
FIFO is out of reach of every in-house engine at 64 entries, and the
one row that stays proven at every size is "with the helper". This
chapter is the catalog of ways to change a verification problem so
that an engine finishes, or so that a finished answer means what the
engineer thinks. Thirty-one techniques in six families, each written
as the same six parts (the problem it answers, the idea, how to
write it in this tool, what it preserves, a runnable example,
pitfalls), or as a compact three-part entry where an earlier chapter
owns the idea or the tool has no feature for it. One sentence
governs every entry: a change to the problem either keeps every
proof (it only adds behaviors), keeps every counterexample (it only
removes behaviors), or keeps both (it changes nothing the property
can see), and the engineer must know which before reading a verdict.
The entries run on three designs the reader already knows: the
book's FIFO, the valid/ready handshake with its 200-cycle timer, and
the DMA of the architecture case study. On the small designs every
technique is shown working and failing; on the DMA the chapter shows
honestly where techniques stop paying: the end-to-end property of a
channel follows from two lemmas in a fraction of a second, and the
lemmas themselves need invariants of the DMA that no engine settled
within a minute. A worked example composes five techniques to prove
two control properties of a pipe of two 256-entry FIFOs by
k-induction in under a second, where the flat design gave no
verdict. Six one-page recipes close the chapter and point forward to
the chapters that own each flow.

## 1. Decisions

### 1.1 Taken (handed to this outline, or taken here)

| # | decision | basis |
|---|---|---|
| D1 | Full six-part entries for the 21 techniques the tool can show and no earlier chapter owns; compact entries (idea, what it preserves, pointer) for T7, T17, T22, T23, T24, T25, T26, T27, T28, T31 | handed; RN 8(1), Q3 |
| D2 | Two-word ordering: position form is the example; the flag form's no-verdict result is the lesson about invariants over memory | handed; RN M2 (qualified in 1.2) |
| D3 | Case split keeps the multiplier miter, marked as outside the spine | handed; RN M6, section 5 |
| D4 | Entry title "History and prophecy variables"; the tool has no prophecy support, said plainly; the spurious depth-1 counterexample is the pitfall | handed; RN M5 D/E |
| D5 | Every example that proves only with rIC3 declares `REQUIRES := ric3` and its text says so; DMA AXI-rule examples select rIC3 | handed (second half qualified in 1.2) |
| D6 | The protocol checker used both ways derives from Chapter 9's `hs_check`, one parameter choosing assume or assert | handed (qualified in 1.2) |
| D7 | Symmetry: the round-robin arbiter is the clean example, the DMA's pointer reset value the cautionary case | handed (contradicted in 1.2) |
| D8 | Six recipes, one short page each, forward pointers by chapter name | handed |
| D9 | Spine: FIFO, handshake with timer, DMA version 2; decomposition on the DMA taught as "the chain is sound, the last link is easy, the first links are where the work is" | handed; RN Q1(1), M7 |
| D10 | An example's in-house rows and its rIC3 rows live in separate example directories (`x/` and `x-ric3/`), so CI without rIC3 still runs every entry's core lesson | here; a directory has one `REQUIRES` |
| D11 | Example limits: no example over about 75 s; an `undetermined` row is run at 5 to 10 s and the text says "no verdict in N s" with N printed in the output; the research's 60 s results are not quoted as numbers in the chapter | here; RN 2.0 wall times (two-word 1,060 s, hierarchical 799 s, decomposition 570 s); Ch. 18 practice |
| D12 | Seconds appear only in one dated, generated table (`seconds-ric3/`, rows with a verdict only), as in Ch. 18's `engine-seconds` | here; Ch. 18 rule |
| D13 | The worked example is the two-FIFO pipe at 256 entries (T1 + T13 + T17 + T21 + T28), not the DMA, because a worked example must end in a proof | here; RN M9 E rows |
| D14 | Each family opens on the FIFO or the handshake and closes on the DMA (the cost on a real block) | RN section 5 |
| D15 | Epigraph is the book's own sentence | no checked quotation exists |

### 1.2 Where the evidence contradicts or qualifies a handed decision

These do not change the chapter's shape, so they are settled here
under the delegation; each needs its measurement before the draft.

1. **D7 is contradicted by the arbiter's own source.**
   `research/ch19-measurements/symmetry/rr_arb.sv` resets
   `last <= W'(N - 1)`, exactly the asymmetry RN M3 found in the
   DMA's `r_last`. The round-robin transition relation is symmetric
   under *rotation* of the ports (rotate `req`, `gnt` and `last`
   together), not under arbitrary permutation, and the reset state
   `last = 3` is not fixed by any non-trivial rotation. Emerson and
   Sistla require the initial state to be invariant under the group
   (section 2.5, condition 4 of their definition; read, section 7).
   So "prove port 0, the others follow" is unsound on the measured
   arbiter as much as on the DMA; `symmetry/run.out:1-11` shows all
   four ports proven separately, which is not a symmetry argument.
   **Settled:** the clean example is the same arbiter with `last`
   given a free initial value (an initial-value abstraction, T6,
   whose start set is rotation-invariant), proved on port 0, plus
   the reset-state proof that the free start covers reset. To be
   measured (`symmetry/` row "free `last`"). The measured arbiter
   with `last` reset to 3 becomes the first cautionary case, the DMA
   the second, fixed priority the extreme (`symmetry/run.out:12-22`).
2. **D5's DMA clause rests on k-induction only.** RN M4 E compared
   `informal-kind` with `ric3-ic3`. Chapter 9's `axi-formal` example
   proves all six master rules on the DMA with `informal-ic3`, no
   assumptions, limit 120 s (`@sec-ch09-axi`), and Ch. 18's engine
   table proves `ArStable_A` with `informal-ic3` in 4 s
   (`tbl-ch18-engines`). The DMA rules do not need rIC3. **Settled:**
   the DMA protocol example selects `informal-ic3` and needs no
   `REQUIRES := ric3` if a re-run with the R and B rules assumed
   proves the six (to be measured); otherwise it falls back to rIC3
   and D5 applies.
3. **The DMA half of T15 repeats Chapter 9.** `@sec-ch09-axi` proves
   the six AXI master rules with every input free and says the slave
   rules "were not needed"; `@sec-ch09-where` already teaches the
   checker-used-both-ways idea (OpenTitan's TL-UL checker, a role
   parameter) and gives the Definition callout for assumption and
   assume-guarantee. RN M4 E adds the R and B rules as assumptions,
   but no asserted property depends on them, so the run shows
   nothing Chapter 9 did not. **Settled:** T15's DMA paragraph is a
   pointer to `@sec-ch09-axi` plus one new property that does depend
   on the slave keeping its rules (candidate: the DMA's read data
   captured on the R handshake equals RDATA held since RVALID rose;
   to be written and measured), or, if none is found, the DMA is
   dropped from T15 and the entry closes on the handshake.
4. **D6 needs a role parameter, not an assume/assert switch.**
   `hs_check` holds `Answer_A` (`ready |-> valid`), a rule on the
   *receiver*, beside `Held_A` and `Stable_A`, rules on the
   *sender*. A single parameter that flips all three to assumptions
   would assume `Answer_A` on whatever block drives `ready`, which
   is the wrong-direction trap measured in
   `protocol-checker/run.out:21-27`. **Settled:** the derived
   checker takes `ROLE` (`SENDER` or `RECEIVER`, naming the block
   under proof): the rules on signals that block drives are
   asserted, the others assumed. This is OpenTitan's host/device
   scheme (`opentitan-tlul-assert`, already cited by Chapter 9).
   One parameter still selects assume or assert, per rule group.
5. **D2's position form does not prove ordering.**
   `two-word/run.out:21-29`: rIC3 proves `p_head1` and `p_head2`
   (each tracked word is at the head when the count of words ahead
   of it reaches zero) and leaves `p_ahead`, the ordering lemma,
   with no verdict; at DEPTH 16 nothing is proved
   (`two-word/run.out:39-47`). What is proved is the one-word
   integrity check of T9, done for two words. Worked out by hand and
   to be stated as such: under data independence, a one-word check
   that counts the words ahead of the tracked word already implies
   order (a word that overtakes the tracked one changes the count),
   and the duplicating mutant is caught by `p_head1` at depth 3
   (`two-word/run.out:83`). **Settled:** the entry teaches the two
   forms, says that neither ordering assertion was proved, and makes
   the lesson double: the flag form needs a quantified invariant
   over memory slots; the position form avoids it by carrying an
   "ahead" counter, which is why FM H's one-word check is the form
   to use. A slot-indexed helper ("while tracked, the slot at
   `rd_ptr + ahead` holds `d1`"; a single symbolic slot, not a
   quantifier) is the candidate that might make `p_ahead` provable
   in-house; to be tried, and reported either way.
6. **D8: three more recipes have an owner.** The design doc gives
   connectivity, register checks and X-propagation to "Equivalence,
   Structural and Static Verification" together with clock gating;
   information flow to "Safety and Security Verification";
   unreachable-coverage exclusion to "Metrics, Closure and Sign-off";
   register models to "Registers and Reuse"; mutation as a method to
   "Mutation Testing: Qualifying the Testbench". Pointers name these
   chapters (section 3.9).
7. **RN's report rows are not always what they seem** (affects every
   example, not a decision): the shell's report lists every property
   with its last verdict, so a block printed under one engine's
   header can carry a row proved by an earlier engine:
   `memory-abstraction/run.out:37-40` (header `informal-kind`, row
   `a_read ... proven ric3-ic3`), `history-prophecy/run.out:20-24`
   (header `ric3-ic3`, cover row `informal-kind depth 11`),
   `hierarchical/run.out:7-11`. Constraint C1 below.
8. **RN T15's source claim is wrong** (fixed in the note's
   bibliography section): `gisselquist2021axirules` is a blog post on
   the handshake rules, and ZipCPU's `faxil_slave.v` hard-codes its
   assume and assert macros with no switch. The source for one
   checker with a role parameter is `opentitan-tlul-assert`.

No question left by the research changes the chapter's shape, so
nothing is raised with the author.

### 1.3 Constraints from the evidence (cited below as C1 to C12)

- **C1. Stale rows.** An example either runs one engine per session
  or prints only the rows of the property just proved; the text never
  reads the engine column of a row the block did not prove (1.2(7)).
- **C2. Limits.** `undetermined` means "no verdict within the limit
  printed above it" (RN 2.0) and costs its limit in run time (D11).
- **C3. rIC3 split.** In-house rows and rIC3 rows in separate
  directories (D10). Ric3-only entries, from RN Q2 and the runs:
  memory abstraction's flat comparison (M1 A/B), data independence on
  the FIFO (FM H), two-word (M2), history and prophecy at the FIFO
  (M5 C, E), the initial-value proof of the correct FIFO at 256 (M10
  C), boxed and flat pipes without the parent helper (M9 B, D).
- **C4. The tool's notes are the soundness statement.** The black-box
  note (`memory-abstraction/run.out:45`) and the cut-point note (FM
  C.6) are spliced from `run.out`, never retyped.
- **C5. `$anyconst` is rejected and every RTL property of the design
  is then dropped without a message** (FM summary item 2); the
  symbolic constant is a free input with `assume {$stable(x)}`.
- **C6. Reset.** Asynchronous reset is modeled as synchronous; a
  register is free in the reset cycle (`@sec-ch09-axi` Pitfall); a
  `$stable` assumption may not bind the value between cycle 0 and
  cycle 1 (RN T8, [U], to measure before the chapter says it).
- **C7. A shell-only property set prints `informal: svlang: the design
  has no assertions`** (`initial-value/run.out:34`); examples either
  avoid it or the text explains it in one clause.
- **C8. Chapter 9 owns** SVA, vacuity, `bind`, the assumption and
  assume-guarantee definitions, the checker-both-ways idea, the six
  DMA AXI rules proved, the reset trap and dropped immediate
  assertions; cited by label.
- **C9. Chapter 18 owns** reachable set, (inductive) invariant,
  bounded proof, k-induction and the counterexample to induction,
  one helper written and assumed, IC3 vocabulary, assumption as
  constraint and over-constraint, cover as reachability and witness
  cover, lasso and fairness, engine choice, the 64-entry worked
  example and its proof record; cited by label (section 6).
- **C10. Unmeasured tool claims** wait for a run or are cut: boxing
  removes the boxed module's own assertions (RN T1(3)); `$stable` in
  cycle 0 (C6); `clk & en` as a clock (R6); combinational circular
  assume-guarantee (T18).
- **C11. No quotation** from any paper. The sources marked read in
  section 7 were read through a fetch tool that returns extracted
  text summarized; a definition or soundness sentence in the chapter
  may rest on them at the level of the section and theorem named,
  and any wording must be re-read in the document before print.
- **C12. Vendor statements** (Jasper and VC Formal apps in the
  recipes) are labelled as the vendor's, once each, and none is
  needed for a claim the chapter makes.

## 2. Front matter

**Epigraph (own words; drafter may improve):**
> Every technique here makes the problem smaller. The question is
> which answers survive the shrinking.

**Learning objectives.** After this chapter you can:

1. say, for any change to a verification problem, whether it keeps
   proofs, keeps counterexamples, or keeps both, and read a verdict
   accordingly;
2. remove logic from a proof with a black box, a cut point or a timer
   abstraction, and turn a spurious counterexample into the contract
   that removes it;
3. replace a memory by one symbolic slot, and start a proof from an
   invariant instead of from reset, discharging the side condition
   each one leaves;
4. write a symbolic constant, a free oracle and a tracked-word check
   in a tool without `$anyconst`, and say when data independence
   justifies them;
5. argue symmetry soundly, including the reset state, or show why a
   design is not symmetric;
6. write ghost state, a reference model, history variables and a
   protocol checker used as assertion on one side and assumption on
   the other, and say why a prophecy cannot be used the same way in
   a safety check;
7. decompose a proof by assume-guarantee, case split, lemmas and
   hierarchy, and list the side conditions that keep each sound,
   including the circularity that is sound for safety and not for
   liveness;
8. check that a proof's assumptions leave the design room to fail,
   and that its properties can fail at all, with witness covers,
   per-property witness covers under the assumptions, and mutants;
9. choose a technique for an `undetermined` row from the shape of
   its counterexample to induction, and record what the resulting
   proof rests on.

Word budget for title, epigraph and objectives: 300.

## 3. Sections

Budgets sum to 21,000 words (band 18,000 to 22,000). Full entry
about 550 to 700 words; compact entry about 150 to 220. Each full
entry is a level-3 heading with the six parts as bold run-in labels
(*Problem. Idea. How to write it. What it preserves. Example.
Pitfalls.*), not six sub-headings. Example paths are under
`examples/ch19-formal-techniques/` (section 4); evidence lines are
the research outputs the example will reproduce. "In-house" means
the example runs with `informal-bmc`, `informal-kind` or
`informal-ic3` only; "ric3" means `REQUIRES := ric3`, and the text
says so in the sentence that introduces the example. Figures are
written by `figures/gen_ch19_figures.py`, one function each, reading
an example's `run.out` where a verdict is drawn; `figures/blocks.py`
palette; at most 1000 px wide.

### 3.1 Motivation: the row that stayed green (~550 words)

- **Content.** The scaling grid of `@fig-ch18-scale` by reference:
  without the helper the pointer property leaves each engine's reach
  as the FIFO grows; with it, size stops mattering. That helper was
  one designer's line. This chapter is the rest of the toolkit: what
  to do when no single helper is obvious, when the design is too big
  for any engine to see whole, and when a `proven` must be trusted
  by someone else. One exhibit to set the stakes: the 256-word
  memory of 3.3 (T5), which induction does not prove whole within
  its limit and proves in a fraction of a second once the array is
  replaced by one slot and a contract (`mem-abs/run.out`, from
  `memory-abstraction/run.out:26-31, 43-50`). Then the price,
  stated at once: the abstraction itself left a claim to prove, and
  the chapter's real subject is keeping track of such claims. The
  map of the chapter (figure) and the three designs.
- **Reader can:** say what the green row of the previous chapter's
  grid cost and why a technique that shrinks a problem always leaves
  a side condition behind.
- **Figure `fig-ch19-map`:** the six families as columns, each entry
  a cell marked with what it preserves (proofs / counterexamples /
  both / n.a.) and with its example's design (FIFO, handshake, DMA,
  other) and engine class (in-house / ric3 / no example). Drawn from
  a small data file `figures/ch19_catalog.csv` that is the chapter's
  own classification (not a measurement); the drafter keeps it equal
  to the entry headings, and the figure function fails if an entry
  heading in the `.qmd` is missing from the file.
- **Sources:** `@sec-ch18-example`, `@sec-ch18-engines`.
- **Constraints:** C2 (the whole-design row is "no verdict in N s").

### 3.2 Reading an entry: what a change to the problem preserves {#sec-ch19-preserve} (~900 words)

- **Content.** A property-checking problem is a design, a set of
  assumptions, and a property; each technique changes one of the
  three. Two set pictures carry the chapter. If the changed problem
  allows every behavior of the original and possibly more (an
  over-approximation), a proof of a safety property carries back, a
  counterexample may be spurious. If it allows only some of the
  original's behaviors (an under-approximation), a counterexample
  carries back, a proof does not. If the change is invisible to the
  property, both carry. Source: Clarke, Grumberg and Long's
  preservation result for universal temporal formulas under an
  abstraction that simulates the concrete model (read, section 7):
  one sentence of attribution, the rest in the book's words, with
  the restriction stated (universal properties: every safety
  property the book writes is one; covers are existential and
  behave the other way: a cover reached on an over-approximation
  may be unreachable in the design). Then the tool's own sentence,
  printed on every abstracted run (C4), as the same rule. Then what
  each entry carries in every case, as a three-item rule the chapter
  repeats without restating: a witness cover for every assertion
  (`@sec-ch18-cover`), a mutant that some property must catch (3.8,
  T30), and a line in the proof record for every side condition
  (`@sec-ch18-example`). How the six parts read, and why some
  entries are compact (owned earlier; or no feature in this tool).
- **Definition callouts (2):** over-approximation and
  under-approximation, with "preserves proofs / counterexamples";
  side condition (an obligation a technique creates, discharged
  elsewhere).
- **Pitfall callout:** a cover is existential: reached on an
  abstracted model, it says nothing about the design (FM C.6: the
  timer cover drops from depth 202 to 3 under a black box; shown in
  3.3).
- **Reader can:** classify a proposed change (free an input, add an
  assumption, fix a parameter, replace a memory) as over-, under- or
  exact, and say which verdicts survive it.
- **Figure `fig-ch19-preserve`:** three nested-set panels: design
  behaviors inside abstract behaviors with a bad trace outside the
  design (spurious counterexample); restricted behaviors inside the
  design with a bug outside the restriction (missed); exact. Each
  panel captioned with the entries of that kind. `blocks.py`.
- **Example:** none new; the black-box note line from `cut-timer/`
  (3.3) is spliced here as the first sight of it.
- **Sources:** Clarke, Grumberg and Long 1994 (read); `@sec-ch18-assume`.
- **Constraints:** C4, C9, C11.

### 3.3 Shrinking the problem {#sec-ch19-shrink} (~3,700 words)

Opens on the handshake's timer, then the FIFO, closes with a pointer
to the DMA (T7). Order: T1, T2, T4 (one design, three cuts of the
same logic), T3, T5, T6, T7.

**T1 Black box** (full, ~550). *Problem:* a sub-block the property
does not depend on, or depends on only through a promise, makes the
model large. *Idea:* remove it; its outputs become free inputs.
*Write:* `elaborate -bbox_m {timer}` (and `-bbox_i`); the note
line. *Preserves:* proofs (RN T1; Clarke et al. 1994). *Example:*
`cut-timer/` (in-house) on Ch. 18's `handshake.sv` by path: with the
timer boxed, `a_hold_q` proven, `a_no_early` refuted at depth 3
(spurious: the boxed timer expires at once), `c_gnt` covered at
depth 3 against 202 unboxed (FM C.6). *Pitfalls:* most
counterexamples under a box are spurious until the box's contract is
assumed (forward to T5, T21); a name inside a box is accepted by
`assert` and fails at `prove` (FM C.6); covers become shallow
(Pitfall of 3.2); whether the boxed module's own assertions leave
the report is C10, to measure and state, or cut. Reader can: box a
module, read the note, and say whether a given counterexample could
be spurious.

**T2 Cut point** (full, ~500). *Problem:* one internal signal, not a
whole module, carries the complexity. *Idea:* free that signal
(`stopat`). *Write:* `stopat u_timer.expired`, `stopat -list`,
`-clear`. *Preserves:* proofs, for the cone behind the cut.
*Example:* `cut-timer/` second block: the same three properties and
cover under the cut, with the cut-point note line (FM C.6 rows).
*Pitfalls:* cutting a register frees it every cycle, which is more
than freeing its initial value (contrast with T6); a cut on a
signal in a property's antecedent plus an assumption that restricts
it can hide the antecedent (witness cover). Reader can: choose
between a box and a cut for a given cone.

**T4 Timer abstraction** (full, ~550; titled "Counter abstraction"
with the qualifier). *Problem:* a long timer makes every trace deep.
*Idea:* replace the count by a free "expired", optionally with a
minimum-gap assumption that is then a claim about the real timer.
*Write:* the T2 cut plus `assume` on the gap, discharged as an
`assert` on the unabstracted timer. *Preserves:* proofs (a cut); the
gap assumption must itself be proved. *Example:* `cut-timer/` third
block: `a_no_early` proven under the gap assumption, the gap
proved on the timer alone (to be measured; RN T4 proposes it, FM did
not run it). *Pitfalls:* the word means something else in the
parameterized-systems literature, where counters count processes per
local state saturated at "many" (Pnueli, Xu and Zuck 2002, abstract
read): say so in one sentence and define the hardware sense in the
book's words; a property that names the exact delay
(`##[1:201] gnt`, proven unabstracted, FM C.7) is not provable after
the cut. Reader can: abstract a timer and write the gap assumption
and its discharge.

**T3 Parameter reduction** (full, ~600). *Problem:* the proof
finishes at DEPTH 4 and not at 256. *Idea:* prove small, argue for
large. *Write:* `elaborate -parameter DEPTH 4`. *Preserves:*
neither, by itself: a proof transfers only with an argument (a
cutoff theorem for the class of design, data independence, or an
induction on the parameter); a counterexample at the small size is
real at the large one only when the large design contains the small
one's behavior. Cutoff results exist for restricted classes of
concurrent process templates (Emerson and Kahlon, read, section 7),
not for parameterized RTL in general; one sentence. *Example:*
`param-width/` (in-house, to be measured): the FIFO of
`@sec-ch01-example`, whose count is one bit too narrow, checked at
two depths; at the smaller depth the bug is absent or the cover
says so, at the larger it is found; plus a `$clog2` of a non-power
of two probe. *Pitfalls:* widths that change control; full and
empty depending on DEPTH. Reader can: say what argument a small-
parameter proof needs before it counts for the shipped parameter.

**T5 Memory abstraction** (full, ~700). *Problem:* an array is
thousands of state bits the property reads one at a time; the
previous chapter's induction failure has the same shape here
(`memory-abstraction/run.out:1-11`, 16 words: induction no verdict,
rIC3 proven). *Idea:* keep one symbolic slot: a free stable address
`sa`, a shadow of the word stored there with a valid bit, and box
the storage under a contract that pins its read data at `sa`.
*Write:* `mem_abs.sv` (from the research file, 80-column pass),
`-bbox_m` on the storage, the contract as `assume`, the address held
by `$stable` (C5). *Preserves:* proofs, **provided the contract
holds of the real storage** (an assumption to discharge), and,
because `sa` is free, a proof at "the" address is a proof at every
address (forward reference to T8). Sources: Burch and Dill 1994
(read: memories as read/write terms over an unbounded address space,
independent of size), Bjesse 2008 (not opened; title level only).
*Example:* `mem-abs/` (in-house), 256 words: whole design,
induction, no verdict in N s (`memory-abstraction/run.out:26-31`);
storage boxed and contract assumed, proven
(`memory-abstraction/run.out:43-50`); storage boxed and no
contract, spurious counterexample at depth 3
(`memory-abstraction/run.out:51-57`); the contract proved on the
storage alone with the helper `sv_ok -> m[sa] == sv` assumed and
proved (`memory-abstraction/run.out:67-71, 80-84`; the helper at
256 words took about 7 s in RN M1, so this block's limit is set
after timing); the forwarding bug found boxed and whole
(`memory-abstraction/run.out:85-97`). `mem-abs-ric3/` (ric3): the
flat design proven at 16 and 256 words (`run.out:7-11, 32-36`),
which is the comparison. *Pitfalls:* read-during-write semantics in
the contract (a stronger contract than the memory is a false
proof); the shadow's valid bit; the address is constant over the
whole trace, reset included. Reader can: write the four pieces and
name the obligation the abstraction leaves.

**T6 Initial-value abstraction** (full, ~650). *Problem:* a bug 256
pushes from reset is out of reach of a bounded search. *Idea:* start
from every state satisfying an invariant INV; if INV holds at reset
and is inductive, every reachable state is among them
(`@sec-ch18-reach`, `@sec-ch18-induction` by label; no external
source, RN 7(6)). *Write:* `reset -none` plus a start assumption
guarded by a first-cycle flag written as RTL (`iv.sv`). *Preserves:*
proofs, with two side conditions (INV at reset; INV inductive);
counterexamples only if the start state is reachable. *Example:*
`init-value/` (in-house): the wrap mutant from reset at DEPTH 16,
counterexample at depth 16 (`initial-value/run.out:1-4`), and at
256 no verdict in N s (`run.out:5-8`); from INV states at 256, depth
1 (`run.out:9-13`); INV from reset proven (`run.out:23-26`); a
weaker start set gives a spurious counterexample at depth 0
(`run.out:27-31`); the full cover at depth 257 from reset and 0 from
INV (`run.out:32-41`; C7 applies; the 257 row costs about 6 s).
The correct FIFO proved from INV states needs rIC3 at 256
(`run.out:14-22`); `init-value-ric3/` holds it, unless the in-house
run at DEPTH 16 with the Ch. 18 helper proves it (to be measured; if
so, that row moves in-house and the text says starting from INV
does not make a property inductive). *Pitfalls:* `reset -none`
frees registers INV does not mention; assumptions apply every cycle
(hence the first-cycle flag), and reset becomes a free input that
may fire mid-trace; a deep bug found from an INV state is real only
if its start is reachable (confirm by a cover from reset or by
simulation). Reader can: set up the start set, discharge both side
conditions, and tell a reachable counterexample from an
unreachable one.

**T7 Localization and refinement** (compact, ~200). Idea: free most
logic, restore what a spurious trace needs, repeat; the automatic
form is abstraction refinement (Clarke, Grumberg, Jha, Lu and
Veith 2000; McMillan and Amla 2003, at title level). Preserves:
proofs at each step, both at the end. Pointer: the manual loop is
T1/T2 plus reading a counterexample, done in `cut-timer/` and
`mem-abs/`; the tool has no automatic localization at `5114330` (RN
T7). Future Directions mention in 3.11.

- **Callouts in 3.3:** Definition (black box; cut point) as one
  callout; Pitfall (the spurious counterexample under a box, with the
  rule "assume the contract before reading a trace"); In Practice
  (when to box versus cut versus abstract the timer).
- **Figure `fig-ch19-memabs`:** left, the array with the property
  reading one word; right, the abstraction: free `sa`, shadow and
  valid bit, the boxed storage, and the contract arrow; beneath, the
  verdict rows of `mem-abs/run.out` as colored cells. Generated.
- **Reader can (section):** shrink a design three ways and name, for
  each, what was given up and what must still be proved.

### 3.4 Symbolic reasoning {#sec-ch19-symbolic} (~3,100 words)

Order: T8, T11, T9, T10 on the FIFO; T12 on the arbiter and the DMA.

**T8 Symbolic constant** (full, ~550). *Problem:* "for every
address" is 256 properties. *Idea:* one free value held constant
over the trace stands for every value (universal generalization, in
the book's words). *Write:* a free input and `assume {$stable(x)}`
(C5); SymbiYosys's `anyconst` attribute named as one tool's
extension (its documentation, read; the IEEE 1800-2023 status of
`$anyconst` is not stated until the standard's index is checked,
RN 7(3)). *Preserves:* both. *Example:* `symconst/` (in-house): the
`$anyconst` spelling fails and the RTL properties disappear from the
report without a message (C5; to be re-run in the example), then the
working spelling on the T5 address. *Pitfalls:* C5; C6 (the value in
the reset cycle, measure first); a stable value is stable across a
mid-trace reset too. Reader can: write a symbolic constant that the
tool accepts and check that every property is still listed.

**T11 Free oracle input** (full, ~450). *Problem:* "some push",
"the moment to save". *Idea:* a free input chooses; restricted to
fire once. *Write:* `pick` with the `!in_q` guard (FM H).
*Preserves:* both, provided the restriction excludes no case.
Source: the liveness-to-safety construction already uses an oracle
(`@sec-ch18-liveness`). *Example:* shares `track-word-ric3/` (T9).
*Pitfalls:* an oracle that may fire twice; a guard that silently
excludes the boundary (no pick while full). Reader can: write a
once-only oracle and say which pushes it can choose.

**T9 Data independence: tracking one word** (full, ~650).
*Problem:* data integrity over all data values. *Idea:* if the
design only moves data, one tagged word chosen by the oracle stands
for all. *Write:* FM H's wrapper: `sd` stable, `pick`, ghost `in_q`
and `ahead`, property `in_q && ahead == 0 |-> rd_data == sd`.
*Preserves:* both, only for a design that never computes on, compares
or branches on the data. Source: Wolper 1986 named as the origin of
the term **at title level only**: the paper was not opened (section
7); the soundness argument is the book's own. *Example:*
`track-word-ric3/` (ric3): proven at DEPTH 16 (FM H: rIC3 only,
in-house no verdict at 60 s), cover of the tracked word leaving with
nine ahead, and the read-pointer mutant at depth 3 (FM H). To be
re-measured at DEPTH 4 to cut the time; and the slot-indexed helper
of 1.2(5) tried in-house (if it proves, a `track-word/` in-house
example replaces this one and the text teaches the helper).
*Pitfalls:* parity or matching on data breaks the argument; the
oracle's guard. Reader can: write the tracked-word check and say
which designs it is sound for.

**T10 Two-word ordering check** (full, ~650). *Problem:* order, loss
and duplication across words. *Idea:* two symbolic words, d1 pushed
before d2. *Write:* the flag form (each word in, each word out:
`a_order`, `a_once1`, `a_once2`) and the position form (words ahead
of each tracked word: `p_head1`, `p_head2`, `p_ahead`).
*Preserves:* both, under data independence; loss needs a liveness or
bounded-response property. Source: folklore of industrial practice,
attributed to nobody (RN T10). *Example:* `two-word-ric3/` (ric3),
DEPTH 4: flag form, no verdict in N s for all three
(`two-word/run.out:1-10`; also `first-run.out` for every engine);
position form, `p_head1` and `p_head2` proven, `p_ahead` no verdict
(`two-word/run.out:21-29`); duplicating mutant caught by every
property, the deepest at 6 (`two-word/run.out:73-85`); witness
cover at depth 3. *Lesson (1.2(5)):* why the flag form needs an
invariant over memory contents ("no slot but the tracked one holds
d1"), a quantified statement no engine here learned; why the
position form avoids it; and that ordering was not proved in either
form, so the one-word check of T9 is the form to use on a FIFO.
*Pitfalls:* forgetting "every other push carries another value"
makes a second d1 a spurious duplicate (RN T10). Reader can: say
why one property is provable and its neighbor is not from what
invariant each would need.

**T12 Symmetry** (full, ~800). *Problem:* N identical channels, N
proofs. *Idea:* a permutation of the channels that maps the
transition relation, the initial states and the property onto
themselves lets one proof stand for the orbit (Emerson and Sistla
1996, read: their automorphism definition includes the initial
state, section 2.5; the quotient preserves formulas invariant under
the group, Theorem 3.3); in hardware, almost always rotations, not
all permutations. *Write:* no tool support; the engineer states the
permutation and checks its three conditions. *Preserves:* proofs, if
the three conditions hold. *Example:* `symmetry/` (in-house):
(a) the round-robin arbiter with `last` free at start, port 0
proven, plus the proof that reset is in the free start set (to be
measured; 1.2(1)); (b) the arbiter as measured, `last` reset to 3,
all four ports proven separately (`symmetry/run.out:1-11`) and the
remark that this is four proofs, not a symmetry argument; (c) fixed
priority: port 0 proven, ports 1-3 refuted at depth 5
(`symmetry/run.out:12-22`); (d) the DMA: `r_last` resets to the last
channel, so the channel swap does not fix reset; with two channels
the sound answer is to prove both: `a_excl` proven on each
(`symmetry/run.out:23-33`, in-house rows only). *Pitfalls:* the
initial-state condition; a property whose image under the
permutation is not the property for the other channel; a design
symmetric in its RTL text and not in its reset. Reader can: check
the three conditions for a proposed symmetry, or exhibit the one
that fails.

- **Callouts:** Definition (symbolic constant; data independence);
  Pitfall (`$anyconst` silently drops properties, C5); In Practice
  (when tracking one word is enough).
- **Figure `fig-ch19-track`:** a FIFO strip with the tracked word,
  `ahead` counting down, and the two-word variant with the
  memory-slot invariant the flag form would need, drawn as the
  shaded set of slots it quantifies over. `blocks.py`; no verdicts.
- **Reader can (section):** replace "for all values" and "for all
  channels" by one free value or one channel, with the argument that
  makes it sound.

### 3.5 Modeling code {#sec-ch19-modeling} (~2,700 words)

Order: T13, T14 on the FIFO contract; T15 on the handshake (DMA
pointer); T16 on a grant unit and the FIFO.

**T13 Ghost state** (full, ~500). *Problem:* the property needs a
quantity the design does not hold (pushes minus pops). *Idea:*
logic that only reads the design. *Write:* a bound module with
inputs only (`@sec-ch09-where` for `bind`); the ghost count `g` of
the single-FIFO contract. *Preserves:* both, provided the ghost
never drives the design (Owicki and Gries 1976, read: auxiliary
variables appear only in assignments to themselves, Definition 3.6,
and can be deleted without changing the result, rule 3.7; one
sentence of attribution). *Example:* `contract/` (in-house): `g`
and the contract `CE_A` (empty iff `g == 0`), `CF_A` (full iff
`g == DEPTH`) proven at DEPTH 16 (`hierarchical/run.out:1-6`); the
ghost helper `H_A` (`g == u.count`) proven; at DEPTH 64 the contract
has no verdict in N s alone and is proven with `H_A` assumed
(`hierarchical/run.out:24-29, 40-45`). *Pitfalls:* the ghost has its
own reset (C6); a counter that wraps must be wide enough or
saturate. Reader can: write ghost logic that cannot change the
design, and tie it to the design with a helper.

**T14 Reference model** (full but short, ~400). *Problem:* the
specification is a behavior, not a single relation. *Idea:* a small
abstract model the design must match (`g` is one: occupancy, not a
second FIFO). Chapter 9's FIFO checker `occ` is the same idea in
simulation and formal (`@sec-ch09-example`); the reference-model
chapter owns predictors in simulation (named, not numbered).
*Preserves:* both. *Example:* `contract/` as above; no new run.
*Pitfalls:* a model written from the RTL repeats its bugs; a model
as large as the design is a second design. Reader can: choose the
abstraction level of a model.

**T15 Protocol checker as assumption and assertion** (full, ~800).
*Problem:* the same interface rules are obligations for one block
and promises for its neighbor. Idea and definition by label
(`@sec-ch09-where`): this entry adds how to write it so that one
file serves both sides, and the trap of the wrong side. *Write:*
`hs_rules.sv`, a new file derived from Chapter 9's `hs_check.sv`
(not an edit of it), with a `ROLE` parameter: rules on signals the
block under proof drives are asserted, the others assumed, in
`if (ROLE == ...)` generate blocks (works in a `bind`, RN M4;
1.2(4)). *Preserves:* proofs, if each assumed rule is discharged as
an assertion on the block that drives it. *Example:* `protocol/`
(in-house), on `vr.sv` (the research's stage, rebuilt to use
`hs_rules`): (A) wire stage, input free: both output rules refuted
at depth 2 (`protocol-checker/run.out:1-6`); (B) input rules assumed:
proven, cover reached (`run.out:7-14`); (C) register stage, input
free: proven (`run.out:15-20`); (D) the checker bound with the wrong
role: an assertion about the input is proven and a cover of the
input dropping `valid` is unreachable (`run.out:21-27`), because
the assumption on the output reaches back through the wire. The
DMA: pointer to `@sec-ch09-axi` and, if found and measured, one
property that needs the slave rules (1.2(2), 1.2(3)); then the
example is `protocol-dma/`, `informal-ic3` (or ric3 per 1.2(2)).
*Pitfalls:* direction (D); `Answer_A`-type rules that belong to the
other side (1.2(4)); `disable iff` and reset apply to both roles.
Reader can: bind one checker on both sides of a link, and detect
the wrong-side binding with a cover.

**T16 History and prophecy variables** (full, ~800). *Problem:* a
property about "a request at some earlier time" or "the k-th word"
cannot be written with bounded `$past`. *Idea:* a history variable
records the past; a prophecy variable guesses the future and is
checked when the future arrives (Abadi and Lamport, read in the
1988 report version: both introduced so refinement mappings exist;
adding either leaves the externally visible behaviors unchanged,
Propositions 4 and 5, the prophecy only under a finiteness condition
without which it can rule out behaviors, section 5.2). *Write:* a
`seen` bit; a saturating k-th-push counter and the captured word.
*Preserves:* history: both. Prophecy in this tool: **InFormal has no
prophecy support**; an assumption that checks a guess at the k-th
pop cannot remove a trace that ends before the k-th pop, so in a
safety check of finite traces an assertion that reads the guess
earlier fails spuriously. *Example:* `history/` (in-house): three
cycles of `$past` refuted at depth 5 on a correct unit
(`history-prophecy/run.out:1-4`); the `seen` bit proven, and the
mutant refuted at depth 1 (`run.out:5-13`); the prophecy asserted at
the push, a spurious counterexample at depth 1 (`run.out:25-31`).
`history-ric3/` (ric3): the k-th word out equals the k-th word in,
by a history variable, proven (`run.out:14-24`); the prophecy read
only at the pop, proven (`run.out:32-46`), which is logically the
history check with one more free variable. *Pitfalls:* the depth-1
trace of D (as D4 says); bounded `$past` chains as false alarms;
saturating counters. Reader can: replace an unbounded look-back by a
history variable, and say why the same property cannot be written
with a prophecy here.

- **Callouts:** Definition (ghost state; history variable; prophecy
  variable, in one callout); Pitfall (the wrong-side checker, D);
  Pitfall (the prophecy trace at depth 1); In Practice (put ghost
  logic in a bound module with inputs only).
- **Figure `fig-ch19-prophecy`:** a timeline: push k (the assertion
  reads the guess), pop k (the assumption checks it), and the
  depth-1 trace that ends between them, from `history/run.out`.
- **Reader can (section):** add observation logic that cannot change
  the design and use it to state properties the design's own
  signals cannot.

### 3.6 Decomposition {#sec-ch19-decompose} (~3,000 words)

Order: T17 (compact), T18, T19, T21, T20 (the DMA last: where it
gets hard).

**T17 Helper invariant** (compact, ~200). By label
(`@sec-ch18-helper`, `@sec-ch18-example`). Adds two things: the
tool does not reuse a proved assertion, so keep one Tcl variable for
the assertion and its assumption (Ch. 18 practice); and in this
chapter every abstraction's side condition is a helper of this
kind (T5's contract, T6's INV, T21's parent helper).

**T18 Assume-guarantee** (full, ~750). Definition by label
(`@sec-ch09-where`). *Problem:* two blocks whose properties depend
on each other. *Idea:* prove each under the other's guarantee.
*Write:* assumption by Tcl text equal to the neighbor's assertion.
*Preserves:* proofs for safety when every loop of mutual dependence
passes through a register, so each guarantee at cycle t+1 needs the
other only up to t (induction on time); Abadi and Lamport 1995 (read:
the guarantee holds one step longer than the assumption; their
composition theorem, section 5; assumptions as safety properties);
for liveness, circular reasoning is unsound in general and needs
explicit induction with unit-delay edges breaking every cycle
(McMillan 1999, read, section 2); Misra and Chandy 1981 at title
level (not opened). *Example:* `ag/` (in-house, 0.2 s): one block
proven under its neighbor's guarantee, a reset-value mutant refuted
at depth 1, the safety ring proven flat (`assume-guarantee/run.out:
1-14`); each block proven live under the other's "eventually", the
ring refuted with a lasso at depth 3 (`run.out:15-23`). *Pitfalls:*
the liveness ring; same-cycle (combinational) circularity is the
safety version (C10: not measured; stated as an argument, not a
run). Reader can: decide whether a mutual assumption is sound, and
point to the register that makes it so.

**T19 Case split** (full, ~650; flagged "outside the spine").
*Problem:* one solver problem too hard whole. *Idea:* prove under
each of several conditions that together cover all cases, and prove
that they do. McMillan 1999 (read: case splitting on an auxiliary
variable's value, Theorem 1 of section 3; coverage of every value
is what makes it sound). *Write:* one session per case with `assume`
on `a[7:6]`, plus a completeness assertion. *Preserves:* proofs, if
every case is proved and completeness is proved. *Example:*
`case-split/` (in-house) on an 8-bit multiplier miter (also a
preview of the equivalence chapter): whole proven; four cases
proven; completeness proven (`case-split/run.out:1-29`); the bug in
case 3, a three-case list whose completeness fails at depth 0
(`run.out:46-53`; cases 0-2 of part C are not re-run). Seconds in
`tbl-ch19-seconds`: the split costs about the same in total and pays
only in parallel (RN M6). The 10-bit result (no verdict whole or by
case) is not run (D11) and not claimed. *Pitfalls:* the forgotten
case; splits that do not shrink the hard part. Reader can: write a
complete split and its completeness check.

**T21 Hierarchical proof** (full, ~650). *Problem:* a parent whose
children are each proved. *Idea:* box each child under its proved
contract (T1 + T13 + T18). *Write:* `-bbox_m {fifo}`, contracts on
ports and ghost state the parent can see. *Preserves:* proofs, if
each contract is proved on its block under that block's input
assumptions, which become assertions in the parent. *Example:*
`hier/` (in-house), DEPTH 16: boxed, contract assumed, both parent
properties no verdict in N s by induction
(`hierarchical/run.out:47-57`); half the contract assumed, P2
refuted at depth 1, spurious (`run.out:140-148`); the parent helper
(the pipe's count is the sum of the two, each at most DEPTH) proven,
and P1 and P2 proven under it (`run.out:181-203`). `hier-ric3/`
(ric3), DEPTH 16: boxed and flat both proven
(`run.out:58-77, 149-164`), with seconds in the dated table. The
honest finding (RN Q1(3)): boxing alone did not make the parent
cheaper, because these properties read counters and flags, not the
memories; the contract is what lets the parent's helper be stated on
ports at all. Whether the tool's own cone reduction already dropped
the memories was not checked: the text says so or the drafter checks
it. *Pitfalls:* a contract naming a child's internal `count` is
unusable once the child is boxed; the half contract. Reader can:
state a child's contract on its ports, and say what boxing does and
does not buy.

**T20 Property decomposition on the DMA** (full, ~750). *Problem:*
an end-to-end property of a 647-bit design. *Idea:* replace it by a
chain of local lemmas, each proved, and the end-to-end proved from
them. *Write:* ghost write-response count bound into the DMA
(`dma_wcount.sv`), `E2E_A`, `L1_A`, `L2_A`. *Preserves:* proofs, if
the end-to-end follows from the lemmas (itself checked) and each
lemma is proved. *Example:* `decomp/` (in-house): each of E2E, L1,
L2 alone, no verdict in N s by `informal-kind` and by `informal-ic3`
(`decomposition/run.out:1-13`); a bounded search at N s finds no
counterexample to them either (the research's scratch run was not
kept, RN 7(8): this block is new and must be measured); the witness
cover reached at depth 15 (`run.out:7`); E2E proven with L1 and L2
assumed (`run.out:20-28`). The lesson as D9 says: the chain is
sound and its last link is easy; the lemmas need invariants of the
DMA (a read in flight implies the channel is busy), and the first
of those is itself `undetermined` for every engine including rIC3
(`symmetry/run.out:27, 37`). The next step (a layer of DMA
invariants as further lemmas) is named and left as an exercise
without an answer key in the chapter; it is not measured.
*Pitfalls:* lemmas that are true and not inductive move the
difficulty; a chain that assumes its own conclusion. Reader can:
decompose an end-to-end property, check that the chain closes, and
say where the remaining work is.

- **Callouts:** Definition (case split with completeness;
  hierarchical contract); Pitfall (liveness assume-guarantee); In
  Practice (when decomposition pays: when each local property is
  inductive or nearly so).
- **Figures.** `fig-ch19-ag`: left, the safety ring with the
  register that breaks the cycle; right, the liveness ring's lasso of
  all zeros, from `ag/run.out`. `fig-ch19-decomp`: the chain E2E ←
  L1, L2 ← DMA invariants, each node colored by its verdict in
  `decomp/run.out` and `symmetry/run.out` (generated).
- **Reader can (section):** split a proof four ways and write, for
  each, the side condition that keeps it sound.

### 3.7 Constraining and bug hunting {#sec-ch19-constrain} (~1,200 words)

All compact, each ~170 to 220 words, each ending in a pointer.

- **T22 Environment assumptions.** Definition owned by
  `@sec-ch18-assume`; adds: write them from the specification's
  interface rules (T15) and discharge them on the neighbor (T18).
  Preserves: proofs only for environments that keep them.
- **T23 Over-constraint for hunting.** Restrict inputs to reach a
  deep bug sooner; preserves counterexamples only; a hunting script
  prints no `proven` the reader could take for a proof (label it).
  Pointer: `@sec-ch18-assume` (the `!req` run).
- **T24 Bounded proof with a depth argument.** Owned by
  `@sec-ch18-bmc` (bounded proof, completeness threshold); the shell
  prints no bound; the industrial argument (deep covers reached
  within the bound) is evidence, not proof. Not available as a
  feature.
- **T25 Cover-guided deep search.** Start a search from a covered
  deep state; preserves counterexamples; a vendor feature with no
  peer-reviewed source read; not available; T6 is the sound cousin.
- **T26 Bounded liveness.** Owned by `@sec-ch18-liveness`; on the
  handshake `##[1:201] gnt` is proven unabstracted and
  `##[1:200]` refuted (FM C.7; cite by Ch. 18's examples if they
  print it, else measure in `cut-timer/`); and the T4 cut makes the
  bounded form unprovable.
- **T27 Fairness.** Owned by `@sec-ch18-liveness`; adds the M8
  observation: a fairness assumption in a mutual liveness argument
  is the circular case of T18.

Reader can: say for each of the six what it preserves and where the
book teaches it in full.

### 3.8 Trusting the result {#sec-ch19-trust} (~1,800 words)

**T28 Witness cover** (compact, ~200). Owned by `@sec-ch18-cover`;
this chapter has used it in every entry; the tool flags no vacuity.

**T29 Assumption sanity** (full, ~650). *Problem:* assumptions that
leave no room to fail. *Idea:* check with covers that the
environment can run on, and with per-assertion witness covers that
each assertion's scenario survives the assumptions. The exact
condition (every reachable state that satisfies the assumptions has
a successor that does) is branching-time and not expressible in SVA
(book's words; no source, RN T29). *Write:* `Deep_C` (a free-running
count reaches 50), `Witness_C` per assertion. *Preserves:* n.a. *
Example:* `sanity/` (in-house, 0.2 s), `sanity.sv` (a counter with
a mode): no assumption: assertion refuted at depth 10, both covers
reached (`assumption-sanity/run.out:1-6`); a dead end for every
trace: assertion proven, both covers unreachable (`run.out:7-13`);
a dead end for mode-1 traces only: assertion proven, deep cover
reached at depth 51, witness cover unreachable (`run.out:14-20`).
*Pitfalls:* the middle row of C: a generic deep cover passes;
contradictory assumptions pass silently (FM C.5). Reader can: write
the witness cover that catches a partial dead end.

**T30 Mutation of the design** (full, ~550). *Problem:* a property
set that cannot fail. *Idea:* plant a bug; some property must fail;
a surviving mutant is a gap or an equivalent mutant. Sources:
DeMillo, Lipton and Sayward 1978 (`demillo1978mutation`); Chockler,
Kupferman, Kurshan and Vardi 2001 (read by the research note:
coverage as which mutations make the specification fail). Pointer:
the mutation-testing chapter owns the method (named). *Example:*
`mutants/` (in-house): the chapter's FIFO property set (the T5, T9
and Ch. 9 assertions that run in-house) against `fifo_dup.sv`,
`fifo_wrap.sv` and FM H's read-pointer mutant, each killed by a
named property with its depth (rows from
`two-word/run.out:73-85`, `initial-value/run.out:1-4`, FM H; the
combined table is new and must be measured). *Pitfalls:* a mutant
that survives because the property set is vacuous under the
assumptions (T29); equivalent mutants. Reader can: run a mutant
against a property set and read a survivor.

**T31 Cone-of-influence and proof-core coverage** (compact, ~200).
Which logic the proofs needed: COI over-reports, proof cores are
tighter (McMillan and Amla 2003; Ghassabani, Gacek and Whalen 2016,
title level); a vendor app is named as a vendor statement (C12);
not available in the tool.

- **Callouts:** Pitfall (the partial dead end); In Practice (the
  three things every proof ships with: witness covers under the final
  assumptions, a killed mutant, the record).
- **Figure:** none new (`fig-ch19-preserve` is referred to); the
  `sanity/run.out` block is the exhibit.
- **Reader can (section):** produce, for a proof, the evidence that
  it could have failed.

### 3.9 Six recipes {#sec-ch19-recipes} (~1,500 words)

Each recipe ~250 words: the question, the techniques it combines (by
entry), the assertion pattern in prose, what it preserves, and the
chapter that owns the full flow, named. Vendor apps are named once
each as vendor statements (C12). No recipe is measured; two get a
small example if they run in time, else they stay prose.

- **R1 Connectivity.** T1 (box the IP, keep the wiring), T22 (mode
  inputs), one assertion per connection-table row; candidate the
  DMA's interrupt path. Optional example `conn-irq/` (to measure).
  Owner: Equivalence, Structural and Static Verification.
- **R2 Register access.** T8 (symbolic address and data), T13 (a
  ghost copy), T15 (the bus rules assumed); the DMA's `SRC_ADDR`
  read-back with its two low bits dropped by design. Optional example
  `reg-readback/` (to measure). Owners: Equivalence, Structural and
  Static Verification; Registers and Reuse.
- **R3 X-propagation.** The tool is two-valued; the recipe is
  self-composition with the X sources free and independent in two
  copies (R5's construction); no primary source read for the
  encoding (RN R3), so stated as the book's construction. Owner:
  Equivalence, Structural and Static Verification.
- **R4 Unreachable-coverage analysis.** A coverage point restated as
  a cover; `unreachable` is a proof under the assumptions in force,
  so an exclusion holds only for environments that keep them. Owner:
  Metrics, Closure and Sign-off; back-pointer `@sec-ch08-closure`.
- **R5 Information flow by self-composition.** Two copies, public
  inputs shared, secrets free; the pair property is a safety
  property of the product (Terauchi and Aiken 2005; Clarkson and
  Schneider 2010; Barthe, D'Argenio and Rezk 2004, metadata only;
  none opened in this outline, title level). Owner: Safety and
  Security Verification.
- **R6 Clock-gating equivalence.** A hand-built miter of the gated
  register written as an enable against the original; the tool has
  no equivalence command (FM C.8); `clk & en` is C10. Owner:
  Equivalence, Structural and Static Verification.

Reader can: assemble each of the six checks from the catalog's
entries and say which chapter carries it further.

### 3.10 Worked example: a pipe of two 256-entry FIFOs {#sec-ch19-example} (~1,100 words)

- **Content.** The chapter's method as one procedure, on the design
  of T21 at DEPTH 256, where flat and boxed proofs gave no verdict
  in the research runs (`hierarchical/run.out:109-139` boxed;
  flat at 64 already partly undetermined, `run.out:165-180`). Steps:
  (1) covers first: P1's and P2's antecedent witness covers (the
  "both full" cover is 513 cycles deep and was not reached at 64 with
  the helper, `run.out:226`; the step teaches choosing a witness
  cover that a search can reach, to be measured); (2) the child's
  contract proved at 256 with its ghost helper (`contract/` at 256,
  to be measured; at 16 and 64 proven, `run.out:1-45`); (3) box both
  children, assume the contracts; (4) induction on the parent: no
  verdict in N s (`run.out:109-118` pattern, re-measured at the
  example's limit); (5) the counterexample to induction says what is
  missing (the pipe's count against the two children's ghost counts);
  write the parent helper; prove it (`run.out:229-240`); (6) P1 and
  P2 proven under it (`run.out:241-252`); (7) the mutant: one child
  with the wrap mutant of T6 refutes its contract (to be measured);
  (8) the record: each property, engine, assumptions, each assumption
  with where it is discharged (child contract at child level, parent
  helper at parent level, both by induction), covers with depths,
  limits that ended without a verdict.
- **Worked Example callout:** the eight steps as a recipe.
- **Reader can:** compose box, ghost, contract, helper and witness
  cover into a proof of a design too large to prove flat, and write
  its record.
- **Example `pipe-256/`** (in-house): the steps above, limit 10 s
  for the `undetermined` step, the rest well under a second each in
  the research (0.14 s and 0.02 s rows). About 25 s.
- **Figure `fig-ch19-pipe`:** the two boxed FIFOs, their contracts,
  the parent helper; under it the verdict cells of the steps from
  `pipe-256/run.out`.
- **Sources:** `@sec-ch18-example` for the procedure's earlier form.
- **Constraints:** C1, C2, C4.

### 3.11 Future directions (~250 words; one Future Directions callout)

Labelled as open, no result claimed: automatic localization and
abstraction refinement (Clarke et al. 2000) as what T1/T2/T7 become
when a tool does them; proof-core coverage in open tools (T31);
learning quantified invariants over arrays (the flag form of T10
names the gap); compositional certificates (a record a reviewer can
re-check, extending Ch. 18's certificate paragraph). One sentence on
the book's last part, no claim.

### 3.12 Summary (~350 words)

Nine bullets mirroring the objectives, each with its measured fact
(256 words proven under one slot and a contract; a bug 256 pushes
deep found at depth 1 from invariant states; `$anyconst` drops
properties; a symmetry that fails at reset; a wrong-side checker
proves a false input property; the prophecy's depth-1 trace; the
liveness ring's lasso; a partial dead end caught only by the witness
cover; the pipe at 256 proved by induction with a parent helper), and
`fig-ch19-map` once more.

### 3.13 Exercises (~700 words; list in section 5)

### 3.14 Further reading (~150 words)

Names, authors, editions only: Seligman, Schubert and Kumar,
*Formal Verification: An Essential Toolkit for Modern VLSI Design*,
2nd ed. (edition verified, text not; no paraphrase); Clarke,
Grumberg and Long 1994; Emerson and Sistla 1996; Abadi and Lamport
1991 and 1995; McMillan 1999 (both); Burch and Dill 1994; Biere and
Kroening's handbook chapter as in Ch. 18.

### Budget

| section | words |
|---|---|
| title, epigraph, objectives | 300 |
| 3.1 motivation | 550 |
| 3.2 reading an entry | 900 |
| 3.3 shrinking (T1, T2, T4, T3, T5, T6 full; T7 compact) | 3,700 |
| 3.4 symbolic (T8, T11, T9, T10, T12) | 3,100 |
| 3.5 modeling (T13, T14, T15, T16) | 2,700 |
| 3.6 decomposition (T17 compact; T18, T19, T21, T20) | 3,000 |
| 3.7 constraining (T22 to T27 compact) | 1,200 |
| 3.8 trusting (T28, T31 compact; T29, T30) | 1,800 |
| 3.9 recipes | 1,500 |
| 3.10 worked example | 1,100 |
| 3.11 future, 3.12 summary, 3.13 exercises, 3.14 further reading | 250 + 350 + 700 + 150 = 1,450 |
| **total** | **21,300** |

Full entries: 21 (T1-T6, T8-T16, T18-T21, T29, T30). Compact: 10 (T7,
T17, T22-T28, T31). Callout census (six kinds only): Definition x 7
(3.2 x2; 3.3, 3.4, 3.5 one combined callout each; 3.6 x2), Pitfall
x 7 (3.2; 3.3, which is T1's spurious trace; 3.4; 3.5 x2; 3.6; 3.8),
In Practice x 5 (3.3, 3.4, 3.5, 3.6, 3.8), Worked Example x 1, Future Directions x 1,
Exercise x 1. If the draft runs long, the Definition callouts of
3.4 and 3.5 become defined terms in running text first.

## 4. Example directories

All under `examples/ch19-formal-techniques/`. Every tool example sets
`EXAMPLE_LANG := informal`, `REQUIRES := informal` (plus `ric3` where
marked), selects one engine per `prove` with Ch. 18's `one`
procedure from `examples/ch18-formal-property-verification/common/
proof.tcl` (sourced by path, not copied), checks every verdict with
`expect`, ends with `finish`, and names in `EXPECT_OUTPUT` a line
only a real run prints. RTL from Chapters 9, 11 and 18 is read by
path, never copied or edited. Research files in
`research/ch19-measurements/` are the starting point; each needs the
80-column pass, the 72-column comment ruler, a header naming what
it is, and C1 applied to its output. Times are the research's
wall-clock where a row exists, otherwise "to be timed".

| directory | needs | design and files | `run.out` (expected; evidence) | time |
|---|---|---|---|---|
| `common/` | — | `ch19.tcl` (the research `design` proc) | library | — |
| `cut-timer/` | informal | Ch. 18 `over-constraint/handshake.sv` by path; `cut.tcl`: box, cut, cut plus gap assumption, gap proved on the timer | FM C.6 rows; gap rows to be measured | to be timed, < 5 s |
| `param-width/` | informal | Ch. 1 FIFO by path at two depths; `$clog2` probe | to be measured | to be timed |
| `mem-abs/` | informal | `mem_abs.sv`, `mem.tcl` | `memory-abstraction/run.out:26-31, 43-57, 67-71, 85-97` | ~25 s at a 5 s limit for the whole-design row plus the 256-word helper (time it) |
| `mem-abs-ric3/` | informal, ric3 | same files | `memory-abstraction/run.out:7-11, 32-36` | ~10 s |
| `init-value/` | informal | `iv.sv`, Ch. 9 FIFO and `fifo_wrap.sv` (sed-generated at run time from Ch. 9's file, as Ch. 9's mutants are) | `initial-value/run.out:1-13, 23-41` | ~20 s (the 256 bounded row at a 10 s limit; the depth-257 cover about 6 s) |
| `init-value-ric3/` | informal, ric3 | same | `initial-value/run.out:14-22` | ~35 s; or folded into `init-value/` if the DEPTH-16 in-house run proves |
| `symconst/` | informal | FIFO wrapper with `$anyconst` and with a free stable input | the dropped-properties report and the working one (FM summary item 2; re-run) | < 5 s |
| `track-word-ric3/` | informal, ric3 | FM `tech/sym_fifo.sv`, mutant | FM H rows; re-measure at DEPTH 4 | to be timed (32 s at DEPTH 16) |
| `two-word-ric3/` | informal, ric3 | `two_word.sv`, `fifo_dup.sv` (sed-generated) | `two-word/run.out:1-10, 21-29, 73-85` at a 10 s limit | ~50 s (four rows end at the limit) |
| `symmetry/` | informal | `rr_arb.sv` with a `FREE_LAST` parameter; DMA by path | `symmetry/run.out:1-26, 30` (in-house rows) plus the free-`last` rows to be measured | ~5 s |
| `contract/` | informal | `hier.sv` single-FIFO part | `hierarchical/run.out:1-6, 17-29, 40-45` | ~10 s |
| `protocol/` | informal | `hs_rules.sv` (derived from Ch. 9 `hs_check.sv`, `ROLE` parameter), `vr.sv` | `protocol-checker/run.out:1-27` | < 2 s |
| `protocol-dma/` | informal (ric3 only if 1.2(2) fails) | `hs_rules.sv` bound on the DMA; the slave-dependent property | to be measured (1.2(2), 1.2(3)); dropped if no such property | to be timed |
| `history/` | informal | `hp.sv` | `history-prophecy/run.out:1-13, 25-31` | < 2 s |
| `history-ric3/` | informal, ric3 | `hp.sv` | `history-prophecy/run.out:14-24, 32-46` (in-house blocks at a 5 s limit or omitted, C1) | ~25 s |
| `ag/` | informal | `ag.sv` | `assume-guarantee/run.out:1-23` | 0.2 s |
| `case-split/` | informal | `mul.sv` (W = 8) | `case-split/run.out:1-29, 46-53` | ~40 s |
| `hier/` | informal | `hier.sv` | `hierarchical/run.out:47-57, 140-148, 181-203` | ~15 s |
| `hier-ric3/` | informal, ric3 | `hier.sv` | `hierarchical/run.out:58-77, 149-164` | ~10 s |
| `decomp/` | informal | DMA by path, `dma_wcount.sv` | `decomposition/run.out:1-13, 20-28` at an 8 s limit, plus a bounded block (new) | ~75 s, the longest; split into two directories if over |
| `sanity/` | informal | `sanity.sv` | `assumption-sanity/run.out:1-20` | 0.2 s |
| `mutants/` | informal | FIFO, three mutants (sed-generated) | one kill line per mutant (new) | to be timed |
| `pipe-256/` | informal | `hier.sv` at DEPTH 256 | worked example steps; `hierarchical/run.out:229-252` pattern | ~25 s |
| `seconds-ric3/` | informal, ric3 | runs the rows with a verdict from `mem-abs`, `hier`, `case-split`, `history` at 60 s limits; writes `tbl-seconds.md` | dated table, regenerated with rIC3 present | to be timed; CI skips |
| `conn-irq/`, `reg-readback/` | informal | DMA by path | optional; to be measured | to be timed |

Twenty-four directories plus two optional; seven need rIC3. In-house
total about four minutes; with rIC3 about six more. The rIC3 set is
skipped in CI and named as such in the text.

To be measured before drafting, collected: 1.2(1) free-`last`
arbiter; 1.2(2) DMA rules with `informal-ic3` under the slave
assumptions; 1.2(3) a slave-dependent DMA property; 1.2(5) the
slot-indexed helper for `p_ahead` and for T9; T4 gap assumption and
its discharge; T3 width probe; T6 correct-FIFO proof at DEPTH 16
in-house; T9 at DEPTH 4; T20 bounded block; T30 combined mutant
table; worked-example contract and witness covers at 256; C6
`$stable` in cycle 0; C10 boxed assertions. Each either lands in an
example or the sentence that needed it is cut.

## 5. Exercises (each with one determinate answer; solutions to the solutions appendix)

1. **Which way does it go?** For each change say whether proofs,
   counterexamples or both survive: box a module; add `assume !req`;
   replace the address by a free stable input; set DEPTH from 256 to
   4. *(Proofs; counterexamples; both; neither without an argument.)*
2. **Read the note.** In `mem-abs/run.out`, the boxed run without a
   contract reports a counterexample at depth 3. Is the memory
   wrong? What line of the output says so, and what removes the
   trace? *(No; the black-box note; the contract at `sa`.)*
3. **Two side conditions.** The wrap mutant is found at depth 1 from
   invariant states. Which two facts make a proof from those states a
   proof from reset, and which row of `init-value/run.out` proves the
   one that is a run? *(INV holds at reset and is inductive;
   `INV_A proven`.)* Why is the depth-0 counterexample of the weak
   start set not a bug? *(Its start state is unreachable.)*
4. **The vanished properties.** A colleague's FIFO proof reports
   only the shell's assumptions after they added `$anyconst`. What
   happened, and what is the accepted spelling? *(The RTL properties
   were dropped without a message; a free input with
   `assume {$stable(x)}`.)*
5. **Is it symmetric?** For the four-port round-robin arbiter with
   `last` reset to 3, give the permutation of ports that maps its
   transition relation to itself and say which of the three
   conditions fails. *(Rotation by one port, with `last` rotated;
   the initial state is not fixed.)* Under which change does "port 0
   proven" cover all four? *(A free initial `last`, with reset shown
   to be in the start set.)*
6. **Fixed priority.** From `symmetry/run.out`, which ports fail and
   at what depth? *(1, 2, 3; depth 5.)* Give the request pattern
   that starves port 3 for four cycles. *(Port 0 or a lower-numbered
   port requesting every cycle.)*
7. **The wrong side.** In `protocol/run.out` part D, which row shows
   that the checker was bound with the wrong role, and why is the
   proven assertion worthless? *(`c_in_drop` unreachable; the
   assumption on the output constrains the input through the wire.)*
8. **Prophecy at depth 1.** Explain from the two-row trace of
   `history/run.out` part D why the assumption that checks the guess
   does not remove it. *(The trace ends before the k-th pop, where
   the assumption would be evaluated.)*
9. **A sound ring.** In `ag/run.out`, which register makes the safety
   ring sound, and why does the same argument not prove the liveness
   ring? *(Each block's output register: each guarantee at t+1 needs
   the other only up to t; "eventually" is never violated at a
   particular cycle, so there is no first violation to induct on.)*
10. **Complete the split.** The three-case list on `a[7:6]` proves
    every case. Which assertion fails, at what depth, and which case
    is missing? *(`A_cover3`; depth 0; `a[7:6] == 3`.)*
11. **Half a contract.** With only "empty iff `g == 0`" assumed for
    each boxed FIFO, P2 fails at depth 1. Give the free behavior of a
    boxed FIFO that the trace uses. *(`full` raised with the FIFO
    not full.)*
12. **The partial dead end.** In `sanity/run.out` part C, which cover
    is reached and which is not, and which of them is the one that
    exposes the assumption? *(`Deep_C` covered at depth 51;
    `Witness_C` unreachable; the witness cover.)*

Answers that cite a `run.out` are fixed when the examples are
written. Exercise 5's second answer depends on the free-`last`
measurement (1.2(1)); if it fails, the exercise keeps its first part.

## 6. Deliberately not here, and what is cited by label

**Owned by Chapter 9 (cited, not repeated):** SVA syntax and
semantics; vacuity; assert, assume, cover; `bind` and where
properties live (`@sec-ch09-where`), with the Definition of
assumption and assume-guarantee and the checker-both-ways idea; the
DMA's six AXI master rules proved (`@sec-ch09-axi`); the reset trap;
dropped immediate assertions; the FIFO checker's `occ` model
(`@sec-ch09-example`).

**Owned by Chapter 18 (cited, not repeated):** reachable set,
invariant, inductive invariant (`@sec-ch18-reach`); bounded proof
and completeness threshold (`@sec-ch18-bmc`); k-induction and the
counterexample to induction (`@sec-ch18-induction`); one helper and
its two obligations (`@sec-ch18-helper`); IC3 vocabulary
(`@sec-ch18-ic3`); assumption as constraint, over-constraint
(`@sec-ch18-assume`); cover as reachability and witness cover
(`@sec-ch18-cover`); lasso, liveness-to-safety, fairness
(`@sec-ch18-liveness`); engine choice and the engine table
(`@sec-ch18-engines`); the eight-step procedure and proof record
(`@sec-ch18-example`); the tool's tables (`@sec-ch18-reference`).

**Left to later chapters (named, not numbered):** equivalence as a
flow, connectivity, register checks, X-propagation and clock gating
(Equivalence, Structural and Static Verification); coverage
exclusion and sign-off (Metrics, Closure and Sign-off); information
flow and security properties (Safety and Security Verification);
mutation as a method and MCY (Mutation Testing: Qualifying the
Testbench); register models (Registers and Reuse); reference models
in simulation (Reference Models and the Foreign Boundary);
multi-clock formal modeling (equivalence chapter or later).

**Stated here and not again:** over- and under-approximation and the
preservation rule; side condition; black box, cut point, timer
abstraction, parameter reduction, memory abstraction, initial-value
abstraction; symbolic constant, oracle, data independence, two-word
check, symmetry with its reset condition; ghost state, history and
prophecy variables, protocol checker with a role parameter;
assume-guarantee soundness conditions, case split with completeness,
hierarchical contract, property decomposition; assumption sanity by
witness covers; mutation for property sets.

## 7. Primary sources behind the full entries: read, and not read

All reads on 2026-11-16, through a fetch tool that returns the
document's extracted text summarized against a question (C11): what
is recorded is the section, definition or theorem located, not a
checked wording. "Read" below means abstract, introduction and the
named section.

| entry | source (refs key, proposed) | status | URL of the copy read | what it supports in the chapter |
|---|---|---|---|---|
| 3.2, T1, T2, T4 | Clarke, Grumberg, Long 1994, TOPLAS (`clarke1994abstraction`) | **read**: abstract, introduction, the preservation corollary (abstract truth of a universal formula implies concrete truth; exact when the abstraction is a congruence) | https://orna.cswp.cs.technion.ac.il/wp-content/uploads/sites/72/2022/12/abstraction.pdf (author-hosted; venue and section numbers garbled in the extraction, venue from the DOI record) | over-approximation preserves universal (safety) properties |
| T3 | Emerson, Kahlon 2000 (`emerson2000cutoff`, new, report form) | **read**: abstract, section 1 (cutoffs for asynchronous process templates with disjunctive or conjunctive guards; not a theorem about parameterized hardware) | https://www.cs.utexas.edu/ftp/techreports/tr00-03.pdf | "cutoff results exist only for restricted classes" |
| T4 | Pnueli, Xu, Zuck 2002 (`pnueli2002counter`) | **abstract only** (counters of processes per local state saturated at 2) | https://www.wisdom.weizmann.ac.il/~verify/publications/2002/PXZ02.html | "the term means something else there" |
| T5 | Burch, Dill 1994 (`burch1994pipelined`) | **read**: abstract, introduction, the read/write memory model over an unbounded address space | https://cs.uwaterloo.ca/~jmatlee/Teaching/CS745/PaperPres/BurchAndDill.pdf (authors' extended version with appendix) | memory as read/write terms independent of size |
| T5 | Bjesse 2008 (`bjesse2008memory`) | **not opened** (dblp blocked the fetch; no open copy found) | — | title level only, or cut |
| T5 | Bryant, German, Velev 2001 | **not opened** | — | not cited in the chapter |
| T8 | SymbiYosys "Formal extensions to Verilog" | **read**: `anyconst`, `anyseq`, `allconst`, `allseq` as attributes Yosys supports; the page says nothing about IEEE status | https://yosyshq.readthedocs.io/projects/sby/en/latest/verilog.html | "one tool's extension"; IEEE status unstated until the standard is checked |
| T9, T10 | Wolper 1986 (`wolper1986expressing`) | **not opened** (metadata only: bibtex.github.io record; no open copy found) | — | title-level attribution of the term; no sentence about what the paper states |
| T12 | Emerson, Sistla 1996 (`emerson1996symmetry`) | **read**: abstract, sections 1-3; automorphism definition including the initial state (2.5, condition 4); Theorem 3.3 | https://people.irisa.fr/Nicolas.Markey/PDF/Papers/fmsd9(1-2)-ES.pdf | the three conditions of a sound symmetry argument; 1.2(1) |
| T12 | Clarke, Enders, Filkorn, Jha 1996; Ip, Dill 1996 | **not opened** (Crossref and unpaywall records only; initials) | — | further reading at most |
| T13 | Owicki, Gries 1976 (`owicki1976axiomatic`) | **read**: abstract, section 1, Definition 3.6 (auxiliary variables), rule 3.7 (deleting them) | https://ilyasergey.net/CS6213/_static/papers/OwickiGries.pdf (course mirror of the journal text) | ghost logic that only writes itself does not change the result |
| T15 | OpenTitan `tlul_assert.sv` (`opentitan-tlul-assert`) | read for Chapter 9 (2026-11-15), not re-read | — | one checker, role parameter |
| T15 | ZipCPU `wb2axip` README and `bench/formal/faxil_slave.v` | **read**: hard-coded `SLAVE_ASSUME`/`SLAVE_ASSERT` macros, no switch; only slave files listed for AXI-lite | https://github.com/zipcpu/wb2axip ; https://github.com/ZipCPU/wb2axip/blob/master/bench/formal/faxil_slave.v | correction of RN T15 (1.2(8)); not cited in the chapter |
| T16 | Abadi, Lamport 1991 (`abadi1991refinement`) | **read in the 1988 report version** (DEC SRC Research Report 29): abstract, section 1, section 5 (history variables 5.1, Proposition 4; prophecy 5.2-5.3, Proposition 5, condition P6) | https://ftp.mirrorservice.org/sites/www.bitsavers.org/pdf/dec/tech_reports/SRC-RR-29.pdf | definitions; both leave visible behavior unchanged; a prophecy without finiteness can rule out behaviors |
| T18 | Abadi, Lamport 1995 (`abadi1995conjoining`) | **read**: abstract, sections 1, 2.2, 5 (composition theorem; guarantee one step longer than the assumption; assumptions as safety properties) | https://microsoft.com/en-us/research/uploads/prod/2016/12/Conjoining-Specifications.pdf | safety circularity sound, liveness assumptions break it |
| T18 | McMillan 1999, circular liveness (`mcmillan1999circular`) | **read**: abstract, sections 1-2 (induction over time, unit-delay edges breaking every cycle) | https://link.springer.com/content/pdf/10.1007/3-540-48153-2_30.pdf | condition for sound circular liveness reasoning |
| T18 | Misra, Chandy 1981 (`misra1981proofs`) | **not opened** (the DTIC file found is a different report) | — | title-level attribution only |
| T19 | McMillan 1999, compositional (`mcmillan1999compositional`) | **read**: abstract, sections 1 and 3 (temporal case splitting, Theorem 1; cases range over all values) | https://link.springer.com/content/pdf/10.1007/3-540-48153-2_17.pdf | case split with completeness |
| T30 | Chockler, Kupferman, Kurshan, Vardi 2001 | read by the research note (RN T30), not re-read | — | mutation-based coverage |
| T30 | DeMillo, Lipton, Sayward 1978 | in `refs.bib` from an earlier chapter, not re-read | — | origin of mutation |
| T20, T21, T6, T29, T10 | none exists or none found (RN 7(6)) | — | — | defined in the book's words, attributed to nobody |

Compact entries (T7, T24, T31 and the rest) and the recipes cite at
title level only; none of their sources was opened here except as
listed in the research note. A sentence that needs an unopened
source waits until it is read or is cut.

Bibliography corrections made in the research note's section 6 (the
note's own record of them is at the end of its BibTeX block): both
McMillan 1999 entries gain the LNCS volume 1703 printed on the papers
and keep the author as printed (K. L. McMillan); Abadi and Lamport
1991 gains a note that the report version was read; Abadi and
Lamport 1995 gains a note that the author-hosted copy prints pages
507-533 against Crossref's 507-535 (Crossref kept); Burch and Dill
gains a note on the extended version read; Emerson and Kahlon is
added in report form. No author name or URL among the entries opened
was found wrong; the one wrong attribution found is the T15 claim
about `gisselquist2021axirules` (1.2(8)), recorded in the note.

## 8. Gate-1 checklist (against AGENTS.md)

| requirement | where met |
|---|---|
| every section names what the reader must be able to do | "Reader can" for 3.1-3.10 and for every full entry; objectives 1-9 map to 3.2 (1), 3.3 (2, 3), 3.4 (4, 5), 3.5 (6), 3.6 (7), 3.8 (8), 3.6 and 3.10 (9) |
| the research note's constraints are folded in | section 1.3 (C1-C12) cites RN Q1-Q4, M1-M11, section 7; RN section 8's eight questions are answered by D1-D9 and 1.2; RN 7(8) (the unkept bounded run) becomes a measurement in `decomp/` |
| a question that changes the chapter's shape is raised, not chosen | none found; the four contradictions in 1.2 change examples, not shape, and are settled under the delegation with their measurements listed |
| house template | epigraph, objectives, motivation (3.1), concepts (3.2-3.9), worked example (3.10), callouts of six kinds only (census above), future directions (3.11), summary, exercises, further reading |
| every listing a file under `examples/` | section 4; no code in prose; Chapter 9, 11 and 18 RTL read by path; Chapter 9's `hs_check.sv` not edited (`hs_rules.sv` is new) |
| simulator and tool output from `run.out` | every verdict cited is a `run.out` row of an example in section 4; seconds only in `tbl-ch19-seconds` (D12) |
| every number sourced | research `run.out` lines, FM rows and the read sources of section 7; no 60 s figure from the research is printed (D11) |
| 80 columns, 72-column rulers, real tabs | section 4 preamble (80-column pass on every research file) |
| cross-references by label, later chapters by name | section 6; no chapter, section or figure number in the outline's planned prose |
| American spelling | to be held in the draft ("modeled", "behavior") |
| attribution and originality | section 7: what was read, what was not; C11 (no quotation); recipes and compact entries at title level; vendor statements labelled (C12); figures drawn from the book's own runs or as schematic diagrams, none reproduced |
| the book never cites its working documents | the chapter cites `run.out` via splices and `refs.bib` keys, never `research/` |
| publication rule | no assistant or vendor of it named in this outline or in planned files |
| registration in `_quarto.yml` | under "Part IV · Proof and Probability", after `ch18`, before the generative-AI chapter (at draft time) |
| 8 to 12 exercises with determinate answers | section 5: twelve |
| new glossary terms | over-approximation, under-approximation, side condition, black box, cut point, timer abstraction, parameter reduction, cutoff, memory abstraction, symbolic slot, initial-value abstraction, symbolic constant, oracle input, data independence, two-word check, symmetry, automorphism, ghost state, reference model, history variable, prophecy variable, protocol checker role, assume-guarantee (cited from Ch. 9), case split, completeness check, hierarchical contract, property decomposition, assumption sanity, design mutant, proof core |
| new `refs.bib` entries (about 20) | Clarke-Grumberg-Long 1994; Emerson-Kahlon 2000 (report); Pnueli-Xu-Zuck 2002; Burch-Dill 1994; Emerson-Sistla 1996; Owicki-Gries 1976; Abadi-Lamport 1991 and 1995; McMillan 1999 (two); Misra-Chandy 1981 and Wolper 1986 (title level, flagged); Clarke et al. 2000 CEGAR and McMillan-Amla 2003 (compact, title level); Ghassabani et al. 2016; Chockler et al. 2001; Terauchi-Aiken 2005, Clarkson-Schneider 2010, Barthe et al. 2004 (recipe R5, title level); van Eijk 2000 (R6, title level); the SymbiYosys extensions page; vendor app pages as vendor statements; Seligman et al. (further reading). Bjesse 2008 and the two other 1996 symmetry papers only if opened |

Gate-1 verdict proposed for `STATUS.md` (to be written by the
session that records the gate, not by this outline): passes under
the delegation on 2026-11-16, with the measurements of section 4's
list as preconditions for drafting the entries that need them.

## 9. Pre-draft measurements

Run 2026-11-16 with InFormal 0.1.0 at `5114330` and rIC3 1.5.2,
through the book's wrapper (`examples/mk/informal.sh`), one engine
selected for each `prove` and a fresh session (`design`, from
`examples/ch19-formal-techniques/common/ch19.tcl`) before each one,
so that no report row carries a verdict from an earlier engine (C1).
Every result below is now a row of an example's `run.out` under
`examples/ch19-formal-techniques/`, checked there with `expect`;
the command for each is `scripts/check-examples.sh
ch19-formal-techniques/<dir>`. Section 4's table changes as follows:
`track-word-ric3/` is replaced by an in-house `track-word/`;
`two-word-ric3/` keeps the rIC3-alone rows and an in-house
`two-word/` is added; `init-value-ric3/` is folded into
`init-value/`; the optional `conn-irq/` and `reg-readback/` were not
built (R1 and R2 stay prose). Twenty-four directories, five of them
`REQUIRES := ric3` (`mem-abs-ric3`, `two-word-ric3`, `history-ric3`,
`hier-ric3`, `seconds-ric3`).

**Two tool findings met on the way, both affecting the text.**
(i) An assumption whose consequent spans several cycles
(`req && !busy |=> !u_timer.expired [*199]`) constrains only traces
long enough to hold its whole window: under the cut it does not remove
the depth-3 trace of `a_no_early`, although the one-cycle form
(`$rose(busy) |-> !u_timer.expired`) does (`cut-timer/run.out`, block
F, with the trace table). This is the prophecy trap of T16 met in an
ordinary assumption; T4 and T16 should say it once and point to each
other. (ii) A `parameter string ROLE` compared in a generate `if`
(`ROLE == "SENDER"`) elaborates without error and yields an empty
property table, and `-parameter OUT_ROLE "RECEIVER"` is rejected as
an invalid override; `hs_rules.sv` uses an enum from a package
(`hs_role_pkg::SENDER`, `RECEIVER`) instead. Another silent loss of
properties of the kind C5 describes.

| # | measurement | command (example, block) | verdict | entry |
|---|---|---|---|---|
| 1 | 1.2(1) free-`last` arbiter | `symmetry/`, A and B | free start (`FREE_LAST = 1`): `a_wait0` proven (kind); rotation check `rr_rot` (second copy fed rotated requests, `last` one more in the first cycle) `a_rot` proven, its start covered at depth 1; reset state inside the free start: `c_reset` covered at depth 1. With `last` reset to 3 in both copies the rotation check is refuted at depth 2; the four ports are proven one by one; fixed priority as before (ports 1-3 refuted at depth 5); DMA `a_excl0`, `a_excl1` proven in-house | **stands**, and gains a run: "the rotation is a symmetry" is now a proof (`a_rot`), and "reset breaks it" a counterexample, not only an argument. Exercise 5 keeps both parts |
| 2 | 1.2(2) DMA rules, `informal-ic3`, slave rules assumed | `protocol-dma/`, A | `hs_rules` bound as SENDER on AR, AW, W (asserted) and RECEIVER on R, B (assumed), `ANSWER = 0`: all six master rules proven by `informal-ic3`, three waits covered (depths 5, 8, 8); about a second | **stands**: no `REQUIRES := ric3`; D5's DMA clause is withdrawn. `ANSWER = 0` is needed because AXI lets ready come first, and Chapter 9's `Answer_A` would over-constrain the slave; T15's text says so |
| 3 | 1.2(3) a slave-dependent DMA property | `protocol-dma/`, B | `RFirst_A` (the R response the DMA takes after waiting is the one first offered; ghost `r_first.sv`): cex at depth 6 with no rules assumed, proven by `informal-ic3` with only the R/B rules assumed; `RWait_C` covered (6, 5) | **stands**: the DMA stays in T15 with this property and a pointer to `@sec-ch09-axi` |
| 4 | 1.2(5) slot-indexed helper, T9 | `track-word/`, A-C | DEPTH 16: `a_integrity` no verdict in 5 s by kind and by IC3; the helper (`!in_q || mem[rd_ptr + ahead] == sd && ahead < count`, with the pointer helper and `count <= DEPTH`, one conjunction) proven by kind; `a_integrity` proven with it assumed; `c_out` covered at depth 10; read-pointer mutant refuted at depth 3. (At DEPTH 256 the helper proves in about 10 s; not in the example) | **changes**: T9 is in-house; `track-word-ric3/` is dropped and `track-word/` teaches the helper. "rIC3 only" in C3 is cut for T9 |
| 5 | 1.2(5) slot-indexed helper, `p_ahead` | `two-word/`, A-C | DEPTH 4: position form alone, no verdict in 5 s (kind); slot helpers for both words plus the pointer helper plus the ordering, one conjunction, proven by kind (< 1 s); under it `p_head1`, `p_head2`, `p_ahead` and the flag form's `a_order` proven, `a_once1`, `a_once2` no verdict in 5 s; duplicating mutant caught by all six (depths 3, 3, 4, 6, 3, 5). At DEPTH 16 the same conjunction had no verdict in 20 s (probe, not in an example) | **changes**: the sentence "neither ordering assertion was proved" is cut. Ordering is proved, in-house, at DEPTH 4, in the position form with slot helpers, and `a_order` follows; what stays unproved is the flag form's once-only checks, which need "no other slot holds d1", the quantified invariant. `two-word/` (in-house) is new; `two-word-ric3/` keeps rIC3 alone: flag form no verdict in 5 s, `p_head1`/`p_head2` proven, `p_ahead` no verdict in 10 s |
| 6 | T4 gap assumption and its discharge | `cut-timer/`, C-F | under the cut, `$rose(busy) |-> !u_timer.expired` assumed: `a_no_early` proven, `c_gnt` covered at depth 4; the same proven as an assertion on the real timer (kind). The 199-cycle form leaves the depth-3 trace (finding (i)) | **stands**, with the one-cycle gap; the pitfall of finding (i) is added |
| 7 | T3 width probe | `param-width/` | Chapter 1's FIFO: `full |-> occ == DEPTH` refuted at depth 4 (DEPTH 4) and 16 (DEPTH 16), `occ == DEPTH` unreachable at both; repaired FIFO against a five-bit count (Chapter 9's width): proven at 16, refuted at 32 (depths 2, 1); `wr_ptr < DEPTH && rd_ptr < DEPTH` proven at 4 and 8, refuted at 5 (depth 6) | **changes**: "at the smaller depth the bug is absent" is cut: Chapter 1's bug is at every depth, and its small-size counterexample is the large one's. The non-transfer of proofs is shown by the five-bit count (16 to 32) and by `$clog2(5)` |
| 8 | T6 correct FIFO from INV, in-house | `init-value/`, C | DEPTH 16 from INV states: kind no verdict in 5 s, `informal-ic3` proven; DEPTH 256 from INV states with the pointer helper assumed every cycle: kind proven; INV proven from reset and from INV states (inductive). Other rows as in the research: wrap mutant cex 16 (DEPTH 16), no verdict in 5 s at 256, cex at depth 1 from INV, weak start cex at depth 0, `Full_C` at 257 and 0 | **changes**: `init-value-ric3/` is folded into `init-value/`; the text says that starting from INV does not make P inductive (kind fails at 16) and that the helper does |
| 9 | T9 at DEPTH 4 | `track-word/`, A | `a_integrity` alone proven by `informal-ic3` (about 2 s; rIC3 0.3 s in the probe) | **changes**: in-house at DEPTH 4 without a helper; the example prints it as the row before the DEPTH-16 rows |
| 10 | T20 bounded block | `decomp/`, A | `informal-bmc`, 5 s each: E2E, L1, L2 no counterexample (`undetermined`), `Done3_C` covered at depth 15; kind and IC3 no verdict in 5 s; E2E proven with L1, L2 assumed. About 50 s | **stands**, at a 5 s limit (not 8 s) |
| 11 | T30 combined mutant table | `mutants/` | 2 s bounded search per property, Chapter 9 checker (bound) + `EmptyPtrs_A` + `a_integrity`: dup killed by `a_integrity` (3) and `EmptyPtrs_A` (4); wrap by `EmptyExact_A`, `Sync_A`, `EmptyPtrs_A` (16), `FullForward_A` (17), `NoOverflow_A` (18); skip by `a_integrity`, `EmptyPtrs_A` (3). Chapter 9's checker kills only the wrap mutant; `a_integrity` does not kill wrap within 2 s | **stands**; the text can add that the occupancy checker alone misses both data mutants |
| 12 | worked-example contract and covers at 256 | `pipe-256/` | child: `H_A` proven, `CE_A`/`CF_A` proven with it assumed (kind, well under a second); boxed parent: `Drain_C` (depth 4), `Both1_C` (3), `U1Full_C` (258, about 7 s) covered, `Full_C` (P2's antecedent, 513 deep) no verdict in 10 s; P1/P2 no verdict in 5 s; `HP_A` proven; P1/P2 proven under it; wrap-mutant child refutes `H_A` at depth 256 (about 8 s; `CE_A`/`CF_A` themselves gave no counterexample in 10 s, so step 7 names the helper, not the contract) | **changes** in two sentences: step 1 says P2's own witness is out of reach and uses `U1Full_C` and the two shallow covers; step 7 says the mutant is caught by the child's ghost helper. About 37 s, not 25 |
| 13 | C6 `$stable` in cycle 0 | `symconst/`, C | `first |-> sa0 == sa` (sa0 holds sa from the reset cycle) proven; `first && sa0 != sa` unreachable; `first` covered at depth 1 | **changes**: C6's third clause is cut. A `$stable` assumption does bind the reset cycle to the next one in this tool; T8's pitfall becomes "a stable value is stable across a mid-trace reset too" only |
| 14 | C10 boxed assertions | `cut-timer/`, A and B (`timer_chk.sv` bound into `timer`) | unboxed: `Range_A` proven; with `-bbox_m {timer}` it stays in the report with status `error`, detail "not in the model (inside a black box)"; the same for Chapter 9's checker bound into a boxed `fifo` (probe) | **changes**: RN T1(3) "silently leaves the table" is wrong; the sentence becomes "stays listed as an error, unchecked", from `run.out` |
| 15 | C5 `$anyconst`, re-run | `symconst/`, A | with only the RTL assertion: zero properties listed, an empty table, no message. (A property added by Tcl to the same design gets status `error` naming `$anyconst`; its detail prints the absolute file path, so that block is left out of the example) | **stands** for RTL properties; the Exercise 4 answer holds. Add: a Tcl property in the same session does get an error |

Times measured by the second clean run of every example are in
section 4's terms: see the table below, which replaces section 4's
"time" column.

| directory | needs | time (s) | directory | needs | time (s) |
|---|---|---|---|---|---|
| `cut-timer/` | informal | 8.9 | `protocol-dma/` | informal | 1.8 |
| `param-width/` | informal | 4.8 | `history/` | informal | 0.5 |
| `mem-abs/` | informal | 29.9 | `history-ric3/` | ric3 | 21.1 |
| `mem-abs-ric3/` | ric3 | 9.5 | `ag/` | informal | 0.5 |
| `init-value/` | informal | 17.2 | `case-split/` | informal | 35.7 |
| `symconst/` | informal | 0.5 | `hier/` | informal | 11.9 |
| `track-word/` | informal | 12.8 | `hier-ric3/` | ric3 | 6.1 |
| `two-word/` | informal | 27.5 | `decomp/` | informal | 46.5 |
| `two-word-ric3/` | ric3 | 31.1 | `sanity/` | informal | 0.6 |
| `symmetry/` | informal | 0.9 | `mutants/` | informal | 38.0 |
| `contract/` | informal | 17.0 | `pipe-256/` | informal | 36.4 |
| `protocol/` | informal | 0.7 | `seconds-ric3/` | ric3 | 88.8 |

Wall-clock of `scripts/check-examples.sh` from `make clean`, lint
included. In-house total about 5 minutes (longest `decomp/`, 47 s);
the five rIC3 directories about 2.5 minutes more, of which
`seconds-ric3/` is 89 s (it is skipped in CI and regenerates
`tbl-seconds.md` only with `MEASURE=1`). Two clean runs gave
byte-identical `run.out` in every directory.
