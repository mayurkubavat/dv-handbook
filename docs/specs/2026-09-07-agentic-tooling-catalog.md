# Agentic tooling catalogue for RTL, verification and debug

**Status:** discussion draft, 2026-09-07. Companion to Chapter 34.
**Sources:** `research/tooling-landscape-hardware.md` (about 120 tools, URLs checked 2026-09-07), `research/tooling-landscape-software.md` (244 URLs checked), `research/dv-adaptation-synthesis.md`, `research/ai-in-dv-state-of-the-art.md`.
**Purpose:** an exhaustive map of what an AI agent could call across RTL design, DV, debug and automation, organised so that every hardware capability sits next to its software-engineering analogue, what exists today, what an agent would do with it, and what is missing. It is written to be argued with.

## 1. How to read this

### 1.1 Three doors into a tool

Software agents reach tools through three doors, and the door decides how much glue is needed.

| Door | Software examples | Hardware examples today | Cost to add |
|---|---|---|---|
| **Shell**: a CLI with parseable stdout | `pytest`, `ruff`, `git bisect run` | `verilator`, `sby`, `make run`, `dvsim.py` | none; the agent runs it and reads text |
| **File format**: a machine-readable artifact | SARIF, JUnit XML, LCOV, OpenAPI, ReqIF | JUnit from cocotb, SARIF from Verilator, FST/VCD, UCIS XML, Hjson testplans | lowest for an EDA flow: emit a file, no server needed |
| **Protocol**: a live session | LSP, DAP, MCP, REST | verible-verilog-ls, wave-mcp, pyslang-mcp, OpenROAD-MCP | highest, and the only door that supports interactive queries (a waveform cursor, a formal counterexample walk) |

The file-format door is the cheapest way to make an existing EDA flow agent-usable, and most of the gaps below close with a file format before they close with a server.

### 1.2 The rule every tool must respect

From Chapter 34: whatever generates must not own what judges. Every tool in this catalogue is therefore tagged with which **roles** may call it and whether the call is **read** or **write**. The stimulus role never gets write access to the oracle (checker, reference model, assertions, coverage model); the debug and review roles need read access to everything. A tool server enforces this by construction: the stimulus agent's server simply does not have an `edit_checker` tool.

| Role | May write | May read | Judge |
|---|---|---|---|
| Planner | plan items (draft) | spec, plan, RTL, history | human gate 1 |
| Stimulus | tests, sequences, constraints | spec, plan, RTL, coverage report, failures | simulator, coverage DB |
| Checker author (human or isolated agent) | checker, reference model, assertions, coverage model | spec, plan, RTL | formal engine, human gate 2 |
| Coverage analyst | gap reports | coverage DB, plan | coverage DB |
| Debug / triage | hypotheses, clusters | everything, including the oracle | human reading the hypothesis |
| Formal | property proposals (to gate 2) | spec, plan, RTL | formal engine |
| Reviewer | findings, mutation reports | everything | mutation kill rate, held-out tests |

### 1.3 Maturity vocabulary

**Exists** (open, usable today), **partial** (exists with a stated limitation), **vendor** (commercial only), **research** (paper or prototype), **gap** (nothing found). The two research notes carry the URLs, licences and dates for every tool named here; this document does not repeat them.

## 2. The catalogue by domain

Each entry: the capability, its software analogue, what exists on the hardware side, what an agent does with it, and the gap. Twelve domains, A to L.

### A. Specification and requirements

| Capability | Software analogue | Hardware today | Agent use | Gap |
|---|---|---|---|---|
| Spec as code, built and linted in CI | Sphinx/MkDocs with warnings-as-errors; Vale prose lint | Markdown/mdBook (OpenTitan), AsciiDoc (RISC-V), Quarto (this book); no common convention | Read the spec by section; fail a build on a broken cross-reference | **gap**: no agreed Markdown spec convention for silicon blocks |
| Register description as the single source | OpenAPI as the API contract | SystemRDL + systemrdl-compiler + PeakRDL (RTL, UVM RAL, headers, docs from one file); IP-XACT + ipyxact; OpenTitan reggen (Hjson) | Query fields, resets, access types; regenerate every view; check that RTL, RAL and doc agree | **partial**: no lint or breaking-change diff for SystemRDL/IP-XACT (software has Spectral and oasdiff) |
| Requirements with IDs and trace links | StrictDoc, Doorstop, sphinx-needs, OpenFastTrace, ReqIF | Same tools apply unchanged; OpenTitan Hjson testplans are the nearest DV-native form | Extract "shall" statements into items; trace requirement to plan item to test to coverage; report untraced requirements | **partial**: no routine requirement-to-coverpoint trace checker in CI |
| Timing diagrams as data | Mermaid sequence diagrams | WaveDrom JSON | Draw a protocol from a spec paragraph; compare a spec waveform to a simulated one | exists |
| Interface contracts | OpenAPI, Protobuf/buf, AsyncAPI | IP-XACT bus definitions; PSS for test intent | Generate BFMs and monitors from a contract; detect a port change that breaks integrators | **gap**: contract diff |
| Decision records | ADR / MADR | none in common use | Record why a verification choice was made, in a fixed template an agent can fill | exists (adopt as is) |

### B. RTL understanding (read-only)

| Capability | Software analogue | Hardware today | Agent use | Gap |
|---|---|---|---|---|
| Parse and elaborate; "what the compiler sees" | compiler front end; pyright/rust-analyzer | slang / pyslang (IEEE 1800-2023), Surelog + UHDM, Verilator `--xml-only`, GHDL for VHDL, CIRCT `circt-verilog` | Compile-check an edit, list ports and parameters, walk the elaborated hierarchy | exists |
| Syntax tree, error-tolerant, incremental | tree-sitter | tree-sitter-systemverilog, Verible CST as JSON, sv-parser | Chunk a file by module or always block; validate an LLM edit by re-parsing and rejecting `ERROR` nodes | exists |
| Language server: definition, references, hover, rename | LSP 3.17 servers; LSP-to-MCP bridges (Serena, multilspy) | verible-verilog-ls (definition, references, no rename), svls, veridian, vhdl_ls; AMIQ DVT MCP (vendor) | Navigate a UVM environment without loading it into context; jump from a failing assertion to its driver | **gap G1**: no full-surface SV/UVM server; no open rename; no macro- and class-hierarchy awareness |
| Structural search and rewrite | ast-grep, Semgrep, Comby, CodeQL | none over SV beyond tree-sitter queries; Verible lint rules | "Every `always @*` without a default", "every FIFO instance with DEPTH not a power of two"; house-style rules as data | **gap**: no ast-grep-style tool with SV patterns; no CodeQL-style semantic queries |
| Netlist and dataflow queries | call graphs, dataflow analysis | Yosys RTLIL and `write_json`; naja-scope MCP (cones, drivers, loads, register frontier); Pyverilog dataflow (Verilog-2005 only); wave-mcp driver tracing | Fan-in cone of a signal; which registers feed a flag; where a value could have come from | exists (partial for SV) |
| Symbol index across a repository | ctags, SCIP | universal-ctags has SV support; Verible Kythe indexer | Cheap cross-repo definition lookup | exists |
| Repository map for context | Aider repo-map | none | Feed an agent a ranked outline of modules, ports and classes instead of files | **gap**: trivial to build on Verible JSON or pyslang |
| Lint with machine-readable findings | SARIF from Ruff, ESLint, CodeQL; baseline diffing | Verilator `--diagnostics-sarif` (the only HDL SARIF); Verible lint and svlint as text | Lint a generated edit, fix only new findings against a baseline, auto-apply fixes where the tool offers them | **gap G2**: SARIF from Verible, svlint, CDC/RDC and commercial lint; a converter is small, adoption is the work |
| Formatting | Black, clang-format, gofmt | Verible formatter | Remove style from review; run pre-commit | exists (no UVM-aware formatter) |
| Structural checks | type checkers | Yosys `check` (undriven, multi-driven, loops); Verilator lint (width, latch, case) | First gate on any generated RTL | exists |
| Clock and reset domain crossing | no direct analogue (data races: TSan) | none open; Questa CDC, SpyGlass, Jasper CDC (vendor) | Flag a crossing an agent introduced | **gap**: no open CDC/RDC checker at all |

