# Source methods and constructors

Modules 141/142 extend named source classes with instance methods and
constructors. The nonpublic-method milestone adds protected/private instance
access and declaring-class private identity. The static/scoped milestone adds
static declarations and scoped calls. The target remains PHP 8.5.10 CLI NTS 64-bit
under the ordinary profile. The [public-method review](../../coverage/semantics/methods-review.json)
and [nonpublic-method review](../../coverage/semantics/method-visibility-review.json)
bind separate native sources, compiler projections and paused ownership checks;
these are bounded observations, not complete class semantics.

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
repairs retain separate private reviews. The current-c8bee
[projection](../../coverage/semantics/method-capture-current-review.json) passes
author and independent source groups16/7/3/5/2/2 and forty finite stages, plus
independent creator2/89. Forty fixture bodies elaborate with zero state execution.
Canonical installation remains pending; [capture authority](METHOD-CAPTURE-AUTHORITY.md) does not reconstruct
arbitrary retired dynamic binding history.

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
Interface methods and traits,
static/readonly properties, hooks, user magic methods, destructors,
remaining closure services and internal protocols are still open.
Deferred `new` parameter defaults remain outside the admitted initializer
language and require a separate cache/scope provenance increment.
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
