# Object property storage

Class descriptors record ordered public/protected/private instance declarations, types and
source-backed defaults. Each allocation creates owned slots: a typed property
without a default starts uninitialized, while an untyped one starts as null.
An override of an inherited nonprivate declaration must preserve its type and
reuse its slot; visibility narrowing is checked first. Inherited private
declarations retain separate declaring-class slots and impose no child type
constraint. Early and deferred links enforce the same conditions. Reads, writes,
`unset`, `isset`, `empty` and computed names use the same slots; writes apply
the declared type and report the declaring class. A simple typed property assignment
converts against its declaration before checking the current alias's other type
sources, and returns the converted value. Aliased compound updates keep the generic
reference checks. Dynamic properties use the
same storage, with the pinned deprecation on ordinary source classes and no
deprecation on `stdClass` or a source class/descendant with the single builtin
`#[AllowDynamicProperties]`. Allowed creation uses the existing slots and bypasses
deprecation capture; see the [attribute review](../../coverage/semantics/allow-dynamic-properties-review.json).
A leading-NUL computed name raises the engine error
for read, write and unset, while quiet tests remain silent.

Main-scope `$base->{name()}` reads now defer the simple CV lookup until a
source-proved quiet USER name helper returns. Its exact body binds the two global
CVs, copies the preallocated replacement into the base and returns a literal
non-NUL key. Both touched cells start plain; an independent CV keeps the old
object live, and the helper's ordinary global binding may then mark those cells
referenced. Parentless methodless classes with initialized public untyped scalar
slots bound this route. The zero-argument helper has empty attributes/parameters
and an untyped by-value header; source/body/code/selected-target authority stays
explicit. The main route requires an unsaved caller context; active cleanup,
resumable, error-handler, tick and buffered-output entry remains outside both
this and the bounded reader route below.

The existing `PROPERTY_BASE_NAME(BASE_VALUE(VARIABLE))` carrier owns no object
or cell. Saved-main/reader history uses immutable CV/site/line and continuation,
then completion reads the current caller CV into the ordinary property base. It
never authenticates history by rereading the old value or retained alias. Old
pending-writer validity remains independent of the new read-specific guards;
magic, hooks, typed/reference targets, wider helpers and callers keep their
previous boundaries. The [review](../../coverage/semantics/property-cv-dynamic-name-review.json)
records native22 versus original model11, the corrected source agreement and
130 independent source/owner/budget conditions. This adds no dynamic-property
creation or typed-property support.

A zero-argument ordinary named reader, directly called from main, can use the
same lookup through an existing global-CV reference. Its empty-attribute, untyped
by-value header, nongenerator body/source membership and real reader/main frame
are authenticated by the existing context law; no new reader-body language is
introduced. Entry proves the local receiver and real request table share the
identical cell, then qualifies replacement and retained alias on that real table.
Equal names or values do not establish this identity. Canonical live-reference
checks plus per-cell container/literal/native exclusions keep typed property
sources, coercion/backing, released cells and debts outside the route. Main
admission keeps its exact nonreference-cell test. Saved-reader history does not
reread those mutable cells, the global table or old alias; property slots remain
untyped DIRECT, and reference producers/pending-writer rules stay unchanged.
The [reader review](../../coverage/semantics/property-reader-global-name-review.json)
keeps its original model11/native22 mismatch, corrected source1 and 151 focused
conditions separate from the earlier main-only cut and a fixture-only failure.

A single terminal `isset($base->{name()})` now shares the same deferred receiver
transport. Its sole property must occupy the actual parent's FIELD0/INDEX0; both
real origin returns, false mode, compiled property line and terminal ISSET_NEXT
are authenticated together. The existing quiet presence consumer sees the
replacement's initialized NULL after the name returns, without a getter or old
object pin. Main/reader cell and target bounds remain unchanged. Empty/truth,
NaN warnings and multi-operand isset gain no new route. The
[terminal review](../../coverage/semantics/property-terminal-isset-name-review.json)
separates the original true/false model mismatch, corrected source1/133 focused
conditions and the fixture-only presemantic failure.

A quiet `$base->{name()} ?? 7` read uses the same deferred CV transport when
the RHS is an integer literal. Its actual coalesce parent, property LHS, identical
RHS AST, both compiled runtime lines and real parent return authenticate the
`COALESCE_QUIET` continuation. Published code flags retain their actual values;
the source query does not infer constantness from literal syntax. Saved-task
history remains independent of mutable receiver values and aliases. The existing
coalesce kernel tests only NULL: the replacement NULL schedules the lazy RHS,
while nonNULL values, including falsey scalars, use the existing selected-value
copy. This adds no RHS producer or NaN-specific Warning/handler coverage.
Main/reader, cell, helper and plain-slot bounds stay unchanged, as do the old
value/isset/writer routes and the coalesce kernel. The
[review](../../coverage/semantics/property-coalesce-name-review.json) separates
the original model11/native7 mismatch, affected source1 and 136 first-pass
source/owner/history/budget conditions from the actual current load.

Terminal nullsafe value reads preserve their original CV check before the same
quiet name helper, then fetch the current CV after it returns. The
[nullsafe contract](SOURCE-NULLSAFE-PROPERTIES.md) keeps this checkpoint distinct
from the delayed fetch and the unchanged initial-NULL skip. When the quiet helper
instead leaves NULL, its normal terminal fetch uses the existing Warning/NULL
rule without a second checkpoint, within the no-handler boundary.
Terminal single isset and integer-fallback coalesce also preserve their true
quiet nullsafe checkpoint before selecting the replacement object's slot; their
actual parent/consumer line authority is distinct from the access line.

Selected terminal CV/literal `empty` of an initialized public nonreadonly float
property now warns on NaN before rereading the live slot. Handlers can change it
to `0.0` (empty true), `1.0` (false), or leave NaN (false, without another Warning).
The continuation captures receiver/key/source history without owning a receiver
or manufacturing BASE; it survives source-CV nulling while a saved alias stays
live. A supplied throw preserves the same Exception at catch, and the receiver
destructor follows result/catch after the alias is cleared. Four originals and
469 focused premises (409 reached +60 derived) cover these paths, authenticity
refusals and budgets. Changing an initially direct slot into a reference,
unsetting/retyping it or retiring its receiver remains outside that direct-slot
slice; wider quiet-CV GC stays open.
[Public NaN review](../../coverage/semantics/quiet-public-nan-review.json).

The selected property receipt remains valid while the error API sends handler
arguments. A local pure projection recognizes only SEND/REF error cursors that
resume this property operation; source, owner, caller, first matching marker and
exact tail remain authoritative. The API still validates its own target and
argument protocol. The projection adds no receiver or cell owner and leaves
slot/type validation unchanged. One unchanged `1.0`/default-warning original and
an 82-condition actual cursor/ownership/budget front validate the
[repair](../../coverage/semantics/gc-property-nan-cursor-review.json); the initial
interpreter failure retains zero credit. Existing reference-slot evidence keeps
its original cut without a new source agreement.

An initially referenced public float slot now captures its original inner cell
before the Warning. Handler property rebinding transfers the property type-source
to a new cell; the old alias keeps the captured cell live without a marker owner.
Old-cell `0.0` gives true and `1.0`/NaN false despite opposite new-property values.
Four originals and 298 focused premises (257 reached +41 derived) cover actual
cell identities/type-source transfer, outside-frame owners, same Exception at
catch and budgets. The direct-mode bridge and old1/NaN/cell refusals are derived;
earlier direct-slot evidence is not rerun. Retired or nonfloat old cells, sole-owner
receiver retirement and wider quiet-CV GC remain open.
[Reference NaN review](../../coverage/semantics/quiet-public-reference-nan-review.json).

Selected public typed backed sole block `&get` hooks on a parentless class now
admit literal reads and reference fetches through a direct ordinary CV receiver.
The real hook returns the backing cell with its property type-source; an ordinary
read dereferences after hook-frame cleanup. Destination `=&` invokes Get first,
then raises `Cannot assign by reference to overloaded object`, preserving the
original property and initially defined RHS cell. The active hook's `$this`
backing fetch retains the existing pending-base route. One receiver hold moves
from the call target into the frame; the new result marker owns nothing.
Two source agreements and 251 Boolean checks plus six raw transitions are in the
[reference-Get review](../../coverage/semantics/reference-get-hooks-review.json).
The same parentless, public, sole backed block shape also admits untyped `&get`.
An initialized scalar or implicit-null backing becomes a live reference cell
without a property type source. Alias writes remain unconstrained, an ordinary
read copies the current value, and receiver retirement leaves an escaped alias
and earlier copy distinct. Destination rebinding still calls Get before its
overloaded-object Error. Three original-source agreements and 214 Boolean checks
plus three raw transitions are in the
[untyped reference-Get review](../../coverage/semantics/untyped-reference-get-hooks-review.json).

Own public parentless sole short `&get` headers also admit all six raw
`float|bool|string` orders. Exact source order and the implicit return signature
preserve FLOAT/BOOL/STRING tags, numeric strings, copies, alias constraints and
quiet type-source removal; integer writes widen to FLOAT in either strict mode.
Six original sources agree. Author and independent fixture-SL cuts and the actual
508-module joined load retain separate identities. Wider headers, producers,
owners and lifetimes remain partial; exact standing holds remain unchanged.
[Review](../../coverage/semantics/float-bool-string-parentless-short-reference-get-hook-review.json).

Own public parentless sole short `&get` also admits all24 raw
`int|float|bool|string` orders. Exact source order and the implicit return
signature preserve all four scalar tags, including numeric, empty and zero
strings. Ordinary copies remain independent; live aliases retain the genuine
property constraint until quiet receiver retirement permits a NULL write.
Six originals agree. Ten separate fixture-SL cuts retain the source, owner,
cleanup and budget checks; the original timeouts and recorder failure keep zero
credit. Wider headers, producers, owners and lifetimes remain partial, with exact
standing holds unchanged.
[Review](../../coverage/semantics/int-float-bool-string-parentless-short-reference-get-hook-review.json).

The same own public parentless sole short shape now admits all six raw
`int|float|null` orders. Zero, omitted defaults and explicit NULL retain actual
storage; Get materializes an omitted nullable backing as NULL. Exact tags,
independent copies, genuine aliases, weak numeric-text/Boolean conversion and
strict rejection retain source and return authority. Quiet receiver retirement
removes the constraint before a free string write. Six originals agree; separate
fixture and production loads keep their scopes. Wider headers, producers, owners
and lifetimes remain partial, with exact standing holds unchanged.
[Review](../../coverage/semantics/int-float-null-parentless-short-reference-get-hook-review.json).

The same Parent declaration now serves a direct Child with no property
redeclaration. The Parent getter runs with the Child receiver and Parent lexical
scope; the inherited physical slot carries a typed source only when Parent's
declaration has a type. An ordinary read copies, an escaped alias survives Child
destruction, and destination rebinding calls Get before Error. Three source
agreements and 271 Boolean checks plus three raw transitions are in the
[inherited reference-Get review](../../coverage/semantics/inherited-reference-get-hooks-review.json).
For an immediate Child that plainly redeclares the same public `int` property,
the inherited Parent `&get` uses Parent lexical scope and Child receiver, but
returns Child's own backing slot. Its typed source constrains alias writes and
names Child in the TypeError; ordinary reads copy, escaped aliases outlive Child,
and destination rebinding still calls Get before Error. Three source agreements
and 341 Boolean checks plus three raw transitions are in the
[plain Child reference-Get review](../../coverage/semantics/plain-child-reference-get-hooks-review.json).
The matching immediate untyped plain Child redeclaration uses Child's own scalar
or implicit-null slot under Parent's inherited `&get`. Its live alias has no
property type source, so string writes remain unconstrained; ordinary reads
copy and the alias survives Child destruction. An own write precedes Get on a
later destination `=&`, whose Error retains the selected line and file. Three
sources and 364 Boolean checks plus three raw transitions pass in the
[untyped plain Child review](../../coverage/semantics/untyped-plain-child-reference-get-hooks-review.json).
An unchanged Grandchild now inherits that immediate plain Child slot and
Parent's backed `&get`. The getter keeps Parent lexical scope and the actual
Grandchild called class; its reference carries Child's type source when typed
and no source when untyped. Four originals, 392 reached premises and four raw
fetch/rebind steps pass in the
[Grandchild reference-Get review](../../coverage/semantics/grandchild-reference-get-hooks-review.json).
The linked reference-Get route now follows bounded chains back to that sole
backed Parent getter. Unchanged descendants declare no properties, interfaces
or constants; each redeclaring descendant declares only the same-type public
plain property, with no set restriction, interfaces or constants. Methods may
also be declared. The last redeclaration supplies the physical slot and any
typed reference source; the getter keeps Parent lexical scope and the receiver's
called scope. The promoted Greatgrandchild, repeated untyped and typed
redeclarations, a mixed chain and Get-before-rebind Error give five exact sources,
449 reached premises and five raw steps in the
[reference-Get chain review](../../coverage/semantics/reference-get-chain-review.json).
The same linked path now permits distinct-name sibling properties, own scalar
class constants and methodless marker interfaces on ordinary descendants. The
selected plain redeclaration remains a separate singleton source declaration
with the same public type and no set restriction. Its own source origin and key,
each authentic parent link and the unchanged descendants' equal selected layout
still determine the latest physical slot. The four new originals cover sibling
reads, constants and interface membership before `&get`, Parent lexical scope,
leaf called scope, typed alias coercion, independent copies, receiver retirement
and Get-before-rebind Error. Reached checks also authenticate the sibling,
constant and linked interface descriptors, latest default/type source, link
removal refusals and four raw fetch/rebind steps.
[Memberful reference-Get review](../../coverage/semantics/reference-get-memberful-review.json).
The getter-declaring class may now have one linked parentless ordinary Base.
An absent selected key in Base leaves the getter's own backing slot; a
same-name public plain equal-type singleton nonstatic Base property is
overridden by the getter's own separate slot and default. Existing linked descendants may retain or
plainly redeclare the selected key; the last redeclaration supplies the typed
source or untyped absence. The getter can read an inherited unrelated Base
property, while `__CLASS__` names the declaring class and `static::class` names
the leaf receiver. Four frozen originals and source-reached checks cover the
two Base shapes, typed coercion, implicit null, copies, alias retirement and
Get-before-rebind Error. This is still a bounded `&get` subset; see the
[parented reference-Get review](../../coverage/semantics/reference-get-parented-review.json).
Hook-bearing intermediate redeclarations remain Unsupported; an incompatible
property type remains a static rejection. Different-type compatible chains,
grouped selected declarations, virtual/arrow/set/trait forms, dimensions,
quiet reads and compound consumers remain outside these slices.

Public backed by-value block and expression `get` hooks compile into source functions with the
property's return type. Literal reads through an ordinary CV or `$this` execute
the hook each time. Direct backing access requires the same property and receiver
in the active hook; saved hook frames, ordinary helpers and other receivers do
not grant that bypass. Writes keep ordinary typed storage, and uninitialized
backing raises its error before magic lookup. One receiver hold moves from the
selected target to the entered hook. Its return payload survives receiver cleanup,
and exceptions retain the hook's class/name/line. The
[hook review](../../coverage/semantics/backed-get-hooks-review.json) records eight
originals and separate 177 source/state checks. Expression bodies reuse implicit
return compilation at the authentic expression child, preserving its emitted line
and the Hook source across string callbacks. Seven additional originals and 137
derived/reached checks are recorded in the
[expression review](../../coverage/semantics/expression-get-hooks-review.json).

Module403 adds selected public typed backed set-only statement hooks with implicit
`$value` and void return. The declaring class is parentless; unchanged inheritance
keeps its original private scope and the receiver’s called class. Actual parameter
receipt precedes the body. Only the active matching property/receiver bypasses
the setter for backing storage; the saved continuation returns original input20
after the body stores33. Ordinary reads return33. Bad array input raises the
hook argument TypeError with caller line21 before body entry and keeps33. One
original and three states/234 premises (208 reached,26 derived) are in the
[set-only review](../../coverage/semantics/backed-set-only-hook-review.json). Other
set shapes, references, indirect writes and wider override/lifetime families remain required.

Sole public typed short SET hooks on ordinary parentless classes compile the
authentic expression child, then use the existing backing assignment and void
fallthrough. A short SET is backed even when its expression contains no explicit
property access. The exact source hook, completed property, function/code and
current SET context authenticate the implicit write; no synthetic checked
assignment or source occurrence is introduced. The original caller input and the
transformed stored value stay distinct. Parameter rejection precedes the body,
typed result rejection prevents the slot update, and RHS throws skip the implicit
assignment.
The captured write target and existing outer result retain the receiver after
global removal until abrupt cleanup; retry and ordered destruction are covered
by the [short-SET review](../../coverage/semantics/short-set-expression-review.json).
Trait, wider paired/header and Tick-bearing short SET forms remain partial.

Selected sole public typed backed implicit SET hooks also import directly into a
parentless Consumer. The raw Trait function remains a source authority; only the
published Consumer clone is callable on Grand. It retains Trait body/magic while
using Consumer private scope, receives20, stores33 and restores assignment20.
Two real cuts pass231 premises (179 reached,52 derived), including the forbidden
raw-Trait callable forgery. [Trait-setter review](../../coverage/semantics/trait-imported-backed-set-hook-review.json).

Selected public typed sole backed SET hooks on a parentless class also compile
one real typed, defaultless by-value parameter, retaining its name, normalized
type and source occurrence. The property
type must fit the parameter type. Body compilation precedes that compatibility
check; incompatible `int` property/string-only parameter fails at hook ENDLINE7.
An `int|string $incoming` parameter receives `"20"` unchanged, while the body
casts and stores `33`; assignment still returns the original string. Bad-array input
fails at actual Param line4 with caller21 before body entry. Three states pass270
premises (238 reached,32 derived), including source-type/Param-leaf forgeries and
genuine compiler rejection. The existing target/result, storage and generic typed
receive rules are reused. [Explicit-parameter review](../../coverage/semantics/explicit-setter-parameter-review.json).

The same real typed, defaultless by-value parameter route now binds ordinary
class short SET expressions. Its supplied name, actual Param occurrence,
normalized signature and contravariant property compatibility authenticate the
expression's existing implicit write. Original string inputs remain distinct
from transformed integer storage. Body compilation still precedes final variance
checking: a body error wins over an incompatible parameter, while an otherwise
valid body leaves the variance error before main execution. Typed input/result
rejections, throw/retry, retained receiver owners and budget resumption are in the
[explicit short-SET review](../../coverage/semantics/short-set-explicit-review.json).
Trait, byref/default/attribute and wider header forms remain partial.

An ordinary parentless class can pair an existing public typed block GET with
an implicit or explicitly typed short SET. Both indexed source functions share
the actual backing descriptor: an own-backing write in GET bypasses SET, and an
own-backing read in SET bypasses GET. Assignment input, transformed storage and
the subsequent getter result remain distinct through RHS throw, retry and receiver
cleanup. Getter compilation still precedes setter compilation and variance checks.
Three original-source agreements, strict448 and the independent source/owner/budget
front are recorded in the
[short-pair review](../../coverage/semantics/short-get-set-pair-review.json).
A pure block GET on an initialized property can also use the short SET's intrinsic
backing, even when neither hook syntactically accesses that storage. The compiler
certificate binds the actual property, explicit initializer and GET/SET indices;
the authenticated source pair excludes virtual classification. The getter's fixed
700 stays separate from assignment input and backing storage: a later SET reads
the earlier stored 18 rather than 700. Four originals, strict448 and 148 independent
source/slot/owner/budget checks retain their recorded cuts in the
[pure-pair review](../../coverage/semantics/pure-get-short-set-pair-review.json).
An absent initializer also retains the real `PROP_UNINITIALIZED` descriptor and
`PROP_INITIAL` backing slot. GET can return 700 before any write, while an own-backing
read raises the exact uninitialized-property Error. Parameter and implicit-write
TypeErrors preserve that slot or its prior 15; successful writes and retries store 15/12.
First-write RHS abort/global removal retains the uninitialized receiver until unwind.
Four originals, strict449 and 148 independent initial-slot/owner/budget checks are in the
[uninitialized-pair review](../../coverage/semantics/uninitialized-pure-get-short-set-pair-review.json).
Existing expression-bodied GET hooks also pair with short SET on initialized or
uninitialized properties. Pure initialized GET uses the same actual backing
certificate; the existing expression compiler and source-authenticated implicit
return preserve the property's return type and real expression line. Getter
throws and return TypeErrors keep the caller's prior target and backing unchanged.
The entered getter owns its receiver through the saved call context; its result
receipt adds no owner. Five originals, strict449 and 146 independent source/return/
owner/budget checks are in the
[expression-pair review](../../coverage/semantics/expression-get-short-set-pair-review.json).
Short SET may also precede GET physically. Actual names/body certificates derive
logical GET 1/SET 0 while compilation still visits the physical first hook before
the second: the checked first SET body/builtin-variance errors precede a later GET body error.
Block/expression GET and implicit/explicit typed SET retain the same descriptor,
including source-covered absent initializers. Getter return and Closure class-owner
certificates consume the actual getter origin and authenticate the Closure's source
class after getter frames retire. Seven originals, strict449, main 148 and
corrected Closure 37 checks retain their separate cuts in the
[SET-first review](../../coverage/semantics/set-first-hook-pair-review.json).
Source-backed block SET also composes with the admitted block/expression GET forms
in either physical order. Class-only admission preserves real typed/defaultless
parameters and the old implicit Trait-pair policy. Actual SET backing syntax admits
pure initialized GET without inventing storage; absent initializers keep their real
uninitialized state. Original string input, transformed storage and checked physical
body/builtin-variance priorities remain distinct. A local RHS temporary uses actual
statement paths before its later property write; the existing outer setter receipt
retains the receiver through throw/retry. Seven originals, strict449 and 156 independent
source/statement/owner/budget checks are in the
[block-SET pair review](../../coverage/semantics/block-set-hook-pair-review.json).
GET's own-backing syntax also supplies whole-property storage when a block SET
does not access or write that storage. The actual pair/default/role certificate
admits its ordinary body and prevents setter-only virtual classification. Initialized
backing remains unchanged by successful SET; an absent initializer retains a real
uninitialized slot through success, throw and retry. Weak implicit reception can
produce an integer formal while the caller keeps its original string result.
Five originals, strict449 and 147 independent slot/source/receipt-owner/budget checks
are in the [GET-backed no-write review](../../coverage/semantics/get-backed-no-write-set-review.json).
When neither GET nor an ordinary block SET has backing syntax, the class pair is
genuinely virtual. Actual role/source certificates admit existing block/expression
GET and implicit/explicit typed SET bodies without implying backing. Descriptor
metadata remains typed/uninitialized, but the object has no property slot; successful
SET and throw/retry never create one. Caller string input remains distinct from
the weakly received integer. Explicit defaults are rejected after both physical
hooks compile, using the last hook's end line; ordinary invalid-default typing
and checked hook body/builtin-variance errors retain their earlier priority.
Seven originals and 150 independent no-slot/source/receipt-owner/budget conditions
use the current 450-module manifest in the
[virtual-pair review](../../coverage/semantics/virtual-get-block-set-pair-review.json).
The original temporary `(array)$object === []` observation stopped during array
cleanup and remains unresolved with zero credit. Accepted observations assign the
cast to a CV before testing emptiness; no cleanup rule was expanded. Virtual-pair
overrides, Trait and wider headers remain separate. Ordinary type, parameter,
storage and hook execution rules are reused.

