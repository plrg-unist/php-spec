# Core PHP semantics progress

Target: **PHP 8.5.10 CLI, NTS, signed 64-bit integers**. [PLAN](PLAN.md) defines
complete core; the [inventory](coverage/semantics/features.json) tracks the 169
syntax constructors and 306 runtime obligations. The executable core remains
partial. Syntax acceptance and selected agreement do not establish full semantics
or BOLA freedom. [CORE](docs/semantics/CORE.md) defines the intrinsic boundary.

## Current checkpoint

Ordinary `%`, shifts and numeric bitwise operations now admit a fractional
finite LEFT CV with an empty live `stdClass` RIGHT CV without a materialized
property table. LEFT's saved `12` survives its handler's write to `99.5`; repaired
RIGHT `5` supplies results `2`/`384`/`0`/`4`/`13`/`9`. Retaining RIGHT raises
TypeError after the notice using current raw types, while a supplied throw skips
RIGHT and preserves the outer value. Ten formerly Unsupported warning originals
and one unchanged quiet TypeError control agree exactly; three independent
sources check numeric-string repair, object-first failure and a changed live
LEFT type. Strict424 and three source-reached fronts/314 checks pass, including
two derived type-failure checks. The first duplicate-assertion preparation stop
has zero semantic credit. Joined strict compilation over the current 424-module
tail also passes. Wider object, reference and producer forms remain
partial. [Object-RIGHT review](coverage/semantics/integer-object-right-warning-review.json).

Unit0 global anonymous classes may now extend a previously compiled plain
parentless Base through an unqualified reference. Inherited and overridden
constructors see Base property defaults; inherited methods keep Base lexical
scope and the anonymous called scope, and private Base/public child slots stay
distinct. Generated names use the resolved parent reference spelling before
`@anonymous`. Four new author originals and one independent name-visible source
agree exactly with pinned PHP; one unchanged parentless control stays exact.
Two source-reached states pass 88 premises, including full generated names, and
joined strict SL compilation passes all 424 modules. Independent review exposed
and corrected the initial wrong-prefix candidate; its mismatch and two earlier
runner stops retain zero agreement credit. Typed Base properties, forward or
autoloaded parents, dynamic units, interfaces and wider inheritance remain partial.
[Parented anonymous class review](coverage/semantics/anonymous-parent-review.json).

A fresh Aggregate-returned CONFIG Iterator with a public destructor may now
own one declared direct child with a public destructor and no child storage.
The parent destructor sees the child live; ordinary storage release then runs
the child destructor before API entry or catch. Three frozen originals agree
exactly with pinned PHP across normal, invalid-key and saved-Exception paths.
An independent normal source also agrees and observes parent weak death before
the child destructor, while the child's own weak reference remains live.
Strict compilation passes on 424 modules, and 233+216+229 source-reached
premises check ownership, order, weak death and pending identity. Joined strict
compilation over the actual tail also passes. Earlier
fixture compiler, timeout and stopped attempts retain zero credit.
[Returned Iterator child review](coverage/semantics/config-aggregate-iterator-child-review.json).
Wider child graphs, child-only finalization and destructor throws/reentry remain partial.

Primed public method-created by-reference `Generator::throw` now carries its
cached reference cell, authenticated receiver and saved Throwable through a
Fiber catch or pending `finally`. An external name rebind leaves the old cell
selected; `throw()` returns a snapshot while later `current()` follows cell
writes. Normal and supplied `Fiber::throw` continuations preserve the original
exception and `Previous` order, with separate receiver/cache retirement. Three
authored and one independent source agree exactly with pinned PHP; two I62/I63
controls remain exact. The three new authored sources were checked
`Unsupported` on the unchanged model. Strict compilation of 424 modules and
one reached state with 129 custom checks pass. Joined strict compilation
over the actual tail also passes. Two overstrong reached-state premises and an independent recorder comparison error retain zero credit.
Fresh method THROW, bound/delegated resumers and wider lifetimes remain partial.
[Method reference THROW review](coverage/semantics/generator-fiber-method-reference-throw-transfer-review.json).

Bounded unit0 anonymous `new` now takes one or two direct positional/named
arguments. Public required by-value untyped/`int` constructor formals use the
ordinary binder; a class without a constructor evaluates positional values and
ignores them. Class publication precedes sends, unknown named arguments stop
before later values, and typed failure leaves assignment untouched. Six new
originals and one unchanged zero-arg control agree with pinned PHP; one
independent named/int coercion source also agrees. The six new originals were
genuine Unsupported on the unchanged parent. Three source-reached groups pass
107 premises; two initial fixture elaboration failures keep zero credit.
Three off-scope status controls remain explicit Unsupported without agreement credit.
[Anonymous constructor argument review](coverage/semantics/anonymous-constructor-arguments-review.json).
Wider signatures, unpacking, dynamic units and lifecycle forms remain partial.

Fresh plain unbound Closure-created by-reference Generator::throw now carries
its advancing resumer and original temporary Throwable through a Fiber pause
before the first yield. The empty cache becomes a live reference cell only
after resume; the value returned by throw() is a dereferenced snapshot while
later current() follows that cell. Copied and reference captures, normal
catch/finally cleanup, and an independently frozen pre-yield Fiber::throw
abort match pinned PHP in four new sources. Two I65/I66 controls remain exact.
The three authored sources were genuinely Unsupported on the unchanged
parent; an initial 75-second reference-capture timeout has zero credit and
a selected 240-second run reached Unsupported. Private SL strict compilation
of 424 modules and one reached state with 118 custom checks (123 reported
assertions) pass. Method by-reference/fresh, bound Closure, delegated and
wider lifecycle forms remain partial.
[Fresh Closure reference THROW review](coverage/semantics/generator-fiber-fresh-closure-reference-throw-transfer-review.json).

Primed plain unbound Closure-created by-reference `Generator::throw` now
transfers an authenticated cached cell and real Closure through Fiber catch or
pending `finally`. Source-name rebinding preserves the old cache; copied and
reference captures, the parked original Throwable, reentry Error and normal
versus supplied `Fiber::throw` cleanup match pinned PHP. Three authored and one
independent normal-finally source agree exactly, with two unchanged direct
by-reference/by-value Closure controls. The three new authored sources were
`Unsupported` on the unchanged parent. Strict compilation of 424 modules and
136 custom source-reached checks (141 reported assertions) pass. The first
180-second reference-capture timeout remains zero credit; a selected
240-second run passed. At that cut, fresh by-reference Closure THROW and wider
callee and lifecycle shapes remained partial.
[Closure reference THROW review](coverage/semantics/generator-fiber-closure-reference-throw-transfer-review.json).

Fresh plain unbound Closure-created by-value `Generator::throw` now transfers
through a Fiber pause before the first yield. The advancing resumer retains
the original temporary Throwable while the Generator cache is empty; the
Closure keeps copied captures and original reference cells across source-name
rebinding. Three new original sources and a byte-identical primed I64 control
agree with pinned PHP; an independent fourth source also agrees when
`Fiber::throw` aborts before the first yield and the original Throwable gains
the supplied one as `Previous`. The three authored fresh sources were
`Unsupported` on the unchanged parent. Strict compilation of 424 modules and
117 source-reached premises pass. [Fresh Closure THROW review](coverage/semantics/generator-fiber-fresh-closure-throw-transfer-review.json).
By-reference, method, bound Closure and wider lifecycle forms remained partial
at that cut.

Selected public untyped backed block `&get` hooks now preserve the real backing
reference without attaching a property type source. The initial backing may be
an explicit scalar or implicit null. Alias writes, independent ordinary copies,
receiver retirement and Get-before-rebind Error agree in three exact original
sources and 214 Boolean checks plus three raw transitions.
[Untyped reference-Get review](coverage/semantics/untyped-reference-get-hooks-review.json).
The earlier typed `&get` slice retains its two source agreements and separate
251 Boolean/six raw checks without renewed credit.
[Typed reference-Get review](coverage/semantics/reference-get-hooks-review.json).
Inherited, virtual and wider hook consumers remain partial.

