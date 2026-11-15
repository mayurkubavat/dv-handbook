// Saturating counter with an enable, used by the FPV flow tests.
// It counts 0..9 and stops; `wrap` is never set.
module counter (
    input  logic       clk,
    input  logic       rst_n,
    input  logic       en,
    output logic [3:0] q,
    output logic       done
);
    logic [3:0] nxt;
    logic       wrap;
    assign nxt  = q + 4'd1;
    assign done = (q == 4'd9);
    assign wrap = 1'b0;
    always_ff @(posedge clk or negedge rst_n)
        if (!rst_n)          q <= 4'd0;
        else if (en && !done) q <= nxt;
endmodule
