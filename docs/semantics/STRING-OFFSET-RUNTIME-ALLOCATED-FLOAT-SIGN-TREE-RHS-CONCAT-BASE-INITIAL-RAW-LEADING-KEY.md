# Raw FLOAT sign-tree RHS allocation

An allocated CONCAT string-offset base admits a right STRING cast whose child
is a raw `NScalarFloat` or any finite nesting of `NExprUnaryPlus` and
`NExprUnaryMinus` around that atom. A syntax-only predicate states this grammar.
One shared allocation clause replaces the former raw, single-plus and
single-minus clauses; their remaining guard bodies were identical.

The predicate supplies no value or compiler authority. The existing typed
runtime certificate still authenticates the value, including nested folded or
emitted signs. The cast retains its complete SOURCE subtree, captured and live
precision, and positive emitted line. The selected left REQUEST identity is
resultID-2; the right cast appends exactly one row at resultID-1. Both CONCAT
constant flags remain false. Full saved-prefix CASTSTRING and CONCAT state
equalities permit only the expected registry appends and RESULT updates.
The selected KNOWN temporary owns the string; registry rows do not create roots.

At PHP 8.5.10, `zend_compile_unary_pm` recursively compiles its child and
`zend_try_ct_eval_unary_pm` uses multiplication by integer ±1. The DOUBLE arm
of `mul_function_fast` preserves FLOAT typing and the sign of zero. The new
direct original uses `+(-(+0.0))` and selects the minus byte in `"42-0"`.
The reference original uses `-(-(+(-12.5)))`, retaining the allocated
`"-10.5bcde-12.5"` header while the Warning callback rebinds the current key.
The saved offset9 selects `-`; the current key13 would select `5`.

Finite describes the source tree. Previously admitted infinite FLOAT values
retain the existing rules, and NaN retains its existing quietness exclusion.
The raw leaf check is deliberately syntactic: installed compiled pools keep
their prior trust boundary. No global compiler-consistency theorem is added.

The current raw-FLOAT and single-sign reviewers promote only their existing
derived nested-sign controls to admission. Their original accepted campaigns
remain frozen. The new independent review also checks a same-value CASTFLOAT
leaf with a valid FLOAT value and one-row replay: the sign-tree grammar still
refuses that wider producer.

The [review record](../../coverage/semantics/string-offset-runtime-allocated-float-sign-tree-rhs-concat-base-initial-raw-leading-key-review.json)
separates the two native originals observed once, prelaw refusals, source
comparisons, author and independent fixture cuts, and current derived controls.
General VALUE producers, other RHS shapes, multirow RHS allocations and wider
ownership/release/lifetimes remain partial. Complete PHP core is unfinished;
raw artifacts stay outside Git as evidence rather than operational inputs.
