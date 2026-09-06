// sc_main.cpp -- the SystemC testbench: clock, stimulus, and a self-check.
#include "counter.h"
#include <iostream>

int sc_main(int, char**) {
  sc_clock            clk("clk", 10, SC_NS);
  sc_signal<bool>     rst_n, en;
  sc_signal<sc_uint<8>> count;

  Counter dut("dut");
  dut.clk(clk); dut.rst_n(rst_n); dut.en(en); dut.count(count);

  rst_n = false; en = false;
  sc_start(20, SC_NS);                 // two cycles in reset
  rst_n = true;

  en = true;  sc_start(100, SC_NS);    // count for 10 cycles
  en = false; sc_start(30, SC_NS);     // pause for 3
  en = true;  sc_start(50, SC_NS);     // count 5 more
  en = false; sc_start(10, SC_NS);

  const int expected = 15;
  if (count.read() == expected) {
    std::cout << "PASS: counter reached " << count.read() << std::endl;
    return 0;
  }
  std::cout << "FAIL: count=" << count.read()
            << " expected=" << expected << std::endl;
  return 1;
}
