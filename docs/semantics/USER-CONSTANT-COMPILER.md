# User constant compiler

Compiler88 prepares the initializers of ordinary user constants for runtime89.
The paired source increment is recorded in the [independent review](../../coverage/semantics/user-constant-review.json).
Defaults and the complete constant family remain open.

A `NStmtConst` walks its declaration list at field1 in order. Each `NConst`
initializer is field1 of that declaration. Existing45 folds it in the current
lexical environment, then88 validates the remaining expression, following the
original folded facts and redirects. Invalid operations in eliminated arms can
therefore disappear. Legal object, property, class-constant and callable forms
whose core consumers remain unavailable are explicitly Unsupported. Dynamic
class names and `static::` retain their separate compile errors.

Initializer compilation precedes special-name and import-conflict diagnostics.
The declared `CODENAME` belongs to the actual `NConst` origin; it preserves the
qualified source spelling, has no fallback, and is distinct from initializer
constant-fetch names. A declaration `CODEEXPR` retains the compiler's declaration
line. Runtime registration normalizes namespace prefixes and preserves terminal
case; this is not uniform lowercasing. The existing source environment's SEEN
and import rules retain their pinned compile-order case distinction.

Attributed global declarations with at least two constants enter this compiler
at the first constant-name line. Their initializers and name checks run in order
before the final multi-constant attribute error. Remaining constant reads and
compiled closure ends advance the diagnostic cursor; literals retain it. The
constant walk follows folded facts and redirects, visits array values before keys,
and checks constructor argument structure before values. It compiles reached
closure bodies once, preserving their earlier errors without emitting runtime
operands for a declaration that cannot execute. Qualified class keywords retain
their distinct folding, NEW/callable and `::class` checks.

Attribute arguments are not compiled before this error; completed parser encoding
warnings inside them still precede it. The error terminates eval/included units
before catch/finally. Compiler-only source predicates admit initializer contexts
without extending runtime constant declaration authority. Single attributed
constants were left Unsupported at that cut.
[COMP181 evidence](../../coverage/semantics/attributed-constant-compile-review.json).

Quiet single attributed constants now compile their initializer and name before
metadata. Attribute arguments check unpacking, duplicate names and positional
order immediately before each value; secondary builtin target/repetition checks
follow all groups. Arguments remain deferred, including NEW/callable values and
compiled closure bodies. Initializer closures retain ordinary runtime operands
while reusing their exact compiled template, body and source lines.

Resolved attribute names are stored at genuine source paths without CODEEXPR.
The existing source-image projection authenticates the complete compiled code
and pool, including metadata names. Runtime activation and constant receipts admit only the genuine
single declaration and quiet validated metadata; attribute fields stay outside
initializer roots. Duplicate registration retains the original constant origin.
[COMP182 evidence](../../coverage/semantics/single-attributed-constant-review.json).

Literal/null Deprecated message and since fields now activate without evaluating
attribute arguments. Actual source fetches and `constant()` warn using the
installed declaration's spelling and metadata; duplicate candidates cannot
replace them. User constants deliver level16384, while startup E_STRICT keeps
level8192. The captured lookup prefix and API query survive handler rebinding
and later namespace shadows. Protection lasts through callback argument sends,
body and return cleanup. Direct handler throws and admitted body/retval exits
restore the handler and release protection; locals release while the raw handler
is still disabled, and a saved callback releases while the constant is protected.
A fresh local throw can cancel exit and reach the genuine saved catch/caller
tail. Eager callback release retains the pending exception, protected read and
captured API owner; a new release exception keeps the previous link, and normal
continuation preserves the exit status. `defined()` stays quiet; parameter and
class initializer caches retain their ordinary first-use behavior. Declaration
namespace controls literal/null admission.

The consumer also accepts owning values from the existing ordinary constant
producers. Direct opcodes retain the actual fetched value/class before warning;
only that live receipt owns the copy. Stable-text `constant()` and genuine global
`NConst` AST reads retain selection until successful warning delivery. Arrays,
certified Closures, user instances and stdClass reuse their existing value-class
checks. Facts keep the actual class and a prefix-bound nonfoldable lookup, so a
handler-created namespace shadow cannot change the earlier read. Exit markers
expose only their genuine saved global binder to context validation; the full
marker contract still authenticates the callback, status and saved tail.

