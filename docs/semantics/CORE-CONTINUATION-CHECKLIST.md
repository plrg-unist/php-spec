# Full-core successor checklist

Management snapshot, not coverage closure. The [inventory](../../coverage/semantics/features.json)
has169 constructors and306 obligations:134 partial,171 pending,1 validated
(oracle identity). Only6 obligation rows currently record dependency edges.
Scheduling dependencies below are derived from [PLAN phases12–14](../../PLAN.md)
and the [activation plan](../../docs/semantics/CALLS-ACTIVATION-PLAN.md), not a
claim that the inventory dependency graph is complete.

## Checkpoint and next acceptance units

- [x] Firstcalls' current state/reviewer gate and exact canonical publication
  bridge accepted at **f3149e32**. Its5751-lint/5783-assertion broad compiler gate is reviewed;
  it does not replace full runtime/syntax/offline gates. Preserve firstcall versus
  historical quiet/request identities and newly retired control source hashes.
- [x] Positional reference parameters, temporary DIM/list ownership and checked
  resume integrity are accepted in code **31640654**. The
  [review](../../coverage/semantics/reference-parameter-review.json) retains
  frozen882 and its explicit canonical884 bridge, 166 source replays,
  61 independent original agreements, 283 shared regressions and independent
  state8/1,868 assertions. Author state6/1,413 and canonical CLI8 pass.
  This bounded acceptance closes no callable or core family.
- [x] Ordinary user-constant declarations/reads and nonowning allocation classes
  are accepted in [user-constant-review.json](../../coverage/semantics/user-constant-review.json).
  Frozen899/e7d552ec gates bridge to899/ca3c06e5 through one corrected state-test
  assertion. Constant-family closure, PHP_VERSION value reads, class/callable
  constants and dynamic registration remain pending.
- [x] Untyped positional defaults through compiler90/runtime91 are accepted at
  c7cb1b44 on exact909/e25eb2b9. The [review](../../coverage/semantics/default-parameter-review.json)
  binds original-context receives/caches, fresh reference/array owners, shared
  opcode-line/readiness repairs, four independent states / 1,091 assertions and CLI8.
- [x] Strict-only source declarations and source-bound unit/function flags are
  reviewed on917/309b046c in [strict-declaration-review.json](../../coverage/semantics/strict-declaration-review.json).
  Compiler92/runtime93 preserve untyped calls/defaults/reference owners; two
  independent cache states/543 assertions and three complete weak909 state bridges
  pass. Other declare directives remain open.
- [x] Builtin scalar/container positional parameters and value returns through
  compiler94/runtime95 are accepted at e097f95e on926/599f3963, code0ed17419.
  [Review](../../coverage/semantics/typed-function-review.json):15 native profiles
  plus3 dependency controls,5 states/1357,19 retained protocol/217 and2 complete
  untyped917 bridges. Author38/3 cache projections,4 states/1096, compiler56+8/38,
  corrected fresh19/218 and CLI8 pass; semantic926/baa identities remain distinct.
- [x] Direct-call reference assignment is accepted at36224bc3 on933/7391ccdf,
  codeaf228143. [Review](../../coverage/semantics/call-reference-review.json)
  binds7 native+4 pending controls,13 protocol/227,3 states/819 and2 exact926
  bridges; author17/2 states553, compiler26+3/29, typed38/adjacent13 and CLI8 pass.
  Shared call/enclosing emission lines and finite source/result guards are reviewed.
- [x] Source reference returns through98/99 are accepted at9959e771 on942/3c331e74,
  code563fee7a. [Review](../../coverage/semantics/reference-return-review.json)
  binds12 native,26 protocol/378,4 states/1282 and2 exact933 bridges; author31,
  compiler56+2/49, demand19/38,2 states/777, typed38/acquisition17 and CLI8 pass.
  Semantic7951 and regressiondd8 retain a one-state-test bridge to3c.
- [x] Source suppression through100/101 is accepted at29baca42 on951/c6501bd8,
  code14003331. [Review](../../coverage/semantics/error-suppression-review.json)
  binds4 native,23 protocol/489,4 states/1312 and2 exact942 old-field bridges;
  author26,37 reporter checks,17 compiler/131,19 demand/38,2 states/779,
  reference-return31 and CLI8 pass. Semanticff8d retains a one-print bridge.
- [ ] General reporting configuration, handlers and configured fatal display;
  class/object/callable/iterable types, typed-property reference constraints and
  mixed-unit strictness source integration remain required dependent work.
- [x] Defer eager variadic-default/void parser checks to existing static compilation;
  accepted51ca21db on951/440f3966, code c00a5c38. Exact PHPT/source/CLI phases and
  patch reproduction are bound by the [review](../../coverage/semantics/parameter-phase-review.json).
- [x] Paired102/103 positional variadics accepted at4187c887 on959/4854, codeb49a564c.
  [Review](../../coverage/semantics/variadic-review.json) binds4 native profiles,
  20 protocol/372,4 states/1322 and2 exact951 bridges with no projection;
  author28 source,23+2 compiler/194,2 states/829,8 regressions andCLI8 pass.
  Semanticcee5, compiler-test4d69 and timeout-only4854 retain separate identities.
