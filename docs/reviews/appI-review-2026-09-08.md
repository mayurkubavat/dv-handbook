---
title: "Review: Appendix I, An Agent Tool Layer for RTL, UVM and Debug"
date: 2026-09-08
reviewer: independent technical review (fresh context, no drafting history)
chapter: appendices/appI-agent-tool-layer.qmd
evidence: research/agentic-dv-tools-synopsys.md, research/agentic-dv-tools-cadence.md, research/agentic-dv-tools-amiq-others.md, research/agentic-dv-tools-open.md, docs/specs/2026-09-07-agentic-tooling-catalog.md, refs.bib, tools/dvh/ (schema/, schema.py, cli.py, design.py, tests/test_ch03.py), examples/ch03-digital-design/dvh-tests/, .github/workflows/book.yml, _book/Design-Verification-draft.pdf, AGENTS.md
verdict: needs another draft pass
---

# Verdict

**Needs another draft pass.** The appendix is the strongest thing in the book on
how to read vendor evidence: the "How to read the numbers" Pitfall is correctly
sourced, correctly hedged, and does work no other page does. The catalogue is
concrete and the roles argument is the book's own. Three classes of problem
block author review.

First, the section that describes the book's own code makes three statements
the code does not support, and one of them is contradicted by the listing
spliced immediately above it. Second, the four-verdict triage claim — the
centerpiece of §I.4 and the justification for the whole retrofit — drops the
one qualifier the working document is explicit about, and two of its four rows
are not distinguishable from the evidence the section describes. Third, the
manual `I.n` section numbers are wrong in the shipped PDF, where they render on
top of Quarto's own numbering as "B.1. I.1 …" and, at the duplicated heading,
"B.7. I.6 Who may call what".

The vendor-claims sweep, which was the top priority, came back better than
expected: the Pitfall at line 230 does the hard work honestly and every figure
in it is attributed to a vendor channel. The residue is in the *prose around*
it — capability sentences in "The commercial tools" that state vendor
assertions as fact, and two dropped "up to"s.

The three most serious findings, in order:

1. **[C-1, line 205 against tools/dvh/schema/crossings.schema.json:33,40,60]
   "Every field carries a description written for a person" is false, and the
   counter-example is printed directly above the sentence.** The spliced
   listing shows `from_domain`, `to_domain` and `synchronized` with no
   `description`. Across the four schemas, twelve fields carry none
   (`connections`: `edges`, `from_port`, `to_port`, `nets`; `reset-tree`:
   `registers`, `kind`, `active`, `sources`, `through`). `STATUS.md` line 93
   records why: JSON has no line continuation, so descriptions were shortened
   to hold 80 columns. The claim is stale, and a reader can check it in four
   seconds.
2. **[T-5, lines 118–125 against docs/specs/2026-09-07-agentic-tooling-catalog.md:383]
   The four-verdict table promises a classification the join cannot produce.**
   Rows 1 and 3 are the same evidence pattern — observed ≠ expected — separated
   only by "X matches the specification", which is not in the log. The working
   document states the limit plainly: the classifier decides "whether the
   model's expectation matches the specification (a question it can only flag,
   not answer)". Line 125 nonetheless says the most expensive question in
   triage "is answered by a join over structured records", and line 187 has
   `log.classify_failure` returning "one of the four verdicts" from a lifecycle
   alone.
