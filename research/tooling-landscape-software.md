---
title: Tooling Landscape for AI Coding Agents in Software Engineering
date: 2026-09-07
author: research-agent
status: draft
feeds: tooling catalogue / Ch. 34 follow-up
scope: Exhaustive catalogue of the tools, protocols and automation flows that AI coding agents call in software engineering, organised so each can be mapped to a hardware-verification counterpart. URLs verified by HTTP fetch on 2026-09-07 unless marked otherwise.
---

## 0. How to read this note

Each section has a table with the same seven columns: **tool**, **what it is**, **agent use** (what a coding agent actually does with it), **interface** (CLI / LSP / API / MCP / library / file format), **license**, **maturity**, **URL**. "Maturity" uses four levels: *standard* (a written spec with multiple independent implementations), *mature* (widely deployed for five or more years, stable release cadence), *active* (in wide use, still changing quickly), *research* (paper or prototype). Interface abbreviations: LSP = Language Server Protocol, DAP = Debug Adapter Protocol, MCP = Model Context Protocol, SARIF = Static Analysis Results Interchange Format.

Two cross-cutting observations drive the rest of the note. First, agents consume tools through **three doors**: a shell (CLI plus parseable stdout, still the dominant path), a **protocol** (LSP, DAP, MCP, a REST API), or a **file format** (SARIF, JUnit XML, LCOV, OpenAPI, ReqIF). The file-format door matters most for hardware mapping because it is the cheapest to add to an existing EDA flow. Second, the value of a tool to an agent is set by how **machine-readable and localised** its feedback is: a linter that emits file, line, rule-id and a fix suggestion closes a loop; one that prints prose does not.

The publication rule for this repository forbids citing the AI assistant vendor's own materials. All citations below are open-source repositories, specifications, standards, papers or independent write-ups. Other vendors' materials are cited and labelled as vendor sources.

## 1. Code understanding via ASTs and language servers

**What agents do with these.** Two distinct jobs. *Navigation*: answer "where is X defined, who calls it, what is its type" without reading whole files, so the agent can keep its context window small. *Editing*: make structural changes (rename a symbol across a repo, rewrite every call matching a pattern) that are correct by construction rather than by text search-and-replace. Language servers serve both; tree-sitter and ast-grep serve editing and lightweight navigation; CodeQL and Semgrep serve semantic search over large codebases; SCIP/ctags serve cross-repo indexing.

| Tool | What | Agent use | Interface | License | Maturity | URL |
|---|---|---|---|---|---|---|
| Language Server Protocol (LSP) | JSON-RPC protocol between editor and language-analysis server; v3.17 spec | Go-to-definition, find-references, hover types, diagnostics, rename, code actions; agents drive it via an LSP client library | LSP (JSON-RPC over stdio) | Spec: CC-BY / MIT (Microsoft) | standard | https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/ |
| LSP implementations index | Community list of language servers and clients | Discover which language has a usable server | web | n/a | standard | https://langserver.org/ |
| tree-sitter | Incremental parsing library that produces concrete syntax trees; grammars per language; S-expression query language | Fast, error-tolerant parsing for chunking files, extracting symbol outlines, locating nodes to edit, without a full compiler | C library with Rust/Python/Node bindings, CLI | MIT | mature | https://github.com/tree-sitter/tree-sitter |
| tree-sitter query syntax | Pattern language over syntax trees (captures, predicates) | Agents write queries to find every function with a given decorator, every call to an API, etc. | query files (`.scm`) | MIT | mature | https://tree-sitter.github.io/tree-sitter/using-parsers/queries/1-syntax.html |
| tree-sitter-verilog / tree-sitter-systemverilog | Community grammars for Verilog/SystemVerilog | Direct HW counterpart hook: outline modules, ports, always blocks for an agent | grammar | MIT | active | https://github.com/tree-sitter/tree-sitter-verilog |
| ast-grep | Structural search/replace using tree-sitter patterns that look like the target language | Code-mod at scale: "rewrite every `foo($A)` to `bar($A)`", lint rules in YAML, JSON output for agents | CLI (`sg`), YAML rules, `--json` | MIT | active | https://github.com/ast-grep/ast-grep |
| Semgrep (OSS engine) | Pattern-based static analysis; rules in YAML, semantic patterns with metavariables; registry of rules | Find bug classes and API misuse; emit SARIF/JSON findings the agent fixes; write project-specific rules | CLI, `--sarif`, `--json` | LGPL-2.1 (engine); rules vary | mature | https://github.com/semgrep/semgrep |
| CodeQL | Treats code as a relational database; queries in QL language; dataflow and taint analysis | Deep semantic queries ("all paths from user input to this sink"), variant analysis; SARIF output; integrates with GitHub code scanning | CLI, QL language, SARIF | CLI free for OSS; engine proprietary (GitHub, vendor) | mature | https://codeql.github.com/ |
| CodeQL open-source query packs | The QL query libraries | Agents reuse or extend standard queries | QL | MIT | mature | https://github.com/github/codeql |
| Comby | Structural search-and-replace with a lightweight template syntax; language-aware bracket matching | Quick rewrites where a full grammar is unavailable | CLI, `-json-lines` | Apache-2.0 | mature (low activity) | https://github.com/comby-tools/comby |
| Universal Ctags | Generates tag index of symbols (definitions) for 100+ languages including Verilog/SystemVerilog | Cheap symbol index for "jump to definition" without a language server | CLI, tags file (JSON output option) | GPL-2.0 | mature | https://github.com/universal-ctags/ctags |
| SCIP (Sourcegraph Code Intelligence Protocol) | Protobuf index format for cross-repo, precise code navigation; successor to LSIF | Precise references and definitions across a monorepo or many repos, built offline in CI | protobuf index files + indexers (scip-python, scip-typescript, etc.) | Apache-2.0 | active | https://github.com/sourcegraph/scip |
| LSIF | Earlier language-server-index format | Legacy; mention only | JSON index | Microsoft spec | mature, deprecated in favour of SCIP | https://lsif.dev/ |
| Sourcegraph (vendor; source snapshot) | Code search across repos, uses SCIP for precise nav; the main repository went private in 2024 and a read-only public snapshot remains | Repo-wide search agents query via GraphQL API | API (GraphQL), web | Apache-2.0 for the snapshot; current product proprietary (vendor) | mature | https://github.com/sourcegraph/sourcegraph-public-snapshot |
| Multilspy (Microsoft Research) | Python library that spawns language servers and exposes LSP as a static-analysis API for LLM agents | Reference implementation of "LSP as an agent tool"; underlies Monitor-Guided Decoding paper | Python library | MIT | active | https://github.com/microsoft/multilspy |
| Serena | Open-source coding-agent toolkit that wraps language servers as MCP tools (find symbol, references, insert after symbol) | Canonical example of LSP-to-MCP bridge | MCP server | MIT | active | https://github.com/oraios/serena |
| lsp-mcp (community) | Small generic LSP-to-MCP bridge servers | Alternative bridges | MCP | MIT (varies) | early | https://github.com/Tritlo/lsp-mcp |
| Aider repo-map | Tree-sitter based ranked "repository map" that gives an LLM a compressed outline of a repo | Widely copied technique for feeding structure, not text, into context | library / write-up | Apache-2.0 | active | https://aider.chat/docs/repomap.html |
| Monitor-Guided Decoding (paper) | Uses static analysis (via LSP) to constrain LLM token generation to valid identifiers | Evidence that static-analysis-in-the-loop reduces hallucinated APIs | paper (NeurIPS 2023) | n/a | research | https://arxiv.org/abs/2306.10763 |

**Navigation vs. editing.** For navigation, agents call LSP (`textDocument/definition`, `references`, `documentSymbol`), ctags or SCIP; for editing they prefer AST-level rewriters (ast-grep, Comby, LSP `rename` and `codeAction`) because text patches from an LLM are the dominant source of syntax errors in agent traces. A common pattern is "propose with the LLM, validate with the parser": the agent applies a text edit, re-parses with tree-sitter, and rejects the edit if the tree contains `ERROR` nodes.

**Hardware counterparts.** The SystemVerilog language-server landscape is covered in the companion hardware note; the relevant open servers are Verible's `verible-verilog-ls` (https://github.com/chipsalliance/verible), `svls` (https://github.com/dalance/svls), `veridian` (https://github.com/vivekmalneedi/veridian) and `slang` as a front end (https://github.com/MikePopoloski/slang). Their coverage of the LSP surface (references, rename, code actions) is far below that of pyright or rust-analyzer; this is Gap G1 in §10.

## 2. Static analysis, lint and formatting as agent feedback

**What agents do with these.** Run the tool, parse the structured output, patch, re-run until clean. The loop only works when the output carries a location, a stable rule identifier, a severity and ideally a machine-applicable fix. SARIF is the interchange format that makes these loops tool-agnostic: an agent that understands SARIF can consume any of dozens of analysers without per-tool parsers. Formatters are the simplest closed loop of all: the agent never needs to reason about style, it just runs the formatter and commits.

