# Research note: Logic and Solvers for Verifiers (Chapter 17)

Date: 2026-11-15. Status: in progress (written section by section; the
decisive material is first). Feeds: the logic-and-solvers chapter; sets
up the formal property verification chapter and the formal techniques
catalog. Outline: `research/ch17-outline.md`.

Machine and versions for every measurement below (4 cores, 15 GB, Linux):
Python 3.13.18 (`/opt/dvtools/venv`), z3 5.4.1 (binary and `z3-solver`
5.4.1.0), Yosys 0.68 (38e001a6f), InFormal 0.1.0 commit 5114330,
CaDiCaL 3.0.1 (c6073042; a `cadical` binary exists at
`/opt/informal-tools/cadical/build/cadical`, it is not on the PATH),
ABC (`/opt/dvtools/bin/abc`, `yosys-abc`). Installed for this note with
`pip install python-sat dd` into the venv: `python-sat` 1.9.dev22
(ships compiled solvers: MiniSat 2.2, Glucose, CaDiCaL 1.9.5, Kissat
4.0.4 and others; it is a binary wheel, not pure Python) and `dd` 0.6.0
(pure-Python BDDs, `dd.autoref`; the CUDD binding `dd.cudd` is not in
the wheel) with their dependencies `ply`, `six`, `networkx`,
`astutils`. `PATH=/opt/dvtools/bin:$PATH:/opt/dvtools/venv/bin`.

Scratch scripts: `/tmp/claude-0/-home-user/94f1b657-ef34-54a0-bbd5-70269d6ff646/scratchpad/ch17/`
(outside the repository; the ones the chapter needs are reproduced in
the appendix of this note so that the note stands alone).

