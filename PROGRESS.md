# Core semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit. Complete core remains the goal; see the
[plan](PLAN.md), [contract](docs/semantics/CORE.md) and
[inventory](coverage/semantics/features.json). Syntax coverage is not semantic coverage.

## Current checkpoint and next work

[Parameter source phases](docs/semantics/PARAMETER-PHASE.md) are independently
accepted at **51ca21db** in [parameter-phase-review.json](coverage/semantics/parameter-phase-review.json).
Canonical **951/440f3966** binds code **c00a5c38** and compiler evidence **4290295e**.
Only PHP-Parser's eager variadic-default and void-parameter checks are deferred;
existing17/16/90 supplies native static diagnostic order. Exactly three watched
paths and three patch/provenance files change; semantic modules and all modes
remain unchanged. The two exact phase exceptions are retired.

Independent fourteen-source and eight-CLI controls preserve one valid-variadic
Unsupported boundary; two exact retired PHPT FILE sources pass native parsing,
lint and repaired CLI diagnostics, with original frontend failures retained.
Zero-fuzz reproduction matches all five handwritten patch outputs. Author checks
include fourteen checked roundtrips/CLI controls,359 signature comparisons,
28 descriptors,174 reference-return assertions and exact generated-parser
reproduction. Compiler archive0f6bea05 binds8,251 paths/1,280 responses/8 closures;
independent archive6898c6d5 binds366 paths/36 responses/4 closures. Counts overlap.
Inventory remains169 constructors/306 obligations,131 partial/174 pending and
one validated oracle; this parser prerequisite adds no runtime admission.

The preceding semantic checkpoint is source suppression:
[Source error suppression](docs/semantics/SOURCE-ERROR-SUPPRESSION.md) is independently
accepted at **29baca42** in [error-suppression-review.json](coverage/semantics/error-suppression-review.json).
Historical **951/c6501bd8** binds code **14003331**, compiler evidence **601b496d**
and author evidence **5535cffc**. Compiler100/runtime101 preserve folded effects,
read deferred CVs inside suppression, filter runtime nonfatal events and restore
frame-owned masks through normal return and abrupt cleanup. The pinned C-int
reporting field and saved masks use signed32; arbitrary valid masks and owning
values remain legal paused-state controls.

Independent gates pass4 native profiles,23 protocol controls/489 assertions,
4 dense states/1,312 assertions and2 complete942 state bridges at seven cuts,
removing only new default reporting/empty silence fields. Author26 source,
37 reporter checks, compiler17 phases/131 projections,19 demand/38,2 states/779,
31 reference-return regressions and canonical CLI8 pass. Sets overlap. Independent
90 responses/33 worker closures and author198/14 plus corrected demand38/2 are
audited; successful standalone and retained fixture failures remain distinct.

Semantic gates retain **951/ff8d4b9f**. Final c650 changes only a demand-report
print key after its assertions passed;950 other files and all951 modes are exact.
Original scope/source-line/mask counterexamples and setup failures remain retained.
General reporting APIs, handlers and configured fatal display remain required;
the native source profile is30719, with fatal mask4437 inside `@`.

Reference returns remain accepted at9959e771 on942/3c331e74, preserving their
7951/dd8 one-state-test bridges. Acquisition933, typed926, strict917 and defaults909
retain their historical linked reviews and source identities.

Next is paired compiler102/runtime103 positional variadic receive; read the
[successor handoff](docs/semantics/RUNTIME-VARIADIC-HANDOFF.md).
Compiler7/runtime7/review10 continue under root coordination. Frozen56f4d181
preparation and its later STARTUP proposal are not implementation acceptance.

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
| 3a: control, exceptions, diagnostics and unwinding | Partial; loops/jumps, returns, suppression and fatal frame cleanup reviewed; exceptions/handlers pending |
| 3b: calls, closures and static checks | Partial; positional value/reference parameters, defaults, lexical strictness and builtin scalar/container value types reviewed; reference assignment/returns reviewed; remaining call protocols pending |
| 4a–b: linking and declarations | Partial; user constants and header/relation helpers reviewed; object execution pending |
| 5a–b: dynamic sources, services, resumability and lifetime | Pending |
| 6: complete inventory/review, differential campaign and offline audit | Pending |

Inventory: **169 constructors/306 runtime obligations**, with70 field domains.
The runtime inventory now records131 partial,174 pending and one validated
obligation. Accepted constants, defaults, strictness, builtin value types,
reference returns and suppression remain partial.
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

The [current successor handoff](docs/semantics/RUNTIME-VARIADIC-HANDOFF.md)
binds951 inputs and the next source-pipeline/variadic prerequisites. Compiler7,
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
