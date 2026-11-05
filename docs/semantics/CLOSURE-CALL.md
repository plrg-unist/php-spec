# `Closure::call`

Modules 182/268 retain the selected core Closure and its arguments. Nongenerator
bodies use a temporary receiver/scope without a bound copy. Their sources include ordinary
Closures, named/function/method/`__invoke` captures, `Closure::fromCallable`
results, transformed fake bindings and finite Throwable getters. The pinned
routes are `zend_closures.c::ZEND_METHOD(Closure, call)`,
`zend_valid_closure_binding` and `zend_execute_API.c::zend_call_function`.

Module 428 collects ARRAY argument lists, including the fixed `newThis` slot.
The receiver may arrive as an integer-keyed value, a named pack entry or a later
direct named send. Earlier named extras do not occupy that fixed slot; once it
is filled, later integer values forward to the inner function. Receiver capture
is separate from canonical forwarded values and survives source-cell replacement.
The list permits a direct positional prefix and named tail. Each pack resets its
own named-order check; integer keys add consecutive positional values even after an earlier
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

User nongenerator bodies enter through the ordinary call machinery with temporary
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

Real user Generator Closures use a separate copied-object branch for admitted
compiled literal calls and ordinary user-class receivers. Actual API roots hold
source/copy/first/raw values before clone rules duplicate captures/statics.
Reference-formal warnings run after that copy and before fresh-cell allocation,
so callback writes to the original cannot change an isolated copied static cell.
Shared wrappers remain shared. The Gen frame owns its copy with no API wrapper;
a used retval stays in one explicit continuation through source finalizers.
Warning traces have an internal handler header followed by the raw Closure::call
frame; that API frame disappears before later Gen body execution. Native5/source5
and private433 retain their distinct cuts; six reached fronts pass 625 custom/655
reported checks.
Computed/packed calls, other producer/receiver forms and no-Gen receive/callback
or mapping errors remain partial. [Copy review](../../coverage/semantics/generator-call-copy-review.json),
[reference review](../../coverage/semantics/generator-call-reference-review.json).

Admitted fake user-method Generator calls also allocate a distinct copy, keeping
the original method selection as nonowning history. Their new receiver must have
the exact declaring class, and their method static table stays shared. The copy
uses the existing API argument, fresh-reference and used/ignored result tasks;
its This survives through CLOSED and retires before the Gen cache. getCurrent
continues to reject the fake function. Ordinary ARRAY-capture calls select the
existing call handler. Native4/source4/private433 retain distinct cuts;
five reached fronts pass 633 custom/658 reported checks. Other receiver/binding/call forms and
abrupt receive paths remain partial.
[Fake-copy review](../../coverage/semantics/generator-fake-call-copy-review.json).

Variable/dynamic string first-class conversion rejects a nonstatic method before
evaluating later Closure::call arguments. The caller-aware fromCallable(string)
API can instead retain compatible This and authentic private selection; this is
a FROMCALLABLE source, not a STRING capture. I95 validates finite bound-source
chains and makes consumed Gen history a fallback to unavailable live lookup.
Three current native/source controls agree; four reached fronts pass
609 custom/629 reported checks.
At the I95 cut, literal/constant-folded capture had no new positive validation;
I96 below covers its separate compiler route. Wider binding/receive contexts remain partial.
[Bound-source review](../../coverage/semantics/generator-fake-string-call-review.json).

Literal full-name first-class capture can take the compiler's static-method-init
route and retain compatible This; variable-string rejection is unchanged. I96
routes admitted non-first-class STRING call consumers through the existing API.
A failed static binding has not copied arguments into a callee: SOURCE/FIRST/RAW
are the real owners and receiver/SENT are borrowed preparation. On normal return
or a handler throw, ordered jobs release newThis then raw arguments before the
selected Closure; real pending THROW_SEARCH remains protected during destructors.
Four current native/source controls agree; five reached fronts pass
516 custom/541 reported checks. Wider binding, callback and receive contexts
remain partial.
[Folded-call review](../../coverage/semantics/generator-folded-string-call-review.json).

I97 checks normal Fiber suspension during copied reference forwarding. The copy
already exists while the warning handler runs, but its Gen frame does not.
The saved API cursor owns source/copy/newThis/raw values independently of root
CVs. With the seed retired, a static cell owned only by the real Closure is
copied; fake method statics remain shared. Continuation wraps the original raw snapshot,
not a later root alias value. Native3/source3 and four reached fronts pass
553 custom/573 reported checks at distinct cuts on unchanged semantics. Aborts
during copied reference warnings and no-Gen receive/mapping errors retain their
limits.
[Warning Fiber review](../../coverage/semantics/generator-call-warning-fiber-review.json).

I98 follows an owning handler retval into its normal destructor before reference
wrapping. Existing cleanup records and the actual emitting caller retain the
already allocated copy and raw values during a Fiber park. Root reentry preserves
the independent real static copy; the fake-method control keeps Token in both a
retval property and the API snapshot until normal cleanup. Native2/source2 and
three reached fronts pass 459 custom/474 reported checks at distinct cuts on
unchanged semantics, with no state failures or retries. Trace expansion,
handler/destructor throws and no-Gen receive errors remain partial.
[Warning retval review](../../coverage/semantics/generator-call-warning-retval-review.json).
The [joined review](../../coverage/semantics/generator-call-series-current-review.json)
records strict433, four source comparisons and 187 custom/192 reported ownership
checks while preserving every original cut and zero-credit failure.

I99 admits PHP throws while copied reference warnings are pending, including
Fiber cancellation in an owning handler-return destructor. The engine can leave
a hidden zero-ref copy without free_obj. One request-global authenticated row
retains only that copy; its metadata adds no SOURCE/oldThis/API owners. Cleanup releases prepared cells, FIRST, RAW, then SOURCE while preserving
the supplied exception and handler restoration. Repeated calls retain distinct
copies/receivers and two edges to their shared capture. This is an abstract
lifetime model, not raw refcount equality; wider receive/mapping and bailout
paths remain partial.
[Cancellation review](../../coverage/semantics/generator-call-cancellation-review.json).

I100 uses the same raw forwarding cursor for copied value and reference arguments.
An unknown or overwritten ordinary named target throws after the successfully
prepared prefix, retaining the hidden copy before ordered argv/API cleanup.
The generated Error's trace owns raw argument values until the Error is released;
it owns neither SOURCE nor the old receiver. Required named holes retain the copy
at the authentic existing fake-receive failure, preserving default priority and
callee/API traces. Frame cleanup drops its prepared values before the API cursor
releases FIRST, RAW and SOURCE. Later receives, default throws and bailout paths
remain partial; the ordinary non-Generator dispatch is unchanged.
[Named-failure review](../../coverage/semantics/generator-call-mapping-review.json).

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
priority. The
[outer-binding review](../../coverage/semantics/closure-call-outer-binding-review.json)
adds packed and late-named receiver capture, missing-receiver traces and invalid
receiver priority over remembered inner errors after successful collection.
Duplicate `newThis` stops later producers before receiver type checking.
Traversable delivery and direct call-time references remain unsupported.
Further internal API capture, missing core internal bodies and the REAL
temporary-current lifetime decision remain required. Return verification remains
paused.