Owning omitted defaults now enter genuine unscoped named functions. The active
receive binds the actual parameter/default origin and the selected read prefix;
fixed primitive `define` calls from its handler retain an authenticated publication
cut. The old builtin E_STRICT and eval-cut routes keep their separate contracts.
Nested receives may fill a pending default's cache: the outer read still delivers
its original value and replaces that slot only when cacheable. Shared empty arrays
can cache; nonempty arrays remain per-call reads. Cache publication and formal-slot
initialization precede type verification, including a TypeError. Saved exit markers
expose only their real parameter binder, and receive retirement follows the actual
binder discard after cancellation.

Fixed-name `->` and `::` calls also receive owning defaults in ordinary named,
by-value nongenerator methods declared in named classes. The actual descriptor,
default/function identity, declaring and called scopes, and publication prefix
must match the receive's birth. User-Deprecated handler publications preserve that entire saved
call suffix; no historical row retains a receiver. Inherited methods share the
declaring method's default cache. Reentry, formal ownership before TypeError and
exit cancellation reuse the same receive and cleanup contracts.

REAL Closure literals, class-scoped method literals, bound copies and their
ordinary clones receive owning defaults through their actual cache identity.
Shared entries retain the default-origin key; private entries additionally name
the selected Closure object. Same-template Shared/private histories coexist
without poisoning each other. Every positional/named lookup and write uses that
identity, including a scalar cached before a later owning donor. Private clones
and rebindings start fresh caches. Unknown stamps never become Shared implicitly.

The genuine receive birth captures its nonowning cache owner; only same-owner
closed child receives can justify a filled pending slot. Retired stamps and births
do not require a live source object. Native cache zvals are nonrefcounted: the model's
empty-array availability root preserves its immutable value/COW, without claiming
a native refcount increment or retaining the Closure/source/captures/receiver.
Unscoped private rows survive capture/static callbacks until actual store drop.
For ordinary scoped destruction, a nonowning private-cache marker ends the rows
after capture/static callbacks and before bound `$this` release. A remaining
HANDLE alone cannot validate those retired rows. Quiet release drops them
atomically. Existing Shared
and class-constant encodings stay fixed. Actual Closure/formal roots preserve
TypeError and exit-cancellation order; generic scalar/type paths remain separate
from the new private owning-read authority, which requires an actual REAL callee.

Ordinary nongenerator `Closure::call` also receives these defaults through its
actual REAL source and instance receiver. Existing455 receipts select either
the same-scope Shared cache or a fresh invocation cache, keyed by invocation and
default origin. Receive births preserve that identity; nested calls with the same
source, receiver and site still have distinct temporary caches. Callee locals
and their destructor callbacks finish before the cache-free job. API argument
and receiver owners then retire before the existing source-Closure owner, with
no extra capture pin. Quiet, throwing and TypeError completion use the same
native lifetime; Generator calls retain their separate path.

Direct scoped recipients use actual116 scope/creation records or181 binding/API
records. The selected REAL Closure owns its receiver; the call borrows it without
an extra pin. Lexical and called classes stay distinct, including inherited
receiver-free literals/clones with a late-called Child. New scoped-private row
lifetime uses the immutable455 class stamp and source proof after live binding
records retire; pending marker authority ends before the receiver's destructor.
Birth and stamp history remains valid without reviving cache storage or guessing
a recipient from a source site.

Direct public ordinary instance/static method FCCs, `Closure::fromCallable`
results and their clones reuse existing captured descriptors and scope/receiver
records. Runtime direct captures share the original method cache; cold API
captures can have private caches, with fresh private clones. A genuine receive
records its selected callee in nonowning ENTRY history, including Shared owners.
Active receipts require that exact instance; closed receipts use immutable
body/cache/function facts without rereading retired receivers or API inputs.
An ENTRY-bearing parent requires genuine child entry proof for pending-cache
reuse. A different Shared FCC can fill the same slot, while another Private
owner cannot. Fake method statics stay owned by the original method; private
fake cleanup queues cache-free then its actual This-only children.
Explicit wrapper/pending invokes do not gain owning-default authority from a
warmed slot; their ordinary non-Deprecated scalar route is separate.

Ordinary named-class constant initializers read owning global dependencies
through their actual declaration and pending binder. Selected lookup facts
preserve object/Closure identity after namespace shadows and callback cleanup;
the request's class-cache row owns the delivered value. Type validation precedes
publication. A real begin-history cut authenticates nested fills: an untyped
outer initializer can replace a child's row, while a failed typed outer leaves
that row intact. Nonowning write facts and old-row snapshots preserve earlier
compiler prefixes. Inline values and exact permanent global donors retain their
existing snapshot route. Computed arrays instead retain readonly images of
keys, values, nested classes and append metadata. Foldable images reconstruct
only in a temporary compiler view; retired Closure leaves stay opaque and do
not become live compiler values. No historical field adds a heap root.

