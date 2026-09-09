# Array/reference implementation handoff

Read PLAN.md, PROGRESS.md, DESIGN.md and the php/php-spec/p4-spectec skills first.
The current source machine supports ordinary ordered arrays, delayed array/string/scalar dimension
reads, simple/nested array and string writes, array append and unset. Variable-cell aliases and literal
references to direct/dynamic variables and writable array elements work, including
element reference assignment targets. String-offset reference and nested writes
produce their required errors. Foreach, callbacks and source GC remain pending. Do not infer
those paths from the ALIAS constructor or pure ownership helpers.
Reference-assignment expressions now return owning `REFERENCE` operands. Their
cell identity is captured but their contained value is read by the consumer;
keep this distinct from both a captured `KNOWN` value and a delayed `VARIABLE`.

The compiler/pool source activation is described in
[the runtime bridge handoff](RUNTIME-BRIDGE-HANDOFF.md).

## Entry points

- `20-machine.watsup`: PHP values/completions, static availability checks and
  source-location functions; effective compiler lines are retained separately in33. `30-storage`: cells, operand/base/path/task
  domains, state, variable binding operations. `31-source-origins` supplies
  checked unit/path task scopes; see [runtime origins](SOURCE-ORIGINS.md).
- `32-compiled-pools`: internal per-unit constant storage, disjoint array-ID
  installation and permanent roots; see [compiled pools](COMPILED-POOLS.md).
  Source execution invokes it through `33-runtime-compiler`.
- `36-arrays`: ordered entries/history, key coercions, reads, identity, union,
  pure operations shared with the constant compiler. `37-array-locations`: location acquisition and
  conditional shallow path copying. `38-array-unset`: unset contexts.
- `39-ownership`: allocation graph, root projection, owner counts, RC pruning,
  separate mathematical cycle collection. Source driver prunes completed tasks.
- `40-control`: driver and variable/scalar tasks; `41` array literals/reads;
  `42` assignments; `43` unset. Modules are ordered in `modules.json`.
- `tests/semantics/validate.py`: exact original-source differential observations;
  `--prefix` runs a named subset plus all negatives. `ownership.py`: helper-only
  allocation invariants. Reviewer-owned `conformance/` contains oracle targets,
  including pending references/GC/literal-identity cases, not source pass claims.

## Current invariants and next work

- Mutation helpers move their captured task inputs into `HELD`, clear borrowed
  `RESULT`/`BASE`, and restore earlier `HELD` on every outcome. Driver pruning
  happens after completed tasks. Terminal errors release machine temporaries;
  budgets retain them. No helper callback/suspension boundary is modeled yet.
- COW counts surviving owners after RC pruning, retaining uncollected cycles.
  Copies unwrap singleton ALIAS cells except source-self references. Union left
  duplication uses that exception; right merge unwraps every singleton wrapper,
  and conflicting keys skip copying. Captured operands remain rooted throughout.
- Element sources separate their path before promoting the final slot, returning
  a borrowed cell. Nonliteral-target/non-CV-source assignment explicitly owns it
  in `REF_DYNAMIC` or `REF_ARRAY`; direct literal names do not add that owner.
  `REF_ARRAY_CV` designates the target before initializing its source. Binding
  replaces the entry's alias; ordinary assignment writes through an alias.
- Literal reference entries acquire an owning temporary before delayed key
  conversion, then transfer it into the entry. The compiler constant-expression
  prepass has a distinct traversal, including append rejection; see below.
- [Scalar/string dimensions](DIMENSIONS.md) and the ordered compiler prepass are
  integrated. Next: control/loops, array unpack, destructuring and foreach.
  Runtime tasks now retain [source-unit occurrence identities](SOURCE-ORIGINS.md);
  permanent pools consume compiler facts by those identities. Pool roots are separate from task `HELD`
  and survive temporary cleanup. Equal subtrees and editable metadata are not
  occurrence identities. Foreach additionally needs persistent bucket/cursor
  state and mutation/reference interaction tests.

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
- Dynamic reference assignment consumes its target name before initializing a CV
  source; element targets designate the slot before CV acquisition. Non-CV sources
  are acquired earlier; literal references acquire before delayed keys. Literal
  float variable names are CVs, while unary and named constants are dynamic.
- `$x=&$a[]` works, but `[&$a[]]` fails during the array constant-evaluation
  prepass. It visits every value then key even for by-reference entries, retaining
  the array's ambient compiler line. Its recursive cases stop at assignments and
  variable names: `[&$a[($x=&$b[])]]` therefore remains valid. Keep this narrow
  checked traversal aligned with the compiler-context work.

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
