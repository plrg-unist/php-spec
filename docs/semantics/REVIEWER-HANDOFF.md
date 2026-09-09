# Independent review handoff

Continue the complete-core goal with small independently reviewed commits; never
push. [PROGRESS](../../PROGRESS.md) is the current checkpoint. Runtime bridge owns
storage/tasks/source dispatch; compiler owns lexical and ordinary compilation,
frontend/schema changes and compiler descriptors. Reviewer owns independent
evidence, discrepancy history, inventory and progress. Coordinate watched-file
freezes and stage only owned files. Selected tests do not close a family.

## Current gate

Source control `d87f3f9f` passed **747 exact source comparisons +25 outcome
negatives**. Independent review adds 67 exact sources, 20 alternate compiler cases,
16 metadata controls and two path-order checks. Canonical control state checks
pass 40 sources/41 states/1,231 assertions; dense replay adds 2,493 assertions over
163 budgets for each of three nested/jump/COW programs. Source compiler 789 lint
cases +15 emission observations, ownership 617+96/5,434, origins 25/333 and compiler
bridge 15/148 share the final closure. See
[control review](../../coverage/semantics/control-review.json).
Accepted fingerprint: `ff73f0181b1fb5b61beb3427967cc05c20bc78d91f3957eba10f0ab4654dd7af`
(767 files). Legacy traversal retirement `846dc3d2`, temporary-lvalue rejection
`32d4163a` and checked body metadata `3a137a36` remain covered.

The inventory contains 169 constructors and 306 obligations. Only
`validation.oracle-pin` closes, against the archived six-case source evidence
and independent review at `6b5981cc`. That scope establishes oracle selection,
measured runtime identity/hash and supplied profile plus recorded build
provenance. It does not establish effective INI measurements from that source
campaign, a fresh rebuild, or a PHP semantic family.

## Evidence and commands

Run from the project root. `.tools/php/bin/php` is the sole native oracle:
PHP 8.5.10 CLI NTS 64-bit, source pin
`34308a6666b2d489c509541ea9befea9e2b42348`. Never substitute host PHP. Runtime
semantics remain pure `.watsup`; host services do not evaluate PHP operations.

- `python3 tests/semantics/validate.py`: full original-source campaign. Compare
  exact stdout, stderr and status; native success alone is insufficient.
- `python3 tests/semantics/source_compiler.py`: ordered compile diagnostics,
  descriptor roles, effective lines and malformed metadata/export boundaries.
- `python3 tests/semantics/namespace_constants.py`, `constant_context.py`,
  `runtime_compiler.py`, `control_flow.py`, `control_compiler.py`,
  `source_origins.py`, `compiled_pools.py`, `ownership.py`,
  `dimension_read.py`, `dimension_write.py`: applicable helper/source contracts
  under `tests/semantics/`. Helpers build their runner briefly at startup;
  serialize builds. Source validation can run alongside a stable helper gate.
- `python3 tests/source_context_metadata.py` and
  `python3 tests/semantics/source_occurrences.py`: checked metadata and occurrence
  transport. Use actual byte/encoding profiles, not edited ASTs as source evidence.
- `make test`, `make inventory`: bounded syntax/metadata checks. The 30,980-record
  audit in `coverage/frontend-syntax-repair.json` is historical after metadata
  changes. Its copied binaries establish no rebuild or portability claim. Full
  final syntax validation and offline closure audit remain required.
- `python3 scripts/check-semantic-inventory.py` and
  `python3 tests/semantics/evidence.py`: evidence integrity and rejection tests.
  `--complete` must reject unfinished entries and stale closure fingerprints.

Reports record exact commands, source bytes, raw process streams/status and
implementation fingerprints. Every final acceptance needs a stable current
closure; interrupted runs and reports predating watched edits are historical.
The checker enforces evidence bindings, not semantic branch completeness or
reviewer independence. Human review establishes those. Preserve original failed
observations and append resolutions separately; never rerun a script that
overwrites a tracked discrepancy capture.

## High-risk next witnesses

- Ordered compilation must finish before runtime WORK executes. Compile failure
  suppresses preceding runtime output while retaining earlier compile warnings.
  Structural preorder is an occurrence index, not PHP compiler order.
- Constant prepass FACTS, ordinary code-generation EXPRESSIONS and actual ACCESS
  roles are distinct. Only compiled PPR operands consume pool constants. Skipped
  children have no executable roles. Partial rewrites retain their effective
  compiler lines; cached occurrences retain their first rewrite provenance.
- Units and paths select occurrence identity. Equal AST metadata cannot choose
  identity. Repeated loop execution must reuse the same installed literal while
  distinct NaN-array occurrences remain distinct. Test global `NAN`, imported
  constant aliases and namespace late fallback separately.
- Permanent unit pools retain roots across cleanup and budget resumption.
  Compiler store/cells/environment cannot enter a pool. IDs are remapped before
  runtime use. Uncollected cycles retain reference-owner multiplicities; do not
  simulate collection by pruning reachable-owner information.
- Reference assignment targets replace an element's alias rather than write through its previous
  cell. CV reference sources initialize after target acquisition; non-CV source
  captures own their cell across target COW. String targets coerce keys before
  a delayed CV RHS is read; too-negative writes return NULL before RHS conversion, and
  reference/nested errors have distinct ordering. Preserve captured locations.
- Bare `break` uses the exact terminator token start line. Closing-tag tokens may
  contain a newline. Explicit depth expressions have a different Zend AST shape:
  negative syntax is unary, and compile_break_continue does not first fold it.
  Do not apply bare-statement line rules indiscriminately to depth expressions.
- Checked body metadata distinguishes brace/colon synthetic lists from single
  statements, including empty/comment-only for bodies. Preserve its token-derived
  transport and explicit semantic consumption; do not guess from nearby nodes.
  Metadata type/range checks do not authenticate edited in-range source positions.

- Next truth operators need separate compiler/runtime decisions: constant-left
  false&& and true|| may skip RHS compilation, while a runtime variable does not.
  Global NaN short-circuit conversion warnings may occur at compile time; unary
  not/ternary and namespace late NaN differ. The 63 tracked
  [oracle witnesses](../../coverage/semantics/truth-oracle-review.json) cover phase,
  prepass, selected-child copy/identity and grouping effects. Array prepass can
  replace a ternary with a nonconstant child, preserving delayed reads; ordinary
  ternary materializes a value. Checked `parenthesizedConditional` metadata now
  distinguishes grouping for ordinary static checks after applicable rewrites.

## Remaining boundaries

Runtime next connects truth/short-circuit/ternary/comparisons, then compound
lvalues and remaining numeric operations/casts. The compiler successor coordinates
truth folding before unpack/destructuring and declaration/default/frame work.
Array unpack/destructuring precedes foreach cursor/ownership integration. Objects, linking, dynamic
sources, callbacks, collection and resumable lifetime remain incomplete.
Frontend early compile restrictions (including some parameter/type restrictions)
still need proper source-phase treatment. The intentional namespace-relative
`static` divergence remains separately recorded with source activation proof
pending. See [DISCREPANCIES](DISCREPANCIES.md) for unchanged raw failures and
resolutions. Production no longer exposes bare `run_source`/`run_statements` or recursive
availability/classification traversals. Source-origin fixtures alone define an
explicitly unchecked task wrapper; public execution uses full ordered compilation.
