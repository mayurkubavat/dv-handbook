// counter.h -- a SystemC model of the same counter, cycle-accurate at the pins.
#pragma once
#include <systemc.h>

SC_MODULE(Counter) {
  sc_in<bool>          clk;
  sc_in<bool>          rst_n;
  sc_in<bool>          en;
  sc_out<sc_uint<8>>   count;

  void step() {
    if (!rst_n.read())      count.write(0);
    else if (en.read())     count.write(count.read() + 1);
  }

  SC_CTOR(Counter) {
    SC_METHOD(step);
    sensitive << clk.pos() << rst_n.neg();   // async reset, like the RTL
  }
};
