// packed and unpacked fixed arrays
module top;
  logic [3:0][7:0] packed4;         // 32 bits, addressable per byte
  logic [7:0] mem [0:3];            // unpacked
  int grid [2][3];
  int sum;
  initial begin
    packed4 = 32'hDEADBEEF;
    foreach (mem[k]) mem[k] = packed4[k];
    foreach (grid[r,c]) grid[r][c] = r*10 + c;
    sum = 0; foreach (grid[r,c]) sum += grid[r][c];
    $display("packed4[3]=%h mem[0]=%h $size(mem)=%0d $bits(packed4)=%0d sum=%0d",
             packed4[3], mem[0], $size(mem), $bits(packed4), sum);
    if (packed4[3] == 8'hDE && mem[0] == 8'hEF && sum == 36) $display("PROBE p02 PASS");
    else $display("PROBE p02 FAIL");
    $finish;
  end
endmodule
