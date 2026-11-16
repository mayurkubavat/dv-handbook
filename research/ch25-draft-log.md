# Draft log: Mutation Testing: Qualifying the Testbench

Started 2026-11-16. Inputs: `research/ch25-outline.md` (gate 1 passed;
section 10, "Pre-draft measurements", overrides the earlier sections
where they differ), `research/ch25-mutation-testing.md` (RN), the 17
example directories under `examples/ch25-mutation-testing/` (their
`run.out` and `measure.out` files and generated tables are the only
source for every number), and `chapters/ch21-statistics-random-testing.qmd`
and `chapters/ch19-formal-techniques.qmd` as the model for shape, voice,
callouts, splicing, figures, glossary and exercises.

## 1. Plan and choices made before writing

- One chapter file, `chapters/ch25-mutation-testing.qmd`, unwrapped, one
  paragraph per line, as ch19 and ch21. Registered in `_quarto.yml` under
  a new part, "Part V · Borrowed from Software", between Part IV and
  Part VII.
- Section order follows the outline: motivation (kill rate beside
  coverage), concepts, fault model I (source operators), reading
  survivors, equivalent mutants and the miter, the property set as a
  judge, fault model II (netlist mutation, schemata, MCY), sampling,
  the evidence that mutants stand for real bugs, the worked example
  (closing the gap with a data check), Future directions, Summary,
  Exercises, Further reading.
- One object carries the chapter: the matrix of verdicts, mutant by
  testbench, on the repaired FIFO. Every later section either explains
  a column of it, classifies a row of it, or changes the population it
  is computed over.
- Every listing is spliced with `{.lang include=... lines="a-b"}` (53
  includes) or `{{< include >}}` (3 generated tables:
  `tbl-ch25-operators.md`, `tbl-ch25-survivors.md`,
  `tbl-ch25-report.md`). Every range was checked by script against its
  file (section 7). No number appears in prose that a splice or a
  generated table does not show, except arithmetic on numbers a run
  prints (the ratio $0.8905/(1-e)$ and the operator counts).
- Toolchain stated plainly in the netlist section: the examples use
  Yosys's `mutate` pass and hand-built InFormal miters (InFormal's BMC
  and k-induction, rIC3's IC3 for proofs); MCY is described from its
  documentation and not run, because its documented equivalence filter
  runs SymbiYosys, which the book replaced with InFormal.
- The three numbers (kill rate, equivalent fraction, score) are kept
  apart throughout and given a Definition in the sampling section; the
  ratio of interval ends is shown failing (1.019).
- Vendor material (Certitude papers, the vendor's
  activation/propagation/detection, the YosysHQ application note) is
  labeled as vendor in the sentence that uses it.
- No quotation longer than a sentence. MCY's documentation could not be
  fetched again while drafting (the proxy refuses external hosts), so
  MCY is paraphrased from the RN's reading of it, not quoted.

## 2. Sections and what each claim rests on

- **Kill rate beside coverage** (`sec-ch25-motivation`):
  `opening/run.out` 14-20 (coverage table with kill counts) and 7-8
  (covergroup coverage). The checking testbench at 22/44 kills with the
  highest coverage; ch08's "nothing in the file checks the FIFO" quoted
  as ch08's. `fig-ch25-axes`.
- **Concepts** (`sec-ch25-concepts`): definitions of mutant, kill,
  strong/weak/firm mutation from `jia2011survey`; the harness verdicts
  from `common/mutlib.py` 5-11; mutation score versus kill rate; the two
  hypotheses (`jia2011survey`, `budd1980theoretical`); first-order and
  higher-order as concepts only; reach/infect/propagate/reveal with
  revealability attributed through `papadakis2019advances`;
  `fig-ch25-rip` (verdicts from `source-sim`); `tbl-ch25-conditions`
  hand-written, words only, vendor names from `hampton2009fq`.
