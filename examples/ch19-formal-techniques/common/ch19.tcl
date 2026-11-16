# ch19.tcl -- procedures this chapter's InFormal scripts share. It
# loads the previous chapter's (`one`, `depth`, `expect_depth`,
# `full`) by path, on top of the book's `expect` and `finish`
# (examples/mk/informal.tcl), and names the directories of the RTL
# that other chapters own. That RTL is read where it stands; no file
# of another chapter is copied or edited.
set ::common19 [file dirname [file normalize [info script]]]
set ::ex       [file dirname [file dirname $::common19]]
source $::ex/ch18-formal-property-verification/common/proof.tcl
set ::rtl01 $::ex/ch01-what-is-dv/rtl
set ::rtl09 $::ex/ch09-temporal-properties/rtl
set ::chk09 $::ex/ch09-temporal-properties/fifo-checker
set ::rtl11 $::ex/ch11-architecture-to-verification/rtl
set ::ch18  $::ex/ch18-formal-property-verification

# design FILES TOP ARGS -- a new session: clear, read, elaborate,
# clock clk, reset on !rst_n. ARGS go to `elaborate` (parameters,
# -bbox_m). Every `one` in this chapter's scripts follows a `design`
# of its own, so that each report holds only the verdicts of the
# engine named above it, and no row left over from an earlier
# `prove` with another engine.
proc design {files top args} {
  clear -all
  analyze -sv12 {*}$files
  elaborate -top $top {*}$args
  clock clk
  reset -expression {!rst_n}
}

# mutant NAME FILE EDIT -- FILE with one sed edit applied, written to
# the work directory as NAME.sv; returns its path. A mutant is made
# when the script runs, from the file as it stands, so it cannot
# drift from the design it mutates.
proc mutant {name file edit} {
  set out [file join $::workdir $name.sv]
  set fd [open $out w]
  puts $fd "// $name.sv -- MUTANT of [file tail $file], made by sed\
 when the script runs."
  close $fd
  exec sed $edit $file >> $out
  # The edit must have matched: past its first line, the mutant is
  # not the file it came from. (cmp exits with status 0, and exec
  # raises no error, only when the two are the same.)
  if {![catch {exec sh -c "tail -n +2 '$out' | cmp -s '$file' -"}]} {
    error "mutant $name: the edit changed nothing"
  }
  return $out
}
