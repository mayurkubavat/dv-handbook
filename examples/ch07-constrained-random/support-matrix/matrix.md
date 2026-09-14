| Construct | Icarus 13.0 | Verilator 5.052 with z3 5.1.0 |
|---|---|---|
| `rand` properties, unconstrained `randomize()` | no build — Error: randomize is not a method of class pkt. | runs |
| `randc`: each value once per cycle | no build — Error: randomize is not a method of class pkt. | runs |
| `randomize() with { inside }` | no build — syntax error | runs |
| `constraint` block with `inside` set | no build — "inside" expressions not supported yet. | runs |
| relational constraint between two variables | no build — Constraint declarations not supported. | runs |
| `dist` with `:=` weights | no build — syntax error | runs |
| `dist` with `:/` weights | no build — syntax error | runs |
| implication `->` | no build — Constraint declarations not supported. | runs |
| `if`/`else` constraint | no build — Constraint declarations not supported. | runs |
| `foreach` constraint on a fixed array | no build — Constraint declarations not supported. | runs |
| `solve … before` (legality) | no build — syntax error | runs |
| `soft` constraint, overridden inline | no build — syntax error | runs |
| `unique` constraint | no build — syntax error | runs |
| `constraint_mode(0)` and query | no build — Constraint declarations not supported. | runs |
| `rand_mode(0)` and query | no build — Can't find task rand_mode in class pkt | runs |
| `pre_randomize` / `post_randomize` | no build — Error: randomize is not a method of class pkt. | runs |
| `std::randomize(v)` | no build — syntax error | runs |
| `std::randomize(v) with` | no build — syntax error | runs |
| `$urandom`, `$urandom_range` | runs | runs |
| `$urandom(seed)` replays a sequence | no run | wrong |
| run-to-run reproducibility (values printed) | no build — "inside" expressions not supported yet. | runs |
| object stability: `obj.srandom(seed)` | no build — Can't find task srandom in class pkt | runs |
| thread stability: `process::self().srandom` | no build — syntax error | runs |
| contradictory constraints return 0 | no build — Constraint declarations not supported. | runs |
| `inside {array}` | no build — "inside" expressions not supported yet. | runs |
| `rand` enum with a constraint | no build — Constraint declarations not supported. | runs |
| `rand` class-handle member (nested) | no build — "inside" expressions not supported yet. | runs |
| `randomize(a)` argument form | no build — Error: randomize is not a method of class pkt. | runs |
| signed `int` in a negative range | no build — "inside" expressions not supported yet. | runs |
| constraint on a non-rand state variable | no build — Constraint declarations not supported. | runs |
| hand-rolled `$urandom_range` in a class method | runs | runs |

: What each open simulator does with the randomization constructs this chapter teaches, measured by running one probe per row with the flags the book's build uses, the solver on the path, and checking the printed values. Of 31 constructs, 2 run on both, 28 on Verilator only, 0 on Icarus only and 1 on neither. Regenerated from the probes on every run. {#tbl-ch07-support}
