# Computed operands in typed ternary-left coalesce selectors

The existing direct ternary-left coalesce certificate admits constructor-known
STRING and BOOL operands in full ternary arms and shorthand conditions/fallbacks.
An authenticated quiet CONCAT yields its exact non-NUL PSTRING bytes. NOT and
the five Boolean binary constructors yield PBOOL, requiring their existing quiet
byte certificate to return exactly empty bytes or ASCII "1". The outer constructor
establishes the tag; arbitrary bare ternary/coalesce results are not inferred from
echo text.

The primitive branch is unchanged and runs first. Every old primitive Some(v)
therefore gives the same new operand Some(v), including its exact scalar tag,
value and SOURCE requirements. Replacing only the four operand premises preserves
all prior typed-left successes and their composed tree/receipt successes. This
pointwise bridge does not renew earlier source, fixture or native evidence.

Selected NULL alone requests the coalesce RHS. BOOLfalse, INT0, empty STRING and
STRING "0" remain nonnull. A truthy shorthand keeps its original tagged operand;
STRING "01"/"10" must not become BOOLtrue. ABSENT remains distinct from a present
NULL or FALSE. The existing source certificate authenticates both proper arms,
including quiet skipped operands; their real compiler fold/read/pool facts remain.

The existing full-condition byte proof, byte tree, positive nonfolded CONCAT root
receipt and 46 dispatch guards remain literal. Lookup, namespace/cache, callback,
receiver retirement and owner/lifetime behavior also remain unchanged. No native
evaluator or new runtime string carrier supplies the certificate's answer.

PHP 8.5.10 authorities are `zend_compile_conditional`,
`zend_compile_shorthand_conditional`, `zend_compile_coalesce` and Boolean/CONCAT
lowering in `Zend/zend_compile.c`; `ZEND_QM_ASSIGN`, `ZEND_JMP_SET`,
`ZEND_COALESCE`, Boolean handlers and `ZEND_CONCAT` in `Zend/zend_vm_def.h`
preserve the selected result kind and distinguish truth from nullness.

FLOAT/CV/nonquiet/NUL operands, wider parents/selectors/producers and ownership
or lifecycle extensions remain partial. No core or family obligation closes.
The [review](../../coverage/semantics/magic-property-methodclosure-static-raw-computed-operand-typed-ternary-left-coalesce-quiet-get-review.json)
records fresh source comparisons, saved native originals, focused fixtures and
the preserved prelaw timeout separately.
