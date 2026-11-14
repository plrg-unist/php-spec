# Raw numeric-String UnaryPlus selector trees

Bounded static USER method Get captures accept UnaryPlus of raw String literals
inside recursive CONCAT class and method selectors when the original PSTRING
quietly coerces to a signed64 integer. Leading zeros, surrounding numeric
whitespace and signed zero retain their original bytes and type as input;
the result contributes pure integer text.

The helper authenticates the complete operator and its actual PCFIELD0 String
child, including metadata. It requires quiet `COERCED (NINT i) false` and the
signed64 range before rendering. Recursive CONCAT checks actual child origins;
other leaves delegate to the unchanged prior helper. The new selector arms
require new-helper success and previous-helper refusal. Exact folded root
PSTRING bytes remain mandatory; child pools are unnecessary. Class normalization
occurs once after the full join, while method names use casefold only.

The matching engine's `zend_compile_unary_pm` and `zend_try_ct_eval_unary_pm`
fold through multiplication by integer one. Pure `coerce_number` and
`unary_apply` checks consume the original String and preserve its quiet integer
result. CV `??`, private `??=` and literal/CV Empty retain existing source,
cache, owner and cleanup bounds. FLOAT results, leading numeric data, warnings,
nonnumeric, nested/CV and wider producers remain refused; all exact holds remain.

Four fresh native originals and pre-change Unsupported controls preceded the
edit. Separate source/fixture cuts and the combined MAIN production load are in
the [family review](../../coverage/semantics/magic-property-methodclosure-static-raw-positive-string-concat-tree-quiet-get-review.json).
