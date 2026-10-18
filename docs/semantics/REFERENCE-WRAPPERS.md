# Reference wrappers and dimension fetching

Reference acquisition records wrapper identity separately from the backing cell's
value and ownership count. A wrapper survives writes and removal of its last
alias while the variable remains bound. Removing the variable and creating an
ordinary binding allocates a fresh, unmarked cell. Copying a reference value does
not mark the destination; array copy and union retain their existing singleton
reference unwrapping rules. Ordinary writable-name fetching initializes a missing
slot without creating a wrapper; only reference-source acquisition marks it.
This distinction also applies to computed variable names.

Generic dimension fetching through a wrapper containing `false` creates an array
without the false-to-array deprecation. An intermediate unset through that wrapper
also skips the deprecation. Final dimension assignment and final unset use their
own Zend paths and retain the warning. The distinction applies to root variables
and aliased array entries, including singleton wrappers.

`REFCELLS` records stable cell IDs. It adds no heap edges or roots and cannot keep
an unreachable allocation alive. Dead markers are inert because IDs are never
recycled. Constant compilation rejects reference markers in isolated compiler
memory; installing a valid unit preserves runtime markers.

`LITERALREFRETAINED` records acquired `ADD_ARRAY_ELEMENT` owners left on old
wrappers when a lossy-float key handler retargets the element CV. Each unmatched
occurrence contributes one request root, including repeated IDs, through normal
and abrupt cleanup. Stable same-cell insertion transfers that owner into its array alias.

`LITERALREFDEBTS` records omitted owners on different reference cells inserted
after that callback. Logical aliases remain intact; effective owner counts and
pruning counters subtract the debt multiplicity. Retaining an indebted cell first
cancels one debt, and owing a retained cell first cancels one positive owner.
Thus inverse retargeting restores ordinary ownership without spurious GC roots.
Primitive acquired and new cells may carry ordinary live instance-property
sources; their metadata adds no owner. Singleton COW strips the
copied entry's wrapper even when it has type sources, while original aliases and
shared copies retain typed rejection/coercion. For debt-bearing cells, source
objects and their actual property aliases must survive logical pruning. The
[typed-source review](../../coverage/semantics/array-literal-float-ref-types-review.json)
checks both typed sides and multiple live sources. Untyped CELL payloads may also
be mutable nonpool flat arrays of DIRECT null/bool/int/float entries. The CELL
keeps one child-table edge; its debt never subtracts from HARRAY owners. A singleton
outer copy unwraps the wrapper, then ordinary child COW separates array values.
Changing the child table leaves the same CELL debt in place. Old-array completion
also admits an ordinary-scalar DIRECT value. Its acquired count cancels an existing
debt first; otherwise the wrapper and its child remain owned for the request.
Repeated unmatched occurrences preserve multiplicity through normal and throwing
callbacks. The active builder cannot be either payload. The
[array-to-scalar review](../../coverage/semantics/array-literal-float-ref-array-scalar-review.json)
checks child COW after ordinary names disappear and debt cancellation. The
[flat-array review](../../coverage/semantics/array-literal-float-ref-arrays-review.json)
checks these counts through stable insertion, deletion, throw and inverse cleanup.
Debt cells must keep positive effective counts. Array-valued type sources,
nested/reference-bearing/string-leaf or pooled/immutable arrays, other owning
values, static/hooked/queued or retired sources,
coercion/backing records, active collection, effective-zero retirement and
outstanding debt at request end are explicit Unsupported before pruning. Isolated
compiler images reject both runtime fields. The [deficit review](../../coverage/semantics/array-literal-float-ref-deficit-review.json)
keeps fresh balanced sources separate from the earlier
[positive-owner slice](../../coverage/semantics/array-literal-float-ref-key-warning-review.json).

Ordinary by-value array CVs use separate `LITERALARRAYRETAINED` and
`LITERALARRAYDEBTS` fields for HARRAY counts. Their saved continuation owns the
pre-conversion table, rather than its original CV cell. Inserting a different live
table preserves the old count and omits one new-table owner; inverse retargeting
cancels both, while same-table insertion adds no bias. Only unmarked ordinary CVs
and mutable nonpool flat DIRECT null/bool/int/float tables are admitted. Combined
CELL/table debt safety uses logical pruning before subtracting either count bias;
positive flat table targets have no outgoing owner edges. Deletion/throw deficits,
restored COW and retired original CV cells are checked in the
[ordinary array-CV ledger](../../coverage/semantics/array-literal-float-array-cv-review.json).

`tests/semantics/reference_wrappers.py` checks original source regressions,
copying and rebinding, budget resumption, ownership graphs, cycle collection and
compiler-pool isolation. The cycle check exercises the pure collection helper;
it does not admit a source-level `gc_collect_cycles` call. Prior mismatches remain
in the `coverage/semantics/false-reference-*` archives.

`tests/semantics/write_fetch.py` retains computed-write regressions and checks
plain versus existing reference cells through writes, nested unsets and resumption.

[Container276](SOURCE-CONTAINER-WRITES.md) stages those false/undefined writable
callbacks and genuine array-reference assignment. Captured source cells own once;
simple source CVs stay delayed until target acquisition. Raw typed DIM_OP array
backing records its source in `CONTAINERINITS`, adding no owner or ordinary type
permission. Pointer COW transports that backing; whole-cell stores clear it.
