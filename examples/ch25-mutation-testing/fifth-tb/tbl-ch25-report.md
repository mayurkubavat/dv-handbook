+--------------------+------------+------------+--------------------+
| testbench (traffic | source,    | source,    | netlist sample,    |
| of tb_fifo_sva.sv) | default    | randomized | 95% interval       |
+====================+============+============+====================+
| the checker as     | 22 of 44   | 23 of 44   | 39 of 1000 [0.028, |
| shipped            |            |            | 0.053]             |
+--------------------+------------+------------+--------------------+
| the checker plus   | 37 of 44   | 40 of 44   | 899 of 1000        |
| the data check     |            |            | [0.879, 0.917]     |
+--------------------+------------+------------+--------------------+

: Kills before and after the data check: 44 source mutants at default and randomized initial values (seeds 1-5), and a uniform sample of 1,000 netlist mutations (seed 1) {#tbl-ch25-report}
