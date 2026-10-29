# Core PHP semantics progress

This project targets PHP 8.5.10 CLI, NTS, 64-bit. Executable core semantics and
source-driven differential validation are active; complete PHP core, the later
Rocq interaction-tree model and BOLA/CRIS verification remain unfinished.
[PLAN](PLAN.md) records settled scope; the [feature inventory](coverage/semantics/features.json)
and current family documents identify implemented routes and remaining obligations.

## Current checkpoint

ATTR01 adds builtin NoDiscard declarations with literal/NULL messages and
ordinary source-call warnings after sends/named defaults, before reception/body.
Selected references, real argument/receiver owners and caller-only traces survive
handlers and supplied throws; used results and callback APIs remain distinct.
Twenty-six originals agree, and four reached fronts pass 297 checks including 24
derived guards. Joined strict430 and the new FINAL callback control pass;
accepted private cuts are unchanged. Wider messages, targets, hooks and wrappers
remain partial.
[Attribute contract](docs/semantics/BUILTIN-ATTRIBUTES.md),
[review](coverage/semantics/builtin-nodiscard-review.json).

GC04 uses Zend's ordinary-sibling mark-on-push order for fresh quiet
no-WeakMap collection. A shared zero-declared property table counts as a real
array when claimed from a later field before the first object's proxy visit.
Two native-first inline/materialized originals agree at count 3; the old
model completed normally but counted 2 on the inline case. Three private
strict SL reached fronts pass 106 checks, including a protected forged-plan
rejection and real GC_FREE consumers. Private strict428 and actual-tail joined
strict429 compilation pass; source/reached cuts retain their original inputs.
The plan remains callback-free, PASS0, canonical and unmarked; current
callbacks, residual tags, workers, hooks and active contexts remain open.
[GC04 review](coverage/semantics/gc-ordinary-claim-review.json).

I75 is integrated: receiver-free static Generator bodies called through `self`,
`parent` or `static` retain the real factory's scope after return. Actual live
Generator owners authenticate resume and close, including a retired factory
selector, fresh same-context sibling and late static override. Six authored and
one independent source match PHP; four reached fronts pass 354 custom/374
reported checks. Private strict426 and actual-tail joined strict428 pass. The
peer's raw HEAD flag is false after a fixture-only commit; its watched inputs
stayed identical and independent review accepted the exact native agreement.
Keyword-invoked factory chains, Closure factories and receiver-bearing keyword
bodies remain partial. [I75 review](coverage/semantics/generator-keyword-creation-review.json).

CLASS148 is integrated: successful include/eval units now admit dependent anonymous
classes at existing no-argument CV-assignment sites. Each unit keeps its own namespace/import context,
frozen source-entry parent bindings and compiler-derived request-wide RTD cost.
Ordinary loader callbacks preserve retained loads, same-site retry and genuine
unit-specific publication causes. Body/default errors remain eager, with first-NEW
linking before construction. Eight native-first originals agree and strict428 plus
178 source-reached conditions pass, including independent unit-specific retry/cause
and frozen-entry no-lookahead checks. The original wrong expected-status row
remains zero credit, with only that corrected row rerun. Failed/open histories, broader placements/arguments and
enum/trait co-residence remain partial. Joined strict428 passes on the actual
enum-acquisition tail; accepted private source/state cuts retain their identities.
[Dynamic dependency review](coverage/semantics/anonymous-dynamic-dependencies-review.json).

GC03's quiet WeakMap registration/proxy-count behavior and its separate tested
cuts remain in the [GC03 review](coverage/semantics/gc-registration-order-review.json).
A67's typed-current behavior remains in the
[CONFIG contract](docs/semantics/INCLUDE-SOURCES.md).

Current combined behavior is summarized below. Family docs and linked reviews
retain exact admission limits, original failures and tested cuts; this file does
not repeat historical receipt counts or renew their execution credit.

## Integrated behavior and entrypoints

