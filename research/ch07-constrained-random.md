---
title: "Research note: Chapter 7 — Constrained-Random Stimulus"
date: 2026-09-12
author: research-agent
status: complete
feeds: Ch. 7
---

# Chapter 7 — Constrained-Random Stimulus: evidence note

Scope: the randomization language — `rand`, `randc`, `randomize()` and its
silent failure, constraint blocks in every form, random stability — and the
method behind it: why constrained-random verification exists, what a
constraint solver does and does not promise, distributions, seeds and
reproducibility. Then a *measured* account of what the book's two open
simulators do with each construct, without a solver (the environment as it
stands) and with `z3` from a pip wheel (in the scratchpad only).

Gathered in three independent passes and kept in three parts. **Section
numbers are local to their part.** Each part carries its own unsourced-claims
table, BibTeX suggestions and confidence notes.

## Which part feeds which chapter section

| Chapter topic | Part | Sections |
|---|---|---|
| `randomize()`, `rand`/`randc`, silent atomic failure | A | §2 |
| Constraint blocks: `inside`, `dist`, implication, `foreach`, `solve before`, `soft`, `unique` | A | §3 |
| Random stability: threads, objects, seeds, what is guaranteed | A | §4; B | §4 |
| What goes wrong: the 22-row catalog | A | §5 |
| Why constrained-random exists; the measured evidence, such as it is | B | §1 |
| What a solver does; the readable pipeline in Verilator | B | §2 |
| Solver freedom: no uniformity promised; distributions | B | §3 |
| Seeds end to end: dvsim, UVM `reseed`, cocotb | B | §4 |
| **What runs where, with and without a solver** (decides every example) | C | matrices |
| Silent wrong results and documentation-versus-measurement | C | catalog, §4 |

## Findings that decide the chapter, across the parts

1. **`randomize()` fails silently and atomically**: returns 0, changes
   nothing (Part A §1). OpenTitan makes the check mandatory by macro. The
   chapter's first Pitfall, and every call in its examples is checked.
2. **Constrained `randomize()` runs on neither tool as the book's
   environment stands** (Part C): Icarus has no `randomize` at all;
   Verilator 5.030 warns to stderr, returns 0 and exits 0 without a solver.
   The pip `z3-solver` wheel supplies a `z3` binary Verilator accepts
   unchanged, taking the chapter's constructs from 6 to 20 on Verilator.
   Installing it into `dvbook` is one line; it is an environment change for
   the author.
3. **Verilator 5.030 discards distribution shaping even with a solver**
   (Parts B and C): weighted `dist` honors membership only, `solve before`
   changes nothing, `soft` is treated as hard, `unique` is ignored; the
   change log dates real support to 5.046, 5.048 and 5.052. Either the tool
   baseline moves or distribution shaping stays in prose and a Pitfall.
4. **Uniformity is a tool property the language does not promise** (Part B
   §3): documented in Verilator's own bug history and fixed by importing a
   published sampler; measured on 5.030, a three-bit variable under `a < 8`
   never produced 7 in 20,000 calls.
5. **Random stability is a property of code structure** (Part A §4, B §4):
   per-thread and per-object generators; UVM reseeds by type and path;
   nobody promises same-seed reproducibility across simulators or versions.
6. **Every "wrong distribution" gotcha is arithmetic** (Part A §1): chained
   relations, integer `dist` weights, unsigned wrap in a range bound.
7. **IEEE 1800-2023 clause 18 text was not read**; top-level subclauses are
   confirmed by slang and Verilator diagnostics, the rest are 2017-edition
   numbers and are not to be printed as 2023.


---

# Part A — Randomization as SystemVerilog defines it

Scope: `rand`/`randc`, `randomize()` and its return value, `randomize()
with` and inline-constraint scoping, constraint blocks (relational,
`inside`, `dist` with `:=` and `:/`, implication, `if`/`else`, `foreach`,
`solve … before`, `soft`, `unique`), static and dynamic control
(`constraint_mode`, `rand_mode`), `pre_randomize`/`post_randomize`,
`std::randomize`, `$urandom`/`$urandom_range` versus `$random`, and random
stability (seeding, thread and object stability, what is and is not
guaranteed). Then the catalog of what goes wrong. Chapter 5's note
(`research/ch05-testbench-language.md`, Part A §1) already covers why random
stimulus is declared two-state and Part C measures which randomization
constructs Verilator 5.030 and Icarus 13.0 run; neither is redone here.
Solver internals, distributions as a mathematical topic and coverage
feedback are Parts B and C of this chapter's evidence.

Written section by section; the most important part is first.

