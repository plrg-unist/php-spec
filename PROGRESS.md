# Core PHP semantics progress

This project targets PHP 8.5.10 CLI, NTS, 64-bit. Executable core semantics and
source-driven differential validation are active; complete PHP core, the later
Rocq interaction-tree model and BOLA/CRIS verification remain unfinished.
[PLAN](PLAN.md) records settled scope; the [feature inventory](coverage/semantics/features.json)
and current family documents identify implemented routes and remaining obligations.

## Current checkpoint

I80 admits captured ordinary user-method factories made with first-class
callables or `Closure::fromCallable` when they create scoped Generators. The
real selected method, source access, lexical/called scope and receiver are
borrowed after callable retirement; actual Generator resume/close ownership
and ordinary frame/cache roots remain unchanged. Three new authored, one
independent and one unchanged named-function control match PHP. Three reached
fronts pass 174 custom/189 reported checks; private and actual-tail joined
strict431 pass. The old first-class case was checked Unsupported with zero
agreement credit. Other callable factory kinds, wider binding, producer and lifecycle contexts
remain partial. [I80 review](coverage/semantics/generator-captured-factory-review.json).

GC06 carries an authenticated claimed count source through canonical materialized
ordinary destructor callbacks and PASS1, including retired original tables.
Ordered nested buffer removal preserves proxy-table count roles and free slots:
one first pass contributes 1 after debit 2, then retrace contributes 3.
Source-authenticated immediate `===`/`!==` temporary release and borrowed
matching `BASE` caches avoid false potential roots. Four native-first sources
agree at their recorded cuts; 11 reached SL groups pass 330 checks. Private
strict430 and actual-tail joined strict431 pass. WeakMap callbacks, skipped
prior histories, worker/residual/reentry paths, hooks, active contexts and wider
cache lifetimes remain partial.
[GC06 review](coverage/semantics/gc-materialized-claimed-callback-review.json).

Immediate identity cleanup now validates a sole produced right object/array
temporary with a borrowed or scalar left operand in both AL and SL. Fourteen
focused conditions pass in each mode, including strict compilation of the actual
431-module tail; the affected cached-enum Stringable original matches PHP again.
Existing owners and collection policy are unchanged.
[Identity receipt review](coverage/semantics/identity-produced-right-review.json).

Earlier [I75](coverage/semantics/generator-keyword-creation-review.json),
[I76](coverage/semantics/generator-keyword-chain-review.json),
[I77](coverage/semantics/generator-keyword-receiver-review.json),
[I78](coverage/semantics/generator-closure-factory-review.json) and
[I79](coverage/semantics/generator-closure-method-review.json) reviews retain
their distinct scope, counts and raw failures.

CONFIG Iterator sends preserve scalar snapshots and finite CFG-admitted ARRAY or
ordinary non-Stringable INSTANCE arguments. Existing by-value Generator routes
also copy flat scalars before later resumes; INI_SET conversion, strict errors and
NULL handlers follow traversal and DATA/INPUT cleanup. COW protects array tables,
while embedded aliases, object identity and API TraceArgs retain ordinary owners.
Owning Iterator aborts release CURRENT, DATA/INPUT, then the copied prefix. Admitted
last-owner temporary Iterator INPUT finalizers keep live copied arguments protected.
Typed-source reads and existing producer/key/finite-graph policies stay intact;
named direct-CV Generator reference yields now copy scalars from authenticated
ordinary cells before later writes. Last-DATA reference retirement, typed Generator
cells, owning Generator arguments, effectful casts and wider lifecycles remain partial.
[Owning arguments](coverage/semantics/config-iterator-argument-review.json),
[INPUT cleanup](coverage/semantics/config-iterator-input-finalizer-review.json),
[Generator scalars](coverage/semantics/config-generator-scalar-review.json),
[Generator reference scalars](coverage/semantics/config-generator-reference-scalar-review.json),
[CONFIG contract](docs/semantics/INCLUDE-SOURCES.md).

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

