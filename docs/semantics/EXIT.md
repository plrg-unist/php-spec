# Exit and die

Modules 147/148 model the PHP 8.5.10 language intrinsics `exit` and `die`.
The ordered compiler retains the compact `NExprExit` child and the existing
function-call form. Lexical `die` has the canonical `exit` identity; qualified
and computed `die` calls retain their alias name in diagnostics. Literal,
dynamic, first-class and pipe calls select a finite internal identity before
argument evaluation, without a fabricated source function.

The dedicated binder evaluates argument expressions in order, then sends each
value. It preserves named/unpacked argument errors before intrinsic entry;
arity and `string|int` conversion occur after sending all arguments. Numeric
strings remain strings. Weak conversion tries integer before string, preserving
fractional-float and null deprecations and nonfinite-float string behavior.
Strictness comes from the caller source unit. Receiving errors include a real
internal trace frame; send errors do not.

First-class internal callables use `INTRINSICCLOSURE pintrinsic`. They retain
ordinary Closure identity, callable/nominal typing, comparison, casts and heap
ownership. The selected closure remains owned while arguments execute and
while user frames are suspended. The finite identity seam can admit another
reviewed language intrinsic; it is not a general library dispatcher.

Successful invocation completes with `EXITED int`, independently of ordinary
return and error completion. The integer is normalized to the engine's signed
32-bit exit-status slot. The CLI observer reports `explicit_exit` and the
process status modulo 256. String status writes its nonempty bytes and uses
status zero. The internal unwind path releases evaluation and user-frame
owners without capturing a Throwable trace or executing ordinary finally
continuations. Request global/static roots remain available for subsequent
lifecycle integration.

Shutdown functions, destructors, output callbacks, user error handlers and
Stringable conversion callbacks remain open dependencies. This increment does
not claim full request shutdown or general Throwable/catch/finally semantics.
Ordinary libraries and unimplemented Traversable dispatch remain explicit
Unsupported results.

Native evidence compares the original source's exact stdout, stderr and
process status. Those bytes cannot distinguish `exit(0)` from ordinary finish,
or every nonzero exit from a suppressed fatal error. Expected model tags are
separate source-derived assertions; paused-state checks establish the distinct
terminal completion and ownership behavior. No native category is inferred
from the observable tuple.

Source authority: `zend_compile_call` and send lowering in
`vendor/php-src/Zend/zend_compile.c`; `T_EXIT` in
`Zend/zend_language_parser.y`; `ZEND_FUNCTION(exit)` in
`Zend/zend_builtin_functions.c`; string-or-long parameter conversion in
`Zend/zend_API.c`; internal unwind-exit handling in
`Zend/zend_exceptions.c` and `zend_dispatch_try_catch_finally_helper` in
`Zend/zend_vm_def.h`; `EG(exit_status)` in `Zend/zend_globals.h`.