Selected direct trait SET imports also preserve that real builtin parameter
signature. Raw Trait property type, Param leaf and variance authenticate the
Consumer clone; physical body/magic and logical private/called scope stay distinct.
The original string input survives receipt and void restoration after backing33.
A narrow parameter fails at the Trait hook ENDLINE7 before import. Two originals
and two states pass281 premises (233 reached,48 derived), including synchronized
narrowing and raw-function/Param/type/callable forgeries.
[Explicit trait-setter review](../../coverage/semantics/trait-imported-explicit-set-hook-review.json).

A selected public typed statement pair ordered get then set now compiles both indexed
source functions and retains one backing descriptor. Its declaring class is
parentless and inheritance keeps the same descriptor. An active matching GET
can write backing without invoking SET; an active matching SET can read backing
without invoking GET. The source distinguishes physical10/get23, assignment20
return20/physical33/get46, and pre-body bad-array rejection with caller26. Two
real cuts pass210 premises (181 reached,29 derived), including both crossed
accesses and original-input restoration. Setter overlap remains Unsupported;
other order/body, unadmitted trait, reference and wider override families remain required.
[Paired-hook review](../../coverage/semantics/paired-backed-get-set-hook-review.json).

The same fixed statement GET/implicit-SET pair now imports directly from one
nonnested Trait into a parentless Consumer. Both raw functions authenticate an
atomic two-clone projection; incomplete partners keep read/write interception
required while refusing a plan. Genuine GET24/cross-write6 and SET25/cross-read10
prove Trait magic, Consumer scope, return23 and original20/store33/get46. Two cuts
pass333 premises (280 reached,53 derived), including partner/source/type,
raw-row callable and crossed-frame controls.
[Paired trait-hook review](../../coverage/semantics/trait-imported-paired-hooks-review.json).
Direct flat Trait composition also admits existing backed GET/ordinary block-SET
forms and real typed/defaultless builtin parameters in either physical order.
Actual raw partners and Param/type facts authenticate an atomic Consumer clone
pair; source-declared pairs prevent imported raw-origin gaps from misclassifying
backed storage as virtual. Either hook can supply backing. Initialized and ABSENT
properties retain their actual slots/defaults, including a no-write SET that leaves
storage uninitialized. Two Consumers share physical Trait code and magic while
keeping separate property identities, storage and lexical/called classes. A local
RHS callback retains one outer SET receipt owner through removal/throw, preserving
the caller's original string until fresh retry. Imported expression GET and GET1
Closure source certificates select the authentic getter and its atomic partner.
Six originals and 212 independent source/clone/slot/owner/budget conditions use the
450-module manifest in the
[Trait pair-family review](../../coverage/semantics/trait-backed-get-block-set-pair-review.json).
The initial 180-second source timeout and first peer fixture typing failure retain
zero credit; the completed sources use a measured-cost 600-second cap. These recorded cuts exclude virtual/short pairs and wider binding; the composed
virtual and short families below supersede those producer limits. No storage,
transition or general Closure rule was added.
Backed pair export also follows acyclic unadapted Trait wrapper chains. Each
real TraitUse fetch and already-installed child property row must match the existing
projection; a decreasing class-count bound excludes cycles. The importing owner is admitted
before its new row/name is published, while children remain fully authenticated.
Intermediate rows have `TRAIT_MEMBER_ORIGIN(Wrapper, rawProperty)` and no callable
hooks; final Consumers keep flattened property/GET/SET identities and atomic raw
partners. Two/three-level paths preserve separate storage, original input and
Consumer lexical/called scope while retaining Inner Trait magic. Pure initialized
GET, ABSENT backing and imported GET1 Closure source use the same certificate.
Equal-default hooked-property conflicts still fail after prior output, at the
actual wrapper/Consumer line and with the immediate exporter name. Six originals
and 256 independent path/row/clone/slot/owner/budget conditions use the 451-module
manifest in the [nested pair review](../../coverage/semantics/nested-trait-backed-pairs-review.json).
Property-specific export also admits multiple Traits and branching wrappers. The
actual fetched candidates retain their immediate owner and property row, selected
by property name. Final callable selection requires one authentic installed path;
import admission authenticates the specific incoming row among all candidates.
Thus distinct exporters of the same raw property are not flattened or deduplicated
before ordinary hooked-property collision handling. Same-raw diamonds, distinct
raw leaves with the same name and local-property priority preserve native errors.
Two independent properties retain separate slots, builtin Param signatures, raw
Trait/Consumer scopes and original input through throw/retry; removing one export
path or raw partner leaves the unrelated property's authority intact.
Six originals and 313 independent exporter/path/clone/slot/receipt-owner/budget
conditions use the 452-module manifest in the
[Branching pair review](../../coverage/semantics/branching-trait-exporters-review.json).
True virtual Trait GET/ordinary block-SET pairs use the same unadapted export
paths and atomic raw partners/Params. Both raw bodies lack own-property syntax;
an imported virtual certificate binds the actual installed Consumer row, raw
virtual descriptor and unique exporter, without deriving callable clones during
layout. Existing slot allocation/validation omits the virtual value while keeping
adjacent backed slots; descriptor UNINITIALIZED metadata does not allocate a
PROP_INITIAL slot. Direct/branching Consumers retain raw Trait code and distinct
lexical/called scopes, original string input, typed reception and no-write effects
through callback throw/retry. GET return-type and raw Trait default, body and builtin
variance errors retain the existing physical compile priority. Imported virtual pair
classification prevents entry into the admitted virtual GET override and SET
inheritance paths through empty raw-origin lists.
Nine new original-source agreements and 279 independent source/no-slot/clone/
receipt-owner/budget conditions use the 453-module manifest in the
[Virtual Trait pair review](../../coverage/semantics/virtual-trait-pairs-review.json).
Short-SET Trait pairs reuse the same authentic raw Params, atomic Consumer clones
and unadapted exporter paths. A short setter is inherently backed even when neither
hook mentions its own property. Source compilation admits only a real paired Trait
certificate with builtin types; sole short-SET Traits remain outside this producer.
The imported expression certificate matches the selected clone, actual raw RHS,
Consumer row/projection and code occurrence. Existing body tasks evaluate that raw
RHS then perform the implicit assignment at the imported hook origin. Exact function
lookup prevents a forged BODY/CODE from selecting this sequence. In the main,
raw RHS13 and hook12 are distinct; a separate native TypeError distinguishes
RHS6 from implicit-write line5. Initialized slots and genuine ABSENT backing keep
original input, received values and stored results distinct from pure GET700.
Callback abort skips the implicit store; input and implicit-write type failures
preserve the prior value and caller result. At a real RHS helper pause, the pending
property base and outer SET result each retain one receiver owner; the borrowed
context adds none.
Eight new source agreements and 305 independent source/RHS/write/slot/owner/budget
conditions use the 453-module manifest in the
[Short Trait pair review](../../coverage/semantics/trait-short-set-pairs-review.json).
The admitted pair family also composes into Consumers extending an ordinary
installed source Parent with no declared/effective hooks or selected-name collision.
Actual source headers reuse lexical context and the existing named-header compiler;
pre-link import does not require the Consumer name or Parent link yet. Runtime
GET/SET/RHS and imported virtual authority require the final SOURCE_PARENT link.
Raw Trait/wrapper origins remain parentless and final Consumer clone ownership
stays unchanged. Inherited fields retain their real Parent declarations/defaults;
an ordinary descendant keeps Consumer lexical scope and its distinct called class.
The no-inherited-key linker check admits only an already-authenticated imported
pair; same-name override handling remains unchanged. FINAL Parent metadata is
admitted before linking so the existing later failure and earlier Trait conflict
retain native priority. Raw hook compilation errors still precede main. A plain
Parent redeclaration that inherits an effective GET remains excluded. The final
absence guards are entailed by the hook-free parentless Bases in all six original
comparisons, preserving
that source cut; the new held contrast is checked separately. The final 454-module
frontier passes 419 source/Parent/layout/clone/owner/budget conditions.
[Parented pair review](../../coverage/semantics/parented-trait-pairs-review.json).
Public-read protected(set)/private(set) backed Trait pairs reuse the same exporter
and atomic Consumer clone rules. The new source branch requires a Trait, backed
headers and exact flags 256/257/512/513, setter visibility and implicit finality.
It admits neither raw class asymmetric pairs nor virtual-asymmetric or arbitrary
explicit-final pairs. Existing lexical permission and called-scope diagnostics
remain separate: an inherited Consumer method may write its private setter on a
Grand receiver, while Grand own scope and an unrelated Consumer may not. RHS
effects/throws precede access denial; allowed arrays reach reception TypeError.
Protected short-SET transformation stays distinct from GET700 and original input;
private block SET retains real uninitialized storage until its first write.
Private(set) finality reaches the existing child-redeclaration failure after the
visible P during conditional Child linking.
At the actual permitted writer-to-SET RHS pause, the saved ordinary method context,
pending property base and SET result each own the receiver; the SET context borrows
it. Source comparisons and the focused permission/owner/budget cut are recorded in
[Asymmetric pair review](../../coverage/semantics/asymmetric-trait-pairs-review.json).
Ordinary symmetric protected/private READ backed Trait pairs use source flags 2/4,
normalized SETVIS eps and FINAL false. Raw descriptors authenticate the existing
protected/private key construction; wrapper and Consumer projection retain actual
installed rows and flattened origins while giving each Consumer its private key.
The hook selector keeps private-first lookup and requires permitted raw-name
resolution to that descriptor's canonical key. GET source/layout identity remains
independent of a plain helper's scope; frame validation checks access in the saved
caller view. SET uses the same descriptor selection and existing setter permission.
Short SET tasks and write authentication carry the authentic source NAME, then the
ordinary resolver maps it to storage KEY; mangled keys are never user names.
An inherited Consumer reader can access its private key on Grand, but an unrelated
Consumer cannot. Grand own reads of inherited private state retain ordinary
Warning/null fallback without entering GET. Protected direct denial precedes GET,
while permitted reads of absent backing retain the exact typed-uninitialized Error.
At the private GET helper pause, reader and getter contexts each retain one
receiver owner; the result task retains none. Two compact source agreements use
the 456-module manifest; the focused key/caller/owner/budget cut is recorded in
[Nonpublic key review](../../coverage/semantics/nonpublic-trait-pair-keys-review.json).
Existing disjoint ordinary Parent proof is key-independent: it excludes every
same-NAME Parent row before import, so private Consumer keys and the protected
prototype cannot be changed by those fields. No new Parent source claim is added.
Nonpublic `isset`/`empty` and `??=` use the same permitted descriptor; their
result tails check access in the saved caller view. Inaccessible quiet probes
skip GET, permitted NULL/zero values retain their distinct decisions, and getter
failure preserves the prior result. Plain `??` already follows normal GET.
The actual `COALESCE_ASSIGN_WRITE` authenticates its real source occurrence,
memoized base and write line before reusing ordinary SET entry/results. It
reacquires a borrowed CV/global-cell selector after the RHS, rather than retaining
the getter's receiver as the write target. Getter-time rebinding can retire that
old receiver before the RHS; later rebinding to an unrelated Consumer preserves
private denial. Successful SET keeps original STRING5 as the assignment result
while persisting15. RHS failure leaves the prior result intact for a fresh retry.
[Quiet conditional review](../../coverage/semantics/nonpublic-quiet-trait-pairs-review.json).
The existing integer-RHS `+=` path also supports symmetric builtin-backed pairs.
After RHS effects it selects the permitted descriptor and fixes one receiver for
GET, addition and SET, even if GET replaces the original CV. The real PLUS parent,
retained finish task and saved caller authenticate that SET object/property and
its actual partner/signature. The expression keeps the computed sum while SET
may transform storage. Getter/RHS/SET throw or typed-write failure leaves the
outer assignment result unchanged. The compound finish and SET receipt
independently retain the receiver, with the ordinary extra base owner for a short
SET. GET-only store/finish is unchanged. The new pair branch excludes asymmetric,
virtual and byref families.
[Compound pair review](../../coverage/semantics/compound-get-set-pairs-review.json).
Direct named CV/This `unset` uses an isolated canonical-key query over the actual
instance layout and authentic GET/SET origin. It follows ordinary visibility
resolution: inaccessible private/protected names raise the access Error, while a
permitted hooked property raises `Cannot unset hooked property` with the runtime
class and unmangled name. Unset dispatches neither hook and leaves backing intact,
including inside the property's active GET or SET; there is no backing-reset path.
The ordinary throw/store bodies and raw-name hook queries used by magic consumers
stay unchanged. Indirect hooked unset remains Unsupported.
[Canonical unset review](../../coverage/semantics/canonical-hook-unset-review.json).
Normal GET and assignment on admitted backed pairs accept a plain non-NUL
string-CV name with a direct CV/This receiver. The source certificate checks the
actual emitted name CV and line. Entry reads that operand before selecting the
permitted descriptor; normal assignment retains the existing late name resolution
after its RHS. Once selected, source and frame validation use the descriptor's
NAME/origin rather than rereading a name CV changed by the hook or helper. A
private imported getter therefore keeps its real value slot when the live name
now selects an ordinary plain field, even after the global receiver is removed.
Reader/getter contexts retain their ordinary independent owners through abort.
Short SET still writes the selected source NAME, preserving original assignment
input separately from transformed backing. Arbitrary expressions, Stringable and
owned names remain outside this entry; literal consumers keep their existing
domains.
[String-CV name review](../../coverage/semantics/string-cv-hook-names-review.json).
Checked CV-name quiet entry uses the actual `PROPERTY_NAME`/`ISSET_RESULT` role;
it remains separate from normal/coalesce GET dispatch. The same structural
source and selected descriptor survive getter changes to the live name CV.
Existing NULL/zero decisions, getter exceptions and saved caller access remain.
For `??=`, both GET and later write selection validate the plain name operand;
the pending receiver/name variables are reacquired after the RHS. A name change
may select ordinary storage and return its typed int, while a retry selecting
SET retains original STRING5 and stores15. The original GET receiver may retire
before the RHS pause; captured selectors add no receiver owner. For symmetric
builtin-backed integer-RHS `+=`, the CV branch dispatches SET using the retained
descriptor's source NAME, preserving the object/property selected before GET.
Computed105 differs from stored1050 even if GET changes the live name to an
ordinary field. The real coalesce/PLUS source, existing receipts and independent
operation/SET pins remain
authoritative; literal GET-only storage stays unchanged. No new selector storage,
opcode, type or owner formula is introduced.
[CV name consumer review](../../coverage/semantics/string-cv-hook-consumers-review.json).
Raw class nonpublic/asymmetric pairs, virtual nonpublic pairs and nonpublic READ
with asymmetric SET remain held. Existing public-read asymmetric Trait permission
policy is unchanged. Internal keys are unowned byte lists, with no
owned-NUL value or release expansion.
Recorded prior Unsupported/elaboration cuts and this family's failed cuts retain
zero credit. Same-name or hooked Parents, adaptation, nominal,
ref/attribute/default-parameter and wider binding forms remain separate; no
new descriptor nesting, storage, transition or generic Trait linking rule was added.

Selected sole implicit virtual SET hooks also compile on a parentless class,
with unchanged inheritance. Actual source ABSENT and descriptor PROP_UNINITIALIZED
are distinct from the default helper’s PROP_INITIAL: allocation keeps no value slot.
The body writes a different stored property10→33 and restores assignment20. A real
read raises the receiver-class write-only Error; an array fails at hook5/caller28
before body entry. Two cuts pass252 premises (209 reached,43 derived). Active
same-object writes still refuse recursive SET plans; the defined-CV Error path is
described below. Other virtual setter forms remain required.
[Virtual setter review](../../coverage/semantics/virtual-set-only-hook-review.json).

A real same-object alias write inside that virtual SET now resolves its defined
ordinary CV input, then raises the receiver-class Must-not-write Error at write8.
It preserves the remaining task tail for throw/catch, skips setter conversion/call,
and leaves outer result7 plus stored10/no value slot unchanged. One genuine cut
passes116 premises (92 reached,24 derived), including array-input Error priority
and RHS-leaf/operand/frame refusals. Other RHS, missing-variable warnings and wider
receiver/catch/lifetime forms remain partial.
[Alias-write review](../../coverage/semantics/active-virtual-set-alias-review.json).

A selected public protected(set), typed, sole implicit backed class SET keeps its
public key and authentic source flags. Child lexical permission survives the setter
call and saved result restoration; Parent private13 differs from Child private900.
Assignment20 returns20 after storage33. A global array write resolves its RHS then
raises the access Error before any call/receive; the same array through Child reaches
TypeError at hook4/caller14 and leaves33. Two genuine cuts pass266 premises
(224 reached,42 derived), including forged metadata-valid global calls that fail
permission and disjoint indirect denial. Existing permission/layout/receive rules
are reused. Other private(set), explicit/trait/paired/virtual asymmetric hooks and
wider write/reference/receiver forms remain partial.
[Protected setter review](../../coverage/semantics/protected-set-backed-hook-review.json).

The same bounded class family accepts genuine private(set) flags512/513, retaining
its public key and implicit FINAL equality. Only the declaring Parent lexical
scope may write on Child; called scope alone grants no permission. Parent input20
stores33 and the assignment returns20. Child/global arrays raise access Errors
before reception; the permitted Parent array raises TypeError4/caller11. A plain
Child redeclaration fails through the unchanged final linker at class14. Two
originals and two cuts305 (252 reached,53 derived) cover these paths plus source,
FINAL, key and lexical/called counterexamples. Arbitrary explicit-final and wider
asymmetric hook shapes remain unsupported.
[Private setter review](../../coverage/semantics/private-set-backed-hook-review.json).