### C. RTL design automation (write)

| Capability | Software analogue | Hardware today | Agent use | Gap |
|---|---|---|---|---|
| Generate from templates rather than raw text | code generators, Jinja; template-first agent generation | PeakRDL for registers; HAVEN-style UVM from protocol templates (research); Chisel/FIRRTL via CIRCT | Emit register blocks, bus wrappers, glue from a contract; keep the LLM to parameters, not syntax | partial |
| Refactor with an equivalence guarantee | refactoring tools + tests | Yosys eqy (gold vs gate, partitioned) | Let an agent restructure RTL and prove it unchanged | exists |
| Does it synthesise, what did it cost | compile + size report | Yosys `synth` + `stat`; OpenROAD / OpenLane for timing and area; OpenROAD-MCP (official) | Reject an edit that infers a latch or triples area; STA sanity | exists |
| Language conversion | transpilers | sv2v, Veryl to SV | Feed SV into Verilog-only tools | exists |
| Automatic repair from a testbench | program repair (SMT-based, LLM-based) | RTL-Repair (research, UC Berkeley) | Baseline for "propose a fix", always behind gate 2 | research |

### D. Testbench and DV construction

| Capability | Software analogue | Hardware today | Agent use | Gap |
|---|---|---|---|---|
| Plan as code, reported against by the regression | requirements tools; test plans in code | OpenTitan Hjson testplans + testplanner; this book's `fifo_plan.yaml` + `plan_report.py`; vendor planners (Verisium Manager, Verdi VMS, Questa VM) | Read the plan to pick a target; map a new test to its item by name; report evidence per item | exists (open); no shared schema |
| Testbench scaffolding | project generators, cookiecutter | cocotb 2.x runner; pyuvm; UVM from templates (research); core-v-verif as a reference environment | Scaffold an environment for a new block from interface definitions | partial |
| Stimulus generation aimed at holes | property-based testing, fuzz harness generation (OSS-Fuzz-Gen) | constrained-random in SV; cocotb-coverage randomisation; coverage-directed agent loops (research) | Propose a sequence for a named coverage hole; keep it only on positive delta | exists / research |
| Constraint solving as a tool | Z3, cvc5 | SV constraint solvers (simulator-bound); Z3 directly for stimulus problems | Solve for a legal transaction meeting a target; prove a constraint set unsatisfiable | exists |
| Checker and reference model | tests written first; contracts | scoreboards, reference models, SVA; written by the oracle role only | Not delegable today (Ch. 34); the tool question is how to keep the stimulus role away from them | policy, not a tool |
| Assertion proposal with a formal judge | invariant generation checked by Z3/Dafny | SVA proposals checked by SymbiYosys or EBMC, vacuity check, mutants (research: ProofLoop and similar) | Propose, prove or refute, reject vacuous, score against mutants | exists (open stack); SVA subset limits in open engines |
| Functional coverage model from the plan | none exact; mutation score as the test-quality metric | covergroups (SV), cocotb-coverage (Python); UCIS for interchange | Derive bins and crosses from plan items; the coverage model stays in the oracle role | exists; **partial** interchange |
| Unit tests for testbench code | pytest, Google Test | SVUnit, VUnit (VHDL), pytest for Python testbenches | Test the checker itself | exists |
| Shrink a failing random run | Hypothesis shrinking; creduce/cvise; delta debugging | none | Reduce a 400-cycle failing sequence to the minimal transactions that still fail before asking anyone to explain it | **gap G4**: a delta-debugging wrapper around a sequence replayer |

### E. Simulation and regression

| Capability | Software analogue | Hardware today | Agent use | Gap |
|---|---|---|---|---|
| Run one test, get a structured verdict | pytest + JUnit XML; pytest-json-report | cocotb `results.xml` (JUnit, with attachments); VUnit JUnit; this book's `status.json`; Verilator exit codes | The primitive tool call: `run(test, seed)` returning pass/fail, sim time, log path | exists |
| Run across simulators through one API | test runner abstraction | Edalize (about 30 tools), FuseSoC targets, cocotb runner, dvsim | One tool interface over Verilator, Icarus, GHDL and the commercial three | exists |
| Regression orchestration and results | CI systems with APIs; Bazel test caching | dvsim (OpenTitan; CLI-only, not packaged), vendor regression managers | Launch a named regression, poll, read the table | partial; **gap**: no open, reusable regression database or schema |
| Regression selection from a change | predictive test selection (Meta), pytest-testmon, Bazel dependency-based selection | none open; regression tiers by hand | Select the tests affected by an RTL diff; rank by failure likelihood | **gap G11** |
| Flaky and seed-dependent test handling | rerun plugins, quarantine lists with owners and expiry, pass^k | manual seed hunting; OpenTitan's 100-seed convention | Quarantine a seed-flaky test with an owner and expiry; require pass^k | **gap G11** |
| Hermetic, cached build of RTL plus testbench | Bazel, Nix, Remote Execution API | rules_hdl (Bazel), nixpkgs EDA, OSS CAD Suite, hdl/containers | Deterministic environments per agent; cached compiles | partial; **gap G5** for commercial simulators (licences, non-deterministic compiles) |
| Simulator farm as a service | Remote Execution API, CI runners | LSF, Slurm, Grid Engine | Front a farm with one API an agent can call | partial (schedulers exist, no agent-facing API) |
| Full UVM on an open simulator | n/a | Verilator runs UVM 2020-3.2 with tracked limitations; pyuvm sidesteps it | Run UVM examples without a licence | partial |

### F. Coverage

