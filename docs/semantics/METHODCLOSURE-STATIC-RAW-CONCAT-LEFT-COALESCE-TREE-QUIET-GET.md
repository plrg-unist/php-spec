# Quiet static method selectors with CONCAT-left coalesces

Bounded static USER method-closure selectors retain the string type of a quiet
CONCAT used on the left of `??`. Empty and `"0"` strings remain nonnull, including
when their components contain false or NULL. A separate typed left receipt uses
the preceding closed primitive-coalesce tree; its primitive fallback also lets
an outer literal NULL select a new coalesce RHS. New forms compose through
CONCAT and coalesce RHSs. Earlier providers remain unchanged.

Every present source arm and keyword-name child remains authenticated, including
skipped arms. Exact non-NUL bytes, class lookup, method identity, defining scope,
static caches, callback capture and existing ownership limits remain required.
Four measured original-source states justify the emitted root receipt: a positive
nonfolded expression marker, with no compiled read, pool value, redirect or effect.
The new receipt applies only when the preceding primitive-tree provider refuses;
it creates no child or pool facts.

The matching PHP 8.5.10 source routes are `concat_function` in
`Zend/zend_operators.c`, and `zend_compile_coalesce`/`ZEND_COALESCE` in
`Zend/zend_compile.c`/`Zend/zend_vm_def.h`. CONCAT returns a string; coalesce tests
nullness rather than string truth.

Left CONCATs containing this new form, new forms below outer NOT/Boolean/ternary
operators, FLOAT/CV/nonquiet/NUL selectors and wider owners or lifetimes remain
partial. This increment does not close the magic-property or core inventory.

The [review](../../coverage/semantics/magic-property-methodclosure-static-raw-concat-left-coalesce-tree-quiet-get-review.json)
binds the source cases, separate author/independent fixture cuts and raw evidence.
