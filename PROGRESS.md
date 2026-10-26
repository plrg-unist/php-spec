# Core PHP semantics progress

Target: **PHP 8.5.10 CLI, NTS, signed 64-bit integers**. [PLAN](PLAN.md) defines
complete core; the [inventory](coverage/semantics/features.json) tracks the 169
syntax constructors and 306 runtime obligations. The executable core remains
partial. Syntax acceptance and selected agreement do not establish full semantics
or BOLA freedom. [CORE](docs/semantics/CORE.md) defines the intrinsic boundary.

## Current checkpoint

Named Generator delegation retains its actual resumers and source claims across
Fiber suspension. Five exact fresh/cached and one-/two-link Throwable sources
agree with PHP through final Generator/object retirement; the retained closure
sources pass at `f3ddab851`/418 with model180/process200 and100000 steps.

All intact whole completions (43/49/43,135 premises) pass at the same cut with
SL240/seek4000/finish4000. Prior gate6/components459 retain `3a551c0f0`/415;
native/genuine/strict/earlier source cuts remain unchanged. Original100s/120s
timeouts and diagnostic0 stay separate. No source, operational rule or assertion
was weakened; the shared fixture budget defaults remain120.
[Delegation transfer review](coverage/semantics/generator-fiber-delegation-transfer-review.json).

## Integrated behavior and entrypoints

Each family is bounded; its linked contract and inventory entries retain the
implemented cases, exclusions, exact tested revisions and independent reviews.

