# Research note: Formal Techniques (Chapter 19)

Date: 2026-11-16. Status: research for gate 1 (no outline yet).
Written section by section, the deciding questions first. Sections:
1 questions that decide the chapter, 2 measurements (the "To measure"
and "By hand" entries of the approved plan), 3 the catalog, one block
per technique with sources, soundness, pitfalls and InFormal status,
4 the six recipes, 5 the worked-example spine, 6 bibliography,
7 confidence notes, 8 open questions for the outline.

Scope given: design doc section 4, entry 19, and the approved plan
(project review folder, `2026-11-15-informal/formal-plan.txt`, lines
112-350): 31 techniques in six families, each entry with six parts
(problem, idea, how to write it, what it preserves, a runnable
example, pitfalls), plus one short recipe each for connectivity,
register access, X-propagation, unreachable-coverage analysis,
information flow by self-composition and clock-gating equivalence.

Pins for every measurement below: InFormal 0.1.0 at commit `5114330`
(`informal --version` prints `informal 0.1.0`), CaDiCaL linked,
Bitwuzla not built; rIC3 at `4d63899` as `ric3`, listed in the book's
`examples/mk/informal-engines.toml`; 4 cores, 15 GB. Every run goes
through the book's own wrapper `examples/mk/informal.sh` (time column
stripped, `expect` and `finish` from `examples/mk/informal.tcl`), one
engine selected per `prove`, a per-property limit of at most 60 s.
Seconds come from a separate timed run of the same script (section
2.0). Scripts and outputs: `research/ch19-measurements/<name>/`.

What the previous chapter already teaches and this chapter must cite
by label, not repeat (from `research/ch18-outline.md` section 6 and
`chapters/ch18-formal-property-verification.qmd`): reachable set,
invariant, inductive invariant; bounded proof; base and step case,
counterexample to induction, unique-states completeness; one helper
invariant written and assumed (`@sec-ch18-helper`); IC3 frames,
lemmas, proof obligations; assumption as constraint, over-constraint
and contradiction (`@sec-ch18-assume`); cover as reachability and the
witness cover (`@sec-ch18-cover`); lasso, liveness to safety, one
fairness assumption (`@sec-ch18-liveness`); engine choice; the
pointer property's scaling grid at 64 entries (`@sec-ch18-example`).
Chapter 9 owns SVA syntax, vacuity defined, the reset trap and the
silently dropped immediate assertions.

## 1. The questions that decide the chapter

### Q1. Do the eleven "To measure" and "By hand" entries work?

**Every one runs, and every one has a mutant or a control that the
technique catches; four of them did not give the verdict the plan
expected.** Section 2 has the table. In order of how much they change
the chapter:

1. **Property decomposition on the DMA (T20, M7) moved the
   difficulty, it did not remove it.** The end-to-end property
   (a channel that finishes without error has had as many write
   responses as the length it was started with) follows from two
   local lemmas in 0.06 s, but neither lemma, nor the end-to-end
   property, got a verdict from any engine (k-induction, in-house
   IC3, rIC3) in 60 s, and a 40 s bounded search found no
   counterexample to them either. The lemmas are true but need the
   DMA's own invariants (a write in flight implies the channel is
   busy), and one of those (`rd_fly[c] |-> busy[c]`, M3) is itself
   `undetermined` for every engine. The chapter can show the
   decomposition step honestly only as "the chain is sound and the
   last link is easy; the first links are where the work is", or it
   must add the DMA invariants as a further layer of lemmas (not
   measured).
2. **Two-word ordering (T10, M2) is the hardest entry.** In the flag
   form (each word in, each word out) no engine gave a verdict in
   60 s even at DEPTH 4. In the position form (words ahead of each
   tracked word, as FM H tracks one) rIC3 proves that each tracked
   word is at the head when its count reaches zero (0.44 s and
   5.2 s at DEPTH 4), but not the ordering lemma, and nothing at
   DEPTH 16 within 60 s. The duplicating mutant is caught at once by
   bounded search. Reason, worked out by hand and not measured: the
   flag properties need an invariant over the memory contents ("no
   slot other than the tracked one holds d1"), which is a quantified
   statement over slots; the single-word check of FM H avoids it.
3. **Hierarchical proof (T21, M9) did not get cheaper by boxing
   alone.** With both FIFOs black-boxed under their proved contracts
   the parent properties were no easier than flat for rIC3 (DEPTH
   64: 31.2 s boxed against 25.7 s flat for one property, 9.8 s
   boxed against no verdict in 60 s flat for the other; at DEPTH 256
   neither finishes), and k-induction proved neither form. Boxing
   removes the memories, but these control properties read only
   counters and flags, so the memories were never what made them
   hard (whether the tool's own cone reduction already dropped them
   was not checked); the difficulty is the
   counting invariant across the two blocks. With the parent's own
   helper (the pipe's count is the sum of the two blocks' counts,
   each at most DEPTH) proved and assumed, k-induction proves both
   parent properties at DEPTH 16, 64 and 256 in well under a second
   each. So the chapter's hierarchical entry is two techniques in
   one: contract-based boxing plus a parent-level helper.
4. **The protocol checker as assumption (T15, M4) works exactly as
   planned on the small stage**, and on the DMA the same checker
   bound five ways is proved by rIC3 in 0.08 to 0.16 s per rule, but
   k-induction leaves the three `$stable` data rules `undetermined`
   in 60 s (the hold rules prove in 0.04 s). FM B.1's "six AXI rules
   proved in 0.08 to 0.32 s" was the default portfolio; with one
   in-house engine selected, three of them have no verdict. Any
   chapter example that runs the DMA rules must select rIC3.

The other seven gave the expected verdicts: memory abstraction (a
256-word proof by induction in 0.02 s under the abstraction),
symmetry (round robin proves on all four ports, fixed priority only
on port 0), history and prophecy (the naive prophecy is a spurious
counterexample at depth 1), case split (the forgotten case is caught
only by the completeness check), assume-guarantee (safety ring sound,
liveness ring false), initial-value abstraction (a bug 256 pushes
deep from reset is found at depth 1 from invariant states) and
assumption sanity (a partial dead end passes the deep cover and is
caught only by the witness cover).

### Q2. Which entries need rIC3?

Measured here, an entry whose example has no in-house engine that
proves it within 60 s: memory abstraction's flat comparison (the
abstraction itself proves by k-induction), the history variable on
the FIFO (M5 C, 9.8 s) and the prophecy version (M5 E, 11.9 s), the
two-word position form (M2), the DMA protocol rules (M4 E), the DMA
per-channel FIFO bound in symmetry (M3), the initial-value proof of
the correct FIFO at 256 words (M10 C, 34.4 s; it also needs a helper
under induction), and the flat and boxed pipes without the parent
helper (M9). The book's engine list names `ric3-ic3` and an example
that selects it declares `REQUIRES := ric3`; the outline should mark
each entry's example as in-house or rIC3 (section 8, question 5).

### Q3. Is a six-part entry possible for all 31 techniques?

Yes in content (section 3 gives sources, soundness and pitfalls for
each), but not at uniform depth: four entries are not available in
the tool (localization and refinement, bounded proof with a depth
argument, cover-guided deep search, proof-core coverage) and six are
owned by the previous two chapters. Section 8, question 1 proposes a
compact form for those ten.

### Q4. What carries the chapter?

Three designs the book already has: the FIFO (about 14 entries),
a valid/ready handshake with the 200-cycle timer block (about 10),
and the two-channel DMA (about 7, plus three recipes). Section 5.

## 2. Measurements (run 2026-11-16)

### 2.0 How the numbers were taken

Every script is `research/ch19-measurements/<name>/<name>.tcl`, run
by `research/ch19-measurements/run.sh <name>`, which calls the
book's wrapper `examples/mk/informal.sh` (engine list
`examples/mk/informal-engines.toml`, time column stripped) and keeps
two files beside the script: `run.out` (what an example's `run.out`
would hold) and `timed.out` (the same report with the seconds the
tool printed for each property, plus the wall time of the whole
script). Each `prove` selects one engine with the previous chapter's
`one` procedure (from `examples/ch18-formal-property-verification/
common/proof.tcl`, sourced, not copied) and sets a per-property limit
of at most 60 s. `undetermined` means "no verdict within the limit
printed above it" and nothing more. Up to three scripts ran at once
on the 4-core machine (each engine run is single-threaded); seconds
are wall-clock and vary by run. A `run.out` here is evidence for
this note, not a chapter example: the chapter's examples must be
rebuilt under `examples/ch19-*/` with the house Makefile pattern.

Two FIFO mutants were generated with `sed` from the book's
`fifo_fixed.sv` and saved with a header naming the change:
`two-word/fifo_dup.sv` (the read pointer does not move on a cycle
that pushes and pops), `initial-value/fifo_wrap.sv` (the count wraps
to zero on the push that would make it DEPTH - 1). Other designs are
new and small: `mem_abs.sv` (16 or 256 words), `rr_arb.sv` (4 ports),
`vr.sv` (a valid/ready stage), `hp.sv` (a grant unit and a k-th-word
tracker on the 4-entry FIFO), `mul.sv` (an 8- or 10-bit multiplier
miter), `dma_wcount.sv` (ghost state bound into the DMA), `hier.sv`
(two FIFOs in series), `ag.sv` (two one-register blocks),
`iv.sv` (the FIFO with a first-cycle flag), `sanity.sv` (a counter
with a mode).

### 2.1 Table of measured verdicts and seconds

Engines: kind = `informal-kind`, ic3 = `informal-ic3`, bmc =
`informal-bmc`, ric3 = `ric3-ic3`. "u (L)" = undetermined at limit L.

