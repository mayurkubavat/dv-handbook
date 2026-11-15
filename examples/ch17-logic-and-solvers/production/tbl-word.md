| bits | `a*b != b*a` | `shift_add(a,b) != shift_add(b,a)` |
|---:|---:|---:|
| 4 | unsat, 0.00 s | unsat, 0.01 s |
| 6 | unsat, 0.00 s | unsat, 0.02 s |
| 8 | unsat, 0.00 s | unsat, 0.82 s |
| 9 | unsat, 0.00 s | unsat, 6.25 s |
| 10 | unsat, 0.00 s | unsat, 31.07 s |
| 11 | unsat, 0.00 s | no answer in 120 s |
| 32 | unsat, 0.00 s | not run |
| 64 | unsat, 0.00 s | not run |

: One theorem asked of z3 in two forms: with the solver's own multiplication on both sides, and with a shift-and-add multiplier written out in word-level operators. z3 5.4.1, 2026-11-15, one four-core Linux machine, limit 120 seconds; the seconds are that machine's. {#tbl-ch17-word}
