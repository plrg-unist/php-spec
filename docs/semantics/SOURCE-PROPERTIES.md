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
raw-row callable and crossed-frame controls. Parented/nested/adapted pairs,
explicit parameters and other body/order forms remain required.
[Paired trait-hook review](../../coverage/semantics/trait-imported-paired-hooks-review.json).

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
abrupt cleanup is a task-local derived check. Other signatures, absent/public-unset
or protected callback selection, wider receivers/names and recursive magic remain
unsupported. Unrecognized pending receivers or names conservatively stop
when a declared `__unset` exists, without evaluating a receiver in demand detection.
[Magic unset review](../../coverage/semantics/magic-unset-review.json).

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
unsupported. Coalesce and wider magic combinations stop explicitly rather than
silently use quiet NULL.
[Magic isset review](../../coverage/semantics/magic-isset-review.json).

Terminal `empty` of that external CV/literal private property now composes the
inherited bool `__isset` with a public nonstatic nonref `__get($name)` having no
parameter or return type, declared on the same parentless ordinary owner. False
skips the getter; true calls it with the original name and captured receiver. One
saved RESULT owns the receiver across both borrowed calls. Integer getter results
are inverted by zero/nonzero truth; other result families stop explicitly. Parent
lexical scope and Child called scope remain distinct, and initialized public or
typed-INITIAL slots bypass both callbacks. An active getter can still read its own
initialized private slot ordinarily. One normal original and state208 =138 reached
+70 derived cover those seams, name/source/task/frame refusals, rebound caller CV,
budget resume and normal receiver release. Both abrupt receiver releases are
derived state checks, not throwing-source agreements. Recursive magic, other
signatures/results and wider quiet receivers/names remain partial.
[Magic empty review](../../coverage/semantics/magic-empty-review.json).

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

Literal ordinary CV-base reads now invoke public nonstatic `__get` with one
untyped required parameter and no declared return type. The first family covers
ordinary instances, literal names and missing or publicly accessible UNSET
properties. Denied private/protected reads and ancestor-private literal fallback
also invoke the getter, with no hidden property type verification,
even for INITIAL or initialized typed backing. Allowed lexical VALUE reads the
physical key; accessible typed INITIAL raises Error without invoking the getter.
Lexically accessible nonpublic UNSET, changed Closure scopes for nonpublic access, writes, quiet probes,
wider signatures and guarded recursion remain explicit Unsupported.

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
distinct retained cuts. By-reference factories, owned denied access and wider
factory/receiver forms remain Unsupported; prior CV/denied evidence is unchanged.

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
magic setters and quiet access, and wider property consumers remain open.
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
