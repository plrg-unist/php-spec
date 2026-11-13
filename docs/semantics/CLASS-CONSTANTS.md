# Source class constants

The 183/184 increment extends the existing user-constant compiler and
expression machine for PHP8.5.10 CLI. Scalar/array constants and selected static
Closure/fixed first-class callable initializers execute; the family remains partial.

Class descriptors retain each constant's declaring owner, visibility, type,
initializer origin and folding status; folded values remain in initializer unit pools. Earlier available scalar constants can fold;
forward/deferred expressions remain lazy. Typed constants use strict acceptance,
including integer-to-float promotion. Existing `::class` strings retain their
separate lexical/called-class behavior.

Runtime fetch checks visibility before initialization, evaluates deferred values
in the declaring owner's scope, and publishes a cache value only after successful
evaluation and type checking. Failed initialization can be retried. Arrays remain
owned cache roots and ordinary reads use copy-on-write. Parent private constants
are excluded from inherited lookup. AST constant expressions and ordinary VM
fetch preserve their different class/member evaluation and diagnostic priorities.

A single resolved noarg `#[Deprecated]` is admitted on constants of a physical
named class, and public constants of a named interface. Fixed-name, literal-member fetches emit E_USER_DEPRECATED
(16384) with the declaring class and the fetch file/line, after access checks and
before value acquisition. Warm reads still warn. Protection follows the selected
declaration across inherited aliases; a recursive read may initialize its value
without a second notice. The outer continuation then reads the current slot.
A handler throw discards that continuation and protection, preserving an unfinished
assignment and allowing the next fetch to warn again. Table updates keep their
separate initialization path without a fetch notice.

The same noarg attribute may cover several public constants in one named class
or interface group. Attribute preprocessing happens once, then the ordinary
compiler processes the original ordered list. Each member retains its own source
index, initializer, declaring guard and pool/cache identity. Guarding one sibling
does not guard another. Existing type/link checks and compiler substitution vetoes
remain in place; no descriptor or notice task changes.
[Grouped constants](../../coverage/semantics/deprecated-multi-constant-group-review.json).

Literal `self`, `parent` and `static` reads in ordinary public named-class method
bodies use their actual current normal target, function and lexical/called scopes.
The fetch must lie inside the compiled method body, excluding default/attribute/
initializer sites. Existing selection chooses the requested class and canonical
declaration; the same value-free notice task restores that method context.
Static calls distinguish Base lexical scope from Child called scope and overrides.
A constructed receiver may have initialized the inherited cache already; a warm
parent read still warns and keeps its normal This owner through callback alias
removal, then permits receiver cleanup before the caller continues. Cache history
adds no receiver root or access to retired This. Contextual `constant()` queries
and wider call targets retain their separate bounds.
[Keyword notices](../../coverage/semantics/deprecated-keyword-class-constant-review.json).

Protected/private named-class constants use their actual source visibility.
Outside and unauthorized inherited reads raise Error before a notice or value,
even when the slot is cached or the same declaration is already notice-protected.
Normal and keyword pending-notice validation rechecks the restored caller's
access; metadata recognition remains independent of that access for existing
owning-source, update and history consumers. Source-flag mismatches reject both
public/nonpublic forgeries without narrowing source-wide compiler/query vetoes.
Public API selection and interface visibility retain their prior bounds.
[Nonpublic notices](../../coverage/semantics/deprecated-nonpublic-class-constant-review.json).

Quiet literal string/null `message` and `since` arguments reuse the existing
positional/named parser, including reordered named fields. Recognition reads the
declaring namespace, imports, class/member and source line rather than the reader
or handler. Nonempty `since` precedes a nonempty message; null/empty fields add no
suffix. Literal and public API notices use the same stateful text hook, while
existing source visibility and access checks remain in force. The compiler marks
these exact attribute argument locations as deferred metadata: their pool classes
validate without ordinary operand emission or initializer authority. No descriptor,
notice task, value owner or constructor-object protocol is added. Two scalar
originals and 240 strict481 conditions validate this slice; existing initializer
and consumer bounds remain separate from that evidence.
[Message metadata](../../coverage/semantics/deprecated-class-constant-message-review.json).

An initialized static-name, non-This/non-autoglobal CV may select the class of a
literal public constant. Existing normalization accepts a string or live ordinary
USER object and captures the published named class/interface before notice.
Entry authenticates that normalized RESULT. Once a notice occupies the current
task head, its exact declaration/requested-class/member/line tuple takes priority
over RESULT. Restored frames validate their own task head; an outer saved notice
does not block a fresh nested selection. Validation never rereads the CV or object.
The task adds no owner of an input object: the observed last-alias clear destroys
it before the folded constant result is acquired. Two originals and 208 strict482
conditions cover rebinding, real retirement, tuple priority and folded-array COW.
These fronts do not claim a deferred binder/cache fill or whole-state equivalence;
existing initializer and consumer bounds remain unchanged.
[CV selectors](../../coverage/semantics/deprecated-cv-class-constant-review.json).

With a literal nonkeyword class/interface name, a quiet initialized non-This/
non-autoglobal CV may supply the public constant member. Existing literal-class
selection stays source-authenticated; resolved member string bytes authenticate
the current fetch. The unchanged current-head decoder then requires the exact
saved tuple, with priority over a different RESULT. A fresh local member read at
a different handler line remains valid while an outer same-declaration notice is
protected; no repeated notice occurs. Handler rebinding/unset cannot redirect the
outer member, while a later evaluation sees the new value. Two originals and 225
strict483 conditions also check request-string metadata and folded-array COW.
Native observations establish captured bytes and values, not carrier pointer
identity. No task/root/history or initializer rule changes; class-CV+member-CV,
keyword/API/effectful members and owning-NUL modes retain their separate bounds.
[CV members](../../coverage/semantics/deprecated-cv-member-constant-review.json).

When both operands are quiet initialized CVs, the real adjacent member/capture
pair retains the normalized class while RESULT retains the resolved member.
The new forwarding arm validates that pair, source, line and exact tail before
consuming it; its default preserves the old path. Common notice dispatch keeps the original protected and
unprotected branches; only real dispatch creates a saved notice, so the first
warning is not suppressed by synthetic protection. Resumed validation requires
the exact saved tuple and has no RESULT fallback or mutable input read. Two
originals and 224 strict484 conditions cover both string-CV rebindings and actual
object retirement/member unset before the folded result. Class cache remains
empty/history unchanged in these fronts; existing initializer bounds are not
renewed. No task/root/history field is added.
[Dual CV snapshots](../../coverage/semantics/deprecated-dual-cv-constant-review.json).

Ordinary public named method bodies also admit quiet CV members with `self`,
`parent` and `static`. The existing method/body proof authenticates lexical,
parent and called-class selection; current member bytes then exact saved-tuple
priority preserve the selected member. No forwarding or shared transport changes.
Two originals and 288 strict485 conditions distinguish Base/Child overrides,
actual member rebinding/null and normal This ownership through notice to return.
Both fronts remain folded, with empty class cache and unchanged history.
[Keyword CV members](../../coverage/semantics/deprecated-keyword-cv-member-constant-review.json).