Actual replacement stages old-value release before new publication. The old
slot is unreadable and contributes no cache root during release; existing
destruction jobs own its remaining children. One publication task protects the
new value through callbacks, including another class's lazy initialization.
The image serves earlier compiler prefixes even while release is pending.
Normal completion publishes once and restores the real initializer context.
Abrupt old-child cleanup remains explicit Unsupported. The pinned native
throwing-child original timed out after `H|F|D|`; it establishes no terminating
catch or publication law. These class-cache rules leave static-property/Trait
initialization and held Generator/303 release routes separate.

Ordinary named-class deferred static-property defaults now receive existing
owning globals through their real binder and declaring `CLASSSTATICS` cell.
Selected lookup facts include array identity, preserving the original value
after namespace shadowing. Reentry can fill or assign the mutable cell first;
the checked outer bind preserves first-fill and escaped typed-reference laws.
Handler throw or exit before binding skips that commit. Global object and
Closure aliases retain their existing identity and scope.

Normal replacement removes the old cell edge before release. A nonowning marker
makes the slot unreadable while one publication task protects the new value.
Publication follows completion of the old-item release; shared or escaped old
values can survive. In the unique old Drop case, real This/C pins last through
its destructor and storage drops before commitment. Other-property lazy
initialization remains available during that callback. Same-slot reads, quiet reads, writes and reference fetch/bind
during release refuse explicitly. Old-release abrupt completion, Trait,
Generator/303 and wider construction/producer domains remain separate.

Ordinary named-class instance defaults receive owning globals through the actual
`INSTANCE_DEFAULT_BIND` and class template before object allocation. Frozen
lookup facts retain the selected value across handler shadowing; each later
object gets its own property edge, with normal array COW and shared object
identity. A child copies the parent's value at its actual link cut. Binding
records name their genuine write event; later owning or legacy writes cannot
authorize an earlier child snapshot.

Current templates and pending publication tasks own their values. Historical
records remain valid after a computed container and its Closure retire, without
adding roots or dereferencing retired storage. Normal replacement releases the
old template edge while one task protects the new value, then publishes after
that release completes. A destructor of a value released from the unique old Closure's static storage
can initialize another class during cleanup. Busy same-template construction/linking and
old-release abrupt completion remain Unsupported. Construction, producer,
Trait/Generator/303 and the other held boundaries are unchanged; no class-cache
image or new Closure identity is introduced.

Fixed-name ordinary public USER constructors receive omitted owning defaults
after class-template initialization and actual receiver allocation. The live
method target, receiver/scopes and matching caller `CTOR_RESULT` authenticate
that recipient. Existing Shared function/default-origin caches compose with
explicit `__construct` and inherited calls; formal/cache publication precedes
TypeError, and normal promotion adds its ordinary property owner. Closed receive
history keeps genuine source/scopes/publication, without retaining or looking
up the former receiver.

Automatic construction failure suppresses the user destructor even for escaped
`$this`. Deprecated-handler and ordinary body exits preserve that flag before
receiver/result roots unwind; explicit `__construct` keeps ordinary method
semantics. These bounded hooks add no owner, schema field or unwind framework.
Anonymous and default-AST `new` entry protocols,
nonpublic/Generator/wider signatures and existing held families remain separate.

Initialized statically named CV class strings now use the existing dynamic-new
selection captured before allocation and argument sends. Live reception requires
the immediate caller's matching `CTOR_RESULT` and `DYNAMIC_NEW_FINISH`; a receive
birth copies that nonowning selection for closed history. Rebinding or clearing
the CV does not change the selected class, and history reads no retired receiver.
Different named subclasses can share one inherited constructor/default cache
without sharing their per-entry class receipt. Leading slash/case spelling and
the existing failed-construction exit behavior are preserved.

Existing by-value CV reads retain ordinary alias dereferencing. This adds no
reference acquisition, reference-result selector or paused protocol. Object,
temporary, undefined, anonymous and autoload selection modes remain
separate; the selected runtime class and constructor owner must both be named.
The [class-string review](../../coverage/semantics/deprecated-class-string-constructor-default-review.json)
records four originals and 70/73/53 independent strict459 conditions.

