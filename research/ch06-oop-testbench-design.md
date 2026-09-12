---
title: "Research note: Chapter 6 — Object-Oriented Testbench Design"
date: 2026-09-11
author: research-agent
status: complete
feeds: Ch. 6
---

# Chapter 6 — Object-Oriented Testbench Design: evidence note

Scope: the second half of the class system — inheritance, overriding and
dynamic dispatch, abstract and interface classes, `$cast` across a
hierarchy, copying — and what a testbench is built from once it has them:
parameterized classes as a design tool, the factory, strategy, template
method, singleton and callback patterns traced to where UVM and OpenTitan
use them, and the substitution property that decides whether a subclass is a
subtype. Then a *measured* account of which of those constructs the book's
two open simulators run, and the sixteen cells where one of them runs and
prints the wrong answer in silence.

Gathered in three independent passes and kept in three parts. **Section
numbers are local to their part**: "§2.3" inside Part A means Part A's §2.3.
Each part carries its own unsourced-claims table, BibTeX suggestions and
confidence notes.

## Which part feeds which chapter section

| Chapter topic | Part | Sections |
|---|---|---|
| `extends`, `super`, constructor chaining | A | §1 |
| Overriding, hiding, and what `virtual` changes | A | §2 |
| Abstract classes, pure virtual methods, interface classes | A | §3 |
| `$cast` across a hierarchy | A | §4 |
| Copying in a hierarchy: `copy`, `do_copy`, `clone` | A | §5 |
| `this`/`super` in virtual methods; statics under inheritance | A | §6–§7 |
| Parameterized classes as a design tool | B | §2 |
| The factory | B | §3 |
| Strategy, composition, template method, singleton, callbacks | B | §4–§8 |
| What practitioners warn against; substitutability | B | §9 |
| The Python track | B | §10 |
| **Which constructs run on which tool** (decides every example) | C | matrix |
| **Silent wrong results**, with mechanisms and tracker records | C | catalog |
| Documentation versus measurement | C | later sections |

## Findings that decide the chapter, across the parts

1. **Icarus 13.0 ignores `virtual`** (Part C matrix and catalog; Part A §2):
   a virtual call binds to the declared type of the handle expression, so
   one leaf object answers three ways through three handles, and the
   template-method shape is wrong even on the derived handle. The tracker
   states the mechanism in the maintainer's words (issue #421). Icarus
   also refuses composition at compile time (a method call through a
   handle-typed property) and handle comparison. So Chapter 6's examples
   run on Verilator, and the Icarus column is a Pitfall about a tool that
   runs and prints the wrong answer.
2. **Verilator 5.030 builds a base object from `new derived_via_base_handle`**
   (Part C catalog; Part A §5): fixed in 5.046, sixteen months after the
   version this book measures. The chapter teaches `clone()` as a virtual
   method that constructs its own class, which runs correctly, and never
   presents `new src` as a polymorphic copy.
3. **One idea, not six patterns** (Part B §1): a base class fixes an
   algorithm and leaves named holes — which class (factory), what a step
   does (virtual method), knob values (config object), behavior in a
   component the test does not own (callback) — and each is visible in
   OpenTitan or UVM source the reader can open.
4. **Every specialization of a parameterized class is a distinct type**
   (Part B §2), with three sourced consequences in UVM and OpenTitan:
   per-specialization static pools, create-by-wrapper-then-`$cast`, and
   no type name for name-based factory operations.
5. **A virtual method called from a base-class constructor runs the base
   body on both tools** (Part C); the standard's text for this was not
   read. Chapter guidance: do not do it.
6. **Clause numbers** of IEEE 1800-2023 rest on the two compilers' own
   diagnostics (Part A), cross-checked against slang's clause table; the
   standard's text was not read.


---

# Part A — Inheritance and dynamic dispatch

Scope: inheritance and dynamic dispatch as SystemVerilog defines them and
what goes wrong with them in a testbench. `extends`, `super`, constructor
chaining; overriding versus hiding; `virtual` methods and what a call
through a base handle does; pure virtual methods, abstract classes and
interface classes; `$cast` across a hierarchy; copying in a hierarchy;
`this` and `super` inside virtual methods; static members under
inheritance. Patterns built on these (factory, configuration objects,
callbacks) are Part B's business and are mentioned here only where the
UVM base library's source is the best evidence of a language rule in use.

Chapter 5's note (`research/ch05-testbench-language.md`, Part B) drew the
Chapter 5 / Chapter 6 line construct by construct and this note follows it:
handles, `new`, `null`, lifetime, shallow copy, `this` in a constructor,
static members of a single class and parameterized-class *mechanics* are
Chapter 5's and are not re-taught here. Chapter 5's published text
(`chapters/ch05-testbench-language.qmd`, "Classes: handles and objects")
ends by promising that inheritance, virtual methods and polymorphism are
the next chapter's subject and that `$cast` across a hierarchy "waits for
the hierarchy"; this note is the evidence for that promise.

