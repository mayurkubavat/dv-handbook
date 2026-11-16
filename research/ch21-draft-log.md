# Draft log: The Statistics of Random Testing and Coverage

Started 2026-11-16. Inputs: `research/ch21-outline.md` (section 10,
"Pre-draft measurements", overrides the earlier sections where they
differ), `research/ch21-statistics-random-testing.md` (RN), the ten
example directories under `examples/ch21-statistics-random-testing/`
(their `run.out` files and generated tables are the only source for
every number), and `chapters/ch19-formal-techniques.qmd` and
`chapters/ch18-formal-property-verification.qmd` as the model for shape
and style.

## 1. Plan and choices made before writing

- One chapter file, `chapters/ch21-statistics-random-testing.qmd`,
  unwrapped, one paragraph per line, as ch18 and ch19.
- Section order follows the outline: motivation, the hit-probability
  vector, the seed as the unit of independence, the coupon collector,
  clean seeds, uniformity, t-way coverage, unseen bins, information,
  operational profiles and reliability growth, the worked example
  (sizing and signing off the FIFO regression), Future directions,
  Summary, Exercises, Further reading.
- One object carries the chapter: the hit-probability vector $p$ of a
  fixed generator and seed length. Each later section is a question
  about $p$ or about the seeds drawn from it.
- Every listing is spliced with `{.lang include=... lines="a-b"}` (53
  includes, two of them generated tables with `{{< include >}}`); every
  range was checked by script against its file (section 7). No number
  appears in prose that a splice or a generated table does not show,
  except arithmetic that the run itself prints on another line.
- Definitions and short derivations sit in Definition callouts with
  their conditions stated (independence of seeds, fixed generator,
  fixed seed length). Every definition, bound or result cites a source
  the outline marks as read; sources read at abstract level are cited
  only for what the abstract states.
- References to earlier chapters by label: `@sec-ch01`, `@sec-ch07`
  (`-why`, `-constraints`, `-solver`, `-example`), `@sec-ch08`
  (`-example`, `-where`, `-closure`, `-cross`), `@sec-ch09-example`,
  `@sec-ch11`, `@sec-ch11-coverage`. Later unwritten chapters by name
  only ("Fuzzing Hardware", "Machine Learning in Verification",
  "Metrics, Closure and Sign-off").
- The clean-seed step of the worked example uses Chapter 9's checker,
  as the `worked` and `clean-seeds` examples do. The chapter does not
  run or mention Chapter 1's random testbench against the fixed FIFO.
- Exercises: one Exercise callout under `## Exercises`, as ch18 and
  ch19; the twelve answers are recorded here (section 6).

## 2. Sections and what each claim rests on

Line numbers are of the `run.out` named; directories are under
`examples/ch21-statistics-random-testing/`.

- Motivation (`sec-ch21-motivation`): `seed-unit/run.out` 20-22.
- Hit-probability vector (`sec-ch21-p`): `statlib.py` 173-177;
  `hit-prob/run.out` 1-7 (247 of 1000 seeds, Clopper-Pearson
  [0.2205, 0.2750]), 8-20 (exact chain 0.2421), 21-23;
  `hit-prob/fifo_chain.py` 20-36; `common/fifo_cov.sh` 19-31;
  `seed-unit/run.out` 1-19 (28 reachable bins; `push_x_full` 0.187),
  30-34.
- Seed as unit (`sec-ch21-seed`): sampling-unit definition from
  `chao2017thirty`. `seed-unit/run.out` 42-45 (streak mean 3.04 against
  3.05), 24-29 (`almost` bins: independent-cycle model 0.898 against
  measured 0.271); `unseen/run.out` 42-44. First-trigger window
  (earliest cycle 16, median 137) from the chain, per outline section
  10. Figure `fig-ch21-burst`.
- Coupon collector (`sec-ch21-coupon`): `erdos1961coupon`,
  `flajolet1992coupon`, `boisberranger2012weighted` for the equal,
  limit and Poissonized forms. `statlib.py` 253-271;
  `coupon/run.out` 1-11 (packet example, $E[T]$ 11.0, union bound 44),
  12-21 (256-value forms 37% and 29% above $k H_k$), 22-30;
  `seed-unit/run.out` 35-41 (union sum 27, split 39, product 27,
  median 5, q99 26), 46-47 (cycle model 10.6 seeds, 2.4 times).
  Figure `fig-ch21-coupon`.