Ordinary named method factories also admit `new self`, `parent` and `static`.
The same receipt keeps the factory's lexical/late-called scopes separate from
the constructor's owner/selected class. Live checks use the immediate saved
factory frame; closed checks use its genuine call history and publication cut,
without reading or retaining the former factory receiver. Self/parent selection
alone cannot authenticate a changed factory late-called scope. Nested calls may
share the inherited constructor cache while keeping distinct selections; a
selected parent requires the child's existing cache-entry proof.

This finite route uses ordinary named nongenerator by-value method factories,
named factory-called/selected classes and public constructors. Captured factories,
service main-code, Trait/Generator and wider entry modes remain separate. Existing
promotion and failed-construction exit behavior add no new lifecycle rule.
The [keyword review](../../coverage/semantics/deprecated-keyword-constructor-default-review.json)
records four originals and 63/63/52/23 independent strict460 conditions.

Public ordinary instance/static methods also admit initialized CV string member
names. INIT selects the function before later arguments and rejects nonstring
names before entry. The actual ordinary target, receiver/scopes and public source
descriptor authenticate live reads and cache hits. Existing captured call history
and publication cuts identify the function after name or receiver retirement;
neither current CV contents nor retired receiver storage is consulted.

Shared cache identity remains the function/default origin. Case aliases and
inherited called classes can share it, while different methods at one site keep
their own slots. No raw-name witness, new owner or schema field is needed. Existing
ordinary CV aliases retain their read behavior. The static class operand is a
literal/keyword Name; dynamic class expressions, nullsafe/callback/captured,
nonpublic/magic/Generator and wider name/signature modes remain separate.
The [CV method review](../../coverage/semantics/deprecated-cv-method-default-review.json)
records four exact normal originals and 55/57/56 independent strict461 conditions.

Ordinary public method shutdown callbacks now receive owning defaults from their
genuine registry entry. The callee keeps an absent callsite and line -1; registration
source is separate. Exact entry/target/ARGS/SENT and public function/scopes checks
protect current reads and hits. A four-field nonowning receive witness captures
the index, registration source/line and selected target. Closed proof uses immutable
function/scopes/publication; it reads no retired receiver, arguments or registry
row. The saved index is descriptive after final cleanup resets the queue.

String, class-array and object-array callbacks include compatible ordinary implicit
This. Registry receiver/argument ownership and borrowed This remain unchanged.
This finite route uses fixed registrations with neutral capture/producer metadata
and existing public nongenerator by-value methods. Closure/raw invokable-object,
captured/private/magic/Generator and wider modes remain separate. Parent cache
reuse requires the child's real entry proof. Five normal originals and 86/78/83
strict462 conditions are recorded in the
[shutdown review](../../coverage/semantics/deprecated-shutdown-method-default-review.json).

Ordinary public method error and exception handlers receive owning extra defaults
through their genuine API entry. Error handlers receive four arguments at the
original diagnostic site; exception handlers receive one Throwable with no callee
site. A nonowning kind/selected-producer witness preserves closed Shared-cache
authority after callback cleanup. Borrowed This stays rootless; existing raw
callback, formal and original-Throwable owners remain intact. Four normal originals
and 252 strict463 conditions pass. The type case preserves one builtin default-read
deprecation before two caught TypeErrors, with no handler body entry.
[Handler review](../../coverage/semantics/deprecated-handler-method-default-review.json).
This slice admits existing string and direct class/object-array public named-class
nongenerator by-value methods with plain internal producers. Closure, raw invokable,
scope/binding/clone producers, nonpublic/magic, by-reference/variadic and Generator
entries remain separate. Existing handler throw/exit machinery is reused; no new
general failure campaign or callback lifecycle is claimed.

Ordinary public autoload methods receive owning extra defaults after their one
class-name argument. The exact saved autoload request and selected callback
authenticate implicit lookup sites and explicit calls with no callee site.
The registry owns the receiver while registered; the known-function invocation
borrows This. A warning handler can unregister and clear the last alias, letting
the receiver die before the loader body. Immutable selected-target metadata still
validates the name/default body and an ordinary class-publication helper; actual
retired This, scoped and capture consumers remain explicitly held.
Closed default authority uses the existing own-index-zero autoload snapshot;
deeper snapshots authenticate callers. Warning publications preserve the exact
shifted snapshot list. Existing string carriers reach explicit dispatch through
their bytes, retaining the original argument record. Four normal originals and
258 strict464 conditions pass; no new birth field, cache key or global root rule
is introduced. Capture/producer/Closure/nonpublic/magic/Generator and wider held
modes keep their boundaries.
[Autoload review](../../coverage/semantics/deprecated-autoload-method-default-review.json).