| Tool | What | Agent use | Interface | License | Maturity | URL |
|---|---|---|---|---|---|---|
| SARIF 2.1.0 (OASIS standard) | JSON format for static-analysis results: runs, rules, results, locations, fixes, code flows | The one format an agent parser should target; supported by CodeQL, Semgrep, ESLint, clang-tidy (via converter), Trivy, Bandit, PMD, etc. | JSON file format | OASIS open standard | standard | https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html |
| SARIF tooling (sarif-tools, multitool) | Converters, validators, diffing of SARIF files | Diff "new findings vs. baseline" so the agent only fixes what it introduced | CLI (Python) | MIT | active | https://github.com/microsoft/sarif-tools |
| GitHub code scanning SARIF upload | CI consumes SARIF and renders inline annotations | Agents and humans see the same findings in the PR | REST API | vendor (GitHub) | mature | https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning |
| Ruff | Fast Python linter and formatter (Rust) with `--fix` and `--output-format=sarif`/`json` | Auto-fix loop; replaces flake8/isort/pyupgrade | CLI | MIT | mature | https://github.com/astral-sh/ruff |
| ESLint | JavaScript/TypeScript linter with rule plugins, `--fix`, SARIF formatter | Same loop for JS/TS | CLI, Node API | MIT | mature | https://github.com/eslint/eslint |
| clang-tidy | Clang-based C/C++ linter with fix-its; `-export-fixes` YAML | Apply fix-its mechanically via `clang-apply-replacements` | CLI, YAML fixes | Apache-2.0 with LLVM exception | mature | https://clang.llvm.org/extra/clang-tidy/ |
| clang-format / Black / Prettier / gofmt / rustfmt | Deterministic formatters | Remove style from review; agent runs them pre-commit | CLI | Apache/MIT/BSD | mature | https://github.com/psf/black |
| Pyright | Static type checker for Python (also the engine behind Pylance); JSON output | Type errors as agent feedback; `--outputjson` | CLI, LSP | MIT | mature | https://github.com/microsoft/pyright |
| mypy | Reference Python type checker | Same; slower but PEP-canonical | CLI | MIT | mature | https://github.com/python/mypy |
| TypeScript compiler (`tsc`) | Type-checks TS; `--pretty false` gives parseable diagnostics | Same loop for TS | CLI, LSP (tsserver) | Apache-2.0 | mature | https://github.com/microsoft/TypeScript |
| Bandit | Python security linter, SARIF/JSON output | Security findings in the fix loop | CLI | Apache-2.0 | mature | https://github.com/PyCQA/bandit |
| Trivy | Vulnerability/misconfiguration scanner for containers, filesystems, IaC; SARIF output | Dependency and container scanning gate | CLI | Apache-2.0 | mature | https://github.com/aquasecurity/trivy |
| OSV-Scanner | Scans lockfiles against the OSV vulnerability database | Dependency CVE gate; JSON/SARIF | CLI | Apache-2.0 | active | https://github.com/google/osv-scanner |
| Infer (Meta) | Interprocedural static analyser for C/C++/Java/ObjC (null deref, leaks, races) | Deeper bug finding than lint; JSON report | CLI | MIT | mature | https://github.com/facebook/infer |
| cppcheck | C/C++ static analyser with XML/SARIF output | Lightweight C/C++ checks | CLI | GPL-3.0 | mature | https://github.com/danmar/cppcheck |
| reviewdog | Bridges any linter output (errorformat, SARIF, RDFormat) to PR review comments | Uniform "linter findings as review comments" for humans and bots | CLI, GitHub Action | MIT | mature | https://github.com/reviewdog/reviewdog |
| pre-commit framework | Runs hooks (formatters, linters) on staged files | Agents install the same hooks so their commits are gated like a human's | CLI, YAML config | MIT | mature | https://github.com/pre-commit/pre-commit |
| EditorConfig | Cross-editor whitespace/encoding conventions | Trivial but universal | file format | spec | standard | https://editorconfig.org/ |

**Pattern.** The mature agent loop is: *analyse → SARIF → filter to changed lines (baseline diff) → fix (auto-fix where the tool offers one, LLM where it does not) → re-analyse*. Ruff, ESLint and clang-tidy all expose machine-applicable fixes, which means the LLM is only invoked for the residue.

**Hardware counterparts.** Verible lint emits a `--lint_fatal`/text format and has a `--rules` set; Verilator `--lint-only` emits `%Warning-<RULE>: file:line:col` lines that are parseable but not SARIF. No commercial or open lint tool for RTL or UVM emits SARIF today (Gap G2). Formatters exist (Verible formatter) but are not universally adopted, and no UVM-aware formatter exists.

## 3. Test tooling

**What agents do with these.** Tests are the agent's primary oracle. The agent needs (a) a runner with structured pass/fail output per test, (b) coverage to know what its tests reached, (c) mutation testing to know whether the tests would detect a bug at all, (d) generators (property-based, fuzzing) to reach beyond hand-written cases, and (e) infrastructure to handle scale: predictive selection, flaky quarantine, snapshot updates.

### 3.1 Runners and structured output

| Tool | What | Agent use | Interface | License | Maturity | URL |
|---|---|---|---|---|---|---|
| pytest | Python test runner; `--junitxml`, `-p no:cacheprovider`, `--lf` (last failed) | Runs subsets, re-runs failures, structured results | CLI, plugin API | MIT | mature | https://github.com/pytest-dev/pytest |
| pytest-json-report | JSON report per test with stdout/stderr and tracebacks | Easier to parse than JUnit XML | pytest plugin | MIT | mature | https://github.com/numirias/pytest-json-report |
| JUnit XML | De-facto test result format, no formal spec; schema reverse-engineered | Universal CI consumption; hardware regressions could emit it today | XML file format | de facto | standard (de facto) | https://github.com/testmoapp/junitxml |
| Test Anything Protocol (TAP) | Line-oriented test output protocol, v14 | Simplest structured output; used by Perl, node:test, Bats | text protocol | spec | standard | https://testanything.org/tap-version-14-specification.html |
| Google Test | C++ test framework; `--gtest_output=json:` and XML | Same for C++ (also common for SystemC/Verilator testbenches) | library, CLI | BSD-3 | mature | https://github.com/google/googletest |
| Jest / Vitest | JS test runners with JSON reporters, watch mode, snapshot testing | Same for JS/TS | CLI, Node API | MIT | mature | https://github.com/vitest-dev/vitest |
| Bazel test (`bazel test`) | Runs tests as hermetic actions, caches results, emits `test.xml` and Build Event Protocol stream | Result caching means agents only re-run what changed | CLI, BEP protobuf | Apache-2.0 | mature | https://bazel.build/reference/test-encyclopedia |
| Allure | Aggregated test-report format and UI | Human-readable trend reports across agent runs | file format, CLI | Apache-2.0 | mature | https://github.com/allure-framework/allure2 |

### 3.2 Coverage

| Tool | What | Agent use | Interface | License | Maturity | URL |
|---|---|---|---|---|---|---|
| coverage.py | Python line/branch coverage; JSON, XML (Cobertura), LCOV output | Find uncovered lines, generate tests for them | CLI, API | Apache-2.0 | mature | https://github.com/nedbat/coveragepy |
| gcov / lcov | GCC instrumentation and LCOV report format (`.info` tracefiles) | LCOV tracefile is the de-facto interchange format for line coverage; `genhtml` for reports | CLI, LCOV format | GPL | mature | https://github.com/linux-test-project/lcov |
| LLVM source-based coverage | `-fprofile-instr-generate`; `llvm-cov export -format=lcov` or JSON with region/branch/MC-DC | Precise region and MC/DC coverage; export JSON | CLI | Apache-2.0 with LLVM exception | mature | https://clang.llvm.org/docs/SourceBasedCodeCoverage.html |
| Cobertura XML | Coverage XML format consumed by most CI dashboards | Interchange | XML file format | de facto | standard (de facto) | https://github.com/cobertura/cobertura |
| Codecov / Coveralls | Hosted coverage dashboards with PR comments and gates | Coverage-delta gate on agent PRs | API, GitHub App | vendor (SaaS); CLI uploader OSS | mature | https://github.com/codecov/codecov-action |
| Istanbul / c8 | JS coverage (LCOV, JSON) | Same for JS | CLI | BSD/ISC | mature | https://github.com/bcoe/c8 |
| diff-cover | Reports coverage only on lines changed in a diff | "Did the agent test what it changed?" gate | CLI | Apache-2.0 | mature | https://github.com/Bachmann1234/diff_cover |

### 3.3 Mutation testing

| Tool | What | Agent use | Interface | License | Maturity | URL |
|---|---|---|---|---|---|---|
| mutmut | Python mutation testing; mutants cached, incremental | Mutation score as a test-quality oracle; surviving mutants tell the agent which tests to write | CLI | BSD-3 | mature | https://github.com/boxed/mutmut |
| cosmic-ray | Python mutation testing with distributed execution | Same, scales out | CLI | MIT | mature (lower activity) | https://github.com/sixty-north/cosmic-ray |
| Stryker (JS/TS, .NET, Scala) | Mutation testing framework with HTML/JSON report, incremental mode | Same for JS/.NET | CLI, JSON report | Apache-2.0 | mature | https://github.com/stryker-mutator/stryker-js |
| PIT (pitest) | Java mutation testing; bytecode mutation, fast | Reference implementation for JVM | CLI, Maven/Gradle | Apache-2.0 | mature | https://github.com/hcoles/pitest |
| Mull | LLVM-based mutation testing for C/C++ | Mutation of compiled code | CLI | Apache-2.0 | active | https://github.com/mull-project/mull |
| cargo-mutants | Rust mutation testing | Same for Rust | CLI | MIT | active | https://github.com/sourcefrog/cargo-mutants |
| Mutation testing at Google (paper) | Petrović & Ivanković, "State of Mutation Testing at Google", ICSE-SEIP 2018; probabilistic diff-based mutants surfaced in code review | Evidence that mutation testing scales when restricted to changed lines and filtered for productive mutants | paper | n/a | research (deployed at scale) | https://research.google/pubs/state-of-mutation-testing-at-google/ |
| Mutation testing survey | Papadakis et al., "Mutation Testing Advances: An Analysis and Survey", 2019 | Background | paper | n/a | research | https://doi.org/10.1016/bs.adcom.2018.03.015 |