3. **[C-2, line 52 against tools/dvh/design.py:12] "an elaborated front end,
   slang in this book" — slang appears nowhere in the book's code.** `grep -r
   slang tools scripts examples .github` returns nothing; `design.py` builds
   both views from `yosys -p "… write_json"`. The book's design model is a
   flattened Yosys netlist, which is also why C-3 below bites.

The most *visible* defect is H-1: the appendix currently prints its own section
headings twice, with the wrong letter.

## 1. Vendor claims presented as results

The Pitfall at lines 230–240 is correct and should not be touched. Every finding
below is in the surrounding prose. All quotations checked against the four
notes' "Measured results" tables and "Confidence notes and gaps" sections.

| # | Location | Problem | Proposed fix |
|---|---|---|---|
| 1.1 | Line 218, opening sentence | "**Someone has shipped the layer this appendix describes.**" A capability judgment, in bold, resting entirely on a vendor product page and vendor documentation. Nobody in the evidence base has run it; the amiq note's §4 records "Nothing in this note is a measured result from a controlled study." | "AMIQ EDA's published tool list covers much of what @sec-appI-catalogue specifies." Keep the enthusiasm in the following sentence, which is already framed as a judgment ("worth knowing about before building anything"). |
| 1.2 | Line 218 | "AMIQ EDA's development environment has understood SystemVerilog and UVM semantically for years" — vendor claim, stated as fact, with no citation on the sentence and no date behind "for years". | Attribute and cite: "AMIQ states that its IDE compiles a project into a single database of the hierarchical design and verification environment, and that its UVM support includes class hierarchy and TLM port navigation [@amiq-dvt-ide]." That key already exists in `refs.bib` (line 1323) and is currently uncited. |
| 1.3 | Line 222 | "Its documentation generator derives documents from source without relying on comments [@amiq-specador]" — stated as a property of the tool. The note marks the whole Specador paragraph **[vendor]**. | "AMIQ states that Specador compiles the code and derives documents from project structure rather than from comments [@amiq-specador]." |
| 1.4 | Line 224 | "Cadence's verification platform is organized as applications over a shared data layer, including automatic triage, waveform comparison across runs, and regression debug [@cadence-verisium-pr-2022]." Present tense, no date, describing a product whose own pages could not be read. The cadence note's §7 is emphatic: every `cadence.com` URL returned 403, the Internet Archive was down, "no Verisium datasheet, no per-app product page and no Cadence blog post was read", and "a human should open the product pages in a browser and confirm before the appendix names them." | Date it and mark the channel: "As described at its 2022 launch, Cadence's verification platform is organized as applications over a shared data layer — triage, waveform analysis across runs, and debug among them; the description here is the launch release, republished, because Cadence's own pages were not retrievable [@cadence-verisium-pr-2022]." |
| 1.5 | Line 224 | "its simulator has applied machine learning to regression compaction since 2020 [@cadence-xcelium-ml-2020]" — a vendor claim about a capability, stated as fact. The mechanism qualifier is well handled ("compaction", not coverage improvement — this is the appendix at its best); the attribution is not. | "Cadence has described machine-learned regression compaction in its simulator since 2020 [@cadence-xcelium-ml-2020]." |
| 1.6 | Line 233 | "a tenfold reduction in coverage holes and a thirty percent productivity gain". Two qualifiers dropped. The source reads "up to 10x improvement in reducing functional coverage holes and up to 30% increase in **IP verification** productivity". The synopsys note's §7 names this figure first among those needing care. | "an *up to* tenfold improvement in reducing functional coverage holes and an *up to* thirty percent increase in IP verification productivity". The paragraph's whole point is provenance loss, so it must not itself shed the hedges. |
| 1.7 | Line 235 | "A 2026 announcement claimed a fiftyfold speedup to validated RTL." The announcement itself is uncited; only the critical trade report carries a key. A reader cannot get to the primary claim. | Add `[@synopsys-agentic-ai-page]` to the first sentence, keeping `[@uniteai-synopsys-agents-2026]` on the footnote sentence. |
| 1.8 | Line 220 | "no language server is claimed anywhere, which is worth recording as *not claimed* rather than as absent". The gap is well judged, but "anywhere" overstates the evidence: the note records "No LSP claim was found on **any AMIQ page fetched**" and files it as "not claimed where it would be expected". | "no language server is claimed on any page of its documentation read for this survey". |

## 2. Unsourced or wrongly sourced claims

**Citation keys: clean.** All 27 keys used by the appendix resolve to entries in
`refs.bib` (checked by set difference against the 172 keys in the file), and all
four `@sec-` targets exist (`sec-ch34`, `sec-ch02`, `sec-ch03-example`,
`sec-ch03-resets`). No page whose fetch failed in the notes is described:
nothing in the appendix describes a Cadence per-app page, a gated Synopsys white
paper, or the SNUG slides.

| # | Location | Problem | Proposed fix |
|---|---|---|---|
| 2.1 | Line 237 | "Searching the archived proceedings of the main verification conferences turns up no paper from either company reporting a measured result for these products." Stated as a completed result. Both notes forbid this shape: the cadence note says "**This should be treated as 'not found,' not as 'does not exist'**", records that the DVCon archive's full-text search is JavaScript-driven and its API route unavailable, and that CDNLive sits behind a Cadence login; the synopsys note records SNUG behind SolvNetPlus. As written the sentence is also unsourceable — the only record of the search is a `research/` note, which the book may not cite. | Make it a dated, scoped, first-person negative, which the book already does elsewhere (ch03 line 191, "As of September 2026 … counted from the list itself"): "As of September 2026 no paper reporting a measured result for these products could be found in the publicly indexed DVCon proceedings. That is a failure to find rather than a demonstration of absence: the archive's full-text search is partial, and SNUG and CDNLive proceedings sit behind vendor logins." |
| 2.2 | Line 145 | `rtl.compile_check` … "Verilator `--diagnostics-sarif`". A specific flag on a named tool, uncited. House rule: every claim about a tool has a source. | Cite `[@verilator-docs]` (already in `refs.bib`, line 8) on the sentence introducing the table, or add the citation in the cell. The open note quotes the flag and its SARIF description from the manual source, so the claim is safe — only the pointer is missing. |
| 2.3 | Lines 79, 84 | "These exist today as text in the reference implementation" and "UVM already prints the topology, the configuration database and the phase and objection traces." Behavior of a standard, uncited. `refs.bib` has no UVM or IEEE 1800.2 entry (`ieee1800-2023` is the SystemVerilog LRM). | Add a `refs.bib` entry for IEEE 1800.2-2020 or the Accellera UVM reference implementation, and cite it here. Naming the printing mechanisms (`uvm_top.print_topology()`, `uvm_config_db::dump()`, `+UVM_PHASE_TRACE`, `+UVM_OBJECTION_TRACE`) would also make the sentence actionable, which it currently is not. |
| 2.4 | Line 220 | "some operations are documented as available only to command-line clients and others only inside the graphical environment" — no citation on the sentence. It comes from the tool documentation. | Add `[@amiq-dvt-mcp-tools]`. |
| 2.5 | Line 246 | "slang provides a full front end with a Python binding" — uncited at the point of use. `@slang-docs` is cited only at line 52, four sections earlier. | Add `[@slang-docs]`. |
| 2.6 | Lines 260, 350 | `@agentic-coverage-limits` is called "a recent measurement" and "a study". The open note's §8 records that both 2026 agentic-coverage preprints are "not confirmed peer-reviewed". Since the paragraph's argument is about evidence quality, the distinction matters here more than usual. | "a recent preprint measuring where agentic coverage closure stops improving". |
| 2.7 | Lines 155–156, 176 | "SystemRDL tooling", "UCIS tooling" and "the specification repository" appear in the **Built on** column as if they were named, findable things. No note covers SystemRDL or UCIS, and neither appears anywhere in `refs.bib`. | Either name a concrete project and add a `refs.bib` entry (PeakRDL for SystemRDL; the Accellera UCIS standard for coverage interchange), or move these two rows' Built-on cells to "no open implementation surveyed" so the column stays honest. |
| 2.8 | Line 218 | "Its release notes run from January 2026 through August of the same year" — true on the access date, but the page is live and will drift. | "As of September 2026 its release notes run from January 2026 to August 2026 [@amiq-dvt-mcp-whatsnew]." The book already uses this construction in ch03. |

## 3. Claims about the book's own code

Verified by running the code, not by reading it: `conda run -n dvbook python -m
pytest tools/dvh/tests -q` → **14 passed**. `jsonschema` 4.26.0 is installed, so
`schema.validate` is really validating and not returning its
not-installed message.

**What checks out.** The three test kinds at line 336 are all really there:
behavior pins (`test_two_clock_domains`, `test_crossings_found_and_classified`,
…), an exact-text pin (`test_report_text_is_exactly_what_the_chapter_prints`),
and three regression fixtures kept as their own files
(`tools/dvh/tests/rtl/gated_clock.sv`, `mux_select.sv`, `per_bit_sync.sv`) with
a test each. Every schema really is versioned by URL, and a test enforces it:
`test_every_schema_is_versioned_by_url` asserts `$id` starts with `https://` and
ends `-1.json` for all four. `--validate` really exists on the CLI
(`tools/dvh/cli.py:76`). The negative test
(`test_the_schemas_reject_a_payload_that_is_wrong`) is real, not vacuous.
Both spliced files are within 80 columns (max 80 in each). The tests do run in
CI, through `examples/ch03-digital-design/dvh-tests/`.

