clear -all
analyze -sv12 [file dirname [info script]]/imm.sv
elaborate -top imm
clock clk
reset -expression {rst}
prove -all
puts "session: [informal::session]"