| M | entry | run | engine | verdict | s |
|---|---|---|---|---|---|
| M1 | T5 memory abstraction | whole, 16 words, `a_read` | kind | u (20 s) | - |
| | | whole, 16 words | ric3 | proven | 0.10 |
| | | helper `sv_ok -> m[sa]==sv` alone, 16 words | kind | proven | 0.04 |
| | | `a_read` with the helper assumed, 16 words | kind | proven | 0.06 |
| | | whole, 256 words | kind | u (20 s) | - |
| | | whole, 256 words | ric3 | proven | 9.34 |
| | | helper alone, 256 words | kind | proven | 7.49 |
| | | **storage boxed, contract at sa assumed, 256 words** | kind | **proven** | **0.02** |
| | | storage boxed, no contract | bmc | cex depth 3 (spurious) | 0.02 |
| | | contract on the storage, 16 / 256 words | kind | u (20 s) / u (20 s) | - |
| | | contract on the storage, 16 / 256 words | ric3 | proven / proven | 0.10 / 8.23 |
| | | contract, helper assumed, 16 / 256 words | kind | proven / proven | 0.04 / 11.73 |
| | | forwarding bug, boxed and whole | bmc | cex depth 3, both | 0.02 |
| M2 | T10 two-word ordering | flag form (order, once each), DEPTH 4 | ric3 | u (30 s), all three | - |
| | | flag form, DEPTH 4 (first run, `two-word/first-run.out`) | kind, ic3, ric3 | u (60 s), all three, each engine | - |
| | | position form, DEPTH 4: head1 / head2 / ahead | kind | u (60 s), all three | - |
| | | position form, DEPTH 4: head1 / head2 / ahead | ric3 | proven / proven / u (60 s) | 0.40 / 5.15 / - |
| | | position form, DEPTH 16 | kind, ric3 | u (60 s), all three, both | - |
| | | flag form with the position properties assumed, DEPTH 4 | kind, ric3 | u (60 s), all three | - |
| | | duplicating mutant, DEPTH 4: flag / position properties | bmc | cex depth 3-6, all six | 0.02 |
| | | duplicating mutant, DEPTH 16: `a_order` | bmc | cex depth 18 | 3.73 |
| | | witness cover (d2 leaves after d1) | every engine | covered depth 3 | 0.02-0.06 |
| M3 | T12 symmetry | round robin, bounded wait on ports 0-3 | kind | proven x4 | 0.02 each |
| | | fixed priority, port 0 / ports 1-3 | kind | proven / cex depth 5 | 0.02 |
| | | DMA `!(busy&&done)`, ch 0 / ch 1 | kind | proven / proven | 0.08 / 0.06 |
| | | DMA `rd_fly -> busy`, ch 0 / ch 1 | kind, ric3 | u (60 s), all four | - |
| | | DMA `in_fifo <= 2`, ch 0 / ch 1 | kind | u (60 s) / u (60 s) | - |
| | | DMA `in_fifo <= 2`, ch 0 / ch 1 | ric3 | proven / proven | 0.08 / 0.08 |
| M4 | T15 protocol checker | wire stage, input free | bmc | cex depth 2 (both rules) | 0.02 |
| | | wire stage, input rules assumed | kind | proven (both) | 0.02 |
| | | register stage, input free | kind | proven (both) | 0.02 |
| | | wire stage, output rules assumed by mistake: input rule asserted / input-drop cover | kind | proven / unreachable | 0.02 |
| | | DMA: AR, AW, W hold rules | kind | proven | 0.04 |
| | | DMA: AR, AW, W `$stable` rules | kind | u (60 s) | - |
| | | DMA: all six rules | ric3 | proven | 0.08-0.16 |
| M5 | T16 history, prophecy | `gnt |-> $past(req) or (req,2) or (req,3)`, correct unit | bmc | cex depth 5 (false alarm) | 0.02 |
| | | history bit `seen`, correct / mutant | kind | proven / cex depth 1 | 0.02 |
| | | k-th word out = k-th in, history (FIFO 4) | kind | u (30 s) | - |
| | | same | ric3 | proven | 9.84 |
| | | prophecy, asserted at the push | bmc | cex depth 1 (spurious) | 0.02 |
| | | prophecy, asserted at the pop | kind / ric3 | u (30 s) / proven | 11.90 |
| M6 | T19 case split | 8-bit miter, whole | kind | proven | 18.52 |
| | | four cases on `a[7:6]` | kind | proven x4 | 3.12, 4.60, 4.83, 5.01 |
| | | completeness of the four cases | kind | proven | 0.02 |
| | | bug in case 3: cases 0-2 / case 3 | kind | proven / cex depth 0 | 3-5 / 0.02 |
| | | completeness of a three-case list | kind | cex depth 0 | 0.02 |
| | | 10-bit miter, whole and each of four cases | kind | u (60 s), all five | - |
| M7 | T20 decomposition (DMA) | E2E, L1, L2 alone | kind, ic3, ric3 | u (60 s), all nine | - |
| | | E2E, L1, L2 (scratch run) | bmc | u (40 s) | - |
| | | witness cover (len 3 finishes) | kind / ric3 / ic3 | covered depth 15 | 0.26 / 4.71 / 24.13 |
| | | E2E with L1 and L2 assumed | kind | proven | 0.06 |
| M8 | T18 assume-guarantee | block alone, `in==0` assumed, `out==0` | kind | proven | 0.02 |
| | | block with reset value 1 | kind | cex depth 1 | 0.02 |
| | | ring, flat, both guarantees | kind | proven | 0.02 |
| | | block alone, `s_eventually in` assumed, `s_eventually out` | ic3 | proven | 0.02 |
| | | ring, flat, `s_eventually x` | ic3 | cex depth 3 (lasso) | 0.02 |
| M9 | T21 hierarchical | contract on one FIFO (empty, full), DEPTH 16 | kind | proven | 3.34 / 3.08 |
| | | same, DEPTH 64 | kind / ric3 | u (30 s) / proven | 0.04 / 0.06 |
| | | same with the helper `g == u.count` assumed, DEPTH 16 and 64 | kind | proven | 0.02 |
| | | helper `g == u.count`, DEPTH 16 and 64 | kind | proven | 0.02 |
| | | pipe, both boxed, contract assumed: P1 / P2, DEPTH 16 | kind | u (30 s) | - |
| | | same | ric3 | proven / proven | 1.10 / 0.48 |
| | | same, DEPTH 64 | ric3 | proven / proven | 31.16 / 9.83 |
| | | same, DEPTH 256 | kind, ric3 | u, all | - |
| | | half the contract (empty only), DEPTH 16: P2 | bmc | cex depth 1 (spurious) | 0.02 |
| | | pipe flat: P1 / P2, DEPTH 16 | ric3 | proven / proven | 1.31 / 2.75 |
| | | pipe flat, DEPTH 64 | ric3 | proven / u (60 s) | 25.73 / - |
| | | pipe flat, DEPTH 16 and 64 | kind | u (30 s), all | - |
| | | **boxed, parent helper proved (DEPTH 16 / 64 / 256)** | kind | **proven** | 0.04 / 0.06 / 0.14 |
| | | **boxed, parent helper assumed: P1, P2 at 16, 64, 256** | kind | **proven** | 0.02 each |
| | | witness cover (both FIFOs full), boxed, DEPTH 16 / 64 | kind | covered depth 33 / 129 | 0.28 / 24.35 |
| M10 | T6 initial value | wrap mutant from reset, DEPTH 16 / 256 | bmc | cex depth 16 / u (60 s) | 0.26 / - |
| | | wrap mutant from INV states, DEPTH 256 | bmc | cex depth 1 | 0.02 |
| | | correct FIFO from INV states, DEPTH 256 | kind / ric3 | u (20 s) / proven | 34.44 |
| | | INV from reset (the side condition) | kind | proven | 0.12 |
| | | weak start set (`count <= DEPTH`) | bmc | cex depth 0 (spurious) | 0.02 |
| | | cover `full`, from reset / from INV | bmc | depth 257 / depth 0 | 5.92 / 0.02 |
| M11 | T29 assumption sanity | no assumption: assertion / deep cover / witness | kind | cex 10 / covered 51 / covered 9 | 0.02 |
| | | dead end for every trace | kind | proven / unreachable / unreachable | 0.02 |
| | | dead end for mode-1 traces only | kind | **proven / covered 51 / unreachable** | 0.02 |

### 2.2 Notes on the runs

- **M1.** The flat design's induction failure is the same shape as
  the previous chapter's pointer property: the property is true but
  not inductive, and the helper that makes it inductive names the
  array element at the symbolic address (`u_ram.u_mem.m[sa]`; the
  shell accepts an array indexed by a free input). The abstraction
  removes the array from the model; what remains is a contract that
  the storage must be shown to satisfy (part E), which is the same
  helper again. So the chapter can say precisely what memory
  abstraction buys: the expensive obligation is proved once, on the
  storage alone, and every user of the storage is proved against
  the contract.
- **M2.** See Q1, item 2. The flag form's three assertions read as
  the plan's "order, loss and duplication", but they are not
  provable without a memory-content invariant. The position form
  is provable for one word at a time.
- **M3.** The DMA has one asymmetry, in reset: `r_last` starts at
  `NCH - 1`, so the channel swap does not map the reset state onto
  itself. Every per-channel property measured gave the same verdict
  on both channels, as expected from the design, but a symmetry
  argument would have to cover the reset state; with two channels
  the cheaper sound answer is to prove both.
- **M4.** Part D is the cautionary run: with the output's rules
  assumed (the checker instantiated on the wrong side), an assertion
  about the *input* is proved and a cover of the input dropping
  `valid` is unreachable, because the wire stage connects the two.
  The checker's `if (ASSUME)` generate block in a module, bound with
  `bind`, works in the shell; names come out as
  `dma_v2.u_ar.g_chk.Held_A`.
- **M5.** Part D is a measured consequence of checking safety on
  finite prefixes: the assumption that checks the guess at the k-th
  pop cannot remove a trace that ends at the k-th push. Part E is
  provable but is, logically, the history check of part C with an
  extra free variable.
- **M6.** Splitting the 8-bit miter into four cases cost 17.6 s in
  total against 18.5 s whole, so the split pays only by running the
  cases in parallel (about 5 s of wall time on four cores); at 10
  bits neither the whole miter nor any case finished in 60 s. A
  split on two operand bits does not shrink a multiplier enough.
- **M7.** See Q1, item 1.
- **M8.** The liveness counterexample is the composed ring's lasso
  of all zeros; each block's proof was correct under its assumption.
- **M9.** Not measured: the flat pipe with the same parent helper
  assumed (its proof would also need each FIFO's `g == u.count`), so
  the table does not show whether boxing adds anything once the
  helper is there. What it shows is that the contract is what lets
  the parent's helper be stated on ports at all. Part C is the
  half-contract trap: with only "empty iff g is 0" assumed, a boxed
  FIFO may raise `full` at any time, and P2 fails at depth 1.
- **M10.** The rows confirm both halves of the soundness rule:
  INV's own proof from reset (0.12 s) is the side condition that
  makes a proof from INV states a proof from reset; a weaker start
  set gives a counterexample from an unreachable state at depth 0.
  Part C needed rIC3 (34 s): starting from INV states does not
  make the property inductive, it only enlarges the initial set.
- **M11.** The middle row of part C is the point of the entry: a
  deep cover of time is covered, so a generic "the environment can
  run 50 cycles" check passes, while the assertion is proved only
  because every trace that could violate it is cut by the
  assumption. Only the witness cover of the assertion's own
  scenario is `unreachable`.


## 3. The catalog: sources, soundness, pitfalls, status

Marks, as in the notes for the two chapters before this one.
**[V-CR]**: authors, title, venue and pages checked against the
publisher's Crossref record (fetched through `api.crossref.org` on
2026-11-16; metadata only; where Crossref gives initials, the given
names are not verified). **[V-META]**: the same fields from another
bibliographic page (named), 2026-11-16. **[V-TEXT: what]**: the named
passage read in a copy of the document, as extracted text (a wording
below is a pointer, not a checked quotation). **[VENDOR]**: a vendor
product page or datasheet; what it says is the vendor's claim and is
labelled so. **[U]**: not verified in this session. **[CH18]**: verified
for the previous chapter (its note, section 2), not re-read here.