| # | Location | Problem | Proposed fix |
|---|---|---|---|
| 3.1 (C-1) | Line 205 | "Every field carries a description written for a person, because a field name is not a definition." False for 12 of the fields, 3 of them in the listing spliced 3 lines above. See the top-three entry. | Either add the missing descriptions (12 short strings; the 80-column limit is real but `description` values can be split across JSON array-free multi-line strings only by shortening, so some will have to be terse), or change the sentence to what is true and interesting: "Every field whose name is not self-explanatory carries a description written for a person" — and then make sure `synchronized`, the one verdict field in the file, is among those that do. `synchronized` carrying no description is the worst case of the twelve. |
| 3.2 (C-2) | Line 52 | "slang in this book" — the book uses Yosys only. See the top-three entry. | "Use an elaborated front end — slang for a source-level tree, or, as this book's own tools do, the elaborated netlist Yosys writes as JSON — for anything that needs a parameter resolved, a generate unrolled or a connection bound [@slang-docs; @yosys-json]." Both keys exist in `refs.bib`. |
| 3.3 | Line 47 | "A tool's answer comes with a provenance a person can check: this cell, this net, this file and line." No schema carries a file or line field, and `tools/dvh/design.py` never reads Yosys's `src` attribute (`grep -n 'src\|attributes' tools/dvh/design.py` → nothing). The book's tools give cell and net names and nothing else. The same overpromise sits in the evidence-pointer Definition at line 289. | Say what the tools deliver and make the rest a build step: "this cell, this net — and, once the extractor carries Yosys's `src` attributes through, this file and line." Then add "carry `src` through into every schema" to the sequence at @sec-appI-building, where it belongs. |
| 3.4 | Line 207 | "the tests validate every command's output on every run". Four of the five CLI commands. `read` prints no JSON at all (`tools/dvh/cli.py:87–92` prints the human report and returns), has no entry in `schema.FOR_COMMAND`, and is not validated. `cli.py`'s own docstring line 15 ("Every command prints JSON") is wrong in the same way, which is presumably where the sentence came from. | "the tests validate the output of every command that prints JSON on every run". The `cli.py` docstring is worth fixing at the same time — outside this appendix's scope but the same error. |
| 3.5 | Line 205 | "the schema records what the tool *cannot* decide, in the same place a caller reads what it returns: this one says in its own text …". It says it in `$comment` (`crossings.schema.json:6`), which the JSON Schema specification reserves for notes from schema authors to readers and says implementations should not present to end users. `description` is the consumer-facing keyword. So the caveat is in the file but not in the place a caller reads. | Move the sign-off caveat into the top-level `description`: "Paths between clock domains, and how each was classified. Recognition is structural; neither verdict is a sign-off." Then the sentence is true as written. |
| 3.6 | Line 336 | "The book's own tool layer is checked on every commit." True for CI (`.github/workflows/book.yml:39` runs the whole checker). The pre-commit hook runs `scripts/check-examples.sh --changed`, whose `--changed` branch derives directories from `git diff --name-only HEAD -- examples`, so a commit touching only `tools/dvh` selects no directory and the tests do not run locally. | Low severity, and arguably a script fix rather than a prose fix. If the prose stays, "checked in continuous integration on every push" is exact. |

