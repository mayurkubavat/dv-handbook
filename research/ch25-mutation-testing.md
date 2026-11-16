# Research note: Mutation Testing: Qualifying the Testbench (Chapter 25)

Date: 2026-11-16. Status: research for gate 1 (no outline yet).
Written section by section, the deciding questions first. Sections:
1 questions that decide the chapter, 2 measurements (results table;
scripts and saved outputs under `research/ch25-measurements/<name>/`),
3 topics (theory, surveys, empirical evidence, HDL mutation, mutation of
formal property sets, equivalent-mutant detection, LLMs, coverage and
statistics), 4 the worked-example spine, 5 bibliography (BibTeX-ready),
6 confidence notes, 7 open questions for the outline.

Scope given: design doc section 4, entry 25: "Mutation Testing:
Qualifying the Testbench -- fault models, equivalent mutants, kill rate
beside coverage; MCY on the book's designs". Part: Borrowed from
Software, beside property-based testing and fuzzing.

What earlier chapters already teach and this chapter cites by label,
not repeats: coverage measures activation, not propagation or
detection, with the vendor's three conditions quoted as the vendor's
and Huang et al. as the independent statement (`@sec-ch08-where`); the
FIFO coverage model that checks nothing (`@sec-ch08-example`); the
Chapter 9 checker and its two FIFOs, the original being in effect a
mutant the checker kills with `FullBackward_A` (`@sec-ch09-example`);
"mutation of the design" as a formal technique, three `sed` mutants of
the repaired FIFO against the Chapter 9 checker, `EmptyPtrs_A` and the
tracked-word check, with DeMillo-Lipton-Sayward and Chockler et al.
cited and the method in full deferred to this chapter
(`@sec-ch19-mutation`); Clopper-Pearson, the rule of three, and the
FIFO bug's per-seed detection probability (`@sec-ch21`, its bounds
section). This chapter must not contradict any of them; it supplies
the method they each point at.

Pins for every measurement: Verilator 5.052 (the book's flags from
`examples/mk/sv.mk`), Yosys 0.68 (git 38e001a6f) for netlist mutation
with its `mutate` pass, InFormal 0.1.0 at commit 5114330 with its
in-house engines and rIC3 for formal, Python 3.13.18 standard library.
Icarus 13.0 is installed but rejects Chapter 1's random testbench
("Overriding the default variable lifetime is not yet supported"), so
every simulation here is Verilator. MCY is not installed in
`/opt/dvtools`; see Q5.

## 1. Questions that decide the chapter

These are the choices the outline must make; each changes what
sections exist or what the worked example has to carry. Measurement
numbers in brackets point at section 2.

**Q1. Which fault model does the chapter teach first: source-level
operators or MCY's netlist bit flips?** The two give different
populations of the same FIFO and different pictures. The source-level
set (the selective operators of Offutt et al. plus statement deletion
and three HDL operators) gives 44 mutants a reader can read one by
one, each with a sentence ("the reset of `count` deleted"), and a
complete equivalence classification by miter [M1-M4]. Yosys's `mutate`
pass, the fault model MCY drives, gives 9,281 single-bit mutations of
the synthesized netlist (`inv`, `const0`, `const1`, `cnot0`, `cnot1`
on cell ports) [M6], which nobody reads individually and which force
sampling, and therefore the statistics. Recommendation: source-level
first, because equivalence and "real gap" can only be taught on
mutants the reader can read; netlist mutation second, as the
industrial-scale population where sampling and confidence intervals
become necessary. MCY is named as the tool that packages the second
(Yosys `mutate` plus a database and a formal filter), and the chapter
shows the mechanism with Yosys alone, since MCY is not in the book's
toolchain (Q5).

**Q2. What does "killed" mean for a testbench that has no checker?**
Chapter 8's FIFO coverage testbench kills 0 of 44 source mutants and
0 of the 9,281 netlist mutations (it cannot fail by construction,
once a Verilator pragma assertion is switched off [M6a]) while
reporting functional coverage; Chapter 1's directed test, which covers
eight entries and checks them, kills 34 of 44 [M2]. This is the
chapter's opening fact and the cleanest available demonstration of
Chapter 8's "coverage measures activation only". The outline must
decide whether to print "0 of 44" beside the coverage percentage in
the first section (recommended: yes, as the motivating table, with
the code-coverage numbers of the same runs beside it [M5]).

**Q3. Is an equivalent mutant defined at the ports, or against the
property set?** The measurement found a mutant (`m44`, the two case
labels of the counter exchanged) that is equivalent at the ports
(proved by miter with rIC3: the counter holds minus the occupancy
modulo 32, and full and empty test only 0 and 16, the two fixed points
of negation) yet is killed by Chapter 9's `Sync_A`, which compares
the checker's occupancy with the design's internal `count` [M3, M4].
Under MCY's terminology that is an EQGAP, "should never occur in a
correct setup". So the chapter must choose a definition of
equivalence (observable behavior at the ports under the contract,
which is what the miter compares) and then say what a kill by a
white-box property means: the checker constrains the implementation,
not the specification. Recommendation: define equivalence by the
miter's comparison, print the comparison as part of the definition
(rd_data is compared only when the FIFO is not empty), and teach
`m44` as the over-specified-checker pitfall.

**Q4. Which equivalences does the chapter call equivalent: absolute,
under reachability, or under the tool's model?** Of the seven source
mutants no testbench kills, the miter separates three kinds [M3]:
`m32` (the `default` hold assignment deleted) and `m36` (`count <=
'0` for `count == '0` on an unsigned count) are equivalent outright;
`m43` (`count >= 16` for `count == 16`) is equivalent only because
the count never exceeds 16, which a proof has to establish (rIC3
proves it; BMC never could); `m05` (the asynchronous reset made
synchronous) is equivalent under InFormal because the tool models an
asynchronous reset as synchronous, not because the designs agree.
And three more (`m09`, `m11`, `m13`, a reset assignment deleted)
survive every testbench only because Verilator starts every register
at zero: the miter, whose registers start free, distinguishes them at
depth 1-2, and Verilator with randomized initial values kills them
[M3, M7]. The outline must say whether the simulator's initialization
semantics are part of the oracle (recommended: yes, as a Pitfall with
its own measurement), and whether "equivalent under the tool's reset
model" is reported as equivalent (recommended: no; reported as its
own class, with the tool limitation stated).

**Q5. MCY or the book's own driver?** MCY is not installed in
`/opt/dvtools`. It is a single Python script (1,028 lines at upstream
commit 5a2cad0, 2026-08-04) needing `click` (and `flask` for the
dashboard) and, for its equivalence step, SymbiYosys, which the book
replaced with InFormal (decisions log, 2026-11-15). Its clone works
through the proxy, so it is buildable, but adopting it brings back
SBY for the filter and a second Python dependency. Its mechanism is
reproducible with Yosys alone: `mutate -list` for the population and
`mutate -ctrl` to put every mutation behind one select input, so each
testbench is built once and run 9,282 times [M6]. Recommendation: the
chapter teaches the mechanism on Yosys plus InFormal miters, names
MCY as the tool that packages it with its tags (COVERED, UNCOVERED,
NOCHANGE, EQGAP) and its BMC-based filter, and does not make it a
dependency. This needs the author's agreement only if the design
doc's "MCY on the book's designs" is read as a promise to run MCY
itself (open question O1).