For fixed nonkeyword named requests, a nonvariable member expression may instead
carry immutable compiler authority: its exact FIELD1 child has true code and a
non-NUL PSTRING pool value while the whole Deprecated fetch has false code.
Source/DECL/access proof determines the member independently of RESULT; no new
snapshot is needed. Two originals and 234 strict486 conditions cover braced strings,
concat, genuine protected reentry, repeated notices and array result/COW. The
values remain folded/cache-empty; general runtime expressions remain separate.
[Pooled members](../../coverage/semantics/deprecated-pooled-member-constant-review.json).

An immutable compiled class expression uses exact FIELD0 true-code/string
identity and the existing literal-selection proof. Requested bytes retain raw
case after existing one-leading-slash removal; canonical class NAME is not a
substitute. Identifier members keep their literal proof, while non-CV expression
members need their exact FIELD1 string. Two originals and 246 strict487 conditions
cover class/member concat, protected reentry, normalization and interface result/COW.
Both fronts remain folded/cache-empty/history-unchanged, with no new snapshot.
[Compiled classes](../../coverage/semantics/deprecated-compiled-class-constant-review.json).

A fixed-name fetch may obtain its member from an existing ordinary named USER
function with zero sent/formal arguments and no namespace fallback. Real function
effects/throws finish before lookup and notice. Current resolved string bytes,
then exact saved-tuple priority, preserve the returned name without reading its
old global source again. Two originals and 247 strict488 conditions cover genuine
nested reexecution, source mutation/null, throw priority and interface result/COW.
No producer ABI, forwarding, task/root or initializer law changes.
[Member calls](../../coverage/semantics/deprecated-call-member-constant-review.json).

Other supported member expressions enter through the genuine MEMBER/CAPTURE
continuation after producing a known, valid nonowning string rvalue. A neutral
forwarding wrapper retains the original operand alongside its resolved value;
REFERENCE/VARIABLE operands gain no new admission. Source, adjacent tasks and
normal caller state authenticate entry, then real dispatch alone creates the
exact saved notice tuple. Validation never reruns a retired or effectful producer.
The entire old zero-argument named-call shape stays on its original route,
including its refusals; CV and compiled-child routes remain separate.
Two originals and 223 strict489 conditions cover method destruction before notice,
runtime ternary/concat carriers, callback source changes and interface result/COW.
These reached continuations do not turn a constructed pair into a producer-history
proof; folded values keep empty class caches and unchanged history.
[Completed rvalues](../../coverage/semantics/deprecated-rvalue-member-constant-review.json).

A completed nonowning string class rvalue may select a public Deprecated constant
with a literal Identifier member. The normal class continuation passes its
original operand alongside the normalized state; existing string validity and
raw-name lookup must agree with the canonical selected class before dispatch.
Saved validation uses only source and the exact notice tuple, without consulting
a retired producer or a changed class-source CV. Nonvariable false-code class
expressions remain disjoint from named, CV and compiled-string routes.
Two originals and 268 strict490 conditions cover method/destructor cleanup before
selection, runtime ternary/concat normalization, changed sources and fresh later
selection. A producer Exception wins before normalization and the MISSING-member
lookup. Folded values keep empty class caches and unchanged history; returned
references, objects and autoload gain no new admission.
[Completed class rvalues](../../coverage/semantics/deprecated-rvalue-class-constant-review.json).

Completed nonowning string class and member expressions also compose when both
children have false code and are nonvariable. The class continuation validates
its original operand, then appends a value-free string-acquisition marker after
the unchanged MEMBER/CAPTURE pair. Structural marker validity proves only the
captured site, canonical class and line; the consuming entry separately requires
the exact triple and original known string member before real notice dispatch.
Normal handling removes all three tasks, including old default/type/access paths.
On member throw, existing MEMBER discard removes CAPTURE and generic throw search
then removes the orphan marker before catch. No cleanup body or existing root rule changes.
Two originals and 274 strict491 conditions retain class-before-member order,
captured selection through both source changes, actual orphan validity/removal,
missing-kind refusal and interface result/COW. Folded/cache-empty limits remain.
[Composed class/member rvalues](../../coverage/semantics/deprecated-rvalue-class-member-constant-review.json).

An initialized ordinary class CV can use the same completed runtime member law
through its existing canonical MEMBER/CAPTURE pair. That acquisition already
admits string or ordinary-object selectors, so this source needs no new kind.
Entry checks the original known supported nonowning string member, exact pair,
source/scope and public selected declaration; real dispatch creates the saved
tuple. Source and saved-notice proofs neither reread the changed CV nor require
the old selector object to remain live.
Two originals and 231 strict492 conditions cover string rebinding, actual object
destruction inside member evaluation before notice, same-declaration request
priority and array result/COW. The retired object record remains in storage;
folded values keep empty class caches and unchanged history. Existing loader-
resumed CV acquisition is inherited, without a new loader witness or native claim.
[CV class/runtime members](../../coverage/semantics/deprecated-cv-class-rvalue-member-constant-review.json).

Within the admitted ordinary public method bodies, scoped keywords also accept
completed nonvariable runtime members. Existing490 authenticates the real caller,
its body and lexical/called scope; the actual target method's CODE proves false
member code. Original supported nonowning string, exact pair and task/scope checks
precede real dispatch, then the restored caller and exact notice tuple validate
resumption. No kind, owner or contextual `constant()` route is added.
Two originals and 308 strict493 conditions distinguish Base lexical `self` from
Base/Child called `static`, after a separate member helper has returned. In the
parent-instance front, clearing the global receiver during memberM leaves normal
This ownership through memberR/noticeH; destruction follows method return before
the caller's result. Folded values keep empty caches, and caller COW preserves the
permanent tree. No constructor-cold, fake/Closure/trait or wider scope claim.
[Scoped runtime members](../../coverage/semantics/deprecated-keyword-rvalue-member-constant-review.json).

An immutable compiled class string also composes with a completed runtime member.
Exact FIELD0 PSTRING and existing one-prefix normalization retain raw case;
canonical descriptor NAME is not a substitute. Original supported nonowning
member, exact pair and public lookup checks precede dispatch, then the existing
source proof and exact saved tuple authenticate notice resumption.
Literal selection deliberately need not find the class before member evaluation.
One original begins with no target, then memberM publishes an ordinary named
Deprecated class through existing checked eval and the later fetch returns7.
The state fixture supplies the real checked SOURCE_ACCEPT at SOURCE_PENDING;
the initial missing-response fixture stays zero. The peer preserves raw spelling,
FIELD0 refusal and interface array/COW. Two originals and 240 strict494 conditions
pass, without an EVAL, root, kind, API or autoload change. Folded/cache-empty and
wider initializer/producer limits remain.
[Compiled classes/runtime members](../../coverage/semantics/deprecated-compiled-class-rvalue-member-constant-review.json).

