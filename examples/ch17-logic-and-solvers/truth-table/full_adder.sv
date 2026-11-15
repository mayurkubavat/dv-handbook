// full_adder.sv -- one column of an adder, as five gates.
module full_adder (
  input  logic a, b, cin,
  output logic sum, cout
);
  logic p, g, t;
  assign p    = a ^ b;        // the column propagates a carry
  assign sum  = p ^ cin;
  assign g    = a & b;        // the column generates a carry
  assign t    = p & cin;
  assign cout = g | t;
endmodule
