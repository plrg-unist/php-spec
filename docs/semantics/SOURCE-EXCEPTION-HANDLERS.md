# Source exception handlers

Module222 implements `set_exception_handler`, `get_exception_handler` and
`restore_exception_handler` through the ordinary checked CONFIG call path.
Registration retains the raw callable or null, returns the prior raw value, and
pushes the prior registration. Invalid callbacks and exact argument-count errors
leave the stack unchanged. Named, unpacked and captured builtin calls share that
path; getters preserve normal array copy-on-write behavior.

After source unwinding and `finally`, an uncaught Throwable selects the raw handler
again with no USER caller. The current registration moves onto the stack while
the callback receives exactly one original Throwable through ordinary weak
parameter reception. Captured private permission remains usable; raw private
methods cannot inherit the registration frame. False return still handles the
exception; selection precedes terminal Throwable stringification. A handler may
restore or replace handlers before throwing: the new exception uses the current
handler, or terminates with an uncaught fatal when none is installed. Exit enters the ordered [shutdown queue](SOURCE-SHUTDOWN.md); its status
survives unless a shutdown callback replaces it.

Selected callbacks keep an immutable borrowed raw-array snapshot, without adding
a registry owner. A static selector can retire after the handler pops its
registration and mutates the original array. Nonstatic receivers and the
Throwable keep their actual owners. Current and saved callback frames certify the
null caller, internal trace, one argument and original extra operand. Typed
variadic reception keeps its converted view in a separate borrowed certificate;
later local-array writes preserve that view for argument introspection. By-reference
reception warns at `Unknown:0`; an error handler can install a replacement
exception handler and throw. After the nested callback returns, the originally
selected exception callback resumes.

Invalid raw error handlers selected at that send-warning boundary produce an
internal fatal at `Unknown:0`. Their reference sends also warn at that boundary;
four-argument reception and false fallback retain the original exception send.
Accepted Stringable variadic/default reception remains weak under a strict main
script, and static-default diagnostics retain their actual source file.

The source catalogue and finite checkpoints are separate validation gates:

```sh
python3 tests/semantics/exception_handlers.py
python3 tests/semantics/exception_handler_state.py
python3 tests/semantics/exception_handler_review.py
python3 tests/semantics/exception_handler_state_review.py
python3 tests/semantics/exception_handler_static_default.py
python3 tests/semantics/callback_api_review.py --match exception-
```

The [author/composition record](../../coverage/semantics/exception-handlers-review.json)
and [independent review](../../coverage/semantics/exception-handler-review.json)
separate original source tuples, ownership/context checks and affected corrections.
The earlier two explicit Unsupported controls retain zero agreement credit at
their original cut. Module247 now stages scope-keyword/compound registration and
terminal selection through the shared221 API. Registration keeps raw values;
terminal deprecations use the genuine null caller and `Unknown:0`. Warning
callbacks may mutate referenced methods, restore or replace handlers, throw or
exit; the original selected continuation and Throwable remain authenticated.
Module270 releases returned values and the original Throwable before restoring
the old handler, preserving genuine callback state during destructor effects.
Wider magic/autoload/internal callbacks and GC/output/free request phases remain
open. Ordered shutdown callback entry is implemented by module231. Shared207 error-handler reference-return bodies and temporary-value
reference returns retain their existing Unsupported boundaries; accepted local
variable reference returns are ignored correctly by this exception callback.
This milestone does not close complete core.