Effective virtual getters without defaults retain the same declaration, function
and return type while omitting the physical slot. The receiver owns no returned-value edge;
result copies survive receiver cleanup and release independently. Ordinary writes
evaluate the RHS before read-only rejection and skip destination coercion. Literal
string `$this`/property forms still establish backing; nested function bodies do
not. Eight affected originals and 139 derived/reached checks are recorded in the
[virtual review](../../coverage/semantics/virtual-get-hooks-review.json).
Literal CV and `$this` `isset`/`empty` also invoke these public by-value getters.
The quiet consumer authenticates its source mode and carries the property's
origin restoration through the call. `isset` tests the returned nullness;
`empty` negates its truth value. Temporary returned objects release before the
boolean branch while the receiver remains live. Two originals and 162 state
premises (143 reached, 19 derived) pass in the
[quiet hook review](../../coverage/semantics/quiet-get-hooks-review.json).
Literal CV and `$this` coalescing also invoke these getters and retain their
actual returned value. Zero and false skip the fallback; null evaluates the
original RHS at the restored parent and its emitted child line. Result ownership
survives the extra base-copy decrement and receiver cleanup; the last kept owner
then releases the returned object. Two originals and 249 state premises
(224 reached, 25 derived) pass in the
[coalesce review](../../coverage/semantics/coalesce-get-hooks-review.json).
Literal CV and `$this` `??=` tests the actual getter result. False and zero
skip the RHS and leave null backing unchanged; a null result evaluates the
original RHS at its emitted child line and uses ordinary property storage.
The pending target borrows a CV and refetches its current receiver at write;
`$this` retains its target owner through the null write and releases it on a
nonnull selection. Returned objects gain no extra base copy or task value owner.
Three originals and 308 premises (264 reached, 44 derived) pass in the
[assignment review](../../coverage/semantics/coalesce-assignment-get-hooks-review.json).
Direct literal CV and `$this` unset of these public hooked properties resolves
visibility before raising `Error` with the runtime class, property name and source
line. It invokes no getter and preserves storage; active getter backing permission
does not permit unset. The backing payload survives each rejected unset and releases
when receiver storage is freed. Two originals and 182 premises (178 reached,
4 derived) pass in the [unset review](../../coverage/semantics/hooked-unset-review.json).
Public backed by-value hook `+=` through literal CV or `$this` admits an already
evaluated integer RHS. It selects the current receiver after RHS effects, invokes
the getter and applies ordinary addition to its returned value, then stores on
that selected receiver even if the getter rebinds the original CV. The expression
retains the arithmetic result across existing destination type checks. An owned
finish continuation keeps the receiver while the returned RV releases, including
through a pending arithmetic error; actual unwind then retires that hold before
catch. Source selector metadata adds no second `$this` owner. Three originals
and separate scalar291/affected129 state cuts are recorded in the
[addition-assignment review](../../coverage/semantics/backed-get-hook-addassign-review.json).
Named public backed by-value getters can override another such getter with an
identical normalized property type. The child declaration replaces the effective
slot/default and retains its getter body, lexical class and private-method scope;
the called class remains the runtime descendant. Parent-defined `$this` reads use
the effective child getter. Direct backing access still requires the active
property and receiver; returning a fresh object does not store it in that slot.
Two originals and separate scalar238/lifetime97 cuts are recorded in the
[override review](../../coverage/semantics/backed-get-hook-override-review.json).
A child getter without its own backing access or initializer also retains a
physical slot over an immediate parent whose getter body is backed. Its own
uninitialized typed or null untyped default removes the parent default; ordinary
writes use that slot while reads still invoke the child getter. Receiver cleanup
releases the backing reference independently of a returned object retained by
the caller. Two originals and separate scalar185/lifetime100 cuts are recorded
in the [effective backing review](../../coverage/semantics/effective-backed-get-hook-review.json).
Storage also propagates through repeated body-unbacked overrides and intervening
classes without a redeclaration. A bounded linked-ancestry walk follows each
effective property's authentic declaring class to a source-backed getter anchor.
The newest child retains its own default, slot and getter scope. Separate CV,
inherited `$this`, write, ancestry, untyped and lifetime checks are recorded in the
[repeated override review](../../coverage/semantics/repeated-effective-backed-get-hook-review.json).
Admission requires a nonabstract, nonfinal named subclass, public by-value getters
and identical normalized types.
Virtual getters without initializers also override another virtual getter when
a separate bounded ancestry check closes at an authentic virtual root. Child
declaration defaults remain metadata; neither typed uninitialized nor untyped
null metadata creates a physical slot. Reads retain child lexical/private scope
and runtime descendant dispatch, including inherited `$this` methods. Ordinary
writes raise read-only errors naming the runtime class at the actual write line,
without getter dispatch or slot mutation. Returned objects can survive receiver
cleanup. Two originals and four separate state cuts are recorded in the
[virtual override review](../../coverage/semantics/virtual-get-hook-override-review.json).
Public get-only virtual overrides without initializers now allow one-way type
covariance when both declarations have a type. Comparison uses the actual
declaring scopes and active nominal registry; builtin `int|string` to `int` and
linked `Animal` to `Dog` narrowing retain child/private scope, empty storage and
returned-value ownership. Known incompatible getter signatures fail at their
hook line before the property-type diagnostic; static, readonly, visibility and
final errors keep their existing priority. Unresolved comparisons defer to the
hook-link refusal rather than becoming a known-incompatible fatal. Three originals
and four separate state cuts are recorded in the
[covariance review](../../coverage/semantics/virtual-get-hook-covariance-review.json).
In this public get-only virtual scope, removing the inherited type removes the
synthesized getter return annotation and raises its compatibility fatal at the
child hook line. A typed child overriding an untyped parent preserves the later property
TYPE-presence fatal at the class line. Both-untyped overrides keep their empty
return annotation, child/private scope and inherited `$this` dispatch without
physical storage. Three originals and four separate compiler/dispatch state cuts
are recorded in the
[type-presence review](../../coverage/semantics/virtual-get-hook-type-presence-review.json).
Public source-body-backed getter pairs with literal defaults have the same
removal diagnostic priority. Passed TYPE/default descriptors must match the real
declaring descriptors; both getter bodies must read their own backing property.
Both-untyped controls retain the child effective slot/private scope through CV
and inherited `$this` reads and ordinary integer writes. Three originals and five
separate state cuts are recorded in the
[backed type-presence review](../../coverage/semantics/backed-get-hook-type-presence-review.json).
A genuinely source-body-backed child also overrides a virtual parent of the same
normalized TYPE, including an intervening class without a redeclaration. Admission
requires positive closed virtual ancestry, the child's actual own descriptor and
its linked parent layout. The child retains its own physical slot/default rather
than a parent slot; inherited reads use its lexical/private scope and the runtime
descendant. Ordinary writes change that slot, while receiver cleanup releases its
backing reference independently of a retained returned object. Two originals and
four separate state cuts are recorded in the
[virtual-parent review](../../coverage/semantics/virtual-parent-backed-get-hook-review.json).
A closed virtual get-only parent also permits builtin and linked nominal
covariance for a genuinely body-backed child when both TYPEs are present.
Prelink compatibility checks the child's own source descriptor; linked admission
also checks its actual parent layout. The child keeps its own narrowed slot/default,
backing-read bypass and private scope. Rejected stores preserve that slot and
report the declaring child type; incompatible getters fail at the hook line.
Separate stored and returned objects retain independent cleanup. Three originals
and five selected state cuts are recorded in the
[backed-child covariance review](../../coverage/semantics/virtual-parent-backed-get-hook-covariance-review.json).
These own-body-backed children also reject removal of an inherited type at the
getter declaration. The prepublication proof authenticates closed virtual-parent
ancestry and the child's own TYPE/default descriptor; the rejected child has no
ancestry link. A typed child overriding an untyped parent retains the later
class-line property error. Both-untyped controls keep the child slot, private scope,
inherited `$this` dispatch and ordinary writes. Three originals and five separate
state cuts are recorded in the
[cross-shape type-presence review](../../coverage/semantics/virtual-parent-backed-get-hook-type-presence-review.json).
Typed source-body-backed parents also reject an untyped, body-unbacked child
without an initializer at the getter declaration. This prepublication proof checks
both own descriptors and the child's implicit null default; it does not require a
child ancestry link. The reverse typed-child direction keeps the class-line error.
Both-untyped linked controls distinguish Parent backing 100 from one Child-origin
null slot, source backing from effective storage, and Child/private scope from
Grand called scope. An ordinary write stores 300 while the getter remains 13.
Three originals and five separate state cuts are recorded in the
[inherited-storage type-presence review](../../coverage/semantics/backed-parent-unbacked-get-hook-type-presence-review.json).
A typed source-unbacked parent with published backing ancestry also rejects an
untyped source-unbacked child without an initializer at the getter declaration.
The bounded proof follows the actual declaring descriptor through an intervening
class, authenticates the parent's backing basis and the child's own null default,
and leaves the rejected child unpublished. Reverse addition keeps the class-line
error. Repeated untyped controls retain one null slot and getter 13 after write 300;
[effective-storage type-presence review](../../coverage/semantics/effective-backed-parent-unbacked-get-hook-type-presence-review.json).
That getter error priority also covers a genuinely body-backed child with its own
default below the source-unbacked, effectively backed parent. Before publication,
the proof authenticates the parent's source classification and bounded backing
ancestry, then the child's exact own descriptor and genuine backing body. It does
not require an ancestry link for the rejected child. Reverse type addition retains
the class-line error; both-untyped controls distinguish Root 100, First null and
one child slot 200, active getter backing access, child/private scope and Grand
called scope. An ordinary write stores 300 and the getter returns 313;
[own-backed-child type-presence review](../../coverage/semantics/effective-backed-parent-backed-get-hook-type-presence-review.json).
Ordinary public parent properties also admit genuine own-body-backed, plain
by-value get children of equal normalized TYPE. Linking authenticates the ordinary
empty-hook source and both own descriptors, then the child parent link and inherited
layout across intervening classes. The child keeps its own default and single slot;
private/inherited reads dispatch to its getter and ordinary writes update that slot.
Backing references release independently of retained getter results;
[ordinary-parent review](../../coverage/semantics/ordinary-parent-backed-get-hook-review.json).
Ordinary parents also back a plain by-value getter child with no initializer or
own-property read, at equal normalized TYPE. A bounded pure parent-layout lookup
across intervening classes authenticates the ordinary descriptor and source; the
same positive proof admits the pair and prevents virtual classification. Typed
slots start uninitialized, untyped slots null; source backing and active getter
bypass remain false. Writes update physical slots while getter results stay
independent. Distinct stored S and retained returned R use the existing cleanup;
[ordinary-storage review](../../coverage/semantics/ordinary-parent-unbacked-get-hook-review.json).
Repeated plain by-value, no-initializer/no-backing-read getter declarations now
carry the same ordinary anchor through the existing bounded backing walk. Actual
parent layout selects the declaring getter across intervening classes; typed
physical slots start uninitialized and untyped slots null. Latest private/called
scope and getter results remain independent of raw writes, with distinct stored S
and retained R cleanup;
[repeated ordinary-storage review](../../coverage/semantics/repeated-ordinary-unbacked-get-hook-review.json).
A typed, source-unbacked getter directly backed by an ordinary parent now rejects
a source-unbacked/no-initializer child that omits its type. The existing
missing-return check accepts the positive ordinary parent proof before child
publication; the error names the declaring getter at the child hook line. Reverse
addition retains the property class-line error, and untyped null-slot reads/writes
remain controls;
[ordinary-backing type-presence review](../../coverage/semantics/ordinary-backed-parent-unbacked-get-hook-type-presence-review.json).
A genuinely own-body-backed child omitting its type now receives the same
getter-declaration error before the invariant property check. The sixth
missing-return arm accepts the authenticated ordinary parent basis; the rejected
child's own descriptor and backing body remain required. Reverse addition keeps
the class-line error. Untyped controls retain the child slot 200→300 and getter
213→313; a real entered getter confirms active backing bypass.
[Own-backed type-presence review](../../coverage/semantics/ordinary-backed-parent-backed-get-hook-type-presence-review.json).
An equal-TYPE public plain child now inherits a genuine body-backed parent's
by-value getter across intervening classes. Own descriptors, source and bounded
parent layout authenticate the pair. The effective property and physical slot
stay Child's, while the resolved getter/function, lexical/private scope and trace
class stay Parent's; called scope follows the receiver. Child 200→300 and getter
213→313 are covered by genuine entered Child/Grand and writer states;
[inherited-getter review](../../coverage/semantics/plain-child-inherited-backed-get-hook-review.json).
Repeated plain equal-TYPE redeclarations now resolve the same original getter
through bounded ordinary-source edges. Each edge authenticates its actual own
descriptors and immediate selected parent; decreasing fuel closes at a genuine
local backed getter. Latest Second storage 300→400 stays separate from original
Parent function/lexical/private/trace and receiver called scope, returning 313→413;
[repeated inherited-getter review](../../coverage/semantics/repeated-plain-child-inherited-backed-get-hook-review.json).
A source-unbacked, no-initializer getter directly backed by an ordinary ancestor
can also be inherited by a plain equal-TYPE child. The existing terminal proof
accepts that positive ordinary anchor with the supplied fuel. Parent starts
uninitialized, Child owns 200 then 300, and the original getter returns 13;
function/lexical/private/trace remain Parent's and called scope follows the receiver.
Active source backing bypass stays false despite the physical slot;
[ordinary-backed inherited-getter review](../../coverage/semantics/ordinary-backed-parent-plain-inherited-getter-review.json).
The terminal also accepts an authenticated hooked backing ancestor through the
existing inherited walk with supplied fuel. Root's genuine backed getter returns
107, while source-unbacked Parent remains the selected getter/function/private
owner and returns 13 on plain Child/Grand. Parent starts uninitialized and Child's
own slot changes 200 to 300 with active backing bypass false;
[hook-backed inherited-getter review](../../coverage/semantics/inherited-backed-parent-plain-inherited-getter-review.json).
A closed virtual get-only Parent is also an authenticated terminal basis with the
supplied fuel. Its descriptor default helper yields INITIAL, but the virtual
object owns no physical slot. A plain public equal-TYPE Child remains nonvirtual
and owns 200 then 300; the inherited Parent function/lexical/private/trace identity
and receiver called scope stay distinct. Active source backing bypass is false
and the getter returns 13 independently of the slot;
[virtual-root inherited-getter review](../../coverage/semantics/virtual-parent-plain-inherited-getter-review.json).
Plain children under that closed virtual get-only family also admit compatible
covariance. Actual source/own descriptors authenticate the prepublication family;
the linked edge additionally requires the existing scoped subtype result. A mixed
Parent getter on an int Child retains its original mixed return declaration and
returns the string "13", independently of the integer slot 200→300. Reverse
widening receives "must be subtype of int" at the child class, with no synthesized
child getter declaration or hook-line reattribution. Function/private/called scope
and false active source bypass remain unchanged;
[plain-child covariance review](../../coverage/semantics/virtual-parent-covariant-plain-inherited-getter-review.json).
The equal-TYPE closed virtual get-only family also accepts a public protected(set)
plain Child. Its own physical slot starts at 200; global stores are rejected, while
Child and inherited Parent scopes store 300/400 through existing protected-family
permissions. The inherited getter retains Parent's function, lexical and private
scope; called scope follows the receiver. It returns 13 independently with false
active backing bypass. A
genuinely body-backed public-set Parent still rejects the same narrowing at the
child class. The scoped prelink exception handles source-fast-equal linking; the
linked edge additionally authenticates Child ancestry and normalized setter flags.
TYPE/covariance, defaults, layouts, stores and permission rules are unchanged;
[protected setter review](../../coverage/semantics/virtual-parent-protected-set-plain-inherited-getter-review.json).
A plain untyped Child removing the closed virtual Parent's int TYPE receives
"must be subtype of int" at the child class. There is no child getter declaration
to reattribute to a hook line. Reverse type addition under an untyped Parent
keeps the later "must be omitted" property error. Both-untyped inheritance retains
Parent's RETURNS eps/private method and string "13" result, while the plain Child
owns 200 then 300. In the untyped control, Parent's NULL default metadata creates no slot;
active source backing bypass stays false. This only extends authenticated
diagnostic-family recognition; pure variance and linked compatible admission,
getter/default/layout/store/owner rules remain unchanged;
[plain-child type-presence review](../../coverage/semantics/virtual-parent-plain-type-presence-review.json).
The getter also survives repeated equal-TYPE plain protected(set) redeclarations:
virtual Parent -> First200 -> Bridge -> Second300 -> Grand. Each immediate edge
keeps its actual source/own/link proof and the getter walk decreases fuel. A
positive Second edge alone does not certify malformed First source or a missing
ancestor getter. Latest Second storage changes 300 to 400 through its class-scope writer,
while the inherited Parent function/private/lexical identity and receiver called
scope stay distinct; source backing bypass remains false and the result stays 13.
Later private(set) narrowing is rejected against immediate First at class17,
without borrowing the distant virtual-parent exception. Existing permission,
default/layout/store/owner rules are unchanged;
[repeated protected-setter review](../../coverage/semantics/repeated-protected-plain-inherited-getter-review.json).

Naked literal zero-argument `parent::$value::get()` inside an ordinary public
virtual Child statement getter selects the physical public virtual get in its
lexical immediate parent. The new target borrows This; the outer hook retains it
through receiver-CV nulling, and returned values survive receiver release. Grand
called scope differs from Parent lexical/private scope. Real Throwable traces use
the captured parent property/class, including after receiver retirement.
Outside-hook/wrong-property diagnostics precede application output; matching
file/token starts distinguish naked from parenthesized class operands. Six unique
sources and 377 focused checks keep separate cuts in the
[parent get-hook review](../../coverage/semantics/parent-get-hook-review.json).
This get-only cut leaves backing/plain-parent trampolines, refs/FCC/arguments,
traits and wider callers partial; existing declarations, return typing and generic
cleanup are reused.

A public virtual implicit `int` setter on Child may also call the matching
physical setter on its immediate parentless Parent with naked
`parent::$value::set(f())`. The single positional, nonreference argument comes
from a named zero-argument by-value producer. Parent borrows This through the
callback clearing the global receiver; the outer setter marker retains the sole
receiver owner. Parent private secret 7, Child private secret 99 and called Grand
remain distinct. The parent call returns `NULL`; the tested outer assignment
retains its literal 20. Supplied throws preserve identity/destination 42, while
an array argument errors after callback effects and before Parent body, with
`$value::set`/Parent/`->` trace fields. The wrong-kind call fails compilation.
Four source agreements and 459 focused checks retain separate cuts in the
[parent set-hook review](../../coverage/semantics/parent-set-hook-review.json).
Only the public virtual implicit-int root/Child edge is added; backing/asymmetric
or wider setter hierarchies/types, explicit parameters, other argument/result
producers and wider lifetime/reentry remain partial. Existing get behavior is
preserved structurally without renewing its application evidence.

Other inherited getter roots/shapes and wider
type-presence combinations remain required.
Backed-parent inheritance retains invariant types; broader type equivalence and
wider hook variance remain required.
Hooked object iteration is explicit Unsupported rather than a raw storage view;
array casts retain ordinary storage only. Defaulted virtual/set/byref hooks,
other inheritance/traits, temporary/computed receivers, other compound operators/RHS
forms, wider coalescing assignment and
quiet/reference/indirect access and wider `__unset` consumers remain boundaries.

A parentless class may declare a public nonstatic `__unset(string $name): void`
with one required by-value parameter, inherited unchanged by Child. For a direct
CV receiver and literal declared private name, pending unset resolves receiver/name
before the internal call. An accessible initialized public slot still uses ordinary
unset. The selected inherited-private raw-name lookup invokes Parent's method with
Child called scope; its ordinary lexical unset removes the real private slot.
The saved RESULT retains one receiver owner through normal return or abrupt frame
unwind. Guard authority requires that internal call and its adjacent saved frame;
an ordinary direct call to the same method gains no implicit guard.
One native/source original and a genuine state cut212 =165 reached +47 derived
cover public bypass, typed name reception, private deletion, `seen=13` and restoration;
abrupt cleanup is a task-local derived check. That historical cut did not admit
other signatures, absent/public-unset or protected selection, wider receivers/names
or recursive magic. Unrecognized pending receivers or names conservatively stop
when a declared `__unset` exists, without evaluating a receiver in demand detection.
[Magic unset review](../../coverage/semantics/magic-unset-review.json).

For declared ordinary public int slots, INITIAL first unset bypasses the callback;
a later UNSET invokes the inherited unsetter. Captured descriptor history survives
repopulation with VALUE `7`. Only UNSET magic demand is suppressed under the active
guard: initialized VALUE deletion stays ordinary. Exact live compiled-local
release/frame history retains IN_UNSET during Probe D, ending before the result
marker and receiver destruction. Four originals and 579 focused premises cover
recursive suppression/reset, CV-null lifetime, supplied throw/following store `42`, full
saved call guards and budget resumption. Wider types, absent/dynamic/protected,
readonly/hooked slots and general reentry remain partial; private evidence retains
its earlier cut. [Public unset review](../../coverage/semantics/public-unset-review.json).

Terminal `unset` also admits an undeclared literal, nonempty property name on a
direct non-This CV receiver, including anonymous instances, with the existing
ordinary public `__unset(string): void` owner/signature/body contract.
`PROPERTY = eps` certifies declaration absence; present descriptors use the
injective Some form.
Fresh capture requires live slot absence and no actual cached property table.
Entered/result history retains the selected receiver/name after binding, slot or
cache changes. Existing `__get` and `__isset` methods are not called by unset.
The same-object/name guard suppresses recursive missing-slot unset through actual
PPUNSET resolution. Its authentic void frame-exit and live destruction-frame
membership retain the guard during compiled-local destruction, ending before
the plain RESULT marker. That marker owns one receiver; ordinary release cleanup
may follow its raw pop. Five source agreements, separate author AL99/110/158 and
independent AL82/32 fixtures, and six ordinary legacy SL gates pass at their
recorded 503-module cuts. Wider names/producers, cache-present entry, signatures
and lifecycle combinations remain partial.
[Missing unset review](../../coverage/semantics/anonymous-missing-unset-review.json).

Legal `__isset` declarations may also omit the parameter type under the existing
arity/reference/default/return restrictions. Language-triggered magic consumers
retain the typed-string source proofs below; declaration acceptance does not
admit an untyped magic callback. See the
[method-image review](../../coverage/semantics/throwable-trace-methods-comparison-review.json).

A selected public nonstatic `__isset(string $name): bool` uses the same closed
physical method-source proof, with a separate terminal-isset call/result protocol.
Direct CV/literal declared-private tests invoke the inherited method; initialized
accessible slots and typed INITIAL slots bypass it. The actual callback boolean
passes unchanged to `ISSET_NEXT`, so a false result skips later operands. Parent
lexical/private scope and Child called scope remain distinct, and cast storage is
unchanged. A saved RESULT retains one receiver owner through return or abrupt
frame discard. One original and state215 =164 reached +51 derived cover the
selected behavior; abrupt cleanup is a task-local derived check. Other signatures,
traits/owners, property families, receivers/names and recursive magic remain
unsupported. At that cut, selected getter-present coalesce combinations stopped
explicitly; the paired coalesce consumer is described below.
[Magic isset review](../../coverage/semantics/magic-isset-review.json).

Terminal `isset` also admits an undeclared literal, nonempty property name on an
emitted external CV, including anonymous instances. The public ordinary
`__isset(string): bool` retains its existing parentless, nonreadonly owner/body
contract; the route requires no getter or property hook. `PROPERTY = eps` records
immutable declaration absence, authenticated by effective lookup and the existing
class/declaration replay invariant. Fresh capture checks live slot absence and
the actual CV; entered/result validation preserves the saved object/name after
CV clearing or dynamic-slot population. One RESULT hold owns the callback
receiver while call frames borrow it. Five original agreements, separate author
224 and independent 89+24 AL conditions, and affected private/getter-pair/empty
SL fixtures pass at their recorded cuts. Wider consumers, signatures, reentry
and lifecycle compositions remain partial.
[Missing-property review](../../coverage/semantics/anonymous-missing-isset-review.json).

Terminal missing-property `isset` also admits the existing same-owner untyped
by-value `__get` alongside typed-bool `__isset`. Both producers retain their
source/target proofs; the operation calls only Isset and preserves its Boolean.
The new absence certificate authenticates an emitted external CV, literal name
and actual terminal Isset source, keeping paired `empty` on its separate Get
dispatch. Fresh capture and saved name/receiver history use the existing rules;
no task, result, root, storage or 380/408 rule changes. Three originals agree at
their separate 507-module SL cuts; author AL92/43 and peer AL84/25 pass separately.
The earlier fixture failures and finite owner checkpoint retain zero credit.
Wider names, signatures, receivers and lifetimes remain partial.
[Missing isset pair review](../../coverage/semantics/anonymous-missing-isset-pair-review.json).

Missing-property `isset` also accepts an initialized, nonempty plain non-NUL
string-CV name with typed-bool Isset and either the admitted same-owner Get or
no Get. The shared source helper retains the literal proof and reuses the existing
CV source contract. Fresh capture authenticates the actual selector; the saved
record and matching frame/result retain it after formal-name, caller-name and
receiver rebinding. Get stays inactive and the callback Boolean is preserved.
Three originals agree at separate 507-module SL cuts; author AL88/88 and peer
AL110 pass separately, with no runtime or fixture correction. Wider name
producers, signatures and lifetimes remain partial.
[Missing isset CV review](../../coverage/semantics/anonymous-missing-isset-cv-pair-review.json).

