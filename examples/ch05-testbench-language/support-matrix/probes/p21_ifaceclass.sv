// interface class (pure virtual methods) and local/protected members
interface class printable;
  pure virtual function string str();
endclass
class acct implements printable;
  protected int bal;
  local int secret = 7;
  function int peek(); return secret; endfunction
  function new(int b); bal = b; endfunction
  virtual function string str(); return $sformatf("bal=%0d", bal); endfunction
endclass

module top;
  printable p; acct a;
  initial begin
    a = new(42); p = a;
    $display("%s", p.str());
    if (p.str() == "bal=42") $display("PROBE p21 PASS");
    else $display("PROBE p21 FAIL");
    $finish;
  end
endmodule
