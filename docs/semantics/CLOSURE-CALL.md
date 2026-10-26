# `Closure::call`

Modules 182/268 invoke a selected core Closure with a temporary receiver and
scope, without allocating a bound copy. Supported sources include ordinary
Closures, named/function/method/`__invoke` captures, `Closure::fromCallable`
results, transformed fake bindings and finite Throwable getters. The pinned
routes are `zend_closures.c::ZEND_METHOD(Closure, call)`,
`zend_valid_closure_binding` and `zend_execute_API.c::zend_call_function`.

Module 428 collects ARRAY packs after an ordinary positional `newThis`, with a
direct positional prefix and named tail. Each pack resets its own named-order
check; integer keys add consecutive positional values even after an earlier
pack's named entries. API forwarding puts those positional values before named
extras and recomputes inner binding, default holes and the first remembered
inner error. Pack aliases are copied by value before reference-formal warnings;
forwarding allocates detached cells after any callback returns. The selected
Closure, receiver and already captured direct values survive later producer
writes. Completed history validates source-indexed delivery without keeping the
source arrays alive or rereading them; pooled literal facts constrain captured
entries. Expanded wrappers retain raw values and signature-consistent labels
while weak reception and body writes update separate inner arguments.

The selected Closure and evaluated values stay owned during ordinary, computed
and nullsafe method entry. Immediate simple-variable checks authenticate the
selection; later argument effects may replace those variables. Collection follows
source order; `RAW` keeps original values in positional-then-named forwarding
order. The no-pack route permits named `newThis` anywhere among named arguments
and excludes it from inner forwarding. A nullsafe null receiver
skips its arguments. Pending stages authenticate the actual call site, compiled
line, receiver and sent values.

Outer duplicate names and a positional entry after a named entry in the same
pack stop later producers, before API entry, with a caller-only Error trace.
After successful collection, receiver/scope binding and remembered inner-name
errors follow. Invalid scalar `newThis` fails before an inner-name error. Binding warnings run
next, suppress that error and return null after a normal handler; a throwing
handler unwinds its writes. Static wins first. A fake method requires a compatible
receiver before scope checks, then requires its exact selected function scope:
a subclass still cannot change a fake method's scope. This uses the actual
selected method owner, including object fallback, rather than a raw callable's
requested class. An unscoped fake function cannot acquire a user-class scope.
Exact internal scopes admit supported getters and dummy Closure-scope functions;
free-intrinsic internal scope changes remain warnings.

User bodies enter through the ordinary call machinery with temporary
lexical/called scope and receiver. Source captures retain their original binding
and share source static cells; a later ordinary invocation restores that binding.
The internal wrapper owns the original positional values and named labels/order,
independently of weak receive conversion and body writes. Defaults and created
source Closures retain genuine permission. Parameter diagnostics and traces use
the temporary function scope. A finite getter invokes its selected method on
the new receiver after argument/binding checks; it preserves the original capture
and produces its own count/name errors.

Reference formals receive isolated fresh cells after outer evaluation and binding,
in canonical forwarding order. Each warning runs **before** its cell is allocated.
A handler may change the caller or allocate intervening cells; normal continuation
wraps the frozen original value, while a throw creates no pending argument cell
and enters no body. Preparation authenticates actual distinct reference IDs,
bounds, reference registration, frozen values and exclusion from original owned
cells, without assuming contiguous allocation. The wrapper retains raw values.
Normal array copies preserve embedded references. The result task resolves a
returned reference without exposing its alias; the inner value remains demanded
when the outer result is unused.

Created user-class Closures use the exact selected method/import scope. A child
created inside a temporary dummy Closure scope copies the actual function,
call-site, lexical/called scope and new receiver in a durable certificate. Its
retired parent and old receiver add no owner. Nonstatic children and clones own
the new receiver; static children do not. REAL child clones copy their static
cells. Fake temporary `getCurrent` raises its ordinary Error; REAL temporary
`getCurrent` retains the separate source-only lifetime boundary recorded in
[CLOSURE-CURRENT-BINDING](CLOSURE-CURRENT-BINDING.md).

The [temporary fake-call ledger](../../coverage/semantics/temporary-fake-call-review.json)
keeps new source/state cuts and original failures separate. Historical REAL,
named-forwarding and cache repairs retain their own
[call](../../coverage/semantics/closure-call-review.json),
[argument](../../coverage/semantics/closure-call-arguments-review.json) and
[default-cache](../../coverage/semantics/closure-default-cache-review.json)
ledgers; none establishes complete core. The
[ARRAY-pack review](../../coverage/semantics/closure-call-array-pack-review.json)
keeps positional/COW, named-default/error and detached-reference cuts separate.
Unknown inner names retain the raw receiver/named argument trace after the saved
Closure retires. The
[argument-list review](../../coverage/semantics/closure-call-argument-list-review.json)
adds multiple-pack replay, mixed delivery and distinct outer versus inner error
priority. Packed `newThis`, Traversable delivery and direct call-time references
remain unsupported.
Further internal API capture, missing core internal bodies and the REAL
temporary-current lifetime decision remain required. Return verification remains
paused.