Terminal literal-name `empty` also admits genuinely absent declarations on an
external CV receiver, including anonymous instances. With the existing typed-bool
`__isset` and same-owner untyped by-value `__get`, false skips Get and true calls
Get with the captured receiver/name. Without Get, either Isset boolean yields
empty true. Optional PROPERTY identity separates declaration absence from the
existing declared-private route; only fresh entry checks physical slot absence
and the caller CV. The saved RESULT retains one receiver owner through both
borrowed calls, including formal-name rebinding and caller-CV clearing. Four
distinct originals agree at their recorded 507-module SL cuts; author
63/79/56/35 and independent 87 AL conditions, plus the affected declared-private
209-condition SL fixture, pass separately. Earlier fixture binding failures keep
zero credit. Wider consumers, signatures, reentry and lifecycle combinations
remain partial. [Missing empty review](../../coverage/semantics/anonymous-missing-empty-review.json).

Missing-property `empty` also accepts initialized, nonempty plain non-NUL
string-CV names with the same typed-bool Isset and admitted same-owner untyped
by-value Get, or no Get. A shared site/line helper preserves the old literal
AST premise exactly and otherwise reuses the existing CV source proof. Fresh
entry captures the live name, receiver and slot absence; saved Get history keeps
the original selection after both caller CVs change. False skips Get; no Get
always yields empty true. CV Get results retain the known-integer bound.
Three original SL507 comparisons and separate author AL87/99 and peer AL86
fixtures pass on their first attempts. Wider names, signatures, receivers and
lifetimes remain partial.
[Missing empty CV review](../../coverage/semantics/anonymous-missing-empty-cv-pair-review.json).

Terminal `empty` now also accepts that inherited bool `__isset` when `__get` is
absent. Either callback boolean delivers true before the receiver-owning RESULT
pops. The borrowed call and saved receiver use the existing isset protocol;
caller-CV rebinding does not invalidate the captured selection. A callback throw
keeps the same Exception through receiver destruction and actual catch binding.
Three originals and focused242 (224 reached +18 derived) cover false/true/throw,
callback isset guards, Get inactivity, receiver ownership, cached result and budgets.
The plan authenticates the consumer flag against the source AST; mismatched flags,
lines, names, methods and missing source are derived refusals. Ordinary isset and
the getter-present route keep their prior behavior; no new phase or task is added.
[Isset-only empty review](../../coverage/semantics/magic-empty-isset-only-review.json).

With no `__isset`, terminal `empty` now skips the inherited public untyped
by-value `__get` for the same external CV/literal private-property family.
Authenticated preparation delivers true without creating a BASE receiver owner;
both source-CV identity and inaccessible/missing effective-private lookup are
checked. Two originals and 235 focused premises (201 reached +34 derived) cover the skip,
initialized-public false bypass, later real getter return/throw and catch,
source/flag/owning-operand/dynamic-slot refusals and budgets. A native GC diagnostic
exposed an artificial BASE decrement; the focused clean-collection prefix now
preserves the buffer and one receiver owner through private empty. The diagnostic
stops before unsupported `gc_status` and has no full-source credit. Other quiet-CV
GC paths remain open; terminal isset/coalesce were also open at that cut.
[Getter-only empty review](../../coverage/semantics/magic-empty-get-only-review.json).

Terminal `empty` of that external CV/literal private property now composes the
inherited bool `__isset` with a public nonstatic nonref `__get($name)` having no
parameter or return type, declared on the same parentless ordinary owner. False
skips the getter; true calls it with the original name and captured receiver. One
saved RESULT owns the receiver across both borrowed calls. Null/bool/int and byte
strings use PHP truth; only empty bytes or exactly ASCII `0` make a string empty.
At that primitive cut, NaN and owning result families stopped explicitly. Parent
lexical scope and Child called scope remain distinct, and initialized public or
typed-INITIAL slots bypass both callbacks. An active getter can still read its own
initialized private slot ordinarily. The original integer slice and state208 =138 reached
+70 derived cover those seams, name/source/task/frame refusals, rebound caller CV,
budget resume and normal receiver release. Both abrupt receiver releases are
derived state checks, not throwing-source agreements. Recursive magic, other
signatures/results and wider quiet receivers/names remain partial.
[Magic empty review](../../coverage/semantics/magic-empty-review.json).
One further original covers nine null/bool/literal-string returns, including NUL
and `0` plus NUL. State155 =132 reached +23 derived checks the actual INTERNED
payloads, saved receiver owner release, pure conversion and late budget resume. REQUEST
carrier authentication and stale/mismatched/invalid-byte refusals are constructed
controls; they add no computed-producer source claim or heap ownership machinery.
[Primitive result review](../../coverage/semantics/magic-empty-scalars-review.json).
Non-NaN float RVs now use the existing numeric truth helper after a 64-bit range
guard: both signed zeros are empty; other finite/subnormal values and infinities
are not. One further original and state145 =132 reached +13 derived check nine
actual float bit patterns, saved receiver owner release and late budget equality.
At that cut, NaN and invalid-bit refusals were constructed result-state controls.
[Float result review](../../coverage/semantics/magic-empty-floats-review.json).
NaN getter truth now emits its Warning after Get returns, with the isset guard
and saved receiver still active. Default reporting and return-true/throwing
handlers agree in three originals. Handler CV rebinding cannot replace the saved
NaN: normal completion yields empty false; a throw retains the same Exception.
The last receiver owner is released before branch output or catch binding.
Normal141 at5a05 and throwing101 atb66 total242 checks (195 reached +47 derived),
covering callback guards, genuine receiver/destructor/catch steps and budgets.
Default dispatch and malformed record/value/packet refusals are derived controls.
[NaN warning review](../../coverage/semantics/magic-empty-nan-review.json).
Ordinary user-object RV truth now caches empty false, then disposes the RV while
the isset guard and saved receiver remain; Get is already inactive. The phase owns
only the receiver and survives an RV destructor's caller-CV rebinding. Normal RV
disposal releases the receiver next; a throwing RV destructor keeps the same live
Exception through receiver destruction and actual catch binding. Two exact originals
and focused247 (188 reached +59 derived) cover these steps and budgets. Same-object
RV/receiver and extra-owner cases are derived controls that preserve allocations and
skip user destructors after ordinary release bookkeeping.
[Object RV review](../../coverage/semantics/magic-empty-object-rv-review.json).
stdClass RVs now use the same phase without changing pure truth or storage/return
rules. Two originals place an ordinary owned payload in the RV: its destructor
rebinds the sole caller CV and returns/throws while the box storage pin and saved
receiver remain. Focused222 (208 reached +14 derived) checks actual NEXT0→1,
Get-inactive/isset-active guards, box/payload retirement before receiver destruction,
the same Exception at catch and budgets. Kind/bounds and already-freeing box
refusals are derived controls; the original stdClass cut is retained.
[stdClass RV review](../../coverage/semantics/magic-empty-std-rv-review.json).
Nonempty array RVs now use the same receiver-only phase. The array retires before
its owned payload destructor runs with isset active and Get inactive; the saved
receiver survives caller-CV rebinding and is released after payload disposal.
Immutable empty literal RVs use direct true delivery: they have no children and
are not GC candidates. Three originals and focused255 (222 reached +33 derived)
cover these paths, the same Throwable at catch and budgets. At that cut,
mutable-empty refusal and an extra array owner preventing premature payload
destruction are derived.
The empty helper gains only the authenticated immutable-empty case; generic array,
key, return and destruction rules are unchanged. Other internal-object RVs and
wider signatures/receivers/lifecycles remain partial.
[Array RV review](../../coverage/semantics/magic-empty-array-rv-review.json).

Mutable empty getter arrays now use the same receiver-only phase with cached
true. Ordinary RV release retires a sole table and removes its GC-buffer entry
before clearing isset and releasing the receiver; a held table remains allocated
and buffered with one owner. Three originals cover sole/shared true and a receiver
destructor's Exception. The 265 focused premises across normal171 and throw94 cuts
(245 reached +20 derived) identify the actual table at receiver destruction,
preserve cached results and catch identity, and check budgets. A native-only roots
pair observes roots 1 versus 2 after prebuffering; its prefix bridge is static and gives
no `gc_status` model/source agreement. The earlier mutable-empty negative is
superseded without replay; generic array/GC/return/disposal rules stay unchanged.
Sole-owner public-NaN lifetime and wider quiet-CV GC remain open.
[Mutable array RV review](../../coverage/semantics/magic-empty-mutable-array-rv-review.json).

Empty and singleton WeakMap getter RVs now use the same receiver-only phase;
both are truthy regardless of entry count. Singleton disposal unregisters the
live leaf key before releasing an ordinary leaf value. During its destructor,
the empty map's physical storage pin remains while dropping the key makes
`WeakReference::get()` return null; the model retains its nonowning target history.
The saved receiver survives caller-CV nulling and is released after value/map
retirement, preserving a value destructor's Exception at catch. A held map delays
value disposal until after the empty result, so receiver destruction can nest
inside that later callback. Four original sources and 333 focused premises
(315 reached +18 derived) cover these orders, the real pin, wrapper-result refusal,
empty-map truth and budgets. One faulty raw-wrapper expectation and two narrow
diagnostics retain zero credit. Only the RV-kind arm changes; generic WeakMap,
GC and destruction machinery stays unchanged. Wider map/key/value lifetimes and
sole-owner public-NaN retirement remain open.
[WeakMap RV review](../../coverage/semantics/magic-empty-weakmap-rv-review.json).

Real static Closure getter RVs now use the phase for ordered RV release, with
one ordinary payload captured by value or reference. For a sole RV, Closure
disposal expires its weak wrapper before releasing captures; the phase keeps the
receiver through the payload destructor and its possible Exception. A held Closure
stays live after `empty`, whereas a retained reference cell keeps the payload alive
after the Closure expires.
The later held/alias write then permits nested receiver destruction inside the
payload callback. Four originals and 452 focused premises (447 reached +5 derived)
verify actual DIRECT/ALIAS edges, static scope without an implicit receiver,
cell owners 2 to 1 and the subsequent null write, logical weak reads, catch identity
and budgets. Only the raw REALCLOSURE RV-kind arm changes; capture, reference,
free and GC rules stay unchanged. The original reference-export source mistake
retains zero credit. Fake/internal/wrapped Closure RVs remain unsupported; wider
implicit-receiver, cold-static, reentry and cycle combinations are outside this
validated slice.
[Closure RV review](../../coverage/semantics/magic-empty-closure-rv-review.json).

The paired route also admits a public nonref `__isset(string $name)` with no
return declaration. Booleans keep the existing decision; an ordinary INSTANCE RV
caches true in the existing receiver-owning result marker, then ordinary eager
disposal finishes before Get can start. For a sole RV, its destructor can null the
caller CV and change the getter-visible value without losing the captured receiver
or IN_ISSET; Get is inactive during this disposal. A held RV survives the result and
permits later nested receiver destruction. A destructor throw skips Get and keeps
the same Exception through receiver release and catch.
Four originals and 313 focused premises (289 reached +24 derived) cover these
states, authenticated saved-prefix call certificates, Boolean/source/result
refusals and budgets. The original normal certificate failure and three diagnostic
records remain zero credit. At that cut, module407 required a typed-bool callback;
other untyped scalar/null/internal-object results and wider recursive cases
remain Unsupported. No new task, owner or generic destruction/GC rule is added.
[Isset RV review](../../coverage/semantics/magic-empty-isset-rv-review.json).

The paired route now also truth-tests live array RVs before ordinary disposal.
Nonempty truth survives table retirement and a payload destructor that clears the
caller CV and changes Get's value from 1 to 0. A held table delays that destructor
until after Get/result, when receiver destruction may nest inside it. A supplied
payload-destructor Exception skips Get and reaches the same catch/destination.
Mutable empty tables use ITEMSeps despite NEXT1/SERIAL1 history: false skips a
throwing Get, with the table retired before receiver destruction. IN_ISSET and
the saved receiver remain through sole payload cleanup; Get is inactive there.

[Four originals and 416 focused premises](../../coverage/semantics/magic-empty-isset-array-rv-review.json)
check these lifetimes, full call validity and budget resumption. Bounds/allocation
refusals and the derived old-object truth bridge add no earlier-suite execution
credit. At that cut, the existing VALUEtrue destructor cleanup certificate, bool
decisions, ordinary/no-Get typed-bool admission and generic array/free/GC rules remained unchanged.
Embedded reference cells, cycles, wider alias/reentry histories and other untyped
result kinds remain partial; no full-program GC-preservation claim is made.

Terminal `isset` now consumes the already-admitted absent-return
`__isset(string $name)` for the selected inherited private-property CV/literal
family, including a present untyped `__get`. Authenticated PREP deferral prevents
ordinary getter interception; terminal isset never calls Get. Live ordinary
INSTANCE and array RVs cache truth in the receiver-owning result marker before
ordinary disposal. For a sole RV, IN_ISSET and the captured receiver remain through
its destructor despite caller-CV nulling, then end before receiver destruction.
A held array delays payload disposal until after the result, permitting nested
receiver destruction. Mutable-empty false retires its table before receiver D;
a supplied payload-destructor Exception preserves the same catch and destination 42.

[Four originals and 457 focused premises](../../coverage/semantics/terminal-isset-rv-review.json)
check these lifetimes, Get inactivity, actual saved-prefix/full call validity,
source/result refusals and zero/resume budgets. The original pre-execution source
failure, derived-fixture failure and prefix diagnostic retain zero credit.
Only modules 407/408 change; no task/schema or generic destruction/GC rule changes.
No-Get `empty` remains typed-bool; terminal typed-bool-with-Get, other untyped
primitive/internal RVs, recursive and wider ownership/GC histories remain partial.

Selected external CV/literal private-property `??` now pairs the inherited public
nonstatic `__isset(string $name): bool` with a nonref, absent-return `__get($name)`
from the same declaring class. One result marker retains the captured receiver
after the caller CV becomes null. IN_ISSET ends after Isset and its compiled-local
cleanup, before Get starts; IN_GET covers Get and its cleanup. Both are inactive
when receiver destruction runs. Lexical Parent and called Child remain distinct.

The known by-value getter result stays solely in RESULT as a node-free handoff
selects ordinary `COALESCE_RESULT`; BASE never duplicates it. Receiver release
completes before fallback evaluation. False Isset skips a throwing Get; Get zero
suppresses a throwing fallback, null observes the destructor's fallback mutation,
and an ordinary Payload survives receiver D and main output until its later release.
A supplied Get Exception preserves the same catch and destination 42 without RHS
evaluation. [Five originals and 604 focused premises](../../coverage/semantics/magic-coalesce-review.json)
cover these transitions, actual frame-exit/full call validity, source/caller/tail
refusals and budgets beginning before PREP. Separate source and state cuts retain
the original binding failures, duplicate-discard failure and fixture binding failure
at zero credit. No generic coalesce, ownership, destruction or GC rule changes.
The transfer is generic for known BYVAL values; validated result histories are
zero, null and ordinary Payload. Untyped Isset remains excluded from the getter-present
route; reference Get, wider values and local-destructor/reentry lifetimes remain partial.

The same external CV/literal inherited-private `??` source now admits no-Get
objects with the existing typed-bool or absent-return `__isset(string)` signature.
GET is optional metadata, without a fake method target. Both booleans deliver
quiet NULL; an ordinary live INSTANCE RV makes the decision true. Its separate
receiver-owning continuation caches NULL while ordinary RV disposal runs with
IN_ISSET and IN_GET inactive. Only afterward does receiver release precede the
ordinary fallback. Sole RV destruction sees a live receiver through WeakReference;
held RV destruction runs later and sees the retired receiver. A supplied RV-D
Exception cancels fallback, preserving the same catch and destination 42.
[Four originals and 640 focused premises](../../coverage/semantics/magic-coalesce-no-get-review.json)
check actual compiled-local guard exit, saved NULL/SOURCE cleanup receipts, owner
counts, weak visibility and PREP budget resumption. Booltrue is a derived bridge.
The getter-present route has a static optional-record compatibility bridge, with
no renewed earlier execution credit. Other RV kinds, false owning RVs, reference
returns, wider receiver/property forms, aliases, cycles and reentry remain partial;
generic coalesce, destruction, roots and GC rules are unchanged.

Terminal literal-name `??` also admits undeclared properties on an external CV,
including anonymous instances. It uses the existing typed-bool Isset and
same-owner ordinary by-value Get, or no getter. False skips Get; a returned zero
skips fallback, while NULL and either no-Get boolean reach the quiet fallback.
Isset's guard clears before Get, and the single receiver-owning RESULT releases
before fallback. Saved selection survives formal-name mutation and caller-CV
clearing; only fresh entry checks physical slot absence. An explicit binary-parent
and quiet-tail proof keeps undeclared `??=` outside this increment. Five distinct
originals, focused state controls and the two affected declared-private fixtures
pass at their separate cuts. Wider forms and lifetimes remain partial.
[Missing coalesce review](../../coverage/semantics/anonymous-missing-coalesce-review.json).

Binary `??` on a missing property also accepts an initialized, nonempty plain
non-NUL string-CV name. A separate declaration-absence CV plan uses the existing
typed-bool Isset and admitted same-owner untyped by-value Get, or no Get. Fresh
entry captures the name, receiver and slot absence; matching saved records keep
that selection after both caller CVs change. Isset ends before Get; false and
no-Get decisions reach fallback, while a returned zero skips it. CV Get results
retain the known-integer bound, and the binary-parent/quiet-tail fence keeps
missing CV-name `??=` Unsupported. Three SL507 originals and separate author
AL87/100, assignment-control30 and peer AL93 checks pass at their recorded cuts.
The failed derived-marker controls and recorder projection retain zero credit.
Wider producers, signatures, results and lifetimes remain partial.
[Missing coalesce CV review](../../coverage/semantics/anonymous-missing-coalesce-cv-pair-review.json).

These missing-property `isset`, `empty` and binary `??` CV-name routes also admit
an initialized plain string whose bytes are empty. Five declaration-absence gates
retain their nonempty literal premises and reuse the existing static CV-source
proof. Fresh entry still captures the actual name, receiver and slot absence;
saved frame/target/result history keeps the empty name after both caller CVs
change. Typed-bool Isset, same-owner admitted Get/noGet, the integer CV Get-result
bound and the missing `??=` fence remain unchanged. Three new originals agree at
their separate SL507 cuts, reusing each native observation once. Focused entry
SL49 and independent history SL93 fixtures have separate source0 cuts; the precode
SL34 checkpoint adds no implementation credit. Its earlier notation failure and
AL300 timeout retain zero credit. Wider producers, signatures, results and
lifetimes remain partial.
[Empty CV-name review](../../coverage/semantics/anonymous-missing-empty-name-review.json).

These compositions also consume an already compiled public nonstatic by-value
`__get(string $incoming)` on named parentless owners, with no return declaration.
Module 408 matches the
physical parameter type to the compiled string type while preserving the old
untyped case. Shared literal/CV originals cover false missing and true private
Some dispatch, plus literal getter-only Empty skipping Get. A separate history
witness preserves the captured empty name after both caller CVs change and the
typed formal becomes integer 9; receiver destruction precedes caller output.
The same proof admits the existing declared-private `??=` consumer: Get's 7 keeps
the value without evaluating RHS or Set. Four distinct originals and separate
SL fixtures with 69 and 101 conditions pass; the precode SL checkpoint with 36
conditions gives no source credit.
The integer result bound for CV names and prior literal result domain are unchanged.
Missing `??=`, typed Get in ordinary/reference reads, anonymous typed-Get compilation
and wider headers/receivers/lifetimes remain partial.
[Typed Get review](../../coverage/semantics/magic-property-typed-get-review.json).

Anonymous classes also compile that required canonical string Get header with no
return declaration. A separate module 383 member arm preserves the old untyped
case and existing class/unit gates. The admitted runtime compositions then apply
to parentless anonymous owners with class-free Get bodies and the existing
template identity. Two originals agree at separate private cuts, with separate
SL fixtures containing 53 compiler and 102 history conditions. Child-class Get
factories and wider owners/results/lifetimes remain
partial; ordinary/reference property-read and update bounds are unchanged.
[Anonymous typed Get review](../../coverage/semantics/anonymous-typed-get-member-review.json).

Named parentless owners also admit nullable string, well-formed string-bearing
unions and `mixed` name parameters in these existing compositions. Declaration
acceptance reuses the ordinary Get header restrictions. The runtime source proof
normalizes the physical type in its actual defining namespace/import, class,
member, file and parameter-line context and requires the exact compiled type;
string membership alone cannot authenticate a forged signature. Empty and
singleton raw unions remain refused. Numeric-name source controls preserve string
identity in union/mixed Get; actual compiled-type controls also verify nullable
exact string reception. Saved selection survives later formal mutation and
caller-CV clearing.

Two originals agree at their separate SL507 cuts with each native observation
reused once. Separate author SL98 and independent SL135 fixtures pass; the
before-code SL48 checkpoint, Unsupported baselines and invocation-only failures
retain zero source credit. Generic ordinary/reference Get,
factory/result/root bounds and missing `??=` remain unchanged and
partial. [String-compatible Get review](../../coverage/semantics/magic-property-string-compatible-get-review.json).

Anonymous parentless owners also compile these wider name headers for the same
class-free Get compositions. Module 383 admits raw nullable, union and `mixed`
header candidates; ordinary method compilation still owns normalization and
string acceptance. The runtime proof is unchanged and checks the actual generated
owner, defining environment and exact compiled type. A namespace/import witness
preserves the resolved class arm in `Imported|int|string`, while all three Get
bodies receive numeric-looking name `"12"` as a string. Independent saved history
keeps that name after caller rebinding and formal mutation, then releases the
receiver before caller output.

Two new originals agree at separate SL507 cuts. Actual-context SL106 and
independent history SL141 fixtures pass separately; the provisional-context
precode SL87 and Unsupported baselines retain zero source credit. Untyped factory
admission, child-class exclusion, generic ordinary/reference Get, results, roots,
PREP and missing `??=` retain their prior bounds.
[Anonymous wider Get review](../../coverage/semantics/anonymous-string-compatible-get-review.json).

Ordinary missing-property reads also admit an own parentless public by-value
`__get(string $name)` without a return declaration. The receiver is an emitted
external non-This CV; existing literal or plain non-NUL string-CV names use a
strict-identity-left or discarded-expression source and its exact saved tail.
Raw method/body authentication and exact owner/class identity fence this admission.
The implicit call uses existing typed parameter reception and one RESULT receiver hold.
Its captured string name survives reassignment of the formal to integer 9;
the new typed route admits only a known integer result.

