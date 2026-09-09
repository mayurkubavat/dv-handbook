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
- `docs/specs/2026-09-05-dv-handbook-design.md` design doc (the spec)
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

## Chapter workflow (agent skills, kept locally and not in this repository)
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
- The generative-AI chapter closes the book. Register every new chapter in
  `_quarto.yml` **before** `chapters/ch34-generative-ai-agentic-dv.qmd`, never
  after. Its file keeps the `ch34-` name for history; it is chapter 35.
- Cross-reference by label (`@sec-...`, `@tbl-...`), never by hard-coded chapter,
  section, figure or table number. Part numbers ("Part II") are exempt: parts are
  fixed structure and Quarto cannot label them.
- Every chapter opens with a one-line epigraph, then a `callout-note` titled
  "Learning objectives". That box is the template's opener, not a seventh
  callout kind.
- Simulator output shown in a chapter is included from the example's `run.out`
  (written by `scripts/check-examples.sh`), never typed by hand, so it cannot
  drift from what the code prints.
- British or American spelling: American, consistently.

## Attribution and originality (applies to every chapter)
- Cite the primary source for every fact, figure and quotation: `[@key]` with a
  full `refs.bib` entry (author, title, venue or publisher, year, URL, access
  date). Surveys are cited by edition. Secondary retellings are not sources.
- Write in the book's own words. Paraphrase from understanding, never by
  rewording a passage sentence by sentence. Direct quotation is limited to a
  sentence or two, in quotation marks, with the citation on the same line.
- Never reproduce a figure, table, code listing or dataset from a copyrighted
  source. Redraw figures from the underlying data with a "data from [@key]"
  credit; write code from scratch. Open-licensed material may be adapted only
  with its license and attribution stated in the caption.
- Named bugs, products and people are described from public primary accounts
  (vendor advisories, CVE records, the discoverer's own write-up) and credited
  to them. Trademarks are used descriptively.
- Further-reading entries name the work, its authors and, where relevant, the
  edition; they do not summarise the work's text.
- The book never cites its own working documents. `research/` notes and
  `docs/specs/` are evidence and planning records, not sources: their content
  belongs in the chapter text and their citations in `refs.bib`. A reader of
  the published book has no access to them and no reason to care that they
  exist. A `.qmd` that names a repository path as a source is a defect.

## Separation of drafting and judging
While `draft-chapter` runs, a local marker file exists and a tool hook denies
edits under `research/` and `docs/specs/`. The drafter
reads the evidence; it does not rewrite it. `review-chapter` always runs in a
fresh subagent that never sees the drafting conversation.

## Publication rule
This is a public repository. Nothing in it names the AI assistant, its vendor, or
AI assistance in authoring: not in prose, comments, docs, `STATUS.md`, or commit
messages (no co-author or session trailers). Factual references to AI models as
the *subject* of the book (benchmarks, vendors in Part VII) are fine. The
pre-commit hook rejects a commit whose staged files (outside `research/` and
`docs/reviews/`, which are evidence records) or message mention them.

## Git
`main` is the release branch. Commit messages: imperative, one line, body
optional. The pre-commit hook runs `scripts/check-examples.sh --changed`.
Tags `vX.Y` trigger the release workflow (PDF attached, Pages deployed).
