clear -all
analyze -sv12 /home/user/dv-handbook/examples/ch03-digital-design/rtl/top.sv /home/user/dv-handbook/examples/ch03-digital-design/rtl/datapath.sv /home/user/dv-handbook/examples/ch03-digital-design/rtl/sync2.sv /home/user/dv-handbook/examples/ch03-digital-design/rtl/regblock.sv
elaborate -top top
clock bclk
clock cclk -factor 3
set_prove_time_limit 20s
cover -name c_any {1'b1}
prove -all
