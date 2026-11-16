+--------------------------------+--------------------------+------------------------------------------+
| Command                        | What it is for           | What the tool did                        |
+================================+==========================+==========================================+
| **Reading a design**           |                          |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `clear -all`                   | forget the design, the   | accepted; returns nothing                |
|                                | properties and the       |                                          |
|                                | results                  |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `analyze -sv12                 | read SystemVerilog       | accepted; returns nothing                |
| bmc-depth/deep.sv`             | source                   |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `elaborate -top deep           | build one top,           | 1 property more; returns `deep`          |
| -parameter BUG 16`             | overriding a parameter   |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `get_design_info`              | summary of what was      | returns `top deep files 1 clocks 0 props |
|                                | elaborated               | 1`                                       |
+--------------------------------+--------------------------+------------------------------------------+
| **Clock and reset**            |                          |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `clock clk`                    | name the clock that      | accepted; returns nothing                |
|                                | every property samples   |                                          |
|                                | on                       |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `reset -expression {rst}`      | the condition held in    | accepted; returns nothing                |
|                                | the reset cycle          |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| **Properties from the script** |                          |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `assert -name a_step {!en |=>  | add an assertion         | 1 property more; returns `a_step`        |
| $stable(cnt)}`                 |                          |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `assume -name m_slow {en |=>   | add an assumption        | 1 property more; returns `m_slow`        |
| !en}`                          |                          |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `cover -name c_three {cnt ==   | add a cover              | 1 property more; returns `c_three`       |
| 16'd3}`                        |                          |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `include extra.tcl`            | read another script      | 1 property more; returns `c_five`        |
+--------------------------------+--------------------------+------------------------------------------+
| `get_property_list`            | names of all properties, | returns `deep.a_never a_step m_slow      |
|                                | the RTL ones under their | c_three c_five`                          |
|                                | path                     |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `get_property_list -include    | names filtered by type   | returns `c_three c_five`                 |
| {type cover}`                  |                          |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| **Proving**                    |                          |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `set_prove_time_limit 5s`      | limit for each property; | accepted; returns nothing                |
|                                | units s, m, h            |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `set_prove_time_limit 500ms`   | a unit the tool does not | error: bad time unit in '500ms'          |
|                                | read                     |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `informal::set_engines         | select engines by name   | accepted; returns nothing                |
| informal-kind`                 | (tool extension)         |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `prove -all`                   | prove every enabled      | prints the property table; returns the   |
|                                | property                 | counts `proven 1 cex 1 covered 2         |
|                                |                          | unreachable 0 undetermined 0 error 0`    |
+--------------------------------+--------------------------+------------------------------------------+
| `prove -property deep.a_never` | prove one property, by   | prints the property table; returns the   |
|                                | its full name            | counts `proven 0 cex 1 covered 0         |
|                                |                          | unreachable 0 undetermined 0 error 0`    |
+--------------------------------+--------------------------+------------------------------------------+
| `prove -property a_never`      | a short name for a       | error: no property matches 'a_never'     |
|                                | property of the RTL      |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `prove -bg -all`               | a vendor option that has | says: prove: ignoring -bg (vendor        |
|                                | no meaning here          | engine/GUI option); prints the property  |
|                                |                          | table; returns the counts `proven 1 cex  |
|                                |                          | 1 covered 2 unreachable 0 undetermined 0 |
|                                |                          | error 0`                                 |
+--------------------------------+--------------------------+------------------------------------------+
| `set_engine_mode {Ht}`         | a vendor engine code     | accepted; returns nothing                |
+--------------------------------+--------------------------+------------------------------------------+
| **Results**                    |                          |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `get_status a_step`            | one status word          | returns `proven`                         |
+--------------------------------+--------------------------+------------------------------------------+
| `get_status deep.a_never`      | the same for a failing   | returns `cex`                            |
|                                | property                 |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `get_property_list -include    | names filtered by status | returns `c_three c_five`                 |
| {status covered}`              |                          |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `report`                       | the property table again | prints the property table; returns       |
|                                |                          | several lines of text                    |
+--------------------------------+--------------------------+------------------------------------------+
| `informal::session`            | the whole session as     | returns several lines of text            |
|                                | JSON (tool extension)    |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `visualize -violation          | open a trace in a viewer | error: visualize: the waveform UI is not |
| -property deep.a_never`        |                          | available yet (phase 1 UI v1)            |
+--------------------------------+--------------------------+------------------------------------------+
| **Changing the problem**       |                          |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `assume -disable m_slow`       | switch an assumption     | accepted; returns nothing                |
|                                | off, results kept        |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `assume -enable m_slow`        | and on again             | accepted; returns nothing                |
+--------------------------------+--------------------------+------------------------------------------+
| `assert -disable deep.a_never` | switch an assertion of   | accepted; returns nothing                |
|                                | the RTL off              |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `assert -enable deep.a_never`  | and on again             | accepted; returns nothing                |
+--------------------------------+--------------------------+------------------------------------------+
| `assume -remove m_slow`        | delete a property        | 1 property fewer                         |
+--------------------------------+--------------------------+------------------------------------------+
| `assert -env {en}`             | an assumption written in | 1 property more; returns `assume_0`      |
|                                | the other vendor style   |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `stopat cnt`                   | cut a signal free of its | accepted; returns nothing                |
|                                | driver                   |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `stopat -list`                 | the signals cut free     | returns `cnt`                            |
+--------------------------------+--------------------------+------------------------------------------+
| `stopat -clear`                | undo every cut           | accepted; returns nothing                |
+--------------------------------+--------------------------+------------------------------------------+
| `set_lowering`                 | the tool's switches for  | returns `skip_initial_checks off         |
|                                | reading properties       | isunknown_is_false off`                  |
+--------------------------------+--------------------------+------------------------------------------+
| `task -create t1`              | a second set of          | says: task -create t1: tasks are not     |
|                                | properties               | modelled yet; properties stay in one     |
|                                |                          | task                                     |
+--------------------------------+--------------------------+------------------------------------------+
| `get_version`                  | a command the tool does  | error: invalid command name              |
|                                | not have                 | "get_version"                            |
+--------------------------------+--------------------------+------------------------------------------+
| **A design with a black box**  |                          |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `clear -all`                   | start again              | 5 properties fewer                       |
+--------------------------------+--------------------------+------------------------------------------+
| `analyze -sv12                 | the second design        | accepted; returns nothing                |
| over-constraint/handshake.sv`  |                          |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `elaborate -top handshake      | replace a module by free | returns `handshake`                      |
| -bbox_m {timer}`               | outputs                  |                                          |
+--------------------------------+--------------------------+------------------------------------------+
| `get_property_list`            | the properties that      | accepted; returns nothing                |
|                                | survive                  |                                          |
+--------------------------------+--------------------------+------------------------------------------+

: Shell commands and InFormal 0.1.0 (commit `5114330`), generated by the example `shell-commands`: the lines run top to bottom in one session, each caught so that an error does not end it, and the last column is what was measured for that line: an error message, a message the tool printed, a change in the number of properties, the value returned. Paths are shown relative to the chapter's examples. {#tbl-ch18-shell}