## 4. Dates and currency

| # | Location | Problem | Proposed fix |
|---|---|---|---|
| 4.1 | Line 250 | "For regression management as a machine-readable flow rather than a pile of scripts, OpenTitan's is public and in production use [@dvsim-tool]." The open note calls the move of dvsim "**the correction most likely to save a reader**": `util/dvsim/dvsim.py` in OpenTitan now 404s, and the tool lives at `lowRISC/dvsim`. The bib URL is right; the prose sends the reader to the old mental model. | "dvsim, the regression build-and-run system OpenTitan uses, is public and in production use; it now lives in its own repository rather than inside OpenTitan [@dvsim-tool], and the data it consumes — one `*_sim_cfg.hjson` per IP — is still in the OpenTitan tree [@opentitan-dv-methodology]." Both keys exist. |
| 4.2 | Line 248 | "an open viewer can be driven remotely, though its control protocol is not separately documented [@surfer-viewer]". The undocumented-protocol caveat is exactly right. The licence is not mentioned: Surfer is EUPL-1.2, and the open note singles it out as "worth flagging to readers, since it differs sharply from the permissive licenses elsewhere in this note". A team linking a viewer into an internal tool needs that before it starts, not from a general "check three things" callout. | "…driven remotely, under a copyleft licence (EUPL-1.2) unlike the permissive licences elsewhere in this list, and its control protocol is not separately documented [@surfer-viewer]." |
| 4.3 | Lines 258, 260, 253 | The In Practice callout tells the reader to check the licence, the last commit and whether a release was ever cut, and to "cite the paper" where a repository is stale — good advice, but it names no project, while the same paragraphs cite four repositories the note flags. `NVlabs/verilog-eval` has been dormant since 2025-02-07, `NVlabs/FVEval` since 2025-04-03. A reader cannot act on the rule without redoing the survey. | Name them once, where they are cited: "the standard benchmarks are of that shape [@verilogeval-revisited; @rtllm-bench], though only RTLLM's repository is still active — cite VerilogEval's paper, not its harness". The `refs.bib` notes on both keys already say this; the appendix is where a reader sees it. |
| 4.4 | Line 246 | "slang provides a full front end with a Python binding". True, but a reader who searches for that binding lands on `MikePopoloski/pyslang`, archived 2025-01-18. The note's instruction: "cite slang, install `pyslang` from PyPI, and never link the archived repository." | "…with a Python binding that ships from the same repository and installs from PyPI as `pyslang` [@slang-docs]." The `refs.bib` note on `slang-docs` already records the archiving; surface it. |
| 4.5 | Line 224 | Duplicate of 1.4 from the currency side: the Cadence app description is four years old and undated in the prose. | See 1.4. |

