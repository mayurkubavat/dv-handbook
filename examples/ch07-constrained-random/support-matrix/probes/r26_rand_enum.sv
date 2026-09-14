// rand enum with a constraint excluding one member: IDLE never appears
class pkt; typedef enum bit [1:0] {IDLE, RD, WR, RMW} op_t; rand op_t op;
  constraint c { op != IDLE; } endclass
module top; pkt p; int ok, nrd, nwr, nrmw;
  initial begin p = new; ok = 1; nrd = 0; nwr = 0; nrmw = 0;
    for (int i = 0; i < 60; i++) begin
      if (p.randomize() != 1) ok = 0;
      case (p.op) pkt::RD: nrd++; pkt::WR: nwr++; pkt::RMW: nrmw++;
        default: ok = 0; endcase end
    $display("rd=%0d wr=%0d rmw=%0d", nrd, nwr, nrmw);
    if (ok && nrd > 0 && nwr > 0 && nrmw > 0) $display("PROBE r26 PASS");
    else $display("PROBE r26 FAIL"); $finish; end
endmodule
