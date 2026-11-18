# Typed coalesce conditions in quiet Get selectors

FULL typed ternaries retain the existing quiet condition-byte proof and add one
fallback for a COALESCE condition root. Only when the old proof returns None may
the existing typed operand proof supply the exact COALESCE value and its echo
bytes. This admits typed TERNARY/COALESCE children while preserving NULL-only
selection and the distinction between None and Some(empty bytes).

NULL, FALSE and empty STRING produce Some(empty); INT0 and STRING0 produce
Some(ASCII0). These are false conditions. BOOLtrue and STRING10 are true. The
unchanged non-NUL/truth test chooses the existing FULL arm and retains its exact
scalar tag. The SHORT rule and shared raw byte tree remain literal, so this does
not extend unrelated CONCAT/NOT/Boolean parents or non-COALESCE condition roots.

Every old condition Some(bytes), including UnaryPlus INT forms not admitted
by the typed operand helper, returns those same bytes through the first branch.
Old positive typed trees therefore remain pointwise equal. New mutual cycles
pass proper COALESCE children before another FULL condition, reducing finite AST
height. Complete selected/skipped SOURCE and metadata remain required; checking
skipped source is pure. No child fold/read/pool state or runtime carrier is
invented. Root receipt, 46 dispatch guards, caches and owner/lifetime bodies stay
unchanged.

The maintained prior COALESCE review changes only S_coalesce_bound_10 from
refusal to PBOOLfalse. A static CASE bridge preserves all other sources, stages,
checks and counts; its exact old shape is tested in the fresh values cut. Prior
native/source/fixture campaigns keep their original identities. UnaryPlus +1/+0
and an already-supported SHORT condition are retained controls with zero new
behavior credit.

Fresh source observations keep executed SELECT/COALESCE snapshots distinct from
complete SOURCE nodes. Immediate AFTER PNULL queues work rather than reporting
a completed RHS tag. Resolved conditions and enclosing COALESCE LEFT expose
completed values; nonnull retained copies are direct observations. Native
originals execute once and production comparisons reuse their exact bytes,
paths, CWD and profile.

PHP 8.5.10 authorities are zend_compile_conditional, zend_compile_coalesce and
zend_compile_shorthand_conditional in Zend/zend_compile.c, with ZEND_COALESCE,
ZEND_QM_ASSIGN and ZEND_JMP_SET in Zend/zend_vm_def.h. FLOAT/CV/nonquiet/NUL/owning
children, UnaryMinus expression roots, other new condition roots, wider parents
and lifetimes remain partial.
The [review](../../coverage/semantics/magic-property-methodclosure-static-raw-coalesce-condition-typed-ternary-left-coalesce-quiet-get-review.json)
keeps fresh comparisons, fixtures, controls and preparation failures separate.
