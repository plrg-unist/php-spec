# Core semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit. Complete core remains the goal; see the
[plan](PLAN.md), [contract](docs/semantics/CORE.md) and
[inventory](coverage/semantics/features.json). Syntax coverage is not semantic coverage.

## Current checkpoint and next work

The **full quiet/request checkpoint is independently accepted** on 846/14d17662:
5,706 ordinary comparisons and 263 explicit-request comparisons, plus 21 separate
outcome controls. The [combined audit](coverage/semantics/quiet-integration-review.json)
checks every ordinary source/subprocess pair and all 22,873 lossless author files;
all 4,997 historical source bytes remain unchanged. Author **83cce919** binds the
ordinary run. Request author **c9fce8c9** and acceptance **ba2e421a** separately
bind 263 native calls,526 complete frontend/adapter responses and 2,381 raw files.
These are 5,969 case/profile observations, with 5,926 distinct source-byte programs.

Request/GLOBALS/top-level magic code **652d10b7** is accepted at **eed5bf8d**,
after author **d3dfb87a** and compiler **ca3ac883**. Its historical845 bridge
retains260+3 private request observations and44 ordinary magic sources, eight
independent state programs/1,936 assertions,72 final state comparisons and six
author programs/2,619 assertions. [Input](docs/semantics/REQUEST-INPUTS.md) and
[state](docs/semantics/REQUEST-STATE-REVIEW.md) contracts cover external facts,
PG ownership, CV order, callback replacement and source identity.

Next complete [source calls/frames](docs/semantics/CALLS-ACTIVATION-PLAN.md).
[Independent preflight](coverage/semantics/quiet-integration-preflight-review.json)
verifies5,706 ordinary cases retain all 4,997 historical source bytes, plus263
explicit-request cases; immediate raw retention is checked for both profiles.
Preserve ordinary uninstrumented results and count new shared-input observations separately.
The five remaining old container controls are three object quiet forms, return
and nullsafe-reference iterable compilation; four parser controls stay separate.
Seven old request-environment controls, four isset/empty GLOBALS controls and the
guarded GLOBALS original now have explicit-request witnesses. Their original
Unsupported outcomes remain unchanged history. Two later-eval callback witnesses
still await dynamic-source execution. Ordinary-library exclusions cannot close core work.

Validation infrastructure **9fc1ce9f** now gives **846/14d17662** inputs. Its
[independent review](coverage/semantics/private-validation-infrastructure-review.json)
binds13-reference private preflight and exclusive compiler timeout/failure
retention. Runtime, adapter and catalogues are unchanged. Earlier reports keep
their exact845 identities; the accepted broad checkpoint binds846 separately.

The actual private full compiler gate passes5,753 lints/5,786 aggregate assertions;
current5,750 is its exact ordered subset after three magic sources moved profiles.
The [compiler binding](coverage/semantics/request-compiler-group.json) retains the
missing-reference setup, first120s timeout and unused canonical-wrapper failure
separately. The new audit rechecks its exact catalogue binding and the
infrastructure-only846 bridge; it does not relabel that private run as canonical.

First calls remain private and unaccepted. Real declaration/body/frame/return/
recursion examples run, with global scope, fatal unwinding and dense ownership
checks in progress. Independent originals **8d65b928** preserve two compiler
priority defects, now corrected in a private recheck. **4f639832** adds eight
paired native ownership witnesses (77 with retained roots,17 without them).
Originals **b16ec243** retain literal/computed autoglobal binding, intermediate
error-iterator and unchecked callable-mapping defects before repair. The source-derived 780-name builtin occupancy prerequisite
is now published as a standalone pure predicate, source generator and focused test.
Its [source audit](docs/semantics/BUILTIN-FUNCTIONS.md) derives 780 names from 13
configured C registration tables and 238 actual source/configuration inputs.
It implements no builtin bodies and closes no core obligation; declaration and
call consumers remain in the private paired milestone. Implementation **87519651** has
780 exact native registration names and 1,569 pure membership assertions, plus a
[canonical reproduction bridge](coverage/semantics/builtin-functions-publication.json).
The [lossless author archive](coverage/semantics/builtin-function-originals.json)
retains source preprocessing, metadata, membership and injected timeout originals;
[Independent prerequisite acceptance](coverage/semantics/builtin-functions-review.json)
verifies exact canonical publication, 322 author files and 71 reviewer files.

The positional builtin argument-mode prerequisite **eef227b2** now derives all
780 configured signatures from those source arginfo tables. It distinguishes
required/preferred reference parameters and variadic tails while leaving builtin
execution separate. Its [contract](docs/semantics/BUILTIN-ARGUMENT-MODES.md),
[canonical bridge](coverage/semantics/builtin-argument-modes-publication.json) and
[400-file author archive](coverage/semantics/builtin-argument-mode-originals.json)
retain 780 exact native metadata rows and 7,508 pure flag assertions, including
the original standalone-loader setup failure. [Independent acceptance](coverage/semantics/builtin-argument-modes-review.json)
checks all 400 author files and 73 reviewer files, reproduces the exact source-derived
table, and replays all 7,508 flags on the standalone prerequisites. No call source
activation or core closure is claimed. Forward/known argument fetch compilation
and multiline call-site metadata corrections remain in the private paired work.

## Milestones

| Milestone | Status |
| --- | --- |
| 0a–b: contracts, inventory, checked runner, source harness | Complete for bounded bootstrap |
| 1a–c: numeric/byte conversions and operators | Partial; admitted scalar/array paths reviewed |
| 2a–b: storage, references, arrays, strings and sequencing | Partial; request/GLOBALS reviewed, frame/object protocols pending |
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
  immutable. Four of its16 core controls retired at quiet publication; seven more now have
  explicit-request witnesses, leaving five core controls.
- [Quiet/name access](coverage/semantics/quiet-access-review.json):a42fddfe/f3235689,
  295 sources +18 controls, author8/3,760 and independent6/2,277 state assertions.
  Compiler5,336 lints remain historical.
- [Isset/empty](coverage/semantics/isset-empty-review.json):701e39fa/16035534,
  232 sources +22 controls, author9/4,230 and independent7/2,655 on835/afbaa198.
  Four historical GLOBALS boundaries now have explicit-request witnesses.
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

Runtime5 owns storage/request/source integration; compiler5 owns paired compiler
work; review8 owns independent evidence/inventory/docs. Root orchestrates. Stage
owned files, commit reviewed increments and never push. Use canonical-root Dune
builds and coordinate shared binaries. Current [runtime](docs/semantics/RUNTIME-QUIET-HANDOFF.md),
[compiler](docs/semantics/COMPILER-HANDOFF.md) and
[reviewer](docs/semantics/REQUEST-REVIEWER-HANDOFF.md) handoffs retain interfaces.

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
