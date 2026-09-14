# Main-script statics after named-function statics

Read [PLAN](../../PLAN.md), [PROGRESS](../../PROGRESS.md) and the accepted
[named-function review](../../coverage/semantics/function-statics-review.json)
before source admission. Complete PHP core remains the goal. Compiler111/runtime112
admit named-function statics on999/0484; main-script declarations remain Unsupported.

The bounded next slice is static declarations in the initial main script. Reuse
the pinned initializer folding, CV inventory, declaration priority and source-line
facts where applicable. Main binding must synchronize the global table and direct,
dynamic and `$GLOBALS` views. The named-function hidden-CV evidence does not
establish main-scope behavior. A lexical unit/declaration origin can identify an
initial-script slot; include/eval op-array lifetime requires separate evidence.

Compiler7 preparation is `.tools/compiler7-main-statics-next/`: `PLAN.md`,
`STARTUP.md`, `records6.json` and immutable `originals.tar.xz`, SHA256
`cc3206313ec060a69f337fc1d68d361ab563c1e1f8e7886cae4a415947019852`.
It retains172 payloads, six exact native/source/request contexts on990 (five normal,
one duplicate declaration error), and three separate opcode profiles. Replay the
six original contexts on the accepted successor without repeating native runs.
Preparation alone does not authorize source admission or establish a schema.

Before implementation hardens, independently review current-main versus active
function identity, stored/null/dynamic initialization, cell ownership, global
rebinding and unset, and source-authenticated MAIN descriptors. Preserve actual
cross-unit/nested-function origin counterexamples before finite guards. Admit
arbitrary consistent cell values and local aliases; do not reconstruct execution
history. Retain exact tools, modes, request profiles, raw workers, failures and
bounded state/resumption/compatibility evidence on frozen identities.

The previous105 paused-receive ambiguity was repaired on442a, and0484 adds only
its maintained protocol regression. Keep those semantic/test bridges explicit.
Closure/arrow/method/trait/inherited static identity, objects/destructors,
catch/retry, include/eval lifetime, other callable protocols, full current syntax
and a fresh network-isolated offline audit remain required. No static/storage or
callable family is complete.