ATTR02 adds literal/NULL-message and since Deprecated declarations for named
functions and ordinary methods. Prepared VM calls warn after sends and named-hole
completion, before NoDiscard and reception, for used and discarded results.
Selected arguments, references and receivers survive handlers and abrupt cleanup.
Thirteen originals agree exactly (nine authored, four independent);
at the ATTR02 cut, two internal API cases were explicit Unsupported with zero
agreement credit.
Four reached fronts pass 314 conditions: 278 source-reached checks, 24 derived
guards and 12 raw API projections. Private and actual-tail joined strict430
pass; earlier failed fixtures retain zero credit. Wider messages, targets,
wrappers and other internal API consumers remain partial.
[Attribute contract](docs/semantics/BUILTIN-ATTRIBUTES.md),
[ATTR02 review](coverage/semantics/builtin-deprecated-review.json).

ATTR03 stages selected error-handler and `assert` callbacks at the internal API
phase: Deprecated precedes copies, by-reference warnings and reception. Error
handlers run with their registry disabled; `assert` warnings retain the active
handler, saved target and live failure policy. Captured Closure targets stay
borrowed until one call owner starts at entry. Ten new native-first originals
agree exactly, including one unmarked control; four reached fronts pass 179
conditions (172 reached, seven derived guards), and private and actual-tail
joined strict431 pass.
The maintained ATTR02 `assert` boundary is promoted without replay or new
agreement credit. Explicit captured-Closure `__invoke()` and wider API consumers
remain partial. [ATTR03 review](coverage/semantics/builtin-deprecated-api-review.json).

ATTR04 extends that selected API cursor to exception handlers, including
unmarked callbacks. Deprecated precedes copies and by-reference warnings;
the moved registry owns the selected callback and the cursor holds the original
Throwable. Warning-handler replacement and nested exception reentry preserve
the original target; Closure call ownership begins at entry and can end before
readonly result validation. Nine new native-first originals agree, including
two terminal fatals. Four reached fronts pass 189 checks (184 reached, five
derived), and private and actual-tail joined strict431 pass. One measured old
API refusal remains zero credit. Effectful special callables and the explicit Closure wrapper stay
partial. [ATTR04 review](coverage/semantics/builtin-deprecated-exception-api-review.json).

The earlier GC05 cut admitted public destructors on quiet, canonical
materialized ordinary cycles when the legacy callback walk and claimed walk
agree on ordered visits and counted nodes in the actual collector plan. The
collector rechecks after callback
mutation and before fresh collection of already-called survivors, refusing an
order mismatch. Two native-first sources agree, including resurrection followed
by later count 3; four strict SL reached groups pass 151 checks. Private strict429
and actual-tail joined strict430 compilation pass; source and reached cuts retain
their original inputs. At that cut, count-ambiguous callbacks, WeakMap callbacks,
residual tags, workers, hooks, reentry and active contexts remained partial.
[GC05 review](coverage/semantics/gc-materialized-callback-review.json).

CLASS152 removes the two-formal/send bound for admitted anonymous constructors.
Finite direct positional/named sends and public unpromoted by-value signatures
use ordinary type/default compilation and binding, including inherited calls and
named-hole completion before typed reception. Full class identities survive
argument-TypeError whole-name formatting and missing-arity class/member formatting.
Six originals agree (five normal, one compiler rejection), and 212 conditions pass
across authored62 and independent150 reached groups. Corrected private and
actual-tail joined strict431 pass; all cuts retain their actual revisions. The original diagnostic mismatch
and carrier-fixture refusal retain zero credit. Reference/variadic/promoted,
nonpublic, unpacked and wider body/factory/lifetime contexts remain partial.
[Finite-constructor review](coverage/semantics/anonymous-constructor-arity-review.json).
The prior [rejected-source review](coverage/semantics/anonymous-rejected-sources-review.json)
retains CLASS151 source5/state261 and zero-cost parser-rejection history at its own cuts.