"Preserves" uses the plan's three words. *Proofs*: if the changed
problem is proved, the original is (the change over-approximates the
behaviors). *Counterexamples*: if the changed problem fails, the
original does (the change under-approximates). *Both*: the change is
exact for the property (a reformulation, not an abstraction).

Status words: **Measured** (a run exists, with its section), **By
hand** (runs, no command for it), **Not available** (InFormal has
no feature and the book shows a manual equivalent or prose).

### 3.1 Shrinking the problem

**T1. Black box.** Remove a module; its outputs become free inputs.
- Sources: Clarke, Grumberg, Long, "Model checking and abstraction",
  *ACM TOPLAS* 16(5):1512-1542, 1994, DOI 10.1145/186025.186051
  [V-CR] (the general result that a model whose behaviors include the
  concrete ones preserves universal properties; text not read).
  InFormal `docs/fpv-shell.md` (`elaborate -bbox_m`, `-bbox_i`) at
  `5114330` [CH18 for the document; FM C.6 for the run]. The tool's
  own note on every black-boxed run is the clearest primary
  statement of the soundness rule for the reader: "A proof holds for
  the design; a counterexample may use output values the boxed logic
  cannot produce" (printed by the shell, FM C.6; quote it from
  `run.out`).
- Soundness: freeing outputs adds behaviors (every value the box
  could produce is still possible), so a safety proof carries over;
  a counterexample may be spurious. Preserves proofs.
- Pitfalls: (1) a black-boxed module's outputs change every cycle,
  including values that violate the box's own protocol, so most
  counterexamples after boxing are spurious until the box's contract
  is assumed (measured: section 2, `hierarchical` part C and
  `memory-abstraction` part D); (2) a name inside a box is accepted
  by `assert` and fails only at `prove` (FM C.6); (3) boxing removes
  the box's assertions too: a property written inside the boxed RTL
  silently leaves the table [U: not measured; inferred from "contents
  not modelled"; measure before the chapter says it]; (4) covers get
  shallower (202 to 3, FM C.6): a covered cover under a box says
  nothing about the real design.
- InFormal: Measured (FM C.6; here `hierarchical`,
  `memory-abstraction`).

**T2. Cut point.** Free one internal signal (`stopat`).
- Sources: as T1; the shell document for `stopat`, `stopat -list`,
  `stopat -clear` [CH18]. Industrial practice: Seligman, Schubert,
  Kumar, *Formal Verification: An Essential Toolkit for Modern VLSI
  Design*, 2nd ed., Morgan Kaufmann, 2023, ISBN 9780323956123 [CH18:
  edition and ISBN checked, text not opened]; cite in further reading
  only.
- Soundness: identical to T1 for the cone behind the cut.
- Pitfalls: cutting a register (not a wire) frees it every cycle,
  which is stronger than freeing its initial value (that is T6);
  a cut on a signal that feeds the property's antecedent can make
  the property vacuous only if an assumption also restricts it
  (witness cover, T29).
- InFormal: Measured (FM C.6: `stopat u_timer.expired`, the tool's
  note names the cut points on every run).

**T3. Parameter reduction.** Prove at a small parameter, argue for
the large one.
- Sources: the theory of when this is sound is "cutoff" results for
  parameterized systems, not a general theorem: Emerson and Kahlon,
  "Reducing model checking of the many to the few", CADE 2000 [U: not
  looked up]. Wolper 1986 (T9) is a data-width cutoff of this kind.
  No hardware-specific primary source was read.
- Soundness: preserves neither by itself. A counterexample at the
  small size is usually real at the large one only if the large
  design contains the small one's behavior (it does not when, for
  example, a full flag depends on DEPTH). A proof transfers only
  with an argument (a cutoff theorem, data independence, or an
  induction on the parameter).
- Pitfalls: widths that change control (a counter one bit too
  narrow at DEPTH 16 is correct at DEPTH 4: the book's own Chapter 1
  bug is exactly a width bug); `$clog2` of a non-power of two.
