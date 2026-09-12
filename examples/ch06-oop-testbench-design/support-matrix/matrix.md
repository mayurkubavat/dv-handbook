| Construct | Icarus 13.0 | Verilator 5.030 |
|---|---|---|
| `extends` with an explicit `super.new(args)` | runs | runs |
| `extends` with the implicit `super.new()` | runs | runs |
| non-virtual method hidden, called through a base handle | runs | runs |
| virtual function through a base handle | wrong | runs |
| virtual task through a base handle | wrong | runs |
| virtual void function setting a property, base handle | wrong | runs |
| override calling `super.f()`, through a base handle | wrong | runs |
| virtual dispatch two levels deep, root and middle handles | wrong | runs |
| virtual call from a non-virtual base method (template) | wrong | runs |
| virtual dispatch across a level that does not override | wrong | runs |
| override declared without the `virtual` keyword | wrong | runs |
| virtual call through a base-typed property of another object | no build — Method name nesting is not supported yet. | runs |
| virtual call on a base-typed function argument | wrong | runs |
| virtual calls inside `fork ... join` | wrong | runs |
| `virtual class` with a `pure virtual` method | no build — syntax error | runs |
| `interface class` and `implements` | no build — syntax error | runs |
| one class implementing two interface classes | no build — syntax error | runs |
| `$cast` down the hierarchy, matching object | no run | runs |
| `$cast` down the hierarchy, mismatched object | no run | runs |
| `new src` through a base handle holding a derived object | no run | wrong |
| `clone()` as a virtual method constructing its own class | wrong | runs |
| parameterized class, type parameter | no build — syntax error | runs |
| parameterized class, value parameter | no build — syntax error | runs |
| parameterized class specialized twice | no build — syntax error | runs |
| class extending a specialized parameterized base | no build — syntax error | runs |
| static member of a specialization | no build — syntax error | runs |
| queue of base handles, iterated with a virtual call | no build — Sorry: Queue of type | runs |
| factory: static function returning a base handle | no build — syntax error | runs |
| singleton: static handle and static `get()` | no build — syntax error | runs |
| callback hook object with a virtual method | no build — Method name nesting is not supported yet. | runs |
| method called on a handle-typed property (composition) | no build — Method name nesting is not supported yet. | runs |
| handle identity: `==`, `!=`, `!= null` | no build — SORRY: Compare class handles not implemented | runs |

: What each open simulator does with the object-oriented constructs this chapter teaches, measured by running one probe per row with the flags the book's build uses and checking the printed values. Of 32 constructs, 3 run on both, 28 on Verilator only, 0 on Icarus only and 1 on neither. Regenerated from the probes on every run. {#tbl-ch06-support}
