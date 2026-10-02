| Construct | Icarus 13.0 | Verilator 5.052 |
|---|---|---|
| `covergroup` sampled by a clocking event `@(posedge clk)` | no build — syntax error | runs |
| `covergroup` with explicit `sample()` | no build — syntax error | runs |
| `covergroup` embedded in a class, sampling members | no build — syntax error | runs |
| `covergroup` with a `ref` formal argument, two instances | no build — syntax error | runs |
| `covergroup … with function sample(args)` | no build — syntax error | runs |
| explicit value bins `bins lo = {0, 1}` | no build — syntax error | runs |
| range bins with `$`: `{[0:3]}`, `{[12:$]}` | no build — syntax error | runs |
| array bins `bins b[] = {[0:3]}` | no build — syntax error | runs |
| sized array bins `bins b[2] = {[0:7]}` | no build — syntax error | wrong |
| transition bins `(0 => 1)`, `(0 => 1 => 3)` | no build — syntax error | runs |
| `wildcard bins hi = {2'b1?}` | no build — syntax error | runs |
| `ignore_bins` on an array of bins | no build — syntax error | wrong |
| `illegal_bins` declared, not hit | no build — syntax error | runs |
| `bins rest = default` | no build — syntax error | runs |
| `bins ev[] = {[0:7]} with (item % 2 == 0)` | no build — syntax error | wrong |
| `cross` of two coverpoints, read as `g.ab.get_inst_coverage()` | no build — syntax error | no build — Member 'ab' not found in covergroup 'cg' |
| `cross` with `binsof … intersect` user bins, read as member | no build — syntax error | no build — Member 'ab' not found in covergroup 'cg' |
| `ignore_bins` on a `cross` via `binsof`, read as member | no build — syntax error | no build — Member 'ab' not found in covergroup 'cg' |
| `iff` guard on a coverpoint | no build — syntax error | runs |
| `iff` guard on a cross, read as member | no build — syntax error | no build — Member 'ab' not found in covergroup 'cg' |
| `option.per_instance` with two instances | no build — syntax error | runs |
| `option.weight` on coverpoints | no build — syntax error | wrong |
| `option.goal` | no build — syntax error | runs |
| `option.at_least` at the covergroup level | no build — syntax error | wrong |
| `option.auto_bin_max` at the covergroup level | no build — syntax error | runs |
| `get_coverage()` (type-level, two instances) | no build — syntax error | wrong |
| `get_inst_coverage()` on a coverpoint, `g.cp.get_inst_coverage()` | no build — syntax error | no build — Member 'cp' not found in covergroup 'cg' |
| `stop()` / `start()` | no build — syntax error | wrong |
| `$get_coverage` | no build — syntax error | no build — Unsupported: IEEE 1800-2005 reserved word not implemente |
| enum coverpoint, auto bins per literal (3 literals, 2 bits) | no build — syntax error | wrong |
| `cross` of two auto-bin coverpoints, read as member | no build — syntax error | no build — Member 'ab' not found in covergroup 'cg' |
| `cross` of bare variables, read as member | no build — syntax error | no build — Member 'ab' not found in covergroup 'cg' |
| range-to-range transition bin `([0:1] => [2:3])` | no build — syntax error | no build — ../V3Ast.cpp:483: Null item passed to setOp1p |
| two-argument `get_inst_coverage(ref, ref)` | no build — syntax error | wrong |
| `option.name` | no build — syntax error | runs |

: What each open simulator does with the functional-coverage constructs this chapter teaches, measured by running one probe per row with the flags the book's build uses plus `--coverage` and `-Wno-fatal`, and checking the printed percentage against the one the standard gives. Of 35 constructs, 0 run on both, 17 on Verilator only, 0 on Icarus only and 18 on neither; 9 run on Verilator and print a wrong percentage. Regenerated from the probes on every run. {#tbl-ch08-support}

| Construct | Icarus 13.0 | Verilator 5.052 |
|---|---|---|
| cross, auto cross bins, judged through the group | no build — syntax error | wrong |
| cross with `binsof … intersect` user bins, judged through the group | no build — syntax error | wrong |
| `iff` on a cross, judged through the group | no build — syntax error | wrong |
| cross of two auto-bin coverpoints, judged through the group | no build — syntax error | wrong |
| cross of bare variables, judged through the group | no build — syntax error | wrong |
| `illegal_bins` value sampled | no build — syntax error | no run |
| two coverpoints of 4 and 2 bins, judged through the group | no build — syntax error | wrong |
| `ignore_bins` covering a whole named bin | no build — syntax error | wrong |
| `option.at_least` at the coverpoint | no build — syntax error | runs |
| bin value `'1` on an 8-bit coverpoint | no build — syntax error | wrong |
| `option.auto_bin_max` at the coverpoint | no build — syntax error | runs |
| transition repetition `(0 [*2])` | no build — syntax error | no build — Transition set without items |
| `option.weight`, expected 62.5 (c22 re-stated) | no build — syntax error | wrong |
| `bins b[2] = {[0:7]}` after one sample | no build — syntax error | wrong |
| enum with 4 literals on 2 bits (control for c30) | no build — syntax error | runs |
| `stop()` before every sample | no build — syntax error | wrong |

: What each open simulator does with the second set of functional-coverage probes: crosses judged through the group, and discriminating probes, measured by running one probe per row with the flags the book's build uses plus `--coverage` and `-Wno-fatal`, and checking the printed percentage against the one the standard gives. Of 16 constructs, 0 run on both, 3 on Verilator only, 0 on Icarus only and 13 on neither; 11 run on Verilator and print a wrong percentage. Regenerated from the probes on every run. {#tbl-ch08-support-x}
