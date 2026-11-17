# Nested typed ternary operands in quiet Get selectors

The existing direct ternary-left coalesce certificate admits authenticated FULL
and shorthand ternaries recursively in its four operand positions: present FULL
arms and shorthand condition/fallback. Primitive values and constructor-known
STRING/BOOL results retain their existing proofs. Nested selection preserves
exact NULL, FALSE, INT0, empty STRING, STRING0, STRING01/10 and BOOLtrue tags.
Only NULL requests coalesce fallback; truthy shorthand retains its original value.

One disjoint TERNARY operand clause delegates to the existing typed-left selector.
Its single declaration moves forward for the mutual call. The delegation keeps
the same node; selection then descends only into FULL arms1/2 or shorthand
condition0/fallback2. Every mutual cycle reduces finite AST height. FULL conditions
keep the existing quiet byte proof. Both selected and skipped nested operands
authenticate complete proper SOURCE; genuine ABSENT differs from present NULL.

Previous primitive/CONCAT/Boolean operand successes remain literal and pointwise:
their root constructors are disjoint from TERNARY. Existing typed-tree and receipt
successes therefore retain their prior identities. Earlier blanket TERNARY operand
refusal controls remain historical at the prior source; this authenticated typed
grammar supersedes that frontier. No closed source, native or fixture evidence
is renewed.

The existing coalesce RHS domain, outer CONCAT/NOT composition, nonfolded root
receipt, 46 dispatch guards, cache and owner/lifetime bodies remain unchanged.
No native evaluation, echo-based tag inference or runtime carrier invention is
introduced. Bare COALESCE operand roots, FLOAT/CV/nonquiet/NUL values, owning
results and wider parents/selectors/lifetimes remain partial.

Fresh original-source observations keep executed SELECT events separate from
skipped SOURCE nodes and preserve actual child folds/reads/pools. Full AFTER PNULL
is an enqueue placeholder; resolved shorthand conditions and COALESCE LEFT expose
actual tagged values and carriers. The logical source certificate remains separate.

PHP 8.5.10 authorities are `zend_compile_conditional`,
`zend_compile_shorthand_conditional` and `zend_compile_coalesce` in
`Zend/zend_compile.c`, with `ZEND_QM_ASSIGN`, `ZEND_JMP_SET` and `ZEND_COALESCE`
in `Zend/zend_vm_def.h`. Nested selection composes their ordinary value-preserving
rules. The [review](../../coverage/semantics/magic-property-methodclosure-static-raw-nested-operand-typed-ternary-left-coalesce-quiet-get-review.json)
keeps source comparisons, fixtures, observations and the prelaw timeout distinct.
