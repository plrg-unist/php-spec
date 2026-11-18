# Single unary-minus FLOAT RHS allocation

An allocated CONCAT string-offset base admits a right operand of exactly
`(string)(-<raw FLOAT>)`. The new clause in
`425-string-offset-read-continuations.watsup` differs from the existing single
unary-plus clause only in its source constructor and comment. Its completion,
source, compiler, precision, registry, identity and state-replay guards remain
literal.

The selected left REQUEST identity is resultID-2, and the right cast appends
exactly one row at resultID-1. Both CONCAT constant flags remain false. Complete
saved-prefix CASTSTRING and CONCAT equalities permit only the expected registry
append and RESULT updates. The right cast retains its whole SOURCE subtree and
existing typed FLOAT authority; the selected KNOWN temporary retains ownership.
Registry rows do not become roots.

At PHP 8.5.10, `zend_compile_unary_pm` and `zend_try_ct_eval_unary_pm` lower unary
minus to multiplication by integer -1. `mul_function_fast` preserves the DOUBLE
operand's type. The direct original therefore casts negative FLOAT zero to
`"-0"`, producing REQUEST3 with four registry rows and selecting `-` at offset2.
The reference original produces REQUEST5 with six rows and
`"-10.5bcde-12.5"`; saved offset9 selects `-`, while the callback's rebound key13
would select `5`.

Raw atom payloads retain their original nonnegative sign. Negated unary result
bits, including the sign bit of zero, are checked separately. The mixed nested
`+(-12.5)` control retains a valid same-negative right cast and one-row full-state
replay, but refuses the exact single-sign CONCAT gate and read plan. Existing
raw-FLOAT and unary-plus clauses and their nested-plus controls are unchanged.

The existing installed-pool precondition remains. Folded unary identity uses
the existing literal-unary equality; irrelevant atom facts do not add authority,
and retained valid atom facts can support the existing emitted-unary route.
This is not a global compiler-consistency theorem or a new general VALUE rule.

The [review record](../../coverage/semantics/string-offset-runtime-allocated-unary-minus-float-rhs-concat-base-initial-raw-leading-key-review.json)
keeps native originals observed once, source comparisons, author fixtures and
independent review as separate cuts. Nested signs, other RHS producers, identity
STRING casts, multirow allocations and wider ownership/release/lifetimes retain
their existing limits. Complete PHP core remains unfinished; raw artifacts stay
outside Git as evidence rather than operational inputs.