Ordinary public tick method callbacks receive owning extra defaults after their
registered arguments, with no implicit runtime argument. The actual marker site
and saved selected entry authenticate current use; nonowning marker/target history
keeps closed Shared-cache authority after unregister and receiver cleanup. Registry
receivers and copied arguments retain their existing owners; current This borrows.
Active unregister raises Error while retaining the calling row. Cache/formal
publication precedes type rejection, and a warm second marker creates no birth.
Four normal originals and 259 strict466 conditions pass. Attribute planning is limited to single no-argument
Deprecated donors while ticks are inactive (`FREQUENCY=0`).
Closure/capture/producer/private/magic/Generator and wider signatures remain held.
[Tick review](../../coverage/semantics/deprecated-tick-method-default-review.json).

Ordinary named USER string callbacks use the same extra-default path in error,
exception, shutdown, tick and autoload entries. Full entered-context proof authenticates
the real supplied argument count and diagnostic, marker, lookup or absent site;
no source-call syntax is invented there. Existing witnesses borrow the selected
function and publication, preserving closed authority after raw handler/registry
changes without reading retired argument or Throwable storage. Ordinary direct
children keep their source-selection proof and Shared function/default identity.
Named and method/Closure publication proofs remain disjoint. The only autoload
cut change reuses the existing exact shifted-history law. Six normal originals
and 343 strict467 conditions pass, including actual cold shutdown and nested
inner9→outer[] publication. Only undecorated nongenerator by-value nonvariadic
named functions selected by strings/carriers are admitted; existing held modes
and all receiver, cache, argument and Throwable ownership laws remain unchanged.
[Named callback review](../../coverage/semantics/deprecated-named-callback-default-review.json).

Initialized quiet callable CVs containing ordinary public method strings or
class/object arrays receive owning defaults through their real selected wrappers.
Argument callbacks can replace the source array/name without changing the selected
function or cache. Nonstatic This retains its normal owner; static selection can
continue after the source object retires. A borrowed raw-ingress bit preserves
closed source kind and keeps existing method-Closure ENTRY proofs mandatory,
including same-site nested children. No raw value or receiver is retained for
history. Five normal originals and 342 strict468 conditions pass; keyword/magic,
Closure/API and wider held invocation modes gain no new admission.
[Raw callable review](../../coverage/semantics/deprecated-raw-callable-default-review.json).

Literal-member nullsafe calls on initialized non-This receiver CVs receive
owning defaults only after the live ordinary public target is selected. The null
branch skips argument/default evaluation and the body. Instance This retains its
normal owner; static selection can continue after the source object retires.
Captured function/scopes and explicit nullsafe declaration/publication proof
validate closed history without a new witness or receiver lookup. Four normal
originals and 281 strict469 conditions pass, including inherited cache separation,
repeated TypeErrors and one static-binder continuation check. Wider/held entry
modes remain separate.
[Nullsafe review](../../coverage/semantics/deprecated-nullsafe-default-review.json).

Literal-member static calls through initialized quiet class CVs receive owning
defaults after existing string or ordinary-object normalization selects a published
named class. Arguments may change the CV; the normalized target preserves the
original function/called scope and Shared default cache. Source-object retirement
can precede binding/body because static invocation adds no owner. Captured
function/scopes and effective public static descriptor/publication certify history
without the former CV, raw spelling or heap. Four normal originals and 282 strict470
checks pass. Wider selectors, nonstatic/captured/held entries and conversions stay
separate; the normalized selector does not prove string-only input.
[Class-value review](../../coverage/semantics/deprecated-class-value-default-review.json).

Public constants in named interfaces accept existing owning global values through
their physical field3 source declaration. Inherited interfaces and implementers
resolve the same declaring descriptor/cache. Existing normal replacement retires
a computed old array before publication;183 compiler projections preserve earlier
eval reads. Global Closure aliases retain identity and original lexical context,
while typed outer failure preserves a child value already published during reentry.
Four normal originals and 281 strict471 checks pass without changing shared
183/184/465/466, state fields or root laws. Wider attribute groups, Traits, enums,
new producers and old-release abrupt completion remain separate.
[Interface review](../../coverage/semantics/deprecated-interface-constant-review.json).