### 3.4 Property-based testing and fuzzing

| Tool | What | Agent use | Interface | License | Maturity | URL |
|---|---|---|---|---|---|---|
| Hypothesis | Python property-based testing; strategies, shrinking, example database, stateful (rule-based) testing | Agent writes properties, not examples; failing cases shrink to minimal reproducers | library | MPL-2.0 | mature | https://github.com/HypothesisWorks/hypothesis |
| QuickCheck (Haskell) | Original property-based testing library (Claessen & Hughes, 2000) | Conceptual ancestor; the paper is the citation | library | BSD-3 | mature | https://hackage.haskell.org/package/QuickCheck |
| fast-check | Property-based testing for JS/TS with shrinking and model-based testing | Same for JS | library | MIT | mature | https://github.com/dubzzz/fast-check |
| proptest | Rust property testing | Same for Rust | library | MIT/Apache-2.0 | mature | https://github.com/proptest-rs/proptest |
| AFL++ | Coverage-guided greybox fuzzer; persistent mode, custom mutators, QEMU mode | Find crashes; corpus as regression tests | CLI | Apache-2.0 | mature | https://github.com/AFLplusplus/AFLplusplus |
| libFuzzer | In-process coverage-guided fuzzer in LLVM; `LLVMFuzzerTestOneInput` harness convention | Harness convention is what agents generate; works with sanitizers | library, CLI | Apache-2.0 with LLVM exception | mature | https://llvm.org/docs/LibFuzzer.html |
| OSS-Fuzz | Google's continuous fuzzing service for open-source projects; build integration scripts | Reference architecture for continuous fuzzing plus triage plus reporting | infrastructure, Dockerfiles | Apache-2.0 | mature | https://github.com/google/oss-fuzz |
| OSS-Fuzz-Gen | LLM-generated fuzz harnesses for OSS-Fuzz projects | Direct evidence of LLM agents generating harnesses; reports coverage gains | framework | Apache-2.0 | research (deployed) | https://github.com/google/oss-fuzz-gen |
| FuzzBench | Fuzzer benchmarking service | Evaluate fuzzers fairly | infrastructure | Apache-2.0 | mature | https://github.com/google/fuzzbench |
| Atheris | Coverage-guided Python fuzzer built on libFuzzer | Fuzz Python code | library | Apache-2.0 | mature | https://github.com/google/atheris |
| cargo-fuzz | libFuzzer for Rust | Same for Rust | CLI | MIT/Apache-2.0 | mature | https://github.com/rust-fuzz/cargo-fuzz |
| Sanitizers (ASan/UBSan/MSan/TSan) | Compiler-instrumented runtime checkers | The oracle that turns a fuzz input into a detected bug | compiler flags | Apache-2.0 with LLVM exception | mature | https://github.com/google/sanitizers |

### 3.5 Snapshot, flaky-test and test-selection infrastructure

| Tool | What | Agent use | Interface | License | Maturity | URL |
|---|---|---|---|---|---|---|
| Jest snapshot testing | Serialise output, compare with stored `.snap`, `-u` to update | Golden-file testing; the agent must justify an update, not just run `-u` | CLI | MIT | mature | https://jestjs.io/docs/snapshot-testing |
| insta (Rust) | Snapshot testing with review tool (`cargo insta review`) | Same, with a review step | CLI, library | Apache-2.0 | mature | https://github.com/mitsuhiko/insta |
| syrupy | pytest snapshot plugin | Same for Python | pytest plugin | Apache-2.0 | mature | https://github.com/syrupy-project/syrupy |
| pytest-rerunfailures | Re-run failing tests N times | Cheapest flaky mitigation; hides flakes rather than fixing | pytest plugin | MPL-2.0 | mature | https://github.com/pytest-dev/pytest-rerunfailures |
| pytest-randomly | Randomise test order to expose order dependence | Flake root-causing | pytest plugin | MIT | mature | https://github.com/pytest-dev/pytest-randomly |
| iDFlakies | Detects order-dependent flaky tests (Java) | Research tool | CLI | MIT | research | https://github.com/idflakies/iDFlakies |
| DeFlaker (paper) | Bell et al., ICSE 2018: detects flaky tests by coverage of changed code without reruns | Flaky detection method | paper | n/a | research | https://www.jonbell.net/icse18-deflaker.pdf |
| "An Empirical Analysis of Flaky Tests" (Luo et al., FSE 2014) | Taxonomy of flaky-test root causes | The standard reference for flake categories | paper | n/a | research | https://doi.org/10.1145/2635868.2635920 |
| Flaky-test quarantine (GitLab, Buildkite Test Engine) | CI-side quarantine: known-flaky tests run but do not gate | Pattern: quarantine list with owner and expiry | vendor docs | vendor | mature | https://docs.gitlab.com/ee/development/testing_guide/unhealthy_tests.html |
| Predictive test selection (Meta, paper) | Machayo et al., "Predictive Test Selection", ICSE-SEIP 2019: ML model picks tests likely to fail for a change | Reference for ML-based regression selection | paper | n/a | research (deployed) | https://arxiv.org/abs/1810.05286 |
| Regression test selection survey | Yoo & Harman, "Regression testing minimization, selection and prioritization: a survey", 2012 | Background | paper | n/a | research | https://doi.org/10.1002/stvr.430 |
| Launchable | Commercial predictive test selection SaaS | Vendor example | API | vendor (proprietary) | active | https://www.launchableinc.com/ |
| pytest-testmon | Selects tests affected by code changes using coverage data | Open-source dependency-based selection | pytest plugin | AGPL-3.0 | mature | https://github.com/tarpas/pytest-testmon |
| Bazel test caching / `--test_sharding` | Content-addressed test result cache and sharding | Structural selection: only tests whose inputs changed re-run | CLI | Apache-2.0 | mature | https://bazel.build/docs/user-manual#test-sharding |

**Hardware counterparts.** Coverage (code and functional) is the one area where hardware tooling is *ahead* in concept (functional coverage, covergroups, UCIS) but behind in interchange: UCIS exists as an Accellera standard but open readers are rare. Mutation testing for RTL exists commercially (Certitude) and in research (see hardware note) but has no open, drop-in tool of mutmut's maturity (Gap G3). Constrained-random stimulus is the hardware analogue of property-based testing; the missing piece is *shrinking* (Gap G4). Fuzzing of RTL has research tools (RFUZZ, DifuzzRTL, TheHuzz, Cascade) covered in the companion note.

## 4. Build, CI and environments

**What agents do with these.** Three things. *Reproduce*: a hermetic build means the agent's local result equals the CI result, so a green run is trustworthy. *Isolate*: many agents work in parallel on one repo, each needs its own checkout, environment and (ideally) kernel boundary. *Automate*: CI systems expose APIs so an agent can trigger a workflow, poll for the result and read logs without a browser.

