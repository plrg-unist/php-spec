# Core semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit. Complete core remains the goal; see the
[plan](PLAN.md), [contract](docs/semantics/CORE.md) and
[inventory](coverage/semantics/features.json). Syntax coverage is not semantic coverage.

## Current checkpoint and next work

Variable/DIM `isset` and `empty` are independently accepted at **16035534** after
code **701e39fa**, runtime evidence **65cefcc1** and compiler evidence **72c30740**.
Current inputs: **835/afbaa198**. The [review](coverage/semantics/isset-empty-review.json)
binds232 exact sources +22 separate controls, author9 state programs/4,230 assertions,
independent7/2,655 and12 fresh canonical CLI comparisons. Four GLOBALS temporary/key
cases remain Unsupported. [Contract](docs/semantics/ISSET-EMPTY-REVIEW.md) records
terminal string rules, quiet ancestors, effects, static rejection and cleanup.

Next, complete request bootstrap and GLOBALS access/snapshots. Ordered CV compiler
facts are reviewed; compiler AUTOGLOBALS642 activation ordering has
[compiler-only independent acceptance](coverage/semantics/autoglobal-compiler-independent-review.json)
at a2953bce. Its canonical/runtime pairing remains pending. The [request provider](docs/semantics/REQUEST-INPUTS.md) supplies
explicit external clock/environment inputs, with native transport accepted at
be12200b/9a5b11e1. Its two fresh copied-source builds passed in separate network
namespaces with identical provider bytes. This does not admit PHP bootstrap rules
or replace the eventual whole-project offline audit.

After the paired request/GLOBALS increment, run the full quiet/CV integration
checkpoint before broader calls/frames. Then continue declarations, linked objects,
exceptions, dynamic sources, resumable services, lifetime and core intrinsics.
The twelve old container controls remain required: seven request-environment,
three object quiet forms, return and nullsafe-reference iterable compilation.
The guarded `??=` GLOBALS original and four isset/empty GLOBALS controls also remain
separate pending observations. Ordinary-library exclusions cannot discharge core work.

## Milestones

| Milestone | Status |
| --- | --- |
| 0a–b: contracts, inventory, checked runner, source harness | Complete for bounded bootstrap |
| 1a–c: numeric/byte conversions and operators | Partial; admitted scalar/array paths reviewed |
| 2a–b: storage, references, arrays, strings and sequencing | Partial; request/GLOBALS and object protocols pending |
| 3a: control, exceptions, diagnostics and unwinding | Partial; loops/jumps reviewed, return/frames and exceptions pending |
| 3b: calls, closures and static checks | Partial; source activation pending |
| 4a–b: linking, objects, traits and properties | Partial; header/relation helpers reviewed, execution pending |
| 5a–b: dynamic sources, services, resumability and lifetime | Pending |
| 6: complete inventory/review, differential campaign and offline audit | Pending |

Inventory: **169 constructors/306 runtime obligations**, with70 field domains.
Only oracle identity closes. Helper tests and compiler prepass traversal do not
close ordinary source-execution families.

## Historical accepted evidence

Earlier identities remain historical after watched changes; linked reports retain
exact originals, subprocesses, failures and scope.

- [Full container audit](coverage/semantics/container-campaign-audit.json):4,997 exact
  sources +24 controls on819/a0e3709a; author d71d4107, acceptance96cbf051. It checks26
  source archives, two compiler scopes and all4,407 earlier sources. Raw f0fc89de is
  immutable. Four of its16 core controls retired at quiet publication;12 remain.
- [Quiet/name access](coverage/semantics/quiet-access-review.json):a42fddfe/f3235689,
  295 sources +18 controls, author8/3,760 and independent6/2,277 state assertions.
  Compiler5,336 lints remain historical.
- [Coalescing assignment](coverage/semantics/coalesce-assignment-review.json):
  f073c750/1fe36808,137 sources +18 controls, author8/3,760, independent7/3,024 and
  nine descriptor controls/74 assertions;826/cc1d3e5e retained guarded834 dependencies.
- [Foreach](coverage/semantics/foreach-runtime-review.json):1f0e8810,155 sources,
  author9/6,498 and independent8/3,096; [destructuring](coverage/semantics/destructuring-review.json):
  77f8d3c0,283 selected sources; [unpack](coverage/semantics/array-unpack-review.json):
  4ca826d2,155 sources. The historical full container campaign includes these additions.
- [Earlier ordinary audit](coverage/semantics/ordinary-campaign-audit.json):4,407/25
  on a8f6aa0c; [exclusive raw-output protection](coverage/semantics/raw-output-review.json)
  preserves separate run files. Original defects and failed setups remain classified.

## Coordination and validation

Runtime5 owns storage/request/source integration; compiler4 owns paired compiler
work; review7 owns independent evidence/inventory/docs. Root orchestrates. Stage
owned files, commit reviewed increments and never push. Use canonical-root Dune
builds and coordinate shared binaries. Current [runtime](docs/semantics/RUNTIME-QUIET-HANDOFF.md),
[compiler](docs/semantics/COMPILER-HANDOFF.md) and
[reviewer](docs/semantics/QUIET-REVIEWER-HANDOFF.md) handoffs retain interfaces.

Each coherent increment needs native/source originals, focused phase/line checks,
appropriate state/ownership/resumption gates and independent review. Run early
evidence/inventory preflight; commit compatible prerequisites separately and
paired source rules atomically. Broaden testing at integration checkpoints or
when unresolved shared numeric/compiler/ownership risk requires it.

[Discrepancies](docs/semantics/DISCREPANCIES.md) distinguish engine behavior from
specification defects. Namespace-relative `static` is the sole intentional
divergence, with source activation pending. The30,980-record syntax audit is
historical. Final current-source closure, full syntax, fresh offline rebuild and
every core obligation remain mandatory. Unsupported, tool failures, timeouts and
interrupted runs never pass. Final design/departure reporting waits for the entire goal.
