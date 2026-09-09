# Reference wrappers and dimension fetching

Reference acquisition records wrapper identity separately from the backing cell's
value and ownership count. A wrapper survives writes and removal of its last
alias while the variable remains bound. Removing the variable and creating an
ordinary binding allocates a fresh, unmarked cell. Copying a reference value does
not mark the destination; array copy and union retain their existing singleton
reference unwrapping rules.

Generic dimension fetching through a wrapper containing `false` creates an array
without the false-to-array deprecation. An intermediate unset through that wrapper
also skips the deprecation. Final dimension assignment and final unset use their
own Zend paths and retain the warning. The distinction applies to root variables
and aliased array entries, including singleton wrappers.

`REFCELLS` records stable cell IDs. It adds no heap edges or roots and cannot keep
an unreachable allocation alive. Dead markers are inert because IDs are never
recycled. Constant compilation rejects reference markers in isolated compiler
memory; installing a valid unit preserves runtime markers.

`tests/semantics/reference_wrappers.py` checks original source regressions,
copying and rebinding, budget resumption, ownership graphs, cycle collection and
compiler-pool isolation. The cycle check exercises the pure collection helper;
it does not admit a source-level `gc_collect_cycles` call. Prior mismatches remain
in the `coverage/semantics/false-reference-*` archives.
