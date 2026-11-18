# Raw-FLOAT nonnull coalesce RHS allocation

The raw-FLOAT RHS grammar admits recursive COALESCE trees together with FLOAT
leaves, unary signs, FLOAT casts and four arithmetic operations. Both operands
must belong to that same grammar. This syntax check supplies no VALUE, SOURCE,
pool, precision or allocation authority.

The existing emitted nonnull VALUE rule preserves the selected FLOAT bits,
including falsey negative zero. It requires NORMAL completion, emitted root
CODE with a positive line, no compiled root read, proper immediate SOURCE for
both children and matching root/selected-left precision. Nonnull selection
does not demand the skipped fallback's VALUE, CODE or precision. The outer STRING cast still checks
its complete SOURCE subtree, so corrupted skipped descendants remain rejected.
Installed folded pools retain their existing trust boundary; no source-to-pool
theorem or native numeric fallback is added.

The allocation body remains literal: the left REQUEST identity is resultID-2,
STRING conversion appends one RHS row at resultID-1, and CONCAT appends the final
row. Exact full-state CASTSTRING/CONCAT equalities, both false CONCAT flags,
source/captured/live precision, genuine owners, fresh final-row capture and
saved-key continuation proofs remain required. Registry rows add no roots.

PHP 8.5.10's `zend_compile_coalesce` emits COALESCE followed by the fallback
and QM_ASSIGN. `ZEND_COALESCE` tests nullness, copies the selected value and
jumps over the fallback; it does not test FLOAT truth.

The two originals preserve negative zero directly and -12.5 through nested
arithmetic, while skipping a FLOAT division by zero. Returning Warning callbacks
still change or rebind the current key after its original offset is saved.
The independent numeric-ternary control has the same quiet FLOAT VALUE and
exact one-row replay but remains outside this grammar. This supersedes only
the arithmetic cut's COALESCE exclusion; earlier failures and credits retain
their original identities.

The [review record](../../coverage/semantics/string-offset-runtime-allocated-float-coalesce-tree-rhs-concat-base-initial-raw-leading-key-review.json)
separates native originals observed once, Unsupported/prelaw refusals, source
comparisons, author/independent fixtures and static composition. General VALUE
producers, numeric ternaries/POWER, non-FLOAT leaves and multirow RHS allocations
remain outside this grammar; wider owners, release and lifetimes remain partial. Complete PHP core is unfinished.
