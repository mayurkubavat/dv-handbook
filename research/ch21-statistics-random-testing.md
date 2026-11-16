# Research note: The Statistics of Random Testing and Coverage (Chapter 21)

Date: 2026-11-16. Status: research for gate 1 (no outline yet).
Written section by section, the deciding questions first. Sections:
1 questions that decide the chapter, 2 measurements (table of results,
scripts under `research/ch21-measurements/<name>/`), 3 the mathematics
topic by topic (statement with conditions, sources, DV application,
where the assumptions break), 4 literature on closure prediction and
reliability growth, 5 the worked-example spine, 6 bibliography
(BibTeX-ready), 7 confidence notes, 8 open questions for the outline.

Scope given: design doc section 4, entry 21: "hit probability, coupon
collector, bounds after N clean seeds, uniformity tests, t-way
combinatorial coverage, estimating unseen coverage; information theory
as a section". Part: Proof and Probability, after the formal chapters
and before Graphs, Tours and Portable Stimulus.

What earlier chapters already teach and this chapter cites by label,
not repeats: `randomize()`, constraint forms, `dist` with `:=` and
`:/`, the solver's distribution as a measured fact, seeds and random
stability (`@sec-ch07`, `@sec-ch07-solver`, `@sec-ch07-seeds`);
covergroups, bins, crosses, the percentage rule, merge and closure as a
reviewed process (`@sec-ch08`, `@sec-ch08-cross`, `@sec-ch08-closure`);
the FIFO coverage model and its two runs (`@sec-ch08-example`). Ch 7
says "no controlled study of constrained-random effectiveness ... was
found" and prints no number; this chapter is where numbers *with stated
assumptions* become possible, and must not contradict that sentence
(it supplies models, not an effectiveness study).

Pins for every measurement: Python 3.13.18, standard library only (no
numpy or scipy: the book's `dvbook` venv at `/opt/dvtools/venv` has
neither, and the logic chapter's precedent is that no new Python
dependency enters the environment); Verilator 5.052 with z3 from
`/opt/dvtools/venv/bin/z3` (z3-solver 5.4.1.0); Icarus from
`/opt/dvtools/bin`. All random experiments take a fixed seed printed in
their output.

## 1. Questions that decide the chapter

These are the choices the outline must make; each changes what sections
exist or what the worked example has to carry.

**Q1. Is the chapter's object a bin, a bug, or a test?** Three
different random variables run through the topics. Coupon collector and
species estimation are about *bins* (a finite, known or unknown set of
events, each hit with some per-test probability). The rule of three and
Clopper-Pearson are about *bugs* (an unknown per-test failure
probability, estimated from N passing tests). Covering arrays are about
*tests* (a designed set chosen to cover all t-tuples). The chapter
reads coherently only if one per-test probability vector p (the chance
that one random test hits bin i, or exposes bug j) is introduced once,
early, and every later section is a question about p. Recommendation:
introduce "the hit-probability vector" in section 1 of the chapter and
reuse it everywhere; the bug-bound section is the special case of one
unknown bin whose hit means failure.

**Q2. Which running example: Ch 8's FIFO covergroup, or Ch 7's packet
`dist`?** The FIFO's `fifo_cg` has strongly unequal bin probabilities
under even stimulus (run A: `almost` and `full_16` never hit in 200
cycles; `op_x_empty` cells near 1%), which is exactly what makes the
equal-probability coupon formula wrong; the packet's `kind dist {6:3:1}`
is a clean multinomial for the uniformity and goodness-of-fit section.
Measured below (section 2) both carry their sections. Recommendation:
the FIFO covergroup is the spine (bins, crosses, unseen-bin estimation,
bounds after clean runs against the Ch 1 full-at-15 bug); the packet
`dist` and the 16-bit `v < 16'h8000` constraint from the distribution
example are the goodness-of-fit specimens. Decision for the outline:
whether to add the packet as a second spine or treat it as a side
example.

**Q3. Do the chapter's numbers come from formulas, from simulation of
the formulas in Python, or from Verilator runs?** The house rule is that
every number has a source; for mathematics, the source is a derivation
plus a measurement that agrees with it. The measurements below show the
three agree where the assumptions hold and disagree in instructive
places (the FIFO's bin hits are *not* independent across cycles, so
cycle-level coupon formulas overestimate coverage speed by a measured
factor). Recommendation: each formula is stated, then checked by a
pure-Python simulation, then confronted with one Verilator run where the
assumption breaks. That structure is what makes the chapter more than a
statistics primer.

**Q4. How much proof?** The book's audience is DV/RTL engineers; the
logic chapter derives DPLL, the formal chapter derives k-induction.
Recommendation: derive the hit probability, the equal-probability
coupon expectation, the union bound for "every bin with probability
1 - delta", the rule of three, and the Good-Turing missing-mass
estimate (all short); *state* with conditions and cite the unequal
coupon integral (Flajolet, Gardy and Thimonier), Clopper-Pearson, the
chi-square and Kolmogorov-Smirnov limits, the covering-array bounds and
Chao1's lower-bound property. The outline must decide whether the
derivations go inline or into a mathematical appendix.

**Q5. Does information theory earn a full section, or a closing
section?** The spec says "information theory as a section". The
measured content (entropy of a `dist` as a uniformity score, KL
divergence from target as the quantity chi-square approximates,
mutual information between a stimulus knob and a bin as a "which knob
moves this bin" ranking, and Böhme, Manès and Cha's Entropic, which
uses species entropy to schedule fuzzing) is enough for one section of
moderate length. Recommendation: one section, placed after species
estimation, because entropy over the bin-hit distribution is the same
object Entropic estimates; it then hands off to the fuzzing chapter.

**Q6. Where does the chapter stop and the fuzzing, mutation and CDG
chapters begin?** Species estimation and residual risk are Böhme's
fuzzing results; reliability growth models are software-reliability
results; coverage-directed generation is the ML chapter's. The chapter
should own the *estimators* and their assumptions and point forward to
the fuzzing chapter for adaptive (non-stationary) generation, which is
exactly where the estimators' assumptions break (section 3.6.4).

**Q7. Bounds for "bug rate" are about a test *distribution*, not the
design.** The rule of three bounds the failure probability of one
random test *drawn from this generator*. A bug the generator cannot
reach has probability zero under it and no number of clean seeds says
anything about it. This is the single most important caveat and must be
in a Pitfall in the bug-bound section; the outline should decide
whether the chapter also teaches operational-profile weighting
(Musa) or only states the limit.

## 2. Measurements

Every script and its saved output is under
`research/ch21-measurements/`. `statlib.py` holds the shared functions
(regularized incomplete gamma for the chi-square tail, the Kolmogorov
limit series, binomial CDF and Clopper-Pearson by bisection, the
coupon-collector integral, its Poissonized CDF and exact
inclusion-exclusion, the union bound, entropy and KL), standard library
only. Each directory holds the script and `run.out`; `fifo-log/` and
`uniformity/` also hold the Verilator testbench, `run.sh` and the raw
logs under `out/` (the uniformity draws gzip-compressed). Build
directories are deleted by each `run.sh`.

### 2.0 The FIFO logger (`fifo-log/`)

`tb_fifo_log.sv` is Chapter 8's FIFO coverage driver and monitor
(`examples/ch08-functional-coverage/fifo-coverage/tb_fifo_cov.sv`) with
the covergroup replaced by a plain 17 x 4 counter array (occupancy
0..16 by operation `{rd_en, wr_en}`), so that one run prints one line
Python can read: the per-bin hit counts and whether a push was
requested while the DUT showed full (the dropped push that Chapter 1's
scoreboard reports; the bug is `full` at 15 entries). Push and pop
percentages are plusargs. `run.sh` builds it once on Verilator 5.052
and writes `out/even.log` (1000 seeds, 50/50, 200 cycles: Chapter 8's
run A mix), `out/sweep.log` (push 30/50/70/90 percent, pop 50, 250
seeds each) and `out/long.log` (one run of 20000 cycles). Whole script:
13 s. The covergroup is not used because the counts are needed per
run and Chapter 8 already measured the covergroup itself; the bins are
the same cross Chapter 8 samples, at finer occupancy resolution.

Sanity check against Chapter 8: the logger's seed-1 run, like Chapter
8's run A at seed 1, never reaches occupancy 15 (`exposed=0`); every
run samples exactly 200 cycles. The grid has 68 bins of which 64 are
reachable (occupancy 16 cannot occur because the DUT stops at 15).

### 2.1 Results table