An unchanged Grandchild over a plain equal-typed or untyped Child redeclaration
now runs Parent's backed `&get` against Child's physical slot. Four exact sources,
392 reached premises and four raw steps pass; an unchanged Greatgrandchild
remained Unsupported at that earlier cut with zero agreement.
[Grandchild reference-Get review](coverage/semantics/grandchild-reference-get-hooks-review.json).
The linked reference-Get route now follows bounded descendants to Parent's sole
backed `&get`: unchanged classes have no properties/interfaces/constants, and
each redeclaring class has only that same-type public plain property without set
restrictions, interfaces or constants. The latest physical slot and typed
source or untyped absence win, while Parent lexical and leaf called
scope remain distinct. Five frozen originals, 449 reached premises and five raw
steps agree; the earlier Greatgrandchild control is now positive. A hook-bearing
intermediate remains Unsupported and changed-type declaration is a static
rejection with zero runtime agreement. The first fixture failure retains zero
credit. [Reference-Get chain review](coverage/semantics/reference-get-chain-review.json).

The selected linked `&get` path now admits distinct-name sibling properties,
own class constants and methodless marker interfaces on unchanged and plain
same-type redeclaring descendants. It still selects the latest physical slot,
attaches only that slot's type source, and keeps Parent lexical scope separate
from the leaf receiver. Four frozen native/model sources agree, with 538 reached
premises and four raw reference fetch/rebind steps; the two boundary controls
remain Unsupported and static rejection with zero runtime credit. Two first
fixture compiler stops retain zero strict credit.
[Memberful reference-Get review](coverage/semantics/reference-get-memberful-review.json).

A backed block `&get` may now be declared in a class with one linked parentless
Base. Base may lack the selected key or declare a same-name public plain property
of the same type; in the latter case the hooked child keeps its own slot and
default. Existing linked descendants still select the latest plain slot and
its typed source or untyped absence. Four frozen native/model sources and a
separate independent same-name chain agree, with 417 source-reached premises
and four raw fetch/rebind steps in the author packet. The initial two
Unsupported stops, one timeout and one semantic helper elaboration failure
retain zero full-packet credit.
[Parented reference-Get review](coverage/semantics/reference-get-parented-review.json).
Deeper Base ancestry, hooked/trait-selected Base properties and wider hook
shapes remain partial.

Parentless, trait-free `#[AllowDynamicProperties]` classes with no declared
instance slots and a dynamic history now materialize a validated ordinary
property table. Cloning without an effective `__clone` shares it, so a later
by-reference foreach bucket promotion reaches both objects; writable lookup
still splits the table. An effective callback takes a separate copy, including
after the last dynamic property is unset. One frozen live-foreach source exposed
the unchanged model's mismatch; the other thirteen frozen sources were already
exact. Reached checks exercise sharing, mirrors, source-driven COW,
non-clone table images and both all-unset branches. Earlier fixture/compiler
failures retain zero credit. [Dynamic-only cached clone review](coverage/semantics/dynamic-only-cached-clone-review.json).
Inherited/trait-composed classes, active collection and wider table layouts
remain partial.

Canonical same-kind builtin `Exception`/`Error` pairs now compare nonempty trace
arrays when captured arguments are direct primitive scalars or authenticated
string carriers. Eight source agreements, two object/array-argument refusals and
96 strict-SL premises with three raw steps pass; the original compiler-order and
carrier-admission failures retain zero credit. [Trace comparison review](coverage/semantics/throwable-trace-comparison-review.json).
Wider Throwable graphs and complete core semantics remain partial.

Finite acyclic `DIRECT` array arguments in canonical builtin Throwable traces
now preserve captured COW snapshots and compare nested count/key/value order;
shared child DAGs remain valid. Six native/model normal sources and three explicit
object/reference/cycle refusals pass. Own and independent strict fixtures cover
129 premises and three raw steps. The initial witness-scan compiler and pool-owner
fixture failures retain zero credit. [Array-trace review](coverage/semantics/throwable-trace-array-comparison-review.json).
Wider callback/recursive graphs remain partial.

Explicit builtin `__toString()` warms the physical `string` slot of canonical
same-kind `Exception`/`Error` pairs with empty traces and null previous links.
Five new warm sources and one unchanged cold control agree with PHP; two wider
controls remain Unsupported. Two strict source-reached fixtures pass 114 premises
and four raw comparison steps, including cache-before-line order and aggregate
continuation. The first aggregate budget fixture failure retains zero credit.
[Warm Throwable review](coverage/semantics/throwable-warm-comparison-review.json).
Wider Throwable graphs and pending comparisons remain partial.

Warm builtin caches now compare alongside nonempty canonical `Exception`/`Error`
traces with finite `DIRECT` primitive or acyclic array argument graphs. Equal
`Array` cache text continues to captured trace count/key/value order and COW
snapshots, while unequal cache text stops first. Five new normal sources and one
unchanged cold control agree with PHP; three object/reference/cycle controls
remain Unsupported. Strict source-reached checks pass 134 premises and five raw
steps. The first compiler-order failure retains zero credit.
[Warm trace review](coverage/semantics/throwable-warm-trace-comparison-review.json).
Previous links, materialized and pending comparisons remain partial.

Cold canonical builtin `Exception`/`Error` pairs now compare finite `previous`
chains of up to 16 same-kind, live, unmaterialized nodes with empty caches and
allocated empty traces. Seven new source agreements (six author, one independent) and three
exact wider Unsupported controls pass; one strict source-reached fixture checks 68 premises
and two raw steps through distinct equal links and an array tail. The native
same-line equality, null/object signs, inner order, shared identity and depth
three are preserved. [Previous-chain review](coverage/semantics/throwable-previous-comparison-review.json).
Longer, warm, nonempty-trace, mixed-kind, materialized and pending chains remain partial.

Physical warm `string` caches now compare at any node of finite canonical
same-kind builtin `previous` chains with empty allocated traces. One-sided
root or child warmth wins before deeper code; equal warmed cache text still
descends to the inner `code` slot. Six new source agreements (five author, one independent), two unchanged
normal controls and two exact Unsupported controls pass. Two strict
source-reached fixtures check 216 premises and eight raw steps across cold,
one-sided, reverse and equal-cache comparisons. The first premature-seek fixture
failure retains zero credit. [Warm previous-chain review](coverage/semantics/throwable-warm-previous-comparison-review.json).
Nonempty-trace, mixed-kind, materialized and pending chains remain partial.

Canonical cold builtin Throwable traces now compare finite captured array
arguments containing live primitive reference cells below a direct top-level
argument. Eight new source agreements (seven author, one independent), two
exact object/array-cell Unsupported controls and one unchanged direct control
pass. Source-reached strict checks pass 122 premises and three raw comparison
steps: a reference write changes the captured value while a direct sibling
keeps its COW snapshot, and repeated child entries retain one physical ID.
The initial pre-execution witness-helper compiler failure retains zero credit.
[Trace-alias review](coverage/semantics/throwable-trace-alias-comparison-review.json).
Warm, previous, materialized, pending and callback-bearing graphs remain partial.

Public user `__invoke` instances now serve as ordinary or optimized pipe RHS
callables. Eight new original-source comparisons agreed with pinned PHP at the
first direct cut, including strict type checks and reference returns; noncallable
and Closure controls were already normal. A later result-receipt correction
passes five reached stages/54 assertions for selected receiver, retired result
receipt, forged source/target rejection and left-before-right by-reference
refusal cleanup. The direct and corrected protocol cuts remain
separate; the two failed protocol attempts retain zero full credit.
[Object pipe review](coverage/semantics/pipe-object-callable-review.json).
Nonpublic and wider object callables were separate at that cut.

Private and inherited protected user `__invoke` methods now serve as ordinary
and optimized pipe RHS callables despite their declaration visibility Warnings.
Six new source comparisons and two unchanged controls agree exactly with PHP;
five source-reached stages check private/protected target identity, retired
result receipt and left/right owner cleanup. A separate inherited protected
by-reference refusal also agrees exactly. The six unchanged-baseline
Unsupported outcomes and failed fixture/affinity attempts retain zero credit.
[Nonpublic object pipe review](coverage/semantics/pipe-nonpublic-object-review.json).
Internal and wider object callables remain partial.

