# Design Verification Textbook — Project Design

**Status:** DRAFT — all six sections approved 2026-09-06; pending self-review and user review
**Date:** 2026-09-05
**Author:** Mayur Kubavat
**Title:** *Design Verification: From First Principles to Agentic AI*
**Repo (planned):** github.com/mayurkubavat/dv-handbook, rooted at `DV/Book`

## 1. Goal

A publishing-quality, open textbook for Design Verification (DV) engineers covering
the complete discipline — fundamentals through UVM, formal, emulation, portable
stimulus, alternative flows (cocotb, pyuvm, SystemC, UVM-SystemC), engineering
practice, and the future of verification including machine learning and
generative/agentic AI. Written in the spirit of Patterson-style teaching
textbooks, with UVM Golden Reference Manual-style reference appendices.

**Vision (author, 2026-11-15):** "a reference to DV/RTL engineers experimenting
new workflows, references, and innovating by merging fields of SWE, AI,
Silicon, Mathematics, etc." The book therefore names a fourth reader beside
the student, the working engineer and the lead: the engineer who experiments.
Software engineering, mathematics, silicon practice and machine learning are
parts of the discipline in this book, each with its own chapters, and every
technique is presented with what it has been measured to do.

## 2. Decisions (2026-09-05)

| Topic | Decision | Rationale |
|---|---|---|
| Toolchain | **Quarto** (`.qmd` chapters; PDF via installed MacTeX/TeX Live 2024; HTML site) | Single source → PDF + web + blog-ready HTML. Model: McKinney *Python for Data Analysis* 3e, Wickham *R4DS*. |
| Editor | VS Code + Quarto + LaTeX Workshop extensions (TeXShop as fallback; Gummi not viable on macOS) | |
| Style | **Teaching textbook** with GRM-style reference appendices | Career-spanning, serializable, exercises |
| Examples | **SystemVerilog/UVM primary**; cocotb, pyuvm, SystemC, UVM-SystemC and future tech as first-class secondary tracks. Book is language-open. | Matches industry, covers present + future DV tech |
| Example verification | Verilator (installed) for SV; conda env for cocotb/pyuvm; SystemC via Homebrew/source | Listings are `{{< include >}}`d from `examples/`, so printed code == CI-compiled code |
| Blog | **Companion posts** (announcements, excerpts, progress) on Blogger with PDF copy/link; chapters are *not* serialized in full | Reuses existing `format-blogger` command in `DV/.claude/commands/` |
| License | **CC BY-NC-SA 4.0** | Open, attribution, author keeps commercial print option |
| Hosting | **GitHub + GitHub Pages** (HTML) + **GitHub Releases** (PDF per version) | Standard for open books |
| Publishing | Free/open only | |
| Structure | **Monorepo** (approach A): text + examples + theme + blog drafts + CI in one repo | One commit == one version of text+code; cross-refs can't drift |
| Agent memory | `AGENTS.md` (stable) + `STATUS.md` (living zero-time memory) + `research/` | Survive across sessions/machines |

Rejected: pure LaTeX (blog conversion lossy), Pandoc+Markdown (rebuilds Quarto features),
AsciiDoc (publisher-oriented), Typst (too young), split repos (drift), folding into
non-git `DV/` agents tree (public book needs its own clean history).

## 3. Section 1 — Repo layout and agent memory (APPROVED)

