# Single unary-plus FLOAT RHS allocation

An allocated CONCAT string-offset base admits a right operand of exactly
`(string)(+<raw FLOAT>)`. The existing FLOAT cast certificate already supplies
the right value; the new clause in `425-string-offset-read-continuations.watsup`
authenticates this one source shape at the CONCAT allocation boundary.

The result REQUEST identity is two above the selected left identity and one
above the right identity. The right cast appends exactly one registry row and
both CONCAT operands retain false constant flags. Complete saved-prefix
`cast_apply` and `string_concat` equalities allow only the expected registry
append and RESULT updates. Equal captured precision, unchanged live precision,
proper SOURCE occurrences, positive emitted lines and the existing typed value
authority remain required. The selected KNOWN operand owns the temporary;
registry rows do not establish ownership.

PHP 8.5.10's `zend_compile_unary_pm` and `zend_try_ct_eval_unary_pm` lower unary
plus to multiplication by integer one. `mul_function_fast` preserves a DOUBLE
operand's type. Thus the native `+0.0` original requires an allocated FLOAT
string row even though its bytes are `"0"`; replacing it by integer zero would
change the allocation history.

The two new original sources retain their exact native observations once.
The direct case produces REQUEST3 with four registry rows. The reference case
produces REQUEST5 with six rows and distinguishes the saved offset11 (`.`)
from the callback's rebound current key12 (`5`). Source comparisons, author
continuation fixtures and independent review keep separate evidence cuts in the
[review record](../../coverage/semantics/string-offset-runtime-allocated-unary-plus-float-rhs-concat-base-initial-raw-leading-key-review.json).

The checked nested `+(+12.5)` control still has a valid right cast and one-row
replay, but refuses the new exact-one-plus CONCAT gate and read plan. It replaces
only the current raw-FLOAT reviewer's former single-plus refusal control; the
original raw-FLOAT review cut remains historical evidence.

Installed compiled pools retain their existing trust boundary. A coherent
unary SOURCE rewrite with a stale folded unary value is refused by the existing
literal-unary equality. Irrelevant atom pool/precision facts do not become new
authority. An emitted unary with retained valid atom facts may certify the same
FLOAT through the existing runtime rule. No global compiler-consistency theorem
or new general VALUE rule is claimed.

This RHS admission excludes nested signs, unary minus, other producers, identity
STRING casts and multirow RHS allocations. General VALUE, wider owners, NUL
source release, cleanup and lifetimes retain their existing bounds. Complete
PHP core remains unfinished. Raw execution artifacts stay outside Git and are
evidence rather than build or runtime inputs.