- **Fault model I** (`sec-ch25-source`): `srcmut.py` 40-75,
  `source-mutants/run.out` 3-47 (44 mutants), the generated operator
  table, lint 59-68 (lint kills 7), `source-sim/measure.out` 3 (180
  builds, 1685 s), `srcmut.py` 142-151 (schema forms). In Practice on
  operator choice from `just2014mutants`.
- **Reading survivors** (`sec-ch25-survivors`): `source-sim/run.out`
  1-60 and 63-64 (matrix; schema agrees with per-mutant builds 44/44);
  `opening/run.out` 5-6 (occupancy). Classes: stimulus gap `m35`;
  checking gap of 15 (`m08`, `m10`, `m14`-`m25`, `m33`); directed-test
  gaps `m12` and `m42`; seven killed by nobody. Seed Pitfall from
  `source-sim/run.out` 61-62 (first killing seed 2, 53 of 100) and
  `netlist-population/run.out` 9-16.
- **Equivalent mutants and the miter** (`sec-ch25-equiv`):
  `common/miter.sv`, `miter.py` 29-30; `miter-differ/run.out` 1-13 and
  48-52 (`m42` differs at depth 17; no difference for `m32 m36 m43
  m44`); `equiv-outright` 4-11; `equiv-invariant` 2-12;
  `tb_async_reset.sv` 20-37 and `equiv-reset/run.out` 1-12 (`m05`
  proved by rIC3, killed by a reset pulse between edges);
  `white-box/run.out` 8-32 (`m44`); TCE from `papadakis2015tce` and
  `source-mutants/run.out` 69-77 (only `m32` identical; `m06`/`m07`
  refused); generated `tbl-ch25-survivors.md`; initial-values Pitfall
  from `rand-init/run.out` 5-24 and the Verilator guide
  (`verilator-exe-verilator`, `verilator-exe-sim`); comparison Pitfall
  from `miter-differ/run.out` 53.
- **The property set as a judge** (`sec-ch25-formal`):
  `property-set/run.out` 2-5 and 52-57 (38 counterexamples of 44, 2
  refused, kills every non-equivalent mutant); `measure.out` 20-39 and
  59-64; Hoskote, Chockler, Große, Claessen for the literature;
  `beer2001vacuity` as ch09 describes it. `fig-ch25-matrix`.
- **Fault model II** (`sec-ch25-netlist`): `yosysmut.py` 41-49;
  `netlist-list/run.out` 4-22 and 47-48 (9,281 mutations, 73.8% on the
  memory); `untch1993schemata` ("more than 300%");
  `fifo_wrap.sv` 22-28; `netlist-population/measure.out` 3-6 and
  `run.out` 3-8, 69-75; `source-sim/run.out` 54-59 for the comparison.
  MCY from `mcy-docs` and `yosys-ap400` (labeled vendor); the `m42`
  EQGAP point from `miter-differ/run.out` 48. Two Pitfalls from
  `harness-pitfalls/run.out` 2-10 and 11-14, `yosysmut.py` 97-104,
  `tb_plusarg.sv`.
- **Sampling** (`sec-ch25-sampling`): `gopinath2015hard`;
  `netlist-sample/run.out` 2-7, 14-19, 26-33;
  `netlist-population/run.out` 50-55 and 62-68; `fig-ch25-sampling`;
  `netlist-formal/run.out` 3-21 (equivalent fraction 0.060 [0.022,
  0.126]; score 80/94 for the property set); `netlist-formal/measure.out`
  83-94 and 3-4 (715 s on 4 workers).
- **Evidence** (`sec-ch25-evidence`): `just2014mutants`,
  `papadakis2018correlated`, `chekam2017threshold`,
  `inozemtseva2014coverage`; HDL work `alhayek1996unified`,
  `serrestou2007rtl`, `lin2012epa`, `huang2015mutation`, and the
  vendor's Certitude papers labeled as vendor; `petrovic2021mutation`
  (89%) for mutation on the diff.
