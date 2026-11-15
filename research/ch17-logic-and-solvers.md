# Research note: Logic and Solvers for Verifiers (Chapter 17)

Date: 2026-11-15. Status: done (about 9,000 words plus a script
appendix). Written section by section with the decisive material
first, so the order is: 1 questions, 3 measurements, 2 sources,
4 constraints, 5 open question, appendix, addendum. Feeds: the logic-and-solvers chapter; sets
up the formal property verification chapter and the formal techniques
catalog. Outline: `research/ch17-outline.md`.

Machine and versions for every measurement below (4 cores, 15 GB, Linux):
Python 3.13.18 (`/opt/dvtools/venv`), z3 5.4.1 (binary and `z3-solver`
5.4.1.0), Yosys 0.68 (38e001a6f), InFormal 0.1.0 commit 5114330,
CaDiCaL 3.0.1 (c6073042; a `cadical` binary exists at
`/opt/informal-tools/cadical/build/cadical`, it is not on the PATH),
ABC (`/opt/dvtools/bin/abc`, `yosys-abc`). Installed for this note with
`pip install python-sat dd` into the venv: `python-sat` 1.9.dev22
(ships compiled solvers: MiniSat 2.2, Glucose, CaDiCaL 1.9.5, Kissat
4.0.4 and others; it is a binary wheel, not pure Python) and `dd` 0.6.0
(pure-Python BDDs, `dd.autoref`; the CUDD binding `dd.cudd` is not in
the wheel) with their dependencies `ply`, `six`, `networkx`,
`astutils`. `PATH=/opt/dvtools/bin:$PATH:/opt/dvtools/venv/bin`.

Scratch scripts were kept in a temporary directory outside the
repository; the ones the chapter needs are reproduced in the appendix
of this note so that the note stands alone.

## 1. The questions that decide the chapter's shape

**Q1. Can the whole chapter run on what the book already installs?**
Yes, and it should. Everything below was reproduced with Python 3 and
the `z3-solver` wheel, which the book's CI already installs (workflow
`book.yml`, the `pip install ... z3-solver ...` step), plus `informal`
and Yosys for the two examples that touch RTL. `python-sat` and `dd`
were installed for this note as *cross-checks* only: a 150-line CDCL
solver and a 60-line reduced ordered BDD written for the chapter
reproduce every curve (section 3, B, D), and `z3` (binary or Python)
reads DIMACS and serves as the production SAT solver. Recommendation:
**no new dependency**; `python-sat` is a compiled wheel, not the "small
pure-Python package" the brief allowed, and its solver conflict counts
change with the wheel's version (C.3). This is the one question for
the author (section 5).

**Q2. Does a hand unrolling find the Chapter 1 bug, and at what depth?**
Yes. Two independent unrollings agree with InFormal: the bit-level one
(AIGER from `informal simp --aag`, unrolled by an 80-line Python script,
one CNF per bound) is UNSAT for bounds 0 to 15 and SAT at bound 16; the
word-level one (z3 bit-vectors written from the RTL, state taken after
reset) is unsat for 0 to 14 and sat at 15. The difference of one is
the reset cycle, which the bit-level model contains and the hand model
starts after. InFormal reports depth 16 (section 3, E). So the chapter
can end on the exact number Chapter 9 printed, produced by the reader's
own loop, and the next chapter starts from "what a tool adds to this
loop".

**Q3. What shows "why they blow up" honestly, at example scale?**
Four measured effects, each with a different cause and each cited:
(i) a *proof-system* limit: pigeonhole, 110 variables and 561 clauses,
takes a production solver 2.2 million conflicts (Haken 1985); (ii) a
*structure* limit: the miter of `a*b` against `b*a`, bit-blasted, costs
about four times more per added bit (36 thousand conflicts at 8 bits,
573 thousand at 10), while the adder miter grows linearly to 128 bits;
(iii) a *representation* limit: the BDD of an adder's carry is 3n-1
nodes in one variable order and 2^(n+1)-2 in another, and a
multiplier's middle bit grows by about 2.4 times per bit in any order
tried (Bryant 1986, 1991); (iv) a *density* effect: random 3-SAT is
hardest near 4.3 clauses per variable (Mitchell, Selman, Levesque
1992). None needs more than a minute.

**Q4. Is "what clause learning buys" visible in a readable solver?**
Yes, cleanly. On the adder miter with the same decision order, DPLL
needs exactly 4^n - 1 decisions, the same search with learning about
2^n conflicts, the same again with an activity heuristic a number that
grows linearly (1,723 conflicts at 32 bits, where DPLL would need
1.8e19). On pigeonhole all three stay exponential. That one table
separates the three ideas (search, learning, heuristics) and shows the
limit none of them removes.

**Q5. Word level or bit level: what does an SMT solver add?**
Measured: z3 answers `a*b != b*a` at 64 bits in 0.00 s because its
rewriter normalizes the two products to the same term; no search runs.
The same theorem stated with a schoolbook shift-and-add multiplier on
both sides, where no rewrite applies, costs z3 0.84 s at 8 bits, 6.1 s
at 9, 31 s at 10 and more than 100 s at 11, the same curve as the
bit-blasted CNF in a SAT solver. So the honest statement is: the
bit-vector theory is decided by rewriting first and bit-blasting
second; the word level helps exactly when a rewrite fires.

**Q6. Order of presentation.** Question-first, one thread: a full
adder (one gate at a time into CNF), two adders (a miter), a solver
(DPLL, then learning), the same solver on things it cannot do, the two
other representations (BDD, AIG), the word level (SMT), then a clock
(unrolling the counter and the FIFO). History is carried by citations,
not by ordering: BDDs (1986) come after SAT in the chapter although
they came first in tools, because the reader's toolchain is SAT-based.

**Q7. What must be left out.** Induction, IC3/PDR, interpolation,
liveness, assumptions/covers methodology and every abstraction
technique belong to the next two chapters. This chapter may say that a
bound is not a proof and show the unrolling getting slower with depth
on the fixed FIFO (0.6 s for 20 bounds, 9.2 s for 40 in z3); it must
not explain how a proof is obtained.

## 3. Measurements (run 2026-11-15; section 2, the source table, follows below)

Conventions. `PY` is `/opt/dvtools/venv/bin/python` (the `python3`
first on the PATH is `/usr/local/bin/python3`, which has no `z3`; see
pitfall P1). `CADICAL` is `/opt/informal-tools/cadical/build/cadical`.
"Book solvers" are the three Python files in the appendix: `dpll.py`
(85 code lines), `cdcl.py` (149), `cdcl_vsids.py` (35, a subclass).
They were checked against MiniSat on 3,000 random formulas of up to 25
variables (`selftest.py`: "3000 random instances agree with MiniSat;
953 satisfiable", models verified clause by clause). Counts printed by
the book solvers are deterministic (no randomness, no clock); counts
from z3, CaDiCaL and MiniSat are deterministic for one version and
change between versions; wall-clock seconds are indicative only.

### A. Tseitin encoding of a full adder, by hand and by four tools

Circuit (`full_adder.sv`): `p = a ^ b; sum = p ^ cin; g = a & b;
t = p & cin; cout = g | t`. Hand encoding (`full_adder.cnf`), one
variable per signal (1=a 2=b 3=cin 4=p 5=sum 6=g 7=t 8=cout), 4
clauses per XOR, 3 per AND, 3 per OR: **8 variables, 17 clauses**,
plus the question as unit clauses.

| question | units added | `CADICAL -q` | `dpll.py` |
|---|---|---|---|
| can `sum` and `cout` both be 1 with `a = 0`? | `5`, `8`, `-1` | `s UNSATISFIABLE`, exit 20 | `s UNSATISFIABLE`, `decisions 0 conflicts 1 propagations 8` |
| can `sum` and `cout` both be 1? | `5`, `8` | `s SATISFIABLE`, `v 1 2 3 -4 5 6 -7 8 0`, exit 10 | same model; `cdcl.py`: `decisions 2 conflicts 0` |

The unsatisfiable one is refuted by unit propagation alone (no
decision), a good first trace to walk through by hand. The model of
the second is unique (a = b = cin = 1), so it is safe to print.

The same circuit through tools (all equisatisfiable with the hand CNF,
none identical to it):

| route | command | size |
|---|---|---|
| Yosys AIG | `yosys -q -p "read_verilog -sv full_adder.sv; proc; opt_clean; aigmap; opt_clean; write_aiger -ascii -symbols fa.aag"` | `aag 12 3 0 2 9`: **9 ANDs**; `a & b` appears twice (`8 4 2` and `20 4 2`), so does `p & cin`: `aigmap` does not hash structurally |
| ABC | `yosys-abc -c "read_aiger fa.aig; strash; print_stats; write_cnf fa_abc.cnf"` | `and = 7 lev = 4`; `CNF stats: Vars = 8. Clauses = 17. Literals = 45.` |
| InFormal | `informal simp fa.aag` | `loaded inputs 3 latches 0 ands 9 bads 2 ...` / `simplified inputs 3 latches 0 ands 7 bads 2 ...` (outputs are read as bads) |
| Yosys SAT | `yosys -q -p "read_verilog -sv full_adder.sv; proc; opt_clean; sat -set sum 1 -set cout 1 -set a 0 -dump_cnf fa_yosys.cnf"` | `p cnf 40 100` (ezSAT; not minimal) |
| z3 | `Tactic("tseitin-cnf")` on the goal `{sum, cout}` | `p cnf 4 10` (z3 simplifies while encoding; one auxiliary variable) |

Lesson for the text: the encoding is not unique, its size is linear in
the circuit (3 clauses per AND gate is the whole rule for an AIG), and
tools differ by a constant factor of up to 6 here (17 to 100 clauses).
ABC's CNF has the same counts as the hand encoding (8 variables, 17
clauses) but is not the same clauses: it encodes the majority function
of `cout` directly.

### B. DPLL against clause learning, same instances (`compare.py`)

`PY gen.py adder N f.cnf` writes the miter of two N-bit adders (a
ripple-carry adder with carry `g | (p & c)` against one with carry
`ab | ac | bc` and the sum's XORs associated the other way), inputs
numbered first; unsatisfiable. `php N` is N+1 pigeons in N holes.
`fifo_kK` is the Chapter 1 FIFO unrolled to bound K (section E).
Columns: decisions/conflicts of `dpll.py`; conflicts of `cdcl.py`
(same decision order: lowest-numbered free variable, true first);
conflicts of `cdcl_vsids.py` (activity order); conflicts of CaDiCaL
1.9.5 through python-sat, as the production reference.

| instance | vars | clauses | DPLL decisions | CDCL conflicts | +activity conflicts | CaDiCaL conflicts | answer |
|---|---|---|---|---|---|---|---|
| adder2 | 24 | 71 | 15 | 12 | — | 22 | unsat |
| adder3 | 39 | 116 | 63 | 27 | — | 44 | unsat |
| adder4 | 54 | 161 | 255 | 54 | 79 | 56 | unsat |
| adder5 | 69 | 206 | 1,023 | 106 | — | 79 | unsat |
| adder6 | 84 | 251 | 4,095 | 208 | 174 | 98 | unsat |
| adder7 | 99 | 296 | 16,383 | 410 | — | 127 | unsat |
| adder8 | 114 | 341 | 65,535 (17.6 s) | 812 (0.16 s) | 476 (0.05 s) | 147 | unsat |
| adder10 | 144 | 431 | > 100,000 (stopped) | 3,216 | 493 | 197 | unsat |
| adder12 | 174 | 521 | stopped | 12,820 (5.2 s) | 553 | 309 | unsat |
| adder16 | 234 | 701 | stopped | > 20,000 (stopped) | 1,075 (0.15 s) | 469 | unsat |
| adder32 | 474 | 1,421 | stopped | stopped | 1,723 (0.57 s) | 883 | unsat |
| adderbug8 | 114 | 341 | 263 | 15 | — | 16 | sat |
| adderbug12 | 174 | 521 | 4,107 | 23 | — | 24 | sat |
| php4 | 20 | 45 | 51 | 37 | — | 32 | unsat |
| php5 | 30 | 81 | 374 | 145 | 103 | 133 | unsat |
| php6 | 42 | 133 | 3,245 | 602 | 432 | 1,044 | unsat |
| php7 | 56 | 204 | 32,780 (3.7 s) | 2,384 (0.5 s) | 2,019 | 7,130 | unsat |
| php8 | 72 | 297 | > 200,000 (stopped) | 8,872 (5.4 s) | — | 31,719 | unsat |
| fifo_k8 | 955 | 2,765 | > 20,000 (92 s, stopped) | 33 (0.03 s) | 48 | 32 | unsat |
| fifo_k15 | 1,690 | 4,914 | — | 185 (0.11 s) | 221 | — | unsat |
| fifo_k16 | 1,795 | 5,221 | > 3,000 (stopped) | 195 (0.09 s) | 247 | — | **sat** |

Readings the chapter may state, each visible in the table:

- DPLL on the adder miter makes **exactly 4^N - 1 decisions** (15, 63,
  255, 1,023, 4,095, 16,383, 65,535): with the 2N inputs first in the
  order it enumerates every input pair, i.e. it simulates.
- With learning and the *same* order the count roughly **doubles per
  bit** (54, 106, 208, 410, 812; 3,216 at 10; 12,820 at 12): 2^N in
  place of 4^N. Learning alone halves the exponent; it does not remove
  it.
- With the activity heuristic the count is **near-linear** (476, 493,
  553, 1,075, 1,723 for 8, 10, 12, 16, 32 bits). CaDiCaL: 147 to 883.
- On pigeonhole every column multiplies per added hole (DPLL about 9x,
  learning about 4x, CaDiCaL between 4x and 8x): no heuristic helps, which is
  what the resolution lower bound predicts.
- The book's 149-line solver finds the FIFO bug in the bound-16 CNF
  (1,795 variables) in 0.09 s and 195 conflicts; `dpll.py` does not
  finish bound 8.
- On the two satisfiable (bugged) miters learning also wins (263 vs 15,
  4,107 vs 23), so "learning only matters for proofs" would be false.

Commands: `PY gen.py adder 8 cnf/adder8.cnf; PY dpll.py cnf/adder8.cnf;
PY cdcl.py cnf/adder8.cnf; PY cdcl_vsids.py cnf/adder8.cnf`. Example
output, verbatim: `s UNSATISFIABLE` / `c decisions 822 conflicts 812
propagations ... learned 811`.

CI budget: adder 2..8 with all three solvers is about 20 s, dominated
by `dpll.py` at 8 bits (17.6 s); stop DPLL at 7 bits (3.8 s) and the
whole table is under 6 s. php 4..7 is under 5 s.

### C. Blow-up by width: adders against multipliers

C.1 Bit-blasted by the chapter's own Tseitin builder (`mul_scale.py`,
CaDiCaL 1.9.5 through python-sat; `gen.py mul N` is the miter of a
schoolbook shift-and-add multiplier, low N bits, `a*b` against `b*a`):