The thirteen computed literal-fetch source clauses also honor PRIVATE/PROTECTED
access through their existing visibility-matched metadata and caller-scope proofs.
Only redundant PUBLIC premises are removed; all acquisition and saved-tuple bounds
remain. An external handler is denied even while the same declaration is protected;
resumption checks the restored privileged caller. Protected inherited dual-CV and
immutable reads preserve folded array COW. Two originals and 303 strict494 conditions
pass. Public-only APIs and existing initializer/held bounds remain separate.
[Computed nonpublic access](../../coverage/semantics/deprecated-nonpublic-computed-constant-review.json).

Immutable compiled members also work with ordinary method keywords or an existing
class CV. Keyword reads use actual caller Fn.CODE, scoped selection and FIELD1 pool
bytes without mutable RESULT authority. CV reads authenticate the canonical old
pair and original supported member before real dispatch; saved validation requires
source plus the exact head tuple. Protected nested CV reads skip only the repeated
notice. Private/protected scopes, class-source rebinding and array COW pass in two
originals/344 strict495 conditions. Existing277 acquisition and all held bounds
remain, without a new kind/root or class-rvalue/compiled-member admission.
[Scoped/CV immutable members](../../coverage/semantics/deprecated-scoped-cv-pooled-member-constant-review.json).

Strict completed string-class rvalues reuse the existing zero-root stamp with
quiet member CVs or immutable members. Two member contracts preserve old runtime
behavior: pooled source returns exact byte equality, while CV input requires the
matching original VARIABLE. A false source-selected result cannot fall back to
old defaults. Class effects precede member reads; real dispatch and exact saved
class/member survive callbacks, and protected nested reads skip only the notice.
Two originals/281 strict496 conditions pass, with a separate old43 refusal
diagnostic at zero acceptance credit. No new kind/root/cleanup or held admission.
[Class rvalues/quiet members](../../coverage/semantics/deprecated-rvalue-class-quiet-member-constant-review.json).

Direct `$this` reads in ordinary public named methods select the allocated current
receiver's physical class, independently of the method's lexical scope. Literal,
compiled, quiet CV and completed runtime members retain their existing source and
saved-tuple authority. Existing current/saved frames keep the receiver alive after
a handler clears its global source; the notice adds no owner. Two public originals
and 349 strict497 conditions cover selected Child versus lexical Base, member
rebinding, receiver retirement and folded-array COW. Nonpublic visibility composes
through the unchanged metadata/access predicates without new native credit.
[Direct This reads](../../coverage/semantics/deprecated-this-class-constant-review.json).

A completed ordinary-object class rvalue with a literal member first enters a
value-free normal cursor. Existing eager cleanup retires the temporary before the
constant notice is protected. The selected canonical class survives without an
object pointer or root; exact source and adjacent operation metadata authenticate
the later fetch. A destructor can therefore read the same constant and warn before
the outer notice. A supplied destructor Exception instead cancels the fetch and
leaves its assignment target unchanged. Three public folded originals and 318
strict497 conditions cover these paths, including the genuine pending Throwable
owner. [Object selectors](../../coverage/semantics/deprecated-object-rvalue-class-constant-review.json).

Ordinary-object class rvalues also admit computed runtime, quiet CV and compiled
members. A separate value-free OBJECT kind marker authenticates the raw instance;
existing member staging retires its receiver before member evaluation. Original
VARIABLE identity and exact immutable-member bytes remain authoritative. Handler
rebinding cannot replace the captured class/member. Three public folded originals
and 310 strict497 conditions cover destructor writes before member reads, array COW
and supplied-Exception cancellation of the unentered member, pair and marker.
Literal Identifier members retain their separate cursor, while the old STRING kind
rules remain unchanged. [Computed object members](../../coverage/semantics/deprecated-object-class-computed-member-review.json).

Live returned references can also supply primitive non-NUL class strings. The
physical cell and supported payload authenticate the same canonical class before
existing literal dispatch or STRING marker creation. Generic decrements retire a
sole local cell before handler entry or member evaluation; a global cell retains
its real owner until handler unset. No notice or marker stores the cell pointer,
and saved validation does not reread its payload. Two public folded originals and
293 strict497 conditions cover these lifetimes, stale-STORE refusal, captured
interface/class values and array COW. Owning payloads and wider contexts remain
separate. [Reference class strings](../../coverage/semantics/deprecated-reference-class-string-review.json).

Live returned references may instead hold an allocated ordinary INSTANCE with
physically empty slots and no object table. Existing neutral OBJECT tasks let a
sole cell release its object before outer notice protection or member evaluation.
The active destructor owns its receiver until it returns. A retained global cell
keeps that object until handler unset/retarget; D then reads the protected selected
constant without another notice. Supplied-D-throw cancels the unentered member
and acquisition. Four public folded originals and separate strict505 packets
execute 717 conditions, including saved Child versus live Other and array COW.
Owning fields and held lanes remain separate.
[Reference objects](../../coverage/semantics/deprecated-reference-object-class-review.json).

A disjoint physical-singleton route admits a plain public untyped declared field
whose DIRECT value is an allocated ordinary fieldless child. Inherited slot
identity and both source/effective hook refusals precede admission. For a local
last-owner selector, receiver D runs before field release, then a sole child P
runs before M/H. Receiver storage remains pinned during that child callback.
A separately rooted child survives M/H/value until its later unset. Child P may throw
the supplied Exception before M/H/acquisition. Three public folded originals and
separate strictSL505 fixtures execute 613 conditions, with real child-owner counts
and array COW. Old fieldless/SOURCE/retirement rules remain unchanged.
[Owning property](../../coverage/semantics/deprecated-reference-object-property-review.json).

A separate singleton arm admits a plain declared DIRECT NULL, BOOL or INT field,
including an inherited field. The existing graph policy supplies ordinary named
identity and property constraints; the scalar value adds no heap edge. Normal
receiver D and real field-storage retirement precede M/H/acquisition. A retained
same-cell selector may instead survive until H retargets that cell: D reads the
protected selected constant, then the saved B10 result survives the live Other
class string. Two originals exercise NULL/false/17/true, with separate 166+152
strict SL507 conditions. Byte-only/NUL strings, arrays and reference fields remain partial.
[Primitive singleton](../../coverage/semantics/deprecated-reference-object-scalar-review.json).

Plain DIRECT FLOAT fields additionally use the existing singleton, wider-vector
and nested graph routes. Float values contribute no heap child; their flat-field
whitelist delegates to the whole ordinary named graph proof, preserving both the
named/non-NUL boundary and arm disjointness. Three originals validate singleton
and wider 1.5 fields plus nested NaN with shared and separately retained children.
Separate 210+179 strict SL507 conditions check real float-slot retirement and
pending child-edge consumption. Numeric operations, formatting, ownership and
source images are unchanged; wider payloads remain partial.
[Float fields](../../coverage/semantics/deprecated-reference-object-float-review.json).