**On clause numbers.** IEEE 1800-2023 is paywalled and its text was not
consulted. A clause number is given below only where one of two open
compilers cites it *against the 2023 edition* in its own source: Verilator
cites 8.4, 8.7, 8.10, 8.11, 8.13, 8.15, 8.17, 8.24, 8.25.1 and 8.26
(including 8.26.6.2) as "IEEE 1800-2023"
[Verilator `src/V3LinkDot.cpp`, `src/V3Width.cpp`, `src/V3LinkParse.cpp`, `include/verilated_types.h`, accessed 2026-09-11](https://github.com/verilator/verilator/tree/master/src),
and slang's language-support page lists the 2023 edition's clause 8
subclauses by number and title (8.13 Inheritance and subclasses, 8.14
Overridden members, 8.15 Super, 8.16 Casting, 8.17 Chaining constructors,
8.20 Virtual methods, 8.21 Abstract classes and pure virtual methods, 8.22
Polymorphism: dynamic method lookup, 8.26 Interface classes, 8.30 Weak
references)
[slang, "Language Support", accessed 2026-09-11](https://sv-lang.com/language-support.html).
Where the two agree the number is used; where only slang's table supports
it, the sentence says "slang's table". Everything else is cited to the
edition without a clause.

### Findings that decide the chapter

1. **Icarus 13.0's silent wrong answer on virtual dispatch has a tracker
   record, and the record says why.** Chapter 5's note measured it in six
   variants but found no Icarus document stating the mechanism. There is
   one: on issue #421 the maintainer wrote, 2020-12-14, "There is currently
   no support for abstract classes. The virtual keyword is accepted by the
   parser, but otherwise ignored. This is also true for virtual methods."
   [Icarus Verilog issue #421, comment 2020-12-14](https://github.com/steveicarus/iverilog/issues/421).
   That is the sentence the chapter's Pitfall needs: `virtual` is parsed and
   discarded, so every call binds to the declared type of the handle. The
   pull request that would add even parse-only `pure virtual` support has
   been open and unmerged since 2021-01-04
   [Icarus Verilog PR #469](https://github.com/steveicarus/iverilog/pull/469),
   and the one that would add class-handle `$cast` was closed unmerged on
   2026-07-21
   [Icarus Verilog PR #1447](https://github.com/steveicarus/iverilog/pull/1447).
   Every dispatch example in Chapter 6 therefore runs on Verilator, and the
   chapter should say so in the Makefile and in the text
   (`examples/ch05-testbench-language/support-matrix/matrix.md`, rows
   "inheritance, method called on the derived handle": runs / runs;
   "virtual method, call through a base handle": wrong / runs;
   "interface class": no build / runs; "parameterized class": no build /
   runs).

2. **The book's measured Verilator, 5.030, predates the fix that makes
   `new obj` polymorphic, so a shallow copy through a base handle produces a
   base object on it.** Verilator's change log records "Fix `new` shallow
   copy to preserve polymorphic runtime type (#7105)" under 5.046,
   2026-02-28
   [Verilator Changes, accessed 2026-09-11](https://github.com/verilator/verilator/blob/master/Changes),
   and the issue describes the prior behavior: with `Base b = derived_obj;
   Base copy = new b;` the copy "creates a `Base` object, not a `Derived`
   object" and "Virtual methods on `copy` dispatch to the base class
   implementation"
   [Verilator issue #7105, 2026-02-19](https://github.com/verilator/verilator/issues/7105).
   The matrix does not contain this probe. The chapter's copying section
   must either measure it on 5.030 before claiming anything about `new obj`
   across a hierarchy, or teach the `do_copy`/`clone` convention, which does
   not depend on it. This note recommends the second, and the reason is the
   third finding.

3. **The UVM copy protocol is the language's own answer to "a base-class
   copy is wrong for a derived object", and it is built from exactly the
   constructs this Part teaches.** `uvm_object::copy` is *not* virtual and
   calls the *virtual* hook `do_copy`; a derived class's `do_copy` "must
   call `super.do_copy`, and it must $cast the rhs argument to the derived
   type before copying"; `clone` is virtual and by default "calls `create`
   followed by `copy`"
   [UVM-core `uvm_object.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_object.svh).
   A non-virtual method calling a virtual one through `this`, a
   `super.` call to reach the parent's version, and a checked down-cast:
   the protocol is a worked example of §2, §4 and §6 below at once. Open
   testbench code follows it: OpenTitan's TileLink item writes `do_compare`
   by hand, opens with `if (!$cast(rhs_, rhs)) return 0;`, and combines
   `super.do_compare(rhs, comparer)` with its own field comparisons
   [lowRISC OpenTitan `tl_seq_item.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/tl_agent/tl_seq_item.sv).

4. **Constructor chaining has three rules a reader can be tested on, and
   two of the book's tools got them wrong at some point.** `super.new` must
   be the first statement of a derived constructor (Verilator errors
   "'super.new' not first statement in new function (IEEE 1800-2023 8.15)");
   if the `extends` clause supplies constructor arguments, an explicit
   `super.new` is illegal (Verilator: "Explicit super.new not allowed with
   class extends arguments (IEEE 1800-2023 8.17)"); and when the derived
   constructor writes no `super.new`, the compiler inserts a call to the
   base constructor with no arguments (Verilator's linker synthesizes an
   implicit `super.new`, and slang errors when the base constructor needs
   arguments that neither route supplies)
   [Verilator `src/V3LinkDot.cpp`, `src/V3LinkParse.cpp`, accessed 2026-09-11](https://github.com/verilator/verilator/tree/master/src),
   [slang `scripts/diagnostics.txt`, accessed 2026-09-11](https://github.com/MikePopoloski/slang/blob/master/scripts/diagnostics.txt).
   Icarus fixed a bug in 2023 in which, with an implicit constructor in the
   middle of a three-level chain, a constructor was skipped or a base
   constructor run twice
   [Icarus Verilog PR #984, 2023-08-05](https://github.com/steveicarus/iverilog/pull/984);
   Verilator added its "super.new must be first" check only in 2025–26
   (#6784) and fixed a crash on `super.new()` without a base class (#6772)
   [Verilator Changes](https://github.com/verilator/verilator/blob/master/Changes).

5. **Interface classes are not abstract classes with a different keyword,
   and the difference is the one rule the chapter must state: a class may
   `extends` one class but `implements` many interface classes.** Verilator
   rejects a second `extends` on a non-interface class with "Multiple
   inheritance illegal on non-interface classes (IEEE 1800-2023 8.13)", and
   its interface-class checks (every method must be implemented; a name
   inherited from two interface classes must be resolved; an interface class
   may not be nested in another) each cite 8.26
   [Verilator `src/V3LinkDot.cpp`, `src/V3LinkParse.cpp`](https://github.com/verilator/verilator/tree/master/src).
   slang's diagnostics add the complementary rules: an interface class's
   methods "must be marked 'pure'", it cannot extend a normal class and a
   normal class cannot extend it, and a class implementing one must supply
   each method *as a virtual method*
   [slang `scripts/diagnostics.txt`](https://github.com/MikePopoloski/slang/blob/master/scripts/diagnostics.txt).

6. **The gotcha literature has one inheritance gotcha and it is about
   dispatch depth, not about `virtual` itself.** The 2006 paper's §7.1
   shows three levels of an overridden virtual method and states that "there
   will only ever be one definition for a virtual method within a
   constructed class, and it is always the definition that is the furthest
   descendent from the base"
   [Sutherland & Mills, SNUG Boston 2006, §7.1, p. 53](http://sutherland-hdl.com/papers/2006-SNUG-Boston_standard_gotchas_paper.pdf).
   The 2007 paper has no inheritance gotcha; its class section is about
   handles, `input` versus `ref` and arrays of handles (§4.3–4.5), which
   Chapter 5 already carries, and its only mention of `pure virtual` is as a
   then-illegal vendor extension that a standards proposal was about to
   admit (§8.3)
   [Sutherland, Mills & Spear, SNUG San Jose 2007](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf).
   The chapter should not cite either paper for anything else about
   inheritance.

### 1. `extends`, `super`, and constructor chaining

A derived class names its parent with `extends`, inherits every property
and method the parent declared, and may add its own or replace the parent's
(IEEE 1800-2023; 8.13 per Verilator's citation, "Inheritance and
subclasses" per slang's table). Verilator's linker enforces the
single-parent rule at the `extends` list: a second `extends` on a
non-interface class is "Multiple inheritance illegal on non-interface
classes (IEEE 1800-2023 8.13)"
[Verilator `src/V3LinkDot.cpp`, accessed 2026-09-11](https://github.com/verilator/verilator/blob/master/src/V3LinkDot.cpp).

**`super` is a name for the parent's members, usable only inside a derived
class.** Verilator reports "'super' used outside class (IEEE 1800-2023
8.15)" and "'super' used on non-extended class (IEEE 1800-2023 8.15)"
[Verilator `src/V3LinkDot.cpp`](https://github.com/verilator/verilator/blob/master/src/V3LinkDot.cpp).
`super.method()` calls the parent's version of a method regardless of
whether it is virtual; that is what makes it the tool for *extending* a
behavior rather than replacing it, and it is the idiom the UVM base library
documents for every phase: "Any override should call super.build_phase(phase)
to execute the automatic configuration of fields registered in the
component"
[UVM-core `uvm_component.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_component.svh).
OpenTitan's base classes do it in every override this note read:
`dv_base_scoreboard::build_phase` and `run_phase` open with
`super.build_phase(phase)` and `super.run_phase(phase)`, and its `reset`
and `pre_abort` overrides call `super.` as well
[lowRISC OpenTitan `dv_base_scoreboard.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_lib/dv_base_scoreboard.sv).
Icarus once accepted `super` only inside `new`: a 2022 issue shows
`super.print()` in an ordinary method failing while `super.new()` worked;
it is closed (2022-12-26)
[Icarus Verilog issue #671](https://github.com/steveicarus/iverilog/issues/671).

**Constructor chaining.** The rules a reader needs, each with the source
that states it:

- *The base constructor runs before the derived body.* A derived
  constructor that names `super.new(...)` must do so as its first
  statement: Verilator's parser reports "'super.new' not first statement in
  new function (IEEE 1800-2023 8.15)", its linker comments "super.new shall
  be the first statement (IEEE 1800-2023 8.15)", and slang's diagnostic
  reads "super class constructor can only be called from the first
  statement in a derived class's constructor"
  [Verilator `src/V3LinkParse.cpp`, `src/V3LinkDot.cpp`](https://github.com/verilator/verilator/tree/master/src),
  [slang `scripts/diagnostics.txt`](https://github.com/MikePopoloski/slang/blob/master/scripts/diagnostics.txt).
  Verilator added this as its SUPERNFIRST check in change #6784
  [Verilator Changes](https://github.com/verilator/verilator/blob/master/Changes).
- *If you write no `super.new`, one is written for you, with no
  arguments.* Verilator's linker synthesizes an implicit `super.new` and
  inserts it before the first statement; slang scans the constructor body
  for a `super.new` and, finding none while the base constructor needs
  arguments, reports that the class "must provide arguments for
  constructing base class ... via 'super.new' or the 'extends' clause"
  [Verilator `src/V3LinkDot.cpp`](https://github.com/verilator/verilator/blob/master/src/V3LinkDot.cpp),
  [slang `scripts/diagnostics.txt`](https://github.com/MikePopoloski/slang/blob/master/scripts/diagnostics.txt).
  The defect this produces: a base class whose constructor takes a required
  argument, and a derived class whose author forgot `super.new`, is a
  compile error rather than a silent default. That is the good case; the
  bad case is a base constructor with *default* arguments, which chains
  silently with the defaults.
- *`extends base(args)` is the alternative to `super.new(args)`, and the
  two are exclusive.* Verilator: "Explicit super.new not allowed with class
  extends arguments (IEEE 1800-2023 8.17)"; slang: "cannot provide both
  'super.new' as well as class constructor arguments in 'extends' clause"
  [Verilator `src/V3LinkDot.cpp`](https://github.com/verilator/verilator/blob/master/src/V3LinkDot.cpp),
  [slang `scripts/diagnostics.txt`](https://github.com/MikePopoloski/slang/blob/master/scripts/diagnostics.txt).
  The 2023 edition also allows `super.new(default)` to forward the derived
  constructor's own defaulted arguments; slang has diagnostics for its
  misuse ("cannot use 'default' in super.new since the containing
  constructor does not use 'default' in its argument list")
  [slang `scripts/diagnostics.txt`](https://github.com/MikePopoloski/slang/blob/master/scripts/diagnostics.txt).
  Marked low-confidence below: the feature's edition of origin is inferred
  from slang, not read in the standard.
- *Tools have got chaining wrong.* Icarus's 2023 fix describes a three-level
  chain `C` → `D` → `E` in which `D`'s explicit constructor was never
  called because the lookup found `C`'s implicit one first, and a mirror
  case in which a base constructor ran twice
  [Icarus Verilog PR #984, 2023-08-05](https://github.com/steveicarus/iverilog/pull/984).
  Verilator fixed "chain call of abstract class constructor" (#3868) in
  5.008 and "handling of super.new calls" (#4366) in 5.018
  [Verilator Changes](https://github.com/verilator/verilator/blob/master/Changes).
  A chapter example with three levels and a `$display` in each constructor
  is the cheapest test of a tool's chaining, and the book's probe suite
  should carry one.

UVM's own base constructor is the canonical shape: `uvm_component::new(string
name, uvm_component parent)` begins with `super.new(name)` and only then
registers the component in the hierarchy
[UVM-core `uvm_component.svh`](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_component.svh);
OpenTitan's configuration base class does the same, `super.new(name)` first
[lowRISC OpenTitan `dv_base_env_cfg.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_lib/dv_base_env_cfg.sv).

### 2. Overriding, hiding, and what `virtual` changes

A derived class that declares a method with the same name as a base-class
method *overrides* it (slang's table: 8.14 "Overridden members"). What
happens at a call site then depends on one word in the base declaration.

**Without `virtual`, the call binds to the declared type of the handle.**
A `base` handle that holds a `derived` object calls `base`'s method. This
is "hiding": the derived method exists and runs when called through a
`derived` handle, but a base handle cannot see it. **With `virtual`, the
call binds to the type of the object**, whatever the handle's declared type
(slang's table: 8.20 "Virtual methods", 8.22 "Polymorphism: dynamic method
lookup"). The 2006 gotchas paper states the consequence for a chain of
overrides: the definition used is "always the definition that is the
furthest descendent from the base", so a `base` handle holding an `ext2`
object prints ext2's message even when `ext1` in between also overrides
[Sutherland & Mills, SNUG Boston 2006, §7.1, p. 53](http://sutherland-hdl.com/papers/2006-SNUG-Boston_standard_gotchas_paper.pdf).
(The paper's third listing, `tb_ext2`, assigns `b = e1` before `e1 = e2`,
so as printed `b` is null at its call; the chapter should write its own
listing rather than adapt that one.)

**Once virtual, always virtual.** A method declared `virtual` in a base
class stays virtual in every descendant whether or not the override repeats
the keyword. Chapter 5's probe j15g measured exactly this, an override
declared without `virtual`, and it dispatched dynamically on Verilator
(`research/ch05-testbench-language.md`, Part C §4). This note found no
compiler diagnostic quoting the rule, so it is carried as a language
statement cited to the edition
[IEEE 1800-2023](https://standards.ieee.org/ieee/1800/7743/).

**An override must match the base signature.** slang's diagnostics list the
checks, and they are the checklist a reviewer applies to a failed override:
task versus function must agree ("mismatch between 'function' and 'task'
declared in superclass method"), visibility must agree, return type must
match, argument count, types, directions and default-value presence must
match, and a mismatched argument *name* is only a warning
[slang `scripts/diagnostics.txt`, `VirtualKindMismatch` through `VirtualArgDirectionMismatch`, `VirtualArgNameMismatch`](https://github.com/MikePopoloski/slang/blob/master/scripts/diagnostics.txt).
The trap for a testbench author is the default-value rule: adding a default
to an argument in the override, or omitting one the base has, is an error,
not a silent variation.

**The 2023 override specifiers.** slang has diagnostics for a method
"marked 'extends' but doesn't override a base class virtual member" and for
a `final` specifier on a pure virtual member
[slang `scripts/diagnostics.txt`, `OverridingExtends`, `FinalWithPure`](https://github.com/MikePopoloski/slang/blob/master/scripts/diagnostics.txt),
which is evidence that the 2023 edition lets an author mark an override as
one (`:extends`) or forbid further overriding (`:final`) — the mechanism by
which a misspelled override becomes a compile error instead of a hidden
method. Which edition introduced them and which clause holds them was not
verified; neither Verilator's sources nor slang's table names them, and
the chapter should mention them, if at all, as "the 2023 edition adds" with
this note's low-confidence mark and without a clause.

**The book's tool fact, with its record.** Icarus 13.0 accepts `virtual`,
builds the probe without a warning, and runs the base body through the base
handle (matrix row "virtual method, call through a base handle": *wrong*;
probe `examples/ch05-testbench-language/support-matrix/probes/j15a_virtual_dispatch.sv`
prints `direct=9 via_base=0`). The maintainer's statement of 2020-12-14
explains it: the `virtual` keyword "is accepted by the parser, but otherwise
ignored. This is also true for virtual methods"
[Icarus Verilog issue #421](https://github.com/steveicarus/iverilog/issues/421);
on the companion issue the same day, "I don't think there is any support
for polymorphism as yet", and that issue, in which `base = derived` was
rejected as a type mismatch, is still open
[Icarus Verilog issue #422](https://github.com/steveicarus/iverilog/issues/422).
Since the 13.0 probe compiled and ran, the *assignment* now elaborates;
the *dispatch* does not. Verilator's support has its own history: "Fix
virtual methods (#4616)" in 5.018, 2023-10-30
[Verilator Changes](https://github.com/verilator/verilator/blob/master/Changes),
which is a reminder that a dispatch example is worth a probe in every tool
version the book measures.

### 3. Abstract classes, pure virtual methods, and interface classes

**An abstract class is declared `virtual class`; it may declare `pure
virtual` methods with no body; it cannot be constructed; and a concrete
subclass must implement every pure virtual method it inherits.** slang's
diagnostics state each half: "cannot create instance of virtual class",
"pure virtual methods can only be declared in virtual classes", "pure
virtual methods cannot have a function body defined", and "cannot inherit
from virtual class ... without providing an implementation for pure virtual
method"
[slang `scripts/diagnostics.txt`](https://github.com/MikePopoloski/slang/blob/master/scripts/diagnostics.txt).
Verilator added its own "error on missing pure virtual functions (#4961)"
in 5.024, 2024-04-05
[Verilator Changes](https://github.com/verilator/verilator/blob/master/Changes).
Icarus has neither check: the maintainer's 2020 reply to a report that `new`
on a `virtual class` succeeded was that "There is currently no support for
abstract classes"
[Icarus Verilog issue #421](https://github.com/steveicarus/iverilog/issues/421),
and the parse-only `pure virtual` pull request is still open
[Icarus Verilog PR #469](https://github.com/steveicarus/iverilog/pull/469).
The 2007 gotchas paper is the historical marker: `pure virtual` was then an
illegal keyword pair one vendor's libraries used, with a proposal approved
"to add this to the next version of the IEEE SystemVerilog standard"
[Sutherland, Mills & Spear, SNUG San Jose 2007, §8.3, p. 40](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf).
It arrived in 1800-2009; the chapter can say "since the 2009 edition" with
that paper as the before-picture.

**Practice.** The two roots of the UVM library are abstract: `virtual class
uvm_object extends uvm_void;` and `virtual class uvm_component extends
uvm_report_object;`
[UVM-core `uvm_object.svh`](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_object.svh),
[UVM-core `uvm_component.svh`](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_component.svh).
The header comment of `uvm_object` says classes deriving from it "must
implement the pure virtual methods such as `create` and `get_type_name`",
but in the source both are ordinary virtual methods with default bodies
(`create` returns `null`; `get_type_name` returns `"<unknown>"`)
[UVM-core `uvm_object.svh`](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_object.svh).
That gap is worth a sentence in the chapter: "pure virtual" in a library's
prose often means "you must override this", enforced by a run-time
`null`-return or warning rather than by the compiler, and the language
construct is stricter than the convention. OpenTitan documents the weaker
form by name: `dv_base_reg_block::build` is "a pseudo pure virtual function
(returns a fatal error if called directly)"
[lowRISC OpenTitan `hw/dv/sv/dv_lib/README.md`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_lib/README.md).
Why a library would choose the weaker form is a design question for Part
B (the factory needs a constructible type for `create`, and UVM keeps a
separate `uvm_object_abstract_utils` registration for classes that are
abstract
[UVM-core `uvm_object_defines.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/macros/uvm_object_defines.svh)).

**Interface classes.** An `interface class` declares only pure virtual
methods (slang: "method in interface class must be marked 'pure'"), and a
class adopts one with `implements`, of which there may be several, while
`extends` still names at most one class. The rules that separate the two
kinds, each from a compiler that cites the 2023 clause or names the rule:

| Rule | Source |
|---|---|
| A non-interface class cannot extend two classes | Verilator, "Multiple inheritance illegal on non-interface classes (IEEE 1800-2023 8.13)" |
| An interface class cannot be nested in another | Verilator, "(IEEE 1800-2023 8.26)"; slang `NestedIface` |
| A class that implements an interface class must implement every method | Verilator, "is missing implementation for ... (IEEE 1800-2023 8.26)"; slang `IfaceMethodNoImpl` |
| The implementation must itself be virtual | slang `IfaceMethodNotVirtual`, "(existing method is not virtual)" |
| A name inherited from two interface classes must be resolved explicitly | Verilator, "missing inheritance conflict resolution for ... (IEEE 1800-2023 8.26.6.2)" |
| A normal class cannot `extends` an interface class, and an interface class cannot `extends` a normal class | slang `ExtendIfaceFromClass`, `ExtendClassFromIface` |
| An interface class cannot be constructed | slang `NewInterfaceClass` |

[Verilator `src/V3LinkDot.cpp`, `src/V3LinkParse.cpp`](https://github.com/verilator/verilator/tree/master/src),
[slang `scripts/diagnostics.txt`](https://github.com/MikePopoloski/slang/blob/master/scripts/diagnostics.txt).

The difference the chapter should teach is therefore not "abstract classes
have bodies and interface classes do not" but *what each can be combined
with*: a class has one ancestry and any number of contracts. The measured
support: Verilator has had interface classes since 5.008 (2023-03-04) and
fixed a multi-inherited case in 5.018
[Verilator Changes](https://github.com/verilator/verilator/blob/master/Changes);
the matrix row "interface class" is *no build* on Icarus and *runs* on
Verilator, from the probe
`examples/ch05-testbench-language/support-matrix/probes/interface_class.sv`.
This note found no OpenTitan `hw/dv/sv` use of `interface class` in the
files it read (the base classes use abstract-by-convention and virtual
methods throughout); the chapter should present interface classes as a
language facility with a small example of its own rather than claim a
practice.

### 4. `$cast` across a hierarchy

Two directions, two rules. **Up-cast is implicit**: a derived handle may be
assigned to a base handle with plain `=`, because every derived object *is
a* base object. Icarus once rejected exactly this ("the type of the variable
'u_t_0' doesn't match the context type" for `uvm_test_top = u_t_0` where the
right side was the derived class), and the report is still open although
the 13.0 probe suite shows the assignment elaborating
[Icarus Verilog issue #422, 2020-12-13](https://github.com/steveicarus/iverilog/issues/422).
**Down-cast is checked and needs `$cast`**: assigning a base handle to a
derived handle is a compile error with `=`, and `$cast(derived_h, base_h)`
tests at run time whether the object the base handle names really is of the
derived type (or a subtype), assigning on success and, as a function,
returning 0 on failure (slang's table: 8.16 "Casting"; clause not cited by
Verilator). The task form errors instead of returning. That is the rule as
this note understands it from the edition and from three uses in open code
below; the standard's text was not read, and the chapter should quote none
of it.

Verilator has supported `$cast` since 4.108 (2021-01-10)
[Verilator Changes](https://github.com/verilator/verilator/blob/master/Changes);
its run-time implements the check as a C++ `dynamic_cast` on the object
[Verilator `include/verilated_types.h`, `dynamicCast`, accessed 2026-09-11](https://github.com/verilator/verilator/blob/master/include/verilated_types.h).
Icarus 13.0 has no class-handle `$cast`: the pull request that would add
"runtime is-a checks along the class inheritance chain" was closed unmerged
on 2026-07-21, with its own test plan's item "Spot-check failed cast
(base-only object into derived) returns 0 and leaves dest unchanged" left
unticked
[Icarus Verilog PR #1447](https://github.com/steveicarus/iverilog/pull/1447).
Chapter 5's matrix measured only `$cast` on an enum (Icarus: *no run*;
Verilator: *runs*); a class-handle `$cast` row belongs in Chapter 6's
probes, and the expectation on Icarus is a build failure.

**The three idioms, from code that ships.** Down-cast on entry to a
polymorphic hook, as UVM prescribes for `do_copy` ("it must $cast the rhs
argument to the derived type before copying")
[UVM-core `uvm_object.svh`](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_object.svh)
and OpenTitan's `tl_seq_item::do_compare` performs, with the comment that
a failed cast means the comparison has failed and that the null check is
the caller's, `compare()`'s, job
[lowRISC OpenTitan `tl_seq_item.sv`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/tl_agent/tl_seq_item.sv).
Down-cast of a factory product to the type the caller needs, with the
failure fatal: `dv_base_test` creates its configuration object through the
factory as a `uvm_object`, then `if (!$cast(cfg, base_cfg))` and a
`uvm_fatal` "Failed to cast object of type %p to expected CFG_T class"; the
comment above it explains that the object may be "some extension class"
and either way "we should be able to cast the result to a CFG_T"
[lowRISC OpenTitan `dv_base_test.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_lib/dv_base_test.sv).
Down-cast as a *type query* with a soft failure: the CIP scoreboard casts a
register-model lookup to its own `dv_base_mem` and `dv_base_reg` types and
reports `uvm_error` rather than aborting when the object is of another kind
[lowRISC OpenTitan `cip_base_scoreboard.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/cip_lib/cip_base_scoreboard.sv).
The chapter's rule of thumb follows from the three: a `$cast` whose failure
is impossible by construction is a fatal check; one whose failure is a
legitimate "not this kind" is a branch.

### 5. Copying in a hierarchy

Chapter 5 taught `b = new a` as the language's shallow copy and left the
copy *protocol* here. Two facts decide how the chapter teaches it.

**The shallow copy is defined to preserve the object's run-time type, and
the book's Verilator does not.** Verilator's run-time comments its clone as
"Polymorphic shallow clone (IEEE 1800-2023 8.7: new <handle> preserves
runtime type)"
[Verilator `include/verilated_types.h`](https://github.com/verilator/verilator/blob/master/include/verilated_types.h),
and issue #7105 quotes the 2017 edition's wording, "The new object has the
same type as the source object", while reporting that until the fix the
copy took the *declared* type of the variable, so that "Virtual methods on
`copy` dispatch to the base class implementation"
[Verilator issue #7105, 2026-02-19](https://github.com/verilator/verilator/issues/7105).
The fix shipped in 5.046 (2026-02-28); the matrix measures 5.030
(2024-10-27)
[Verilator Changes](https://github.com/verilator/verilator/blob/master/Changes).
So on the measured tool, `base_h = derived_obj; copy = new base_h;` yields
a base object that has lost the derived fields and the derived behavior, a
silent wrong result of the same family as Icarus's dispatch. The chapter
must not print the correct output of that listing from a tool that cannot
produce it. Either the book's Verilator is upgraded and the matrix re-run,
or the chapter shows the shallow copy through a *derived* handle only, and
says why.

**A base-class `copy` is wrong for a derived object, and the library
answer is a virtual hook called from a non-virtual method.** The UVM
design: `copy` is "not virtual and should not be overloaded in derived
classes. To copy the fields of a derived class, that class should override
the `do_copy` method"; `do_copy` is "the user-definable hook called by the
`copy` method"; a typical override declares a handle of its own type,
calls `super.do_copy(rhs)`, `$cast`s `rhs` into it, and copies its fields;
and `clone` "creates and returns an exact copy of this object" by calling
`create` followed by `copy`, and is virtual so that a derived class may
replace it
[UVM-core `uvm_object.svh`, "copy", "do_copy", "clone"](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_object.svh).
The default `do_copy` in `uvm_object` is empty, and `copy` refuses a null
source with an error
[UVM-core `uvm_object.svh`, implementations](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_object.svh).
Why the split works: `copy` is called through whatever handle the caller
has, but inside it `do_copy` is a virtual call on `this`, so the derived
class's fields are copied whether or not the caller knew the derived type;
and each level's `super.do_copy` reaches the level above, so the chain
copies every layer once. A class that overrides `copy` instead of `do_copy`
breaks the chain for every class below it, which is the reason the library
forbids it.

OpenTitan's transaction does not hand-write `do_copy`; it lists its fields
in a `uvm_object_utils_begin` / `uvm_field_int` block and lets the field
macros generate the copy and print behavior, while writing `do_compare` by
hand with the `$cast`-then-`super` shape above
[lowRISC OpenTitan `tl_seq_item.sv`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/tl_agent/tl_seq_item.sv).
The chapter can show both: the hand-written hook is what the reader must
understand, the macro is what they will meet. The monitor-side use of
`clone` (a fresh item per request, a clone kept for bookkeeping) is
already in Chapter 5's note and need not be repeated.

### 6. `this` and `super` inside virtual methods

`this` names the object a method was invoked on, at its run-time type, not
the declared type of the handle the caller used (8.11 per Verilator's
citation). The consequence the chapter needs: **a virtual call made on
`this` inside a base-class method dispatches to the derived override.**
That is the mechanism of `copy` → `do_copy` in §5, of `clone` → `create`,
and of every phase method: `uvm_component::build_phase` is virtual, the
derived class's override calls `super.build_phase(phase)` to reach the base
behavior, and the base library warns that the phase methods "should never
be called directly" because the phasing machinery calls them through the
component handle
[UVM-core `uvm_component.svh`](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_component.svh).
The constructor is the one place where the rule surprises: in
`uvm_component::new`, `set_name("")` is annotated `// *** VIRTUAL` in the
source, the library's own note-to-self that a virtual call from a
constructor reaches a derived override whose own constructor has not yet
run
[UVM-core `uvm_component.svh`, `new`](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_component.svh).
Whether the standard defines what a virtual call from a base constructor
does before the derived constructor has completed is not something this
note could verify; the chapter should present it as a hazard to avoid, not
as a rule.

`super.method()` is the opposite: a static call to the parent's version,
never re-dispatched, which is why an override can wrap the parent's
behavior (call `super`, then add) without recursing into itself. The
two-name rule for the reader: `this.m()` goes down to the most-derived
override; `super.m()` goes up one level and stops.

Static methods have neither: "Cannot use 'this' in a static method (IEEE
1800-2023 8.10-8.11)" and "Cannot access non-static member variable ...
from a static method ... without object (IEEE 1800-2023 8.10)"
[Verilator `src/V3Width.cpp`](https://github.com/verilator/verilator/blob/master/src/V3Width.cpp).

### 7. Static members under inheritance

Chapter 5 taught that a static property is one per class, shared by all its
objects. Under inheritance the questions are whether a subclass shares the
parent's static, and whether a static method can be overridden. This note
found no compiler diagnostic that states either answer, so both are carried
as language statements cited to the edition and marked in the unsourced
table: a static declared in a base class is inherited and remains a single
variable shared across the base and every subclass; and a static method
is resolved by the class name it is called through, is not virtual, and
cannot be made so.

The best evidence of what practice does about the second is UVM's
registration macro, which pairs the two kinds of method deliberately:

```
typedef uvm_object_registry#(T,"S") type_id;
static function type_id get_type();            return type_id::get(); endfunction
virtual function uvm_object_wrapper get_object_type(); return type_id::get(); endfunction
```

[UVM-core `uvm_object_defines.svh`, `m_uvm_object_registry_internal`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/macros/uvm_object_defines.svh).
`get_type` is static, answers for the class it was written in, and is what
you call when you have a *type* (`my_txn::get_type()`); `get_object_type`
is virtual, answers for the object's run-time class, and is what you call
when you have a *handle* whose declared type may be a base. Every class
re-runs the macro, because a static inherited from the parent would answer
with the parent's type; that is precisely the "one per class, not
overridable" rule made operational. The parameterized-class corollary from
Chapter 5's note (one static per specialization) applies unchanged.

### Tool facts for the chapter's Makefiles

| Construct | Icarus 13.0 | Verilator 5.030 | Record |
|---|---|---|---|
| Override called through the derived handle | runs | runs | matrix row "inheritance, method called on the derived handle" |
| Virtual method called through a base handle | **wrong** (base body runs, no warning) | runs | matrix; [Icarus #421 comment 2020-12-14](https://github.com/steveicarus/iverilog/issues/421) |
| `base_h = derived_h` | elaborates in 13.0 | runs | [Icarus #422](https://github.com/steveicarus/iverilog/issues/422) still open |
| `virtual class`, `pure virtual` | parsed, not enforced | enforced since 5.024 | [Icarus #421](https://github.com/steveicarus/iverilog/issues/421), [PR #469](https://github.com/steveicarus/iverilog/pull/469); [Verilator Changes](https://github.com/verilator/verilator/blob/master/Changes) |
| `interface class` / `implements` | no build | runs (since 5.008) | matrix row "interface class"; Verilator Changes |
| Class-handle `$cast` | not implemented (expect no build) | runs (since 4.108) | [Icarus PR #1447, closed unmerged](https://github.com/steveicarus/iverilog/pull/1447); Verilator Changes |
| `new obj` through a base handle | unmeasured | **base-typed copy on 5.030**; fixed in 5.046 | [Verilator #7105](https://github.com/verilator/verilator/issues/7105) |
| `super.method()` outside `new` | fixed 2022 (#671 closed) | runs | [Icarus #671](https://github.com/steveicarus/iverilog/issues/671) |
| Three-level constructor chain | fixed 2023 | runs | [Icarus PR #984](https://github.com/steveicarus/iverilog/pull/984) |

Rows marked "unmeasured" or "expect" are predictions from the tracker, not
measurements; the chapter's `verify-examples` step should add probes for
them and replace the words with results.

### Unsourced-claims table

Statements above that rest on this note's reading of the language rather
than on a passage it can point to. Each must either find a source before
the chapter states it, or be stated as the book's own reading.

| Claim | Where | Status |
|---|---|---|
| Down-cast with `=` is a compile error; `$cast` as a function returns 0 on failure, as a task reports an error | §4 | Clause text not read; consistent with three open-code uses and with the tracker record of PR #1447's test plan. Cite the edition, no clause. |
| A method declared `virtual` in a base stays virtual in all descendants whether or not the keyword is repeated | §2 | Measured (probe j15g, Chapter 5 note Part C §4) on Verilator; no diagnostic quotes the rule. Cite the edition. |
| A static property declared in a base is one variable shared with every subclass; a static method is not virtual and cannot be overridden | §7 | No diagnostic found; UVM's paired `get_type`/`get_object_type` is evidence of practice only. Cite the edition and mark as the book's reading. |
| `super.new(default)` and the `:extends`/`:final` override specifiers are additions of the 2023 edition | §1, §2 | Inferred from slang diagnostics; edition of origin and clause not verified. State as "the 2023 edition adds", low confidence, or omit. |
| A virtual call from a base constructor reaches a derived override before the derived constructor has run | §6 | Evidence is UVM's own `// *** VIRTUAL` annotation; the standard's rule was not read. Present as a hazard, not a rule. |
| `pure virtual` entered the standard with the 2009 edition | §3 | The 2007 paper says a proposal was approved for "the next version"; the edition itself was not consulted. |
| Icarus 13.0 refuses class-handle `$cast` at build time | tool table | Predicted from PR #1447's status; not measured. Probe it. |
| Verilator 5.030 produces a base-typed object for `new base_h` | Finding 2, §5 | Inferred from the fix date (5.046) and the issue's description; not measured on 5.030. Probe it before the chapter says it. |

### Key sources

Existing keys reused: `ieee1800-2023`, `sutherland2006gotchas`,
`sutherland2007gotchas`, `spear2012svfv`, `verilator-changes`,
`slang-docs`, `icarus-release-13`, `opentitan-cip-scoreboard`,
`verilator-issue-4651`. New entries:

```bibtex
@misc{icarus-issue-421,
  author       = {{Icarus Verilog contributors}},
  title        = {{SV}: abstract class not working as expected},
  howpublished = {GitHub, steveicarus/iverilog, issue 421},
  year         = {2020},
  url          = {https://github.com/steveicarus/iverilog/issues/421},
  note         = {Opened 2020-12-13, closed 2022-12-17. The maintainer's
                  comment of 2020-12-14 records that the virtual keyword
                  is accepted by the parser but otherwise ignored, for
                  classes and for methods. Accessed 2026-09-11}
}

@misc{icarus-issue-422,
  author       = {{Icarus Verilog contributors}},
  title        = {{SV}: issue with type compatibility across inheritance
                  tree},
  howpublished = {GitHub, steveicarus/iverilog, issue 422},
  year         = {2020},
  url          = {https://github.com/steveicarus/iverilog/issues/422},
  note         = {Opened 2020-12-13; open as of 2026-09-11. Base-handle
                  assignment from a derived handle rejected; maintainer
                  comment: no support for polymorphism. Accessed
                  2026-09-11}
}

@misc{icarus-pr-469,
  author       = {Srinivasan Venkataramanan},
  title        = {Added parse-only support for pure virtual methods},
  howpublished = {GitHub, steveicarus/iverilog, pull request 469},
  year         = {2021},
  url          = {https://github.com/steveicarus/iverilog/pull/469},
  note         = {Opened 2021-01-04; open and unmerged as of 2026-09-11.
                  Accessed 2026-09-11}
}

@misc{icarus-pr-984,
  author       = {{Icarus Verilog contributors}},
  title        = {Fix class constructor chaining corner cases},
  howpublished = {GitHub, steveicarus/iverilog, pull request 984},
  year         = {2023},
  url          = {https://github.com/steveicarus/iverilog/pull/984},
  note         = {Merged 2023-08-06. Describes a skipped constructor and a
                  twice-run base constructor in a three-level chain.
                  Accessed 2026-09-11}
}

@misc{icarus-pr-1447,
  author       = {{Icarus Verilog contributors}},
  title        = {{SV}: class-handle \$cast and static \$typename},
  howpublished = {GitHub, steveicarus/iverilog, pull request 1447},
  year         = {2026},
  url          = {https://github.com/steveicarus/iverilog/pull/1447},
  note         = {Closed unmerged 2026-07-21. Accessed 2026-09-11}
}

@misc{icarus-issue-671,
  author       = {{Icarus Verilog contributors}},
  title        = {Class handle ``super'' is only supported in ``new'' of
                  the child class},
  howpublished = {GitHub, steveicarus/iverilog, issue 671},
  year         = {2022},
  url          = {https://github.com/steveicarus/iverilog/issues/671},
  note         = {Opened 2022-04-06, closed 2022-12-26. Accessed
                  2026-09-11}
}

@misc{verilator-issue-7105,
  author       = {{Verilator contributors}},
  title        = {Fix new <obj> shallow copy not preserving polymorphic
                  runtime type},
  howpublished = {GitHub, verilator/verilator, issue 7105},
  year         = {2026},
  url          = {https://github.com/verilator/verilator/issues/7105},
  note         = {Opened 2026-02-19; fix released in Verilator 5.046,
                  2026-02-28. Accessed 2026-09-11}
}

@misc{verilator-src-classes,
  author       = {Wilson Snyder and {Verilator contributors}},
  title        = {Verilator source: class linking and width checks
                  (\texttt{src/V3LinkDot.cpp}, \texttt{src/V3LinkParse.cpp},
                  \texttt{src/V3Width.cpp}, \texttt{include/verilated\_types.h})},
  howpublished = {GitHub, verilator/verilator},
  year         = {2026},
  url          = {https://github.com/verilator/verilator/tree/master/src},
  note         = {Diagnostics cite IEEE 1800-2023 clauses 8.4, 8.7, 8.10,
                  8.11, 8.13, 8.15, 8.17, 8.24, 8.25.1, 8.26 and 8.26.6.2.
                  Accessed 2026-09-11}
}

@misc{slang-diagnostics,
  author       = {Michael Popoloski},
  title        = {slang diagnostics catalogue
                  (\texttt{scripts/diagnostics.txt})},
  howpublished = {GitHub, MikePopoloski/slang},
  year         = {2026},
  url          = {https://github.com/MikePopoloski/slang/blob/master/scripts/diagnostics.txt},
  note         = {Message texts for virtual-method signature checks,
                  constructor chaining, abstract and interface classes.
                  Accessed 2026-09-11}
}

@misc{slang-language-support,
  author       = {Michael Popoloski},
  title        = {slang: Language Support},
  year         = {2026},
  url          = {https://sv-lang.com/language-support.html},
  note         = {Lists IEEE 1800-2023 clause 8 subclauses by number and
                  title with the slang version that added each. Accessed
                  2026-09-11}
}

@misc{uvm-core-object,
  author       = {{Accellera Systems Initiative}},
  title        = {{UVM} core library: \texttt{uvm\_object}
                  (\texttt{src/base/uvm\_object.svh})},
  howpublished = {GitHub, accellera-official/uvm-core},
  year         = {2026},
  url          = {https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_object.svh},
  note         = {Implementation of IEEE 1800.2-2020; \texttt{copy},
                  \texttt{do\_copy}, \texttt{clone} documentation and
                  bodies. Apache-2.0. Accessed 2026-09-11}
}

@misc{uvm-core-component,
  author       = {{Accellera Systems Initiative}},
  title        = {{UVM} core library: \texttt{uvm\_component}
                  (\texttt{src/base/uvm\_component.svh})},
  howpublished = {GitHub, accellera-official/uvm-core},
  year         = {2026},
  url          = {https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_component.svh},
  note         = {Virtual phase methods and the rule that overrides call
                  \texttt{super}. Apache-2.0. Accessed 2026-09-11}
}

@misc{uvm-core-defines,
  author       = {{Accellera Systems Initiative}},
  title        = {{UVM} core library: object registration macros
                  (\texttt{src/macros/uvm\_object\_defines.svh})},
  howpublished = {GitHub, accellera-official/uvm-core},
  year         = {2026},
  url          = {https://github.com/accellera-official/uvm-core/blob/main/src/macros/uvm_object_defines.svh},
  note         = {Pairs a static \texttt{get\_type} with a virtual
                  \texttt{get\_object\_type} in every registered class.
                  Apache-2.0. Accessed 2026-09-11}
}

@misc{opentitan-tl-seq-item,
  author       = {{lowRISC contributors (OpenTitan project)}},
  title        = {{OpenTitan} \texttt{tl\_seq\_item}: the {TileLink}
                  transaction class},
  howpublished = {GitHub, lowRISC/opentitan,
                  hw/dv/sv/tl\_agent/tl\_seq\_item.sv},
  year         = {2026},
  url          = {https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/tl_agent/tl_seq_item.sv},
  note         = {Hand-written \texttt{do\_compare} with \$cast and
                  \texttt{super}; field macros for copy. Apache-2.0.
                  Accessed 2026-09-11}
}

@misc{opentitan-dv-base-test,
  author       = {{lowRISC contributors (OpenTitan project)}},
  title        = {{OpenTitan} \texttt{dv\_base\_test}},
  howpublished = {GitHub, lowRISC/opentitan,
                  hw/dv/sv/dv\_lib/dv\_base\_test.sv},
  year         = {2026},
  url          = {https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_lib/dv_base_test.sv},
  note         = {Factory-created configuration object down-cast with a
                  fatal check. Apache-2.0. Accessed 2026-09-11}
}

@misc{opentitan-dv-base-scoreboard,
  author       = {{lowRISC contributors (OpenTitan project)}},
  title        = {{OpenTitan} \texttt{dv\_base\_scoreboard}},
  howpublished = {GitHub, lowRISC/opentitan,
                  hw/dv/sv/dv\_lib/dv\_base\_scoreboard.sv},
  year         = {2026},
  url          = {https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_lib/dv_base_scoreboard.sv},
  note         = {Every phase override opens with a \texttt{super} call.
                  Apache-2.0. Accessed 2026-09-11}
}

@misc{opentitan-dv-lib-readme,
  author       = {{lowRISC contributors (OpenTitan project)}},
  title        = {{OpenTitan} {DV} base library (\texttt{dv\_lib}) README},
  howpublished = {GitHub, lowRISC/opentitan, hw/dv/sv/dv\_lib/README.md},
  year         = {2026},
  url          = {https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_lib/README.md},
  note         = {Describes \texttt{dv\_base\_reg\_block::build} as a
                  ``pseudo pure virtual function''. Apache-2.0. Accessed
                  2026-09-11}
}
```

Works named but not read, for the chapter's further-reading list only,
with no claim about their contents: Cummings, "SystemVerilog's Virtual
World: An Introduction to Virtual Classes, Virtual Methods and Virtual
Interface Instances" (SNUG Boston 2009) and "SystemVerilog Virtual Classes,
Methods, Interfaces and Their Use in Verification and UVM" (SNUG Silicon
Valley 2018), both listed in the author's paper index behind a login
[Paradigm Works, Technical Library, accessed 2026-09-11](https://www.paradigm-works.com/papers/);
and Spear & Tumbush, chapter 8, "Advanced OOP and Testbench Guidelines",
pp. 273–321, whose title and extent come from the Crossref chapter record
[Crossref, ISBN 9781461407140, accessed 2026-09-11](https://api.crossref.org/works?filter=isbn:9781461407140&rows=30&select=title,DOI,page).
Chapter 5 already cites that split; Chapter 6 may cite the chapter title
and pages and nothing inside it.

### Confidence notes

- **High:** the Icarus maintainer's statement that `virtual` is parsed and
  ignored (quoted from the issue thread); the status and dates of Icarus
  PRs #469, #984, #1447 and issues #421, #422, #671 (read from the GitHub
  API on 2026-09-11); Verilator's clause citations and change-log entries
  (read from the source and the `Changes` file); the UVM `copy`/`do_copy`/
  `clone` documentation and bodies, the `virtual class` declarations, the
  registration macro, and the `// *** VIRTUAL` annotation (read from
  uvm-core `main`); the OpenTitan `$cast` and `super` uses (read from the
  files named); the 2006 §7.1 and 2007 §4.3–4.5, §8.3 passages (read from
  the PDFs). Every quotation above is from text this note read.
- **Medium:** clause numbers. Verilator's citations are against the 2023
  edition and are taken as verified; slang's table gives 2023 subclause
  titles for 8.14, 8.16, 8.20–8.22 and 8.30 but is a third party's index,
  not the standard. The Chapter 5 note's table used 2017-era numbering for
  the same constructs and the two agree for every clause both mention.
- **Medium:** the reading of the interface-class rules as "one ancestry,
  many contracts". Each rule in the §3 table is a compiler diagnostic; the
  framing is this note's.
- **Low:** everything in the unsourced-claims table; in particular the two
  tool predictions (Icarus on class-handle `$cast`, Verilator 5.030 on
  `new base_h`) are the two things most likely to embarrass the chapter if
  stated before a probe confirms them.
- **Not done:** the standard's text; the Cummings papers (behind a login;
  the Sutherland index has no OOP paper); OpenTitan's use of `interface
  class` (none found in the files read, which is not a survey of the
  repository); web search was unavailable for the final third of this run,
  so tracker records were found through the GitHub API rather than
  search, and a differently titled Icarus issue on dispatch may exist.

---

# Part B — The patterns a testbench is built from, and parameterized classes

Scope: parameterized classes as a *design* tool (type and value parameters,
specialization, `typedef` of a specialization, parameterized base classes,
the distinct-type rule and what it does to static members and `$cast`); the
patterns a verification testbench actually uses — factory, strategy/policy,
composition over inheritance, template method, singleton, callbacks versus
overrides — each traced to a general source and to the place a verification
methodology or a production testbench uses it; and the warnings practitioners
give about inheritance, with the Liskov substitution principle applied to a
transaction class. Part A of the Chapter 6 evidence covers inheritance and
polymorphism as language mechanics; Chapter 5's note (`research/ch05-testbench-language.md`,
Part B §6) already covers the *syntax* of parameterized classes and the
one-static-per-specialization rule, which this part builds on rather than
repeats.

Written section by section; the most important part is first.

### 1. The findings that decide the chapter

**The testbench's patterns are one pattern: a base class fixes an algorithm
and leaves named holes, and the test fills the holes without editing the
environment.** The factory fills the hole "which class gets constructed", the
virtual method fills "what this step does", the configuration object fills
"which knob values apply", and the callback fills "what happens at this
point in a component the test does not own". The UVM 1.2 User's Guide says
this in one sentence about the factory — it "allows the developer to derive a
new class extended from my_driver and cause the factory to return the
extended type in place of my_driver", so the parent never changes
[Accellera, UVM 1.2 User's Guide §3.7, 2015-10-08](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf)
— and its callback section says the same about hooks: they "augment component
behavior" while the "integrity of the component's overall behavior is intact"
[Accellera, uvm-core `uvm_callback.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_callback.svh).
The chapter can therefore teach *one* idea (open for extension, closed for
edit) and show four mechanisms that deliver it, rather than six unrelated
patterns.

**Every pattern the chapter names is visible in code the reader can open.**
The factory is `uvm_factory` and the `type_id::create` proxy; the template
method is `uvm_driver`'s `run_phase` in OpenTitan, which forks
`reset_signals()` and `get_and_drive()` and documents that "the get_and_drive
task should be implemented in any subclass"
[lowRISC OpenTitan `dv_base_driver.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_base_agent/dv_base_driver.sv);
the strategy/policy pattern is UVM's literal `uvm_policy` family
(`uvm_comparer`, `uvm_copier`, `uvm_printer`, `uvm_packer`), passed as an
argument to `compare()` and `copy()`
[Accellera, uvm-core `uvm_object.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_object.svh);
the singleton is `uvm_root::get()` and `uvm_coreservice_t::get()`
[Accellera, uvm-core `uvm_coreservice.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_coreservice.svh);
composition is `dv_base_agent`, which *holds* a driver, a monitor and a
sequencer and holds a `cfg` object rather than inheriting any of them
[lowRISC OpenTitan `dv_base_agent.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_base_agent/dv_base_agent.sv).
None of these is a textbook abstraction the chapter must invent an example
for.

**Parameterized classes are how a production testbench chooses composition
without giving up static typing, and the price is real.** OpenTitan's entire
base library is type-parameterized: `dv_base_env #(CFG_T, VIRTUAL_SEQUENCER_T, SCOREBOARD_T, COV_T)`,
`dv_base_agent #(CFG_T, DRIVER_T, HOST_DRIVER_T, DEVICE_DRIVER_T, SEQUENCER_T, MONITOR_T, COV_T)`,
`dv_base_test #(CFG_T, ENV_T)`
[lowRISC OpenTitan `dv_base_env.sv`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_lib/dv_base_env.sv),
[`dv_base_agent.sv`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_base_agent/dv_base_agent.sv),
[`dv_base_test.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_lib/dv_base_test.sv).
The price, in the words of the driver's own header comment: the driver
"would make more sense as an abstract base class" but cannot be, because the
agent "ends up needing to instantiate a uvm_driver instance unless parameters
are overridden" and `uvm_driver::create` is not implemented in UVM 1.2
[lowRISC OpenTitan `dv_base_driver.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_base_agent/dv_base_driver.sv).
A default type parameter must be a *concrete* type; that is the design
constraint the chapter should state.

**Every specialization is a distinct type, and the factory pays for it in
names.** The UVM 1.2 Class Reference says of the `_param_utils` macros that
"a type name is not associated with the type when registering with the
factory, so the factory's *_by_name operations will not work with
parameterized classes" and that the factory's `print` and debug methods list
them as `<unknown>`
[Accellera, UVM 1.2 Class Reference, `uvm_default_factory` Usage, 2015](https://www.accellera.org/images/downloads/standards/uvm/UVM_Class_Reference_Manual_1.2.pdf).
The `+UVM_TESTNAME=` mechanism is name-based, which is why OpenTitan's tests
are non-parameterized leaves over a parameterized base.

**Tool support decides the examples.** Chapter 5's measured matrix found
that a parameterized class `#(type T, int N)` runs on Verilator and is a
syntax error on Icarus 13.0, and that Icarus dispatches virtual methods
statically (Chapter 5 note, Part C §1 and §4). Every runnable Chapter 6
listing that uses either construct is therefore Verilator-only, and the
chapter must say so beside each listing.

### 2. Parameterized classes as a design tool

Chapter 5 taught the syntax; this section is about *what to parameterize
and why*. The chapter's line is: a type parameter says "this component works
with any T that has the members I use", checked when the specialization is
elaborated; a value parameter fixes a width or a count at the same time.
Both are resolved before simulation starts, so a parameterized class costs
nothing at run time and cannot be changed by a plusarg.

**Type parameters as the composition knob.** The UVM library's own
components are parameterized on the transaction type: `uvm_driver #(type
REQ=uvm_sequence_item, type RSP=REQ)` declares `REQ req; RSP rsp;` and a
`uvm_seq_item_pull_port #(REQ, RSP)`
[Accellera, uvm-core `uvm_driver.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/comps/uvm_driver.svh).
OpenTitan generalizes this to every part of an agent: `dv_base_agent`'s
header comment names seven type parameters and says of each what it "should
be a subclass of" — `DRIVER_T` "should be a subclass of dv_base_driver",
`HOST_DRIVER_T` and `DEVICE_DRIVER_T` "should be a subclass of DRIVER_T"
[lowRISC OpenTitan `dv_base_agent.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_base_agent/dv_base_agent.sv).
That comment is the honest statement of what SystemVerilog cannot express:
there is no constraint on a type parameter, so the "should be" is a
convention enforced only when the agent's `build_phase` calls
`MONITOR_T::type_id::create(...)` and assigns `monitor.cfg = cfg` — a
`MONITOR_T` without those members fails at elaboration of the specialization,
not at the declaration. The chapter can present this as the SystemVerilog
version of a bounded generic, with the bound written in a comment.

**Parameterized base classes and the `typedef` of a specialization.** Every
OpenTitan IP derives concrete, non-parameterized classes from the
parameterized base and gives the specialization a short name in one place;
the Class Reference's own factory example does the same
(`typedef driverB #(packet) B_driver;`) before using `B_driver::type_id::create`
and `B_driver::get_type()` in overrides
[Accellera, UVM 1.2 Class Reference, `uvm_default_factory` Usage, 2015](https://www.accellera.org/images/downloads/standards/uvm/UVM_Class_Reference_Manual_1.2.pdf).
The lowRISC style guide adds a rule that looks contradictory until the
distinct-type rule is understood: when creating with
`<type_name>::type_id::create()`, "the `<type_name>` must be explicitly
declared, parameters representing types must not be used here"
[lowRISC DV style guide, Factory §3, accessed 2026-09-11](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).
OpenTitan's *base* classes nonetheless write `SCOREBOARD_T::type_id::create`
and `MONITOR_T::type_id::create` (files cited above); the rule is for the
IP-level code that extends them, where the concrete type is known. The
chapter should show both and explain the split: inside the parameterized
base the parameter is the only name available; in the leaf, naming the
concrete type keeps the factory's name-based tooling and error messages
meaningful (next paragraph).

**Each specialization is a distinct type: three consequences.** (i) *Static
members*: `uvm_config_db #(type T=int)` stores each setting as a
`uvm_resource#(T)` — itself a distinct type per `T` — in a
`static uvm_pool#(string,uvm_resource#(T)) m_rsc[uvm_component]` that exists
once per specialization, so a value `set` under `#(int)` is not found by a
`get` under `#(bit [31:0])`: the lookup is typed, and the two specializations
hold different resources in different static pools
[Accellera, uvm-core `uvm_config_db.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_config_db.svh).
The lowRISC guide's response is to pass configuration *objects* only and
never "integers, strings, or other basic data types", because "it is much
easier for namespace collisions to occur when using lower level types"
[lowRISC DV style guide, Configuration Mechanism §4, accessed 2026-09-11](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).
(ii) *`$cast`*: a handle of `pkt #(8)` cannot be cast to `pkt #(16)`; they
share no ancestor other than what the parameterized declaration `extends`.
The idiom OpenTitan uses when the concrete type is only known at run time is
to create through a `uvm_object_wrapper` and cast to the parameter:
`base_cfg = cfg_type.create_object("cfg"); if (!$cast(cfg, base_cfg)) `uvm_fatal(...)`,
with the comment that the result "might" be "an instance of some extension
class" but "we should be able to cast the result to a CFG_T"
[lowRISC OpenTitan `dv_base_test.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_lib/dv_base_test.sv).
(iii) *Names*: the `_param_utils` macros register no type name, so
`create_*_by_name`, `+UVM_TESTNAME` and the factory's `print` cannot see a
parameterized class; the Class Reference's example works around it by hand
with `const static string type_name = {"driverB #(",T::type_name,")"}`
[Accellera, UVM 1.2 Class Reference, `uvm_default_factory` Usage, 2015](https://www.accellera.org/images/downloads/standards/uvm/UVM_Class_Reference_Manual_1.2.pdf),
and `uvm_factory`'s own header warns that "the name-based interface is not
portable across simulators when used with parameterized classes"
[Accellera, uvm-core `uvm_factory.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_factory.svh).

**Value parameters.** The Class Reference's registration example is
`class packet #(type T=int, int WIDTH=32) extends uvm_object;` with
`` `uvm_object_param_utils(packet #(T,WIDTH)) ``; Chapter 5's note already
records OpenTitan's `push_pull_agent_cfg#(.DeviceDataWidth(EDN_DATA_WIDTH))`
as the production case (Chapter 5 note, Part B §6). The chapter needs one
listing with both kinds, and the Class Reference example is the model.

**What the tools run.** Verilator added class parameters in 4.226 and was
still fixing "typedefs pointing to parameterized classes" in 5.020
[Verilator `Changes`, accessed 2026-09-11](https://github.com/verilator/verilator/blob/master/Changes);
Icarus 13.0 rejects `class fifo #(` outright (Chapter 5 note, Part C §1).
Any example in this section is Verilator-only.

### 3. The factory: constructing objects by name and by proxy

**What the pattern is.** Gamma, Helm, Johnson and Vlissides catalogue
twenty-three patterns in three groups; the creational group is where the
factory patterns live, and the book's stated purpose is "a catalog of simple
and succinct solutions to commonly occurring design problems"
[Gamma, Helm, Johnson & Vlissides, *Design Patterns*, 1st ed., Addison-Wesley, 1994 (publisher record)](https://www.informit.com/store/design-patterns-elements-of-reusable-object-oriented-9780201633610).
The chapter should cite the book by edition for the general pattern and not
reproduce its structure; what a testbench needs is narrower than either
Factory Method or Abstract Factory, and UVM's own description is the better
primary source for that narrower thing.

**Why a testbench constructs by name.** The UVM 1.2 User's Guide states the
purpose in one paragraph: the factory lets "components create objects
without specifying the exact class of the object being creating", the
mechanism "is referred to as an override and the override can be by instance
or type", and "Any components which are to be swapped shall be
polymorphically compatible"
[Accellera, UVM 1.2 User's Guide §6.2.1, 2015-10-08](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf).
The mechanism is a *proxy*: every registered class has a lightweight
`uvm_object_registry #(T,Tname)` or `uvm_component_registry #(T,Tname)`
object that knows how to `new` a `T`, and "when the factory needs to create
an object of a given type, it calls the proxy's create_object or
create_component method"
[Accellera, uvm-core `uvm_factory.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_factory.svh).
`type_id` is the `typedef` of that proxy's specialization (Chapter 5 note,
Part B §6), which is why `my_driver::type_id::create("drv", this)` is a
static call on a class that is *not* `my_driver`.

**Search order.** The factory "will first search for an instance override
that matches the full instance name of the object. If no instance-specific
override is found, the factory will search for a type-wide override"
[Accellera, UVM 1.2 User's Guide §6.2.1](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf);
instance overrides are matched "in order of override registrations, and the
first override match prevails", so "more specific overrides should be
registered first"; and overrides chain — "If foo overrides bar, and xyz
overrides foo, then a request for bar will produce xyz", with a loop
reported as an error
[Accellera, uvm-core `uvm_factory.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_factory.svh).
The two override forms as the User's Guide prints them are
`<orig_type>::type_id::set_type_override(<override_type>::get_type(), bit replace = 1)`
and `<orig_type>::type_id::set_inst_override(<override_type>::get_type(), string inst_path)`
[Accellera, UVM 1.2 User's Guide §6.2.3.1–§6.2.3.2](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf).

**The rule that makes the factory work, and the rule that breaks it.** An
override is only visible to objects constructed *after* it: "All
type-override code should be executed in a parent prior to building the
child(ren). This means that environment overrides should be specified in the
test" [Accellera, UVM 1.2 User's Guide §6.2.3](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf).
lowRISC turns this into three rules: "All classes must be registered with
the factory", "The `create()` API must be used to create all objects and
components" except TLM objects and covergroups, and "All type or instance
overrides must be in place before creating the class instance"
[lowRISC DV style guide, Factory §1, §2, §8, accessed 2026-09-11](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).
A `new` typed by hand in an environment is invisible to the factory and is
the first thing to look for when an override "does not take". The chapter's
Pitfall is that sentence.

**Type-based versus name-based.** `uvm_factory` documents its two
interfaces with a preference: type-based requests are "far less prone to
errors in usage" and errors "are caught at compile-time"; name-based requests
are "dominated by string arguments that can be misspelled and provided in the
wrong order"
[Accellera, uvm-core `uvm_factory.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_factory.svh).
The one name-based call every testbench makes is the test selection: lowRISC
requires `run_test()` with no argument so that `+UVM_TESTNAME=<testname>`
selects the test "without having to recompile"
[lowRISC DV style guide, UVM Guidelines, accessed 2026-09-11](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).
That is the factory's real payoff for a regression: one compiled image, N
tests chosen by string.

**The factory as the replacement for a `case` on type.** The User's Guide's
sequence-item example is the cleanest small case for the chapter: a
`word_aligned_item extends simple_item` adds one constraint, and
`set_type_override_by_type(simple_item::get_type(), word_aligned_item::get_type())`
makes every sequence that creates a `simple_item` produce the aligned one,
with no sequence edited
[Accellera, UVM 1.2 User's Guide §3.1.1 and §3.10.4](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf).
A widely cited practitioner treatment, Cummings and Chambers' "The OVM/UVM
Factory & Factory Overrides: How They Work – Why They Are Important" (SNUG
Silicon Valley 2012), is listed in its authors' library
[Paradigm Works technical library, accessed 2026-09-11](https://www.paradigm-works.com/papers/)
but the page exposes no PDF link; its text was not consulted and it is
recorded in the confidence notes.

### 4. Strategy and policy: changing a step without touching the environment

**What the pattern is.** A strategy is an object that encapsulates one
interchangeable algorithm behind a fixed interface, so the client that calls
it does not change when the algorithm does; it is one of the behavioral
patterns in Gamma et al. (1994, cited above). In SystemVerilog the smallest
form of it is a virtual method: the environment calls `compare(exp, act)`;
the test decides what `compare` does.

**Where UVM uses it, by name.** UVM's `uvm_object` operations take a
*policy object*: `copy(uvm_object rhs, uvm_copier copier=null)`,
`compare(uvm_object rhs, uvm_comparer comparer=null)`, and the print, pack
and record methods likewise; "If a compare policy is not provided, then the
global uvm_default_comparer policy is used"
[Accellera, uvm-core `uvm_object.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_object.svh).
All of them derive from an abstract `uvm_policy`, "a common base from which
all UVM policy classes derive", implemented per IEEE 1800.2 clause 16.1
[Accellera, uvm-core `uvm_policy.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_policy.svh).
This is the strategy pattern with the strategy passed as an argument; a
scoreboard that wants field-wise tolerance changes the comparer, not the
transaction.

**The test-overrides-a-virtual-method form.** The User's Guide's guidance
for data items is that the base class "should use virtual methods to allow
derived classes to override functionality"
[Accellera, UVM 1.2 User's Guide §3.1.1](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf),
and for tests that the base test's `build_phase` and `run_phase` "may be
refined as needed because they are all virtual"
[Accellera, UVM 1.2 User's Guide §4.5.1](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf).
OpenTitan's base virtual sequence gives the test a named hook,
`virtual function void configure_vseq()`, "invoked in pre_randomize()" and
meant to be overridden "in the extended classes to configure / control the
randomization of this sequence"
[lowRISC OpenTitan `dv_base_vseq.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_lib/dv_base_vseq.sv);
its scoreboard's `sample_resets()` is an empty virtual task whose comment
says "actual coverage collection is under extended classes"
[lowRISC OpenTitan `dv_base_scoreboard.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_lib/dv_base_scoreboard.sv).
The chapter's example can be exactly this shape: a base scoreboard with a
virtual `compare`, a test that overrides it through the factory.

**The `do_copy` / `do_compare` convention (deep copy, deferred from Chapter
5).** `copy` "is not virtual and should not be overloaded"; a derived class
overrides `do_copy`, and "must call super.do_copy, and it must $cast the rhs
argument to the derived type before copying"; `do_compare` likewise "must
call super.do_compare()"
[Accellera, uvm-core `uvm_object.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_object.svh).
That is a non-virtual public method calling a virtual hook — the template
method of §6 applied to copying — and it is where the chapter's `$cast`
discussion lands: the downcast is the price of a hook whose signature is
fixed in the base class as `uvm_object rhs`.

### 5. Composition versus inheritance: why a driver holds a transaction

**The general rule.** The Google C++ style guide, a public engineering
standard, states it as "Composition is often more appropriate than
inheritance", limits inheritance to the case where "it can reasonably be
said that Bar 'is a kind of' Foo", and gives the cost: with implementation
inheritance "the code implementing a sub-class is spread between the base and
the sub-class, it can be more difficult to understand an implementation"
[Google C++ Style Guide, Inheritance, accessed 2026-09-11](https://google.github.io/styleguide/cppguide.html#Inheritance).
Gamma et al. state the same principle in their introduction; the wording is
recorded in the unsourced table because the book's text could not be
consulted online.

**Where UVM applies it.** A `uvm_driver` *has* a `REQ req` and a `RSP rsp`
and a `seq_item_port` through which it pulls items from a sequencer
[Accellera, uvm-core `uvm_driver.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/comps/uvm_driver.svh);
a driver is not a transaction, and a transaction is not a driver, so neither
extends the other. The User's Guide's architecture chapter separates the two
kinds of class by lifetime: components "remain in place for the duration of
the simulation", in contrast to sequences, sequence items and transactions,
"which are transient — they are created, used, and then garbage collected
when dereferenced"
[Accellera, UVM 1.2 User's Guide §6.1 and footnote 1](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf).
That lifetime difference is the chapter's argument for composition: the
long-lived object holds a handle to the short-lived one, and inheritance
across that boundary would tie a transaction's lifetime to a component's.

**Where OpenTitan applies it.** `dv_base_agent` declares `CFG_T cfg; COV_T
cov; DRIVER_T driver; SEQUENCER_T sequencer; MONITOR_T monitor;` and wires
them in `build_phase` and `connect_phase`
[lowRISC OpenTitan `dv_base_agent.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_base_agent/dv_base_agent.sv).
Configuration is composed the same way: lowRISC recommends "a designated
configuration object extended from `uvm_object`" for every env and agent,
and "that the environment's configuration object contain the agent's
configuration object"
[lowRISC DV style guide, Configuration Mechanism §2–§3, accessed 2026-09-11](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).
The agent's two-driver rule is composition chosen *over* a driver subclass
hierarchy: for interfaces with host and device modes, "two drivers should be
created, one for each mode, and arbitration done in the
`uvm_agent::build_phase` function to determine which driver to instantiate"
[lowRISC DV style guide, `uvm_agent` usage §3](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md),
which is what `HOST_DRIVER_T` and `DEVICE_DRIVER_T` in `dv_base_agent` are
for.

**The transaction-class rule.** lowRISC's transaction guideline is a
composition rule in disguise: a transaction "Should contain only information
that is relevant to the data being transmitted over an interface, and not to
the means of transmit"
[lowRISC DV style guide, Class Definitions §8](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).
Timing, interface handles and driver state belong to the component that
holds the transaction, not in the transaction's class hierarchy.

### 6. Template method: a base algorithm with virtual hooks

**What the pattern is.** A template method is a base-class method that
fixes the *order* of steps and calls virtual methods for the steps
themselves, so subclasses vary the steps without restating the order; it is
one of the behavioral patterns in Gamma et al. (1994).

**UVM phasing is the template method at the scale of the whole testbench.**
The base library "provide[s] a set of phases to initialize, run, and
complete each test"; `uvm_component` declares `build_phase`,
`connect_phase`, `run_phase` and the rest as virtual methods and its
`build_phase` documentation says "This method should never be called
directly"
[Accellera, uvm-core `uvm_component.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_component.svh).
The order is the library's; the content is the user's. The obligation that
comes with it is `super`: "Any override should call super.build_phase(phase)"
(same file), and lowRISC makes it a rule for every user-defined component —
"`super.<phase_name>_phase` must be called for every phase method that is
being overridden"
[lowRISC DV style guide, Class Definitions §7](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).

**The driver-sized version.** OpenTitan's `dv_base_driver::run_phase` is
five lines: `fork reset_signals(); get_and_drive(); join`. The header
comment says "Subclasses might not need to implement run_phase directly",
that `reset_signals` is a task "Subclasses shouldn't normally need to
override", that `get_and_drive` "should be implemented in any subclass", and
that `on_enter_reset` and `on_leave_reset` are hooks a subclass "can"
implement
[lowRISC OpenTitan `dv_base_driver.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_base_agent/dv_base_driver.sv).
This is the listing the chapter should model its worked example on: one
fixed algorithm, one mandatory hook, two optional hooks, each named for what
it is.

**The sequence version.** `uvm_sequence_base::start` runs `pre_body`,
`body` and `post_body` in order when `call_pre_post` is 1, and `body`'s
default implementation only warns "Body definition undefined"
[Accellera, uvm-core `uvm_sequence_base.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/seq/uvm_sequence_base.svh).
lowRISC's rule that `body()` "should only execute the raw functional
behavior of the sequence" with housekeeping in `pre_start()` and
`post_start()` — because those "will always be called, even for subsequences
called from a parent sequence"
[lowRISC DV style guide, Sequences §3](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md)
— is a rule about which hook of the template to use, and a good Pitfall:
`pre_body` "is not called" when `start` is invoked with `call_pre_post` set
to 0, and that is exactly how the `` `uvm_do `` macros start a subsequence
(`__seq.start(__seq.get_sequencer(), this, PRIORITY, 0)`)
[Accellera, uvm-core `uvm_sequence_base.svh` and `macros/uvm_sequence_defines.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/macros/uvm_sequence_defines.svh).

**Why the hook cannot be `pure virtual` in UVM 1.2.** The abstract form of
the template method — a base class that cannot be instantiated because a
step is undefined — is what OpenTitan wanted for its driver and could not
have, for the reason quoted in §1: the parameterized agent instantiates the
default `DRIVER_T` unless overridden, and a `pure virtual` task would make
that default uninstantiable
[lowRISC OpenTitan `dv_base_driver.sv`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_base_agent/dv_base_driver.sv).
The chapter can show the abstract form in a standalone example and then
show why a library with concrete defaults settles for a run-time failure.

### 7. Singleton: the databases and the root, and what they cost

**What the pattern is.** A singleton is a class that guarantees one
instance and provides a global access point to it; it is the creational
pattern in Gamma et al. (1994) that practitioners most often warn against,
because a global access point is global state.

**Where UVM uses it.** `uvm_root` is "the implicit top-level and phase
controller for all UVM components"; "The UVM automatically creates a single
instance of uvm_root that users can access via the global (uvm_pkg-scope)
variable, uvm_top", and it is implemented as a `static local uvm_root m_inst`
behind a `static function uvm_root get()`
[Accellera, uvm-core `uvm_root.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_root.svh).
The factory and the resource pool are reached the same way: since 1800.2,
through `uvm_coreservice_t::get()`, itself a singleton
(`local static uvm_coreservice_t inst`) whose `get_factory`, `set_factory`
and sibling methods hand out the other services
[Accellera, uvm-core `uvm_coreservice.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_coreservice.svh).
`uvm_config_db#(T)` is a singleton per specialization by construction —
"All of the functions in uvm_config_db#(T) are static, so they must be
called using the :: operator"
[Accellera, UVM 1.2 Class Reference, `uvm_config_db`](https://www.accellera.org/images/downloads/standards/uvm/UVM_Class_Reference_Manual_1.2.pdf) —
and the phase objects are documented as "singleton phase handles"
(`uvm_run_phase::get()`) (same reference).

**The cost, as the library itself records it.** Three costs are visible in
primary sources. (i) *Global state needs a global namespace*: lowRISC's rule
against passing "integers, strings, or other basic data types" through
`uvm_config_db` exists because "it is much easier for namespace collisions
to occur when using lower level types", and its rule that "Wildcards must not
be used in the field argument" is the same problem from the other side
[lowRISC DV style guide, Configuration Mechanism §4, §6](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).
(ii) *A failed lookup is silent unless checked*: `get` returns a bit, and
lowRISC requires "Checks for success must always be performed", with a
`uvm_fatal` on failure (same section §5). (iii) *Precedence is time
dependent*: `uvm_config_db::set` documents that at build time "Settings from
hierarchically higher levels have higher precedence", but "After build time,
all settings use the default precedence and thus have a last wins semantic",
so "a low level component" setting a field at run time "will have precedence
over a setting from the test level that was made earlier"
[Accellera, uvm-core `uvm_config_db.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_config_db.svh).
That last rule is the chapter's Pitfall for the singleton: global state has
an order of assignment that the class hierarchy does not show.

**The mitigation UVM chose.** `uvm_coreservice_t` exists so that the
singletons can be *replaced*: it is an abstract class with `set_factory`,
`set_report_server` and so on, and a `set(uvm_coreservice_t cs)` that swaps
the whole service object
[Accellera, uvm-core `uvm_coreservice.svh`](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_coreservice.svh).
OpenTitan uses exactly this seam: `dv_base_test::build_phase` installs its
own `dv_report_server` with `uvm_report_server::set_server(m_dv_report_server)`
[lowRISC OpenTitan `dv_base_test.sv`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_lib/dv_base_test.sv).
A singleton with a setter is a global that a test can substitute; the
chapter should present the pattern with that seam, not without it.

### 8. Callbacks versus overrides

**Two ways to fill the same hole.** UVM's callback documentation lays out
the choice explicitly. The component developer "defines a set of 'hook'
methods", and the library recommends that the developer "also define a
corresponding set of virtual method hooks in the component itself", which
"affords users the ability to customize via inheritance/factory overrides as
well as callback object registration"; the virtual method "would provide the
default traversal algorithm" for the registered callbacks, and an override
can add work "before and/or after calling super.<method>" or skip the base
call to disable the hook
[Accellera, uvm-core `uvm_callback.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_callback.svh).
The User's Guide's example does both: the driver "defines corresponding
virtual methods for each callback hook", and "The end-user may then define
either a callback or a driver subtype to extend driver's behavior"
[Accellera, UVM 1.2 User's Guide §6.3.2](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf).

**When to choose which.** The User's Guide's own guidance is restrictive:
"Callbacks may have a noticeable impact on performance, so they should only
be used when the desired functionality cannot be achieved in any other way"
[Accellera, UVM 1.2 User's Guide §6.3](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf).
The structural difference the chapter should teach: an override is a *type*
decision (one derived class, chosen once through the factory, one behavior
per instance), while callbacks are an *instance list* (several objects,
added and removed at run time, "iteratively invoke[d]" by the component
[§6.3.1](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf)).
Callbacks compose — two tests' hooks can both be registered — and overrides
do not; overrides are checked at compile time and callbacks are checked
when `add` is called, against the pairing declared with `` `uvm_register_cb ``
[Accellera, uvm-core `uvm_callback.svh`](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_callback.svh).
OpenTitan's base test registers a report catcher with
`uvm_report_cb::add(null, m_report_catcher)` to demote messages — a
cross-cutting change to a component the test does not own, which is the
case the callback form exists for
[lowRISC OpenTitan `dv_base_test.sv`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_lib/dv_base_test.sv).

### 9. What practitioners warn against

**Inheritance for reuse versus inheritance for substitution.** Liskov drew
the line in 1987: "subtype" and "supertype" mark "a semantic distinction",
whereas "subclass" and "superclass" "are simply linguistic concepts in
programming languages that allow programs to be built in a particular way",
which "can be used to implement subtypes, but also ... in other ways"
[Liskov, "Data abstraction and hierarchy", OOPSLA '87 Addendum, pp. 17–34, DOI 10.1145/62138.62141](https://doi.org/10.1145/62138.62141)
(text read from the [author's archived copy](https://www.cs.tufts.edu/~nr/cs257/archive/barbara-liskov/data-abstraction-and-hierarchy.pdf)).
The substitution property in her words: "If for each object o1 of type S
there is an object o2 of type T such that for all programs P defined in
terms of T, the behavior of P is unchanged when o1 is substituted for o2,
then S is a subtype of T" (same paper, §3.3). The 1994 formalization is
[Liskov & Wing, "A behavioral notion of subtyping", ACM TOPLAS 16(6):1811–1841, 1994, DOI 10.1145/197320.197383](https://doi.org/10.1145/197320.197383)
(record from Crossref; the paper's text is paywalled and was not read).
The Google C++ guide's operational version is the "is a kind of" test
quoted in §5.

**The principle applied to a transaction class.** The UVM factory's
precondition is the substitution property under another name: components
to be swapped "shall be polymorphically compatible"
[Accellera, UVM 1.2 User's Guide §6.2.1](https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf).
For a transaction, the "programs P defined in terms of T" are the driver,
the monitor, the scoreboard's `do_compare` and every sequence that
randomizes the item. A derived transaction that *adds a constraint* (the
User's Guide's `word_aligned_item`) keeps every program's behavior legal,
because every aligned item is a legal `simple_item`; a derived transaction
that *removes* a field's constraint, changes a field's meaning, or fails
`super.do_compare` is a subclass that is not a subtype, and the factory will
substitute it without complaint. lowRISC's requirement that a transaction
"Should result in a legal transaction when randomized"
[lowRISC DV style guide, Class Definitions §8](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md)
is the substitution property stated for the one program that matters most,
`randomize()`. This is the chapter's Definition callout for LSP, in
verification terms.

**Deep hierarchies.** The published warnings are about *implementation*
inheritance: Google's "code implementing a sub-class is spread between the
base and the sub-class" cost grows with every level
[Google C++ Style Guide, Inheritance](https://google.github.io/styleguide/cppguide.html#Inheritance),
and Spear and Tumbush's advanced-OOP chapter opens with the opposite
failure — "a large, flat class" that "is a maintenance burden, as anyone who
wants to make a new transaction behavior has to edit the same file" — and
the remedy "you should break classes down into smaller, reusable blocks"
[Spear & Tumbush, *SystemVerilog for Verification*, 3rd ed., Ch. 8 abstract, 2012](https://doi.org/10.1007/978-1-4614-0715-7_8).
The two warnings bound the chapter's advice from both sides: one flat class
and a six-deep tower are both wrong, and the production data point is that
OpenTitan's hierarchy is `uvm_component` → `uvm_driver` → `dv_base_driver`
→ one IP driver, with variation pushed into type parameters and
configuration objects rather than further subclasses (files in §1). The
chapter's Pitfall is inheritance used to *share code* between siblings that
are not substitutable — a `spi_driver extends uart_driver` because both
toggle a clock — and its fix is a shared helper class held by both, which is
§5.

**Language-level traps the chapter inherits from Part A and Chapter 5.**
Icarus's static dispatch of virtual methods (Chapter 5 note, Part C §4) is
the tool trap; the `super.<phase>` omission (§6 above) and the untyped
`new` that bypasses the factory (§3) are the two methodology traps a
reviewer should look for in every listing.

### 10. The Python track: the same problems without classes-as-feature

cocotb's own testbench guide contains no component classes, no factory and
no configuration database: a test is an `async` function marked with the
`@cocotb.test` decorator, "a special type of coroutine that is meant to
either pass or fail"
[cocotb, "Writing Testbenches", accessed 2026-09-11](https://docs.cocotb.org/en/stable/writing_testbenches.html).
The pattern-shaped facilities it does have are the standard library's:
selection of tests by name and generation of test variants come from a
decorator, `cocotb.parametrize`, which "will generate a test for each of the
Cartesian products of the parameters and their values", replacing the older
`TestFactory` ("Deprecated since version 2.0")
[cocotb library reference, "Marking and Generating Tests", accessed 2026-09-11](https://docs.cocotb.org/en/stable/library_reference.html).
Where the type-parameterized SystemVerilog base class fixes a type at
elaboration, a Python parameter is just a value passed at call time.

The template method survives the language change intact. cocotb-bus's
`Driver` is "the standard interface for a driver within a testbench",
`append` queues a transaction, and the hook is documented as "Sub-classes
should override this method to implement the actual send routine" —
`_driver_send`, whose base implementation raises
[cocotb-bus `drivers/__init__.py`, BSD-3-Clause, accessed 2026-09-11](https://github.com/cocotb/cocotb-bus/blob/master/src/cocotb_bus/drivers/__init__.py).
That is `dv_base_driver::get_and_drive` with the "must implement or fail at
runtime" note made explicit by the language.

pyuvm is the experiment that shows which patterns were about the *problem*
and which were about *SystemVerilog*. Its source comments say the factory's
registration machinery is "a SystemVerilog artifact": "any class that
extends uvm_void automatically gets registered into the factory" through a
metaclass, so "there is no need for 8.2.2 the type_id" nor for
`uvm_object_registry`
[pyuvm `src/pyuvm/_s08_factory_classes.py`, accessed 2026-09-11](https://github.com/pyuvm/pyuvm/blob/master/src/pyuvm/_s08_factory_classes.py);
`FactoryMeta.__init__` is one line, `FactoryData().classes[cls.__name__] = cls`
[pyuvm `src/pyuvm/_utility_classes.py`](https://github.com/pyuvm/pyuvm/blob/master/src/pyuvm/_utility_classes.py);
and `create` is a plain classmethod calling
`uvm_factory().create_object_by_type(cls, name=name)`
[pyuvm `src/pyuvm/_s05_base_classes.py`](https://github.com/pyuvm/pyuvm/blob/master/src/pyuvm/_s05_base_classes.py).
The README states the trade directly: "Python does not have strict typing
and does not require parameterized classes", "The `ConfigDB()` singleton
acts the same way as the `uvm_config_db`", and "pyuvm refactored away the
`uvm_resource_db`"
[pyuvm README, accessed 2026-09-11](https://github.com/pyuvm/pyuvm/blob/master/README.md).
So: the factory, the singleton config database and the template-method
phases survive translation (they are about the testbench); `type_id`, the
registry proxies, the `_param_utils` split and the per-specialization
`config_db` pools do not (they are about the language). That is the
chapter's closing contrast, and it is the cleanest way to tell the reader
which of the section's rules are portable.

### Unsourced-claims table

| Claim in this note | Status | What would source it |
|---|---|---|
| Gamma et al. state "Favor object composition over class inheritance" as a design principle in their introduction (§5) | From memory of the book; only the publisher's record and table of contents were read | The book itself, 1st ed., Ch. 1 (the principle is stated in the section on inheritance versus composition) |
| Factory Method, Strategy, Template Method and Singleton are each one of the twenty-three patterns, in the creational/behavioral groups named (§3, §4, §6, §7) | The publisher's record confirms the three groups and the count of 23; the assignment of each pattern to a group is from memory | Same |
| Cummings & Chambers, SNUG SV 2012 factory paper: title and venue (§3) | Title and venue read from the authors' library listing; the paper's text was not consulted (no PDF link on the page) | The PDF, if the chapter wants to cite its argument rather than its existence |
| Liskov & Wing 1994: bibliographic record (§9) | Crossref record only; ACM DL returned 403 | The paper, for any quotation |
| Bloch, *Effective Java*, "Favor composition over inheritance" (Item 18, 3rd ed.) | Publisher's record confirms the book; the item title is from memory and is *not* used in the note's text | Not needed unless the chapter cites it |
| "Icarus 13.0 rejects `class fifo #(`", "Verilator runs parameterized classes", "Icarus dispatches virtual methods statically" (§1, §2, §9) | Measured in the Chapter 5 research note (Part C §1, §4), not re-measured here | Re-running the Chapter 5 probes when Chapter 6's examples are built |
| A `$cast` between two specializations of the same parameterized class fails (§2 (ii)) | Follows from the distinct-type rule of IEEE 1800-2023 8.25 as Chapter 5's note records it (Verilator cites the clause); not executed here | A two-line Verilator probe in the Chapter 6 example set |
| OpenTitan's IP-level drivers are one level below `dv_base_driver` (§9) | Inferred from `dv_base_agent`'s parameter comments and the base-class files read; no IP driver file was opened | Open one, e.g. `hw/dv/sv/uart_agent/uart_driver.sv` |

### Key sources

Keys reuse existing `refs.bib` entries where they exist (`lowrisc-dv-style`,
`spear2012svfv`, `cocotb-docs`, `ieee1800-2023`); the rest are new.

```bibtex
@book{gamma1994patterns,
  author    = {Erich Gamma and Richard Helm and Ralph Johnson and John Vlissides},
  title     = {Design Patterns: Elements of Reusable Object-Oriented Software},
  edition   = {1},
  publisher = {Addison-Wesley},
  address   = {Reading, MA},
  year      = {1994},
  isbn      = {978-0-201-63361-0},
  url       = {https://www.informit.com/store/design-patterns-elements-of-reusable-object-oriented-9780201633610},
  note      = {Cited by edition; publisher's record accessed 2026-09-11}
}

@misc{accellera2015uvmug,
  author       = {{Accellera Systems Initiative}},
  title        = {Universal Verification Methodology ({UVM}) 1.2 User's Guide},
  howpublished = {Accellera},
  year         = {2015},
  url          = {https://www.accellera.org/images/downloads/standards/uvm/uvm_users_guide_1.2.pdf},
  note         = {Dated 2015-10-08. Accessed 2026-09-11}
}

@misc{accellera2015uvmref,
  author       = {{Accellera Systems Initiative}},
  title        = {Universal Verification Methodology ({UVM}) 1.2 Class Reference},
  howpublished = {Accellera},
  year         = {2015},
  url          = {https://www.accellera.org/images/downloads/standards/uvm/UVM_Class_Reference_Manual_1.2.pdf},
  note         = {Accessed 2026-09-11}
}

@misc{ieee1800.2-2020,
  author       = {{IEEE}},
  title        = {{IEEE} Std 1800.2-2020, {IEEE} Standard for Universal
                  Verification Methodology Language Reference Manual},
  howpublished = {IEEE Standards Association},
  year         = {2020},
  url          = {https://standards.ieee.org/ieee/1800.2/7567/},
  note         = {Approved 2020-06-04, published 2020-09-14. Available at no
                  cost through the IEEE GET program courtesy of Accellera
                  (\url{https://www.accellera.org/downloads/ieee}). Clause
                  numbers in this note are those the uvm-core sources annotate
                  (\texttt{@uvm-ieee 1800.2-2020 auto}); the text itself was
                  not consulted. Accessed 2026-09-11}
}

@misc{uvm-core,
  author       = {{Accellera Systems Initiative}},
  title        = {{UVM} Core Library ({uvm-core}), {IEEE} 1800.2-2020 reference implementation},
  howpublished = {GitHub, accellera-official/uvm-core},
  year         = {2026},
  url          = {https://github.com/accellera-official/uvm-core},
  note         = {Apache-2.0. Files cited: src/base/uvm\_factory.svh,
                  uvm\_registry.svh, uvm\_object.svh, uvm\_policy.svh,
                  uvm\_callback.svh, uvm\_component.svh, uvm\_root.svh,
                  uvm\_coreservice.svh, uvm\_config\_db.svh,
                  src/comps/uvm\_driver.svh, src/seq/uvm\_sequence\_base.svh,
                  src/macros/uvm\_sequence\_defines.svh. Accessed 2026-09-11}
}

@misc{opentitan-dv-lib,
  author       = {{lowRISC contributors (OpenTitan project)}},
  title        = {{OpenTitan} {DV} base library: \texttt{dv\_lib} and \texttt{dv\_base\_agent}},
  howpublished = {GitHub, lowRISC/opentitan, hw/dv/sv/dv\_lib and hw/dv/sv/dv\_base\_agent},
  year         = {2026},
  url          = {https://github.com/lowRISC/opentitan/tree/master/hw/dv/sv/dv_lib},
  note         = {Apache-2.0. Files cited: dv\_base\_env.sv, dv\_base\_test.sv,
                  dv\_base\_scoreboard.sv, dv\_base\_vseq.sv,
                  dv\_base\_agent/dv\_base\_agent.sv, dv\_base\_driver.sv.
                  Accessed 2026-09-11}
}

@inproceedings{liskov1987hierarchy,
  author    = {Barbara Liskov},
  title     = {Data Abstraction and Hierarchy},
  booktitle = {Addendum to the Proceedings on Object-Oriented Programming
               Systems, Languages and Applications (OOPSLA '87 Addendum)},
  publisher = {ACM},
  year      = {1987},
  pages     = {17--34},
  doi       = {10.1145/62138.62141},
  url       = {https://doi.org/10.1145/62138.62141},
  note      = {Keynote address. Accessed 2026-09-11}
}

@article{liskov1994subtyping,
  author  = {Barbara H. Liskov and Jeannette M. Wing},
  title   = {A Behavioral Notion of Subtyping},
  journal = {ACM Transactions on Programming Languages and Systems},
  volume  = {16},
  number  = {6},
  pages   = {1811--1841},
  year    = {1994},
  doi     = {10.1145/197320.197383},
  url     = {https://doi.org/10.1145/197320.197383},
  note    = {Record from Crossref; accessed 2026-09-11}
}

@misc{google-cpp-style,
  author       = {{Google}},
  title        = {Google {C++} Style Guide},
  howpublished = {google.github.io/styleguide},
  year         = {2026},
  url          = {https://google.github.io/styleguide/cppguide.html#Inheritance},
  note         = {Section ``Inheritance''. Accessed 2026-09-11}
}

@misc{cummings2012factory,
  author       = {Clifford E. Cummings and Heath Chambers},
  title        = {The {OVM/UVM} Factory \& Factory Overrides: How They Work --
                  Why They Are Important},
  howpublished = {SNUG Silicon Valley},
  year         = {2012},
  url          = {https://www.paradigm-works.com/papers/},
  note         = {Listed in the authors' technical library (rev. 1.2,
                  January 2013); text not consulted. Accessed 2026-09-11}
}

@misc{cocotb-bus,
  author       = {{cocotb contributors}},
  title        = {cocotb-bus: pre-packaged testbenching tools and reusable bus interfaces for cocotb},
  howpublished = {GitHub, cocotb/cocotb-bus},
  year         = {2026},
  url          = {https://github.com/cocotb/cocotb-bus/blob/master/src/cocotb_bus/drivers/__init__.py},
  note         = {BSD-3-Clause. Accessed 2026-09-11}
}

@misc{pyuvm,
  author       = {Ray Salemi and {pyuvm contributors}},
  title        = {pyuvm: the {UVM} written in Python},
  howpublished = {GitHub, pyuvm/pyuvm},
  year         = {2026},
  url          = {https://github.com/pyuvm/pyuvm},
  note         = {Files cited: README.md, src/pyuvm/\_s08\_factory\_classes.py,
                  \_s05\_base\_classes.py, \_utility\_classes.py.
                  Accessed 2026-09-11}
}
```

### Confidence notes

- **High.** Every quotation from the UVM 1.2 User's Guide and Class
  Reference was read in the PDFs downloaded from accellera.org on
  2026-09-11 (section numbers are the documents' own). Every uvm-core,
  OpenTitan, lowRISC style-guide, cocotb-bus and pyuvm quotation was read
  in the file at the URL given, on the default branch, the same day; none
  is pinned to a commit, so a reader checking later should expect drift in
  line positions but not, so far, in the quoted comments.
- **High.** Liskov 1987: the substitution-property sentence and the
  subtype/subclass distinction were read from the archived PDF (§3.3);
  the DOI record was confirmed through Crossref.
- **Medium.** IEEE 1800.2-2020 clause numbers (8.3.1 factory, 10.7
  callbacks, 13.1.4 phases, 14.2.3 sequences, 16.1 policies, F.4
  coreservice) are taken from the `@uvm-ieee 1800.2-2020 auto` annotations
  in uvm-core, not from the standard's text. The standard is free through
  the IEEE GET program and should be checked before the chapter cites a
  clause.
- **Medium.** Gamma et al.: bibliographic record confirmed; pattern
  definitions in §3–§7 are written from understanding and attributed to the
  book only by edition, as the task requires. The "favor composition"
  principle is in the unsourced table.
- **Low.** Cummings & Chambers 2012 and Liskov & Wing 1994 are cited for
  existence only.
- **Author's attention.** The lowRISC rule "parameters representing types
  must not be used" in `type_id::create()` (Factory §3) is contradicted by
  OpenTitan's own base classes (`SCOREBOARD_T::type_id::create`,
  `MONITOR_T::type_id::create`). The note reads the rule as applying to
  IP-level code; if the chapter quotes the rule it should say so, or the
  chapter will be teaching a rule its own production example breaks.
- **Length.** The note runs longer than the ~3,000-word target because
  every claim carries an inline URL; the prose alone is close to the
  target.

---

# Part C — What the open tools run of the object-oriented language, measured

Scope: for every object-oriented construct Chapter 6 teaches — `extends`
and constructor chaining, method hiding, virtual dispatch in every shape a
testbench uses it, abstract and interface classes, `$cast`, copy and clone
conventions, parameterized classes, and the factory, singleton and callback
patterns built from them — what the book's two open simulators compile, run
and print. Two kinds of evidence are kept apart throughout: **documented**
support, quoted from the tools' own files with a dated URL, and **measured**
support, from one probe per construct run on this machine with the book's
own runner and cited as "measured, this note, <tool> <version>". Where they
disagree, the measurement decides whether the chapter can ship the example,
and the disagreement is recorded in §3.

This part extends Part C of the Chapter 5 note
(`research/ch05-testbench-language.md`), which measured 57 probes of the
whole testbench language and found one object-oriented silent failure: an
Icarus virtual call through a base handle runs the base body. This note
characterizes that failure fully, finds the tracker record that explains it,
and adds a second silent failure the Chapter 5 sweep did not reach — on
Verilator, and on a construct the chapter's `clone()` section would
otherwise use.

### The two findings that decide the chapter

1. **Icarus Verilog 13.0 does not implement virtual methods at all.** Every
   call is bound to the *declared type of the handle expression*, never to
   the object. The project said so itself in 2020: "The virtual keyword is
   accepted by the parser, but otherwise ignored. This is also true for
   virtual methods" [iverilog #421, comment of 2020-12-14](https://github.com/steveicarus/iverilog/issues/421),
   and again in 2023: "This is not yet working ... Especially support for
   virtual methods since that requires changes in vvp as well" [iverilog
   #292, comment of 2023-01-16](https://github.com/steveicarus/iverilog/issues/292).
   Twenty probes in §1 agree with that sentence in every shape (measured,
   this note, Icarus 13.0). Icarus also refuses, at compile time, to call a
   method on, or read a property of, an object held in a class property —
   so it cannot run *composition* either. Every polymorphism example in
   Chapter 6 therefore runs on Verilator only, and the chapter must say so
   with the mechanism, because the Icarus build prints a plausible number
   and no warning.
2. **Verilator 5.030 has one silent wrong result in this territory: the
   shallow copy `c = new b` builds an object of the handle's declared type,
   not the source object's type, so a virtual call on the copy reaches the
   base body.** The project fixed this on 2026-02-22 [Verilator #7105](https://github.com/verilator/verilator/issues/7105),
   sixteen months after the 5.030 release the book installs. The chapter's
   copy/clone section must build `clone()` as a virtual method that calls
   `new` on its own class — the convention the chapter would teach anyway
   — and must not present `new src` as a polymorphic copy. A second,
   smaller disagreement — a virtual method called from the *base*
   constructor runs the base body on both tools — is recorded in §2 with
   its reading of the standard flagged as unverified.

Everything else the chapter needs — constructor chaining, hiding, every
shape of virtual dispatch, abstract and interface classes, `$cast` in both
outcomes, parameterized classes with type and value parameters, static
members of specializations, `this` passed out, factories, singletons,
callbacks — runs on Verilator 5.030 with the book's flags, with a lint
warning to suppress on three rows (measured, this note, Verilator 5.030).

### Tool versions and flags used for every measurement

| Tool | Version string, as printed | Path |
|---|---|---|
| Verilator | `Verilator 5.030 2024-10-27 rev UNKNOWN.REV` | `/opt/homebrew/bin/verilator` |
| Icarus Verilog | `Icarus Verilog version 13.0 (stable) (v13_0)` | `/opt/homebrew/bin/iverilog`, `/opt/homebrew/bin/vvp` |

Versions were read with `verilator --version` and `iverilog -V` (measured,
this note, 2026-09-11). No `z3` is on PATH, which matters for nothing in
this part: none of the probes randomizes.

The runner is a verbatim copy of the book's
`examples/ch05-testbench-language/support-matrix/matrix.py` (only the table
label changed), so the four verdicts are the book's own: **runs** —
compiled, ran, printed `PROBE <name> PASS` after checking every value;
**wrong** — compiled, ran to `$finish`, printed `FAIL` because a value was
not what the standard requires; **no run** — compiled, then failed at run
time; **no build** — did not compile, with the first line of the tool's
error kept. Verilator is invoked as `--binary --timing --timescale 1ns/1ps
-Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-fatal --top-module top`;
Icarus as `iverilog -g2012` then `vvp`. The `-Wno-fatal` is the runner's
own choice, so that a lint warning does not read as a refusal; §4 lists
which probes warn under the book's fatal flags. The 51 probes, `probes.txt`
and the runner copy are in the session scratchpad under `ch06-probes/`, and
are written so that they can be dropped into a Chapter 6 `support-matrix/`
example unchanged.

### 1. The support matrix

##### 1.1 How to read it

Every cell is a measured result from the runner described above (measured,
this note, Verilator 5.030 and Icarus 13.0, 2026-09-11). The probe id in
parentheses names the file in `ch06-probes/probes/`. "Printed" gives the
value the tool printed where the verdict is **wrong**, and the first line
of the tool's own diagnostic where it is **no build** or **no run**, cut as
the runner cuts it. Rows marked *negative* are probes whose *correct*
outcome is a refusal: they measure diagnostics, not support, and are kept
out of the counts. The runner's headline for the 51 rows, including the
two negatives, is: **7 run on both, 39 on Verilator only, 0 on Icarus
only, 5 on neither.**

##### 1.2 Inheritance, constructors and hiding

| Construct (probe) | Icarus 13.0 `-g2012` | Verilator 5.030 `--timing` | Printed / documented |
|---|---|---|---|
| `extends` with an explicit `super.new(args)` (o01) | runs | runs | Verilator Changes 5.004: "Support super.new calls" |
| `extends` with the implicit `super.new()` and a base default argument (o02) | runs | runs | Verilator Changes 5.014: "Fix implicit calls of base class constructors with optional arguments" |
| `super.new()` called with a local variable of the derived constructor (o45) | runs | runs | Verilator #6214 reports this shape failing under `-O0`/`-fno-life` in later versions; not reproduced with the book's flags |
| three-level constructor chain, base has a default `string` argument (o46) | runs | runs | shape of Verilator #6036; runs on 5.030 as installed |
| non-virtual method hidden in the derived class, called through a base handle (o03) | runs | runs | base body through the base handle, derived through the derived: both correct |
| `protected` property read from a derived method (o32) | runs | runs | — |

##### 1.3 Virtual dispatch, in every shape a testbench uses it

| Construct (probe) | Icarus 13.0 | Verilator 5.030 | Printed |
|---|---|---|---|
| virtual `int` function through a base handle (o04) | **wrong** | runs | Icarus `via_base=1 via_derived=2`, expected 2 and 2 |
| virtual task with an `output` argument through a base handle (o05) | **wrong** | runs | Icarus `via_base=1 via_derived=2` |
| virtual `void` function setting a property, through a base handle (o06) | **wrong** | runs | Icarus `v=1`, expected 2 |
| override calling `super.f()`, through a base handle (o07) | **wrong** | runs | Icarus `via_base=10 via_derived=11`, expected 11 and 11 |
| `super.f()` chained through two levels, through the root handle (o28) | **wrong** | runs | Icarus `via_a=1`, expected 111 |
| three levels, through root and middle handles holding the leaf (o08) | **wrong** | runs | Icarus `via_a=1 via_b=2 via_c=3`, expected 3, 3, 3 — the middle handle gives the *middle* body |
| across a level that does not override (o10) | **wrong** | runs | Icarus `a_holding_c=1 a_holding_b=1`, expected 3 and 1 |
| override declared without repeating `virtual` (o27) | **wrong** | runs | Icarus `via_base=1`, expected 2 |
| virtual call from a non-virtual base method, on the derived handle and on the base handle (o09) | **wrong** | runs | Icarus `run_via_derived=100 run_via_base=100`, expected 200 and 200 — wrong even on the *derived* handle |
| virtual call from a base task after a delay (o33) | **wrong** | runs | Icarus `r=1`, expected 2 |
| virtual call on a base-typed function argument (o39) | **wrong** | runs | Icarus `f=1`, expected 2 |
| virtual calls inside `fork ... join`, two handles, two derived types (o24) | **wrong** | runs | Icarus `r1=0 r2=0`, expected 1 and 2 |
| one base handle reassigned between two derived objects (o43) | **wrong** | runs | Icarus `r1=0 r2=0`, expected 1 and 2 |
| callback hook: virtual call on the hook handle from the module (o34b) | **wrong** | runs | Icarus `sent=4`, expected 5 |
| virtual call through a base-typed property of another object, `h.item.f()` (o38) | no build | runs | Icarus `sorry: Method name nesting is not supported yet.` |
| callback hook called from inside the driver's method, `cb.on_send(v)` (o34) | no build | runs | Icarus `sorry: Method name nesting is not supported yet.` |
| virtual call from the **derived** constructor after `super.new()` (o26c) | runs | runs | both print `seen=100` |
| virtual call from the **base** constructor, override returns a constant (o26b) | **wrong** | **wrong** | both print `seen=1`; see §2.3 for why "wrong" is this note's reading, not yet the standard's text |
| same, override reads a derived property with an initializer (o26) | **wrong** | **wrong** | both print `seen=1` |

##### 1.4 Abstract classes, interface classes, `$cast`, copy and clone

| Construct (probe) | Icarus 13.0 | Verilator 5.030 | Printed / documented |
|---|---|---|---|
| `virtual class` with a `pure virtual` method, called through the abstract handle (o11) | no build | runs (lint: `UNDRIVEN` on the pure-virtual name) | Icarus `syntax error` / `Invalid class item.`; Icarus PR #469 "parse-only support for pure virtual methods" open since 2021 |
| `interface class` and `implements` (o12) | no build | runs (lint: `UNDRIVEN`) | Icarus `syntax error` / `I give up.`; Verilator Changes 5.008: "Support interface classes and class implements" |
| one class implementing two interface classes (o13) | no build | runs (lint: 2× `UNDRIVEN`) | Verilator Changes 5.022: "Fix compilation error on multi-inherited interface class usage" |
| `$cast` down the hierarchy, matching object (o14) | no run | runs | Icarus `vvp`: `System task/function $cast() is not defined by any module.`; Icarus PR #1447 closed **unmerged** 2026-07-21 |
| `$cast` function form on a mismatched object: returns 0, target stays `null` (o15) | no run | runs | same Icarus message; Verilator `ok=0 y_null=1` |
| shallow copy `new src`, scalar copied, inner handle shared (o16, o16b) | no build | runs | Icarus `sorry: Nested member path not yet supported for class properties.` (o16b keeps every path inside methods and fails the same way) |
| shallow copy `new src` through a **base handle holding a derived object** (o44) | no run | **wrong** | Icarus `vvp` aborts: `Assertion failed: (defn_ == that->defn_), function shallow_copy, file vvp_cobject.cc, line 83.`; Verilator `copy_f=1`, expected 2 — see §2.2 |
| `copy()`/`clone()` convention: virtual `clone()` returning a base handle, derived override, `$cast` of the result (o17) | no build | runs | Icarus `SORRY: Compare class handles not implemented` (and `$cast`) |
| handle identity `a == b`, `a != c`, `a != null` (o40) | no build | runs | Icarus `SORRY: Compare class handles not implemented` — handle-to-handle comparison; `!= null` alone ran in the Chapter 5 sweep |

##### 1.5 Parameterized classes

| Construct (probe) | Icarus 13.0 | Verilator 5.030 | Printed / documented |
|---|---|---|---|
| type parameter `#(type T = int)`, two specializations (o18) | no build | runs | Icarus `syntax error` at the `class … #(` line; Icarus #291 "Parameterized class not supported" open since 2019 |
| value parameter sizing a property (o19) | no build | runs | Verilator manual: "class parameters" supported |
| the same class specialized twice, both alive (o20) | no build | runs | — |
| class extending a value-specialized base, virtual call still dispatches (o21) | no build | runs | Verilator Changes 5.010: "Support parameterized class references in extends statement" |
| class extending a type-specialized base (o35) | no build | runs | — |
| static member of a specialization: `counter#(1)::count` and `counter#(2)::count` separate (o22) | no build | runs (lint: `UNUSEDPARAM`) | Verilator Changes 5.008: "Fix static members of type aliases of a parameterized class" |
| class handle held by a parameterized container, `box #(pkt)` (o23) | no build | runs | — |

##### 1.6 Composition and the patterns the chapter builds

| Construct (probe) | Icarus 13.0 | Verilator 5.030 | Printed / documented |
|---|---|---|---|
| method called on a handle property from inside a method, `item.f()` (o41) | no build | runs | Icarus `sorry: Method name nesting is not supported yet.` |
| method called through a property chain from the module, `h.item.f()` (o42) | no build | runs | same |
| `this` passed to another object and stored as a back-pointer (o25, o25b) | no build | runs | Icarus `sorry: Nested member path not yet supported for class properties.` on `parent.tag` *inside* the child's method, plus `Method name nesting` on `c.attach(this)` |
| queue of base handles iterated with a virtual call (o29) | no build | runs | Icarus `Sorry: Queue of type \`class base{}\` is not yet supported.`; Icarus PR #1416 "class queue/darray property foundation" merged 2026-07-12, after 13.0 |
| factory: static function selecting the derived type by a string, forward `typedef class` (o30) | no build | runs | Icarus `syntax error` / `Malformed statement` at `base::make(…)` |
| singleton: static handle and static `get()` via `cfg::get()` (o31) | no build | runs | Icarus `syntax error` / `Malformed statement` at `cfg::get()` |

##### 1.7 Negative probes: is the diagnostic right?

| Construct (probe) | Icarus 13.0 | Verilator 5.030 | Printed |
|---|---|---|---|
| `new` on a `virtual class` — must be refused (o36) | no build, for the wrong reason | no build, correctly | Icarus fails on `pure virtual` before it can judge the `new`; Verilator: `Illegal to call 'new' using an abstract virtual class 'shape' (IEEE 1800-2023 8.21)` |
| `$cast` as a task on a mismatched object — must raise a runtime error (o37) | no run, for the wrong reason | no run, correctly | Icarus: `$cast()` undefined; Verilator: `%Error: … Assertion failed in top: 'assert' failed.` then `$stop` |

##### 1.8 Headline

- **Runs on both, unchanged:** `extends`, explicit and implicit `super.new`
  chains including a local-variable argument and a three-level chain with a
  default argument, non-virtual hiding, `protected`, and a virtual call
  made from the derived constructor. Seven rows.
- **Runs on Verilator only:** every virtual-dispatch shape (fourteen rows
  wrong on Icarus, two more refused), abstract and interface classes,
  `$cast` in both outcomes, `new src` on a same-typed handle, the
  `copy()`/`clone()` convention, handle comparison, every parameterized-
  class row, every composition row, the queue-of-base-handles loop, the
  factory and the singleton. Thirty-nine rows.
- **Runs on Icarus only:** none.
- **Wrong on both:** a virtual method called from the *base* constructor,
  in both variants; see §2.3 for the standing of that expectation.
- **Silent wrong results a status-only check would miss:** fourteen
  dispatch cells on Icarus, all one mechanism; one cell on Verilator
  (`new src` through a base handle); and the constructor pair on both.
  §2 is the catalog.

### 2. Catalog of silent wrong results

A silent wrong result is a cell where the tool builds, runs to `$finish`,
exits zero, prints no warning, and prints a value the language does not
permit. These are the cells that matter most to a chapter, because a
reader who follows the book's recipe sees output and believes it.

##### 2.1 Icarus 13.0: virtual methods are bound to the declared type of the handle

**Cells.** o04, o05, o06, o07, o08, o09, o10, o24, o27, o28, o33, o34b,
o39, o43 (fourteen matrix rows), plus o26 and o26b, which are wrong on both
tools and treated in §2.3. In every one the build is clean, `vvp` runs to
`$finish`, and the value printed is the one the base body — or more
precisely, the body belonging to the handle's declared class — produces
(measured, this note, Icarus 13.0).

**Mechanism, inferred from the behavior.** Three probes separate the
candidate explanations:

- o08 declares handles of the root, middle and leaf types and points all
  three at one leaf object. It prints `via_a=1 via_b=2 via_c=3`. So the
  method chosen is not "always the base" and not "the most recent override
  below the handle's type"; it is the method of the handle's *declared*
  class, exactly as if the `virtual` keyword were absent.
- o09 calls a non-virtual `run()` on the *derived* handle; `run()` calls
  `step()`, which the derived class overrides. It prints `100`, the base
  `step()`. Inside `run()` the implicit `this` is declared as the base
  class, so the rule above predicts the base body, and that is what
  appears. The template-method pattern is therefore wrong on Icarus even
  when no base handle exists anywhere in the test.
- o26c calls a virtual method from the *derived* constructor and gets the
  derived body: `this` is declared derived there. The same rule again.

The rule "bind to the declared type" explains all sixteen printed values,
including o24 and o43 (`r1=0 r2=0`: the handle is declared `base`, whose
`f()` returns 0) and o10 (`a_holding_b=1` is right by coincidence: the
declared type and the object's nearest override are both `a`).

**The project's own record.** The behavior is not a bug the project is
unaware of; it is a feature it has said, in the tracker, that it has not
implemented. On issue #421, "SV: abstract class not working as expected"
(opened 2020-12-13, closed 2022-12-17), a maintainer wrote on 2020-12-14:
"There is currently no support for abstract classes. The virtual keyword is
accepted by the parser, but otherwise ignored. This is also true for
virtual methods" [iverilog #421](https://github.com/steveicarus/iverilog/issues/421).
On issue #292, "Issue in calling class methods" (opened 2019-12-27, still
open), a maintainer wrote on 2023-01-16: "This is not yet working. We'll
get there, but it will take some time. Especially support for virtual
methods since that requires changes in vvp as well" [iverilog #292](https://github.com/steveicarus/iverilog/issues/292).
The searches "virtual method", "polymorphism", "dispatch class", "virtual
dispatch" and "virtual function" over the repository's issues and pull
requests (GitHub search API, 2026-09-11) found no issue whose title names
virtual dispatch as wrong, and no pull request that implements it; the
open pull request #469 adds parse-only support for `pure virtual` [iverilog
PR #469, 2021-01-04](https://github.com/steveicarus/iverilog/pull/469), and
the adjacent open issue #422 is about assigning a derived handle to a base
one, which 13.0 now accepts [iverilog #422, 2020-12-13](https://github.com/steveicarus/iverilog/issues/422).
The 2020 comment is the closest thing to documentation of the behavior;
the README's own "too large to enumerate" sentence [iverilog README,
v13-branch](https://github.com/steveicarus/iverilog/blob/v13-branch/README.md)
is the only statement in the shipped documentation.

**What a chapter can do with it.** Nothing in Icarus 13.0 can be switched
on to get virtual dispatch. The chapter's examples that depend on it are
Verilator-only, and the Icarus row of the matrix is itself the best
illustration the chapter has of why "it ran" is not "it is right".

##### 2.2 Verilator 5.030: `new src` copies the declared type, not the object

**Cell.** o44: `base b = d; base c = new b; c.f()` prints `copy_f=1`, the
base body; the source object is a `derived` whose `f()` returns 2. The
same-typed copy (o16) is correct: scalars copied, inner handle shared
(measured, this note, Verilator 5.030).

**Mechanism.** The project's own issue #7105, "Fix new <obj> shallow copy
not preserving polymorphic runtime type" (opened 2026-02-19, closed
2026-02-22), states it: "The shallow copy constructor `copy = new
source_handle` creates an object of the **declared variable type** instead
of the **actual runtime type** of the source object", quoting IEEE
1800-2017 §8.7, "The new object has the same type as the source object",
and notes the impact on "riscv-dv instruction template registry uses `new
instr_template[name]` for polymorphic copies" [Verilator #7105](https://github.com/verilator/verilator/issues/7105).
The maintainer's reply proposes "a virtual clone() method to VlClass"
generated per class, which is the C++ mechanism 5.030 lacks. The fix
postdates the 5.030 release of 2024-10-27 by sixteen months, so the book's
installed Verilator has the defect and a reader who installs the same
5.030 has it too.

**What a chapter can do with it.** Teach `clone()` as a virtual method
whose every override does `<own class> p = new; p.copy(this); return p;`
(o17, which runs correctly on Verilator 5.030), and never `new this` or
`new src` as the polymorphic copy. Say why: the language guarantees `new
src` keeps the object's type, but the book's Verilator does not until a
release made after 2026-02-22, and a reader's UVM-style factory that copies templates
with `new` will quietly produce base objects.

##### 2.3 Both tools: a virtual call from the base constructor runs the base body

**Cells.** o26b (override returns a constant) and o26 (override reads a
derived property with an initializer) print `seen=1` on both tools; the
derived override returns 100 (measured, this note, Verilator 5.030 and
Icarus 13.0). On Icarus the result follows from §2.1 (`this` inside the
base constructor is declared `base`). On Verilator it is a deliberate or
inherited C++ semantics: a C++ virtual call made during a base-class
constructor binds to the base version, and Verilator emits its classes as
C++ classes with the base constructor invoked from the derived one's
initializer list, as the generated code quoted in Verilator #6214 shows
[Verilator #6214, 2025-07-22](https://github.com/verilator/verilator/issues/6214).

**Standing of the expectation.** This note's reading is that SystemVerilog
has no separate "under construction" type: the object is of its final
class from `new` onward, and a virtual call resolves to the latest
override wherever it is made — a reading consistent with #7105's quotation
of §8.7 and with the two tools' *own* correct behavior in o26c, where the
call is made one frame later. The book has not consulted the clause text
(`refs.bib` records IEEE 1800-2023 as "paywalled; clause text not
consulted"), so this row is entered as **wrong on this note's reading, not
yet established**, and appears in the unsourced-claims table. The
chapter's guidance does not depend on resolving it: calling a virtual
method from a constructor is a design smell in every object language, and
the derived object's properties have not been initialized when the base
constructor runs (o26 prints 1, not 105, on both tools), so the chapter
should teach "do not do this" and, if it shows the trap, say that the two
open tools agree with each other and that the standard's clause should be
checked before asserting what a commercial simulator prints.

##### 2.4 Cells that are not silent

For completeness, the cells where a tool is wrong but *says so*: every
Icarus "no build" row prints `sorry:` or `syntax error` and produces no
`vvp` file; both Icarus "no run" rows for `$cast` stop `vvp` before time
zero with `Program not runnable`; the Icarus o44 row aborts `vvp` with an
assertion; Verilator's o36 and o37 refusals cite the standard's clause and
`$stop` respectively. A check that looks only at the exit status catches
all of these. The count of silent cells is therefore **Icarus 16 (fourteen
dispatch shapes and the constructor pair), Verilator 3 (the shallow copy
and the constructor pair), for 16 distinct constructs** once o26 and o26b
are counted as one.

### 3. Documented support, and where it disagrees with the measurement

##### 3.1 Verilator 5.030

The release-tagged manual has two sentences on classes. Under the 2005
keyword list: "Verilator has limited support for class and related
object-oriented constructs." Under Language Limitations, the whole "Class"
entry: "Verilator class support is limited but in active development.
Verilator supports members, methods, class extend, and class parameters"
[Verilator languages.rst, v5.030, 2024-10-27](https://github.com/verilator/verilator/blob/v5.030/docs/guide/languages.rst).
Nothing in the manual names virtual methods, abstract classes, interface
classes, `$cast` or shallow copy, so for those the change log is the
documentation. Entries in the log that bear on this note's rows, with the
release each sits under [Verilator Changes, v5.030](https://github.com/verilator/verilator/blob/v5.030/Changes):
"Support class static members" (4.218); "Support class parameters" (4.226);
"Support standalone 'this' in classes" (5.002); "Support super.new calls"
(5.004); "Support class queue equality" and "Fix chain call of abstract
class constructor" (5.006); "Support interface classes and class
implements", "Fix static members of type aliases of a parameterized class"
(5.008); "Support parameterized class references in extends statement"
(5.010); "Fix implicit calls of base class constructors with optional
arguments", "Fix comparison of class objects", "Fix handling of super.new
calls" (5.014); "Fix virtual methods (#4616)", "Fix class name in error on
'new' on virtual class" (5.018); "Fix compilation error on multi-inherited
interface class usage" (5.022); "Add error on missing pure virtual
functions", "Support 1800-2023 class and function :initial, :extends,
:final virtual overrides" (5.024).

**Where documentation and measurement disagree.**

- The manual's "limited" undersells the measurement: 46 of the 49
  non-negative rows run; the three that do not are the shallow copy the
  project has since fixed and the constructor pair of §2.3. A chapter that quoted the manual's sentence as
  the state of Verilator's classes would be wrong in the pessimistic
  direction.
- No entry in the 5.030 log mentions `new <handle>` polymorphic copies;
  the defect in §2.2 is documented only by the 2026 issue that fixed it.
- The manual says nothing about calling a virtual method from a
  constructor; §2.3 stands on measurement alone.
- The `UNDRIVEN` warning on a `pure virtual` prototype (o11, o12, o13) is
  the lint being wrong about a construct the language supports; the
  manual's description of `UNDRIVEN` as "relatively liberal in the usage
  calculations" is the closest acknowledgement [Verilator warnings.rst,
  v5.030](https://github.com/verilator/verilator/blob/v5.030/docs/guide/warnings.rst).
  `UNUSEDPARAM` on o22 is correct as far as it goes: the specialization's
  parameter `K` exists only to make two types.

##### 3.2 Icarus Verilog 13.0

The README says the compiler "also compiles a (slowly growing) subset of
the SystemVerilog language" and that "The list of unsupported
SystemVerilog constructs is too large to enumerate here" [iverilog README,
v13-branch](https://github.com/steveicarus/iverilog/blob/v13-branch/README.md);
the v13.0 release note does not mention classes [iverilog v13.0 release,
2026-03-02](https://github.com/steveicarus/iverilog/releases/tag/v13_0).
The tracker supplies what the README does not:

| Construct | Tracker record | State on 2026-09-11 |
|---|---|---|
| virtual methods | #421 comment: "The virtual keyword is accepted by the parser, but otherwise ignored. This is also true for virtual methods." [2020-12-14](https://github.com/steveicarus/iverilog/issues/421); #292 comment: "support for virtual methods ... requires changes in vvp as well" [2023-01-16](https://github.com/steveicarus/iverilog/issues/292) | #421 closed 2022-12-17 without the feature; #292 open |
| `pure virtual`, `virtual class` | PR #469 "Added parse-only support for pure virtual methods" [2021-01-04](https://github.com/steveicarus/iverilog/pull/469) | open, unmerged |
| `local`/`protected` combined with `virtual` | issue #1061 [2024-01-04](https://github.com/steveicarus/iverilog/issues/1061) | open |
| parameterized classes | issue #291 "Parameterized class not supported" [2019-12-26](https://github.com/steveicarus/iverilog/issues/291) | open |
| `$cast` on class handles | PR #1447 "SV: class-handle $cast and static $typename" [2026-07-21](https://github.com/steveicarus/iverilog/pull/1447) | closed 2026-07-21, **not merged** |
| queue-typed class properties | PR #1416 "SV: class queue/darray property foundation" [merged 2026-07-12](https://github.com/steveicarus/iverilog/pull/1416) | merged to master after the 13.0 tag; the book's 13.0 does not have it |
| base = derived assignment | issue #422 [2020-12-13](https://github.com/steveicarus/iverilog/issues/422) | open, but 13.0 accepts the assignment (every dispatch probe compiles) |
| interface classes, `implements`, handle comparison, nested member paths, method calls on properties | no issue found by title search | the compiler's own `sorry:` and `SORRY:` lines in §1 are the only record |

**Where documentation and measurement disagree.** The README's sentence
is accurate and useless; nothing it says is contradicted. The
disagreement is between the tracker's *state* and the *behavior*: issue
#421 is closed, which a reader could take to mean abstract classes work,
while the closing comment records that they do not; and the Chapter 5
note's statement that PR #1447 is "open, unmerged" does not match the
tracker on 2026-09-11 — it was closed without merging on 2026-07-21, so
`$cast` on handles is further from Icarus, not nearer.

### 4. Lint under the book's fatal flags, and the runner's caveats

Under the book's own `sv.mk` flags (`-Wall` fatal, no `-Wno-fatal`), a
`--lint-only` pass over all 51 probes warns on exactly four: o11
(`UNDRIVEN` ×1), o12 (`UNDRIVEN` ×1), o13 (`UNDRIVEN` ×2) — each on the
name of a `pure virtual` prototype — and o22 (`UNUSEDPARAM` on the
specialization's parameter). No other probe warns (measured, this note,
Verilator 5.030). A shipped abstract-class or interface-class example
therefore needs `-Wno-UNDRIVEN` in its Makefile, with a comment naming the
prototype, as the Chapter 5 note already prescribes; every other Chapter 6
listing can be lint-clean as written.

Two caveats on the runner. First, `matrix.py` keeps only the first line
containing "error" or "sorry"; for o25 that line is the nested-member
`sorry:` and hides the `Method name nesting` error on the same probe, so
§1.6 quotes both from the full log. Second, the runner classifies the two
negative probes as failures of support ("no build", "no run") when they
are successes of diagnosis; a Chapter 6 `probes.txt` that includes them
should label them as this note does, or leave them out of the shipped
table and keep them as a test.

### 5. What this means for the chapter's examples

- **Every polymorphism listing runs on Verilator only.** The chapter's
  `sv.mk` example directories for dispatch, abstract classes, interface
  classes, `$cast`, clone, parameterized classes, factories, singletons
  and callbacks build with Verilator; the Icarus column exists to be shown
  as wrong, and the chapter's In Practice callout should quote the 2020
  tracker comment and print the o08 line `via_a=1 via_b=2 via_c=3` beside
  the expected `3 3 3`.
- **Constructor chaining, hiding and `protected` can be shown on both**,
  and a listing that contrasts hiding (o03) with dispatch (o04) is the one
  place where Icarus's output is *correct for hiding and wrong for
  dispatch* on the same page — a precise demonstration of what `virtual`
  adds.
- **Teach `clone()` as a virtual method that constructs its own class**
  (o17's shape), and say that `new src` is not a polymorphic copy on
  Verilator 5.030 with the issue number, so a reader on a later Verilator
  knows why their result differs from the book's `run.out`.
- **Do not call virtual methods from constructors** in any listing, and
  if the trap is shown, show it as "both open tools print the base body;
  check the clause before assuming a commercial tool differs".
- **Icarus cannot run composition at all** (o41, o42, o16, o25): a class
  that holds another class's handle cannot call through it or read its
  properties. Any driver/monitor/scoreboard listing is Verilator-only for
  this reason alone, before dispatch enters.
- **Handle comparison** `a == b` (o40) is Verilator-only; a chapter
  identity example that runs on both must compare against `null` only.
- **Negative examples** (`new` on an abstract class, the `$cast` task
  form) should be shown with Verilator's messages, which cite the clause;
  Icarus fails earlier and for another reason.

### Unsourced-claims table

| Claim | Status |
|---|---|
| A virtual call from the base constructor must reach the derived override (o26, o26b are "wrong") | This note's reading of the standard; the clause text was not consulted (`refs.bib`, `ieee1800-2023`). Both tools disagree with the reading. Verify against IEEE 1800-2023 §8.7/§8.20 before the chapter asserts it. |
| "The new object has the same type as the source object" is the text of IEEE 1800-2017 §8.7 | Quoted at second hand from Verilator #7105; not checked against the standard. |
| Icarus binds virtual calls to the declared type of the handle expression | Inferred from o08, o09, o26c; the tracker says virtual is "ignored", which is consistent but does not state the binding rule. |
| Verilator's constructor-time dispatch is inherited from C++ construction order | Inferred from the generated code quoted in #6214; not stated by the project for this case. |
| No Icarus issue names virtual dispatch as wrong | Title search over five queries, unauthenticated GitHub search API, 2026-09-11; body-text matches beyond the first 30 results were not read. |
| The 51 probes can be dropped into a Chapter 6 `support-matrix/` example unchanged | Format checked against `matrix.py`; the example's Makefile and `check-examples.sh` run were not tried. |

### Key sources

Existing `refs.bib` keys reused: `verilator-languages`, `verilator-warnings`,
`verilator-changes`, `icarus-release-13`, `icarus-issue-291`,
`icarus-issue-464`, `icarus-pr-1348`, `icarus-issue-792`, `ieee1800-2023`.
Where the chapter quotes a limitation it should cite the 5.030-tagged
files, as the Chapter 5 note proposed. New entries:

```bibtex
@misc{icarus-issue-421,
  author       = {{Icarus Verilog contributors}},
  title        = {{SV}: abstract class not working as expected},
  howpublished = {GitHub, steveicarus/iverilog, issue 421},
  year         = {2020},
  url          = {https://github.com/steveicarus/iverilog/issues/421},
  note         = {Opened 2020-12-13, closed 2022-12-17. The maintainer's
                  comment of 2020-12-14 records that the virtual keyword is
                  parsed but ignored, for classes and for methods.
                  Accessed 2026-09-11}
}

@misc{icarus-issue-292,
  author       = {{Icarus Verilog contributors}},
  title        = {Issue in calling class methods},
  howpublished = {GitHub, steveicarus/iverilog, issue 292},
  year         = {2019},
  url          = {https://github.com/steveicarus/iverilog/issues/292},
  note         = {Open since 2019-12-27; the comment of 2023-01-16 records
                  that virtual-method support requires changes in vvp.
                  Accessed 2026-09-11}
}

@misc{icarus-pr-469,
  author       = {Srinivasan Venkataramanan},
  title        = {Added parse-only support for pure virtual methods},
  howpublished = {GitHub, steveicarus/iverilog, pull request 469},
  year         = {2021},
  url          = {https://github.com/steveicarus/iverilog/pull/469},
  note         = {Opened 2021-01-04; open and unmerged on 2026-09-11}
}

@misc{icarus-pr-1447,
  author       = {{Icarus Verilog contributors}},
  title        = {{SV}: class-handle \$cast and static \$typename},
  howpublished = {GitHub, steveicarus/iverilog, pull request 1447},
  year         = {2026},
  url          = {https://github.com/steveicarus/iverilog/pull/1447},
  note         = {Opened and closed without merging on 2026-07-21.
                  Accessed 2026-09-11}
}

@misc{icarus-pr-1416,
  author       = {{Icarus Verilog contributors}},
  title        = {{SV}: class queue/darray property foundation},
  howpublished = {GitHub, steveicarus/iverilog, pull request 1416},
  year         = {2026},
  url          = {https://github.com/steveicarus/iverilog/pull/1416},
  note         = {Merged 2026-07-12, after the v13.0 tag of 2026-03-02.
                  Accessed 2026-09-11}
}

@misc{icarus-issue-1061,
  author       = {{Icarus Verilog contributors}},
  title        = {Inability to use local/protected and virtual qualifiers
                  simultaneously},
  howpublished = {GitHub, steveicarus/iverilog, issue 1061},
  year         = {2024},
  url          = {https://github.com/steveicarus/iverilog/issues/1061},
  note         = {Open since 2024-01-04. Accessed 2026-09-11}
}

@misc{icarus-readme-13,
  author       = {{Icarus Verilog contributors}},
  title        = {{Icarus Verilog} README},
  howpublished = {GitHub, steveicarus/iverilog, v13-branch},
  year         = {2026},
  url          = {https://github.com/steveicarus/iverilog/blob/v13-branch/README.md},
  note         = {Accessed 2026-09-11}
}

@misc{verilator-issue-7105,
  author       = {{Verilator contributors}},
  title        = {Fix new <obj> shallow copy not preserving polymorphic
                  runtime type},
  howpublished = {GitHub, verilator/verilator, issue 7105},
  year         = {2026},
  url          = {https://github.com/verilator/verilator/issues/7105},
  note         = {Opened 2026-02-19, closed 2026-02-22; the fix postdates
                  the 5.030 release this book measures. Accessed 2026-09-11}
}

@misc{verilator-issue-6214,
  author       = {{Verilator contributors}},
  title        = {Super constructor calls with local variables don't work},
  howpublished = {GitHub, verilator/verilator, issue 6214},
  year         = {2025},
  url          = {https://github.com/verilator/verilator/issues/6214},
  note         = {Opened 2025-07-22, closed 2026-03-04; quotes the generated
                  C++ constructor chain. Accessed 2026-09-11}
}

@misc{verilator-languages-5030,
  author       = {Wilson Snyder and {Verilator contributors}},
  title        = {Verilator User's Guide: Language Limitations, release 5.030},
  year         = {2024},
  url          = {https://github.com/verilator/verilator/blob/v5.030/docs/guide/languages.rst},
  note         = {Release-tagged 2024-10-27; the text that applies to the
                  installed binary. Accessed 2026-09-11}
}

@misc{verilator-changes-5030,
  author       = {{Verilator contributors}},
  title        = {Verilator Changes, release 5.030},
  year         = {2024},
  url          = {https://github.com/verilator/verilator/blob/v5.030/Changes},
  note         = {Release-tagged 2024-10-27. Accessed 2026-09-11}
}
```

### Confidence notes

- **High:** every matrix cell and every printed value. Each is a file in
  the scratchpad, a fixed command, and an output captured on 2026-09-11 by
  the book's own runner; the whole set re-runs in about three minutes.
- **High:** the Icarus tracker quotations (#421, #292) and the Verilator
  issue text (#7105), read from the GitHub API on 2026-09-11; the Verilator
  manual and change-log quotations, from the v5.030-tagged files.
- **High:** the Icarus binding rule as a *description* of the sixteen
  outputs. **Medium** as a statement about the implementation: three
  probes discriminate it from the alternatives, but no maintainer has
  stated the rule.
- **Medium:** the release attribution of each change-log line, read by
  line position under the version headers of the local `Changes` file.
- **Low:** that o26/o26b are "wrong". The standard's clause was not read.
  The chapter must not assert what a commercial simulator does here.
- **Not measured:** any Icarus build from master after 2026-07-12, which
  would have queue-typed class properties; any Verilator after 5.030,
  which would have the shallow-copy fix. The chapter should name versions,
  not tools.
