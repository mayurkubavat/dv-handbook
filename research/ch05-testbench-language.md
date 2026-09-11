---
title: "Research note: Chapter 5 — The SystemVerilog Testbench Language"
date: 2026-09-11
author: research-agent
status: complete
feeds: Ch. 5
---

# Chapter 5 — The SystemVerilog Testbench Language: evidence note

Scope: the language a testbench is written in, as a verification engineer
uses it — the type system and the two-state/four-state choice at the
testbench boundary, aggregate types, structs and enums, interfaces and
virtual interfaces, classes as the language defines them (with the line to
Chapter 6's object-oriented design drawn construct by construct), and a
*measured* account of which of those constructs the book's two open
simulators compile and run, which decides what the chapter's examples can be.

Gathered in three independent passes and kept in three parts. **Section
numbers are local to their part**: "§2.3" inside Part A means Part A's §2.3.
Each part carries its own unsourced-claims table, BibTeX suggestions and
confidence notes.

## Which part feeds which chapter section

| Chapter topic | Part | Sections |
|---|---|---|
| Two-state and four-state at the testbench boundary; signedness | A | §1, §2 |
| Aggregate types: arrays, queues, associative arrays | A | §3 |
| `struct`, `union`, `enum`, `typedef`, `string` | A | §4 |
| Interfaces, modports, virtual interfaces and their pitfalls | A | §5 |
| Contrast with a Python testbench | A | §6 |
| Where the Chapter 5 / Chapter 6 line falls | B | opening section |
| Handles, objects, lifetime, copying, `this`, static members | B | §1–§4 |
| Automatic versus static lifetime; `ref` arguments | B | §5, §7 |
| Class scope operator; parameterized classes | B | §6 |
| Defect catalogue for the Pitfall callouts | B | §8 |
| **Which constructs run on which tool** (decides every example) | C | §1, §4 |
| Documented versus measured support | C | §2, §3, §5 |
| slang and cocotb | C | §6 |
| What this means for the chapter's examples | C | §7 |

## Findings that decide the chapter, across the parts

1. **The testbench type rule is the inverse of the RTL rule** (Part A §1):
   two-state for what the testbench computes, four-state for what it
   observes — and Verilator stores 0 for `8'bx`, so the chapter's four-state
   example must run on Icarus (Part C §1).
2. **Every language construct the chapter teaches runs on at least one of
   the two tools, and the chapter must say which** (Part C §1). Associative
   arrays, virtual interfaces, parameterized classes, clocking blocks and
   `$cast` are Verilator-only; the four-state half is Icarus-only; constrained
   randomization runs on neither as installed (Verilator needs an SMT solver).
3. **Two silent wrong results** (Part C §4): Icarus 13.0 dispatches virtual
   methods statically — an inheritance example compiles, runs and prints the
   base class's output with no warning — which Chapter 6 must carry as a
   Pitfall; and the four-state case above.
4. **The Chapter 5 / Chapter 6 line** (Part B opening): handles, `new`,
   `null`, lifetime, static members, `this`, copying and argument passing
   are Chapter 5; inheritance, virtual methods and polymorphism are
   Chapter 6; `$cast` and deep copy straddle and are split as the table says.
5. **Clause numbers of IEEE 1800-2023 are partly inferred from the 2017
   edition** (Parts A and B). The ones Verilator's own sources cite are
   confirmed; the rest must be checked against the standard's text, free
   through the IEEE GET program, before the chapter cites them.


---

# Part A — Types and interfaces

Scope: the SystemVerilog data types a testbench author chooses between and
what each choice costs or hides (two-state and four-state, signedness), the
aggregate types (packed and unpacked arrays, dynamic arrays, associative
arrays, queues) with their semantics, methods and cost model, the composite
and named types (`struct`, `union`, `enum`, `typedef`, `string`) with packed
structs as protocol fields, and interfaces: what one is, modports,
parameterization, virtual interfaces as the testbench's handle onto the
design, and the pitfalls that recur. Chapter 4's note (`research/ch04-simulation-fundamentals.md`,
Part B §2 and §4) already covers clocking blocks, program blocks and the
four-state versus two-state argument; this note references those and does not
redo them. Connection strategy for virtual interfaces belongs to Chapter 10.

Written section by section; the most important part is first.

### 1. The findings that decide the chapter