Canonical cold builtin Throwable traces now compare finite array-valued live
reference cells inside captured array arguments. Eight new source agreements
(seven author, one independent), two exact object/cycle Unsupported controls
and one unchanged primitive-cell control pass. Two source-reached strict fixtures
check 131 premises and three raw steps: whole-array retarget follows the cell,
direct siblings retain COW snapshots, and repeated child entries share one
physical ID and its owners. Count/key/value signs, seven operators, Error and
aggregate continuation/skip agree with pinned PHP.
[Array-cell trace review](coverage/semantics/throwable-trace-array-cell-comparison-review.json).
Object/cyclic, warm, previous, materialized and pending graphs remain partial.

Cold canonical builtin Throwable traces now compare live `stdClass` arguments
through their ordinary property tables. Matching finite direct trace shapes and
object/object leaf positions admit property count/key/value, live writes, nested
array COW, identity, both builtin kinds, all seven operators and aggregate
continuation/skip. Ten new exact native/model normal sources (nine author, one
independent) and three explicit Unsupported controls pass. One source-reached
fixture checks 88 premises and two raw steps: a reached comparison materializes
two property tables, then a second comparison reads their current values while
a separate source array has copied. The first compiler-order and fixture
empty-iteration failures retain zero credit.
[StdClass trace review](coverage/semantics/throwable-trace-stdclass-comparison-review.json).
Mixed object/scalar leaves, reference/object properties, cycles, warm caches,
previous links and pending comparisons remain partial.

Cold canonical builtin Throwable traces now compare captured plain source
objects of one methodless root class with initialized public declared slots.
Inline declared-slot priority and current materialized-table count/key/value
agree across live property writes, nested array COW, identity, both builtin
kinds, seven operators and aggregate continuation/skip. Eleven new exact
native/model normal sources (ten author, one independent) and three explicit
Unsupported controls pass. Separate reached-state cuts check 92 inline and
109 table premises with four raw steps total, including no-table persistence,
current table owners and pool absence, guard/budget and COW. The first strict
report failed an owner-count hypothesis and retains zero overall credit;
its passing inline row is retained separately from the corrected table run.
[User-object trace review](coverage/semantics/throwable-trace-instance-comparison-review.json).
Callback-capable classes, aliases, different-class/object-scalar leaves,
cycles, warm caches, previous links and pending comparisons remain partial.

Cold canonical builtin Throwable traces now compare finite current object
property graphs below captured arguments, including an object inside a direct
property array. Matching callback-free `stdClass` or plain methodless class
nodes descend through live slots and lazily materialized tables under a
16-physical-node path cap; shared children remain valid. Thirteen new original
normal sources (11 author, two independent) agree with pinned PHP, while four
different-class, object/scalar, reference and cycle cases remain exact
Unsupported controls. Two reached fixtures pass 286 premises and four raw
steps, checking four reached table materializations, live child writes, shared
physical IDs/owners, guard release, budgets and final bytes. The first
compiler-order failure and two earlier strict fixture failures retain zero
credit. [Nested object graph review](coverage/semantics/throwable-trace-object-graph-comparison-review.json).
Wider callback, reference, cyclic, warm, previous and pending paths remain partial.

Cold canonical builtin Throwable traces now compare finite live reference cells
inside callback-free object properties, including cells in property arrays and
one-sided ALIAS/direct pairs. Current defined scalar, array or matching object
payloads are read through the same physical table order, while direct copied
arrays retain COW snapshots. Twelve new native/model normal sources (11 author,
one independent) and three exact Unsupported controls pass. Two reached-state
fixtures check 236 premises and four raw steps, including a scalar-to-array
retarget and repeated shared cell. The first strict fixture failure and two
pre-execution harness attempts retain zero credit.
[Property-reference graph review](coverage/semantics/throwable-trace-property-alias-comparison-review.json).
Warm, previous, pending, callback and cyclic paths remain partial.

Exact builtin `Exception` versus `Error` pairs now return the standard handler's
class-mismatch order before inspecting canonical physical slots or captured
payloads. Normal nonpending live roots with unmaterialized images and a shallow
comparison guard give order `1` in both directions, preserving native false
relational operators even with warm caches, previous links or cyclic/callback
trace arguments. Six new native/model normal sources (five author, one independent)
and one unchanged same-kind cold control agree; a same-kind cycle remains exact
Unsupported. One reached fixture passes 74 premises/two raw steps with unchanged
heap/events and a skipped aggregate tail caster. The first aggregate-budget
fixture failure retains zero credit. [Cross-kind Throwable review](coverage/semantics/throwable-cross-kind-comparison-review.json).
Subclass, materialized-root, deeper-stack and pending cases remain partial.

Distinct exact source-constructible builtin Throwable kinds now take the same
early class-mismatch route before slots, traces or previous links. Parent/child,
sibling and eight-slot `ErrorException` examples return order `1` in both
orientations under normal nonpending completion, live canonical unmaterialized
images and guard depth below 16. Six new native/model normal sources (five
author, one independent), one unchanged Exception/Error control and one exact
same-kind Unsupported control pass. Reached severity and cyclic-tail fixtures
pass 125 premises/four raw steps. The first strict file-tag assertion and an
uncopied-source pre-execution baseline attempt retain zero credit; the reviewer's
first broad-affinity run also has zero credit.
[Builtin-kind comparison review](coverage/semantics/throwable-builtin-kind-comparison-review.json).
Generated-only `FiberError`, materialized roots, subclasses, deeper stacks and
pending states remain partial.

Canonical same-kind exact builtin Throwable roots beyond `Exception`/`Error`
now compare all physical slots under normal nonpending completion, null
`previous`, cold or warmed cache, allocated finite DIRECT scalar/carrier/array
traces and a guard below 16. `ErrorException` severity follows its seven
inherited slots; TypeError trace arrays preserve count/key/value order, and
RuntimeException warm cache text can precede numeric trace order. Seven new
native/model normal sources (five main author, one separate reached source,
one independent), three exact Unsupported controls and one unchanged Exception
control pass. Two strict fixtures pass 137 premises/four raw steps, including
equal warm cache text followed by severity and a skipped aggregate caster.
[Same-kind builtin review](coverage/semantics/throwable-builtin-same-comparison-review.json).
Alias/object/cyclic trace payloads, previous links, materialized roots,
generated-only `FiberError`, subclasses, deeper guards and pending states remain
partial.

Fresh, unheld user Iterators returned by a borrowed `IteratorAggregate` getter
now enter CONFIG unpack with DATA as their sole owner. Two original normal and
saved-key-Exception sources agree with PHP; 243 source-reached premises check
death before API/catch and authenticate the nonowning producer receipt. One
invalid-bool-key original was explicit Unsupported at that cut, with zero agreement.
Five adjacent original source controls and the affected retained-Aggregate
state fixture pass. Earlier timeouts and raw-step fixture failures retain zero
credit. [Fresh Aggregate Iterator review](coverage/semantics/config-aggregate-fresh-iterator-review.json).
Wider Aggregate return lifetimes and keys remain partial.

Fresh Aggregate-returned user Iterators with sole quiet DATA now raise the
unpack-site Error for NULL, bool or float keys while the producer stays live.
Three new originals, the formerly Unsupported Source109 bool-key original and
one independent-byte stable sole-CV producer source agree with PHP. Two fresh
named controls and four adjacent older sources remain exact. Three
source-reached fixtures pass 404 premises and six raw promotion/Error steps;
strict SL passes across 424 modules. The previous Source109 Unsupported result
keeps zero credit. A separately frozen source that rebinds the sole Aggregate
CV and kills the producer remains native-normal/model-interpreter-failure with
zero agreement. [Fresh Aggregate invalid-key review](coverage/semantics/config-aggregate-fresh-invalid-key-review.json).
Wider producer lifetimes, finalizers and keys remain partial.