- **Worked example** (`sec-ch25-example`): `fifo_data_sva.sv` 22-37,
  `fifo_data_bind.sv`, `fifth-tb/run.out` 1-6 and 7-24, generated
  `tbl-ch25-report.md` (37/44 default, 40/44 randomized, 899/1000
  [0.879, 0.917]).
- **Future directions**: `foster2025ach`, `jasper2025buggen` (vendor),
  `tian2024llmequiv`, `bhadra2026gatetruth`, cross-references to the
  generative-AI chapter and named, unwritten chapters.

## 3. Figures

Generated by `figures/gen_ch25_figures.py` from the example data. The
script pins the SHA-256 of the 11 `run.out` files it reads and asserts
the facts each figure draws (the `m16` row, 38 property-set
counterexamples, every sampling interval containing the population
rate), so it fails if the data change. Each was rendered to PNG with
headless Chrome and checked as an image.

- `ch25-axes.svg`: coverage against kill rate for the four testbenches
  (`opening/run.out`). Labels moved after the first render overlapped.
- `ch25-rip.svg`: `m16` through reach, infect, propagate, reveal, one
  bar per testbench. Datapath labels moved after the first render.
- `ch25-matrix.svg`: the verdict matrix, 44 mutants by four testbenches,
  with the miter class beside it. Narrowed from 1020 to 971 px wide.
- `ch25-sampling.svg`: Clopper-Pearson intervals at n = 30, 100, 300,
  1,000 against the population line for three testbenches. The
  population label collided with the n = 1,000 bars; moved under each
  panel title.

## 4. Deviations from the outline

Where section 10 or a `run.out` disagrees with the earlier outline, the
run wins:

- The property set scores 80/94, 0.851 [0.763, 0.916], and misses 14
  netlist mutations at depths 16-31, not 15.
- The formal sample took 715 s (about 12 minutes) on 4 workers.
- Trivial compiler equivalence finds only `m32`; `m06` and `m07` are
  refused by Yosys's front end rather than found duplicate.
- `m35` is killed first at seed 2, by 53 of 100 seeds.
- The miter that compares `rd_data` on every cycle differs from itself
  at depth 1.
- `m05` is proved equivalent only under the formal tool's reset model
  and is killed by an asynchronous reset pulse.
- The induction contrast for `m43` is changed: the helper `count <= 16`
  is not enough to prove the whole miter by k-induction; rIC3 proves it.
- The fifth testbench kills 37/44 at default initial values and 40/44
  randomized, and 899/1000 netlist mutations.
- The newly killed mutants are `m08`, `m10`, `m14`-`m25` and `m33`
  (15); the checking-gap set is 15, not 13. "`m35` dies because traffic
  drains" is stated as already true before the fix, not as news.
- `m42` is killed by two testbenches, not three; the MCY example uses
  it as an EQGAP case.

## 5. Claims cut

- Wong and Mathur's figures: not read for content.
- Lin et al.'s 33-61% range: not kept; the chapter keeps
  only the comparison against weak-mutation preprocessing.
- BugGen's 94% and 104: not kept; BugGen cited for its method only.
- `jia2009hom`: not cited; higher-order mutants mentioned as a concept.
- Petrović et al.'s 820: not kept; 89% kept.
- MCY's wording: paraphrased, not quoted (documentation not refetchable).
- Semantics of Yosys's `cnot0`/`cnot1` modes: not documented; removed.
- Prose removed while drafting because no run prints it: "176 builds",
  "takes a second", an unsourced claim about in-house engines (replaced
  by the REQUIRES/skip sentence), "benchmark efforts", "most of the
  rest" for `$procdff` (now "one in seven"), "sparse on flags" for the
  directed column, the claim that every deep netlist mutation sits on
  the write path (narrowed to the two rows rerun, lines 42/43).

## 6. Exercise answers

Intervals were recomputed with `common/mutlib.py`'s `cp()`, the
function the examples use.