GC03's quiet WeakMap registration/proxy-count behavior and its separate tested
cuts remain in the [GC03 review](coverage/semantics/gc-registration-order-review.json).
Typed-current capture and scalar argument snapshots remain in the
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
| Comparisons | Reached physical slots, count/key/value order, live reference contents and COW snapshots decide comparisons. Visited captured-graph traversal has no fixed depth limit and reports an authentic active-left recursion Error; earlier identity/class/leaf decisions skip later unsupported payloads. Canonical root admission and acyclic Previous-path validation have no numeric context/length ceiling. Canonical same-kind roots of the admitted builtin kinds share the visited physical-slot fold after older admissions once both finite Previous paths authenticate, preserving cache/trace/previous/severity order and reached table effects. Invalid/cyclic/materialized/freeing Previous nodes, pending states and actually reached callback contexts retain family limits. Captured canonical builtin Throwables share this fold; every distinct equal-kind entry checks active-left recursion before slots, including Previous descent. Supported initialized-public ordinary images admit uncalled methods and locally authenticated declared interfaces, including implicit Stringable; parent/hook/readonly and wider layout fences remain. Whole-path authentication stays eager. [Current comparison contract](docs/semantics/COMPARISONS.md), [finite captured graphs](coverage/semantics/throwable-trace-unbounded-comparison-review.json), [finite Previous paths](coverage/semantics/throwable-previous-finite-comparison-review.json), [standalone traces](coverage/semantics/throwable-null-trace-comparison-review.json), [base fallback](coverage/semantics/throwable-base-null-comparison-review.json), [linked base](coverage/semantics/throwable-base-previous-comparison-review.json), [captured Throwables](coverage/semantics/throwable-captured-comparison-review.json), [ordinary methods](coverage/semantics/throwable-trace-methods-comparison-review.json), [local interfaces](coverage/semantics/throwable-trace-interfaces-comparison-review.json). |
| Calls and callable values | Ordinary, scoped, captured and magic-call routes retain the selected callee/receiver, lexical/called scope, argument origin, positional/named ordering and reference mode across later effects. Closure and pipe consumers preserve their real owners, send diagnostics and abrupt cleanup. Callable producers, signatures and reentry remain partial. Bounded NoDiscard declarations preserve pre-body warning and pending-owner behavior. [Attributes](docs/semantics/BUILTIN-ATTRIBUTES.md), [Calls](docs/semantics/SOURCE-CALLS.md), [Closure::call](docs/semantics/CLOSURE-CALL.md), [first-class callables](docs/semantics/SOURCE-FIRST-CLASS-CALLABLES.md). |
| Configuration and constants | Supported INI_SET/DEFINE/CONSTANT/DEFINED routes retain their selected callee, option/name and API timing. Iterator and named Generator inputs preserve real DATA/INPUT and Aggregate producer history, copied sends, named-key Error priority and pre-API cleanup. CONFIG typed-current reads reuse property-source validation; structural receipts remain valid after physical cache retirement. Iterator sends retain raw scalar snapshots or real finite ARRAY/ordinary-instance slot roots, then defer INI_SET binding/conversion until after DATA/INPUT cleanup. COW, shared embedded aliases and API TraceArgs keep their ordinary owners. Generator/other consumers, effectful casts and wider lifetimes retain their documented limits. [Include/configuration](docs/semantics/INCLUDE-SOURCES.md), [constants](docs/semantics/SOURCE-USER-CONSTANTS.md). |
| Classes, properties and enums | Linked declarations preserve receiver identity, slot declaration, visibility, typed-reference sources, readonly/hook policy and diagnostic order. Supported magic getters and reference-get chains preserve alias/copy and rebind timing. Enum declarations lower to cached singleton cases with lazy backing checks, readonly slots, ordered interfaces and generated/user methods. Registered-loader first use for static calls and class-constant fetches preserves selected class/member order and source-authenticated resume; reached dynamic/named/folded/enum cases and forged-target rejection retain separate raw cuts under `.tools/enum-acquisition-review-state-*`. Captured enum `cases(...)` preserves its selected target and singleton cache after closure retirement. Captured scalar `from(...)`/`tryFrom(...)` preserve cold backing tables, ordinary/inherited constant aliases, caller strictness and cached case identity after closure retirement. Captured Stringable arguments preserve their real callback child and line, selected closure lifetime and temporary retirement before lookup. For published enums, class-string array callables select generated `cases()`/`from()`/`tryFrom()` before argument evaluation; a case-object receiver also invokes `from()`. Array Stringable conversion preserves the selected enum and temporary retirement. Source-certified direct or negated enum-case conditions in class constants retain selected case identity or scalar results, including a condition from another enum; wider object-valued conditional transfers, other callable routes, the default loader, case attributes, link/type contexts and object lifetimes remain partial. [Classes](docs/semantics/SOURCE-CLASSES.md), [properties](docs/semantics/SOURCE-PROPERTIES.md), [property references](docs/semantics/SOURCE-PROPERTY-REFERENCES.md), [enum evidence](docs/ARTIFACTS.md). |
| Generators and Fibers | Supported named/method/Closure producers retain actual resumer and callee owners, by-value or reference caches, supplied Throwables and catch/finally continuations across Fiber suspension. Receiver-free static and same-`$this` nonstatic Generator bodies called through finite scoped chains retain real scope after return; supported real Closure and captured ordinary user-method factories also authenticate scoped method-created bodies when the original source scope differs. Delegation and SEND preserve their selected chains and copied/delivered owners. Wider producers, binding/delegation combinations and teardown remain partial. [Generators](docs/semantics/GENERATORS.md), [Fibers](docs/semantics/FIBERS.md), [delegation](docs/semantics/GENERATOR-DELEGATION.md), [reference yields](docs/semantics/GENERATOR-REFERENCE-YIELDS.md). |
| Lifetime, weak references and collection | Eager release tracks real ownership, pending results/Throwables, destructor frames and protected storage. WeakMap protocols preserve weak-Key visibility, ordinary Value owners, aliases, selective notification and conditional collection. Physical tracing handles admitted ordinary/materialized graphs; quiet same-Key entries and no-Map ordinary siblings use claimed first-visit counts. Canonical materialized destructor callbacks retain claimed count and nested-buffer authority across retrace; source-authenticated immediate identity cleanup borrows matching result caches. WeakMap callbacks, skipped prior histories, residual and active collector contexts remain open. Stable retired cell metadata owns nothing; pooled literal arrays remain rooted by compiled constants. [Eager cleanup](docs/semantics/SOURCE-EAGER-DESTRUCTORS.md), [reference returns](docs/semantics/SOURCE-REFERENCE-RETURNS.md), [weak references](docs/semantics/WEAK-REFERENCES.md), [cycle collection](docs/semantics/CYCLE-COLLECTION.md). |
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
pass. Its original 90/40-second abnormal timeouts and then-unrun captured throw
retain their historical zero-credit status. OB02 now covers those sources at
new tested cuts. [OB01 review](coverage/semantics/output-request-end-review.json).