- InFormal: Measured (`elaborate -parameter`, FM D.2; the previous
  chapter's scaling grid is the motive).

**T4. Counter abstraction.** Replace a long timer with a free
"expired" signal.
- Sources: in model checking, "counter abstraction" usually names
  the parameterized-systems technique of counting processes per
  local state: Pnueli, Xu, Zuck, "Liveness with (0,1,infinity)-
  counter abstraction", CAV 2002, LNCS, pp. 107-122, DOI
  10.1007/3-540-45657-0_9 [V-CR]. **The hardware usage (a timer
  abstracted by a cut point plus, optionally, a minimum-gap
  assumption) has no single primary source found**; it is cut point
  (T2) applied to a counter. The chapter should define its own term
  ("timer abstraction" or "counter abstraction in the hardware
  sense") and say the word means something else in the
  parameterized-systems literature.
- Soundness: a cut point; preserves proofs. Adding an assumption
  "expired at least N cycles after start" restores some real
  behavior but is then a claim to discharge on the real timer.
- Pitfalls: the cover depth drops (202 to 3, FM C.6), so bounded
  depth arguments made on the abstract model are about a different
  depth; a property that depends on the exact delay (`##[1:201]`)
  is not provable after the cut and needs the timer.
- InFormal: Measured (FM C.6).

**T5. Memory abstraction.** One symbolic location instead of the
array.
- Sources: Burch, Dill, "Automatic verification of pipelined
  microprocessor control", CAV 1994, LNCS, pp. 68-80, DOI
  10.1007/3-540-58179-0_44 [V-CR] (uninterpreted functions and
  memories as the classical origin; text not read); Bryant, German,
  Velev, "Processor verification using efficient reductions of the
  logic of uninterpreted functions to propositional logic", *ACM
  TOCL* 2(1):93-134, 2001, DOI 10.1145/371282.371364 [V-CR];
  Bjesse, "Word-level sequential memory abstraction for model
  checking", FMCAD 2008, pp. 1-9, DOI 10.1109/FMCAD.2008.ECP.20
  [V-META: isc.ac record] (the automatic version for model checking:
  only the slots a property can observe are kept). The one-address
  form taught here is symbolic constant (T8) plus black box (T1)
  plus a contract; no single source names exactly that recipe.
- Soundness: the box's outputs are free except at the symbolic
  address, where the contract pins them; behaviors of the real
  memory are a subset, so proofs carry over **provided the contract
  holds of the real memory** (it is an assumption to discharge,
  measured in `memory-abstraction` E). Because the address is a
  free constant, a proof for "the" symbolic address is a proof for
  every address.
- Pitfalls: (1) read-during-write semantics: the contract must say
  which word a same-cycle read returns (the measured design returns
  the old word from storage and forwards the new one; getting this
  wrong in the contract is a spurious counterexample or, worse, a
  false proof if the contract is stronger than the memory);
  (2) uninitialized memory: the shadow needs a valid bit, or the
  first read of an unwritten word fails; (3) the symbolic address
  must be held with `$stable` (no `$anyconst`, FM H), and a reset
  in the middle of a trace re-picks nothing: the free input is
  constant over the whole trace.
- InFormal: Measured here (section 2, M1): 256 words proved in
  0.02 s by k-induction under the abstraction against 9.3 s for
  rIC3 on the flat design, where k-induction gave no verdict in 20 s.

**T6. Initial-value abstraction.** Start from any state satisfying an
invariant, not from reset.
- Sources: no primary source read that names it. The standard
  justification is the induction rule of the previous chapter: if
  INV holds in every initial state and is inductive, every reachable
  state satisfies INV, so any property proved from all INV states is
  proved from reset. [U] for an origin; in industry this is often
  called "reset abstraction" or "starting from a symbolic state"
  (Seligman et al., not opened).
- Soundness: preserves proofs if (a) the reset states satisfy INV and
  (b) INV is inductive, both proved (measured: `initial-value` C
  proves INV from reset by k-induction). Counterexamples from INV
  states may be unreachable unless INV is exactly the reachable set:
  measured weak-INV spurious counterexample (D).
- Pitfalls: (1) the shell's `reset -none` frees every register,
  including ones the INV does not mention (pointer bits of a memory,
  ghost state), so the start set is larger than the writer pictures;
  (2) InFormal applies every assumption in every cycle; a start
  condition must be guarded by a first-cycle flag written as RTL
  (`initial first = 1'b1`), and the reset input becomes a free input
  that can fire mid-trace; (3) a deep bug found from an INV state is
  only a bug if the start state is reachable: confirm with a cover
  from reset or replay in simulation.
- InFormal: By hand (`reset -none` plus a guarded assumption):
  measured in M10.

**T7. Localization and refinement.** Let the tool free logic, then
restore what a spurious trace needs.
- Sources: Kurshan, *Computer-Aided Verification of Coordinating
  Processes: The Automata-Theoretic Approach*, Princeton University
  Press, 1994 (localization reduction) [U: not opened; title and
  year from memory, check before citing]; Clarke, Grumberg, Jha, Lu,
  Veith, "Counterexample-guided abstraction refinement", CAV 2000,
  LNCS, pp. 154-169, DOI 10.1007/10722167_15 [V-CR, re-checked
  2026-11-16]; McMillan, Amla, "Automatic abstraction without
  counterexamples", TACAS 2003, LNCS, pp. 2-17, DOI
  10.1007/3-540-36577-X_2 [V-CR] (proof-based abstraction: keep the
  logic a bounded refutation used).
- Soundness: each abstract model frees logic (preserves proofs); a
  counterexample is checked on the concrete design and either is
  real or names logic to restore. Both, at the end of the loop.
- Pitfalls: the manual loop converges only if the engineer restores
  the logic the trace actually used; restoring by guessing grows the
  model back to the original.
- InFormal: Not available (no automatic localization in the shell
  at `5114330`, its engine list); taught by doing it with cut points.

### 3.2 Symbolic reasoning

**T8. Symbolic constant.** One free, stable value stands for every
address, index or ID.
- Sources: the SVA construct is `$anyconst` (not in IEEE 1800; it is
  a formal-tool extension, documented by SymbiYosys/Yosys [U: page
  not re-read this session]); IEEE 1800-2023 has `checker` variables
  with `rand const` (clause 17.7 [U: clause number from memory]).
  The logic is universal generalization: a property proved for a
  free value proves it for each value.
- Soundness: exact (both), because the value is universally
  quantified by being free and constant over the trace.
- Pitfalls: InFormal rejects `$anyconst` and then drops every RTL
  property of the design silently (FM summary item 2): use a free
  input and `assume {$stable(x)}`; the `$stable` assumption is
  vacuous in the reset cycle (registers free in cycle 0, FM D.3) so
  the value may differ between cycle 0 and cycle 1 [U: not measured;
  the measured scripts never read the value in cycle 0].
- InFormal: Measured by hand (FM H; here M1, M2, M5).

**T9. Data independence.** Track one tagged word through a data path.
- Sources: Wolper, "Expressing interesting properties of programs in
  propositional temporal logic", POPL 1986, pp. 184-193, DOI
  10.1145/512644.512661 [V-CR] (data independence: if a program
  only moves data, properties about data can be checked over a small
  data domain; text not read in this session, the claim is the
  paper's well-known result [U for the exact statement]).
- Soundness: both, if the design never computes on the data (no
  comparison, arithmetic or branching on it); the tag chooser (a
  free `pick` input) makes the tracked word universally quantified.
- Pitfalls: a design that tests the data (parity, a match) breaks
  the argument; the "pick" input must be able to choose every push
  (an assumption on it that excludes pushes while full makes the
  check skip exactly the boundary).
- InFormal: Measured (FM H: proved by rIC3 only, 32 s, mutant at
  depth 3).

**T10. Two-word ordering check.** Two symbolic words prove order,
loss and duplication.
- Sources: Wolper 1986 (data independence with a small number of
  distinguished values) [V-CR metadata; U for the two-value
  statement]. The FIFO-specific "two tagged words" check is
  folklore of industrial formal; no primary source read.
- Soundness: both, under data independence; with d1 pushed before
  d2 the check "d2 never leaves before d1" plus "each leaves once"
  covers reordering and duplication; loss of the second word needs
  a liveness or bounded-response property.
- Pitfalls: the assumptions that restrict pushes of d1 and d2 to at
  most once are themselves the data-independence argument: forget
  "every other push carries another value" and a second d1 is a
  spurious duplication.
- InFormal: Measured here (M2), see the result: the hardest entry.

**T11. Free oracle input.** A free input chooses when or which.
- Sources: the oracle input is the device in Biere, Artho, Schuppan
  2002 (liveness to safety: an input chooses when to save the state)
  `biere2002liveness` [CH18]; FM H's `pick`.
- Soundness: both; the oracle is universally quantified.
- Pitfalls: an oracle that may fire more than once must be
  restricted (the `!in_q` guard in FM H), and the restriction must
  not exclude a case.
- InFormal: Measured (FM H).

**T12. Symmetry.** Prove for one channel, argue the rest identical.
- Sources: Emerson, Sistla, "Symmetry and model checking", *FMSD*
  9(1-2):105-131, 1996, DOI 10.1007/BF00625970 [V-CR]; Clarke,
  Enders, Filkorn, Jha, "Exploiting symmetry in temporal logic model
  checking", *FMSD* 9(1-2):77-104, 1996, DOI 10.1007/BF00625969
  [V-CR, initials only]; Ip, Dill, "Better verification through
  symmetry", *FMSD* 9(1-2):41-75, 1996, DOI 10.1007/BF00625968
  [V-META: scilit record].
- Soundness: proofs, if a permutation of the channels maps the
  transition relation and the initial states onto themselves and the
  property onto its image. The initial-state condition is the one a
  hardware engineer forgets.
- Pitfalls: the DMA is not symmetric: its round-robin pointer resets
  to the last channel (`r_last <= NCH - 1`), so the swap of channels
  0 and 1 does not map the reset state to itself; a fixed-priority
  arbiter is the extreme case (measured: port 0 proves, port 3
  fails, M3). With two channels the cheap answer is to prove both.
- InFormal: Measured here (M3).

### 3.3 Modeling code

**T13. Ghost state.** Counters and shadow registers that exist only
for the property.
- Sources: auxiliary variables, Owicki, Gries, "An axiomatic proof
  technique for parallel programs I", *Acta Informatica* 6(4):
  319-340, 1976, DOI 10.1007/BF00268134 [V-CR] (text not read: cite
  for the origin of auxiliary variables in proofs [U for the exact
  framing]).
- Soundness: both, provided the ghost logic only reads the design
  (never drives it). In SystemVerilog a bound module guarantees
  this by having only inputs.
- Pitfalls: the ghost is RTL and has its own reset; an asynchronous
  reset is modeled as synchronous (FM D.3); a ghost counter that
  wraps must be wide enough or saturate (measured: `history-prophecy`
  uses saturating counters).
- InFormal: Measured (FM A.2, bound module).

**T14. Reference model.** A small abstract model the design must
match.
- Sources: no separate primary source needed beyond T13 and
  refinement (Abadi, Lamport 1991, T16). Chapter 10 of the book owns
  reference models in simulation.
- Soundness: both, as for ghost state.
- Pitfalls: the model must be abstract (an occupancy count, not a
  second FIFO); a model written from the RTL repeats its bugs.
- InFormal: Measured (FM A.4).

**T15. Protocol checker as assumption and assertion.** One checker
constrains inputs on one side and checks outputs on the other.
- Sources: OVL (`accellera2014ovl`) and the vendor assertion IPs
  (VC Formal datasheet lists "AIP" for AMBA APB, AHB, AXI and CHI
  [VENDOR, 2022 datasheet, read 2026-11-16]); Gisselquist's AXI
  property files (`gisselquist2021axirules`) use one file with a
  parameter that swaps assume and assert [U: confirm in the file
  before the chapter says so]. The method is assume-guarantee (T18).
- Soundness: proofs, if the assumed side is discharged as an
  assertion on whatever drives that interface.
- Pitfalls: direction: an assumption on a signal the block drives is
  an over-constraint that reaches back through combinational paths
  into the inputs (measured, M4 part D: a false input property
  proved, and an input cover unreachable); disable iff and reset
  apply to both roles.
- InFormal: Measured here (M4), as assertions and as assumptions,
  with `if (ASSUME)` generate blocks inside a module, in a `bind`.

**T16. History and prophecy variables.** Record the past, or guess
the future and check the guess.
- Sources: Abadi, Lamport, "The existence of refinement mappings",
  *Theoretical Computer Science* 82(2):253-284, 1991, DOI
  10.1016/0304-3975(91)90224-P [V-CR] (history and prophecy
  variables are introduced to make refinement mappings exist; text
  not read in this session).
- Soundness: adding a history variable does not change the
  behaviors of the design (it is ghost state, both). A prophecy
  variable is a guess checked later: in Abadi and Lamport's setting
  the guess is constrained by the whole infinite behavior; **in a
  safety check of finite traces an assumption about the future does
  not remove a prefix that ends before the check**, so asserting on
  the guess before it is checked gives a spurious counterexample
  (measured M5 part D). A prophecy is usable in the shell only where
  the assertion reads it no earlier than the assumption checks it,
  and then it is equivalent to a history variable (M5 part E).
- Pitfalls: as above; SVA has no unbounded past operator, and
  bounded `$past(x, N)` chains are false alarms when the gap is
  unbounded (measured M5 part A).
- InFormal: Measured here (M5).

### 3.4 Decomposition

**T17. Helper invariant.** Prove a lemma, then assume it.
- Sources: the previous chapter (`@sec-ch18-helper`) with
  `sheeran2000checking`, `bradley2011sat`, `een2011pdr` [CH18].
- Soundness: proofs, provided the lemma is itself proved (in the
  same flow) and the reasoning is not circular in the same cycle
  (see T18).
- Pitfalls: a proved assertion is not reused automatically (FM A.4,
  CH18 P9): the lemma must be retyped as an assumption, and a typo
  in the copy is an unproved assumption; keep one Tcl variable for
  both (as `fifo-64` does).
- InFormal: Measured, by hand (FM C.3; here M1 part A, M7, M9).

**T18. Assume-guarantee.** Each block's assumptions are its
neighbor's assertions.
- Sources: Misra, Chandy, "Proofs of networks of processes", *IEEE
  TSE* SE-7(4):417-426, 1981, DOI 10.1109/TSE.1981.230844 [V-CR,
  initials only]; Abadi, Lamport, "Conjoining specifications", *ACM
  TOPLAS* 17(3):507-535, 1995, DOI 10.1145/203095.201069 [V-CR];
  McMillan, "Circular compositional reasoning about liveness",
  CHARME 1999, LNCS, pp. 342-346, DOI 10.1007/3-540-48153-2_30
  [V-CR, initials only].
- Soundness: for safety, mutual assumptions are sound when each
  guarantee at cycle t+1 depends on the other's assumption only up
  to cycle t (a register in every loop of the reasoning; induction
  on time). For liveness, circular reasoning is unsound in general
  (McMillan's paper gives conditions under which it is sound; text
  not read [U for the conditions]).
- Pitfalls: measured in M8: the safety ring proves and agrees with
  the flat proof; the liveness ring, each block proved under the
  other's "eventually", is false when composed (a lasso of all
  zeros). Same-cycle (combinational) circularity is the safety
  version of the trap [U: not measured, because the composition is
  a combinational loop the tool would reject or model oddly].
- InFormal: By hand (assumption by Tcl text), measured in M8.

**T19. Case split.** Prove under each of several assumptions that
together cover every case.
- Sources: McMillan, "Verification of infinite state systems by
  compositional model checking", CHARME 1999, LNCS, pp. 219-237, DOI
  10.1007/3-540-48153-2_17 [V-CR] (case splitting with symbolic
  values in the Cadence SMV system; text not read).
- Soundness: proofs, if every case is proved and the disjunction of
  the case conditions is proved to hold always (completeness). On a
  stable input the completeness is a tautology; on state it is an
  invariant to prove.
- Pitfalls: a forgotten case is a silent gap; measured (M6 part C):
  the bug lives in case 3, a list of three cases proves, and only
  the completeness assertion fails. Splitting does not always pay:
  measured on a multiplier miter (M6 B and D).
- InFormal: Measured here (M6), by hand.

**T20. Property decomposition.** Replace one end-to-end property with
a chain of local ones.
- Sources: McMillan 1999 (T19) and assume-guarantee (T18); no
  separate primary source read.
- Soundness: proofs, if the end-to-end property follows from the
  local ones (itself a check: here the end-to-end property is proved
  with the locals assumed) and each local one is proved.
- Pitfalls: local properties that are true but not inductive just
  move the difficulty; a chain that assumes its own conclusion.
- InFormal: Measured here on the DMA (M7).

**T21. Hierarchical proof.** Prove a block, then black-box it under
its proved contract.
- Sources: T1 and T18 combined; no separate primary source.
- Soundness: proofs, if the contract is proved on the block (under
  the block's own input assumptions, which become assertions on the
  parent).
- Pitfalls: the contract must be stated on ports and ghost state the
  parent can see (a contract naming the block's internal `count` is
  unusable once the block is boxed); a half contract gives spurious
  counterexamples (measured M9 part C).
- InFormal: Measured here (M9).

### 3.5 Constraining and bug hunting

**T22. Environment assumptions.** State what the inputs may legally
do. Owned by `@sec-ch18-assume` for the definition; this chapter adds
how to write them from a specification and how to discharge them
(T15, T18). Sources [CH18]. InFormal: Measured (FM C.5).

**T23. Over-constraint for hunting.** Restrict inputs to reach a deep
bug sooner. Preserves counterexamples only. Sources: [CH18]
(Seligman et al. for practice, not opened). Pitfall: the restricted
run's "proven" is meaningless; label every hunting script. InFormal:
Measured (FM C.5).

**T24. Bounded proof with a depth argument.** Justify "N cycles is
enough".
- Sources: Clarke, Kroening, Ouaknine, Strichman, "Completeness and
  complexity of bounded model checking", VMCAI 2004
  (`clarke2004completeness`) [CH18]; `biere1999symbolic` [CH18].
- Soundness: a bounded proof is a proof to depth N only; it equals a
  full proof when N reaches the completeness threshold (for a safety
  property, the diameter or recurrence diameter), which is rarely
  computable for real designs. The industrial argument (covers of
  the deepest behavior of interest reached within N) is evidence,
  not proof.
- Pitfalls: the shell prints no bound (FM C.1); `undetermined` after
  a time limit says nothing about depth.
- InFormal: Blocked (no bound in the shell). Taught in prose.

**T25. Cover-guided deep search.** Start the search from a covered
deep state.
- Sources: semi-formal search ("guided search", "state swarm") is a
  vendor feature; no peer-reviewed primary source read [U]. T6 is
  the sound cousin available here.
- Soundness: counterexamples only (the start state is reachable
  because it was covered from reset).
- InFormal: Not available. The book can approximate it with T6 plus
  a start condition copied from a cover trace [not measured].

**T26. Bounded liveness.** "Eventually" becomes "within N cycles".
Stronger than the original (a proof of the bounded form proves the
unbounded one; a counterexample to it may not be a liveness bug).
Sources: `biere2002liveness` [CH18]. InFormal: Measured (FM C.7:
`##[1:201]` proved in 0.72 s, `##[1:200]` refuted).

**T27. Fairness.** Owned by `@sec-ch18-liveness`. Sources [CH18].
InFormal: Measured (FM C.7). This chapter adds one thing measured
here: fairness in an assume-guarantee loop is circular (M8 C/D).

### 3.6 Trusting the result

**T28. Witness cover.** Every assertion ships with a cover of its
antecedent. Sources: `beer2001vacuity` [CH18]. Owned by
`@sec-ch18-cover`; this chapter makes it a rule for every entry.
InFormal: Measured; the tool does not flag vacuity.

**T29. Assumption sanity.** Prove the assumptions can be satisfied,
forever.
- Sources: no primary source read for the hardware practice. The
  exact condition ("every reachable state satisfying the assumptions
  has a successor satisfying them", a branching-time property, AG EX
  true) cannot be stated in SVA; covers can show only that some long
  trace exists. [U for any literature; Beer et al. 2001 is about
  vacuity of properties, not of assumptions.]
- Soundness: n/a (a check on the setup).
- Pitfalls, measured in M11: a dead end that every trace meets is
  caught by a deep cover of a free-running cycle count; a dead end
  that only some traces meet (one mode) leaves the deep cover
  covered and the false assertion proved; only the per-assertion
  witness cover catches it.
- InFormal: By hand, with covers (M11). No built-in check
  (contradictory assumptions pass silently, FM C.5).

**T30. Mutation of the design.** Plant a bug; some property must
fail.
- Sources: DeMillo, Lipton, Sayward 1978 (`demillo1978mutation`) for
  mutation; Chockler, Kupferman, Kurshan, Vardi, "A practical
  approach to coverage in model checking", CAV 2001 [V-TEXT:
  abstract and section 1 in the author-hosted PDF
  www.cs.huji.ac.il/~ornak/publications/cav01.pdf, 2026-11-16: a
  state is covered if flipping an observable signal there makes the
  specification fail]; Hoskote, Kam, Ho, Zhao, "Coverage estimation
  for symbolic model checking", DAC 1999, pp. 300-305, DOI
  10.1145/309847.309936 [V-CR]; Chockler, Kupferman, Vardi,
  "Coverage metrics for formal verification", *STTT* 2006 (journal
  version of CHARME 2003) [U: volume and pages not opened]. Vendor:
  VC Formal "FTA" uses Certitude to find missing properties or
  constraints [VENDOR, datasheet 2022]; `hampton2007certitude`
  exists in refs.bib.
- Soundness: n/a. A surviving mutant shows a gap in the property set
  (or an equivalent mutant).
- InFormal: Measured (FM B.1 two DMA mutants; FM H FIFO mutant; here
  every measurement carries a mutant).

**T31. Cone-of-influence and proof-core coverage.** Which logic the
proofs depended on.
- Sources: McMillan, Amla 2003 (T7) for proof-based abstraction (the
  logic used by a refutation); Ghassabani, Gacek, Whalen, "Efficient
  generation of inductive validity cores for safety properties", FSE
  2016, pp. 314-325, DOI 10.1145/2950290.2950346 [V-CR]; vendor:
  Jasper COV app "Proof Core technology, which measure[s] checker
  coverage" [VENDOR: newstaging.cadence.com COV app page, read
  2026-11-16; the main host was not tried].
