# Core semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit. Complete core remains the goal; see the
[plan](PLAN.md), [contract](docs/semantics/CORE.md) and
[inventory](coverage/semantics/features.json). Syntax coverage is not semantic coverage.

## Current checkpoint and next work

[Array call argument unpacking](docs/semantics/SOURCE-CALL-UNPACK.md) is independently
accepted at **e45c7139** in [call-unpack-review.json](coverage/semantics/call-unpack-review.json).
Canonical **981/3f3ca6b6** binds code **adb21f56**, compiler evidence **50d0fbbc** and
runtime evidence **5318ed52**. Direct user calls expand integer keys in insertion
order and map string keys through the named binder. Emitted operand class controls
reference eligibility; container and sent owners survive later effects and errors.
Default holes, uncoerced caches, typed receives and saved suppression keep their
reviewed ordering. NArg markers preserve SEND_UNPACK lines separately from child calls.

Author55 exact source outcomes (31 normal,18 PHP errors,6 static rejections),
29 compiler phases/56 projections,34 protocol controls/824 assertions,12 adjacent
profiles and2 ownership cases/435 assertions pass. Independent7 source profiles,
4 state cases/1063 assertions and14 complete-response cuts for2 old972 programs
pass; compatibility needs no projection. Canonical CLI8 passes. Counts overlap.
Three builtin-result contexts remain explicit dependencies.

The [review](coverage/semantics/call-unpack-review.json) binds compiler cb917,
runtime5175 and independent review archives, original failures and raw closures.
Final source/protocol/state gates retain **981/ec4cf850**. Earlier862d compiler and
regression gates retain their identity; the cursor guard and protocol successor
bridges are explicit. Installation3f3 removes only an unused two-line helper,
with zero-reference and exact byte/mode proof. All other final files are unchanged.
Class passthrough, emitted-line and finite source/state guard repairs preserve
arbitrary consistent values; no prior execution history is reconstructed.

Next is the current ordinary/request/callable integration checkpoint, before any
109 source activation. Read the [handoff](docs/semantics/RUNTIME-CALLABLE-INTEGRATION-HANDOFF.md).
Root coordinates compiler7, runtime7 and review10. Freeze current memberships,
profiles, tools and modes after root reads this checkpoint; validate a representative
full request/source/native profile through the prepared raw wrapper before263.
Historical full campaigns remain historical until these current runs are accepted.

Current integration is in progress on independently copied **981/3f3** inputs;
accepted108 remains the checkpoint above. Shared membership is frozen at5706
ordinary cases,263 explicit requests,751 callable rows across13 suites and5751
ordered compiler sources, with distinct profiles and overlapping counts. Four
full request-wrapper preflight profiles pass (8 responses,6 clean closures);
runtime7 is independently auditing that preflight before the full263 run.
Compiler7 owns ordinary/compiler execution, runtime7 callable execution, and
review10 requests plus ordinary-lane audit. No109 source activation or semantic
mutation is authorized during these runs. Current results will be published
with exact raw closures; historical full campaigns remain separately scoped.

Builtin106 name/mode metadata remains accepted on972/e1bf; builtin bodies,
default filling and callbacks remain required. Traversable, dynamic callables,
function statics, closures, objects, exceptions, reporting APIs/configuration,
dynamic sources and lifetime protocols remain open. Current native reporting
profile30719 uses fatal mask4437 inside `@`. The
[core checklist](docs/semantics/CORE-CONTINUATION-CHECKLIST.md) retains complete
inventory, source, full syntax and fresh offline gates. No family closes.

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
runtime campaigns have not been relabeled current after calls. Refresh the
combined current source campaign at the callable checkpoint or earlier shared
risk; the final full-source/full-syntax/fresh network-isolated offline gates remain
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
| 2a–b: storage, references, arrays, strings and sequencing | Partial; request/GLOBALS and first call frames reviewed; object protocols pending |
| 3a: control, exceptions, diagnostics and unwinding | Partial; loops/jumps, returns, suppression and fatal frame cleanup reviewed; exceptions/handlers pending |
| 3b: calls, closures and static checks | Partial; positional/named value/reference and variadic parameters, defaults, lexical strictness and builtin scalar/container value types reviewed; reference assignment/returns reviewed; remaining call protocols pending |
| 4a–b: linking and declarations | Partial; user constants and header/relation helpers reviewed; object execution pending |
| 5a–b: dynamic sources, services, resumability and lifetime | Pending |
| 6: complete inventory/review, differential campaign and offline audit | Pending |

Inventory: **169 constructors/306 runtime obligations**, with70 field domains.
The runtime inventory now records134 partial,171 pending and one validated
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

The [current successor handoff](docs/semantics/RUNTIME-NAMED-SUCCESSOR-HANDOFF.md)
binds968 inputs and the next builtin-name/compiler and call-unpack prerequisites. Compiler7,
runtime7 and independent review10 coordinate private roots, exact frozen gates,
canonical builds and the index under root. Preserve baseline originals before
admission, stage only reviewed files, commit small increments and never push.
Earlier identities and failures remain historical rather than rebuilt counts.

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