Dates that check out: AMIQ's January 2026 server (26.1.1, 2026-01-26; press
release 2026-01-27), the release-notes span through August 2026, the 2023
provenance of the 10x/30% pair, the 2026 date of the 50x announcement, and the
mid-2025 keynote framing at line 226, which is the appendix's cleanest piece of
dating.

## 5. Attribution and originality

No reproduced figure, table, code listing or dataset was found. The two
listings are the book's own files, spliced. The frame (three models, three
doors; the tool/agent split; the message signature; the roles matrix) is the
book's own and is not in any of the four notes.

| # | Location | Problem | Proposed fix |
|---|---|---|---|
| 5.1 | Line 218, last sentence | "The vendor states it can run inside the editor for live context or in batch to support fleets of agents." This tracks the source clause for clause — "run within DVT IDE to provide live project context to interactive AI assistants, or operate in batch mode to support fleets of AI agents in automated workflows" — and reuses its distinctive phrase, "fleets of … agents", without quotation marks. The sentence also carries no citation of its own. | Either quote the phrase with the citation on the same line — the vendor "states that it can run in batch mode to support 'fleets of AI agents' [@amiq-dvt-mcp-server]" — or rewrite from the fact: "the same server runs either attached to an editor session or headless, which is what makes it usable by more than one agent at a time [@amiq-dvt-mcp-server]." |
| 5.2 | Line 248 | "a thirty-four-tool server from an industrial research group". The `refs.bib` entry names Tencent Penglai Lab; the prose does not. The house rule is to credit named work to its authors. | "a thirty-four-tool server from Tencent's Penglai Lab verification team [@wave-mcp]". There is no reason to be coy: the tool count and the provenance are both from the project's own documentation. |

## 6. Technical errors and misleading simplifications