Fresh Aggregate-returned CONFIG Iterators now keep their nonowning producer
receipt after the sole Aggregate CV is rebound during the first `key()` callback
and the producer allocation retires. The returned Iterator remains owned by
DATA through normal sends, an invalid second key, or a saved second-key
Exception; DATA retires before API reception or catch. Three byte-frozen
originals agree with pinned PHP in a CPU-pinned source cut, and separate
source-reached strict fixtures check 177+163+146 premises across normal,
Error and Exception paths. The original unchanged-model `interpreter_failure`
and the first incorrect abrupt-budget fixture keep zero credit. The receipt
still validates structural history rather than proving an unforgeable return
witness. [Retired producer review](coverage/semantics/config-aggregate-retired-producer-review.json).
Effectful producer finalizers, child storage and wider consumers remain partial.

Selected RIGHT NaN values in all four short-circuit forms now resume their
named Warning callback before `ZEND_BOOL` reads the same live float CV. A
returning callback supplies the final Boolean without a second Warning; a
supplied throw cancels the outer store, while an unselected RIGHT remains silent.
Eight original sources and 258 checked-source reached premises agree with pinned
PHP; two independent controls check unchanged NaN and an ineligible handler mask.
The [RIGHT NaN review](coverage/semantics/short-right-nan-warning-review.json)
records the bounded source, cell and handler contract.

Nonfolded `+`, `*` and `/` LEFT temporaries in ordinary `&`, `|` and `^` now
use their TMP2 rank against a direct RIGHT CV8. Source evaluation completes
LEFT first, but the bitwise handler converts RIGHT first: its 5.5 notice can
change the live CVs before the saved LEFT 12.5 notice. Eight new originals
agree with pinned PHP across normal results and second-handler cancellation;
one quiet control was already exact. Four source-reached recipes check 579
conditions, including the physical order and no-store catch. Two independent
controls check the opposite CV8/TMP2 order and an ineligible handler mask.
Other producers, objects and wider operand histories remain partial.
[Computed bitwise review](coverage/semantics/bitwise-computed-warning-review.json).

The same fresh sole-DATA CONFIG Iterator can now run a public
`__destruct` after its Aggregate producer dies at first `key()`. Normal
completion releases DATA before API entry; an invalid second bool key or a
saved second-key Exception releases it before catch. The destructor's output
and stamp change precede API/catch in three byte-exact PHP 8.5.10 agreements;
183+169+178 source-reached premises include the retired pending-Exception
operation exit. Strict compilation passes on 424 modules. The unchanged model
was Unsupported on all three originals, and the first incomplete candidate's
saved-throw failure has zero whole-packet credit. The destructor is bounded to
a public no-argument, by-value, nongenerator method with no child roots.
[Returned Iterator finalizer review](coverage/semantics/config-aggregate-iterator-finalizer-review.json).
Destructor throws/reentrancy, wider values and the structural retired-producer
receipt limit remain partial.

## Integrated behavior and entrypoints

Each family is bounded; its linked contract and inventory entries retain the
implemented cases, exclusions, exact tested revisions and independent reviews.