Authenticated non-NUL string carriers additionally occupy those plain DIRECT
positions. Literal INTERNED and request STRINGDATA identities retain their existing
validation; the field whitelist checks the supplied carrier as well as the whole
owner graph. The singleton classifier remains structural, with stateful graph
validation required afterward. Three originals and separate 275+221 strict SL507
conditions validate literal, inherited-vector and nested request fields. String
identity metadata adds no heap owner and remains recorded after field retirement;
real shared object edges still drain before the outside child owner releases.
Byte-only strings and NUL carriers retain their refusals.
[String carrier fields](../../coverage/semantics/deprecated-reference-object-string-review.json).

Initialized plain DIRECT fields with the canonical single `string` type now admit
those carriers, including inherited declarations and nested graphs. The actual
value must authenticate and contain no NUL; type metadata alone grants no entry.
Two originals and separate 213+264 strict SL conditions validate literal INTERNED
and nested inherited REQUEST fields. These DIRECT strings add no property-reference
source or heap edge. Ordinary storage clears the string slot while real shared
child edges drain; the outside child owner survives until its later unset.
Wider types and ALIAS fields remain outside this increment; other plain-field
fences stay in force.
[Typed string fields](../../coverage/semantics/deprecated-reference-object-typed-string-review.json).

Initialized plain DIRECT fields with the canonical single `float` type now share
these routes. Admission requires an actual PFLOAT value and preserves the existing
whole named-graph proof. Two originals and separate 210+253 strict SL507 conditions
validate singleton 1.5 and inherited nested NaN with shared and outside child owners.
The float adds no reference source, release job or heap edge. Real storage clears
it before child-edge jobs drain; the outside child survives saved B10 acquisition
until its later unset. Numeric conversion, formatting and ownership rules stay
unchanged; wider types and field forms remain partial.
[Typed float fields](../../coverage/semantics/deprecated-reference-object-typed-float-review.json).

Canonical single `int` fields now admit actual initialized DIRECT PINT values.
Three originals and separate 229+257 strict SL507 conditions cover singleton 17,
an inherited flat vector with a false pad, and an inherited nested graph with
shared and outside child owners. The new flat field policy requires the whole
named graph for the typed integer; the previous untyped flat policy stays intact.
An anonymous/NUL child therefore refuses the new typed route while retaining the
old untyped whitelist result. The integer adds no reference source or heap edge;
ordinary storage and saved B10 delivery retain their existing order.
[Typed integer fields](../../coverage/semantics/deprecated-reference-object-typed-int-review.json).

Canonical single `bool` fields likewise admit actual initialized DIRECT PBOOL
values. Three originals cover a false singleton, an inherited false flat vector
and an inherited true nested graph with shared and outside child owners. The
existing owner-aware flat policy requires the whole named graph for this typed
pair; the untyped Boolean policy remains intact. Separate strict SL241 at author508
and SL300 at peer507 check type/payload correlation, anonymous/NUL-child refusal,
real storage retirement, saved B10 delivery and zero/one-step resumption. The
Boolean adds no reference source or heap edge; wider types and property forms
remain partial.
[Typed Boolean fields](../../coverage/semantics/deprecated-reference-object-typed-bool-review.json).

Initialized canonical single `false` fields additionally admit DIRECT PBOOL false;
PBOOL true retains its refusal for that type. Three originals cover an own
singleton, inherited flat vector and inherited nested graph with shared and
outside child owners. The guarded owner-aware flat policy and all prior Boolean
paths remain intact. Separate strict SL245 at author508 and SL305 at peer507
validate correlation, anonymous/NUL-child refusal, actual retirement, saved B10
and resumption. Exactly four obsolete false-pair refusals in the Boolean fixture
are retired; its other 237 premise strings stay literal, and historical cuts are
unchanged. Wider types and property forms remain partial.
[Typed false fields](../../coverage/semantics/deprecated-reference-object-typed-false-review.json).

Initialized canonical single `true` fields likewise admit DIRECT PBOOL true;
PBOOL false retains its refusal for that type. Three originals cover an own
singleton, inherited flat vector and inherited nested graph with shared and
outside child owners. Existing Boolean/false paths and the guarded whole-owner
flat policy remain intact. Separate strict SL245 at author508 and SL305 at peer507
validate correlation, anonymous/NUL-child refusal, actual retirement, saved B10
and resumption. Exactly five obsolete true-pair refusals in the earlier Boolean
peer fixture are retired; its other 295 premise strings stay literal, and
historical cuts are unchanged. Wider types and forms remain partial.
[Typed true fields](../../coverage/semantics/deprecated-reference-object-typed-true-review.json).

Initialized canonical single `null` fields admit DIRECT PNULL. Their uninitialized
declaration default stays distinct from the actual initialized slot. Three
originals cover an own singleton, inherited flat vector and inherited nested
graph with shared and outside child owners. The pure type guard and guarded
whole-owner flat policy preserve every prior path. Separate strict SL255 at
author508 and SL301 at peer507 validate type/payload correlation, anonymous/NUL
flat refusal, actual retirement, saved B10 and zero/one-step resumption. PNULL
adds no reference source or heap edge. INITIAL/UNSET and Boolean payloads for
this type refuse; wider types and property forms remain partial.
[Typed null fields](../../coverage/semantics/deprecated-reference-object-typed-null-review.json).

The nullable primitive family admits initialized DIRECT NULL or exact stored
values for `int`, `float`, `string`, `bool`, `false` and `true`. Actual descriptors
from `?T` and `T|null` use `[T,null]`; reverse source forms preserve `[null,T]`.
A shared guard accepts exactly those two singleton branches and delegates the
nonnull case to the existing single-type guard after removing the null branch.
This preserves exact numeric/Boolean values and authenticated non-NUL carriers
without adding coercion. The flat path still requires the whole owner graph.
Four originals agree with native PHP; separate strict SL541 at author508 and
SL303 at peer507 cover all 15 actual type/value rows, wrong pairs, uninitialized
slots, owner/source authority, real retirement and saved B10/resumption. The
single peer fixture notation failure retains zero credit; only that fixture
reran. Fourteen obsolete nullable-refusal rows retire 58 assertions while every
retained premise stays literal and ordered. Mixed/class/array field types,
aliases and wider property forms remain partial.
[Nullable primitive fields](../../coverage/semantics/deprecated-reference-object-nullable-primitive-review.json).

