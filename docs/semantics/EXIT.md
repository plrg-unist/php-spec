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

Successful invocation starts an internal unwind that may complete with
`EXITED int`. A separate signed32 request `EXITSTATUS` register records the
last integer/default status; string status writes its nonempty bytes and keeps
that register. The CLI observer reports its low byte for both normal and explicit
exit completion, retaining fatal-error status255 precedence. The unwind releases evaluation and user-frame
owners without capturing a Throwable trace or executing ordinary finally
continuations. Request global/static roots remain available for subsequent
lifecycle integration.

A throwing source-table destructor may replace exit and resume caller catch
after remaining slots retire, while request status remains set. Nested exits
can update status even when an older saved exit continues unwinding; saved
frames and destructor operations do not restore the request register.
[The scoped status review](../../coverage/semantics/source-static-exit-status-review.json)
keeps source ownership and status validation separate. Hard-fatal shutdown roots
and wider lifecycle interactions remain required.

Exit clears the active source origin with the discarded continuation. Saved
frames keep their own context until they unwind. A budget pause during exit
can therefore resume from a catch or finalizer without requiring a discarded
protected-region marker. The [origin cleanup ledger](../../coverage/semantics/exit-origin-author.json)
separates six exact sources, paused cleanup checks, the original invalid pause,
and retained exit controls.

The installed bridge at **b54f984b4** preserves six original native tuples and
passes two public paused stages (64 assertions), including saved caller
iterators and inherited suppression before terminal reporting restoration.

The historical exit increment above does not claim full request shutdown.
[Ordered shutdown callbacks](SOURCE-SHUTDOWN.md) now follow its completion;
destructors, GC, output buffering and registration release remain required.
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