1. [0.212, 0.400]; yes, it contains 2725/9281 = 0.2936.
2. [0.022, 0.126] (`netlist-formal/run.out` line 5).
3. 0.947 at 0.060; 0.911 at 0.022; 1.019 at 0.126. The division is
   not wrong (the score is monotone in both inputs); the input is: it
   shows that 0.126 is incompatible with the kill rate, since an
   equivalent mutant is never killed and so $e \le 1-k = 0.1095$. The
   interval for $e$ was computed without that relation. (Round 1, A-B1.)
4. Chebyshev $\sqrt{0.25/(1000 \cdot 0.05)} = 0.071$; normal
   $1.96\sqrt{0.25/1000} = 0.031$ (`netlist-population/run.out`
   line 62).
5. `m32`. A deleted hold synthesizes to the same flop. `m36`'s `<=`
   comparator is structurally different from `==` and survives `opt`, so
   only a proof shows they are the same function
   (`source-mutants/run.out` 69-77).
6. This tool's bounded search knows no completeness threshold, so it
   only refutes, and no trace from reset reaches a state
   where the two differ. The `rd_data` comparison needs an invariant
   relating the memory words between the pointers in both copies (the
   live words equal); `count <= 16` does not state it
   (`equiv-invariant/run.out` 3-6).
7. Pushes decrement and pops increment: 32 - 5 + 2 = 29, so count = 29;
   `full` 0, `empty` 0. The repaired FIFO has count 3, `full` 0, `empty`
   0: the same at the ports.
8. Yes, after the first accepted push (31 against 1).
9. Any of the fifteen data-path mutants `m08`, `m10`, `m14`-`m25`,
   `m33` (for example `m15`, `m16`, `m33`): each changes only which word
   reaches `rd_data`, never the count or the flags. That comparison
   would excuse the whole checking gap of the checking testbench.
   (Rewritten in round 1, A-N19; the old question was the Pitfall's
   own run.)
10. `m13` as well: after three pushes, the count's reset is deleted, so
   the pulse leaves count at 3 and `empty=0`. The pulse's timing is not
   the reason: any second reset after traffic exposes `m13`. `m09` and
   `m11` survive (the count is reset, so `empty` is right; the stale
   pointer shows only on a later push and pop), and `m32`, `m36`, `m43`
   are equivalent under any reset. Checked in round 1 by running the
   built `equiv-reset` schema binary with `+mut=` 0, 5, 9, 11, 13, 32,
   36, 43: killed exactly for 5 and 13. (Rewritten, A-N19.)
11. $1 - 0.47^n \ge 0.99$ gives $n \ge \ln 0.01 / \ln 0.47 = 6.1$, so
   7 seeds. Not independent with one probability: a seed kills `m35`
   exactly when its traffic drains the FIFO after the first push, a
   property of each seed's whole stimulus, so the 100 seeds are 100
   fixed stimuli, not draws of one event; the 0.53 is a frequency over
   these seeds. (Rewritten, A-N19.)
12. $1 - 0.05^{1/1000} = 0.0030$ (the exercise now says it is not the
    two-sided end 0.004 the run prints; A-N20). The testbench has no checker, so its
    true kill rate is zero by construction; the bound only describes the
    sample.

## 7. Final checks

- Word count: 13,812 by `wc -w` on the source (markup included), the
  measure ch21's log uses; 13,108 excluding fenced blocks and attributes.
- `scripts/check-structure.sh`: "every chapter keeps the template".
- `scripts/check-citations.sh`: check 1, no swallowed references.
  Check 2 run against a pandoc plain-text render of the chapter: of the
  39 keys ch25 cites, all appear except `grosse2007bmccoverage`,
  `just2014mutants` and `petrovic2021mutation`, which are false
  positives from the script's surname extraction on LaTeX-escaped
  accents (`Gro{\ss}e`, `Ren{\'e}`, `Petrovi{\'c}`); the render contains
  "Große", "Just, René" and "Petrović".
