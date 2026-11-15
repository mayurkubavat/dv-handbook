// resp_bind.sv -- attaches the checker to every responder.
bind responder resp_check chk (.clk, .rst_n, .req, .gnt);