Two distinct originals agree at separate production SL507 cuts with each native
observation reused once. Author SL76 and independent SL111 fixtures pass
separately, including genuine TYPE_RECEIVE, source/tail/descriptor refusals,
receiver ownership and budget continuation. Precode SL54/54, failures and
diagnostics retain source0 without AL or aggregate credit. Shared untyped Get,
factory/This/indirect/reference/update, PREP and root formulas retain their prior
bounds. Wider headers, results, receivers and lifetimes remain partial.
[Ordinary string Get review](../../coverage/semantics/magic-property-string-read-get-review.json).

Those canonical-string Get reads also admit a direct singleton `echo` expression.
The source proof requires exactly one item at `[PCFIELD 0, PCINDEX 0]`; its saved
tail restores the actual Echo origin and emits at the same property site using
the existing echo-line rule. The previous identity/discard premises are preserved.
Header, owner/class, missing-property, external-CV, integer-result and receiver
ownership bounds remain. Two distinct SL507 originals reuse native observations
once; author SL67, independent SL133 and precode SL49 keep separate source0 cuts,
without AL or aggregate credit. The Unsupported baselines remain zero credit.
Comma echo, other consumers, signatures, results and lifetimes remain partial.
[Singleton echo Get review](../../coverage/semantics/magic-property-string-echo-get-review.json).

Those ordinary reads now admit required nullable-string, well-formed
string-bearing-union and mixed name headers on named and source-validated
parentless anonymous owners. Existing raw-header normalization in the defining
context authenticates each actual TYPE; an explicit nonempty TYPE guard preserves
genuine untyped Get and its noninteger results. Consumers, class-free bodies,
absent return declarations, integer results and receiver ownership retain their bounds.
Two new production-SL507 originals rotate headers across strict-left, discard and
singleton Echo, preserving string names through formal reassignment. Native
observations are reused once; author SL107, independent SL142 and genuine-untyped
SL40 fixtures retain separate source0 cuts, as do precode SL63/58 and Unsupported
baselines. No AL, aggregate or header/consumer cross-product credit is claimed.
Wider consumers, returns, results and lifetimes remain partial.
[Compatible ordinary Get review](../../coverage/semantics/magic-property-compatible-read-get-review.json).

Those ordinary typed-name reads also return known NULL, Booleans, finite doubles
and authenticated non-NUL INTERNED strings. Existing source/header/consumer and
receiver bounds remain; genuine untyped CV-name Get keeps its NULL-result refusal.
RESULT retires its receiver hold before COPY; in the checked states, actual owners
change from two to one without adding a scalar heap edge. REQUEST/plain strings, nonfinite values,
NUL bytes, owning results and references retain their exclusions.
Two separate production-SL507 originals reuse native observations once. Author
SL85, peer SL109, the unchanged genuine-untyped companion SL32 and precode SL46/47
keep separate source0 cuts, with no AL or unique aggregate. Both peer pre-main
positive-fixture failures stay zero. Actual `47dc49ad9`/508 loading is separate,
quiet and stable with source0. Return declarations and wider consumers, producers,
receivers and lifetimes remain partial.
[Primitive ordinary Get review](../../coverage/semantics/magic-property-primitive-read-get-review.json).

Those ordinary typed-name reads also admit canonical `int`, `float`, `bool`,
`string` and `mixed` return declarations. The existing verifier uses the defining
function's strictness before Get RESULT; tested weak literal conversions add no
source-store writes.
Raw syntax and normalized RETURNS retain defining-context authority; quiet Get
keeps its absent-return proof. Bare returns under those declared types in methods
and lexical class Closures use
method diagnostics at the real return line, while named functions retain function
wording. Anonymous Get return errors C-format class and member separately.
Two production-SL507 originals reuse native observations once. Author SL134/36 and
peer SL103 keep separate source0 cuts, including exact strict rejection, caller
preservation, guard/release and public budget equality. Three static diagnostics,
a caught-message source and the original named-function control retain their own
cuts; failures and expectation corrections stay explicit. Actual `a2907470c`/508
and joined loading (`9db1e93a`, quiet/stable/reaped) are separate with source0.
Nullable/union/void/never returns, wider producers and lifetimes remain partial.
[Scalar-return Get review](../../coverage/semantics/magic-property-scalar-return-get-review.json).

Those reads also admit canonical `?int`, `?float`, `?bool` and `?string` return
syntax. Raw nullable syntax, normalized `[T,null]` and defining context must agree;
existing exact/weak/strict checks and result/receiver bounds remain. Equivalent
named `T|null` declarations share the normalized type. The initial nullable cut
retained raw-union refusal before the callback; the primitive-null union cut below
supersedes that refusal.
Two production-SL507 originals reuse native observations once. Author SL125/19,
peer SL86 and the affected old scalar SL134 retain separate source0 cuts; the
union control is not a native agreement and historical SL134/36 stay separate.
All new checks pass first try. Actual `532c971b2`/508 and joined loading (`18abf3d4`,
quiet/stable/reaped) are separate with source0. Other return forms, wider
producers and lifetimes remain partial.
[Nullable-return Get review](../../coverage/semantics/magic-property-nullable-return-get-review.json).

Canonical `int|string` and `string|int` Get returns now use matching raw
two-Identifier unions and defining-context normalized types under those same
ordinary typed-name bounds. Exact numeric-looking strings retain their type;
tested weak Boolean returns choose integers, while NULL/strict Boolean return
errors preserve caller destinations. Existing95 verification runs before
GetRESULT; its finite-float/deprecation routes were source-traced without new
source credit. Two new private507 originals agree with native once reused;
SL93/32 and independent SL82 retain separate source0 cuts, including actual
STRING return/copy and receiver owners2→1 in the checked states. Actual019544
and joined8d67820/508 (16.949847s, source0) remain separate. Other union and
wider return/value/consumer/root/lifetime bounds remain partial.
[Int/string-union Get review](../../coverage/semantics/magic-property-int-string-return-get-review.json).

Canonical singleton `true`, `false` and `null` Get returns now use the same
ordinary typed-name declaration/source proof. Existing95 accepts only the
matching literal tag, including in weak mode; rejected returns preserve caller
slots before assignment. Two private507 originals agree with native once reused;
SL142 and independent SL107 retain separate source0 cuts for actual rejection,
guard/receiver release and public budget equality. Three whitelist lines changed;
quiet Get, value/root/task and wider lifetime bounds remain. Actual d630 and
joined994493f99/508 (16.131328s, source0) are separate from the private cuts.
[Literal-return Get review](../../coverage/semantics/magic-property-literal-return-get-review.json).

Canonical primitive `T|null` and `null|T` Get return unions now share those
ordinary typed-name bounds, with both raw orders covered for `int`, `float`,
`bool` and `string`. Raw two-Identifier syntax, normalized branch order and
defining context must agree; quiet Get still requires an absent return. Existing95
preserves NULL, weak conversion, strict int-to-float promotion and rejected-return
caller slots. Two private507 originals agree with native once reused. New SL135/93
and affected125/19/86 retain separate source0 cuts. A preexecution19 fixture binding
failure is preserved; only its unused binder was corrected and19 rerun, with125
unchanged. Whole10 and actual484d runtime/test/Make seams are independently CLEAR;
separate joined484d/508 passes in33.197897s with source0. Wider return/value/
consumer/root/lifetime forms remain partial.
[Primitive-null union Get review](../../coverage/semantics/magic-property-nullable-union-return-get-review.json).

Nullable literal `?true`/`?false` Get returns and either raw union order with NULL
now use that same declaration/source proof. Existing95 accepts only the matching
literal or NULL; wrong INT/BOOL values reject even in weak mode before caller
stores. Two private507 originals agree with native once reused; new SL150/124
retain separate source0 error/guard/receiver/public-budget cuts. Three old pure
mask queries now assert admission and are tested verbatim in150; historical142/135
source/stage/other checks stay unchanged without replay or whole-state renewal.
Whole10 and actual c465 runtime/test/Make seams are independently CLEAR; later
joined loading passes after equivalent guard factoring, with both original
fixed-cap timeouts retained at zero credit. Quiet and wider return/value/consumer/root/
lifetime forms remain partial.
[Nullable-literal Get review](../../coverage/semantics/magic-property-nullable-literal-return-get-review.json).

Ordinary typed-name Get also admits well-formed canonical unions of
int/float/string/bool/true/false/null. The complete raw Identifier list must agree
with defining return normalization; duplicates, bool/literal overlaps,
true|false and mixed unions remain rejected. Shared verification preserves tags,
weak numeric preference, caller destinations on rejection and receiver cleanup under
the existing source/value/consumer/root bounds. Six private507 originals and
119/120 assertions, including fixture setup, retain their cuts; joined508 loading
adds zero source credit.
[Primitive-union Get review](../../coverage/semantics/magic-property-scalar-union-return-get-review.json).

Those ordinary scalar/nullable/primitive-union return declarations also admit a
required untyped Get-name parameter. Raw ABSENT and normalized TYPEeps must agree;
the legacy untyped getter without a return declaration retains its prior route.
Parentless/class-free bodies, primitive carriers, external-CV consumers, return
verification and receiver cleanup retain their bounds. Four private507 originals
and159/124 assertions remain separate from joined508 loading/source0.
[Untyped-name Get return review](../../coverage/semantics/magic-property-untyped-name-return-get-review.json).

Canonical `void` and `never` return declarations now share those ordinary
by-value Get bounds. Void bare return or fallthrough supplies NULL; never
fallthrough raises TypeError at the method end line, while explicit throw and
exit keep their own behavior. Anonymous never diagnostics retain Zend's full-name
C-string truncation (`class@anonymous()`), and illegal returns use method wording.
Seven native-once/private507 originals agree; separate SL81/62/104 state cuts
check real receiver/formal cleanup and budget resumption, and three compiler
controls check exact diagnostics on line4. Joined508 loading at `2c2c8f051` is
separate with source0. Quiet typed-return consumers, owning returns and wider
source/value/lifetime forms remain partial.
[Void/never Get review](../../coverage/semantics/magic-property-void-never-return-get-review.json).

Ordinary strict-identity-left and discarded Get reads now accept live array
results, including canonical `array` returns and existing mixed/typed-name
absent-return headers. Raw/normalized declarations keep their defining context;
results require a bounded live HARRAY. Scalar/union helpers, quiet typed-return
and Echo fences stay unchanged. Nine native-once originals agree, covering
COW/shared references, receiver and payload destruction, exception replacement/
Previous and a live post-catch read. Separate SL75/20/121 checks distinguish
result ownership and live catch binding from EOF global teardown. Joined508
loading is separate/source0. Object results, Echo array Warnings and wider
signatures/receivers/lifetimes remain partial.
[Array Get review](../../coverage/semantics/magic-property-array-return-get-review.json).

Those ordinary strict-identity-left/discard reads also admit live, nonfreeing
STDINSTANCE or INSTANCE results with a present class, including canonical
`object` returns and existing mixed/typed-name absent headers. Raw return
context and bounded allocation remain authenticated; internal object kinds,
Echo, quiet typed returns and wider declarations/lifetimes stay partial.
Six native-once originals agree. Separate SL96/21/24/121 checks retain the
same receiver/RV through guard release and caller RHS, reject real Echo/internal
cases, and preserve direct-object pending exceptions/Previous and EOF retirement.
Public release-job accounting remains distinct from the raw Get step;
joined508 loading adds source0.
[Object Get review](../../coverage/semantics/magic-property-object-return-get-review.json).

Selected paired Empty, binary `??` and existing private `??=` also admit
canonical `int` Get declarations in their defining strictness. Weak conversion
preserves caller/name values; authenticated anonymous method diagnostics survive
receiver-destructor replacement as Previous. Integer zero keeps coalesce's RHS
and setter skipped; false Isset keeps the existing producer/write route.
Six native-once originals agree. Separate SL100/32/113/114 cuts retain actual
return conversion, receiver roots, genuine float refusal, pending errors,
live catch/EOF distinctions and full resumption. Fixture corrections keep
original failures at0; composed508 loading is separate/source0. Wider selected
quiet returns, missing-property `??=` and RW/receiver/lifetime forms remain partial.
[Quiet int Get review](../../coverage/semantics/magic-property-int-quiet-get-review.json).

Selected quiet Get also admits canonical `float` returns and bit-valid FLOAT
results through the existing CV-name gate. Weak numeric-string conversion and
strict integer widening retain the declaration's strictness; strict strings
raise the existing TypeError before fallback. NaN Empty truth keeps the Isset
guard through its Warning callback. Authenticated literal same-name Isset
returns false without another callback; argument copying retains the original
source-marker witness. Receiver release still follows the decision.
Four native-once originals agree at separate private507 SL cuts. Separate
SL111/ARRAY32/208/118 checks cover real owners, forged cursor/source controls,
pending errors, live catch/request retirement and full budget resumption.
Original interpreter/output/load failures and the two fixture corrections
retain zero credit; the first finite source keeps its earlier cut.
Joined `ad66eb71c`/508 loading stays separate/source0. CV-name reentry, other quiet result/header
forms, callback reference formals, Echo/RW and wider receivers/lifetimes remain partial.
[Quiet float Get review](../../coverage/semantics/magic-property-float-quiet-get-review.json).

NaN Empty warning callbacks also preserve terminal Isset suppression through
existing authenticated string-CV names, including empty names. Entry reads the
current name; the saved outer name/receiver survives handler selector rebinding.
A different name calls Isset normally, while restoring the original name skips it.
Two native-once originals retain separate private507 production-SL cuts. Separate
SL97/136 checks preserve raw NAME-owner3-to2, source/capture/line/mode guards,
live normal delivery or no-Previous catch, request retirement and0/1/full state
resumption. Original wrong-guard output and two fixture corrections remain0.
Actual `2eccacf5c`/508 loading stays separate/source0. Wider result/header forms,
callback reference formals, recursive consumers and receivers/lifetimes remain partial.
[CV-name NaN Isset review](../../coverage/semantics/magic-property-nan-cv-isset-reentry-get-review.json).

Terminal bool Isset also accepts the existing full typed-Get declaration proof
without calling Get. Getter-only private Empty retains its borrowed CV and
returns true without invoking the typed getter. Four native-once originals
include unused invalid int/array returns and a never-returning companion.
Separate SL74/62/126 cuts preserve private slots and caller aliases, authenticate
source/line/flag authority, and observe Isset guard clearing before a real
normal-result receiver destructor throws with no Previous; caller value42
remains unchanged. Live catch and request retirement remain distinct; the pre-main fixture failure
stays0 and joined508 loading adds source0. Selected return/result, RW and wider
header/body/receiver/lifetime domains remain partial.
[Unselected typed Get review](../../coverage/semantics/magic-property-unselected-typed-get-review.json).

Selected quiet Get also admits canonical `bool`, `true` and `false` returns,
and existing CV-name Get admits Boolean results, including ABSENT-return headers.
False makes Empty true but stays nonNULL for `??` and existing private `??=`,
so present reads skip RHS/setter. Weak bool conversion and exclusive-false
rejection preserve declaration strictness, method names and pending cleanup.
Four native-once originals agree; separate SL108/115/76 cuts retain real
GetRESULT roots, the promoted old query, caller values, Previous and resumption.
The unaccepted Boolean-RHS producer original remains Unsupported0; its fresh
integer-RHS variant preserves that producer boundary and the accepted first row.
Joined447/508 loading stays separate/source0. Wider result/producer/header,
receiver/reference and lifetime domains remain partial.
[Quiet Boolean Get review](../../coverage/semantics/magic-property-bool-quiet-get-review.json).

Existing quiet CV-name Get consumers also admit live raw empty/singleton
WeakMap objects under their source, allocation and nonfreeing checks. Binary ??
and private ??= retain the map through receiver retirement. Empty caches false
before existing map/value disposal and receiver release; key unregister
precedes the value callback, and a value throw preserves the old caller
destination through catch. Multi-entry CV Get results and wider kinds/lifetimes
remain partial.
[WeakMap quiet Get review](../../coverage/semantics/magic-property-weakmap-quiet-get-review.json).

Initialized WeakReference wrappers follow those quiet consumer paths. Binary ??
and private ??= preserve wrapper identity with live or retired targets; Empty
caches false and retires its wrapper result before receiver cleanup, including
a receiver throw that preserves the caller destination. The immutable target
ID is borrowed history; `WEAKREFERENCE eps` denotes a pending constructor and
is excluded. Existing source, allocation, nonfreeing and full-state uniqueness
checks remain. Four native-once originals and separate SL85/87/120/128 fixtures
pass; wider producers and lifetimes remain partial.
[WeakReference quiet Get review](../../coverage/semantics/magic-property-weakreference-quiet-get-review.json).

Authentic unscoped, unbound nongenerator function literals also cross quiet CV
binary ??, private ??= and Empty. Complete captures, no pending capture task
or initialized static cells, and the exact original SOURCE-eps/shared cache
stamp authenticate the result. Unused source static declarations are not
blanket-rejected. Existing literal Empty already handles the throwing-capture
control: last-owner capture disposal precedes receiver cleanup and preserves the caller
destination on throw. Three changed-model source agreements and that retained
prelaw control remain distinct; SL98/106/187/198 fixtures add no source credit.
Fake, bound, other clone/private-cache modes and wider lifetimes remain partial.
[Literal Closure quiet Get review](../../coverage/semantics/magic-property-realclosure-quiet-get-review.json).

Genuine unscoped Arrow results follow those quiet consumers with the same
owner and cleanup laws. Raw Arrow source, BODY child5, CODEARROW marker and
exact IMPLICIT names from source discovery minus parameters authenticate
the template. Captures must be complete; an undefined IMPLICIT slot may be
completed UNINITIALIZED, while ALIAS slots and pending cursors remain refused.
The original unscoped/shared stamp, no binding or initialized static cells
and existing live/cache checks remain. Three changed-source agreements and
the retained prelaw literal control keep distinct cuts; SL115/127/207/216
fixtures add no source credit. Wider producers and lifetimes remain partial.
[Arrow quiet Get review](../../coverage/semantics/magic-property-arrow-quiet-get-review.json).

Unscoped shared-cache clones of those raw function literals and Arrows also
cross quiet CV binary ??, private ??= and Empty. A strictly descending SOURCE
walk checks each immutable ancestor is a raw REALCLOSURE at the same origin
with an exact Unscoped/Shared stamp, ending at an original SOURCE-eps record.
It never reads retired ancestor captures, static cells or allocations. Whole
cache validity still proves ordering and uniqueness; current source/capture/
static/scope/binding and owner/cleanup checks remain. Wrapped/fake ancestors,
private/scoped/unknown stamps and other clone/lifetime modes stay outside.
[Shared-cache clone quiet Get review](../../coverage/semantics/magic-property-clone-quiet-get-review.json).

Original raw named USER FCC wrappers also cross quiet CV binary ??, private
??= and literal/CV Empty. A registered nongenerator NStmtFunction, no binding
or scope record, and the exact SOURCE-eps Unscoped/Shared cache stamp with
whole-cache validity authenticate the live result. Literal Empty checks the
actual result object ID through that same predicate. The wrapper owns no
function-static cells: shared static roots survive
its weak notification and retirement. Empty retires the wrapper before its
receiver, including a receiver throw that preserves the destination. Four
changed-source agreements reuse four native originals once; separate SL
fixtures check ownership, malformed histories and budget0/1/full rejoining.
Wider named wrappers and lifetimes remain partial.
[Named FCC quiet Get review](../../coverage/semantics/magic-property-namedclosure-quiet-get-review.json).

Shared-cache named FCC clones now follow the same quiet consumers. The original
SOURCE-eps guard remains explicit; a separate certificate checks every copied
stamp through raw same-origin NAMED ancestors and strictly lower object IDs.
Current stamp identity, function, SOURCE and Unscoped/Shared fields are checked
explicitly. Retired ancestors add no roots and require no allocation or static
reads; current source/live/binding and whole-cache order/uniqueness guards stay.
Four new originals reuse native observations once at the final guard. Separate
new and affected-old SL fixtures retain zero source credit. Two earlier executed
private-cache counterfacts prompted the explicit field checks; earlier positive
source observations retain their own cut. No cache/free/GC policy changes.
[Named FCC clone quiet Get review](../../coverage/semantics/magic-property-namedclosure-clone-quiet-get-review.json).

Original raw USER public static nongenerator/nonabstract own-method captures now cross the same quiet consumers. The capture occurs in global code through an exact direct class token and literal method placeholder; its named parentless owner has no traits. Indexed raw class/member/body/flags, CODE.NAMES resolution, live equal lexical/called/requested/owner scope and absent receiver/creation/binding authenticate it. The original SOURCE-eps BIND_CLASS-owner Shared stamp must agree with Shared birth policy and whole-cache validity. Literal Empty checks the actual result ID. Shared method-static roots outlive wrapper disposal; Empty retires RV before receiver, including throw and budget rejoining. No cache/free/GC policy changes. [Review](../../coverage/semantics/magic-property-methodclosure-static-quiet-get-review.json).

Same-scope Shared clones and finite clone chains now follow the same quiet consumers. A strictly descending SOURCE certificate retains identical raw METHOD/capture-eps/site/owner and explicit Shared owner stamps. The original SOURCE-eps stamp must satisfy Shared policy at the original id, including after retirement. Pruned historical scope rows may be absent; any present row must remain canonical, with no binding. Current live/source/scope/birth/cache and consumer fences stay exact. No retired allocation, static/capture value or owner reads are added. New sources exercise retired ancestry, shared statics, Empty cleanup/throw and budget rejoining; affected-old fixtures retain source0. [Review](../../coverage/semantics/magic-property-methodclosure-static-clone-quiet-get-review.json).

Direct NName and NNameFullyQualified class selectors also admit case-insensitive spelling for original and authenticated same-scope Shared-clone method Get values. Exact raw selector, genuine global class/member/body/flags and emitted CODE.NAMES identity precede unchanged owner/scope/cache/birth and consumer proofs. Shared method statics, result/receiver retirement, receiver throw and budget resumptions retain their existing rules. Relative/dynamic/alias selectors, wider declaring classes, inherited methods, wrappers and This/private-cache/Generator or lifetime modes remain partial. [Review](../../coverage/semantics/magic-property-methodclosure-static-named-selector-quiet-get-review.json).