- Includes expanded by script (53 code splices, 3 table includes), every
  line range asserted within its file. The check caught one stale range
  (`tb_async_reset.sv` 64-81 in a 38-line file), corrected to 20-37.
  The first and last line of every splice were read against the prose.
- Pandoc 3.1.3, `--citeproc --bibliography refs.bib`, to HTML, LaTeX and
  plain: no citation warnings other than the `@sec-`/`@fig-`/`@tbl-`
  cross-references, which only Quarto resolves; one "could not convert
  TeX math" note for `1/\sqrt{n}` in HTML and plain (no MathML engine in
  bare pandoc). Quarto is not installed here, so the book was not built.
- `refs.bib`: 26 new entries (432 to 458), no duplicate keys; DOI
  entries carry no URL; `note` fields do not print under the book's
  style (checked in the render).
- Glossary: 16 entries added to `appendices/appG-glossary.qmd` in
  alphabetical place; existing "Miter" and "Mutant (design)" unchanged.
- Grep of the chapter, figure script, SVGs, glossary, `refs.bib` and
  `_quarto.yml` for the assistant's or vendor's name: none. No
  hard-coded chapter, section, figure or table numbers. No British
  spellings found.

## 8. Round 1 fixes (gate 2, 2026-11-16)

Reviews: `docs/reviews/ch25-gate2a-2026-11-16.md` (text, A) and
`docs/reviews/ch25-gate2b-2026-11-16.md` (code, B). Every changed
example was run twice from clean (build directories and `__pycache__`
removed) with `scripts/check-examples.sh ch25-mutation-testing`: 17 of
17 pass both times, and every `run.out`, generated table, `measure.out`
and `pop.tsv` of the second run is byte-identical to the first's
(`netlist-formal` was run a third time from clean after its last edit,
identical).

### Blocking

- **A-B1** (ratio of interval ends). The text now says the division is
  sound (the score is monotone in $k$ and $e$) and that the fault is
  the interval for $e$, computed without $k \le 1-e$: with $k = 0.8905$
  known exactly, $e \le 0.1095$, so 0.126 is impossible. Changed in the
  sampling section, the summary bullet, Exercise 3's question, and its
  answer in section 6 above.
- **A-B2 + B-B1** (`m05` and the reset model). Measured: on the `m05`
  miter, `cover {!rst_n}` is unreachable and `assert {rst_n}` is proven
  by rIC3. `equiv-reset/reset.py` now runs both and pins them; its
  docstring no longer says the tool "models an asynchronous reset as
  one seen at the clock". The chapter states the mechanism (reset at
  the start of every trace, `rst_n` high after it, so no second reset)
  on that run (`equiv-reset/run.out` 1-13), says the simulator *does*
  distinguish `m05` and the testbenches hide it by their stimulus, and
  the equivalent-mutant Definition now names the tool's reset model
  (`@sec-ch09-formal`) as part of the definition. Objective 4 and the
  glossary's "Equivalent mutant" say the same. Note for the author:
  Chapter 9's "The tool models every reset that way, including the
  asynchronous resets" (line 357) is about the initial reset and is not
  contradicted, but a reader could take it to cover mid-trace resets;
  Chapter 9 was not edited (out of scope).
- **A-B3** (netlist-formal splice). `nformal.py` now prints the 14
  misses (mutation, mode, line, cell, miter depth, random-test verdict)
  and the depth split, pinned: 14 misses, all killed by the random
  test, misses at 16-31, `a_integrity` kills at 15 or less. The
  reviewer's "every kill at 15 or less" was not quite right: two flag
  kills (rows 2039, 2083) are at 17 and 18, so the run prints both
  numbers and the text says so. The chapter splices that block
  (`run.out` 16-33) instead of `measure.out` 83-94, and the reruns
  (34-39) where the text mentions them. "Ten of the fourteen" are on
  lines 42/43 (counted from the block).
