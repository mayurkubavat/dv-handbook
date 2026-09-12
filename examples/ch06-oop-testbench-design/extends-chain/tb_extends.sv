// tb_extends.sv -- extending a class: constructors chain, methods hide or
// override.
//
// A derived constructor must reach its base's constructor first: with
// `super.new(...)` as its first statement, or implicitly with no arguments
// when it says nothing. A method redeclared in the derived class *hides*
// the base's version if neither is virtual -- a call through a base handle
// still runs the base body -- and *overrides* it if the base's is virtual.
class packet;
  int id;
  string kind;
  function new(int id_);
    id = id_; kind = "packet";
  endfunction
  function string describe();            // not virtual: hidden below
    return $sformatf("%s #%0d", kind, id);
  endfunction
  virtual function string tag();         // virtual: overridden below
    return "base";
  endfunction
endclass

class error_packet extends packet;
  int code;
  function new(int id_, int code_);
    super.new(id_);                      // first statement, explicitly
    kind = "error"; code = code_;
  endfunction
  function string describe();            // hides packet::describe
    return $sformatf("%s #%0d code=%0d", kind, id, code);
  endfunction
  virtual function string tag();         // overrides packet::tag
    return "derived";
  endfunction
endclass

class idle_packet extends packet;
  // No constructor: the implicit one calls super.new() with no arguments,
  // which is an error here because packet::new needs one. So it is given.
  function new(); super.new(0); kind = "idle"; endfunction
endclass

module tb_extends;
  packet       p;
  error_packet e;
  idle_packet  i;
  initial begin
    e = new(7, 42);
    i = new;
    p = e;                               // base handle to the derived object
    $display("through e: %s / tag %s", e.describe(), e.tag());
    $display("through p: %s / tag %s", p.describe(), p.tag());
    $display("idle: %s", i.describe());
    $finish;
  end
endmodule
