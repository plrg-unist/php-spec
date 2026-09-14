# Core semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit. Complete core remains the goal; see the
[plan](PLAN.md), [contract](docs/semantics/CORE.md) and
[inventory](coverage/semantics/features.json). Syntax coverage is not semantic coverage.

## Current checkpoint and next work

Real explicit closure instances115/116 are independently accepted at **14e3bf7d** in
[closures-review.json](coverage/semantics/closures-review.json) on exact
**1017/9325300f**, code **875c7867**. Source templates stay separate from shared
object identities. Ordered captures, fresh value bindings per invocation, shared
references and instance statics survive selected-callee argument effects and
frame cleanup. Source guards authenticate live state without replaying its history.

Author final gates pass70 source outcomes,26 compiler phases/109 projections,
20 protocol controls/217 assertions,12 regressions and dense2/443. Independent
final gates pass27 retained native observations plus one explicit method-service
dependency,20 controls/217, dense4/621 and24 complete old1008 response bridges.
The bridge removes only verified empty object/template fields and absent instance
fields, including actual active and saved call contexts. Dense checks compare48
one-step and48 complete resumptions. All source/state failures and fixture-only
corrections remain archived; final archive cross-audits and canonical CLI8 pass.
Fresh maintained profiles, exact original70 model-only replays and28 historical
ordinary CLI regressions retain separate identities and are not added together.

Initial-main statics113/114 remain accepted historical **5ef385d6**, on1008/2829,
in [main-statics-review.json](coverage/semantics/main-statics-review.json).
Their global-table bindings, prior aliases, initializer calls and unit0 eligibility
retain the original16 source,12/59 compiler,9/173 protocol,2/283 author dense,
4/623 independent dense and20 complete old999-response evidence.

Named-function statics111/112 remain accepted historical **c00a5d53** in
[function-statics-review.json](coverage/semantics/function-statics-review.json)
on999/0484. Their recursive initialization, hidden CVs, cached null and source-line
checks retain original gates, including the repaired105 receive ambiguity on442a
and test-only0484 protocol bridge. Initial-main statics reuse these rules.

Dynamic109/110 remains accepted historical **178f993c**, on990/866, in the
[dynamic-call review](coverage/semantics/dynamic-call-review.json). Its45 source,
42 compiler phases plus two boundaries/275 projections,19 protocol/278,
author2 dense/385, independent4 dense/652 and14 old981 responses retain their
original identities. Full archive and current canonical evidence are bound in
the named-function review.

The broad [integration checkpoint](coverage/semantics/callable-integration-review.json)
**f244a78e**, on 981/764 and its one-test8051f53e bridge from981/3f3, is now historical:
5706 ordinary comparisons plus21 outcome controls,263 explicit requests,751 callable
rows across 13 suites and5751 compiler phases. Their native/request/configuration
profiles and identities remain separate; these gates were not rerun or relabelled
for 109/110 or111/112. The compiler reused a verified binary. Callable entry alarm60 is
replaced/cancelled by per-packet alarm30, not a continuous whole-case deadline.

Inventory now records140 partial/165 pending/1 oracle validated. Full syntax,
a fresh network-isolated offline rebuild/audit and complete core remain required.
Builtin compilation/bodies/defaults/callbacks, other callable forms, Traversable,
exceptions, reporting configuration and object/dynamic-source lifetimes stay open.

Next is the bounded arrow-function implicit-capture and expression-return slice.
Read the [arrow handoff](docs/semantics/ARROWS-HANDOFF.md) before any new schema or
native campaign. Completed undefined captures must remain distinct from pending
construction; source discovery and runtime ownership need separate review.
A refreshed broad integration checkpoint follows arrows before further callable
or class expansion, unless a concrete shared defect requires it sooner. Required
Closure method services, ordinary objects, cycle collection and dynamic lifetime
remain open; valid Closure::fromCallable type checking is explicitly Unsupported.

