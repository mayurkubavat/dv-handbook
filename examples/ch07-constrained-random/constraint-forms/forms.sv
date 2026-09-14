// forms.sv -- one small class per constraint form. Each class constrains
// one thing and nothing else, so that what the testbench prints for it
// is the effect of that form alone.
class c_inside;                       // membership in a set of ranges
  rand bit [7:0] a;
  constraint c { a inside {[10:19], 42, [200:203]}; }
endclass

class c_relation;                     // a relation between two variables
  rand bit [7:0] lo, hi;
  constraint c { lo < hi; hi - lo <= 8'd4; }
endclass

class c_dist_assign;                  // := weights each value
  rand bit [3:0] a;
  constraint c { a dist { [0:3] := 1, 9 := 1 }; }
endclass

class c_dist_divide;                  // :/ shares one weight over a range
  rand bit [3:0] a;
  constraint c { a dist { [0:3] :/ 1, 9 := 1 }; }
endclass

class c_implication;                  // if s then v is zero
  rand bit       s;
  rand bit [7:0] v;
  constraint c { s -> v == 0; }
endclass

class c_ifelse;                       // two regimes, chosen by mode
  rand bit       mode;
  rand bit [7:0] a;
  constraint c { if (mode) a > 200; else a < 10; }
endclass

class c_foreach;                      // every element, and a relation
  rand bit [3:0] x[4];
  constraint c { foreach (x[i]) x[i] inside {[1:8]};
                 foreach (x[i]) if (i > 0) x[i] > x[i-1]; }
endclass

class c_solve_before;                 // solve s first: s is 0 or 1 alike
  rand bit       s;
  rand bit [7:0] v;
  constraint c { s -> v == 0; solve s before v; }
endclass

class c_soft;                         // a default an inline call overrides
  rand bit [7:0] a;
  constraint c { soft a == 5; }
endclass

class c_unique;                       // all different
  rand bit [1:0] x[3];
  constraint c { unique {x}; }
endclass
