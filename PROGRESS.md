# Core semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit. Complete core remains the goal; see the
[plan](PLAN.md), [contract](docs/semantics/CORE.md) and
[inventory](coverage/semantics/features.json). Syntax coverage is not semantic coverage.

## Current checkpoint and next work

The [positional reference parameter](docs/semantics/SOURCE-REFERENCE-PARAMETERS.md)
increment is independently accepted at **3956fbe1**: code **31640654**,
compiler evidence **7263bf5b**, runtime evidence **7aed92c3**. Final author/reviewer
gates retain **882/4b5e15e4**; an explicit unchanged two-file bridge binds canonical
**884/7399e812**. [Independent evidence](coverage/semantics/reference-parameter-review.json)
records 61 original reference agreements and three separate pending suppression
controls, 166 exact author-source replays, 283 fresh native destructuring regressions,
and eight state programs with 1,868 assertions. Author gates add 139 first-call
comparisons, 40 existing protocol fixtures, five reference protocol groups and six
state programs with 1,413 assertions. Each dense state program checks 35 cuts,
adjacent public resumes and seven full resumes. Canonical CLI8 passes.

Reference sends preserve caller cells through later argument effects, parameter
rebinding, saved calls, surplus values and fatal cleanup. Literal/TMP sends throw;
value-call/VAR sends can emit a Notice and create a temporary reference. Shared
call-result DIM writes and reference destructuring preserve temporary ownership,
COW and exact diagnostics. Compiler preparation retains 48 phase/16 descriptor
checks, 12 send-kind/36 context checks, and 91 optimized builtin write-context
phase controls. These compiler facts implement no builtin bodies. The source
originals, intermediate disagreements, interrupted state run and setup failures
remain separately archived. No family is closed by this increment.

The first actual [source calls](docs/semantics/SOURCE-CALLS.md) remain the historical
accepted prerequisite at **f3149e32** on **869/c946394c**. Code **a8fdac1e**, runtime author
**d907c5db** and compiler author **04ac151f** retain their separate evidence.
Named declarations activate at their compiler/runtime
phase; untyped positional value calls execute through real local frames, including
recursion, global/superglobal access, returns and fatal unwinding. The paired
compiler/runtime change retains deferred argument fetch timing and source-derived
resume metadata. Builtin registration/signature tables supply compiler facts;
their bodies remain separate required work.

The [independent review](coverage/semantics/calls-final-review.json) binds 139 exact
source/native comparisons, fresh complete recorded responses on 866 and 870, and
an explicit 870→869 production bridge. All loaded modules and five tools are
identical across that last bridge. Nine then-current production state programs check
2,079 assertions: heap/frame/iterator ownership, request roots, adjacent-step
resumption, selected full resumes and final cleanup. Forty protocol fixtures cover
source-derived metadata and controls; fresh production saved-target/fallback and
20 no-call full-response checks supplement the audit. Eight public CLI sources
match the retained native profiles. Original defects, setup failures, transport
bytes, process outcomes and immutable input snapshots remain archived.

The historical broad compiler checkpoint on 866 has **5,751 native lint comparisons
and 5,783 aggregate assertions**. Its complete 70,239-file archive retains exact
native/SpecTec subprocess bytes and 11,561 decoded Worker exchanges. Those older
Worker records are not exact transport wire; the independent 139 source bridge
provides separate exact-wire evidence. Focused compiler groups add 848 phase
comparisons, with emission/context assertions counted separately. Historical
compiler 5753/5786 and its 5750 subset retain their original identities.

The [reviewer handoff](docs/semantics/FIRST-CALLS-REVIEWER-HANDOFF.md) and
[runtime handoff](docs/semantics/RUNTIME-CALLS-HANDOFF.md) give exact continuation inputs.
Next complete defaults, parameter/return types and reference returns, then the
remaining argument and callable protocols in the
[calls plan](docs/semantics/CALLS-ACTIVATION-PLAN.md). The earlier reference
[pre-repair originals](coverage/semantics/reference-parameter-review-preparation.json)
and [DIM diagnosis](coverage/semantics/reference-parameter-review-diagnosis.json)
retain their exact older Unsupported and disagreement states. All seven existing
pending signature controls remain pending; no reference-parameter control existed
to retire.
The [core continuation checklist](docs/semantics/CORE-CONTINUATION-CHECKLIST.md)
keeps switch/match/labels/goto, objects/properties, exceptions, dynamic sources,
generators/fibers, observable lifetime, core intrinsics and source-input gaps
explicit. Global function `namespace\static` signature
rejection matches the pin; the sole intentional divergence remains the pending
class-scope relative-static branch.

The exact old nested-foreach return witness now prints 13, returns 7, clears both
iterator roots and preserves `v`/`w` aliases. Four old property/nullsafe container
controls remain pending, plus two later-eval ENV/REQUEST callback witnesses; four
parser controls remain separate. This source witness retires its old boundary
case without closing the complete return or function family.

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
| 4a–b: linking, objects, traits and properties | Partial; header/relation helpers reviewed, execution pending |
| 5a–b: dynamic sources, services, resumability and lifetime | Pending |
| 6: complete inventory/review, differential campaign and offline audit | Pending |

Inventory: **169 constructors/306 runtime obligations**, with70 field domains.
The runtime inventory now records123 partial,182 pending and one validated
obligation; accepted positional reference activation is reflected in its call rows.
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

Runtime6 owns positional reference-parameter runtime integration; compiler5 owns
paired compiler work; review9 owns independent evidence/inventory/docs. Runtime5
and review8 authored/reviewed the historical checkpoints above. Root orchestrates. Stage
owned files, commit reviewed increments and never push. Use canonical-root Dune
builds and coordinate shared binaries. Current [runtime](docs/semantics/RUNTIME-CALLS-HANDOFF.md),
[compiler](docs/semantics/COMPILER-HANDOFF.md) and
[reviewer](docs/semantics/FIRST-CALLS-REVIEWER-HANDOFF.md) handoffs retain interfaces.

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
