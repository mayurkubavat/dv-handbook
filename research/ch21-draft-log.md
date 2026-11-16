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