| Family | Current behavior and scope pointers |
| --- | --- |
| Source and compilation | Checked ASTs retain source occurrences, ordered publication, compilation phases and diagnostic priority. Dynamic source and request inputs have explicit provider boundaries. [Compiler](docs/semantics/SOURCE-COMPILER.md), [context](docs/semantics/SOURCE-CONTEXT.md), [dynamic source](docs/semantics/DYNAMIC-SOURCE.md). |
| Operators and warning decisions | Arithmetic/casts distinguish saved values from live CVs and stage supported diagnostics through callbacks. Direct NaN Boolean NOT/Boolean cast produce stricttrue/false after a live0.0 write; NaN array casting constructs a fresh singleton from that live float. Initially-NaN LEFT logical XOR caches post-warning truth across live RIGHT conversion, including remaining default Warning before a LEFT throw unwinds. Retained-reference Boolean NOT keeps its captured inner cell across source unset/rebinding. NaN LEFT short-circuit decisions use post-callback truth to skip or enter RIGHT. NaN shorthand ternary preserves the live selected value after its callback. A LEFT-array Warning may install a same-cell Stringable RHS; real conversion retains its selected receiver through source retargeting. A direct call's acquired RHS keeps a separate temporary owner until retirement before store/catch. Acquired Stringable LEFT now survives through the remaining RHS conversion; borrowed CV timing stays distinct. Copied fractional BITNOT retains its saved integer. [Operators](docs/semantics/ORDINARY-OPERATORS.md), [truth callbacks](docs/semantics/SOURCE-WARNING-TRUTH.md), [numerics](docs/semantics/NUMERICS.md). |
| Comparisons and arrays | Initialized materialized private/protected declared tables preserve numeric Notice cursors, live slots and retained reference cells through normal handlers. [Nonpublic numeric review](coverage/semantics/nonpublic-numeric-comparison-review.json). Seven missing-CV comparisons admit bounded DIRECT/ALIAS arrays, including ordinary non-Stringable object leaves. Finite acyclic DIRECT/ALIAS graphs now admit descendant reference cells, preserving successive singleton unwrapping, shared-cell replacement, deep snapshots and final release. [Reference-graph review](coverage/semantics/undefined-comparison-reference-graph-review.json). [ALIAS DAG review](coverage/semantics/undefined-comparison-alias-direct-dag-review.json). [DIRECT graph review](coverage/semantics/undefined-comparison-direct-array-graph-review.json), [child-array review](coverage/semantics/undefined-comparison-array-payload-review.json). Undefined key variables in array literals resume Warning callbacks with a fixed empty key and live null/bool/int/float CVs; initially owning ordinary ARRAY CVs also preserve acquisition and retarget retention/debt through throw and balanced inverse writes. [Primitive review](coverage/semantics/array-literal-undefined-key-warning-review.json), [ARRAY-CV review](coverage/semantics/array-literal-undefined-key-array-cv-review.json). NULL-key literals support bounded CV, returned, temporary and pooled CONST values. Nested DIRECT TMP graphs preserve shared physical child edges and handler-time COW, cascading unowned runtime descendants while folded siblings remain pooled. [Nested TMP review](coverage/semantics/array-literal-null-key-array-tmp-subtree-review.json), [nested CONST review](coverage/semantics/array-literal-null-key-constant-subtree-review.json). String R-offset callbacks preserve selected old carriers and live primitive cast keys; fixed bounds completion survives source/key unset, with pending-throw default/suppression. [String-read review](coverage/semantics/string-offset-read-warning-review.json). [Comparisons](docs/semantics/COMPARISONS.md), [dimensions](docs/semantics/DIMENSIONS.md), [object-reference review](coverage/semantics/undefined-comparison-object-reference-array-review.json). Initialized user Iterator literal spreads retain raw current references through key before DIRECT copy, with bounded COW and invalid-key/current/key/next cleanup. [Iterator spread review](coverage/semantics/array-iterator-unpack-review.json). Named Generator literal spreads use native resumes, preserve yield cache edges through resumed code/CLOSED, and retire DATA then owning INPUT before transferring or canceling the protected builder. [Generator spread review](coverage/semantics/array-generator-unpack-review.json). |
| Calls and configuration | Ordinary/scoped/captured calls preserve selected targets, argument order, references and genuine callback frames. Closure::call preserves captured direct values and ARRAY-pack histories, canonical positional/named forwarding, defaults and reference-warning order; outer binding errors skip later producers. [Closure contract](docs/semantics/CLOSURE-CALL.md), [argument-list review](coverage/semantics/closure-call-argument-list-review.json). Two singleton INI_SET packs retain raw NULL/quiet ARRAY, callee and option through later effects. Initialized user Iterators stream integer-key/string sends into INI_SET with callback ordering, pre-API retirement and supplied-Exception recovery. Non-generator getIterator producers transfer retained Iterator or fresh named Generator returns into DATA; Generator-method producers preserve a real owned receiver and historical method/source receipt. Fresh named Generator consumers finish native resumes and retire quiet sole DATA before historical API reception. Bounded WeakMaps distinguish empty arity failure from occupied object-key Error before any current copy. [Calls](docs/semantics/SOURCE-CALLS.md), [include/configuration](docs/semantics/INCLUDE-SOURCES.md), [two-pack review](coverage/semantics/ini-set-two-pack-null-array-value-review.json), [Iterator CONFIG review](coverage/semantics/config-iterator-unpack-review.json), [WeakMap CONFIG review](coverage/semantics/config-weakmap-unpack-review.json), [Aggregate CONFIG review](coverage/semantics/config-aggregate-iterator-unpack-review.json), [Generator CONFIG review](coverage/semantics/config-generator-unpack-review.json), [Aggregate→Generator review](coverage/semantics/config-aggregate-generator-unpack-review.json), [sole DATA review](coverage/semantics/config-generator-sole-data-review.json), [method-producer review](coverage/semantics/config-aggregate-generator-method-review.json). |
| Constants and callable values | Bounded DEFINE/CONSTANT/DEFINED preserve source authority, scopes and primitive/array/object snapshots. Captured intrinsic Closures preserve selected callees, strict/weak reception, raw/received traces, COW/reference sharing and callback/destructor cleanup. Singleton ARRAY packs bind positional/named global-string snapshots after source array retirement, constrained by literal facts. [Constant contract](docs/semantics/SOURCE-USER-CONSTANTS.md), [query-pack review](coverage/semantics/constant-owned-query-pack-review.json). |
| Classes and properties | Visibility, references, typed writes, hooks, magic access and clone have bounded routes. Accessible nonpublic UNSET Get retains the caller-selected physical DECL/type across Child scope and backing population. Bounded literal-this Get authenticates receiver identity and preserves saved history through callbacks and method retirement. Caller-source declaration selection also wins over public Child shadow across the existing producers, with fresh actual-access agreement. Named noarg owned factories also admit bounded BYVAL nonpublic/denied Get while preserving COPY/BASE retirement. CV reference getters share saved-declaration verification, preserve existing type sources and attach no target constraint. Bounded same-name recursion distinguishes captured NULL, typed Error and visibility Error; real guards survive local cleanup. [Properties](docs/semantics/SOURCE-PROPERTIES.md), [classes](docs/semantics/SOURCE-CLASSES.md), [recursion review](coverage/semantics/magic-get-recursion-review.json), [declared-UNSET review](coverage/semantics/magic-get-unset-recursion-review.json), [typed reentry review](coverage/semantics/magic-get-recursive-error-review.json), [denied reentry review](coverage/semantics/magic-get-denied-recursion-review.json), [scoped getter review](coverage/semantics/magic-get-scoped-unset-review.json), [literal-this review](coverage/semantics/magic-get-direct-this-review.json), [selected-declaration review](coverage/semantics/magic-get-lexical-selection-review.json), [owned-access review](coverage/semantics/magic-get-owned-access-review.json), [scoped-reference review](coverage/semantics/magic-get-scoped-reference-review.json). |
| Generators and Fibers | Direct named bodies entered by CURRENT/NEXT preserve their authentic resumer across Fiber suspension and supplied-Throwable injection, with distinct fresh/cached reentry Errors. Ordinary named helpers retain their real caller frames, parameter owners and unique underlying resumer. [Helper-frame review](coverage/semantics/generator-fiber-helper-transfer-review.json). [Transfer review](coverage/semantics/generator-fiber-transfer-review.json). Shared delegation, initialization history, unused snapshots and abrupt SEND cleanup retain their bounded contracts. [Generators](docs/semantics/GENERATORS.md), [Fibers](docs/semantics/FIBERS.md), [delegation](docs/semantics/GENERATOR-DELEGATION.md), [refresh review](coverage/semantics/generator-refresh-unused-current-review.json). Named native delegation preserves actual resumer/claim chains across Fiber transfer. Five exact fresh/cached and Throwable sources,459 component/short-budget and135 whole-completion premises pass; earlier timeouts remain separate. [Delegation transfer review](coverage/semantics/generator-fiber-delegation-transfer-review.json). |
| Returns and lifetime | Bounded by-reference return/finally chains retain remaining owners, local catches and consumed recovery through normal/throw retirement. First C retirement with one REF/object remainder preserves local catch, the computed-return Notice and a detached caller cell. Bounded WeakMap slots preserve Value/reference-cell ownership, Key notification and selective mutation. Finite traversal, owned Iterator DATA and manual weak-Key cursors preserve copied targets, escaped aliases, normalization and staged cleanup. Last-owner Map teardown with multiple entries preserves actual Map/self weak gets, borrowed occupancy for bounded `isset` reentry and pending Exceptions. Conditional GC supports canonical reference/array backedges and copy/COW protection, transitive entry-Key protection with selective multi-entry normalization, and bounded Map/Value cycles with an independently live Key. [WeakMap review](coverage/semantics/weak-map-review.json). The finite `returns_verify` work is complete; wider PHP return and lifetime coverage remains open. [Return contract](docs/semantics/SOURCE-REFERENCE-RETURNS.md), [eager cleanup](docs/semantics/SOURCE-EAGER-DESTRUCTORS.md), [return review](coverage/semantics/reference-return-local-cv-lifetime-review.json). |
| Diagnostics and environment | Supported warning/exception handlers retain raw registration, selected callback and emitting frame. Request facts, inclusion and lifecycle effects stay explicit. [Handlers](docs/semantics/SOURCE-ERROR-HANDLERS.md), [exception handlers](docs/semantics/SOURCE-EXCEPTION-HANDLERS.md), [request inputs](docs/semantics/REQUEST-INPUTS.md). |

## Active and unintegrated work

| Track | Owner-confirmed current work |
| --- | --- |
| Source94 | Strict/source3/entry45 accepted; corrected completion and remaining state packet frozen after preserved fixture syntax failure. |
| COMP125 | Declared-UNDEF source6 closed; focused390 plus affected63 prefix freezing. COMP123 held work stays separate. |
| CLASS128 | Owned nonpublic/public-shadow/denied BYREF Get source5 accepted at `d19042042`/417; author live-reference/conflict fixtures preparing, peer262 ready. |
| COMP123 | Held unrun; no actor. |

Iterator49/50/51/52/53/54/55, V99/V100/V101/V102/V103/V104/V105/V106/V107/V108, M132–M154, A46/A47/A48/A49/A50/A51/A52/A53, OP79/80/81/82/83/84/85/86/87/88, Source86/87/88/89/90/91/92/93, COMP118/119/120/121/122/124 and CLASS119/120/121/122/123/124/125/126/127 are integrated
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
