# guide.tcl -- eight situations, four engines, one verdict each.
# Every `prove` selects one engine and gets four seconds. A line
# beginning "cell|" records what that engine said; guide.py turns the
# lines into the chapter's engine table. The verdict expected of each
# engine is written here, so a changed verdict fails the run.
set here [file dirname [info script]]
source $here/../common/proof.tcl
set c11 $here/../../ch11-architecture-to-verification
set engines {informal-bmc informal-kind informal-ic3 ric3-ic3}

# ran NAME -- how many engines the last `prove` ran on property NAME,
# read from the session's list of engine outcomes for it. The tool
# leaves the list empty when it gives the property to no engine.
proc ran {name} {
  set json [informal::session]
  set at [string first "\"name\": \"$name\"," $json]
  set at [string first "\"engines\": \[" $json $at]
  set end [string first "\]" $json $at]
  return [regexp -all {"engine":} [string range $json $at $end]]
}

# situation KEY NAME WANT -- prove NAME under each engine in turn;
# WANT lists the status expected of each, in the order of $engines:
# a status, or notrun for an `undetermined` with no engine run.
proc situation {key name want} {
  set name [full $name]
  foreach engine $::engines status $want {
    informal::set_engines $engine
    set_prove_time_limit 4s
    prove -property $name
    set got [get_status $name]
    if {$got eq "undetermined" && [ran $name] == 0} {set got notrun}
    if {$got ne $status} {
      puts "unexpected: $name is $got under $engine, expected $status"
      incr ::unexpected
    }
    puts "cell|$key|$engine|$got|[depth $name]"
  }
}

# counter BUG -- the counter of ../bmc-depth with its bug BUG steps in.
proc counter {bug} {
  clear -all
  analyze -sv12 $::here/../bmc-depth/deep.sv
  elaborate -top deep -parameter BUG $bug
  clock clk
  reset -expression {rst}
}

# fifo RTL ARGS -- a FIFO, alone or with files to bind to it.
proc fifo {rtl args} {
  clear -all
  analyze -sv12 $rtl {*}$args
  elaborate -top fifo {*}$::params
  clock clk
  reset -expression {!rst_n}
}
set checker [list $ch09/fifo-checker/fifo_sva.sv \
                  $ch09/fifo-checker/fifo_bind.sv]

counter 16
situation bug16 a_never {cex cex cex cex}
counter 64
situation bug64 a_never {cex cex cex cex}

set params {-parameter DEPTH 8 -parameter WIDTH 1}
fifo $ch09/rtl/fifo_fixed.sv
assert -name CountPtrs_A {count[$clog2(DEPTH)-1:0] == wr_ptr - rd_ptr}
assert -name EmptyPtrs_A {empty |-> wr_ptr == rd_ptr}
situation onestep CountPtrs_A {undetermined proven proven proven}
situation reach   EmptyPtrs_A {undetermined undetermined proven proven}

set params {}
fifo $ch09/rtl/fifo_fixed.sv {*}$checker
situation cover FullReached_C {covered covered covered covered}
fifo $here/../../ch01-what-is-dv/rtl/fifo.sv {*}$checker
situation nocover FullReached_C \
    {undetermined unreachable unreachable unreachable}

clear -all
analyze -sv12 $here/../lasso/live_small.sv
elaborate -top live_small
clock clk
reset -expression {rst}
assert -name Grant_A {req && n == 2'd0 |-> s_eventually gnt}
assume -name Fair_M  {s_eventually !stall}
situation live Grant_A {undetermined proven proven notrun}

clear -all
analyze -sv12 $c11/rtl/dma_regs_pkg.sv $c11/rtl/dma_v2.sv \
    $ch09/axi-rules/axil_master_sva.sv $ch09/axi-rules/dma_bind.sv
elaborate -top dma_v2
clock PCLK
reset -expression {!PRESETn}
situation dma ArStable_A {undetermined undetermined proven proven}
finish