Plain DIRECT fields also admit wellformed primitive unions over `int`, `float`,
`string`, `bool`, `false`, `true` and `null` in source order. Every branch must be
supported and nonredundant before a matching single-type stored-value guard can
authorize the field. Duplicate masks, `bool` with an exact Boolean, and
`false|true` refuse; authenticated non-NUL strings and exact numeric tags retain
their existing checks. The flat path still requires the whole named owner graph.
Three originals cover an own singleton, an inherited eight-field vector and a
nested shared graph. Separate strict SL516 at author508 and SL319 at peer507
validate all 11 actual rows, wrong pairs, unsupported branches, source/layout
authority, real owner counts 3→2→1 and saved B10/resumption. The original head/tail
binder diagnostic retains zero credit; only affected source models reran.
Two obsolete global refusals retire while 301 retained nullable premises stay
literal and ordered. Mixed/class/array types and wider property forms remain partial.
[Primitive-union fields](../../coverage/semantics/deprecated-reference-object-primitive-union-review.json).

Initialized DIRECT fields with one resolved `PTCLASS` target now admit allocated
ordinary instances of that loaded user class or a linked subclass. The type check
remains separate from the complete named, non-NUL owner graph and source/layout
authority. A disjoint flat singleton route closes the typed-child dispatch gap;
its graph guard precedes descriptor lookup. Existing object release jobs preserve
each physical edge without adding a reference constraint or owner.
Three originals cover an own singleton, inherited shared-edge vector and nested
outside-owned child. Separate strict SL329 at author508 and SL321 at peer507
validate all seven actual type/child/job rows, subtype and wrong-pair controls,
malformed-owner refusal, source authority, owner counts and saved B10/resumption.
The peer fixture constructor diagnostic retains zero credit; only that fixture
reran. Named `self`/`parent` may compose when already resolved to this `PTCLASS`;
unresolved variants and wider property forms remain partial.
[Class-typed edges](../../coverage/semantics/deprecated-reference-object-typed-class-review.json).

Canonical unions with at least two singleton branches additionally admit named
class alternatives and the seven supported primitive types. Every name, branch
shape, duplicate class/mask and Boolean redundancy check precedes exact stored-value
selection. Unselected class names need no lookup; a selected object branch retains
the existing loaded ordinary-class and subtype guard. The flat path still proves
the whole owner graph, and a disjoint object-singleton arm checks that graph before
descriptor lookup. No conversion, reference constraint or owner is added.
Three originals cover nullable-class objects and NULL, an inherited mixed vector
including an absent class with a matching integer, and nested shared/outside-owned
objects with absent alternatives before and after loaded matches. Separate strict
fixture SL630 at author508 and SL374 at peer507 validate all 15 actual type/value/job
rows, malformed whole types, source/layout authority, real retirement and saved
B10/resumption, without a unique-count claim. Exactly nine obsolete generic
refusals retire; all 1,476 retained strings stay literal and ordered. No new failure,
retry or old execution replay occurs. Array fields and wider property/lifetime
forms remain partial.
[Class-union fields](../../coverage/semantics/deprecated-reference-object-class-union-review.json).

Standalone `mixed` and `object`, and wellformed unions combining `object` with
the seven supported primitive types, additionally admit bounded initialized
DIRECT payloads. Local checks authenticate non-NUL string carriers and allocated
ordinary INSTANCE/class values before exact whole-type tag matching. They do not
traverse a graph: the existing owner traversal retains its ancestor path and
rejects cycles. The flat wrapper and disjoint object-singleton arm still require
that complete graph before admission. No conversion, reference type source or owner is added.
Three originals cover a mixed object singleton, mixed primitive/carrier values,
nullable object NULL and a primitive-valued six-branch object union, plus nested
shared/outside-owned objects. Separate strict fixture SL671 at author508 and
SL404 at peer507 check all 15 actual rows, malformed types, bounded mixed-array
refusal, local-type-positive cycles, source/layout authority and real retirement
through saved B10/resumption. No unique-count claim is made. Seventy obsolete
assertions, including one orphan context binding, retire while all 5,115 retained
strings remain literal and ordered; earlier executions are not replayed. Arrays,
aliases and wider property/lifetime forms remain partial. Existing ordinary classes may implement interfaces; this adds no new
nominal interface source credit.
[Object/mixed fields](../../coverage/semantics/deprecated-reference-object-object-mixed-review.json).

Resolved ordinary user-interface constraints and class/interface intersections or
DNF types now compose with the seven primitive alternatives. Complete canonical
name, duplicate, mask, Boolean and syntactic subset checks precede matching. A
selected conjunction requires every target loaded as an ordinary class/interface;
unselected names need no lookup, and primitive matches perform no nominal lookup.
Existing exact subtype/interface closure supplies the answer. Local payload checks
retain allocation/carrier bounds and never restart the ancestor graph. The flat
wrapper and disjoint object-singleton route retain the whole owner proof.
Three originals cover inherited interface membership, a shared nine-field DNF/
primitive vector and a nested graph with an outside child owner. Separate strict
SL633 at author508 and SL432 at peer507 validate all 13 actual type/value/job rows,
partial conjunction refusal, malformed types, source/layout authority, cycles and
real release edges through saved B10/resumption. No unique-count claim is made.
Exactly five obsolete assertions retire; 653 retained strings in the three
reviewed lists stay literal and ordered. The initial draft failure and diagnostic/
preparation failures retain zero credit; no native or legacy campaign is replayed.
Arrays, ALIAS constraints, readonly/hooks/setter variants and wider lifetime forms
remain partial.
[Nominal fields](../../coverage/semantics/deprecated-reference-object-nominal-review.json).

Initialized readonly DIRECT fields retain their actual public/protected(set)
descriptors, nonempty supported types and uninitialized defaults. The local
no-hook/nonstatic policy composes with existing exact field types; graph traversal
retains its ancestor path, and flat admission proves the whole owner graph.
Own/inherited declarations and readonly-class normalization preserve real class
flags, physical shared edges and ordinary cleanup. Three fresh originals agree,
with native observations reused once, at separate author508 and peer507 cuts.
Strict SL336/327 validate nine actual fields, flag/source/layout forgeries, cycles,
retirement and saved B10/resumption; these are 663 physical conditions, source0,
without a unique-count claim. The failed precode signature fixture remains0;
no legacy assertion or campaign is replayed. Protected/private get visibility,
other setters, aliases, hooks and wider lifetime forms remain partial.
[Readonly fields](../../coverage/semantics/deprecated-reference-object-readonly-review.json).

Plain protected/private DIRECT fields now compose with existing exact field types,
including untyped fields, stored defaults and inherited private shadows with the
same textual name. Actual mangled KEY/DECL and full source/layout authentication
remain distinct from the local field policy. Structural NULs in property keys add
no Owned-NUL payload authority; untyped EPS remains type-only locally, and the
whole owner graph retains arrays/cycle bounds. Three originals agree using native
observations once at separate author508/peer507 cuts. Strict SL333/344 exercise
nine actual fields, key/declaration/default/order forgeries, scoped private reads
and real shared/outside cleanup through saved B10/resumption:677 physical
conditions/source0, without a unique-count claim. Eighteen obsolete generic
PRIVATE refusals retire;2171 retained strings stay literal. The failed finite
fixture/preparation stays0, with no historical replay. Other setters, nonpublic
readonly, aliases, hooks and wider lifetime forms remain partial.
[Nonpublic fields](../../coverage/semantics/deprecated-reference-object-nonpublic-review.json).