| Tool | What | Agent use | Interface | License | Maturity | URL |
|---|---|---|---|---|---|---|
| Bazel | Hermetic, content-addressed build with remote caching/execution; Starlark rules; Build Event Protocol | Reproducible builds, incremental test re-runs; `bazel query` for dependency graph questions | CLI, BEP, remote-execution API | Apache-2.0 | mature | https://github.com/bazelbuild/bazel |
| Remote Execution API | gRPC API for remote build/test execution and CAS, shared by Bazel, Buck2, BuildStream | Scale agent test runs across a farm; same API could front a simulator farm | gRPC API | Apache-2.0 | standard | https://github.com/bazelbuild/remote-apis |
| Buck2 | Meta's Bazel-alternative in Rust; same Starlark model, faster, uses Remote Execution API | Same | CLI | MIT/Apache-2.0 | active | https://github.com/facebook/buck2 |
| Nix / Nixpkgs | Purely functional package manager; reproducible environments by hash; flakes | Pin every toolchain byte-for-byte; one `nix develop` gives an agent the same env as CI | CLI, Nix language | LGPL-2.1 | mature | https://github.com/NixOS/nix |
| devenv / devcontainers | Declarative developer environments (Nix-based; Docker-based via `devcontainer.json` spec) | Standardised "how to set up this repo" for agents | JSON spec, CLI | Apache-2.0 / MIT | active | https://containers.dev/ |
| Docker / OCI | Container image format and runtime | Default agent sandbox unit; images as environment snapshots (SWE-bench ships per-task images) | CLI, REST API, OCI spec | Apache-2.0 | mature | https://github.com/opencontainers/image-spec |
| GitHub Actions | CI workflows; REST API to dispatch, list runs, download logs and artifacts; `gh` CLI wraps it | Agents trigger workflows, poll status, read logs (`gh run view --log`) | REST API, CLI (`gh`) | vendor (GitHub); `gh` MIT | mature | https://docs.github.com/en/rest/actions |
| `gh` CLI | GitHub command-line client; JSON output on every command | The dominant way coding agents talk to GitHub (PRs, checks, runs) | CLI, `--json` | MIT | mature | https://github.com/cli/cli |
| GitLab CI | Pipelines API, `glab` CLI | Same on GitLab | REST API, CLI | vendor (GitLab; CE is MIT) | mature | https://docs.gitlab.com/ee/api/pipelines.html |
| Buildkite / Jenkins / Tekton / Argo Workflows | Other CI engines with APIs; Tekton and Argo are Kubernetes-native | Alternatives; Argo Workflows is a DAG engine agents can schedule sim jobs into | REST API | Apache-2.0 (Tekton, Argo, Jenkins MIT); Buildkite vendor | mature | https://github.com/argoproj/argo-workflows |
| act | Run GitHub Actions locally in Docker | Agent tests the CI definition before pushing | CLI | MIT | mature | https://github.com/nektos/act |
| pre-commit | Hook framework (see §2) | Local gate | CLI | MIT | mature | https://github.com/pre-commit/pre-commit |
| git worktree | Multiple working trees from one repository | One worktree per agent task; parallel agents without clone cost | CLI | GPL-2.0 | mature | https://git-scm.com/docs/git-worktree |
| Firecracker | KVM-based microVM monitor (AWS); ~125 ms boot, minimal device model | Strong isolation for untrusted agent code with VM-level boundary | REST API over Unix socket, CLI | Apache-2.0 | mature | https://github.com/firecracker-microvm/firecracker |
| gVisor | User-space kernel (`runsc`) implementing the Linux syscall surface; OCI runtime | Container-compatible sandbox with reduced kernel attack surface | OCI runtime | Apache-2.0 | mature | https://github.com/google/gvisor |
| nsjail | Lightweight process isolation with namespaces, seccomp-bpf, cgroups; protobuf config | Per-command sandbox for agent shell tools | CLI, protobuf config | Apache-2.0 | mature | https://github.com/google/nsjail |
| bubblewrap | Unprivileged namespace sandbox (used by Flatpak) | Same, unprivileged | CLI | LGPL-2.0 | mature | https://github.com/containers/bubblewrap |
| Landlock / seccomp | Linux kernel LSM for unprivileged filesystem sandboxing; syscall filter | Building blocks for the above | kernel API | GPL-2.0 | mature | https://landlock.io/ |
| E2B | Open-source sandbox runtime for AI agents (Firecracker-backed) | Example of a purpose-built agent sandbox | SDK, API | Apache-2.0 (SDK); hosted service vendor | active | https://github.com/e2b-dev/E2B |
| Dagger | Programmable CI/CD engine: pipelines as code in Go/Python/TS, run in containers, content-addressed cache; has an agent-oriented "Dagger Shell" | CI pipelines callable as functions from an agent | CLI, SDK, GraphQL API | Apache-2.0 | active | https://github.com/dagger/dagger |
| Earthly | Dockerfile-like reproducible build syntax | Alternative | CLI | MPL-2.0; README states the project is no longer actively maintained | mature, low activity | https://github.com/earthly/earthly |
| Renovate / Dependabot | Automated dependency-update PRs | The oldest "bot PR" pattern; human gates apply | GitHub App, CLI | AGPL-3.0 (Renovate) / vendor | mature | https://github.com/renovatebot/renovate |
| SWE-bench per-instance Docker images | Reproducible task environments for the benchmark | Reference for "environment as artefact" | Docker images, harness | MIT | active | https://github.com/SWE-bench/SWE-bench |

**Pattern: per-agent isolation stack.** The emerging norm is *worktree (source isolation) + container or microVM (process isolation) + hermetic build (result isolation) + CI API (result publication)*. Agents that skip the middle layer eventually run `rm -rf` on the wrong directory or leak credentials; several open agent frameworks now default to gVisor or Firecracker.

**Hardware counterparts.** Simulator farms already have job schedulers (LSF, Slurm, Grid Engine), and the Remote Execution API plus Bazel rules for Verilator (`rules_verilator`, `rules_hdl`) show that hermetic RTL builds are possible. What is missing is a *hermetic* wrapper around commercial simulators (licence servers, uncached compile) and structured CI logs (Gap G5).

## 5. Debugging and observability

**What agents do with these.** Debuggers are the least-used tool class in current agent traces, because print-debugging plus tests is cheaper in tokens; but the machine interfaces exist and matter for the hard cases. DAP is the debugging analogue of LSP: one protocol, many adapters. Record-replay (rr) turns nondeterministic bugs into deterministic ones, which is exactly what an agent needs to iterate. Crash dedup and bisection are the workhorses of automated triage.

| Tool | What | Agent use | Interface | License | Maturity | URL |
|---|---|---|---|---|---|---|
| Debug Adapter Protocol (DAP) | JSON-RPC protocol between an editor/agent and a debugger adapter: breakpoints, stepping, stack, variables, evaluate | One client drives gdb, lldb, debugpy, delve, etc.; agents set a breakpoint, run, inspect state | DAP (JSON over stdio/socket) | spec (Microsoft, CC-BY) | standard | https://microsoft.github.io/debug-adapter-protocol/specification |
| DAP implementations list | Adapters and clients | Discover adapters | web | n/a | standard | https://microsoft.github.io/debug-adapter-protocol/implementors/adapters/ |
| GDB/MI | GDB's machine interface: line-oriented, parseable command/response protocol (`gdb --interpreter=mi3`) | Older alternative to DAP for C/C++/Rust; Python API (`gdb` module) for scripted debugging | CLI (MI), Python API | GPL-3.0 | mature | https://sourceware.org/gdb/current/onlinedocs/gdb.html/GDB_002fMI.html |
| pygdbmi | Python parser for GDB/MI | Agent library | library | MIT | mature | https://github.com/cs01/pygdbmi |
| LLDB | LLVM debugger with Python scripting and `lldb-dap` adapter | Same for Clang toolchains | CLI, Python API, DAP | Apache-2.0 with LLVM exception | mature | https://lldb.llvm.org/ |
| debugpy | Python DAP adapter (used by VS Code) | Python debugging under DAP | DAP | MIT | mature | https://github.com/microsoft/debugpy |
| pdb | Python's built-in debugger; scriptable via `.pdbrc` or `pdb.Pdb` API | Cheap in-process debugging | CLI, library | PSF | mature | https://docs.python.org/3/library/pdb.html |
| rr | Record-and-replay debugger for Linux: record once, replay deterministically, reverse-step | Makes intermittent bugs reproducible; `rr replay` under gdb | CLI, gdb front end | MIT/BSD-2 | mature | https://github.com/rr-debugger/rr |
| Pernosco | Hosted rr-based omniscient debugger with queryable execution database | Vendor example of "debugging as a database query" | web, API | vendor (proprietary) | mature | https://pernos.co/ |
| Undo (UDB) | Commercial time-travel debugger | Vendor example | CLI | vendor (proprietary) | mature | https://undo.io/ |
| OpenTelemetry | Vendor-neutral spec, SDKs and protocol (OTLP) for traces, metrics, logs | Agents read traces to localise latency or errors; agents also emit their own tool-call traces in OTLP | spec, OTLP (gRPC/HTTP), SDKs | Apache-2.0 | standard | https://github.com/open-telemetry/opentelemetry-specification |
| OpenTelemetry semantic conventions for GenAI | Standard attribute names for LLM/agent spans | Instrumenting agents themselves | spec | Apache-2.0 | active | https://github.com/open-telemetry/semantic-conventions/tree/main/docs/gen-ai |
| Jaeger / Grafana Tempo | Trace stores with query APIs | Trace lookup | API | Apache-2.0 / AGPL-3.0 | mature | https://github.com/jaegertracing/jaeger |
| Grafana Loki / LogQL | Log aggregation with a label-and-grep query language | Log querying via API | API, LogQL | AGPL-3.0 | mature | https://github.com/grafana/loki |
| OpenSearch / Elasticsearch | Full-text log search | Same | REST API | Apache-2.0 / SSPL+ELv2 | mature | https://github.com/opensearch-project/OpenSearch |
| lnav | Terminal log navigator with SQL over logs | Ad-hoc log analysis from a shell | CLI | BSD-2 | mature | https://github.com/tstack/lnav |
| ripgrep | Fast regex search; `--json` output | The most-called tool in agent traces for logs and code | CLI | MIT/Unlicense | mature | https://github.com/BurntSushi/ripgrep |
| ClusterFuzz | Google's fuzzing infrastructure: crash dedup by stack signature, minimisation, bisection to the culprit commit, auto-filing | Reference architecture for crash triage at scale | web, API, Python | Apache-2.0 | mature | https://github.com/google/clusterfuzz |
| ClusterFuzzLite | Lightweight ClusterFuzz for CI | Same in a PR pipeline | GitHub Action | Apache-2.0 | mature | https://github.com/google/clusterfuzzlite |
| Sentry (self-hosted) | Error aggregation with stack-trace fingerprinting | Dedup and grouping of runtime errors | API | FSL (source available) | mature | https://github.com/getsentry/sentry |
| `git bisect run` | Automated bisection given a script that exits 0/1/125 | Agent writes the predicate script, git finds the culprit commit | CLI | GPL-2.0 | mature | https://git-scm.com/docs/git-bisect |
| creduce / cvise | Test-case reducers for C/C++ (and generic text with cvise) | Minimise a failing input before asking the LLM to explain it | CLI | BSD / MIT | mature | https://github.com/marxin/cvise |
| Delta debugging (paper) | Zeller & Hildebrandt, "Simplifying and Isolating Failure-Inducing Input", TSE 2002 (DOI 10.1109/32.988498) | The algorithm behind reducers and shrinkers | paper | n/a | research (foundational) | https://www.st.cs.uni-saarland.de/papers/tse2002/ |
| perf + FlameGraph | Linux profiler and Brendan Gregg's flame-graph scripts; also `pprof` for Go | Locate hot spots; agents read the folded-stack text, not the SVG | CLI, folded text format | GPL-2.0 (perf) / CDDL (FlameGraph) | mature | https://github.com/brendangregg/FlameGraph |
| py-spy / Austin | Sampling profilers for Python producing flame graphs | Same for Python | CLI | MIT | mature | https://github.com/benfred/py-spy |
| Valgrind | Dynamic binary instrumentation: memcheck, callgrind | Memory-error oracle | CLI, XML output | GPL-2.0 | mature | https://valgrind.org/ |