Earlier checkpoints retain their own identities and detailed gates in linked
reviews: [user constants](coverage/semantics/user-constant-review.json) **3341519d**,
code5151608e / compiler41b2c1a2 / runtime06b64f88, tested899/e7d552ec with an explicit
one-test bridge to899/ca3c06e5; [references](coverage/semantics/reference-parameter-review.json)
**3956fbe1**, code31640654 / compiler7263bf5b / runtime7aed92c3, tested882/4b5e15e4
with an unchanged two-file bridge to884/7399e812; and
[first calls](coverage/semantics/calls-final-review.json) **f3149e32**, codea8fdac1e /
runtimed907c5db / compiler04ac151f, on869/c946394c. The broad compiler5,751-lint
checkpoint remains historical866. Original failures, 119 default/cache baseline
profiles and historical signature17 preparation remain linked from the current
review; historical gates are never relabelled current.

The full quiet/request checkpoint remains accepted **historical 846/14d17662**:
5,706 ordinary comparisons plus 263 explicit-request comparisons and 21 separate
outcome controls. [Its audit](coverage/semantics/quiet-integration-review.json)
retains all 4,997 historical source bytes and 22,873 ordinary author files; explicit
request acceptance retains 263 native calls, 526 responses and 2,381 files. These
are 5,969 case/profile observations and 5,926 distinct source programs. Those full
runtime campaigns retain their historical identity. The later integration above supplied separate post-call evidence and retains
its historical981 identity; the final full-source/full-syntax/
fresh network-isolated offline gates remain
required before complete-core acceptance.

The source-only [builtin occupancy](docs/semantics/BUILTIN-FUNCTIONS.md) and
[positional mode](docs/semantics/BUILTIN-ARGUMENT-MODES.md) prerequisites remain
independently accepted: 780 names/signatures from 238 configured source inputs,
1,569 membership and 7,508 argument-mode assertions. They implement no builtin
bodies and close no core obligation. Request table/callback interfaces remain in
[the input](docs/semantics/REQUEST-INPUTS.md) and
[state](docs/semantics/REQUEST-STATE-REVIEW.md) contracts.

## Milestones

| Milestone | Status |
| --- | --- |
| 0a–b: contracts, inventory, checked runner, source harness | Complete for bounded bootstrap |
| 1a–c: numeric/byte conversions and operators | Partial; admitted scalar/array paths reviewed |
| 2a–b: storage, references, arrays, strings and sequencing | Partial; request/GLOBALS, call frames and shared real-closure identities reviewed; general object protocols pending |
| 3a: control, exceptions, diagnostics and unwinding | Partial; loops/jumps, returns, suppression and fatal frame cleanup reviewed; exceptions/handlers pending |
| 3b: calls, closures and static checks | Partial; positional/named value/reference and variadic parameters, defaults, lexical strictness and builtin scalar/container value types reviewed; reference assignment/returns and explicit closures/captures reviewed; arrows and remaining call protocols pending |
| 4a–b: linking and declarations | Partial; user constants and header/relation helpers reviewed; ordinary object/class execution pending |
| 5a–b: dynamic sources, services, resumability and lifetime | Pending |
| 6: complete inventory/review, differential campaign and offline audit | Pending |

Inventory: **169 constructors/306 runtime obligations**, with70 field domains.
The runtime inventory now records140 partial,165 pending and one validated
obligation. Accepted constants, defaults, strictness, builtin value types,
reference returns, suppression, positional variadics, named binding and call unpack remain partial.
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

The [current successor handoff](docs/semantics/CLOSURES-HANDOFF.md)
binds1008/2829 initial-main statics and the proposed closure foundation.
Compiler7, runtime7 and independent review12 coordinate private roots, exact
frozen gates, canonical builds and the index under root. Preserve baseline
originals before admission, stage only reviewed files, commit small increments
and never push. Earlier identities and failures remain historical.

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
