# Integer/String NOT(CONCAT) selector trees

Bounded static USER method Get captures accept BooleanNot of actual CONCAT
roots whose descendants are raw String or signed64 Integer literals. The
unchanged raw-integer/string proof authenticates every actual node and metadata;
the new helper authenticates the outer NOT and PCFIELD0. CONCAT supplies String
truth: `0 . 0` yields "00" and is truthy, while `0 . ''` yields "0" and is falsey.
Joined bytes must be non-NUL. Exact Integer text uses the existing pure
`$ntsigned` rules; native witnesses use actual raw zero and positive MAX, while
synthetic negative AST values carry no source credit.

Recursive selector CONCAT delegates old forms to the unchanged String-only
NOT(CONCAT) helper. New site arms require new-helper success and prior-helper
refusal, then exact folded root PSTRING bytes without child pools. Class
normalization occurs once after the full join; methods use casefold only.
CV `??`, private `??=` and literal/CV Empty retain their source, cache, owner
and cleanup guards.

The matching `zend_compile_binary_op` and `concat_function` routes convert
Integer operands with `__zval_get_string_func`/`zend_long_to_str`, then
`zend_compile_unary_op`/`boolean_not_function`/`i_zend_is_true` use String truth.
Keywords, unary signs, FLOAT/CV/NUL, triple NOT and wider producers, owners and
lifetimes remain partial; all exact held boundaries remain unchanged.

Native4 once and prelaw Unsupported4 precede the helper edit. Author source2
and219/245 fixtures, plus independent source2 and402/109/107/85/82/139 fixtures,
retain separate stable cuts. The original combined method199 timeout remains0
credit; the corrected partitions retain the exact ordered381 literal checks.
Fixture assertions and synthetic raw negative ASTs carry source0. See the
[review record](../../coverage/semantics/magic-property-methodclosure-static-raw-integer-concat-not-tree-quiet-get-review.json).

Independent MAIN composition and the sole joined SL508 load are clear in the
review record. Full core and wider contexts remain unfinished.