`#[Deprecated]` on a public named-class or named-interface constant has a separate fetch protocol.
Both folded-pool and warm-cache imports, and same-unit constant facts, refuse
substitution so compilation cannot erase the notice. The pending notice carries
no selected value or initializer history; acquisition follows successful handler
return. Existing scalar formal-default caching still avoids a second fetch.
[Class-constant notices](../../coverage/semantics/deprecated-class-constant-fetch-review.json).
A single such attribute can also apply to a multi-item public group in a named
class/interface. The ordinary item compiler receives the original list after one
attribute preprocessing step. Member indices and initializer origins stay
distinct; existing notice guards, compiler vetoes and owning cache facts work per
declaration, including an owning second sibling beside a folded first one.
[Multi-constant groups](../../coverage/semantics/deprecated-multi-constant-group-review.json).
Keyword class-constant fetches in ordinary public method bodies now authenticate
the normal current function/target and actual body source before reusing the
notice task. Existing lexical, parent-link and called-class selection remains
independent of declaring cache identity. Cold static reads and constructor-warmed
parent reads retain their different entry states and normal ownership. Default,
Closure/fake/borrowed/wrapper and contextual API modes remain separate.
[Keyword fetch notices](../../coverage/semantics/deprecated-keyword-class-constant-review.json).
Named-class protected/private noarg Deprecated groups reuse the same ordered
compiler and source facts. Recognition agrees with source flags but does not grant
caller access: actual fetch and pending-notice validation enforce visibility.
A global handler cannot read a private constant merely because its outer notice
is protected. Existing487 source eligibility still serves authenticated updates
and history; source-wide compiler/query refusal and public API selection stay
unchanged. [Nonpublic source/access](../../coverage/semantics/deprecated-nonpublic-class-constant-review.json).
Quiet nonempty Deprecated message/since fields now use the same real declaring
context and existing literal/null parser for named classes and public interfaces.
Exact source argument paths receive metadata pool classes without operand emission;
they confer no runtime initializer authority. A text hook preserves the old message
by default and serves literal/API dispatch and their error validators. Reordered
fields, private access, empty/null suffixes and declaration-versus-reader imports retain their own checks.
[Constant message fields](../../coverage/semantics/deprecated-class-constant-message-review.json).
Quiet initialized class CVs with literal members reuse normal string/object
normalization. The new notice source proof requires a compiled fetch, canonical
published named request and public recognized declaration. Its current normalized
RESULT and saved current-head tuple are separate authorities; a mismatched tuple
cannot borrow RESULT, and resumed validation reads no mutable CV/object storage.
No task, root or history record is added. Existing nonfolded initializer laws are
unchanged; the new native/state fronts use folded values.
[CV notice source](../../coverage/semantics/deprecated-cv-class-constant-review.json).
Literal class names with quiet member CVs preserve the old strong class-source
proof. Existing184 resolves the member and consumes its member/capture pair before
fetch; current authority is the member string RESULT, not493's class RESULT.
The unchanged decoder authenticates the saved tuple after dispatch, including
member unset and nested same-declaration protection at a different source line.
This late-only source rule adds no task/root fields, initializer or lookup modes.
[Member notice source](../../coverage/semantics/deprecated-cv-member-constant-review.json).
Dual class/member CVs authenticate the genuine member/capture pair before184
consumes it. The default forwarding path is the old member-value call; its abrupt
rule is unchanged. Factored483 dispatch preserves both old bodies and requested
message-class arguments. The new source arm validates pair/origin/line/tail, then
uses that dispatch, which creates the sole saved notice. Closed notice validation
is exact tuple-only, without current RESULT or CV/object reconstruction.
[Dual CV entry](../../coverage/semantics/deprecated-dual-cv-constant-review.json).
A single late clause covers scoped-keyword/CV-member reads in the existing
ordinary public method-body domain. The old method scope/selected-class proof
and current-byte/saved-head member decoder remain authoritative, without another
capture, forwarding change or input reread. Existing initializer bounds remain.
[Keyword member source](../../coverage/semantics/deprecated-keyword-cv-member-constant-review.json).
The compiled-member source law requires true child code and the exact FIELD1
PSTRING pool value, alongside a false whole FETCH. It preserves Deprecated result
substitution vetoes while accepting existing folded member expressions. No mutable
RESULT, new receipt or broader compiler folding is used.
[Compiled member authority](../../coverage/semantics/deprecated-pooled-member-constant-review.json).
Compiled class-string sources reuse FIELD0 and the old exact literal selector,
including raw spelling after one-prefix normalization. Hidden FIELD0 cannot use
the generic published-target fallback. Identifier(eps) and expression-member pool
proofs remain separate; no class/member CV or mutable RESULT authority is added.
[Compiled class authority](../../coverage/semantics/deprecated-compiled-class-constant-review.json).
Effectful member calls require false FIELD1 code, a resolved Name with no fallback,
zero sent/formal parameters and the existing physical USER-function/selection
certificate. The function has already returned before current member capture;
resumed validation reads its immutable metadata and exact tuple, not the mutable
return-source or body. [Member-call authority](../../coverage/semantics/deprecated-call-member-constant-review.json).
The rvalue consumer instead authenticates false child/whole code, fixed named
class source and the real adjacent member/capture tasks. It receives the original
known string operand before resolution can hide a reference, uses existing string
carrier validity, and validates saved notices only through their exact tuple.
An immutable source-shape exclusion preserves every old named zero-argument call
route and refusal. Producer evaluation, return/cleanup and held gates are unchanged.
[Rvalue authority](../../coverage/semantics/deprecated-rvalue-member-constant-review.json).
Class rvalues use a separate neutral normal continuation before literal-member
fetch. False FIELD0/whole code and the real class task authenticate the source;
the original known string maps through existing normalization to the canonical
request. Saved notice validation is exact-tuple-only. This adds no producer,
reference-return, task/root or image representation.
[Class-rvalue authority](../../coverage/semantics/deprecated-rvalue-class-constant-review.json).
Composed runtime class/member expressions need one acquisition-kind marker:
normalization and member evaluation otherwise erase the original string domain.
It stores only site/canonical class/line and adds no owner. A genuine exact triple
and original supported member rvalue grant entry; source-only marker validity
also permits existing abrupt cleanup and grants no notice by itself.
[Composed-rvalue authority](../../coverage/semantics/deprecated-rvalue-class-member-constant-review.json).
For quiet class-CV sources, existing string/object acquisition already explains
the canonical pair. A completed nonvariable false-code member uses original-
operand validation and exact saved-tuple authority without another kind marker.
Existing loader-resumed CV construction remains possible under unchanged 277
bounds; later publication alone is not a direct-loaded certificate. These new
natives use directly published classes/interfaces.
[CV-class/member authority](../../coverage/semantics/deprecated-cv-class-rvalue-member-constant-review.json).
Scoped runtime members use existing490's ordinary-method body/current-target
certificate and the actual caller Fn.CODE FIELD1, independently of the completed
member producer's metadata. Strong self/parent/static selection and the real old
pair precede dispatch; saved validation restores the original CURRENT and checks
the exact tuple. Existing acquisition, root and contextual API bounds remain.
[Scoped-member authority](../../coverage/semantics/deprecated-keyword-rvalue-member-constant-review.json).
Compiled-class/runtime-member reads combine immutable FIELD0 class proof with
original-member completion at the real pair. The class stays literal, so member
effects may publish it before lookup; current canonical publication cannot replace
the exact raw compiled string. Existing checked eval/publication and source-image
validation remain literal, with no new class receipt or loader assumption.
[Compiled-class/member authority](../../coverage/semantics/deprecated-compiled-class-rvalue-member-constant-review.json).
The existing computed-fetch source proofs now reuse visibility-matched Deprecated
metadata and caller access for all admitted constant visibilities. Removing thirteen
PUBLIC-only premises changes no compiler, acquisition, tuple, root or API contract.
[Computed access authority](../../coverage/semantics/deprecated-nonpublic-computed-constant-review.json).
The interface source decoder uses member field3 and reuses those same compiler
vetoes, notice task and declaring cache across interface/implementer aliases.
[Interface notices](../../coverage/semantics/deprecated-interface-constant-fetch-review.json).
The `constant()` scalar consumer preserves its captured query through a notice
before acquiring a folded, cached or deferred value. It reuses the existing
initializer/fact/cache laws and does not bypass the compiler vetoes or add owning
initializer authority. [API notices](../../coverage/semantics/deprecated-class-constant-api-review.json).
Folded literal-array API results also reuse the existing pool/tree checks after
the notice. Their caller and handler COW copies leave the permanently pooled
source intact; deferred owning initializer admission remains separate.
[Array API results](../../coverage/semantics/deprecated-class-constant-array-api-review.json).

