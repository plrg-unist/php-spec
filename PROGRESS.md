# Core semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit. Complete core remains the goal; see the
[plan](PLAN.md), [contract](docs/semantics/CORE.md) and
[inventory](coverage/semantics/features.json). Syntax coverage is not semantic coverage.

## Current checkpoint and next work

Current ordinary/request/callable integration is independently accepted at
**f244a78e** in [callable-integration-review.json](coverage/semantics/callable-integration-review.json).
Canonical **981/7640870f** includes the one-test correction **8051f53e** over
accepted107/108 **981/3f3ca6b6**. `f()[0]="X"` now requires the native undefined-function
Error instead of a stale Unsupported expectation. All980 other watched files, including every
semantic module, remain byte-identical; all981 modes are unchanged.

The current campaigns retain distinct profiles and actual execution identities:

- **5706 ordinary comparisons** on7640:4060 normal,1006 PHP errors,640 static
  rejections;21 separate outcome controls include expected timeout/runner failures.
- **263 explicit requests** on3f3, with526 raw responses and2 clean worker closures;
  the representative4-source full-profile preflight remains separately recorded.
- **751 callable rows across13 suites** on3f3, with1502 responses and26 closures;
  three builtin-result dependencies remain explicitly Unsupported.
- **5751 compiler lint comparisons** on7640, with15 emitted-line cases,8 access
  sources/24 paths,7 metadata boundaries and constant checks in5783 fixture cases.
  The557.41s aggregate passed within its original600s allowance.

Independent audits verify ordered source membership, native outcomes, full request
FD198/environment/argv/path/clock/config facts, raw packets, fixtures, closures and
all archive payload hashes/modes. Counts overlap and are not unique-program coverage.
Ordinary inherited-environment execution, explicit primitive requests and callable
fixed-clock requests remain distinct. The compiler used an explicitly verified
existing binary; this is not a fresh build. Callable entry alarm60 is replaced and
cancelled by per-packet alarm30, so it is not a continuous whole-case deadline.

[Array call unpacking](docs/semantics/SOURCE-CALL-UNPACK.md) remains accepted at
**e45c7139**, code **adb21f56**, with its source/state/compatibility evidence in
[call-unpack-review.json](coverage/semantics/call-unpack-review.json). This integration
refreshes the broad evidence after107/108 and closes no new inventory obligation.
Inventory remains134 partial/171 pending/1 oracle validated. Full syntax, a fresh
network-isolated offline rebuild/audit, complete core and later callable/object
lifetime integration remain required.

Next109/110 dynamic string user calls require root's accepted-checkpoint read.
Root coordinates compiler7, runtime7 and review10; read the
[successor handoff](docs/semantics/DYNAMIC-CALL-HANDOFF.md). Replay20 preserved972
native contexts without duplicate native execution. Preserve initial parser-string,
later compiled-constant and runtime-callee modes, selected-function ownership,
source-derived emitted lines and shared99/105/107/108 consumers. No next code was
activated during integration. Builtin bodies/defaults/callbacks, Traversable,
function statics, closures, objects, exceptions, reporting configuration, dynamic
sources and remaining lifetime protocols stay required.

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
runtime campaigns retain their historical identity. The fresh current integration
above supplies separate post-call evidence; the final full-source/full-syntax/
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

The [current successor handoff](docs/semantics/DYNAMIC-CALL-HANDOFF.md)
binds981/764 integration and the next dynamic string user-call increment. Compiler7,
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
