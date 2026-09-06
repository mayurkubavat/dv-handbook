# Design Verification: From First Principles to Agentic AI

Open textbook (Quarto, CC BY-NC-SA 4.0). This file is the stable constitution.
The living state is in `STATUS.md`.

## First and last thing in every session
1. **Read `STATUS.md` first.** It holds the milestone, next actions, chapter
   states, decisions and session log. Do not re-litigate decisions listed there.
2. **Update `STATUS.md` before ending.** Add a session-log line and adjust next
   actions. A Stop hook blocks ending the turn if other files changed and
   `STATUS.md` did not.

## Map
- `docs/specs/2026-09-05-dv-textbook-design.md` design doc (the spec)
- `chapters/`, `appendices/` Quarto `.qmd` sources; `index.qmd` preface
- `examples/<chNN-slug>/<lang>/` runnable listings; `examples/common.mk` +
  `examples/mk/*.mk` build system (targets `lint`, `run`, `clean`)
- `research/` cited research notes, indexed in `research/README.md`
- `theme/` LaTeX preamble, Lua filters, highlight theme, cover generator
- `scripts/check-examples.sh` verifies examples, writes `examples/status.json`
- `scripts/build-book.sh` renders PDF and binds the cover
- `blog/` companion-post drafts; `docs/reviews/` chapter review findings

## Commands
```bash
scripts/check-examples.sh [filter|--changed]   # lint + run examples
scripts/build-book.sh                          # _book/Design-Verification-draft.pdf
~/.local/bin/quarto render --to html           # web edition
conda run -n dvbook --no-capture-output make run   # cocotb/pyuvm example
```
Quarto is at `~/.local/bin/quarto`. Use `/bin/ls`; bare `ls` hangs here.

## Chapter workflow (skills in `.claude/skills/`)
research-topic → outline-chapter → **[gate 1: outline approved by author]** →
draft-chapter → verify-examples → review-chapter → **[gate 2: author review]**
→ release → book-blog-post. **[gate 3: author tags the release]**

Chapter states: planned → outlined → drafting → examples-verified → reviewed →
published. A state advances only through the skill that produces its evidence.
Never hand-edit a state to look further along than the evidence supports.

## House rules (apply to every chapter)
- Follow the chapter template: learning objectives, motivation, concepts,
  worked example, callouts, future directions, summary, exercises, further
  reading. Six callouts only: Definition, In Practice, Pitfall, Future
  Directions, Worked Example, Exercise.
- Every number, benchmark or claim about a tool has a source: `[@key]` in
  `refs.bib`, or a `research/` note that cites a URL. No unsourced numbers.
- Vendor marketing figures are labelled as vendor claims, never as results.
- Every listing is a file under `examples/` spliced with
  ```` ```{.lang include="examples/..."} ```` ````. No code typed into prose.
- Included source files stay at 80 columns or less; comment rulers are 72.
- Makefile recipes use real tabs.
- Cross-reference by label (`@sec-...`, `@tbl-...`), never by hard-coded number.
- British or American spelling: American, consistently.

## Separation of drafting and judging
While `draft-chapter` runs, a marker file `.claude/state/drafting` exists and a
PreToolUse hook denies edits under `research/` and `docs/specs/`. The drafter
reads the evidence; it does not rewrite it. `review-chapter` always runs in a
fresh subagent that never sees the drafting conversation.

## Publication rule
This is a public repository. Nothing in it names the AI assistant, its vendor, or
AI assistance in authoring: not in prose, comments, docs, `STATUS.md`, or commit
messages (no co-author or session trailers). Factual references to AI models as
the *subject* of the book (benchmarks, vendors in Part VII) are fine. The
pre-commit hook rejects a commit whose staged files (outside `research/`) or
message mention them.

## Git
`main` is the release branch. Commit messages: imperative, one line, body
optional. The pre-commit hook runs `scripts/check-examples.sh --changed`.
Tags `vX.Y` trigger the release workflow (PDF attached, Pages deployed).
