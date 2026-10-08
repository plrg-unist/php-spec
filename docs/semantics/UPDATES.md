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

Stringable `.=` converts the left value before dereferencing the selected RHS
slot. A defined direct RHS CV is borrowed and follows callback rebinding; an
initially undefined read keeps its warned null value, while a later unset is a
quiet empty string. Evaluated temporary values and reference-return cells retain
their actual owners through the final store, then release before outer operands.
An initially non-reference root self CV casts once and reuses those bytes;
reference self CVs follow the late RHS read. The destination pointer is selected
before conversion: a later reference alias does not change whether the final
write detaches the CV slot or writes the originally dereferenced reference cell.
The expression returns the combined string value independently of later writes.
The [focused evidence](../../coverage/semantics/compound-string-live-rhs-review.json)
also checks cleanup when either cast throws. Broader borrowed destination retirement
retains its separate boundary.

Literal named-class/static-property `.=` also retains the destination selected
before conversion. A plain slot detaches an alias created during a callback; an
initial reference writes its original cell after rebinding. Typed nonstring stores
verify the final value and return that converted result. Initial-string fast paths
skip that verification, preserving actual late type sources and retained constraints
on detached aliases. Source-bound history records certify these facts without
adding owners. The [static evidence](../../coverage/semantics/static-compound-string-review.json)
separates its new originals from earlier compound checks.

Ordinary-method `self`, `parent` and `static` selectors retain the actual method
lexical/called class in nonowning ENTRY metadata before conversion. The final
write uses that selection after nested callbacks; instance and scoped-parent
forwarding preserve the same destination. Dynamic class expressions resolve once
before RHS evaluation and retain that class after selector mutation. Temporary
object selectors retire before the RHS; the selected plain slot/reference and
typed final result follow the same static store rules. Ordinary scalar concat
restores its base without creating conversion history. Computed static-property
name CVs are read after eager RHS effects; evaluated name values/reference cells
retain their earlier selection. Source-bound tasks keep actual evaluated name
and RHS owners through queued class initialization; CVs remain borrowed. They
transfer the resolved property
to the same conversion/store protocol. Property fetches retain their buffered
opcode line, while initializer failures report the initializer source. Stringable
property-name callbacks, keyword scopes entered through Closure/fromCallable or
other callable wrappers, and registered-handler missing-RHS continuations remain
outside this slice.

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
