# Quiet access and CV review

This is a design review for the next required core increment, not implementation
acceptance. [28 independent native originals](../../coverage/semantics/quiet-cv-independent-originals.json)
preserve exact PHP 8.5.10 source, lint and execution observations. The existing
five quiet-access, one list/header and seven request-environment boundaries
remain required work.

`??=` uses the compiler's expression memoization protocol: evaluated temporary
expressions are reused, while simple CV operands remain delayed reads. Thus
`$a[$i] ??= ($i=2)` stores at key 2, and `$$n ??= ($n="b")` stores into `$b`.
The original IDs containing `retained` are probe names, not a claimed outcome.
An incremented key expression executes once; a non-null left value skips the
right expression. The write phase must resolve the current target after right
side effects, including array replacement and scalar failure. See
`zend_compile_assign_coalesce` in `vendor/php-src/Zend/zend_compile.c`.

Quiet access suppresses missing-value diagnostics, but does not erase all
exceptions or expression effects. Missing nested dimensions still evaluate their
key expressions. Array/string access with an array key throws; a null base
quietly falls back. A missing ordinary property base evaluates a dynamic property
name, while nullsafe access to null skips that expression. A missing static class
still throws. Literal `$this ?? 7` throws outside object context, while a dynamic
variable with the string name `this` quietly falls back.

The `$http_response_header` deprecation depends on compiler context and access
mode. A statically compiled write, even inside a dead branch, suppresses later
ordinary CV-read deprecations. Quiet read and unset do not set that write flag;
coalesce assignment does. Repeated ordinary reads can each emit a compile-time
deprecation. The tests retain lint separately from execution so compile-time
messages cannot be misclassified as runtime fetch events. The relevant routines
are `zend_try_compile_cv` and `zend_compile_simple_var_no_cv`.

Computed `$this` writes and folded `$GLOBALS` names must retain their own static
versus runtime outcomes. These originals complement the seven preserved ordinary
request-environment boundaries; they do not discharge object callbacks, class
lookup, global environment, or frame semantics.