```
DV/Book/                          ← git repo → github.com/mayurkubavat/dv-handbook
├── AGENTS.md                     # STABLE: conventions, commands, style rules; points to STATUS.md
├── STATUS.md                     # LIVING: zero-time memory (see 3.1)
├── research/                     # one file per topic: sources, spec refs, papers, links
│   ├── README.md                 #   index of research notes
│   └── <topic>.md
├── docs/
│   ├── specs/                    # this design doc
│   └── plans/                    # implementation plans, milestone plans
├── _quarto.yml                   # book config: parts, chapter order, output formats
├── index.qmd                     # preface
├── chapters/                     # one .qmd per chapter, numbered (ch01-what-is-dv.qmd)
├── appendices/                   # GRM-style reference appendices
├── examples/                     # runnable code, mirrored by chapter
│   └── chNN-<slug>/{sv,cocotb,pyuvm,systemc}/  each with Makefile
├── theme/                        # preamble.tex, tcolorbox styles, fonts, blog.css
├── blog/                         # companion-post drafts → format-blogger → Blogger HTML
├── scripts/                      # check-examples.sh, release.sh, new-chapter.sh
└── .github/workflows/            # render + check examples + deploy Pages + PDF release
```

### 3.1 Zero-time memory: `STATUS.md`

First file read in any session. Contents:
1. **Current milestone + next three actions**
2. **Chapter status table** — state ∈ {planned, outlined, drafting, examples-verified, reviewed, published}, word count, last-touched date
3. **Decisions log** — dated one-liners (never re-litigate)
4. **Research references** — pointers into `research/<topic>.md` with what each was used for
5. **Session log** — 2–3 lines per session: what changed, what's blocked

`AGENTS.md` rule: *read `STATUS.md` before doing anything; update it before ending a session.*
A Stop hook in the agent settings blocks ending a session while `STATUS.md` is untouched.
The assistant's private memory is for cross-project preferences only; the repo file is the source of truth.

## 4. Section 2 — Table of contents (APPROVED; revised 2026-11-15)

Seven parts, 36 chapters, appendices. Order = teaching arc. Each chapter is
independently draftable/verifiable/releasable. Revised on 2026-11-15 after the
second whole-book review (author: "lets implement all of these"): part numerals
and every written chapter keep their place; the unwritten chapters are
reorganized around the vision in section 1. The table of 2026-09-05 is in git
history.

### Part I · Foundations
1. What Is Design Verification? — cost of bugs, verification gap, DV in the silicon lifecycle
2. Verification Planning — spec → features → vPlan → coverage → sign-off criteria
3. Digital Design for Verifiers — RTL, clocks/resets, FSMs, pipelines, interfaces; verifier vs designer thinking
4. Simulation Fundamentals — event-driven scheduling, regions, races, delta cycles, and how far a real simulator implements the model (Verilator schedules statically and implements the Active and NBA regions only)

### Part II · SystemVerilog for Verification
5. The SystemVerilog Testbench Language — types, classes, interfaces, clocking blocks
6. Object-Oriented Testbench Design — inheritance, polymorphism, parameterization, patterns
7. Constrained-Random Stimulus — randomization, constraint solving, distributions
8. Functional Coverage — covergroups, crosses, coverage-model design, closure
9. Temporal Properties and Assertions — SVA from regular sequences and linear temporal logic; safety and liveness; vacuity; `bind`; the same property as a simulation checker and as a proof obligation (SymbiYosys); a Python monitor as the non-SVA mirror
10. Reference Models and the Foreign Boundary — DPI-C, VPI as cocotb uses it, SystemC or Python models as predictors, co-simulation pitfalls (interfaces and modports are already in Ch 5)
11. From Architecture to Verification: a DMA Case Study — architecture spec → microarchitecture → vPlan → testbench → coverage, on one DMA in two versions

### Part III · Testbench Architecture and Methodology
12. Testbench Architecture — components, phases, factory, configuration; UVM (IEEE 1800.2) shown beside pyuvm
13. Stimulus Architecture — sequences, sequencers, drivers, layering, virtual sequences; cocotb coroutines as the minimal form
14. Checking Architecture — monitors, scoreboards, predictors, analysis paths
15. Registers and Reuse — register models generated from a machine-readable spec, adapters, built-in tests; agent → VIP, block → SoC
16. One Design, Three Testbenches — the Ch 11 DMA in UVM, pyuvm and cocotb: same plan and coverage model, compared on lines, run time and what each could not express
(Advanced UVM — callbacks, objections, reporting, performance — becomes callouts in 12–15 and entries in Appendix B.)

