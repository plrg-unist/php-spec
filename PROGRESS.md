# Core semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit. Complete core remains the goal; see the
[plan](PLAN.md), [contract](docs/semantics/CORE.md) and
[inventory](coverage/semantics/features.json). Syntax coverage is not semantic coverage.

## Current checkpoint and next work

[Source strict_types declarations](docs/semantics/SOURCE-STRICT-DECLARATIONS.md)
are independently accepted at **85a16bae** in [strict-declaration-review.json](coverage/semantics/strict-declaration-review.json)
on exact **917/309b046c** (code **c81fb14e**, compiler **410291bb**, author **3772ec36**).
Compiler92/runtime93 compile legal strict-only directives,
execute declaration work without runtime effects, and bind unit/function STRICT
metadata to actual source. Setting 1 is sticky; zero does not clear it. Five original
forged unit flags survived public resume before the repaired guard; existing
function-flag rejection remains intact. Canonical CLI 8 passes. No family closes.

Independent gates retain 21 source profiles: 18 native agreements and three explicit
encoding/type boundaries. Seven additional builtin profiles remain Unsupported.
Two strict-cache programs pass 543 dense state/resumption assertions. Three no-directive
programs preserve entire 909 states at seven cuts after removing only new false
pcode.STRICT fields, including saved reference owners and cache-before-error behavior.
Retained-context and fresh 17-control protocol runs each pass 168 assertions. Author
8 sources/17 flag projections, 2 states/542 assertions and 17 protocol/168 assertions
pass. The paired compiler gate has 37 exact phases/lines, two other-directive
boundaries and 47 source projections. Source sets overlap and are not added.

The review audits 236 independent recorded responses/23 clean closures, including
historical originals and a separate precleanup tool attempt; author final 115/8
is separate. Compiler910/912 preparation, unguarded913 and packaging917/15db remain
historical. The 15db→309b bridge removes only an unused test dictionary; runtime,
compiler and tools are byte-identical. Full frozen bytes and modes match canonical.

[Untyped defaults](docs/semantics/SOURCE-POSITIONAL-DEFAULTS.md) remain accepted at
c7cb1b44 on909/e25eb2b9 (code1fce6586, compiler2b247d81, runtime8151b96d).
Their [review](coverage/semantics/default-parameter-review.json) retains 130 source
profiles, 57 exact author contexts, 4 states/1,091 assertions, 6 readiness programs,
12 projections/95 assertions and two historical no-default bridges. Omitted
receives, caches, declaration contexts and fresh reference/array ownership remain
unchanged by strict declaration activation.

The next increment connects scalar/container parameter and return types through
existing 16/17 normalization and call/default machinery. Caller strictness governs
argument checks; callee strictness governs returns. Successful deferred evaluation
caches before type verification, and caches the uncoerced value. Reference returns,
other callables, other declare directives and builtin execution remain required.
The [core checklist](docs/semantics/CORE-CONTINUATION-CHECKLIST.md) retains control,
objects, exceptions, dynamic sources, generators/fibers, lifetime and core intrinsics.
PHP_VERSION value reads, other missing builtin constants, define/defined and legal
object/class/callable constants remain open. NEW side effects must extend caching.

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
| 3b: calls, closures and static checks | Partial; named positional value/reference calls, untyped defaults and lexical strictness reviewed; typed and remaining call protocols pending |
| 4a–b: linking and declarations | Partial; user constants and header/relation helpers reviewed; object execution pending |
| 5a–b: dynamic sources, services, resumability and lifetime | Pending |
| 6: complete inventory/review, differential campaign and offline audit | Pending |

Inventory: **169 constructors/306 runtime obligations**, with70 field domains.
The runtime inventory now records125 partial,180 pending and one validated
obligation; accepted constants, defaults and lexical strictness are reflected in their partial rows.
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

Runtime6 and compiler6 continue with typed parameter/return integration after
strict declaration acceptance. Review10 owns independent strict review and follows
through types; root orchestrates. The [strict contract](docs/semantics/SOURCE-STRICT-DECLARATIONS.md)
and [core checklist](docs/semantics/CORE-CONTINUATION-CHECKLIST.md) record current
continuation. Stage owned files, commit reviewed increments and never push.
Coordinate canonical builds, binaries and the index. Earlier handoffs retain
historical identities and original failures.

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
