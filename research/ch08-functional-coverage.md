---
title: "Research note: Chapter 8 — Functional Coverage"
date: 2026-09-26
author: research-agent
status: complete
feeds: Ch. 8
---

# Chapter 8 — Functional Coverage: evidence note

Scope: the coverage language — covergroups, sampling forms, bins of every
kind, crosses, options, the API and how the percentage is computed — and the
method behind it: what code, functional and assertion coverage each measure
and miss, why coverage is not correctness, and how closure is done as a
reviewed process with exclusions, merging and formal unreachability. Then a
*measured* account of what the book's two open simulators do with each
construct, what Verilator's own coverage machinery prints end to end, and
whether the two free alternatives for the constructs they refuse
(`cocotb-coverage`, FC4SC) work on the book's toolchain.

Gathered in three independent passes and kept in three parts. **Section
numbers are local to their part.** Each part carries its own unsourced-claims
table, BibTeX suggestions and confidence notes.

## Which part feeds which chapter section

| Chapter topic | Part | Sections |
|---|---|---|
| Covergroup declaration, embedding, arguments; the four sampling forms | A | §2, §3 |
| Coverpoints and every bin kind; `auto_bin_max` | A | §4 |
| Crosses, `binsof`, the Cartesian-product trap | A | §5 |
| Options, per-type versus per-instance, the API and the percentage rule | A | §6, §7 |
| What goes wrong: the 15-row catalog | A | §8 |
| Code versus functional versus assertion coverage; the two-gate example | B | §1 |
| The coverage-driven argument and the evidence for it | B | §2 |
| Coverage is not correctness: activate, propagate, detect | B | §3 |
| Closure: merging, exclusions, unreachability, UCIS | B | §4 |
| How OpenTitan closes coverage end to end | B | §5 |
| Coverage in UVM, cocotb-coverage, FC4SC | B | §6; C | §5 |
| **What runs where** (decides every example) | C | matrices |
| Silent wrong results and documentation-versus-measurement | C | §2, §4 |
| Verilator's own line/toggle/branch/expression coverage, end to end | C | §3 |

## Findings that decide the chapter, across the parts

1. **A covergroup that is never constructed, never sampled, or sampled from
   the wrong place reports nothing and warns about nothing** (Part A §1).
   The chapter's first Pitfall is silence, not syntax; its rule is to
   sample from the observer, with `sample()` arguments, never from the
   driver. Measured on OpenTitan: 322 of 417 class covergroups declare a
   sample function and none uses a clocking event.
2. **Verilator 5.052 runs covergroups; Icarus 13.0 refuses the keyword**
   (Part C). Support landed in 5.050. Of 35 constructs probed, 17 run with
   the right percentage on Verilator, 9 run and print a wrong one, 9 do
   not build; all 35 are a syntax error on Icarus. The coverage flag does
   not change a covergroup verdict; it only controls the `.dat` dump.
   Every SystemVerilog listing in the chapter is therefore Verilator-only,
   and the chapter's matrix is measured with the flags the book's build
   uses.
3. **Eight silent wrong results, one of them structural** (Part C §2): a
   covergroup's `get_inst_coverage()` is the ratio of bins hit to bins
   defined across its items, not the standard's average of per-item
   percentages, so any group whose items have unequal bin counts reports
   a wrong number without a warning. Ignored values stay in the
   denominator, `get_coverage()` returns 0.0, `stop()` is dropped, enum
   auto bins are per bit pattern, and `'1` as a bin value matches 1. Five
   more are wrong but warned (`COVERIGN`), which the book's `-Wall` turns
   into a build error. These decide which constructs the chapter shows
   running and which it shows as Pitfalls with spliced output.
4. **Coverage counts what was sampled, never what was checked** (Parts A
   §1, B §3). The activate-propagate-detect model, lowRISC's rule that
   `illegal_bins` is not a checker, and the 100%-next-to-an-empty-
   scoreboard case are the chapter's central Pitfall. No controlled study
   of coverage-driven against directed verification exists; the chapter
   attaches no percentage to the method's benefit.
5. **Closure is a reviewed process, not a number** (Part B §3–§5).
   OpenTitan's flow: designer sign-off on exclusions, five exclusion
   categories, checksums that expire an exclusion when the code changes,
   formal unreachability only after design freeze, and a failed test's
   coverage deleted before merge. UCIS 1.0 standardizes the database and
   API and says in its own words that the merge is not fully specified.
6. **Auto bins and crosses are traps by arithmetic** (Part A §1): 64
   auto bins by default over any width; a cross is the full Cartesian
   product with no `default`; and a bin range written with `^` for a power
   is XOR, which OpenTitan's HMAC coverage does today — 8 bins where 64
   were meant, a cross that closes early, no warning from any tool. *A
   public claim about a named project: the author decides whether the
   book prints it or it is reported upstream first.* `cross_auto_bin_max`
   is not in any IEEE edition and must not be taught.
7. **The free alternatives** (Part C §5): `cocotb-coverage` 2.0 installs
   with `pip` beside `dvbook`'s cocotb 2.1.0 and runs on both simulators
   with XML/YAML export — an environment change for the author, as `z3`
   was. FC4SC needs a one-line patch for Apple's libc++, was last
   committed in 2021, and is not recommended for the chapter.
8. **Verilator's own code coverage is complete end to end** (Part C §3)
   and gives the chapter a runnable code-coverage example beside the
   functional one, with two measured surprises: the annotation threshold
   defaults to 10 hits, and a class-based testbench's line summary is
   dragged down by Verilator's own standard-library records.
9. **IEEE 1800-2023 clause 19 text was not read**; the 2017 and 2012
   texts were, and diffed. Top-level 19.3–19.11 numbers are confirmed for
   2023 by slang; third-level numbers are 2017 numbers and are not to be
   printed as 2023. The weighted-average percentage rule that finding 3
   rests on is read from the 2017 text.


---

# Part A — Functional coverage as SystemVerilog defines it

Scope: `covergroup` declaration, instantiation and embedding; sampling in
its four forms; `coverpoint` expressions and every bin kind; `cross`,
`binsof`/`intersect` and cross bins; the option tables and where each option
may be set; the coverage methods and system functions; how the percentage is
computed; and the catalog of what goes wrong. Coverage-model *design* from a
plan is Chapter 2's note (`research/ch02-verification-planning.md` §3) and
Chapter 1 taught the coverage-model gap; neither is redone. The method
(why coverage, closure, merging across runs) is Part B and what the book's
tools run is Part C of this chapter's evidence.

Written section by section; the most important part is first.