The exact noarg Deprecated class/interface source now also authenticates
nonfolded owning-global reads through its declaration/initializer-child path.
Class protection has cleared before the initializer global notice. Existing
lookup facts, strict type checks and normal cache replacement preserve selected
array/Closure identity, retry and child publication. This source-only gate also
feeds existing authenticated update consumers; it adds no construction or root
protocol. Wider owning API initializer forms remain separate.
[Attributed owning initializers](../../coverage/semantics/deprecated-owned-class-constant-notice-review.json).

For an untyped fully resolved direct global name, the same API now receives the
actual supported owning USER donor. Cold selection reuses the ordinary binder;
warm selection requires donor value/class equality and genuine cache publication
history. Query rebinding cannot retarget the captured call. A nested literal fill,
caller array COW and inherited global Closure aliases retain their existing owners
and identities. Primitive classifiers, scalar/folded routes, notice protection and
initialization visited rules are unchanged. Computed and wider producers remain
separate. [Owning API results](../../coverage/semantics/deprecated-owned-class-constant-api-review.json).

Source-only primary/fallback donor checks still protect hits, including cached
scalars before a later owning donor, and post-handler binds. Folded children and
nested Closure bodies acquire no read authority.
Unknown identities and wider defaults remain core work. The ordinary `Closure::call` path
does not admit fake method sources, Closure receivers or held Generator,
captured-entry and pending/iteration families.

