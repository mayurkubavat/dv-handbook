// tb_abstract.sv -- an abstract class, and an interface class.
//
// A `virtual class` cannot be constructed; it exists to be extended, and
// a `pure virtual` method inside it is a promise every concrete subclass
// must keep. An `interface class` is a set of such promises with no data
// and no bodies at all, and a class may implement several of them while
// extending only one base. The choice is that difference: extend for
// shared state and shared code, implement for a shared contract.
virtual class shape;                      // abstract: has data, no area
  string name;
  function new(string n); name = n; endfunction
  pure virtual function int area();
endclass

interface class printable;               // a contract, nothing else
  pure virtual function string str();
endclass
interface class scalable;
  pure virtual function void scale(int k);
endclass

class square extends shape implements printable, scalable;
  int side;
  function new(int s); super.new("square"); side = s; endfunction
  virtual function int area(); return side * side; endfunction
  virtual function string str();
    return $sformatf("%s side=%0d area=%0d", name, side, area());
  endfunction
  virtual function void scale(int k); side = side * k; endfunction
endclass

module tb_abstract;
  shape     sh;
  printable pr;
  scalable  sc;
  square    sq;
  initial begin
    sq = new(3);
    sh = sq; pr = sq; sc = sq;            // one object, three contracts
    $display("area through the abstract base: %0d", sh.area());
    sc.scale(2);
    $display("after scale(2) through the interface class: %s", pr.str());
    $finish;
  end
endmodule
