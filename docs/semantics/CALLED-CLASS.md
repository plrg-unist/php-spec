# Called-class introspection

Module 223 implements `get_called_class()` for the admitted source call routes.
It shares the ordered intrinsic argument protocol in 198/199: argument effects
and named/unpack errors precede the zero-argument count check, which precedes
class lookup. Direct calls, dynamic names, builtin first-class callables,
explicit `Closure->__invoke` and pipe calls retain their selected source,
arguments and callable owner. User namespace declarations still override the
global intrinsic.

The result is the active called class, preserving its declared spelling. It is
distinct from the lexical declaring class: inherited instance and static methods,
forwarding `self`/`parent`/`static` calls, captured methods and source Closures use
the existing authenticated call context. Rebound source Closures and temporary
`Closure::call` use their actual receiver/scope. Eval retains that context.
A plain user function or a global-created Closure stops lookup; a suspended
method cannot lend its class to that frame. A source error handler observes its
own called class, and normal/throw cleanup restores the genuine emitter.

An unscoped builtin callable observes its invocation context and retains no
creator class. Its explicit `Closure->__invoke` wrapper has a Closure receiver,
so that route returns `Closure`, including after the selected variable is unset.
The compiler-special zero-argument `GET_CALLED_CLASS` opcode has no builtin error
trace frame. Generic, named/unpacked, dynamic and captured calls preserve their
internal frame; count errors retain supplied arguments.

The source routes are `Zend/zend_builtin_functions.c::get_called_class`,
`Zend/zend_execute_API.c::zend_get_called_scope`,
`Zend/zend_compile.c::zend_compile_func_get_called_class` and
`Zend/zend_vm_def.h::ZEND_GET_CALLED_CLASS` in the pinned PHP 8.5.10 tree.
The optimized result is TMP even outside an ordinary function. Parser-initial
literal names share that optimization; later cast-folded constant names retain
the generic frame and result category. Temporary writes use the same compiler
facts and reject in the native phase.

Source cases are in `tests/semantics/called_class_cases.json`; run them with
`python3 tests/semantics/method_runtime.py --catalogue tests/semantics/called_class_cases.json`.
`python3 tests/semantics/called_class_protocol.py` checks stopping frames,
selected owners, dynamic-name certificates and actual/saved handler contexts.
The [review ledger](../../coverage/semantics/called-class-review.json) records
tested revisions, commands, original failures and independent evidence.
Reached `Closure::fromCallable` is an explicit Unsupported core dependency,
preserving the native witness rather than reporting a missing class. Its focused
control also keeps genuine missing-class errors and namespaced user methods
distinct. Builtin Closure rebinding, builtin API callback targets, unsupported
suspension and broader reference-result consumers remain separate dependencies.
Both bare and echo suppression of an undefined variable retain their existing
Unsupported warning-producer boundary; neither is counted as source agreement.
