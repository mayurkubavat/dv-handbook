# Research index

One file per topic. Each note: header (title, date, author, status), findings with inline citations, key sources, confidence notes.
Link every note from `STATUS.md` → "Research references" with what it feeds.

| File | Topic | Status | Feeds |
|---|---|---|---|
| `genai-agentic-flows.md` | Generative AI & agentic flows (general) | done (2026-09-05, ~3.6k words) | Ch. 34, design §6 |
| `sw-engineering-ai-era.md` | Modern SW engineering practices, AI era | done (2026-09-05, ~3.1k words) | Ch. 27–29, 32, 34 |
| `ai-in-dv-state-of-the-art.md` | AI/ML/LLM/agents applied to DV & EDA | done (2026-09-06, ~3.4k words) | Ch. 33–35 |
| `dv-adaptation-synthesis.md` | Synthesis: adapting SW/GenAI practice to DV | done (2026-09-06, ~4.3k words) | Ch. 34, book workflow |
| `ch01-cost-gap-lifecycle.md` | Survey figures, cost of bugs, escapes, definitions, lifecycle, sign-off | done (2026-09-06, ~3k words) | Ch. 1 |
| `ch02-verification-planning.md` | Plan definitions, feature extraction, traceability, coverage model, OpenTitan plan format + sign-off stages, failure modes, AI-generated plans | done (2026-09-06, ~4.5k words) | Ch. 2 |
| `ch34-concept-sources.md` | Primary sources for generative-AI concepts, SW-practice parallels, governance | done (2026-09-06, 43 bib entries) | Ch. 34 |
| `tooling-landscape-software.md` | Catalogue of tools/protocols AI coding agents use in SW engineering (LSP, tree-sitter, SARIF, test/coverage/mutation/fuzz, build/CI/sandbox, DAP/rr/OTel, formal, MCP/A2A/AGENTS.md, docs/requirements, eval gates) + 14 HW gaps | draft (2026-09-07, ~10.7k words, 244 URLs verified) | tooling catalogue, Ch. 34 follow-up |
| `tooling-landscape-hardware.md` | Open (and labelled vendor) RTL/DV/debug tools an agent could call: parsers, sims, coverage, waveforms, formal, MCP servers, spec tooling, CI; gaps | done (2026-09-07, ~120 rows) | tooling catalogue, Ch. 34 follow-up |
| `ch03-digital-design-for-verifiers.md` | RTL/synthesis semantics, clocks and metastability, resets and RDC, FSMs, handshakes and FIFOs, interfaces, lint and X, structural extraction (Yosys/slang/Verilator) | done (2026-09-07, ~17k words in three parts, 50 bib entries) | Ch. 3 |
| `agentic-dv-tools-synopsys.md` | Synopsys AI/agentic tooling for RTL and DV: Synopsys.ai, VSO.ai, copilots, AgentEngineer; twelve claimed figures with provenance | done (2026-09-07, ~2.8k words) | Appendix on the agent tool layer |
| `agentic-dv-tools-cadence.md` | Cadence: Verisium and its apps, JedAI, Xcelium ML, agentic scope as of 2025 | done (2026-09-07, ~2.6k words; cadence.com returned 403, text recovered from verbatim republication) | Appendix on the agent tool layer |
| `agentic-dv-tools-amiq-others.md` | AMIQ EDA (DVT IDE, DVT MCP Server and its 39 tools, Verissimo, Specador), Siemens, Aldec | done (2026-09-07, ~2.8k words) | Appendix on the agent tool layer |
| `agentic-dv-tools-open.md` | Open and academic: MCP servers for hardware, parsers and elaborators, waveform libraries, benchmarks; maturity table with licences and last activity | done (2026-09-07, ~3.9k words, 54 URLs) | Appendix on the agent tool layer |
| `ch04-simulation-fundamentals.md` | Event queue and timestep, scheduling regions, races and the assignment guidelines derived from them, testbench/design sampling, clocking and program blocks, assertion sampling, four-state vs two-state, timescale, and what Verilator and Icarus actually implement | done (2026-09-09, ~16.8k words in three parts) | Ch. 4 |
| `ch05-testbench-language.md` | Testbench types and the two-state/four-state boundary, aggregates, structs/enums, interfaces and virtual interfaces, classes as the language defines them with the Ch.5/Ch.6 line, and a measured Verilator/Icarus support matrix for every construct (57 probes) | done (2026-09-11, ~15.7k words in three parts) | Ch. 5; Ch. 6 (virtual-dispatch pitfall); Ch. 7 (randomization needs an SMT solver) |
| `ch06-oop-testbench-design.md` | Inheritance and dispatch, abstract and interface classes, `$cast` and copying in a hierarchy; parameterized classes and the factory, strategy, template-method, singleton and callback patterns traced to UVM and OpenTitan; substitutability; a measured 51-row matrix of OOP support on Verilator and Icarus with a catalog of 16 silent wrong results | done (2026-09-11, ~19k words in three parts) | Ch. 6; Ch. 11–12 (UVM factory and phases) |
| `ch07-constrained-random.md` | `rand`/`randc`, `randomize()` and its silent failure, every constraint form, random stability and seeds; why constrained-random exists, what a solver does and does not promise, distributions; a measured 31-row matrix on both simulators with and without `z3`, and a catalog of silent wrong results | done (2026-09-12, ~18k words in three parts) | Ch. 7; Ch. 12 (sequences and seeds); Appendix F (the solver as part of the free toolchain) |

## Conventions
- Cite as `[Source, YYYY-MM-DD](URL)`; separate vendor claims from peer-reviewed results.
- Mark unverified claims in a "Confidence notes" section.
- When a note is used in a chapter, add the chapter number to "Feeds" and cite in `refs.bib`.
