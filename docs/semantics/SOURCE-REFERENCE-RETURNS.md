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

Exact reference-return verification and acquisition now avoid assigning the
unchanged cell. This preserves genuine parameter-backing certificates and
property type sources, including forwarded reference calls and the repeated
check after `finally`. Writers compare the checked value with the captured
pre-check input; real scalar conversions and quiet missing-slot initialization
still write, and ordinary later assignments/binds still enforce property types.
The [focused review](../../coverage/semantics/reference-return-exact-review.json)
records 16 focused source agreements and private358 state cuts of 35 independent
plus 483 reviewed assertions across 13 fixtures. Actual359 over6536a8339
passes separate strict SL compilation at37b08adeb, with zero runtime evaluations.
That ledger retains the original delayed-TypeError failure and disproved
`F|R|SHARED` prediction. The same original now matches PHP's `F|F|R|SHARED` in the
[replay increment](../../coverage/semantics/reference-return-replay-review.json):
ten replay originals and 14 current/saved fixtures with 954 assertions pass at
private360. Four preserved affected return controls and one core-only terminal
weak-conversion control also agree; actual361 compilation retains a distinct cut.
The [scalar continuation increment](../../coverage/semantics/reference-return-scalar-replay-review.json)
also recovers while/do/for tails and caught break/continue/goto through source
contexts: 14 originals and 15 reached fixtures with 1,102 assertions pass at
separate private361 cuts; actual361 strict compilation has a distinct cut.
The [no-FREE switch increment](../../coverage/semantics/reference-return-switch-replay-review.json)
recovers selected-case remainder and fallthrough for CV/compiled-CONST subjects
without repeating their evaluation. Adjacent END/PHASE metadata owns no payload
and retires together on end, jump or incoming transfer. Seven preserved originals
and 14 current/saved fixtures with 1,339 assertions pass at retained private361
cuts; actual-parent compilation is separate. Runtime VAR/TMP array owners,
active-finalizer replay, protected temporary/NULL Notice timing and by-reference
Stringable conversion remain required.

Module 379 defers the designated Notice until finalizers and repeated type checks
complete. Source occurrence, designation and emitted line remain captured through
current/saved handlers; the raw operand retains its existing payload owner until
ordinary materialization and frame cleanup. A throwing handler leaves this function
and propagates in the caller; a replacing variable return cancels the old Notice.
Six focused originals plus one protected-unused control agree, and eight reached
fixtures pass 722 assertions. Actual-parent compilation keeps a distinct cut in the
[Notice review](../../coverage/semantics/reference-return-notice-review.json).
Active-finalizer replay, Stringable186 and wider owner protocols remain required.

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
