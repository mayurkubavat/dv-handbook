module top; typedef struct packed { logic [3:0] tag; logic [11:0] addr; } hdr_t; hdr_t h; logic [15:0] raw;
  initial begin h = '{4'hA, 12'h123}; raw = h;
    if (raw==16'hA123 && h.tag==4'hA) $display("PROBE i06a PASS"); else $display("PROBE i06a FAIL"); $finish; end
endmodule
