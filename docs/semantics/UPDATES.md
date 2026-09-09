# Update expressions

## Increment and decrement

The four pre/post increment/decrement forms use checked read/write descriptors.
Their targets evaluate dynamic names and dimension keys once, retain delayed
variable/reference operands, then acquire the writable location. Missing names
and explicit array keys warn and initialize to null; `[]` appends a null slot
without an undefined-key warning. Intermediate dimensions use the same read/write
mode. Computed-name fetch diagnostics use their own compiler line; direct compiled
variables use the containing dimension instruction line. Copy-on-write separation
counts the captured inputs as owners.

Increment/decrement writes the acquired location. Prefix expressions return the
new value; postfix expressions return a value snapshot from before the update.
Neither result retains a reference to the modified cell. Integer overflow produces
binary64; numeric strings follow the numeric scanner, while nonnumeric strings
use byte-wise carry or the pinned no-effect/deprecation behavior. Null and boolean
updates retain their distinct results and warnings. Arrays throw a TypeError.

String dimensions validate the key before rejecting increment/decrement; nested
string dimensions retain the separate nested-array error. Generic dimension
fetches preserve the reference-wrapper distinction in
[REFERENCE-WRAPPERS.md](REFERENCE-WRAPPERS.md). Compiler errors for temporary,
call-return and nullsafe targets precede runtime execution. Constant-expression
preparation stops at each update node; ordinary compilation later traverses its
target with read/write access.

The executable scope is local variables and dimensions of the currently admitted
scalar/array forms. Objects, typed references/properties and environment-owned
variables need their separate contracts. In the current global execution context,
direct `$this` fetching throws before its dimension keys are evaluated. Computed
reads of the name `this` use ordinary missing-variable behavior; computed updates
throw the distinct rebinding error after normal name/key preparation. Direct
assignment, reference rebinding and unset of `$this` are compiler errors. Computed
plain writes/reference binding/unset and parser-folded concatenation names retain
their existing explicit boundaries, pending their separate access protocols.
Coalescing assignment still requires its separate quiet-read and memoized-write
protocol.

The source/state gate checks exact diagnostics, strict result types, alias and
copy behavior, captured keys/names, and small-budget resumption with valid heaps
and unchanged compiled pools/code. Source compilation checks read/write roles,
phase ordering and diagnostic lines independently of runtime execution.


## Compound assignment

The twelve arithmetic, shift, bitwise and concatenating assignment forms prepare
the target before evaluating the RHS. Names and keys are captured once; delayed
CV/reference reads retain their separate timing. Direct CV assignment reads its
RHS before fetching the target. Dynamic-name and dimension assignment acquire the
writable target before delayed RHS CV reads, with the existing self-assignment
exception for dimensions. Eager RHS expressions keep their own evaluation order.

Missing writable slots warn and initialize to null. Intermediate dimensions use
generic read/write fetching; final DIM_OP retains its own false conversion and
string-offset errors. A delayed DIM_OP reuses the captured target opcode line for
operator diagnostics and delayed RHS reads. Compiler traversal retains its final context after
RHS compilation, and dynamic-name fetching retains its own earlier line.

Array `+=` has a same-table no-op and an in-place union path with separation before
singleton-reference inspection. Results are ordinary values: assigning an array
result preserves copy-on-write and genuine shared reference entries. Other values
use the pinned numeric/string conversions, overflow, precision warnings and
operator-specific errors. Power evaluation uses the existing pure binary64/libm
specification helpers.

All twelve nodes stop constant preparation without traversing their children;
ordinary compilation then visits the target and RHS in order. Direct/literal
`$this` compound assignment is compile-valid, unlike ordinary rebinding. In the
current global source context its eager FETCH_THIS throws before keys or RHS;
computed-name fetching remains delayed. Invalid RHS syntax/compile contexts are
reported before any runtime execution.

`compound.py` and `compound_compiler.py` bind original programs, prepass/static
phase controls, diagnostic lines, type pairs, alias/copy behavior and resumed
execution. This activation covers compound forms over current scalar/array values.
Remaining ordinary binary operators, casts, object/typed locations, coalescing assignment and
parser-folded concatenation variable names remain separate source obligations.
