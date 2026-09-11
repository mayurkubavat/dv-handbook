---
title: "Research note: open-source and academic agentic tooling for RTL and DV"
date: 2026-09-07
author: research-agent
status: draft
feeds: Appendix on the agent tool layer
---

# Open-source and academic tooling

Scope: what an agent could actually call today, on an open license, to parse
SystemVerilog, run a simulation, read a waveform, or be scored on a
verification task. Every entry below was checked against the repository or the
paper itself on 2026-09-07, with license, last commit and release date taken
from the hosting platform's API rather than from a README. Four pages did not
resolve and are recorded as such in §8; two of them have no Wayback Machine
snapshot either. The dominant finding is that the parsing and waveform layers
are mature and well licensed, the protocol layer on top of them is roughly one
year old and thin, and the benchmark layer is heavily skewed toward *generating*
RTL rather than *verifying* it.

## 1. Tool-protocol servers and AI integrations for hardware

This layer barely existed before 2026 and should be presented to readers as
early work, not as settled infrastructure.

**wave-mcp** — [Tencent/wave-mcp, GitHub, 2026-09-07](https://github.com/Tencent/wave-mcp).
MIT (the license file carries a Tencent preamble, so GitHub's detector reports
"NOASSERTION"; the text itself is the MIT license). Created 2026-07-27, last
commit 2026-09-07, release v0.2.3 on 2026-09-05, 182 stars. From Tencent's
Penglai Lab verification team. It reads FST directly (auto-converting VCD and
FSDB), pairs the waveform with a pyslang-elaborated netlist, and exposes 34
tools: hierarchy exploration, signal queries, driver and fan-in analysis,
backward value and X-root-cause tracing, pass/fail waveform diff, and a browser
viewer the agent drives and reads back. It runs no simulator; it consumes
waveforms your flow produced. On PyPI as `wave-mcp` 0.2.3, Python >= 3.10
([PyPI, 2026-09-07](https://pypi.org/project/wave-mcp/)). Its README reports
validation over a production chip project plus 27 OpenTitan and 38 XiangShan
IPs, with 2.25 million signal-level value checks
([README.en.md, 2026-09-07](https://github.com/Tencent/wave-mcp/blob/main/README.en.md)) —
**the project's own claims, unreproduced by any third party**. The most
substantial open hardware MCP server found, and the one to show readers, with
its youth stated.

**waveform-mcp** — [jiegec/waveform-mcp, GitHub, 2026-09-07](https://github.com/jiegec/waveform-mcp).
MIT, last commit 2026-08-01 (`chore: release v0.6.0`), 48 stars. A Rust MCP
server reading VCD and FST through `wellen`, shipped on crates.io. Far smaller
in scope than wave-mcp — waveform reading, not driver analysis — but a clean,
legible example of the pattern.

**surfer-mcp** — [PaoloRondot/surfer-mcp, GitHub, 2026-09-07](https://github.com/PaoloRondot/surfer-mcp).
**No license file**, 6 stars, last commit 2026-05-08. Drives the Surfer
waveform viewer over WCP (see §3). Interesting as a proof of concept that an
agent can steer a GUI viewer; **do not send readers here as a dependency** —
unlicensed code is not reusable, and it has been quiet for four months.

**mcp-vcd** — [SeanMcLoughlin/mcp-vcd, GitHub, 2026-09-07](https://github.com/SeanMcLoughlin/mcp-vcd).
MIT, v0.1.1 released 2024-12-23, **last commit 2024-12-23**. Historically the
first of its kind, and **dead**: nothing in twenty months. Cite only as
provenance.

**zesun33/mcp-verilog, mcp-yosys, mcp-cocotb, mcp-openroad, mcp-fpga** — five
Apache-2.0 servers wrapping Verilog lint/simulate, Yosys, cocotb, OpenROAD and
FPGA flows, all created 2026-09-05, pushed 2026-09-07
([zesun33/mcp-verilog, GitHub, 2026-09-07](https://github.com/zesun33/mcp-verilog)).
READMEs are substantive and CI is configured, but each is two days old with zero
stars and no release. Borrow the *design goal* they illustrate — structured JSON
diagnostics instead of raw compiler output dumped into the context window — and
say plainly that they are unproven.

**Naming caution:** "wave MCP" is badly overloaded; a search for `wave-mcp`
returns servers for Wave Accounting, Wave Terminal and the Tracktion Waveform
DAW alongside the hardware ones.

**Not found:** no general slang/pyslang MCP server (wave-mcp embeds pyslang but
exposes no general parsing API), and no EDA-vendor MCP announcement via
repository or arXiv search — weak evidence, since vendor announcements live in
press releases this note did not survey.

## 2. Language tooling: parsers, elaborators, linters

This is the mature layer. All four projects below are actively maintained and
permissively licensed.

**slang** — [MikePopoloski/slang, GitHub, 2026-09-07](https://github.com/MikePopoloski/slang).
MIT, 1,132 stars, release v11.0 on 2026-05-15, last commit 2026-09-05. A
SystemVerilog front end doing lexing, parsing, type checking and elaboration —
the elaboration is what makes it answer semantic questions, not just syntactic
ones. **The archived-pyslang question resolves cleanly:**
[MikePopoloski/pyslang](https://github.com/MikePopoloski/pyslang) is
**archived**, last commit 2025-01-18
([GitHub, 2026-09-07](https://github.com/MikePopoloski/pyslang); an earlier state
is preserved at
[Wayback, 2026-01-02](http://web.archive.org/web/20260102100046/https://github.com/MikePopoloski/pyslang)).
Packaging moved into the slang repository, where the binding lives in `pyslang/`
and the most recent commit is a pyslang build change. PyPI `pyslang` 11.0.0 was
uploaded 2026-05-15, matching slang v11.0
([PyPI, 2026-09-07](https://pypi.org/project/pyslang/)). So: **cite slang, install
`pyslang` from PyPI, and never link the archived repository.**

**Verible** — [chipsalliance/verible, GitHub, 2026-09-07](https://github.com/chipsalliance/verible).
Apache-2.0 (confirmed from the `LICENSE` file; GitHub reports "NOASSERTION"
because of a Debian-style `Files: *` header), 1,931 stars, last commit
2026-09-02, rolling release `v0.0-4163-g6cce8f19` on 2026-09-01. Parser,
style linter, formatter and language server. The agent-relevant feature is
`verible-verilog-syntax --export_json`, documented as "Uses JSON for output.
Intended to be used as an input for other tools", alongside `--printtokens`,
`--printrawtokens` and `--printtree`
([tools/syntax/README.md, 2026-09-07](https://github.com/chipsalliance/verible/blob/master/verible/verilog/tools/syntax/README.md)).
It also ships a Python wrapper and worked examples
(`export_json_examples/verible_verilog_syntax.py`, `print_tree.py`,
`print_modules.py`) — the shortest path from a `.sv` file to a navigable tree in
Python. Caveat: 610 open issues.

**Surelog and UHDM** — [chipsalliance/Surelog](https://github.com/chipsalliance/Surelog)
and [chipsalliance/UHDM](https://github.com/chipsalliance/UHDM), both
Apache-2.0, both at v1.87 released 2026-08-24, both last committed 2026-09-04
([GitHub, 2026-09-07](https://github.com/chipsalliance/Surelog)). Surelog is a
preprocessor, parser and elaborator emitting UHDM, a serialized model of the
IEEE SystemVerilog object model with a VPI interface. The pairing matters to the
appendix's argument: UHDM is an *interchange format between tools*, exactly what
a tool layer wants underneath it.

**tree-sitter-systemverilog** — [gmlarumbe/tree-sitter-systemverilog, GitHub, 2026-09-07](https://github.com/gmlarumbe/tree-sitter-systemverilog).
MIT, 58 stars, v0.4.0 released 2026-07-17, last commit 2026-07-20. One primary
maintainer, Gonzalo Larumbe — worth stating, since bus factor rather than
abandonment is the risk here. An incremental, error-tolerant grammar: right for
editor-style navigation of *broken* code, wrong for anything needing elaboration
or types, where slang or Surelog belong.

**Verilator** — [verilator/verilator, GitHub, 2026-09-07](https://github.com/verilator/verilator).
`LGPL-3.0-only OR Artistic-2.0` (from the repository README's SPDX line;
GitHub reports "NOASSERTION" for the dual license), 3,912 stars, latest tag
v5.052, last commit 2026-09-07. Three flags matter to an agent, all confirmed in
the manual source
([docs/guide/exe_verilator.rst, 2026-09-07](https://github.com/verilator/verilator/blob/master/docs/guide/exe_verilator.rst)):

- `--json-only` — "Create JSON output only". The format "is intended to be used
  to leverage Verilator's parser and elaboration to feed to other downstream
  tools", but the manual warns "the JSON format is still evolving; there will be
  some changes in future versions." Quote that caveat rather than presenting the
  format as stable. Companions: `--json-only-output`,
  `--json-only-meta-output`, `--dump-tree-json`.
- `--diagnostics-sarif` — emits diagnostics as SARIF, "a standard, JSON-based
  format for the output of static analysis tools such as linters", with
  `--diagnostics-sarif-output <filename>`. The most underappreciated flag here:
  it turns lint output into a schema shared with the software world.
- `--coverage`, an alias for `--coverage-line --coverage-toggle
  --coverage-expr --coverage-fsm --coverage-user`, plus
  `--coverage-per-instance`. Note `--coverage-fsm` (native FSM state and arc
  coverage) and `--coverage-user` (user covergroups).

**Yosys** — [YosysHQ/yosys, GitHub, 2026-09-07](https://github.com/YosysHQ/yosys).
ISC, 4,741 stars, v0.68 released 2026-08-05, last commit 2026-09-07.
`write_json` writes a JSON netlist of the current design, with `-aig`,
`-compat-int`, `-selected` and `-noscopeinfo` options and a documented top-level
shape of `creator` / `modules` / attributes
([backends/json/json.cc, 2026-09-07](https://github.com/YosysHQ/yosys/blob/main/backends/json/json.cc)).
RTLIL is the in-memory representation behind it. Companion tools, all active but
**none of which cut releases** — pin a commit, not a version:

- [YosysHQ/sby](https://github.com/YosysHQ/sby) — SymbiYosys, formal
  verification front end. 545 stars, last commit 2026-08-04, no releases.
- [YosysHQ/eqy](https://github.com/YosysHQ/eqy) — equivalence checking. 62
  stars, last commit 2026-09-03, no releases.
- [YosysHQ/mcy](https://github.com/YosysHQ/mcy) — mutation coverage. ISC, 97
  stars, last commit 2026-08-04, no releases. Directly relevant to any chapter
  arguing that coverage numbers overstate verification quality.

## 3. Waveform and simulation libraries

**wellen** — [ekiwi/wellen, GitHub, 2026-09-07](https://github.com/ekiwi/wellen).
BSD-3-Clause, 144 stars. **GitHub's release list is misleading**: the newest
GitHub release is v0.11.1 from 2024-09-24, but crates.io shows 0.25.6 last
updated 2026-07-21 with 237,760 downloads
([crates.io, 2026-09-07](https://crates.io/crates/wellen)). The project is
maintained; only its GitHub releases are stale. Fast VCD, FST and GHW parsing in
Rust, and the parsing engine under both Surfer and `jiegec/waveform-mcp`.

**pylibfst** — [mschlaegl/pylibfst, GitHub, 2026-09-07](https://github.com/mschlaegl/pylibfst).
16 stars, last commit 2025-06-11 — **dormant, roughly fifteen months idle**. The
`COPYING` file states the package mixes licenses: the Python CFFI wrapper under
`LICENSE-pylibfst` and the bundled FST C library under `LICENSE-fst`, so it is
not a single-license dependency. It still matters because it is the FST reader
inside wave-mcp; present it as a working component with a quiet upstream, not as
a project to build on unexamined.

**Surfer** — [surfer-project/surfer, GitLab, 2026-09-07](https://gitlab.com/surfer-project/surfer).
**EUPL-1.2** (via the GitLab API's license field) — a copyleft license, which
is worth flagging to readers, since it differs sharply from the permissive
licenses elsewhere in this note. 194 stars, created 2022-12-22, last activity
2026-09-06, v0.7.0 released 2026-04-27. Runs natively, in the browser at
`app.surfer-project.org`, and headless via a `surver` remote-file server.
**WCP (Waveform Control Protocol) is real but undocumented.** It is a dedicated
`surfer-wcp` workspace crate in the root `Cargo.toml`, implemented with a TCP
server under `libsurfer/src/wcp/` (`mod.rs`, `wcp_handler.rs`, `wcp_server.rs`)
and integration tests (`libsurfer/src/tests/wcp.rs`, `wcp_tcp.rs`). Yet the user
book's contents has no WCP entry
([docs/SUMMARY.md, 2026-09-07](https://gitlab.com/surfer-project/surfer/-/blob/main/docs/SUMMARY.md)),
`docs.surfer-project.org/book/wcp.html` 404s with no Wayback snapshot, and the
crate is unpublished on crates.io. **Say this plainly:** an agent-drivable
viewer protocol ships in production Surfer today, and using it means reading the
source.

**GTKWave** — [gtkwave/gtkwave, GitHub, 2026-09-07](https://github.com/gtkwave/gtkwave).
**GPL-2.0** — the most restrictive license here. 1,015 stars, last commit
2026-08-23, **no releases on GitHub**. Reads LXT, LXT2, VZT, FST, GHW and VCD.
Its Tcl scripting interface is the long-standing way to automate a viewer;
Surfer's WCP is the modern alternative. For new work prefer wellen for reading,
Surfer for viewing.

**cocotb** — [cocotb/cocotb, GitHub, 2026-09-07](https://github.com/cocotb/cocotb).
BSD-3-Clause, 2,495 stars, v2.1.0 released 2026-08-30 and on PyPI the same day
([PyPI, 2026-09-07](https://pypi.org/project/cocotb/)), last commit 2026-09-07.
The agent-relevant piece is the runner: `cocotb_tools.runner` with `get_runner`,
documented at `docs/source/runner.rst`, which builds and launches a test from
Python without a Makefile, plus a pytest plugin at
`src/cocotb_tools/_pytest/plugin.py`
([runner.rst, 2026-09-07](https://github.com/cocotb/cocotb/blob/master/docs/source/runner.rst)).
Describe the run in Python, invoke it programmatically, collect results through
pytest — which makes cocotb the easiest simulation target for a tool layer.

## 4. Research and benchmarks

The generation-side benchmarks are well established; the verification-side ones
are fewer, newer, and more valuable to this book. Listed roughly in order of
usefulness to the appendix.

**CVDP (Comprehensive Verilog Design Problems)** — **[research]** Pinckney,
Deng, Ho, Tsai et al., *Comprehensive Verilog Design Problems: A Next-Generation
Benchmark Dataset for Evaluating Large Language Models and Agents on RTL Design
and Verification*, [arXiv:2506.14074, 2025-06-17](https://arxiv.org/abs/2506.14074).
Harness at [NVlabs/cvdp_benchmark, GitHub, 2026-09-07](https://github.com/NVlabs/cvdp_benchmark),
Apache-2.0, 218 stars, last commit 2026-06-08; dataset at
[nvidia/cvdp-benchmark-dataset, Hugging Face, 2026-09-07](https://huggingface.co/datasets/nvidia/cvdp-benchmark-dataset),
last modified 2026-07-21. **This is the answer to "a benchmark about
verification rather than generation"** — it scores agents, not just models, and
covers verification tasks explicitly. Two honesty points its README states
itself: twenty datapoints were withheld from the public release for harness and
licensing reasons, and reference solutions were excluded to limit contamination.
Its adoption by the Silicon Integration Initiative's LLM Benchmarking Coalition
makes it the likeliest of these benchmarks to still matter when the book is
read.

**FVEval** — **[research]** Kang, Liu, Bany Hamad, Suhaib et al., *FVEval:
Understanding Language Model Capabilities in Formal Verification of Digital
Hardware*, [arXiv:2410.23299, 2024-10-15](https://arxiv.org/abs/2410.23299).
Code at [NVlabs/FVEval, GitHub, 2026-09-07](https://github.com/NVlabs/FVEval),
44 stars, v1.1.0 released 2025-04-03, **last commit 2025-04-03 — dormant for
seventeen months**. Still the clearest formal-verification-specific evaluation;
cite the paper, and warn that the repository is not being maintained.

**AutoBench** and **CorrectBench** — **[research]** Qiu, Zhang, Drechsler,
Schlichtmann et al., *AutoBench: Automatic Testbench Generation and Evaluation
Using LLMs for HDL Design*, [arXiv:2407.03891, 2024-07-04](https://arxiv.org/abs/2407.03891),
and *CorrectBench: Automatic Testbench Generation with Functional
Self-Correction using LLMs for HDL Design*,
[arXiv:2411.08510, 2024-11-13](https://arxiv.org/abs/2411.08510). The testbench
counterpart to VerilogEval, and directly on this book's subject.

**AssertLLM** — **[research]** Fang, Li, Li, Yan et al., *AssertLLM: Generating
and Evaluating Hardware Verification Assertions from Design Specifications via
Multi-LLMs*, [arXiv:2402.00386, last updated 2026-02-25](https://arxiv.org/abs/2402.00386);
the ASP-DAC'25 version is [arXiv:2411.14436, 2024-11-04](https://arxiv.org/abs/2411.14436).
Assertion generation from specifications. The v4 update in February 2026 shows
the line of work is live; follow-ups include DeepAssert
([arXiv:2509.14668](https://arxiv.org/abs/2509.14668)) and AssertMiner
([arXiv:2511.10007](https://arxiv.org/abs/2511.10007)).

**VerilogEval** — **[research]** the widely used generation benchmark, best
cited in its second edition: Pinckney, Batten, Liu, Ren et al., *Revisiting
VerilogEval: A Year of Improvements in Large-Language Models for Hardware Code
Generation*, [arXiv:2408.11053, updated 2025-02-03](https://arxiv.org/abs/2408.11053),
which explicitly revisits the original arXiv:2309.07544. Code at
[NVlabs/verilog-eval, GitHub, 2026-09-07](https://github.com/NVlabs/verilog-eval),
466 stars, **last commit 2025-02-07 — dormant for nineteen months**, though the
repository is not archived.

**RTLLM** — **[research]** Lu, Liu, Zhang, Xie, *RTLLM: An Open-Source Benchmark
for Design RTL Generation with Large Language Model*,
[arXiv:2308.05345, 2023-08-10](https://arxiv.org/abs/2308.05345). Code at
[hkust-zhiyao/RTLLM, GitHub, 2026-09-07](https://github.com/hkust-zhiyao/RTLLM),
MIT, 224 stars, last commit 2026-08-15 tagged `v2.1` — **the best-maintained of
the generation benchmarks**, and the one to prefer over VerilogEval if only one
is shown.

**VeriGen** — **[research]** Thakur, Ahmad, Pearce, Tan et al., *VeriGen: A
Large Language Model for Verilog Code Generation*,
[arXiv:2308.00708, 2023-07-28](https://arxiv.org/abs/2308.00708). An early open
fine-tuned Verilog model; cite as provenance.

**VeriContaminated** — **[research]** Wang, Shao, Bhandari, Mankali et al.,
*VeriContaminated: Assessing LLM-Driven Verilog Coding for Data Contamination*,
[arXiv:2503.13572, updated 2025-06-12](https://arxiv.org/abs/2503.13572).
A companion to any benchmark figure the book quotes: it argues that published
Verilog benchmark scores are inflated by training-data contamination. A textbook
citing pass@k numbers should cite this alongside them.

**Agentic coverage work** — **[research]** two 2026 preprints that measure
*limits* rather than wins: Patel, Chhabria, Arora, *Understanding Inference-Time
Token Allocation and Coverage Limits in Agentic Hardware Verification*,
[arXiv:2604.15657, updated 2026-07-05](https://arxiv.org/abs/2604.15657); and
Lowe, Hilaneh, Babbit, Gopalan et al., *Spec2Cov: An Agentic Framework for Code
Coverage Closure of Digital Hardware Designs*,
[arXiv:2604.15606, updated 2026-05-21](https://arxiv.org/abs/2604.15606).
Both are recent preprints, neither yet shown as peer-reviewed at these URLs.

## 5. Open silicon projects as reference flows

**OpenTitan** — [lowRISC/opentitan, GitHub, 2026-09-07](https://github.com/lowRISC/opentitan).
Apache-2.0, 3,632 stars, last commit 2026-09-07. Its DV methodology document is
the best public statement of a production-grade open verification flow:
"quality must win, and thus we aim to create a verification product that is
equal to the quality required from a full production silicon chip tapeout"; it
specifies UVM 1.2 constrained-random simulation plus formal property
verification, and requires every DUT to ship a testbench, a testplan, a DV
document, a test suite and a way to build, run and report status
([doc/contributing/dv/methodology/README.md, 2026-09-07](https://github.com/lowRISC/opentitan/blob/master/doc/contributing/dv/methodology/README.md)).
It is also candid that VCS is the signoff simulator and JasperGold the FPV tool,
naming Verilator, Yosys and cocotb as open alternatives the project is "working
towards a future where these are signoff-grade" — a useful corrective to any
claim that the open flow is already sufficient.

**dvsim has moved — this is the correction most likely to save a reader.**
`util/dvsim/dvsim.py` in the OpenTitan repository now returns 404; only report
parsers (`LintParser.py`, `verible-report-parser.py`,
`verilator-report-parser.py`, and vendor lint parsers) remain in that directory.
The regression manager itself now lives at
[lowRISC/dvsim, GitHub, 2026-09-07](https://github.com/lowRISC/dvsim),
Apache-2.0, described as "a build and run system written in Python that runs a
variety of EDA tool flows", v1.52.1 released 2026-09-03, last commit 2026-09-03.
The repository is young (created 2025-07-23) with 13 stars, but it is the live
home. The machine-readable side an agent would target is unchanged: OpenTitan
still carries 128 `*_sim_cfg.hjson` regression configurations, one per IP
(`hw/ip/uart/dv/uart_sim_cfg.hjson`, `hw/ip/i2c/dv/i2c_sim_cfg.hjson`, …) — a
rare public example of a verification flow described as data rather than as a
shell script.

## 6. Maturity table

| Project | What it does | License | Last activity | Maintained? | Send a reader here? |
|---|---|---|---|---|---|
| slang / pyslang | SV parse, typecheck, elaborate | MIT | commit 2026-09-05; v11.0 2026-05-15 | Yes, actively | **Yes** — but link `slang`, never the archived `pyslang` repo |
| Verible | Lint, format, LSP, `--export_json` tree | Apache-2.0 | commit 2026-09-02 | Yes | **Yes** — best path to a JSON syntax tree |
| Surelog / UHDM | Elaborate to a VPI object model | Apache-2.0 | commit 2026-09-04; v1.87 2026-08-24 | Yes | Yes, for interchange-format work |
| tree-sitter-systemverilog | Incremental, error-tolerant grammar | MIT | commit 2026-07-20; v0.4.0 2026-07-17 | Yes, one main maintainer | Yes, for editor-style navigation only |
| Verilator | Simulate, lint, JSON AST, SARIF, coverage | LGPL-3.0-only OR Artistic-2.0 | commit 2026-09-07; v5.052 | Yes, very | **Yes** |
| Yosys | Synthesize, `write_json`, RTLIL | ISC | commit 2026-09-07; v0.68 2026-08-05 | Yes, very | **Yes** |
| sby / eqy / mcy | Formal, equivalence, mutation coverage | ISC / NOASSERTION | commits 2026-08-04 to 2026-09-03 | Yes, but **no releases** | Yes — pin a commit |
| wellen | Rust VCD/FST/GHW parsing | BSD-3-Clause | crates.io 0.25.6, 2026-07-21 | Yes (GitHub releases are stale) | **Yes** — cite crates.io, not GitHub releases |
| pylibfst | FST in Python | Mixed (see `COPYING`) | commit 2025-06-11 | **Dormant ~15 months** | Only with the caveat stated |
| Surfer | Waveform viewer; WCP remote control | **EUPL-1.2** (copyleft) | activity 2026-09-06; v0.7.0 2026-04-27 | Yes | Yes — but note WCP is undocumented |
| GTKWave | Waveform viewer, Tcl scripting | **GPL-2.0** | commit 2026-08-23; no releases | Yes | Only for legacy context |
| cocotb | Python testbenches; `cocotb_tools.runner` | BSD-3-Clause | v2.1.0 2026-08-30 | Yes, very | **Yes** |
| Tencent wave-mcp | 34-tool waveform-debug MCP server | MIT | commit 2026-09-07; v0.2.3 2026-09-05 | Yes, but 6 weeks old | Yes, labelled as new |
| jiegec/waveform-mcp | Waveform-reading MCP server (Rust) | MIT | commit 2026-08-01 | Yes | Yes, as a small worked example |
| surfer-mcp | Drives Surfer over WCP | **None** | commit 2026-05-08 | Quiet | **No** — unlicensed |
| SeanMcLoughlin/mcp-vcd | VCD MCP server | MIT | **commit 2024-12-23** | **Dead** | **No** |
| zesun33 MCP set | Verilog/Yosys/cocotb/OpenROAD/FPGA servers | Apache-2.0 | created 2026-09-05 | Too new to judge | Not as a dependency |
| lowRISC/dvsim | Regression build-and-run system | Apache-2.0 | v1.52.1 2026-09-03 | Yes | **Yes** — and note it moved |
| OpenTitan | Reference DV methodology + 128 sim cfgs | Apache-2.0 | commit 2026-09-07 | Yes, very | **Yes** |
| NVlabs/cvdp_benchmark | Design **and verification** benchmark | Apache-2.0 | commit 2026-06-08 | Yes | **Yes** — the key benchmark |
| hkust-zhiyao/RTLLM | RTL generation benchmark | MIT | commit 2026-08-15 (v2.1) | Yes | Yes |
| NVlabs/verilog-eval | VerilogEval harness | NOASSERTION | **commit 2025-02-07** | **Dormant ~19 months** | Cite the paper, flag the repo |
| NVlabs/FVEval | Formal verification benchmark | NOASSERTION | **commit 2025-04-03** | **Dormant ~17 months** | Cite the paper, flag the repo |

## 7. Suggested BibTeX entries

All accessed 2026-09-07.

| Key | Citation | Supports |
|---|---|---|
| `slang-frontend` | Popoloski, M. *slang: SystemVerilog compiler and language services*, v11.0, 2026. https://github.com/MikePopoloski/slang | Elaboration-grade parsing; that pyslang ships from this repo |
| `verible-syntax-json` | CHIPS Alliance. *verible-verilog-syntax: SystemVerilog Syntax Tool*, 2026. https://github.com/chipsalliance/verible/blob/master/verible/verilog/tools/syntax/README.md | `--export_json` as a documented tool-input interface |
| `surelog-uhdm` | CHIPS Alliance. *Surelog and UHDM*, v1.87, 2026. https://github.com/chipsalliance/Surelog | Open elaboration to a standard object model |
| `treesitter-sv` | Larumbe, G. *tree-sitter-systemverilog*, v0.4.0, 2026. https://github.com/gmlarumbe/tree-sitter-systemverilog | Error-tolerant incremental parsing |
| `verilator-manual` | Snyder, W. and contributors. *Verilator User's Guide: verilator command*, v5.052, 2026. https://github.com/verilator/verilator/blob/master/docs/guide/exe_verilator.rst | `--json-only`, `--diagnostics-sarif`, coverage flags, and the format-instability caveat |
| `yosys-write-json` | YosysHQ. *Yosys `write_json` backend*, v0.68, 2026. https://github.com/YosysHQ/yosys/blob/main/backends/json/json.cc | JSON netlist schema |
| `yosys-mcy` | YosysHQ. *MCY: Mutation Cover with Yosys*, 2026. https://github.com/YosysHQ/mcy | Mutation coverage as a check on coverage metrics |
| `wellen-lib` | Kivelson (ekiwi). *wellen: waveform data structures in Rust*, 0.25.6, 2026. https://crates.io/crates/wellen | Open waveform parsing underneath viewers and servers |
| `surfer-viewer` | Surfer Project. *Surfer waveform viewer*, v0.7.0, 2026. https://gitlab.com/surfer-project/surfer | Scriptable open viewer; WCP source location; EUPL-1.2 |
| `cocotb-runner` | cocotb contributors. *cocotb Python runner*, v2.1.0, 2026. https://github.com/cocotb/cocotb/blob/master/docs/source/runner.rst | Programmatic simulation launch |
| `wave-mcp` | Tencent Penglai Lab. *wave-mcp: MCP server for RTL waveform debug*, v0.2.3, 2026. https://github.com/Tencent/wave-mcp | A real 34-tool hardware MCP server on an open stack |
| `cvdp-benchmark` | Pinckney, N., Deng, C., Ho, C.-T., Tsai, Y.-D., et al. *Comprehensive Verilog Design Problems*, arXiv:2506.14074, 2025. https://arxiv.org/abs/2506.14074 | Benchmarking agents on verification, not only generation |
| `fveval-formal` | Kang, M., Liu, M., Bany Hamad, G., Suhaib, S., et al. *FVEval*, arXiv:2410.23299, 2024. https://arxiv.org/abs/2410.23299 | Formal verification capability evaluation |
| `autobench-tb` | Qiu, R., Zhang, G. L., Drechsler, R., Schlichtmann, U., et al. *AutoBench*, arXiv:2407.03891, 2024. https://arxiv.org/abs/2407.03891 | Automatic testbench generation and its evaluation |
| `correctbench-tb` | Qiu, R., et al. *CorrectBench*, arXiv:2411.08510, 2024. https://arxiv.org/abs/2411.08510 | Self-correcting testbench generation |
| `assertllm` | Fang, W., Li, M., Li, M., Yan, Z., et al. *AssertLLM*, arXiv:2402.00386, 2026. https://arxiv.org/abs/2402.00386 | Assertion generation from specifications |
| `verilogeval-revisited` | Pinckney, N., Batten, C., Liu, M., Ren, H., et al. *Revisiting VerilogEval*, arXiv:2408.11053, 2025. https://arxiv.org/abs/2408.11053 | The standard generation benchmark, second edition |
| `rtllm-bench` | Lu, Y., Liu, S., Zhang, Q., Xie, Z. *RTLLM*, arXiv:2308.05345, 2023. https://arxiv.org/abs/2308.05345 | Open RTL generation benchmark |
| `vericontaminated` | Wang, Z., Shao, M., Bhandari, J., Mankali, L., et al. *VeriContaminated*, arXiv:2503.13572, 2025. https://arxiv.org/abs/2503.13572 | Benchmark scores inflated by data contamination |
| `agentic-coverage-limits` | Patel, Vihaan; Chhabria, Vidya; Arora, Aman. *Understanding Inference-Time Token Allocation and Coverage Limits in Agentic Hardware Verification*, arXiv:2604.15657, 2026. https://arxiv.org/abs/2604.15657 | Measured limits of agentic coverage closure |
| `opentitan-dv` | lowRISC. *Design Verification Methodology within OpenTitan*, 2026. https://github.com/lowRISC/opentitan/blob/master/doc/contributing/dv/methodology/README.md | A public, production-grade DV methodology |
| `dvsim-tool` | lowRISC. *DVSim build and run system*, v1.52.1, 2026. https://github.com/lowRISC/dvsim | Machine-readable regression management |

## 8. Confidence notes and gaps

**High confidence.** Every license, commit date and release date in §§1–3, 5–6
came from the GitHub, GitLab, crates.io, PyPI or Hugging Face APIs, not from
prose. The Verilator flags, Yosys `write_json` options, Verible `--export_json`
flag and OpenTitan methodology quotations are quoted directly from the primary
source files.

**Fetch failures, all recorded rather than guessed.** (1)
`docs.surfer-project.org/book/wcp.html` returns 404 and has **no Wayback
Machine snapshot**; WCP's existence is instead established from the source tree
and `Cargo.toml`. (2) `util/dvsim/dvsim.py` in OpenTitan returns 404 and has
**no Wayback snapshot**; the move to `lowRISC/dvsim` is inferred from that 404
plus the live repository, and is stated as such. (3) GitLab's blob search API
returned `401 Unauthorized`, so Surfer's source was surveyed by directory
listing instead of full-text search — a WCP mention elsewhere in that repo could
have been missed. (4) `pylibfst`'s `LICENSE` path 404s; the licensing statement
above comes from its `COPYING` file, which points at two further files this note
did not open, so **the exact SPDX identifiers for pylibfst remain unverified**.

**Gaps a follow-up should close.** No EDA-vendor MCP announcement was located;
that search needs vendor press pages rather than repositories, so the appendix
should not assert that none exist. Verible's Apache-2.0 and Verilator's dual
license were read from their license and README files, neither checked for
per-file exceptions. The wave-mcp validation figures are self-reported. The two
2026 agentic-coverage preprints are not confirmed peer-reviewed. And `zesun33`'s
five servers appeared two days before this note; anything said about them will
date fast, so describe the *pattern* rather than the repositories.

**Dead or dormant — do not send readers to these as live projects:**
`MikePopoloski/pyslang` (archived 2025-01-18), `SeanMcLoughlin/mcp-vcd` (dead
since 2024-12-23), `NVlabs/verilog-eval` (dormant since 2025-02-07),
`NVlabs/FVEval` (dormant since 2025-04-03), `mschlaegl/pylibfst` (dormant since
2025-06-11), and `PaoloRondot/surfer-mcp` (quiet since 2026-05-08 and, more
seriously, carrying no license at all).
