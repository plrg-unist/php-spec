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

Module390 stages registered warning/deprecation callbacks for defined direct CVs
with initially untyped scalar values. Bool and decrement-null restore the captured
value even when the handler throws; nonnumeric/empty strings restore only on normal
return. An initially referenced target keeps its borrowed old cell after rebinding.
An initially plain CV detaches a reference wrapper created by the callback. Postfix
returns the prior scalar snapshot; prefix returns the restored value. Source lines,
fresh handler selection, supplied Throwable identity and real alias owners are checked
in the [focused ledger](../../coverage/semantics/incdec-warning-review.json).
The [restoration extension](../../coverage/semantics/incdec-restoration-review.json)
releases callback-installed objects and object-bearing arrays before the captured
scalar store. Destructors retain the old slot view; scalar writes are overwritten
afterward, including when a destructor throws. Replacement Throwables preserve
Previous. Borrowed cells add no owner, surviving wrapper aliases keep their
referents alive, and ordered child cleanup continues after a supplied throw.
Released arrays permit authenticated strict comparisons with literal scalars and
terminal isset; ordinary, nested and empty reads remain Unsupported. Late type-source
attachment, destructor rebinding/new owned payloads and replacement/destructor
exit retain explicit boundaries and native obligations. Wider update locations
remain partial.

[Named warning-handler exits](../../coverage/semantics/incdec-exit-review.json)
unwind the real handler frame and its locals before restoring the registry and
captured bool/decrement-null value. Strings skip restoration. Pending caller
operands survive handler cleanup, then retire before caller cleanup and shutdown;
catch/finally and interrupted result assignment are skipped while exit remains
pending. Borrowed old cells, genuine GLOBALS rebinding/unset, nested handlers,
registry replacement and request exit status preserve their distinct effects.
[Handler-local cleanup Throwables](../../coverage/semantics/incdec-exit-cancellation-review.json)
now cancel exit for the named, safe-restoration slice. Registry restoration and
captured bool/decrement-null commit precede the original caller throw; strings
retain writes. Catch/finally and subsequent code resume without delivering the
interrupted result or synthesizing Previous. Live borrowed cells, late peer
detachment, nested handlers, request status23 and nonthrowing parent-temporary
cleanup are validated by seven new and one repaired original plus 499 genuine SL
conditions at separate cuts. Unsafe restoring targets keep their native obligations
and named boundaries.

[Caller-temporary cleanup Throwables](../../coverage/semantics/incdec-parent-exit-cancellation-review.json)
now cancel pending exit after the warning helper finishes: bool/decrement-null
restore their capture while strings skip the store. Main/function expression
statements inside bounded blocks/try/catch/finally recover their ordered source
control without retired operand or prior finally-exception owners. Existing eager
cleanup drains before caller throw search; destructor writes and request status23
survive without repeating the scalar store or registry restoration. Pending finally
outcomes retire before unfinished binary holders, which follow source lifetime
order while each container retains its own child order. Seven new and one repaired source agree; 342 author
and 341 independent genuine SL conditions retain separate cuts. The repaired old
parent control/state expectation is maintained without renewing older counts.
Wider owning call builders, returns/loops/iterators and unsafe restoration remain
required; unknown cleanup ordering stops before observable release.

[Owning invokable warning callbacks](../../coverage/semantics/incdec-callback-exit-review.json)
now stage selected receiver release, one registry restore/drop decision, then raw
handler release before helper completion. Retained registry or external owners
prevent destruction. Last-owner destruction may mutate or clear the registry;
that result survives and the dead handler is not restored again. A root-free
historical certificate retains source authority without reviving callback owners.
Bool/decrement-null restore their safe capture after destruction, including a
supplied callback-destructor throw; strings skip the store. Borrowed old cells
remain distinct from rebound callers. Pending ownership transfers once into
caller throw search, preserving identity, Previous and request status 23.
Seven new and one repaired source agree; 299 author and 269 independent genuine
SL conditions retain separate cuts. The repaired old callable-owner expectation
is maintained without renewing historical counts. Broader callback-destructor
exits, unsafe targets and wider callbacks/control remain required.

[Owning handler-local cleanup Throwables](../../coverage/semantics/incdec-callback-exit-cancellation-review.json)
now cancel warning-handler exit while callback-owner release continues. The real
pending Throwable moves into and out of each selected/raw release operation once;
the saved-handler registry decision still happens once. Surviving registry or peer
owners prevent forced destruction. Bool/decrement-null restore their safe capture
after release; strings retain writes. A secondary callback-destructor Throwable
keeps the first as Previous. Caller catch/finally, late-peer detachment, old borrowed
cells and request status 23 survive without result delivery. Five new sources,
383 author and 264 independent genuine SL conditions retain separate tested cuts.
The original Unsupported baseline remains zero; older campaigns are not renewed.

[Raw callback-destructor exits](../../coverage/semantics/incdec-callback-destructor-exit-review.json)
now unwind a direct entered destructor and finish its real raw-handler release
before the warning helper completes. The saved caller operands remain owned until
safe bool/decrement-null capture restoration or string store skip. A later integer
exit replaces body exit 23; string exit retains the request status. Registry clearing
or replacement survives; weak-reference probes observe callback retirement before
caller-temporary cleanup.
The first cut excludes a pending user Throwable, destructor local cells and owned
pending operands. Its authentic pending-Throwable control stopped before caller cleanup;
that Unsupported result retains zero agreement credit. Four new originals and 240 author
plus 313 independent genuine SL conditions retain their actual cuts and original
failures. Nested destructor exits, owning cleanup,
unsafe targets and wider callback/control forms remain required.

[Pending-Throwable callback-destructor exits](../../coverage/semantics/incdec-callback-destructor-exit-pending-review.json)
now retain a supplied Throwable owner through raw-handler release, helper completion
and caller-temporary cleanup, then release that owner before shutdown. This models the
internal exit's previous owner without creating a user-visible Exit or changing
the supplied Throwable's Previous. Bool/decrement-null restore their safe capture
before parent cleanup; strings skip the store. Last-owner destruction observes the
restored value, and its later writes survive. Three new and one repaired original
agree; 440 author and 170 independent genuine SL premises retain their exact cuts.
The former refusal fixture delegates the accepted original without renewing old
counts. Admission requires a MAIN caller and a direct destructor scope without local
cells, held roots or owned pending operands, plus no retained source-end controls.
Nested/outer contexts, parent/cause cleanup throws or exits,
unsafe targets and wider routes remain required.

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

For distinct initially plain CVs, `%=` saves a fractional-float left conversion
before its deprecation and reads the live quiet integer RHS after callback return.
Only a successful remainder replaces the original target; a supplied throw or
live zero preserves callback writes and any late alias. The latter produces the
ordinary original-line `DivisionByZeroError` before any detachment.
[Modulo-assignment evidence](../../coverage/semantics/modassign-warning-review.json)
retains three source agreements and 362 focused SL premises; wider operands,
targets and lifecycle forms remain partial.

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
