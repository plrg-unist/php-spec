# Quiet NOT over coalesce method selectors

Bounded static USER method selectors admit NOT and repeated NOT over the closed
CONCAT-left-coalesce tree. New forms compose through NOT and surrounding CONCAT;
all earlier raw providers remain literal. NOT contributes Boolean echo bytes, while
the surrounding emitted CONCAT retains its exact PSTRING tag.

Echo truth agrees with PHP truth only within the admitted quiet NULL, BOOL,
signed64 INT and STRING domain. Empty and ASCII `"0"` are false; `"00"`, `"01"`
and String `"-0"` are true. FLOAT is excluded: negative zero's echo `"-0"` would
lose its numeric falsehood, and NaN truth conversion can warn at this PHP pin.
Arrays, objects and CVs also remain outside this closed certificate.

NOT and CONCAT descend through proper source children, authenticating every
present source arm and keyword-name child. New NOT operands must be non-NUL.
Four measured original-source states justify the emitted root receipt: positive
nonfolded CODE, with no compiled read, pool value, redirect or effect. The new
route requires refusal by the preceding coalesce provider and creates no child
or pool facts. Existing class lookup, method identity, scope, caches, callback
capture and ownership guards remain unchanged.

A shared syntax filter skips legacy alternatives incompatible with coalesce
below NOT along NOT/CONCAT paths. Each skipped alternative requires an older raw
certificate that excludes this shape. This changes proof cost without supplying
a value or source authority; literal and two-STRING folded shapes stay untouched.

PHP 8.5.10 source authorities are `i_zend_is_true` in `Zend/zend_operators.h`,
`ZEND_BOOL_NOT` in `Zend/zend_vm_def.h`, and `zend_compile_unary_op` plus
`zend_try_ct_eval_unary_op` in `Zend/zend_compile.c`.

New NOT below coalesce/Boolean/ternary parents, new forms within a coalesce-left
CONCAT, nonquiet/NUL selectors and wider producers, owners or lifetimes remain
partial. This increment does not close the magic-property or core inventory.
The [review](../../coverage/semantics/magic-property-methodclosure-static-raw-not-concat-left-coalesce-tree-quiet-get-review.json)
binds the separate source and fixture evidence.