| Capability | Software analogue | Hardware today | Agent use | Gap |
|---|---|---|---|---|
| Code coverage with an interchange format | coverage.py JSON, LCOV, Cobertura, LLVM JSON | Verilator `--coverage` with `verilator_coverage --write-info` (lcov); vendor databases | Read hit counts per line; feed lcov tooling and CI dashboards | exists (open) |
| Functional coverage and its interchange | none exact | covergroups; cocotb-coverage XML/YAML; UCIS XML via pyucis; pyEDAA.UCIS to Cobertura | Diff coverage between runs; list holes by plan item | **partial G12**: no open reader for vendor UCIS binaries |
| Coverage on the diff | diff-cover | none | "Did the agent's new test reach what it changed?" | **gap** (small) |
| Merge and rank | coverage merge tools | verilator_coverage merge; dvsim coverage merge; vendor | Merge seeds; rank tests by unique contribution | exists (open, basic) |
| Coverage-to-plan mapping | none | OpenTitan testplanner join by name; `plan_report.py` (test evidence only) | Report closure per plan item, not per bin | partial; the coverage half of the plan report is unbuilt |
| Mutation and fault injection | mutmut, PIT, Stryker; Google's changed-lines mutants | Yosys mcy (open, low activity); Certitude (vendor) | Score a testbench by mutants killed; surface a few relevant mutants per change | **gap G3**: no drop-in open RTL mutation tool of mutmut's maturity |

### G. Formal

| Capability | Software analogue | Hardware today | Agent use | Gap |
|---|---|---|---|---|
| Bounded model checking and induction | CBMC, Kani, ESBMC | SymbiYosys (smtbmc, abc pdr) with Yices/Bitwuzla/Z3; EBMC/hw-cbmc (SVA subset, k-induction, IC3); CIRCT `circt-bmc` (early) | Prove or refute a property; get a counterexample | exists (open) |
| Counterexample as structured data | CBMC JSON/XML traces | VCD/FST from sby; log text | Hand a counterexample to the debug tools without a viewer | **gap G7**: no machine-readable trace beyond a waveform; small to add |
| Vacuity and cover checks | assertion sanity | sby `cover` mode; vacuity by construction (assert with the premise negated) | Reject a property whose premise never occurs | exists (manual pattern) |
| Equivalence checking | differential testing | Yosys eqy | Prove an agent's refactor unchanged | exists |
| SVA subset support in open engines | full language support in CBMC | Yosys `read_verilog -formal` (immediate assertions, limited concurrent SVA); slang front end and EBMC widen it | Know which properties the open engine can take | partial |
| Solver access as a tool | Z3 API | Z3, cvc5, Bitwuzla | Direct constraint queries for stimulus and property debugging | exists |
| Open SVA benchmarks | SV-COMP scale suites | FVEval, AssertLLM datasets (small) | Measure a property-generating agent honestly | **gap G7** |

### H. Debug and triage

