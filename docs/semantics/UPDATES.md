# Increment and decrement

The four pre/post increment/decrement forms use checked read/write descriptors.
Their targets evaluate dynamic names and dimension keys once, retain delayed
variable/reference operands, then acquire the writable location. Missing names
and explicit array keys warn and initialize to null; `[]` appends a null slot
without an undefined-key warning. Intermediate dimensions use the same read/write
mode. Copy-on-write separation counts the captured inputs as owners.

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
Compound and coalescing assignments are
separate protocols and are not supplied by this activation.

The source/state gate checks exact diagnostics, strict result types, alias and
copy behavior, captured keys/names, and small-budget resumption with valid heaps
and unchanged compiled pools/code. Source compilation checks read/write roles,
phase ordering and diagnostic lines independently of runtime execution.
