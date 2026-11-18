# Raw-FLOAT full-ternary RHS allocation

The raw-FLOAT tree grammar admits full ternaries with three proper FLOAT
subtrees. The true arm must be an expression; explicit ABSENT shorthand remains
excluded. The clause adds syntax membership only, retaining every existing
VALUE, compiler/pool, SOURCE, precision, full-state and ownership premise.

The existing evaluator demands a genuine FLOAT condition and exact quiet truth
state, then the selected child's typed VALUE. Root/condition/selected precision
and all three immediate SOURCE children remain required. The unselected arm's
VALUE, CODE and precision are undemanded. Outer STRING conversion still checks
the complete SOURCE tree, including skipped descendants; noisy NaN truth does
not acquire this quiet certificate.

The allocation certificate retains resultID-2/resultID-1/resultID for the left
header, one RHS CASTSTRING row and final CONCAT row. Both false CONCAT flags,
full prefix CASTSTRING/CONCAT equality, genuine owners, fresh initial capture,
saved offsets, key aliases and budget resumption remain unchanged. Registry rows
supply bytes without roots.

At PHP 8.5.10, `zend_compile_conditional` uses JMPZ and QM_ASSIGN to select one
arm and skip the other. `i_zend_is_true` tests DOUBLE zero/nonzero and warns for
NaN; the existing exact-state truth premise retains that diagnostic boundary.
The direct original selects negative zero through ELSE, while the nonzero
reference condition selects -25 before arithmetic produces -12.5. Both skip a
division-by-zero arm and preserve the saved minus-byte result after Warnings.

The independent shorthand control has genuine quiet FLOAT VALUE and the same
one-row replay but fails the proper-three-child grammar. Earlier NN/arithmetic
full-ternary refusals retain their historical identities; only their affected
current query/helper expectations are projected, without old campaign replay.

The [review record](../../coverage/semantics/string-offset-runtime-allocated-float-ternary-tree-rhs-concat-base-initial-raw-leading-key-review.json)
keeps native originals observed once, Unsupported/prelaw controls, source
comparisons, author/independent fixtures and static composition separate.
General VALUE/non-FLOAT producers, shorthand/POWER grammar, multirow allocation,
wider owners, release and lifetimes remain partial. Complete PHP core is unfinished.