Raw NScalarString class selectors also cross the existing quiet CV ??, private ??= and literal/CV Empty consumers of method Closure values on the bounded own and inherited ordinary classes. The actual capture child at PCFIELD 0 must match the scalar source and identical decoded compiled PSTRING bytes before removing one optional leading backslash and looking up the genuine global requested class. Namespace/import aliases do not select literal targets. Missing/type reads and case/backslash variants in the pool remain refused even when the generic scoped helper accepts them. Existing direct name helpers, complete member authority, lexical/called/cache scope, Shared birth/history and separate result/receiver cleanup remain unchanged; CV/computed/keyword selectors and wider concat forms stay partial. [Review](../../coverage/semantics/magic-property-methodclosure-static-literal-selector-quiet-get-review.json).

Quoted NScalarString method names also authenticate the existing own/inherited public static USER method Closure Get values. The actual PCFIELD 1 scalar and identical decoded compiled PSTRING bytes precede casefold comparison; method names retain leading backslashes. The old NIdentifier equality and current direct/literal class helpers remain unchanged. Separate name-read counterfacts preserve class/requested/source-name proofs while the new helper refuses them; Shared ancestry, owner versus called scope, static roots, result/receiver cleanup, throw and resumptions retain their rules. CV/computed names and wider concat forms stay partial. [Review](../../coverage/semantics/magic-property-methodclosure-static-literal-method-selector-quiet-get-review.json).

A flat NExprBinaryOpConcat of exactly two raw NScalarString method-name operands also authenticates these own/inherited static USER method Closure Get values. The actual PCFIELD 1 root and both scalar child occurrences must match, and its compiled ROOT PSTRING must equal decoded-left++decoded-right exactly before casefold comparison. Folded child pools may be absent; method names receive no class/function slash normalization. Direct/literal class proof, complete members, lexical/called/cache scope, Shared ancestry, method-static roots and result/receiver cleanup, throw and resumptions retain their rules. Nested/numeric/CV/computed operands and wider forms remain partial. [Review](../../coverage/semantics/magic-property-methodclosure-static-literal-concat-method-selector-quiet-get-review.json).

A flat NExprBinaryOpConcat of exactly two raw NScalarString class operands now composes with the existing literal method-name concatenations for these own/inherited static USER method Closure Get values. The actual PCFIELD 0 root and both scalar child occurrences must match, and the compiled ROOT PSTRING must equal decoded-left++decoded-right exactly before one optional leading class backslash is removed, case is folded and class_named authenticates the requested global class. Folded child pools may be absent. Namespace/import aliases do not choose literal targets; method normalization, complete members, lexical/called/cache scope, Shared ancestry, static roots and result/receiver cleanup, throw and resumptions retain their rules. Nested/numeric/CV/computed/keyword selectors and wider forms remain partial. [Review](../../coverage/semantics/magic-property-methodclosure-static-literal-concat-class-selector-quiet-get-review.json).

Selected inherited private writes now call a public nonstatic, nonref
`__set(string $name, $incoming): void`, with a required untyped value parameter.
The source receiver is an external CV, the property name is literal, and the RHS
is initially a nonreference integer CV or integer literal. The setter's lexical
private write and the caller's initialized public write use ordinary storage.
The callback receives the original integer; a receiver-owning result marker keeps
the object through the call even when the caller CV becomes null. IN_SET ends
with that call, before receiver destruction. A nonowning delivery marker then
reads the captured RHS cell after release, allowing ordinary global binding to
promote it to a reference. Thus callback `99` followed by destructor `123` yields
`123` for a used CV assignment, literal `7` stays `7`, and a held receiver yields
`99` before its later destruction. A setter throw cancels outer assignment and
keeps the same Exception through receiver cleanup and actual catch binding.
Four originals and 524 focused premises (506 reached +18 derived) verify these
transitions, actual typed parameter reception, saved delivery after receiver
retirement, pointer/input/source refusals and driver budgets. The reached module318
check covers the default-handler bypass, without a handler-enabled suppression
claim. Two original source failures, the first focused failure and two diagnostics
retain zero credit. Other setter signatures, owning/initial-reference RHSs,
indirect or recursive writes and wider receiver/lifetime forms remain open;
generic ownership, destruction and GC rules are unchanged.

These admitted setter, terminal-isset and unset bodies may create source-owned
anonymous classes, including anonymous declaring owners and admitted deferred
factory bodies. Method headers, actual saved result markers and receiver scopes
retain their existing authority. Child ownership remains independent of the
receiver; scalar setter delivery still reads the captured RHS cell after receiver
release. The [factory review](../../coverage/semantics/anonymous-property-magic-factories-review.json)
separates original execution and genuine callback/delivery/budget checks from
explicit source/runtime boundaries. No consumer dispatch or ownership layout is
widened; Trait declaration, wider header/receiver and owning-RHS limits remain.
[Magic setter review](../../coverage/semantics/magic-setter-review.json).

Selected CV/literal inherited-private `??=` composes the existing typed-bool
`__isset(string)`, absent-return by-value `__get($name)` and
`__set(string $name, $incoming): void` sources. One read marker retains the
receiver through Isset/Get, then releases that hold before a named no-argument,
nonreference integer-returning RHS executes. The node-free decision retains
source/caller/line history without retaining or requiring the old receiver.
The later write re-fetches the CV: a replacement gets the returned `7`, while
current NULL raises Error after RHS effects. Get zero suppresses RHS and Set.
The setter receives a cached temporary `7`; changing an unrelated global to
`99` does not change expression delivery. A supplied Set Exception retires its
receiver before the same catch and preserves destination `42`.

[Four originals and 746 focused premises](../../coverage/semantics/magic-coalesce-assignment-review.json)
check actual receiver retirement, root-free continuation, fresh Set reception,
entered/saved call validity after CV nulling, cached zero disposal, both errors,
compiled-name/source refusals and PREP budget resumption. The earlier four
typed-Get-name sources retain their declaration Unsupported observations; four
fresh untyped-name variants isolate the genuine quiet-consumer gap. Existing
declarations, inheritance, ordinary `??` and assignment machinery are reused;
their earlier campaigns are not renewed. Reference/owning RHS values, no-Get or
untyped-Isset variants, Get/RHS throws, wider receiver/property forms and reentry
remain partial. No generic ownership, destruction, WeakMap or GC rule changes.

Selected main-CV/literal inherited-private integer `+=` now composes the existing
by-value `__get($name)` and `__set(string $name, $incoming): void` signatures.
A named no-argument, nonreference integer-returning RHS runs before receiver
lookup. Once selected, a separate outer hold keeps that object through Get,
addition and Set; clearing its CV in Get does not redirect Set. Each handler
retains its own inner hold. Raw PINT operands and an in-range integer sum are
required. The used result caches `7` before receiver destruction changes the
live global to `99`; supplied Get/Set throws skip the outer store and preserve
the same Exception and destination `42`.

[Four source agreements and 891 premises (870 reached + 21 derived)](../../coverage/semantics/magic-property-addassign-review.json)
check post-RHS selection, actual handler receives, saved caller authority after
CV nulling, separate holds, cleanup receipts, source refusals and PREP budgets.
The read descriptor has DECL absent because the inherited private storage key is
mangled; a separate physical property origin authenticates the Set continuation.
Existing Get verification remains unchanged. A native `'5tail'` Get result
warns then stores `7`; the model refuses that out-of-slice raw kind before
Warning/Set, with zero agreement. Original admission/fixture/driver failures and
two localization diagnostics retain zero credit. Wider receivers/names, RHSs,
coercions, overflow, references, hooks and reentry remain partial. Declaration,
inheritance, ordinary arithmetic, generic cleanup and GC rules are unchanged.

Selected main-scope CV/literal inherited-private integer pre/post updates now
compose the existing Get/Set handlers. UPDATE_PREP captures the selected object;
a separate outer hold survives Get clearing or retargeting its CV, and each
handler keeps its own inner hold. Immutable OLD/NEW integers select the postfix
old value or prefix new value before outer receiver destruction. The read's DECL
remains absent; the separate physical property origin authenticates Set.

[Four originals and 821 focused premises (798 reached + 23 derived)](../../coverage/semantics/magic-property-incdec-review.json)
cover normal post++/pre--, pre++ Set committing `6` then throwing with destination `42`,
and post-- Get throwing before arithmetic/Set. Actual receives, stable release
fronts, cached result/destructor effects, same-error catches, source/range refusals
and budgets pass. One pre-application fixture binding failure retains zero credit.
Raw PINT and in-range +/-1 are required; wider coercions, overflow, references,
hooks, access variants and reentry remain partial. Generic numeric, handler,
ownership and GC rules are unchanged; earlier 115/390 campaigns are not renewed.

Constructor promotion declares a property from its original parameter flags and
source occurrence. A parameter default does not initialize the property, and
promoted nonnullable types do not acquire ordinary implicit nullable widening.
All argument receives finish before promotion writes run in parameter order,
reading each current parameter cell. Value writes preserve ordinary copy behavior;
reference writes alias that cell and attach the property’s ordered type source.
Explicit constructor re-entry, inherited private slots and trait aliases use the
same declaration scope and readonly checks. The original body remains unchanged.
A promoted WeakReference property owns the wrapper while its target remains weak.
[The promotion review](../../coverage/semantics/constructor-promotion-review.json)
records nine exact sources, genuine Weak/byref steps and preserved failures.
One zero-argument builtin `#[Override]` on a promoted property resolves through
its real namespace/import context. It requires an exact-name nonprivate parent
property after ordinary inheritance compatibility. Simple root declarations fail
during compilation, including unreachable declarations; trait checks defer until
the using class links. Compatible trait collisions retain the effective property's
own source obligation. A failed check rolls back class publication. The
[Override review](../../coverage/semantics/promoted-override-review.json) records
thirteen source agreements, a separate user-attribute Unsupported control and 110
genuine certificate/write/rollback assertions.
A single builtin `#[SensitiveParameter]` on a promoted constructor parameter
belongs to the parameter target. It creates no property Override obligation;
ordinary value/reference writes precede the body, while later trace capture reads
the live CV. Queued promotions retain the authentic head and each task's source
suffix. The [Sensitive promotion review](../../coverage/semantics/sensitive-promotion-review.json)
records eight source agreements and separate source/property/wrapper controls.
Other parameter attributes/hooks remain explicit Unsupported.

Object `foreach` by value uses a live slot cursor, so later writes can affect
later iterations. Dynamic deletion leaves a cursor tombstone; reinsertion
appends a new slot. Array casts expose initialized properties. Loose comparison
uses declared offsets until a property table materializes, then compares live
table entries, including uninitialized declared slots. The object heap owns
property values and their nested arrays or objects across copies, calls and
abrupt cleanup. Paused tasks authenticate the property source occurrence and
line without reconstructing captured receiver values.

Literal undefined reads from ordinary instances and `stdClass` now resume
warning handlers with fixed null, preserving handler writes and throws. Ordinary
CV and `$this` receivers remain borrowed and may retire inside the handler;
temporary receivers retain their actual object owner until the read completes.
Unvisited, explicitly unset untyped declarations during ordinary instance
cleanup support quiet null and the same warning continuation through the
authenticated physical storage carrier. Consumed slots remain refused.

When a handler returns false, default reporting precedes return/selected-target
cleanup and raw-handler restoration. The
[undefined-property review](../../coverage/semantics/undefined-property-review.json)
keeps native/source and reached-state cuts separate. Computed names, hooks and
wider receiver forms remain required.

At PHP8.5, a literal named nonbuiltin reference-return call without name fallback,
with no arguments, one ordinary CV supplied positionally or by name, two
positional ordinary CVs, two CVs with distinct named labels, or a positional CV
followed by one named CV, keeps its returned
reference cell through callee leave. Module377 now
captures that actual cell before PROPERTY_PREP, borrows the live ordinary
instance/stdClass target and keeps the warning result null even when handler
rebinding retires that target. FETCH cleanup through270 releases the read's
returned cell owner; other aliases can keep that cell and its replacement alive.
Cell and source checks are disjoint
from the existing CV/temporary lanes; duplicate current or saved carriers are
refused. [The reference-receiver review](../../coverage/semantics/reference-property-receiver-review.json)
records exact native/source cases, reached ownership controls and the pinned8.5
engine distinction from8.6. Accepted99/79 are unchanged; wider call forms,
computed receivers and already-freeing targets remain required.
The one-CV certificate uses compiled source metadata, so callee cleanup or the
handler can unset the argument. A by-value parameter's last-owner destruction
may rebind the returned cell before lookup; a by-reference parameter may share
that same cell. The fixed warning result and existing270 cleanup remain unchanged.
For named sends, compile-known targets use the CV diagnostic line; deferred
targets use the emitted SEND line while retaining the documentary CV operand.
Module377 authenticates the literal property parent, selected reference-return
target and actual named task before capturing that deferred warning. Handler
mutation still sends fixed null, and unknown labels fail before CV demand.
Named default cleanup may replace the receiver during callee leave, so lookup
captures the returned cell's current object without rereading the argument.
For two positional CVs,377 separately authenticates both source/SEND occurrences
without widening361's ECHO certificate. A first argument Warning sends fixed
null; its handler may change or unset the second CV before the later SEND.
Deferred SEND2 preserves the already-captured prefix and documentary CV INPUT,
but reports its actual compiled line. Both last-owned parameter callbacks may
replace the returned cell during leave before property lookup. Prefix cleanup
after an argument throw and wrapper cleanup after a property throw preserve
exception chaining. Core-only companions replace the ordinary `is_null`
observers in the positive comparison set; original bytes and builtin boundaries
remain recorded separately.
Two distinct named CVs use a separate local certificate without restricting label
order. SENDs read CVs in source order; named binding puts each captured operand in
its formal slot. Known sends use individual CV lines, while both deferred
ordinals use the emitted argument-list line and preserve documentary INPUT and
already-sent slots. Skipped defaults and parameter destruction follow formal
order, so lookup captures the cell after all callee-leave callbacks. Unknown and
duplicate labels fail before that CV's demand. Captured prefix release can leave
a caller-local owner whose later frame unwind runs its destructor; the pending
label Error remains protected and may become a cleanup exception's previous.
A positional CV followed by a named CV uses the same actual named-task protocol.
Its first Warning fixes null in formal slot0; the later named CV is read after
handler effects and can bind around a skipped default. The first SEND retains
its equal documentary line, while a deferred named SEND uses the compiled
argument-list line without changing INPUT or the captured prefix. Unknown and
duplicate destinations still fail before CV demand; buffer release and later
caller-local frame cleanup keep their distinct owners and pending Error.
More than two arguments, unpacked or computed actuals and dynamic callees
remain outside this bounded lane.

Normal direct-CV reads with a plain/interned non-NUL string-CV name also enter the
existing nonref magic getter. Entry checks the real emitted VARIABLE and plain
value; later source/history validation uses captured NAME/DECL and method/source
facts rather than rereading the changed name CV. The new completion gate accepts
only a known integer with no property conversion, keeping wider results and
typed coercions Unsupported. The existing RESULT receipt owns one receiver while
getter/helper contexts borrow it. Removing the global receiver during the helper
therefore preserves the selected private name and slot through throw, destruction
before catch and fresh retry. Private magic SET uses the real assignment/CV source
and the same entry-only name check, retaining its existing descriptor, method,
signature, body, caller-scope and integer literal/direct-CV RHS limits. Captured
method input and transformed private storage stay distinct; used CV RHS delivery
still follows the established late-read rule. This normal assignment route adds
no RHS-function, This, factory, reference, compound-update or owned-name family.
[Magic CV name review](../../coverage/semantics/string-cv-magic-properties-review.json).

The same plain/interned non-NUL string-CV name producer now enters existing
terminal `isset`, paired `empty` and `??` magic consumers through a separate
PROPERTY_NAME quiet role. Only entry reads the live emitted name operand. The
real quiet receipt authenticates NAME, property, receiver, caller and source
through the `__isset` to GET handoff; it remains valid after the live name changes
or the global receiver disappears. The RESULT task retains its one receiver and
the handler context borrows it. New CV callbacks accept booleans for `__isset`
and known integers for GET; other results are Unsupported. False `__isset`
retains its synthetic null/no-GET path. That terminal typed witness uses a no-GET
class; paired handlers retain their existing source/signature gates.
Conditional `??=` retains real pending receiver/name VARIABLE operands and the
existing named no-argument by-value integer RHS. After RHS effects it selects the
current target/name again, producing ordinary storage or actual private `__set`
without a synthetic assignment. Once SET enters, its captured NAME and formal
argument stay fixed. RHS/SET throws preserve the outer result; no general backing
rollback is claimed. Normal assignment RHS, This/factory/reference and wider
name/result/body/producer families are unchanged.
[Quiet magic CV name review](../../coverage/semantics/string-cv-magic-quiet-review.json).

Direct-CV magic `__unset` also accepts the existing plain/interned non-NUL string-CV
name producer for an ordinary private descriptor. A disjoint source arm proves the
real UNSET statement child and canonical absence of hooks. Its pending plan keeps
the actual VARIABLE name and authenticated source base, then uses existing PPUNSET
resolution. Only initial capture compares the live name with receipt NAME;
entered/frame/result history stays structural after the handler mutates the name
or removes the global receiver. The existing RESULT receipt owns one receiver
while handler/helper contexts borrow it. Successful callbacks do not implicitly
delete the private slot: only the executed method body changes storage. With no
other references, removing the global receiver leaves only the receipt, which
throw retires before catch.
The literal site/private route and existing public history stay unchanged; the
public CV storage-state extension is described below. Existing void method,
private descriptor, signature, body and caller-scope bounds remain authoritative.
No hook/reset/indirect/This/factory/reference/type/storage/root rule is added.
[Magic unset CV name review](../../coverage/semantics/string-cv-magic-unset-review.json).

Public integer CV-name unset also composes with the existing storage-state rule.
A narrow ordinary-clear certificate proves the actual UNSET/CV pending base and
line, plain selected name/receiver through PPUNSET, admitted public descriptor and
void target, canonical no-hook key and an actual INITIAL or VALUE slot. It excludes
active same-name guards and partitions only the first broad unknown-name pending
arm, allowing unchanged ordinary storage clearing. An already-UNSET slot stays
pending and uses the existing magic receipt/capture path. Capture requires UNSET
only on entry; entered public history remains valid after the method repopulates
VALUE9 and changes the live name. The existing receipt holds one receiver while
method/helper contexts borrow it, including binding removal/throw and fresh retry.
Literal/private routes and the preexisting literal guarded arm remain pointwise;
no method/body/type/header, result, storage, unwind or root rule was added by that
state slice. Only the unchanged public-desc declaration moves earlier inside406.
[Public CV unset state review](../../coverage/semantics/public-cv-magic-unset-state-review.json).

The public integer CV unset state law also applies under the active same-object,
same-name __unset guard. An authentic VALUE slot still uses ordinary clearing;
only an already-UNSET slot takes the disjoint CV guarded plan and existing no-op.
That plan proves the actual VARIABLE selector/source and PPUNSET resolution,
public integer descriptor/canonical no-hook key, void method, capture and scope.
The normal callback plan keeps its negative guard. No second callback or receipt
is created: the outer receipt still owns one receiver, contexts borrow it, and an
ordinary helper CV may hold its separate owner. Alias removal and helper throw
retire the outer receipt before catch; fresh retry preserves the state order.
New native evidence uses reachable active VALUE and UNSET only. Inactive INITIAL
keeps its earlier evidence, with no active-INITIAL claim. Wider recursive and
producer forms remain separate; no method/body/header/type, task, storage or root
formula changes are added.
[Recursive CV unset review](../../coverage/semantics/public-cv-magic-unset-recursion-review.json).

An active recursive CV-name unset of an inaccessible ordinary private integer
property instead reaches the existing visibility Error. A separate guarded plan
requires actual PROPERTY_DENIED, private TYPE=int, real CV/name/PPUNSET source,
canonical no-hook descriptor and the existing void method/capture/scope proof.
The positive same-object/name guard suppresses another call, then the ordinary
access-error helper uses the original borrowed-base state and actual inner line.
The step consumes that UNSET without creating an inner receipt or deleting the
private slot. At the witnessed helper state, its local CV and the outer receipt
own the receiver independently, while contexts borrow it. The inner Error can be
caught before helper alias removal/outer throw; receiver retirement precedes the
outer catch and a fresh object can retry. Existing public no-op/clear, literal
and normal callback negative-guard paths remain unchanged; no body/header/type,
producer, task, storage or root-formula expansion is added.
[Private recursive unset review](../../coverage/semantics/private-cv-magic-unset-recursion-review.json).

A main-scope direct-CV/literal-name append assignment can also consume an existing
nonref magic getter for an ordinary private integer property. Its actual source,
raw descriptor and method authenticate the writable entry; the RHS is a literal
integer. On a known integer return, guarded GET RESULT transfers its one receiver
hold to the existing guard-free BASE while COPY retains the scalar. The Notice
uses the actual property site and line. Its handler can reenter ordinary GET
with IN_GET clear and remove the last caller alias without retiring the receiver.
After the handler, COPY restores and verifies the saved integer; BASE releases
the receiver before DIM_CAPTURE and the original append continuation reach the
ordinary scalar-container Error. A handler throw instead unwinds that hold before
catch, preserving the prior outer result. Existing untyped getter signatures,
normal/quiet GET routes, tasks, storage and root formulas stay unchanged. Other
indirect sources and returned reference/array/object values remain separate.
[Indirect magic getter review](../../coverage/semantics/indirect-magic-get-append-review.json).

The existing main-scope private integer magic `+=` family also admits plain CV
names through a disjoint real PLUS source and pending VARIABLE-name plan. Existing
PPRW resolution selects receiver and name after the named no-argument integer RHS.
The selected GET receipt then fixes both through GET-time rebinding; SET receives
the computed sum and the expression keeps that sum even if the setter transforms
storage. Entered/source history never rereads current selectors. The existing
outer operation hold and GET/SET receipt hold remain independent; method contexts
borrow them. A local setter RHS helper before the backing target is captured
therefore has exactly those two holds, with no pending property-base pin. The new
CV domain also excludes hooks by the actual canonical descriptor key, while
literal source/plan and prior private/int/nonref/method/body/range laws remain
pointwise. No normal-assignment RHS, getter conversion, operator, source-node,
class-header, storage, cleanup or root rule is added.
[Magic compound CV name review](../../coverage/semantics/string-cv-magic-addassign-review.json).