- **A-B4** (37/40 of 44). `fifth-tb` gained `fifo_port_bind.sv`, which
  binds the ch09 checker with its `count` input tied to the checker's
  own `occ`, so `Sync_A` cannot fail and every other property judges
  the ports. With it the fifth testbench kills 36/44 (default) and
  39/44 (randomized); the only kill made by `Sync_A` alone is `m44`;
  non-equivalent 36/39 and 39/39. Printed and pinned
  (`fifth-tb/run.out` 23-29) and spliced in Step 5, whose sentence now
  reports port kills, the white-box `m44` kill and the score
  separately. (A scratch run first showed that with `Sync_A` present,
  the first failing assertion of 14 non-equivalent mutants' runs is
  `Sync_A`, so the port count could not be read off the old run.)
- **B-B2** (coverage wording). "same line, branch and expression
  coverage ... three more toggle points", "between 98.8% and 99.7%",
  "equal to within three toggle points"; the splice is widened to
  `opening/run.out` 14-24 so the one-decimal toggle lines show; the
  example's verdict line no longer says "equal code coverage".

### Non-blocking, taken

- A-N1: as B-B2.
- A-N2: the mode paragraph states both (random a few points, directed
  a factor of 2.6).
- A-N3: "most properties earn their place", with the three that kill
  nothing alone named, checked against `property-set/measure.out`.
- A-N4: `m44` is "under a reachable-state invariant relating the
  copies" in the text, the summary, the survivors table (`rand-init`
  `CLASS`) and the matrix figure's legend.
- A-N5: "a bounded search that does not know a completeness threshold
  (`@sec-ch18-bmc`)" at objective 4, the miter Definition, the
  undecided-mutants sentence and Exercise 6.
- A-N6: the weighting is attributed to the `mutate` pass, via MCY's
  documentation of it (`mcy-docs`, mutate.html); "even" explained.
- A-N7 and B-N4: `pop.py` now computes the exact coverage under the
  draw it makes (without replacement, hypergeometric) and prints it
  beside each Monte Carlo value, plus the standard error 0.005; pinned
  that every exact coverage is at least 0.95 and every estimate within
  2.5 standard errors. Directed at n = 100: 0.945 estimated, 0.954
  exact. The text says so, and the hypergeometric clause is added
  where the binomial model's assumptions are discussed.
- A-N8: one framing for `m06`/`m07`: refused by the formal front end
  and by Yosys, a kill by the flow, counted apart, never a
  counterexample.
- A-N9: the `m32` proof named as the self-comparison control.
- A-N10: white-box splice widened to 3-32, "both verdicts".
- A-N11: the missing occupancy level is named and explained.
- A-N12: "the sequential form of the miter"; glossary "Miter" gains a
  sentence for the sequential case pointing to `@sec-ch25-equiv`.
- A-N13: the sampling figure takes the population rate from the count
  (8265/9281 = 0.891), not the printed 0.8905.
- A-N14: the RIP figure has a fourth bar (directed test, killed);
  caption and alt text updated.
- A-N15: limited to the three vendor sources read.
- A-N16: Hoskote et al. cited at title level only. The same treatment
  for Al Hayek and Robach, and Serrestou et al., which were also not
  opened ("applied it to HDL descriptions" removed).
- A-N17: "which this chapter counts as conditional changes".
- A-N18: the two unwritten chapters are named as where things belong,
  not as present-tense content.
- A-N19: Exercises 9-11 rewritten to need reasoning; answers above.
  Exercise 10's answer (`m13` is killed too) was checked by running
  the built schema binary.
- A-N20: Exercise 12 names the two-sided end it does not ask for.
- B-N1: `mutlib.pin_measured` pins every committed `measure.out` and
  `pop.tsv` by SHA-256 in the default run of the example that reads it
  (`source-sim`, `property-set`, `netlist-population`,
  `netlist-formal`); under `MEASURE=1` it prints the new digest instead.
