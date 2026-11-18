# FLOAT cast/sign-tree RHS allocation

The existing syntax-only raw-FLOAT RHS grammar also recurses through
`NExprCastDouble`. Raw FLOATs, unary signs and FLOAT casts can therefore nest
in any finite order. The allocation body remains byte-identical: typed VALUE,
immediate left/right SOURCE, the full right STRING-cast subtree, precision,
both false CONCAT flags, contiguous REQUEST identities and full saved-prefix
state replay retain their existing authority. The left BASE contract still
governs selected or skipped coalesce/shorthand children. Registry rows do not
become owners.

PHP 8.5.10's `zend_compile_cast` emits `ZEND_CAST` for DOUBLE. The existing
runtime VALUE certificate requires emitted CODEfalse, readEPS, positive lines,
proper child SOURCE, matching precision and a quiet child value. FLOAT-to-FLOAT
`CASTFLOAT` changes only RESULT. `NExprCastDouble` is the source constructor;
`CASTFLOAT` is the semantic cast operator.

Both new original sources interleave two FLOAT casts with unary signs. Their
right operands remain FLOAT, including negative zero, and the final STRING
cast appends one row. Saved leading offsets still select the original minus
byte after the Warning callback changes or rebinds the current key. Pure
grammar checks and the prior sign-tree reviewer's current CASTFLOAT helper are
promoted separately; accepted original campaigns remain frozen.

Arithmetic `(-12.5)+0.0` is a same-value FLOAT producer with the same one-row
STRING cast, but stays outside the grammar. Integer/string leaves, other casts,
general VALUE, multirow RHS allocation and wider owner/release/lifetime forms
remain partial. NaN refusal, admitted infinity and installed compiled-pool
boundaries are unchanged.

The [review record](../../coverage/semantics/string-offset-runtime-allocated-float-cast-sign-tree-rhs-concat-base-initial-raw-leading-key-review.json)
keeps two native originals observed once and two source agreements separate
from prelaw 80/91, author 247/92 and 264/92, independent 387/218 and the current
derived-only 53 checks (52 helper conditions and one call). All 14 bounded
WHOLE judgments are clear; accepted historical originals remain unrenewed. The original
author fixture's CASTDOUBLE operator typo failed compilation without executing
the model; its correction changes only that fixture token. A later fixture
incorrectly treated an unused pool entry as authority for an emitted root;
CODEfalse/readEPS instead preserves the genuine child VALUE. Both original
failures stay outside Git with zero agreement credit. Complete PHP core remains
unfinished.
