# Array/reference implementation handoff

Read PLAN.md, PROGRESS.md, DESIGN.md and the php/php-spec/p4-spectec skills first.
The current source machine supports ordinary ordered arrays, delayed dimension
reads, simple/nested writes, append and unset. Variable-cell aliases work. Embedded
array references, foreach, callbacks and source GC are still pending. Do not infer
source support from the existing ALIAS constructor or pure ownership helpers.
Reference-assignment expressions now return owning `REFERENCE` operands. Their
cell identity is captured but their contained value is read by the consumer;
keep this distinct from both a captured `KNOWN` value and a delayed `VARIABLE`.

## Entry points

- `20-machine.watsup`: PHP values/completions, static availability checks and
  source/compiler line functions. `30-storage`: cells, operand/base/path/task
  domains, state, variable binding operations.
- `36-arrays`: ordered entries/history, key coercions, reads, identity, union,
  isolated constant classifier. `37-array-locations`: location acquisition and
  conditional shallow path copying. `38-array-unset`: unset contexts.
- `39-ownership`: allocation graph, root projection, owner counts, RC pruning,
  separate mathematical cycle collection. Source driver prunes completed tasks.
- `40-control`: driver and variable/scalar tasks; `41` array literals/reads;
  `42` assignments; `43` unset. Modules are ordered in `modules.json`.
- `tests/semantics/validate.py`: exact original-source differential observations;
  `--prefix` runs a named subset plus all negatives. `ownership.py`: helper-only
  allocation invariants. Reviewer-owned `conformance/` contains oracle targets,
  including pending references/GC/literal-identity cases, not source pass claims.

## Next bounded increments

1. Array write/unset entry now moves captured path/RHS inputs into `HELD` before
   internal borrowed `RESULT` lookups, then restores earlier `HELD`. The driver
   prunes after completed tasks and releases terminal abrupt temporaries; budgets
   retain interrupted roots. Binary consumers also hold captured operands while
   resolving borrowed values. Location COW clears borrowed `RESULT` and prunes
   with live inputs held. Scalar/read helpers still require resumable roots before callbacks.
   `CELL`/`LOCATION` remain borrowed for admitted variable-only references;
   `zend_compile_assign_ref`/`ZEND_MAKE_REF` identify the precise future owned
   acquisition cases. Extend task-root dispatch whenever adding captured tasks.
2. Conditional COW and singleton unwrapping now have pure helper rules; validate
   them through source embedded references next. `zend_array_dup_value` unwraps a
   singleton reference except when its value is the source container itself.
   Union duplicates left entries this way; right-merge singleton wrappers unwrap
   even for source-self references (`zval_add_ref`). Conflicting keys skip copying.
   Entry copying counts a pruned graph projection rooted at its borrowed source;
   it leaves caller allocations intact for constant-classifier local builders.
   Unreachable cycles remain owners until collection; dead acyclic allocations do not.
3. Admit literal/element reference acquisition and assignment in small reviewed
   increments, preserving designation and diagnostic order. Reuse singleton,
   shared-container, nested-reference and cycle oracle targets before foreach.
4. Before repeated literal execution, add explicit source-unit/compiled-occurrence
   identities and persistent literal-pool roots. One constant literal occurrence
   can return the same container across iterations/calls; separately written
   identical literals differ. Editable metadata/AST structural equality is not an
   occurrence identity. Dynamic literals still allocate per evaluation.

## Discriminators to preserve

- `$a[0]=$a` captures its direct RHS before acquiring the location. Dynamic root
  names and variable aliases can instead form cycles. Terminal append consumes
  delayed RHS before overflow; keyed assignment designates the slot first.
- Dynamic array base names, root reads and nested keys have delayed/captured
  descriptors independent of scalar arithmetic operands. The recursive `pbase`
  rules already have independent sequencing regressions; avoid replacing them
  with eager evaluation.
- Same-container strict identity succeeds even with NaN. Distinct containers
  recurse, comparing count/keys before values; recursive comparison guards active
  left container IDs and throws a PHP Error instead of getting stuck.
- Missing string array-key diagnostics truncate at NUL; missing-variable names
  preserve NUL. Undefined literal keys suppress null-key deprecation; reads and
  writes do not. Terminal unset suppresses it; intermediate unset retains it.
- A dead uncollected cycle can retain a reference owner and change later singleton
  copying. `array-{uncollected,collected}-cycle-reference` targets distinguish99
  from19. Pure graph collection does not model triggers, counts or destructors.

## Validation and coordination

Run `python3 tests/semantics/ownership.py` and the full source validator after
root/COW changes. The source helper executable compiles every listed module, so
`bin/php-semantics FILE` is also a useful checked smoke test. Final reports require
stable dependency fingerprints: coordinate a brief no-edit interval with the
static/signature worker and independent reviewer. Generated reports are historical
snapshots; changing shared spec/tests/scripts invalidates a report's current-closure
claim. Commit reviewed bounded slices with DESIGN/PROGRESS kept honest.

The startup profile is fixed in `tests/semantics/profile.json`; use only its pinned
local PHP oracle. The whole core inventory remains far from complete. Calls,
types/class activation, handlers, object protocols, generators/fibers, dynamic
sources and lifecycle work are separate pending phases, not helper fallbacks.
