# usage: set design/top first
proc setup {file top args} {
  clear -all
  analyze -sv12 [file join [file dirname [info script]] $file]
  elaborate -top $top {*}$args
  clock clk
  reset -expression {rst}
}
proc with {engine limit body} {
  puts "--- engines: $engine, limit $limit"
  informal::set_engines {*}$engine
  set_prove_time_limit $limit
  uplevel 1 $body
}