| width | adder miter: vars | clauses | conflicts | time | multiplier miter: vars | clauses | conflicts | time |
|---|---|---|---|---|---|---|---|---|
| 2 | 24 | 71 | 22 | 0.00 s | 17 | 44 | 9 | 0.00 s |
| 3 | 39 | 116 | 44 | 0.00 s | 40 | 115 | 34 | 0.00 s |
| 4 | 54 | 161 | 56 | 0.00 s | 75 | 226 | 123 | 0.00 s |
| 5 | 69 | 206 | 79 | 0.00 s | 122 | 377 | 555 | 0.00 s |
| 6 | 84 | 251 | 98 | 0.00 s | 181 | 568 | 2,076 | 0.04 s |
| 7 | 99 | 296 | 127 | 0.00 s | 252 | 799 | 9,707 | 0.15 s |
| 8 | 114 | 341 | 147 | 0.00 s | 335 | 1,070 | 36,350 | 0.71 s |
| 9 | 129 | 386 | 175 | 0.00 s | 430 | 1,381 | 148,242 | 4.04 s |
| 10 | 144 | 431 | 197 | 0.00 s | 537 | 1,732 | 572,683 | 18.65 s |
| 16 | 234 | 701 | 469 | 0.00 s | | | | |
| 32 | 474 | 1,421 | 883 | 0.01 s | | | | |
| 64 | 954 | 2,861 | 2,439 | 0.03 s | | | | |
| 128 | 1,914 | 5,741 | 3,173 | 0.10 s | | | | |

The multiplier formula grows quadratically (537 variables at 10 bits)
and the conflicts by about **4x per bit** (ratios 4.5, 3.7, 4.7, 3.7,
4.1, 3.9 from 5 to 10 bits). Extrapolated, not measured: 16 bits would
be of the order of 10^9 conflicts. The adder miter at 128 bits is
smaller than the multiplier miter at 7.

C.2 Other solvers on the same DIMACS files (to show it is not one
solver's weakness): `z3 -st cnf/mul8.cnf` `:sat-conflicts 30947`,
mul9 `125554`; `CADICAL cnf/mul8.cnf` (3.0.1) `conflicts: 36404`,
0.70 s; mul9 `145682`, 3.64 s.

C.3 Version sensitivity (pitfall P3): CaDiCaL 1.9.5 gives 36,350
conflicts on mul8 and CaDiCaL 3.0.1 gives 36,404; on php8, 31,719 and
51,727. Conflict counts from a production solver must not be printed
in a `run.out` unless the solver version is pinned.

### D. BDD size and variable order

D.1 Own 60-line ROBDD (`robdd.py`: unique table + memoized `apply`;
no complement edges; size = decision nodes, terminals not counted),
`bdd_own.py`:

| width n | adder carry-out, order a0 b0 a1 b1 ... | order a0..a(n-1) b0..b(n-1) | multiplier bit n-1, interleaved |
|---|---|---|---|
| 1 | 2 | 2 | 2 |
| 2 | 5 | 6 | 7 |
| 3 | 8 | 14 | 14 |
| 4 | 11 | 30 | 34 |
| 5 | 14 | 62 | 71 |
| 6 | 17 | 126 | 167 |
| 7 | 20 | 254 | 379 |
| 8 | 23 | 510 | 926 |
| 9 | 26 | 1,022 | 2,186 |
| 10 | 29 | 2,046 | 5,246 |
| 11 | 32 | 4,094 | 12,371 |
| 12 | 35 | 8,190 | 29,398 (2.7 s) |

Closed forms that fit every row: interleaved **3n - 1**, separated
**2^(n+1) - 2**. The multiplier column grows by 2.36 to 2.44 per bit
from 7 to 12 bits.

D.2 Cross-check with `dd` 0.6.0 (`dd.autoref`, which uses complemented
edges and counts its single terminal): adder 3n and 2^(n+1) - 1 up to
n = 14 (42 and 32,767); multiplier middle bit 7, 13, 30, 62, 144, 325,
777, 1,813, 4,266, 10,008, 23,334, 54,659, 127,589 for n = 2..14 (26 s
at n = 14, 3.7 million nodes in the manager). Same shape, different
constants: **node counts depend on the package's conventions** and the
chapter must say which it prints (pitfall P4).

D.3 Is it the order? Multiplier bit n-1 under three static orders
(own ROBDD) and after `dd`'s sifting:

| n | interleaved | a then b | a ascending with b descending | dd interleaved | dd after sifting |
|---|---|---|---|---|---|
| 6 | 167 | 236 | 178 | 144 | 115 |
| 7 | 379 | 567 | 422 | 325 | 307 |
| 8 | 926 | 1,367 | 974 | 777 | 468 |
| 9 | 2,186 | 3,315 | 2,382 | 1,813 | 1,356 |
| 10 | 5,246 | 8,012 | 6,002 | | |

Every order grows by more than 2x per bit. This is consistent with,
and is not a demonstration of, Bryant's lower bound (which is
asymptotic and much smaller than what is measured: 2^(n/8) is 2.4 at
n = 10).

### E. The FIFO as a formula