- Soundness: n/a. COI coverage over-reports (logic in the cone that
  the proof did not need); proof-core coverage is tighter.
- InFormal: Not available; described only.

## 4. The six recipes

Each recipe is a page at the end of the chapter built from entries
above. None of the six was measured in this session (the plan asks
for one short recipe each, not a measurement); the "InFormal" line
says what the tool allows. Vendor apps exist for five of the six;
their pages are cited only for what each says the app checks, as the
vendor's statement.

**R1. Connectivity.** Prove that a signal at one block's port reaches
another block's port, possibly under a condition or after a pipeline
delay. Built from T1 (box every IP, keep only the wiring), T22 (mode
inputs as assumptions) and one assertion per row of a connection
table (`en |-> dst == src`, or `|-> ##N` for a pipelined path).
- Vendor statements: Jasper CONN app: "exhaustively verify the
  static, structural, temporal, and conditional connectivity of IP
  blocks inside a system on chip"; the specification "captured in a
  comma-separated-values (CSV) file or an IP-XACT XML file"
  [VENDOR: newstaging.cadence.com CONN app page, Japanese edition,
  read 2026-11-16]. VC Formal CC: "SoC-level connectivity" with
  root-cause analysis [VENDOR: VC Formal datasheet, dated 08/10/22,
  read 2026-11-16].
- Standard for the table: IEEE 1685 (IP-XACT) [U: edition 2022 not
  opened; cite at title level only after checking].
- Soundness: proofs survive the boxes (T1); a counterexample through
  a box is spurious and names the box to open.
- InFormal: possible today (`-bbox_m`, Tcl loop over a CSV that
  emits one `assert` per row). A natural running example: the DMA's
  `IRQ` path from `irq_en`, `done`, `err` (a registered OR).

**R2. Register access.** Every register reads back what was written,
honors its access type and reset value.
- Built from T8 (symbolic address and data), T13 (a ghost copy per
  symbolic register) and T15 (the bus protocol as assumptions). For
  the DMA: write `SRC_ADDR` of channel c with a symbolic value v,
  read it back with no write between: `PRDATA == {v[31:2], 2'b00}`
  (the two low bits are dropped by design, a fact the register YAML
  states).
- Vendor statements: Jasper CSR app checks "aliased registers,
  masking", "simultaneous access from hardware and software", lock
  conditions and read side effects, from "comma-separated values
  (CSV) or IP-XACT XML files" [VENDOR: newstaging.cadence.com CSR
  page, Korean edition, read 2026-11-16]; VC Formal FRV verifies
  "register attributes and behaviors, such as read-only or reset
  value" [VENDOR: datasheet 2022].
- Soundness: both (symbolic constants are exact).
- InFormal: possible today; the DMA's generated register package is
  the specification (Chapter 11's YAML).

**R3. X-propagation.** Can an unknown value (an uninitialized
register, an undriven input) reach an output or a control point?
- InFormal is two-valued: `$isunknown` is rejected unless
  `allow_four_state_ops` (FM D.1), and the shell has no X mode.
  Recipe without four-state logic: self-composition (R5) with the X
  sources free and independent in two copies and every other input
  shared; an output that differs between the copies is an output an
  X can reach. This is the standard two-valued encoding of "X as any
  value" [U: no primary source read for this encoding; Turpin 2003
  `turpin2003x` and Sutherland 2013 `sutherland2013x` are in
  refs.bib for X semantics in simulation].
- Vendor statement: Jasper XPROP app checks that clocks and resets
  are "free of Xs", where X values travel in control and data logic,
  and whether they escape at outputs [VENDOR: newstaging.cadence.com
  XPROP page, Japanese edition, read 2026-11-16]; VC Formal FXP
  "checks for unknown (X) value propagation" [VENDOR].
- Soundness: a self-composition difference is a real X escape under
  the "X is any value" reading; it is pessimistic against silicon,
  where an X is one value in both copies only if it is the same
  physical register (both copies' free values model two different
  silicon outcomes, which is the point).
- InFormal: possible by hand (two instances, free initial values via
  `reset -none` or no-reset registers, which the shell leaves free,
  FM D.3).

**R4. Unreachable-coverage analysis.** Prove that a coverage point
that simulation never hit can never be hit, so it can be excluded.
- Built from covers (`@sec-ch18-cover`): a cover is checked as the
  negation of an assertion, so `unreachable` is an unbounded proof
  (FM C.4).
