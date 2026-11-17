# Raw String BooleanNot selector trees

Bounded static USER method Get captures accept BooleanNot of actual raw
non-NUL String leaves inside recursive CONCAT class and method selectors.
Empty and sole ASCII-zero strings contribute ASCII-one text; other admitted
strings contribute empty text. Numeric-looking strings such as "00" and " 0"
retain String truth without numeric coercion. An admitted empty byte result
remains distinct from helper refusal.

The helper authenticates the complete operator and actual PCFIELD0 String,
including metadata, through the unchanged raw-string source proof. The new
NOT-child route explicitly excludes NUL. Recursive CONCAT checks every actual
child and delegates other leaves to the previous helper. New site arms require
new-helper success and prior-helper refusal. Exact folded root PSTRING bytes
remain mandatory without child pools. Class normalization occurs once after
the full join; methods use casefold only.

The matching engine's `zend_compile_unary_op`, `zend_try_ct_eval_unary_op`,
`boolean_not_function` and `i_zend_is_true` fold these quiet original strings.
CV `??`, private `??=` and literal/CV Empty retain existing source, cache,
owner and cleanup bounds. Bare/nested NOT, NUL, FLOAT, CV, sign and wider
producers remain outside this extension; all exact holds remain.

Four fresh native originals and pre-change Unsupported controls preceded the
edit. Separate author source2/162x2 and independent source2/319x2 cuts and the
independently accepted MAIN production load are in the
[family review](../../coverage/semantics/magic-property-methodclosure-static-raw-not-string-concat-tree-quiet-get-review.json).