E.1 `informal lower` on the design alone:
`informal lower examples/ch01-what-is-dv/rtl/fifo.sv > fifo.btor2`
prints `note: the design has no assertions`; 194 lines of Btor2.
`informal info fifo.btor2`: `"nodes": 189, "inputs": 7, "states": 19,
"state_bits": 140, "array_states": 0, "bad": 0, ... "max_width": 34,
"arith_ops": 6`, operators `add 3, and 22, concat 1, const 22, eq 38,
input 7, ite 40, next 19, not 7, slice 2, slte 4, state 19, sub 3,
uext 2`. The 16x8 memory is 16 registers (128 of the 140 state bits).
`informal simp fifo.btor2`: `loaded inputs 28 latches 140 ands 937
bads 0 constraints 0` / `simplified inputs 0 latches 0 ands 0 ...`:
with no property, nothing is in any cone of influence and everything
is removed. (That line is a compact illustration of cone of influence;
the term itself is the techniques chapter's.)

E.2 A property and a reset written as hardware (`fifo_bmc.sv`, in the
appendix): a wrapper that instantiates the FIFO, holds `rst_n` low for
the first cycle by `assume (rst_n == started)` with `logic started =
1'b0`, keeps the contract's 5-bit `occ`, and asserts `!rst_n || !full
|| occ == 16`. `informal lower` needs this because it does no clock
or reset setup and reads only *immediate* assertions (FINDINGS C.9).

```
$ informal lower fifo_bmc.sv --top fifo_bmc > fifo_bmc.btor2     # 225 lines
$ informal info fifo_bmc.btor2    # "nodes": 219, "inputs": 7, "states": 21,
                                  # "state_bits": 146, "bad": 1, "constraints": 1
$ informal simp fifo_bmc.btor2
loaded    inputs 28 latches 146 ands 992 bads 1 constraints 1 (0.4 ms)
simplified inputs 3 latches 10 ands 102 bads 1 constraints 1 (0.0 ms, 0 constant latches)
$ informal simp fifo_bmc.btor2 --aag > fifo_bmc.aag      # header: aag 115 3 10 0 102 1 1
$ informal check --engines examples/mk/informal-engines.toml --only informal-bmc fifo_bmc.btor2
  informal-bmc   unsafe         14 ms
UNSAFE (by informal-bmc, depth 16)
...
@0 fifo_bmc.rst_n=0 fifo_bmc.wr_en=0 fifo_bmc.rd_en=1
@1 fifo_bmc.rst_n=1 fifo_bmc.wr_en=1 fifo_bmc.rd_en=1
@2 fifo_bmc.rst_n=1 fifo_bmc.wr_en=1 fifo_bmc.rd_en=0
```

(exit status 10.) 992 ANDs and 146 latches become 102 ANDs and 10
latches: the memory, `wr_ptr`, `rd_ptr` and `wr_data` do not reach the
property. The same reduction on the model the Chapter 9 shell run wrote
for `FullBackward_A` (`fifo-formal/build/informal/prop_2.btor2`):
`loaded inputs 28 latches 157 ands 1052 bads 1 constraints 1` /
`simplified inputs 3 latches 12 ands 106 bads 1 constraints 1`.

E.3 Bit-level unrolling by hand (`bmc_aag.py`, 97 lines, in the
appendix; python-sat's CaDiCaL here, any DIMACS solver works):

```
$ PY bmc_aag.py fifo_bmc.aag 20
model: 3 inputs, 10 latches, 102 ANDs
bound   vars  clauses  result  conflicts
    0    115      308  UNSAT          0
    1    220      615  UNSAT          0
   ...
   15   1690     4913  UNSAT        213
   16   1795     5220  SAT          370
```

105 variables and 307 clauses per frame (102 ANDs x 3 clauses + 1
constraint unit); latches cost nothing because frame t+1's latch *is*
frame t's next-state literal. The whole run is 0.12 s. On the shell's
`prop_2` model the same script gives SAT at bound 16 as well (1,863
variables, 5,424 clauses). The simplified AIGER has no symbol table,
so inputs print as `in0..in2`; from the trace `in0` is `rst_n` (0 in
frame 0 only), `in1` `wr_en`, `in2` `rd_en`.

E.4 Word-level unrolling by hand (`unroll_z3.py`, 70 lines): state
`(count, occ)` after reset, `step()` transcribed from the RTL's `case`,
`bad = full && occ != 16`. Output: `bound 0: unsat` ... `bound 14:
unsat`, `bound 15: sat -- full with occ != 16 after 15 cycles`, 0.35 s.
With `fixed` (5-bit count, full at 16): `no counterexample within 20
cycles of reset` in 0.6 s, and within 40 cycles in **9.2 s**: each
bound re-solves a longer formula. A bound is not a proof, and the cost
of the next bound grows; that is the hand-off to the next chapter.

The witness is not unique (in frame 0 `rd_en` is free because the FIFO
is empty), so a printed input trace can change with the solver version
(pitfall P5).

E.5 A model small enough to print whole (`counter.sv`, a 3-bit counter
that stops at 6 where its assertion says 5): `informal lower` gives 20
lines of Btor2 (reproduced in the appendix), `informal simp`: `loaded
inputs 2 latches 3 ands 23 bads 1 ...` / `simplified inputs 1 latches 3
ands 19 bads 1 ...`, `informal check ... --only informal-bmc`: `UNSAFE
(by informal-bmc, depth 6)` with `@0 counter.en=1` ... `@6
counter.en=1`; `bmc_aag.py counter.aag`: UNSAT for bounds 0..5, SAT at
6 (141 variables, 400 clauses). Its initial value comes from a
declaration initializer (`logic [2:0] count = 3'd0;`), which becomes
the Btor2 `init` line; Verilator's lint needs `-Wno-PROCASSINIT`
(already in `informal.mk`'s default flags).

### F. Pigeonhole against production solvers (`php_scale.py`)

| holes | vars | clauses | MiniSat 2.2 conflicts | time | CaDiCaL 1.9.5 conflicts | time |
|---|---|---|---|---|---|---|
| 4 | 20 | 45 | 29 | 0.00 s | 32 | 0.00 s |
| 5 | 30 | 81 | 201 | 0.00 s | 133 | 0.00 s |
| 6 | 42 | 133 | 2,498 | 0.01 s | 1,044 | 0.01 s |
| 7 | 56 | 204 | 11,530 | 0.04 s | 7,130 | 0.07 s |
| 8 | 72 | 297 | 39,063 | 0.21 s | 31,719 | 0.41 s |
| 9 | 90 | 415 | 510,308 | 2.91 s | 267,023 | 3.95 s |
| 10 | 110 | 561 | 10,712,415 | 112.59 s | 2,227,032 | 43.18 s |

(11 holes did not finish for MiniSat inside the 600 s budget of the
run.) `z3 -st cnf/php9.cnf`: `:sat-conflicts 37261`; z3's SAT core is
an order of magnitude better here, so "all solvers take the same time"
must not be claimed; "all of them grow by a large factor per hole" is
what was measured. CI: 4..9 holes, about 8 s.

### G. Word level against bits in z3 (`word_vs_bits.py 100 11`)

`rewrite` is `a*b != b*a`; `word` is `shift_add(a,b) != shift_add(b,a)`
with `shift_add` = sum over i of `If(b[i], a << i, 0)`, both through
`z3.SolverFor("QF_BV")`; `bits` is the second formula through
`Then("simplify","bit-blast","tseitin-cnf")` and CaDiCaL.

| width | rewrite | word | bits | conflicts (bits) |
|---|---|---|---|---|
| 4 | unsat 0.00 s | unsat 0.01 s | unsat 0.00 s | 136 |
| 6 | unsat 0.00 s | unsat 0.02 s | unsat 0.02 s | 1,529 |
| 7 | unsat 0.00 s | unsat 0.13 s | unsat 0.11 s | 5,416 |
| 8 | unsat 0.00 s | unsat 0.84 s | unsat 0.53 s | 23,597 |
| 9 | unsat 0.00 s | unsat 6.11 s | unsat 2.31 s | 86,741 |
| 10 | unsat 0.00 s | unsat 31.38 s | unsat 12.93 s | 346,588 |
| 11 | unsat 0.00 s | unknown (100 s limit) | unsat 74.05 s | 1,518,378 |
| 32 | unsat 0.00 s | | | |
| 64 | unsat 0.00 s | | | |

Also 0.00 s at 64 bits at the word level: `a + b != b + a` and
`a*(b+c) != a*b + a*c`. `z3.simplify(a*b != b*a)` prints `False`: the
rewriter alone decides it. `Tactic("simplify")` does not by itself
rewrite the distributive law; the `QF_BV` solver's preprocessing does.
The size columns of z3's CNF export are **not** recorded here because
two constructions of the same width-8 formula exported 791 and 834
clauses (pitfall P6).

### H. Random 3-SAT near the threshold (`phase.py 150 50`, 6.2 s)

150 variables, 50 instances per ratio (Python `random.Random(seed)`,
seeds 0..49; three distinct variables per clause), MiniSat 2.2:

| clauses/variables | satisfiable | median conflicts | max conflicts |
|---|---|---|---|
| 3.0 | 50/50 | 4 | 70 |
| 3.4 | 50/50 | 24 | 229 |
| 3.8 | 50/50 | 127 | 2,079 |
| 4.0 | 48/50 | 525 | 15,911 |
| 4.2 | 30/50 | 2,307 | 13,456 |
| 4.4 | 12/50 | 2,693 | 8,498 |
| 4.6 | 3/50 | 2,190 | 5,451 |
| 4.8 | 0/50 | 1,492 | 3,718 |
| 5.0 | 0/50 | 1,187 | 2,357 |
| 5.4 | 0/50 | 763 | 1,681 |
| 6.0 | 0/50 | 478 | 706 |

(rows at 3.2, 3.6, 5.2, 5.6, 5.8 omitted here; the script prints all
sixteen.) Half the instances are satisfiable between 4.2 and 4.4, and
the median cost peaks there. The instances are reproducible because
Python's Mersenne Twister is specified; the conflict column is
MiniSat's and would have to come from the book's `cdcl_vsids.py` to be
version-proof (not yet run at 150 variables; expect seconds per
instance in pure Python, so use 50 to 75 variables in CI).

### I. Which runs are fit for CI

| example | deterministic output? | time | needs |
|---|---|---|---|
| A full adder by hand, `dpll.py` | yes | < 0.1 s | Python |
| A by tool (Yosys AIG, ABC strash) | yes for Yosys 0.68; pin | 1 s | yosys, yosys-abc |
| B three solvers, adder 2..7, php 4..7, fifo_k16 | yes (own solvers) | < 10 s | Python |
| C adder vs multiplier, widths to 8 (9: +4 s) | verdicts yes; conflicts only with a pinned solver | 1 s (5 s) | z3 or own `cdcl_vsids.py` (smaller widths) |
| D BDD sizes, n to 10 or 11 | yes (own ROBDD) | 0.4 s (1.1 s) | Python |
| E `informal lower/info/simp/check` | yes after dropping the `(x ms)` fields | < 1 s | informal (skipped in CI: the workflow does not install it) |
| E `bmc_aag.py` on a checked-in `.aag` | verdict per bound yes | 0.2 s | Python + a solver (own `cdcl.py` works: 0.09 s at bound 16) |
| E `unroll_z3.py bug` | verdict lines yes; witness no | 0.4 s | z3-solver |
| F pigeonhole 4..9 | verdicts yes; counts need a pin | 8 s | z3 or own solver to 7 holes |
| G word vs bits to width 8 (9: +9 s) | verdicts yes; times no | 2 s (11 s) | z3-solver |
| H phase transition | satisfiable column yes for any complete solver; conflicts need own solver | 6 s with MiniSat | Python (+ solver) |

## 2. Source table

Marks. **[V-CR]**: authors, title, venue, volume and pages checked
against the publisher's Crossref record on 2026-11-15 (metadata only;
the paper's text was not read unless a second mark says so). Crossref
records of IEEE papers carry initials only, so a given name printed
here for such a paper is **not** verified unless noted. **[V-TEXT:
what]**: the named passage was read in the document itself or its
publisher page. **[U]**: unverified; from memory; check before
citing. Web access went through a fetch proxy; `doi.org`, `dblp.org`
and `fmv.jku.at` were not reachable with curl, some through the proxy.

### 2.1 Logic and encoding

| topic | source | status |
|---|---|---|
| Algebra of logic | George Boole, *An Investigation of the Laws of Thought, on Which Are Founded the Mathematical Theories of Logic and Probabilities*, London: Walton and Maberly, 1854. Project Gutenberg ebook 15114, https://www.gutenberg.org/ebooks/15114 | [U] record seen in a search listing only; the text was not opened. Do not quote. |
| Boolean algebra as circuit algebra | Claude E. Shannon, "A symbolic analysis of relay and switching circuits", *Transactions of the American Institute of Electrical Engineers* 57(12):713-723, 1938. DOI 10.1109/T-AIEE.1938.5057767 | [V-CR] |
| Linear-size CNF by naming subformulas | G. S. Tseitin, "On the Complexity of Derivation in Propositional Calculus", in *Automation of Reasoning 2: Classical Papers on Computational Logic 1967-1970* (J. Siekmann, G. Wrightson, eds.), Springer, 1983, pp. 466-483. DOI 10.1007/978-3-642-81955-1_28. Original: Russian, 1968, in *Studies in Constructive Mathematics and Mathematical Logic, Part II* (A. O. Slisenko, ed.) | reprint [V-CR] (author, title, book, pages); editors' names, the 1968 original and its English 1970 translation pages [U]. Cite the 1983 reprint and say "first published in Russian in 1968". |
| Polarity-aware variant (one direction of each definition is enough) | David A. Plaisted, Steven Greenbaum, "A Structure-preserving Clause Form Translation", *Journal of Symbolic Computation* 2(3):293-304, 1986. DOI 10.1016/S0747-7171(86)80028-1 | [V-CR]; the content claim [U] |
| SAT is NP-complete | Stephen A. Cook, "The complexity of theorem-proving procedures", *Proc. Third Annual ACM Symposium on Theory of Computing (STOC '71)*, pp. 151-158, 1971. DOI 10.1145/800157.805047 | [V-CR]; [V-TEXT: summary and Theorem 1 read in a course-hosted scan]. Theorem 1 is stated for **DNF tautologies**, not for CNF satisfiability: "If a set S of strings is accepted by some nondeterministic Turing machine within polynomial time, then S is P-reducible to {DNF tautologies}." The chapter must say "Cook's theorem, in today's terms" if it says SAT. |
| DIMACS CNF format | No primary document was located and read. | [U] Describe the format from the example files; cite a solver's documentation only if one is read. |

### 2.2 SAT solving

| topic | source | status |
|---|---|---|
| Resolution-based procedure | Martin Davis, Hilary Putnam, "A Computing Procedure for Quantification Theory", *Journal of the ACM* 7(3):201-215, 1960. DOI 10.1145/321033.321034 | [V-CR] |
| Backtracking search with unit propagation (DPLL) | Martin Davis, George Logemann, Donald Loveland, "A machine program for theorem-proving", *Communications of the ACM* 5(7):394-397, 1962. DOI 10.1145/368273.368557 | [V-CR] |
| Clause learning, implication graph, non-chronological backtracking | J. P. Marques Silva, K. A. Sakallah, "GRASP - A new search algorithm for satisfiability", *Proc. International Conference on Computer Aided Design (ICCAD)*, pp. 220-227, 1996. DOI 10.1109/ICCAD.1996.569607. Journal: J. P. Marques-Silva, K. A. Sakallah, "GRASP: a search algorithm for propositional satisfiability", *IEEE Transactions on Computers* 48(5):506-521, 1999. DOI 10.1109/12.769433 | [V-CR] both; given names (Joao, Karem) [U]; note the 1996 record prints the surname without a hyphen |
| Two watched literals, VSIDS | Matthew W. Moskewicz, Conor F. Madigan, Ying Zhao, Lintao Zhang, Sharad Malik, "Chaff: Engineering an Efficient SAT Solver", *Proc. 38th Design Automation Conference (DAC)*, pp. 530-535, 2001. DOI 10.1145/378239.379017 | [V-CR] (Crossref splits the title as "Chaff" plus subtitle); [V-TEXT: abstract, sections 2-3 in a course-hosted copy]: abstract claims "one to two orders of magnitude performance improvement on difficult SAT benchmarks" over other solvers "including GRASP and SATO"; section 2 says more than 90% of run time "in most cases" is spent in BCP; VSIDS is "Variable State Independent Decaying Sum"; the scheme is called "two literal watching". Those are the authors' claims about their benchmarks. |
| First-UIP learning scheme | Lintao Zhang, C. F. Madigan, M. H. Moskewicz, S. Malik, "Efficient conflict driven learning in a Boolean satisfiability solver", *IEEE/ACM ICCAD 2001*, pp. 279-285. DOI 10.1109/ICCAD.2001.968634 | [V-CR]; that the paper finds first-UIP best [U] |
| A small, readable CDCL solver | Niklas Een, Niklas Sorensson, "An Extensible SAT-solver", in *Theory and Applications of Satisfiability Testing (SAT 2003)*, LNCS 2919, pp. 502-518, Springer, 2004. DOI 10.1007/978-3-540-24605-3_37 | [V-CR] (LNCS volume number [U]) |
| CDCL survey chapter | Joao Marques-Silva, Ines Lynce, Sharad Malik, "Conflict-Driven Clause Learning SAT Solvers", chapter 4 of *Handbook of Satisfiability*, 2nd ed., IOS Press, 2021. DOI 10.3233/FAIA200987 | [V-CR] (no pages in the record) |
| Handbook | Armin Biere, Marijn Heule, Hans van Maaren, Toby Walsh (eds.), *Handbook of Satisfiability*, second edition, Frontiers in Artificial Intelligence and Applications 336, IOS Press, 2021. DOI 10.3233/FAIA336 | editors and "second edition" [V-TEXT: IOS Press page]; volume 336 from the DOI and a dblp URL; ISBN 978-1-64368-160-3 seen only in a bookseller URL [U]; chapter page ranges [U] |
| Preprocessing (variable elimination, subsumption) | Niklas Een, Armin Biere, "Effective Preprocessing in SAT Through Variable and Clause Elimination", SAT 2005, LNCS, pp. 61-75. DOI 10.1007/11499107_5 | [V-CR] |
| CaDiCaL | Armin Biere, Tobias Faller, Katalin Fazekas, Mathias Fleury, Nils Froleyks, Florian Pollitt, "CaDiCaL 2.0", in *Computer Aided Verification (CAV 2024)*, LNCS, pp. 133-152, 2024. DOI 10.1007/978-3-031-65627-9_7 | [V-CR] (LNCS volume [U]); the binary measured here is 3.0.1 |
| Checkable proofs of unsatisfiability | Nathan Wetzler, Marijn J. H. Heule, Warren A. Hunt Jr., "DRAT-trim: Efficient Checking and Trimming Using Expressive Clausal Proofs", SAT 2014, LNCS, pp. 422-429. DOI 10.1007/978-3-319-09284-3_31 | [V-CR]. Only needed for one sentence on why an "unsat" can be trusted (FINDINGS says InFormal's verdicts are certified). |
| What learning adds, formally | Paul Beame, Henry Kautz, Ashish Sabharwal, "Towards Understanding and Harnessing the Potential of Clause Learning", *Journal of Artificial Intelligence Research* 22:319-351, 2004. DOI 10.1613/jair.1410; Knot Pipatsrisawat, Adnan Darwiche, "On the power of clause-learning SAT solvers as resolution engines", *Artificial Intelligence* 175(2):512-525, 2011. DOI 10.1016/j.artint.2010.10.002 | [V-CR] both (Beame/Kautz/Sabharwal given names [U]); the statements (DPLL corresponds to tree-like resolution; clause learning with restarts simulates general resolution polynomially) [U]: read before stating |
| Textbook treatment | Daniel Kroening, Ofer Strichman, *Decision Procedures: An Algorithmic Point of View*, 2nd ed., Texts in Theoretical Computer Science, Springer, 2016. DOI 10.1007/978-3-662-50497-0. Chapters: 2 "Decision Procedures for Propositional Logic", 6 "Bit Vectors", 11 "Propositional Encodings" | [V-TEXT: Springer page, edition, series and table of contents] |
| Encyclopedic treatment | Donald E. Knuth, *The Art of Computer Programming, Volume 4B: Combinatorial Algorithms, Part 2*, Addison-Wesley, 2022 (section 7.2.2.2, Satisfiability) | [U] further reading only |

### 2.3 Why it is hard

| topic | source | status |
|---|---|---|
| Pigeonhole needs exponentially long resolution proofs | Armin Haken, "The intractability of resolution", *Theoretical Computer Science* 39:297-308, 1985. DOI 10.1016/0304-3975(85)90144-6 | [V-CR]; the paper was **not** read. A later paper (Sam Buss, Toniann Pitassi, "Resolution and the Weak Pigeonhole Principle") describes it as "the first superpolynomial lower bound on the length of resolution refutations" and as a size lower bound of 2^(epsilon n) for a constant epsilon [V-TEXT of that secondary description]. State the result as "exponential in n"; give no constant. |
| Another hard family (parity on graphs) | Alasdair Urquhart, "Hard examples for resolution", *Journal of the ACM* 34(1):209-219, 1987. DOI 10.1145/7531.8928 | [V-CR]; optional |
| Hard random instances at a critical ratio | David G. Mitchell, Bart Selman, Hector J. Levesque, "Hard and Easy Distributions of SAT Problems", *Proc. AAAI-92*, pp. 459-465, 1992. https://cdn.aaai.org/AAAI/1992/AAAI92-071.pdf | [V-TEXT: paper PDF, OCR]: 50% satisfiable "when the number of clauses is about 4.3 times the number of variables"; the hardest area "is near the point where 50% of the formulas are satisfiable"; procedure: Davis-Putnam; curves for 20, 40 and 50 variables; crossover 4.55 at 20 variables, 4.3 at 50 and at 140. Pages 459-465 from an index (mlanthology.org), not from the PDF. The AAAI award page prints the title as "Distribution" (singular). |
| Crossover measured more finely | James M. Crawford, Larry D. Auton, "Experimental results on the crossover point in random 3-SAT", *Artificial Intelligence* 81(1-2):31-57, 1996. DOI 10.1016/0004-3702(95)00046-1 | [V-CR]; any value such as 4.26 [U] |
| OBDD lower bound for multiplication | R. E. Bryant, "On the complexity of VLSI implementations and graph representations of Boolean functions with application to integer multiplication", *IEEE Transactions on Computers* 40(2):205-213, 1991. DOI 10.1109/12.73590 | [V-CR]; the bound is known here only through Woelfel's abstract (next row) |
| Stronger bound, and an upper bound | Philipp Woelfel, "Bounds on the OBDD-size of integer multiplication via universal hashing", *Journal of Computer and System Sciences* 71(4):520-534, 2005. DOI 10.1016/j.jcss.2005.05.004 | [V-CR]; [V-TEXT: abstract]: Bryant showed that any OBDD for the middle bit of n-bit multiplication "requires at least 2^(n/8) nodes"; this paper proves "essentially 2^(n/2)/61" and an upper bound of (7/3)*2^(4n/3). (Exponents reconstructed from a text extraction that lost superscripts: check on the publisher page.) |
| Finding the best order is itself hard | B. Bollig, I. Wegener, "Improving the variable ordering of OBDDs is NP-complete", *IEEE Transactions on Computers* 45(9):993-1002, 1996. DOI 10.1109/12.537122 | [V-CR]; given names (Beate, Ingo) [U] |
| Multipliers and SAT: **no lower bound; the opposite** | Paul Beame, Vincent Liew, "Towards Verifying Nonlinear Integer Arithmetic", arXiv:1705.04302 (version of 2018-08-13); conference version CAV 2017 and journal version in *Journal of the ACM* [U for both venues] | [V-TEXT: arXiv abstract]: polynomial-size regular resolution proofs exist for degree-2 identities (commutativity among them) on array, diagonal and Booth multipliers, n^(O(log n)) on Wallace trees; "Such short proofs were conjectured not to exist." The paper reports that solvers nevertheless "perform badly" and cites a report that no known CNF technique handles commutativity above 16 bits. **The chapter must not say multiplier miters are provably hard for SAT.** They are hard for today's solvers; short proofs exist and are not found. |
| What is done instead | Daniela Kaufmann, Armin Biere, Manuel Kauers, "Verifying Large Multipliers by Combining SAT and Computer Algebra", *Formal Methods in Computer Aided Design (FMCAD 2019)*, pp. 28-36. DOI 10.23919/FMCAD.2019.8894250 | [V-CR]; content [U]; one forward-looking sentence at most |
| Complexity of bit-vector logic | Gergely Kovasznai, Andreas Frohlich, Armin Biere, "Complexity of Fixed-Size Bit-Vector Logics", *Theory of Computing Systems* 59(2):323-376, 2016. DOI 10.1007/s00224-015-9653-1 | [V-CR]; the result (quantifier-free bit-vectors with binary-encoded widths are NEXPTIME-complete) [U]: read before stating, or leave out |

### 2.4 BDDs

| topic | source | status |
|---|---|---|
| Binary decision programs/diagrams before Bryant | Akers, "Binary Decision Diagrams", *IEEE Transactions on Computers* C-27(6):509-516, 1978. DOI 10.1109/TC.1978.1675141 | [V-CR] (the record has no given name; Sheldon B. [U]) |
| Reduced ordered BDDs, canonicity, apply | Randal E. Bryant, "Graph-Based Algorithms for Boolean Function Manipulation", *IEEE Transactions on Computers* C-35(8):677-691, August 1986. DOI 10.1109/TC.1986.1676819 | [V-CR] + given name from a bibliography page; the paper's own examples (order sensitivity, multiplication) were **not** read: [U] for any statement of what the paper shows beyond its title |
| Unique table, computed table, complement edges | Karl S. Brace, Richard L. Rudell, Randal E. Bryant, "Efficient implementation of a BDD package", *Proc. 27th ACM/IEEE Design Automation Conference (DAC '90)*, pp. 40-45, 1990. DOI 10.1145/123186.123222 | [V-CR]; content [U] |
| Symbolic model checking with BDDs | J. R. Burch, E. M. Clarke, K. L. McMillan, D. L. Dill, L. J. Hwang, "Symbolic model checking: 10^20 states and beyond", *Proc. Fifth Annual IEEE Symposium on Logic in Computer Science (LICS)*, pp. 428-439, 1990. DOI 10.1109/LICS.1990.113767. Journal: *Information and Computation* 98(2):142-170, 1992. DOI 10.1016/0890-5401(92)90017-A | [V-CR] both; given names (Jerry R. Burch, Edmund M. Clarke, Kenneth L. McMillan, David L. Dill, L. James Hwang) [V-TEXT: LICS archive page]. The abstract (read in paraphrase) describes a mu-calculus model checker on Bryant's BDDs and a synchronous pipeline example; **where the figure 10^20 comes from in the paper was not read**: use it only as the title. |
| Dynamic reordering (sifting) | Richard Rudell, "Dynamic variable ordering for ordered binary decision diagrams", ICCAD 1993 | [U] entirely |

### 2.5 AIGs, formats, bounded model checking

| topic | source | status |
|---|---|---|
| AIGs with structural hashing for verification | A. Kuehlmann, V. Paruthi, F. Krohm, M. K. Ganai, "Robust Boolean reasoning for equivalence checking and functional property verification", *IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems* 21(12):1377-1394, 2002. DOI 10.1109/TCAD.2002.804386 | [V-CR]; given names [U]; content [U] |
| The word "miter" | D. Brand, "Verification of large synthesized designs", *Proc. ICCAD 1993*, pp. 534-537. DOI 10.1109/ICCAD.1993.580110 | [V-CR]; that this paper introduces the term [U]: say "a miter" without attributing the coinage unless read |
| AIG rewriting | A. Mishchenko, S. Chatterjee, R. Brayton, "DAG-aware AIG rewriting: a fresh look at combinational logic synthesis", DAC 2006. DOI 10.1145/1146909.1146995 | [U]: the Crossref lookup failed twice |
| AIGER format | Armin Biere, "The AIGER And-Inverter Graph (AIG) Format Version 20071012", FMV Reports Series, Technical Report 07/1, Institute for Formal Models and Verification, Johannes Kepler University, Linz, 2007. https://fmv.jku.at/papers/Biere-FMV-TR-07-1.pdf (text form: https://fmv.jku.at/aiger/FORMAT.aiger) | [V-TEXT: the format text and the institute's report list]: header `aag M I L O A`; "The least significant bit of the unsigned word encoding a literal is the sign bit"; "The constant FALSE is represented by the literal '0', the constant TRUE by '1'." |
| AIGER 1.9 (bad states, constraints, reset values) | Armin Biere, Keijo Heljanko, Siert Wieringa, "AIGER 1.9 And Beyond", FMV Reports Series, Technical Report 11/2, Johannes Kepler University, Linz, July 2011. https://fmv.jku.at/papers/BiereHeljankoWieringa-FMV-TR-11-2.pdf | [V-TEXT: report]: header "may now be extended with four more decimal numbers" B C J F (bad, invariant constraints, justice, fairness); a latch line may carry a third literal: 0, 1, or the latch's own literal for "uninitialized". This is exactly the form `informal simp --aag` printed (`aag 115 3 10 0 102 1 1`, latch lines such as `8 218 8`). |
| Btor2 | Aina Niemetz, Mathias Preiner, Clifford Wolf, Armin Biere, "Btor2, BtorMC and Boolector 3.0", in *Computer Aided Verification (CAV 2018)*, LNCS 10981, pp. 587-595, Springer, 2018. DOI 10.1007/978-3-319-96145-3_32 (open access, CC BY 4.0) | [V-CR]; [V-TEXT: abstract on the publisher page]: "a word-level model checking format", "a sorted extension of the word-level format Btor", uses "design principles from the bit-level format Aiger" and the semantics of SMT-LIB bit-vectors with arrays |
| Bounded model checking | Armin Biere, Alessandro Cimatti, Edmund Clarke, Yunshan Zhu, "Symbolic Model Checking without BDDs", in *Tools and Algorithms for the Construction and Analysis of Systems (TACAS 1999)*, LNCS 1579, pp. 193-207, Springer, 1999. DOI 10.1007/3-540-49059-0_14 | [V-CR] (volume number [U]); [V-TEXT: paper PDF]: abstract, p. 193: "We introduce a bounded model checking procedure for LTL which reduces model checking to propositional satisfiability."; section 4, p. 200, Definition 10: the path formula is the initial-state predicate on s0 conjoined with T(s_i, s_i+1) for i from 0 to k-1; section 6: solvers were SATO and PROVER (Stalmarck's method); p. 194: "We give examples in which SAT based model checking significantly outperforms BDD based model checking." |
| Same, for a design audience | A. Biere, A. Cimatti, E. M. Clarke, M. Fujita, Y. Zhu, "Symbolic model checking using SAT procedures instead of BDDs", *Proc. 36th Design Automation Conference (DAC)*, pp. 317-320, 1999. DOI 10.1145/309847.309942 | [V-CR] |

### 2.6 SMT and bit-vectors

| topic | source | status |
|---|---|---|
| SMT-LIB language | Barrett, Fontaine, Tinelli, *The SMT-LIB Standard: Version 2.6* (already in `refs.bib` as `barrett2017smtlib26`) | as recorded in `refs.bib`. The SMT-LIB site now says version 2.7 (released 2024-07-21, per the theory page); cite 2.6 for what was read, or read 2.7. |
| Bit-vector theory | SMT-LIB theory `FixedSizeBitVectors`, written by Clark Barrett, Pascal Fontaine, Silvio Ranise and Cesare Tinelli; theory date 2010-05-02, last updated 2025-09-09. https://smt-lib.org/theories-FixedSizeBitVectors.shtml | [V-TEXT: page]: `bvadd` and `bvmul` are defined through `nat2bv[m](bv2nat(s) op bv2nat(t))`, i.e. the result modulo 2^m; `bvudiv` by zero returns all ones and `bvurem` by zero returns the dividend. (The last fact is a good Pitfall: SystemVerilog gives X.) |
| DPLL(T) | Robert Nieuwenhuis, Albert Oliveras, Cesare Tinelli, "Solving SAT and SAT Modulo Theories: From an abstract Davis-Putnam-Logemann-Loveland procedure to DPLL(T)", *Journal of the ACM* 53(6):937-977, 2006. DOI 10.1145/1217856.1217859 | [V-CR] (the record's title is the part before the colon; subtitle [U]). One sentence at most: bit-vectors are mostly solved eagerly, not by DPLL(T). |
| SMT survey chapter | Clark Barrett, Roberto Sebastiani, Sanjit A. Seshia, Cesare Tinelli, "Satisfiability Modulo Theories", chapter 33 of *Handbook of Satisfiability*, 2nd ed., 2021. DOI 10.3233/FAIA201017 | [V-CR] |
| Z3 | de Moura and Bjorner, TACAS 2008 (in `refs.bib` as `demoura2008z3`); repository entry `z3-repo`; wheel `z3-solver-pypi` | existing entries; not re-checked here |
| Bit-vector solvers that bit-blast | Aina Niemetz, Mathias Preiner, "Bitwuzla", CAV 2023, LNCS, pp. 3-17. DOI 10.1007/978-3-031-37703-7_1 | [V-CR]; FINDINGS says InFormal's word-level path needs Bitwuzla, which is not built here: name it, run nothing on it |

### 2.7 Anchors asked for and their outcome

Confirmed as expected (metadata): Shannon 1938; Davis-Putnam 1960;
Davis-Logemann-Loveland 1962; Cook 1971; GRASP 1996 and 1999; Chaff
2001; MiniSat (the paper is in the SAT 2003 proceedings, published
2004); Bryant 1986; Burch et al. 1990 and 1992; Biere et al. 1999;
Kuehlmann et al. 2002; AIGER (two reports); Btor2 2018; CaDiCaL (CAV
2024, "CaDiCaL 2.0"); Handbook 2nd ed. (2021); Kroening and Strichman
2nd ed. (2016); Haken 1985; Bryant 1991; Mitchell, Selman, Levesque
1992. Corrections to the expected list: (1) "Tseitin 1968" is citable
as the 1983 Springer reprint; the 1968 original was not seen. (2)
"multiplier hardness for SAT" has **no** primary source as a theorem;
the primary literature says the reverse (Beame and Liew). (3) Boole is
unverified. (4) Cook's theorem is stated for DNF tautologies.

## 4. Constraints for the drafter

### 4.1 Must not be claimed (unverified or false)

1. **"Multipliers are provably hard for SAT."** False as a theorem:
   Beame and Liew give polynomial-size resolution proofs for
   commutativity on array multipliers. Say what was measured: a
   production CDCL solver's conflicts grew about fourfold per bit on
   the chapter's miter, and the BDD bound (Bryant 1991) is a theorem
   about BDDs only.
2. **Any constant for Haken's bound**, or that the measured pigeonhole
   growth "is" the bound. The theorem is about resolution proof size;
   the measurement is about three solvers. The link is that a CDCL
   run that answers "unsat" yields a resolution proof (state this only
   with a source read for it: Beame, Kautz, Sabharwal 2004 or the
   Handbook's CDCL chapter).
3. **The measured BDD growth "confirms" 2^(n/8).** At n = 10 the bound
   is 2.4 nodes. The measurement shows growth of about 2.4x per bit to
   n = 12 (own package) and n = 14 (`dd`); it is an observation.
4. **Anything about what Bryant 1986, GRASP, MiniSat, Kuehlmann et
   al., Brace et al. or Tseitin's paper contain** beyond title-level
   attribution, until read. In particular do not attribute the
   interleaved/separated adder example to Bryant 1986 without reading
   it, and do not attribute the word "miter" to Brand 1993.
5. **"10^20 states"** as a fact about a design: it is the title of
   Burch et al.; where the number arises was not read.
6. **Cook's theorem "for SAT"** without the qualifier: the 1971
   theorem is about DNF tautologies (verbatim in section 2.1).
7. **A threshold value more precise than "about 4.3"** (the value in
   Mitchell et al.); 4.26/4.267 are from sources not read.
8. **"z3 bit-blasts bit-vectors"** as the whole story. Measured: it
   rewrites first (0.00 s at 64 bits for three identities) and falls
   to search when no rewrite fires. Do not describe z3's internals
   beyond what the measurement shows; the Z3 paper in `refs.bib` was
   not re-read for this.
9. **"SMT is faster than SAT" or the reverse.** In G the word-level
   route was slower than CNF + CaDiCaL at every width from 8 to 11
   (0.84 vs 0.53 s, 6.1 vs 2.3, 31 vs 13, >100 vs 74) on one formula
   family; that is one family, one version.
10. **Complexity of bit-vector logic** (NEXPTIME-completeness): not
    read; leave out or read Kovasznai et al. first.
11. **InFormal internals**: which SAT solver each engine calls, what
    `simp` does beyond the sizes it prints (the reduction 992 to 102
    ANDs is measured; calling it "cone of influence plus structural
    hashing" is an inference from the FIFO case, where every removed
    part is outside the property's support, and from the full adder,
    where two duplicate ANDs disappear: phrase it as such).
12. **Quotations.** Verbatim text in hand exists only for the strings
    in quotation marks in section 2 (Cook Theorem 1 and summary; Chaff
    abstract/section phrases; Mitchell et al. three phrases; AIGER two
    sentences; AIGER 1.9 one phrase; Btor2 abstract phrases; BMC paper
    three sentences; Woelfel abstract phrases with reconstructed
    exponents; Beame-Liew abstract phrases). One OCR caveat: the
    Mitchell et al. text was read through OCR ("hardest urea for
    sutisfiubility"); re-read the PDF page before quoting it.

### 4.2 Version pins

Python 3.13.18 here, 3.12 in CI; z3-solver 5.4.1.0; Yosys 0.68;
InFormal 0.1.0 at 5114330; Verilator 5.052 (lint); CaDiCaL 3.0.1
binary (only at `/opt/informal-tools/cadical/build/cadical`, not on
the PATH, not in CI); python-sat 1.9.dev22 and dd 0.6.0 (research
only). The CI workflow does not install `informal`, Yosys' ABC or
CaDiCaL; examples that need `informal` already skip there
(`REQUIRES := informal`).

### 4.3 Pitfalls found

- **P1. Which Python.** With the documented PATH (`venv/bin` last),
  `python3` is `/usr/local/bin/python3`, which has neither `z3` nor
  cocotb; `python.mk` runs `python3`. The scripts here ran under
  `/opt/dvtools/venv/bin/python`. In CI `python3` has `z3-solver`. The
  examples must either run under `scripts/check-examples.sh`'s
  environment (it wraps in `conda run -n dvbook` when that exists) or
  guard the import and print a `skipped:` line; decide once, in
  `python.mk`, not per example. A z3-free path exists for every
  example except G and E.4.
- **P2. `informal check` and `informal bench` need `--engines`**: the
  default `config/engines.toml` is relative to the current directory
  and its absence is a Rust backtrace, not a message. Use
  `--engines $(EXAMPLES_ROOT)mk/informal-engines.toml`.
- **P3. Solver statistics are version facts.** CaDiCaL 1.9.5 vs 3.0.1:
  36,350 vs 36,404 conflicts (mul8), 31,719 vs 51,727 (php8). z3's
  `:sat-conflicts` on php8 is 7,010. Print production-solver counts in
  a chapter table with the version in the caption, never in a
  `run.out` that CI diffs; `run.out` may carry the book solvers'
  counts, which are exact.
- **P4. BDD node counts depend on the package.** Own ROBDD (no
  complement edges, terminals not counted): 3n-1 and 2^(n+1)-2. `dd`:
  3n and 2^(n+1)-1. Textbook counts that include two terminals: 3n+1
  and 2^(n+1). State the convention beside the table.
- **P5. Witnesses are not unique.** `unroll_z3.py` and `bmc_aag.py`
  print a satisfying input trace; frame 0's `rd_en` (FIFO empty) and
  any don't-care input can differ between solver versions. `run.out`
  should print the bound, the verdict per bound and derived facts
  (`count` and `occ` per frame are forced: 15 pushes), not raw
  don't-care inputs.
- **P6. z3's CNF export is not stable.** `Then("simplify",
  "bit-blast", "tseitin-cnf")` on the same width-8 formula gave 791,
  798, 803, 804, 812 and 834 clauses in different calls (variable
  numbers come from a process-wide counter and grow from call to
  call), and CaDiCaL's conflicts on them ranged from 21,591 to 23,597.
  Use the chapter's own `tseitin.py` for anything whose size is
  printed. Also a trap: `Then("bit-blast", "tseitin-cnf")`
  *without* `simplify` on `a*b != b*a` exported `p cnf 1 1`, which a
  SAT solver calls satisfiable although the formula is not: the
  blasted term is still wrapped in `mkbv(...)`, and the CNF tactic
  treats the whole disequality as one opaque atom. A wrong pipeline
  gives a wrong answer silently; do not hand-roll it in the text.
- **P7. Depth conventions differ by one.** InFormal and the AIGER
  unroller count the reset cycle (depth/bound 16); a hand model that
  starts after reset finds the same trace at bound 15. FINDINGS A.3
  records that sby called the same trace "step 17". The chapter must
  define "bound k = k transitions, k+1 states" once and say which
  state is state 0.
- **P8. `informal lower` is not the shell.** It reads immediate
  assertions only, does no clock or reset setup (registers start free
  unless initialized in the declaration or an `initial`), turns
  immediate `assume` into a Btor2 `constraint` (measured: `Reset_M`
  became line `201 constraint 200`), and with no assertion prints
  `note: the design has no assertions`. The chapter's FIFO model
  therefore needs the wrapper `fifo_bmc.sv`. The shell's own models
  (`prop_N.btor2` in the work directory) do contain a reset, as a
  one-bit `informal_step` state plus a `constraint`; they are named by
  property index, which is fragile to depend on in an example.
- **P9. `informal simp --aag` writes the two size lines to stderr and
  the AIGER to stdout; the AIGER has no symbol table**, so input order
  is the only link to names (here in0 = `rst_n`, in1 = `wr_en`, in2 =
  `rd_en`, established from the trace, not from documentation).
  `informal info ... | head` panics on the closed pipe (harmless;
  avoid `head` in scripts).
- **P10. Yosys `aigmap` does not share equal gates**: the full adder
  is 9 ANDs from Yosys and 7 after ABC `strash` or `informal simp`.
  Good material, but the "7" needs one of those tools; Yosys alone
  prints 9.
- **P11. Verilator lint on declaration initializers** needs
  `-Wno-PROCASSINIT` (in `informal.mk`'s default `LINT_FLAGS`);
  `initial q = 0` beside an `always_ff` that writes `q` is
  `MULTIDRIVEN` under `-Wall`. Use the declaration initializer.
- **P12. Pure-Python cost.** `dpll.py` re-scans every clause per
  propagation pass: 17.6 s for 65,535 decisions on 341 clauses, and it
  cannot finish FIFO bound 8 (2,765 clauses; stopped after 92 s). Keep
  DPLL to adder widths of 7 or less and pigeonhole of 7 or less in CI
  and give it a decision limit argument (it has one).
- **P13. The adder-miter result depends on the variable numbering.**
  The exact 4^N - 1 arises because `gen.py` numbers the 2N inputs
  first and `dpll.py` branches in numeric order. That is the point of
  the example (a bad order makes search into simulation) and must be
  said, or a reader with another encoder will not reproduce it.
- **P14. `cdcl.py` is 166 lines with its header and `main`** (149 of
  code). If the chapter promises "about 150 lines", count code lines.
  Listings of that length should be spliced in three parts
  (propagate, analyze, solve), not whole.
- **P15. Random-instance reproducibility** rests on Python's
  `random.Random(seed)` with `sample` and `random`; the instance files
  are identical across CPython 3.12 and 3.13 only if those methods'
  algorithms did not change. Not checked across versions; check in CI
  or check in the generated `.cnf` files for the few that are printed.

## 5. Open question for the author (changes the chapter's shape)

**Should the chapter add `python-sat` and `dd` to the book's Python
environment, or stay on z3 plus its own 150-line solver and 60-line
BDD?** The measurements were reproduced both ways. Staying on the
existing environment keeps CI unchanged, makes every printed count
exact and version-proof, and fits "every idea must be runnable" in
the strongest sense (the reader runs the algorithm, not a wrapper);
it costs the production-solver columns in `run.out` (they move to
chapter tables captioned with versions, or come from the `z3` binary
reading DIMACS). Adding the two packages gives one-line access to
MiniSat, Glucose, CaDiCaL and Kissat and a faster BDD, at the price of
a compiled wheel in CI and version-dependent output. The outline
assumes **no new dependency**; if the author prefers the packages,
sections 4 and 6 of the outline gain a production-solver column in
their `run.out` and nothing else moves.

A smaller question, not shape-changing: whether the wrapper
`fifo_bmc.sv` (reset and occupancy written as hardware for `informal
lower`) is acceptable beside Chapter 9's bound checker, or whether the
chapter should instead read the shell's `prop_N.btor2`. The outline
assumes the wrapper (pitfall P8).

## Appendix: the scratch files, verbatim

Written for this note; original, no code taken from any source.
All are at most 80 columns. They are evidence, not final listings:
the drafter may restructure them, and must re-run whatever changes.

### `tseitin/full_adder.sv`

```
// full_adder.sv -- one column of an adder, as five gates.
module full_adder (
  input  logic a, b, cin,
  output logic sum, cout
);
  logic p, g, t;
  assign p    = a ^ b;        // the column propagates a carry
  assign sum  = p ^ cin;
  assign g    = a & b;        // the column generates a carry
  assign t    = p & cin;
  assign cout = g | t;
endmodule
```

### `tseitin/full_adder.cnf`

```
c full_adder.cnf -- the full adder, encoded by hand, one gate at a time
c 1=a 2=b 3=cin 4=p 5=sum 6=g 7=t 8=cout
p cnf 8 20
c p = a xor b
-4 1 2 0
-4 -1 -2 0
4 -1 2 0
4 1 -2 0
c sum = p xor cin
-5 4 3 0
-5 -4 -3 0
5 -4 3 0
5 4 -3 0
c g = a and b
-6 1 0
-6 2 0
6 -1 -2 0
c t = p and cin
-7 4 0
-7 3 0
7 -4 -3 0
c cout = g or t
8 -6 0
8 -7 0
-8 6 7 0
c the question: can sum and cout both be 1 while a is 0?
5 0
8 0
-1 0
```

### `solvers/dimacs.py`

```
"""dimacs.py -- read and write CNF in the DIMACS format."""


def read(path):
    """Return (number of variables, list of clauses) from a .cnf file."""
    nvars, clauses, cur = 0, [], []
    with open(path) as f:
        for line in f:
            if line.startswith(("c", "%")) or not line.strip():
                continue
            if line.startswith("p"):
                nvars = int(line.split()[2])
                continue
            for tok in line.split():
                if tok == "0":
                    clauses.append(cur)
                    cur = []
                else:
                    cur.append(int(tok))
    return nvars, clauses


def write(path, nvars, clauses, comment=""):
    with open(path, "w") as f:
        for line in comment.splitlines():
            f.write(f"c {line}\n")
        f.write(f"p cnf {nvars} {len(clauses)}\n")
        for c in clauses:
            f.write(" ".join(map(str, c)) + " 0\n")
```

### `solvers/dpll.py`

```
"""dpll.py -- the Davis-Putnam-Logemann-Loveland procedure, plainly.

    python dpll.py file.cnf [max_decisions]

Assign a variable, propagate every clause that has become a unit, and
on a conflict undo the most recent decision and try its other value.
Nothing is remembered about why a branch failed.
"""
import sys
import dimacs


class Dpll:
    def __init__(self, nvars, clauses, limit=None):
        self.nvars, self.clauses, self.limit = nvars, clauses, limit
        self.value = {}                 # variable -> True/False
        self.trail = []                 # literals in assignment order
        self.decisions = self.conflicts = self.propagations = 0

    def lit_value(self, lit):
        v = self.value.get(abs(lit))
        return None if v is None else v == (lit > 0)

    def assign(self, lit):
        self.value[abs(lit)] = lit > 0
        self.trail.append(lit)

    def propagate(self):
        """Unit propagation to a fixed point; False on a conflict."""
        changed = True
        while changed:
            changed = False
            for clause in self.clauses:
                unassigned, satisfied = [], False
                for lit in clause:
                    v = self.lit_value(lit)
                    if v is True:
                        satisfied = True
                        break
                    if v is None:
                        unassigned.append(lit)
                if satisfied:
                    continue
                if not unassigned:
                    self.conflicts += 1
                    return False
                if len(unassigned) == 1:
                    self.assign(unassigned[0])
                    self.propagations += 1
                    changed = True
        return True

    def undo_to(self, size):
        while len(self.trail) > size:
            del self.value[abs(self.trail.pop())]

    def solve(self):
        """True (satisfiable), False (not), None (limit reached)."""
        stack = []                      # (trail size, literal still to try)
        ok = self.propagate()
        while True:
            if ok:
                var = next((v for v in range(1, self.nvars + 1)
                            if v not in self.value), None)
                if var is None:
                    return True
                if self.limit and self.decisions >= self.limit:
                    return None
                self.decisions += 1
                stack.append((len(self.trail), -var))
                self.assign(var)        # try true first
            else:
                if not stack:
                    return False
                size, other = stack.pop()
                self.undo_to(size)
                self.assign(other)      # the other value is now forced
            ok = self.propagate()

    def model(self):
        return [v if self.value.get(v) else -v
                for v in range(1, self.nvars + 1)]


def main():
    nvars, clauses = dimacs.read(sys.argv[1])
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    s = Dpll(nvars, clauses, limit)
    result = s.solve()
    word = {True: "SATISFIABLE", False: "UNSATISFIABLE", None: "UNKNOWN"}
    print(f"s {word[result]}")
    print(f"c decisions {s.decisions} conflicts {s.conflicts} "
          f"propagations {s.propagations}")
    if result:
        print("v " + " ".join(map(str, s.model())) + " 0")


if __name__ == "__main__":
    main()
```

### `solvers/cdcl.py`

```
"""cdcl.py -- conflict-driven clause learning, in its smallest form.

    python cdcl.py file.cnf [max_conflicts]

The same search as dpll.py (first unassigned variable, true first),
with the three things GRASP and Chaff added: every assignment records
the clause that forced it, a conflict is analyzed back to the first
unique implication point and the result is kept as a new clause, and
the search jumps back to the level where that clause becomes a unit.
Propagation uses two watched literals per clause.
"""
import sys
import dimacs


class Cdcl:
    def __init__(self, nvars, clauses, limit=None):
        self.nvars, self.limit = nvars, limit
        self.clauses = []
        self.watches = {l: [] for v in range(1, nvars + 1) for l in (v, -v)}
        self.value, self.level, self.reason = {}, {}, {}
        self.trail, self.trail_lim, self.qhead = [], [], 0
        self.decisions = self.conflicts = self.propagations = 0
        self.learned, self.ok = 0, True
        for c in clauses:
            self.ok = self.ok and self.add_clause(sorted(set(c), key=abs))

    def lit_value(self, lit):
        v = self.value.get(abs(lit))
        return None if v is None else v == (lit > 0)

    def add_clause(self, c):
        """Attach a clause; False if it is empty or a falsified unit."""
        if any(-l in c for l in c):
            return True                 # contains x and not x: always true
        if len(c) == 1:
            if self.lit_value(c[0]) is False:
                return False
            if self.lit_value(c[0]) is None:
                self.assign(c[0], None)
            return True
        if not c:
            return False
        self.clauses.append(c)
        self.watches[c[0]].append(c)
        self.watches[c[1]].append(c)
        return True

    def assign(self, lit, reason):
        self.value[abs(lit)] = lit > 0
        self.level[abs(lit)] = len(self.trail_lim)
        self.reason[abs(lit)] = reason
        self.trail.append(lit)

    def propagate(self):
        """Return a falsified clause, or None when nothing is left."""
        while self.qhead < len(self.trail):
            false_lit = -self.trail[self.qhead]
            self.qhead += 1
            watching, self.watches[false_lit] = self.watches[false_lit], []
            for i, c in enumerate(watching):
                if c[0] == false_lit:   # keep the false watch in slot 1
                    c[0], c[1] = c[1], c[0]
                if self.lit_value(c[0]) is True:
                    self.watches[false_lit].append(c)
                    continue
                for k in range(2, len(c)):          # find a new watch
                    if self.lit_value(c[k]) is not False:
                        c[1], c[k] = c[k], c[1]
                        self.watches[c[1]].append(c)
                        break
                else:                   # none: c is a unit or a conflict
                    self.watches[false_lit].append(c)
                    if self.lit_value(c[0]) is False:
                        self.watches[false_lit] += watching[i + 1:]
                        return c
                    self.assign(c[0], c)
                    self.propagations += 1
        return None

    def analyze(self, conflict):
        """First-UIP learning: (learned clause, level to jump back to)."""
        here = len(self.trail_lim)
        seen, learned, open_paths = set(), [], 0
        clause, index, uip = conflict, len(self.trail) - 1, None
        while True:
            for lit in clause:
                var = abs(lit)
                if var in seen or self.level[var] == 0:
                    continue
                seen.add(var)
                if self.level[var] == here:
                    open_paths += 1     # still to be resolved away
                else:
                    learned.append(lit)
            while abs(self.trail[index]) not in seen:
                index -= 1
            uip = self.trail[index]
            index -= 1
            open_paths -= 1
            if open_paths == 0:
                break
            clause = self.reason[abs(uip)]
        learned.sort(key=lambda l: -self.level[abs(l)])
        back = self.level[abs(learned[0])] if learned else 0
        return [-uip] + learned, back

    def backjump(self, level):
        size = self.trail_lim[level]
        for lit in self.trail[size:]:
            del self.value[abs(lit)]
        del self.trail[size:], self.trail_lim[level:]
        self.qhead = size

    def pick(self):
        """The next variable to decide: the first one without a value."""
        return next((v for v in range(1, self.nvars + 1)
                     if v not in self.value), None)

    def solve(self):
        """True (satisfiable), False (not), None (limit reached)."""
        if not self.ok:
            return False
        while True:
            conflict = self.propagate()
            if conflict is not None:
                self.conflicts += 1
                if not self.trail_lim:
                    return False        # conflict with no decision to blame
                if self.limit and self.conflicts >= self.limit:
                    return None
                learned, back = self.analyze(conflict)
                self.backjump(back)
                self.learned += 1
                if len(learned) > 1:
                    self.clauses.append(learned)
                    self.watches[learned[0]].append(learned)
                    self.watches[learned[1]].append(learned)
                self.assign(learned[0], learned if len(learned) > 1 else None)
            else:
                var = self.pick()
                if var is None:
                    return True
                self.decisions += 1
                self.trail_lim.append(len(self.trail))
                self.assign(var, None)

    def model(self):
        return [v if self.value[v] else -v for v in range(1, self.nvars + 1)]


def main():
    nvars, clauses = dimacs.read(sys.argv[1])
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    s = Cdcl(nvars, clauses, limit)
    result = s.solve()
    word = {True: "SATISFIABLE", False: "UNSATISFIABLE", None: "UNKNOWN"}
    print(f"s {word[result]}")
    print(f"c decisions {s.decisions} conflicts {s.conflicts} "
          f"propagations {s.propagations} learned {s.learned}")
    if result:
        print("v " + " ".join(map(str, s.model())) + " 0")


if __name__ == "__main__":
    main()
```

### `solvers/cdcl_vsids.py`

```
"""cdcl_vsids.py -- cdcl.py with Chaff's decision heuristic.

    python cdcl_vsids.py file.cnf [max_conflicts]

The only change is which variable is decided next: each variable has an
activity that is raised when it appears in a learned clause, recent
conflicts count for more than old ones, and the search branches on the
most active unassigned variable instead of the lowest-numbered one.
"""
import sys
import dimacs
from cdcl import Cdcl


class CdclVsids(Cdcl):
    def __init__(self, nvars, clauses, limit=None):
        self.activity = {v: 0.0 for v in range(1, nvars + 1)}
        self.bump = 1.0
        super().__init__(nvars, clauses, limit)

    def analyze(self, conflict):
        learned, back = super().analyze(conflict)
        for lit in learned:
            self.activity[abs(lit)] += self.bump
        self.bump /= 0.95               # older conflicts fade
        return learned, back

    def pick(self):
        free = [v for v in range(1, self.nvars + 1) if v not in self.value]
        return max(free, key=self.activity.get) if free else None


def main():
    nvars, clauses = dimacs.read(sys.argv[1])
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    s = CdclVsids(nvars, clauses, limit)
    result = s.solve()
    word = {True: "SATISFIABLE", False: "UNSATISFIABLE", None: "UNKNOWN"}
    print(f"s {word[result]}")
    print(f"c decisions {s.decisions} conflicts {s.conflicts} "
          f"propagations {s.propagations} learned {s.learned}")


if __name__ == "__main__":
    main()
```

### `solvers/tseitin.py`

```
"""tseitin.py -- build CNF gate by gate (the Tseitin encoding).

Every gate output gets a fresh variable g and the clauses that say
"g equals the gate's function of its inputs". Literals are DIMACS
integers: variable v is v, its complement is -v.
"""


class Cnf:
    def __init__(self):
        self.nvars = 0
        self.clauses = []

    def var(self):
        self.nvars += 1
        return self.nvars

    def vars(self, n):
        return [self.var() for _ in range(n)]

    def add(self, *clause):
        self.clauses.append(list(clause))

    def and_(self, a, b):
        g = self.var()
        self.add(-g, a)                 # g -> a
        self.add(-g, b)                 # g -> b
        self.add(g, -a, -b)             # a and b -> g
        return g

    def or_(self, a, b):
        return -self.and_(-a, -b)       # De Morgan: no new clause shapes

    def xor_(self, a, b):
        g = self.var()
        self.add(-g, a, b)
        self.add(-g, -a, -b)
        self.add(g, -a, b)
        self.add(g, a, -b)
        return g

    def or_all(self, lits):
        g = self.var()
        self.add(-g, *lits)             # g -> some input
        for lit in lits:
            self.add(g, -lit)           # any input -> g
        return g
```

### `solvers/gen.py`

```
"""gen.py -- the instance families the chapter measures.

    python gen.py php N out.cnf        N+1 pigeons in N holes (unsat)
    python gen.py adder N out.cnf      two N-bit adders differ? (unsat)
    python gen.py adderbug N out.cnf   the same with one gate wrong (sat)
    python gen.py mul N out.cnf        N-bit a*b differs from b*a? (unsat)
    python gen.py rand N M SEED out.cnf   random 3-SAT, N vars, M clauses
"""
import random
import sys
import dimacs
from tseitin import Cnf


def pigeonhole(n):
    cnf = Cnf()
    x = [cnf.vars(n) for _ in range(n + 1)]     # x[p][h]: p sits in h
    for p in range(n + 1):
        cnf.add(*x[p])                          # every pigeon sits
    for h in range(n):
        for p in range(n + 1):
            for q in range(p + 1, n + 1):
                cnf.add(-x[p][h], -x[q][h])     # no two share a hole
    return cnf


def ripple(cnf, a, b):
    """Textbook ripple-carry adder: sum bits, then the carry out."""
    out, c = [], None
    for ai, bi in zip(a, b):
        p = cnf.xor_(ai, bi)
        if c is None:
            out.append(p)
            c = cnf.and_(ai, bi)
        else:
            out.append(cnf.xor_(p, c))
            c = cnf.or_(cnf.and_(ai, bi), cnf.and_(p, c))
    return out + [c]


def majority(cnf, a, b, bug_at=None):
    """The same function with the carry as a majority of three."""
    out, c = [], None
    for i, (ai, bi) in enumerate(zip(a, b)):
        if c is None:
            out.append(cnf.xor_(ai, bi))
            c = cnf.and_(ai, bi)
        else:
            out.append(cnf.xor_(ai, cnf.xor_(bi, c)))
            ab = cnf.or_(ai, bi) if i == bug_at else cnf.and_(ai, bi)
            c = cnf.or_(ab, cnf.or_(cnf.and_(ai, c), cnf.and_(bi, c)))
    return out + [c]


def adder_miter(n, bug=False):
    cnf = Cnf()
    a, b = cnf.vars(n), cnf.vars(n)
    s1 = ripple(cnf, a, b)
    s2 = majority(cnf, a, b, bug_at=n - 1 if bug else None)
    diff = [cnf.xor_(u, v) for u, v in zip(s1, s2)]
    cnf.add(cnf.or_all(diff))                   # some output bit differs
    return cnf


def multiply(cnf, a, b):
    """Schoolbook multiplier, low len(a) bits: add a<<i where b[i]."""
    n = len(a)
    acc = [cnf.and_(a[j], b[0]) for j in range(n)]
    for i in range(1, n):
        row = [cnf.and_(a[j], b[i]) for j in range(n - i)]
        acc[i:] = ripple(cnf, acc[i:], row)[:-1]    # drop the carry out
    return acc


def multiplier_miter(n):
    cnf = Cnf()
    a, b = cnf.vars(n), cnf.vars(n)
    p1, p2 = multiply(cnf, a, b), multiply(cnf, b, a)
    cnf.add(cnf.or_all([cnf.xor_(u, v) for u, v in zip(p1, p2)]))
    return cnf


def random_3sat(n, m, seed):
    rng = random.Random(seed)
    cnf = Cnf()
    cnf.vars(n)
    for _ in range(m):
        vs = rng.sample(range(1, n + 1), 3)
        cnf.add(*[v if rng.random() < 0.5 else -v for v in vs])
    return cnf


def main():
    kind, args, out = sys.argv[1], sys.argv[2:-1], sys.argv[-1]
    n = int(args[0])
    if kind == "php":
        cnf = pigeonhole(n)
    elif kind == "adder":
        cnf = adder_miter(n)
    elif kind == "mul":
        cnf = multiplier_miter(n)
    elif kind == "adderbug":
        cnf = adder_miter(n, bug=True)
    else:
        cnf = random_3sat(n, int(args[1]), int(args[2]))
    dimacs.write(out, cnf.nvars, cnf.clauses, " ".join(sys.argv[1:-1]))


if __name__ == "__main__":
    main()
```

### `bdd/robdd.py`

```
"""robdd.py -- reduced ordered binary decision diagrams in one page.

A node is an integer. 0 and 1 are the terminals; every other node is a
triple (level, low, high) kept in a unique table, so two nodes with the
same triple are the same integer, and a node whose two children are
equal is never created. Those two rules are Bryant's reduction, and
they make the diagram canonical: two functions are equal exactly when
their nodes are the same integer.
"""


class Bdd:
    def __init__(self, order):
        self.level = {name: i for i, name in enumerate(order)}
        self.nodes = [None, None]       # index -> (level, low, high)
        self.unique = {}                # (level, low, high) -> index
        self.memo = {}                  # (op, f, g) -> result

    def mk(self, level, low, high):
        if low == high:                 # the test does not matter
            return low
        key = (level, low, high)
        if key not in self.unique:      # share equal subgraphs
            self.unique[key] = len(self.nodes)
            self.nodes.append(key)
        return self.unique[key]

    def var(self, name):
        return self.mk(self.level[name], 0, 1)

    def top(self, f):
        return self.nodes[f][0] if f > 1 else len(self.level)

    def apply(self, op, f, g):
        """Combine two diagrams with a two-input Boolean operator."""
        if f <= 1 and g <= 1:
            return int(op(bool(f), bool(g)))
        key = (op, f, g)
        if key not in self.memo:
            level = min(self.top(f), self.top(g))
            f0, f1 = self.nodes[f][1:] if self.top(f) == level else (f, f)
            g0, g1 = self.nodes[g][1:] if self.top(g) == level else (g, g)
            self.memo[key] = self.mk(level, self.apply(op, f0, g0),
                                     self.apply(op, f1, g1))
        return self.memo[key]

    def size(self, f):
        """Number of decision nodes reachable from f."""
        seen, stack = set(), [f]
        while stack:
            n = stack.pop()
            if n > 1 and n not in seen:
                seen.add(n)
                stack += self.nodes[n][1:]
        return len(seen)


def AND(x, y):
    return x and y


def OR(x, y):
    return x or y


def XOR(x, y):
    return x != y
```

### `bdd/bdd_own.py`

```
import sys, time
sys.setrecursionlimit(100000)
from robdd import Bdd, AND, OR, XOR

def add(b, xs, ys):
    out, c = [], 0
    for x, y in zip(xs, ys):
        p = b.apply(XOR, x, y)
        out.append(b.apply(XOR, p, c))
        c = b.apply(OR, b.apply(AND, x, y), b.apply(AND, c, p))
    return out, c

def names(n, inter):
    a = [f"a{i}" for i in range(n)]; bb = [f"b{i}" for i in range(n)]
    return a, bb, ([v for p in zip(a, bb) for v in p] if inter else a + bb)

if __name__ == "__main__":
  print("width  carry: interleaved separated   mult bit n-1: nodes  s")
  for n in range(1, int(sys.argv[1]) + 1):
      row = f"{n:5d}"
      for inter in (True, False):
          a, bb, order = names(n, inter)
          b = Bdd(order)
          _, c = add(b, [b.var(v) for v in a], [b.var(v) for v in bb])
          row += f" {b.size(c):12d}"
      a, bb, order = names(n, True)
      b = Bdd(order); t = time.time()
      k = n - 1
      acc = [0] * n
      for i in range(n):
          r = [0] * i + [b.apply(AND, b.var(a[j]), b.var(bb[i])) for j in range(n - i)]
          acc, _ = add(b, acc, r)
      row += f" {b.size(acc[k]):12d} {time.time()-t:6.2f}"
      # equivalence check by canonicity: ripple vs majority carry
      print(row, flush=True)
```

### `fifo/fifo_bmc.sv`

```
// fifo_bmc.sv -- the first chapter's FIFO with everything a model
// checker needs written out as hardware: a reset sequence, an
// occupancy counter built from the contract, and one assertion.
`include "fifo.sv"
module fifo_bmc (
  input logic       clk,
  input logic       rst_n,
  input logic       wr_en,
  input logic [7:0] wr_data,
  input logic       rd_en
);
  logic [7:0] rd_data;
  logic       full, empty;
  fifo dut (.*);

  logic       started = 1'b0;       // 0 in the first cycle only
  logic [4:0] occ;                  // occupancy by the contract
  always_ff @(posedge clk) begin
    started <= 1'b1;
    if (!rst_n) occ <= '0;
    else        occ <= occ + 5'(wr_en && !full) - 5'(rd_en && !empty);
  end

  always_comb begin
    // Reset is held for the first cycle and released for good.
    Reset_M:        assume (rst_n == started);
    // FIFO-005, the direction the first chapter's bug breaks.
    FullBackward_A: assert (!rst_n || !full || occ == 5'd16);
  end
endmodule
```

### `fifo/bmc_aag.py`

```
"""bmc_aag.py -- unroll an ASCII AIGER model into one CNF per bound.

    python bmc_aag.py model.aag [max_bound]

The model is a set of latches, a network of two-input ANDs, one "bad"
literal and optional "constraint" literals (AIGER 1.9). Frame t gets a
fresh copy of every input and AND; a latch in frame t+1 is the same
CNF variable as its next-state literal in frame t, so the transition
relation costs no clauses beyond the ANDs themselves.
"""
import sys
import time
from pysat.solvers import Solver


def read_aag(path):
    with open(path) as f:
        rows = [line.split() for line in f]
    assert rows[0][0] == "aag"
    m, i, l, o, a, b, c = (int(x) for x in rows[0][1:8])
    body = [[int(x) for x in r] for r in rows[1:1 + i + l + o + b + c + a]]
    inputs = [r[0] for r in body[:i]]
    latches = body[i:i + l]             # lit, next, reset (0, 1 or lit)
    bads = [r[0] for r in body[i + l + o:i + l + o + b]]
    cons = [r[0] for r in body[i + l + o + b:i + l + o + b + c]]
    ands = body[i + l + o + b + c:]     # lhs, rhs0, rhs1
    return inputs, latches, bads, cons, ands


class Unroller:
    def __init__(self, model):
        self.inputs, self.latches, self.bads, self.cons, self.ands = model
        self.nvars = 1                  # CNF variable 1 is "true"
        self.clauses = [[1]]
        self.frames = []                # frame -> {aiger var: CNF literal}

    def fresh(self):
        self.nvars += 1
        return self.nvars

    def lit(self, t, aig_lit):
        """CNF literal of an AIGER literal in frame t."""
        if aig_lit < 2:
            return 1 if aig_lit else -1
        v = self.frames[t][aig_lit >> 1]
        return -v if aig_lit & 1 else v

    def add_frame(self):
        t = len(self.frames)
        cur = {}
        self.frames.append(cur)
        for x in self.inputs:
            cur[x >> 1] = self.fresh()
        for lit, nxt, *reset in self.latches:
            if t > 0:                   # the wire that fed it last cycle
                cur[lit >> 1] = self.lit(t - 1, nxt)
            elif reset and reset[0] == lit:
                cur[lit >> 1] = self.fresh()        # starts unknown
            else:
                cur[lit >> 1] = 1 if reset and reset[0] else -1
        for lhs, r0, r1 in self.ands:   # Tseitin: g <-> a AND b
            g = self.fresh()
            cur[lhs >> 1] = g
            a, b = self.lit(t, r0), self.lit(t, r1)
            self.clauses += [[-g, a], [-g, b], [g, -a, -b]]
        for c in self.cons:             # constraints hold in every frame
            self.clauses.append([self.lit(t, c)])
        return t


def main():
    model = read_aag(sys.argv[1])
    bound = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    u = Unroller(model)
    print(f"model: {len(u.inputs)} inputs, {len(u.latches)} latches, "
          f"{len(u.ands)} ANDs")
    print("bound   vars  clauses  result  conflicts")
    for k in range(bound + 1):
        t = u.add_frame()
        bad = u.lit(t, u.bads[0])
        with Solver(name="cadical195", bootstrap_with=u.clauses) as s:
            sat = s.solve(assumptions=[bad])
            conf = s.accum_stats()["conflicts"]
            print(f"{k:5d} {u.nvars:6d} {len(u.clauses):8d}  "
                  f"{'SAT' if sat else 'UNSAT':6s} {conf:9d}")
            if sat:
                model_ = set(s.get_model())
                print("frame  " + " ".join(f"in{n}" for n in
                                           range(len(u.inputs))))
                for f in range(t + 1):
                    vals = [int(u.lit(f, x) in model_) for x in u.inputs]
                    print(f"{f:5d}  " + "   ".join(str(v) for v in vals))
                return
    print("no counterexample up to the bound")


main()
```

### `fifo/unroll_z3.py`

```
"""unroll_z3.py -- the FIFO's occupancy logic, unrolled by hand.

    python unroll_z3.py [bug|fixed] [max_bound]

The state is the design's count register and the checker's occ; one
step of the design is a function from (state, inputs) to the next
state, written here with z3 bit-vectors straight from the RTL. A bound
of k makes k+1 copies of the inputs and chains the steps together.
"""
import sys
import z3

BUG = (sys.argv[1] if len(sys.argv) > 1 else "bug") == "bug"
BOUND = int(sys.argv[2]) if len(sys.argv) > 2 else 20
CW = 4 if BUG else 5                    # width of the count register
FULL_AT = 15 if BUG else 16             # the value full is decoded from


def flags(count):
    return count == FULL_AT, count == 0             # full, empty


def step(count, occ, wr_en, rd_en):
    """Next (count, occ) after one clock edge out of reset."""
    full, empty = flags(count)
    do_write = z3.And(wr_en, z3.Not(full))
    do_read = z3.And(rd_en, z3.Not(empty))
    one = z3.BitVecVal(1, CW)
    nxt = z3.If(z3.And(do_write, z3.Not(do_read)), count + one,
                z3.If(z3.And(do_read, z3.Not(do_write)), count - one,
                      count))
    occ_nxt = (occ + z3.If(do_write, z3.BitVecVal(1, 5), 0)
               - z3.If(do_read, z3.BitVecVal(1, 5), 0))
    return nxt, occ_nxt


def bad(count, occ):
    """The negation of FullBackward_A: full, and not sixteen entries."""
    full, _ = flags(count)
    return z3.And(full, occ != 16)


count, occ = z3.BitVecVal(0, CW), z3.BitVecVal(0, 5)    # after reset
inputs = []
for k in range(BOUND + 1):
    s = z3.Solver()
    s.add(bad(count, occ))              # one query: the whole unrolling
    if s.check() == z3.sat:
        m = s.model()
        print(f"bound {k:2d}: sat -- full with occ != 16 after {k} cycles")
        print("wr_en " + " ".join(
            str(int(z3.is_true(m.eval(w, model_completion=True))))
            for w, _ in inputs))
        print("rd_en " + " ".join(
            str(int(z3.is_true(m.eval(r, model_completion=True))))
            for _, r in inputs))
        break
    print(f"bound {k:2d}: unsat")
    wr_en, rd_en = z3.Bools(f"wr_en@{k} rd_en@{k}")
    inputs.append((wr_en, rd_en))
    count, occ = step(count, occ, wr_en, rd_en)
else:
    print(f"no counterexample within {BOUND} cycles of reset")
```

### `counter/counter.sv`

```
// counter.sv -- a 3-bit counter that is meant to stop at 5.
module counter (
  input  logic       clk,
  input  logic       en,
  output logic [2:0] q
);
  logic [2:0] count = 3'd0;         // the value at the first clock edge
  always_ff @(posedge clk)
    if (en && count != 3'd6)        // the bug: the spec says stop at 5
      count <= count + 3'd1;
  assign q = count;
  always_comb
    AtMostFive_A: assert (count <= 3'd5);
endmodule
```

### `counter/counter.btor2`

```
1 sort bitvec 1
2 input 1 counter.clk
3 input 1 counter.en
4 sort bitvec 3
5 state 4 counter.count
6 const 4 110
7 neq 1 5 6
8 and 1 3 7
9 const 4 001
10 add 4 5 9
11 ite 4 8 10 5
12 const 1 1
13 const 4 101
14 ulte 1 5 13
15 const 4 000
16 init 4 5 15
17 not 1 14
18 and 1 12 17
19 bad 18 AtMostFive_A
20 next 4 5 11
```

### `bv/word_vs_bits.py`

```
"""word_vs_bits.py -- one question, asked of words and asked of bits.

    python word_vs_bits.py [seconds per call] [largest width]

Three ways to ask "is multiplication commutative at width w?", each as
a search for a counterexample that does not exist:

  rewrite   a*b != b*a on z3 bit-vectors. The solver's rewriter knows
            the algebra and answers without searching.
  word      shift_add(a,b) != shift_add(b,a), where shift_add is the
            schoolbook multiplier written with word-level operators.
            No rewrite rule applies; z3 must reduce it to bits.
  bits      the same formula turned into CNF by z3's own bit-blaster
            and handed to a SAT solver.
"""
import sys
import threading
import time
import z3
from pysat.formula import CNF
from pysat.solvers import Solver

LIMIT = float(sys.argv[1]) if len(sys.argv) > 1 else 20.0
WMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 9


def shift_add(a, b, w):
    """Sum of the shifted copies of a selected by the bits of b."""
    acc = z3.BitVecVal(0, w)
    for i in range(w):
        row = z3.If(z3.Extract(i, i, b) == 1, a << i, z3.BitVecVal(0, w))
        acc = acc + row
    return acc


def ask_z3(formula):
    s = z3.SolverFor("QF_BV")
    s.set("timeout", int(LIMIT * 1000))
    s.add(formula)
    t = time.time()
    r = str(s.check())
    return r, time.time() - t


def ask_sat(formula):
    goal = z3.Goal()
    goal.add(formula)
    cnf = z3.Then("simplify", "bit-blast", "tseitin-cnf")(goal)[0]
    f = CNF(from_string=cnf.dimacs())
    with Solver(name="cadical195", bootstrap_with=f.clauses) as s:
        timer = threading.Timer(LIMIT, s.interrupt)
        timer.start()
        t = time.time()
        r = s.solve_limited(expect_interrupt=True)
        dt = time.time() - t
        timer.cancel()
        conflicts = s.accum_stats()["conflicts"]
    word = {True: "sat", False: "unsat", None: "unknown"}[r]
    return word, dt, f.nv, len(f.clauses), conflicts


def main():
    print(f"limit {LIMIT:.0f} s per call")
    print("width  rewrite         word            "
          "bits: vars clauses conflicts")
    for w in list(range(4, WMAX + 1)) + [32, 64]:
        a, b = z3.BitVecs("a b", w)
        r0, t0 = ask_z3(a * b != b * a)
        row = f"{w:5d}  {r0:7s}{t0:6.2f} s"
        if w <= WMAX:
            f = shift_add(a, b, w) != shift_add(b, a, w)
            r1, t1 = ask_z3(f)
            r2, t2, nv, nc, conf = ask_sat(f)
            row += (f"  {r1:7s}{t1:6.2f} s  {r2:7s}{t2:6.2f} s"
                    f" {nv:5d} {nc:7d} {conf:9d}")
        print(row, flush=True)


main()
```

### `solvers/phase.py`

```
"""phase.py -- random 3-SAT: where the hard instances are.

    python phase.py [variables] [instances per ratio]

For each clause-to-variable ratio, draw random 3-SAT instances and
record how many are satisfiable and how many conflicts MiniSat needs.
"""
import statistics
import sys
from pysat.solvers import Solver
from gen import random_3sat

N = int(sys.argv[1]) if len(sys.argv) > 1 else 150
RUNS = int(sys.argv[2]) if len(sys.argv) > 2 else 50

print(f"{N} variables, {RUNS} instances per ratio, seeds 0..{RUNS - 1}")
print("ratio  clauses  satisfiable  median conflicts  max conflicts")
for tenth in range(30, 62, 2):
    m = N * tenth // 10
    sat, conflicts = 0, []
    for seed in range(RUNS):
        cnf = random_3sat(N, m, seed)
        with Solver(name="minisat22", bootstrap_with=cnf.clauses) as s:
            sat += s.solve()
            conflicts.append(s.accum_stats()["conflicts"])
    print(f"{tenth / 10:5.1f} {m:8d} {sat:8d}/{RUNS} "
          f"{int(statistics.median(conflicts)):13d} {max(conflicts):14d}",
          flush=True)
```

### `solvers/php_scale.py`

```
"""php_scale.py -- pigeonhole instances against two production solvers."""
import time
from pysat.solvers import Solver
from gen import pigeonhole

print("holes  vars  clauses   minisat22: conflicts  seconds"
      "   cadical195: conflicts  seconds")
for n in range(4, 13):
    cnf = pigeonhole(n)
    row = f"{n:5d} {cnf.nvars:5d} {len(cnf.clauses):8d}"
    for name in ("minisat22", "cadical195"):
        with Solver(name=name, bootstrap_with=cnf.clauses,
                    use_timer=True) as s:
            t = time.time()
            assert s.solve() is False
            row += (f"   {s.accum_stats()['conflicts']:20d}"
                    f" {time.time() - t:8.2f}")
    print(row, flush=True)
```

### `solvers/mul_scale.py`

```
"""mul_scale.py -- a*b against b*a, bit-blasted, by width."""
import sys
import threading
import time
from pysat.solvers import Solver
from gen import multiplier_miter, adder_miter

LIMIT = float(sys.argv[1]) if len(sys.argv) > 1 else 30.0
WMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 10


def run(cnf):
    with Solver(name="cadical195", bootstrap_with=cnf.clauses) as s:
        timer = threading.Timer(LIMIT, s.interrupt)
        timer.start()
        t = time.time()
        r = s.solve_limited(expect_interrupt=True)
        dt = time.time() - t
        timer.cancel()
        word = {True: "sat", False: "unsat", None: "unknown"}[r]
        return (f"{cnf.nvars:6d} {len(cnf.clauses):7d} "
                f"{s.accum_stats()['conflicts']:9d} {dt:7.2f} s {word}")


print("width  adder miter: vars clauses conflicts  time      "
      "multiplier miter: vars clauses conflicts  time")
for w in range(2, WMAX + 1):
    print(f"{w:5d}  {run(adder_miter(w))}   {run(multiplier_miter(w))}",
          flush=True)
for w in (16, 32, 64, 128):
    print(f"{w:5d}  {run(adder_miter(w))}", flush=True)
```

### `solvers/selftest.py`

```
import random, sys
from pysat.solvers import Solver
from dpll import Dpll
from cdcl import Cdcl
random.seed(1)
n_sat = 0
for trial in range(3000):
    n = random.randint(1, 25)
    m = random.randint(1, int(n * 5.5) + 2)
    cls = [[random.choice([-1, 1]) * random.randint(1, n)
            for _ in range(random.randint(1, 4))] for _ in range(m)]
    with Solver(name="minisat22", bootstrap_with=cls) as s:
        ref = s.solve()
    n_sat += ref
    for cls_ in (Dpll, Cdcl):
        s = cls_(n, [list(c) for c in cls])
        r = s.solve()
        assert r == ref, (cls_, cls)
        if r:
            mod = set(s.model())
            assert all(any(l in mod for l in c) for c in cls), (cls_, cls)
print("3000 random instances agree with MiniSat;", n_sat, "satisfiable")
```

## Addendum to section 3 (measured after the appendix was written)

**J. The book solvers on the families the outline puts in `run.out`**
(`own_scale.py`: `cdcl.py` and `cdcl_vsids.py`, conflict limit 30,000;
all counts exact and repeatable):

| instance | vars | clauses | `cdcl.py` conflicts | time | `cdcl_vsids.py` conflicts | time |
|---|---|---|---|---|---|---|
| mul2 | 17 | 44 | 8 | 0.00 s | 8 | 0.00 s |
| mul3 | 40 | 115 | 25 | 0.00 s | 27 | 0.00 s |
| mul4 | 75 | 226 | 87 | 0.01 s | 125 | 0.02 s |
| mul5 | 122 | 377 | 282 | 0.04 s | 452 | 0.06 s |
| mul6 | 181 | 568 | 1,014 | 0.16 s | 2,008 | 0.43 s |
| mul7 | 252 | 799 | 3,655 | 1.09 s | 7,232 | 3.09 s |
| adder3 | 39 | 116 | 27 | | 37 | |
| adder5 | 69 | 206 | 106 | | 87 | |
| adder7 | 99 | 296 | 410 | | 280 | |
| adder24 | 354 | 1,061 | > 30,000 | 24 s | 1,176 | 0.23 s |

On the multiplier the activity heuristic is *worse* than the fixed
order (7,232 against 3,655 at 7 bits) and both grow about 3.6x per
bit: a heuristic is a bet, and the chapter should show a case it
loses. (`adder2`: 12 and 13.)

**K. Phase transition with the book solver** (`phase_own.py 60 30`,
1.3 s, `cdcl_vsids.py`, 60 variables, 30 instances per ratio, seeds
0..29): satisfiable 30, 30, 29, 21, 6, 0, 0, 0 of 30 at ratios 3.0,
3.4, 3.8, 4.2, 4.6, 5.0, 5.4, 5.8; median conflicts 1, 4, 18, 79, 105,
83, 74, 58; maxima 21, 63, 110, 260, 172, 167, 131, 115.

**L. `REQUIRES`** in `scripts/check-examples.sh` is one program name
tested with `type -P`; `REQUIRES := yosys` or `:= informal` both work,
a Python module cannot be named there (a script that needs `z3` must
print a line starting `skipped: ` and exit 0 itself, which the checker
already recognizes).

**M. A commit appeared on `main` during this work** (`8730788`, "Start
the research note for the logic and solvers chapter"), not made by this
research run. It holds the first 24 lines of this note as they then
were, including a scratch-directory path that the note no longer
contains. Whoever owns the history should look at that line.
