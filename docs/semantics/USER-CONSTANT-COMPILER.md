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
Anonymous, keyword-specific and default-AST `new` entry protocols,
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
temporary, undefined, keyword, anonymous and autoload selection modes remain
separate; the selected runtime class and constructor owner must both be named.
The [class-string review](../../coverage/semantics/deprecated-class-string-constructor-default-review.json)
records four originals and 70/73/53 independent strict459 conditions.

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