| Family | Current behavior and scope |
| --- | --- |
| Source and compilation | Checked ASTs retain source occurrences, ordered declaration publication, lexical/called scope and emitted-task authority. Include/eval, anonymous classes, traits and linked headers use source-authenticated routes; remaining acquisition and linker contexts stay explicit. [Source context](docs/semantics/SOURCE-CONTEXT.md), [linking](docs/semantics/LINKING-HANDOFF.md), [classes](docs/semantics/SOURCE-CLASSES.md). |
| Values, operators and warning decisions | Arithmetic and conversions are pure executable SpecTec. Supported warning callbacks preserve saved operands, live delayed reads, source sites, handler changes and pending-Throwable order. Operators, casts, dimensions and undefined-variable routes remain partial across their producers. [Numerics](docs/semantics/NUMERICS.md), [dimensions](docs/semantics/DIMENSIONS.md), [comparisons](docs/semantics/COMPARISONS.md). |
| Arrays and references | Physical owner edges distinguish DIRECT copies from ALIAS cells, COW table copies, selected lvalues and shared descendants. Iterator spreads retain raw current references through key before copying the value; invalid-key cleanup retires current before DATA while protecting the partial builder. Ordinary initialized declared fields share the reviewed fold across legal return modes. Materialized/special/cyclic graphs and wider callback lifetimes retain their documented limits. [Array unpack](docs/semantics/ARRAY-UNPACK.md), [reference wrappers](docs/semantics/REFERENCE-WRAPPERS.md), [cleanup review](coverage/semantics/array-iterator-invalid-key-cleanup-review.json), [field review](coverage/semantics/array-iterator-byval-fields-review.json). |
| Comparisons | Reached physical slots, count/key/value order, live reference contents and COW snapshots decide comparisons. Visited captured-graph traversal has no fixed depth limit and reports an authentic active-left recursion Error; earlier identity/class/leaf decisions skip later unsupported payloads. Canonical root admission and acyclic Previous-path validation have no numeric context/length ceiling. Standalone same-kind non-base roots also admit these traces with NULL Previous values, preserving physical cache/trace/severity order; the older DIRECT route remains disjoint. Invalid/cyclic/materialized/freeing Previous nodes, pending states and actually reached callback contexts retain family limits; base Exception/Error dispatch remains separate from other builtin kinds. [Current comparison contract](docs/semantics/COMPARISONS.md), [finite captured graphs](coverage/semantics/throwable-trace-unbounded-comparison-review.json), [finite Previous paths](coverage/semantics/throwable-previous-finite-comparison-review.json), [standalone traces](coverage/semantics/throwable-null-trace-comparison-review.json). |
| Calls and callable values | Ordinary, scoped, captured and magic-call routes retain the selected callee/receiver, lexical/called scope, argument origin, positional/named ordering and reference mode across later effects. Closure and pipe consumers preserve their real owners, send diagnostics and abrupt cleanup. Callable producers, signatures and reentry remain partial. Bounded NoDiscard declarations preserve pre-body warning and pending-owner behavior. [Attributes](docs/semantics/BUILTIN-ATTRIBUTES.md), [Calls](docs/semantics/SOURCE-CALLS.md), [Closure::call](docs/semantics/CLOSURE-CALL.md), [first-class callables](docs/semantics/SOURCE-FIRST-CLASS-CALLABLES.md). |
| Configuration and constants | Supported INI_SET/DEFINE/CONSTANT/DEFINED routes retain their selected callee, option/name and API timing. Iterator and named Generator inputs preserve real DATA/INPUT and Aggregate producer history, copied sends, named-key Error priority and pre-API cleanup. CONFIG typed-current reads reuse property-source validation; structural receipts remain valid after physical cache retirement. Capture uses the existing finite graph policy and SEND still requires strings. Wider producers, nonstring coercion and effectful lifetimes remain partial. [Include/configuration](docs/semantics/INCLUDE-SOURCES.md), [constants](docs/semantics/SOURCE-USER-CONSTANTS.md). |
| Classes, properties and enums | Linked declarations preserve receiver identity, slot declaration, visibility, typed-reference sources, readonly/hook policy and diagnostic order. Supported magic getters and reference-get chains preserve alias/copy and rebind timing. Enum declarations lower to cached singleton cases with lazy backing checks, readonly slots, ordered interfaces and generated/user methods. Registered-loader first use for static calls and class-constant fetches preserves selected class/member order and source-authenticated resume; reached dynamic/named/folded/enum cases and forged-target rejection retain separate raw cuts under `.tools/enum-acquisition-review-state-*`. Generated enum callable capture, default loader, case attributes, wider link/type contexts and object lifetimes remain partial. [Classes](docs/semantics/SOURCE-CLASSES.md), [properties](docs/semantics/SOURCE-PROPERTIES.md), [property references](docs/semantics/SOURCE-PROPERTY-REFERENCES.md), [enum evidence](docs/ARTIFACTS.md). |
| Generators and Fibers | Supported named/method/Closure producers retain actual resumer and callee owners, by-value or reference caches, supplied Throwables and catch/finally continuations across Fiber suspension. Receiver-free static Generator bodies called through `self`/`parent`/`static` retain real factory scope after return. Delegation and SEND preserve their selected chains and copied/delivered owners. Wider producers, binding/delegation combinations and teardown remain partial. [Generators](docs/semantics/GENERATORS.md), [Fibers](docs/semantics/FIBERS.md), [delegation](docs/semantics/GENERATOR-DELEGATION.md), [reference yields](docs/semantics/GENERATOR-REFERENCE-YIELDS.md). |
| Lifetime, weak references and collection | Eager release tracks real ownership, pending results/Throwables, destructor frames and protected storage. WeakMap protocols preserve weak-Key visibility, ordinary Value owners, aliases, selective notification and conditional collection. Physical tracing handles admitted ordinary/materialized graphs; quiet same-Key entries and no-Map ordinary siblings use claimed first-visit counts. Callback, residual and active collector contexts remain open. Stable retired cell metadata owns nothing; pooled literal arrays remain rooted by compiled constants. [Eager cleanup](docs/semantics/SOURCE-EAGER-DESTRUCTORS.md), [reference returns](docs/semantics/SOURCE-REFERENCE-RETURNS.md), [weak references](docs/semantics/WEAK-REFERENCES.md), [cycle collection](docs/semantics/CYCLE-COLLECTION.md). |
| Diagnostics, output and environment | Supported handlers retain registration, callback and emitting-frame identity through warnings, throws and cleanup. Echo/print preserve left-to-right effects and flat-array diagnostics; bounded default output buffers retain native callback/output order. Request, clock, stream and startup profiles have explicit contracts rather than ambient host answers. Wider buffering/shutdown/tick behavior remains open. [Handlers](docs/semantics/SOURCE-ERROR-HANDLERS.md), [exception handlers](docs/semantics/SOURCE-EXCEPTION-HANDLERS.md), [output buffers](docs/semantics/OUTPUT-BUFFERS.md), [request inputs](docs/semantics/REQUEST-INPUTS.md). |

