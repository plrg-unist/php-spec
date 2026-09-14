# Function statics after dynamic string calls

Read [PLAN](../../PLAN.md), [PROGRESS](../../PROGRESS.md) and the accepted
[dynamic-call review](../../coverage/semantics/dynamic-call-review.json) first.
The complete PHP core remains the goal. Root must read the accepted checkpoint
before the proposed compiler111/runtime112 implementation starts; preparation
alone does not authorize source admission.

Current dynamic109/110 uses the existing named/unpacked send and default/type
receive paths. Initial parser-string, later compiled CONST and true runtime
callees retain distinct name/mode relations. Keep CODECALL_INIT, callee expression
and outer call lines separate. Selected true dynamic functions have no historical
name field. Fixed emitted names retain their source relation. Shared99 reference
returns and107/108 unpack result classification must continue to work.

Compiler7's bounded preparation is `.tools/compiler7-function-statics-next/`:
`PLAN.md`, `STARTUP.md`, `records14.json` and the frozen ef5238fe archive. It retains
fourteen ordinary native/parser/lint/request contexts on981/764 and four separate
opcode profiles. Replay those exact contexts on the accepted dynamic baseline;
do not repeat native runs merely to change the candidate identity. Runtime7 retains
five separate981 originals in
`.tools/runtime7-function-statics-next/`: four ordinary candidates for bare-null
aliases, recursive scalar/array initialization and prior-reference rebinding,
plus one catch-dependent initializer-failure observation. All remain Unsupported
on that baseline. Review10 reserves the disjoint suppression/type-error/retry contrast;
catch-dependent observations must remain explicit dependencies until supported.

The proposed slice is static bindings inside named user functions. Establish
compiler traversal order and declaration identity from pinned Zend source before
choosing descriptors. Duplicate names and `$this` have compile-phase priorities,
including declarations in dead branches. Constant/no-default and evaluated
initializers use different BIND paths. Initializers read the current locals and
parameters before binding. A cached null must be distinguishable from an entry
whose initialization has not succeeded.

Runtime design must give each persistent entry a clear owning reference cell.
Local unset or rebinding does not erase that entry. Recursive initialization can
initialize the entry before an outer initializer finishes; do not introduce a
speculative reentry lock. Review source-derived bind/initializer lines, cell
promotion and replacement, discarded initializer owners, saved frames, reference
returns and abrupt cleanup before finalizing a state schema. Preserve actual
first-state counterexamples before adding guards. Permit arbitrary consistent
initialized values/aliases; avoid reconstructing initialization history.

Retain complete old-state bridges with only the precise new schema additions,
if any. Require ordinary sources, native compile priorities, actual paused-state
negatives/positives and dense ownership/resumption gates. Full integration981/764
is historical after109/110; a focused new gate does not relabel it current.

Main-unit statics, closure/arrow identity, inherited/trait/method tables, object
and destructor behavior, exception/catch retries, builtin bodies/defaults/callbacks,
Traversable and dynamic-source lifetime remain required. Neither this successor
nor the dynamic milestone closes the function/callable or storage families.
