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
Both acquired and new cells must hold null/bool/int/float when retargeting
between different reference cells. Ordinary live instance-property sources may
constrain either cell; their metadata adds no owner. Singleton COW strips the
copied entry's wrapper even when it has type sources, while original aliases and
shared copies retain typed rejection/coercion. For debt-bearing cells, source
objects and their actual property aliases must survive logical pruning. The
[typed-source review](../../coverage/semantics/array-literal-float-ref-types-review.json)
checks both typed sides and multiple live sources. Debt cells must keep positive
effective counts. Owning values, static/hooked/queued or retired sources,
coercion/backing records, active collection, effective-zero retirement and
outstanding debt at request end are explicit Unsupported before pruning. Isolated
compiler images reject both runtime fields. The [deficit review](../../coverage/semantics/array-literal-float-ref-deficit-review.json)
keeps fresh balanced sources separate from the earlier
[positive-owner slice](../../coverage/semantics/array-literal-float-ref-key-warning-review.json).

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