| Capability | Software analogue | Hardware today | Agent use | Gap |
|---|---|---|---|---|
| Structured logs | JSON logs, OpenTelemetry | UVM report lines (regular but unschema'd); cocotb structured log; Verilator `%Warning`/`%Error`; pyEDAA.OutputFilter for vendor logs | Parse to records; first `UVM_ERROR` and its time is the triage key | exists (regex-level) |
| Waveform access from a program | rr traces, OTLP spans as artifacts | pylibfst, wellen (FST); pyvcd, vcdvcd (VCD); WAL query language; FST as the pragmatic open format; FSDB only via vendor libraries | Value at time, transitions, first divergence, driver and X tracing | exists |
| Waveform debug as tools | DAP for debuggers | wave-mcp (34 tools: hierarchy, values, `trace_value`, `trace_x`, `diff_waveforms`, viewer); TraceWeave (logs plus waves plus source, commercial-sim aware); Surfer WCP for driving a viewer | The first serious open debug servers; converge on the same vocabulary | exists (2026) |
| Debug adapter over a simulator | DAP | simulator Tcl/UCLI shells; checkpoints; no protocol | Set a breakpoint on a signal condition, step cycles, evaluate expressions, from one client across simulators | **gap G6** |
| Pass-versus-fail first divergence | differential debugging | wave-mcp `diff_waveforms`, TraceWeave divergence queries | The most reusable triage primitive: where did the failing seed leave the passing one | exists |
| Record and replay | rr, Pernosco | save/restore checkpoints; deterministic reseed | Reproduce and rewind; nearly exact analogue already exists in simulators | partial (no common interface) |
| Failure clustering and dedup | ClusterFuzz stack signatures, Sentry fingerprints | none open; vendor AutoTriage (research/vendor) | Cluster a regression's failures by first-error signature; one hypothesis per cluster | **gap G6** |
| Bisection | `git bisect run`; ClusterFuzz culprit bisection | `git bisect run` with a cocotb/Verilator oracle; PinDown (vendor) | Agent writes the predicate; git finds the commit | exists (generic) |
| Test-case reduction | creduce/cvise, Hypothesis shrinking | none | Minimal failing sequence and seed | **gap G4** |
| Log search | ripgrep `--json`, lnav, Loki | ripgrep works unchanged; no regression-log store | Grep at scale; SQL over logs | partial |
| Showing a person the evidence | screenshots, flame graphs | Surfer/GTKWave scripted screenshots; WaveDrom; sootty (dormant) | Put a cursor at the failing time for the human at gate 3 | exists |

### I. Physical and structural checks (as sanity gates)

| Capability | Software analogue | Hardware today | Agent use | Gap |
|---|---|---|---|---|
| Synthesis and timing sanity | compile time and binary size gates | Yosys + OpenROAD/OpenLane + OpenSTA; nextpnr for FPGA; OpenROAD-MCP | "Does it still meet timing" after an RTL edit | exists |
| Lint beyond function | security scanners | Verilator, Verible, svlint | Style and structure gates | exists |
| CDC/RDC | none | vendor only | see B | **gap** |
| Power intent (UPF) checks | none | vendor only | Verify an agent did not break an isolation cell | **gap** (open) |

### J. Documentation and knowledge

| Capability | Software analogue | Hardware today | Agent use | Gap |
|---|---|---|---|---|
| Instruction file for the repository | AGENTS.md (now under the Linux Foundation's agent foundation), Agent Skills format | this book's `AGENTS.md`; none in common DV use | Tell an agent how to compile, run one test, find the plan, what never to edit | **gap G8**: no DV convention; low effort |
| Docs as code with CI gates | Sphinx `-W`, markdownlint, lychee, Vale | Quarto (this book), mdBook (OpenTitan) | Broken cross-reference fails the build; prose lint | exists |
| API and class documentation | Doxygen, rustdoc | Doxygen works on SV with filters; UVM class docs | Keep testbench docs next to code | partial |
| Knowledge base for retrieval | docs-as-code feeding search or retrieval | regression history and bug databases, rarely as text | Ground a debug agent in past failures of this block | **gap**: regression history as a queryable artifact |
| Decision records | ADR | none | Why this coverage waiver, why this sign-off exception | adopt as is |

### K. Agent infrastructure

| Capability | Software analogue | Hardware today | Agent use | Gap |
|---|---|---|---|---|
| Tool protocol and discovery | MCP spec, MCP registry, SDKs, Inspector | wave-mcp, TraceWeave, pyslang-mcp, naja-scope, OpenROAD-MCP, fpgaZeroMCP, MCP4EDA; AMIQ DVT MCP (vendor); a dozen single-tool servers | Wrap a CLI in tens of lines; the registry lists three EDA servers | exists; **gap G8**: no agreed schemas for `run_test`, `get_coverage`, `read_waveform` |
| Agent-to-agent delegation | A2A protocol | none DV-specific | Orchestrator hands a triage task to a debug agent | exists (generic) |
| Isolation per agent | git worktree + container/microVM (gVisor, Firecracker, nsjail); network deny | worktree works; EDA installs on NFS and licence servers conflict with network-deny sandboxes | One worktree and one container per agent task | **gap G14**: sandboxing that coexists with licence servers; policy and EULA questions |
| Pinned tool environments | Nix, devcontainers, per-task Docker images | OSS CAD Suite, hdl/containers, nixpkgs EDA, rules_hdl | The same environment on a laptop, in CI and in an agent sandbox | exists (open tools) |
| Tool-description security | MCP security guidance; tool-poisoning disclosures; OWASP agentic top 10 | none DV-specific; a log an agent reads is untrusted input | Review tool descriptions; treat simulation logs as untrusted text | policy |
| Observability of agent actions | OpenTelemetry GenAI semantic conventions | none | Trace every tool call an agent made in a regression, for the sign-off evidence bundle | **gap G13** |
| Cost model for expensive tools | build caching, test sharding | none | Budget simulation seconds per loop iteration; cache compiles | **gap** (design, not tool) |

### L. Evaluation and governance

| Capability | Software analogue | Hardware today | Agent use | Gap |
|---|---|---|---|---|
| Task benchmark with held-out oracle | SWE-bench (hidden tests, per-task containers), SWE-smith (synthetic tasks by bug injection), Terminal-Bench | VerilogEval, RTLLM, CVDP, ChipBench, FVEval (see AI-in-DV note); contamination shown for the older ones | Measure an agent on bug-finding, not coverage | **gap G10**: no SWE-bench-scale DV benchmark with held-out checkers and containerised open simulators |
| Gate stack in repository policy | formatter, lint on diff, types, unit tests, coverage on diff, mutation score, security scan, review bot, CODEOWNERS, branch protection, merge queue | regression status rarely a required check; coverage closure rarely a branch rule | Encode sign-off criteria as policy no agent can bypass | **gap** (adoption; the mechanisms exist) |
| Human gates and ownership | CODEOWNERS | none conventional | Route oracle changes to a named checker owner | adopt as is |
| Provenance and attribution | signed commits (Sigstore), SLSA | none | Distinguish agent-written from human-written artifacts in a tapeout package | adopt as is |
| Outcome metrics | DORA metrics; METR-style trials | none standard | bugs found per engineer-week, escape rate, time to closure, mutation kill rate, review load (Ch. 34) | **gap** (measurement practice) |

### M. Testbench understanding and logs as context (added 2026-09-07)

Domains B and H cover the RTL and the waveform. This domain covers what an agent needs to understand the *testbench*, which is class-based, dynamically constructed and observable mostly through its log. Nothing open does this today; the two surveys found no server with UVM class-hierarchy awareness, and the software analogues are the strongest guide.

#### M.1 Structural understanding from the AST and the elaborated design

| Capability | Software analogue | Hardware today | Agent use | Gap |
|---|---|---|---|---|
| Clock tree: every clock source through buffers, gates, muxes and dividers to every sequential element it drives | none exact (build dependency graph) | none open; vendor CDC tools infer it | Name the clock domain of any register; list crossings an edit introduced; the first half of CDC | **gap**: derivable from Yosys RTLIL or pyslang by walking `always_ff` sensitivity through the driver cone of the clock net |
| Reset tree: sources, polarity, sync or async per register, reset domains | none exact | none open | Same for resets; find a register with no reset; find an async reset crossing | **gap**: same derivation, from `always_ff` reset branches |
| Instance connection graph: which port of which instance connects to which, including implicit `.*` and interface modports | module dependency graph, import graph | Verilator `--xml-only`, Yosys `write_json`, pyslang connections; naja-scope | Answer "what is connected to this FIFO's full flag" without reading RTL; render a block diagram | partial (data exists, no tool exposes it as a graph query) |
| UVM component hierarchy, static: what `build_phase` constructs, from `type_id::create` and `new` calls, with factory overrides and `uvm_config_db` set/get sites | dependency-injection graph analysis (Spring, Guice bean graphs) | none; slang parses the classes but no tool walks the construction | Know the testbench topology before running it; find a config_db key set but never got, or got with the wrong type | **gap**: an AST walk over slang's class model plus a small interpreter for the UVM idioms |
| UVM component hierarchy, dynamic: the real tree at run time | runtime object graph dumps | `uvm_top.print_topology()`, `uvm_config_db::dump()`, `+UVM_PHASE_TRACE`, `+UVM_OBJECTION_TRACE`, `+UVM_CONFIG_DB_TRACE` all exist in the reference implementation | Parse the printed topology into a tree; diff static versus dynamic to find factory surprises | exists (text only; parsers to write) |
| TLM connection graph: analysis ports to exports and FIFOs, from `connect_phase` | message-flow graphs | none | Trace where a monitor's transactions go; find a scoreboard export nothing feeds | **gap**: same AST walk over `connect()` calls |
| Dry sequence trace: statically walk a sequence `body()` through `` `uvm_do ``, `start()`, nested sequences, `p_sequencer` and `grab`/`lock`, without simulating | static call-graph and control-flow analysis; symbolic execution of the "happy path" | none | Produce the expected transaction order and the sequencer arbitration a test will exercise; compare with the plan item's stimulus intent before running | **gap**: bounded control-flow walk of sequence bodies; loops summarised, randomised fields left symbolic |
| Phase and objection map | lifecycle analysis | `+UVM_PHASE_TRACE`, `+UVM_OBJECTION_TRACE` | Explain a test that ended at time zero (no objection) or never ended (objection leak) | exists (text) |
| Transaction recording | tracing databases | `uvm_tr_database` / `uvm_text_tr_database` in the reference implementation record begin and end of transactions with attributes; vendor transaction viewers (Verdi, DVT) | Transaction-level view without a vendor viewer; the recorded stream is the join key for M.2 | partial (text database; no open parser) |

#### M.2 Logs as context: a message-signature methodology

The problem: a UVM log of a large environment is millions of lines, mostly `UVM_INFO`, and the lines that explain a failure are scattered across components and times. An agent cannot read it, and a person reads it by grep and intuition. The software world solved the same problem for distributed systems with **structured logging** and **distributed tracing**: every log record is a structured event, every request carries a trace identifier that all its spans share, and a query engine reconstructs the request's path after the fact. The mapping onto UVM is direct, and most of the machinery already exists in the reference implementation.

**The convention.** Every transaction gets a unique identifier at the point it is created (in the sequence), and every component that touches it logs with that identifier. The UVM message ID field, which today holds an arbitrary string, becomes a **signature**: a small grammar rather than free text.

| Field | Content | UVM carrier |
|---|---|---|
| component role | `SEQ`, `DRV`, `MON`, `SB`, `RM` (reference model), `COV`, `ENV`, `TEST` | first token of the message ID |
| component instance | the UVM hierarchical name | already printed by the report server as the scope |
| transaction id | unique per transaction, created in the sequence, copied by the driver into the pin activity's metadata, recovered by the monitor (from a sideband, a tag field, or ordering), carried into the scoreboard | second token of the ID, `TXN=<n>` |
| stage | `CREATE`, `SEND`, `DRIVE_BEGIN`, `DRIVE_END`, `OBSERVE`, `EXPECT`, `COMPARE_OK`, `COMPARE_FAIL`, `DROP` | third token |
| payload | key-value pairs, machine-parseable (`addr=0x40 data=0xA7 len=4`) | message text, in a fixed `key=value` form |
| time and scope | simulation time and hierarchical scope | already in every report line |

A line then reads, for example, `UVM_INFO @ 1230ns: uvm_test_top.env.agt.drv [DRV TXN=17 DRIVE_END] addr=0x40 data=0xA7`. The reference model logs `[RM TXN=17 EXPECT] data=0xA7`, the monitor logs `[MON TXN=17 OBSERVE] data=0xB3`, and the scoreboard logs `[SB TXN=17 COMPARE_FAIL] expected=0xA7 actual=0xB3`.

**What the convention buys.** A transaction's whole lifecycle is one grep: `TXN=17`. The first `COMPARE_FAIL` names the transaction; joining on its identifier gives, in order, what the sequence intended, what the driver drove, what the model expected and what the monitor saw. That join is the evidence an agent needs to make the single most valuable distinction in triage:

- **Sequence intended X, driver drove X, monitor observed Y, model expected X**: the RTL did something the model did not expect. Suspect the RTL (or the model's understanding of the spec); hand the debug role the monitor's time and the signal names.
- **Sequence intended X, driver drove Y**: the driver or the sequence item is wrong. Suspect the testbench.
- **Monitor observed X, model expected Y, and X matches the spec on inspection**: the reference model is wrong. Suspect the oracle, and route to the oracle owner, not the stimulus role.
- **No `OBSERVE` for a transaction that was driven**: the monitor missed it, or the DUT dropped it; the waveform at `DRIVE_END` time decides which.

**Structured at the source, not regex after the fact.** UVM's `uvm_report_catcher` and a custom `uvm_report_server` can emit each message as one JSON object (time, severity, scope, role, transaction id, stage, payload) alongside the text log, so no parser is needed; the software analogue is JSON-lines logging feeding a query engine. Where the convention cannot be retrofitted, a parser over the text ID grammar is enough.

**Context injection for an agent.** The log is never given to a model whole. A tool assembles, for one failure, a bounded context in a fixed order: the plan item under test, the first error line, the lifecycle of its transaction, the lifecycles of the two transactions before it, the phase and objection events around that time, and a pointer to the waveform window. That is a few hundred lines, chosen by the join rather than by proximity, and it is the same shape as the software practice of attaching a trace to an error report.

| Tool | Arguments | Returns | Built on |
|---|---|---|---|
| `log.uvm_parse` | log path | JSON records (time, severity, scope, role, txn, stage, payload) | ID grammar above; or the JSON emitter |
| `log.txn_lifecycle` | log, txn id | the ordered events for one transaction across components | join on `TXN` |
| `log.first_failure_context` | log, window | plan item, first error, lifecycle of the failing and preceding transactions, phase and objection events, wave window | composition of the above and `plan.items` |
| `log.classify_failure` | lifecycle | one of the four verdicts above, with the evidence lines | rule table over stages present and payload equality |
| `log.compress` | log | INFO lines deduplicated by signature with counts; transitions kept; errors kept verbatim | signature grouping (the software analogue is error fingerprinting) |
| `log.summarize_by_role` | log | counts and first/last time per role and stage | grouping |
| `tb.topology` | log or design | the component tree (dynamic from `print_topology`, static from the AST walk), with a diff | M.1 tools |
| `tb.sequence_dry_run` | sequence class, config | expected transaction order and sequencer arbitration, randomised fields symbolic | M.1 dry trace |
| `tb.tlm_graph` | environment | analysis-port connection graph | M.1 |
| `rtl.clock_tree`, `rtl.reset_tree`, `rtl.connections` | top | trees and connection graph as JSON | M.1 |

**Software parallels, stated once.** Structured logging (JSON lines) and log levels map to severity and verbosity. Distributed tracing with a trace identifier maps to the transaction identifier carried from sequence to scoreboard. Error fingerprinting for deduplication maps to `log.compress` and to failure clustering in domain H. OpenTelemetry's semantic conventions are the model for the signature grammar: a fixed vocabulary of attribute names, so tools compose.

## 3. A proposed tool set for the book's flow

The book's build system already has three uniform targets and a status file. The proposal below grows that into a tool set an agent could call, using only open tools from the two surveys. Names are suggestions for discussion. Every tool is tagged **R** (read) or **W** (write) and with the roles allowed to call it; the permission column is the invariant of Chapter 34 made concrete.

### 3.1 Read-only understanding (all roles)

| Tool | Arguments | Returns | Built on |
|---|---|---|---|
| `rtl.compile_check` | files, top, defines | diagnostics (SARIF) | slang / pyslang; Verilator `--lint-only --diagnostics-sarif` |
| `rtl.hierarchy` | top | instances, modules, ports, params (JSON) | pyslang |
| `rtl.symbol` | name, scope | declaration site, type, width, drivers, loads | pyslang, naja-scope |
| `rtl.search` | pattern (tree-sitter query or ast-grep style) | matches with file:line | tree-sitter-systemverilog, Verible CST JSON |
| `rtl.cone` | signal, direction, depth | fan-in or fan-out cone to the register frontier | Yosys RTLIL `write_json`, naja-scope |
| `rtl.lint` | files, ruleset, baseline | SARIF, filtered to new findings | Verilator SARIF; Verible and svlint through a small SARIF wrapper (gap G2) |
| `rtl.synth_stat` | top | cells, latches, comb loops, area estimate | Yosys `synth; stat; check` |
| `spec.section` | id or query | spec text for one section, with source location | the spec repository; Markdown headings as the unit |
| `regs.query` | block, register or field | fields, reset values, access, address | systemrdl-compiler / PeakRDL |
| `plan.items` | block, filter (state, priority) | plan items with intents and closure | `fifo_plan.yaml` schema; OpenTitan Hjson |
| `plan.report` | block | per-item evidence state (tests pass / fail / none), coverage state once built | `plan_report.py` |

### 3.2 Stimulus role (W on tests only)

| Tool | Arguments | Returns | Built on |
|---|---|---|---|
| `sim.run` | test dir, seed, plusargs | pass/fail, sim time, log path, wave path, JUnit | `make run`; cocotb runner; Verilator `--binary` |
| `sim.run_seeds` | test dir, seeds[] | per-seed verdicts, pass^k | same, in a loop |
| `cov.report` | block, runs[] | code and functional coverage summary; holes by bin | `verilator_coverage --write-info`, cocotb-coverage XML, pyucis |
| `cov.holes_by_item` | block | plan items whose coverage intent has unhit bins | join of `cov.report` and `plan.items` (unbuilt) |
| `test.write` | test dir, files | applies the edit; re-parses; rejects on syntax error | filesystem under `examples/<chapter>/`; guard hook denies oracle paths |
| `test.shrink` | test dir, seed | minimal transaction sequence that still fails | delta-debugging wrapper around a sequence replayer (gap G4) |

### 3.3 Oracle role (W on checker, model, assertions, coverage model; human-gated)

| Tool | Arguments | Returns | Built on |
|---|---|---|---|
| `oracle.write` | path, files | edit under `checker/`, `model/`, `assertions/`, `coverage/` only | filesystem; the stimulus role's server has no such tool |
| `formal.prove` | properties, depth, engine | proven / refuted / unknown, counterexample wave, structured trace (gap G7) | SymbiYosys, EBMC |
| `formal.vacuity` | property | vacuous or not | sby `cover` on the premise |
| `formal.equiv` | gold, gate | equivalent or counterexample | Yosys eqy |
| `mutants.generate` | rtl, operators, count | mutant set | Yosys mcy; small SV mutation operators (gap G3) |
| `mutants.score` | testbench, mutant set | kill rate, surviving mutants | mcy plus `sim.run` |

### 3.4 Debug and review roles (R on everything)

| Tool | Arguments | Returns | Built on |
|---|---|---|---|
| `log.parse` | log path | structured records; first error, time, scope, id | UVM report regex; cocotb log; Verilator diagnostics |
| `wave.value` | wave, signal, time | value | pylibfst, wellen |
| `wave.transitions` | wave, signal, window | edges with times | same |
| `wave.trace_driver` | wave, signal, time | driver chain back to a source | wave-mcp `trace_value` |
| `wave.trace_x` | wave, signal, time | origin of an X | wave-mcp `trace_x` |
| `wave.first_divergence` | pass wave, fail wave, signals | first differing signal and time | wave-mcp `diff_waveforms` |
| `wave.snapshot` | wave, signals, window | image for a person | Surfer WCP or GTKWave Tcl |
| `triage.cluster` | run logs[] | clusters by first-error signature, one representative each | to build (gap G6); ClusterFuzz as the model |
| `triage.bisect` | good rev, bad rev, predicate | culprit commit | `git bisect run` |
| `review.mutation_report` | block | kill rate over time, surviving mutants by plan item | `mutants.score` history |
| `review.held_out` | block | results on tests the stimulus role never saw | a held-out test directory outside the stimulus role's write set |
| `log.first_failure_context`, `log.txn_lifecycle`, `log.classify_failure` | see M.2 | bounded, joined context for one failure; DV-versus-RTL verdict with evidence | M.2 convention |
| `tb.topology`, `tb.tlm_graph`, `tb.sequence_dry_run`, `rtl.clock_tree`, `rtl.reset_tree` | see M.1 | testbench and design structure as JSON | M.1 walks over slang and RTLIL |

### 3.5 Planner role (W on plan drafts only)

| Tool | Arguments | Returns | Built on |
|---|---|---|---|
| `plan.draft_items` | spec section, block | candidate items with stimulus, checking, coverage intents, marked draft | LLM over `spec.section` and `regs.query`; a person approves at gate 1 |
| `plan.trace` | requirement id | item, tests, coverage, results | StrictDoc or Doorstop links plus `plan.report` |

## 4. The gap map, in build order

Merged from both surveys and ordered by leverage per unit of effort. The first five are small; the book could build them as examples.

| # | Gap | Software has | Effort | Why first |
|---|---|---|---|---|
| 1 | SARIF wrapper for Verible and svlint; baseline diff (G2) | SARIF everywhere | days | makes every lint loop tool-agnostic; Verilator already emits it |
| 2 | Agreed tool schemas and a DV `AGENTS.md` convention (G8) | MCP schemas, AGENTS.md | days | every other server benefits; the book's flow is a worked instance |
| 3 | Coverage half of the plan report: bins joined to plan items (Ch. 2 follow-up) | none exact | days | turns "tests pass" into "closed" |
| 4 | Machine-readable formal counterexample trace (G7, traces only) | CBMC JSON traces | days | lets `formal.prove` feed the debug tools |
| 5 | Repository map for SV (Aider-style) | Aider repo-map | days | cheapest context win |
| 5a | UVM log signature convention + JSON emitter + `log.first_failure_context` (M.2) | structured logging, distributed tracing | days to a week | turns the largest artifact in DV into bounded, joined context; enables the DV-versus-RTL verdict |
| 5b | Clock and reset tree, connection graph from RTLIL/pyslang (M.1) | dependency graphs | a week | first half of open CDC; every debug question starts here |
| 5c | Static UVM topology, TLM graph and dry sequence trace over slang's class model (M.1) | DI-graph and call-graph analysis | weeks | no open tool understands the testbench today |
| 6 | Shrinking for constrained-random failures (G4) | Hypothesis, cvise | weeks | halves debug effort per failure |
| 7 | Failure clustering by first-error signature (G6, dedup half) | ClusterFuzz | weeks | one hypothesis per cluster instead of per seed |
| 8 | Open RTL mutation tool with SV operators and per-mutant reports (G3) | mutmut, PIT | months | the honest metric for agent-written stimulus |
| 9 | Full-surface SV/UVM language server with rename (G1) | pyright, rust-analyzer | months | slang has the front end; the LSP surface is the work |
| 10 | Debug adapter over a simulator (G6, protocol half) | DAP | months | interactive debug from one client |
| 11 | Regression selection and flaky quarantine as CI features (G11) | predictive selection, quarantine lists | months | needs a regression database first |
| 12 | Open regression database and schema | JUnit into CI stores | months | prerequisite for 11 and for grounding debug agents in history |
| 13 | DV task benchmark with held-out checkers (G10) | SWE-bench, SWE-smith | months | the only way to measure bug-finding power of agents honestly |
| 14 | Hermetic wrappers and sandboxes that coexist with licence servers (G5, G14) | Bazel, Nix, Firecracker | policy plus engineering | commercial-flow adoption depends on it |
| 15 | Open CDC/RDC, UCIS binary readers, emulation | n/a | large | no open path; vendor-only for now |

## 5. Questions for discussion

1. Which of the first five gaps should the book build as examples in Part V or Part VII, and which belong in an appendix?
2. Should the tool schemas in section 3 be published as a standalone convention (a small spec plus a reference server over the book's build system), or stay internal to the book?
3. The stimulus role's server has no oracle write tool by construction. Is read access to the checker denied too (stronger, costlier), or allowed (Chapter 34's current position: write-denial is the rule, read-denial an option)?
4. The plan report currently measures test evidence only. Does the coverage join (gap 3) belong in Chapter 8 (functional coverage) as its worked example?
5. Which existing servers should the book cite as reference implementations: wave-mcp and pyslang-mcp are the clear open candidates; TraceWeave needs commercial libraries for FSDB.
6. For AST-based tools, is tree-sitter-systemverilog complete enough for the book's rules, or should structural search be specified over slang's elaborated tree?
7. Where does the "regression history as text" knowledge base live, and who owns it, given that it grounds every debug agent?
8. What is the minimum measurement plan (Chapter 34, section on measuring) a team must run before any of this is adopted?
9. The message-signature convention (M.2) needs a transaction identifier to survive from sequence to monitor. Which mechanism does the book recommend: a sideband tag the monitor can read, ordering plus a sequence number, or a payload-derived hash? Each fails differently under reordering and drops.
10. Should M.2 become the worked example of the debug chapter (Chapter 28), with the FIFO environment retrofitted to the convention, so that the four verdicts are demonstrated on a real log?

## 6. Building the tools: designs, use cases, and where they go in the book

Added 2026-09-07 in answer to the author's question. This section proposes how each tool in domain M and the top of the build order would actually be built with the open tools the surveys found, what a verification engineer or an agent would do with it, and which chapter it becomes a worked example of. One principle governs all of it: **the tools are deterministic programs, not agents.** They take a design, a testbench or a log and return JSON. They run in the book's continuous integration like every other example, need no model access, and are the tool layer that Chapter 34's agents would call. The agent loops that call them are a separate, later question; the tools are useful to a person on day one.

### 6.1 One substrate, three doors

Everything below is one Python package, working name `dvh` (for DV handbook), under `tools/dvh/` in the repository, with a command-line interface, JSON output, and an MCP server that exposes the same functions. Three thin layers, each a few hundred lines:

| Layer | Provides | Built on |
|---|---|---|
| **Design model** | elaborated hierarchy, ports, parameters, symbols, drivers and loads; cached as JSON per top | pyslang (elaboration); Yosys `prep; write_json` (netlist for cone and clock walks); Verible CST JSON (syntax-level, error-tolerant) |
| **Testbench model** | class hierarchy, `build_phase` construction sites, config-db keys, `connect_phase` edges, sequence bodies | pyslang's class and method AST; a small interpreter for the dozen UVM idioms that matter |
| **Evidence model** | log records, transaction lifecycles, plan items, coverage bins, waveform windows | the UVM message convention (M.2); `plan_report.py`'s plan schema; `verilator_coverage --write-info` (lcov) and cocotb-coverage XML; pylibfst |

Each tool is a pure function from these models to JSON, which makes it testable with pytest against small fixtures (the book's FIFO and counter), deterministic, and cheap to expose: the shell door is the CLI, the file-format door is the JSON it writes, and the protocol door is the MCP server generated from the same function signatures with the Python SDK.

### 6.2 Tool designs

**`rtl.clock_tree` and `rtl.reset_tree`.** Run Yosys `read_slang` (or `read_verilog -sv`), `prep`, `write_json`. Every sequential cell (`$dff`, `$adff`, `$sdff`, `$dffe` and friends) has a clock input and, for the reset variants, a reset input and polarity. Walk each clock net backwards through buffers, multiplexers, gates and inverters to its source: a top-level port, a PLL or divider model, or a register (a divided clock, which starts a new domain). Group registers by source net; the output is a tree per source and a table of registers with clock, reset, reset polarity and synchronicity. A crossing is a register whose data-input cone contains a register of a different clock domain; report each with the path. That last step is the first half of a CDC checker, and the second half (recognising synchronizer structures and waiving them) is a good exercise. The tool exposes what no open tool does today and what every debug question starts with.

**`rtl.connections`.** From pyslang's elaborated instances, or from the Yosys JSON `netnames` and `cells`, build a graph whose nodes are instance ports and whose edges are nets, with `.*` and modport connections resolved. Output as JSON adjacency plus, optionally, an SVG block diagram drawn with the book's own `figures/blocks.py`, so the chapter's figures and the tool's output share one visual language.

**`tb.topology` (static).** Walk every class that extends `uvm_component`. In its `build_phase`, collect `<Type>::type_id::create("<name>", this)` and `<Type>::new("<name>", this)` calls; record `set_type_override_by_type` and `set_inst_override_by_type` calls anywhere; record `uvm_config_db#(T)::set(...)` and `::get(...)` sites with their key strings and scope patterns. Resolve overrides, build the tree, and mark nodes whose type or name is computed at run time as unresolved. The dynamic counterpart parses `print_topology()` output, whose format is fixed by the reference implementation. The diff between the two is the tool's most useful output: a factory override that changed a component's type, a config-db key set with a scope pattern that matches nothing, a `get` with a type that no `set` provides.

**`tb.tlm_graph`.** In every `connect_phase`, match `<a>.<port>.connect(<b>.<export>)` and its variants, resolve `a` and `b` against the topology, and emit edges. Report analysis exports with no producer and analysis ports with no consumer: a scoreboard nothing feeds is the classic silent-pass bug.

**`tb.sequence_dry_run`.** Walk a sequence class's `body()`. slang expands the `uvm_do` macro family, so the walk looks for `start_item` and `finish_item` pairs, `randomize()` calls and explicit field assignments between them, `.start(<sequencer>)` calls on sub-sequences (recursed), and `grab`, `lock`, `p_sequencer` references. Loops with constant bounds are unrolled up to a limit and summarised as `×N` above it; loops with randomised bounds are summarised symbolically; both branches of a conditional are kept with the condition attached; randomised fields are printed as their constraint set rather than a value. The output is an expected transaction-order sketch: what the sequence will try to send, in what order, on which sequencer, before a simulator runs. Compared against the plan item's stimulus intent, it is a review of an agent-written or human-written sequence at zero simulation cost.

**The message-signature convention (M.2), SystemVerilog side.** Three small pieces. A `dvh_txn` base class extending `uvm_sequence_item` with a `txn_id` field allocated from a global counter at creation. A set of macros, `` `dvh_info(ROLE, txn, STAGE, "key=value ...") ``, that wrap `uvm_info` and build the message ID from the grammar in M.2 so that the convention cannot be misspelt. A `dvh_report_server` extending `uvm_report_server` that, in addition to the text line, appends one JSON object per message to a `.jsonl` file: time, severity, scope, role, transaction id, stage, and the payload parsed into key-value pairs. The transaction id crosses the pin boundary by whichever mechanism the interface allows: a sideband tag when there is one, a sequence number when the stream is ordered (the FIFO), or a payload hash when neither, and the convention records which was used so the join's failure modes are known.

**The message-signature convention, Python side.** `log.uvm_parse` reads either the JSON lines or the text log through the ID grammar. `log.txn_lifecycle` joins on the transaction id. `log.classify_failure` applies the four-verdict rule table: which stages are present for the failing transaction, whether the driven and observed payloads are equal, whether the model's expectation matches the specification (a question it can only flag, not answer). `log.first_failure_context` composes the bounded context in the fixed order. `log.compress` groups INFO lines by a signature made of role, stage and the message with numbers masked, keeps counts, transitions and every error, and is what a person or an agent reads first.

**The coverage half of the plan report.** Plan items already carry a coverage intent in prose; the tool needs bins. Extend the plan schema with an optional `bins` list naming covergroups and bins (SystemVerilog) or cover points (cocotb-coverage). Read Verilator's lcov file for code coverage and cocotb-coverage's XML for functional bins, and report per item: bins named, bins hit, and closure as the conjunction of tests passing and bins hit. This is the missing half of Chapter 2's tool, and Chapter 8's natural worked example.

**SARIF wrapper for Verible and svlint.** Both emit `file:line:col: message [rule]` lines. A converter to SARIF 2.1 (rules array, results with locations and rule ids, a fingerprint per finding) is small; `sarif-tools` then diffs against a baseline so an agent fixes only what it introduced. Verilator's native SARIF completes the set.

**`repo.map`.** From Verible's CST JSON or pyslang: modules, ports, parameters, classes, tasks and functions, ranked by how often they are referenced, truncated to a token budget. The same idea as a software repository map, and the cheapest way to give an agent a block's shape without its text.

**`test.shrink`.** Record the transaction stream of a failing random run (the convention's JSON lines already are that record). Replay subsets with the sequence replaced by a replay sequence, using the delta-debugging algorithm: halve, test, keep the failing half, refine. The output is the shortest transaction list that still fails, with its seed, which is what a person or a debug agent should be handed instead of the original run.

**`triage.cluster`.** Signature per failing run: first error's role, stage, scope with instance indices masked, message with numbers masked, and the phase. Cluster by signature; one representative per cluster with the count of seeds. The software model is crash deduplication by stack signature.

### 6.3 Use cases, as narratives

1. **The block brief.** A new engineer, or an agent, is handed a block. One command produces a page: the hierarchy, the clock and reset domains and any crossings, the connection graph as a diagram, the testbench topology with its factory overrides, the TLM graph, the plan with each item's evidence state. Everything in it is derived, not written, so it is never stale.
2. **Nightly triage.** A regression with forty failing seeds. Clustering reduces them to three signatures. For each, the lifecycle join produces the bounded context and a verdict: two clusters are reference-model suspects and go to the oracle owner; one is an RTL suspect with the monitor's time and signals, and `wave.first_divergence` against a passing seed gives the cycle. A person reads three contexts instead of forty logs.
3. **Reviewing a sequence before running it.** An agent, or a colleague, submits a new sequence for plan item FIFO-007. The dry run shows it never attempts a write while full, because the loop bound is randomised between one and eight. The review catches it in seconds; the simulator would have reported a pass with the hole still open.
4. **A CDC gate on every edit.** The clock-tree tool runs in the pre-commit hook. An edit that routes a signal from the bus-clock domain into the core-clock domain without a synchronizer fails the commit with the path printed.
5. **Closing a plan item.** The coverage join reports item 005 with all tests passing and two bins unhit. The stimulus role is given exactly those bins as its target. When they are hit, the item closes by the plan's own criterion, not by anyone's impression.
6. **A reviewer's mutation report.** The mutant set from Yosys mcy, run through the regression, yields a kill rate per plan item. The item whose tests kill no mutants is the item whose checker is not checking, and the report says which.
7. **Retrofitting the convention.** An existing environment is converted in three steps: the base transaction class, the macro, the report server. The first day's log already supports the lifecycle join; the classifier follows once the stages are consistent.

### 6.4 Where each lands in the book

The tools are chapters' worked examples, built when the chapter is written, so that each tool exists because a chapter needed it.

| Tool | Chapter | Role in the chapter |
|---|---|---|
| `rtl.clock_tree`, `rtl.reset_tree`, `rtl.connections` | Ch. 3, Digital Design for Verifiers | the worked example: read a design's clocks, resets and connections before writing a test |
| `repo.map`, SARIF wrapper | Ch. 27, Testbench Infrastructure | lint as SARIF in CI; the map as the first thing a regression report links to |
| Coverage half of the plan report | Ch. 8, Functional Coverage | the worked example: bins joined to plan items, closure by criterion |
| `tb.topology` (static and dynamic), config-db checks | Ch. 11, UVM Architecture | the worked example: see the testbench the factory actually built |
| `tb.sequence_dry_run` | Ch. 12, Sequences, Sequencers, Drivers | the worked example: review a sequence at zero simulation cost |
| Message-signature convention, `dvh_txn`, report server, lifecycle join | Ch. 13, Monitors, Scoreboards, Checkers | introduced with the first scoreboard; the FIFO environment adopts it |
| `tb.tlm_graph` | Ch. 13 | exercise: find the unfed scoreboard |
| `log.classify_failure`, `log.first_failure_context`, `triage.cluster`, `test.shrink` | Ch. 28, Debug Methodology | the worked example: nightly triage on a seeded regression of the FIFO |
| CDC crossing report from the clock tree | Ch. 20, Structural Verification | the worked example: a minimal open CDC checker, with its limits stated |
| Mutation report | Ch. 29, Metrics and Closure | the worked example: kill rate per plan item |
| `formal` tools, counterexample trace | Ch. 17, Formal Verification | counterexamples handed to the debug tools |
| The MCP server over all of the above | New appendix, "An agent tool layer for this book's examples" | the protocol door; tool schemas as a published convention if the author chooses; agent loops that call it remain out of the book's runnable examples until the recorded-transcript question is settled |
| The whole set, as concepts | Ch. 34 | already there: domains B, D, H, K of this catalogue are what Chapter 34's tool layer means in practice |

Repository layout: `tools/dvh/` for the package with its own pytest suite run by the example checker (a fourth language recipe, `python.mk`, already exists); `examples/chNN-*/` directories that call it; `tools/dvh/mcp_server.py` for the protocol door; the SystemVerilog side (`dvh_txn`, macros, report server) under `examples/lib/dvh/` so every UVM example in Parts III and VI includes it.

### 6.5 Sequence of work

1. Chapter 3's tools first (clock, reset, connections), because Chapter 3 is next and the design model they need is the foundation for everything else.
2. The message-signature convention next, retrofitted onto the appendix's UVM counter example and the future FIFO environment, because every later debug example depends on the log being joinable.
3. The coverage join, when Chapter 8 is written.
4. Topology, TLM graph and dry trace with Part III.
5. Triage, shrinking and clustering with Chapter 28.
6. The MCP server and the appendix last, once the functions exist and have a year of use behind them.
