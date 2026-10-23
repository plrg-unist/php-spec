# Core PHP semantics progress

Target: **PHP 8.5.10 CLI, NTS, signed 64-bit integers**. [PLAN](PLAN.md) defines
complete core; the [inventory](coverage/semantics/features.json) tracks the 169
syntax constructors and 306 runtime obligations. The executable core remains
partial. Syntax acceptance and selected agreement do not establish full semantics
or BOLA freedom. [CORE](docs/semantics/CORE.md) defines the intrinsic boundary.

## Current checkpoint

Unused zero-argument CURRENT now drops its snapshot before receiver cleanup
when the selected ancestor is still pending at a pre-refreshed primitive COMPLETE.
CURRENT preserves both bits. Independently initialized Middle releases the old
row inside its finally; assignment retains that copy until caller drop. Normal
and throwing object-slot cleanup occurs inside Middle finally before Upper K;
a separate global Exception does not become Previous.

Native4 and the genuine checked NORMAL timing disagreement retain `b7f96b717`/409:
model J/J-END/K/A versus native J/A/J-END/K, with raw recordfalse/agreement0.
Source4/strict409 pass at `c7aa278da`; gate4 and 581 focused premises
(307 author +274 independent; 561 local +20 generic) pass at `cc849531f`/409.
All affected checks pass first attempt at original caps. Actors are reaped and
CPU5 released; accepted native/source evidence is not replayed.
[Pending CURRENT review](coverage/semantics/generator-pending-unused-current-review.json).

Only two premises in289 are removed. Existing endpoint, update identity,
source-use, discarded tail and plain-result guards remain; no root, close,
scheduler, API or collector change. One old48 helper counter now expects NULL
without renewing historical credit. Child prefixes, deeper/owning/parked or wider
endpoints and collection remain partial. Publication is independently reviewed.

Composed over `30fd9927fa`/409 with tested289 and seven maintained test
inputs preserved. Incoming156/270 and all other production/shared harness paths
stay parent-exact. Getter recursion, constant queries, pooled NULL-key arrays,
NaN bool casts and ordinary typed-reference retirement selectors have no producer
here; original source/state cuts retain their credit without joined execution.

## Integrated behavior and entrypoints

Each family is bounded; its linked contract and inventory entries retain the
implemented cases, exclusions, exact tested revisions and independent reviews.

