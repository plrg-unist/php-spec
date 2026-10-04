# Source methods and constructors

Modules 141/142 extend named source classes with instance methods and
constructors. The nonpublic-method milestone adds protected/private instance
access and declaring-class private identity. The static/scoped milestone adds
static declarations and scoped calls. The target remains PHP 8.5.10 CLI NTS 64-bit
under the ordinary profile. The [public-method review](../../coverage/semantics/methods-review.json)
and [nonpublic-method review](../../coverage/semantics/method-visibility-review.json)
bind separate native sources, compiler projections and paused ownership checks;
these are bounded observations, not complete class semantics.

[Source trait composition](SOURCE-TRAITS.md) imports method bodies into distinct
using-class and alias identities, preserving source provenance and inherited cells.

## Descriptors and dispatch

Class-owned method descriptors retain their declaring origin, signature, body,
modifiers and source context. They never enter the global function registry.
Compilation preserves member order and diagnoses modifier/body/redeclaration
errors before later members. Linking checks final methods, nonprivate override
variance, inherited abstract obligations and constructor-specific exceptions.
Constructor signatures are unconstrained by ordinary concrete parent constructors;
abstract constructor prototypes remain constraints.

Protected lookup compares the caller scope with the root nonprivate prototype,
so siblings in that family may call an overriding method. An ancestor method's
own private declaration stays separate from a child's same-name method. A call
executed in that ancestor's lexical scope selects its private declaration on a
descendant receiver; an unrelated or child scope cannot acquire that access.
Private nonabstract methods other than constructors impose no override
signature, finality or visibility requirement on child declarations. A final
private method emits PHP's warning; a final private constructor still forbids
an overriding constructor. A nonabstract parent constructor permits a child
constructor to change visibility and signature, while abstract constructor
prototypes retain both checks. Visibility denial occurs before argument
evaluation for ordinary and nullsafe calls and before constructor arguments.
Selected call tasks and entered/saved contexts authenticate the declaring
origin against the receiver, executed caller scope and source call site.
Error traces name an inherited source method by its declaring class and
declaration spelling, while calls retain the runtime receiver separately.

Static descriptors retain their declaring owner and static flag. Linking rejects
static/nonstatic override mismatches after final checks and before visibility
and abstract mismatch checks. A constructor cannot be static. `A::f()`, `self::f()`,
`parent::f()` and `static::f()` resolve through the selected class, while
`self`, `parent` and `static` forward the active called class. An explicit
class name sets the called class for static methods. A nonstatic scoped method may
reuse the active `$this` only when it is an instance of the requested class;
its called class is then the receiver's class. Visibility is checked before
arguments. A literal `__construct` call uses Zend's constructor arm, including
its receiver-class private check; a variable method name follows ordinary
method lookup. Parser-foldable string concatenation of `__construct` also
uses that arm. Class expressions resolve their type and lookup before a
computed method name; literal class lookup follows the computed name.

Scoped selected tasks retain requested, declaring and called class origins,
the genuine receiver, and the captured class selector. An object class selector
normalizes to the canonical class name before computed-name evaluation; ordinary
owners determine its lifetime. Direct calls use `STATIC_METHOD_TARGET` after
selecting a static descriptor, retaining class identity without an object root.
Source checks revalidate class identity, receiver, visibility and forwarding
context after selector retirement. A fully correlated forgery of a
completed dynamic class string or method name and all matching target origins
cannot be reconstructed from the admitted paused state; the protocol records
this limit explicitly.

First-class source method expressions capture after receiver, class and method
selection, before any argument send or method entry. Capture checks visibility
at that point and stores the selected declaring descriptor, called class and
nonstatic bound receiver in an owned `Closure` object. Rebinding the source
variable does not change that receiver. Static captures retain their called
class without retaining an object class selector. A fetched direct receiver
stays owned through computed-name evaluation until static selection releases
that temporary owner. Invocation uses the
captured method body and shared declaring-origin static cells. Its trace frame
names the declaring class and method directly, with `->` for nonstatic methods
and `::` for static methods, without an extra `Closure->__invoke` frame.
Literal source selectors and method names, executed class selection, visibility and
live captured receiver are rechecked in paused tasks and closure rows. As with
scoped calls, a correlated substitution of a completed dynamic selector or
method name cannot be reconstructed after its expression has returned.