Remaining initialized typed DIRECT modifier forms now retain actual setter/final
metadata: readonly with no setter bits, public nonreadonly protected(set), and
public/protected private(set) with FINAL. Readonly defaults remain uninitialized;
nonreadonly defaults gain no new restriction. The existing exact type, complete
owner graph and full source/layout authority remain. Three originals agree at
separate author508/peer507 cuts with native observations once, covering explicit
equivalent setters, readonly-class normalization and inherited shared cleanup.
Strict SL354/352 execute706 physical conditions/source0 without a unique-count
claim, including nine actual rows, local/source forgeries and saved B10/resumption.
Twenty obsolete generic projections retire;2219 retained strings and specialized
helper/source negatives stay literal. No attempt fails or retries and no
historical campaign replays. Hooks, aliases, containers and wider lifetime forms
remain partial.
[Modifier fields](../../coverage/semantics/deprecated-reference-object-modifiers-review.json).

Typed public backed GET and body-backed block SET fields now retain their actual
DIRECT storage during class selection and cleanup. Structural source backing is
independent of an active hook callback; selection and physical slot release
themselves dispatch no hook. User constructors/destructors retain ordinary PHP execution.
The whole owner graph and full source/layout authority remain. Three originals
agree at separate508 cuts with native observations once, including an inherited
shared-Leaf vector, a SET-only stored int default and nested outside ownership.
Strict SL389/252 execute641 physical conditions/source0 without a unique-count
claim. Ten actual rows and six backing ASTs distinguish real storage from forged
virtual/static/unbacked projections, preserving release order, B10 and resumption.
Both initial finite-fixture failures retain0 and only those checks rerun; legacy
assertions and campaigns remain untouched. Untyped hooks, short SET implicit
backing, wider hook forms, aliases and lifetime contours remain partial.
[Backed hook fields](../../coverage/semantics/deprecated-reference-object-hooks-review.json).

Short SET expressions also retain physical DIRECT backing even without a lexical
own-property occurrence. The existing installed function/source child/code receipt
certifies that backing and is disjoint from GET and block SET evidence. Existing
field types, whole owner graphs and full source/default/layout authority remain.
Three originals agree at separate508 cuts using native observations once: stored
int17 and boolfalse setters remain uncalled through singleton, inherited shared
and nested outside-owner cleanup. Strict SL367/292 execute659 physical
conditions/source0 without a unique-count claim, preserving NEXT/slot order,
Leaf2-to1 and3-to2-to1 ownership, false setter markers, B10 and resumption.
Missing function/code/source-child receipts and virtual/empty-block projections
refuse. One initial finite-fixture type failure retains0; only that query reruns,
with no legacy assertion edit or historical replay. Untyped hooked fields,
broader hook modifiers, aliases and wider lifetime forms remain partial.
[Short SET backing](../../coverage/semantics/deprecated-reference-object-short-set-review.json).

Untyped public body-backed block SET retains its absent property type and real
stored default. The source-authenticated compiler and origin keep an implicit
required by-value `value` parameter with no type and a `void` return. Structural
backing composes with the existing complete graph and physical slot cleanup;
selection and release never invoke SET. Four originals agree at separate508 cuts,
including ordinary writes, stored17/false selectors and nested outside ownership.
Separate strict SL468/341 preserve exact descriptors, raw-source/compiler bounds,
shared release order, inactive setter markers and saved B10/resumption. The first
fixture failure and pre-admission Unsupported/timeout cuts retain zero credit;
only genuinely affected work repeats. Wider headers, traits, modifiers, aliases
and lifetime contours remain partial.
[Untyped block SET](../../coverage/semantics/deprecated-reference-object-untyped-set-review.json).

Untyped short SET now compiles its original expression with the same implicit
untyped parameter and authenticates the installed function, source child and
compiled-expression receipt. The existing implicit assignment, EPS hook-field
graph and physical cleanup rules remain unchanged. Four fresh originals agree
at separate508 cuts using native observations once; ordinary false/int/string
writes and singleton/inherited/nested selectors distinguish actual storage from
uncalled hooks. First strict SL500/403 preserve receipt forgeries, source/layout
authority, shared/outside ownership and saved B10/resumption. Two corrected
precode query failures remain0; the earlier Unsupported3 and every private cut
retain their original identities. Explicit parameters, pairs/traits, declaring
inheritance, wider modifiers/aliases/containers and lifetimes remain partial.
[Untyped short SET](../../coverage/semantics/deprecated-reference-object-untyped-short-set-review.json).

One actual untyped required Param on a sole class short SET now retains its own
source name and indexed origin. Separate absent-type guards preserve typed and
implicit rules; existing signature compilation supplies the untyped receive and
`void` return. Exact raw Param/RHS and installed signature/BODY/code authenticate
backing, and an actual Current SET supplies its real parameter origin and line.
Four originals agree at separate508 cuts with native observations once. A false
input/result with transformed true backing distinguishes reception from implicit
`value`; stored defaults, inactive selectors and shared/outside cleanup remain
exact. First strict SL579/464 include active binding/default-origin/CV checks,
Param/function forgeries and zero/one/full resumption. The preparation and first
algorithmic binding failures retain0; only the affected binding premise splits
before corrected validation. Pairs/traits, wider declaring inheritance/modifiers,
aliases/containers and lifetimes remain partial.
[Explicit untyped short SET](../../coverage/semantics/deprecated-reference-object-untyped-short-set-explicit-review.json).

One actual required untyped Param also compiles on a sole body-backed block SET.
Separate absent-type rules retain its source name, indexed Param origin, `void`
return and real statement tasks. A genuine active SET before its first statement
has input false, backing17 and count0; resumed writes distinguish the assignment
result from transformed storage. Four fresh originals agree using native
observations once; separate strict SL578/433 preserve source/function/Param
forgeries, inactive defaults, physical shared/outside release and B10/resumption.
The first elaboration failure and peer Git HEAD-marker failure remain explicit;
a reviewed protocol-only revision bridge accepts the completed peer comparison
without replay. The actual joined508 production SL load remains separate/source0.
Pairs/traits, declaring inheritance/modifiers, aliases/containers and broader
lifetimes remain partial.
[Explicit untyped block SET](../../coverage/semantics/deprecated-reference-object-untyped-set-explicit-review.json).

A direct trait import now preserves an actual required untyped block SET Param,
its raw trait function and copied consumer scope. Separate source/compiler gates
reuse the existing trait import, default-origin, task and ownership machinery;
physical storage appends the imported field after the consumer's own fields.
Four eligible originals agree with native observations once, while a retained
own-GET plus trait-use original stays an explicit Unsupported control. First
actual strict SL260/301 preserve raw/imported identity, real active consumer
scope, named reception and shared/outside release; source/fixture preparation
failures retain zero credit. The joined508 production SL load is separate/source0.
Methodless exporters are the tested selection. Implicit untyped trait SET, pairs,
nested/adapted exporters and wider import/lifetime contours remain partial.
[Direct trait untyped block SET](../../coverage/semantics/deprecated-reference-object-untyped-trait-set-explicit-review.json).