- [x] Named104/105 accepted at1a562e8f on968/ab389, codecb1febe7.
  [Review](../../coverage/semantics/named-review.json) binds5 source profiles,
  44 protocol/935,4 states/731 and2 complete959 bridges removing only empty NAMED;
  author70 source,55+6 compiler/129,12 regressions,2 states/373 andCLI8 pass.
  Semantic55cd and regression-selection-onlyab389 retain distinct identities.
- [x] Builtin named compiler106 acceptedbb38d1d7 on972/e1bf, code84fc35f5.
  [Review](../../coverage/semantics/builtin-named-review.json) binds780 signatures,
  source modes/static priorities and reproducible generation; no builtin execution.
- [x] Direct user-function array call unpack107/108 accepted e45c7139 on981/3f3,
  codeadb21f56. [Review](../../coverage/semantics/call-unpack-review.json) binds55
  source outcomes,29 compiler phases/56 projections,34 protocol/824, author2
  states/435, independent4 states/1063 and14 full old972 compatibility cuts.
  Traversable and builtin execution remain required.
- [x] Current ordinary/request/callable integration before109; [review](../../coverage/semantics/callable-integration-review.json)
  binds5706+21 ordinary,263 request,751 callable and5751 compiler observations,
  exact profiles/raw closures and981/3f3→764 one-test bridge.
- [ ] Dynamic string calls109/110 after root checkpoint read; see the
  [handoff](DYNAMIC-CALL-HANDOFF.md).
- [ ] Complete named/unpacked/variadic sends, then captures/closures/arrows,
  first-class/dynamic callables, function statics, pipe and argument introspection.
  Use the same call/ownership protocol; object-bound callable cases join objects.

## Remaining dependency lanes

| Lane | Required work and dependencies | Evidence/exit route |
| --- | --- | --- |
| Existing scalar/container closure | Remaining numeric/byte/interpolation/string-increment, source encoding/preamble/halt, access/COW/typed-reference and object-coercion branches remain open. Preserve reviewed scalar/array behavior while completing dependent objects/types. | [Array omissions](../../docs/semantics/ARRAY-OMISSIONS.md), [numerics](../../docs/semantics/NUMERICS.md), inventory phase0b–2b |
| Control and diagnostics | Switch/match, labels/goto, throw/catch/finally, reporting/handler stacks and exit remain explicit. Throwable objects and callbacks depend on minimal objects plus calls; nested cleanup must use shared unwinding. | Inventory3a/diagnostics; [CORE execution](../../docs/semantics/CORE.md) |
| Objects/declarations | Ordered member compilation/linking/availability, inheritance/interfaces/traits/visibility, identity/creation/clone, method invocation and late-static scope; then typed/readonly/asymmetric/hooked/magic properties, enums, attributes and constants. | [Linking handoff](../../docs/semantics/LINKING-HANDOFF.md); source activation and alias/type-source/reentry gates, not header helpers alone |
| Required intrinsics/protocols | Implement the reviewed CORE catalog through ordinary calls: Throwable/Closure, iteration/ArrayAccess/Stringable, exit/clone, assertions, introspection, registration APIs and builtin attribute behavior. Registered-name780/arginfo metadata is not builtin execution. | [Exact catalog](../../docs/semantics/CORE.md); no ordinary-library exclusion may discharge a core obligation |
| Dynamic sources/environment | Checked eval/include/require/once, source identity/scope/failure, dynamic declarations and autoload; explicit finite shell/source services. Two later-eval request callback witnesses remain pending. | Inventory5a/environment; actual source-service→compile→execution path, no Zend evaluation fallback |
| Resumption/lifetime | Generators/yield-from/Fibers, suspension/finally/throw, destructors/reentry, shutdown/ticks/output callbacks, cycle collection/weak references/resurrection. Depend on calls, objects and shared unwind/ownership. | Inventory5b and CORE protocols; retained-root and resumed/error/source interaction tests |

## Parallel work boundaries

Root coordinates two implementers plus an independent reviewer. While runtime
pairs a frozen compiler stage, compiler work may independently capture the next
header/default originals or research object declaration/linking semantics.
Object research can produce source-backed tables and interface proposals before
method/property runtime exists; it cannot claim source admission. Assign shared
state/compiler/emitter/registry files explicitly before integration. Keep private
roots and copied tools separate; no concurrent shared build/index mutation.
Reviewer owns checkpoint PROGRESS/inventory corrections and accepts each exact
combined candidate independently.

## Closure gates

- [x] PROGRESS distinguishes historical5753/current5750 compiler evidence from
  the accepted5751 checkpoint and first frame/return/call slice; later stages remain explicit.
- [ ] Populate/audit dependencies and every obligation's remaining branches.
  Namespace-relative static remains the sole intentional divergence, confined to
  the pending class-scope declaration-type branch.
- [x] Run current all-source campaigns at the combined callable checkpoint; repeat
  when unresolved shared regressions require it. Preserve raw failures and all source
  identities; Unsupported, timeouts and tool errors never pass.
- [ ] Finish complete inventory/review, full syntax, and a fresh network-isolated
  offline rebuild/audit against actual final inputs. No full-core completion report
  until every required obligation and dependency closes. Never push.