### Part IV · Proof and Probability
17. Logic and Solvers for Verifiers — propositional logic, SAT, bit-vector SMT, BDDs, and-inverter graphs; what the engines under Ch 7 and Ch 18 do and why they blow up
18. Formal Property Verification — bounded model checking, k-induction, IC3/PDR at reading level, assumptions and over-constraint, covers and vacuity, on SymbiYosys
19. Equivalence, Structural and Static Verification — lint, CDC, RDC, X-propagation as static analyses; combinational and sequential equivalence; connectivity and register checks
20. The Statistics of Random Testing and Coverage — hit probability, coupon collector, bounds after N clean seeds, uniformity tests, t-way combinatorial coverage, estimating unseen coverage; information theory as a section
21. Graphs, Tours and Portable Stimulus — state graphs, transition tours, reachability; PSS as a graph-based stimulus standard

### Part V · Borrowed from Software
22. Property-Based Testing for Hardware — generators, properties, shrinking; Hypothesis driving cocotb
23. Fuzzing Hardware — coverage-guided and differential fuzzing on Verilator models; fuzz vs constrained-random measured
24. Mutation Testing: Qualifying the Testbench — fault models, equivalent mutants, kill rate beside coverage; MCY on the book's designs
25. Hardware Construction Languages and Compiler IRs — Chisel, Amaranth, SpinalHDL; FIRRTL, CIRCT/MLIR, RTLIL; verifying generators and generated RTL; HLS verification
26. Reproducible Verification: Build, Regression and CI — hermetic toolchains, seeds as inputs, regression as a build graph, flaky-test triage; the book's own CI as the example

### Part VI · Systems, Silicon and Sign-off
27. Processor Verification: a RISC-V Case Study — instruction-stream generation, lock-step co-simulation against an ISS, RVFI, ISA formal checks, Sail as the oracle
28. System-Level and Hardware-Assisted Verification — SystemC/TLM-2.0 virtual platforms, firmware co-verification, emulation and FPGA prototyping
29. Debug Methodology — waveform/transaction-level debug, triage, minimization, root cause
30. Metrics, Closure and Sign-off — coverage merging and ranking, bug-rate curves, the coverage database as a dataset
31. Gate-Level, Low-Power and Tapeout on an Open PDK — GLS and equivalence on a real open-PDK netlist, power intent, tapeout sign-off as a checklist
32. Post-Silicon Validation and Bring-Up — observability, reuse of pre-silicon assets, closing the loop to the plan (needs a research note first; may begin as a section of 31)
33. Safety and Security Verification — fault injection, ISO 26262 and DO-254 evidence, information-flow and security properties

### Part VII · Machines in the Loop
34. Machine Learning in Verification — coverage-directed generation, regression selection, failure clustering, each with a baseline
35. Experiments and Evaluation: Measuring a New Workflow — baseline, metric, seeds, cost, leakage, threats to validity; AI-for-hardware benchmarks; review and estimation practice; open questions in place of "The Road Ahead"
36. Generative AI and Agentic DV — LLM-assisted testbench/SVA generation, spec-to-vPlan, debug assistants, agentic flows, RAG over specs, risks and evaluation

**The generative-AI chapter closes the book** (author, 2026-09-08). Consequences
to honour: every new chapter is registered in `_quarto.yml` *before* it, never
after; its file keeps the name `ch34-...` for continuity of history, so file
name and chapter number differ here and nowhere else.

Dropped as standalone chapters on 2026-11-15: cocotb, pyuvm, SystemC and
UVM-SystemC, and the open-source ecosystem survey (absorbed into Chs 10, 12,
13, 16, 22, 28 and Appendix E); Advanced UVM (callouts and Appendix B);
Verifying Standard Protocols (APB and AXI are in Ch 11; a protocol-checker
catalogue becomes reference material); The DV Engineer's Craft and The Road
Ahead (merged into Ch 35).

