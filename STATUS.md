# STATUS — DV Textbook (zero-time memory)

> **Read this file first in every session. Update it before ending a session.**
> Stable conventions live in `AGENTS.md`; this file holds the living state.

## Current milestone
**M2 — Chapters 1, 2 reviewed and live; Ch.34 drafted, reviewed, revised, live; awaiting gate 2.** In parallel: AI-concept inventory delivered; MCP/automation tooling catalogue in research (two landscape subagents). Ch.3 after.

M1 — Repo scaffold: COMPLETE (2026-09-06). CI green on main (examples → PDF+HTML render → Pages deploy). Web edition live at https://mayurkubavat.github.io/dv-handbook (PDF at /Design-Verification-draft.pdf). Next: M2 = Chapter 1.

### Next three actions
1. Review `research/*.md` outputs; read `research/dv-adaptation-synthesis.md` once produced.
2. Finish design doc section 6 (writing workflow + AI assistance) using the synthesis note in `docs/specs/2026-09-05-dv-handbook-design.md`.
3. Write implementation plan for M1 (repo scaffold: Quarto skeleton, AGENTS.md, CI, first chapter) → `docs/plans/`.

## Chapter status
States: planned → outlined → drafting → examples-verified → reviewed → published

| # | Chapter | State | Words | Last touched |
|---|---|---|---|---|
| F | Building and Running the Examples (`appendices/appF-building-examples.qmd`) | examples-verified (4 run, 2 skipped: UVM needs commercial sim, UVM-SystemC needs library) | ~2,600 | 2026-09-06 |
| 1 | What Is Design Verification? (`chapters/ch01-what-is-dv.qmd`) | **reviewed** (gate 2 approved by author 2026-09-06 after subagent review + revision) | ~5,400 | 2026-09-06 |
| 2 | Verification Planning (`chapters/ch02-verification-planning.qmd`) | **reviewed** (gate 2 approved by author 2026-09-06) | ~5,500 | 2026-09-06 |
| 34 | Generative AI and Agentic DV (`chapters/ch34-generative-ai-agentic-dv.qmd`) | examples n/a (concept chapter); reviewed by subagent (`docs/reviews/ch34-review-2026-09-07.md`) and revised; pushed; **awaiting gate 2 (author review)** | ~7,600 | 2026-09-06 |
| — | chapters 3–33, 35 + appendices A–E, G, H | planned | 0 | 2026-09-05 |

Edition 1 target: Parts I–III + appendices A–D, F, G. See design doc §4.

## Decisions log
- 2026-09-05 — Toolchain: Quarto (PDF via MacTeX, HTML site). Rejected pure LaTeX, Pandoc, AsciiDoc, Typst.
- 2026-09-05 — Style: teaching textbook (Patterson-style) + GRM-style reference appendices.
- 2026-09-05 — Examples: SV/UVM primary; cocotb, pyuvm, SystemC, UVM-SystemC, future tech as secondary tracks. Language-open.
- 2026-09-05 — Blog: companion posts only (not full chapters) + PDF copy; reuse `DV/.claude/commands/format-blogger.md`.
- 2026-09-05 — License CC BY-NC-SA 4.0; hosting GitHub + Pages + Releases; free/open publishing.
- 2026-09-05 — Structure: monorepo at `DV/Book` → github.com/mayurkubavat/dv-handbook (not yet initialized).
- 2026-09-06 — Title: *Design Verification: From First Principles to Agentic AI*.
- 2026-09-06 — Style: 7×10 trim; Source Serif 4 / Source Sans 3 / JetBrains Mono; silicon-blue palette; 6 callout types; WaveDrom+Mermaid+draw.io figures. See design doc §4a.
- 2026-09-05 — Agent memory: `AGENTS.md` (stable) + `STATUS.md` (living) + `research/`.

## Research references
See `research/README.md` for the index. Active notes:
- `research/genai-agentic-flows.md` — agent architectures, MCP, memory, evals, agentic coding tools → feeds Ch. 34, design §6
- `research/sw-engineering-ai-era.md` — spec-driven dev, testing, formal, CI/CD, docs-as-code → feeds Ch. 27–29, 32, 34
- `research/ai-in-dv-state-of-the-art.md` — commercial + academic AI-for-DV → feeds Ch. 33–35
- `research/dv-adaptation-synthesis.md` — synthesis: adapting the above to DV → feeds Ch. 34, book workflow

