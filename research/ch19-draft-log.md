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
   rows, `init-value/run.out` lines 32 and 36. The depth-0 trace of
   block D starts in a state (empty with the pointers apart) that the
   weaker start set allows and no trace from reset reaches.
4. The tool did not accept `$anyconst` and dropped every RTL property
   without a message (`symconst/run.out` line 2, "properties listed:
   0"). It accepts a free input to the wrapper held by an assumption,
   `assume {$stable(sa)}` (lines 6-10).
5. The rotation i -> i+1 mod 4. It maps the transitions to themselves
   (the rotation check of block A, `a_rot` proven, line 11) and the
   property for port 0 to that for port 1, but not the initial state:
   `last` reset to 3 is not mapped to itself, and `a_rot` with both
   copies reset fails at depth 2 (line 32). With a free start for
   `last`, port 0 proven covers all four: lines 6, 11, and 16-17 (the
   reset state is one of the free starts).
6. Ports 1, 2 and 3, each at depth 5 (`symmetry/run.out` lines 39, 41,
   43). Port 0 requesting in every cycle starves port 3 (as it does
   ports 1 and 2).
7. `c_in_drop cover unreachable` (`protocol/run.out` line 32). The
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
   with a lasso in which both outputs stay 0 (`ag/run.out` line 25).
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
