# Draft log: Formal Techniques: Abstraction, Symbolic Reasoning and Decomposition

Started 2026-11-16. Inputs: `research/ch19-outline.md` (section 9,
"Pre-draft measurements", overrides the earlier sections where they
differ), `research/ch19-formal-techniques.md` (RN), the 24 example
directories under `examples/ch19-formal-techniques/` (their `run.out`
files are the only source for verdicts, depths and counts), and
`chapters/ch18-formal-property-verification.qmd` as the model for shape
and style.

## 1. Plan and choices made before writing

- One chapter file, `chapters/ch19-formal-techniques.qmd`, unwrapped,
  one paragraph per line, as ch18.
- Section order and entry order follow the outline: motivation, the
  preservation framing, six families (Shrinking the problem, Symbolic
  reasoning, Modeling code, Decomposition, Constraining and bug
  hunting, Trusting the result), six recipes, the worked example
  (`pipe-256`), Future directions, Summary, Exercises, Further reading.
  Full six-part entries (Problem, Idea, How to write it, What it
  preserves, Example, Pitfalls) where the outline gives an example
  directory; compact entries (Idea, What it preserves, Where it is
  taught or Not available) for the rest. 31 entries in all; the
  heading order is checked by the figure script against
  `figures/ch19_catalog.csv`.
- Every listing is spliced with `{.lang include=... lines="a-b"}`;
  every range was checked by script against the file it names (section
  7). No verdict is typed by hand that a splice does not show.
- Seconds appear only in `seconds-ric3/tbl-seconds.md`, included once
  with `{{< include >}}` in the worked example; the prose says "about as
  much" and points at @tbl-ch19-seconds.
- rIC3 is named where it is needed. Five directories select it:
  `mem-abs-ric3`, `two-word-ric3`, `history-ric3`, `hier-ric3`,
  `seconds-ric3`. The text says so at each splice, and the
  motivation section lists them. Every other example runs on the
  in-house engines; `protocol-dma` runs on `informal-ic3`.
- Exercises: ch18 places them in one Exercise callout under
  `## Exercises` and the book has no solutions appendix, so the twelve
  answers are recorded here (section 6), each tied to `run.out` rows.

## 2. Sections and what each claim rests on

Line numbers are of the `run.out` named.

- Motivation (`sec-ch19-motivation`): `mem-abs/run.out` 1-14 (flat 256
  words: `a_read` undetermined under informal-kind; boxed with
  contract: proven). Figure `fig-ch19-map` from `figures/ch19_catalog.csv`.
- Preservation (`sec-ch19-preserve`): definitions from
  `clarke1994abstraction` (read per outline section 9 table). The
  tool's own black-box note is spliced from `cut-timer/run.out` 11.
  Cover pitfall: `cut-timer/run.out` (grant covered at depth 3 boxed,
  202 in the design). Figure `fig-ch19-preserve` (no verdicts).
- Black box, cut point, timer (`sec-ch19-bbox`, `-cut`, `-timer`):
  `cut-timer/run.out` 1-17, 18-22 (a name inside a box: accepted by
  `assert`, refused at `prove`), 30-39, 40-53, 54-64 (the 199-cycle
  gap assumed under the cut; the depth-3 trace survives), 65-73
  (bounded liveness, reused in `sec-ch19-boundedlive`).
- Parameter reduction (`sec-ch19-param`): `param-width/run.out` whole
  (the bug at every depth; the 5-bit count and `$clog2(5)` show the
  non-transfer). Cutoff sentence rests on `emerson2000cutoff` (read:
  abstract, section 1).
- Memory abstraction (`sec-ch19-memabs`): `mem-abs/run.out` 15-21,
  22-37, 38-51; `mem-abs-ric3/run.out` whole (flat proven by rIC3 at 16
  and 256 words). Burch and Dill sentence: `burch1994pipelined` (read,
  extended version). Bjesse at title level. Figure `fig-ch19-memabs`
  asserts eight verdicts from `mem-abs/run.out`.
- Initial value (`sec-ch19-initval`): `init-value/run.out` 1-12, 13-36,
  37-41, 42-51. Mutant start state: count 254 (corrected during
  drafting).
- Localization (`sec-ch19-localize`): compact; `clarke2000cegar`,
  `mcmillan2003abstraction` at title level.
- Symbolic constant (`sec-ch19-symconst`): `symconst/run.out` 1-10
  (`$anyconst`: zero properties listed), 11-18 (`$stable` binds the
  reset cycle; outline C6 per section 9). `sby-docs` for the extension.
