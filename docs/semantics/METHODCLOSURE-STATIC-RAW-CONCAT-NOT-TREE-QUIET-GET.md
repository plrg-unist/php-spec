# Raw String NOT(CONCAT) selector trees

Bounded static USER method Get captures accept BooleanNot of actual raw-String
CONCAT roots inside recursive class and method selector trees. The unchanged
raw-string proof authenticates the inner root and every String/CONCAT descendant;
the new helper authenticates the outer NOT and its actual PCFIELD0. Joined bytes
must be non-NUL. String truth is false only for empty bytes or sole ASCII zero:
"00", whitespace and "false" retain String truth without numeric coercion. An
admitted empty Boolean-text result stays distinct from helper refusal.

Recursive selector CONCAT delegates old forms to the unchanged Double-NOT helper.
New site arms require new-helper success and prior-helper refusal, then exact
folded root PSTRING bytes without child pools. Class normalization occurs once
after the full join; method names use casefold only. CV `??`, private `??=` and
literal/CV Empty retain the existing source, cache, owner and cleanup bounds.

The matching engine's `zend_compile_unary_op`, `zend_try_ct_eval_unary_op`,
`boolean_not_function` and `i_zend_is_true` fold the quiet String operand and
preserve its String truth rule. Mixed INT/keyword/sign children under NOT(CONCAT),
CV/FLOAT/NUL, triple NOT and wider producers, owners and lifetimes remain partial;
all exact held boundaries remain unchanged.

Four fresh native originals and four pre-change Unsupported controls preceded
the edit. Author source2 and 214/241 fixtures, plus independent source2 and
382/270/127 fixtures, passed in separate SL507 cuts. The original unsplit
literal fixture timed out at 297 seconds and retains zero credit. Its exact
ordered checklist was partitioned under the same cap; accepted source/CV/author
cuts were not replayed. The [family review](../../coverage/semantics/magic-property-methodclosure-static-raw-concat-not-tree-quiet-get-review.json)
records these separate outcomes and the MAIN production-load status.