| # | Experiment | Result | Where |
|---|---|---|---|
| M1 | Equal-probability coupon collector, k = 8, 64, 256 | E[T] = k H_k = 21.7, 303.6, 1567.8; simulation (4000 trials) 22.0, 305.4, 1566.9. Draws for 99%: exact 51 (k = 8); union bound 51, 557, 2594; Poissonized 54, 561, 2598 | `coupon/run.out` s.1 |
| M2 | Packet `kind dist {6:3:1}` (Ch 7 `rand_packet.sv`) | E[T] = 11.0 packets (5.5 if the three were equal); P(all three kinds within 10 / 20 / 30 / 44 packets) = 0.629 / 0.878 / 0.958 / 0.990 exact; 99% needs 44 (union bound 55, Poisson 47). P(no kind 2 in Ch 7's 64-packet run) = 0.9^64 = 0.0012 | `coupon/run.out` s.2 |
| M3 | Every value of an 8-bit `v` under Ch 7's `dist` forms | uniform: E[T] = 1568, 99% at 2598; `:=` {1,1,2}: E[T] = 2143, 99% at 3793 (union 4177); `:/` {1,1,2}: E[T] = 2027, 99% at 3399. The equal-p formula is 27-37% low for both | `coupon/run.out` s.3 |
| M4 | FIFO grid, the independence assumption, Verilator | Per-cycle rates from one 20000-cycle run, fed to an i.i.d.-cycles model, predict P(bin hit in a 200-cycle run) = 0.71 for `occ15_*`; measured over 1000 seeds: 0.18. The i.i.d. model over-predicts 56 of 64 bins. Seeds to cover all 64 reachable bins: measured median 6, 99th percentile 27; the cycle-level i.i.d. model says 4.5 seeds for 99% (6x optimistic); a seed-level model (bins independent, per-seed rates measured) says median 11, n99 29; seed-level union bound 44 | `coupon/run.out` s.4 |
| M5 | Bounds after n clean tests | 95% upper bound on p: n = 10: 3/n 0.300, Clopper-Pearson 0.259, Bayes (uniform prior) 0.238, Jeffreys 0.171; n = 300: 0.0100, 0.0099, 0.0099, 0.0064; converge for n >= 300. Tests needed for p <= 1e-3 at 95%: 2995; at 99%: 4603; for 1e-6 at 95%: 2,995,731 | `bug-bound/run.out` s.1, s.3 |
| M6 | Coverage of the CP bound by simulation | Conservative as theory says (>= 0.95 in all six cells, 0.964-1.000) | `bug-bound/run.out` s.2 |
| M7 | The FIFO bug per seed, Verilator, 200 cycles | 50/50: 236 of 1000 seeds expose it, p = 0.236, 95% CP [0.210, 0.264]; an exact Markov chain of the FIFO gives 0.2421 (inside the interval). 18 clean seeds give a 99% detection chance. Clean streaks: mean 3.23 vs geometric 3.24. Push 70%: 250/250. Push 30%: 0 of 250, so "p <= 0.0119 at 95%"; the Markov chain gives p = 0.000040, and 74,143 seeds for a 95% detection chance | `bug-bound/run.out` s.4, s.5 |
| M8 | Per-cycle hazard of the FIFO bug | First exposure never before cycle 40, median 135; by 50-cycle window 3, 56, 84, 93: not constant, so a seed's failure probability is not proportional to its length | `bug-bound/run.out` s.4 |
| M9 | Uniformity of Ch 7 constraint shapes, Verilator 5.052 + z3 | No test rejects the asked-for law except `solve s before v`: 10,000 draws each of `v < 16'h8000`, `:=` and `:/` dists per value, the packet kind mix 6:3:1 and the joint-uniform `s -> v == 0` (s = 1 in 38 of 10000, 38.9 expected): p from 0.013 to 0.76, none below the 12-test Bonferroni threshold; 50,000 draws of the 16-bit range: chi-square p = 0.87, KS p = 0.56, every bit within 0.25 points of 50%. Across 20 seeds x 500 draws, 8 of 220 tests below 0.05 (11 expected; Python control 18). `solve s before v`, asked for s = 1 half the time: 0 of 10000, p = 0 | `uniformity/run.out` |
| M10 | Covering arrays vs random, pairwise and 3-way | Greedy (AETG-style) sizes: binary k = 10, t = 2: 9 (known optimum 6, and the Katona / Kleitman-Spencer construction gives 6); 3^4, t = 2: 9 (= optimum, = orthogonal array); 3^13, t = 2: 19 (best known 15); DMA-style mixed space (4,3,2,3,2,2,2,4,3,3), t = 2: 18 (lower bound 16), t = 3: 72 (lower bound 48). Uniform random tests to full coverage (median of 41 runs): 18, 38, 63, 65, 294; the union bound for 99%: 35, 73, 95, 120, 473. Random/greedy ratio 2.0-4.2 | `covering-array/run.out` |
| M11 | Coverage curve, mixed space | Random tests reach 82% of pairs with 16 tests (greedy 98%), 97% with 32, all by about 64-100; 3-way: random 48% at 16, 92% at 64; expected-coverage formula 1 - (1 - 1/m)^n matches the simulation to 0.01-0.04 | `covering-array/run.out` |
| M12 | Good-Turing and Chao1 on a known bin space (200 bins, Zipf) | Good-Turing f1/n is unbiased for the missing mass (mean over 300 replications 0.2305 vs true 0.2309 at n = 200; 0.0212 vs 0.0218 at n = 1600); Chao1 is a lower bound (mean 156 at n = 200, 199 at n = 1600, truth 200) | `species/run.out` s.1 |
| M13 | Unseen bins on the FIFO grid, Verilator | 50/50 mix: Chao2 (seed as sampling unit) median 64.3 at 4 seeds, 64.0 at 8, when 58.5 and 62.8 bins had been seen; prediction of new bins in the next seed 1.56 / 0.37 vs measured 1.95 / 0.40. Push 30%: after 128 seeds 44.6 bins seen, Chao2 median 59 (mean 69, unstable), Chao1 on cycle counts 49.5; the next seed shows a new bin 0.5% of the time while 14 reachable bins have never been seen | `species/run.out` s.2, s.3 |
| M15 | Power of a uniformity test | A bit set with probability 0.65 (Ch 7's pre-fix bug was 65-90%): 90% power at 113 draws; 0.55: 1047; 0.51: 26,265. 50,000 draws resolve a bias of about 0.007 | `uniformity/run.out` s.3 |
| M14 | Entropy and mutual information | Entropy of the Ch 7 `dist`s: `:=` 7.93 bits (effective 244 values of 256), `:/` 7.60 (194), kind 6:3:1 1.30 (2.5 of 3). G = 2n KL equals Pearson X2 to 0.005 on the kind counts. Push knob: bin-hit entropy peaks at push 50% (52.7 effective bins), bins per run peak at 70% (45.8), bug exposure is 1.0 from 70% up. I(knob; hit) is 0.76-0.82 bits for `occ14/15_*`, 0.000 for always-hit and never-hit bins; permutation baseline 0.008 | `info-theory/run.out` |

### 2.2 The uniformity measurement in detail (`uniformity/`)

`tb_uniform.sv` declares six classes rewritten from Chapter 7's
`distribution`, `constraint-forms` and `packet-stream` examples and
prints every drawn value; `run.sh` builds it on Verilator 5.052 with
`z3` (z3-solver 5.4.1.0 from the book's venv) on the path and draws
10,000 of each under seed 1, 500 of each under seeds 1-20, and 50,000
of the 16-bit range alone under seed 2 (about 3.6 ms per
`randomize()`; the whole script runs in roughly 8 minutes). Every
`randomize()` returned 1. `uniform.py` applies the tests and runs the
same tests on samples drawn by Python's generator from the asked-for
law, as a control for the test code itself.

| Constraint (10,000 draws, seed 1) | Test | Statistic | p |
|---|---|---|---|
| `v < 16'h8000` | chi-square, 64 buckets | X2 = 77.7, df 63 | 0.10 |
| | KS vs U{0..32767} | D = 0.0159 | 0.013 |
| | 15 bit-balance tests, Bonferroni | raw min 0.031 | 0.46 |
| | serial pairs, 8 x 8 | X2 = 83.6, df 63 | 0.043 |
| `v dist {[0:9]:=1,[10:99]:=1,[100:255]:=2}` | per value, df 255 | X2 = 293.6 | 0.049 |
| | per range | 236 / 2211 / 7553 | 0.76 |
| `v dist {... :/ 1, :/ 1, :/ 2}` | per value | X2 = 284.8 | 0.096 |
| | per range | 2489 / 2559 / 4952 | 0.39 |
| `kind dist {0:/6, 1:/3, 2:/1}` | chi-square | 6076 / 2940 / 984 | 0.30 |
| | consecutive pairs vs product | X2 = 3.8, df 4 | 0.44 |
| `s -> v == 0` (257 solutions) | joint uniform | s = 1 in 38 | 0.081 |
| `s -> v == 0; solve s before v` | P(s = 1) = 1/2 | 0 of 10000 | 0 |

Reading: one run of twelve tests, five p-values between 0.01 and 0.1,
none below the Bonferroni threshold 0.05/12 = 0.004. The suspicion that
cluster raises is what the next two measurements were for: 50,000
draws of the range under another seed (chi-square p = 0.87 at 64
buckets, 0.20 at 256, KS p = 0.56, bits 49.7-50.25%, every 4096-wide
eighth within 2% of expected) and twenty seeds of 500 (8 of 220
p-values below 0.05 against 11 expected; the Python control: 18). On
this release, with this solver, the solver-backed sampler is
indistinguishable from uniform at these sample sizes, `dist` weights
are honored per value and per range, consecutive draws are independent
as far as a pair test sees, and the unconstrained-preference case
(`s -> v == 0`) samples the joint solution set uniformly as the
standard asks. The single rejection is Chapter 7's `solve s before v`
result again, now with a p-value. The 5.050 fix for the opening bug of
Chapter 7 is therefore confirmed by a test with stated power: a bit
bias as large as the one reported before the fix (65-90%) is detected
at 90% power with about 113 draws (M15); this run used 50,000.

Two methodological results for the chapter: (1) the smallest of 15
bit p-values is not a p-value (under the null it is below 0.05 in
about 54% of runs); the first version of `uniform.py` made exactly
that mistake and flagged 11 of 20 seeds before the Bonferroni
correction; (2) a cluster of p-values near 0.05 in one run is what
twelve tests look like, and the response is a second, larger sample,
not a conclusion.

## 3. The mathematics, topic by topic

Notation used throughout (proposed for the chapter): a *test* is one
seeded run of a fixed generator; a *bin* is any event the test can
produce (a coverage bin, a cross cell, a bug's trigger). The generator
and the design together define a per-test hit probability p_i for each
bin i. Everything below is a statement about p, and every statement
holds only for the generator that defined p.

### 3.1 Hit probability: one bin

**Statement.** If each test hits bin i independently with probability
p, the number of tests until the first hit is geometric:
P(not hit in n tests) = (1 - p)^n, the mean wait is 1/p, and the n
needed for a hit with probability 1 - delta is
n >= ln(delta) / ln(1 - p), approximately ln(1/delta)/p for small p.
ln(100) = 4.6, so "99% sure to hit a 1-in-1000 bin" costs about 4600
tests.

**Conditions.** Independent, identically distributed tests (different
seeds of an unchanged generator and design). Holds across *seeds*;
fails across *cycles inside one test* whenever the design has state
(M4, M8): the FIFO's high-occupancy bins are reached by runs of
pushes, so their per-cycle hits cluster within the runs that get there.

**DV application.** The `kind 2` packet at weight 1 in 10: the Ch 7
run of 64 packets misses it with probability 0.9^64 = 0.0012 (M2).
The FIFO bug at 0.236 per seed: 18 seeds for 99% (M7). Per-bin
reasoning is also the right first question for a cross: a cell of
`op_x_full` whose marginals are each 1-in-10 is 1-in-100 only if the
two are independent, which in the FIFO they are not (`push_x_full`
is far likelier than the product under a push-heavy mix).

**Where it breaks.** (a) p is unknown; it is what the bounds of 3.3
estimate. (b) Tests are not identically distributed when the generator
changes between regressions (a constraint edit, a new sequence library,
an ML-steered regression) or when the design changes (every RTL drop
redefines p). (c) Within a test, stateful designs make hits bursty;
the unit of independence is the seed, not the cycle or the transaction.

### 3.2 Coupon collector: every bin

**Statement, equal probabilities.** With k bins each hit with
probability 1/k per draw, the number of draws T until all are hit has
E[T] = k H_k = k (1 + 1/2 + ... + 1/k), approximately k ln k + 0.577 k.
Erdős and Rényi's limit law: P(T < k ln k + c k) -> exp(-e^{-c}) as
k -> infinity [Erdős and Rényi 1961, 2026-11-16](https://static.renyi.hu/~p_erdos/1961-09.pdf).
So the spread around k ln k is of order k: for 99%, c = -ln(-ln 0.99)
= 4.6 and T99 is about k ln k + 4.6 k.

**Statement, unequal probabilities.** With per-draw probabilities
p_1..p_k (sum 1),
E[T] = integral_0^inf (1 - prod_i (1 - e^{-p_i t})) dt
(Flajolet, Gardy and Thimonier 1992, Discrete Applied Mathematics
39(3):207-229; the formula as reproduced and attributed in
[du Boisberranger, Gardy and Ponty, 2026-11-16](https://arxiv.org/pdf/1202.0920.pdf);
the original was not opened, see confidence notes). The integrand is
the Poissonization: if draws arrive as a Poisson process of rate 1,
bins fill independently, and P(all hit by time t) = prod(1 - e^{-p_i t})
exactly. For a fixed number n of draws the product is an
approximation, slightly pessimistic in M1-M3 (54 vs exact 51 for
k = 8; 47 vs 44 for the packet). The exact CDF is the inclusion-
exclusion sum P(T <= n) = sum_{S} (-1)^{|S|} (1 - p(S))^n, usable for
up to about 20 bins (M2).

**The usable bound.** For a design review, the union bound is the
statement with no approximation in it: P(some bin missed after n draws)
<= sum_i (1 - p_i)^n, so n >= max_i ln(k/delta)/(-ln(1 - p_i))
guarantees all k bins with probability >= 1 - delta. It depends on the
rarest bin almost alone. Measured: for equal probabilities it equals
the exact 99% point at k = 8 (51) and is within 1% of the Poissonized
point at k = 64 and 256; for the skewed `dist` cases it is 7-25% above
(packet 55 vs exact 44, `:=` 4177 vs 3793, `:/` 3650 vs 3399); for the
FIFO's correlated bins, 44 seeds against 27 measured (M1-M4). It never
under-states, so the chapter can teach it as *the* safe answer to "how
many seeds until every bin is hit with 99% probability", with the
integral for the mean.

**The rarest bin dominates.** For the 8-bit `v` under Ch 7's `:=`
{1,1,2} weights the slowest values have probability 1/412 instead of
1/256, and E[T] rises from 1568 to 2143 (M3). For the FIFO grid the
rarest bins (`occ15_*`, 0.18-0.22 per seed) set the number of seeds;
the 60 other bins are irrelevant to it. This is the quantitative form
of the closure folklore that "the last few bins take most of the time".

**DV application.** (1) Sizing a regression: from a few hundred seeds,
estimate each bin's per-seed hit rate pi_i (fraction of seeds that hit
it), then n99 = max_i ln(k/0.01)/(-ln(1 - pi_i)). For the FIFO: 44
seeds by union bound, 29 by the independent-bins product, 27 measured
(M4). (2) Weighting: the formula says how much a `dist` weight on a rare
value buys. (3) Crosses: k is the product of the coverpoint sizes and
the cell probabilities are joint, not products of marginals.

**Where it breaks.** (a) Bins are not independent of each other: the
four `occ15_*` bins are hit together or not at all (positively
correlated), which makes the independent-bins product pessimistic for
the median (11 vs measured 6) but close at the 99th percentile (29 vs
27); the union bound is valid regardless of dependence. (b) The draw
is the seed, not the cycle: the cycle-level i.i.d. model, fed with
true per-cycle rates, predicts 4.5 seeds for 99% where 27 are needed
(M4), because cycles inside one run are a Markov chain, not
independent draws. This is the single most important measured result
for the chapter: *a coupon-collector argument over cycles or
transactions is wrong for a stateful design; over seeds it is right.*
(c) Unreachable bins make T infinite; the formulas presuppose p_i > 0
for every bin in the denominator, which is what Ch 8's exclusion
review establishes. (d) A bin with p_i = 0 under this generator but
reachable in the design (push 30%: `occ15`) also makes T infinite,
and only a different generator fixes it.

Peer-reviewed: Erdős and Rényi 1961 (opened); Flajolet, Gardy and
Thimonier 1992 (formula verified through a secondary, original not
opened). Vendor: none.

### 3.3 Bounds after N clean seeds

**Statement.** After n independent tests with zero failures, the exact
one-sided 1 - alpha upper confidence bound on the per-test failure
probability p is p_U = 1 - alpha^{1/n} (Clopper-Pearson with x = 0).
Since -ln(0.05) = 3.0, p_U is approximately 3/n at 95%: the *rule of
three* (Hanley and Lippman-Hand 1983, JAMA 249(13):1743-1745,
[scilit record, 2026-11-16](https://scilit.net/publications/ddfc523d905fccaecb8488227831d6ec);
the rule as restated in [Newman 1995, JAMA letter, 2026-11-16](https://jamanetwork.com/journals/jama/article-abstract/389714)).
At 99%, 4.6/n. For x failures the Clopper-Pearson bounds solve
P(X <= x | p_U) = alpha and P(X >= x | p_L) = alpha
(Clopper and Pearson 1934, Biometrika 26(4):404-413,
DOI 10.2307/2331986, [scilit record, 2026-11-16](https://www.scilit.net/publications/db65b7b21348fddd8a4297389dc98cf3);
text not opened). Coverage is at least 1 - alpha for every p
(conservative), confirmed in M6.

A Bayesian alternative with a uniform prior gives a posterior
Beta(1, n + 1) and upper 95% quantile 1 - 0.05^{1/(n+1)}; Jeffreys'
prior gives a smaller bound. All four agree to two significant figures
from n = 300 (M5). The chapter needs only the exact bound and the rule.
Miller et al. derive failure-probability estimates for the zero-failure
case with Bayesian priors and explicitly for non-uniform input
distributions [Miller et al. 1992, NASA NTRS record, 2026-11-16](https://ntrs.nasa.gov/citations/19920043306)
(IEEE TSE 18(1), DOI 10.1109/32.120314; text not opened).

**The scale argument.** To claim p <= 1e-6 per test at 95% takes about
three million clean tests (M5). Butler and Finelli make the same
argument for life-critical software: demonstrating a 1e-9 failure
probability for a 10-hour mission by life testing takes on the order
of a million years with one test specimen, "114 years" even with
10,000, and reliability-growth models do not escape it
[Butler and Finelli, NASA preprint, 2026-11-16](https://ntrs.nasa.gov/api/citations/20040139817/downloads/20040139817.pdf).
Littlewood and Strigini's CACM paper is on the same limit
[Littlewood and Strigini 1993, City Research Online, 2026-11-16](https://openaccess.city.ac.uk/id/eprint/1251/)
(metadata opened; body not read, so not cited for content).

**DV application.** "After 2000 clean nightly seeds, the per-seed
failure probability *under this generator* is below 0.0015 at 95%."
That is a true and useful statement for a release note, and the
chapter should teach the sentence with its qualifier. With x > 0 (a
known, unfixed, intermittent bug), the CP interval on the bug's
per-seed rate is what triage needs: the FIFO bug's rate is
[0.210, 0.264] at 95% from 1000 seeds (M7), and an exact Markov chain
of the FIFO gives 0.2421, inside it, which is the chapter's check that
the formula and the simulator agree.

**Where it breaks.** (a) **The bound is about the generator, not the
design** (Q7). Under push 30% the FIFO bug's true per-seed probability
is 0.00004; 250 clean seeds bound it by 0.012, which is correct and
says nothing about the bug (M7). Miller et al.'s and Musa's term for
the missing ingredient is the input distribution or operational
profile; for DV it is "the generator's distribution over the design's
state space". (b) Seeds must be independent and the design unchanged;
a bound accumulated across RTL drops is not a bound on the current RTL.
(c) Clean means "no checker fired"; the bound inherits every hole in
the checkers (Ch 8's "a covered bin is not a checked bin"). (d) A
failing seed's length matters: per-cycle hazard is not constant (M8:
no exposure before cycle 40), so a per-seed bound does not convert to a
per-cycle bound by dividing by cycles.

Peer-reviewed: Clopper and Pearson 1934, Hanley and Lippman-Hand 1983,
Miller et al. 1992, Butler and Finelli 1993 (preprint opened),
Littlewood and Strigini 1993. Vendor: none.

### 3.4 Uniformity and goodness of fit

**Statement, Pearson chi-square.** For counts O_j in m cells with
expected E_j = n q_j under a hypothesized law q, X2 = sum (O_j - E_j)^2
/ E_j is asymptotically chi-square with m - 1 degrees of freedom when
q is fully specified (Pearson 1900, Philosophical Magazine 50(302):
157-175, [scilit record, 2026-11-16](https://scilit.com/publications/85336553a134b10c9229ce4db8ba0081);
text not opened). The usual working condition is expected counts of
at least about 5 per cell (textbook rule; source not opened, see
confidence notes). The G statistic 2 sum O_j ln(O_j/E_j) = 2 n KL(emp ||
q) (in nats) has the same limit; on the packet counts they agree to
0.005 (M14), which is the bridge to section 3.7.

**Statement, Kolmogorov-Smirnov.** D_n = sup |F_n(x) - F(x)|; for a
continuous F, P(sqrt(n) D_n > lambda) -> 2 sum_{k>=1} (-1)^{k-1}
e^{-2 k^2 lambda^2}. The approach to the limit is "rather slow" and the
exact distribution is computable [Marsaglia, Tsang and Wang 2003, JSS
8(18), 2026-11-16](https://www.jstatsoft.org/article/view/v008i18).
For a discrete law (every constrained integer) the continuous p-value
is conservative; the experiments use Stephens' small-n correction
(sqrt(n) + 0.12 + 0.11/sqrt(n)), as in Numerical Recipes (not opened
for this note; see confidence notes).

**Which test for which constraint.** Chi-square on the cells the
constraint names (each value of a small `dist`, each range of a
`dist`, each solution of a small joint constraint); KS for a wide
integer range where binning would throw away resolution; per-bit
binomial tests for the specific defect Ch 7's opening bug had (low bits
stuck); a serial-pair chi-square for independence between consecutive
draws. Sample size: to see a bit set with probability 0.55 instead of
0.5 with 90% power takes about 1050 draws; 0.65 takes about 115; 0.51
takes about 26,000 (section 2.2 table, by formula and by simulation).
The pre-fix bug in Ch 7 (65-90% set) would have been caught by a
100-draw test; a near-uniform sampler's residual skew would not.

**Multiple testing.** Twenty tests at 0.05 reject one on average when
every null holds; a test suite over many coverpoints needs a
Bonferroni or similar correction or it will "find" non-uniformity
every night (section 2.2: control samples from Python's generator).

**DV application.** M9 applies the tests to six constraint shapes on
Verilator 5.052 with z3 (results in section 2.2). The design lesson
for the chapter: a `dist` is a hypothesis with a fully specified q, so
it is testable for free from the histogram Ch 7 already prints; the
test turns "the counts look about right" into a p-value with a stated
power.

**Where it breaks.** (a) Draws must be independent for the chi-square
law to hold; a generator with memory (`randc`, a solver that returns
neighboring models) violates it, and the serial-pair test is the check.
(b) The hypothesis must be the right one: for `s -> v == 0` without
`solve before`, the standard's uniform-over-solutions law gives
P(s = 1) = 1/257, not 1/2, and the test must be against the former
(M9 confirms the tool samples it). (c) A non-rejection is not a proof
of uniformity: power is everything, and a near-uniform sampler (UniGen2
gives almost-uniform guarantees within a tolerance
[Chakraborty et al. 2015, refs.bib `chakraborty2015unigen2`]) can be
skewed by less than the test can see at feasible n. (d) Across seeds:
the test checks one seed's stream; a regression wants the mixture over
seeds, which is a different (and usually better behaved) distribution.

Peer-reviewed: Pearson 1900 (record only), Marsaglia, Tsang and Wang
2003 (opened). Vendor: none.

### 3.5 t-way combinatorial coverage and covering arrays

**Definitions.** A covering array CA(N; t, k, v) is an N x k array over
v symbols in which, for every choice of t columns, all v^t t-tuples
appear in some row; CAN(t, k, v) is the smallest such N; mixed-level
arrays allow a different v per column [NIST covering arrays page,
2026-11-16](https://math.nist.gov/coveringarrays/coveringarray.html).
NIST archives best-known arrays; Colbourn maintains the best-known
sizes for t = 2..6 [Colbourn tables, 2026-11-16](https://www.public.asu.edu/~ccolbou/src/tabby/catable.html)
(the page opened; the table values did not render for the fetch tool
and direct download is blocked from this environment).

**Known bounds and constructions.**
- Trivial lower bound: N >= product of the t largest level counts
  (v^t for uniform arrays).
- Binary, t = 2, exact: CAN(2, k, 2) is the least N with
  k <= C(N - 1, ceil(N/2)) (Katona 1973; Kleitman and Spencer 1973,
  Discrete Mathematics 6(3):255-262, DOI 10.1016/0012-365X(73)90098-8,
  [scilit record, 2026-11-16](https://scilit.com/publications/c32d0f2256284da93f17fc1fc85aa6f9)),
  as stated in [Hiess and Kampel 2025, arXiv:2510.17596, 2026-11-16](https://arxiv.org/html/2510.17596v1),
  which also states CAN(2, 13, 3) = 15 (a computational result it
  attributes to Izquierdo-Marquez and Torres-Jimenez) and
  CAN(3, k, 2) <= 17 for k <= 16 (Sloane). The construction is
  constructive and short: row 0 all zeros, columns are distinct
  ceil(N/2)-subsets of the other N - 1 rows; covering-array/covering.py
  builds it and checks it (6 rows for 10 binary parameters, 10 rows for
  126).
- Orthogonal arrays give optimal strength-2 arrays when v is a prime
  power and k <= v + 1: (a, b, a+b, a+2b) mod 3 is a 9-row CA for 3^4,
  optimal by the v^2 bound (checked in the script).
- Growth: for fixed t and v, the number of tests grows with v^t times a
  logarithm of the number of parameters; NIST states the scaling in
  SP 800-142 [Kuhn, Kacker and Lei 2010, 2026-11-16](https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-142.pdf).
- Greedy algorithms: AETG builds one row at a time, each the best of
  several randomized greedy candidates (Cohen, Dalal, Fredman and
  Patton, IEEE TSE 23(7):437-444, 1997, [researchr record,
  2026-11-16](https://researchr.org/publication/CohenDFP97); abstract
  not available there, the algorithm description in the note is the
  well-known one and the script is written from it, see confidence
  notes); IPOG grows the array parameter by parameter (horizontal) and
  then adds rows (vertical), generalizing IPO from t = 2 to any t
  [Lei, Kacker, Kuhn, Okun and Lawrence, ECBS 2007, pp. 549-556,
  DOI 10.1109/ECBS.2007.47, 2026-11-16](https://csrc.nist.gov/pubs/conference/2007/03/29/ipog-a-general-strategy-for-tway-software-testing/final);
  NIST's ACTS tool implements IPOG-family algorithms and supports
  constraints that exclude invalid combinations (SP 800-142).

**Why t is small: the interaction rule.** Kuhn, Wallace and Gallo
report from fault data in several domains that faults are triggered by
interactions of few parameters, and argue that testing all t-tuples
for the largest t observed is "pseudo-exhaustive" [Kuhn, Wallace and
Gallo, IEEE TSE 30(6):418-421, 2004, DOI 10.1109/TSE.2004.24,
2026-11-16](https://csrc.nist.gov/pubs/journal/2004/06/software-fault-interactions-and-implications-for-s/final)
(abstract opened; the per-system percentages are in the paper body,
which did not load, so no percentage is cited here). SP 800-142
restates the empirical rule ("most failures are triggered by a single
parameter value or interactions between a relatively small number of
parameters") and says 4- to 6-way combinations detected nearly all
failures in the data studied. These are software data; the chapter
must say no comparable study of RTL bugs by interaction strength was
found (confidence notes).

**Random tests against covering arrays.** For uniform random tests the
expected fraction of t-tuples covered after n tests is the mean over
tuples of 1 - (1 - 1/m)^n, m the product of the levels in the tuple
(exact; M11 matches it to 0.01-0.04), and the union bound gives the
n for full coverage with probability 1 - delta. Measured (M10): random
needs 2.0-4.2 times as many tests as the greedy array for full t-way
coverage; NIST's SP 800-142 tables report averages of about 3.9 (2-way),
3.8 (3-way) and 3.2 (4-way) and note that a random set of the same size
as a covering array already covers most tuples (10 random binary tests,
about 89% of pairs). Arcuri and Briand prove that random testing's
interaction-fault detection approaches combinatorial testing's as the
number of features grows, may beat it when generating the array is
costly, and can be arbitrarily worse under constraints [Arcuri and
Briand, IEEE TSE 38(5):1088-1099, 2012, 2026-11-16](https://orbilu.uni.lu/handle/10993/1190).
M11 shows the shape: random reaches 82% of the mixed space's pairs at
16 tests and 97% at 32, then spends as many again on the last 3%,
which is the coupon collector of 3.2 over tuples.

**DV application.** Configuration and mode spaces are where t-way
designs apply directly: register-programmed modes of a DMA or bus
bridge, CSR combinations, compile-time parameters of an IP, test-knob
plusargs. The measurement uses a DMA-style space of ten knobs (burst
length 4 values, size 3, alignment 2, direction 3, channel 2,
priority 2, interrupt enable 2, FIFO threshold 4, error injection 3,
back-pressure 3; 20,736 combinations): 18 tests give every pair, 72
every triple. The chapter's honest framing: a covering array makes
*configuration* coverage deterministic and small; constrained-random
stimulus *within* each configuration is still needed, and the cross
coverage of Ch 8 measures the same tuples after the fact. A
`covergroup` cross over the ten knobs at t = 2 is 45 crosses and 350
cells, which is the denominator a pairwise array closes by
construction.

**Where it breaks.** (a) Constraints between parameters (illegal
combinations) change everything: random sampling from a constrained
space is non-uniform over tuples, and Arcuri and Briand's
"arbitrarily worse" result applies; covering-array tools must take the
constraints (ACTS does). (b) Parameters with many values (addresses,
lengths) need equivalence classes first; t-way coverage over classes
is only as good as the partition. (c) Sequential behavior: a covering
array covers combinations of static settings, not orders of events;
sequence covering arrays exist (NIST has worked on them; not opened for
this note) and are the bridge to the graphs chapter. (d) The
interaction rule is an empirical regularity from software, not a
theorem.

Peer-reviewed: Kuhn, Wallace and Gallo 2004 (abstract); Cohen et al.
1997 (metadata); Lei et al. 2007 (abstract); Kleitman and Spencer 1973
(metadata, formula via Hiess and Kampel); Arcuri and Briand 2012
(abstract); Hiess and Kampel 2025 (preprint, opened). Government
technical report: NIST SP 800-142 (opened). Vendor: none.

### 3.6 Estimating unseen coverage: species estimation

**The analogy.** Ecology estimates how many species exist from how
often each observed species was seen; software testing borrowed it.
Böhme's STADS maps a fuzzer's generated inputs to individuals and a
behavioral class (a path, a covered statement, an exposed
vulnerability type) to a species, and imports the estimators with
their assumptions [Böhme, "STADS: Software Testing as Species
Discovery", ACM TOSEM 27(2), 2018, DOI 10.1145/3210309; arXiv
1803.02130 read, 2026-11-16](https://arxiv.org/pdf/1803.02130). For
DV, a species is a coverage bin; an individual is a test (incidence
data: one test hits many bins) or a sampled cycle (abundance data).

**Good-Turing.** With n draws and f1 bins seen exactly once, the
probability that the next draw hits a never-seen bin (the *missing
mass*, or STADS's *discovery probability*) is estimated by f1/n; the
sample coverage is 1 - f1/n. Good credits the formula to Turing
("first suggested to me ... by Dr A. M. Turing") [Good 1953,
Biometrika 40, 2026-11-16](https://gwern.net/doc/statistics/order/capture/1953-good-2.pdf).
M12 confirms it is unbiased for the missing mass on a known 200-bin
space (0.2305 vs 0.2309).

**Chao1 and Chao2.** Chao1 (Chao 1984, Scandinavian Journal of
Statistics 11, not opened) estimates the number of bins:
S_obs + ((n-1)/n) f1^2/(2 f2), with f1(f1-1)/2 in place of f1^2/(2f2)
when f2 = 0, as STADS writes it. Chao2 is the incidence form, with Q1
and Q2 the bins seen in exactly one and two sampling units out of T:
S_obs + ((T-1)/T) Q1^2/(2 Q2). Both come from a Cauchy-Schwarz
inequality and are **lower bounds**, nearly unbiased only when the
rarest bins have roughly equal detection probabilities; Chao2 assumes
independent sampling units with constant per-bin detection
probability [Chao and Colwell 2017, SORT 41(1):3-54,
2026-11-16](https://gwern.net/doc/statistics/order/capture/2017-chao.pdf).
The same source gives the extrapolation S(T + t) = S_obs + Q0_hat
[1 - (1 - Q1/(T Q0_hat + Q1))^t], the prediction of how many new bins
t more units will show (abundance form after Shen, Chao and Lin 2003,
Ecology 84:798-804, as cited in [Chao et al. 2009, Ecology 90(4),
2026-11-16](https://www.uvm.edu/~ngotelli/manuscriptpdfs/ChaoEcology2009.pdf)).

**Which unit for DV.** The measurement's main result (M13): the seed
is the sampling unit, so Chao2 over seeds is the right estimator; Chao1
over cycle counts treats 200 dependent cycles as 200 independent draws
and is wrong in the same way as the cycle-level coupon model. Under
the 50/50 mix Chao2's median reached the true 64 at 4 seeds, when 58.5
bins had been seen, and the one-more-seed prediction tracked the
measured number of new bins (1.56 vs 1.95 at 4 seeds; 0.37 vs 0.40 at
8). Chao1 on cycles stayed close to S_obs throughout (60.7 at 4 seeds)
because the bins are seen many times per run, so f1 is small and the
estimator sees no evidence of unseen bins.

**The residual-risk result.** Böhme, Liyanage and Wüstholz show that
for greybox (adaptive) fuzzing the discovery probability is an upper
bound on residual risk but that estimators built for blackbox
(non-adaptive) sampling "systematically and substantially
under-estimate the true risk", because adaptive bias makes discovery
probabilities increase over time [Böhme, Liyanage and Wüstholz,
ESEC/FSE 2021, DOI 10.1145/3468264.3468570, 2026-11-16](https://2021.esec-fse.org/details/fse-2021-papers/39/Estimating-Residual-Risk-in-Greybox-Fuzzing)
(abstract read). Liyanage, Böhme, Tantithamthavorn and Lipp evaluate
seven incidence-based richness estimators (Chao2, bias-corrected
Chao2, iChao2, ICE, ICE-1, jackknife 1 and 2) for "reachable coverage"
of fuzzers: on programs with known ground truth the jackknives had the
lowest bias and variance, most estimators were within about 15% after a
burn-in, and on real programs all estimators predicted maxima that
further fuzzing exceeded, i.e. they behaved as lower bounds
[Liyanage et al., ICSE 2023, 2026-11-16](https://mpi-softsec.github.io/papers/ICSE23-effectiveness.pdf).
Böhme's roadmap paper states the IID condition and points to
Horvitz-Thompson-style corrections as open work [Böhme, "Assurance in
Software Testing: A Roadmap", arXiv 1807.10255, 2026-11-16](https://ar5iv.arxiv.org/html/1807.10255).

**DV application.** (1) A covergroup with a known bin list still has
an *unknown reachable count* under a given generator; Chao2 over seeds
estimates it, and the gap between the estimate and the plan's bin count
is the set of bins this generator will not hit without a new test
(M13, push 30%: 14 of 64 never seen in 250 seeds, all the high-
occupancy cells). (2) For open-ended coverage spaces (unique
instruction sequences, transaction-order signatures, FSM paths, toggle
patterns, or a fuzzer's edge coverage on a Verilator model) there is
no bin list, and species estimation is the only way to talk about the
denominator. (3) Good-Turing over seeds answers "what is the chance the
next nightly seed adds anything", the stopping question.

**Where it breaks.** (a) The estimate is about the generator's
reachable set, never the design's (M13: 64 reachable bins, 68 in the
plan; 50 seen under push 30%). (b) Rare-bin heterogeneity makes Chao
estimators lower bounds and unstable: under push 30% Chao2's mean over
resamples overshot (69 at 128 seeds) while its median was 59, with
individual estimates ranging widely, because Q2 was 2-4. (c) A small
discovery probability does not mean few unseen bins: under push 30% the
next seed showed a new bin 0.5% of the time while 14 bins (22%) had
never been seen. Discovery probability is a mass, and rare bins carry
little mass. (d) Adaptive generation (coverage-driven test selection,
ML-steered regressions, fuzzers) violates the constant-probability
assumption, in the direction Böhme et al. measured (underestimated
risk). (e) Changing RTL or constraints resets the sample.

Peer-reviewed: Good 1953 (opened), Böhme 2018 TOSEM (preprint opened),
Böhme, Liyanage and Wüstholz 2021 (abstract), Liyanage et al. 2023
(paper opened), Chao and Colwell 2017 (opened), Chao et al. 2009
(opened), Chao 1984 and Shen, Chao and Lin 2003 (not opened; cited
through the two Chao papers). Preprint: Böhme roadmap 2018. Vendor:
none.

### 3.7 Information theory as a tool for stimulus quality

**Statements.** Shannon entropy H(p) = -sum p_i log2 p_i is at most
log2 k, with equality exactly when all p_i are equal ("H is a maximum
and equal to log n when all the p_i are equal") [Shannon 1948, Bell
System Technical Journal 27, 2026-11-16](https://people.csail.mit.edu/dmoshkov/courses/codes/shannon1948.pdf).
2^H is the *effective number of bins*: a distribution with entropy H
spreads its draws like a uniform one over 2^H bins. KL divergence
D(p || q) = sum p_i log(p_i/q_i) >= 0 measures how far a measured
stimulus histogram p is from an intended q; 2 n D (in nats) is the G
statistic of 3.4 (M14). Mutual information I(X; Y) = H(Y) - H(Y | X)
measures how much knowing a stimulus knob X tells about a coverage
outcome Y.

**DV uses, measured (M14).**
1. *Entropy as a uniformity score for a constraint.* The `:=` dist of
   Ch 7 has 2^H = 244 effective values out of 256, the `:/` dist 194,
   the packet mix 2.5 of 3. One number per coverpoint, comparable
   across releases, cheap to compute from the histogram Ch 7 already
   prints. Caveat: the plug-in estimate is biased low on small samples
   (M14: 6.25 bits from 100 draws for a true 7.93; the Miller-Madow
   correction (k - 1)/(2n) recovers most of it from 1000 draws).
2. *Entropy over bins as a regression score.* For the FIFO knob sweep
   the bin-hit entropy peaks at push 50% (52.7 effective bins of 64),
   while bins hit per run peak at 70% (45.8) and the bug is exposed
   in every run from 70% up. Entropy, coverage and bug exposure rank
   the same four generators three different ways, which is the
   chapter's point: maximizing spread is not maximizing coverage of
   the hard bins, and neither is checking.
3. *Mutual information as knob attribution.* I(push%; bin hit) is
   0.76-0.82 bits for the occupancy-14/15 cells and 0.00 for cells
   every generator hits or none can; a permutation baseline is 0.008.
   It ranks which knob moves which bin without a model, which is the
   question coverage-directed generation asks (refs.bib `fine2003cdg`,
   `ioannides2012cdg`; text not consulted).
4. *Entropic.* Böhme, Manès and Cha define a fuzzer's efficiency in
   terms of the entropy of the species (coverage features) its inputs
   exercise ("Intuitively, efficient fuzzers maximize information"),
   estimate each seed's local entropy with a Laplace-smoothed
   estimator over rare features, and schedule seeds by it; Entropic in
   LibFuzzer covered more than LibFuzzer on about 77% of 263 OSS-Fuzz
   subjects in their evaluation [Böhme, Manès and Cha, ESEC/FSE 2020,
   DOI 10.1145/3368089.3409748, 2026-11-16](https://softsec.kaist.ac.kr/%7Esangkilc/papers/bohme-fse20.pdf).
   This is the hand-off to the fuzzing chapter.

**Where it breaks.** Entropy ignores which bins matter: a generator can
raise entropy by spreading over easy bins. KL needs a target q, and
for most coverpoints the target is "every bin at least once", which
is a coupon-collector objective, not a distribution. Mutual
information from a handful of knob settings is a plug-in estimate with
upward bias on small samples (hence the permutation baseline). And
none of it measures checking.

Peer-reviewed: Shannon 1948 (opened), Böhme, Manès and Cha 2020
(opened). Miller-Madow correction: Miller 1955 (not opened; formula is
textbook, see confidence notes). Vendor: none.

## 4. Closure prediction and reliability growth: the directly relevant literature

**Bug-discovery curves in hardware (peer-reviewed, IBM).** Malka and
Ziv fit software reliability-growth models to the daily bug counts and
cumulative passing random-simulation cycles of two superscalar PowerPC
projects (719 bugs over about 68,052 million cycles; 236 bugs over
about 2,383 million cycles; bugs found by formal or inspection
excluded). They used the Laplace trend test for reliability growth,
Goel-Okumoto, Duane and Musa-Okumoto models, and the KS test for fit.
For processor A, Musa-Okumoto predicted about 790 total bugs three
months ahead, against 794 actual, and MTTF within 6.7%; for processor
B, Goel-Okumoto fit best, and only after discarding the data before a
mid-project feature addition. Their own caveat: "Unfortunately, no one
model is clearly better than the other models", and predictions apply
to the test environment, not field operation [Malka and Ziv, DAC 1998,
2026-11-16](https://www.cs.york.ac.uk/rts/docs/SIGDA-Compendium-1994-2004/papers/1998/dac98/pdffiles/39_2.pdf).
This is the one primary DV source found that applies the statistics of
this chapter to a real verification project, and the chapter should
carry it (dated, with its caveats) as the In Practice for reliability
growth.

**The NHPP model.** Goel and Okumoto model software failures as a
non-homogeneous Poisson process with an exponentially saturating mean
value function m(t) = a(1 - e^{-bt}) (a the eventual total number of
faults); IEEE Transactions on Reliability R-28(3):206-211, 1979,
DOI 10.1109/TR.1979.5220566 [scilit record, 2026-11-16](https://scilit.com/publications/a0ef8d84616bdb7c34ba257dbd33ef3a)
(abstract only; the mean-value form is the well-known one and should be
checked against the paper before the chapter prints it). Its assumption
set is the same as this chapter's: a stationary test process and
independent detections; Malka and Ziv's processor B shows the
assumption failing when the design changes.

**Efficiency of random testing.** Böhme and Paul analyze random testing
(cost 1 per test) against a systematic strategy (cost c per test, one
test per error-revealing partition): the systematic strategy beats
random only if c is below a bound that depends mainly on the target
confidence (about 4x for 90%, about 37x for 99% in their example),
random's rate of progress decays exponentially, and a hybrid that
switches from random to systematic does as well as the better of the
two [Böhme and Paul, IEEE TSE 2016 (accepted version, DOI
10.1109/TSE.2015.2487274), 2026-11-16](https://mboehme.github.io/paper/TSE15.pdf).
For DV this is the quantitative form of "random first, directed for
the holes": it says when the switch pays, under stated assumptions.

**Species estimation and residual risk in fuzzing.** Section 3.6:
Böhme 2018 (STADS), Böhme, Liyanage and Wüstholz 2021, Liyanage et al.
2023, Böhme, Manès and Cha 2020. Their lesson for coverage closure: the
estimators work for non-adaptive sampling, are lower bounds, and are
biased toward optimism under adaptive generation.

**Coverage holes as structure.** Lachish, Marcus, Ur and Ziv, "Hole
analysis for functional coverage data", DAC 2002, pp. 807-812, DOI
10.1145/513918.514119 ([researchr record, 2026-11-16](https://researchr.org/publication/LachishMUZ02/bibtex);
text not opened) is the IBM work on grouping uncovered cross-product
cells into large holes; it belongs in Further Reading for the cross
section, not as a cited claim until read.

**ML-steered closure (vendor co-authored).** Kwon et al. (Samsung with
Cadence) report a closure flow that learns from regression traces which
target scenarios are satisfied and how hard the rest are, then builds
steered regressions: 100% of about 120,000 bins in 8,362 CPU hours
versus 96.27% after 41,158 CPU hours of repeated original regressions
(4.92x), and an 18.2x figure on a 5,850-bin category; the tool and
simulator are the vendor's [Kwon et al., "Functional Coverage Closure
in SoC Interconnect Verification with Iterative Machine Learning",
DVCon proceedings, 2026-11-16](https://dvcon-proceedings.org/wp-content/uploads/1096.pdf)
**[vendor co-authored; venue year not stated in the text]**. Its
relevance here is negative: a steered regression is adaptive, so every
estimator of 3.2-3.6 loses its constant-probability assumption on it.
The same holds for VSO.ai-style regression optimization, whose vendor
claims are catalogued with labels in `research/agentic-dv-tools-synopsys.md`
section 2 (not re-cited here).

**Leads not opened (do not cite until read).** Musa, "Operational
profiles in software-reliability engineering", IEEE Software 1993;
Littlewood and Strigini 1993 body text; Duran and Ntafos, "An
evaluation of random testing", IEEE TSE 1984; Hamlet, "Probable
correctness theory", 1987; Chao 1984 and 1987; Shen, Chao and Lin
2003; Wagner, Bertacco and Austin on Markov-model stimulus for
processors; NIST work on sequence covering arrays; IEEE 1633
(recommended practice on software reliability) which surfaced in a
search.

## 5. Proposed worked-example spine

**One design, one covergroup, one bug: the Chapter 1 FIFO under the
Chapter 8 coverage model.** Files the chapter would reuse by path:
`examples/ch01-what-is-dv/rtl/fifo.sv` (the DUT, full asserted at 15
entries), `examples/ch08-functional-coverage/fifo-coverage/tb_fifo_cov.sv`
(driver, monitor, `fifo_cg` and `fill_cg`, the `+bias` knob) and its
runner `run_fifo_cov.sh` (the `.dat` bin reader). The research
logger `research/ch21-measurements/fifo-log/tb_fifo_log.sv` shows the
per-seed form the chapter's examples need; the chapter's own examples
should instead run `tb_fifo_cov.sv` itself under many seeds and read
`fifo_cg`'s bins from the per-seed `.dat` files, so that the bins in
the chapter are Chapter 8's bins (the outline must budget the run
time: about 13 s per 1000 seeds of 200 cycles for the logger; the
covergroup build adds a `.dat` per seed).

Why this spine: it is already familiar to the reader; its bins have
strongly unequal probabilities under the even mix (the coupon formulas
with unequal p are needed); it is stateful, so it shows the
seed-versus-cycle independence failure that is the chapter's most
important measured result; it has one known bug with a per-seed
exposure probability that an exact Markov chain can compute (so the
chapter can check simulation against mathematics, as Chapter 18 checks
its engines against explicit-state search); it has an unreachable bin
(`full_16`, Chapter 8's exclusion) that the estimators must not
"predict"; and it has a single knob (`+bias`, generalized to push and
pop percentages) that moves the hard bins, which carries the
information-theory section.

| Chapter section | What the FIFO carries | Measured basis |
|---|---|---|
| Hit probability | P(`almost` bin in a 200-cycle seed) and P(bug exposed) = 0.236; the Markov chain gives 0.2421 | M4, M7 |
| Coupon collector | seeds to close `fifo_cg` with 99%: union bound vs measured; the cycle-level model's 6x error | M4 |
| Bounds after clean seeds | the *fixed* FIFO under 50/50 for N clean seeds gives "p <= 3/N"; the same N under push 30% bounds a bug the generator cannot reach (true p = 4e-5) | M5, M7 |
| Uniformity | side specimens from Chapter 7: `rand_packet.sv` kind mix and `tb_distribution.sv` shapes; the FIFO's own `$urandom_range` driver could be tested too | M9, M15 |
| t-way | the FIFO has too few knobs; use Chapter 11's DMA transfer space (`examples/ch11-architecture-to-verification/tb/dma_tb_pkg.sv`: `len_cp` 6 bins, `out_cp` 3, `pos_cp` 3, `style_cp` 4, plus channel 2), whose exclusions (`over` v1-only, zero-length errors, `pos` only when `out` != ok) are exactly the constraints that make random tuple coverage non-uniform | M10, M11 (on a DMA-style space; the Ch 11 space itself not yet measured) |
| Unseen coverage | Chao2 over seeds on `fifo_cg` crosses, 50/50 vs push 30%; discovery probability 0.5% with 22% of bins unseen | M12, M13 |
| Information theory | entropy and MI across the push knob; entropy, coverage and bug exposure rank the mixes differently | M14 |

A second, smaller spine is possible for uniformity alone (Chapter 7's
packet stream), and the outline should decide whether that section
leaves the FIFO (Q2).

## 6. Bibliography (BibTeX-ready)

Keys already in `refs.bib` to reuse: `chakraborty2015unigen2`,
`kitchen2007stimulus`, `fine2003cdg`, `ioannides2012cdg`,
`piziali2004coverage`, `tasiran2001coverage`, `verilator-issue-7563`,
`verilator-pr-7684`, `verilator-pr8042`, `verilator-issue-8024`,
`verilator-changes`, `ieee1800-2023`, `opentitan-dv-methodology`,
`cocotb-coverage`. None of the entries below exists in `refs.bib`
(checked by key and author surname). Entries with a DOI carry no URL
or access date (house rule); `note` says what was actually read.

```bibtex
@article{erdos1961coupon,
  author  = {Erd{\H{o}}s, Paul and R{\'e}nyi, Alfr{\'e}d},
  title   = {On a Classical Problem of Probability Theory},
  journal = {Magyar Tudom{\'a}nyos Akad{\'e}mia Matematikai Kutat{\'o}
             Int{\'e}zet{\'e}nek K{\"o}zlem{\'e}nyei},
  volume  = {6},
  pages   = {215--220},
  year    = {1961},
  url     = {https://static.renyi.hu/~p_erdos/1961-09.pdf},
  note    = {Read in the Erd{\H{o}}s archive scan, which shows pages
             216--220; volume and year from the archive's file name and a
             second scan (real.mtak.hu); verify before print. Accessed
             2026-11-16}
}

@article{flajolet1992coupon,
  author  = {Flajolet, Philippe and Gardy, Dani{\`e}le and Thimonier, Lo{\"y}s},
  title   = {Birthday Paradox, Coupon Collectors, Caching Algorithms and
             Self-Organizing Search},
  journal = {Discrete Applied Mathematics},
  volume  = {39},
  number  = {3},
  pages   = {207--229},
  year    = {1992},
  doi     = {10.1016/0166-218X(92)90177-C},
  note    = {Not opened; the unequal-probability expectation integral as
             reproduced and attributed in du Boisberranger, Gardy and Ponty
             (arXiv:1202.0920). DOI from memory: verify}
}

@article{clopper1934binomial,
  author  = {Clopper, C. J. and Pearson, E. S.},
  title   = {The Use of Confidence or Fiducial Limits Illustrated in the
             Case of the Binomial},
  journal = {Biometrika},
  volume  = {26},
  number  = {4},
  pages   = {404--413},
  year    = {1934},
  doi     = {10.2307/2331986},
  note    = {Metadata from the Scilit record; text not opened}
}

@article{hanley1983nothing,
  author  = {Hanley, James A. and Lippman-Hand, Abby},
  title   = {If Nothing Goes Wrong, Is Everything All Right?},
  journal = {JAMA},
  volume  = {249},
  number  = {13},
  pages   = {1743--1745},
  year    = {1983},
  doi     = {10.1001/jama.1983.03330370053031},
  note    = {Metadata from the Scilit record (authors not shown there:
             from Newman 1995's attribution); a subtitle may exist; text not
             opened}
}

@article{miller1992nofailures,
  author  = {Miller, Keith W. and Morell, Larry J. and Noonan, Robert E. and
             Park, Stephen K. and Nicol, David M. and Murrill, Branson W. and
             Voas, Jeffrey M.},
  title   = {Estimating the Probability of Failure When Testing Reveals No
             Failures},
  journal = {IEEE Transactions on Software Engineering},
  volume  = {18},
  number  = {1},
  year    = {1992},
  doi     = {10.1109/32.120314},
  note    = {NASA NTRS record and abstract read; issue number and pages
             not confirmed}
}

@article{butler1993infeasibility,
  author  = {Butler, Ricky W. and Finelli, George B.},
  title   = {The Infeasibility of Quantifying the Reliability of
             Life-Critical Real-Time Software},
  journal = {IEEE Transactions on Software Engineering},
  volume  = {19},
  number  = {1},
  pages   = {3--12},
  year    = {1993},
  doi     = {10.1109/32.210303},
  note    = {Read as the NASA Langley preprint (NTRS 20040139817);
             journal volume, pages and DOI not confirmed from the
             journal}
}

@article{littlewood1993ultrahigh,
  author  = {Littlewood, Bev and Strigini, Lorenzo},
  title   = {Validation of Ultrahigh Dependability for Software-Based
             Systems},
  journal = {Communications of the ACM},
  volume  = {36},
  number  = {11},
  pages   = {69--80},
  year    = {1993},
  doi     = {10.1145/163359.163373},
  note    = {City Research Online record read; body not read}
}

@article{pearson1900chisquare,
  author  = {Pearson, Karl},
  title   = {On the Criterion that a Given System of Deviations from the
             Probable in the Case of a Correlated System of Variables is
             Such that it Can be Reasonably Supposed to have Arisen from
             Random Sampling},
  journal = {The London, Edinburgh, and Dublin Philosophical Magazine and
             Journal of Science},
  volume  = {50},
  number  = {302},
  pages   = {157--175},
  year    = {1900},
  doi     = {10.1080/14786440009463897},
  note    = {Metadata from the Scilit record (title truncated there; the
             tail is the well-known one); DOI not shown there: verify}
}

@article{marsaglia2003kolmogorov,
  author  = {Marsaglia, George and Tsang, Wai Wan and Wang, Jingbo},
  title   = {Evaluating {Kolmogorov's} Distribution},
  journal = {Journal of Statistical Software},
  volume  = {8},
  number  = {18},
  pages   = {1--4},
  year    = {2003},
  doi     = {10.18637/jss.v008.i18},
  note    = {Abstract page read}
}

@article{kuhn2004interactions,
  author  = {Kuhn, D. Richard and Wallace, Dolores R. and Gallo, Albert M.},
  title   = {Software Fault Interactions and Implications for Software
             Testing},
  journal = {IEEE Transactions on Software Engineering},
  volume  = {30},
  number  = {6},
  pages   = {418--421},
  year    = {2004},
  doi     = {10.1109/TSE.2004.24},
  note    = {NIST CSRC record and abstract read; given names Dolores R.
             and Albert M. not confirmed there (record shows "Richard Kuhn,
             Dolores Wallace, A. Gallo")}
}

@techreport{kuhn2010practical,
  author      = {Kuhn, D. Richard and Kacker, Raghu N. and Lei, Yu},
  title       = {Practical Combinatorial Testing},
  institution = {National Institute of Standards and Technology},
  type        = {NIST Special Publication},
  number      = {800-142},
  year        = {2010},
  month       = oct,
  url         = {https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-142.pdf},
  note        = {Read (first 100,000 characters): interaction rule, Tables
                 10--11 on random versus covering arrays. Accessed
                 2026-11-16}
}

@article{cohen1997aetg,
  author  = {Cohen, David M. and Dalal, Siddhartha R. and Fredman, Michael L.
             and Patton, Gardner C.},
  title   = {The {AETG} System: An Approach to Testing Based on Combinatorial
             Design},
  journal = {IEEE Transactions on Software Engineering},
  volume  = {23},
  number  = {7},
  pages   = {437--444},
  year    = {1997},
  doi     = {10.1109/32.605761},
  note    = {Researchr record read (abstract missing there); DOI from
             memory: verify}
}

@inproceedings{lei2007ipog,
  author    = {Lei, Yu and Kacker, Raghu and Kuhn, D. Richard and Okun, Vadim
               and Lawrence, James},
  title     = {{IPOG}: A General Strategy for T-Way Software Testing},
  booktitle = {14th Annual IEEE International Conference and Workshops on the
               Engineering of Computer-Based Systems (ECBS'07)},
  pages     = {549--556},
  year      = {2007},
  doi       = {10.1109/ECBS.2007.47},
  note      = {NIST CSRC record and abstract read; J. Lawrence's given name
               not shown there}
}

@article{kleitman1973kindependent,
  author  = {Kleitman, Daniel J. and Spencer, Joel},
  title   = {Families of k-Independent Sets},
  journal = {Discrete Mathematics},
  volume  = {6},
  number  = {3},
  pages   = {255--262},
  year    = {1973},
  doi     = {10.1016/0012-365X(73)90098-8},
  note    = {Scilit record read (authors not shown there); the CAN(2,k,2)
             formula as stated in Hiess and Kampel 2025}
}

@misc{hiess2025balanced,
  author       = {Hiess, Irene and Kampel, Ludwig},
  title        = {Determining Covering Array Numbers via Balanced Covering
                  Arrays},
  howpublished = {arXiv:2510.17596},
  year         = {2025},
  url          = {https://arxiv.org/abs/2510.17596},
  note         = {Read: CAN(2,k,2) formula, CAN(2,13,3) = 15, CAN(3,k,2)
                  <= 17 for k <= 16. Preprint. Accessed 2026-11-16}
}

@misc{nist-covering-arrays,
  author       = {{NIST Covering Arrays Team}},
  title        = {Covering Array Tables},
  howpublished = {National Institute of Standards and Technology},
  url          = {https://math.nist.gov/coveringarrays/coveringarray.html},
  note         = {Definition of CA(t,k,v) and CAN; archive of best-known
                  arrays; points to Colbourn's tables. Accessed 2026-11-16}
}

@misc{colbourn-ca-tables,
  author       = {Colbourn, Charles J.},
  title        = {Covering Array Tables for t=2,3,4,5,6},
  url          = {https://www.public.asu.edu/~ccolbou/src/tabby/catable.html},
  note         = {Index page read; table values not retrieved. Accessed
                  2026-11-16}
}

@article{arcuri2012interaction,
  author  = {Arcuri, Andrea and Briand, Lionel},
  title   = {Formal Analysis of the Probability of Interaction Fault
             Detection Using Random Testing},
  journal = {IEEE Transactions on Software Engineering},
  volume  = {38},
  number  = {5},
  pages   = {1088--1099},
  year    = {2012},
  url     = {https://orbilu.uni.lu/handle/10993/1190},
  note    = {ORBilu record and abstract read; DOI not shown there.
             Accessed 2026-11-16}
}

@article{good1953species,
  author  = {Good, I. J.},
  title   = {The Population Frequencies of Species and the Estimation of
             Population Parameters},
  journal = {Biometrika},
  volume  = {40},
  number  = {3--4},
  pages   = {237--264},
  year    = {1953},
  doi     = {10.1093/biomet/40.3-4.237},
  note    = {Read in a scan (page headers 238--262; Turing credited for
             formula (2)); issue, first and last page and DOI from memory:
             verify}
}

@article{chao2017thirty,
  author  = {Chao, Anne and Colwell, Robert K.},
  title   = {Thirty Years of Progeny from {Chao's} Inequality: Estimating
             and Comparing Richness with Incidence Data and Incomplete
             Sampling},
  journal = {SORT: Statistics and Operations Research Transactions},
  volume  = {41},
  number  = {1},
  pages   = {3--54},
  year    = {2017},
  url     = {https://gwern.net/doc/statistics/order/capture/2017-chao.pdf},
  note    = {Read: Chao2 (eq. 2b), sample coverage (7d--e), extrapolation
             (7c), assumptions. Accessed 2026-11-16}
}

@article{chao2009sufficient,
  author  = {Chao, Anne and Colwell, Robert K. and Lin, Chih-Wei and
             Gotelli, Nicholas J.},
  title   = {Sufficient Sampling for Asymptotic Minimum Species Richness
             Estimators},
  journal = {Ecology},
  volume  = {90},
  number  = {4},
  pages   = {1125--1133},
  year    = {2009},
  url     = {https://www.uvm.edu/~ngotelli/manuscriptpdfs/ChaoEcology2009.pdf},
  note    = {Read; cites Shen, Chao and Lin 2003 (Ecology 84:798--804).
             Accessed 2026-11-16}
}

@article{boehme2018stads,
  author  = {B{\"o}hme, Marcel},
  title   = {{STADS}: Software Testing as Species Discovery},
  journal = {ACM Transactions on Software Engineering and Methodology},
  volume  = {27},
  number  = {2},
  year    = {2018},
  doi     = {10.1145/3210309},
  note    = {Read as arXiv:1803.02130v2 (subtitle there: Spatial and
             Temporal Extrapolation from Tested Program Behaviors); journal
             metadata from researchr}
}

@inproceedings{boehme2021residual,
  author    = {B{\"o}hme, Marcel and Liyanage, Danushka and W{\"u}stholz,
               Valentin},
  title     = {Estimating Residual Risk in Greybox Fuzzing},
  booktitle = {Proceedings of the 29th ACM Joint European Software Engineering
               Conference and Symposium on the Foundations of Software
               Engineering (ESEC/FSE '21)},
  year      = {2021},
  doi       = {10.1145/3468264.3468570},
  note      = {Abstract read on the conference page; full text not opened}
}

@inproceedings{liyanage2023reachable,
  author    = {Liyanage, Danushka and B{\"o}hme, Marcel and Tantithamthavorn,
               Chakkrit and Lipp, Stephan},
  title     = {Reachable Coverage: Estimating Saturation in Fuzzing},
  booktitle = {Proceedings of the 45th International Conference on Software
               Engineering (ICSE 2023)},
  year      = {2023},
  url       = {https://mpi-softsec.github.io/papers/ICSE23-effectiveness.pdf},
  note      = {Read (author copy); venue from dblp search result, DOI not
               retrieved. Accessed 2026-11-16}
}

@inproceedings{boehme2020entropic,
  author    = {B{\"o}hme, Marcel and Man{\`e}s, Valentin J. M. and Cha,
               Sang Kil},
  title     = {Boosting Fuzzer Efficiency: An Information Theoretic
               Perspective},
  booktitle = {Proceedings of the 28th ACM Joint European Software Engineering
               Conference and Symposium on the Foundations of Software
               Engineering (ESEC/FSE '20)},
  year      = {2020},
  doi       = {10.1145/3368089.3409748},
  note      = {Read (author copy)}
}

@misc{boehme2018roadmap,
  author       = {B{\"o}hme, Marcel},
  title        = {Assurance in Software Testing: A Roadmap},
  howpublished = {arXiv:1807.10255},
  year         = {2018},
  url          = {https://arxiv.org/abs/1807.10255},
  note         = {Read via ar5iv. Accessed 2026-11-16}
}

@article{boehme2016efficiency,
  author  = {B{\"o}hme, Marcel and Paul, Soumya},
  title   = {A Probabilistic Analysis of the Efficiency of Automated
             Software Testing},
  journal = {IEEE Transactions on Software Engineering},
  volume  = {42},
  number  = {4},
  pages   = {345--360},
  year    = {2016},
  doi     = {10.1109/TSE.2015.2487274},
  note    = {Read as the accepted version (volume, issue, pages blank
             there; 42(4):345--360 from memory: verify)}
}

@inproceedings{malka1998bugdata,
  author    = {Malka, Yossi and Ziv, Avi},
  title     = {Design Reliability -- Estimation through Statistical Analysis
               of Bug Discovery Data},
  booktitle = {Proceedings of the 35th Design Automation Conference (DAC '98)},
  year      = {1998},
  url       = {https://www.cs.york.ac.uk/rts/docs/SIGDA-Compendium-1994-2004/papers/1998/dac98/pdffiles/39_2.pdf},
  note      = {Read (SIGDA compendium copy). Pages and DOI not retrieved.
               Accessed 2026-11-16}
}

@article{goel1979nhpp,
  author  = {Goel, Amrit L. and Okumoto, Kazu},
  title   = {Time-Dependent Error-Detection Rate Model for Software
             Reliability and Other Performance Measures},
  journal = {IEEE Transactions on Reliability},
  volume  = {R-28},
  number  = {3},
  pages   = {206--211},
  year    = {1979},
  doi     = {10.1109/TR.1979.5220566},
  note    = {Scilit record and abstract read (authors not shown there);
             text not opened}
}

@inproceedings{lachish2002holes,
  author    = {Lachish, Oded and Marcus, Eitan and Ur, Shmuel and Ziv, Avi},
  title     = {Hole Analysis for Functional Coverage Data},
  booktitle = {Proceedings of the 39th Design Automation Conference (DAC 2002)},
  pages     = {807--812},
  year      = {2002},
  doi       = {10.1145/513918.514119},
  note      = {Researchr record only; text not opened}
}

@misc{kwon-dvcon-simai,
  author       = {Kwon, Jihye and Ha, Sukwon and Kim, Youngsik and Choi,
                  Seonil Brian and Cha, Daeseo and Kim, Space and Kang,
                  Kunhyuk and Pierce, John and Metodi, Amit and Sharma,
                  Saurabh and Jung, Heedo and Watanabe, Yosinori},
  title        = {Functional Coverage Closure in {SoC} Interconnect
                  Verification with Iterative Machine Learning},
  howpublished = {DVCon proceedings},
  url          = {https://dvcon-proceedings.org/wp-content/uploads/1096.pdf},
  note         = {Read. Samsung and Cadence authors; results on the vendor's
                  tools: vendor co-authored. Year and conference edition not
                  stated in the text. Accessed 2026-11-16}
}

@article{shannon1948communication,
  author  = {Shannon, C. E.},
  title   = {A Mathematical Theory of Communication},
  journal = {The Bell System Technical Journal},
  volume  = {27},
  pages   = {379--423, 623--656},
  year    = {1948},
  doi     = {10.1002/j.1538-7305.1948.tb01338.x},
  note    = {Read (reprint copy); DOI is Part I's, from memory: verify}
}

@misc{boisberranger2012weighted,
  author       = {du Boisberranger, J{\'e}r{\'e}mie and Gardy, Dani{\`e}le
                  and Ponty, Yann},
  title        = {The Weighted Words Collector},
  howpublished = {arXiv:1202.0920},
  year         = {2012},
  url          = {https://arxiv.org/abs/1202.0920},
  note         = {Read for eq. (1.1), the unequal-probability coupon integral
                  attributed to Flajolet, Gardy and Thimonier. Accessed
                  2026-11-16}
}
```

## 7. Confidence notes

Measured and reproducible (high confidence): every number in section 2
comes from a saved `run.out` produced by the script beside it, with
fixed seeds; the Verilator runs are on 5.052 and the uniformity runs
on 5.052 with z3-solver 5.4.1.0. The FIFO Markov chain and the
Verilator exposure rate agree (0.2421 inside [0.210, 0.264]), which
checks the logger's semantics against the RTL's.

Unverified or partly verified, to settle before the chapter prints:
1. **Flajolet, Gardy and Thimonier 1992**: the integral formula is
   verified only through du Boisberranger, Gardy and Ponty; the original
   was not opened (HAL behind bot protection). The DOI in the entry is
   from memory.
2. **Erdős and Rényi 1961**: the limit law is confirmed in the scan,
   but the scan's text is garbled; volume 6 and pages 215-220 are from
   the archive file names, not from the page.
3. **Clopper-Pearson, Pearson 1900, Hanley and Lippman-Hand,
   Goel-Okumoto, Kleitman-Spencer, Lachish et al.**: metadata records
   only. The mathematics attributed to each is standard, but "cite the
   primary source" means the chapter's drafter should open each before
   quoting anything beyond the formula.
4. **Rule-of-thumb sources not opened**: the "expected count >= 5" rule
   for chi-square (usually credited to Cochran), Stephens' small-n KS
   correction, the Miller-Madow entropy correction (Miller 1955). The
   chapter should either open a source or state them as the book's
   working rules without attribution.
5. **AETG's algorithm**: the one-row-at-a-time, best-of-M-candidates
   description used to write `covering.py` is the commonly cited one;
   the AETG paper's text was not read (researchr had no abstract).
6. **Kuhn, Wallace and Gallo**: the per-system cumulative percentages
   by interaction strength are in the paper body, which did not load;
   only SP 800-142's restatement ("4- to 6-way ... nearly all
   failures") was read. No study of *hardware* bugs by interaction
   strength was found; the chapter must not transfer the software
   percentages to RTL.
7. **CAN(2, 13, 3) = 15**: read in Hiess and Kampel (preprint), who
   attribute it to a computational result; Colbourn's table values
   were not retrieved (blocked).
8. **Littlewood and Strigini**: only the record was read; the note
   cites it for its topic, not for any claim.
9. **Kwon et al.**: the DVCon year is not stated in the PDF text; the
   results are on vendor tools with vendor co-authors and must carry
   the vendor label.
10. **ICSE 2023 DOI** for Liyanage et al. not retrieved (dblp blocked
    the fetch).
11. **Böhme and Paul's volume and pages** (42(4):345-360) are from
    memory; the accepted version leaves them blank.
12. **Uniformity results are release-specific.** Verilator 5.054
    (2026-11-01) lists a `solve...before` change; the M9 table is a
    5.052 measurement and will need re-running if the pin moves
    (STATUS next action 3).
13. **The greedy covering-array sizes are from one randomized
    implementation** (best of three runs); they are an illustration
    that greedy is near but above the best known, not a benchmark of
    AETG or IPOG. ACTS was not run (not in the book's toolchain; a Java
    download from NIST).
14. **Species-estimator instability at small Q2** (push 30%): the
    resampled mean and median differ by 10 bins; the chapter should
    report medians or intervals, and should not print a single Chao2
    figure as "the" estimate.
15. **The covergroup itself was not used** in the measurements; the
    grid is a finer version of Chapter 8's cross. Bin counts for
    `fifo_cg` per seed are an outline-stage task.

## 8. Open questions for the outline

1. **Spine** (Q2): FIFO throughout with Chapter 7's packet as the
   uniformity specimen, or a second spine? And does the t-way section
   use Chapter 11's DMA transfer space (needs one more measurement with
   its exclusions as constraints)?
2. **Proof depth** (Q4): inline derivations or a mathematical appendix?
   Which results are derived (hit probability, union bound, rule of
   three, Good-Turing) and which only stated?
3. **New Python dependency?** All experiments used the standard library
   (incomplete gamma, Kolmogorov series, binomial bisection written
   out, about 250 lines). The chapter can ship `statlib.py`-style code
   as listings, or add scipy to the `dvbook` environment. The logic
   chapter's precedent was no new dependency; recommend the same.
4. **Where cycle-level dependence is taught.** M4 (6x error of the
   cycle-level coupon model) and M13 (Chao1 on cycles stays near
   S_obs) are the same lesson; one Pitfall or a section of its own
   ("the unit of independence is the seed")?
5. **Bounds after clean seeds: operational profile or not** (Q7)?
   Teaching Musa's operational profile needs a source not yet opened;
   stating the limit with the push-30% measurement may be enough.
6. **Information theory scope** (Q5): one section with entropy, KL/G
   and MI, ending on Entropic as the hand-off to the fuzzing chapter?
7. **Reliability growth**: is Malka and Ziv (1998) enough as the In
   Practice, or should the chapter fit a Goel-Okumoto curve to the
   book's own bug data (there is none at scale; the FIFO has one bug)?
   Recommend: present the model and the IBM data, no fit of our own.
8. **Covergroup example cost**: running `tb_fifo_cov.sv` under hundreds
   of seeds in `scripts/check-examples.sh` adds minutes; decide seed
   counts per example (the experiments used 250-1000) and whether long
   runs are captured once as data files.
9. **Re-measure on 5.054?** If the Verilator pin moves, M9 must be
   re-run (`uniformity/run.sh`, about 8 minutes), and the
   `solve before` row may change.
