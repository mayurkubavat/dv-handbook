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
3. 0.947 at 0.060; 0.911 at 0.022; 1.019 at 0.126. A "score" above one:
   the ratio of interval ends is not an interval for the ratio.
4. Chebyshev $\sqrt{0.25/(1000 \cdot 0.05)} = 0.071$; normal
   $1.96\sqrt{0.25/1000} = 0.031$ (`netlist-population/run.out`
   line 62).
5. `m32`. A deleted hold synthesizes to the same flop. `m36`'s `<=`
   comparator is structurally different from `==` and survives `opt`, so
   only a proof shows they are the same function
   (`source-mutants/run.out` 69-77).
6. Bounded search only refutes, and no trace from reset reaches a state
   where the two differ. The `rd_data` comparison needs an invariant
   relating the memory words between the pointers in both copies (the
   live words equal); `count <= 16` does not state it
   (`equiv-invariant/run.out` 3-6).
7. Pushes decrement and pops increment: 32 - 5 + 2 = 29, so count = 29;
   `full` 0, `empty` 0. The repaired FIFO has count 3, `full` 0, `empty`
   0: the same at the ports.
8. Yes, after the first accepted push (31 against 1).
9. Differs at depth 1 (`miter-differ/run.out` 53): the memory is not
   reset, and the two copies' words start free.
10. Yes: `empty=0` on `m05`, killed (`equiv-reset/run.out` 10-11).
11. Seed 2 (`source-sim/run.out` 61-62).
12. $1 - 0.05^{1/1000} = 0.0030$. The testbench has no checker, so its
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