- Vendor statement: VC Formal FCA proves that uncovered points are
  "indeed unreachable" so they can be removed from analysis
  [VENDOR: datasheet 2022]; Jasper lists a separate "Coverage
  Unreachability App" [VENDOR: COV page].
- Soundness: unreachable **under the assumptions in force**. An
  over-constraint makes points unreachable that simulation can hit;
  an exclusion from a formal run with assumptions is an exclusion
  only for environments that satisfy them. Chapter 8 (closure as a
  reviewed process, exclusions) and Chapter 9 are the places to
  point back to.
- InFormal: possible today; the point must be restated as a cover
  (the tool does not read coverage databases).

**R5. Information flow by self-composition.** A secret input must
not influence a public output.
- Sources: Barthe, D'Argenio, Rezk, "Secure information flow by
  self-composition", CSFW 2004, pp. 100-114 [V-META: researchr
  record; DOI not given there, not found in Crossref by the guessed
  DOI, which belongs to another paper]; Terauchi, Aiken, "Secure
  information flow as a safety problem", SAS 2005, LNCS,
  pp. 352-367, DOI 10.1007/11547662_24 [V-CR]; Clarkson, Schneider,
  "Hyperproperties", *Journal of Computer Security* 18(6):1157-1210,
  2010, DOI 10.3233/JCS-2009-0393 [V-CR] (non-interference is a
  property of pairs of traces, not of one trace). Hardware: Tiwari,
  Wassel, Mazloom, Mysore, Chong, Sherwood, "Complete information
  flow tracking from the gates up", ASPLOS 2009, pp. 109-120, DOI
  10.1145/1508244.1508258 [V-META: bibtex.github.io record] (gate-
  level tracking, the alternative to self-composition). Vendor:
  Jasper SPV (security path) [VENDOR, page listed, not read]; VC
  Formal FSV "secure data does not reach non-secure destinations"
  [VENDOR: datasheet].
- Recipe: two instances of the design, public inputs tied together,
  secret inputs free and independent, same reset; assert the public
  outputs equal in every cycle. Terauchi and Aiken's point is that
  this pair property is a safety property of the product, so the
  ordinary engines apply.
- Soundness: exact for non-interference of the modeled design
  (both). Timing channels in cycles are included because the check
  is cycle by cycle; physical channels are not.
- Pitfalls: the two copies must start from the same reset state; a
  copy with free registers differs at once (that is R3, not R5);
  declassification (a secret allowed out after a check) needs an
  assumption that the declassified values are equal.
- InFormal: possible by hand (two instances in a wrapper). Candidate
  running example: the DMA's PRDATA must not depend on the other
  channel's registers when reading one channel's status.

**R6. Clock-gating equivalence.** A design with clock gating inserted
behaves like the design without it.
- Sources: van Eijk, "Sequential equivalence checking based on
  structural similarities", *IEEE TCAD* 19(7):814-819, 2000, DOI
  10.1109/43.851997 [V-CR, initials only]; sequential equivalence as
  a safety property of a product machine (a miter), which the
  previous chapter can carry by label. Vendor: Jasper SEC lists
  "confirming that dynamic power optimizations (such as clock
  gating) were inserted correctly" [VENDOR: newstaging.cadence.com
  SEC page, read 2026-11-16]; VC Formal SEQ covers changes "such as
  retiming or clock gating" [VENDOR: datasheet].
- Recipe: both versions in one wrapper, inputs shared, same reset,
  assert outputs equal. The gated version's enable logic must be
  modeled at cycle level: InFormal has one clock model per declared
  clock and models `clk & en` either as a second clock or not at all
  [U: not measured]. The safe form for the book is a gated register
  written as an enable (`if (en) q <= d`) against the original; a
  latch-based integrated clock gate is a cell the formal model
  treats as behavior, so glitch freedom is a separate (structural)
  check.
- InFormal: no equivalence command (FM C.8); a hand-built miter only.
  Belongs with the equivalence chapter; here one page that points
  forward.

## 5. Proposed worked-example spine

Goal: the chapter is a catalog, but a reader should meet three
designs, not thirty-one. Each family is carried by the design on
which its entries are least artificial, and every design is one the
book has already explained, so no entry spends words on a new
circuit. Measured support for each assignment is in section 2.

**Design 1: the book's FIFO** (`examples/ch09-temporal-properties/
rtl/fifo_fixed.sv`, unchanged; the previous chapter's pointer
property, helper and scaling grid are the hand-over). Carries:
- *Shrinking*: memory abstraction (T5) on its storage is the
  natural step from the previous chapter's "at 256 entries nothing
  finishes"; parameter reduction (T3) with its width trap (the
  Chapter 1 bug is a width bug); initial-value abstraction (T6)
  with the previous chapter's helper as INV (M10: a bug 256 pushes
  deep from reset is 2 cycles deep from INV states).
- *Symbolic reasoning*: symbolic constant (T8), data independence
  (T9, FM H), two-word ordering (T10, M2), free oracle (T11).
- *Modeling code*: ghost occupancy (T13), reference model (T14),
  history variable and the prophecy trap (T16, M5 C to E: the k-th
  word out against the k-th word in).
- *Decomposition*: helper invariant (T17, by label to
  `@sec-ch18-helper`), hierarchical proof (T21, M9: two FIFOs in
  series, each boxed under its proved contract).
- *Trusting*: mutation (T30) with the three FIFO mutants this note
  generated (`fifo_dup.sv`, `fifo_wrap.sv`, the read-pointer mutant
  of FM H).

**Design 2: a valid/ready handshake** (Chapter 9's `hs_check.sv`
rules and FM's `tech/handshake.sv` request/busy/grant block with its
200-cycle timer). Carries:
- *Shrinking*: black box, cut point and counter abstraction on the
  timer (T1, T2, T4: FM C.6's 202-to-3 cover).
- *Modeling code*: the protocol checker used both ways (T15, M4 A to
  D; the measurement used its own `vr_rules`, but Chapter 9's
  `hs_check` has the same rules and should be the one the chapter
  splices, given an `ASSUME` parameter in a new example file, not an
  edit of Chapter 9's).
- *Decomposition*: assume-guarantee (T18, M8: the two-block ring,
  safety sound, liveness circular), case split is better on design 3
  or a datapath (see below).
- *Constraining*: environment assumptions, over-constraint, bounded
  liveness and fairness (T22, T23, T26, T27; all FM C.5 and C.7,
  already on this design).
- *Trusting*: witness cover and assumption sanity (T28, T29, M11).
  M11's design is a separate eight-line counter; it could be folded
  into the handshake by making the dead-end assumption on the
  requester's mode.

**Design 3: the DMA, version 2** (Chapter 11, unchanged). Carries the
"real block" end of each family, where the reader sees a technique
pay off or cost on a design with 647 state bits:
- *Symmetry* (T12, M3): two channels, the reset asymmetry of the
  round-robin pointer, and the four-port arbiter extracted from the
  read engine as the clean demonstration.
- *Protocol checker* (T15, M4 E): AXI rules asserted on the three
  channels it drives, assumed on the two it receives.
- *Property decomposition* (T20, M7): "a channel that finishes
  without error has had as many write responses as its length",
  proved as two local lemmas.
- *Recipes*: connectivity (R1: the IRQ path), register access (R2:
  the generated register map), information flow (R5: one channel's
  status read does not depend on the other channel's registers),
  unreachable coverage (R4: Chapter 11's coverage holes, if any
  remain, restated as covers).

**Outside the spine, by necessity:** the case split (T19, M6) was
measured on a multiplier miter because a case split pays only where
the cases shrink a hard solver problem, and the three designs have
no such datapath; the outline should decide whether to keep the
miter (it also previews the equivalence chapter) or to state case
split in prose on the DMA (split on which channel is active). The
four-port arbiter (M3) is extracted from the DMA's own read engine,
so it stays "the DMA's arbiter" in the text.

Order suggestion: the families in the plan's order, but each family
opens on the FIFO or the handshake (small, every state explainable)
and closes on the DMA (the cost on a real block). The FIFO carries
the most entries (about 14), the handshake about 10, the DMA about 7
plus three recipes.

## 6. Bibliography (BibTeX-ready)

Keys already in `refs.bib` and reused by this chapter (no new entry):
`informal-tool`, `biere1999symbolic`, `sheeran2000checking`,
`bradley2011sat`, `een2011pdr`, `biere2002liveness`,
`clarke2004completeness`, `beer2001vacuity`, `demillo1978mutation`,
`hampton2007certitude`, `accellera2014ovl`, `gisselquist2021axirules`,
`turpin2003x`, `sutherland2013x`, `ieee1800-2023`,
`cadence-jasper-fpv`, `synopsys-vcformal`, `clarke1981modelchecking`.

New entries. Fields are those Crossref (or the named page) returned
on 2026-11-16; where Crossref gives initials only, the given names
below are as the record gives them and must be checked in the paper
before print (AGENTS.md: the whole author field against the
document). DOI entries carry no URL or access date, by the house
rule. Proceedings volume numbers of LNCS were not in the Crossref
records fetched and are left out rather than given from memory.

```bibtex
@article{clarke1994abstraction,
  author  = {Edmund M. Clarke and Orna Grumberg and David E. Long},
  title   = {Model Checking and Abstraction},
  journal = {ACM Transactions on Programming Languages and Systems},
  volume  = {16},
  number  = {5},
  pages   = {1512--1542},
  year    = {1994},
  doi     = {10.1145/186025.186051}
}

@inproceedings{clarke2000cegar,
  author    = {Edmund Clarke and Orna Grumberg and Somesh Jha and
               Yuan Lu and Helmut Veith},
  title     = {Counterexample-Guided Abstraction Refinement},
  booktitle = {Computer Aided Verification (CAV 2000)},
  series    = {Lecture Notes in Computer Science},
  publisher = {Springer},
  pages     = {154--169},
  year      = {2000},
  doi       = {10.1007/10722167_15}
}

@inproceedings{mcmillan2003abstraction,
  author    = {Kenneth L. McMillan and Nina Amla},
  title     = {Automatic Abstraction without Counterexamples},
  booktitle = {Tools and Algorithms for the Construction and Analysis
               of Systems (TACAS 2003)},
  series    = {Lecture Notes in Computer Science},
  publisher = {Springer},
  pages     = {2--17},
  year      = {2003},
  doi       = {10.1007/3-540-36577-X_2}
}

@inproceedings{pnueli2002counter,
  author    = {Amir Pnueli and Jessie Xu and Lenore Zuck},
  title     = {Liveness with $(0,1,\infty)$-Counter Abstraction},
  booktitle = {Computer Aided Verification (CAV 2002)},
  series    = {Lecture Notes in Computer Science},
  publisher = {Springer},
  pages     = {107--122},
  year      = {2002},
  doi       = {10.1007/3-540-45657-0_9}
}