**How agents consume them.** Three modes observed in open agent frameworks: (1) *shell-and-grep*, run the tool, grep its output (dominant); (2) *protocol client*, a DAP or GDB/MI client exposed as agent tools (`set_breakpoint`, `step`, `evaluate`), used in a few research agents; (3) *artefact-first*, the agent never runs the debugger interactively but reads a recorded artefact (rr trace, flame graph text, OTLP span JSON). Mode 3 fits hardware best because waveforms and simulation logs are already artefacts (see Gap G6 on DAP-for-waveforms).

**Hardware counterparts.** Waveform databases (FSDB, VCD, FST) plus viewer scripting (Verdi Tcl, GTKWave Tcl, Surfer) are the artefacts; simulator interactive debug (Tcl shells, UCLI) is the protocol; `rr` has a near-exact analogue in save/restore checkpoints and deterministic reseed. The missing piece is a *DAP-like adapter* over a simulator or waveform database, and structured crash-dedup for simulation failures (Gap G6).

## 6. Formal and symbolic

**What agents do with these.** Two loops. *Verification loop*: the agent writes a specification (contract, invariant, temporal property) and the tool proves or refutes it; a counterexample is a concrete test the agent can reason about. *Generation loop*: the agent uses a solver to generate inputs that reach a target (symbolic execution). Recent papers show LLMs can draft loop invariants, Dafny proofs, and TLA+ specs when the checker is in the loop, but that unguided LLM output is rarely correct on first try, so the checker is load-bearing.

| Tool | What | Agent use | Interface | License | Maturity | URL |
|---|---|---|---|---|---|---|
| Z3 | SMT solver (Microsoft Research); SMT-LIB 2 input, Python/C/Java/.NET APIs | The default solver behind most of the tools below; agents call it directly to check constraints or find models | library, CLI, SMT-LIB 2 | MIT | mature | https://github.com/Z3Prover/z3 |
| cvc5 | SMT solver with strong theory support (strings, sets, sequences) | Alternative solver; SyGuS support useful for synthesis | library, CLI, SMT-LIB 2 | BSD-3 | mature | https://github.com/cvc5/cvc5 |
| SMT-LIB standard | Input language and theories for SMT solvers | The interchange format; agents emit SMT-LIB text | text format | spec | standard | https://smt-lib.org/ |
| Bitwuzla / Boolector / Yices | Bit-vector-focused SMT solvers (relevant to RTL) | Solvers used by hardware formal back ends (e.g., SymbiYosys) | library, CLI | MIT / MIT / GPL | mature | https://github.com/bitwuzla/bitwuzla |
| CBMC | Bounded model checker for C/C++ (also JBMC for Java, Kani for Rust); checks assertions, memory safety, overflow | Agent writes `__CPROVER_assert` / proof harnesses; counterexample traces in JSON/XML | CLI, JSON/XML output | BSD-4-clause | mature | https://github.com/diffblue/cbmc |
| Kani | Rust bounded model checker on CBMC | Same for Rust; used in AWS Rust standard-library verification challenge | CLI (`cargo kani`) | MIT/Apache-2.0 | active | https://github.com/model-checking/kani |
| ESBMC | Another C/C++ bounded model checker; used in LLM-repair papers (ESBMC-AI) | Same; the ESBMC-AI work is one of the earliest "BMC in the LLM loop" results | CLI | BSD | mature | https://github.com/esbmc/esbmc |
| KLEE | Symbolic execution engine on LLVM IR; generates test cases that cover paths | Path-targeted test generation; test inputs come out as `.ktest` files | CLI | NCSA | mature | https://github.com/klee/klee |
| angr | Binary symbolic execution framework (Python) | Same at binary level | Python library | BSD-2 | mature | https://github.com/angr/angr |
| Dafny | Verification-aware language with Hoare-style contracts, checked by Z3, compiles to C#/Go/Java/JS/Python | Agents write code plus pre/postconditions and invariants; the verifier rejects wrong proofs; several papers on LLM-generated Dafny | CLI, LSP | MIT | mature | https://github.com/dafny-lang/dafny |
| Verus | Verified Rust (SMT-backed) | Same for Rust | CLI | MIT | active | https://github.com/verus-lang/verus |
| Lean 4 / Mathlib | Interactive theorem prover and library; the main target of LLM proof-generation research | Proof-search agents (see papers) | CLI, LSP, library | Apache-2.0 | active | https://github.com/leanprover/lean4 |
| TLA+ / TLC | Specification language for concurrent and distributed systems; TLC explicit-state model checker; PlusCal algorithm language | Agents write specs from prose designs; TLC finds traces; used at AWS, MongoDB, etc. | CLI (`tlc`), Toolbox IDE, VS Code extension | MIT | mature | https://github.com/tlaplus/tlaplus |
| Apalache | Symbolic (SMT-based) model checker for TLA+ | Bounded checking beyond TLC's state-space limits; typed TLA+ | CLI | Apache-2.0 | active | https://github.com/apalache-mc/apalache |
| Quint | Modern specification language that compiles to TLA+; JSON output, REPL | More LLM-friendly syntax than TLA+ | CLI, REPL | Apache-2.0 | active | https://github.com/informalsystems/quint |
| Alloy | Relational logic specification with bounded SAT-based analysis; visual instances | Lightweight structural models; counterexamples as instances | GUI, CLI, Java API | MIT | mature | https://github.com/AlloyTools/org.alloytools.alloy |
| P language | State-machine language with model checking and systematic testing (used at AWS) | Executable specs of protocols | CLI | MIT | active | https://github.com/p-org/P |
| SymbiYosys / Yosys formal | Open-source formal front end for Verilog with SystemVerilog assertions (SVA subset); drives SMT/SAT back ends | The open hardware formal path; direct counterpart to CBMC | CLI | ISC | mature | https://github.com/YosysHQ/sby |
| Frama-C / WP | C source verification with ACSL contracts | Contracts in C | CLI | LGPL-2.1 | mature | https://frama-c.com/ |
| SV-COMP | Annual software-verification competition and benchmark set | Benchmark for BMC/verifier tools | benchmarks | various | mature | https://sv-comp.sosy-lab.org/ |

### 6.1 Property checkers in the loop with LLMs (papers)

| Paper | What | Relevance | URL |
|---|---|---|---|
| Pei et al., "Can Large Language Models Reason about Program Invariants?" (ICML 2023) | LLMs predict loop invariants; evaluated against Daikon and checkers | Invariant drafting | https://proceedings.mlr.press/v202/pei23a.html |
| Kamath et al., "Finding Inductive Loop Invariants using Large Language Models" (2023) | LLM proposes invariants, Z3-based checker validates, loop repairs | Checker-in-the-loop pattern | https://arxiv.org/abs/2311.07948 |
| Sun et al., "Clover: Closed-Loop Verifiable Code Generation" (2023) | Dafny: consistency checks among code, docstring and annotations | Code + spec + proof consistency | https://arxiv.org/abs/2310.17807 |
| Misu et al., "Towards AI-Assisted Synthesis of Verified Dafny Methods" (FSE 2024) | LLMs generate Dafny methods with proofs; retrieval and feedback help | Dafny generation | https://arxiv.org/abs/2402.00247 |
| Charalambous et al., "A New Era in Software Security: Towards Self-Healing Software via LLMs and Formal Verification" (ESBMC-AI, 2023) | BMC finds a violation, LLM repairs, BMC re-checks | BMC-in-loop repair | https://arxiv.org/abs/2305.14752 |
| First et al., "Baldur: Whole-Proof Generation and Repair with LLMs" (FSE 2023) | Isabelle proof generation with repair loop | Proof generation | https://arxiv.org/abs/2303.04910 |
| Yang et al., "LeanDojo: Theorem Proving with Retrieval-Augmented Language Models" (NeurIPS 2023) | Lean environment for LLM proof search | Prover as an environment | https://arxiv.org/abs/2306.15626 |
| Wu et al., "Lemur: Integrating Large Language Models in Automated Program Verification" (ICLR 2024) | Calculus for combining LLM guesses with sound verifier steps | Soundness argument for LLM + verifier | https://arxiv.org/abs/2310.04870 |
| Yang et al., "AutoVerus: Automated Proof Generation for Rust Code" (2024) | LLM proof generation for Verus | Verified Rust | https://arxiv.org/abs/2409.13082 |
| "VerusBench"/"Alpha-Verus" family and Dafny benchmark "DafnyBench" (2024) | Benchmarks for LLM-written proofs | Evaluation | https://arxiv.org/abs/2406.08467 |
| Chakraborty et al., "Towards Neural Synthesis for SMT-Assisted Proof-Oriented Programming" (F*, 2024) | Large F* dataset and LLM proof synthesis | Proof-oriented programming | https://arxiv.org/abs/2405.01787 |
| Chen et al., "Fine-Tuning LLMs for Loop Invariant Generation" / "LLM-based Verification of Loop Invariants" (Wu et al., 2024) | Ranking LLM invariants to reduce verifier calls | Cost reduction | https://arxiv.org/abs/2310.09342 |

