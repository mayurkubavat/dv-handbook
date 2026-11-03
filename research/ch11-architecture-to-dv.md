---
title: "Research note: Chapter 11 — From Architecture to Verification, a DMA case study"
date: 2026-11-03
author: research-agent
status: done
feeds: Ch. 11
---

# Chapter 11 — From Architecture to Verification: evidence note

Scope: how industry teams take a block from an architecture specification
to a microarchitecture, a verification plan, and a testbench with its
coverage model; the protocol rules the chapter's checks come from; and a
measured account of the chapter's DMA in two versions. The chapter's plan
(author-approved 2026-11-03) set the outline; this note records what each
source was read for and what was measured, so the prose can be checked
against it.

Labels: **[methodology]** textbook, **[standard]** protocol specification,
**[primary/open]** open-source project documentation, **[measured]** run
by the chapter's examples on Verilator 5.052 and Icarus 13.0.

## 1. Sources read for the chapter

### 1.1 Protocol rules [standard]

- **ARM IHI 0024B, AMBA 3 APB Protocol Specification v1.0, Issue B,
  17 August 2004.** Read from a university course copy
  ([umich.edu](https://web.eecs.umich.edu/~prabal/teaching/eecs373-f12/readings/ARM_AMBA3_APB.pdf));
  Arm's own portal (`developer.arm.com/documentation/ihi0024/latest`)
  302-redirects to `support.arm.com`, which served only a page shell.
  - §2.2.1, read transfer with no wait states: "The slave must provide the
    data before the end of the read transfer."
  - §2.3, error response: "PSLVERR is only considered valid during the last
    cycle of an APB transfer, when PSEL, PENABLE, and PREADY are all HIGH."
- **ARM IHI 0022C, AMBA AXI Protocol Specification v2.0, Issue C, 2010.**
  Read from Arm's documentation service
  ([documentation-service.arm.com](https://documentation-service.arm.com/static/64256e84314e245d086bc88f)).
  This issue includes AXI4-Lite as Chapter 14.
  - §3.1, Handshake process: "All five channels use the same VALID/READY
    handshake to transfer data and control information." "It is not
    permitted to wait until READY is asserted before asserting VALID."
    VALID stays asserted until the handshake; READY may be asserted before
    VALID.
  - §3.3, Dependencies between channel handshake signals: "the slave can
    wait for AWVALID or WVALID, or both, before asserting AWREADY."
  - This closes the gap the Chapter 3 note recorded (no Arm wording was
    retrievable then). The quotations above are the only Arm wording the
    chapter prints.

### 1.2 Textbooks [methodology]

- **Hennessy and Patterson, *Computer Architecture: A Quantitative
  Approach*, 6th ed., Morgan Kaufmann, 2017, ISBN 9780128119051.**
  Publisher page read for metadata; Chapter 1 is "Fundamentals of
  Quantitative Design and Analysis". Cited for the method (targets by
  arithmetic, confirmed by measurement) and for the term *precise
  exception*; no page is cited. *Confidence: high for the method, which the
  publisher page and the 2017 Turing citation state; the book was not
  reread for this note.*
- **Dally and Harting, *Digital Design: A Systems Approach*, Cambridge,
  2012, ISBN 9780521199506.** Table of contents read from the publisher:
  Chapter 16 "Datapath sequential logic" with §16.3 "Control and data
  partitioning"; Chapter 17 "Factoring finite-state machines". The chapter
  cites the book only for the existence of these two moves at those
  places.
- **Mehta, *ASIC/SoC Functional Design Verification*, Springer, 2018,
  doi 10.1007/978-3-319-59418-7.** Publisher page: eighteen chapters, from
  UVM, SVA and coverage to SoC interconnect verification and the product
  design life cycle. Further reading only.
- Already in `refs.bib` and used as the earlier chapters used them:
  Bergeron 2006, Spear and Tumbush 2012, Piziali 2004, Wile, Goss and
  Roesner 2005, Cummings 1998 and 2019 on FSMs, the UVM user's guide.

### 1.3 Production comparison [primary/open]

- **OpenTitan DMA, Theory of Operation**
  ([opentitan.org](https://opentitan.org/book/hw/ip/dma/doc/theory_of_operation.html)),
  read 2026-11-03. Sections: block diagram, memory regions, modes of
  operation (generic and hardware handshake), security checks,
  configuration notes, inline hashing, clocking and reset, SoC
  integration. No state machine is described. No throughput figure is
  stated; the only requirement-like sentence is "Shared modules are thus
  preferable if they can meet throughput and latency requirements."
- **OpenTitan DMA, DV document**
  ([opentitan.org](https://opentitan.org/book/hw/ip/dma/dv/index.html)),
  read 2026-11-03. CIP testbench; four TileLink interfaces; a testbench
  diagram; "the `dma_scoreboard` checks every transaction within a transfer
  occurs as expected"; six DMA covergroups (`dma_config_cg`,
  `dma_tlul_error_cg`, `dma_status_cg`, `dma_error_code_cg`,
  `dma_interrupt_cg`, `dma_intr_src_cg`); the RAL model "is created with
  the `ralgen` FuseSoC generator script automatically when the simulation
  is at the build stage."
- **Carried from the Chapter 2 note** (`research/ch02-verification-planning.md`,
  sections 4.2 and 5.1): the dvsim testplanner schema, cited as
  `opentitan-testplanner` for the plan's `name`, `stage`, `desc` and
  `tests` fields, and the OpenTitan development stages, cited as
  `opentitan-dev-stages` for the V0 to V3 stage wording. Not re-fetched
  for this chapter.
- **The source design**: `mayurkubavat/SystemC`, `projects/dma`, file
  `rtl/verilog/dma_engine.v` at commit 9b3bd55, copied byte for byte as
  `examples/ch11-architecture-to-verification/rtl/dma_v1.v`. Its own
  UVM-SystemC testbench's AXI slave answers READY only after VALID and
  accepts the write address and data together (read from the repository's
  slave agent).

## 2. Measured [measured]

All from the chapter's ten examples, green under
`scripts/check-examples.sh ch11` on 2026-11-03, after review round 3.

| Claim | Example | Output |
|---|---|---|
| Two registers have two procedural writers in v1, none in v2 | `v1-lint` | `MULTIDRIVENPROC` on `ctrl` (line 184) and `status` (line 189) |
| `XFER_LEN = 65536` moves no word and reports done | `v1-findings` | `moved 0 words`, `STATUS 2`, IRQ after 10 cycles, counted from the start of programming |
| A write to a busy channel is ignored without an error | `v1-findings` | `PSLVERR=0`, `DST_ADDR` unchanged |
| An APB read returns the previous read's data | `v1-findings` | three reads, each one behind |
| A READY-first slave hangs v1 before any read | `v1-findings` | `ARVALID high for 0 cycles`, 0 handshakes |
| AW and W on different edges deadlock v1 | `v1-findings` | 1 AR, 1 AW, 1 W, 0 B |
| A random-ready slave hangs v1 too | `v1-findings` | `random_ready`: 0 handshakes; verdict 5 of 6 questions fail |
| Cycles per word, 64-word copy | `throughput` | v1 7.98; v2 4.05 (WAIT_VALID), 3.03 (READY_FIRST) |
| v1's phases per word | `waves` | READ_REQ 3, READ_RESP 1, WRITE_REQ 3, WRITE_RESP 1 |
| v1's random test varied no slave style | `v1-random` | `style_cp` hit only `wait_valid`; every FSM arc hit, `r_err` 10 times |
| v2 meets the plan | `v2-tests` | directed, 15 register rules, a 65,535-word copy (`len_cp.max`=1; 262,156 cycles from the first programming write to the status clear, about 262,143 for the copy itself, 3.3 s of wall time on the review machine) and 300 random rounds pass; zero bins are `over`, the two zero-length error cells and the two maximum-length error cells |
| A read error with words queued is reached | `v2-tests` | `rd_err_cp.queued` = 9 (per-channel event: an error on a channel that has words in the FIFO) |
| Round robin while both owe reads | `v2-tests` | 999 grants, 485 and 514, 0 repeats; 0 reads started at a full FIFO |
| A fixed-priority arbiter breaks `DMA-101` | scratch mutant of `dma_v2.sv` (`c = k - 1`), not kept | random test fails on seeds 1 to 5, with 1152, 1270, 998, 916 and 933 repeated grants; 0 reads at a full FIFO |
| The first draft (PRECISE=0) loses queued words on a read error | `v2-tests` | 14 of 600 channel transfers (300 rounds) fail; passes directed, regs, abort and maxlen (scratch build) |
| The draft's run diverges from version 2's despite the shared seed | scratch build of the draft with `--coverage` | `rd_err_cp.queued` = 14, one per failure, against 9 in version 2's run |
| A second language agrees, and its slave must vary to matter | `v2-cocotb` | 30 rounds on Icarus, 0 failures; with the write response delayed 0 to 4 cycles a PRECISE=0 copy fails 3 checks, and without the delay an earlier version of the test passed the draft |
| The plan report fails while a must-have row has no test | `vplan` | revision 1: 11 of 13, failed on `DMA-009`; revision 2 adds the maxlen test: 12 of 13, "every must-have item has a passing test"; `DMA-104` (should) still open |

Register semantics. The register map (`regs/dma_regs.yaml`) was written
from what the source RTL does, since the source project has no register
specification: field widths, reset values and the start and IRQ bits are
read from `dma_v1.v`. The chapter therefore says what the RTL does and
asks which behavior is the specification, rather than quoting a
specification sentence.

## 3. Constraints folded into the outline

1. Every covergroup construct used is one Chapter 8 measured as correct on
   Verilator 5.052; every bin count is read from the `.dat`, never from a
   percentage.
2. The SystemVerilog testbench is Verilator-only (covergroups, clocking
   blocks); the cocotb mirror runs version 2 on Icarus, with
   `dma_v2.sv` written without `inside`, which Icarus 13 refuses.
3. Assertions and UVM chapters are not written: protocol rules are shown as
   monitor checks and coverpoints, with the SVA and UVM forms as forward
   pointers, by description rather than chapter number.
4. Figures are generated from the example files (`figures/gen_ch11_figures.py`)
   and reproduce no copyrighted figure.

## 4. Confidence notes

- The OpenTitan pages are live documentation and will drift; the chapter
  says what they contained when read.
- The textbooks were cited from publisher metadata and tables of contents,
  not reread; no page number is printed.
- `DMA-104` (reset during a transfer) is left without a test on purpose; it
  is a should-have, so the plan report passes and lists it. Writing it is an
  exercise.
- The fixed-priority result was measured on a scratch copy that is not part
  of the examples; the chapter states it as measured on five seeds.
