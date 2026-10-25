# Core PHP semantics progress

Target: **PHP 8.5.10 CLI, NTS, signed 64-bit integers**. [PLAN](PLAN.md) defines
complete core; the [inventory](coverage/semantics/features.json) tracks the 169
syntax constructors and 306 runtime obligations. The executable core remains
partial. Syntax acceptance and selected agreement do not establish full semantics
or BOLA freedom. [CORE](docs/semantics/CORE.md) defines the intrinsic boundary.

## Current checkpoint

Seven missing-CV comparisons now admit finite acyclic graphs of DIRECT array
edges, with primitive or live ordinary non-Stringable object leaves. Path-local
checks allow shared subtrees and remove the fixed depth limit. Captured deep COW
snapshots, live root aliases and final child release preserve destructor order
before the outer store or supplied-Exception catch. Legacy ALIAS payloads stay
primitive/object/one flat DIRECT child; source certificates and roots stay exact.

Ten normal source agreements and two Unsupported controls retain `54d6d1ead` and
`b077cd7ea`/409. All925 accepted raw premises/eight groups, seven affected source
selectors and five narrow reached predicates pass at `f428c4119`/409. The sixth
earlier pooled-child predicate reuses its `54d6d1ead` observation with zero renewal.
Original228 fixture failure and the assignment-owner observation retain zero;
three fixture guards select the settled post-operation cut without weakening
owner assertions. [DIRECT graph review](coverage/semantics/undefined-comparison-direct-array-graph-review.json).

Composed over `edbb8c01f`/410, preserving incoming CONFIG/array/collector/operator
behavior and captured Stringable queries. Accepted cuts keep409; composition adds no execution. Nested aliases,
deeper ALIAS payloads, internal/Stringable leaves, object-property cycles and
wider owning histories remain partial. Paused COMP88 remains untouched.

## Integrated behavior and entrypoints

Each family is bounded; its linked contract and inventory entries retain the
implemented cases, exclusions, exact tested revisions and independent reviews.