### Appendices (GRM-style reference)
A. SV quick reference · B. UVM class/macro reference · C. SVA cheat sheet ·
D. UVM command-line/config reference · E. What runs where: the measured
support matrices of every chapter, generated in CI, with the cocotb/pyuvm API
pointers (revised 2026-11-15) ·
F. Tool setup (macOS/Linux) · G. Glossary · H. Selected exercise solutions ·
I. An agent tool layer and derived documentation for the book's examples (added 2026-09-07; see `docs/specs/2026-09-07-agentic-tooling-catalog.md`).
Plus bibliography and index.

### 4.1 Chapter template
learning objectives → motivation (real bug/story) → concepts → worked example
(runnable, from `examples/`) → "In Practice" / "Pitfall" callouts → future
directions → summary → exercises → further reading.

### 4.2 Phasing
~600–800 pages; 2–3 years at a sustainable pace. Revised 2026-11-15:
- **Edition 1 (v0.x → v1.0):** Parts I–II complete (Chs 9, 10), then Chs 17,
  18, 20, 22 and 24 — the chapters no other DV textbook has, all on the
  toolchain already in CI — plus appendices A, C, F, G and the preface maps.
  Writing order: 9, 17, 18, 20, 24, then 10.
- **Edition 2:** Part III, the rest of Parts IV and V, appendices B and E
- **Edition 3:** Parts VI–VII, appendices H, I
TOC is a plan, not a contract; `STATUS.md` tracks reality.

## 4a. Section 3 — Design style (APPROVED 2026-09-06)

- **Trim:** 7 × 10 in (178 × 254 mm); single column with wide outer margin for margin notes; appendices two-column (GRM density).
- **Fonts (OFL, XeLaTeX via Quarto):** body Source Serif 4; headings/tables/captions Source Sans 3; code JetBrains Mono (plain, not Nerd Font). Same faces on web via Google Fonts.
- **Colors:** silicon blue `#1B4F72` (headings, chapter numbers, links, cover); assertion amber `#B7791F` (pitfalls/warnings); coverage green `#2E7D32` (in-practice, verified marks); formal violet `#5B3E8E` (future directions, AI sidebars); text `#1C1C1C`; code ground `#F4F6F8`; rules `#CBD2D9`.
- **Callouts (6, identical in PDF/HTML):** Definition · In Practice · Pitfall · Future Directions · Worked Example · Exercise — left color bar, icon, bold label. Implemented as tcolorbox styles in `theme/` and Quarto callout classes.
- **Chapter opener:** oversized number, title, epigraph, boxed Learning Objectives, mini-TOC. Fixed closer: Summary → Exercises → Further reading.
- **Listings:** numbered per chapter ("Listing 7.3"), captioned, line numbers, language badge; source `{{< include >}}`d from `examples/`. Output/log excerpts in a distinct lighter style.
- **Figures:** WaveDrom (waveforms), Mermaid (flows/sequences), draw.io → SVG (architecture); sources in `figures/`.
- **Covers:** SVG sources in `theme/cover/` generated by `gen_cover.py`. Front: silicon-blue ground; motif = 7-lane valid/ready handshake (reset, 2-cycle stall, `$stable(data)` assertion window, 40 ns cursor) fanning into a coverage grid, over a git-branch → CI pipeline strip (lint/sim/cov/formal/release) as the software-engineering hint; title/subtitle/author, "Open edition · CC BY-NC-SA 4.0". Back: ~120-word blurb, five "inside" bullets, author bio, QR to web edition, license badge, version string.
- **Title (decided 2026-09-06):** *Design Verification: From First Principles to Agentic AI*. Rejected: "Verifying Silicon…", "The Design Verification Book…", "Modern Design Verification…" (dates badly).