@inproceedings{burch1994pipelined,
  author    = {Jerry R. Burch and David L. Dill},
  title     = {Automatic Verification of Pipelined Microprocessor
               Control},
  booktitle = {Computer Aided Verification (CAV '94)},
  series    = {Lecture Notes in Computer Science},
  publisher = {Springer},
  pages     = {68--80},
  year      = {1994},
  doi       = {10.1007/3-540-58179-0_44},
  note      = {Read 2026-11-16 in the authors' extended version (with
               an appendix the conference version lacks), hosted at
               cs.uwaterloo.ca; cite claims present in both}
}

@article{bryant2001positive,
  author  = {Randal E. Bryant and Steven German and Miroslav N. Velev},
  title   = {Processor Verification Using Efficient Reductions of the
             Logic of Uninterpreted Functions to Propositional Logic},
  journal = {ACM Transactions on Computational Logic},
  volume  = {2},
  number  = {1},
  pages   = {93--134},
  year    = {2001},
  doi     = {10.1145/371282.371364}
}

@inproceedings{bjesse2008memory,
  author    = {Per Bjesse},
  title     = {Word-Level Sequential Memory Abstraction for Model
               Checking},
  booktitle = {Formal Methods in Computer-Aided Design (FMCAD 2008)},
  publisher = {IEEE},
  pages     = {1--9},
  year      = {2008},
  doi       = {10.1109/FMCAD.2008.ECP.20},
  note      = {Metadata from a library record; check against IEEE
               Xplore before print}
}

@inproceedings{wolper1986expressing,
  author    = {Pierre Wolper},
  title     = {Expressing Interesting Properties of Programs in
               Propositional Temporal Logic},
  booktitle = {Proceedings of the 13th ACM SIGACT-SIGPLAN Symposium on
               Principles of Programming Languages (POPL '86)},
  publisher = {ACM},
  pages     = {184--193},
  year      = {1986},
  doi       = {10.1145/512644.512661}
}

@article{emerson1996symmetry,
  author  = {E. Allen Emerson and A. Prasad Sistla},
  title   = {Symmetry and Model Checking},
  journal = {Formal Methods in System Design},
  volume  = {9},
  number  = {1--2},
  pages   = {105--131},
  year    = {1996},
  doi     = {10.1007/BF00625970}
}

@article{clarke1996symmetry,
  author  = {E. M. Clarke and R. Enders and T. Filkorn and S. Jha},
  title   = {Exploiting Symmetry in Temporal Logic Model Checking},
  journal = {Formal Methods in System Design},
  volume  = {9},
  number  = {1--2},
  pages   = {77--104},
  year    = {1996},
  doi     = {10.1007/BF00625969},
  note    = {Crossref gives initials only; given names to be checked}
}

@article{ip1996symmetry,
  author  = {C. Norris Ip and David L. Dill},
  title   = {Better Verification Through Symmetry},
  journal = {Formal Methods in System Design},
  volume  = {9},
  number  = {1--2},
  pages   = {41--75},
  year    = {1996},
  doi     = {10.1007/BF00625968},
  note    = {Metadata from the scilit record; Crossref not fetched}
}

@article{owicki1976axiomatic,
  author  = {Susan Owicki and David Gries},
  title   = {An Axiomatic Proof Technique for Parallel Programs {I}},
  journal = {Acta Informatica},
  volume  = {6},
  number  = {4},
  pages   = {319--340},
  year    = {1976},
  doi     = {10.1007/BF00268134}
}

@article{abadi1991refinement,
  author  = {Mart{\'\i}n Abadi and Leslie Lamport},
  title   = {The Existence of Refinement Mappings},
  journal = {Theoretical Computer Science},
  volume  = {82},
  number  = {2},
  pages   = {253--284},
  year    = {1991},
  doi     = {10.1016/0304-3975(91)90224-P},
  note    = {Read 2026-11-16 in the report version, DEC SRC Research
             Report 29 (1988), sections 1 and 5; the journal text was
             not opened}
}

@article{misra1981proofs,
  author  = {J. Misra and K. M. Chandy},
  title   = {Proofs of Networks of Processes},
  journal = {IEEE Transactions on Software Engineering},
  volume  = {SE-7},
  number  = {4},
  pages   = {417--426},
  year    = {1981},
  doi     = {10.1109/TSE.1981.230844},
  note    = {Crossref gives initials only (Jayadev Misra, K. Mani
             Chandy are to be checked in the paper)}
}

@article{abadi1995conjoining,
  author  = {Mart{\'\i}n Abadi and Leslie Lamport},
  title   = {Conjoining Specifications},
  journal = {ACM Transactions on Programming Languages and Systems},
  volume  = {17},
  number  = {3},
  pages   = {507--535},
  year    = {1995},
  doi     = {10.1145/203095.201069},
  note    = {Read 2026-11-16 in the author-hosted copy, sections 1, 2.2
             and 5; that copy's header prints pp. 507--533, Crossref
             gives 507--535 (kept)}
}

@inproceedings{mcmillan1999circular,
  author    = {K. L. McMillan},
  title     = {Circular Compositional Reasoning about Liveness},
  booktitle = {Correct Hardware Design and Verification Methods
               (CHARME '99)},
  series    = {Lecture Notes in Computer Science},
  publisher = {Springer},
  volume    = {1703},
  pages     = {342--346},
  year      = {1999},
  doi       = {10.1007/3-540-48153-2_30},
  note      = {Text read 2026-11-16 (publisher PDF): the paper prints
               the author as K. L. McMillan; volume 1703 as printed}
}

@inproceedings{mcmillan1999compositional,
  author    = {K. L. McMillan},
  title     = {Verification of Infinite State Systems by Compositional
               Model Checking},
  booktitle = {Correct Hardware Design and Verification Methods
               (CHARME '99)},
  series    = {Lecture Notes in Computer Science},
  publisher = {Springer},
  volume    = {1703},
  pages     = {219--237},
  year      = {1999},
  doi       = {10.1007/3-540-48153-2_17},
  note      = {Text read 2026-11-16 (publisher PDF): author printed as
               K.L. McMillan; volume 1703 as printed}
}

@inproceedings{hoskote1999coverage,
  author    = {Yatin Hoskote and Timothy Kam and Pei-Hsin Ho and
               Xudong Zhao},
  title     = {Coverage Estimation for Symbolic Model Checking},
  booktitle = {Proceedings of the 36th Design Automation Conference
               (DAC '99)},
  publisher = {ACM},
  pages     = {300--305},
  year      = {1999},
  doi       = {10.1145/309847.309936}
}

@inproceedings{chockler2001practical,
  author    = {Hana Chockler and Orna Kupferman and Robert P. Kurshan
               and Moshe Y. Vardi},
  title     = {A Practical Approach to Coverage in Model Checking},
  booktitle = {Computer Aided Verification (CAV 2001)},
  series    = {Lecture Notes in Computer Science},
  publisher = {Springer},
  year      = {2001},
  url       = {https://www.cs.huji.ac.il/~ornak/publications/cav01.pdf},
  urldate   = {2026-11-16},
  note      = {Read in the author-hosted copy; pages and DOI not
               checked}
}

@inproceedings{ghassabani2016ivc,
  author    = {Elaheh Ghassabani and Andrew Gacek and Michael W.
               Whalen},
  title     = {Efficient Generation of Inductive Validity Cores for
               Safety Properties},
  booktitle = {Proceedings of the 24th ACM SIGSOFT International
               Symposium on Foundations of Software Engineering
               (FSE 2016)},
  publisher = {ACM},
  pages     = {314--325},
  year      = {2016},
  doi       = {10.1145/2950290.2950346}
}

@inproceedings{barthe2004selfcomposition,
  author    = {Gilles Barthe and Pedro R. D'Argenio and Tamara Rezk},
  title     = {Secure Information Flow by Self-Composition},
  booktitle = {17th IEEE Computer Security Foundations Workshop
               (CSFW-17)},
  publisher = {IEEE Computer Society},
  pages     = {100--114},
  year      = {2004},
  url       = {https://researchr.org/publication/BartheDR04},
  urldate   = {2026-11-16},
  note      = {Metadata from the researchr record; DOI not found}
}

@inproceedings{terauchi2005safety,
  author    = {Tachio Terauchi and Alex Aiken},
  title     = {Secure Information Flow as a Safety Problem},
  booktitle = {Static Analysis (SAS 2005)},
  series    = {Lecture Notes in Computer Science},
  publisher = {Springer},
  pages     = {352--367},
  year      = {2005},
  doi       = {10.1007/11547662_24}
}

@article{clarkson2010hyperproperties,
  author  = {Michael R. Clarkson and Fred B. Schneider},
  title   = {Hyperproperties},
  journal = {Journal of Computer Security},
  volume  = {18},
  number  = {6},
  pages   = {1157--1210},
  year    = {2010},
  doi     = {10.3233/JCS-2009-0393}
}

@inproceedings{tiwari2009glift,
  author    = {Mohit Tiwari and Hassan M. G. Wassel and Bita Mazloom
               and Shashidhar Mysore and Frederic T. Chong and
               Timothy Sherwood},
  title     = {Complete Information Flow Tracking from the Gates Up},
  booktitle = {Proceedings of the 14th International Conference on
               Architectural Support for Programming Languages and
               Operating Systems (ASPLOS 2009)},
  publisher = {ACM},
  pages     = {109--120},
  year      = {2009},
  doi       = {10.1145/1508244.1508258}
}

@article{vaneijk2000sec,
  author  = {C. A. J. {van Eijk}},
  title   = {Sequential Equivalence Checking Based on Structural
             Similarities},
  journal = {IEEE Transactions on Computer-Aided Design of Integrated
             Circuits and Systems},
  volume  = {19},
  number  = {7},
  pages   = {814--819},
  year    = {2000},
  doi     = {10.1109/43.851997}
}

@book{seligman2023formal,
  author    = {Erik Seligman and Tom Schubert and M. V. Achutha Kiran
               Kumar},
  title     = {Formal Verification: An Essential Toolkit for Modern
               {VLSI} Design},
  edition   = {2},
  publisher = {Morgan Kaufmann},
  year      = {2023},
  isbn      = {9780323956123},
  note      = {Edition and ISBN from Crossref chapter records; text
               not opened. Further reading only}
}

@misc{synopsys-vcformal-datasheet,
  author  = {{Synopsys}},
  title   = {{VC Formal} Datasheet},
  year    = {2022},
  url     = {https://www.synopsys.com/content/dam/synopsys/verification/datasheets/vc-formal-datasheet.pdf},
  urldate = {2026-11-16},
  note    = {Vendor datasheet dated 08/10/22. Lists the FPV, DPV,
             AEP, FCA, CC, SEQ, FRV, FXP, FTA, FSV, RMA, AIP and FuSa
             apps; every statement from it is a vendor claim}
}

@misc{cadence-jasper-conn,
  author  = {{Cadence Design Systems}},
  title   = {Jasper {CONN} App},
  year    = {2026},
  url     = {https://www.cadence.com/en_US/home/tools/system-design-and-verification/formal-and-static-verification/jasper-verification-platform/connectivity-verification-app.html},
  note    = {Vendor product page. Read on 2026-11-16 on the vendor's
             host newstaging.cadence.com (Japanese edition)}
}

@misc{cadence-jasper-csr,
  author  = {{Cadence Design Systems}},
  title   = {Jasper {CSR} App},
  year    = {2026},
  url     = {https://www.cadence.com/en_US/home/tools/system-design-and-verification/formal-and-static-verification/jasper-gold-verification-platform/jaspergold-control-and-status-register-app.html},
  note    = {Vendor product page. Read on 2026-11-16 on
             newstaging.cadence.com (Korean edition); the en_US path
             is assumed by analogy with the other pages [check]}
}

@misc{cadence-jasper-xprop,
  author  = {{Cadence Design Systems}},
  title   = {Jasper {XPROP} App},
  year    = {2026},
  url     = {https://www.cadence.com/en_US/home/tools/system-design-and-verification/formal-and-static-verification/jasper-gold-verification-platform/jaspergold-x-propagation-verification-app.html},
  note    = {Vendor product page. Read on 2026-11-16 on
             newstaging.cadence.com (Japanese edition) [check en_US]}
}

@misc{cadence-jasper-sec,
  author  = {{Cadence Design Systems}},
  title   = {Jasper {SEC} App},
  year    = {2026},
  url     = {https://www.cadence.com/en_US/home/tools/system-design-and-verification/formal-and-static-verification/jasper-gold-verification-platform/jaspergold-sequential-equivalence-checking-app.html},
  note    = {Vendor product page. Read on 2026-11-16 at the same path
             on newstaging.cadence.com}
}

@misc{cadence-jasper-cov,
  author  = {{Cadence Design Systems}},
  title   = {Jasper {COV} App},
  year    = {2026},
  url     = {https://www.cadence.com/en_US/home/tools/system-design-and-verification/formal-and-static-verification/jasper-gold-verification-platform/jaspergold-design-coverage-verification-app.html},
  note    = {Vendor product page. Read on 2026-11-16 on
             newstaging.cadence.com (Korean edition) [check en_US]}
}
```

```bibtex
@techreport{emerson2000cutoff,
  author      = {E. Allen Emerson and Vineet Kahlon},
  title       = {Reducing Model Checking of the Many to the Few},
  institution = {Department of Computer Sciences, University of Texas
                 at Austin},
  number      = {TR-00-03},
  year        = {2000},
  url         = {https://www.cs.utexas.edu/ftp/techreports/tr00-03.pdf},
  urldate     = {2026-11-16},
  note        = {Report dated 2000-01-31, read 2026-11-16 (abstract,
                 section 1). The CADE 2000 version's volume and pages
                 were not checked; cite the report}
}
```

Corrections made on 2026-11-16 while outlining (research/ch19-outline.md,
section 8): the two McMillan 1999 entries gained the LNCS volume
printed on the papers; Abadi and Lamport 1991 and 1995 and Burch and
Dill gained notes on which copy was read; Emerson and Kahlon gained
an entry (read). No author name or URL in the entries above was found
wrong against a document opened. One claim in section 3 was found
wrong against its source: T15 attributes to `gisselquist2021axirules`
"one file with a parameter that swaps assume and assert"; that key is
a blog post on the handshake rules, and the ZipCPU property file
`bench/formal/faxil_slave.v` hard-codes `SLAVE_ASSUME` as `assume` and
`SLAVE_ASSERT` as `assert` with no switch (read 2026-11-16). The
one-module-with-a-role-parameter source is `opentitan-tlul-assert`,
already cited by Chapter 9.

Not given an entry because not opened: Kurshan 1994 (localization
reduction), Emerson and Kahlon 2000 (cutoffs), IEEE 1685 (IP-XACT),
the STTT version of Chockler, Kupferman and Vardi, Jones's
rely-guarantee papers. Each is named in section 7.

## 7. Confidence notes

What could not be verified, in one list. A sentence of the chapter
that needs one of these waits until it is read, or is cut.

1. **No paper text was read for this chapter except one**: the CAV
   2001 coverage paper (Chockler, Kupferman, Kurshan, Vardi), whose
   abstract and opening were read in the author-hosted copy. Every
   other source in section 3 was checked at the metadata level only
   (Crossref, or a named library page). The one-line descriptions of
   what each paper contributes (Wolper's data independence, Burch
   and Dill's uninterpreted memories, Abadi and Lamport's history
   and prophecy variables, McMillan's circular reasoning and case
   splitting, Emerson and Sistla's symmetry) are the standard
   attributions but were not checked against the text in this
   session. **No quotation from any paper**; read the passage before
   any sentence says what a paper states.
2. **Given names from initials.** Crossref gave initials only for
   McMillan (both 1999 papers), Misra and Chandy, Clarke, Enders,
   Filkorn and Jha, van Eijk, and Ip (first name). Check in the
   papers.
3. **Not opened at all**: Kurshan 1994 (localization reduction; title
   and year from memory); Emerson and Kahlon 2000 (cutoffs); IEEE
   1685 (IP-XACT) edition and clause; the STTT 2006 coverage paper;
   Jones's rely-guarantee papers (1981 thesis, 1983 paper); Seligman,
   Schubert and Kumar (edition and ISBN checked for the previous
   chapter, text not opened); any SymbiYosys or Yosys page on
   `$anyconst` (T8 says it is a tool extension, not in IEEE 1800:
   check the 2023 standard's index before printing that);
   the IEEE 1800-2023 clause on checker `rand const` variables
   (number from memory).
4. **Barthe, D'Argenio, Rezk 2004** has no DOI in the record found;
   the guessed DOI resolved to a different paper (Backes and
   Pfitzmann, same workshop). Use the researchr metadata or find the
   IEEE Xplore record.
5. **Vendor pages** were read on `newstaging.cadence.com`, in the
   Japanese or Korean edition for three of them (CONN, CSR, XPROP,
   COV); the fetch tool translated. Their `en_US` URLs in the
   bibliography are by analogy with the pages read in English (SEC)
   and with `cadence-jasper-fpv`; open each before print. The
   Synopsys datasheet is dated 2022 and may be superseded.
6. **Origins not found** for three techniques as hardware engineers
   use them: "counter abstraction" in the timer sense (T4), initial-
   value abstraction (T6), assumption sanity as a practice (T29),
   cover-guided deep search (T25). The chapter should define each in
   its own words and attribute nothing.
7. **Unmeasured tool claims in section 3**, each marked [U] where it
   appears: boxing removes the boxed RTL's own assertions (T1); the
   `$stable` symbolic constant may change between cycle 0 and cycle
   1 (T8); a gated clock written as `clk & en` (R6); combinational
   circular assume-guarantee (T18).
8. The 40 s bounded search on the DMA lemmas (M7) was a scratch
   run whose script was not kept; their results are in the table and
   should be re-run as part of a kept script before the chapter
   relies on them.
9. Every measured verdict in section 2 is from one machine (4 cores,
   15 GB) on 2026-11-16; seconds are wall-clock per property as the
   tool printed them, with up to two scripts running at once (noted
   per row where it applied). Verdicts with one selected engine were
   repeatable in FM D.5; this note did not re-run each script to
   check repeatability.

## 8. Open questions for the outline

1. **Thirty-one entries times six parts is long.** At the previous
   chapter's density (about 12,000 words for one engine story), six
   parts each would put this chapter near 25,000 words. Options:
   (a) full six-part entries only for the entries measured on the
   spine, and a compact form (problem, idea, preserves, one-line
   pitfall, pointer to the example) for those the two previous
   chapters already own (T17, T22, T23, T26, T27, T28) and those not
   available in the tool (T7, T24, T25, T31); (b) all six parts
   everywhere and a split into two chapters. The note assumes (a);
   it does not change the plan's catalog, only the length per entry.
2. **The two-word ordering check (T10) is the one entry whose natural
   formulation got no verdict** (section 2, M2). Keep it with the
   position form that did prove, and show the flag form's
   `undetermined` as the lesson that the tracking state, not the
   property, decides provability? Or move it to an exercise? The
   note assumes the first.
3. **The case split (T19) sits outside the spine** (section 5). Keep
   the multiplier miter (it previews the equivalence chapter and is
   the only measured case where a split is natural), or describe the
   split in prose on the DMA?
4. **Prophecy (T16).** The measurement shows that the shell cannot
   use a prophecy variable for anything a history variable cannot
   do, and that the naive use is a spurious counterexample. Should
   the entry be retitled "History variables, and why prophecy needs
   care" (an honest framing), or kept under the plan's title with the
   trap as its pitfall? The note assumes the plan's title with the
   trap as the pitfall.
5. **rIC3 carries several entries.** Without it, memory abstraction's
   flat comparison, the history-variable FIFO check (M5 C) and the
   two-word position form have no proving engine at all (the
   in-house engines leave them `undetermined`). The book's engine
   list already names rIC3 and examples that select it declare
   `REQUIRES := ric3`; every such example is skipped on a machine
   without it. The outline should list which entries are ric3-only.
6. **One protocol checker or two.** The measurements wrote a fresh
   `vr_rules` with an `ASSUME` parameter. Chapter 9 ships `hs_check`
   with the same two rules (plus `Answer_A`, ready only when valid,
   which is a rule about the receiver and would become an assumption
   on the wrong side for a sender). Decide whether the chapter
   splices a new parameterized checker or derives from `hs_check`.
7. **Symmetry on the DMA** is not an exact symmetry (reset value of
   the round-robin pointer). The outline must decide whether the
   chapter (a) says the DMA is "symmetric up to reset" and proves
   both channels anyway, or (b) uses the extracted arbiter as the
   example and the DMA as the cautionary case. The note assumes (b).
8. **Where the six recipes live.** R6 (clock gating) and R3
   (X-propagation) overlap with the equivalence and static chapter;
   R4 overlaps with Chapter 8's closure. The plan puts all six here;
   the outline should name, for each, which chapter owns the full
   treatment and keep this chapter's page to the recipe.

