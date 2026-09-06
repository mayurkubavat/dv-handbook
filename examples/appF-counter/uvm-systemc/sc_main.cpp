// sc_main.cpp -- UVM-SystemC: the same smoke test as counter_pkg.sv, in C++.
// UVM-SystemC mirrors the SystemVerilog class library; compare the phases and
// the objection calls with counter_smoke_test in the UVM example.
#include <systemc.h>
#include <uvm>
#include "../systemc/counter.h"

// The interface handle is passed through the config database, as in SV.
struct CounterPins {
  sc_signal<bool>* rst_n;
  sc_signal<bool>* en;
  sc_signal<sc_uint<8>>* count;
  sc_clock* clk;
};

class counter_smoke_test : public uvm::uvm_test {
 public:
  UVM_COMPONENT_UTILS(counter_smoke_test);
  CounterPins* pins = nullptr;

  explicit counter_smoke_test(uvm::uvm_component_name name)
      : uvm::uvm_test(name) {}

  void build_phase(uvm::uvm_phase& phase) override {
    uvm::uvm_test::build_phase(phase);
    if (!uvm::uvm_config_db<CounterPins*>::get(this, "", "pins", pins))
      UVM_FATAL("NOPINS", "CounterPins not found in uvm_config_db");
  }

  void run_phase(uvm::uvm_phase& phase) override {
    phase.raise_objection(this);
    *pins->rst_n = false; *pins->en = false;
    wait(20, SC_NS);
    *pins->rst_n = true;
    *pins->en = true;
    wait(100, SC_NS);
    *pins->en = false;
    wait(10, SC_NS);
    if (pins->count->read() == 10)
      UVM_INFO("PASS", "count = 10", uvm::UVM_LOW);
    else
      UVM_ERROR("FAIL", "count != 10");
    phase.drop_objection(this);
  }
};

int sc_main(int, char**) {
  sc_clock clk("clk", 10, SC_NS);
  sc_signal<bool> rst_n, en;
  sc_signal<sc_uint<8>> count;

  Counter dut("dut");
  dut.clk(clk); dut.rst_n(rst_n); dut.en(en); dut.count(count);

  CounterPins pins{&rst_n, &en, &count, &clk};
  uvm::uvm_config_db<CounterPins*>::set(nullptr, "*", "pins", &pins);

  uvm::run_test("counter_smoke_test");
  return 0;
}