## 4b. Section 4 — Example verification pipeline (APPROVED 2026-09-06)
- Every listing is a file under `examples/chNN-<slug>/<lang>/`, included via Quarto include shortcode (printed code == compiled code).
- One Makefile per example dir, fixed targets `lint`, `run`, `clean`. Tools: Verilator (SV), conda env (cocotb/pyuvm), Homebrew SystemC (SystemC/UVM-SystemC). `REQUIRES=commercial` marker → lint-only in CI, noted in listing caption.
- `scripts/check-examples.sh` walks examples, runs lint+run, writes JSON status consumed by CI and the `STATUS.md` chapter table; locally checks only dirs changed since last commit.
- Appendix F (tool setup) generated from the same environment file CI uses.
- Failure policy: chapter cannot reach `examples-verified` while any example fails.

## 4c. Section 5 — Blog companion and release flow (APPROVED 2026-09-06)
- Versioning: `v0.x` while Edition 1 incomplete (each minor adds ≥1 reviewed chapter); `v1.0` when Parts I–III + appendices reviewed.
- Release GitHub Action on tag: render PDF+HTML → run example checks → deploy HTML to Pages → attach PDF + changelog to Release. Nothing published from a laptop.
- Companion posts drafted in `blog/` (one per release + occasional excerpts) by a `book-blog-post` skill from changelog + chapter summaries, then `DV/.claude/commands/format-blogger.md` → Blogger HTML. Every post links web edition + release PDF and carries the version string.
- Feedback: GitHub Issues with chapter labels, linked from chapter footers and back-cover QR.

## 4d. Section 6 — Writing workflow and AI assistance (APPROVED 2026-09-06)
The book is written the way it says verification should be done: a spec, separated producer and judge, executed evidence, human gates. Grounded in `research/dv-adaptation-synthesis.md` §8.

**Per-chapter pipeline** (each step an agent skill in the repo's `.claude/skills/`):
1. `research-topic` → `research/<topic>.md` with citations.
2. `outline-chapter` → section outline per chapter template. **Human gate 1: outline approval.**
3. `draft-chapter` → prose + example code. May read `research/` and the design doc; a PreToolUse hook blocks it from editing them (generator/judge separation).
4. `verify-examples` → runs `scripts/check-examples.sh` for the chapter, records pass/fail JSON. Agent-related examples report pass^k over several runs.
5. `review-chapter` → fresh subagent, no drafting context; checks every number against a cited source, labels vendor claims, checks template + house style, writes findings. **Human gate 2: technical review.**
6. `book-blog-post` + `release` (see §4c). **Human gate 3: tagging a release.**

**Memory and rules.** `STATUS.md` chapter states advance only via these skills with evidence attached. `AGENTS.md` constitution: read STATUS first; citation format; no unsourced numbers; vendor claims labelled; examples must run; house style. Hooks: Stop hook flags unchanged `STATUS.md`; pre-commit hook runs example checks for touched chapters.

## 5. Pending design sections
- None. M1 (repo scaffold) started 2026-09-06 directly at the user's request: examples build system, Appendix F, Quarto skeleton and PDF build are done; AGENTS.md/hooks/skills, git+GitHub, CI remain.
- Decision 2026-09-07: the tool layer and documentation-agent material from the tooling catalogue becomes Appendix I, with three forward pointers from Ch.34; each individual tool is the worked example of the chapter that needs it (3, 8, 11, 12, 13, 20, 28, 30). Ch.34 stays conceptual.
- Implementation note: appendix lettering is forced with `\setcounter{chapter}{5}` in the PDF until appendices A–E exist; HTML will show it as A until then.

## 6. Research track (completed 2026-09-06)
Parallel deep-research into generative AI / agentic flows and modern software
engineering practice, then adaptation to DV. Outputs in `research/`:
- `genai-agentic-flows.md`
- `sw-engineering-ai-era.md`
- `ai-in-dv-state-of-the-art.md`
- `dv-adaptation-synthesis.md` (synthesis of the three above)
Feeds Ch. 33–35 and Section 6 (the book's own AI-assisted writing workflow).