Arrow and wider fake/nonpublic recipients, by-reference parameters/returns/captures,
variadic and Generator Closure recipients remain separate. Trait and wider dynamic
method/callable recipients, plus wider class-constant and property initializers,
retain their separate boundaries. For parameter-default causal paths, the bounded
handler producer remains fixed primitive `define`; namespaced fallback `define`
is Unsupported there. Scoped builtin/trait warning cuts
are outside this increment. Existing scalar default routes
remain paired. Function-local dynamic static initializers use ordinary opcodes.
Converted queries, trait collision folding, wider metadata and reflection remain
separate. Attribute argument paths acquire no runtime initializer authority.
Generator-close release of an already warmed scoped value is held; the ordinary
private-cache marker law does not extend the separate303 close path.
[COMP183 evidence](../../coverage/semantics/deprecated-global-constant-review.json).
[COMP184 cancellation](../../coverage/semantics/deprecated-handler-cancellation-review.json).
[COMP185 owning reads](../../coverage/semantics/deprecated-owned-constant-review.json).
[COMP186 parameter defaults](../../coverage/semantics/deprecated-parameter-default-review.json).
[COMP187 method defaults](../../coverage/semantics/deprecated-method-default-review.json).
[COMP188 Closure defaults](../../coverage/semantics/deprecated-closure-default-review.json).
[COMP189 bound Closure defaults](../../coverage/semantics/deprecated-bound-closure-default-review.json).
[COMP190 private Closure caches](../../coverage/semantics/deprecated-private-closure-default-review.json).
[COMP191 ordinary Closure::call defaults](../../coverage/semantics/deprecated-closure-call-default-review.json).
[COMP192 direct scoped Closure defaults](../../coverage/semantics/deprecated-scoped-closure-default-review.json).
[COMP193 public method FCC defaults](../../coverage/semantics/deprecated-method-fcc-default-review.json).
[COMP194 class-constant initializers](../../coverage/semantics/deprecated-class-constant-owned-review.json).
[COMP195 computed cache replacement](../../coverage/semantics/computed-class-cache-replacement-review.json).
[COMP196 static-property defaults](../../coverage/semantics/deprecated-static-property-default-review.json).
[COMP197 instance-property defaults](../../coverage/semantics/deprecated-instance-property-default-review.json).
[COMP198 constructor defaults](../../coverage/semantics/deprecated-constructor-default-review.json).

The initializer uses ordinary source expressions and the existing unit code and
constant pool. Successful folded child values remain pool owners even when a
parent fold makes their execution unnecessary. Non-owning `PCCLASS` companions
carry the allocation provenance explained in [constant value classes](CONSTANT-VALUE-CLASSES.md).
Runtime integrity projects declaration names, lines and compiled pool class
descriptors from checked source, including units without function declarations.
Runtime value/class tags and topology are checked without reconstructing values.
A missing or duplicate descriptor is not a PHP error or successful execution.

Compiler889/cb31d858 retains 45 exact native compiler phase comparisons, ten
explicit pending legal forms and29 declaration assertions. A separate40-source
class gate checks120 descriptor assertions alongside native lint. Existing
constant-context42+5, source-context233 prefixes and additional controls, and
magic48/context regressions pass on the same frozen bytes. Historical887 and
its initial line/import failures remain separate; test setup failures and the
incorrect float-cast class expectation are retained rather than reclassified.
The float-to-string cast still follows existing45's deferred policy.

Authority: PHP8.5.10 source34308a6666b2d489c509541ea9befea9e2b42348,
`Zend/zend_compile.c` constant declarations and constant-expression folding;
`Zend/zend_constants.c` registration; `Zend/zend_vm_def.h` DECLARE_CONST.