Direct trait short SET also retains its actual untyped Param, copied consumer
scope and original RHS/CODE receipt. Certified implicit backing follows the real
expression through the existing scoped assignment tasks. Four fresh originals
agree using native observations once; first strict SL277/311 preserve actual
parameter reception, transformed storage, raw/scoped expression authority,
appended fields and shared/outside release. All first candidate checks pass;
prior Unsupported controls retain their original cuts. The actual joined508
production SL load remains separate/source0. Implicit untyped trait SET, pairs,
nested/adapted exporters and wider import/lifetime contours remain partial.
[Direct trait untyped short SET](../../coverage/semantics/deprecated-reference-object-untyped-trait-short-set-explicit-review.json).

An implicit untyped trait block SET now keeps an empty source Param list distinct
from its runtime `value` signature/CV. No checked Param or Param CODE entry is
fabricated; active reception uses the real hook line and copied consumer scope.
Four valid originals agree with native observations once, and separate first
strict SL262/297 check source absence, imported identity and shared/outside
release. The actual joined508 production SL load remains separate/source0.
The discovered explicit `set()` ambiguity and its shared token-presence repair
have separate retained evidence; an empty AST list alone does not prove source
parentheses were omitted. Short implicit forms, pairs and wider imports remain
partial. [Implicit trait block SET](../../coverage/semantics/deprecated-reference-object-untyped-trait-implicit-set-review.json);
[header-presence repair](../../coverage/semantics/property-hook-parameter-list-review.json).

Implicit trait short SET also keeps no checked Param while installing a required
untyped `value` and the real RHS/CODE receipt. The known-absent header fact
authenticates raw and copied origins; existing scoped short tasks write the
backing field. Four originals agree with native observations once, and separate
first strict SL302/309 cover actual reception, header/RHS/function refusals and
physical shared/outside release. All candidate campaigns pass first; the old
preparation and header failures stay separate. The joined508 production SL load
is source0. Untyped pairs, wider modifiers/imports and lifetime forms remain
partial. [Implicit trait short SET](../../coverage/semantics/deprecated-reference-object-untyped-trait-implicit-short-set-review.json).

Wider physical vectors of plain declared DIRECT fields admit NULL/BOOL/INT pads
and flat ordinary fieldless children. Existing full entry validation supplies
layout/order/unique-slot authority; per-slot policy alone does not. For a local
last-owner selector, existing cleanup follows physical inherited/local order
independently of child allocation or write order. Separate slots sharing a child
retain separate edges until the last release; a middle callback observes that
child alive before its single finalizer. A first-child Exception still permits
later-field cleanup before catch and cancels M/H/value. Three originals and
separate 281+203 strict SL507 conditions validate these paths. Old empty/singleton arms and
continuation/ownership bodies remain unchanged.
[Field vectors](../../coverage/semantics/deprecated-reference-object-fields-review.json).

A separate non-flat route admits finite acyclic nested graphs with the same plain
DIRECT field policy. Each new graph node is a canonical, non-NUL named ordinary
INSTANCE with no table or Throwable ancestry. Ancestor paths reject cycles while
allowing reconverging child edges and outside owners. Existing cleanup preserves
nested storage pins and releases each physical edge; a shared child runs once
after its last edge, while an externally retained child survives acquisition.
Two source originals and separate 211+217 strict SL507 conditions validate the
normal saved B10 result and supplied deep-Exception cleanup. The throw control
already agreed before this extension; its new OBJECT operation image is checked
separately. Wider field payloads remain partial.
[Nested graphs](../../coverage/semantics/deprecated-reference-object-graph-review.json).

The value-free pending task retains only declaration, requested class, member and
line; it adds no root or initializer context. Same-unit folding, folded-pool imports
and warm-cache imports refuse substitution for these declarations. The first
ordinary formal-default evaluation fetches and warns; its later parameter-cache hit
does not fetch again. `defined()` keeps its existing separate path. Other attribute
argument forms, declaration kinds and wider dynamic/keyword contexts remain
separate. [Notice review](../../coverage/semantics/deprecated-class-constant-fetch-review.json).

Interface source groups use their physical field3 path. Inherited interface and
implementer fetches share the declaring interface's attribute, notice guard and
value slot; only interface requests need the additional source-validity arm.
Implementing-class requests retain the existing class proof. Deferred scalar
reentry, warm throw, diagnostics and checked eval/formal-default compilation are
validated separately from the original class slice. Owning-global recipient source
authority has its own gate; the attr-free source arms remain unchanged.
[Interface notices](../../coverage/semantics/deprecated-interface-constant-fetch-review.json).

`constant()` receives attributed public scalar constants through a literal or
initialized plain-CV string query. The pending task retains the captured config
and selected declaration. Its notice phase protects that declaration across API
and literal reads; its acquisition phase is unprotected and never stores a
selected value. Successful handler return then uses a folded scalar, current
cache or the existing lazy `CLASS_CONST_CALL` binder. The actual adjacent API
acquisition continuation authenticates that binder; an autoload resume alone
does not grant permission. Handler throw cancels acquisition and leaves an
unfinished assignment unchanged.

The task delegates existing config roots and nonce. Request-string carriers are
immutable metadata with zero heap nodes. The checks establish captured-query
stability across CV rebinding. Existing class/interface lookup,
source facts, cache history and trace rules stay in place. Wider owning results,
keyword/autoload/conversion contexts and wider query expressions remain separate.
A held keyword query now honors the same value fence. `defined()` and ordinary
unattributed query routes retain their prior behavior.
[API review](../../coverage/semantics/deprecated-class-constant-api-review.json).

The same API phases now admit folded literal-array initializers using the existing
array-tree validator. Eligibility reads pool class metadata; acquisition reads the
actual tree after the notice. The notice task adds no array owner. Handler-local
COW copies can retire before the outer API returns the original pool value and
adds one result edge. Later result mutations preserve the permanent pool tree.
Empty and nested literals, named-class/interface aliases and warm notice throws
retain these distinctions. No nonfolded owning initializer, image, task or root
law is added. [Array API review](../../coverage/semantics/deprecated-class-constant-array-api-review.json).

Authenticated nonfolded declarations with this exact attribute also receive
existing owning globals. Their declaration and initializer-child origins reuse
the ordinary binder and source facts. The class notice finishes and its protection
clears before the initializer emits a global notice. Normal outer replacement
releases a computed child value before publishing its own value; a global-notice
throw leaves assignment/cache uncommitted and allows retry. Global Closure aliases
retain identity and scope, and typed outer failure preserves a child cache fill.
The source gate also serves existing authenticated update consumers without a new
construction protocol. Wider owning API initializers and abrupt old-value release
remain separate. [Owning source review](../../coverage/semantics/deprecated-owned-class-constant-notice-review.json).