Ordinary and nullsafe calls evaluate receiver and computed name in the pinned
order. A CV receiver can be read after name effects; a fetched property receiver
already denotes its value. Null skips the active nullsafe chain before names and
arguments. Receiver-bearing targets own their receiver throughout argument sending.
Calls reuse the positional/named/unpacked/variadic and reference protocols.
Construction allocates before arguments, calls the effective inherited constructor,
and retains the new object independently of the constructor's ignored return.

Contexts distinguish closure identity, receiver, lexical class and called class.
Current and saved contexts require `INSTANCE` to match their selected target;
static and ordinary method calls have no closure instance identity.
`$this`, `self::class`, `parent::class`, `static::class`, `__CLASS__` and `__METHOD__`
use those channels. Explicit closures/arrows inherit applicable class context and
nonstatic receivers; named nested functions clear it. The sparse `CLOSURESCOPES`
table is source-authenticated and follows live closure ownership. Inherited
method statics share declaring-origin storage; overrides have distinct storage.

## Object invocation

Bare source-object calls and object first-class conversion select effective
runtime-table `__invoke` without a visibility check. Private/protected methods
retain their declaring owner, runtime called class and real receiver. An Owner
method's bare call selects a Child override even when explicit `->__invoke`
from that lexical frame selects Owner's private declaration. Ordinary explicit
method calls and captures retain ordinary visibility checks. Named array/string
selectors use the separate lexical access rules below.

A dual-role Stringable object uses the selected `__invoke` without a string cast.
[Callable/string parameter reception](../../coverage/semantics/callable-string-current-review.json)
admits these nonstatic invokable objects before weak conversion in either union
order. Weak/strict, typed by-reference parameter and unpacked controls retain
receiver ownership. Modules95 and the return bodies are unchanged; shared
ordinary by-value callable return classification inherits the lookup change
without a new return target, agreement or paused-return validation.

Compilation processes method parameters/body before magic-method validation.
Static `__invoke` is fatal at that point and emits no nonpublic-visibility warning;
a private-final begin warning can precede that fatal. Nonpublic `__invoke` warns
at publication even in an unexecuted declaration, while ordinary inheritance
access compatibility may subsequently reject the class. Delivery of these
warnings to already registered handlers during include/eval remains separate.

Selection authenticates evaluated source operands before argument effects and
keeps the selected receiver independently of changed CVs. Bare-object capture,
clone and later calls retain source certificates, owner/called scopes and shared
method cells without a new carrier. Bare-object error handlers use the same
lookup, preserving genuine ARG4 and strict USER versus weak direct-API reception.
The [publication review](../../coverage/semantics/invoke-publication-current-review.json)
binds separate source, compiler/runtime, independent and current truth-warning
checks, including original failures. Earlier public invocation evidence remains
in its [ledger](../../coverage/semantics/source-invoke-current-review.json).
Transformed weak wrappers, wider magic protocols and native-only lifecycle
observations remain outside these selected agreements.

## Public source method arrays

Module205 shares structural resolution between callable admission, dynamic calls
and first-class conversion. Arrays require exactly integer keys0/1 regardless
of insertion order; members are dereferenced before class/method lookup. Public
concrete source instance/static methods retain declaring owner and called class.
Method lookup uses full bytes and case folding, without Stringable conversion or
NUL truncation. Known-invalid arrays reject before argument effects; unavailable
services remain explicit Unsupported.

Class-string nonstatic admission uses the receiving method's lexical scope and
active receiver. It can admit a parent descriptor on a child even when the child
has overridden that method. This truth-only result does not create a dispatch
target: direct dynamic class-string calls still reject nonstatic methods.

Selection stores the chosen descriptor, source site/lines and requested/called
class or instance receiver. Later argument effects cannot replace that choice
by changing either referenced array member. Instance targets own only the selected
receiver; static selection keeps class identity, and ordinary owners determine
the original object's lifetime. Array-origin Closure
objects preserve that certificate, clone scopes and method static cells without
retaining the original array, maker or temporary creator. Captured static methods
also pass through the existing Closure PIPE route. Broader binding/Closure
consumers and arbitrary retired dynamic binding history remain separate.

The [array review](../../coverage/semantics/array-callables-current-review.json)
binds distinct private author29/seven249 and independent17/five217 observations,
plus one fresh current publication/Restore/property/ARG source and its corrected
finite witness/100. A separate current INI option/value witness checks the selected
Owner/Child argument frame, two original callback operands and converted-option
value rejection, with full raw mutation and cleanup. Unsupported controls and
original failures stay separate; ordinary
`$GLOBALS` behavior remains partial. Deprecated keyword/compound API admission is
described below; magic/autoload/internal resolution and full callable closure remain open.
Shared ordinary type classification adds no new return agreement or paused-return
validation.

