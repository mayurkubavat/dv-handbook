// a method called on a handle-typed property from inside another class's
// method (item.f() where item is a property) -- the shape every driver,
// monitor and scoreboard uses; no virtual dispatch involved
class pkt; function int f(); return 3; endfunction endclass
class holder; pkt item;
  function new(); item = new; endfunction
  function int call(); return item.f(); endfunction endclass
module top; holder h;
  initial begin h = new;
    $display("f=%0d", h.call());
    if (h.call() == 3) $display("PROBE o41 PASS");
    else $display("PROBE o41 FAIL"); $finish; end
endmodule