The API also acquires existing owning values from an untyped, fully resolved
direct global-name initializer. At acquisition it authenticates the actual USER
donor's value/class. Cold reads retain the real CLASS_CONST_CALL and API task;
warm reads require exact donor/cache identity and the existing publication/type/
history proof. No value is copied into the notice continuation. A nested literal
read during the global warning can fill the same slot; the API's visited state
and the declaration notice guard keep their existing separate roles. Result/cache
owners, caller array COW and global Closure identity/scope are preserved without
a new task or root rule. Computed initializers and wider query forms remain separate.
[Owning API review](../../coverage/semantics/deprecated-owned-class-constant-api-review.json).

Initializer continuations preserve nested global/default contexts, selected class
and member operands, source origins and recursion protection. Simple unresolved
names report the fetch file/line; compound evaluation uses its expression location
and an extra constant-expression frame only when the executor location differs.
Post-evaluation type errors restore the fetch context. Finite controls reject
swapped, duplicated or skipped update tasks and coherently forged selected slots.

[Diagnostic ingress217](../../coverage/semantics/reporting-diagnostics-review.json)
saves and restores initializer facts through error-handler and nested ordinary
calls. The active lexical evaluator is separate from the global busy stack;
callbacks retain recursion protection without inheriting initializer scope.
Selected deprecated-constant values survive callback declarations, and failed
initializations can retry. Compound diagnostics and thrown constructors keep
expression/fetch locations and synthetic constant-expression traces distinct.
Compound callback/eval filename creation remains open.

Inheritance checks preserve finality, different-owner ambiguity, visibility and
type covariance in that order. Same-owner interface diamonds remain unambiguous;
private parent constants do not constrain a child's replacement. Real linking
checks constants before methods, while the early availability probe keeps its
separate method/property/constant order and defers only unresolved types.

Append-only link, cache-fill and table-completion origins preserve temporal AST
status. Individual fetches never mark a class fully updated. NEW enters the
parent-first updater only when the requested class still needs it; successful
earlier fills survive a later failure, and retry retains the unfinished work.
Source-derived inverse controls reject incorrect task order, missing completion
markers, unrelated update sites and a class used before its publication.

The earlier bounded evidence comprises25 original source/native comparisons
across successive revisions and finite16+13. The later linking slice accepts
twelve further tuples (6 normal,5 static rejections,1 PHP error) and five finite
programs with27+13+19+18+16 overlapping predicates. These are distinct cutoffs,
not a single-revision37 rerun or whole-family acceptance.
The [ledger](../../coverage/semantics/class-constants-current-review.json) retains
original failures, including the refuted native update hypothesis. Maintained
source and finite commands are in `Makefile`; raw files stay outside Git.

Included/evaluated units import only earlier published scalar/constant-array
values that were folded or successfully cached before that unit entered. Uncached
initializers stay lazy even when their referenced global is now defined. Imported
arrays are copied into the new pool, and later fills cannot retroactively change
a compiled image. Five further native comparisons (3 normal/2 static) and one
finite fixture/31 predicates validate this boundary. The original negative
transport expectation is retained as a fixture failure.

Current-runtime checks add six native agreements for static access priority,
runtime array FCC owner/called-class scope, handler fetch, completed reference
aliasing and static unset. Their two source cutoffs remain separate. A later
borrowed strict-identity callback fills a deferred array cache and reads it after
handler retirement (`7ne7`). On the current StaticCall-reference composition,
NewC completes its table before a getter exports the property cell; alias mutation
changes the property while the cached constant stays unchanged (`32`). The
earlier catalogue contains 50 agreements across these preserved revisions.

Static anonymous Closure initializers require no explicit use-list and create
with the declaring owner as both lexical and called scope, without a receiver.
Fixed function callables preserve the first successful namespace/fallback target
even when a later initializer error discards the object. Static-method callables
retain the method owner and selected called class separately, including private
access from the initializer owner. Literal string class selectors use global
spelling, while named selectors keep their namespace/scope rules. Invalid
nonstatic/use/dynamic forms and literal nonstring names retain PHP compile errors.

Object caches retain genuine constructor identity and recursive array/alias
certificates; objects never become cross-unit folded pool values. Nonowning
creation records preserve retired selection history. The cache owns the object
and its scope and static cells. Clones copy the current body/scope/static state
without acquiring the original constructor marker. Four finite fixtures reject
coherent scalar erasure, wrong array sites, substituted clones with invented
records, invalid selection prefixes/scopes and missing roots (159 predicates).
A later literal-class fixture adds 44 predicates. Twenty-two new full native
comparisons bring the maintained catalogue to 72 (32 normal, 22 PHP errors, 18 static
rejections). Source and finite cutoffs remain separate; promotion adds no rerun.
A later current-source comparison registers a cached constant Closure as a handler.
Its GLOBALS write leaves the folded false-left expression's original null intact,
and repeated identity/direct invocation retains the static counter (`1null:same:2`).
This brings the maintained catalogue to 73; the earlier 72 sources stay unchanged.

Named constexpr `::class` folds namespace/import spelling without class lookup.
Known self uses the declaring owner; known parent retains its source spelling.
Closure and eval contexts resolve deferred self/parent from authenticated lexical
scope, including rebound defaults. Contextual defaults bypass origin-only caches;
ordinary defaults retain their existing cache ownership. Literal class strings
and parser-folded literal concatenation follow Zend's separate class-name route.
Live static/computed forms and nonstring literals retain their PHP errors, while
folded dead branches disappear before admission.

Seventeen constant-context and two ordinary keyword-form comparisons add nineteen
agreements (11 normal, one PHP error, seven static rejections), bringing the
catalogue to 92. Two focused fixtures add 25/38 predicates for coherent folded
spelling substitution and a forged contextual default cache/rebound scope.
Original Unsupported and elaboration failures stay preserved; the earlier
binding-premise draft remains unrun.
The original concat rejection hypothesis remains refuted by normal `GhostName`.
These source and finite cutoffs are separate. One later current reporting/214
comparison invokes a rebound B default before original A inside a Stringable
receive callback, retaining cached identity (`B:A:same`), bringing the catalogue
to 93. Maintenance adds no execution credit.

Accessible references into an incomplete class table are explicitly Unsupported;
the separate rejected control is not a native agreement. Unretained
computed/scoped table-update selectors remain
Unsupported. Constructor contexts outside class constants, builtin FCC targets
and object transfers without an authenticated source/cache relation also remain
Unsupported. Constant modifier
admission, wider attributes, traits/enums/internal constants and broader default/property
consumers stay open. These checks reused the recorded runtime; they add no fresh
copied rebuild, reporting-mask, paused return or full-core closure.
