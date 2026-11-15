clear -all
analyze -sv12 /home/user/dv-handbook/examples/ch11-architecture-to-verification/rtl/dma_v1.v
elaborate -top dma_engine
clock PCLK
reset -expression {!PRESETn}
set_prove_time_limit 20s
assert -name ArHeld {ARVALID && !ARREADY |=> ARVALID}
assert -name AwHeld {AWVALID && !AWREADY |=> AWVALID}
assert -name WHeld {WVALID && !WREADY |=> WVALID}
assert -name ArStable {ARVALID && !ARREADY |=> $stable(ARADDR)}
prove -all
