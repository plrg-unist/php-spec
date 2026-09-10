# Source reference returns

Compiler98/runtime99 connect reference-returning named positional functions on
pinned PHP 8.5.10 CLI NTS64. The paired input is942/3c331e74; the independent
acceptance report records its exact code, evidence and one-test bridge. This
increment does not close the callable family or PHP core.

A returned reference owns its cell before the callee frame releases its locals.
Reference assignments and reference parameters preserve that identity; value
consumers read the value with the existing array ownership/COW rules. Temporary
call-array leaves can be returned by reference and survive their container's
release. The parameter-send restriction on temporary bases does not apply here.

Return source designation remains independent of the resulting operand. Ordinary
variables and actual reference calls avoid the return Notice. Literal/value
expressions, including an assignment-by-reference expression with a REFERENCE
result, emit `Only variable references should be returned by reference`. Calls
returning ordinary values also emit it. Bare and implicit returns emit the Notice
at their own instruction/end line after applicable static/fallthrough checks.
Whole `$GLOBALS` is a variable-designated copied value, not an alias to the global
table; its reference return does not emit that Notice.

An emitted type verifier reads an ordinary CV before the quiet return write fetch.
Missing untyped or mixed CVs stay quiet; a nullable typed missing CV warns and can
succeed, while an int CV warns before TypeError. Computed variables and dimensions
perform their writable fetch before verification, initializing missing slots
quietly. Successful coercion writes the shared source location/cell before frame
cleanup, including when the caller discards the result. Existing value-return
coercion remains detached from external aliases.

Caller demand comes from the original checked callsite's immediate source
consumers. Expression statements and discarded for clauses have unused results;
casts to void, ternary/coalesce expressions and value/reference consumers retain
used results. Variable promotion occurs only for a used result. Nineteen separate
pre-optimizer opcode observations constrain this projection. Two suppression
sources are projection-only controls: runtime error suppression remains required
work, and their Unsupported outcomes are not agreements.

`RETURN_REF_FETCH`, `RETURN_REF_VALUE` and `RETURN_REF_NULL` bind the owning BYREF
function, actual return source class and emitted line, or the permitted implicit
function/end line. Legacy value/null stages cannot replace them in BYREF frames.
Each call context's CALLSITE equals its immediate saved caller frame's ORIGIN,
including the saved context chain. An active RETURN_REF_VALUE stage accepts owning
KNOWN/REFERENCE results through leading AT/ORIGIN_RETURN wrappers; queued stages
do not inspect an unrelated current RESULT. Arbitrary consistent owning values
and references remain valid. The original forged lines, missing origins, legacy
stage substitutions and used/unused callsite swap are retained before repair.

Author gates cover31 source profiles,56 exact compiler phases plus2 suppression
boundaries/49 projections,19 demand projections/38 assertions, typed38 and
acquisition17 regressions, and2 dense cases/777 assertions. Independent gates
cover12 profiles,26 protocol controls/378 assertions,4 dense cases/1282 assertions
and2 complete933 state comparisons at seven cuts. Sets overlap. Final942 changes
only the repaired author state-test producer from semantic gate942/7951; all941
other files and modes agree. Three failed fixture preparations remain retained.

Authority is pinned `vendor/php-src` commit
`34308a6666b2d489c509541ea9befea9e2b42348`: `zend_compile_return`, return type
verification and `ZEND_RETURN_BY_REF`, with existing variable/dimension and frame
ownership machinery. Suppression, named/unpacked/variadic calls, closures/callables,
objects, exceptions/finally, dynamic sources, generators/Fibers, lifecycle and
intrinsics remain required, followed by callable integration and final complete
source/syntax/fresh offline checks. No intentional engine departure is introduced.
