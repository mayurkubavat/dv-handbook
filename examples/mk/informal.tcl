# informal.tcl -- three procedures the book's InFormal scripts share.
# examples/mk/informal.sh loads this file before the script it runs.
#
# `informal shell` exits with status 0 whatever it proved or refuted,
# so a script that is part of a build has to compare the verdicts with
# the ones it expects and choose its own exit status.

set ::unexpected 0

# expect STATUS NAME ... -- each named property must have this status
# (proven, cex, covered, unreachable, undetermined, error). A property
# written in the RTL is listed under its hierarchical name. A name given
# here matches every property whose name ends in it, so two instances
# of one checker are both held to the status; a full hierarchical name
# selects one. A name that matches nothing is unexpected too.
proc expect {status args} {
  foreach want $args {
    set found 0
    foreach full [get_property_list] {
      if {$full eq $want || [string match "*.$want" $full]} {
        incr found
        set got [get_status $full]
        if {$got ne $status} {
          puts "unexpected: $full is $got, expected $status"
          incr ::unexpected
        }
      }
    }
    if {$found == 0} {
      puts "unexpected: $want is missing, expected $status"
      incr ::unexpected
    }
  }
}

# trace NAME -- the VCD file InFormal wrote for a counterexample or a
# covered cover; ::workdir is set by informal.sh.
proc trace {name} {
  foreach full [get_property_list] {
    if {$full eq $name || [string match "*.$name" $full]} {
      return [file join $::workdir $full.vcd]
    }
  }
  error "trace: no property named $name"
}

# finish -- the last command of a script: exit status 1 when any
# expectation was not met.
proc finish {} {
  exit [expr {$::unexpected > 0}]
}