| Family | Current behavior and scope pointers |
| --- | --- |
| Source and compilation | Checked ASTs retain source occurrences, ordered publication, compilation phases and diagnostic priority. Dynamic source and request inputs have explicit provider boundaries. An absent dynamic HALT constant raises at its compiled lookup site. [Compiler](docs/semantics/SOURCE-COMPILER.md), [context](docs/semantics/SOURCE-CONTEXT.md), [dynamic source](docs/semantics/DYNAMIC-SOURCE.md). |
| Operators and warning decisions | Arithmetic/casts distinguish saved values from live CVs and stage supported diagnostics through callbacks. Direct NaN Boolean NOT/Boolean cast produce stricttrue/false after a live0.0 write; NaN array casting constructs a fresh singleton from that live float. Initially-NaN LEFT logical XOR caches post-warning truth across live RIGHT conversion, including remaining default Warning before a LEFT throw unwinds. Retained-reference Boolean NOT keeps its captured inner cell across source unset/rebinding. NaN LEFT short-circuit decisions use post-callback truth to skip or enter RIGHT. NaN shorthand ternary preserves the live selected value after its callback. A LEFT-array Warning may install a same-cell Stringable RHS; real conversion retains its selected receiver through source retargeting. A direct call's acquired RHS keeps a separate temporary owner until retirement before store/catch. Acquired Stringable LEFT survives the remaining RHS conversion; two distinct acquired Stringables retain both temporaries until ordered LEFT/RIGHT retirement. Borrowed CV timing stays distinct. Used print retains an acquired noarg function result through emission and protects integer1 across retirement before outer store. A direct missing RIGHT CV now selects a fixed fallback before acquired LEFT conversion, preserving ownership through its named handler. Copied fractional, NaN and range-only BITNOT inputs retain saved conversion results through callbacks. Direct-CV NaN used print keeps preformatted NAN through a Warning callback, emits it before pending exception search, and yields integer1 only normally. Direct-CV flat-array used print emits interned Array after a returning or throwing Warning handler; pooled and runtime-built array owners remain distinct. An acquired flat-array return from a named noarg function retains its temporary through the Warning callback and Array write, then releases before print1 or same-Exception search; two array sources, 143+112 ownership states and independent controls agree. [Owned print review](coverage/semantics/print-owned-array-warning-review.json). An explicit string cast now retains a named noarg by-value flat-array result through its Warning, releases it before assignment or, after handler-result cleanup, before catch handling, and returns interned Array without output; two new originals, 125+124 reached checks and two independent controls agree. [Owned cast review](coverage/semantics/cast-owned-array-warning-review.json). Ordinary concat now retains a named noarg acquired flat-array LEFT through its Warning and the post-handler same-cell Stringable RHS conversion, then releases before assignment; a handler throw skips RHS and releases before catch. Two new exact sources, one prior scalar control, 171+128 reached checks and two independent controls agree. [Acquired LEFT array review](coverage/semantics/concat-owned-array-warning-review.json). An acquired flat-array RIGHT now survives a completed direct-CV LEFT Stringable conversion and its own Warning handler; concat uses the saved LEFT despite CV rebinding and retires RIGHT before store or catch. Two new exact sources, a scalar control, 168+146 reached checks and independent fresh-return/ineligible-mask controls agree. [Acquired RIGHT array review](coverage/semantics/concat-right-owned-array-warning-review.json). Used plain-CV `.=` now retains a named noarg acquired flat-array RHS and the initially selected LHS string/cell across its Warning; normal commit overwrites callback B with AArray and copies the used result, while a supplied throw preserves B and the old outer value. Three exact sources, 154+125 reached checks and independent fresh-return/ineligible-mask controls distinguish owner2→1→0 and pending cleanup. [Acquired concat-assignment review](coverage/semantics/concatassign-owned-array-warning-review.json). [Operators](docs/semantics/ORDINARY-OPERATORS.md), [truth callbacks](docs/semantics/SOURCE-WARNING-TRUTH.md), [numerics](docs/semantics/NUMERICS.md). |
| Comparisons and arrays | Materialized private/protected declared tables preserve physical keys through normal numeric Notice handlers, including declared UNSET and initial typed holes. Live slots, retained cells and inline/outside retirement stay distinct. [Declared-UNDEF review](coverage/semantics/declared-undef-comparison-review.json), [nonpublic numeric review](coverage/semantics/nonpublic-numeric-comparison-review.json). Mixed nonpublic/dynamic tables preserve old live indirections, copied values and ordered retirement. [Mixed-table review](coverage/semantics/mixed-property-table-numeric-comparison-review.json). Materialized backed-hook tables compare physical slots without GET; real setters update live backing/cells and virtual declarations stay absent. [Backing-hook review](coverage/semantics/backed-hook-table-comparison-review.json). No-table hook-bearing ARRAY snapshots preserve later inline comparison and singleton/shared reference ownership. [Projection review](coverage/semantics/hook-array-projection-review.json). Cold builtin Exception/Error pairs compare canonical physical slots under normal completion, continuing equal array prefixes and skipping later casters after nonzero leaves. [Cold Throwable review](coverage/semantics/throwable-cold-comparison-review.json). Warm builtin caches compare their physical string slot before line under normal completion, with equal array continuation and nonzero skip. [Warm Throwable review](coverage/semantics/throwable-warm-comparison-review.json). Canonical nonempty builtin traces with direct primitive or valid string-carrier arguments now compare physical slots and trace arrays through native count/key/value order; named keys, aggregate continuation and Unsupported object/array arguments are checked. [Trace review](coverage/semantics/throwable-trace-comparison-review.json). Finite DIRECT array-valued trace arguments now retain captured COW snapshots, nested count/key/value order and repeated shared children under a path-local cycle guard. [Array-trace review](coverage/semantics/throwable-trace-array-comparison-review.json). Captured descendant ALIAS cells now read live primitive values while direct siblings retain the COW snapshot; repeated child IDs and owners are checked. [Trace-alias review](coverage/semantics/throwable-trace-alias-comparison-review.json). Array-valued ALIAS cells now follow their current finite graph across writes/retargeting, preserving direct sibling snapshots and shared child IDs. [Array-cell trace review](coverage/semantics/throwable-trace-array-cell-comparison-review.json). Live captured stdClass arguments now compare through lazily materialized current property tables under finite matching trace shapes, preserving nested COW and later writes. [StdClass trace review](coverage/semantics/throwable-trace-stdclass-comparison-review.json). Captured plain source objects now compare initialized public declared slots inline or through current materialized table count/key/value, with live writes and COW. [User-object trace review](coverage/semantics/throwable-trace-instance-comparison-review.json). Finite current object-valued property graphs below captured arguments now compare through matching callback-free child objects and reached live tables, admitting shared DAGs under a 16-node path cap. [Nested object graph review](coverage/semantics/throwable-trace-object-graph-comparison-review.json). Live reference cells in object slots, tables and property arrays now compare their current defined scalar, array or matched object payloads; ALIAS/direct pairs, COW siblings and shared-cell DAGs are source-reached under a finite path guard. [Property-reference graph review](coverage/semantics/throwable-trace-property-alias-comparison-review.json). Exact builtin Exception/Error class mismatch now returns order1 before slots or captured payloads; both orientations preserve false relational operators and skip cyclic traces and later aggregate casters under a shallow normal guard. [Cross-kind Throwable review](coverage/semantics/throwable-cross-kind-comparison-review.json). Distinct exact constructible builtin Throwable kinds now share that early class-mismatch route, including eight-slot ErrorException; six new sources and 125 reached premises/four raw steps agree. [Builtin-kind review](coverage/semantics/throwable-builtin-kind-comparison-review.json). Same-kind constructible builtin Throwables now compare canonical complete slots, including ErrorException severity last and finite direct trace arrays; seven new sources and 137 reached premises/four raw steps agree. [Same-kind builtin review](coverage/semantics/throwable-builtin-same-comparison-review.json). Warm cache text now precedes nonempty finite trace graphs; equal `Array` placeholders descend to captured count/key/value order. [Warm trace review](coverage/semantics/throwable-warm-trace-comparison-review.json). Cold canonical builtin previous chains compare up to 16 same-kind nodes through physical slots before resuming array tails. [Previous-chain review](coverage/semantics/throwable-previous-comparison-review.json). Physical warm caches at any finite previous node compare before deeper code or links, while equal cache bytes continue the chain. [Warm previous-chain review](coverage/semantics/throwable-warm-previous-comparison-review.json). Seven missing-CV comparisons admit bounded DIRECT/ALIAS arrays, including ordinary non-Stringable object leaves. Finite acyclic DIRECT/ALIAS graphs now admit descendant reference cells, preserving successive singleton unwrapping, shared-cell replacement, deep snapshots and final release. [Reference-graph review](coverage/semantics/undefined-comparison-reference-graph-review.json). [ALIAS DAG review](coverage/semantics/undefined-comparison-alias-direct-dag-review.json). [DIRECT graph review](coverage/semantics/undefined-comparison-direct-array-graph-review.json), [child-array review](coverage/semantics/undefined-comparison-array-payload-review.json). Undefined key variables in array literals resume Warning callbacks with a fixed empty key and live null/bool/int/float CVs; initially owning ordinary ARRAY CVs also preserve acquisition and retarget retention/debt through throw and balanced inverse writes. [Primitive review](coverage/semantics/array-literal-undefined-key-warning-review.json), [ARRAY-CV review](coverage/semantics/array-literal-undefined-key-array-cv-review.json). NULL-key literals support bounded CV, returned, temporary and pooled CONST values. Nested DIRECT TMP graphs preserve shared physical child edges and handler-time COW, cascading unowned runtime descendants while folded siblings remain pooled. [Nested TMP review](coverage/semantics/array-literal-null-key-array-tmp-subtree-review.json), [nested CONST review](coverage/semantics/array-literal-null-key-constant-subtree-review.json). String R-offset callbacks preserve selected old carriers and live primitive cast keys; fixed bounds completion survives source/key unset, with pending-throw default/suppression. [String-read review](coverage/semantics/string-offset-read-warning-review.json). [Comparisons](docs/semantics/COMPARISONS.md), [dimensions](docs/semantics/DIMENSIONS.md), [object-reference review](coverage/semantics/undefined-comparison-object-reference-array-review.json). Initialized user Iterator literal spreads retain raw current references through key before DIRECT copy, with bounded COW and invalid-key/current/key/next cleanup. [Iterator spread review](coverage/semantics/array-iterator-unpack-review.json). Named Generator literal spreads use native resumes, preserve yield cache edges through resumed code/CLOSED, and retire DATA then owning INPUT before transferring or canceling the protected builder. [Generator spread review](coverage/semantics/array-generator-unpack-review.json). Named IteratorAggregate CVs now invoke a borrowed getter and transfer its owned Iterator/Generator return into DATA; stable-self/CLOSED acquisition errors preserve return cleanup and the builder. [Aggregate spread review](coverage/semantics/array-aggregate-unpack-review.json). Finite acyclic DIRECT cache graphs now preserve shared child edges, deep COW, pool siblings and abrupt cascading retirement in both spread engines; builder backedges remain refused. [Nested-cache review](coverage/semantics/array-traversable-nested-cache-review.json). Ordinary CV Iterator DATA destructors retain the builder through normal and replacement-key release; invalid-key eager cleanup releases the builder before DATA and preserves the current cache until later retirement. [DATA destructor review](coverage/semantics/array-iterator-data-destructor-review.json). Ordinary no-destructor Iterator current arrays now admit finite DIRECT descendants with ordinary scalar reference cells; held aliases stay shared across COW and a sole cell unwraps after external alias removal, including an Aggregate-returned Iterator. Three exact source agreements and 273 focused conditions retain separate strict/source and corrected-fixture cuts. [Reference-cache review](coverage/semantics/array-traversable-reference-cache-review.json). Named by-value Generator spreads now retain scalar reference leaves in finite DIRECT array yields, including an Aggregate-returned Generator. Held/drop COW and weakly observed last-DATA retirement agree in four originals; strict421 and 367 focused premises pass at separate tested cuts, while the first peer frontier failure remains zero credit. By-reference producers keep their old scope. [Generator reference-cache review](coverage/semantics/array-generator-reference-cache-review.json). Named by-reference Generator spread dereferences a real outer cell into a copied row; later rebind leaves that row intact while inner aliases share writes. Dropping an outside leaf alias exposes COW singleton unwrap, and a supplied throw retires the outer cell before builder-held row/leaf cancellation. Four original source agreements, strict423 and 588 focused premises (six raw) retain separate cuts; unchanged baseline Unsupported0. [By-reference Generator cache review](coverage/semantics/array-generator-byref-reference-cache-review.json). Ordinary no-destructor by-reference Iterator current cells remain raw through key callbacks; key-time rebinding selects the new DIRECT spread row while saved old and inner scalar aliases stay distinct. Held/drop COW and a supplied key throw with authentic atomic discard/prune have four exact source agreements, strict424 and 528 focused premises (four raw) at separate cuts; unchanged baseline Unsupported0. [By-reference Iterator cache review](coverage/semantics/array-iterator-byref-reference-cache-review.json). Ordinary no-owning-field by-reference Iterator rows now remain valid through real DATA destruction: last-DATA release protects the scalar-ALIAS builder while destructor writes precede assignment; a retained outside Iterator defers destruction, and supplied key throw preserves its Exception through builder cancellation. Four exact source agreements (including one Aggregate promotion), strict424 and 670 direct-source focused checks (664 Boolean/six raw) retain separate tested cuts; unchanged baseline Unsupported0. [By-reference destructor review](coverage/semantics/array-iterator-byref-destructor-review.json). |
| Calls and configuration | Ordinary/scoped/captured calls preserve selected targets, argument order, references and genuine callback frames. Public user-method array pipes now retain the selected receiver after RHS-array retirement and report by-reference refusal and lookup errors at their native lines, and retire an invalid owning RHS before the held left value. [Array pipe review](coverage/semantics/pipe-array-callable-review.json). Public static user-method string pipes now accept literal, variable and temporary RHS values, with exact lookup/send sites and reference result mode. Nine exact CLI agreements and five reached stages/65 assertions are recorded separately in the [method-string pipe review](coverage/semantics/pipe-static-method-string-review.json); scoped, nonstatic and magic method-string forms remain open. Optimized public-static first-class RHS method strings now accept fixed, variable and temporary names, including one leading slash, with eleven initial direct agreements and one corrected leading-slash direct agreement, a final 12-source request pass and six reached stages/79 assertions. [Optimized method-string pipe review](coverage/semantics/pipe-optimized-static-review.json). Ordinary named-function string carriers now cover optimized first-class and nonoptimized pipe RHS values, with 19 exact CLI outcomes and five reached stages/72 assertions; dynamic selected-name history remains limited at later call tasks. [Named-carrier pipe review](coverage/semantics/pipe-named-carrier-review.json). Closure::call captures packed or late-named receivers separately from canonical forwarded values; source histories preserve defaults, reference-warning order and raw traces after source replacement. Outer duplicates skip later producers; missing/type checks follow successful collection before inner errors. [Closure contract](docs/semantics/CLOSURE-CALL.md), [outer-binding review](coverage/semantics/closure-call-outer-binding-review.json). Two singleton INI_SET packs retain raw NULL/quiet ARRAY, callee and option through later effects. Initialized user Iterators stream integer-key/string sends into INI_SET with callback ordering, pre-API retirement and supplied-Exception recovery. Non-generator getIterator producers transfer retained Iterator or fresh named Generator returns into DATA; Generator-method producers preserve a real owned receiver and historical method/source receipt. Fresh named Generator consumers finish native resumes and retire quiet sole DATA before historical API reception; temporary named-call results retain distinct INPUT until DATA then INPUT retirement. CV consumers reuse the first-yield cache, reject advanced rewind after DATA acquisition and reject CLOSED before DATA. Bounded CLOSED return payloads retire through real storage pins before reception/catch, preserving argument-site callbacks and pending recovery. Direct-CV Generator and initialized user Iterator string keys check named destinations before the next yield or callback. Two Aggregate-produced named Iterator cases agree with PHP. A direct noarg user factory now keeps temporary Iterator INPUT separate from DATA and retires quiet last INPUT before API or catch. Source104 handles invalid primitive Iterator keys under a live selected-Iterator CV, raising the unpack Error before next/API and retiring DATA before catch. Source106 extends quiet temporary Iterator factories to that Error, retiring DATA then INPUT before catch. Fresh borrowed Aggregate getters return quiet unheld user Iterators whose sole DATA retires before API or catch; a nonowning producer receipt preserves history. Source111 admits quiet invalid primitive keys for live producer receipts, raising the unpack Error before next/API and retiring sole DATA before catch; its producer-death baseline was an interpreter failure with zero credit. Source114 continues the same fresh Iterator after its sole Aggregate CV retires during first key(), with exact normal, invalid-key and saved-Exception source outcomes and separate reached cleanup checks. Source115 admits its public no-child Iterator destructor at last sole-DATA release; normal, invalid-key and saved-Exception outcomes match PHP, with separate retired cleanup and pending-Exception checks. Bounded WeakMaps distinguish empty arity failure from occupied object-key Error before any current copy. [Calls](docs/semantics/SOURCE-CALLS.md), [include/configuration](docs/semantics/INCLUDE-SOURCES.md), [two-pack review](coverage/semantics/ini-set-two-pack-null-array-value-review.json), [Iterator CONFIG review](coverage/semantics/config-iterator-unpack-review.json), [WeakMap CONFIG review](coverage/semantics/config-weakmap-unpack-review.json), [Aggregate CONFIG review](coverage/semantics/config-aggregate-iterator-unpack-review.json), [Generator CONFIG review](coverage/semantics/config-generator-unpack-review.json), [Aggregate→Generator review](coverage/semantics/config-aggregate-generator-unpack-review.json), [sole DATA review](coverage/semantics/config-generator-sole-data-review.json), [method-producer review](coverage/semantics/config-aggregate-generator-method-review.json), [call-result review](coverage/semantics/config-generator-call-result-review.json), [initial-state review](coverage/semantics/config-generator-initial-state-review.json), [return-storage review](coverage/semantics/config-generator-return-storage-review.json), [named-send review](coverage/semantics/config-generator-named-unpack-review.json), [named Iterator review](coverage/semantics/config-iterator-named-unpack-review.json), [temporary Iterator review](coverage/semantics/config-iterator-temp-call-review.json), [invalid Iterator key review](coverage/semantics/config-iterator-invalid-key-review.json), [temporary invalid-key review](coverage/semantics/config-iterator-temp-invalid-key-review.json), [fresh Aggregate Iterator review](coverage/semantics/config-aggregate-fresh-iterator-review.json), [fresh Aggregate invalid-key review](coverage/semantics/config-aggregate-fresh-invalid-key-review.json), [retired producer review](coverage/semantics/config-aggregate-retired-producer-review.json), [returned Iterator finalizer review](coverage/semantics/config-aggregate-iterator-finalizer-review.json). |
| Constants and callable values | Bounded DEFINE/CONSTANT/DEFINED preserve source authority, scopes and primitive/array/object snapshots. Captured intrinsic Closures preserve selected callees, strict/weak reception, raw/received traces, COW/reference sharing and callback/destructor cleanup. Singleton ARRAY packs bind positional/named global-string snapshots after source array retirement, constrained by literal facts. [Constant contract](docs/semantics/SOURCE-USER-CONSTANTS.md), [query-pack review](coverage/semantics/constant-owned-query-pack-review.json). |
| Classes and properties | Visibility, references, typed writes, hooks, magic access and clone have bounded routes. Selected typed backed `&get` preserves backing aliases, independent read copies and Get-before-rebind Error. [Typed reference-Get review](coverage/semantics/reference-get-hooks-review.json). The matching untyped backed form keeps the alias unconstrained, including implicit-null backing, while retaining copy/rebind/lifetime order. [Untyped reference-Get review](coverage/semantics/untyped-reference-get-hooks-review.json). An unchanged direct Child now inherits Parent's backed `&get` while retaining Child receiver, Parent lexical scope, typed or untyped alias rules, copy/lifetime and Get-before-rebind order. [Inherited reference-Get review](coverage/semantics/inherited-reference-get-hooks-review.json). A direct Child plain equal-typed redeclaration now supplies its own slot and type source to Parent's inherited `&get`, preserving Parent lexical scope, Child receiver, copy/lifetime and Get-before-rebind order. Three sources and 341 Boolean/three raw reached checks pass; deeper and untyped redeclarations remain partial. [Plain Child reference-Get review](coverage/semantics/plain-child-reference-get-hooks-review.json). The matching untyped plain Child now uses its own scalar or implicit-null slot without a type source; aliases/copies survive Child retirement and rebind still calls Get before Error. Three exact sources and 364 Boolean/three raw checks pass; deeper Child chains remain partial. [Untyped plain Child review](coverage/semantics/untyped-plain-child-reference-get-hooks-review.json). An unchanged Grandchild over the same plain Child slot now retains Parent lexical scope, Grandchild called class, Child typed source or untyped absence, and Get-before-rebind order. Four exact sources and 392 Boolean/four raw reached checks passed at that cut; its Greatgrandchild control then remained Unsupported. [Grandchild reference-Get review](coverage/semantics/grandchild-reference-get-hooks-review.json). The bounded linked chain route selects the latest slot when unchanged classes declare no properties/interfaces/constants and redeclaring classes declare only that same-type public plain property without set restrictions, interfaces or constants; five exact sources and 449 reached/five raw checks pass. [Reference-Get chain review](coverage/semantics/reference-get-chain-review.json). Distinct-name sibling properties, own constants and marker interfaces now coexist with that selected linked getter through memberful descendants; four exact sources and 538 reached/four raw checks pass. [Memberful reference-Get review](coverage/semantics/reference-get-memberful-review.json). Accessible nonpublic UNSET Get retains the caller-selected physical DECL/type across Child scope and backing population. Bounded literal-this BYVAL/BYREF Get authenticates receiver identity and preserves saved history through callbacks and method retirement. Caller-source declaration selection also wins over public Child shadow across the existing producers, with fresh actual-access agreement. Named noarg owned factories admit bounded BYVAL/BYREF nonpublic/denied Get, keeping references live through local cleanup and detaching COPY before receiver retirement. CV/owned/literal-this reference getters share saved-declaration verification, preserve existing type sources and attach no target constraint. Valid historical parameter-backing receipts now preserve exact reads/conflicts or clear on committed conversion after source detach. By-reference factory receivers now retain the original input cell through COPY, preserving distinct early Get-hold and later input retirement. Bounded same-name recursion distinguishes captured NULL, typed Error and visibility Error; real guards survive local cleanup. [Properties](docs/semantics/SOURCE-PROPERTIES.md), [classes](docs/semantics/SOURCE-CLASSES.md), [recursion review](coverage/semantics/magic-get-recursion-review.json), [declared-UNSET review](coverage/semantics/magic-get-unset-recursion-review.json), [typed reentry review](coverage/semantics/magic-get-recursive-error-review.json), [denied reentry review](coverage/semantics/magic-get-denied-recursion-review.json), [scoped getter review](coverage/semantics/magic-get-scoped-unset-review.json), [literal-this review](coverage/semantics/magic-get-direct-this-review.json), [selected-declaration review](coverage/semantics/magic-get-lexical-selection-review.json), [owned-access review](coverage/semantics/magic-get-owned-access-review.json), [scoped-reference review](coverage/semantics/magic-get-scoped-reference-review.json), [owned-reference review](coverage/semantics/magic-get-owned-reference-review.json), [literal-this reference review](coverage/semantics/magic-get-this-reference-review.json), [parameter-receipt review](coverage/semantics/magic-get-param-reference-review.json), [receiver-cell review](coverage/semantics/magic-get-receiver-cell-review.json). |
| Generators and Fibers | Direct named and ordinary method bodies entered by CURRENT/NEXT preserve their authentic resumer across Fiber suspension and supplied-Throwable injection, with distinct fresh/cached reentry Errors. Method receivers preserve their actual callee owner, closed self-yield cache and supplied-Throwable retirement. Ordinary named helpers retain their real caller frames, parameter owners and unique underlying resumer. [Helper-frame review](coverage/semantics/generator-fiber-helper-transfer-review.json). [Transfer review](coverage/semantics/generator-fiber-transfer-review.json). Shared delegation, initialization history, unused snapshots and abrupt SEND cleanup retain their bounded contracts. [Generators](docs/semantics/GENERATORS.md), [Fibers](docs/semantics/FIBERS.md), [delegation](docs/semantics/GENERATOR-DELEGATION.md), [refresh review](coverage/semantics/generator-refresh-unused-current-review.json). Named native delegation preserves actual resumer/claim chains across Fiber transfer. Five exact fresh/cached and Throwable sources,459 component/short-budget and135 whole-completion premises pass; earlier timeouts remain separate. [Delegation transfer review](coverage/semantics/generator-fiber-delegation-transfer-review.json). Direct one-value SEND now preserves buffer/delivered/returned owners through Fiber transfer and supplied-Throwable cleanup. [SEND review](coverage/semantics/generator-fiber-send-transfer-review.json). Plain Closure-created callees preserve copied/reference captures, closed-callee lifetime and fresh linked reentry Errors. [Closure review](coverage/semantics/generator-fiber-closure-transfer-review.json). Direct named by-reference NEXT preserves its old cache cell across Fiber suspension, source-name rebinding and supplied-Throwable cleanup; a defined cache gives one outside reentry Error. [Reference cache review](coverage/semantics/generator-fiber-reference-transfer-review.json). Primed direct named Generator::throw now transfers its saved Throwable and by-value cache through catch/finally Fiber suspension: three primed THROW sources, one fresh CURRENT control and 75 reached-state premises pass, while the original two THROW baselines remain Unsupported. [THROW transfer review](coverage/semantics/generator-fiber-throw-transfer-review.json). Fresh pre-first-yield direct named THROW now retains a temporary Exception in its advancing saved resumer across Fiber suspension; normal escape, caught recovery and supplied-Fiber-Throwable Previous order have three exact sources and 86 reached-state premises. Two post-yield fresh and one primed source already matched unchanged semantics. [Fresh THROW review](coverage/semantics/generator-fiber-fresh-throw-transfer-review.json). Cached direct named by-reference Generator::throw preserves a live reference cell and saved Throwable through catch/finally Fiber suspension; four new exact sources, one unchanged by-value control and 102 source-reached assertions pass. [Reference THROW review](coverage/semantics/generator-fiber-reference-throw-transfer-review.json). Primed public method-created by-value Generator::throw preserves the authenticated receiver and saved Throwable through catch/finally Fiber suspension; four new exact sources, one unchanged direct named control and 157 source-reached assertions distinguish scalar completion from self-cache lifetime. [Method THROW review](coverage/semantics/generator-fiber-method-throw-transfer-review.json). Primed plain unbound Closure-created by-value Generator::throw now retains the real callee, copied/reference captures, old cache and temporary Throwable across Fiber catch/finally; five new exact sources and 302 reached assertions pass, with one unchanged direct control. [Closure THROW review](coverage/semantics/generator-fiber-closure-throw-transfer-review.json). Fresh unbound Closure-created by-value THROW now transfers before its first yield with the saved original Throwable and distinct copied/reference captures; four new exact sources (including independent pre-yield Fiber::throw), one unchanged primed control and 117 reached premises pass. [Fresh Closure THROW review](coverage/semantics/generator-fiber-fresh-closure-throw-transfer-review.json). Cached unbound Closure by-reference THROW now retains its authenticated old reference cell, Closure capture and saved Throwable through Fiber catch/finally; three authored and one independent exact source, two unchanged controls and 136 custom reached checks pass at this bounded cut. [Closure reference THROW review](coverage/semantics/generator-fiber-closure-reference-throw-transfer-review.json).  I67 admits fresh unbound Closure-created by-reference THROW before first yield with an empty cache and authenticated Closure/producer. Four new exact sources (including an independent pre-yield Fiber::throw abort), two unchanged controls and 118 custom reached checks pass at the private cut; the original 75-second unchanged reference timeout has zero credit and a selected 240-second run reached Unsupported. Method by-reference/fresh, bound/delegated and wider lifetimes remain partial. See generator-fiber-fresh-closure-reference-throw-transfer-review.json. I68 admits primed public method-created BYREF THROW with an authenticated cached cell/receiver: three authored plus one independent exact sources, two unchanged controls, strict424 and 129 reached checks pass; three authored unchanged baselines were Unsupported. Fresh method, bound/delegated and wider lifetimes remain partial. [Method reference THROW review](coverage/semantics/generator-fiber-method-reference-throw-transfer-review.json). |
| Returns and lifetime | Bounded by-reference return/finally chains retain remaining owners, local catches and consumed recovery through normal/throw retirement. First C retirement with one REF/object remainder preserves local catch, the computed-return Notice and a detached caller cell. Bounded WeakMap slots preserve Value/reference-cell ownership, Key notification and selective mutation. Finite traversal, owned Iterator DATA and manual weak-Key cursors preserve copied targets, escaped aliases, normalization and staged cleanup. Selective Key retirement and last-owner finite Map or owned Iterator cleanup preserve observed weak-reference visibility, ordinary Value copies, retained sibling storage, bounded `isset` reentry and pending Exceptions. Conditional GC supports canonical reference/array backedges and copy/COW protection, transitive entry-Key protection with selective multi-entry normalization, and bounded Map/Value cycles with an independently live Key. [WeakMap review](coverage/semantics/weak-map-review.json). The finite `returns_verify` work is complete; wider PHP return and lifetime coverage remains open. [Return contract](docs/semantics/SOURCE-REFERENCE-RETURNS.md), [eager cleanup](docs/semantics/SOURCE-EAGER-DESTRUCTORS.md), [return review](coverage/semantics/reference-return-local-cv-lifetime-review.json). |
| Diagnostics and environment | Supported warning/exception handlers retain raw registration, selected callback and emitting frame. Multi-expression echo writes a flat-array operand after its Warning callback, then evaluates or skips later siblings. A second array operand reads a CV built by the first handler, raises its own Warning and writes before either later evaluation or the supplied Exception search. One default chunk-zero buffer started inside a named Warning handler now captures cached Array/NAN print and first-child echo bytes before print1, the next sibling, or the same-Exception catch; five original sources, 591 reached checks and two independent controls agree. [Buffered output review](coverage/semantics/buffered-output-warning-review.json). [Echo](docs/semantics/SOURCE-ECHO.md), [handlers](docs/semantics/SOURCE-ERROR-HANDLERS.md), [exception handlers](docs/semantics/SOURCE-EXCEPTION-HANDLERS.md), [request inputs](docs/semantics/REQUEST-INPUTS.md). |

