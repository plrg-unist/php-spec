# Core semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit. Complete core remains the goal; see the
[plan](PLAN.md), [contract](docs/semantics/CORE.md) and
[inventory](coverage/semantics/features.json). Syntax coverage is not semantic coverage.

## Current checkpoint and next work

[Typed positional parameters and value returns](docs/semantics/SOURCE-TYPED-FUNCTIONS.md)
are independently accepted at **e097f95e** in [typed-function-review.json](coverage/semantics/typed-function-review.json).
Canonical **926/599f3963** contains code **0ed17419**, compiler evidence
**2ea12015** and author evidence **dabc28d9**. Compiler 94/runtime 95 connect
builtin scalar/container singleton and union types, sequential receives, stored
float defaults, uncoerced deferred caches, reference-parameter coercion and
detached value returns. Source-derived return locations and saved caller task
contexts are checked. Class/object/callable types and reference returns remain open.

Independent gates pass 18 source profiles (15 native agreements, three explicit
mixed-strictness ticks dependencies), five dense states/1,357 assertions,
19 retained-context protocol controls/217 assertions and two complete untyped
917 state bridges at seven cuts. Author 38 source profiles plus three cache
projections/12 assertions, four states/1,096 assertions and compiler 56 exact
phases plus eight boundaries/38 projections pass. Sets overlap and are not added.

Those semantic gates retain **926/baa85f57**. A missing standalone test output
helper was corrected in one file: all 925 other bytes and all 926 modes remain
identical. The corrected fresh 19-control protocol passes 218 assertions on599,
including arbitrary return output9911; canonical CLI8 passes. Raw audits cover
202 independent responses/42 clean closures and separate author234/8, with23
successful author state/protocol runner closures. Original failures remain retained.

[Strict declarations](docs/semantics/SOURCE-STRICT-DECLARATIONS.md) remain accepted
at85a16bae on917/309b046c; [untyped defaults](docs/semantics/SOURCE-POSITIONAL-DEFAULTS.md)
atc7cb1b44 on909/e25eb2b9. Their exact historical gates remain in linked reviews.
The next bounded increment is reference returns and required call-reference
acquisition; use the [runtime handoff](docs/semantics/RUNTIME-REFERENCE-RETURNS-HANDOFF.md)
and its pinned13b3 preparation. Replay the retained917 originals on accepted926
before new admission. Root orchestrates, compiler6/review10 retain continuity,
and a fresh runtime implementer starts from all926 canonical inputs.

The [core checklist](docs/semantics/CORE-CONTINUATION-CHECKLIST.md) retains named,
unpacked/variadic and other callable protocols, objects, exceptions, dynamic
sources, generators/fibers, lifetime and core intrinsics. Mixed caller/callee
strictness still needs an admitted source route. PHP_VERSION value reads, other
missing builtin constants, define/defined and legal object/class/callable constants
remain open. NEW side effects must extend caching. No family closes.

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
| 3a: control, exceptions, diagnostics and unwinding | Partial; loops/jumps, first returns and fatal frame cleanup reviewed; exceptions pending |
| 3b: calls, closures and static checks | Partial; positional value/reference parameters, defaults, lexical strictness and builtin scalar/container value types reviewed; reference returns and remaining call protocols pending |
| 4a–b: linking and declarations | Partial; user constants and header/relation helpers reviewed; object execution pending |
| 5a–b: dynamic sources, services, resumability and lifetime | Pending |
| 6: complete inventory/review, differential campaign and offline audit | Pending |

Inventory: **169 constructors/306 runtime obligations**, with70 field domains.
The runtime inventory now records129 partial,176 pending and one validated
obligation; accepted constants, defaults, lexical strictness and builtin parameter/value-return types are reflected in partial rows.
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

The [runtime successor handoff](docs/semantics/RUNTIME-REFERENCE-RETURNS-HANDOFF.md)
records exact typed inputs, interfaces, gates and the next reference-return
preparation. Compiler6 and review10 retain continuity; root orchestrates the fresh
runtime implementer. Stage owned files, commit reviewed increments and never push.
Coordinate canonical builds, binaries and the index. Preserve earlier identities
and original failures instead of rebuilding historical counts.

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