**Hardware counterparts.** The formal side is where hardware is closest to software. SVA plus a model checker (JasperGold, VC Formal, SymbiYosys) is the same loop as Dafny or CBMC. Papers on LLM-generated SVA (AssertLLM, FVEval, and others in the companion note) mirror the invariant-generation papers. The missing pieces are a machine-readable *counterexample format* (software BMC emits JSON traces; hardware tools emit waveforms) and open benchmarks of CBMC-benchmark scale for SVA (Gap G7).

## 7. Agent tool protocols and ecosystems

**What agents do with these.** This section is about the *plumbing* that lets an agent discover and call the tools in §§1–6 without bespoke glue. MCP standardises "here is a tool, here is its JSON schema, call it"; A2A standardises agent-to-agent delegation; AGENTS.md and the Agent Skills format standardise how a repository tells an agent what to do; sandboxing patterns constrain what a tool call may touch.

| Tool | What | Agent use | Interface | License | Maturity | URL |
|---|---|---|---|---|---|---|
| Model Context Protocol (MCP) specification | JSON-RPC protocol between an AI host and "servers" exposing tools, resources and prompts; stdio and streamable-HTTP transports; OAuth for remote servers | The dominant tool-integration protocol across agent products in 2025–26; governed since late 2025 under the Linux Foundation's Agentic AI Foundation (AAIF) | MCP (JSON-RPC) | MIT (spec and SDKs) | standard (active revision) | https://modelcontextprotocol.io/specification/latest |
| MCP specification repository | Source of the spec, schema (TypeScript/JSON Schema) | Schema is what SDK authors code against | JSON Schema | MIT | standard | https://github.com/modelcontextprotocol/modelcontextprotocol |
| Official MCP Registry | Community-run registry (API and CLI) for discovering MCP servers, with namespaced names and publisher verification | Agents or hosts discover and install servers | REST API | MIT | active (preview launched 2025-09) | https://github.com/modelcontextprotocol/registry |
| Agentic AI Foundation (Linux Foundation) | Neutral home for MCP, goose and AGENTS.md as founding projects (announced 2025-12-09) | Governance reference | web | n/a | active | https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation |
| MCP reference servers | Filesystem, git, memory, fetch, sequential-thinking, time, everything | Canonical examples; the `git` and `filesystem` servers are the ones most agents start from | MCP | MIT | active | https://github.com/modelcontextprotocol/servers |
| GitHub MCP server | Official GitHub server: issues, PRs, code search, Actions, code scanning | Agents act on GitHub without `gh` | MCP | MIT | active | https://github.com/github/github-mcp-server |
| Playwright MCP | Browser automation via accessibility tree snapshots rather than screenshots | Web UI testing and browsing for agents | MCP | Apache-2.0 | active | https://github.com/microsoft/playwright-mcp |
| Database MCP servers (e.g., Postgres) | SQL query and schema tools | Query logs/results databases | MCP | MIT | active | https://github.com/modelcontextprotocol/servers-archived |
| Serena (LSP-to-MCP) | See §1 | Semantic code tools over MCP | MCP | MIT | active | https://github.com/oraios/serena |
| MCP SDKs (Python, TypeScript, Java, C#, Kotlin, Rust, Go, Swift) | Official SDKs | Build a server around any CLI in tens of lines | libraries | MIT | active | https://github.com/modelcontextprotocol/python-sdk |
| MCP Inspector | Interactive tool for testing MCP servers | Debug a server before an agent uses it | web/CLI | MIT | active | https://github.com/modelcontextprotocol/inspector |
| Agent2Agent (A2A) protocol | Google-originated, now Linux Foundation, protocol for agent-to-agent task delegation: Agent Cards, tasks, streaming, push | Orchestrator delegates sub-tasks to specialist agents | JSON-RPC / HTTP | Apache-2.0 | active (2025) | https://github.com/a2aproject/A2A |
| A2A specification page | Spec text | Reference | web | Apache-2.0 | active | https://a2a-protocol.org/latest/specification/ |
| AGENTS.md | Convention originated by OpenAI (vendor): a Markdown file at repo root with build/test/style instructions for coding agents; adopted by many agents; contributed to AAIF in 2025-12 | Repo tells the agent how to work here | Markdown file | CC / MIT | active (2025) | https://agents.md/ |
| Agent Skills format | Open format: a directory with `SKILL.md` (YAML frontmatter: name, description) plus optional scripts and resources, loaded progressively | Packaged procedures an agent can invoke; portable across hosts | file format | Apache-2.0 (spec) | active (late 2025) | https://agentskills.io/ |
| Agent Skills spec repository | Spec and reference tooling | Reference | web | Apache-2.0 | active | https://github.com/agentskills/agentskills |
| OpenAI function-calling JSON Schema convention | Tools declared as JSON Schema; the de-facto schema shape MCP inherited | Baseline | JSON Schema | vendor (OpenAI) | mature | https://platform.openai.com/docs/guides/function-calling |
| llms.txt | Proposed convention: a Markdown file that gives LLMs a site or project map | Documentation discovery | file convention | CC | early | https://llmstxt.org/ |
| SWE-agent "Agent-Computer Interface" (paper) | Yang et al., NeurIPS 2024: designing the tool interface (file viewer with line windows, search, edit with lint check) matters as much as the model | Evidence for interface design | paper | MIT (code) | research | https://arxiv.org/abs/2405.15793 |
| OpenHands (ex-OpenDevin) | Open agent platform: sandboxed runtime (Docker), event-stream architecture, tools for bash/IPython/browser | Reference open implementation of an agent runtime | platform, API | MIT | active | https://github.com/All-Hands-AI/OpenHands |
| Aider | Open terminal coding agent; repo-map, lint/test hooks | Reference for lint/test-in-the-loop | CLI | Apache-2.0 | active | https://github.com/Aider-AI/aider |
| Goose (Block) | Open extensible agent; MCP-native | MCP host example | CLI, GUI | Apache-2.0 | active | https://github.com/block/goose |
| Cline / Roo Code / Continue | Open IDE agents with MCP support | Host examples | VS Code ext | Apache-2.0 | active | https://github.com/cline/cline |
| OpenAI Codex CLI | Open-source terminal agent (vendor) with sandboxing (macOS Seatbelt, Linux Landlock/seccomp) | Vendor example of sandbox policy in an agent | CLI | Apache-2.0 | active | https://github.com/openai/codex |
| LangGraph / smolagents / Pydantic AI | Agent orchestration frameworks with tool abstractions | Frameworks | libraries | MIT / Apache-2.0 | active | https://github.com/langchain-ai/langgraph |
| Tool sandboxing: MCP security guidance | Spec section on security/trust: user consent, tool-poisoning, confused-deputy | Threat model for tool servers | spec | MIT | active | https://modelcontextprotocol.io/specification/latest/basic/security_best_practices |
| Invariant Labs "tool poisoning" write-up | Independent disclosure of prompt-injection via MCP tool descriptions | Why tool descriptions need review | write-up | n/a | active | https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks |
| OWASP Top 10 for LLM Applications | Includes prompt injection, insecure tool/plugin design, excessive agency | Risk checklist | document | CC-BY-SA | active | https://owasp.org/www-project-top-10-for-large-language-model-applications/ |
| "Design Patterns for Securing LLM Agents against Prompt Injections" (Beurer-Kellner et al., 2025) | Six architectural patterns (action-selector, plan-then-execute, dual LLM, etc.) | Sandboxing patterns at the architecture level | paper | n/a | research | https://arxiv.org/abs/2506.08837 |
| CaMeL (Debenedetti et al., 2025) | Capability-based control flow to defeat prompt injection | Formal-ish sandboxing of agent data flow | paper | n/a | research | https://arxiv.org/abs/2503.18813 |

**Sandboxing patterns observed.** (1) *Allow-list of tools per task*; (2) *read-only vs. write tool split* with human approval for writes; (3) *OS sandbox around the shell tool* (Seatbelt, Landlock, gVisor, Firecracker, §4); (4) *network egress deny by default*; (5) *tool-description review* because descriptions are prompt-injection vectors; (6) *dual-LLM or plan-then-execute* so untrusted tool output cannot choose the next tool.

**Hardware counterparts.** Wrapping a simulator, a lint tool, a waveform reader or a regression database as an MCP server is mechanically trivial; what is missing are *agreed tool schemas* (what does `run_test` return?) and an AGENTS.md-style convention for a DV repo (Gap G8). Licence-server constraints make network-deny sandboxes awkward; commercial EULAs may forbid automated invocation in some cases (a policy gap, not a technical one).

## 8. Documentation and requirements as tools

**What agents do with these.** Documentation is input (the agent reads the spec) and output (the agent updates docs when it changes behaviour). The useful forms are the ones that are *machine-checkable*: an OpenAPI file can be validated and diffed; a requirements file with IDs can be traced to tests; an ADR has a fixed template the agent can fill. Docs-as-code toolchains make docs a build artefact with a CI gate, which is what lets an agent touch them safely.

| Tool | What | Agent use | Interface | License | Maturity | URL |
|---|---|---|---|---|---|---|
| Sphinx | Python-born docs generator; reStructuredText and MyST Markdown; autodoc; cross-references; `-W` warnings-as-errors | Build docs in CI; broken refs fail the build | CLI | BSD-2 | mature | https://github.com/sphinx-doc/sphinx |
| MkDocs (+ Material) | Markdown docs generator; `--strict` | Same, simpler | CLI | BSD-2 / MIT | mature | https://github.com/mkdocs/mkdocs |
| Docusaurus | React-based docs site generator | Same for JS ecosystems | CLI | MIT | mature | https://github.com/facebook/docusaurus |
| Quarto | Scientific/technical publishing (this book's toolchain) | Same, with executable code cells | CLI | MIT (CLI) / GPL-2.0 (some) | mature | https://github.com/quarto-dev/quarto-cli |
| Vale | Prose linter with style rules (Google, Microsoft styles) | Lint prose like code; CI gate on docs | CLI, JSON output | MIT | mature | https://github.com/errata-ai/vale |
| markdownlint / lychee | Markdown linter; link checker | CI gates on docs | CLI | MIT / MIT-Apache | mature | https://github.com/lycheeverse/lychee |
| Architecture Decision Records (ADR) | Nygard's format: context, decision, consequences; one file per decision | Agents propose and record decisions in a fixed template | Markdown convention | CC | mature | https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions |
| adr-tools | Shell scripts to create, number, supersede ADRs | Tooling for the above | CLI | MIT | mature | https://github.com/npryce/adr-tools |
| MADR | Markdown Any Decision Records template with fields | Structured ADR template | Markdown template | MIT | mature | https://adr.github.io/madr/ |
| log4brains | ADR site generator with timeline | Publish ADRs | CLI | MIT | mature (low activity) | https://github.com/thomvaill/log4brains |
| OpenAPI Specification 3.1 | Machine-readable HTTP API contract (paths, schemas, examples) | Agents generate clients, validate requests, diff API changes for breaking changes | YAML/JSON spec | Apache-2.0 | standard | https://github.com/OAI/OpenAPI-Specification |
| Spectral | OpenAPI/AsyncAPI linter with rulesets | Contract lint in CI | CLI | Apache-2.0 | mature | https://github.com/stoplightio/spectral |
| oasdiff | Breaking-change detection between OpenAPI versions | Gate: "does this PR break the API contract?" | CLI | Apache-2.0 | active | https://github.com/oasdiff/oasdiff |
| Schemathesis | Property-based testing of an API from its OpenAPI/GraphQL schema | Spec-derived stimulus (Hypothesis under the hood) | CLI | MIT | mature | https://github.com/schemathesis/schemathesis |
| Protocol Buffers / gRPC / buf | IDL contracts with `buf breaking` | Same for RPC | CLI | Apache-2.0 | mature | https://github.com/bufbuild/buf |
| JSON Schema | Schema language for JSON; the substrate of OpenAPI, MCP tool definitions, etc. | Validate any structured artefact | spec | BSD / CC | standard | https://json-schema.org/specification |
| AsyncAPI | Contract for event-driven/message APIs | Same for messaging | YAML spec | Apache-2.0 | mature | https://github.com/asyncapi/spec |
| StrictDoc | Text-based requirements tool (`.sdoc` files): requirement IDs, links, traceability matrix, export to HTML/ReqIF/Excel; requirement-to-source and test traceability | Agents edit requirements as text; CI builds a trace matrix | CLI, file format | Apache-2.0 | active | https://github.com/strictdoc-project/strictdoc |
| Doorstop | Requirements management in YAML files under version control; links, validation, publishing | Same, lighter | CLI, Python API | LGPL-3.0 | mature | https://github.com/doorstop-dev/doorstop |
| ReqIF (Requirements Interchange Format) | OMG standard XML for exchanging requirements between tools (DOORS, Polarion, etc.) | Interchange from enterprise RM tools into text-based tools | XML standard | OMG spec | standard | https://www.omg.org/spec/ReqIF/ |
| reqif (Python library) | Parser/writer for ReqIF (from the StrictDoc project) | Programmatic access | library | Apache-2.0 | active | https://github.com/strictdoc-project/reqif |
| sphinx-needs | Sphinx extension for requirements, specs, test cases with IDs, links and generated traceability tables | Requirements inside docs-as-code; used in safety-critical projects | Sphinx extension | MIT | mature | https://github.com/useblocks/sphinx-needs |
| OpenFastTrace | Requirement tracing across Markdown, code comments and tests; coverage of requirements by artefacts | Traceability checker in CI | CLI | GPL-3.0 | mature | https://github.com/itsallcode/openfasttrace |
| Gherkin / Cucumber | Executable specifications (Given/When/Then) bound to step definitions | Spec text that is also a test | text format, runners | MIT | mature | https://github.com/cucumber/gherkin |
| Doxygen / pdoc / JSDoc / rustdoc | API documentation from source comments | Keep docs and code together; agents update docstrings | CLI | GPL-2.0 / MIT etc. | mature | https://github.com/doxygen/doxygen |
| Diátaxis | Documentation framework: tutorials, how-to, reference, explanation | Where an agent-written doc should go | framework | CC-BY-SA | mature | https://diataxis.fr/ |

**Hardware counterparts.** Verification plans in spreadsheets are the direct analogue of requirements documents; OpenTitan's Hjson testplans (see the Ch. 2 note) are the closest thing to StrictDoc for DV. Interface specs (IP-XACT, SystemRDL for registers) play the role of OpenAPI, and SystemRDL tooling (PeakRDL) already generates RAL models and docs. The gap is a *lint and breaking-change diff* for those contracts, and a requirement-to-coverpoint trace checker as routine as OpenFastTrace (Gap G9).

## 9. Evaluation and quality gates

**What agents do with these.** Two layers. *Evaluation harnesses* measure whether an agent (or a model) can do a class of task; they define the environment, the task and the held-out oracle. *Quality gates* are what stop an individual agent change from merging: tests, coverage and mutation thresholds, review bots and human approvals encoded in repository policy.

| Tool | What | Agent use | Interface | License | Maturity | URL |
|---|---|---|---|---|---|---|
| SWE-bench | 2,294 real GitHub issues with held-out FAIL_TO_PASS / PASS_TO_PASS tests; Docker-based harness; Verified (500 human-validated) and Lite subsets | The reference structure: task = issue + repo snapshot, oracle = hidden tests | harness, dataset | MIT | active | https://github.com/SWE-bench/SWE-bench |
| SWE-bench paper | Jimenez et al., ICLR 2024 | Citation | paper | n/a | research | https://arxiv.org/abs/2310.06770 |
| SWE-bench Multimodal / Multilingual / Pro | Extensions to visual issues, other languages, harder tasks | Same | harness | MIT | active | https://github.com/SWE-bench/SWE-bench |
| SWE-Gym | Environments for training agents, not just evaluating | Training on executable tasks | dataset | MIT | research | https://github.com/SWE-Gym/SWE-Gym |
| SWE-smith | Synthesises many task instances per repo by breaking code and recording failing tests | Cheap generation of verified tasks (bug injection, the mutation-testing idea reused) | toolkit | MIT | research | https://github.com/SWE-bench/SWE-smith |
| Terminal-Bench | Tasks in a terminal sandbox with verifier scripts | Terminal-agent evaluation | harness | Apache-2.0 | active | https://github.com/laude-institute/terminal-bench |
| HumanEval / MBPP / LiveCodeBench | Function-level code generation benchmarks with hidden tests | Older baseline; LiveCodeBench avoids contamination with dated problems | dataset | MIT | mature | https://github.com/LiveCodeBench/LiveCodeBench |
| Aider polyglot benchmark | 225 Exercism problems across 6 languages, edit-format sensitive | Practical editing benchmark | harness | Apache-2.0 | active | https://github.com/Aider-AI/polyglot-benchmark |
| Inspect (UK AI Security Institute) | Framework for building LLM evaluations with sandboxed tool use | Build your own harness | Python library | MIT | active | https://github.com/UKGovernmentBEIS/inspect_ai |
| Held-out tests pattern | Tests the agent cannot see decide pass/fail; prevents "teaching to the test" | Core methodology; SWE-bench's FAIL_TO_PASS | pattern | n/a | standard practice | https://arxiv.org/abs/2310.06770 |
| Mutation-score gate (Stryker dashboard, PIT thresholds) | Fail CI if mutation score drops below threshold | Test-quality gate | CI config | Apache-2.0 | mature | https://stryker-mutator.io/docs/General/dashboard/ |
| Coverage gate (Codecov `threshold`, `diff-cover --fail-under`) | Fail CI if coverage on changed lines is below X | Coverage gate | CI config | various | mature | https://github.com/Bachmann1234/diff_cover |
| Danger | Scriptable PR-rule bot (e.g., "PR touches src but not tests") | Codified review rules | CLI, JS/Ruby | MIT | mature | https://github.com/danger/danger-js |
| reviewdog | Linter-to-review-comment bridge (see §2) | Lint as review | GitHub Action | MIT | mature | https://github.com/reviewdog/reviewdog |
| PR-Agent (Qodo, vendor) | Open-source LLM PR review/description/improve bot | Vendor example of an LLM review bot | GitHub App, CLI | AGPL-3.0 | active | https://github.com/qodo-ai/pr-agent |
| CodeRabbit (vendor) | Commercial LLM PR reviewer | Vendor example | GitHub App | vendor (proprietary) | active | https://www.coderabbit.ai/ |
| Sourcery / Codacy / SonarQube (vendors) | Static-analysis-driven review bots with quality gates | Vendor examples; SonarQube Community is LGPL | GitHub App, server | mixed | mature | https://github.com/SonarSource/sonarqube |
| CODEOWNERS | File mapping paths to required reviewers; enforced by branch protection | The human-gate routing table | file convention | vendor (GitHub/GitLab) | mature | https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners |
| Branch protection / rulesets | Required status checks, required reviews, signed commits, linear history | Policy that no agent can bypass | repository setting, REST API | vendor (GitHub) | mature | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches |
| Merge queues | Serialise merges and re-test against the up-to-date base (GitHub merge queue, Mergify, Bors-ng) | Keeps main green when many agents open PRs | vendor / OSS | Mergify vendor; bors-ng Apache-2.0 | mature | https://github.com/bors-ng/bors-ng |
| Sigstore / gitsign | Signed commits and artefacts, keyless with OIDC | Attribution of agent vs. human commits | CLI | Apache-2.0 | mature | https://github.com/sigstore/gitsign |
| SLSA | Supply-chain levels for build provenance | Provenance of agent-built artefacts | spec | Apache-2.0 | active | https://slsa.dev/ |
| OpenSSF Scorecard | Automated repo-hygiene checks (branch protection, CI tests, signed releases) | Audit that gates exist | CLI, GitHub Action | Apache-2.0 | mature | https://github.com/ossf/scorecard |
| DORA metrics | Deployment frequency, lead time, change-failure rate, time to restore | Outcome metrics for agent adoption; the 2025 DORA report on AI (vendor: Google) | framework | n/a | mature | https://dora.dev/ |

**Pattern: gate stack for agent PRs.** Formatter → lint (SARIF, changed-lines only) → type check → unit tests (JUnit XML) → coverage on diff → mutation score on diff (optional) → security scan → review bot → CODEOWNERS human review → merge queue re-test. Every layer is machine-readable except the human one, which is deliberate.

**Hardware counterparts.** Regression pass rate and coverage closure are the hardware gates, but they are rarely encoded as *repository policy* (branch protection with required regression status) and there is no SWE-bench-style open benchmark of DV tasks with held-out checkers of comparable scale (Gap G10; see the companion note for VerilogEval, CVDP and similar).

## 10. Gaps: what software has that hardware verification does not yet

The list is ordered by how much leverage a counterpart would give an agent, based on the reading above. Each gap names the software artefact and what the hardware equivalent would need.

| # | Software has | Hardware lacks | Nearest existing HW piece | Effort to close |
|---|---|---|---|---|
| G1 | Full-surface LSP servers (pyright, rust-analyzer, clangd): references, rename, code actions, semantic tokens, with LSP-to-MCP bridges | A SystemVerilog/UVM server with cross-file references, rename, and macro/class hierarchy awareness; open servers cover diagnostics and definitions only | verible-verilog-ls, svls, veridian, slang front end | medium; slang has the elaboration front end, the LSP surface is the work |
| G2 | SARIF as a universal findings format, consumed by CI, editors, diff tools | Any lint (Verible, Verilator, commercial lint, CDC/RDC) emitting SARIF; baseline diffing of RTL lint | Verilator `%Warning-RULE:` lines; Verible text | low; a converter is a weekend project, adoption is the hard part |
| G3 | Drop-in mutation testing (mutmut, PIT, Stryker) with incremental mode and per-mutant reports | An open RTL/UVM mutation tool with SystemVerilog mutation operators, sim-farm integration and a standard report | commercial Certitude; research prototypes | medium |
| G4 | Property-based testing with shrinking (Hypothesis) | Shrinking of constrained-random failures: minimal seed/transaction sequence that still fails | manual seed hunting; delta-debug scripts | medium; a delta-debugging wrapper around a sequence replayer |
| G5 | Hermetic build and test with content-addressed caching (Bazel, Nix, Remote Execution API) | Hermetic compile of RTL plus testbench with commercial simulators; cached compile artefacts; CI logs in JUnit XML/BEP | rules_hdl, rules_verilator, Slurm/LSF farms | medium; licensing and non-deterministic compile outputs are the obstacles |
| G6 | DAP: one debugging protocol across debuggers; rr record-replay; ClusterFuzz crash dedup | A DAP-like adapter over a simulator or waveform database; structured failure signatures for dedup across seeds | simulator Tcl/UCLI, checkpoints, Verdi scripting, FST readers | medium-high |
| G7 | BMC/verifier counterexamples as JSON traces; SV-COMP-scale open benchmarks | Machine-readable counterexample traces from formal tools (beyond waveforms); an open SVA property benchmark at scale | SymbiYosys `.vcd` traces; FVEval, AssertLLM datasets | low for traces; high for benchmarks |
| G8 | MCP servers plus agreed tool schemas; AGENTS.md convention | Agreed schemas for `run_regression`, `get_coverage`, `read_waveform`; an AGENTS.md convention for DV repos (how to compile, run one test, find the testplan) | ad-hoc Makefiles and `dvsim` in OpenTitan | low |
| G9 | OpenAPI + Spectral + oasdiff: contract lint and breaking-change diff; StrictDoc/OpenFastTrace requirement tracing | Breaking-change diff for IP-XACT/SystemRDL; routine requirement-to-coverpoint trace checking in CI | PeakRDL, OpenTitan Hjson testplans, UCIS | low-medium |
| G10 | SWE-bench-style task harnesses with held-out tests and per-task containers; SWE-smith synthetic tasks | An open DV-task benchmark: bug-injected RTL plus testbench, held-out checker, containerised open simulator | VerilogEval, CVDP, RTLLM (see companion note) | medium |
| G11 | Predictive test selection and flaky quarantine as CI features | Regression selection from RTL diff to affected tests; formal quarantine lists for known-flaky (seed-dependent) tests with owners and expiry | manual regression tiers | medium; data exists in regression databases |
| G12 | Coverage interchange (LCOV, Cobertura, LLVM JSON) read by any dashboard | Open UCIS readers/writers in wide use; coverage-on-diff reports | UCIS standard, vendor exports | low-medium |
| G13 | Agent-observability conventions (OpenTelemetry GenAI semantic conventions) | Any convention for logging agent actions in an EDA flow | none | low |
| G14 | Sandboxing with network-deny and OS isolation | Sandboxing that coexists with licence servers and NFS-mounted EDA installs | none documented | policy plus engineering |

## Confidence notes

- Every URL was checked with an HTTP fetch on 2026-09-07 (see verification log below). Repository licences were read from the repository's license file or README where possible; where a project has dual or changing licences (Earthly, Sentry, Elasticsearch) the note gives the licence at time of writing.
- Maturity labels are the author's judgement from release history and adoption, not a measured quantity.
- Claims about "what agents do" are drawn from open agent code bases (SWE-agent, OpenHands, Aider, Serena, Goose, OpenAI Codex CLI) and the cited papers; they describe observed practice, not a survey with counts.
- The MCP governance move to the Linux Foundation's Agentic AI Foundation and the MCP Registry preview are dated from the Linux Foundation and registry announcements; check dates before quoting in a chapter.
- The Comby, log4brains and Earthly projects have low recent activity; cite as historical if the chapter needs currency.
- Gap assessments for hardware tools (G1–G14) rely on the companion hardware note for the state of the SystemVerilog tools; where that note disagrees, it wins.

## Verification log (2026-09-07)

- 244 unique URLs extracted from this note and fetched with curl (browser user agent, 25 s timeout). 238 returned 200 on the first pass.
- Three DOI links (Yoo & Harman 2012, Luo et al. 2014, Zeller & Hildebrandt 2002) returned 403/202 from the publisher's bot filter at doi.org resolution; the DOIs are correct and the Zeller paper is linked to the authors' page instead. Cite the DOIs in `refs.bib`.
- `sourceware.org` (GDB/MI manual) and `valgrind.org` returned 403 to a browser user agent and 200 to curl's default agent; both are live.
- `github.com/sourcegraph/sourcegraph` returns 404: the repository was made private in 2024. Replaced with the public snapshot repository and relabelled as vendor.
- No AI-assistant-vendor URLs are cited. Vendor citations present and labelled: GitHub (CodeQL, code scanning, Actions, CODEOWNERS, branch protection), GitLab, Google (DORA, Launchable is separate), OpenAI (function-calling docs, Codex CLI repo), Pernosco, Undo, Launchable, CodeRabbit, Qodo, SonarSource, Sourcegraph, Codecov.