Direct `constant` calls with a singleton ARRAY unpack from a raw literal or an
ordinary variable expression resolve the filename-local HALT offset through
key `0` or `name`. A live direct item or retained reference cell must agree
with the captured pack; rebinding the cell's original variable name leaves the
array's reference intact. The reference-cell increment has seven distinct exact
sources and five reached fronts/515 checks; wider packs remain partial.
[Literal-pack review](coverage/semantics/halt-pack-review.json),
[CV-pack review](coverage/semantics/halt-cv-pack-review.json),
[alias-pack review](coverage/semantics/halt-alias-pack-review.json).

Direct public instance-method calls now accept an initialized user Iterator CV
unpack. They retain the selected receiver across key callbacks, bind positional
and named values, report the declaring class in by-reference warnings, and
preserve invalid-key, throwing-key and warning-handler cleanup order. Five new
author method originals and a destructor-bearing handler original agree with
PHP; six source-reached stages check selected targets, saved origins, owners and
cleanup. Earlier failed fixture cuts retain zero credit. A temporary Iterator
method operand remains explicit Unsupported; other callable targets and wider
argument sources remain partial.
[Method Iterator review](coverage/semantics/method-iterator-unpack-review.json).

Accepted eval/include class and interface declarations fetch ordered direct
interfaces before publication. Supported mixed class plans resolve the parent,
then one direct trait or two distinct traits before their interfaces; the
tested two-trait eval plan also composes one `insteadof`/`as` adaptation.
Wrong-kind traits stop later lookup, and later failures retain earlier eval
functions and the dynamic Error origin. The [interface](coverage/semantics/multi-interface-autoload-review.json),
[mixed-dependency](coverage/semantics/mixed-dependency-autoload-review.json) and
[two-trait](coverage/semantics/ordered-two-trait-autoload-review.json) reviews retain
their original bounded source, reached and preservation evidence.

