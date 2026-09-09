# Quiet access and CV review

Quiet variable/DIM coalescing and compiled header/name conversion are accepted
at `a42fddfe`; [independent review](../../coverage/semantics/quiet-access-review.json)
binds295 exact sources, author 8 state programs/3,760 assertions and independent 6/
2,277. Earlier 286 independent source runs retain their original identity; nine added
originals and nine canonical public CLI replays pass separately. Full checked/state
observations are retained losslessly in the linked evidence. Three object quiet
forms, request environment, `isset`/`empty` and `??=` remain source work.

The [28 independent native originals](../../coverage/semantics/quiet-cv-independent-originals.json)
preserve exact PHP 8.5.10 source, lint and execution observations for the broader
continuation described below.

`??=` uses the compiler's expression memoization protocol: evaluated temporary
expressions are reused, while simple CV operands remain delayed reads. Thus
`$a[$i] ??= ($i=2)` stores at key 2, and `$$n ??= ($n="b")` stores into `$b`.
The original IDs containing `retained` are probe names, not a claimed outcome.
An incremented key expression executes once; a non-null left value skips the
right expression. The write phase must resolve the current target after right
side effects, including array replacement and scalar failure. See
`zend_compile_assign_coalesce` in `vendor/php-src/Zend/zend_compile.c`.

Coalescing quiet access suppresses missing-value diagnostics, but does not erase
all exceptions or expression effects. Missing nested dimensions still evaluate
their key expressions. Array/string access with an array key throws; a null base
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

Twenty further [original multiline controls](../../coverage/semantics/coalesce-assignment-line-originals.json)
and their [independent native/lint replay](../../coverage/semantics/coalesce-assignment-line-review.json)
separate the initial quiet-read line from the later write-refetch line. Constant
or temporary float keys warn on the ending line during initial evaluation, then
on the original expression line when reused for writing; a CV key keeps its own
line for both reads. Nested targets preserve each key's own line. The engine sets
AST line before memoized FETCH. Retained temporary copies must also be released
when a non-null result skips the write branch.

Coalesce dimension fetch and `isset`/`empty` dimension checks need distinct
protocols. For a string base, key `"0x"` warns and reads offset zero with `??`,
while `isset` is false and `empty` true silently. An array key throws with `??`
but gives those same silent boolean results for a string base with `isset`/`empty`.
A float key1.5 is silent with `??`, but `isset`/`empty` report lossy conversion.
Array-base illegal-key diagnostic text also differs. The retained198-source matrix distinguishes these protocols; the quiet
publication admits only the `??` protocol. `isset`/`empty` remain pending.

Twelve [reference-valued memoization originals](../../coverage/semantics/coalesce-assignment-reference-originals.json)
show that a copied temporary can still contain a reference cell. `ZEND_COPY_TMP`
uses `ZVAL_COPY`, preserving wrappers. With `$j=1`, the key `($k=&$j)` in
`$a[($k=&$j)] ??= ($j=2)` becomes2 on refetch. Rebinding `$j` to another cell instead
leaves the saved key at1. A ternary around that AssignRef copies its resolved value,
also retaining key1. Computed variable names show the same distinction. Mutating
the retained cell to an array raises an illegal-key TypeError during writing.
Memoization therefore retains the actual VALUE, including a REFERENCE; resolving
all temporary operands early would lose this behavior. The non-null branch and
throwing RHS need ownership cleanup for these retained wrappers.

Sixteen [nested memoization and result-ownership originals](../../coverage/semantics/coalesce-assignment-nested-originals.json)
cover independent nested memo tables, shared reference operands, selected and
assigned array results, by-reference iteration of expression results, list effects
and loop/throw cleanup. They retain native/lint/checked observations before the
compiler-export guard correction; source/state acceptance remains separate.
