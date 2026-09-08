---
title: "Research note: AMIQ EDA and other vendors, AI tooling for RTL and DV"
date: 2026-09-07
author: research-agent
status: draft
feeds: Appendix on the agent tool layer
---

# AMIQ EDA and other vendors

Scope note. This note gathers primary-source evidence on tools that expose
*code comprehension* for SystemVerilog, VHDL, Verilog and `e` in a form a
program can consume, with AMIQ EDA treated first and at length. Everything
below was fetched from vendor sites, vendor product documentation, and trade
articles on 2026-09-07. Reachable and used: `eda.amiq.com` (product pages, the
press-release index, the documentation index, and the DVT MCP Server,
Verissimo and Specador user guides), `semiwiki.com`, Siemens'
`siemens.com/en-us/products/ic/questa-one/` and
`blogs.sw.siemens.com/verificationhorizons`, and `aldec.com/en/company/news`.
Unreachable, with no guess substituted: `www.consulting.amiq.com/papers/` and
`/knowledge-base/` (both HTTP 404), `eda.amiq.com/documentation/` (404; the
working index is `eda.amiq.com/docs/`), `aldec.com/en/company/press` and
`/press_releases` (both 404), and a guessed Siemens newsroom URL for the
Questa One launch (404). The Wayback Machine was tried for the AMIQ Consulting
papers index and could not be reached from this environment, so AMIQ's DVCon
paper list is a gap; see §6. Note that `dvteclipse.com` now 301-redirects to
`eda.amiq.com`, so older citations to the former should be updated.

## 1. AMIQ EDA: code comprehension as the substrate

