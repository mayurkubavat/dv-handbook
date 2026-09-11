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
research-topic → outline-chapter → **[gate 1]** → draft-chapter →
verify-examples → review-chapter → **[gate 2]** → release → book-blog-post.
**[gate 3: the author tags the release]**

**Gates 1 and 2 are delegated** (author, 2026-09-09: "You decide review
process ... and ungate to proceed"). Gate 3 stays with the author, because a
tag is public and irreversible. Delegated does not mean removed: a gate is
passed by evidence, not by the drafter's own satisfaction.

- **Gate 1** passes when the outline names, for every section, what the reader
  must be able to do, and when the research note's constraints are folded into
  it. Record the decision and its date in `STATUS.md`. If the research left a
  question that changes the chapter's shape, raise it with the author instead
  of choosing.
- **Gate 2** passes only when an independent reviewer, in a fresh subagent that
  never saw the drafting conversation, returns **no blocking findings**. One
  review is not enough where the chapter makes claims about code the book
  ships: those are verified by a reviewer that *runs* the code against designs
  it constructs itself, because three of the four blocking bugs found in Ch.3
  were things the prose asserted and nobody had executed. A verdict of "needs
  another pass" means another pass and another review, not a judgement call.
- **Escalate to the author regardless of the gates** for: a change to the
  book's structure or scope, anything that would make a public claim about a
  named company or person, and any finding that suggests an earlier approved
  chapter is wrong.

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
- **When a spliced file changes, check every page that splices it.** A
  chapter and an appendix can print the same file, and a commit that fixes
  one page's claim about it can silently falsify another's. `grep -rn
  'include="<path>"' chapters/ appendices/` before committing a change to
  anything under `tools/` or `examples/`.
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
- A DOI is a locator: an entry that carries one needs no URL and no access date.
  Where a paper's own URL has since died, the entry keeps the canonical URL and
  its `note` says where the paper was actually read. A reader who clicks gets
  nothing either way; a reader who searches gets the paper.
- Check the *whole* author field and the *whole* title against the document
  itself, not against a note about it. `scripts/check-citations.sh` matches a
  surname and nothing else, so a wrong given name, a wrong title and an author
  who does not belong on the paper all pass it. Three of those reached print in
  one chapter. A surname with a particle is braced -- `{Ben Dhaou}, Imed` --
  because BibTeX otherwise reads the particle as a middle name.
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

## Writing long outputs from a subagent
A review or research note that is composed in one response and written at the
end can be lost whole to an output limit, and that has now happened to both a
research run and a review. Instruct any subagent producing a long document to
**write the file early and append to it section by section**, ordered so that
the most important part lands first: a review starts with its verdict and
blocking findings, a research note with the question that decides the work. A
partial file is worth far more than a lost run, and the work itself usually
survives even when the write does not, so ask the agent to resume and append
before re-running it from scratch.

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
