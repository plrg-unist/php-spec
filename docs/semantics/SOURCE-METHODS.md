# Instance methods and constructors

Modules 141/142 extend named source classes with instance methods and
constructors. The nonpublic-method milestone adds protected/private instance
access and declaring-class private identity. The target remains PHP 8.5.10 CLI NTS 64-bit
under the ordinary profile. [The review](../../coverage/semantics/methods-review.json) binds retained
native sources, compiler projections, paused ownership checks and compatibility
bridges; these are bounded observations, not complete class semantics.

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

Ordinary and nullsafe calls evaluate receiver and computed name in the pinned
order. A CV receiver can be read after name effects; a fetched property receiver
already denotes its value. Null skips the active nullsafe chain before names and
arguments. The selected target then owns its receiver throughout argument sending.
Calls reuse the positional/named/unpacked/variadic and reference protocols.
Construction allocates before arguments, calls the effective inherited constructor,
and retains the new object independently of the constructor's ignored return.

Contexts distinguish closure identity, receiver, lexical class and called class.
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

Maintained commands are `method_compiler.py`, `method_runtime.py`,
`method_visibility_protocol.py` and `method_wrapper_protocol.py` under
`tests/semantics`. The visibility source catalogue is
`method_visibility_cases.json`. Native parse-only validation raises a static
`CompileError` for `final abstract` methods. The frontend retains those method
ASTs so the checked compiler can emit the same no-trace fatal;
`method_visibility_frontend.py` checks the original source and nearby parser
rejections. A direct checked-AST fixture tests modifier priority in a
concrete class. Retained compiler, runtime, NUL argument,
intrinsic invocation and paused reports keep separate identities in
the review ledger. Existing match/print/exit cross cases have explicit bridges;
a prior broad campaign is not relabeled as a current full-core run.

Static methods, first-class method callables, interfaces/traits,
static/readonly properties, hooks, user magic methods, destructors,
closure rebinding services and remaining internal protocols are still open.
Deferred `new` parameter defaults remain outside the admitted initializer
language and require a separate cache/scope provenance increment.
Unsupported declarations/consumers remain explicit; no native evaluation fallback
is used. Generated Throwable errors and ordered catches use owned objects;
finally transfers have a separate contract. Dynamic lifecycle
work follow separately.

Primary engine routes: `Zend/zend_compile.c` method and call compilation;
`Zend/zend_inheritance.c` method compatibility and constructor inheritance;
`Zend/zend_object_handlers.c` instance method and constructor visibility;
`Zend/zend_vm_def.h` method initialization/SEND/RECEIVE; `Zend/zend_closures.c`
closure creation and `Closure::__invoke`; `Zend/zend_execute.c` parameter errors;
`Zend/zend_exceptions.c` trace construction. All are from the vendored target.
