# Coalesce operands in quiet typed ternary selectors

The existing four typed ternary operand positions now admit bare COALESCE roots:
present FULL arms and SHORT condition/fallback. Both proper children recursively
retain their authenticated scalar tags. A non-NULL left value is returned exactly;
only NULL selects the right value. NULL, FALSE, INT0, empty STRING and STRING0
remain distinct, and truthy shorthand preserves its original STRING10 or BOOL.

One disjoint COALESCE operand clause reuses the existing typed-value selector.
Its single declaration moves forward; its body is unchanged. Each new recursive
call descends a proper child. Existing operand-to-TERNARY delegation takes one
same-node step before selecting proper children, so every mutual cycle reduces
finite AST height. No tag is inferred from an echo byte sequence.

Root and complete proper-child SOURCE, including keyword NAME children and
selected/skipped metadata, remain required. Certifying a skipped child is a pure
source check and performs no PHP effects. The FULL condition byte proof, old
trees, nonfolded CONCAT-root receipt, 46 dispatch guards, caches and owner/lifetime
bodies remain literal. Child CODE/read/pool/fold facts are observed separately;
the law does not invent a common child compilation shape or runtime carrier.

Old positive operand roots are disjoint from COALESCE and retain their exact
values. Historical refusal results keep their original source identities. The
maintained tests update exactly 17 obsolete expectations: ten new COALESCE
promotions and seven earlier delegation promotions. A static CASE bridge and one
fresh extraction preserve every other check, source, stage and count without
rerunning historical campaigns.
FLOAT/CV/nonquiet/NUL/owning children, wider parent contexts and lifetimes remain
partial. The outer certificate still requires the existing direct ternary-left
coalesce form and its supported CONCAT/NOT composition.

Fresh original-source observations distinguish executed SELECT/COALESCE events
from complete SOURCE nodes. Immediate AFTER PNULL for FULL selection or NULL-left
COALESCE is an enqueue placeholder, not a completed RHS tag. Enclosing COALESCE
LEFT and resolved SHORT conditions expose completed tagged values/carriers;
nonnull retained values are observed directly. The typed rule keeps its separate
quiet SOURCE proof. Native
originals execute once and their exact source paths, bytes, CWD and profile are
reused for production comparisons. The original CV prelaw timeout and failed
observer helper retain zero credit at the unchanged limits.

PHP 8.5.10 authorities are `zend_compile_coalesce`, `zend_compile_conditional` and
`zend_compile_shorthand_conditional` in `Zend/zend_compile.c`, and `ZEND_COALESCE`,
`ZEND_QM_ASSIGN` and `ZEND_JMP_SET` in `Zend/zend_vm_def.h`. Their selected-value
and NULL-versus-false behavior composes through these pure operands. The
[review](../../coverage/semantics/magic-property-methodclosure-static-raw-coalesce-operand-typed-ternary-left-coalesce-quiet-get-review.json)
keeps source comparisons, fixtures, observations and zero-credit failures distinct.