- Clean seeds (`sec-ch21-clean`): `hanley1983nothing`,
  `newman1995small` (rule of three), `clopper1934binomial`,
  `butler1993infeasibility`. `statlib.py` 150-170;
  `clean-seeds/run.out` 1-14 (bound table), 15-24 (30-cycle generator,
  0 of 250, bound 0.0119, true p 8.45e-05 from the chain, 141 times),
  25-29 (35,462 seeds for a 95% chance of one trigger), 30-38 (Jeffreys
  ratio 0.64, inside the Pitfall). Figure `fig-ch21-clean`.
- Uniformity (`sec-ch21-uniform`): `pearson1900chisquare`,
  `marsaglia2003kolmogorov`; `ieee1800-2023` for the `dist` and
  `solve...before` semantics; `verilator-issue-8024`.
  `uniformity/run.out` 1-11 (`:=` form p 0.0339 against Bonferroni
  0.0083), 24-26 (`solve...before` 0 of 2000), 28-31 (power: 113, 1047,
  26,265), 32-38 (control: 7 of 200 rejected); `tb_draws.sv` 11-14;
  `uniform.py` 47-63; generated table `tbl-ch21-uniform.md`.
- t-way coverage (`sec-ch21-tway`): `nist-covering-arrays`,
  `kuhn2010practical`, `kleitman1973kindependent`, `hiess2025balanced`
  for the definitions and the binary result; `lei2007ipog`,
  `arcuri2012interaction`, `kuhn2004interactions` at the level the
  outline marks. `tway.py` 88-98, 66-76, 41-49; `t-way/run.out` 2-7
  (200 legal rows, 115 pairs), 8-16 (greedy 23 and 68), 17-35 (uniform
  200 and 551, 8.7 and 8.1 times; factor by factor 89 and 378), 36-56
  (the DMA's own test levels off at 0.887 and 0.828; `|z|` 1.52).
  Figure `fig-ch21-tway`.
- Unseen bins (`sec-ch21-unseen`): `boehme2018stads`; Good-Turing from
  `good1953species`; Chao2 from `chao2017thirty` and
  `chao1987capture`; `boehme2021residual`, `liyanage2023reachable` at
  abstract level. `statlib.py` 311-336; `unseen/run.out` 2-11, 12-22
  (Chao2 28.1 [22.0, 39.2] at 4 seeds), 23-41 (30-cycle generator: 22
  seen, $Q_1 = Q_2 = 0$, reach probability 0.00018). Figure
  `fig-ch21-unseen`.
- Information (`sec-ch21-info`): `shannon1948communication`.
  `info/run.out` 2-11 (effective values 243.7, 193.5, 2.45), 12-16
  (G against $X^2$ within 0.007 and 0.12), 32-45 (mutual information
  0.745 against permutation baseline 0.0075); `statlib.py` 286-295;
  generated table `tbl-ch21-knob.md`. `fine2003cdg`,
  `ioannides2012cdg`, `boehme2020entropic` by title and abstract.
- Operational profiles and growth (`sec-ch21-growth`):
  `musa1989quantifying`, `miller1992nofailures`, `goel1979nhpp`,
  `malka1998bugdata` (In Practice), `butler1993infeasibility`,
  `boehme2016efficiency`. No numbers from the papers are quoted.
- Worked example (`sec-ch21-example`): `worked/run_worked.sh` 14-22;
  `worked/run.out` 1-16 (pilot: union bound 32, 94% of it from the
  `x_full` cells), 17-24, 25-28 (`op_cp` $X^2$ 1.25, p 0.74), 29-31,
  32-34 (1000 of 1000 clean seeds under Chapter 9's checker, bound
  0.0030), 35-44. Worked Example callout of six steps.
- Future directions: `chakraborty2015unigen2`, `boehme2021residual`,
  `kwon-dvcon-simai` (labeled a vendor claim in the text),
  `verilator-changes`.
- Further reading: `kuhn2010practical`, `cohen1997aetg`,
  `boehme2018stads`, `boehme2018roadmap`, `chao2017thirty`,
  `malka1998bugdata`, `lachish2002holes`.

## 3. Figures

Five figures, `figures/gen_ch21_figures.py` (style module `hw`, palette
from `blocks.py`, as ch19). The script reads each data file through a
SHA-256 pin, so a changed data file stops it, and asserts the values the
captions and prose name against the `run.out`:

- `ch21-burst.svg`: `seed-unit/data.tsv`, 28 rows; cross-checked against
  `seed-unit/run.out`.
- `ch21-coupon.svg`: `seed-unit/curve.tsv`; asserts the 0.99 crossings
  at 26 (measured), 27 (product) and 11 (cycle model).
- `ch21-clean.svg`: the `clean-seeds/run.out` table; asserts 8.45e-05,
  0.0119, "141 times" and 35462.
- `ch21-tway.svg`: `t-way/data.tsv`; asserts greedy 23 and 68 and the
  plateau 0.887 and 0.828.
- `ch21-unseen.svg`: `unseen/data.tsv`; asserts 22 seen and the 4-seed
  line.

Rendered to PNG with headless Chrome and inspected. Fixed while
drafting: the x-axis label of `ch21-burst` overlapped the legend
(taller canvas, legend moved down); the "250 clean seeds" label of
`ch21-clean` sat over the rule-of-three line and the n = 300 point
(moved below left); the "greedy" and "plateau" labels of `ch21-tway`
were crossed by the curves (moved to the empty lower right, greedy
completion marked with a hollow point).

## 4. Deviations from the outline

All per outline section 10 unless noted.

- Union bound for `fifo_cg`: sum form 27 and split form 39 (not the
  outline's earlier single figure).
- The Jeffreys bound does not converge to the exact bound; it stays at
  about 0.64 of it at every n. Stated that way.
- First-trigger windows are taken from the exact chain, not from
  simulation.
- Chao2 at 30 cycles is blind (it sees no singletons or doubletons and
  returns the seen count), not unstable. The low-reach comparison was
  cut from the seed section and kept in the unseen section only.
- t-way: random-to-greedy ratio given as 3.9 to 8.7 times; the DMA's own
  test never draws `len = max`, so its curve levels off. The model of
  t-way coverage was confronted with the Verilator runs as the outline
  asks.
- Worked example step 6 uses Chapter 9's checker; G against $X^2$ quoted
  as agreeing within 0.007 and 0.12.
- The packet example's union bound is 44.
- Exercises 4 and 6 kept as the outline gives them; exercise 8 reworded
  to ask for the expected number of new bins, which is also an upper
  estimate of the chance of any.

## 5. Claims cut

- The research-grid "6 times" ratio: not in a `run.out`.
- Musa 1993 (operational profiles) quotation and citation: not read.
- Chao et al. 2009 (sufficient sampling): not read.
- Feller and Mitzenmacher as further reading: not in the note's
  bibliography.
- The Goel-Okumoto mean-value formula: the paper was read at abstract
  level only; the model is named, not stated.
- The IEEE 1800 clause number for `dist`: not reconfirmed.
- Böhme and Paul's "37": not in the read abstract.
- Liyanage et al.'s percentage: not in the read abstract.
- Malka and Ziv's 719 bugs and 6.7% MTTF figure: not read past the
  abstract.
- Accellera constraint proposal citation (`accellera2002constraints`)
  and the Colbourn covering-array tables (`colbourn-ca-tables`): not
  opened.
- Prose numbers that no `run.out` prints were removed while drafting:
  "one run in 850", "one in four of six tests", "at 2000 draws one in
  eight".
- Not given a refs.bib entry because the chapter does not cite them:
  `chao2009sufficient`, `musa1993profiles`, `accellera2002constraints`,
  `littlewood1993ultrahigh`, `colbourn-ca-tables`.

## 6. Exercise answers

Each answer follows from the definitions of the section named; the
computations were rerun in Python and agree with the forms the
`common/run.out` checks (lines 9-30), `hit-prob/run.out` and
`seed-unit/run.out` line 47 print.

1. $\lceil \ln 0.05 / \ln 0.99 \rceil = 299$ seeds.
2. $1 - 0.05^{1/600} = 0.00498$; the rule of three gives
   $3/600 = 0.005$.
3. $6 H_6 = 6(1 + 1/2 + \cdots + 1/6) = 14.7$ throws.
4. The smallest $n$ with $28 (1 - 0.187)^n \le 0.01$: $n = 39$ (the
   split form of `seed-unit/run.out`).
5. $0.9^{64} = 0.0012$ (0.00118).
6. (a) $1 - (1 - 0.0113)^{200} = 0.897$. (b) The smallest $n$ with
   $(1 - 0.27)^n \le 0.01$: $n = 15$.
7. $S_{\mathrm{obs}} + \frac{T-1}{T}\,\frac{Q_1^2}{2 Q_2} = 60 + 0.9
   \cdot 16/4 = 63.6$.
8. $Q_1 / T = 3/200 = 0.015$.
9. $X^2 = 76^2/6000 + 60^2/3000 + 16^2/1000 = 0.963 + 1.2 + 0.256 =
   2.42$; below 5.99, so the 6:3:1 law is not rejected at 0.05.
10. $H = -(0.6 \log_2 0.6 + 0.3 \log_2 0.3 + 0.1 \log_2 0.1) = 1.295$
    bits; effective number $2^{1.295} = 2.45$ (as `info/run.out`
    prints for the 6:3:1 law).
11. $6 \times 4 = 24$: the two largest factors' level pairs must each
    appear in some test.
12. The least $N$ with $\binom{N-1}{\lceil N/2 \rceil} \ge 20$:
    $\binom{7}{4} = 35 \ge 20$ and $\binom{6}{4} = 15 < 20$, so
    $N = 8$.

## 7. Final checks

- Word count: 15,359 by `wc -w` on the source (markup included);
  15,147 excluding fenced blocks and include shortcodes.
- `scripts/check-structure.sh`: "every chapter keeps the template".
- `scripts/check-citations.sh`: check 1, no swallowed references.
  Check 2 run against a pandoc plain-text render of the chapter: of the
  39 keys ch21 cites, all appear except `erdos1961coupon` and the five
  `boehme*` keys, which are false positives: the script's surname
  extraction stops at the brace in `Erd{\H{o}}s` and `B{\"o}hme` (the
  rendered text contains "Erdős" three times and "Böhme" eighteen
  times). The accents are kept in the house LaTeX-escape form.
- Splices: every `include` path exists and every `lines` range lies
  inside its file (script over all 53 includes).
- Cross-references: all 31 distinct `@sec-`, `@fig-`, `@tbl-` targets in
  the chapter resolve to a label in `chapters/`, `appendices/` or an
  included table; every glossary `See @sec-ch21-...` resolves.
- Render: quarto is not installed. Includes were expanded by a script
  and the result converted with pandoc to HTML (MathJax) and LaTeX,
  with and without `--citeproc --bibliography refs.bib`: no warnings.
  (The plain-text writer warns that it cannot turn some display math,
  such as `\Bigl`, into Unicode; that writer was used only for the
  citation check.) No stray backslash outside code and math; the two
  generated tables contain no math; no bibliography note prints a
  working note.
- No hard-coded chapter, section, figure or table number in prose; no
  British spellings found by grep in prose.
- refs.bib: 33 new entries appended under a Chapter 21 comment (keys
  checked absent first); DOI entries carry no URL or access date; URL
  entries carry a year and "Accessed 2026-11-16" in `note`. DOIs were
  taken from the research note and could not be reconfirmed against
  Crossref (the proxy refused the connection).
- Glossary: 20 entries added to `appendices/appG-glossary.qmd`, in
  alphabetical place within their sections; no existing entry changed.
- `_quarto.yml`: ch21 registered after ch19 in Part IV.
- `scripts/check-examples.sh` not run: it re-runs the examples and
  rewrites `examples/status.json`, which this task does not touch.

## 8. Round 1 fixes (2026-11-16)

Reviews: `docs/reviews/ch21-gate2a-2026-11-16.md` (A) and
`docs/reviews/ch21-gate2b-2026-11-16.md` (B). Each finding, and what was
done. Line ranges in section 2 above predate this round; the chapter's
`include` attributes are the current map.

### Blocking

- **A-B1, B-B2 (second half): the coupon-figure paragraph.** Rewritten
  with the mechanisms the data support, every number on a `run.out`
  line (`seed-unit/run.out` 48-51, now spliced into the paragraph). The
  bound cannot sit above the measured curve: a draw from the 1000 seeds
  misses bin i with probability exactly 1 - p_i, so the bound is a
  theorem about that law, and `seed_unit.py` checks it for n = 1..80
  (this also removes A-B1 point 5, the 0.9968 against 0.9965 at n = 32,
  which was resampling noise). It is pessimistic by two seeds, 27
  against 25, because at 25 seeds the sum is 0.0149 against a true
  P(some bin missed) of 0.0099: the 0.0028 of runs that miss two or
  more bins are counted once per bin missed, and a factor of 1.5 in
  risk costs about two seeds when each seed multiplies the rarest miss
  probability by 0.813 (ln 1.5 / -ln 0.813 = 1.96). "Hit together or
  not at all" replaced by the measured correlation: every seed that
  shows `full` shows `almost`, none shows an `op_x_full` cell without
  `full`, and 137 of 271 hit all four cells against 0.34 if independent
  given `full`. The tail: the product and the sum agree for the
  arithmetic reason A gives (they differ by products of two or more
  small terms); what sets it is the individual cells missed in seeds
  that do fill the FIFO, 25 seeds against 15 for `full` alone. The
  reviewers' replacement text was used in substance and checked
  against these numbers; A's "nearly disjoint" was not used, because at
  the tail three runs in ten that miss anything miss more than one bin.
- **A-B2: "a clean regression is the expected outcome".** Replaced with
  A's text: 35,000 seeds is where a clean run becomes a 5% event; a
  clean run is more likely than not below ln 2 / p. `clean.py` now
  prints ln 2 / p = 8205 (pinned) inside the spliced Pitfall block
  (`clean-seeds/run.out` 30-39); the text says "about 8,200".
- **B-B1: "within its standard error".** `coupon.py` prints se to two
  decimals and z = (sim - E[T]) / se on each row (the trial count moved
  to the row's third line, so the block keeps its line numbers). z is
  1.45, 1.44, 0.08 for 8, 64, 256 equal bins, -0.86 for 6:3:1, -0.20
  and 0.34 for the two dist laws. The text now says "within one and a
  half standard errors at every size" and quotes the z column; the
  check is |z| <= 2 (was 4 se). "At 64 and 256 bins" became "at every
  size" (at 8 bins sim q99 53 is above the bound's 51 too).
- **B-B2: Chao2's blindness at 30 cycles.** The wrong mechanism ("arrive
  together or not at all, so no singleton") replaced: no seed reached
  fifteen entries, 250 x 0.00018 = 0.044 expected seeds, now printed by
  `unseen.py` (pinned) in the spliced block (`unseen/run.out` 23-42).
  The text adds that one seed reaching the region would have made
  singletons. The same wrong reasoning in `research/ch21-outline.md`
  10.2 is left as written: the outline is a gate-1 evidence record.

### Non-blocking, taken

- **B-N2 (and the 26s).** The resampled curve (2000 shuffled orders,
  Python seed 2026) is replaced by the exact closure law of seeds drawn
  independently from the 1000 measured ones, by inclusion-exclusion
  over the 11 bins not hit by every seed (12 with `climb`): median 5,
  q99 **25** (was 26), with `climb` median 9, q99 **46** (was 43).
  Drawing with replacement was chosen over B's without-replacement
  computation because it is the bootstrap model of a fresh seed and its
  marginal misses are exactly (1 - p_i)^n, which is what makes the
  union-bound comparison exact; without replacement gives the same
  median and q99 (5, 25) and 9, 45 with `climb` (computed in scratch,
  not shipped). The Python seed and the 2000-order loop are gone, so
  the seed-dependence B found (24 to 28; seed 2027 failing the bound
  check) cannot recur. Every use of 26 changed: the seed section, the
  coupon paragraph and figure caption and alt text (0.57 -> 0.55 at 5
  seeds, crossing at 25; "joins" -> "approaches from below" for the
  product, which is 0.9545 against 0.9731 at 20), the summary (two
  lines), the `climb` sentence (43 -> 46). The ratio to the cycle model
  prints 2.4 still (25 / 10.63 = 2.35). `curve.tsv`'s column is renamed
  `measured`; the figure generator was re-pinned (curve.tsv and
  clean-seeds/run.out SHA-256, the q99 regex, the crossing assert and
  the label) and the legend reads "measured: exact law of the 1000
  seeds". Only `ch21-coupon.svg` changed; it was rendered with headless
  Chrome and inspected (crossings 11, 25, 27 labeled; union below the
  measured curve everywhere).
- **B-N1.** `tway.py` section 4 adds the count-level Pearson test of the
  summed `len_x_out` counts against the model (zero cells held out and
  required empty, total required to be 1000): X2 3.1, 9 df, p 0.96,
  checked p > 0.01. The text says so after the per-seed sentence; B's
  three wrong models were not re-run here and are not claimed in the
  text.
- **B-N3: quoted numbers now checked.** seed-unit: 0.0031 before cycle
  40, hazard more than sixfold, |z| < 2 for the 525-of-2266 line (was
  3), iid/measured ratios 1.85-2.4 and above 3, the new tail and
  correlation numbers. coupon: simulated mean, z and q99 pinned per
  row. clean-seeds: smallest coverage 0.959 pinned (was >= 0.94), 141,
  35462, 0.979, 8205 pinned. unseen: the synthetic means (0.2287,
  0.2319, 154.5; 0.0211, 0.0218, 198.8), the 213.3 single-run Chao1,
  the 22.0-39.2 band and 25.7 seen at four seeds. uniformity: every
  p-value but the ordering's above 0.3; one control p-value below the
  Bonferroni threshold. worked: the four op_x_full cells' share, which
  is **95%**, not 94% (the four printed shares, rounded, sum to 94);
  the text now says 95% and a "together" line prints it. t-way: the
  per-seed |z| 1.52 pinned; the formula-against-simulation gap is
  0.0054 at t = 2, so the text's "within 0.005" became "within 0.006"
  and the gap prints to four decimals. info: plug-in 6.25 and true
  7.93, baseline 0.0075, push_x_full's 0.650 and 0.027 pinned. Found
  while doing this: `pop_x_full` carries 0.49 bits, not "about 0.7",
  and was not printed; the table now prints seven rows, the text says
  "0.49 to 0.75 bits, 65 to 100 times the baseline" and names
  `pop_x_full` as the cell the run length moves most (0.138 bits). The
  `Checks` docstring says "the numbers a chapter quotes" instead of
  "every number". Also found: the self-test's `show()` passed every
  string-valued check without comparing it; string, None and inf
  results now go through a pinned `show_is()`.
- **B-N4.** "Good-Turing P(next seed adds a bin)" and "Good-Turing chance
  the next seed adds a bin" relabeled "Good-Turing Q1/T, new bins
  expected in the next seed" in `unseen.py` and `worked.py`;
  `good_turing`'s docstring distinguishes abundance (a probability)
  from incidence (an expected count, an upper estimate of the chance).
  The chapter sentence at the 30-cycle block now says "expects no new
  bin".
- **B-N6.** statlib: `coupon_expect` returns inf for a zero bin;
  `seeds_to_hit` and `union_split_draws` return None for one; `first_n`
  returns None past a cap instead of looping; `chao1`, `chao2`,
  `good_turing` and `ks_uniform` raise ValueError on an empty sample;
  `pearson` and `g_test` drop empty zero-probability cells from the sum
  and df and return p = 0 for a count in one; `quantile` sorts None
  last. Each is a self-test line. The five statlib splice ranges were
  moved to the new line numbers; the `seeds_to_hit` splice now shows
  the p = 0 case and the sentence before it says so.
- **B-N7.** `uniform.py` pins the solver string, "Z3 version 5.4.1",
  beside the simulator pin. The run used `/opt/dvtools/venv/bin/z3`,
  z3-solver package 5.4.1.0 (`pip show`), z3 Python module 5.4.1.
  Not taken: pinning z3-solver in CI and in `dvbook`, and correcting
  `STATUS.md:122`; this round was told not to change the environment
  or `STATUS.md`. `REQUIRES := z3` not added: B judged the loud failure
  acceptable, and the solver pin now names the cause first.
- **B-N8.** `run_worked.sh` records per seed whether `FullBackward_A`
  fired; `worked.py` counts as the original's failures only seeds that
  did not pass and fired it, checks that this is every non-passing seed
  and that it never fires on the repaired FIFO; the printed line says
  "fail in FullBackward_A". `run_tway.sh` uses `grep ... >/dev/null`
  instead of `grep -q`.
- **B-N9.** `tb_draws.sv` header: "Chapter 7's" -> "the constrained-random
  chapter's" (same line count, so the 11-14 splice is unchanged). The
  `tway.py` check label "ch11 unreachable tuples", which prints on
  failure, now names the architecture chapter.
- **A-N1** = B-B1. **A-N2, B-N5 first point:** "a factor of about two,
  and `full` and `almost` by more than three" (ratios 1.88-2.37 and
  3.31), checked. **A-N3:** reworded: the example has no unconstrained
  baseline, so 3.9 to 8.7 does not test Arcuri and Briand's clause; what
  it shows is that under constraints the ratio depends on how tests are
  drawn. "The constraints make it worse" removed. **A-N4:** "on average
  ... low; a single run can overshoot, as the 800-draw row does".
  **A-N5:** the info column reads "KL to uniform ... bits". **A-N6:** "a
  quarter of its cycles at fifteen entries". **A-N7, B-N5 second
  point:** "if the pilot's rates are right". **A-N8:** "would be caught
  nine times in ten by a sample of that size". **A-N9:** "almost
  nothing unseen". **A-N10:** the run.out says "measured per-cycle push
  share 0.249" and the text says it is the measured share, not the
  driver's 1/4. **A-N12:** `institution` braced; renders as one name.
  **A-N13:** `year = {2025}` for `kwon-dvcon-simai`, from the DVCon
  archive listing recorded in `research/agentic-dv-tools-synopsys.md`
  (the PDF states none; the edition is not confirmed, which the note
  says). **A-N14:** the Newman URL could not be checked (no network:
  the proxy refused jamanetwork.com and Crossref) and both research
  records attach 389714 to different articles, so it was dropped; the
  entry is located by JAMA 274(13):1013, and the note says why.
  **A-N15:** Miller et al. softened to "treat explicitly input
  distributions other than the uniform one". **A-N16:** Katona removed
  from the Definition, exercise 12 and the spliced `binary_pairwise`
  docstring (same line count) rather than cited without the text.
  **A-N17:** the two glossary entries now call Q1/n an estimate of the
  number of new bins and an upper estimate of the chance.

### Left, with the reason

- **A-N11** (section 2's mislabeled ranges): not rewritten; the
  paragraph at the head of this section supersedes them.
- **B-N5 third point** (alt text "zero until about 8 seeds"): B calls it
  fine as written.
- **B-N9, file and column names:** `uniformity/ch07_counts.py` and the
  `ch11gen2`/`ch11gen3` columns of `t-way/data.tsv` keep their names;
  they are identifiers that mirror the example directories, not prose,
  and renaming them means re-pinning data the figure reads for no
  change a reader sees.
- **B-N7 environment items:** see above.

### Checks run

- Every changed example (all ten, since statlib changed) run twice from
  clean (build/ and __pycache__ removed) with
  `scripts/check-examples.sh ch21-statistics-random-testing`: all ten
  lint=pass run=pass, and every `run.out`, `.tsv` and table byte-identical
  between the two runs. (The first full run failed `worked` on the
  share pin, 95 against 94; after the fix `worked` was run twice more
  from clean.) `examples/status.json` is as those runs wrote it.
- `python3 -I -B figures/gen_ch21_figures.py`: all five figures, only
  `ch21-coupon.svg` changed.
- `scripts/check-structure.sh` and `scripts/check-citations.sh` pass.
- Includes expanded by script and converted with pandoc 3.1.3,
  `--citeproc --bibliography refs.bib`, to HTML (MathJax) and LaTeX: no
  warnings beyond the expected unresolved Quarto cross-references.
  `kwon-dvcon-simai` prints 2025, the NIST institution prints whole.
