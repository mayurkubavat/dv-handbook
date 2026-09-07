# Chapter 3 research, part 3: pipelines, interfaces, and structural extraction

Scope: flow-control contracts (valid/ready, back-pressure, FIFOs), the block
boundary as a specification, and what open tools can extract from RTL. Every
factual claim carries a URL. Fetch failures are recorded verbatim in §6.

Access date for undated pages: 2026-09-07.

---

## 1. Pipelines, handshakes and queues

### 1.1 The valid/ready contract, as specified

The chapter's central claim is that a two-wire handshake is a *contract with
normative rules*, not a convention. The cleanest openly-readable statement of
those rules is the SiFive TileLink specification, §4.1 "Flow Control Rules"
[SiFive TileLink Specification, Version 1.7-draft, 2017-08-21](https://static.dev.sifive.com/docs/tilelink/tilelink-spec-1.7-draft.pdf)
**[standard]**. Quoting the specification directly:

> "To regulate the flow of beats in TileLink channels, receivers raise the
> channel ready signal to indicate their ability to accept a beat. The receiver
> lowers the ready signal to indicate that they are busy and are not accepting a
> beat. Conversely, the sender of a beat raises the channel valid signal to
> indicate the presence of a beat on the channel. Only when both ready and valid
> are raised is the beat exchanged."

And the rules themselves, verbatim from §4.1:

> "In order to implement correct ready-valid handshaking, these rules must be
> followed:
> - If ready is LOW, the receiver must not process the beat and the sender must
>   not consider the beat processed.
> - If valid is LOW, the receiver must not expect the control or data signals to
>   be a syntactically correct TileLink beat.
> - valid must never depend on ready. If a sender wishes to send a beat, it must
>   assert valid independently of whether the receiver signals that it is ready.
> - As a consequence, there must be no combinational path from ready to valid or
>   any of the control and data signals.
> - A receiver may only hold ready LOW in accordance with the deadlock freedom
>   rules in Section 4.2."

The asymmetry the chapter needs — the *destination* may look at valid, the
*source* may not look at ready — is stated explicitly in the same section:

> "Anything not forbidden is allowed. In particular, it is acceptable for a
> receiver to drive ready in response to valid or any of the control and data
> signals. For example, an arbiter may lower ready if a valid request is made for
> an address which is busy. However, whenever possible, it is recommended that
> ready be driven independently so as to reduce the handshaking circuit depth."

One important difference from AXI that the chapter must not blur: TileLink beats
are *revocable* at the channel level.

> "Note that a sender may raise valid and then lower it on the following cycle,
> even if the message was not accepted on the previous cycle. ... Furthermore,
> the sender may change the contents of the control and data signals when a
> message was not accepted."

AXI takes the opposite position (VALID, once asserted, must stay asserted and the
payload must remain stable until the transfer completes). See §6 for why the ARM
wording could not be fetched in this session; do not paraphrase ARM clause text
into the chapter until it is quoted from the specification itself.

Burst atomicity is also specified, which matters for stream-style pipelines:

> "It is forbidden in TileLink to interleave the beats of different messages on a
> channel. Once a burst has begun, the sender must not send beats for any other
> message until the last beat of the burst has been accepted by the receiver."

### 1.2 The same contract elsewhere

That the contract is ecosystem-independent is supported by OpenTitan, which
adopts TileLink-UL as the mandatory boundary for every peripheral
[OpenTitan Comportability Definition and Specification, accessed 2026-09-07](https://opentitan.org/book/doc/contributing/hw/comportability/index.html)
**[primary]**: "All peripherals use TileLink-UL (TileLink-Uncached-Lite, aka
TL-UL) as their interface to the framework." OpenTitan's own bus documentation
restates the handshake and adds throughput restrictions — "Only one request (read
or write) per cycle" and "Only one response (read or write) per cycle"
[OpenTitan TL-UL bus documentation, accessed 2026-09-07](https://opentitan.org/book/hw/ip/tlul/index.html)
**[primary]** — and notes a deliberate deviation from the specification's reset
requirement, which is itself a good chapter example of a project documenting
where it departs from a standard.

A practitioner restatement of the AXI form of the rules, usable as a cited source
in place of the ARM text, is
[ZipCPU, "AXI Handshaking Rules", 2021-08-28](https://zipcpu.com/blog/2021/08/28/axi-rules.html)
**[primary]**, which gives them as: "Nothing happens unless `xVALID && xREADY`";
"Something _always_ happens anytime `xVALID && xREADY`"; and "Nothing can change
unless `!xVALID || xREADY`" — the last being the payload-stability rule, which the
article also expresses as the formal property `assert($stable(M_AXIS_TDATA))`
under a stall.

### 1.3 Back-pressure and skid buffers

The skid buffer is the standard answer to "I must register my ready output and
still not drop data."
[ZipCPU, "Building a skid buffer for AXI processing", 2019-05-22](http://zipcpu.com/blog/2019/05/22/skidbuffer.html)
**[primary]** states the handshake obligation as "any time `VALID & !READY`, the
respective data values must remain constant into the next clock cycle" and "Once
o_valid goes high, the data cannot change until the clock after i_ready."

The two-slot argument, in the article's terms: when a stage registers its stall
signal, the upstream stage does not learn about back-pressure until it has already
launched a beat, so "the data needs to go somewhere or get dropped." The buffer
therefore holds an output register plus one internal register (`o_data` and
`r_data`) — one slot for the beat being presented downstream, one for the beat
already in flight. The performance argument is in the same source: the author
reports 100% throughput on both read and write channels for his AXI slave,
against "just less than a 50% read throughput" for a vendor demonstration core
without the technique. That is a practitioner measurement of one design, not a
general benchmark, and the chapter should say so.

### 1.4 FIFOs: pointer width, full/empty, and the off-by-one

The canonical treatment is
["Simulation and Synthesis Techniques for Asynchronous FIFO Design", SNUG San Jose 2002 (rev. 1.3, Nov 2005)](https://www.paradigm-works.com/papers/)
**[industry paper]**, with a companion paper "…with Asynchronous Pointer
Comparisons" (rev. 1.3, Aug 2020). Both are listed as "Voted Best Paper 1st
Place." The sunburst-design.com paper URLs now 301-redirect to
paradigm-works.com and the PDFs sit behind a login, so the paper text could not
be quoted here (see §6).

The technique itself is quotable from
[ZipCPU, "Crossing clock domains with an Asynchronous FIFO", 2018-07-06](https://zipcpu.com/blog/2018/07/06/afifo.html)
**[primary]**, which describes the Cummings design as using `N+1` address bits for
a pointer into a `2^N`-element FIFO, and gives the full condition as: "It is full
when wbin-rbin = 2^N. In that case, the bottom AW address bits are identical, but
the top bit is different." Empty is pointer equality across all bits. The same
article states the capacity consequence the chapter wants — "his FIFO holds a
full `2^N` elements. The FIFO I presented earlier only holds `(2^N)-1` elements" —
and the Gray-code motivation: "if you want to check whether or not two pointers
are identical, you only need to check whether the two Gray coded pointers are
identical", because "only one bit will ever change at any time."

The chapter's framing — *a counter's width is an assumption about capacity* — has
a live example in OpenTitan, where the occupancy output width is computed as
`DepthW = prim_util_pkg::vbits(Depth+1)`, i.e. wide enough for the values 0
through Depth inclusive, not 0 through Depth-1
[lowRISC/opentitan, `hw/ip/prim/rtl/prim_fifo_sync.sv`, accessed 2026-09-07](https://raw.githubusercontent.com/lowRISC/opentitan/master/hw/ip/prim/rtl/prim_fifo_sync.sv)
**[primary]**. The `+1` is exactly the off-by-one under discussion.

### 1.5 Occupancy invariants as assertions and coverage

The same file is the best evidence that occupancy invariants are written as
assertions in production RTL. Quoted verbatim:

- `` `ASSERT(depthShallNotExceedParamDepth, !empty |-> depth_o <= DepthW'(Depth)) ``
- `` `ASSERT(OnlyRvalidWhenNotUnderRst_A, rvalid_o -> ~under_rst) ``
- `` `ASSERT_KNOWN_IF(DataKnown_A, rdata_o, rvalid_o) ``

The first is the occupancy bound; the second and third are reset-behavior and
X-propagation obligations on the same boundary. A pre-built checker library also
exists: the Accellera Open Verification Library is "a library of assertion
checkers intended to be used by design, integration, and verification engineers
to check for good/bad behavior in simulation, emulation, and formal
verification", latest version 2.8.1 released 2014-04-08
[Accellera, Open Verification Library, accessed 2026-09-07](https://www.accellera.org/downloads/standards/ovl)
**[standard]**.

---

## 2. Interfaces and the block boundary

### 2.1 SystemVerilog interface and modport

The normative home of interfaces is IEEE Std 1800, "IEEE Standard for
SystemVerilog--Unified Hardware Design, Specification, and Verification
Language", current edition IEEE 1800-2023, published 2024-02-28
[IEEE 1800-2023, 2024-02-28](https://standards.ieee.org/ieee/1800/7743/)
**[standard]**. Clause 25 of the LRM is the interfaces clause: the ChipsAlliance
conformance suite indexes its interface tests under "Chapter 25: Interface
syntax" [sv-tests results, accessed 2026-09-07](https://chipsalliance.github.io/sv-tests-results/)
**[docs]**. The LRM itself is paywalled, so the chapter should cite the clause by
name and number but must not quote LRM text that has not been read.

Second-hand confirmation that modports are direction contracts comes from the
Yosys manual, which lists among supported constructs "SystemVerilog interfaces
(SVIs), including modports for specifying whether ports are inputs"
[Yosys manual, "Verilog support", accessed 2026-09-07](https://yosyshq.readthedocs.io/projects/yosys/en/latest/using_yosys/verilog.html)
**[docs]**.

Worth reporting honestly: interfaces are not universally embraced in RTL. The
lowRISC coding style guide lists "Interfaces" among discouraged language features
[lowRISC Verilog Coding Style Guide, accessed 2026-09-07](https://raw.githubusercontent.com/lowRISC/style-guides/master/VerilogCodingStyle.md)
**[primary]**; OpenTitan instead names the contract with packed structs
(`tl_h2d_t`, `tl_d2h_t`) per the TL-UL documentation cited above. The chapter can
use this as a real disagreement rather than presenting interfaces as settled
practice.

### 2.2 What a boundary specification contains

An openly citable, complete example of "everything a block boundary must declare"
is OpenTitan's comportability specification **[primary]** (URL above). It requires,
per peripheral: at least one device interface on the chip bus, using TL-UL; a
declared primary clock plus any secondary clocks; reset behavior, stated
normatively as "Resets within the design are **asynchronous active low**" with
deassertion synchronized to the associated clock; a register map — "Each
peripheral must define its collection of registers in the specified register
format" — from which "hardware, software, and documentation collateral" are
generated; and a declaration of interrupts versus alerts, with three
auto-generated registers `INTR_STATE`, `INTR_ENABLE`, `INTR_TEST`. Error
responses are part of the bus contract: TL-UL responses carry `d_error`, and the
response opcode is determined by the request — "If the original request was Get,
then the corresponding response must be AccessAckData. Otherwise, the response
must be AccessAck"
[OpenTitan TL-UL Protocol Checker specification, accessed 2026-09-07](https://opentitan.org/book/hw/ip/tlul/doc/TlulProtocolChecker.html)
**[primary]**.

This gives the chapter the full list — signals, protocol, clocking, reset,
register map, optionality, error responses — from one source that a reader can
open. ARM's APB and AXI-Lite would be the more familiar small examples; they are
not cited here because the specification text could not be retrieved (§6).

### 2.3 Protocol monitors and assertion-based contracts

OpenTitan's `tlul_assert.sv` is a working, readable protocol monitor and the best
citation for "the boundary is checked by assertions" **[primary]** (URL above).
Two details are directly useful to the chapter:

1. It validates opcodes, size and address alignment, mask contiguity, data
   validity, source-ID uniqueness ("preventing multiple pending requests per
   source"), X-values on control signals, and that no requests are outstanding at
   end of simulation. Sample rule: "Only the following 3 opcodes are legal: Get,
   PutFullData, PutPartialData."
2. The same property is an *assumption* or an *assertion* depending on which side
   of the boundary the monitor is bound to — device mode uses an `_M` suffix,
   host mode an `_A` suffix — because formal verification needs the environment
   constrained rather than checked. Simulation behavior is identical. This is a
   genuinely instructive point for a verification textbook.

The standard trade reference is Foster, Krolnik and Lacey, *Assertion-Based
Design* (Springer). The Springer catalog page redirected to an authentication
endpoint in this session, so full bibliographic details (edition, year, ISBN)
must be confirmed before the book is cited (§6).

---

## 3. Structural extraction from RTL

### 3.1 Yosys: JSON schema and the flip-flop cell library

Flow: `read_verilog -sv` → `hierarchy -check -top <top>` → `proc` → optionally
`flatten` → `opt_clean` → `write_json`.

- `hierarchy` "check, expand and clean up design hierarchy"; `-check` "generates
  an error when an unknown module is used as cell type"; `-top <module>` means
  "Modules outside this tree (unused modules) are removed"; `-auto-top`
  "automatically determine the top of the design hierarchy". `flatten` "flattens
  the design by replacing cells by their implementation", and "Cells and/or
  modules with the 'keep_hierarchy' attribute set will not be flattened"
  [Yosys manual, hierarchy passes, accessed 2026-09-07](https://yosyshq.readthedocs.io/projects/yosys/en/latest/cmd/index_passes_hierarchy.html)
  **[docs]**.
- `proc` "translate[s] processes to netlists", running `proc_clean`, `proc_rmdead`,
  `proc_prune`, `proc_init`, `proc_arst`, `proc_rom`, `proc_mux`, `proc_dlatch`,
  `proc_dff`, `proc_memwr`, `proc_clean`, `opt_expr -keepdc`
  [Yosys manual, proc passes, accessed 2026-09-07](https://yosyshq.readthedocs.io/projects/yosys/en/latest/cmd/index_passes_proc.html)
  **[docs]**. This step is mandatory before register extraction: RTLIL processes
  are not cells, and "Some passes refuse to operate on modules that still contain
  `RTLIL::Process` objects"
  [Yosys manual, RTL Intermediate Language, accessed 2026-09-07](https://yosyshq.readthedocs.io/projects/yosys/en/latest/yosys_internals/formats/rtlil_rep.html)
  **[docs]**. The same page gives the hierarchy Design → Module →
  cells/wires/processes/memories, the `\`-vs-`$` identifier convention (user names
  vs. auto-generated), and that "Busses (signal vectors) are represented using a
  single wire object with a width more than 1."

**JSON schema** [Yosys manual, backends / `write_json`, accessed 2026-09-07](https://yosyshq.readthedocs.io/projects/yosys/en/latest/cmd/index_backends.html#write-json-write-design-to-a-json-file)
**[docs]**. Top level: `creator`, `modules`, and `models` (with `-aig`). Each
module has `attributes`, `parameter_default_values`, `ports`, `cells`,
`memories`, `netnames`. A port is `{"direction": "input"|"output"|"inout",
"bits": <bit_vector>, "offset": …, "upto": …, "signed": …}`. A cell is
`{"hide_name": 1|0, "type": …, "model": …, "parameters": {…}, "attributes": {…},
"port_directions": {…}, "connections": {…}}`. Critically for a Python extractor:
signal bits are unique integers, and constant-driven bits appear as the *strings*
`"0"`, `"1"`, `"x"`, `"z"` in the same array — so a bit vector is a mixed
list of ints and strings, and net identity is integer identity.

**Register cells.** All are in the "Registers" section of the word-level cell
library [Yosys manual, word-level register cells, accessed 2026-09-07](https://yosyshq.readthedocs.io/projects/yosys/en/latest/cell/word_reg.html)
**[docs]**, with parameters and ports as follows:

| Cell | Parameters | Extra control ports |
|---|---|---|
| `$dff` | WIDTH, CLK_POLARITY | — |
| `$dffe` | + EN_POLARITY | EN |
| `$adff` | + ARST_POLARITY, ARST_VALUE | ARST |
| `$adffe` | + EN_POLARITY, ARST_POLARITY, ARST_VALUE | ARST, EN |
| `$sdff` | + SRST_POLARITY, SRST_VALUE | SRST |
| `$sdffe` | + EN_POLARITY, SRST_POLARITY, SRST_VALUE | SRST, EN |
| `$sdffce` | + EN_POLARITY, SRST_POLARITY, SRST_VALUE | SRST, EN |
| `$aldff` | + ALOAD_POLARITY | ALOAD, AD |
| `$aldffe` | + EN_POLARITY, ALOAD_POLARITY | ALOAD, EN, AD |
| `$dffsr` | + SET_POLARITY, CLR_POLARITY | SET[W-1:0], CLR[W-1:0] |
| `$dffsre` | + SET_POLARITY, CLR_POLARITY, EN_POLARITY | SET, CLR, EN |

All have `D` input and `Q` output of WIDTH bits. Note `SET`/`CLR` on `$dffsr` are
per-bit vectors, not scalars — a per-bit set/reset structure a naive extractor
will get wrong. The `$adlatch`, `$dlatch`, `$dlatchsr` and `$sr` cells are in the
same section and are what an unintended latch shows up as.

**Front-end limits.** With `-sv`, Yosys supports `assert`/`assume`/`restrict`/
`cover`, `always_comb`/`always_ff`/`always_latch`, `logic`/`bit`, `rand` free
variables, packages (not nested), typedefs, enums, packed structs/unions,
multidimensional arrays, interfaces with modports, and `unique`/`unique0`/
`priority`. Unsupported: type casts, structure literals, array literals, and
array assignment of unpacked arrays; on the Verilog-2005 side, `tri`/`triand`/
`trior`, `config` and `disable` (URL above, **[docs]**). Anything using the
unsupported constructs will not reach the JSON at all.

### 3.2 pyslang / slang: the AST route

slang is "a C++ library and command-line tool" for "lexing, parsing, type
checking, and elaboration" of SystemVerilog, offering "Full type checking,
cross-module elaboration, semantic verification, and data-flow analysis" and
targeting "the 1800-2023 LRM"
[sv-lang.com, accessed 2026-09-07](https://sv-lang.com/) **[docs]**. It claims to
be "the fastest and most compliant SystemVerilog frontend according to the open
source chipsalliance test suite" — a project self-claim, though the sv-tests
comparison cited in §2.1 is the independent scoreboard behind it. The driver has
`--ast-json` for dumping the elaborated AST; Python bindings install with
`pip install pyslang`; license MIT
[MikePopoloski/slang, accessed 2026-09-07](https://github.com/MikePopoloski/slang)
**[docs]**. Packaging note the chapter's example must respect: the standalone
pyslang repository was **archived 2025-01-18** and is read-only, its packaging
having moved into the upstream slang repository
[MikePopoloski/pyslang, accessed 2026-09-07](https://github.com/MikePopoloski/pyslang)
**[docs]**.

What it gives that a netlist does not: source locations, the unelaborated syntax
tree, declarations that synthesis erases (typedefs, parameters, generate
structure, assertions), and errors with diagnostics. What it does not give: a
synthesized netlist — no inferred flip-flop cells, no post-optimization net
identity, no answer to "which registers actually exist."

### 3.3 Verilator: AST dump and SARIF diagnostics

`--json-only`: "Create JSON output only, do not create any other output" — the
elaborated AST as `.tree.json` plus `.tree.meta.json`, with
`--json-only-output`, `--json-only-meta-output`, `--no-json-edit-nums` (for
run-to-run stability) and `--no-json-ids`. `--lint-only`: "Check the files for
lint violations only, do not create any other output". `--diagnostics-sarif`:
"Enables diagnostics output into a Static Analysis Results Interchange Format
(SARIF) file, a standard, JSON-based format for the output of static analysis
tools such as linters", with `--diagnostics-sarif-output <filename>`
[Verilator manual, verilator arguments, accessed 2026-09-07](https://veripool.org/guide/latest/exe_verilator.html)
**[docs]**. The manual itself flags that the JSON format evolves across versions.

**`--xml-only` is gone.** The changelog records "Add DEPRECATED warning on
`--xml-only` and `--xml-output`" in Verilator 5.036 (2025-04-27) and "Remove
deprecated `--xml-only`" in 5.044 (2026-01-01); `--diagnostics-sarif` arrived in
5.038 (2025-07-08)
[Verilator Changes, accessed 2026-09-07](https://raw.githubusercontent.com/verilator/verilator/master/Changes)
**[docs]**. The chapter must describe the JSON route, not the XML route.

### 3.4 Other routes

- **Verible**: `verible-verilog-syntax` exports the concrete syntax tree with
  `--export_json`, which "Uses JSON for output. Intended to be used as an input
  for other tools", plus `--printtree`
  [Verible, verilog_syntax, accessed 2026-09-07](https://chipsalliance.github.io/verible/verilog_syntax.html)
  **[docs]**. Syntax only — no elaboration.
- **Surelog / UHDM**: "a complete SystemVerilog 2017 front-end: a preprocessor, a
  parser, an elaborator for both design and testbench", emitting UHDM databases
  that follow "the Standard VPI API", consumable from C/C++ or through a Python
  wrapper; Apache 2.0
  [chipsalliance/Surelog, accessed 2026-09-07](https://github.com/chipsalliance/Surelog)
  **[docs]**.

### 3.5 What no structural tool can decide without a specification

The following are *inferences from what the formats above contain*, not sourced
claims, and are labeled as such in §4. None of the four routes emits: which
clocks are asynchronous to which (Yosys JSON carries cells, nets, parameters and
attributes — no clock-relationship or timing information; that lives in an SDC or
equivalent constraints file, outside every format described here); the intended
reset sequence and release order; which clock-domain crossings have been reviewed
and waived; whether a register array is a FIFO, a scoreboard or a lookup table;
or which of two structurally identical counters is a capacity bound and which is
an index. A netlist answers *what exists*; it never answers *what was meant*. The
chapter's worked example should therefore be framed as producing a **candidate
list requiring a specification to interpret**, not an answer.

---

## 4. Commonly repeated but unsourced claims

| Claim | Where it is repeated | Status |
|---|---|---|
| "A source must not wait for READY before asserting VALID; VALID must remain asserted until the transfer completes" (AXI wording) | Universally attributed to ARM IHI 0022 §A3.2 | **Not verified here.** The rule is confirmed for TileLink §4.1 and paraphrased by ZipCPU for AXI; the ARM clause number and wording were not retrievable (§6). Do not print a clause number. |
| `$sdffce` gates the synchronous reset with EN while `$sdffe` does not | Yosys community usage | Plausible from the identical parameter lists, but the cell page prose was not captured. Verify against the `word_reg.html` text before asserting. |
| Cliff Cummings is the author of the SNUG 2002 FIFO papers | Ubiquitous | Almost certainly correct, but the fetched paradigm-works listing gave title/venue/year without an author line. Confirm from the PDF before citing an author. |
| "A skid buffer costs zero throughput" | Practitioner blogs | Supported only as a single-design measurement (§1.3); state as such. |
| Avalon-ST states the same valid/ready rules | Common in the FPGA world | Unverified — the Intel documentation URL redirected to a 404 redirector. Use TileLink/OpenTitan instead. |
| Structural extraction cannot recover clock relationships | This note, §3.5 | Inference from the documented contents of the four formats, not a cited claim. Present as reasoning. |

---

## 5. Suggested BibTeX keys

| Key | Citation | Used by |
|---|---|---|
| `sifive2017tilelink` | SiFive, Inc. *SiFive TileLink Specification, Version 1.7-draft*, 2017-08-21. https://static.dev.sifive.com/docs/tilelink/tilelink-spec-1.7-draft.pdf | §1.1, §1.2 |
| `opentitan2026comportability` | lowRISC. *Comportability Definition and Specification*, OpenTitan documentation, accessed 2026-09-07. https://opentitan.org/book/doc/contributing/hw/comportability/index.html | §1.2, §2.2 |
| `opentitan2026tlul` | lowRISC. *TileLink-UL bus*, OpenTitan documentation, accessed 2026-09-07. https://opentitan.org/book/hw/ip/tlul/index.html | §1.2, §2.2 |
| `opentitan2026tlulchecker` | lowRISC. *TL-UL Protocol Checker Specification*, accessed 2026-09-07. https://opentitan.org/book/hw/ip/tlul/doc/TlulProtocolChecker.html | §2.3 |
| `opentitan2026primfifo` | lowRISC. `hw/ip/prim/rtl/prim_fifo_sync.sv`, OpenTitan, accessed 2026-09-07. https://raw.githubusercontent.com/lowRISC/opentitan/master/hw/ip/prim/rtl/prim_fifo_sync.sv | §1.4, §1.5 |
| `lowrisc2026style` | lowRISC. *Verilog Coding Style Guide*, accessed 2026-09-07. https://github.com/lowRISC/style-guides/blob/master/VerilogCodingStyle.md | §2.1 |
| `gisselquist2019skid` | Gisselquist, D. "Building a skid buffer for AXI processing", ZipCPU, 2019-05-22. http://zipcpu.com/blog/2019/05/22/skidbuffer.html | §1.3 |
| `gisselquist2021axirules` | Gisselquist, D. "AXI Handshaking Rules", ZipCPU, 2021-08-28. https://zipcpu.com/blog/2021/08/28/axi-rules.html | §1.2 |
| `gisselquist2018afifo` | Gisselquist, D. "Crossing clock domains with an Asynchronous FIFO", ZipCPU, 2018-07-06. https://zipcpu.com/blog/2018/07/06/afifo.html | §1.4 |
| `cummings2002fifo` | *Simulation and Synthesis Techniques for Asynchronous FIFO Design*, SNUG San Jose, 2002 (rev. 1.3, Nov 2005). https://www.paradigm-works.com/papers/ | §1.4 |
| `ieee2023sv` | IEEE Std 1800-2023, *IEEE Standard for SystemVerilog — Unified Hardware Design, Specification, and Verification Language*, 2024-02-28. https://standards.ieee.org/ieee/1800/7743/ | §2.1 |
| `chipsalliance2026svtests` | ChipsAlliance. *sv-tests results*, accessed 2026-09-07. https://chipsalliance.github.io/sv-tests-results/ | §2.1, §3.2 |
| `accellera2014ovl` | Accellera. *Open Verification Library*, v2.8.1, 2014-04-08. https://www.accellera.org/downloads/standards/ovl | §1.5 |
| `yosys2026json` | YosysHQ. *Yosys manual: backends (`write_json`)*, accessed 2026-09-07. https://yosyshq.readthedocs.io/projects/yosys/en/latest/cmd/index_backends.html | §3.1 |
| `yosys2026regcells` | YosysHQ. *Yosys manual: word-level register cells*, accessed 2026-09-07. https://yosyshq.readthedocs.io/projects/yosys/en/latest/cell/word_reg.html | §3.1 |
| `yosys2026rtlil` | YosysHQ. *Yosys manual: RTL Intermediate Language*, accessed 2026-09-07. https://yosyshq.readthedocs.io/projects/yosys/en/latest/yosys_internals/formats/rtlil_rep.html | §3.1 |
| `yosys2026verilog` | YosysHQ. *Yosys manual: Verilog support*, accessed 2026-09-07. https://yosyshq.readthedocs.io/projects/yosys/en/latest/using_yosys/verilog.html | §2.1, §3.1 |
| `slang2026` | Popoloski, M. *slang — SystemVerilog compiler and language services*, accessed 2026-09-07. https://sv-lang.com/ and https://github.com/MikePopoloski/slang | §3.2 |
| `verilator2026manual` | Verilator developers. *Verilator manual: verilator arguments*, accessed 2026-09-07. https://veripool.org/guide/latest/exe_verilator.html | §3.3 |
| `verilator2026changes` | Verilator developers. *Changes*, accessed 2026-09-07. https://raw.githubusercontent.com/verilator/verilator/master/Changes | §3.3 |
| `verible2026syntax` | ChipsAlliance. *Verible: verilog_syntax*, accessed 2026-09-07. https://chipsalliance.github.io/verible/verilog_syntax.html | §3.4 |
| `surelog2026` | ChipsAlliance. *Surelog*, accessed 2026-09-07. https://github.com/chipsalliance/Surelog | §3.4 |

---

## 6. Confidence notes and gaps

**High confidence** (text quoted from the source in this session): TileLink §4.1
flow-control rules; OpenTitan comportability, TL-UL and protocol-checker
requirements; `prim_fifo_sync` assertions and `DepthW` computation; all Yosys
command, cell and JSON-schema details; Verilator option text and the `--xml-only`
removal timeline; Verible, Surelog, slang and pyslang facts; OVL version and date.

**Fetch failures, recorded honestly.**

1. **ARM specifications could not be read.** `developer.arm.com/documentation/
   ihi0022/latest/` 301-redirects to `support.arm.com`, which returns a
   JavaScript shell with no document text; `static.docs.arm.com` no longer
   resolves (DNS failure); the AMD/Xilinx AXI reference-guide PDFs redirect to
   `adaptivesupport.amd.com`; `web.archive.org` is not reachable from this
   session's fetch tool; and the browser-automation extension was not connected.
   The session's web-search quota was also exhausted before this work began, so
   no alternative mirror could be located. **Consequence: the chapter must not
   state an ARM clause number or quote ARM wording for the AXI or APB handshake
   until someone reads IHI 0022 / IHI 0024 directly.** §1.1 and §1.2 give
   equivalent, fully quotable material from TileLink and OpenTitan, which is
   arguably better for an open textbook.
2. **Cummings SNUG papers**: sunburst-design.com now redirects to
   paradigm-works.com and the PDFs require login. Title, venue, year, revision
   and award are sourced; author is not (§4).
3. **Avalon-ST**: the Intel documentation URL redirected into a 404 redirector.
4. **Foster/Krolnik/Lacey, *Assertion-Based Design***: the Springer catalog page
   redirected to an authentication endpoint; edition/year/ISBN unconfirmed. §2.3
   substitutes OpenTitan's `tlul_assert.sv` as the citable example.
5. **IEEE 1800 clause text**: paywalled. Clause 25 is confirmed as the interfaces
   clause only indirectly, via the sv-tests chapter index. Cite by number and
   name; do not quote.

**Deliberate scope choice.** §1.1 uses TileLink rather than AXI as the normative
anchor. This is defensible on its merits — the rules are stated more explicitly
and the document is freely readable — but the chapter should still name AXI as
the industrially dominant instance, and should flag TileLink's revocable-valid
divergence from AXI so a reader does not carry the wrong rule into an AXI review.
