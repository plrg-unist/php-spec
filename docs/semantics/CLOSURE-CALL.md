# `Closure::call`

Module 182 calls a selected ordinary `REALCLOSURE` with a temporary user-class
receiver and lexical/called scope. The original closure keeps its binding and
shares its static cells; `call` does not allocate a bound copy. The pinned
source routes are `zend_closures.c::ZEND_METHOD(Closure, call)`,
`zend_valid_closure_binding`, and `zend_execute_API.c::zend_call_function`.

The selected closure and evaluated arguments remain rooted during argument
execution. Immediate simple-variable selector checks authenticate the chosen
objects; later argument effects may rebind those variables. `RAW` stores
original evaluated argument values in source order. Its keys and prepared
`SENT` values correlate until a deferred inner-name error clears `SENT`.
Every pending stage checks the compiled call line and evaluated operand modes.
An undefined simple-variable receiver retains null after its ordinary warning.

Named `newThis` may appear anywhere among named outer arguments. It fills the
receiver slot and is excluded from inner forwarding. Receiver selection and
the remaining original values stay separate even when arguments rebind the
source closure or receiver variable.

Forwarded expressions run before `newThis` type and inner-name validation; a
later throw takes priority. Invalid scalar `newThis` takes priority over an
inner-name error. Static and `stdClass` binding warnings run after argument
evaluation, suppress an inner-name error, and return null. Repeated outer named
arguments or a name that overwrites the filled `newThis` formal fail after that
expression, before later arguments, with the caller trace.

The body frame records the temporary class and an internal `Closure->call`
wrapper. The wrapper owns original positional values and named labels/order,
independently of weak parameter conversion and body writes. A deferred pre-entry
error records that wrapper with all evaluated arguments. Context validation
requires the wrapper; deleting it cannot select the ordinary call fallback.
The temporary class qualifies parameter, variadic and return diagnostics.
The inner return value is always demanded, including an unused outer call, and
the outer result resolves any returned reference without exposing its alias.
The result task authenticates its literal call site and compiled line.

By-reference closure formals receive values through fresh isolated reference
cells. Preparation happens after all outer expressions and receiver binding
checks, in original argument order. A reference warning precedes a later
inner-name error when that formal was reached first. Typed conversion and body
writes affect the isolated cell; the caller's outer cell remains unchanged.
Normal array values retain PHP copy behavior and nested reference elements
remain shared. Pending preparation validates its allocation extent and rejects
reusing a cell reachable through the original caller/source/argument roots.
The wrapper continues to retain the original values rather than prepared cells.

The repaired private freeze passed its bounded source, paused-state, independent
review and retained compatibility gates. Focused installed source and paused
interaction checks also passed. The [ledger](../../coverage/semantics/closure-call-review.json)
keeps their distinct executable snapshots. Old 13-source
and four-stage passing reports are historical: their subset missed argument
ordering and trace defects and does not establish current acceptance.

The [argument extension review](../../coverage/semantics/closure-call-arguments-review.json)
records current private named receiver and reference-formal source/state gates;
the focused later-base forwarding/exit bridge passes; canonical installation
remains pending. A separate
source-derived deferred-default cache counterexample remains a required generic
closure/default repair; these forwarding catalogues do not cover that branch.

Unpacking and broader reference argument forms remain required extensions. Non-`stdClass`
internal/Throwable receivers, computed `call` names, captured method/getter/invoke
wrappers, generic array callables and source `__invoke` remain separate required
work. Reached unsupported forms are explicit `Unsupported` controls, never
native agreements.
