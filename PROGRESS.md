# Core PHP semantics progress

Target: **PHP 8.5.10 CLI, NTS, signed 64-bit integers**. [PLAN](PLAN.md) defines
complete core; the [inventory](coverage/semantics/features.json) tracks the 169
syntax constructors and 306 runtime obligations. The executable core remains
partial. Syntax acceptance and selected agreement do not establish full semantics
or BOLA freedom. [CORE](docs/semantics/CORE.md) defines the intrinsic boundary.

## Current checkpoint

Literal `$this` now enters bounded by-value Get using the actual current receiver
and the existing source certificate. Saved caller DECL/history survives a global
Warning handler with no `$this`; captured NULL survives live9 and later reset.
After Get clears the global CV and releases its hold, the read-method receiver
remains until `m`, then destruction precedes caller output.

Four new source agreements retain `ce3f1b081`/414;488 focused conditions
(451 reached+37 derived) retain `171a2dbc2`/414. INITIAL is an existing control.
The original fixture false and shared-state diagnostic retain zero credit.
[Literal-this Get review](coverage/semantics/magic-get-direct-this-review.json)
records the bounded scope, correction and415 composition without renewed execution.

## Integrated behavior and entrypoints

Each family is bounded; its linked contract and inventory entries retain the
implemented cases, exclusions, exact tested revisions and independent reviews.