## Public class-method strings

Module210 resolves ordinary public concrete source method strings using the
full byte sequence and the pair preceding the final colon. It preserves one
leading class slash, case folding and registered function-string handling.
NUL bytes are never truncated during lookup. Known lookup errors precede
argument effects; services outside the selected scope remain Unsupported.

Computed strings dispatch and capture only static methods. Fixed names from
the existing compiler projection may select a compatible active receiver,
including the requested parent descriptor when the child overrides it. Callable
parameter admission instead uses the receiving lexical scope and receiver;
its truth-only result never invents a dispatch target.

Selection authenticates source form, site/lines, full original bytes and exact
requested descriptor. Direct fixed calls and conversion bind the producer's
actual receiver. Captures retain that selected receiver independently of later
callers or retired makers. Clone, nominal Closure typing, invocation, deferred
defaults and method static cells reuse the existing protocols. Static captures
also use the selected Closure PIPE route. A selected INI source/state check
preserves saved arguments, both normalized callback operands and the static
`::` error trace before value rejection and raw mutation cleanup.

The [string review](../../coverage/semantics/class-method-strings-current-review.json)
keeps original source/state observations distinct from Unsupported controls.
Keyword/compound names, magic/autoload/internal resolution, binding and transformed
Closure consumers remain open; lexical access is described below. StaticCall reference RHS acquisition
with untyped return signatures now preserves selected lexical/called scope and
typed static cells through97/99. Nullsafe class chains reject before ordinary or FCC
lowering; first-class call results reject in reference context. The
[reference review](../../coverage/semantics/static-method-reference-review.json)
also checks discarded genuine reference getters: typed slots acquire an alias
before return, while ordinary by-value getters leave them raw. It does not close
deferred property defaults or references into incomplete class-constant tables,
broader temporary-return Notice timing or typed return verification. Legal untyped
static-slot getters preserve ignored raw values and used shared aliases across
public/protected/private lexical reads. Ordinary non-FCC StaticCall results retain
their result kind for direct by-reference sends: genuine references share the
static cell, value results use the existing Notice/fresh-cell route, and first-class
callable results reject. Wider dimensions/list/wrapper consumers remain open.
Shared ordinary type classification adds no paused-return validation.

First-class compilation clears only the completed result fold after callee
selection. Constant-array callees retain their pooled child descriptors while
the runtime expression produces a Closure. The preserved independent failure
exposed this compiler bug; its unchanged57 checks pass after the119 repair.
The current named-handler source and corrected100 state retain Owner/Child,
saved ARG1/7, normalized handler ARG4 and exact trace materialization. A local
fixture seek mirrors the evaluator's Throwable transitions; its original
failure remains separate and receives no finite credit.

## Closure invocation and ownership

`Closure->__invoke` and its nullsafe/computed forms route real and named closures
through the same selected-callee protocol. SEND uses the underlying parameter
names/reference/variadic flags and reports reference errors as `Closure::__invoke`.
The underlying callee receives weakly; its body and return retain their own strict
mode. The optional call-context `WRAPPER` owns original sent slots and named extras
before defaults/coercion. Holes stay holes, references stay aliases, and copied
array values participate in ordinary COW ownership.

Errors after entry capture the callee frame followed by `Closure->__invoke` with
its original operands; holes render as NULL. SEND errors precede this frame.
Current and saved contexts root wrapper operands until return/unwind. Intrinsic
exit/die closures retain their separate intrinsic binder, weak internal RECEIVE,
extra wrapper trace and terminal cleanup. Diagnostic names containing NUL bytes
use native C-string display while lookup and argument identities retain full bytes.

## Validation and remaining scope