OB02 admits default fatal takeover from builtin FINAL throws with scalar messages
and NULL previous. Stored traces and cache mutation precede fatal reporting;
inactive buffers then release raw owners without lower writes. Four originals
match PHP and three reached groups pass 131 assertions. Actual-tail strict431
and both affected guard fronts (70+33) pass without native or differential source
reruns. Its original pending-Throwable decrement admission was nonfinal or
destructor-inactive; OB03 extends it below. Selected exception handlers, wider
rendering and reentrant/abrupt deactivation remain partial.
[OB02 review](coverage/semantics/output-final-throw-review.json).

OB03 releases the retained local FINAL Throwable after cache/reporting while
buffers remain active/running; child output stays buffered. A child destructor
throw preserves the first report, emits a fresh unchained fatal and retains the
existing abandoned C cleanup owners before raw-zoh deactivation. Four originals
agree exactly and four reached groups pass 169 checks. Private and actual-tail
joined strict431 and separate affected FINAL fronts 77+33 pass. The original sole Unsupported and later failed
attempts retain zero agreement credit. Wider selected-handler/rendering and
reentrant/abrupt raw-owner teardown remain partial.
[Pending-release review](coverage/semantics/output-pending-release-review.json).

## Active and unintegrated work

| Track | Owner-confirmed current work |
| --- | --- |
| COMP157 | Inherited ordinary initialized-public images; independent packet frozen, source preparation. |
| ATTR05 | Explicit captured-Closure `__invoke()` warning phases; five native-first originals frozen, private preparation. |
| Enum M3/M4 | Published-enum array dispatch is integrated for reviewed class-string and case-object sources, including named Stringable arguments. String callable routes, wider generated dispatch, backing dependency and the default loader remain partial. |
| A73 | Quiet CLOSED scalar REFCELL retirement from sole Generator DATA; native-first preparation. |
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
