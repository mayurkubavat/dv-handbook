// hs_bind.sv -- the handshake checker of this chapter, attached to
// the sink.
bind hs_sink hs_check u_hs (.clk, .rst_n, .valid, .ready, .data);