**On editions and clause numbers.** IEEE 1800-2023 is paywalled and its
text was not read. The clause 19 text of **IEEE 1800-2012** and **IEEE
1800-2017** *was* read, from public copies
([IEEE 1800-2012, hosted by UAH, accessed 2026-09-26](https://ece.uah.edu/~gaede/cpe526/2012%20System%20Verilog%20Language%20Reference%20Manual.pdf),
[IEEE 1800-2017, hosted by MIT 6.205, accessed 2026-09-26](https://fpga.mit.edu/6205/_static/F23/documentation/1800-2017.pdf)),
and a whitespace-insensitive diff of the two editions' clause 19 shows only
editorial changes plus three added table rows (`get_inst_coverage` in Table
19-2, `merge_instances` and `distribute_first` in Table 19-4) and one added
example in 19.11.3. Clause numbers below are therefore **2017 numbers, read
in the 2017 text**. slang's language-support table, which states it tracks
1800-2023, lists 19.3 Defining the coverage model, 19.4 Using covergroup in
classes, 19.5 Defining coverage points, 19.6 Defining cross coverage, 19.7
Specifying coverage options, 19.8 Predefined coverage methods, 19.9
Predefined coverage system tasks, 19.10 Organization of option members and
19.11 Coverage computation, so the top-level numbers carry over to 2023
[slang, "Language Support", accessed 2026-09-26](https://sv-lang.com/language-support.html).
What 2023 *added* to clause 19 is known only from slang's changelog for
v7.0: covergroups may inherit from covergroups in parent classes,
coverpoints may have `real` type, and two new options `cross_retain_auto_bins`
and `real_interval`
[slang CHANGELOG, v7.0, 2024-09-26](https://github.com/MikePopoloski/slang/blob/master/CHANGELOG.md).
The chapter should cite the 2023 edition and print a clause number only
from the list above.

### 1. Findings that decide the chapter

1. **A covergroup that is never constructed collects nothing and says
   nothing.** An embedded covergroup "may only be assigned in the new
   method", and "if it is not, then the coverage group is not created and no
   data will be sampled" (19.4). Sutherland, Mills and Spear make it the
   first coverage gotcha: no errors or warnings, "the only indication that
   there is a problem is an erroneous or incomplete coverage report", and
   the second cause of a 0% group is a sampling event that never fired or a
   `sample()` never called
   [Sutherland, Mills & Spear, SNUG SJ, 2007-02-13](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf)
   (§6.1). OpenTitan's coverage classes construct every covergroup in
   `new()` and the RTL-bound ones through a macro that prints "Creating
   covergroup" when it does
   [OpenTitan `hw/dv/sv/dv_utils/dv_fcov_macros.svh`, commit 69d8208, accessed 2026-09-26](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_utils/dv_fcov_macros.svh).
   The chapter's first Pitfall is silence, not syntax.
2. **The sampling form is the design decision, and real code samples
   explicitly.** The standard offers a clocking event, `with function
   sample(...)`, block events `@@(begin|end ...)`, or nothing, in which case
   "users must procedurally trigger the coverage sampling via the built-in
   sample() method" (19.3). Bromley and Litterick call the clocked form "too
   inflexible for serious usage" and favour "explicit code elsewhere in the
   class that calls the covergroup's sample method", especially when the
   data comes from several sources over time
   [Bromley & Litterick, SNUG 2016](https://assets.website-files.com/63f4bb21bd5303fe472ad00e/64957f836fbf7349210cf29c_bromley_coverage_paper.pdf)
   (§8.2). Measured on OpenTitan: of 417 covergroups in the 76 `*_cov.sv`
   class files, 322 declare `with function sample(...)`, none uses a
   clocking event; of 104 covergroups in the 57 RTL-bound `*_cov_if.sv`,
   `*_cov_bind.sv` and `*fcov*` files, 49 use a clocking event
   [OpenTitan, commit 69d8208, measured 2026-09-26](https://github.com/lowRISC/opentitan/tree/master/hw).
   The chapter teaches `sample()` with arguments as the default and the
   clocked form as the interface-embedded special case.
3. **Auto bins are a trap on anything wider than six bits.** With no
   explicit bins the tool creates N = min(2^M, `auto_bin_max`) bins, default
   64, and distributes the 2^M values across them (19.5.3, Table 19-1); the
   coverpoint's percentage is then covered bins over that N (19.11.1). So
   a 32-bit address coverpoint reports 100% after 64 values spread across
   64 ranges of 2^26 each, and an 8-bit field silently gets 64 four-value
   bins. The UVM user guide's own example sets `auto_bin_max = 16` on an
   address and 8 on data
   [Accellera UVM 1.2 User's Guide, 2015-10-08](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf)
   (§3.12.1); OpenTitan's coverage classes set `auto_bin_max` three times in
   76 files and otherwise name every bin.
4. **A cross is a Cartesian product and nothing else.** The standard's own
   example crosses a 4-bit variable with a 10-bin coverpoint and gets 160
   bins (19.6); Ellis and Jain warn of "thousands or even millions of
   cross-bins" and recommend an explicit cross-bin list [vendor: Mentor]
   [Ellis & Jain, DVCon US 2018](https://dvcon-proceedings.org/wp-content/uploads/unraveling-the-complexities-of-functional-coverage-an-advanced-guide-to-simplify-your-use-model.pdf)
   (§IV); Verilator master refuses a cross "whose normal-bin Cartesian
   product exceeds 2**32 - 1 tuples"
   [Verilator `docs/guide/warnings.rst`, master, accessed 2026-09-26](https://github.com/verilator/verilator/blob/master/docs/guide/warnings.rst).
   There is no `default` bin for a cross, so auto bins survive for every
   tuple not named, and Bromley calls it "essential" that a cross name bins
   for every combination (§9.2).
5. **`illegal_bins` is a run-time error, not a check.** An illegal value
   or transition "is issued" as a run-time error and takes precedence over
   every other bin (19.5.6, 19.6.3). Smith and Aynsley ask what happens
   "when coverage is turned off" and answer: use `ignore_bins` and "write an
   assertion" [Smith & Aynsley, DVCon 2011](https://dvcon-proceedings.org/wp-content/uploads/a-practical-look-systemverilog-coverage-tips-tricks-and-gotchas.pdf)
   (§4.1). lowRISC's DV style guide: "Do not use `illegal_bins` as a
   checker", the check "must be outside the coverage enable sampling
   blocks", and "some simulators may still show a test to pass even when one
   of the `illegal_bins` condition is hit"
   [lowRISC DV style guide, accessed 2026-09-26](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).
6. **Per-type and per-instance coverage are different numbers, and the
   default hides the instances.** `option.per_instance` defaults to 0, in
   which case "implementations are not required to save instance-specific
   information" (Table 19-1); `get_coverage()` is static and cumulative
   over all instances, `get_inst_coverage()` is per instance (19.8); type
   coverage is a weighted average of instances unless
   `type_option.merge_instances` makes it a union (19.11.3). Two instances
   that each hit a different half of one two-bin coverpoint report 50%
   apiece and 50% for the type by default, 100% for the type when merged
   [Ellis & Jain, 2018](https://dvcon-proceedings.org/wp-content/uploads/unraveling-the-complexities-of-functional-coverage-an-advanced-guide-to-simplify-your-use-model.pdf)
   (§II). Sutherland's 2007 gotcha §6.2 is the same fact seen from the
   report. OpenTitan sets `option.per_instance = 1` in 39 of its 76
   coverage class files and `option.name` in 37.
7. **Coverage counts what was sampled, never what was checked.** The
   standard says coverage "is a user-defined metric" that measures whether
   conditions "have been observed, validated, and tested" (19.2) and
   provides no link to a checker. Sprott, Marriott and Graham: "When
   planning functional coverage, the corresponding checks must also be
   planned", "many false positive coverage problems occur due to greedy or
   sloppy sampling", and covering register values alone "can often lead to
   a very false sense of security"
   [Sprott, Marriott & Graham, DVCon US 2015](https://dvcon-proceedings.org/wp-content/uploads/navigating-the-functional-coverage-black-hole-be-more-effective-at-functional-coverage-modeling.pdf).
   The UVM user guide puts class coverage in `uvm_monitor` subclasses
   (§3.12.1) and OpenTitan samples "in 'reactive' components of the
   testbench, such as monitors and/or the scoreboards"
   [OpenTitan DV methodology, commit 69d8208](https://github.com/lowRISC/opentitan/blob/master/doc/contributing/dv/methodology/README.md).
   The chapter's rule: sample from the observer, never from the driver.
8. **`cross_auto_bin_max` is not in any IEEE edition.** Table 19-1 of the
   2005, 2012 and 2017 texts lists `auto_bin_max` and
   `cross_num_print_missing`; none lists `cross_auto_bin_max`. slang adds it
   only under `--allow-cross-auto-bin-max` "for compatibility with
   (pre-IEEE) SystemVerilog 3.1a"
   [slang CHANGELOG, Unreleased, accessed 2026-09-26](https://github.com/MikePopoloski/slang/blob/master/CHANGELOG.md).
   The chapter must not teach it as a language option.
9. **Verilator now runs covergroups.** Verilator 5.050 (2026-07-01)
   added "Support covergroups, coverpoints, and bins" and the 5.052 manual
   says it "partially supports SystemVerilog functional coverage with
   `covergroup`, `coverpoint`, bins, cross coverage, and transition bins"
   [Verilator `Changes`, accessed 2026-09-26](https://github.com/verilator/verilator/blob/master/Changes),
   [Verilator `docs/guide/languages.rst`, v5.052](https://github.com/verilator/verilator/blob/v5.052/docs/guide/languages.rst).
   Part C measures what that means; this part only notes that the
   installed baseline is 5.052 and that every construct below needs a row
   there.
10. **A bin range is an expression, and `^` is XOR.** `hmac_env_cov`
   declares `bins fifo_depth[] = {[0:2^(HmacStaMsgFifoDepthMsb+1-HmacStaMsgFifoDepthLsb)-1]}`
   with Msb = 9 and Lsb = 4, intending 2**6 - 1 = 63. Binary `-` binds
   tighter than `^` (IEEE 1800-2017 Table 11-2), so the bound is
   `2 ^ 5` = 7: eight bins instead of sixty-four, the coverpoint and its
   five-way cross reach 100% on depths 0 to 7, and no tool warns because
   every operand is legal
   [OpenTitan `hw/ip/hmac/dv/env/hmac_env_cov.sv` and `hmac_env_pkg.sv`, commit 69d8208, read 2026-09-26](https://github.com/lowRISC/opentitan/blob/master/hw/ip/hmac/dv/env/hmac_env_cov.sv).
   This is the chapter's cleanest evidence that a coverage model is code
   that needs its own review (Sprott 2015 says so in words; this is the
   instance), and a candidate for the worked example's "test the coverage
   model" step. Printing it names a project's bug: the author decides
   whether the book cites it or the finding is reported upstream first.

### 2. The covergroup: declaration, instantiation, embedding, arguments

A `covergroup` "is a user-defined type": defined once, instantiated any
number of times with `new`, and legal "in a package, module, program,
interface, checker, or class" (19.3). Its parts are an optional clocking
event, coverpoints, crosses, optional formal arguments and options. The
UVM user guide's construct table adds that a covergroup may sit in a
generate block but not in an `initial` or `always` block
[Accellera UVM 1.2 User's Guide, 2015-10-08](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf)
(Table 5). Inside an interface it is the idiom for white-box coverage of
RTL internals: Bromley notes that SVA and covergroups "encapsulated in an
interface or checker can be injected into any place in the
statically-instantiated Verilog hierarchy using the bind construct"
[Bromley & Litterick, SNUG 2016](https://assets.website-files.com/63f4bb21bd5303fe472ad00e/64957f836fbf7349210cf29c_bromley_coverage_paper.pdf)
(§4), and OpenTitan's `*_cov_if.sv` files are exactly that, bound by a
`*_cov_bind.sv` and instantiated through `DV_FCOV_INSTANTIATE_CG`, whose
`en_<name>` bit lets the test decide at time zero whether the instance is
created at all
[OpenTitan `dv_fcov_macros.svh`, commit 69d8208](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_utils/dv_fcov_macros.svh).

**Embedding in a class.** A covergroup declared inside a class "declares
an anonymous covergroup type and an instance variable of the anonymous
type"; the identifier names the variable, which "may only be assigned in
the new method" (19.4). It may cover `protected` and `local` members
without breaking encapsulation, and an object it depends on must be
constructed first (the standard's `Helper` example constructs `m_obj`
before `Cov`). Bromley §10.1 draws the UVM consequence: a component's
covergroup must be built in `new()`, before `build_phase` has fetched any
configuration, so configurable coverage goes into objects built later or
into factory-overridden parameterized classes (§10.2). OpenTitan's answer
is the wrapper class: `tl_errors_cg_wrap` holds one covergroup, takes the
name through `new(string name)`, and is created from the scoreboard when
the configuration is known
[OpenTitan `hw/dv/sv/cip_lib/cip_base_env_cov.sv`, commit 69d8208](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/cip_lib/cip_base_env_cov.sv);
`hmac_env_cov` builds one `nist_cov_wrap` per vector list the same way
[OpenTitan `hw/ip/hmac/dv/env/hmac_env_cov.sv`, commit 69d8208](https://github.com/lowRISC/opentitan/blob/master/hw/ip/hmac/dv/env/hmac_env_cov.sv).

**Arguments.** A covergroup takes a task-style argument list; every
non-defaulted actual must be supplied to `new`, and actuals "are evaluated
when the new operator is executed". A `ref` argument "allows a different
variable to be sampled by each instance"; an `input` argument "will not
track the value" but keeps what was passed. `output` and `inout` are
illegal, a `ref` is treated as `const ref`, and formals are invisible from
outside the covergroup (19.3). The 2007 gotcha §6.3: direction is sticky,
so `(ref int ra, int low, int high)` makes `low` and `high` `ref` too and
`new(va, 0, 50)` fails to compile; write the direction on every argument
[Sutherland, Mills & Spear, 2007](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf).
Arguments are how bins are parameterized: `cip_base_env_cov` declares
`covergroup intr_cg (uint num_interrupts)` and uses it in
`bins all_values[] = {[0:num_interrupts-1]}`. Only constants, class
instance constants and non-`ref` arguments may appear in a bin
expression, and functions used there must be automatic, side-effect free
and constant-argument (19.5).

### 3. Sampling: four forms, `iff`, `strobe`

1. **Clocking event** `@(posedge clk)` or `@(some_event)`: sampled "the
   instant the clocking event takes place, as if the process triggering
   the event were to call the built-in sample() method", and if the event
   occurs several times in a time step the group is sampled several
   times (19.3). Sampling a clocking-block signal takes the value the
   clocking block made available: `#1step` skew reads the Preponed
   region, `#0` the Observed region (19.5).
2. **`with function sample(args)`**: overrides the built-in method so the
   data is passed in rather than read from the enclosing scope; each
   formal "may only designate a coverpoint or conditional guard
   expression", and a name may not appear in both the covergroup and the
   sample argument lists (19.8.1). The standard's example calls
   `cg1.sample(a, x)` from a property's match action and from an
   automatic function. This is OpenTitan's dominant form (finding 2) and
   Bromley's recommended one; his `reg_toggle_cg` samples once per bit of
   a word so the cross `bit_num × bit_val` accumulates toggle coverage
   (§8.2).
3. **Block events** `@@(begin task_name)` / `@@(end ...)`: sampled
   immediately before a named block, task, function or method starts, or
   after its last statement; `end` does not fire if the block is disabled
   (19.3). No use was found in OpenTitan or the UVM guide.
4. **No event**: the user calls `sample()`; the UVM guide's monitor
   assigns the coverpoint variables in a function and then calls
   `cov_trans_beat.sample()` once per data beat (§3.12.1).

`iff (expr)` on a coverpoint, a cross or a single bin is a guard: if false
at the sample the item is ignored or the bin not incremented (19.5, 19.6).
OpenTitan uses `iff` in 7 of 76 class files, for instance
`coverpoint op iff (wip == 1)` and `cross cmd_cp, state iff (access_type ==
AccessSoftwareWrite)`
[OpenTitan `hw/ip/otbn/dv/uvm/env/otbn_env_cov.sv`, commit 69d8208](https://github.com/lowRISC/opentitan/blob/master/hw/ip/otbn/dv/uvm/env/otbn_env_cov.sv).
`type_option.strobe = 1` moves clocked samples to the Postponed region so
that "only one sample per time slot is taken"; it is a type option, may
only be set in the definition, and "shall have no effect on procedural
calls to the built-in sample() method" (19.3, 19.7.1). Smith and Aynsley
use it to sample an associative array that several cover properties set
in different deltas of the same cycle (§3.4.1).

### 4. Coverpoints and bins

A coverpoint covers an integral expression (a variable, a part-select, a
concatenation, a function result); its type is either declared, as in
`bit [7:0] d: coverpoint y[31:24]`, or the self-determined type of the
expression, and the value is what assignment to that type would give
(19.5). Enums, packed structs and vectors are all integral: OpenTitan
covers a concatenation `{rx_sync, rx_sync_q1, rx_sync_q2}`, a register
slice `cfg[DigestSizeMsb:DigestSizeLsb]`, and enum values by name
[OpenTitan `hw/ip/uart/dv/env/uart_env_cov.sv`, commit 69d8208](https://github.com/lowRISC/opentitan/blob/master/hw/ip/uart/dv/env/uart_env_cov.sv).
Bromley's idiom is a classifier function that returns an enum, so the
bins are named by the enumeration and the arithmetic lives in one place
(§8.1). The expression is evaluated "in a procedural context" at the
sample and may reach through a virtual interface (19.5).

**Bin kinds, as the standard defines them.**

| Form | Meaning (19.5.x) | Seen in OpenTitan |
|---|---|---|
| none | auto bins: N = min(2^M, `auto_bin_max`), enums one per value; x/z samples excluded; names `auto[v]` / `auto[lo:hi]` (19.5.3) | the default for 1-bit and enum coverpoints |
| `bins b = {list}` | one bin for the whole range list; `$` is the type's min or max | `bins large_timeout = {[50:$]}` |
| `bins b[] = {list}` | one bin per value; overlaps allowed and retained (19.5.1) | `bins all_values[] = {[0:num_interrupts-1]}` |
| `bins b[N] = {list}` | values split into N bins in order, remainder to the last; `{[1:10],1,4,7}` into 4 gives `<1,2,3>,<4,5,6>,<7,8,9>,<10,1,4,7>` | `bins others[Width] = ...` |
| `bins b = (a => b), (c [*3]), (d [-> 2]), (e [= 2])` | transition bins: consecutive `=>`, consecutive repeat `[*]`, goto `[->]` (next transition must follow the last occurrence), non-consecutive `[=]`; a bin increments on every complete match, at most once per sample; unbounded sequences may not use `[]` (19.5.2) | `bins Any2Any[] = ([Standard:Quad] => [Standard:Quad])`, four-step reset sequences in `resets_cg` |
| `wildcard bins b = {4'b11??}` | x, z, ? match 0 or 1; values with x/z in the sample are excluded (19.5.4) | none (0 of 76 files) |
| `bins b = default` / `default sequence` | catches values or transitions in no other bin; **excluded from the percentage and from every cross**; cannot be `ignore_bins` (19.5) | `illegal_bins il = default` in `csrng_agent_cov` and `otbn_env_cov` |
| `bins b = {list} with (expr)` / `bins b = cp with (expr)` | keeps only values where `item` satisfies `expr`; evaluated "at the time the covergroup instance is constructed" (19.5.1.1) | `bins key_invalid = key_length with (!$onehot0(item))` |
| `bins b = queue_expr` | a set expression: any array of compatible type except associative, evaluated at construction (19.5.1.2) | `bins vector_list[] = valid_vec_q` in `hmac_env_cov` |
| `ignore_bins` | values removed from every bin after distribution; an emptied bin drops out of the percentage (19.5.5) | 25 files |
| `illegal_bins` | same removal, plus a run-time error when hit, with precedence over all other bins (19.5.6) | 19 files |

Two rules matter for the chapter's pitfalls. First, **value resolution**
(19.5.7): a bin value is cast to the coverpoint's type, and a value that
does not fit, or a signed negative against an unsigned point, draws a
warning and is dropped; `bins b2 = {-1, [1:10], 15}` on a `bit [2:0]`
becomes `{[1:7]}`. Second, **emptiness**: a bin "associated with no
values or sequences" is excluded from the calculation, so a `with` clause
that excludes everything, or an `ignore_bins` that swallows a whole auto
bin, changes the denominator silently rather than reporting a hole
(19.5.5, 19.11.1).

### 5. Cross coverage

A `cross` names two or more coverpoints or variables; a bare variable gets
an implicit `coverpoint V;`, and an expression cannot be crossed until it
has a named coverpoint. The cross is "the Cartesian product of the N sets
of coverage point bins", so two 4-bit variables give 256 bins and a 4-bit
variable against a 10-bin coverpoint gives 160 (19.6). Bins declared
`default`, ignored or illegal in a coverpoint create no cross bins, and
crossing across covergroups is a compile error (19.6).

**Cross bins** are select expressions: `binsof(cp)` or `binsof(cp.bin)`,
optionally `intersect {range_list}`, negated with `!`, combined with `&&`
and `||`; `with (expr)` over the crossed coverpoint names, and `matches
N` to require that many value tuples (default one); or a queue of
`CrossValType` tuples built by a function inside the cross for wide
points where enumerating the product "would be computationally
expensive" (19.6.1 through 19.6.1.4). User bins and auto bins coexist:
auto bins "are retained for those cross products that do not intersect
cross products specified by any user-defined cross bin" (19.6.1), which
is why Bromley says a cross must name bins for every combination or carry
"unwanted auto-generated bins that will distort your coverage figures"
(§9.2). `ignore_bins` on a cross removes tuples even when another cross
bin includes them (19.6.2); `illegal_bins` does the same and raises a
run-time error with precedence over ignore (19.6.3). On transition bins
`binsof` uses the last value of the transition (19.6.1.1).

OpenTitan uses `binsof` in 17 of 76 class files and cross `with` in
several: `ignore_bins unsupported = binsof(cp_baud_rate) intersect
{BaudRate1p5Mbps} && binsof(cp_clk_freq) intersect {24}` in
`uart_env_cov`; `illegal_bins test_1_state_0 = binsof(cp_intr_test)
intersect {1} && binsof(cp_intr_state) intersect {0}` in `intr_test_cg`;
`illegal_bins illegal = reset_cross with (reset_cp && sleep_cp)` in
`pwrmgr_env_cov`
[OpenTitan `hw/top_earlgrey/ip_autogen/pwrmgr/dv/env/pwrmgr_env_cov.sv`, commit 69d8208](https://github.com/lowRISC/opentitan/blob/master/hw/top_earlgrey/ip_autogen/pwrmgr/dv/env/pwrmgr_env_cov.sv).
Named-bin crosses versus auto-bin crosses differ in size only: `hmac`'s
`fifo_depth_cross` crosses an array bin over the FIFO-depth field with
four 1-bit auto-binned points, whereas `spi_device` shrinks a status
field to `auto_bin_max = 8` "so that cross coverage can be hit easier"
[OpenTitan `hw/ip/spi_device/dv/env/spi_device_env_cov.sv`, commit 69d8208](https://github.com/lowRISC/opentitan/blob/master/hw/ip/spi_device/dv/env/spi_device_env_cov.sv).

### 6. Options: what each means and where it may be set

Instance options (`option.*`, Table 19-1, 2017 text) and type options
(`type_option.*`, Table 19-3) are implicitly declared structs (19.10).
Setting the same option twice in one definition is an error, and
assignments in the definition are evaluated at instantiation (19.7).

| Option | Default | Effect | Set where |
|---|---|---|---|
| `option.weight` | 1 | weight of the instance in the overall instance score, or of a coverpoint/cross within its group; non-negative | group, coverpoint, cross; procedurally after `new` |
| `option.goal` | 100 | target percentage | group, coverpoint, cross; procedurally |
| `option.name` | tool-generated unique name | instance name in the database and report | group only; procedurally (`set_inst_name` is the method form) |
| `option.comment` | "" | saved in the database and report | group, coverpoint, cross; procedurally |
| `option.at_least` | 1 | minimum hits for a bin to count; the type computation uses the **maximum** `at_least` over instances (19.11.1) | group (default for items), coverpoint, cross; procedurally |
| `option.detect_overlap` | 0 | warn on overlapping value or transition lists in one coverpoint | group or coverpoint definition only |
| `option.auto_bin_max` | 64 | cap on auto bins | group (default for coverpoints) or coverpoint definition only |
| `option.cross_num_print_missing` | 0 | how many missing cross bins the report prints | group or cross |
| `option.per_instance` | 0 | when 1 the instance is saved and reported; when 0 tools "are not required" to keep it | group definition only |
| `option.get_inst_coverage` | 0 | with `merge_instances`, makes `get_inst_coverage()` per instance; otherwise it equals `get_coverage()` | group definition only |
| `type_option.weight`, `.goal`, `.comment` | 1, 100, "" | same roles for the type score; constants only, so no per-instance difference; settable as `cg::type_option.x` or `cg::cp::type_option.x` | group, coverpoint, cross; procedurally at any time |
| `type_option.strobe` | 0 | clocked samples taken in the Postponed region | group definition only |
| `type_option.merge_instances` | 0 | type score is the union of instances instead of their weighted average | group |
| `type_option.distribute_first` | 0 | distribute values into bins before applying `with` | group |

Group-level `weight`, `goal`, `comment` and `per_instance` do **not**
act as defaults for the items below them; the other instance options do
(19.7). There is no `option.cross_auto_bin_max` (finding 8). Measured
usage in OpenTitan's 76 class files: `per_instance` 39 files, `name` 37,
`auto_bin_max` 3, `weight`/`goal`/`at_least`/`comment`/`type_option`
none.

### 7. The API, and how the percentage is computed

Methods (Table 19-5): `sample()` on the group; `get_coverage()` and
`get_inst_coverage()` on group, coverpoint or cross, each returning a
real 0 to 100 and optionally filling two `ref int` arguments with covered
and total bins; `set_inst_name(string)` on the group; `start()` and
`stop()` on any of the three. `get_coverage()` is static, callable as
`cg::get_coverage()` or on an instance, and cumulative over all
instances; `get_inst_coverage()` is per instance only (19.8). Neither
reaches a bin: "there are no built in methods to report details of
individual bins", so a test that needs a bin's status gives it its own
coverpoint [Sutherland & Mills, SNUG Boston 2006](http://sutherland-hdl.com/papers/2006-SNUG-Boston_standard_gotchas_paper.pdf)
(§7.5), the trick Smith and Aynsley use to steer a `dist` from coverage
(§3.2, §3.3). System functions (19.9): `$set_coverage_db_name(file)`,
`$load_coverage_db(file)` and `$get_coverage()` for the overall type
coverage, which "shall return a value of 100.0" on a design with no
covergroup instances (19.11). The UVM guide names the instance in the
constructor with `cov_trans.set_inst_name({get_full_name(), ".cov_trans"})`
and gates sampling with a `coverage_enable` bit settable through
`uvm_config_db` (§3.12.1, §4.10.3). OpenTitan calls none of the query
methods in its coverage classes (0 of 76 files); closure is done in the
database, which is Part B.

**Computation (19.11).** A group's score is the weighted average of its
items' scores, Σ(W_i × C_i) / Σ W_i. A coverpoint with user bins scores
covered bins over defined bins; with auto bins, covered over
min(`auto_bin_max`, 2^M); a bin with no values is dropped from both
numerator and denominator, and a bin counts as covered only when its hits
reach `at_least` (19.11.1). A cross scores covered bins over B_c + B_u,
where B_c is the auto-cross bins remaining after user bins take their
products and B_u the significant user bins excluding ignore and illegal
(19.11.2). Type coverage is the weighted average of instance scores when
`merge_instances` is 0 and the union of bins matched by name when it is
1; the standard's example has two instances with bins `b[0..1]` and
`b[1..2]`, one hit each on 0 and 1, giving 66.67% for the type and 100%
and 50% for the instances (19.11.3). A zero denominator returns 0.0 for a
nonzero-weight item and 100.0 for a zero-weight one (19.11). Smith and
Aynsley add the consequence for queries: with `at_least = 5`, a bin hit
four times shows 4/5 in the report but the coverpoint's `get_coverage()`
counts it as uncovered (§3.2).

### 8. What goes wrong: the catalog for the chapter's Pitfalls

| # | Symptom | Cause in the language | Source | Fix the chapter teaches |
|---|---|---|---|---|
| 1 | Group reports 0% forever, no message | embedded covergroup never assigned in `new()`; or event never fires / `sample()` never called | 19.4; [Sutherland 2007 §6.1](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf) | construct in `new()`; assert `get_inst_coverage() > 0` in a smoke test |
| 2 | 100% on a 32-bit address after 64 transactions | auto bins: N = min(2^M, 64); score is covered/N | 19.5.3, 19.11.1; [UVM UG §3.12.1](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf) | name the bins; treat `auto_bin_max` as a debugging default |
| 3 | Cross has millions of bins, run slows, report unreadable | Cartesian product; auto cross bins retained for every unnamed tuple; no `default` for a cross | 19.6, 19.6.1; [Ellis & Jain 2018 §IV](https://dvcon-proceedings.org/wp-content/uploads/unraveling-the-complexities-of-functional-coverage-an-advanced-guide-to-simplify-your-use-model.pdf) [vendor]; [Bromley 2016 §9.2](https://assets.website-files.com/63f4bb21bd5303fe472ad00e/64957f836fbf7349210cf29c_bromley_coverage_paper.pdf) | bin the points first; name cross bins with `binsof`/`with`; `ignore_bins` the unreachable |
| 4 | Sample taken before the value is valid, or twice per cycle | clocked sampling is immediate and repeats per event; race with the producing process | 19.3; [Sprott 2015 "When to sample"](https://dvcon-proceedings.org/wp-content/uploads/navigating-the-functional-coverage-black-hole-be-more-effective-at-functional-coverage-modeling.pdf); OpenTitan `i2c_protocol_cov.sv` flops the state "so we don't race against new events" | `sample(args)` from the monitor after the transaction completes; `strobe` or a clocking-block signal for clocked groups |
| 5 | Test fails mid-run from a coverage file, or does not fail when coverage is off | `illegal_bins` is a run-time error with precedence over all bins; a disabled group raises nothing | 19.5.6, 19.6.3; [Smith & Aynsley 2011 §4.1](https://dvcon-proceedings.org/wp-content/uploads/a-practical-look-systemverilog-coverage-tips-tricks-and-gotchas.pdf); [lowRISC DV style](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md) | `ignore_bins` plus an assertion or scoreboard check |
| 6 | One instance hit everything, report says 100% for the type | type score averages or merges instances; `per_instance` off by default; auto-generated instance names | Table 19-1, 19.8, 19.11.3; [Sutherland 2007 §6.2](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf); [Ellis & Jain 2018 §II, §III](https://dvcon-proceedings.org/wp-content/uploads/unraveling-the-complexities-of-functional-coverage-an-advanced-guide-to-simplify-your-use-model.pdf) [vendor] | `option.per_instance = 1` and `option.name` when instances differ; know which of the two numbers the report shows |
| 7 | Coverage full, bug escapes | the sampled value was never checked; register or stimulus coverage without observed behavior | [Sprott 2015](https://dvcon-proceedings.org/wp-content/uploads/navigating-the-functional-coverage-black-hole-be-more-effective-at-functional-coverage-modeling.pdf) planning §A, §F, §G; [Bromley 2016 §6](https://assets.website-files.com/63f4bb21bd5303fe472ad00e/64957f836fbf7349210cf29c_bromley_coverage_paper.pdf) | every coverpoint pairs with a check; sample what a monitor or scoreboard observed |
| 8 | Sampling in the driver | counts stimulus applied, not behavior seen; the driver runs before the DUT reacts | [UVM UG §3.12.1](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf); [OpenTitan methodology](https://github.com/lowRISC/opentitan/blob/master/doc/contributing/dv/methodology/README.md) | monitor and scoreboard sample; `uvm_subscriber` for a coverage collector ([Bromley §5.1](https://assets.website-files.com/63f4bb21bd5303fe472ad00e/64957f836fbf7349210cf29c_bromley_coverage_paper.pdf)) |
| 9 | Bin vanishes, denominator shrinks | `with` excludes every value, `ignore_bins` empties an auto bin, or value resolution drops out-of-range literals with a warning; empty bins leave the calculation | 19.5.1.1, 19.5.5, 19.5.7, 19.11.1 | read the warnings; check `get_inst_coverage(covered, total)` totals in a unit test |
| 10 | `bins a[4] = default` gives no coverage and no cross | `default` bins are excluded from the score and from crosses | 19.5, 19.6; [Smith & Aynsley 2011 §4.2](https://dvcon-proceedings.org/wp-content/uploads/a-practical-look-systemverilog-coverage-tips-tricks-and-gotchas.pdf) | `$` ranges or `wildcard bins`; `default` only as a catch-all sentinel |
| 11 | Compile error passing constants to `new` | sticky `ref` direction on later arguments | [Sutherland 2007 §6.3](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf) | write `input`/`ref` on every argument |
| 12 | Coverpoint reports 0% though the bin shows 4/5 hits | `at_least` makes the bin uncovered; `get_coverage()` returns whole bins over bins | 19.11.1; [Smith & Aynsley 2011 §3.2](https://dvcon-proceedings.org/wp-content/uploads/a-practical-look-systemverilog-coverage-tips-tricks-and-gotchas.pdf) | one coverpoint per value when a bin must be queried |
| 13 | Missing bins: tested values fall in no bin, holes look closed | bins defined by hand from the spec; the language reports only defined bins | [Lee et al., DVCon 2024](https://dvcon-proceedings.org/wp-content/uploads/1062.pdf): 14.1% of holes in a cache IP were missing bins | a `default` sentinel bin, reviewed, or the paper's queue-and-waiver method |
| 15 | Bin range silently too small | `^` is XOR and binds looser than `-`; `2^(w)-1` is `2 ^ (w-1)`; both operands legal, no warning | finding 10; [OpenTitan `hmac_env_cov.sv`](https://github.com/lowRISC/opentitan/blob/master/hw/ip/hmac/dv/env/hmac_env_cov.sv) | `2**w - 1` or `{w{1'b1}}`; unit-test bin counts with `get_inst_coverage(covered, total)` |
| 14 | Covergroup wanted in `build_phase`, cannot be | embedded covergroups are assignable only in `new()` | 19.4; [Bromley 2016 §10.1](https://assets.website-files.com/63f4bb21bd5303fe472ad00e/64957f836fbf7349210cf29c_bromley_coverage_paper.pdf) | wrapper object built later; OpenTitan `*_cg_wrap` classes |

### Unsourced-claims table

| Claim | Status |
|---|---|
| Clause 19 numbers as they appear in IEEE 1800-2023 | inferred: top-level 19.3 to 19.11 confirmed by slang's table; third-level numbers (19.5.x, 19.6.x, 19.11.x) are 2017 numbers, read in the 2017 text, not confirmed for 2023 |
| What 1800-2023 added to clause 19 | second-hand from slang's changelog; the 2023 text was not read |
| "A driver samples before the DUT reacts" (row 8) | reasoning from Chapter 4's scheduling material, not a quoted source; the sources cited say only *where* to sample |
| OpenTitan counts (417 / 322 / 104 / 49 covergroups; option and construct file counts) | measured by `grep` on the files listed by the GitHub tree API at commit 69d8208 on 2026-09-26; `covergroup ` counted at line start, so commented-out declarations are excluded but string mentions are not |
| Verilator 5.052 "runs covergroups" | documented only; nothing here was executed. Part C measures it |
| Ellis & Jain figures (screenshots of a vendor GUI) | vendor material; the numbers repeated here (50% / 100%) follow from 19.11.3 independently |

### Key sources

Existing keys reused: `sutherland2006gotchas`, `sutherland2007gotchas`,
`spear2012svfv` (add to its note: Ch. 9 "Functional Coverage", pp.
323--361, per the Crossref chapter record for
`10.1007/978-1-4614-0715-7_9`), `lowrisc-dv-style`, `ieee1800-2023`,
`accellera2015uvmug`, `slang-docs`, `verilator-languages`,
`verilator-warnings`, `verilator-changes`, `opentitan-dv-methodology`.
New entries:

```bibtex
@misc{ieee1800-2017,
  author       = {{IEEE}},
  title        = {{IEEE} Std 1800-2017, {IEEE} Standard for {SystemVerilog}:
                  Unified Hardware Design, Specification, and Verification
                  Language},
  howpublished = {IEEE Standards Association},
  year         = {2018},
  url          = {https://standards.ieee.org/ieee/1800/6700/},
  note         = {Clause 19 read from the copy hosted for MIT 6.205 at
                  https://fpga.mit.edu/6205/_static/F23/documentation/1800-2017.pdf.
                  Accessed 2026-09-26}
}

@misc{ieee1800-2012,
  author       = {{IEEE}},
  title        = {{IEEE} Std 1800-2012, {IEEE} Standard for {SystemVerilog}:
                  Unified Hardware Design, Specification, and Verification
                  Language},
  howpublished = {IEEE Standards Association},
  year         = {2013},
  url          = {https://standards.ieee.org/ieee/1800/4869/},
  note         = {Published 2013-02-21. Clause 19 read from the copy hosted
                  at https://ece.uah.edu/~gaede/cpe526/ and diffed against
                  the 2017 text. Accessed 2026-09-26}
}

@inproceedings{smithaynsley2011coverage,
  author    = {Doug Smith and John Aynsley},
  title     = {A Practical Look @ {SystemVerilog} Coverage -- Tips, Tricks,
               and Gotchas},
  booktitle = {Design and Verification Conference (DVCon) US},
  year      = {2011},
  url       = {https://dvcon-proceedings.org/wp-content/uploads/a-practical-look-systemverilog-coverage-tips-tricks-and-gotchas.pdf},
  note      = {Accessed 2026-09-26}
}

@inproceedings{sprott2015coverage,
  author    = {Jason Sprott and Paul Marriott and Matt Graham},
  title     = {Navigating The Functional Coverage Black Hole: Be More
               Effective At Functional Coverage Modeling},
  booktitle = {Design and Verification Conference (DVCon) US},
  year      = {2015},
  url       = {https://dvcon-proceedings.org/wp-content/uploads/navigating-the-functional-coverage-black-hole-be-more-effective-at-functional-coverage-modeling.pdf},
  note      = {Session 13.4, 2015-03-04. Accessed 2026-09-26}
}

@inproceedings{bromleylitterick2016coverage,
  author    = {Jonathan Bromley and Mark Litterick},
  title     = {Effective {SystemVerilog} Functional Coverage: Design and
               Coding Recommendations},
  booktitle = {Synopsys Users Group (SNUG)},
  year      = {2016},
  url       = {https://assets.website-files.com/63f4bb21bd5303fe472ad00e/64957f836fbf7349210cf29c_bromley_coverage_paper.pdf},
  note      = {Hosted by Verilab. Accessed 2026-09-26}
}

@inproceedings{ellisjain2018coverage,
  author    = {Thomas Ellis and Rohit Jain},
  title     = {Unraveling the Complexities of Functional Coverage: An
               Advanced Guide to Simplify Your Use Model},
  booktitle = {Design and Verification Conference (DVCon) US},
  year      = {2018},
  url       = {https://dvcon-proceedings.org/wp-content/uploads/unraveling-the-complexities-of-functional-coverage-an-advanced-guide-to-simplify-your-use-model.pdf},
  note      = {Vendor authors (Mentor); tool screenshots are vendor
               material. Accessed 2026-09-26}
}

@inproceedings{lee2024missingbins,
  author    = {Jikjoo Lee and Tony Gladvin George and Kihyun Park and
               Dongkun An and Wooseong Cheong and ByungChul Yoo},
  title     = {Tackling Missing Bins: Refining Functional Coverage in
               {SystemVerilog} for Deterministic Coverage Closure},
  booktitle = {Design and Verification Conference (DVCon)},
  year      = {2024},
  url       = {https://dvcon-proceedings.org/wp-content/uploads/1062.pdf},
  note      = {Accessed 2026-09-26}
}

@misc{opentitan-cov-classes,
  author       = {{lowRISC contributors (OpenTitan project)}},
  title        = {{OpenTitan} functional coverage classes and bound
                  coverage interfaces},
  howpublished = {GitHub, lowRISC/opentitan, commit 69d8208},
  year         = {2026},
  url          = {https://github.com/lowRISC/opentitan/tree/master/hw/dv/sv},
  note         = {Apache-2.0. Files cited: hw/dv/sv/cip\_lib/cip\_base\_env\_cov.sv,
                  hw/dv/sv/dv\_utils/dv\_fcov\_macros.svh,
                  hw/ip/uart/dv/env/uart\_env\_cov.sv,
                  hw/ip/hmac/dv/env/hmac\_env\_cov.sv,
                  hw/ip/otbn/dv/uvm/env/otbn\_env\_cov.sv,
                  hw/ip/spi\_device/dv/env/spi\_device\_env\_cov.sv,
                  hw/ip/i2c/dv/sva/i2c\_protocol\_cov.sv,
                  hw/top\_earlgrey/ip\_autogen/pwrmgr/dv/env/pwrmgr\_env\_cov.sv,
                  hw/ip/uart/dv/env/uart\_scoreboard.sv. Accessed 2026-09-26}
}

@misc{slang-changelog,
  author       = {Michael Popoloski},
  title        = {slang {CHANGELOG}},
  howpublished = {GitHub, MikePopoloski/slang},
  year         = {2026},
  url          = {https://github.com/MikePopoloski/slang/blob/master/CHANGELOG.md},
  note         = {v7.0 (2024-09-26) entry lists the IEEE 1800-2023
                  covergroup additions; the Unreleased entry documents
                  \texttt{--allow-cross-auto-bin-max}. Accessed 2026-09-26}
}
```

### Confidence notes

- **High**: every statement attributed to clause 19 was read in the 2017
  text and checked against the 2012 text; quotations are verbatim. The
  gotcha papers, the Doulos, Verilab, Mentor and Samsung DVCon papers, the
  Bromley SNUG paper, the UVM user guide sections and the OpenTitan files
  were read in full or in the cited sections.
- **Medium**: clause numbers below the second level as 2023 numbers
  (see the unsourced table). DVCon region for the 2018 and 2024 papers
  (the proceedings pages give the year only; both author lists are
  US-based or unspecified). Spear and Tumbush chapter 9's *content* is not
  cited anywhere; only its title and pages from the Crossref record.
- **Low / open**: none of the constructs was executed here. In
  particular, whether Verilator 5.052 honours `auto_bin_max`,
  `per_instance`, `illegal_bins` as an error, `get_coverage()` scaling
  and transition bins is Part C's question; nothing in this part should
  be printed as tool behavior. Block-event sampling `@@(begin ...)` has no
  real-world example in any source consulted; the chapter should mention
  it in one sentence or not at all.
- **Scope boundary kept**: closure, merging across runs, UCIS and
  exclusions are Part B; coverage-model design from the plan is Chapter
  2's note; `cover property` and assertion coverage belong to the SVA
  chapter and are mentioned only where Smith and Aynsley contrast them
  with covergroups.

---

# Part B — Why functional coverage exists, what it measures, and how closure is done

Scope: the coverage *method* rather than the covergroup syntax (Part A) or
the tool measurements (Part C). What each coverage kind measures and
misses; the coverage-driven argument as its originators made it and the
evidence for it; why coverage is not correctness; closure in practice
(merging, exclusions, ranking, holes, sign-off, UCIS); how OpenTitan
closes coverage; where coverage lives in UVM, `cocotb-coverage` and
FC4SC; and one paragraph of pointers to coverage-directed generation for
the later chapter. Chapter 2's note already established how a coverage
model is derived from a verification plan and the OpenTitan V-stage
checklist items; Chapter 1's note established the "coverage-model gap"
and the sign-off list. This part builds on those and does not restate
them.

### Findings that decide the chapter

1. **The two coverage kinds answer different questions, and the standards
   say so in plain words.** The UVM 1.2 User's Guide names them *explicit*
   (user-defined, "the user specifies the coverage goals, the needed
   values, and collection time") and *implicit* (automatic, "driven from
   the RTL"), and states the failure mode of each: explicit coverage "does
   not take into account" goals nobody wrote, implicit coverage "is not
   complete, since it does not take into account high-level abstract
   events and does not create associations between parallel threads"
   [UVM 1.2 User's Guide §4.10.1, 2015-10-08](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf).
   OpenTitan's methodology makes the same point with a two-gate example:
   an AND gate reaches 100% code coverage on inputs `00` and `11`, and
   "We could not say for certain that the design was in fact an AND gate:
   it could just as easily be an OR gate"; conversely, a functional model
   written for one gate stays at 100% when a second gate is added, "but
   half of the design was not exercised"
   [OpenTitan DV methodology, accessed 2026-09-26](https://github.com/lowRISC/opentitan/blob/master/doc/contributing/dv/methodology/README.md).
   That pair of examples is the chapter's motivation section, ready-made
   and open-licensed for redrawing.
2. **Coverage is a claim about stimulus, not about checking, and every
   serious source draws the line.** The lowRISC DV style guide forbids
   using `illegal_bins` as a checker, because a bin "will only be active
   when coverage is enabled" and "some simulators may still show a test to
   pass even when one of the `illegal_bins` condition is hit"
   [lowRISC DV coding style, accessed 2026-09-26](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).
   The mutation-analysis literature formalizes the gap as three
   conditions: a bug must be *activated*, *propagated* to an observable
   point, and *detected* by a checker; coverage measures only the first
   [Hampton, EDN, 2009-03-02](https://www.edn.com/functional-qualification-a-technical-brief/)
   (a vendor CTO's article, labelled as such),
   [Huang et al., VLSI Design, 2015](https://doi.org/10.1155/2015/256474)
   (peer-reviewed, same model). The chapter's central Pitfall is a
   covergroup that reaches 100% next to a scoreboard that checks nothing.
3. **Closure is a review process, not a number.** OpenTitan requires
   designers to "sign-off on exclusions in a PR review", annotates every
   exclusion with one of five prefixes (`UNR`, `NON_RTL`, `UNSUPPORTED`,
   `EXTERNAL`, `LOW_RISK`), keeps the tool-generated `CHECKSUM` so an
   exclusion is invalidated by a change to the code it excludes, and
   requires exclusion files to be "redone and re-reviewed" after any RTL
   change
   [OpenTitan DV methodology, accessed 2026-09-26](https://github.com/lowRISC/opentitan/blob/master/doc/contributing/dv/methodology/README.md).
   Its V2 gate is 90% and its V3 gate is "100% code and 100% functional
   coverage with waivers"
   [OpenTitan development stages, accessed 2026-09-26](https://github.com/lowRISC/opentitan/blob/master/doc/project_governance/development_stages.md).
   So "100%" is reached by subtracting reviewed exclusions from the
   denominator, and the chapter should teach the review, not the figure.
4. **The unreachable-versus-untested distinction is made by a formal
   tool, at a specific stage, and only for code coverage.** OpenTitan's
   `dvsim --cov-unr` runs a formal unreachability analysis over the merged
   simulation database; the output is reviewed by designer and DV
   engineer together; exclusions for unreachable code are added only
   "between the D2 and V3 stage when the design is frozen", never to reach
   an earlier gate; and "VCS UNR doesn't support assertion or functional
   coverage"
   [OpenTitan DV methodology, accessed 2026-09-26](https://github.com/lowRISC/opentitan/blob/master/doc/contributing/dv/methodology/README.md).
   "Getting to 90% coverage via functional tests is easy. Over 90% is the
   hard part as there may be a big chunk of unreachable codes" is the
   sentence for the chapter's closure section.
5. **Coverage from a failing test is discarded before merge.** `dvsim`
   deletes the per-test coverage directory when a run's status is not
   `PASSED`, so a run that hit a bin on the way to a failure contributes
   nothing
   [lowRISC dvsim `deploy.py`, accessed 2026-09-26](https://github.com/lowRISC/dvsim/blob/master/src/dvsim/job/deploy.py),
   and the VCS configuration says why: "so that coverage from failiing
   tests is not included in the final report"
   [OpenTitan `vcs.hjson`, accessed 2026-09-26](https://github.com/lowRISC/opentitan/blob/master/hw/dv/tools/dvsim/vcs.hjson).
   The chapter can state the rule as a methodology fact: a bin counts
   only when the test that hit it also passed its checks.
6. **UCIS 1.0 standardizes the database and API, not the merge.** The
   standard's own text: "The merging algorithm is not fully specified by
   this standard"; its history nodes record which test produced which
   counts; its `excluded` and `excludedReason` attributes carry waivers;
   and its target flow is "fast primary data collection in-memory by the
   simulator or formal tool, with export to disk"
   [Accellera UCIS 1.0, 2012-06-02](https://www.accellera.org/images/downloads/standards/ucis/UCIS_Version_1.0_Final_June-2012.pdf).
   Open readers and writers exist: FC4SC writes UCIS XML, and pyucis reads
   and converts it. cocotb-coverage does not write UCIS; it lists it as a
   roadmap item.
7. **The measured evidence for coverage-driven verification is adoption,
   not effectiveness.** Tasiran and Keutzer's 2001 survey frames coverage
   as the way to "measure the completeness of validation, and direct
   simulations toward unexplored areas"
   [OpenAlex record, accessed 2026-09-26](https://api.openalex.org/works/doi:10.1109/54.936247);
   no controlled comparison of coverage-driven against directed
   verification on a real design was found, and the chapter must not
   imply one. What is peer-reviewed is the *feedback loop*: Fine and
   Ziv's 2003 DAC paper closes it automatically with Bayesian networks
   [OpenAlex record, accessed 2026-09-26](https://api.openalex.org/works/doi:10.1145/775832.775907),
   and the chapter leaves that to the later research chapter.
8. **Where coverage lives is a structural decision the sources already
   made.** UVM's `uvm_subscriber` is a component with one analysis export
   and a pure virtual `write`
   [uvm-core `uvm_subscriber.svh`, accessed 2026-09-26](https://github.com/accellera-official/uvm-core/blob/main/src/comps/uvm_subscriber.svh);
   the UVM User's Guide says agents "might include other components, like
   coverage collectors" and that "A verification component should come
   with a protocol-specific functional-coverage model"
   [UVM 1.2 User's Guide §2.3, §4.10.2, 2015-10-08](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf);
   lowRISC names both an agent-level `<dut>_agent_cov` and an env-level
   `<dut>_env_cov` object
   [lowRISC DV coding style, accessed 2026-09-26](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).
   Protocol coverage sits in the agent; feature crosses sit in the env.

---

### 1. What each coverage kind measures, and what it misses

**Code coverage** is derived from the RTL by the simulator with no
authoring effort, which is why the UVM User's Guide calls it *implicit*
and OpenTitan calls it "implicit coverage as it is generated based on
the code and takes no additional effort to implement"
[UVM 1.2 User's Guide §4.10.1, 2015-10-08](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf),
[OpenTitan DV methodology, accessed 2026-09-26](https://github.com/lowRISC/opentitan/blob/master/doc/contributing/dv/methodology/README.md).
The kinds, in the open definitions OpenTitan gives:

| Kind | Measures | Source wording |
|---|---|---|
| Line | which RTL lines executed | "measures which lines of SystemVerilog RTL code were executed during the simulation" |
| Toggle | each bit seen going both `0→1` and `1→0` | "measures every logic bit to see if it transitions from 1 → 0 and 0 → 1" |
| FSM state | which states were entered | "measures which finite state machine states were executed" |
| FSM transition | which arcs were taken | "measures which arcs were traversed for each finite state machine" |
| Conditional | combinations of a conditional expression's inputs | "tracks all combinations of conditional expressions simulated" |
| Branch | control-flow alternatives taken, plus conditions | "tracks the flow of simulation (e.g. if/else blocks) as well as conditional expressions" |

[OpenTitan DV methodology, accessed 2026-09-26](https://github.com/lowRISC/opentitan/blob/master/doc/contributing/dv/methodology/README.md).
UCIS 1.0 gives each of these a data model (branch, statement and block,
condition and expression, toggle, FSM) and adds a taxonomy the chapter
can use: code-coverage metrics are "input-contribution metrics,
expression value coverage metrics and transition coverage metrics";
covergroups and assertions "have their own definitions"
[Accellera UCIS 1.0 §4.9.5, §6.5, 2012-06-02](https://www.accellera.org/images/downloads/standards/ucis/UCIS_Version_1.0_Final_June-2012.pdf).
Two limits are stated by the sources themselves. Toggle coverage on
everything is "very difficult, and not particularly useful", so OpenTitan
closes it only on DUT and pre-verified-IP ports; and FSM holes "almost
always" show up as branch holes too, so the metrics overlap
[OpenTitan DV methodology, accessed 2026-09-26](https://github.com/lowRISC/opentitan/blob/master/doc/contributing/dv/methodology/README.md).
UCIS adds the deeper limit: a metric "explicitly does not define or
record the sampling rules", and binning loses information that "is not
re-constructable in the general case"; its own example shows the same
two observed values scoring 2/256 under one binning and 2/8 under
another
[Accellera UCIS 1.0 §4.9.1, 2012-06-02](https://www.accellera.org/images/downloads/standards/ucis/UCIS_Version_1.0_Final_June-2012.pdf).
A coverage percentage is therefore a property of the metric's binning
as much as of the stimulus, a point the chapter should make before it
shows any number.

**Functional coverage** is written by hand against the plan (Chapter 2's
note covers the derivation). OpenTitan's definition: it captures
"whether signals (that reflect the current state of the design) have met
an interesting set or a sequence of values (often called corner cases)",
is sampled "in 'reactive' components of the testbench, such as monitors
and/or the scoreboards", and a cross "asserts that several coverage
points are hit at once"
[OpenTitan DV methodology, accessed 2026-09-26](https://github.com/lowRISC/opentitan/blob/master/doc/contributing/dv/methodology/README.md).
What it misses is exactly what nobody wrote: "The disadvantage of such
metrics is that missing goals are not taken into account"
[UVM 1.2 User's Guide §4.10.1, 2015-10-08](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf).
The Guide's recommendation is the ordering the chapter should teach:
"Starting with explicit coverage is recommended", with implicit coverage
"as a 'safety net' to check and balance the explicit coverage", and the
diagnostic "Reaching 100% functional coverage with very low
code-coverage typically means the functional coverage needs to be
refined and enhanced" (same source).

**Assertion coverage** is the third kind and the one the book's other
chapters will keep meeting. OpenTitan counts it under "cover property
coverage", observes "events or series of events" such as a
valid/ready handshake, and notes that "an assertion precondition counts
as a cover point"
[OpenTitan DV methodology, accessed 2026-09-26](https://github.com/lowRISC/opentitan/blob/master/doc/contributing/dv/methodology/README.md).
UCIS models SVA/PSL `cover` and `assert` separately (§6.6.1, §6.6.2),
so an assertion that never had its antecedent satisfied is visible as
uncovered, which is the sourced form of "a vacuous assertion is a
coverage hole"
[Accellera UCIS 1.0 §6.6, 2012-06-02](https://www.accellera.org/images/downloads/standards/ucis/UCIS_Version_1.0_Final_June-2012.pdf).

**The canonical books.** Piziali's *Functional Verification Coverage
Measurement and Analysis* is the standard reference on coverage-model
design; the publisher record gives Springer US, Boston, 2004, and the
original Kluwer ISBN 1-4020-8025-5 with a June 2004 date
[Crossref record, accessed 2026-09-26](https://api.crossref.org/works/10.1007/b117979),
[Open Library record, accessed 2026-09-26](https://openlibrary.org/isbn/1402080255.json).
Tasiran and Keutzer's survey in *IEEE Design & Test* 18(4), pp. 36–45
is the peer-reviewed taxonomy; its abstract states the three jobs of a
metric: "ensure optimal use of resources, measure the completeness of
validation, and direct simulations toward unexplored areas of design"
[OpenAlex record, accessed 2026-09-26](https://api.openalex.org/works/doi:10.1109/54.936247).
The VMM's chapter "Coverage-Driven Verification" (pp. 259–280) is where
the method got its name in print
[Crossref record, accessed 2026-09-26](https://api.crossref.org/works/10.1007/0-387-25556-7_6).
None of the three texts was read in full this run (see Confidence
notes); their metadata is verified and the chapter should cite them for
authorship and priority, not for quotations.

### 2. The coverage-driven argument, and the evidence for it

The argument as the method's users state it has two halves. The first
is that random stimulus without a measure is noise: OpenTitan's
methodology says the purpose of coverage is "to flush out flaws in the
design", meaning "either design bugs or deficiencies in the design with
respect to the specification", and then puts the operational question,
"When are we done testing?", with the answer "Only coverage can answer
this question for you"
[OpenTitan DV methodology, accessed 2026-09-26](https://github.com/lowRISC/opentitan/blob/master/doc/contributing/dv/methodology/README.md).
The second half is that coverage should steer stimulus, not merely
score it. Tasiran and Keutzer put "direct simulations toward unexplored
areas of design" in the abstract of their 2001 survey
[OpenAlex record, accessed 2026-09-26](https://api.openalex.org/works/doi:10.1109/54.936247),
and the VMM's "Coverage-Driven Verification" chapter is the
practitioner statement of the loop: constrain, run, measure, re-aim
[Crossref record, accessed 2026-09-26](https://api.crossref.org/works/10.1007/0-387-25556-7_6).
The lineage through *e* and Vera is in Chapter 7's note (Part B §1.1)
and is not repeated; the chapter should reference it rather than
retell it.

The measured evidence is thin in the same way Chapter 7's note found for
constrained-random: adoption is documented, effectiveness against an
alternative is not. The Wilson Research Group series plots adoption of
code coverage, functional coverage, assertions and constrained-random
together as one "maturing" trend, and is a vendor-commissioned survey
[Foster, WRG 2020 IC/ASIC report, accessed 2026-09-26](https://uobdv.github.io/Design-Verification/WilsonResearchGroupFunctionalVerificationStudy/2020-WRGFV-Study/ic-asic-trend-report_2020-wilson-research-verification-study_hfoster.pdf)
[@foster2020wrg]. The UVM User's Guide simply assumes the method
("Completing all your coverage goals should be one of the metrics used
to determine the completion of the DUT's verification")
[UVM 1.2 User's Guide §4.10.1, 2015-10-08](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf).
The one peer-reviewed line that does measure something is the
coverage-directed generation literature (§7 below), which measures how
fast a learned generator closes a coverage model, not whether the model
finds bugs. The honest framing for the chapter: coverage-driven
verification is justified by the structure of the problem (you cannot
enumerate what you did not think of, so you measure what you reached),
and the OpenTitan text is the sourced statement of that structure. No
percentage should be attached to "coverage-driven finds more bugs".

### 3. Coverage is not correctness

The argument has three parts, each with a source of a different kind.

**The structural argument.** A bin records that a value or a cross of
values was observed at a sampling point. Nothing in that record says
the design's response was compared with anything. The UVM User's Guide
keeps the two activities in separate components on the same analysis
port, "such as coverage collectors and scoreboards"
[UVM 1.2 User's Guide §2.3.3, 2015-10-08](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf),
and the lowRISC style guide turns the separation into a rule: "Do not
use `illegal_bins` as a checker", with the two reasons that a bin "will
only be active when coverage is enabled" and that "some simulators may
still show a test to pass even when one of the `illegal_bins` condition
is hit"; the check "must be outside the coverage enable sampling blocks"
[lowRISC DV coding style, accessed 2026-09-26](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).
OpenTitan's methodology adds the mirror case from the design side: with
only the cover points for one gate, adding a second gate leaves
functional coverage at 100% while "half of the design was not exercised"
[OpenTitan DV methodology, accessed 2026-09-26](https://github.com/lowRISC/opentitan/blob/master/doc/contributing/dv/methodology/README.md).

**The mutation-analysis argument.** Mutation analysis inserts artificial
bugs and asks whether the testbench fails. Its practitioners describe
three conditions a testbench must meet, quoted here from the CTO of the
company that built the first commercial hardware tool (a vendor source,
labelled): "The bug must be activated; i.e. the code containing the bug
is exercised", "The bug must be propagated to an observable point", and
"The bug must be detected; i.e. behavior is checked and a failure
indicated"
[Hampton, EDN, 2009-03-02](https://www.edn.com/functional-qualification-a-technical-brief/).
Coverage, code or functional, measures activation only. The tool
itself, Certitude, is described in a peer-reviewed venue as "a
commercial software tool performing mutation analysis" that "has been
deployed within the microelectronics industry"
[OpenAlex record for Hampton and Petithomme 2007, accessed 2026-09-26](https://api.openalex.org/works/doi:10.1109/TAIC.PART.2007.39)
[@hampton2007certitude]; its current vendor page says only that it
activates, propagates and detects "systematic faults" to expose
weaknesses in "stimuli, observability, checkers, assertions, &
verification plan" and gives no figures
[Synopsys, Testbench Quality Assurance, accessed 2026-09-26](https://www.synopsys.com/verification/simulation/certitude.html)
(vendor claim). The independent, open-access statement of the same
model is Huang, Zhu, Yan and Yan in *VLSI Design* 2015: "Current
approaches emphasize activation using coverage models but neglect
propagation and detection", with a mutation-based metric and an
iterative refinement loop evaluated on two designs
[OpenAlex record, accessed 2026-09-26](https://api.openalex.org/works/doi:10.1155/2015/256474).
Its numbers were not retrieved (the full text returned 403 from both
hosts tried) and are not quoted. The software-testing result the book
already holds, Inozemtseva and Holmes's ICSE 2014 finding that coverage
"Is Not Strongly Correlated with Test Suite Effectiveness"
[@inozemtseva2014coverage], is the same conclusion by a different
route and belongs in the chapter as the software analogue, labelled as
such.

**What a checker-coverage pairing looks like.** The sourced pattern is
OpenTitan's: functional coverage is sampled in the monitor or the
scoreboard, the scoreboard does the checking, and the two are reviewed
together at the V2 gate, where "the fully implemented functional
coverage plan, the observed coverage and the coverage exclusions are
expected to be scrutinized to ensure there are no verification holes"
[OpenTitan signoff checklist, accessed 2026-09-26](https://github.com/lowRISC/opentitan/blob/master/doc/project_governance/checklist/README.md).
The Chapter 2 note's four planning questions (feature, conditions,
infrastructure, check) already put the check next to the coverage item
in the plan. For the chapter, the pairing rule can be stated without a
new source: every covergroup names the checker that would fail if the
covered behavior were wrong, and a covergroup that cannot name one is
measuring stimulus for its own sake.

### 4. Closure in practice

**Merging.** Each test run writes its own database; the regression
merges them into one for analysis, because closure is a property of the
regression and no single test is meant to close anything. OpenTitan:
"Coverage collected from all tests run as a part of the regression is
merged into a database for analysis"
[OpenTitan DV methodology, accessed 2026-09-26](https://github.com/lowRISC/opentitan/blob/master/doc/contributing/dv/methodology/README.md).
UCIS describes the same shape as its target flow, primary databases
from each run, then "post-analyzed or combined (merged) by custom UCIS
API applications", and is explicit that merging is under-specified:
"The merging algorithm is not fully specified by this standard". Its
use cases distinguish merging "similar databases", where "the topology
which produced the databases to be merged is the same", from
"dissimilar databases", where "Vendor tools may not support certain
types of merging", and warn that "Incremental changes to the design
also challenge merging because they create different topologies"
[Accellera UCIS 1.0 §2.1, §4.2, §4.3, 2012-06-02](https://www.accellera.org/images/downloads/standards/ucis/UCIS_Version_1.0_Final_June-2012.pdf).
That last sentence is the sourced reason a merged database is only as
old as the last RTL change. `dvsim` orders the primary build mode's
database first, keeps the last seven merged databases, and can fold the
previous regression's merge in with `--cov-merge-previous`
[lowRISC dvsim `deploy.py`, accessed 2026-09-26](https://github.com/lowRISC/dvsim/blob/master/src/dvsim/job/deploy.py).

**Grading and ranking.** UCIS lists as a use case "Comparing UCISDBs
from multiple verification runs across one or more coverage types to
evaluate and rank coverage efficiency"
[Accellera UCIS 1.0 §2.1, 2012-06-02](https://www.accellera.org/images/downloads/standards/ucis/UCIS_Version_1.0_Final_June-2012.pdf).
OpenTitan's report step asks the VCS report tool for test grading
("-grade index testfile", commented "Enable test grading using the
'index' scheme, and the generation of the list of contributing tests")
and for the list of tests that covered each object ("-show tests")
[OpenTitan `vcs.hjson`, accessed 2026-09-26](https://github.com/lowRISC/opentitan/blob/master/hw/dv/tools/dvsim/vcs.hjson),
and its Xcelium merge script writes a `runs.txt` "for the 'rank'
command"
[OpenTitan `cov_merge.tcl`, accessed 2026-09-26](https://github.com/lowRISC/opentitan/blob/master/hw/dv/tools/xcelium/cov_merge.tcl).
The flag semantics are vendor-defined and undocumented in the open; the
chapter should describe ranking as "which subset of tests reaches the
same coverage" and cite UCIS for the concept and OpenTitan for the
practice.

**Holes, by kind.** OpenTitan's text sorts them: "Coverage holes can be
addressed accordingly through either updating the design specification
and augmenting the testplan / written tests, or by optimizing the
design to remove unreachable logic if possible. There may be features
that cannot be tested and cannot be removed from the design either.
These would have to be analyzed and excluded from the coverage
collection as a waiver"
[OpenTitan DV methodology, accessed 2026-09-26](https://github.com/lowRISC/opentitan/blob/master/doc/contributing/dv/methodology/README.md).
So: *untested* holes get tests; *unreachable* holes get a design
change or a `UNR` exclusion proved by formal analysis (§5); *illegal*
values get a checker, not a bin (§3); and *unsupported* or
*out-of-scope* holes get a labelled, mandatory-explanation waiver.

**Exclusions and how they are reviewed.** The UCIS data model carries a
boolean `excluded` and a string `excludedReason` on every object
[Accellera UCIS 1.0 §9, 2012-06-02](https://www.accellera.org/images/downloads/standards/ucis/UCIS_Version_1.0_Final_June-2012.pdf),
so the reason travels with the waiver. OpenTitan's practice is the
detailed one and is in §5. The general rules it states are portable:
the designer signs off; every exclusion is annotated; annotations use a
fixed category prefix; an RTL change invalidates the file; and the
exclusion files themselves are a sign-off deliverable.

**Sign-off, and where 100% is not the goal.** OpenTitan's gates are
90% at V2 and "100% code and 100% functional coverage with waivers" at
V3 (Chapter 2's note has the full checklist rows). The methodology
text is candid that the last stretch is the expensive part, "Coverage
closure is perhaps the most time-consuming part of the whole DV effort,
often with low return", and that over-collection is itself a cost:
"Conservatively collecting coverage on everything might result in poor
ROI of DV user's time. Also, excessive coverage collection slows down
simulation"
[OpenTitan DV methodology, accessed 2026-09-26](https://github.com/lowRISC/opentitan/blob/master/doc/contributing/dv/methodology/README.md).
Its answer is to shape collection at compile time (toggle on ports
only, pre-verified sub-modules black-boxed), which is the sourced form
of "100% of the right denominator". Chapter 1's note lists the other
sign-off components (regression health, bug convergence, waiver review)
and they are not repeated.

**UCIS 1.0 in one paragraph.** Accellera's Unified Coverage
Interoperability Standard, version 1.0, dated 2012-06-02, defines "an
application programming interface (API) that enables the sharing of
coverage data across software simulators, hardware accelerators,
symbolic simulations, formal tools or custom verification tools", plus
"an abstract representation of the coverage database called the UCIS
database (UCISDB), the XML interchange format for text-based
interoperability". Its audience is "anyone performing electronic design
verification across multiple test platforms or multiple test runs and
wishing to merge the coverage information from various sources"
[Accellera UCIS 1.0 §1.1–1.2, 2012-06-02](https://www.accellera.org/images/downloads/standards/ucis/UCIS_Version_1.0_Final_June-2012.pdf).
Accellera's page calls it "a first step"
[Accellera, UCIS, accessed 2026-09-26](https://www.accellera.org/downloads/standards/ucis).
Who reads it: in the open, FC4SC writes it (§6) and pyucis, an
Apache-2.0 Python library last pushed 2026-08-31, reads and converts
"XML, YAML, and UCIS binary formats", imports "from Verilator,
cocotb-coverage, and AVL frameworks", and exports LCOV, Cobertura,
JaCoCo and Clover
[fvutils/pyucis README, accessed 2026-09-26](https://github.com/fvutils/pyucis).
Vendor support was not verified this run and is not claimed.

### 5. How OpenTitan closes coverage

The flow, end to end, from the project's own files. All URLs accessed
2026-09-26.

1. **Plan.** The Hjson testplan has two lists: testpoints and
   `covergroups`. Each covergroup entry has a `name` that "needs to map
   to the actual written covergroup, so that it can be audited from the
   simulation results", suffixed `_cg`, and a `desc` where listing the
   coverpoints and crosses is "recommended, but not necessary"
   [dvsim testplanner doc](https://github.com/lowRISC/dvsim/blob/master/doc/testplanner.md).
   Testpoints carry a `stage` of `V1`, `V2`, `V2S` or `V3`; there is no
   per-covergroup stage. (The lead's "cover" and "milestone" items are
   these `covergroups` and `stage` fields; `milestone` is not a key in
   the current format.) The HMAC plan is a filled example (`cfg_cg`,
   `status_cg`, `err_code_cg`, `msg_len_cg`, ...)
   [`hmac_testplan.hjson`](https://github.com/lowRISC/opentitan/blob/master/hw/ip/hmac/data/hmac_testplan.hjson);
   the UART plan still carries the `foo_cg` placeholder Chapter 2's note
   flagged
   [`uart_testplan.hjson`](https://github.com/lowRISC/opentitan/blob/master/hw/ip/uart/data/uart_testplan.hjson).
2. **Shape collection at compile time.** `cover.cfg` enables coverage
   on `tb.dut`, removes DV constructs (`pins_if`, `clk_rst_if`) and a
   list of pre-verified `prim_*` modules, re-enables only assertion
   coverage on the bound-in CSR and TileLink assertion modules, and
   limits toggle coverage to DUT ports plus the pre-verified modules'
   ports
   [`hw/dv/tools/vcs/cover.cfg`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/tools/vcs/cover.cfg).
   The build enables `line+cond+fsm+tgl+branch+assert`, ignores initial
   blocks, filters "unreachable/statically constant blocks", and does
   not count "zero-time glitches"
   [`vcs.hjson`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/tools/dvsim/vcs.hjson).
3. **Run, drop failures, merge, report.** Nightly regression runs each
   test with "a sufficiently large number of seeds (arbitrarily chosen
   to be 100)" and then "Collect and merge coverage" and "Publish the
   testplan-annotated regression and coverage results"
   [DV methodology](https://github.com/lowRISC/opentitan/blob/master/doc/contributing/dv/methodology/README.md).
   A failed run's coverage directory is deleted (§ Findings 5); the
   merge job runs "even if one test passes"; the report job parses the
   tool's text dashboard into the per-metric totals the regression
   dashboard shows
   [dvsim `deploy.py`](https://github.com/lowRISC/dvsim/blob/master/src/dvsim/job/deploy.py).
   The same structure exists for Xcelium with `imc` and refinement
   files instead of `urg` and exclusion files
   [`xcelium.hjson`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/tools/dvsim/xcelium.hjson).
4. **Exclude, with a category and a checksum.** Shared exclusions live
   in `common_cov_excl.cfg`, each line prefixed by its category, for
   example "[UNSUPPORTED] Based on our Comportable IP spec, these TL
   pins are reserved / unused" and "[UNR] design ties these outputs to
   zeros"
   [`common_cov_excl.cfg`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/tools/vcs/common_cov_excl.cfg).
   Block-specific files are tool-generated: the UART file is one branch
   exclusion, `ANNOTATION: "[UNR] default branch"`, with a `CHECKSUM`
   and the instance and branch it names
   [`uart_cov_excl.el`](https://github.com/lowRISC/opentitan/blob/master/hw/ip/uart/dv/cov/uart_cov_excl.el).
   The methodology says to keep the checksum "as it checks the
   exclusion isn't outdated by changes on the corresponding code" and
   not to bypass that check
   [DV methodology](https://github.com/lowRISC/opentitan/blob/master/doc/contributing/dv/methodology/README.md).
5. **Prove unreachability formally, late.** `dvsim ... --cov-unr` runs
   the vendor's formal unreachability analysis (metrics
   `line+cond+fsm+tgl+branch`, not assertion or functional) against the
   merged database; the output is reviewed by designer and DV engineer
   and, if accepted, submitted as a PR to the exclusion file. Timing
   rule: designers may run it early, but exclusions are added "between
   the D2 and V3 stage when the design is frozen", and "it is not the
   right thing to add a coverage exclusion file to reach the 80% needed
   for V2". No reuse of exclusions between IP-level and top-level
   benches, "since they are independently closed for coverage"
   [DV methodology](https://github.com/lowRISC/opentitan/blob/master/doc/contributing/dv/methodology/README.md).
   (The "80%" in that sentence disagrees with the 90% V2 gate elsewhere
   in the same project; see Unsourced claims.)
6. **Gate.** V2: code coverage (line, toggle, FSM, branch, assertion) at
   90%, toggle on DUT and pre-verified sub-module ports "individually
   reached 90% in both directions", functional coverage 90%. V2S:
   exclusions added to reach V2 for countermeasure blocks "should be
   removed", and UNR exclusions must be regenerated "as fault injection
   can exercise countermeasures which are deemed as unreachable code".
   V3: all metrics at 100%, and "All coverage exclusion files and
   coverage configuration file ... should be checked during sign-off"
   [Signoff checklist](https://github.com/lowRISC/opentitan/blob/master/doc/project_governance/checklist/README.md),
   [DV methodology](https://github.com/lowRISC/opentitan/blob/master/doc/contributing/dv/methodology/README.md).

The lowRISC DV style guide's contribution is the `illegal_bins` rule
(§3) and the naming of two collection objects, `<dut>_env_cov` and
`<dut>_agent_cov`
[lowRISC DV coding style](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).

### 6. Coverage in the book's other flows

**UVM.** `uvm_subscriber #(T)` is a `uvm_component` holding one
`uvm_analysis_imp` named `analysis_export` and a `pure virtual function
void write(T t)`; the source tags `write` as IEEE 1800.2-2020 clause
13.9.3.2
[uvm-core `uvm_subscriber.svh`, accessed 2026-09-26](https://github.com/accellera-official/uvm-core/blob/main/src/comps/uvm_subscriber.svh).
The User's Guide shows a coverage collector as exactly that subclass
connected to a monitor's analysis port, says agents "might include
other components, like coverage collectors, protocol checkers", and
says a reusable verification component "should come with a
protocol-specific functional-coverage model" that a user may partly
disable or extend with crosses against "other attributes in the
system", its example being transaction type crossed with FIFO status
[UVM 1.2 User's Guide §2.3.3, §4.10.2–4.10.3, 2015-10-08](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf).
That is the agent/env split: protocol coverage ships with the agent;
crosses that need two interfaces or DUT state live in the env, which
is where lowRISC's `<dut>_env_cov` sits.

**cocotb-coverage.** A BSD-2-Clause Python package by Marek Cieplucha,
release 2.0 dated 2025-10-03, requiring `cocotb >= 2.0` and Python 3.11
or later
[cocotb-coverage repository, accessed 2026-09-26](https://github.com/mciepluc/cocotb-coverage),
[`setup.py`, accessed 2026-09-26](https://github.com/mciepluc/cocotb-coverage/blob/master/setup.py).
Its model is decorator-based: `CoverPoint` "corresponds to a
SystemVerilog coverpoint", `CoverCross` to a cross with "a list of bins
to be ignored and an optional ignore relation function", and
`CoverCheck` is "a higher-level assertion"; sampling happens at each
call of the decorated function rather than by a separate sample method
[cocotb-coverage docs, accessed 2026-09-26](https://cocotb-coverage.readthedocs.io/en/latest/introduction.html).
Export is `coverage_db.export_to_xml()` and `export_to_yaml()` in the
package's own schema, with a `merge_coverage()` function over files of
either kind; UCIS is listed under "Planned basic support"
[`coverage.py`, accessed 2026-09-26](https://github.com/mciepluc/cocotb-coverage/blob/master/cocotb_coverage/coverage.py).
(pyucis imports that XML, §4.)

**FC4SC.** "Functional Coverage for SystemC", a "header only C++11
library", Apache-2.0; the Accellera repository states it "is the
reference implementation provided by the Accellera Systems Initiative
and is developed by the SystemC Verification Working Group", offers
"covergroups, bins, and coverpoints to enable type- and instance-based
functional coverage", and "will store the coverage results in the
Unified Coverage Interoperability Standard (UCIS) format"
[accellera-official/fc4sc README, accessed 2026-09-26](https://github.com/accellera-official/fc4sc).
The AMIQ origin is the company's own 2018-02-22 announcement, which
says the library "saves collected data in UCIS format in order to be
compatible with functional coverage tools provided by 3rd party
vendors" (author's account, labelled)
[AMIQ Consulting, 2018-02-22](https://www.consulting.amiq.com/2018/02/22/cpp-implementation-of-functional-coverage-for-systemc/).
The original repository's `docs/` holds a User Guide and an
"FC4SC_Feature_Comparison_SV_vs_FC4SC.pdf"; `tools/` holds
`coverage_merge`, `coverage_report`, `gui` and `ucis_parser.py`
[amiq-consulting/fc4sc, accessed 2026-09-26](https://github.com/amiq-consulting/fc4sc).
Last pushes: Accellera repo 2023-07-12, AMIQ repo 2022-10-05 (GitHub
API, same dates). Neither PDF was read this run.

### 7. The research frontier, as pointers only

Coverage-directed test generation closes the loop of §2 automatically.
The founding paper is Fine and Ziv, "Coverage directed test generation
for functional verification using Bayesian networks", DAC 2003, pp.
286–291, which builds "an efficient feedback mechanism connecting
coverage metrics back to test stimulus generation"
[OpenAlex record, accessed 2026-09-26](https://api.openalex.org/works/doi:10.1145/775832.775907).
The survey to cite is Ioannides and Eder, "Coverage-Directed Test
Generation Automated by Machine Learning – A Review", *ACM TODAES*
17(1), 2012
[Crossref record, accessed 2026-09-26](https://api.crossref.org/works/10.1145/2071356.2071363).
Both are metadata-verified only; the later chapter reads them.

### Unsourced-claims table

| Claim as it might be written | Status | What to print instead |
|---|---|---|
| "Coverage-driven verification finds more bugs than directed testing." | No controlled study found; only adoption surveys (vendor-commissioned). | State the structural argument and cite OpenTitan's "Only coverage can answer this question"; attach no percentage. |
| "Tasiran and Keutzer classify metrics as code-based, circuit-structure, FSM, functional and error-based." | Full text not retrieved (Xplore, ResearchGate, academia.edu all refused); only the abstract was read. | Cite the paper for its abstract's three roles of a metric; do not list its taxonomy. |
| "Piziali defines implicit versus explicit coverage." | Book text not read; Chapter 2's note asserted it from a table of contents that was not fetched then either. | Attribute the implicit/explicit split to the UVM 1.2 User's Guide §4.10.1, which was read; cite Piziali as the book-length treatment. |
| "Certitude reports N% of testbenches have undetected faults." | Vendor page carries no figures; Hampton 2009 EDN gives only the "over 50% of effort" claim, unrelated to detection. | Print no Certitude figure. |
| Huang et al. 2015 detection rates | Full text returned 403 from Hindawi and Wiley. | Cite the abstract's claim of "effectiveness in improving testbench quality" only. |
| "Vendor X's simulator reads and writes UCIS." | Not verified this run. | Name FC4SC and pyucis as the open writer and reader; say vendor support "is advertised" only if a vendor page is later read. |
| OpenTitan V2 coverage gate is 80% | The UNR section says "the 80% needed for V2"; the development-stages page and checklist say 90%. Internal inconsistency in the source. | Print 90% and cite the checklist; footnote the discrepancy if the UNR passage is quoted. |
| `urg -grade index` ranks tests by marginal coverage contribution | Vendor flag semantics not publicly documented. | Describe ranking as a concept (UCIS use case) and say OpenTitan asks its tool for a graded test list, without explaining the algorithm. |
| Verification Academy Coverage Cookbook definitions of code coverage kinds | Body behind login; only tags and one intro sentence visible. | Use OpenTitan's definitions; cite the cookbook only for the visible sentence "No single metric is sufficient". |
| FC4SC feature-comparison PDF contents | Not read. | Say the comparison exists in `docs/`; quote nothing from it. |

### Key sources

Existing keys reused unchanged: `ucis2012`, `opentitan-dv-methodology`,
`opentitan-checklist`, `opentitan-dev-stages`, `opentitan-testplanner`,
`opentitan-dvsim-tool-cfgs`, `dvsim-repo`, `lowrisc-dv-style`,
`accellera2015uvmug`, `uvm-core`, `piziali2004coverage`,
`tasiran2001coverage`, `bergeron2003testbenches`, `bergeron2005vmm`,
`hampton2007certitude`, `inozemtseva2014coverage`, `foster2020wrg`,
`va-coverage-cookbook`, `opentitan-uart-testplan`,
`opentitan-hmac-testplan`. Suggested additions or amendments:

```bibtex
@inproceedings{fine2003cdg,
  author    = {Shai Fine and Avi Ziv},
  title     = {Coverage Directed Test Generation for Functional Verification using {Bayesian} Networks},
  booktitle = {Proceedings of the 40th Design Automation Conference (DAC 2003)},
  publisher = {ACM},
  year      = {2003},
  pages     = {286--291},
  doi       = {10.1145/775832.775907},
  note      = {Metadata and abstract from OpenAlex; text not consulted. Accessed 2026-09-26}
}
@article{ioannides2012cdg,
  author  = {Charalambos Ioannides and Kerstin I. Eder},
  title   = {Coverage-Directed Test Generation Automated by Machine Learning -- A Review},
  journal = {ACM Transactions on Design Automation of Electronic Systems},
  volume  = {17},
  number  = {1},
  pages   = {7:1--7:21},
  year    = {2012},
  doi     = {10.1145/2071356.2071363},
  note    = {Metadata and abstract from Crossref and OpenAlex; text not consulted. Accessed 2026-09-26}
}
@article{huang2015mutation,
  author  = {Kai Huang and Peng Cheng Zhu and Rongjie Yan and Xiaolang Yan},
  title   = {Functional Testbench Qualification by Mutation Analysis},
  journal = {VLSI Design},
  volume  = {2015},
  pages   = {256474},
  year    = {2015},
  doi     = {10.1155/2015/256474},
  note    = {Open access (CC BY). Abstract read via OpenAlex; full text returned 403. Accessed 2026-09-26}
}
@misc{hampton2009fq,
  author       = {Mark Hampton},
  title        = {Functional qualification: a technical brief},
  howpublished = {EDN},
  year         = {2009},
  url          = {https://www.edn.com/functional-qualification-a-technical-brief/},
  note         = {Author was CTO of Certess, the tool's vendor; vendor source. Dated 2009-03-02. Accessed 2026-09-26}
}
@misc{synopsys-certitude,
  author       = {{Synopsys}},
  title        = {Testbench Quality Assurance ({Certitude})},
  howpublished = {Synopsys product page},
  year         = {2026},
  url          = {https://www.synopsys.com/verification/simulation/certitude.html},
  note         = {Vendor claim; no figures on the page. Accessed 2026-09-26}
}
@misc{uvm-core-subscriber,
  author       = {{Accellera Systems Initiative}},
  title        = {{UVM} core library: \texttt{uvm\_subscriber} (\texttt{src/comps/uvm\_subscriber.svh})},
  howpublished = {GitHub, accellera-official/uvm-core},
  year         = {2026},
  url          = {https://github.com/accellera-official/uvm-core/blob/main/src/comps/uvm_subscriber.svh},
  note         = {Tags write() as IEEE 1800.2-2020 13.9.3.2. Accessed 2026-09-26}
}
@misc{cocotb-coverage,
  author       = {Marek Cieplucha},
  title        = {cocotb-coverage: Functional Coverage and Constrained Randomization Extensions for cocotb},
  howpublished = {GitHub, mciepluc/cocotb-coverage; docs at https://cocotb-coverage.readthedocs.io/},
  year         = {2025},
  url          = {https://github.com/mciepluc/cocotb-coverage},
  note         = {BSD-2-Clause. Release 2.0, 2025-10-03; requires cocotb >= 2.0 and Python >= 3.11. Exports XML and YAML in its own schema; UCIS listed as planned. Accessed 2026-09-26}
}
@misc{fc4sc,
  author       = {{Accellera Systems Initiative, SystemC Verification Working Group}},
  title        = {{FC4SC}: Functional Coverage for {SystemC}},
  howpublished = {GitHub, accellera-official/fc4sc},
  year         = {2023},
  url          = {https://github.com/accellera-official/fc4sc},
  note         = {Apache-2.0; header-only C++11; writes UCIS XML. Origin: AMIQ Consulting, announced 2018-02-22 (https://www.consulting.amiq.com/2018/02/22/cpp-implementation-of-functional-coverage-for-systemc/); original repository https://github.com/amiq-consulting/fc4sc. Last push 2023-07-12. Accessed 2026-09-26}
}
@misc{pyucis,
  author       = {Matthew Ballance and contributors},
  title        = {pyucis: {Python} {API} to the Unified Coverage Interoperability Standard ({UCIS}) data model},
  howpublished = {GitHub, fvutils/pyucis},
  year         = {2026},
  url          = {https://github.com/fvutils/pyucis},
  note         = {Apache-2.0. Reads/writes UCIS XML, YAML and binary; imports Verilator, cocotb-coverage and AVL coverage. Author name from the repository's build badge (dev.azure.com/mballance); verify before print. Last push 2026-08-31. Accessed 2026-09-26}
}
@misc{opentitan-cov-cfg,
  author       = {{lowRISC contributors (OpenTitan project)}},
  title        = {{OpenTitan} coverage configuration and exclusion files},
  howpublished = {GitHub, lowRISC/opentitan},
  year         = {2026},
  url          = {https://github.com/lowRISC/opentitan/blob/master/hw/dv/tools/vcs/cover.cfg},
  note         = {Also hw/dv/tools/vcs/common\_cov\_excl.cfg, hw/ip/uart/dv/cov/uart\_cov\_excl.el, hw/dv/tools/xcelium/cov\_merge.tcl. Apache-2.0. Accessed 2026-09-26}
}
```

Amendment to `piziali2004coverage`: add `address = {Boston, MA}`,
`isbn = {978-1-4020-8025-8}` (Kluwer hardcover, June 2004 per Open
Library; Crossref lists the 2007 Springer softcover 978-0-387-73992-2)
and `note = {Text not consulted; metadata from Crossref and Open Library}`.
Amendment to `tasiran2001coverage`: add `volume = {18}`, `number =
{4}`, `pages = {36--45}`.
Amendment to `dvsim-repo` note: add `src/dvsim/job/deploy.py (CovMerge,
CovReport, CovUnr; failed-run coverage deleted in RunTest.post_finish)`.

### Confidence notes

- **High.** Everything quoted from OpenTitan (methodology README,
  checklist, development stages, `cover.cfg`, `common_cov_excl.cfg`,
  `uart_cov_excl.el`, `vcs.hjson`, `xcelium.hjson`, `cov_merge.tcl`,
  the HMAC and UART testplans), from `dvsim` (`deploy.py`,
  `testplanner.md`), from the lowRISC DV style guide, from the UCIS 1.0
  PDF, from the UVM 1.2 User's Guide PDF, from `uvm_subscriber.svh`,
  and from the cocotb-coverage, FC4SC and pyucis repositories was read
  in the source file on 2026-09-26.
- **Medium.** Fine and Ziv 2003, Ioannides and Eder 2012, Huang et al.
  2015, Hampton and Petithomme 2007, Tasiran and Keutzer 2001: metadata
  and abstracts verified through Crossref and OpenAlex; bodies not read.
  Hampton's 2009 EDN article was read through the fetch tool's summary,
  with the three-condition quotations returned verbatim; a second
  reader should open the page before print.
- **Low.** Piziali 2004, Bergeron 2003 and the VMM chapter: metadata
  only. The cocotb-coverage introduction page was read through the
  fetch tool's summary, but every statement about its API was checked
  against `coverage.py` directly. Verification Academy cookbook pages
  are login-walled; nothing from them beyond the visible intro sentence
  is used.
- **Not attempted.** Vendor coverage-tool documentation (urg, IMC,
  Questa coverage) was not fetched; every vendor flag in this note is
  quoted from OpenTitan's configuration files and labelled as
  tool-specific. Part C measures what Verilator and Icarus actually do.

---

# Part C — What the open tools do with functional coverage, measured, and the free alternatives

Scope: for every functional-coverage construct Chapter 8 teaches —
`covergroup` with a clocking event and with `sample()`, embedded in a
class, with `ref` and `with function sample` arguments, `coverpoint`
with auto bins, explicit value and range bins, array bins, transition
bins, `wildcard bins`, `ignore_bins`, `illegal_bins`, `default`, `bins
… with`, `cross` with `binsof`/`intersect`, `iff`, the `option.*`
fields, `get_coverage()`, `get_inst_coverage()`, `start()`/`stop()` and
`$get_coverage` — what Verilator 5.052 and Icarus Verilog 13.0 compile,
run and *print as a percentage*. Then Verilator's own coverage machinery
(line, toggle, expression, FSM, `cover property`), the `.dat` file and
`verilator_coverage`, measured end to end on the book's counter. Then
two free alternatives for what the simulators refuse: `cocotb-coverage`
(Python, in a `pip` venv beside the `dvbook` cocotb) and FC4SC (C++,
header-only, driven from a Verilator harness). Documented and measured
evidence are kept apart: documented support is quoted from the tools'
own files with a dated URL; measured support is cited as "measured,
this note, <tool> <version>, <flags>". §4 records where they disagree.

The runner is an unmodified copy of
`examples/ch07-constrained-random/support-matrix/matrix.py` with one
change, `--coverage` appended to the Verilator flag list (and, for a
second column, no coverage flag at all), so every verdict is the book's:
**runs** — compiled, ran, and printed `PROBE <id> PASS` after checking
the percentage `get_inst_coverage()` (or `get_coverage()`, or
`$get_coverage`) returned against the value a known sample set must
produce; **wrong** — ran to `$finish` but the percentage was not what
IEEE 1800 requires; **no run** — compiled but failed at run time; **no
build** — did not compile, first error kept.

#### Tool versions for every measurement

| Tool | Version string, as printed | Where |
|---|---|---|
| Verilator | `Verilator 5.052 2026-09-05 rev vUNKNOWN-built20260905` | `/opt/homebrew/bin/verilator`, `/opt/homebrew/bin/verilator_coverage` |
| Icarus Verilog | `Icarus Verilog version 13.0 (stable) (v13_0)` | `/opt/homebrew/bin/iverilog`, `/opt/homebrew/bin/vvp` |
| z3 (on PATH since the Ch. 7 decision) | `Z3 version 5.1.0 - 64 bit` | `/opt/homebrew/bin/z3` (not used by any coverage probe) |
| cocotb in `dvbook` | `2.1.0`, Python `3.12.14` | `conda run -n dvbook` |
| C++ | Apple `clang++` at `/usr/bin/clang++` (`g++` is the same binary) | for FC4SC and the Verilator harness |

`lcov` and `genhtml` are **not** installed (`which lcov genhtml` → not
found, 2026-09-26), so `--write-info` output is inspected as text, not
rendered.

#### The findings that decide the chapter

1. **Verilator 5.052 compiles and runs covergroups; Icarus 13.0 refuses
   the keyword.** Covergroup support landed in 5.050 (2026-07-01) as
   "Support covergroups, coverpoints, and bins (#784) (#7117) (#7728)"
   and was extended in 5.052 [Verilator Changes, local copy at
   `/opt/homebrew/Cellar/verilator/5.052/Changes`, read 2026-09-26; same
   text at the tag](https://github.com/verilator/verilator/blob/v5.052/Changes).
   Of the 35 constructs probed, 17 run on Verilator with the right
   percentage, 9 run and print a wrong percentage, and 9 do not build;
   on Icarus all 35 are a `syntax error` at the `covergroup` keyword
   (measured, this note, Verilator 5.052 `--coverage`, Icarus 13.0
   `-g2012`). **The flag makes no difference to covergroups:** the same
   35 verdicts were obtained with `--coverage`, with `--coverage-user`
   only, and with no coverage flag at all (three runs of the same
   runner, §1.3). What `--coverage` changes is whether the bins are
   also written to `coverage.dat` (§3).
2. **Thirteen constructs run and print a wrong percentage; eight of
   them are silent, and one of the eight is structural.**
   `get_inst_coverage()` on a covergroup returns the ratio of bins hit
   to bins defined across all its coverpoints and crosses, not the
   standard's average of per-item percentages: two coverpoints at 25%
   and 100% report 50%, not 62.5% (x07). Every probe with a single
   coverpoint therefore passes and every probe with two or more items
   of unequal size is wrong, with no warning. The other seven silent
   ones: ignored values stay in the denominator (c12, x08),
   `option.at_least` at the covergroup level is dropped (c24),
   `get_coverage()` returns 0.0 (c26), `stop()` is dropped (c28, x16),
   enum auto bins are one per bit pattern rather than one per literal
   (c30), the two-argument `get_inst_coverage(ref, ref)` leaves both
   outputs at 0 (c34), and the unsized literal `'1` as a bin value
   matches 1 rather than all-ones (x10). Five more are wrong but
   warned with `COVERIGN` at build time, which the book's `-Wall`
   turns into a build error: sized array bins (c09), `bins … with`
   (c15), `option.weight` (c22), `binsof` user bins on a cross (x02)
   and a cross of bare variables (x05). §2 is the catalog.
3. **What does not build is the cross-and-method layer.** A coverpoint
   or cross cannot be reached as a member of the instance
   (`g.cp.get_inst_coverage()` → `Member 'cp' not found in covergroup
   'cg'`), `$get_coverage` is an `UNSUPPORTED` reserved word, a
   range-to-range transition bin is an internal compiler error, and a
   transition repetition is `Transition set without items`. Crosses
   themselves work — auto cross bins, `iff` on a cross, crosses of
   auto-bin coverpoints — when judged through the group's own
   percentage; `binsof` user bins and a cross of bare variables are
   silently replaced by, or dropped from, the auto cross (x02, x05).
4. **Verilator's own coverage is complete end to end and prints what
   the manual says**, on the counter: line, toggle, branch, expression
   and `cover property` counts in one `.dat`, a summary and hierarchy
   report, an annotated source listing, a two-run merge that sums
   counts, a test ranking, and an lcov `.info` export — with two
   surprises for the chapter: the default annotation threshold is 10
   hits, so a design that passed its test shows 14% of lines "covered"
   until `--annotate-min 1` is given, and under `--binary` the line
   and expression records of Verilator's own `verilated_std.sv`
   (semaphore and process classes) land in every `.dat` with zero hits
   and drag the line summary of a class-based testbench to 13.6% (§3).
5. **Both free alternatives for Icarus work, one unpatched and one
   with a one-line patch.** `cocotb-coverage` 2.0 installs with `pip`
   into a venv built on the `dvbook` interpreter, sees `dvbook`'s
   cocotb 2.1.0, and a `CoverPoint`/`CoverCross` test on the counter
   passes under both Icarus and Verilator with XML and YAML exports
   (§5.1). FC4SC does not compile with the book's C++ toolchain
   because one line uses the libstdc++ internal `std::__not_`, which
   Apple's libc++ does not have; with that line replaced in a scratch
   copy, a covergroup with two coverpoints and a cross, sampled from
   `main()` around `eval()` on the Verilated counter, builds under
   `-std=c++17`, prints the expected percentages and writes UCIS XML
   (§5.2). The library's last commit is from 2021-01-15.

#### 1. The support matrices

###### 1.1 How to read them

Each probe is one file under `ch08-probes/probes/` (main set) or
`ch08-extra/probes/` (second set) in the session scratchpad, one
construct each, a `module top` that samples a known sequence of values
and checks the percentage `get_inst_coverage()` (or `get_coverage()`,
or `$get_coverage`) returns against the value the language requires,
printing `PROBE <id> PASS` only if it matches to within 0.01. So
**runs** means the percentage was right, not merely that the process
exited 0. **wrong** means the process ran to `$finish` and printed a
different percentage; §2 gives every printed value. **no run** means it
compiled and stopped before printing a verdict (only x06, the illegal
bin, which is the correct behavior). **no build** keeps the first error
line the runner extracted. Row ids are the probe file prefixes.

The expected values are the note's own arithmetic from the definitions
in IEEE 1800: auto bins one per value up to `auto_bin_max`, a
covergroup's coverage the average of its items' coverage weighted by
`option.weight`, ignored and illegal values excluded from the
denominator, a `default` bin excluded from the percentage. The
standard's text was not read in this session; the reading is recorded
in the unsourced-claims table.

###### 1.2 Main matrix: 35 constructs, Icarus 13.0 and Verilator 5.052 with `--coverage`

| id | Construct | Icarus 13.0 | Verilator 5.052, `--coverage` |
|---|---|---|---|
| c01 | `covergroup` sampled by a clocking event `@(posedge clk)` | no build — syntax error | runs |
| c02 | `covergroup` with explicit `sample()` | no build — syntax error | runs |
| c03 | `covergroup` embedded in a class, sampling members | no build — syntax error | runs |
| c04 | `covergroup` with a `ref` formal argument, two instances | no build — syntax error | runs |
| c05 | `covergroup … with function sample(args)` | no build — syntax error | runs |
| c06 | explicit value bins `bins lo = {0, 1}` | no build — syntax error | runs |
| c07 | range bins with `$`: `{[0:3]}`, `{[12:$]}` | no build — syntax error | runs |
| c08 | array bins `bins b[] = {[0:3]}` | no build — syntax error | runs |
| c09 | sized array bins `bins b[2] = {[0:7]}` | no build — syntax error | wrong (25.00 for 50.00) |
| c10 | transition bins `(0 => 1)`, `(0 => 1 => 3)` | no build — syntax error | runs |
| c11 | `wildcard bins hi = {2'b1?}` | no build — syntax error | runs |
| c12 | `ignore_bins` on an array of bins | no build — syntax error | wrong (75.00 for 100.00) |
| c13 | `illegal_bins` declared, not hit | no build — syntax error | runs |
| c14 | `bins rest = default` | no build — syntax error | runs |
| c15 | `bins ev[] = {[0:7]} with (item % 2 == 0)` | no build — syntax error | wrong (100.00 for 50.00) |
| c16 | `cross` of two coverpoints, read as `g.ab.get_inst_coverage()` | no build — syntax error | no build — Member 'ab' not found in covergroup 'cg' |
| c17 | `cross` with `binsof … intersect` user bins, read as member | no build — syntax error | no build — Member 'ab' not found in covergroup 'cg' |
| c18 | `ignore_bins` on a `cross` via `binsof`, read as member | no build — syntax error | no build — Member 'ab' not found in covergroup 'cg' |
| c19 | `iff` guard on a coverpoint | no build — syntax error | runs |
| c20 | `iff` guard on a cross, read as member | no build — syntax error | no build — Member 'ab' not found in covergroup 'cg' |
| c21 | `option.per_instance` with two instances | no build — syntax error | runs |
| c22 | `option.weight` on coverpoints | no build — syntax error | wrong (75.00 for 62.50) |
| c23 | `option.goal` | no build — syntax error | runs |
| c24 | `option.at_least` at the covergroup level | no build — syntax error | wrong (50.00 for 25.00) |
| c25 | `option.auto_bin_max` at the covergroup level | no build — syntax error | runs |
| c26 | `get_coverage()` (type-level, two instances) | no build — syntax error | wrong (0.00 for 75.00) |
| c27 | `get_inst_coverage()` on a coverpoint, `g.cp.get_inst_coverage()` | no build — syntax error | no build — Member 'cp' not found in covergroup 'cg' |
| c28 | `stop()` / `start()` | no build — syntax error | wrong (50.00 for 25.00) |
| c29 | `$get_coverage` | no build — syntax error | no build — Unsupported: IEEE 1800-2005 reserved word not implemented: '$get_coverage' |
| c30 | enum coverpoint, auto bins per literal (3 literals, 2 bits) | no build — syntax error | wrong (25.00 for 33.33) |
| c31 | `cross` of two auto-bin coverpoints, read as member | no build — syntax error | no build — Member 'ab' not found in covergroup 'cg' |
| c32 | `cross` of bare variables, read as member | no build — syntax error | no build — Member 'ab' not found in covergroup 'cg' |
| c33 | range-to-range transition bin `([0:1] => [2:3])` | no build — syntax error | no build — Internal Error: ../V3Ast.cpp:483: Null item passed to setOp1p |
| c34 | two-argument `get_inst_coverage(ref, ref)` | no build — syntax error | wrong (50.00, covered=0 total=0, for 50.00, 2, 4) |
| c35 | `option.name` | no build — syntax error | runs |

: Measured, this note, 2026-09-26; 35 probes, the book's runner with
`--coverage` appended. 0 run on both, 17 on Verilator only, 0 on Icarus
only, 18 on neither. The Icarus column is one message: `syntax error` /
`error: Invalid module item.` at the line of the `covergroup` keyword.
The Verilator column was identical in the `--coverage-user` run and in
the run with no coverage flag (§1.3).

###### 1.3 Second set: crosses judged through the group, and discriminating probes

The seven `no build` rows above that read a coverpoint or cross as a
member of the instance say nothing about whether the cross itself
works. These probes ask the same questions through the covergroup's
own `get_inst_coverage()`, and add cases that separate one hypothesis
from another.

| id | Construct | Icarus 13.0 | Verilator 5.052, `--coverage` |
|---|---|---|---|
| x01 | cross, auto cross bins, judged through the group | no build — syntax error | wrong (75.00 for 83.33) |
| x02 | cross with `binsof … intersect` user bins, judged through the group | no build — syntax error | wrong (62.50 for 66.67) |
| x03 | `iff` on a cross, judged through the group | no build — syntax error | wrong (62.50 for 75.00) |
| x04 | cross of two auto-bin coverpoints, judged through the group | no build — syntax error | wrong (12.50 for 18.75) |
| x05 | cross of bare variables, judged through the group | no build — syntax error | wrong (100.00 for 83.33) |
| x06 | `illegal_bins` value sampled | no build — syntax error | no run — `%Error: … Assertion failed in top.cg.sample: Illegal bin 'il' hit in coverpoint 'cp'`, then `$stop` (correct) |
| x07 | two coverpoints of 4 and 2 bins, judged through the group | no build — syntax error | wrong (50.00 for 62.50) |
| x08 | `ignore_bins` covering a whole named bin | no build — syntax error | wrong (50.00 for 100.00) |
| x09 | `option.at_least` at the coverpoint | no build — syntax error | runs |
| x10 | bin value `'1` on an 8-bit coverpoint | no build — syntax error | wrong (0.00 for 50.00) |
| x11 | `option.auto_bin_max` at the coverpoint | no build — syntax error | runs |
| x12 | transition repetition `(0 [*2])` | no build — syntax error | no build — Transition set without items |
| x13 | `option.weight`, expected 62.5 (c22 re-stated) | no build — syntax error | wrong (75.00) |
| x14 | `bins b[2] = {[0:7]}` after one sample | no build — syntax error | wrong (12.50 for 50.00) |
| x15 | enum with 4 literals on 2 bits (control for c30) | no build — syntax error | runs (25.00 either way) |
| x16 | `stop()` before every sample | no build — syntax error | wrong (50.00 for 0.00) |

: Measured, this note, 2026-09-26; 16 probes, same runner and flags.
3 run on Verilator only, 13 on neither.

**Reading x01–x05 and x07 together.** Verilator's group percentage is
`100 × Σ covered / Σ total` over the items' bins; the generated
`get_inst_coverage` sums each item's `coverageParts(covered, total)`
and divides once (read from the generated
`Vtop_top__03a__03acg__Vclpkg__0.cpp` of x07 and from
`coverageParts` in the shipped `verilated_covergroup.h`; measured,
this note). Under that formula the printed values decode exactly:

| id | bins hit / bins defined per item | Verilator's ratio | Standard's average |
|---|---|---|---|
| x07 | cp 1/4, cw 2/2 | 3/6 = 50.00 | (25 + 100)/2 = 62.50 |
| x01 | ca 2/2, cb 2/2, cross 2/4 | 6/8 = 75.00 | (100 + 100 + 50)/3 = 83.33 |
| x03 | ca 2/2, cb 2/2, cross 1/4 (iff honored) | 5/8 = 62.50 | 75.00 |
| x04 | ca 1/4, cb 1/4, cross 1/16 | 3/24 = 12.50 | 18.75 |
| x02 | ca 1/2, cb 2/2, auto cross 2/4 (user bins ignored) | 5/8 = 62.50 | 66.67 with the two user bins |
| x05 | no items at all: the `.dat` has no covergroup record for `cg` | 0/0 → 100.00 by the `total == 0` rule | 83.33 |

So the cross machinery is right in x01, x03 and x04 — auto cross bins,
`iff` on a cross, and a cross over auto-bin coverpoints all count the
bins the standard says (the x01 `.dat` lists `cg.ab.a0_x_b0 1`,
`a0_x_b1 0`, `a1_x_b0 0`, `a1_x_b1 1`) — and only the group formula is
off. In x02 the `binsof` bins are replaced by the auto cross, and in
x05 the cross of bare variables, and the implicit coverpoints it would
create, are dropped altogether, leaving an empty group that reports
100%.

###### 1.4 Headline

- **Runs on both:** nothing. Icarus has no covergroups (§4.3).
- **Runs on Verilator, right percentage:** the covergroup forms —
  clocking event, explicit `sample()`, embedded in a class, `ref`
  arguments, `with function sample` (c01–c05); value, range, `$`,
  unsized array, transition, wildcard and `default` bins (c06–c08,
  c10, c11, c14); `illegal_bins` declared and, when hit, a loud `$stop`
  (c13, x06); `iff` on a coverpoint (c19); `option.per_instance`,
  `option.goal`, `option.name`, and `option.at_least` and
  `option.auto_bin_max` at the coverpoint level (c21, c23, c25, c35,
  x09, x11); `get_inst_coverage()` on a group of one coverpoint.
- **Runs on Verilator, wrong percentage, silent:** any group of two or
  more items of unequal bin count (x07, x01, x03, x04); `ignore_bins`
  (c12, x08); covergroup-level `option.at_least` (c24);
  `get_coverage()` (c26); `stop()` (c28, x16); enum auto bins (c30);
  two-argument `get_inst_coverage` (c34); bin value `'1` (x10).
- **Runs on Verilator, wrong percentage, warned at build (a build
  error under the book's `-Wall` without `-Wno-fatal`):** sized array
  bins (c09, x14), `bins … with` (c15), `option.weight` (c22, x13),
  `binsof` user bins on a cross (x02), a cross of bare variables (x05).
- **Builds on neither:** member access to a coverpoint or cross of an
  instance (c16–c18, c20, c27, c31, c32), `$get_coverage` (c29),
  range-to-range transition bins (c33, an internal error), transition
  repetition (x12).

#### 2. Catalog of silent wrong results

A silent wrong result is a cell where the tool builds with no
`COVERIGN` or other coverage warning, runs to `$finish`, exits 0,
prints no run-time message, and prints a percentage the language does
not permit. Cells that are wrong but *warned at build time* are listed
in §2.9 so the chapter can tell the two apart: under the book's `-Wall`
without `-Wno-fatal`, a `COVERIGN` warning is a build error, so a
shipped example cannot reach those wrong runs; the silent ones it can.
All rows measured, this note, Verilator 5.052, `--coverage`, and
identical without it. Count: **eight silent constructs, five warned.**

###### 2.1 A covergroup's percentage is the bins ratio, not the average of its items — silent, structural

**Cells.** x07, x01, x03, x04 (and every group of two or more items
whose bin counts differ). **Printed.** x07 `group=50.00` for a 4-bin
coverpoint at 1/4 and a 2-bin coverpoint at 2/2; x01 `group=75.00`;
x03 `group=62.50`; x04 `group=12.50`. **Why.** The generated
`get_inst_coverage` accumulates `covered` and `total` over all items
and returns `100.0 * covered / total`, or `100.0` when `total` is zero
(read from the generated C++ of x07, §1.3). IEEE 1800 defines a
covergroup instance's coverage as the weighted average of its
coverpoints' and crosses' coverage (this note's reading of 19.11;
unsourced-claims table). **No warning.** The roadmap issue does not
list this as a known gap (§4.2). **Why it matters.** A coverage-driven
"stop when the group reaches 90%" loop, and every number in a
chapter table, is off whenever bins are unequal; a single-coverpoint
group is exactly right, which is why 17 rows pass. Note also that an
*empty* group (every item ignored) reports 100%.

###### 2.2 Ignored values stay in the denominator — silent

**Cells.** c12, x08. **Printed.** c12 `cov=75.00` where `bins b[] =
{[0:3]}; ignore_bins ig = {3};` was sampled with 0, 1, 2 (three of the
three remaining bins); x08 `cov=50.00` where `bins lo = {0,1}; bins hi
= {2,3}; ignore_bins ig = {2,3};` was sampled with 0. In both the
ignored values are not subtracted from the named bins. The `.dat`
file shows the arithmetic: c12 writes five records, `cg.cp.b[0]` to
`b[2]` with count 1, `b[3]` with count 0, and `cg.cp.ig` tagged
`bin_type ignore` with count 0; x08 writes `lo 1`, `hi 0`, `ig 0`. The
ignore bin exists as a bin of its own kind (`KIND_IGNORE` in
`verilated_covergroup.h`, "count only; never propagates to cross
coverage") but the values it names are not removed from `b[3]` or
`hi`, which stay normal bins in `total`. **Why it matters.**
The chapter's standard idiom for reserved encodings and unreachable
combinations produces a group that cannot reach 100%.

###### 2.3 `option.at_least` at the covergroup level is dropped — silent; at the coverpoint level it works

**Cells.** c24 (wrong, `cov=50.00` for 25.00) versus x09 (runs, 25.00).
The same option written inside the coverpoint braces takes effect;
written as `option.at_least = 2;` at covergroup scope it does not, and
nothing is printed. The runtime has a single `m_atLeast` per
coverpoint (`verilated_covergroup.h`, line 100) and the inheritance
from the enclosing group is what is missing. `option.auto_bin_max`
does inherit (c25 and x11 both run). **Why it matters.** UVM-style
covergroups set `option.at_least` once at group scope.

###### 2.4 `get_coverage()` returns 0.0 — silent, documented

**Cell.** c26. **Printed.** `cov=0.00` for two instances that together
hit 3 of 4 bins. The roadmap issue records "`cg_inst.get_coverage()` —
type-level (returns 0.0, no instance registry)" as not implemented
(FC-029) [Verilator #7560, updated 2026-08-17](https://github.com/verilator/verilator/issues/7560).
No warning at build or run time. **Why it matters.** `get_coverage()`
is the method a test's end-of-run check most often calls; on 5.052 it
must be `get_inst_coverage()`, and the chapter must say why.

###### 2.5 `stop()` is dropped — silent, documented as "parsed only"

**Cells.** c28 (`cov=50.00` for 25.00), x16 (`cov=50.00` for 0.00 with
`stop()` before every sample). Roadmap: "`start()` / `stop()` 🔲"
(parsed only, FC-027). No warning.

###### 2.6 Enum auto bins are one per bit pattern, not one per literal — silent

**Cells.** c30 (`cov=25.00` for 33.33: three literals on a 2-bit
base, one hit) with x15 as control (four literals on 2 bits, 25.00
either way, runs). The roadmap lists "Auto bins for enum type (one per
value) ✅"; the measurement says the bin count is 2^width (§4.2).
**Why it matters.** A state-machine coverpoint on a 3- or 5-state enum
can never reach 100%, and the extra bin is invisible unless the `.dat`
is read.

###### 2.7 Two-argument `get_inst_coverage(ref, ref)` leaves the outputs at 0 — silent

**Cell.** c34. **Printed.** `cov=50.00 covered=0 total=0`; the
percentage is right, the `ref` arguments are never written. The
generated wrapper (`__Vtcwrap_1_2`, §1.3) converts the two `int`s to
strings and calls a one-argument body. Roadmap FC-028 says ⬜ (not
implemented), but the call compiles and returns. No warning.

###### 2.8 The unsized literal `'1` as a bin value matches 1 — silent, fixed after 5.052

**Cell.** x10. **Printed.** `cov=0.00` after sampling `8'hff` into
`bins ones = {'1}`. The report against a 5.053 development build
gives the mechanism: bin values are widthed self-determined, so `'1`
stays one bit and is zero-extended [Verilator #8458, opened and closed
2026-09-23](https://github.com/verilator/verilator/issues/8458). Not in
5.052's `Changes`; a later release will carry the fix.

###### 2.9 Cells that are wrong but warned at build time

- **Sized array bins** (c09 `cov=25.00`, x14 `cov=12.50`):
  `%Warning-COVERIGN: … Unsupported: 'bins' explicit array size
  (treated as '[]')`, so `b[2] = {[0:7]}` becomes eight bins.
- **`bins … with`** (c15 `cov=100.00`): `%Warning-COVERIGN: …
  Unsupported: 'with' in cover bin (bin created without filter)`; the
  run then reports one bin, hit.
- **`option.weight`** (c22, x13 `cov=75.00` for 62.50):
  `%Warning-COVERIGN: … Ignoring unsupported coverage option:
  'weight'`, once per occurrence.
- **`binsof` user bins on a cross** (x02 `group=62.50`): four warnings,
  `Unsupported: 'binsof' in coverage select expression`, `…
  'intersect' …`, `… '&&' …`, and `Unsupported: explicit coverage
  cross bins`; the auto cross is counted instead.
- **Cross of bare variables** (x05 `group=100.00`):
  `%Warning-COVERIGN: … Unsupported: cross of 'a' which is not a
  coverpoint (implicit coverpoint)`; the cross contributes nothing and
  the group reads 100%.
- **Illegal bin hit** (x06) is *not* a wrong result: `[0] %Error:
  x06_illegal_hit.sv:3: Assertion failed in top.cg.sample: Illegal
  bin 'il' hit in coverpoint 'cp'`, then `%Error: … Verilog $stop`,
  `Aborting...`, non-zero exit. That is what the roadmap promises
  ("runtime `$error`+`$stop`") and what the chapter can show.

#### 3. Verilator's own coverage on the counter, end to end

All measured, this note, Verilator 5.052, on a copy of
`examples/appF-counter/rtl/counter.sv` with the book's `tb_counter.sv`
and a second testbench `tb_cov.sv` that takes `+n=<cycles>` and adds
two `cover property` statements. Flags: the book's `sv.mk` set
(`--binary --timing --timescale 1ns/1ps -Wall -Wno-DECLFILENAME
-Wno-UNUSEDSIGNAL -Wno-PROCASSINIT`) plus the coverage flag named.

###### 3.1 `--coverage` and the `.dat` file

`--coverage` is documented as the union of `--coverage-line
--coverage-toggle --coverage-expr --coverage-fsm --coverage-user`
[Verilator exe_verilator.rst, v5.052](https://github.com/verilator/verilator/blob/v5.052/docs/guide/exe_verilator.rst).
The build printed nothing beyond the normal report. The run printed
`PASS: counter reached 15 as expected` and wrote `coverage.dat` (6,014
bytes, 63 lines) into the current directory, with no message saying
so; the name is changed with `+verilator+coverage+file+<name>`
[Verilator exe_sim.rst, v5.052](https://github.com/verilator/verilator/blob/v5.052/docs/guide/exe_sim.rst).
The file begins `# SystemC::Coverage-3` and holds one line per point,
`C '<key>' <count>`, where the key packs file (`f`), line (`l`),
column (`n`), type (`t`: `toggle`, `line`, `branch`, `expr`, `user`,
`covergroup`), page (`page`: `v_toggle`, `v_line`, …), comment (`o`)
and hierarchy (`h`). Three lines verbatim:

```
C 'fcounter.svl10n28ttogglepagev_toggle/counterocount[7]:0->1htb_counter.dut' 0
C 'fcounter.svl14n10tbranchpagev_branch/counteroifS14htb_counter.dut' 15
C 'fcounter.svl13n9texprpagev_expr/countero(rst_n==0) => 1htb_counter.dut' 2
```

Toggle records are per bit and per direction (`0->1`, `1->0`
separately, added in 5.036 as "Add separate coverage counters for
toggles 0->1 and 1->0 (#6086)" [Verilator Changes, v5.052]); line
records list the statement lines a block covers (`S17-20,23-26,30`);
expression records are one per truth-table term.

###### 3.2 `verilator_coverage`: summary, hierarchy, annotate

`verilator_coverage coverage.dat` (no other argument) printed:

```
Coverage Summary:
  line      : 100.0% (11/11)
  toggle    : 54.5% (24/44)
  branch    : 66.7% ( 4/ 6)
  expr      : 100.0% ( 4/ 4)
  fsm_state : 0.0% ( 0/ 0)
  fsm_arc   : 0.0% ( 0/ 0)
```

`--report summary` printed the same; `--report hier` added a
per-instance roll-up (`tb_counter`, `tb_counter.dut`) and a "Design
Unit Coverage Summary" per module, in which `counter` is `line 100.0%
(2/2) toggle 54.5% (12/22) branch 100.0% (2/2) expr 100.0% (2/2)`. The
toggle figure is honest: after 15 enabled cycles `count[3]:1->0` and
`count[4..7]` in both directions never happened, and `rst_n:1->0` never
happens because the testbench asserts reset only at time zero.

`--annotate ann --annotate-all --annotate-points` wrote `ann/counter.sv`
and `ann/tb_counter.sv` and printed, after the summary, `Annotation
Summary: lines with all attached points covered : 14.00% (5/35)`. The
14% is not a contradiction of the 100% line figure above it: the
annotation threshold `--annotate-min` defaults to 10 hits
[Verilator exe_verilator_coverage.rst, v5.052](https://github.com/verilator/verilator/blob/v5.052/docs/guide/exe_verilator_coverage.rst),
and a 15-cycle test hits most points fewer than ten times. Verbatim
from `ann/counter.sv`:

```
 000020   always_ff @(posedge clk or negedge rst_n) begin
+000020  point: type=line comment=block hier=tb_counter.dut
~000018     if (!rst_n)   count <= '0;
-000002  point: type=line comment=elsif hier=tb_counter.dut
-000002  point: type=expr comment=(rst_n==0) => 1 hier=tb_counter.dut
+000018  point: type=expr comment=(rst_n==1) => 0 hier=tb_counter.dut
~000015     else if (en)  count <= count + 1'b1;
+000015  point: type=branch comment=if hier=tb_counter.dut
-000003  point: type=branch comment=else hier=tb_counter.dut
```

With `--annotate-min 1` on the merged data of §3.4 the same file reads
`92.00% (24/26)` with only `rst_n:1->0` below the line. Without
`--annotate-all`, the default writes only files with low coverage.
The chapter must set `--annotate-min` explicitly and say what it means.

###### 3.3 `cover property` under `--coverage-user`

`tb_cov.sv` declares `cov_counting: cover property (@(posedge clk)
en);` and `cov_wrap: cover property (@(posedge clk) count == 8'hff);`.
A first attempt wrote `rst_n && en` in the first property and the
build stopped with `%Warning-SYNCASYNCNET: tb_cov.sv:6:15: Signal
flopped as both synchronous and async: 'tb_cov.rst_n'`, pointing at
the async use in `counter.sv:13` and the "sync usage" in the property
— under `-Wall` a fatal error. A `cover property` that reads an
asynchronous reset therefore needs a `lint_off` or a different
expression; the chapter should know this before it writes one. With
`en` alone, `--coverage-user` built cleanly and the run with `+n=10
+verilator+coverage+file+user.dat` wrote exactly two records:

```
# SystemC::Coverage-3
C 'ftb_cov.svl15n17tuserpagev_user/tb_covocov_countinghtb_cov.cov_counting' 10
C 'ftb_cov.svl16n17tuserpagev_user/tb_covocov_wraphtb_cov.cov_wrap' 0
```

and `verilator_coverage user.dat` printed the six zero lines of §3.2
plus `user : 50.0% (1/2)`. The annotated file marks the unreached
property `%000000   cov_wrap: cover property (@(posedge clk) count ==
8'hff);` and its point `-000000  point: type=user comment=cov_wrap
hier=tb_cov.cov_wrap`. Note the count is the number of clock edges at
which the property held (10), not a 0/1.

###### 3.4 Two runs, merge, rank, lcov export

The full `--coverage` build of `tb_cov` was run twice: `+n=10` →
`runA.dat` (`count=10 after 10 enabled cycles`) and `+n=300` →
`runB.dat` (`count=44 after 300 enabled cycles`, the counter having
wrapped once). Summaries: A `toggle 54.5% (24/44) … user 50.0% (1/2)`;
B `toggle 95.5% (42/44) … user 100.0% (2/2)`. Then:

- `verilator_coverage --write merged.dat runA.dat runB.dat` exited 0
  silently and wrote a 62-line file whose counts are the sums:
  `count[7]:0->1` is 0 in A, 1 in B, 1 in merged; `cov_counting` is
  10, 300, 310. `verilator_coverage merged.dat` printed `toggle 95.5%
  (42/44) … user 100.0% (2/2)`: the two toggles still missing are
  `rst_n:1->0` in `dut` and in the testbench.
- `--rank runA.dat runB.dat` printed a table, `Covered 40 / Rank 0 /
  RankPts 0` for `runA.dat` and `59 / 1 / 59` for `runB.dat`: run A
  adds nothing that run B does not already cover, so it ranks 0. The
  manual calls the report experimental.
- `--write-info merged.info runA.dat runB.dat` exited 0 and wrote an
  lcov file with `TN:verilator_coverage`, one `SF:` record per source
  file, `DA:<line>,<count>` for line hits, `BRDA:<line>,0,<name>,<count>`
  for every toggle, branch and expression point (so toggles appear as
  "branches" to lcov), and `BRF:27 / BRH:12` for `counter.sv`. The
  `cover property` lines appear only as `DA:15,310` and `DA:16,1`; the
  `user` type has no separate representation. `lcov` and `genhtml` are
  not installed, so the file was not rendered.
- `--filter-type user merged.dat` printed the summary with only the
  `user` line non-zero, as documented.

###### 3.5 Covergroup bins in the `.dat`, and the `verilated_std.sv` pollution

Re-running the c02 probe binary (built with `--coverage`) with
`+verilator+coverage+file+cg02.dat` wrote 47 records. Four are the
covergroup's bins:

```
C 'tcovergrouppagev_covergroup/cgf<path>/c02_explicit_sample.svl3n22binauto_0hcg.cp.auto_0' 1
C 'tcovergrouppagev_covergroup/cgf<path>/c02_explicit_sample.svl3n22binauto_1hcg.cp.auto_1' 1
C 'tcovergrouppagev_covergroup/cgf<path>/c02_explicit_sample.svl3n22binauto_2hcg.cp.auto_2' 0
C 'tcovergrouppagev_covergroup/cgf<path>/c02_explicit_sample.svl3n22binauto_3hcg.cp.auto_3' 0
```

and `verilator_coverage` printed `covergroup : 50.0% ( 2/ 4)` as a
seventh summary line, with the annotated source showing each bin as
`point: type=covergroup comment= hier=cg.cp.auto_0`. The hierarchy is
the covergroup *type* and coverpoint name, not the instance path, so
two instances of one covergroup would merge in the file (consistent
with the roadmap's "no instance registry"). Without `--coverage` (or
`--coverage-user`) the probe still runs and prints the right
percentage but writes no file: `get_inst_coverage()` is computed
in-model; the flag only controls the dump (§1's three identical runs;
the fix "Fix covergroups without --coverage (#7848)" in 5.050 is what
makes the flag-less build legal).

The other 43 records are the problem. Thirty-one of them are `line`,
`branch` and `expr` points inside
`/opt/homebrew/Cellar/verilator/5.052/share/verilator/include/verilated_std.sv`
(the `std::semaphore` and `std::process` classes Verilator links into
any `--binary --timing` model), all with count 0, and they drag the
probe's summary to `line : 13.6% (3/22)`, `branch : 12.5% (1/8)`,
`expr : 11.1% (1/9)`. The counter build of §3.1 did not show this
because its testbench uses no class or process features; a
class-based testbench (every Chapter 6 through 12 example) will. The
chapter's recipe needs either `--filter-type` on the report, a
`coverage_off` control-file entry for that path, or an explicit
statement that the summary counts Verilator's own package.

#### 4. Documented support, and where it disagrees with the measurement

###### 4.1 Verilator 5.052: what its own files say

- **Language manual.** The "Language Limitations" chapter has a
  `Coverage` section of two sentences: "Verilator partially supports
  SystemVerilog functional coverage with `covergroup`, `coverpoint`,
  bins, cross coverage, and transition bins. See Covergroup Coverage"
  [Verilator languages.rst, v5.052, read 2026-09-26](https://github.com/verilator/verilator/blob/v5.052/docs/guide/languages.rst).
  The `Assertions` section just above it says Verilator "partially
  supports assertions and assertion-driven functional coverage". The
  simulation chapter adds only "Verilator supports coverpoints with
  value and transition bins, and cross points"
  [Verilator simulating.rst, v5.052, "Covergroup Coverage"](https://github.com/verilator/verilator/blob/v5.052/docs/guide/simulating.rst).
  Nothing in the manual lists which options, methods or bin forms are
  in the "partially".
- **Flags.** `--coverage` = `--coverage-line --coverage-toggle
  --coverage-expr --coverage-fsm --coverage-user`; `--coverage-user`
  "Enables adding user-inserted functional covergroup coverage";
  `--coverage-underscore` covers signals starting with an underscore,
  which are otherwise skipped; `--coverage-max-width` defaults to 256
  bits for toggle coverage; `--coverage-per-instance` keeps per-instance
  counters instead of summing instances of a module
  [Verilator exe_verilator.rst, v5.052](https://github.com/verilator/verilator/blob/v5.052/docs/guide/exe_verilator.rst).
  Toggle coverage "makes a minimally-intelligent decision about what
  clock domain the signal goes to, and only looks for edges in that
  clock domain … coverage may be lower than what would be seen by
  looking at traces" [simulating.rst, "Toggle Coverage"]. Line
  coverage may over-count combinational blocks whose `UNOPTFLAT`
  warning was disabled [same, "Line Coverage"].
- **`verilator_coverage`.** `--annotate`, `--annotate-all`,
  `--annotate-min` (default 10), `--annotate-points`, `--filter-type`
  (`toggle`, `line`, `branch`, `expr`, `covergroup`, `user`,
  `fsm_state`, `fsm_arc`; "the `covergroup` type represents
  SystemVerilog functional coverage including covergroups,
  coverpoints, bins, and cross coverage as defined in IEEE 1800-2023
  Section 19"), `--rank` ("experimental"), `--report summary|hier`,
  `--write`, `--write-info` for `lcov` ("This format lacks the comments
  for cover points that the verilator_coverage format has")
  [Verilator exe_verilator_coverage.rst, v5.052](https://github.com/verilator/verilator/blob/v5.052/docs/guide/exe_verilator_coverage.rst).
- **The warning.** `COVERIGN`: "Warns that Verilator does not support
  certain forms of `covergroup`, `coverpoint`, and coverage options,
  and the construct was ignored … Ignoring this warning may make
  Verilator ignore lint checking on the construct, and collect
  coverage data differently from other simulators"
  [Verilator warnings.rst, v5.052](https://github.com/verilator/verilator/blob/v5.052/docs/guide/warnings.rst).
- **Since when** (all from the local `Changes`, read by line position
  under version headers; same text at the tag [Verilator Changes,
  v5.052](https://github.com/verilator/verilator/blob/v5.052/Changes)):
  5.050 (2026-07-01) "Support covergroups, coverpoints, and bins (#784)
  (#7117) (#7728)", "Support covergroup runtime model Phase A1
  (#7728)", "Support hierarchical reference cross members (#7749)
  (#7820)", "Add `--coverage-per-instance` (#7636)", "Add
  hierarchy-aware reporting to `verilator_coverage` (#7657)", "Fix
  covergroups without --coverage (#7848) (#7849)", "Fix `$` as
  unsupported coverpoint-bin range bounds (#7750) (#7825)"; 5.052
  (2026-09-05) "Support embedded covergroup member references (#7749)
  (#8015)", "Support embedded covergroup clocking events (#8028)",
  "Support class handle covergroup arguments (#8071)", "Support
  covergroup/function/task (ref/virtual/array) interface arguments
  (#8180)", "Support covergroup events with reference members or ref
  arguments (#8201)", "Fix internal error for coverpoints that
  reference a covergroup formal parameter (#7853 partial) (#7889)",
  "Fix --coverage on labeled inline assert/cover property (#7898)
  (#7904)", "Add FSM arc and state coverage to verilator_coverage
  .info output (#7972) (#7973)". Before that, covergroups were parsed
  and ignored: 5.040 "Fix COVERAGEIGN-ignored `get_inst_coverage` and
  other covergroup methods (#6383)", 5.038 "Support covergroup
  extends, etc., as unsupported (#6160)". Older machinery: "Create
  new --coverage-line and --coverage-user options" and "Add
  --coverage_toggle" are in the 3.x era; "New verilator_coverage
  program added" 3.850 (2013); "Support verilator_coverage
  --write-info for lcov HTML reports" 4.028 (2020); "Add
  --coverage-max-width (#2853)" 4.202 (2021); "Add expression coverage
  (#4677) (#5719)" 5.034 (2025); "Add `--coverage-fsm`" 5.048 (2026).
- **The tracker's own status table.** Issue #784 "Support covergroup"
  was opened 2014-06-10 and closed 2026-06-05 by PR #7117 "Baseline
  support for covergroups, coverpoints, and bins" [Verilator #784](https://github.com/verilator/verilator/issues/784);
  [Verilator PR #7117](https://github.com/verilator/verilator/pull/7117).
  The tracking issue "Covergroup Roadmap and Progress", open, last
  updated 2026-08-17, carries a per-feature table with a legend of
  "✅ supported · ⚠️ `COVERIGN` (silently ignored) · ❌ `UNSUPPORTED`
  (error) · 🔲 parsed only · ⬜ not implemented" and the notes "bin
  counts are currently 32-bit" and "Verilator caps the maximum bins to
  avoid hangs. Currently, it's hard-coded to 1000"
  [Verilator #7560](https://github.com/verilator/verilator/issues/7560).
  The one other open covergroup issue is "ensure covergroupRegistry is
  threadsafe" (#8221). Closed since the release: #8351 (crash widthing
  an option through a forward class), #8458 (`'1` bin value), #8461
  (embedded covergroup cannot call a method of its enclosing class),
  all 2026-09.

###### 4.2 Verilator: where documentation and measurement disagree

| Documented (source) | Measured (this note, 5.052) | Reading |
|---|---|---|
| "`cp.get_inst_coverage()` / `cr.get_inst_coverage()` ✅" (#7560) | `g.cp.get_inst_coverage()` → `Member 'cp' not found in covergroup 'cg'` (c27, c16–c18, c20, c31, c32) | member access through the instance is not the form the roadmap tested; the chapter must not use it |
| "`ref` formal arguments ⬜" (#7560, 2026-08-17) | runs, two instances on two variables (c04) | superseded by 5.052 "Support covergroup events with reference members or ref arguments (#8201)"; the roadmap table is stale here |
| "Auto cross bins when coverpoints use auto bins ⬜ FC-022" (#7560) | works, 1/16 counted (x04) | roadmap stale, or FC-022 means something narrower |
| "`iff` guard on cross ⚠️" (#7560) | honored (x03: 1/4, not 2/4), no warning | roadmap stale |
| "Auto bins for enum type (one per value) ✅" (#7560) | one per bit pattern: 4 bins for 3 literals (c30) | disagreement; a silent wrong result |
| "`option.at_least` ✅" (#7560, covergroup options table) | honored at coverpoint level (x09), dropped at covergroup level (c24) | half right; the table does not distinguish scopes |
| "Two-argument `get_inst_coverage(ref int, ref int)` ⬜" (#7560) | compiles, returns the percentage, leaves both `ref`s at 0 (c34) | "not implemented" would be better as a build error than a silent zero |
| "`ignore_bins` — values and transitions ✅" (#7560) | ignored values remain in named bins' denominators (c12, x08) | the ignore bin is created; the subtraction is not |
| Covergroup coverage as a percentage (implied by `get_inst_coverage()` returning a real) | bins ratio, not the IEEE 1800 weighted average of items (x07, x01, x03, x04) | not mentioned anywhere; the roadmap's FC-033 "Weighted coverage computation" is the nearest item |
| "`bins name = {...} with (expr)` ⚠️", "`binsof` ⚠️", "`wildcard bins` on transition lists ⚠️", "explicit array size" | all warn `COVERIGN` as promised (c15, x02, c09) | agrees |
| "Transition repetition operators ❌ UNSUPPORTED" (#7560) | `COVERIGN` warning then `%Error: … Transition set without items` (x12) | an error either way; the message is not the documented one |
| "Transition bins: two-value, multi-step, range-to-range ✅" (#7560) | two-value and multi-step run (c10); range-to-range is `Internal Error: ../V3Ast.cpp:483: Null item passed to setOp1p` after four `COVERIGN: Unsupported: covergroup value range '[...]'` (c33) | disagreement; a compiler crash, reportable |
| "`$get_coverage()` ⬜" (#7560) | `%Error-UNSUPPORTED: … IEEE 1800-2005 reserved word not implemented: '$get_coverage'` (c29) | agrees, loudly |
| `--coverage-user` "Enables adding user-inserted functional covergroup coverage" (exe_verilator.rst) | covergroups compute and print percentages with no coverage flag at all; the flag controls only the `.dat` dump | the doc describes the dump, not the language support |
| "Covergroup in a build without --coverage generates invalid C++" (#7848, closed 2026-06-29) | fixed: 35 of 35 probes build without the flag | agrees with the fix in 5.050 |
| `--annotate-min` default 10 (exe_verilator_coverage.rst) | a passing 15-cycle test annotates 14% of lines as covered | agrees; the chapter must set it |

###### 4.3 Icarus Verilog 13.0

The README says Icarus "compiles a (slowly growing) subset of the
SystemVerilog language" and that "The list of unsupported
SystemVerilog constructs is too large to enumerate here"
[iverilog README, v13-branch, read 2026-09-26](https://github.com/steveicarus/iverilog/blob/v13-branch/README.md);
it does not contain the words "coverage" or "covergroup". The tracker
has no issue with "covergroup" in its title (title search, 2026-09-26)
and two with "coverage": to "Is it possible to generate coverage
report in icarus verilog … ?" the maintainer answered "There is no
support for coverage analysis in Icarus Verilog" and moved the thread
to Discussions [iverilog #1232, comment of 2025-04-13](https://github.com/steveicarus/iverilog/issues/1232);
to a 2023 question on code coverage, "Icarus Verilog has no built-in
support for generating coverage statistics. `covered` is the only free
tool I know of for doing this. See 'Using Covered As a Vpi Module' in
the `covered` man page" [iverilog #911, comment of 2023-04-25](https://github.com/steveicarus/iverilog/issues/911).
Measurement agrees exactly: every probe fails at the `covergroup`
keyword with `syntax error` / `error: Invalid module item.`, and a
module that calls only `$get_coverage()` compiles and then fails at
`vvp` load with `Error: System task/function $get_coverage() is not
defined by any module.` / `Program not runnable, 1 errors.` (measured,
this note, Icarus 13.0, `-g2012`). The `covered` tool the maintainer
names was not evaluated here; its last release predates Icarus 12.

#### 5. The free alternatives, measured

###### 5.1 `cocotb-coverage` with the `dvbook` cocotb

- **What it is.** `cocotb-coverage` 2.0 on PyPI (uploaded 2025-10-03),
  `requires_python >=3.11`, `requires_dist` `cocotb>=2.0`,
  `python-constraint`, `pyyaml`, home page
  github.com/mciepluc/cocotb-coverage [PyPI JSON for cocotb-coverage,
  read 2026-09-26](https://pypi.org/project/cocotb-coverage/).
- **Install.** `conda run -n dvbook python -m venv --system-site-packages
  <scratchpad>/covvenv` then `covvenv/bin/pip install cocotb-coverage`.
  The venv sees `dvbook`'s cocotb 2.1.0 through the system site
  packages (printed `venv sees cocotb 2.1.0 from
  /opt/miniconda3/envs/dvbook/lib/python3.12/site-packages/cocotb/__init__.py`),
  so pip installed only `python-constraint 1.4.0` (built from source,
  no wheel for this platform) and `cocotb-coverage 2.0`; `PyYAML 6.0.3`
  was already present. Nothing was written to `dvbook` (measured, this
  note, 2026-09-26). `from cocotb_coverage.coverage import CoverPoint,
  CoverCross, coverage_db` imports.
- **Gotcha.** The venv has no `cocotb-config` of its own, because
  cocotb was satisfied from the parent; a bare `PATH` with the venv
  first picks up the *base* conda `cocotb-config` (Python 3.13), whose
  embedded interpreter cannot see the venv and fails with
  `ModuleNotFoundError: No module named 'cocotb_coverage'`. The
  working invocation is `PATH=/opt/miniconda3/envs/dvbook/bin:$PATH
  PYTHONPATH=<venv>/lib/python3.12/site-packages make`, i.e. `dvbook`'s
  cocotb with the venv's packages on the import path.
- **The test.** `test_counter_cov.py` decorates a `sample(en, count)`
  function with `@CoverPoint("top.en", bins=[0, 1])`, `@CoverPoint(
  "top.count_range", bins=[(0,3), (4,7), (8,15), (16,255)], rel=<range
  test>)` and `@CoverCross("top.en_x_count", items=[…])`, drives the
  counter for 10 enabled and 3 idle cycles sampling after each edge,
  then calls `coverage_db.report_coverage`, `export_to_xml` and
  `export_to_yaml`, and asserts the percentages. Under Icarus 13.0
  (`make SIM=icarus`, cocotb's own `Makefile.sim` with `-g2012`) it
  printed per-bin counts (`BIN (0, 3) : 3`, `BIN (16, 255) : 0`, …) and
  `top.en: 2/2 = 100.00%`, `top.count_range: 3/4 = 75.00%`,
  `top.en_x_count: 4/8 = 50.00%`, `TESTS=1 PASS=1 FAIL=0`. Under
  Verilator 5.052 (`make SIM=verilator`, `--timing -Wno-DECLFILENAME
  -Wno-UNUSEDSIGNAL`) the same three lines and `PASS=1`, with no
  Verilator warnings (measured, this note). `coverage.xml` begins
  `<top abs_name="top" size="14" coverage="9" cover_percentage="64.29">`
  with one element per point and `<bin0 bin="0" hits="3" …/>` children;
  `coverage.yml` is the same tree as a mapping. The `size="14"`
  top-level figure is the bins ratio (9 of 2 + 4 + 8), the same
  aggregate Verilator uses for a covergroup — worth one sentence in
  the chapter, since neither tool computes the IEEE average.
- **Verdict.** Works, on both simulators, with no change to the book's
  environment beyond a `pip install` into `dvbook` (one package plus
  `python-constraint`). It is the only way to show functional coverage
  on Icarus at all.

###### 5.2 FC4SC from a Verilator C++ harness

- **What it is.** "A header only C++11 library for functional
  coverage", Apache-2.0, 35 stars, default branch `master`, last push
  2022-10-05, last commit `15f1d59` dated 2021-01-15 [GitHub API for
  amiq-consulting/fc4sc, read 2026-09-26](https://github.com/amiq-consulting/fc4sc).
  `includes/` holds ten headers (`fc4sc.hpp` is the entry point);
  `docs/` holds a user guide and a feature-comparison PDF; `examples/fir`
  is a SystemC example compiled with `-std=c++11`; `tools/` holds a
  UCIS merge script and a report/GUI. There is no README at the
  repository root (raw fetch returned 404); the description is the
  GitHub blurb. The tracker's 28 items (issues and PRs) are 2018–2022;
  open ones concern the UCIS report scripts (#24, #27, #28).
- **Where it stopped, unmodified.** `verilator --cc --exe --build
  -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL --top-module counter
  -CFLAGS "-std=c++17 -I<fc4sc>/includes" counter.sv main.cpp` failed
  in the first compile of `main.cpp`:

  ```
  fc4sc_base.hpp:60:15: error: unknown template name '__not_'
     60 |   public std::__not_<std::is_convertible<first, forbidden>> {};
  fc4sc_bin.hpp:131:54: error: no member named 'value' in 'forbid_type<std::string, int>'
  3 errors generated.
  ```

  `std::__not_` is an internal helper of GNU libstdc++; Apple's
  `clang++` (the book's `/usr/bin/g++` is the same binary) uses libc++,
  which has no such name. The tracker has no report of it (searches
  for `__not_` and `clang`, 2026-09-26, the latter matching only two
  2018 PRs about the merge tool on Darwin). On a Linux host with
  libstdc++ the line would compile; the book's stated toolchain is the
  one that fails.
- **With a one-line patch** (scratch copy only): the line replaced by
  `public std::integral_constant<bool, !std::is_convertible<first,
  forbidden>::value> {};`. The same command then built with zero
  warnings, and `obj_fc/Vcounter` printed `en_cp=100.00
  count_cp=66.67 cross=66.67 group=55.56 (8/11)` and wrote
  `fc4sc_coverage.xml` (162 lines, `<ucis:UCIS …>` with
  `<ucis:coverpoint name="en_cp" …>`, `<ucis:coverpointBin name="off"
  …>`, 18 bin elements). The harness: a `counter_cg : public
  covergroup` with `CG_CONS`, two `COVERPOINT(int, …)` with
  `bin<int>("low", interval(0,3))`-style bins, a `cross<int,int>
  en_x_count = cross<int,int>(this, "en_x_count", &en_cp, &count_cp)`,
  and `main()` that toggles `clk`, calls `eval()` and then
  `cg.sample(dut->en, dut->count)` per cycle (measured, this note,
  Verilator 5.052, Apple clang, `-std=c++17`). The `high` count bin
  (16–255) and two cross bins are unreached after ten cycles, hence
  66.67 twice. The group's 55.56 is not the mean of its three items
  (77.78) nor the bins ratio it prints beside it (8/11 = 72.7); FC4SC's
  `get_inst_coverage` weights items by `option.weight` and the cross
  appears to contribute 0 to the average while reporting 66.67 on its
  own. Not investigated further; the chapter should not print FC4SC's
  group figure without checking the library's formula.
- **Verdict.** Header-only and driveable from a Verilator harness, but
  not with the book's toolchain as shipped: one libstdc++-only line
  stops the build on macOS/clang, the project has had no commit since
  January 2021, and its group percentage needs its own verification.
  A chapter example would have to vendor a patched copy, which the
  book's originality rule permits (Apache-2.0, attribution in the
  caption) but which is a maintenance burden the cocotb route does
  not carry.

#### 6. What this means for the chapter's examples

- **Icarus cannot run any functional-coverage listing.** The chapter's
  Icarus column is the same one message for every construct. The only
  functional coverage the book can show on Icarus is cocotb-coverage
  (§5.1), which is a Python testbench, not SystemVerilog.
- **On Verilator 5.052 the chapter can ship, as verified listings with
  the right percentages:** covergroups with a clocking event, explicit
  `sample()`, `with function sample`, embedded in a class, `ref`
  arguments; value, range, `$`, `bins b[]`, transition (`=>`,
  multi-step), `wildcard`, `default` bins; `illegal_bins` with the
  loud `$stop` when hit; `iff` on a coverpoint; `option.per_instance`,
  `option.goal`, `option.name`, `option.auto_bin_max` at either scope,
  `option.at_least` at the coverpoint; `get_inst_coverage()` on a
  group of **one** item, or of items with equal bin counts.
- **Constructs the chapter must teach from the standard and label
  "wrong on 5.052", with the mechanism:** the covergroup percentage
  itself for mixed groups (§2.1: show the `.dat` bins, compute by hand,
  and say which formula the tool uses); `ignore_bins` (§2.2);
  covergroup-level `option.at_least` (§2.3); `get_coverage()` (§2.4);
  `start()`/`stop()` (§2.5); enum auto bins (§2.6); the two-argument
  method (§2.7); `'1` as a bin value (§2.8, fixed after 5.052);
  `option.weight`, `bins … with`, sized `bins b[N]`, `binsof` cross
  bins, crosses of bare variables (§2.9, build errors under the
  book's flags); `$get_coverage`, member access `g.cp.…`, range-to-range
  transitions, repetition operators (no build). Each should cite the
  roadmap issue's FC number where one exists so the reader can check
  whether a later release closed it.
- **A cross example must be judged through the group** and must have
  coverpoints of equal size, or the group percentage will be wrong
  for the §2.1 reason: `ca` and `cb` of 2 bins each and a 4-bin cross
  gives 6/8 = 75 for the tool and 83.33 for the standard, so even
  x01's shape is unsafe as a printed number. The safe demonstration is
  to read the `.dat` bins (§3.5) rather than the percentage.
- **The `.dat`/`verilator_coverage` flow is solid and worth a full
  worked example on the counter:** two runs with different `+n`, a
  merge, `--rank`, `--annotate --annotate-min 1`, and the
  `--write-info` file shown as text. Three things to state: the file
  is written silently to the cwd, `--annotate-min` defaults to 10, and
  a class-based testbench pulls `verilated_std.sv` records into the
  summary (§3.5), so the chapter should filter or explain.
- **`cover property` works under `--coverage-user`** and counts edges,
  not hits; a property that reads an asynchronous reset trips
  `SYNCASYNCNET` under `-Wall` (§3.3).
- **The support-matrix example.** The 35 + 16 probes and their two
  `probes.txt` files are in the runner's format and were run by a copy
  of `matrix.py` whose only change is the coverage flag appended from
  an environment variable; they can become
  `examples/ch08-functional-coverage/support-matrix/` as Chapter 7's
  did. Two changes the shipped copy needs: the flag line (three lines),
  and, for the x rows, the caption. The runner's classification is
  already right for percentages because each probe prints its own
  verdict. The `matrix.py` copy also prints the "with z3" header
  because z3 is now on PATH; no coverage probe uses it.

#### Unsourced-claims table

| Claim | Status |
|---|---|
| A covergroup's coverage is the `option.weight`-weighted average of its coverpoints' and crosses' coverage (§1.1, §2.1, expected values of x01–x05, x07, c16, c22, c27) | This note's reading of IEEE 1800 19.11; the clause text was not consulted. `refs.bib` has `ieee1800-2023`. It is also what cocotb-coverage does *not* do (§5.1), so the chapter must verify before printing any group percentage as "the standard's". |
| Ignored and illegal values are excluded from the coverage denominator; a `default` bin is excluded from the percentage (c12, c13, c14, x08) | Reading of 19.5.2/19.5.3; not consulted. Verilator's `default` behavior matched it (c14 runs). |
| Auto bins for an enum are one per named literal (c30) | Reading of 19.5.1; not consulted. |
| `bins b[N] = {range}` distributes the range over N bins (c09, x14) | Reading of 19.5.1; Verilator's own `COVERIGN` text ("explicit array size (treated as '[]')") confirms it is a distinct form. |
| `option.at_least` and `option.auto_bin_max` set at covergroup scope apply to every coverpoint (c24, c25) | Reading of 19.7 (Table 19-1); not consulted. |
| `start()`/`stop()` suspend sampling (c28, x16); the two-argument `get_inst_coverage` writes covered and total (c34) | Reading of 19.8; not consulted. |
| `$get_coverage` returns the overall coverage as a real (c29) | Reading of 19.9; not consulted. |
| Release attribution of each `Changes` line | Read by line position under version headers in the local 5.052 file; medium confidence, as in the Chapter 6 and 7 notes. |
| The roadmap table in #7560 reflects the maintainers' view of 5.052 | It is dated 2026-08-17, between the 5.050 and 5.052 releases; three of its rows are stale against measurement (§4.2). |
| `verilated_std.sv` records appear because the model uses classes/timing | Inferred from the counter build (no such records) versus the probe builds (31 such records); the exact trigger was not isolated. |
| FC4SC compiles unpatched on Linux/libstdc++ | Inferred from `std::__not_` being a libstdc++ name; not tested. |
| `covered` (Icarus's suggested coverage tool) is unmaintained | Not evaluated; the maintainer's 2023 comment names it. |

#### Key sources

Existing `refs.bib` keys reused: `verilator-docs`, `verilator-languages`,
`verilator-warnings`, `verilator-changes`, `verilator-exe-sim`,
`verilator-simulating` (already in `refs.bib`, pointing at the latest
guide; its coverage section is the one quoted in §4.1),
`icarus-readme`, `icarus-release-13`, `cocotb-docs`, `ieee1800-2023`.
Where the chapter quotes a 5.052 limitation it should cite the
v5.052-tagged files. New entries:

```bibtex
@misc{verilator-exe-verilator-coverage,
  author       = {Wilson Snyder and {Verilator contributors}},
  title        = {Verilator User's Guide: verilator\_coverage},
  howpublished = {GitHub, verilator/verilator,
                  docs/guide/exe\_verilator\_coverage.rst at tag v5.052},
  year         = {2026},
  url          = {https://github.com/verilator/verilator/blob/v5.052/docs/guide/exe_verilator_coverage.rst},
  note         = {\texttt{--annotate}, \texttt{--annotate-min} (default
                  10), \texttt{--filter-type}, \texttt{--rank},
                  \texttt{--report}, \texttt{--write},
                  \texttt{--write-info}. Accessed 2026-09-26}
}

@misc{verilator-exe-verilator,
  author       = {Wilson Snyder and {Verilator contributors}},
  title        = {Verilator User's Guide: Verilator Arguments},
  howpublished = {GitHub, verilator/verilator, docs/guide/exe\_verilator.rst
                  at tag v5.052},
  year         = {2026},
  url          = {https://github.com/verilator/verilator/blob/v5.052/docs/guide/exe_verilator.rst},
  note         = {\texttt{--coverage} and its five components,
                  \texttt{--coverage-max-width},
                  \texttt{--coverage-underscore},
                  \texttt{--coverage-per-instance}. Accessed 2026-09-26}
}

@misc{verilator-issue-784,
  author       = {{Verilator contributors}},
  title        = {Support covergroup},
  howpublished = {GitHub, verilator/verilator, issue 784},
  year         = {2014},
  url          = {https://github.com/verilator/verilator/issues/784},
  note         = {Opened 2014-06-10, closed 2026-06-05 by pull request
                  7117; released in 5.050. Accessed 2026-09-26}
}

@misc{verilator-pr-7117,
  author       = {Matthew Ballance},
  title        = {Baseline support for covergroups, coverpoints, and bins},
  howpublished = {GitHub, verilator/verilator, pull request 7117},
  year         = {2026},
  url          = {https://github.com/verilator/verilator/pull/7117},
  note         = {Opened 2026-02-20, merged 2026-06-05. Accessed 2026-09-26}
}

@misc{verilator-issue-7560,
  author       = {{Verilator contributors}},
  title        = {Tracking: Covergroup Roadmap and Progress},
  howpublished = {GitHub, verilator/verilator, issue 7560},
  year         = {2026},
  url          = {https://github.com/verilator/verilator/issues/7560},
  note         = {Open; per-feature status table last updated
                  2026-08-17: \texttt{get\_coverage()} returns 0.0,
                  \texttt{start()}/\texttt{stop()} parsed only,
                  \texttt{option.weight} not applied, bins capped at
                  1000. Accessed 2026-09-26}
}

@misc{verilator-issue-7848,
  author       = {{Verilator contributors}},
  title        = {Covergroup in a build without --coverage generates
                  invalid C++},
  howpublished = {GitHub, verilator/verilator, issue 7848},
  year         = {2026},
  url          = {https://github.com/verilator/verilator/issues/7848},
  note         = {Opened 2026-06-28, closed 2026-06-29; fixed in 5.050.
                  Accessed 2026-09-26}
}

@misc{verilator-issue-8458,
  author       = {{Verilator contributors}},
  title        = {Covergroup bin value '1 matches 1 instead of all ones},
  howpublished = {GitHub, verilator/verilator, issue 8458},
  year         = {2026},
  url          = {https://github.com/verilator/verilator/issues/8458},
  note         = {Opened and closed 2026-09-23, after the 5.052 release;
                  reproduced on 5.052 in this note. Accessed 2026-09-26}
}

@misc{verilator-covergroup-runtime,
  author       = {{Verilator contributors}},
  title        = {verilated\_covergroup.h: covergroup runtime model},
  howpublished = {GitHub, verilator/verilator,
                  include/verilated\_covergroup.h at tag v5.052},
  year         = {2026},
  url          = {https://github.com/verilator/verilator/blob/v5.052/include/verilated_covergroup.h},
  note         = {\texttt{VlCoverpoint}, \texttt{VlCoverCross},
                  \texttt{coverageParts}; bin kinds Normal, Ignore,
                  Illegal, Default. Accessed 2026-09-26}
}

@misc{icarus-issue-1232,
  author       = {{Icarus Verilog contributors}},
  title        = {Coverage analysis},
  howpublished = {GitHub, steveicarus/iverilog, issue 1232},
  year         = {2025},
  url          = {https://github.com/steveicarus/iverilog/issues/1232},
  note         = {Maintainer's comment of 2025-04-13: ``There is no
                  support for coverage analysis in Icarus Verilog''.
                  Accessed 2026-09-26}
}

@misc{icarus-issue-911,
  author       = {{Icarus Verilog contributors}},
  title        = {getting code coverage with iverilog (question)},
  howpublished = {GitHub, steveicarus/iverilog, issue 911},
  year         = {2023},
  url          = {https://github.com/steveicarus/iverilog/issues/911},
  note         = {Maintainer's comment of 2023-04-25: no built-in
                  coverage; \texttt{covered} via VPI is the only free
                  tool named. Accessed 2026-09-26}
}

@misc{cocotb-coverage,
  author       = {Marek Cieplucha and {cocotb-coverage contributors}},
  title        = {cocotb-coverage: Functional Coverage and Constrained
                  Randomization Extensions for cocotb},
  howpublished = {PyPI, version 2.0; GitHub, mciepluc/cocotb-coverage},
  year         = {2025},
  url          = {https://pypi.org/project/cocotb-coverage/},
  note         = {Version 2.0 uploaded 2025-10-03; requires
                  \texttt{cocotb>=2.0}, Python 3.11 or later. Accessed
                  2026-09-26}
}

@misc{fc4sc,
  author       = {Teodor Vasilache and Dragos Dospinescu and
                  {AMIQ Consulting}},
  title        = {FC4SC: Functional Coverage for SystemC},
  howpublished = {GitHub, amiq-consulting/fc4sc},
  year         = {2021},
  url          = {https://github.com/amiq-consulting/fc4sc},
  note         = {Header-only C++11 library, Apache-2.0; last commit
                  2021-01-15. Does not compile unmodified with Apple
                  clang/libc++ (\texttt{std::\_\_not\_}). Accessed
                  2026-09-26}
}
```

#### Confidence notes

- **High:** every matrix cell, every printed percentage and message.
  Each is a file in the scratchpad (`ch08-probes/`, `ch08-extra/`,
  `ch08-msgs/`, `ch08-msgs-x/`, `ch08-e2e/`, `ch08-cocotbcov/`,
  `ch08-fc4sc/`), a fixed command, and an output captured on
  2026-09-26 by the book's own runner or by a shell script kept beside
  the output (`e2e.sh`, `e2e2.sh`). The main matrix was run four times
  (three flag configurations, then once more after the c22 expected
  value was corrected from 25.0 to 62.5) with identical verdicts.
- **High:** the quotations from the v5.052-tagged `languages.rst`,
  `simulating.rst`, `exe_verilator.rst`, `exe_verilator_coverage.rst`,
  `exe_sim.rst`, `warnings.rst`, the local `Changes`, the shipped
  `verilated_covergroup.h` and the generated C++; from Verilator #784,
  #7117, #7560, #7848, #7853, #8458 and the tracker searches; from
  iverilog #911, #1232 and the README, all read on 2026-09-26.
- **High:** that `cocotb-coverage` installs beside `dvbook`'s cocotb
  without touching `dvbook`, and that the FC4SC failure is the one
  line quoted; that with the one-line patch it builds and runs.
- **Medium:** the *expected* percentages, which rest on the note's
  reading of IEEE 1800 clause 19 (unsourced-claims table). Every
  "wrong" verdict that depends on the weighted-average formula (x01,
  x03, x04, x07) would flip to "runs" if the standard defined
  covergroup coverage as the bins ratio; the note believes it does
  not, and cocotb-coverage's choice of the ratio shows the question is
  live.
- **Medium:** the count of silent rows (eight constructs). It depends
  on treating c12/x08, c28/x16 and c22/x13 as one construct each and
  on the definition in §2 (no build-time `COVERIGN`, no run-time
  message).
- **Medium:** release attribution of `Changes` lines before 5.050.
- **Low:** the FC4SC group-percentage discrepancy (55.56); one run,
  formula not read.
- **Not measured:** Verilator later than 5.052 (the #8458 fix and
  #8461 are after it), `--coverage-fsm` on an FSM (the counter has
  none), `--coverage-per-instance`, `lcov`/`genhtml` rendering of the
  `.info` file, `covered` for Icarus, FC4SC on Linux, cocotb-coverage
  on any design but the counter.
- **What must be installed in the `dvbook` environment for the
  chapter's examples to run under `scripts/check-examples.sh`:**
  for every SystemVerilog covergroup listing, **nothing** — Verilator
  5.052 as installed compiles and runs them, with or without
  `--coverage`; the examples' `Makefile`s need `--coverage` (or
  `--coverage-user`) added to `VERILATOR_FLAGS` only if the listing is
  to write a `.dat`, and a `verilator_coverage` step in the recipe if
  the chapter prints a report from `run.out`. For the cocotb-coverage
  listing, one line: `conda run -n dvbook pip install cocotb-coverage`
  (which also pulls `python-constraint`; `pyyaml` is already there),
  plus the same line in CI and the README as PyYAML was added for
  Chapter 2. For an FC4SC listing, a vendored and patched copy of
  `includes/` under `examples/` and `-CFLAGS "-std=c++17 -I…"` in a
  SystemC-style Makefile; not recommended (§5.2). `lcov` is not needed
  unless the chapter renders HTML, which it should not attempt from
  `check-examples.sh`.

---