## Decisions that constrain further work

- Implement PHP behavior in authored semantics, including pure arithmetic; the
  pinned project-local PHP binary is the differential oracle, never a runtime
  fallback. Core intrinsics/internal protocols are included where the language
  needs them; ordinary external libraries and services are separate.
- Authenticate execution from actual source, selected declarations and genuine
  frames. Historical/nonowning receipts preserve provenance; they neither own a
  dead value nor establish a current live alias.
- Keep acquisition, key evaluation, send snapshots, API reception and cleanup
  distinct. Type-source metadata constrains writes without adding owner edges;
  reading an authenticated typed cell does not perform coercion.
- Preserve diagnostic priority, skipped later work, PHP Error/Throwable identity,
  pending completion and physical lifetime. Explicit Unsupported, failed
  derivations, runner failures and timeouts are different outcomes.
- A bounded passing family does not close its inventory obligation. Extend
  coherent producers/consumers and shared invariants without special-casing
  spelling or weakening refusal boundaries.

OB01 integrates normal EOF and integer/string EXIT draining for existing user
output handlers after real shutdown/global/store retirement. Nested lower writes,
weak diagnostics and callback-local destructors preserve saved completion and the
sole handler owner. Fifteen native-first normal originals agree, six reached
groups pass 238 assertions, private strict427 and joined actual-tail strict429
pass. The first abnormal model timed out at 90 seconds and at reduced fuel/40
seconds before returning a state; the captured-throw model is unrun. Both remain
unresolved with zero model credit. [OB01 review](coverage/semantics/output-request-end-review.json).