Main-scope private integer magic pre/post updates also admit the same CV-name
producer through a disjoint source proof of the actual update kind and postfix
flag. The pending UPDATE_PREP plan authenticates the emitted VARIABLE name and
uses existing PPRW selection; entered history retains its selected object/name
without rereading mutated CVs. OLD/NEW and prefix/postfix result selection stay
on the existing update receipts: prefix returns NEW, postfix returns OLD, while
SET receives NEW and may transform the store. The outer update and active handler
retain separate receiver holds; contexts borrow them. A local setter RHS helper
before its property target is captured has those two holds. Canonical no-hook
checking is new-CV only behind a literal-true fence. Literal/main/private/raw-int,
nonref/method/body/range, SET source/capture, cleanup and root rules remain
pointwise; no RHS, getter conversion, operator or producer family is added.
[Magic update CV name review](../../coverage/semantics/string-cv-magic-incdec-review.json).

Terminal `isset` also composes the existing typed-bool `__isset` producer with a
present same-owner admitted getter. Its new terminal-only certificate authenticates
the real `__isset` source/target, getter source/target and canonical private key's
absence of hooks. The operation invokes only `__isset` and retains its bool;
getter presence does not introduce a GET call. Literal terminal preparation
defers ordinary read interception for this certificate, while the existing CV
PROPERTY_NAME quiet role is unchanged. Empty remains on its separate dispatch,
and old untyped/noGET paths pass pointwise. The result receipt owns one receiver
while callback/helper contexts borrow it; selected NAME remains valid after live
name changes or receiver binding removal, through throw and fresh retry. Only an
unchanged getter-source declaration moves from408 to407 before use; its body and
all result/RV/typing, storage, unwind and root rules stay unchanged. No wider
getter/signature/body/result family is added, and the historical78 off-domain
draft keeps its original zero credit without replay.
[Terminal bool pair review](../../coverage/semantics/terminal-typed-isset-pair-review.json).

Literal ordinary CV-base reads now invoke public nonstatic `__get` with one
untyped required parameter and no declared return type. The first family covers
ordinary instances, literal names and missing or publicly accessible UNSET
properties. Denied private/protected reads and ancestor-private literal fallback
also invoke the getter, with no hidden property type verification,
even for INITIAL or initialized typed backing. Allowed lexical VALUE reads the
physical key; accessible typed INITIAL raises Error without invoking the getter.
Wider lexically accessible nonpublic UNSET, changed Closure scopes for nonpublic access, writes, quiet probes,
wider signatures and recursion beyond the bounded cases below
remain explicit Unsupported.

For CV receivers, module380 owns one hold while the known-instance getter frame borrows
it. The raw returned value or reference survives any captured property verification
and receiver release. Only afterward does read reception copy the reference cell's
current payload, so receiver destruction can change that result; a value return
keeps its original payload. Discarded reads still retain the getter RV through
receiver release. Public UNSET type verification uses the getter's strictness and
performs no backing-slot write or type-source attachment. An actual mismatch
raises the declaring property's TypeError before receiver cleanup; later cell
repair cannot remove it, and a successful check is not repeated after cleanup.
Coercions and returned-reference constraints beyond the bounded cases below remain
Unsupported.

Getter throws release the receiver under the pending exception. If receiver
cleanup throws after a normal return, the raw reference is materialized and its
payload released under that exception, preserving a later cleanup exception's
previous link. Current/saved carrier checks reject missing or duplicate holds;
entered continuations never reread the caller CV or property absence. The
nonpublic path authenticates the ordinary caller scope from its source site
before entry and retains that lookup history through privileged getter and
destructor contexts.

Same-name implicit recursion on an absent undeclared literal property now uses
the ordinary undefined-property Warning and captured NULL. The actual by-value
getter frame retains the guard through compiled-local destruction; explicit
`__get` calls, queued RESULT and returned COPY markers do not supply authority.
Handler population cannot redirect the interrupted NULL, and clearing the caller
CV leaves the getter's receiver hold intact. A supplied throw releases that hold
before catch and preserves the untouched outer assignment. Later access enters
the getter again after guard reset. Four source agreements and 868 focused
premises retain separate runtime and fixture cuts in the
[recursion review](../../coverage/semantics/magic-get-recursion-review.json).
Declared public untyped UNSET properties now also use that Warning/NULL path.
Their immutable descriptor remains valid after handler population; the original
DECL identity and physical key survive the interrupted read and local cleanup.
[Four new source agreements and 542 focused premises](../../coverage/semantics/magic-get-unset-recursion-review.json)
retain separate source and state cuts. Sole-owner clearing and supplied throw
have new source evidence; population and local cleanup also have reached proofs.
Those typed-UNSET and denied-private Warning refusals retain their original
cuts; typed INITIAL remains a separate existing agreement.

Public typed UNSET reentry now raises a fresh Error under the same actual Get
guard, including compiled-local cleanup. The message names the declaring class,
and the file/line identify the inner read. Caller-CV clearing releases the receiver
before catch without overwriting the outer assignment; a destructor's supplied
Exception retains that Error as Previous. A nullable slot populated with NULL is
read normally under the still-active guard, and a later unset starts a new Get.
[Four source agreements and 496 focused premises](../../coverage/semantics/magic-get-recursive-error-review.json)
retain separate runtime and state cuts. Recovery, replacement and local cleanup
have reached proofs; inherited propagation has source-only evidence. The typed
private source control stops at class compilation, and its descriptor mutation
has selector-only refusal credit. Those earlier controls retain their own cuts.

Denied private/protected reentry now raises the ordinary visibility Error under
the actual Get guard, including during local cleanup. Its message names the
receiver class; the inner read supplies file/line and ordinary lexical scope.
Hidden untyped VALUE, typed UNSET and typed INITIAL storage all preserve this
priority. Local recovery can return an incompatible hidden-type value (`'ok'`)
without verification. Allowed protected scope reads the mangled backing key,
and another object enters its own Get. [Three source agreements and 405 focused
premises](../../coverage/semantics/magic-get-denied-recursion-review.json) retain
separate cuts; private VALUE propagation has source and an independent reached
cut, while recovery/local cleanup have full author trajectories. The original
plain-string fixture assumption and its carrier diagnostic retain zero credit.
The earlier class-level comment Nop remains a compiler residual; these multiline
witnesses do not expand that compiler route. Wider scoped access and lifetime
combinations remain partial.

Ordinary local-CV reads of accessible private/protected UNSET now retain the
caller's selected canonical declaration. Parent's private int wins over a
same-name Child private string during Parent's read, even while Get runs in
Child scope. Weak `'7'` becomes int7 internally; the same object's external denied
Get still returns raw string `'7'`, and Child backing remains unchanged.
An incompatible RV raises the declaring Parent's TypeError at the caller read
site after the Get guard clears. Untyped protected Get can populate backing99
without redirecting its interrupted `'ok'` return; history never rechecks UNSET.
[Three source agreements and 330 focused premises](../../coverage/semantics/magic-get-scoped-unset-review.json)
retain separate runtime/state cuts. Real caller frames, selected DECL, normal
COPY release and caller-line rejection are reached; saved control projections
and forged DECL/BYREF controls are derived. Raw-key public/denied behavior keeps
its separate bounds. Wider reference getters, owned receivers, special coercions,
scoped recursive-inner Errors,
bound-Closure scopes, quiet probes and wider lifetimes remain partial.

Literal `$this` now enters bounded by-value Get through the existing323 source
certificate and the actual current receiver. Pending capture rebuilds KNOWN;
source and selected DECL remain valid after Get/callback entry. The transient
receiver root becomes the Get hold without an extra BASE owner. A global handler
with no `$this` preserves captured NULL after live9, while an ordinary read method
retains its receiver after Get clears the sole global CV and releases its hold.
[Four source agreements and 488 focused premises](../../coverage/semantics/magic-get-direct-this-review.json)
retain414 cuts; INITIAL is a separate existing control. The original false and
shared diagnostic retain zero credit. Warning continuation validity is checked
at its saved emitter, while Get source/history remains valid in the handler.

Caller-source resolution now precedes the effective-public shortcut across the
existing CV, literal-this and effective-public owned-factory producers. Parent's
private int therefore governs Get even when Child has an initialized public
string of the same name. This fixes a genuine normal wrong-result case: the owned
factory returned raw string7 instead of converted int7. Verification still
precedes original-receiver D and caller reception. Fresh actual access must agree
with saved-source access; different scope classes may select the same public key.
[Three source agreements and 413 focused conditions](../../coverage/semantics/magic-get-lexical-selection-review.json)
retain415 cuts. INITIAL/public fallback are existing controls; the first runtime
nondeterminism and peer pre-main binder failure retain zero credit. Raw and
scoped verification are disjoint by retained DECL; wider scoped coercions and
owned producers remain partial.

The same named noarg owned-factory producer now also admits by-value Get for
accessible private/protected UNSET and denied hidden properties. The owned gate
retains immutable access/signature facts instead of rechecking absence after a
callback. Selected private int verification converts `'7'` before COPY and receiver
D; a protected Get can populate backing99 while returning captured `'ok'`. Denied
private int INITIAL keeps DECL absent and returns raw `'ok'` without consulting the
hidden type. Both receiver holds remain distinct: getter release precedes COPY,
then BASE retires the original temporary before caller reception.
[Three source agreements and 477 focused conditions](../../coverage/semantics/magic-get-owned-access-review.json)
retain separate415 cuts. Existing public BYREF still detaches7 before receiver D
changes its source cell to9; accessible INITIAL bypasses Get. Wider producers and
special coercions remain partial; owned references have separate coverage below.

Ordinary CV reads now also admit by-reference Get for accessible nonpublic UNSET
properties. Plain and constrained-reference verification share the saved physical
declaration, so Parent private int still wins over Child public string after Get
runs in Child scope. An unconstrained returned cell changes from string7 to int7;
COPY then releases its wrapper owner. A held string-property source instead raises
the first-source conflict TypeError without writing the cell, at the original read
file/line. Exact int|string sources survive COPY and later accept `'free'`: the
requested Parent type never attaches to the referent.
[Three source agreements and 432 focused conditions](../../coverage/semantics/magic-get-scoped-reference-review.json)
retain416 cuts. Parameter backings, wider scoped coercions and lifetimes remain
partial; no new task, state or root machinery.

The existing named noarg owned-factory route now also admits reference Get for
nonpublic/public-shadow and denied access. It retains the same selected declaration
and access history while accepting either return convention. The reference stays
live through getter-local cleanup: a local destructor's string7-to9 write precedes
selected private-int verification of the actual cell. COPY then detaches int9 before
BASE releases the receiver and its destructor writes `'free'`. Exact constrained
sources keep their original vector; the requested type never attaches. A denied
hidden INITIAL/int slot keeps DECL absent and returns constrained string7 unchanged.

On a typed-source conflict, COPY captures raw7 under the pending TypeError before
receiver destruction. Its supplied replacement preserves the original caller-site
TypeError as Previous and leaves destination42 unchanged. A copied object payload
also survives receiver-time source clearing, then retires under pending H and
chains its supplied C to H. These are actual reference/COPY/destruction trajectories,
using existing RESULT/COPY/BASE/DROP rules.
[Five source agreements and 586 focused conditions](../../coverage/semantics/magic-get-owned-reference-review.json)
retain417 cuts; the original Unsupported3 and wrong-PHP-error2 baselines retain
zero agreement. Wider factories, PARAM sources and broader coercion/callback/
lifetime histories remain partial.

Literal `$this` now also admits reference Get through the same source certificate.
Actual current receiver identity still gates Plan/capture; immutable source/access/
DECL history survives Get entry and callbacks. Get adds no duplicate method receiver
or BASE owner: its result hold replaces the transient read root, while the ordinary
read-method RECEIVER remains owned through return or unwind.

A Get-local destructor changes the returned cell from string7 to9 before selected
Parent-int verification under a public Child-string shadow. COPY then detaches int9;
the enclosing method can clear its last global receiver alias and write `'free'`
while that receiver remains live. A real int|string source keeps its original type
vector through COPY and later writes. A string-source conflict leaves7 unchanged,
materializes the caller-line10/file TypeError, and captures raw7 into DROP before
ordinary method-frame retirement. Its destructor can replace that error while
preserving it as Previous, changing source8 and leaving destination42 unchanged.
[Three source agreements and 496 focused conditions](../../coverage/semantics/magic-get-this-reference-review.json)
retain419 cuts. Missing current receiver and forged DECL are derived admission
controls; the original Unsupported2/wrong-PHP-error1 baselines keep zero agreement.
No verification, COPY, frame, task, root or GC machinery changed; wider computed/
suspended producers, PARAM sources and coercion/lifetime histories remain partial.

Valid historical parameter-backing receipts now pass shared Get verification.
Weak BYREF Stringable reception can add a real Holder:object source during its
callback, then write the captured string7 without a second source check. That
nonowning receipt certifies the exact value and parameter declaration, independently
of the current function; it is not a persistent parameter-type constraint.

An exact string Get preserves the receipt/source vector, while a requested int
raises the real first-source conflict without writing either cell. A later ordinary
write still checks Holder's object type. Unsetting that instance slot removes only
the real source; the subsequent Get int conversion clears the receipt through the
existing checked write, and later `'free'` proves no requested-type attachment.
[Three source agreements and 511 focused conditions](../../coverage/semantics/magic-get-param-reference-review.json)
retain 419 cuts, including malformed value/line/duplicate-receipt controls. The two
fixture failures and one diagnostic keep zero credit. No producer, state, root,
receive, COPY or type-source mechanism changed. The shared unconstrained
numeric-string warning route also inherits valid-receipt admission and checked
writes; constrained special-path fences remain. Wider callbacks/coercions remain
partial.

Named noarg factories returning a receiver by reference now preserve the original
input cell through a distinct `PROPERTY_GET_INPUT` tail. Fresh admission checks
its actual reference/object value; immutable source/DECL history then survives
retargeting. This task owns the cell, while RESULT supplies Get's separate receiver
hold. COPY reads the live returned reference before retiring the input cell.

If Get clears the receiver cell, its last hold can run D after int7 verification;
D writes string9 before COPY, so the caller receives string9. A factory-local sole
cell instead keeps the receiver alive through COPY, preserving caller int7 while
D later writes string9. A constrained conflict keeps its original caller-site
TypeError through replacement H and captures the later source8 before pending
INPUT/DROP. Copied owning payloads survive input-time source clearing/H, then
retire with C.previous=H before the unchanged destination42 reaches catch.
[Four source agreements and 714 focused conditions](../../coverage/semantics/magic-get-receiver-cell-review.json)
retain 420 cuts. Missing/duplicate/address/line/release-kind controls are derived;
KNOWN-RV/COPY checks add no by-value Get source agreement. Existing verification,
reference sources, state fields and generic ownership/GC rules remain unchanged; wider
producer/coercion/lifetime combinations remain partial.

The [getter review](../../coverage/semantics/magic-property-get-review.json) records
eight exact source agreements, 1293 setup-inclusive reached premises and the
separate original failures. The
[denied-getter review](../../coverage/semantics/magic-property-denied-review.json)
separately records six exact sources and 1094 reached premises for lexical keys,
absent hidden type info, captured caller scope and reference/exception cleanup.

Literal BP_VAR_R also accepts an owned result from a statically named ordinary
noarg nonbuiltin/nofallback by-value nongenerator function, for public missing or
public UNSET properties. The original receiver temporary and standard getter
hold are separate owners; the getter context borrows. After verification and
getter-hold release, COPY detaches the payload and releases the raw return's cell
owner before BASE releases the original receiver. Surviving aliases can retain
the cell; its rebinding preserves the selected copied payload, which stays alive
through receiver cleanup. A replacement held only by the global cell can
retire during receiver destruction. Real surviving aliases suppress receiver destruction.
Abrupt BASE cleanup protects the copied value in GET_DROP under the pending
exception, with null read registers and genuine H/B/C previous links.
By-value and discarded getter results follow the same receiver-release order.
The [owned-getter review](../../coverage/semantics/magic-property-owned-review.json)
records seven source agreements and 1266 setup-inclusive reached premises at
distinct retained cuts. Named noarg by-reference factories have separate input-cell
coverage in the [receiver-cell review](../../coverage/semantics/magic-get-receiver-cell-review.json).
Wider factory/receiver forms remain partial; prior CV/denied evidence keeps its
original cuts.

Weak MAGIC_GET verification also accepts numeric strings parsed as an in-range
integer, using the getter declaration's strictness rather than the caller's.
An unconstrained reference return converts the actual cell and retains its
wrapper owner; a value return forwards the converted RV without changing the
caller's cell. Exact values require no write. Readonly backing remains UNSET,
and no property type source is attached, so repeated reads invoke the getter
and later ordinary cell writes remain valid. CV reception can copy a cell
changed during receiver destruction; owned reception detaches the converted
value before BASE release. A strict rejection retains the original raw return
and TypeError through later receiver cleanup.
The [integer-getter review](../../coverage/semantics/magic-property-integer-review.json)
records six source agreements and six whole reached groups/909 setup-inclusive
premises. Fractional/exponent strings parsed as NFLOAT, lossy or callback-based
conversions and wider returned-cell constraints remain Unsupported; earlier getter
evidence retains its distinct cuts.

Module384 admits actual returned reference cells with nonempty unique valid
typed-property sources for public UNSET builtin int/object targets. Exact
compatible verification leaves the whole state unchanged: no checked write or
getter target type source is added. A weak string parsed as a fitting integer is
tested purely to select the source/target incompatibility Error, even when its
source union accepts the converted int. The real cell stays unchanged. Strict
and nonnumeric rejection uses ordinary MAGIC_GET TypeError, and the first actual
source entry selects the conflict label. Receiver cleanup can later detach that
source and repair the cell while the original Error survives. Owned reception
releases the raw RV cell owner before BASE; surviving aliases can retain the cell
until their actual removal, while the copied payload stays alive.
The [reference-getter review](../../coverage/semantics/magic-property-reference-review.json)
records six source agreements and six whole reached groups/829 setup-inclusive
premises. PARAMETERBACKINGS, wider target types and possible conversions remain
Unsupported beyond the bounded cases below; existing receiver/consumer residuals
and prior evidence are unchanged.

Builtin float verification widens an original integer on an actual unconstrained
RV, including strict getter declarations. A reference updates its real cell and
retains the raw return's owner; a value return forwards only the converted RV.
The conversion uses the exact binary64 result, including rounding integers beyond
the exact range. Readonly backing stays UNSET with no getter type-source attachment.
CV reception copies the cell after receiver destruction; owned reception detaches
the converted value and releases the raw RV cell owner before BASE release.
Exact floats with real typed-property sources leave the whole state unchanged.
An integer instead raises the first-source conflict without converting the real
cell, even when its int|float source would accept that conversion and the getter
is strict. Later source detachment and repair retain the already-created Error.
The [float-getter review](../../coverage/semantics/magic-property-float-review.json)
records six source agreements and six whole reached groups/904 setup-inclusive
premises. At that cut numeric strings, booleans, PARAMETERBACKINGS and wider float
conversions remained Unsupported; prior getter evidence retains its separate cuts.

Weak builtin-float MAGIC_GET verification also accepts full numeric strings
classified NFLOAT or NINT, using the getter declaration's strictness. NINT casts
the parsed in-range integer to binary64, including ties-to-even rounding beyond
2^53 and positive zero for `-0`. The actual
unconstrained reference cell converts in place; a by-value return changes only
its RV. Repeated 7.5/0.1 reads preserve exact binary64 bits, UNSET readonly backing
and no getter type-source attachment. CV reception copies the referent after
reader destruction, while owned reception detaches before BASE destruction.
A real string|float property source instead selects a first-source conflict
without converting the string or changing its source. The original TypeError
survives later source detachment and repair. Leading-numeric `7.5tail` and a
strict getter under a weak caller reject before conversion.
The [numeric-string float review](../../coverage/semantics/magic-property-decimal-review.json)
records six source agreements and six whole reached groups/877 setup-inclusive
premises for NFLOAT strings. The separate
[integer-string float review](../../coverage/semantics/magic-property-integer-float-review.json)
records six source agreements and six whole reached groups/899 setup-inclusive
premises for NINT strings, including signed limits and strict-getter rejection.
PARAMETERBACKINGS and wider conversions remain Unsupported; earlier
evidence and failed preparations retain their original cuts.

Weak builtin-float MAGIC_GET also accepts booleans: false becomes positive zero
and true becomes one. The actual unconstrained reference cell converts in place;
a by-value return changes only its RV. Getter-declaration strictness rejects a
boolean, and null remains rejected. Real float|bool property sources select a
first-source conflict without converting the cell or changing its source; later
source repair preserves the pending TypeError. CV reception still copies after
reader destruction, while owned reception detaches before BASE release.
Getter rejection/conflict diagnostics name `bool`, as Zend's type-name helper
does; shared95's value names `false`/`true` remain unchanged in other contexts.
The [boolean-float review](../../coverage/semantics/magic-property-boolean-float-review.json)
records six source agreements and six whole reached groups/911 setup-inclusive
premises. Three maintained constructed boolean controls contribute nine clauses
only to the new kept group; phase31–33 evidence is not renewed.

Weak builtin-int MAGIC_GET also converts original false to zero and true to one
using the existing TYPEINTEGER marker. Actual unconstrained references update their
cell; by-value returns change only RV. Getter-declaration strictness and null reject.
Real int|bool sources conflict while preserving the raw bool/source, even though
the source accepts both types. CV reception copies after destruction; owned results
detach before BASE release, and later source repair preserves pending TypeError.
The [boolean-integer review](../../coverage/semantics/magic-property-boolean-integer-review.json)
records six source agreements and six whole reached groups/915 setup-inclusive
premises. Two maintained constructed controls contribute three kept and two conflict
clauses; earlier whole campaigns retain their cuts.