| Family | Current behavior and scope pointers |
| --- | --- |
| Source and compilation | Checked ASTs retain source occurrences, ordered publication, compilation phases and diagnostic priority. Dynamic source and request inputs have explicit provider boundaries. [Compiler](docs/semantics/SOURCE-COMPILER.md), [context](docs/semantics/SOURCE-CONTEXT.md), [dynamic source](docs/semantics/DYNAMIC-SOURCE.md). |
| Operators and warning decisions | Arithmetic/casts distinguish saved values from live CVs and stage supported diagnostics through callbacks. Direct NaN Boolean NOT/Boolean cast produce stricttrue/false after a live0.0 write; NaN array casting constructs a fresh singleton from that live float. Initially-NaN LEFT logical XOR caches post-warning truth across live RIGHT conversion, including remaining default Warning before a LEFT throw unwinds. Copied fractional BITNOT retains its saved integer. [Operators](docs/semantics/ORDINARY-OPERATORS.md), [truth callbacks](docs/semantics/SOURCE-WARNING-TRUTH.md), [numerics](docs/semantics/NUMERICS.md). |
| Comparisons and arrays | Seven missing-CV comparisons admit bounded DIRECT/ALIAS arrays, including ordinary non-Stringable object leaves. Recursive acyclic DIRECT array-edge graphs preserve shared deep COW snapshots and final child release; ALIAS-held child arrays stay flat. [DIRECT graph review](coverage/semantics/undefined-comparison-direct-array-graph-review.json), [child-array review](coverage/semantics/undefined-comparison-array-payload-review.json). Undefined key variables in array literals resume Warning callbacks with a fixed empty key and live null/bool/int/float CVs; initially owning ordinary ARRAY CVs also preserve acquisition and retarget retention/debt through throw and balanced inverse writes. [Primitive review](coverage/semantics/array-literal-undefined-key-warning-review.json), [ARRAY-CV review](coverage/semantics/array-literal-undefined-key-array-cv-review.json). NULL-key literals support bounded CV, returned, temporary and pooled CONST values, including nested DIRECT subtrees with physical child edges and handler-time COW. [Nested CONST review](coverage/semantics/array-literal-null-key-constant-subtree-review.json). [Comparisons](docs/semantics/COMPARISONS.md), [dimensions](docs/semantics/DIMENSIONS.md), [object-reference review](coverage/semantics/undefined-comparison-object-reference-array-review.json). |
| Calls and configuration | Ordinary/scoped/captured calls preserve selected targets, argument order, references and genuine callback frames. Two singleton INI_SET packs retain raw NULL/quiet ARRAY, callee and option through later effects. Initialized user Iterators stream integer-key/string sends into INI_SET with callback ordering, pre-API retirement and supplied-Exception recovery. Bounded WeakMaps now distinguish empty arity failure from occupied object-key Error before any current copy. [Calls](docs/semantics/SOURCE-CALLS.md), [include/configuration](docs/semantics/INCLUDE-SOURCES.md), [two-pack review](coverage/semantics/ini-set-two-pack-null-array-value-review.json), [Iterator CONFIG review](coverage/semantics/config-iterator-unpack-review.json), [WeakMap CONFIG review](coverage/semantics/config-weakmap-unpack-review.json). |
| Constants and callable values | Bounded DEFINE/CONSTANT/DEFINED preserve source authority, scopes, primitive/array/object snapshots and captured intrinsic Closure identity. Captured Boolean/integer/finite-float/NULL queries preserve strict ordinary versus weak explicit reception, raw/received trace arguments and callee ownership through deprecation callbacks. Captured positional Stringable queries distinguish ordinary prelookup destruction from explicit raw-wrapper retention and strict raw-object rejection. [Constant contract](docs/semantics/SOURCE-USER-CONSTANTS.md), [scalar-query review](coverage/semantics/constant-owned-scalar-query-review.json), [NULL-query review](coverage/semantics/constant-owned-null-query-review.json), [Stringable-query review](coverage/semantics/constant-owned-stringable-query-review.json). |
| Classes and properties | Visibility, references, typed writes, hooks, magic access and clone have bounded routes. Same-name implicit getter recursion delivers captured NULL for missing/untyped UNSET properties and a fresh declaring-class Error for public typed UNSET; defined NULL, local cleanup and replacement Previous retain their distinctions. [Properties](docs/semantics/SOURCE-PROPERTIES.md), [classes](docs/semantics/SOURCE-CLASSES.md), [recursion review](coverage/semantics/magic-get-recursion-review.json), [declared-UNSET review](coverage/semantics/magic-get-unset-recursion-review.json), [typed reentry review](coverage/semantics/magic-get-recursive-error-review.json). |
| Generators and Fibers | Supported suspension, delegation and cleanup preserve snapshots and initialization history. First CURRENT refresh through one quiet closed Child also retires the unused copy before receiver cleanup. [Refresh review](coverage/semantics/generator-refresh-unused-current-review.json). Unused CURRENT also retires its snapshot before a still-pending selected receiver, preserving both bits and live Middle-finally cleanup. [Pending CURRENT review](coverage/semantics/generator-pending-unused-current-review.json). Direct/one-ancestor node-free SEND handles supplied argument-destructor Exceptions and distinct unused/assigned owners. [Generators](docs/semantics/GENERATORS.md), [delegation](docs/semantics/GENERATOR-DELEGATION.md), [ancestor review](coverage/semantics/generator-ancestor-abrupt-argument-send-review.json). |
| Returns and lifetime | Bounded by-reference return/finally chains retain remaining owners, local catches and consumed recovery through normal/throw retirement. First C retirement with one REF/object remainder preserves local catch, the computed-return Notice and a detached caller cell. Singleton WeakMap collection follows canonical reference-cell backedges and array entries containing Key references, discovering conditional values from white keys without adding physical owners. Bounded foreach drops Map DATA at loop exit while copied object Key/Value CVs survive. [WeakMap review](coverage/semantics/weak-map-review.json). The finite `returns_verify` work is complete; wider PHP return and lifetime coverage remains open. [Return contract](docs/semantics/SOURCE-REFERENCE-RETURNS.md), [eager cleanup](docs/semantics/SOURCE-EAGER-DESTRUCTORS.md), [return review](coverage/semantics/reference-return-local-cv-lifetime-review.json). |
| Diagnostics and environment | Supported warning/exception handlers retain raw registration, selected callback and emitting frame. Request facts, inclusion and lifecycle effects stay explicit. [Handlers](docs/semantics/SOURCE-ERROR-HANDLERS.md), [exception handlers](docs/semantics/SOURCE-EXCEPTION-HANDLERS.md), [request inputs](docs/semantics/REQUEST-INPUTS.md). |

## Active and unintegrated work

No pending private milestone is recorded at this integration checkpoint.

Iterator49/50/51/52, V99/V100/V101/V102, M132/M133/M134/M135/M136, A46/A47/A48/A49, OP79/80/81/82, Source86/87/88, COMP118/119/120 and CLASS119/120/121 are integrated
into this branch.
Their accepted evidence keeps its original cuts; integration adds no new execution
credit. The active table is a handoff snapshot, not a claim of current validation
for private changes.

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
  initialized user Iterators and the bounded empty/singleton WeakMap slice.
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
