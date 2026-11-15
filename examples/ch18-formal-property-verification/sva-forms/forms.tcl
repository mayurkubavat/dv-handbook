# forms.tcl -- try every probe of forms.list and print what the tool
# did with it, one line a probe, fields separated by tabs:
#
#   row  key  kind  label  accepted  message  good  bad  depth
#
# `good` and `bad` are the verdicts on the property that holds and on
# the one that does not; `depth` is the depth reported with the last
# verdict, or -1.
#
# Each property gets a session of its own, so that one form cannot
# change the model another is judged on. forms.py makes the table.
set here [file dirname [info script]]
source $here/../common/proof.tcl

# fresh FILE TOP -- an empty session with one design in it.
proc fresh {file top} {
  clear -all
  analyze -sv12 $::here/$file
  elaborate -top $top
  clock clk
  reset -expression {rst}
  set_prove_time_limit 3s
}

# verdict ENGINE -- prove everything; the status of the first assert
# or cover, "none" when the session has no such property, and the
# tool's message when the status is error.
proc verdict {engine} {
  informal::set_engines $engine
  prove -all
  set ::message ""
  set ::depth -1
  foreach name [get_property_list] {
    set status [get_status $name]
    if {$status eq "unprocessed"} continue      ;# an assumption
    set ::depth [depth $name]
    if {$status eq "error"} {
      regexp {"message": "([^"]*)"} [informal::session] -> ::message
    }
    return $status
  }
  return none
}

# check KIND TEXT ENGINE -- add one property by command and prove it;
# "refused" when the command itself is an error.
proc check {kind text engine} {
  if {[catch {$kind -name p $text} ::message]} {return refused}
  return [verdict $engine]
}

proc group {title} {puts "group\t$title"}

proc p {args} {
  array set f $args
  set ::message ""
  set ::depth -1
  set engine informal-kind
  set accepted yes
  set good -
  set bad -
  switch $f(kind) {
    live - fair {set engine informal-ic3}
  }
  switch $f(kind) {
    assert - live {
      fresh probe.sv probe; set good [check assert $f(good) $engine]
      fresh probe.sv probe; set bad  [check assert $f(bad)  $engine]
    }
    cover {
      fresh probe.sv probe; set good [check cover $f(good) $engine]
      fresh probe.sv probe; set bad  [check cover $f(bad)  $engine]
    }
    refuse {
      fresh probe.sv probe
      set accepted [check assert $f(good) $engine]
    }
    assume - fair {
      fresh probe.sv probe
      if {[catch {assume -name m $f(good)} ::message]} {
        set accepted refused
      } else {
        set good [check assert $f(bad) $engine]
        fresh probe.sv probe
        set bad [check assert $f(bad) $engine]
      }
    }
    rtl {
      fresh where.sv $f(good); set good [verdict $engine]
      fresh where.sv $f(bad);  set bad  [verdict $engine]
    }
    dropped {
      fresh where.sv $f(good)
      set accepted [verdict $engine]
    }
  }
  puts [join [list row $f(key) $f(kind) $f(label) $accepted $::message \
                   $good $bad $::depth] "\t"]
}

source $here/forms.list
finish