Fixed-name ordinary `new` now recognizes an unlinked source class through the
authenticated saved continuation of its entered dependency loader. It raises
the missing-class Error without a redundant loader call; after failed linking
unwinds, a later `new` autoloads normally. Two repaired author originals and
one independent interface-loader original agree exactly with pinned PHP; one
unchanged same-name recursion control remains exact. All three repaired-source
baselines completed normally with wrong output. Strict compilation of 424
modules and two reached fronts with 67+73 premises pass. Separately, 26 recursion
assertions and 19 linked class-constant/new predicates pass as preservation.
Joined strict compilation over the actual tail also passes. Earlier predictions,
candidate mismatches and fixture elaboration failures keep
zero credit. Dynamic-name `new`, other declaration kinds and wider reentry
remain partial. [Reentrant lookup review](coverage/semantics/reentrant-unlinked-new-review.json).

Ordinary dynamic array callables selected as public user object or class-string
static methods now accept initialized Iterator CV unpack. Selection survives
callback rebinding; inherited static calls keep the child called scope while
by-reference warnings name the declaring class. Abrupt invalid and throwing
keys retire a selected receiver before catch. Six exact original comparisons
and seven source-reached stages/126 assertions pass on the private tested cut;
neighboring array and direct-method controls pass. Earlier cleanup failures
remain zero credit. The [CALL119 review](coverage/semantics/array-callable-iterator-unpack-review.json)
records the scope and raw evidence. Wider callable and operand forms remain open.

