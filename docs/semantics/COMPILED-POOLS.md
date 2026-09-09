# Permanent compiled constant pools

`32-compiled-pools.watsup` installs compiler-owned constant arrays into runtime
storage without exposing them to temporary-root cleanup. This is an internal
storage interface. Source execution does not yet install a pool or consume a
compiled fact; the ordered compiler and source bridge have separate gates.

Each `ppool` belongs to one compiled source instance and maps structural paths
to values. `S.POOLS` contributes permanent roots to the allocation graph, separate
from `HELD`, task operands, and borrowed result scratch. Clearing temporaries or
finishing an abrupt task leaves those roots intact. A budget interruption retains
both permanent and temporary roots. No compiled-unit teardown is modeled yet;
the installed pool lasts for the machine's lifetime.

`$install_pool` accepts a canonical `pcunit`, isolated array backing, allocated
array IDs, and unique path/value entries. It checks that paths select expressions,
array-valued facts select live allocations, and live tables contain direct values
whose child arrays are also allocated. Cell allocations, live reference entries,
missing children, duplicate allocations, duplicate paths, inconsistent source
units and repeated installation are rejected as internal Unsupported states.
This validates the storage boundary; it does not prove that an arbitrary supplied
value is the result of compiling its expression. The caller must supply reviewed
compiler output and reject compiler states containing variable cells or bindings.

Installation shifts array IDs by the entire existing backing length, including
reclaimed slots. It remaps nested direct values and every exported constant value,
preserving keys and next-index history. Historical slots remain backing only;
their contents do not acquire owners. Existing runtime arrays, cells, aliases,
scratch values, tasks and held owners remain intact. Later dynamic allocation
starts after the appended backing. Two instances of identical checked source have
different pool IDs; repeated lookup of one instance/path returns the same ID.

A permanent array root also ensures a runtime variable's first mutation separates
the shared constant container. Array identity remains observable with NaN: two
lookups of one array compare identical, while distinct equal-looking NaN arrays
do not. These helper checks exercise identity and COW after cleanup; they do not
claim source-level repeated literal execution or immutable-array implementation
details beyond this storage model.

Run `python3 tests/semantics/compiled_pools.py`. Its checked original source
provides occurrence identities for constructed storage tests. It includes
malformed boundaries, persistent roots through normal/abrupt/budget states,
nested remapping, duplicate source instances, retained runtime cycles, COW and
100 acyclic allocation graphs checked against a separate reachability traversal.
The report is `coverage/semantics/compiled-pools.json`. Run ownership and the full
source regression after root-domain changes.

The next bridge must merge partial constant facts and ordinary compiled operand
results, rejecting conflicting values at a shared path, and retain effective
compiler lines separately. It must install each source instance once and dispatch
by the task's explicit unit/path. It must not rebuild pools during execution,
choose paths by AST equality, or transplant the isolated compiler's `HELD` list
into runtime temporaries. String/scalar read activation also requires the exact
constant-prepass suppression and partial-fold behavior described in
[constant context](CONSTANT-CONTEXT.md).
