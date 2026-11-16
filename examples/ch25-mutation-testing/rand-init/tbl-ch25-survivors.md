+--------+------------------------+----------------+----------------+------------------------+
| mutant | miter                  | killed by      | killed by      | class                  |
|        |                        | (default       | (randomized    |                        |
|        |                        | values)        | values)        |                        |
+========+========================+================+================+========================+
| `m05`  | proved equivalent      | none           | none           | equivalent only under  |
|        | (ric3-ic3) under the   |                |                | the tool's reset model |
|        | tool's reset model     |                |                |                        |
+--------+------------------------+----------------+----------------+------------------------+
| `m09`  | differs at depth 2     | none           | ch01-directed, | not equivalent: a      |
|        |                        |                | ch01-random    | missing reset          |
+--------+------------------------+----------------+----------------+------------------------+
| `m11`  | differs at depth 2     | none           | ch01-directed, | not equivalent: a      |
|        |                        |                | ch01-random    | missing reset          |
+--------+------------------------+----------------+----------------+------------------------+
| `m13`  | differs at depth 1     | none           | ch01-directed, | not equivalent: a      |
|        |                        |                | ch01-random,   | missing reset          |
|        |                        |                | ch09-sva       |                        |
+--------+------------------------+----------------+----------------+------------------------+
| `m32`  | proved equivalent      | none           | none           | equivalent outright    |
|        | (ric3-ic3)             |                |                |                        |
+--------+------------------------+----------------+----------------+------------------------+
| `m36`  | proved equivalent      | none           | none           | equivalent outright    |
|        | (ric3-ic3)             |                |                |                        |
+--------+------------------------+----------------+----------------+------------------------+
| `m43`  | proved equivalent      | none           | none           | equivalent under a     |
|        | (ric3-ic3)             |                |                | reachable-state        |
|        |                        |                |                | invariant              |
+--------+------------------------+----------------+----------------+------------------------+
| `m44`  | proved equivalent      | ch09-sva       | ch09-sva       | equivalent under a     |
|        | (ric3-ic3) at the      |                |                | reachable-state        |
|        | ports                  |                |                | invariant relating the |
|        |                        |                |                | copies; killed by      |
|        |                        |                |                | Sync_A                 |
+--------+------------------------+----------------+----------------+------------------------+

: The seven source mutants no testbench killed, and m44: the miter's verdict and the simulation verdicts {#tbl-ch25-survivors}