**Q6. Does the chapter report a mutation score from a sample, and with
what interval?** On the netlist population the true kill rate of each
testbench is known (every mutant run), so the chapter can show the
Clopper-Pearson interval of the statistics chapter on a sample of n
and check its coverage against the truth [M8]. Recommendation: yes, a
section that reuses `@sec-ch21`'s interval by name, with the population
result as the check, and Gopinath et al.'s ~1,000-mutant rule stated
with its assumptions. The deciding sub-question: the interval is for
the kill rate over all mutants; the mutation score over non-equivalent
mutants needs a second estimate (the equivalent fraction, from a
formal sample), and the ratio of two estimates has a wider interval
[M9]. The outline must decide whether to carry the ratio or report
kill rate and equivalent fraction separately (recommended: separately;
the ratio's interval as an exercise).

**Q7. How much of the formal side belongs here rather than in the
formal chapters?** `@sec-ch19-mutation` already runs three mutants
against the property set. This chapter adds what that section defers:
the property set's kill rate over a population beside each
simulation testbench's [M4], the survivors classified by miter, and
mutation as property-set completeness (Hoskote et al., Chockler et
al., Große et al., Claessen) with vacuity as the degenerate case.
Recommendation: one section, on the same FIFO, citing
`@sec-ch19-mutation` for the procedure, with the miter (the formal
tool used as an equivalence checker) as the chapter's own technique.

## 2. Measurements

Every script and its saved output is under
`research/ch25-measurements/`. `mutlib.py` holds the four testbenches
as the book ships them (read in place under `examples/`, never
copied) and a runner that builds one testbench against one design on
Verilator 5.052 with the book's flags and returns killed, survived,
timeout or stillborn. The design under mutation is the repaired FIFO,
`examples/ch09-temporal-properties/rtl/fifo_fixed.sv`, because a
mutant of Chapter 1's buggy FIFO would be judged against a testbench
that already fails (MCY's prerequisite: "the test suite must pass on
the original design"). Chapter 1's testbenches instantiate `fifo` and
take the repaired file in place of the original, as its header says.
Every run has a control: the unmutated design passes all four
testbenches and the property set in every script. Build directories
are deleted by each script; nothing under `examples/` was written.

The testbenches, as run (kill = non-zero exit or no PASS line):
- **ch01-directed**: `tb_fifo_directed.sv`, eight pushes and eight pops
  with data compared, `empty` checked at the end.
- **ch01-random**: `tb_fifo_random.sv` at `+seed=1`, 400 cycles, queue
  reference model checking data and both flags (the version after
  commit 1f290b8, flags judged before the edge).
- **ch08-coverage**: `tb_fifo_cov.sv`, runs A (even) and B (push
  biased), 200 cycles each, seed 1; covergroups, no checker.
- **ch09-sva**: `tb_fifo_sva.sv` with `fifo_sva.sv` bound, 400 cycles,
  seed 1; occupancy and flag assertions, no data check.
- **property set** (formal): Chapter 19's `mutants/` set on InFormal
  5114330, `informal-bmc` with a per-property limit (5 s source, 3 s
  netlist): the Chapter 9 checker bound, `EmptyPtrs_A`, and the
  tracked-word `a_integrity`, through the book's `examples/mk/informal.sh`.

### 2.1 Results table

| # | Experiment | Result | Where |
|---|---|---|---|
| M1 | 44 source mutants (`src-mutants/mutate_src.py`): LCR 2, LNR 3, CNG 3, ROR 10, AOR 4, CRP 7, SDL 9, VSW 4, ARS 1, CSW 1, every site of each operator in the module body | All 44 compile on Verilator with `-Wno-fatal`; 7 draw a warning that the book's `-Wall` lint makes fatal (`m15` UNDRIVEN, `m18 m23 m27 m30` WIDTHEXPAND, `m35 m38` UNSIGNED), so lint alone "kills" 7. 180 builds (44 + control, x4): 1,704 s of build time, 1.1 s of simulation, 433 s wall on 4 cores | `src-mutants/mutants.tsv`, `sim.tsv`, `run_sim.log` |
| M2 | Kill rate per testbench, source mutants | directed 34/44 (77.3%); random 35/44 (79.5%); coverage **0/44**; SVA checker 22/44 (50.0%); union 37/44 (84.1%). The SVA checker kills no mutant of the data path (`m14`-`m25`, `m33`) and every non-equivalent counter or flag mutant except `m13`. Random misses `m35` (`empty` stuck at 0), directed kills it: seed 1 never drains the FIFO after the first push ("16 of 17 occupancy levels", level 0 missing). Directed misses `m12` (count resets to 31) and `m42` (`count > 16`, full never raised) | `src-mutants/sim.tsv` |
| M3 | Miter (repaired FIFO vs mutant; full, empty always, rd_data when not empty) on InFormal: BMC 10 s, in-house IC3 30 s, rIC3 120 s | 37 differ (all by BMC, depth 1-17; `m42` at 17); 5 equivalent, all by rIC3 in about 20 s after the in-house IC3 gave no verdict in 30 s: `m32` (default hold deleted), `m36` (`<=` for `==` on unsigned), `m43` (`>=` for `==`, needs count <= 16 proved), `m05` (async reset made sync: equivalent only under the tool's synchronous reset model), `m44` (case labels exchanged: count = -occupancy mod 32, flags test only 0 and 16). 2 refused by the front end (`m06`, `m07`: "asynchronous reset 'if' condition does not match sensitivity list signal or edge polarity"; Verilator simulates them and every checking testbench kills them). The three reset-deletion mutants that every testbench passes (`m09`, `m11`, `m13`) differ at depth 1-2. A first run with the population simulation sharing the cores and rIC3 at 30 s left `m05`, `m32`, `m36` unknown | `formal/src_formal.tsv`, `run_src.log` |
| M4 | The property set against the source mutants, BMC 5 s per property | Kills all 37 non-equivalent mutants it can read, including `m09`, `m11`, `m13` (registers start free in InFormal) and `m35`; kills one equivalent mutant, `m44`, by `Sync_A` alone at depth 2 (a property on the internal counter, an MCY "EQGAP"). The script's summary line counts the two refused mutants among its 40 "kills"; 38 are counterexamples. Survivor runs cost 9 x 5 s; 468 s wall for 44 kills plus miters | `formal/src_formal.tsv` |
| M5 | Code and functional coverage of the repaired FIFO under each testbench (`--coverage`, points in `fifo_fixed.sv`) | directed: line 4/4, branch 6/6, expr 7/8, toggle 80/330 (24%); random: 4/4, 6/6, 8/8, toggle 329/330, occupancy 16 of 17; **coverage TB: 4/4, 6/6, 8/8, toggle 326/330, covergroup 75.86% (run A) and 89.66% (run B)**; SVA: 4/4, 6/6, 8/8, toggle 327/330, covers FullReached 113, PushFull 69, PopEmpty 51, Drained 96. Beside M2: the highest-coverage testbench kills nothing, the lowest-coverage one kills 77% | `coverage/run.out` |
| M6 | MCY's fault model with Yosys alone: `mutate -list 100000` on the `prep`ped FIFO, all mutations behind `mutsel` (`mutate -ctrl`, MCY's mechanism, and schemata in the software literature) | 9,281 mutations exist (`inv` 2,046, `const0` 2,046, `const1` 2,046, `cnot0` 1,573, `cnot1` 1,570; cells: `procmux` 5,742, no source cell 1,868, `procdff` 1,394, `add` 130, `eq` 65, `sub` 52, logic 30). Yosys replaces the memory by 128 registers (async-reset block), and 6,849 mutations (73.8%) carry the source tags of the memory's declaration, its write, its read and the clocked block (lines 29, 42, 43, 57, 36); 1,868 more carry no source tag. One 48,016-line netlist, generated in 22 s; four builds (87 s) and 46,410+ runs (102 s wall). Kill rates: directed 2,725 (29.4%), random 8,265 (89.1%), **coverage 0**, SVA 351 (3.8%), union 8,300 (89.4%). Random with seeds 1..3: 8,355 (90.0%), flat to seed 8 | `yosys-mutants/run_pop.log`, `pop.tsv`, `mutants.txt.gz` |
| M6a | A false kill: the first population run | Yosys writes each `$pmux` as a `casez` marked `synopsys parallel_case`; Verilator turns the pragma into an assertion, so a mutation of a select bit fails in any testbench. That run "killed" 383 mutations (4.1%) in Chapter 8's checkless testbench and inflated the SVA checker from 351 to 726. Rebuilt with `--no-assert-case` (concurrent assertions stay on). A second harness bug in that run, now fixed: the seed sweep passed `+seed=S` after the testbench's own `+seed=1` and `$value$plusargs` took the first, so seeds 2-8 were seed 1 | `yosys-mutants/run_pop_assert_case.log` |
| M7 | The seven sim-surviving source mutants and `m44`, Verilator `--x-initial unique` + `+verilator+rand+reset+2`, seeds 1-5 | Control passes all. `m09`, `m11` (pointer reset deleted): killed by directed and random under all 5 seeds; `m13` (count reset deleted): killed by directed, random and the SVA checker. `m05`, `m32`, `m36`, `m43` survive everything (as M3 says they must); `m44` killed only by the SVA checker. 1 min 54 s | `src-mutants/rand_init.tsv`, `rand_init.log` |
| M8 | Sampled kill rate with 95% Clopper-Pearson interval vs the known population rate | One sample of 100 (seed 1): directed 30/100 [0.212, 0.400] (truth 0.294), random 89/100 [0.812, 0.944] (0.891), coverage 0/100 [0, 0.036] (0), SVA 4/100 [0.011, 0.099] (0.038). Coverage of the interval over 2,000 samples: 0.945-0.998 at n = 30-1000 for the non-degenerate rates (conservative, as Clopper-Pearson is); mean width at n = 100: 0.185 (directed), 0.130 (random); at n = 1000: 0.057, 0.040. Gopinath et al.'s worst-case half-widths, Chebyshev / normal: 0.224 / 0.098 at n = 100, 0.071 / 0.031 at n = 1000. By mode (population, random TB): `inv` 0.925, `const0` 0.894, `const1` 0.883, `cnot1` 0.871, `cnot0` 0.869 | `sampling/run.out` s.1-s.3 |
| M9 | Formal sample: 100 uniform netlist mutations (seed 25), property set (BMC 3 s) and miter | 94 differ, 6 equivalent (rIC3), 0 unknown: equivalent fraction 0.060 [0.022, 0.126]; the six are three untagged cells, one write-mux cell (line 43) and two read-mux cells (line 57); none is killed by anything. Among the 94 non-equivalent: random 93 (0.989 [0.942, 1.000]), directed 26 (0.277), SVA 7 (0.074), coverage 0 ([0, 0.038]), property set 79 (0.840 [0.750, 0.908]); simulation and formal together 94 of 94. The 15 the property set misses differ only at depth 15-31 (memory slots that need filling, two found only by rIC3 at depth 31): a 3 s bounded search does not reach them. The one non-equivalent mutation random seed 1 misses (5012, a write-mux select) dies at seed 2 and to `a_integrity` at depth 6. 13 min wall | `formal/ysample.tsv`, `run_ysample.log`, `sampling/run.out` s.4 |

### 2.2 What the measurements say together

1. **Coverage and kill rate are different axes** [M2, M5, M6]. The
   coverage testbench has the best code coverage of the four and the
   second-best functional coverage report, and kills nothing, on
   either fault model. The directed test has 24% toggle coverage and
   kills 77% of source mutants. This is `@sec-ch08-where`'s argument
   made numerical on the book's own code.
2. **The fault model sets the score** [M2 vs M6]. The SVA checker
   scores 50% on the hand-readable source set and 3.8% on the netlist
   population, because three quarters of the netlist mutations carry the
   memory's source lines, and the checker never looks at data. A kill rate without its
   fault model, and the composition of its population, is not a
   number anyone can compare.
3. **Survivors split three ways, and only formal tells them apart**
   [M3, M4, M7]: real gaps in stimulus (`m35`), in checking (the data
   mutants against the SVA checker) or in the simulator's model
   (`m09`, `m11`, `m13` behind zero initialization); equivalents
   outright, under reachability, or under the tool's model; and one
   equivalent mutant a white-box property kills.
4. **The harness is part of the measurement** [M6a]. Two harness
   defects changed the population numbers by up to a factor of two
   before they were caught: a simulator pragma assertion that kills
   mutants in a testbench with no checker, and a plusarg that silently
   kept every seed at 1. Both were found because the result was
   implausible (a checkless testbench killing 4%; a seed sweep that
   added nothing). The chapter should teach "a kill you cannot explain
   is a harness bug until shown otherwise".
5. **Sampling works as the statistics chapter says** [M8], and the
   score needs two estimates [M9]: the kill rate (from simulation) and
   the equivalent fraction (from formal). The population's random-TB
   survivors are 10.9%; the formal sample puts equivalents at 6% [2.2,
   12.6]; their difference is the real gap, and its interval is wide
   at n = 100.

## 3. Topics

Each topic: what the primary source says (as read, with the access
date), the hardware translation, and where it touches the
measurements. Peer-reviewed sources and vendor sources are kept in
separate paragraphs; every vendor sentence is labeled.

### 3.1 Origins and the two hypotheses

Mutation analysis has two independent 1977-78 origins. Hamlet's
"Testing programs with the aid of a compiler" (IEEE TSE SE-3(4),
279-290, 1977; metadata from the publisher's Crossref record,
[Crossref, 2026-11-16](https://api.crossref.org/works/10.1109/TSE.1977.231145);
text not read) and DeMillo, Lipton and Sayward's "Hints on test data
selection" (`demillo1978mutation`, already in `refs.bib`). Jia and
Harman's survey attributes both founding hypotheses to DeMillo et al.
1978 [Jia and Harman, TSE 2011, read in a course-hosted copy,
2026-11-16](https://web.eecs.umich.edu/~weimerw/2020-481F/readings/mutation-testing.pdf):

- **Competent programmer hypothesis.** Programmers write programs
  close to correct, so real faults are small syntactic deviations that
  a few small changes would correct. Mutation operators model those
  deviations.
- **Coupling effect.** Test data that detects all simple faults also
  detects a high share of complex ones. Offutt formalized it as the
  coupling effect hypothesis and the *mutation* coupling effect
  hypothesis and tested it empirically ("Investigations of the
  software testing coupling effect", ACM TOSEM 1(1), 5-20, 1992;
  metadata from [Crossref, 2026-11-16](https://api.crossref.org/works/10.1145/125489.125473);
  text not read, the survey's account used).

Hardware translation: the competent-designer hypothesis is plausible
for RTL in the sense the FIFO shows (Chapter 1's bug is one constant,
`LAST` for `DEPTH`, and the repair is one width), and it is the
justification for single-change mutants; the coupling effect is what
lets a team infer from killing simple mutants that the testbench
would catch the compound bug. Neither has been tested on hardware in
any source found; the chapter states them as software hypotheses.

**Definitions the chapter needs** (all from Jia and Harman unless
noted): a mutant is *killed* by a test when the test's result differs
from the original's; *strong* mutation compares outputs, *weak*
mutation compares state immediately after the mutated point (Howden
1982, via the survey), *firm* in between. The **mutation score** is
killed mutants over non-equivalent mutants. The reachability /
infection / propagation conditions (RIP, extended to RIPR with
revealability in the later survey) are exactly the three conditions
the Certitude vendor names as activation, propagation and detection
(`@sec-ch08-where` quotes them as the vendor's). The chapter can show
that correspondence as one table: RIP is the peer-reviewed name;
"activation / propagation / detection" is the vendor's.

### 3.2 Equivalent, duplicate and subsumed mutants

- **Equivalent mutants** are undecidable in general: Budd and Angluin,
  "Two notions of correctness and their relation to testing" (Acta
  Informatica 18(1), 31-45, 1982; [Crossref, 2026-11-16](https://api.crossref.org/works/10.1007/BF00625279);
  text not read, cited for the result through Jia and Harman, who
  write that detecting all equivalent mutants is impossible "because
  program equivalence is undecidable"). Jia and Harman report
  empirical equivalent fractions of 10% to 40% from two earlier
  studies. For a finite-state design this changes: equivalence of two
  FSMs is decidable, and a miter plus an unbounded proof decides it
  when the engine finishes. The FIFO measurement shows the practical
  limit: BMC can only ever show "differs"; equivalence needs
  induction or IC3, and InFormal's in-house IC3 gave no verdict in 30
  s on the FIFO miters where rIC3 proved equivalence [M3].
- **Trivial compiler equivalence (TCE).** Papadakis, Jia, Harman and
  Le Traon (ICSE 2015, 936-946) compile each mutant and compare the
  binary with the original's: identical code means equivalent, and
  identical code between two mutants means duplicates. On six large C
  programs TCE flagged 7.4% of all mutants as equivalent and 21% as
  duplicates, and found about 30% of the hand-identified equivalent
  mutants of an 18-subject benchmark [read in the authors' copy,
  2026-11-16](https://orbilu.uni.lu/bitstream/10993/20289/1/ICSE15.pdf).
  Hardware translation: synthesize the mutant and compare netlists (a
  structural check that Yosys's `opt` and an AIG hash do cheaply)
  before any simulation; in the source set `m06` and `m07` (`if
  (rst_n)` and `if (!(!rst_n))`) are duplicates TCE would catch, and
  `m36` (`count <= '0` for `count == '0`) likely synthesizes to the
  same netlist. Not measured here; an exercise candidate.
- **Subsumed and redundant mutants.** Ammann, Delamaro and Offutt,
  "Establishing theoretical minimal sets of mutants" (ICST 2014,
  21-30, doi 10.1109/ICST.2014.13; [researchr record, 2026-11-16](https://researchr.org/publication/AmmannDO14/bibtex);
  text not read): a mutant subsumes another when every test that
  kills the first kills the second, and a minimal set keeps one
  mutant per class. The later survey (Papadakis et al., below) states
  the consequence for scores: subsumed and duplicated mutants
  "inflate" the mutation score and make it hard to interpret, and
  reports an overestimation "as high as 10%" for one operator
  refinement. The FIFO set shows the shape: the five ROR mutants of
  one comparison (`m34`-`m38`) are not independent evidence.

### 3.3 Higher-order mutants, selective mutation, sampling, schemata

- **Higher-order mutants** (Jia and Harman, "Higher order mutation
  testing", IST 51(10), 1379-1393, 2009; [Crossref, 2026-11-16](https://api.crossref.org/works/10.1016/j.infsof.2009.04.016)):
  apply more than one change; a *subsuming* HOM is harder to kill
  than its constituents. The later survey reports that tests kill a
  larger share of HOMs than FOMs, i.e. most HOMs are weaker; the
  coupling effect is the reason the chapter can stay first-order.
- **Selective mutation.** Offutt, Lee, Rothermel, Untch and Zapf, "An
  experimental determination of sufficient mutant operators" (ACM
  TOSEM 5(2), 99-118, 1996; [Crossref, 2026-11-16](https://api.crossref.org/works/10.1145/227607.227610);
  text not read): five operators (ABS, AOR, LCR, ROR, UOI) whose
  adequate test sets achieved 99.5% mutation score over the full
  Mothra set (figure as reported by Jia and Harman). The FIFO source
  set uses AOR, LCR, ROR, a negation operator and the HDL extras;
  ABS (absolute value) has no site in the FIFO.
- **Mutant sampling.** Acree and Budd proposed random sampling (via
  Jia and Harman); Wong and Mathur ("Reducing the cost of mutation
  testing: an empirical study", JSS 31(3), 185-196, 1995;
  [researchr, 2026-11-16](https://researchr.org/publication/WongM95);
  text not read) found a random 10% of mutants "only 16% less
  effective" than the full set (the survey's words). Gopinath,
  Alipour, Ahmed, Jensen and Groce ("How hard does mutation analysis
  have to be, anyway?", ISSRE 2015, 216-227; [authors' copy,
  2026-11-16](https://www.cefns.nau.edu/~adg326/issre15.pdf)) give
  the statistical argument the chapter needs: the score of a random
  sample of n mutants is a binomial estimate whose error does not
  depend on how many mutants the program has. With Chebyshev's
  inequality and the worst case p = 0.5, n = 1000 gives about 7% at
  95%; the normal approximation gives about 3%. Measured: on Apache
  commons-math (122,484 mutants, true score 74.03%) 95% of samples of
  1000 fell in 71.3-76.7%; over 158 projects the mean absolute error
  was 0.62% at 1000 mutants and 2.56% at 100. This is the bridge to
  the statistics chapter: the right interval is Clopper-Pearson
  (`clopper1934binomial`, as `@sec-ch21` uses it), not Chebyshev,
  and the population measurement [M8] checks it.
- **Mutant schemata.** Untch, Offutt and Harrold ("Mutation analysis
  using mutant schemata", ISSTA 1993, 139-148, doi
  10.1145/154183.154265; [bibtex record, 2026-11-16](https://bibtex.github.io/ISSTA-1993-UntchOH.html);
  text not read): encode every mutant in one program with a run-time
  selector, so the program is compiled once. Yosys's `mutate -ctrl`
  is the netlist form of the same idea, and the measurement uses it:
  four builds instead of 37,124 [M6]. The source-level set compiled
  each mutant separately (180 builds, 1,704 s of build time for 1.1 s
  of simulation [M1]), which is the cost schemata exist to remove.

### 3.4 Surveys

- Jia and Harman, "An analysis and survey of the development of
  mutation testing", IEEE TSE 37(5), 649-678, 2011 (doi
  10.1109/TSE.2010.62; [Crossref, 2026-11-16](https://api.crossref.org/works/10.1109/TSE.2010.62);
  read in a course-hosted copy, first 100,000 characters). Its scope
  is 1977-2009 and it says it excluded hardware work; its only
  hardware citation is Serrestou et al. on RTL validation.
  Specification mutation (Gopal and Budd 1983; FSMs, Statecharts,
  Petri nets) is covered.
- Papadakis, Kintis, Zhang, Jia, Le Traon and Harman, "Mutation
  testing advances: an analysis and survey", Advances in Computers
  vol. 112, 275-378, 2019 (doi 10.1016/bs.adcom.2018.03.015; pages and
  year from [Crossref, 2026-11-16](https://api.crossref.org/works/10.1016/bs.adcom.2018.03.015),
  whose record lists no authors; authors from the preprint;
  [preprint read, 2026-11-16](https://mutationtesting.uni.lu/survey.pdf),
  first 100,000 characters). Relevant findings, as the survey reports
  them: TCE detects at least 30% of equivalent mutants; random
  sampling of 10% loses roughly 26% of fault detection, 50% loses 7%;
  schemata compile all mutants once; infection-condition monitoring
  speeds execution up to 5x; RIPR. Its volume number is not printed
  in the preprint (the Crossref record gives none either): `vol. 112`
  is from the Elsevier series page and must be checked before print.
- Petrović, Ivanković, Fraser and Just, "Practical mutation testing at
  scale: a view from Google" (`petrovic2021mutation`, in `refs.bib`):
  diff-based, probabilistic mutants surfaced in code review; the
  industrial reference for "mutation on the change, not the code
  base" (not reopened this session).

### 3.5 Do mutants stand for real faults?

- **Just, Jalali, Inozemtseva, Ernst, Holmes and Fraser**, "Are mutants
  a valid substitute for real faults in software testing?" (FSE 2014,
  654-665, doi 10.1145/2635868.2635929; [authors' copy read,
  2026-11-16](https://homes.cs.washington.edu/%7Emernst/pubs/mutation-effectiveness-fse2014.pdf)).
  357 real faults of five Java programs (the Defects4J set), 230,000
  mutants from Major with four operator classes, 480 developer test
  pairs and 35,141 generated suites. Measured: 73% of real faults are
  coupled to at least one mutant; mutant detection correlates with
  real-fault detection, significantly even with statement coverage
  held fixed; 27% of faults are not coupled, of which most need
  operators that do not exist (algorithm changes, code deletion).
  Conditional-operator, relational-operator and statement-deletion
  mutants were the ones most often coupled to real faults.
- **Papadakis, Shin, Yoo and Bae**, "Are mutation scores correlated
  with real fault detection?" (ICSE 2018, doi
  10.1145/3180155.3180183; [authors' copy read, 2026-11-16](https://core.ac.uk/download/154760839.pdf)).
  The correction: once test-suite *size* is controlled, the
  correlation drops from 0.35-0.75 to 0.05-0.20, weak; most of the
  association is the size confound. But suites in the top 10% by
  mutation score detect significantly more faults (for 138 of 231
  Defects4J and 59 of 68 CoREBench faults).
- **Chekam, Papadakis, Le Traon and Harman**, "An empirical study on
  mutation, statement and branch coverage fault revelation that avoids
  the unreliable clean program assumption" (ICSE 2017, 597-608, doi
  10.1109/ICSE.2017.61; [authors' copy read, 2026-11-16](https://discovery.ucl.ac.uk/10058915/7/Chekam_ICSE17.pdf)).
  A threshold effect: strong mutation helps fault revelation only at
  high scores (top 20% of attainable coverage about 5% more faults,
  top 5% about 18%), and below the threshold coverage of any kind
  makes little difference; strong mutation uniquely coupled 21 faults,
  statement and branch coverage none.
- `inozemtseva2014coverage` (in `refs.bib`): coverage is not strongly
  correlated with suite effectiveness once size is controlled; Chapter
  8 already cites it as the software analogue.

Hardware translation, and the limit of it: there is no hardware
counterpart of Defects4J with real RTL bugs and their fixes at this
scale, so "mutation score predicts real bug detection" is a software
result the chapter must not transfer as a number. What transfers is
the shape: (1) the size confound means a kill rate must be compared
between testbenches of comparable cost (cycles, seeds), which is why
the measurements table prints cycles and seeds beside each kill rate;
(2) the threshold effect means a kill rate is informative at the top,
not in the middle; (3) the operators that coupled best (conditions,
relational operators, statement deletion) are the ones the FIFO set
uses.

### 3.6 Mutation of hardware descriptions

**Peer-reviewed.**
- Al Hayek and Robach, "From specification validation to hardware
  testing: a unified method" (ITC 1996, 885-893; [researchr record,
  2026-11-16](https://researchr.org/publication/HayekR96%3A0); text
  not read): mutation of VHDL descriptions as a validation method,
  one of the earliest HDL uses.
- Serrestou, Beroulle and Robach, "Functional verification of RTL
  designs driven by mutation testing metrics" (DSD 2007, 222-227,
  doi 10.1109/DSD.2007.4341472; [Crossref, 2026-11-16](https://api.crossref.org/works/10.1109%2FDSD.2007.4341472);
  abstract not in the record, text not read). The record's author
  field runs two names together ("Vincent Beroulle Chantal Robach");
  the paper has three authors, Serrestou, Beroulle, Robach, to be
  checked on the document before print.
- Hampton and Petithomme, "Leveraging a commercial mutation analysis
  tool for research" (TAIC PART-MUTATION 2007, `hampton2007certitude`,
  in `refs.bib`): Certitude described in a peer-reviewed workshop by
  its vendor's staff; peer-reviewed venue, vendor authors.
- Lisherness and Cheng, "SCEMIT: a SystemC error and mutation
  injection tool" (DAC 2010, 228-233, doi 10.1145/1837274.1837333;
  [bibtex record, 2026-11-16](https://bibtex.github.io/DAC-2010-LishernessC.html);
  text not read): mutation at the SystemC level.
- Lin, Wang, Chang, Chen, Chou, Huang, Yang and Shen, "A probabilistic
  analysis method for functional qualification under mutation
  analysis" (DATE 2012; [proceedings PDF read, 2026-11-16](https://past.date-conference.com/date16/files/proceedings/2012/pdffiles/03.2_3.pdf)):
  a static estimate of error propagation per mutant to drop
  simulations that cannot kill it; mutants from Certitude in three
  classes (operator changes, dead assignments, condition stuck at true
  or false); three OpenCores designs; 33-61% of simulation rounds
  removed, about 14% CPU time saved over weak-mutation preprocessing.
  The three classes are a useful published list of the commercial
  tool's fault model, read from a peer-reviewed paper rather than
  from the vendor.
- `huang2015mutation` (in `refs.bib`): testbench qualification by
  mutation analysis, the independent statement that coverage neglects
  propagation and detection (Chapter 8 cites it).

**Vendor (label as such).** Certitude (Certess, then SpringSoft, then
Synopsys): `synopsys-certitude` (the product page, no figures),
`hampton2009fq` (EDN, by Certess's CTO), and SpringSoft's
"The principles of functional qualification" ([TechDesignForums,
undated, read 2026-11-16](https://www.techdesignforums.com/practice/?p=2269)):
activation, propagation, detection; a "Certitude fault model" not
specified on the page; "production-proven" claimed without figures.
Nothing quantitative from any vendor source.

**Open source: MCY.** "Mutation Cover with Yosys" ([GitHub
YosysHQ/mcy, cloned 2026-11-16 at commit 5a2cad0](https://github.com/YosysHQ/mcy);
[methodology, 2026-11-16](https://mcy.readthedocs.io/en/latest/methodology.html);
[mutation export options, 2026-11-16](https://mcy.readthedocs.io/en/latest/mutate.html);
[equivalence setup, 2026-11-16](https://mcy.readthedocs.io/en/latest/eqsetup.html);
[AppNote 400, 2026-11-16](https://yosyshq.readthedocs.io/projects/ap400/en/latest/)).
What the documents say: mutations change "the value of a single bit
in the design"; `mutate -list N` samples candidates from eight lists
(by wire, wire bit, cell, source location, each per module) with
configurable weights and a source-coverage heuristic; `-ctrl` adds an
input that enables a mutation when it equals the mutation's value,
"0 is reserved for the unmodified behaviour"; the equivalence check
is a miter of the design with `mutsel` 0 and 1 run by SymbiYosys in
BMC mode (the example uses depth 10, the AppNote depth 1), so MCY's
"NOCHANGE" is a bounded statement; tags COVERED, UNCOVERED,
NOCHANGE, and EQGAP for a test failure the equivalence check calls
equivalent, which "should never occur in a correct setup". The
measured mutation modes on the FIFO are `inv`, `const0`, `const1`,
`cnot0`, `cnot1` [M6]; the documents read do not list them.

Hardware-specific operator families seen across these sources and
used in the source set: condition stuck-at (CNG here), dead
assignment (SDL), operator replacement (AOR, ROR, LCR), constant
replacement, reset removal, case-item exchange, sensitivity-list
change (ARS). The two that have no software counterpart and matter
most on the FIFO are reset removal (its survival depends on the
simulator's initial values [M7]) and the sensitivity change (its
equivalence depends on the formal tool's reset model [M3]).

### 3.7 Mutation of formal property sets: completeness and vacuity

The formal counterpart of "does the testbench catch the bug" is "do
the properties constrain the behavior", and it was developed under
the name *coverage in model checking*:

- Hoskote, Kam, Ho and Zhao, "Coverage estimation for symbolic model
  checking" (DAC 1999, 300-305, doi 10.1145/309847.309936;
  [bibtex record, 2026-11-16](https://bibtex.github.io/DAC-1999-HoskoteKHZ.html);
  text not read): the first coverage metric for model checking, by
  which states' observed-signal values a property set depends on.
- Chockler, Kupferman, Kurshan and Vardi (`chockler2001practical`, in
  `refs.bib`, read 2026-11-16 by the Chapter 19 note): coverage as
  the set of small design mutations under which the specification
  fails; the direct ancestor of running a property set against
  mutants.
- Große, Kühne and Drechsler, "Estimating functional coverage in
  bounded model checking" ([authors' copy read, 2026-11-16](https://agra.informatik.uni-bremen.de/doc/konf/07date_coverage.pdf);
  venue DATE 2007 from the file name, to be confirmed): for each
  output, insert a multiplexer that may invert it and ask whether the
  proven properties still hold; a counterexample is an unspecified
  scenario. That is a mutation of the output with a formal kill, and
  on a RISC CPU it found three gaps.
- Claessen, "A coverage analysis for safety property lists" (FMCAD
  2007, 139-145, doi 10.1109/FAMCAD.2007.32; [Chalmers record read,
  2026-11-16](https://research.chalmers.se/en/publication/67786)):
  design-independent; a gap is a scenario in which the property list
  does not constrain an output at some time.
- Vacuity: Beer, Ben-David, Eisner and Rodeh (`beer2001vacuity`, in
  `refs.bib`) and Kupferman and Vardi, "Vacuity detection in temporal
  model checking" (STTT 4(2), 224-233, 2003; [Crossref,
  2026-11-16](https://api.crossref.org/works/10.1007%2FS100090100062);
  text not read): a property is vacuous when a subformula can be
  replaced without changing the verdict, which is mutation of the
  *property*, the dual of mutation of the design.

On the FIFO this reads: the property set kills a mutant iff some
property fails on it; a mutant equivalent at the ports that a
property kills (`m44` by `Sync_A`) shows a property about the
implementation; a non-equivalent mutant no property kills is a gap in
the property set, located by the miter's trace. The FIFO's property
set leaves the data path to `a_integrity` and `EmptyPtrs_A` (Chapter
19's finding); the population run measures how much of the netlist
that leaves [M9].

### 3.8 Equivalent-mutant detection by formal equivalence

For hardware the equivalent-mutant problem is the textbook use of
sequential equivalence checking: a miter (both designs, shared
inputs, an assertion that the outputs agree), proved by an unbounded
engine. MCY's filter is that miter with BMC; the book's InFormal has
no equivalence command (FINDINGS C.8: "A hand-built miter ... is the
only way"), so the measurement builds one (`formal/miter.sv`). Three
lessons from the runs [M3]:

1. **What is compared is the definition.** The FIFO's memory is not
   reset, so `rd_data` of an empty FIFO is arbitrary and differs
   between two copies from the start; the miter compares `rd_data`
   only when the FIFO is not empty, as the contract says. Comparing
   it always would make every mutant "differ" at depth 0.
2. **BMC only refutes.** Every "equivalent" verdict came from IC3
   (rIC3); InFormal's in-house IC3 gave none within 30 s on the
   miters measured, and BMC never can. MCY's BMC filter would call
   `m43` NOCHANGE at any depth, correctly, but for a reason it cannot
   state; and a mutant whose difference lies deeper than the BMC
   depth would be called NOCHANGE wrongly.
3. **Equivalent under the tool's model.** `m05` (asynchronous reset
   made synchronous) is proved equivalent because InFormal models an
   asynchronous reset as synchronous (FINDINGS D.3); the designs are
   not equivalent in silicon. The chapter must report it as its own
   class.

### 3.9 Large language models and mutants

Measured versus claimed is kept apart for each source; every number
below is the paper's own, read from its arXiv abstract page unless
stated.

- Tian, Shu, Wang, Cao, Kamei and Chen, "Large language models for
  equivalent mutant detection: how far are we?" (arXiv 2408.01760,
  2024; the ISSTA 2024 programme lists it, [ISSTA page,
  2026-11-16](https://2024.issta.org/details/issta-2024-papers/138/Large-Language-Models-for-Equivalent-Mutant-Detection-How-Far-Are-We-);
  [arXiv abstract read, 2026-11-16](https://arxiv.org/abs/2408.01760v1)).
  Measured: 3,302 Java method-level mutant pairs; LLM-based techniques
  improve F1 by 35.69% on average over prior techniques; fine-tuned
  code embeddings did best. Claimed, not quantified in the abstract:
  "excellent balance" of cost and effectiveness. Software only.
- Foster, Gulati, Harman, Harper, Mao, Ritchey, Robert and Sengupta,
  "Mutation-guided LLM-based test generation at Meta" (arXiv
  2501.12862, 2025, FSE 2025 industry track; [arXiv abstract read,
  2026-11-16](https://arxiv.org/abs/2501.12862)). An LLM writes
  mutants for a stated concern (privacy) and then tests that kill
  them; an LLM agent classifies equivalent mutants. Measured: 10,795
  Kotlin classes, 9,095 mutants, 571 tests; engineers accepted 73% of
  tests and judged 36% privacy-relevant; the equivalence detector had
  precision 0.79 and recall 0.47, rising to 0.95 and 0.96 with
  pre-processing the abstract does not describe. Claimed: that the
  tests harden code against regressions (no regression measurement
  in the abstract).
- Jasper, Luu, Pan, Tyagi, Quinn, Hu and Houngninou, "BugGen: a
  self-correcting multi-agent LLM pipeline for realistic RTL bug
  synthesis" (arXiv 2506.10501v2, 2025; [abstract read,
  2026-11-16](https://arxiv.org/abs/2506.10501)). LLM agents insert
  functional bugs in OpenTitan IP. Measured as reported: 500 bugs in
  five IP blocks, "94% functional accuracy" (undefined in the
  abstract), 17.7 validated bugs per hour, "104 previously undetected
  bugs" found in OpenTitan regressions (the abstract's phrase; whether
  these are design bugs or mutants the regressions miss is not clear
  from the abstract and must be read in the paper before any use).
  Claimed: realism, supported only indirectly by triage accuracy; a
  syntactic accuracy "over twice" Certitude's, with no absolute
  figure.
- Bhadra, "GateTruth: auditing the rigor of RTL design benchmarks via
  mutation testing" (arXiv 2608.12635v1, 2026-08-12, single author,
  not peer-reviewed; [abstract read, 2026-11-16](https://arxiv.org/abs/2608.12635)).
  Mutation kill rate used to audit the *testbenches* of LLM RTL
  benchmarks. Measured: 46 of the author's 60 testbenches kill at
  least 95% of mutants; 72% of 46 auditable RTLLM v2.0 designs fall
  below 95%, three score 0%. The mutation operators are not named in
  the abstract. This is the closest published analogue of the
  chapter's Chapter 8 result (a testbench that passes everything),
  applied to benchmarks; cite as a preprint.

What the chapter can say: LLMs are being used to *generate* mutants
(BugGen, ACH) and to *classify* equivalence (Tian et al., ACH), with
measured results on software and one hardware preprint, and no
comparison against a formal miter, which for finite-state hardware is
the exact answer whenever the proof finishes. The natural experiment
for the AI chapters is an LLM classifier's verdicts scored against
the miter's on the FIFO set (open question O5); not run here.

### 3.10 Mutation and coverage closure

The measurements give the chapter its central table [M2, M5]: Chapter
8's coverage testbench reaches 100% line, branch and expression
coverage and 99% toggle coverage of the FIFO, and 76-90% functional
coverage, and kills 0 of 44 mutants; Chapter 1's directed test, with
24% toggle coverage, kills 34. Code coverage is necessary for a kill
(a mutant on an unreached line cannot be killed; RIP's R) and says
nothing about P and D. Where the literature stands: Chekam et al.'s
threshold effect, and Papadakis et al.'s size confound, are the
cautions on reading a kill rate as a closure metric. Practical uses
the chapter can teach: (1) a survivor names a missing check (the data
mutants that pass Chapter 9's checker), a missing stimulus (`m35`,
`empty` stuck low, survives Chapter 1's random test because seed 1
never drains the FIFO again after the first push: "16 of 17 occupancy
levels", level 0 the one missing), or an equivalence; (2) kill rate
is reported beside coverage, never instead of it; (3) mutation runs
on the diff (Google's practice, `petrovic2021mutation`) to make the
cost tolerable.

### 3.11 The statistics of sampling mutants

From the statistics chapter (`@sec-ch21`, its bounds section): a
random sample of n mutants of which k are killed gives a binomial
estimate of the population kill rate, with the Clopper-Pearson
interval. Three hardware-specific cautions the measurements make
concrete:
1. *What is sampled.* Yosys's `mutate -list N` with N below the
   population is not a uniform sample: it is weighted toward source
   locations and cells with few mutations so far (the documented
   heuristic). A uniform sample of the full list (as [M8] draws) is
   what the binomial interval assumes; the interval for `mutate -list
   N` output is not justified by the binomial model.
2. *What is estimated.* The kill rate over all mutants is not the
   mutation score, which divides by non-equivalent mutants; with an
   equivalent fraction e estimated from a formal sample, the score is
   kill / (1 - e), and its interval needs both samples [M9].
3. *Correlated mutants.* The binomial model treats mutants as
   independent draws; mutants on adjacent bits of one cell are killed
   together or not at all, which does not bias a uniform sample but
   makes the effective information per mutant smaller than it looks
   when results are reported per source line.

## 4. Proposed worked-example spine

One design, the repaired FIFO of `@sec-ch09-example`, carried through
the whole chapter, with the four testbenches the book already ships
and the property set of `@sec-ch19-mutation`. No new testbench is
needed until the last step, which is the point: the chapter measures
the book's own verification before improving it.

1. **The table that opens the chapter.** Four testbenches, their
   coverage and their kill rates on the 44 source mutants [M2, M5]:
   Chapter 8's coverage testbench at 100% line and branch coverage
   kills 0; Chapter 1's directed test at 24% toggle coverage kills
   34; then the same four on the 9,281 netlist mutations [M6]. The reader predicts the order before seeing it. (Splice from a
   `run.out`, never typed.)
2. **Fault models.** Read five mutants as RTL diffs (one per operator
   family: a condition negated, a relational operator, a deleted
   statement, a reset removed, the case labels exchanged) and say for
   each what bug it stands for. Then the netlist fault model: Yosys
   `mutate -list` on the same file, 9,281 single-bit mutations in five
   modes [M6], and why nobody reads them one at a time.
3. **Kill, survive, and the three conditions.** RIP (reach, infect,
   propagate) beside the vendor's activation/propagation/detection
   (cited, as in `@sec-ch08-where`), shown on three survivors: `m35`
   (`empty` stuck low) survives Chapter 1's random test because seed
   1 never drains the FIFO (not reached); the data mutants survive
   Chapter 9's checker because nothing compares data (propagated, not
   detected); Chapter 8's testbench detects nothing.
4. **Equivalent mutants and the miter.** The seven mutants no
   testbench kills, classified by an InFormal miter [M3]: equivalent
   outright (`m32`, `m36`), equivalent only under reachability
   (`m43`, which BMC can never decide and IC3 proves), equivalent
   only under the tool's reset model (`m05`), and three that are not
   equivalent at all but survive because Verilator starts registers at
   zero (`m09`, `m11`, `m13`; killed with random initial values
   [M7]). Then `m44`: equivalent at the ports, killed by `Sync_A`;
   what a white-box assertion kills is the implementation, not a bug.
5. **The property set as a testbench.** The same 44 mutants against
   the formal property set [M4]: it kills every mutant the miter
   calls non-equivalent, including the three reset mutants simulation
   missed, and two mutants are refused by InFormal's front end
   (`m06`, `m07`, a reset branch whose polarity does not match the
   sensitivity list), which is a kill at compile time, like a lint
   error (seven source mutants also draw warnings the book's `-Wall`
   makes fatal [M1]).
6. **Sampling and the interval.** The netlist population is too large
   to classify by hand and expensive to simulate one build at a time;
   schemata (`mutate -ctrl`) make it one build. Kill rates of the
   whole population are known [M6], so a sample of 100 with its
   Clopper-Pearson interval (`@sec-ch21`) can be checked against the
   truth, and its coverage over 2,000 samples measured [M8]. Then the
   equivalent fraction from a formal sample and the score among
   non-equivalent mutants [M9].
7. **Closing the gap.** One survivor turned into one new check: the
   data comparison Chapter 9's checker lacks (the tracked-word check
   of `@sec-ch19-track` is the formal one; a scoreboard line is the
   simulation one), re-run to show the kill rate move. (Not measured
   here; the outline decides whether the chapter ships it as an
   example or leaves it as an exercise.)

Exercises that fall out of the measurements: compute TCE by
synthesizing each source mutant and hashing the netlist (which of
`m06`/`m07`, `m36` collapse?); find the first seed of Chapter 1's random test that drains the FIFO
and so kills `m35`; write the miter
that compares `rd_data` always and explain why every mutant then
"differs"; compute the interval of the ratio kill/(1-e) from [M9].

## 5. Bibliography (BibTeX-ready)

Keys already in `refs.bib` to reuse (checked by key 2026-11-16):
`demillo1978mutation`, `petrovic2021mutation`,
`inozemtseva2014coverage`, `hampton2007certitude`, `hampton2009fq`,
`synopsys-certitude`, `huang2015mutation`, `chockler2001practical`,
`beer2001vacuity`, `clopper1934binomial`, `informal-tool`,
`su2025ric3`, `verilator-docs`. None of the entries below exists in
`refs.bib` (checked by key and surname). House rule: an entry with a
DOI carries no URL or access date; `note` says what was actually read.
Crossref (through the fetch tool) supplied the metadata marked so;
direct API access from the shell was refused by the proxy.

```bibtex
@article{hamlet1977compiler,
  author  = {Hamlet, Richard G.},
  title   = {Testing Programs with the Aid of a Compiler},
  journal = {IEEE Transactions on Software Engineering},
  volume  = {SE-3},
  number  = {4},
  pages   = {279--290},
  year    = {1977},
  doi     = {10.1109/TSE.1977.231145},
  note    = {Metadata from Crossref; text not read}
}

@article{offutt1992coupling,
  author  = {Offutt, A. Jefferson},
  title   = {Investigations of the Software Testing Coupling Effect},
  journal = {ACM Transactions on Software Engineering and Methodology},
  volume  = {1},
  number  = {1},
  pages   = {5--20},
  year    = {1992},
  doi     = {10.1145/125489.125473},
  note    = {Metadata from Crossref; text not read, findings as
             reported by jia2011survey}
}

@article{offutt1996sufficient,
  author  = {Offutt, A. Jefferson and Lee, Ammei and Rothermel, Gregg
             and Untch, Roland H. and Zapf, Christian},
  title   = {An Experimental Determination of Sufficient Mutant
             Operators},
  journal = {ACM Transactions on Software Engineering and Methodology},
  volume  = {5},
  number  = {2},
  pages   = {99--118},
  year    = {1996},
  doi     = {10.1145/227607.227610},
  note    = {Metadata from Crossref; text not read, the 99.5\% figure
             as reported by jia2011survey}
}

@article{budd1982correctness,
  author  = {Budd, Timothy A. and Angluin, Dana},
  title   = {Two Notions of Correctness and Their Relation to Testing},
  journal = {Acta Informatica},
  volume  = {18},
  number  = {1},
  pages   = {31--45},
  year    = {1982},
  doi     = {10.1007/BF00625279},
  note    = {Metadata from Crossref; text not read}
}

@inproceedings{untch1993schemata,
  author    = {Untch, Roland H. and Offutt, A. Jefferson and Harrold,
               Mary Jean},
  title     = {Mutation Analysis Using Mutant Schemata},
  booktitle = {Proceedings of the 1993 ACM SIGSOFT International
               Symposium on Software Testing and Analysis (ISSTA)},
  pages     = {139--148},
  year      = {1993},
  doi       = {10.1145/154183.154265},
  note      = {Metadata from a bibliography record; text not read}
}

@article{wong1995reducing,
  author  = {Wong, W. Eric and Mathur, Aditya P.},
  title   = {Reducing the Cost of Mutation Testing: An Empirical Study},
  journal = {Journal of Systems and Software},
  volume  = {31},
  number  = {3},
  pages   = {185--196},
  year    = {1995},
  url     = {https://researchr.org/publication/WongM95},
  note    = {Metadata from the researchr record (DOI not shown there;
             find it before print); text not read. Accessed 2026-11-16}
}

@article{jia2009hom,
  author  = {Jia, Yue and Harman, Mark},
  title   = {Higher Order Mutation Testing},
  journal = {Information and Software Technology},
  volume  = {51},
  number  = {10},
  pages   = {1379--1393},
  year    = {2009},
  doi     = {10.1016/j.infsof.2009.04.016},
  note    = {Metadata from Crossref; text not read}
}

@article{jia2011survey,
  author  = {Jia, Yue and Harman, Mark},
  title   = {An Analysis and Survey of the Development of Mutation
             Testing},
  journal = {IEEE Transactions on Software Engineering},
  volume  = {37},
  number  = {5},
  pages   = {649--678},
  year    = {2011},
  doi     = {10.1109/TSE.2010.62},
  note    = {Read in a course-hosted copy
             (web.eecs.umich.edu/~weimerw/2020-481F/readings/), first
             100,000 characters, 2026-11-16}
}

@incollection{papadakis2019advances,
  author    = {Papadakis, Mike and Kintis, Marinos and Zhang, Jie and
               Jia, Yue and {Le Traon}, Yves and Harman, Mark},
  title     = {Mutation Testing Advances: An Analysis and Survey},
  booktitle = {Advances in Computers},
  volume    = {112},
  pages     = {275--378},
  publisher = {Elsevier},
  year      = {2019},
  doi       = {10.1016/bs.adcom.2018.03.015},
  note      = {Pages and year from Crossref, which lists no authors;
               authors from the preprint (mutationtesting.uni.lu/survey.pdf,
               first 100,000 characters read 2026-11-16); volume 112
               from the series, to be checked before print}
}

@inproceedings{ammann2014minimal,
  author    = {Ammann, Paul and Delamaro, M{\'a}rcio Eduardo and
               Offutt, Jeff},
  title     = {Establishing Theoretical Minimal Sets of Mutants},
  booktitle = {IEEE Seventh International Conference on Software
               Testing, Verification and Validation (ICST 2014)},
  pages     = {21--30},
  year      = {2014},
  doi       = {10.1109/ICST.2014.13},
  note      = {Metadata from the researchr record; text not read}
}

@inproceedings{papadakis2015tce,
  author    = {Papadakis, Mike and Jia, Yue and Harman, Mark and
               {Le Traon}, Yves},
  title     = {Trivial Compiler Equivalence: A Large Scale Empirical
               Study of a Simple, Fast and Effective Equivalent Mutant
               Detection Technique},
  booktitle = {37th IEEE/ACM International Conference on Software
               Engineering (ICSE 2015)},
  pages     = {936--946},
  year      = {2015},
  doi       = {10.1109/ICSE.2015.103},
  note      = {Read in the authors' copy (orbilu.uni.lu), 2026-11-16}
}

@inproceedings{gopinath2015hard,
  author    = {Gopinath, Rahul and Alipour, Amin and Ahmed, Iftekhar
               and Jensen, Carlos and Groce, Alex},
  title     = {How Hard Does Mutation Analysis Have to Be, Anyway?},
  booktitle = {IEEE 26th International Symposium on Software
               Reliability Engineering (ISSRE 2015)},
  pages     = {216--227},
  year      = {2015},
  doi       = {10.1109/ISSRE.2015.7381815},
  note      = {Read in the authors' copy (cefns.nau.edu), 2026-11-16}
}

@inproceedings{just2014mutants,
  author    = {Just, Ren{\'e} and Jalali, Darioush and Inozemtseva,
               Laura and Ernst, Michael D. and Holmes, Reid and Fraser,
               Gordon},
  title     = {Are Mutants a Valid Substitute for Real Faults in
               Software Testing?},
  booktitle = {Proceedings of the 22nd ACM SIGSOFT International
               Symposium on Foundations of Software Engineering
               (FSE 2014)},
  pages     = {654--665},
  year      = {2014},
  doi       = {10.1145/2635868.2635929},
  note      = {Read in the authors' copy (homes.cs.washington.edu),
               2026-11-16}
}

@inproceedings{papadakis2018correlated,
  author    = {Papadakis, Mike and Shin, Donghwan and Yoo, Shin and
               Bae, Doo-Hwan},
  title     = {Are Mutation Scores Correlated with Real Fault
               Detection? A Large Scale Empirical Study on the
               Relationship Between Mutants and Real Faults},
  booktitle = {Proceedings of the 40th International Conference on
               Software Engineering (ICSE 2018)},
  year      = {2018},
  doi       = {10.1145/3180155.3180183},
  note      = {Read in the authors' copy (core.ac.uk); page range to be
               taken from the ACM record before print. 2026-11-16}
}

@inproceedings{chekam2017threshold,
  author    = {Chekam, Thierry Titcheu and Papadakis, Mike and
               {Le Traon}, Yves and Harman, Mark},
  title     = {An Empirical Study on Mutation, Statement and Branch
               Coverage Fault Revelation That Avoids the Unreliable
               Clean Program Assumption},
  booktitle = {39th IEEE/ACM International Conference on Software
               Engineering (ICSE 2017)},
  pages     = {597--608},
  year      = {2017},
  doi       = {10.1109/ICSE.2017.61},
  note      = {Read in the authors' copy (discovery.ucl.ac.uk),
               2026-11-16}
}

@inproceedings{alhayek1996unified,
  author    = {{Al Hayek}, Ghassan and Robach, Chantal},
  title     = {From Specification Validation to Hardware Testing: A
               Unified Method},
  booktitle = {Proceedings of the IEEE International Test Conference
               (ITC 1996)},
  pages     = {885--893},
  year      = {1996},
  url       = {https://researchr.org/publication/HayekR96%3A0},
  note      = {Metadata from the researchr record; DOI to be found;
               text not read. Accessed 2026-11-16}
}

@inproceedings{serrestou2007rtl,
  author    = {Serrestou, Youssef and Beroulle, Vincent and Robach,
               Chantal},
  title     = {Functional Verification of {RTL} Designs Driven by
               Mutation Testing Metrics},
  booktitle = {10th Euromicro Conference on Digital System Design
               Architectures, Methods and Tools (DSD 2007)},
  pages     = {222--227},
  year      = {2007},
  doi       = {10.1109/DSD.2007.4341472},
  note      = {Metadata from Crossref, whose author field runs the
               second and third names together; check against the
               paper. Text not read}
}

@inproceedings{lisherness2010scemit,
  author    = {Lisherness, Peter and Cheng, Kwang-Ting},
  title     = {{SCEMIT}: A {SystemC} Error and Mutation Injection Tool},
  booktitle = {Proceedings of the 47th Design Automation Conference
               (DAC 2010)},
  pages     = {228--233},
  year      = {2010},
  doi       = {10.1145/1837274.1837333},
  note      = {Metadata from a bibliography record; text not read}
}

@inproceedings{lin2012epa,
  author    = {Lin, Hsiu-Yi and Wang, Chun-Yao and Chang, Shih-Chieh
               and Chen, Yung-Chih and Chou, Hsuan-Ming and Huang,
               Ching-Yi and Yang, Yen-Chi and Shen, Chun-Chien},
  title     = {A Probabilistic Analysis Method for Functional
               Qualification under Mutation Analysis},
  booktitle = {Design, Automation and Test in Europe (DATE 2012)},
  year      = {2012},
  url       = {https://past.date-conference.com/date16/files/proceedings/2012/pdffiles/03.2_3.pdf},
  note      = {Read in the proceedings PDF; DOI and pages to be taken
               from the IEEE record before print. Accessed 2026-11-16}
}

@inproceedings{hoskote1999coverage,
  author    = {Hoskote, Yatin Vasant and Kam, Timothy and Ho, Pei-Hsin
               and Zhao, Xudong},
  title     = {Coverage Estimation for Symbolic Model Checking},
  booktitle = {Proceedings of the 36th Design Automation Conference
               (DAC 1999)},
  pages     = {300--305},
  year      = {1999},
  doi       = {10.1145/309847.309936},
  note      = {Metadata from a bibliography record; text not read}
}

@inproceedings{grosse2007bmccoverage,
  author    = {Gro{\ss}e, Daniel and K{\"u}hne, Ulrich and Drechsler,
               Rolf},
  title     = {Estimating Functional Coverage in Bounded Model
               Checking},
  booktitle = {Design, Automation and Test in Europe (DATE 2007)},
  year      = {2007},
  url       = {https://agra.informatik.uni-bremen.de/doc/konf/07date_coverage.pdf},
  note      = {Read in the authors' copy; venue and year from the file
               name, pages and DOI to be confirmed. Accessed 2026-11-16}
}

@inproceedings{claessen2007coverage,
  author    = {Claessen, Koen},
  title     = {A Coverage Analysis for Safety Property Lists},
  booktitle = {Formal Methods in Computer Aided Design (FMCAD 2007)},
  pages     = {139--145},
  year      = {2007},
  doi       = {10.1109/FAMCAD.2007.32},
  note      = {Abstract read in the Chalmers research record; the
               record gives the author as Koen Lindstr{\"o}m Claessen.
               2026-11-16}
}

@article{kupferman2003vacuity,
  author  = {Kupferman, Orna and Vardi, Moshe Y.},
  title   = {Vacuity Detection in Temporal Model Checking},
  journal = {International Journal on Software Tools for Technology
             Transfer},
  volume  = {4},
  number  = {2},
  pages   = {224--233},
  year    = {2003},
  doi     = {10.1007/s100090100062},
  note    = {Metadata from Crossref; text not read}
}

@misc{mcy-docs,
  author       = {{YosysHQ}},
  title        = {Mutation Cover with {Yosys} ({MCY}) documentation:
                  methodology, mutation export options, equivalence
                  setup},
  howpublished = {Read the Docs},
  year         = {2026},
  url          = {https://mcy.readthedocs.io/en/latest/},
  note         = {Pages methodology.html, mutate.html, eqsetup.html read
                  2026-11-16. Tool documentation}
}

@misc{mcy-repo,
  author       = {{YosysHQ}},
  title        = {{MCY}: Mutation Cover with {Yosys}},
  howpublished = {GitHub repository YosysHQ/mcy, commit 5a2cad0},
  year         = {2026},
  url          = {https://github.com/YosysHQ/mcy},
  note         = {Cloned 2026-11-16; latest commit dated 2026-08-04.
                  Not installed in the book's toolchain}
}

@misc{yosys-ap400,
  author       = {{YosysHQ}},
  title        = {{AppNote} 400: Introduction to Mutation Coverage with
                  {Yosys} ({MCY})},
  howpublished = {YosysHQ documentation},
  year         = {2022},
  url          = {https://yosyshq.readthedocs.io/projects/ap400/en/latest/},
  note         = {Vendor application note (YosysHQ sells the Tabby CAD
                  suite that includes MCY). Accessed 2026-11-16}
}

@misc{springsoft-fq,
  author       = {{SpringSoft}},
  title        = {The Principles of Functional Qualification},
  howpublished = {Tech Design Forums},
  url          = {https://www.techdesignforums.com/practice/?p=2269},
  note         = {Vendor article, undated, no author named; describes
                  Certitude. Accessed 2026-11-16}
}

@misc{tian2024llmequiv,
  author       = {Tian, Zhao and Shu, Honglin and Wang, Dong and Cao,
                  Xuejie and Kamei, Yasutaka and Chen, Junjie},
  title        = {Large Language Models for Equivalent Mutant Detection:
                  How Far Are We?},
  howpublished = {arXiv:2408.01760; ISSTA 2024},
  year         = {2024},
  url          = {https://arxiv.org/abs/2408.01760},
  note         = {Abstract read 2026-11-16; take the ISSTA DOI from the
                  ACM record before print}
}

@misc{foster2025ach,
  author       = {Foster, Christopher and Gulati, Abhishek and Harman,
                  Mark and Harper, Inna and Mao, Ke and Ritchey,
                  Jillian and Robert, Herv{\'e} and Sengupta, Shubho},
  title        = {Mutation-Guided {LLM}-based Test Generation at {Meta}},
  howpublished = {arXiv:2501.12862 (FSE 2025 Industry Track)},
  year         = {2025},
  url          = {https://arxiv.org/abs/2501.12862},
  note         = {Abstract read 2026-11-16; industrial authors}
}

@misc{jasper2025buggen,
  author       = {Jasper, Surya and Luu, Minh and Pan, Evan and Tyagi,
                  Aakash and Quinn, Michael and Hu, Jiang and
                  Houngninou, David Kebo},
  title        = {{BugGen}: A Self-Correcting Multi-Agent {LLM} Pipeline
                  for Realistic {RTL} Bug Synthesis},
  howpublished = {arXiv:2506.10501v2},
  year         = {2025},
  url          = {https://arxiv.org/abs/2506.10501},
  note         = {Preprint; abstract read 2026-11-16}
}

@misc{bhadra2026gatetruth,
  author       = {Bhadra, Meet},
  title        = {{GateTruth}: Auditing the Rigor of {RTL} Design
                  Benchmarks via Mutation Testing},
  howpublished = {arXiv:2608.12635v1},
  year         = {2026},
  url          = {https://arxiv.org/abs/2608.12635},
  note         = {Preprint, single author; abstract read 2026-11-16}
}
```

## 6. Confidence notes

- **Read versus metadata.** Full text (or the first 100,000
  characters) was read for: Jia and Harman 2011, Papadakis et al. 2019
  (preprint), Just et al. 2014, Papadakis et al. 2018, Chekam et al.
  2017, Papadakis et al. 2015 (TCE), Gopinath et al. 2015, Lin et al.
  2012, Große et al. 2007, the MCY documents and AppNote 400, and the
  SpringSoft article. Abstracts only: Tian et al., Foster et al.,
  BugGen, GateTruth, Claessen 2007. Metadata only (Crossref or a
  bibliography record), with the claim taken from a survey that was
  read: Hamlet 1977, Offutt 1992, Offutt et al. 1996, Budd and Angluin
  1982, Untch et al. 1993, Wong and Mathur 1995, Jia and Harman 2009,
  Ammann et al. 2014, Al Hayek and Robach 1996, Serrestou et al. 2007,
  Lisherness and Cheng 2010, Hoskote et al. 1999, Kupferman and Vardi
  2003. A chapter sentence resting on a metadata-only source must be
  checked against the paper before print (the house rule of
  2026-09-11: cite the paper, read from the paper).
- **Survey numbers quoted second-hand.** "99.5%" (Offutt et al.'s five
  operators), "16% less effective" (Wong and Mathur), "10% to 40%"
  equivalent mutants: each is Jia and Harman's report of another
  paper. Print them as "as reported by" or read the originals.
- **Papadakis et al. 2019 volume.** The preprint and the Crossref
  record give no volume; 112 is from the series listing and must be
  checked.
- **Serrestou et al. author list.** Crossref runs two names together;
  check the paper.
- **BugGen's "104 previously undetected bugs".** The abstract does
  not say whether these are design bugs or injected bugs the
  regressions miss. Do not print the number without reading the
  paper.
- **GateTruth** is a single-author preprint of 2026-08-12, not peer
  reviewed; its mutation operators are not named in the abstract.
- **MCY's equivalence check is BMC.** Stated from its documentation
  (`mode bmc`, depth 10 in the example, 1 in the AppNote). That MCY's
  NOCHANGE is bounded is therefore a documented fact; that it would
  misclassify any particular FIFO mutant was not measured, because MCY
  was not run.
- **The measurements are one design.** Every kill rate is for one
  16-entry FIFO, with the book's four testbenches at their shipped
  seeds and lengths. They show mechanisms (a coverage testbench kills
  nothing; reset removal hides behind zero initialization), not rates
  that transfer to other designs.
- **Timing-dependent verdicts.** Formal kills are BMC with a per-
  property limit (5 s source, 3 s netlist); "no counterexample" is a
  bounded statement. Miter verdicts of "equivalent" are proofs (IC3);
  "unknown" means no engine finished in its limit, and the first
  source run, with the population simulation sharing the four cores,
  left three miters unknown that a rerun with a 120 s rIC3 limit
  decided (see [M3]). The rIC3 proof times are tens of seconds and
  depend on load.
- **Equivalent under InFormal's model.** `m05` is equivalent only
  because the tool models asynchronous reset as synchronous (FINDINGS
  D.3). A chapter sentence must say so.
- **Verilator's zero initialization** is the documented default
  (variables without an initializer start at zero unless built with
  `--x-initial unique` and run with `+verilator+rand+reset+2`); the
  measurement [M7] shows its effect; the flag semantics were taken
  from the Verilator documentation the book already cites
  (`verilator-docs`) and not re-read this session.
- **Yosys `mutate` modes and weighting.** The five modes are measured
  from the list Yosys 0.68 printed; the selection heuristic of
  `mutate -list N` for N below the population is as documented, not
  measured.

## 7. Open questions for the outline

- **O1 (author).** Does "MCY on the book's designs" in the design doc
  require running MCY itself? MCY is not in `/opt/dvtools`; it clones
  and would run with `click` installed, but its equivalence step uses
  SymbiYosys, which the book retired for InFormal. The recommendation
  (Q5) is the mechanism on Yosys plus InFormal, with MCY named. If the
  author wants MCY run, the cheapest path is MCY with its test step
  pointed at the book's testbenches and its equivalence step replaced
  by the InFormal miter, which MCY's `[logic]` section allows.
- **O2.** Should the chapter ship a fifth testbench, Chapter 1's random
  test with a data check added to Chapter 9's checker, to show a kill
  rate rising? Or leave the gap as an exercise?
- **O3.** The DMA of `@sec-ch11` was not mutated here. Its v2 has a
  formal property set (six AXI rules) and a cocotb and an SV
  testbench; a population run on one block (the FIFO inside it, or
  the arbiter) would show mutation on a design with a protocol. Worth
  a second measurement before drafting if the chapter wants a second
  design; not needed for the spine above.
- **O4.** Report the mutation score as kill/(non-equivalent) with the
  ratio's interval, or kill rate and equivalent fraction separately
  (Q6)?
- **O5 (the AI chapters).** An LLM classifier of equivalent mutants
  scored against the miter on the 44 source mutants, whose exact
  answer is known [M3], is a small, honest experiment for
  `@sec-ch34` or the machine-learning chapter. Not run here.
- **O6.** Verilator 5.054 (2026-11-01) is out; the book pins 5.052.
  Nothing here depends on the covergroup changes except Chapter 8's
  percentages, which the kill rates do not use.
