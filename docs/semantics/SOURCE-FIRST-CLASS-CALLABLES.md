# First-class callable source increment

The singleton `...` call argument converts an active named user function into a
callable object without entering its body. Converting an existing real, arrow,
or named-function callable returns that object with the same identity. Invocation
uses the existing call binder, reference returns, and named function static cells.
The source compiler retains separate callee, call-initialization, and conversion
locations; multiline failures use the callee initialization line. The conversion
result is a temporary value, so reference assignment and required-reference
argument checks retain their PHP behavior.

The implementation is in `119-first-class-compiler.watsup` and
`120-first-class-callables.watsup`, with narrow shared call, storage, comparison,
and closure rules. Matching-engine evidence starts at
`zend_compile_call_common` and `ZEND_CALLABLE_CONVERT` in the pinned
`vendor/php-src/Zend/zend_compile.c` and `Zend/zend_vm_def.h`, and
`zend_create_fake_closure` in `Zend/zend_closures.c`.

[The review record](../../coverage/semantics/first-class-review.json) binds the
private 17-source differential audit (13 normal, 3 PHP errors, 1 static
rejection), four separate reference-context pairs, and three paused-state
stages with 49 assertions. The maintained source, compiler, and protocol tests
are under `tests/semantics/first_class*`; their profiles remain distinct from
the prior ordinary and callable campaigns. Builtin, method, array, and
constant-context callable conversion remain open dependencies.