The [selector repair review](../../coverage/semantics/method-class-selector-review.json)
keeps eleven historical source agreements, thirteen passing stages from a failed
fourteen-stage report, and its corrected affected stage separate. Installed
checkpoint **e9af13fd0** preserves interface, CONFIG and error-unwind rules.
Author and independent gates each pass two exact source tuples and one finite
CONFIG stage/26 assertions. CONFIG uses source-derived finite initialization;
whole-source ordinary CONFIG/native TCR agreement remains untested here. The
earlier fdef source2 and finite2/59 retain their private identities, alongside
setup and fixture failures. Rebound capture, called-class and receiver-creation116
repairs retain separate private reviews. Their current-c8bee
[projection](../../coverage/semantics/method-capture-current-review.json) passes
author and independent source groups16/7/3/5/2/2 and forty finite stages, plus
independent creator2/89. Forty fixture bodies elaborate with zero state execution.
Installed checkpoint **c536d1f74**, on **44edf5d2/1302**, separately accepts nine
sources and seventeen finite stages/541 maintained assertions for each actor,
plus independent creator2/89. These checks preserve selector, INSTANCE,
interface, origin-retirement and finite CONFIG guards. [Capture authority](METHOD-CAPTURE-AUTHORITY.md)
does not reconstruct arbitrary retired dynamic binding history.

Maintained commands are `method_compiler.py`, `method_runtime.py`,
`method_visibility_protocol.py`, `method_modifier_phase.py` and
`method_wrapper_protocol.py` under
`tests/semantics`. The visibility source catalogue is
`method_visibility_cases.json`. Native parse-only validation raises a static
`CompileError` for `final abstract` methods. The frontend retains those method
ASTs so the checked compiler can emit the same no-trace fatal;
`method_visibility_frontend.py` checks the original source and nearby parser
rejections. Four pinned PHPT sources also bridge native parse-only static
rejection to frontend method flags and the checked no-trace fatal. A direct
checked-AST fixture tests modifier priority in a
concrete class. Retained compiler, runtime, NUL argument,
intrinsic invocation and paused reports keep separate identities in
the review ledger. Existing match/print/exit cross cases have explicit bridges;
a prior broad campaign is not relabeled as a current full-core run.
Static/scoped source controls are in `static_method_cases.json` and run through
`method_runtime.py --catalogue tests/semantics/static_method_cases.json`.
`static_method_protocol.py` checks selected, saved, entered and object-rooted
states. Their native raw groups are stored in the ignored review archive;
the [tracked static-method ledger](../../coverage/semantics/static-method-review.json)
records hashes and recovery instructions.
First-class source method controls are in `first_class_method_cases.json` and
use the same runtime runner; `static_method_protocol.py` also checks capture
provenance and ownership transitions. A separate first-class review ledger
[records](../../coverage/semantics/first-class-method-review.json) the exact
native archive and frozen replay reports.

Finite internal Throwable getters now capture their selected receiver and
internal declaring owner. Invoking the captured callable uses the existing
ordered getter argument checks, including unknown named-argument errors.
`Closure->__invoke(...)` capture retains the selected Closure and invokes that
original object with its bound scope and static cells; the extra capture adds
no trace frame. Rebinding the source variable does not change either capture.
The [internal capture ledger](../../coverage/semantics/first-class-internal-review.json)
pins nine exact native cases and paused ownership/provenance controls. A
nullsafe first-class method expression emits PHP's compile-time rejection.
Ordinary real-Closure `bindTo` and static `bind` are in private review under
the separate [binding contract](CLOSURE-BINDING.md); that evidence does not
establish `Closure::call` or captured-callable rebinding.
Trait property/constant composition, remaining static/readonly properties,
hooks, user magic methods, destructors, remaining closure services and internal
protocols are still open. Deferred `new` parameter defaults use the
[source constructor-default rules](../../coverage/semantics/default-constructors-review.json); remaining
keyword NEW and initializer consumers retain explicit boundaries.
Unsupported declarations/consumers remain explicit; no native evaluation fallback
is used. Generated Throwable errors and ordered catches use owned objects;
finally transfers have a separate contract. Dynamic lifecycle
work follows separately.

Primary engine routes: `Zend/zend_compile.c` method and call compilation;
`Zend/zend_inheritance.c` method compatibility and constructor inheritance;
`Zend/zend_object_handlers.c` instance method and constructor visibility;
`Zend/zend_vm_def.h` method initialization/SEND/RECEIVE; `Zend/zend_closures.c`
closure creation and `Closure::__invoke`; `Zend/zend_execute.c` parameter errors;
`Zend/zend_exceptions.c` trace construction. All are from the vendored target.

## Lexical method arrays and class-method strings