## Environment (verified 2026-09-06)
- macOS, TeX Live 2024; **Quarto 1.10.18 at `~/.local/bin/quarto`** (tarball install; brew cask needs sudo). `scripts/build-book.sh` renders + binds cover → `_book/Design-Verification-draft.pdf`
- Verilator 5.030, Icarus (brew), SystemC (env `SYSTEMC_HOME=/usr/local/systemc-3.0.0`, also brew systemc); conda env **`dvbook`** (py3.12) with cocotb 2.x + pyuvm. Run examples via `conda run -n dvbook --no-capture-output make run` or `scripts/check-examples.sh`
- NOT available: commercial simulators, UVM source tree (UVM_HOME), UVM-SystemC library
- `gh` authenticated as mayurkubavat; git identity set
- Fonts installed via brew casks: Source Sans 3, Source Serif 4, JetBrains Mono (also JetBrains Mono Nerd Font)
- Cover tooling: rsvg-convert (librsvg), pdfinfo/pdffonts (poppler)

## House rules learned
- The publication rule is broader than the mention hook: any description of AI-assisted authoring (roles, hooks, reviewers) is out, even with no names. Reviewer prompt now checks for it explicitly; keep doing so.
- Ch.34 (and Part VII generally): concept chapters, theory + block diagrams + SW-practice parallels; cite evidence where a number is claimed but do not survey DV articles or build the chapter around runnable agent code (author, 2026-09-06).
- Run `research-topic` BEFORE `draft-chapter`, never during: the drafting lock blocks research writes (a research subagent had to park its note in scratch on 2026-09-06). Sequence is research → outline → draft.
- Attribution: primary sources for every fact, short attributed quotations only, redraw never reproduce, credit discoverers of named bugs (author, 2026-09-06). Written into AGENTS.md.
- Agent configuration (`.claude/` and the one-line stub that imports AGENTS.md) never goes to the remote; it is gitignored. Keep a private backup if it matters.
- No mention of AI assistance, its vendor, or its tooling anywhere in the repo, including commit messages (decided 2026-09-06). Factual references to AI models as book subject matter are fine.
- Keep every included source file ≤ 80 columns (≈ 83 fit at `\small` mono in the 7×10 trim); comment rulers exactly 72 cols. `breaklines` is only the safety net.
- Makefile recipes need real tabs; listings show 4 spaces (Pitfall callout in the build appendix explains this).

## Blockers
- Bare `ls` in this shell hangs (aliased to an interactive tool); use `/bin/ls`.