| Family | Current behavior and scope pointers |
| --- | --- |
| Source and compilation | Checked ASTs retain source occurrences, ordered publication, compilation phases and diagnostic priority. Dynamic source and request inputs have explicit provider boundaries. [Compiler](docs/semantics/SOURCE-COMPILER.md), [context](docs/semantics/SOURCE-CONTEXT.md), [dynamic source](docs/semantics/DYNAMIC-SOURCE.md). |
| Operators and warning decisions | Arithmetic/casts distinguish saved values from live CVs and stage supported diagnostics through callbacks. Direct NaN Boolean NOT/Boolean cast produce stricttrue/false after a live0.0 write; NaN array casting constructs a fresh singleton from that live float. Initially-NaN LEFT logical XOR caches post-warning truth across live RIGHT conversion, including remaining default Warning before a LEFT throw unwinds. Retained-reference Boolean NOT keeps its captured inner cell across source unset/rebinding. NaN LEFT short-circuit decisions use post-callback truth to skip or enter RIGHT. NaN shorthand ternary preserves the live selected value after its callback. A LEFT-array Warning may install a same-cell Stringable RHS; real conversion retains its selected receiver through source retargeting. Copied fractional BITNOT retains its saved integer. [Operators](docs/semantics/ORDINARY-OPERATORS.md), [truth callbacks](docs/semantics/SOURCE-WARNING-TRUTH.md), [numerics](docs/semantics/NUMERICS.md). |
| Comparisons and arrays | Seven missing-CV comparisons admit bounded DIRECT/ALIAS arrays, including ordinary non-Stringable object leaves. Recursive acyclic DIRECT array-edge graphs also pass through ALIAS payload cells, preserving deep COW snapshots, live replacements and final transitive release. [ALIAS DAG review](coverage/semantics/undefined-comparison-alias-direct-dag-review.json). [DIRECT graph review](coverage/semantics/undefined-comparison-direct-array-graph-review.json), [child-array review](coverage/semantics/undefined-comparison-array-payload-review.json). Undefined key variables in array literals resume Warning callbacks with a fixed empty key and live null/bool/int/float CVs; initially owning ordinary ARRAY CVs also preserve acquisition and retarget retention/debt through throw and balanced inverse writes. [Primitive review](coverage/semantics/array-literal-undefined-key-warning-review.json), [ARRAY-CV review](coverage/semantics/array-literal-undefined-key-array-cv-review.json). NULL-key literals support bounded CV, returned, temporary and pooled CONST values. Nested DIRECT TMP graphs preserve shared physical child edges and handler-time COW, cascading unowned runtime descendants while folded siblings remain pooled. [Nested TMP review](coverage/semantics/array-literal-null-key-array-tmp-subtree-review.json), [nested CONST review](coverage/semantics/array-literal-null-key-constant-subtree-review.json). String R-offset callbacks preserve selected old carriers and live primitive cast keys; fixed bounds completion survives source/key unset, with pending-throw default/suppression. [String-read review](coverage/semantics/string-offset-read-warning-review.json). [Comparisons](docs/semantics/COMPARISONS.md), [dimensions](docs/semantics/DIMENSIONS.md), [object-reference review](coverage/semantics/undefined-comparison-object-reference-array-review.json). |
| Calls and configuration | Ordinary/scoped/captured calls preserve selected targets, argument order, references and genuine callback frames. Two singleton INI_SET packs retain raw NULL/quiet ARRAY, callee and option through later effects. Initialized user Iterators stream integer-key/string sends into INI_SET with callback ordering, pre-API retirement and supplied-Exception recovery. Ordinary Aggregate producers call real getIterator and transfer its retained Iterator result into DATA. Fresh named Generator consumers retain DATA and finish native resumes before API reception. Bounded WeakMaps distinguish empty arity failure from occupied object-key Error before any current copy. [Calls](docs/semantics/SOURCE-CALLS.md), [include/configuration](docs/semantics/INCLUDE-SOURCES.md), [two-pack review](coverage/semantics/ini-set-two-pack-null-array-value-review.json), [Iterator CONFIG review](coverage/semantics/config-iterator-unpack-review.json), [WeakMap CONFIG review](coverage/semantics/config-weakmap-unpack-review.json), [Aggregate CONFIG review](coverage/semantics/config-aggregate-iterator-unpack-review.json), [Generator CONFIG review](coverage/semantics/config-generator-unpack-review.json). |
| Constants and callable values | Bounded DEFINE/CONSTANT/DEFINED preserve source authority, scopes, primitive/array/object snapshots and captured intrinsic Closure identity. Captured Boolean/integer/finite-float/NULL queries preserve strict ordinary versus weak explicit reception, raw/received trace arguments and callee ownership through deprecation callbacks. Captured positional Stringable queries preserve conversion/destruction order, strict rejection and trace ownership. Destructor Exceptions keep ordinary lookup active with Error/Previous chaining; explicit cleanup omits completed API/wrapper frames. Captured positional nonStringable queries reject with raw API/wrapper traces and retain objects through copied argument arrays. [Constant contract](docs/semantics/SOURCE-USER-CONSTANTS.md), [scalar-query review](coverage/semantics/constant-owned-scalar-query-review.json), [NULL-query review](coverage/semantics/constant-owned-null-query-review.json), [Stringable-query review](coverage/semantics/constant-owned-stringable-query-review.json), [destructor-query review](coverage/semantics/constant-owned-stringable-query-throw-review.json), [nonStringable-query review](coverage/semantics/constant-owned-nonstringable-query-review.json). |
| Classes and properties | Visibility, references, typed writes, hooks, magic access and clone have bounded routes. Accessible nonpublic UNSET Get retains the caller-selected physical DECL/type across Child scope and backing population. Bounded literal-this Get authenticates receiver identity and preserves saved history through callbacks and method retirement. Bounded same-name recursion distinguishes captured NULL, typed Error and visibility Error; real guards survive local cleanup. [Properties](docs/semantics/SOURCE-PROPERTIES.md), [classes](docs/semantics/SOURCE-CLASSES.md), [recursion review](coverage/semantics/magic-get-recursion-review.json), [declared-UNSET review](coverage/semantics/magic-get-unset-recursion-review.json), [typed reentry review](coverage/semantics/magic-get-recursive-error-review.json), [denied reentry review](coverage/semantics/magic-get-denied-recursion-review.json), [scoped getter review](coverage/semantics/magic-get-scoped-unset-review.json), [literal-this review](coverage/semantics/magic-get-direct-this-review.json). |
| Generators and Fibers | Direct named bodies entered by CURRENT/NEXT preserve their authentic resumer across Fiber suspension and supplied-Throwable injection, with distinct fresh/cached reentry Errors. [Transfer review](coverage/semantics/generator-fiber-transfer-review.json). Shared delegation, initialization history, unused snapshots and abrupt SEND cleanup retain their bounded contracts. [Generators](docs/semantics/GENERATORS.md), [Fibers](docs/semantics/FIBERS.md), [delegation](docs/semantics/GENERATOR-DELEGATION.md), [refresh review](coverage/semantics/generator-refresh-unused-current-review.json). |
| Returns and lifetime | Bounded by-reference return/finally chains retain remaining owners, local catches and consumed recovery through normal/throw retirement. First C retirement with one REF/object remainder preserves local catch, the computed-return Notice and a detached caller cell. Bounded WeakMap slots preserve value/reference-cell ownership, Key notification order, explicit entry removal and occupied replacement with detached aliases and deferred results. Finite by-value/by-reference traversal keeps weak cursor history, retains Map DATA or an owned InternalIterator through iteration, and preserves copied targets or escaped aliases across teardown. Bounded manual cursor methods retain standalone current copies through end, rewind and Key death. Conditional GC supports canonical reference/array backedges and copy/COW protection, transitive entry-Key protection with selective multi-entry normalization, and bounded Map/Value cycles with an independently live Key. [WeakMap review](coverage/semantics/weak-map-review.json). The finite `returns_verify` work is complete; wider PHP return and lifetime coverage remains open. [Return contract](docs/semantics/SOURCE-REFERENCE-RETURNS.md), [eager cleanup](docs/semantics/SOURCE-EAGER-DESTRUCTORS.md), [return review](coverage/semantics/reference-return-local-cv-lifetime-review.json). |
| Diagnostics and environment | Supported warning/exception handlers retain raw registration, selected callback and emitting frame. Request facts, inclusion and lifecycle effects stay explicit. [Handlers](docs/semantics/SOURCE-ERROR-HANDLERS.md), [exception handlers](docs/semantics/SOURCE-EXCEPTION-HANDLERS.md), [request inputs](docs/semantics/REQUEST-INPUTS.md). |

## Active and unintegrated work

| Track | Owner-confirmed current work |
| --- | --- |
| A52 | Iterator literal spread. |
| COMP122 | Descendant ALIAS graphs. |
| V105 | Captured ARRAY-name TypeErrors. |
| Iterator54 | Helper-frame Fiber transfer. |
| M152 | Multi-entry manual WeakMap cursor. |
| OP87 | Returned Stringable concatenation. |
| Source91 | Aggregate→Generator CONFIG. |

Iterator49/50/51/52/53, V99/V100/V101/V102/V103/V104, M132/M133/M134/M135/M136/M137/M138/M139/M140/M141/M142/M143/M144/M145/M146/M147/M148/M149/M150/M151, A46/A47/A48/A49/A50/A51, OP79/80/81/82/83/84/85/86, Source86/87/88/89/90, COMP118/119/120/121 and CLASS119/120/121/122/123/124 are integrated
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
  initialized user Iterators, their bounded Aggregate producer, fresh named Generators and the empty/singleton WeakMap slice.
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