Module 215 extends ordinary concrete selectors with private/protected access.
Object arrays may redirect to a selecting parent's private descriptor when a
child replaces it; concrete class arrays and strings use the requested effective
table. Protected checks use the root nonprivate prototype in either ancestor
direction. Full-byte lookup and public target certificates retain their contracts.
Direct access errors precede abstract/nonstatic dispatch errors; API callable
checks retain their distinct abstract/nonstatic-before-access ordering.

A nonpublic target carries its actual selecting scope, object/class selector kind
and source site. Direct saved calls authenticate that scope against the genuine
caller. Fixed strings retain the producer's compatible receiver; computed class
selectors remain static-only. Callable admission uses the receiving frame and
does not manufacture a dispatch target. Literal array kind proofs apply only to
exactly two ordinary unkeyed items; keyed/unpacked or variable history stays opaque.

Capture/clone retains permission from the source class or genuine rebound creator
origin after the maker and creator retire. That proof adds no heap owner. Array
captures require the outer creator certificate to equal the inner access proof;
later arbitrary dynamic binding history remains unproved. Selected receivers,
method defaults and static cells retain ordinary ownership and cleanup.

API registration stores raw callbacks. Dispatch resolves them in the emitting
USER frame, then entered callbacks freeze the selected target, ARG4 and saved
emitter. DIRECT members authenticate the snapshot; referenced members stay opaque
after mutation. The ordinary named/unpack receive predicates exclude genuine
handler contexts so the dedicated four-value receive arm remains disjoint.
Current213 assignment-warning checks preserve this selected private handler while
its throw retires the saved read and writes captured null through the caller
reference. ARG4, caller argument views and receiver cleanup remain authentic.

The [scoped ledger](../../coverage/semantics/scoped-callables-current-review.json)
separates original source outcomes, reached witnesses, failures and repaired checks.
Magic/autoload/internal consumers, dynamic compilation-warning handlers and
reference-return callbacks remain open. Shared ordinary callable
classification adds no fresh return agreement or paused-return dependency.

## Deprecated API keyword and compound callables

Module221 stages `self`, `parent` and `static` class selectors and qualified array
methods for supplied fixed callable parameters, error-handler registration and
delayed error dispatch. Exact scalar/array or nominal union branches keep their
earlier priority and emit no callable warning. The selecting scope is the actual
USER frame's lexical class; parameter checking uses the receiving frame, including
an empty scope in a free function. A compound constant's declaration location
does not replace that real USER permission.

Keyword deprecation runs after choosing the class and before method lookup. An
array's qualified method chooses its inner class after that callback, then emits
the compound deprecation without an inner keyword warning. The selected class and
string split stay fixed while a referenced method is reread after the callback.
Byref class-method strings likewise retain their old offset and method length;
by-value strings retain their original value. A retained old array can still admit
after a callback replaces the whole byref formal; the body and caller observe its
live replacement. These borrowed snapshots add no heap owner.

Error registration retains the raw callback. Dispatch clears the active registry
before selection deprecations and reselects using the genuine emitter. A narrow
API method target authenticates the selected method, declaring owner, static bit,
actual emitter and called class. It admits Zend's compound `self`/`parent` case
with a foreign `$this` without weakening ordinary scoped target eligibility.
The requested class table has priority. When it has no method and the array's
inner class is still its original outer class, lookup can select a declared
method on the actual receiver. Its getter checks access before strict-class
rejection. Registration and typed reception expose the getter's `Error` for
inaccessible methods. Delayed dispatch replaces it with an `Invalid callback`
`Error` whose previous exception is the getter error, then restores the raw handler.
Static selection retains no object owner. Warning throws abort admission and
restore raw handlers through the existing unwind route. Failed callable admission
uses only constrained scalar union fallback; it does not run another callable lookup.

Direct calls and first-class conversion retain ordinary lookup: raw keyword class
names reject as missing classes, and qualified array methods reject as literal
undefined method names. The [221 ledger](../../coverage/semantics/keyword-compound-callables-current-review.json)
records source comparisons, independent counterexamples, paused states and failures.
Default/variadic reception, `Closure::fromCallable`, other internal consumers and
user-return warning ingress remain required. Unstaged special callable checks stay
Unsupported; kind-changing or shorter retained method buffers, magic/autoload and
reference-return handlers remain open. Primary rules follow `zend_is_callable_at_frame`,
`zend_is_callable_check_class` and `zend_is_callable_check_func` in vendored
`Zend/zend_API.c`, with `zend_check_type_slow` in `Zend/zend_execute.c`.
