# Explicit user output handlers

Module395 extends the Module391 stack with chunk0 user handlers for explicit
flush, clean, end and content-get operations. Ordinary named functions, simple
method/invokable callbacks and real Closures use cached selection and ordinary
weak internal parameter reception. Traces retain the internal handler frame and
the originating builtin API frame. Handler names preserve raw string/array
spelling; wider Closure and effectful callable forms remain dependencies.

The handler receives a copied input string and the native START/CLEAN/FLUSH/FINAL
phase flags. Get-clean/get-flush return a separate frozen copy. The live top
buffer remains visible through callback getters. Callback writes append there
and mark PRODUCED_OUTPUT; PHP8.5 deprecates those writes while temporarily
disabling that layer. Error-handler writes then bypass it, including the native
PRODUCED bit on an enabled lower default layer. FALSE forwards the current live
bytes and permanently disables the handler, with empty storage of size0. TRUE
and NULL suppress output; other admitted scalars supply converted bytes.

The raw callback value (`zoh`) is the buffer's sole callback owner. Cached FCC
selection and original snapshots are readonly witnesses. Reference-backed raw
arrays can release a receiver when the callee returns, while ordinary raw arrays
retain it until buffer removal. Arguments/retval finish cleanup before buffer
reset and the running state ends. End operations write lower layers before
releasing `zoh`; budget pauses retain every live owner and continuation.

Automatic chunk callbacks, request-end/fatal callback drains, non-scalar or
reference-return conversion, typed variadic reception, mutating buffer APIs
during a handler, capability
failure notices for user handlers, and invalid/effectful callable creation stay
explicit Unsupported dependencies. Output handlers permit Fiber switching in
PHP; this milestone refuses switch entry until its suspension protocol is
specified. A retired borrowed target can authenticate normal completion, but
cannot be invoked again by this slice. Buffered stdout diagnostics keep the
existing Module391 boundary. Full core remains partial.

Primary authority is `main/output.c` handler creation/op/stack-pop/destruction and
`Zend/zend_API.c` callable names/selection and
`Zend/zend_execute_API.c::zend_call_function` invocation. The source runners compare
original bytes, both output channels and exits against the sole pinned runtime.
Reached-state checks distinguish borrowed receiver retirement, sole raw callback
ownership, post-route release, temporary disablement and valid forged getter
copies. Final acceptance is recorded in the concise author and independent
ledgers; original failures and raw observations remain external.
