// An array declared inside a generate block. The registers it becomes are
// named `lane[0].mem[3]`, and a parser that split the name at the first
// bracket pointed every one of them at the module header.
module generate_block_array (input logic wclk, rclk, input logic [1:0] wa, ra,
               input logic [7:0] wd, output logic [7:0] rd0, rd1);
  for (genvar l = 0; l < 2; l++) begin : lane
    logic [7:0] mem [0:3];
    logic [7:0] r;
    always_ff @(posedge wclk) mem[wa] <= wd;
    always_ff @(posedge rclk) r <= mem[ra];
  end
  assign rd0 = lane[0].r;
  assign rd1 = lane[1].r;
endmodule
