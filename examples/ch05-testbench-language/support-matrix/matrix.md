| Construct | Icarus 13.0 | Verilator 5.030 |
|---|---|---|
| 2-state and 4-state integral types | runs | wrong |
| fixed and packed arrays | runs | runs |
| dynamic arrays | runs | runs |
| associative arrays | no build — Type names are not valid expressions here. | runs |
| queues | runs | runs |
| packed structs | runs | runs |
| packed unions | runs | runs |
| enums and their methods | runs | runs |
| `$cast` on an enum | no run | runs |
| strings | runs | runs |
| interface, used hierarchically | runs | runs |
| interface as a module port, with modport | no build — syntax error | runs |
| virtual interface | no build — syntax error | runs |
| class: new, handles, properties | runs | runs |
| static member, read through an instance | runs | runs |
| static member, read through `cls::` | no build — syntax error | runs |
| parameterized class | no build — syntax error | runs |
| inheritance, method called on the derived handle | runs | runs |
| virtual method, call through a base handle | wrong | runs |
| nested class | no build — syntax error | no build — Unsupported: class within class |
| clocking block | no build — syntax error | runs |
| modport carrying a clocking block | no build — syntax error | no build — Unsupported: Modport clocking |
| program block | runs | runs |
| randomize(), no constraints | no build — Error: randomize is not a method of class txn. | runs |
| randomize() with a constraint | no build — syntax error | wrong |
| solve-before and soft constraints | no build — syntax error | wrong |
| covergroup inside a class | no build — syntax error | no build — Unsupported: covergroup |
| event, fork and join | runs | runs |
| mailbox, typed | no build — syntax error | runs |
| queues and arrays of handles | no run | runs |
| interface class | no build — syntax error | runs |

: What each open simulator does with the constructs this chapter teaches, measured by running one probe per row with the flags the book's build uses and checking the printed values. Of 31 constructs, 13 run on both, 12 on Verilator only, 1 on Icarus only and 5 on neither. Regenerated from the probes on every run. {#tbl-ch05-support}
