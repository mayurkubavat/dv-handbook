# Research note: Formal Property Verification (Chapter 18)

Date: 2026-11-15. Status: research for gate 1; the outline is
`research/ch18-outline.md`. Written section by section, the deciding
questions first. Section numbers are fixed (1 questions, 2 sources,
3 measurements, 4 constraints) but the sections were written in the
order 1, 3, 2, 4, so section 3 stands before section 2 in the file,
as in the note for the chapter before this one.

Scope given: design doc section 4, entry 18: "bounded model checking,
k-induction, IC3/PDR at reading level, assumptions and over-constraint,
covers and vacuity, liveness and fairness; three reference tables (SVA
forms, shell commands, engine selection); on InFormal, the author's
open formal tool, pinned by commit". The author's instruction for the
two formal chapters: this material "will serve as golden reference for
Formal Verification and techniques". Readers: DV and RTL engineers.

Machine and pins for every measurement below: 4 cores, 15 GB, Ubuntu
24.04; InFormal 0.1.0 at commit `5114330` (`informal --version` prints
`informal 0.1.0`), CaDiCaL linked, Bitwuzla not built; rIC3 1.5.2 as
`ric3` (used for comparison rows only: the book's engine list,
`examples/mk/informal-engines.toml`, is empty, so no book example can
select it); Python 3.13.18; the `z3-solver` package 5.4.1. Experiments
ran in a scratch directory made with `mktemp -d`; every script that
is worth keeping is under `research/ch18-measurements/`, with the
output it printed under `research/ch18-measurements/out/`.

What already exists and is not repeated here: the tool survey in
`research/informal-measurements/FINDINGS.md` (cited as FM with its
section letter), Chapter 9's research note, and Chapter 17's
(`research/ch17-logic-and-solvers.md`).