- B-N2: `source-sim`'s writer now wraps its build and control lines;
  `MEASURE=1` was rerun (12 min under load): the per-mutant matrix and
  control are identical, the build line is now 2855 s summed / 721 s
  wall (was 1685 / 427; the machine was loaded), re-pinned, spliced as
  3-4. For `netlist-formal` the chapter now splices the settings and
  cost from the default run's `run.out` (41-43, wrapped), so no
  `measure.out` line over 80 columns is spliced. Its `MEASURE=1` run
  was **not** repeated: its 3 s bounded searches stop at the depth
  15/16 boundary the chapter discusses, so a rerun under different load
  could move rows and change the printed 80/94 and 14 for a formatting
  fix; its unspliced row lines stay over 80 columns.
- B-N3: the docstring and the text say 31 is rIC3's trace length and
  bounds the first difference from above (the reviewer's 29 was not
  re-measured here, so it is not printed).
- B-N5: `miter.refusal` subtracts the header line `srcmut.single`
  adds: the refusals now say line 37, as the source list does. The
  committed `property-set/measure.out` (unspliced lines 16-19) still
  says 38, since its `MEASURE=1` run was not repeated.
- B-N6: `netlist-list` labels the count "on the memory's lines" and
  says lines 36 and 42 also hold pointer and count registers and the
  write pointer's enable; the text says "about three quarters of the
  netlist mutations sit on the memory's lines".
- B-N7: the figure generator's checks raise `SystemExit` through
  `check()`; no `assert` left. Run with `python3 -O` as well.

### Figures

Re-pinned to the new `run.out` files; regenerated; rip, matrix and
sampling changed (axes identical). Rendered to PNG with headless
Chrome and checked as images: the fourth RIP bar and its label, the
matrix legend's new label within the width, the 0.891 label.

### Checks

`scripts/check-structure.sh`: every chapter keeps the template.
`scripts/check-citations.sh`: no swallowed references. Includes
expanded by script: every range within its file, every spliced line
at 80 columns or less. Pandoc 3.1.3 with `--citeproc` to HTML
(MathJax) and LaTeX: no warnings other than the Quarto
cross-references.

## 9. Round 2 fixes (gate 2, 2026-11-16)

Reviews: `docs/reviews/ch25-gate2c-2026-11-16.md` (text, C-B1 and
N1-N13) and `docs/reviews/ch25-gate2d-2026-11-16.md` (code, B1-B3 and
N1-N2). Every finding is fixed; none left.

### Blocking

- 2d B1: `figures/gen_ch25_figures.py` re-pinned `source-sim/run.out`
  to `c03da492...54c332`. Regenerated under `python3` and `python3 -O`:
  all four SVGs byte-identical to the committed ones. (The axes
  footnote was then reworded for 2c N2, which changes only that text
  line of `ch25-axes.svg`.)
