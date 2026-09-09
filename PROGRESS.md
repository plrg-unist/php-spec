# Core semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit. Complete core remains the goal; see the
[plan](PLAN.md), [contract](docs/semantics/CORE.md) and
[inventory](coverage/semantics/features.json). Syntax coverage is not semantic coverage.

## Current checkpoint and next work

The [user-constant prerequisite](docs/semantics/SOURCE-USER-CONSTANTS.md) is
independently accepted at **3341519d** in the [review](coverage/semantics/user-constant-review.json).
Code **5151608e** installs **899/ca3c06e5**; compiler evidence is **41b2c1a2**
and runtime evidence is **06b64f88**. Source and independent gates retain
**899/e7d552ec**; the explicit bridge changes only one state-test expectation to
retain initial request roots after an initializer error. Runtime/compiler bytes
and modes are identical. Original fixture and metadata failures remain archived.

Ordinary declarations activate in order, preserve namespace/import/fallback and
name case, evaluate duplicate initializers before warning, and retain constant
array ownership across copies, calls and abrupt cleanup. Nonowning allocation
classes follow actual compiler/runtime operations. Conditional observations use
recorded operands; public guards reject inconsistent branch or pooled-class
facts while accepting legitimate changed runtime values.

Independent gates pass 42 retained constant sources, 75 exact author-source replays,
24 existing quiet regressions, four constant state programs/1,082 assertions,
two quiet state programs/676, and branch 6/126. Each dense state program checks 35
cuts, adjacent public resumes and seven full resumes. Two accepted reference-call
programs preserve complete historical 882 states at six selected cuts/full after
removing only the new empty constant fields. Compiler review adds 15 retained
class projections/195 assertions and 12 boundary controls/26 assertions; its
original 889 gates and focused shared 45 regressions retain their own identity.
Author gates pass 75 source profiles / 46 class assertions, table 14 / context 14,
branch 6/126, and corrected state 3/821. Canonical CLI 8 passes. Three PHP_VERSION
value-read controls remain separate Unsupported boundaries. No family closes.

The positional-reference checkpoint remains historical **3956fbe1**: code
**31640654**, compiler **7263bf5b**, runtime **7aed92c3**, tested882/4b5e15e4 and
installed884/7399e812 through an unchanged two-file bridge. Its
[review](coverage/semantics/reference-parameter-review.json) retains166 author
sources,61 independent agreements,283 shared destructuring regressions,
state8/1,868, author state6/1,413,139 first-call sources,40 existing protocols,
five reference groups and CLI 8. The earlier first-call checkpoint remains
**f3149e32** on869/c946394c (codea8fdac1e, runtimed907c5db, compiler04ac151f);
[its review](coverage/semantics/calls-final-review.json) records139 sources,
40 protocols, state9/2,079 and the870→869 bridge. Its broad compiler checkpoint
on866 retains5,751 native lints/5,783 assertions and70,239 archived files.
Historical gates are not relabelled current.

The [compiler handoff](docs/semantics/CONSTANTS-COMPILER-HANDOFF.md) and
[runtime handoff](docs/semantics/RUNTIME-DEFAULTS-HANDOFF.md) give exact continuation inputs.
The next [untyped-default phase plan](docs/semantics/DEFAULTS-ACTIVATION-PLAN.md)
now proceeds from accepted user constants (compiler88/runtime89) to omitted
untyped-default receives (compiler90/runtime91). Supplied arguments skip defaults;
omitted arguments use declaration context, fresh parameter/array ownership and
observable deferred-value caching. Allocation provenance is implemented, but
receive caching is not. Independent preparation retains 119 later default/cache
originals: 108 from the [162-source preparation/diagnosis](coverage/semantics/constant-review-diagnosis.json)
and 11 [literal-constructor controls](coverage/semantics/literal-class-review-preparation.json).
The historical 877 signature 17 suspension prototype and paused default compiler
are preserved in the [successor archive](coverage/semantics/default-compiler-preparation.json),
not admitted source semantics. Types, reference returns and remaining callable
protocols follow. All seven existing pending signature controls remain pending.
The earlier reference [originals](coverage/semantics/reference-parameter-review-preparation.json)
and [DIM diagnosis](coverage/semantics/reference-parameter-review-diagnosis.json)
retain their original Unsupported/disagreement states. The [core continuation checklist](docs/semantics/CORE-CONTINUATION-CHECKLIST.md)
keeps switch/match/labels/goto, objects/properties, exceptions, dynamic sources,
generators/fibers, observable lifetime, core intrinsics and source-input gaps
explicit. Global function `namespace\static` signature
rejection matches the pin; the sole intentional divergence remains the pending
class-scope relative-static branch.

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
| 3b: calls, closures and static checks | Partial; named positional value/reference calls reviewed; remaining call protocols pending |
| 4a–b: linking and declarations | Partial; user constants and header/relation helpers reviewed; object execution pending |
| 5a–b: dynamic sources, services, resumability and lifetime | Pending |
| 6: complete inventory/review, differential campaign and offline audit | Pending |

Inventory: **169 constructors/306 runtime obligations**, with70 field domains.
The runtime inventory now records124 partial,181 pending and one validated
obligation; accepted user constants are reflected in declaration rows, which remain partial.
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

Runtime6 owns current default receives; compiler6 owns the paired default
compiler and shared signature adapter; review9 owns independent evidence/inventory/docs.
Compiler5 authored the accepted constant and historical default preparation.
Runtime5 and review8 authored/reviewed earlier checkpoints. Root orchestrates. Stage
owned files, commit reviewed increments and never push. Use canonical-root Dune
builds and coordinate shared binaries. Current [runtime](docs/semantics/RUNTIME-DEFAULTS-HANDOFF.md) and
[compiler](docs/semantics/CONSTANTS-COMPILER-HANDOFF.md) handoffs retain the default
interfaces; the [review](coverage/semantics/user-constant-review.json) binds this checkpoint.

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