| # | Location | Problem | Proposed fix |
|---|---|---|---|
| 6.1 | Line 41 | "elaboration is precisely the act of resolving parameters, unrolling generates, binding connections and expanding macros". Macro expansion is the preprocessor's job and happens before parsing, not during elaboration. As written, the sentence tells a reader that a tool which elaborates necessarily expands macros, and that a tool which does not elaborate cannot. | "A full front end removes all four at once: the preprocessor expands the macros before anything is parsed, and elaboration then resolves parameters, unrolls generates and binds connections." |
| 6.2 | Line 39 | "A text search for `run_phase` finds the ones written by hand and none of the ones a macro generated." UVM's macros do not generate `run_phase`. `uvm_component_utils` generates type registration, `get_type_name` and the `type_id` proxy; `uvm_field_*` generate `do_copy`, `do_compare`, `do_print`, `do_pack`; the sequence macros generate `body` code at the call site. The point is right and the example is wrong. | Use a real one: "A text search for `do_compare` finds the ones written by hand and none of the ones `uvm_field_int` generated — and the generated ones are where a comparison silently includes a field nobody meant to compare." |
| 6.3 | Line 35 | "Searching for `u_sync` finds one line and misses the eight instances @sec-ch03-example had to name individually." Neither half holds. The eight-instance structure is `tools/dvh/tests/rtl/per_bit_sync.sv`, where the generate loop names them `g_sync[i].u`, not `u_sync`; the worked example's own design has a single `u_sync_en`. And nothing was named individually — ch03 line 249 says the tool "groups recognized synchronizers by the value they carry and rejects any group with more than one bit in it". | "Searching for a synchronizer instance name finds the one line of the generate loop, not the eight instances it produces — this book's own per-bit-synchronizer fixture names them `g_sync[0].u` through `g_sync[7].u`, and only the elaborated netlist knows that." Drop the "had to name individually" clause. |
| 6.4 | §I.2 heading and line 41 | The section is "What a syntax tree gives a model that text does not", and its worked contrast is the book's tool — which reads a *flattened netlist*, not a syntax tree. A Yosys netlist has resolved parameters and unrolled generates (so the section's argument survives) but has lost types, expressions and source locations (so the section's exemplar does not demonstrate what its title claims). Line 57's "nothing in a netlist distinguishes…" shows the draft knows the difference; the section body does not maintain it. | One sentence at line 41 or 45: "The book's own tools take the cheaper of the two roads: an elaborated netlist, which answers structural questions and has thrown the source-level tree away. A syntax-tree front end answers the same questions and also the ones about types, expressions and source locations." That also sets up C-3 honestly. |
| 6.5 (T-5) | Lines 118–125, 187 | The four verdicts are not four. See the top-three entry: rows 1 and 3 differ only by a specification judgment that is not in the log, and the working document says the tool "can only flag, not answer" it. | Make the table three verdicts plus one flag, and say what decides the fourth: rows 2 and 4 are decidable from the join (driven ≠ intended; driven and never observed). Rows 1 and 3 collapse into "the design and the reference model disagree — the specification decides which is wrong, and the tool's job is to hand a person both lines and the pointer". Then line 125 becomes true: the join *narrows* the most expensive question in triage from a log read to a two-way decision with the evidence attached, which is still worth the retrofit. Line 187's `log.classify_failure` returns "one of three verdicts, or the flag that a specification decision is needed". |
| 6.6 | Lines 63–65 | "Software has met this problem before, and the analogy is exact enough to be useful." The analogy is sound in shape and overstated in precision: a DI container is configured declaratively (annotations, XML, a module class), which is exactly why static extraction tools work on it. UVM's equivalents are not declarative — `uvm_config_db` keys are strings assembled at run time, factory overrides can arrive from the command line (`+uvm_set_type_override`), and sequence bodies are procedural. The UVM static walk is strictly harder than the DI case, which is worth saying because it is the reason the tool does not exist yet. | "The analogy is close, and where it breaks is the reason the tool is missing: a container is configured declaratively, which is what makes it statically extractable, while UVM's configuration is string keys computed at run time and overrides that can arrive on the command line. A static walk therefore reports what the source implies, and the run-time dump remains the ground truth — which is why the diff below is the valuable output rather than the tree alone." |
| 6.7 | Lines 268–274 | The roles table's fourth column is headed "Never" and its meaning is never declared. Read as access, it contradicts the neighboring cell twice over: Planner "may read … design" but "never … RTL"; Debug and Review "may read: everything" and "never: everything". Read as *never writes*, every row is correct but the column is redundant with "May write". It also inverts the working document, where every role may read RTL (`docs/specs/2026-09-07-agentic-tooling-catalog.md:27`). | Head the column **Never writes**, and set Debug and Review to "anything". Then drop "RTL" from the read side of the confusion by keeping the vocabulary constant: use "RTL" in both columns or "design" in both, not one each. |
| 6.8 | Line 95 and the table at 97–103 | Putting the transaction number in the UVM message ID makes every message's ID unique, which disables the only thing that field exists for: `set_report_id_verbosity`, `set_report_id_action` and `+uvm_set_verbosity` all match the ID, so a per-transaction ID means no per-ID verbosity or action control anywhere in the environment. | Keep role and stage in the ID (`DRV_DRIVE_END`, matchable and stable) and put `TXN=17` first in the message text, where the payload already is. If the draft prefers the current shape, state the trade-off in the In Practice callout at line 127 — a reader who retrofits this and loses ID filtering will not thank the appendix. |
| 6.9 | Lines 107–110 | The sample line is not what UVM prints. The default report format is `UVM_INFO <file>(<line>) @ <time>: <scope> [<id>] <message>`; the appendix has no `file(line)`, and writes `@1230ns:` where UVM writes `@ 1230:`. A reader who builds the parser of `log.uvm_parse` against this grammar writes a regex that fails on the first real log. | Show a real line, or label the block as a sketch of the grammar rather than of the output. If it becomes real output it must come from an example's `run.out` — see H-4. |
| 6.10 | Line 69 | "produce the component tree before anything runs" — a static walk cannot see `+uvm_set_type_override` / `+uvm_set_config_*` from the command line, or an override set from a value read at run time. The section's own remedy (the diff against the printed tree) covers this, but the promise is made before the limit is stated. | Add the clause where the promise is: "…apply the factory overrides visible in the source — command-line overrides are not — and produce the component tree the source implies." |

## 7. House-rule and template deviations

**Clean.** No `research/` or `docs/specs/` path is cited anywhere in the file
(`grep -n 'research/\|docs/specs'` → nothing): the rule added on 2026-09-07 is
satisfied. Only the six permitted callout kinds appear (Definition ×2, Pitfall
×4, In Practice ×3, Future Directions ×2), all with the right `title=`. No
hard-coded chapter, section, figure or table number appears in any
cross-reference. No AI-assistant or AI-vendor product name appears anywhere in
the file, including the clients the amiq note lists. Both included files are
within 80 columns. Every citation key resolves.

| # | Location | Problem | Proposed fix |
|---|---|---|---|
| 7.1 (H-1) | Lines 13, 29, 59, 87, 137, 212, 264, 284, 298, 316, 322 | Every `##` heading carries a manual `I.n` prefix, and Quarto numbers appendix sections itself. The shipped PDF (`_book/Design-Verification-draft.pdf`, from p. 142) therefore prints "B.1. I.1 The substrate: three models, three doors", "B.5. I.5 The tool catalogue", and — because `## I.6` appears twice (lines 212 and 264) — "B.6. I.6 What exists today" followed by "**B.7. I.6 Who may call what**". The letter is B, not I, because only two appendices are registered; the numbers are doubled either way. `appendices/appF-building-examples.qmd` carries no manual numbers. | Delete all eleven `I.n ` prefixes. That fixes the double numbering, the wrong letter and the duplicate in one edit, and matches appF. The `{#sec-appI-*}` labels are already the reference mechanism and need no change. |
| 7.2 | Line 253 | "the licence" and "no licence at all" — British, against the American-spelling rule. The book is 5 "license" to 2 "licence", and both "licence"s are here. | "license" twice. Also worth a pass on any new occurrences in the fixes proposed above (4.2 as written uses "licence" — use "license"). |
| 7.3 | Lines 26, 137, and the label `sec-appI-catalogue` | "catalogue" is the British-preferred form; the American is "catalog". The book is split 3 "catalogue" to 3 "catalog", and the ch34 review already ruled on this spelling (finding 6.4 there: "'catalogue' is British → 'catalog'"). | "catalog", and rename the label to `sec-appI-catalog`, updating the one internal reference at line 26. Cheap now, since nothing outside this file links it. |
| 7.4 | Lines 107–110 | A simulator-output block typed by hand. The house rule: "Simulator output shown in a chapter is included from the example's `run.out` … never typed by hand, so it cannot drift from what the code prints." appF has the same pattern, so this is a book-wide question rather than a private lapse, but this block is the one presented as a UVM log line and is also wrong (6.9). | Two acceptable outcomes. Either build the emitter as a small example under `examples/` — the appendix says at line 328 that it is days of work and at line 84 that a team "could have it this week", so the book saying so and then not shipping it is conspicuous — and splice its `run.out`. Or relabel the block explicitly as the grammar, not the output: "a line under this grammar reads", and drop the `UVM_INFO` prefix that makes it look like output. |
| 7.5 | Tables at 97, 118, 143, 162, 172, 182, 268 | Seven tables, none with a caption or a `#tbl-` label, so none can be cross-referenced; the prose falls back on position ("That table is the reason…", line 125). Not a rule violation as written, but it is the situation the label rule exists to prevent, and §I.4's two tables are the ones most likely to be referred to from ch28 later. | Caption and label at least the signature grammar and the verdict tables (`#tbl-appI-signature`, `#tbl-appI-verdicts`) and refer to them by label at line 125. |

Template: no "Learning objectives" callout, no Summary and no Exercises.
appF has none of the three either, so appendices are exempt by the book's own
precedent — recorded as a non-finding, but if the author wants the exemption
written down, AGENTS.md is where it belongs.

## 8. Clarity and structure

| # | Location | Problem | Proposed fix |
|---|---|---|---|
| 8.1 | Line 212 vs 264 | "What exists today" — a market survey — sits between the catalogue (§I.5) and the rest of the specification (roles, derived documentation, workflow, retrieval, build sequence). The specification is split in half by a section that will date faster than anything around it. | Move "What exists today" to just before "Further reading". The last line of §I.5 and the first line of the roles section join up cleanly, and the survey then sits next to the Further-reading paragraph that already frames it as "dated positions". |
| 8.2 | Lines 182–194 | The Debug table has no **Built on** column, though line 139 promises one for every entry and line 196 says this is where "the leverage is highest and the open tooling is thinnest". The evidence base names the source for three of these rows precisely: wave-mcp does "driver and fan-in analysis, backward value and X-root-cause tracing, pass/fail waveform diff". | Add the column: `wave.trace_driver`, `wave.trace_x`, `wave.first_divergence` → wave-mcp [@wave-mcp]; `wave.value` → wellen [@wellen-lib]; the `log.*` rows → this appendix's §I.4; `triage.bisect` → `git bisect`. It converts the strongest claim in the section from an assertion into a shopping list. |
| 8.3 | Line 224 | "The large vendors approach the same ground from the platform side" covers two of the three. Siemens is absent from the whole appendix, though the evidence base carries it in documentation-grade form: Questa One, an "Agentic Toolkit" for "agentic RTL sign-off", and a DAC 2026 agent inventory (coding, fuse, RTL, lint, CDC, planning, debug) with human-in-the-loop and LLM-agnostic framing. A reader surveying "what exists today" will notice the gap. | Two sentences after the Cadence one, with the vendor framing the notes require, and two new `refs.bib` entries (`siemens-questa-one`, `payne-2026-questa-one-dac`) built from the amiq-and-others note §2 and §5. Its "more than 17 AI-based capabilities" is a feature count, not a result, and must be presented as such if quoted at all. |
| 8.4 | Line 65 | "The tools that grew up around those frameworks are the model to copy" — no tool is named, so the reader cannot copy anything. | Name one and say what it does: a container-graph dumper that prints the resolved object graph and flags a binding nothing requests is the direct analogue of `tb.topology` plus `tb.config_db`. |
| 8.5 | Line 156 | `spec.section` "Built on: the specification repository" assumes the specification is text in a repository. For most readers it is a PDF or a Word document, which is the whole difficulty of that row. | State the assumption: "assumes the specification is text under version control; where it is a PDF this row is the gap, not the tool". |
| 8.6 | Lines 82, 84, 328, 339 | Four effort estimates — "weeks of work, not months", "a team could have it this week", "Days of work", "in a fortnight" — with nothing behind them. The book is careful about this elsewhere (ch03 line 49 marks Cummings' ninety-percent figure as "his expert judgment rather than a measurement"). | Mark them once, in the Future Directions callout at 338: "The effort estimates in this appendix are the author's judgment from building the design half, not measurements." Then they are usable. |
| 8.7 | Line 21 vs line 178 | The evidence model is introduced as answering "which coverage bins are hit", and `cov.holes_by_item` and `plan.report` are listed without qualification, but the working document records that the coverage half of the plan report is unbuilt. §I.10 step 5 lists the evidence model as still to come, so the appendix is internally consistent about the plan — only §I.1's present tense ("@sec-ch02 builds the first of it") oversells how much of it exists. | "…@sec-ch02 builds the test-evidence half of it; the coverage half is step 5 of @sec-appI-building." |

## 9. Verdict

**Needs another draft pass.** Blocking items, in the order they should be fixed:

1. **C-1 (3.1), C-2 (3.2), C-3 (3.3), 3.4 and 3.5 — the output-contract
   paragraph.** Five statements about the book's own code in ten lines, three of
   them false and one contradicted by the listing directly above it. This is the
   part of the appendix a reader can check most cheaply, so it is the part that
   costs most when it is wrong.
2. **T-5 (6.5) — the four verdicts.** The claim that a join answers the
   design-versus-testbench question drops the qualifier the working document
   states explicitly, and two of the four rows are not separable from log
   evidence. §I.4 is the appendix's best idea and this is the sentence that
   oversells it; three verdicts and a flag is both true and still impressive.
3. **H-1 (7.1) — the doubled section numbers.** Eleven manual `I.n` prefixes
   render on top of Quarto's own numbering, with the wrong letter, and `I.6`
   appears twice. One deletion pass fixes all three.
4. **1.6, 1.4, 2.1 — the vendor residue.** Restore "up to" and "IP
   verification" to the 10x/30% pair; date the Cadence description and say the
   source is a republished launch release because the vendor's pages could not
   be read; turn the conference-archive sentence into a dated, scoped negative.
   The Pitfall's whole authority depends on the prose around it holding the same
   standard.
5. **6.1, 6.2, 6.3 — three wrong examples in §I.2.** Macro expansion is not
   elaboration, UVM macros do not generate `run_phase`, and the eight
   synchronizer instances are named `g_sync[i].u` and were grouped, not
   enumerated. All three are in the section that argues the appendix's central
   technical point, and all three are the kind of error a verification engineer
   notices immediately.
6. **6.7 — the roles table's fourth column**, which contradicts its neighbor in
   five of five rows on the natural reading.
7. **7.2 and 7.4 — "licence" twice, and the hand-typed UVM line**, which is
   also not a UVM line (6.9).

After those, the pass should pick up the sourcing items (2.2–2.8), the currency
corrections (4.1–4.4, of which dvsim's move is the one most likely to waste a
reader's afternoon), the two attribution items (5.1, 5.2), and the structural
suggestions 8.1–8.3, which between them would make the survey age better and
give the Debug group the same actionable Built-on column every other group has.

**Counts.** 48 findings: vendor claims 8, sourcing 8, book's own code 6,
dates and currency 5, attribution 2, technical 10, house rules 5, structure 7 —
7 of them blocking. Verified clean and needing no action: every citation key
resolves, every `@sec-` target exists, no repository working document is cited,
only the six permitted callout kinds appear, no hard-coded numbers appear in
cross-references, both spliced listings are within 80 columns, no
AI-assistant product is named, the tool layer's 14 tests pass, all four schemas
are versioned by URL with a test enforcing it, and the three test kinds
described at line 336 are all really present.
