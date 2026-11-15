# proof.tcl -- procedures this chapter's InFormal scripts share, on
# top of the book's own `expect` and `finish` (examples/mk/informal.tcl).
set ::common [file dirname [info script]]
set ::ch09   $::common/../../ch09-temporal-properties

# one ENGINE LIMIT ARGS -- one `prove` with one engine selected and
# the time limit set, under a heading that names both. The limit is
# for each property, and it is printed because an `undetermined` row
# means "no verdict within this limit" and nothing else.
proc one {engine limit args} {
  informal::set_engines $engine
  set_prove_time_limit $limit
  puts "--- $engine, limit $limit for each property"
  prove {*}$args
}

# depth NAME -- the depth the last `prove` reported for a property,
# or -1 when it reported none. NAME is a full name or, as in `expect`,
# the last part of one. The shell has no command for a depth; the
# number is read from the session, which the tool prints as JSON.
proc depth {name} {
  foreach full [get_property_list] {
    if {$full eq $name || [string match "*.$name" $full]} {
      set json [informal::session]
      set at  [string first "\"name\": \"$full\"," $json]
      set end [string first "\"source\":" $json $at]
      if {[regexp {"depth": ([0-9]+)} [string range $json $at $end] \
           -> d]} {
        return $d
      }
      return -1
    }
  }
  error "depth: no property named $name"
}

# expect_depth N NAME ... -- each named property must have been
# reported at depth N; like `expect`, a miss prints an "unexpected:"
# line, which fails the run.
proc expect_depth {want args} {
  foreach name $args {
    set got [depth $name]
    if {$got != $want} {
      puts "unexpected: $name is at depth $got, expected $want"
      incr ::unexpected
    }
  }
}

# full NAME -- the full name of the one property NAME selects.
proc full {name} {
  foreach f [get_property_list] {
    if {$f eq $name || [string match "*.$name" $f]} {return $f}
  }
  error "full: no property named $name"
}