AMIQ operates two divisions: AMIQ Consulting (2003) and AMIQ EDA (2008), the
latter selling DVT Eclipse IDE, DVT IDE for Visual Studio Code, DVT Debugger,
DVT MCP Server, Verissimo SystemVerilog Linter and Specador Documentation
Generator, across SystemVerilog, Verilog, VHDL, PSS and the `e` language
([AMIQ, accessed 2026-09-07](https://www.amiq.com/)) **[vendor]**.

### 1.1 DVT IDE: what it understands about SystemVerilog and UVM

The DVT product page states the IDE "performs on-the-fly incremental
compilation and highlights the errors in real time, as you type," and offers
"[c]ode and project navigation features such as hyperlinks, semantic search,
class and structural browsing (e.g. class hierarchy, design hierarchy)"
([AMIQ EDA, accessed 2026-09-07](https://eda.amiq.com/products/dvt-ide/))
**[vendor]**. On methodology awareness the same page states: "DVT IDE supports
SystemVerilog UVM, including features for navigating class hierarchies,
analyzing verification components and TLM port connections." Signal tracing
("[t]race a signal throughout your design"), macro expansion, quick fixes and
refactoring are listed alongside "dynamically created UML diagrams and design
diagrams." The VS Code edition carries the same claims
([AMIQ EDA, accessed 2026-09-07](https://eda.amiq.com/products/dvt-ide-for-visual-studio-code/))
**[vendor]**.

Two things matter for the appendix. First, the unit of understanding is a
*compiled, elaborated project database*, not a text index: AMIQ describes
connecting "code from hundreds or thousands of files into a single internal
database of the complete hierarchical design and verification environment"
([SemiWiki, 2026-02-12](https://semiwiki.com/eda/amiq-eda/366471-giving-ai-agents-access-to-a-compiled-design-and-verification-database/))
**[vendor]**, the article being written by AMIQ's Tom Anderson and quoting
AMIQ's Gabriel Busuioc. Second, **no LSP claim was found** on any AMIQ page
fetched; the programmatic surface AMIQ actually advertises is MCP (§1.4).

### 1.2 Verissimo: linting and machine-readable output

Verissimo offers a "[c]omprehensive library of both generic SystemVerilog and
UVM built-in checks," and "supports batch mode execution, allowing lint checks
to run from the command line," with an "API for creating new custom checks"
([AMIQ EDA, accessed 2026-09-07](https://eda.amiq.com/products/verissimo-linter/))
**[vendor]**. AMIQ does not publish a rule count on the product page; the rule
list is generated from the tool itself with
`$DVT_HOME/bin/verissimo.sh -gen_rulepool_doc`
([AMIQ EDA, accessed 2026-09-07](https://eda.amiq.com/documentation/verissimo/toc/available-rules/index.html))
**[vendor]**. The January 2026 release added "nearly fifty new rules"
([AMIQ EDA, 2026-01-27](https://eda.amiq.com/press-releases/amiq-eda-gives-ai-agents-access-to-essential-design-and-verification-data))
**[vendor]** — an increment, not a total.

Machine-readable output is explicit and is the important fact here. The custom
report is driven by FreeMarker templates, and the documentation states "the
custom report template sets the format of the generated custom report which can
be any type of text file format: CSV, TXT, XML, JSON, etc." Predefined
templates include `FAILURES_JSON`, `CHECKS_JSON`, `FAILURES_XML`,
`WAIVED_FAILURES_CSV` and `AVAILABLE_CHECKS_CSV`, emitted via
`-gen_custom_report` / `-gen_custom_report_ftl` with `-custom_report_location`
([AMIQ EDA, accessed 2026-09-07](https://eda.amiq.com/documentation/verissimo/toc/custom-report/index.html))
**[vendor]**. So Verissimo is scriptable end to end: batch invocation in, JSON
or XML out.

### 1.3 Specador: derived documentation

Specador is relevant to the appendix's derived-documentation section precisely
because it does not depend on the source being commented. AMIQ states the tool
"compiles the code and understands the project structure," producing
"cross-linked class inheritance trees, design hierarchies, and diagrams" even
where comments are absent
([AMIQ EDA, accessed 2026-09-07](https://eda.amiq.com/products/specador-documentation-generator/))
**[vendor]**. Diagram kinds claimed: block and schematic diagrams with
hyperlinked elements, UML class inheritance and collaboration diagrams,
bitfield diagrams "parsed from packed data types or UVM register
configurations," WaveDrom-format waveform diagrams, and custom diagrams via
external scripts. Output is HTML or PDF; comments may be written in Markdown or
reStructuredText; the tool runs in "batch mode (command line)."

### 1.4 AI features

AMIQ's AI work has a clear, datable arc, all of it vendor-announced:

- **2024-10-15**, DVCon Europe, Munich: AI Assistant added to DVT Eclipse IDE
  and DVT IDE for VS Code, backed by OpenAI, GitHub Copilot, Google AI, locally
  hosted Ollama, or in-house proprietary models, with user preview of all LLM
  traffic before transmission. CEO Cristian Amitroaie: "The power of LLMs,
  combined with the DVT IDE ability to help users compose more efficient
  requests and incrementally analyze code changes, provides our users with more
  options for understanding, debugging, and writing code."
  ([AMIQ EDA, 2024-10-15](https://eda.amiq.com/press-releases/amiq-eda-adds-ai-assistant-to-flagship-products))
  **[vendor]**
- **2025-06-17**, DAC: AI Assistant "leverages the knowledge contained in the
  IDE design and verification database."
  ([AMIQ EDA, 2025-06-17](https://eda.amiq.com/press-releases/amiq-eda-to-showcase-ai-and-new-product-features-at-dac-in-san-francisco))
  **[vendor]**
- **2025-10-14**, DVCon Europe: AI Assistant extended to waveform analysis and
  documentation generation.
  ([AMIQ EDA, 2025-10-14](https://eda.amiq.com/press-releases/amiq-eda-to-highlight-additional-ai-based-capabilities-at-dvcon-europe-in-munich))
  **[vendor]**
- **2026-01-27**, Santa Clara: DVT MCP Server announced, giving AI agents
  "access to a complete compiled database of design and verification knowledge
  for semiconductor projects."
  ([AMIQ EDA, 2026-01-27](https://eda.amiq.com/press-releases/amiq-eda-gives-ai-agents-access-to-essential-design-and-verification-data))
  **[vendor]**
- **2026-07-27**, Long Beach: debug and root-cause analysis steps automated
  through the AI Assistant.
  ([AMIQ EDA, 2026-07-27](https://eda.amiq.com/press-releases/amiq-eda-integrates-code-development-and-debug-with-ai-assistance))
  **[vendor]**

**DVT MCP Server is the answer to the appendix's central question.** AMIQ
describes it as "a tools server that supports Verilog, SystemVerilog, VHDL, and
the e language, enabling AI agents and LLM-based code generators to understand,
modify, and debug real-world design and verification projects efficiently and
accurately," "[f]ully compliant with the Model Context Protocol (MCP)
standard," and able to "run within DVT IDE to provide live project context to
interactive AI assistants, or operate in batch mode to support fleets of AI
agents in automated workflows"
([AMIQ EDA, accessed 2026-09-07](https://eda.amiq.com/products/dvt-mcp-server/);
[SemiWiki, 2026-02-12](https://semiwiki.com/eda/amiq-eda/366471-giving-ai-agents-access-to-a-compiled-design-and-verification-database/))
**[vendor]**. Clients named in the user guide's integration pages: Claude Code
CLI, Codex CLI, Gemini CLI, GitHub Copilot CLI, OpenCode, Kiro CLI and Devin
CLI
([AMIQ EDA, accessed 2026-09-07](https://eda.amiq.com/documentation/mcp-server/index.html))
**[vendor]**.

The tool list is documented and is the concrete evidence the appendix needs.
Thirty-nine tools are listed; representative names and descriptions, quoted
from the docs
([AMIQ EDA, accessed 2026-09-07](https://eda.amiq.com/documentation/mcp-server/toc/tools/index.html))
**[vendor]**:

| Tool | Documented description |
| --- | --- |
| `dvt_get_symbol_definitions` | "Retrieves the full source code definitions of symbols (e.g., classes, modules, interfaces)." |
| `dvt_get_symbol_references` | "Retrieves all usages of a symbol across the project." |
| `dvt_get_symbol_dependencies` | "Retrieves source code definitions of all symbols that a given symbol depends on." |
| `dvt_search_design_hierarchy` | "Retrieves elaborated design hierarchy paths of design instances that match specific filters." |
| `dvt_search_verification_hierarchy` | searches verification components matching filters in the hierarchy |
| `dvt_get_problems` | "Retrieves compilation problems (errors/warnings) for a given list of files." |
| `dvt_get_linting_failures` | "Retrieves linting failures reported by the Verissimo linter for a given list of files." |
| `dvt_get_field_constraints` | "Retrieves the constraints associated with a given random field." |
| `dvt_build_project` | "Performs a full DVT project build, retrieving up-to-date information about possible compilation problems." |
| `dvt_get_simulation_log_messages` | "Retrieves a list of log messages matching specific filters from a simulation log." |
| `dvt_waveform_get_signal_value_changes` | "Retrieves all value changes by time for a given signal from the loaded waveform dump file." |
| `dvt_start_runtime_elaboration` | "Starts the Runtime Elaboration for the SystemVerilog project currently loaded in DVT MCP." |
| `dvt_debugger_toggle_breakpoint` | toggles a breakpoint, watchpoint or tracepoint in the project |

Also documented: `dvt_get_symbol_locations`, `dvt_get_identifier_references`,
`dvt_get_identifier_info`, `dvt_get_compiled_files`, `dvt_get_design_top` /
`dvt_set_design_top`, `dvt_get_verification_top` / `dvt_set_verification_top`,
`dvt_get_file_identifiers`, `dvt_compile_changed_files`,
`dvt_get_cursor_scope`, `dvt_waveform_load_file`,
`dvt_waveform_search_signals_paths`, `dvt_stop_runtime_elaboration`,
`dvt_debugger_wait`, `dvt_debugger_step`,
`dvt_debugger_evaluate_expression`, `dvt_debugger_get_active_breakpoints`, and
a set restricted to the in-IDE assistant (`read_file`, `edit_file`,
`write_file`, `get_open_files`, `run_agent`, `bash`, `load_skill`, `think`).
Several tools are marked as available only to CLI agents or only to the DVT AI
Assistant and GUI agents, which is worth noting in the appendix: the surface is
not uniform across clients.

The server also ships two Agent Skills, installed with
`$DVT_HOME/bin/dvt_mcp.sh installSkills <installation path>`: `dvt-mcp`, which
"[i]nstructs agents on how to use the DVT MCP Server in an accurate and
efficient manner," and `dvt-root-cause-analysis`, which "[i]nstructs agents on
how to identify root causes of test failures by correlating simulation logs,
waveform analysis and source code"
([AMIQ EDA, accessed 2026-09-07](https://eda.amiq.com/documentation/mcp-server/toc/agent-skills/index.html))
**[vendor]**.

Release history is published and dated, which makes the pace citable: 26.1.1 on
2026-01-26 ("This is the first release of the DVT MCP Server"), then roughly
fortnightly increments to 26.1.18 on 2026-08-31; hierarchy search and
design/verification top tools arrived in 26.1.6 (2026-03-16), simulation log
messages in 26.1.13 (2026-06-22), UVM debugger and waveform tools plus the
root-cause-analysis skill in 26.1.15 (2026-07-21), and linting failures in
26.1.16 (2026-08-03)
([AMIQ EDA, accessed 2026-09-07](https://eda.amiq.com/documentation/mcp-server/toc/whats-new/index.html))
**[vendor]**.

## 2. Siemens EDA

Siemens describes Questa One as "the Siemens EDA smart verification solution
powered by AI, purpose-built to address productivity gaps caused by increasing
design complexities of 3DIC and chiplet-based architectures," and states it
"synergistically integrates the power of tools, technologies and products by
offering over one dozen new products and more than 17 generative, analytic, and
prescriptive AI-based capabilities across simulation and debug, design
creation, static, formal and verification intellectual property (IP)"
([Siemens, accessed 2026-09-07](https://www.siemens.com/en-us/products/ic/questa-one/))
**[vendor]**. The page introduces a "Questa One Agentic Toolkit" for "agentic
RTL sign-off." No Verification IQ branding appeared on the page fetched; that
name may have been folded into Questa One, and the appendix should not assert
otherwise without a further source.

Trade coverage of DAC 2026 names the toolkit's parts — Agentic ToolKit (ATK), a
Coding Agent, a Fuse Agent, and specialized agents for RTL code, lint, CDC,
verification planning and debug — and reports Siemens' Abhi Kolpekwar (VP and
GM, Digital Verification Technologies) saying that with Tessent, "DFT
simulations that used to run for weeks are slimmed down to just days." The same
report notes a "human in the loop approach" and an "LLM-agnostic" methodology
([SemiWiki, 2026-08-20](https://semiwiki.com/eda/372370-questa-one-updated-at-dac-2026/))
**[vendor]** — trade press relaying a vendor briefing, not an independent
measurement.

Siemens' verification chief scientist Harry Foster has published on agentic AI
as a role change rather than a tool change: "The HDL revolution scaled what
specialists could build. The AI revolution is redefining who gets to build"
([Siemens Verification Horizons, 2026-08-31](https://blogs.sw.siemens.com/verificationhorizons/2026/08/31/why-agentic-ai-could-redefine-the-future-of-design-and-verification/))
**[vendor]**. The post carries no survey data; it is opinion, and citable only
as such.

## 3. Other vendors

**Aldec.** The reachable Aldec newsroom shows no AI or LLM claim. Its most
recent listed item is "ALINT-PRO™ Adds New Mixed-Language Design Rules for More
Predictable Cross-Language Integration"
([Aldec, 2026-01-14](https://www.aldec.com/en/company/news/2026-01-14/475))
**[vendor]**, and the earlier items concern UVM generation in Riviera-PRO,
DO-254 flows, and prototyping boards
([Aldec, accessed 2026-09-07](https://www.aldec.com/en/company/news))
**[vendor]**. Aldec's dedicated press URLs 404 (§scope note), so absence of an
AI claim here is weak evidence, not proof. Useful to the appendix as a
contrast: a linter vendor still shipping rule packs rather than agents.

**Industry framing.** Panel coverage from DAC 2026 reports a move to "agentic
workflows capable of performing complex, multi-step tasks" with productivity
gains of "approximately 50%"
([SemiWiki, 2026-09-02](https://semiwiki.com/eda/llmda-ai/372271-dac-2026-a-discussion-of-who-owns-the-intelligence-behind-tomorrows-chips-and-how-to-make-it-better/))
**[vendor]**. That 50% is a panel assertion with no published method behind it
and should not be repeated as a result.

## 4. Measured results, as distinct from claims

| Claim | Figure | Who says it | Venue | Vendor or measured |
| --- | --- | --- | --- | --- |
| Verissimo rule additions in the 2026.1 release | "nearly fifty new rules" | AMIQ EDA | Own press release, 2026-01-27 | Vendor claim |
| DVT MCP Server tool surface | 39 tools documented | AMIQ EDA | Own product documentation, accessed 2026-09-07 | Vendor documentation; verifiable by inspection of a licensed install |
| DVT MCP Server release cadence | 18 releases, 2026-01-26 to 2026-08-31 | AMIQ EDA | Own "What's New" page | Vendor documentation, dated |
| Grounding agents in a compiled database reduces invalid output | No figure given | AMIQ EDA | Product page and SemiWiki, 2026-02-12 | Vendor claim, unquantified |
| Questa One AI capability count | "over one dozen new products and more than 17 generative, analytic, and prescriptive AI-based capabilities" | Siemens EDA | Own product page | Vendor claim (a count of features, not a result) |
| DFT simulation runtime | "weeks … slimmed down to just days" | Abhi Kolpekwar, Siemens EDA | SemiWiki report of DAC 2026 briefing, 2026-08-20 | Vendor claim relayed by trade press; no benchmark, no baseline |
| Agentic workflow productivity | "approximately 50%" | DAC 2026 panelists | SemiWiki, 2026-09-02 | Panel assertion; no method |

**Nothing in this note is a measured result from a controlled study.** No
peer-reviewed or preprint source was located for any of these tools within this
note's scope. If the appendix needs a **[research]**-grade number, it must come
from elsewhere.

## 5. Suggested BibTeX entries

| Key | Citation | Supports |
| --- | --- | --- |
| `amiq-dvt-ide` | AMIQ EDA. "DVT IDE." Product page. https://eda.amiq.com/products/dvt-ide/ (accessed 2026-09-07). | Incremental compilation, semantic search, UVM class/TLM navigation, signal tracing, refactoring |
| `amiq-dvt-mcp-server` | AMIQ EDA. "DVT MCP Server." Product page. https://eda.amiq.com/products/dvt-mcp-server/ (accessed 2026-09-07). | MCP compliance; in-IDE and batch operation; agent fleets |
| `amiq-dvt-mcp-tools` | AMIQ EDA. "DVT MCP Server User Guide: Tools." https://eda.amiq.com/documentation/mcp-server/toc/tools/index.html (accessed 2026-09-07). | The 39-tool list; per-tool names and descriptions |
| `amiq-dvt-mcp-whatsnew` | AMIQ EDA. "DVT MCP Server: What's New." https://eda.amiq.com/documentation/mcp-server/toc/whats-new/index.html (accessed 2026-09-07). | Version 26.1.1 (2026-01-26) through 26.1.18 (2026-08-31) |
| `amiq-mcp-pr-2026` | AMIQ EDA. "AMIQ EDA Gives AI Agents Access to Essential Design and Verification Data." Press release, Santa Clara, CA, 2026-01-27. https://eda.amiq.com/press-releases/amiq-eda-gives-ai-agents-access-to-essential-design-and-verification-data | Announcement date; Amitroaie quote; "nearly fifty new rules" |
| `amiq-ai-assistant-2024` | AMIQ EDA. "AMIQ EDA Adds AI Assistant to Flagship Products." Press release, Munich, 2024-10-15. https://eda.amiq.com/press-releases/amiq-eda-adds-ai-assistant-to-flagship-products | First AI Assistant release; provider list; IP-preview policy |
| `amiq-verissimo` | AMIQ EDA. "Verissimo SystemVerilog Linter." Product page. https://eda.amiq.com/products/verissimo-linter/ (accessed 2026-09-07). | UVM checks, batch mode, custom-check API |
| `amiq-verissimo-custom-report` | AMIQ EDA. "Verissimo User Guide: Custom Report." https://eda.amiq.com/documentation/verissimo/toc/custom-report/index.html (accessed 2026-09-07). | JSON/XML/CSV output; `-gen_custom_report` flags |
| `amiq-specador` | AMIQ EDA. "Specador Documentation Generator." Product page. https://eda.amiq.com/products/specador-documentation-generator/ (accessed 2026-09-07). | Documentation derived without comments; diagram kinds; HTML/PDF; batch mode |
| `anderson-2026-compiled-db` | Anderson, Tom. "Giving AI Agents Access to a Compiled Design and Verification Database." SemiWiki, 2026-02-12. https://semiwiki.com/eda/amiq-eda/366471-giving-ai-agents-access-to-a-compiled-design-and-verification-database/ | The compiled-database framing; error-feedback-to-agent loop |
| `siemens-questa-one` | Siemens EDA. "Questa One." Product page. https://www.siemens.com/en-us/products/ic/questa-one/ (accessed 2026-09-07). | AI capability counts; Agentic Toolkit; agentic RTL sign-off |
| `payne-2026-questa-one-dac` | Payne, Daniel. "Questa One Updated at DAC 2026." SemiWiki, 2026-08-20. https://semiwiki.com/eda/372370-questa-one-updated-at-dac-2026/ | Agent inventory; human-in-the-loop; LLM-agnostic; DFT runtime claim |
| `foster-2026-agentic` | Foster, Harry. "Why Agentic AI Could Redefine the Future of Design and Verification." Siemens Verification Horizons blog, 2026-08-31. https://blogs.sw.siemens.com/verificationhorizons/2026/08/31/why-agentic-ai-could-redefine-the-future-of-design-and-verification/ | Role-change framing; the "Design & Verification Scientist" idea |
| `aldec-alint-pro-2026` | Aldec. "ALINT-PRO Adds New Mixed-Language Design Rules for More Predictable Cross-Language Integration." 2026-01-14. https://www.aldec.com/en/company/news/2026-01-14/475 | Contrast case: linting vendor with no announced AI layer |

## 6. Confidence notes and gaps

- **High confidence, documentation-grade.** The DVT MCP Server tool list, its
  client list, its Agent Skills, its dated release history, and Verissimo's
  JSON/XML/CSV custom reports. These are product documentation, not marketing
  copy, and are checkable against a licensed install.
- **Vendor claim only, do not state as fact.** Everything in §4's table.
  Siemens' "17 AI-based capabilities" counts features; "weeks to days" has no
  published baseline; the "50%" is panel talk.
- **Gaps.** (a) AMIQ's DVCon paper list could not be retrieved — both AMIQ
  Consulting paper indexes 404 and the Wayback Machine was unreachable from
  this environment; `eda.amiq.com/articles` is the working index and lists
  SemiWiki and Electronic Design pieces rather than conference papers, so an
  AMIQ DVCon citation still needs a `dvcon-proceedings.org` lookup. (b) Total
  Verissimo rule count is unpublished; only `-gen_rulepool_doc` yields it. (c)
  No Questa One launch press release with a dateline was located. (d) No LSP
  claim was found for DVT on any fetched page — record this as "not claimed
  where it would be expected," not as a confirmed absence. (e) No **[research]**
  source exists in this note; every entry is **[vendor]** or trade press
  relaying a vendor.
- **Central question, answered.** Yes. DVT MCP Server exposes AMIQ's compiled
  design and verification database to programs rather than to a human in an
  IDE, over a documented, standard protocol, with named tools for symbol
  definitions and references, elaborated design and UVM verification hierarchy
  search, compilation problems, Verissimo lint failures, randomization
  constraints, simulation-log queries, waveform value changes, and breakpoint
  control — and it runs in batch mode for agents with no IDE attached. Second,
  weaker but real: Verissimo alone is fully scriptable via batch invocation plus
  JSON/XML/CSV report templates, and Specador emits derived documentation from
  the command line, so useful machine-readable output predates the MCP layer.