- 2c C-B1: lines 34 and 39 no longer say the covergroup reports the
  same percentages on any FIFO. Line 34: "reports percentages and never
  a failure, whether the FIFO is correct or broken". Line 39: the even
  mix gives the same 75.86 as the coverage chapter's original
  (`ch08-functional-coverage/fifo-coverage/run.out` 2, `opening/run.out`
  7); the push-biased mix gives 89.66 against 86.21 (`fifo-coverage`
  15, `opening` 8), because the monitor counts a push only while `full`
  is low, so the bin for sixteen entries stays empty on the original
  (the coverage chapter's "still zero after the merge: full_16") and
  fills on the repaired FIFO. Checked in a scratch run of the coverage
  chapter's runner against `fifo_fixed.sv` (not committed): run A
  identical bin for bin, 75.86; run B 89.66, `full_16=136`, "push
  while full at occupancy 16", every other bin hit in both designs.
- 2d B2 / 2c N1: summary "the random test, with the same line, branch
  and expression coverage, kills 35".
- 2d B3 / 2c N2: line 157 "for this chapter's copy of the test at
  `+seed=1` and 400 cycles"; the axes figure's footnote "each testbench
  was run as the chapter configures it".

### Non-blocking

- 2c N3: line 23 "never holds sixteen entries".
- 2c N4 / 2d N1: Step 3 splices `fifth-tb/run.out` 7-22, so the
  ports heading appears only under Step 5.
- 2c N5: `nformal.py` prints "(the property set's kills: 18 or less)".
  Formatting of committed `measure.out` data only; the same two lines,
  so no splice moved. No `MEASURE=1` rerun.
- 2c N6: line 464 "what three seconds of bounded search on
  `a_integrity` reaches on this design".
- 2c N7 (bounds, not gaps): demonstrated rather than softened. The
  default run of `netlist-formal` now runs `a_integrity` alone on each
  of the fourteen misses, bounded search for 30 s, then rIC3 for 120 s
  if that finds nothing. Bounded search refutes twelve, each at exactly
  its miter depth (7 at 16, 4 at 17, 1 at 18; pinned per mutation);
  rIC3 refutes 7759 at 29 and 8394 at 31 (trace lengths, upper
  bounds). In a probe, 60 s of bounded search did not reach those two.
  Cost: about 45 s more (the deep two start first); the default run
  is now about a minute and a half (docstring, Makefile). Printed as
  `run.out` 40-43, spliced with the rIC3 reruns (34-43); the settings
  splice moved from 41-43 to 45-47. Text at 327, 459, 464-469 says the
  run shows it; summary 557 unchanged and now rests on the run.
- 2c N8: `fifth.py` runs the port bind on the 1,000-mutation netlist
  sample too: 899/1000 at the ports, 0 killed only by `Sync_A`
  (pinned). Printed as `run.out` 30-31; Step 5 splices 23-31; line 533
  adds "all of them at the ports". About 20 s more (docstring and
  Makefile updated).
- 2c N9: line 488 "The commercial tool Lin and colleagues use".
- 2c N10 / 2d N2: line 309 "the first property tried that fails it,
  `FullBackward_A`, needs eighteen cycles".
- 2c N11: line 245 "A testbench that does not, and instead pulses the
  reset between two edges and looks at the FIFO before the next one,
  tells them apart:".
- 2c N12: line 440 "The output of `mutate -list N` may be ...".
- 2c N13: alt text "toward reveal".

### Checks

`scripts/check-examples.sh examples/ch25-mutation-testing` from clean
(build directories and caches removed first): 17 of 17 pass. Changed
outputs: `fifth-tb/run.out` (two new lines, checks 10 of 10) and
`netlist-formal/run.out` (the N5 wording, four new lines, checks 14 of
14, verdict reworded); every other `run.out`, table, `measure.out` and
`pop.tsv` unchanged. Includes expanded by script: every range inside its
file and on the intended lines, every spliced line at 80 columns or
less. `scripts/check-structure.sh` and `scripts/check-citations.sh`
pass.

## 10. Round 3

Text (`docs/reviews/ch25-gate2e-2026-11-16.md`) and code (`ch25-gate2f`)
both pass with no blocking finding. Non-blocking notes taken:

- E-N1: the sentence on the bin for sixteen entries no longer says it
  fills on the repaired FIFO, which no committed output prints; it says
  the bin can be hit there.
- E-N2: the netlist sampling paragraph now names the `a_integrity`
  rerun of the fourteen misses.
- E-N3: "the five survivors at the ports" is qualified to the
  randomized run.
- F-N1: the `a_integrity` rerun's bounded search limit is raised from
  30 s to 60 s, doubling its margin over the slowest job (8.5 s here);
  `run.out` line 41 changes only in that number.
- F-N2: the depth-15/16 split is stated as this machine's result, since
  the twelve shallow misses take 3.1 to 8.5 s against the measured
  run's 3 s.