## Active and unintegrated work

| Track | Owner-confirmed current work |
| --- | --- |
| A68 | Scalar INI_SET Iterator sends and saved argument lifetimes. |
| Enum M3/M4 | Generated-method callable capture/dispatch, backing-initializer dependency modes and wider enum acquisition; private. |
| V110 | Temporarily held/unintegrated after repeated generic cybersecurity-risk flag; CPU3 released, exact rejected action unknown. Accepted source3 retained. |
| COMP123 | Held unrun; no actor. |

The active table is an owner-confirmed handoff snapshot, not validation credit
for private changes. Integrated work is indexed by the current family docs,
[feature inventory](coverage/semantics/features.json) and linked reviews above;
[ARTIFACTS](docs/ARTIFACTS.md) locates original evidence and private cuts.

## Remaining core work

- Finish the partial inventory obligations across every source constructor and
  runtime dependency. Unsupported cases remain explicit; a passing bounded slice
  does not close its family.
- Extend warning/read/cast and argument consumers, callable/Closure forms,
  reference parameters/returns and constrained coercions without erasing delayed
  reads, diagnostic priority, saved targets or abrupt cleanup.
- Complete wider array/object/reference ownership, nested access and key forms,
  ArrayAccess/Iterator interactions, COW, released targets and callback lifetimes.
- Complete remaining class/static/trait/enum/attribute/hook/readonly contexts and
  wider magic/property/callable producers, including reentry and typed aliases.
- Complete wider Generator/Fiber suspension, delegation, destructor reentry,
  physical collection, weak-reference/WeakMap, output/shutdown/tick and other
  required lifecycle behavior.
- Extend remaining Traversable CONFIG producers, consumers and lifetimes beyond
  initialized user Iterators, fresh named Generators, their bounded Aggregate producers and the empty/singleton WeakMap slice.
- Extend dynamic compilation, startup/configuration profiles, environment and
  provider consumers within the agreed core/intrinsic boundary. Ordinary external
  libraries/services are separate; builtin presence alone supplies no semantics.
- Run final combined current-source validation and a fresh copied-path,
  network-isolated offline rebuild. Current local tool reuse is not that rebuild.

Interaction-tree semantics in Rocq and the selected BOLA/CRIS proofs follow
completed PHP core and renewed differential validation; they are not established
by these tests.

## Paused boundaries

Do not resume or broaden these lanes through neighboring work:

- OP12 increment/decrement dimension warnings.
- Source47 low-precision DEFINE-name NaN conversion.
- Owned-NUL source-release behavior.
- Undefined by-reference LIST key handling.
- COMP88 Stringable supplied-throw crash.

## Validation and evidence

Use the pinned project-local PHP oracle and matching profile. Preserve original
bytes/path/cwd, raw streams/status, semantic completion, tested revision,
compiler/runtime identity, commands and relevant environment. Ordinary, explicit
request and callable profiles retain separate contracts.

Independent review covers semantic correctness, counterexamples and test
reliability. Fix discrepancies narrowly; rerun affected checks only. Metadata
edits and pointwise disjoint composition do not renew accepted execution credit.
Interrupted, timed-out, Unsupported, malformed and budget-control outcomes remain
separate from native agreements. State fixtures complement source comparisons.

Large originals and raw failures stay outside Git; [ARTIFACTS](docs/ARTIFACTS.md)
provides recovery. Detailed prior checkpoints remain in their existing ledgers,
[MILESTONE-HISTORY](MILESTONE-HISTORY.md), and Git history through `25b63539e`.
The [post-arrow baseline](coverage/semantics/post-arrow-integration-review.json)
retains its historical profile/count identities, not current full-core coverage.
Keep this file focused on current behavior, remaining work and active boundaries;
replace superseded status prose instead of accumulating receipt history.
