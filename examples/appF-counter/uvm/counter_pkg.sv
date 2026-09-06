// counter_pkg.sv -- the smallest UVM test that still checks something.
// There is no agent yet; the test drives the interface directly. Later
// chapters grow this into a full driver / monitor / scoreboard environment.
package counter_pkg;
  import uvm_pkg::*;
  `include "uvm_macros.svh"

  class counter_smoke_test extends uvm_test;
    `uvm_component_utils(counter_smoke_test)

    virtual counter_if vif;

    function new(string name = "counter_smoke_test",
                 uvm_component parent = null);
      super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      // The top module publishes the interface handle in the config database.
      if (!uvm_config_db#(virtual counter_if)::get(this, "", "vif", vif))
        `uvm_fatal("NOVIF", "counter_if not found in uvm_config_db")
    endfunction

    task run_phase(uvm_phase phase);
      phase.raise_objection(this);
      vif.rst_n = 0; vif.en = 0;
      repeat (2) @(posedge vif.clk);
      vif.rst_n = 1;
      vif.en = 1;
      repeat (10) @(posedge vif.clk);
      vif.en = 0;
      @(posedge vif.clk);
      if (vif.count == 10)
        `uvm_info("PASS", $sformatf("count = %0d", vif.count), UVM_LOW)
      else
        `uvm_error("FAIL", $sformatf("count = %0d, expected 10", vif.count))
      phase.drop_objection(this);
    endtask
  endclass
endpackage