| Family | Current behavior and scope pointers |
| --- | --- |
| Source and compilation | Checked ASTs retain source occurrences, ordered publication, compilation phases and diagnostic priority. Dynamic source and request inputs have explicit provider boundaries. [Compiler](docs/semantics/SOURCE-COMPILER.md), [context](docs/semantics/SOURCE-CONTEXT.md), [dynamic source](docs/semantics/DYNAMIC-SOURCE.md). |
| Operators and warning decisions | Arithmetic/casts distinguish saved values from live CVs and stage supported diagnostics through callbacks. Direct NaN Boolean NOT produces stricttrue after a live0.0 write; copied fractional BITNOT retains its saved integer. [Operators](docs/semantics/ORDINARY-OPERATORS.md), [truth callbacks](docs/semantics/SOURCE-WARNING-TRUTH.md), [numerics](docs/semantics/NUMERICS.md). |
| Comparisons and arrays | Seven missing-CV comparisons admit bounded DIRECT/ALIAS arrays, including ordinary non-Stringable object leaves. Cell replacement, COW and final release preserve distinct owners. NULL-key literals support bounded CV, returned, temporary and pooled CONST values, including nested DIRECT subtrees with physical child edges and handler-time COW. [Nested CONST review](coverage/semantics/array-literal-null-key-constant-subtree-review.json). [Comparisons](docs/semantics/COMPARISONS.md), [dimensions](docs/semantics/DIMENSIONS.md), [object-reference review](coverage/semantics/undefined-comparison-object-reference-array-review.json). |
| Calls and configuration | Ordinary/scoped/captured calls preserve selected targets, argument order, references and genuine callback frames. Two singleton INI_SET packs retain raw NULL/quiet ARRAY, callee and option through later effects. [Calls](docs/semantics/SOURCE-CALLS.md), [include/configuration](docs/semantics/INCLUDE-SOURCES.md), [two-pack review](coverage/semantics/ini-set-two-pack-null-array-value-review.json). |
| Constants and callable values | Bounded DEFINE/CONSTANT/DEFINED preserve source authority, scopes, primitive/array/object snapshots and captured intrinsic Closure identity. Captured Boolean/integer/finite-float queries distinguish strict ordinary reception from weak explicit calls and converted API/raw wrapper arguments. [Constant contract](docs/semantics/SOURCE-USER-CONSTANTS.md), [string-query review](coverage/semantics/constant-owned-query-review.json), [scalar-query review](coverage/semantics/constant-owned-scalar-query-review.json). |
| Classes and properties | Visibility, references, typed writes, hooks, magic access and clone have bounded routes. Same-name implicit getter recursion delivers missing-property Warning/captured NULL and resets its guard before later entry. [Properties](docs/semantics/SOURCE-PROPERTIES.md), [classes](docs/semantics/SOURCE-CLASSES.md), [recursion review](coverage/semantics/magic-get-recursion-review.json). |
| Generators and Fibers | Supported suspension, delegation and cleanup preserve snapshots and initialization history. Unused CURRENT also retires its snapshot before a still-pending selected receiver, preserving both bits and live Middle-finally cleanup. [Pending CURRENT review](coverage/semantics/generator-pending-unused-current-review.json). Direct/one-ancestor node-free SEND handles supplied argument-destructor Exceptions and distinct unused/assigned owners. [Generators](docs/semantics/GENERATORS.md), [delegation](docs/semantics/GENERATOR-DELEGATION.md), [ancestor review](coverage/semantics/generator-ancestor-abrupt-argument-send-review.json). |
| Returns and lifetime | Bounded by-reference return/finally chains retain remaining owners, local catches and consumed recovery through normal/throw retirement. First C retirement with one REF/object remainder preserves local catch, the computed-return Notice and a detached caller cell. The finite `returns_verify` work is complete; wider PHP return and lifetime coverage remains open. [Return contract](docs/semantics/SOURCE-REFERENCE-RETURNS.md), [eager cleanup](docs/semantics/SOURCE-EAGER-DESTRUCTORS.md), [return review](coverage/semantics/reference-return-local-cv-lifetime-review.json). |
| Diagnostics and environment | Supported warning/exception handlers retain raw registration, selected callback and emitting frame. Request facts, inclusion and lifecycle effects stay explicit. [Handlers](docs/semantics/SOURCE-ERROR-HANDLERS.md), [exception handlers](docs/semantics/SOURCE-EXCEPTION-HANDLERS.md), [request inputs](docs/semantics/REQUEST-INPUTS.md). |

## Active and unintegrated work

Preserve these private branches, original failures and evidence until their
reviewed milestones are integrated. Integration must update this table rather
than retain superseded operational checkpoints.

| Track | Current state |
| --- | --- |
| M134 WeakMap HCELL backedge | Scope agreed; native-first alias-held/unheld packet preparing. |
| Source87 user-Iterator CONFIG unpack | Native6 retained; genuine wrong TypeError has zero credit; implementation pending. |
| COMP119 array-valued ALIAS child COW | First two changed-source cases pass; remaining gate running. |
| CLASS120 declared UNSET `__get` recursion | Changed source4 accepted; focused checks preparing. |
| OP81 `(array)` NaN cast | Native packet preparing. |
| V101 | Scoping after V100 integration. |

Iterator49/50/51, V99/V100, M132/M133, A46/A47, OP79/80, Source86, COMP118 and CLASS119 are integrated
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
