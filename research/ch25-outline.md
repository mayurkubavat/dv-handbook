# Outline: Mutation Testing: Qualifying the Testbench

Date: 2026-11-16. Status: outline for gate 1. Evidence:
`research/ch25-mutation-testing.md` (cited as RN with its question,
measurement or section number: Q1 to Q7, M1 to M9, RN 3.n, RN 6 for
confidence notes, O1 to O6 for its open questions) and its scripts and
saved outputs under `research/ch25-measurements/<name>/` (cited as
`<name>/<file>:<lines>`, line numbers counted within that file).
Chapter file `chapters/ch25-mutation-testing.qmd`, label `{#sec-ch25}`;
third chapter of the part "Borrowed from Software", after Property-Based
Testing for Hardware and Fuzzing Hardware and before Hardware
Construction Languages and Compiler IRs (design doc section 4, entry
25: "fault models, equivalent mutants, kill rate beside coverage; MCY
on the book's designs"). The part is not yet in `_quarto.yml`: the
drafter adds `part: "Part V · Borrowed from Software"` between "Part
IV · Proof and Probability" and "Part VII · The Future of
Verification", with this chapter as its first written chapter, always
before `chapters/ch34-generative-ai-agentic-dv.qmd`.

Section 1 records the decisions handed to this outline and, in 1.2,
**the places where the evidence contradicts or qualifies one of
them**. Read 1.2 first. None of them changes the chapter's shape; two
change how an example must be built (1.2(6), 1.2(7)), and one changes
how a number must be computed (1.2(4)).

(Written section by section, in the order 0, 1, 2, 3, 4, 5, 6, 7, 8,
9.)

## 0. The chapter in one paragraph

Every earlier chapter that touched the FIFO measured something about
its testbench: what the stimulus reached (`@sec-ch08-example`), what
the checker asserted (`@sec-ch09-example`), what a property set proved
(`@sec-ch19-mutation`), how many clean seeds bound a failure rate
(`@sec-ch21-clean`). None measured whether the testbench would fail if
the design were wrong. This chapter does, by planting small bugs
(mutants) in the repaired FIFO and counting which of the book's own
four testbenches and its formal property set notice them. It opens
with the one table that makes the point: Chapter 8's coverage
testbench reaches 100% line, branch and expression coverage of the
FIFO and kills none of 44 mutants, as it must, because it has no
checker by design and Chapter 8 says so; Chapter 1's directed test, at
24% toggle coverage, kills 34. Kill rate and coverage are different
axes, and the chapter's job is to make the first as well understood as
the second. It teaches two fault models on the same file, 44
source-level operators a reader can read one by one and then 9,281
single-bit netlist mutations from Yosys's `mutate` pass, the fault
model MCY packages; it classifies every survivor with a hand-built
miter on InFormal into real gaps (stimulus, checking, or the
simulator's initial values) and three kinds of equivalent mutant
(outright, under a reachable-state invariant, under the tool's reset
model), plus one equivalent mutant that a white-box assertion kills;
it runs the property set as a fifth judge; it estimates kill rate and
equivalent fraction from samples with the Clopper-Pearson interval of
`@sec-ch21-clean`, checked against a population whose truth is known;
and it closes the gap it found by adding a data check and rerunning.
The software evidence on whether mutants stand for real faults is
reported with its limits, and nothing from it is transferred to RTL as
a number.

## 1. Decisions

### 1.1 Taken (handed to this outline, or taken here)

| # | decision | basis |
|---|---|---|
| D1 | Spine: the repaired FIFO, `examples/ch09-temporal-properties/rtl/fifo_fixed.sv` read by path, with the book's four testbenches (Chapter 1 directed, Chapter 1 random at `+seed=1`, Chapter 8 coverage runs A and B, Chapter 9 checker bound) and Chapter 19's `mutants/` property set, all read by path; the chapter opens with kill rate beside coverage, Chapter 8's testbench presented fairly (no checker by design, as `@sec-ch08-example` says: "nothing in the file checks the FIFO") | handed; RN Q2, RN 4 |
| D2 | Fault models: source-level operators first (3.3), then Yosys netlist mutations with sampling (3.8, 3.9) | handed; RN Q1 |
| D3 | MCY named and its mechanism taught (`mutate -list`, `mutate -ctrl`, the miter filter, its four tags); the examples run Yosys's `mutate` pass and hand-built InFormal miters; MCY is not a dependency, and the text says why in one plain sentence (its documented equivalence step runs SymbiYosys, which the book replaced with InFormal) | handed; RN Q5, O1; qualified in 1.2(3) |
| D4 | Equivalent mutants in three kinds (outright: `m32`, `m36`; under a reachable-state invariant: `m43`; only under the tool's reset model: `m05`) plus `m44`, equivalent at the ports and killed by `Sync_A`, as the lesson that an implementation-constraining assertion kills an equivalent mutant | handed; RN Q3, Q4, M3, M4; qualified in 1.2(2) |
| D5 | Kill rate and equivalent fraction reported separately, each with its Clopper-Pearson interval, and the score derived from them | handed; RN Q6, O4; qualified in 1.2(4) |
| D6 | A fifth testbench with a data check closes the gap in the worked example (3.11) | handed; RN O2; must be measured (section 9) |
| D7 | FIFO only; the DMA of `@sec-ch11` appears at most as a pointer in Future Directions (no exercise: none with a determinate answer exists without a measurement) | handed; RN O3 |
| D8 | LLM-based mutant generation and equivalence classification: one compact subsection inside Future Directions, cited only to sources opened (section 7), handing off to Machine Learning in Verification and Generative AI and Agentic DV by name; no new measurement | handed; RN 3.9, O5 |
| D9 | The three reset-deletion survivors (`m09`, `m11`, `m13`) are a Pitfall about the simulator's default initial values, with the measured randomized run | handed; RN Q4, M7; qualified in 1.2(5) |
| D10 | The two harness defects found in research (Verilator turning Yosys's `parallel_case` into an assertion; a duplicated `+seed=` plusarg resolved to its first occurrence) are taught as Pitfalls of building a mutation harness, each with a small runnable demonstration | handed; RN M6a, RN 2.2(4) |
| D11 | Every example runs under about 90 s on the book's machine; populations are split or sampled to fit, and each full-population run is a `MEASURE=1` opt-in when longer | handed; qualified in 1.2(6), (7) |
| D12 | Numbers in prose are spliced from the example's own `run.out`; the research lines cited below are evidence that the example will print a number of that size, not text to copy | house rule |
| D13 | Verilator 5.052, Yosys 0.68 (git 38e001a6f), InFormal 0.1.0 at `5114330` with rIC3, Python 3.13 standard library, as pinned in RN; every tool-derived block prints the version it ran on | RN pins; RN O6 (5.054 not used) |
| D14 | Definitions follow the peer-reviewed literature (Jia and Harman's survey, read); the vendor's activation / propagation / detection triple appears only as the vendor's, beside the peer-reviewed reach / infect / propagate (/ reveal) conditions, never as the definition | RN 3.1; house rule on vendor claims |
| D15 | Equivalence is defined by what the miter compares (full and empty always, `rd_data` whenever the original is not empty), and the comparison is printed as part of the Definition callout | RN Q3, RN 3.8(1) |
| D16 | Epigraph is the book's own sentence | no checked quotation planned |

### 1.2 Where the evidence contradicts or qualifies a handed decision

Nothing below changes the sections or their order; each item changes a
sentence, a number, or how an example is built, and is settled here
under the delegation.

1. **D1, "full code coverage".** The coverage testbench's run on the
   repaired FIFO reaches line 4/4, branch 6/6 and expression 8/8, but
   toggle 326/330 (99%), not 100% (`coverage/run.out:8`); the four
   "lines" are Verilator's coverage points for the module, not source
   lines. **Settled:** the chapter says "every line, branch and
   expression point and 99% of toggles", and explains in one sentence
   what a Verilator line point is (citing `@sec-ch08-code-coverage`,
   not repeating it). The fairer comparison than coverage-vs-directed
   is also on the table and the text uses both: Chapter 1's random
   test has the same code coverage as the coverage testbench (line,
   branch, expression 100%, toggle 329/330, `coverage/run.out:5`) and
   kills 35 of 44 (`src-mutants/run_sim.log:4`), so two testbenches
   with identical code coverage sit at opposite ends of the kill
   axis. The functional-coverage percentages (75.86 and 89.66,
   `coverage/run.out:6-7`) are for the *repaired* FIFO and differ from
   the ones Chapter 8 prints for the original; the chapter splices its
   own and says which RTL they are for.
2. **D4, `m05` "only under the tool's reset model".** The evidence
   supports a slightly wider statement. `m05` (the asynchronous reset
   made synchronous) is proved equivalent by rIC3 because InFormal
   models an asynchronous reset as synchronous (RN 3.8(3), FINDINGS
   D.3 as cited there); but *no simulation testbench* kills it either,
   with zero or randomized initial values (`src-mutants/sim.tsv:7`,
   `rand_init.log:3`), because every book testbench asserts reset
   across a clock edge. So the class is "equivalent only under a
   cycle-level model in which reset is seen at the clock", and both
   judges here share that model. **Settled:** the class keeps D4's
   name in the text ("equivalent only under the tool's reset model"),
   the paragraph adds that the book's testbenches share the
   assumption, and a short measurement before drafting (section 9,
   P8) checks that a testbench which pulses `rst_n` between edges and
   reads `empty` before the next edge kills `m05` in Verilator; if it
   does, that becomes exercise 10 and the sentence "the designs are
   not equivalent in silicon" rests on it; if it does not, the
   sentence is cut and the class is described only as what the tool
   assumes.
3. **D3, "MCY needs SymbiYosys".** MCY's own test step is any script,
   and only its *documented equivalence step* runs SymbiYosys (the
   example `[script]`s and AppNote 400 both use `sby` in BMC mode;
   RN 3.6, MCY docs as read; section 7). MCY therefore could be run
   with the book's testbenches and an InFormal miter in place of the
   SBY step (RN O1's "cheapest path"). **Settled:** the sentence the
   chapter prints is "MCY's documented equivalence filter runs
   SymbiYosys, which this book replaced with InFormal, so the
   examples reproduce MCY's mechanism with Yosys and InFormal directly
   rather than adding MCY and SymbiYosys to the toolchain", not "MCY
   requires SymbiYosys". The design doc's "MCY on the book's designs"
   is read as "MCY's method on the book's designs"; this is a reading
   under the author's "choose on your own", recorded here so the
   author can overrule it (it does not change any section). A fact
   the drafter should know: an `sby` binary is present in
   `/opt/dvtools/bin` on this machine, so "not installed" would be
   false for SymbiYosys; the reason not to use it is the book's
   2026-11-15 decision, and the chapter says that, not that the tool
   is unavailable. MCY itself is not installed (RN Q5).
4. **D5, "the derived score".** The naive derivation misbehaves on the
   measured numbers. The population kill rate of the random testbench
   is 0.8905 (`sampling/run.out:3`); the formal sample's equivalent
   fraction is 0.060 with interval [0.022, 0.126]
   (`sampling/run.out:24`). Dividing, kill / (1 - e) is 0.947, and
   the same division at the interval's ends gives 0.911 and **1.019**,
   a "score" above one. Meanwhile the same formal sample estimates the
   score directly, as kills among the sampled mutants the miter called
   non-equivalent: 93 of 94, 0.989 [0.942, 1.000]
   (`sampling/run.out:26`). The two point estimates differ (0.947 vs
   0.989), both legitimately, because one combines a population rate
   with a sampled e and the other is one sample's conditional rate.
   **Settled:** the chapter reports (a) kill rate over all mutants
   with its interval, (b) equivalent fraction with its interval, and
   (c) the score computed *directly on the jointly classified sample*
   (kills among non-equivalent sampled mutants, Clopper-Pearson on
   that count), because a uniform sample's non-equivalent members are
   a uniform sample of the non-equivalent population. The ratio
   kill / (1 - e) is shown once as a point estimate, its interval-end
   arithmetic (the 1.019) is the cautionary line, and exercise 3 asks
   for it. This keeps D5 (separate reports, a derived score) and
   corrects only how the score is derived.
5. **D9, "Verilator's zero initialization": the zeros come from a
   runtime default, not from the build.** The measurement shows that
   the three reset-deletion mutants survive under the book's flags and
   die with `--x-initial unique` plus `+verilator+rand+reset+2`
   (`rand_init.log:4-6`). The Verilator 5.052 documentation, read for
   this outline from the release's own `docs/guide/exe_verilator.rst`
   and `exe_sim.rst` (section 7), says that `--x-initial unique` *is
   the default*, that it initializes variables "using a function"
   meant for "finding reset bugs", and that the runtime option
   `+verilator+rand+reset+<value>` chooses what that function returns:
   0 "Reset to zeros" (the default), 1 all ones, 2 "Randomize"; and
   that `--x-initial fast` "will likely hide any code bugs relating to
   missing resets". The input-languages page adds that state-holding
   variables are "initialized to a random value". So the zeros are the
   default value of a *runtime* plusarg, and the compile flag in RN M7
   is redundant. **Settled:** the Pitfall says that by default the
   simulator's initialization function returns zero, so a register
   whose reset was deleted starts where the reset would have put it;
   that the documented remedy is `+verilator+rand+reset+2` with a
   varied `+verilator+seed+`; and it cites `verilator-exe-verilator`
   and `verilator-exe-sim` (both already in `refs.bib`). It does not
   say "Verilator zero-initializes" as if it were the language's or
   the tool's guarantee. Precondition P4 (section 9) reruns M7 without
   `--x-initial unique` to confirm that the plusarg alone kills the
   three mutants; the example then uses the book's flags unchanged
   plus the plusarg.
6. **D11 and the source-mutant examples: per-mutant builds cannot fit
   90 s.** The research built each source mutant separately: 180
   builds, 1,704 s of build time for 1.1 s of simulation, 433 s wall
   on four cores (`src-mutants/run_sim.log:8`). Splitting cannot
   bring that under 90 s (one build is about 9.5 s; 44 builds for one
   testbench alone exceed it). **Settled:** the default run of
   `source-sim/` builds a *source-level schema*: one generated copy of
   the FIFO in which every one of the 44 edits sits behind a run-time
   select read from a plusarg, so each testbench is built once and
   run 45 times, which is the schemata idea of Untch, Offutt and
   Harrold that 3.8 teaches for the netlist. The per-mutant build is
   kept as `MEASURE=1`, and it prints a line that compares its 44 x 4
   verdict matrix with the schema's; the chapter splices that line
   from a committed `measure.out` (see section 4). Three edits need
   care in a schema and are a precondition (section 9, P1): `m05`
   (the sensitivity list: one `always_ff` with an effective async
   reset that is held inactive when `m05` is selected), `m06`/`m07`
   (reset polarity: legal in Verilator, refused by InFormal's front
   end, which concerns only `property-set/`), and the seven edits
   that draw `-Wall` warnings (`src-mutants/sim.tsv:17,20,25,29,32,37,40`),
   which in a schema must not make the whole schema fail lint; the
   lint verdict of each mutant is therefore measured separately in
   `source-mutants/` by linting the 44 single-edit copies, which is
   fast (lint only, no C++ build). If the schema's verdict matrix
   differs from the per-mutant matrix anywhere, the schema is wrong
   and the drafter fixes it before splicing anything.
7. **D11 and the formal examples: equivalence needs rIC3, and rIC3 is
   not in CI.** Every "equivalent" verdict came from rIC3 after
   InFormal's in-house IC3 gave none in 30 s (`formal/src_formal.tsv`,
   `miter_s` column 58-66 s, which is BMC 10 s + in-house IC3 30 s +
   rIC3; RN M3). So the equivalence examples must select `ric3-ic3`
   directly (about 20 s each by RN M3, to be re-timed alone) and
   declare `REQUIRES := ric3`, which `check-examples.sh` skips where
   the program is absent, as the Chapter 18 examples already do. The
   chapter says in a sentence that the equivalence verdicts rest on
   rIC3 (`@su2025ric3`) and that BMC alone can only ever report
   "differs". The property-set run (468 s wall with the miters,
   `formal/run_src.log:7`) is re-planned as depth-bounded BMC with a
   per-mutant stop at the first failing property in the default run
   and the full per-property matrix under `MEASURE=1`; the formal
   netlist sample (780 s wall, `formal/run_ysample.log:7`) is
   `MEASURE=1` only, with its summary spliced from a committed
   `measure.out`, and a short default run that re-proves two of its
   six equivalents and refutes two of its deep non-equivalents so that
   the default run still exercises the mechanism (section 4).
8. **D6, "closes the gap": which gap.** The measured gap of the
   Chapter 9 checker is the data path: it kills none of `m14`-`m25`
   and `m33` (`src-mutants/sim.tsv:16-27,35`) and 3.8% of netlist
   mutations, three quarters of which carry the memory's source lines
   (RN M6). Chapter 1's random test already has a data check and
   kills 35 of 44, so the fifth testbench is **Chapter 9's traffic and
   checker plus a data check**, which also drains the FIFO and so
   kills `m35` (which random seed 1 misses). Its expected result,
   from the union of the measured columns, is 37 of 44 under the
   default initial values (every non-equivalent mutant except `m09`,
   `m11`, `m13`, plus `m44` through `Sync_A`) and 40 of 44 with
   randomized initial values; on the netlist sample, near the random
   testbench's rate or above. None of this is measured yet; it is
   precondition P5, and the section's sentences are written from its
   `run.out`, whatever it prints. "Closes the gap" therefore means the
   data-path gap; the reset gap closes only with randomized initial
   values, and the text says so instead of claiming a perfect score.

### 1.3 Escalation check

No item above suggests an earlier approved chapter is wrong. Two
points touch earlier chapters and are recorded so the drafter does not
create a contradiction:

- `m44`'s kill by `Sync_A` does not make Chapter 9's checker wrong.
  Chapter 9 introduces `Sync_A` as "cheap insurance against a mistake
  in `occ`" and says it is the only place the design's internal
  `count` is read (`@sec-ch09-example`). This chapter adds what that
  choice costs under mutation (it also constrains the implementation),
  and says the remedy is to report such kills separately, not to
  delete the assertion.
- Chapter 21's worked example states that Chapter 9's checking
  testbench drains the FIFO for 200 cycles (`@sec-ch21-example`); this
  chapter's `m35` result (killed by the Chapter 9 testbench, missed by
  Chapter 1's random seed 1, `src-mutants/sim.tsv:37`) is consistent
  with it.

## 2. Front matter

**Epigraph (own words; drafter may improve):**
> A testbench that cannot fail has told you nothing, however much it
> covered.

**Learning objectives.** After this chapter you can:

1. say what it means for a testbench to kill a mutant, and why a kill
   rate and a coverage figure measure different things, using the
   FIFO's four testbenches as the example;
2. generate source-level mutants of an RTL file with a stated operator
   set, and name the bug each mutant stands for;
3. classify a surviving mutant as a stimulus gap, a checking gap, a
   simulator-model artifact, or an equivalent mutant, using the reach,
   infect and propagate conditions and a formal miter;
4. build a miter of a design and its mutant, decide what it must
   compare, and read its verdict, knowing that bounded search can only
   refute equivalence;
5. distinguish equivalence outright, under a reachable-state
   invariant, and under a tool's model, and recognize a white-box
   assertion that kills an equivalent mutant;
6. run a formal property set as a judge of mutants and read its
   survivors as gaps in the specification;
7. generate a netlist mutation population with Yosys's `mutate` pass,
   run it as one schema build, and explain what MCY adds to that
   mechanism;
8. estimate a kill rate, an equivalent fraction and a mutation score
   from samples, each with an interval, and say what the binomial
   model assumes about how the sample was drawn;
9. recognize the harness defects that make kills appear or disappear,
   and state what the software evidence on mutants and real faults
   does and does not license for hardware.

Word budget for title, epigraph and objectives: 300.

## 3. Sections

Budgets sum to about 14,300 words (band 13,500 to 15,000; Chapter 21
is about 16,000, and this chapter reuses its interval by label rather
than re-deriving it). Example paths are under
`examples/ch25-mutation-testing/` (section 4). Evidence is cited as
research files and lines; in the chapter every number is spliced from
the example's own `run.out` (D12). Figures are written by
`figures/gen_ch25_figures.py`, one function each, reading the named
example's `run.out` or a small `data.tsv` it writes, with the
`figures/blocks.py` palette, at most 1000 px wide. Mutant names
(`m01`-`m44`) are the generator's stable identifiers and are printed by
the example; the chapter refers to a mutant by name and by its one-line
description together ("`m35`, `empty` stuck low"), never by name
alone.

### 3.1 Motivation: kill rate beside coverage {#sec-ch25-motivation} (~900 words)

- **Content.** One table first, spliced: four testbenches as rows;
  columns line / branch / expression / toggle coverage of
  `fifo_fixed.sv`, the covergroup percentage where there is one, and
  kills out of 44 source mutants. Evidence: `coverage/run.out:1-14`
  for coverage, `src-mutants/run_sim.log:3-7` for kills. The reader
  is asked to predict the kill column from the coverage columns
  before reading it. Then the reading: the coverage testbench (every
  line, branch and expression point, 99% of toggles, 75.86% and
  89.66% functional) kills 0; Chapter 1's directed test (toggle 24%)
  kills 34; Chapter 1's random test, with the same code coverage as
  the coverage testbench, kills 35. The fair statement about Chapter
  8's testbench, in its own words: it was written to measure stimulus
  and has no checker (`@sec-ch08-example`), so a score of zero is
  the correct result of a correct measurement, not a defect of that
  testbench; what the table shows is that coverage cannot tell a
  testbench with a checker from one without. That is
  `@sec-ch08-where`'s "coverage measures activation only" with a
  number on it, cited and not re-argued. One paragraph on what the
  chapter will do (two fault models, survivors classified, the
  property set as a judge, samples with intervals, a gap closed), and
  the one-sentence claim: a kill rate is a measurement of the
  testbench's ability to fail, reported beside coverage and never
  instead of it.
- **Reader can:** read a table of coverage beside kill rate and say
  which testbench would notice a bug, and why the coverage columns
  could not have told them.
- **Example:** `opening/` (coverage of the four testbenches on the
  repaired FIFO, plus a short schema run that prints the four kill
  counts; or the kill column spliced from `source-sim/run.out`, to
  decide by time, section 4).
- **Figure:** `fig-ch25-axes`: two panels, source mutants and netlist
  sample; x = toggle coverage (or covergroup percentage, one panel
  each is clearer; decide at draft), y = kill rate; four points
  labeled by testbench. Data from `opening/` and `netlist-sample/`.
- **Sources:** by label only (`@sec-ch08-where`, `@sec-ch08-example`,
  `@sec-ch08-code-coverage`, `@sec-ch01-example`, `@sec-ch09-example`).
- **Constraints:** never call the coverage testbench "bad" or
  "broken"; the functional-coverage percentages are those of the
  repaired FIFO (1.2(1)); the chapter does not repeat Chapter 8's
  vendor quotation, it points at it.

### 3.2 Mutants, kills and the two hypotheses {#sec-ch25-concepts} (~1,300 words)

- **Content.** Vocabulary, in the peer-reviewed form (D14), all from
  Jia and Harman's survey as read: a mutant is the design with one
  small syntactic change; a test kills a mutant when its verdict on
  the mutant differs from its verdict on the original; *strong*
  mutation compares outputs, *weak* mutation compares state just after
  the mutated point (Howden, as the survey credits), *firm* in
  between (Woodward and Halewood, as the survey credits); the mutation
  score is killed over non-equivalent mutants (the denominator is the
  point of 3.5 and 3.9). For a testbench, "verdict differs" means the
  testbench's pass/fail result: exit status and the pass line, which
  is how the examples judge. The two founding hypotheses, stated as
  software hypotheses: the competent programmer (faults are small
  deviations), and the coupling effect (tests that catch simple faults
  catch most complex ones), credited to DeMillo, Lipton and Sayward
  and stated in their 1980 Georgia Tech report with Budd (read,
  section 7); the competent-designer reading on the FIFO itself (the
  original bug is one constant, the repair one width; `@sec-ch09-example`).
  Neither hypothesis has been tested on hardware in any source found
  (RN 3.1); the text says so. Then the conditions for a kill: reach
  the mutated point, infect the state, propagate to an output, and
  (in the later RIPR form the 2019 survey reports) have the check
  reveal it. Beside them, in one small table, the vendor's
  activation / propagation / detection, labeled as the vendor's
  (`@hampton2009fq`, already quoted in `@sec-ch08-where`; pointed at,
  not re-quoted). The mapping: code coverage measures reach; nothing
  in a coverage report measures infection, propagation or detection.
- **Definition callouts (3):** mutant and kill (strong / weak);
  mutation score (killed / non-equivalent), with "equivalent" forward
  to 3.5; the reach-infect-propagate-reveal conditions.
- **Reader can:** state when a testbench kills a mutant, compute a
  score from counts, and say which of the four conditions a coverage
  report can show.
- **Example:** none new (the opening table is the worked instance).
- **Figure:** `fig-ch25-rip`: the FIFO's datapath as blocks (pointers,
  memory, counter, flags), one mutant's effect traced through reach,
  infect, propagate and reveal, with the testbench's checker at the
  end; three small markers show where Chapter 8's testbench (no
  checker), Chapter 9's checker (no data check) and Chapter 1's queue
  stop the chain. Drawn by the book, no source redrawn.
- **Sources:** `jia2011survey` (read), `budd1980theoretical` (read;
  new entry, section 7), `demillo1978mutation` (credited as origin;
  **not opened**, so no sentence quotes or paraphrases its text),
  `papadakis2019advances` (RIPR as reported; the survey's own source
  for RIPR not opened), `hampton2009fq` (vendor).
- **Constraints:** no number from Jia and Harman's report of another
  paper unless labeled "as reported by"; Hamlet 1977 named only as
  the other independent origin, at title level (not opened).

### 3.3 Fault model I: source-level operators {#sec-ch25-source} (~1,300 words)

- **Content.** The operator set and why: the five selective operators
  of Offutt et al. reduce to the four with sites in the FIFO (AOR,
  LCR, ROR, a negation operator; ABS has no site), plus statement
  deletion, constant replacement and four HDL-specific ones: variable
  swap, asynchronous-reset sensitivity change, reset-polarity, and
  case-label exchange. Every site of each operator in the module body
  gives 44 mutants (`src-mutants/mutants.tsv`; counts by operator in
  RN M1). The example prints the list as one-line diffs, generated at
  run time from `fifo_fixed.sv` by path, failing if an edit matches
  nothing (the Chapter 19 rule, `@sec-ch19-mutation`). Five are read
  as RTL with the bug each stands for: `m14` (write condition negated:
  a write enable of the wrong polarity), `m35` (`empty` stuck low: a
  comparison against an unsigned zero), `m13` (count reset deleted: a
  missing reset), `m42` (`full` from `>`: an off-by-one), `m44` (case
  labels exchanged: push and pop swapped in the counter). Then two
  facts about the population: (1) lint kills seven before any
  simulation, because the book's `-Wall` turns their warnings fatal
  (UNDRIVEN, WIDTHEXPAND, UNSIGNED; `src-mutants/sim.tsv:17,20,25,29,32,37,40`),
  which the chapter counts as a kill by the build and reports
  separately; (2) the mutants are not independent evidence: the five
  ROR mutants of one comparison (`m34`-`m38`) and the duplicate pair
  `m06`/`m07` (`if (rst_n)` written two ways) inflate a score, the
  point that subsumption and trivial compiler equivalence address
  (TCE in 3.5). Cost: one build per mutant is the naive harness; the
  research's 180 builds took 1,704 s of build time for 1.1 s of
  simulation (`run_sim.log:8`), which is why the example builds a
  schema (1.2(6)), named here and explained in 3.8.
- **Definition callouts (1):** mutation operator (with the operator
  table as `tbl-ch25-operators`, generated by the example: operator,
  meaning, sites, mutant names).
- **In Practice (1):** choosing operators for RTL: the ones the
  software evidence found most often coupled to real faults
  (conditional, relational, statement deletion; Just et al., read) are
  the ones with most sites here; reset and sensitivity operators have
  no software counterpart and the chapter shows (3.5) why they matter.
- **Reader can:** write an operator set for an RTL file, generate its
  mutants mechanically, and name the bug each one models.
- **Example:** `source-mutants/` (generator, the list, lint verdicts
  of the 44 single-edit copies).
- **Figure:** none (the operator table).
- **Sources:** `offutt1996sufficient` (read in the GMU draft; 99.51%
  is the draft's Table 9 figure, to be checked against the TOSEM
  version before it is printed, or printed as "about 99.5%" with the
  draft named in the note), `just2014mutants` (read).
- **Constraints:** the 7 lint kills are reported as their own line,
  never folded silently into a testbench's score; operator names are
  the book's, with the software acronyms given once.

### 3.4 Reading survivors {#sec-ch25-survivors} (~1,200 words)

- **Content.** The kill matrix: 44 rows x 4 testbenches
  (`src-mutants/sim.tsv:2-46`, spliced from `source-sim/run.out`),
  then the survivors read with the conditions of 3.2, one per kind:
  - *Not reached (stimulus gap):* `m35`, `empty` stuck low, survives
    Chapter 1's random test because seed 1 never drains the FIFO after
    the first push ("16 of 17 occupancy levels", `coverage/run.out:3`);
    the directed test and Chapter 9's traffic, which drain it, kill
    it. The coverage line that would have warned is the occupancy line
    the random test already prints: here coverage and mutation agree,
    and the mutant names the hole.
  - *Reached and propagated, not detected (checking gap):* every
    data-path mutant (`m14`-`m25`, `m33`) survives Chapter 9's
    checker, which compares occupancy and flags and never data
    (`sim.tsv:16-27,35`); `@sec-ch19-mutation` found the same of the
    formal checker with three mutants; here it is twelve of twelve.
  - *Directed-test misses:* `m12` (count resets to 31) and `m42`
    (`full` never raised, needs a 17th push) survive the directed test
    of eight entries (`sim.tsv:14,44`), a stimulus gap of a test that
    never fills the FIFO.
  - *No testbench kills seven* (`m05`, `m09`, `m11`, `m13`, `m32`,
    `m36`, `m43`): forward to 3.5, where a miter sorts them.
  The union of the three checking testbenches kills 37 of 44
  (`run_sim.log:7`). The lesson for practice: a survivor is a
  question with three possible answers, and the matrix alone cannot
  say which.
- **Pitfall (1):** a survivor of a short or single-seed run is a
  statement about that seed. `m35` dies to the random test at some
  seed (precondition P6 finds the first seed that drains the FIFO);
  on the netlist, sweeping seeds 1..3 raised the random kill count
  from 8,265 to 8,355 and seeds 4..8 added nothing
  (`yosys-mutants/run_pop.log:12-19`). Report a kill rate with its
  seeds and cycles, because the size confound of the software
  evidence (3.10) applies to testbenches too.
- **Reader can:** read a kill matrix, put each survivor in the
  stimulus-gap or checking-gap class with a reason, and say which
  survivors need a different tool to classify.
- **Example:** `source-sim/` (the matrix).
- **Figure:** `fig-ch25-matrix`: the 44 x 5 kill matrix as a grid (four
  testbenches and the property set, plus a lint column and the miter
  class as a colored margin), mutants grouped by operator; data from
  `source-sim/`, `property-set/`, and the `equiv-*` and
  `miter-differ/` examples. Placed here, completed in 3.6.
- **Sources:** by label (`@sec-ch01-example`, `@sec-ch09-example`,
  `@sec-ch19-mutation`).
- **Constraints:** the chapter's random-test result is at `+seed=1`,
  400 cycles, the testbench as shipped; say so beside the table.

### 3.5 Equivalent mutants and the miter {#sec-ch25-equiv} (~1,800 words)

- **Content.** Why equivalence is the hard part in software (undecidable
  in general for programs; Jia and Harman report 10% to 40% of mutants
  equivalent in two earlier studies, printed "as reported by") and why
  it is not, in principle, for a finite-state design: two finite
  machines are either equivalent or not, and a miter with an unbounded
  proof decides which when the engine finishes. The miter, built by
  hand because InFormal has no equivalence command: both designs, the
  same inputs, and assertions that the outputs agree, with the
  comparison as part of the definition (D15): `full` and `empty`
  always, `rd_data` only when the original is not empty, because the
  memory is not reset and an empty FIFO's `rd_data` has no meaning
  (`formal/miter.sv` header). Comparing it always makes everything
  differ at once (exercise 9). BMC only refutes: the 37 differing
  mutants are found at depth 1-17 (`m42` at 17; `formal/src_formal.tsv`),
  and every "equivalent" verdict is an IC3 proof from rIC3
  (`@su2025ric3`; 1.2(7)). Then the seven survivors sorted (RN M3):
  - **Equivalent outright:** `m32` (the `default` hold deleted; a
    clocked block holds its value anyway) and `m36` (`count <= '0`
    for `count == '0` on an unsigned count).
  - **Equivalent under a reachable-state invariant:** `m43` (`count >=
    16` for `count == 16`) agrees only because the count never
    exceeds 16. BMC can never decide it; induction needs the invariant;
    IC3 finds it. This is `@sec-ch18-helper` and `@sec-ch18-ic3` at
    work, cited not repeated; the example shows k-induction failing
    alone and succeeding with `count <= DEPTH` proven first (to
    measure, P3).
  - **Equivalent only under the tool's reset model:** `m05`
    (asynchronous reset made synchronous) is proved equivalent because
    InFormal treats an asynchronous reset as synchronous; the book's
    testbenches share that assumption (1.2(2)). Reported as its own
    class, never folded into "equivalent".
  - **Not equivalent at all:** `m09`, `m11`, `m13` (a reset
    assignment deleted) differ at depth 1-2 in the miter, whose
    registers start free (`src_formal.tsv` rows `m09`, `m11`, `m13`).
    They survived simulation for a reason in the simulator: the
    Pitfall below.
  Then `m44`: the case labels of the counter exchanged. rIC3 proves it
  equivalent at the ports: the mutant's counter holds minus the
  occupancy modulo 32, and `full` and `empty` test only 0 and 16, the
  two fixed points of negation modulo 32. Yet Chapter 9's `Sync_A`,
  which compares the checker's occupancy with the design's internal
  `count`, kills it at depth 2 (`src_formal.tsv` row `m44`), and so
  does the simulation checker (`sim.tsv:46`). The assertion constrains
  the implementation, not the contract. MCY's name for a test failure
  on a mutant its equivalence check passes is EQGAP, which its
  documentation says "violates at least one" of its assumptions; here
  the assumption violated is that the testbench judges only what the
  contract specifies. The remedy is to report white-box kills
  separately (1.3), not to remove `Sync_A`. Last, trivial compiler
  equivalence in hardware form: synthesize each mutant and compare
  netlists before simulating (Papadakis et al., read: 7.4% of mutants
  equivalent and 21% duplicates on six C programs, about 30% of the
  hand-found equivalents); which FIFO mutants collapse is exercise 5,
  after precondition P7 measures it.
- **Definition callouts (2):** equivalent mutant, *as this chapter
  measures it* (the miter's comparison printed inside the callout);
  the miter (two copies, shared inputs, agreement asserted; bounded
  search refutes, an unbounded proof establishes).
- **Pitfall (1, D9):** the simulator's initial values are part of the
  oracle. `m09`, `m11`, `m13` survive every testbench because the
  simulator's initialization function returns zero by default, so a
  register whose reset was deleted starts exactly where the reset would
  have put it (1.2(5); `verilator-exe-verilator`, `verilator-exe-sim`).
  With `+verilator+rand+reset+2` under five seeds, the directed and
  random tests kill all three and Chapter 9's checker kills `m13`
  (`rand_init.log:2-10`), while `m05`, `m32`, `m36`, `m43` survive, as
  the miter says they must. A missing reset is a real bug that a
  zero-initializing run cannot see; run mutation, and regressions, with
  randomized initial values.
- **Pitfall (1):** an equivalent verdict is only as good as the
  comparison. A miter that compared less (dropped `rd_data`) would
  call every data mutant equivalent; one that compared more would call
  the original different from itself.
- **Reader can:** build a miter for a design and a mutant, choose what
  it compares and defend the choice, read "differs at depth k" and
  "proved equivalent", and place a survivor in one of the three
  equivalence classes or show it is not equivalent.
- **Example:** `miter-differ/` (37 refutations and the two front-end
  refusals), `equiv-outright/` (`m32`, `m36`), `equiv-invariant/`
  (`m43`, with the induction contrast), `equiv-reset/` (`m05`, and the
  asynchronous-pulse simulation if P8 succeeds), `white-box/` (`m44`:
  the miter's proof beside `Sync_A`'s counterexample), `rand-init/`
  (the Pitfall).
- **Figure:** `tbl-ch25-survivors` (generated): the seven survivors and
  `m44`, with miter verdict and depth or engine, simulation verdict at
  default and randomized initial values, and class.
- **Sources:** `jia2011survey` (undecidability and the 10-40% figure,
  both as the survey reports them; Budd and Angluin **not opened**, so
  not cited for content), `papadakis2015tce` (read), `mcy-docs`
  (EQGAP), `su2025ric3`, `informal-tool`; by label `@sec-ch18-helper`,
  `@sec-ch18-ic3`, `@sec-ch18-bmc`, `@sec-ch09-example`.
- **Constraints:** "equivalent under the tool's model" is never
  reported as equivalent; the `m44` paragraph does not say Chapter 9
  erred; numbers of seconds are not printed as facts about the engines
  (they depend on load; RN 6).

### 3.6 The property set as a judge {#sec-ch25-formal} (~1,300 words)

- **Content.** The same 44 mutants against Chapter 19's property set
  (Chapter 9's checker bound, `EmptyPtrs_A`, the tracked-word
  `a_integrity`), procedure cited to `@sec-ch19-mutation`, not
  repeated. Results (RN M4, `src_formal.tsv`): every mutant the miter
  calls non-equivalent and the front end accepts is killed, including
  the three reset mutants simulation missed (free initial registers)
  and `m35`; `m06` and `m07` are refused by InFormal's front end
  ("asynchronous reset 'if' condition does not match sensitivity list
  signal or edge polarity") and counted as their own line, a kill by
  the tool like the seven lint kills, not a counterexample (the
  research summary counted 40 "kills", of which 38 are
  counterexamples; the example prints the two separately); and one
  equivalent mutant, `m44`, killed by `Sync_A` alone. Which property
  kills which: the data mutants fall to `a_integrity` and
  `EmptyPtrs_A`, the counter mutants to the occupancy assertions; no
  single property kills everything (the same conclusion as
  `@sec-ch19-mutation`, now over a population). Then mutation as
  property-set completeness, compactly: Chockler, Kupferman, Kurshan
  and Vardi's coverage by single-signal flips in one state (read);
  Große, Kühne and Drechsler's output multiplexer whose freedom the
  proven properties must forbid (read; three gaps on a RISC CPU);
  Claessen's design-independent "forgotten cases" for safety property
  lists (abstract read); Hoskote et al. as the first metric (title
  level, not opened). Vacuity as the dual: mutating the *property*
  rather than the design (`beer2001vacuity`, and `@sec-ch09-vacuity`
  by label). A survivor of the property set that the miter calls
  non-equivalent is a gap in the specification, and the miter's trace
  is a scenario the properties leave open; on the source set there are
  none, which is what a complete-looking property set looks like, and
  3.9 shows the netlist sample finding 15 (`sampling/run.out:30`).
- **Definition callouts (1):** property-set kill (some property fails
  on the mutant within the stated bound) and its two non-kills
  (bounded "no counterexample" and proof).
- **In Practice (1):** run the property set and the simulation
  testbenches against the same mutants and report them in one matrix:
  formal kills what initial values hide in simulation, simulation runs
  deep traces cheaply that a bounded search does not reach (3.9).
- **Reader can:** run a property set against a mutant population,
  read which property kills which mutant, and interpret a surviving
  non-equivalent mutant as a missing property.
- **Example:** `property-set/` (default: depth-bounded BMC, stop at
  the first failing property per mutant; `MEASURE=1`: the full
  per-property matrix).
- **Figure:** completes `fig-ch25-matrix` (the property-set column).
- **Sources:** `chockler2001practical` (read), `grosse2007bmccoverage`
  (read), `claessen2007coverage` (abstract read), `beer2001vacuity`
  (in `refs.bib`, used by Chapter 9), `hoskote1999coverage` (title
  level only), `informal-tool`.
- **Constraints:** a "no counterexample" from bounded search is never
  called a survival proof (`@sec-ch19-mutation`'s pitfall, cited);
  the formal "kills" of `m09`/`m11`/`m13` rest on free initial values,
  the same fact that makes them real bugs.

### 3.7 Fault model II: netlist mutation, schemata and MCY {#sec-ch25-netlist} (~1,400 words)

- **Content.** The fault model of MCY, run with Yosys alone: after
  `prep`, `mutate -list` with a list size above the population (the
  tool warns that only 9,281 could be created; `gen.log:1-2`) enumerates
  every single-bit mutation on cell ports in five modes, `inv`,
  `const0`, `const1`, `cnot0`, `cnot1` (counts in RN M6; modes measured
  from the list, the documents read do not list them, and the chapter
  says so). Where they fall: Yosys turns the memory into 128 registers,
  and 73.8% of mutations carry the source tags of the memory's
  declaration, write, read and clocked block, with 1,868 more carrying
  none (RN M6). So the population's composition is decided by the
  synthesis, not by the designer, and nobody reads 9,281 mutants one
  at a time: from here on, the chapter counts. Schemata: `mutate -ctrl
  mutsel 14 <value>` puts each mutation behind its own value of a
  select input, value 0 the unmutated design (MCY's documented `-ctrl`
  semantics, read), so each testbench is built once; this is the
  netlist form of Untch, Offutt and Harrold's mutant schemata (read:
  one compiled metamutant, over 300% faster than interpretation in
  their benchmark), and the reason 3.3's source set also runs as a
  schema. Population result (`run_pop.log:7-11`): directed 29.4%,
  random 89.1%, coverage 0, Chapter 9 checker 3.8%, union 89.4%;
  against the source set's 77.3 / 79.5 / 0 / 50.0. **The fault model
  sets the score**: the Chapter 9 checker drops from half to under
  four percent because three quarters of the netlist is the memory it
  never looks at. A kill rate is meaningless without its fault model
  and the composition of its population. MCY, named and taught: what
  it adds to the mechanism is a project database, a sampling list
  (`mutate -list N` with N below the population draws a weighted
  sample favoring source locations with few mutations so far; read,
  `mcy-docs`), a formal filter (a miter with `mutsel` 0 against 1 run
  by SymbiYosys in BMC mode, depth 10 in its example and 1 in
  AppNote 400, so its NOCHANGE is a bounded statement; read), and four
  tags (COVERED, UNCOVERED, NOCHANGE, EQGAP). The plain sentence of
  1.2(3) about why the book does not run MCY. Last, practice: MCY's
  prerequisite, that the test suite pass on the unmutated design (its
  docs: "It is not possible to measure mutation coverage for a failing
  design"), is why the spine is the repaired FIFO and not Chapter 1's.
- **Pitfall (1, D10):** a harness can kill mutants by itself. Yosys
  writes each `$pmux` as a `casez` with a `synopsys parallel_case`
  pragma, and Verilator turns the pragma into an assertion, so a
  mutation of a select bit fails in any testbench; the first population
  run credited Chapter 8's checkless testbench with 383 kills and
  inflated the Chapter 9 checker from 351 to 726
  (`run_pop_assert_case.log:7-11` against `run_pop.log:7-11`).
  `--no-assert-case` removes the pragma assertions and keeps the
  concurrent ones. Rule: a kill you cannot explain is a harness bug
  until shown otherwise, and a testbench with no checker is the
  control that exposes one.
- **Pitfall (1, D10):** a harness can also hide kills. A seed sweep
  that appended `+seed=S` after the testbench's own `+seed=1` ran seed
  1 eight times, because `$value$plusargs` returns the first match
  (`run_pop_assert_case.log:12-19`, every line 8,306, against
  `run_pop.log:12-19`). Found only because a sweep that adds nothing
  is implausible. Each pitfall has a small demonstration in
  `harness-pitfalls/`.
- **Reader can:** generate a netlist mutation population with Yosys,
  put it behind one select input, run a testbench over it, explain the
  difference between this fault model and source operators, and say
  what MCY would add and what its bounded filter cannot decide.
- **Example:** `netlist-list/` (the population: counts by mode, by
  cell type, by source tag), `netlist-sample/` (3.8),
  `harness-pitfalls/`.
- **Figure:** none here (the by-mode rates go in a sentence or a short
  generated table, `sampling/run.out:17-22`, inv 0.925 to cnot0 0.869
  for the random testbench: modes differ little).
- **Sources:** `mcy-docs`, `mcy-repo`, `yosys-ap400` (vendor
  application note, labeled: YosysHQ sells the commercial suite that
  includes MCY), `untch1993schemata` (read), the Yosys 0.68 `help
  mutate` text (read locally; new entry `yosys-mutate`, section 7).
- **Constraints:** MCY's EQGAP sentence quoted at most once and short;
  MCY is never shown running; the 9,281 is "for this file under Yosys
  0.68 after `prep`" every time it is printed.

### 3.8 Sampling: kill rate, equivalent fraction, score {#sec-ch25-sampling} (~1,400 words)

- **Content.** A population too large to run, or to classify, is
  sampled, and a sampled kill rate is a binomial estimate whose error
  depends on the sample size, not the population (Gopinath, Alipour,
  Ahmed, Jensen and Groce, read: at n = 1000, about 7% worst case by
  Chebyshev and about 3% by the normal approximation; on
  commons-math, 95% of 1,000-mutant samples within 71.3% to 76.7% of a
  true 74.03%). The right interval is the Clopper-Pearson interval of
  `@sec-ch21-clean`, used by label and not re-derived. Because this
  population was run in full, the truth is known and the interval can
  be checked: one uniform sample of 100 gives directed 30/100 [0.212,
  0.400] around a true 0.294, random 89/100 [0.812, 0.944] around
  0.891, coverage 0/100 [0, 0.036], checker 4/100 [0.011, 0.099]
  around 0.038 (`sampling/run.out:9`); over 2,000 samples the interval
  covered the truth 94.5% to 100% of the time at n = 30 to 1000, as a
  conservative interval should, with mean width 0.185 at n = 100 and
  0.057 at n = 1000 for the directed test (`sampling/run.out:13-16`).
  What the binomial model assumes: a uniform draw from the full list.
  `mutate -list N` with N below the population is a weighted draw
  (3.7) and its output does not justify the interval; the examples
  list everything and draw uniformly in Python. Correlated mutants
  (adjacent bits of one cell) do not bias a uniform sample but make
  per-line reports overconfident. Then the second estimate, D5 as
  qualified in 1.2(4): the equivalent fraction from a formal sample of
  100 is 6 of 100, 0.060 [0.022, 0.126] (`sampling/run.out:24`; the
  six are three untagged cells and three memory-mux cells, none killed
  by anything). Report the two separately. The score, kills among
  non-equivalent mutants, is computed on the same jointly classified
  sample: random 93/94, 0.989 [0.942, 1.000]; directed 26/94; checker
  7/94; property set 79/94, 0.840 [0.750, 0.908]; simulation and
  formal together 94/94 (`sampling/run.out:25-31`). The naive ratio of
  the population kill rate to 1 - e gives 0.947, and at the interval's
  upper end 1.019, a score above one: the ratio of two estimates is
  not the ratio of their intervals (exercise 3). The 15 non-equivalent
  mutations the property set misses differ only at depth 15 to 31,
  memory slots a 3 s bounded search did not reach (RN M9): a formal
  "survivor" here is a bound, and simulation's 400-cycle traces reach
  them cheaply.
- **Definition callouts (1):** the three numbers reported for a
  sampled population (kill rate over all; equivalent fraction; score
  over non-equivalent, from the joint sample), each with its interval
  and its n.
- **Pitfall (1):** a sample drawn by the tool's own heuristic is not
  a uniform sample, and an interval computed on it is decoration.
- **In Practice (1):** the Gopinath-style budget: about a thousand
  uniformly drawn mutants give a kill rate to within a few points for
  any design size; the equivalent fraction needs a formal sample, and
  a hundred miters is a night of compute here (13 min on four cores,
  `run_ysample.log:7`), which is the real cost of a score.
- **Reader can:** draw a uniform sample from a mutation list, report
  kill rate, equivalent fraction and score with intervals, check a
  sampling procedure against a known population, and say why the
  ratio's interval is not the ratio of intervals.
- **Example:** `netlist-sample/` (default: n = 1000 uniform at seed 1,
  a schema of those only, four builds, the s.1-style lines at n = 100
  and n = 1000, and a cross-check of each sampled verdict against the
  committed population file), `netlist-population/` (Python over the
  committed population file: the interval-coverage check and the
  by-mode table; `MEASURE=1` regenerates the population), and
  `netlist-formal/` (default: a short subset; `MEASURE=1`: the 100
  joint classification).
- **Figure:** `fig-ch25-sampling`: per testbench, the 95% interval at
  n = 30, 100, 300, 1000 from one sample, with the population rate as
  a horizontal line; data from `netlist-sample/` and
  `netlist-population/`.
- **Sources:** `gopinath2015hard` (read), `clopper1934binomial` (by
  label through `@sec-ch21-clean`; not opened, as in Chapter 21),
  `papadakis2019advances` (reports that random 10% sampling loses
  about 26% of fault detection; optional, "as reported by").
- **Constraints:** Wong and Mathur's "16% less effective" is not
  printed (not opened; the survey's report only); every interval
  printed with its n and seed.

### 3.9 Do mutants stand for real bugs? {#sec-ch25-evidence} (~1,000 words)

- **Content.** The software evidence, each item with its limit:
  Just et al. (read): 357 real faults of five Java programs, 73%
  coupled to at least one mutant, mutant detection correlated with
  real-fault detection with coverage controlled, 27% uncoupled and
  mostly needing algorithmic changes no operator makes. Papadakis,
  Shin, Yoo and Bae (read): once suite size is controlled the
  correlation falls from mostly 0.35-0.75 to about 0.05-0.20, but
  suites in the top 10% by score detect significantly more faults (138
  of 231 Defects4J, 59 of 68 CoREBench). Chekam et al. (read): a
  threshold effect; strong mutation helps only at high scores (top
  20% about 5% more faults, top 5% about 18%), and it alone was
  uniquely coupled to 21 faults. Inozemtseva and Holmes (by key, as
  Chapter 8 cites it). Then the hardware line: mutation of HDL
  descriptions has a peer-reviewed history (Al Hayek and Robach 1996,
  title level; Serrestou, Beroulle and Robach 2007, title level;
  Lin et al. 2012, read: a probabilistic propagation analysis that
  drops simulations, with Certitude's three mutant classes, operator
  changes, dead assignments and conditions stuck at true or false,
  printed as read from a peer-reviewed paper; Huang et al. 2015,
  abstract read) and a commercial tool described by its vendor
  (Hampton and Petithomme 2007, vendor authors at a peer-reviewed
  workshop; `hampton2009fq`, SpringSoft article, Synopsys page: vendor,
  no figures). There is no hardware counterpart of Defects4J, so no
  number transfers. What transfers is the shape: compare kill rates
  only between testbenches of comparable cost (seeds, cycles, the size
  confound); read a kill rate at the top, not in the middle (the
  threshold); prefer operators that coupled best (conditions,
  relational operators, statement deletion), which are the FIFO set's
  majority. Industrial practice in software: Google surfaces a few
  diff-based mutants in code review (Petrović et al., read: median 7
  per change against 820; developers rated 89% of reported mutants
  productive after refinement), which is the model for running
  mutation on a design change rather than on the whole design.
- **In Practice (1):** mutation on the diff: mutate the lines a change
  touched, run the regression's fastest checking tests, report the
  survivors in review; cost scales with the change.
- **Reader can:** state what the software studies found and what
  they did not, and say which conclusions may and may not be carried
  to RTL.
- **Example:** none.
- **Figure:** none.
- **Sources:** `just2014mutants`, `papadakis2018correlated`,
  `chekam2017threshold`, `inozemtseva2014coverage`,
  `petrovic2021mutation` (all read; Inozemtseva by Chapter 8),
  `lin2012epa` (read), `huang2015mutation` (abstract),
  `alhayek1996unified`, `serrestou2007rtl` (title level, not opened),
  `hampton2007certitude`, `hampton2009fq`, `springsoft-fq`,
  `synopsys-certitude` (vendor, labeled).
- **Constraints:** no software percentage is presented as applying to
  hardware; every vendor sentence says "the vendor"; Lin et al.'s
  33-61% figure from RN is not printed unless re-read (this outline's
  reading confirmed only the 14% CPU-time figure).

### 3.10 Worked example: closing the gap with a data check {#sec-ch25-example} (~1,100 words)

- **Content.** One flow on the spine, in the order an engineer runs
  it: (1) the matrix says Chapter 9's checker has a data-path gap
  (3.4) and the netlist says the gap is most of the design (3.7);
  (2) write the smallest check that closes it: a bind module
  `fifo_data_sva.sv` that keeps a queue of accepted pushes and asserts,
  on every accepted pop, that `rd_data` equals the queue's head,
  bound beside Chapter 9's unchanged checker on Chapter 9's unchanged
  traffic (a scoreboard line in simulation; `@sec-ch19-track` is its
  formal counterpart, cited); (3) control first: the fifth testbench
  passes on the repaired FIFO and fails on Chapter 1's original (the
  control run is part of the method, as in `@sec-ch21-example`);
  (4) rerun the 44 source mutants and the n = 1000 netlist sample;
  (5) read the new matrix: the data mutants die; `m35` dies because
  this traffic drains the FIFO; `m09`, `m11`, `m13` still survive
  under the default initial values and die with randomized ones; the
  five equivalents survive and `m44` still dies to `Sync_A`; (6) write
  the result as the chapter recommends: kill rate with fault model,
  n, seeds and initial-value mode, the equivalent fraction beside it,
  and the coverage beside both. Expected numbers in 1.2(8); the text is
  written from P5's `run.out`.
- **Worked Example callout:** qualifying a testbench in six steps:
  (1) control: the testbench passes the design and fails a known-bad
  one; (2) mutate with a stated fault model, every site, or a uniform
  sample of a stated size; (3) run as a schema with randomized initial
  values, and keep a checkless control to expose harness kills;
  (4) classify survivors with a miter: equivalent (which kind), or a
  gap (stimulus, checking); (5) fix the gap the survivors name, not
  the score; (6) report kill rate, equivalent fraction and score with
  intervals and the fault model, beside coverage.
- **Reader can:** go from a survivor list to a specific missing check,
  write it, and show the kill rate move with a control.
- **Example:** `fifth-tb/` (source schema and netlist sample with the
  fifth testbench; split into `fifth-tb/` and `fifth-tb-netlist/` if
  over 90 s).
- **Figure:** none (the before/after table is the output); optionally
  the fifth testbench added as a fifth point on `fig-ch25-axes`.
- **Sources:** by label.
- **Constraints:** Chapter 9's files are read by path and not edited;
  the new check lives in this chapter's directory; "closes the gap"
  means the data-path gap (1.2(8)).

### 3.11 Future directions (~450 words; one Future Directions callout)

Large language models in mutation, compact and measured-versus-claimed
(D8): LLMs as *generators* of mutants aimed at a concern (Foster et
al., abstract read: 9,095 mutants and 571 tests over 10,795 Kotlin
classes, 73% of tests accepted by engineers; industrial authors) and
of realistic RTL bugs (BugGen, abstract read: 500 bugs in five
OpenTitan IP blocks, 17.7 validated bugs per hour; its "94% functional
accuracy" and "104 previously undetected bugs" are not printed because
the abstract does not define them, RN 6); LLMs as *classifiers* of
equivalence (Tian et al., abstract read: 35.69% average F1 improvement
over earlier techniques on 3,302 Java mutant pairs; Foster et al.'s
detector at precision 0.79 and recall 0.47, 0.95 and 0.96 with
pre-processing the abstract does not describe); and mutation kill rate
as an audit of LLM benchmarks' testbenches (GateTruth, single-author
preprint, abstract read: 72% of 46 auditable RTLLM v2.0 designs below
a 95% kill threshold). The book's position in one sentence: for
finite-state hardware a miter is the exact classifier whenever its
proof finishes, so an LLM classifier is to be scored against it; that
experiment is named for Machine Learning in Verification and Generative
AI and Agentic DV (by name, not label; the latter is `@sec-ch34`,
which may be cited by label since it exists, at
`@sec-ch34-evaluation`, where mutation is already named as the hidden
metric). Also: higher-order mutants as the open question the coupling
effect leaves (title level, `jia2009hom` not opened, so named only),
mutation of the DMA of `@sec-ch11` with its protocol property set as
the natural next population (D7), and Safety and Security Verification
(by name) as the chapter where fault injection asks the same question
of the silicon rather than of the testbench. No claim of results.

### 3.12 Summary (~350 words)

One bullet per section: kill rate and coverage are different axes; a
kill needs reach, infection, propagation and a check; operators are a
stated fault model; survivors are stimulus gaps, checking gaps, model
artifacts or equivalents, and the matrix alone cannot tell; equivalence
is what the miter compares, decided only by an unbounded proof, in
three kinds, and a white-box assertion can kill an equivalent mutant;
the property set is a judge with its own blind spots; the fault model
sets the score; sample uniformly and report three numbers with
intervals; the software evidence licenses the method, not its numbers;
a harness that kills by itself is the first thing to rule out.

### 3.13 Exercises (~700 words; list in section 5)

### 3.14 Further reading (~150 words)

Jia and Harman's survey (2011) and Papadakis et al.'s (2019, in
Advances in Computers, volume to confirm); Just et al. 2014;
Gopinath et al. 2015; Untch, Offutt and Harrold 1993; Chockler,
Kupferman, Kurshan and Vardi 2001; Große, Kühne and Drechsler 2007;
the MCY documentation and AppNote 400 (vendor); DeMillo, Lipton and
Sayward 1978 (title level, not opened).

### Budget

| section | words |
|---|---|
| front matter | 300 |
| 3.1 motivation | 900 |
| 3.2 mutants, kills, hypotheses | 1,300 |
| 3.3 source operators | 1,300 |
| 3.4 survivors | 1,200 |
| 3.5 equivalence and the miter | 1,800 |
| 3.6 property set as judge | 1,300 |
| 3.7 netlist, schemata, MCY | 1,400 |
| 3.8 sampling | 1,400 |
| 3.9 real bugs | 1,000 |
| 3.10 worked example | 1,100 |
| 3.11 future directions | 450 |
| 3.12 summary | 350 |
| 3.13 exercises | 700 |
| 3.14 further reading | 150 |
| **total** | **14,650** (callouts and captions included; band 13,500-15,000) |

Callout census (six kinds only): Definition 11 (3.2: 3, 3.3: 1, 3.5:
2, 3.6: 1, 3.8: 1, plus the operator and survivor tables as generated
tables, not callouts; drafter may merge to about 9); Pitfall 7 (3.4: 1,
3.5: 2, 3.7: 2, 3.8: 1, and the opening's "don't call it broken" is
prose, not a callout); In Practice 4 (3.3, 3.6, 3.8, 3.9); Worked
Example 1 (3.10); Future Directions 1 (3.11); Exercise 1 wrapping the
list. The learning-objectives box is the opener, not a callout.

Figures (4): `fig-ch25-axes` (3.1), `fig-ch25-rip` (3.2, drawn),
`fig-ch25-matrix` (3.4/3.6), `fig-ch25-sampling` (3.8). Generated
tables (3): `tbl-ch25-operators` (3.3), `tbl-ch25-survivors` (3.5),
`tbl-ch25-report` (3.10, before/after). All from the book's own runs;
nothing redrawn from a source.

## 4. Example directories

All under `examples/ch25-mutation-testing/`. Python drivers use the
book's Python example pattern (`EXAMPLE_LANG := python`, standard
library only, `python3 -I`), print the tool versions they ran and the
seed of every random draw, and name in `EXPECT_OUTPUT` a line only a
real run prints. Verilator builds use the flags of `examples/mk/sv.mk`
(as `mutlib.py` copies them) plus `-Wno-SYNCASYNCNET` for the Chapter 9
testbench, `--coverage` only where coverage is read, and
`--no-assert-case` for every build of a Yosys netlist (Pitfall, 3.7).
Formal runs go through `examples/mk/informal.sh` with an engine
selected for each `prove`; any example that selects `ric3-ic3` sets
`REQUIRES := ric3` and is skipped where rIC3 is absent (CI today).
Files of other chapters are read **by path** and never copied or
edited: `examples/ch09-temporal-properties/rtl/fifo_fixed.sv`,
`examples/ch01-what-is-dv/sv-directed/tb_fifo_directed.sv`,
`examples/ch01-what-is-dv/sv-random/tb_fifo_random.sv`,
`examples/ch08-functional-coverage/fifo-coverage/{lint.vlt,tb_fifo_cov.sv}`,
`examples/ch09-temporal-properties/fifo-checker/{fifo_sva.sv,fifo_bind.sv,tb_fifo_sva.sv}`,
Chapter 19's property-set files under
`examples/ch19-formal-techniques/` (`common/ch19.tcl`,
`track-word/track.sv`, the `mutants/` script's property list), and
Chapter 21's `common/statlib.py` for Clopper-Pearson (imported by path;
its self-test already checks the interval). Research scripts in
`research/ch25-measurements/` are the starting point; each needs the
80-column pass, 72-column rulers, a header saying what it is, and its
numbers re-derived by the example. Build directories go under the
example's own scratch directory and are deleted by `make clean`.

**Times.** Research timings on the book's four-core machine: one
Verilator build of a FIFO testbench about 9.5 s (1,704 s / 180,
`run_sim.log:8`); one build of the full 48,016-line netlist schema
10.7 to 31.7 s by testbench (`run_pop.log:1-4`); a run about 10 ms;
Yosys list plus full netlist 22 s (`gen.log:2`); a BMC refutation of a
source miter about 0.1 s after start-up (`src_formal.tsv` `miter_s`);
an rIC3 equivalence proof of a FIFO miter about 20 s alone (RN M3; the
recorded 58-66 s includes the BMC and in-house IC3 attempts before
it). The "expected" column below is an estimate from those numbers;
each must be measured (section 9) and any directory over 90 s split
as its row says. **`MEASURE=1` outputs**: where the chapter splices a
full-population figure that the default run does not produce, the
`MEASURE=1` run writes `measure.out` beside `run.out`, the file is
committed, and its first lines print the tool versions, date and wall
time; the chapter splices it like a `run.out` and the caption says it
is the opt-in run. Every default run that depends on a committed
`measure.out` or population file cross-checks a slice of it and fails
if they disagree.

| directory | needs | design and files | `run.out` (what it prints; evidence) | expected |
|---|---|---|---|---|
| `common/` | python | `mutlib.py` (testbench table, build and run with verdicts killed / survived / timeout / stillborn, from `research/ch25-measurements/mutlib.py`), `srcmut.py` (the 44 operator edits applied at run time to `fifo_fixed.sv`, each failing if it matches nothing; writes single-edit copies or the schema), `schema.py` (the source schema: every edit behind `mut == K` read from `+mut=K`; `m05` as an effective asynchronous reset held inactive when selected), `yosysmut.py` (list parse, uniform sample, `-ctrl` script for a chosen subset), `miter.py` (miter and property-set Tcl generation, from `formal/formal.py` and `miter.sv`) | library; a self-test prints the 44 edit count, the schema's control verdict on all four testbenches, and one Clopper-Pearson value from Chapter 21's `statlib.py` | < 5 s |
| `opening/` | verilator, python | four testbenches with `--coverage` against `fifo_fixed.sv`; coverage summary per testbench; covergroup percentages; the kill column read from `source-sim/run.out` by path (or recomputed if time allows) | `coverage/run.out:1-14`; kills `run_sim.log:3-7` | 4 builds x ~12 s + runs + `verilator_coverage` ~ 60 s |
| `source-mutants/` | verilator, python | the 44 edits as one-line diffs; `verilator --lint-only` with the book's flags on each single-edit copy | the list (`src-mutants/mutants.tsv`), operator counts (RN M1), 7 lint rejections with their warning names (`sim.tsv:17,20,25,29,32,37,40`) | 45 lint runs ~1 s each: ~45 s |
| `source-sim/` | verilator, python | the schema built once per testbench (4 builds); 45 runs each; prints the 44 x 4 matrix, per-testbench kills, union; `MEASURE=1`: 180 per-mutant builds (about 7 min on 4 cores) and a line comparing that matrix with the schema's, written to `measure.out` | `run_sim.log:1-8`; `sim.tsv:1-46` | 4 x ~10 s + 180 runs ~ 2 s: ~50 s |
| `rand-init/` | verilator, python | the schema with `+verilator+rand+reset+2`, seeds 1-5, on `m05 m09 m11 m13 m32 m36 m43 m44` and the control | `rand_init.log:1-10` | reuse no build dir across examples: 4 builds + 180 runs: ~50 s |
| `harness-pitfalls/` | yosys, verilator | (a) one select-bit mutation of the netlist under Chapter 8's checkless testbench, built with and without `--no-assert-case`: killed, then survived; (b) a ten-line testbench reading `+seed=` given twice, printing the value `$value$plusargs` returns | `run_pop_assert_case.log` vs `run_pop.log` as evidence; both demonstrations **to be measured** (P9) | 1 small netlist + 2 builds: ~40 s |
| `miter-differ/` | informal, python | miters of the 37 non-equivalent source mutants, `informal-bmc` to depth 20; the two front-end refusals (`m06`, `m07`) printed with the tool's message | depths per mutant (`src_formal.tsv`), `m42` at 17 | 39 InFormal runs; start-up cost unknown: **measure**; split by halves if > 90 s |
| `equiv-outright/` | informal, ric3 | `m32`, `m36`: BMC undetermined, rIC3 proves | `src_formal.tsv` rows `m32`, `m36` | ~45 s |
| `equiv-invariant/` | informal, ric3 | `m43`: BMC undetermined to depth 40; k-induction alone fails; prove `count <= DEPTH` on the miter, assume it, k-induction proves; rIC3 alone proves | row `m43`; the induction contrast **to be measured** (P3) | ~40 s |
| `equiv-reset/` | informal, ric3; verilator | `m05`: rIC3 proves under the tool's reset model; plus a Verilator testbench that pulses `rst_n` low between clock edges and reads `empty` before the next edge, on the original and on `m05` | row `m05`; the simulation half **to be measured** (P8) | ~40 s |
| `white-box/` | informal, ric3 | `m44`: the miter proved equivalent; the property set run on `m44`, `Sync_A` refuted at depth 2 and every other property not refuted to the bound; the counter trace printed for four cycles to show count = -occupancy mod 32 | row `m44`; `sim.tsv:46` | ~45 s |
| `property-set/` | informal, python | the 44 source mutants against Chapter 19's set; default: `informal-bmc` depth-bounded, properties in a fixed order, stop at the first failing property per mutant; `m06`/`m07` refused, printed apart; `MEASURE=1`: every property on every mutant (the full matrix) into `measure.out` | `run_src.log:2`, `src_formal.tsv` `killed_by` | **measure** (P2); research 468 s with miters; split m01-m22 / m23-m44 if over 90 s |
| `netlist-list/` | yosys, python | `mutate -list 100000 -seed 1 -none` on the `prep`ped FIFO; counts by mode, cell type and source tag; the list written to the example's scratch dir and its SHA-256 printed | `gen.log:1-2`; RN M6 counts | list only (no netlist write): **measure**; < 22 s |
| `netlist-sample/` | yosys, verilator, python | uniform sample of 1000 from the list (seed 1); a `-ctrl` netlist of those only; 4 builds; runs; kills and Clopper-Pearson at n = 30, 100, 300, 1000 (nested prefixes of one draw); cross-check: each sampled verdict equals its row in `netlist-population/pop.tsv` | `sampling/run.out:7-11` | smaller netlist builds **measure**; ~70 s; split testbenches across two dirs if over |
| `netlist-population/` | python; `MEASURE=1`: yosys, verilator | default: reads the committed `pop.tsv` (9,281 rows, about 525 KB), prints population rates, the 2,000-sample interval-coverage table and the by-mode table; `MEASURE=1`: regenerates `pop.tsv` from a full schema (about 3 min on 4 cores) and prints the seed sweep | `run_pop.log:5-19`, `sampling/run.out:1-6,12-22` | default ~30 s (`sampling/run.out:34` real 27 s) |
| `netlist-formal/` | informal, ric3, python | `MEASURE=1`: the 100-mutation formal sample (seed 25): property set (BMC 3 s) and miter per mutation, about 13 min on 4 cores, into `measure.out`; default: two of its six equivalents proved and two of its deepest non-equivalents refuted, plus the summary lines recomputed from the committed `measure.out` | `run_ysample.log:1-7`, `sampling/run.out:23-32` | default ~70 s |
| `fifth-tb/` | verilator, python | new `fifo_data_sva.sv` (queue of accepted pushes, `rd_data` compared on accepted pops) and its bind file, beside Chapter 9's checker and testbench by path; control on repaired and original FIFO; source schema (44) at default and randomized initial values; the before/after table | **to be measured** (P5); expected 37/44 and 40/44 (1.2(8)) | ~60 s |
| `fifth-tb-netlist/` | yosys, verilator, python | the fifth testbench on the same n = 1000 netlist sample; before/after beside `netlist-sample/` | **to be measured** (P5) | ~50 s |

Eighteen directories. If the drafter wants fewer, the four `equiv-*`
and `white-box/` may merge into two only if measured under 90 s each;
the teaching order of 3.5 does not depend on the split.

## 5. Exercises (each with one determinate answer; solutions to the solutions appendix)

1. A uniform sample of 100 netlist mutations; the directed test kills
   30. Give the two-sided 95% Clopper-Pearson interval, and say
   whether it contains the population rate 2,725 / 9,281.
   **[0.212, 0.400]; yes (0.294)** (`sampling/run.out:2,9`).
2. A formal sample of 100 finds 6 equivalent mutants. The 95%
   interval for the equivalent fraction. **[0.022, 0.126]**
   (`sampling/run.out:24`).
3. The population kill rate is 0.8905 and the equivalent fraction's
   interval is [0.022, 0.126]. Compute kill / (1 - e) at e = 0.060 and
   at both interval ends, and say what the upper value shows.
   **0.947; 0.911 and 1.019; a "score" above one: the ratio of
   intervals is not an interval for the ratio** (1.2(4)).
4. Gopinath et al.'s worst case p = 0.5 at n = 1000 and 95%: the
   half-width by Chebyshev (n >= 1/(4 e^2 d)) and by the normal
   approximation. **0.071; 0.031** (`sampling/run.out:16`).
5. Synthesize each of the 44 source mutants and the original with the
   same Yosys script and compare the optimized netlists. Which mutants
   are trivially equivalent to the original, and which pairs are
   duplicates of each other? **To be fixed by P7** (expected:
   `m06`/`m07` a duplicate pair; `m32` and `m36` candidates for
   identity with the original).
6. Why can no bounded search ever report `m43` equivalent, and what
   invariant does an inductive proof of its miter need?
   **Bounded search only refutes; it needs `count <= 16` (DEPTH) on
   every reachable state.**
7. Under `m44`, starting from reset, apply three pushes and then one
   pop. What value does the mutant's `count` hold, and what are
   `full` and `empty`? **30 (= -2 mod 32); full 0, empty 0, the same
   as the original.**
8. Is `m44` killed under weak mutation, comparing state right after
   the mutated statement? After how many accepted operations from
   reset? **Yes; after the first push (count 31 against 1).**
9. Change the miter to compare `rd_data` on every cycle and run it on
   the original FIFO against an unmutated copy of itself. What does
   it report, and why? **A difference at the first cycle (depth to be
   read from P10), because the memory is not reset and the two copies'
   words start free.**
10. Write a testbench that drops `rst_n` between clock edges and
    checks `empty` before the next edge. Does it kill `m05`?
    **To be fixed by P8 (expected: yes; if not, the exercise is
    cut).**
11. Chapter 1's random test misses `m35` at seed 1. Find the smallest
    seed at which it kills `m35`. **To be fixed by P6.**
12. Chapter 8's coverage testbench killed 0 of 1000 sampled netlist
    mutations. Give the exact one-sided 95% upper bound on its kill
    rate (`@sec-ch21-clean`'s formula) and say why the bound, though
    correct, says nothing about whether the testbench could ever
    kill a mutant. **0.0030 (1 - 0.05^(1/1000)); the testbench has no
    checker, so its true kill rate is zero by construction, and the
    bound only measures the sample.**

Twelve exercises (band 8-12). Exercises 5, 9, 10 and 11 have answers
that a precondition measures; if any measurement fails, that exercise
is cut, leaving at least eight. No DMA exercise (D7).

## 6. Deliberately not here, and what is cited by label

- **Chapter 1 owns** the FIFO, its bug and the two testbenches
  (`@sec-ch01-example`); **Chapter 9** owns the repaired FIFO, the
  checker and `Sync_A`'s rationale (`@sec-ch09-example`), vacuity
  (`@sec-ch09-vacuity`) and the formal half of the checker.
- **Chapter 8 owns** "coverage measures activation only", the vendor's
  three conditions as quoted, Huang et al.'s sentence, Inozemtseva and
  Holmes, the FIFO coverage model and its runs, code coverage on
  Verilator (`@sec-ch08-where`, `@sec-ch08-example`,
  `@sec-ch08-code-coverage`). This chapter points at them; the vendor
  quotation is not repeated.
- **Chapters 17-19 own** miters as SAT problems (`@sec-ch17`), BMC,
  induction, helper invariants, IC3 and assumptions (`@sec-ch18-bmc`,
  `@sec-ch18-induction`, `@sec-ch18-helper`, `@sec-ch18-ic3`), and the
  three-mutant procedure on the property set, the tracked-word check
  and its pitfalls (`@sec-ch19-mutation`, `@sec-ch19-track`). This
  chapter supplies the method that `@sec-ch19-mutation` defers to it
  and does not repeat the procedure.
- **Chapter 21 owns** Clopper-Pearson, the zero-failure bound and the
  rule of three (`@sec-ch21-clean`), and the seed as the sampling unit
  (`@sec-ch21-seed`).
- **The generative-AI chapter** already names mutation as the hidden
  metric (`@sec-ch34-evaluation`); this chapter is consistent with it
  and cites it once in Future Directions.
- **Later chapters, by name only:** Hardware Construction Languages and
  Compiler IRs (RTLIL, where Yosys mutates), Reproducible Verification
  (seeds as inputs; the harness pitfalls as CI hygiene), Metrics,
  Closure and Sign-off (kill rate as a sign-off column), Safety and
  Security Verification (fault injection), Machine Learning in
  Verification (an LLM equivalence classifier scored against the
  miter).
- **Not here at all:** MCY run as a tool (1.2(3)); any hardware
  number derived from software studies; the DMA population (D7); an
  LLM experiment (D8); higher-order mutants beyond a sentence; a
  re-derivation of Clopper-Pearson; a new Python dependency.

## 7. Primary sources behind the chapter's definitions and results: read, and not read

All opened 2026-11-16 through a fetch tool that returns extracted text,
summarized; "read" means the abstract, the introduction and the section
named were seen at that level (for long PDFs the first 100,000
characters). Local reads are marked. Any wording the chapter quotes
must be re-read in the document before print; planned quotations are
at most MCY's EQGAP clause and the Verilator option names.

| claim the chapter makes | source | status | URL read | section |
|---|---|---|---|---|
| killed; strong / weak / firm; score = killed / non-equivalent; CPH and coupling credited to DeMillo et al.; equivalence undecidable (credited to Budd and Angluin); 10-40% equivalent (credited to two studies); 99.5% for five operators (credited to Offutt et al.) | Jia and Harman 2011 | **read** (course copy, first 100,000 of 107,731 characters; volume and pages not printed in the copy, taken from Crossref) | https://web.eecs.umich.edu/~weimerw/2020-481F/readings/mutation-testing.pdf | 3.2, 3.5 |
| competent programmer and coupling effect, in the originators' words | Budd, DeMillo, Lipton and Sayward 1980, GIT-ICS-80/01 | **read** (DTIC scan; states both hypotheses; coupling posed as open) | https://apps.dtic.mil/sti/pdfs/ADA083078.pdf | 3.2 |
| origin of mutation analysis | DeMillo, Lipton and Sayward 1978 | **not opened** (only a course page's BibTeX and summary seen at https://users.cs.northwestern.edu/~chrdimo/teaching/eecs396-w19/16.pdf, a secondary); credited as origin, no content attributed | — | 3.2, 3.14 |
| other independent origin | Hamlet 1977 | **not opened** (Crossref record via RN only) | — | 3.2 (title level) |
| coupling effect formalized | Offutt 1992 | **not opened** | — | not cited for content |
| five sufficient operators, 99.51% | Offutt, Lee, Rothermel, Untch and Zapf | **read** in the GMU draft "An Experimental Determination of Sufficient Mutation Operators" (Table 9: 99.51%; Table 10: ~78% fewer mutants); TOSEM 1996 version not opened | https://cs.gmu.edu/media/techreports/ISSE-TR-94-00.pdf | 3.3 |
| RIPR; TCE finds at least 30% of equivalents; redundant mutants inflate scores up to 10% (credited to Just et al.); 10% sampling loses ~26% (credited to Papadakis and Malevris) | Papadakis, Kintis, Zhang, Jia, Le Traon and Harman 2019 | **read** (preprint, first 100,000 of 101,415 characters; volume not printed, Crossref gives pages 275-378, ISBN 9780128151211, no volume) | https://mutationtesting.uni.lu/survey.pdf ; https://api.crossref.org/works/10.1016/bs.adcom.2018.03.015 | 3.2, 3.8 |
| RIPR's own origin | the survey's ref. [32] | **not opened** | — | not cited |
| equivalence undecidable for programs | Budd and Angluin 1982 | **not opened** (search found only catalog records) | — | cited only "as Jia and Harman report" or not at all |
| TCE: 7.4% equivalent, 21% duplicates, ~30% of known equivalents | Papadakis, Jia, Harman and Le Traon 2015 | **read** (authors' copy; venue confirmed ICSE 2015, pp. 936-946, from Crossref) | https://orbilu.uni.lu/bitstream/10993/20289/1/ICSE15.pdf ; https://api.crossref.org/works/10.1109/ICSE.2015.103 | 3.5 |
| subsumption, minimal mutant sets | Ammann, Delamaro and Offutt 2014 | **not opened**; definition seen only in Shin and Bae's summary (https://arxiv.org/pdf/1601.06466), a secondary | — | not cited; the idea is stated in the book's words without a citation, or the paper is read first |
| schemata: one compiled metamutant; >300%, 4.1x on Newton's method | Untch, Offutt and Harrold 1993 | **read** (scispace copy; venue not printed, ISSTA 1993 from the record) | https://scispace.com/pdf/mutation-analysis-using-mutant-schemata-1k0msw5h9z.pdf | 3.7 |
| sample size independent of population; Chebyshev ~7%, normal ~3.1% at n = 1000; commons-math 122,484 mutants, 74.03%, 71.3-76.7%; MAE 0.62% / 2.56% | Gopinath, Alipour, Ahmed, Jensen and Groce 2015 | **read** (authors' copy; venue from Crossref: ISSRE 2015, 216-227) | https://www.cefns.nau.edu/~adg326/issre15.pdf ; https://api.crossref.org/works/10.1109/ISSRE.2015.7381815 | 3.8 |
| 10% sample "16% less effective" | Wong and Mathur 1995 | **not opened** | — | not printed |
| Clopper-Pearson | Clopper and Pearson 1934 | **not opened** (as in Chapter 21); used through `@sec-ch21-clean` | — | 3.8 |
| 357 faults, 73% coupled; uncoupled need algorithmic change; best-coupled operators | Just, Jalali, Inozemtseva, Ernst, Holmes and Fraser 2014 | **read** (authors' copy; pages from Crossref 654-665) | https://homes.cs.washington.edu/%7Emernst/pubs/mutation-effectiveness-fse2014.pdf | 3.3, 3.9 |
| size confound 0.35-0.75 to 0.05-0.20; top 10%: 138/231, 59/68 | Papadakis, Shin, Yoo and Bae 2018 | **read** (authors' copy; pages 537-548 from Crossref) | https://core.ac.uk/download/154760839.pdf ; https://api.crossref.org/works/10.1145/3180155.3180183 | 3.9 |
| threshold effect; top 20% ~5%, top 5% ~18%; 21 faults unique to strong mutation | Chekam, Papadakis, Le Traon and Harman 2017 | **read** (authors' copy; venue from Crossref) | https://discovery.ucl.ac.uk/10058915/7/Chekam_ICSE17.pdf ; https://api.crossref.org/works/10.1109/ICSE.2017.61 | 3.9 |
| diff-based mutants in review; median 7 vs 820; 89% productive | Petrović, Ivanković, Fraser and Just | **read** (accepted version) | https://homes.cs.washington.edu/~rjust/publ/practical_mutation_testing_tse_2021.pdf | 3.9 |
| coverage by single flips of an observable signal in a state | Chockler, Kupferman, Kurshan and Vardi 2001 | **read** (author copy) | https://www.cs.huji.ac.il/~ornak/publications/cav01.pdf | 3.6 |
| output multiplexer; three gaps on a RISC CPU | Große, Kühne and Drechsler | **read** (authors' copy; venue, year and pages not printed: DATE 2007 from the file name only) | https://agra.informatik.uni-bremen.de/doc/konf/07date_coverage.pdf | 3.6 |
| forgotten cases, design-independent | Claessen 2007 | **abstract read** (Chalmers record: author "Koen Lindström Claessen", FMCAD 2007, 139-145, DOI 10.1109/FAMCAD.2007.32) | https://research.chalmers.se/en/publication/67786 | 3.6 |
| first coverage metric for model checking | Hoskote, Kam, Ho and Zhao 1999 | **not opened** | — | 3.6 (title level) |
| vacuity as property mutation | Beer et al. 2001; Kupferman and Vardi 2003 | Beer: in `refs.bib`, used by Chapter 9, not re-opened; Kupferman-Vardi **not opened** | — | 3.6 (Beer only) |
| MCY: single-bit mutations; prerequisite; tags; EQGAP sentence; candidate lists and weights; `-ctrl`, 0 reserved; equivalence = miter in SBY BMC depth 10 | MCY documentation | **read** (methodology, mutate, eqsetup pages) | https://mcy.readthedocs.io/en/latest/methodology.html ; https://mcy.readthedocs.io/en/latest/mutate.html ; https://mcy.readthedocs.io/en/latest/eqsetup.html | 3.5, 3.7 |
| MCY tutorial; SBY with yices at depth 1 | AppNote 400 (YosysHQ, copyright 2022; **vendor**) | **read** | https://yosyshq.readthedocs.io/projects/ap400/en/latest/ | 3.7 |
| `mutate -list N` "using an even sampling", `-ctrl`, `-cfg` weights | Yosys 0.68 `help mutate` | **read locally** (`/opt/dvtools/bin/yosys -h mutate`); modes not listed there either | local | 3.7 |
| `--x-initial unique` is the default; `+verilator+rand+reset+` 0/1/2; `fast` hides missing resets; state variables "initialized to a random value" | Verilator 5.052 guide | **read locally** in the 5.052 source docs (`docs/guide/exe_verilator.rst` lines 2283-2307) and online (exe_sim; input languages) | https://verilator.org/guide/latest/exe_sim.html ; https://github.com/verilator/verilator/blob/master/docs/guide/languages.rst | 3.5 |
| three Certitude mutant classes; 14% CPU saving on three OpenCores designs | Lin et al. 2012 | **read** (proceedings PDF; the RN's "33-61%" not confirmed in this reading) | https://past.date-conference.com/date16/files/proceedings/2012/pdffiles/03.2_3.pdf | 3.9 |
| activation, propagation, detection (**vendor**) | Hampton 2009, EDN, Certess CTO | **read** (dated 2009-03-02) | https://www.edn.com/functional-qualification-a-technical-brief/ | 3.2 |
| Certitude principles; "production-proven"; no figures (**vendor**) | SpringSoft, Tech Design Forums | **read** (undated, no author) | https://www.techdesignforums.com/practice/?p=2269 | 3.9 |
| Certitude in a peer-reviewed workshop (**vendor authors**) | Hampton and Petithomme 2007 | **not opened** this session (in `refs.bib`; Chapter 37 cites it) | — | 3.9 (descriptive only) |
| testbench qualification by mutation | Huang et al. 2015 | **abstract** (as Chapter 8 recorded it; full text 403) | — | 3.9 |
| early HDL mutation | Al Hayek and Robach 1996 | **record only** (researchr: ITC 1996, 885-893, no DOI, no abstract) | https://researchr.org/publication/HayekR96%3A0 | 3.9 (title level) |
| RTL verification driven by mutation metrics | Serrestou, Beroulle and Robach 2007 | **record only** (Crossref still runs names 2 and 3 together) | https://api.crossref.org/works/10.1109%2FDSD.2007.4341472 | 3.9 (title level) |
| SystemC mutation | Lisherness and Cheng 2010 | **not opened** | — | not cited |
| LLM equivalence detection: 3,302 pairs, +35.69% F1 | Tian, Shu, Wang, Cao, Kamei and Chen 2024 | **abstract read** | https://arxiv.org/abs/2408.01760v1 | 3.11 |
| ACH: 10,795 classes, 9,095 mutants, 571 tests, 73% accepted, 36% privacy-relevant; detector 0.79/0.47, 0.95/0.96 | Foster et al. 2025 | **abstract read** (seven platforms) | https://arxiv.org/abs/2501.12862 | 3.11 |
| BugGen: 500 bugs, five OpenTitan IPs, 17.7/hour | Jasper et al. 2025 | **abstract read** (v2, 2025-06-18); 94% and 104 not printed | https://arxiv.org/abs/2506.10501 | 3.11 |
| GateTruth: 46/60; 72% of 46 RTLLM v2.0 below 95% | Bhadra 2026 | **abstract read** (v1, 2026-08-12; operators unnamed) | https://arxiv.org/abs/2608.12635 | 3.11 |
| higher-order mutants | Jia and Harman 2009 | **not opened** | — | named only |

### 7.1 BibTeX corrections to the research note's section 5

To apply when the entries move to `refs.bib` (the drafter does it; this
outline edits nothing outside itself):

1. `papadakis2018correlated`: add `pages = {537--548}` (Crossref); the
   note's "page range to be taken from the ACM record" is resolved.
   Title as Crossref and the paper print it: "Are Mutation Scores
   Correlated with Real Fault Detection? A Large Scale Empirical Study
   on the Relationship Between Mutants and Real Faults".
2. `offutt1996sufficient`: the note says "text not read"; it is now
   read in the GMU draft, whose title says "Mutation Operators" where
   the journal says "Mutant Operators". Keep the journal title, and set
   `note = {Read in the authors' draft, GMU technical report
   (cs.gmu.edu/media/techreports/ISSE-TR-94-00.pdf), 2026-11-16; the
   99.51\% average is the draft's Table 9}`.
3. `untch1993schemata`: `note` becomes "Read in a scispace copy,
   2026-11-16"; the copy prints the second author's name without its
   "ff" ligature, so check the name against the ACM record, not the
   copy.
4. `gopinath2015hard`, `papadakis2015tce`, `chekam2017threshold`,
   `just2014mutants`: venue and pages confirmed by Crossref (the
   authors' copies do not print them); the TCE copy's own metadata
   says 2014, which is the preprint's date, not the venue's.
5. `papadakis2019advances`: Crossref gives pages 275-378, year 2019,
   ISBN 9780128151211 and no volume; the preprint prints no volume.
   Keep `volume = {112}` only after it is read on the publisher's page
   for that ISBN; until then drop the field and add the ISBN.
6. `claessen2007coverage`: the record names the author "Koen Lindström
   Claessen"; the IEEE record and his other papers use "Koen
   Claessen". Use the form printed on the paper's first page once it
   is opened; until then keep `Claessen, Koen` with a note naming the
   record's form. Booktitle: "Formal Methods in Computer Aided Design
   (FMCAD 2007)", Austin, Texas.
7. `serrestou2007rtl`: unchanged and still flagged; the paper was not
   opened, so "three authors" remains an inference from the run-on
   name.
8. `wong1995reducing`, `ammann2014minimal`, `budd1982correctness`,
   `hamlet1977compiler`, `offutt1992coupling`, `jia2009hom`,
   `hoskote1999coverage`, `kupferman2003vacuity`, `lisherness2010scemit`:
   not opened; enter them only if a sentence cites them, and then only
   at title level, as the table says.
9. `jasper2025buggen`: add the v2 date (2025-06-18) to `note`.
10. `foster2025ach`: `note` gains "Industrial authors (Meta)".
11. `lin2012epa`: the note's 33-61% figure was not seen in this
    reading; the 14% CPU-time figure was. Print only the latter.
12. New entries: `budd1980theoretical` (Budd, Timothy A. and DeMillo,
    Richard A. and Lipton, Richard J. and Sayward, Frederick G.,
    "Theoretical and Empirical Studies on Using Program Mutation to
    Test the Functional Correctness of Programs", technical report
    GIT-ICS-80/01, Georgia Institute of Technology, February 1980,
    url https://apps.dtic.mil/sti/pdfs/ADA083078.pdf, accessed
    2026-11-16; the given names from the report's title page, to be
    checked there); `yosys-mutate` (YosysHQ, "mutate" command help,
    Yosys 0.68 git 38e001a6f, read locally, no URL; or the online
    command reference page once found); the Verilator keys
    `verilator-exe-verilator` and `verilator-exe-sim` already exist.
13. `mcy-docs`: the methodology page does not describe `-list` or
    `-ctrl`; those come from `mutate.html`. The note's description is
    right as a whole; attribute per page in the chapter.
14. Vendor labels: `hampton2009fq`, `springsoft-fq`,
    `synopsys-certitude` (vendor); `hampton2007certitude` (peer-reviewed
    venue, vendor authors); `yosys-ap400` (vendor application note).

## 8. Gate-1 checklist (against AGENTS.md)

| requirement | where met |
|---|---|
| every section names what the reader must be able to do | "Reader can" in 3.1-3.10; objectives 1-9 map to 3.1-3.2 (1), 3.3 (2), 3.4-3.5 (3), 3.5 (4, 5), 3.6 (6), 3.7 (7), 3.8 (8), 3.7 pitfalls and 3.9 (9); 3.10 exercises 2, 3, 4, 6 together |
| the research note's constraints are folded in | RN Q1 (D2), Q2 (D1, 3.1), Q3 (D4, D15, 3.5), Q4 (D4, D9, 1.2(2), 1.2(5)), Q5 (D3, 1.2(3)), Q6 (D5, 1.2(4), 3.8), Q7 (3.6); RN 2.2(1)-(5) are 3.1, 3.7, 3.4-3.5, 3.7 pitfalls, 3.8; RN 6 confidence notes applied: read vs metadata (section 7), second-hand numbers labeled or dropped (Wong-Mathur, 10-40%, 99.5%), BugGen's 104 not printed, GateTruth as preprint, MCY's filter as bounded, one design only (3.9 and 3.1 wording), timing-dependent verdicts (bounded kills never called survivals; seconds not printed as facts), `m05` as its own class, Verilator initialization (corrected in 1.2(5)), Yosys modes measured not documented; O1-O6 answered by D3, D6, D7, D5, D8, D13 |
| a question that changes the chapter's shape is raised, not chosen | none: the eight items of 1.2 change numbers, sentences and example construction, not sections. The one reading the author may want to overrule (design doc "MCY on the book's designs" read as MCY's method) is recorded in 1.2(3) and changes no section either way |
| escalate: an earlier approved chapter wrong | no (1.3: `m44` and `Sync_A`, `m35` and Chapter 21, both consistent) |
| house template | epigraph, objectives, motivation (3.1), concepts (3.2-3.9), worked example (3.10), callouts of six kinds only (census under Budget), future directions (3.11), summary (3.12), exercises (3.13), further reading (3.14) |
| every listing a file under `examples/` | section 4; mutants are generated at run time from the shipped RTL by path; the new data check is a file in this chapter's directory |
| simulator output from `run.out` | every number is a line of an example's `run.out` or of a committed `measure.out` from its `MEASURE=1` run (D12, section 4); the research lines cited here are evidence |
| every number sourced | research outputs cited by file and line; literature numbers only from sources marked read in section 7; nothing printed from a source marked not opened |
| vendor figures labelled | Certitude sources labeled vendor in 3.2 and 3.9; AppNote 400 labeled vendor; no vendor figure is printed (none exists in the sources read) |
| 80 columns, 72-column rulers, real tabs | section 4 preamble |
| cross-references by label, later chapters by name | section 6; labels checked against the chapters on 2026-11-16 (`sec-ch08-where`, `sec-ch08-example`, `sec-ch08-code-coverage`, `sec-ch09-example`, `sec-ch09-vacuity`, `sec-ch18-bmc`, `sec-ch18-induction`, `sec-ch18-helper`, `sec-ch18-ic3`, `sec-ch19-mutation`, `sec-ch19-track`, `sec-ch21-clean`, `sec-ch21-seed`, `sec-ch21-example`, `sec-ch34-evaluation`, `sec-ch01-example`, `sec-ch11`) |
| American spelling | to hold in the draft ("behavior", "modeled", "favoring") |
| attribution and originality | section 7; no figure redrawn from a source; at most one short quotation from MCY's docs |
| the book never cites its working documents | chapter cites `refs.bib` keys and splices `run.out` / `measure.out`; never `research/` |
| publication rule | no assistant or vendor of one named in this outline or the planned files |
| registration in `_quarto.yml` | new part "Part V · Borrowed from Software" between Part IV and Part VII, this chapter its first entry, before `chapters/ch34-generative-ai-agentic-dv.qmd` |
| 8-12 exercises with determinate answers | section 5: twelve; four depend on preconditions and are cut if those fail, leaving at least eight |
| examples under about 90 s | section 4 times; every research run that exceeded it is redesigned (schema, sample, split) or moved to `MEASURE=1` (1.2(6), 1.2(7)) |
| new glossary terms | mutant, mutation operator, kill (strong, weak), mutation score, equivalent mutant, duplicate mutant, miter, mutant schema, fault model, reach / infect / propagate / reveal, kill rate, equivalent fraction, EQGAP (as MCY's term), trivial compiler equivalence |

Gate-1 verdict proposed for `STATUS.md` (written by the session that
records the gate, not by this outline): passes under the delegation on
2026-11-16, with section 9's preconditions P1-P10 required before the
sections that use them (P1 for 3.3-3.4, P2 for 3.6, P3 and P8 for 3.5,
P4 for the 3.5 Pitfall, P5 for 3.10, P6, P7, P9, P10 for exercises and
the 3.7 Pitfalls).

## 9. Measurements needed before drafting

Each becomes a line of an example's `run.out` (or `measure.out`); none
was run for this outline, which made no measurements. Run on the book's
machine with the pinned tools; record wall time for each example.

| # | measurement | needed by | pass condition / what to do if it fails |
|---|---|---|---|
| P1 | Source schema: generate it, build the four testbenches, run the 45 selections; compare the 44 x 4 matrix with `src-mutants/sim.tsv` cell by cell; time the whole example | 3.1, 3.3, 3.4, `source-sim/`, `rand-init/` | identical matrix and under 90 s. If `m05`, `m06` or `m07` cannot be expressed in a schema that Verilator accepts with the book's flags, build those three as separate single-edit copies inside the same example (3 extra builds, ~30 s) and say so in the example's header |
| P2 | Property set on the 44 source mutants with depth-bounded BMC (depth 20 covers every first kill in `src_formal.tsv` except `a_integrity`'s 33 on `m03`, which other properties kill earlier) and stop-at-first-failure; time it | 3.6, `property-set/` | the kill set equals RN M4 (38 counterexamples, 2 refusals, `m44` by `Sync_A`, no kill of `m05`, `m32`, `m36`, `m43`); if over 90 s, split by halves; the full matrix under `MEASURE=1` |
| P3 | `m43`: k-induction on the miter alone (expected: fails); with `count <= DEPTH` proven and assumed (expected: proves); rIC3 alone; each with its time | 3.5, `equiv-invariant/` | if induction with the helper does not prove it, drop the induction contrast and keep rIC3 |
| P4 | `rand-init/` without `--x-initial unique` (the documented default), `+verilator+rand+reset+2`, seeds 1-5 | 3.5 Pitfall | result equals `rand_init.log:2-10`; if not, the example keeps the explicit flag and the Pitfall's sentence about the default is rewritten from what the run shows |
| P5 | Fifth testbench: control on repaired and original FIFO; source schema at default and randomized initial values; n = 1000 netlist sample | 3.10, `fifth-tb*/` | control passes the repaired FIFO and fails the original; whatever the kill counts are, the section is written from them (expected 37/44, 40/44, netlist near or above 0.89) |
| P6 | Chapter 1 random testbench on `m35`, seeds 1..N until killed (the schema build, `+mut=35`) | exercise 11, 3.4 Pitfall | a seed under 100 is found; else the exercise asks for the fraction of seeds 1-100 that kill it |
| P7 | Yosys netlist identity of each source mutant with the original and with each other (same script, `opt -purge`, compare `write_verilog -noattr` output or a structural hash) | exercise 5, 3.5 TCE sentence | any result; the exercise's answer is what it prints |
| P8 | `m05` under a Verilator testbench that drops `rst_n` between clock edges and samples `empty` before the next edge | 1.2(2), 3.5, exercise 10 | killed: keep "not equivalent in silicon" and exercise 10; survived: cut both |
| P9 | `harness-pitfalls/`: one select-bit mutation that the pragma assertion kills in the checkless testbench, with and without `--no-assert-case`; the duplicated `+seed=` demonstration | 3.7 Pitfalls | both demonstrations reproduce the research behavior; else the Pitfall cites the population numbers only, from `netlist-population/` |
| P10 | The miter comparing `rd_data` on every cycle, original against itself | exercise 9, 3.5 Pitfall | reports a difference at a small depth; the exercise answer is that depth |
| P11 | Times of `netlist-list/`, `netlist-sample/` (sampled schema build), `miter-differ/`, the four rIC3 examples run alone | section 4 | each under 90 s, or split as section 4 says |
| P12 | `netlist-population/` cross-check: the n = 1000 sample's verdicts against the committed `pop.tsv` | 3.8 | 1000 of 1000 agree; any disagreement means the harness or a tool changed, and the committed file is regenerated under `MEASURE=1` before anything is spliced |

## 10. Pre-draft measurements

Run 2026-11-16 on the book's four-core machine with Verilator 5.052,
Yosys 0.68 (git 38e001a6f), InFormal 0.1.0 at `5114330` with rIC3 and
Python 3.13, through `scripts/check-examples.sh
ch25-mutation-testing/<name>` unless a command is given. Every example
directory is under `examples/ch25-mutation-testing/`; "run.out" below
means that directory's `run.out`. Times are wall-clock seconds of one
`make run` on an otherwise idle machine, measured for this section and
printed in no `run.out` (they depend on load). Each entry says whether
the sentence of sections 1-5 that depends on it **stands**,
**changes** or is **cut**.

| # | command | result | dependent sentence |
|---|---|---|---|
| P1 | `source-sim/` (`python3 -I -B sim.py`; the schema of `common/srcmut.py`, 4 builds, 45 x 4 runs) | the 44 x 4 matrix equals `src-mutants/sim.tsv` cell for cell (pinned in the run); control survives all four; kills 34 / 35 / 0 / 22, union 37; survivors `m05 m09 m11 m13 m32 m36 m43`. `m05`, `m06`, `m07` all expressed in the schema (no separate builds needed): `m05` as `rst_a`, held at 1 when selected, in the sensitivity list with the body still testing `rst_n`; `m06`/`m07` as a selected `if` condition. The schema draws UNSIGNED and WIDTHEXPAND, built with `-Wno-fatal`. 13.5 s | 1.2(6) **stands**; the fallback (three single-edit builds) is not needed, and the example header says how the three are expressed |
| P1 (cont.) | `MEASURE=1` in `source-sim/`: 180 per-mutant builds (`-Wno-fatal`), as RN M1 ran them | 44 of 44 rows of the per-mutant matrix equal the schema's; 1,685 s of build time summed over 4 workers, 427 s wall (RN: 1,704 s, 433 s). Committed as `source-sim/measure.out`; every default run compares its matrix with it | 3.3's cost sentence (180 builds, about 1,700 s of build time) **stands**, spliced from `measure.out` |
| P2 | `property-set/` (`props.py`: properties one at a time in the fixed order `EmptyExact_A Sync_A a_integrity EmptyPtrs_A FullBackward_A NoOverflow_A FullForward_A PushFull_A PopEmpty_A`, `informal-bmc` 2 s each, stop at the first counterexample; InFormal has no depth bound, so "depth-bounded" is a time bound) | control: no counterexample; 38 counterexamples, `m06`/`m07` refused by the front end with RN's message, no counterexample for `m05 m32 m36 m43`; `m44` first killed by `Sync_A` at depth 2. First killers: `EmptyExact_A` (flag and counter mutants), `a_integrity` (data and pointer-reset mutants), `FullBackward_A` (`m39`-`m42`, `m42` at depth 18). 62 s. `MEASURE=1` (every property, 5 s each) wrote `measure.out`; the default run checks each first kill is among its refutations: 44 of 44 | 3.6's kill set **stands** (equals RN M4). One detail **changes**: the full 5 s run did not refute `a_integrity` on `m03` (RN: depth 33), so "`a_integrity`'s 33 on `m03`" is not reproduced at 5 s and is not printed |
| P3 | `equiv-invariant/` (`invariant.py`, six runs on the `m43` miter) | bounded search 3 s: no verdict; k-induction on the whole miter 10 s: no verdict; helper `a.count <= 16 && b.count <= 16`: proven by k-induction at once; whole miter with the helper assumed, k-induction 10 s: **no verdict**; the flag half alone (`full`, `empty` compared, no `rd_data`), k-induction, no helper: **proven** (about 1 s); rIC3 on the whole miter: proven (about 20 s). A further probe outside the example (pointer equalities and `a.count == b.count` assumed too) also gave no k-induction verdict in 10 s: the `rd_data` comparison needs an invariant about the memory words between the pointers, which free initial memory makes hard to state | 3.5's "the example shows k-induction failing alone and succeeding with `count <= DEPTH` proven first" is **cut** (pass condition failed); the example keeps the contrast as measured: the helper is not enough, rIC3 finds what is. Exercise 6 **changes**: its first half stands (bounded search only refutes); its second half becomes "k-induction proves the flag half of `m43`'s miter with no helper but not the whole miter even with `count <= 16`; what does the `rd_data` comparison need that the flags do not?" or is cut |
| P4 | `rand-init/` (`randinit.py`: the book's flags, no `--x-initial`, `+verilator+rand+reset+2`, `+verilator+seed+1..5`, the seed given once: the testbench's own `+verilator+seed+1` is replaced, not followed) | identical to `rand_init.log:2-10`: `m09`, `m11` killed by directed and random at seeds 1-5; `m13` also by Chapter 9's checker; `m44` by the checker at default and randomized values; `m05 m32 m36 m43` and the control survive every run. 17 s | 1.2(5) **stands**: the plusarg alone, under the documented default, kills the three; the example uses the book's flags unchanged plus the plusarg. Note for the drafter: RN M7's harness appended `+verilator+seed+S` after the Chapter 8 and 9 testbenches' own `+verilator+seed+1`, the duplicated-plusarg pattern of D10; the example avoids it and reproduces the same table, so RN's numbers stand |
| P5 | `fifth-tb/` (`fifth.py`; `fifo_data_sva.sv` judges pushes and pops by the contract at the ports, `wr_en && !full`, `rd_en && !empty`, keeps a queue and asserts `Data_A` on every accepted pop; bound beside Chapter 9's checker on Chapter 9's traffic, both read by path) | control: passes the repaired FIFO, fails Chapter 1's original (first failure `FullBackward_A`); source mutants: checker as shipped 22/44 default, 23/44 randomized; fifth 37/44 default (survivors `m05 m09 m11 m13 m32 m36 m43`), **40/44** randomized (survivors `m05 m32 m36 m43`); newly killed `m08 m10 m14`-`m25 m33`; netlist sample n = 1000 (seed 1): checker 39/1000 [0.028, 0.053], fifth **899/1000 = 0.899 [0.879, 0.917]** (random test 896, union of the four 900). Writes `tbl-ch25-report.md`. 43 s; `fifth-tb-netlist/` not needed and not created | 1.2(8)'s expectations **stand** exactly (37/44 and 40/44; netlist "near or above 0.89": 0.899). One small **change**: `m35` was already killed by the checker as shipped (`sim.tsv:37`), so "`m35` dies because this traffic drains the FIFO" is true of the traffic but not news of the fifth testbench; the newly killed list above is what 3.10 should name |
| P6 | `source-sim/`: `ch01-random` on the schema at `+mut=35`, seeds 1-100, each the only `+seed=` | first killing seed **2**; 53 of 100 seeds kill `m35` | exercise 11 **stands** (answer 2); 3.4 Pitfall may say "seed 2 kills it; about half of seeds 1-100 do" |
| P7 | `source-mutants/` step 4: each single-edit copy and the original through `prep -top fifo; opt -full; opt_clean -purge`, netlist as JSON, a Weisfeiler-Lehman hash over cells and bits (internal names ignored). A plain `write_verilog` text comparison was tried first and found nothing, because Yosys numbers and orders internal wires differently even for identical structure; a gate-level variant (`synth; abc -g AND`) also found nothing, `m32` included | identical to the original: **`m32` only**; `m36` is not (`$le` against `$logic_not`/`$eq` survives `opt -full`); `m06` and `m07` are **refused by Yosys** ("Async reset \rst_n yields non-constant value 4'mmmm for signal \wr_ptr"), as by InFormal's front end, so the expected duplicate pair cannot be seen by synthesis; no duplicate groups among the other 41 | exercise 5 **changes**: answer "`m32` is identical to the original; no two others are duplicates; `m06`/`m07` are refused by the synthesis front end (so the pair whose source differs only in `!(!x)` against `x` is not collapsed by this route)". 3.5's TCE sentence **changes** accordingly: TCE by synthesis finds one of the five equivalents on this file |
| P8 | `equiv-reset/` (`reset.py`; `tb_async_reset.sv` pushes three words, drops `rst_n` 1 ns after a falling edge for 2 ns, reads `empty` 1 ns before the next rising edge; built once against the source schema) | the repaired FIFO: `empty=1`, passes; `m05`: `empty=0`, **killed**. The miter: bounded search 3 s no verdict, rIC3 proves `m05` equivalent. 34 s | 1.2(2)'s "the designs are not equivalent in silicon" may **stand**, resting on this run; exercise 10 **stands** (answer: yes) |
| P9 | `harness-pitfalls/` (`pitfalls.py`) | (a) the two `const1` mutations of a select bit of the counter's `$pmux` (numbers 7572 and 7576 of the list): built without `--no-assert-case`, Chapter 8's checkless testbench "kills" both (Verilator: "synthesis parallel_case, but multiple matches found for '2'h3'"); with it, both survive; control survives both builds. (b) `tb_plusarg.sv` with `+seed=1 +seed=7` prints 1; Chapter 1's random test on source `m35` (schema): `+seed=2` kills, `+seed=1 +seed=2` survives. 39 s | both 3.7 Pitfalls **stand**, each with a demonstration that reproduces RN's behavior; (b) now uses the book's own testbench and a source mutant, which is clearer than the population numbers |
| P10 | `miter-differ/`: the miter with `rd_a == rd_b` on every cycle, the original against an unmutated copy | differs at **depth 1** | exercise 9 **stands** with answer depth 1 |
| P12 | `netlist-sample/` (`sample.py`): the n = 1000 uniform sample (seed 1) as its own `-ctrl` netlist of 1,000 mutations (5,620 lines), four builds, 4,004 runs | **1000 of 1000** sampled mutations have exactly the four verdicts of `netlist-population/pop.tsv`; kills at n = 30, 100, 300, 1000 equal `sampling/run.out:7-10` (directed 30/100 [0.212, 0.400], random 89/100, checker 4/100; n = 1000: 302, 896, 0, 39, union 900). `pop.tsv` itself was regenerated by `MEASURE=1` in `netlist-population/` (3 min) and is byte-identical to `research/ch25-measurements/yosys-mutants/pop.tsv`; the Yosys list is byte-identical to `mutants.txt.gz`. 22 s | 3.8 and exercise 1 **stand**. The nested-sample claim holds: for these sizes `random.sample` draws one at a time, so seed 1's first 100 of 1,000 is RN's sample of 100 |
| P11 | every directory alone through `check-examples.sh`, from clean, second of two runs | seconds: `common` 13, `equiv-invariant` 22, `equiv-outright` 25, `equiv-reset` 32, `fifth-tb` 44, `harness-pitfalls` 38, `miter-differ` 20, `netlist-formal` 25, `netlist-list` 1, `netlist-population` 13, `netlist-sample` 21, `opening` 24, `property-set` 63, `rand-init` 12, `source-mutants` 2, `source-sim` 13, `white-box` 34; `MEASURE=1`: `source-sim` 427 s wall, `property-set` 419 s, `netlist-population` 179 s, `netlist-formal` 715 s. Two clean runs give byte-identical `run.out`, tables and committed outputs | section 4 **changes**: everything is under 90 s, so `fifth-tb-netlist/` is not split out; its netlist half (the n = 1000 sample before and after) is step 3 of `fifth-tb/` |
| 1.2(4) | `MEASURE=1` in `netlist-formal/` (`nformal.py`): the 100 mutations drawn at seed 25; per mutation the property set (`informal-bmc` 3 s per property) and the miter (`informal-bmc` 10 s, then `ric3-ic3` 120 s); the default run recomputes the summary from `measure.out` and `pop.tsv` and reruns four rows by rIC3 | equivalent **6/100 = 0.060 [0.022, 0.126]** (252 264 1188 3618 5877 7345, none killed by anything); over the 94 non-equivalent: directed 26/94, random 93/94 = 0.989 [0.942, 1.000], Chapter 8's 0/94, checker 7/94, property set **80/94 = 0.851 [0.763, 0.916]**, sim + formal 94/94. The 14 the property set misses differ at depth 16 to 31; the two at depth 31 (8394, 7759, memory write muxes) were found by rIC3, not by the 10 s bounded search, and the default run finds them again at depth 31 | 1.2(4) **changes**: property set 80/94, 0.851 [0.763, 0.916] (not 79/94, 0.840 [0.750, 0.908]); "the 15 ... depth 15 to 31" becomes "the 14 ... depth 16 to 31". The equivalent fraction, random score and naive-ratio sentences **stand**. In Practice: "13 min" becomes "12 min" (715 s) |