Ordinary dynamic real, arrow and named user-function first-class Closures now
accept initialized Iterator CV unpack. The selected Closure survives callback
rebinding; scoped and unscoped by-reference Warnings name the selected function.
Invalid-key cleanup uses a PREP-created origin witness after the Closure and
captured cells retire. Nine source outcomes agree exactly with PHP,
and twelve reached fixtures pass 224 checks, including wrapper exclusions and
retired cleanup negatives. Earlier failed cuts retain zero credit. `bindTo`
clones, method wrappers, `Closure::call` and non-CV operands remain open.
[CALL120 review](coverage/semantics/closure-iterator-unpack-review.json).

Dynamic calls through a public user object `__invoke` CV now accept initialized
Iterator CV unpack. A selected receiver survives key-time CV rebinding; inherited
named and by-reference parameters keep their effective method and declaring-class
Warning. Invalid and throwing keys retain authentic retired-receiver cleanup.
Five authored and one independent frozen source agree byte-for-byte with pinned
PHP; seven source-reached fixtures pass 146 assertions. Independently reviewed
actual-tail composition passes strict compilation of 424 modules. A native-positive
temporary callee remains explicit `Unsupported`. The earlier fixture failures
and all unchanged Unsupported baselines have zero agreement credit. The saved
target ID carries original selection after retirement; same-class historical
selection is not reconstructed. Wider callee/operand forms remain partial.
[CALL121 review](coverage/semantics/invokable-iterator-unpack-review.json).

## Active and unintegrated work

| Track | Owner-confirmed current work |
| --- | --- |
| A62 | Owning-field Iterator lifetime; peer checks pass for throwing-key and pending invalid-key cleanup. |
| COMP145 | Builtin Throwable previous chains; private implementation. |
| CALL122 | Non-CV Iterator unpack operands; preparation. |
| I69 | Fresh method by-reference Generator THROW; unchanged-model baseline work. |
| V110 | Temporarily held/unintegrated after repeated generic cybersecurity-risk flag; CPU3 released, exact rejected action unknown. Accepted source3 retained. |
| COMP123 | Held unrun; no actor. |

Iterator49/50/51/52/53/54/55/56/57/58/59/60/61/62/63/64, V99/V100/V101/V102/V103/V104/V105/V106/V107/V108/V109, M132–M157, A46/A47/A48/A49/A50/A51/A52/A53/A54/A55/A56/A57/A58/A59/A60/A61, OP79/80/81/82/83/84/85/86/87/88/89/90/91/92/93/94/95/96/97/98/99/100/101/102/103/104/105/106, Source86/87/88/89/90/91/92/93/94/95/96/97/98/99/101/102/104/106/113/114/116/117, CALL113, COMP118/119/120/121/122/124/125/126/127/128/129/130/131/132/133/134/135/136/137/138/139/140/141/142/143/144 and CLASS119/120/121/122/123/124/125/126/127/128/129/130/131/132/133/134/135/136/143 are integrated
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
