# Core semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit; [plan](PLAN.md),
[contract](docs/semantics/CORE.md), [inventory](coverage/semantics/features.json).
Complete core remains the goal. Syntax coverage is not semantic coverage.

## Milestones

| Milestone | Deliverable | Current status |
| --- | --- | --- |
| 0a–b | Contracts, inventory, checked runner and source harness | Complete — bounded bootstrap |
| 1a–c | Integers, bytes, binary64, conversions and power | Partial — scalar/array operator and cast source paths reviewed |
| 2a | Slots, aliases, frames and access modes | Partial — bindings/references reviewed; calls and frames pending |
| 2b | Arrays, strings, lvalues and sequencing | Partial — reads/writes/updates and omissions reviewed; unpack/list/foreach next |
| 3a | Control, exceptions, diagnostics and unwinding | Partial — conditionals/loops/jumps reviewed; exceptions pending |
| 3b | Calls, closures and independent static checks | Partial — static helpers reviewed; source activation pending |
| 4a–b | Linking, objects, traits, properties and internal protocols | Partial — local headers/relations reviewed; execution pending |
| 5a | Dynamic sources, autoload and explicit services | Pending |
| 5b | Generators/Fibers, lifetime, collection and callbacks | Pending |
| 6 | Full inventory/review closure, differential campaign and offline audit | Pending |

## Ownership and handoffs

- Runtime successor: storage/source integration; `runtime3` is handing over. Immutable raw-output fix comes next, then unpack/destructuring/foreach.
- `compiler4`: paired compiler/frontend work, then declarations/frames and class lookup.
- Independent reviewer: evidence, inventory, phase ledger and concise status/docs. `compiler3` is handing over after this checkpoint.
- Root orchestrates; stage owned files, commit reviewed increments, never push. Use canonical-root Dune builds and coordinate shared binaries.

[Runtime](docs/semantics/RUNTIME-SUCCESSOR-HANDOFF.md),
[compiler](docs/semantics/COMPILER-HANDOFF.md) and current
[reviewer](docs/semantics/REVIEWER-HANDOFF.md) handoffs retain exact interfaces and history.

## Latest accepted checkpoint

Array-unpack code **`4ca826d2`** and author evidence **`7ac2519f`** pass
**155 exact sources +24 outcome negatives**, 31 state programs/2,454 assertions
and 42 compiler lints plus 10 metadata/descriptor controls.
[Independent acceptance](coverage/semantics/array-unpack-review.json) verifies
all ordered raw rows, 154 original memberships, and eight additional source/state
programs/1,368 assertions. The formerly Unsupported empty spread is now a source
pass. Array spread is partial until Traversable objects/callbacks are implemented;
argument unpacking is separate. Full current source validation follows the combined
container checkpoint; the full ordinary report below remains historical.

Ordinary operator/cast code **`dba21cee`**, reports `a3290ae3`/`e397b137` and
independent review `2ab579eb` pass **4,407 exact sources +25
outcome negatives** on `a8f6aa0c` (799 inputs). Independent
[raw audit](coverage/semantics/ordinary-campaign-audit.json) verifies every ordered
ID, source byte/hash and stdout/stderr/status, 16 retained archive groups and 13
current reports. The [review](coverage/semantics/ordinary-review.json) also binds
62 independent sources, 25 state programs/2,875 assertions and 4,449 compiler lints.
The catalog includes 1,506 new operator selections and 262 omission prerequisites.
Seven retained request-environment cases remain Unsupported, excluded explicitly
from agreement counts; objects and complete constructor families remain unfinished.

Ordinary numeric/byte operators, five casts, bitnot and void now preserve delayed
CV reads, computed operand copies, explicit conversion diagnostics, COW and cycles.
Parser-folded concat names keep their actual parser designation. Concat separates
compiler scalar conversion from runtime array conversion and delayed reads.
[Contract](docs/semantics/ORDINARY-OPERATORS.md) records these decisions.

The accepted nullable/context prerequisite `9b82507a` preserves ordinary array
omissions, original indices and compiler diagnostic context. Narrow first-hole,
concat, nullary and clone metadata are justified by retained original sources;
five old syntax exemptions are retired. Required classconstant lookup remains an
explicit boundary where its value affects branch selection. Unsupported is not
resolution. Compound `63028b5a`, incdec `7d5718fb` and wrapper `84d70299` contracts
remain covered by the current campaign; their original failures and prior report
identities remain in linked evidence and handoffs.

Inventory remains **169 constructors/306 runtime obligations**, with 70 field
domains. Only oracle identity closes. Prepass traversal, helper tests and syntax
acceptance never establish ordinary source execution or full family coverage.

## Next bounded work

Raw output protection **`de04828e`** now creates an exclusive file for every run.
[Independent review](coverage/semantics/raw-output-review.json) repeats the same
selection twice (one source +25 negatives each), verifies distinct paths and
preserves both prior runs and historical selected/full evidence byte for byte.
The accepted full campaign above is historical after this harness change; its
semantic rules are unchanged. The earlier exact
[recovery proof](coverage/semantics/ordinary-selected-raw-recovery.json) remains preserved.

The immutable `.tools/runtime-list-candidate` contains unpublished list,
constant-result effects and nonvariable-coalesce rules. Independent 44 source
controls pass. Further [independent review](coverage/semantics/list-mechanism-review.json)
reproduces 263 archived agreements plus the recorded header Unsupported, passes
23 mechanism checks and 12 dense programs/6,192 assertions. Twelve reused private
source filenames are preserved as an evidence incident; archived bytes remain intact.
The `http_response_header` and five quiet-access boundaries remain pending. Additional foreach originals justify key-reference
syntax and list keys for later compiler rejection; three syntax exemptions need
proper retirement after representation/phase gates.

A list assignment may return a compiler-known constant while still emitting
writes. Parent folding must retain ordered effects separately; casts/coalesce and
AST prepass traversal have different folding rules. Four actual draft failures
and independent effect/line controls are retained. This mechanism is not yet
production-admitted. Its independent ownership, resumption and occurrence gates
pass; final compiler-consumer integration remains a publication gate.

Then complete request environment, named/class/magic lookup, quiet assignments,
destructuring/foreach and object unpacking, calls/frames/declarations, linked objects/properties,
exceptions, dynamic sources, resumable services, lifetime and core intrinsics.
Ordinary-library exclusions cannot discharge required core behavior.

## Validation cadence and closure

Each coherent increment needs exact source/native originals, focused compiler
phase/line checks, appropriate state/ownership/resumption gates and independent
review. Run evidence/inventory preflight after watched changes, before long runs.
Commit compatible prerequisites separately; admit mutually dependent source rules
atomically. Preserve failing observations before repair and keep docs current.

Run full current source campaigns at meaningful integration checkpoints:
unpack/list/foreach; calls/declarations/frames; linked objects/properties;
exceptions/dynamic/resumable services. Unresolved shared numeric, compiler or
ownership risk can require an earlier broad run. A changed implementation leaves
the previous full report explicitly historical; never relabel it as current.

[Discrepancies](docs/semantics/DISCREPANCIES.md) distinguish engine behavior from
specification defects. Namespace-relative `static` remains the sole intentional
divergence, with source activation pending. The 30,980-record syntax audit is
historical; final full syntax validation, fresh offline rebuild, current source
closure and every core obligation remain mandatory. Unsupported, tool failures,
timeouts and interrupted runs never pass. Final design/departure reporting waits
until the entire requested goal is complete.
