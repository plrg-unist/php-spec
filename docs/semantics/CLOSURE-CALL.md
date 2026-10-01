# Ordinary `Closure::call`

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

The repaired private freeze passed its bounded source, paused-state, independent
review and retained compatibility gates. Its current canonical bridge remains
pending in the [ledger](../../coverage/semantics/closure-call-review.json). Old 13-source
and four-stage passing reports are historical: their subset missed argument
ordering and trace defects and does not establish current acceptance.

Named `newThis`, unpacking, reference argument forms and by-reference closure
formals remain required extensions. By-reference formals need warning-producing
value forwarding into isolated cells, without caller write-back. Non-`stdClass`
internal/Throwable receivers, computed `call` names, captured method/getter/invoke
wrappers, generic array callables and source `__invoke` remain separate required
work. Reached unsupported forms are explicit `Unsupported` controls, never
native agreements.