**On clause numbers.** IEEE 1800-2023 is paywalled and its text was not
read. Top-level subclause numbers of clause 18 are given where slang's
language-support table (which states it tracks "1800-2023") and Verilator's
source agree: slang lists 18.3 Concepts and usage, 18.4 Random variables,
18.5 Constraint blocks, 18.6 Randomization methods, 18.7 In-line
constraints, 18.8 Disabling random variables, 18.9 Controlling constraints,
18.10 Dynamic constraint modification, 18.11 In-line random variable
control, 18.12 Randomization of scope variables, 18.13 Random number system
functions, 18.14 Random stability, 18.15 Manually seeding randomize, 18.16
Random weighted case, 18.17 Random sequence generation, and 20.14
Probabilistic distribution functions
[slang, "Language Support", accessed 2026-09-12](https://sv-lang.com/language-support.html).
Verilator's `src/V3Randomize.cpp` and `src/V3Width.cpp` cite, as "IEEE
1800-2023", 18.3, 18.4, 18.4.1, 18.5.1, 18.5.3, 18.5.13, 18.6.2, 18.6.3,
18.7, 18.7.2, 18.8, 18.9, 18.11, 18.11.1, 18.12 and 18.16
[Verilator `src/V3Randomize.cpp`, master, file last changed 2026-09-10, accessed 2026-09-12](https://github.com/verilator/verilator/blob/master/src/V3Randomize.cpp),
[Verilator `src/V3Width.cpp`, master, accessed 2026-09-12](https://github.com/verilator/verilator/blob/master/src/V3Width.cpp).
Third-level numbers (18.5.x) rest on Verilator alone and are labelled so.
Everything else is cited to the edition without a clause, or to the paper
that explains it.

### 1. Findings that decide the chapter

1. **`randomize()` fails silently by design, and the two reference gotcha
   papers agree on the fix.** The method returns 1 on success and 0 when
   the solver cannot satisfy the constraints, and on 0 "the variables are
   not randomized"; the only symptom of an unchecked failure is stale
   values [Sutherland, Mills & Spear, SNUG SJ, 2007-02-13](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf)
   (§5.3). Yehia adds that the attempt is atomic, "all-or-none": no random
   variable is updated when any constraint fails, and an ignored return
   value forces a void cast and a silent failure
   [Yehia, DVCon Europe, 2014](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf)
   (§III.A). OpenTitan makes the check mandatory by macro:
   `DV_CHECK_RANDOMIZE_FATAL(VAR_)` expands to a `uvm_fatal` check around
   `VAR_.randomize()`, with `_WITH_`, `STD_` and `MEMBER_` variants, and the
   lowRISC DV style guide says these "must be used for all randomization
   functionality"
   [lowRISC OpenTitan `hw/dv/sv/dv_utils/dv_macros.svh`, commit fca045d, 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_utils/dv_macros.svh),
   [lowRISC DV style guide, accessed 2026-09-12](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).
   The chapter's first Pitfall is therefore not a constraint bug but an
   unchecked return value, and the worked example wraps every call.
2. **Random stability is a property of the code's structure, not of the
   simulator, and the standard's model is per-thread and per-object RNGs
   seeded from their parent.** Efody defines random stability as "the
   resistance of random results to code changes", explicitly not the
   ability to repeat a run given identical code, which "depends on the
   vendor's simulator code"
   [Efody, DVCon US, 2012](https://dvcon-proceedings.org/wp-content/uploads/uvm-random-stability.pdf)
   (§I.A). Each thread, module, program, interface, package and class
   instance has its own RNG; the thread-level RNGs feed `$urandom`,
   `$urandom_range`, `std::randomize`, `randcase`, `randsequence` and
   `shuffle` and seed child threads and new objects, while a class
   instance's RNG serves only its `randomize()` and changes state only when
   `randomize()` is called, so an object's results depend on earlier
   `randomize()` calls on that object and on the thread state at its
   construction, and nothing else
   [Yehia, 2014](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf)
   (§IV.A), [Efody, 2012](https://dvcon-proceedings.org/wp-content/uploads/uvm-random-stability.pdf)
   (§II.A). `srandom()` on a process or object, and
   `get_randstate`/`set_randstate`, are the escape hatches; UVM 1.2 uses the
   first one systematically: `uvm_object::reseed()` calls
   `this.srandom(uvm_create_random_seed(get_type_name(), get_full_name()))`,
   and components, sequence items and default sequences call it
   [Accellera UVM 1.2 `src/base/uvm_object.svh`, `src/base/uvm_misc.svh`, 2014](https://www.accellera.org/images/downloads/standards/uvm/uvm-1.2.tar.gz).
   The chapter can state the model, show the `srandom` idiom, and say
   plainly that reproducibility *across* simulators, or across versions of
   one, is not promised by anyone ([Yehia, 2014](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf) §IV.H).
3. **Every "surprising distribution" gotcha is an operator-precedence or
   integer-arithmetic fact, not a solver quirk.** `lo < med < hi` parses
   as `(lo < med) < hi`, constrains only `hi > 1`, never fails, and shows
   up as low coverage [Sutherland, Mills & Spear, 2007](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf)
   (§5.2); `[0:10] : 1/11` is integer division and weights the range zero
   [Yehia, 2014](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf)
   (§IV.D); `i - length + 1` on an unsigned wraps and turns a range into
   one that is always or never satisfied (§IV.B-2), which is exactly why
   OpenTitan writes `int'(edn_clk_freq_mhz - clk_freq_mhz) inside {[-2:2]}`
   with the comment "cast to `int`, as … are unsigned"
   [lowRISC OpenTitan `hw/dv/sv/cip_lib/cip_base_env_cfg.sv`, commit fca045d](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/cip_lib/cip_base_env_cfg.sv).
   The chapter teaches these as three rules (one relation per statement;
   `:/` for ranges; cast before subtracting) rather than as solver lore.
4. **`randc` is a per-variable promise and nothing more.** Yehia:
   "The SystemVerilog LRM only describes the cyclic nature of the values
   produced by individual randc variables, while it says nothing about any
   kind of cyclic behavior of solutions from multiple related randc
   variables"; `randc` variables are solved before `rand` ones, in an
   undefined order, so an equality between a `randc bit [7:0]` and a `randc
   bit [3:0]` fails, and constraint dependencies between two `randc`
   variables force the solver to either fail or break one cycle
   [Yehia, 2014](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf)
   (§III.D, §IV.E). OpenTitan's DV library and the two IP testbenches
   sampled use `randc` nowhere (0 of 416 files) and `rand` with `inside`
   126 times [OpenTitan, commit fca045d, measured 2026-09-12](https://github.com/lowRISC/opentitan/tree/master/hw/dv/sv).
   The chapter presents `randc` as a tool for exhaustive small enumerations
   and warns against constraining it against anything.
5. **Constrained randomization needs an external SMT solver on Verilator
   and does not exist on Icarus** (Chapter 5's note, Part C). Verilator's
   manual documents the failure mode and the diagnostic: `UNSATCONSTR`
   "warns that a `randomize()` call failed because one or more constraints
   could not be satisfied … issued at simulation runtime when the SMT
   solver determines that the combination of constraints is
   unsatisfiable", and `CONSTRAINTIGN` that a form of `constraint`,
   `constraint_mode` or `rand_mode` "was ignored"
   [Verilator `docs/guide/warnings.rst`, master, accessed 2026-09-12](https://github.com/verilator/verilator/blob/master/docs/guide/warnings.rst).
   The chapter's examples must be checked with `z3` installed, and the
   example Makefile must say so; this is a Part C question for the
   drafter, but it decides which listings can carry `run.out`.

### 2. The randomization methods

**`rand`, `randc` and what `randomize()` touches.** Only properties tagged
`rand` or `randc` receive values; a handle to another object must itself be
`rand` for the child's `rand` properties to be randomized, otherwise the
child keeps its values with no diagnostic (the 2007 paper's `Header`/
`Payload` example, §5.1)
[Sutherland, Mills & Spear, 2007-02-13](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf).
Verilator's implementation notes the same rule from the other side: nested
`pre_randomize`/`post_randomize` are called on `rand` class-typed members
("IEEE 18.4.1"), and an unpacked-struct member is randomized "only if its
own declaration carries rand/randc" (18.4)
[Verilator `src/V3Randomize.cpp`, accessed 2026-09-12](https://github.com/verilator/verilator/blob/master/src/V3Randomize.cpp).
A dynamic array or queue declared `rand` is resized only if its size is
constrained; with no size constraint it keeps its previous size, initially
zero, and `randomize()` reports success, and the solver never constructs
objects when it resizes an array of handles
[Yehia, 2014](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf)
(§IV.C); Verilator likewise does "not randomize associative array size
(IEEE 18.4)". Unconstrained randomization ranges over every two-state value
of the type, so `rand int` and `rand byte` produce negatives (§5.4 of the
2007 paper; note that its remedy sentence says "signed types such as
logic" where its example and Chapter 5's reading mean an unsigned
four-state vector, a slip the chapter must not copy)
[Sutherland, Mills & Spear, 2007-02-13](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf);
Yehia gives the rule positively: `bit [7:0]` not `byte`, `bit [31:0]` not
`int`, unless negatives are wanted
[Yehia, 2014](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf)
(§IV.B-1).

**The return value and the null handle.** `randomize()` returns 1 on
success and 0 on failure, and the failure is atomic (§1, finding 1).
Verilator wraps every call as `(obj != null) ? obj.randomize() : 0` with
the comment "IEEE 1800 requires randomize() on null handle to return 0"
[Verilator `src/V3Randomize.cpp`](https://github.com/verilator/verilator/blob/master/src/V3Randomize.cpp),
which is Chapter 5's "forgot `new`" pitfall seen from this side: a null
handle does not crash, it returns 0 and leaves nothing changed. Verilator
also implements `randomize(null)` as a check-only solve that validates the
constraints "against the current runtime values without assigning new
ones" (18.11), calling `pre_randomize` always and `post_randomize` only on
success (18.6.2, 18.6.3); the chapter can mention this as the standard's
"is this object legal?" query without teaching it.

**Randomizing a subset.** `obj.randomize(x)` randomizes `x` only, but the
solver still enforces every constraint in the object against the *current*
values of the other variables. Yehia's example: `constraint { b < a; }`
with `a` still at its initial 0 makes `randomize(b)` fail; the remedy is
to randomize the whole object once before randomizing members
[Yehia, 2014](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf)
(§III.B). Verilator quotes 18.11 on the argument form: "Arguments are
limited to the names of properties of the calling object; expressions are
not allowed", and accepts `obj.member[idx].field` anyway "for
compatibility with other simulators"
[Verilator `src/V3Randomize.cpp`](https://github.com/verilator/verilator/blob/master/src/V3Randomize.cpp).
OpenTitan's `DV_CHECK_MEMBER_RANDOMIZE_FATAL` wraps `this.randomize(foo)`
and is used 23 times in the sampled tree
[OpenTitan `dv_macros.svh`; counts measured 2026-09-12](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_utils/dv_macros.svh).

**`randomize() with` and where names resolve.** An inline constraint block
is resolved "first in the scope of the randomize() with object class
followed by … the local scope", so `t.randomize() with {t.addr == addr;}`
inside a class that also has `addr` constrains `t.addr` to itself; the
`local::` qualifier bypasses the object's scope and the correct form is
`with { addr == local::addr; }`
[Yehia, 2014](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf)
(§IV.F, quoting the 2012 edition). Verilator's grammar handles the
identifier list for `with` under 18.7 and the implication form under
18.7.2. OpenTitan's `tl_device_seq::randomize_rsp` is a full-size witness:
one `rsp.randomize() with {…}` carries an `inside` range, an `if`/`else`
on the request opcode, two equalities tying the response to the request,
and a `dist` on `d_error`
[lowRISC OpenTitan `hw/dv/sv/tl_agent/seq_lib/tl_device_seq.sv`, commit fca045d](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/tl_agent/seq_lib/tl_device_seq.sv).

**`pre_randomize` and `post_randomize`.** The solver's procedure, as Yehia
lays it out from the standard, begins by calling `pre_randomize()`
"recursively in a top-down manner" and ends, after every variable has been
assigned, by calling `post_randomize()` the same way
[Yehia, 2014](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf)
(§II.C, steps 1 and 12c). Verilator's comment adds the dispatch rule that
matters in a hierarchy: they "appear to behave as virtual methods" because
`randomize()` is virtual (18.6.2)
[Verilator `src/V3Randomize.cpp`](https://github.com/verilator/verilator/blob/master/src/V3Randomize.cpp).
Two practices follow. The UVM register model requires an overridden
`post_randomize()` to call `super.post_randomize()`, because that is where
the randomized field value is copied into the mirror
[Accellera, UVM 1.2 User's Guide, 2015-10-08](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf)
(§5.3.4, §5.10); and OpenTitan's `dv_base_vseq::pre_randomize()` fetches the
`cfg` handle "so that the knobs in cfg are available during sequence
randomization"
[lowRISC OpenTitan `hw/dv/sv/dv_lib/dv_base_vseq.sv`, commit fca045d](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_lib/dv_base_vseq.sv).
Yehia's remedy for a function-in-constraint cycle is also a
`post_randomize` idiom: compute the dependent bit there instead of
constraining it (§III.C).

**`rand_mode` and `constraint_mode`.** Both are built-in methods that
cannot be overridden (Verilator reports "The 'rand_mode' method is built-in
and cannot be overridden (IEEE 1800-2023 18.8)" and the same for
`constraint_mode` under 18.9)
[Verilator `src/V3Width.cpp`](https://github.com/verilator/verilator/blob/master/src/V3Width.cpp).
The UVM user guide shows the canonical use between `uvm_create` and
`uvm_rand_send`: `req.addr.rand_mode(0)` to freeze a field, then
`req.dc1.constraint_mode(0)` to drop a constraint, with the note "You
might need to disable a constraint to avoid a conflict"
[Accellera, UVM 1.2 User's Guide, 2015-10-08](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf)
(§6.5.3.1). OpenTitan's `tl_seq_item` has both as named functions:
`disable_a_chan_randomization()` calls `rand_mode(0)` on the seven A-channel
fields so a response can be re-randomized without disturbing the request,
and `disable_a_chan_protocol_constraint()` calls `constraint_mode(0)` on
six protocol constraints to generate deliberately illegal requests
[lowRISC OpenTitan `hw/dv/sv/tl_agent/tl_seq_item.sv`, commit fca045d](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/tl_agent/tl_seq_item.sv).

**`std::randomize`.** Randomizes variables that are not class members;
Verilator notes that 18.12 "limits args to current scope variables" and
accepts class members "for compatibility"
[Verilator `src/V3Width.cpp`](https://github.com/verilator/verilator/blob/master/src/V3Width.cpp).
OpenTitan's `randomize_a_chan_with_protocol_error()` uses it on five local
`bit` flags to choose which constraints to disable, then randomizes the
item, and the sampled tree has 12 uses
[lowRISC OpenTitan `tl_seq_item.sv`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/tl_agent/tl_seq_item.sv).
Its random source is the *thread's* RNG, not an object's, which matters for
stability (§4).

**`$urandom`, `$urandom_range` and `$random`.** `$urandom` returns an
unsigned 32-bit value and `$random` a signed one; Verilator sets the types
with the comment "Says the spec" in both cases, and its runtime shows the
seed-argument difference: `$random(seed)` takes the seed by reference and
writes a new seed back, `$urandom(seed)` takes it by value
[Verilator `src/V3Width.cpp`, `include/verilated.cpp`](https://github.com/verilator/verilator/blob/master/include/verilated.cpp).
Yehia's rule is the one the chapter needs: `$random` and `$dist_*` come
from 1364 Verilog and "should not be used in SystemVerilog as they are not
part of the random stability model"
[Yehia, 2014](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf)
(§II.A). OpenTitan practice matches: 139 `$urandom_range` and 17
`$urandom` calls, zero `$random`, in the sampled tree; typical uses are
delays (`wait_clks($urandom_range(0, 3))`), one-in-ten decisions
(`$urandom_range(1, 10) == 10`) and an iteration count
(`repeat ($urandom_range(2, 20))`)
[lowRISC OpenTitan `hw/dv/sv/cip_lib/seq_lib/cip_base_vseq.sv`, commit fca045d](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/cip_lib/seq_lib/cip_base_vseq.sv).
`randcase` (18.16) is the weighted-branch form; OpenTitan uses it 14 times,
and Verilator errors at runtime when "All randcase items had 0 weights"
[Verilator `src/V3Randomize.cpp`](https://github.com/verilator/verilator/blob/master/src/V3Randomize.cpp).

### 3. Constraint blocks

**Relational constraints and the chained-comparison trap.** A constraint is
an expression the solver must make true; a bare expression wider than one
bit is treated as `expr != 0` (Verilator cites 18.5.1)
[Verilator `src/V3Randomize.cpp`](https://github.com/verilator/verilator/blob/master/src/V3Randomize.cpp).
The trap is that relational operators return 1-bit results and associate
left to right: `lo < med < hi` becomes `(lo < med) < hi`, and `a == b == c`
becomes `(a == b) == c`, so `c` is 0 or 1 and all three are equal with
probability about 1/2^16; neither ever fails, and the symptom is low
coverage. The fix is one relation per statement
[Sutherland, Mills & Spear, 2007-02-13](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf)
(§5.2, with sample output from two simulators).

**`inside`.** Set membership over values and `[lo:hi]` ranges; OpenTitan's
most common constraint form (126 occurrences): `a_valid_len inside
{[1:10]}`, `d_opcode inside {AccessAckData, AccessAck}`, and the negated
form `!(a inside {data})`, which the lowRISC style guide prefers to a
`foreach` loop of inequalities for speed
[lowRISC OpenTitan `tl_seq_item.sv`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/tl_agent/tl_seq_item.sv),
[lowRISC DV style guide, §Randomization](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).
What `inside` does *not* do is weight: with no other constraint the
solver's choice is over the set's values, so `x inside {[0:9], 1000}`
makes 1000 as likely as any single small value, one in eleven. The
uniformity premise is the standard's (18.5.3 in the 2017 numbering) and was
not read; it is listed in the unsourced-claims table. The engineer who
wanted "mostly small, occasionally the big corner" wanted `dist`.

**`dist`: `:=` versus `:/`.** A `dist` item is a value or range with a
weight; `:=` gives the weight to *each* value in a range, `:/` divides the
weight *across* the range. Verilator's lowering says exactly this, ":= on
a range weights every element, so scale by the range size", and adds a hard
membership constraint because "values outside the set must never appear"
(18.5.3 in its numbering); a weight that is zero, even only at runtime,
excludes its bucket, and if every weight is zero the `dist` is "vacuously
true (unconstrained)"
[Verilator `src/V3Randomize.cpp`](https://github.com/verilator/verilator/blob/master/src/V3Randomize.cpp).
Yehia's §IV.D is the canonical misuse: `x dist {[0:10]: 1/11, 12: 1,
[13:30]: 1/18, 31}` computes `1/11` and `1/18` in integer arithmetic,
gets 0, and the solver "would only generate values 12 and 31"; the intended
constraint is `[0:10] :/ 1, 12 : 1, [13:30] :/ 1, 31`
[Yehia, 2014](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf).
OpenTitan uses `dist` 67 times and both weight forms idiomatically: `:=`
on single values (`dummy_ir dist { 0 := 99, 1 := 1 }`) and `:/` on ranges
(`host_delay_max dist { [1:10] :/ 1, [11:50] :/ 4, [51:100] :/ 3,
[101:500] :/ 2, [501:1000] :/ 1 }`), with weights that are runtime
knobs (`1 :/ rsp_abort_pct, 0 :/ 100 - rsp_abort_pct`)
[lowRISC OpenTitan `hw/dv/sv/jtag_agent/jtag_item.sv`, `hw/dv/sv/push_pull_agent/push_pull_agent_cfg.sv`, `tl_device_seq.sv`, commit fca045d](https://github.com/lowRISC/opentitan/tree/master/hw/dv/sv).

**Implication and `if`/`else`.** `a -> b` makes `b` required whenever `a`
holds; `if (c) {…} else {…}` is the two-sided form. OpenTitan:
`a_opcode == PutFullData -> `MASK_IS_FULL(a_mask, a_size)` (75 lines with
`->` in the sample) and the three-way `if`/`else if`/`else` on
`tlul_and_edn_clk_freq_diff` in `cip_base_env_cfg`
[lowRISC OpenTitan `tl_seq_item.sv`, `cip_base_env_cfg.sv`](https://github.com/lowRISC/opentitan/tree/master/hw/dv/sv).
Verilator's grammar splits the 18.7.2 production `expr -> constraint_set`
by right-hand shape; a `dist` under an implication is a real case it
handles (`cond -> x dist {...}`)
[Verilator `src/verilog.y`, `src/V3Randomize.cpp`](https://github.com/verilator/verilator/blob/master/src/verilog.y).

**`foreach` and array reductions.** Iterative constraints range over array
elements; lowRISC's guide says to avoid loops in constraints where
`inside` will do and never to compute inside them
[lowRISC DV style guide, §Randomization](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).
Yehia's §III.E is the width trap: `descr.sum() == 50` over a `rand bit`
array sums at the element width, one bit, and fails; write
`descr.sum() with (int'(item)) == 50`
[Yehia, 2014](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf).

**`solve … before`.** Changes the order in which the solver picks
variables, and therefore the distribution, not the solution set; Yehia
lists it as the operator for "probability and distribution" and shows the
cycle error from `solve a before b; solve b before c; solve c before a`
(§II.B, §III.C). The OpenTitan uses (15 in the sample) are all of one
shape: decide a mode first, then the value the mode governs, `solve
zero_delays before host_delay_max; if (zero_delays) {host_delay_max == 0;}
else {host_delay_max dist {…}}`, `solve clen before cmd_data_q;
cmd_data_q.size() == clen`
[lowRISC OpenTitan `push_pull_agent_cfg.sv`, `hw/dv/sv/csrng_agent/csrng_item.sv`](https://github.com/lowRISC/opentitan/tree/master/hw/dv/sv).
`cip_base_env_cfg` carries the one comment on the interaction with
functions: an expression was written out instead of calling a function
because "per the LRM that could cause circular constraints against the
`solve ... before` above"
[lowRISC OpenTitan `cip_base_env_cfg.sv`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/cip_lib/cip_base_env_cfg.sv).
Verilator's `CONSTRAINTIGN` warning covers the forms it drops (Chapter 5's
note measured `solve … before` as one of them at 5.030).

**`soft` constraints.** A `soft` constraint is dropped, not reported, when
a hard constraint contradicts it. Yehia recommends it over the
pre-standard `default constraint` extension, which is silently discarded
in its entirety once any of its variables appears in another constraint
(§IV.I). Verilator implements a priority between scopes ("outer-scope soft
constraints override inner-scope", citing 18.5.13 in its numbering) and
`disable soft` as a directive on the constraint graph
[Verilator `src/V3Randomize.cpp`](https://github.com/verilator/verilator/blob/master/src/V3Randomize.cpp).
OpenTitan uses `soft` 27 times, always as an overridable default:
`soft d_error == 0`, `soft host_delay_min == 0`, `soft int_err_cyc dist {1
:/ 5, [2:10] :/ 5}`. One detail is instructive: the `tl_seq_item` comment
says the soft `d_error == 0` "is overridden in e.g. tl_device_seq", but
the override in `tl_device_seq` is `rsp.no_d_error_c.constraint_mode(0)`
followed by an inline `d_error dist {…}`. A `dist` does not *contradict*
`soft d_error == 0` (zero is in the set), so the soft constraint would
survive and the `dist` would never produce 1; disabling the constraint is
the correct move, and the chapter should say why
[lowRISC OpenTitan `tl_seq_item.sv`, `tl_device_seq.sv`, commit fca045d](https://github.com/lowRISC/opentitan/tree/master/hw/dv/sv/tl_agent).
(That a soft constraint yields only to a contradicting hard one is the
standard's rule, not read; see the unsourced-claims table.)

**`unique`.** `unique {a, b, c}` requires pairwise-distinct values;
Verilator expands the explicit-element form "into pairwise != constraints"
and handles whole-array `unique {arr}` separately
[Verilator `src/V3Randomize.cpp`](https://github.com/verilator/verilator/blob/master/src/V3Randomize.cpp).
OpenTitan's single use is the whole-array form on a 256-entry `bit [7:0]`
array, `constraint rd_data_c { unique { rd_data }; }`, which asks for a
permutation of all 256 byte values
[lowRISC OpenTitan `hw/dv/sv/i2c_agent/i2c_driver.sv`, commit fca045d](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/i2c_agent/i2c_driver.sv).

**Constraint inheritance and the same-name trap.** Constraints are
inherited and a derived class adds to them; the UVM user guide calls adding
constraints to a transaction type by inheritance "an important use model"
and the reason the generic payload's members are `protected`, not `local`
[Accellera, UVM 1.2 User's Guide, 2015-10-08](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf)
(§2.4.1.2). Yehia's §IV.G shows the failure: redeclaring `rand bit [15:0]
a` in the derived class hides the base's `a`, the base constraint `a <
256` binds to the hidden one, and the derived `a` runs free; the same
symptom appears when a base-class constructor calls `randomize()` before
the derived part exists
[Yehia, 2014](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf).
OpenTitan declares constraints `extern` in the class and defines them
out-of-body (`constraint tl_seq_item::param_c { … }`), 180 constraint
declarations in the sample, each named `<what>_c` as the style guide
requires
[lowRISC OpenTitan `tl_seq_item.sv`; lowRISC DV style guide](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).

### 4. Random stability: what is guaranteed and what is not

**The model.** Every thread, module, program, interface and package
instance, and every class object, has its own RNG. A thread's RNG changes
state on each `$urandom`-family call, each object construction and each
fork it performs, and it seeds the RNGs of the threads it forks and the
objects it constructs; an object's RNG changes state only on that object's
`randomize()`. The root RNGs are seeded by the simulator from the run's
seed [Efody, DVCon US, 2012](https://dvcon-proceedings.org/wp-content/uploads/uvm-random-stability.pdf)
(§II.A, Figure 1 and its annotated example), restated in
[Yehia, 2014](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf)
(§IV.A). Two consequences: constructing an unrelated object *before* a
sequence object changes every value that sequence's `randomize()` later
produces (Yehia's `rand_s`/`rw_s` example), and a `$urandom` in a task
depends on every `$urandom`, `new` and `fork` that thread executed before
it. Efody's footnotes record that some simulators deviate from the model
for object construction (one "doesn't affect results unless some_class has
some rand variables"), which is itself a reason not to rely on it.

**Manual seeding.** `srandom(seed)` on a `process` handle reseeds a thread;
on an object it reseeds that object, so results from that point depend
only on the relative execution path. `get_randstate()`/`set_randstate()`
save and restore a thread's RNG so that inserted code leaves later values
unchanged [Efody, 2012](https://dvcon-proceedings.org/wp-content/uploads/uvm-random-stability.pdf)
(§II.B, §II.C). The seed should be a function of the run's seed, or the
testbench becomes "too stable": constant across runs (Efody §II.B); Yehia's
idiom is `static int global_seed = $urandom; … rw_s.srandom(global_seed +
"rw_s")` (§IV.A).

**What UVM does with it.** `uvm_object::reseed()` is
`if (use_uvm_seeding) this.srandom(uvm_create_random_seed(get_type_name(),
get_full_name()))`; `uvm_create_random_seed` hashes `{type_id, "::",
inst_id}` with a CRC-style one-way hash seeded from
`uvm_global_random_seed = $urandom`, and increments a per-type counter so
that unnamed instances of one type do not collide. `uvm_component::new`
calls `reseed()` once the instance name is known, `uvm_sequence_item::
set_item_context` calls it, and the sequencer calls `seq.reseed()` before
randomizing a default sequence
[Accellera UVM 1.2 source `src/base/uvm_object.svh`, `src/base/uvm_misc.svh`, `src/base/uvm_component.svh`, `src/seq/uvm_sequence_item.svh`, `src/seq/uvm_sequencer_base.svh`, 2014](https://www.accellera.org/images/downloads/standards/uvm/uvm-1.2.tar.gz).
Efody explains the design: UVM "cut[s] the execution path into a multitude
of slices, each … protected by its own srandom() call", and sequence seeds
are prefixed with the sequencer's path so identical sequences on different
sequencers differ; the limit is that unique naming "is not enforced", so
unnamed items fall back to a counter and the stability of Figure 3 "simply
can't be achieved" (§III.A.2, §III.B.3a)
[Efody, 2012](https://dvcon-proceedings.org/wp-content/uploads/uvm-random-stability.pdf).
OpenTitan's DV tree contains no `srandom`, `get_randstate` or
`set_randstate` call at all (0 of 416 files): it relies entirely on UVM's
reseeding and on named objects [measured 2026-09-12](https://github.com/lowRISC/opentitan/tree/master/hw/dv/sv).

**What is not guaranteed.** Reproducing a run given identical code, seed
and simulator is a vendor property, outside the standard's stability model
(Efody §I.A). Across simulators, or across versions of one, "a simulator A
invoked with initial seed S, would probably generate totally different
random stimulus than simulator B invoked with the same initial seed S"
[Yehia, 2014](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf)
(§IV.H). DPI-C code is untouched by the simulation seed unless the
testbench passes one in (§IV.J). Verilator states its own deviation in the
manual: "There is one random seed per C thread, not per module for $random,
nor per object for random stability of $urandom/$urandom_range", set by
`+verilator+seed+<value>`; seed 0 picks a non-zero seed and exposes it
through `$get_initial_random_seed` so the run can be repeated
[Verilator `docs/guide/languages.rst`, `docs/guide/exe_sim.rst`, master, accessed 2026-09-12](https://github.com/verilator/verilator/blob/master/docs/guide/languages.rst).
Slang marks 18.14 Random stability and 18.15 Manually seeding randomize
"N/A" because it is a front end, not a simulator
[slang, "Language Support"](https://sv-lang.com/language-support.html).

### 5. What goes wrong: the catalog

Each row is a documented failure, its symptom, and the source that
documents it. The "silent?" column is the chapter's Pitfall trigger: a
row that compiles, runs and prints nothing wrong.

| Failure | Symptom | Silent? | Source |
|---|---|---|---|
| Return value of `randomize()` ignored, constraints contradictory | Fields keep their previous values; no message | yes | [Sutherland et al. 2007 §5.3](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf); [Yehia 2014 §III.A](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf) |
| Constraint satisfiable only for some state: `b < a` with `a` unrandomized; non-random variables changed between calls | `randomize()` returns 0 sometimes | with an unchecked return, yes | [Yehia 2014 §III.B](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf) |
| `rand` missing on a member or on a handle to a child object | Member (or whole child) never changes | yes | [Sutherland et al. 2007 §5.1](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf) |
| Randomizing a constant-valued expectation (`rand` on an unconstrained `int`) | Negative values reach the DUT | yes | [Sutherland et al. 2007 §5.4](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf); [Yehia 2014 §IV.B-1](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf) |
| Chained relations `lo < med < hi`, `a == b == c` | Never fails; wrong distribution; low coverage | yes | [Sutherland et al. 2007 §5.2](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf) |
| Unsigned subtraction in a range bound (`[i-length+1 : …]`) | Range wraps; constraint always or never true | yes | [Yehia 2014 §IV.B-2](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf); OpenTitan's `int'(…)` cast in `cip_base_env_cfg.sv` |
| `dist` weight written as a fraction (`1/11`) | Integer division gives 0; those values never occur | yes | [Yehia 2014 §IV.D](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf) |
| `:=` on a range where `:/` was meant | Range receives weight × size | yes | Verilator's `:=` scaling comment; OpenTitan uses `:/` on every range |
| `inside` where a weighted choice was meant | Rare corner value as likely as any other | yes | uniformity premise unread (see table below) |
| Unconstrained `rand` dynamic array | Size unchanged (0); success returned | yes | [Yehia 2014 §IV.C](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf) |
| `sum()` over a `rand bit` array | 1-bit arithmetic; failure | no (returns 0) | [Yehia 2014 §III.E](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf) |
| Function of a `rand` variable in a constraint on that variable | Circular dependency; sporadic failure | no | [Yehia 2014 §III.C](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf) |
| `solve … before` cycle | Compile-time error | no | [Yehia 2014 §III.C](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf) |
| Equality between `randc` variables of different widths; constraints between `randc` variables | Failure, or one cycle broken | the second, yes | [Yehia 2014 §III.D, §IV.E](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf) |
| Inline constraint names resolve to the object, not the caller | `t.addr == addr` constrains `t.addr` to itself | yes | [Yehia 2014 §IV.F](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf) |
| Same-named `rand` member redeclared in a subclass | Base constraint binds to the hidden member | yes | [Yehia 2014 §IV.G](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf) |
| `randomize()` called from a base-class constructor | Derived constraints absent; tool-dependent | yes | [Yehia 2014 §IV.G](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf) |
| `soft` default combined with a `dist` on the same variable | `dist` never contradicts the soft equality; value fixed | yes | inferred from OpenTitan `tl_device_seq.sv` disabling the constraint; standard's rule unread |
| Unrelated `new`, `$urandom` or `fork` added earlier in a thread | Every later random value changes | yes | [Efody 2012 §II.A](https://dvcon-proceedings.org/wp-content/uploads/uvm-random-stability.pdf); [Yehia 2014 §IV.A](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf) |
| Unnamed sequence items in UVM | Reseeding falls back to a counter; stability lost | yes | [Efody 2012 §III.B.3a](https://dvcon-proceedings.org/wp-content/uploads/uvm-random-stability.pdf) |
| `$random` in a SystemVerilog testbench | Outside the stability model | yes | [Yehia 2014 §II.A](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf) |
| Same seed, different simulator or version | Different stimulus | — | [Yehia 2014 §IV.H](https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf) |
| Constrained `randomize()` on Verilator without `z3` | Returns 0, fields stay at reset (Chapter 5 note, Part C §4) | with an unchecked return, yes | Chapter 5 note; [Verilator warnings `UNSATCONSTR`, `CONSTRAINTIGN`](https://github.com/verilator/verilator/blob/master/docs/guide/warnings.rst) |

### 6. What the book's tools do with this (pointer)

Chapter 5's note (Part C) measured it: unconstrained `rand`/`randc`,
`pre_randomize`/`post_randomize` and `srandom` run on Verilator 5.030
without a solver; any `constraint` block or `randomize() with` needs an
external SMT solver (`z3 --in`, overridable through `VERILATOR_SOLVER`) and
returns 0 without one; `solve … before`, `soft` and `std::randomize` drew
`CONSTRAINTIGN` at 5.030; Icarus 13.0 has no `randomize` at all. Two
additions from Verilator's current sources, dated so the drafter can
re-measure: `randc` is implemented as an LFSR of width `clog2(N)+1` that
walks all `N` values before reseeding, so a cycle is a permutation of the
range, and constrained `randc` uses "exclusion-based cycling" that records
used values [Verilator `include/verilated_types.h` (`VlRandC`), `include/verilated_random.h`, master, accessed 2026-09-12](https://github.com/verilator/verilator/blob/master/include/verilated_types.h);
the `RANDC` warning "never issued since version 5.018, when `randc` became
fully supported", and `UNSATCONSTR` reports each unsatisfied constraint
with its source location
[Verilator `docs/guide/warnings.rst`, master](https://github.com/verilator/verilator/blob/master/docs/guide/warnings.rst).
`+verilator+solver+file+<filename>` logs every solver command and
response, which is the debugging aid the chapter can name for "why did
`randomize()` return 0"
[Verilator `docs/guide/exe_sim.rst`, master](https://github.com/verilator/verilator/blob/master/docs/guide/exe_sim.rst).

### Unsourced-claims table

| Claim in this note | Status | What would source it |
|---|---|---|
| With no other constraint, `inside {set}` (and an unconstrained `rand` variable) gives every value in the set equal probability | Standard's rule, text not read; folklore-level agreement | IEEE 1800-2023 18.5.3 / 18.4 text (free through the IEEE GET program) |
| A `soft` constraint is dropped only when a hard constraint (or a higher-priority soft one) contradicts it, so a `dist` that admits the soft value does not override it | Reasoned from `dist` semantics and OpenTitan's choice to `constraint_mode(0)`; standard's text not read | IEEE 1800-2023 soft-constraint subclause; or a measured run on Verilator with `z3` |
| `randc` cycles through every value of its range in a random permutation before repeating | Yehia's paraphrase plus Verilator's LFSR implementation; standard's text not read | IEEE 1800-2023 18.4 text |
| `$urandom_range(max, min)` with `max < min` swaps the arguments | Not verified in any source read here; not stated in the note's body | IEEE 1800-2023 18.13.2; or Verilator's `V3Width.cpp`/runtime |
| Verilator's third-level clause numbers (18.5.1, 18.5.3, 18.5.13) match the 2023 edition; they sit one below the 2017 edition's numbering as remembered by this note's writer (18.5.4 Distribution, 18.5.14 Soft constraints), not checked against either text | Inference from Verilator's comments; neither edition's text read | The 2023 table of contents |
| OpenTitan counts (0 `randc`, 0 `srandom`, 126 `inside`, 67 `dist`, 27 `soft`, 15 `solve before`, 139 `$urandom_range`, 180 `constraint` lines, 416 files) | Measured by `grep` over `hw/dv/sv`, `hw/ip/uart/dv`, `hw/ip/hmac/dv` at commit fca045d on 2026-09-12; counts are lines, not semantic uses | Re-run the grep at the commit the chapter cites |
| Spear & Tumbush Chapter 6 covers the constructs listed here | Only the chapter title "Randomization", pages 169–227 and the publisher's keywords (external constraint, constraint solver, implication operator, dynamic array) were read, from the Crossref record | Read the chapter |

### Key sources

Existing `refs.bib` keys reused: `sutherland2007gotchas` (§5.1–5.4),
`spear2012svfv` (add Ch. 6 to its note), `ieee1800-2023`, `slang-docs`,
`verilator-warnings`, `verilator-languages`, `lowrisc-dv-style`,
`opentitan-tl-seq-item`, `opentitan-dv-lib`, `accellera2015uvmug`.
New entries:

```bibtex
@inproceedings{yehia2014crgotchas,
  author    = {Ahmed Yehia},
  title     = {The Top Most Common {SystemVerilog} Constrained Random Gotchas},
  booktitle = {Design and Verification Conference and Exhibition (DVCon) Europe},
  year      = {2014},
  url       = {https://dvcon-proceedings.org/wp-content/uploads/the-top-most-common-systemverilog-constrained-random-gotchas.pdf},
  note      = {Author at Mentor Graphics; the solver-procedure list in
               \S II.C is the author's reading of IEEE 1800-2012 and is
               cited as such. Proceedings record:
               https://dvcon-proceedings.org/document/the-top-most-common-systemverilog-constrained-random-gotchas/.
               Accessed 2026-09-12}
}

@inproceedings{efody2012randstability,
  author    = {Avidan Efody},
  title     = {{UVM} Random Stability: Don't Leave It to Chance},
  booktitle = {Design and Verification Conference and Exhibition (DVCon) United States},
  year      = {2012},
  url       = {https://dvcon-proceedings.org/wp-content/uploads/uvm-random-stability.pdf},
  note      = {Author at Mentor Graphics. Proceedings record:
               https://dvcon-proceedings.org/document/uvm-random-stability/.
               Accessed 2026-09-12}
}

@misc{accellera2014uvm12src,
  author       = {{Accellera Systems Initiative}},
  title        = {Universal Verification Methodology ({UVM}) 1.2 reference implementation},
  howpublished = {Accellera, uvm-1.2.tar.gz},
  year         = {2014},
  url          = {https://www.accellera.org/images/downloads/standards/uvm/uvm-1.2.tar.gz},
  note         = {Files cited: src/base/uvm\_object.svh (\texttt{reseed},
                  \texttt{use\_uvm\_seeding}), src/base/uvm\_misc.svh
                  (\texttt{uvm\_global\_random\_seed},
                  \texttt{uvm\_oneway\_hash},
                  \texttt{uvm\_create\_random\_seed}),
                  src/base/uvm\_component.svh,
                  src/seq/uvm\_sequence\_item.svh,
                  src/seq/uvm\_sequencer\_base.svh. Apache-2.0.
                  Accessed 2026-09-12}
}

@misc{verilator-src-randomize,
  author       = {{Verilator contributors}},
  title        = {Verilator source: \texttt{src/V3Randomize.cpp},
                  \texttt{src/V3Width.cpp}, \texttt{src/verilog.y},
                  \texttt{include/verilated\_types.h},
                  \texttt{include/verilated\_random.h},
                  \texttt{include/verilated.cpp}},
  howpublished = {GitHub, verilator/verilator, master},
  year         = {2026},
  url          = {https://github.com/verilator/verilator/blob/master/src/V3Randomize.cpp},
  note         = {Cited for the IEEE 1800-2023 clause-18 subclauses its
                  comments name and for its \texttt{dist}, \texttt{randc},
                  \texttt{\$random}/\texttt{\$urandom} lowering.
                  \texttt{V3Randomize.cpp} last changed 2026-09-10; this is
                  later than the 5.030 release the book measures.
                  LGPL-3.0/Artistic-2.0. Accessed 2026-09-12}
}

@misc{verilator-exe-sim,
  author       = {Wilson Snyder and {Verilator contributors}},
  title        = {Verilator User's Guide: Simulation Runtime Arguments},
  year         = {2026},
  url          = {https://verilator.org/guide/latest/exe_sim.html},
  note         = {\texttt{+verilator+seed+}, \texttt{+verilator+solver+file+}.
                  Source: docs/guide/exe\_sim.rst. Accessed 2026-09-12}
}

@misc{opentitan-tl-device-seq,
  author       = {{lowRISC contributors (OpenTitan project)}},
  title        = {{OpenTitan} \texttt{tl\_device\_seq}},
  howpublished = {GitHub, lowRISC/opentitan, hw/dv/sv/tl\_agent/seq\_lib/tl\_device\_seq.sv},
  year         = {2026},
  url          = {https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/tl_agent/seq_lib/tl_device_seq.sv},
  note         = {\texttt{randomize\_rsp}: \texttt{constraint\_mode(0)} on
                  a soft default, then \texttt{randomize() with} carrying
                  \texttt{inside}, \texttt{if}/\texttt{else} and
                  \texttt{dist}. Commit fca045d. Apache-2.0. Accessed 2026-09-12}
}

@misc{opentitan-dv-constraints,
  author       = {{lowRISC contributors (OpenTitan project)}},
  title        = {{OpenTitan} {DV} agents: constraint blocks},
  howpublished = {GitHub, lowRISC/opentitan, hw/dv/sv},
  year         = {2026},
  url          = {https://github.com/lowRISC/opentitan/tree/master/hw/dv/sv},
  note         = {Files cited: cip\_lib/cip\_base\_env\_cfg.sv
                  (\texttt{solve before}, signed cast),
                  cip\_lib/seq\_lib/cip\_base\_vseq.sv
                  (\texttt{\$urandom\_range}, \texttt{randcase}),
                  jtag\_agent/jtag\_item.sv (\texttt{:=}),
                  push\_pull\_agent/push\_pull\_agent\_cfg.sv
                  (\texttt{:/} on ranges), csrng\_agent/csrng\_item.sv
                  (array size), i2c\_agent/i2c\_driver.sv
                  (\texttt{unique}), i2c\_agent/i2c\_item.sv,
                  alert\_esc\_agent/alert\_esc\_seq\_item.sv
                  (\texttt{soft dist}), dv\_utils/dv\_macros.svh.
                  Commit fca045d, 2026-09-11. Apache-2.0. Accessed 2026-09-12}
}
```

### Confidence notes

- **High.** The gotcha mechanisms in §3 and §5 attributed to Sutherland,
  Mills & Spear (2007, §5.1–5.4) and to Yehia (2014, §III–IV): the full
  text of both papers was read from the PDFs. The UVM 1.2 reseeding
  mechanism: read from the 1.2 kit's source. The OpenTitan constraint
  bodies: read from a sparse checkout at commit fca045d.
- **High, but vendor-authored.** Both DVCon papers are by Mentor Graphics
  engineers. They are conference papers, not marketing, and every claim
  used here is about the language or is illustrated with code; where Yehia
  describes "the Solver", the note attributes it to him as a description
  of the standard's procedure, not as a fact about any product. Efody's
  footnotes on simulator deviations are reported as his observations.
- **Medium.** Clause numbers: top-level 18.x from slang's table and
  Verilator's comments, which agree; third-level 18.5.x from Verilator
  alone, whose master branch is sixteen months past the version the book
  measures. The standard's text was not read (paywalled; it is available
  through the IEEE GET program and a drafter with access should check
  18.4, 18.5.3/18.5.4 and the soft-constraint subclause before the chapter
  quotes a rule).
- **Medium.** The UVM 1.2 User's Guide was read from a text extraction of
  the official PDF; section numbers 2.4.1.2, 3.10.2.2, 5.3.4, 5.10 and
  6.5.3.1 are from that extraction.
- **Low.** The `inside` uniformity claim, the soft-versus-`dist`
  interaction, and the `$urandom_range` argument-swap rule are marked
  unsourced above and must not appear in the chapter as the standard's
  words until the text is read or the behavior is measured.
- **Not reached.** Spear & Tumbush's Chapter 6 text (only the Crossref
  record); any Cummings, Sutherland or Bromley paper specifically on
  constraints or random stability beyond the two gotchas papers (the
  session's web-search budget was exhausted before that search could be
  made; the DVCon proceedings archive's search page found the two DVCon
  papers by direct URL); the 2006 gotchas paper has no randomization
  section. IEEE 1800-2023 18.13 (`$urandom` semantics) and 20.14
  (`$random`) were not read; the signed/unsigned and seed-argument
  differences are cited to Verilator's implementation comments.

---

# Part B — Method and solving

Scope: why constrained-random verification exists and what evidence there
is for it; what a constraint solver does and what the SystemVerilog
standard does and does not promise about which solution it returns;
distributions (`dist`, `solve … before`, `soft`, corner-case bias) and the
gap between "uniform over the solution space" and what the engineer
meant; seeds, random stability, and how UVM, OpenTitan's `dvsim` and cocotb
record and replay a seed. Language mechanics of `rand`, `randc`,
`constraint` blocks and `randomize()` are Part A's business and are not
re-taught here; Chapter 5's note already established that on this
machine constrained `randomize()` needs an external SMT solver under
Verilator and is unsupported on Icarus
(`research/ch05-testbench-language.md`, Part C).

**On clause numbers.** IEEE 1800-2023 is paywalled and its text was not
consulted. Clause numbers below are given only where an open compiler's
own diagnostics or the slang language-support table name them against the
2023 edition; otherwise a statement is cited to the edition without a
clause, and the Unsourced-claims table says so.

### Findings that decide the chapter

1. **The book's measured Verilator (5.030) silently discards every
   distribution-shaping constraint.** Chapter 5's probes showed that on
   5.030 `solve a before b` and `soft` produce
   `%Warning-CONSTRAINTIGN: Constraint expression ignored (imperfect
   distribution)` and `randomize()` returns 1 anyway
   (`research/ch05-testbench-language.md`, Part C). The change log dates the
   fixes: `solve..before` at 5.046 (2026-02-28), soft constraints and
   "constraint imperfect distributions" (`dist` with the weights honored) at
   5.048 (2026-04-26), and a near-uniform sampler (UniGen2) at 5.052
   (2026-09-05)
   [Verilator Changes, accessed 2026-09-12](https://github.com/verilator/verilator/blob/master/Changes).
   So a Chapter 7 example that *demonstrates* `dist`, `solve before` or
   `soft` cannot be verified on the tool the book measures: on 5.030 the
   listing compiles, runs, prints a warning, and shows the wrong
   distribution. The chapter needs either a Verilator upgrade to 5.048 or
   later for its `examples/ch07-*` Makefile (a change to the book's
   tool baseline, which the author should decide) or a scope that keeps
   distribution shaping to prose and a Pitfall.
2. **"The solver returns *some* satisfying assignment, not a uniform one"
   is documented by a solver-backed simulator's own bug history, not only
   asserted by the standard's silence.** Verilator's maintainers describe the
   mechanism in PR #7684: "An SMT solver returns _some_ satisfying model,
   not a uniform one: for `value < 2^N` it keeps returning the boundary
   value `K-1`", so low bits were set in 65–90% of trials instead of about
   50%
   [Verilator PR #7684, accessed 2026-09-12](https://github.com/verilator/verilator/pull/7684).
   The issue it fixed (#7563) reports that a constraint limiting a value to
   `0..1<<16` "nearly never produces all lower 16 bits getting set"
   [Verilator issue #7563, accessed 2026-09-12](https://github.com/verilator/verilator/issues/7563).
   This is the chapter's central worked pitfall: the constraint was right
   and the distribution was wrong, and nothing in the language says the
   distribution had to be right.
3. **Uniform sampling over a constraint's solution space is a research
   problem, and the open tool imports the research.** Verilator 5.052's
   sampler is "UniGen2 - a near-uniform sampling algorithm" from Chakraborty,
   Fremont, Meel, Seshia and Vardi (TACAS 2015), adopted because the earlier
   sampler "can produce visibly skewed distributions and provide lower
   coverage of the solution space"
   [Verilator PR #8042, accessed 2026-09-12](https://github.com/verilator/verilator/pull/8042);
   Kitchen and Kuehlmann's ICCAD 2007 paper is the DV-specific statement of
   the same problem
   [Crossref record, accessed 2026-09-12](https://doi.org/10.1109/ICCAD.2007.4397275).
   The chapter can therefore say, with sources, that "uniform over the
   solutions" is neither guaranteed by the language nor cheap for a tool.
4. **A seed is a 32-bit number the simulator accepts, and everything else
   is methodology layered on top.** `dvsim` draws 256-bit seeds with
   `random.getrandbits(256)` and masks to 32 bits because "Systemverilog
   accepts seeds with a maximum size of 32 bits", then passes it as
   `+ntb_random_seed={svseed}` (VCS) or `+SVSEED={svseed}` (Xcelium); the
   run directory name carries the seed
   [lowRISC dvsim `deploy.py`, accessed 2026-09-12](https://github.com/lowRISC/dvsim/blob/main/src/dvsim/job/deploy.py),
   [OpenTitan `vcs.hjson`, accessed 2026-09-12](https://github.com/lowRISC/opentitan/blob/master/hw/dv/tools/dvsim/vcs.hjson),
   [OpenTitan `xcelium.hjson`, accessed 2026-09-12](https://github.com/lowRISC/opentitan/blob/master/hw/dv/tools/dvsim/xcelium.hjson).
   UVM then re-seeds every object from a hash of its type name and
   instance path with the global seed, which is what makes adding an object
   *not* perturb its neighbors
   [UVM-core `uvm_misc.svh`, accessed 2026-09-12](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_misc.svh).
   cocotb seeds Python's `random` from `int(time.time())` unless
   `COCOTB_RANDOM_SEED` is set and prints the seed at the start of every run
   [cocotb `_init.py`, accessed 2026-09-12](https://github.com/cocotb/cocotb/blob/master/src/cocotb/_init.py).
5. **The lowRISC style guide states the random-stability rule the chapter
   needs, in one sentence, with the reason.** `$random` and `$dist_*` "are
   not part of the SystemVerilog random stability model and can break
   simulation reproducibility"; `$srandom` "is not part of the SystemVerilog
   standard"
   [lowRISC DV coding style, accessed 2026-09-12](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).
   The same guide is the source for "constraint style affects solver
   performance": avoid loops in constraints, replace `foreach` with
   `inside`, prefer bit masks to modulus, split a constraint that "becomes
   too complex" and randomize the variables separately.
6. **Clause 18's 2023 numbering is confirmed only at the subclause level.**
   slang's table lists 18.3 Concepts and usage, 18.4 Random variables, 18.5
   Constraint blocks, 18.6 Randomization methods, 18.7 In-line constraints,
   18.8 Disabling random variables, 18.9 Controlling constraints, 18.10
   Dynamic constraint modification, 18.11 In-line random variable control,
   18.12 Randomization of scope variables, 18.13 Random number system
   functions, 18.14 Random stability, 18.15 Manually seeding randomize,
   18.16 Random weighted case, 18.17 Random sequence generation
   [slang, "Language Support", accessed 2026-09-12](https://sv-lang.com/language-support.html);
   Verilator's diagnostics cite 18.4 and 18.11 "IEEE 1800-2023"
   [Verilator `src/V3Randomize.cpp`, accessed 2026-09-12](https://github.com/verilator/verilator/blob/master/src/V3Randomize.cpp).
   The deeper numbers Verilator's PRs cite for `dist` (18.5.4), `solve
   before` (18.5.11), and `soft` (18.5.13) are given *against the 2017
   edition* and must not be printed as 2023 numbers.

---

### 1. Why constrained-random verification exists

#### 1.1 The argument as the originators made it

The case is older than SystemVerilog and rests on one observation: a
directed test exercises what its author thought of, and a design's bugs
are, by construction, in what nobody thought of. Bergeron's *Writing
Testbenches* framed the testbench as a self-checking program that generates
stimulus and predicts the response, and its second edition (2003) is the
one the book already cites for the constrained-random, coverage-driven
testbench as the object of verification engineering
[Crossref record for Bergeron 2003, accessed 2026-09-12](https://doi.org/10.1007/978-1-4615-0302-6)
[@bergeron2003testbenches]. Its SystemVerilog rewrite is a separate work,
*Writing Testbenches using SystemVerilog* (Springer, 2006)
[Crossref record, accessed 2026-09-12](https://doi.org/10.1007/0-387-31275-7),
and the *Verification Methodology Manual for SystemVerilog* (Bergeron,
Cerny, Hunter and Nightingale) carries a chapter titled exactly
"Coverage-Driven Verification"
[Crossref record for the VMM chapter, accessed 2026-09-12](https://doi.org/10.1007/0-387-25556-7_6),
[Crossref record for the book, accessed 2026-09-12](https://doi.org/10.1007/b135575).
None of these texts was read this run; the metadata is verified, the
content is not, and the chapter should cite them for *who said it and
when*, not for quotations.

The coverage-driven loop the VMM names is the method's actual claim:
random stimulus under constraints produces the cases the engineer did not
enumerate; functional coverage measures which of the cases that *matter*
have occurred; the engineer tightens or loosens constraints until coverage
closes. OpenTitan's methodology states the loop's premise in its own words:
"we rely on constrained-random techniques to generate the stimulus" for
IP-level verification, and on the question of when to stop, "Do we need 1,
10, or 100 tests and should they run 10, 100, or 1000 regressions? Only
coverage can answer this question for you"
[OpenTitan DV methodology, accessed 2026-09-12](https://opentitan.org/book/doc/contributing/dv/methodology/index.html)
[@opentitan-dv-methodology]. That is the sourced form of "constrained-random
without coverage is noise", and it is the sentence the chapter should hang
its motivation on.

The lineage. Constrained-random stimulus with functional coverage entered
practice through two proprietary testbench languages, *e* (Verisity's
Specman) and Vera (Synopsys), before it entered SystemVerilog. What is
sourced here is the standardization trail, not the corporate history: *e*
became IEEE 1647, with editions recorded by Crossref in 2006, 2008, 2017
and 2019
[Crossref records for IEEE 1647, accessed 2026-09-12](https://doi.org/10.1109/IEEESTD.2006.246244),
and SystemVerilog's first IEEE edition, 1800-2005, was approved
2005-11-08
[Crossref record for IEEE 1800-2005, accessed 2026-09-12](https://doi.org/10.1109/IEEESTD.2005.97972).
The Accellera SystemVerilog 3.1 documents that would source the OpenVera
donation returned 404 from every URL tried, so the chapter must not state
who donated what to whom (see Unsourced claims).

#### 1.2 The measured evidence, such as it is

There is no controlled study comparing constrained-random with directed
testing on a real design that this run could find. What exists is adoption
data. The 2020 Wilson Research Group study (commissioned by Siemens EDA, so
a vendor-sponsored survey, not a measurement of effectiveness) plots
"IC/ASIC project adoption trends for various simulation-based techniques
from 2012 through 2018, which include code coverage, functional coverage,
assertions, and constrained-random simulation" and reads the trend as the
market continuing "to mature its verification processes"
[Foster, WRG 2020 IC/ASIC report, p. 10, accessed 2026-09-12](https://uobdv.github.io/Design-Verification/WilsonResearchGroupFunctionalVerificationStudy/2020-WRGFV-Study/ic-asic-trend-report_2020-wilson-research-verification-study_hfoster.pdf)
[@foster2020wrg]. The percentages are in a figure (Fig. 20) that the text
extraction did not capture, so no number is quoted here. The 2022 series
establishes UVM as the predominant methodology
[Foster, WRG 2022 Part 10, 2022-12-26](https://blogs.sw.siemens.com/verificationhorizons/2022/12/26/part-10-the-2022-wilson-research-group-functional-verification-study/)
[@foster2022wrg], and UVM's user guide assumes the method: "random traffic
is created and sent to the DUT. The user can change the randomization seed
to achieve new test patterns"
[UVM 1.2 User's Guide §4.6, 2015-10-08](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf)
[@accellera2015uvmug]. The honest framing for the chapter: adoption is
near-universal and documented; effectiveness relative to directed testing
is an argument from the structure of the bug-finding problem, not a
measured result.

The peer-reviewed literature does record *why* the method is hard rather
than whether it works. IBM's stimulus generators are described as a
constraint-programming application in Naveh and Emek's CP 2005 abstract
and, at length, in Adir and Naveh's 2010 chapter "Stimuli Generation for
Functional Hardware Verification with Constraint Programming"
[Crossref records, accessed 2026-09-12](https://doi.org/10.1007/11564751_120),
[Adir and Naveh 2010, accessed 2026-09-12](https://doi.org/10.1007/978-1-4419-1644-0_16);
Kitchen and Kuehlmann's "Stimulus generation for constrained random
simulation" (ICCAD 2007, pp. 258–265) is the paper that poses stimulus
generation as *sampling* a solution space rather than merely finding a
point in it
[Crossref record, accessed 2026-09-12](https://doi.org/10.1109/ICCAD.2007.4397275).
Abstracts were not retrievable (IEEE Xplore and the ACM DL refused the
fetch); the titles and venues are verified.

### 2. What a constraint solver does

#### 2.1 Satisfiability modulo theories in one paragraph

A constraint block is a formula over the `rand` variables; `randomize()`
asks for an assignment that makes it true. That is a satisfiability
problem, and because the variables are fixed-width bit-vectors and the
constraints use arithmetic, comparison and array indexing, it is
satisfiability *modulo a theory* rather than plain Boolean SAT. The SMT-LIB
standard defines the field: "Satisfiability Modulo Theories (SMT) is an
area of automated deduction that studies methods for checking the
satisfiability of first-order formulas with respect to some logical theory
T of interest", and the defining problem is "whether there is a model of T
that makes ϕ true"
[SMT-LIB Standard v2.6, 2017-07-18, §1.2 and §2.1](https://smt-lib.org/papers/smt-lib-reference-v2.6-r2017-07-18.pdf).
SMT-LIB "calls an SMT solver any software system that implements a
procedure for satisfiability modulo some given theory" and lists the
interface a solver may offer beyond a yes/no answer: "the ability to return
concrete solutions for satisfiable inputs, return proofs for unsatisfiable
ones, allow incremental and backtrackable input" (§2.1). The command
language is what a simulator actually speaks: `check-sat` asks the solver
"to search for a model of the logic that satisfies all the currently
asserted formulas", and the answer is one of `sat`, `unsat`, or `unknown`,
where "an unknown response [indicates] that the search was
inconclusive—because of resource limits, solver incompleteness, or other
reasons"; after `sat` the solver answers `get-value` and `get-model`
(§4.2.5). SMT-LIB is "an international initiative aimed at facilitating
research and development in Satisfiability Modulo Theories"; the current
reference document is Version 2.7 by Barrett, Fontaine and Tinelli, with
releases dated 2025-02-05, 2025-07-07 and 2026-03-27
[SMT-LIB home, accessed 2026-09-12](https://smt-lib.org/),
[SMT-LIB language page](https://smt-lib.org/language.shtml),
[SMT-LIB news](https://smt-lib.org/news.shtml). Version 2.6 is cited here
because its text was read; 2.7 was not.

Two open solvers matter to this book. z3 describes itself as "a theorem
prover from Microsoft Research", MIT-licensed, taking SMT-LIB 2 as its
default input
[Z3Prover/z3 README, accessed 2026-09-12](https://github.com/Z3Prover/z3);
its paper is de Moura and Bjørner, "Z3: An Efficient SMT Solver", TACAS
2008, LNCS, pp. 337–340
[Crossref record, accessed 2026-09-12](https://doi.org/10.1007/978-3-540-78800-3_24).
cvc5 "is a tool for determining the satisfiability of a first order formula
modulo a first order theory (or a combination of such theories)",
BSD-3-Clause, from Stanford and the University of Iowa
[cvc5 README, accessed 2026-09-12](https://github.com/cvc5/cvc5),
[cvc5 home](https://cvc5.github.io/); its paper is Barbosa et al., "cvc5: A
Versatile and Industrial-Strength SMT Solver", TACAS 2022, pp. 415–442
[Crossref record, accessed 2026-09-12](https://doi.org/10.1007/978-3-030-99524-9_24).
Neither paper's text was read; the metadata is from Crossref.

#### 2.2 A simulator's solver pipeline, readable end to end

Commercial simulators hide their solvers. Verilator does not, and its
runtime is the one place a reader can watch a `constraint` become an SMT
query. The environment variable is documented as: "If set, the command to
run as a constrained randomization backend, such as `cvc4 --lang=smt2
--incremental`. If not specified, it will use the one supplied or found
during configure, or `z3 --in` if empty"
[Verilator docs, `environment.rst`, accessed 2026-09-12](https://github.com/verilator/verilator/blob/master/docs/guide/environment.rst);
the compiled-in default is `"z3 --in"`
[Verilator `include/verilated.cpp`, accessed 2026-09-12](https://github.com/verilator/verilator/blob/master/include/verilated.cpp).
The runtime forks the solver, probes it with `(set-logic QF_ABV)`
`(check-sat)` `(reset)`, and on failure prints "Unable to communicate with
SAT solver, please check its installation or specify a different one in
VERILATOR_SOLVER environment variable"; each `randomize()` sets
`:produce-models true`, asserts the constraints as `(assert (= #b1 ...))`,
issues `(check-sat)`, and reads the assignment back with `(get-value ...)`;
on `unsat` it re-runs with `:produce-unsat-cores true` and reports the
conflicting constraints by source location; on `unknown` it warns once
that "randomize() may return 0"; after three consecutive failures it
disables itself ("Solver failed repeatedly, so randomize() returns 0 from
now on")
[Verilator `include/verilated_random.cpp`, accessed 2026-09-12](https://github.com/verilator/verilator/blob/master/include/verilated_random.cpp).
The theory it selects, `QF_ABV`, is quantifier-free arrays and bit-vectors,
which is precisely what `rand` variables, `inside`, and `foreach` over
arrays need. That is the whole story of "what does `randomize()` do": build
a formula, ask a decision procedure, decode the model, and return 1 or 0.

Chapter 5's note already recorded the consequence on this machine: with no
`z3` on the PATH, every constrained `randomize()` on Verilator 5.030 warns
and returns 0, so the fields stay at their reset values
(`research/ch05-testbench-language.md`, Part C). Chapter 7's examples
require the solver to be installed and the Makefile to say so.

### 3. Solver freedom and distributions

#### 3.1 What the language promises, and what it does not

IEEE 1800-2023 is paywalled and unread; what can be said about its
distribution guarantees comes from what open compilers cite against it and
from what their bug trackers assume. Clause 18's subclauses (18.3–18.17)
are listed in §Findings 6; among them, 18.14 "Random stability" and 18.15
"Manually seeding randomize" are the ones the seed discussion needs, and
18.5 "Constraint blocks" holds `dist`, `solve..before` and `soft`, whose
2017-edition sub-numbers Verilator's PRs cite as 18.5.4, 18.5.11 and 18.5.13
[Verilator PRs #7168, #7123, #7166, accessed 2026-09-12](https://github.com/verilator/verilator/pull/7168).
Verilator's own warning text states the portability consequence of a
tool's deviation without appealing to any guarantee: ignoring
`CONSTRAINTIGN` "may make Verilator randomize() simulations differ from
other simulators"
[Verilator warnings, accessed 2026-09-12](https://verilator.org/guide/latest/warnings.html)
[@verilator-warnings]. Two simulators that both satisfy every constraint
can, and do, return different value sequences for the same seed; a
testbench whose *checking* depends on the sequence is not portable, and a
testbench whose *coverage closure* depends on it will close on one tool
and not another. The chapter should state this as a property of the
problem, not as a defect of any tool, and the evidence that it is a
property of the problem is §3.2.

#### 3.2 "Uniform over the solution space" is not what a solver gives you

A decision procedure answers "is there a model?" and hands back one. The
SMT-LIB command semantics say exactly that: "A sat response indicates that
the solver has found a model" (§4.2.5, cited above). Nothing in the
protocol makes the model a random draw. Verilator's maintainers hit this
in the simplest constraint imaginable: "An SMT solver returns _some_
satisfying model, not a uniform one: for `value < 2^N` it keeps returning
the boundary value `K-1`", and the reported symptom was low bits set in
65–90% of trials against an expected ~50%
[Verilator PR #7684, accessed 2026-09-12](https://github.com/verilator/verilator/pull/7684),
[Verilator issue #7563](https://github.com/verilator/verilator/issues/7563).
Every solver-backed randomizer must therefore add randomness *on top of*
the decision procedure, and the runtime shows three ways: pinning each free
bit to a random target through an assumption literal and dropping
conflicting pins one per round "so the maximal compatible set survives"
(#7684); asserting random XOR equations over the variable bits; and,
since 5.052, UniGen2 hashing, which partitions the solution space into
cells with random XOR constraints and enumerates a cell
[Verilator `verilated_random.cpp`, accessed 2026-09-12](https://github.com/verilator/verilator/blob/master/include/verilated_random.cpp),
[Verilator PR #8042](https://github.com/verilator/verilator/pull/8042).
PR #8042's motivation is the clearest statement of the problem in a DV
tool: the prior sampler "can produce visibly skewed distributions and
provide lower coverage of the solution space", and the PR reports
solution-space coverage rising from 92.32% to 100% on one benchmark and
from 98.66% to 100% on another at a 25x budget (the PR's own measurements,
on its own benchmarks; not independent). The algorithm is Chakraborty,
Fremont, Meel, Seshia and Vardi, "On Parallel Scalable Uniform SAT Witness
Generation", TACAS 2015, LNCS, pp. 304–319
[Crossref record, accessed 2026-09-12](https://doi.org/10.1007/978-3-662-46681-0_25),
and the DV statement of the requirement is Kitchen and Kuehlmann (ICCAD
2007), cited in §1.2. The chapter's teaching point: a solver-backed
`randomize()` is a *sampler bolted onto a decision procedure*, and the
quality of the sampler is a tool property that no constraint can fix.

Even a perfect uniform sampler is rarely what the engineer meant. Uniform
over `{addr, len}` with `addr + len <= 4096` is dominated by small `len`
because there are more solutions there; uniform over a 32-bit field
almost never produces 0, all-ones, or a power of two. The three language
mechanisms exist to change *which* distribution is sampled, not which
values are legal:

- **`dist`** attaches weights to values or ranges (`:=` per value, `:/`
  shared across a range). Verilator's issue #6811 shows how visibly this
  matters: `value dist {[0:100] :/ 70, [101:255] :/ 30}` produced 35–38%
  in the first range on a tool that ignored the weights; the fix (PR
  #7168, 5.048) selects a weighted bucket by a random variable and
  emits an if-chain of constraints, "making the weighted selection before
  constraint solving completes"
  [Verilator issue #6811](https://github.com/verilator/verilator/issues/6811),
  [Verilator PR #7168](https://github.com/verilator/verilator/pull/7168).
  That implementation is a good picture of what `dist` *is*: a weighted
  choice of sub-problem, then a solve.
- **`solve a before b`** orders the solve so `a` is drawn without regard
  to how many `b` values each `a` admits. Verilator implements it exactly
  that way: variables are topologically sorted into layers, each layer is
  solved "with ALL constraints asserted", and earlier layers' values are
  "pinned" as equalities in the next phase
  [Verilator PR #7123, accessed 2026-09-12](https://github.com/verilator/verilator/pull/7123).
  The consequence the chapter must state: the set of legal solutions is
  unchanged (every phase asserts every constraint), only their frequencies
  move. (That this is also the standard's statement is believed but
  unread; see Unsourced claims.)
- **`soft`** constraints are preferences the solver drops when they
  conflict with hard constraints, with later soft constraints winning over
  earlier ones. Verilator's issue #7124 states the expected semantics it
  set out to implement: soft constraints are "relaxed (silently dropped)
  when they conflict with hard constraints; `randomize()` returns 1",
  "the last-declared one takes priority", and `UNSATCONSTR` "is only
  reported when hard constraints are mutually unsatisfiable"
  [Verilator issue #7124, accessed 2026-09-12](https://github.com/verilator/verilator/issues/7124);
  the runtime does it by re-adding soft constraints highest priority first
  under `push`/`pop` and discarding those that make the set `unsat`
  [Verilator `verilated_random.cpp`](https://github.com/verilator/verilator/blob/master/include/verilated_random.cpp).
  A `soft` default in a base sequence that a test overrides with a hard
  in-line constraint is the idiom; PR #7963 records the trap when features
  interact: with `solve..before` present, "all soft constraints were
  dropped" and `randomize()` still returned 1
  [Verilator PR #7963, accessed 2026-09-12](https://github.com/verilator/verilator/pull/7963).

**Corner-case bias.** None of the three mechanisms finds a corner the
engineer did not name. The methodology answer, visible in OpenTitan's
style, is explicit: knobs weighted by percentage, `dist` clauses that put
mass on boundaries, and separate randomization of the variables a
"too complex" constraint entangles
[lowRISC DV coding style, accessed 2026-09-12](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md)
[@lowrisc-dv-style]. The chapter can generalize: a `dist` on a boundary is
a directed test in disguise, and that is fine, because the coverage model
(not the constraint) is where "did we hit the corner?" is answered.

#### 3.3 Overconstraint and underconstraint, and how each is found

*Overconstraint* is a constraint set with no solution, or with a solution
space so small the interesting cases are excluded. The unsatisfiable form
is loud: `randomize()` returns 0 and a solver-backed tool can say why.
Verilator's `UNSATCONSTR` warning is "issued at simulation runtime when
the SMT solver determines that the combination of constraints is
unsatisfiable. Each unsatisfied constraint is reported with its source
location to help identify conflicting constraints"
[Verilator warnings, accessed 2026-09-12](https://verilator.org/guide/latest/warnings.html),
and the runtime obtains that list with `(get-unsat-core)`
[Verilator `verilated_random.cpp`](https://github.com/verilator/verilator/blob/master/include/verilated_random.cpp).
The *quiet* form (satisfiable but too narrow) is found only by coverage,
which is why OpenTitan wraps every call in `DV_CHECK_RANDOMIZE_FATAL` (so a
0 return is a fatal, not a silent reset value) and reads coverage to decide
when it is done
[lowRISC DV coding style](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md),
[OpenTitan DV methodology](https://opentitan.org/book/doc/contributing/dv/methodology/index.html).
The lowRISC rule "Do not use `assert()` to check manual randomization
calls, use the provided macros instead" exists because an ignored return
value is the most common way an overconstrained test passes.

*Underconstraint* is the opposite: legal but meaningless stimulus (an
address the DUT does not decode, a length the protocol forbids), which
shows up as scoreboard mismatches or, worse, as coverage of nothing. It is
diagnosed by the checker, not the solver, and the language offers no
help; this is where the constraint set meets the specification, and it is
Part A's territory to say how constraints encode protocol legality.

#### 3.4 Solver performance and constraint style

The lowRISC guide is the only open, primary source found that states
performance rules, and it states them as rules without measurements:
"Avoid using loops in constraints whenever possible. In some cases,
`foreach` can be replaced by `inside`"; "avoid doing calculations inside
the loops"; "use bitmasking operations over modulus operations, as
bitmasking operations are much faster"; and "If a constraint becomes too
complex, it is highly recommended to split the constraint and separately
randomize all relevant variables"; when randomizing an array of objects,
iterate and randomize each object rather than the array
[lowRISC DV coding style, accessed 2026-09-12](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).
Why these rules hold follows from §2: a `foreach` over N elements becomes
N copies of the body in the formula; multiplication and modulus by
non-constants are hard for bit-vector decision procedures where a mask is
a single bit-select; and one formula over all variables is solved as one
problem, so splitting it trades solver freedom for tractability. Verilator
adds two facts about *when* a solver is slow: `unknown` (time-out or
incompleteness) is a possible answer, warned once; and the tool
deliberately skips UniGen2 on the first `randomize()` per constraint set
"to amortize setup costs" and disables it for `randc`, `solve..before`,
frozen variables and soft constraints
[Verilator `verilated_random.cpp`](https://github.com/verilator/verilator/blob/master/include/verilated_random.cpp),
[Verilator PR #8042](https://github.com/verilator/verilator/pull/8042).
No vendor performance figure was found in an open document; the chapter
should give none.

### 4. Seeds and reproducibility

#### 4.1 What a seed determines

A seed is the initial state of a pseudo-random generator; the sequence of
values a simulation draws is a function of the seed and of the *order and
number* of draws. That second half is the methodology problem. Verilator's
manual states its own model plainly: "There is one random seed per C
thread, not per module for $random, nor per object for random stability of
$urandom/$urandom_range"
[Verilator language limitations, accessed 2026-09-12](https://verilator.org/guide/latest/languages.html)
[@verilator-languages], and the seed is set with `+verilator+seed+<value>`:
"If not specified, the seed defaults to 1. If specified as 0, a non-zero
seed is generated at startup; the picked value is exposed through
`$get_initial_random_seed` so the run can be reproduced later"
[Verilator runtime arguments, accessed 2026-09-12](https://verilator.org/guide/latest/exe_sim.html).
The manual's wording names the standard's clause by its title (18.14
"Random stability", confirmed in slang's table) while saying Verilator does
not implement it; that is a clean, sourced way for the chapter to explain
what the clause is *for*. Verilator issue #6945 is the cautionary case
about seeds and generators: for single-bit signals the reset-value
randomization reduced to XOR with the seed, so the seed "is only able to
flip the bit when it is odd, and not when it is even"
[Verilator issue #6945, accessed 2026-09-12](https://github.com/verilator/verilator/issues/6945);
fixed at 5.044 ("Fix variable randomization to better differ by seed")
[Verilator Changes](https://github.com/verilator/verilator/blob/master/Changes).
A seed only reproduces; it does not by itself guarantee that different
seeds explore differently.

#### 4.2 Random stability as a methodology concern

If every object draws from one thread-level stream, adding a variable,
an object or a `$urandom` call anywhere earlier in the run shifts every
later value: a regression that passed on seed 42 fails on seed 42 after an
unrelated edit, and the failing seed from last night cannot be replayed on
today's testbench. The standard's answer (18.14) is per-thread and
per-object generators; UVM's answer is stricter and readable in its
source. `uvm_object::reseed` "Calls ~srandom~ on the object to reseed the
object using the UVM seeding mechanism, which sets the seed based on type
name and instance name instead of based on instance position in a thread"
[UVM-core `uvm_object.svh`, accessed 2026-09-12](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_object.svh)
[@uvm-core]; the seed is `uvm_oneway_hash({type_id,"::",inst_id},
uvm_global_random_seed)`, where `uvm_global_random_seed = $urandom` is
"based off of the global seed ... but will change if the command line seed
setting is changed", and `uvm_create_random_seed` "updates the seed map so
that if the same string is used again, a new value will be generated"
[UVM-core `uvm_misc.svh`, accessed 2026-09-12](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_misc.svh).
So a UVM component's stream depends on the simulator seed, its type, its
path, and how many objects of that type and path came before it, and on
nothing else. That is what makes "add a monitor" not perturb the driver.
The lowRISC guide's two prohibitions are the practical rules: `$random`
and `$dist_*` "are not part of the SystemVerilog random stability model
and can break simulation reproducibility"; `$srandom` "is not part of the
SystemVerilog standard. Use `process::self().srandom()` instead"
[lowRISC DV coding style](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).

#### 4.3 Regression seeds: OpenTitan's `dvsim`

OpenTitan's nightly regression is defined by seeds: "Run each constrained
random test with a sufficiently large number of seeds (arbitrarily chosen
to be 100)" and "Pass completely random seed values to the simulator when
running the tests"
[OpenTitan DV methodology, accessed 2026-09-12](https://opentitan.org/book/doc/contributing/dv/methodology/index.html).
The mechanism, now in the separate `lowRISC/dvsim` repository: a run job
"is one per seed for each test"; seeds come from `random.getrandbits(256)`
in batches of 1000 unless `--fixed-seed` is set; "Systemverilog accepts
seeds with a maximum size of 32 bits", so `svseed = seed & 0xFFFFFFFF`;
and the job's qualified name is `run_dir_name + "." + str(seed)`
[dvsim `src/dvsim/job/deploy.py`, accessed 2026-09-12](https://github.com/lowRISC/dvsim/blob/main/src/dvsim/job/deploy.py).
The command-line contract: `--fixed-seed S` "Run all items with the seed
S. This implies --reseed 1"; `--reseed N` "Override any reseed value in
the test configuration and run each test N times, with a new seed each
time"; `--reseed-multiplier N` scales every test's configured count "while
maintaining the ratio of numbers of runs between different tests"
[dvsim `src/dvsim/cli/run.py`, accessed 2026-09-12](https://github.com/lowRISC/dvsim/blob/main/src/dvsim/cli/run.py).
The simulator sees it as `+ntb_random_seed={svseed}` (VCS) or
`+SVSEED={svseed}` (Xcelium), and the coverage database directory is named
`{run_dir_name}.{svseed}`
[OpenTitan `vcs.hjson`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/tools/dvsim/vcs.hjson),
[OpenTitan `xcelium.hjson`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/tools/dvsim/xcelium.hjson).
Replay is a documented step: "Since the CI runs tests with pseudo-random
behaviour driven from 'seed' numbers, to be confident of reproducing the
failure we must supply the exact seed that CI used", with
`dvsim ... -i uart_smoke --fixed-seed=<seed>`
[OpenTitan "Setup DV", accessed 2026-09-12](https://opentitan.org/book/doc/getting_started/setup_dv.html).

#### 4.4 cocotb, for the book's Python examples

cocotb seeds Python's `random` module once per run: the default is
`int(time.time())`, overridden by `COCOTB_RANDOM_SEED` (the old
`RANDOM_SEED` and the plusargs `+ntb_random_seed` and `+seed` are accepted
with deprecation warnings), and the run logs "Seeding Python random module
with <seed>"
[cocotb `src/cocotb/_init.py`, accessed 2026-09-12](https://github.com/cocotb/cocotb/blob/master/src/cocotb/_init.py).
The manual: "Seed the Python random module to recreate a previous test
stimulus. At the beginning of every test a message is displayed with the
seed used for that execution", and "To recreate the same stimuli use the
following: `make COCOTB_RANDOM_SEED=1377424946`"
[cocotb library reference, accessed 2026-09-12](https://docs.cocotb.org/en/stable/library_reference.html)
[@cocotb-docs]. This seeds Python only; the HDL simulator's own generator
(Verilator's `+verilator+seed`) is separate, and a cocotb test that mixes
`$urandom` in RTL with Python `random` has two seeds to record.

#### 4.5 What a failing seed is worth

A failing seed is the cheapest bug report in verification: one number that
reproduces a scenario nobody wrote, on the same testbench revision. Its
value decays with every change that breaks random stability, which is why
OpenTitan records the seed in the run directory name and its CI
instructions begin with "supply the exact seed that CI used". The chapter
should say three things about it: record the seed with the testbench
commit, not alone; replay it before touching the constraint (a "fix" that
moves the distribution can hide the failure without fixing the design);
and once understood, convert it into a directed or `dist`-biased test and a
coverage bin, because the seed will stop finding it as soon as the
constraints change.

### Unsourced-claims table

| Claim | Status | What the chapter may say |
|---|---|---|
| IEEE 1800-2023 states that `solve..before` changes the distribution but not the set of solutions | Believed; the standard's text is unread. Verilator's phased implementation (every phase asserts all constraints) is consistent with it. | Describe the semantics from the implementation; do not attribute the wording to the standard or print a sub-clause number. |
| IEEE 1800-2023 says or implies that values are drawn uniformly over the solution space absent `dist`/`solve before` | Unread. | Say the language does not specify *which* solution a solver returns and that uniformity is a tool property; cite Verilator #7684 and PR #8042. |
| The 2023 sub-clause numbers for `dist`, `solve before`, `soft` | Only 2017 numbers (18.5.4, 18.5.11, 18.5.13) are cited by Verilator PRs; 2023 top-level numbers 18.3–18.17 confirmed by slang. | Cite clause 18 or the top-level subclause only. |
| Vera (Synopsys) and OpenVera were donated to Accellera for SystemVerilog 3.1; *e* came from Verisity, acquired by Cadence | Not sourced this run: every Accellera SV 3.1/3.1a URL returned 404; no press release fetched. IEEE 1647 editions are sourced. | Name *e*/IEEE 1647 and SystemVerilog/IEEE 1800-2005 as the standardized lineage; do not name donors or acquisitions. |
| Bergeron's *Writing Testbenches* first edition (2000) | No Crossref record found. | Cite the 2003 second edition and the 2006 SystemVerilog edition only. |
| Constrained-random adoption percentages (WRG 2020, Fig. 20) | In a figure; not extractable from the PDF text. | Say the study plots the trend 2012–2018; give no percentage. |
| Abstracts and content of Kitchen & Kuehlmann 2007, Naveh & Emek 2005, Adir & Naveh 2010, de Moura & Bjørner 2008, Barbosa et al. 2022, Chakraborty et al. 2015 | Metadata verified via Crossref; texts unread. | Cite for title, venue, year and for the topic their titles state; no quotations. |
| Content of the VMM and both Bergeron books | Metadata verified; texts unread. | Cite for who/when; no quotations, no paraphrase of their argument as theirs. |
| PR #8042's coverage/JSD improvements | The PR's own benchmarks. | Label as the maintainers' measurement on their tests. |
| "UVM re-seeds every object in `new()`" | `uvm_object::new` shown does **not** call `reseed()`; `uvm_component` may; not checked. | Say `reseed()` exists and what it hashes; do not say when it is called without checking `uvm_component.svh`. |

### Key sources

```bibtex
@misc{smtlib-home,
  author       = {{The SMT-LIB Initiative}},
  title        = {{SMT-LIB}: The Satisfiability Modulo Theories Library},
  year         = {2026},
  url          = {https://smt-lib.org/},
  note         = {Version 2.7 reference releases 2025-02-05, 2025-07-07, 2026-03-27. Accessed 2026-09-12}
}
@techreport{barrett2017smtlib26,
  author      = {Clark Barrett and Pascal Fontaine and Cesare Tinelli},
  title       = {The {SMT-LIB} Standard: Version 2.6},
  institution = {The SMT-LIB Initiative},
  year        = {2017},
  url         = {https://smt-lib.org/papers/smt-lib-reference-v2.6-r2017-07-18.pdf},
  note        = {Release 2017-07-18. Sections 1.2, 2.1, 4.2.5 read. Accessed 2026-09-12}
}
@inproceedings{demoura2008z3,
  author    = {Leonardo de Moura and Nikolaj Bj{\o}rner},
  title     = {{Z3}: An Efficient {SMT} Solver},
  booktitle = {Tools and Algorithms for the Construction and Analysis of Systems (TACAS)},
  series    = {Lecture Notes in Computer Science},
  publisher = {Springer},
  year      = {2008},
  pages     = {337--340},
  doi       = {10.1007/978-3-540-78800-3_24},
  url       = {https://doi.org/10.1007/978-3-540-78800-3_24},
  note      = {Metadata from Crossref; text not consulted. Accessed 2026-09-12}
}
@misc{z3-repo,
  author       = {{Microsoft Research}},
  title        = {{Z3} Theorem Prover},
  howpublished = {GitHub, Z3Prover/z3},
  year         = {2026},
  url          = {https://github.com/Z3Prover/z3},
  note         = {MIT license. Accessed 2026-09-12}
}
@inproceedings{barbosa2022cvc5,
  author    = {Haniel Barbosa and Clark Barrett and Martin Brain and Gereon Kremer and Hanna Lachnitt and Makai Mann and Abdalrhman Mohamed and Mudathir Mohamed and Aina Niemetz and Andres N{\"o}tzli and Alex Ozdemir and Mathias Preiner and Andrew Reynolds and Ying Sheng and Cesare Tinelli and Yoni Zohar},
  title     = {{cvc5}: A Versatile and Industrial-Strength {SMT} Solver},
  booktitle = {Tools and Algorithms for the Construction and Analysis of Systems (TACAS)},
  series    = {Lecture Notes in Computer Science},
  publisher = {Springer},
  year      = {2022},
  pages     = {415--442},
  doi       = {10.1007/978-3-030-99524-9_24},
  url       = {https://doi.org/10.1007/978-3-030-99524-9_24},
  note      = {Metadata from Crossref; text not consulted. Accessed 2026-09-12}
}
@misc{cvc5-repo,
  author       = {{cvc5 developers}},
  title        = {{cvc5}},
  howpublished = {GitHub, cvc5/cvc5},
  year         = {2026},
  url          = {https://github.com/cvc5/cvc5},
  note         = {BSD-3-Clause. Accessed 2026-09-12}
}
@inproceedings{kitchen2007stimulus,
  author    = {Nathan Kitchen and Andreas Kuehlmann},
  title     = {Stimulus Generation for Constrained Random Simulation},
  booktitle = {IEEE/ACM International Conference on Computer-Aided Design (ICCAD)},
  publisher = {IEEE},
  year      = {2007},
  pages     = {258--265},
  doi       = {10.1109/ICCAD.2007.4397275},
  url       = {https://doi.org/10.1109/ICCAD.2007.4397275},
  note      = {Metadata from Crossref; text not consulted. Accessed 2026-09-12}
}
@inproceedings{chakraborty2015unigen2,
  author    = {Supratik Chakraborty and Daniel J. Fremont and Kuldeep S. Meel and Sanjit A. Seshia and Moshe Y. Vardi},
  title     = {On Parallel Scalable Uniform {SAT} Witness Generation},
  booktitle = {Tools and Algorithms for the Construction and Analysis of Systems (TACAS)},
  series    = {Lecture Notes in Computer Science},
  publisher = {Springer},
  year      = {2015},
  pages     = {304--319},
  doi       = {10.1007/978-3-662-46681-0_25},
  url       = {https://doi.org/10.1007/978-3-662-46681-0_25},
  note      = {Metadata from Crossref; text not consulted. Accessed 2026-09-12}
}
@incollection{adir2010stimuli,
  author    = {Allon Adir and Yehuda Naveh},
  title     = {Stimuli Generation for Functional Hardware Verification with Constraint Programming},
  booktitle = {Hybrid Optimization},
  series    = {Springer Optimization and Its Applications},
  publisher = {Springer},
  year      = {2010},
  pages     = {509--558},
  doi       = {10.1007/978-1-4419-1644-0_16},
  url       = {https://doi.org/10.1007/978-1-4419-1644-0_16},
  note      = {Metadata from Crossref; text not consulted. Accessed 2026-09-12}
}
@book{bergeron2006testbenches,
  author    = {Janick Bergeron},
  title     = {Writing Testbenches using {SystemVerilog}},
  publisher = {Springer},
  year      = {2006},
  isbn      = {978-0-387-29221-2},
  doi       = {10.1007/0-387-31275-7},
  url       = {https://doi.org/10.1007/0-387-31275-7},
  note      = {Metadata from Crossref; text not consulted. Accessed 2026-09-12}
}
@book{bergeron2005vmm,
  author    = {Janick Bergeron and Eduard Cerny and Alan Hunter and Andrew Nightingale},
  title     = {Verification Methodology Manual for {SystemVerilog}},
  publisher = {Springer},
  year      = {2006},
  isbn      = {0-387-25538-9},
  doi       = {10.1007/b135575},
  url       = {https://doi.org/10.1007/b135575},
  note      = {Crossref gives print year 2006; chapter "Coverage-Driven Verification" doi:10.1007/0-387-25556-7\_6 dated 2005. Author list from the chapter record was empty; authors as commonly listed, unverified. Text not consulted. Accessed 2026-09-12}
}
@misc{ieee1647-2019,
  author       = {{IEEE}},
  title        = {{IEEE} Std 1647-2019, {IEEE} Standard for the Functional Verification Language e},
  howpublished = {IEEE},
  year         = {2019},
  doi          = {10.1109/IEEESTD.2019.8793253},
  url          = {https://doi.org/10.1109/IEEESTD.2019.8793253},
  note         = {Earlier editions 2006 (doi:10.1109/IEEESTD.2006.246244), 2008, 2017. Metadata from Crossref. Accessed 2026-09-12}
}
@misc{ieee1800-2005,
  author       = {{IEEE}},
  title        = {{IEEE} Std 1800-2005, {IEEE} Standard for {SystemVerilog}: Unified Hardware Design, Specification and Verification Language},
  howpublished = {IEEE},
  year         = {2005},
  doi          = {10.1109/IEEESTD.2005.97972},
  url          = {https://doi.org/10.1109/IEEESTD.2005.97972},
  note         = {Approved 2005-11-08 per Crossref. Accessed 2026-09-12}
}
@misc{verilator-random-runtime,
  author       = {{Verilator contributors}},
  title        = {Verilator runtime: constrained randomization (\texttt{include/verilated\_random.cpp})},
  howpublished = {GitHub, verilator/verilator},
  year         = {2026},
  url          = {https://github.com/verilator/verilator/blob/master/include/verilated_random.cpp},
  note         = {Also docs/guide/environment.rst (VERILATOR\_SOLVER), include/verilated.cpp (default "z3 --in"), src/V3Randomize.cpp. Accessed 2026-09-12}
}
@misc{verilator-pr8042,
  author       = {{Verilator contributors}},
  title        = {Add {UniGen2} constrained randomization algorithm (PR \#8042)},
  howpublished = {GitHub, verilator/verilator},
  year         = {2026},
  url          = {https://github.com/verilator/verilator/pull/8042},
  note         = {Related: PR \#7684 and issue \#7563 (biased distribution), PR \#7123 (solve..before), PR \#7166 and issue \#7124 (soft), PR \#7168 and issue \#6811 (dist), PR \#7963, issue \#6945, PR \#7991. Accessed 2026-09-12}
}
@misc{dvsim-repo,
  author       = {{lowRISC contributors}},
  title        = {dvsim: a build and run system for {EDA} tool flows},
  howpublished = {GitHub, lowRISC/dvsim},
  year         = {2026},
  url          = {https://github.com/lowRISC/dvsim},
  note         = {Files cited: src/dvsim/cli/run.py (--fixed-seed, --reseed, --reseed-multiplier), src/dvsim/job/deploy.py (seed generation). Accessed 2026-09-12}
}
@misc{opentitan-setup-dv,
  author       = {{lowRISC contributors (OpenTitan project)}},
  title        = {{OpenTitan}: Setup DV (reproducing a CI failure with --fixed-seed)},
  howpublished = {OpenTitan documentation},
  year         = {2026},
  url          = {https://opentitan.org/book/doc/getting_started/setup_dv.html},
  note         = {Accessed 2026-09-12}
}
@misc{opentitan-dvsim-tool-cfgs,
  author       = {{lowRISC contributors (OpenTitan project)}},
  title        = {{OpenTitan} dvsim tool configurations: vcs.hjson and xcelium.hjson},
  howpublished = {GitHub, lowRISC/opentitan},
  year         = {2026},
  url          = {https://github.com/lowRISC/opentitan/blob/master/hw/dv/tools/dvsim/vcs.hjson},
  note         = {+ntb\_random\_seed={svseed}; xcelium.hjson uses +SVSEED={svseed}. Accessed 2026-09-12}
}
@misc{cocotb-init-seed,
  author       = {{cocotb contributors}},
  title        = {cocotb source: seeding in \texttt{src/cocotb/\_init.py}},
  howpublished = {GitHub, cocotb/cocotb},
  year         = {2026},
  url          = {https://github.com/cocotb/cocotb/blob/master/src/cocotb/_init.py},
  note         = {COCOTB\_RANDOM\_SEED; default int(time.time()). Accessed 2026-09-12}
}
```
Reused existing keys: `ieee1800-2023`, `bergeron2003testbenches`,
`accellera2015uvmug`, `uvm-core`, `opentitan-dv-methodology`,
`lowrisc-dv-style`, `verilator-changes`, `verilator-languages`,
`verilator-warnings`, `foster2020wrg`, `foster2022wrg`, `cocotb-docs`.

### Confidence notes

- **High** (read at the source): Verilator change-log dates and entries;
  `verilated_random.cpp` protocol, sampling, soft-constraint relaxation and
  failure handling; VERILATOR_SOLVER documentation and default; warning
  texts; PR/issue quotations (#7684, #7563, #8042, #7123, #7166, #7124,
  #7168, #6811, #7963, #6945, #7991); slang's clause-18 table; SMT-LIB 2.6
  §1.2, §2.1, §4.2.5; SMT-LIB site version/release dates; z3 and cvc5
  README self-descriptions and licenses; lowRISC DV style rules; OpenTitan
  methodology regression sentences and the setup-DV replay instruction;
  `dvsim` seed code and CLI help; `vcs.hjson`/`xcelium.hjson` seed
  plusargs; UVM-core `reseed`/`uvm_create_random_seed` text; cocotb
  `_init.py` and manual text; UVM 1.2 UG §4.6 sentence; WRG 2020 p. 10
  sentence.
- **Medium**: the 2017-edition sub-clause numbers, taken from Verilator
  PRs; the claim that the sampling approach in PR #8042 was enabled in
  release 5.052 (the change log lists it there; not run).
- **Low / not verified**: everything in the Unsourced-claims table; the
  VMM author list; whether `uvm_component` calls `reseed()`; that no
  open vendor performance figures exist (none found, not proven absent).
- **Not measured this run**: nothing was executed. The 5.030 behavior of
  `solve before`/`soft` (CONSTRAINTIGN, `randomize()` returns 1) is
  Chapter 5's measurement, reused.

---

# Part C — What the open tools do with randomization, measured with and without a solver

Scope: for every randomization construct Chapter 7 teaches — `rand` and
`randc`, unconstrained and constrained `randomize()`, inline `with`
constraints, `inside`, both weight forms of `dist`, implication and
`if`/`else`, `foreach`, `solve … before`, `soft`, `unique`,
`constraint_mode` and `rand_mode`, `pre_/post_randomize`,
`std::randomize`, `$urandom` and `$urandom_range`, seeding, and object and
thread stability — what Verilator 5.030 and Icarus Verilog 13.0 compile,
run and print, first as the book's environment stands (no SMT solver on
PATH) and then with a `z3` binary obtained from the `z3-solver` pip wheel
in a throw-away virtual environment. Documented and measured evidence are
kept apart: documented support is quoted from the tools' own files with a
dated URL; measured support is cited as "measured, this note, <tool>
<version>, <with|without solver>". Where they disagree, §4 records it.

This part extends Part C of the Chapter 5 note, which found in one row
that constrained `randomize()` runs on neither simulator as installed, and
uses the runner the Chapter 6 note shipped
(`examples/ch06-oop-testbench-design/support-matrix/matrix.py`), so that
every verdict is the book's own: **runs** — compiled, ran, printed `PROBE
<name> PASS` after checking every value; **wrong** — ran to `$finish` but a
checked value was not what the language requires; **no run** — compiled
but failed at run time; **no build** — did not compile, first error kept.


#### The findings that decide the chapter

1. **Constrained randomization on Verilator 5.030 is a run-time dependency
   on an external SMT solver, and the book's environment does not have
   one.** The compiled model forks `z3 --in` (overridable through
   `VERILATOR_SOLVER`) the first time a constrained `randomize()` runs; if
   the fork fails it prints a warning to stderr, returns 0, leaves every
   `rand` field untouched, and the simulation continues to `$finish` with
   exit status 0 (measured, this note, Verilator 5.030, without solver).
   The pip wheel `z3-solver` 5.1.0.0 ships an arm64 `bin/z3` that answers
   Verilator's handshake; with that directory on PATH, or its absolute
   path in `VERILATOR_SOLVER`, 20 of the 31 probes run on Verilator
   against 6 without it (measured, this note, both configurations).
2. **Even with the solver, four constructs the chapter teaches are wrong
   on 5.030 and two of them are silent:** `dist` weights are ignored (with
   a compile-time `CONSTRAINTIGN` warning), `soft` is treated as hard (no
   warning at compile time; `randomize() with` that contradicts it returns
   0), `unique` is ignored with a warning, and `randomize(a)` — the
   argument form that randomizes only the named variable — randomizes
   every `rand` field and returns 1 with no warning at all. A fifth,
   `$urandom(seed)` whose result is assigned to an unused variable, is
   optimized away and reseeds nothing, on both configurations. §2 is the
   catalog.
3. **The solver path's distribution is not uniform and the project has
   since said so.** Under the tautological constraint `a < 8` on a 3-bit
   variable, 20,000 calls produced value 0 6,139 times and value 7 never,
   under four seeds (measured, this note, Verilator 5.030 with z3 5.1.0).
   `solve s before v` changed nothing (64 of 2,000 with and without it).
   The maintainers closed a report of exactly this non-uniformity on
   2026-08-27 and shipped a new algorithm in 5.052 [Verilator #8024,
   2026-08-01](https://github.com/verilator/verilator/issues/8024);
   [Verilator Changes, master, 2026-09-12](https://github.com/verilator/verilator/blob/master/Changes).
   The chapter must not demonstrate distribution claims on 5.030.
4. **Icarus Verilog 13.0 has no `randomize()` at all.** `rand` is accepted
   as decoration, `$urandom`, `$urandom_range` and `$urandom(seed)` with a
   variable seed work, and every other row is a compile error; the
   maintainer said in 2020 "there is no support for the randomize()
   method" [iverilog #369, comment of 2020-09-10](https://github.com/steveicarus/iverilog/issues/369).
   The Icarus column is the same with and without a solver, because a
   solver is not what it lacks.

#### Tool versions and the solver used for every measurement

| Tool | Version string, as printed | Where |
|---|---|---|
| Verilator | `Verilator 5.030 2024-10-27 rev UNKNOWN.REV` | `/opt/homebrew/bin/verilator` |
| Icarus Verilog | `Icarus Verilog version 13.0 (stable) (v13_0)` | `/opt/homebrew/bin/iverilog`, `/opt/homebrew/bin/vvp` |
| z3 (pip) | `Z3 version 5.1.0 - 64 bit`, package `z3-solver 5.1.0.0`, `Mach-O 64-bit executable arm64` | `<scratchpad>/z3venv/bin/z3`, created with `python3 -m venv` (Python 3.13.5) and `pip install z3-solver` |

No `z3`, `cvc4` or `cvc5` is on PATH in the book's environment or in the
`dvbook` conda env (`which z3` → not found; measured, this note,
2026-09-12). Nothing was installed with conda or Homebrew. The runner is a
copy of `examples/ch06-oop-testbench-design/support-matrix/matrix.py` with
only the table label changed, so the flags are the book's: Verilator
`--binary --timing --timescale 1ns/1ps -Wall -Wno-DECLFILENAME
-Wno-UNUSEDSIGNAL -Wno-fatal --top-module top`; Icarus `iverilog -g2012`
then `vvp`. The "with solver" column was produced by the same runner with
the venv's `bin` directory prefixed to PATH and nothing else changed; the
same result is obtained with PATH untouched and
`VERILATOR_SOLVER="<venv>/bin/z3 --in"` exported (measured on r21).

#### 1. The support matrices

###### 1.1 How to read them

Each probe is one file under `ch07-probes/probes/` in the session
scratchpad, one construct each, a `module top` that checks the *values*
every call returned and prints `PROBE <id> PASS` only if all of them were
right — so **runs** means the values were right, not merely that the
process exited 0. **wrong** means the process ran to `$finish` and at
least one checked value was not what IEEE 1800 requires; the printed
values are in §2 and §3. **no build** keeps the first error line the
runner extracted. Row ids (r01–r31) are the probe file prefixes.

###### 1.2 Matrix, three columns: Icarus, Verilator as installed, Verilator with the pip z3

| id | Construct | Icarus 13.0 | Verilator 5.030, no solver | Verilator 5.030 with z3 5.1.0 |
|---|---|---|---|---|
| r01 | `rand` properties, unconstrained `randomize()` | no build — Error: randomize is not a method of class pkt. | runs | runs |
| r02 | `randc`: each value once per cycle | no build — Error: randomize is not a method of class pkt. | runs | runs |
| r03 | `randomize() with { inside }` | no build — syntax error | wrong | runs |
| r04 | `constraint` block with `inside` set | no build — "inside" expressions not supported yet. | wrong | runs |
| r05 | relational constraint between two variables | no build — Constraint declarations not supported. | wrong | runs |
| r06 | `dist` with `:=` weights | no build — syntax error | wrong | wrong |
| r07 | `dist` with `:/` weights | no build — syntax error | wrong | wrong |
| r08 | implication `->` | no build — Constraint declarations not supported. | wrong | runs |
| r09 | `if`/`else` constraint | no build — Constraint declarations not supported. | wrong | runs |
| r10 | `foreach` constraint on a fixed array | no build — Constraint declarations not supported. | wrong | runs |
| r11 | `solve … before` (legality) | no build — syntax error | wrong | runs |
| r12 | `soft` constraint, overridden inline | no build — syntax error | wrong | wrong |
| r13 | `unique` constraint | no build — syntax error | wrong | wrong |
| r14 | `constraint_mode(0)` and query | no build — Constraint declarations not supported. | wrong | runs |
| r15 | `rand_mode(0)` and query | no build — Can't find task rand_mode in class pkt | runs | runs |
| r16 | `pre_randomize` / `post_randomize` | no build — Error: randomize is not a method of class pkt. | runs | runs |
| r17 | `std::randomize(v)` | no build — syntax error | wrong | wrong |
| r18 | `std::randomize(v) with` | no build — syntax error | wrong | wrong |
| r19 | `$urandom`, `$urandom_range` | runs | runs | runs |
| r20 | `$urandom(seed)` replays a sequence | no run | wrong | wrong |
| r21 | run-to-run reproducibility (values printed) | no build — "inside" expressions not supported yet. | wrong | runs |
| r22 | object stability: `obj.srandom(seed)` | no build — Can't find task srandom in class pkt | runs | runs |
| r23 | thread stability: `process::self().srandom` | no build — syntax error | no build — Unsupported: Non-variable on LHS of built-in method 'sra | no build — Unsupported: Non-variable on LHS of built-in method 'sra |
| r24 | contradictory constraints return 0 | no build — Constraint declarations not supported. | runs | runs |
| r25 | `inside {array}` | no build — "inside" expressions not supported yet. | wrong | runs |
| r26 | `rand` enum with a constraint | no build — Constraint declarations not supported. | wrong | runs |
| r27 | `rand` class-handle member (nested) | no build — "inside" expressions not supported yet. | wrong | runs |
| r28 | `randomize(a)` argument form | no build — Error: randomize is not a method of class pkt. | wrong | wrong |
| r29 | signed `int` in a negative range | no build — "inside" expressions not supported yet. | wrong | runs |
| r30 | constraint on a non-rand state variable | no build — Constraint declarations not supported. | wrong | runs |
| r31 | hand-rolled `$urandom_range` in a class method | runs | runs | runs |

: Measured, this note, 2026-09-12; 31 probes, the book's runner and
flags. Without a solver: 2 run on both, 6 on Verilator only, 0 on Icarus
only, 23 on neither. With the pip z3 on PATH: 2 on both, 20 on Verilator
only, 0 on Icarus only, 9 on neither. The Icarus column is identical in
both runs.

###### 1.3 Headline

- **Runs on both, as installed:** `$urandom`, `$urandom_range` (including
  reversed arguments) and a hand-rolled `my_randomize()` that calls
  `$urandom_range` inside a class method (r19, r31). That is the whole
  intersection. Icarus additionally accepts `rand` as a decoration (x03)
  and `$urandom(seed)` with a *variable* seed (x02, replays the sequence
  and updates the seed variable to 2900899).
- **Runs on Verilator only, without a solver:** `rand`/`randc` with
  unconstrained `randomize()`, `rand_mode`, `pre_/post_randomize`,
  `obj.srandom(seed)`, and — a negative probe — contradictory constraints
  returning 0 (r01, r02, r15, r16, r22, r24). `randc` cycles correctly
  with no solver: four values seen once each per cycle, two cycles.
- **Runs on Verilator only, and only with the solver:** every constraint
  form the chapter's worked example needs — `inside` sets and array
  members, relational, implication, `if`/`else`, `foreach`, `solve …
  before` (legal results; distribution not honored, §3), state-dependent
  constraints, `constraint_mode`, signed ranges, `rand` enums, nested
  `rand` handles, `randomize() with` (r03–r05, r08–r11, r14, r25–r27,
  r29, r30), and run-to-run reproducibility (r21).
- **Wrong on Verilator even with the solver:** `dist` (both weight forms),
  `soft`, `unique`, `std::randomize` (with and without `with`),
  `$urandom(seed)` assigned to an unused variable, and `randomize(a)`
  (r06, r07, r12, r13, r17, r18, r20, r28).
- **Builds on neither:** `process::self().srandom` (r23): Icarus syntax
  error; Verilator `%Error-UNSUPPORTED: Non-variable on LHS of built-in
  method 'srandom'`.

#### 2. Catalog of silent wrong results

A silent wrong result is a cell where the tool builds, runs to `$finish`,
exits 0, prints no warning at run time, and prints a value the language
does not permit. Cells that fail *loudly* are listed at the end so the
chapter can tell the two apart. All rows measured, this note, Verilator
5.030, configuration as stated. Count: **four silent rows on 5.030**, of
which two occur with the solver installed and two on both configurations.

###### 2.1 Without a solver: every constrained `randomize()` returns 0 and leaves the fields unchanged — warned once, on stderr, then silent

**Cells.** r03–r14, r17, r18, r21, r25–r30 (all "wrong" without solver).
**Printed.** The first constrained call prints, on stderr,
`Process::open: execvp(z3): No such file or directory`, then `%Warning:
Subprocess command `z3 --in' failed: exit status 127`, then `%Warning:
Unable to communicate with SAT solver, please check its installation or
specify a different one in VERILATOR_SOLVER environment variable.` and
` ... Tried: $ z3 --in`. Every later call is silent. `randomize()`
returns 0; the fields keep their previous values (r12: `r1=0 a1=0 r2=0
a2=0`; r24 kept `a=77`; r10 printed `arr=0 0 0 0`; r21 printed
`randomize 0` three times). Exit status is 0 and `$finish` is reached.
**Why it matters.** A testbench that writes `void'(p.randomize())` — the
common idiom — gets a stream of zeros and no failure. The chapter must
show `if (!p.randomize()) $fatal(...)` as the norm, and must say that
the warning goes to stderr once per process, where a `make` log can
bury it. **Two exceptions inside this group:** `randomize() with` (x01)
returned 0 but *did* change the field (`r=0 a=190`, `a=82`, `a=202`), so
the inline form randomizes unconstrained before the solver is consulted
and the failure leaves random garbage rather than the old value; and
r28's `randomize(a)` returned 1 and randomized both fields, because it
never involves the solver (§2.3).

###### 2.2 `$urandom(seed)` assigned to an unused variable does not reseed — both configurations

**Cells.** r20 (literal seed), x02 (variable seed). **Printed.** r20:
`s1[0]=1314212542 s2[0]=299309948`, the two sequences after
`dummy = $urandom(42)` differ; x02: the seed variable is still 42
afterwards, where Icarus advanced it to 2900899. **Discriminator.** x06:
when the assigned variable is later printed, or the call is written
`void'($urandom(42))`, all three sequences after seeding are identical
(`3942645759 2599763966`). **Cause, documented.** The maintainer's
diagnosis of the same report: "It removed the seed because of the
dummy_rand being unused, calling it as a task worked" [Verilator #5703,
comment of 2025-01-11](https://github.com/verilator/verilator/issues/5703);
fixed as "Fix mis-optimizing away `$urandom` (#5703)" in 5.034,
2025-02-24 [Verilator Changes, master](https://github.com/verilator/verilator/blob/master/Changes).
**No warning** is printed at compile or run time (r20 build log carries
only `WIDTHTRUNC`). The chapter's seeding example must use the `void'()`
form or consume the result.

###### 2.3 `randomize(a)` randomizes every `rand` field and returns 1 — both configurations

**Cell.** r28. **Printed.** `a=91 b=233 sameA=0` after `p.b = 99` and
eight calls of `p.randomize(a)`; with the solver, x01 printed `arg: r=1
a=219`, `a=59`, `a=209`, `a=10` and (same object as the `with` calls
before it) the other field also moved. IEEE 1800 says the argument list
restricts randomization to the named variables; here `b` was overwritten.
**No warning** at compile or run time. No tracker entry names this form
(title searches for "randomize arguments", "partial randomization",
"randomize(var)" on 2026-09-12 returned only `std::randomize` items). The
chapter should not use the argument form on 5.030.

###### 2.4 `soft` is a hard constraint — silent at compile time, loud at run time only through the return value

**Cell.** r12. **Printed, with solver.** `r1=1 a1=5 r2=0 a2=5`: the
soft `a == 5` is honored, and `randomize() with { a == 7; }` — which the
language must satisfy by dropping the soft constraint — returns 0 and
leaves `a=5`. **No `CONSTRAINTIGN`** is printed for `soft` (the r12
build log has no warning), unlike `dist`, `unique` and `solve before`.
The original solver pull request listed "soft constraints (treated as
hard)" among its limitations [Verilator PR #4947, merged
2024-05-17](https://github.com/verilator/verilator/pull/4947); support
arrived as "Support soft constraint solving (#7124) (#7166)" in 5.048,
2026-04-26 [Verilator Changes, master](https://github.com/verilator/verilator/blob/master/Changes).
Counted as silent because a `void'()` caller sees nothing.

###### 2.5 Cells that are not silent

- **`dist`, both forms** (r06, r07): compile-time `%Warning-CONSTRAINTIGN:
  ... Constraint expression ignored (imperfect distribution)`; under the
  book's `-Wall` without `-Wno-fatal` this is a build error, so a shipped
  example cannot reach the wrong run. With the solver, values stay
  *inside* the listed set but the weights are ignored (§3.1).
- **`unique`** (r13): `%Warning-CONSTRAINTIGN: ... Constraint expression
  ignored (unsupported)`; with the solver, `randomize()` returns 1 with
  `x=2 2 2` (x04). Loud at build, silent at run.
- **`solve … before`** (r11): `Constraint expression ignored (imperfect
  distribution)`; results are legal, distribution unchanged (§3.2).
- **`std::randomize`** (r17, r18): `%Warning-CONSTRAINTIGN: std::randomize
  ignored (unsupported)`; at run time it returns **0** and leaves the
  variable unchanged (x04: `std: r=0 v=3`), on both configurations.
- **`process::self().srandom`** (r23): `%Error-UNSUPPORTED`, no binary.

#### 3. What the solver-backed runs actually do

All measured, this note, Verilator 5.030 with z3 5.1.0 on PATH, from the
counting programs `c01`–`c05` in `ch07-extra/`.

###### 3.1 `dist` produces the set, not the weights

| Constraint (2,000 calls) | Outcome counts |
|---|---|
| `a dist { 2 := 1, 7 := 9 }` | 2: 1,228; 7: 772; other: 0 |
| `a dist { [0:3] :/ 1, 9 := 9 }` | 0: 538; 1: 308; 2: 315; 3: 308; 9: 531 |
| `a dist { [0:3] := 1, 9 := 9 }` | 0: 539; 1: 308; 2: 315; 3: 307; 9: 531 |
| unconstrained 2-bit (reference) | 0: 487; 1: 482; 2: 514; 3: 517 |

The value with weight 9 came up *less* often than the value with weight
1 (772 vs 1,228); the `:/` and `:=` forms, which the language defines to
differ by a factor of four for a four-element range, produced the same
counts to within one; and the range's own members are not equiprobable
(538 vs 308). This is consistent with "basic `dist`" in 5.030 meaning
membership only [Verilator Changes, v5.030, line "Support basic `dist`
constraints (#5431)"](https://github.com/verilator/verilator/blob/v5.030/Changes),
and with the warning text "imperfect distribution". The chapter cannot
show a `dist` histogram from 5.030.

###### 3.2 `solve … before` has no effect on the distribution

`s -> v == 0` with `solve s before v` gave `s == 1` in 64 of 2,000 calls;
the same constraint without the `solve` line gave 64 of 2,000 — the same
count, because both runs consumed the same seeded stream. IEEE 1800's
worked example for this construct expects about one half with `solve
before` and 1/257 without. 5.030 delivers neither: 3.2%. Real support is
"Support solve..before constraints (#5647) (#7123)" in 5.046, 2026-02-28
[Verilator Changes, master](https://github.com/verilator/verilator/blob/master/Changes).

###### 3.3 The solver path is not uniform, and one value never appears

3-bit `a` under `a < 8` (every value legal), 20,000 calls:

| seed | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| default | 6,139 | 4,032 | 2,466 | 531 | 3,398 | 2,285 | 1,149 | **0** |
| 9 | 6,079 | 4,149 | 2,332 | 567 | 3,404 | 2,306 | 1,163 | **0** |
| 3 (4,000 calls) | 1,149 | 817 | 493 | 113 | 748 | 435 | 245 | **0** |
| 4 (4,000 calls) | 1,198 | 863 | 472 | 108 | 695 | 450 | 214 | **0** |

The unconstrained 3-bit reference in the same binary was flat (465–520
each). An 8-bit `b < 255` over 5,000 calls reached 254 or 255 of the 255
legal values depending on seed, so the hole is not a general omission of
the maximum; it is the 3-bit all-ones pattern under this constraint. The
mechanism is visible in the shipped runtime: after the first `sat`,
`VlRandomizer::next` asserts `_VL_SOLVER_HASH_LEN_TOTAL` (4) further
one-bit constraints, each equating a random bit to the XOR of a random
subset of variable bits, and takes whatever model the solver returns
[verilated_random.cpp, v5.030, `randomConstraint` and
`next`](https://github.com/verilator/verilator/blob/v5.030/include/verilated_random.cpp).
That is a diversification heuristic, not a uniform sampler. The project
accepted the general report — "constrained randomize() does not give a
uniform distribution over legal value combinations", which quotes IEEE
1800-2023 18.5.9 — and closed it on 2026-08-27 [Verilator #8024](https://github.com/verilator/verilator/issues/8024),
with "Add Unigen2 constrained randomization algorithm (#8042)" in 5.052,
2026-09-05 [Verilator Changes, master](https://github.com/verilator/verilator/blob/master/Changes).
The chapter's claim that a solver gives "a uniform distribution over
legal combinations" is the standard's requirement, not what the installed
tool does; it must be phrased that way.

###### 3.4 Reproducibility

- Two runs of the same binary with no arguments printed identical
  `$urandom` and `randomize()` sequences (`630429010 4208334026
  3831827219` / `146 58 171`, twice); `+verilator+seed+1` twice gave
  identical sequences that differ from the default; `+verilator+seed+2`
  differed again; `c03` under `+verilator+seed+5` twice: `62 38 59 38 20
  15`, both times. Constrained randomization is reproducible per seed
  with this solver. (Whether z3's own answer order is deterministic across
  solver versions is not something this note can say.)
- `+verilator+seed+0` is rejected: `%Error: COMMAND_LINE:0: Argument
  '+verilator+seed+' must be an unsigned integer, greater than 0`. The
  5.030 manual says "If zero or not specified picks a value from the
  system random number generator" [Verilator exe_sim.rst,
  v5.030](https://github.com/verilator/verilator/blob/v5.030/docs/guide/exe_sim.rst);
  measurement says zero is refused and "not specified" is deterministic.
  Recorded in §4.
- Object stability holds without a solver: two objects after
  `srandom(7)` draw identical unconstrained sequences (r22). Thread
  stability through `process::self().srandom` cannot be measured (r23
  does not build); per-process RNG arrived in 5.048 [Verilator Changes,
  master](https://github.com/verilator/verilator/blob/master/Changes).

###### 3.5 `randomize()` returning 1 with a constraint violated

Over the 31 probes and the extra programs, every value that violated a
hard constraint came with a return value of 0, **except** `unique`
(x04: `r=1 x=2 2 2`, warned at compile time) and `randomize(a)` (§2.3).
`soft` produced the inverse: a legal solution refused with 0. No probe
found a hard `inside`, relational, implication, `foreach` or `if`/`else`
constraint violated with return value 1 (r03–r05, r08–r10, r25–r30: 40
to 100 calls each, every value checked).

#### 4. Documented support, and where it disagrees with the measurement

###### 4.1 Verilator 5.030: the solver design, as documented

- **Since when.** "Support constrained randomization with external
  solvers (#4947)" is the first line of its kind, under the 5.026
  (2024-06-15) header [Verilator Changes, v5.030](https://github.com/verilator/verilator/blob/v5.030/Changes).
  5.028 (2024-08-21) added "Support state-dependent constraints (#5217)",
  "Support inline constraints for class randomization methods (#5234)",
  "Support conditional constraints (#5245)", "Support foreach constraints
  (#5302)", "Support `constraint_mode` (#5338)", "Add warning on dist in
  constraints (#5264)" and "Add parsing but otherwise ignore
  std::randomize (#5354)". 5.030 (2024-10-27) added "Support basic
  `dist` constraints (#5431)", "Support inside array constraints
  (#5448)", "Support basic constrained queue randomization (#5413)" and
  unconstrained randomization of unions, arrays, queues and associative
  arrays (same file). Earlier: "Support randomize() class method and
  rand (#2607)" (4.106, 2020-12-02), "Support pre_randomize and
  post_randomize" (5.004, 2022-12-14), "Add CONSTRAINTIGN warning when
  constraint ignored" and "Support class srandom and class random
  stability" (5.012, 2023-06-13), read by line position under the
  version headers of the local `Changes` file.
- **Which solvers, how found.** The environment-variable entry:
  "`VERILATOR_SOLVER` — If set, the command to run as a constrained
  randomization backend, such as `cvc4 --lang=smt2 --incremental`. If
  not specified, it will use the one supplied or found during configure,
  or `z3 --in` if empty" [Verilator environment.rst,
  v5.030](https://github.com/verilator/verilator/blob/v5.030/docs/guide/environment.rst).
  The install guide: "In order to use constrained randomization the Z3
  Theorem Prover must be installed, however this is not required at
  Verilator build time. There are other compatible SMT solvers, like
  CVC5/CVC4, but they are not guaranteed to work" [Verilator install.rst,
  v5.030](https://github.com/verilator/verilator/blob/v5.030/docs/guide/install.rst).
  `configure.ac` checks for `z3`, `cvc5`, `cvc4` in that order and bakes
  `z3 --in`, `cvc5 --incremental` or `cvc4 --lang=smt2 --incremental` in
  as `CFG_WITH_SOLVER` [Verilator configure.ac, v5.030, lines
  140–160](https://github.com/verilator/verilator/blob/v5.030/configure.ac).
  The shipped runtime confirms the fallback: `#define VL_SOLVER_DEFAULT
  "z3 --in"` and `m_solverProgram = VlOs::getenvStr("VERILATOR_SOLVER",
  VL_SOLVER_DEFAULT)` [verilated.cpp, v5.030, lines 88 and
  2477](https://github.com/verilator/verilator/blob/v5.030/include/verilated.cpp);
  the Homebrew binary's default is `z3 --in`, so no solver was found when
  it was configured.
- **How it talks to the solver.** `getSolver()` forks the command once
  per process, writes `(set-logic QF_ABV)` `(check-sat)` `(reset)` and
  expects the line `sat` back; on anything else it prints the warning
  quoted in §2.1. `next()` then declares each `rand` variable as a
  bit-vector, asserts each constraint, checks satisfiability, reads a
  model with `(get-value …)`, and adds the four random XOR constraints of
  §3.3 [verilated_random.cpp, v5.030](https://github.com/verilator/verilator/blob/v5.030/include/verilated_random.cpp).
  The PR that introduced it described the constraints as "expressed in
  SMT-LIB2 format" with "z3, cvc4 or cvc5 … popen()ed and their output
  parsed", and listed as unsupported: switching constraints on and off,
  soft constraints "treated as hard", and `obj.randomize() with {...}`
  [Verilator PR #4947, merged 2024-05-17](https://github.com/verilator/verilator/pull/4947)
  — two of which 5.028 later added.
- **What the language manual says.** Nothing. The v5.030 `languages.rst`
  does not mention `rand`, `constraint`, `randomize` or a solver; its
  only randomization sentence is "$random, $urandom, $urandom_range: Use
  `+verilator+seed+<value>` runtime option to set the seed" [Verilator
  languages.rst, v5.030](https://github.com/verilator/verilator/blob/v5.030/docs/guide/languages.rst).
  `CONSTRAINTIGN` "Warns that Verilator does not support certain forms of
  `constraint`, `constraint_mode`, or `rand_mode`, and the construct was
  are ignored. Ignoring this warning may make Verilator randomize()
  simulations differ from other simulators"; `RANDC` is "Historical,
  never issued since version 5.018, when `randc` became fully supported"
  [Verilator warnings.rst, v5.030](https://github.com/verilator/verilator/blob/v5.030/docs/guide/warnings.rst).
- **Later releases, for the chapter's version caveats** (all [Verilator
  Changes, master, read 2026-09-12](https://github.com/verilator/verilator/blob/master/Changes)):
  5.034 fixes the `$urandom` seed optimization (#5703); 5.040 "Support
  randomization of scope variables with 'std::randomize()' (#5438)";
  5.046 "Support solve..before constraints (#5647)", "Support `unique`
  constraints (on 1D static arrays) (#6810)", "Fix variable randomization
  to better differ by seed (#6945)"; 5.048 "Support soft constraint
  solving (#7124)", "Support dist and solve...before inside foreach
  constraints (#7245)", "Support per-process RNG for process::srandom()
  and object seeding (#7408)", "Add `+verilator+solver+file` for
  debugging constraint solver (#7242)"; 5.050 "Change `+verilator+seed`
  to default to 1, and 0 to randomly select (#7325)", "Support
  `randomize() with (identifier_list) {constraint_block}`"; 5.052 "Add
  Unigen2 constrained randomization algorithm (#8042)". The current
  manual documents `+verilator+solver+file+<filename>` and says the seed
  "defaults to 1. If specified as 0, a non-zero seed is generated at
  startup" [Verilator exe_sim.rst, master](https://github.com/verilator/verilator/blob/master/docs/guide/exe_sim.rst).

###### 4.2 Verilator: where documentation and measurement disagree

| Documented | Measured (this note) | Reading |
|---|---|---|
| "Support basic `dist` constraints" (Changes 5.030) | membership honored, weights ignored, `CONSTRAINTIGN` "imperfect distribution" at build | "basic" means set membership; the warning is the honest record |
| `CONSTRAINTIGN` covers "certain forms of `constraint`, `constraint_mode`, or `rand_mode`" (warnings.rst) | `soft` is treated as hard with **no** warning; `unique`, `solve before`, `dist`, `std::randomize` do warn | the warning list is incomplete for `soft` on 5.030 |
| PR #4947: `obj.randomize() with {...}` unsupported | runs (r03) | superseded by 5.028 "inline constraints"; the PR text is stale, not the release |
| `+verilator+seed+`: "If zero or not specified picks a value from the system random number generator" (exe_sim.rst v5.030) | 0 is rejected as an argument error; unspecified gives the same sequence on every run | doc wrong for 5.030; master doc now says default 1, and 5.050's change log confirms the default was changed |
| IEEE 1800 `randomize(a)` restricts randomization to the named variables (chapter's claim) | all `rand` fields change, returns 1, no warning | unsupported form, undocumented; 5.050's `randomize() with (identifier_list)` is a different feature |
| IEEE 1800-2023 18.5.9 uniform distribution (quoted in #8024) | value 7 never appears under `a < 8`; `solve before` no effect | acknowledged by the project in #8024; fixed after 5.030 |
| languages.rst v5.030 says nothing about classes beyond "members, methods, class extend, and class parameters" | 20 randomization probes run | the manual undersells the release, as the Chapter 5 note found for virtual interfaces |

###### 4.3 Icarus Verilog 13.0

The README claims "a (slowly growing) subset of the SystemVerilog
language" and warns that "the list of unsupported SystemVerilog
constructs is too large to enumerate here" [iverilog README,
v13-branch](https://github.com/steveicarus/iverilog/blob/v13-branch/README.md).
The tracker is the only specific statement: to "Does Icarus support
rand?" the maintainer answered "No, it doesn't. You can declare random
variables, but there is no support for the randomize() method. You will
have to implement your own randomize() method, using the standard
probabilistic distribution system functions (e.g. $random) to provide
the random values", and "without support for randomize(), that is just
decoration" [iverilog #369, comments of 2020-09-10](https://github.com/steveicarus/iverilog/issues/369).
The issue is still open. Title searches for "randomize" and "constraint"
on 2026-09-12 returned only #369 and #292.

Measurement agrees exactly (measured, this note, Icarus 13.0). The
messages, verbatim: `Error: randomize is not a method of class pkt.` /
`error: Object top.p has no method "randomize(...)".` (r01, r02, r16,
r28); `sorry: Constraint declarations not supported.` (r05, r08, r09,
r10, r14, r24, r26, r30); `sorry: "inside" expressions not supported
yet.` (r04, r21, r25, r27, r29 — reported before the constraint
message, so `inside` is refused even outside constraints); `syntax error`
/ `error: Errors in the constraint block item list.` for `dist`, `solve
before`, `soft`, `unique` (r06, r07, r11, r12, r13); `syntax error` /
`error: Malformed conditional expression.` for `randomize() with` and
`std::randomize` (r03, r17, r18); `error: Can't find task rand_mode in
class pkt` (r15) and `... srandom ...` (r22); and for a literal seed,
`ERROR: $urandom's seed must be an integer/time variable or a register.`
(r20, x06) — a *run-time* `vvp` error, hence "no run", where a variable
seed works (x02). The maintainer's 2020 advice — write your own
`randomize()` from the system functions — is r31, and it runs on both
tools; it is the one shape of "randomization" the chapter can show on
Icarus.

#### 5. What this means for the chapter's examples

- **Nothing constrained can run under `scripts/check-examples.sh` in
  the `dvbook` environment today.** For that to change, one binary is
  needed: an SMT solver that answers `(check-sat)` on stdin with `sat`,
  found either as `z3` on PATH or named in `VERILATOR_SOLVER`. This note
  established that `pip install z3-solver` (5.1.0.0) into any Python
  environment provides `bin/z3` (arm64 Mach-O, `Z3 version 5.1.0`) that
  Verilator 5.030 accepts unchanged. The least invasive change to the
  book's environment is therefore `conda run -n dvbook pip install
  z3-solver`, which places `z3` in `/opt/miniconda3/envs/dvbook/bin/`;
  `examples/mk/sv.mk` would then need either that directory on PATH when
  the Verilator binary runs or `VERILATOR_SOLVER := $(CONDA_PREFIX)/bin/z3
  --in` exported for the `run` target. This note did **not** install it
  there; that is the author's call and a `STATUS.md` decision. A Homebrew
  `z3` (`brew install z3`) would work the same way, per the install guide.
- **Constructs the chapter can ship as verified listings, with the
  solver:** `rand`/`randc`, `randomize()`, `randomize() with`, `inside`,
  relational, implication, `if`/`else`, `foreach`, state-dependent
  constraints, `constraint_mode`, `rand_mode`, `pre_/post_randomize`,
  nested `rand` objects, `rand` enums, `obj.srandom`, run-to-run
  reproducibility under `+verilator+seed+N`, and the contradiction probe.
- **Constructs the chapter must teach from the standard and label
  "not runnable on 5.030":** `dist` weights (build error under `-Wall`;
  show the histogram as what the standard requires, not as output),
  `solve … before` distribution, `soft`, `unique`, `std::randomize`,
  `randomize(a)`, `process::self().srandom`. Each has a release in §4.1
  where it landed; the chapter should say "Verilator 5.046/5.048/5.052
  and later" by construct rather than "newer Verilator".
- **Two idioms the chapter must make habitual, because 5.030 punishes
  their absence silently:** check the return value of every
  `randomize()` (§2.1), and write seeding as `void'($urandom(seed))` or
  consume the result (§2.2).
- **The support-matrix example.** The 31 probes and `probes.txt` are in
  the runner's format and were run by an unmodified copy of `matrix.py`;
  they can become `examples/ch07-constrained-random/support-matrix/` as
  Chapter 6's did. The runner would need one extension to print the
  third column: run each Verilator binary twice, once with the solver
  directory removed from PATH. That is a ten-line change to `matrix.py`
  and was not made here, because the book's copy is outside this note's
  write scope.
- **Icarus:** the chapter can show only §4.3's hand-rolled method on it.
  Every constrained example is Verilator-only, and the chapter must say
  so with the reason (no `randomize()` at all), as Chapter 6 does for
  virtual dispatch.

#### Unsourced-claims table

| Claim | Status |
|---|---|
| `randomize(a)` must randomize only the named variables (§2.3) | This note's reading of IEEE 1800 §18.11 (argument form); the clause text was not consulted in this session. `refs.bib` has `ieee1800-2023`. Verify before the chapter asserts it. |
| `solve before` should give `s == 1` about half the time and its absence about 1/257 (§3.2) | Quoted from the report in Verilator #8024, which cites IEEE 1800-2023 18.5.9 and Table 18-1; not read from the standard here. |
| `:/` and `:=` differ by a factor of four for a four-element range (§3.1) | This note's arithmetic from the definitions of the two operators; standard text not consulted. |
| The value-7 hole is caused by the XOR-hash diversification (§3.3) | Inferred from the shipped source and the counts; no maintainer statement ties the hole to that code. The non-uniformity itself is acknowledged in #8024. |
| The Homebrew Verilator was configured without a solver | Inferred from the runtime message `Tried: $ z3 --in` matching `VL_SOLVER_DEFAULT`; the Homebrew build log was not read. |
| `pip install z3-solver` into `dvbook` would behave as it did in the scratchpad venv | Same wheel, same machine, same architecture; not executed in `dvbook`. |
| Release attribution of each `Changes` line | Read by line position under version headers, local file for ≤5.030 and the master file for later; medium confidence, as in the Chapter 6 note. |
| Two Icarus tracker searches are exhaustive | Title search, unauthenticated API, 2026-09-12; body-text matches not read. |

#### Key sources

Existing `refs.bib` keys reused: `verilator-docs`, `verilator-languages`,
`verilator-warnings`, `verilator-changes`, `icarus-release-13`,
`icarus-issue-292`, `ieee1800-2023`. Where the chapter quotes a 5.030
limitation it should cite the v5.030-tagged files, as the Chapter 5 and
6 notes proposed. New entries:

```bibtex
@misc{verilator-environment,
  author       = {Wilson Snyder and {Verilator contributors}},
  title        = {Verilator User's Guide: Environment},
  howpublished = {GitHub, verilator/verilator, docs/guide/environment.rst
                  at tag v5.030},
  year         = {2024},
  url          = {https://github.com/verilator/verilator/blob/v5.030/docs/guide/environment.rst},
  note         = {Documents \texttt{VERILATOR\_SOLVER} and the
                  \texttt{z3 --in} default. Accessed 2026-09-12}
}

@misc{verilator-install,
  author       = {Wilson Snyder and {Verilator contributors}},
  title        = {Verilator User's Guide: Installation},
  howpublished = {GitHub, verilator/verilator, docs/guide/install.rst
                  at tag v5.030},
  year         = {2024},
  url          = {https://github.com/verilator/verilator/blob/v5.030/docs/guide/install.rst},
  note         = {``Install Z3'' section: Z3 required for constrained
                  randomization, not at build time; CVC4/CVC5 ``not
                  guaranteed to work''. Accessed 2026-09-12}
}

@misc{verilator-exe-sim,
  author       = {Wilson Snyder and {Verilator contributors}},
  title        = {Verilator User's Guide: Simulation Runtime Arguments},
  howpublished = {GitHub, verilator/verilator, docs/guide/exe\_sim.rst
                  at tag v5.030},
  year         = {2024},
  url          = {https://github.com/verilator/verilator/blob/v5.030/docs/guide/exe_sim.rst},
  note         = {\texttt{+verilator+seed+<value>} and
                  \texttt{+verilator+rand+reset+<value>}. Accessed 2026-09-12}
}

@misc{verilator-random-runtime,
  author       = {{Verilator contributors}},
  title        = {verilated\_random.cpp: constrained randomization runtime},
  howpublished = {GitHub, verilator/verilator, include/verilated\_random.cpp
                  at tag v5.030},
  year         = {2024},
  url          = {https://github.com/verilator/verilator/blob/v5.030/include/verilated_random.cpp},
  note         = {Solver handshake, SMT-LIB emission, and the random XOR
                  constraints used to diversify solutions. Accessed 2026-09-12}
}

@misc{verilator-pr-4947,
  author       = {Arkadiusz Kozdra},
  title        = {Constrained randomization with popen and external solvers},
  howpublished = {GitHub, verilator/verilator, pull request 4947},
  year         = {2024},
  url          = {https://github.com/verilator/verilator/pull/4947},
  note         = {Merged 2024-05-17; released in 5.026. Lists soft
                  constraints ``treated as hard''. Accessed 2026-09-12}
}

@misc{verilator-issue-5703,
  author       = {{Verilator contributors}},
  title        = {\$urandom seeding},
  howpublished = {GitHub, verilator/verilator, issue 5703},
  year         = {2024},
  url          = {https://github.com/verilator/verilator/issues/5703},
  note         = {Opened 2024-12-23, closed 2025-01-11: a
                  \texttt{\$urandom(seed)} call whose result is unused is
                  optimized away; fixed in 5.034. Accessed 2026-09-12}
}

@misc{verilator-issue-8024,
  author       = {{Verilator contributors}},
  title        = {constrained randomize() does not give a uniform
                  distribution over legal value combinations},
  howpublished = {GitHub, verilator/verilator, issue 8024},
  year         = {2026},
  url          = {https://github.com/verilator/verilator/issues/8024},
  note         = {Opened 2026-08-01, closed 2026-08-27; quotes IEEE
                  1800-2023 18.5.9. Accessed 2026-09-12}
}

@misc{icarus-issue-369,
  author       = {{Icarus Verilog contributors}},
  title        = {Does Icarus support rand?},
  howpublished = {GitHub, steveicarus/iverilog, issue 369},
  year         = {2020},
  url          = {https://github.com/steveicarus/iverilog/issues/369},
  note         = {Open. Maintainer's comment of 2020-09-10: ``there is no
                  support for the randomize() method''. Accessed 2026-09-12}
}

@misc{icarus-readme,
  author       = {{Icarus Verilog contributors}},
  title        = {Icarus Verilog README},
  howpublished = {GitHub, steveicarus/iverilog, v13-branch},
  year         = {2026},
  url          = {https://github.com/steveicarus/iverilog/blob/v13-branch/README.md},
  note         = {``a (slowly growing) subset of the SystemVerilog
                  language''. Accessed 2026-09-12}
}

@misc{z3-solver-pypi,
  author       = {{Microsoft Research}},
  title        = {z3-solver: an efficient SMT solver library},
  howpublished = {PyPI},
  year         = {2026},
  url          = {https://pypi.org/project/z3-solver/},
  note         = {Version 5.1.0.0 installed 2026-09-12; the wheel ships a
                  \texttt{bin/z3} executable. Accessed 2026-09-12}
}
```

#### Confidence notes

- **High:** every matrix cell, every printed count and message. Each is
  a file in the scratchpad (`ch07-probes/`, `ch07-probes-z3/`,
  `ch07-extra/`), a fixed command, and an output captured on 2026-09-12
  by the book's own runner; the two matrix runs take about four minutes
  each, the counting programs under a minute.
- **High:** that the pip wheel's `z3` is usable by Verilator 5.030 with
  no configuration beyond PATH or `VERILATOR_SOLVER`, and that nothing
  outside the scratchpad was installed or changed.
- **High:** the quotations from the v5.030-tagged `environment.rst`,
  `install.rst`, `exe_sim.rst`, `warnings.rst`, `languages.rst`,
  `configure.ac`, the local `Changes` and the shipped runtime sources;
  from Verilator #5703, #8024 and PR #4947; and from iverilog #369, all
  read on 2026-09-12.
- **Medium:** the release attribution of `Changes` lines after 5.030,
  read from the master file by line position.
- **Medium:** the count of silent rows (four). It depends on the
  definition in §2 — no run-time warning — and on treating `soft`'s
  return of 0 as silent for a `void'()` caller; a stricter definition
  gives two (`$urandom(seed)` and `randomize(a)`).
- **Low:** any statement about *why* the solver path leaves value 7
  unreached; only that it does, under four seeds.
- **Not measured:** any Verilator later than 5.030 (which would change
  eight cells according to its change log), cvc4/cvc5 as the backend, an
  Icarus build from master, and `dvbook`'s own Python after a
  `z3-solver` install. The chapter should name versions, not tools.
- **What must be installed for the chapter's examples to run under
  `scripts/check-examples.sh`:** exactly one thing — a `z3` binary
  reachable from the Verilator-generated executable, e.g. `conda run -n
  dvbook pip install z3-solver` plus either `/opt/miniconda3/envs/dvbook/bin`
  on PATH in the `run` recipe or `VERILATOR_SOLVER="/opt/miniconda3/envs/dvbook/bin/z3 --in"`
  exported by `examples/mk/sv.mk`. No change to Verilator, Icarus, cocotb
  or the flags is needed. Without it, every constrained example prints
  zeros and passes a status-only check.