## Session log
- 2026-09-07 — Two landscape subagents writing `research/tooling-landscape-hardware.md` and `research/tooling-landscape-software.md` section by section (in progress). Stop hook now ignores `research/` (subagent output lands mid-session; STATUS is updated when notes are indexed).
- 2026-09-07 — Ch.34 second pass from review (verdict: needs another pass; 3 blockers): deleted the paragraph describing the book's own AI-assisted process (publication rule, caught by the reviewer, not the hook); fixed 4 alt texts + tools caption to match drawings; flow figure now feeds logs to planner and debug and routes formal status to gate 3; over-claims softened (search vs retrieval, 'since 2007', 90/14 pairing labeled as two experiments, TDD-faking claim replaced by the SpecBench result, superlatives dropped, AI Act hedged); no-overflow row rewritten as the RTL-counter trap; conventions box folded into prose; Future Directions moved after the worked example; delegation split for checker/coverage roles; DV counterparts made specific for grounding and multi-agent. PDF 102 pages. Pushed.
- 2026-09-07 — Ch.34 figures re-laid out: page-width figures ≤1000 px wide (type ≥7 pt in print), flow/delegation/swim-lane placed as sideways full-page figures (`rotating` package). PDF 100 pages. Reviewer relaunched (first run lost to a usage limit). Author requested: exhaustive AI-concept inventory for Ch.34 and an MCP/automation tooling catalogue for RTL, DV, debug, AST-based tools and SW-engineering analogues; two landscape-research subagents dispatched.
- 2026-09-06 — Ch.34 drafted as a concept chapter: 11 sections + worked example on paper (walk table + swim-lane), 11 block diagrams via `figures/blocks.py` + `gen_ch34_figures.py`, 43 concept-primary bib entries from `research/ch34-concept-sources.md`. PDF 94 pages. Review subagent dispatched.
- 2026-09-06 — Gate 1: Ch.34 outline rev. 2 approved. Research subagent dispatched for primary sources of the general concepts (no vendor blogs). Starting the block-diagram library.
- 2026-09-06 — Author asked to deep-dive the generative-AI chapter next. First Ch.34 outline (code-heavy agent loops) rejected by author: they want mainly theory and block diagrams, concepts related to DV and to SW-development practice, original rather than a survey of DV articles. Outline revision 2 written on that basis (11 sections, 11 planned figures, worked example on paper, no runnable code; model choice deferred). Gate 2: Ch.2 approved as reviewed. Order: Ch.34 before Ch.3.
- 2026-09-06 — Ch.2 second pass from review: report tool states renamed (tests pass / tests fail / unknown test / no test) with an evidence-only header line; prose no longer equates a passing test with closure; textbook/standards claims softened to the note's confidence; OpenTitan V2/V3 quoted directly; V2S acknowledged; Future Directions moved after the worked example; plan file folded to 80 cols, American spelling; figure matches the plan. Hook: `docs/reviews/` exempt from the mention check (evidence records). Pushed.
- 2026-09-06 — Ch.2 research note delivered (2nd run; 15 bib entries) and indexed; chapter prose written with citations; `figures/ch02-traceability.svg`; 3 bib entries added (UART/HMAC testplans, EE Times); chapter registered; PDF 70 pages. Review subagent dispatched.
- 2026-09-06 — Ch.2 examples: `examples/mk/python.mk` (lint = py_compile, run = python3 TOP), `fifo_plan.yaml` (12 items with stimulus/checking/coverage/closure), `plan_report.py` (reads `status.json`; treats EXPECT=fail examples as design failures; exits 1 while must-have items lack evidence), UART spec for exercises. Report: 3 passing / 4 failing / 5 no evidence. PyYAML added to dvbook env, CI and README.
- 2026-09-06 — Gate 2: Ch.1 approved as reviewed. Gate 1: Ch.2 outline approved. Ch.2 drafting started with examples.
- 2026-09-06 — Ch.2 outline written (7 sections; worked example = machine-readable FIFO plan + plan-report tool; UART spec for exercises). Research subagent relaunched with save-early instructions after the first run hit a usage limit.
- 2026-09-06 — Ch.1 live on Pages (CI green). Ch.2 started: research subagent dispatched (planning methodology, feature extraction, coverage model design, plan formats incl. OpenTitan testplans, sign-off, failure modes, AI-assisted planning).
- 2026-09-06 — `run.out` made deterministic: cocotb seed pinned (`COCOTB_RANDOM_SEED`) and timing columns stripped, so re-running examples no longer dirties the tree.
- 2026-09-06 — Ch.1 second pass from review: uncited details cut or hedged (Cougar Point transistor claim, lost-revenue clause, Zen 2 launch, sim speed), CAGR citation corrected to 2022 edition, Ormandy's method described correctly and quoted with marks, American spelling, run output included from `run.out` (new checker output), coverage-model gap taught + exercise 7, references page added (bibliography now renders). Checker now merges `status.json` across filtered runs. House-rule decisions recorded in AGENTS.md: Part numbers exempt from the label rule; Learning-objectives box is the opener; output always included from `run.out`. Not done from the review: mini-TOC per chapter (theme work, later); H-3 theme styling of callouts (later).
- 2026-09-06 — Ch.1 research note delivered (2nd run; 1st hit a usage limit); 15 markers filled with citations; 3 bib entries added (UVM2, HAVEN, Coverage Cookbook); chapter re-enabled in `_quarto.yml`; PDF 47 pages; review subagent dispatched.
- 2026-09-06 — CI: chapter-1 directed test failed lint only on Ubuntu's older Verilator (WIDTHEXPAND on `8'hA0 + i`); fixed with an explicit cast. Checker now prints failing lint/run logs so CI failures are readable. Watching the run; research note for Ch.1 still pending.
- 2026-09-06 — Project renamed: repo github.com/mayurkubavat/dv-handbook, site mayurkubavat.github.io/dv-handbook (old Pages URL does not redirect; old repo URL does). All links, cover, design doc filename updated. Ch.1 held out of `_quarto.yml` until sourced. First research subagent for Ch.1 hit a usage limit after saving 17 bib entries; relaunched.
- 2026-09-06 — Attribution rules added (AGENTS.md, review skill). Research subagent for Ch.1 still running; it has begun appending BibTeX entries to `refs.bib`. Next: fill the 15 `[NEEDS SOURCE]` markers from `research/ch01-cost-gap-lifecycle.md`, re-render, run review-chapter, then push.
- 2026-09-06 — Ch.1 drafted: examples (FIFO with early-full bug; directed passes, random SV + cocotb fail as intended), `EXPECT := fail` added to build system + checker + Appendix F, `figures/ch01-lifecycle.svg` (generator in `figures/`), chapter registered in `_quarto.yml`, PDF renders at 42 pages. Committed locally, NOT pushed until sources are filled. Verilator: `$fatal`/`$stop`/`$error` all abort (exit 134); `sv.mk` maps that to exit 1.
- 2026-09-06 — M2 started: Chapter 1 outline (`chapters/ch01-what-is-dv.qmd`, 9 sections, 4 planned examples, 6 exercises); research subagent dispatched for cost/gap/lifecycle figures + BibTeX. Skills were followed by hand (new project skills load on the next session start).
- 2026-09-06 — CI fixed twice (static fonts only; HTML rendered to `_site` so the PDF render does not wipe it). Run green; Pages live. M1 closed.
- 2026-09-06 — Pushed to GitHub (public). Publication rule enforced by commit-msg + pre-commit hooks; attribution trailers off. The agent stub file and the `.claude/` directory (skills, hooks, settings) are local-only, ignored, and purged from history. First CI: examples pass on Ubuntu; PDF render failed on fonts (xdvipdfmx invalid font), fix pushed: static font instances only.
- 2026-09-06 — Wrote `AGENTS.md` (constitution; a one-line stub imports it for the agent runtime), `.claude/settings.json` hooks (Stop → STATUS.md check; PreToolUse guard on research/ + docs/specs while `.claude/state/drafting` exists), `.githooks/pre-commit` (check changed examples), six skills in `.claude/skills/`, `.github/workflows/book.yml` (examples → render → Pages deploy on main → PDF on v* tags), LICENSE (CC BY-NC-SA text, MIT code), README. `git init`, first commit, repo github.com/mayurkubavat/dv-handbook.
- 2026-09-06 — Fixed PDF code wrapping: fvextra `breaklines` in `theme/preamble.tex` (Quarto's `code-overflow: wrap` is HTML-only), tabs→4 spaces in `theme/include-code.lua`, all included sources kept ≤80 cols. House rule added below.
- 2026-09-06 — M1 started: wrote `examples/common.mk` + `mk/{sv,cocotb,systemc}.mk`, six counter examples, `scripts/check-examples.sh` (→ `examples/status.json`), Quarto skeleton (`_quarto.yml`, `theme/preamble.tex`, `theme/include-code.lua`, highlight theme), Appendix F, `scripts/build-book.sh`. Installed Quarto, Icarus, SystemC, conda env dvbook. PDF: 24 pages incl. cover.
- 2026-09-06 — Synthesis note delivered; approved design §6 (writing workflow). Design doc complete pending review.
- 2026-09-06 — Approved design §4 (example pipeline) and §5 (blog/release). Cover finalized: boxed SVA inside viewer, Title-case CI stages, noise removed. Installed librsvg + poppler + fonts (Source Sans 3, Source Serif 4, JetBrains Mono). `theme/cover/build_cover.sh` → `cover.pdf` (2 pages, 7×10 in, fonts embedded) + PNG previews.
- 2026-09-06 — Research notes 1–2 delivered (agentic AI, SW engineering). Approved design §3 (style); chose title; cover generator + SVGs in `theme/cover/`; proof sheet reviewed locally
- 2026-09-05 — Brainstormed project; chose toolchain/style/license/hosting; approved repo layout + TOC; wrote design doc; launched 3 research agents (agentic AI, SW engineering, AI-in-DV); seeded STATUS.md and research index.
