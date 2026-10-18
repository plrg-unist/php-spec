# Core PHP semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit. [PLAN.md](PLAN.md) defines complete core;
[the inventory](coverage/semantics/features.json) tracks obligations. Selected
agreement does not establish complete semantics. Large evidence stays outside
Git; [ARTIFACTS.md](docs/ARTIFACTS.md) locates it.

## Current checkpoint

Pending Generator `throw` now reaches the caller without body entry when a
delegating actual root still has pending initialization and native links end
at a bare yield, or at a detached current with a nonowning copied return.
Its current copy survives receiver close and then retires before catch as a
no-GC temporary, preserving a destructor replacement's previous chain.
Nonowning parked-source history keeps getters live and omits that physical
frame's finally on explicit close even after initialization clears.
Four exact normal originals agree across retained `e349`/`9d517` cuts. Four
genuine fronts pass428 premises (208 author +220 independent) and the same
four full endings at `d01b2715d`/399; strict399 passes. Real snapshot/TEMP
owners, retired-Generator destructor receipts, reference frame jobs, detached
COMPLETE23, public admission and budgets are covered. Initial preparation
and one revised-fixture elab grant0 credit; no compiler or state actor failed.
The original mixed source packet retains firstPASS1/secondFAIL0: sole-receiver
cache destruction preceded middle finally because Throwable adaptation erased
the current copy. Only the failed wrapper repeated; later state fronts expose
that copy and the separately corrected detached route hidden by retained aliases.
Native4/unchanged baseline remain0. Later real resume after parked throw,
used-yield buffers, owning suspended temporaries and wider exception-opline
history remain explicit open scope. See the
[pending-throw ledger](coverage/semantics/generator-pending-throw-review.json).

Composed over `f42dcd6c5`/400 after pointwise review of the incoming
NaN/empty-array DEFINE, nullable-array return cleanup, class/WeakMap, quiet
numeric, property-empty and LIST selectors, all absent from these originals.
A12's new list-key module and parent task tags are preserved; only the tested
Generator field/task additions compose into shared Module30. Source4/state428
retain their private cuts with no joined actor or renewed execution credit.

Distinct authenticated SensitiveParameterValue constructor Closures now compare
equal when they select the same live receiver, including clones and fresh capture
sites. Distinct receivers remain uncomparable +1 both ways even when wrapping the
same Map; getter/constructor mismatch and strict identity stay separate. The
unchanged baseline completed normally with the wrong equality tuple. Two originals
and 448 Boolean premises (434 setup + 14 pure)/10 actual comparison steps pass at
27032c3bb/399. Arrays continue past equal captures to signed integer tails;
declared-property scans stop before later casters for distinct receivers. Whole
states preserve receiver/Map/private-value/key ownership, scopes and budgets. Later
explicit calls expose the existing readonly Error. No actor failed; native/baseline/
preparation/EL retain zero credit. Other Closure representations, constructor bases
and wider lifetimes remain partial; carrier, factory-clone and uninitialized-wrapper
gaps stay separate.
[Constructor-pair review](coverage/semantics/constructor-closure-comparison-review.json).

Composed over 694afed07/399 after pointwise review of guarded NaN/empty-array
constant duplicates, magic-empty, nullable-array destructor-return, numeric-string
compound and LIST selectors, all absent here. Source2/state448 retain their private
cut; no joined actor or renewed execution credit.

Weak NaN `define` names with primitive candidates and omitted/bool-false flags
now preserve full `NAN` rendering/allocation before the first string-conversion
Warning. Its callback/API trace sees raw NaN; normal return
then emits the protected duplicate Warning with the converted name despite live
precision changes. Default delivery returns false without a user NAN row; either
phase can throw the same supplied Exception while keeping callback effects and the
unassigned caller result. Two module30 alternatives and83 module400 insertions keep
the old strict/low-precision routes, scalar NaN refusals and shared numeric/string/
error rules unchanged. Four originals agree at317d31b62; all451 public premises pass:
author105+157+58 and independent131 across default, captured second-throw, strict
and runtime-NaN first-throw groups. Actual raw/converted API traces, saved14/live1,
preallocated carrier, sameException/caller99/siblings, full restored discards,
source/bit/carrier/phase/bounds refusals and budgets pass. No actor failed or repeated.
Initial native/baseline usedCPU3 atce75c4d07; later source/state usedCPU5. Baseline
Unsupported afterB| retains its single PHP conversion Warning and0 credit; accepted
literal PHPstderr has two Warnings, captured/strict/peer are quiet. Truncated N/NA
callback protocols, other flags and wider candidates remain partial.
[NaN-name review](coverage/semantics/define-nan-name-review.json).

Pointwise composition over 1ec88d68f preserves the incoming 399-module parent.
Modules30/400 and four tests are private-exact; incoming return, magic-property,
WeakMap, LIST and compound-operator selectors are disjoint. Source4/public451 retain
their private cut with no joined actor or renewed execution credit.

Complete quiet numeric strings now convert after the first callback in the
both-fractional plain-CV modulo/shift/numeric-bitwise routes. Cached LEFT `12` with
numeric `5` stores `2`/`384`/`0`/`4`/`13`/`9`, preserving RHS string identity and
detaching alias `99`. Real concat carrier `"05"` and whitespace/exponent text are
covered. Supplied throw preserves its Exception/destination/alias; independent
default-first `"-1"` XOR stores `-13`, but negative shift and `"0"` modulo raise
ArithmeticError/DivisionByZeroError at RHS line 25 before store/detachment.
Ten originals agree at 43865027d; 130/109/109 plus independent 153/153/153 SL premises pass 807 at
668e39707/399, covering actual handlers, carrier metadata, cells/owners and budgets.
One guarded string snapshot, five rules and three boundary exclusions; old helpers,
source guards, tags/schema and other routes stay exact. All 15 rows remain partial;
controls and earlier renewed credit zero, OP12 paused.
[Quiet string ledger](coverage/semantics/quiet-string-review.json).

Composed over b4661142f/399 after pointwise review of typed-return array
cleanup, DEFINE flags/INF, SensitiveParameterValue/WeakMap comparison, literal-list
and private-member empty/getter selectors. Source10/state807 retain private cuts
without actor, replay or renewed credit.

Terminal inherited private-property `empty` now skips an untyped public
by-value `__get` when `__isset` is absent. It authenticates the external CV/literal
site and completes true without manufacturing a receiver owner. Later ordinary
reads still run the real getter and preserve its return or same Exception at catch.
Two originals agree at `7f348182d`; 235 focused premises at `d82965600`
(201 reached +34 derived) cover borrowed preparation, public false bypass,
actual Get/catch, source/consumer and
live-dynamic-slot refusals, and budgets. A clean-collection prefix preserves the
GC buffer and one receiver owner through private empty. The original Unsupported
source and locating GC mismatch retain zero credit; the intermediate stream-only
cut is superseded. Native CPU4 masks were observed for both short cases, with
empty argv at exit qualified. No generic GC, ownership, return or quiet-read rule
is relaxed. Other quiet-CV GC paths, terminal isset/coalesce and mutable-empty
array retirement remain open. [Getter-only empty review](coverage/semantics/magic-empty-get-only-review.json).
Earlier class cuts retain their identities without replay.

Composed over `816e1c57d` after pointwise review of unrelated selectors.
Both originals and the 235 focused premises retain their tested revisions;
no joined actor or renewed execution credit.

WeakMap comparisons now admit initialized SENSITIVEVALUE wrappers and exact
SensitiveParameterValue CTORCLOSURE captures as uncomparable +1 both ways, before
wrapped-value or receiver traversal. Both real producers precede the unchanged
baseline. Two originals and 264 Boolean premises (252 setup + 12 pure)/8 actual
comparison steps pass at 5207218f5/399. All seven operators, a wrapped Map snapshot,
cloned constructor ownership after wrapper array/CV removal, private/key owners,
quiet aggregate tails and budgets are covered. Later calls confirm getValue
identity and the existing readonly constructor Error. No actor failed; native/
baseline/preparation/EL retain zero credit. Uninitialized wrappers, other constructor
bases, special intrinsic captures and wider lifetimes remain partial; carrier and
factory-clone gaps stay separate.
[Sensitive wrapper/capture review](coverage/semantics/weakmap-sensitive-comparison-review.json).

Composed over 08ef06924/399 after pointwise review of nullable-array abrupt
return, infinite/array define names and quiet compound RHS selectors, all absent
here. Source2/state264 retain their private cut; no joined actor or renewed
execution credit.

At profile precision14, positive infinite float `define` names now reach the
protected `INF` duplicate Warning/false path with primitive candidates and
omitted/bool-false flags. Two module400 predicates reuse the existing received
name/precision/prefix marker;
source/capture/carrier guards, conversion, strict errors and trace/discard code
stay exact. Four originals agree at83478a404. All529 public premises pass at33743f57f:
author205+124+61 and independent139, covering two default duplicates, fresh `-INF`,
captured raw false/request candidate through callback writes, converted API names,
strict NaN priority, saved14/live1 precision, same Exception/caller99/sibling919,
full restored discard, refusals and budgets. The first state fixture incorrectly
assumed precision1 preserves `INF`; pinned `zend_gcvt` and existing numeric rules
truncate it to `I`. That failure and the unchanged Unsupported baseline retain0;
only affected state fixtures repeated, with source4 kept at its original cut.
Initial native/baseline usedCPU4; later source/state usedCPU1. Expected PHP stderr
has two literal duplicate Warnings and one false-handler Warning; strict/peer are
quiet. Nonbool nonfinite flags and wider candidates remain open.
[Infinite-name review](coverage/semantics/define-nonfinite-name-review.json).

Pointwise composition over 464c0cf26 preserves the incoming 399-module parent.
V67 string-name/array duplicates use a separate marker; new Generator, WeakMap,
LIST and compound-operator selectors do not match these scalar calls. Source4 and
public529 retain their private cuts, with no joined actor or renewed credit.

Bool/null RHS values now convert quietly after the first warning in the
both-fractional plain-CV modulo/shift/numeric-bitwise routes. With cached LEFT `12`,
`true` stores `0`/`24`/`6`/`0`/`13`/`13`; false/null modulo raises DivisionByZeroError
at RHS line 25 before store/detachment. Success detaches alias `99`; supplied throw
preserves its Exception, destination `100` and alias write-through. Independent
default-first null XOR stores `12` despite current `99`, contrasting null modulo's
preserved alias. Ten originals agree at 6cd72d022; 304 SL premises at 63738bb2f plus
384 at 2db904217/399 cover actual handler frames, RHS guards, result cells/error
owners, aliases and budgets. The original fixture binding failure stays zero;
only the corrected branch and previously unrun peers then execute. One shared safe snapshot, four
rules and three boundary exclusions; no initial/tag/schema change. All 14 rows
stay partial; controls and earlier renewed credit zero, OP12 paused.
[Quiet scalar ledger](coverage/semantics/quiet-scalar-review.json).

Composed over f64f2639d/399 after pointwise review of typed-return cleanup,
DEFINE array/special-name duplicates, property isset/empty, recursive list and
WeakMap/Closure selectors, plus buffered Generator throw disposal. Source10 and state304+384
retain private cuts without actor, replay or renewed credit.

Non-pending Generator `throw` now releases a paused child's buffered simple-CV
yield result before catch search, directly or through finite native links. The
no-GC temporary decrement preserves independent cache/orphan owners; payload
destruction can replace the injected Exception with its previous chain intact.
Four exact normal originals agree at `46f1d6208`/399. Five genuine fronts pass
509 premises (267 author + 242 independent), including real slot/release/search
steps, COW/cache aliases, pending/receipt refusals and public validity inside the
payload destructor. Strict399 passes; fixture elaboration adds no semantic credit.
The main435 retain `46f1`, and the separate callback74 uses test-only `d5a499c3e`.
Two pre-application compiler failures remain zero credit; only affected checks
were retried. Native4 and unchanged Unsupported retain `6d377` and zero agreement;
no source/state actor failed or was replayed. Pending/global-opline `throw`, acquired
producers, other result shapes and wider lifecycle remain partial. No engine bug
or intentional divergence is claimed. See the [buffered-throw review](coverage/semantics/generator-buffered-throw-review.json).

Composed over `fcf554d6b`/399 after pointwise review of nullable-array return
cleanup, constant snapshots, magic-empty/list, bitwise and WeakMap/Closure
selectors. Only modules280/289/301 change; every other parent runtime file,
task layout, pipeline and manifest is preserved. Source4/state509/strict
retain their private cuts; no joined actor or renewed execution credit.

WeakMap comparisons now admit normalized GETTERCLOSURE and FROMCALLABLEFACTORY
objects as uncomparable +1 in either direction before receiver, method, source or
private-entry traversal. Both producers precede the genuine unchanged baseline.
Two exact originals and 353 Boolean premises (339 setup + 14 pure)/10 actual
steps pass at edc6f81dd/399. All seven operators, builtin/inherited getters, cold
caches, trace/Map edges, sole cloned-getter receiver ownership, quiet aggregate
tails and budgets are covered. Source endings invoke real getters and the factory.
One pre-main fixture-type failure remains zero; native/baseline/preparation/EL
retain zero credit. Other producers, constructor/special intrinsic captures and
wider weak lifetimes remain partial; stored-string carrier conversion is separate.
[Getter/factory review](coverage/semantics/weakmap-getter-factory-comparison-review.json).

Composed over 2e75ac2d1/399 after pointwise review of guarded array-constant,
isset-only empty, nullable-array abrupt-return and nested-list selectors, all
absent here. Source2/state353 retain their private cut; no joined actor or renewed
execution credit.

WeakMap comparisons now admit ordinary eligible INTRINSICCLOSURE and normalized
FIBERAPICLOSURE objects as uncomparable +1 in either direction before callable,
capture, VM or private-entry traversal. Two exact originals and 279 Boolean
premises (266 setup + 13 pure)/8 actual steps pass at 8ce9bd0e2/399. All seven
operators, unchanged GC-enabled observations, a sole cold Fiber owner, quiet
aggregate tails and budgets are covered. Later explicit calls supply observable
GC flag changes and Fiber execution. Native/baseline/preparation/EL retain zero
credit; no actor failed. Special intrinsic kinds, other producers and wider weak
lifetimes remain partial; no new INI, collection or ephemeron semantics is claimed.
Stored-string carrier conversion stays separate.
[Intrinsic/API review](coverage/semantics/weakmap-api-comparison-review.json).

Composed over 7af29e2c6/399 after pointwise review of special-name/array constants,
magic-empty array RV, quiet-CV list keys, bitwise assignment and abrupt-return
selectors, all absent here. Source2/state279 retain their private cut; no joined
actor or renewed execution credit.

Duplicate `define` now recognizes non-NUL `true`/`false`/`null` string names without
case sensitivity, warning and returning false with primitive candidates and
omitted/bool-false flags. Messages and raw API traces retain the supplied spelling;
returning or throwing handlers preserve all special values without publishing a
user row. Four exact originals agree at 84817642f. All 645 public premises pass:
author 199+162+134 and independent 150 across four source-derived groups, including
actual dispatch/handler/resume/discard, captured false versus live true flags,
strict argument effects, raw request strings, sibling/caller/Exception identity,
case/source/carrier/bounds refusals and budgets. No actor failed or repeated;
the unchanged Unsupported baseline retains zero credit. Runtime widens two name
predicates; two old Source43 protocol files repair obsolete refusals with admission
and stale-message rejection, with fresh equivalents here and no 614 replay. Unknown
startup values, other flags/coercions and owning/wider candidates remain partial.
[Special-name duplicate review](coverage/semantics/define-special-duplicate-review.json).

Pointwise composition over 62c33de71 preserves the incoming 399-module parent.
The array-leaf class delegate is exact for primitives and no source uses an array
candidate; other incoming task/source selectors are disjoint. Source4/public645
and the older 614 campaign retain their cuts, with no joined actor or renewed credit.

Numeric bitwise assignments now quietly convert fitting integral float masks
left by the first handler in the both-fractional plain-CV route. Cached LEFT 12
with live `5.0` directly stores 4/13/9 and detaches alias 99; supplied throw keeps
the same Exception, destination 100 and alias write-through. An independent handler
returning false leaves `-1.0`: XOR stores (-13) despite live LEFT 99, with one default
LEFT Deprecated at line 25, no second callback and alias detachment. Five exact originals pass at
7724196ca; author 135/135/135/99 plus independent 130 SL premises pass 634 at
1332b0f1c/399, covering actual first frames, original bindings, atomic storage,
cells/owners and budgets. Runtime adds one direct commit and a boundary exclusion,
reusing the exact integral snapshot; tasks/schema and other routes stay unchanged.
Native/baseline/prep/syntax and earlier renewed credit stay 0. Wider forms remain
partial; OP12 paused.
[Quiet float bitwise ledger](coverage/semantics/bitassign-quiet-float-review.json).

Composed over 73f140047/399 after pointwise review of startup/array constants,
magic-empty array RV, quiet-CV list keys and WeakMap/Closure seams. Source5/state634
retain private cuts without actor, replay or renewed credit.

WeakMap comparisons now admit normalized FROMCALLABLECLOSURE and BOUNDFAKECLOSURE
objects as uncomparable +1 in either direction before factory/binding metadata or
private-entry traversal. Two exact originals and 361 Boolean premises
(349 setup + 12 pure)/8 actual steps pass at 8504d9800/399. All seven operators, distinct bound
receiver markers, cloned rebinding on an overriding child, retired nonowning history,
sole receiver owners, skipped aggregate tails and budgets are covered. Native/
baseline/preparation/EL retain zero credit; no actor failed. Other Closure forms,
producers and wider weak lifetimes remain partial; stored-string carrier conversion
is separate. [Factory/binding review](coverage/semantics/weakmap-factory-comparison-review.json).

Composed over 180baaf665/399 after pointwise review of startup-constant duplicate
traces, magic-empty, Generator send, shifts and abrupt-return selectors, all absent
here. Source2/state361 retain their private cut; no joined actor or renewed credit.

Duplicate `define` of known fixed startup primitives now warns and returns false
without changing the builtin or publishing a user row. Omitted/bool-false flags and
primitive candidates cover ordinary/strict calls, argument effects, returning
handlers and supplied throws. Four exact originals agree at b55e4edaf. All 614
public premises pass across four groups: retained literal199 at f9a7e2cb9 and
corrected author154+129 plus independent132 at 7891c0df5, including actual dispatch,
raw request-string API traces, sibling/caller effects, full restored discard,
source/carrier/bounds refusals and budgets. A real trace-guard counterexample
corrected projection from handler scope without changing continuation admission;
source4 retains its earlier cut because observed string values are unchanged.
That failed actor, the earlier pre-main syntax failure and unchanged Unsupported
baseline retain zero credit. Only affected state checks repeated. Runtime adds
30 module400 lines; old user-duplicate and ignored-flag domains stay exact.
Unknown startup values, other flags/coercions and owning/wider
candidates remain partial.
[Startup duplicate review](coverage/semantics/define-startup-duplicate-review.json).

Pointwise composition over 6d3771b64 preserves the incoming 399-module parent.
The primitive value-class delegate is exact and GENERATORINPUTS stays empty;
other incoming task/source selectors are disjoint. Source4/literal199/affected415
retain their tested cuts; no joined actor or renewed execution credit.

Shifts now quietly convert fitting integral float counts left by the first
handler in the both-fractional plain-CV route. Cached LEFT (-12) with `2.0` stores
(-48)/(-3) and detaches alias 99 directly. Supplied throw preserves its Exception,
destination 100 and alias write-through. Independent default-first `-1.0` raises
ArithmeticError at line 25 without storage/detachment; `64.0` still stores right-
shift (-1) from the historical sign despite live 99, detaching alias 99. Each has
one LEFT deprecation. Five exact originals pass at 92a56ffcc; author 135/135/99 plus
independent 130/130 SL premises pass 629 at 33bc8b754/399, covering real first frames,
original bindings, atomic commit/error, cells/owners and budgets. Runtime adds two
rules and one boundary exclusion, reusing the exact OP34 snapshot; tasks/schema
and other routes stay unchanged. Native/baseline/prep/syntax and earlier renewed
credit stay 0. Wider forms remain partial; OP12 paused.
[Quiet float shift ledger](coverage/semantics/shiftassign-quiet-float-review.json).

Composed over a43c7a30a/399 after pointwise review of reference-return cleanup,
unused Generator send, stdClass define/property-empty and WeakMap/string-method
Closure seams. Source5/state629 retain private cuts without actor, replay or
renewed credit.


Pending shared Generator `send` now also accepts a bare statement yield with no
native result target. It snapshots current and clears initialization without
advancing or buffering the ignored argument. Argument destruction precedes receiver
cleanup, preserving old reference-row snapshots through live-cache COW and the same
supplied Exception through real child/middle close. Four exact normal originals
and four reached state groups/363 premises (167 author +196 independent, including
20 generic reachability premises) pass at `dcc8f917d`/399. Real API/OP_EXIT/queued
close steps, physical owners, source/tail refusals and budget resume are covered.
Strict399 passes; the four-fixture elaboration gate adds no semantic credit.
No actor failed or was retried. Native4 and the unchanged genuine Unsupported
baseline retain `844f` and zero model credit. Existing used-slot retention stays
unchanged; other expression shapes, pending/buffered `throw`, owning copied returns
and broader lifecycle remain partial. No engine bug or intentional divergence is
claimed. [Unused-target review](coverage/semantics/generator-pending-unused-send-review.json).
Composed over `f4bfc340e`/399 after pointwise review of incoming class-RV,
constant, comparison, list, arithmetic and abrupt-return selectors. Only Generator
modules 280/289 change; all other runtime and the manifest preserve parent bytes.
Source/state/strict retain their private cut; no joined actor or renewed credit.

WeakMap comparisons now admit normalized STRINGMETHODCLOSURE objects from fixed
literal method captures, returning uncomparable +1 in either direction. Two exact
originals and 321 Boolean premises (309 setup + 12 pure)/8 actual steps pass at
79559094c/399. Bound and inherited static operator rows, cloned parent-descriptor
selection on an overriding child, sole receiver ownership, unchanged scope rows,
quiet aggregate tails and budget resume are covered. Native/baseline/preparation/EL
retain zero credit; no actor failed. Stored-string carrier conversion, other Closure
representations and wider weak lifetimes remain partial.
[Literal method-string review](coverage/semantics/weakmap-string-method-comparison-review.json).

Composed over 7994b0e50/399 after pointwise review of magic-empty disposal,
list-key, abrupt-return, integral-modulo and constant-born define selectors, all
absent here. Source2/state321 retain their private cut; no joined actor or renewed credit.

Modulo now quietly converts a fitting integral float RHS left by the first
handler in the both-fractional plain-CV route. Cached LEFT 12 with live `5.0`
stores 2 and detaches alias 99 in one production step; supplied throw preserves the
same Exception, destination 100 and alias write-through. Independent default-first
`-0.0` raises DivisionByZeroError at line 25 without storage or detachment, after
exactly one LEFT deprecation. Three exact originals pass at edb2bf2a2; author
135/99 plus independent 130 SL premises pass 364 at f9f677e78/399, covering real
frames, original bindings, result/error cells and owners, and budgets. Only module404
gains 25 lines plus a boundary exclusion; tasks/schema and other routes stay unchanged.
Native/baseline/checked prep/syntax and earlier renewed credit stay 0. Wider initial
forms, RHS conversions, unsafe targets and lifecycle remain partial; OP12 paused.
[Quiet float modulo ledger](coverage/semantics/modassign-quiet-float-review.json).

Composed over 13313e206/399 after pointwise review of Generator buffered inputs,
integer-CV list warnings, object-RV empty cleanup, Throwable returns and define/
WeakMap seams. The new owner channel stays empty; source3/state364 retain private
cuts without actor, replay or renewed credit.

WeakMap comparisons now admit normalized direct-method and callable-array method
Closures, returning uncomparable +1 in either direction before receiver/capture or
private-entry traversal. Three exact originals and 266 Boolean premises
(254 setup + 12 pure)/8 actual steps pass at 623149672/399. All seven operators,
real aggregate frames, receiver-only capture owners, scope rows, quiet later tails and budget
resume are covered. Two earlier source failures and the split STRING producer
failure retain zero credit; the bounded diagnostic and prelaunch provisioning add
none. That retained cut covers two representations; other producers and wider
weak lifetimes remain partial. [Method-Closure review](coverage/semantics/weakmap-method-comparison-review.json).

Composed over af38e86d0/399 after pointwise review of constant arguments, define,
property/list, abrupt-return and Generator-input seams. GENERATORINPUTS stays empty
for these non-generator sources, adding no roots or validity restriction. Source3/
state266 retain their private cut; no joined actor or renewed execution credit.

Pending shared Generator `send` now fills a paused child's used yield assigned
directly to a simple CV, through finite native Generator links, without advancing.
A direct or forwarded `next` that resumes the child transfers its one payload
owner. Close and overwrite preserve the pinned engine's untraced count through
real finally/cache cleanup until request-store destruction, independently of
Generator and receiver owners. Reference-row snapshots and COW stay separate.
Six exact normal originals agree: three author cases at `2b9ceced5` and three
independent cases at `3bc9dcbf6`. Five genuine state groups pass 470 premises
(255 author + 215 independent), including
actual API/forwarded/close/store steps, immutable-source and continuation refusals,
physical owners and budget resume. Strict checking of 399 modules passes at `2b9`;
the combined five-fixture
elaboration gate adds no semantic credit. Two DSL/application failures and two
observer failures remain zero credit; only affected checks were retried.
Six native captures and the unchanged Unsupported baseline retain `845` and zero
model credit.
Pending/active-buffered `throw`, other used-expression shapes, owning copied
returns and broader GC/callback/Fiber lifetimes remain partial. No engine bug or
intentional divergence is claimed.
[Shared-send review](coverage/semantics/generator-pending-shared-send-review.json).

Pointwise composition over `6d2b2fdef` preserves the incoming retained-constant
fields, roots and defaults in modules 30/39/40 alongside the new Generator input
field. The other four Generator runtime files keep the tested bytes; all other
runtime, pipeline and the 399-module manifest retain parent bytes.
Source/state/strict evidence keeps its private cuts; no joined actor or renewed
execution credit.

Finite float `define` names now accept quiet false scalar flags with primitive
values. Weak calls keep distinct `"-0"`/`"0"` keys and raw captured flags; duplicate
handlers retain the received key and call-time precision despite later writes.
Strict parameter-1 errors precede nonbool flag rejection after argument effects.
Four exact originals agree at 9fb6cdf4, with one expected default duplicate Warning.
All 603 public premises pass: author 274+80+108 and independent 141 across four
groups, including actual publication/duplicate/strict/discard steps, saved precision
14 versus live 1, old binding/sibling/caller effects, carrier/source/name refusals
and budgets. The unchanged Unsupported baseline retains zero credit; no actor failed
or was repeated. Runtime adds four module400 lines. Two obsolete float-shape
refusals now check shape admission plus immutable source or received-name authority;
their equivalents are exercised here without replaying the old 595 campaign.
Nonfinite names with these flags, truthy/NULL/NaN flags and owning/wider forms remain
partial. [Float false-flag review](coverage/semantics/define-float-false-flag-review.json).

Pointwise composition over 06f381e75 preserves the incoming 399-module parent.
Source4/state603 and the older 595 campaign retain their tested cuts; the incoming
empty REJECTED field and other selectors are conservative here, so no joined actor
or renewed execution credit is warranted.

Both-fractional plain-CV numeric `&=`/`|=`/`^=` now order both conversion
deprecations. LEFT 12 survives the first callback, then live 5.5 becomes cached 5
before the second; later 88/10 still stores 4/13/9 and detaches alias 88. Quiet
integer RHS 5 after the first callback skips the second diagnostic and reaches the
unchanged OR commit, detaching alias 99. First/second supplied throws preserve the
same Exception, callback effects, destination 100 and alias write-through.
Independent negative RHS (-1) from -1.5 still stores XOR (-13) after the second
default Deprecated at line 25 despite live 88/10, detaching alias 88.
Seven exact originals pass at 37d32f153; author 231/231/231/148/215/184 plus
independent 181 SL premises pass 1421 at 2858f5b35/399. All three AST/OP pairs,
fresh first-LEFT/second-RHS guards, actual entered frames, quiet handoff, cells/
owners and budgets are covered; LEFT stays historical at second capture. Native/
baseline/retained checked prep/syntax retain 0. Initial references/copies, wider
RHS conversions, unsafe bindings/targets and wider callbacks/lifecycle remain
partial; pure projections establish refusals only.
[Ordered bitwise ledger](coverage/semantics/bitassign-both-warning-review.json).
OP12 stays paused; earlier accepted operator cuts retain 0 renewed credit.

Composed over bbcfe62e5/399 after pointwise review of rejected constant owners,
NaN property empty, typed reference-return cleanup and define/list seams. The new
owner channel stays empty; source7/state1421 retain private cuts without actor,
replay or renewed credit.

NULL `define` names now receive quiet false nonbool flags with primitive values.
The first deprecation keeps raw NULL and captured flags; normal return converts
only the name, checks the live empty-key binding and can issue a separate duplicate
Warning. Strict parameter-1 errors precede flag rejection after argument effects;
a first-handler throw preserves the same Exception/callback effects without
registering the empty key. Four exact originals agree across retained tested cuts.
All 755 public premises pass: author 334+116+179 and independent 126 across four
groups, covering actual dispatch/return/duplicate/discard, raw versus converted API
views, carrier/source refusals and budgets. The original captured-source timeout,
pre-main fixture binding failure and unchanged Unsupported baseline retain zero
credit; only affected checks were repeated. Runtime adds four module400 lines,
reusing the old NULL-name pipeline with a bounded marker-domain extension.
Nonfinite float names with these flags, other coerced flags with NULL/scalar names and
owning/wider forms remain partial.
[NULL-name false-flag review](coverage/semantics/define-null-name-false-flag-review.json).

Pointwise composition over ee63167a1 preserves the incoming 399-module parent.
Source4/state755 retain their distinct private cuts; shared task/source selectors
are disjoint, so no joined actor or renewed execution credit is warranted.

Both-fractional plain-CV `<<=`/`>>=` now order both conversion deprecations.
LEFT (-12) survives the first callback, then live 2.5 becomes cached count 2 before
the second; later 88/1 still stores (-48)/(-3) and detaches alias 88. A quiet count 2
after the first callback skips the second diagnostic and reaches the unchanged
shift commit, detaching alias 99. First/second supplied throws preserve the same
Exception, callback effects, destination 100 and alias write-through. Independent
cached (-1) from -1.5 still raises ArithmeticError at line 25 after the second default
Deprecated despite live count 2, without storage or detachment.
Six exact originals pass at e9144f0d7; author 227/227/144/211/180 plus independent 183
SL premises pass 1172 at 01ce8b03b/399. Both AST/OP pairs, fresh first-LEFT/second-count
guards, actual entered frames, quiet handoff, real cells/owners and budgets are
covered; LEFT stays historical at second capture. Native/baseline/retained checked
prep/syntax retain 0. Initial references/copies, wider count conversions, unsafe
bindings/targets and wider callbacks/lifecycle remain partial; pure projections
establish refusals only.
[Ordered shift ledger](coverage/semantics/shiftassign-both-warning-review.json).
OP12 stays paused; earlier accepted operator cuts retain 0 renewed credit.

Composed over 440cf9c2b/399 after pointwise review of abrupt reference returns,
WeakMap comparison/array casts, Generator send, stdClass/define and recursive-list
seams. Source6/state1172 retain private cuts; no joined actor, replay or renewed credit.

Live nonfreeing WeakMap array casts now create fresh mutable empty arrays,
including populated maps, without exporting entries or retaining their key/value.
Two exact originals and 177 Boolean premises (168 setup + 9 pure)/6 actual casts pass
at 243651a80/399. Empty CV/temporary and real function fronts preserve private owner1,
fresh result IDs, actual COW/reference history, key retirement and budget resume.
Native/baseline/preparation/EL retain zero credit; no actor failed. Pure pin/bounds
controls establish refusal only. Freeing casts and wider map producers/lifetimes
remain partial. [Array-cast review](coverage/semantics/weakmap-array-cast-review.json).

Composed over dc87cf01d/399 after pointwise review of abrupt reference returns,
stdClass constant births, define flags, modulo and list dispatch. The two source
agreements and 177 state premises retain their private cut; no joined actor or renewed credit.

Both-fractional plain-CV `%=` now orders the two conversion deprecations. LEFT12
is retained through the first callback, then live RHS5.5 becomes cached5 before
the second; later88/7 still stores2 and detaches alias88. A quiet RHS5 after the
first callback instead skips the second diagnostic and uses the unchanged modulo
commit, leaving alias99 detached. Either supplied throw preserves the same
Exception, callback effects, destination100 and alias write-through. Independent
cached0 from0.5 still raises DivisionByZeroError at line25 after the second default
Deprecated despite liveRHS7, without storage or detachment.
Five exact originals pass at3964e0453; author223/140/207/176 plus independent183 SL
premises pass929 at70a8c13cc/399. Fresh first-LEFT/second-RHS guards, actual entered
frames, quiet handoff, real cells/owners and budgets are covered; LEFT stays
historical at the second capture. Native/baseline/retained checked prep/syntax
retain0. Initial references/copies, wider RHS conversions, unsafe bindings/targets
and wider callbacks/lifecycle remain partial; pure projections establish refusals
only. [Ordered modulo ledger](coverage/semantics/modassign-both-warning-review.json).
OP12 stays paused; earlier accepted operator cuts retain0 renewed credit.

Composed over 573d02d38/399 after pointwise review of abrupt reference returns,
WeakMap/Throwable comparison, Generator send, stdClass/define and recursive-list
seams. Source5/state929 retain private cuts; no joined actor, replay or renewed credit.

Int/bool `define` names now accept nonbool false scalar flags: integer zero,
empty or `"0"` strings and signed float zero. Weak calls convert only the API name,
retaining the raw flag; strict parameter-1 errors precede flag rejection after all
argument effects. Duplicate callbacks preserve converted empty-name traces, raw
request flags, old bindings, sibling effects and the original Exception/caller result.
Four exact originals agree at b00e6346. All 595 public premises pass: author
274+80+108 and independent 133 across four groups, covering fresh publication,
default duplication and handler return/throw, strict errors, full discard equality,
carrier and source refusals and budgets. The unchanged Unsupported baseline retains zero
credit; a fixture name collision was fixed before execution. Runtime adds only 20
module400 lines and reuses existing receive/duplicate/trace code with a bounded
marker-domain extension. Nonfinite float names with these flags, truthy/NULL/NaN flags,
owning/wider values and full family closure remain partial.
[False-flag name review](coverage/semantics/define-scalar-false-flag-review.json).

Pointwise composition over 108b026fe preserves the incoming 399-module parent.
Source4/state595 retain their private cuts; shared selectors are disjoint, so no
joined actor or renewed execution claim is warranted.

WeakMap now compares with normalized real/named Closure, actual Generator/Fiber
and finite builtin Throwable objects as uncomparable +1 in both directions.
Class mismatch precedes private entries, captures, VMs and formatter/cache fields;
nonzero aggregate leaves skip later real casts. The old Throwable effect refusal
and admitted route are explicitly disjoint. Three exact originals and 468 Boolean
premises (438 setup + 30 pure)/16 actual steps pass at the retained be386/2f97 cuts,
covering all seven operators, VM phases, warm caches, private owner1 and budgets.
The oversized originals' three timeouts, initial reserved-constructor fixture,
older effect refusal and pre-main fixture failures retain zero credit; two smaller
complete author originals preserve the intended coverage. Other Closure bodies,
internal/custom counterparts and wider weak producers/lifetimes remain partial.
[Internal WeakMap review](coverage/semantics/weakmap-internal-comparison-review.json).

Composed over e50d681b7/399 after pointwise review of shared tasks, typed returns,
Generator/delegation, constants, assignments and property/list dispatch. Source3
and state468 retain their private cuts; no joined actor or renewed credit.

With a quiet integer LEFT, plain-CV numeric `&=`/`|=`/`^=` now retain both longs
through fractional-RHS deprecation. Captured12/5 from5.5 stores4/13/9 despite
callback99/10 and detaches a late alias; supplied throw preserves callback writes,
the same Exception and alias write-through. Independent negative RHS(-1) from-1.5
still stores XOR-13, with original-line default Deprecated and detached alias99.
Five exact originals pass at9bcb1a3c9; author155/155/155/140 plus independent119
SL premises pass724 at3f53cfce6/399. Fresh both-cache/source/op/line/range guards,
actual cells/owners and budgets are covered; only the safe target is rechecked
after conversion. Native/baseline/retained checked prep/syntax retain0; pure ready
projections establish refusals only. Both-fractional operands, initial references/
copies, unsafe targets and wider callbacks/lifecycle remain partial; OP12 stays paused.
[RHS bitwise-assignment ledger](coverage/semantics/bitassign-right-warning-review.json).

Composed over 67c660172/399 after pointwise review of typed returns, Generator,
stdClass/define, property-empty/list and weak comparison seams. Source5/state724
retain their private cuts; no joined actor, replay or renewed credit.

NaN third flags with non-NUL `::` define names now emit their conversion Warning
before the name ValueError, skipping the ignored-true Warning. Returning handlers
retain raw captures and callback effects; first-handler throws cancel the body
while preserving the original Exception and inner binding. Strict calls reject the
raw float after argument effects without either Warning.
Four exact originals agree at 0dd57949; default and false-return cases each retain
one expected PHP-stderr Warning. All 441 public premises pass: author 96+147+72 and
independent 126 across four groups, covering actual dispatch/handler/resume/discard,
raw API/caller traces, canonical-literal versus runtime NaN captures, source/carrier
refusals and budgets. The unchanged Unsupported baseline retains zero credit;
copied rule labels were fixed before execution. Runtime adds one tag and 51
module400 lines; existing marker guards stay exact. NUL/coerced names, owning/wider
values and wider NaN producers/payloads remain partial. Native bit identity is not
claimed. [NaN class-name review](coverage/semantics/define-class-nan-flag-review.json).

Pointwise composition over e70950fc preserves the incoming 399-module parent.
Source4/state441 retain their private cuts; independent seam review warrants no
joined actor or renewed execution claim.

Plain-CV numeric `&=`/`|=`/`^=` now retain their fractional LEFT conversion
through deprecation handlers, then read the live quiet integer RHS. Captured12/live5
stores4/13/9 despite callback99 and detaches a late alias; supplied throw cancels
storage, preserves the same Exception and leaves later alias writes connected.
Independent signed XOR stores-15 with original-line default Deprecated.
Four exact originals pass at2a1acc7f2; corrected peer1 passes at9feef8126.
Author148/148/148/131 plus independent117 SL premises pass692 atcc0cd7bef/399,
covering all3 AST/OP guards, fresh cache/source/line refusals, actual cells/owners
and budgets. Retained checked prep/native/baseline/syntax and original unsupported
is_int observer failure keep0; only its strict-equality correction was rerun.
Initial references/copies, noninteger or warning RHS, unsafe targets and wider
callbacks/lifecycle remain partial; pure projections establish refusals only.
[Bitwise-assignment ledger](coverage/semantics/bitassign-warning-review.json). OP12 stays paused.

Composed over edd7296de/399 after pointwise review of typed assigned returns,
Generator, stdClass/define, property-empty/list and weak comparison seams. Source5
and state692 retain their private cuts; no joined actor, replay or renewed credit.

For non-NUL `define` names containing `::`, a NULL third flag now emits its
bool-reception deprecation before the name ValueError. Returning handlers preserve
raw captures despite live argument/callee writes; a throwing handler cancels the
body and keeps its original Exception and inner binding. Strict calls reject raw
NULL with parameter-3 TypeError after argument effects, without deprecation.
Four exact originals agree at 12e06acc, including the default Deprecated PHP-stderr
line. All 429 public premises pass: author 92+145+72 and independent 120 across four
groups, checking actual default/entered-handler/result/throw-discard steps, raw API
and caller traces, retained callback effects, source/carrier refusals and budgets.
The unchanged Unsupported baseline retains zero credit. Runtime adds one task tag
and 51 module400 lines; existing flag-marker guards stay exact. NaN flags for
these names, NUL/coerced names and wider/owning values remain partial.
[NULL class-name review](coverage/semantics/define-class-null-flag-review.json).

Pointwise composition over 7638815f preserves the incoming 399-module parent.
Source4/state429 retain their private cuts; independent seam review warrants no
joined actor or renewed execution claim.

With a quiet integer left operand, plain-CV `<<=`/`>>=` now keep both converted
longs through a fractional-count deprecation. Captured `-12`/`2` from `2.5` stores
`-48`/`-3` despite callback `99`/`1`, detaching a late alias. Supplied throw cancels
storage; cached negative count still raises original-line `ArithmeticError` after
a live positive rewrite, while cached `64` keeps the original right-shift sign.
Five exact originals pass at ebefecafe; 151/151/136 author plus 122/114 independent
SL premises pass 674 at 6312d9683/399, covering fresh both-cache/source/op/line
refusals, actual cells/owners, default Deprecated and budgets. Checked prep reuses
retained source/native bytes. Native/baseline/prep/syntax and the pre-PHP taskset
launcher failure retain0; pure ready projections establish refusals only.
Both-fractional operands, initial references/copies, unsafe targets and wider
callbacks/lifecycle remain partial; OP12 stays paused.
[RHS shift-assignment ledger](coverage/semantics/shiftassign-right-warning-review.json).

Composed over e90b3a746/399 after pointwise review of Generator, stdClass/define,
property-empty/list and typed assigned-return seams. Source5/state674 retain their
private cuts; no joined actor, replay or renewed credit.

Non-NUL `define` names containing `::` now receive int/string/non-NaN float
third flags with primitive values. Weak calls raise the name ValueError before any
ignored-flag Warning; strict calls instead raise parameter-3 TypeError after all
argument effects. Both retain raw flags, including negative zero and request `"0"`,
without warning callback, class lookup or constant-table mutation.
Four exact originals agree at f09a31dc. All 620 public premises pass: author
189+84+184 and independent 163 across four groups/nine genuine CONFIG error fronts,
checking raw API/caller traces, captured arguments despite live mutations, unchanged
state, source/carrier refusals and budgets. The unchanged Unsupported baseline retains
zero credit. Only 35 module400 insertions change runtime; the omitted/bool route
stays exact. NULL/NaN flags for these names, NUL names and wider/owning values remain
partial. [Scalar class-name review](coverage/semantics/define-class-scalar-flag-review.json).

Pointwise composition over 91ff8844 preserves the incoming 399-module parent.
Source4/state620 retain their private cuts; independent seam review warrants no
joined actor or renewed execution claim.

Plain-CV `<<=`/`>>=` now keep their fractional left conversion through deprecation
handlers, then read the live quiet integer count. Captured `-12` and count `2` store
`-48` or `-3` despite callback `99` and detach a late target alias. Supplied throw cancels storage;
negative live count raises the original-line `ArithmeticError` without detachment,
preserving callback writes/aliases and destination `100`. Four exact originals pass at
4a919d8f0; 141/141/124 author plus 120 independent SL premises pass 526 at 92a8ad2e0/398.
They cover both source/op guards, unchanged modulo refusals, actual CELL/LOCATION
and alias/error owners, default Deprecated and budgets. Checked prep reuses retained
source/native bytes; native/baseline/prep/syntax retain0. Pure ready projections
establish refusals only. Initial references/copies, warning or noninteger counts,
unsafe targets and wider callbacks/lifecycle remain partial; OP12 stays paused.
[Shift-assignment ledger](coverage/semantics/shiftassign-warning-review.json).

Composed over 040868796/399 after pointwise review of define, typed/byref return,
property-empty/list and weak numeric-comparison seams. Source4/state526 retain their
private cuts; no joined actor, replay or renewed credit.

Non-NUL string `define` names containing `::` now raise parameter-1 ValueError
before any ignored-true Warning. Omitted/bool flags preserve raw API arguments;
strict bool calls keep the same priority after all argument effects. No class
resolution, warning callback or constant-table mutation occurs.
Four exact originals agree at acf518e8. Author 167+69+69 and independent 145 public
premises pass 450 across four groups/seven genuine CONFIG error fronts, checking
raw two/three-argument traces, real caller frames, unchanged store/events/table,
request-string captures, source/carrier refusals and budgets. The unchanged
Unsupported baseline retains zero credit. The runtime adds only 30 module400
lines; wider/coerced flags, names and owning values remain partial. Pointwise
composition over 0cc3e18a preserves the 399-module incoming parent. Source4/state450
retain their private cuts; independent review warrants no joined actor or renewed
execution claim.
[Class-name review](coverage/semantics/define-class-name-review.json).

WeakMap and WeakReference numeric comparisons now dispatch real Notice callbacks
with fixed class names, including wrappers whose referents have expired. Private
1/1.0, CV/COPY/retained-cell selection and SECOND callbacks survive live writes.
Two exact originals and 355 Boolean premises (331 setup + 24 pure)/14 actual steps
pass at 1337908c3/398, covering private owner1, weak nonownership, real ALIAS/COW,
registered-handler restoration, pending late weak Notice/caster skips and the same
TypeError/finally with fresh guard cleanup. No actor failed; native/baseline,
preparation and typed elaboration add no agreement credit. Wider handlers, other
internal/custom classes and weak producer/lifetime protocols remain partial.
[Weak numeric review](coverage/semantics/weak-numeric-comparison-review.json).
The pointwise 399-module composition over 6f3488104 preserves incoming list,
property, arithmetic, constants and return paths. Source2/state355 retain their
private cut; independent seam review warrants no joined actor or renewed credit.

Destructuring key warnings retain recursive by-value CV/literal and mixed CV
patterns with quiet compiled/implicit or ordinary defined quiet CV keys. Module410
now resumes lossy float CV-key conversion for flat wholly by-value direct-CV RHS
patterns with direct CV leaves. The converted integer and table survive
E_DEPRECATED; lookup afterward sees current embedded-reference values or enters
module409's missing warning before any target store. Later key CVs are read afresh.
Default reporting, handler replacement and E_WARNING-only handlers preserve the
deprecation/lookup/warning order. Supplied throws cancel lookup and result delivery;
the captured table and otherwise unowned cells retire after their owners disappear.
Six A12 exact originals agree at f9fb2ad96. Five SL fronts pass 710 premises
(695 Boolean + 15 raw steps): author 151+135 at 0920e58fb, corrected throw 116
and independent 308 at 5a8d19d10. The initial throw fixture's negative constructor
atom failed before execution; only that fixture repeated, with zero credit for
the failure. The [float-key review](coverage/semantics/list-float-key-warning-review.json)
retains the unchanged Unsupported baseline and source/state cuts. A two-line
state-helper extension checks exact expected default stderr; old callers retain
empty-stderr behavior. Existing module409 plans, source gates and key conversion
helpers remain unchanged. Earlier [literal-CV cuts](coverage/semantics/list-literal-cv-missing-warning-review.json)
and [family reviews](docs/semantics/SOURCE-DESTRUCTURING-WARNINGS.md) retain their
original evidence without replay. Nested/literal/mixed lossy conversion, other key
diagnostics, wider RHS/targets and scalar/object callbacks/lifecycle remain partial.

Pointwise composition over 070236b5 preserves 399 incoming modules and adds module 410.
Magic-property, return, define, closure and compound selectors are disjoint.
Six sources and 710 premises retain their cuts; no joined actor or renewed credit.

Plain-CV `%=` now keeps both converted longs through a fractional-RHS deprecation.
Captured12/5 stores2 despite callback99/7 and detaches a late target alias; supplied
throw cancels the store. Captured0 from0.5 still raises the original-line modulo
`DivisionByZeroError` after a live RHS5, preserving target/alias99 and destination100.
Three exact originals pass at 2c04fc25e; 141/126 author plus137 independent SL premises
pass404 at c54aa0f05/397, covering public fresh guards, actual CELL/LOCATION and
alias/error owners, default Deprecated and budgets. Checked prep reused accepted
source/native bytes without application replay; prep/syntax and the original bb9
binding failure retain0. Pure target refusals establish no wider execution.
Both-fractional operands, initial references/copies, unsafe targets and wider
callbacks/lifecycle remain partial; OP12 stays paused.
[RHS modulo ledger](coverage/semantics/modassign-right-warning-review.json).
The pointwise 398-module composition over ca70c7aaf preserves Source35/M76/V60
and incoming list/comparison/Generator paths. Source3/state404 retain their private
cuts; independent seam review warrants no joined actor or renewed agreement.

A NaN third `define` flag now emits its bool-conversion Warning before the
ignored-flag Warning while retaining raw NaN in API arguments. A throwing first
handler cancels outer registration; a later ignored-warning throw still completes
its registration tail. Returning callbacks read the live constant table, and
strict calls reject after all argument effects without either warning.
Four exact originals agree at adce3cd8. Author 177+136+51 and independent 108
public premises pass 472 across four genuine fronts, checking literal publication,
duplicate ordering, captured raw bits, real first/second throw discard equality,
source/carrier/phase refusals and budgets. The unchanged Unsupported baseline
retains zero credit. Old quiet/scalar eligibility is unchanged; wider names,
values and owning/packed forms remain partial. Pointwise composition over
8d148d6b preserves the 398-module incoming parent. Source4/state472 retain their
private cuts; independent review warrants no joined actor or renewed execution.
[NaN-flag review](coverage/semantics/define-nan-flag-review.json).

Live WeakMap comparisons with stdClass, supported source instances and
WeakReference now return uncomparable +1 in either direction before property or
private-entry traversal. All seven operators cover both orientations and live/expired
wrappers; aggregate nonzero leaves skip later casts. Three exact sources and
398 Boolean premises (367 setup + 31 pure)/12 actual steps pass at 30ae1f26e/397,
including real function frames, source self-cycles, private owner1, weak nonownership
and budget splits. Original recorder/binding failures remain zero-credit; numeric,
other internal/custom counterparts and wider producer/lifetime forms remain partial.
[Mixed WeakMap review](coverage/semantics/weakmap-mixed-comparison-review.json).
The pointwise 398-module composition over f8882d5c preserves incoming
LIST_MISSING_RESULT and every parent helper. Source3/state398 retain their private
cuts; independent seam review warrants no joined actor or renewed agreement credit.

Plain-CV `%=` now keeps its fractional-float left conversion through deprecation
handlers, then reads the live quiet integer RHS. Captured12/live5 stores2; a supplied
throw preserves callback writes and its late alias, while live zero creates the
original-line `DivisionByZeroError` without store or detachment. Three exact
originals pass at 9ed645105; 126/116 author plus 120 independent SL premises pass
362 at 4e11c3dae/396. They cover fresh source/selection/cache/line guards, actual
CELL/LOCATION, error/alias owners, false-handler default Deprecated and budgets.
Pure ready projections establish refusals only; baseline/native/preparation/syntax
retain zero agreement credit. Initial references/copies, warning or noninteger RHS,
unsafe targets and wider callbacks/lifecycle remain partial; OP12 stays paused.
[Modulo-assignment ledger](coverage/semantics/modassign-warning-review.json).
The pointwise 397-module composition over 04c3c8c2f preserves incoming Source34
and every parent declaration/helper. Source3/state362 retain their private cuts;
independent seam review warrants no joined actor or renewed agreement credit.

Primitive `define` now completes duplicate reporting while an ignored-flag
warning exception is pending. An eligible handler is skipped without fallback;
a live handler that excludes Warning level uses default reporting instead. The
original binding, Throwable identity/Previous, captured arguments, callback effects
and caller destination survive. The duplicate report clears the stale fatal-trace
snapshot and respects the current reporting mask.
Two author originals agree at fc4e235a; an independent preexisting-row/scalar-flag
original agrees at 7d069659. Author 83 and independent strict 123 state premises
pass 206 at 7d069659, covering actual discard steps, complete state preservation,
source/carrier refusals, a source-backed seeded trace, quiet reporting and budgets.
The unchanged Unsupported baseline retains zero credit. The sole runtime change
is a 22-line module400 append using the existing boolean/scalar-flag guards;
wider values, coerced-name flags and owning/packed paths remain separate.
The NaN follow-up is recorded above.
Pointwise composition over 52357c36 preserves the 397-module incoming parent.
Source3/state206 retain their private cuts; independent review warrants no joined
actor or renewed execution claim.
[Pending-duplicate review](coverage/semantics/define-pending-duplicate-review.json).

A comparison's second implicit string cast now fails quietly when its opposing
live operand becomes a WeakMap or WeakReference, even after referent expiry.
Private entries and referents stay unread; copied strings, live CVs and retained
cells keep distinct outcomes. Three exact sources agree; author/independent state
tests pass 318 Boolean premises (315 setup + 3 pure) and 12 raw steps at efea0df4/396,
covering signed returns, real PLAIN caller frames, array COW, private child ownership
and identical-TypeError/finally cleanup. The original fixture parse failure retains
zero credit; initialization, syntax preparation and typed elaboration add no runtime
credit. Pair/numeric/explicit casts and existing producer/lifetime limits are unchanged.
[Weak internal redispatch ledger](coverage/semantics/weak-nonstringable-redispatch-review.json).
Dynamic include/eval now compile closed anonymous-class sites with request-wide
name history. Repeated visits allocate distinct instances of one compiled class;
recompilation gets the next suffix, while include_once skips preserve history.
Two exact originals and 254 SL premises (121 eval, 133 include) pass at runtime
diff 4182f25e, including old-class authority and one budget resume. Direct CV
assignment sites, completed prior compilations and no pre-name diagnostics bound
this slice; wider source shapes and ambiguous/failure histories remain partial.
[Dynamic anonymous review](coverage/semantics/anonymous-dynamic-units-review.json).

Selected inherited `__isset(string): bool` now handles terminal CV/literal private
property tests, while initialized public and typed-INITIAL slots bypass it. Actual
true/false callback results preserve multi-property short circuiting and unchanged
storage. Source1 passes at 5a6f91be; one state215 =164 reached +51 derived passes
at 5551514f, including normal/abrupt receiver release. Wider coalesce combinations
and magic forms remain unsupported. Historical `__unset` retains an exact
source-proof compatibility bridge without replay.
[Review](coverage/semantics/magic-isset-review.json).
The 397-module composition over 214dbc9b passes retained SL initialization at e484862a;
private source/state cuts keep their recorded revisions without replay.

Primitive plain-CV `**=` now commits captured power even when the deprecation
handler throws. The same pending Exception resumes after the store and detachment
of a late alias; the outer assignment stays at 100 and later target writes leave the
old alias unchanged. Three exact originals pass at 28b22bd35; 135/161 author plus
111 independent SL premises pass 407 at 7221327bc. They check signed infinity,
normal same-cell storage, pending-owner transfer, exact new-CELL/LOCATION and
alias owners, fresh source/number/target/metadata guards, default RHS-line Deprecated
and budgets. Pure ready projections establish refusals only. Wider operands,
targets, callbacks and lifecycle remain partial; OP12 stays paused.
[Power-assignment ledger](coverage/semantics/powerassign-warning-review.json).
Pointwise composition over 2566b810 preserves the 396-module parent and all
incoming declarations and helpers. Source3/state407 retain their private cuts;
no joined actor or renewed agreement credit was needed.

String-name `define` now receives a NULL third flag with primitive values.
Weak calls emit the parameter-3 deprecation before registration; normal return
uses false without replacing the raw NULL API argument. A callback-created
binding causes the separate duplicate Warning against the live table. A throwing
first deprecation cancels registration while preserving completed callback effects;
strict calls evaluate every argument before raw TypeError without deprecation.
Three author sources agree at e1692447 and one independent first-deprecation-throw
source at 587a95bd. Three public fronts pass 349 premises at 33871767, checking
literal publication/history, raw handler traces, captured selection, source/carrier
refusals and budget resumption. The unchanged Unsupported baseline retains zero
credit. Primitive values and ordinary string names bound this slice; NaN flags,
wider values and owning/packed calls remain separate. The 396-module composition
over 0533d397 passes full SL load/elaboration at be690134; its true fixture makes
no PHP application or initial-state assertion. Independent pointwise review
preserves the incoming parent; source4/public349 keep their private cuts.
[NULL-flag review](coverage/semantics/define-null-flag-review.json).

Live WeakMap pairs now return order zero through the standard zero-property
shortcut, without reading their private entries. Enclosing array and declared-slot
walks reach later casters; keys stay weak and map-owned values retain their owners.
Three exact sources and author/independent state tests pass 246 Boolean premises
(231 setup + 15 pure) and 9 raw steps at 12046434/395, including COW, skipped private
bodies, real later callbacks and identical-TypeError/finally cleanup. The original
peer type failure and author binary-state observer failure retain zero credit;
initialization, syntax preparation and typed elaboration add no agreement credit.
Mixed/numeric comparisons and wider map protocols/lifetimes remain partial.
[WeakMap comparison ledger](coverage/semantics/weakmap-comparison-review.json).

Direct-root zero-argument global `new stdClass()` now installs a genuine internal
object with a separate nonowning birth certificate. Ordinary reads share identity
and property writes; duplicate registration retains its fresh candidate through
the Warning handler, then frees it while preserving the original binding/mutation.
Two exact source comparisons and 225 SL premises (110 root, 115 duplicate) pass at
runtime diff 369ebde3, including live/dead value authority, owners and budget resume.
The original duplicate observer compile failure retains zero credit; the accepted
root native row remains separately scoped. Other internal/Throwable producers,
arguments and embedded/default values remain partial.
[stdClass producer review](coverage/semantics/global-constant-stdclass-review.json).

Global `constant()` now returns already-certified stdClass rows through literal
and retained selected calls. Lookup shares the exact live object, adds one RESULT
owner and allocates nothing; source aliases retain property writes after a query
result is released. Two exact originals and author239/independent145 SL premises
pass384 at runtime191ddd25/397, including same-site left→right selection and one
budget resume. The baseline Unsupported, first independent control failure and
undriven certificate controls keep zero agreement credit. Wider query/value forms remain partial.
[stdClass query review](coverage/semantics/global-constant-stdclass-query-review.json).
The 397-module composition over 1e732d1ca preserves incoming comparison, pending
define and modulo rules pointwise; source2/state384 retain their private cuts
without replay.

Certified stdClass aliases now pass through global constant array trees and
`constant()` queries, including eval declarations and whole-tree donation.
Querying adds one array root owner without copying or adding an object edge;
nested COW adds a real shared-object edge, while caller bucket replacement
preserves the original DIRECT tree. Three exact originals and author392 plus
independent256 SL premises pass648 at runtime d5026ab1/397. The baseline remains genuinely Unsupported;
its wrong expected-reason assertion is retained separately. Direct nested NEW,
defaults, generic objects and wider query forms remain partial.
[stdClass array review](coverage/semantics/global-constant-stdclass-array-review.json).
The 398-module composition over 84d03da88 preserves incoming Generator, list,
WeakMap, NaN-define and return selectors pointwise. Source3/state648 retain their
private397 cuts without replay.

Nested global constant arrays now create zero-argument stdClass leaves after
authentic earlier facts. Full and shorthand ternaries transfer the selected
newborn through immediate source arms to its exact completed birth receipt.
Fresh eval duplicate candidates remain distinct from installed leaves and retire
after the real Warning handler; shared property writes and ordinary COW persist.
Four exact sources and author596 plus independent511 SL premises pass1107.
Literal244 retains its original cut; corrected eval352 and peer307/204 retain
their affected398-module cuts. The
[nested-birth review](coverage/semantics/global-constant-stdclass-new-review.json)
records exact source paths, birth/flow guards, query owners and cleanup.
The unchanged Unsupported, first peer transfer failure and original cross-unit
empty-array fixture failure retain zero passing credit. A relocated-path pass
also retains zero credit; the accepted peer retry uses its native filename/cwd.
Defaults, arguments, whole-array conditional transfer/coalescing and wider
producers remain partial.
Pointwise composition over c9fc1c864 preserves the incoming399-module parent,
including define, arithmetic, Generator, return and mixed-list selectors.
Source4/state1107 retain their private398 cuts; no joined actor or renewed credit.

Newborn stdClass `??` leaves now keep a nonnull left value or select a fresh
fallback after a captured NULL, including nested chains and eval units. Only two
module283 flow heads are added; source/completion and separate live-value guards
remain. Three exact sources agree at their retained399-module cuts. Author282/316
plus independent219 SL premises pass817 at aee1b2cae, covering ordinary
COALESCE_RESULT handoff, quiet literal-DIM capture with V61 ternaries, two births
from five sites, temporary retirement
and real query/COW owners. Pure malformed histories are never driven. The
unchanged Unsupported and initial peer elaboration binding failure retain0; only
the affected peer fixture is renewed. Alias/whole-array coalescing, arguments,
defaults and wider producers remain partial.
[Coalescing review](coverage/semantics/global-constant-stdclass-coalesce-review.json).
Pointwise composition over c53bf2a3d preserves incoming399 modules, define,
shift, typed-return, magic-empty and nested-list selectors. Source3/state817
retain their private cuts; no joined actor or renewed credit.

Global stdClass constant-AST NEW now evaluates ordinary positional and uniquely
named ignored arguments through227. Exact source/value-table guards retain
argument owners; saved incomplete birth and pending binding survive context
clearing and avoid constructor-failed marking at the immediate discard. Source3
and author376/independent320 premises pass696, checking donor/array retirement,
argument Error, distinct fresh-eval retry and real value destructors. Normal
storage retirement later uses its ordinary CALLED marker and physical pin.
The first peer fixture assumed late marker absence; its corrected pin check
renews only that failed packet, with original failure0 preserved.
The original source with duplicate argument names exposes a real lifetime
mismatch and retains0: native keeps the rejected current value until shutdown.
That milestone's source guard requires unique names; the retained-current-value
follow-up below addresses its duplicate argument names.
References, unpacking, defaults and wider lifecycle forms remain partial.
[Argument review](coverage/semantics/global-constant-stdclass-arguments-review.json).

Duplicate named global stdClass AST arguments now retain the rejected current
value in a dedicated request owner, including whole nested arrays and their
physical leaf edges. Earlier values and the unfinished target retire before
catch search; the existing store scan invokes retained destructors after normal
output. Three exact sources agree, including escaped leaf41 and fresh-unit retry.
Author408 and independent312 premises pass720, checking real capture/root
neutrality, ordinary eager cleanup, durable source/prefix/live guards and
shutdown ownership. The V63 mismatch stays
historical0; parser/type and fixture scheduling/context/array-syntax failures are
preserved0, with only affected checks renewed. The first peer elaboration binder
failure is likewise corrected locally. Other owning classes, generic NEW
duplicates, references/unpacking, defaults and wider lifecycle remain partial.
[Duplicate-argument review](coverage/semantics/global-constant-stdclass-duplicate-arguments-review.json).

String-name `define` with an omitted/false flag now registers certified live
stdClass donors. Sole400 +13/-3 reuses their completed birth/live guards; actual
CONFIG capture transfers one call root to one row root without allocation.
Three exact sources agree, including named capture before a CV rebind, callback
mutation and throwing-handler cleanup. Author287 and independent229 premises
pass516, checking publication/query owners,
pure certificate refusals, normal false delivery and actual Exception trace/call
root release while the old property ALIAS keeps 53.
The first eval original's temporary-property write compile failure and literal
fixture binding failure remain0; only affected checks were renewed. Ordinary
uncertified objects and wider flags/names remain partial.
[Certified define review](coverage/semantics/define-stdclass-review.json).

Fresh two-argument `define` now copies nonempty array trees containing certified
stdClass leaves. Sole400 changes one leaf classifier; existing folds dereference
source cells, rebuild append history and share exact object pointers. Three exact
sources agree. Author299 and independent 270 premises check fresh physical
containers/leaf edges, literal and eval capture, no-allocation queries and real
nested bucket-reference COW, with pure live-birth/table refusals. All accepted
checks pass their first attempt; the unchanged Unsupported baseline retains0.
Other owning leaves, nested empties and wider flags/names remain
partial. [Array-object define review](coverage/semantics/define-stdclass-array-review.json).

User-key duplicate nonempty array `define` now keeps a canonical copied candidate
separate from the original CONFIG/input through reporting. The new30 task tag and
50 module400 lines reuse the existing primitive/carrier/certified stdClass fold
and ordinary cleanup; no generic lifecycle rule changes. Three exact sources
agree, including an eval false-handler Warning and a throwing handler whose trace
observes the rebound original input. Author333 and independent 221 premises
check private edges, live/prefix guards, normal and abrupt retirement, old rows,
callback writes and trace owners. All accepted checks pass first attempts; the
unchanged Unsupported baseline retains0. Empty-array duplicates, nested empties,
other owning leaves, startup keys and wider flags remain partial.
[Array-duplicate review](coverage/semantics/define-stdclass-array-duplicate-review.json).

Array definitions now also admit a captured boolean-false third slot. Actual
pre-flag and invoke fronts distinguish alias rebinding during flag evaluation
from later callback writes; copies retain the values after all arguments.
Three exact sources agree, including a throwing handler whose live flag becomes
true while its API trace retains false. All 524 premises pass (377 author, 147
independent), covering copied/original owners, normal/abrupt retirement and
true/nonboolean refusals. The first fixture preflight missing-import failure
remains0; only that fixture was corrected.
True/coerced flags and nested empties remain partial.
[False-flag array review](coverage/semantics/define-stdclass-array-false-flag-review.json).

Empty-root duplicate definitions now distinguish an authenticated pooled argument
from a freshly copied mutable empty candidate. Existing marker roots and ordinary
cleanup preserve source-pool pins and original API/Exception trace append history.
Three exact sources agree, including eval default reporting and a throwing
handler after flag-expression COW. All 398 premises pass (276 author, 122
independent), covering root multiplicity, canonical class/identity/history and
actual normal/abrupt retirement. A moved nonempty-input guard rejects mixed-shape
forged candidates; retained source cuts are pointwise unaffected. Nested empty
descendants and wider flags/names remain partial.
[Empty-duplicate review](coverage/semantics/define-empty-array-duplicate-review.json).

Selected inherited `__unset(string): void` now dispatches direct CV/literal-name
access to a declared private property. Accessible public unset skips magic;
the callback retains Parent lexical scope and Child called scope, removes the
private slot and sets `seen=13`. Source1 passes at 37ff84dd; current state
212 =165 reached +47 derived passes at ed8cccb4, including actual abrupt frame cleanup
and one saved receiver-owner release. Wider names/receivers and recursive magic
remain unsupported. [Review](coverage/semantics/magic-unset-review.json).
The 396-module composition over 60e77d86 passes retained SL initialization at 53ff2364;
private source/state cuts retain their recorded revisions without replay.

Boolean-true `define` now registers a fresh captured primitive even when its
ignored-flag warning handler throws. The old warning marker retains the pending
Throwable, caller destination and callback effects; strict calls preserve true
and a captured request-string value after named argument effects and a sibling
definition. The unchanged model had returned normally with the binding absent;
that measured disagreement remains zero credit.
Two original sources agree at cd8121ee; author 76 and independent strict 120 public
premises pass 196 at ba8d720c, checking exact row-only actual steps, immutable facts,
carrier/source/throw refusals and whole budget resumption. The pending duplicate
follow-up is recorded above. Wider values, NaN flags and coerced flags with
scalar/null names remain separate. The 395-module
composition over af5b5255 passes full SL load/elaboration at 8044e425; its true fixture makes no PHP application
or initial-state assertion. Independent pointwise review preserves the incoming parent;
source2/public196 retain their private revisions without replay.
[Boolean-tail review](coverage/semantics/define-bool-flag-pending-review.json).

String-name `define` now receives int/string/non-NaN float flags with primitive
values. Weak boolean parsing leaves the raw API argument intact through ignored
and duplicate warnings; strict calls evaluate all arguments before raw `TypeError`.
Returning callbacks use the live table. If the first ignored-warning handler
throws and the name is still fresh, registration installs the captured value
before the original exception continues, leaving the caller destination intact.
Three author sources and one independent throwing-handler source agree at cd955233.
Public462 retains author188/126/51 at 8643b193 plus independent97 at 4fb4eb6d,
covering named capture, raw traces, authentic string carriers, exact row-only
pending effects, refusals and budget resume. The original peer binder collision
remains zero credit; only its two captured-name premises changed.
NaN flags and scalar/null names with coerced flags remain separate; the
boolean-true and pending-duplicate follow-ups are recorded above.
The 395-module composition over 91a58a8b passes full SL initialization at 7260f84c.
Independent pointwise review preserves V56 and every incoming runtime selector;
source4/public462 retain their private cuts without replay.
[Scalar-flag review](coverage/semantics/define-scalar-flag-review.json).

Ordinary `**` now captures both primitive numbers before zero-base/negative-
exponent deprecation handlers. Normal return preserves signed infinity despite
callback writes; supplied throw cancels delivery and leaves the destination intact.
Three exact originals pass at 380f627cd; 135/130 author plus 101 independent SL
premises pass 366 at 6edf6aff8 using retained 23a7865a5 preparation. They cover
signed zero, fresh/public source/cache/range/metadata guards, saved TARGET,
unchanged store, supplied-object cancellation, default operand-line Deprecated and
budgets. The original fixture parse failure and old unrun numeric thin retain zero
credit; the correction groups negative constructor payloads without changed values.
Wider operands, conversion warnings, callbacks/lifecycle and `**=` remain partial;
OP12 stays paused. [Power ledger](coverage/semantics/power-warning-review.json).
The 395-module union over 675f40a2 preserves incoming scalar-define, return and
Generator paths. Independent pointwise review warrants no joined actor; source3
and state366 retain their private cuts without replay.

Plain-CV `.=` now retains the first string across a right-array warning.
Normal return commits cached concatenation over callback writes and detaches a
late alias; supplied throw cancels the store and preserves that alias. RHS removal
releases the borrowed array without a saved PARRAY. Three exact originals pass at
f1653b443; 147/138 author and 110 independent SL premises pass 395 at 884c8fbb1,
including actual CELL/LOCATION, owners, saved TARGET, fresh carrier/source/metadata
guards, default operand-line Warning, cancellation and budgets. Pure ready
projections establish refusals only. Baseline/native/preparation/syntax retain zero
agreement credit. Left-array warnings and wider operands/targets/callbacks/lifecycle
remain partial; OP12 stays paused.
[Concat-assignment ledger](coverage/semantics/concatassign-array-warning-review.json).
The 395-module composition over 11955af3 preserves incoming trait-autoload,
return/comparison/hook/Generator paths. Independent pointwise review warrants no
joined actor; source3 and state395 retain their private cuts without replay.

Class and trait declarations now autoload a sole missing user trait before method
import and publication. Parent availability precedes trait lookup, which precedes
interface lookup. Two exact originals and 380 SL premises at runtime diff b37690d7
cover eval/direct use, nested import, raw Trait versus logical Consumer identity,
source/history refusal and one budget resume. Raw headers authenticate the bounded
source independently of derived implicit interfaces; the latter control is pure.
Wider dependency lists, parents, adaptations and loading/failure interactions remain
partial. [Trait autoload review](coverage/semantics/trait-dependency-autoload-review.json).
The 395-module composition over b94139c8 preserves the incoming parent and accepted
rules at 06e40e61. Incoming reference-return/internal-object/private-set/Generator
selectors are absent; source2/public380 retain their private cuts without replay.

Public private(set) backed implicit class setters now retain their public slot key
and implicit finality. An inherited Parent writer on Child stores33 and returns
original20; Child/global array writes fail access, while Parent array reception
raises TypeError4/caller11. Plain Child redeclaration fails at class14. Source2
and strict395 pass at eb5f7e79; two genuine cuts305 =252 reached +53 derived pass
at a89dfc88. Existing normalization, permissions and final linker are reused;
wider asymmetric hook forms remain partial.
[Review](coverage/semantics/private-set-backed-hook-review.json).
The 395-module composition over b909b1a9 passes retained SL initialization at 9c1faa78;
private source/state cuts retain their recorded revisions without replay.

Null `define` names now dispatch the weak-call deprecation before conversion
or registration. A returning callback can create the empty-name binding first,
causing a separate duplicate Warning with the converted string in its API trace.
A throwing first handler retains raw null and cancels registration; strict calls
evaluate all arguments before raising `TypeError` with raw arguments.
Author3 at 2eaf296c and an independent throwing-handler source at 303b70c1 agree.
Public396 retains first209 at 5cb61a189 plus selected137/50 at 303b70c1,
covering exact empty-key history, captured named arguments, both warning phases,
raw/converted traces, source refusals and budget resumption. The original optional
field fixture failure remains zero credit; only its binder changed.
Primitive values and an omitted/already-false flag bound this slice; wider values,
flags and owning/packed forms remain separate. The 395-module composition over
aaa4d214 passes full SL initialization at b1d2e0c. Independent pointwise review
preserves V55 and the incoming parent; source4/public396 retain their private cuts.
[Null-define review](coverage/semantics/define-null-name-review.json).

Class and interface declarations now autoload a missing sole interface dependency
before linking or publishing the target. The resumed link retains the declaring
prototype and nominal ancestry. Two exact originals and 324 SL premises at runtime
diff 0a1b5855 cover eval/class implements, interface extends, dependency-versus-target
publication, source/history guards and budget resume. Two filename fixture failures
retain zero credit. Admission requires a parentless ordinary user target without
traits; wider dependency lists, parent/trait loading and callback/failure interactions
remain partial. [Interface autoload review](coverage/semantics/interface-dependency-autoload-review.json).
The 395-module composition over 859ae9eb preserves the incoming parent and accepted
rules at 96b1f9fd. Incoming concat/null-query/setter/reference-return/Generator selectors
are absent; source2/public324 retain their private cuts without renewed numeric credit.

Ordinary `.` now suspends for named array-warning handlers on two distinct
plain CVs with one nonempty mutable flat scalar array and one quiet string.
The left-array path yields fixed `Array` then reads its original live RHS cell;
the right-array path preserves the first converted string after callback mutation.
Borrowed array owners fall one to zero without a saved PARRAY. Supplied throws
preserve the destination and callback mutations. Three exact originals pass at
a23b774de; 270 author and 135 independent SL premises pass 405 at 39aa24b2f,
using retained PREP d1a9, including saved TARGET, marker-free throw, consumer/cache
public guards, default RHS-line Warning and budgets. Pure pruned/missing-name
projections are refusal checks only. Original source-elaboration and helper-structuring failures
remain zero credit; wider arrays/operands and RHS changes after a left-array
warning remain partial and OP12 paused.
[Concat-array ledger](coverage/semantics/concat-array-warning-review.json).
The 395-module composition over 20808896 preserves incoming paths and the
accepted concat rules. Independent pointwise review warrants no joined actor;
source3 and state405 retain their private cuts without replay.

Public protected(set) backed implicit class setters now use lexical access before
call/receive. Child writer20 stores33 and returns20; the same array gives a global
access Error versus Child TypeError4/caller14, leaving33. Source1/strict394 at6e018
and two cuts266 =224 reached +42 derived pass: receive149 at321b and corrected
errors117 at7dd75. The one partial fixture query and three diagnostics retain zero
credit. Wider asymmetric setter forms remain partial.
[Review](coverage/semantics/protected-set-backed-hook-review.json).
The 395-module composition over e116b628 passes retained SL initialization at b67d0b19;
private source/state cuts retain their recorded revisions without replay.

Null names in `constant`/`defined` now dispatch the weak-call deprecation before
conversion or lookup. A returning handler can publish the empty-name binding;
caller mutations preserve the captured null and selected API. Throwing handlers
keep raw null in the API trace, while a later missing-name Error uses the converted
empty string. Strict null calls raise `TypeError` without a deprecation.
Author3 at dae1196f and an independent throwing-handler source at 0c933990 agree;
400 public premises at 0c933990 cover real warning/resume fronts, late lookup,
default reporting, immutable source refusal, raw/converted traces and budgets.
The initial inner-handler terminal-phase assertion remains zero credit; its
correction checks the same refusal inside budgeted error unwind.
Stringable/array reception and packed/owning forms remain separate.
The 395-module composition over a7b6bf8b passes full SL initialization at 58697e27.
Independent pointwise review preserves the parent; source4/public400 retain their
private cuts without a replay.
[Null-query review](coverage/semantics/global-constant-null-name-review.json).

After an ordinary `__toString`, newly read real/named Closures, Generators and
Fibers now fail the comparison's second implicit string cast quietly. Signed order
uses the saved first string and stops nonzero aggregate leaves without invoking a
callable or resuming a VM. Three exact sources and 352 Boolean premises
(338 setup + 14 pure) and 13 raw steps pass at 474902f9/395, including CV/COPY/retained
cells, array COW, declared slots, captured children and normal/throw guard cleanup.
The unchanged refusal, initialization, syntax preparation and typed elaboration
keep zero agreement credit. Other internal handlers and wider lifetimes remain partial.
[Internal failed-cast review](coverage/semantics/internal-nonstringable-redispatch-review.json).

The authenticated numeric comparison remainder now skips builtin and inherited
Throwable string handlers after a Notice handler throws. Signed nonzero order
stops before later Notices; cold/warm caches and previous links remain untouched.
Three exact sources pass; author and independent state tests pass 509 Boolean
premises (485 setup + 24 pure) and 11 raw steps at fb3350b6/394, including both orientations,
array/property cursors, compared-error identity, COW and fresh guard cleanup.
The unchanged refusal, initialization, syntax preparation and typed elaboration
keep zero agreement credit. Normal, finally and post-catch formatting are unchanged;
wider pending effects and lifetimes remain partial.
[Pending Throwable review](coverage/semantics/pending-throwable-comparison-review.json).

With Zend multibyte disabled, closed single-line literal `declare(encoding=...);`
now emits its parser Warning before compiler diagnostics and bypasses user handlers.
The declaration then executes as a source-authenticated no-op. Two exact originals
and 177 SL premises pass at runtime diff 376d6a27, including eval ordering, once
skip versus ordinary reparse, helper stderr custody and budget resume. Bad placement,
wider declaration shapes and rejected parser inputs with warnings remain Unsupported;
the initial syntax failure retains zero credit. [Encoding review](coverage/semantics/encoding-declare-review.json).
The 395-module composition over 41b294b8 preserves the accepted compiler/CLI/test
blobs at b5b628fab and every incoming path. Incoming Generator, scalar DEFINE,
reference-return and array-cast selectors are absent; no joined numeric credit is claimed.


Explicit array-to-string casts now suspend for named warning handlers on a
defined plain CV with a nonempty mutable flat scalar array. The borrowed array
has no saved owner: replacement or removal of its CV still returns interned
`Array`; a supplied throw preserves the destination and callback mutations.
Three exact originals pass at 39c5e76cb; 213 author and 113 independent genuine
SL premises pass 326 at 3a3f0a674, including owner one to zero, saved TARGET,
marker-free throw, default operand-line Warning, public guards and budgets.
Pure refusal projections do not establish wider array/operand execution.
Empty/immutable/nested/owning arrays, wider operands/callbacks and lifecycle
paths remain partial; OP12 stays paused.
[Array-cast ledger](coverage/semantics/array-string-cast-warning-review.json).
The 395-module composition over 94402a17 preserves incoming Generator unpack,
constant and return paths. Independent pointwise review warrants no joined actor;
source3 and state326 retain their private cuts without replay.

`define` now receives int/bool/float names with primitive values and an
omitted/already-false flag. Weak registration uses call-time precision; historical
immutable-name checks allow a possible conversion after later precision changes.
Source sends map to normalized named slots while raw call authority stays intact.
Duplicate warnings retain the received carrier, precision and old table prefix;
throwing handlers expose the converted API name while caller values remain raw.
Author3 at 3e61a3a9 and an independent reordered-named source at 425a5543 agree;
351 public premises pass as157 at425a +194 atb537, including actual publication,
handler resume, source/identity refusals, strict TypeError and budget equality.
Original elaboration, mapping and fixture failures remain zero credit. Null,
Stringable/array names, array/object values with scalar names, true/coerced flags,
packed/owning calls and wider arity remain separate.
[Scalar-define review](coverage/semantics/define-scalar-name-review.json).
The 394-module composition over32234352 passes full SL initialization at aef78180.
Independent pointwise review preserves the parent; source4/public351 retain their
private cuts without a replay.

Global constant AST `new` now runs autoload before target allocation or argument
reads, then resumes with its authentic declaration context and loaded constructor.
A missed load raises the real Error without publishing the constant; a fresh
same-text eval declaration can retry successfully. Two exact sources and 326 SL
premises (141 retained success premises + 185 corrected retry premises) pass at runtime diff f3cd41fa,
covering incomplete/completed receipts, mutable object identity and budget resume.
The first binder and two fixture failures retain zero credit. Admission is bounded
to direct initializer roots with no earlier facts and supported positional arguments;
nested autoload and wider callback/lifecycle forms remain partial.
[Global NEW autoload review](coverage/semantics/global-constant-new-autoload-review.json).
The 394-module composition over b1688787 preserves the parent and accepted rules
at b9f0981e. Both source comparisons and 326 premises retain their private cuts;
no joined numeric evidence is claimed.


Initially plain CV numeric `+=` now keeps its original destination classification
through named warning handlers. Successful replacement detaches a callback-created
reference and writes a new non-reference CV cell; a supplied throw retains the
late alias and callback mutations. Three exact originals at ab36f1604 cover
return, throw and live nonnumeric alias/default Warning at the operand line.
Author 272 and independent 115 focused SL premises pass 387 at ed0f44a2a,
including saved TARGET frames, new CELL/LOCATION, old alias owners two to one,
public snapshot/selection/flavor rejection and budget continuation. Pure missing-name,
PROPREF, owning and RHS projections remain refusal checks only. Newly wrapped,
missing/warning/invalid RHS, owning/constrained/missing targets, other producers,
callbacks and lifecycle paths stay partial; OP12 remains paused.
[Plain-CV compound ledger](coverage/semantics/addassign-cv-warning-review.json).
The 394-module composition over ac8fc88f preserves all three private runtime
modules and incoming parent paths. Independent pointwise review warrants no
joined actor; source3 and state387 retain their recorded cuts without replay.

Active same-object alias writes inside a sole virtual class SET now raise the
receiver’s Must-not-write Error after reading a defined CV RHS. No second setter
call/conversion occurs; the task tail, outer result7 and stored10/no slot survive.
Source1/strict394 pass at292bd; one real state passes116 =92 reached +24 derived
at15982, including retained-array RHS priority. Other RHS/warning and virtual setter
forms remain partial. [Review](coverage/semantics/active-virtual-set-alias-review.json).
The 394-module composition over9dbf3b30 adds no current actor; actual incoming
paths are disjoint and private source/state results retain their recorded revisions.

After an ordinary `__toString` returns, a newly read live stdClass or standard
source object with no effective method now fails the comparison's second implicit
string cast quietly. Signed order finishes the original operator or skips later
aggregate leaves. CV/COPY/retained-cell differences, pinned arrays, declared slots,
first-caster throw/finally and fresh guard cleanup pass three exact sources and
423 Boolean premises (403 setup + 20 pure) and 12 raw steps at 209cb21d/394.
The unchanged refusal, initialization, syntax preparation and typed elaboration
keep zero agreement credit. Other internal handlers, unsupported method forms and
wider lifetimes remain partial.
[Failed second-cast review](coverage/semantics/nonstringable-redispatch-review.json).

Global `constant`/`defined` now receive int/bool/float names after argument
effects. Weak calls use the existing string conversion; strict calls raise the
native `TypeError`. Captured originals retain exact immutable input and callee
authority; only a weak missing-name Error's argument view becomes the converted
string. Three exact sources at 5b6d1079, an independent false-CV source at a8945805
and 320 public premises at a8945805 pass, covering selection mutation, raw/converted
traces, unchanged stores, source forgery refusal and budget resumption. Null
deprecation, Stringable/array reception, arity, packed/owning calls and define
name/flag coercions remain separate.
[Scalar-name review](coverage/semantics/global-constant-scalar-name-review.json).
The 394-module composition over ad37d550 passes full SL initialization at 8112dfc8.
Independent pointwise review preserves the parent; source4/public320 keep their
private cuts without a replay.

A selected sole implicit virtual class SET now omits its value slot while its
body writes separate stored10→33. Assignment20 returns20; reads raise the receiver’s
write-only Error, and array input fails before the body. Active same-object virtual
setter writes retain demand and explicitly refuse a recursive plan. Source1 and
strict394 pass at8969; two real state cuts pass252 =209 reached +43 derived at6aff.
Other virtual setter forms and active alias-write RHS families remain partial.
[Review](coverage/semantics/virtual-set-only-hook-review.json).
The 394-module composition over6bad passes retained SL initialization at37931863;
private source/state cuts keep their recorded identities without replay.

Numeric `+=` now saves the leading-numeric left conversion before a named
warning handler and commits into the originally selected untyped reference cell.
Three exact originals at cd6eff510 cover callback writes, supplied-object throw
cancellation and old-cell commit after name rebinding with default Warning.
Author 273 and independent 87 focused SL premises pass 360 at 472dc8d4d using
retained PREP23c inputs. Genuine production fronts cover captured holders,
selected owners, commit/cancellation, public descriptor rejection and budget resume;
PROPREF and unrooted-target projections are pure refusal queries only.
The original fixture syntax failure remains zero credit; only its cardinality
parentheses changed. Typed/owning/expired targets, newly warning or invalid RHS,
wider operands/callbacks and lifecycle paths remain partial. OP12 stays paused.
[Compound ADD warning ledger](coverage/semantics/addassign-warning-review.json).
The 394-module composition over 0c7eec9f preserves OP17's separate ADD failure
route. Independent pointwise review finds no joined gate necessary; source3 and
the 360 state conditions retain their private cuts without replay.


Class-query `self`/`parent` now use the actual lexical scope and `static` uses the
called class, including inherited-method eval. Both APIs raise scope Errors before
quiet member lookup; the original query spelling and trace argument remain intact.
Two exact sources and two public fronts/368 premises pass at runtime diff 5e4b4199,
covering six eval queries, two representative Error states and budget resumption.
Keyword `constant` values remain folded primitives/literal strings; wider values,
initializers and internal/bound-Closure scopes remain partial.
[Keyword-query ledger](coverage/semantics/class-keyword-query-review.json).
The 394-module composition over 0ef18e1a preserves Source26's global-array leaf
rules and the accepted keyword block at 89729506. Private source2/public368 keep
their tested cut; no joined numeric evidence is claimed.

Global `constant` array queries now admit certified `PVINSTANCE` and `PVCLOSURE`
leaves through their existing live/source certificates. Queries preserve the stored
root and embedded-object owners; actual COW adds a distinct physical array-to-object edge.
Two exact sources at 7941e9f6, an independent bucket-reference source at 58d4993a
and 564 public premises at 58d4993a pass, covering
nested COW, shared properties/statics, readonly storage and forged leaf rejection.
The unchanged first-source refusal and native/preparation retain zero credit.
Stored ALIAS/cyclic array trees, generic objects and wider query forms remain outside
this slice.
[Object-leaf review](coverage/semantics/global-constant-object-array-review.json).
The 394-module composition over 0818945b passes full SL initialization at 3743963b.
Independent pointwise review preserves the incoming parent; source3/public564
retain their private cuts without a replay.

Numeric comparisons now finish a bounded C remainder after a Notice handler
throws. Later registered callbacks and source string casts are skipped; an
excluded numeric Notice still uses default reporting before the original error
reaches catch/finally. Three exact sources and author and independent tests pass
319 premises (292 setup + 27 pure) and 10 raw steps at dca8ccfc/394, including
retained/replaced/null registrations, array/property scans, COW and fresh cleanup.
The unchanged refusal, initial type-check failure and syntax/initialization keep
zero agreement. Throwable formatting and wider storage/lifetime effects remain open.
[Pending comparison ledger](coverage/semantics/pending-exception-comparison-review.json).

A selected direct backed Trait GET/implicit-SET pair now imports both Consumer
clones atomically, retaining raw Trait code and magic. Missing raw partners keep
interception required while refusing a call plan. Real GET self-write and SET
self-read bypass both hooks; assignment20 returns20 after storage33/get46.
The original source and strict 394-module initialization pass at 8d33; two
state checks pass333 premises (280 reached,53 derived) at03ba.
Other pair order/body/import forms remain partial. [Review](coverage/semantics/trait-imported-paired-hooks-review.json).
The 394-module composition over24b84e08 adds no current actor; actual incoming
paths are disjoint and private results retain their recorded revisions.

Class-qualified `defined` now initializes a requested untyped plain-global-name
member before returning true. Inaccessible members stay false without evaluation;
a missing global raises the actual `defined` Error and permits retry after
definition. Two exact sources and two public fronts/415 premises pass, preserving
request-string cache identity and exact binder/resume authority. Source comparisons
retain runtime diff 07143790; current public chains cover the narrow source-site
guard at f79db9. Other initializers, fixed namespace fallback and wider class,
autoload and owning forms remain open.
[Deferred-defined ledger](coverage/semantics/class-qualified-defined-deferred-review.json).
The 394-module composition over 6c80b851 preserves the incoming parent and accepted
class-defined rules at 746d1dcb. Private source2/public415 retain their tested cuts;
no joined numeric evidence is claimed.

Selected-cell ADD now raises TypeError from live raw scalar operand types when
RIGHT conversion fails after a leading-numeric warning. Completed RIGHT warnings
still deliver their cached number despite later invalid writes. Two exact originals
at 1c858 agree; 82 author and 77 independent genuine SL premises pass 159 at 99217,
including marker-free caller THROW_SEARCH, sole Error ownership, unchanged
assignment, public source/phase rejection, default Warning and budget resumption.
The native observations, unchanged Unsupported baseline, preparation and syntax
recorder/adjudication retain zero agreement credit. Wider operands, owning/expired
values and callback/lifecycle forms remain partial; OP12 stays paused.
[ADD failure ledger](coverage/semantics/arithmetic-failure-review.json).
The 394-module composition over 4ff preserves the accepted rules at c2ce.
Independent pointwise review finds unchanged direct interfaces and disjoint parent
selectors; source2/state159 retain their private cuts without another actor.


Real/named Closure, Generator and Fiber numeric comparisons now enter Notice
callbacks through finite class images. Existing pair comparisons and VM storage
stay unchanged. Three exact sources and author and independent tests pass 317
premises (286 setup + 31 pure) and 13 raw steps at 0187401a/394, including live
versus copied operands, saved float across a second Notice, real captured children,
COW and same-TypeError/finally cleanup with cold bodies. The unchanged refusal,
initialization and syntax preparation retain zero agreement. Other Closure bodies
and wider handlers/lifetimes remain open; pending remainders have a separate bounded extension.
[Internal numeric Notice ledger](coverage/semantics/internal-numeric-comparison-review.json).
Selected HALT-offset queries now retain the first registration for the API
call site's compiled filename, while fixed raw literal `defined` keeps its
separate false result. Repeated eval returns runtime offset 111 alongside
current direct offset 137. Two exact sources and two public fronts/375 premises pass at runtime
diff 8b355616, including parser-reject absence and budget resumption. Ambiguous
HALT compilation returns Unsupported; other direct calls, absent value lookup
Errors and wider source forms remain partial. Preparatory syntax failures retain zero credit.
[HALT lookup ledger](coverage/semantics/halt-lookup-review.json).
The 394-module composition over 5dba9ba1 retains the parent global-array lookup
and accepted HALT rules at 248d9c9f. Private source/state cuts are unchanged;
no new numeric evidence is claimed.

Direct sole backed trait SET now preserves an actual builtin explicit parameter.
Raw Trait Param/type/variance proof authenticates the Consumer callable signature
and physical body. Trait magic, Consumer private13 and Grand called scope remain
distinct; assignment returns original STRING20 after backing33. A narrow parameter
fails at physical Trait hook ENDLINE7 before import. Two originals/strict394 pass
at fddc, and two states pass281 =233 reached +48 derived at fd604. No earlier
class cut is renewed; wider trait/parameter forms remain partial.
[Review](coverage/semantics/trait-imported-explicit-set-hook-review.json).
The 394-module composition over b0ee passes retained SL initialization at b17f;
private source/state cuts retain their original identities without replay.

Bitwise NOT now stages finite in-range fractional-float deprecations from a
defined non-reference CV through named handlers. It captures the converted long
before dispatch; handler writes cannot replace it. Three exact originals at 895e
cover saved 2 becoming -3 with live 99, supplied throw with unchanged destination,
and saved -1 becoming 0 with one default Deprecated on the operand line.
Author 227 and independent 97 genuine SL premises pass 324 at 3d3f, including
saved TARGET frames, public snapshot/diagnostic rejection, ownership and budget
resumption. Native, unchanged Unsupported baseline, preparation and syntax-only
records retain zero agreement credit. Range/NaN, other operands, callbacks and
lifecycle forms remain partial; OP12 stays paused.
[BITNOT warning ledger](coverage/semantics/bitnot-warning-review.json).
The 394-module join over a202 passes full SL initialization at 739d.
Independent pointwise review preserves the incoming parent; source3 and the
324 state premises retain their private cuts without a replay.


Same-class Generator and Fiber pairs now compare with order zero through the
standard zero-property shortcut. Comparison preserves VM/capture storage and
continues to later array or declared-property leaves. Three exact sources and
author and independent tests pass 409 premises (376 setup + 33 pure) and 14 raw steps
at 2929/394, including created/suspended/completed pairs, real later casts, COW
and same-TypeError/finally cleanup. The unchanged normal mismatch and two fixture
elaboration failures retain zero agreement. Numeric internal handlers and wider
lifetime behavior remain separate.
[Generator/Fiber comparison ledger](coverage/semantics/generator-fiber-comparison-review.json).
Selected nonowning `trigger_error` calls now drain a retained file-compiler
fatal with the current callback trace. An exact CONFIG/nonce receipt preserves
captured arguments and authenticates each abandoned record. One retained v33
original now agrees; 182 public premises cover prefix replay, malformed/omitted
receipts and budget resumption at runtime diff fb33. The failed trace-identity
expectation remains 0; only its fixture was corrected. Owning, named, unpacked
and coercing forms remain outside this slice.
[Selected-drain ledger](coverage/semantics/source-recorded-dynamic-fatal-review.json).
The 394-module composition over 211048a5 preserves the accepted rules at
52637d06 and incoming parent paths. Shared30 retains parent unary additions;
no new actor/source/state evidence is claimed.

Direct sole backed implicit trait SET now imports into a parentless Consumer.
An authenticated raw Trait source yields a Consumer callable without mutating
FUNCTIONS; Trait magic, Consumer private13 and Grand called scope stay distinct.
Assignment20 restores20 after backing33; bad-array caller24 remains pre-body.
Source1/strict394 pass at c352; the later class-owner guard is covered by two
current-code states at d586, passing231 =179 reached +52 derived. The measured
fixture false, syntax failure and diagnostic retain0; no old class cut is renewed.
[Review](coverage/semantics/trait-imported-backed-set-hook-review.json).
The 394-module composition over 8c7938fc passes retained SL initialization at ae95;
private source/state cuts retain their original identities without replay.

Module404 now stages unary `+`/`-` leading-numeric warnings from a defined
non-reference CV through named handlers. Fresh capture/dispatch matches the CV;
entered callbacks and resumed numbers remain historical despite live writes.
Three exact originals at 0575 cover saved 12 with live CV 99, a supplied throw
with unchanged destination, and negative boundary float capture/default Warning
at the operand line. Author 227 at 44ae and independent 96 at 19bf pass 323 SL premises,
including saved TARGET frames, public snapshot/message rejection, owner counts,
sign delivery and budget resumption. The original baseline, forward-declaration
failure and incorrect integer-capture fixture retain zero credit. Wider operand,
value, callback and lifecycle forms remain partial. OP12 stays paused.
[Unary warning ledger](coverage/semantics/unary-warning-review.json).
The 394-module join over a843 passes full SL initialization at 1177.
Independent pointwise review preserves all incoming changes; the three sources
and 323 state premises retain their private cuts without a replay.

Ordinary string-valued `const` declarations now accept authentic interned and
request carriers without changing their identity or source allocation classes.
Five exact sources retain their 10475/3342 cuts; two publication fronts pass 279 SL
premises at 3342, including raw source-class versus receiving interning, invalid
identity/fact/table refusal, unchanged storage and budget resumption. The unchanged
baseline, first-BIND decision and two fixture failures retain zero agreement.
Independent request-array COW and actual default reads agree. The 394-module
composition over 8e7f74f1 passes one V48 deferred-string comparison at 37c0, preserving
incoming rules and the private cuts. The constant family stays partial.
[String-publication ledger](coverage/semantics/const-string-review.json).

Class-qualified `constant` now evaluates a requested untyped class initializer
that reads a plain global constant, without updating unrelated members. Failure
restores the class context without caching; defining the missing global permits
retry. Actual request-string carriers survive initialization and later caller CV
writes. Two exact sources and two public fronts/314 premises pass; native,
unchanged baseline and preparations retain 0. Other deferred initializers and
wider value/class domains remain open.
[Deferred-query ledger](coverage/semantics/class-qualified-constant-deferred-review.json).
The 394-module composition over 0fbe7684 preserves the parent and accepted class
rules at 89655060. The sole selected-string interaction comparison passes; private
source/state cuts and counts remain unchanged.

Builtin Throwable and admitted source-subclass int/float comparisons now
enter numeric Notice handlers with the correct nominal kind or source name.
The receiver image does not consult formatter fields. Three original sources
agree with PHP; author and independent tests pass 340 premises (318 setup +22 pure) and
17 raw steps at f757/394, including copied static values versus retained aggregate
cells, saved float across a second Notice, original-Exception/previous identity and cold caches.
The quiet pending-exception and wider handler/lifetime limits remain.
[Throwable Notice ledger](coverage/semantics/throwable-numeric-comparison-review.json).

Global `constant` now returns primitive user/startup values and authenticated
string carriers after argument effects, preserving namespace/case rules and
missing-name API Errors. Four exact sources retain their 516c/5b83/5e33 cuts; three
public fronts pass 323 physical premises at fdcb, including named immutable-query
facts, captured dynamic selection, row classes, Error arguments and budget resume.
The baseline, historical pre-call `const` string publication failure and reached
array-result refusal retain zero agreement. Wider values, coercions and owning
forms remain required; full core stays partial.
The 394-module composition over c011d175 passes full SL initialization and one
exact qualified-empty source at 54ac3199, preserving V47 and incoming rules.
Private source/state cuts retain their identities without replay.
[Global-query ledger](coverage/semantics/global-constant-review.json).

Global array `constant` queries now retain their stored root and nested identities,
including authenticated request-string leaves and immutable and mutable empty roots.
Existing COW handles nested writes and references without modifying the constant
or another query result. Three author sources agree at `82cd`, an independent
reference/append-history source agrees at `fa767`, and 327 public premises pass
at `fa767`. Composition over `3eddc5f9` passes full 394-module SL initialization
at `8dc83f69`; private source/state cuts remain unchanged.
The unchanged query baseline and initial fixture parse failure retain zero credit.
[Array-query review](coverage/semantics/global-constant-array-review.json).

Global `constant` queries now return already-certified `PVINSTANCE` user objects
with the same identity and current mutable properties. Existing completed-NEW
and live-allocation guards remain authoritative; ordinary RESULT adds one owner.
Two author sources agree at `8850668`, an independent alias/property-reference
source agrees at `3893fe5`, and two source-derived state groups pass 375 premises
at `3893fe5`, including table-only ownership after unset and malformed certificates.
The unchanged query baseline retains zero credit. Composition over `c8161a0e`
passes full 394-module SL initialization at `3857d5f8`, preserving V50 HALT and
M62 rules; private source/state cuts remain unchanged. Generic `PVOBJECT` and
instance array leaves remain outside this slice.
[Instance-query review](coverage/semantics/global-constant-instance-review.json).

Global `constant` queries now return already-certified `PVCLOSURE` values with
shared identity, static cells and callable scope. Two author sources agree at
`d7aa877c`, an independent inherited-method FCC source agrees at `8e5c038d`, and
two genuine query groups pass 475 SL premises at `8e5c038d`. Checks distinguish
one versus two table owners, alias declaration from original receipt, mutable
counter cells and RESULT ownership. The unchanged query baseline retains zero
credit. Composition over `91e8184a` passes full 394-module SL initialization at
`8b6e3f5e`, preserving V51 and all incoming rules; private source/state cuts remain
unchanged. Generic objects, object-bearing arrays and wider conversion remain open.
[Closure-query review](coverage/semantics/global-constant-closure-review.json).

Class-qualified `constant` now admits source-authenticated immutable empty array
roots and children. Queries retain pooled identity; a reference bucket initially
holds the shared empty child, then append detaches it. Two exact sources and two
public fronts/244 premises pass with runtime diff 015b, distinguishing post-unset
append history and canonical mutable clones from immutable provenance. The
baseline/native/preparations retain 0; mutable-empty/deferred/nonliteral query
values remain Unsupported.
[Empty-query ledger](coverage/semantics/class-qualified-constant-empty-review.json).
The 394-module composition over 8aa85111 passes independent pointwise review at
2222a077; accepted class-only rules/protocol and incoming paths are preserved.
No renewed actor/source/state evidence is claimed.

Module404 now stages leading-numeric-string DIV warnings for two direct CVs with
preexisting untyped reference cells and named handlers. The next conversion reads
its selected referent; captured numbers survive later handler writes. Two exact
originals at a3a preserve handler-written and captured zero divisors, one default
Warning, DivisionByZeroError at the operator line and an unchanged result destination.
Author130 and independent94 genuine production fronts pass 224 SL premises at 862,
including public snapshot/source/phase rejection, real Error ownership and budget
resumption. The original Unsupported baseline and native/preparation/syntax-only
records retain zero credit; the syntax recorder correction reuses the retained
author output without a rerun. Other slot classes, copies, right-only ingress,
owning callbacks and unsafe/nonconvertible replacements remain required. OP12 stays
paused. [DIV warning ledger](coverage/semantics/division-warning-review.json).
The 394-module join over ba76 passes full SL initialization at 68e2. Independent
pointwise review preserves the parent's unrelated runtime changes; the two source
agreements and 224 state premises keep their private cuts without a replay.

Builtin stdClass/int/float comparisons now use the numeric Notice continuation.
Its local class image preserves the fixed builtin name and source-class origins
across restored second Notices, without adding receiver owners. Three exact
sources and author/independent tests pass 347 premises (330 setup +17 pure) and
19 raw steps at 264d/392, including saved float 1.0 versus a late 9, property
old-cell rebinding, real array COW and same-TypeError/finally cleanup. The two
fixture failures retain zero credit; the quiet pending-exception restriction
and wider handler/lifetime limits remain. [stdClass Notice ledger](coverage/semantics/stdclass-numeric-comparison-review.json).

Class-qualified `constant` now returns source-pooled nonempty literal array trees.
Queries preserve the pooled root and nested tables; ordinary writes and reference
acquisition use the existing COW machinery without changing the constant or peer.
Two exact sources and two public fronts/326 premises pass with runtime diff 580b,
including same-root/no-allocation results, shallow then nested detachment, real
reference acquisition and canonical DIRECT-tree/history checks. The unchanged
baseline, native observations and preparations retain 0. At that cut, empty,
deferred and nonliteral arrays and wider value domains remain Unsupported.
[Array-query ledger](coverage/semantics/class-qualified-constant-array-review.json).
The 394-module composition over a5d519d7 passes independent pointwise review at
700649de1; accepted array rules/protocol and all incoming paths are preserved.
No renewed actor/source/state evidence is claimed.

Embedded-NUL include/require paths now fail before file-provider or dynamic-parser
requests, nonce allocation and once lookup. Include emits one frozen-path warning
and returns false; require throws `Error`. The display uses the credential-stripped
C-string prefix while retaining the full requested bytes. Eight NUL originals and
two empty-path regression controls agree at c69ecf; five reached fronts/208 premises
pass at 2cd61, covering saved handlers, trace/source guards, no-provider state and
a genuine captured-conversion refusal. That refusal and the original baseline and
two pre-runtime failures retain zero agreement. Captured conversion lifetime and
broader source/service contexts remain open.
The 394-module composition over 238baa65 passes both builds, full SL initialization
and inventory at 4afe5d10; private source/state cuts retain their original identities.
[NUL-path evidence](coverage/semantics/source-nul-path-review.json).

Module404 stages leading-numeric-string ADD warnings for two direct CVs with
preexisting untyped reference cells. Both selected referents survive callback
mutation; each numeric holder is captured before its warning. Returning handlers,
a supplied throw with an unchanged result destination, and a second false-handler
warning/default fallback agree in three originals at ec44/cb7. Two author fronts
pass 128/119 premises and the independent RIGHT-warning front passes 74 (321 total)
at 9dcb with cb7 runtime bytes. Whole public validation rejects coordinated
snapshot/number forgeries and another live-cell pointer; genuine owners and budget
resumption pass. The original Unsupported baseline, native observations and
syntax/native preparations retain zero credit. Other slot classes, copies,
right-only ingress, owning callbacks, unsafe/nonconvertible replacements and wider
arithmetic/lifecycle routes remain required. OP12 stays paused.
[ADD warning ledger](coverage/semantics/arithmetic-warning-review.json).
The 394-module join over d8bcbc01 passes current full SL initialization at 48d2.
Independent pointwise review preserves parent comparisons, setters and constant
lookup; private source/state cuts retain their identities without a source replay.

Class-qualified `constant` now returns inherited folded primitives and authenticated
literal strings with the actual lexical visibility. Missing/inaccessible lookup
raises an API Error; named autoload retains its full query and selection across
real caller CV mutations, then resumes once. Two exact sources retain runtime
diffs a26b/9960; two public fronts/384 premises pass with runtime diff 9960, including
value types, raw-to-installed string class and Error trace authority. The original
selected failure, baseline/native/preparation evidence retain 0. At that cut, global
queries, deferred evaluation, wider values/class kinds/coercions and owning forms
remain Unsupported. [Qualified-constant ledger](coverage/semantics/class-qualified-constant-review.json).
The 393-module composition over d3c27de8 passes independent pointwise review at
b19ee1e7; accepted runtime deltas/protocol and incoming setter/comparison paths
are preserved. No renewed actor/source/state evidence is claimed.

Module 402 now resumes ordinary source-instance/int/float comparisons after the
failed-cast Notice. Generic handler restoration preserves live CV/CELL versus
COPY reads, saved 1/1.0 across a second Notice, and authentic aggregate guards,
pins and zero-only cursor continuation. Four exact sources agree at a1ec/392;
author and independent tests pass 482 premises (285 +197; 464 setup +18 pure)
and 26 raw steps, including Notice↔Stringable handoffs, same-TypeError/finally cleanup and
quiet exception cancellation. Future effectful comparison remainders under a
pending exception are explicit Unsupported. The original unchanged baseline,
initializer, syntax preparation and helper-binding failure retain zero runtime
credit. Internal/custom handlers, legacy materialized routes and wider lifetimes
remain open. [Numeric Notice ledger](coverage/semantics/object-numeric-comparison-review.json).

Class-qualified `defined` now checks inherited user constants with actual lexical
visibility and quiet missing/inaccessible results. Named autoload retains the full
query and dynamic selection, then resumes once; a missing member on a loaded class
never reloads it. Two exact source comparisons pass with runtime diff e355; two
public fronts/288 premises pass with runtime diff 5d45 after a narrow carrier guard.
The baseline/native/preparation evidence retains 0. At that cut, deferred evaluation, keyword/internal/
trait/interface/enum queries, coercions and wider owning forms remain Unsupported.
[Qualified-defined ledger](coverage/semantics/class-qualified-defined-review.json).
The 391-module composition over 0420409 passes independent pointwise review at
64d0ab3e; accepted runtime/protocol and parent operational paths are preserved.
No renewed actor/source/state evidence is claimed.

Top-level empty `define` values now preserve their allocation class. Authenticated
immutable empties retain their table; mutable emptied arrays become fresh canonical
tables with rebuilt append history. Two exact sources and two public fronts/162
premises pass with runtime diff 9e6a, including same-table versus fresh-copy roots, wrong-class and
history rejection, and a mutable clone that cannot impersonate a fixed literal.
The baseline/native/preparations retain 0; nested-empty refusal is a pure projection.
Nested empties, array warning/flag paths and wider domains remain Unsupported.
[Empty-define ledger](coverage/semantics/dynamic-constant-empty-review.json).
The 391-module composition over a2b660c passes independent pointwise review at
0ea017fb9; accepted rules/helpers and parent operational paths are preserved.
No renewed actor/source/state evidence is claimed.

Fresh two-argument `define` now snapshots nonempty acyclic scalar-array trees.
It dereferences source cells and rebuilds ordered tables, so later source writes
preserve the constant and append indexes follow surviving keys. Two exact sources
and two public fronts/219 premises pass at ada3, including request-string classes,
nested references, literal-array facts and rejection of installed aliases or forged
table history. Pure cycle/DAG checks remain separate; the baseline and preparations
retain0. At that cut, empty arrays at any depth, array warning/flag paths and objects
remain Unsupported; variable payloads retain structural authority.
[Array-define ledger](coverage/semantics/dynamic-constant-array-review.json).
The 391-module composition over 0599 passes independent review at 9ce759fd;
accepted rules/protocol and parent operational paths are preserved.
No renewed actor/source/state evidence is claimed.

Direct MAIN warning-callback destructor exit now overrides a pending user
Throwable while retaining its owner through helper completion and caller-temporary
cleanup. Safe bool/decrement-null restore before parent cleanup; strings skip the
store. The internal exit releases its retained Throwable owner before shutdown;
last-owner destructor writes survive. Three new and one repaired original agree
at c54a/8852; three author fixtures pass 440 premises and the independent last-owner fixture
passes 170 (610 total). The original Unsupported baseline, compiler/interpreter
failures, diagnostic/preparation runs and stopped tiny reproducer retain zero
credit. Two equivalent list-prefix premises avoid a confirmed SpecTec structured
dispatch overlap without a vendor change. Admission requires a MAIN caller and
a direct destructor scope without local cells, held roots or owned pending operands.
Nested/outer contexts, parent/cause cleanup throws or exits, unsafe targets and
wider callbacks/control remain required.
[Pending-Throwable destructor-exit ledger](coverage/semantics/incdec-callback-destructor-exit-pending-review.json).
The 391-module join over 4767ec3bd preserves current output, class and cleanup
state. Current strict and the sole last-owner original pass at cc9e38c2f; private
source/state cuts retain their identities.

Module401 handles reference-warning throws before direct explicit output API
callback entry. One authenticated task releases the prepared scalar prefix, then
normalizes the original fci arguments and reuses undefined-result failure cleanup.
Three distinct originals agree at 35a9, including second-warning traces and warning
output without deprecation. Two reached fronts pass 106 physical premises (61 at e13,
45 at 4f; 16 shared setup), checking sole reference ownership, exact scalar contents,
retirement, readonly metadata, malformed certificates and fuel0 preservation.
The original Unsupported baseline, unreachable-phase fixture and same-cap memory
failures retain 0. The bounded retired fixture stops after its new ownership front;
full completion remains covered by the exact source. The superseded Module398 control is
retired without renewing old campaigns. Wider warning/exit/lifecycle paths remain
partial. The 391-module composition over fa7e9170 passes both builds, full
structuring and inventory. Private source/state cuts retain their original identities.
[Contract](docs/semantics/OUTPUT-HANDLERS.md),
[author evidence](coverage/semantics/output-reference-warning-author.json),
[independent review](coverage/semantics/output-reference-warning-review.json).

Boolean `case_insensitive=true` in primitive `define` now warns before registration
and keeps case-sensitive lookup. The original captured arguments survive the
handler. A handler may install the same name first; the outer call then emits the
duplicate warning and returns false, retaining the handler's binding. Two exact
sources and two public fronts/221 premises pass at aacc, including genuine handler
entry, original true at both resumes, inner-definition origin and post-callback
duplicate prefix. Baseline/native/preparation evidence retains0; wider domains and
callbacks remain partial.
[Ignored-flag ledger](coverage/semantics/dynamic-constant-flag-review.json).
The 390 composition over b88b passes independent pointwise review at 79abff45;
accepted runtime/protocol and parent hook/WeakMap paths are preserved.
No renewed actor/source/state evidence is claimed.

Primitive duplicate `define` now warns and returns false without replacing the
old binding. Retained dynamic selection survives a named warning callback that
appends another constant; false-handler fallback and handled delivery preserve
the table. Two exact sources and two public fronts/207 premises pass at a3c3.
The pre-warning prefix admits genuine appends but rejects later-only duplicate
keys, source/nonce and error-metadata forgeries. The unchanged baseline and native/
fixture preparations retain0; no raw projections or synthetic continuations are
credited. Wider values, owning calls and warning branches remain partial.
[Duplicate-define ledger](coverage/semantics/dynamic-constant-duplicate-review.json).
The 390 composition over 1b692 passes independent pointwise review at c8e6d7f39;
accepted runtime/protocol deltas and parent output paths are preserved.
No renewed actor/source/state evidence is claimed.

Module399 preserves a defined scalar output-handler return when callee cleanup
throws. Fixed by-reference wrappers belong only to the callee; entered methods
borrow their cached receiver. Normal-return certificates remain distinct from
body-throw null results, and API callee cleanup retains internal/API traces.
Seven author originals agree at separate cuts; two boundaries retain zero
agreement. Three independent originals agree at retained cuts. Four genuine
state groups pass 317 premises (64 at38e9,253 atd983), covering pre-ENTER site
validation, callee ownership, pending normal commit, unsealed body failure and
retired receiver refusal. Missing-pending task fallthrough was corrected without
changing generic validation. Original failures and bounded diagnostics remain
zero credit. The bounded milestone is independently accepted; full core remains
partial.
[Contract](docs/semantics/OUTPUT-HANDLERS.md),
[author evidence](coverage/semantics/output-result-cleanup-author.json),
[independent review](coverage/semantics/output-result-cleanup-review.json).
The 390-module composition over67022a7d passes pointwise review, both builds,
full structuring and inventory. Parent class/fatal/cancellation/WeakMap/constants
are preserved. The proposed WeakMap check stopped before output at its existing
named-key boundary with zero agreement; private source/state cuts were not replayed.

Module400 now executes scalar global `define`/`defined` through real argument
capture, namespace keys, retained dynamic selection and no-file dispatch. Actual
string carriers determine the stored class; later name/value CV changes preserve
the row. Four exact sources retain three at9356 and interned1 at8c27. Four public
fronts pass262 premises at8c27, including literal/selection/key/class/carrier and
metadata rejection. Variable-derived payloads keep the existing structural table
policy; no full past-input provenance is claimed. The baseline, two pre-runtime
failures, original recorder predicate and terminal-fixture failure retain0; direct
source acceptance adjudicates the same raw run. Wider values, warning/conversion
paths, namespace fallback and full constant/core behavior remain partial.
[Dynamic-constant ledger](coverage/semantics/dynamic-constants-review.json).
The 389-module composition over 99d2 passes independent pointwise review at 895b3ac9;
accepted code and parent selectors/pipeline are preserved. No renewed actor, source
or state evidence is claimed.

Exit from a raw invokable warning-handler destructor now returns through the real
release operation before helper completion. Safe bool/decrement-null captures
restore before caller-temporary cleanup; strings skip the store. Integer exit 17
replaces body exit 23, while string exit retains 23. Destructor registry changes and
weak retirement survive. That first cut requires no pending user Throwable, destructor
local cells or owned pending operands. Four new originals agree at cdc375d6d,
951ffe0e2 and a3f256992. Two author fixtures pass 240 conditions; independent
positive fixtures pass 247 and the pending-boundary fixture passes 66 (553 total).
Its pending control was Unsupported with zero agreement credit and stopped before
caller cleanup. Its driver handoff correction at 2cd6b6481 preserves the earlier
positive cuts; the original baseline, preflight/compile and fixture/driver failures
retain zero credit.
Nested destructor exits, owning cleanup,
unsafe targets and wider callbacks/control remain required; full core stays partial.
[Callback-destructor exit ledger](coverage/semantics/incdec-callback-destructor-exit-review.json).
The 388-module join over bbb9c5eab preserves current output, class and cleanup
state. Current strict and the sole bool/status-17 original pass at 91db163c1;
private source/state cuts retain their identities.

Deferred named user-class duplicates now drain a retained file fatal with the
current binding trace. The existing receipt records the real class site/cause/index;
captured-prefix index and journal replay reject omitted-entry extra records while
genuine no-record binding remains valid. Five runtime files and the protocol at
70270d8cd /387 retain two exact sources and two public fronts/165 premises at3258.
One raw step and one pure base activation projection stay separate from two production
continuations. The original mismatching baseline retains0; class activation helpers,
compiler publication, request schema/status rules and retention policy are unchanged.
Other class/fatal producers and formatter combinations remain partial.
[Class-drain ledger](coverage/semantics/source-recorded-class-fatal-review.json).
The 388-module composition over 04a9a231 passes independent pointwise review at
cd9cc619; accepted runtime deltas/protocol and parent output/class/WeakMap behavior
are preserved. No renewed actor/source/state evidence is claimed.

Module398 implements explicit output API reception failures and callback throws.
Arguments release while running; clean discards live bytes, flush restores its
upper, and end/get pop before lower routing and sole callback-owner release.
Frozen getters stay owned while pending Throwables interrupt assignment. Actual
replacement/Previous and saved/cleared destructor exceptions retain API traces.
Eight author and three independent originals agree at separate cuts. Three
reached state groups pass 202 premises (117 at6dc,85 at4f2a). Site-only trace
classification and optional-caller replay matching were corrected narrowly;
original failures and bounded diagnostics retain zero credit. The bounded private
milestone is independently accepted. The 388-module composition over6b203c519
passes pointwise review, both builds, full structuring and the inventory check.
Parent fatal/cancellation/WeakMap/cast behavior is preserved; no renewed numeric
source/state evidence is claimed.
[Contract](docs/semantics/OUTPUT-HANDLERS.md),
[author evidence](coverage/semantics/output-api-failure-author.json),
[independent review](coverage/semantics/output-api-failure-review.json).
Callback exit, wider warning-handler throws, other producers/request-end/fatal drains
and wider protocols remain required; full core stays partial. Module399 extends
the bounded scalar normal-result cleanup path above.

Handler-local destructor Throwables now cancel exit from owning invokable warning
callbacks. The supplied pending Throwable survives selected-receiver and raw-handler
release before bool/decrement-null capture restoration; strings skip the store.
The single registry decision, surviving owners, secondary Previous chain and real
caller catch/finally are preserved, including request status 23 and late-peer detach.
Five new originals agree at retained 1fd8/f352 cuts. Three author SL fixtures pass
383 conditions and two independent fixtures pass 264 (647 total). The original
Unsupported baseline and native/preparation runs retain zero credit.
Broader callback-destructor exits, unsafe targets and wider callbacks/control
remain required; full core stays partial.
[Callback-local cancellation ledger](coverage/semantics/incdec-callback-exit-cancellation-review.json).
The 387-module join over 0186877ee preserves current shared cleanup and output
state. Current strict and the sole secondary-throw/borrowed-cell original pass at
350237d11; private source/state cuts retain their identities.

Deferred runtime function redeclaration now drains a retained file fatal with the
current binding trace. Its receipt records the actual function site/call cause/index;
historical bindings reconstruct the raw failure. Captured-prefix index replay and
exact replayed-journal equality reject both shortened extra records while keeping
genuine no-record binding valid. Five runtime files/protocol at edbc95f71 /386 retain
two exact sources at302a and two public fronts/157 premises at69fc. One raw step and
one pure binding projection stay separate from two production continuations.
Baseline, two original public failures and eval preparation failure retain0.
Other producers/formatter combinations remain required; full core stays partial.
[Function-drain ledger](coverage/semantics/source-recorded-function-fatal-review.json).
The 387-module composition over 96f29b4f passes independent pointwise review at
f2b4d9ce; accepted runtime/protocol and parent WeakMap/output/callback/type behavior
are preserved. No renewed actor/source/state evidence is claimed.

Owning invokable warning callbacks now release their selected receiver and raw
handler before the inc/dec helper finishes. The saved handler returns to the
registry or is released once; replacement/clearing by its destructor survives. Bool/decrement-null
restore their safe capture afterward, while strings skip the store. Real callback
owners prevent premature destruction; a supplied Throwable from the callback destructor
cancels exit into caller catch/finally without changing request status 23.
Seven new and one repaired source agree at 2bc9/34c8. Three author SL fixtures
pass 299 conditions and three independent fixtures pass 269 (568 total).
The original Unsupported baseline and pre-runtime compile failure retain zero credit.
Unsafe targets, wider callbacks/control and broader callback-destructor exits
remain required; full core stays partial.
[Callback-exit ledger](coverage/semantics/incdec-callback-exit-review.json).
The 387-module join over 70f124b2 preserves current output/fatal/class state and
cleanup validation. Current strict and the sole int23 owner-throw original pass at
ee074563e; private source/state cuts retain their identities.

Module397 remains integrated at6f7e99f6/387; its eight author/four independent
originals and three groups/166 retain their original cuts without replay.
[Accepted ledger](coverage/semantics/output-abrupt-review.json).

Fixed-name `trigger_error`/`user_error` with `E_USER_ERROR` now drains a retained
file-compiler fatal before handler selection, delivering the cached message/location
with the current callback trace. Its own runtime receipt consumes the index and
authenticates both saved fatal records. Five runtime modules and the maintained
protocol at 2a863d1c0 /386 retain two exact sources and one genuine public front/117
premises at a9c7. One raw projection is separate from production starting at the
genuine prestate. Dynamic selection stays explicitly Unsupported0; baseline,
signature-order and original fixture-syntax failures retain0. Owning forms, other
fatal producers and wider queues remain required; full core stays partial.
[Runtime-drain ledger](coverage/semantics/source-recorded-runtime-fatal-review.json).
The386 composition over27a92 passes independent pointwise review at a9821407;
accepted runtime deltas/protocol and parent cancellation/WeakMap paths are preserved.
No renewed actor/source/state evidence is claimed.

Caller-temporary cleanup Throwables now cancel a named inc/dec warning-handler
exit after the warning helper finishes: bool/null restore their capture while
strings skip the store. Authentic main/function catch/finally resumes without
reviving retired operands or a previous finally exception. Post-commit writes and
request status23 survive; nested binary operands retire in source lifetime order.
Seven new and one repaired original agree at retained cuts. Three author SL fixtures
pass 342 conditions and three independent fixtures pass 341 (683 total). The original
Unsupported baseline, reversed-order failure and fixture/launcher failures retain zero credit.
Unsafe targets, wider owning holders and unmodeled enclosing control remain
required; callback ownership is covered by the current bounded milestone. Full
core stays partial.
[Parent cancellation ledger](coverage/semantics/incdec-parent-exit-cancellation-review.json).
The 386-module join over cbc57 preserves current output/compile/fatal state and
operation validation. Current strict and the sole two-retired original pass at
63e5dd8df; earlier source/state cuts retain their original identities.

Nonfatal runtime diagnostics now skip handler/default delivery while a genuine
file-compiler fatal receipt remains retained. Trigger_error returns true and an
undefined-variable read yields null; the new receipt branch excludes fatal-mask errors.
Module236 and its maintained protocol at 3f28d7ddc /385 retain three exact source
tuples and two public fronts/185 premises at 571d3211. No raw projections or ownership/lifetime
changes; baseline and the original typed-subtraction fixture failure remain0.
Other recorded runtime fatal producers, E_DONT_BAIL and broader diagnostic/formatter queues stay partial.
[Recorded-warning ledger](coverage/semantics/source-recorded-warning-review.json).
The386 composition over eeb6a7bb passes independent pointwise review at efc0d7147;
accepted236/protocol and parent output/public/comparison behavior are preserved.
No renewed actor/source/state evidence is claimed.

Module396 normal positive chunks remain integrated at fdf9903d/386. Its eight author,
five independent originals and five groups/210 retain their cuts, including the
current-parent live destructor EXIT/typed callback gate45 over cb498.
[Accepted ledger](coverage/semantics/output-chunk-review.json).

Module395 explicit chunk0 normal callbacks remain integrated. Its frozen source
and state cuts, including the 385-module busy-lower repair with one source and
49 state premises, are retained
without replay in [the accepted ledger](coverage/semantics/output-handler-review.json).

Dynamic file compiler FATAL now retains its recorded diagnostic across bailout.
Later file/eval compiler fatals drain that tuple with the current trace while
retaining the actual new cutoff. Own receipts authenticate both abandoned records;
stale extra, raw/origin/index forgeries are rejected. b98bc436e /385 retains four
exact source tuples and one genuine public group109 atc1127. No raw projections,
lifetime or opened-membership changes; original native expectation failure,
baselines/diagnostics and model14 pre-runtime failure remain0. Wider recorded
runtime errors/compiler/formatter combinations stay partial.
[Recorded-fatal ledger](coverage/semantics/source-recorded-fatal-review.json).
The385 composition overa377 passes independent pointwise review at6659a8b89;
accepted runtime/protocol and newer parent behavior are preserved.
No renewed actor/source/state evidence is claimed.

Redeclaration compiler fatals now admit fresh shutdown eval/file sources through
full declaration-history authentication. Current waiting contexts, completion and
reporting stay separate from the saved failed prefix/raw snapshot and source owner.
Module270/protocol86611341e /384 keeps four exact source tuples and two genuine
public groups/218 premises at28138624. No raw projections or lifetime policy changes;
original baseline, lookup diagnostics and fixture-name failure retain zero credit.
Wider compiler/fatal/source lifecycle remains partial.
[Redeclaration-fatal ledger](coverage/semantics/source-redeclare-fatal-review.json).
The385 composition overa058d76c passes independent pointwise review at37136e422;
accepted compiler-proof delta/protocol and parent OP06/395/M41/class behavior are preserved.
No renewed actor/source/state evidence is claimed.

Handler-local cleanup Throwables now cancel named inc/dec warning-handler exit,
restore safe captured bool/decrement-null values (strings retain writes), and resume
real caller catch/finally without delivering the interrupted result. Supplied identity,
Previous null, live aliases, fresh nested registry and request status23 are preserved.
Seven new and one repaired earlier original agree at 5887/f2a/66cb. Three author
fixtures pass 240 conditions and three independent fixtures pass 259 (499 total). The original
Unsupported baseline and native/preparation-only records retain zero credit; older
campaigns are unchanged. Owning callbacks and unsafe targets remain required;
parent cleanup cancellation is covered by the current milestone. Full core stays partial.
[Cancellation ledger](coverage/semantics/incdec-exit-cancellation-review.json).
The 385-module join over c8aa passes current strict SL and one exact parent-owner
original at 24dba6266; earlier source/state cuts retain their identities.

Named inc/dec warning-handler exits now finish handler-local cleanup and registry
restoration before bool/decrement-null commit; strings skip restoration. Caller
temporaries remain alive until that commit, then cleanup precedes shutdown.
Kept borrowed cells, GLOBALS unset, nested handlers and integer exit status 23
retain their native observations. Eleven new and one repaired earlier original
agree at separate cuts; three named Unsupported controls have zero agreement.
Three author SL fixtures pass 203 conditions at 93c and four independent fixtures
pass 245 at 96b7 (448 total), including normal/pending parent cleanup validation,
source/metadata negatives and public budget resume. Original baseline, status-label
and descriptor failures remain zero credit; older campaigns are not renewed.
Owning callback release and cleanup throws that cancel exit remain required next
continuations, alongside replacement/destructor exit and wider update locations.
[Exit ledger](coverage/semantics/incdec-exit-review.json).
The 384-module join over 214ae passes strict SL (6.421s) and the sole parent-throw
source control at 4f935, preserving fatal-status and aggregate394 behavior. The
control remains zero agreement; earlier private cuts retain their revisions.

Frozen fatal completion now observes request status after caught shutdown-exit
replacement, retaining diagnostics while callbacks continue. Fresh fatal reporting
writes255 in both display branches; frozen passthrough preserves resets.
Three-line231/observer and protocol3a517483e /383 retain six exact source tuples
and three public fronts/133 premises at paired207947da. No raw projections or
old lifecycle/guard renewals are claimed. Original baseline/diagnostic and
fixture compiler failure remain0; wider fatal/lifecycle work stays partial.
[Fatal-observer ledger](coverage/semantics/source-static-fatal-observer-review.json).
The384 composition over7d4fb passes independent pointwise review at78c7ff03;
accepted runtime/protocol and parent M40/394/pipeline bytes are preserved.
No renewed actor/source/state evidence is claimed.

Recursive array and declared-property Stringable/string comparisons now suspend
at the reached leaf through 394. Real aggregate pins preserve array copy-on-write;
live slots and captured cells stay distinct, and the active left recursion guard
survives caster entry. Successive casts, nested recursion Error and TypeError
catch/finally entry pass at b28d9 /383: six exact source agreements and 521 reached
premises, including 48 pure controls and 31 raw PhpSteps; strict 3 passes.
Original baseline, pre-main and fixture-selector failures retain zero credit.
The [property-table increment](coverage/semantics/materialized-stringable-comparison-review.json)
passes six new exact sources, strict 3 and 576 reached premises/28 raw steps at
447859 /384. stdClass owns both objects and concrete tables, keeping old dynamic
buckets under COW; genuine foreach-produced declared tables use live slots and
captured cells. Identical tables precede recursion checks, and throw/normal return
remove the guard. Ordinary `(array)` views remain copied projections. Mixed
membership, guarded projection and wider lifetimes remained open at that cut;
full core stays partial. The disproved transition and original fixture/compiler
failures retain zero credit.
[Aggregate comparison ledger](coverage/semantics/aggregate-stringable-comparison-review.json).
The preceding [direct comparison increment](coverage/semantics/stringable-comparison-review.json)
retains its six sources and 487/26 state cut at aabff656 /381.

[Fiber comparison transfers](coverage/semantics/fiber-aggregate-stringable-comparison-review.json)
now retain aggregate recursion guards in source-authenticated waiting and suspended
VMs without adding roots. Waiting-array COW, resumed declared live slots versus
captured cells, and the identical injected TypeError through caster/caller finally
entry pass at f536e6ea /385: three exact sources, strict 3 and 315 reached premises
(292 setup/frontier, 23 pure controls, 23 raw PhpSteps). The original peer EL recorder
label failure keeps zero runtime credit; its genuine closed elaboration is reused.
That cut left mixed tables and guarded projection open; broader close/destructor
lifetimes remain required.

[Mixed cached-table comparison](coverage/semantics/mixed-property-stringable-comparison-review.json)
now retains concrete old table generations with live declared-slot locators while
dynamic writes produce copied buckets. Actual foreach and array views can differ
from later property reads. Six original sources agree across the retained fa6f/468275
cuts; 743 reached premises (676 setup, 67 pure controls, 37 raw steps) pass at
468275 /386. Ordered skips, retained UNDEF, old/new guard identity and the same
TypeError through catch/finally are checked. Compiler3 is reused across the sole
same-object exclusivity guard. Original pre-main, timeout, nondeterminism and
cleanup-fixture failures retain zero credit. Cached clone/collector visitation and
copied-declared reference iteration remain open.

[Materialization under direct comparison](coverage/semantics/direct-table-comparison-review.json)
now leaves the captured direct cursor on declared inline slots while a nested
comparison creates and pins actual tables under an independent guard. Three exact
originals agree at 8d897ce /387; 383 reached premises (361 setup,
22 pure controls, 26 raw steps) check one-sided/implicit materialization,
unequal newly added dynamic fields, live slot versus old cell and identical TypeError
through both caster finally blocks and caller catch/finally. Strict 4 passes; the original
pre-main fixture failure retains zero credit. Existing GC/clone/reference-iteration/
lifetime limits remain open.

[Fast projections under direct comparison](coverage/semantics/direct-projection-comparison-review.json)
now export copied property arrays while preserving the original inline cursor and
object guard, without creating cached tables. Singleton reference wrappers unwrap;
retained shared cells stay live in the view. Three original sources agree at
04743e74 /388. Author and independent states pass 503 reached premises
(483 setup, 20 pure controls, 35 raw steps), covering actual cast allocation,
reference owners, independent array recursion and identical TypeError through both
caster finally blocks and caller catch/finally. Strict initialization and syntax-only
preparation add no semantic credit; the original grouping fixture failure remains zero.

[Stringable comparison redispatch](coverage/semantics/stringable-redispatch-comparison-review.json)
now handles an opposing live CV/cell/property becoming another ordinary Stringable.
The second cast compares against the saved first string in original order; aggregate
parents/guards persist until leaf completion or unwind. Four exact originals agree
at 7431f462 /388. Author and independent states pass 531 Boolean premises
(509 setup, 22 pure controls, 32 raw steps), covering saved text after receiver
retirement, unequal short-circuit, old-cell/case resumption and identical TypeError
through finally/caller cleanup. Initialization, syntax preparation, diagnostic and
original fixture failures add zero runtime credit. Wider object handlers and
receiver/destructor lifetimes remain open.

[Finite Throwable string comparisons](coverage/semantics/throwable-string-comparison-review.json)
now update the root cache at reached builtin/inherited leaves and after a source
cast changes an opposing CV/cell. Previous-node overrides are ignored; count/key/
earlier-value skips stay cold. Three exact originals and 278 Boolean premises
(254 setup, 24 pure controls, 8 raw steps) pass at 42ae18da /390. Initialization,
syntax preparation and original preparation/fixture failures add zero runtime
credit. Callback-valued fields, cyclic previous chains and active object-guard
overlap remain explicit Unsupported. Wider handler and lifetime behavior remains open.

Hard bailout now records request EXITSTATUS255 before shutdown. Direct callback
strings preserve it; integer/default exits replace it and skip later callbacks.
One-line257 and protocol20db1b23e /382 retain four exact source tuples and three
public groups/238 premises at the single6c91c81d cut. Three raw exit projections
stay separate from three production fatal and final-exit continuations; the
original exit0/native255 baseline remains0. Static roots/destructor policy are
unchanged. Its later frozen-completion observation is recorded above.
[Fatal-status ledger](coverage/semantics/source-static-fatal-status-review.json).
The383 composition over2676 passes independent pointwise review at0f51a247;
parent ticks/WeakMap behavior is preserved. No renewed source/state evidence.

Ticks393 is independently accepted; its current383 composition is checked.
Source-derived
marker plans cover lexical frequencies, compiler adjacency/control and certified
callback lines; the live registry retains arguments, supports mutation and keeps
calling/Fiber restrictions through post-return destruction. Author26 distinct
originals agree at retained21+5 cuts, with3 Unsupported controls; the earlier
TATBT original retains its own cut. Independent16 originals and3 controls pass
at separate4+3+3+6 cuts, including cached-receiver release on normal/throw/exit.
Seven genuine state groups pass334 premises at6/269+1/65 cuts; the hold fixture
waits until the queued alias decrement finishes. Failed whole campaigns retain
zero credit. Wider placement and callable dependencies remain explicit.
[Contract](docs/semantics/TICKS.md), [author evidence](coverage/semantics/tick-author.json),
[independent review](coverage/semantics/tick-review.json).
The383 join over557fc63 preserves parent exit status and source-frame cleanup;
one new exact AHDZ eval-static/post-return original passes at3c02667e3.
Earlier source/state cuts retain their identities.

Parser-backed USERFATAL now captures its actual eval/file location and retires
execution contexts through an authenticated fatal snapshot. Static cells retain
their existing bailout roots, allowing fresh shutdown evals while interrupted
objects remain alive. Historical origin/END and false-handler-result forgeries
are rejected; destructor flags/table ownership reuse their existing policy.
Private a31b12ffc /381 keeps seven exact source tuples at1+6 cuts and three
public groups/281 premises at210+71 cuts. Three raw projections remain separate
from three production fatal transitions; original failures/diagnostics remain0.
Wider fatal/compiler producers and lifecycle/return cleanup stay partial.
[Source-static fatal ledger](coverage/semantics/source-static-fatal-review.json).
The382 composition over1fe8fae6 passes independent pointwise review at3a4b0921;
accepted runtime/protocol bytes and all newer parent behavior are preserved.
No renewed actor/source/state evidence is claimed.

Module390 now releases callback-installed object/array payloads before captured
inc/dec scalar commit. Destructors see the old slot; scalar writes are overwritten
afterward, while pending/replacement Throwables preserve identity and Previous.
Real aliases keep nonlast objects alive, and callback wrappers detach without
adding borrowed owners. Ten author and ten independent new originals agree at
retained cuts; four earlier restoration controls now agree separately. Eleven
author SL fixtures pass 893 conditions, the changed earlier fixture passes 54,
and four independent fixtures pass 290 (1,237 total). Five Unsupported source
controls receive zero agreement. Original baseline, wrapper-option and two isset
failures remain preserved; unselected native repetitions receive no source credit.
Late typed sources, destructor ownership changes, exit, ordinary/nested/empty
released-array reads and wider update locations remain required.
[Restoration ledger](coverage/semantics/incdec-restoration-review.json).
The 382-module join over 69ff passes strict SL (6.256s) and one exact both-throw
destructor original at 3d1dcba90; earlier source/state cuts keep their revisions.

Caught source-static destructor exceptions now keep user execution through caller
catch and remaining-slot release, preserving Previous without treating exit as a
Throwable. Request signed32 EXITSTATUS survives caught replacement; integer/default
exit updates it, strings retain it, and nested resets remain independent of saved
exit control. Private owner1e3067/380 keeps three exact originals and325 public
premises; status3d8014372/381 keeps seven exact originals and150 new premises.
Five fronts/475 premises,12 raw steps and four production table drops retain their
separate cuts; original baseline/fixture failures remain0. Hard-fatal shutdown
roots and wider lifecycle work remain required; full core stays partial.
[Source-static status ledger](coverage/semantics/source-static-exit-status-review.json).
The381 composition overf59 passes independent pointwise review atdf505395,
with accepted runtime/protocol bytes unchanged and parent382/386/391 preserved.
No new actor or source/state credit is claimed.

Default output buffers391 now route exact echo/print/inline/exit/direct-call bytes
through nested NULL handlers, whole chunks, capabilities, copied get results,
Notice-handler reentry and exact status. Forced flush follows shutdown/destructors;
BUDGET and Unsupported preserve buffers. Buffered stdout diagnostics and wider
handler dispatch remain dependencies; Module395 adds explicit user operations above. Author26 originals agree at
identical1+25 cuts, with4 Unsupported controls; independent6 originals/2 controls
and SL5 groups177 premises pass separately. Original compiler/PRINT/fixture
failures retain zero credit. [Contract](docs/semantics/OUTPUT-BUFFERS.md),
[author evidence](coverage/semantics/output-buffer-author.json),
[independent review](coverage/semantics/output-buffer-review.json). Private review
is accepted; the381 composition over2f15e222 passes current strict SL and one
exact AED1S1 buffered eval-static/string-exit/destructor/shutdown original at
894561c42, preserving390 warning-exit guards. Earlier cuts retain their identities;
full core stays partial.

Graceful exit now retires parser-backed static tables before shutdown through
real callee restoration and source-frame steps. Nested eval/file order, saved
destructor parser reentry and escaped references retain their owners. At private
69dcc8d30 / 377, fourteen exact exit originals and one retained notice control
agree at separate cuts. Six genuine fronts pass 950 public/ownership premises,
with 24 raw PhpSteps separate from six production table drops and one callee
restoration. Original parser/fixture failures retain zero failed-group credit.
Hard-fatal shutdown roots and wider lifecycle work remain required; full core
stays partial. Caught destructor status now has the separate extension above.
[Source-static exit ledger](coverage/semantics/source-static-exit-review.json).
The 380 composition over7d694efd passes one exact destructor-reentry source
and72 saved parser/exit ownership premises at a974afec0, retaining390
warning-exit refusal. Earlier source/state cuts keep their revisions.

Module390 resumes direct defined untyped-CV pre/post inc/dec warnings. Bool/null
restore captured values after returning or throwing handlers; strings restore
only after normal handling. Borrowed old cells and callback-created wrappers keep
their distinct writes and owners. Author 50 and independent 28 ordinary originals
agree at retained cuts; eight explicit Unsupported controls receive zero agreement.
Nine author SL fixtures pass 539 conditions at 585/9c and three independent fixtures
pass 155 at 585, including genuine throw roots, alias detachment, fresh nested
registry selection and budget resume. Original fixture failures retain zero failed-group
credit. The earlier warning cuts remain distinct from the restoration extension;
late typed sources, exit and wider locations stay partial.
[Inc/dec warning ledger](coverage/semantics/incdec-warning-review.json).
The 380-module join over f12 passes strict SL (6.121s) and the affected
GLOBALS-unset callback original at 0b564; earlier source/state cuts retain their revisions.

Backtick command construction and finite shell dispatch are implemented in389.
Compiler deprecation, root-builtin lookup, Stringable/array/undefined interpolation,
empty/NUL errors with builtin traces, exact byte/null results and real pipe-failure
handlers are covered. Shell requests authenticate source, nonce, converted command,
post-interpolation CWD and ordered raw environment; missing/forged/replayed facts
remain Unsupported. Author20 source cases retain separate18+2 cuts and original
warning-dispatch failure0; SL11 groups/823 premises pass. Independent4 source
interactions and3 Unsupported controls are accepted at their separate cuts. [Contract](docs/semantics/SHELL-DISPATCH.md),
[author evidence](coverage/semantics/shell-dispatch-author.json),
[independent review](coverage/semantics/shell-dispatch-review.json).
The 379-module join over3faec9e passes the exact VDE eval-static retirement
source and the warning-handler SL group/128 premises at54f60dde. The original
ED expectation mismatch stays0; private source/state cuts retain their identities.

Eval/file top-level static tables now retire before body exceptions cross to
caller catch. Pending Throwables remain rooted through real destructor operations;
replacement exceptions retain Previous, and normal-end destructor throws still
release remaining slots in declaration order. Nested source tables and escaped
references retain their separate owners. At private 87864cc3c / 377, eight exact
originals agree; four genuine groups pass 466 public/ownership premises, with
12 raw PhpSteps and four production-drop continuations kept separate. Original
recorder and broad-seek fixture failures retain zero failed-group credit.
Hard-fatal shutdown roots and wider destructor/return interactions remain
required; the separate graceful-exit extension is recorded above.
[Source-static throw ledger](coverage/semantics/source-static-throw-review.json).
The 378 composition over acaee66fa passes one exact destructor-override source
and 116 public/pending-root premises at 6d568f59c. Earlier source/state cuts
retain their original revisions.

Top-level eval/file statics now stay separate from a real Closure caller's
instance table. Each source unit retains its cached cell, later units allocate
fresh cells, and escaped references survive normal source-table retirement.
Caller captures, scope metadata and own statics remain intact; nested evals
keep separate source tables. At private 93d2abdb1 / 377, one affected and five
independent exact originals agree; three genuine groups pass 360 public/ownership
premises and 16 explicit boundary PhpSteps. The original Closure/parser refusal
remains zero credit. Hard-fatal and wider destructor/return cleanup remain
required; graceful-exit validation stays separate above.
[Source-static identity ledger](coverage/semantics/source-static-identity-review.json).
The 378 composition over e0668aabe passes one exact cache/reference source and
118 public ownership premises at 3b9c3cd26. Earlier source/state cuts retain
their original revisions.

Integer operators now retain evaluated literal/unary/ternary copies and owning
reference-assignment/named byref-call results through conversion callbacks.
Bitwise operations preserve source evaluation but convert in Zend's physical
CONST/TMP/VAR/CV order, including array-first failure before a float warning.
The 37 source cases retain their unchanged 2/14 and corrected 21 cuts; 11 author
SL fixtures and one independent shared-cell fixture pass 714 conditions
(657 author, 57 independent) at 197c/377. The
[COPY ledger](coverage/semantics/integer-operator-copy-review.json) records
actual temporary roots, captured conversions and preserved baseline/mismatch
failures. Wider bitwise producer classes, objects and expired borrowed pointers
remain open; no reference-return producer semantics changed.
The 378-module join over e208 passes strict SL at ae107 (6.046s); private
source/state cuts retain their recorded revisions without renewal.

Parser-backed top-level statics now authenticate source ownership and release
normal/explicit-return slots in compiler declaration order. Callable slots,
escaped aliases and copied return operands keep their existing roots. The
second eval-response refusal is repaired without relaxing parser/public guards.
At private 19b999682 / 377, four exact checked originals retain their source cuts;
11 genuine frontiers pass 382 premises and 12 explicit boundary PhpSteps.
Original parser, model and fixture failures retain zero failed-group credit.
Hard-fatal shutdown roots and wider destructor/return interactions remain
required; the separate graceful-exit extension is recorded above.
[Source-static ledger](coverage/semantics/source-static-retirement-review.json).
The 378 composition over a6fdf13c passes one exact returned-object source and
34 public copied-return premises at 32670dbed. Earlier source/state cuts retain
their original revisions.

Opened-file identity now follows recorded compiler diagnostics: ordinary
include/require registers afterward, while once forms register before compilation.
Nested handlers, shared throws, graceful exit and hard bailout retain native
ordering and cleanup. Twenty-one authored originals and four independent originals
agree at their retained cuts. Eight reached frontiers pass 263 premises and seven
explicit boundary PhpSteps, including public rejection of forged notice owners.
Replay validates diagnostics without invoking the live handler; `trigger_error`
accepts authentic string carriers. Original source/fixture failures retain zero
failed-group credit. Wider source/provider contexts and Stringable/null message
conversion remain required; full core stays partial.
[File compiler-notice ledger](coverage/semantics/file-compile-notice-review.json).
The 376 composition over 804fe189 passes one exact repeated-exit source and
41 public exit-frontier premises with full SL admission at b9dfa5def.
Earlier source/state cuts retain their original revisions.

Module387 stages scalar integer conversion warnings for `%`, shifts and mixed
bitwise operations with two defined direct CV operands. It retains captured
numbers and string spelling while callbacks mutate/rebind operands; `%`/shifts
select the RHS referent after left conversion, and bitwise operations borrow it
before conversion. Returning/throwing handlers, fresh registry selection and
source lines are checked. Author source4 and independent source30 retain their
separate cuts; author5 production-SL state fixtures pass304 premises and independent3
pass174. The [ledger](coverage/semantics/integer-operator-warning-review.json) records
their revisions and raw evidence.
Fixture parser/elaboration failures and AL-only observations have zero credit.
Wider producers and object conversions remain open beyond the COPY increment;
genuinely expired pointers stay Unsupported. Six callback-unset native originals crashed
with signal11 and receive no agreement or engine-cause claim.
The 377 composition over c5e88ccc passes strict3 at 7a0567247 (6.022s),
preserving parent error-handler, property/WeakMap and return guards. Prior
source/state evidence retains its original revisions without renewal.

Unknown literal `declare` names now compile ordered E_COMPILE_WARNING (128)
diagnostics with original spelling and the first item's line. Runtime no-op/body
work authenticates the source and enters PCFIELD1 children; compilation retains
enclosing EARLY. Two fresh eval originals agree at 713be74f4 /373:
strict3 (5.422s), ordered warning/default delivery, body warning2 and original
shared Throwable cleanup. Seven genuine PhpSteps pass 228 source-frontier/guard
checks plus six pure known-directive/nonliteral exclusions in 105/129 groups.
Type-only elab2 has zero runtime credit; the original compile Unsupported remains
zero agreement. Ticks, encoding, wider literal/body/publication and dynamic-source
interactions remain required; previous cuts and safety boundaries stay frozen.
The actual composition of 374 modules over fa678cc48 passes strict3 at
6ff4ac8d (5.474s), preserving canonical Fiber358 and property384 guards.
Private source2 / 228+6 checks retain their original cuts.
[Declare ledger](coverage/semantics/compiler-declare-review.json).

Exact named-function and static no-capture Closure factories now admit plain empty
named descendants in If/elseif/else branches beneath actual Do ancestry and body
Blocks. Three originals agree at 8ba686a6 /377 (strict3 6.074s), including selected
Do→If→While publication, reversed calls, retained Closure receivers and fresh
defaults. Author657 and independent211 pass 868 checks: 821 setup/frontier +47 pure,
with 36 genuine branch/publication/creation/allocation steps. Direct While hosts
beneath Do and wider guards remain Unsupported. The original baseline recorder
exit-label failure and peer fixture failures retain zero credit; the baseline's
checked-program Unsupported reason establishes the prior gap.
[Do-hosted If ledger](coverage/semantics/anonymous-do-if-rtd-review.json).

Exact noattr/noarg by-value untyped named functions and static no-capture Closure
assignments now admit plain empty named descendants in nested Do bodies through
existing Do host ancestry and body-Block chains. Three originals agree at
686cb43f /376 (strict3 6.126s), covering skipped outer hosts, reverse publication,
retained Closure receivers, lexical namespace and fresh defaults. Author543 and
independent159 pass 702 premises: 649 setup/frontier +53 pure, with 25 genuine Block,
publication, creation/capture, allocation and eligible no-op steps. Fixtures stop at
required allocations; syntax-only preparation/elaboration has zero runtime credit.
No executed COMP45 failures. Only the authenticated If-beneath-Do placement is now
superseded; direct While hosts beneath Do and wider factory guards remain Unsupported.
[Nested-Do ledger](coverage/semantics/anonymous-nested-do-rtd-review.json).
The [earlier While-hosted Do ledger](coverage/semantics/anonymous-while-do-rtd-review.json)
retains source3/state683 at 5a13bfe4 and its 5ff2413e/d02e5167 strict3 composition.
Only authenticated nested Do hosts supersede its placement exclusion; original cuts
remain frozen.

The [earlier If-hosted Do ledger](coverage/semantics/anonymous-conditional-do-rtd-review.json)
retains its source3/state841 and accepted WeakMap composition; only authenticated
direct While hosts supersede its Do-host exclusions. Original cuts remain frozen.

The [earlier Do body-Block ledger](coverage/semantics/anonymous-do-block-rtd-review.json)
retains source3/state690 at 9d2ca309; only authenticated conditional hosts supersede
its Do-host exclusions.
The 375 join over 75c2bdfc passes strict3 at 15c9705e (5.972s), checking
the shared getter task and Iterator snapshot record. Review preserves parentless
class linking and excludes the bool-typed __get/Iterator reception routes; private
cuts keep their original revisions.

The earlier direct-Do cut retains source3/state653 at 2ee1454b and its original
5306defe/75aaa60f composition reusing strict3 at tested 2ee1454b (5.974s), with
unchanged task/schema/manifest, reviewed bind/hook exclusions and reached parentless
linking. Historical body-Block negatives are superseded only for authenticated
Block chains; no old Do-control/fatal or private evidence replay.
[Direct-Do ledger](coverage/semantics/anonymous-do-rtd-review.json).

The earlier While-hosted If cut retains source3/state722 at df0ae18c and its original
zero-credit literal-list elaboration failure. Its 375 composition at de256ec9 over
07af20a3 reuses strict3 at tested df0ae18c (6.122s), with unchanged task/schema/manifest,
reviewed reference-notice/bind/getter/hook/collector/Iterator exclusions and reached
parentless class-link identity. No current actor or private replay is claimed.
Historical Do negatives are superseded only for authenticated direct bodies;
other original cuts stay frozen.
[While-hosted If ledger](coverage/semantics/anonymous-while-if-rtd-review.json).

The earlier nested-While cut retains source3/state636 at 8089eb5f and its
fb295c7c/c40c6f57 strict3 join (5.976s), including the shared task datatype and
reviewed parentless class linking. Historical If-inside-While negatives are superseded
only for authenticated mixed ancestry; all original cuts remain frozen without replay.
[Nested-While ledger](coverage/semantics/anonymous-nested-while-rtd-review.json).

The earlier If-hosted While cut retains source3/state887 at 376de1e1 and its
zero-credit Else-union elaboration failure. Its 375 composition at aa241bdf over
1867decf reuses strict3 at tested 376de1e1 (6.226s), with unchanged task/schema/manifest
and reviewed hook/finally/bind/collector/Iterator exclusions; reached parentless
class linking stays identity. No current actor or private replay is claimed.
Historical nested-While negatives are superseded only for actual While/Block ancestry.
[If-hosted While ledger](coverage/semantics/anonymous-conditional-while-rtd-review.json).

The earlier body-Block cut retains source3/state738 at 35adca9a. Its 375
composition at ac329f66 over 772760f0 reuses strict3 at tested
35adca9a (6.125s), with unchanged task/schema/manifest and reviewed exclusion of
the parent by-reference finally, first-class bind and Iterator-unpack routes.
No current actor or private replay is claimed. Historical conditional-While
negatives are superseded only for authenticated If ancestry; other cuts remain frozen.
[While body-Block ledger](coverage/semantics/anonymous-while-block-rtd-review.json).

The earlier direct-While cut retains source4/state1007 at ff82bb60 and its
1c0ffdae/30a22375 strict3 join (5.925s), including loop selection and same-source
second-iteration fatal before any factory body call in that probe. Historical body-Block
negatives are superseded only for authenticated Block chains; no replay.
[While ledger](coverage/semantics/anonymous-while-factory-rtd-review.json).

The earlier nested-host cut retains source3/state882 and its 75edad90/f37653ce
composition reusing strict3 at tested 4ea0db1d (5.972s), without a current actor
or private replay. Historical loop exclusions are superseded only for authentic
direct While bodies; other original cuts remain frozen.
[Nested-host ledger](coverage/semantics/anonymous-nested-branch-rtd-review.json).

The earlier branch-body Block cut retains source3/state784 and its original
revisions, including the ae8b65a9/d3beefe6 strict join. Historical nested-If
negatives are superseded only for authenticated nested hosts, without replay.
[Branch-body Block ledger](coverage/semantics/anonymous-branch-block-rtd-review.json).

The earlier Block-host cut retains source3/state737, its three zero-credit failures
and all original cuts. Its 431dacbd/c35c223e join reuses strict3 at tested 5d91ff5f
(5.922s) after independent guarded-route review, with no current actor or replay.
Historical Blocks-after-If negatives are superseded only for authenticated branch-body
Block chains; nested If/loop/factory exclusions remain.
[Block-host ledger](coverage/semantics/anonymous-block-branch-rtd-review.json).

The earlier conditional-Closure cut retains source3/state577 at 80a2707, its
original peer type-elaboration failure0 and all original cuts. Historical Block-hosted
If negatives are superseded only for the new source-authenticated host ancestry.
Its 375 join over 4b13f151 passes strict3 at 7983239b (5.925s); independent review
preserves the reached parentless class-link identity without private replay.
[Conditional-Closure ledger](coverage/semantics/anonymous-conditional-closure-rtd-review.json).

The earlier branch-function cut retains source4/state665 at d66d951a, selected
case-insensitive same-name callable origins and both original fixture failures0.
Its 375 join over a123a1a5 passes strict3 at 8bde7b9d (5.925s); independent review
preserves the reached parentless class-link identity. Historical conditional-Closure
admission negatives are superseded only for the new direct forms, at their original
cut without replay. Private native/source/state records retain their revisions.
[Branch-factory ledger](coverage/semantics/anonymous-branch-factory-rtd-review.json).

The earlier direct-main cut retains source4/state578 at 9386d628, duplicate executed
callable fatal before either body runs, and its original parser failure with zero
credit. The fatal frontier preserves all class/object/allocation state; it makes no
shutdown cleanup claim. Its 375 join over 8087545b passes strict3 at 78decf21
(5.875s), including shared task structuring and scalar-echo guard compatibility. Private source/state cuts
retain their original revisions; no accepted evidence was replayed.
[Conditional-factory ledger](coverage/semantics/anonymous-conditional-factory-rtd-review.json).

The earlier Block-Closure cut retains source3/state539 at 6e5f5075, with 18 actual
steps for Block entry, Closure creation/capture, named publication, eligible class
no-op and anonymous allocation. Its 375 join over 92f726a3 passes strict3 at
fbacca7a (5.976s), including the shared task datatype and scalar-echo guard
compatibility. Private cuts retain their revisions; no source/state replay was
needed. The historical28 Block-Closure exclusion is superseded, while
conditional/loop/nested assignments remain required.
[Block-Closure ledger](coverage/semantics/anonymous-block-closure-rtd-review.json).
The earlier [direct-Closure cut](coverage/semantics/anonymous-named-closure-rtd-review.json)
retains source4/state539, fatal redeclaration and both zero-credit fixture failures
at 058; its c4a942ec/096e strict join and all private cuts remain unchanged.

Named-function factories retain callable-before-Block and eligible function no-op
behavior. Their source3/state424 at 55dc and d176816f/0d53475a composition reuse
the tested strict3 after independent retired-slot/ordinary-binary compatibility
review, with no replay. The historical26 Block-function exclusion is superseded;
its original direct-factory source/state388 and 684ff104/9ae join remain unchanged.
[Block-factory ledger](coverage/semantics/anonymous-block-factory-rtd-review.json);
[earlier named-factory ledger](coverage/semantics/anonymous-named-factory-rtd-review.json).

The earlier namespace cuts retain qualified early root/block cost0, deferred cost1,
repeated unbracketed sections and lexical method namespaces. Their source3/state392
and both fixture failures keep their original cuts; historical style1 exclusion is
superseded by positive named/negative ABSENT-style1 controls.
Their375 join over 4fa216264 passes strict3 at e95aa8ce (5.922s); private
native/source/state cuts retain their original revisions.
[Unbracketed ledger](coverage/semantics/anonymous-unbracketed-rtd-review.json).
The earlier [bracketed cut](coverage/semantics/anonymous-namespace-rtd-review.json)
retains native/source3/state305 and its 375 join over 1dd6e543 at a219a473; its historical
style1 exclusion is superseded by the new positive/ABSENT-style1 controls.

Standalone global blocks now preserve early class binding through each actual
block ancestor; nested conditional blocks remain deferred. Three fresh originals
agree at 7f52ed18 /375 (strict3 5.624s), including prior deferred same-name classes,
pre-declaration allocation and case-insensitive name retention. Author172 and
independent87 pass 259 checks: 230 setup/source-frontier premises and 29 pure
queries, with 12 actual PhpSteps for block entry, exact early no-op, publication
and anonymous allocation. Eligible named root-block classes cost0; deferred named
classes cost1 even when never published. A same-shaped do-body path is rejected by checking
the actual ancestor. Syntax-only preparation/elaboration adds no runtime credit.
The missing retained-tool alias stopped before execution and retains zero credit;
repaired exercised tools match accepted binaries. At that cut, namespaces/functions/Closures,
wider named declarations and RTD ordering remain required. Actual375 over
651c4a5d passes strict3 at 4263f24e (5.625s); private cuts retain their revisions.
[Block-class ledger](coverage/semantics/anonymous-block-rtd-review.json).

Anonymous classes can now share unit0 with plain empty global named declarations.
Early root declarations consume no RTD key; deferred declarations consume one even
when never executed. Three fresh originals agree at 234734715 /375, including factory
lookup before calls and reversed call order. Author166 there and independent115 at
c860977b0 pass 281 checks: 256 setup/source-frontier premises plus 25 pure queries,
with 13 actual PhpSteps for early no-op, runtime publication and anonymous allocation.
Changed strict3 passes at c860 (5.671s). The independent Closure admission failure
exposed shared pattern variables; the one-line fix keeps static/byref flags independent.
That failure and the original reserved-name native probe retain zero credit;
syntax-only preparation/elaboration adds none. At that cut, named declarations inside
namespaces, functions or Closures, broader named headers/bodies
and wider RTD ordering remain required. Actual375 over e68ebf38 passes strict3 at
02c43d49 (5.575s); private source/author/peer cuts retain their revisions.
[Mixed-class ledger](coverage/semantics/anonymous-mixed-rtd-review.json).

Public noarg/by-value/untyped constructors on parentless anonymous classes now
use ordinary allocation, call frames, result and throw cleanup with authenticated
source/name receipts. Defaults precede body effects; automatic `new` ignores
`return 99` while explicit calls observe it. Four fresh originals agree at
5d3e3da49 /374 (strict3 5.421s), including factory pre-call lookup, repeated effects,
shared Throwable identity and constructor `finally`. Author and independent groups
pass 391 checks: 371 setup/source-frontier premises and 20 pure queries, with 17
actual PhpSteps. The unescaped failed receiver loses its marker owner and is pruned;
escaped receivers and the shared Throwable survive. Terminal same-class result
receipt acceptance remains an explicit preexisting abstraction. Original interpreter
and fixture parse failures retain zero credit; syntax-only preparation/elaboration
adds none. Arguments/types/nonpublic constructors and broader anonymous contexts
remain required. Actual375 over 57f2f4b8 passes strict3 at 77f9c0eda (5.521s);
private source/state cuts retain their revisions.
[Constructor ledger](coverage/semantics/anonymous-constructors-review.json).

Simple global noarg/by-value/untyped function and static no-capture Closure factories
now record authenticated inner class checkpoints, save only restored unit images
and publish class names before the first call. Two fresh originals agree at
c417b2b03 /374 (strict3 5.473s), including pre-call dynamic lookup and compile-order
`$0/$1` independent of call order. Function140 at c417 and Closure140 at 36b2811b
pass 248 completed-compiler/source-frontier checks plus 32 explicitly pure context
premises, with eight real AT/EVAL PhpSteps. Changed strict3 passes at 36b2811b
(5.374s). The original compiler Unsupported, fixture binding stop and short-path
slice failure retain zero credit; the corrected guard checks length before slicing.
Original a898 source2 / 205+21 and e646 trace1 / 45+2 cuts remain frozen. Wider RTD
consumers, factory parameters/captures/types/class scope, incomplete scope images,
include/eval, constructor arguments/types and broader class consumers remain required.
Actual composition of 374 modules over 3609d8d4 passes strict3 at 137edf830
(5.572s), preserving task-specific hook, finalizer, Fiber, property/yield and GC
guards. Private source2 and separate function140/Closure140 cuts retain their
original revisions.
[Anonymous class ledger](coverage/semantics/anonymous-classes-review.json).

Private-final E_COMPILE_WARNING (128) delivery remains accepted at dec3e9968 /371:
two originals and 231 source-frontier checks plus 10 pure mask queries. Actual371
over 3a0be383 passes strict3 at 8e254b11 (5.374s); the original mismatch remains zero.
Wider warning producers and dynamic interactions remain required.
[Severity ledger](coverage/semantics/compiler-warning-severity-review.json).

Root-terminal HALT compilation now folds original-file byte offsets and treats
the authenticated final statement as a no-op, preserving pools, events and the
remaining continuation. Two fresh originals agree at c78beb627/371, including
namespace/global379 versus local17 and UTF-8 byte positioning. Strict3 passes 5.272s;
104 checks at real source frontiers plus 20 pure queries pass in 66/58 groups.
A separate pure payload decoder2 passes; the compile-stage baseline and two
fixture failures retain zero credit. Encoded profiles, broader constant/default/class
contexts and include/eval registration remain required.
Actual 371 over 8f1b22aad passes strict3 at 72e1a9d58 (5.321s), preserving attributed
class lines, property/factory/collector and foreach acquisition guards. Private
source2/104+20 checks and both fixture failures retain their original cuts.
[HALT ledger](coverage/semantics/halt-compiler-review.json).

Aggregate yield-from380 recursively acquires real Iterator/Generator data through
borrowed getter calls, retires raw layers and the original operand before rewind,
and keeps returned Generators in generic iterator mode: null result, no send/throw
forwarding and live raw reference cache. Copied getter frames own This once;
parked acquisition keeps the real parent resumer/source receipt. Early pending
cleanup retains constructed data until request cleanup; real rewind errors drop
it before catch. Seventeen unchanged originals agree across the retained source16
and owning-reference source1 cuts; strict368 passes at `b1164af45`. Independent
25/720 physical owner and source-authority premises pass at separate cuts.
Original compiler/source/fixture failures remain zero. At that acquisition cut,
Iterator NaN warnings and changed original operands remained required.
Ordinary-call Aggregate unpack remains required.
Actual368 over `7b449476` passes strict compilation at `f4567b30`; private
source/state cuts retain their inputs. [Yield-from review](coverage/semantics/yield-from-aggregate-review.json).

Acquired Iterator `valid()` NaN warnings now retain their raw retval and acquisition
receipt through ordinary handler invoke, result and cleanup. One post-handler
decision rereads numeric references; copied NaN remains true. Real parked handlers
preserve the parent resumer and delegation claim in the Fiber VM. False or thrown
warnings retire raw retval before iterator data, without request retention.
Nine exact native-grounded originals and strict368 pass at `c52ae1d16`.
Twenty independent genuine-source groups/637 physical ownership and warning
authority premises pass at `d825e3fc0`. Wider raw payload changes stay explicit Unsupported. Actual370 over `d827dc635` passes strict SL at `4723282ff`;
private source/state cuts retain their own inputs.
[Warning review](coverage/semantics/yield-from-valid-nan-review.json).

Aggregate yield-from getters may rebind an original CV or reference operand when
the raw result is a terminal Iterator/Generator or a rejected non-Aggregate value.
The original class still names rejection; borrowed CV and owning-cell cleanup
retain their existing owners. Six safe unchanged originals agree at `f82e9b3ed`;
strict370 passes at that cut. At that earlier cut changed operands returning another
Aggregate remained Unsupported/zero agreement. Nine genuine-source groups/376 physical
owner and source-authority premises pass at separate cuts; the two fixture
failures retain zero credit.
Actual370 over `288dc800` passes strict SL at `50367af16`; private source/state
cuts retain their own inputs.
[Rebound review](coverage/semantics/yield-from-rebound-operand-review.json).

Aggregate yield-from recursion now compares the first known Aggregate return
against its live object-valued source CV/reference, then later returns against
their owned raw layer. An independently kept original may be the first repeated
layer even after deeper source rebinding and comparator retirement; no history
owner is added. Self returns from immutable inputs and deeper layers retain the
fixed class rejection. Nine selected originals agree at `25f6a9f33` and strict372
passes there. The first-nonobject-source control stays Unsupported/zero agreement.
Sixteen genuine-source groups/732 physical ownership and authority premises pass
at `890007303`, including the identical forwarded old case9; no state correction
was needed. Previous rebound checks retain their cuts.
Actual372 over `488a190bc` passes strict SL at `5c27d4886`; private
source/state cuts retain their own inputs.
[Source comparison](coverage/semantics/yield-from-source-comparison-review.json).

Ordinary source-function calls now unpack direct user Iterators through borrowed
callbacks and a real cursor. Raw current references survive key callbacks;
reference-valued keys unwrap before positional/named binding. Valid retval,
cached current, Iterator DATA, raw INPUT and sent argument cleanup preserve native
order, including object-key errors and same-source reentry. By-reference Warning
handlers support null/bool/int/float payloads, numeric reference mutation, real
Fiber park/throw and fresh private callee cells. Pending abort operations finish
the remaining cleanup when a destructor replaces the exception, preserving its
previous Throwable. Strict373 passes at `9d8afc613`; 25 selected source agreements
retain `a59`/`9d8` cuts, and a Generator Unsupported control keeps zero agreement.
Twenty-nine genuine-source groups/1174 physical premises pass at retained
`4eb`/`79d`/`20e1` cuts; original compiler and fixture failures stay zero credit.
At that cut direct Generator/Aggregate unpack, other call targets, Generator
callbacks, valid NaN and refcounted by-reference warning payloads remained required.
Actual375 over `e1a016144` passes strict SL at `6ece4f690`; private
source/state cuts retain their own inputs.
[Iterator unpack ledger](coverage/semantics/iterator-call-unpack-review.json).

Direct Iterator call-unpack valid NaN warnings now retain the raw retval through
numeric handler mutation, Fiber park and throw. One numeric reread distinguishes
copied NaN from live references, including integer-minimum signed-zero bits;
retval retirement precedes current or Iterator/input teardown. False later warnings
keep prior named/sent owners into target entry; thrown warnings retire remaining
owners in native order.
Strict375 and eleven source agreements pass at `79104d0da`; the nonnumeric raw-tag
control is Unsupported/zero agreement. Three original Fiber expectation failures
and the ENOSPC-interrupted source campaign retain zero credit. Twelve independent
reached-state groups/432 physical premises pass across retained ten at `64d205280`
and affected two at `76cf54a4c`; the original parked-owner fixture failure stays
zero campaign credit. Actual375 over `0e847d333` passes strict SL at `ced657d93`;
private source/state cuts retain their own inputs. Direct Generator/Aggregate
unpack, other call targets, Generator callbacks, nonnumeric raw valid changes and
refcounted by-reference warning payloads remained required at that cut.
[NaN warning review](coverage/semantics/iterator-call-unpack-nan-review.json).

Copied KNOWN strings now survive direct Iterator by-reference argument warnings
with their original bytes/carrier, including key/handler source writes, named
variadic binding and Fiber park/throw. The callee receives a distinct private
reference cell. Strict375 and four original source agreements pass at `f96cae5f4`;
two live-reference string controls retain Unsupported/zero agreement with4/11
output events. Eight independent reached-state groups/331 physical premises pass
at `b42b46ced`, including fresh-cell ownership, actual parked line/cursor guards,
throw cleanup and out-of-pool carrier rejection.
At that cut reference strings, handler changes to strings and array/object
pre-warning payload holds remained required; earlier Iterator/NaN evidence keeps
its original cuts.
Actual375 over `b002fc277` passes strict SL at `ad7a95533`; private native/source
and independent state cuts retain their original inputs.
[String review](coverage/semantics/iterator-call-unpack-string-review.json).

Authenticated INTERNED_STRING references now reread the live key/handler/main
literal into a distinct fresh callee cell, including scalar-to-interned handler
changes, named variadic binding and Fiber park/throw. Interned strings need no
pre-warning refcounted payload hold. Strict375 and four new source agreements
pass at `27477d9fb`; the safe REQUEST reference control stays Unsupported with4
output events and zero agreement. Two affected prior literal originals now agree
using their unchanged `f96` native bytes, without replaying four copied sources
or six unaffected state groups. Eight independent reached-state groups/353
physical premises pass at `230682b1c`. REQUEST/plain reference strings, handler
replacements with those strings and array/object pre-warning holds remain required.
Actual375 over `bbbf2c166` passes strict SL at `92ae3426c`; private native/source
and independent state cuts retain their original inputs.
[Interned reference review](coverage/semantics/iterator-call-unpack-interned-reference-review.json).

Copied KNOWN objects now retain a pre-warning payload hold when the sent buffer
is empty. Resume transfers it to a fresh private cell; thrown warnings retire
raw cache, DATA and input before the failed argument payload, including actual
Fiber park/throw after the handler drops its source owner. Native6 passes at
`82b2581b6`; strict375 and five original agreements pass at `7baa83b0a`, with
the REFERENCE object control Unsupported/zero agreement. Nine independent groups
with 436 physical premises pass at `12a75251c` (two eligibility-only queries); the
original `9519` fixture syntax failure retains zero credit. Arrays, REFERENCE
objects, object warnings after earlier sent arguments and request/plain reference
strings remain required. Earlier cuts keep their original inputs.
Actual375 over `5f467baee` passes strict SL at `45cfc118d`; private native/source
and independent state cuts retain their original inputs.
[Object hold review](coverage/semantics/iterator-call-unpack-object-review.json).

Copied-object warnings now retain earlier fixed-slot arguments while the failed
payload maps to its real parameter slot. Cache/DATA/input retire first; positional
throws release the earlier payload first, while reversed named keys release the
failed payload first.
Normal resume transfers the held payload into a fresh private cell; real parked
throw preserves both earlier SENT and main scalar rewrites. Native5 passes at
`2b8b026b0`; strict375 and five original agreements pass at `2f055195a` without
fresh native capture. Ten genuine-source state groups pass 586 physical/555 driver
ownership and authority premises at `97b67a7b5`, including occupied-slot and retired
SOURCE forgeries. Later extra-named/variadic object sends remained required at that cut; earlier
cuts stay frozen. Actual375 over `9cc8cfa8d` passes strict SL at `352bf99fd`;
private native/source/state cuts retain their original inputs.
[Fixed-slot review](coverage/semantics/iterator-call-unpack-object-sent-review.json).

Copied-object warnings in one direct construction of a statically named Iterator
implementation now map fixed-to-extra arguments and extra-to-fixed arguments with
a by-value variadic tail through fixed-then-extra cleanup, including parked throw.
A private singleton object cell in an untyped reference variadic uses a separated
logical rest array while the original named-send owner survives rest-item writes;
this does not claim Zend's pre-write shared-table identity. Native5 composes the
unchanged first observation at `12f9405c` with four previously unrun rows at
`c4260073`; the first expectation failure remains zero credit. Strict375 and five
source agreements pass at `777199493` without fresh native execution. Eleven
independent reached-state groups pass 620 physical/589 driver premises across retained
six at `283f11cc` and affected five at `9ddd85c0`, including three counterfactual
helper guards. The strict constructor/binder and state record-syntax/seek-binding
stops retain zero campaign credit. General shared-buffer release before COW,
later positional variadic, arrays and REFERENCE object payloads remain required;
extra-to-extra remained open at that cut. Earlier cuts stay frozen. Actual375 over
`9a478e060` passes strict SL at `e5119c633`; private native/source/state cuts retain
their original inputs.
[Extra-named review](coverage/semantics/iterator-call-unpack-object-extra-named-review.json).

Copied-object extra-to-extra warnings now retain earlier private named cells and
map failed payloads in insertion order. Both warnings use the same variadic
argument number; normal rest writes retain original cells through F, and handler
or parked throws release Iterator then earlier and failed payloads. Native3 passes
at `8b914be9`; strict375 and three unchanged-source agreements pass at `fc1013009`
without fresh native execution. Eight genuine-source state groups pass 446 physical/419
driver ownership and authority premises at `a8f7e9f1`, including both private-cell
receives, retired SOURCE guards and F-to-A-to-B cleanup; no pure queries are counted.
The direct-site, untyped variadic and no-positional-extra guards remain; general
shared buffers, later positional variadic and REFERENCE payloads remained required
at that cut. Actual375 over `36a9933d` passes strict SL at `f4245b43`; private native/source/state
cuts retain their original inputs.
[Extra-to-extra review](coverage/semantics/iterator-call-unpack-object-extra-extra-review.json).

Later positional copied-object warnings now admit an untyped by-reference
variadic at one direct statically named Iterator construction, with no prior
named extras. Packed rest items alias the original private cells; clearing the
current item destroys its payload before F, while the earlier payload survives
until frame cleanup. Warning and parked throws retire Iterator before earlier
and current payloads. Native3 passes at `29d80a94`; strict375 and three unchanged
source agreements pass at `43f44b08` without fresh native execution. Independent
reached-state groups pass 453 physical/426 driver premises across seven retained
groups at `49cc58c1` and the corrected final body at `85237e75`, with no pure
queries. The original parked timeout and final request-marker fixture failure
retain zero campaign credit. At that cut typed/wider-site tails remained required;
general shared named buffers, arrays and REFERENCE object payloads stay open.
Earlier cuts stay frozen.
Actual375 over `334be798` passes strict SL at `b70b5df5`; private native/source/state
cuts retain their original inputs.
[Positional variadic review](coverage/semantics/iterator-call-unpack-object-positional-variadic-review.json).

Nullable single-class positional tails now preserve warnings and fresh sends
before receive-time verification. Accepted rest items alias the private cells;
a later rejected class leaves only the first rest entry. Its generated TypeError
trace owns both dereferenced payloads after frame cleanup, retaining them through
the final output. Handler and parked injected exceptions preserve Iterator-before-
payload teardown. Four native originals compose retained two at `0f4dac17` with
two previously unrun rows at `43f84aef`; the original expectation failure stays
zero credit. Strict375 and four source agreements pass at `1ad2ce8a` using retained
native bytes. Eight genuine-source state groups pass 501 physical/480 driver
premises at `ce17751e`, with no pure queries, including partial typed receive,
owning trace snapshots after frame retirement, packed ALIAS writes and parked
resume guards. At that cut typed named buffers remained open; other type shapes,
wider sites, arrays and REFERENCE payloads stay required. Earlier cuts remain frozen.
Actual375 over `e6879e16` passes strict SL at `80000219`; private native/source/state
cuts retain their original inputs and original expectation failure.
[Typed positional review](coverage/semantics/iterator-call-unpack-object-typed-positional-variadic-review.json).

Nullable single-class named tails now admit copied-object warnings at one direct
statically named Iterator construction with no positional extras. Receive checks
each item before collecting an ALIAS; clearing the current rest item destroys its
payload before F. A later rejected class leaves only the earlier rest item, while
the generated TypeError trace keeps both named payloads in insertion order through
E. Handler and parked injected throws retain Iterator-before-payload cleanup.
Four native originals pass at `f2af82e5`; strict375 and four unchanged-source
agreements pass at `cf6d4358` without fresh native execution. Eight genuine-source
state groups pass 505 physical/484 driver premises at `5cbc1a29`, with no pure
queries, including typed ALIAS writes and keyed trace owners after callee
retirement. Other type shapes, wider sites, general
shared named buffers, arrays and REFERENCE payloads remain required; prior cuts
stay frozen.
Actual375 over `8728e2d1` passes strict SL at `bf83dfb8`; private native/source/state
cuts retain their original inputs without renewal.
[Typed named review](coverage/semantics/iterator-call-unpack-object-typed-named-variadic-review.json).

Copied arrays now retain their container through the first positional warning
into an untyped fixed by-reference parameter at a direct statically named Iterator
construction. The fresh private cell takes the hold; element writes release the
child before F, while handler and parked throws retire Iterator DATA/INPUT before
the held container and child. Native4 passes at `197b2af0`; strict375 and three
unchanged-source agreements pass at `9a439a21` using retained native bytes. The
initial REFERENCE-array control remains Unsupported with four events/zero agreement.
Nine genuine-source groups compose 481 physical/456 driver premises from retained
six at `cf0cba5c` and corrected three at `7c6d28d3`, with no pure queries. The
original injected-source fixture lookup failure remains zero credit. Later/named/
typed array warnings, wider array/COW interactions and live REFERENCE payloads
remain required at that cut; prior cuts stay frozen.
Actual375 over `32ed5056` passes strict SL at `79f2ad1b`; private native/source/state
cuts and the original fixture failure retain their inputs without renewal.
[Array review](coverage/semantics/iterator-call-unpack-array-review.json).

Copied-array warnings now retain earlier fixed-slot sends and map failed holds
by parameter order. Positional throws retire the earlier container/child first;
reversed named keys retire the failed container/child first, after Iterator
DATA/INPUT. Normal private element writes destroy the current child before F;
real parked injection preserves both containers and main scalar rewrites.
Five native originals pass at `302d31de`; strict375 and five unchanged-source
agreements pass at `917659fd` using retained native bytes. Eleven genuine-source
state groups pass 783 physical/750 driver premises at `0465c123`, with no pure
queries, including container-to-child cleanup, retired SOURCE authority and real
parked ownership. Extra-named/variadic/typed array warnings, broader array/COW
interactions and live REFERENCE payloads remained required at that cut; prior cuts
stay frozen.
Actual375 over `8f3f57de` passes strict SL at `7f6968ed`; private native/source/state
cuts retain their original inputs without renewal.
[Array fixed-slot review](coverage/semantics/iterator-call-unpack-array-sent-review.json).

Copied-array warnings now admit an untyped positional by-reference variadic at
the same direct Iterator construction, with no named extras. Packed rest items
alias fresh private cells; a nested current-item write destroys its child before
F, while the earlier child remains until frame cleanup. Warning and parked injected
throws retire Iterator before earlier and current containers/children. Three
native originals pass at `f87e8531`; strict375 and three unchanged-source
agreements pass at `ab804d84` using retained native bytes. Nine genuine-source
state groups pass 639 physical/607 driver premises at `76c89432`, with no pure
queries, including container-to-child retirement, nonowning SOURCE guards, real
parking and packed-cell aliasing. Extra-named/typed arrays, broader array/COW
interactions and live REFERENCE payloads remained required at that cut; prior cuts
stay frozen.
Actual375 over `d7e80379` passes strict SL at `6b4656fd`; private native/source/state
cuts retain their original inputs without renewal.
[Array positional variadic review](coverage/semantics/iterator-call-unpack-array-positional-variadic-review.json).

Nullable-array positional by-reference variadics now preserve warning holds and
fresh private cells before receive-time verification at the direct Iterator site.
Packed rest items alias those cells; nested current-child writes destroy it before
F. A later scalar rejection leaves only the earlier rest item, while the generated
TypeError trace owns the earlier array and child after private cells retire,
retaining them through E. Handler and parked injected throws preserve Iterator-
before-earlier-before-current cleanup. Four native originals pass at `ce5706f85`;
strict375 and four unchanged-source agreements pass at `cdef79262` using retained
native bytes. Nine genuine-source state groups pass 626 physical/595 driver
premises at `1369211ea`, with no pure queries, including partial typed receive,
trace-held container/child lifetime after private cells retire, parked authority
and nested ALIAS writes.
Extra-named/other typed arrays, wider sites, broader array/COW interactions and live
REFERENCE payloads remained required at that cut; earlier cuts retain their inputs.
Actual375 over `ab478bca` is composed at `86faf6cc`; independent pointwise seam
review retains private strict/source/state cuts without a new current execution.
[Typed positional array review](coverage/semantics/iterator-call-unpack-array-typed-positional-variadic-review.json).

Nullable-array named by-reference variadics now preserve copied container holds
at the same direct Iterator site, with no positional extras. Typed receive keeps
keyed ALIAS items; nested current-child writes destroy it before F. A later scalar
rejection leaves only the earlier rest alias and an owning keyed TypeError array
snapshot that retains the child after private cells retire through E. Warning and
parked throws retire Iterator before earlier/current containers and children in
named insertion order. Four native originals pass at `2d6e8e83`; strict375 and four
unchanged-source agreements pass at `7ea7489d` using retained native bytes.
Nine genuine-source state groups pass 632 physical/601 driver premises at
`70f7916d`, with no pure queries, including keyed ALIAS writes, parked authority
and trace-only container/child ownership after private frame retirement.
Untyped named arrays, other type shapes, wider sites, broader array/COW interactions
and live REFERENCE payloads remained required at that typed cut; prior cuts stay
frozen.
Actual375 over `b10b0042` is composed at `720ec713`; independent pointwise seam
review retains private strict/source/state cuts without a new current execution.
[Typed named array review](coverage/semantics/iterator-call-unpack-array-typed-named-variadic-review.json).

Untyped named by-reference variadics now admit copied arrays at the same direct
Iterator site with no positional extras. Authenticated singleton private cells
become DIRECT items in a separated logical rest array; the original named-send
cells retain their containers. Nested alpha writes copy its container, keeping B
through F, then releasing A and B in insertion order. This representation abstracts
Zend's shared table before COW, without asserting native table identity or counts.
Warning and real parked throws retain Iterator-before-A-before-B cleanup. Three
native originals pass at `c39b75ba`; strict375 and three unchanged-source agreements
pass at `06189ef8` using retained native bytes. Eight genuine-source state groups
pass 608 physical/579 driver premises at `e6f8f16b`, including three counterfactual
receive guards and no standalone pure-query groups.
General shared named buffers, other types, wider sites, embedded references/cycles,
broader array/COW interactions and live REFERENCE payloads remained required at
that untyped named-array cut.
Actual375 over `5e996a3b` passes strict SL at `ab4c9d22`; private native/source/state
cuts retain their original inputs without renewal.
[Untyped named array review](coverage/semantics/iterator-call-unpack-array-named-variadic-review.json).

Property-backed Iterator reference objects now retain a detached payload owner
across the first positional warning at a direct construction, empty sent buffer
and untyped fixed by-reference target. A nonowning snapshot authenticates the live
source cell; retired SOURCE receipts do not read dead STORE/property contents.
The fresh callee cell is independent: a separate global alias survives its NULL
write through F. Warning and real parked throws retire Iterator before payload;
main changes only an unrelated scalar marker. Five native originals are observed
across retained normal and corrected-alias/remaining captures at `8be397cc`.
Strict375 and five unchanged-source agreements pass at `78fd0843` using retained
native bytes. Nine genuine-source state groups pass 538 physical/515 driver
premises across retained prefixes and corrected tails, ending at `3f88b358`, with
no standalone pure-query groups. Original alias, compiler and state fixture
failures remain zero credit. Other reference-object sources, live payload
replacements, reference arrays, later/named/typed sends and wider sites remained
required at that reference-object cut.
Actual375 over `df1ed558` passes strict SL at `292e0bc8`; the parent bool-NaN task
and Iterator snapshot compose without renewing native/source/state cuts.
[Property reference review](coverage/semantics/iterator-call-unpack-reference-object-review.json).

Stable Iterator-owned property references now retain array payloads with one
acyclic destructible child at the same first positional, empty-buffer, direct-site
and untyped fixed-reference target. The detached container HOLD and nonowning
snapshot remain separate from the raw HCELL. A fresh callee cell copies the array
on nested write when a global alias retains the original; its child survives
through F until alias unset. Without that alias, the child retires before F.
Warning and real parked throws retire Iterator before container and child.
Five native originals pass at `af04e4a3`; strict375 and five unchanged-source
agreements pass at `3f6ddf6f` using retained native bytes. Nine genuine-source state
groups pass 617 physical/594 driver premises at `e0a34c6f`, with no standalone pure
queries, including alias COW, retired receipts and authentic parked ownership.
Other reference sources,
live payload replacement, later/named/typed sends, wider sites and broader
array/COW interactions remain required; earlier cuts retain their original inputs.
[Property reference array review](coverage/semantics/iterator-call-unpack-reference-array-review.json).
Exact `7925550a` composition retains the private cuts through unchanged Iterator/schema
inputs; the disjoint parent changes require no current actor.

Stable Iterator property-reference object/array sends now also accept a first
named key selecting fixed untyped BYREF parameter0, with an empty sent buffer at
the same direct construction. Detached holds transfer into fresh private cells;
source aliases and array COW survive, while named history rejects a later
positional key before another warning or target entry. Strict390, ten author and
three independent originals, and seven genuine-source state groups/514 driver
premises pass at `913195852`. The original Unsupported baseline, independent
fixture grammar failure and terminated successor retain zero agreement. Later,
typed or variadic reference sends, wider sources/live replacements and broader
array/COW interactions remained required at that cut; full core stays partial.
[Named reference review](coverage/semantics/iterator-call-unpack-named-reference-review.json).
The composition of 391 modules over `11fdbc879` passes canonical inventory and strict SL at
`b15c57efc`; private source/state cuts retain their original identities.

Initial named stable Iterator property-reference sends now resolve later fixed
untyped BYREF parameters with an empty sent buffer. Earlier argument holes bind
defaults before the body, while the selected slot determines warning number and
argument count. Handler writes cannot retarget the captured key; missing required
earlier arguments raise real `ArgumentCountError` with trace-owned payloads.
Strict391 and eleven new originals pass at `b2d6e6e539`. Eight new genuine-source
state groups/555 driver premises and only the affected prior group/69 pass there;
other prior cuts retain their own identities. The unchanged Unsupported baseline
retains zero agreement. Actual later sends, typed/variadic targets, wider
sources/live replacements and broader array/COW interactions remained open at that cut.
[Reference-hole review](coverage/semantics/iterator-call-unpack-reference-holes-review.json).
Canonical391 composition over `9b733e448` passes inventory and strict SL at
`58bbbacc1`; private source/state evidence retains its original cuts.

Initial stable Iterator property-reference sends now admit exact normalized
nullable class/array shapes at fixed BYREF targets. Types are checked at receive;
later incompatible scalar writes through source-free private cells succeed while
source aliases retain the original payload and array COW. Real receive TypeErrors
own dereferenced trace arguments until caught-exception release; warning throws
precede receive. Strict391, thirteen new originals and nine genuine-source state
groups/629 driver premises pass at `c9f29a120`. Earlier evidence retains its own
cuts without replay. Both unchanged named and positional Unsupported frontiers retain
zero agreement. Reversed/nonnullable/other type shapes, variadic targets, actual
later sends and wider sources/live replacements remained required at that cut.
[Typed reference review](coverage/semantics/iterator-call-unpack-typed-reference-review.json).
Canonical394 composition over `bf7fd3bba` passes inventory and strict SL at
`c04ac28e9`; private source/state evidence retains its original cuts.

Noninitial stable object property-reference sends now accept vacant fixed untyped
BYREF slots after an earlier fixed slot is filled, without extra argument buffers
at the same direct construction. Earlier copied roots/private cells, raw source
cells and detached holds stay separate; repeated raw properties create distinct
private callee cells. Reversed named aborts release by parameter order after
Iterator retirement; duplicate or positional-after-named keys fail before another
warning. Retired receipts read no dead source storage. Strict394 passes at `40cbbedc9`; eleven new originals
compose first five there with remaining author three and independent three at
later test-only cuts. Seven genuine-source groups/524 driver premises compose
retained capture79, author292 and independent153. The unchanged Unsupported
baseline, original source/parked-state timeouts and transfer fixture failure keep
zero credit; corrections touch test bounds/registry assertions only. Earlier cuts
are retained without replay. Later arrays, typed/variadic targets and wider
sources/live replacements remained required at that cut.
[Noninitial reference review](coverage/semantics/iterator-call-unpack-noninitial-reference-review.json).
Canonical394 composition over `122f54805` passes inventory and strict SL at
`415d9afa1`; private source/state evidence retains its original cuts.

Noninitial stable array property-reference sends now reuse that fixed untyped
admission. Detached containers transfer to distinct private cells while child
edges remain single; nested writes preserve repeated-source arguments and source
aliases through COW. Reversed warning aborts preserve parameter-order cleanup,
retired receipts read no dead array storage, and real second-warning Fiber throw
retains saved owners. Strict394, nine new originals and six genuine-source state
groups/546 driver premises pass at `31e9d1262`. The sole affected prior documentary
group/80 passes separately; native9 and the unchanged second-send Unsupported
baseline earn zero model agreement. Earlier cuts remain frozen. Later typed or
variadic reference targets, wider sources/live replacements and broader array/
reference/COW interactions remained required at that cut.
[Noninitial array reference review](coverage/semantics/iterator-call-unpack-noninitial-array-reference-review.json).
Canonical394 composition over `4a0d4f705` passes inventory and strict SL at
`ba187beeb`; private source/state evidence retains its original cut.

Noninitial stable property-reference sends now admit the existing exact normalized
nullable class/array shapes at fixed BYREF targets. Receive-time types do not
constrain later writes through fresh private cells. Repeated array sends preserve
COW; rejected receives retain earlier/current values in owning DIRECT traces,
including by-value arrays and source aliases. Warning throws and real parked
injections precede receive errors. Strict394, ten new originals and seven genuine
state groups/528 driver premises pass at `7158abb01`; the sole affected prior
group/80 passes separately. Native10 and the unchanged second-send Unsupported
baseline retain zero model agreement; earlier cuts stay frozen. Other type shapes,
variadic targets, wider sources/live replacements and broader array/reference
interactions remained required at that cut.
[Noninitial typed reference review](coverage/semantics/iterator-call-unpack-noninitial-typed-reference-review.json).
Canonical394 composition over `f742468b0` passes inventory and strict SL at
`9fcd6760e`; private source/state evidence retains its original cut.

Untyped positional BYREF variadic tails now accept stable Iterator property-reference
object/array payloads at the same direct construction. Distinct private cells feed
packed ALIAS rest entries; original EXTRA owners survive rest unset, and repeated
arrays/source aliases retain nested COW. Warning aborts and real parked injection
preserve Iterator-before-argument cleanup; retired receipts read no dead storage.
Nine new originals compose six at `05e880bea` with three at `444909b50`;
strict394 remains at the former cut. Six genuine-source state groups/488 premises
pass through retained fixture cuts at `444909b50`, with affected prior80 separate.
Native9 and the unchanged Unsupported baseline earn zero model agreement. The
identifier-elaboration and premature-unset fixture failures retain zero credit;
only test identifiers and cleanup-phase expectations changed. Earlier cuts remain
frozen. Typed or named variadic reference targets, wider sources/live replacements
and broader array/reference interactions remained required at that cut.
[Positional variadic reference review](coverage/semantics/iterator-call-unpack-reference-positional-variadic-review.json).
Canonical394 composition over `a3d23c935` passes inventory and strict SL at
`a7ff8b83a`; private source/state evidence retains its original cuts.

Positional property-reference variadics now admit the existing exact nullable
single-class/array shapes. Receive-only checks permit later scalar writes;
partial rest failures retain owning DIRECT traces after callee retirement, with
source aliases independent. Later warning throws and real Fiber injection
precede even an earlier receive mismatch. Nine exact originals and seven reached
groups pass 562 premises at 5df4; two affected prior guards pass 133 separately.
Native/baseline cuts and the original alias-fixture failure retain zero agreement.
Named tails, other type shapes, wider sources and live replacement remain open.
[Typed variadic reference review](coverage/semantics/iterator-call-unpack-reference-typed-positional-variadic-review.json).
Canonical394 composition over `b2c8b1ce1` passes inventory and strict SL at
`6c04f7455`; private source/state evidence retains its original cut.

Plain source-function calls now unpack direct Generators into by-value parameters.
Native iterator resumes snapshot reference yields without invented method traces;
completion/finally precede defaults and receive checks. Temporary versus retained
operands preserve cache/argument cleanup and owning TypeError traces. Last-owner
storage retains its quiet release carrier when ordinary destructors are inactive.
Ten new exact originals and one promoted prior control agree; nine state groups
from genuine source frontiers pass 642 premises. Source/state evidence retains
its 5c9/151f/2ea/e8d cuts. Final strict initialization of 395 modules and the
nested yield-from Unsupported control pass at 18f9. Native observations, the
unchanged baseline, Unsupported controls and preserved failures/diagnostics earn
zero agreement. At that cut, by-reference targets, active
yield-from producers, wider calls and broader lifecycle interactions remained open.
[Generator unpack review](coverage/semantics/generator-call-unpack-review.json).
Canonical395 composition over `470e9adce` passes inventory and strict SL at
`648402fb6`; private source/state evidence retains its original cuts.

Ordinary Generator call unpack now consumes array `yield from` through a present,
source-authenticated cache. Sent values preserve reference snapshots and repeated-row
COW; real table/cache owners distinguish temporary and retained-CV cleanup.
Queued close follows the caller's destructor receipt and carries child-destructor
exceptions through finally/cache release. Nine new exact originals and one promoted
prior control agree. Five genuine reached groups pass 435 premises: author 251 at
`f480dce9` and independent 184 at `871fc198`. Final strict initialization of 395
modules passes at `871fc198`; earlier source cuts retain `87fabcdc`/`f480dce9`.
Ten native observations, the unchanged Unsupported baseline, the non-array required
control and original failures earn zero agreement. At that cut, non-array delegates,
by-reference targets and broader call/lifecycle interactions remained open.
[Delegated-array review](coverage/semantics/generator-call-unpack-array-delegation-review.json).
Canonical395 composition over `52dccd723` passes inventory and strict SL at
`957703ff4`; private source/state evidence retains its original cuts.

Ordinary Generator call unpack now follows finite active Generator chains to a
paused value or authenticated array delegate. Parents borrow the real leaf cache;
reference snapshots, nested-row COW, child returns and source traces stay intact.
Temporary versus retained parent/child owners preserve distinct finally/cache
cleanup. Nine new exact originals and one promoted prior control agree; five
source-reached groups pass 460 premises at `f0d153efd`. Full strict initialization
of 395 modules passes at that cut. Ten native observations, the unchanged baseline
and the Iterator-leaf Unsupported control earn zero agreement. The saved-locals
fixture elaboration failure also retains zero credit. At that cut Iterator/Aggregate
leaves, detached independently completed-child states, by-reference targets and
wider lifecycle interactions remained open.
[Generator-chain review](coverage/semantics/generator-call-unpack-generator-delegation-review.json).
Canonical395 composition over `8a121da8c` passes inventory and strict SL at
`d85413ebc`; private source/state evidence retains its f0d cut and fixture hashes.

Direct detached Generator roots now unpack copied raw caches under a source-valid
FROM_COMPLETE receipt whose return owns no heap nodes. Child storage may retire
without consuming the parent cache; key errors leave the real return/tail for a
later next, and parent finally precedes cached destructors, including caught
throws. Strict395, seven new normal originals and five genuine-source groups/460
driver premises pass across the `d39565f95`/`9a5c60dda` cuts using retained native10.
Three Unsupported controls, the unchanged baseline and five original failures
keep zero agreement. At that cut owning copied returns, active chains ending in detached
roots, Iterator/Aggregate leaves and valid-key by-reference targets remained required.
[Detached-child review](coverage/semantics/generator-call-unpack-detached-child-review.json).
Canonical395 composition over `53d2924e7` passes inventory and strict SL at
`e7d1b874e`; private source/state cuts and original failures retain their identities.

Generator call unpack now consumes source Iterator yield-from leaves, including
finite active shared links. Key callbacks precede by-value capture; reference
mutation, row COW, next-callback throws and temporary/retained cleanup preserve
real producer frames and existing owners. Strict395, six new normal originals
and four source-reached groups/360 premises pass at `4a67329a1`; the promoted
prior Iterator-leaf source agrees separately. Seven native observations, the
Aggregate-acquisition control and unchanged baseline earn zero agreement.
At that cut acquired leaves, valid-key by-reference targets, owning copied returns and
active chains ending in detached roots remained required.
[Iterator-leaf review](coverage/semantics/generator-call-unpack-iterator-delegation-review.json).
Canonical396 composition over `40468e240` passes inventory and strict SL at
`a14595aee`; private source/state evidence retains its `4a67329a1` cut.

Generator call unpack now admits Aggregate-acquired Iterator leaves through the
existing nonowning receipt. Acquisition/input owners release before rewind;
independent aliases keep their own lifetimes. Queued close authenticates the
acquired-next marker after input detachment, preserving the real destructor
carrier. Four new normal originals and one promoted prior control agree across
`ab7018438`/`1a0b15cdb`; strict396 and three reached groups/303 premises pass at
the latter cut. Native5, the unchanged baseline, acquired-Generator control and
original temporary-cleanup Unsupported failure retain zero agreement.
At that cut acquired Generator data, ordinary Aggregate call operands, valid-key
by-reference targets, owning copied returns and nested detached roots remained required.
[Acquired-Iterator review](coverage/semantics/generator-call-unpack-acquired-iterator-review.json).
Canonical397 composition over `dbd756ab7` passes inventory and strict SL at
`74f63b964`; private source/state cuts and the original failure retain their identities.

Generator call unpack now consumes Aggregate-acquired Generator data directly or
below active shared links. The acquired parent owns its raw CURRENT copy and
child; by-value SEND snapshots references before native iterator resumes, without
invented API frames.
Method receivers survive acquisition, unused owning child returns retire before
the null-result parent tail, and temporary key errors close child before parent
finally/cache/SENT release. Independent child CVs retain their own COW cache and
real body-throw trace. Five new exact originals and one promoted prior control
agree at `80ad118bf`; strict397 and four reached groups/436 premises pass there
(author195, independent241). See the
[acquired-Generator ledger](coverage/semantics/generator-call-unpack-acquired-generator-review.json).
Native-only observations and the unchanged Unsupported baseline earn zero model
agreement. At that cut ordinary Aggregate call operands, valid-key by-reference
targets, owning copied returns and active chains ending in detached roots remained required.
The397-module composition over `bb312fcd2` preserves the tested405 bytes and
every incoming runtime selector. Independent pointwise review warrants no joined
actor; private strict/source/state evidence retains its `80ad118bf` cut.

Generator call unpack now follows finite active shared links to a detached middle
whose copied child return owns no heap nodes. Its null key raises the real Error
before SEND; copied current rows, retained cache owners and later return/tail
execution remain intact. A nonowning pending-initialization bit models Zend's
root-resume history: an inherited middle with its own cache can skip finally on
forced close, while direct initialization or a real next that consumes the bit
without advancing restores finally execution. The earlier omitted-middle-finally
native answer is preserved; the assigned-yield-from probe refutes a result-demand
explanation. Six new exact originals and one promoted prior control agree;
strict397 and four reached groups/341 premises pass (author159, independent182).
Runtime/source evidence retains `10c4c10bf`; fixture-only corrections and independent
checks retain their `c150ad30a`/`5ee387433` cuts. Native-only observations, the
unchanged baseline and original observer failures earn zero model agreement. See the
[nested-detached ledger](coverage/semantics/generator-call-unpack-nested-detached-review.json).
At that cut owning copied returns, pending-initialization send/throw, ordinary Aggregate call
operands, valid-key by-reference targets and wider callback/Fiber interactions
remained required.
The399-module composition over `ee0b6af27` preserves the tested Generator rules
and the parent's disjoint storage tasks/manifest. Independent pointwise review
and inventory pass; no joined runtime actor adds execution credit.

Pending `send` on an authenticated detached Generator with a nonowning copied
return now clears initialization and snapshots the raw current without advancing.
Yield-from has no native send target, so no argument buffer is added. Argument
cleanup precedes receiver release, preserving a sole method receiver; returned
rows survive a reference-cache rewrite and an argument-destructor throw preserves
the cleared bit for later finally. Shared internal resumes now preserve actual-root
first-yield history, including a previously initialized middle whose rewind stays
allowed after shared advancement. The
[pending-send ledger](coverage/semantics/generator-pending-init-send-review.json)
retains five exact original-source agreements and strict399 at runtime `0969bd40c`,
plus five reached groups/468 physical premises (author308 + independent160) at
fixture-only `4efd38733`. The combined five-fixture parse/elab gate adds no runtime
agreement. Native-only observations, unchanged Unsupported baseline and original
preparation/observer failures retain zero agreement. Pending sends to live yield
targets, owning copied returns and pending throw remain Unsupported; broader
callback/Fiber interactions remain required.
The399-module composition over `e319c9e89` preserves both tested Generator
modules and the parent's runtime/manifest. Independent pointwise review and
inventory pass; no joined actor adds execution credit.

Foreach Aggregate getters now permit terminal Iterator/Generator or rejected
non-Aggregate returns after rebinding an independently protected original CV or
reference. Borrowed CVs and owning cells retain their modes through initial
Iterator valid-result cleanup or Generator yield; input retirement then precedes
current/body with data protected.
Six unchanged originals agree at `4e9dd1014`;
strict370 passes there. At that earlier cut the changed-Aggregate control passed zero-agreement
assertions at `1cf220b69`; its original event-encoding failure stays zero.
Nine genuine-source groups/361 physical ownership and authority premises pass
at `5a811c3d5`; no state fixture correction was needed.
Actual371 over `557e8c817` passes strict SL at `ab0808dff`; private source/state
cuts retain their own inputs.
[Foreach rebound review](coverage/semantics/foreach-rebound-operand-review.json).

Foreach Aggregate recursion now compares the first known Aggregate return against
its live object-valued source CV/reference, and later returns against their owned
raw layer. An independently kept original can be the first repeated layer even
if a deeper callback rebinds the source again. Self returns from immutable inputs
and deeper layers are rejected with the fixed class message. No comparator/history
owner is added.
Nine selected originals agree across `60b6fbdef`, `0a1ef1232` and `ecc2923d8`;
strict371 passes at the first cut. The nonobject-source control stays Unsupported
with zero agreement, and its original missing-cleanup-output fixture failure is
preserved. Sixteen genuine-source groups/666 physical ownership and authority premises pass
at `7eaed6c5a`, including the identical forwarded old case9; no state correction
was needed. Previous rebound checks retain their cuts without renewal.
Actual371 over `aa2483c8b` passes strict SL at `0f9308067`; private
source/state cuts retain their own inputs.
[Source comparison](coverage/semantics/foreach-source-comparison-review.json).

Bounded assertion quantity warnings retain frozen parsed modes and old returns
through nested raw writes, throw and restore. Immutable string carriers preserve
INI identity while ordinary consumers use bytes. Seventeen safe originals retain
the separate 5ec/4141/1a8 cuts; actual phase234 at93be contains208 well-defined and26
reached lifetime-boundary checks. A replaced modified request raw stops with explicit
Unsupported; four native lifetime probes have zero agreement, with no allocator model.
Affected Throwable source3, genuine trace47 and retained Generator source1/report52
pass at1a8; template2 passes at6cb. Strict361 compiler3 passes at1a8 (4.623s).
The [quantity ledger](coverage/semantics/assertion-quantity-review.json) preserves
failures and the separate diagnostic46. Per-round original recapture and warned
restore now pass two fresh safe originals and182 source-frontier checks plus one
pure NULL trace query at57ee/363; strict3 passes5.024s. Pending shared Throwable
identity and real restore commits remain intact. Retained-entry Stringable SET
now snapshots the converted option before the old return, warning/refusal and trace
arguments. The original conversion is borrowed evidence; actual calls own only the
converted string, so handler retirement runs the Option destructor immediately.
Three fresh safe originals and236 checks at real frontiers, including a projected
ownership query, pass at7eaee/363; strict3 passes4.921s. Warned Stringable RESTORE
now retains a unary converted call and commits the saved original despite handler
retirement/shared throw. Two fresh safe originals and211 frontier checks, including
a projected owner query, pass at05db/365; strict3 passes5.024s. NaN SET now freezes
the old return and formatted input before conversion warning dispatch, then captures
live raw/original after the callback. Two fresh safe originals and247 source-frontier
checks plus eight pure trace-clear companions pass atc2b195/367; strict3 passes5.021s.
The shared Throwable survives committed NAN/mode0 without a second handler entry;
the baseline and original entry-certificate failure retain zero credit. Reentrant
restore now represents a cleared live original as raw NULL with modified=false.
The getter returns canonical empty bytes; parsed mode12 and safe no-op restores
remain intact through the shared Throwable. Two fresh originals and323 checks at
real frontiers plus12 pure exclusion queries pass at242576/367; strict3 passes5.074s.
New or active SET/NaN continuations encountering NULL stop explicitly; no source
executes NULL parsing. Retained-owner Stringable descriptions now convert once before
truth and resume the entered assertion despite a callback changing live mode to0.
Cast-time traces retain the original object; a failed assertion stores the converted
argument/message. Original cast Throwable identity and untouched assignment survive.
Three fresh originals,265 checks at source frontiers and4 pure owner-exclusion queries
pass atb4ea/367; strict3 passes5.174s. The original raw-descriptor timing failure retains
zero credit; the corrected fixture checks admission after actual driver publication to
THROW_SEARCH. Quiet weak scalar descriptions now apply TYPESTRING and replace only
the actual second call argument before failure policy and trace capture. Integer17
gets a fresh authenticated carrier; false gets canonical empty bytes and NULL stays
NULL, while source variables and assignment sentinels stay unchanged. Two fresh
originals and217 checks at source-derived frontiers, including helper counterexamples,
pass at088d14878/370; strict3 passes5.224s. The prior TypeError diagnostic carries
zero agreement. Description warning conversion/unpack and last-owner entry/handoff
remain required. [Description checkpoints](coverage/semantics/assertion-quantity-review.json).
Logical-not generated descriptions now use Zend prefix precedence240/child241,
retaining compound-child parentheses. Two fresh originals and79 checks at a genuine
compound pool/default-message/trace/true-control frontier pass atbb485b301/370, plus
two pure export-context queries; strict3 passes5.223s. The compile-stage exporter
Unsupported baseline retains zero agreement/reached credit; wider exporter forms
remain required. [Exporter checkpoint](coverage/semantics/assertion-quantity-review.json).
Actual370 over2ffab90c passes strict3 at461e012e (5.274s), preserving factory
invocation, denied-getter scope and yield-from Aggregate acquisition guards.
Private logical-not source2/79+2 checks and all prior cuts retain their identities.
Actual370 over1963b152 passes strict3 atb74fe28fb (5.775s), preserving current
factory/GEN/SensitiveParameter, implicit-getter, typed-reference and EX worker guards.
Private description source3/265+4 checks and all previous cuts remain unchanged.
Actual367 over78f866bb passes strict3 at7a2095bf (5.071s), preserving
SensitiveParameterValue reception and by-reference finalizer cursor/replay guards.
Private nullable source2/335 and all earlier cuts remain unchanged.
Actual367 overdb808 passes strict3 atfac7c8 (5.121s), preserving ARG
receiver/argument/foreach continuations and EX parked-public lookup/collector guards.
Private source2/255 cuts and prior unsafe boundaries remain unchanged.
Actual367 over288c passes strict3 ate6c5 (5.224s), preserving Aggregate foreach,
deferred return Notices, live concat and mixed-CV property ingress; private
source2/211 cuts are unchanged.
Actual365 over7377 passes strict3 at6b2a (5.020s), retaining current GEN/PROPS,
retired-owner and SensitiveParameter guards; private source3/236 cuts are unchanged.
Actual363 over1b33 passes strict3 at1ad9 (4.975s), preserving canonical GEN release
evidence and carrier-aware ARG/GEN fixtures; the private source/state cuts are unchanged.
Actual363 over75dade passes final strict3 atb0d8 (4.921s), preserving current
CALLS/CLASS/PROPS guards. Source-backed static70, Fiber54 plus4 pure key queries
and three retained incoming originals keep their0506/2ae cuts. Static356/371 and
key376 preserve carriers; the ledger retains separate failed source/VERIFY/fixture cuts.

Constructor property promotion retains source Param flags/origins, compiles separate
property defaults and performs ordered value/reference writes after all receives.
Explicit re-entry, private/inherited/trait scope, readonly checks and supported method
attributes reuse ordinary property protocols. Exact original9b85 now gives
`B|Y|F|D1||Z|1|1`; eight focused originals add seven normals and one ordered
CompileError. Private359 at00c passes strict compilation, source9 and genuine
Weak48/byref47. Historical Unsupported, strict/fixture stops and wrong-status row
retain zero affected credit. Actual361 over6e09 passes strict compilation
at8335 (4.840s); private source/state cuts retain their inputs. Other parameter
attributes/hooks and complete core remain required. [Promotion review](coverage/semantics/constructor-promotion-review.json).

Promoted properties accept one zero-argument builtin `#[Override]` through the
actual namespace/import scope. Exact nonprivate parent properties satisfy it;
simple root errors occur during compilation, while parent/trait links check after
ordinary compatibility and roll back failed publication. Trait collisions retain
the effective declaration's source. Two originals plus eleven focused sources
agree at `373f804e` (361 modules);
the namespaced user attribute stays Unsupported with zero agreement. Strict
compilation and 110 genuine assertions (own 63, trait 26, rollback 21) pass at
`456ebb0b`; the source cut and four earlier compiler stops retain their identities.
The actual 361-module composition over `61e7b80ff` passes strict compilation at
`6c098ce8` (4.979 s), preserving current EX/CALLS interfaces without renewing
the private checks. [Override review](coverage/semantics/promoted-override-review.json).

One zero-argument builtin `#[Override]` on an ordinary parameter now raises the
native target Fatal in methods, functions, Closures and arrows. Name/variadic
guards and constant-default compilation precede it; type/default compatibility
follows it. Resolved spelling and surviving compiler lines are retained. Eval
preserves earlier output/notices and stops before catch, body or publication.
Sixteen originals agree across the bad18/94a/929/ba904 cuts. Strict compilation
of 361 modules and one SL gate with 109 checks (68 derived request checks,
41 reached eval checks) pass at `4f6a47d6`. Earlier line/nondeterminism
discrepancies, fixture stops and the failed state run retain zero credit. Other
parameter attributes/hooks remain required. The actual 361-module composition
over `786137a55` passes strict compilation at `f5eb9399b` (4.954 s), preserving
current runtime/owner/GC/replay paths without renewing the private checks.
[Parameter-target review](coverage/semantics/parameter-override-review.json).

Ordinary parameters accept one zero-argument builtin `#[SensitiveParameter]`.
Fixed trace slots snapshot current CVs; positional/named variadic slots retain
their original operands, with no invented omitted defaults. Real owning wrappers
are allocated before callback/retirement and shared by getters and trace rendering.
Ten originals agree at `e27ceb30c` (362 modules); the namespaced user attribute
remains explicit Unsupported with zero agreement. Strict compilation and SL112
(34 derived source checks, 78 reached lifetime checks) pass at the same cut.
The original false105 fixture and both diagnostics retain zero state credit.
Actual 365-module composition over `88ddc64c5` passes strict compilation at
`78453102d` (5.083 s), preserving current retirement, string, GEN and PROPS paths
without renewing the private checks. Mixed/repeated/argument attributes, hooks and
wider wrapper protocols remain required. [Sensitive review](coverage/semantics/sensitive-parameter-review.json).

Promoted constructor parameters also accept the single builtin SensitiveParameter.
Value/reference property writes retain ordinary semantics; trace wrappers capture
later live CVs without creating a property Override obligation. Source8 passes at
separate bf6/688 cuts, including readonly/private/trait and ordered promotion
errors. Strict 365-module compilation and SL176 (74 derived, 102 reached checks)
pass at `75c4aba82`, including authentic queued-promotion admission. Earlier
Unsupported, method-continuation failure, fixture stops, false states and diagnostics
retain zero affected credit. Actual 367-module composition over `235a74c84`
passes strict initialization at `5448b4ba` (5.214 s), preserving current owner,
GC, GEN, PROPS, CALLS and returns paths without renewing private checks.
[Sensitive promotion review](coverage/semantics/sensitive-promotion-review.json).

Direct SensitiveParameterValue construction uses ordinary ordered argument sends
and stores an owning dereferenced snapshot. Arity precedes readonly re-entry;
named arguments, array COW, getter copies and final object release retain ordinary
semantics. Seven originals, strict compilation of 367 modules and SL121 (20
constructed, 101 reached checks) pass at `a50f9bc5`. Both checked baselines retain
Unsupported with zero agreement; the earlier raw-completion fixture preparation
was corrected before execution. Actual 367-module composition over `24c1b9e4`
passes strict initialization at `0e5152643` (5.351 s), preserving current assertion
fields and sibling constructor arms without renewing private source/state checks.
Uninitialized getter, debug/property and wider wrapper protocols
remain required. [Constructor review](coverage/semantics/sensitive-value-constructor-review.json).

First-class SensitiveParameterValue `getValue(...)` callables own their receiver
and snapshot through the existing getter-closure protocol. Five originals agree
at `db70c7a5`: array COW, argument priority, computed capture/alias and clone
ownership. Strict initialization of 367 modules and separate SL76 (15 derived,
61 reached checks) pass; four real steps verify capture, getter-copy ownership
and final destructor/weak-null release. Both checked baselines retain Unsupported
with zero agreement. Actual 368-module composition over `47accb555` passes strict
initialization at `f4ca5840` (5.209 s), retaining parent owner/runtime paths and
existing getter-closure ownership without renewing private checks.
[Getter review](coverage/semantics/sensitive-value-getter-review.json).

First-class wrapper constructors retain their initialized receiver through ordered
sends, arity checks and readonly rejection. Computed capture names stay fixed;
aliases, explicit/nullsafe invocation and clones preserve ownership. Five originals
agree across `420f47247`/`9602dbc4f`. Strict compilation of 368 modules and SL129
(27 derived, 102 reached checks) pass at `a9228bdd8`: real capture/SEND/Error steps
and final releases distinguish the callable's old value from the Error's rejected
replacement; saved caller queues authenticate nested argument calls. Both original
Unsupported baselines, the initial trace mismatch and fixture AL stop retain zero
affected credit. Binding/Closure::call and wider wrapper protocols remain partial.
Actual 370-module composition over `36b0c6948` passes strict initialization at
`b39a2a2b0` (5.284 s), preserving current factory/carrier and sibling runtime paths
without renewing the private source/state checks.
[Constructor callable review](coverage/semantics/sensitive-value-constructor-callables-review.json).

One zero-argument builtin `#[AllowDynamicProperties]` on a named nonreadonly
class resolves real namespace/import scope and permits inherited dynamic slots.
Allowed writes/reference creation and unset/recreation stay silent; ordinary
classes retain first-creation deprecation. Trait/interface/readonly targets fail
before body/interface checks, using the actual declaration keyword line.
Ten originals agree at separate `2945e171`/`8c37b2c6` cuts; a namespaced user
attribute remains Unsupported with zero agreement. Strict compilation of 370
modules and SL131 (37 derived, 94 reached checks) pass at `8c37b2c6`, including
real writes, inherited links and rejection of substituted compiled-name evidence.
The earlier trait-line mismatch and both pre-main fixture stops retain zero
affected credit. Mixed/repeated/argument attributes, anonymous/enum targets and
wider attribute protocols remain required. Actual 371-module composition over
`55c9c98a9` passes strict initialization at `9f2ed249d` (5.553 s), preserving
current GC/PROPS/ARG interfaces without renewing private source/state checks.
[Dynamic-property attribute review](coverage/semantics/allow-dynamic-properties-review.json).

Public backed by-value block and expression get hooks compile as authentic source functions
with the property's implicit return type. Ordinary CV and `$this` reads invoke
the hook; backing access bypasses it only in the active hook on that receiver.
Nested ordinary calls and other receivers dispatch normally, uninitialized
backing precedes magic, and traces retain `$value::get`. Eight originals and
strict compilation of 372 modules pass at `3ae28b26`. SL177 (19 derived, 158
reached checks) proves real entry/backing/throw steps and receiver/result cleanup,
including the payload parked across receiver destruction and final weak-null.
The virtual nested-closure control was Unsupported at that cut; prior compiler/fixture
stops, false states and diagnostics retain zero affected credit. Defaulted virtual/set/byref,
inheritance/traits, temporary/computed receivers, quiet/reference/indirect access
and hooked unset remain required. Actual 372-module composition over `48b6455fd`
passes strict initialization at `390c27db4` (5.421 s), preserving parent callable
and magic-get ownership paths without renewing the private source/state checks.
[Hook review](coverage/semantics/backed-get-hooks-review.json).
Expression bodies retain the actual expression origin and compiled return line,
including untyped return admission and saved Hook source during string conversion.
Seven new originals and strict 372-module initialization pass at `41ed4ea8d`;
SL137 (15 derived, 122 reached) proves actual return, saved conversion, parked
payload and final weak-null release. Its virtual declaration control was
Unsupported at that cut. These cuts retain the block results above. Actual 372-module
composition over `de44ad6d3` passes strict initialization at `5e3f9cbcf`
(5.448 s), preserving parent yield-from and magic-get dispatch without renewing
the private checks. [Expression review](coverage/semantics/expression-get-hooks-review.json).

Public by-value virtual get hooks without a default retain their declaration and
return type while owning no backing slot. Repeated reads execute the body;
ordinary writes evaluate the RHS before the read-only Error, without conversion.
Returned values survive receiver release and die when their last result owner is
removed. Literal string forms of `$this` and property names establish backing
correctly. Eight source agreements retain `90d182c4` (5) and `c4dd589c` (3),
including the two formerly Unsupported virtual controls. SL139 at `c4dd589c`
(13 derived, 126 reached) proves pending CV writes, forged-slot rejection and
result ownership; false135 and diagnostic runs retain zero credit. Hooked object
iteration is explicitly Unsupported; defaulted virtual/set/byref and wider
receiver/access families remain partial. Actual 374-module composition over
`2112d1e9` passes strict initialization at `964aa9e4` (5.479 s), retaining the
parent magic-get/reference paths and the private source/state cuts.
[Virtual hook review](coverage/semantics/virtual-get-hooks-review.json).

Literal CV/`$this` `isset` and `empty` now invoke public by-value backed/virtual
get hooks, preserve the property origin marker and distinguish returned nullness
from truthiness. Temporary returned objects die before branch output while the
receiver remains live. Strict374 and two original agreements pass at `f67a994c`;
SL162 at `ec1f309d` (143 reached, 19 derived) proves actual call/frame/boolean and
eager destructor/weak-null states. Earlier source failure, two AL stops and false162
retain zero affected credit. At that quiet cut, coalesce has only a derived parent
exclusion and no runtime/source credit; wider hook access remains required.
[Quiet hook review](coverage/semantics/quiet-get-hooks-review.json).
Actual375 composition over `b8f90d5` passes strict initialization at `a259f2ec`
(5.572 s), preserving parent magic-get verification and the private source/state cuts.

Literal CV/`$this` public by-value hook coalescing now retains the actual getter
value, including zero and false, and evaluates the original RHS only for null.
Two original agreements and strict375 pass at `0023fecf`; SL249 at `6be8d904`
(224 reached, 25 derived) proves source parent/RHS lines, ordinary result ownership
through decrement completion, and kept-object survival across receiver cleanup.
Earlier elaboration/fixture failures and diagnostics retain zero affected credit;
native/source/quiet cuts remain frozen. Wider hook families remain required.
[Coalesce review](coverage/semantics/coalesce-get-hooks-review.json).
Actual375 over `b0fc24b6` passes strict initialization at `4e98563e` (6.637 s);
the private source2/state249 cuts retain their original revisions.

Literal CV/`$this` public by-value hook `??=` retains returned false/zero and
evaluates the original RHS only for null, preserving its writable pending target.
RHS rebinding releases the old CV receiver before the current replacement receives
the store. Strict375 and three originals pass at `cc6ed080`; SL308 at `8e03445e`
(264 reached, 44 derived) checks actual call/frame/decision, This target ownership,
fallback/write lines, current-CV refetch and sole returned-object cleanup.
Earlier compiler/fixture failures and diagnostics retain zero affected credit;
the ordinary receiver control and prior hook cuts remain separate.
[Assignment review](coverage/semantics/coalesce-assignment-get-hooks-review.json).
Actual375 over `5709f4f8` passes strict initialization at `576cfa58` (5.829 s);
private source3/state308 and earlier hook cuts retain their original revisions.

Direct literal CV/`$this` unset of public backed/virtual get hooks raises `Error`
without dispatch or slot mutation, including inside the active getter. Strict375
and two originals pass at `7c7a322a`; SL182 at `3aa7cd48` (178 reached, 4 derived)
checks authentic errors, This root retirement and receiver/leaf cleanup through
`B|D` and weak-null. Magic-bearing originals remain native-only observations with
a declaration compiler stop; false182 and diagnostics retain zero affected credit.
`__unset` declarations/consumers, indirect access and wider hook families remain
required. [Unset review](coverage/semantics/hooked-unset-review.json).
Actual375 over `af067517` passes strict initialization at `99a51c34` (5.737 s),
preserving the private source2/state182 cuts and earlier failures.

Literal CV/`$this` public backed by-value hook `+=` uses the actual getter value
with an already evaluated integer RHS. It refetches the receiver after the RHS
and retains that selected receiver across getter rebinding, arithmetic and store.
Strict375 and three originals pass at `ee1ae2f1`. Separate state cuts retain
scalar291 at `77a0f81c` (265 reached, 26 derived) and affected receiver/lifetime129
at `7070262a` (all reached). Genuine pending TypeError cleanup releases the RV
while the selected receiver lives, then retires it before catch. False410 and
localization diagnostics retain zero whole-gate credit; earlier hook cuts stay
unchanged. [Addition-assignment review](coverage/semantics/backed-get-hook-addassign-review.json).
Actual375 over `d233bb59` passes strict initialization at `8f3aae08` (5.854 s),
preserving source3 and the separate scalar291/affected129 cuts.

Public backed by-value getters now override another public backed getter with
the same normalized property type in named subclasses. The child supplies one
effective slot/default and getter lexical scope; inherited `$this` reads retain
runtime descendant dispatch. Strict375 and two originals pass at `79d98c8e`.
Separate scalar238 at `a166611d` (213 reached, 25 derived) and retained lifetime97
at `e099fbf7` check child/private scope, backing access, exclusion/rollback and
returned-object ownership through inherited receiver destruction. Earlier AL
failures, false335 and localization diagnostics retain zero whole-gate credit.
Virtual cross-shapes, broader type compatibility and other hook inheritance
remain required. [Override review](coverage/semantics/backed-get-hook-override-review.json).
Actual375 over `b1e869f5` passes strict initialization at `4534b2c2` (5.747 s);
private source2/scalar238/lifetime97 retain their separate accepted revisions.

A public by-value child getter without backing access or an initializer now
retains a physical slot over an immediate parent whose getter body is backed,
with equal normalized types. The child's typed uninitialized or untyped null
default replaces the parent's default; ordinary writes and inherited `$this`
dispatch keep the child slot and scope. Strict375 and two originals pass at
`64d12f44`. Separate scalar185 (161 reached, 24 derived) and lifetime100
(all reached) pass at `b589ca70`, checking distinct stored/returned payload
cleanup. The combined285 timeout retains zero credit; M36 cuts remain frozen.
At this cut repeated body-unbacked overrides remained excluded; virtual parents
and broader hook inheritance remain required.
[Effective backing review](coverage/semantics/effective-backed-get-hook-review.json).
Actual375 over `7ba745ca` passes strict initialization at `5afd646c` (5.959 s);
private source2/scalar185/lifetime100 retain their separate accepted revisions.

Repeated public by-value getter overrides now retain physical backing through
body-unbacked equal-type declarations without initializers and intervening
classes without a redeclaration. A bounded walk follows authentic declaring
descriptors and source parent links to a backed getter; the latest child supplies
the slot/default and lexical scope. Strict375 and two originals pass at `2549e260`.
Separate state cuts
at `4dc91304` retain untyped58, lifetime109 and controls73 (42 reached, 31 derived);
CV62, inherited This74 and write60 pass at `4503b112`. These check uninitialized/null
defaults, private/called scope, ordinary writes, bounded ancestry refusals and
separate stored/returned-object cleanup. Counts include repeated setup and metadata.
Typed159/typed128 timeouts retain zero credit; M37 cuts stay frozen. At this cut,
virtual pairs without a backed anchor, ordinary-parent/plain redeclarations and broader hook inheritance
remain required. [Repeated override review](coverage/semantics/repeated-effective-backed-get-hook-review.json).
Actual375 over `2f3cbc4b` passes strict initialization at `b1176d40` (5.948 s);
private source2 and the six separate state cuts retain their accepted revisions.

Public by-value virtual getters without initializers now override another virtual
getter with identical normalized TYPE. A bounded positive ancestry check closes
at a genuine virtual root; child/private scope and runtime descendant dispatch
retain no physical slot. Writes raise runtime-class read-only errors at the actual
write line. Strict375 and two originals pass at `fbc19eb9`. Separate CV90 at
`5d5e6361` (63 reached, 27 derived), This87/writes74 at `2318e256` and lifetime95
at `44686722` check dispatch, pending errors, empty storage and kept-object cleanup.
The latter three groups are all reached; counts include four source setups.
Two AL fixture stops and This85 false retain zero credit. At that cut broader
virtual type covariance remained required; prior hook cuts stay frozen.
[Virtual override review](coverage/semantics/virtual-get-hook-override-review.json).
Actual375 over `8b17c9ec` passes strict initialization at `2d234593` (5.833 s);
private source2 and the four separate state cuts retain their accepted revisions.

Public get-only virtual overrides without initializers now accept covariant types
when both declarations have a type. Declaring scopes and active nominal ancestry
support builtin and class narrowing; physical backing stays invariant. Known
incompatible getter signatures fail at the hook line, preserving ordinary flag
error priority. Strict375 and three originals pass at `7259dc1c`. Separate CV115
(65 reached, 50 derived), This88 and lifetime100 pass at `1abdd809`; rejection14
passes at `4769720b`. These check actual dispatch/return types, kept Dog ownership
and line6 rejection before child publication. The original native recorder stop,
strict/AL stops, false fixtures and diagnostic retain zero affected credit;
the retained native process observations and prior hook cuts remain frozen.
[Covariance review](coverage/semantics/virtual-get-hook-covariance-review.json).
Actual375 over `3601e385` passes strict initialization at `c36d7732` (6.010 s);
private source3 and the four separate state cuts retain their accepted revisions.

Public get-only virtual overrides without initializers now reject removal of an
inherited type at the child getter line, before property-type compatibility.
A typed child overriding an untyped parent retains the existing class-line diagnostic;
both-untyped overrides retain child/private and descendant inherited `$this`
dispatch with no slots. Strict375 and three originals pass at `ce4a654b`, repairing
the removal case while preserving two baseline controls. Separate remove48
(26 reached, 22 derived), add26, CV62 and This64 pass at `fab1ea9c`; the latter
three are all reached. Counts include four source setups. Native's informational
anticipation-suffix miss and prior hook cuts remain frozen.
[Type-presence review](coverage/semantics/virtual-get-hook-type-presence-review.json).
Actual375 over `709fd7af` passes strict initialization at `8846907e` (5.822 s);
private source3 and four separate state cuts retain their accepted revisions.

Public source-body-backed get overrides with literal defaults now reject removal
of an inherited type at the child getter line, before property-type compatibility.
A typed child overriding an untyped parent retains the class-line error; the
both-untyped control keeps backing value 200 and getter result 213 through CV
and inherited `$this` reads, then stores 300 and returns 313. Strict375 and three originals pass at
`e3473265`, repairing one diagnostic and preserving two baseline controls. Separate
remove49 (26 reached,23 derived), add26, CV65, This67 and write63 pass at
`b739b230` (247 reached,23 derived across five setups). Runtime/storage and prior
M41 cuts remain unchanged.
[Backed type-presence review](coverage/semantics/backed-get-hook-type-presence-review.json).
Exact `e1166134` composition retains private strict/source/state cuts through
unchanged hook/type/task/schema paths; the disjoint additions require no new actor.

Public by-value getters now admit a genuinely body-backed child over a closed
virtual-parent ancestry with identical normalized TYPE. The child keeps its own
slot/default, active backing read and private scope; inherited `$this` dispatch
keeps the runtime descendant. Strict375 and two originals pass at `3f03c88b`.
Separate CV104 (69 reached, 35 derived), This68, write64 and lifetime104 pass at
`c6ff1271` (305 reached, 35 derived across four setups). These check child slot 200,
raw write 300/getter 313, ancestry refusals and stored-S release independently of
retained-R cleanup. Layout/default/runtime/owner rules and prior cuts stay unchanged.
[Virtual-parent review](coverage/semantics/virtual-parent-backed-get-hook-review.json).
Exact `c1198518` composition retains private strict/source/state cuts through
unchanged hook/layout/task interfaces; the disjoint additions require no new actor.

Virtual get-only parents now admit covariant own-body-backed children with both
TYPEs present. Builtin and linked nullable nominal narrowing retain the child
slot/default, private scope and inherited `$this` dispatch. An incompatible string
store preserves slot 300 and raises TypeError at line 36; getter widening fails at
hook line 6. Strict375 and three originals pass at `f902fe15`. Separate CV128
(72 reached, 56 derived) and This71 pass at `5cc79ee0`; write86, lifetime111 and
invalid18 pass at `d2ae7862` (358 reached, 56 derived across five setups).
The write fixture's literal-carrier correction preserves the original false cut
and both zero-credit localizations. Layout/default/tasks/pure variance remain
unchanged; backed-parent invariance, wider TYPE-presence and effective-backing
variance remain boundaries.
[Backed-child covariance review](coverage/semantics/virtual-parent-backed-get-hook-covariance-review.json).
Exact `e5f605aa` composition carries these cuts through unchanged hook/type/layout paths;
the disjoint parent additions require no current actor.

Closed virtual get-only parents now reject a genuine own-body-backed child
removing the inherited type at hook line 6, before the property-type check.
A typed child of an untyped parent retains the class-line error; both-untyped
controls keep an empty Parent and one Child slot through private/inherited `$this`
reads and write 300/getter 313. Strict375 and three originals pass at `03c2456e`,
repairing one diagnostic and preserving two baseline controls. Separate remove48
(26 reached, 22 derived), add26, CV69, This71 and write67 pass at `9573b369`
(259 reached, 22 derived across five setups). The original AL fixture-domain stop
stays zero credit; pure variance/layout/runtime and prior hook cuts stay unchanged.
[Cross-shape type-presence review](coverage/semantics/virtual-parent-backed-get-hook-type-presence-review.json).
Actual376 over `142e91d7` passes strict initialization at `9b39b8b1` (5.922 s);
private source3 and five selected state cuts retain their accepted revisions.

Typed source-body-backed parents now reject an untyped, body-unbacked child without
an initializer at hook line 6, before the property-type check. The reverse direction
retains its class-line error. Both-untyped controls distinguish Parent backing
100 from the inherited Child null slot, private/inherited reads returning 13,
and an ordinary write storing 300 while the getter stays 13. Strict376 and three
originals pass at `ea5a608c`, repairing one diagnostic and retaining two baseline
controls. Separate remove50 (26 reached, 24 derived), add26, CV69, This71 and
write67 pass at `3bbfe1af` (259 reached, 24 derived across five setups).
Pure variance/layout/runtime and earlier hook cuts retain their identities.
[Inherited-storage type-presence review](coverage/semantics/backed-parent-unbacked-get-hook-type-presence-review.json).
Exact `22dd4b27d` composition preserves these cuts through unchanged hook/type/layout paths;
disjoint file-notice, Stringable and reference-finally additions require no current actor.

Typed source-unbacked getters with published backing ancestry now reject an untyped
source-unbacked child without an initializer at the getter declaration. Across Bridge,
the error names declaring First at hook 10, before the property check at class 9;
reverse addition and repeated null-slot/read/write behavior remain baseline controls.
Strict376/source3 pass at `fdb60e53`; separate remove62 (32 reached, 30 derived),
add32, CV75, This77 and write73 pass at `bc534b7d` (289 reached, 30 derived).
The initial count-based scalar Unsupported remains zero credit; only six slot
predicates and its affected native/baseline were corrected. Pure variance/layout/
runtime and earlier cuts retain their identities.
[Effective-storage type-presence review](coverage/semantics/effective-backed-parent-unbacked-get-hook-type-presence-review.json).
The actual377 join over `cfd262d2` passes init-only strict at `7aed3831` (6.106s,
application0/source0); private source/state cuts retain their original identities.

Typed source-unbacked getters with published backing ancestry also reject an
untyped child with genuine backing access and its own default at the getter
declaration. Across Bridge, the error names declaring First at child hook 10,
before property class 9; reverse addition and the existing own-slot/read/write
behavior remain controls.
Strict377/source3 pass at `9b5a12dd`; separate remove65 (32 reached, 33 derived),
add32, CV75, This77 and write73 pass at `0b0acb56` (289 reached, 33 derived).
Controls distinguish Root 100, First null and child backing 200/getter 213, then
an ordinary write 300/getter 313. Pure variance/layout/runtime/lifetime and earlier
cuts retain their identities.
[Own-backed-child type-presence review](coverage/semantics/effective-backed-parent-backed-get-hook-type-presence-review.json).
Exact `5ab0f736` composition preserves these cuts through unchanged hook/type/layout paths;
disjoint object-Closure capture and dynamic-static binding require no current actor.

Ordinary public parent properties now link genuine own-body-backed, plain
by-value child getters with equal normalized TYPE. The proof authenticates actual
source/own descriptors and child ancestry across Bridge. Two originals formerly
Unsupported now match native: Parent 100 versus Child/Grand 200, private/inherited
result 213, then slot 300/getter 313; separate stored S and returned R cleanup.
Strict378/source2 pass at `0dda8304`; separate CV111 (70 reached, 41 derived),
This68, write64 and lifetime104 pass at `83b032a1` (306 reached, 41 derived).
Existing layout/default/store/task/owner rules and earlier cuts retain their identities;
wider plain-child inherited-getter shapes remain required.
[Ordinary-parent review](coverage/semantics/ordinary-parent-backed-get-hook-review.json).
Joined released `0940b7ee`/378 with retained private cuts and zero current actors;
incoming Closure/reference/WeakMap/operator/anonymous-factory paths are disjoint.

Ordinary public parent properties now retain physical storage under plain by-value
child getters without initializers or backing reads, with equal normalized TYPE.
A bounded parent-layout proof authenticates the ordinary source and actual child
ancestry across Bridge, supporting linking and physical classification. Typed
child slots start uninitialized; untyped slots start null. Writes store 300/5 while
getters remain 13/false; distinct stored S and returned R release separately.
Strict378/source2 pass at `8f8626b4`; CV117 (71 reached, 46 derived), This69 and
write65 pass at `ae89d874`, untyped79 and lifetime105 at `6e80fc03` (389 reached,
46 derived across five invocations). Two untyped AL fixture failures retain zero
credit; native NNULL supersedes the informational NEMPTY anticipation. Existing
default/layout/store/task/owner rules and earlier cuts retain their identities.
[Ordinary-storage review](coverage/semantics/ordinary-parent-unbacked-get-hook-review.json).
Joined exact `3fd8e25a`/380; one count-only current init check passes with no application.
Private source/state cuts remain retained through neutral shell state and disjoint incoming paths.

Repeated plain by-value getters without initializers or backing reads now retain
ordinary storage at equal normalized TYPE. Two parent-basis predicates carry the
authenticated ordinary anchor through the existing bounded hook ancestry walk;
defaults, layouts, stores and ownership rules remain unchanged. Across Bridge,
First and Second retain typed uninitialized/untyped null slots; latest private
getters return 13/0 independently of writes 300/5, with distinct S/R cleanup.
Strict380/source2 pass at `f56c3ad8`. Nine separate selected state checks pass
542 premises (497 reached, 45 derived), including repeated setup: controls at
`7d89eed2`, metadata/CV at `bb27b579`, This/write at `aff64add`, and untyped
metadata/read/write/lifetime at `0932752f`. Four SL caps retain zero credit;
authentic frontier partitions keep all assertions, with AL90 and affected SL150.
[Repeated ordinary-storage review](coverage/semantics/repeated-ordinary-unbacked-get-hook-review.json).
Joined exact `af903227`/381; one count-only current init check passes with no application.
Private cuts remain retained through neutral output-buffer state and disjoint incoming paths.

Removing the type from a source-unbacked child below a typed getter directly
backed by an ordinary Root now reports the getter error at child hook 10, naming
declaring First across Bridge. The existing missing-return guard accepts the
authenticated ordinary parent basis; reverse addition keeps property class 9.
Strict381/source3 pass at `196c13eb` (one repaired source, two baseline controls).
Three separate state checks pass at `814991e9`: remove62 (32 reached, 30 derived),
add32 and actual scalar plan47, totaling 111 reached plus 30 derived. Runtime,
defaults, layouts, pure covariance and earlier cuts retain their identities.
[Ordinary-backing type-presence review](coverage/semantics/ordinary-backed-parent-unbacked-get-hook-type-presence-review.json).
Joined exact `35068001`/381; one current init-only check passes with no application.
Private cuts remain retained through neutral EXITSTATUS 0 and disjoint WeakMap/source-exit paths.

Removing the type from a genuine own-body-backed child below the same ordinary-backed
First now reports the getter error at child hook 10, naming First across Bridge,
before property class 9. One sixth-arm parent-basis OR repairs this priority;
reverse addition and child backing 200→300/getter 213→313 remain baseline controls.
Strict381/source3 pass at `37bc2d87`. Three separate state checks at `0e0d255d`
pass remove62 (32 reached, 30 derived), add32 and entered-getter50: 114 reached
plus 30 derived. Runtime, defaults, layouts, pure covariance and ownership stay unchanged.
[Own-backed type-presence review](coverage/semantics/ordinary-backed-parent-backed-get-hook-type-presence-review.json).
Joined exact `08666ae75`/382; one count-only current init check passes with no application.
Private cuts remain retained through disjoint comparison, update-warning and ref-chain paths.

A public plain child property of equal normalized TYPE now inherits a genuinely
backed parent getter across Bridge. Its effective property/default/slot remain
Child's (200→300), while function, lexical/private scope and trace class remain
Parent's; called scope follows Child or Grand. Strict382/source1 pass at `771ad7b9`.
Four separate states at `6617e08a` pass controls69 (33 reached, 36 derived),
Child entry52, inherited Grand54 and write68: 207 reached plus 36 derived.
The original anticipation-encoding failure and two AL fixture failures remain zero.
Wider inherited-getter and hook/type/reference families remain required.
[Inherited-getter review](coverage/semantics/plain-child-inherited-backed-get-hook-review.json).
Joined exact `706af40d`/383; one count-only current init check passes with no application.
Private cuts remain retained through neutral tick state and disjoint incoming callback/source paths.

Repeated public plain properties of equal normalized TYPE now retain the original
backed getter through a bounded, authenticated ancestry walk. First's default 200
gives way to Second's default 300; Grand writes 400 and gets 413. Second supplies
the property and slot, Parent the function, lexical/private scope and trace, and
the receiver its called class. Strict383/source1 pass at `9d0e4d88`; four separate
states at `55768b65` pass controls91 (45 reached, 46 derived), Second64, Grand66 and
writer80: 255 reached plus 46 derived. Defaults/layouts/stores/owners remain unchanged.
Other inherited getter roots, wider type/reference/trait/flag families remain required.
[Repeated inherited-getter review](coverage/semantics/repeated-plain-child-inherited-backed-get-hook-review.json).
Joined exact `61cd4dc8`/384; one count-only current init check passes with no application.
Private cuts remain retained through disjoint aggregate/update-warning and WeakMap callback paths.

A public equal-normalized-TYPE plain Child now inherits a source-unbacked getter
directly backed by an ordinary Root. One terminal guard accepts the authenticated
ordinary proof with its supplied fuel; defaults, layouts, stores and owners are unchanged.
Typed Parent starts uninitialized; Child owns 200 then 300 while the getter returns 13.
Parent retains function/lexical/private/trace identity, receiver its called scope;
active source backing bypass is false. Strict384/source1 pass at `3e6ef25b`.
Three separate states at `2171db7c` pass controls82 (42 reached, 40 derived),
entered Child61 and writer77: 180 reached plus 40 derived. D40 is task-local
parent matching, not another native class case; wider inherited roots remain required.
[Ordinary-backed inherited-getter review](coverage/semantics/ordinary-backed-parent-plain-inherited-getter-review.json).
Joined exact `b55942bc`/385; one count-only current init check passes with no application.
Private cuts remain retained through neutral output-handler state and disjoint reference-return cleanup.

A source-unbacked Parent getter over a genuinely body-backed hooked Root can now
be inherited by an equal-normalized-TYPE plain Child across Bridge. One terminal
OR uses the existing inherited backing walk with supplied fuel; nearest Parent
remains the getter descriptor. Root100/get107/private7 is only the backing witness;
Parent starts uninitialized, Child owns 200 then 300, and Parent's getter/private13
remains independent with false active bypass and actual receiver called scope.
Strict385/source1 pass at `42870592`; three separate states at `953039ba` pass
controls95 (49 reached, 46 derived), Child68 and writer84: 201 reached plus 46 derived.
Root-source removal is derived and D46 task-local; no new default/layout/store/owner
or lifetime behavior is claimed. Wider inherited roots and hook families remain required.
[Hook-backed inherited-getter review](coverage/semantics/inherited-backed-parent-plain-inherited-getter-review.json).
Joined exact `98d1efd6`/385 by pointwise compatibility bridge; zero current actors.
Private cuts remain retained through hook-excluded plain projection and disjoint comparison/lifecycle paths.

A public plain Child of equal normalized TYPE now inherits a closed virtual Parent
get-only getter across Bridge. One terminal basis uses the existing virtual chain
with supplied fuel; Parent owns no slot, while Child owns 200 then 300. Original
Parent function/lexical/private/trace and receiver called scope remain distinct;
the getter returns 13 with false active source bypass. Strict385/source1 pass at
`55fd8584`; three separate states at `1e2c28c0` pass controls84 (39 reached, 45 derived),
Child58 and writer74: 171 reached plus 45 derived. D45 is task-local matching; no
new classifier/layout/default/store/owner or lifetime behavior is claimed. Wider
roots and hook/type/reference families remain required.
[Virtual-root inherited-getter review](coverage/semantics/virtual-parent-plain-inherited-getter-review.json).

Closed virtual get-only Parent to plain Child now recognizes covariance separately
from linked compatible admission. The selected mixed→int original preserves Parent's
mixed getter/string "13" while Child's slot changes 200 to 300; reverse int→mixed
reports the subtype property error at class13 before Child publication. No getter
return/coercion or physical/default/layout/store/owner rules changed. Strict385 and
source2 pass at `5012d481`; four separate states at `c5bfa53f` pass controls95
(41 reached, 54 derived), Child67, writer76 and reverse26: 210 reached plus 54 derived.
Natives were observed separately; the positive wrong-invariant baseline keeps zero
agreement. Wider types/roots/flags/hook families remain required.
[Plain-child covariance review](coverage/semantics/virtual-parent-covariant-plain-inherited-getter-review.json).
Joined exact `fdf9903d`/386; one count-only current init check passes with no application.
Private cuts remain retained through neutral output/compile-error state and disjoint destructor/WeakMap paths.

Closed virtual public get-only Parent now admits an equal-TYPE plain public
protected(set) Child. Parent owns no slot; Child/Grand start at 200, global denial
leaves 200, and Child/Parent scopes store 300/400 while the inherited getter uses
Parent's private method and returns 13 with receiver called scope and false bypass.
A body-backed public-set Parent retains its narrowing rejection at class11.
Strict386/source2 pass at `1f4fae54`; five separate states retain controls100 at
`e69b3571` and corrected denied68/Child83/Parent83/backed25 at `a648488c`:
316 reached plus 43 derived. Initial declaration and denied fixture failures remain
zero; the diagnostic and native newline anticipation miss are retained separately.
Existing TYPE/default/layout/store/permission/owner rules are unchanged; wider
setter/flags/hook families remain required.
[Protected setter review](coverage/semantics/virtual-parent-protected-set-plain-inherited-getter-review.json).
Joined exact `2fa9fb92`/386; one current init-only check passes with no application.
Private cuts remain retained through inactive runtime journals and disjoint update-warning/WeakMap paths.

Closed virtual int Parent to plain untyped Child now reports the subtype property
error at class13. No child getter is synthesized; reverse addition under an
untyped Parent still requires omitted TYPE. Both-untyped inheritance retains
Parent's untyped string "13" getter and private scope, empty Parent storage versus
NULL metadata, and own Child/Grand slot200→300 with false active backing bypass.
Strict386/source3 pass at `e03ade5d`; three separate states at `da64048c` pass
remove71 (36 reached, 35 derived), add26 and entered67: 129 reached plus 35 derived.
Only diagnostic-family routing changed; pure variance and runtime/default/layout/
store/owner rules are unchanged. The removal article hypothesis miss is
informational/raw-preserved; no failed actor. Wider hook/type roots and flags
remain required.
[Plain-child type-presence review](coverage/semantics/virtual-parent-plain-type-presence-review.json).
Joined exact `0df6172c`/387; one count-only current init check passes with no application.
Private cuts remain retained through inactive output-handler/Stringable cleanup and empty output buffers.

Repeated equal-TYPE protected(set) plain First -> Bridge -> Second now resolves
the original virtual Parent getter. Parent owns no slot, First owns 200 and
Second/Grand own 300; a real Second-scope write stores 400 while the inherited
Parent private method still yields 13 with receiver called scope and false bypass.
Later private(set) narrowing names immediate First at class17. Only two metadata
edge guards changed; source/own/link/fuel closure and runtime permissions,
defaults/layouts/stores/owners remain unchanged. Strict387/source2 pass at
`87331b33`; four separate states at `64d31c3a` pass controls106 (54 reached,
52 derived), Second73, writer93 and narrow23: 243 reached plus 52 derived.
No failed actor; broader setter/type/root/hook families remain required.
[Repeated protected-setter review](coverage/semantics/repeated-protected-plain-inherited-getter-review.json).
Joined exact `aba5383e`/387; one retained current init check passes with no application.
Private cuts remain retained through inactive warning-callback, recorded-function and WeakMap paths.

A direct trait’s public body-backed by-value `int` getter now imports with an
authenticated Consumer callable and property, preserving physical Trait code and
`__METHOD__` spelling. Consumer lexical/private13 and receiver called scope stay
distinct; real backing100→300 yields113→313. Even an identical plain own property
conflicts before Consumer publication: raw runtime STATICBYTES at class10 and
public php_error/CompileError are distinct observations. Strict387 passes at
`10c953cb`; scalar and collision source agreements are separate retained cuts.
Four states pass267 =231 reached +36 derived (first235 at `ea101806`, collision32
at `37476242`). Initial compiler, recorder-classification and fixture failures
remain zero; wider trait hook imports/types/flags/ref/set/lifetime remain required.
[Imported trait getter review](coverage/semantics/trait-imported-backed-getter-review.json).
Joined exact `7d361d4c`/388; the count-only current init passes with no application.
Private cuts retain their identities through the hooked-slot cast and inactive callback/fatal paths.

Direct public virtual get-only `int` trait getters now import with no
initializer or physical slot. Consumer lexical/private13, Trait magic spelling
and receiver called scope remain distinct; a Grand write raises its exact
read-only Error and leaves both objects empty. Only compiler/import admission
changes; storage, classifier and permission rules stay unchanged. Strict388 and
source1 pass at `287151403`; three states at `0265e795` pass242 =205 reached
+37 derived. Default/initializer/header refusals are derived, no failed actor;
wider trait hook shapes remain required.
[Virtual trait getter review](coverage/semantics/trait-imported-virtual-getter-review.json).

Body-backed expression trait getters now use physical expression tasks with
authenticated logical Consumer returns. Trait magic, Consumer private13 and
receiver called scope stay distinct; Grand backing100→300 yields113→313.
Initial strict388 at `ed187985` is retained; its source interpreter failure
remains0. Corrected source1 passes at `d745b7d5`, and three states at
`d1bfb49b` pass263 =240 reached +23 derived. Global arrow, storage and permission
rules stay unchanged; wider imports remain required.
[Expression trait getter review](coverage/semantics/trait-imported-expression-getter-review.json).
Joined exact `e3ba712d`/388 with no current actor; accepted private cuts retain their identities.
Inactive callback-destructor exit and WeakMap GC paths preserve the ordinary expression/getter/write route.

Virtual expression trait getters now import through the existing source-authenticated
virtual proof, retaining absent initializer, no physical slots and false backing
bypass. Consumer private13 receives Trait magic; Grand’s read-only write leaves
storage empty and getter13. Strict388/source1 pass at `2cd696e2`; three new states
at `74403ac7` pass284 =247 reached +37 derived. A separate updated M65 controls75
passes; its old source/entry/write and ledger identities remain historical.
Only the body-kind fence is removed; storage/permissions and expression tasks
are unchanged. [Virtual expression trait review](coverage/semantics/trait-imported-virtual-expression-getter-review.json).
Joined exact `f52c92f1`/389; count-only initialization adds no source/state credit.
Hooked empty-slot casts keep their marked route; define/defined/Fiber and object-comparison protocols are absent.

A direct backed expression trait getter now imports into a named class with a
real source parent and no same-name parent property. Prelink admission and
published matching-link proof stay separate. Genuine Base parentRead→Consumer
getter scope/private13/Trait magic and Grand100→300/get313 preserve marker700.
Strict389 at `9b38e2a0` is retained; its later inherited-hook Unsupported remains0.
Corrected source1 passes at `304ec0f6`; three states at `940d92d2` pass294 =266
reached +28 derived. Only parent admission and the authenticated absent-name
fallback change; layout/storage/permissions and expression/return rules remain.
[Parented trait getter review](coverage/semantics/parented-trait-expression-getter-review.json).
Joined exact `2bb4e1b6`/390; count-only initialization adds no source/state credit.
Empty-buffer output, ordinary Base/getter targets and absent define/defined callbacks preserve the accepted route.

Selected ordinary public same-name Base properties now admit a direct backed
expression trait getter. Existing inheritance checking accepts int10→imported
int100 and rejects Base string at Consumer16; only parent-shape admission changes.
A single physical value slot, marker700, Base caller versus Consumer/private13
and Grand300/get313 pass. Strict390/source2 at `48321a13` and four states at
`154e2cb9` pass349 =319 reached +30 derived. Separately, only the superseded M67
controls74 pass; its old ledger/source/entry/write identities remain historical.
The initial setter-mutation elaboration stop remains0.
[Inherited overlap review](coverage/semantics/inherited-overlap-trait-getter-review.json).
Joined exact `5f6f84e7`/391; count-only initialization adds no source/state credit.
Inactive comparison, define-warning, output-reference and WeakMap paths preserve the accepted class routes.

Selected private ordinary same-name Base properties now admit a direct backed
expression trait getter with distinct private/public keys. Lexical Base reads7
without entering the public hook; Grand100→300/get313 preserves private7,
marker700 and Consumer100. Strict391 at `cebf4954` is retained; its source refusal
at Base parentRead remains0. The one-premise read-selection correction passes
source1 at `a5833e7b`; three states at `38ee1514` pass277 =242 reached +35 derived.
Layout/storage/permission and expression task/return rules remain unchanged.
[Private overlap review](coverage/semantics/private-overlap-trait-getter-review.json).
Joined exact `21189749f`/391; retained initialization adds no source/state credit.
Absent warning-destructor previous-owner tasks, Iterator unpack and define calls preserve the accepted private/public route.

Selected one-level nested backed expression trait getters now authenticate both
real use edges and the intermediate Outer own row. Final Consumer keeps raw
Inner code/magic and its own lexical/private scope; Grand100→300 yields313.
The original Outer collision already agrees at `111a5e2d`; legal scalar1 and
strict391 pass at `18164dde`. Two states at `713efd41` pass 223 premises
(184 reached + 39 derived). Initial strict constructor elaboration remains0; no
collision or earlier trait actor is renewed.
[Nested trait getter review](coverage/semantics/nested-trait-getter-review.json).
Joined exact `beb13e29`/391 by pointwise review; no current actor or renewed source/state credit.
Absent Throwable/Stringable comparisons, WeakMap replacement and define calls preserve the accepted export route.

Selected backed set-only class hooks now authenticate an implicit property-typed
value parameter, void return, actual call/frame and active backing write. Input20
returns20 while Parent private13 transforms storage to33; bad-array receipt fails
before the body with caller21 and keeps33. Ordinary reads stay physical.
Strict392/source1 retain `be58adae`; three states at `76e562ef` pass234 =208 reached
+26 derived. Initial parse and transient-validator failure/diagnostic remain0; the
unchanged controls fixture passes after the cons-form validator correction.
[Set-only hook review](coverage/semantics/backed-set-only-hook-review.json).
Joined exact `b128c9da`/393; count-corrected initialization adds no source/state credit.
Absent numeric-comparison, defined/autoload, unpack and computed-ref-return protocols preserve the accepted setter route.

Selected public typed statement pairs ordered get then set now compile two indexed
functions and share active-property/receiver backing access. GET’s write6 does
not enter SET; SET’s read10 does not enter GET. Physical10/get23 becomes
assignment20/physical33/get46, with pre-body array rejection/caller26 unchanged.
Strict393 passes at `545e6e20`; corrected source1 at `169aafa5` matches native.
Two states at `1d7facd8` pass210 =181 reached +29 derived. Initial source failure
remains0; one EPS premise disjoins the paired and setter-only classifiers.
[Paired-hook review](coverage/semantics/paired-backed-get-set-hook-review.json).
Joined exact `43cc7432`/394; CPU2-pinned initialization passes and the unpinned original is retained.
Absent warning, include/NUL, computed-ref-return and Iterator-unpack protocols preserve the accepted pair route.

Selected sole backed SET hooks now compile an actual explicit typed/defaultless
parameter, retaining its source name/type and property-to-parameter compatibility.
The string `"20"` is received unchanged, the body stores `33`, and assignment returns
the original string; bad array input retains Param4/caller21. Incompatible string-only
SET rejects at hook ENDLINE7 after body compilation. Strict394/source2 pass at
`b5e89715`; three states at `7f54c43d` pass270 =238 reached +32 derived, including
actual receive/result restoration and genuine compiler rejection. The original
Unsupported baseline/native/preparations retain0; no old hook actors were renewed.
[Explicit-parameter review](coverage/semantics/explicit-setter-parameter-review.json).
Joined exact `b8b92ac0`/394; retained initialization passes on CPU2 without source/state renewal.
Absent divide-warning, Iterator-unpack, computed-ref-return and constant/object-comparison routes preserve the accepted setter path.

Exact reference returns99 avoid unchanged checked writes during verification,
acquisition and156 repeated finalizer checks. Genuine backing certificates,
selected cells and property sources survive; conversions, quiet initialization
and later ordinary writes remain checked. Sixteen of17 focused originals agree,
with private358 independent35 and13 source-reached fixtures/483 assertions passing.
Actual359 over6536a8339 passes strict SL compilation at37b08adeb (4.679s);
those source/state cuts and the original seventeenth failure retain their identities.
[Exact-return review](coverage/semantics/reference-return-exact-review.json).

Delayed reference-return TypeError now re-enters the protected exception chain
once, preserving pending-error ownership, selected catch eligibility and code
after a caught try. Ten replay originals agree at `247446c` (360 modules), including
the former `F|F|R|SHARED` mismatch; 14 source-reached current/saved fixtures pass
954 assertions.
Four preserved affected return controls and one core-only terminal weak-conversion
control agree. The 361-module composition over `5b7452edd` passes separate strict
compilation at `2c3dbf30`.
The old prediction, pre-evaluation declaration failure and Unsupported `gettype`
observer remain zero-credit at their original cuts. Physical-array owners,
active-finalizer replay,
protected temporary/NULL Notice timing and Stringable reference conversion remain
required. [Replay review](coverage/semantics/reference-return-replay-review.json).

Source-authenticated while/do/for tails now recover after caught delayed reference
rejection without repeating initialization. Break/continue depth, goto labels and
try/catch origin survive named, method and closure frames. Fourteen originals
agree at retained private361 cuts; 15 reached current/saved fixtures pass 1,102
assertions (13/973 at51eb, corrected label/direct2/129 at89e). The actual361
composition over `cf9411d` passes strict compilation at `c5579f5d` (4.878s).
Fixture elaboration and label-finder failures retain zero affected credit.
Physical-array owners, active-finalizer replay and protected temporary/NULL
Notice/Stringable paths remain required.
[Scalar replay review](coverage/semantics/reference-return-scalar-replay-review.json).

Source-authenticated CV/compiled-CONST switch tails now recover selected-case
remainder and fallthrough without repeating subject or case evaluation. Paired
END/PHASE metadata adds no payload roots or freeable owner and preserves catch
scope through current/saved frames, goto and abrupt transfer. Seven preserved
originals and 14 reached fixtures/1,339 assertions pass at retained private361
cuts; actual361 over `dd6478b` passes strict compilation at `3c06eba5` (4.880s).
The selected-catch admission failure keeps zero affected credit at its original cut. Runtime VAR/TMP
array owners, active-finalizer replay and protected NULL/186 paths remain open.
[Switch replay review](coverage/semantics/reference-return-switch-replay-review.json).

Protected reference returns now preserve the first cleanup of mutable, refcounted
switch temporaries and dense value-foreach owners. Non-owning rows retain physical
identity/cursor through current and saved frames, authenticated replacement and replay.
Capture conservatively requires at least three genuine owning edges before cleanup
and two after; aliases sharing a cell count once. Later one-owner reads remain live;
collected switch END reads nothing, while collected foreach fetch stops explicitly.
Thirteen originals pass at private362 cuts: four exact native tuples and nine deliberate
c/d=8(native) to1(spec) differences, with zero agreement for those nine. State23/1,873
and independent pending98 pass across retained cuts. Actual364 over `2c1283f04` passes
strict at `31838d5ad` (5.033s) and one genuine carrier bridge/71 assertions. Original
failures/timeouts remain zero-credit. Wider payloads, active-finalizer replay and
Stringable186 remain required. [Owner review](coverage/semantics/reference-return-retired-owner-review.json).

By-reference VALUE, bare/null and implicit-return Notices now dispatch after protected
finalizers and repeated type checks. Captured source and line survive saved handlers;
throwing handlers leave through ordinary cleanup, and replacing variable returns cancel
the old Notice. Six focused originals and one protected-unused control agree at retained
private cuts with 365 modules. Eight reached current/saved fixtures pass 722 assertions (315+407);
Actual 367-module composition over `d23ed96e6` passes strict compilation at `8d7fad70e` (5.082 s), with zero application evaluations. Stringable186
and wider owner domains remain required.
[Notice review](coverage/semantics/reference-return-notice-review.json).

Delayed rejection inside one already-active finalizer now preserves its consumed
ordinary CV reference-return cursor without retaining the discarded operand root.
Uncaught errors cross that consumed continuation once; a local catch resumes the
cleared old return, whose NULL recheck can re-enter the outer finalizer. Successful
replacement keeps the selected new alias. Three originals agree at `d12494664`;
eight source-reached current/saved fixtures pass 602 assertions (277+325).
Actual367 over `99f3432e` passes strict compilation at `5b40480dc` (5.173s, zero
application evaluations); its cut stays separate in the
[active-finalizer review](coverage/semantics/reference-return-active-finalizer-review.json).
Wider consumed VALUE/CONST/NULL and multiple-active-finalizer histories,
wider Stringable CV layouts and owner domains remain required.

One consumed string literal compiled as CONST now resumes its original interned
value after an inner delayed TypeError is caught in an already-active finalizer.
Its non-owning source cursor restores one VALUE Notice at the original return
line after the catch and finalizer tail. A fresh returned cell keeps the caller
write separate from the globals. Two exact originals agree at `bdb0f010` and
`1341b27f`; three reached current/saved fixtures pass 347 assertions at `9b98849d`.
Actual 371 over `88d7e5d4c` passes strict at `682126ff1` (5.413s, zero application evaluations).
The [consumed-literal review](coverage/semantics/reference-return-consumed-literal-review.json) keeps these cuts distinct.

Consumed explicit `return null` now resumes its original NULL value after a
locally caught inner rejection in one already-active finalizer. The checked
special-constant source restores one VALUE Notice at the original line, without
an operand root. A fresh returned cell keeps the caller write separate from the
globals. Two originals agree at `ec95462f7`; three reached
current/saved fixtures pass 367 assertions at `459978fe0`.
Actual 371 over `05b0a4db4` passes strict at `c93d4cba4` (5.339s, zero application evaluations).
[Consumed-NULL review](coverage/semantics/reference-return-consumed-null-review.json).

Consumed computed string returns resume cleared NULL after a locally caught
inner rejection. The bounded source concatenates a named zero-argument call
with an empty string; its cursor retains no old payload and never repeats
the call. One original VALUE Notice remains pending at the public pause.
Nonnullable string rejects NULL before delivery, reenters the outer finalizer
and later returns the selected y alias (source1/state3-386 in the
[computed-VALUE review](coverage/semantics/reference-return-consumed-value-review.json)).
The checked ordered string|null mask instead accepts NULL, delivers one
original-line Notice and returns a fresh caller cell distinct from x and y,
with no second finalizer entry. One nullable original agrees at `dffae89b0`;
three reached current/saved fixtures pass 381 assertions at `4e6396234`.
Actual 372 over `c2e06b6d7` passes strict at `2094ee751` (5.562s, zero application evaluations).
[Nullable computed-VALUE review](coverage/semantics/reference-return-consumed-value-nullable-review.json).

Two already-active ordinary CV finalizers now retain ordered non-owning history
in a named reference-return function with the exact string signature and no
destructor operation at capture. Genuine Z then X task/phase/restore triples
are consumed separately; old operands acquire no new roots. Inner rejection
replays its finalizer, then leaves Z and X in order. Initial successful
replacement retires both certificates and returns the selected y alias.
Two originals agree at `e2275499a`; four reached current/saved
fixtures pass 439 assertions at `ddc500037`.
Actual 374 over `626142838` passes strict at `eef043fe1` (5.610s, zero application evaluations).
[Two-history CV review](coverage/semantics/reference-return-multiple-active-cv-review.json).
Locally caught inner rejection now resumes the consumed middle CV as cleared NULL.
The atomic Z/X restoration carries no old operand root; NULL rejection creates a
fresh TypeError at Z's line, replays its finalizer and retains the outer history
through saved ping frames before the selected y alias returns. One original
agrees at `478eb1e4`; three reached current/saved fixtures pass 391 assertions
(163+80+148) at `0068f567`. Private strict374 passes at `478eb1e4` in 5.513s.
Actual375 over `204200d1` passes strict at `45223cc60` in 5.546s,
with zero application evaluations; private source/state cuts keep their identities.
The helper-internal first Z leave is not a public frontier; missing CLEARED is
helper refusal only. The old state439 caught-Unsupported boundary is superseded
only for this slice.

An immutable outer string literal now shares the ordered pair with ordinary Z/Y
CV returns. Source-equal interned history owns no cell; replacement cancels its
VALUE Notice. Caught inner rejection replays cleared Z with the literal history
retained; successful Y or error escape retires it with x/z unchanged. Three exact
originals agree at `46247e9b`; five reached fixtures pass 461 assertions
(133+139+66+62+61) at `beec37fa`, and independent three/187 pass at `56f553af`.
Private strict374 at `46247e9b` passes in 5.767s with zero applications.
Actual375 over `0228435a` passes strict at `cdf702106` in 5.533s,
with zero application evaluations; private source/state cuts keep their identities.
At this cut, actual outer-literal resumption/Notice remained required.

An authenticated catch passage now preserves the middle CV and outer literal
histories while ordinary catch/finalizer statements run. Four reached pending
suffixes retain the actual D/outer-finally origin; Y has three replay contexts
and Z has two. After caught Y rejection, M2 skips Y; Z's fresh NULL TypeError
reaches D, then B and the original literal resume with one original-line VALUE
Notice and a fresh caller cell distinct from x/z/y. Three exact originals and
strict375 pass at `9b206d38` (5.581s, zero applications). Five reached fixtures
pass 480 assertions (176+140+60+51+53) at `dfe52b85`, including public zero-budget
admission of the expanded pair; independent pending63/7 passes at `9b206d38`.
The retained capture176/four compilations and affected group2/remaining groups
keep their separate raw cuts. Original compiler/fixture failures and the expanded
descriptor discrepancy remain preserved in the same review. The first-Z helper
remains nonpublic; other passages/layouts, lifecycle capture, wider operands and
complete returns verification remain open.
Actual375 over `5e28bb06` passes strict at `83375f47` in 5.663s,
with zero application evaluations; private source/state/independent cuts remain separate.

The catch passage also admits a checked named no-argument call before B. At
`e4d16551`, three originals agree and six reached fixtures pass 514 assertions
(155+55+140+60+51+53); independent saved post-D ping70/4 passes separately.
Pending4/3 retain D scope and 2/1/0 follow its actual restore; the saved call keeps
root-free literal history/Notice0, then D;P;B restores one Notice and a fresh cell.
Private strict375 passes in 5.659s with zero applications. Throwing, mutating and
reentrant call bodies and broad returns_verify remain OPEN.
Actual375 over `15951738` passes strict at `c1d95aaf` in 5.785s,
with zero applications; private source/state/independent cuts retain their revisions.

Adjacent ordinary CV histories now use an ordered non-owning cursor list when
more than two finalizers are active. Checked source authenticates every return,
phase3/restore triple, distinct CV and protected path; partial capture retires
each old operand root once. The observed Z/W/X chain survives Y TypeError replay
and saved ping frames, then leaves all three histories in order. Initial success
keeps the selected y alias. Two originals agree at `5a9fd5ba`; five reached
fixtures pass 467 assertions (132+78+76+99+82), and independent partial90/7 passes
separately. Private strict375 passes in 5.719s with zero applications. Earlier
dispatch and fixture failures retain zero agreement credit. Other caught/mixed
layouts, lifecycle capture and broad returns_verify remain OPEN. [Ordered-chain review](coverage/semantics/reference-return-multiple-active-cv-review.json).
Actual375 over `324d3f88` passes strict at `d68bbf48` in 5.857s,
with zero applications; private source/state/independent cuts retain their revisions.

A source-authenticated singleton TypeError catch in the selected owner now
resumes the ordinary Z/W/X chain through atomic root-free cleared NULL. First-Z
source/line/recheck survive every internal leave; its fresh NULL TypeError stays
distinct from the live Y error while W/X replay and saved ping scope restore.
Rethrow carries the original Y error to the caller. Three originals agree at
`cc93bbac`; six reached fixtures pass 640 assertions (138+84+136+93+83+106),
with first three states and five compilations retained from the original wave.
Independent CLEARED75/5 passes separately. The saved-callsite fixture correction
keeps its original group4 failure at zero credit; immediate Y success is source3
evidence only and helper partial leaves remain nonpublic. Private strict375
passes in 5.888s with zero applications. Other caught/mixed layouts, lifecycle
capture and broad returns_verify remain OPEN. Actual375 over `52180b3f` passes
strict at `2d6ea69f4` in 6.082s with zero applications; private cuts remain separate.

The ordered chain now permits a source-equal interned string only as its last
history, with inner Z/W/Y ordinary CVs. Initial VALUE Notice is canceled before
capture; the root-free literal survives saved Y replay, then ordered error escape
or selected-Y success retires it. Two originals and five reached fixtures/504
assertions (165+78+78+101+82) pass at `d28f2a0c`; independent partial96/8 is
separate. Private strict375 passes in 5.831s with zero applications. The original
597 elaboration failure keeps zero credit. At that cut, normal mixed clearing/resumption,
other operand/layout/lifecycle domains and broad returns_verify remain OPEN. Actual375 over
`d6df5f11` passes strict at `9d6c4a4e` in 5.814s with zero applications;
private source/state/independent cuts remain separate.

The checked C/IF/E passage now carries Z/W/old literal history through Y rejection,
fresh Z-NULL error and saved M2 scope. E/B resumes old once with its original line4
Notice and a fresh caller return cell; selected Y keeps its alias, while E rethrow
retires W/old with the identical fresh-Z error. Source3 and one affected old643
compatibility pass at `4336a2a2`; eight reached fixtures/811 assertions pass with
first7/705 retained there and final106 at validator-only `3abcfc78`.
Independent E-prefix2 four/297 checks and five public refusals pass separately.
Private strict375 passes in 5.794s with zero applications; original failures and
timeouts keep zero credit. Maintained producer `511ed517` removes only one EOF
newline from tested c670 and preserves its AST. Exact-length Cons suffixes avoid
a confirmed pinned SpecTec dispatch overlap limitation without a vendor edit.
Other mixed layouts, lifecycle/typed capture, effectful calls and broad
returns_verify remain OPEN. Actual375 over `4f93b073` passes strict at
`36238b5f` in 5.980s with zero applications; private cuts remain separate.

The checked E catch now admits a named zero-argument call before its literal echo,
with optional rethrow of the same catch CV. The measured pure `ping()` call preserves
the parked W/old history and fresh Z TypeError through its saved f frame, then resumes
E/B and old with one original-line Notice/fresh caller cell, or retires history on
rethrow. Selected Y keeps its alias and cancels that call. Three original sources,
three reached fixtures/301 assertions and an independent saved-frame80/1 check pass
at `e18e338a`; private strict375 passes in 5.954s with zero applications. The maintained
producer is byte-identical to tested ac7c; original fixture elaboration failures retain
zero credit. The syntactic named-call admission is wider than this pure E-call evidence;
mutating/reentrant/suspending calls, other catch layouts and broad returns_verify remain
OPEN. The [multiple-history review](coverage/semantics/reference-return-multiple-active-cv-review.json)
keeps these cuts separate from earlier replay and the next abrupt-callee probe.
Actual375 over `fd12fd35` passes strict at `5001d1f8` in 5.927s with zero
applications; original private source/state/independent cuts remain separate.

Guarded E-call reentry now restores a missing pending VALUE Notice when throw
retirement exposes the surviving live literal return. Restoration preserves its
source/line and emits nothing; nested unused `f()` delivers one Notice before T,
and outer return delivers one additional Notice. E rethrow emits neither. The
helper excludes NULL-return forms and access-reference VALUE cases, preserving
markers. Two originals agree at `23cde2d9`; reached3/260 (86+83+91) and independent
saved-frame59/1 pass separately. Private strict375 passes in 5.802s with zero
applications; compile1 is retained from the original fixture elaboration failure.
The generic helper is wider than this guarded string-literal witness. Other
layouts/lifecycle/NULL-form restoration and broad returns_verify remain OPEN.
[Notice review](coverage/semantics/reference-return-notice-review.json).
Actual375 over `41db4e84` passes strict at `6e897cd2` in 5.972s with zero
applications; original private source/state/independent cuts remain separate.

Ordered Z/W/X global string histories now admit an idle lifecycle certificate for
a sole checked plain class with an echo-only destructor. Capture retires only the
history roots and keeps SelectedY live; ordinary I2 assignment emits D once, then
the identical original Y TypeError escapes through ordered retirement. Selected Y
keeps its alias without object birth. Source2 and reached3/306 (88+135 retained,
83 affected) pass at `c121e080`; private strict375 passes in 5.852s with zero
applications. Independent saved-D82/1 authenticates the full registered
result/release/operation-exit prefix and existing projection to idle f scope;
deleting the operation exit is publicly refused. Original declaration/fixture
failures retain zero credit; exact frontier finders account for real eager work.
The maintained producer is byte-identical to the tested producer. Other destructor
effects, reentry/suspension, caught/mixed lifecycle and broad returns_verify remain
OPEN. [Multiple-history review](coverage/semantics/reference-return-multiple-active-cv-review.json).
Actual375 over `167731401` passes strict at `5a9ba189` in 5.941s with zero
applications; original private source/state/independent cuts remain separate.

The same idle lifecycle certificate now admits a checked literal echo followed by
`throw new TypeError` with a literal message. Existing eager/finally rules create
the fresh destructor error, then link the original Y TypeError after Y-finally
replacement; the callback's immediate Previous is empty. Ordered Z/W/X retirement
preserves the fresh caller error and late Previous. Source2, reached3/335
(102+150+83) and independent post-D91/1 pass at `df2d4e0b`; deleting only the
registered operation exit is publicly refused. A separate native caller observer
confirms message/line/distinct Previous. Private strict375 passes in 5.851s with
zero applications. Compiles2/3 are retained from the original receiver-field
fixture failure, which keeps zero state credit; the maintained producer is exact.
Other destructor effects, active direct validation and broad returns_verify remain
OPEN. [Multiple-history review](coverage/semantics/reference-return-multiple-active-cv-review.json).
Actual376 over `0e36f837` passes strict at `ce3ad7b0` in 6.116s with zero
applications; original private source/state/independent cuts remain separate.

The idle lifecycle certificate now admits one checked global string-CV import/write
before echo/TypeError throw, tied to W's source beneath the surviving outer X.
Source2 and reached3/355 (107+165+83) pass at `a8110086`; changed W survives actual
public WX/X retirement, caller error/late Previous and late budget equality. The
selected-Y bypass keeps its alias without object birth/write. Independent saved
post-write110/1 authenticates executed local/global W and full registered prefix,
with wrong-cell public refusal; original metadata-binder failure stays zero credit. Private strict376 passes in 5.901s with zero
applications; maintained producer is byte-identical. After W retirement the
reconstruction is a local source certificate. Other mutation/lifecycle/returns
remain OPEN. [Multiple-history review](coverage/semantics/reference-return-multiple-active-cv-review.json).
Actual376 over `6d134df2` passes strict at `5bf62df1` in 5.878s with zero
applications; original private source/state/independent cuts remain separate.

The same idle lifecycle certificate now admits an in-range integer-literal W
write, retaining the original string checks on all other histories. Source2 and
reached2/266 (183+83) pass at `b38a164b`: W remains PINT17 through actual public
WX/X retirement, caller error/late Previous and late budget equality; bypass keeps
its alias without object birth/write. Independent saved109/1 binds executed
local/global/saved W and the full prefix, refusing payload18; author rejects
non-W X17. Original parse failure keeps zero state credit. Private strict376
passes in 5.875s with zero applications; maintained producer is byte-identical.
Post-W reconstruction remains a local source certificate; only integer17 is
observed, and wider mutation/lifecycle/returns remain OPEN.
[Multiple-history review](coverage/semantics/reference-return-multiple-active-cv-review.json).
Actual377 over `a0e805cc` passes strict at `3d605669` in 6.002s with zero
applications; original private source/state/independent cuts remain separate.

The idle lifecycle certificate now admits checked `$GLOBALS["w"] =& $GLOBALS["x"]`
before echo/TypeError throw. Global W follows X while f retains its distinct local
W/string cell through public WX/X retirement. Source2 and reached2/293 (210+83)
pass at `a850a5df`; caller alias/probe, fresh error/late Previous, budget equality
and bypass are checked. Independent public136/1 validates the actual current8/
saved21 registered prefix and refuses wrong global W→Z; author refuses wrong
global X. Private strict377 passes in 6.026s with zero applications. The original
caller-table fixture failure keeps zero state credit; bypass compilation is
retained and the maintained producer is byte-identical. Post-W reconstruction
remains a local source certificate; wider rebinding/lifecycle/returns remain OPEN.
[Multiple-history review](coverage/semantics/reference-return-multiple-active-cv-review.json).
Actual378 over `2a5dcf424` passes strict at `2ff75de2` in 5.940s with zero
applications; original private source/state/independent cuts remain separate.

The idle lifecycle certificate now admits checked `unset($GLOBALS["w"])` before
echo/TypeError throw. Global W disappears while f retains its original local
W/string cell through public WX/X retirement. Source2 and reached2/326 (240+86)
pass at `cec65d21`; both actual caller reads emit WARNING(w,6), with zero warnings
through retirement/caller entry. Fresh error/late Previous, budget equality and
quiet bypass are checked. Independent public134/1 authenticates current7/saved21
registered1/2/2 and rejects forged global W→Z; author rejects wrong non-W global X.
Private strict378 passes in 6.100s with zero applications. The maintained producer
is byte-identical; there was no author fixture failure. Post-W reconstruction
remains a local source certificate; wider unset/lifecycle/returns remain OPEN.
[Multiple-history review](coverage/semantics/reference-return-multiple-active-cv-review.json).
Actual379 over `03ebb6ed` passes strict at `f01eb8f8` in 6.274s with zero
applications; original private source/state/independent cuts remain separate.

The idle lifecycle certificate now admits a checked counter-guarded destructor
call to the same named f, retaining all original string/idle/prefix guards.
Source2 and reached2/324 (238+86) pass at `7ab32609`: nested f returns unused PNULL
to the genuine destructor before T; T then D preserves the original Y TypeError
through ordered Z/W/X retirement and the caller. Public counter-PBOOL refusal,
late budget equality and the selected alias/no-object bypass pass. Independent
public129/1 binds actual nested f/saved destructor7/outer f21/main registered1/1/1
and refuses a missing outer operation exit. Private strict379 passes in 5.969s
with zero applications; maintained producer is byte-identical. The original
fixture parse and qualified-name finder failures keep zero state/diagnostic
credit; separate elaboration checks are syntax-only. No active lifecycle guard
changed. Reduced-history reconstruction remains a local source certificate;
wider reentry/lifecycle and broad returns_verify remain OPEN.
[Multiple-history review](coverage/semantics/reference-return-multiple-active-cv-review.json).
Actual380 over `fb9d482a` passes strict at `b453661a` in 6.001s with zero
applications; original private source/state/independent cuts remain separate.

The guarded destructor additionally admits an ordinary local reference binding
from nested f followed by a literal write through that same local. M35's bare-call
route and all common idle/string/prefix guards are unchanged. Source2 and
reached2/332 (246+86) pass at `30e2fdbc`: inner/global/saved Y share the real return
cell before the probe write; probe/T/D preserves the original outer Y TypeError
through ordered Z/W/X/public retirement, caller and budget continuation. The
selected bypass keeps its alias without object birth. Independent public150/1
admits the full bound-inner prefix and refuses missing outer operation exit;
author counter-PBOOL refusal is separate. Private strict380 passes in 6.050s,
zero applications, and maintained producer is byte-identical. Worker60 source2
is a cap-only retry after genuine progress; original Worker45 timeout/trailing
closure and unrun selected-payload correction keep zero credit. Local source
reconstruction and reachable alias evidence do not prove historical alias
provenance; wider demand/lifecycle and broad returns_verify remain OPEN.
[Multiple-history review](coverage/semantics/reference-return-multiple-active-cv-review.json).
Actual380 over `663f0ef4` passes strict at `ac9a8f50` in 6.081s with zero
applications; original private source/state/independent cuts remain separate.

The guarded destructor additionally admits an exact local TypeError catch around
nested AssignRef/probe, with ordinary local names and the checked getMessage
receiver. Old M35/M36 and common idle/string/prefix rules are unchanged. Source2
and reached2/350 (264+86) pass at `8a125248`: the failed inner binding/probe is
canceled, C/T/D continues, and the same original outer Y TypeError survives
ordered Z/W/X/public retirement, caller and budget continuation. The caught
nested error stays distinct with empty Previous; selected bypass keeps its alias
without object birth. Independent early-catch public99/1 admits the actual
current6/outer f21/main registered1/1/1 prefix and refuses missing outer operation
exit; author counter-PBOOL refusal is separate. Private strict381 passes in
6.089s with zero applications. Sparse-import and catch-sort failures retain zero
credit. Source reconstruction remains local; broader catch/reentry/returns OPEN.
M37 is validation-only: source2 and public96/1 at `2f15e222` preserve a fresh
escaping nested TypeError. Previous is empty at the reached nested throw; the
caller catches the same error with old Y as Previous. Its
original fixture elaboration failure remains zero; the exact maintained producer
requires the retained checked query beside it in an ignored recovery directory.
[Multiple-history review](coverage/semantics/reference-return-multiple-active-cv-review.json).
Actual381 over `4d26abc3` passes strict at `de54edc1` in 6.244s with zero
applications; original private source/state/public and M37 validation cuts stay separate.

The idle class certificate additionally admits catch echo followed by throwing
the same decoded ordinary caught local. Old M38/M36 and common guards remain
exact; no throw/Previous/active rule changed. Source2 and reached2/353 (267+86)
pass at `64d33559`: the same caught error retains creation origin, line4 and its
entire reached trace-array graph through late Y replacement and caller catch.
Previous is empty at callback rethrow; old Y is linked at the later cuts. T/D
and the failed inner binding/probe stay canceled. Ordered Z/W/X/public retirement,
counter-PBOOL refusal, budget continuation and quiet selected alias bypass pass.
Independent public132/1 binds actual current11/outer f21/main registered1/1/1,
early trace graph and missing-operation-exit refusal. Private strict381 passes in
6.173s with zero applications. The original public restore-origin fixture failure
keeps zero credit. Trace/identity are reached-state/engine-derived evidence,
separate from native output agreement. Local source reconstruction and wider
catch/rethrow/lifecycle/returns remain OPEN.
[Multiple-history review](coverage/semantics/reference-return-multiple-active-cv-review.json).
Actual382 over `aa8ddc73` passes strict at `eebde3e7` in 6.216s with zero
applications; the private source/state/public cuts retain their original identities.

The same idle/source certificate now admits a checked catch that creates a fresh
one-literal TypeError. Old helpers, string/prefix guards and throw/Previous rules
remain unchanged. Source2, reached2/368 (282+86) and independent public161/1 pass
at `98aacd7d`/382. The replacement has its own New origin, line3 and two-frame
trace; caught nested retains line4/three frames, and both have empty Previous at
the early callback cut. Late cleanup links old Y to the identical replacement,
retires the caught-only error, and preserves the replacement trace through ordered
Z/W/X/caller/budget. T/D/probe stay canceled; counter and operation-exit controls
refuse, while selected bypass retains its alias. Private strict passes in 6.484s
with zero applications. Worker120 source retry changes only the cap; original
Worker60 and pre/post-C timeouts stay zero, and Q-step cuts are diagnostic only.
Identity/trace/Previous are reached-state and engine evidence, separate from
native output agreement; local reconstruction and broader returns remain OPEN.
[Multiple-history review](coverage/semantics/reference-return-multiple-active-cv-review.json).
Actual384 over `30057795` passes strict at `b89cdc07` in 6.291s with zero
applications; private source/state/public cuts retain their original identities.

The bounded class certificate now admits positional New TypeError(literal,0,
same ordinary caught local), preserving old helpers and common guards. Source2,
reached2/411 (325+86) and independent public163/1 pass at `aed60b2e`/384. Early
replacement.previous=caught and caught.previous=null; later old Y is appended
to the caught tail. All three identities and both creation-line/trace graphs
survive ordered Z/W/X/caller, with caught kept live and T/D/probe canceled.
Budget resumption starts after actual main e/p/q bindings, before R output; the
counter control refuses and selected alias passes. Private strict takes 6.362s
with zero applications. Original parse7709 stays0; corrected-primary elab680e
is syntax-only. Native Previous messages, modeled identity/trace and early/late
state cuts remain separate; local source reconstruction and wider returns OPEN.
[Multiple-history review](coverage/semantics/reference-return-multiple-active-cv-review.json).
Actual385 over `ad50ffd2` passes strict at `6d36ef8b` in 6.574s with zero
applications; private source/state/public cuts retain their original identities.

Weak by-reference Stringable returns now preserve the selected live, unconstrained
aliased CV cell through callbacks. Current/saved f-local bindings authenticate that
cell while GLOBALS may rebind or disappear; conversion writes the old cell atomically.
Failed callbacks report the live selected value and chain the callback Exception.
The certificates add no roots; existing STRINGIFY_RESULT retains the cast receiver.
Thirteen exact originals agree at `010545`/368; eight reached fixtures pass 843 assertions
(95 at `34607` plus 748 at `436014`). Actual 370 over `6f096ef1` passes strict at
`cfd5f87d` (5.280s, zero application evaluations); the
[typed CV review](coverage/semantics/reference-return-typed-cv-review.json) keeps each cut separate.
Sole nonreference local CV string returns now borrow their selected cell, while
protected returns first create the real owning reference temporary. Successful
conversion releases the old receiver before raw copying into that cell, so its
destructor precedes finally; callback failure retains the object through finally
and reports its live value with the previous callback Exception. Five originals
agree at `18ab1ad5`/371; eight reached fixtures pass 871 assertions (488 at `dfb45`
plus 383 at `fbb5d0a`). Actual 371 over `3d99674e` passes strict at `cf1094`
(5.293s, zero application evaluations). The
[local CV lifetime review](coverage/semantics/reference-return-local-cv-lifetime-review.json)
keeps these cuts separate from the earlier aliased-CV evidence. Genuinely released
targets, destructor throw/reentry, real suspension and wider typed consumers remain open.

M42 validates existing protected string-return behavior at `b55942bc`/385. The
unchanged model agrees with both native unset/control originals. Independent
public107/2 ties the original pre-unset x to the same saved return carrier, with
the local binding absent/present, and refuses deletion of only FINALLY_PHASE.
Reached2/176 delivers that cell as REFERENCE to main r/a, checks write-through,
quiet cleanup and budget equality from the alias caller cut. The protected
carrier still owns the cell. Fixture parse/elaboration failures retain zero
credit; publication changes only validation metadata and the exact maintained
producer. Released borrowed-cell conversion and broad returns remain OPEN.

M43 validates untyped by-reference `finally` cancellation: an override returns a
new y cell and runs D before R; its control returns the original x cell and runs
D after R. Source2 and late2/230 pass at `43df347e`; the old cell's modeled
allocation/root retirement is distinct from physical Zend collection. Genuine
active cleanup exposed a missing registered-operation exit check (81fe failure0).
The scoped84/270 repair at `b6805e2` passes strict385/source2 and independent
active68 + parked23 premises with two exact EXIT-only refusals. Generic fatal
history validation stays unchanged; broad returns_verify remains OPEN.
Actual385 over `b4ff3014` passes joined strict SL initialization at `87ea3155` (6.464 s).
Private source/public/native and original230 cuts keep their tested revisions.

M44 adds validation only at `cb498f92`/385. Two originals agree: suspension
interposes B:1 before the resumed worker delivers the selected cell; direct control
reports B:0 after its worker. Independent58/two refusals authenticates pre-unset x
and the parked Fiber-to-cell edge; late124+106 follows its own carrier to resumed
f/worker returned REFERENCE, r/a writes, main E and budget from the worker alias
state. These are separate reached executions. Original059ac elaboration0,
6c05 syntax-only app0 and unrun6909 field correction0 stay distinct. No runtime
patch, physical collection or broad returns completion is claimed.

M45 validates suspended untyped by-reference `finally` cancellation at `cbc57fdb`/386.
Source2 agrees with native2. Early92/two controls follows original x/O through the
parked Fiber carrier to resumed active destruction with distinct y/override;
phase and saved operation EXIT deletion both refuse publicly. Separate late107+107
follows its own override carrier through worker returned REFERENCE, r/a writes,
main E and budget from the worker alias state, with direct control. No runtime
change, cross-fixture identity, physical collection or broad returns completion.
[Cancellation and integrity evidence](coverage/semantics/reference-return-local-cv-lifetime-review.json).

M46 validates orphaned suspended object-reference carriers at `27a92e4b`/386.
Source/native2 agrees: early external drop emits D before L, delayed drop after
the first GC emits D between G/E. Early98/two refusals follows original x/O through
parking to drop-triggered destruction and checks parked phase/close-VM EXIT integrity.
Separate late135+135 executions retain their own carrier until drop, then cancel
worker R, retire modeled allocations, restore main and preserve caller-cut budget.
Parse d531 remains0; corrected paired elaboration0db9 is syntax-only/app0. No runtime
change, cross-fixture identity, physical collection or broad returns completion.

M47 validates throwing old-O destruction during orphan Fiber close at `0df6172`/387.
Source/native2 agrees for early/delayed drop. Early102/one refusal authenticates
original x/O to parked carrier and fresh Exception, distinct from the private
graceful-exit control; deleting saved f's operation EXIT while retaining the active
operation registry is heap-valid and refuses publicly.
Separate late130+130 executions preserve that fresh error/New origin/line2/pure
trace through main catch/caller with null Previous, then failed Fiber retirement,
canceled worker R and caller-cut budget. Final request error retirement is separate.
Both prelaunch wrapper/origin corrections remain unrun0. No runtime change, native
identity/trace, cross-fixture identity, physical collection or broad returns closure.

M48 at `059bc886`/387 repairs cycle GC and later request-store Fiber refusal.
Collector roots now include suspended live-VM selected reference-return temporaries;
the ordinary ownership graph and internal-node rejection stay intact. A bounded
normal idle store route closes an empty-local pending-REF Fiber with INDEX+1 and
one truthful USER=false receiver hold; eager zero-owner selection is unchanged.
Source/native2 agrees: cycle D follows both GC calls/E, while null-control D is early.
Independent122/two heap-valid refusals checks coordinated plan-root deletion and
in-range store-index rollback. Separate late163+99 follows the same post-G carrier
through second GC/E to its O destructor, retirement and actual caller-cut budget.
Original first-GC141d/later-store0c1b failures and fixture-analysis0411 remain0;
source-qualified diagnostic tuples are separate. Wider layouts, native ownership,
physical collection and broad returns verification remain OPEN.
Actual `fa74e4b0`/387 composition passes one quiet ff24 strict gate (app0);
the parent cached-table GC guard is preserved without private evidence renewal.

M49 handles a selected O destructor error during request-store Fiber close.
With no executing PHP frame, the genuine USER=false store consumer transfers the
same ordinary error directly to UNCAUGHT, then fatal cleanup; no handler dispatch.
The direct-finally trace site derives from the authenticated suspended callsite.
Source/native2 and early139 pass at `0ec20831`/387. At `d16a062b`, a separate
storage-only rule admits the exact private-control release/callback operation/store
hold, preserving old USER=true rules. Fresh compile2 and late125+137 preserve
same-error trace, fatal255/null catch, retirement and split/full budget equality;
paused123 adds public admission and coordinated stale-sequence refusal.
The source/early cuts retain their original revision through an explicit
admission-only bridge. Early store INDEX refusal is helper-only; line and sequence
controls use the actual driver. Original Unsupported/trace mismatch, transient
fixture overclaim, genuine budget gap and compiler-binding failure retain0.
Physical collection, other layouts and broad returns_verify remain OPEN.
Actual `a1c76bf2`/388 composition preserves current class/output/callback rules;
one quiet ff24 SL45 compiler gate passes (app0), without private evidence renewal.

M50 validates existing typed by-reference Fiber rechecks at `ee915d44`/388.
Source/native2 agrees without a runtime change. Early79/one heap-valid replay-line
refusal follows the selected global cell through an external bad write and a
second parked finally with pending TypeError. Separate late144+146 executions
preserve that error/line2/null Previous/pure trace through the worker catch, or
deliver the integer reference to r/a and write3 through to global x. Both complete
normally and retain the global cell; caller-cut split/full budgets and cleanup
pass. Original parse5918/static e6ee remain0; static42f8 is app0 and query26e4 is
diagnostic only. Validation publication changes no runtime or source catalogue.
Native trace/identity, internal Stringable suspension and wider returns remain OPEN.

M51 validates a selected by-reference string return while its `__toString`
callback is suspended at `ee915d44`/388. Both write-order sources agree with
native PHP without a runtime change. A same-execution diagnostic ties CELL7 and
OBJECT0 to the parked stringify receiver, the external write, and delivered
worker r/a; it has no proof credit by itself. Early64/one public refusal keeps
the authentic destination and receiver through suspension and rejects a
coordinated allocated wrong destination. Separate late54+54 checks the same
delivered global cell, worker write, distinct final global values, cleanup and
split/full caller budget in each source. That mutant can also violate REFCELLS,
so it does not isolate the local-binding guard. Native object identity, physical
collection, other receiver layouts and broad returns verification remain OPEN.

M54 repairs the computed owning-object return consumed by a caught inner-finally
`?object` recheck. An authenticated nonowning cursor records the old call source
before eager object release; replay restores detached NULL and exactly one
original-line VALUE Notice. The saved destructor cleanup-prefix descriptor check
admits the actual pause while rejecting a LINE-only cursor forgery. Clean native2
and source2 agree at private `7d843e3b`; public80 and separate caller54+40 pass at
`ff7768cb`/388. The treatment split/full budget agrees from the real destructor
pause, and its r/a alias is detached from bad y; the control retains r=a=y and
the live stdClass before the shared write. Initial Unsupported, a genuine public
descriptor failure and fixture-only failures retain zero affected credit.
Actual-parent 391-module composition passes strict SL45 at `413193ad` (app0);
broad returns_verify stays OPEN. [Local CV lifetime review](coverage/semantics/reference-return-local-cv-lifetime-review.json).

M55 validates nested computed owning A/B by-reference returns without a runtime
change at `0420409b`/391. Two native sources agree exactly with the checked
model; one source-linked state fixture proves distinct pending owners, B then A
destructor releases, public admission and the treatment's selected y alias.
The control and final write are separate source-comparison observations. Physical
collection, other nested layouts and broad returns verification remain OPEN;
the [ledger](coverage/semantics/reference-return-local-cv-lifetime-review.json)
records the original reports and recovery path.

M56 admits one computed owning array `[new O]` through the caught `?array`
return recheck. A source-only cursor survives eager table and child-object
retirement; replay restores detached NULL and one original-line VALUE Notice.
Native2 and affected source2 agree at private `ec9c395a`/391. Public95 follows
the same array-to-object edge through the destructor, verifies pre-destructor
split/full budget and rejects a LINE-only saved-cursor forgery through the
actual driver. The pre-repair treatment Unsupported and a parse-only query
failure retain zero repair credit. This bounded array layout does not establish
physical collection, other aggregate layouts or broad returns completion;
see the [ledger](coverage/semantics/reference-return-local-cv-lifetime-review.json).

M57 distinguishes a computed-call return slot from an immutable string literal
in a caught by-reference `?string` recheck. Both pending values contain `"old"`;
the computed source resumes with detached NULL after the inner TypeError, while the
literal restores `"old"`. Each emits one original-line by-reference Notice.
Native2/source2 agree at private `dfa3632d`/391. Paired public88 authenticates
the source-only cursor, null versus literal restoration, a LINE-only driver
refusal and active-replay split budget. The interned payload carries no heap
owner; other computed scalars, CONST forms and broad returns remain open in the
[ledger](coverage/semantics/reference-return-local-cv-lifetime-review.json).

M58 repairs the caught `?object` recheck with two nested computed owning
returns. Both A and B objects are pending before the deepest replacement;
their destructor callbacks retire B then A while two source-only cursors keep
the return history. Replay restores detached NULL and one Notice from the inner
B return. Native2/source2 agree at private `86109c30`/394. Public123 admits
both saved callback views, rejects a heap-identical inner cursor LINE forgery,
and checks split/full budget from the B callback and detached final r/a versus
bad y. The first private guard failure and output-only query retain zero repair
credit. Physical collection, other payloads and broad returns verification
remain open in the [ledger](coverage/semantics/reference-return-local-cv-lifetime-review.json).

M59 repairs a computed owning switch subject `[new O]` discarded during a
by-reference string return. A node-free historical row is recorded before
ordinary table and child-object cleanup so the destructor's saved caller can
later resume the selected switch case without reading the retired array.
Native2/source2 agree at private `646a9e5b`/394; public102 follows the live
array-to-object edge, saved callback row, dead-table replay and final row
removal. It rejects a heap-identical FIRSTLINE forgery and checks split/full
budget from the destructor pause. The constant-array control remains native-
exact. The pre-repair Unsupported and output-only diagnostic retain zero repair
credit. This proves one direct-object array layout and modeled retirement, not
physical collection or general switch subjects; broad returns verification
remains open in the [ledger](coverage/semantics/reference-return-local-cv-lifetime-review.json).

M61 restores a compiled literal array `['old']` after a caught by-reference
`?array` finalizer recheck. The compiled CONST source retains its pooled table;
the otherwise equal computed-call return resumes with NULL. Native2/source2
agree at private `46af5bbc`/394, including one original-line Notice each.
Public104 follows the literal's source-only cursor and restoration, rejects a
heap-identical cursor LINE forgery, and checks split/full budget. The caller's
append creates a distinct result table while the pooled table stays unchanged.
The baseline Unsupported and output-only pool query retain zero repair credit.
This covers the reached nonempty literal and modeled copy-on-write, not general
CONST arrays or broad returns verification; see the
[ledger](coverage/semantics/reference-return-local-cv-lifetime-review.json).

M62 repairs a selected local array bucket `$a[0]` in a by-reference `?object`
return after a caught finalizer recheck. After the sole local array is unset,
replacement cleanup invokes the old object's destructor before replay;
retaining the array delays that callback.
The authenticated DIM cursor keeps the original source without retaining the
old bucket, and a used nullable result resumes through a fresh detached NULL
reference without a Notice. Native2/source2 agree at private `3ea78c33`/394,
including the distinct destructor order. Public172 admits both reached owner
states, the saved callback cursor and fresh caller cell, rejects a heap-equal
cursor LINE forgery, and checks split/full budget from the callback. The
pre-repair Unsupported, output-only owner queries and first repaired stderr
mismatch retain zero repair credit. Other DIM forms, nonnullable returns and
broad returns verification remain open in the
[ledger](coverage/semantics/reference-return-local-cv-lifetime-review.json).

M63 admits a simple typed-property return `$box->slot` through a caught
by-reference `?object` finalizer recheck. Unsetting the sole local Box before
replacement lets ordinary cleanup retire its property cell and invoke O's
destructor; retaining Box delays that callback. The saved cursor records the
old source without retaining the property or its type constraint. A used
nullable result gets a fresh detached NULL reference with no by-reference
Notice. Native2/source2 agree at private `39e5223b`/394 with both destructor
orders. Public216 checks the typed source, both owner states and the fresh
reference without PROPREFS; it rejects a heap-identical cursor LINE forgery
through the driver and checks split/full callback budget. The prior Unsupported
baseline and output-only owner query have zero repair credit. Wider property
expressions, unused or nonnullable returns and broad returns verification
remain open in the
[ledger](coverage/semantics/reference-return-local-cv-lifetime-review.json).

M65 restores a pending bare `return;` Notice after an inner finalizer throws
and is caught. The old by-reference NULL return remains live, so its Notice
belongs to the source return, as with the explicit `return null;` control.
Native2/source2 agree at private `797abaa7`/394, including the exact source
line and no caller assignment Notice. Paired public74+68 proves the bare NULL
marker is restored and the explicit-NULL VALUE marker remains, rejects a
heap-identical wrong-kind marker through the driver, and checks detached caller
alias and split budget. The unchanged misplaced-Notice baseline and output-only
frontier retain zero repair credit. Implicit fallthrough and other NULL histories
remain open in the
[ledger](coverage/semantics/reference-return-local-cv-lifetime-review.json).

M66 admits a mixed old return history: an owning computed `O` value outside a
global `$z` reference, followed by a selected `$y` return whose `?object`
recheck fails and is caught. Two source-only cursors survive ordinary O
destruction; `$z` stays live. The used nullable result resumes through a fresh
detached NULL reference without a Notice, while the retained-y control delivers
its alias. Native2/source2 agree at private `17fa485a`/394. Public157 follows
the owning value, saved destructor pair, TypeError replay and caller; it rejects
a heap-identical saved cursor LINE forgery and checks callback split budget.
The unchanged Unsupported baseline and output-only frontier have zero repair
credit. Other mixed histories, unused or nonnullable returns and broad
returns verification remain open in the
[ledger](coverage/semantics/reference-return-local-cv-lifetime-review.json).

M67 extends that mixed source history to a used nonnullable `object` return.
After the first caught `$y` recheck error, the middle `$z` return resumes as a
node-free cleared NULL. Its recheck creates a distinct TypeError at the middle
return's line with no Previous exception; the inner finalizer runs again and
the same error reaches the caller catch. Source2 at private `836b7845`/394
matches retained native2, including no Notice and the retained-y control. Public120
binds the prior and new errors, cleared replay, reentry and caller identity,
rejects a heap-identical cursor LINE forgery through the driver, and checks
split budget. The prior Unsupported baseline and output-only frontier have
zero repair credit. Unused and other mixed histories remain open in the
[ledger](coverage/semantics/reference-return-local-cv-lifetime-review.json).

M68 covers the reversed used `?object` history: an outer global `$z` reference
and an inner computed owning `O` value are pending when `$y` is selected.
Replacement cleanup runs the old object's destructor while `$z` stays live;
the delayed `$y` recheck then fails and is caught. Source2 at private
`d49392a2`/394 matches retained native2:
the treatment delivers a detached NULL and one inner-call by-reference Notice;
the retained-y control delivers its alias. Public155 follows the real saved
pending pair, old VALUE release, retirement, two-owner replay and NULL/Notice
marker through caller delivery. It rejects a heap-identical saved cursor LINE
forgery through the actual driver and checks callback split budget. The old
Unsupported baseline and output-only frontier have zero repair credit. Unused,
nonnullable and other mixed layouts remain open in the
[ledger](coverage/semantics/reference-return-local-cv-lifetime-review.json).

M69 covers a used `?array` return with an outer global `$z` reference and an
inner array return from either a no-argument computed call or a compiled
`["old"]` literal. When the deepest `$y` recheck is caught, the computed
return slot resumes as NULL while the literal restores its pooled array.
Source2 at private `952bc3db`/394 matches retained native2 in both cases,
including the distinct caller append results and one callee line4 Notice each.
Paired public checks bind the real pending pair, source-only capture, old pool
retention, raw source-specific restoration and caller copy-on-write. One
heap-identical literal cursor LINE forgery fails the actual driver; both
pair-cut budget laws pass. The old Unsupported baseline and output-only
frontier have zero repair credit. Unused, nonnullable and other mixed array
layouts remain open in the
[ledger](coverage/semantics/reference-return-local-cv-lifetime-review.json).

M70 admits an ordinary no-argument instance-method result as the old computed
source in a used `&f():?object` return. The same Factory is temporary or
published to a global slot; its ordinary lifetime differs, while replacement
cleanup invokes the returned O object's destructor. A source-only cursor
resumes as detached NULL with one method-source by-reference Notice after the
caught `$y` recheck. Source2 at private `6e4e1115`/395 matches native2 in both
cases, including Factory destructor order and exact callee line4 Notice.
Paired public checks bind the saved cursor and original VALUE-O release, raw
NULL/Notice marker, caller alias and retained Factory root. One heap-identical
cursor LINE forgery fails the actual driver; both callback budget laws pass.
The old Unsupported baseline and output-only frontier have zero repair credit.
Method arguments, dynamic names, nullsafe calls, reference-returning methods
and broader returns verification remain open in the
[ledger](coverage/semantics/reference-return-local-cv-lifetime-review.json).

M71 admits an ordinary literal-name instance-method result with one positional
argument as the old computed source in a used `&f():?object` return. The
globally retained Factory is unchanged; a temporary Arg is cleaned before F,
while an Arg assigned to a global slot remains live through the caller cut.
Ordinary replacement cleanup invokes the returned O destructor. The saved
nonowning cursor resumes the old method return as detached NULL with one
method-source VALUE Notice marker after the caught `$y` recheck. Source2 at
private `031881ee`/395 matches retained native2, including Arg/O destructor
order and the exact callee line5 Notice. Paired public checks bind the genuine
saved cursor and original VALUE-O release, raw NULL/Notice marker, detached
caller alias and retained Arg root. One heap-identical cursor LINE forgery
fails the actual driver; both callback budget laws pass. The unchanged
Unsupported baseline and output-only frontier have zero repair credit.
Other argument forms, dynamic method names, nullsafe or reference-returning
methods and broader returns verification remain open in the
[ledger](coverage/semantics/reference-return-local-cv-lifetime-review.json).

M72 admits an evaluated REFERENCE from an ordinary no-argument, literal-name
instance method as the old source of a used `&f():?object` return. The method
returns Factory's slot; after `unset($factory->slot)`, its pending old cell
still carries O until ordinary replacement cleanup invokes O's destructor.
The saved f frame then carries only a source cursor, and the caught `$y`
recheck resumes the old return as NULL with one method-source VALUE
Notice marker. Source2 at private `e1cff5d3`/395 matches retained native2 in
both reference and value-method cases, including the exact callee line4
Notice. The reference-only public proof binds the live old cell, unset slot,
original VALUE-O release and retired cell/object, then raw NULL/Notice marker,
detached caller alias and one delivered diagnostic. A heap-identical saved
cursor LINE mutation fails the actual driver; the callback budget law passes.
The prior Unsupported baseline and output-only diagnostic have zero repair
credit. Wider method forms and broader returns verification remain open in the
[ledger](coverage/semantics/reference-return-local-cv-lifetime-review.json).

M73 checks the mixed owning-object/global-CV history when the caller discards
`f()`'s result. A nullable `?object` return completes normally; an `object`
return must still check the cleared middle NULL after the first caught `$y`
error. That check creates a distinct TypeError at the middle return's line,
reenters its finalizer and reaches the caller catch without a Notice. Source2
at private `7806bdc2`/395 matches retained native2 in both signatures.
Public125 binds the genuine node-free pair, raw NULL clearing without a new
allocation, prior and new errors through caller delivery, a heap-equal cursor
LINE refusal and split budget. The old Unsupported baseline and output-only
guard query have zero repair credit. Other unused layouts and broader returns
verification remain open in the
[ledger](coverage/semantics/reference-return-local-cv-lifetime-review.json).

M74 admits two node-free integer old returns in a used `&f():?int` finalizer
history. An evaluated `old_value()` result is cleared to NULL when the caught
`$y` recheck interrupts it; a compiler-folded `40 + 1` restores its authenticated
compiled `41`. Each raw resumption installs one old-source VALUE Notice marker
before delivery. Source2 at private `04a21f96`/396 matches retained native2,
including the opposite caller values and exact callee Notice. Paired public
checks bind both genuine active cursors, raw NULL/41 restoration, caller r/b
alias and final write; a heap-equal folded cursor LINE mutation fails the
actual driver, and both split budgets agree. The old Unsupported baseline and
output-only category query have zero repair credit. Other scalar expressions,
CONST forms and broader returns verification remain open in the
[ledger](coverage/semantics/reference-return-local-cv-lifetime-review.json).

Deprecated assertion options preserve raw flags, old-value snapshots, callback
arguments and live warning/exception/bail policy after callback/retval retirement.
Per-constant protection survives namespace publication and parked handlers.
Earlier 17 accepted originals retain their cuts; parked constant at 6fcb and selected
receiver plus independent RAW-array cleanup at ca196 add three, giving 20 distinct
options originals. State 117 stays at d7; original pending state 52 plus 15 real/history
and frozen-wrapper counterexamples pass at ca196 (67 total), with strict 356 compilation.
Pending exceptions validate on the real heap; the historical target view owns none.
The [ledger](coverage/semantics/assertion-options-review.json) keeps original failures,
the Count Unsupported/foreach distinction and bailout status-only correction.
Actual 359 over dfca passes strict compilation at 14ae4, preserving current property
warning/base roots and collector/storage fields. Earlier 358/f5 compilation retains
its own cut. Wider callback/description producers and INI warning paths remain required.

Module 374 unpacks arrays into ordinary method/array and captured START buffers.
Per-pack named ordering, dereferenced value copies and nonowning completed history
survive selector/pack retirement; copied C-root buffers authenticate their genuine
outer API. Ordered unwind preserves active-pack, positional/EX(This)/named and
direct Closure versus explicit invoke cleanup. Strict356, ten exact normals at
9+1 cuts and 345 independent plus 296 author premises pass. Constant packs retain
their genuine pool owner; a distinct dynamic-pack companion proves retired history.
Initial elaboration/matching failures and pooled fixture assumptions retain zero
affected credit. Compound/lifecycle gaps and paused returns remain open.
[Start-unpack ledger](coverage/semantics/fiber-start-unpack-review.json).

Module 376 uses native Generator resumes and real Iterator callbacks for START
packs. Borrowed CVs, iterator data and retained `current()` references have
distinct owners; arguments copy after `key()`, before `next()`. Exact unpack
lines authenticate implicit calls and saved frames. The 374 quiet-unwind fix
prunes consumed owners without creating inactive release jobs. Strict359 and
thirteen exact normals at 11+1+1 cuts and 752 independent plus 308 author physical
premises pass. Source-identical cuts preserve every original assertion within
existing caps; earlier failures and timeouts retain zero affected credit.
At that cut, IteratorAggregate acquisition was Unsupported/zero agreement;
wider raw payload changes and compound selectors remained required.
Actual361 over `401bfb516` passes strict SL compilation at `a54204745`, preserving
the current ARG Stringable/static, exact-return, property and abrupt-cleanup paths;
private13/1060 source/state cuts retain their original inputs.
[Traversable ledger](coverage/semantics/fiber-start-traversable-review.json).

NaN Iterator `valid()` warnings retain the original raw retval through ordinary
handler mutation, suspension and throw. Live references reread the changed float;
copied NaN stays true. Warning wrappers preserve one authentic START pack through
retval cleanup, and thrown handlers retire raw result/data/temporary before the
unfinished buffer. Strict361 and four unchanged native-profile normals pass at
`d2852e8bf`; eight independent source-reached groups/269 physical premises pass.
The original Unsupported baseline and thrown-tail fixture failure retain zero
affected credit; selected-handler cleanup precedes exact raw/data/temp release.
Prior376 cuts are not renewed. Actual361 over `169dd2f3f` passes strict SL
compilation at `f8d591f24`; EX32 and fatal-render interactions preserve their own paths.
[NaN ledger](coverage/semantics/fiber-start-nan-review.json).

IteratorAggregate START acquisition preserves original borrowed/owning input and
distinct returned Iterator/Generator data. Real prototype/inheritance, tentative
return notices and builtin covariance are checked; raw reference/scalar/self
returns raise the native Exception and survive until authenticated unwind.
The `getIterator()` receiver is borrowed, while Generator creation adds one
receiver to its saved frame. Successful cleanup retires
inner data before temporary input. Thirteen exact normals and five native255
declaration failures pass; four explicit consumer controls have zero agreement.
The affected historical Aggregate original now agrees, with its earlier
Unsupported record preserved. Strict361 and fourteen independent source-reached
groups/425 physical premises pass at their separate cuts. Live interface-link
admission and rejected raw-return retention are corrected; original failures stay
at zero credit. At this single-acquisition cut, nested acquisition and
foreach/yield-from/ordinary-call unpack consumers remained required. Actual361 over `5ec31e145` passes strict SL at
`35d7e73f1`, preserving current promotion, reference-recheck and EX33 collector
paths; private source/state cuts retain their original inputs.
[Aggregate ledger](coverage/semantics/fiber-start-aggregate-review.json).

Recursive Aggregate START acquisition owns each returned layer, including
nonadjacent repeated identities, and retires layers inside-out before rewind.
Terminal data stays protected while a throwing retval destructor preserves the
pending Throwable through remaining layer retirement. Eleven exact normal
originals and strict361 pass privately. Literal-output/scalar-yield startup with
a pending error runs the real Generator body, then closes a frame with no owned roots
without finally; two explicit controls keep pre-yield calls and owned roots at zero
agreement. Twenty independent reached groups/544 physical premises pass, including genuine
borrowed/raw owners, retained Generator receipts and pending-error startup/close.
Original model, strict-binding and cleanup-fixture failures retain zero credit.
Actual361 over `fbc87ced3` passes strict SL at `53396820d`, preserving current
switch replay, promotion and shutdown fatal cleanup; private source/state cuts
retain their inputs. Other Aggregate consumers and broader pending Generator
startup remain required.
[Nested ledger](coverage/semantics/fiber-start-nested-aggregate-review.json).

Aggregate foreach378 acquires nested real Iterator/Generator data with borrowed
getter receivers and one raw owner per returned layer. Layers retire before
initialization; raw valid retval cleanup precedes original input retirement and
the loop body. Acquisition/layer throws prevent startup, while retval/input throws
keep exact data-before-input unwind. Persistent reference-mode CVs stay borrowed;
reference-valued inputs retain their HCELL, and reference-yielding Generators keep
ordinary live aliases. Retained foreach Generator close runs real finally throw
and Fiber suspension, with source-authenticated receipts and unique operation
ownership across saved VMs. Earlier cuts retain twenty normal sources, strict362
and the later-valid NaN Unsupported control/zero agreement. Twenty-six independent reached
groups/719 physical premises pass at separate retained cuts; genuine getter
creation readiness and one initializer cursor claim are checked. Original admission/source failures stay
zero; prior Aggregate/START evidence is not renewed. Changed original CV/reference
operands, wider byref locations and remaining Aggregate
consumers stay required. Actual366 over `c07eac043` passes strict SL at
`646095932`, preserving current retired-owner replay, sensitive trace wrappers
and assertion conversion; private source/state cuts retain their inputs.
[Foreach ledger](coverage/semantics/foreach-aggregate-review.json).

Foreach valid NaN warnings retain the raw return through ordinary handler invoke,
result and cleanup, then reread live numeric references once. Copied NaN stays
true; first-valid input retirement follows raw-result cleanup, and thrown handlers
retire raw retval before data/input. Seven new originals and the affected unchanged
late-valid original agree with preserved native tuples; strict366 passes at
`6ce4b1524`. Eighteen independent genuine-source groups/495 physical premises
pass at retained cuts, including saved-frame forgeries and exact raw retirement. Wider raw
payload changes remain explicit Unsupported; previous foreach/START evidence is
not renewed. Actual367 over `88f132db8` passes strict at `0b37a8334`,
preserving the parent reference-return Notice protocol.
[NaN ledger](coverage/semantics/foreach-valid-nan-review.json).

Actual358 over `0f28f9d62` passes strict compilation at `8b1b71064`, preserving
current physical collector, source-line, assertion and retained-method fields;
private source/state cuts retain their inputs.

Runtime assertion INI preserves raw initial/current bytes, modified/restore timing
and the live numeric mode. Quiet quantities permit nonnegative updates; changes
involving a negative mode warn before a frozen false completion on the handler's state.
At `1593cd3ca` (354 modules), strict compilation, 12 new native-profile source
tuples, 54 typed quantity/state premises and 96 authentic state premises pass.
Nested writes and original thrown identity survive; altered refusal bytes/options
are rejected. Raw output is under
`.tools/compiler-assertion-ini-368-19/.tools/{assertion-ini-gate-v1,method-runtime-9j809l_h,assertion-ini-state-v1}`.
The later bounded warning/overflow/carrier cut is recorded above; original recapture,
warned restore and authenticated Stringable-option refusal remain required. Explicit
startup transport still admits exactly `-1`/`0`/`1`.
The actual 356-module composition over `4563a5bf9` passes strict initialization
at `06409ee08` (4.471 seconds); raw output is in
`.tools/compiler-assertion-ini-current-19/.tools/assertion-ini-current-gate-v1`.
Earlier 354-module runtime cuts retain their identities.

Module 370 executes simple RAW Fiber API array C-root callbacks, including start
and constructor. RAW owns current members; frozen caches and C handlers borrow
the receiver, with separate original/copied buffers. Saved states and actual
callers authenticate parked static, nested, collector and warning continuations.
Strict 353, twelve exact normals at 6+6 cuts and 293 independent plus 241 author
reached premises pass. A narrow 296 fix admits nominal WeakReference argument/property
types and names their diagnostics. The historical promoted-parameter original, initial
compiler stop, typed-companion failure and fixture parse stop retain zero credit;
the explicit-property companion is distinct. Compound selectors, start unpacking,
broader lifecycle work remain required; paused returns stay excluded.
Constructor promotion has its separate accepted cut above.
Actual 355 over `aa8ebb4d1` passes strict compilation at `cb42ba678`, preserving
current startup/source/collector and retained-method guards; private source/state
cuts retain their inputs. [Raw-array ledger](coverage/semantics/fiber-array-core-callbacks-review.json).

Assertions368 supplies early startup `-1`/`0`/`1` selection for main/eval/include
and replay, resolved direct-call elision, pre-argument immutable descriptions,
dynamic/FCC evaluation and description validation before truth. At `02f0d61c4`
(350 modules), strict compilation, 25 exact native-profile source tuples and 64
authentic state premises pass; fresh errors have code 1 and supplied Throwables
retain identity. Independent quote7 at `45cdd2f92`, export17 at `85f098d5f` and
startup18 retain separate cuts. Raw results are under
`.tools/compiler-assertions-368-19/.tools/{method-runtime-itg9mwvs,assertion-state-v3,assertion-gate-v13,assertion-gate-v10,assertion-gate-v8,assertion-startup-v1}`;
startup rejection classification is derived from unchanged recorded streams.
Original compiler/receive failures remain preserved. Assertion options/callbacks,
Stringable descriptions and wider export/producer shapes remain
required. Combined/offline catalogue wiring is prepared; its fresh run is pending.
The actual 354-module composition over `fa0180918` passes strict initialization
at `c24807fcd` (4.370 seconds); raw output is in
`.tools/compiler-assertions-368-current-19/.tools/assertion-current-gate-v1`.
Earlier private 350-module source/state/helper cuts retain their own identities.

367 ordinary simple array START retains six exact normals and 267/160 reached
premises at their own cuts, with ordered positional/receiver/named unwind and
real start exception sites. Actual 352 over `262ab0c38` passes strict compilation
at `c757a7e25`; no earlier evidence is renewed. [Ledger](coverage/semantics/fiber-array-start-review.json).

Generator 363 handles uncaught request-finally and throwing-handler fatal cleanup.
Actual close/cache owners survive normal rendering and handler-registry mutation;
the reported exception releases after frozen emission and before bailout suppresses
later destructors. Internal C-root trace rows preserve real function arguments.
Seven exact php_error255 originals and 493 strict premises pass at separate cuts.
Normal post-report stdClass and ordinary child storage add one exact fatal original
and 161 premises, preserving real pins and excluding consumed prefixes only from
the future validation view. Earlier seven/493 cuts retain their own inputs.
The current 353-module composition over `a210cd253` passes strict compilation at
`b7b693fa3`; earlier validation retains its own inputs and current fields remain intact.
Original refusals, preparation stops and corrected trace/admission failures stay at zero.
Request C-root renderer rethrows with no current handler add three exact fatal
originals and 527 reached premises. The real receiver decrement preserves owners;
the builtin inner Throwable reports/releases before the original report and
Generator/cache/EHR carriers are abandoned. Structural future projections avoid
heap-query recursion; full admission and malformed producer rejection remain intact.
Actual 356 over `2b98ff468` passes strict compilation at `72d5f7353`;
private source/state cuts retain their own inputs.
A renderer-installed handler returning normally adds three exact fatal originals
and 611 reached premises: inner release precedes handler restoration, warning callbacks
receive Unknown/line0, and fatal reporting reads the original live cached string.
Real pins/transient Weak owners, actual-head refusal and budget replay pass.
Actual 358 over `b721887ce` passes strict compilation at `00536106a`, preserving
current source/argument/storage fields; private 3/611 retain their own inputs.
A throwing renderer-installed handler adds two exact fatal originals and 163/180
strict premises at separate cuts. Genuine EHR/renderer-return/outer-report carriers
retain prior exceptions and Generator/cache owners while the new renderer holds
three roots; frozen reporting precedes its release and reporting-zero destructor.
The release replay starts from its already authenticated bailout; all 180 premises
remain. Earlier nondeterminism, wrong renderer-owner and 120-second AL/SL timeouts
retain zero affected credit. Final 358 over `ea04fbbe4` passes strict compilation
at `ff3d3278b`, preserving named-SEND warning shapes; the earlier 2aa/646 compiler
and private source/state cuts retain their revisions. A throwing renderer warning
callback redispatches through the restored handler before warning cleanup resumes
the original empty cached fatal report. Exact source1 and strict compiler358 retain
`558e53a9c`; 220 reached SL premises retain `80be20cde`. Genuine warning/handler/report
owners and malformed source/site/line/origin rejection pass; initial binding stops
and the incorrect fixed-argument phase retain zero credit. Actual361 over `59c163ef4`
passes strict compilation at `7983c825f` (6.128 seconds), preserving current ARG/CALLS
fields; private source/state cuts retain their inputs. A ROOT/nonuser ordinary
child destructor throwing during reported-exception release, with no live handler,
emits a second fatal while retaining the unfinished release tail. The Parent pin
keeps Weak lookup null; two Leaf C claims and real Generator/cache owners survive.
Actual unreleased fatal frames retain both INSTANCE pins and nonowning retired
HANDLE jobs; borrowed history is not another carrier. Source1 retains `7d3574e75`;
549 SL premises and complete compiler361 retain `47c8c3c1c` (6.459 seconds).
Original refusal, diagnostic/binding stops, cache/retirement fixture failures and
Weak/GC admission gaps stay at zero. Final361 over `e889a1592` passes strict
compilation at `77e534575` (6.488 seconds), preserving EX34's301/372 collector
guards; this source has no collector task. Private source/state cuts retain their
inputs. A declared property ALIAS whose last local alias is unset transfers its
HCELL then Leaf through the actual release chain and emits the same second fatal.
Stable retired-cell markers and STORE evidence certify the consumed child without
owning it; Parent Weak-null and both Leaf C claims survive. Source1/compiler361
retain `c5b8de418` (6.315 seconds); 677 strict SL premises retain `4870a1a8c`.
The original Unsupported, reached discriminator and pre-evaluation bounds syntax
stop retain zero credit. Actual363 over `d54dd9fa8` passes strict compilation
and the affected 677 SL group at `a2847abb8` (compiler 6.438 seconds). Three shared
message predicates observe bytes across the parent's immutable carriers;
private source/compilerc5 and state487 retain their cuts. A declared array child's
sole owning Leaf entry transfers through genuine HARRAY retirement and emits the
same second fatal; retired contents add no array pin, GC slot or child edge.
The real shared-array control keeps its live owner and Leaf silent through the
first fatal. Source2, strict712/77 and complete compiler363 retain `5da367130`
(6.312 seconds). The original primary Unsupported and 118-premise reached
discriminator retain zero credit at `4c410b607`; the exact shared baseline is a
separate control. Actual364 over `70c5ff9fc` passes strict compilation at
`3aeb34484` (6.399 seconds). The parent's retired-owner carriers remain empty on
both sources; current frame/fatal-history fields survive. Private source2/789
retain their `5da367130` inputs. A sole reference entry retires HARRAY then HCELL
before the authentic Leaf release; stable cell markers and historical rows add
no owner, edge or GC pin. An explicit global reference instead retains the cell
and Leaf through the first fatal. Source2, strict816/113 and complete compiler364
retain `9faf09e39` (6.536 seconds). The initial helper-load stop, failed local-CV
alias control, primary Unsupported and 172-premise reached diagnostic remain zero.
Final366 over `87752f2a0` passes strict compilation at `807fa6013`
(6.471 seconds). Empty parameter attributes/plain traces add no sensitive wrapper
or owner; Aggregate/Fiber, quantity and undefined-read hooks are inactive.
Private source2/929 retain their `9faf09e39` inputs. Wider
handlers/rendering, child lifetimes, reacquisition, message warnings,
parked/escaped storage and generic terminal cleanup remain required.
Actual 351 over `7c4a13bc1` passes strict
compilation at `ba1c17c07`, preserving current schema, storage and collector/source
guards; private source/state cuts retain their own revisions.
[Ledger](coverage/semantics/generator-request-abrupt-review.json).

Module 364 converts simple Fiber API arrays to first-class Closures, including
start and constructor methods. An independent ARRAY witness freezes selected
members; the temporary bound receiver owner moves into the Closure, while static
object inputs stay nonowning after retirement. Existing consumers retain named
buffers, traces and last-RAW cleanup; duplicate conversion tasks fail admission.
Strict compilation of 349 modules, nine exact normal originals at 1+8 cuts and
261 independent plus 121 author premises pass. The live-static helper overlap is
corrected with a disjoint bound guard and a fresh ordinary-static counterexample;
the static-source failure and compiler/preparation/fixture stops retain zero
affected credit. Ordinary array-selected start, raw array C-root callbacks,
compound selectors and Fiber-start unpacking remain required.
Actual350 over `f0ab3bcaa` passes strict compilation at `3ef6eb4e9`, preserving
current collector/source/static and storage-table guards; private source/state
cuts retain their inputs, with no earlier362/358 renewal.
[Array-capture ledger](coverage/semantics/fiber-array-captures-review.json).

362 selects ordinary callable arrays with simple Fiber API method names before
argument evaluation. Frozen members survive selector retirement and REF mutation;
one bound receiver owner transfers from CONFIG to its waiting API, while static
object selectors own none. Local receipts preserve recursive argument frames,
real saved callers and constructor warning/validation order. Strict346,
thirteen exact normal originals at12+1 cuts and independent259/author206 reached
premises pass. Three required array-start/FCC/C-root Unsupported controls earn
zero agreement. The compiler stop and original static fixture failure remain
zero; the corrected fixture pins V in its genuine cleanup carrier and queued
receiver retirement. Compound selectors, Fiber-start unpacking, broader adapters
and lifecycle/library behavior remain required.
Actual348 over `b03c0d918` passes strict compilation at `e109fec8a`, preserving
current storage pins, compound/SELF, Generator and generic ownership paths;
private source/state cuts retain their inputs.
[Array-consumer ledger](coverage/semantics/fiber-array-consumers-review.json).

Module 360 closes normal request delegations, detaching real input owners before
finally while retaining independent CV owners and shared store order. Delegated
CURRENT is the physical value slot; consumed-cell history is tied to the object's
own storage stage. Nested normal handlers retain inner cache/close pins and admit
the authenticated queued outer source frame. Eight exact normals and 553 new
strict premises pass at separate cuts; malformed actual handlers remain rejected.
Composition with 346 modules over `9cacdbf51` passes strict compilation at
`4d867f6b0`, preserving current ownership/source/Fiber/collector semantics;
earlier source/state cuts retain their inputs.
Original Unsupported/failed cuts stay zero. Abrupt terminal cleanup, parked/escaped
storage and broader lifecycle work remain required.
[Ledger](coverage/semantics/generator-request-delegation-review.json).

358 selects simple Fiber API method arrays and static class-method strings
through `Closure::fromCallable`, including named and unpacked factory arguments.
Frozen members and completed factory history survive callback-array mutation,
array retirement and factory-owner retirement without new metadata roots.
Bound receivers and static object selectors keep their distinct ownership;
direct, explicit `__invoke` and C-root calls reuse the existing API protocols.
Successful waiting resume/throw traces retain their actual API callsite.
Strict342 initialization, ten exact normal originals at7+3 cuts and independent288
plus author114 reached premises pass. The original trace mismatch and two fixture
stops retain zero affected credit; native recorder preparation stopped before
launch and is separate from the accepted ten-original native cut.
The actual345 composition over `d5e07cef2` passes strict initialization, preserving
current Generator/source/property/collector and trait target-reuse guards; earlier
source/state cuts retain their inputs.
Fiber-start argument unpacking, ordinary API callable arrays, effectful compound
factory selectors and wider lifecycle/library consumers remain required.
[Fiber factory ledger](coverage/semantics/fiber-from-callable-review.json).

Direct ECHO now admits an ordinary CV dynamic callee with no arguments.
The source certificate selects INIT5 independently of call7 and ECHO5, before
operand retirement, live selection and warning demand. Undefined handlers resume
captured null; invoker/array selection and existing TMPVAR/HCELL output ownership
preserve mutation and retirement order. Dynamic and implicit-string declaration
history alternatives now have disjoint domains, allowing a returned cast to
publish a function before later eval. Nine exact originals retain seven rows at
`50f11389e`, late installation at `dc8943d37` and cast publication at `f01375e6f`,
all private354. Independent239 premises retain `dc8943d37`, with38 fresh history premises at
`f01375e6f` (277 total,193 bindings/84 checks). Actual356 over `5107cc589`
passes strict compilation with reviewed Generator/collector/scoped-method and
assertion-state compatibility. Original
baseline mismatches and nondeterministic replay failures retain zero agreement.
No module, task or owner schema is added; wider callee/argument forms remain open.
The one-positional-CV increment now preserves independent INIT5/call7/SEND-ECHO9,
selected targets across returning/throwing argument warnings, silent missing
by-reference cells and existing returned TMPVAR/HCELL output ownership. A narrow
nonowning discard source keeps SEND9 destruction distinct from ordinary body
throw7. Nine fresh exact originals retain two rows at20cd and seven at491e;
independent231 premises (153 bindings/78 checks) pass at491e/private356.
Actual358 over478710ea passes strict compilation with reviewed Fiber/collector
and storage seams. Earlier9/277 retain their cuts; wider call shapes remain open.
The named-CV increment additionally separates SEND/ECHO line9 from operand
metadata line11. Its source-selected warning shape rejects forged operand metadata
before fallback; the existing nonowning discard source preserves throwing-handlerD9.
Second-slot/default binding, unknown-name priority and independent returned
reference cells keep their runtime protocols. Eight exact originals and251 independent
premises (entry101/warning72/result78;170 bindings/81 checks) retain `db5c0f0f3`/358.
Actual358 over `2aa14083a` passes strict compilation at `a2dcb99e3` with reviewed
current seams. Prior9/231 remain unchanged; wider call shapes remain required.
[Ledger](coverage/semantics/source-echo-dynamic-cv-call-review.json).

Direct ECHO now admits one named ordinary CV argument through361's existing
certificate and owning output protocol. INIT5 precedes live SEND; known second-slot
binding uses ECHO8, while late-bound names use7. Default holes, unknown-name errors
before CV demand and fixed-null returning warnings retain their native order.
Returned TMPVAR/HCELL values survive post-SEND argument mutation. Seven exact
originals and204 independent premises (142 bindings/62 checks) retain `5baec287b`/351.
Actual354 over `1c4c8f283` passes strict compilation with reviewed current-parent
compatibility. The unchanged baseline's parent/cast lines and early destruction
retain zero agreement. No new module or owner schema is added.
[Ledger](coverage/semantics/source-echo-named-cv-call-review.json).

SOURCE365 extends361 through a shared certificate for one ordinary positional
CV argument. INIT5 precedes live SEND8; operand retirement can install the callee
or replace the CV, while returning warnings send fixed null and earlier throws
abort later work. Returned TMPVAR/HCELL values retain bytes after argument deletion;
conversion and final release use ECHO8 independently of call initialization.
Public pending/active cast admission authenticates that separate line.
Nine exact originals retain seven rows at `21fc1ae04`, eval at `3493d49bd` and the
new line discriminator at `3c9cc065f`, all private349. The two unchanged baselines
and intermediate final-destructor line mismatch retain zero affected agreement.
Independent236 premises (150 bindings/86 checks) retain three groups at `f5f4ac0c1`
and the affected result group at `3c9cc065f`. Actual351 over `760771d9d` passes
strict compilation with reviewed Generator/Fiber, trait and storage-read compatibility.
No new module or owner schema is added.
[Ledger](coverage/semantics/source-echo-cv-call-review.json).

Source361 selects first INIT for a direct ECHO of a resolved named noarg
nonbuiltin call without namespace fallback. Owned include/eval operands retire
before invocation, allowing late function installation. A returned Stringable
TMPVAR or REFERENCE keeps its original owner beside the cast pin until output;
mutable references preserve returned bytes through an old-referent destructor
exception before later referent cleanup and Throwable replacement. Borrowed CV
release stays distinct. Ten exact originals retain eight rows at `4ea22120a` and
two affected rows at `e51d0e343`, both private344;247 independent premises pass
at the latter cut. Actual349 over CALLS362 `d46556cb0` passes strict compilation
at `eb0ce479d` with reviewed ownership and source-history compatibility.
Original early-free and admission failures and the corrected
pre-call owner fixture retain zero affected credit. Wider calls and output producers
remain required. [Ledger](coverage/semantics/source-direct-call-emission-review.json).

Source357 selects INIT for a named noarg nonbuiltin key call in an ordinary
CV-base DIM, directly under ECHO or before a literal property. Owned include/eval
operands retire before the call; existing runtime keeps the base borrowed and the
returned key fixed before live lookup. Six exact originals and128 independent
premises pass at `d198116d0`/341. Actual343 over `36ccc4520` passes strict compilation
at `3bfd78e2d` with reviewed Generator storage/ordinary destructor compatibility.
Earlier source/state cuts retain their inputs; dynamic/builtin/argument/fallback
calls and wider emissions remain required.
[Ledger](coverage/semantics/source-call-key-emission-review.json).

Generator355 keeps one physical closed-storage pin through Closure/value/key/return
release. Child callbacks retain weak Generator liveness and readable RETURN;
consumed Closure/reference metadata adds no repeated owner. Existing257/303
parents retain pending Throwable priority, with sole-pin retirement before handle
reuse. Six exact normals and 784 new strict premises pass at `b62f360d7`; the two
actually affected maintained storage queues separately pass 209 at `d67773039`.
Actual342 over `dc68616a3` passes strict compilation at `f78a1a06b`;
reviewed current-parent composition preserves the separate source/state cuts.
Original failures remain zero; the earlier349 11/663 retains its own cuts. Abrupt
terminal cleanup, parked/escaped storage and nested ordinary-object RETURN reads
remain required. [Ledger](coverage/semantics/generator-storage-pin-review.json).

354 executes bound `__construct` captures directly, through explicit `__invoke`
and as Fiber C-root callbacks. Immutable receivers and real parser/warning
continuations preserve validation-before-status ordering, handler suspension and
last-RAW retirement. Known valid registered callbacks reach repeated-constructor
rejection without executing their bodies. Strict339 initialization, eleven exact
normal originals at separate cuts and independent210/author112 reached premises
pass. The original registered-builtin Unsupported failure retains zero agreement;
pre-entry names and entered constructor traces retain native frames and arguments.
The actual341 composition over `500a2cedc` passes strict initialization with
reviewed current source353, compound-string352, property-warning and generic
ownership guards; earlier source/state cuts retain their inputs. Outer unpacking,
broader callable adapters and lifecycle consumers remain required.
[Constructor-capture ledger](coverage/semantics/fiber-constructor-callables-review.json).


Source353 selects the first ordinary CV-base DIM read before ECHO or a literal
property, using the key compiler line before live base/key lookup. The affected
writable array-property receiver now separates its table; the later literal
null-property warning has an authenticated fixed-null resume. Seven exact originals
and245 independent premises retain separate private336 cuts. Actual340 over
`ea7cf0a34` passes strict compilation at `7ff6d34c3`; current ARG/GEN/Fiber/collector
interactions are independently reviewed. Original source failures, fixture stops
and the receiver frontier false/vector retain zero affected credit. Wider emission
and receiver forms remain required.
[Ledger](coverage/semantics/source-dimension-emission-review.json).

351 executes captured `start` as a Fiber C-root callback. Immutable RAW selection
and genuine outer caller chains preserve separate original/copied argument
buffers, RAW/result Closure owners and borrowed API receivers. Inner traces have
no file or line site; actual outer callsites, body exception identity and
last-callback retirement retain their native order. Strict334 initialization,
ten normal originals and independent228/author107 reached premises pass at the
recorded private cuts. The original compiler/source stops, diagnostic prefixes
and author fixture elaboration stop retain zero agreement or state-group credit.
The affected348 C-root control gains agreement only at351; outer unpacking,
constructor captures, broader adapters and lifecycle consumers remain required.
The actual338 composition over `b2fb07e1d` passes strict initialization with
reviewed Generator349, collector345, source350, trait347 and property/ownership
interactions; earlier source/state cuts retain their inputs.
[Start C-root ledger](coverage/semantics/fiber-start-core-callables-review.json).

Collector345 preserves cached callbacks across suspension and genuine reentry
within the same live physical pass. The parked VM authenticates its real suspend
and saved-frame projections; reentry binds the fresh public API without detaching
or adding an owner. One normal source and 228 independent physical premises pass
at separate cuts, including captured old/new exception priority and exact full
continuations. Both captured source variants retain 60s CLI timeouts/zero agreement;
fixture stops remain zero affected credit. Final 343 over `e1c3d4d61` compiles at
`bb74145c7`, preserving reviewed Generator storage, call-key source and eager
owner-order changes; the earlier 341 compiler cut remains separate.
Publication 344 over `2ed57ca8a` preserves the static-property change by review.
Quiescent post-pass reentry separately admits the actual parked VM and fresh
caller after collection completes, requiring no destructor tags and no retired
caller/old-slot authority. One normal source and 203 independent physical premises
pass at separate b28/95fd+9765 cuts; captured source CLI 60s timeouts retain zero
agreement. Final 345 over `4cd2eab3a` compiles at `0c23223f3`, preserving reviewed
Fiber-factory/trait additions. One obsolete maintained post-pass refusal premise
is superseded; earlier cuts are not renewed.
A new internal collection now resumes the same parked callback with null and a
real GC_WAIT caller. Frozen PLAN.SCAN preserves its old local suffix independently
of the reset global scan; UNVISITED gives no DONE credit. Residual tags remain
physical but do not seed retracing. One normal source at 9bc and 154 independent
physical premises at 0f007+9c8246 pass, including original old-error identity,
owner 2→1 and full request cleanup. Original/compact old-error CLI 60s timeouts retain
zero agreement. Final 349 over `63786460e` compiles at `f1b0dea7a`, preserving
reviewed SOURCE361, exact-state pruning graph reuse and dynamic ARG356.
Quiescent public resume/throw now scans residual physical tags in the current
global interval. A persistent mode keeps normalized callback slots under physical
authority; BIRTH owns nothing and supplies no access scope. One compact throw
source and 119 independent physical premises (66/53) pass at separate ed30 fixture
cuts, including both original full continuations and error owner 3→2. The larger
resume CLI retains its 60s timeout/zero agreement. Final 351 over `8e513981b`
compiles at `3f2ff607d`, preserving reviewed GEN363/364/TRAIT/PROPS fields.
Fresh internal entry now scans residual and new destructor tags through the real
GC_WAIT caller and physical interval. Signed accounting preserves the residual
debit: first-pass −1 plus retrace 2 returns 1 while D/E both retire. Independent
91/75 physical premises at separate 6132 fixture cuts complete both originals,
including prior-error identity; both whole CLI runs retain 60s timeouts/zero
agreement. Final 353 over `d2bba03b2` compiles at `3f2016024`.
372 now scans main-thread residual/fresh tags with a local physical interval,
leaving the cached Fiber cursor unchanged. Exact frozen slots and called flags
authenticate callbacks without adding residual D to fresh DTORS; E protects D’s
error before ordinary finally chaining. At `7e5ff7198`/354, strict compilation/init
and 93/78 independent physical premises complete both unchanged originals,
including signed count1, D/E retirement and exact new/previous identities. Final
356 over `a1c5e2626` compiles at `43e793df3`, preserving reviewed abstract-method,
typed freeing-read, raw Fiber-array tasks and ASSERTIONS additions. Both whole
CLI 60s timeouts retain zero agreement.
375 now detaches an internally suspended residual callback and starts a real
replacement worker on the remaining physical suffix. The old guard pin and
finally error stay in its actual saved VM; replacement pending is separate, and
fresh-plan progress is unchanged until callbacks finish. Independent 92/105
physical premises at separate `be1099c26` fixture cuts, finalized as `7e72ff341`,
complete both unchanged originals, including count0 followed by later count1,
distinct old/new errors and old-worker termination. Both whole CLI 60s timeouts
retain zero agreement; the first error-state 120s cap retains zero affected credit.
Final 357 over `b7419cbe1` compiles at `9ce39cd54`, preserving current assertions,
private-constructor, storage, source and Generator cleanup changes.
Last-cache-owner physical replacement now closes the actual suspended worker
before starting its replacement. Normal close runs finally; failed close moves
the real error into plan pending while the caller's outer error stays in FINALLY.
Only the actual normal/failed private-control release tail gains storage/scoped
admission. Independent 77/89 physical premises at separate `4227d8609` fixture
cuts, finalized as `292b27847`, complete both unchanged originals, count1/weak
retirement and exact new/previous identities. Both whole CLI 60s timeouts retain
zero agreement; the first failed-state root-order premise has zero affected credit.
Final 358 over `0059e0a9e` compiles at `0da2cdae7`, preserving both empty-PACKS API
constructors and reviewed inherited-constructor/quiet-read behavior.
Old public callbacks can now suspend again during internal takeover. Detachment
captures the reset global cursor's advanced suffix, preserving earlier marked
targets without DONE credit and keeping the two real FINALLY errors separate.
At separate `88daee39b` fixture cuts, finalized as `27e65e46e`, 114/98 independent
physical premises complete both unchanged originals. The affected error fixture
now checks request-final retirement of the new error; its obsolete lookup has
zero affected credit. Both whole CLI 60s timeouts retain zero agreement. Final
358 over `6ed4873bd` compiles at `0bc957892`, preserving reviewed Generator render
and dynamic-source hooks.
Different-main public reentry345 now authenticates the actual parked VM/fresh API
while preserving fresh main tags after the old target slot is reused. Old guard
INDEX equals the global cursor; the completed local scan must be INDEX+1, so a
rewind cannot consume the fresh E callback. Independent normal96 at `93cb1cfd5`
and throw109 at `950c158d5` complete both unchanged originals with exact error
identity, heap-identical forgeries and budget replay. Actual359 over `0c549de11`
passes strict compilation/init at `280feeb2a`, preserving GEN176/363 and the
PROPS207/377 warning and ownership interfaces. The printable-metadata helper is the concrete
changed cost dependency for the one throw-only retry; no general speedup is inferred.
The initial undefined-helper compiler stop, first throw-state 120s timeout and
both whole CLI 60s timeouts retain zero affected/agreement credit. Overlap, wider
active residual/Fiber-pass reentry, earlier whole CLI completion and broader GC
remain required; earlier cuts are unchanged.

During a live main callback, public resume/throw of the idle worker now scans
snapshot-marked residual targets outside the fresh plan's DTORS. The authentic
main return, physical cursor and tags govern admission without changing fresh
plan progress. Two native-grounded unset-order companions pass whole CLI60 and
174 independent physical premises (95/79) at `c5a3e54df`, preserving count1 and
exact replacement/prior exception identity. Actual361 over `9988f88bf` passes
strict compilation/init at `5d89edb95`; reviewed Traversable, Generator and
computed-static paths preserve this lane. Four earlier native observations and
the first failed diagnostic remain preserved; corrected41 only localizes refusal.
[Ledger](coverage/semantics/cycle-collection-review.json).

Residual/eligible overlap301 now admits a closed white ordinary-object component
on main PASS0. Physical nested removal clears D's old tag before fresh E runs; the
single retrace calls D, frees E and leaves D's self-cycle/weak probe live, with
signed count -1+1=0. The exact current RETURN pin authenticates preselection SITE
before CALLED; executable return and future-tag/cursor checks retain authority.
One unchanged whole CLI60 source and 247 independent premises (165/82) pass at
`85b9d0b73`. Baseline38 and image110 localize distinct boundaries; earlier compiler,
source/133 and obsolete79 fixture failures retain zero aggregate credit.
Black-root/array/reference/proxy/Fiber overlap and wider GC remain required.
Actual361 over `8ac503030` passes strict compilation/init at `d77cd6d9a`, with
independently reviewed call, ownership and scalar-return interfaces; earlier
source/state cuts are unchanged.

Mixed overlap301/372 now permits separate ordinary residual components outside
the eligible graph, with an incoming-owner closure and surviving-tag authority.
In the grounded original, nested removal drops D's tag while F survives for selection
before E; signed -2+2 returns0, F/E retire and D retains its self-owner/weak liveness.
Source1 and 321 independent premises (215/106) pass at `a2ef8b039`; role-bound
physical slots preserve exact removal, cached-W reuse, retrace order and replay.
Baseline66 localizes the old301 refusal. The first195 ordering fixture fails with
zero aggregate credit; corrected controls change no code/source. Broader
black/external/nonordinary/Fiber/later-pass overlap remains required; prior cuts
and whole CLI timeouts are unchanged.
Actual361 over `be0cfaa7f` passes strict compilation/init at `9391ce28e`, preserving
reviewed call/ownership/property interfaces; source1/state321 retain their inputs.

Closed white ordinary-object overlap317 now runs on a genuine ordinary Fiber
through its distinct idle cached worker when every residual tag is removed.
Exact nested images, saved caller/API and real guards preserve physical cursor,
ordinal and CALLED authority. Source1 agrees under CLI60 at `e3d359d01`; five
source-reached cuts155/134/172/54/130 cover all408 original obligations
(645 executed premises include repeated setup), with count0, E retirement and
D self-owner/weak-live. Pure lookup/source-site factors preserve all validators.
Earlier compiler stops, source failures and timeouts retain zero credit;
nonordinary/later-pass overlap and wider GC remain required.
Actual367 over `6e709da74` passes compiler/init at `020f95d30`; reviewed carrier,
fatal, reference-return and promotion interfaces preserve the unchanged e3 cuts.
[Ledger](coverage/semantics/cycle-collection-review.json).

Mixed ordinary-Fiber overlap301/345 now scans surviving physical tags after
nested removal through the actual U caller and cached worker W. Exact initial BUFFER/FREE,
surviving F/E tags and the selected physical guard retain authority without adding
F to fresh DTORS/progress. Three independent source-reached cuts 147/95/118 at
`fb872a74e` execute 360 premises: F→E→D, signed -2+2=0, F/E retirement, D self-owner 1
and weak-live, request cleanup and replay. Compiler/init pass; baseline 97 and
projection 66 localize ingress and first selection. The first 146-premise fixture clears an
owner-bearing caller and fails with zero credit; its corrected LINE-only forgery
preserves the heap. The whole source CLI60 timeout remains OPEN with zero source
agreement, and only that source is excluded from the default whole-CLI campaign.
Wider overlap/throw/reentry, nonordinary/non-idle and later-pass lanes remain required;
prior cuts are unchanged. Actual370 over `71cf292aa` passes compiler/init at
`aecdcb088`; reviewed typed-return, caller and retained-root interfaces preserve
the fb872 cuts and whole-source CLI60 OPEN/zero agreement limit.
[Ledger](coverage/semantics/cycle-collection-review.json).

Array-mediated overlap301 now permits nonproxy HARRAY alongside HOBJECT in the
fresh closed-white component, retaining the object-only residual-reach fence.
Three source-reached cuts 118/107/corrected104 at `f184ac959` execute 329 premises:
real ordinary-Fiber E→array→D, nested D/array removal with debit4, exact E guard,
signed -1+2=1, E/array retirement, D self-owner1/weak-live and terminal replay.
Native grounding and compiler/init pass; baseline91 localizes the old301 refusal.
The first104 fixture expects a marked E after real selection normalized it and
fails with zero credit; its separate correction changes no code/source.
Whole source37 CLI60 remains OPEN/zero agreement and only that source is newly
excluded from the default whole-CLI campaign; all three state groups remain enabled.
Main/mixed array layouts, references/proxy tables, black/external components,
non-idle caches and later-pass overlap remain required; prior cuts are unchanged.
Actual371 over `d80c97b3c` passes compiler/init at `9233da4ca`; reviewed local-CV
return, property/caller and captured-constructor interfaces preserve state329 at
f184 and the whole-source CLI60 OPEN/zero agreement limit.
[Ledger](coverage/semantics/cycle-collection-review.json).

Reference-mediated overlap301 transparently follows genuine unbuffered HCELL
edges without reference debit. Fresh-component reach, live reference markers and
canonical frozen cell shapes preserve count/image and current worker authority;
residual arrays and outside references remain excluded. Three source-reached cuts
corrected159/130/118
at `b5fc0476e` execute 407 premises: direct/duplicate reference walks, real E guard
and marker/shape counterfeits, signed -1+2=1, E/array/reference retirement,
D self-owner1/weak-live, request cleanup and replay. Native grounding and compiler/init
pass; baseline101 localizes the old refusal. The original159 stops on literal-record
syntax before semantic checks with zero credit; its separate correction is syntax only.
Whole source38 CLI60 remains OPEN/zero agreement; only its default whole-CLI
selection is newly excluded, with all state groups enabled. Broader reference,
main/mixed, proxy/black/external and later-pass overlap remain required; prior cuts
are unchanged. Actual371 over `8ea50de70` passes compiler/init at `711bedcfd`;
reviewed shared compiler/property/return interfaces preserve state407 at b5fc and
the whole-source CLI60 OPEN/zero agreement limit.
[Ledger](coverage/semantics/cycle-collection-review.json).

Protected residual self-reference overlap301 now permits an unbuffered canonical
HCELL only inside fresh-DTORS reach, preserving outsider object closure and all
existing marker/count/image/guard checks. At `1c1de818d`/371, three source-reached
cuts138/122/115 execute 375 premises: direct/duplicate reference traversal,
nested D removal/debit3, real E guard, signed -1+1=0, live D/reference owners1,
E retirement, weak liveness, request cleanup and replay. Native and compiler/init
pass; baseline98 localizes the old residual object fence. Whole source39 CLI60
remains OPEN/zero agreement, with only that default source selection excluded.
Residual arrays/outside references, main/mixed layouts, black/external components,
non-idle workers, later passes and broader GC remain required; prior cuts unchanged.
Actual372 over `fb58ba46f` passes compiler/init at `fb0d5750e`; reviewed hook,
getter/caller and return interfaces preserve state375 at1c1de and source39 CLI60 OPEN/0.
[Ledger](coverage/semantics/cycle-collection-review.json).

Protected residual arrays301 now require nonproxy fresh-DTORS reach. Closed white
object/array producers remove nested BLACK data before parked callback takeover
and ordinary worker PASS1; the zero-owner image task and saved WAIT authenticate
transfer, while worker-only frozen replay retains separate current-image/guard pins.
Six source-reached cuts117/127/112/84/83/36 execute559 premises at their preserved
b481/f2/1df revisions (372 modules): signed -1+1=0, live D/array owners1, E retirement,
weak liveness and native END/request cleanup. Native/compiler/init pass. Terminal36
executes one full continuation; independent pure-function congruence of its checked
zero-budget state identity supplies the omitted second-drive equality. Earlier
zero/one-step replay checks execute. Full58/compact37 SL120 timeouts retain zero
credit. Whole source40 CLI60 remains OPEN/zero agreement
at144cc1, with only that default source selection newly excluded; all six state
groups stay enabled. New main source agreement, fresh reference/proxy producers,
outside/black/external components and broader GC remain required; prior cuts unchanged.
Actual374 over `4368f9d6` passes compiler/init at `e4606537`; reviewed return,
factory/property/class interfaces preserve the original559 cuts and source40 OPEN/0.
[Ledger](coverage/semantics/cycle-collection-review.json).

Disjoint residual-root reach301 now admits canonical unbuffered references while
the protected component and outside-array fence remain unchanged. Live markers
cover protected and residual reach through SCAN and selected guards; fold, count
and owners are unchanged. The literal F.s reference variant of source36 passes
first-SCAN55, marker/shape57+pure9 and genuine F65/E67 selection at preserved374 cuts.
At375, physical PASS1 frontier30 passes atb002 (112.390s), actual retrace transition26
atbb1a (114.863s) excludes the reference from COUNTED and includes it once in
FREESET, and one terminal continuation26 at0575 (123.814s/cap180) retires F/reference,
leaves D weak-live, clears GC and matches native113 END events. Seven cuts execute
326 genuine/control checks plus9 pure exclusions; exact transfers preserve all
prior cases and only the new terminal uses180 (existing defaults120).
Compiler/init pass at000bee and current-parent09be; baseline115 is localization only.
Whole source41 CLI60/180 remains OPEN/zero agreement. Its finite100-step CLI cut
establishes checked early progress only; counted seek120 timed out without a frontier.
Both image197 runs, terminal81/57
and E66's syntax failure retain zero credit. Wider main/mixed/black/external/reference
layouts and non-idle workers remain required; source40 and earlier cuts are unchanged.
[Ledger](coverage/semantics/cycle-collection-review.json).

Main-thread residual overlap301 removes a held live child's old physical tag
without collecting it. The object cut at `8f630`/375 retains native81 source
agreement and103 source/control checks plus2 pure exclusions, including the
outside-held-F frontier. Its reference companion at `21daa`/375 admits canonical
unbuffered HCELL only inside fresh-DTORS reach; the live REFCELLS marker and
frozen reference shape remain separate requirements. Compiler/init, native81
whole-source agreement and99 source/control checks plus2 pure array exclusions
pass: real TRACE/image/E selection, held/weak D, marker/shape/slot/consumer
negatives and zero/one-step replay. Collection returns −1; D runs after END.
Baseline35/49 localize the respective original refusals. Count folding/owners
are unchanged; wider reference/array/worker/later-pass overlap remains required.
The held-F42 original completes at `84e975`/375 in107.411s under CLI180/recorder195,
matching retained native110 with F weak-live at END. Its existing source row is
enabled with that cap; other source cases retain60/75. The original CLI60 timeout
keeps zero credit; source41 remains OPEN/zero and prior cuts are unchanged.
[Ledger](coverage/semantics/cycle-collection-review.json).

Main collection301 now disposes a separate non-destructor `stdClass` self-cycle
reacquired through WeakReference during a destructor. The marked global CV becomes
a nonowning retired slot; weak lookup clears, direct strict-null identity and
overwrite/unset work, and unsafe reads remain explicit Unsupported. Free order,
count folding and ordinary heap validity are unchanged. At `5cc17`/375, compiler/init,
one exact native33 source agreement and146 reached source/control checks (101/45)
pass, including genuine disposal/comparison, owner fences and zero/one-step replay.
Baseline38 localizes the old refusal; the first recursive-fallback compiler stop
retains zero gate credit. Broader retired-object identity, containers, pending owners,
workers/later passes and resurrection remain required; old whole CLI OPEN/zero cuts
are unchanged. [Ledger](coverage/semantics/cycle-collection-review.json).

Main final-retrace preparation301/325 preserves the existing root slot of an
authenticated called ordinary zero-owner leaf outside FREESET. The borrowed tag
adds no owner; actual weak-temporary acquisition promotes it to an ordinary root.
At `1496e`/375, compiler/init, one exact native44 source agreement and203 reached
source/control checks (113/90) pass. Real FREE-to-finish retention, coherent leaf,
slot, called/DONE/consumer controls and one native continuation are covered.
The acquisition cut follows both BASE/operand owners through comparison and
shared release to the actual storage pin: weak lookup is null while allocation
and its physical GC_RETIRED slot remain. Zero/one-budget replay passes. Baseline39
localizes the old refusal; the two premature fixture assertions and root tuple
observation retain zero credit. Workers, pending collectors and wider child layouts
remain required; count folding and old OPEN/zero cuts are unchanged.

Main PASS1 preparation325 also retains one fresh `stdClass` leaf child owned only
by that called owner-zero target, outside the frozen graph/FREESET. Existing BARE
retention preserves the edge without an owner/count change. At `800e`/375, full
compiler/init, native66 source agreement and199 reached source/control checks
(retention129/child-temporary70) pass. Actual child copies release3→2→1 while the
parent stays borrowed; ordinary parent acquisition/release later disposes both.
Coherent graph/type/owner/slot/DONE negatives and zero/one replay pass. Baseline51
localizes the former refusal; the original127 no-op nonleaf control retains zero
credit. Wider child/reference/array/worker/pending graphs remain required.

The posttrace child may also have exactly one self-edge, with only its parent and
self as strong owners. At `746417`/375, full compiler/init, native66 source agreement
and212 reached source/control checks (retention130/second-collection82) pass.
Actual FREE retains the parent at owner0 and child at owner2 without a new machine root;
coherent shape/owner/frozen/slot/DONE controls and zero/one replay pass. A genuine
second TRACE observes the parent retired and child self-owner1/current ROOT,
then traces and frees only that cycle; the short ending matches native66.
Baseline54 localizes the old refusal. Wider child layouts, external sharing,
references, arrays, workers and pending collectors remain required; existing leaf
behavior, count folding and source41 OPEN/zero cuts are unchanged.
[Ledger](coverage/semantics/cycle-collection-review.json).

Main PASS1 preparation325 also retains a fresh child→leaf `stdClass` chain,
with each descendant owned only by its incoming parent and outside frozen
GRAPH/FREESET. At `d690cf5e`/375, compiler/init, native86 source agreement and227
reached source/control checks (retention137/leaf-temporary90) pass. Real FREE
keeps the borrowed parent and full chain; the leaf's BASE/operand copies release
3→2→1 without losing either edge. Shape/type/owner/frozen/slot/DONE controls and
zero/one replay pass. Baseline64 localizes the old refusal; its initial text/bytes
fixture elaboration failure retains zero credit. Wider child graphs and earlier
OPEN/zero cuts remain unchanged. [Ledger](coverage/semantics/cycle-collection-review.json).

Main PASS1 preparation325 also retains one fresh `stdClass` leaf reached by two
distinct direct properties of the called owner-zero parent. Child owners are
exactly those two edges; outside ownership is excluded. At `31605c292`/375,
compiler/init, native66 source agreement and238 reached source/control checks
(retention134/property-release104) pass. Real FREE preserves the borrowed parent;
ordinary teardown transfers and releases each property owner separately, keeping
the child weak-live after the first release and clearing weak identity at its
last-owner storage pin. Allocation persists at that checkpoint. Coherent
shape/owner/frozen/slot/DONE controls and zero/one replay pass. Baseline61 localizes
the old refusal. Wider sharing and child graphs remain required; source41
OPEN/zero cuts are unchanged. [Ledger](coverage/semantics/cycle-collection-review.json).

Main PASS1 preparation325 also admits one fresh `stdClass` leaf held by its
called owner-zero parent and a marked global CV cell. The actual global root,
direct payload, marker and unbuffered carrier are authenticated; existing owner
and count folds stay unchanged. At `fef445a292`/375, compiler/init, native76 source
agreement and281 reached source/control checks (retention167/unset114) pass.
Real FREE keeps the borrowed parent; after ordinary parent teardown, global
unset transfers the cell owner to a child release and reaches its physical
storage pin with weak lookup null. Allocation persists at that checkpoint; the
original source covers its later disposal. Carrier/owner/shape/frozen/slot/DONE
controls and zero/one replay pass. Baseline77 localizes the old refusal; the first
compiler iteration diagnostic retains zero gate credit. Wider outside carriers
and child graphs remain required; source41 OPEN/zero cuts are unchanged.
[Ledger](coverage/semantics/cycle-collection-review.json).

Main PASS1 preparation 325 also retains one fresh ordinary INSTANCE leaf with an
uncalled public, nonstatic, concrete destructor, owned only by its called owner-zero
parent and outside frozen GRAPH/FREESET. At `6222daeb8`/375, compiler/init, exact
native 68-byte source agreement and 216 reached source/control checks (retention 128/
callback 88) pass. Real FREE preserves the borrowed parent and uncalled child;
the source-reached callback is weak-live with unique called authority while the
parent is storage-pinned/weak-null. Actual result and VALUE release steps then
clear child weak identity under its own storage pin, retaining allocation there.
Descriptor/owner/shape/frozen/slot/DONE and consumer controls plus budget replay
pass. Baseline 61 localizes the original refusal. Wider child graphs, callbacks,
worker/pending contexts and count/owner closure remain required; source 41 and
prior OPEN/zero cuts are unchanged. [Ledger](coverage/semantics/cycle-collection-review.json).

Main PASS1 preparation 325 also admits an own private child destructor, tying
its cached owner and member path to the actual source declaration. Ordinary
USER teardown raises `Error` before body entry; existing public dispatch and
owner/count/free rules are unchanged. At `6e12cf29e`/375, compiler/init, native
96-byte agreement and 272 reached checks (retention 141/access 131) pass.
Pending-error cleanup reaches both validated storage pins with weak identities
null and allocations retained; the original supplies eventual catch/disposal.
The public throwing-child original already agrees with native 98 bytes at
`69333905f`. Baseline 62 preserves the old private-child refusal as localization.
Wider visibility, inherited methods, graphs and worker contexts remain required;
source 41 OPEN/zero cuts remain unchanged. [Ledger](coverage/semantics/cycle-collection-review.json).

Source350 admits array-valued ordinary computed-name CVs. Its nonowning warning
resume fixes `Array` before live target lookup; handler/child exceptions abort FETCH.
Seven exact originals and117 independent premises retain `c2a1051db`/331. Actual335
over `94e3593e6` passes strict compilation at `4832f2226` with reviewed current-parent
compatibility. The fixture elaboration stop has zero application/acceptance credit.
[Ledger](coverage/semantics/source-array-name-review.json).

348 executes bound `start` first-class captures directly and through explicit
`__invoke`. Immutable receiver selection and original positional/named buffers
survive argument effects, nested same-Closure calls, weak callback receives and
cleanup. Waiting calls borrow the receiver from the Closure; explicit invocation
keeps its extra Closure owner and copied buffer. Status and entry errors retain
actual start callsites. Strict329 initialization, ten normal originals and
independent186/author96 reached premises pass at the recorded private cuts.
Two C-root-start/outer-unpack controls and the separate original `is_int` builtin
dependency failure have zero agreement. That builtin remains required core work;
a distinct fresh comparison original checks the same weak int receive.
At348, C-root `start`, constructor captures and broader adapters remained open.
The actual333 composition over `05ef7bb9f` passes strict initialization with
reviewed Generator/property/Throwable/ownership interactions; earlier source and
state cuts retain their inputs.
[Start-capture ledger](coverage/semantics/fiber-start-callables-review.json).

Source343 adds Stringable ordinary computed-name CVs with a separate cast owner.
Returned bytes survive receiver retirement before live target lookup; a pending
destructor exception permits the default missing-target warning but suppresses
an eligible registered handler. Eight exact originals and134 independent premises
retain private `fdb6e4577`/325. Actual329 over `fe9ad60a9d` passes strict compilation
at `890496dec`, with reviewed callable/trait/collector compatibility. Original
fixture failures and diagnostic cuts retain zero affected credit.
[Ledger](coverage/semantics/source-stringable-name-review.json).

341 executes fixed bound API captures as Fiber C-root callbacks. Immutable RAW
selection preserves the receiver, borrowed API ownership and genuine nested or
idle collector caller chains. Last callback retirement can close its receiver
before the original `start` argument destructor; C-root API traces have no file
or line. Strict324 initialization, ten new normal originals plus one affected337
former boundary, independent255 and author93 reached premises pass at separate
recorded cuts. The narrow saved-root helper correction is covered by full-drive
nested108 and collector93 checks; original failures retain zero credit.
The actual328 composition over `175a197e9` passes strict initialization while
preserving current collector342, method307, source339 and ownership factors;
earlier source/state cuts retain their inputs.
At341, C-root `start`, constructor captures and broader adapters remained open;
paused undefined-result verification is excluded. Earlier331/337 cuts are unchanged.
[C-root ledger](coverage/semantics/fiber-bound-core-callables-review.json).

Collector342 admits public idle resume/throw during an active pass once every
planned destructor is marked called. The real parked collector consumer remains
busy; worker cache/mask and transient error ownership follow332. Two exact normal
originals and two independent strict-SL groups with127/138 physical premises pass
at private323. Final327 over `5f478ea6a` passes combined compilation at `f9dbe3205`,
preserving337/339/307/334 and the pointwise302 factor. Module345 separately handles
remaining-dtor stale intervals; these earlier cuts are unchanged.
[Ledger](coverage/semantics/cycle-collection-review.json).

Source339 adds the missing ordinary name-CV warning before computed FETCH.
Returning handlers change the live caller CV used for conversion; absent/unset
CVs quietly become null, while a later missing-target warning keeps fixed null.
Seven exact originals and171 independent premises pass at private `bf7bcb3da`/321,
including local/global isolation, fallback, throw priority and authentic include
retirement/FETCH6. The actual324 composition over `6b51f811c` passes strict
compilation at `e3d6a7c85` with reviewed bound-Fiber/Generator/collector/array
compatibility. Original fixture failures and diagnostic vectors retain zero
affected credit. [Ledger](coverage/semantics/source-missing-name-cv-review.json).

337 adds bound first-class `resume`/`throw`/defined `getReturn` and status methods.
The Closure owns its selected Fiber; direct and explicit `__invoke` calls borrow
that receiver while retaining their actual argument buffers and saved operation
provenance. Strict318 initialization, nine normal originals and author65/independent403
reached premises pass at the recorded private cuts. Two explicit start/C-root
Unsupported controls earn zero agreement at that cut; earlier331 evidence is unchanged. A
separate actual322 composition passes strict initialization, one collector
original and115 independent premises: captured public resume/throw authenticate
the genuine saved caller, preserve borrowed receiver roots and retire the idle
cache on request completion. The
[bound-callable ledger](coverage/semantics/fiber-bound-api-callables-review.json)
retains these checks and required follow-ons.

Collector338 admits failed last-owner close of a detached worker after collection.
A throwing `finally` retires the one remaining private control owner while the
real error stays in the caller's pending operation; a genuine prior exception
keeps its identity. Two exact normal originals and two independent strict-SL
groups with117/130 physical premises pass at separate private320 cuts. The
322-module composition over `f89fbee745` passes combined compilation at
`9277e334d`, preserving Generator328, source336 and reviewed ownership factors.
Publication over `0bb453754` preserves the disjoint prior-array foreach guards;
the tested compiler/source/state cuts remain unchanged.
Active-pass failed close and wider close contexts remain required; earlier
collector cuts retain their inputs. [Ledger](coverage/semantics/cycle-collection-review.json).

Generator 340 closes paused frames at normal request end through real reverse
globals and ascending store handles. Registered normal handlers run before cache
release; borrowed zero-owner buckets survive bare store decrements until genuine
weak reacquisition restores ordinary release. 19 normal originals and 692 physical
strict-SL premises retain separate private cuts; 85 premises assert required abrupt
controls with zero observation agreement. Actual330 over `7a0f8044f` passes strict
compilation at `1399d8a7e`, preserving source343, bound C-root and collector342
behavior without renewing source/state cuts. The original observer mismatch stays
zero credit. Delegating request close and wider terminal/free-storage paths
remain required. [Scope and cuts](coverage/semantics/generator-request-finally-review.json).

Generator349 closes fresh store frames without entering body/finally, releases
actual parameter/receiver owners, and transfers the single Closure owner.
Root CV-destructor handlers precede later parameter release; closed storage
releases the Closure before caches. Ten distinct normal originals and 584 strict-SL
premises retain separate cuts and original failures. The composition with 337 modules
over `ed1c8c6a2` passes strict compilation at `5dc524df4`; its fresh typed-slot
interaction adds one exact normal source and 79 strict premises. A real free-storage
pin, late WeakReference notification and readable caches during child destructors remain
required. [Bounded evidence](coverage/semantics/generator-fresh-store-review.json).

Generator328 reference caches, value snapshots and effective destructuring aliases
retain their original source/state cuts and actual321 compiler. 340 promotes the
identical active-finally original; its old refusal40 remains zero agreement.
[Reference-yield scope](docs/semantics/GENERATOR-REFERENCE-YIELDS.md).

Source336 adds one named ordinary CV argument to computed-name emission: INIT6
precedes known FETCH8/property11, and unknown `Sent` binds Error7 before CV demand.
Six exact originals and325 independent premises retain private317. The final320
composition over `89c1019cc` passes strict compilation at `29f5f402b` with reviewed
331/324/335 compatibility. The original deferred-operand fixture false and diagnostic
earn zero affected credit. [Ledger](coverage/semantics/source-named-argument-emission-review.json).

Collector335 admits normal last-owner close of a detached worker after collection.
Assigning null to its shared cell runs `finally` immediately; the worker retires
and its borrowed zero-owner target waits for the next real collection/count1.
Two exact normal originals and two independent strict-SL groups with100/116
physical premises pass at the private317 cut. The final319 composition over
`6fac6d270` preserves static Fiber331 and property324 fields/tasks/owners and
passes combined compilation at `e12be6f67`. Failed-finally close338 has separate cuts;
earlier collector cuts keep their inputs. [Ledger](coverage/semantics/cycle-collection-review.json).

331 adds source-authenticated static `getCurrent`/`suspend` first-class Closures
with receiver-free capture, alias/clone history and distinct direct, `__invoke`
and Fiber C-root owners through resume/throw cleanup. Independent sources and
reached-state guards retain their private cuts. The actual317 composition over
`e91fc6d6` passes strict compilation; newer collector/source/GC guards remain
intact. [Scope and retained cuts](coverage/semantics/fiber-static-api-callables-review.json).

Collector332 adds quiescent public resume/throw into the cached collector Fiber.
Its real caller transfer preserves the worker mask and idle cache without a
stored exception or supplied-value worker owner. Strict compilation/initialization
and three exact source controls pass at `084aebce1`; two explicit strict-SL groups
with169 premises pass separately at `0649fd604`. The final315 composition over
`79546523e` passes combined compilation at `f3d62ee7b` without renewing earlier
cuts. Module342 separately admits active transfer after destructor exhaustion;
remaining-dtor transfer stays Unsupported. Complete GC and the fresh
combined offline rebuild remain required.

Collector325 retains a detached zero-owner target and its outgoing graph through
a borrowed buffer tag, without adding an owner. Real weak reacquisition restores
ordinary last-owner release and parent retirement before child destruction.
Three exact originals and85 reached premises pass at separate private cuts.
An actual305-parent unowned-close original collects the target in the same active
pass;117 reached premises validate its real two-owner private-control retirement
and saved caller VM. The narrow scoped admission repair passes changed compilation.
The final309 join over callable Fibers322 passes its sole combined compiler
at `b4cfe4a14`; earlier source/state cuts retain their identities.
[Scope and retained cuts](docs/semantics/CYCLE-COLLECTION.md).

Integrated321 copies a known YIELD value before an ordinary missing
key-CV warning, authenticates one object-specific partial-cache carrier and keeps
null key/index/opcode-line behavior through callbacks. Actual child-resume markers
select child catch/finally reinjection for KEY and311 VALUE warnings; direct API
resumers preserve closed-cache ownership. A narrow303 release-only handoff moves
cached destructor owners once and preserves replacement exception priority.
Strict compiler295,27 exact normal observations and eight genuine reached groups
with658 physical premises pass at their separate c102/7edf cuts. Actual
`642659405`/304 composition passes strict compiler305 at `309c9b25f`, preserving
accepted receive/source/ARG319/collector fields. Independent seam review requires
no source/state renewal. Original failures and the older required close Unsupported
retain zero credit.
[Scope and results](docs/semantics/YIELD-KEY-WARNINGS.md).

Arrow Generator311 is integrated; its frozen310/276 cut retains44 normal source
agreements, nine compiler rejections and10 genuine strict-SL groups with987
setup-inclusive premises retain separate cuts; two required Unsupported controls
earn zero agreement. Eager receives, deferred captures, implicit sent/delegated
returns and original signatures use accepted280/95/118. Value warnings freeze
null before delayed keys; throwing handlers install the closed Closure owner
before eager frame retirement. The frozen286 parent is privately composed
with exact311 and maintained fixtures at287 modules. One fresh original combines
an eager NEW default, active Fiber, temporary Stringable eval CV ECHO entry and
last-owner child close. Its scoped source/Fiber validator repair passes strict
compiler287, one native/model agreement and148 independent reached premises;
earlier cuts retain their identities. Exact311 also composes over the actual
`2a2e1af7c` property/collection parent at292: strict compilation, the same original
and75 independent source-HANDLE/Arrow-close/gc/clone premises pass without
renewing148. Final294 preserves accepted ARG309/316 and passes strict compilation;
their introduced seams are independently reviewed as compatible, with no source/state
renewal. Earlier cuts retain their own tested parents.
[Scope and retained cuts](docs/semantics/ARROW-GENERATORS.md).

The current source includes accepted ArrayAccess292/304/309/319/326/329, eager destruction270,
WeakReference296, ordinary cycle collection301 and collector Fibers317/325/332/335/338/342/345,
Fiber291/302/308/313/322/341, Generator289/303/310/311/321/328/340 and source operands293/298,
plus instance/readonly properties288/294, clone300/305 with cached maker selection
and ordinary dynamic-property creation318, physical references324 and defaults286/295/306/312,
with 336 modules composed over
`6e107993a`, retaining static/bound Fiber API captures331/337/341/348, property references324/346, Generator344 and collector335/338/342/345.
The ordered integration preserves
the final Generator eager-release bridge, Fiber cleanup guards and source-emission314/316/320/323/327/330/333/336/339/343/350.
The property/clone composition passes strict SL290/compiler application0 at
f6b2cad34, two new exact normal originals and79 independent strict-SL premises at
4767e8ea6. Transfer onto68393 retains the same semantic inputs. Earlier private
cuts below retain their original inputs.
The preceding 284-module cut passes strict compilation, one exact source original and
49 reached premises during active nested Generator delegation. Earlier accepted
cuts retain their original inputs. Accepted290/297/299 add composing-owner REAL
births, dead failure receipts and fatal trait class-name reservation. Their actual313
join passes strict compilation and one fresh REAL/constructor/capture-retirement
source with46 supplied reached conditions; earlier cuts retain their identities.
Nonconstant source-emission314 is installed after Fiber308; literal auto-global316
is integrated after reviewed current-parent composition.
Held 279 and user-paused return verification stay set aside. Complete core and the
final combined, fresh offline rebuild remain required.

Default composition adds286/295/306/312 over actual canonical296,
preserving ARG309/316, property, clone, GC301 and shared source hooks (300 modules).
Exact `279839ac4` passes strict initialization and one fresh native/public original:
two default warning frontiers retain GLOBALS snapshots and storage/readback,
with exact `ArrayArrayg:g:l2:A:B` in29.546s at unchanged45/55 caps. Its omitted-request
Unsupported remains zero; the corrected gate uses matched explicit CLI facts.
Raw records are under `.tools/compiler-defaults-publication-18/.tools/defaults-publication/compact-gate-v{1,2}`.
The genuine current107 prefix/source-origin/refusal/retirement predicates pass
on `b50d4062e` in33.911s; their original request parse and nat-cast elaboration
stops keep zero runtime credit (`compact-controls-v{1,2,3}` in the same directory).
The later812 terminal-seek harness correction changes no tested semantic input.
The final301 join over `ff1b7a888` preserves accepted property warnings318 and
passes strict initialization on `3b6a92f2f` in3.769s. Independent review found no
introduced runtime overlap; earlier source/state cuts retain their own inputs.
Current296 eval31/saved42 plus persistent wrong-id/valid/replay controls and
Stringable/Fiber chdir with73 owner/log/marker predicates keep their distinct cuts.
Earlier old290/v5 Generator/Fiber default227 remain accepted; new231 remain UNRUN.
The full retry original still times out at host55 with zero agreement. A bounded
trace completes throw/catch/new receive/bind before GC:293 completed GC transitions
take27.843s versus294 execution steps5.491s. The separate39 compute-once candidate
preserves pruning guards and partiality and passes strict301 initialization plus
GC42/Generator47/Fiber34 lifecycle predicates on `1060496af1`. Inputs stay stable
and all groups are reaped; raw records are under
`.tools/compiler-defaults-pruning-18/.tools/pruning-current-v1`.
Its unchanged full retry again times out at host55 with empty streams and zero
agreement. No speedup, whole-retry agreement or offline rebuild is claimed.
The actual305 join preserves collector317 and Generator321 and passes strict
initialization on `ad5acdc4d` in3.821s; earlier lifecycle/source cuts stay distinct.
The current301 diagnostic measures297 completed GC bodies27.988s, with pruning
alone26.283s (93.9%), then times out at host55 with zero agreement.
The private retained-node factor passes strict305 initialization, GC42/GEN63/Fiber34
and one parent-child WeakReference original on `67fa589eb`; exact public output
`P:live|C:null|N|END` completes in9.078s. Its full retry still times out at host55
with empty streams and zero agreement; this adds no demonstrated speedup.
The separate destructor preparation/waiting factor passes strict305 initialization,
110 source-reached/controlled branch and original-state fallback predicates plus
GEN63 on `5559f2c00`; the WeakReference original again agrees in9.078s. The selected
RHS Unmatch fallback is statically preserved. Its full retry still times out at
host55.066 with empty streams and zero agreement. The maintained
`destruction_prune_protocol.py` reproduces the corrected110 fixture; its original
relation-premise elaboration stop earns no runtime credit.
Both factors now join actual `bf1c0053a`/309, preserving current325/322/326/327
root and caller hooks. Strict initialization passes on `13bc4e931` in3.769s.
The earlier139/173/WeakReference cuts retain their own inputs; no source renewal
or speedup is claimed.
The nonempty zero-owner scan now computes its unchanged GC keep list once.
Private `7d0ed7543`/309 passes strict initialization, processed-DONE43 and
active-bare75 direct keep/retirement predicates, and the exact WeakReference
original in9.279s. Empty-scan and Unmatch/Runtime domains are statically reviewed.
Its full retry still times out at55.046 with empty streams and zero agreement;
inputs are stable and groups reaped, with no demonstrated speedup or231 credit.
The actual314 join preserves TRAIT290/297/299, CV330 and ARG329 handoff fields;
strict initialization passes on `1a148ff63` in3.871s. The309 cuts stay distinct.
The separate release-walk keep reuse passes strict314, DONE44/ACTIVE77 direct
walk predicates and the WeakReference original on `cd2f2a355`; its full retry
still hits55.065 with empty streams and zero agreement. Empty/HANDLE and fallback
domains are statically preserved, with no demonstrated speedup or231 credit.
The actual316 join retains332/333 roots/source fields and passes strict
initialization on `1e95f04a8` in3.870s; earlier314 runtime cuts stay distinct.
The per-node zero-scan factor binds each owner count once in the unchanged heap.
Private `8bbe41e3d`/316 passes strict initialization, DONE44/ACTIVE77, independent
35 graph premises and the exact WeakReference original in9.175s. The graph
fixture's initial parse stop keeps zero runtime credit. The full 1697-byte retry
still hits55.065 with empty streams and zero agreement; inputs stay stable and
groups are reaped. No speedup or231 credit follows. Raw records are under
`.tools/compiler-gc-zero-owners-18/.tools/gc-zero-owners-gate-v1/run-v{1,2}`.
The actual335-parent319 composition passes strict initialization on `3e56ab759`
in4.019s; earlier316 runtime cuts retain their identities.
Private `2582d7008`/319 partitions edge targets before source-membership scans,
passing strict initialization and 48 graph premises. Both factors compose over
SOURCE336/320 by static review. Actual `c38af3cf7`/320 full retry still hits 55.065
with empty streams and zero agreement; inputs stay stable and groups are reaped.
No speedup or 231 credit is claimed. Raw checks/retry stay under
`.tools/compiler-edge-owners-19/.tools/edge-owner-gate-v1` and
`.tools/compiler-gc-zero-owners-current-parent-19/.tools/full-default-retry-edge-v1`.
A zero-credit `c38af3cf7`/320 diagnostic identifies Fiber protection as the main
completed pruning cost. Module 302 now builds its graph at the first object and
reuses it within the unchanged state, preserving lazy empty/nonobject prefixes,
eager scan order and Unmatch fallbacks. Exact `181931c20`/321 passes strict
initialization, 22 controlled partiality premises and 65 source-reached
protected-result/lifecycle premises. Its original
full retry still times out at 55.066 with empty streams and zero agreement.
The first compiler stop and two malformed Runtime expectations (actual false)
remain preserved; Runtime propagation and eager evaluation of later nodes remain
statically reviewed.
Composition over `b7ed1bea1`/326 preserves SOURCE339, TRAIT307 and ARG334
by static review, without runtime renewal.
Raw records: `.tools/compiler-fiber-protection-graph-19/.tools`
(`fiber-protection-gate-v{1,2,3,4}` and `full-default-retry-protection-v1`).
Pruning now carries its graph through GC selection, Fiber protection and
destructor dispatch, retaining active and idle bare-root guards. Destructor
preparation reuses the graph only for identical states; changed states take the
original prepared-state path. Exact `74a8a11ca`/326 passes strict initialization
and 41 independent fixture premises. Its first destructor78 check exposed an existing
207 ordinary-handler/destructor validation overlap. The one-line fallback repair
at `039abc623`/326 passes changed initialization and four fixtures with 78 destructor,
69 protected Fiber, 40 active GC and 37 ordinary-handler domain premises.
The original full source still times out at host 55.066 with empty streams and
zero agreement; inputs are stable and groups reaped. No speedup or 231 credit follows.
Final 330-module composition at `5ca56cf55` mirrors the new idle retired-bucket guard
and passes changed initialization plus a genuine retirement fixture with 73 body /
190 physical premises. Earlier 326 cuts stay separate. Raw failures and checks remain
under `.tools/compiler-fiber-protection-current-19/.tools` (`prune-graph-controls-v{1,2,3}`
and `full-default-retry-prune-graph-v1`) and `.tools/compiler-prune-graph-publication-19/.tools/prune-graph-gen330-controls-v1`.
Known-current graph reuse now covers keep, zero and release scans, avoiding
rebuilding the graph inside bare/retired retention. Exact `c09806280`/330 passes
strict initialization, 52 independent premises and reached DONE51, bare62,
destructor82 and retired193 physical premises (38/50/76 body premises for
DONE/bare/retired). Public modified-graph helpers and changed-preparation paths
stay intact. Raw checks: `.tools/compiler-prune-graph-publication-19/.tools/prune-graph-keep-controls-v1`.
Final 334-module composition at `989e6bb09` passes changed initialization in
4.222s; its earlier 330 fixture identities stay separate. Raw final check:
`.tools/compiler-prune-keep-current-19/.tools/prune-keep-current-controls-v1`.
The unchanged 1697-byte original on `94e3593e6`/334 matches native output, while
the public model still reaches host55.045 with empty streams and zero agreement.
Inputs stay stable and the group is reaped; no speedup or 231 credit follows.
Raw retry: `.tools/compiler-prune-keep-current-19/.tools/full-default-retry-graph-keep-v1/run-v1`.
Module302 skips total graph owner scans only after evaluating a false close
predicate, retaining per-node fallback and eager recursive tail. Exact `7b02a1d39`/334
passes changed initialization, 44 independent physical/43 main helper premises
and a genuine suspended-ready Fiber frontier with 54 physical/41 main premises.
True branches are typed helper controls only; the source frontier proves false.
Raw checks: `.tools/compiler-fiber-blocked-scan-19/.tools/fiber-blocked-controls-v1`.
Final 336-module composition at `3f19f2278` passes changed initialization in4.122s.
Raw final check: `.tools/compiler-fiber-blocked-current-19/.tools/fiber-blocked-current-controls-v1`.
Its standalone original retry remains UNRUN; the combined result follows below.
Module301's removed-owner consumer now reads the same observed state's edges
after its first roots call, preserving owner order and fallback. Exact `c0cbdd69b`/336
passes initialization, 51 typed physical/44 main and 56 reached physical/39 main
premises, with explicit admission of the changed branch. Raw checks:
`.tools/compiler-gc-transition-edges-19/.tools/gc-observed-edges-controls-v1`.
Final 339-module composition at `a164f0f9e` passes changed initialization in4.171s.
Raw final check: `.tools/compiler-gc-transition-edges-current-19/.tools/gc-observed-edges-current-controls-v1`.
One combined302/301 original retry at `ea7cf0a34`/339 still reaches host55.045625
with empty streams and zero agreement. Inputs stay stable and the group is reaped;
no speedup or231 credit follows. Raw retry:
`.tools/compiler-gc-transition-edges-current-19/.tools/full-default-retry-gc-observed-edges-v1/run-v1`.
Module270's eager-slot consumer now reads same-state allocation edges after
its first roots call, preserving owner/live-slot/property-pending order and fallback.
Exact `6f16a3f11`/339 passes initialization, 68 typed physical/54 main premises
and a genuine main UNSET frontier with 52 physical/32 main premises, explicitly
admitting a nonempty CV-cell release. Raw checks:
`.tools/compiler-eager-observed-edges-19/.tools/eager-observed-edges-controls-v1`.
Final 340-module composition at `6c1a89b38` passes changed initialization in 4.270s.
Raw final check: `.tools/compiler-eager-observed-edges-current-19/.tools/eager-observed-edges-current-controls-v1`.
The `500a2cedc`/340 original retry matches native output but the public model
still reaches host 55.045470 with empty streams and zero agreement; inputs stay
stable and the group is reaped, with no speedup or 231 credit. Raw retry:
`.tools/compiler-eager-observed-edges-current-19/.tools/full-default-retry-eager-observed-edges-v1/run-v1`.
The driver now carries the successfully evaluated original-state eager owner
order into the following GC. Exact `8c889199c`/340 passes initialization, 66 typed
physical/52 main and 102 reached physical/82 main premises. The real empty-slot
STMT and later nonempty UNSET have an authenticated origin-entry step between them.
The declaration stop and original 98-premise task-assumption failure remain preserved failures.
Raw checks: `.tools/compiler-owner-order-carry-19/.tools/owner-order-carry-controls-v{1,2,3}`.
Final 343-module composition at `4a96bad9a` passes changed initialization in 4.320s.
Raw final check: `.tools/compiler-owner-order-carry-current-19/.tools/owner-order-carry-current-controls-v1`.
The `e1c3d4d61`/343 original retry matches native output but reaches host 55.043267
with empty streams and zero agreement. Inputs stay stable and the group is reaped;
no speedup or 231 credit follows. Raw retry:
`.tools/compiler-owner-order-carry-current-19/.tools/full-default-retry-owner-order-carry-v1/run-v1`.
Pure graph pruning now counts distinct node identities, root/edge multiplicities
and removes zero-owner cascades through a worklist. Final filtering preserves
roots and original node/edge order and duplicates, including arbitrary finite typed
graphs with dead sources or absent targets. Exact `a39876cbe`/343 passes strict
initialization in 4.273s, independent 54 physical/33 main premises comparing 512
graph variants in 4.472s, and 54 reached physical/44 main premises in 4.973s.
The real post-UNSET cell/object cascade requires successive old pruning rounds
and matches the new graph and public pruning results. Raw checks:
`.tools/compiler-heap-prune-worklist-19/.tools/heap-prune-worklist-controls-v1`.
Final 345-module composition at `8ed6d5bcb` passes changed initialization in 4.272s.
Raw final check: `.tools/compiler-heap-prune-worklist-current-19/.tools/heap-prune-worklist-current-controls-v1`.
The `9cacdbf51`/345 original retry matches native output but reaches host 55.044761
with empty streams and zero agreement; inputs stay stable and the group is reaped.
Raw retry: `.tools/compiler-heap-prune-worklist-current-19/.tools/full-default-retry-heap-prune-worklist-v1/run-v1`.
One current-public-path hook diagnostic reaches normal active-Fiber execution
with output through `H1|H2|X|H3|same:same:` before host 55.046281. Completed outer
allocation-edge calls total 17.202s; `heap_prune` totals 1.025s. These nested
observations include hook overhead and establish no speedup or source agreement.
Raw diagnostic: `.tools/compiler-heap-prune-worklist-current-19/.tools/current-public-phase-v1`.
GC now reuses pruning's already-built edges only when the full prepared/pruned
states are equal; changed states recompute, preserving owner/root order and fallback.
Exact `738d2a3b1`/345 passes initialization and 60 typed physical/47 main premises
in 4.222s each, plus 65 reached physical/57 main premises in 4.971s. The latter
admits real unchanged STMT GC and changed raw post-UNSET pruning. Its initial
blank-separator parse stop remains preserved, with zero runtime credit.
Raw checks: `.tools/compiler-pruned-edges-19/.tools/pruned-edges-controls-v{1,2}`.
Final 349-module composition at `9b69ebb2e` passes changed initialization in 4.323s.
Raw final check: `.tools/compiler-pruned-edges-current-19/.tools/pruned-edges-current-controls-v1`.
The exact 1697-byte original at `ea58ac361`/349 now agrees with native PHP in
54.832s at unchanged 45/55-second caps: normal, exit 0, exact 46-byte output and
empty stderr, with stable inputs and reaped groups. Earlier timeouts stay preserved.
Raw retry: `.tools/compiler-pruned-edges-current-19/.tools/full-default-retry-pruned-edges-v1/run-v1`.
The source and tuple are retained in `compiler_composed_retry_cases.json`, wired
through the existing runner into combined and offline checks; those runs remain pending.

Ordinary collection301 preserves potential-root order, discarded-temporary
decrements, parked handle authority, weak retirement, destructor guards and
frozen per-pass counts. Its original30/606 and private285-parent3/45 retain their
recorded cuts. The actual286-parent composition passes strict compilation and
initialization, one exact captured-source retirement original and66 independent
strict-SL premises for genuine child6/main26 context, guard ownership, forged
plans/consumers and live-state resumption. The larger nested-Generator original
retains its90s timeout with zero agreement. Actual290-parent composition passes
strict291 compilation/initialization and one new exact readonly self-clone/GC
original: both real cycles are weakly observable until two destructors/count2,
then both retire and a second collection returns0. The
[ledger](coverage/semantics/cycle-collection-review.json) retains each distinct
cut. Module 317 adds the actual collector-Fiber cache,
global parked collection, detached target/pending guards, replacement batches,
source-less traces/scope and callbackless idle retirement. Thirteen exact normals
and two strict-SL groups with 78/68 premises pass at separate cuts with 292 modules.
The actual318 parent passes strict298 compilation/initialization and one fresh
reporting-Fiber/handler original, preserving global busy0 through nested callbacks,
mask restoration and real count1/weak retirement. The final304 additive join
preserves newer default-receive, Get/reference and literal-this source schemas
and passes the required combined compiler without source/state renewal.
The fresh explicit-INI source discriminates
cached mask reuse. The two larger 60s model timeouts retain zero agreement.
Module325 adds separately tested detached zero-owner retention, real reacquisition
and active unowned-close retirement. Wider internal graphs, callback reentry during
a different active pass, internal takeover, automatic thresholds, resurrection and final
request freeing remain required.

Undefined source operands293 resume genuine warnings with fixed null after
handler writes, preserving direct empty-path errors and earlier computed-name
fetch timing. Borrowed/captured Stringable sources298 keep converted bytes and
real owners through cast destruction, compiler notices and parser/provider work.
Separate reviewed cuts cover compiler fast returns, delayed error-API checkpoints,
empty/once/failed helper results and authentic child/main retirement traces.
[Undefined](coverage/semantics/source-undefined-review.json),
[lifetime](coverage/semantics/source-stringable-review.json),
[ordering](coverage/semantics/source-stringable-ordering-review.json),
[helper](coverage/semantics/source-stringable-helper-review.json) and
[retirement](coverage/semantics/source-stringable-retirement-review.json) ledgers
preserve every original cut and failure. The separate
[first-work extension](coverage/semantics/source-stringable-first-work-review.json)
adds constant ECHO and assignment to a literal variable name opcode lines: three original
source agreements and 46 reached entry premises retain their accepted private cut.
[Nonconstant emission314](coverage/semantics/source-expression-emission-review.json) adds ordinary CV ECHO, literal property FETCH and no-argument named-call INIT lines. Its private277 source3/entry57/guards72 retain their original inputs and two zero-credit fixture stops. Actual286 passes strict compilation, one fresh nested-Generator captured-source original and independent70 entry/retirement/public/heap/image premises. The relocated maintained case prepares70 with zero applications. Broader producers, first emissions, checkpoints and providers remain required.
The [composition ledger](coverage/semantics/include-source-composition-review.json)
records genuine child line5/main keyword21, retained captured input after alias
clearing, the saved Generator caller and public/heap owner/suffix controls. The
maintained relocated fixture prepares 49 premises with zero runtime applications.

[Auto-global emission316](coverage/semantics/source-autoglobal-emission-review.json)
selects literal FETCH_R5 before ECHO or property6. Its isolated278 cut passes
strict compilation, two exact explicit-request originals, independent79 MAIN
entry/first-destructor/source/image premises, computed-name11 and new maintained72
classification premises. The omitted-request Unsupported, request-literal fixture
stop and copied Generator-owner false fixture retain zero accepted credit.
A separate cc397-parent291 join passes strict compilation, one genuine readonly
clone-owned include original and independent64 entry/first-destructor premises,
including maker-site and receiver-line counterexamples. Its two maintained
relocations gain no refreshed execution credit. The actual292-parent join passes
strict293 initialization, the same exact original and independent47 source/GC/public
premises, including a heap-identical forged NOGC receipt. Earlier cuts retain
their own inputs; wider emissions remain required.

[Literal GLOBALS emission320](coverage/semantics/source-globals-emission-review.json)
is integrated: FETCH5 precedes later direct Array Warning5 or property-on-array
Warning6; parenthesized entry retains FETCH6/property8 and snapshot timing.
Private294 source4/67 premises retain their inputs. Actual296 passes strict
compilation with reviewed Arrow/Fiber compatibility and no renewed source/state
credit. Relocations add no execution credit; broader first emissions remain required.

[Literal this emission323](coverage/semantics/source-this-emission-review.json)
is integrated: FETCH5 precedes child work or the later
missing-instance Error5, while a method include retains its receiver/private scope.
Private297 retains four exact originals,70 independent premises and9 affected guard
checks; the initial INSTANCE fixture false has zero accepted credit. Actual303
passes strict compilation with reviewed property/default/argument compatibility.
Relocations and the actual join add no source/state credit; broader emissions remain required.

[Computed-name emission327](coverage/semantics/source-computed-emission-review.json)
is integrated: an owned operand retires at INIT6 before
the resolved no-argument helper and later FETCH6/property8 execute. Three exact originals
retain their first cut; the corrected missing-name original passes separately.
The new warning producer resumes with null after handler writes, with188 independent
entry/admission/pending-handler premises. Original Unsupported and two fixture
stops retain zero affected credit. Actual307 passes strict compilation with reviewed
collector/Generator/ArrayAccess compatibility; broader names remain required.

[CV-computed name emission330](coverage/semantics/source-cv-name-emission-review.json)
is integrated: compiling the ordinary name CV emits no opcode,
and outer FETCH6 precedes property8 after operand retirement. Four exact originals
show the live name changes before lookup; a missing target resumes null after handler
name/target writes. Genuine entry/warning/identity controls pass174 premises.
Actual310 passes strict compilation with reviewed Fiber/collector/constructor compatibility.
Earlier cuts and relocations gain no renewed credit; broader names remain required.

[One-argument computed-name emission333](coverage/semantics/source-call-argument-emission-review.json)
is integrated: operand retirement uses INIT6 before argument lookup,
and outer FETCH7 precedes property10. Five exact originals and275 independent
entry/warning/identity/admission premises retain live CV reads and handler writes
with fixed-null argument/target resumes. The parser stop and incorrect CODEARG
origin mismatch have zero affected credit. Actual316 passes strict compilation
with reviewed trait/ArrayAccess/collector compatibility; earlier noarg/CV cuts
and relocations gain no renewed credit.

Generator289 now delegates arrays, source Iterators and shared/nested Generators,
preserving raw caches, input forwarding, actual callback demand and return transfer.
The accepted private52 normal/four compiler agreements and618 reached premises,
plus the distinct actual274 source/87-premise cut, retain their original inputs.
Canonical integration preserves newer ArrayAccess/Fiber/call fields; introduced
composition checks pass with303/310. IteratorAggregate, wider reference-yield forms and
wider lifecycle/API behavior remain required. [Scope and retained evidence](docs/semantics/GENERATOR-DELEGATION.md).

Generator303 now runs ordinary last-owner finalizers, releasing delegation links
before finally and retaining authentic frame, scope, cursor and cached owners
through ordered storage cleanup. Its private 40 normal/two compiler agreements
and 569 reached premises across eight programs/eleven groups retain separate
original cuts. Canonical integration preserves the installed eager-destruction
and Fiber clauses. The actual eager-release bridge retains pending exceptions
and remaining slots through authentic closing-frame restoration. Request-end,
terminal, GC and user-destructor paths remain required.
[Scope and retained evidence](docs/semantics/GENERATOR-FORCE-CLOSE.md).

Generator310 permits ordinary paused-Generator last-owner close inside an active
Fiber, preserving current identity, parked callers and genuine frame/cache owners.
Its accepted private 26 normal sources and eight strict-SL programs/groups with
669 reached physical premises retain their original cuts; four precise required
Unsupported controls earn zero agreement. The actual282 composition passes a
strict compiler cut, five distinct new normal sources, two promoted close sources
and one precise request-end control. One new strict-SL program/group passes189
reached premises for pending frame release, remaining owners, the previous chain
and live-state budget resumption. Private cuts retain their original identities;
the two source discrepancies and stale fixture elaboration failure retain zero
credit in the existing ledger. Parked running Generators, switching
finalizers, request/terminal cleanup, GC and general user destructors remain open.
[Scope and retained evidence](docs/semantics/GENERATOR-FIBER-CLOSE.md).

Integrated module 308 extends force-close of captured cleanup
after an actual callback return: private previous ownership, source-less deprecation, restored reporting
and shared handler registration. With its captured producer payload unchanged,
a nonowning protected pair rejects another older Throwable substituted as the child. The fixed 277 module cut passes AL,
fourteen distinct normal source comparisons and two precise Unsupported controls
with zero agreement. Three authored groups/227 conditions and eleven independent
groups/860 conditions pass, along with two affected existing schema groups.
Composition over the integrated 291/302 parent `9dd9ca8b3` passes strict-SL 280
initialization, one exact defined-result original and two reached strict-SL
groups/113 premises. The final GEN/include parent `ed7f23c67` composition passes
strict-SL 285 initialization, the same exact original and two groups/113 premises
on tested transfer `68b9ec4c4`. Earlier cuts retain their own evidence.
The original verbose-source timeout retains zero agreement. CALLS308's dynamic
property warning retains Unsupported at its original cut; no result is renewed.
Undefined-result engine verification remains held.

Ordinary eager destruction270 releases consumed slots in native order, retaining
pending owners through callbacks, throws and resurrection. MAIN preserves source
permission and catch/trace behavior; used results, borrowed CV receivers and
cold/warm property RHS temporaries retain their native lifetimes. Handler returns
and the original Throwable release before handler restoration and queue entry;
fatal diagnostics freeze before release, while bailout retains real VM and C
owners. Author62 and independent60 exact sources, nineteen reached cases/1,012
assertions and the separate fatal/actual-parent cuts retain their recorded inputs
in the [ledger](coverage/semantics/eager-destructors-review.json). The actual Array
warning/cleanup original now agrees and rejects a forged source-marker suffix.
The [contract](docs/semantics/SOURCE-EAGER-DESTRUCTORS.md) keeps compound
Stringable reception, GC, wider weak protocols, output buffers
and later freeing open. Actual 292/304 composition passes strict-SL initialization
and one new exact returned-object lifetime source at276, with stable inputs;
earlier cuts gain no renewed execution credit. The separately reviewed shared
cleanup bridge authenticates helper producers in the saved caller and binds the
internal destructor frame site. One strict-SL reached277 cut passes19 physical
premises for authentic entry, a heap-identical site/line forgery and zero/one-step
resumption; the oversized62/41 cuts timed out and remain unconfirmed.

WeakReference296 memoizes allocated wrappers using nonowning immutable semantic
target IDs. `get` copies a live target into a genuine strong result; destructor
resurrection stays live, while actual free clears weak lookup before child
retirement. Forbidden direct NEW preserves genuine pre-argument candidates and
validated parked stacks. Twenty-one exact originals and nine reached cuts/344
physical premises retain their private275 inputs in the
[ledger](coverage/semantics/weak-reference-review.json); five Unsupported controls
earn zero agreement. The [contract](docs/semantics/WEAK-REFERENCES.md) keeps
pending-carrier unwind, deferred construction, wider consumers, GC and wider
WeakMap protocols open. Actual292/304/270 composition passes strict277 initialization
and one new exact weak lifetime original, with stable inputs and separate recorded cuts.

WeakMap386 now admits one first entry with a nonowning `stdClass` leaf key and
strong ordinary leaf value. Key notification replaces the map edge with an
authentic VALUE release before the value callback, preserving the key storage pin.
Actual wrapper identity at insertion distinguishes early-null from late-live
callback reads; borrowed pin NOTIFY survives normal and throwing cleanup without
adding ownership. Three originals agree with PHP at `c1cf6c7`; four reached cuts
pass 393 checks for GET ownership, notification timing and physical key retirement,
stopping at the scheduled HANDLE release. The initial 45-byte agreement and
375 lifetime plus 49 GC-refusal checks retain their original cuts; the old
116-check notification refusal is historical and superseded by the 106-check
late GET case. Last-owner map teardown now detaches its value into a real VALUE
release while a live leaf-key CV survives. The emptied map stays pinned and
weak-live through normal or throwing value cleanup, then notifies before physical
retirement. The normal 81-byte and throwing 88-byte originals agree at `0c9b358`;
161 retention checks pass there. Callback GET (97 checks), normal pin (105), throwing
pin (104) and 86 freeing-write refusal checks pass at `061e372`, totaling 553. Pin cuts stop at the scheduled HANDLE release; originals supply full
endings. Wider maps, wrapper creation or mutation during freeing, additional key/map
owners retained beyond callback cleanup and ephemeron collection remain required.
Earlier failures retain zero credit.

Supported scalar values now pass the existing nonempty Map free admission
under real eager destructor machinery. The old object-value predicates and all
current-release/zero-owner/BEFORE/held leaf Key checks remain unchanged. Scalars
create no Value jobs; an authentic empty release precedes the ordinary Map pin,
then notification, physical retirement and handle release preserve Key/Sentinel
owners. Plain map-first already agrees (40 bytes) at `b88b45fc` through unchanged
leaf pruning. A held unrelated destructor activates the previously refused path;
its 42-byte original and 160/100 reached checks (260) pass at `f68c6f09`. Checks
stop after actual handle release; full sources supply later Key/Sentinel cleanup.
Key-first remains a separate native-only observation. The active-context
Unsupported stays zero, with no old test supersession or collector/root change.
Wider scalar replacement and lifetime protocols remain required.
[Ledger](coverage/semantics/weak-map-review.json).

Two singleton maps sharing one leaf Key now admit a wrapper between their entry
registrations. BEFORE identities select the earlier entry independently of map
allocation order, and only that value edge transfers during its callback. One
Key pin clears notification before scheduling the later value release; a valid
heap with a forged empty BEFORE cannot reopen GET. The normal 93-byte original
agrees at `e5b19d0`; the throwing 100-byte original and 106 insertion, 99 transfer,
103 notification and 97 pending-Exception checks pass at `b12f93a`, totaling 405.
The shared-Value redirect with unused Second held is a coherent counterfactual;
other cuts are source-reached and stop at insertion or scheduled VALUE releases.
Originals supply endings. The original Unsupported and duplicate-schema compiler
wrapper failure stay zero. General/equal-BEFORE registration order, wider maps,
freeing mutations/reads and escaped callback owners remain required.
[Ledger](coverage/semantics/weak-map-review.json).

Ordinary object-key reads now create a strong stored-value copy; its held CV
survives removal of the map edge and delays the value destructor. Missing keys
throw Error with the actual object-store handle while preserving the existing
entry. The 56-byte held-copy and 88-byte missing-key originals agree at `c4c097e`;
110 checks for the value copy, 74 for release with a held value and 113 for the
missing-key Error pass, totaling 297. The Error cut stops after real materialization;
originals supply catch and complete endings. The original 73-check owner forecast remains zero;
its corrected control authenticates the two real destructor-entry task roots.
Wider presence/reference/method and key/map protocols remain required.

Direct WeakMap `isset`/`empty` now uses stored null/truth with the existing
terminal test carrier, adding no Value owner. Empty singleton maps also accept
null/bool/int/valid string first values; source literals retain their exact
carrier via the source/precision-authenticated producer in module242. The object
87-byte original agrees at `144597d2`; the later literal arm is false for its
VARIABLE RHS. The scalar 180-byte original and 104/140/61/72 focused checks
(total 377) pass at `b7c1624a`. Coherent table substitutions retain the original
Value CV; current-source and literal-carrier forgeries refuse. Cuts stop at raw
test results or insertion; originals supply explicit scalar removal and endings.
The unchanged refusal, algorithmic binding diagnostic and first scalar refusal
remain zero. Methods, wider quiet/reference reads, nonobject/freeing keys, other values,
wider scalar replacement and teardown/map protocols remain required.
[Ledger](coverage/semantics/weak-map-review.json).

WeakMap quiet `KEY_IS` reads now return the stored pvalue directly or null for
missing keys, preserving the existing coalesce continuation. The object original
(61 bytes) proves a strong copied result, lazy RHS and copy-only survival after
entry removal; the scalar original (166 bytes) distinguishes null from every
non-null falsy value. Both agree at `df2997be`; 135 copy, 76 genuine missing and
68 fallback checks pass (279). The raw object read adds a third owner beside
CV+Map; coherent table controls retain the original CV. Checks end at raw reads
or genuine RHS scheduling; originals supply full removal/destructor endings.
The unchanged Unsupported remains zero. Explicit methods, `??=`, references,
freeing/nonobject keys, wider quiet protocols and wider scalar teardown remain
required. [Ledger](coverage/semantics/weak-map-review.json).

Reads during postponed Key notification now require the unique active stdClass
pin, its live allocated wrapper and its actual store handle. A later-entry read
creates a strong Value copy; a missing entry throws the handle-based Error while
the later edge stays intact. Notice clearing denies reads even with an extra Key
owner. The 111-byte normal and 162-byte caught-Error originals agree at
`2565d378`; copy (146), cleanup (65) and Error/search (98) checks total 309.
They stop at shared release, scheduled later VALUE or THROW_SEARCH; originals
supply endings. Both Unsupported attempts, the diagnostic tuple and failed
148/146 receiver forecasts retain zero credit. Inactive/wider freeing reads,
escaped targets and the other map protocols remain required.
[Ledger](coverage/semantics/weak-map-review.json).

Explicit object-key entry unset now clears only the map's value edge; existing
eager comparison transfers that owner into an authentic VALUE release. Missing
keys preserve the entry, and a held CV keeps the removed value live and uncalled.
The normal 62-byte, throwing 69-byte and held/missing 87-byte originals agree at
`0c01e5f`. Removal (136), missing no-op (100), held-value release (94) and corrected
pending-throw (88) checks total 418. Actual Value cleanup leaves the same Exception
owned until the UNSET operation transfers it to THROW_SEARCH. The original
plain-string message premise remains zero; its correction compares string bytes.
Wider map protocols and ephemeron collection remain open.
[Ledger](coverage/semantics/weak-map-review.json).

Occupied same-key replacement now preserves KEY/BEFORE and publishes the new
value before old cleanup. Existing ACCESS_RESUME retains only the receiver and
original operands; unused results avoid a copy, while used results read the
selected RHS value after cleanup. Five originals and 548 state checks pass at
`70bf0c4`.
An owned-key counterexample then grounds receiver-before-OP2 release order; its
original and 94 reached checks pass at `302b5c9`. The prior variable-key root list
remains literally [Map], preserving those cuts. Total 642 includes transfer,
same-value/shared release, reentrant result copies and pending-throw cleanup;
originals supply complete endings. The original paused-state fixture failure and
owned-key mismatch stay zero. Wider map/freeing/reference/iteration and ephemeron
protocols remain required.

Occupied replacement also accepts the existing bounded scalar family, reusing
the old/new value predicates without changing publication or cleanup. At
`5dd834c5`/391, two exact originals and 76/71 source-reached checks (147) pass.
The old destructor observes the captured scalar entry and changes its actual
RHS CV; the used result reads that changed CV afterward. Scalar-to-scalar
replacement schedules no old value job, and scalar-to-object publication/result
raises owners from 1 to 2 to 3. Checks stop at actual readback; originals supply
copy-only survival and final destruction. The unchanged Unsupported and initial
checkpoint seek failure stay zero. A dedicated maintained suite retains the
tested helpers; wider keys/values, freeing mutation and reference/method/iteration
protocols remain open. [Ledger](coverage/semantics/weak-map-review.json).

WeakReference creation during live map teardown now authenticates the exact
allocated wrapper found for a unique active empty-map pin. After ordinary old
wrapper retirement, creation appends a nonowning replacement and rebinds only
the saved pin's borrowed NOTIFY. The callback-local map copy is released before
return. Reuse/recreation originals (88/123 bytes) agree at `ac980b0`;
reuse (123), fresh creation (133) and notification retirement (77) checks total
333. The real
argument owner drops from three to two map owners; the pin cut stops at its
scheduled HANDLE release, with originals supplying endings. The original freeing-create
Unsupported retains zero agreement. Wider/nonmap freeing, inactive carriers
and retained strong targets remain required; prior cuts retain their evidence.
[Ledger](coverage/semantics/weak-map-review.json).

Destructor-free singleton WeakMap collection now separates conditional GC
tracing from physical value ownership. The value is inserted as a leaf before
its sole public key backedge is assigned. A live map keeps the value only when
the key is reachable; an external value owner also reaches that key. The unheld
pair expires with count two while the map survives. Held-key and held-value
passes each return zero. Two originals agree at `0167ec6c`; unheld (169), held-key
(135) and held-value (135) source-reached checks total 439. Actual GC_FREE clears
the dead entry before the unchanged strong resurrection guard and ordinary
counted/store/handle disposal. Checks stop at the collection return; originals
supply later teardown. The original nonempty-map Unsupported stays zero.
Wider maps/destructor callbacks, inactive contexts and general ephemeron graphs
remain required. [Ledger](coverage/semantics/weak-map-review.json).

Singleton ephemeron collection now admits one source-backed public value
destructor. Existing GC protects Value and Key through the first callback and
retraces current roots afterward: observer-only cleanup collects two nodes;
saved Key protects both, then later collection disposes them without a second
destructor. A separately rooted `stdClass` leaf is preserved; wider changed
shapes stop at the real GC_TRACE boundary. Three originals agree at `18a03e08`;
128 entry, 136 retrace, 165 saved-Key and 154 outside-leaf checks total 583.
The saved-Key stage is source-reached; its root-drop check is a coherent
counterfactual. Checks stop at destructor entry or collection return; originals
supply endings. The original Unsupported, initial-state arity and reach-order
fixture failures retain zero credit. Wider methods, graphs and contexts remain
required. [Ledger](coverage/semantics/weak-map-review.json).

Methodless singleton ephemerons now compose with allocated, nonfreeing ordinary
`stdClass` graphs. Only module386 admission changes; physical edges and
collector301 remain unchanged. Two originals agree at `fa2e00c6`: an independent self-cycle
collects with the unheld pair (3), or alone while Key is held (1), followed by
pair collection (2). Source-reached unheld (150), held (207) and destructor-boundary
(48) checks total 405. Rerooting the real Key CV to Other and then routing Other→Key
are coherent counterfactuals, with fresh plans 2/0. That cut retains its historical destructor/nonleaf
refusal. Checks stop at GC return, plan or refusal; originals supply
endings. The original Unsupported and pre-reroot-edge fixture failure stay zero.
Wider value classes, maps and contexts remain open.
[Ledger](coverage/semantics/weak-map-review.json).

Already-called value destructors now admit ordinary outside `stdClass` graphs
through a single module386 premise;301 and physical ownership remain unchanged. Two
180-byte originals agree at `c3e844a5`: independent Other.self survives pair collection (2), while Other→Key protects the pair (0); dropping Other then collects
1 or 3 respectively, without a second destructor. Source-reached 149/182 checks
total 331, including coherent real-CV root drop and stale-plan rejection. Cleared
CALLED history tests helper/shape denial only, with no valid-continuation claim.
The obsolete active 48-check record and old 154-check case's final 11 negative clauses are superseded;
the 143-check positive prefix and historical ledger/Git results remain. Checks end at
GC return; originals supply endings. Unsupported/CLI60/numeric120 failures stay
zero. Maintained source caps (120 seconds) and final state cap (160 seconds) match accepted runs.
[Ledger](coverage/semantics/weak-map-review.json).

ArrayAccess304 reconstructs intermediate `[]` after ordinary by-value Get and
supports final compound append, including null-key Get/Set on returned children.
Returned temporary arrays extract selected rows before retirement; copied real
cells detach or remain shared according to their actual owners. False-conversion
throws preserve the same-opcode append/write/operator priority, conversion
checkpoints, callback eligibility and complete previous chain. Dimension records
require a real key expression, keeping `[]` distinct from `[null]` at public
admission. Forty-nine normal sources agree across retained cuts; eight genuine
strict-SL recipes with 723 premises pass. One fresh interaction at
actual 38f + accepted 292 + 304 / 275 agrees through include conversion,
private Owner/Child selection, GLOBALS
reference rebinding and a retained-cell append. The
[append ledger](coverage/semantics/arrayaccess-append-review.json) keeps cuts and
original failures separate. Final simple returned-child append309 is installed;
its private276 and actual278 cuts remain independently accepted. The current287 composition keeps
the canonical Generator/Fiber/source fields; clean718b passes full compilation,
one new exact Fiber Set/paused-Generator finalizer original and64 strict-SL
premises. The actual291 bridge overcc397 keeps PROP call/cleanup schemas and
also matches the same original;64 retains its287 cut. Independent review accepts
these separate gates. Canonical292 over2a2 preserves HANDLE/TEMP/NOGC
and301 and passes full compilation plus one new exact cyclic-child original:
Set collects an unrelated cycle, readback returns old CELL25 after global
rebinding to31, and later collection frees the returned child/count1.
The [returned-child ledger](coverage/semantics/arrayaccess-returned-append-review.json)
preserves eight sources/160 premises, separate lifetime/provider/compiler/warning
cuts and zero-credit original failures. Wider producers, remaining reference-Get consumers and
complete core remain open; paused return verification stays separate.

ArrayAccess319 adds accepted untyped/mixed by-reference Get: implicit
callbacks demand their real result, R/IS dereference it, writable shared cells
stay shared, and a genuine sole wrapper moves before receiver release. Direct
DIM_OP owns the raw reference through Set without retaining its old referent.
Final nested reference acquisition and borrowed Unset source prefixes preserve
parent release and callback retirement. Fourteen normal originals agree across
explicit cuts; six strict-SL recipes/375 premises cover demand, wrapper move,
sharing, raw compound/throw cleanup, captured rows and retired-parent Unset.
The [reference-Get ledger](coverage/semantics/arrayaccess-reference-get-review.json)
keeps source, reached, compiler and original failures separate. Actual298 over
ff1b passes full compilation, strict initialization and one new exact original:
a genuine Fiber reporting warning handler suspends inside Get, then resumes
the shared property CELL write while restoring main reporting. Parent318 fields
are preserved; this source makes no dynamic-property runtime claim. Final302
over b135 preserves new default receive fields and passes full algorithmic and
structuring compilation. Module326 adds named sends and nested captured-row
updates below;329 adds VALUE-return Notice callbacks. Wider producers remain required;
typed non-mixed return verification stays user-paused.

Integrated ArrayAccess326 admits captured live ELEMENT rows for named reference
sends and nested pre/post updates. Exact source/writer/RHS/temp guards preserve
name-check priority and existing finishing dispatch. Six new exact normal
originals and three genuine strict-SL groups/246 premises cover named promotion,
duplicate rejection before promotion, copy/shared-cell behavior and resumption.
The [consumer ledger](coverage/semantics/arrayaccess-reference-consumers-review.json)
keeps this303 cut separate. Final306 over `40e3c4fcc` passes full algorithmic
and structuring compilation at `46c624e89`; independent seam review requires no
source/state renewal. Module329 adds VALUE-return Notice callbacks below;
wider Get behavior remains open. Typed non-mixed
return verification stays user-paused.

ArrayAccess329 stages the RETURN_REF_VALUE Notice for genuine untyped/mixed
reference Get. The computed operand survives ordinary handler return, throw or
Fiber suspension without a pre-Notice cell write or saved referent owner. Throw
materialization bypasses Get's inner catch, retains the real RV through local
release, then transfers its owner after the caller's access owner so the receiver
retires before the returned value. Nine new exact normal originals and four
genuine strict-SL groups/401 premises pass at `13e29b78d`/307. The
[producer ledger](coverage/semantics/arrayaccess-reference-value-review.json)
preserves both compiler-only failures and the corrected native rebind forecast.
Final314 over `2a2f69a71` passes full algorithmic/structuring compilation at
`e87987ebc`, preserving current trait, constructor and pruning fields. The
earlier307 source/reached cut remains separate. Finally-sensitive Notice ingress,
bare/fall-through NULL, handler exit and wider producers remain open; typed
non-mixed return verification stays user-paused.

ArrayAccess334 stages real Get, left Stringable conversion, live RHS conversion
and Set while retaining the raw RV/CELL and each genuine cast/key/base owner.
An initially defined key unset by a conversion retains its absent C-call slot:
required and variadic Set reject before entry, while scalar and NEW defaults use
real receives and argument introspection. Twenty-three normal originals agree
across `1a9577fbc`, `e24bc593f`, `44e1bf990` and `e79ff62bd`; three compiler
rejections pass separately at `1a659fe82`. The
[compound ledger](coverage/semantics/arrayaccess-stringable-compound-review.json)
keeps 341 earlier and 248 missing-key reached premises at their separate cuts.
The composition of 325 modules over SOURCE339 `3691db3dd` passes full
algorithmic/structuring compilation and six strict initialization checks at
`7a7dd4faf`, without source/state renewal.
The final composition of 326 modules over TRAIT307 `55c2eab0c` preserves its
TYPE/default/FCC source guards by independent pointwise review; the 325-module
compiler cut remains separate.
The ordinary helper-base compiler repair preserves special builtin temporary
rejection. The deferred Generator Get control at this334 cut remains zero-credit;
module344 below records the later repair. Bare/fall-through NULL, finally-sensitive
Notice ingress and wider
producers remain open; non-mixed typed return verification remains user-paused.

ArrayAccess344 creates mixed/untyped implicit Generator Get results without
starting their body, including reference-yield declarations. A nonowning
TARGET/SITE/LINE certificate preserves exact Get scope after its emitter returns;
actual frames and received arguments retain every heap owner. Ordinary last-owner
close reaches the real caller carrier through an authenticated finished marker,
including destructor replacement of a pending finally exception. Seven maintained
normal originals pass across `dc27aa3e1`, `09ec7db36` and `3ff67878e`; the unchanged
334 Unsupported original has a separate new positive cut. Full327 compilation and
six initialization premises pass at `09ec7db36`. Independent423 reached premises
pass at `4e3062ac4`; actual331 algo/struct and initialization over `d811717a0`
pass separately at `f2d3c6d29`, with reviewed request/name/graph-carry interactions.
No earlier334 evidence is renewed.
Typed non-mixed producers and the other paused return lanes remain unchanged.

ArrayAccess292 now handles ordinary by-value compound Get/operator/Set and
writable Get temporaries through nested W/RW/Unset, pre/post updates and by-value
reference consumers. Defined key/RHS CVs remain live across compound Get;
computed RHS precedes queued Get/Notice and delayed CV demand follows Notice.
Returning arrays preserve real-cell edges while ordinary copies stay detached;
returned objects skip Notice, and thrown Notice suppresses later work. Direct compound Get throws
retain the replacement Error's opcode line and original previous chain. The
exposed276 direct GLOBALS reference finish preserves selected names/global
routing/owners;249 direct Unset admission now excludes255 nested paths.
Thirty-four distinct normal sources agree across retained cuts. Author 223 and
independent 793 premises pass across 13 recipes (1016 total), with 634 in AL and
382 in strict SL.
The [writable ledger](coverage/semantics/arrayaccess-write-review.json) records
actual revision/diffs, original failures and excluded count-observer0; its
core-language companion agrees. Remaining reference-Get consumers,
wider memoized/property/GLOBALS producers and combined interface notice ordering
remain required. Paused return validation remains separate. One fresh source at
actual 38f + 292 / 274 agrees through array-include conversion287, private
Owner/Child warning selection and live GLOBALS RHS rebinding; algorithmic,
structuring and loader checks pass. The original missing-provider input failure
retains zero agreement.
Private multiple-frontier defaults312 retain genuine handler/eval cuts for each
source effect, exact intermediate read prefixes, partial FCC-cache retry and
nested warming. Eight exact normals pass across retained cold v1 and seven v3
sources; native seven preliminary plus minimized warm v3 preserve exact tuples.
Strict277 at v2 and all eight genuine state groups/761 premises at v3 pass.
The two original warm host55 timeouts and actual all-true bind diagnostic retain
zero agreement credit. Catalogue133 preserves prior125. Current306 dispatch
delegates only its old two-frontier boundary to312; archival data stays unchanged.
The [ledger](coverage/semantics/deferred-static-defaults-review.json) records cuts.
Independent review accepts the bounded milestone; canonical integration is pending.
No actor or canonical writer is held.
Parked Fibers, object/null-key/outside-eval and wider producers remain required.

Private parameter alias causality306 preserves callback reads, retries, nested
reentry and captured deprecated values through dense nonowning receive births
and source-derived parent/frontier/eval cuts. Ten exact normal originals pass
across v9/v10. Strict SL276, all15 genuine state groups/1170 premises and the
37-check reporting interface pass on distinct cuts: prefix134 at v10, five555
at v11 and nine481 at v13. At that cut five controls rejected multiemitter,
parked Fiber, object/null-key and outside-eval routes with zero native agreement;
312 above supplies the bounded multiemitter paths. Catalogue125 preserves prior115.
The [ledger](coverage/semantics/deferred-static-defaults-review.json) retains
original failures, runtime identities and concise recovery. Independent review
accepts this bounded increment; canonical integration is pending. No numeric
actor or writer lease is held.

Private parameter aliases295 preserve borrowed global/cached class-constant
Closure identity, statics and donor body permission without adding owners.
Direct mixed-array defaults and selected compiled ternaries now have genuine
source/state witnesses. Eight normal originals and640 reached checks over14
originals pass on the dirty d39d cut:367 AL plus273 strict SL at identical120s
caps. Six historical effectful/object boundaries rejected explicitly and earned
zero native agreement. The unchanged private42 passes SL after its retained AL timeout.
[The ledger](coverage/semantics/deferred-static-defaults-review.json) binds actual
module/runtime hashes and distinct failed/corrected cuts. Global alias admission
is bounded to callback-free initializers and quiet values/facts. The306 slice
above adds bounded effectful read/registration causality;312 adds bounded multiple
emitters. Suspended Fibers and wider producers remain open. Historical
catalogue115 and protocol sources retain exact native bytes. Canonical
integration is pending.

Private parameter callable defaults286 allocate fresh static/no-use Closures and
fixed FCCs from genuine deferred `NParam` receives. REAL scope follows the
receiving lexical class; physical FCC targets stay cached while called classes
remain fresh. Immutable nonowning unscoped evidence survives maker retirement;
plain clones retain earlier permission without acquiring receipts. Nine normal
and two compiler originals pass at0f90; two new originals and one affected replay
pass atd39d. Earlier mixed342 and affected/new162 state premises retain distinct
cuts, including retired rebound-maker and coherent wrapper-erasure controls.
The separate actual285 Closure-body autoload source passes atd39d: private
constructor access rejects before nested argument effects. All274 production
modules pass the public SL path. The [ledger](coverage/semantics/deferred-static-defaults-review.json)
preserves original failures and the wider producer obligations beyond295.
Independent review accepts these gates; Canonical integration is pending.

The integrated dynamic/FCC clone maker follow-on was validated from frozen305
commit367e581df. Live clone calls capture the selected name before arguments;
cached makers retain only their own site, selected name or immutable intrinsic
Closure identity. An immediate genuine callback marker admits computed selectors;
the source-selection alternatives remain disjoint. Nonowning consumer birth keys
distinguish later activations through real Fiber identity, shutdown position and
autoload candidate identity.
Independent autoload bucket and selected-call stamps survive registry movement
and removal, including retained declaration history. Scoped autoload callbacks
use their retained producer source rather than replaying ordinary invocation.
Independent review, production SL277/application0, 20 distinct lifetime/manual,
pipe, argument mutation, autoload and shutdown originals, and 665 clauses across
seven reached-state groups pass at recorded cuts; three affected source repeats
are separate. Maintained builders recreate nine checked programs with exact
accepted clause/prefix parity; preparation adds no model credit. Coherent
pending-candidate identity rewrites remain an admission boundary. The
[selection ledger](coverage/semantics/readonly-clone-selection-review.json)
preserves original failures, scoped repairs and regeneration commands.
Accepted305 semantic inputs and all earlier cuts remain unchanged. Its directly
affected private shutdown companion now agrees exactly at367e581df and is
published at a2cab39d0. Its preserved CALLS308 warning original retains its
historical Unsupported cut with zero agreement.

Ordinary dynamic-property creation318 now resumes eligible callbacks for literal
simple assignments. The real warning owner protects the destination, then its
retirement decision survives destructor resurrection. Late plain CVs, old
reference payloads and owned RHS temporaries retain distinct behavior; same-key
reentry appends physical buckets with latest lookup and ordered value foreach.
Unused results release before receiver cleanup, while used results retain a copy.
Fifteen private exact normals retain separate cuts; initial 297, changed 498 and
cleanup 98 reached premises are not one campaign. The 297-module composition at
`078ecb2f8` passes strict initialization, one new exact GC/resurrection source and 69/98
GC/cleanup premises. At that cut, four explicit Unsupported boundaries cover handler exit,
duplicate casts/reference foreach and expired or undefined RHS pointers.
Computed names, wider writes and full-family closure remain required. The
[review](coverage/semantics/dynamic-property-warning-review.json) retains original
failures, commands and cuts; no historical clone campaign is renewed.

Physical duplicate-property reference foreach324 now selects and promotes the
actual bucket, preserving latest named access and declared readonly/type checks.
Staged own-destructor previous-CV cleanup keeps its raw value readable while live,
masks its released edge and installs the selected reference before normal/throw continuation. The
real shared receiver cell survives unset/recreate and follows alias writes, table
replacement and object/array/scalar dispatch; late scalar warnings retain that
owner until normal or abrupt iterator removal. Initial12 normals and288 reached
premises retain their earlier cuts. The shared-receiver extension has12 additional
exact normals at separate cuts, strict SL298 initialization and491 affected
premises at87f9b399a. The actual318 join at `f643ed070` passes strict
initialization and 92 fresh GC/saved-COMMIT premises; one separately tested
original collects during the previous CV destructor with exact normal output.
The331 schema/FCC seam is independently reviewed; earlier cuts keep their inputs.
HOBJECT-owner forgeries fail public reference-foreach admission. Previous plain-CV
array retirement now stages ordinary child destructors in physical order,
including nested arrays and continuation after
a child throws. Six new exact normals at `ccafc5d65` and 139/145 reached premises
at fixture-corrected `368bed28a` cover surviving array/reference owners, selected
property mutation/deletion and B/previous=A exception chaining; strict318 initialization
and the actual321 join at `be7edc9e2` pass. Ordinary prior-CV objects without their
own destructor now release dynamic children before declared children. Four exact
originals and 152/161 reached premises at `531145bb4` cover shared owners, retired
OLD masking and atomic binding with B/previous=A. At `95899634d`, strict initialization
and 19 fresh guard premises pass; two native observations retain explicit Unsupported
and zero agreement for direct/nested retiring typed sources at that cut.
Module346 now keeps each typed source until its actual declared-slot release visit,
including parked Fiber queues, without retaining the retired parent. Six normal
originals at `77a17756c`, 151 reached premises at `cc326bf43` and 84 Fiber premises
at `7573d02bb` retain separate cuts. They cover declaration order, two sources on
one cell, pending exception chaining, exact detach ownership and resumed scoped
Throwable validation against the actual live heap. The actual332 join at
`108d07bb5` passes strict initialization. Private Generator-close queues now
retain the same per-slot constraints without retaining the retired parent. Four
exact normal originals and strict332 initialization pass at `5b26e3526`; 134/71
reached premises at `edf7e7ec1` cover exact detach, ordinary cell-release transfer,
pending A/B chains and genuine parked/restored Fiber ownership. The actual336
join at `0d233dde9` passes strict initialization; earlier behavioral cuts remain
separate. Borrowed plan snapshots and duplicate queues provide no authority.
Last-owner previous reference wrappers now retire on the actual eager cleanup
queue. A separate nonowning raw CV preserves safe own-destructor reads while the
original wrapper reaches zero owners; normal/throw binding installs the selected
reference atomically. Five exact originals pass at `329ec8e38`; independent
native-first observations retain `f84fdab9d`. At `d3688fdf9`, 136/139 reached
premises cover genuine wrapper release, masked raw storage, pending A/B chaining
and refusal of whole `$GLOBALS` snapshots or expired borrowed-reference reads.
Shared wrappers and surviving payloads decline this staged path. Earlier source,
compiler and state cuts remain separate. The actual341 join over `6848742a2`
passes strict initialization at `ecd8e8745`.
Ordinary INSTANCE free_obj now retains one physical parent pin while visiting
property slots in release order; this supersedes immediate physical retirement
in the ordinary descendant path. WeakReference is already null during children,
while safe class metadata remains readable. Five exact originals pass at
`56b323d89`; separate Weak/get repairs pass affected2 at `99e3902c6`, and physical
GC-slot occupancy passes affected1 plus strict346 at `d91ef1ea4`. Three fresh
groups pass 164/57/67 premises at that latter cut, covering exact typed detach,
A/B chaining, actual355 RETURN-child ownership and genuine parked Fiber pins.
Adapted earlier ordinary fixtures carry no new credit; direct private303 physical
storage pins and wider raw-payload/escape behavior remain required.
The 347-module join over `cd7d74529` passes strict initialization and one exact
Iterator-child original at `5916e0e0b`. Its 113 shared premises at `9d007c3d4`
preserve live Weak-result ownership of 2 and future-tail ownership of 1 after genuine
destructor-result discard; added owners still reject queued close. The original
shared failure/timeouts remain uncredited; prior359/360 campaigns are unchanged.
Ordinary stdClass storage now uses the physical parent pin. Materialized tables
transfer one HARRAY edge before real bucket cleanup; shared-table children survive
parent retirement. Five exact originals pass at `c7e984676`; the disjoint dynamic
tombstone validator repair passes affected2 and strict347 at `f064fd2c6`.
New reached groups pass150/91/51 premises at `f064fd2c6`/`56d3b070b`/`2282b68da`,
covering table ownership, B-before-A throws, early Weak and actual355 RETURN storage.
Original baseline/fixture failures retain zero credit; prior campaigns are unchanged.
The actual349 join over `013ca6d2b` passes strict initialization at `e7e74c6c9`.
Unvisited initialized declared scalar reads now preserve ordinary visibility and
use the current DIRECT/ALIAS value under the actual unique storage carrier.
Native3 at `8488dbc53` establish safe reads; the unchanged scalar model baseline
stops explicitly Unsupported with zero agreement. Source3 and strict349 pass at
`b89e7e66d`; fresh104/89 premises at that same cut prove frame ownership, live9
with its typed source, real NEXT advancement/detach and consumed-slot refusal.
The old typed fixture is adapted statically with no renewed credit. Quiet reads,
consumed storage, mutation and escape remain required.
The actual351 join over `9782fbb4e` passes strict initialization at `4fbcf845e`.
Future initialized declared object/array reads now copy the live payload owner; ALIAS reads
retain the referent without acquiring its wrapper. Native3 at `8bd90af79` precede
an explicit unchanged-model Unsupported control with zero agreement. Strict351,
source3 and fresh136/134 premises pass at `756c4673b`, covering actual captured
VALUE/result transfer, nullable alias rebinding/type detach and array COW/child
survival through parent retirement. Earlier fixtures are adapted statically only.
The actual353 join over `26134d7a0` passes strict initialization at `8469aa86e`.
Unvisited typed PROP_INITIAL reads now raise ordinary Error after visibility
resolution, retaining declaring-class identity and actual source metadata.
Native3 at `e9dd1a554` precede the unchanged inherited-model Unsupported baseline
with zero agreement. Strict354, source3 and fresh123/141 premises pass at
`3418d8268`, proving Error ownership during receiver release, continued cleanup,
B/previousError chaining and atomic selected-reference binding. No earlier
campaign is renewed; consumed slots remain required.
The actual355 join over `64b2fabca` passes strict initialization at `08dfc81ef`.
Future explicitly unset typed properties now raise ordinary Error without a
getter, using the actual dynamic-first release prefix to exclude consumed slots
whose original/current UNSET images match. Native3 and the unchanged dynamic
Unsupported baseline at `0824519ef` are separate from changed strict/source3 at
`f43b28b47` and 142/147 reached premises at `bad93efed`. The resolved-default
fixture correction preserves its original uncredited failure; no earlier
campaign is renewed. The later377 cut below extends untyped unset reads;
wider getter access remains required.
The actual356 join over `976a55232` passes strict initialization at `4b31fc1cc`.
Future initialized declared values and typed INITIAL/UNSET slots now support
quiet `isset`/`empty` and coalescing with ordinary visibility and no magic consumers. Terminal booleans add no payload owner;
coalescing copies the dereferenced value. Native3 and the unchanged scalar
Unsupported baseline at `ad8135241` remain separate from strict356/source3 and
157/138 reached premises at `310e0fac6`. Actual receiver-release queues, unchanged
borrowed owners, alias rebinding/type detach and kept-child survival pass without
corrections. Earlier quiet assertions are adapted statically only; no campaign
is renewed. The actual358 join over `77d86df730` passes strict initialization
at `36df1d531` (4.663s); source3/295 retain their original changed cut.
Consumed/missing slots and wider magic access remain required.
Module377 resumes literal undefined-property warnings with fixed null after
handler writes, throws or borrowed CV/`$this` receiver retirement. Real temporary
owners and future359 untyped UNSET carriers retain their separate cleanup paths.
Strict359/source6 retain `bd419da30`; the false-only207 repair passes strict359
at `cb1c19466`. Borrowed132, owned154 and pending166 pass at separate cuts;
two distinct false sources pass at `192e33452`, including static handler replacement
and default emission before its destructor disables reporting. The original
fallback and direct-relation fixture failures keep zero credit; the earlier
bound-Closure native witness remains a weaker separate observation. Independent
review accepts these private cuts and the actual359 join over `f5c4eed1f`,
which passes strict compilation at `e77c3eff0` (4.567s) while preserving current
state-aware207 guards,270 renderer-source classification and30 Generator fields.
[Ledger](coverage/semantics/undefined-property-review.json).
The pinned8.5 reference-call increment keeps the genuine returned HCELL and
borrows its captured target before PROPERTY_PREP erases the wrapper. Literal
named noarg nonbuiltin calls without fallback now preserve fixed null after
target retirement, release wrapper-only replacements at FETCH cleanup and chain
throwing cleanup B with previous H. Ten exact originals and replacement237 pass
at `cba3ab695`; pending207/stdClass225 pass at `d615fdf4d` after a fixture-only
WeakReference timing correction. Strict359 passes at the original changed cut;
native7/native2/native1 and the failed pending gate retain separate zero-model
or zero-state credit. Accepted99/79 remain unchanged. [Reference-receiver ledger](coverage/semantics/reference-property-receiver-review.json).
The independently reviewed actual361 join over `7c18fccada` passes strict
compilation at `0b6054930` (4.817s), preserving current return-replay vocabulary,
CALLS pack/NaN schemas and exception interfaces. It renews no source/state cut.
One ordinary positional CV argument now shares377's authenticated cell reception
through the existing361 source-image certificate. Native6 retains `2a9aaece4`;
strict361/source6 pass at `44597addc`, and five reached groups pass760 premises
at `50fb5bed6`, including parameter retirement before lookup, shared/scalar and
separate argument cells, saved carriers and pending H/B cleanup. The first
constructed dynamic-image fixture failure remains zero; only its callable-line
certificate changed. Earlier source10/state669 and all prior failures are unrenewed.
The actual361 composition over `43a3fed4f` passes strict at `827c12ebf`
(4.946s), preserving current compiler insertion and class-promotion interfaces.
One named ordinary CV now uses the same cell reception and authenticates deferred
SEND23 while preserving documentary INPUT24; known sends retain CV26/property27.
Native6 retains `ada28d77a`. The original source6 campaign at `3321d2547` failed
with zero whole-gate credit; its five completed per-case agreements remain valid
under the explicit source-line bridge. Changed strict361 and the affected
deferred comparison pass at `85424f5f4`. Five reached groups pass 1008
setup-inclusive premises at `5ed9fbe45`, covering named slot2/defaults, current/saved
carriers, fixed null, parameter retirement and protected H/B cleanup.
Fixture parser, binder and fallback-conversion failures remain zero; earlier
source6/state760 and source10/state669 are unrenewed.
The actual361 join over `b82bd2425` passes strict at `432084968` (4.923s),
preserving current call roots, return replay and class Override interfaces.
It renews no source/state credit.
Two positional ordinary CVs now use a local source certificate in377;
shared361 ECHO admission and99/79/cell ownership are unchanged. Deferred SEND2
reports emitted23 while preserving documentary INPUT24 and captured prefix7
despite caller mutation to99/19. Native6 retains `0be182e03`; distinct core-only
companion2 observations retain `4e9366787`. Strict361 passes at `f16303c4e`;
source6 and six reached groups pass 1207 setup-inclusive premises at `64fdea48c`,
covering first-null/later-live sends, shared formals, both parameter callbacks
before PREP, current/saved malformed carriers and H/B cleanup. The original
`is_null` source campaign retains zero credit; the second original remains
model-unrun. Earlier noarg/one-CV/named cuts and failures are unrenewed.
The actual361 join over `430face8d` passes strict at `4b39fa53c` (5.028s),
preserving current CALLS/class compiler, return replay and fatal-cleanup interfaces.
It adds no source/state credit.
Two distinct named ordinary CVs now preserve source SEND order and formal-slot
binding through377's local certificate;99/79/CELL/270 and shared361 are unchanged.
Native6 retains `4c64cd257`; the late first-SEND companion retains `b5e60e7b1`.
Changed strict361 and affected pending/late-first source2 pass at `7c2c5e8ef`;
five earlier per-case agreements retain `1378c1d0d` under the named-extraction
bridge. Five whole state gates pass 1245 setup-inclusive premises across separate
366/316/186/77/300 cuts, authenticating both emitted SEND lines, captured null,
shared cells, formal/default leave order and frame/operation pending cleanup.
The original whole-source7 and fixture failures remain zero; previous cuts are
unrenewed.
The actual364 join over `e26e3fb2d` passes strict at `2383140e3` (5.104s)
and one affected pending300 gate. Local byte observations accommodate current
Throwable string carriers; GEN363 and RETURNS378 seams remain disjoint. Earlier
source/private state cuts retain their own identities and credit.
Mixed positional-then-named ordinary CVs now use377's local source certificate;
only the deferred second named SEND needs an emitted-line override. First n0
uses the authentic NAMED_SEND carrier with generic equal-line capture. Native6
retains `f41c88dfe`; strict364/source6 and five whole reached gates pass 1235
setup-inclusive premises at `b766af8a1`, covering slot0/slot2 around default3,
shared HCELL3/payload1, parameter/default leave order, current/saved malformed
carriers and frame/operation pending cleanup. Shared105/213/99/79/CELL/270 and
all earlier accepted cuts/failures are unchanged.
The actual367 join over `4d7ef44ee` passes strict at `87aca689f` (5.179s).
Genuine variable returns keep Notice markers absent; introduced GEN request,
compound-string and static FROMCALLABLE paths are inactive. Source/state credit
remains at the separate private cuts.
The first implicit getter family now supports literal ordinary CV-base reads
through public nonstatic `__get` with one untyped required parameter and no
declared return type. Missing/public UNSET invokes it; accessible typed INITIAL
raises Error without a getter. Module380 holds the receiver once while the
getter context borrows it, verifies exact property types before receiver release,
then copies the current reference payload. Value returns stay fixed, discarded
reads retain their real RV, and H/B/C cleanup exceptions preserve previous links.
Native7 and discarded-native1 retain separate cuts; source8 passes at `7971e6693`
under the validator-only bridge to changed strict368 at `9b46165fc`.
Eight whole state groups pass 1293 setup-inclusive premises across `233992212`,
`176e6efa7` and `d3ee92ffd`. Original native/state failures and diagnostic credit remain zero; earlier
property milestones retain their separate cuts.
[Getter ledger](coverage/semantics/magic-property-get-review.json).
The reviewed actual369 join over `b9f0b1ae9` passes strict at `bae438b0f`
(5.181s, state credit0). Current class/Generator targets, return cursors and
callable factory fields are preserved; these untyped nongenerator getters leave
those paths inactive. Private source8/state1293 retain their separate cuts.
Denied private/protected literal-CV reads and ancestor-private fallback now
invoke the same public getter without hidden property type verification.
Allowed lexical VALUE uses its physical key; INITIAL raises Error without a
getter. Source-certified caller scope survives privileged getter/destructor
contexts without repeating CV/absence lookup. Native6 and source6/strict370
retain separate cuts; five groups pass 880 premises at `19cce2600`, and the
affected214 at `b5be8ecec` brings the total to 1094. The original Unsupported
baseline, preparation failure and failed cleanup-source assertion retain zero credit.
[Denied-getter ledger](coverage/semantics/magic-property-denied-review.json).
The actual370 join over `e2ef06143` passes strict at `2fc127185` (5.422s,
state credit0). Current factory/constructor callable, Generator/collector and
assertion additions preserve the ordinary getter interfaces and are inactive
in these originals. Private source6/state1094 and all failures keep their cuts.
Owned results from statically named ordinary noarg by-value functions support literal
BP_VAR_R through the public getter for missing/public UNSET properties. The
original receiver temporary and getter hold are separate roots; the getter
context still borrows. COPY releases the raw return's cell owner before BASE
releases the original receiver; surviving aliases can retain the cell. The
detached payload stays alive through cleanup.
Readonly verification precedes copying, shared receivers are not forced to
destruct, and discarded/by-value reception and H/B/C previous links are retained.
Native6 and separate by-value native1 precede the model Unsupported baseline
(CLI exit1). Source7 passes at `ca973db86`; changed strict370 passes at
`a2a6f4aae` (5.395s, state credit0). Seven whole reached groups pass 1266
setup-inclusive premises across `e293c490f`, `54e85fba1`, `a2a6f4aae` and
`715f48e38`; original failures remain zero. Existing public/denied cuts are unchanged.
[Owned-getter ledger](coverage/semantics/magic-property-owned-review.json).
The actual371 join over `675a2e1b5` passes strict at `d54c66076` (5.417s,
state credit0). Current compiler severity routing is retained; these getter
sources have no private-final diagnostic. Private cuts and failures are unchanged.
Weak MAGIC_GET verification now converts numeric strings parsed as an in-range
integer. An unconstrained reference updates its real cell; a value return
forwards only the converted RV. Getter-declaration strictness wins over caller
strictness, and readonly backing stays UNSET without a new type source. CV
reception observes later cell changes, while owned reception detaches before
BASE release. Native6 and the model Unsupported baseline retain separate cuts;
strict371/source6 and four groups/598 pass at `5324f2a73`. The two cross-unit
groups pass 180/131 at `28f289817` after their checked literal-eval prelude,
bringing the total to 909. Original preparation and whole-state failures retain
zero credit; earlier getter cuts are unchanged.
[Integer-getter ledger](coverage/semantics/magic-property-integer-review.json).
The actual372 join over `e11f0f06c` passes strict at `5f96624c8` (5.554s,
state credit0). Parent hook guards and class/return/collector/Fiber interfaces
are preserved; these originals use unhooked nongenerator instances. Private
cuts and original failures retain their credit.
Module384 now verifies real typed-property-backed getter references for builtin
int/object targets. Exact compatible verification is whole-state identity; weak
fitting integer-string conversion only selects the first-source conflict Error,
while strict/nonnumeric rejection uses ordinary MAGIC_GET TypeError. No cell write
or getter type-source attachment occurs. Native6 and the model Unsupported baseline
(CLI1) retain separate16d6 cuts; strict373/source6 and six whole reached groups pass
829 setup-inclusive premises at `9cb4c6ea9`. Real source detachment/repair preserves
pending errors, and owned copied payloads survive source/cell removal. The rejected
recorder parent argument ran no numeric actor and retains zero credit; prior cuts
are unchanged. [Reference-getter ledger](coverage/semantics/magic-property-reference-review.json).
The actual374 join over `bed352b5a` passes strict at `e0d62e7ed` (5.399s,
state credit0). Parent anonymous-class, hook/type and cleanup interfaces are
preserved; those wider paths are absent from these originals. Private cuts are unchanged.
Modules380/384 now cover original integer to builtin float getter verification.
An unconstrained reference converts its actual cell; a value return changes only
its RV, and strict getter declarations permit integer widening. Exact floats with
real typed-property sources preserve the whole state; integer widening instead
raises the first-source conflict without converting the cell or attaching the
getter target type. Native6 and the CLI1 Unsupported baseline retain separate
`c96598db0` cuts. Strict374/source6 and six whole reached groups pass 904
setup-inclusive premises at `a8174525b`, covering repeated reads, binary64 rounding,
CV post-destructor copy and owned detachment before BASE release. Bits/original-RV,
string/bool and PARAM controls are constructed; prior cuts and failures are unchanged.
[Float-getter ledger](coverage/semantics/magic-property-float-review.json).
The actual374 join over `2c0d9531c` passes strict at `076606980` (5.481s,
state credit0). Current virtual-hook guards are preserved and inactive in these
unhooked originals; private cuts and prior failures retain their credit.
Weak full numeric strings classified NFLOAT now verify against builtin-float
magic getter targets. Actual unconstrained references convert in place; by-value
returns change only their RV. Exact 7.5/0.1 bits, readonly UNSET backing, prefix
and strict-getter rejection, real string|float source conflicts and CV/owned
cleanup retain distinct behavior. Native6 and the unchanged CLI1 Unsupported
baseline remain at `ddd6b8292`; strict374/source6 and six whole reached groups
pass 877 setup-inclusive premises at `770d69b20`, using reviewed runtime `9dbbb824d`.
The actual375 join over `22adef5d5` passes strict at `cab88a623` (5.527s,
state credit0); private source/state cuts retain their original inputs.
The fixture-only LEADINGNUM preparation failure retains zero credit after its
LEADNUM correction; phase31 evidence is not renewed.
[Numeric-string float ledger](coverage/semantics/magic-property-decimal-review.json).
NINT-classified full strings now also verify against weak builtin-float getters,
casting the parsed integer with ties-to-even rounding and positive zero for `-0`.
Native6 and the unchanged Unsupported baseline retain `26c1b4b55`; strict375/source6
and six whole reached groups pass 899 setup-inclusive premises at `498b2281d`.
Signed limits, actual reference/RV mutation, source conflict, strict rejection
and CV/owned cleanup are distinct. Two obsolete constructed NINT outcomes are
corrected and covered only in the new kept group; phase31/32 reports are unchanged.
The missing-parser baseline and negative-NINT fixture preparation failures retain
zero credit. PARAMETERBACKINGS and wider conversions remain required.
[Integer-string float ledger](coverage/semantics/magic-property-integer-float-review.json).
The actual375 join over `2d0146317` passes strict at `50ba5293a` (5.512s,
state/source/native credit0); private source6/state899 are not renewed.
Weak builtin-float MAGIC_GET now converts false to positive zero and true to one
on the actual unconstrained reference cell or only the by-value RV. Declaration
strictness and null rejection remain distinct; genuine float|bool sources select
a diagnostic-only conflict, preserving raw value/source through later cleanup.
Native6 and the unchanged CLI1 Unsupported baseline retain `4b4c16c8d`;
strict375/source6 and six whole reached groups pass 911 setup-inclusive premises
at `cf9bcd566`, covering CV/owned reception and pending-error repair. Local getter
diagnostics name `bool` without changing shared95 value names. Exactly three older
constructed boolean outcomes are corrected; their nine distinctly named clauses
run only in the new kept group. Phase31–33 reports retain their original cuts.
[Boolean-float ledger](coverage/semantics/magic-property-boolean-float-review.json).
The actual375 join over `78cd4d6e8` passes strict at `f44398f38` (5.646s,
state/source/native credit0); private source6/state911 are not renewed.
Weak builtin-int MAGIC_GET now converts original false to zero and true to one
on the actual unconstrained reference cell or only the by-value RV. Strict getters
and null reject; real int|bool sources select a diagnostic-only conflict before cleanup.
Native6 and the unchanged CLI1 Unsupported baseline retain `0c3a7d0ca`;
strict375/source6 and four reached groups/641 pass at `03ed0aa16`. A fixture-only
binding correction precedes conflict140/strict134 at `90fad5bed`, completing 915
setup-inclusive premises without renewing the passing groups. Two maintained
constructed outcomes contribute only five selected clauses. Two preparation failures
and the original conflict compilation failure retain zero credit; phase31–34 cuts are unchanged.
[Boolean-integer ledger](coverage/semantics/magic-property-boolean-integer-review.json).
The actual375 join over `036035583` passes strict at `9c0bce310` (5.582s,
state/source/native credit0); private source6/state915 are not renewed.
Weak builtin-string MAGIC_GET now converts original false to interned empty and
true to ASCII `1` on the actual unconstrained reference cell or only the by-value RV.
Strict getters and null reject; real string|bool sources preserve the exact first
read and select a later diagnostic-only boolean conflict without changing raw/source.
Native6 and unchanged CLI1 Unsupported baseline retain `90347840c`; strict375 and
four source passes retain `eaaf00ba0`. A comma-echo observation correction has identical
native output; affected conflict/strict source checks and six whole reached groups
pass 997 setup-inclusive premises at `cdbd762a1`, completing source6 without renewal.
At the phase36 cut the original concatenated-echo source is Unsupported because scratch
BASE blocks getter entry; its one diagnostic execution has zero agreement credit. Both preparation
failures retain zero credit. PARAMETERBACKINGS and wider conversions remain required.
[Boolean-string ledger](coverage/semantics/magic-property-boolean-string-review.json).
The actual375 join over `619170565` passes strict at `828bad179` (5.769s,
state/source/native credit0); private source6/state997 are not renewed.
Successful normal scalar EMIT now clears current-frame scratch BASE after output,
without changing concat publication, saved owners or getter admission. Five originals
agree and five whole reached groups pass 570 setup-inclusive premises at `a7ca4b349`;
strict375 passes (5.730s). Native6 and unchanged baseline2 retain `7a3a39cda`; the kept
BASE counterexample is now supported. At that phase37 cut the temporary Stringable
control retains its early-destruction mismatch with whole-source agreement0, including its
matching concat suffix. The fixture preparation failure stays0; earlier cuts are
not renewed. [Concat-consumer ledger](coverage/semantics/concat-emit-review.json).
The actual375 join over `f8ad4d4a4` passes strict at `3876bc706` (5.671s,
state/source/native credit0); private source5/state570 and control0 are not renewed.
Direct ordinary Stringable ECHO now separates original named noarg NEW ownership
from the cast pin; original-input destruction follows output. Borrowed CV self-drop
keeps cast-release destruction before output, including successful returned bytes
before a pending destructor exception. Native6 and unchanged mismatching baseline2
retain `c335d746f`; strict375/source6 pass at `b0a90ed31`. Six whole reached groups
pass 787 setup-inclusive premises: owned/borrowed228 at `caf0f56ab` and remaining559
at `e6ff87e95`, with source/runtime unchanged across the fixture-only bridge.
Plain-string compatibility, malformed carriers/source, budgets, error roots and
callback/cleanup previous links are covered; concat and generic168 remain unchanged.
Both original state seek failures stay0; one nested-cleanup diagnostic has agreement0.
Phase37 cuts are frozen; wider inputs/consumers remain required.
[Stringable ECHO ledger](coverage/semantics/stringable-echo-review.json).
The actual375 join over `3d54ec25a` passes strict at `b0d807f94` (5.774s,
state/source/native credit0); private source6/state787 and original failures are not renewed.
Weak builtin-string MAGIC_GET now converts original integers using shared stringify,
preserving interned digits and request strings for signed/limit values. Actual
unconstrained references update their cell; by-value results change only RV.
Native6 and unchanged CLI1 Unsupported baseline retain `2e3c551a7`; strict375/source6
pass at `0f910ddb4`. Six whole reached groups pass 1,188 setup-inclusive premises
at `7556c579f`, including fixed bytes/carriers, one request append, exact reverify,
alias and owner transitions, CV versus owned cleanup, real string|int conflicts
and strict/null rejection. The original kept budget fixture failure stays0;
only its two driver-transition assertions changed, with runtime/source unchanged.
The maintained constructed integer control contributes three new kept clauses;
phase31–38 cuts are not renewed.
[Integer-string ledger](coverage/semantics/magic-property-integer-string-review.json).
The actual375 join over `753f960e2` at `90da67734` reuses private strict/source6/state1188
and the accepted CALLS25 parent strict cut. Reviewed disjoint seams require no new
numeric execution; fresh strict/source/state/native credit remains0.
Weak builtin-string MAGIC_GET now converts original non-NaN floats through shared
stringify, using the current post-getter precision and fresh request strings even
for digits, ±0 and ±INF. Actual unconstrained references update their cell; BYVAL
changes only RV. Native7/baseline1 retain `f72a39fc4`, affected native2 `0eacf8b8f`,
and strict375 `1923d7939`. Seven source agreements and seven whole reached groups
pass 1,351 setup-inclusive premises at `d8030561f`, including precision14→6, fixed
bytes/carriers/one append, aliases, full driver budgets, CV versus owned cleanup,
real exact-first string|float conflicts and strict/null errors. One maintained
constructed float control contributes two new kept clauses. The original composite
keeps CLI60 timeout/source agreement0; source-only split preserves the runtime/caps
and five original fixtures. At the phase40 cut, NaN is guarded out of both new routes:
its native control observes two warnings and keeps model/state/agreement0. Earlier cuts are not renewed.
[Float-string ledger](coverage/semantics/magic-property-float-string-review.json).
The actual375 join over `ca764836f` at `35f7dc33f` preserves disjoint parent paths.
Accepted parent/private compiler cuts and private source7/state1351 are reused; no new numeric execution.
Weak builtin-string MAGIC_GET NaN conversion now allocates its request carrier before
warning dispatch and retains it through scalar handler mutation and string-data growth.
Actual unconstrained references commit saved NAN; BYVAL leaves the changed global alone.
Genuine constrained references retain the pre-warning conflict decision but diagnose the
live post-handler value. Handler throws commit before getter receiver release; later
cleanup preserves warning/cleanup previous links. Strict getters reject without warning.
Native6/baseline1 retain `5daec64a2`, affected observer-only native6 `3f19892d8`, and
strict375 `00902286f` (6.193s). Source6 and six whole reached groups pass 1,014 premises
at `3f19892d8`, including full allocation/dispatch/commit/discard states, owners, budgets
and malformed carrier/input/site/tail/PARAM guards. The original is_float observer
Unsupported and both fixture preparation failures stay0; pure self-comparison observers
preserve native output. Object/array callback replacements, changed type sources and wider
getter/PARAM scope remain required; phase40 evidence is frozen.
[NaN-string ledger](coverage/semantics/magic-property-nan-string-review.json).
The actual375 join over `6f2a0d742` at `925c3b1bd` preserves disjoint parent paths.
Private and parent compiler cuts are reused; fresh strict/source/state/native credit remains0.
Weak builtin-int MAGIC_GET now accepts quiet integral floats, including 7.0/-0.0,
and captures in-range fractional truncation before deprecation dispatch. Normal
REF return overwrites scalar callback mutation; BYVAL changes only RV. A throwing
handler preserves the changed referent without a captured-int write or second
TypeError, then getter cleanup retains warning/cleanup previous links. Genuine
source constraints retain the pre-warning conflict and diagnose the current value.
Native6/baseline1 retain `d8ae81065`, strict375/source6 retain `6674a8cdb` (5.964s).
Seven whole reached groups pass 1,338 setup-inclusive premises at `d6ce7f2cd`,
including owners, full dispatch/commit/discard budgets and eight maintained
constructed clauses. The original whole425 timeout remains0; two fixture-only
parts retain every original premise under the same cap, with five tails unchanged.
MIN/upper/nonfinite/invalid64 bounds remain constructed controls. Object/array
callback replacements, changed sources/tails, PARAM and wider getter scope remain
required; phase41 cuts are frozen.
[Float-integer ledger](coverage/semantics/magic-property-float-integer-review.json).
The join over `2b482deaa` at `751f6f917` preserves reviewed parent routes with 375 modules.
Private and parent compiler cuts are reused; fresh strict/source/state/native counts remain 0.
Weak builtin-int MAGIC_GET now accepts full NFLOAT numeric strings. Quiet `7.0`/`-0.0`
convert without warning; fractional strings retain their original request spelling in
the precision-loss deprecation. Normal REF return overwrites a scalar/string callback
change; BYVAL updates only RV, and throwing handlers preserve their changed referent
without an int write. Genuine source conflicts retain the initial decision and diagnose
the live value; owned detachment, strict and prefix errors preserve cleanup timing.
Native6/baseline1 retain `06c219141`; strict375/source6 retain `8e33f5c84` (5.966s).
Eleven source-driven reached checks pass 1,469 setup-inclusive premises across
`8c44a16a9`, `79d0c8abf`, `86cb4bdc5` and `854949ada`. Compact entry/resume and
quiet/zero/prefix checks stop at their authentic physical stages. Four whole timeouts
and the intermediate cleanup-validator failure remain0; unused diagnostic preparation
adds no execution. Generic range clones earn no fresh credit. Scalar/string callback
referents and unchanged sources/tails bound the producer; object/array replacements
and wider getter/PARAM scope remain required. Phase42 cuts are frozen.
[Numeric-string integer ledger](coverage/semantics/magic-property-numeric-string-integer-review.json).
The join over `69333905f` at `0de05afcb` preserves reviewed parent routes with 375 modules.
Retained private and parent-family compiler cuts are reused; fresh strict/source/state/native counts remain 0.
Weak builtin-bool MAGIC_GET now converts original non-NaN floats, in-range ints and
ordinary/valid-carrier strings using quiet scalar truth, without numeric parsing.
Actual unconstrained references update their cell; BYVAL changes only RV. Genuine
bool|string source references preserve whole-state exact bool reads, then select a
raw-string conflict without conversion. CV reception sees destructor mutation;
owned reception detaches before BASE cleanup. Strict getter/null rejection stays distinct.
Native8/baseline1 retain `3cccdd0ea`; strict375/source7 and seven whole reached groups
pass 1,053 setup-inclusive premises at `a303833a8`, including fixed truth values,
aliases, full driver budgets, source/STRINGDATA preservation and constructed exclusions.
The original fixture preparation failure stays0 after a one-line driver wrapper correction.
At phase44, NaN native control observes normal overwrite/current-type conflict/throw no-write
with model/state/agreement0; that report retains its historical cut. Shared50/95 and
owner rules stay unchanged; phase43 cuts are frozen.
[Scalar-boolean ledger](coverage/semantics/magic-property-scalar-boolean-review.json).
Exact-current `3de7c5ca` joins `ffc9103a` pointwise; CLASS42 hook guards are disjoint.
Private and retained parent compiler cuts are reused with no fresh executions.
Weak builtin-bool MAGIC_GET NaN conversion now retains the actual input/getter pin
through warning dispatch. Unconstrained references read only bounded numeric payloads
on resume: LONG_MIN unsigned bits are negative zero/false, as is handler float -0.
Saved BYVAL NaN stays true despite global int0; real sources keep the copied-temporary
conflict and diagnose current bool without writing. Throwing handlers restore the
callback and preserve their string write before cleanup45.previous warning45.
Strict getter rejection remains warning-free; owned reception detaches before BASE release.
Native8/baseline1 retain `feef3ed01`; strict375/source7 and ten compact reached stages
pass 1,014 setup-inclusive premises at `a3f383502`, including whole commit/discard
states, actual CV/cleanup reception, full driver budgets and authority exclusions.
The original rule-label preparation failure stays0. Normal unconstrained bool/string
payload histories remain Unsupported with native-only control0; object/array replacements,
changed source/tail authority, PARAM and wider getter/type scope remain required.
Prior44 cuts and generic50/95/289/owner rules are unchanged.
[NaN-boolean ledger](coverage/semantics/magic-property-nan-boolean-review.json).
Exact-current `1e818f74f` joins `58d5c5fee` pointwise across disjoint parent guards.
Private and retained parent-family compiler cuts are reused; fresh strict/source/state/native counts remain0.
Weak string MAGIC_GET now calls ordinary Stringable results with separate cast,
original argument and getter owners. Release of the argument or copied temporary
owner precedes the saved string write; a last-owner destructor sees the raw cell. Successful-cast
release exceptions still allow unconstrained commit; callback failure skips conversion.
Real sources diagnose the live referent; pending release errors become the new
first-source TypeError's previous before authentic receiver cleanup. REF reception,
BYVAL independence, owned detachment and strict no-cast rejection follow native order.
Native8+1/baseline1 retain their original cuts. Strict375 and nine source agreements
are retained; twelve compact checks pass 899 setup-inclusive premises across their
tested cuts, including whole stages, owners and full driver budgets.
Original preparation/source/two fixture failures remain0; one diagnostic adds no agreement.
Unconstrained input changes during callbacks/precommit cleanup, object/array replacements,
changed sources/tails, PARAM and wider getters remain required; phase45 cuts stay frozen.
[Stringable-string ledger](coverage/semantics/magic-property-stringable-string-review.json).
Exact-current `d866388aa` joins `fd7eae1` pointwise with 376 modules and disjoint parent guards.
Private cuts and the retained M30 compiler are reused; fresh strict/source/state/native counts remain0.
Wider coercions, other constrained returned cells, wider signatures, quiet/write/recursive
getters, lexically accessible nonpublic UNSET, changed Closure scopes for nonpublic access, computed
names, hooks, consumed storage and wider reference-call receivers remain required;
held278/279 add no dependency or credit.
Released-CV mutation, raw retired-container
reads, wider wrapper-pointer consumers, internal Generator/Fiber descendants,
binding-time exit, nonordinary replacement objects
and expired notice buckets remain Unsupported. The preserved `is_array` original
now stops at builtin dispatch and retains zero agreement credit. Bounded
source/current-address admission is not a
historical reachability proof. The concise
[review](coverage/semantics/duplicate-property-reference-review.json) preserves
original mismatches and the uncredited strlen observer; no earlier318 campaign
is renewed.

The actual290 composition preserves ordinary borrowed eager-cleanup certificates
and authenticates live clone windows in the existing saved Fiber-close VM without
adding heap roots. Two new exact originals cover a retired private clone maker
closing a Generator inside its Fiber and a live clone window surviving Fiber
close before a second-window write. One strict-SL reached group passes79 premises
for the sole saved carrier, heap-identical source-line forgeries, zero/one-step
resumption and terminal window retirement. Its maintained `closer-window` group
keeps this actual-parent cut separate from the earlier20/665 selection evidence.

Readonly clone-with updates305 now open an independent second window, preserve
the saved setter scope and ordered weak writes, and unwind alias/conversion
failures while retaining committed prefixes. Received values keep positive
physical write revisions, so a previously admitted Fiber write may later replace
a live slot. Genuine opcode/fixed clone makers cache durable source/site/scope
authority without extending heap lifetime. The earlier12 normal/468 unique
conditions remain accepted; later3 alias originals, parked-prior-write1 and two
retired/manual maker originals pass separately. New strict-SL77/151/81/50 reached
controls and production SL277/application0 pass. The
[contract](docs/semantics/READONLY-CLONE-UPDATES.md) and
[ledger](coverage/semantics/readonly-clone-updates-review.json) retain failures and
exact cuts. One directly affected private shutdown original also agrees exactly
after both clone objects retire at its separately recorded367e581df cut.
The separate dynamic/FCC follow-on above, destination-release13, Generator callbacks,
Deprecated dispatch, promotion/hooks/enums and wider lifecycle remain required.

Genuine clone lifecycle300 now checks access before allocation and runs the
selected callback with declaring/called scope. Per-object readonly allowances
survive Fiber parking, successful writes consume them, failed conversions retain
them, and return/throw/exit relock unused slots. Borrowed CV originals may retire;
temporary inputs and genuine intrinsic argument buffers retain their real owners.
On the private ordinary294 base, 20 normals, five declaration errors, one explicit
exit and 264 reached conditions pass; SL276/application0 passes. The
[ledger](coverage/semantics/readonly-clone-review.json) preserves original failures
and the corrected parser/fixture boundaries.
The later305 cut supplies the separate nonempty update window. Destination-release13, implicit
Generator clone creation, force-close/hooks and broader lifecycle behavior remain
required.

Backed readonly lifecycle294 now preserves first-initialization scope, initialized
write/type priority, unset, direct/nested updates and readonly class/trait identity.
Raw object source references detach; target reference binding fails without changing
the slot. Genuine first Stringable conversion retains its admitted destination
through inner initialization, same-site recursion and Fiber suspension. On the
private a939 base, 39 ordinary normals, 18 declaration controls, separate Fiber1 and
243 reached conditions pass; production SL275/application0 passes. The
[ledger](coverage/semantics/readonly-lifecycle-review.json) preserves original
failures and supersedes only288's raw-object target-reference expectation.
The new clone callback cut is separate from these ordinary gates. Destination
release, Deprecated dispatch, promotion/hooks and wider
conversions remain required.

Backed asymmetric instance setters288 now preserve lexical permission, called
diagnostics and direct/indirect/reference/unset ordering. Stringable compound
callbacks retain captured destinations, own consumers and the saved writer scope.
Private34 normal/8 compiler/350 reached checks keep their distinct cuts; one
actual38f1/Fiber281 source at a939 agrees after suspension and target retirement,
and production SL274 stages/init passes. The
[ledger](coverage/semantics/instance-set-access-review.json) preserves original
failures and the no-owner native Fiber frontier. Readonly follow-ons/hooks/magic,
wider static compound selectors and borrowed destination lifetime remain required.

Compound Stringable concatenation352 preserves the actual selected RHS slot:
defined CVs remain live through the left cast, initially undefined reads latch
null, and evaluated VAR/TMP operands retain their real owners until after the
store. Non-reference self CVs reuse the left string; reference self CVs reread.
Entry-time destination identity also preserves aliases created or rebound during
conversion. Eleven exact originals and private332 compiler/init pass at632c;
one separate caught left/right throw original passes at4bf8. One root/DIM/property
expression-result original and249 new reached premises pass at7c15. The
current-parent gate retains its separate cut in the
[ledger](coverage/semantics/compound-string-live-rhs-review.json). Earlier334/344
evidence is unchanged; wider borrowed destinations remain open.
Actual339 over CALLS351 `fd432561f` passes algo/struct/init at `0b0bd4336`,
with independent pointwise parent review and no13/249 source/state renewal.

Named static-property Stringable compounds356 retain the initial plain-slot versus
reference-cell destination and conversion branch through callbacks. Typed stores
return their verified value; initial-string reference writes and late plain-slot
alias detachment preserve Zend's unchecked backing and retained type-source history
with nonowning entry/write/retirement evidence. Eleven exact originals and private340
compiler/init pass atc4ed; a separate typed-reference conversion/rejection original
passes at163e. New368 reached premises pass ate148, including future-entry,
foreign-cell and repeated-site history rejection. Actual344 over COMP `e1c3d4d618` passes algo/struct/init at `f0e03c885`,
with pointwise353/354/355/357 and owner-factor review in the
[ledger](coverage/semantics/static-compound-string-review.json).
Ordinary-method `self`, `parent` and `static` selectors now capture the actual
lexical/called scope before callbacks; nonowning selected ENTRY history retains
the destination through nested calls, private shadows and reference rebinding.
Six exact originals and private344 compiler/init pass at `45f32a157`;323 new
reached premises retain separate144 at `b228479d6` and179 at `714465927` cuts.
The unchanged earlier keyword Unsupported record retains zero agreement.
Actual347 over `66160341f` passes algo/struct/init at `c2b0f283b`, with
exact257/296/301/360 parent review and no6/323 source/state renewal.
Dynamic class selectors now preserve the class resolved before RHS evaluation,
including once-only helper/object selection and selector mutation during RHS or
conversion. Captured references retain the original cell and typed result; scalar
concatenation restores the ordinary base without a selected-entry event. Five
exact originals and private344 compiler/init pass at `09034d789`;241 reached
premises pass at `fc7727974`. The unchanged earlier dynamic Unsupported record
retains zero agreement. Actual349 over COMP `ea58ac361` passes algo/struct/init
at `bba0c15be`, with pointwise361/362 and same-state graph-factor review and
no5/241 source/state renewal.
Computed static-property compounds366 delay name CV reads until after RHS work,
retain evaluated name/RHS operands through real class preparation, then transfer
the selected property to the existing static conversion/store. Buffered fetch
lines remain distinct from initializer error lines. Six exact originals pass at
separate `a0b4f81c9`/`82ea0e591`/`03bf61f0a` cuts; first-cut compiler/init passes.
New295 reached premises pass at `1abff50f4`, including real cold-preparation
owners, compiled-name/marker forgeries and retained REF selection. Actual-parent
compiler/init passes at `ed57a7c5c` over CALLS367 `9aec542e2` (353 modules),
with pointwise SOURCE365/367 owner/line review and no6/295 source/state renewal.
Keyword scopes entered through Closure/fromCallable or
other callable wrappers, wider borrowed lifetime and registered-handler
missing-RHS continuations remain separate; paused return producers are unchanged.

Stringable computed static-property names371 freeze the selected class and
converted bytes, check the property address, then retire the receiver before
capturing the live row, reference cell and RHS. Pending scalar writes retain
PHP's conversion/operator priority.
Failed NAME conversion and throwing final cleanup now keep the authenticated
empty-name FETCH and queued tail, with Error.previous=drop.previous=cast.
The descriptor walker restores only its saved inert base and original queued tail.
Eight of nine exact originals pass at distinct private cuts. The original
pending-masks source remains required/open: the changed public run retains its
60-second CLI timeout and zero whole agreement. Prior123 receiver/cold-owner
premises and new238 late-address/pending/projection premises have separate inputs;
changed algo/struct/init and the238 fixture pass. The preserved73.924s diagnostic
records the repaired double-throw mismatch. Current360 algorithmic compilation
passes ataa44149a overb894 with pointwise99/156 review and no accepted source/state
renewal. The unchanged original7 current run repeats CLI60 timeout in65.143s, with
exact native bytes and zero whole agreement. Standalone init/state at that
401 baseline are UNRUN.
A narrow module 46 constant-insertion factor at 30a7223 evaluates the existing lookup
once, preserving exact values/table IDs, list order and conflicting-value refusal.
Changed compilation and strict current 238 plus 23 focused premises pass, including
the nested-NAN export pipeline and ten empty/present/order/identity controls.
Original 7 still returns CLI 60 timeout in 65.092 s with exact native bytes and zero
whole agreement. Matched prefixes of 400 steps return the same BUDGET state tuple:
lookup calls fall from 689,580 to 229,972; exclusive instrumented time falls from 8.4063 s to 2.9977 s.
These wall-time profiles locate work; they do not establish a CLI 60 completion.
The initial fixture syntax failure remains preserved with zero credit.
Standalone initialization is not renewed; prior 123/private 238 keep their cuts.
Actual-parent compilation passes at 64854b87 over 8f9dda67 with 361 modules;
promotion, HCELL and replay hooks are preserved, with no source/state renewal.
A module 39 specialization at 646e075b4 over 43a3fed4 with 361 modules returns
the existing empty roots for STMT before the owning-task fallback. Compilation
and 14 focused controls pass, retaining nested scopes, ordered duplicate roots
and task-owned allocations. Same-parent prefixes of 400 steps return identical
116,334-byte BUDGET tuples. The 254,563 task_nodes calls remain unchanged;
exclusive instrumented time falls from 3.0177 s to 0.8355 s, and total instrumented
time from 23.3692 s to 20.8877 s. These measured wall times are not CLI estimates.
Required original 7 still returns only timeout after 65.157 s under the unchanged
CLI 60/outer 90/100000-step caps, with exact native bytes and zero agreement.
Prior eight sources and 123/238 plus 23 premise cuts are not renewed.
Actual-parent compilation passes at 78a713178 over 78a7c210 with 361 modules,
preserving the one-CV property seam; this checks compiler compatibility only.
A verbatim module 46 access-lookup clause reorder at 566aac7e over cf9411d67
passes compilation and 11 path/mode/first-match controls with 361 modules.
Same-parent prefixes of 400 steps preserve the complete 116,334-byte BUDGET tuple.
The 1,746,870 ppaccess_at calls remain unchanged; exclusive instrumented time
falls from 3.1486 s to 2.8034 s, and total time from 20.8399 s to 20.5914 s.
This modest matched observation is not a CLI estimate. Required original 7 keeps
its prior timeout and zero agreement; no source or accepted state cut is renewed.
Actual-parent compilation passes at 640a59899 over 7c3299fd with 361 modules,
preserving scalar replay hooks; this checks compiler compatibility only.
A new cold double-throw source at b82bd2425 with 361 modules passes native/model
agreement and 155 genuine state premises without a production change. Empty-name
lookup leaves the static default deferred, preserves Error.previous=drop.previous=cast,
and retires the owned RHS without calling its __toString. Actual operation/FETCH,
descriptor, history and heap guards pass. The preparation stop and incorrect
receiver-field fixture failure remain preserved with zero credit. Prior source/state
cuts are unchanged; required original 7 remains open at its CLI 60 timeout.
Current publication over ee06368a4 with 363 modules passes compilation and 156
carrier-aware cold fixture premises at 2009abf79; source agreement stays at b82.
ARG329 EPS/mixed-Notice and held return-verifier work remain excluded.
Live compound string gates now accept authenticated carrier bytes and preserve
the concat helper's STRINGDATA state; empty branches keep legacy unknown identity.
Ordinary inherited-static by-ref NAME/RHS agrees at 09cd/363 with 213 premises
(149 reached, 64 constructed). At 5e77/363, static Closure::fromCallable computed
keyword selection retains genuine CLOSURE_SCOPE through the RHS callback/write
and actual request retirement. The wrapper matches native bytes; 359 premises
(239 reached, 120 constructed) authenticate the entry and reject narrow forgeries.
All prior stops remain zero credit. EPS saved selection keeps ordinary compatibility;
other Closure families, INI identity, ARG329 and required original 7 remain open.
Actual-parent compilation passes at a67b4e4a over 633ecec1e with 367 modules;
pointwise Notice/ownership review adds no source or state renewal.
Inherited nonstatic `Closure::fromCallable` now admits the exact saved receiver
through existing source/body/history evidence. Ordinary-instance agreement stays
at 4d7/367; repaired wrapper agreement passes at ff368a41/367. Its 430 premises
(282 reached, 148 constructed) authenticate receiver ownership through the distinct
RHS callback/write, explicit Closure and receiver retirement, and saved descriptor
validity afterward. Missing or substituted current/saved receivers are rejected;
selection metadata adds no owner. The earlier wrapper Unsupported remains zero
credit, and required original 7 retains its separate CLI 60 timeout.
Actual-parent compilation passes at 943e2c3c over 94f4b007 with 367 modules;
pointwise promotion/property replay review adds no source or state renewal.
First-class `Closure::fromCallable(...)` now has a source-stamped factory carrier
and its own owning CONFIG kind. The returned method capture retains a nonowning
factory certificate after retirement. The direct control agrees at 6e709da7/367;
captured inherited by-ref NAME/live Stringable RHS and six new permission,
named/unpacked argument, identity and argument-retirement originals agree at
8cc7ed12/367. Its 526 state premises pass (467 genuine/derived, 59 constructed),
including factory creation, CONFIG owner count 2, distinct returned receiver
ownership, factory retirement, callback/write and explicit receiver retirement.
Invocation USER scope controls callback access; creation scope grants no later access.
The initializer Unsupported and pre-child clean-status stop remain zero credit.
The maintained renderer is byte-identical to the accepted fixture; relocation
adds no runtime renewal. Invoke aliases, nullsafe/computed method entry,
computed/keyword creation and captured-factory Fiber/wider getter callbacks stay open,
as does required original 7's CLI 60 timeout.
Current-parent compilation passes at def000e9 over ac4a95b5 with 368 modules;
pointwise storage/intrinsic/getter review adds no source or state renewal.
The [factory ledger](coverage/semantics/from-callable-review.json) keeps the
distinct native/source/state cuts and boundaries.
Literal captured-factory `->__invoke(callback: ...)` now authenticates method
entry and preserves METHOD_RESULT plus the caller tail. CONFIG owns the selected
factory while an argument clears its caller cell; the returned Closure owns its
receiver independently after factory retirement. Invocation USER permission and
API→Closure invoke error frames match native PHP. The variable control agrees at
b9f0b1ae/368; four explicit sources and 552 state premises (512 genuine/derived,
40 constructed) pass at c1cdc2b5/368. The wrong-representation state failure and
original interpreter failure remain zero credit. Maintained source/fixture bytes
are unchanged; relocation adds no runtime renewal. Original 7 stays OPEN timeout0.
Actual-parent algorithmic compilation passes at b6022a52 over 7cb33cde with
370 modules; pointwise constructor/COMP/property review renews no source/state cuts.
Literal first-class factory `->__invoke(...)` now forwards to existing identity
capture without allocating an alias object or changing the factory creation site.
The real Closure identity/by-reference control agrees at e2ef/370; the factory
witness agrees at 3cb295d1d/370 after original and alias caller-cell retirement.
Its 610 premises (550 genuine/derived, 60 constructed) preserve exact task/tail,
arena identity, CONFIG owner retention, retired factory provenance and independent
receiver/RHS/write/retirement. The interpreter failure and fixture variable collision
remain zero credit. The maintained renderer is byte-identical to the accepted
fixture; wider computed/nullsafe captures and original 7's CLI60 timeout stay open.
Actual-parent compilation passes at `0b4de6cd` over `5a127787` with 371 modules;
pointwise CLASS/ownership review adds no private source, state or native renewal.
Captured factories now select finite Throwable getters through an immutable,
nonowning creation/invocation certificate. The returned getter owns only its
receiver, reads the changed message after factory retirement, and keeps that
receiver through clone/equality and final release. The direct control agrees at
557e/371; captured live-message and new clone/equality sources agree at 771e/371.
Its 191 premises (154 genuine/derived, 37 constructed) prove actual CONFIG/mint,
parked return cleanup, restored result and last receiver retirement. The prior
Unsupported and one-step fixture failure remain zero credit. The maintained
source/renderer bytes are unchanged; relocation renews no runtime evidence.
Wider getter/binding/library targets and original 7's CLI60 timeout remain open.
Actual-parent compilation passes at `71edcca7` over `8cc17e6e` with 371 modules;
pointwise EX/RETURNS review adds no private source, state or native renewal.
Captured factories now select static `Fiber::getCurrent` with no bound input.
Actual CONFIG validates the selected live factory; its saved CALL authenticates
creation and invocation after producer retirement and adds no owner. Frozen
DIRECT members preserve getCurrent when the source ALIAS cell changes to suspend.
The direct control agrees at 05b0/371, and the repaired captured source agrees at
7928/371 before and after Fiber suspension. Its 270 premises (227 genuine/derived,
43 constructed) pass; the original Unsupported and compiler binding stop remain
zero credit. Other captured Fiber kinds/bound inputs and original 7's CLI60 timeout
remain open. Maintained source/fixture relocation adds no runtime renewal.
Actual-parent compilation and initialized SL270 pass at `f1c392c8` over
`0a4cf46e` with 372 modules; pointwise Hook/EX39/RETURNS review adds no source/native renewal.
Captured factories now select bound `Fiber::isSuspended` with one receiver edge.
The factory, callback arrays and original Fiber cell retire before status calls;
WeakReference confirms the returned Closure alone keeps the Fiber alive. Frozen
selection remains isSuspended after the referenced name changes to isTerminated,
returning false/true/false across INIT, suspension and termination, then releasing
the last strong owner. Direct agreement stays at e11f/372; captured agreement and
241 premises (189 genuine/derived, 52 constructed) pass at 151776b71/372, including
exact zero-budget resumption. Saved producer authority survives final retirement,
while bound capture source/liveness correctly becomes false. The original
Unsupported remains zero credit; other targets and original 7 remain OPEN.
Actual-parent compilation and initialized SL241 pass at `baf287a4` over
`d2ea8468` with 372 modules; CLASS/CALLS seams preserve prior source/native cuts.
Captured factories now select receiver-free static `Fiber::suspend`. Frozen
DIRECT members retain suspend after the source reference becomes getCurrent and
the factory/callback retire. Nulling the selected Closure's caller cell during
value arguments leaves its real result marker as the sole parked owner. Resume
returns the exact value; ordered cleanup retires the capture before restoring
that value to its original consumer. Direct agreement stays at 59080391/372;
captured agreement and 299 premises (247 genuine/derived, 52 constructed) pass
at c871de946/372, including saved VM authority and exact zero-budget resumption.
The original Unsupported and premature-result fixture263 failure remain zero
credit. Maintained source/render bytes are unchanged; no relocation renewal.
Other targets and required original 7's CLI60 timeout remain OPEN.
Actual-parent compilation and initialized SL299 pass at `288bb478` over
`8a81891c` with 374 modules; COMP383/PROPS384 seams preserve prior source/native cuts.
Captured factories now select bound `Fiber::resume`. The producer retires during
selection arguments; frozen resume survives later name mutation and callback
retirement. Clearing the selected capture cell in its value argument leaves the
saved caller result marker
as the sole Closure owner; its INPUT edge retains the receiver through the child
transfer. The child receives the exact done value and the call returns null.
Authentic eager cleanup retires both before restoring the original consumer tail.
Direct agreement stays at fa678cc48/374; repaired agreement and 343 premises
(264 genuine/derived, 79 constructed) pass at 2daa5c433/374, including exact
zero-budget resumption. The original Unsupported remains zero credit; maintained
source/render relocation renews no runtime evidence. Other targets and required
original 7's CLI60 timeout remain OPEN.
Actual-parent compilation and initialized SL343 pass at `56a92700` over
`a6994698` with 374 modules; RETURNS/COMP seams preserve prior source/native cuts.
Captured factories now select bound `Fiber::throw` with frozen selection and
retired producer/callback. Clearing selected and exception caller cells leaves
the authentic SENT buffer owning the Throwable; injection preserves its identity
through THROW_SEARCH and CATCH_BIND. The saved WAIT/result tail retains one
Closure and its receiver edge while the child catches the exact object. Handled
termination returns null; ordinary cleanup retires the exception before the
historical result descriptor, then releases Closure and Fiber before the consumer.
Direct agreement stays at 2112d1e9/374; repaired agreement and 439 premises
(343 genuine/derived, 96 constructed) pass at 07fb94254/374, including exact
zero-budget resumption. Original Unsupported retains zero credit. Maintained
source/render relocation renews no runtime evidence; wider throw/error paths
and original 7's CLI60 timeout remain OPEN.
Actual-parent compilation and initialized SL439 pass at `6d26cefa5` over
`9f00481d` with 375 modules; CALLS385 Iterator and inherited GC/property/anonymous
guards preserve prior source/native cuts.
A new unhandled bound injection crosses ordinary child finally and reaches the
outer caller with the same main-created Throwable. Existing rules agree on two
fresh direct/captured originals at 204200d1f/375; 542 premises (433 reached/derived,
109 constructed) validate pending finally, 302 FIBER_THROW_FINISH callback
retirement, saved API transfer, abrupt capture cleanup and the caught cell's last
owner. Algo and initialized SL pass at the same cut; no semantic edit or old-cut
renewal is needed. The interrupted ENOSPC recorder retains zero credit. Wider
throw/error forms and original 7 remain OPEN.
Exact aa4a7c27/375 validation-only composition is statically reviewed: guarded
reference-return, property, anonymous NEW and Iterator unpack tasks are absent
from these originals. Source2/state542 retain the 204 cut; current runtime is UNRUN.
Wrong-Throwable scalar 7 on an INITIAL Fiber rejects before state checking or
transfer. Two direct/captured originals agree at 47b318154/375; 340 premises
(288 genuine/derived, 52 constructed) validate the fresh scalar argument trace,
original RELEASE tail and ordinary callback/capture/Fiber pruning before catch.
Algo and initialized SL pass; the two corrected fixture failures retain zero
state credit. No runtime change or older-cut renewal is needed.
Exact f09a7275/375 validation-only composition is statically reviewed; guarded
reference-return, GC-plan, magic-property and Iterator unpack paths are absent.
The 47b source2/state340 cut stays distinct; current runtime is UNRUN.
Valid main-created Throwable arguments on the same INITIAL path instead produce
FiberError; its trace keeps the supplied object after capture/Fiber retirement.
Two new direct/captured originals and 456 premises (400 genuine/derived, 56 controls)
pass at 62405de0a/375, including the reached caught-null step that prunes both
Throwable objects and trace graphs before final weak reads. The derived trace-owner
fixture failure retains zero credit; runtime rules and older cuts are unchanged.
Exact 6598b059/375 validation-only composition is statically reviewed; guarded
magic-property, hook-coalesce, empty-class and Iterator unpack changes are absent.
The 624 native2/source2/state456 cut stays distinct; current runtime is UNRUN.
Module 358 now admits captured-factory bound getReturn through the existing API.
A defined ordinary object remains owned by Fiber.VALUE after main argument
retirement; retrieval returns that same object. Direct agreement stays at 96bbf526;
repaired captured agreement and 413 premises (363 genuine/derived, 50 controls)
pass at 3a31fc727/375. The genuine RESULTfalse release operation preserves the
object until the original consumer resumes; selected-null retires capture/Fiber,
then returned-null retires the object and empty trace. Original Unsupported and
syntax failure retain zero credit. [GetReturn cuts](coverage/semantics/from-callable-review.json)
stay separate; wider getReturn forms and source 7 remain OPEN.
Exact 4a30db48/375 composition passes algo and initialized SL413 at cef6efde
(5.537s/49.561s). The preserved fixture validates the current ordinary object
carrier and cleanup; private source/native/state cuts remain distinct.
Captured factory bound START now uses the existing 348 named-buffer protocol.
The saved API retains the same object after callback-local null; ordinary 302
callback retirement precedes buffer release, then RESULTfalse retires capture/Fiber.
Direct agreement stays at 922abc0e; repaired capture and 472 premises (415
genuine/derived, 57 controls) pass at c471c767/375. Original Unsupported and syntax
failure keep zero credit; wider START forms and source 7 remain OPEN.
Exact f0656d75/375 composition passes algo and initialized SL472 at 07e319450
(5.202s/75.748s), preserving the named-buffer and ordinary cleanup paths. Private
source/native/state cuts retain their original identities without renewal.
Captured factory bound constructor now reaches the existing repeated-constructor
FiberError for a valid fresh Closure on an initialized, unstarted receiver.
Direct agreement stays at 799681aa; repaired capture and 489 premises (433
genuine/derived, 56 controls) pass at e716e2f5/375. The same fresh argument stays
owned by the error trace after old callback/capture/Fiber retirement; the actual
caught-null write prunes that graph before final weak reads. Original Unsupported
keeps zero credit; broader constructor forms and source 7 remain OPEN.
Exact 0952d6f7/375 composition passes compiler and initialized SL489 at
6de0971e (5.227s/78.994s); current source credit and private renewal remain 0.
Explicit constructor `__invoke` requires no runtime change. Two fresh originals
and 536 premises (468 genuine/derived, 68 controls) pass at c21eaf7f/375.
Both trace argument arrays retain the same fresh Closure: derived CONFIG plus
copied RESULTtrue gives four owners, while the genuine original RELEASE has two.
Quiet old callback/capture/Fiber retirement and the actual caught-null write
prune both trace paths before weak reads; prior cuts remain separate.
Exact a1b606eb/375 validation-only composition is statically reviewed, including
the reached generic emit BASE clearing and guarded disjoint parent paths. Native,
source2 and state536 retain c21; current runtime is UNRUN with renewal 0.
Module 358 now admits captured-factory bound isStarted/isRunning/isTerminated
through a disjoint nonempty-INPUT guard and saved factory/site certificate.
Direct 3 stay at 4e2702ce; captured 3 and 1287 premises (1230 genuine/derived,
57 controls) pass at 280eac05/375. All 15 genuine phase results preserve real
running caller/global owners; one shared marker-release/status-null suite prunes
capture/Fiber before weak reads, while the other two retain exact heap and source
resumption checks. Existing isSuspended and API protocols are unchanged. Original
Unsupported, failed admission and the genuine guard probe retain zero credit;
source 7 and wider consumers remain OPEN. [Status cuts](coverage/semantics/from-callable-review.json).
Exact 9e263fb/375 composition passes compiler and initialized SL1287 at
73245eed (5.532s/288.774s), retaining actual emit/cleanup ownership checks.
Current source credit and private renewal remain 0.
The [ledger](coverage/semantics/static-compound-string-review.json) retains
the source/state cuts and failures without renewing older evidence.

Array eval/include conversion287 dispatches the real warning before parser or
file-provider work and freezes `Array` after callbacks, even when they replace
the operand. Borrowed variables gain no temporary owner; captured arrays survive
provider/parsing/compiler notices and retire before nontrivial file bodies or
catch search. Four exact destructor-free sources and 207 state premises pass at
3b2c; actual33df preserves Fiber/ArrayAccess/trait-demand routes and passes SL273
at5a0e. The [ledger](coverage/semantics/source-array-review.json) retains original
fixture/compiler failures; the destructor lifetime witness agrees in the separately
reviewed270 composition. Selected undefined/Stringable ingress, helper results and
retirement traces are installed above. Wider source producers/providers remain required.

ArrayAccess284 now admits its builtin interface contract and direct R/IS,
isset/empty, Set/append and Unset calls. Effective inherited methods and tentative
return notices preserve prototype order and ReturnTypeWillChange suppression.
Receiver/key protections, entered parameter owners and borrowed result pointers
retain native callback, reentry and exception timing, including NaN truth warnings.
Author13/205 and independent20/287 share five originals: 28 unique private programs
(26 normal and two declaration errors), 492 reached assertions. One actual465d
source at6ccb preserves private Owner/Child selection, receiver retirement and
post-Set readback through the old typed CELL. The
[contract](docs/semantics/SOURCE-ARRAYACCESS.md) and
[ledger](coverage/semantics/arrayaccess-review.json) retain separate source/compiler/
state cuts and original failures. Full nested/read-write/reference and wider
memoized consumers, plus combined Iterator/ArrayAccess notice ordering, remain
required. Newly reachable unsupported consumers stop explicitly; paused return
verification stays separate.

Fiber281 now implements live user-callback construction and direct
start/suspend/resume/throw, status, current identity and stored returns. Callback
selection is cached; genuine VM stacks, live reporting masks and C argument
buffers survive suspension while globals, INI and handler registration stay
shared. Nested waiting Fibers remain running. Thirty normal originals and thirteen
source-derived states/782 conditions retain their mixed cuts. Deferred/literal
named holes, entry-error caller provenance and raw named-buffer admission are
checked through genuine pending continuations and malformed records. Actual
constant-NEW identity and a separate running Generator preserve genuine owners;
global Generator admission stays on the actual machine while parked Fiber stacks
keep their local guards. Three Unsupported controls earn zero agreement. The
allocated-Fiber argument source and null-callsite preflight state checks retain
separate cuts.
[The contract](docs/semantics/FIBERS.md) retains the exact tested cuts.

Fiber291 now force-closes ordinary suspended callbacks through an unregistered
control: catches skip it, finally blocks run, and replacement exceptions return
through the genuine operation or parent finish. Captured destructor retirement
keeps its real empty internal root and ordered ownership. Five destruction
control lists move with the VM. Actual 270/296 composition at 279 modules
passes strict-SL initialization, one exact destructor/helper source comparison
and a 58-premise default-AL state for parked lists, ownership and resumption.
Twenty-nine normal close comparisons and
fourteen reached states/1,037 conditions retain their private cuts; request-scan
and ordinary-library controls earn zero agreement.

Fiber302 stores a returned result before ordinary callback retirement and keeps
its definedness separate from a thrown body exception. Captured destructors may
suspend, resume and receive public throws; stored results survive replacement
errors even when `getReturn` rejects the failed Fiber. Fifteen targeted normal
comparisons and twelve state groups/871 conditions retain their private cuts.
Module 308 adds protected cleanup after an actual return; the body-undefined
case remains Unsupported and its engine witness is held. The required internal/reference
callbacks, API entry, unpacking, initializer switching, request/fatal cleanup and
GC remain open. Full core stays open; returns verification remains paused.

Fiber313 supports cached string `error_reporting` callbacks with weak C receives,
owned arguments and an authenticated borrowed result tail. Handler suspension and
receiver retirement retain warning producers, resumer traces and internal scope.
The latest294-parent join preserves GC, returned-child append, source emission and
Arrow rules; strict295 compilation and one new explicit-request GC/autoglobal-eval
original pass independent review. The [ledger](coverage/semantics/fiber-core-callbacks-review.json)
preserves prior source/state cuts and separates bounded public checks from the
unconfirmed rich whole-source/full63 runs. Wider internal/FCC/reference callbacks,
initialization, request/fatal/GC consumers and complete core remain required;
the final fresh offline rebuild is outstanding and returns verification stays paused.

Fiber322 adds effectful scoped/deprecated constructor method selection,
warning-before-status ordering and immutable original maker/scope authority.
Actual Fiber nominal argument admission and inherited RuntimeException construction
close gaps found by unchanged originals. The actual305-parent interaction preserves
a private static callback made by a GC destructor after its receiver retires;
one exact source and92 reached premises pass independently. Earlier thirteen
sources and815 conditions retain their original cuts in the
[constructor ledger](coverage/semantics/fiber-callable-constructors-review.json).
Final307-parent composition passes strict308 and compatibility review; broader callable/FCC,
internal/reference/lifecycle consumers and final validation remain required.

Generator280 creates object-owned suspended frames after eager ordinary receives.
Value yields, literal iterator methods, `getReturn` and value foreach retain
captured aliases, ordinary private creation scope and real resumer traces.
Generator-specific completion bypasses ordinary declared-return coercion;
return-supertype admission mirrors the pinned one-level intersection scan.
Twenty-seven normal sources and three compiler rejections agree at e235d8dd1
in separate first5 and independent25 cuts. Six lifecycle Unsupported controls
earn no agreement. Independent source-reached carrier144/Closure154 pass at2f21,
nested77 atd7ca and abrupt44 at6c221 (419 premises across four originals).
Full public admission, live/suspended cursor owners, captured references and
natural try/finally cleanup pass; failed checks remain retained. Delegation/reference
yields, further call forms,
changed caller scopes, force-close finalizers and destruction/GC remain required.
Three introduced parent sources agree at9abff: constructor-created constant
identity, deferred REAL Closure autoload and parse-folded versus live precision.
The new constant95 state phase retains the same completed receipt through
receive/yield/return and retirement; its noncached instance owners pass full
public/heap admission. Original interpreter/fixture failures retain zero credit.
[Scope and maintained tests](docs/semantics/GENERATORS.md).

Literal Generator `send`/`throw` capture one argument before initialization,
deliver used yield results or an ordinary Throwable search, and retain actual
API arguments and live resumer traces. Twenty-three new normal sources agree
at26328 in separate author5/independent18 cuts. Fresh initialization failure keeps
the supplied exception primary and links the initialization exception as previous.
Independent array146/finally124/initialization101 pass at fixture887f51d29,
semantic26328 (371 conditions across three originals): actual input owners,
exception identity, full public admission and malformed resume rejection.
One actualc729 source at63b45/semanticca7da combines default NEW autoload,
live/default versus parser-folded precision and fresh sent-object identity.
The original SL structuring failure retains zero credit. Full Generator
follow-ons remain open.

Parameter-default NEW autoload285 resumes authentic deferred initializers after
lookup, preserving declaration strictness and formal lines. Loaded constructors
are selected afresh; allocation and all nested AST arguments precede constructor
access, while loader throw/miss suppresses arguments. Nine private sources agree
at07a78; lookup94/recursive37/retirement43 pass at ebb346, including retained
receiving owners and heap-valid pending/history tag, line and caller forgeries.
One actuald57/GEN280 source agrees at24f376: lookup/arguments/construction remain
eager before generator suspension. Original public/fixture failures and the
parameter-Closure initializer Unsupported retain zero credit; its WeakReference
lifetime oracle is native-only. The [ledger](coverage/semantics/default-new-autoload-review.json)
keeps these cuts distinct. Global-constant NEW autoload, parameter callable
initializer producers and wider lookup/link consumers remain required.

Autoload277 now implements the four required SPL control APIs with real callable
caches, owner roots and live queue cursor/capacity behavior. Ordinary named/dynamic
NEW and class-parent lookup suspend before arguments; lookup inherits source
strictness/site while explicit dispatch is weak/internal. Selected names retain
exactly one raw slash normalization. Indexed declaration certificates preserve
loader authority after unregistering and receiver/scope retirement. Thirty-four
sources pass at b967 and two at b440; guard cuts stay separate in the
[ledger](coverage/semantics/autoload-review.json). Its 263 original finite premises
pass with seven typing bindings and eight repeated setup premises. One actual
b025/global-constant REAL loader source passes at a37. Original failures and AL
timeouts remain retained; SL uses the existing exact runner at the same120s cap.
Parameter-default AST NEW is covered by285 above. Global-constant AST NEW and
wider lookup/link consumers remain required; default filesystem search is
excluded and returns stay paused.

Scalar-container continuations282 now stage missing-base, key-CV and offset
warnings through ordinary and quiet reads. Missing-base warnings resume with
independent null; defined scalar pointers can change the later message type
without creating a late array lookup. Genuine nested row/key operands retain
real owners, and terminal isset/empty string predicates remain distinct from
coalesce. Throws suppress later callbacks and writes. Author8/212 and independent13/272
share one original (20 unique private programs/484 assertions). One actualb025
source at5eefe retains private Owner/Child selection, key-temporary ownership and
live caller/static17. The [contract](docs/semantics/SOURCE-CONTAINER-READS.md) and
[ledger](coverage/semantics/container-read-review.json) retain separate source cuts
and the original formatter failure. A separate stdClass transition agrees;
the historical ArrayAccess control retains its earlier interface-contract
Unsupported and earns no guard-execution credit. Direct ArrayAccess is covered
by284 above; string/ordinary-object, wider base and GLOBALS/memoized producers
remain required.

Container continuations276 now initialize undefined/null/false CV-rooted W/RW
storage before key demand and preserve final array-reference source cells. False
callbacks retain genuine protection and distinct FETCH/ASSIGN/DIM_OP selection;
throwing paths keep native initialization/write/error priority. Source-backed raw
typed DIM_OP array backing survives COW and clears on whole-cell writes without
changing ordinary type conversion. Author12/242 and independent21/275 share three
originals (30 unique private programs/517 assertions). One actualae0 source at851
preserves private Owner/Child selection, captured source lifetime and live
caller/static17. The [contract](docs/semantics/SOURCE-CONTAINER-WRITES.md) and
[ledger](coverage/semantics/container-warning-review.json) retain the original
loader/fixture failures and separate cuts. Wider read/quiet/memoized/unset/GLOBALS
containers, string/object producers and complete core remain required.

Live precision272 now preserves registered/raw get/set/Restore through option
callbacks, runtime string types/conversions, nonnumeric comparisons and late trace
formatting. Each main/eval/file unit retains creation precision for parser-folded
literals; compiled operands retain their conversion-point precision, while genuine
constant/default/property AST operands instead use live precision after callbacks.
Sixteen exact source/profile comparisons across eleven main programs retain
d028/e594/73011 cuts. At73011,
state54/39/27/74 (194 supplied checks plus12 program bindings) and transport12 pass;
SL261 and the changed adapter jobs1 build retain their separate cuts. The actual
ae0 parent is preserved in264 modules through focused source review, with no
renewed execution. [Ledger](coverage/semantics/precision-review.json) retains the
include-history and deferred-concat mismatches plus fixture failures. Array
include/eval warning ingress, `serialize_precision` and wider raw-float Throwable
formatters remain required.

Suspended eval compilation now records genuine precision resume epochs, retaining
parser creation separately from later concat/name/fold conversion points. Image
refresh preserves escaped earlier arrays, callback allocations and enriched bound
class data; pending throw/exit still permit later compilation and publication.
Nine exact source comparisons retain c9a/f03 cuts. The325 supplied state controls
plus16 program bindings retain f03/193/da3 cuts; named compiler-handler
class causes require the real pending notice and exact eval entry. Actual266 key
scratch now seeds source creation precision separately from live AST evaluation;
one new exact source and28 supplied checks plus1 binding pass at75173 in strict
SL. Both AL timeouts and the stale-wrapper rejection remain zero-credit. The
actual318/GEN parent retains269 modules and passes SL at66453, without renewing
source/state cuts. Original compiler/fixture failures and the former Unsupported
frontier remain in the
[precision ledger](coverage/semantics/precision-review.json). Wider callback cause
selection, formatter/provider interactions and complete core remain required.

Global constant callables271 now evaluate static/no-use Closures and function or
static-method FCCs before registration. REAL lexical/called scope comes from the
immutable source entry, including inherited include/eval scope; NAMED functions
remain unscoped. Exact full declaration/value flow authenticates installed values,
while USERCONSTANTS own them. Duplicate-warning continuations retain candidates
and their pre-callback lookup prefix, preserving the original binding on return
or throw. Raw-trait METHOD notices precede allocation and resume the captured
target. Nine exact source agreements retain414/5d0/92ff cuts; seven source-derived
AL programs/341 premises pass at21b5, checking scopes, transfer forgeries, retry,
reentry and genuine collection. Original compile/interpreter failures remain
zero-credit in the [ledger](coverage/semantics/deferred-static-defaults-review.json).
Per-child alias proofs now retain the exact donor and table prefix for each
completed read, so first registration can preserve an earlier fallback without
freezing later operands. Installed rows and duplicate continuations retain only
nonowning lookup facts. Three fresh source agreements pass at9619d2f57; mixed90
and retry94 AL premises pass at4262f787e, checking distinct selections, failed-unit
transplants, candidate retirement and genuine constant roots. Their compile and
fixture stops remain zero-credit.

Global constant NEW283 now preserves raw user-instance identity through prepared
argument and constructor phases. Every argument is evaluated, including ignored
no-constructor arguments, before constructor access; immutable file/eval entry
scope governs self/parent and private access. Nonowning receipts distinguish
incomplete escaped allocations from successfully ended construction, while
USERCONSTANTS and real GLOBALS/CV owners retain values. Three exact source tuples
pass at17c12b379; argument103/inherited84/retry87 AL premises retain041ce1/00578e/
bc44da cuts (274 total). The optional-tuple and restored-MAIN fixture failures
remain zero-credit. Frozen duplicate/argument-abort destructor originals await
genuine eager release. Cold no-constructor table work adds source1 atd2fb and80 AL
premises ata1e14a2b4: the instance-template warning precedes ignored arguments,
with no allocation until table completion and no premature COMPLETE. A further
source1/81 AL premises at97dab9f8b check failed table work before allocation and
fresh declaration/NEW identities on same-text eval retry. The earlier cold fixture's three
elaboration stops and one slice-length execution failure retain zero credit.
Internal/Throwable/autoload and wider object/constant producers remain
required; full core stays open and return verification stays paused.

Deferred runtime class-link failures275 now replay the held notice prefix and
primary compiler fatal, retaining the genuine inner eval/include trace row.
Source history rederives the failed binding and exact rollback; the immediate
report requires its authentic failure/caller record. Seven exact source agreements
pass at4293f196: runtime eval, constant and include counterparts plus the four
remaining258 eval originals. Independent source-derived eval81/constant83/include84
checks pass in strict SL at the same semantic cut, proving public/history/owner
admission and retirement while rejecting forged failure rows. Earlier236 cuts
retain their identities; full traversal and core remain open.

Temporary fake/METHOD `Closure::call`268 now checks the actual selected scope,
executes user bodies and finite getters, preserves source statics and creates
durable children with only the genuine new receiver owner. Binding warnings
precede inner-name errors; reference warnings precede fresh-cell allocation and
retain frozen values through callback writes, allocations and throws. Private18
normal source agreements retain e2ce; totalized task guards at9342 pass AL252 and
five owner/frame/throw fixtures317 runner conditions (302 supplied checks and
15 reached setup; author106/independent211). The exact original factory/default
source1 and AL258 pass the actual0ef union at975fac. The final8350 parent keeps
its separate GLOBALS and cached constant-NEW routes through focused source review.
The [ledger](coverage/semantics/temporary-fake-call-review.json) preserves mixed
cuts and the original fa90 setup Unsupported with zero agreement. Unpacking,
further internal consumers and REAL temporary-current lifetime remain required;
return verification stays paused.

Global W/RW warning continuations269 now preserve caller-CV name rereads and
captured Array names through updates, compound assignment and nested array ingress.
Returning missing fetches detach callback-created constrained/reentry aliases into
a fresh null binding; throws preserve callback writes and skip later RHS demand.
Compound walks follow eager RHS computation while simple RHS CVs stay delayed.
Author9/224 and independent12/273 share four originals, giving17 unique private
programs/497 assertions ated6/baba/6e8. One actualc906 source at604958 retains private
Owner/Child selection, fresh-global detachment and live caller/static17. The
[contract](docs/semantics/SOURCE-GLOBAL-WRITES.md) and
[ledger](coverage/semantics/globals-write-review.json) preserve the original
multiline Unsupported and corrected native predictions. Container276 above adds
initial W/RW storage; wider GLOBALS/memoized consumers remain required.

Early-eval declaration diagnostics236 now suspend authentic compilation at each
publication, including generic warnings before class publication. Handler throws
and exit retain later publications while skipping the unit body; user fatals stop
compilation and retire its owners before shutdown. Pending-exception formatting
preserves the primary compiler fatal through source writes, conditional class
publication, throws, exit and nested hard eval/include compilation. Diagnostic
arguments retain physical source provenance and callbacks retain actual caller
scope/trace. Compact source plans, chronological prefixes and one real task owner
authenticate the continuation; hidden wrapper/branch claims are rejected.
Twenty-one distinct source agreements keep their separate966 through9b2 cuts;
the affected nested/file source2 also passes at3bd68993a. Authored USERfatal48
and independent pending65/handler36/Iterator28/nested42/Throwable30/formatter45
pass at ea077. The corrected nested-fatal57 passes at3bd68993a. File-public43
and history-retirement49 pass in strict production SL mode on semantic c9e6
(private43b); their union retains all59 original file predicates.
Equivalent call-admission deduplication at c9e6 retains the mandatory source
history/function-table proof; a new coherent descriptor-forgery24 check passes.
The maintained runner's optional `--sl` flag selects that mode only for the two
file phases. Actual23c composition source2 at5cf39c0dd confirms live dollar-curly
warning effects and later class publication before request destructors after exit.
The final1d4f union preserves261 object-cast frame cleanup,265 callable receipts
and267 keyword NEW source guards; these source2 results retain their5cf cutoff.
One actual261 source at0ef99 confirms a fatal formatter's NaN object cast keeps
its value while the recorded conversion warning stays suppressed.
Original failures, AL timeouts and fixture corrections remain
outside Git with no failed-run credit.
[Contract and maintained tests](docs/semantics/ITERATORS.md).

Accepted230 retains runtime/file prototype order, source erasure, direct
restoration, duplicate notices and ReturnTypeWillChange. Runtime classes publish
before callbacks; early file units publish fully before ordered delivery. Its
source19/independent11/affected trace3 and four state phases53/35/25/23 retain
their recorded cutoffs. Actual3b622 composition source3 at e1a654 retains physical
trait diagnostics, live argument/display state and effectful internal defaults.
The former four early-eval Unsupported controls had zero agreement credit.

Ordinary named keyword NEW267 now resolves self/parent/static in the actual
caller before class work and arguments. Inherited constructor entry uses its
immediate owning caller; service-unit main code follows persistent scope entry
bindings. Known function scope errors compile; main, eval, trait and Closure
errors remain deferred. Source18 normal/4 compiler and reached cold57/recursive44
plus corrected eval53 pass at91dc. Actual23c/264/257 composition at9b8 passes
private self/static and current identity after null-binding resets called scope.
Original preparation/eval-fixture failures remain in the [ledger](coverage/semantics/named-keyword-new-review.json).
Cached constant METHODs now admit compiled/named keyword NEW through exact265
receipt authority. One new source and38 reached premises pass at0da3, including
unrelated lexical/called scope and history after plain-clone retirement.
Wider autoload consumers and complete core remain open; returns stay paused.

Trait-constant callables265 retain the first shared AST method/function target,
while named/method captures record each current publication prefix and METHOD
captures select fresh called classes. REAL Closures use their own declaring scope.
Exact receipts authenticate
cached private targets after a real partial initializer failure; wrapped/plain
makers can create children with lexical/called scope and private defaults after
maker retirement. Successful constant caches own their values; history owns none.
Three source agreements and58+54 AL premises pass at4e2d; the unchanged122-premise
constructor guard passes SL at733 in27s under the same120s cap. AL timeouts remain
zero-credit in the [default ledger](coverage/semantics/deferred-static-defaults-review.json).
Compiled/named keyword NEW uses that exact cached METHOD authority through267
above; wider callable/default behavior and complete core stay open.

Non-object casts261 now populate stdClass scalars/arrays, share all-string tables
through genuine COW and fast clone, and preserve numeric round trips, alias type
owners and active foreach cursor history. NaN warnings retain the allocated object
and original operand location; NUL-key notices retain a nonowning TABLE/SERIAL
marker through callbacks and delayed reference promotion. Raw undefined buckets
keep distinct read/isset/copy/comparison behavior. Twelve full source comparisons
retain 3a/82c/b0 cuts; one actual 8ada/a4fc composition gives the first agreement for
the former251 native-only multiline cast holder. Four source-derived groups pass
208 premises at b0, with original fixture stops preserved. The
[cast ledger](coverage/semantics/object-casts-review.json) separates these cuts,
two retired-pointer originals and a longer companion timeout (zero agreement).
Actual257 destruction/frame/pruning hooks are preserved separately. Wider
raw-undefined consumers, lifecycle/GC and callback contexts remain required.

Request-stage destructors257 now repeat reverse direct globals and then scan
reusable live store handles. Once marks, bailout/failed-constructor suppression,
private visibility, nested USER calls and ordered outgoing slots retain exact
owners. Caller restoration precedes compiled CV cleanup; extras precede receiver
release. Pending throws replace and chain through remaining slots. Ignored
by-value ordinary and automatic-constructor returns release in the live callee before
locals; C destructor helper returns remain retained. Eval/include continuations
keep source history. Explicit request facts preserve startup argc order; absent
facts keep the original environment Unsupported, and dead CVs remain admissible.
Author78 source agreements and seven/303 reached assertions retain distinct
cuts; independent64 agreements, two Unsupported controls and12/548 assertions
retain theirs. Actual253/259/260 routes and final SL/AL253 pass on the preserved
a4fc parent;264/262/266 preservation is source-reviewed without old-cut renewal.
[Contract](docs/semantics/SOURCE-DESTRUCTORS.md),
[author record](coverage/semantics/destructors-review.json),
[independent ledger](coverage/semantics/destructor-review.json).
The earlier eager/prequeue Unsupported controls retain their original257 cut;
270 now supplies those releases. GC, output buffering,
queue freeing and final cleanup remain required; complete core stays open.

REAL binding264 now resolves scope before ordered static, `$this`-unbind and
internal-scope warnings. Genuine handler continuations retain selected reasons
through callback mutation and throws. The function's own compiled entries supply
`USES_THIS`, including dead eager literal-name uses and excluding nested bodies
and runtime-name folding. Valid null bindings copy REAL statics, retain reference
captures and reset called scope; explicit null scope removes class permission.
Twenty normal source agreements retain separate2312606/ed1d5 cuts. Five genuine
owner/frame cases pass289 conditions (author113, independent176).
Actual601312 composition at2cb72 passes AL251 and one cached trait-property
METHOD child source: null bind/clone retains private default permission and exact
current identity after makers retire, with called scope reset to lexical Owner.
Original classifier nondeterminism, the combined45-second timeout and fixture
elaboration stop remain separate in the
[binding ledger](coverage/semantics/real-closure-binding-review.json).
Temporary-current and internal API consumers remain required; returns stay paused.

Ordinary dynamic NEW260 evaluates string/object selectors once and captures the
class before arguments, class-table updates and constructor dispatch. Parser
literals, later compiled keywords and runtime names keep distinct scope/error
behavior; fetch/access lines stay separate from constructor call lines. Immediate
caller records authenticate recursive constructors; completed cold-table history
retains nonowning scope after a rebound Closure retires. Source26/compile3 and
retired83/recursive46 pass at0091; affected source3 at a65 and new2 plus
contexts51/rebound45 at3f817 retain separate cuts. Actual6af8/252/263 composition
at26fba passes cached trait METHOD/clone source1 and34 scope premises with lexical
HostA and unrelated called HostB. The [ledger](coverage/semantics/dynamic-new-review.json)
preserves original failures and preparation-only checks. Ordinary named keywords are covered by267; autoload and complete core stay open.

Cached property method callables (module263) now create source Closure children
with authentic lexical scope and a separate, potentially unrelated called class.
Copied full method/receipt authority survives wrapped or plain-clone maker
retirement without owning those makers. Static and receiver-free nonstatic
children, child clones and private `new self` defaults preserve these scopes.
Two normal source agreements pass at aa899; static105 premises pass at9ae61 and
default65 atb8d10. Original fixture parse/elaboration stops remain zero-credit in
the [default ledger](coverage/semantics/deferred-static-defaults-review.json).
Wider transformed callable creation contexts remain required; complete core and
paused return verification remain open.

Current Closure/binding253 returns the exact immediate ordinary Closure and
preserves existing-object `__invoke` capture identity. Transformed fake bindings
keep frozen permission and source statics while owning only their new receiver;
internal REAL copies and returned children retain genuine scope after makers
retire. Static API receivers add no argument-evaluation owner. Selected warnings
preserve scope/error order and unwind callback writes. Source24 normal at distinct
cuts, nine owner/frame fixtures444 conditions (author214/independent230), affected
older identity3/37 and private AL237 pass. Actualc139 preserves246 modules and
passes AL247 plus one inherited property-default source: REAL current/`__invoke`
identity and private fake binding/clone permission, called scope and shared statics.
Original compiler, source and fixture failures,
the global-constant Unsupported control and native-only controls remain separate
in the [ledger](coverage/semantics/closure-current-binding-review.json).
The [contract](docs/semantics/CLOSURE-CURRENT-BINDING.md) keeps temporary-current
escape and further API/keyword consumers required. REAL warning/unbinding is
covered separately by264 above. Return verification stays paused and complete
core remains open.

Literal named-static current FCC capture now reuses the receiver-free API identity
without changing CURRENT or frames. Three native originals/one direct at 16b and
two repaired captured sources at 257/375 agree; separate body (206) and named (241)
gates validate the immediate ordinary caller, distinct picked-null/returned-null
retirement and named Error/caught-null cleanup (425 genuine/derived plus 22 controls).
Four failed full fixtures and one localization cut retain 0. Exact maintained
source/renderer/dispatch relocation preserves all 26 legacy fixtures/counts by pure
comparison; no runtime renewal. Wider captures and argument-retirement forms stay
open in the [ledger](coverage/semantics/closure-current-binding-review.json).
Exact current composition at `90d4caa2` over `c3fbb257` (375 modules) passes all
447 premises: compiler 5.171 s, initialized SL 53.584 s. Common control/storage
interfaces are checked; original body/named and source/native cuts retain their inputs.

Simple class-CV `$class::getCurrent(...)` capture now prepares canonical Closure
before minting the API; a later `stdClass` write leaves its selected current-body
identity intact. Native2/literal1 at 05679 and repaired computed1/state166 at
1cb70154/375 pass (152 genuine/derived plus 14 controls), binding raw VARIABLE,
prepared class, genuine mint, real class write and existing owned CONFIG/result.
Original Unsupported remains 0; wider CURRENT capture expressions and source7
stay open. Exact maintained relocation needs no runtime renewal; old lifetime and
bridge cuts retain their evidence in the same ledger.
Actual375 over c9377bec passes the preserved166 compatibility gate at 4dd91e3ce
(algo 5.168s / initialized SL 30.134s), binding reached EMIT BASE cleanup
and shared storage/pruning; guarded Iterator/getter/factory/history paths are
absent. Private/native/source cuts remain frozen.

Named-class evaluated CURRENT members now authenticate SCOPED_NAME capture
and freeze `getCurrent` after member evaluation. The concat original agrees at
db0ef348/375; state242 passes (223 genuine/derived plus 19 controls), binding
the actual request carrier/index, registered mint, two real operand writes and
unchanged owned CONFIG returning the exact immediate body. Native2/literal1 and
original Unsupported0 retain f98; wider class/combined forms and source7 stay open.
Exact maintained relocation preserves old dispatch without runtime renewal.
Its 376-module join over c999a69f passes preserved242 at 7a205094
(algo5.175s/initializedSL33.386s), checking reached emission/storage/pruning
compatibility; guarded getter/reference/Iterator/factory routes stay disjoint.
Private source/state cuts retain their revisions, without renewal.

Evaluated nonnamed classes with literal CURRENT members now reuse prepared
canonical Closure and existing source/task authority. The concat-class original
agrees at a6b8/375; state240 passes (220 genuine/derived plus 20 controls), binding
the real request producer, raw/prepared class, registered mint, two later operand
writes and unchanged owned CONFIG returning the exact immediate body. The two
native originals, literal control and original Unsupported0 retain 160b; combined
forms, wider evaluation evidence and source7 stay open. Exact relocation needs no
runtime renewal.
Its 376-module join over 41da6ffb passes preserved 240 at 88c9d696
(algo 5.488s / initialized SL 36.655s), binding class preparation to current
replay/storage normalization. Replay clears the already empty error handler;
file notices, typed property getters and conditional factories are absent.
Private source/state cuts remain frozen.

Evaluated nonnamed class and computed CURRENT member now reuse the existing
internal Closure task certificate. The both-concat original agrees at bf0e/375;
state353 passes (328 genuine/derived plus 25 controls), binding two real producers
at distinct request indexes, canonical saved Closure/member authority, registered
mint, four operand writes and unchanged owned CONFIG/immediate body result.
Native2/literal1/original Unsupported0 retain 5c25; wider evaluation evidence,
object captures and source7 stay open. Exact maintained relocation preserves old
dispatch without runtime renewal; old lifetime/bridge cuts remain separate.
Current composition over bc93c428/377 passes the preserved353 gate at 9e0ce
(5.492s compiler, 41.563s initialized SL). It binds reached shared30/40 storage
and operator paths; integer warning, WeakMap key-pin, reference-return, hook and
nested Do factory routes are guarded out. Source/private renewal stays zero.

Ordinary object-form literal CURRENT FCC now authenticates the borrowed receiver
source and live Closure before minting the same receiver-free API. Native2/literal1
at 6fdb and affected object1/state200 at 59ef/375 pass (180 genuine/derived plus
20 controls), binding genuine METHOD_PREP/resolve/mint and the real selector-null
quiet release before its weak producer. Existing owned CONFIG returns the exact
nonnull distinct immediate body; original Unsupported stays zero. Computed/nullsafe
object forms, name/argument retirement, wider receiver evidence and source7 stay
open. Exact relocation needs no runtime renewal; old lifetime/bridge cuts remain
separate.

Object CURRENT200 also passes on the exact e1af12fa current parent / 378 modules
with unchanged fixture (180 genuine/derived plus 20 controls), binding shared
task/storage and selector quiet-release/WeakReference cleanup. Compiler 5.280691 s
and initialized SL 39.217533 s pass strict output/stability/reaping; guarded dynamic
source/end-marker, reference-return and class/operator routes are absent. This
current compatibility check adds source credit 0/private renewal 0; prior cuts stay frozen.

Ordinary object-form evaluated CURRENT members now authenticate METHOD_NAME
source/CODE and the original borrowed receiver before the same receiver-free mint.
Native2/literal1 at 054f and affected source1/state315 at 1f4b / 375 pass
(293 genuine/derived plus 22 controls), binding real get+Current request production,
two later operand writes and selector-null quiet release before its weak producer.
Existing owned CONFIG returns the nonnull distinct immediate body; original
Unsupported remains zero. General member admission is distinct from this concat
witness; nullsafe/name-argument retirement, wider evidence and source7 stay open.
Exact relocation needs no runtime renewal; old lifetime/bridge cuts stay separate.

Member CURRENT315 also passes on exact 2288777932a / 378 modules at 24a4f260
(compiler 5.181748 s, initialized SL 43.825590 s), preserving the fixture
and its 293 genuine/derived plus 22 controls. The request-carrier/METHOD_NAME,
receiver selection and quiet weak-release path bind current task/storage routing;
source-static identity, by-reference destructor, typed getter, WeakMap freeing
and integer warning routes are absent. Source credit 0/private renewal 0; prior
cuts remain frozen.

Captured CURRENT calls now pin the resolved selected API in CONFIG during
ordinary argument evaluation; static receivers remain borrowed. A genuine helper
api-null write leaves the captured API held versus the direct API gone before
the weak producer. Consumed arity-error CONFIG retires the API while the ordinary
body remains current, then caught-null prunes the scalar-only error graph.
Two native originals are retained; unchanged direct source at 7e and affected
captured source at b5f/375 each agree with their own oracle. The 527 state premises
pass (488 genuine/derived plus 39 controls). Recorded zero-argument bridges (54/57)
validate the new tag/owner and unchanged current identity and named Error without
renewing old 447. Three syntax failures remain 0; exact
maintained relocation requires no runtime renewal. Current 333bd/375 composition
passes the preserved 527-premise compiler→initialized gate (5.530/92.496s), covering
reached emit cleanup and shared type/guard changes; source/private renewal 0. Wider
forms and source7 remain open in the [ledger](coverage/semantics/closure-current-binding-review.json).

Literal named-static `Closure::bind(...)` capture now reaches the existing handler.
Authentic dynamic-call receipts retain copied internal scope/function/receiver facts
after the API and original body retire; the bound Closure and returned cell retain
the receiver at distinct cleanup stages. Native2/direct1 at 22c4, affected captured1 and
state289 at 1f58/375 pass (269 genuine/derived plus 20 controls). Original Unsupported
and the first interpreter failure remain 0. The API main cell stays live across
args in that original cut. Exact e687/375 composition at 82389 passes the preserved
289 compiler/initialized-SL gate; current source/private renewal 0.
Captured BIND now uses the existing owned CURRENT tag:
a third-argument helper's API-null write leaves saved CONFIG_SEND as its sole
owner, while the static control observes it gone. Consuming CONFIG releases the
API before the next weak read, preserving the copied binding receipt and distinct
source-body/receiver retirement. Native2/direct1 at 3352, repaired captured1 and
state413 at 5ecda/375 pass (375 genuine/derived plus 38 controls), including only a
34-premise recorded bridge for changed old CONFIG authority. Original 289 remains
frozen; the initial global-table fixture failure retains 0. Wider forms remain
open; exact relocation needs no renewal. Exact 83186897/375 composition at 8a9e
passes the preserved413 compiler/initialized-SL gate; current source/private
renewal 0. See the [ledger](coverage/semantics/closure-current-binding-review.json).

Simple class-CV BIND capture now resolves `Closure` and freezes that selection
before the class cell changes to `stdClass`. Native2/literal1 at fee3 and repaired
computed1/state161 at 275fc/375 pass (148 genuine/derived plus 13 controls), binding
the raw/prepared class, genuine mint, class write and existing CONFIG/receipt.
Original Unsupported, elaboration failure and raw-mint fixture failure remain 0;
wider class expressions stay open in the same ledger.

Exact 1310460b/375 composition passes preserved state161; native/source/private
cuts are not renewed.

Literal-class method-CV `Closure::$method(...)` BIND capture now resolves string
bytes, including the reached interned carrier, before minting the API. A real
method-cell write to `getCurrent` leaves its selection and binding receipt intact.
Native2/literal1 at 836b and computed source1/state169 at 48fee/375 pass
(150 genuine/derived plus 19 controls), with recorded checked-program reuse and
no frontend or old lifetime renewal. The original Unsupported, failed first
repair and guard diagnostic retain 0; wider expressions stay open in the same ledger.
Exact 4a489b79/375 composition passes preserved state169; native/source/private
cuts are not renewed.

Combined simple class/member-CV `$class::$method(...)` BIND capture now has
source-authenticated internal Closure task authority. Genuine class evaluation,
member carrier resolution and handle-normalized mint precede separate writes to
`stdClass` and `getCurrent`, which preserve the API and existing CONFIG/receipt.
Native2/literal1 at 1cb688 and repaired computed1/state237 at 06e6/375 pass
(209 genuine/derived plus 28 controls). Original Unsupported and initial fixture
elaboration failure retain 0; the corrected state reuses its checked program with
frontend0. Wider expressions remain open; exact maintained relocation needs no
runtime renewal. See the same ledger.
Exact 592735d4/375 composition passes preserved state237; native/source/private
cuts are not renewed.

Named-class computed-member BIND capture now uses the existing evaluated member
source/task authority. Genuine concat operands produce a request string at the
actual STRINGDATA index, then minting and separate operand writes preserve the
selected API and its CONFIG/receipt. Native2/literal1 at 64be and repaired computed1
and state233 at 4ec/375 pass (214 genuine/derived plus 19 controls), reusing recorded
checked packets after a source-name fixture-origin failure0. Handler/tag/ownership
are unchanged; wider class/combined expressions and source7 remain open. Exact
maintained relocation needs no runtime renewal; see the same ledger.
Exact 409a37be/375 composition passes preserved state233; native/source/private
cuts are not renewed.

Evaluated nonnamed class expressions with literal BIND members now reuse existing
normalized class/source authority. The concat-class witness produces a genuine
request string, prepares canonical Closure and mints before separate prefix/suffix
writes preserve selection. Native2/literal1 at a303 and repaired computed1/state236
at 43fd/375 pass (216 genuine/derived plus 20 controls). Handler/tag/receipt and
old cuts remain unchanged; combined expression capture and wider evaluation
evidence stay open. One preserved current236 compatibility gate at f890/661bf
passes the reached shared EMIT/storage/pruning seam (5.249/60.095s), with current
source/private renewal0. Exact relocation needs no runtime renewal; see the same ledger.

Evaluated nonnamed class and computed BIND member now share the internal Closure
task certificate. The both-concat witness reaches two distinct request-string
producers, canonical saved Closure and genuine mint before four separate operand
writes. Native2/literal1 at e360 and repaired computed1/state347 at 53a19b/375 pass
(322 genuine/derived plus 25 controls), with unchanged CONFIG/receipt and shared
authority controls. Wider evaluation evidence and source7 stay open. Actual de65
composition at 68d7 passes the preserved347 gate (5.224s compiler, 71.244s
initialized SL); native/source/private cuts retain their original revisions.
See the same ledger.

Object defaults (module252) now create static/no-use source Closures and
function/method callables in genuine declaring scope. Requested-class templates
share their object values with instances and preserve exact successful bindings
across late inheritance, retry and reentry; arrays copy containers and share
embedded objects. Nonowning receipts/copy certificates reject foreign transfers
and survive source retirement, including plain clones. Nine normal source
agreements retain 0d0d (first2)/0e472 (other7); six programs/335 premises retain
0e472/72d5.
One actual238 trait-import source and98 premises pass at a502: cached private
method/function targets keep their first authentic lookup, while each property
uses its own publication prefix and fresh called class. All original compiler,
permission and fixture-seek failures remain separate in the
[default ledger](coverage/semantics/deferred-static-defaults-review.json).
Other object/default producers and consumers remain required; complete core and
paused return verification remain open.

Nested coalesce-assignment262 now owns quiet row values on defined CV-rooted
array chains while the memoized write walks current storage. Computed keys run
once; variable keys stay live. Prefix copy-abort creates a genuine temporary,
while final-key abort skips a delayed RHS CV. Late keyed RHS warnings follow
entry acquisition, write captured null through handler throw and recheck a live
typed cell at the restored emitter. Author9/233 and independent11/277 share two
originals, giving18 unique private programs/510 assertions atf9/2b65/cf7. The
independent tail check found and verified the late-dispatch double-pop fix; only
five affected sources and84/76/76 states were renewed. One actual6013 source
at9ac retains private Owner/Child selection, quiet row17 versus new parent13 and
live caller/static17. Original fixture/loader failures and native prediction
corrections remain in the
[nested coalesce ledger](coverage/semantics/nested-coalesce-review.json).
Wider memoized containers, wider GLOBALS consumers and earlier
container/string/object producers remain required; complete core and paused
returns remain open.

Nested unset and append255 now suspend defined CV-rooted array walks after key
and computed RHS evaluation. Intermediate unset separates before conversion,
latches missing keys as null and skips the next deprecation if the table dies;
ordered float notices share one protection. Final unset keeps its distinct rules.
Append copy-abort retains a genuine null temporary and the computed RHS. A late
missing RHS captures null, checks the old table's liveness, and can insert into a
rebound real child even before propagating its handler's exception. Key-handler
throws still stop the append and preserve typed destinations. Author6/247 and
independent18/356 share the retained expiry original, giving23 unique private
agreements at7ee/d281/643/75c8. One actual0b private-FCC/called-class source passes
at223 with abort/TEMP and live typed caller/RHS cells. Original overlap and
corrected native/source predictions remain in the
[tail ledger](coverage/semantics/dimension-tail-review.json).
Wider memoized containers, wider GLOBALS consumers and earlier
container/string/object producers remain required; complete core remains open.

Legacy dollar-curly compiler notices258 retain the direct/computed grammar flag
through checked fresh printing and emit before child compilation with its real
path and the preceding compiler line. Main/include delivery reuses230 whole-unit
publication, genuine private emitter scope, live mask/display fallback and throw
cleanup. Five exact source/profile comparisons, SL242, 24 syntax/encoding profiles
with320 checks and37 compiler/certificate premises pass atfa084. Actual256 parent
preservation keeps243 modules without renewing those cuts. Original compiler and
fixture parse stops stay zero-credit in the
[ledger](coverage/semantics/dollar-curly-review.json). The early-eval effects pin
passes with236 at5cf39c0dd; the other four originals first pass with275 at4293f196. Wider
interpolation and file-observer gaps remain open;261 separately closes the old
non-object-cast holder pin at its recorded cutoff.

Dynamic object `::class`256 evaluates one child and returns its real class name
without a string cast. Eager parser concat keeps literal/keyword behavior; later
compiled constant operands reject. Embedded undefined-CV callbacks keep captured
null, including a throwing handler retained as the new TypeError previous chain;
dimension throws keep ordinary abort behavior. Source20 and seven full compiler
rejections pass at026ba, with165 reached premises in43+70+52 groups covering actual
lines, task/source admission, temporary retirement and read/exception ownership.
Unused preparation has zero execution. Original native prediction failures and
historical245 Unsupported stay preserved in the
[class-name ledger](coverage/semantics/object-class-name-review.json). One actual251
interpolation source atf626 on4208 retains callback receivers through global-slot
replacement and sees the later mutated operand. Actual247/251 routes are preserved;
complete core remains open.

Ordinary string interpolation251 now follows effective CAST/FAST_CONCAT/ROPE
order. Two-part fetched temporaries survive left callbacks; later variable
conversion reads live borrowed slots. Undefined direct CVs keep singleton null
but reread modes2+ without a second notice; callback-created arrays retain no
invented owner. Real Stringable/array callbacks, throwing cleanup and compiled
multiline lines preserve exact source/consumer/finish markers. Nine exact source
agreements and SL237 pass at88f; affected AFTER guards and111 distinct premises
pass ata7 in six unchanged groups with25 repeated setup premises. Original
fixture stops, full/fast timeouts and native-only non-object-cast line probe keep
zero credit. Actualcde/247 preservation retains240 parent modules plus251 without
renewing those gates. [Contract](docs/semantics/SOURCE-INTERPOLATION.md) and
[ledger](coverage/semantics/interpolation-review.json) retain these cuts. Wider
interpolation producers/source contexts, early eval compiler notices and affected
original dynamic-file observers remain required; complete core and paused return
verification remain open.

Ordinary Throwable reception250 now suspends weak-null/lossy warnings and
Stringable parsing for NEW and explicit inherited/scoped constructor calls.
Ordinary named-send priority stays intact; strict null/objects reject without
conversion. Successful string casts rewrite sent slots and retire old temporary
objects; integer trace arguments stay raw and fields commit only after all
formals pass. Private handlers, method retirement and recursive same-site calls
retain their own owners and traces. Source17 passes as2 at5e828 plus14+1 atb6cac;
141 ownership premises pass in71+70 partitions, and recursive29 passes at e6f71.
Thirteen repeated dependency bindings add no behaviors. Original overlap,
consumer-forgery and fixture failures plus the whole141 timeout stay preserved in
the [reception ledger](coverage/semantics/ordinary-throwable-reception-review.json).
Actual246 template/generic-EMIT composition1 at98c passes on ab5d; latest238/249
are preserved on e2e6 separately without renewing private gates. Complete core
remains open.

Callable default/variadic reception248 now suspends keyword/compound lookup in
actual receiving frames. Deferred class-constant defaults, named-hole preparation
and supplied/variadic operands keep their distinct order and ownership. Referenced
methods/current operands remain live, including borrowed retired arrays. Failed
lookup checks constrained sources before slow scalar fallback; lossy warnings
freeze their result and dual-role objects still invoke Stringable. Source23 normal
and one literal compiler rejection retain758/018/060 cuts; two affected221 sources
stay separate. Author116, independent180 and affected old hole35 conditions pass
on018. Actual99a composition keeps created-child default scope after a foreign
capture retires and passes AL236. Original compiler/fixture failures stay preserved;
RuntimeException Unsupported controls have zero agreement. The
[contract](docs/semantics/CALLABLE-RECEIVES.md) and
[ledger](coverage/semantics/callable-receives-review.json) retain these cutoffs.
Other internal and user-return consumers remain required; return verification
stays paused and complete core remains open.

Stringable include/require operands now convert before resolution and once
checks, retaining the receiver through rebinding and nested eval. Callback writes
determine subsequent CWD/path lookup; throw completes without file facts or a
provider nonce. Failed-open handlers resume ordered warning phases, sampling the
second message after callback1 and preserving saved owners and zero-argument
file traces. Exit, fatal and compiler-stop drops retire only their actual warning
owner; frozen output precedes shutdown callbacks. Fifteen exact source agreements
retain dcb/49/b371/dc9/4639 cuts; 81 conversion, 148 grouped warning and 45 shutdown
premises pass at their recorded revisions. SL229/231/233 stages/init also pass.
Actual f410/245 preservation retains 234 modules without renewing those gates.
[The file operand ledger](coverage/semantics/file-operand-review.json) keeps
original observer, fixture, model and timeout failures. Wider interpolation,
providers/source contexts and request lifecycle remain required.

Anonymous Closure/arrow default NEW245 resolves self/parent using the genuine
receiving lexical scope, independently of called class and receiver. Rebinding,
temporary Closure::call, imported trait makers and missing-scope errors preserve
argument order and private constructor access. Source11 passes as3+6+2 at89fe;
owner172/recursive97 pass at2d7fd, including callback retirement, same-template
saved scopes and public task/source rejection. The original object `::class`
observer remains Unsupported with zero agreement; reduced instanceof observers
retain the default behavior. Original descriptor and fixture failures stay in
the [scope ledger](coverage/semantics/anonymous-default-new-review.json).
Actual239 child composition1 at1b593 passes after temporary maker/receiver
variables retire; the child retains its receiver. Latest231/234/230/242 routes
are preserved without renewed private gates. Ordinary Throwable effects are
covered by250 above; object `::class` is covered by256 at its separate cutoff.

Writable dimension keys242 stage defined mutable CV-array W/RW fetches through
undefined/null/float/NaN callbacks, nested acquisition, updates and direct
assignment/compound consumers. Separation precedes conversion; callback-created
copies abort acquisition while real cell aliases and moved sole keepers preserve
it. Borrowed inner rows retire with their parent; aborted intermediate fetches
retain one genuine unnamed null cell. Delayed RHS CV demand follows successful
conversion. Direct GLOBALS W and named reference sends preserve selected names,
fetch/mapping priority and callable/earlier-argument owners. Throws retain the
old typed destination and previous chain. Author11 source agreements/340 reached
assertions include two independent originals; independent15 fresh agreements/266
assertions retain those two separately, giving26 unique private agreements. One
actual3b622 composition source at6ae passes private-handler/called-class and typed
caller alias/introspection behavior. Accepted231/234 routes are preserved. The
[contract](docs/semantics/SOURCE-DIMENSION-WRITES.md) and
[ledger](coverage/semantics/dimension-write-continuations-review.json) retain
original failures, revisions and the current adapter reuse. Bounded GLOBALS RW
is covered by269 above; earlier container/string/object producers remain required.

Coalesce-assignment and final unset keys249 now stage defined direct CV-array
consumers. Quiet reads retain captured values and genuine memo operands; live CV
and computed keys keep distinct later demand. Actual read/write lines, copy-induced
write abort, delayed RHS suppression and retired-storage reinitialization are
preserved. Unset keeps ordered float protection and deletes callback-shared tables
by liveness while real cells survive. Author6/255 and independent10/216 share one
multiline original, giving15 unique private agreements at cfb/ab7. Two reduced
actualab5 trait-handler sources pass at f5/ea: private selection, Child called
class, read11/write8, copied-table abort/deletion and shared typed caller cells.
Combined and first reduced coalesce CLI60 timeouts retain zero agreement. The
[contract](docs/semantics/SOURCE-DIMENSION-EDITS.md) and
[ledger](coverage/semantics/dimension-edit-review.json) keep original cuts and
native prediction corrections. Nested unset and append are covered by255 above;
wider memoized containers and other producers remain required.

Shutdown registration231 caches callable selection, private/rebound permission
and copied arguments after all argument effects. Ordered callbacks run after
normal, exit and fatal/uncaught paths, including serviced compiler failures.
Append, handled throw, exit override, weak/default/variadic reception and internal
send-warning continuations preserve selected targets and native owners. Frozen
fatal diagnostics precede the queue; effectful default message warnings finish
the builtin cache before pending exception dispatch. Exact registered and
converted argument views remain separate. Existing176 user formatters retain their
C return-warning continuation after handled throws; actual237 freezes the live
display destination after formatting. Imported trait makers preserve using scope
and physical provenance after retirement. Fatal snapshots retain runtime/compile
severity before callback mask writes; actual240 default reception retains its
warning and Stringable owners. Author checks cover 29 source tuples and 149 state
assertions; independent checks cover 77 tuples and 559 assertions. Each keeps its
recorded revision, and production stages pass on the accepted fe51 parent.
[Contract](docs/semantics/SOURCE-SHUTDOWN.md),
[author/composition record](coverage/semantics/shutdown-functions-review.json),
[independent ledger](coverage/semantics/shutdown-function-review.json).
Keyword/compound ingress now uses the staged247 consumers below. Request-stage
destructors and ordinary eager releases are covered separately above; GC, output
buffers and queue release remain required.

Internal default reception240 now suspends weak-null and lossy integer warnings
through real error dispatch and invokes genuine Stringable callbacks in formal
order. Raw integer slots and rewritten string slots preserve internal constructor
traces, with the nearest saved owner through reentrant handlers. Exact source14
atd9 and builtin/fallback2 at7c pass; all185 reached premises at7c pass in unchanged
133+24+28 source groups under120-second caps. The original full185 timeout and
first-source interpreter overlap remain preserved. One composition source at
e7ec retains imported trait Stringable ownership and handler-mutated display
fallback after the filename global retires.
[The reception ledger](coverage/semantics/internal-default-reception-review.json)
records these cuts.
Ordinary constructor effects are covered by250; anonymous keyword defaults
are covered by245 above.

Trait method composition228 supports source use, nesting, precedence, aliases,
visibility/final and abstract requirements in Zend's publication order. Imported
class/alias identities retain physical body provenance, using/called scope,
defaults, static cells, captures, Closures, goto/eval and finalizer ownership.
Failed declarations restore unpublished tables; compile warnings and direct
trait-call deprecations retain their phases and callback ownership. The
[trait ledger](coverage/semantics/trait-methods-review.json) keeps the63 source
union, separate controls and252 conditions at their actual revisions, including
original failures. Actual227/232/239 composition adds nine source comparisons and
127 state premises at separate cutoffs: saved default constructors, cold selected
references, physical interface diagnostic files and imported-maker Closure scope.
Accepted233/237 routes remain preserved; the method checkpoint remains partial.
Ordinary class-owned abstract scoped calls now reject before argument evaluation,
with access errors preceding abstract rejection and concrete/trait-warning dispatch
unchanged. At `a962cef07`/354 over `aa8ebb4d1`, strict algo/struct pass3.719/4.673s,
one normal source and24 supplied clauses plus6 setup pass (5.220s). Nineteen
clauses check the genuine rejection and all four validators; five helper-only
clauses check access/nonstatic priority and concrete dispatch. Raw evidence
under current19 `.tools/` is `method-runtime-ciqhcicl`,
`closure-call-protocol-98d5klby`, `trait266-object-algo-u5b6vb34` and
`trait266-object-struct-e68x39kk`; baseline interpreter failure `4rvh0zjs`
retains zero agreement. Source-profile recording now preserves legacy argv/text
metadata and merges dictionary profiles; five representation checks pass without
semantic reruns. Wider method/core obligations remain open.
The reviewed355 projection `da11ceff4` over `035bbe2de` passes strict
algo/struct at3.719/4.823s, preserving current storage and bound-constructor targets.
Source1/24 bridge unchanged; raw compiler evidence is
`.tools/trait-fcc-failed-target-publish19/.tools/trait266-object-algo-vgui9wdk`
and `trait266-object-struct-p9t_dgxh` in the same directory.
Concrete nonstatic scoped calls now check access before a missing-receiver Error;
literal constructor calls bypass ordinary method access/abstract lookup, preserving
the constructor opcode arm. At `0c48e90f3`/356 over `4563a5bf9`, strict algo/struct
pass3.770/4.770s. Two new normal originals and34/20 supplied clauses plus6 setup
per case pass (5.269/5.319s):40 genuine clauses cover actual rejection/no argument
or allocation effects and all four global validators;14 clauses are helper-only
flag/source probes. The protected-call baseline mismatch `7bc1r1bg` remains zero
agreement. Raw current19 `.tools/` evidence is `method-runtime-y4klgpdm`,
`method-runtime-cn0j7jql`, `closure-call-protocol-pxes1q9x`,
`closure-call-protocol-5t_9yrp5`, `trait266-object-algo-4_69i9m4` and
`trait266-object-struct-z558o98n`. Prior abstract/failed-owner sources and states
are unchanged and not renewed; wider method/core obligations remain open.
Final356 projection `e65e35e2a` over `43890afab` passes strict algo/struct at
3.869/4.871s, preserving current assertion/Generator fields and dispatch.
Source2/34+20 bridge unchanged; raw publish19 compiler evidence is
`.tools/trait266-object-algo-l1ao1xno` and `trait266-object-struct-qztdz26_`.
Literal private constructor denial now precedes receiver compatibility even for
an unrelated active object. At `f515fd26b`/356 over `976a55232`, strict algo/struct
pass3.769/4.770s; one new normal original and24 genuine clauses plus6 setup pass
(5.773s), including the live receiver, exact rejection/no argument effects and
all four global validators. Current19 raw evidence is `method-runtime-seg05ujm`,
`closure-call-protocol-2hk6y4ou`, `trait266-object-algo-c7g31qwq` and
`trait266-object-struct-g7x1yycz`; original normal mismatch `2oh2ovm1` retains
zero agreement. Prior constructor/protected/retained-FCC cuts are unchanged.
Final356 projection `4366f4cae` over `02bff2460` passes strict algo/struct at
3.769/4.823s, preserving current storage-release guards. Source1/24 bridge
unchanged; publish19 raw compiler evidence is `trait266-object-algo-n0wtdaju`
and `trait266-object-struct-prg8u30p` under its `.tools/` directory.
Inherited private constructor errors now name the requested class while retaining
the declaring-owner access proof. At `4c3ece53d`/357 over actual `cbdb9d10a`,
strict algo/struct pass3.772/4.821s; one new normal original and28 supplied clauses
plus6 setup pass (6.123s):26 genuine clauses cover inherited selection/rejection
and all four globals, while2 helper-only clauses check the other Error consumer.
Current19 raw evidence is `method-runtime-svn8anig`, `closure-call-protocol-66s2dn57`,
`trait266-object-algo-zgrybsbw` and `trait266-object-struct-n2_844cu`;
original normal mismatch `s0r3su65` retains zero agreement. Prior constructor
cuts are not renewed; current375 collector/task fields remain preserved.

Ordinary scoped calls without an effective constructor now preserve Zend's
constructor arm: literal and folded names raise `Cannot call constructor`,
while computed names retain the undefined-method Error before arguments.
Two safe originals and distinct17+17 genuine SL premises pass at `fbab085b0` and
`87618a93e`/358, with no argument/allocation effects and all four validators.
Strict compilation passes; the original baseline mismatch and unreached computed
fixture remain zero credit. The corrected fixture uses the authentic live CV.
[The focused ledger](coverage/semantics/missing-constructor-review.json) retains
the separate cuts. Actual `d47aee7c3` composition at `6e462b5e`/359 passes strict
SL in 4.801s with zero runtime/source credit, preserving ASSERT/INI and GC/PROP
interfaces. Private sources/states are not renewed; wider method/core stays open.

Deferred trait parameter constructors now preserve their selected scope across
class-table initialization, including actual arguments, constructor choice and
source line. Independent actual1fa6af571 compiler gates, one fresh ordinary source
and38 supplied reached checks (6 setup) pass on the accepted40e3 foundation without
307. Genuine constructor allocation, capture retirement, durable table history and
post-retirement property iteration are covered. Earlier unpublished-FCC/count
originals keep their separate Unsupported/private results and zero transferred
agreement; no whole trait-family or paused return closure is claimed.

Trait data238 composes constants and properties before parent inheritance, with
scoped invariant types, evaluated pure compatibility, source keyword diagnostics
and full using-class member identities. Inherited statics share cells; explicit
child reuse resets the original default. Owning instance templates246 preserve
importing scope independently of the live caller and retain array copy-on-write.
The [data ledger](coverage/semantics/trait-data-review.json) records72 source tuples
and265 genuine state assertions at preserved cuts; four historical dependency
controls retain92 assertions and zero old-cut agreement. Runtime link fatals keep
native severity, reporting masks and declaration phase. Further effectful collision
evaluation, readonly storage and enums remain
required; this checkpoint does not close the trait family.

Raw trait static-property warnings254 follow lookup, access, table fill and typed
read priority. Retained source/root/member/mode resumes the live cell through
handler rebinding. Computed RHS values keep one store owner; compiled literals
also retain their pool owner. Late CV values remain delayed. Handler throws still finish
the actual write/update/reference opcode, while fetch-only reference promotion
aborts later assignment or call. Typed/Stringable conversion preserves pending
exceptions. Independent source33 (author6 subset) and six reached state groups286
pass at unchanged15155; preparation and incorrect owner assertions are retained
without extra credit in the [access ledger](coverage/semantics/trait-property-access-review.json).
Actual accepted core routes, including258, are preserved in244 modules without
renewing those cuts. Wider effectful collisions, readonly storage and enum
semantics remain required; the trait family stays open.

Trait collision recording259 compares deferred operands before typed table
conversion and records direct `E_STRICT` diagnostics during the source-owned
linking fold. Constants demand incoming then existing values; properties reverse
that order. Successful publication precedes live handler delivery; a handler throw
keeps the composed class. Later link fatals flush recorded diagnostics without
calling user handlers. The [collision ledger](coverage/semantics/trait-collisions-review.json)
retains14 source tuples (11 normal/3 PHP errors) and97 reached queue/callback
guards at their original cuts. Generic arithmetic/key recording now isolates
scratch handler/display settings and follows runtime key→value→insertion order
with checked AST lines. Five affected source comparisons (four new plus one
existing array neighbor),47 additional queue/array-owner guards and bounded
AL/structure checks pass. Private-final compile warnings now join the recorded
batch at concrete/abstract binding phases and remain handler-ineligible128. Four
affected source comparisons (two new and two128 mask neighbors) and43 genuine
alias/queue guards pass at their separate cuts. Module266 binds referenced
deferred constants in their real declaring scopes before strict comparison,
retaining typed caches between operands and distinct full import identities.
Ten normal source comparisons and201 unique cache/owner/lookup-chain guards pass;20 repeated setup checks add no coverage.
Module274 stops copied expressions at their first Error, default-flushes prior
diagnostics and renders the pending exception before a no-trace composition fatal.
Ten PHP-error sources and156 reached failure/cleanup checks pass, with ten separate
formatter checks. Held-primary reporting uses the genuine failed-class route275;
one actual source and112 reached replay checks pass at separate cuts. Direct and
two-hop cyclic lookup errors now use full imported identities; two PHP-error
sources and87 reached chain/cleanup checks pass at their separate cuts. Hard failed
links now retain dependency caches owned by already published classes and retire
unpublished import caches with their array owners. Three PHP-error sources and194
supplied reached restoration/history/ownership conditions pass; six generated setup
checks are separate. A source-rederived failure marker authenticates retention
without publishing the failed class. The same disposition after a reported
initializer Error adds three PHP-error comparisons and188 supplied reached
cache-cause/cleanup checks, with six generated setup checks separate. Failed raw
trait composition adds three PHP-error comparisons and68 supplied source-kind,
cache-owner and rollback conditions; three generated setup checks are separate.
Direct trait-constant denial precedes dependency evaluation. Held/open compilation
and wider object-bearing dependencies remain required. Published Closure/FCC
dependencies now use real initializer/binder contexts, source/receipt value flow
and captured-prefix array/DIM proofs. Seven source comparisons agree (five normal,
two PHP errors); five genuine reached source/flow/ownership groups pass409 supplied
conditions, with15 generated setup checks separate. Exact cuts and the retained
DIM-dispatch failures are in the collision ledger.
Real callable-initializer expression Errors, typed rejection and array-key TypeError
now use actual Throwable fields and demand traces, keeping completed nested caches
while retiring failed owners. Four PHP-error comparisons pass atf780; four reached
groups pass678 supplied source/context/registry/cleanup conditions atba2/d33, with12
generated setup checks separate. The retained handler graph survives scratch cleanup.
Cross-file constant collision typed demand now preserves the executing class file,
physical fetch line and genuine constant-expression frame. Two PHP-error comparisons
and one reached group/139 supplied conditions pass, with five service/setup checks
separate. Wider initializer contexts and unpublished-owner FCC births remain required.
Traits stay partial.

Modules290/297/299 preserve source/collision/prefix authority for unpublished REAL
Closure births, retire failed import owners while retaining only dead receipts,
and reserve the earliest fatal trait class name before later binding or autoload.
Returning link Errors permit retry. Original author/reviewer cuts and failures stay
separate in the collision ledger. Actual313 at `cc9411c1e` over310/`064d382d` passes
strict algo/struct and one new pinned REAL/default-constructor original, with exact
`H;CALL;CTOR:7;C:C:C;AFTER;C:C;` at unchanged45/55 limits. One genuine strict-SL group
passes46 supplied conditions plus6 terminal-aware setup clauses: actual REAL
birth/cache/receipt, selected constructor7 allocation and capture retirement with
the REAL authority still live. The current constructor/default/Generator/Fiber/source
fields are retained. Module307 now reconstructs exact source method copies at the
first target's declaration prefix to validate failed FCC births after rollback.
Dead receipts and pure history replay preserve the first target without publishing
its owner or admitting a live callable. Focused source2 retain exact output/error
bytes and exits; strict-SL failed-import53 and equal-scope34 supplied conditions pass,
with12 setup clauses separate. Raw evidence is under the private
`.tools/trait-selected-constructor-current/.tools/`: `closure-call-protocol-y5x1pwdf`,
`closure-call-protocol-v81oh3gj`, `method-runtime-87l_y5f5` and `method-runtime-a2gromik`.
The first failed source's recorder label is corrected from static rejection to
runtime PHP error; its already completed duplicate adds no coverage. These focused
cuts bridge to the reviewed current composition without renewal. The322 cut at
`4c03c177d` over `f89fbee74` passes strict algo/struct at3.369/4.270s and a genuine
active DEFAULTRECEIVE/TYPE checkpoint with26 supplied conditions plus6 setup clauses
at36.874s. It preserves canonical code/default/return/static identity and rejects a
forged receive owner before the actual old-U constructor Error; no whole-source or
unwind coverage is claimed. Current raw evidence is under
`.tools/trait-fcc-parameters-composed-19/.tools/`: `trait266-object-algo-2riubhjo`,
`trait266-object-struct-k27i1h7p` and `closure-call-protocol-yveph8_d`.
The323 composition over EX338 tightens receipt access to the unfixed exporting
trait's scope. At `77d34fc10`, strict algo/struct pass3.419/4.370s and private/protected
forbidden-receipt checks pass68 supplied conditions plus12 setup clauses. Their native
originals confirm access Errors before the property fatal; they add no source-agreement
credit. The affected public failed-birth53 conditions plus6 setup clauses pass11.734s.
Raw artifacts are `trait266-object-algo-s6o6pssf`,
`trait266-object-struct-n4p5pbmw`, `closure-call-protocol-10bjo22b`,
`closure-call-protocol-08sz3xg1`, `closure-call-protocol-q5w3a8qt` and
`fcc-access-review19/native-*` under the same current
worktree's `.tools/`.
Live concrete alias/visibility lookup now uses the exact source copy plan only
when ordinary import lookup misses. At `6470366fa`, strict algo/struct pass3.469/4.322s;
three normal source tuples and one genuine birth/default/static checkpoint with44
supplied conditions plus6 setup clauses pass (18.696s). Cloned aliases share their
canonical static cells while own methods and excluded originals keep distinct targets.
Raw evidence is `.tools/trait-fcc-adaptations-current19/.tools/`:
`method-runtime-rbmzbjug`, `closure-call-protocol-tb4117ep`,
`trait266-object-algo-wqm4aoeh` and `trait266-object-struct-2n7pfvr6`.
The reviewed327 composition at `1f6313f7e` over `e044ff7cb` passes strict
algo/struct at3.369/4.220s without renewing those source/state cuts. Its raw
compiler results are `trait266-object-algo-gtfakyej` and
`trait266-object-struct-d2ofi_zz` in the same evidence directory.
Later failed FCC imports retain the exact cached target of an already published
first owner, with their own called class and source/collision prefix. At
`494f6b34f`, strict algo/struct pass3.369/4.220s; one PHP-error source comparison
and68 supplied conditions plus6 setup clauses pass (17.433s). The genuine C-to-E
failure preserves C's live cache, retires E's owner and rejects a fresh E method,
forged call scope/prefix/history and live resurrection. Raw evidence is under
`.tools/trait-fcc-later-birth-current19/.tools/`: `method-runtime-ekmhst3r`,
`closure-call-protocol-7846p_2q`, `trait266-object-algo-reoln7u9` and
`trait266-object-struct-s86zgxqr`. A missing watched runner symlink stopped the
first state invocation before numeric execution; that infrastructure failure is
retained without semantic credit.
These unchanged cuts bridge to the reviewed328 composition, preserving bound
callback RAW/INPUT, caller ownership and source fields.
Module347 retains exact first-failure method metadata for later genuine FCCs,
without restoring the failed class's imports, publication or retired live value.
Three shutdown originals cover an imported target, an own/private target and an
alias absent from the later published class, preserving literal defaults and
clone-shared static cells. The imported tuple passes at `6985967dc`; the own tuple
and69 supplied conditions plus6 setup clauses pass at `297715fb6` (29.446s), after
prefix-aware cache dispatch and the shared `039abc623` handler-context fallback.
Raw evidence is under `.tools/trait-fcc-failed-target-current19/.tools/`:
`method-runtime-w4gfa3m7`, `method-runtime-j2l114gl` and
`closure-call-protocol-v8z8eaza`. The original own/state failures
(`method-runtime-w4gfa3m7`, `closure-call-protocol-x00j9n0z`) and alias failure
`method-runtime-q6upsv1_` remain preserved without passing credit.
At the reviewed332 composition `f19c12d66` over `9d1956cd5`, strict algo/struct
pass3.419/4.370s; the alias tuple and46 supplied ordinary-receipt/scope conditions
plus6 setup clauses pass (23.352s), including declaration, call and heap validators.
Raw evidence is `.tools/trait-fcc-failed-target-publish19/.tools/`:
`method-runtime-yzmgrx7y`, `closure-call-protocol-9bii28x9`,
`trait266-object-algo-txlrnwr9` and `trait266-object-struct-zc6hpeu2`.
The earlier source2/69 cuts bridge unchanged; current source, Generator,
ArrayAccess-certificate and pruning-graph fields are preserved.
The final334 composition `5ebf803b2` over `86e7f6ccb` passes strict algo/struct
at3.519/4.370s (`trait266-object-algo-l0tbn4ov`,
`trait266-object-struct-npafxy47` in the same publish evidence directory).
Typed-property retirement and bound Fiber-start ownership remain unchanged;
the source/state cuts bridge without renewal.
Later failed imports also authenticate the first target after its owner failed,
at the later birth prefix while retaining the published-owner path. Both
Closure records stay dead and neither failed class is published. At `070170525`,
strict algo/struct pass3.519/4.371s; one shutdown PHP-error tuple and59 supplied
rollback conditions plus6 setup clauses pass (29.959s), including declaration,
call and heap validation and source/prefix/called/resurrection inverses.
Raw evidence is `.tools/trait-fcc-failed-target-current19/.tools/`:
`method-runtime-49mdsmg6`, `closure-call-protocol-a6halclw`,
`trait266-object-algo-eolich9z` and `trait266-object-struct-je7sw7n_`.
The reviewed EX/SOURCE336 composition `8b47bee97` over `b4f1e6175` passes strict
algo/struct at3.469/4.420s (`trait266-object-algo-pemw9ni4`,
`trait266-object-struct-bjiml5w8` under the publish evidence directory). Its
GC.SCAN schema and caller/source fields are preserved; source1/59 bridge unchanged.
Failed imported first targets distinguish successful data binding followed by abstract
verification failure from a failure before method-scope fixup. Exact historical
data replay selects the fixed C scope or the known unfixed trait scope; an unknown
phase denies cached selection without substituting the later class's method.
Only scratch replay reuses the authenticated direct FCC value. A live retained
FCC can evaluate `self::class` for its failed lexical owner without publishing it.
At `6f76ae9fd`/339, strict algo/struct pass3.719/4.570s, one shutdown PHP-error tuple
and59 supplied conditions plus6 setup clauses pass (49.848s), including genuine
static installation and all declaration/call/heap validators. Raw evidence under
`.tools/trait-fcc-failed-target-current19/.tools/` is `method-runtime-fag72wcy`,
`closure-call-protocol-2k36nias`, `trait266-object-algo-b1gh0tol` and
`trait266-object-struct-izuh_dgb`. Earlier Unsupported/timeout/interpreter failures
(`uh6igkol`, `xf7jjsk7`, `ppfvuqw4`) and the rejected synthetic own-root fixture
`1f6_ozo9` retain zero agreement. The native-warning catalogue transcription was
corrected from preserved raw stderr without repeating PHP. Callbacks after fixup
but before the failure marker remain open.
The reviewed344 composition `0db3c85b5` over `c527549353` passes strict algo/struct
at3.619/4.420s; these source1/59 cuts bridge unchanged. Current GC/Fiber/source
fields and static-compound selectors are preserved. Raw compiler evidence is
`.tools/trait-fcc-failed-target-publish19/.tools/trait266-object-algo-nke5f48d`
and `trait266-object-struct-elvmk9fw` in the same directory.
Retained `new self` now rejects an unresolved implicit abstract trait requirement
before arguments or instance allocation, using the exact copied requirements and live FCC
scope; unknown proof stays Unsupported. At `a18e91e3e`/345 over `4cd2eab3a`, strict
algo/struct pass3.569/4.469s, one shutdown PHP-error tuple and39 supplied NEW
conditions plus6 setup clauses pass (44.118s), including all four global validators.
Raw evidence under `.tools/trait-fcc-failed-target-current19/.tools/` is
`method-runtime-3w3ufl_3`, `closure-call-protocol-gbmre4ve`,
`trait266-object-algo-umrooye4` and `trait266-object-struct-o_3sgnyc`.
The reviewed347 composition `7bfa05c07` over `0ac26ef29` passes strict algo/struct
at3.569/4.522s; the unchanged source1/39 cuts bridge with current INSTANCE storage,
scoped-static selection and Generator fields preserved. Raw compiler evidence is
`.tools/trait-fcc-failed-target-publish19/.tools/trait266-object-algo-1knav8u7`
and `trait266-object-struct-xxwdsrqv` in the same directory.
Retained `new static` now authenticates its saved caller/source scope and constructs
the published called class. Deferred static fills keep the selected NEW certificate
instead of resolving the keyword by spelling; corresponding typed-retirement checks
are statically reviewed.
At `ba08d2141`/347 over `b03c0d918`, strict algo/struct pass3.571/4.520s,
one shutdown PHP-error tuple and40 supplied conditions plus6 setup clauses
pass (59.412s). The genuine argument-entry checkpoint checks allocation order,
completed table history, all four global validators and a forged fill certificate.
Raw evidence under `.tools/trait-fcc-failed-target-current19/.tools/` is
`method-runtime-qw3d9lht`, `closure-call-protocol-iw_iw2zf`,
`trait266-object-algo-hv4l35mf` and `trait266-object-struct-ucfu1_fr`.
The earlier genuine history failure `lqhiz3_8`, diagnostic `s0n7wcj2` and
rejected fixture inputs retain zero agreement; no assertion was weakened.
The reviewed349 composition `620c2dc38` over `07940bc4a` passes strict
algo/struct at3.669/4.520s, preserving current SCAN, source, compound-static
and Fiber fields. The unchanged source1/40 cuts bridge; raw compiler evidence
is `.tools/trait-fcc-failed-target-publish19/.tools/trait266-object-algo-hw829us3`
and `trait266-object-struct-h1twh_vj` in the same directory.
Own/private retained SELF now uses the same explicit data-completion proof;
equal method descriptors cannot substitute for successful data binding. At
`45f4d56df`/349 over `cea25ed85`, strict algo/struct pass3.621/4.570s,
one shutdown PHP-error tuple and44 supplied NEW/phase conditions plus6 setup
clauses pass (28.059s), including fatal/unknown denials and all four validators.
Raw evidence under the current19 `.tools/` directory is `method-runtime-wl909uqp`,
`closure-call-protocol-4ip6lkrl`, `trait266-object-algo-neuz73kp` and
`trait266-object-struct-mi7_5yec`. The imported fixup guard is equivalent;
earlier source/state cuts keep their identities.
The reviewed350 composition `55db5a21f` over `813af1719` passes strict
algo/struct at3.719/4.621s; source1/44 bridge with current callback witnesses
and stdClass storage preserved. Raw compiler evidence is
`.tools/trait-fcc-failed-target-publish19/.tools/trait266-object-algo-jen_5u_i`
and `trait266-object-struct-iqurkbph` in the same directory.
Explicit abstract retained SELF now authenticates the original class flags and
rejects construction even when data binding failed earlier; the implicit proof
still requires NORMAL. At `00d1acb37`/350 over `7c4a13bc1`, strict algo/struct
pass3.719/4.670s, one shutdown PHP-error tuple and39 supplied NEW/source-flag
conditions plus6 setup clauses pass (27.209s), including all four validators.
Raw evidence under current19 `.tools/` is `method-runtime-vcokv2pq`,
`closure-call-protocol-7qumzqku`, `trait266-object-algo-9ms95gjp` and
`trait266-object-struct-es2vzasj`. Earlier cuts remain unchanged.
Old trait-scoped SELF now authenticates the canonical class copy against its
published lexical trait and rejects construction with the pending NEW
certificate intact. At `0d9bde4c6`/350 over `7c4a13bc1`, strict algo/struct
pass3.669/4.670s, one shutdown PHP-error tuple and37 supplied source/scope/NEW
conditions plus6 setup clauses pass (41.881s), including all four validators.
Raw evidence under current19 `.tools/` is `method-runtime-eh0c0688`,
`closure-call-protocol-fu2_4hpy`, `trait266-object-algo-4otuss2g` and
`trait266-object-struct-qd7qmnag`. Earlier cuts remain unchanged.
The reviewed351 union `02f053676` over `4f156a297` passes strict algo/struct
at3.669/4.573s, preserving GEN request-fatal tasks and EX residual-GC fields.
Private source1/39 and source1/37 cuts bridge unchanged. Raw compiler evidence
is `.tools/trait-fcc-failed-target-publish19/.tools/trait266-object-algo-ucz93eec`
and `trait266-object-struct-1edjhak2` in the same directory.
Old trait-scoped STATIC now preserves the selected called class despite raw
trait-method/canonical-copy origin differences. At `2cc1fbb87`/351 over
`9782fbb4e`, strict algo/struct pass3.671/4.570s, one shutdown PHP-error tuple
and40 supplied NEW/allocation/history conditions plus6 setup clauses pass
(59.013s), including all four validators and malformed-certificate rejection.
Raw evidence under current19 `.tools/` is `method-runtime-o8ztu9z_`,
`closure-call-protocol-3yzz1hul`, `trait266-object-algo-mkqwx_04` and
`trait266-object-struct-wdvmpr1n`; previous SELF/STATIC cuts are unchanged.
The reviewed353 projection `ea6b5b5c2` over `54589b343` passes strict
algo/struct at3.719/4.721s, preserving computed-static, Generator and source
consumers; the private source1/40 cut bridges unchanged. Raw compiler evidence
is `.tools/trait-fcc-failed-target-publish19/.tools/trait266-object-algo-5o1ambud`
and `trait266-object-struct-ifvl6gz9` in the same directory.
Retained failed-class `self::n(argument())` now selects an authenticated copied abstract
method and rejects it before argument evaluation. The shared required-class proof
keeps the existing implicit SELF construction behavior; unknown phases stay
Unsupported rather than becoming a fresh named lookup. At `b40dc5c2d`/354 over
`2257ebf82`, strict algo/struct pass3.719/4.723s, one shutdown PHP-error source
and41 supplied pre-send/source/phase conditions plus6 setup clauses pass (28.598s),
including unchanged allocations/events, the exact remaining TODO and all four
validators. Raw evidence under current19 `.tools/` is `method-runtime-cl8ncs4a`,
`closure-call-protocol-rms153ed`, `trait266-object-algo-tx_skl4w` and
`trait266-object-struct-sa28i5sp`. The accepted-baseline mismatch `pynrj2xf`
retains zero agreement; previous SELF/STATIC cuts are unchanged. Parent assertion,
source, storage and collector fields remain intact. Wider failed-owner members
and broader mixed parameter-view contexts remain open.
The failed class remains unpublished; parent/interface construction contracts,
including implicit Stringable, remain required.
Three previously open full parameter-view originals now agree with PHP at
`d75312e09`/358 over `6ed4873bd`, with unchanged100000-step/45/55 limits and
preserved native tuples: constructor/default rejection, error-handler reception
and positional/named variadic Stringable conversion retain old/later/cloned scopes.
Strict algo/struct pass3.869/4.971s. The coherent change combines the shared ARG
ASCII lookup (`e9c62f818`), noncontextual/contextual property-comparison split and
existing failed-header guard order. These preserve exact bytes, bool results and
receipt authority. Unchanged97 ASCII equalities, contextual CASE28+6 and live/failed
header24+12 controls bridge; they are not rerun or new coverage. Raw successful
source results under current19 `.tools/` are `method-runtime-40mogpx6`,
`method-runtime-e03mf3zz` and `method-runtime-xp95r2ob`; compiler results are
`trait266-object-algo-mrwoqqar` and `trait266-object-struct-b53pcjvb`. The bounded
causal trace `fcc-type-trace-wh6972lv` is diagnostic-only. Separate earlier costs
(`juu9_a0t`, `26nefyt9`, `m2nj5bv3`, `zk_o28v9`) retain zero full agreement; no
single-factor speedup is inferred across cuts. Final358 projection `a68e2939b` over
`5fdc40d04` passes strict algo/struct3.869/4.820s, preserving current collector
plan/cursor fields and the unchanged source3/control cuts. Raw compiler results
under publish19 `.tools/` are `trait266-object-algo-8va4fp0i` and
`trait266-object-struct-m308jcyl`. Broader mixed parameter-view contexts, differing-owner
later births and wider failed-owner member/construction behavior remain open.
Paused return work is excluded.

Dynamic read-key continuations233 preserve selected bases/keys through missing-CV,
null/float and global-array-name callbacks. GLOBALS rereads undefined keys in the
caller environment; ordinary arrays retain their fixed converted key. Real
temporary owners and conversion protection distinguish COW, live references and
sole-table retirement; NaN keeps protection across both ordered notices. Quiet
isset/coalesce and nested temporaries keep their distinct demand/ownership paths.
Author9/246 includes the two independent NaN originals; independent14/235 passes
at its separate cut. One
actual71da constructor in a parameter default passes with private captured
handler selection, called class and authentic key line/name through root mutation.
[Contract](docs/semantics/SOURCE-DIMENSION-KEYS.md),
[ledger](coverage/semantics/dimension-key-review.json). Writable242 covers the
bounded CV-array consumers above;249 adds direct coalesce-assignment/final unset.
Nested unset, wider memoized containers, append and wider object/key/container
producers remain core work.

Prepared internal Throwable default constructors235 map completed227 values
before names, arity and sequential reception. Default declaration strictness,
finite holes and nested previous owners retain exact trace argc and ErrorException
fields. Earlier8+7/reached67 at9fa and string-slot trace2 at7fb keep their own cuts
in the [scalar ledger](coverage/semantics/internal-default-constructors-review.json);
the original count observer remains Unsupported with zero agreement.

Live `display_errors`237 retains nullable original/live INI entries and raw
get/set/Restore. Ordinary text diagnostics capture stdout/stderr/off after handler
effects, keeping their position among source output across later writes and
include retirement. Current terminal errors preserve status255 when display is
off. Ten author and one independent exact comparisons, 76 source-derived state
premises and 17 entry/transport controls pass at b8e8, alongside223-module SL
stages/init and the changed adapter build. Actualddb6/233 preservation retains
225 modules with the reviewed display and dimension-warning routes, without renewed execution.
The [display ledger](coverage/semantics/display-errors-review.json) separates
source-defined nullable controls from native profiles. The held shutdown/fatal
source matches its independent original at actual231/237 cutccd900: rendering
selects the fatal destination before queue OFF/Restore writes. This composition
has its own record; wider display, parser/profiles and request phases remain open.

Registered startup inputs225 provide original `error_reporting` and
`include_path` bytes before compilation, independently of file/CWD facts.
Getters and Restore preserve null/empty reporting, signed32 masks and raw bytes
through setters, `@` and callbacks. Restore of an unmodified reporting entry
remains a no-op even when silence leaves its live mask different from startup.
Author7 and independent2 exact profile comparisons, 99 source-derived state
premises and 15 transport controls pass at36810; that cut also passes216-module
SL stages/init and the changed adapter build. The source-equivalent actual0592
composition retains all220 parent modules plus225, with no renewed execution
credit. [Startup ledger](coverage/semantics/startup-ini-review.json).
Wider directives, startup parsing/profiles and lifecycle remain required.

Source-owned parameter default constructors227 complete lazy class tables before
allocation and evaluate every AST argument before constructor access/name mapping.
Direct/inherited dispatch preserves declaring permission, called class, default
declaration strictness and the compiled receive line. Required-reference API
warnings precede temporary wrapping; completed values and nested Stringable
receives retain genuine object/cell/frame owners. Source2/independent16 at a223,
affected cold5 at954 and reached183/affected fact2 atd441 retain separate cuts.
Actual219/222/229 composition2 at2b153 passes normal and terminal-handler paths.
Actual221 callable source1/owner39 at2a380 authenticates the suspended constructor
through deprecation callbacks and rejects a removed retained owner.
The [constructor ledger](coverage/semantics/default-constructors-review.json)
keeps original failures, the fixture line correction and fresh uncached NEW facts
precise. Anonymous keyword defaults are covered by245 and ordinary internal
constructor effects by250; complete core remains open.

Deprecated callable keyword/compound admission221 now stages supplied fixed
parameters, error registration and delayed dispatch. Warnings hold class choice
and string boundaries while rereading referenced methods; whole byref formal
replacement preserves its live value. Genuine receiving/emitting frames and a
narrow API carrier admit compound foreign-`$this` selection and declared receiver
fallback without relaxing ordinary scoped eligibility. Supplied guards exclude
authentic named default holes. Exact union branches bypass warnings; direct/FCC
raw keyword/compound calls preserve ordinary PHP lookup errors. The
[221 ledger](coverage/semantics/keyword-compound-callables-current-review.json)
records independent pins, affected checks and preserved failures. Actual include,
cold-static and GLOBALS interactions preserve real USER permission, constrained
references and captured null; initializer locations retain their declaration owner.
Default/variadic reception is covered by248 above; other internal and user-return
warning consumers remain required. Unstaged special conversion stays Unsupported.

`Closure::fromCallable`234 selects and creates durable captures over existing core
callable forms. Existing Closure inputs preserve identity; method captures freeze
live method bytes and selecting permission before raw values/makers retire.
USER admission and internal Closure getter scope remain distinct, including
foreign receiver/called-class cases. Invocation/clone retain real defaults,
source method statics and receiver ownership. Created source Closures retain
authenticated method/import scope after the parent capture retires; static
children add no receiver owner, while nonstatic children retain their bound
receiver. Imported private cold references and per-host source statics are covered.
Factory lookup-warning throws wrap only after handler/finally unwinding; argument-read throws before entry remain
unwrapped. [Contract](docs/semantics/FROM-CALLABLE.md),
[review ledger](coverage/semantics/from-callable-review.json).

Iterator224 adds compatible explicit declarations and inherited internal
obligations for source by-value foreach; callbacks use
effective runtime methods and retain the iterator/current result through key and
body. Independent source26 confirms callback order, reference results, ownership,
lexical/called scope, inherited signatures and source-interface priority at its
two recorded cutoffs. Author source5 and owner125 retain their original results.
Cursor checks enforce unique live continuation and metadata IDs below `NEXTITER`;
cursor49 and claim85 pass separately. Independent source1/reference63 and affected
fatal teardown38 pass with unchanged87d semantics; the latter corrects only a
fixture line binding. On accepted2e8, source12 passes control cleanup, arbitrary
keys, assignment priority, covariance and the remaining throwing callback stages
at284803284. Independent source1/protocol16 at the same cutoff confirms zero-argument
Stringable default reception. Earlier results and original failures remain preserved.
IteratorAggregate, ArrayAccess and remaining reference/ordinary object traversal
remain required after the early-eval diagnostic work. [Scope and boundaries](docs/semantics/ITERATORS.md).

Direct missing `$GLOBALS[key]` R-fetches226 dispatch before their consumers and
retain the original null through key/global mutation. Handler throws skip later
ASSIGN/SEND, preserving typed destinations and the original exception chain.
Quiet/reference acquisitions keep their existing real cells. Genuine76 whole-table
snapshots under explicit request facts preserve numeric keys, singleton unwrap,
shared reference owners and COW after global retirement. Author8/207 and
independent8/221 pass at distinct private cutoffs. Two current derived sources
on accepted ed6 pass at bb90, retaining private first-class handlers, called class,
eager identity reads and a cold typed static alias. The combined observer retains
its inconclusive CLI60 timeout. [Contract](docs/semantics/SOURCE-GLOBAL-WARNINGS.md),
[ledger](coverage/semantics/global-warning-reads-review.json).

Exception handlers222 retain nullable raw stacks and dispatch an uncaught
Throwable after `finally` through the ordinary weak call receiver. Genuine null
caller and saved-frame certificates preserve one argument, selected targets and
owners through restoration, replacement, nested warning handling, throws and exit.
Author29/216 and independent33/331 retain their distinct source cutoffs; two
explicit Unsupported controls add no agreement at their original cut. Actual219
composition preserves
cross-file diagnostic origins during static defaults, and production algorithm
and structure checks pass. [Contract](docs/semantics/SOURCE-EXCEPTION-HANDLERS.md),
[author/composition record](coverage/semantics/exception-handlers-review.json),
[independent review](coverage/semantics/exception-handler-review.json).
Module247 supplies the effectful keyword/compound registration and terminal
selector through shared221 stages. Exception stacks retain raw values; shutdown
entries freeze the selected target after referenced-method warning effects.
Borrowed producer target/callsite/scope certificates preserve genuine ordinary,
C-handler, Stringable and Closure maker permissions after retirement.
[Author/composition checks](coverage/semantics/callback-api-consumers-review.json)
cover40 source tuples and140 reached assertions; the
[independent review](coverage/semantics/callback-api-consumer-review.json)
covers34 tuples and474 assertions at its own cut. Actual-parent getter Error,
trait/default and retired capture interactions pass; production algorithm and
structure checks retain the237-module cut. Accepted238/249/250 source preservation
adds no execution credit. Destructor/GC/output/free request phases stay open.

Called-class introspection223 implements `get_called_class()` using the active
authenticated called class. Plain functions and global Closures stop lookup;
captured/rebound source Closures retain their own class, while explicit builtin
Closure wrappers return `Closure`. Argument/count priority, optimized/generic
trace paths and real handler/emitter restoration are checked separately in the
[called-class ledger](coverage/semantics/called-class-review.json).

Deferred scalar/array static defaults219 retain the declaring scope, strict
property types, parent/constants/default order and first successful fills across
later failure/retry. Existing static rows own live values, arrays and typed aliases;
history stores no duplicate value. Eleven native/model agreements (seven normal,
four PHP errors) retain their original source cutoff. Five source-derived programs
accept 149 logical guards expressed as 152 sequential premises after narrow fixture
binding repairs. The [deferred-default ledger](coverage/semantics/deferred-static-defaults-review.json)
keeps original failures and unrun broader work visible. Two actual213/215
interactions at 8da51d193 retain inherited defaults through captured/private raw
handlers, captured-null cast/throwing assignment and a 214/216 Stringable receive.
Actual217 composition adds four normal agreements at 5c0887541, including saved
initializer contexts and compound callback traces, plus one cross-file fast-path
diagnostic agreement at 663811e8c. The unchanged owner41 guard passes. Module229
now supports same-default callback reentry: successful outer binding replaces
the live row, while escaped typed aliases retain ordered nonowning constraints.
Throw/type failure preserves the reentrant row; first-fill and table completion
remain once-only. Thirteen exact normal native/model comparisons and an inherited
67-premise ownership/history fixture pass at bf0954840. The earlier Unsupported
controls and declaration-order failure remain historical evidence; prior18/149
checks were not renewed. Cold static-reference continuations232 now keep the
captured RHS cell rooted through class-table initialization and reselect the live
target afterward. Immutable dynamic/ordinary method self/parent/static snapshots
survive callbacks and selected first-fill/retirement/table history. Seven exact
normal source agreements pass at69cc4546c;84 ownership/history premises pass at
0288de513 after narrow fixture syntax and selected work-block validator repairs.
Original failures remain separate; prior31/149/67 checks were not renewed.
Captured/rebound Closure keyword references239 now retain authentic nonowning
scope/binding evidence after pruning. Nested creation copies its immediate
creator's body, scope, receiver and nullable callsite, including error and
terminal callbacks; ordinary method ancestry stays exact. Nine new source
agreements and bound69 premises pass atd6bc09789; handler58/terminal35 pass at
860a8a19a after one fixture ordinal-binding repair. Temporary Closure::call child
creation now retains authentic source/receiver scope after maker collection;
nonstatic children keep the receiver and static children keep only nonowning
evidence. Five source agreements/global77 pass at e32dcc64a, affected callback81
at49d0b9579 after making ordinary/copied scope rules disjoint, and a fresh
same-class source/35 atadbfde09e: six sources/193 premises total. The original
validator failure is retained. Module246 now owns deferred scalar/array instance
templates by requested class and declaration, copies actual parent state at link
time, and fills constants, private-shadow instance layouts and statics before
allocation. Strict failure/retry and reentry retain once-only fill history;
objects copy template values and arrays remain owned after object collection.
Eight exact source agreements pass at80900fa4b; three programs/172 phase, copy
and ownership premises pass at449b45763 after a fixture source-origin binding
repair. Original compilation failures remain separate. Module252 extends these
templates to certified Closure/FCC values; other object/default producers and
wider consumers remain required.


Private and protected method arrays and class-method strings support callable
admission, selection, capture/clone and delayed error-handler dispatch. Object
selectors can redirect to the selecting parent's private method; concrete class
selectors use the requested class table. Protected access follows the root
prototype. Captures retain genuine selecting permission after makers retire,
while direct calls and API callbacks authenticate the real saved caller/emitter.
The current missing-CV assignment writes captured null through the referenced
caller argument after its private handler throws. Source1/94 stays separate from
the original author19/261 and independent16/345 checks.
The [scoped-callable ledger](coverage/semantics/scoped-callables-current-review.json)
keeps original failures and the three ordinary named-receive exclusions distinct.

Missing-CV reference sends retain the existing86/105 behavior: genuine null
cells, no warning and named-slot priority. Module220 rejects captured-null
ASSIGN through live typed aliases, retaining their value and replacing a handler
throw with a caller TypeError whose previous chain owns the original error.
At484d, author9/211 and independent5/249 pass; the latter corrects two fixture
phase assumptions without replaying passing models. The actual3919 composition
accepts one reduced scoped-handler source at5bce: TypeError context, typed caller
alias and the handler chain survive private selection and retired global owners.
The original observer-heavy source retains its inconclusive CLI60 timeout. The
[consumer ledger](coverage/semantics/warning-consumers-review.json) preserves
original failures and distinct revisions.

Warning-read consumers213 retain original null for six casts, selected copies and
ordinary by-value sends across handler mutation. Selected callees and prior arrays
keep their real owners; named-slot errors precede warnings. Direct ASSIGN writes
null even after a handler throws, before the same exception continues. Its
original rejected constrained-write control is addressed by private220 above.
Mixed author21 normal tuples/control0 and
58/60/65/53=236, plus independent10/197, retain their actual revisions and original
failures. Fresh actual6395 composition at181f separately accepts source1/94 and
independent cached-callee source1/96, covering static-reference sends, the real
outer-array prepass redirect and cached target/handler retention. Source-equivalent
publication preserves subsequent reporting, parameter backing and named-class
changes. [Consumer ledger](coverage/semantics/warning-consumers-review.json).

Fixed and variadic Stringable receives preserve receive order, captured cells,
caller strictness and backing authority; constructor-free defaults retain declaring
scope and fresh objects. Named constexpr `::class` retains source spelling and
authentic deferred/rebound lexical scope. Counts and original failures remain in
[parameter](coverage/semantics/weak-string-parameters-review.json),
[variadic/default](coverage/semantics/variadic-default-string-review.json) and
[constant](coverage/semantics/class-constants-current-review.json) ledgers and the
family table below. Internal and anonymous keyword constructor defaults retain
their235/240/245 cuts; broader attribute/modifier and callable initializer consumers
remain required.

Nonstatic private/protected `__invoke` supports bare calls, callable admission,
object capture/clone and bare-object error handlers through the effective runtime
method table. Explicit method calls keep lexical visibility. Compilation checks
parameters/body before the static fatal or nonpublic warning; inheritance access
errors retain preceding warnings. The [publication ledger](coverage/semantics/invoke-publication-current-review.json)
separates the original source/compiler/runtime checks from the current strict USER
truth-warning interaction, failures and unchanged return-classification boundary.

Method-array and class-method-string error handlers register raw values and
select afresh at dispatch. Entered targets retain genuine emitter scope, arguments
and owners through member mutation, nested replacement, throw and false fallback.
The [method-handler ledger](coverage/semantics/handler-callables-current-review.json)
keeps mixed author/independent checks, current CONFIG PIPE and original failures
at their actual revisions.

Diagnostic ingress217 dispatches runtime `E_STRICT` and lossy reporting
conversions through authentic handler continuations. Selected values survive
callback declarations; integer conversion precedes dispatch and the setter reads
the old mask afterward. Saved initializer facts and busy class scopes retain
normal/throw cleanup and expression/fetch exception locations. Fourteen author
and four independent sources plus 211 conditions keep their actual revisions.
Current 210 compilation and one scoped private-handler/Stringable-backing/lexical
class-name source comparison establish added composition separately. The
[diagnostic ledger](coverage/semantics/reporting-diagnostics-review.json) retains
original failures and cutoffs. The separate
[eval-location increment](coverage/semantics/compound-eval-location-review.json)
retains genuine filename owner/root/child through compound class, method/Closure
and static-property callbacks, with real eval call sites and lexical scopes.
Compiler exceptions use their failed unit; ordinary runtime exceptions keep the
execution override. Five original agreements/81 controls retain their distinct
cuts. One current inherited static-default/private-handler source plus214 compiler
stages at2c0c validate that composition and the static-fill compiler-prefix bridge.

The installed families compose as follows; each ledger records its scope and limits.

| Family | Current behavior and evidence |
| --- | --- |
| Class constants183/184/212 | Lazy scalar/array and selected Closure/FCC caches preserve strict types, inheritance priority and compile-entry availability. Named constexpr `::class` and rebound lexical defaults preserve source spelling/scope. Catalogue of 93 and 159 + 44 + 63 callable/class-name guards retain separate cutoffs; broader consumers remain open. [Constants ledger](coverage/semantics/class-constants-current-review.json). |
| Warning-truth decisions209 | Branch/loop/short-circuit/NOT/ternary-condition choices consume the captured null even after handlers define the CV. Saved consumers and thrown-handler cleanup retain authenticated source/line. Later cast/copy/SEND checks are recorded separately below. [Truth ledger](coverage/semantics/warning-truth-review.json). |
| Warning-read consumers213 | Six casts, selected ternary/coalesce copies and ordinary by-value sends preserve captured null, aliases and selected targets through callbacks. Direct ASSIGN retains its null write through throw. Mixed21/control0+236 and independent10/197 remain separate from fresh static-reference/outer-array source1/94 and cached-callee source1/96 at181f. [Consumer ledger](coverage/semantics/warning-consumers-review.json). |
| Borrowed warning reads208 | Strict identity retains the old reference cell across callbacks without adding an owner; saved callers and throw cleanup preserve it. Defined ordinary `$GLOBALS[key]` uses the real table. Getter/setter and method-string interactions keep separate revisions. [Warning-read ledger](coverage/semantics/warning-reads-review.json). |
| Error handlers/reporting206/207/211 | Raw registrations and selected targets retain four arguments and genuine emitting frames through mutation, replacement, nested reentry, throw and false fallback. Reporting get/set/Restore separates full raw bytes, signed32 masks and modified-entry state across suppression and handler writes; twelve normal sources across two revisions and 74 conditions are accepted. Fifteen nondeprecated error constants resolve exactly. Diagnostic ingress217 adds runtime `E_STRICT` and handled lossy reporting conversions with distinct 14+4/211 evidence and current source1. Broader handler forms and producer coverage remain open. [Diagnostics](coverage/semantics/reporting-diagnostics-review.json). [Reporting](coverage/semantics/reporting-ini-review.json), [method handlers](coverage/semantics/handler-callables-current-review.json), [earlier handlers](coverage/semantics/error-handlers-review.json). |
| Exception handlers222 | Raw nullable set/get/restore stacks and null-caller uncaught dispatch reuse ordinary calls with one authentic Throwable. Selected snapshots survive registry removal; weak receive, by-reference warning resume, nested restoration/replacement, throws, exit and fatal masks preserve ownership and termination. Author29/216 and independent33/331 pass at recorded cutoffs; actual219 source1 and production algorithm/structure gates pass. [Exception contract](docs/semantics/SOURCE-EXCEPTION-HANDLERS.md). |
| Class-method strings210 and FCC119 | Full-byte lookup separates frame-based callable admission, computed static dispatch and fixed compatible-this selection. Captures/clone retain immutable source certificates and defaults/static cells. A named throwing handler preserves the selected static caller and arguments. [String ledger](coverage/semantics/class-method-strings-current-review.json). |
| Method arrays205 | Public source method arrays retain immutable selected receiver/owner/called-class certificates through dynamic calls and capture. Current two-slot INI checkpoint **f9f47f115/61370c98/1353** accepts source1/finite103; broader resolution remains open. [Array ledger](coverage/semantics/array-callables-current-review.json). |
| Include/configuration | Failed CHDIR warnings retain provider certificates and caller frames through handler CWD/raw writes, false fallback and throw. One current throwing source/136 conditions, earlier three sources and compiler25 checks keep separate revisions. Stringable CHDIR PIPE retains post-callback CWD/held operands; unary CONFIG PIPE preserves source strictness through borrowed warnings. [PIPE ledger](coverage/semantics/include-config-pipe-review.json). Raw getters, primitive/null Restore, weak-null handler continuations and two-slot INI ownership retain their separate checkpoints. [Readback](coverage/semantics/include-ini-readback-review.json), [INI](coverage/semantics/include-stringable-ini-option-review.json). |
| Stringable SET/Restore and paths | SET separates raw INI bytes from effective C-string paths. Weak Restore uses exact full-name lookup and preserves callback mutations on misses. Current ARG/Restore checks retain caller arguments and zero-argument callbacks. [Restore](coverage/semantics/include-stringable-restore-review.json), [prefix](coverage/semantics/include-ini-prefix-review.json), [SET](coverage/semantics/include-set-current-review.json). |
| Typed static properties197 | Weak simple Stringable assignment rechecks live aliases and retains paired callback owners. Current Restore/ARG/INI composition preserves full property bytes, caller arguments and normal/throw cleanup. [Property ledger](coverage/semantics/typed-static-string-assignment-review.json). |
| Weak string parameters214/216/218 | Fixed and positional/named variadic receives preserve caller strictness, nominal/callable precedence and captured cells; existing constraints reject before callbacks. Newly attached sources permit only the parameter-authorized backing value. Constructor-free defaults use genuine scratch cells, declaring method scope and fresh objects. Source6/state299/independent2 and variadic/default6+6/focused4/independent3/state336 retain separate cutoffs. [Parameter ledger](coverage/semantics/weak-string-parameters-review.json), [variadic/default ledger](coverage/semantics/variadic-default-string-review.json). |
| Static setters200/201 | Backed final/asymmetric declarations normalize equivalent setters and preserve inheritance/error priority; direct and indirect consumers retain lexical access, live raw-slot checks and typed aliases. [Setter ledger](coverage/semantics/static-setter-access-review.json). |
| Instance setters288 | Backed typed setters preserve lexical/prototype permission, called diagnostics, reference/indirect/unset priority and raw-object exceptions. Staged Stringable compound callbacks retain exact destination/consumer and saved writer scope. Private34 normal/8 compiler/350 reached premises retain distinct cuts; actual Fiber source1 and SL274 pass at a939. Wider static selectors, writable append receivers and sole borrowed destination retirement remain open. [Instance ledger](coverage/semantics/instance-set-access-review.json). |
| StaticCall reference acquisition141/142 | Getters with untyped return signatures retain scoped selection, typed and legal untyped static aliases and returned-cell cleanup. Typed REF flags preserve initialization/error priority even when discarded. Direct reference sends retain the real cell; ignored untyped getters leave raw values unchanged. Ownership/type-source and getter/borrowed-read checks keep their distinct revisions. [Reference ledger](coverage/semantics/static-method-reference-review.json). |
| Argument introspection198/199 | Ordinary current and saved frames retain genuine named/unpacked argument views through invocation and callbacks. [Argument ledger](coverage/semantics/argument-introspection-calls-current-review.json). |
| Object invocation and callable typing | Effective nonstatic `__invoke` lookup includes private/protected methods, retaining declaring owner, called class and receiver across argument effects and clone. Explicit access remains lexical. Callable-before-string parameters preserve dual-role objects; shared ordinary by-value return classification adds no fresh return agreement. [Publication](coverage/semantics/invoke-publication-current-review.json), [earlier invocation](coverage/semantics/source-invoke-current-review.json), [parameter reception](coverage/semantics/callable-string-current-review.json). |
| Selection and capture | Source method selection preserves owner/called class; capture/clone retains selected targets and scoped defaults/static cells without retaining retired origin-only creators. [Capture](coverage/semantics/method-capture-current-review.json), [default caches](coverage/semantics/closure-default-cache-review.json). |
| Compiler publication190–196 | Ordered class/function availability, early diagnostics and authenticated declaration history compose with calls and callbacks. Compile-stop freezes saved callers and retires active file replies; it does not perform ordinary unwind. [Publication ledger](coverage/semantics/compiler-publication-review.json). |

Executables and compiler inputs are reused; source-equivalent publication adds
no rebuild or fresh execution credit. Earlier selector, capture, invocation and
baseline milestones remain in [MILESTONE-HISTORY.md](MILESTONE-HISTORY.md) and the
linked ledgers. [Cleanup](coverage/semantics/error-origin-author.json) and
[migration](coverage/semantics/throwable-migration-review.json) retain deferred
failures and interrupted evidence.

## Remaining core work

- Calls: other internal and user-return
  keyword/compound warning consumers,
  magic/autoload/internal consumers, dynamic compile-warning handler delivery,
  transformed wrappers and broader CONFIG PIPE consumers. Only the selected captured-static
  array and string Closure PIPE routes are covered. Direct defined/missing
  `$GLOBALS[key]` reads and explicit-request full-table snapshots are admitted;
  233 additionally stages earlier missing key-CV and null/float/global-array-name
  conversions through nested/quiet reads. Writable242 adds bounded CV-array W/RW
  and direct GLOBALS reference fetches;249 adds direct CV-array coalesce-assignment
  and final unset;255 adds nested unset and append, and262 adds nested coalesce
  assignment on defined CV-rooted arrays;269 adds GLOBALS W/RW name/missing-entry
  continuations with direct updates/compounds and nested array ingress.
  Container276 adds undefined/null/false W/RW initialization and final array-reference
  ingress;282 stages missing/scalar R and quiet-container warnings with genuine
  row/key owners. ArrayAccess284 adds the builtin contract and direct R/IS,
  isset/empty, Set/append and Unset calls. Writable292 adds direct compound and
  ordinary nested W/RW/Unset Get; append304 adds intermediate and compound append,
  and309 adds final simple append to returned children. Module319 adds untyped/mixed
  reference Get;326 adds named sends and nested captured-row updates, and329
  adds VALUE-return Notice callbacks;334 adds real Stringable DIM_OP conversions
  and callback-unset key receives. Finally-sensitive Notice ingress, bare/fall-through
  NULL, handler exit, wider memoized consumers and combined Iterator/ArrayAccess notice ordering,
  initial string/ordinary-object reads, wider variable/property bases and writable
  memoized/unset/append containers stay open.
  Wider memoized and GLOBALS quiet/unset consumers, wider key/object/container
  producers and ordinary snapshots without request facts remain open.
- Include/configuration: wider initializer/callback/compile-warning consumers,
  wider startup directives/parsing/profiles,
  other warning producers, OS services and lifecycle. The
  [include contract](docs/semantics/INCLUDE-SOURCES.md) separates these consumers.
- Values, references and coercion: dynamic object `::class`, dynamic hole provenance and broader weak
  parameter/property conversion, constrained-reference object conversion, wider nonstatic delayed receivers and
  broader reference-result consumers. Other object-bearing default producers and
  wider Closure creation contexts remain Unsupported.
  Uncertified object transfers, unretained update selectors, builtin FCC targets and
  wider callable initializers remain Unsupported; modifiers/attributes stay open.
  Wider deprecated constant consumers remain open. Generic, scalar-loop, CV/compiled-CONST
  and bounded physical-array return replay are integrated, as is deferred reference-return
  Notice dispatch. Bounded single-active-finalizer CV replay and aliased-CV Stringable
  reference conversion 186 and bounded sole-local-CV lifetime 381 are integrated.
  Immutable string-literal, explicit-NULL and bounded computed string VALUE consumed
  continuations are also integrated. M75-M77 add bounded nullable integer assignment
  VALUE returns across a caught finalizer, including one effectful positional argument
  and one folded integer RHS. M78 adds a flat owning-array assignment return with
  a witnessed x-table copy and detached NULL restoration. M79 adds a bounded
  ordinary-object assignment return through destructor release and caught
  selected-reference recheck. M80 adds the exact nonnullable builtin-int
  no-argument assignment source: a restored NULL fails return verification,
  cancels its pending Notice and re-enters the outer finalizer before the
  original TypeError reaches the caller. M81 restores the local catch and
  consumed return cursor when an old C destructor throws an Exception
  during selected reference replacement. M82 admits modeled built-in
  Exception descendants at that same authenticated destructor exit. M83
  admits public resumption from a normal pending-free destructor operation
  exit with the same bounded old-return cursor. M84 admits finite modeled
  built-in Throwable kinds at the pending destructor exit; one destructor-
  produced TypeError is checked through its local catch and consumed return.
  Other VALUE signatures/layouts, general CONST/other
  NULL and multiple-active histories, genuinely released
  CV targets, wider destructor throw/reentry, real suspension and wider typed consumers
  remain open. [String contract](docs/semantics/USER-STRING.md),
  [finally contract](docs/semantics/SOURCE-FINALLY.md).
- Objects and lifetime: remaining static members, effectful trait data composition,
  enums, hooks, readonly and wider instance setter consumers,
  traversal, output handlers and lifecycle callbacks. Static cells remain
  partial across wider producers, bind/clone, include/eval reactivation
  and GC. [Method](docs/semantics/SOURCE-METHODS.md),
  [static-property](docs/semantics/SOURCE-CLASS-STATICS.md) contracts.
- Control and diagnostics: Generator/Fiber, remaining warning/read producers,
  broader API/callable argument consumers and remaining request phases.
  Broader constant consumers and compiler reporting interactions remain open.
  Called-class introspection223 leaves builtin Closure rebinding, builtin API
  callback targets, suspension and wider reference-result consumers open.

`returns_verify` has resumed with the authorized temporary verifier. Preserve
held branches and evidence, and do not retry the rejected engine experiment.
Generic, scalar-loop and CV/compiled-CONST delayed replay are integrated, as is
bounded physical-array owner recovery. Bounded single-active-finalizer CV replay and deferred VALUE/NULL Notice dispatch are
integrated, as are bounded aliased-CV Stringable reference conversion 186 and sole-local-CV
lifetime 381, immutable string-literal, explicit-NULL and bounded computed string VALUE
consumed continuations. M75's assigned integer call has two exact original-source
agreements and one reached 96-premise proof at private `8afe016f`/397. M76's
same-variable nested integer argument has two further exact originals and one
110-premise reached proof at private `8beef331`/397: callee n17/global x17,
pre-finalizer x41, then restored caller NULL/x99 with one old-line Notice. M77
separates direct folded `40 + 1` (caller41) from the same folded RHS wrapped in
an assignment (callerNULL): source2 and an assigned 102-premise reached proof
pass at private `86a52f19`/398, binding RHS compiled41 versus outer compiled-read
absence, raw NULL/new Notice, alias, LINE refusal and budget. Historical native
and Unsupported baseline retain their private `7465dc88`/397 identities. The
[local CV ledger](coverage/semantics/reference-return-local-cv-lifetime-review.json)
retains M75's failed syntax gate and M76-M77's Unsupported baselines with zero repair credit.
M78's assigned `($x = old_value())` with `old_value()` returning `[41]`
separates `$x` to `[41,99]` after the finalizer append, while its direct-call
control ends with `[99]`; both callers receive detached NULL and one old-line
Notice. Native2, unchanged baseline (direct exact/assigned Unsupported), strict,
and source2 are pinned at private `0ca75133` then `90e931fe`/399. One assigned
108-premise reached fixture binds pending old HARRAY and x sharing, distinct
COW x table, root-free consumed marker, raw NULL/new Notice, caller alias,
LINE refusal and budget. The old literal can remain pool-owned, so this does
not isolate pending-root COW causality or prove collection. Its first fixture
compiler binding failure has zero state credit; only the affected fixture was
rerun. [M78 review](coverage/semantics/reference-return-local-cv-lifetime-review.json).
M79's assigned `($x = old_value())` with one runtime-created C instance
retains old object ownership through finalizer `$x = null`; selected-y
replacement releases it and runs `D` between the two `I` markers.
The direct no-argument control has `F:0`; assignment has `F:1`.
Both exact originals end in detached caller NULL, `r=b42`, `xNULL/y0`,
and one old-line Notice. Native2 and unchanged baseline at private
`6512137c`/399 show direct exact/assigned Unsupported; strict/source2
pass at `02ffe678`/399. One assigned 131-premise reached fixture validates
the saved f destructor prefix while D runs, old modeled HOBJECT retirement
after release, root-free consumed marker, raw NULL/new Notice, caller aliases,
saved-LINE refusal and D-cut budget. The first fixture's failed stage search
has zero state credit; only its active-state timing predicate was corrected
and rerun. This proves neither physical Zend collection nor throwing or
reentrant destructors; no prior return fixture was replayed.
[M79 review](coverage/semantics/reference-return-local-cv-lifetime-review.json).
M80's used `&f():int` assigned no-argument integer call initially gives
`x41/F:1`, then selected-y array rejection is caught. The nonowning cursor
restores NULL and one pending old-line VALUE Notice, but int verification
throws a distinct TypeError and cancels the Notice before delivery. The
original NULL error survives a second outer-finalizer pass and reaches the
caller with `r7/x99/yarray`; direct `return old_value()` is separately exact
with first `F:0`, while both sources call the helper once and deliver no
Notice. Native2 and unchanged baseline at `e90b3a74`/399 show direct exact
and assigned Unsupported; strict/source2 pass at `8b7c539a`/399. One assigned
128-premise reached fixture binds both error identities, the pending versus
delivered Notice, second `F:0`, caller error/r7, LINE refusal and budget.
No prior return fixture was replayed. Only the exact builtin-int
no-argument assigned source is newly admitted.
[M80 review](coverage/semantics/reference-return-local-cv-lifetime-review.json).
M81's used `&f():?C` returns a named no-argument old call directly or through
`($x = old_value())`; selected-y replacement releases the old object and its
destructor emits `D` then throws an Exception. The pending selected return
retains that Exception and a nonowning old cursor after old HOBJECT retirement.
The bounded pending-finish rule reconstructs the source replay owners, so the
same Exception reaches local `CE` rather than outer `OE`; consumed replay then
restores caller NULL with one old-line VALUE Notice. Native2 at `e70950fcb`/399
has `F:0/1;I;D;I;CE;A;S`, detached `rNULL/b7` and xNULL/y0. The unchanged
model's two NORMAL outputs route to OE and have zero agreements. A 44-premise
source-reached diagnostic isolates the old premature THROW_SEARCH with zero
repair credit. Strict and both original-source agreements pass at clean
`7bc06612d`/399. One assigned 122-premise reached fixture proves pending
Exception transfer, local catch identity, root-free consumed NULL/new Notice,
real operation-exit descriptor admission, heap-equal LINE-only public refusal
and pending-exit budget equality. The first public state failure at `75c47721a`
has zero full-state credit; only affected guards and checks were rerun.
This covers one ordinary C with a throwing destructor, exact Exception,
named no-argument old source, nullable class declaration and single cursor.
Other exception types, reentrant destructor histories and wider returns remain
open. [M81 review](coverage/semantics/reference-return-local-cv-lifetime-review.json).
M82 changes only the two exact Exception KIND guards at the selected return's
pending destructor exit and saved descriptor to use the existing modeled
Exception hierarchy. New direct/assigned `&f():?C` originals have C's
destructor throw `RuntimeException("boom82")`; local `catch (Exception)`
reports subtype and message as `CE:1/1`. Native2 at `108b026fe`/399 ends
with `F:0/1;I;D;I;CE:1/1;A;S`, detached `rNULL/b7` and one old-line Notice.
The unchanged model routes both to outer OE with r7/no Notice, giving zero
agreements. Strict and both exact source agreements pass at private
`345244d14`/399. One assigned 126-premise reached proof binds pending
RuntimeException and boom82 message bytes at real OP_EXIT, the same object
in the local superclass catch, retired old HOBJECT, root-free consumed
NULL/new Notice, public descriptor/LINE-only refusal and exit-cut budget.
The proof is one RuntimeException history; M81's exact Exception evidence is
separate. Other admitted built-in Exception descendants lack focused validation;
user-defined throwable subclasses, Error siblings, reentrant destructors and
wider returns remain open.
[M82 review](coverage/semantics/reference-return-local-cv-lifetime-review.json).
M83 repairs public descriptor admission at a normal pending-free
`DESTRUCTOR_OPERATION_EXIT` ahead of a selected `RETURN_REF_UNWIND` and one
nonowning old-return cursor. The source-reached diagnostic on unchanged
`440cf9c2b`/399 proves a valid operation and projected cursor after the old
HOBJECT retires, while actual public entry rejects the exit; its 49 Boolean
premises and one raw normal finish have zero repair credit. The seven-line
saved-descriptor clause preserves operation source/context and the bounded
named no-argument nullable-class direct/assigned old-source guard. Strict SL
initialization passes at private `cb2f199bf`/399. One assigned reached
fixture passes 90 Boolean premises and one raw step: real exit admission,
raw finish, M79's `r=bNULL` then `42` caller and one Notice, equal-heap
LINE-only public refusal, and 0→1+10000 versus 10001 budget equality with
the accepted terminal output. The historical M79 native/source agreements
remain separate; no M79 or M82 actor was replayed. Normal operation finish,
Throwable routing and ownership rules are unchanged. Wider destructor,
source and cursor histories remain open.
[M83 review](coverage/semantics/reference-return-local-cv-lifetime-review.json).
M84 changes only the two pending-destructor guards from modeled Exception
nominality to the existing finite built-in Throwable-kind predicate; operation,
source, owner, liveness and single-cursor checks remain. New direct/assigned
`&f():?C` originals make C's destructor throw `TypeError("dtor84")`, distinct
from the selected-y return-verification TypeError. Native2 at clean
`ee63167a1`/399 ends with `F:0/1;I;D;I;CT:1;A;S`, detached `rNULL/b7` and
one old-line Notice. The unchanged model routes both to outer OT with r7/no
Notice, giving zero agreements. Strict SL initialization and both exact
original-source agreements pass at private `913c87471`/399. One assigned
133-premise reached fixture (131 Boolean, two raw steps) binds the actual
pending TypeError to the destructor's `new TypeError` origin and dtor84 message,
distinct from selected-y; the same object reaches local CT. It also proves
old HOBJECT retirement, root-free consumed NULL/new Notice, detached caller,
real public descriptor and equal-heap LINE-only refusal, and exit-cut budget
equality. This is one TypeError witness; the admitted other built-in kinds
need focused validation, while M81/M82/M83 evidence remains separate.
[M84 review](coverage/semantics/reference-return-local-cv-lifetime-review.json).
M85 adds the simple-variable receiver, literal-name no-argument method source
only to the two authenticated pending-destructor-throw guards. A retained
Factory supplies O through reference-returning versus value-returning
`old_ref()`; native2 at clean `06f381e75`/399 reaches local
`CT:1;A;S`, detached `rNULL/b7` and one old-line Notice in both, while the
unchanged model wrongly reaches outer OT/no Notice (zero agreements). Strict
SL and both exact original-source agreements pass at private `c528b1850`/399.
The reference-only reached fixture passes 159 Boolean premises and two raw
steps: pre-finalizer BYREF source/Factory slot/HCELL→O, no early reference
Notice, distinct HCELL and O retirement at the pending TypeError exit while
Factory remains live, the same `dtor85` object at local CT, consumed NULL/new
VALUE Notice and detached caller. Actual descriptor admission, heap-equal
LINE-only refusal and exit-cut budget equality pass. The first fixture's false
pre-finalizer Notice premise failed with zero full-state credit; only that
affected fixture was retried. Normal pending-free method exits, arguments,
dynamic names and wider owner/destructor histories remained open at M85.
[M85 review](coverage/semantics/reference-return-local-cv-lifetime-review.json).
M86 removes M83's extra old-source classifier only from the normal pending-free
destructor-exit saved-descriptor guard. An actual selected return operation,
matching source/caller/origin/context, unique nonowning cursor and full queued
cursor validity still gate admission; normal finish, ownership and pending
Throwable routing are unchanged. A diagnosis-only historical M72 `?object`
method-reference cut on unchanged `b21c01dfd`/399 passes 62 Boolean premises
and one raw normal finish: actual public entry rejects its valid queued cursor
after old HCELL/O retirement. Strict SL init passes at private `ff7b9418f`/399.
One reached fixture there passes 102 Boolean premises and one raw step, proving
normal-exit admission and finish, M72's `r=bNULL` then changed alias/y bad and
one Notice, equal-heap LINE-only public refusal, and whole/split budget
equality. The historical M72 native/source agreements are separate; no old
actor was replayed and the diagnostic has zero repair credit. Wider normal
source histories and broad returns remain open.
[M86 review](coverage/semantics/reference-return-local-cv-lifetime-review.json).
M87 adds a direct named no-argument `?array` old-return source to the
authenticated pending-Throwable destructor-exit guards. A new
`&f():?array` original returns `[new O]`; O's destructor throws
`TypeError("child87")` during selected-reference replacement. Native1 at
clean `a43c7a30a`/399 reaches local `CT:1;A;S`, detached `rNULL/b7` and one
old-line VALUE Notice; the unchanged model wrongly reaches outer OT with r7
and no Notice. A diagnosis-only cut there proves the old table and child retire
before pending exit, with a valid projected cursor but rejected public entry
and premature THROW_SEARCH. Strict SL initialization passes, and the original
source agrees exactly at private `67396fd4c`/399. One reached fixture passes
136 Boolean premises and two raw steps: the old HARRAY→O edge, child87
TypeError origin/message and same local-catch object, retired old nodes,
consumed NULL/new Notice,
caller state, actual LINE-only public refusal and exit budget equality. The
first fixture run failed only a reused metadata binder and has zero state
credit; the corrected fixture alone was rerun. Existing ownership and normal
exit rules are unchanged. This proof covers one runtime single-entry array
with one throwing child; M56's accepted normal-child control stays separate.
[M87 review](coverage/semantics/reference-return-local-cv-lifetime-review.json).
M88 adds a literal-name no-argument `?array` method source only to the
authenticated pending-Throwable destructor-exit guards. Reference-returning
and value-returning `Factory::old_ref()` originals differ only in BYREF; native2
at clean `62c33de71`/399 reaches local `CT:1;A;S`, detached `rNULL/b7` and
one old-line Notice in both. The unchanged model wrongly reaches outer OT/r7
without a Notice (zero agreements). Strict SL initialization and two exact
original-source agreements pass at private `7966a4557`/399. A reference-only
reached fixture passes 195 Boolean premises and two raw steps: after Factory's
slot is unset, the protected old REFERENCE still roots live HCELL→HARRAY→O;
selected-return replacement retires all three at the child88 TypeError exit.
The same destructor-origin exception reaches local CT, then the nonowning
cursor restores NULL/new Notice and detached caller. Actual descriptor
admission, equal-heap LINE-only public refusal and exit budget equality pass.
The value source has separate source agreement, without a reached owner proof.
Normal pending-free routing and ownership rules are unchanged; wider arrays,
other owner histories and broad returns_verify remain OPEN.
[M88 review](coverage/semantics/reference-return-local-cv-lifetime-review.json).
M89 adds bounded assigned `?array` capture for a runtime one-entry
array holding an ordinary object child. Direct `return old_value()` and
assigned `return ($x = old_value())` originals differ by F0/F1; native PHP
runs D normally during selected-reference replacement, then catches the
selected TypeError locally and returns detached NULL with one old-line Notice.
On unchanged `2e75ac2d1`/399 the direct model agrees but assigned stops
after D as Unsupported, without Notice. At private `a50272b80`/399 strict
SL initialization passes and both original source packets agree exactly.
One assigned fixture passes 159 Boolean premises and one raw step: xNULL
leaves the protected HARRAY→O live; inside D the table is retired while O
remains live and the saved descriptor admits a nonowning cursor despite the
dead old operand. After D the f-origin TypeError, consumed NULL/new Notice,
caller `rNULL/b7/xNULL/ybad`, actual inside-D LINE-only public refusal and
whole/split budget equality pass. Existing normal destructor, pending-Throwable
and ownership/release rules stay unchanged; this is one normal child history.
[M89 review](coverage/semantics/reference-return-local-cv-lifetime-review.json).
M90 routes a pending child-destructor TypeError for that assigned `?array`
source through the existing authenticated replay owners. New direct and assigned
runtime `[new O]` originals make O throw `TypeError("child90")`. Native PHP
reaches local `CT:1;A;S`, detached `rNULL/b7` and one old-line Notice in both;
the unchanged `08ef06924`/399 model agrees only on direct and wrongly takes
assigned to outer `OT:1` with r7/no Notice. The sole pending-source guard
change at private `02023496d`/399 passes strict SL initialization and exact
agreement on both originals. One assigned reached fixture passes 143 Boolean
premises and two raw steps: preF x shares HARRAY→O, the destructor-produced
child90 TypeError and same object reach local CT after both old nodes retire,
and the nonowning consumed cursor restores NULL/new Notice. Real exit LINE-only
public refusal and whole/split budget equality pass. M89 capture and D-frame,
normal exit, ownership and release rules are unchanged; this is one throwing
child history, with wider aggregate and reentrant returns still open.
[M90 review](coverage/semantics/reference-return-local-cv-lifetime-review.json).
M91 routes a pending destructor TypeError from a typed `$box->slot` old
reference source in a used `&f():?object` return. The sole local Box is unset
before selected-reference replacement; O's destructor throws `slot91`.
Native PHP on unchanged `cd776548f`/399 catches that exact error locally,
returns detached `rNULL/b7`, and emits no Notice. The unchanged model instead
takes outer OT/r7 (zero agreement). At private `dad7475ce`/399 strict SL
initialization passes and the one original source agrees exactly. One reached
fixture passes 167 Boolean premises and two raw steps: preF typed ALIAS slot
and PROPREF source, retirement of Box/old cell/O at the pending exit, same
destructor-origin TypeError in local CT, then a distinct fresh NULL HCELL with
no PROPREFS or Notice and the detached caller. Actual equal-heap LINE-only
public refusal and exit budget equality pass. Only the authenticated
pending-Throwable property-source guard changed; capture, typed cleanup,
normal exit and consumed materialization remain unchanged. M63's normal
typed-property history stays separate; physical collection, other property
forms, reentry and broad returns_verify remain OPEN.
[M91 review](coverage/semantics/reference-return-local-cv-lifetime-review.json).
Wider owner domains, other VALUE signatures/layouts, general
CONST/other NULL or multiple-active histories,
genuinely released CV targets, wider destructor throw/reentry, real suspension and wider typed
consumers remain required.

Rocq interaction-tree semantics and BOLA proofs follow completed PHP core.

## Validated baseline

The post-arrow checkpoint is **1026/0ec57507**, with arrow capture and returns
117/118 at **87cdc532f**. Its [review](coverage/semantics/post-arrow-integration-review.json)
binds these distinct profiles and independent audits:

| Gate | Accepted observations |
| --- | --- |
| Compiler | 5,751 source lints, 8 access sources, 15 line observations; existing binary reused |
| Explicit request | 263 source profiles, 526 responses with exact request/environment facts |
| Callable | 946 maintained rows in 18 suites plus one regression; 1,894 responses |
| Ordinary | 5,706 source comparisons (4,060 normal, 1,006 PHP errors, 640 static rejections), 21 separate controls; 11,435 process records |

These are observations, not unique PHP programs or current full-core coverage.
Ordinary, request and callable profiles have different environment contracts;
their counts are not interchangeable.

## Validation and integration limits

Configuration permits eight pairs/16 agents; the numerical/model concurrency
cap remains five until explicit resource coordination, with coordinated slot
handoffs. Record the tested revision, compiler/runtime identity, relevant inputs,
environment, exact commands/exits and raw originals. Independent review focuses
on semantic counterexamples and reliable completion; investigate failures
narrowly and repeat only affected checks. Metadata adds no execution credit.

Interrupted runs, timeouts, Unsupported and budget controls are never native
agreements. Paused-state fixtures complement original-source comparisons; passing
subsets do not establish equivalence or full core. Final combined current-source
gates and a fresh copied-path, network-isolated offline rebuild remain required.
