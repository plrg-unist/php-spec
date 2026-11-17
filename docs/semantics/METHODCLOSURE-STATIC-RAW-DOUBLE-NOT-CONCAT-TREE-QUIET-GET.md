# Double BooleanNot selector trees

Bounded static USER method Get captures admit exact outer BooleanNot of an
actual inner BooleanNot inside recursive CONCAT class and method selectors.
The existing raw-string NOT helper authenticates that exact inner operator.
Its result must be genuine Boolean text: empty bytes or sole ASCII one.
The outer operator complements that Boolean without inferring truth from an
arbitrary String, CONCAT or unary-plus expression.

Complete source, metadata and actual PCFIELD0 children remain mandatory.
The inner helper retains its existing raw signed64 Integer, simple or fully
qualified reserved Boolean/null, and non-NUL String leaves. Prior single-NOT
and other leaf admissions retain their fallback. An admitted empty byte result
remains distinct from helper refusal.

Exact root PSTRING bytes remain mandatory without child pools. Class
normalization occurs once after the whole join; methods use casefold only.
CV coalesce, private coalescing assignment and literal/CV Empty preserve
existing source, cache, owner and cleanup bounds. Bare/triple NOT, FLOAT, CV,
NUL and wider producers or lifetimes remain partial; every exact hold remains.

The pinned compiler's `zend_compile_unary_op` and
`zend_try_ct_eval_unary_op` fold these quiet leaves using
`boolean_not_function` and `i_zend_is_true`. Four native originals and four
prelaw Unsupported outcomes preceded the edit. Separate author source2/184x2,
independent source2/425x2 and the accepted MAIN production load retain their
original identities in the [family review](../../coverage/semantics/magic-property-methodclosure-static-raw-double-not-concat-tree-quiet-get-review.json).
