# Outline: The Statistics of Random Testing and Coverage

Date: 2026-11-16. Status: outline for gate 1. Evidence:
`research/ch21-statistics-random-testing.md` (cited as RN with its
question, measurement or section number: Q1 to Q7, M1 to M15, RN 3.n,
RN 7(n) for confidence note n), its scripts and outputs under
`research/ch21-measurements/<name>/` (cited as `<name>/run.out:<lines>`),
and a pre-outline check of Chapter 8's own covergroup run in this
session (cited as PO, section 9; scratch only, nothing committed; the
chapter's example must reproduce it). Chapter file
`chapters/ch21-statistics-random-testing.qmd`, label `{#sec-ch21}`;
fifth chapter of the proof part, after the equivalence and static
chapter and before Graphs, Tours and Portable Stimulus; registered in
`_quarto.yml` under "Part IV · Proof and Probability", before the
generative-AI chapter. Design doc section 4, entry 21: "hit
probability, coupon collector, bounds after N clean seeds, uniformity
tests, t-way combinatorial coverage, estimating unseen coverage;
information theory as a section".

Section 1 records the decisions and, in 1.2, **the places where the
evidence contradicts or qualifies a decision handed to this outline**.
Read 1.2 before anything else. Section 1.3 is the IEEE 1800
`solve...before` check the hand-off asked for (Chapter 7 is not
contradicted).

(Written section by section; sections land in the order 0, 1, 2, 3, 4,
5, 6, 7, 8, 9.)

## 0. The chapter in one paragraph

Chapters 7 and 8 measured what a generator drew and what a
covergroup saw; neither could say how many seeds a regression needs,
what a week of clean seeds proves, whether a `dist` is honored, how
few tests cover every pair of configuration knobs, or how many bins a
generator will never reach. This chapter answers those questions with
one object: the **per-seed hit-probability vector** p, where p_i is
the chance that one seeded run of a fixed generator on a fixed design
hits bin i. A coverage bin, a cross cell, a bug's trigger and a
t-tuple of configuration values are all bins; every section is a
question about p, and every answer holds only for the generator that
defined it. Early and on its own, the chapter establishes that **the
unit of independence is the seed, not the cycle**: the FIFO's
high-occupancy bins are hit in bursts inside the runs that reach them,
so a coupon-collector argument over cycles is optimistic by a measured
factor and a species estimator over cycles sees no unseen bins, while
the same arguments over seeds agree with the simulator. The spine is
the Chapter 1 FIFO under Chapter 8's `fifo_cg`, read by path and run
under many seeds; Chapter 7's constraint examples carry uniformity;
Chapter 11's DMA transfer space carries t-way coverage. Each number
comes three ways: a formula, a standard-library Python check of the
formula, and one Verilator run where an assumption breaks. The
chapter closes with entropy, KL divergence and mutual information as
one section that hands off to the fuzzing chapter, and with a compact
account of reliability growth whose one hardware case is Malka and
Ziv's IBM data.

## 1. Decisions

### 1.1 Taken (handed to this outline, or taken here)

| # | decision | basis |
|---|---|---|
| D1 | One shared object, the per-seed hit-probability vector p, introduced once in 3.2; bins, bugs, tests and tuples are questions about it | handed; RN Q1 |
| D2 | "The unit of independence is the seed, not the cycle" is its own early section (3.3), with the coupon-collector error of the cycle-level model and the Chao1-on-cycles vs Chao2-on-seeds contrast as its evidence | handed; RN M4, M13, RN 8(4) (qualified in 1.2(1)) |
| D3 | Spine: Chapter 1 FIFO under Chapter 8's `fifo_cg`, `tb_fifo_cov.sv` and the FIFO RTL read by path; uniformity on Chapter 7's examples; t-way on Chapter 11's DMA transfer space, measured before drafting | handed; RN Q2, RN 5 (qualified in 1.2(2), (3), (4)) |
| D4 | Each formula: stated, checked in Python, confronted with one Verilator run where an assumption breaks; standard-library Python only; the stats helper becomes `examples/ch21-statistics-random-testing/common/statlib.py` | handed; RN Q3, RN 8(3) |
| D5 | Short derivations inline in Definition callouts (hit probability, union bound, Poissonized coupon integral, zero-failure Clopper-Pearson and the rule of three, Good-Turing, G = 2nKL); stated with conditions and cited: Erdős-Rényi limit, chi-square and KS limits, Chao2's lower-bound property, covering-array bounds; no new appendix | handed; RN Q4 |
| D6 | Information theory: one section (3.9), after species estimation, ending on Entropic and handing off to the fuzzing chapter by name | handed; RN Q5 |
| D7 | Clean-seed bounds describe the generator, not the design: one Pitfall in 3.5 on the measured 250-clean-seeds case | handed; RN Q7, M7 (qualified in 1.2(2)) |
| D8 | Operational profile and reliability growth: compact (3.10), cited only to sources opened (section 7); Malka and Ziv is the hardware In Practice; bug-rate curves as a sign-off metric are handed to the metrics chapter by name | handed; RN 4, RN 8(5), 8(7) |
| D9 | Each example under about 90 s on the book's machine; seed counts chosen to fit (section 4) | handed; PO timing |
| D10 | Verilator pinned at 5.052; every Verilator-derived number is printed with the release in the example output; 5.054's `solve...before` change is not measured here | handed; RN 7(12) |
| D11 | Numbers in prose are spliced from the example's `run.out`; the research `run.out` lines cited below are evidence that the example will print a number of that size, not text to copy | house rule |
| D12 | Medians and intervals, never a single resampled Chao2 figure (RN 7(14)); every randomized result names its seed | RN 7(14) |
| D13 | Epigraph is the book's own sentence | no checked quotation found |

### 1.2 Where the evidence contradicts or qualifies a handed decision

None of these changes the chapter's shape; each changes a number or
an example and is settled here under the delegation, with the
measurement it needs listed in section 4.

1. **D2's "6x" belongs to the research grid, not to Chapter 8's
   covergroup.** RN M4's factor (cycle-level i.i.d. model 4.5 seeds
   for 99% against 27 measured, `coupon/run.out:42-45`) was measured
   on the logger's 17 x 4 occupancy-by-operation grid (64 reachable
   bins). The pre-outline run of Chapter 8's own `fifo_cg` (PO,
   section 9: 1000 seeds, `+bias=even +n=200`) gives 28 reachable
   bins, rarest `push_x_full` at 0.187 per seed, measured q99 25
   seeds, median 5; the cycle-level i.i.d. model predicts 10.6 seeds
   for 99% (product form) and 15.1 (union form): optimistic by about
   2.4x, not 6x. Per bin the gap is still stark: `almost` is hit in
   1.13% of cycles, which an i.i.d.-cycles model turns into a 0.90
   chance per 200-cycle seed; measured 0.27. **Settled:** the section
   keeps D2's argument and its two pieces of evidence, but prints the
   factor the `fifo_cg` example prints (expected about 2-3x), with
   the per-bin 0.90 vs 0.27 as the lead exhibit. The 64-bin grid's 6x
   is not quoted (it is a research artifact the reader cannot rerun
   from the book's files). If the drafter wants the larger factor, it
   needs a finer `occupancy` coverpoint, which would mean a new
   covergroup and break D3; not recommended.
2. **D3 and D7: Chapter 8's testbench has no push-rate knob.**
   `tb_fifo_cov.sv` offers `+bias=even` (50/50) and `+bias=push`
   (90/25) and `+n`. The research's "push 30%" generator, which
   carries D7's Pitfall (`bug-bound/run.out:35-36`, 0 of 250, bound
   0.0119, true p 0.000040 from the Markov chain at
   `bug-bound/run.out:44`), and the four-point knob sweep of the
   information-theory section (`info-theory/run.out:18-39`) cannot be
   produced by Chapter 8's file. **Settled:** the generator knob in
   this chapter is (`+bias`, `+n`), both already in Chapter 8's file.
   D7's Pitfall uses `+bias=even` at a short run length: PO measured
   0 of 300 exposures at `+n=30` and `+n=40` and 2 of 300 at `+n=60`;
   a Markov chain of the FIFO under the even mix (PO, section 9;
   it reproduces the research chain's 0.2421 at 200 cycles) gives
   exposure probabilities 8.45e-5 at `+n=30`, 9.0e-4 at 40, 8.9e-3 at
   60 (PO measured 2 of 300 at 60, consistent). The example uses
   `+n=30`: 250 seeds are all clean with probability 0.98, the
   rule-of-three bound is about 0.012, the chain's exact p is 8.45e-5
   (about 35,000 clean seeds for a 95% chance of one exposure), and
   the text reads the gap exactly as D7 asks. The generator here is
   "even mix, 30 cycles", a short-test generator that cannot fill the
   FIFO often, which is the realistic form of the trap (a regression
   of short directed-random tests).
   The information-theory knob is {even, push} x {50, 100, 200, 400}
   cycles (8 generators, 250 seeds each, about 15 s). The research's
   numbers are evidence that the effects exist, not the printed
   numbers. Alternative rejected: a chapter-local copy of the driver
   with `+pw/+pr` plusargs (breaks "read by path"; Chapter 8's
   bins would then be a second copy to keep equal).
3. **D3's t-way space is small.** Chapter 11's `xfer_cg`
   (`examples/ch11-architecture-to-verification/tb/dma_tb_pkg.sv:347-370`)
   has four coverpoints: `len_cp` 6 bins, `out_cp` 3, `pos_cp` 3
   (sampled only when `out != OK`), `style_cp` 4; channel (2) is a
   fifth factor in version 2. Constraints: a zero-length copy cannot
   fail; `over` exists only in version 1; `pos` exists only on error.
   Pairwise on five factors with largest levels 6 and 4 has a lower
   bound of 24 rows against a full product of 432 (before
   constraints), so the space shows constraints and conditional
   factors well and shows the logarithmic growth in the number of
   factors not at all. RN M10's ten-knob "DMA-style" space
   (`covering-array/run.out:9-10`) is not Chapter 11's and must not
   be presented as it. **Settled:** the section's worked case is the
   Chapter 11 space with its exclusions as constraints (to measure:
   greedy array size, random tests to full pairwise and 3-way
   coverage under Chapter 11's own length generator and under uniform
   draws over the bins, union bound); scaling is shown by the
   Katona/Kleitman-Spencer binary construction, which the example
   builds and checks (6 rows for 10 binary factors, 10 for 126;
   `covering-array/run.out:45-48`), stated as a property of
   configuration spaces in general, not of the DMA.
4. **D3's Verilator confrontation for t-way.** Decision D4 asks for a
   Verilator run where an assumption breaks. For t-way coverage the
   breaking assumption is uniform draws over tuples; Chapter 11's
   version-2 random test is the natural run (its length generator
   makes `max` rare). Whether that test's run time fits D9 is
   unknown. **Settled:** time `examples/ch11-architecture-to-verification/v2-tests`
   first; if one seed's run fits, the t-way example reads Chapter 11's
   `xfer_cg` counts from its coverage database by path (as Chapter 8's
   runner does) for 20-50 seeds; if not, the t-way section's
   confrontation is the Python model of Chapter 11's length generator
   and the text says that no Verilator run was made for this section.
5. **The research cited Musa only by name.** D8 asks for operational
   profiles cited to sources opened. Opened this session: Musa and
   Ackerman 1989 (full text; defines the operational profile and ties
   failure-intensity estimates to testing by it) and Musa 1993's
   abstract record (definition only). **Settled:** one paragraph in
   3.10, citing Musa and Ackerman 1989 for the definition and the
   testing consequence, Musa 1993 only for the phrase "a quantitative
   characterization of how a system will be used" if the drafter
   wants it, and Miller et al. 1992 (abstract read) for zero-failure
   estimation under a non-uniform input distribution.
6. **Chao2 is a lower bound in expectation, not per sample.** Under
   push 30% the research's Chao2 resampled *mean* at 128 seeds was
   68.7 against 64 reachable bins (`species/run.out:36`): individual
   estimates overshoot when Q2 is 2-4. Chao and Colwell (read) state
   the lower-bound property for the expected value under the
   heterogeneity model. **Settled:** the text says "a lower bound on
   average, unstable when few bins were seen exactly twice", prints
   medians and the spread (D12), and never claims a single estimate
   cannot exceed the truth.
7. **Liyanage et al.'s accuracy figure.** RN 3.6 says "most
   estimators were within about 15% after a burn-in"; the paper as
   read here reports convergence to about ±3% in its bootstrapped
   setting and false peaks on real programs. **Settled:** the chapter
   cites the paper for the qualitative results only (jackknives least
   biased; all estimators under-estimated reachable coverage on real
   programs), no percentage.
8. **Böhme and Paul's 99% factor.** RN 4 gives "about 37x for 99%";
   the paper's asymptotic bound is about 37 while its simulations put
   the break-even nearer 7. **Settled:** if the chapter cites the
   paper (3.10, one sentence), it gives the 90% bound (about 4) and
   says the bound grows with the confidence asked, without the 37.

### 1.3 The `solve...before` check (escalation check requested)

**The expectation is right.** The measured class is
`rand bit s; rand bit [7:0] v; constraint c { s -> v == 0; solve s before v; }`
(`research/ch21-measurements/uniformity/tb_uniform.sv`, class
`impl_sb`). The solution set has 257 members: s = 0 with any of 256
values of v, and s = 1 with v = 0. Without the ordering the standard
asks for a uniform distribution over legal combinations, so
P(s = 1) = 1/257. With `solve s before v`, s is chosen first from
its own legal values, both of which are feasible, and then v subject
to s; P(s = 1) = 1/2, and the ordering changes the distribution
without changing the solution set. This is the worked example of the
variable-ordering clause, IEEE 1800-2023 18.5.9 (18.5.10 in
1800-2017), with a 32-bit `d` in place of the 8-bit `v`; the clause
number and the uniformity sentence are as quoted in Verilator issue
8024 (read this session; the issue's `Impl` class uses no
`solve...before` and states no expectation for it). The standard's
text itself was **not opened** (IEEE GET needs an account). The
50% sentence was read in the clause's origin, the SystemVerilog 3.1
Random Constraints proposal (Accellera sv-ec, Version 1.0,
2002-11-18, section 12, "Variable Ordering"): with the ordering "s is
true with 50% probability" and d == 0 about half the time; without
it, s true with probability about 1 in 2^32. The restrictions that
could change the expectation (ordering variables must be `rand`, not
`randc`, and integral; no circular ordering) are all met by
`impl_sb`. The drafter should open 18.5.9 through IEEE GET before
printing the clause number or any wording; until then the chapter
cites `[@ieee1800-2023]` for the semantics at clause level, as
Chapter 7 does.

**What 5.052 does.** s = 1 in 0 of 10,000 draws under seed 1
(`uniformity/run.out:13`) and 20 of 20 seeds rejected at p below
1e-110 (`uniformity/run.out:27`); without the ordering s = 1 in 38 of
10,000 (expected 38.9; `uniformity/run.out:12`). The ordering moves
the distribution away from both laws.

**Chapter 7 is not contradicted; it says the same thing.**
`chapters/ch07-constrained-random.qmd` (constraint-blocks section,
paragraph after the constraint-forms output) states that on 5.052 the
request "did not produce the balance it asks for", with s = 1 eight
times in 2000 without the request and never with it
(`examples/ch07-constrained-random/constraint-forms/run.out:6,12`),
and its distribution Pitfall says 5.052 "for `solve … before`
delivers none of the balance asked for". Its support matrix row
(`support-matrix/matrix.md:13`, "`solve … before` (legality) ...
runs") is a legality probe (`probes/r11_solve_before.sv` checks only
that s = 1 implies v = 0) and the chapter says a *runs* row is "a
legality check and not a distribution". Chapter 7 also notes that
5.054 lists a fix for "phased solve...before diversity" not yet
re-measured. This chapter's measurement adds a p-value and 10,000
draws to Chapter 7's 2000; it agrees in direction and size. Nothing
needs the author. One wording point for the drafter only: this
chapter should call it "the same result Chapter 7 reported, now as a
test" and cite `@sec-ch07-constraints`, not re-measure it as news.

## 2. Front matter

**Epigraph (own words; drafter may improve):**
> A seed is one draw. Everything else follows from counting draws
> honestly.

**Learning objectives.** After this chapter you can:

1. state, for any coverage bin, cross cell or bug trigger, its
   per-seed hit probability, estimate it from a set of seeds with an
   interval, and compute the seeds needed to hit it with a stated
   confidence;
2. say why the seed and not the cycle or transaction is the unit of
   independence in a stateful design, and show the error a cycle-level
   argument makes on the FIFO;
3. size a regression to close a covergroup with probability 1 - delta
   using the union bound, and say which bins set the answer;
4. write the correct sentence after N clean seeds, with its bound and
   its qualifier, and name what the bound cannot see;
5. test a constraint's distribution with chi-square, KS, bit and
   serial tests, size the sample for a stated power, and correct for
   testing many coverpoints at once;
6. build or read a t-way covering array for a configuration space
   with constraints, and compare it with random selection of the same
   space;
7. estimate how many bins a generator will reach and the chance that
   the next seed adds one, and say when those estimates are
   optimistic;
8. use entropy, KL divergence and mutual information to compare
   generators and to rank which knob moves which bin, and say what
   none of them measures;
9. read a reliability-growth claim about a verification project and
   name the assumptions it carries.

Word budget for title, epigraph and objectives: 300.

## 3. Sections

Budgets sum to about 16,000 words (band 14,500 to 16,500). Example paths are
under `examples/ch21-statistics-random-testing/` (section 4). Evidence
is cited as research `run.out` lines (RN) and as PO (pre-outline runs
of Chapter 8's own covergroup, section 9); in the chapter every number
is spliced from the example's own `run.out` (D11). Figures are written
by `figures/gen_ch21_figures.py`, one function each, reading the
named example's `run.out` (or a small `data.tsv` the example writes
next to it), `figures/blocks.py` palette, at most 1000 px wide.
Definition callouts carry the short derivations (D5), each at most
about 120 words of prose plus its formula.

### 3.1 Motivation: three questions a nightly regression cannot answer (~600 words)

- **Content.** Chapter 8's run A at seed 1 never reached `almost`
  (`@sec-ch08-example`), and Chapter 1's FIFO bug, the dropped push at
  15 entries, is exposed by about one 200-cycle seed in four (PO:
  247 of 1000). Three questions follow that no earlier chapter could
  answer with a number: how many seeds until every bin of `fifo_cg`
  is hit with 99% confidence; what 250 clean seeds say about a bug;
  whether a constraint is delivering the distribution it asks for.
  The chapter's claim, stated once: each question is a question about
  one vector of probabilities, and each answer holds for the
  generator that defined it and no other. Chapter 7 found no
  controlled study of constrained-random effectiveness
  (`@sec-ch07-why`); this chapter does not supply one: it supplies
  models with stated assumptions and checks them against the
  simulator, which is a different thing (RN preamble). Map of the
  chapter.
- **Reader can:** name the three questions and say what kind of
  answer (a probability under a stated generator) each will get.
- **Example:** none new; `seed-unit/run.out` exposure line spliced
  as the opening exhibit.
- **Sources:** `@sec-ch08-example`, `@sec-ch01` (the bug, by label),
  `@sec-ch07-why`.
- **Constraints:** do not contradict Chapter 7's "no controlled
  study" sentence (RN preamble).

### 3.2 One object: the hit-probability vector {#sec-ch21-p} (~1,300 words)

- **Content.** Vocabulary: a *test* is one seeded run of a fixed
  generator on a fixed design; a *bin* is any event a test can
  produce (coverage bin, cross cell, bug trigger, t-tuple). p_i is
  the probability that one test hits bin i. Bins, bugs and tuples are
  three readings of the same vector: the bug bound is the case of one
  bin whose hit is a failure; the covering array is a designed set of
  tests for tuple bins. One bin: P(missed in n tests) = (1 - p)^n,
  mean wait 1/p, n >= ln(delta)/ln(1 - p), about ln(1/delta)/p.
  Estimating p_i: the fraction of seeds that hit the bin, with a
  binomial interval (Clopper-Pearson, defined in 3.5; forward
  reference). Checks: the FIFO bug's per-seed rate from 1000 seeds
  against an exact Markov chain of the FIFO (the chain is the formula;
  Verilator is the measurement; they agree inside the interval:
  `bug-bound/run.out:34,45`, PO 247 of 1000, PO chain 0.242); Chapter
  7's packet stream at kind weight 1 in 10 misses kind 2 in a 64-packet
  run with probability 0.9^64 = 0.0012 (`coupon/run.out:19`; Python
  only, the 64-packet run is `@sec-ch07-example`). Crosses: a cell's
  probability is joint, not the product of its marginals (the FIFO's
  `push_x_full` against `push` x `full` under the even mix, PO rates;
  measured in `seed-unit/`).
- **Definition callouts (2):** the hit-probability vector (with "under
  this generator, on this design" as part of the definition); seeds to
  hit one bin (the derivation, three lines).
- **Reader can:** estimate p for a bin from a set of seeds, compute the
  seeds needed to hit it with probability 1 - delta, and say why a
  cross cell's p is not the product of its coverpoints' p.
- **Example:** `hit-prob/` (Python: the one-bin formula, the Markov
  chain of the FIFO, the 0.9^64 line) and `seed-unit/` (Verilator,
  `fifo_cg` over 1000 seeds; bug-trigger rate with interval).
- **Figure:** none (the table of per-seed rates is the output).
- **Sources:** none beyond the Clopper-Pearson forward reference.
- **Constraints:** the bug event is Chapter 8's "push while full"
  coverage line, which is the trigger, not a check (`@sec-ch08-example`
  says so); the text says the chapter counts triggers because
  Chapter 1's scoreboard reports exactly this event as the bug.

### 3.3 The unit of independence is the seed, not the cycle {#sec-ch21-seed} (~1,300 words)

- **Content.** Every formula of 3.2 assumes independent draws. Seeds
  of an unchanged generator are independent by construction (a
  check: clean streaks between exposures have mean 3.23 against the
  geometric 3.24, `bug-bound/run.out:39`; the example reprints it
  for `fifo_cg`). Cycles inside one run are not: the FIFO's occupancy
  is a Markov chain, and the high bins are hit in bursts inside the
  runs that climb there. Evidence one, coupon over cycles: per-cycle
  rates fed to an i.i.d.-cycles model predict that `almost` is hit
  in 90% of 200-cycle seeds; measured 27% (PO); across `fifo_cg` the
  cycle-level model predicts closure at 99% in about 11 seeds where 25
  are needed (PO; the research grid's version of the same comparison
  is 6x, `coupon/run.out:32-45`, not quoted, 1.2(1)). Evidence two,
  first exposure is not memoryless: no exposure before cycle 40,
  median 135 (`bug-bound/run.out:40-41`), so a per-seed rate does not
  divide by cycles into a per-cycle rate. Evidence three, an
  estimator of unseen bins (defined in `@sec-ch21-unseen`) applied to
  cycle counts sees almost nothing unseen because each reached bin is
  seen many times per run, while the same estimator over seeds sees
  the gap (`species/run.out:16-25`: at 4 seeds S_obs 58.5, cycle-based
  Chao1 60.7, seed-based Chao2 median 64.3, truth 64; under the
  low-reach generator, 128 seeds: cycle-based 49.5, seed-based median
  59, `species/run.out:36`; the `fifo_cg` versions are measured by
  the example). The rule: count seeds; treat what happens inside a
  seed as one outcome vector. Transactions in a stateful environment
  are cycles for this purpose. Where the rule can be relaxed: a
  stateless stimulus field drawn fresh per transaction (Chapter 7's
  packet kind) is i.i.d. across transactions, which is why 3.4 can
  use the packet stream at the transaction level.
- **Definition callout:** sampling unit (the independent draw an
  estimator counts; here, the seed).
- **Pitfall callout:** "a million cycles of random stimulus" is not a
  million draws; the formulas want the number of seeds, and a long
  seed is one draw with a different p.
- **Reader can:** decide, for a given bin and stimulus, whether
  cycles, transactions or seeds are the draws, and show by a
  comparison of predicted and measured per-seed rates when a cycle
  model is wrong.
- **Example:** `seed-unit/` (Verilator, `fifo_cg`, 1000 seeds at
  `+bias=even +n=200`, `.dat` per seed; prints per-bin per-cycle rate,
  i.i.d.-predicted per-seed rate, measured per-seed rate, the
  cycle-level and seed-level n99, the streak check and the
  first-exposure windows; the Chao1-cycles vs Chao2-seeds lines come
  from `unseen/`, spliced here by `lines=`).
- **Figure `fig-ch21-burst`:** per bin of `fifo_cg`, the i.i.d.-cycle
  prediction against the measured per-seed hit rate (dot pairs on a
  0-1 axis, bins sorted by measured rate); drawn from
  `seed-unit/data.tsv`.
- **Sources:** Chao and Colwell 2017 for "sampling unit" in the
  incidence sense (read).
- **Constraints:** 1.2(1) (print the example's factor, not 6x).

### 3.4 Closing every bin: the coupon collector {#sec-ch21-coupon} (~1,800 words)

- **Content.** Equal probabilities: E[T] = k H_k, about k ln k; the
  spread is of order k (Erdős and Rényi's limit law, stated with its
  conditions, not derived; read). Unequal probabilities: the
  Poissonization argument (draws as a rate-1 Poisson process, bins
  fill independently, P(all by t) = prod(1 - e^(-p_i t)), integrate
  the complement for the mean), derived in a Definition callout and
  attributed to Flajolet, Gardy and Thimonier through the secondary
  that reproduces it (original not opened; section 7). Exact CDF by
  inclusion-exclusion for small k (the packet). The union bound
  P(some bin missed) <= sum (1 - p_i)^n, valid under any dependence
  between bins, gives the safe n for every bin at 1 - delta and
  depends on the rarest bin almost alone. Specimens: the packet mix
  6:3:1 (E[T] 11.0 vs 5.5 equal; 99% at 44 exact, 55 union, 47
  Poisson; `coupon/run.out:11-19`); every value of an 8-bit `v` under
  Chapter 7's two `dist` forms (`coupon/run.out:21-27`: equal-p
  formula 27-37% low). Then the FIFO, at seed level: per-seed rates
  from 1000 seeds, union bound for 99% (PO 39 seeds), independent-bins
  product (PO 27), measured 99th percentile of seeds-to-close by
  resampling (PO 25), median (PO 5). The union bound never
  under-states, which is why it is the number for a review. Bins are
  positively correlated (the four `*_x_full` cells are hit together
  or not at all), which makes the independent-bins product pessimistic
  at the median and close at the tail (RN 3.2 (a)). The rarest-bin
  rule as the quantitative form of "the last few bins take most of
  the time". Unreachable bins: T is infinite; the formulas presuppose
  Chapter 8's exclusion review (`full_16`, `@sec-ch08-example`).
- **Definition callouts (2):** the coupon-collector time, equal and
  unequal (the Poissonized integral, derived); the union bound for
  every bin (derived in two lines, with "any dependence" stated).
- **In Practice callout:** sizing a nightly regression from a pilot:
  run a few hundred seeds, estimate per-seed rates, compute the union
  bound, and re-estimate when the generator or the RTL changes (the
  estimate is for this generator and this RTL; Chapter 8's merge and
  closure process is where the result is used, `@sec-ch08-closure`).
- **Pitfall callout:** a bin with zero hits in the pilot has no
  estimated rate; the formula's answer is "infinite", and the right
  response is a new test or an exclusion review, not more seeds.
- **Reader can:** compute the expected draws and the 99% point for
  equal and unequal bins, apply the union bound to a covergroup's
  measured per-seed rates, and name the bins that set the answer.
- **Example:** `coupon/` (Python: equal-p table with simulation, the
  packet with exact inclusion-exclusion, the 8-bit `dist` cases) and
  `seed-unit/` (Verilator `fifo_cg`: union bound, product, measured
  quantiles).
- **Figure `fig-ch21-coupon`:** P(every reachable `fifo_cg` bin hit)
  against seeds: empirical curve from resampling, seed-level
  independent-bins product, union-bound guarantee, cycle-level i.i.d.
  model; one panel; from `seed-unit/data.tsv`.
- **Sources:** Erdős and Rényi 1961 (read); Flajolet, Gardy and
  Thimonier 1992 via du Boisberranger, Gardy and Ponty (formula read
  in the secondary; original not opened).
- **Constraints:** cite the FGT formula as "given by FGT [@flajolet...]"
  only with a `note` in its entry saying where it was read; the drafter
  may instead present the integral as derived here and cite FGT as the
  source of the general expression (preferred, since the derivation is
  in the callout).

### 3.5 What N clean seeds prove {#sec-ch21-clean} (~1,500 words)

- **Content.** After n independent clean tests the exact one-sided
  1 - alpha upper bound on the per-test failure probability is
  1 - alpha^(1/n) (Clopper-Pearson at zero failures), about 3/n at
  95% (the rule of three, Hanley and Lippman-Hand) and 4.6/n at 99%.
  Derived in a Definition callout from (1 - p)^n = alpha. The Bayesian
  bounds (uniform and Jeffreys priors) for comparison, converging by
  n = 300 (`bug-bound/run.out:3-11`); the bound covers the truth at
  least 95% of the time in simulation (`bug-bound/run.out:13-21`).
  Cost of a claim: 299 clean seeds for p <= 0.01 at 95%, 2995 for
  0.001, about three million for 1e-6 (`bug-bound/run.out:23-31`);
  Butler and Finelli's life-testing arithmetic as the same argument
  at the extreme (read). With failures: the Clopper-Pearson interval
  on a known intermittent bug's rate is what triage needs (the FIFO
  bug under the even mix: 247 of 1000 in PO, interval printed by the
  example; the chain's 0.242 inside). The sentence to write in a
  release note, with its qualifier: "after N clean seeds, the per-seed
  failure probability under this generator is below 3/N at 95%".
  Limits: seeds independent and RTL unchanged (a bound accumulated
  across RTL drops is not a bound on the current RTL); clean means no
  checker fired, so the bound inherits every checker hole (Chapter 8's
  "covered is not checked", `@sec-ch08-where`); a per-seed bound is
  not a per-cycle bound (3.3, first exposure).
- **Definition callouts (2):** the zero-failure upper bound and the
  rule of three (derived); the Clopper-Pearson interval for x failures
  (stated, cited; computed by bisection in `statlib.py`).
- **Pitfall callout (D7):** the bound describes the generator, not the
  design. The FIFO under the even mix at 30 cycles per seed: 250 clean
  seeds, bound about 0.012, correct; the exact chain gives
  p = 8.45e-5 (PO), about 35,000 seeds for a 95% chance of seeing the
  bug once, and the bug is there in every seed's RTL. A bug the
  generator reaches rarely or never has small or zero p under it, and
  no count of clean seeds speaks to it. Research analog:
  `bug-bound/run.out:35-36,44` (push 30%: 0 of 250, 0.0119, true
  0.000040).
- **Reader can:** compute the exact and rule-of-three bounds after N
  clean seeds, the seeds needed for a target bound, and the interval
  on a known bug's rate; write the release-note sentence with its
  qualifier; say what the bound cannot see.
- **Example:** `clean-seeds/` (Python table and coverage simulation;
  Verilator: Chapter 8's testbench at `+bias=even +n=30`, 250 seeds,
  clean count and bound, beside the chain's exact p; and the even-mix
  200-cycle interval reused from `seed-unit/`).
- **Figure `fig-ch21-clean`:** upper bound against n (log-log), the
  3/n line and the exact bound, with a horizontal line at the n=30
  generator's true p and the point (250, 0.012) marked; from
  `clean-seeds/run.out`.
- **Sources:** Clopper and Pearson 1934 (not opened; the zero-failure
  case is derived in the text, the general interval is cited); Hanley
  and Lippman-Hand 1983 (record read; the rule as restated in Newman
  1995, read); Butler and Finelli 1993 (preprint read); Miller et al.
  1992 (abstract read) for non-uniform input distributions (3.10).
- **Constraints:** 1.2(2) (the n=30 generator, not push 30%).

### 3.6 Is the generator delivering the distribution? {#sec-ch21-uniform} (~1,600 words)

- **Content.** A `dist` or a range constraint is a hypothesis with a
  fully specified law q, so its histogram is testable for free.
  Pearson's chi-square (statistic, degrees of freedom, the expected
  count working rule stated as the book's rule without attribution,
  RN 7(4)); KS for wide integer ranges (statistic, the Kolmogorov
  limit and its slow approach, Marsaglia, Tsang and Wang; conservative
  for discrete laws); per-bit binomial tests for the defect Chapter 7
  opened with (stuck low bits, `@sec-ch07`); a serial-pair test for
  independence of consecutive draws. Power: a bit set 65% of the time
  is caught with 90% power by about 113 draws, 55% by about 1047,
  51% by about 26,000 (`uniformity/run.out:75-94`); so a
  non-rejection is a statement about a stated power, not a proof of
  uniformity. Multiple testing: the smallest of 15 bit p-values is not
  a p-value; Bonferroni; a cluster of p-values near 0.05 in one run of
  twelve tests is what twelve tests look like, and the answer is a
  larger second sample (`uniformity/run.out:1-13, 15-28`; RN 2.2 last
  paragraph). The right hypothesis: for `s -> v == 0` without ordering
  the law is uniform over 257 solutions, P(s = 1) = 1/257, and 5.052
  samples it (`uniformity/run.out:12`); with `solve s before v` the
  asked law is P(s = 1) = 1/2 and 5.052 never draws s = 1, which is
  Chapter 7's result (`@sec-ch07-constraints`) restated as a test
  with a p-value (section 1.3). Run first on Chapter 7's own printed
  histograms (the `dist` range counts and the packet kinds, read from
  Chapter 7's `run.out` files by path), then on a fresh, larger draw.
  On 5.052 with z3 every other shape is indistinguishable from its law
  at the sizes drawn (`uniformity/run.out:2-12, 46-73`); the Python
  control shows the test code itself rejects at about the nominal rate
  (`uniformity/run.out:30-44`).
- **Definition callouts (2):** goodness-of-fit test (chi-square and
  KS statements with conditions); power and sample size for a bit
  test (the normal-approximation formula, derived in two lines).
- **Pitfall callout:** testing every coverpoint every night at 0.05
  reports about one "non-uniform" coverpoint per twenty even when all
  are fine; correct for the number of tests or the dashboard is noise.
- **In Practice callout:** what to put in a regression: one histogram
  per `dist` and constrained field, one test per histogram with the
  correction, and a re-run when the simulator release changes (the
  distribution is a fact about the release, `@sec-ch07-solver`).
- **Reader can:** choose and run the right test for a constraint, say
  how many draws a test needs to see a given bias, and read a set of
  p-values without false alarms.
- **Example:** `uniformity/` (`ch07_counts.py`: tests on Chapter 7's
  printed counts read by path; `tb_draws.sv`: draws from Chapter 7's
  `forms.sv` classes included by path, plus the 16-bit range
  constraint of Chapter 7's distribution example as a one-line class,
  2000 draws each under one seed, sized for D9; `uniform.py`: the
  tests and the Python control; the power table in Python).
- **Figure:** none; a table `tbl-ch21-uniform` (constraint, test,
  statistic, p) generated from `uniformity/run.out` the way Chapter 7
  includes its support matrix (`{{< include >}}` of a generated `.md`).
- **Sources:** Pearson 1900 (read); Marsaglia, Tsang and Wang 2003
  (abstract read); IEEE 1800-2023 at clause level for the uniform
  and ordering semantics (not opened; section 1.3);
  `chakraborty2015unigen2` (in `refs.bib`) for near-uniform sampling
  as a tolerance, not exact uniformity.
- **Constraints:** the 10,000-draw research table is not reprinted;
  the example's smaller draw is what prints (D9). Bits in Chapter 7's
  output are rounded percentages and are not re-tested from it.

### 3.7 Covering every pair: t-way combinatorial coverage {#sec-ch21-tway} (~1,500 words)

- **Content.** Configuration spaces (register modes, knob plusargs,
  IP parameters) are where a designed set of tests beats random
  selection. Definitions: a covering array CA(N; t, k, v), mixed-level
  arrays, CAN; t-way coverage of a test set as the fraction of
  t-tuples present. Bounds and constructions: the trivial lower bound
  (product of the t largest level counts); the exact binary pairwise
  number (Katona; Kleitman and Spencer; as stated in Hiess and Kampel,
  read), built by the example in a few lines and checked (6 rows for
  10 binary factors, 10 for 126; `covering-array/run.out:45-48`);
  orthogonal arrays for prime-power levels (the 9-row 3^4 array,
  `covering-array/run.out:49`); growth as v^t log k (SP 800-142,
  read); greedy construction (AETG one row at a time, IPOG one
  parameter at a time; AETG metadata only, IPOG abstract read: the
  example's greedy is written from the general idea and is called
  "a greedy construction", not AETG). Random against designed: the
  expected t-way coverage of n uniform random tests is the mean over
  tuples of 1 - (1 - 1/m)^n (exact; the example checks it against
  simulation, research agreement 0.01-0.04,
  `covering-array/run.out:12-42`), the union bound gives full coverage
  at 1 - delta, and random needs about 2-4 times the tests of a
  greedy array for full coverage (`covering-array/run.out:3-10`; SP
  800-142's reported averages of 3.9, 3.8, 3.2 for 2-, 3-, 4-way as the
  outside figure); the last few percent are the coupon collector of
  3.4 over tuples. The worked space is Chapter 11's DMA transfer
  space (`len_cp`, `out_cp`, `pos_cp`, `style_cp`, channel;
  `@sec-ch11-coverage`) with its exclusions as constraints (1.2(3)):
  the array closes `len_x_out` and every other pair by construction;
  random selection under Chapter 11's own length generator leaves the
  `max` row for a long time (to be measured). Arcuri and Briand
  (abstract read): random approaches combinatorial testing as the
  number of features grows and can be arbitrarily worse under
  constraints. The interaction rule (Kuhn, Wallace and Gallo, abstract
  read; SP 800-142's restatement, read) is an empirical regularity
  from software fault data; no comparable study of RTL bugs by
  interaction strength was found (RN 7(6)), and the chapter says so.
  Honest framing: a covering array makes configuration coverage small
  and deterministic; constrained-random stimulus inside each
  configuration is still needed, and Chapter 8's crosses measure the
  same tuples after the fact (`@sec-ch08-cross`).
- **Definition callouts (2):** covering array and t-way coverage;
  expected t-way coverage of random tests (derived in one line from
  3.2).
- **Pitfall callout:** a covering array of the unconstrained space
  contains illegal rows; the constraints must go into the
  construction (as Chapter 11's exclusions do), or the array covers
  tuples the design can never be configured into and misses legal ones.
- **Reader can:** compute a lower bound on a t-way array for a mixed
  space, build or check a pairwise array, compute the expected t-way
  coverage of n random tests, and say when random selection is the
  better buy.
- **Example:** `t-way/` (Python: the binary construction and its
  check, the orthogonal array, a greedy array and random-vs-greedy
  curves on Chapter 11's space with exclusions; optionally the
  Verilator confrontation of 1.2(4) on Chapter 11's version-2 test).
- **Figure `fig-ch21-tway`:** fraction of pairs and of triples covered
  against tests, random (simulated and formula) and greedy, on
  Chapter 11's space; from `t-way/data.tsv`.
- **Sources:** NIST covering-array page (read in the research; recheck
  at draft); Colbourn tables (index read, values not retrieved: not
  cited for a number); Hiess and Kampel 2025 (read); Kleitman and
  Spencer 1973 (record only, cited through Hiess and Kampel's
  statement); Kuhn, Kacker and Lei 2010 (read); Cohen et al. 1997
  (record only: further reading, title level); Lei et al. 2007
  (abstract read); Arcuri and Briand 2012 (abstract read); Kuhn,
  Wallace and Gallo 2004 (abstract read, no percentage).
- **Constraints:** 1.2(3), 1.2(4); RN 7(13) (greedy sizes are one
  randomized implementation: print as "this construction found N",
  never as a benchmark); the research's ten-knob space is not
  Chapter 11's. Note that the research's greedy size for the same
  space differs between two runs (18 in `covering-array/run.out:9`,
  21 in `:13`): the example prints one seeded run only.

### 3.8 How many bins will this generator ever reach? {#sec-ch21-unseen} (~1,500 words)

- **Content.** A covergroup has a known bin list but an unknown
  reachable count under a given generator; an open-ended space
  (instruction sequences, FSM paths, toggle patterns) has no list.
  Species estimation answers both, with assumptions. The analogy as
  Böhme's STADS makes it (read): a test is an individual or sampling
  unit, a behavior class is a species; here a seed is the unit and a
  bin the species (incidence data, 3.3). Good-Turing: the probability
  that the next draw shows an unseen class is about f1/n (Good 1953,
  crediting Turing; read); unbiased on a known space
  (`species/run.out:13-14`). Chao1 (abundance) and Chao2 (incidence)
  as lower-bound estimators of the number of classes, with their
  conditions (Chao 1987 read for the capture-recapture form; Chao and
  Colwell 2017 read for Chao2, its assumptions and the extrapolation
  to t more units). On the FIFO: the even mix at 200 cycles, Chao2
  over seeds reaches the reachable count within a few seeds and its
  next-seed prediction tracks the measured number of new bins
  (`species/run.out:16-25`, research grid; `fifo_cg` measured by the
  example); the low-reach generator (even mix, 30 cycles, the D7
  generator) leaves the high-occupancy cells unseen, Chao2 is unstable
  (medians and spread, D12; 1.2(6)), and the discovery probability is
  small while many reachable bins have never been seen (research:
  next seed new 0.5% of the time with 14 of 64 bins unseen,
  `species/run.out:36-37`): discovery probability is a mass, and rare
  bins carry little mass. The estimate is always about the generator's
  reachable set, never the design's. Adaptive generation (coverage
  feedback, steered regressions, fuzzers) breaks the constant-p
  assumption in the optimistic direction: Böhme, Liyanage and
  Wüstholz (abstract read) on residual risk; Liyanage et al. (read)
  on reachable-coverage estimators behaving as lower bounds on real
  programs (1.2(7)).
- **Definition callouts (2):** discovery probability and the
  Good-Turing estimate (derived informally in four lines: a class seen
  once is the best evidence of the classes seen zero times);
  Chao2 and its extrapolation (stated, conditions listed).
- **Pitfall callout:** a small chance that the next seed adds a bin
  is not evidence that few bins are missing.
- **Reader can:** compute Good-Turing and Chao2 from a seed-by-bin
  incidence table, predict new bins from more seeds, and say when the
  estimate is optimistic.
- **Example:** `unseen/` (Python on the `fifo_cg` incidence tables
  written by `seed-unit/` and `clean-seeds/`; resampling for medians
  and spread; the synthetic Zipf check of Good-Turing and Chao1).
- **Figure `fig-ch21-unseen`:** bins seen and Chao2 median with a
  10-90% band against seeds, for the two generators, with a line at
  the reachable count; from `unseen/data.tsv`.
- **Sources:** Böhme 2018 (STADS; preprint read); Good 1953 (read);
  Chao 1987 (read); Chao and Colwell 2017 (read); Chao et al. 2009
  (read in the research, recheck); Böhme, Liyanage and Wüstholz 2021
  (abstract read); Liyanage et al. 2023 (read); Böhme 2018 roadmap
  (read in the research; further reading only).
- **Constraints:** D12; 1.2(6); the 30-cycle generator's numbers come
  from the example (the research's push-30% figures are evidence of
  the effect only).

### 3.9 Information: spread, distance and which knob moves which bin {#sec-ch21-info} (~1,200 words)

- **Content.** Entropy H(p), its maximum log2 k at equal p (Shannon,
  read), and 2^H as the effective number of bins. Chapter 7's
  distributions as numbers: the `:=` dist 244 effective values of 256,
  the `:/` dist 194, the kind mix 2.5 of 3 (`info-theory/run.out:1-6`).
  KL divergence from the intended law, and G = 2n KL (nats) as the
  likelihood-ratio cousin of Pearson's chi-square, equal to it to
  0.005 on the kind counts (`info-theory/run.out:8-9`): the bridge to
  3.6, derived in a Definition callout. Plug-in entropy is biased low
  on small samples (`info-theory/run.out:11-16`; the correction is
  stated as the book's working rule, RN 7(4)). The generator knob:
  across the eight (`+bias`, `+n`) generators of 1.2(2), bin-hit
  entropy, bins per seed and bug-trigger rate rank the generators
  differently (research analog: entropy peaks at push 50%, bins per
  run at 70%, exposure 1.0 from 70%; `info-theory/run.out:18-24`);
  spreading draws is not reaching the hard bins, and neither is
  checking. Mutual information I(knob; bin hit) ranks which knob
  moves which bin without a model, with a permutation baseline for its
  small-sample bias (research: 0.76-0.82 bits for the occupancy-14/15
  cells, 0 for always- and never-hit cells, baseline 0.008;
  `info-theory/run.out:25-39`); that is the question coverage-directed
  generation asks (`fine2003cdg`, `ioannides2012cdg` in `refs.bib`,
  cited for the question only). Entropic (Böhme, Manès and Cha, read):
  a fuzzer's efficiency as the information its inputs reveal, seed
  scheduling by estimated local entropy, more coverage than LibFuzzer
  on about 77% of the subjects in their evaluation: the hand-off to
  the fuzzing chapter ("Fuzzing Hardware", by name).
- **Definition callouts (2):** entropy, effective number of bins, KL
  divergence and G (one callout); mutual information (one).
- **Reader can:** compute entropy and effective bins for a `dist`,
  test a histogram with G, and rank knobs by mutual information with
  a baseline; say why maximizing entropy is not closing coverage.
- **Example:** `info/` (Python on Chapter 7's distributions; Verilator:
  Chapter 8's testbench under the eight generators, 250 seeds each;
  MI with permutation baseline).
- **Figure:** none; `tbl-ch21-knob` (generator, H, 2^H, bins per seed,
  trigger rate, MI of the top bins) generated from `info/run.out`.
- **Sources:** Shannon 1948 (read); Böhme, Manès and Cha 2020 (read);
  `fine2003cdg`, `ioannides2012cdg` (existing keys; the question only).
- **Constraints:** 1.2(2) (eight generators from Chapter 8's own
  knobs); no claim that entropy or MI predicts bugs.

### 3.10 Operational profiles and reliability growth {#sec-ch21-growth} (~800 words)

- **Content.** Compact (D8). The operational profile: the inputs a
  system meets in use and their frequencies; reliability estimated
  from tests drawn by the profile approximates field failure
  intensity (Musa and Ackerman 1989, read; Musa 1993 record for the
  one-line definition). In DV the generator plays the profile's part,
  and 3.5's Pitfall is the same point from the other side; Miller et
  al. (abstract read) give zero-failure estimates under a non-uniform
  input distribution. Reliability growth: bug discovery modeled as a
  non-homogeneous Poisson process whose rate falls as bugs are fixed
  (Goel and Okumoto, abstract read; the mean-value form printed only
  if the paper is opened, section 7). In Practice: Malka and Ziv's IBM
  study (read): two PowerPC projects, bugs from random simulation
  against simulated cycles, Laplace trend test, three growth models;
  for processor A a model fitted three months ahead predicted about
  790 total bugs against 794 found; for processor B a mid-project
  feature addition broke the trend and only the later data fitted;
  their caveat that no model is clearly better and that predictions
  hold for the test environment. Limits, from 3.5: Butler and
  Finelli's argument that growth models do not escape the scale
  problem for ultra-high reliability. One sentence of Böhme and Paul
  (read; 1.2(8)) as the quantitative case for "random first, directed
  for the holes". Bug-rate curves as a sign-off metric belong to the
  metrics chapter ("Metrics, Closure and Sign-off", by name).
- **Definition callout:** operational profile (one paragraph).
- **In Practice callout:** Malka and Ziv, dated 1998, with its
  caveats.
- **Reader can:** say what a reliability-growth prediction assumes
  (stationary test process, unchanged generator, design changes
  restart the fit) and read a bug-discovery curve claim critically.
- **Example:** none (no bug data at scale; RN 8(7)).
- **Figure:** none (a redraw of Malka and Ziv's curves would need
  their data; not done).
- **Sources:** Musa and Ackerman 1989 (read); Musa 1993 (record);
  Miller et al. 1992 (abstract); Goel and Okumoto 1979 (abstract);
  Malka and Ziv 1998 (read); Butler and Finelli 1993 (read); Böhme and
  Paul 2016 (read).
- **Constraints:** no number from a source not opened; Malka and
  Ziv's figures as reported, dated, not generalized.

### 3.11 Worked example: sizing and signing off the FIFO regression {#sec-ch21-example} (~1,200 words)

- **Content.** One flow on the spine, in the order an engineer runs
  it, each step a block of one script's output: (1) a pilot of 200
  seeds of Chapter 8's testbench at the even mix; per-bin per-seed
  rates with intervals; (2) the union bound for every reachable
  `fifo_cg` bin at 99% from the pilot, and the bins that set it;
  (3) a fresh run of that many seeds; did the covergroup close (read
  from the merged `.dat`, as Chapter 8's runner does); (4) Chao2 and
  Good-Turing over the run: no unseen reachable bin indicated, and
  the chance the next seed adds one; (5) the driver's own stimulus as
  a distribution: `op_cp` counts against 1/4 each, a chi-square on
  data the covergroup already collected; (6) the release-note
  sentence for the bug-trigger bin with the fixed RTL (with Chapter
  1's fix applied by a parameter or a sibling file, to decide) or, if
  no fixed RTL is shipped, for a bin that never fires, with the
  qualifier and the 30-cycle counter-example of 3.5. The Worked
  Example callout states the method in six lines.
- **Worked Example callout:** the six steps as a recipe.
- **Reader can:** run the whole sizing-and-sign-off loop on a
  covergroup of their own.
- **Example:** `worked/` (Verilator; Chapter 8's testbench and the
  FIFO by path; reuses `common/statlib.py` and `common/dat.py`).
- **Figure:** none (3.4's figure already shows the curve).
- **Sources:** by label only.
- **Constraints:** step (6) needs a checker, which Chapter 8's
  testbench does not have (it measures stimulus only). Settled here:
  step (6) runs Chapter 1's checking testbench
  (`examples/ch01-what-is-dv/sv-random/tb_fifo_random.sv`, its own
  queue model, 400 cycles, fixed by `localparam`) by path against
  Chapter 9's corrected RTL
  (`examples/ch09-temporal-properties/rtl/fifo_fixed.sv`, module
  `fifo`, same ports, full at DEPTH) by path, under N seeds with
  `+verilator+seed+`; a clean seed is one whose run prints no error.
  To verify before drafting: that the testbench's stimulus is
  seed-driven on Verilator (`$urandom`), its pass line is greppable,
  and N seeds fit D9. The same testbench against the buggy RTL gives
  the per-seed failure rate at 400 cycles, a second check of the
  Markov chain (chain value to compute for 400 cycles and that
  testbench's push/pop mix). With the fixed RTL `full_16` becomes
  reachable and `almost` no longer means full: the text says the bin
  list's meaning depends on the RTL, which is 3.5's "RTL unchanged"
  condition in miniature.

### 3.12 Future directions (~250 words; one Future Directions callout)

Near-uniform samplers and the distance between "a model" and "a
uniform draw" (`chakraborty2015unigen2`; `@sec-ch07-solver`);
estimators for adaptive generation (Böhme, Liyanage and Wüstholz's
adaptive-bias estimators); ML-steered closure as the case where every
estimator here loses its stationarity, with Kwon et al. as a
vendor-co-authored report labelled as such (no figure quoted, or the
4.92x figure quoted only with the label); the 5.054 `solve...before`
change, not measured. No claim of results.

### 3.13 Summary (~350 words)

One bullet per section: p; the seed; the union bound; the clean-seed
sentence and its qualifier; tests with stated power and correction;
covering arrays for configuration, random inside; unseen bins as
lower bounds about the generator; information measures spread, not
checking; growth models assume a stationary test process.

### 3.14 Exercises (~700 words; list in section 5)

### 3.15 Further reading (~150 words)

Feller's or Mitzenmacher and Upfal's treatment of the coupon
collector (edition named; not opened, title level only); NIST SP
800-142; Böhme's STADS; Chao and Colwell 2017; Malka and Ziv 1998;
Lachish, Marcus, Ur and Ziv 2002 on hole analysis (record only, title
level); Cohen et al. 1997 (title level).

### Budget

| section | words |
|---|---|
| front matter | 300 |
| 3.1 motivation | 600 |
| 3.2 hit-probability vector | 1,300 |
| 3.3 the seed is the unit | 1,300 |
| 3.4 coupon collector | 1,800 |
| 3.5 clean seeds | 1,500 |
| 3.6 uniformity | 1,600 |
| 3.7 t-way | 1,500 |
| 3.8 unseen bins | 1,500 |
| 3.9 information | 1,200 |
| 3.10 profiles and growth | 800 |
| 3.11 worked example | 1,200 |
| 3.12 future directions | 250 |
| 3.13 summary | 350 |
| 3.14 exercises | 700 |
| 3.15 further reading | 150 |
| **total** | **16,050** (callout and caption text included; target band 14,500-16,500) |

Callout census (six kinds only): Definition 18 (3.2: 2, 3.3: 1,
3.4: 2, 3.5: 2, 3.6: 2, 3.7: 2, 3.8: 2, 3.9: 2, 3.10: 1, plus
none elsewhere; drafter may merge to about 15); Pitfall 7 (3.3, 3.4,
3.5, 3.6, 3.7, 3.8, and none in 3.9); In Practice 3 (3.4, 3.6, 3.10);
Worked Example 1 (3.11); Future Directions 1 (3.12); Exercise 1
wrapping the list (3.14). Learning-objectives box is the opener, not a
callout.

Figures (5): `fig-ch21-burst` (3.3), `fig-ch21-coupon` (3.4),
`fig-ch21-clean` (3.5), `fig-ch21-tway` (3.7), `fig-ch21-unseen`
(3.8). Generated tables (2): `tbl-ch21-uniform` (3.6), `tbl-ch21-knob`
(3.9). All drawn from the book's own runs; none redrawn from a source.

## 4. Example directories

All under `examples/ch21-statistics-random-testing/`. Python examples
use the book's Python example pattern (`EXAMPLE_LANG := python`,
standard library only, `python3 -I`), print their seed, and name in
`EXPECT_OUTPUT` a line only a real run prints. Verilator examples use
the flags of `examples/mk/sv.mk` plus `--coverage` where `.dat` files
are read, Verilator 5.052 (D10), and read the Chapter 1 FIFO, the
Chapter 9 corrected FIFO, Chapter 8's `tb_fifo_cov.sv` and `lint.vlt`,
Chapter 7's `forms.sv`, Chapter 7's `run.out` files and Chapter 11's
files **by path**; none is copied or edited. A runner builds once and
loops seeds in the shell, as Chapter 8's `run_fifo_cov.sh` does.
`.dat` parsing reuses the record format Chapter 8's `bins()` awk
reads, in Python (`common/dat.py`). Times: PO measured build 13 s and
1000 seeds of 200 cycles in 7 s for Chapter 8's testbench with
`--coverage`; Python parse of 1000 `.dat` files (76 KB each) a few
seconds. Each directory's total must stay under about 90 s (D9).
Research scripts in `research/ch21-measurements/` are the starting
point; each needs the 80-column pass, the 72-column ruler, a header
naming what it is, and its numbers re-derived from the example's own
runs.

| directory | needs | design and files | `run.out` (what it prints; evidence) | time |
|---|---|---|---|---|
| `common/` | python | `statlib.py` (from `research/ch21-measurements/statlib.py`: incomplete gamma, Kolmogorov series, binomial CDF and Clopper-Pearson by bisection, coupon integral and inclusion-exclusion, union bound, entropy, KL), `dat.py` (Verilator `.dat` covergroup records to a seed-by-bin table), `fifo_chain.py` (exact Markov chain of the FIFO under a push/pop mix and run length, buggy or fixed full) | library; a self-test block prints known values (CP at x=0 equals 1 - alpha^(1/n); chain at even mix, 200 cycles, 0.2421) | < 2 s |
| `hit-prob/` | python | one-bin formula table, the chain, 0.9^64 | `coupon/run.out:19`; `bug-bound/run.out:45` | < 2 s |
| `seed-unit/` | verilator | Ch. 8 `tb_fifo_cov.sv` + Ch. 1 `fifo.sv` by path; `run_seeds.sh` (1000 seeds, `+bias=even +n=200`, one `.dat` each), `seed_unit.py` | per-bin per-cycle rate, i.i.d.-predicted and measured per-seed rate; cycle- and seed-level n99; union bound, product, resampled median and q99 of seeds-to-close; bug-trigger rate with CP interval; streak check; first-trigger windows (needs the cycle of first trigger: Ch. 8's testbench prints only the occupancy, so the window line is computed from the chain, or cut; to decide) ; writes `data.tsv` and the incidence table for `unseen/`. PO: 28 reachable, rarest 0.187, union 39, product 27, q99 25, median 5, cycle-iid 10.6 | build 13 s + 7 s + parse; ~30 s |
| `coupon/` | python | equal-p, packet, 8-bit `dist` cases with simulation | `coupon/run.out:1-27` | ~10 s (4000 trials; trim if needed) |
| `clean-seeds/` | verilator, python | bounds table, coverage simulation; Ch. 8 testbench at `+bias=even +n=30`, 250 seeds; chain value at 30 cycles | `bug-bound/run.out:1-31`; PO chain 8.45e-5; writes the 30-cycle incidence table for `unseen/` | build 13 s (or reuse `seed-unit/` build dir: no, one directory, one build) + 2 s + Python ~10 s |
| `uniformity/` | verilator + z3, python | `ch07_counts.py` (tests on Ch. 7 `distribution/run.out`, `packet-stream/run.out`, `constraint-forms/run.out` by path); `tb_draws.sv` including Ch. 7 `forms.sv` by path (`c_dist_assign`, `c_dist_divide`, `c_implication`, `c_solve_before`) plus one 16-bit range class; 2000 draws each, one seed; `uniform.py` (tests, Bonferroni, Python control); power table | `uniformity/run.out:2-13, 30-44, 75-94` (sizes differ); PO-derived budget: about 3.6 ms per `randomize()` (RN 2.2), 10,000 calls about 36 s | build ~15 s + ~40 s + Python; ~60-70 s |
| `t-way/` | python (verilator optional) | binary construction and check, orthogonal array, greedy on Ch. 11 space with exclusions, random curves (uniform over bins and under Ch. 11's length generator), union bound | `covering-array/run.out:3-10, 12-42, 44-49` as evidence of shape only; Ch. 11 space **to be measured** | ~20 s (greedy best-of-3 at t=3 may need trimming) |
| `unseen/` | python | reads the two incidence tables; Good-Turing, Chao2 with resampled median and 10-90% band, extrapolation vs held-out seeds; Chao1 on cycle counts; synthetic Zipf check | `species/run.out:1-38` as evidence; `fifo_cg` values **to be measured** | ~10 s (300 replications in the Zipf check; trim if needed) |
| `info/` | verilator, python | Ch. 8 testbench under {even, push} x {50, 100, 200, 400}, 250 seeds each; entropy, effective bins, bins per seed, trigger rate, MI with permutation baseline; entropy and G of Ch. 7's laws | `info-theory/run.out:1-39` as evidence; eight-generator values **to be measured** | build 13 s + 8 x 250 seeds (~10 s total, longer runs at n=400) + parse ~10 s; ~40 s |
| `worked/` | verilator, python | pilot 200 seeds, union bound, fresh run, merge with `verilator_coverage --write`, Chao2, `op_cp` chi-square; Ch. 1 `tb_fifo_random.sv` against Ch. 9 `fifo_fixed.sv` for the clean-seed sentence | all **to be measured** | two builds ~30 s + runs; must be timed (< 90 s) |

Build note: an example that builds two designs (worked/) may split
into `worked/` and `worked-signoff/` if the two builds and runs
exceed D9.

## 5. Exercises (each with one determinate answer; solutions to the solutions appendix)

1. A bin is hit by 1% of seeds. How many seeds give a 95% chance of
   hitting it at least once? **299** (ln 0.05 / ln 0.99 = 298.1;
   `bug-bound/run.out:24` prints 299 for the same computation).
2. 600 seeds ran clean. Give the exact one-sided 95% upper bound on
   the per-seed failure probability under that generator, and the
   rule-of-three value. **0.00498; 0.005.**
3. A six-sided die as a generator of six equally likely bins: the
   expected number of draws to see every face. **14.7** (6 H_6).
4. A covergroup has 28 reachable bins; the rarest is hit by 18.7% of
   seeds, and treat every other bin as never rarer. Using the union
   bound with each of the 28 bins at the rarest rate, how many seeds
   guarantee every bin with probability at least 0.99? **39**
   (ln(2800)/-ln(0.813) = 38.3; PO prints 39 from the measured rates,
   to be replaced by `seed-unit/run.out`).
5. Chapter 7's packet stream draws kind 2 with weight 1 in 10. The
   probability that a 64-packet run contains no kind 2. **0.0012**
   (0.9^64; `coupon/run.out:19`).
6. A bin is hit in 1.13% of cycles of 200-cycle seeds. (a) What does a
   model of independent cycles predict for the fraction of seeds that
   hit it? (b) The measured fraction is 0.27. Using the measured
   fraction, how many seeds give a 99% chance of a hit? **(a) 0.897;
   (b) 15** (ln 0.01 / ln 0.73 = 14.6). (PO values; replace with
   `seed-unit/run.out` if they move.)
7. Ten seeds; 60 bins seen; 4 bins seen in exactly one seed, 2 in
   exactly two. Chao2. **63.6** (60 + (9/10)(16/4)).
8. Two hundred seeds; three bins seen in exactly one seed. The
   Good-Turing estimate of the chance that the next seed shows a bin
   no seed has shown. **0.015.**
9. Counts 6076, 2940, 984 against a 6:3:1 law. Pearson's X^2 and the
   decision at 0.05 (critical value 5.99 for 2 degrees of freedom).
   **2.42; not rejected** (`info-theory/run.out:9`,
   `uniformity/run.out:10`).
10. Entropy of the 6:3:1 law in bits, and its effective number of
    values. **1.295 bits; 2.45** (`info-theory/run.out:5`).
11. A configuration space has factors with 6, 4, 3, 3 and 2 levels.
    The smallest number of tests any pairwise covering array can
    have, by the trivial bound. **24.**
12. Twenty binary configuration knobs. The smallest pairwise covering
    array, by the Katona/Kleitman-Spencer formula. **8** (C(6,4) = 15
    < 20 <= C(7,4) = 35; `covering-array/run.out:47` builds 8 rows
    for 35 knobs).

Twelve exercises (band 8-12). If one must go, drop 3 (the least
DV-specific). Exercise 4's and 6's numbers are PO values and must be
re-read from the example output before the chapter prints them.

## 6. Deliberately not here, and what is cited by label

- **Chapter 7 owns** `randomize()`, constraint forms, `dist` with
  `:=` and `:/`, `solve...before` semantics and its 5.052 result,
  `randc`, the solver's distribution as a measured fact, UniGen2,
  seeds and random stability (`@sec-ch07`, `@sec-ch07-constraints`,
  `@sec-ch07-solver`, `@sec-ch07-seeds`, `@sec-ch07-tools`,
  `@sec-ch07-example`). This chapter tests distributions; it does not
  re-teach the forms.
- **Chapter 8 owns** covergroups, bins, crosses, the percentage rule,
  merging, exclusion review, closure as a reviewed process, "covered
  is not checked", the FIFO coverage model and its two runs
  (`@sec-ch08`, `@sec-ch08-bins`, `@sec-ch08-cross`,
  `@sec-ch08-percentage`, `@sec-ch08-where`, `@sec-ch08-closure`,
  `@sec-ch08-tools`, `@sec-ch08-example`). This chapter adds the
  probability under each bin and the number of seeds; it does not
  re-teach closure.
- **Chapter 11 owns** the DMA and its transfer coverage model
  (`@sec-ch11-coverage`).
- **Chapter 1 owns** the FIFO and its bug (`@sec-ch01`, by label);
  Chapter 9 owns the corrected FIFO (cited by label of the section
  that introduces `fifo_fixed.sv`, to be looked up at draft).
- **Later chapters, by name only:** Graphs, Tours and Portable
  Stimulus (sequence coverage, the bridge from covering arrays of
  settings to orders of events); Fuzzing Hardware (adaptive
  generation, Entropic in practice); Mutation Testing (what a clean
  seed's checker can see); Reproducible Verification (seeds as
  inputs, regression as a build graph); Metrics, Closure and Sign-off
  (bug-rate curves, coverage ranking); Machine Learning in
  Verification (coverage-directed generation, regression selection).
- **Not here at all:** a controlled effectiveness study of random vs
  directed testing (none found; Chapter 7's sentence stands); any
  transfer of software interaction-strength percentages to RTL; a
  Goel-Okumoto fit to the book's own bug data (none exists at scale);
  scipy or any new Python dependency (D4).

## 7. Primary sources behind the chapter's definitions and bounds: read, and not read

All opened 2026-11-16 through a fetch tool that returns extracted
text, summarized; "read" means the abstract, introduction and the
section named were seen at that level. Any wording the chapter quotes
must be re-read in the document before print (no quotation is planned
beyond Shannon's one sentence and Good's credit to Turing, both
optional). BibTeX corrections made in the research note's section 6
this session: Pearson 1900 (title, venue and DOI now confirmed),
Cohen et al. 1997 (DOI and initials confirmed), Miller et al. 1992
(authors confirmed), Flajolet-Gardy-Thimonier (note: where the formula
was read; the 1987 INRIA report), Hiess-Kampel (k range of the
CAN(3,k,2) bound and attributions), Shannon (two parts, one DOI);
added `chao1987capture`, `musa1989quantifying`, `musa1993profiles`,
`newman1995small`, `accellera2002constraints`. Still unverified and
flagged in their `note`: Kuhn-Wallace-Gallo given names (record shows
"A. Gallo"), Erdős-Rényi venue and pages, Good 1953 issue and last
page, Böhme-Paul volume and pages, Arcuri-Briand and Liyanage DOIs,
Goel-Okumoto and Hanley authors (records show none), Kwon et al. year.

| claim the chapter makes | source | status | URL read | section used |
|---|---|---|---|---|
| coupon-collector limit law exp(-e^(-c)) | Erdős and Rényi 1961 | **read** (scan; theorem for m = 1; venue not printed in scan) | https://static.renyi.hu/~p_erdos/1961-09.pdf | 3.4 |
| unequal-probability coupon integral | Flajolet, Gardy and Thimonier 1992 | **not opened** (HAL bot block; 1987 report cover only); formula **read** in du Boisberranger, Gardy and Ponty, eq. 1.1 | https://arxiv.org/pdf/1202.0920 ; https://core.ac.uk/download/50449011.pdf | 3.4 |
| zero-failure bound, rule of three | Hanley and Lippman-Hand 1983 | **record only** (Scilit: JAMA 249(13):1743-1745, DOI; authors not shown); rule and attribution **read** in Newman 1995's letter | https://scilit.net/publications/ddfc523d905fccaecb8488227831d6ec ; https://jamanetwork.com/journals/jama/article-abstract/389714 | 3.5 |
| Clopper-Pearson interval | Clopper and Pearson 1934 | **not opened** (records only); zero-failure case derived in the chapter | — | 3.5 |
| limits of life testing and growth models | Butler and Finelli 1993 | **read** (NASA preprint) | https://ntrs.nasa.gov/api/citations/20040139817/downloads/20040139817.pdf | 3.5, 3.10 |
| zero-failure estimate under non-uniform inputs | Miller et al. 1992 | **abstract read** (NTRS) | https://ntrs.nasa.gov/citations/19920043306 | 3.5, 3.10 |
| chi-square statistic | Pearson 1900 | **read** (scan; statistic and P from n' - 1 independent errors) | https://jhanley.biostat.mcgill.ca/bios601/Proportion/Pearson1900.pdf ; https://zenodo.org/records/1430618 | 3.6 |
| Kolmogorov distribution, slow approach | Marsaglia, Tsang and Wang 2003 | **abstract read** | https://www.jstatsoft.org/article/view/v008i18 | 3.6 |
| uniform distribution over legal combinations; variable ordering | IEEE 1800-2023 18.5.9 | **not opened** (IEEE GET needs an account); clause number and uniformity sentence **read** as quoted in Verilator issue 8024 | https://github.com/verilator/verilator/issues/8024 | 1.3, 3.6 |
| 50% under `solve s before d` | SystemVerilog 3.1 Random Constraints proposal 2002 | **read** (section 12) | https://accellera.org/images/eda/sv-ec/att-0248/01-Random-Constraints_Proposal.pdf | 1.3 (evidence, not a chapter citation for the standard) |
| covering array definition; v^t log k growth; interaction rule; random vs array ratios | Kuhn, Kacker and Lei 2010 (SP 800-142) | **read** (first 100,000 characters) | https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-142.pdf | 3.7 |
| faults triggered by few interacting parameters | Kuhn, Wallace and Gallo 2004 | **abstract read** (no percentage cited) | https://csrc.nist.gov/pubs/journal/2004/06/software-fault-interactions-and-implications-for-s/final | 3.7 |
| IPOG strategy | Lei et al. 2007 | **abstract read** | https://csrc.nist.gov/pubs/conference/2007/03/29/ipog-a-general-strategy-for-tway-software-testing/final | 3.7 |
| AETG | Cohen et al. 1997 | **record only** (no abstract): title-level further reading | https://www.scilit.com/publications/7be428f0b528234f7976ea8779150744 | 3.7, 3.15 |
| CAN(2,k,2) exact; CAN(2,13,3) = 15 | Hiess and Kampel 2025 (states Katona; Kleitman and Spencer) | **read** (HTML v1 background) | https://arxiv.org/html/2510.17596v1 | 3.7 |
| (same) | Kleitman and Spencer 1973 | **record only** (no abstract); cited through Hiess and Kampel | https://scilit.com/publications/c32d0f2256284da93f17fc1fc85aa6f9 | 3.7 |
| random vs combinatorial; arbitrarily worse under constraints | Arcuri and Briand 2012 | **abstract read** | https://orbilu.uni.lu/handle/10993/1190 | 3.7 |
| covering array tables | NIST page; Colbourn tables | NIST **read in the research** (not re-opened here); Colbourn **index only**, no values | https://math.nist.gov/coveringarrays/coveringarray.html | 3.7 (definition only) |
| testing as species discovery; Good-Turing and Chao1 as used in testing | Böhme 2018 (STADS) | **read** (arXiv v2; TOSEM metadata not on the preprint) | https://arxiv.org/pdf/1803.02130 | 3.8 |
| missing mass f1/N, credited to Turing | Good 1953 | **read** (scan, sections 1-2) | https://gwern.net/doc/statistics/order/capture/1953-good-2.pdf | 3.8 |
| Chao lower bound (capture-recapture form) | Chao 1987 | **read** | https://gwern.net/doc/statistics/order/capture/1987-chao.pdf | 3.8 |
| Chao2, assumptions, lower-bound property, extrapolation | Chao and Colwell 2017 | **read** (eq. 2b, 7c and assumptions) | https://gwern.net/doc/statistics/order/capture/2017-chao.pdf | 3.3, 3.8 |
| Chao1 (abundance) original | Chao 1984 | **not opened**; Chao1 cited through Chao and Colwell and STADS | — | 3.8 |
| residual risk under adaptive fuzzing | Böhme, Liyanage and Wüstholz 2021 | **abstract read** | https://2022.esec-fse.org/details/fse-2022-esec-fse-2021/22/Estimating-Residual-Risk-in-Greybox-Fuzzing | 3.8, 3.12 |
| reachable-coverage estimators | Liyanage et al. 2023 | **read** (author copy) | https://mpi-softsec.github.io/papers/ICSE23-effectiveness.pdf | 3.8 |
| entropy maximal at equal p | Shannon 1948 | **read** (section 6) | https://people.csail.mit.edu/dmoshkov/courses/codes/shannon1948.pdf | 3.9 |
| Entropic | Böhme, Manès and Cha 2020 | **read** (author copy) | https://softsec.kaist.ac.kr/%7Esangkilc/papers/bohme-fse20.pdf | 3.9 |
| operational profile | Musa and Ackerman 1989 | **read** (course copy) | https://www.rose-hulman.edu/class/csse/csse376/Resources/musa.pdf | 3.10 |
| operational profile (definition sentence) | Musa 1993 | **record and abstract only** | https://www.scilit.net/publications/715ca10803e745574e3f0c6d1814f5c5 | 3.10 (optional) |
| NHPP growth model | Goel and Okumoto 1979 | **abstract only** (mean-value form not shown: do not print the formula until opened) | https://scilit.com/publications/a0ef8d84616bdb7c34ba257dbd33ef3a | 3.10 |
| hardware reliability growth | Malka and Ziv 1998 | **read** | https://www.cs.york.ac.uk/rts/docs/SIGDA-Compendium-1994-2004/papers/1998/dac98/pdffiles/39_2.pdf | 3.10 |
| random vs systematic efficiency | Böhme and Paul 2016 | **read** (accepted version) | https://mboehme.github.io/paper/TSE15.pdf | 3.10 |
| expected-count rule for chi-square; Stephens' KS correction; Miller-Madow | Cochran; Stephens; Miller 1955 | **not opened**: stated as the book's working rules, unattributed (RN 7(4)) | — | 3.6, 3.9 |
| ML-steered closure | Kwon et al. (DVCon) | **read in the research** (not re-opened); vendor co-authored | https://dvcon-proceedings.org/wp-content/uploads/1096.pdf | 3.12 |
| Littlewood and Strigini 1993; Duran and Ntafos 1984; Hamlet 1987; Lachish et al. 2002; sequence covering arrays | — | **not opened**: not cited for content (Lachish at title level in further reading only) | — | — |

## 8. Gate-1 checklist (against AGENTS.md)

| requirement | where met |
|---|---|
| every section names what the reader must be able to do | "Reader can" in 3.1-3.11; objectives 1-9 map to 3.2 (1), 3.3 (2), 3.4 (3), 3.5 (4), 3.6 (5), 3.7 (6), 3.8 (7), 3.9 (8), 3.10 (9); 3.11 exercises 1, 3, 4, 5, 7 together |
| the research note's constraints are folded in | RN Q1-Q7 answered by D1-D8 and 1.2; RN 8(1)-(9) answered: spine (D3, 1.2(2)-(4)), proof depth (D5), dependency (D4), cycle dependence (D2, 3.3), operational profile (D8, 1.2(5)), information theory (D6), reliability growth (D8; no own fit), covergroup cost (D9, section 4 times), re-measure on 5.054 (D10: no); RN 7(1)-(15) applied in section 7 and the constraint lines of 3.4-3.9 (FGT via secondary, no Kuhn percentage, greedy as one implementation, Chao2 medians, `fifo_cg` measured in the examples) |
| a question that changes the chapter's shape is raised, not chosen | none found: 1.2's eight items change numbers and examples, not sections; the `solve...before` check (1.3) finds Chapter 7 consistent, so no earlier approved chapter is implicated |
| escalate: an earlier approved chapter wrong | no (1.3) |
| house template | epigraph, objectives, motivation (3.1), concepts (3.2-3.10), worked example (3.11), callouts of six kinds only (census in Budget), future directions (3.12), summary (3.13), exercises (3.14), further reading (3.15) |
| every listing a file under `examples/` | section 4; no code in prose; Chapter 1, 7, 8, 9 and 11 files read by path, none copied or edited |
| simulator output from `run.out` | every Verilator number is a line of an example's `run.out` (D11); the research lines and PO values in this outline are evidence, re-derived by the examples |
| every number sourced | research `run.out` lines, PO (section 9) and the sources of section 7; no number from a source marked not opened |
| vendor figures labelled | Kwon et al. only, labelled vendor co-authored (3.12) |
| 80 columns, 72-column rulers, real tabs | section 4 preamble |
| cross-references by label, later chapters by name | section 6; no hard-coded chapter or section number planned in prose |
| American spelling | to hold in the draft ("behavior", "modeled", "honored") |
| attribution and originality | section 7; no figure redrawn from a source; one optional short quotation each from Shannon and Good, re-read before print |
| the book never cites its working documents | chapter cites `refs.bib` keys and splices `run.out`; never `research/` |
| publication rule | no assistant or its vendor named in this outline or planned files |
| registration in `_quarto.yml` | under "Part IV · Proof and Probability", after the equivalence chapter (or after `ch19` if that chapter is not yet registered), before the generative-AI chapter, at draft time |
| 8 to 12 exercises with determinate answers | section 5: twelve |
| new `refs.bib` entries (about 26) | erdos1961coupon, flajolet1992coupon, boisberranger2012weighted, clopper1934binomial, hanley1983nothing, newman1995small, butler1993infeasibility, miller1992nofailures, pearson1900chisquare, marsaglia2003kolmogorov, kuhn2010practical, kuhn2004interactions, lei2007ipog, cohen1997aetg, hiess2025balanced, kleitman1973kindependent, arcuri2012interaction, nist-covering-arrays, boehme2018stads, good1953species, chao1987capture, chao2017thirty, boehme2021residual, liyanage2023reachable, shannon1948communication, boehme2020entropic, musa1989quantifying, musa1993profiles (optional), goel1979nhpp, malka1998bugdata, boehme2016efficiency, kwon-dvcon-simai; existing: ieee1800-2023, chakraborty2015unigen2, fine2003cdg, ioannides2012cdg, verilator-changes |
| new glossary terms | hit-probability vector, sampling unit, coupon-collector time, union bound, rule of three, Clopper-Pearson interval, goodness-of-fit test, power, Bonferroni correction, covering array, t-way coverage, discovery probability (missing mass), Good-Turing estimate, Chao2, entropy, effective number of bins, KL divergence, mutual information, operational profile, reliability growth |

Gate-1 verdict proposed for `STATUS.md` (to be written by the session
that records the gate, not by this outline): passes under the
delegation on 2026-11-16, with section 9's "before drafting" list as
preconditions for the sections that need them (3.3, 3.4, 3.7, 3.8,
3.9, 3.11).

## 9. Pre-outline measurements (PO) and what must be measured before drafting

### 9.1 Run in this session (scratch only; not committed)

Verilator 5.052 from `/opt/dvtools/bin`, Python 3.13.18. Chapter 8's
`tb_fifo_cov.sv`, `lint.vlt` and Chapter 1's `fifo.sv` built by path
with the flags of `run_fifo_cov.sh` (build 13 s). 1000 seeds,
`+bias=even +n=200 +verilator+seed+<s>`, one `.dat` each: 7 s.
Results:

- Bug trigger ("covered: push while full"): 247 of 1000 seeds.
- `fifo_cg` has 29 bins (`fill_cg` adds `climb`); 28 reachable
  (`full_16` never hit). Per-seed rates: `push_x_full` 0.187,
  `idle_x_full` 0.190, `pop_x_full` 0.218, `both_x_full` 0.235,
  `full` and `almost` 0.271, `high` 0.815, the four `*_x_empty`
  0.848-0.935, the rest 1.000. `climb` 0.097.
- Seeds to hit all 28 reachable `fifo_cg` bins (2000 resamples):
  median 5, 99th percentile 25. With `climb`: median 9, q99 42.
- Union bound at 99%: 39 seeds. Independent-bins product: 27 seeds.
- Cycle-level i.i.d. model from per-cycle rates (bin count / 200,000
  cycles): `almost` 1.13% per cycle, predicted per-seed 0.898 against
  0.271 measured; the `*_x_full` cells 0.26-0.30% per cycle, predicted
  0.41-0.45 against 0.19-0.24. n99: 10.6 seeds (product), 15.1 (union).
- Run length at the even mix, 300 seeds each: 0 triggers at `+n=30`
  and `+n=40`, 2 at `+n=60`.
- Exact Markov chain of the FIFO (16 occupancy states, full at 15,
  trigger = push request while full, independent push and pop at
  1/2): P(trigger within n cycles) = 8.45e-5 (30), 3.3e-4 (35),
  9.0e-4 (40), 1.95e-3 (45), 3.6e-3 (50), 8.9e-3 (60), 0.242 (200);
  the push mix (0.9/0.25) at 200 cycles: 1.000. The 200-cycle value
  matches the research chain (`bug-bound/run.out:45`).

### 9.2 Before drafting (each becomes a line of an example's `run.out`)

1. `seed-unit/`: the 9.1 numbers from the shipped scripts, plus the
   streak check on `fifo_cg`'s bug trigger. Decide whether the
   first-trigger-cycle windows (RN M8) are reprinted: Chapter 8's
   testbench does not print the trigger cycle; either compute the
   first-passage distribution from the chain (`common/fifo_chain.py`)
   or cut the line from 3.3.
2. `unseen/`: Chao1 on cycle counts and Chao2 on seeds for `fifo_cg`
   under the even 200-cycle and even 30-cycle generators; with only 28
   reachable bins and most hit by every seed, check that the contrast
   is still visible (if Chao1-on-cycles and Chao2 agree on `fifo_cg`,
   3.3's third piece of evidence becomes the research grid's figure,
   described as a finer grid of the same bins, or is dropped; record
   which).
3. `clean-seeds/`: 250 seeds at `+bias=even +n=30` (expected all
   clean, probability 0.98); if a trigger appears, report it (a
   correct outcome with probability 0.02) and do not reseed to hide it.
4. `info/`: the eight generators; check that entropy, bins per seed
   and trigger rate still rank them differently (if they agree, 3.9
   says so and keeps the research sweep as the illustration that they
   need not).
5. `t-way/`: the Chapter 11 space with exclusions: greedy size for
   t = 2 and 3, lower bounds, random-to-full medians (uniform over
   bins, and under Chapter 11's length generator), union bound; and
   the run time of `examples/ch11-architecture-to-verification/v2-tests`
   for one seed (decides 1.2(4)).
6. `uniformity/`: time 2000 draws of each class on 5.052 with z3 and
   confirm the total under 90 s; confirm `forms.sv` compiles when
   included into a new top.
7. `worked/`: confirm Chapter 1's `tb_fifo_random.sv` is seed-driven
   on Verilator and has a greppable pass/fail line; the chain value
   for its 400-cycle mix; total time.
8. Open IEEE 1800-2023 18.5.9 (IEEE GET) and the Clopper-Pearson and
   Goel-Okumoto papers if the chapter is to print their wording or
   formula beyond what section 7 allows.