Weak builtin-string MAGIC_GET converts original false to interned empty and true to
ASCII `1` using existing TYPESTRING/echo semantics. Actual unconstrained references
update their cell; by-value returns change only RV. Getter-declaration strictness
and null reject. Real string|bool sources preserve a whole-state exact first read;
the later boolean conversion is diagnostic-only, preserving raw/source before
destructor repair. CV reception copies after destruction; owned results detach
before BASE release, and pending TypeError survives repair.
The [boolean-string review](../../coverage/semantics/magic-property-boolean-string-review.json)
records six source agreements and six whole reached groups/997 setup-inclusive
premises. At that phase36 cut the original concatenated-echo consumer is Unsupported:
its scratch BASE blocks getter entry. A comma-echo observation preserves native output;
only affected checks resume. PARAMETERBACKINGS and wider targets/conversions remain required.

Weak builtin-string MAGIC_GET also converts original integers through shared
stringify. Digits use interned strings; signed and limit values append one request
string and preserve its carrier through the actual unconstrained cell write.
By-value conversion changes only RV; exact re-verification is whole-state identity.
CV reception copies after destruction, while owned reception detaches before BASE
release. Genuine string|int sources preserve an exact first read and select the
later integer conflict without converting raw/source or allocating a request string.
Getter-declaration strictness and null reject; pending TypeError survives repair.
The [integer-string review](../../coverage/semantics/magic-property-integer-string-review.json)
records six source agreements and six whole reached groups/1,188 setup-inclusive
premises. Three maintained constructed clauses run only in the new kept group;
the original budget fixture failure and earlier cuts retain their credit.

Successful normal scalar EMIT now clears current-frame BASE together with RESULT after
output. Concat still publishes its result until consumption; saved frame/continuation
operands and real owners remain intact. Dynamic concat before a getter and inside its
body now permits later authentic getter entry, including a saved outer concat with a
delayed live CV read. Real source-conflict TypeError survives receiver detach/repair.
The [concat-consumer review](../../coverage/semantics/concat-emit-review.json) records
five exact originals and five whole reached groups/570 setup-inclusive premises.
Abrupt stringify and existing getter guards stay unchanged. The phase37 temporary
Stringable control keeps its frozen whole-source agreement0. Fresh
[direct ECHO ownership checks](../../coverage/semantics/stringable-echo-review.json)
repair named noarg NEW and borrowed CV pending-output timing without changing getters.

The compiler and runtime rules are in `135-property-compiler.watsup` and
`136-property-runtime.watsup`. [The review](../../coverage/semantics/properties-review.json)
binds source, compiler and paused-state checks. Public property references
and by-reference object traversal are documented separately in
[SOURCE-PROPERTY-REFERENCES.md](SOURCE-PROPERTY-REFERENCES.md). Protected/private access and
mangled storage keys are described in [SOURCE-PROPERTY-VISIBILITY.md](SOURCE-PROPERTY-VISIBILITY.md).
[Class static members](SOURCE-CLASS-STATICS.md) have a separate bounded storage
and access contract. Non-object casts and stdClass table sharing are described in
[OBJECT-CASTS.md](OBJECT-CASTS.md), including numeric/NUL storage keys, raw undefined
buckets and callback-sensitive iteration. Wider readonly operations, hooks,
other magic-setter forms and quiet access, and wider property consumers remain open.
Public constructors are implemented separately.

Weak builtin-string MAGIC_GET also converts non-NaN floats using shared stringify
and the current post-getter precision. Every conversion appends one request string,
including `7.0`, `+0.0`, `-0.0` and infinities; exact re-verification is identity.
Actual unconstrained references update their cell, while BYVAL changes only RV.
CV reception copies after destruction; owned reception detaches before BASE release.
Genuine string|float sources preserve an exact first read and select the later
non-NaN conflict without changing raw/source/STRINGDATA. Strict/null rejection and
pending TypeError survive cleanup. The
[float-string review](../../coverage/semantics/magic-property-float-string-review.json)
records seven source agreements and seven whole reached groups/1,351 premises,
including real getter precision14→6 and two maintained constructed clauses.
The original composite timeout keeps zero agreement after a source-only split.
At the phase40 cut, NaN warns even for constrained temporary conversion, so both routes
exclude it; its native-only control keeps zero model agreement. PARAMETERBACKINGS, Object/Stringable
and wider getter/conversion scope remain required; earlier cuts are not renewed.

Weak builtin-string MAGIC_GET NaN conversion now has an authenticated warning producer.
The request string is allocated before dispatch and retained across handler string-data
growth. Unconstrained REF commit overwrites a scalar callback change; BYVAL changes only
RV, preserving the global change. A genuine source-constrained result retains its initial
conflict decision and diagnoses the current referent after the callback, even if that
referent is now a compatible string. The getter receiver remains held through warning
and verification. A throwing handler still commits saved NAN before receiver cleanup;
a later cleanup exception keeps the warning exception as previous. Owned reception
detaches before BASE release, while declaration-strict rejection has no warning.
The [NaN-string review](../../coverage/semantics/magic-property-nan-string-review.json)
records six source agreements and six whole reached groups/1,014 premises, including
full state/budget/owner checks and malformed continuation controls. Shared stringify,
typed conversion and generic warning dispatch stay unchanged. Original observer and
preparation failures retain zero credit; phase40 cuts are frozen. Object/array callback
replacements, changed sources, PARAMETERBACKINGS and wider getter scope remain required.

Weak builtin-int MAGIC_GET also accepts original in-range floats. Integral values,
including negative zero, convert quietly; fractional values capture truncation
before deprecation dispatch. Normal return commits the saved int to an unconstrained
REF or BYVAL RV. Handler throws preserve the handler-changed scalar instead, with
no int write or second TypeError before genuine receiver cleanup. Real sources
retain the initial conflict decision and diagnose the live post-handler value.
The [float-integer review](../../coverage/semantics/magic-property-float-integer-review.json)
records six exact sources and seven whole reached groups/1,338 premises. Eight
maintained constructed clauses run only in the new kept/conflict groups. Integral 7,
negative zero and fractional 7.5 have native evidence; MIN/upper/nonfinite/invalid64
bounds are constructed controls. The original whole425 timeout remains0 after a
fixture-only split. Object/array callback replacements, changed sources/tails,
PARAMETERBACKINGS and wider receiver/conversion scope remain required. Shared
numeric/typed conversion and generic warning dispatch stay unchanged; phase41
evidence retains its original cuts.

Weak builtin-int MAGIC_GET also accepts original full NFLOAT numeric strings.
Quiet integral spellings, including `7.0`/`-0.0`, convert without warning. Lossy
strings retain their original bytes/carrier and captured truncation through the
deprecation handler. Normal REF completion overwrites a scalar/string mutation;
BYVAL changes only its RV, while a throwing handler preserves its mutation with
no int write before receiver cleanup. A real int|string source keeps the initial
conflict decision but diagnoses the handler-written current value. Owned reception
detaches before BASE release; strict and numeric-prefix rejection remain distinct.
The [numeric-string integer review](../../coverage/semantics/magic-property-numeric-string-integer-review.json)
records six source agreements and eleven source-driven checks/1,469 premises,
including compact dispatch, resume, quiet conversion and pending-error cleanup
stages. Four whole timeouts and one transient cleanup-validator fixture failure
remain0; unused diagnostic preparation adds no execution. Generic range clones
gain no fresh credit; fractional direct-helper verification remains Unsupported.
Scalar/string callback replacements and unchanged real sources/tails bound this producer;
object/array replacements, PARAMETERBACKINGS and wider getter scope remain required.
Shared numeric/typed conversion and generic warning dispatch stay unchanged;
phase42 evidence retains its original cuts.

Weak builtin-bool MAGIC_GET also converts original quiet scalar results. In-range
integers use nonzero truth; non-NaN floats include false signed zeros and true INF.
Strings use their complete bytes: `"0"` is false, `"0.0"`/nonnumeric strings are true.
Only the actual live unconstrained RV/cell is converted; ordinary and authenticated
carrier strings are accepted without numeric parsing or STRINGDATA allocation.
Genuine bool|string sources preserve exact bool reads and reject possible conversion
with the first-source diagnostic, leaving raw/source unchanged. Getter strictness
and user-property null rejection retain existing errors and receiver cleanup.
The [scalar-boolean review](../../coverage/semantics/magic-property-scalar-boolean-review.json)
records seven source agreements and seven whole groups/1,053 setup-inclusive premises,
including fixed values, aliases, full driver budgets, REF/BYVAL/owned reception,
pending errors and constructed actual-RV/carrier/PARAM/NaN/invalid-bit exclusions.
At phase44, one preparation-only failure stays0. The separate native NaN control observes
warning callbacks with zero model/state/agreement; no pre-warning captured bool is claimed.
Conversion targets beyond exact builtin-bool, PARAMETERBACKINGS and wider getter/coercion
domains remain required. Shared truth/type/owner rules and prior
phase43 evidence retain their original cuts.

Weak builtin-bool MAGIC_GET NaN conversion has an authenticated warning continuation
retaining original operand/getter roots and site/caller/tail/source authority. Normal
unconstrained REF reads only numeric raw payload after callback: LONG_MIN bits are
double negative zero/false, whereas int7 is true; float -0 also yields false.
BYVAL retains saved NaN true despite global int0. Constrained copied NaN keeps the
conflict decision and diagnoses current bool without writing. Handler throw also
skips the bool write; restored callback and cleanup45.previous warning45 remain real.
Owned COPY detaches before BASE retirement; CV receipt sees destructor mutation.
Declaration-strict rejection emits no warning and preserves its error through repair.
The [NaN-boolean review](../../coverage/semantics/magic-property-nan-boolean-review.json)
records source7/ten compact stages/1,014 premises with whole states, full budgets and
input/bits/range/site/owner/tail/PARAM controls at `a3f383502`. Original prep failure stays0.
Literal false and string0 replacement natives both yielded true in this pinned build;
normal unconstrained payload history remains Unsupported/native-only0. Throwing scalar/string
and constrained current-type paths do not decide that payload. Object/array replacements,
changed source/tail and wider targets/getters/PARAM remain required; prior44 cuts stay frozen.

Weak exact-string MAGIC_GET also converts ordinary Stringable results through the
real `__toString` callback. A local continuation retains the returned argument,
getter receiver and saved string. Cast-pin release precedes release of the original
argument or copied temporary owner, which precedes the string write. Destruction
at that last release observes the unchanged raw reference. Saved bytes still commit after a successful
cast's release exception, while callback failure performs no saved-string write.
A real source converts an independent temporary and diagnoses the current referent
without writing. Its new TypeError retains any pending original-object release
exception as previous. Existing getter cleanup then releases the receiver;
BYVAL remains independent, CV reception follows cleanup and owned reception detaches
before BASE release. Declaration-strict rejection invokes no cast.
The [Stringable-string review](../../coverage/semantics/magic-property-stringable-string-review.json)
records nine source agreements and twelve compact stage checks/899 premises,
including whole READY/COPY/commit states, physical owners, full budgets and malformed
input/site/tail/source/carrier exclusions. Original failures keep zero credit;
one pending-COPY diagnostic adds no agreement. Unconstrained inputs must retain
the captured referent through callback/precommit cleanup; object/array replacements,
changed sources/tails, PARAMETERBACKINGS and wider targets/getters remain required. Generic cast timing,
typed-CV release behavior and prior phase45 evidence retain their original cuts.

Own public untyped sole BYVAL GET hooks with omitted defaults and without same-field THIS access acquire same-name ordinary parent backing after the child’s existing slots. Exact raw header/name/type/origin and root plain-parent authority preserve child NULL, metadata order and physical cleanup. [Appended-slot review](../../coverage/semantics/ordinary-parent-unbacked-get-child-slot-review.json).

When the sole block or short BYVAL GET accesses that same field, its existing child slot instead keeps declaration order. Explicit17 and omittedNULL retain actual getter BODY/CODE/line and child identity through physical cleanup and shared owners. [Existing-slot review](../../coverage/semantics/ordinary-parent-backed-get-child-slot-review.json). Wider parents/types/BYREF and lifetimes remain partial; exact holds stay unchanged.

Own public untyped backed block &get hooks also retain their lexical child slot over a same-name ordinary root parent. Actual returned references, unconstrained aliases and real ALIAS-cell edges survive to physical cleanup without reusing the old parent slot. [Block reference-Get slot review](../../coverage/semantics/ordinary-parent-backed-reference-get-child-slot-review.json). Short reference Get, ordinary This-reference-fetch consumers and wider types/parents/lifetimes remain partial.

COMP318 admits all six raw `int|bool|null` orders for the bounded own public
parentless short reference Get, retaining actual defaults, exact tags, real
aliases, ordinary Boolean/NULL copies, weak coercion, strict rejection and quiet
type-source removal. Six original sources agree using saved native observations
once. Separate author438/443/443/444 and peer443/443/444/438 fixtures retain zero
source credit, as do the preserved prelaw and preparation failures. Actual
`7a7814153` and its sole production-SL508 load (16.938333122 s) are separate.
Wider headers, owners and lifetimes remain partial; all exact holds remain.
[Review](../../coverage/semantics/int-bool-null-parentless-short-reference-get-hook-review.json).

COMP319 admits every distinct ordered scalar-or-null union of length3..5 over
`int`, `float`, `bool`, `string` and `null` for that same short reference Get.
Exact raw/normalized order, complete Identifier proof, actual defaults, tags,
copies, aliases and quiet type-source removal remain required. Six originals
agree using native observations once. Eight separate fixture-SL cuts retain
source0: author1253/296/297/299 and peer1253/297/297/297. The initial native
expectation, pooled-array ownership and canonical-Identifier fixture failures
remain0; their narrow corrections do not renew accepted source/header checks.
Actual `eb5aa70f8` and the sole joined production-SL508 load (16.833466227 s)
are independently clear. Wider members, owners and lifetimes remain partial;
all exact holds remain.
[Review](../../coverage/semantics/scalar-union-parentless-short-reference-get-hook-review.json).


COMP320 admits distinct ordered builtin-or-null unions of length2..7 over
`array`, `object`, `int`, `float`, `bool`, `string` and `null` for that same
short reference Get. The local fold retains exact raw/normalized order,
casefolded Identifier proof and overlap rejection. Six originals agree using
native observations once, including nested array COW with shared references,
object identity, mixed payloads, coercion/refusal and quiet source detach.
Separate author and peer header1899/lifecycle253/281/284 fixtures retain source0;
the initial native diagnostic failure remains0. Actual `7a8a3916f` and the sole
joined production-SL508 load at `76639477f` (16.082620611 s) are independently
clear. Wider headers, owners and lifetimes remain partial; all exact holds remain.
[Review](../../coverage/semantics/builtin-union-parentless-short-reference-get-hook-review.json).

COMP321 extends that local fold with `true` and `false`, retaining duplicate
and Boolean-overlap rejection and forbidding both literals together. Existing
literal/null pairs use the same disjoint fold; raw/normalized order, source and
owner bounds remain. Six originals agree using native observations once,
including literal exactness, weak secondary conversion, strict rejection,
nested COW, shared object copies and quiet type-source removal. Separate author
header747/lifecycles271/272/293 and peer747/271/290/293 retain source0, with no
aggregate credit or replay of the earlier header1899. Prelaw Unsupported cuts
remain0; this slice had no failed execution cuts. Actual `0efbd08e6` and its sole
production-SL508 load (15.888344376 s) are independently clear. Wider headers,
owners and lifetimes remain partial; all exact holds remain.
[Review](../../coverage/semantics/literal-boolean-union-parentless-short-reference-get-hook-review.json).

COMP322 admits exact quiet fully qualified class singleton and nullable headers
for that same short reference Get. Raw class spelling matches normalized bytes
exactly; existing runtime matching remains case-insensitive. Whole-name `_`
warning handling remains outside this slice, while `Ns\_` stays admissible.
Six corrected originals agree using current native observations once, with real
`stdClass`/plain-user objects, case variations, copies, retargeting, refused writes
and quiet source detach. Separate author100/255/254/265 and peer100/255/265/264
fixtures retain source0. Original nested-writer Unsupported1/other5 unrun and
original native/prelaw versions stay distinct; corrected fixtures use supported
direct consumers. Actual `ff79f6b6c` and its sole production-SL508 load
(16.893319101 s) are independently clear. Plain/relative/imported names, raw
class-bearing unions, nested hook writers and wider values, owners and lifetimes
remain partial; all exact holds remain.
[Review](../../coverage/semantics/fully-qualified-class-parentless-short-reference-get-hook-review.json).

Ordinary and namespace-relative class singleton and nullable headers use the
declaring namespace/imports for that same parentless short reference Get.
Only quiet normalization to the exact class bytes or ordered class/null pair
is admitted. Runtime authority comes from the canonical source unit, actual
class origin/name/file/line and property origin/line; variable bindings and an
unchecked function environment supply no declaration context. Import prefixes
match without case sensitivity while the remaining class suffix keeps its
original bytes. Raw scope keywords, whole-name underscore, warningful headers,
class-bearing unions and wider owners/lifetimes remain partial.
[Review](../../coverage/semantics/scoped-class-parentless-short-reference-get-hook-review.json).

COMP323 retains six originals with native observations once: weak source3 and
final strict source3 keep their private508 identities and compatibility bridges.
Separate author273/284/285 and independent149/141/141/141 fixtures retain source0.
Original binding/parser/expected-observation failures and then-unrun cases stay0;
only affected fixtures were corrected. The positive-line predicate rewrite is
equivalent because the source-line accessor filters nonpositive metadata.
Actual `7586f120b` and the sole joined `0823d7b3c` production-SL509 load
(16.581980589 s, source0) are independently clear. All exact holds remain.

Explicit class/null unions on that short reference producer retain both raw
orders, `Class|null` and `null|Class`, with matching normalized branches.
Exactly one ordinary, fully qualified or namespace-relative class name and one
raw Identifier NULL use the existing singleton class proof and quiet full type
normalization. Runtime defining source/class/property authority and existing
reference/owner bounds remain. Both orders display `?Class` in diagnostics.
Scope keywords, warningful headers, broader unions and wider owners/lifetimes
remain partial.
[Review](../../coverage/semantics/class-null-union-parentless-short-reference-get-hook-review.json).

Six originals reuse their native observations once: weak3 and independent strict3
finish normally. Separate author145/146/146 and independent259/150/150/150
fixture-SL508 cuts retain source0; prelaw Unsupported6 stays0. No execution
failure, timeout or post-execution correction occurred. Actual `b9cb2a675`
composition and its sole joined production-SL509 load (15.831819022 s, source0)
are independently clear through the saved immutable tuple. Wider forms and all
exact holds remain.
[Independent review](../../coverage/semantics/class-null-union-parentless-short-reference-get-hook-peer-review.json).

Exact class/false unions on that short reference producer retain both raw
orders, `Class|false` and `false|Class`, with matching normalized branches.
One ordinary, fully qualified or namespace-relative class name and one raw
Identifier false require the existing singleton class proof and quiet full
normalization. The defining source/class/property authority and existing owner
bounds remain. False is an exact literal type: NULL, true and nonfalse scalars
do not gain weak Boolean conversion. Both raw orders display `Class|false`.
Broader headers, warningful names and wider owners/lifetimes remain partial.
[Review](../../coverage/semantics/class-false-union-parentless-short-reference-get-hook-review.json).

Six originals agree using saved native observations without native replay.
Separate author148/149/149 and independent288/156/156/156 fixture-SL508
cuts retain source0; prelaw Unsupported6 stays0, with no execution failures,
timeouts or corrections. Placement `17c22de41` and joined `99aea2562` retain
distinct identities. Their composition and the sole joined production-SL509
load (16.639534996 s, source0) are independently clear through the immutable
tuple. Wider forms and all exact holds remain.
[Independent review](../../coverage/semantics/class-false-union-parentless-short-reference-get-hook-peer-review.json).

Exact class/true unions on that short reference producer retain both raw
orders, `Class|true` and `true|Class`, with matching normalized branches.
One ordinary, fully qualified or namespace-relative class name and one raw
Identifier true require the existing singleton class proof and quiet full
normalization. Defining source/class/property authority and existing owner
bounds remain. True is an exact literal type: false, NULL and truthy scalars
do not gain weak Boolean conversion. Both raw orders display `Class|true`.
Broader headers, warningful names and wider owners/lifetimes remain partial.
[Review](../../coverage/semantics/class-true-union-parentless-short-reference-get-hook-review.json).

Six originals agree using their native observations once. Separate author
149/150/150 and independent312/157/157/157 fixture-SL508 cuts retain source0;
prelaw Unsupported6 stays0, with no execution failures, timeouts or corrections.
Actual and joined `76ceffde6` preserve the exact source additions. Their sole
production-SL509 load (16.039205513 s, source0) is independently clear through
immutable peer tuple `762467d5`. Wider forms and all exact holds remain.
[Independent review](../../coverage/semantics/class-true-union-parentless-short-reference-get-hook-peer-review.json).

Exact class/bool unions on that short reference producer retain both raw
orders, `Class|bool` and `bool|Class`, with matching normalized branches.
One ordinary, fully qualified or namespace-relative class name and one raw
Identifier bool require the existing singleton class proof and quiet full
normalization. Defining source/class/property authority and existing owner
bounds remain. Both Boolean literals are admitted; weak scalar writes retain
the existing Boolean conversion, while strict writes reject those scalars.
Broader headers, warningful names and wider owners/lifetimes remain partial.
[Review](../../coverage/semantics/class-bool-union-parentless-short-reference-get-hook-review.json).

Six originals agree using native observations once. Separate author150/151/151
and independent336/160/160/160 fixture-SL508 cuts retain source0; prelaw
Unsupported6 stays0. The header-generator elaboration failure and placement
preparation failure retain0; only two generator lines changed, with the original
successful source/state cuts preserved. Actual and joined `80c2caa8` and their
sole production-SL509 load (16.381116563 s, source0) are independently clear
through immutable peer tuple `60ede2a7`. Wider forms and all exact holds remain.
[Independent review](../../coverage/semantics/class-bool-union-parentless-short-reference-get-hook-peer-review.json).

Exact class/int unions on that short reference producer retain both raw
orders, `Class|int` and `int|Class`, with matching normalized branches.
One ordinary, fully qualified or namespace-relative class name and one raw
Identifier int require the existing singleton class proof and quiet full
normalization. Defining source/class/property authority and existing owner
bounds remain. Existing integer checking admits integer values, converts
eligible weak scalars and rejects strict non-integer scalar writes atomically.
Broader headers, warningful names and wider owners/lifetimes remain partial.
[Review](../../coverage/semantics/class-int-union-parentless-short-reference-get-hook-review.json).