**The testbench default is two-state, and the reasons are not the folklore
ones.** Sutherland and Mills, the authors of the reference "gotchas" papers
this book already cites, give the design-side rule in their synthesis paper:
use `logic` for almost everything in RTL and avoid two-state types there,
because a two-state variable starts at zero (often the reset value, so a
missing reset is invisible) and because synthesis treats `bit` and `logic`
identically, so the two-state behavior is a simulation-only artifact that can
hide a mismatch [Sutherland & Mills, SNUG SV, 2013-03-11](http://sutherland-hdl.com/papers/2013-SNUG-SV_Synthesizable-SystemVerilog_paper.pdf)
(§2.1, §2.3). The same paper's one testbench remark is the opposite rule:
randomly generated stimulus values "should be declared as bit (2-state)"
rather than `logic` (§2.1). Sutherland, Mills and Spear give the mechanism:
`randomize()` ranges over every two-state value of the variable's type, so a
random `int` or `byte` yields negatives unless constrained, and the paper's
advice is to declare stimulus that will be driven into hardware with types
whose full range is meaningful, and to constrain the C-like signed types when
they are needed for DPI [Sutherland, Mills & Spear, SNUG SJ, 2007-02-13](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf)
(§5.4). The chapter's line is therefore: two-state for stimulus, scoreboard
state, counters and anything the testbench computes; four-state wherever the
testbench *observes* the design, because a two-state variable silently
converts an X to zero at the boundary (§3.3 of the 2006 paper, below). This
does not contradict Chapter 4's four-state section, which is about what the
*simulator* does; this is about what the *variable declaration* does at the
testbench/design boundary.

**The 2006 two-state gotchas are all one gotcha: a two-state variable starts
at zero, and zero is a legal value.** Four consequences are given with worked
code: a `bit rst_n` set to zero at time zero produces no negedge, so an
asynchronous reset is missed (§3.1); a two-state enum whose first label has
value zero can lock a state machine in its start-up state because reset does
not change the variable and the combinational block never fires (§3.2); a
two-state comparator with an unconnected input outputs a definite 0 or 1
where four-state would output X (§3.3); and an out-of-range read of a
two-state array returns zero where a four-state array returns X (§3.4)
[Sutherland & Mills, SNUG Boston, 2006-09-08](http://sutherland-hdl.com/papers/2006-SNUG-Boston_standard_gotchas_paper.pdf).
The first is the one a testbench author hits, and the fix is two lines: set
the reset to its inactive value with a blocking assignment, then to its active
value with a non-blocking one.

**A virtual interface is a variable, not a structure, and every well-known
pitfall follows from that.** Sutherland, Mills and Spear's §4.2 states the
rule that a class cannot instantiate or take as an argument an interface,
because "static structural components cannot be directly driven from dynamic
code"; the class holds a *pointer* to the elaborated instance, and that
pointer is a virtual interface [2007-02-13](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf).
Rich's DVCon paper adds the consequence for parameters: the interface is used
"as a type", so a virtual interface declaration must repeat the parameter
values of the instance it will point at, and a `virtual itf #(8,16)` can only
be assigned an `itf #(8,16)` instance [Rich, DVCon, 2012-02-07](https://dvcon-proceedings.org/wp-content/uploads/the-missing-link-the-testbench-to-dut-connection.pdf)
(§III.A). The null-handle failure is the third consequence: the variable
starts null like any class handle, and OpenTitan's agents treat a failed
`uvm_config_db#(virtual tl_if)::get` as fatal at build time rather than let
the first `@(posedge vif.clk)` dereference null
[lowRISC OpenTitan `tl_agent.sv`, 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/tl_agent/tl_agent.sv).

**The design side and the verification side disagree about interfaces, on
the record.** The lowRISC Verilog style guide lists interfaces under
"Problematic Language Features and Constructs" whose use in RTL is discouraged
[lowRISC Verilog style guide, 2026-09-11](https://github.com/lowRISC/style-guides/blob/master/VerilogCodingStyle.md),
while the same project's DV guide requires clocking blocks inside interfaces to
sample and drive the design and names every virtual interface `<if>_vif`
[lowRISC DV style guide, 2026-09-11](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).
Sutherland and Mills say why in one sentence: interfaces are meant to bundle
*related* signals such as a bus, and bundling unrelated ones into a single port
is something verification does and design should not (§8) [2013-03-11](http://sutherland-hdl.com/papers/2013-SNUG-SV_Synthesizable-SystemVerilog_paper.pdf).
The chapter can teach the interface as a testbench construct with a clear
conscience, and should say that the design it connects to will usually have a
flat port list, as OpenTitan's `uart` DUT does (`.tl_i(tl_if.h2d)`).

**What the chapter must not assert.** No clause text from IEEE 1800-2023,
quoted or paraphrased; cite clause numbers for *where a rule lives* and
attribute the exposition to the papers. No performance numbers for
associative arrays, queues or two-state simulation: none of the sources
measure them (Chapter 4 already handles the two-state speed claim via
Cummings & Bening 2004). Do not call `bit`/`logic` "types" in the standard's
sense without care: Sutherland and Mills note that the standard's own terms
("types", "objects", "kinds") differ from engineers' usage and that they
deliberately say "value sets" for 2-state/4-state (§2, note) [2013-03-11](http://sutherland-hdl.com/papers/2013-SNUG-SV_Synthesizable-SystemVerilog_paper.pdf).

### 2. Two-state and four-state types, and signedness

**Where the rules live.** Integer data types and their value sets are Clause
6.11 of IEEE 1800-2023 (Table 6-8 lists `bit`, `logic`, `reg`, `byte`,
`shortint`, `int`, `longint`, `integer`, `time` with their widths, value sets
and default signedness); signedness of expressions is Clause 11.8; casting is
Clause 6.24 [IEEE, 1800-2023, 2024-02-28](https://standards.ieee.org/ieee/1800/7743/).
Clause numbers are those of the 2017 edition, which the 2023 edition kept for
these clauses (see confidence notes); the text was not consulted.

**The engineer's map of the types.** Sutherland and Mills (§2.3) give the
variable types as a list a reader can hold: `reg` and `integer` (4-state,
from Verilog); `logic`, which is not itself a variable type but infers one
except on `input`/`inout` ports, where it infers a net; `bit` (2-state,
user-sized); and `byte`, `shortint`, `int`, `longint` (2-state, 8/16/32/64
bits). Their design recommendation is `logic` nearly everywhere, "avoid all
2-state types in RTL models", with `int` for loop iterators as the one
exception [Sutherland & Mills, 2013-03-11](http://sutherland-hdl.com/papers/2013-SNUG-SV_Synthesizable-SystemVerilog_paper.pdf).
The lowRISC RTL guide is stricter and gives the example this chapter can
reuse: `logic signed [31:0]` "say[s] what you mean", while `int` versus
`integer` is "easy to confuse" and `bit` "doesn't belong in RTL"
[lowRISC Verilog style guide, 2026-09-11](https://github.com/lowRISC/style-guides/blob/master/VerilogCodingStyle.md).
Note what the testbench inherits from that map: `int` and `integer` differ
in value set (2-state versus 4-state), not in width, and both are signed;
`byte` is signed; `bit [7:0]` is not. OpenTitan's DV utilities define
`uint`, `uint8`, `uint16`, `uint32`, `uint64` as `bit [N-1:0]` typedefs
precisely so that testbench code has an unsigned, two-state integer family
[lowRISC OpenTitan `dv_utils_pkg.sv`, 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_utils/dv_utils_pkg.sv).

**What two-state costs in a testbench.** Beyond §1's four gotchas, two more
belong here. First, a two-state variable cannot receive an X from the design:
the 2006 paper's third gotcha (§3.3) includes the case where a four-state
block outputs X into a two-state model and the X "would be converted to a
zero as it propagates" [Sutherland & Mills, 2006-09-08](http://sutherland-hdl.com/papers/2006-SNUG-Boston_standard_gotchas_paper.pdf).
For a monitor or scoreboard that means a sampled `bit` never shows the X that
Chapter 4's four-state discussion is about; sample into `logic` and test with
`$isunknown` if the check matters. Second, truth tests: a 4-state expression
is true only if some bit is 1 *and* no bit is X or Z; a vector such as
`4'b010Z` is neither true nor false and an `if` on it takes the `else` (§6.10)
[2006-09-08](http://sutherland-hdl.com/papers/2006-SNUG-Boston_standard_gotchas_paper.pdf).
A two-state test has two answers and matches C, which is the reason
testbench control flow prefers two-state.

**What two-state buys.** Memory: the 2006 paper states that a four-state array
"requires twice the amount of simulation storage" as a two-state one, and
allows two-state for large memory models on that ground (§3.4) — the only
storage-cost claim in the sources, and it is a rule of thumb, not a
measurement. Speed: none of the sources here measure it; Chapter 4 already
cites the one measurement this book has [cummings2004twostate] and its
authors' warning against repeating it. Randomization: see §1.

**Signedness, in the four rules the papers give.** (1) A simple literal (`5`)
is signed; a based literal (`'h5`, `1'b1`) is unsigned unless written `'sh5`,
so `in + 1` and `in + 1'b1` differ for a negative `byte in`: the first gives
-4, the second 252 (§4.1) [2006-09-08](http://sutherland-hdl.com/papers/2006-SNUG-Boston_standard_gotchas_paper.pdf).
(2) Arithmetic is context-determined: if *any* operand on the right-hand side
is unsigned, every operand is treated as unsigned before the operation,
which is how a signed adder with an unsigned 1-bit carry-in becomes an
unsigned adder (§5.3). (3) Declaring or casting a 1-bit value as signed does
not help, because a 1-bit signed value's sign bit *is* its value bit, so a
carry-in of 1 sign-extends to -1; the correct form is
`signed'({1'b0, ci})` (§5.3). The lowRISC guide gives the same fix with
numbers: `a + incr` for `a = 8'sh80` gives 129, `a + signed'({1'b0, incr})`
gives -127 [lowRISC Verilog style guide, 2026-09-11](https://github.com/lowRISC/style-guides/blob/master/VerilogCodingStyle.md).
(4) A bit-select or part-select is always unsigned, even of a signed vector,
and it is self-determined, so `a[7:0] + b[7:0]` on signed `a`, `b` is an
unsigned add; wrap each in `$signed()` (§5.4) [2006-09-08](http://sutherland-hdl.com/papers/2006-SNUG-Boston_standard_gotchas_paper.pdf).
The testbench consequence: a scoreboard that compares a signed expected value
against a part-select of a design output compares signed against unsigned,
and the result is the unsigned comparison. Also relevant to Chapter 4's race
discussion but sourced here: the widening rules mean a `bit [7:0]` counter
compared with `-1` never matches.

### 3. Aggregate types

**Where the rules live.** Packed and unpacked arrays are Clause 7.4; dynamic
arrays 7.5; array assignment and arguments 7.6–7.7; associative arrays 7.8
with their methods in 7.9; queues 7.10; array querying functions 7.11; array
manipulation methods (locator, ordering, reduction, iterator index) 7.12
[IEEE, 1800-2023, 2024-02-28](https://standards.ieee.org/ieee/1800/7743/).

**Packed versus unpacked.** Sutherland and Mills (§2.4–2.5) explain the
distinction the way the chapter should: a *packed* array is a vector whose
bits are stored contiguously and which may be subdivided into fields
(`logic [3:0][7:0] a` is a 32-bit vector with four byte subfields, so `a[2]`
is a byte and `a[1][0]` a bit), whereas an *unpacked* array's dimensions
follow the name and select whole elements. Unpacked arrays gained whole-array
assignment, value-list assignment with `'{}` and `'{default:0}`, passing
through ports and to subroutines (dimensions and element type must match),
and the query functions `$size`, `$dimensions`, `$low`, `$high`, and so on
[2013-03-11](http://sutherland-hdl.com/papers/2013-SNUG-SV_Synthesizable-SystemVerilog_paper.pdf).
Two style rules a testbench should follow because the design it reads does:
declare packed ranges `[msb:lsb]` with msb ≥ lsb and unpacked arrays with the
`[size]` or `[0:n-1]` form, never `[size-1:0]`
[lowRISC Verilog style guide, 2026-09-11](https://github.com/lowRISC/style-guides/blob/master/VerilogCodingStyle.md).
The literal syntax has a gotcha of its own: `'{...}` is a list of separate
values and `{...}` is a concatenation into one vector, and the two are easy to
confuse (2007 paper §8.4) [2007-02-13](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf).

**Dynamic data has no hierarchical path.** The 2006 paper's §2.4 is the
constraint the chapter should state before it teaches any dynamic type: class
objects, dynamically sized arrays, queues and automatic variables cannot be
referenced hierarchically, because a hierarchy path is static and a dynamic
object "comes and goes during simulation"; the recommendation is to confine
dynamic storage to the testbench and to automatic subroutines
[Sutherland & Mills, 2006-09-08](http://sutherland-hdl.com/papers/2006-SNUG-Boston_standard_gotchas_paper.pdf).
The same paper notes (§2.7) that variables without a hierarchy path are not
written to VCD, which is why a queue's contents are invisible in a waveform
viewer and OpenTitan's end-of-test macros print queue contents by
`pop_front()`-ing them instead
[lowRISC OpenTitan `dv_macros.svh`, 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_utils/dv_macros.svh).

**Dynamic arrays** (`int a[]`, sized by `new[n]`, resized by `new[m](a)`,
`size()` and `delete()`) are the array to use when the length is known at
runtime but fixed thereafter; the methods are Clause 7.5. The 2007 paper's
array-of-objects gotcha (§4.5) is really about handles, but it is met first
with arrays: `Transaction trans[8]` is an array of eight *handles*, `new`
cannot be called on the array, and each element is constructed in a `foreach`
[2007-02-13](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf).

**Associative arrays** (Clause 7.8) allocate storage per index on first
write, with any integral, string or class-handle index type and the methods
`exists`, `delete`, `num`/`size`, `first`, `last`, `next`, `prev` (7.9).
The canonical use is sparse memory: OpenTitan's `mem_model` stores a whole
address space as `logic [7:0] system_memory[mem_addr_t]`, checks presence
with `exists()` before a read, and clears with `delete()`
[lowRISC OpenTitan `mem_model.sv`, 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/mem_model/mem_model.sv).
Note the element type there is four-state so that a never-written byte can be
distinguished from a zero. The lowRISC DV guide adds one rule: never use the
wildcard index `[*]`; always name the index type
[lowRISC DV style guide, 2026-09-11](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).
Misuse to warn about: reading a missing key returns the element type's
default (0 for two-state, X for four-state) *without* creating it, so a
scoreboard that reads before it checks `exists()` sees a silent zero on the
two-state element type; and iterating with `foreach` over an integral-indexed
associative array visits keys in index order, not insertion order (7.8).

**Queues** (Clause 7.10) are variable-size ordered collections with
`push_front`/`push_back`/`pop_front`/`pop_back`, `insert`, `delete`,
`size`, and index and slice access including `$` for the last element. The
standard's own characterization (7.10) is constant-time access to elements
and constant-time insertion and removal at *either end*; `insert` and
`delete` at an arbitrary position are not so characterized, which is the
cost model the chapter should teach: a queue is a deque, not a list. OpenTitan
uses queues as the default in-flight store, for example
`bit [SourceWidth-1:0] a_source_pend_q[$]` for pending TileLink source IDs
[lowRISC OpenTitan `tl_agent_cfg.sv`, 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/tl_agent/tl_agent_cfg.sv),
and a naming convention `_q` for them appears throughout its DV code.

**Array manipulation methods** (7.12) carry one documented gotcha: `sum with
(item > 7)` sums the *values of the `with` expression*, that is, the 1s and
0s of the test, not the elements that pass it; write `sum with ((item > 7) ?
item : 0)` (2007 paper §3.8) [2007-02-13](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf).
The same trap applies to the locator methods' return type: `find_index`
returns a queue of indices, `find` a queue of elements, and both return an
empty queue rather than a sentinel.

**Performance.** No source in this note measures dynamic array, associative
array or queue cost; the only characterization is the standard's own
(constant-time ends for queues, on-demand allocation for associative arrays),
cited by clause. The chapter should give the asymptotic shape and no numbers.

### 4. `struct`, `union`, `enum`, `typedef`, `string`

**Where the rules live.** Structures are Clause 7.2, unions 7.3, enumerations
6.19 (methods `first`, `last`, `next`, `prev`, `num`, `name` in 6.19.5),
user-defined types (`typedef`) 6.18, strings 6.16 with methods in 6.16.1–
6.16.14 [IEEE, 1800-2023, 2024-02-28](https://standards.ieee.org/ieee/1800/7743/).

**Enumerations are the type system's one strong type, with one hole.**
Sutherland and Mills (§2.6.1) list the checks an enum gets that a `reg` with
parameters never did: label values must be unique, the variable and label
sizes must agree, and an enum variable can be assigned only a label of its
own list or another variable of the same enum; their side-by-side FSM shows
six functional bugs in the Verilog version becoming syntax errors in the
enum version [2013-03-11](http://sutherland-hdl.com/papers/2013-SNUG-SV_Synthesizable-SystemVerilog_paper.pdf).
The hole is §6.15 of the 2006 paper: an enum variable can still hold a value
outside its list, in two ways — its uninitialized value (zero for a 2-state
base, X for a 4-state one) when no label is zero, and a static cast
`states_t'(State + 1)`, which forces the value in without checking. The
fixes are `$cast`, which checks at run time and refuses, and the `.next()`
method, which steps through labels rather than values
[Sutherland & Mills, 2006-09-08](http://sutherland-hdl.com/papers/2006-SNUG-Boston_standard_gotchas_paper.pdf).
The default base type is `int`, 2-state and 32 bits (§2.6.1 of the 2013
paper), which is why a bare `enum {A, B} s` is a 32-bit two-state variable
with the lock-up gotcha of §1; lowRISC requires every enum be named by
`typedef`, have an explicit base, and in RTL a 4-state one
[lowRISC Verilog style guide, 2026-09-11](https://github.com/lowRISC/style-guides/blob/master/VerilogCodingStyle.md).
OpenTitan's testbench enums use `bit` bases (`enum bit [1:0] {Host, Device,
...} if_mode_e`) [`dv_utils_pkg.sv`, 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_utils/dv_utils_pkg.sv),
and its RTL enums `logic` bases (`enum logic [2:0] {PutFullData = 3'h0, ...}
tl_a_op_e`) [`tlul_pkg.sv`, 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/ip/tlul/rtl/tlul_pkg.sv):
the two-state/four-state line of §1, applied to enums.

**Packed structs as protocol fields.** A `struct packed` stores its members
contiguously with the first member most significant, so the struct is also a
vector and can be assigned, compared, concatenated and sliced as one
(§2.6.2) [2013-03-11](http://sutherland-hdl.com/papers/2013-SNUG-SV_Synthesizable-SystemVerilog_paper.pdf).
OpenTitan's TileLink channels are exactly this: `tl_h2d_t` is a packed struct
of `a_valid`, `a_opcode` (an enum), `a_param`, `a_size`, `a_source`,
`a_address`, `a_mask`, `a_data`, `a_user` (itself a packed struct) and
`d_ready`; the DUT port is one struct, the interface carries one `wire
tlul_pkg::tl_h2d_t h2d`, and the testbench reads fields by name
[`tlul_pkg.sv`, 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/ip/tlul/rtl/tlul_pkg.sv),
[`tl_if.sv`, 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/tl_agent/tl_if.sv).
Two consequences for the chapter: a packed struct can be a *net* (the `wire`
above), which an unpacked struct cannot; and because it is a vector, an
enum member inside it is written through the struct's bits without the enum
checks. Sutherland and Mills' advice for RTL is "only use packed structures
when the structure will be used in a union" (§2.6.2); the testbench reason to
pack is different and legitimate — matching the design's port type — and the
chapter should say so rather than import the RTL rule. The lowRISC DV guide
notes the tool-side cost: structs on the design side are "likely converted to
a giant" vector in some flows, which affects backdoor and probe access
[lowRISC DV style guide, 2026-09-11](https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md).

**Unions.** Only packed unions are synthesizable; all members must be packed
types of equal width, and writing one member and reading another is legal
(§2.6.3) [2013-03-11](http://sutherland-hdl.com/papers/2013-SNUG-SV_Synthesizable-SystemVerilog_paper.pdf).
In a testbench the same property gives a free reinterpretation of a packet as
its header struct and as raw bits, which is the one use worth a listing.
Tagged unions (7.3.2) are rarely supported and not needed here.

**`typedef`.** Use it liberally, even for plain vectors of a project-wide
width, and keep the definitions in packages, so a size change happens once
(§2.6.4, "Advantage 5") [2013-03-11](http://sutherland-hdl.com/papers/2013-SNUG-SV_Synthesizable-SystemVerilog_paper.pdf).
For the testbench the payoff is type *identity*: a `typedef` of a
parameterized virtual interface (`typedef virtual pins_if #(NUM_MAX_INTERRUPTS)
intr_vif;`) is what lets OpenTitan write `uvm_config_db#(intr_vif)::set` on
one side and `get` on the other without repeating the parameter list
[`dv_utils_pkg.sv`, 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_utils/dv_utils_pkg.sv),
[`tb.sv` (uart), 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/ip/uart/dv/tb/tb.sv).
That is the mechanism behind Rich's parameter-matching warning in §1.

**`string`.** A dynamic, testbench-side type (Clause 6.16) with `len`,
`substr`, `atoi`/`itoa` and friends, comparison operators, and `$sformatf`
for construction; it is not a `byte` array and has no hierarchical path (§3
of this note). The chapter needs it for messages, names and `%s`, not for
data. Beware the one conversion trap the papers do not cover but the
standard does: assigning a packed vector to a `string` interprets the bits as
characters and drops leading NULs (6.16), so a numeric value becomes a
one-character string, not its decimal text.

### 5. Interfaces

**Where the rules live.** Interfaces are Clause 25: syntax and instantiation
25.3, ports 25.4, modports 25.5, tasks and functions in interfaces 25.7,
parameterized interfaces 25.8, virtual interfaces 25.9, access to interface
objects 25.10 [IEEE, 1800-2023, 2024-02-28](https://standards.ieee.org/ieee/1800/7743/).

**What an interface is.** A named bundle of signals, declared once and
connected as a single port, replacing the repeated signal lists that Rich
shows growing from a flat testbench to a module-per-role testbench; when the
DUT cannot take an interface port, its port list is connected with
hierarchical references to the interface's signals (`DUT d1(itf.clock,
itf.reset, ...)`) [Rich, DVCon, 2012-02-07](https://dvcon-proceedings.org/wp-content/uploads/the-missing-link-the-testbench-to-dut-connection.pdf).
An interface may also contain `always` blocks, continuous assignments,
automatic tasks and functions, and assertions (§8 of the 2013 paper); the
Doulos tutorial's framing is that tasks and functions in an interface "allow
a more abstract level of modelling" [Doulos, 2026-09-11](https://www.doulos.com/knowhow/systemverilog/systemverilog-tutorials/systemverilog-interfaces-tutorial/).
OpenTitan's `uart_if` is a good specimen: two wires, per-direction clocking
blocks and modports, and tasks `wait_for_tx_idle`, `reset_uart_rx` and
`drive_uart_rx_glitch` that a driver calls through its virtual interface
[`uart_if.sv`, 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/uart_agent/uart_if.sv).

**Modports.** A modport names a *view* of the interface: which signals are
input and which output as seen by the module connected through it, and which
tasks and functions that module may call; a synthesizable interface whose
signals are variables needs modports to give the ports a direction (§8)
[2013-03-11](http://sutherland-hdl.com/papers/2013-SNUG-SV_Synthesizable-SystemVerilog_paper.pdf).
A modport may also export a clocking block instead of raw signals, which is
how a testbench-side modport carries the timing of Chapter 4's clocking
discussion: OpenTitan's `tl_if` has `dut_host_mp(output h2d_int, input
d2h_int)` for a design connection and `host_mp(clocking host_cb)`,
`mon_mp(clocking mon_cb)` for the testbench
[`tl_if.sv`, 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/tl_agent/tl_if.sv).
Direction mistakes: driving a variable that a modport declares `input` is an
elaboration error, which is a feature; but the 2007 paper's §2.7 shows that
when both sides are *nets*, a tool may silently coerce the port to `inout`
("port coercion") and a reversed assignment goes undetected — the cure is to
use variables (`logic`) for single-driver signals so the mistake becomes an
error [2007-02-13](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf).
The 2006 paper's §2.9 adds the shared-variable hazard: a variable declared in
an interface is visible to every module connected to it, so two processes in
different files can write it and race; `always_comb`/`always_ff` make that a
compile error in RTL, and a testbench must synchronize explicitly
[2006-09-08](http://sutherland-hdl.com/papers/2006-SNUG-Boston_standard_gotchas_paper.pdf).

**Generic versus typed interface ports.** A module port declared `interface
a1` accepts any interface; one declared `intf_1 b1` accepts only that type.
The recommendation for designs is type-specific ports, and a module with a
generic port cannot be the elaboration top (§8) [2013-03-11](http://sutherland-hdl.com/papers/2013-SNUG-SV_Synthesizable-SystemVerilog_paper.pdf).

**Parameterized interfaces.** Parameterized like modules, with per-instance
overrides, so one interface definition serves several bus widths (§8). The
cost falls on the virtual side: Rich's example `virtual itf #(.width(8),
.size(16)) vitf1` can be assigned only from `top.i1` declared with the same
values, and keeping them in step "becomes a challenge" as designs grow
[Rich, 2012-02-07](https://dvcon-proceedings.org/wp-content/uploads/the-missing-link-the-testbench-to-dut-connection.pdf).
His alternative, an abstract class implemented by a concrete class *inside*
the interface, decouples the testbench from the interface's parameters at
the price of method-only access; Chapter 10 owns that choice, but Chapter 5
should present the parameter-matching rule as the reason it exists.

**Virtual interfaces, mechanics only.** A `virtual <interface>` variable is
a handle that can be assigned any instance of that interface type (and of
the same parameterization); it is null until assigned; through it a class
may read and write the interface's signals, wait on its events (`@(posedge
vitf.clock)`), use its clocking blocks and call its tasks
[Rich, 2012-02-07](https://dvcon-proceedings.org/wp-content/uploads/the-missing-link-the-testbench-to-dut-connection.pdf).
The 2007 paper's §4.2 is the compile-error form of the lesson: `arb_ifc arb;`
inside a class and `function new(arb_ifc arb)` are both errors, `virtual
arb_ifc arb;` and `new(virtual arb_ifc arb)` are the correction, and the
authors' summary line is that virtual interfaces "are the bridge or link
between the class-based testbench and the DUT" [2007-02-13](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf).
The handle crosses from the static world in one place, the top-level module:
OpenTitan's `tb.sv` instantiates `tl_if tl_if(.clk, .rst_n)` and publishes it
with `uvm_config_db#(virtual tl_if)::set(null, "*.env.m_tl_agent*", "vif",
tl_if)`; the agent retrieves it with the matching `get` and fatals with
"failed to get tl_if handle from uvm_config_db" if nothing was set
[`tb.sv` (uart), 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/ip/uart/dv/tb/tb.sv),
[`tl_agent.sv`, 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/tl_agent/tl_agent.sv).
Chapter 5 shows the assignment (`d.vitf = itf;`) and the null check; the
config-database mechanism is Chapter 10's.

**The pitfalls, and which are sourced.**
- *Null handle*: sourced by construction (a virtual interface is a variable
  with a null default; Rich; OpenTitan's fatal-on-get). The symptom a reader
  will meet — a null-object dereference at the first `vif.` access in
  `run_phase`, long after `build_phase` — is stated from experience, not a
  source; mark as unsourced.
- *Parameter mismatch*: sourced (Rich §III.A).
- *Modport direction*: sourced for the mechanism (2013 §8, 2007 §2.7). The
  further claim that a virtual interface declared with a modport
  (`virtual tl_if.host_mp`) restricts access to that view is Clause 25.9
  behavior; cite by clause, unverified text.
- *Interface inside interface*: the standard allows an interface to
  instantiate another (25.3) and to have interface ports (25.4); the pitfall
  is tool support, not semantics. Verilator documents that generate blocks
  around modports, virtual interfaces and unnamed interfaces are unsupported
  [Verilator language support, 2026-09-11](https://verilator.org/guide/latest/languages.html);
  nested-interface support is not documented either way. Part C owns tool
  support; this note only flags that "interface in interface" has no
  language-level source for being a pitfall.
- *Shared variables in interfaces*: sourced (2006 §2.9).
- *Driving a net from a class*: a class cannot contain continuous
  assignments and cannot procedurally assign a net, so a bidirectional bus
  needs a variable in the interface continuously assigned onto the wire, or
  a clocking block, which creates that assignment implicitly (Rich §V.A)
  [2012-02-07](https://dvcon-proceedings.org/wp-content/uploads/the-missing-link-the-testbench-to-dut-connection.pdf).
  OpenTitan's `tl_if` is the pattern: `h2d_int` is the variable the clocking
  block drives, and `assign h2d = (if_mode == Host) ? h2d_int : 'z` puts it on
  the wire only when the interface is in host mode
  [`tl_if.sv`, 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/tl_agent/tl_if.sv).

### 6. Contrast: what a Python testbench does with the same design

cocotb has no declared types on the testbench side. A handle's `.value`
returns a Python type chosen by the HDL object: a `LogicArray` for logic
vectors, `int` for integer nets, `float` for `real`, `bool` for booleans and
`bytes` for strings, and forgetting `.value` yields the handle, not the value
[cocotb docs, writing testbenches, 2026-09-11](https://docs.cocotb.org/en/stable/writing_testbenches.html).
Its `Logic` type is nine-valued, modelled on VHDL's `std_ulogic`
(U, X, 0, 1, Z, W, L, H, -), and converting a `Logic` or `LogicArray` to an
integer raises `ValueError` unless every element is 0, 1, L or H
[cocotb `_logic.py`, 2026-09-11](https://github.com/cocotb/cocotb/blob/master/src/cocotb/types/_logic.py),
[cocotb `_logic_array.py`, 2026-09-11](https://github.com/cocotb/cocotb/blob/master/src/cocotb/types/_logic_array.py).
Signedness is not tracked either: an assignment accepts any integer from
the most negative signed value to the largest unsigned value for the width,
and `LogicArray.from_signed`/`from_unsigned` make the choice explicit
[cocotb docs, 2026-09-11](https://docs.cocotb.org/en/stable/writing_testbenches.html).
So the two decisions this chapter spends most of its pages on — two-state or
four-state, signed or unsigned — become in cocotb a per-access decision
(`.value.to_signed()` versus `.to_unsigned()`; an exception on X) rather than
a declaration. There is no interface or virtual-interface concept: the test
holds hierarchical handles (`dut.sub.signal`), which is exactly what the 2012
paper argues against for reuse [Rich, 2012-02-07](https://dvcon-proceedings.org/wp-content/uploads/the-missing-link-the-testbench-to-dut-connection.pdf),
and what SystemVerilog's dynamic types cannot do at all (2006 §2.4). The
chapter can use this to say what the type system is *for*: it moves the X and
signedness decisions from every access to one declaration.

### 7. Unsourced-claims table

| Claim | Status | What would source it |
|---|---|---|
| Clause numbers 6.11, 6.16, 6.18, 6.19, 6.24, 7.2–7.12, 11.8, 25.3–25.10 are those of 1800-2023 | From the 2017 edition's numbering; 2023 text not consulted | Table of contents of 1800-2023 |
| Queues offer constant-time access and constant-time push/pop at both ends; `insert`/`delete` in the middle are not so characterized | Attributed to Clause 7.10 from the 2017 text; not re-read in 2023 | Same |
| Reading a missing associative-array key returns the element default and does not create it; `foreach` visits integral keys in index order | Attributed to Clause 7.8 from memory of the 2017 text | Same |
| Assigning a packed vector to a `string` drops leading NUL bytes | Clause 6.16 from memory | Same |
| A virtual interface declared with a modport (`virtual tl_if.host_mp`) restricts access to that view | Clause 25.9 from memory | Same |
| Null-handle symptom: dereference at first `vif.` access in `run_phase`, not in `build_phase` | Practitioner experience | A published UVM debugging note, or the book's own runnable example |
| Two-state simulation is faster | Not claimed here; Ch. 4 cites the single measurement | — |
| Four-state arrays take twice the storage of two-state | Sutherland & Mills 2006 §3.4 say so as a rule of thumb, no measurement | A tool's memory report on the book's own example |
| OpenTitan uses `_q` as a queue suffix throughout | Observed in `tl_agent_cfg.sv`; not a written rule in the DV guide | The DV guide's naming table (it lists `_vif`, not `_q`) |
| The 2006 paper contains "dozens" of gotchas; the 2007 paper 38 | 2006: its own abstract says "dozens"; 2007: its abstract says 38 | Sourced |

### 8. Key sources

Suggested BibTeX keys follow the repository's `author-year-short` style.
`sutherland2006gotchas`, `sutherland2007gotchas`, `ieee1800-2023`,
`cummings2004twostate`, `sutherland2013x`, `cocotb-docs`,
`opentitan-dv-methodology` already exist in `refs.bib`.

```bibtex
@inproceedings{sutherlandmills2013synth,
  author    = {Stuart Sutherland and Don Mills},
  title     = {Synthesizing {SystemVerilog}: Busting the Myth that
               {SystemVerilog} is only for Verification},
  booktitle = {Synopsys Users Group (SNUG) Silicon Valley},
  year      = {2013},
  url       = {http://sutherland-hdl.com/papers/2013-SNUG-SV_Synthesizable-SystemVerilog_paper.pdf},
  note      = {Data types \S 2, interfaces \S 8. Accessed 2026-09-11}
}
@inproceedings{rich2012missinglink,
  author    = {David Rich},
  title     = {The Missing Link: The Testbench to {DUT} Connection},
  booktitle = {Design and Verification Conference (DVCon)},
  year      = {2012},
  url       = {https://dvcon-proceedings.org/wp-content/uploads/the-missing-link-the-testbench-to-dut-connection.pdf},
  note      = {Author affiliated with Mentor Graphics; the paper is
               technical exposition, not a product claim.
               Accessed 2026-09-11}
}
@book{spear2012svfv,
  author    = {Chris Spear and Greg Tumbush},
  title     = {{SystemVerilog} for Verification: A Guide to Learning the
               Testbench Language Features},
  edition   = {3},
  publisher = {Springer},
  address   = {New York},
  year      = {2012},
  doi       = {10.1007/978-1-4614-0715-7},
  isbn      = {978-1-4614-0714-0},
  url       = {https://doi.org/10.1007/978-1-4614-0715-7},
  note      = {Ch. 2 ``Data Types'' (pp. 25--67), Ch. 4 ``Connecting the
               Testbench and Design'' (pp. 87--129), Ch. 10 ``Advanced
               Interfaces'' (pp. 363--384); chapter titles and pages from
               Crossref. Accessed 2026-09-11}
}
@misc{lowrisc-verilog-style,
  author       = {{lowRISC contributors}},
  title        = {{lowRISC} {Verilog} Coding Style Guide},
  howpublished = {GitHub, lowRISC/style-guides},
  year         = {2026},
  url          = {https://github.com/lowRISC/style-guides/blob/master/VerilogCodingStyle.md},
  note         = {Apache-2.0. Accessed 2026-09-11}
}
@misc{lowrisc-dv-style,
  author       = {{lowRISC contributors}},
  title        = {{lowRISC} Design Verification Coding Style Guide},
  howpublished = {GitHub, lowRISC/style-guides},
  year         = {2026},
  url          = {https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md},
  note         = {Apache-2.0. Accessed 2026-09-11}
}
@misc{opentitan-tl-if,
  author       = {{lowRISC contributors (OpenTitan project)}},
  title        = {{OpenTitan} {TileLink} agent interface (\texttt{tl\_if.sv}),
                  configuration and agent sources},
  howpublished = {GitHub, lowRISC/opentitan, hw/dv/sv/tl\_agent/},
  year         = {2026},
  url          = {https://github.com/lowRISC/opentitan/tree/master/hw/dv/sv/tl_agent},
  note         = {Apache-2.0. Accessed 2026-09-11}
}
@misc{opentitan-mem-model,
  author       = {{lowRISC contributors (OpenTitan project)}},
  title        = {{OpenTitan} \texttt{mem\_model}: associative-array memory model},
  howpublished = {GitHub, lowRISC/opentitan, hw/dv/sv/mem\_model/mem\_model.sv},
  year         = {2026},
  url          = {https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/mem_model/mem_model.sv},
  note         = {Apache-2.0. Accessed 2026-09-11}
}
@misc{opentitan-tlul-pkg,
  author       = {{lowRISC contributors (OpenTitan project)}},
  title        = {{OpenTitan} \texttt{tlul\_pkg}: {TileLink-UL} packed channel structs},
  howpublished = {GitHub, lowRISC/opentitan, hw/ip/tlul/rtl/tlul\_pkg.sv},
  year         = {2026},
  url          = {https://github.com/lowRISC/opentitan/blob/master/hw/ip/tlul/rtl/tlul_pkg.sv},
  note         = {Apache-2.0. Accessed 2026-09-11}
}
@misc{doulos-sv-interfaces,
  author       = {{Doulos}},
  title        = {{SystemVerilog} Interfaces Tutorial},
  howpublished = {Doulos KnowHow},
  year         = {2026},
  url          = {https://www.doulos.com/knowhow/systemverilog/systemverilog-tutorials/systemverilog-interfaces-tutorial/},
  note         = {Training-vendor tutorial; secondary. Accessed 2026-09-11}
}
@misc{verilator-languages,
  note = {already in refs.bib; cite for the interface/virtual-interface
          support statement}
}
```

### 9. Confidence notes

- **Primary and read in full:** Sutherland & Mills 2006 (PDF text
  extracted, sections §2.4, §2.9, §3.1–3.4, §4.1, §5.3, §5.4, §6.10, §6.15
  read); Sutherland, Mills & Spear 2007 (§2.6, §2.7, §3.8, §4.2, §4.5, §5.4,
  §8.4 read); Sutherland & Mills 2013 (§2, §8 read); Rich 2012 (whole paper).
  Dates given are the PDFs' modification dates (2006-09-08, 2007-02-13,
  2013-03-11, 2012-02-07), which precede the respective conferences; the
  conference month is the citation year's venue.
- **Open code, read from the repository at master on 2026-09-11:** the
  OpenTitan and lowRISC files named. They are moving targets; a chapter
  listing must be written from scratch, not copied, and the note cites them
  as evidence of practice, not as text to reproduce.
- **IEEE 1800-2023:** publication date and supersession confirmed from the
  IEEE SA page; every clause number is from the 2017 edition's structure and
  the 2023 text was not consulted. The chapter cites clauses as locations
  and never paraphrases them; a reviewer with access should spot-check
  6.11, 7.8, 7.10 and 25.9.
- **Spear & Tumbush, 3rd ed.:** bibliographic fields and the three chapter
  titles and page ranges come from Crossref records; the book's text was not
  consulted, so the note attributes no claim to it. It is the further-reading
  entry, cited by edition.
- **Verification Academy's virtual-interface cookbook page** returned 504 on
  three attempts; Rich 2012 cites its predecessor page. Bromley & Rich, "Abstract
  BFMs Outshine Virtual Interfaces" (DVCon 2008), is cited by Rich and is the
  primary source for the abstract-class alternative, but no URL was found;
  Chapter 10's research should retrieve it.
- **Not found:** a Cummings paper specifically on interfaces or virtual
  interfaces. His papers in `refs.bib` cover NBAs, FSMs, FIFOs, CDC, resets
  and two-state; none is on interfaces. The interface exposition rests on
  Sutherland & Mills 2013 §8, Rich 2012 and the 2007 gotchas.
- **Vendor material:** Rich 2012 is by a Mentor Graphics engineer and Spear
  2007 by a Synopsys engineer; both are technical exposition without product
  claims and are used as such. The Doulos tutorial is a training vendor's
  page and is used only for one framing sentence.
- **Web search was unavailable for this run** (session budget exhausted);
  every source was reached by direct URL. That is why the source set is the
  known canon rather than a survey; it is adequate for the chapter's claims
  but a later pass could add a DVCon paper on associative-array or queue
  performance if one exists.

---

# Part B — Classes, and the boundary with Chapter 6

Scope: the class constructs Chapter 5 must teach as *language*, before
Chapter 6 teaches *design* with them. Handles versus objects, `new` and the
null handle, what the standard promises about object lifetime and what it
leaves to the tool, copying, `this`, static members, variable and method
lifetime, the scope operator, parameterized classes and `typedef`
specializations, handles crossing interface and task boundaries, and the
defects that follow from each. The last section draws the Chapter 5 / Chapter
6 line construct by construct.

Written section by section; the most important part is first.

### The question that decides the chapter: where the Chapter 5 / Chapter 6 line falls

Chapter 5 teaches what a class *is* in the language; Chapter 6 teaches what one
*does* with several of them. The test applied to each construct below is: can a
reader use it correctly with a single class, no `extends`, and no knowledge of
how a testbench is organized? If yes, it is a language construct and belongs
in Chapter 5. If it only makes sense once there is a hierarchy of classes or a
testbench architecture to fit it into, it is design and belongs in Chapter 6.

The split has a precedent. The standard testbench textbook puts handles,
`new`, `null`, static members, `this`, copying and passing handles to methods
in a chapter titled "Basic OOP" (pp. 131–167), and inheritance, virtual
methods, polymorphism, abstract classes and callbacks in "Advanced OOP and
Testbench Guidelines" (pp. 273–321), with randomization, threads and
interprocess communication between the two
[Spear & Tumbush, 3rd ed., 2012, Crossref chapter records](https://api.crossref.org/works?filter=isbn:9781461407140&rows=30&select=title,DOI,page).
The gotchas book by Sutherland and Mills keeps the same order: general
programming gotchas (static tasks, argument passing) precede a single chapter of
"Object Oriented and Multi-Threaded Programming Gotchas" (pp. 153–172)
[Sutherland & Mills, 2007, Crossref chapter records](https://api.crossref.org/works?filter=isbn:9780387717142&rows=30&select=title,DOI,page,container-title).
Both books separate *the mechanics of one class* from *the design of many*.

| Construct | Standard clause (see confidence notes on numbering) | Chapter | Rationale |
|---|---|---|---|
| Class declaration, properties, methods | 8.3–8.6 | 5 | One class suffices |
| Handles vs objects, `new`, `null`, handle equality | 8.4, 8.7 | 5 | The single most common defect source; needs no hierarchy |
| Object lifetime, what the standard guarantees | 8.29 | 5 | Language semantics; a tool question, not a design one |
| Assignment vs shallow copy (`new obj`) vs deep copy | 8.7, 8.12 | 5 for assignment and shallow copy; 6 for the deep-copy *protocol* (`do_copy`/`clone`) | Shallow copy is one class; a copy protocol is a design convention across a class family |
| `this` | 8.11 | 5 | Needed to write any constructor that names its argument like its property |
| Static properties and static methods | 8.9, 8.10 | 5 | One class; the sharing rule is what must be taught |
| Automatic vs static lifetime of variables, tasks, methods | 6.21, 13.3.1, 13.4.2, 8.6 | 5 | Cuts across modules and classes; must precede any concurrent testbench |
| Class scope operator `::` | 8.23, 8.25.1 | 5 | Required to call a static method or name a parameterized specialization |
| Parameterized classes, `typedef` of a specialization | 8.25, 8.27 | 5 (mechanics only) | Syntax and the one-static-per-specialization rule; *why* to parameterize a component family is Chapter 6 |
| Passing handles to tasks: `input`, `ref`, `const ref` | 13.5.1, 13.5.2 | 5 | Argument passing is a language rule; the gotcha is a one-class gotcha |
| Class handles in interfaces; virtual interfaces in classes | 25.9 (virtual interfaces); Part A of this research | 5 | Both are language mechanics; Chapter 10 owns the connection strategy |
| `extends`, `super`, overriding, `virtual` methods, polymorphism | 8.13–8.15, 8.20–8.22 | 6 | Needs at least two classes to state |
| Abstract classes, `pure virtual`, interface classes | 8.21, 8.26 | 6 | Design contracts |
| Casting between class types (`$cast`) | 8.16 | 6 | Only meaningful with a hierarchy; Chapter 5 mentions `$cast` exists |
| Constructor chaining, `local`/`protected` | 8.17, 8.18 | 6 | Encapsulation decisions belong to design |
| Factory, config object, callbacks, copy/compare protocols | UVM base library, not the standard | 6 | Patterns over the constructs |

Two constructs sit on the line and the outline must place them deliberately.
**`$cast`** is a language builtin but its purpose is downcasting in a
hierarchy; Chapter 5 should show it once (a handle-to-handle copy that fails
at run time when the object's type does not match) and leave the reasoning to
Chapter 6. **Deep copy** is best split: Chapter 5 shows that `b = new a` copies
one level and that a nested handle is shared; Chapter 6 shows the `do_copy`
convention that the UVM base library uses to make the copy deep
[UVM-core `uvm_object.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_object.svh).

### 1. Handles and objects

A class variable holds a *handle*; the object exists only after `new`, and a
declared but unconstructed handle holds `null`. Two handles compare equal
exactly when they refer to the same object, which is the rule an open compiler
cites when it implements `==` on class variables: "In SV A == B iff both are
handles to the same object (IEEE 1800-2023 8.4)"
[Verilator `include/verilated_types.h`, accessed 2026-09-11](https://github.com/verilator/verilator/blob/master/include/verilated_types.h).
The same source enforces a null check on every dereference "per IEEE 1800-2023
8.7", the constructor clause. What the reader must take from this: the
variable and the object have different lifetimes, and copying a variable
copies the handle, never the object.

**Arrays of objects do not exist; arrays of handles do.** Declaring
`Transaction t[8]` allocates eight null handles, and `t = new` is a compile
error; each element needs its own `new`, typically in a `foreach`
[Sutherland, Mills & Spear, SNUG San Jose 2007, §4.5](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf).

**Handle aliasing is the canonical class bug.** The 2007 gotchas paper gives
the mailbox version: one object is constructed, randomized ten times and its
handle pushed into a mailbox ten times, and the consumer sees ten identical
transactions because "the mailbox is full of handles, but they all refer to a
single object"; the fix is to move `new` inside the loop
[Sutherland, Mills & Spear, SNUG San Jose 2007, §4.3](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf).
Practice in an open testbench follows that rule structurally: OpenTitan's
TileLink monitor creates a fresh `tl_seq_item` per request with
`tl_seq_item::type_id::create("req")`, and stores a *clone* of it in the
pending-request table so that the published object and the bookkeeping object
have independent lifetimes
[lowRISC OpenTitan `tl_monitor.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/tl_agent/tl_monitor.sv).
The UVM analysis port makes the contract explicit on the receiving side: its
`write(input T t)` passes the handle by value and its documentation says the
implementation "must not modify the value passed to it", because every
subscriber receives the same object
[UVM-core `uvm_analysis_port.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/tlm1/uvm_analysis_port.svh).

**Forgetting `new`.** Dereferencing a null handle is a fatal run-time error in
every simulator; the standard's only concession is that a method call on a
null handle for `randomize()` returns 0 rather than aborting, which an open
simulator got wrong until 2026 ("Null pointer dereferenced" instead of a zero
return)
[Verilator issue 7059, 2026-02-12](https://github.com/verilator/verilator/issues/7059).
Open testbench code guards the handles it did not construct itself: OpenTitan's
base environment checks `if (cfg == null)` after the config-db lookup, and its
base virtual sequence fails with `` `DV_CHECK_NE_FATAL(p_sequencer, null, "Did you forget to call `set_sequencer()`?") ``
[lowRISC OpenTitan `dv_base_env.sv`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_lib/dv_base_env.sv),
[`dv_base_vseq.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_lib/dv_base_vseq.sv).
The UVM base library does the same at its own boundary: `uvm_object::copy`
reports an error and returns when handed a null source
[UVM-core `uvm_object.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_object.svh).

### 2. Lifetime: what the standard guarantees and what it does not

The standard has no destructor and no `delete` for objects. Clause 8.29
(memory management) states that an object is reclaimed once no handle refers
to it and that the mechanism is the tool's business; the user-visible promise
is only that an object stays alive while any handle, including one inside a
queue, mailbox or another object, still refers to it
[IEEE 1800-2023, published 2024-02-28](https://standards.ieee.org/ieee/1800/7743/).
(Clause text is not quoted here; the standard is paywalled but free through
the IEEE GET program per the same page.) Consequences the chapter must state:

- Setting a handle to `null` releases *that* reference, nothing more. Whether
  the object is freed depends on every other handle.
- There is no finalizer, so no class can run code "when it is freed"; cleanup
  is an explicit method call, which is why UVM has phases rather than
  destructors.
- Dynamic objects have no hierarchical path. A class object "comes and goes
  during simulation", so testbench code cannot reach into one with a
  cross-module reference the way it reaches a module variable
  [Sutherland & Mills, SNUG Boston 2006, §2.4](http://sutherland-hdl.com/papers/2006-SNUG-Boston_standard_gotchas_paper.pdf).

What a real open tool does shows why the standard leaves the mechanism open.
Verilator's runtime base class for every generated class carries an atomic
reference counter and a pointer to a deleter; when the count reaches zero the
object is queued for deferred deletion, and `VlClassRef` increments and
decrements the count on copy and destruction
[Verilator `include/verilated_types.h`, accessed 2026-09-11](https://github.com/verilator/verilator/blob/master/include/verilated_types.h).
Reference counting cannot reclaim cycles, and the maintainers say so in a
design discussion opened in 2023: UVM's `uvm_component` holds a handle to its
parent and an associative array of its children, so under reference counting
"no `uvm_component`s will ever be freed"; a tracing collector was proposed and
the discussion was closed without one in 2024
[Verilator issue 4651, 2023-10-31 to 2024-04-13](https://github.com/verilator/verilator/issues/4651).
The parent/child cycle is real: `uvm_component` declares
`uvm_component m_parent` and `protected uvm_component m_children[string]`
[UVM-core `uvm_component.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_component.svh).
The lesson for Chapter 5 is not "avoid cycles" (UVM is built on them) but
"the standard promises reclamation of unreachable objects and says nothing
about *when* or *how*; a leak in one simulator is not a language error".

### 3. Assignment, shallow copy, deep copy

Three operations look alike and differ in what they copy. `b = a` copies the
handle: one object, two names. `b = new a` constructs a second object and
copies every property one level deep, so a nested handle in `a` is *shared*
by the copy, not duplicated; this is the standard's shallow copy (clauses 8.7
and 8.12). A 2026 tool fix records a subtlety the chapter can use as a worked
example: the object made by `new a` must have `a`'s *run-time* type, not the
declared type of the variable, so a shallow copy through a base-class handle
still yields a subclass object
[Verilator 5.046 change log, "Fix `new` shallow copy to preserve polymorphic runtime type (#7105)", 2026-02-28](https://github.com/verilator/verilator/blob/master/Changes).
That example only makes full sense after Chapter 6 introduces subclasses, so
Chapter 5 should show it with one class and revisit it.

A deep copy is not a language operation at all; it is a method the class
author writes. The UVM base library's `copy` is non-virtual and delegates to a
user hook: "To copy the fields of a derived class, that class should override
the `do_copy` method", and `clone` is "create followed by copy"
[UVM-core `uvm_object.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_object.svh).
Chapter 5 should therefore teach only that shallow copy is what the language
gives, and that a copy method is the author's job; the protocol is Chapter 6.

### 4. `this`, static properties and static methods

`this` names the object a non-static method was called on; its ordinary use
is a constructor whose argument shadows a property, `this.data = d`, which is
exactly how the 2007 gotchas paper resolves "programming statements in a
class get compilation errors" (a class body may hold declarations and
methods, never procedural statements; initialization goes in `new`)
[Sutherland, Mills & Spear, SNUG San Jose 2007, §4.1](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf).

A `static` property is one variable shared by every object of the class and
exists before any object does; a `static` method can be called through the
class name without an object and cannot use `this`. An open compiler cites
clauses 8.10–8.11 for both restrictions ("Cannot use 'this' in a static
method" and "Cannot access non-static member variable ... from a static method
without object")
[Verilator `src/V3LinkDot.cpp` (error text also in `test_regress/t/t_class_static_member_bad.out`), accessed 2026-09-11](https://github.com/verilator/verilator/blob/master/src/V3LinkDot.cpp).
Three uses in the UVM base library are the ones a reader will meet first:

- an instance counter, `static protected int m_inst_count`, read by the
  static `get_inst_count()` and used to give every object a unique id
  [UVM-core `uvm_object.svh`](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_object.svh);
- a singleton, `static local uvm_root m_inst` returned by
  `static function uvm_root get()`, which constructs the object on first use
  [UVM-core `uvm_root.svh`](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_root.svh);
- a global registry, `static protected this_type m_global_pool` in
  `uvm_pool #(KEY, T)`, with `static function T get_global(KEY key)`
  [UVM-core `uvm_pool.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_pool.svh).

The defect that follows is sharing where the author meant per-object state.
The 2006 gotchas paper describes the general form: a variable written by
several concurrent processes is "the same piece of storage ... shared by all",
and the collisions are hardest to find when the storage is declared in a
package, interface or `$unit` rather than next to its users
[Sutherland & Mills, SNUG Boston 2006, §2.8–2.9](http://sutherland-hdl.com/papers/2006-SNUG-Boston_standard_gotchas_paper.pdf).
A static class property is the same storage with a class name in front of it.
The deliberate use is worth showing too: OpenTitan's `csr_spinwait` is an
`automatic` task that declares `static int count` and copies `count++` into a
local, so that concurrent calls get distinct debug ids while everything else
about the call stays private
[lowRISC OpenTitan `csr_utils_pkg.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/csr_utils/csr_utils_pkg.sv).

### 5. Automatic versus static lifetime

Verilog inherited static tasks and functions: every call shares one set of
local storage, so a second call to a task that consumes time overwrites the
arguments of the first. The 2007 paper's example forks two `watchdog` calls
with different cycle counts and shows the second silently corrupting the
first; the fix is `task automatic`, and SystemVerilog also lets a whole
`module`, `program` or `interface` be declared `automatic`
[Sutherland, Mills & Spear, SNUG San Jose 2007, §3.10](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf).
The 2006 paper adds the package case: tasks in packages, interfaces and
`$unit` are called from many places, so their static storage is shared across
the whole design, and the guideline is to declare them `automatic`
[Sutherland & Mills, SNUG Boston 2006, §2.10](http://sutherland-hdl.com/papers/2006-SNUG-Boston_standard_gotchas_paper.pdf).
OpenTitan's utility packages follow that guideline to the letter: every task
and function in `csr_utils_pkg` and `dv_utils_pkg` carries `automatic`
[lowRISC OpenTitan `csr_utils_pkg.sv`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/csr_utils/csr_utils_pkg.sv),
[`dv_utils_pkg.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_utils/dv_utils_pkg.sv).

The rule the chapter must state in one table: the default lifetime is
**static** for tasks and functions declared in a module, interface, program
or package (clauses 6.21, 13.3.1, 13.4.2), and **automatic** for class methods
(clause 8.6, which also forbids declaring a class method `static` in the
lifetime sense; the `static` keyword on a method means a class-level method,
§4 above). Loop variables declared in a `for` header are automatic regardless
of context, which an open compiler documents against clause 6.21
[Verilator `src/V3LinkParse.cpp`, "IEEE 1800-2023 6.21: for loop variables are automatic", accessed 2026-09-11](https://github.com/verilator/verilator/blob/master/src/V3LinkParse.cpp).
Two consequences: a class method is re-entrant without any keyword, which is
why class-based drivers can be forked freely; and a module task that a class
calls back into is *not*, which is the usual explanation when a testbench
"works with one agent and fails with two". The interaction with `ref`
arguments is in §7.

### 6. The class scope operator and parameterized classes

`::` reaches a static member or a nested type through the class name rather
than a handle, and it is the only way to call a static method with no object
in hand. The pattern every reader will type is
`uvm_config_db#(T)::set(...)` and `::get(...)`: the class is parameterized
with `type T = int`, both methods are `static`, and `get` returns its value
through an `inout` argument
[UVM-core `uvm_config_db.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_config_db.svh).
For a parameterized class the operator must name a *specialization*: an open
compiler rejects a reference to a parameterized class without `#()` against
clause 8.25.1
[Verilator `src/V3LinkDot.cpp` (error text also in `test_regress/t/t_class_static_member_bad.out`), accessed 2026-09-11](https://github.com/verilator/verilator/blob/master/src/V3LinkDot.cpp).

**Each specialization is a distinct class with its own statics.** The UVM
factory depends on this: `uvm_component_registry #(type T, string Tname)`
keeps a `static this_type m_inst` and a `static function this_type get()`, so
`uvm_component_registry#(A)` and `uvm_component_registry#(B)` are two
singletons, one per registered type
[UVM-core `uvm_registry.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_registry.svh).
The `typedef` of a specialization is how a class gives that registry a short
name: `uvm_component` declares
`typedef uvm_abstract_component_registry#(uvm_component, "uvm_component") type_id`,
which is what `::type_id::create` resolves to
[UVM-core `uvm_component.svh`, accessed 2026-09-11](https://github.com/accellera-official/uvm-core/blob/main/src/base/uvm_component.svh).

OpenTitan shows the same mechanics without the factory in the way: its base
environment is `dv_base_env #(type CFG_T = dv_base_env_cfg, type VIRTUAL_SEQUENCER_T = ..., type SCOREBOARD_T = ..., type COV_T = ...)`
and constructs each part with `SCOREBOARD_T::type_id::create(...)`
[lowRISC OpenTitan `dv_base_env.sv`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_lib/dv_base_env.sv);
its comportable-IP config declares a dynamic array of a value-parameterized
specialization, `push_pull_agent_cfg#(.DeviceDataWidth(EDN_DATA_WIDTH)) m_edn_pull_agent_cfgs[]`,
and creates elements with the same specialization spelled out before
`::type_id::create`
[lowRISC OpenTitan `cip_base_env_cfg.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/cip_lib/cip_base_env_cfg.sv).
Chapter 5 teaches the syntax and the one-static-per-specialization rule and
stops; choosing type parameters over inheritance for a component family is a
Chapter 6 argument. Tool maturity is a Part C question, but one data point
belongs here because it is about the *mechanics*: the open compiler that now
runs most of the UVM library added class parameters in 4.226 (2022-08-31) and
still fixed "typedefs pointing to parameterized classes" in 5.020 (2024-01-01)
[Verilator `Changes`, accessed 2026-09-11](https://github.com/verilator/verilator/blob/master/Changes).

### 7. Handles across boundaries: interfaces and task arguments

**Classes cannot hold interfaces; they hold virtual interfaces.** An
interface is a static, elaborated object; a class variable of interface type
and a method argument of interface type are both compile errors, and the fix
is `virtual arb_ifc arb`, which the 2007 paper describes as the class's
pointer to the static object
[Sutherland, Mills & Spear, SNUG San Jose 2007, §4.2](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf).
Part A of this research owns virtual interfaces; Chapter 5 needs only the
sentence above.

**Interfaces can hold classes.** An interface may import a package, declare a
class and construct an object in an `initial` block. OpenTitan uses this to
give class-based code a handle onto a static countermeasure instance:
`prim_count_if` imports `uvm_pkg`, declares
`class prim_count_if_proxy extends sec_cm_pkg::sec_cm_base_if_proxy` *inside
the interface* (so its methods can force and release the interface's own
signals), constructs it with `if_proxy = new("if_proxy")` and pushes the
handle into a package-level queue `sec_cm_if_proxy_q[$]` that tests later
search by path
[lowRISC OpenTitan `prim_count_if.sv`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/sec_cm/prim_count_if.sv),
[`sec_cm_pkg.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/sec_cm/sec_cm_pkg.sv).
This is the cleanest open example of a handle crossing from the static world
into the dynamic one, and it needs no UVM knowledge to read.

**Passing a handle to a method.** The default direction is `input`, and an
input argument is a *local copy of the handle*. The object behind it is shared,
so the method can modify the caller's object; but if the method assigns the
argument (`c = new(...)`) the caller never sees the new object, because only
the local copy changed. The 2007 paper's `build_env` example is exactly this
and the fix is `ref`
[Sutherland, Mills & Spear, SNUG San Jose 2007, §4.4](http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf).
Three rules from clause 13.5.2 that the chapter must state with the example:

1. `ref` passes the caller's variable itself; `const ref` passes it read-only,
   which is the usual choice for large arrays and queues that must not be
   copied per call.
2. A subroutine with static lifetime cannot have `ref` arguments. An open
   compiler's error is the clause's own rule: "It is illegal to use argument
   passing by reference for subroutines with a lifetime of static (IEEE
   1800-2023 13.5.2)"
   [Verilator `src/V3Begin.cpp`, accessed 2026-09-11](https://github.com/verilator/verilator/blob/master/src/V3Begin.cpp).
   This is why `ref` and §5 must be taught together: a `ref` argument on a
   module task fails to compile until the task is `automatic`.
3. `const ref` protects the *handle*, not the object; the members of an object
   reached through a `const` handle stay writable unless they are themselves
   `const`, which an open compiler corrected in 2026 after wrongly rejecting
   `cls.x = 1` through a `const automatic Cls cls`
   [Verilator PR 7433, 2026-04-16](https://github.com/verilator/verilator/pull/7433).

Practice: OpenTitan's register adapter takes `const ref uvm_reg_bus_op rw`
and hands a `ref ITEM_T bus_req` to helpers that fill it; `dv_utils_pkg` has
`function automatic int max(const ref int int_q[$])`; and the register block
returns lists through `ref dv_base_reg_block blks[$]`
[lowRISC OpenTitan `tl_reg_adapter.sv`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/tl_agent/tl_reg_adapter.sv),
[`dv_utils_pkg.sv`](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_utils/dv_utils_pkg.sv),
[`dv_base_reg_block.sv`, accessed 2026-09-11](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/dv_base_reg/dv_base_reg_block.sv).
The pattern is consistent: `const ref` for a large read-only input, `ref` for
an output collection, plain `input` for a handle whose object is to be
modified in place. Two tool records show `ref` is where simulators still
diverge: a `ref bit` argument was updated wrongly in one open simulator until
2024 [Verilator issue 3385, 2022-04-14](https://github.com/verilator/verilator/issues/3385),
and passing a subclass handle to a `ref` argument of the base type was
rejected in 2025 with "Ref argument requires matching types"
[Verilator issue 6282, 2025-08-11](https://github.com/verilator/verilator/issues/6282);
the latter is the standard's rule, since a `ref` argument aliases the variable
and a base-typed alias to a subclass variable would let the callee store a
wrong-typed handle into it.

### 8. Defect catalogue for the chapter's Pitfall callouts

| Defect | Symptom | Source that documents it | Chapter |
|---|---|---|---|
| Handle aliasing: one `new`, many pushes | Every consumer sees the last randomization | 2007 gotchas §4.3; OpenTitan `tl_monitor.sv` clone-per-item as the practice | 5 |
| Array of handles left null | `t = new` rejected; `t[i].x` null dereference | 2007 gotchas §4.5 | 5 |
| Forgetting `new` on a handle received from elsewhere | Fatal null dereference; `randomize()` returns 0 | Verilator issue 7059; OpenTitan `dv_base_env.sv`, `dv_base_vseq.sv` null guards | 5 |
| Handle argument assigned inside a method | Caller's handle unchanged | 2007 gotchas §4.4; clause 13.5.1–13.5.2 | 5 |
| `ref` on a static-lifetime task | Compile error | Clause 13.5.2; Verilator error text | 5 |
| Static task called concurrently | Arguments of the first call overwritten | 2007 gotchas §3.10; 2006 gotchas §2.10 | 5 |
| Static property where per-object state was meant | All objects share one value | 2006 gotchas §2.8–2.9 (shared storage); UVM `m_inst_count` as the intended use | 5 |
| Shallow copy shares nested objects | Editing the copy edits the original's child | Clauses 8.7, 8.12; UVM `do_copy` hook | 5 (mechanics), 6 (protocol) |
| Class variable of interface type | Compile error | 2007 gotchas §4.2 | 5 (one sentence), Part A |
| Reference cycles never freed under reference counting | Memory grows in one open simulator; no language error | Verilator issue 4651; clause 8.29 | 5 (Future Directions or In Practice) |

### Unsourced-claims table

| Claim in this note | Status |
|---|---|
| Clause numbers 8.6, 8.9, 8.12, 8.16, 8.17, 8.22, 8.27, 8.29, 13.3.1, 13.4.2, 13.5.1, 25.9 for IEEE 1800-2023 | Inferred from 1800-2017 numbering; not checked against the 2023 text (paywalled; free via IEEE GET with registration). The numbers 6.21, 8.4, 8.7, 8.10, 8.11, 8.13, 8.15, 8.18, 8.21, 8.23, 8.24, 8.25.1, 8.26 and 13.5.2 are confirmed by an open compiler's citations of the 2023 edition. **Verify before publication.** |
| Clause 8.29 says reclamation is the tool's business and gives no timing | Paraphrase from memory of the 2017 text; not re-read for this note |
| Clause 8.6 forbids a `static` *lifetime* on class methods | Same |
| "Every simulator" treats a null dereference as fatal | Verified only for Verilator (issue 7059); commercial simulators not checked |
| Verilator issue 6282 reflects the standard's type-equivalence rule for `ref` | The issue was closed the same day with a "asked reporter" label; the maintainers' final position was not read |
| Spear & Tumbush chapter *contents* (which topics sit in "Basic OOP" vs "Advanced OOP") | Chapter titles and page ranges are from Crossref; the topic-to-chapter mapping is from the note author's knowledge of the edition and should be checked against the book |

### Key sources

Suggested BibTeX keys follow the book's `author-year-short` style. Keys marked
*(exists)* are already in `refs.bib`.

- `sutherland2006gotchas` *(exists)* — Stuart Sutherland and Don Mills,
  "Standard Gotchas: Subtleties in the Verilog and SystemVerilog Standards
  That Every Engineer Should Know", SNUG Boston, 2006.
  http://sutherland-hdl.com/papers/2006-SNUG-Boston_standard_gotchas_paper.pdf
  (accessed 2026-09-11). Note: the 2006 paper has two authors; Spear joins only
  in 2007.
- `sutherland2007gotchas` *(exists)* — Stuart Sutherland, Don Mills and Chris
  Spear, "Gotcha Again: More Subtleties in the Verilog and SystemVerilog
  Standards That Every Engineer Should Know", SNUG San Jose, 2007.
  http://sutherland-hdl.com/papers/2007-SNUG-SanJose_gotcha_again_paper.pdf
  (accessed 2026-09-11).
- `sutherlandmills2007gotchasbook` — Stuart Sutherland and Don Mills, *Verilog
  and SystemVerilog Gotchas: 101 Common Coding Errors and How to Avoid Them*,
  Springer, Boston, 2007. ISBN 978-0-387-71714-2 (print), 978-0-387-71715-9
  (electronic). DOI 10.1007/978-0-387-71715-9.
  https://doi.org/10.1007/978-0-387-71715-9 (Crossref record accessed 2026-09-11).
- `spear2012sv4v` — Chris Spear and Greg Tumbush, *SystemVerilog for
  Verification: A Guide to Learning the Testbench Language Features*, 3rd ed.,
  Springer, New York, 2012. ISBN 978-1-4614-0714-0 (print), 978-1-4614-0715-7
  (electronic). DOI 10.1007/978-1-4614-0715-7.
  https://doi.org/10.1007/978-1-4614-0715-7 (Crossref and Open Library records
  accessed 2026-09-11; xliv + 464 pp.).
- `ieee1800-2023` *(exists)* — IEEE Std 1800-2023, published 2024-02-28.
  https://standards.ieee.org/ieee/1800/7743/. Clauses cited: 6.21, 8.3–8.29,
  13.3.1, 13.4.2, 13.5.1, 13.5.2, 25.9.
- `ieee18002-2020` — IEEE Std 1800.2-2020, *IEEE Standard for Universal
  Verification Methodology Language Reference Manual*, published 2020-09-14.
  https://standards.ieee.org/ieee/1800.2/7567/ (accessed 2026-09-11).
- `accellera-uvm-core` — Accellera Systems Initiative, *UVM 2020-3.x Library
  Code for IEEE 1800.2* (source repository `accellera-official/uvm-core`,
  `main` branch; `UVM_MAJOR_REV 2020`, `UVM_MINOR_REV 3.0` in
  `src/macros/uvm_version_defines.svh`), Apache-2.0.
  https://github.com/accellera-official/uvm-core (accessed 2026-09-11).
  Release dates from https://www.accellera.org/downloads/standards/uvm:
  UVM 1.2 2014-06; 2020-3.0 2024-02; 2020-3.1 2024-08; 2020-3.2 2026-08.
  Files cited: `src/base/uvm_object.svh`, `uvm_component.svh`, `uvm_root.svh`,
  `uvm_pool.svh`, `uvm_config_db.svh`, `uvm_registry.svh`,
  `src/tlm1/uvm_analysis_port.svh`.
- `opentitan-dv-sv` — lowRISC contributors (OpenTitan project), *OpenTitan
  DV shared SystemVerilog libraries* (`hw/dv/sv/`), Apache-2.0.
  https://github.com/lowRISC/opentitan/tree/master/hw/dv/sv (accessed
  2026-09-11). Files cited: `dv_lib/dv_base_env.sv`, `dv_lib/dv_base_vseq.sv`,
  `dv_lib/dv_base_test.sv`, `cip_lib/cip_base_env_cfg.sv`,
  `csr_utils/csr_utils_pkg.sv`, `dv_utils/dv_utils_pkg.sv`,
  `tl_agent/tl_monitor.sv`, `tl_agent/tl_reg_adapter.sv`,
  `dv_base_reg/dv_base_reg_block.sv`, `sec_cm/prim_count_if.sv`,
  `sec_cm/sec_cm_pkg.sv`, `sec_cm/sec_cm_base_if_proxy.sv`. Pin a commit hash
  before the chapter cites a line.
- `verilator-types` — Verilator contributors, `include/verilated_types.h`
  (`VlClass`, `VlClassRef`, `VlDeleter`), LGPL-3.0/Artistic-2.0.
  https://github.com/verilator/verilator/blob/master/include/verilated_types.h
  (accessed 2026-09-11).
- `verilator-issue-4651` — "Garbage collector", Verilator issue 4651, opened
  2023-10-31, closed 2024-04-13.
  https://github.com/verilator/verilator/issues/4651.
- `verilator-changes` — Verilator `Changes` file. Entries used: 4.034
  (2020-05-03) first class support (#377); 4.104 static methods and typedefs
  in classes (#2615); 4.218 (2022-01-17) class static members (#2233); 4.226
  (2022-08-31) class parameters (#2231, #3541); 5.002 (2022-10-29) standalone
  `this` (#2594); 5.020 (2024-01-01) typedefs pointing to parameterized
  classes (#4747); 5.036 (2025-04-27) classes inside interfaces (#5846);
  5.046 (2026-02-28) shallow copy preserves run-time type (#7105).
  https://github.com/verilator/verilator/blob/master/Changes.
- Verilator issues and PRs 3385, 6282, 7059, 7433, 7167 (URLs inline above).
- `verilator-guide-languages` — Verilator user guide 5.052, "Language
  Support": "Verilator class support is limited but in active development.
  Verilator supports members, methods, class extend, and class parameters."
  https://verilator.org/guide/latest/languages.html (accessed 2026-09-11).

Not obtained (see gaps): Cummings, "SystemVerilog's Virtual World" (SNUG
Boston 2009) and "Understanding the UVM m_sequencer, p_sequencer Handles"
(SNUG SV 2024) are listed at https://www.paradigm-works.com/papers/ but the
PDF links are not exposed in the page markup; both are Chapter 6 material.

### Confidence notes

- **High**: every gotcha cited (2006 §2.4, §2.8–2.10, §7.1; 2007 §3.10, §3.11,
  §4.1–4.5) was read in the paper's own text extracted from the PDF; section
  numbers and page numbers are from that text.
- **High**: every UVM-core and OpenTitan line quoted was fetched from the
  `main`/`master` branch on 2026-09-11. Both move; the chapter must pin a
  commit.
- **High**: Verilator's reference-counting implementation and the cycle
  discussion (issue 4651) were read from the source and the issue thread.
- **Medium**: clause numbers, as itemised in the unsourced-claims table. Note
  in particular that an open compiler's comment titles clause 8.23 "Nested
  classes"; in the 2017 edition 8.23 is the class scope resolution operator,
  whose text also covers nested classes, so the number is consistent but the
  chapter should cite it as "clause 8.23" without a title until checked.
- **Medium**: the claim that Spear's "Basic OOP" chapter covers exactly the
  Chapter 5 list; titles and pages are sourced, contents are not.
- **Low / not verified**: behavior of commercial simulators on any point
  above. Nothing in this note is a vendor claim; the only tool evidence is
  from Verilator's open source, and Part C measures what runs.
- Chapter 4's note already covers program blocks and clocking blocks; this
  note does not touch them. Part A covers virtual interfaces; §7 here cites
  only the class-side gotcha.

---

# Part C — What the open tools run, measured

Scope: for every construct Chapter 5 teaches (2-state and 4-state types,
packed/unpacked/dynamic/associative arrays, queues, structs, unions, enums,
strings, interfaces with modports, virtual interfaces, classes, clocking
blocks, program blocks), what the book's two open simulators actually compile
and run. Two kinds of evidence are kept apart throughout: **documented**
support, quoted from the tools' own manuals with a dated URL, and **measured**
support, from minimal probes run on this machine and cited as "measured, this
note, <tool> <version>". Where the two disagree, the measurement wins for the
question "can the chapter ship this example" and the disagreement is recorded.

The output that matters is the support matrix in §1. Everything else is the
evidence behind it.

### Tool versions used for every measurement in this note

| Tool | Version string, as printed | Where |
|---|---|---|
| Verilator | `Verilator 5.030 2024-10-27 rev UNKNOWN.REV` | `/opt/homebrew/bin/verilator`, same binary on PATH and inside conda env `dvbook` |
| Icarus Verilog | `Icarus Verilog version 13.0 (stable) (v13_0)` | `/opt/homebrew/bin/iverilog`, `/opt/homebrew/bin/vvp` |
| cocotb | 2.1.0 | conda env `dvbook` |
| pyuvm | 5.0.0 | conda env `dvbook` |
| pyslang | 11.0.0 | conda env `dvbook` (no standalone `slang` binary on PATH) |

Versions were read with `verilator --version`, `iverilog -V`, and `pip list`
inside the env (measured, this note, 2026-09-11). Note that the book's
`examples/mk/sv.mk` invokes Verilator as `--binary --timing --timescale
1ns/1ps -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL`; every Verilator probe below
uses those flags so that "runs" means "runs under the book's own recipe". Icarus
probes use `iverilog -g2012` followed by `vvp`, the same pair the Chapter 4
comparison example uses (`examples/ch04-simulation/race/run_both.sh`).


### 1. The support matrix

#### 1.1 How to read it

Every cell is a **measured** result: a minimal probe compiled and run on this
machine with the book's own flags (Verilator `--binary --timing --timescale
1ns/1ps -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL`; Icarus `iverilog -g2012`
then `vvp`). The four verdicts are:

- **runs** — compiles, runs, prints the expected value.
- **runs (lint)** — the language is supported and the probe runs correctly,
  but only after suppressing a named `-Wall` warning that the book's default
  flags turn into an error. The warning is given; a shipped example must
  either restructure to avoid it or add the `-Wno-` to its Makefile.
- **wrong result** — compiles and runs to `$finish`, but prints the wrong
  answer. This is the most dangerous cell in the table, because a check that
  only looks at exit status passes.
- **unsupported** — compile or elaboration error, or a `vvp` load error. The
  exact message is in §4.

"Documented" in the last column means the tools' own manuals say the same
thing; where a manual says nothing, or says the opposite, the row says so.
Probes are `p*.sv`, `i*.sv`, `j*.sv` and `k*.sv` in the session scratchpad,
run by `run_probes.sh`; each prints `PROBE <name> PASS` only if the values
check, so "runs" means the values were right, not just that the process
exited zero (measured, this note, Verilator 5.030 and Icarus 13.0,
2026-09-11).

#### 1.2 Constructs the chapter teaches

| Construct (probe) | Verilator 5.030 `--timing` | Icarus 13.0 `-g2012` | Documented? |
|---|---|---|---|
| 2-state vs 4-state types, `$isunknown` (p01) | **wrong result** for the 4-state half: an uninitialized `logic` prints `0`, `l = 8'bx` stores `0`, `$isunknown` returns 0 | runs | Verilator: yes, X is replaced by a constant chosen by `--x-assign` [Verilator languages.rst v5.030, 2024-10-27](https://github.com/verilator/verilator/blob/v5.030/docs/guide/languages.rst) |
| Packed and unpacked fixed arrays, `foreach`, `$size`, `$bits` (p02) | runs | runs | Verilator: `logic`, `typedef`, arrays listed as supported keywords |
| Dynamic arrays: `new[]`, `new[n](old)`, `size`, `delete` (p03) | runs | runs | Icarus ships 30+ `sv_darray_*` regression tests [iverilog ivtest, v13-branch](https://github.com/steveicarus/iverilog/tree/v13-branch/ivtest/ivltests) |
| Associative arrays, `int` and `string` keys, `exists/num/first/next/delete` (p04, i04a–c, j04a–d) | runs (lint: `first`/`next` return `int`; compare `!= 0` or `WIDTHTRUNC` fires) | **unsupported**: every index type tried (`int`, `integer`, `string`, `bit [31:0]`, typedef, `[*]`) fails at parse | Icarus: open issue "SV: Icarus does not support associative arrays" [iverilog #792, 2022-11-20](https://github.com/steveicarus/iverilog/issues/792) |
| Queues: `push_*`, `pop_*`, `insert`, `size`, `delete`, `q[$]` (p05, i05a–b) | runs | runs | — |
| Queue slice `q[1:$]` and `sort()` (i05c, i05d) | runs | **unsupported** (slice: syntax error; sort: "sorry: 'sort()' array sorting method is not currently supported") | Icarus's message is its own "sorry" marker |
| Packed struct, positional pattern, field access (p06, i06a–b) | runs | runs | — |
| Packed struct with **named** assignment pattern `'{tag: …}` (p06) | runs | **unsupported** (syntax error) | Verilator: member-identifier keys supported, data-type keys not [languages.rst v5.030](https://github.com/verilator/verilator/blob/v5.030/docs/guide/languages.rst) |
| Unpacked struct (p06, i06c, k15) | runs | **unsupported** ("sorry: Unpacked structs not supported.") | — |
| Packed union (p07) | runs | runs | Verilator: structs and unions scheduled together [languages.rst v5.030](https://github.com/verilator/verilator/blob/v5.030/docs/guide/languages.rst) |
| Enums, `name()`, `next()`, `num()`, cast (p08) | runs | runs | Icarus ships 70+ `enum_*` tests |
| Strings: concatenation, `len`, `substr`, `atoi`, `$sformatf`, `==` (i09c) | runs | runs | — |
| String methods `toupper`, `tolower`, `compare`, `getc` (i09a–b, i09d) | runs | **unsupported** ("Method toupper is not a string method") | — |
| String method on a literal, `"42".atoi()` (p09 first form) | **unsupported** ("Syntax error: Not expecting CONST under a DOT") | (not reached) | — |
| `interface` instantiated, accessed hierarchically (j10a) | runs | runs | Icarus ships `sv_interface.v` in this form [ivtest](https://github.com/steveicarus/iverilog/blob/v13-branch/ivtest/ivltests/sv_interface.v) |
| `interface` as a **module port**, with or without modport (p10, i10a–b, j10b) | runs | **unsupported** ("Errors in port declarations") | Icarus: issue open since 2021 [#464](https://github.com/steveicarus/iverilog/issues/464); fix merged to master 2026-05-16, after v13.0 (2026-03-02) [PR #1348](https://github.com/steveicarus/iverilog/pull/1348) |
| Virtual interface held by a class, driven with `<=` and `@(posedge vif.clk)` (p11) | runs | **unsupported** ("Invalid class item") | Verilator manual still says "nor are virtual interfaces" — **doc contradicts measurement**; Changes 5.020 lists the support [Verilator Changes v5.030](https://github.com/verilator/verilator/blob/v5.030/Changes) |
| Class: `new`, handle alias vs copy, `null`, methods, scalar properties (p12, j12a) | runs | runs | Verilator: "members, methods, class extend, and class parameters" [languages.rst v5.030](https://github.com/verilator/verilator/blob/v5.030/docs/guide/languages.rst) |
| Class with a queue property (p12) | runs | **unsupported** ("sorry: Queues inside classes are not yet supported.") | — |
| Static property and static method via instance; `static` function variable; `automatic` recursion (i13a, i13c) | runs | runs | — |
| Static access by scope, `cls::method()` / `cls::prop` (p13, i13b) | runs | **unsupported** (syntax error at `::`) | — |
| Parameterized class `#(type T, int N)` (p14) | runs | **unsupported** (syntax error at `class fifo #(`) | — |
| Inheritance with `extends`, `super.new` (p15, i15a) | runs | compiles | — |
| **Virtual method called through a base handle** (j15a–h) | runs | **wrong result**: the base-class body runs in all six variants (int return, void, in a task, property-setting) | Icarus: related open issue on `base = derived` handle compatibility [#422, 2020-12-13](https://github.com/steveicarus/iverilog/issues/422) |
| `$cast` to a derived handle (p15) | runs | **unsupported** (vvp: "System task/function $cast() is not defined") | Icarus: class-handle `$cast` PR open, unmerged [PR #1447](https://github.com/steveicarus/iverilog/pull/1447) |
| Clocking block in an interface: `@(b.cb)`, `cb.sig <=`, sampled `cb.in` (p16) | runs (lint: `UNDRIVEN` on the interface signal driven through a module port) | **unsupported** ("Invalid module item" at `clocking`) | Verilator manual does not mention clocking blocks; Changes 5.028 "Support clocking blocks in virtual interfaces" |
| `modport tb (clocking cb)` (p16 first form) | **unsupported** (`%Error-UNSUPPORTED: Modport clocking`) | (not reached) | — |
| `program` block driving a DUT (p17) | runs | runs | Verilator lists `program` as supported; Icarus ships `program*.v` tests |

#### 1.3 Constructs beyond the chapter's core, measured because the chapter will mention them

| Construct (probe) | Verilator 5.030 | Icarus 13.0 | Note |
|---|---|---|---|
| `rand`/`randc` with **no** constraints, `randomize()`, `pre/post_randomize`, `srandom` (i18a, k04, k05, k12) | runs | **unsupported** ("randomize is not a method of class") | — |
| `constraint` blocks, `randomize() with` (p18, k14) | **needs an external SMT solver**: without `z3` on PATH, `randomize()` returns 0 and values stay at reset (`VERILATOR_SOLVER` names another) | **unsupported** ("sorry: Constraint declarations not supported.") | Verilator Changes 5.026: "Support constrained randomization with external solvers" |
| `solve … before`, `soft`, `std::randomize` (k06, k07) | `CONSTRAINTIGN` warning, fatal under `-Wall`; `std::randomize ignored (unsupported)` | unsupported | [Verilator warnings.rst v5.030](https://github.com/verilator/verilator/blob/v5.030/docs/guide/warnings.rst) |
| `mailbox #(T)`, `semaphore` (p19, j19b–c) | runs | **unsupported** (syntax error at the declaration) | — |
| `event`, `->`, `fork/join`, `wait fork`, `disable fork` (j19a, k09) | runs | runs | — |
| Queue of class handles, assoc array of handles (p20) | runs | **unsupported** ("Queue of type `class …` is not yet supported") | — |
| Fixed array of class handles (i20a, j20a) | runs | **unsupported** at load ("unresolved functor reference … Program not runnable") | compiles, fails in `vvp` |
| `interface class` / `implements`; `virtual class` + `pure virtual` (p21, k01) | runs (lint: `UNDRIVEN` on the pure-virtual name) | **unsupported** (syntax error) | Icarus: parse-only PR open since 2021 [#469](https://github.com/steveicarus/iverilog/pull/469) |
| `protected`, `local` (i21a) | runs | runs | — |
| `extern` method with out-of-body definition (k02) | runs (lint: `UNDRIVEN`) | **unsupported** ("sorry: External methods are not yet supported.") | — |
| Nested class (k03) | **unsupported** (`%Error-UNSUPPORTED: class within class`) | unsupported | — |
| `covergroup` inside a class (k08) | **unsupported** (`covergroup`, `cover point`, `covergroup within class`) | unsupported | — |
| Class in a package, `import pkg::*` (k10) | runs | runs | — |
| `this.prop`, handle-typed property, chained `a.next.v` (k11) | runs (lint: `VARHIDDEN`) | **unsupported** ("sorry: Nested member path not yet supported for class properties.") | — |

#### 1.4 Headline

- **Runs on both, unchanged:** fixed arrays, dynamic arrays, queues (without
  slice or `sort`), packed structs with positional patterns, packed unions,
  enums and their methods, the core string operations, interfaces used
  hierarchically, plain classes with scalar properties, static members via an
  instance, inheritance *without* calling through the base handle, `program`
  blocks, events and `fork`.
- **Runs on Verilator only:** associative arrays, queue slices and `sort`,
  unpacked structs, the remaining string methods, interface ports and
  modports, virtual interfaces, queues inside classes, parameterized classes,
  scope-resolution `::`, virtual dispatch, `$cast`, clocking blocks,
  mailboxes and semaphores, containers of handles, interface and abstract
  classes, `extern` methods, unconstrained `randomize()`.
- **Runs on Icarus only:** the four-state half of the types section. This is
  the one row where the event-driven simulator is the only one that can show
  the language's semantics.
- **Runs on neither, as installed:** constrained randomization (Verilator
  needs `z3`; Icarus has no `randomize`), nested classes, covergroups in
  classes, `modport … (clocking …)`, `std::randomize`.
- **Silent wrong results, which a status-only check would miss:** Verilator
  on four-state values; Icarus on virtual-method dispatch; Verilator on any
  constrained `randomize()` when the solver is absent (it returns 0, which a
  probe that ignores the return value would not see).

### 2. Documented support: Verilator 5.030

Verilator 5.030 is dated 2024-10-27 in its own change log [Verilator Changes,
v5.030 tag](https://github.com/verilator/verilator/blob/v5.030/Changes); the
release-tagged `docs/guide/languages.rst` is the manual that applies to the
installed binary, and the quotations below are from that revision, not from
the rolling `latest` site the book's `refs.bib` already cites as
`verilator-languages` [Verilator languages.rst,
v5.030](https://github.com/verilator/verilator/blob/v5.030/docs/guide/languages.rst).

**What the manual claims.** The 2005 section lists the supported keywords,
and the list includes `bit`, `byte`, `enum`, `int`, `interface`, `logic`,
`longint`, `modport`, `package`, `program`, `shortint`, `struct`, `typedef`,
`union` and `void`. It then says, in one sentence, "Verilator has limited
support for class and related object-oriented constructs." The dedicated
"Class" entry under Language Limitations is the whole of the class
documentation: "Verilator class support is limited but in active development.
Verilator supports members, methods, class extend, and class parameters."
There is **no enumerated list of unsupported class features** in the 5.030
manual; the team lead's request for "the exact list" cannot be met from the
documentation, and §5 assembles the list from measured `UNSUPPORTED` errors
and from the change log instead.

**Interfaces.** The keyword entry reads: "Interfaces and modports, including
generated data types are supported. Generate blocks around modports are not
supported, nor are virtual interfaces nor unnamed interfaces." That sentence
is stale for this release: the change log's 5.020 entries include "Support
parameterized virtual interfaces", "Support --timing triggers for virtual
interfaces" and "Support invoking interface methods on virtual interface
variables", and 5.028 adds "Support clocking blocks in virtual interfaces"
[Verilator Changes, v5.030](https://github.com/verilator/verilator/blob/v5.030/Changes).
The probe in §4 confirms that a class holding a `virtual bus_if` runs. The
chapter should not quote the manual's sentence as current.

**Timing.** "With `--timing`, all timing controls are supported: delay
statements, event control statements not only at the top of a process,
intra-assignment timing controls, net delays, `wait` statements, as well as
all flavors of `fork`." Building such a model "requires a compiler with C++20
coroutine support". `#0` delays draw a `ZERODLY` warning because "they do not
schedule process resumption in the Inactive region" [Verilator languages.rst,
v5.030](https://github.com/verilator/verilator/blob/v5.030/docs/guide/languages.rst).

**Four-state.** "Assigning X to a variable will assign a constant value as
determined by the `--x-assign` option", and "`--x-assign fast`, the default,
converts all Xs to whatever is best for performance" [Verilator
exe_verilator.rst, v5.030](https://github.com/verilator/verilator/blob/v5.030/docs/guide/exe_verilator.rst).
Uninitialized variables follow `--x-initial`, whose default `unique`
"initializes variables using a function". In the probe the function produced
zeros, which is the runtime default of the `+verilator+rand+reset` plusarg;
the chapter's four-state example must therefore run on Icarus.

**Assignment patterns and casts.** "Assignment patterns with an order based,
default, constant integer (array) or member identifier (struct/union) keys
are supported. Data type keys and keys computed from a constant expression
are not supported." "Casting is supported only between simple scalar types,
signed and unsigned, not arrays nor structs." Structures and unions "are
scheduled together" [Verilator languages.rst, v5.030](https://github.com/verilator/verilator/blob/v5.030/docs/guide/languages.rst).

**Constraints.** The `CONSTRAINTIGN` warning "warns that Verilator does not
support certain forms of `constraint`, `constraint_mode`, or `rand_mode`, and
the construct was are ignored" (sic) [Verilator warnings.rst,
v5.030](https://github.com/verilator/verilator/blob/v5.030/docs/guide/warnings.rst).
The change log records "Support constrained randomization with external
solvers" at 5.026 and a run of constraint features at 5.028 and 5.030
(`dist`, `foreach`, `inside`, `solve`-adjacent forms, `rand_mode`,
`constraint_mode`, queue and associative-array randomization) [Verilator
Changes, v5.030](https://github.com/verilator/verilator/blob/v5.030/Changes).
The manual for 5.030 does not name the solver binary; the runtime message in
§4 does (`z3 --in`, overridable through `VERILATOR_SOLVER`).

**`UNSUPPORTED` and `UNDRIVEN`.** `UNSUPPORTED` is "an error that a construct
might be legal according to IEEE but is not currently supported by
Verilator"; `UNDRIVEN` "warns that the specified signal has no source" and
"Verilator is relatively liberal in the usage calculations" [Verilator
warnings.rst, v5.030](https://github.com/verilator/verilator/blob/v5.030/docs/guide/warnings.rst).
Three class probes and the clocking probe fail only on `UNDRIVEN` under the
book's `-Wall`; the language is supported, the lint is wrong about a
pure-virtual prototype, an `extern` prototype and an interface signal driven
through a port.

### 3. Documented support: Icarus Verilog 13.0

Icarus 13.0 was published 2026-03-02 [iverilog releases, tag
v13_0](https://github.com/steveicarus/iverilog/releases/tag/v13_0). Its
documentation is thin on SystemVerilog by design. The README says the
compiler "also compiles a (slowly growing) subset of the SystemVerilog
language, as described in the IEEE 1800 standard", and its Unsupported
Constructs section closes with "The list of unsupported SystemVerilog
constructs is too large to enumerate here" [iverilog README,
v13-branch](https://github.com/steveicarus/iverilog/blob/v13-branch/README.md).
The `-g2012` flag "enables the IEEE1800-2012 standard, which includes
SystemVerilog" [iverilog command_line_flags.rst,
v13-branch](https://github.com/steveicarus/iverilog/blob/v13-branch/Documentation/usage/command_line_flags.rst).
The v13.0 release note lists elaboration, runtime, VPI and diagnostics fixes
and does not mention any of the constructs in §1 [iverilog v13.0 release
note](https://github.com/steveicarus/iverilog/blob/v13-branch/Documentation/releases/v13-0-release-note.rst).
The GitHub wiki the task brief names has a single Home page that points back
to the documentation site; there is no wiki "unsupported list" to cite
[iverilog wiki](https://github.com/steveicarus/iverilog/wiki), and the
`BUGS.txt` path returns 404 on the v13 branch.

Three kinds of primary evidence stand in for the missing list:

1. **The compiler's own "sorry:" diagnostics.** Icarus prefixes a recognized-
   but-unimplemented construct with `sorry:` and an unrecognized one with
   `syntax error`. Every `sorry:` in §4 is the project's own statement that
   the feature is known and not implemented (measured, this note, Icarus
   13.0).
2. **The regression suite.** `ivtest/ivltests` on the v13 branch holds 3,226
   `.v` files; 51 names contain `queue`, 41 `string`, 74 `enum`, 12 `union`,
   over 30 `sv_darray_*`, about 90 `sv_class*`, 11 `program*`, one
   `sv_interface.v`, and **none** containing `assoc`, `modport`, `clocking`,
   `mailbox`, `semaphore` or `virtual` [iverilog ivtest,
   v13-branch](https://github.com/steveicarus/iverilog/tree/v13-branch/ivtest/ivltests).
   Absence from the suite is not proof of absence from the compiler, but it
   matches the measurements exactly.
3. **The issue tracker.** "SV: Icarus does not support associative arrays"
   is open [#792, 2022-11-20](https://github.com/steveicarus/iverilog/issues/792);
   "SV: interface as port item is not supported" is open [#464,
   2021-01-02](https://github.com/steveicarus/iverilog/issues/464) and the
   pull request "Support SystemVerilog interface-typed module ports" merged on
   2026-05-16, two and a half months **after** the 13.0 tag [PR
   #1348](https://github.com/steveicarus/iverilog/pull/1348); "SV: class-handle
   $cast and static $typename" is an open, unmerged pull request [PR
   #1447](https://github.com/steveicarus/iverilog/pull/1447); "Added parse-only
   support for pure virtual methods" is an open pull request from 2021 [PR
   #469](https://github.com/steveicarus/iverilog/pull/469); "SV: issue with
   type compatibility across inheritance tree" is open [#422,
   2020-12-13](https://github.com/steveicarus/iverilog/issues/422). So the
   book's installed 13.0 lacks interface ports, but a reader who builds Icarus
   from master after May 2026 will have them; the chapter should say "13.0"
   and not "Icarus".

### 4. Measured support, construct by construct

All probes were compiled with the flags in §1.1; the text after each verdict
is the tool's own output, cut to the first informative lines (measured, this
note, Verilator 5.030 / Icarus 13.0, 2026-09-11).

**Types (p01).** Icarus prints `logic init=xxxxxxxx bit init=00000000`,
`isunknown(l)=1 isunknown(b)=0`. Verilator prints `logic init=00000000`,
`isunknown(l)=0`, so its comparison `l === 8'bx` fails and the probe reports
`FAIL`. Verilator's first attempt failed lint instead:
`%Warning-UNDRIVEN: Signal is not driven: 'i'` for an `int` declared but
never assigned; initializing the declarations cleared it.

**Arrays and containers (p02–p05).** Both tools ran p02 and p03 with the
right sums and sizes. Icarus on p04: `error: Type names are not valid
expressions here.` / `internal error: I do not know how to elaborate this
expression.` / `Expression type: 10PETypename` / `error: Dimensions must be
constant.`, identically for `[int]`, `[integer]`, `[string]`, `[bit [31:0]]`
and a typedef key; `int m[*];` gives `syntax error` / `Syntax error in
variable list`. Verilator on p04 needed `!= 0` around `first()` and `next()`:
`%Warning-WIDTHTRUNC: Logical operator WHILE expects 1 bit ... but ...
CMETHODHARD 'next' generates 32 bits`. Icarus on p05: `syntax error` /
`Malformed statement` at the `q[1:$]` slice; `sorry: 'sort()' array sorting
method is not currently supported.` The basic queue operations (i05a, i05b)
run on both.

**Structs, unions, enums, strings (p06–p09).** Icarus on p06: `sorry:
Unpacked structs not supported.` and `syntax error` at the named pattern
`'{tag: 4'hA, addr: 12'h123}`; positional `'{4'hA, 12'h123}` (i06a) and
member assignment (i06b) run. p07 and p08 ran on both. Icarus on strings:
`error: Method toupper is not a string method.`, likewise `compare`,
`tolower`, `getc`; `len`, `substr`, `atoi`, `itoa`, concatenation, `==` and
`$sformatf` run (i09c). Verilator refused a method call on a string literal:
`%Error: Syntax error: Not expecting CONST under a DOT in dotted expression`;
through a variable the same call runs.

**Interfaces (p10, p11, i10a–b, j10a–b).** Verilator's first p10 failed lint
only: `%Warning-BLKSEQ: Blocking assignment '=' in sequential logic process`
for `always #5 clk = ~clk` and `%Warning-INITIALDLY: Non-blocking assignment
'<=' in initial/final block`; with `clk <= ~clk` and blocking drives after
`#1` it runs. Icarus on every interface-port form (`bus_if b`, `bus_if.dut
b`, connected as `b` or `b.dut`): `syntax error` / `Errors in port
declarations.` Icarus with the interface instantiated in `top` and its
signals reached as `b.valid` runs (j10a). Icarus on the class holding
`virtual bus_if vif`: `syntax error` / `error: Invalid class item.`
Verilator runs p11.

**Classes (p12–p15, i12a, i13a–c, j12a, j15a–h).** Verilator ran every
class probe in this group. Icarus on p12: `sorry: Queues inside classes are
not yet supported.` and `sorry: Method name nesting is not supported yet.`;
with an `int payload[4]` property instead, whole-array copy fails `error: Got
0 indices, expecting 1 to index the property payload.`; with scalar
properties only (j12a) `new`, aliasing, copying and `!= null` run. Icarus on
p13: `syntax error` / `Malformed statement` at `counter::count()`; the same
static method called as `c1.count()` runs (i13a). Icarus on p14: `syntax
error` / `I give up.` at `class fifo #(type T = int, int DEPTH = 4);`. Icarus
on p15 compiles, and `vvp` stops: `Error: System task/function $cast() is
not defined by any module.` / `Program not runnable, 1 errors.`

The virtual-dispatch result deserves its own paragraph. Six variants were
run on Icarus: an `int`-returning virtual function through a base handle
(j15a `direct=9 via_base=0`; j15d `direct=2 via_base=1`), the same with an
explicit base constructor and `super.new()` (j15b), a `void` function that
prints (j15c prints `base` for `s.show()` and `square` for `sq.show()`), a
`void` function that sets a property (j15h `via_base r=1`), the override
declared without `virtual` (j15g), and the call made inside a task (j15f
`in_task=1`). In every case the **base-class body executed**. Direct calls
on the derived handle are correct. The build reports no warning. This is the
finding most likely to bite the chapter: an inheritance example on Icarus
compiles, runs, and quietly prints the wrong method's output.

**Clocking and program blocks (p16, p17).** Verilator's first p16 with
`modport tb (clocking cb)`: `%Error-UNSUPPORTED: Unsupported: Modport
clocking`. Without the modport the interface's clocking block, `@(b.cb)`,
`b.cb.valid <= 1` and the sampled `b.cb.ready` all behave, but `-Wall`
reports `%Warning-UNDRIVEN: Signal is not driven: 'ready'` for the interface
signal that the DUT drives through its output port; with `-Wno-UNDRIVEN` it
prints `cb.ready=1 data=77`. Icarus on p16: `syntax error` / `error: Invalid
module item.` at the `clocking` line. p17 (a `program` with ports driving a
DUT) prints `q=3c` on both.

**Randomization and synchronization (p18, p19, i18a, j19a–c, k04–k07,
k12).** Verilator with a `constraint` block or `randomize() with`:
`Process::open: execvp(z3): No such file or directory` / `%Warning: Unable to
communicate with SAT solver, please check its installation or specify a
different one in VERILATOR_SOLVER environment variable.` / `... Tried: $ z3
--in`, then `randomize()` returns 0 and the fields stay at 0; neither `z3`
nor `cvc5` is on this machine's PATH or in the `dvbook` env. Unconstrained
`rand`, `randc` (all four values seen once in four calls), `pre_randomize`,
`post_randomize` and `srandom` run without a solver. `solve a before b` and
`soft`: `%Warning-CONSTRAINTIGN: Constraint expression ignored (imperfect
distribution)`; `std::randomize(v)`: `%Warning-CONSTRAINTIGN: std::randomize
ignored (unsupported)`. Icarus: `Error: randomize is not a method of class
txn.`; `sorry: "inside" expressions not supported yet.`; `sorry: Constraint
declarations not supported.`; `syntax error` / `Errors in the constraint
block item list.` for `solve … before`. Icarus on `mailbox #(int) mb;` and
`semaphore sem;`: `syntax error` / `error: Invalid module instantiation`
(the parser does not know the type and reads the declaration as an
instance). `event`, `-> done`, `@done`, `fork/join`, `join_none`, `wait
fork` and `disable fork` run on both (j19a, k09).

**Handles in containers and the remaining class features (p20, p21, i20a,
j20a, k01–k03, k08, k10, k11, k15).** Icarus on p20: `Sorry: Queue of type
`class item{…}` is not yet supported.` and `Error: Class/null r-value not
allowed in this context.`; a fixed `item arr[4]` compiles and `vvp` refuses
to load it: `unresolved functor reference: v0x…` / `Program not runnable`.
Verilator ran all of them. Icarus on `interface class`, `virtual class` with
`pure virtual`, and a nested class: `syntax error` / `Invalid class item`;
on `extern function`: `sorry: External methods are not yet supported.`; on
`this.next = n` then `a.next.v`: `sorry: Nested member path not yet supported
for class properties.` Verilator: `%Error-UNSUPPORTED: Unsupported: class
within class`; `%Error-UNSUPPORTED: Unsupported: covergroup` / `cover point`
/ `covergroup within class`. Verilator's `UNDRIVEN` fired on the pure-virtual
`val`, the `extern`-declared `x` and the interface-class `str`, and
`VARHIDDEN` on a constructor argument named like its property; with those
warnings off every one of k01, k02, k11 and p21 runs. `protected`/`local`
(i21a) and a class inside a `package` (k10) run on both.

### 5. Does any open SystemVerilog simulator run classes fully?

No, and the two tools fail in different shapes. Verilator's class support
is broad in what it accepts and honest about what it refuses: the measured
refusals are all `%Error-UNSUPPORTED` at compile time (nested classes,
covergroups in classes, `modport … (clocking)`), or `CONSTRAINTIGN` for
constraint forms it ignores, and the one silent failure — constrained
`randomize()` without a solver — at least prints a warning to stderr and
returns 0. The assembled list of class-related features Verilator 5.030
does **not** run, from measurement and the change log (there is no such
list in the manual, see §2): nested class declarations; covergroups inside
classes; `std::randomize`; `solve … before` and `soft` constraints (ignored
with a warning); any constraint at all unless an SMT solver is installed;
`modport` items that export a clocking block. Everything else the chapter
needs — handles, `new`, static members, parameterization, inheritance with
virtual dispatch, `$cast`, abstract and interface classes, `extern` methods,
virtual interfaces, clocking blocks, mailboxes, semaphores, queues and
associative arrays of handles — ran (measured, this note, Verilator 5.030).

Icarus 13.0's class support is a subset with sharp edges: it accepts the
`class` keyword, scalar properties, constructors, methods, `extends`,
`super`, `protected`/`local`, static members through an instance and
classes in packages, but not parameterized classes, `::` scope resolution,
queue or handle-array properties, `$cast`, `randomize`, mailboxes,
semaphores, interface or abstract classes, `extern` methods, virtual
interfaces or clocking blocks — and it dispatches virtual methods statically
(measured, this note, Icarus 13.0; §4). The project's own README says the
unsupported list is "too large to enumerate" [iverilog README,
v13-branch](https://github.com/steveicarus/iverilog/blob/v13-branch/README.md).

No third open simulator was measured. The tooling landscape note the book
already holds (`research/tooling-landscape-hardware.md`) is the place for a
broader survey; this note's scope is the two simulators the build system
drives.

### 6. slang and cocotb, briefly

**slang** is a parser and elaborator, not a simulator: its site states it
"has full support for parsing and elaborating all SystemVerilog language
constructs, as specified in the 1800-2023 LRM", performing "full type
checking, cross-module elaboration, semantic verification, and data-flow
analysis" [sv-lang.com, accessed 2026-09-11](https://sv-lang.com/). The
current release is v11.0, published 2026-05-15 [slang releases, GitHub
API](https://github.com/MikePopoloski/slang/releases/tag/v11.0). On this
machine there is **no `slang` binary on PATH**, but `pyslang 11.0.0` is
installed in the `dvbook` conda env (measured, this note), and the site
lists `pip install pyslang` as one of its three install routes. So a
lint-only example that shows the full language (a parameterized interface
class, a `covergroup` in a class) can be checked by `python -c "import
pyslang; ..."` under the book's existing `EXAMPLE_LANG := python` recipe, or
by a `slang` binary the reader installs; the note does not verify pyslang's
CLI behavior and the chapter should not claim more than "it parses". The
existing `refs.bib` key `slang-docs` covers the site.

**cocotb** describes itself as enabling "users to test and verify their chip
designs in Python as opposed to VHDL, (System)Verilog, or other EDA-specific
languages" and "can be used with any simulator supporting the industry-
standard VPI, VHPI or FLI interfaces" [cocotb documentation, stable,
accessed 2026-09-11](https://docs.cocotb.org/en/stable/). Its simulator page
says "cocotb supports Icarus 11.0+" and "cocotb supports Verilator 5.036+"
[cocotb simulator support, stable, accessed
2026-09-11](https://docs.cocotb.org/en/stable/simulator_support.html). The
second sentence matters: the installed Verilator is 5.030, so the book's
`conda run -n dvbook make run` cocotb path should be understood as running
on **Icarus**, which is what a Python-track contrast wants anyway: every
construct in §1 that Icarus cannot compile is a construct that cocotb's
Python replaces (classes, containers, strings, randomization), leaving the
simulator to run only the RTL. The installed cocotb is 2.1.0 and pyuvm is
5.0.0 (measured, this note).

### 7. What this means for the chapter's examples

- **Default rule:** every Chapter 5 example ships under Verilator with the
  book's flags and is also run under Icarus by `scripts/check-examples.sh`
  only when the matrix says it can. An example that only Verilator runs
  says so in one line of prose, not in a footnote.
- **The four-state example runs on Icarus only.** It is the one place the
  chapter should drive the event-driven simulator on purpose, and the Ch. 4
  `run_both.sh` pattern is the model.
- **Inheritance and virtual methods: Verilator only, and the chapter should
  say why in an In Practice callout** — the Icarus result is silently wrong,
  which is a better lesson about tool trust than any correct output.
- **Constrained randomization cannot be shown as a runnable example on this
  toolchain.** Unconstrained `rand`/`randc` can. If the chapter shows a
  `constraint`, it is a lint-only listing (Verilator `--lint-only` accepts
  it) or it documents the `z3` requirement and `VERILATOR_SOLVER`; the
  check-examples run would need the solver installed to go green.
- **Lint hygiene for shipped listings:** initialize declared `int`s
  (`UNDRIVEN`); generate clocks with `<=` (`BLKSEQ`); do not mix `<=` into
  `initial` (`INITIALDLY`); compare `first()`/`next()` against 0
  (`WIDTHTRUNC`); do not name a constructor argument after its property
  (`VARHIDDEN`); expect `UNDRIVEN` on pure-virtual and `extern` prototypes
  and on interface signals driven through ports, and add `-Wno-UNDRIVEN`
  for those examples with a comment saying which signal and why.
- **Avoid on both:** `modport … (clocking cb)`, method calls on string
  literals, nested classes, covergroups in classes, `std::randomize`.

### Unsourced-claims table

| Claim | Status |
|---|---|
| The zeros seen for uninitialized `logic` under Verilator come from the `+verilator+rand+reset` runtime default | Inferred from the `--x-initial unique` doc text and the observed output; the runtime option's own doc paragraph was not located in the 5.030 guide. Treat as plausible, not cited. |
| Icarus dispatches virtual methods statically | Measured in six variants; no Icarus document or issue states it in those words. Issue #422 is adjacent, not identical. |
| Icarus master after 2026-05-16 accepts interface ports | Inferred from the merged PR; not measured (no master build here). |
| pyslang can be used from the book's Python recipe as a lint step | Not tried; the note only records that the package imports. |
| cocotb's `make run` in this repo actually runs on Icarus | Inferred from the version floor in cocotb's docs versus the installed Verilator; not measured in this session. |

### Key sources (suggested BibTeX keys)

Existing keys to reuse: `verilator-languages`, `verilator-warnings`,
`verilator-changes`, `verilator-docs`, `icarus-quirks`, `slang-docs`,
`cocotb-docs`. Note that `verilator-languages` and `verilator-warnings` point
at `guide/latest/`; where the chapter quotes a limitation it should cite the
5.030-tagged file, so a release-pinned entry is proposed.

- `verilator-languages-5030` — Snyder, W. and Verilator contributors,
  "Verilator User's Guide: Language Limitations", revision tagged v5.030,
  2024-10-27. https://github.com/verilator/verilator/blob/v5.030/docs/guide/languages.rst
- `verilator-exe-5030` — same authors, "Verilator User's Guide: verilator
  Executable Options" (`--x-assign`, `--x-initial`), v5.030.
  https://github.com/verilator/verilator/blob/v5.030/docs/guide/exe_verilator.rst
- `verilator-changes` (existing) — used here for the 5.020–5.030 entries on
  virtual interfaces, clocking blocks and constrained randomization.
- `icarus-readme` — Icarus Verilog contributors, "README", v13 branch.
  https://github.com/steveicarus/iverilog/blob/v13-branch/README.md
- `icarus-flags` — "iverilog Command Line Flags", v13 branch.
  https://github.com/steveicarus/iverilog/blob/v13-branch/Documentation/usage/command_line_flags.rst
- `icarus-release-13` — "Release V13.0", 2026-03-02.
  https://github.com/steveicarus/iverilog/releases/tag/v13_0
- `icarus-issue-792` — "SV: Icarus does not support associative arrays",
  GitHub issue, 2022-11-20. https://github.com/steveicarus/iverilog/issues/792
- `icarus-issue-464` — "SV: interface as port item is not supported", GitHub
  issue, 2021-01-02. https://github.com/steveicarus/iverilog/issues/464
- `icarus-pr-1348` — "Support SystemVerilog interface-typed module ports",
  merged 2026-05-16. https://github.com/steveicarus/iverilog/pull/1348
- `icarus-issue-422` — "SV: issue with type compatibility across inheritance
  tree", 2020-12-13. https://github.com/steveicarus/iverilog/issues/422
- `slang-release-11` — Popoloski, M., "slang v11.0", 2026-05-15.
  https://github.com/MikePopoloski/slang/releases/tag/v11.0
- `cocotb-simulators` — cocotb contributors, "Simulator Support", stable
  docs, accessed 2026-09-11. https://docs.cocotb.org/en/stable/simulator_support.html

### Confidence notes

- **High:** every matrix cell. Each is a file on disk, a command with fixed
  flags, and an output captured the same day; the runner and all probes are
  in the scratchpad and can be re-run in under two minutes.
- **High:** the Verilator quotations, taken from the v5.030-tagged files, not
  the rolling site.
- **Medium:** the Icarus "documented" column, because Icarus documents by
  `sorry:` message, regression-test name and issue tracker rather than by
  manual. The issue and PR dates come from the GitHub API and are exact; the
  inference that master now supports interface ports is not measured.
- **Medium:** the reading of the virtual-dispatch result as "static
  dispatch". The behavior is unambiguous across six probes; the mechanism is
  inferred.
- **Low:** anything about pyslang beyond "it imports", and the claim that
  the repo's cocotb examples run on Icarus rather than Verilator; both are
  one command away from being measured and should be before the chapter
  relies on them.
- **Not covered:** commercial simulators (the matrix is about the book's
  open toolchain), Verilator versions newer than 5.030 (cocotb's floor is
  5.036, so an upgrade would change two rows of §6 and possibly several of
  §1), and Icarus builds from master.
