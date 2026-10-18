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
the prior ordinary and callable campaigns. Builtin, method, array and
constant-context conversion were dependencies of that original increment;
later family reviews record their separately validated slices.

[Stored callable names](../../coverage/semantics/stored-callable-carrier-review.json)
now enter the same resolver through raw/interned/request string bytes. Compiler
origins, callee-initialization lines, lookup and method access guards are unchanged.
Named and inherited static targets stay frozen after alias-cell replacement;
a lexical private static capture remains callable after clone/seed retirement,
while a fresh same-byte name outside that scope is denied. Three exact originals
and 291 Boolean premises (283 setup + 8 pure)/12 typed transitions cover named
allocations, method selections/captures and scalar missing/private Errors. Later
source calls and allocated catches are separate from those raw-step claims.
The original COMP71 stored-name failure keeps its cut and zero credit; these fresh
sources validate the bounded reception repair. Nonstatic class-string expansion,
autoload and invalid/embedded-NUL names remain partial.