- Oracle (`sec-ch19-oracle`): compact, refers to `sec-ch18-liveness`.
- Tracking one word (`sec-ch19-track`): `track-word/run.out` whole
  (proved with the slot helper). Wolper at title level.
- Two-word check (`sec-ch19-twoword`): `two-word/run.out` whole
  (position form proved with helpers at 4 entries; flag form's
  once-only checks not proved); `two-word-ric3/run.out` whole. Figure
  `fig-ch19-track`.
- Symmetry (`sec-ch19-symmetry`): `symmetry/run.out` 1-17, 18-32,
  33-43, 44-48. `emerson1996symmetry` (read: sections 1-3).
- Ghost state, reference model (`sec-ch19-ghost`, `-refmodel`):
  `contract/run.out` whole. `owicki1976axiomatic` (read).
- Protocol checker (`sec-ch19-protocol`): `protocol/run.out` 1-24,
  25-32; `protocol-dma/run.out` whole (informal-ic3, `ANSWER = 0`,
  `RFirst_A` fails at depth 6 with no rules assumed, proven with the
  slave's rules). `opentitan-tlul-assert` for the role parameter.
- History and prophecy (`sec-ch19-history`): `history/run.out` whole
  (A: `$past` cex depth 5; B: proven, mutant cex depth 1; C: `c_popk`
  covered depth 11, `a_proph` cex depth 1 with the two-row trace);
  `history-ric3/run.out` whole. `abadi1991refinement` (read, report
  version). Figure `fig-ch19-prophecy`.
- Helper (`sec-ch19-helper`): compact, refers to ch18.
- Assume-guarantee (`sec-ch19-ag`): `ag/run.out` whole.
  `abadi1995conjoining`, `mcmillan1999circular` (read);
  `misra1981proofs` at title level. Figure `fig-ch19-ag`.
- Case split (`sec-ch19-casesplit`): `case-split/run.out` whole.
  `mcmillan1999compositional` (read).
- Hierarchical proof (`sec-ch19-hier`): `hier/run.out` whole;
  `hier-ric3/run.out` whole.
- Decomposition (`sec-ch19-decomp`): `decomp/run.out` whole (L1_A and
  L2_A no verdict for bmc, kind, ic3 in 5 s; E2E_A proven with both
  assumed; Done3_C covered depth 15). Figure `fig-ch19-decomp`.
- Constraining family (`sec-ch19-constrain`): compact entries;
  `cut-timer/run.out` 65-73 for bounded liveness.
- Trust family (`sec-ch19-trust`): `sanity/run.out` whole;
  `mutants/run.out` 52-65; `demillo1978mutation`,
  `chockler2001practical`, `ghassabani2016ivc`, `cadence-jasper-cov`
  (vendor statement, labeled as such). In Practice callout on what a
  proof ships with.
- Recipes (`sec-ch19-recipes`): connectivity, registers, X-propagation,
  unreachable coverage, information flow, clock gating. Vendor
  statements cite `cadence-jasper-conn`, `-csr`, `-xprop`, `-cov`,
  `-sec` and `synopsys-vcformal-datasheet` and are labeled vendor
  statements. Information flow: `clarkson2010hyperproperties`,
  `barthe2004selfcomposition`, `terauchi2005safety`. SEC:
  `vaneijk2000sec`. X: `sec-ch04-fourstate`, `sec-ch17-smt`.
- Worked example (`sec-ch19-example`): `pipe-256/pipe.tcl` 14-20,
  81-87, 96-105; `pipe-256/run.out` 1-13, 14-22, 23-32, 33-41, 42-54,
  55-58, 59-77; the seconds table. Figure `fig-ch19-pipe` asserts the
  15 record lines of `run.out` 59-77.
- Future directions, Summary, Exercises, Further reading
  (`seligman2023formal` and `bierekroening2018sat` by title).

## 3. Figures

Eight figures, `figures/gen_ch19_figures.py` (style module `hw`, as
ch18). Each figure that shows a verdict parses it from the `run.out`
and asserts it, so a changed run fails the script:
`ch19-map.svg` (the catalog; checks headings against
`ch19_catalog.csv`), `ch19-preserve.svg`, `ch19-memabs.svg`,
`ch19-track.svg`, `ch19-prophecy.svg`, `ch19-ag.svg`,
`ch19-decomp.svg`, `ch19-pipe.svg`. Rendered to PNG with headless
Chrome and inspected; fixed while drafting: block end markers that
matched the engine line (`---`), tag text overflowing the catalog
boxes, the helper text running off the right edge of `ch19-track`,
the two footers of `ch19-ag` overlapping, and the `u0.g`/`u1.g`
registers covering the wire labels of `ch19-pipe`.

## 4. Deviations from the outline

All per outline section 9 unless noted.

- T3 (parameter reduction): the bug shows at every depth; the
  non-transfer is shown by the 5-bit count and `$clog2(5)`.
- T4 (timer): the one-cycle gap, and the finding (i) pitfall (a trace
  that ends before an assumption's future survives it).
- T6 folded into T9 (initial value): induction fails from INV at 16
  entries, IC3 proves; induction proves at 256 with the helper.
- T9 (tracking one word) in-house with the slot helper.
- T10 (two-word) ordering proved in position form with helpers.
- C6: `$stable` binds the reset cycle (symconst block C).
- C10: the boxed assertion is listed as an error at `prove`
  (`cut-timer/run.out` 18-22).
- Protocol-dma uses informal-ic3 with `ANSWER = 0` and adds `RFirst_A`.
- Hierarchical proof: "g far from DEPTH" changed to "g below DEPTH"
  (what block B's trace shows).
- Worked example: the outline's "flat gave no verdict at 256" was not
  run, so it is not stated.

## 5. Claims cut

- Two-word "at 16 entries no proof": a probe, not in a `run.out`.
- T20 "first DMA invariant undetermined for every engine including
  rIC3": not in any `run.out`. Also cut: "L1 is true"; the text says
  neither lemma is proved.
- The string-ROLE silent property loss (section 9 finding ii): not in a
  `run.out`.
- "A Tcl property gets an error naming `$anyconst`": not shown by the
  run; the run shows zero properties listed.
- Hard-coded "Chapter 9's" in prose replaced by `@sec-ch09-example` and
  `@sec-ch09-properties`. (The string "Chapter 9's" remains inside
  `mutants/run.out`, which is spliced tool output and was not edited.)
- `@sec-ch04-semantics` does not exist; `@sec-ch04-fourstate` used.
- "InFormal is two-valued (`@sec-ch09-formal`)" and "no equivalence
  command (`@sec-ch09-tools`)": unsourced, replaced by `@sec-ch17-smt`,
  the `$isunknown` drop of `@sec-ch09-tools`, and "the miter is built
  by hand".
- Not given a refs.bib entry because the chapter does not cite them
  (outline: not opened, or further reading at most):
  `bryant2001positive`, `clarke1996symmetry`, `ip1996symmetry`,
  `hoskote1999coverage`, `tiwari2009glift`.

## 6. Exercise answers

1. (a) Proofs (over-approximation). (b) Counterexamples
   (under-approximation; proofs say nothing about `req` traffic).
   (c) Both (a symbolic constant changes nothing the property sees).
   (d) Neither, without an argument such as a cutoff, data
   independence or induction on the parameter (`param-width`).
2. Not necessarily. `mem-abs/run.out` line 17, the tool's note that a
   counterexample may use output values the boxed logic cannot
   produce. Assuming the contract `m_store` removes it (block B,
   `a_read` proven), and block D proves the contract on the real
   storage with the helper.
3. INV holds at reset, and INV is inductive: the two `INV_A proven`
   rows, `init-value/run.out` lines 34 and 38. The depth-0 trace of
   block D starts in a state (empty with the pointers apart) that the
   weaker start set allows and no trace from reset reaches.
4. The tool did not accept `$anyconst` and dropped every RTL property
   without a message (`symconst/run.out` line 2, "properties listed:
   0"). It accepts a free input to the wrapper held by an assumption,
   `assume {$stable(sa)}` (lines 6-10).
5. The rotation i -> i+1 mod 4. It maps the transitions to themselves
   (the rotation check of block A, `a_rot` proven, line 12) and the
   property for port 0 to that for port 1, but not the initial state:
   `last` reset to 3 is not mapped to itself, and `a_rot` with both
   copies reset fails at depth 2 (line 37). With a free start for
   `last`, port 0 proven covers all four: lines 6, 12, and 17-18 (the
   reset state is one of the free starts).
6. Ports 1, 2 and 3, each at depth 5 (`symmetry/run.out` lines 45, 48,
   51). Port 0 requesting in every cycle starves port 3 (as it does
   ports 1 and 2).
7. `c_in_drop cover unreachable` (`protocol/run.out` line 35). The
   assertion is about the stage's input, which the environment drives;
   it is proven only because the wrongly assumed sender rules on the
   output reach back through the wire stage and constrain the input,
   which nobody is obliged to keep.
8. The trace is two cycles long (`history/run.out` lines 30-32): the
   push of the guessed word is in cycle 1 and the trace ends there. The
   assumption `m_check` constrains only the cycle of pop k, which the
   trace does not contain, so nothing removes it.
9. The output register of each block: a guarantee at cycle t + 1
   depends on the neighbor's only up to cycle t, so neither can fail
   first. A liveness assumption has no first violation, so the
   induction has nothing to start from; the ring is refuted at depth 3
   with a lasso in which both outputs stay 0 (`ag/run.out` line 29).
10. The completeness check `A_cover3` fails at depth 0
    (`case-split/run.out` line 38); the missing case is
    `a[7:6] == 3`.
11. The boxed FIFO raises `full` while its ghost `g` is below `DEPTH`
    (`hier/run.out` line 18; the missing half of the contract forbids
    it).
12. `Deep_C` is covered at depth 51, `Witness_C` is unreachable
    (`sanity/run.out` lines 19-20). The witness cover exposes the
    assumption; the deep cover passes because mode-0 traces run on.

## 7. Final checks

- Word count: 18,879 by `wc -w` on the source (markup included);
  18,510 excluding fenced blocks and callout fences.
- `scripts/check-structure.sh`: "every chapter keeps the template".
- `scripts/check-citations.sh`: check 1, no swallowed references.
  Check 2 run against a pandoc plain-text render of the chapter: every
  key cited in ch19 appears, except `abadi1991refinement` and
  `abadi1995conjoining`, which are false positives: the script's
  surname extraction stops at the brace in `Mart{\'\i}n` (the rendered
  text contains "Abadi" eight times). The accent is kept in the house
  LaTeX-escape form.
- Splices: every `include` path exists and every `lines` range lies
  inside its file (script over all 72 includes); first and last lines
  of each range inspected.
- Cross-references: every `@sec-`, `@fig-`, `@tbl-` in the chapter
  resolves to a label in `chapters/`, `appendices/` or the included
  `tbl-seconds.md`; every glossary `See @sec-ch19-...` resolves.
- Render: quarto is not installed (`~/.local/bin/quarto` absent).
  Includes were expanded by a script and the result converted with
  pandoc (`--citeproc --bibliography refs.bib`) to HTML, LaTeX and
  plain text. No citeproc warning other than the Quarto cross-reference
  labels; no stray backslash outside code and math; the one table (the
  seconds table) contains no math.
- No hard-coded chapter, section, figure or table number in prose;
  American spelling (no British forms found by grep in prose; "not
  modelled" occurs only inside spliced tool output).
- refs.bib: 28 new entries appended (keys checked absent first); DOI
  entries carry no URL or access date (AGENTS.md); URL entries carry
  "Accessed 2026-11-16" in `note`.
- Glossary: 28 entries added to `appendices/appG-glossary.qmd`.
- `_quarto.yml`: ch19 registered after ch18 in Part IV.
- `scripts/check-examples.sh` not run: it re-runs the examples and
  rewrites `examples/status.json`, which this task does not touch.

## Round 1 fixes (2026-11-16)

Fixes for `docs/reviews/ch19-gate2a-2026-11-16.md` (A) and
`docs/reviews/ch19-gate2b-2026-11-16.md` (B). One line per finding.
Every changed example was run twice with InFormal `5114330` and rIC3
on the PATH; the two `run.out` files are identical.

Blocking:
- A-B1 / B-B1: timer pitfall and the prophecy Pitfall rewritten. Block
  F of `cut-timer/` now assumes the gap with a window of 2 and of 199:
  the window of 2 (which fits the depth-3 trace) gives `a_no_early`
  proven, the window of 199 keeps the depth-3 trace. The text presents
  this as InFormal's measured behavior (a multi-cycle implication is
  judged only once its window closes; IEEE 1800 would exclude the
  trace), cites the run, separates it from the prophecy trap, and
  says "one cycle before it ends" (the trace breaks the assumption in
  cycle 2 of 0..3). `cut.tcl` header and block comment corrected.
  The outline's finding (i) is left as written (planning record).
- A-B2: helper entry and decomposition "What it preserves" now state
  the side condition (no proof assumes the property it helps, or a
  lemma whose proof assumed it); the Pitfall that forbade lemmas
  implying the end-to-end property is replaced by the proof-graph
  rule, and notes that `L1` and `L2` implying `E2E_A` is the aim.
  Glossary "Decomposition (property)" gets the same condition.
- A-B3: objective 9 removed. Teaching CTI shapes would need material
  no example has (the tool prints no counterexample to induction).
- A-B4: `[check]` and similar notes removed. `cadence-jasper-csr`,
  `-xprop`, `-cov`: URL never loaded, dropped; cited by title with
  `howpublished = {Vendor product page, cadence.com}` and where it was
  read. `bjesse2008memory`, `misra1981proofs`: working notes removed,
  fields kept (DOI; Crossref initials). `chockler2001practical`:
  volume 2102 added, note reduced to where it was read; pages and DOI
  not added (crossref, doi.org and dblp refused by the proxy, so not
  verifiable here). `barthe2004selfcomposition`: "DOI not found"
  removed, no DOI added (the guessed one belongs to another paper).
  `emerson2000cutoff`: working note removed.
- A-B5 / B-B2: witness covers added (one line each, with `expect`):
  `symmetry` A-C (`c_wait<i>`), `ag` A and C (`C_run`, `C_out`),
  `init-value` C (`P_C` in both proving runs), `mem-abs` D (`c_svok`,
  `c_mchk`), `symconst` B (`c_slot`), `history-ric3` A and B
  (`c_popk`), `cut-timer` E, F, G (`c_rose`, `c_req`), `hier-ric3`
  (`Drain_C`, `Full_C`), `two-word-ric3` B and `two-word` B,
  `track-word` A (DEPTH 4) and B. A scan of every `run.out` session
  now finds no proven implication without a cover in its session; the
  sessions left without one prove invariants, helpers or miter
  equalities. Text at the opening of the entries and in the witness
  cover entry says exactly that.

Non-blocking, taken:
- A-N1: initial-value side condition is the reset state in `INV`;
  inductiveness explained as what makes the start set contain every
  reachable state; the second `INV_A` row and `M_H` explained;
  exercise 3 and the glossary entry adjusted.
- A-N2: sentence that `track.sv` takes `ahead` from the FIFO's own
  `count`, which the FIFO checker checks separately.
- A-N3: param-width refutation at 32 explained by `5'(32)` truncating
  to 0 (and the count wrapping after 31).
- A-N4 / B-N3: "eight words behind it" in prose and the script comment.
- A-N5: `c_late` described per unit (depth 5 correct, depth 3 mutant
  with no request); script prints "the pop numbered k = 9".
- A-N6: "no occupied slot holds d1" in prose, figure and alt text.
- A-N7: loss sentence split between the flag and position forms.
- A-N8: refinement mappings exist "under conditions the paper states".
- A-N9: proof-core sentence says "bounded proof", not refutation.
- A-N10: X-propagation "pessimistic" sentence replaced.
- A-N11: 255 pushes (problem, summary, `init.tcl` verdict, Makefile).
- A-N12: forgotten-case sentence reworded (cases proved in block B).
- A-N13: memory CTI reason: the state can persist, not "more states".
- A-N14, A-N16, A-N17, A-N18: reworded as suggested; exercise 7 asks
  for the row about the input.
- A-N15: `reset -none` frees registers without an initial value
  (prose and `init.tcl` comment).
- A-N19: splice `18-29` (now including the unprocessed rows).
- A-N20: `hier.tcl` `9-27`, `dma_wcount.sv` `4-24`.
- A-N21: printed strings in `mutants.tcl` and `width.tcl` (and header
  comments there and in `pw_top.sv`) name no chapter numbers.
- A-N22: semi-formal sentence without the unsourced commercial claim;
  "Five of its six entries".
- A-N23: connectivity rows: one per channel term.
- A-N25: glossary "Symmetry" maps one part's property onto another's.
- A-N26: prophecy figure's far cell labeled "later" (schematic); alt
  text of the preservation figure lists cover-guided search.
- Worked-example suggestion: one sentence citing `hier`'s `Both_C`.
- B-N1: `mutants`: `a_integrity` on the wrap mutant runs alone with
  30 s (refuted at depth 17), so no expected row races the 2 s limit;
  prose updated. `mem-abs` D limits 20 s to 40 s; `case-split` whole
  miter 40 s to 80 s (proven rows; the limit costs nothing).
- B-N2: the DMA lemmas are called unproved and unrefuted, not true.
- B-N4: black-box sentence calls the message an internal "not
  supported yet" error, a tool limit; script heading reworded.
- B-N7: `hp.sv` history bit coinciding with `pend` stated;
  `seconds-ric3` lint compiles in memory (no `__pycache__` in the
  previous chapter's tree).

Non-blocking, left:
- A-N24 (LNCS volumes of five entries): the proxy refuses Crossref,
  doi.org and dblp, so the volumes could not be verified here.
- B-N5 (figure generator does not assert depths stated in alt texts):
  needs a design change to the generator or to check-structure.sh.
- B-N6 (`assume -disable` on an RTL assumption): belongs in the
  previous chapter's tool notes; not touched (other chapter).
- B-N7, mem-abs forwarding cover: optional; the forwarding path is
  exercised by mutant E.
- Appendix-F sentence on limits tied to the machine (B-N1 suggestion):
  other file; the chapter's mutation Pitfall already says it.

## Round 2 fixes (2026-11-16)

Fixes for `docs/reviews/ch19-gate2c-2026-11-16.md` (C, text) and
`docs/reviews/ch19-gate2d-2026-11-16.md` (D, code). One line per
finding. Changed examples: `ag`, `cut-timer`, `pipe-256`, `contract`,
`param-width`, `two-word-ric3`, `protocol`. Each was run twice with
InFormal `5114330` and rIC3 on the PATH (identical `run.out`), and
once each on scratch copies whose `one` sets half and twice the
printed limit (printed limit, and so `run.out`, unchanged).

Blocking:
- C-B1 (circular proof graph): the assume-guarantee entry's "What it
  preserves" now requires each block to be proved on its own, with
  its neighbor removed, so the assumption reaches only its inputs and
  nothing is assumed about its reset state. The decomposition
  Pitfall drops the "through a register" exemption and gives the
  reviewer's ring as the warning. The ring is now measured: `ag` block
  E (`ag_top` takes `RST1`, both resets at 1): `x == 0` alone cex at
  depth 1; with `y == 0` assumed proven, and `y == 0` with `x == 0`
  assumed proven; witness cover `C_run` unreachable in both. The `ag`
  prose describes block E. Glossary needs no change (C-N9).
- D-B1 (cover through an open window): block F's cover `c_rose`
  replaced by `c_win = req && !busy ##N 1` (expect covered, depth N+1:
  3 and 200). A last run of block F ships the vacuous case: assumption
  `req && !busy |=> !u_timer.expired ##1 1'b0`, a false response
  assertion `a_resp` proven, `$rose(busy)` covered at depth 2, `c_win`
  (`##2 1`) unreachable; spliced and explained in a new paragraph
  after the window paragraph (the sentence the reviewer asked for).
  The general claims (opening of the entries, witness-cover entry) now
  say: the antecedent or a scenario whose trace passes through it;
  under a multi-cycle assumption the cover runs to the end of the
  window; vacuity demonstrations leave the cover unreachable on
  purpose. "Every entry plants a bug" replaced by "the entries that
  plant a bug show ...; the others owe the same check". The P2_A
  exception (C-N3) no longer exists: `pipe-256` step 6 now covers
  `Full_C` under the final assumptions (below), so the claim is exact
  without it.
- D-B2 (headroom): `contract` A 5 s to 15 s; `param-width` B 5 s to
  15 s; `two-word-ric3` B 10 s to 30 s (text "in ten" to "in
  thirty"); `pipe-256` split: step 1 runs the three shallow covers
  with 30 s (`U1Full_C` 8.6 s), `Full_C` leaves step 1 and runs once,
  by `informal-bmc` with 120 s under the final assumptions in step 6,
  covered at depth 513 (about 45 s). No run now expects `Full_C`
  undetermined. Example about seventy seconds (Makefile comment).
  `cut-timer` F's real-timer run uses 20 s (`a_gap199` 3.6 s).
  Worked example text (D-N1, C-N4): step 1 says the deep witness is
  run once for budget, step 6 shows the run, the record and the
  closing sentence name `Full_C` at 513, the Worked Example box says
  "deep" not "out of reach", the 16-entry `Both_C` at 33 is given as
  the prediction of 513; figure alt text updated, figure regenerated.

Non-blocking, taken:
- C-N1: block F's first run proves both windows on the real timer
  (`a_gap2`, `a_gap199`, with `c_req`); text says so.
- C-N2: `[@informal-tool]` dropped from the window clause; "as block F
  measures".
- C-N3: see D-B1 (claims exact; `protocol` B gets `c_ready`, the
  antecedent of `Answer_A`, covered at depth 1).
- C-N4: 513 is now measured (step 6).
- C-N5: one sentence: side conditions run at 256; at 16 they hold by
  the same argument, are not run, and are a record line of their own.
- C-N6: the window paragraph split; the prophecy contrast and block G
  are paragraphs of their own.
- C-N7: the "lemmas that imply the goal are the aim" sentence moved
  to the end of the paragraph before the In Practice box.
- D-N2: `ag` C adds `G_none = s_eventually 1'b0`, expected cex (depth
  4, a fair lasso); fairness entry says a fairness assumption is
  checked by refuting a false liveness assertion, not by a cover.
  `C_out` kept.
- D-N3: `protocol` D adds `c_in_wait = i_valid && !i_ready`, covered
  at depth 1; prose says the antecedent happens and the assumption
  forces the consequent. Splices 1-25 and 26-34.
- D-N4: `two-word-ric3` B covers the literal antecedents, `c_head1`
  and `c_head2` (depths 2 and 4 under rIC3), in place of `c_both`.

Non-blocking, left:
- C-N8: the three Cadence entries keep title, publisher and
  `howpublished`; no URL (the vendor URL read was a staging host).
- C-N9: no change needed (reviewer's own conclusion).
- D-N5 (trivially reached covers in `symmetry`, `symconst`): optional,
  the covers meet the claim; not changed.
- D-N6: carried-over B-N5 and B-N6, as recorded in round 1.
- `two-word` C keeps `c_both` (its trace passes through each
  antecedent, which the reworded claim covers).
- Figures: `gen_ch19_figures.py` reads `ag` block D up to the next
  block (block E now follows it); `ch19-ag.svg` unchanged,
  `ch19-pipe.svg` regenerated (step 1 has no hatched cell; step 6
  shows `Full_C` at 513).
- Checks: all seven changed examples pass twice with identical
  `run.out`, and pass with identical `run.out` at half and at twice
  the limits; `check-structure.sh`, `check-citations.sh` pass; the
  chapter with includes expanded converts with pandoc 3.1.3 to HTML,
  LaTeX and plain text with only cross-reference warnings.

## Round 4 fixes (2026-11-16)

Fixes for `docs/reviews/ch19-gate2g-2026-11-16.md` (G, text) and
`docs/reviews/ch19-gate2h-2026-11-16.md` (H, code). G-B1 and H-B1 were
fixed by the reviewers' preferred option, shipping the covers, so the
claims at the opening of the entries and in the witness-cover entry are
true of the shipped scripts. Changed examples: `cut-timer`,
`symmetry`, `symconst`, `protocol`, `two-word`, `ag`, `hier`. Each was
run twice from clean (`make clean`, then `scripts/check-examples.sh
ch19-formal-techniques/<name>`) with InFormal `5114330` and rIC3 on
the PATH: all pass, and both runs are byte-identical to each other and
to a scratch run made before the repository files were written.
Changed `run.out` files: `cut-timer`, `symmetry`, `symconst`,
`protocol`, `two-word`, `ag`, `hier`.

Blocking:
- G-B1 / H-B1 (covers short of the consequent's cycle). Shipped, with
  `expect covered`:
  - `cut-timer` A-D: `c_gnt1 {gnt ##1 1}` in `handshake`, beside
    `c_gnt`, the witness of `a_gnt_once` (depths 203, 4, 4, 5; in the
    error run of block B it is unprocessed, like every other row).
  - `cut-timer` F, real timer: `c_req` replaced by `c_win2` and
    `c_win199`, `req && !busy ##N 1`, one per window (depths 3 and
    200, informal-kind, about 0.3 s for the deeper one).
  - `cut-timer` G, real timer: `c_req` replaced by `c_gnt {gnt}`, the
    grant that satisfies the ranged consequent (depth 202); that run's
    limit raised from 10 s to 20 s as G-B1 asked (`c_gnt` alone took
    6.3 s here). Makefile comment: about thirty seconds (measured 27 s).
  - `symmetry` A-C: `c_wait<i>` is now `req[i] && !gnt[i] ##4 1`
    (depth 5 for all nine; row count unchanged, so the four splice
    ranges did not move). Header comment of `arb` says so.
  - `symconst` B: `c_slot1 {u.do_write && u.wr_ptr == sa ##1 1}`
    (depth 2) beside `c_slot`.
  - `protocol` D: `c_in_wait1 {i_valid && !i_ready ##1 1}` (depth 2)
    beside `c_in_wait`.
  - `two-word` C: `c_inside {in1 && !out1 && in2 && !out2}` (depth 3),
    the witness of `p_ahead` that `c_both` was not (H-B1).
  Timing note: in block A, `c_gnt1` alone took 6.1 s of its 10 s
  limit, the same margin as the existing `c_gnt` (6.3 s); the limit was
  left at 10 s, as the reviewers did not ask to raise it.
  Text: the opening paragraph (:62) now says a witness is a cover of
  the case the assertion exists to check (@sec-ch18-cover), states the
  cycle rule as a minimum, says what "last cycle judged" means for a
  ranged consequent (G-N7: the cycle that satisfies it, or the end of
  the range), cites @sec-ch19-witness and @sec-ch19-timer, says every
  proved implication of the examples has a reached witness meeting the
  minimum (exceptions: the vacuous demonstrations, and the timed
  reruns of `seconds-ric3`, whose sessions carry one assertion and no
  cover; their witnesses are in the examples they time), and that the
  minimum is necessary and not sufficient, pointing at
  @sec-ch19-sanity. The witness-cover entry (:772) says the same, with
  the arbiter's `##4 1` and the grant as examples. The protocol,
  symconst, two-word and hier prose name the new witnesses and depths;
  block F's text says each window's proof has a witness to its end.
- G-B2 (sanity Pitfall recipe). Pitfall rewritten with the reviewer's
  sentence ("reaches the case the assertion exists to check, here mode
  1 with the counter about to reach 9, and at least runs to ..."),
  preceded by why the antecedent cover is not enough there. Measured in
  scratch (informal-kind, 5 s, part C's `M_dead1`): `A_mode` proven,
  `Ante_C {mode && chosen}` covered at depth 2, `Witness_C`
  unreachable, as G-B2 reported. The text gives no depth for `Ante_C`
  (it is not shipped); it argues from the design that mode 1 is chosen
  a cycle or two after reset, before the dead end at 5.

Non-blocking, taken:
- G-N1 / H-N1: :701 now "so an assumed lemma can remove the very
  traces on which the lemma it helps would fail" (G's clause).
- G-N2: :605 rewritten in the reviewer's words (input assumptions
  narrow the engine's choices; a state assumption can contradict a
  forced state; here both lemmas fail in the same cycle), and a new
  paragraph starts at "Block E is the warning".
- G-N3 / H-N2: `ag` block E adds `cover -name C_any {1'b1}`: covered
  at depth 1 alone, unreachable in both assumed runs, so "no trace at
  all" now rests on `run.out`; the text names `C_any`. The optional
  shared-input ring (G-N3 b) was not added; "the cover can still be
  reached" stays a sentence from the semantics, measured by both
  reviewers.
- G-N4: :907 replaced with the reviewer's exact sentence ("step 6
  gives its bounded search two minutes, four times the first look's
  limit"; `pipe-256/run.out` lines 2 and 55).
- G-N5: Summary bullet now "on one ring with both resets at 1, the two
  lemmas, each assumed in the other's proof, were both proven and both
  false".
- G-N6: exercise 9 now "is sound only if ... Which registers must it
  also have".
- G-N7: see G-B1.
- G-N8: section 6 answers updated to the current `run.out` lines:
  exercise 3 lines 34, 38; exercise 5 lines 12, 37 and 6, 12, 17-18;
  exercise 6 lines 45, 48, 51; exercise 7 line 35 (34 in the review,
  one more after `c_in_wait1`); exercise 9 line 29 (`ag` block E's new
  rows come after it).
- G-N9: one sentence added to the sanity Pitfall: `Witness_C` stops at
  8, so a dead end placed at 9 itself would leave it reached; a cover
  run on into the cycle the counter could be 9 catches it. Measured in
  scratch: with `mode && chosen |-> cnt != 4'd9` assumed, `A_mode`
  proven, `Witness_C` covered at depth 9, `mode && chosen && cnt ==
  4'd8 ##1 1` unreachable; with no assumption that cover is reached at
  depth 10. Not shipped.
- H-N3: `hier` block C (assumed) adds `Drain_C {G == 6'd1 ##1 G ==
  '0}`, `P1_A`'s witness as in `pipe-256`, covered at depth 4; the hier
  prose names it.

Non-blocking, left:
- G-N10 (`refs.bib` case bracing): `refs.bib` is shared by every
  chapter and this pass was scoped to the chapter, its examples, log
  and figures, with another chapter being edited at the same time; the
  bracing is left for a pass that owns `refs.bib`.

Splices: every include of a changed file was re-read, first and last
line of each range. New ranges: `cut-timer/run.out` 12-12, 1-19,
20-32, 33-43, 44-59, 60-86, 87-94, 95-104; `cut-timer/cut.tcl` 23-38,
63-71, 73-89; `symconst/run.out` 1-12, 13-20; `protocol/run.out`
26-35. `symmetry/run.out` ranges unchanged (rows replaced, not
added); `two-word`, `ag`, `hier` `run.out` are spliced whole;
`two.tcl` 12-45 and `hier.tcl` 9-27 unchanged. No other chapter or
appendix splices these files.

Checks: `python3 figures/gen_ch19_figures.py` rewrites all eight SVGs
byte for byte (no input it reads changed meaning; no pin changed);
`scripts/check-structure.sh` passes; the chapter with includes
expanded (code splices with their ranges, and `tbl-seconds.md`)
converts with pandoc to HTML and LaTeX, exit 0, and every warning is
an unresolved `sec-`/`fig-`/`tbl-` cross-reference, which plain pandoc
does not resolve. Sources stay within 80 columns.
