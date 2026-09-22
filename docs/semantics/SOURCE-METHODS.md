# Public methods and constructors

Modules 141/142 extend named source classes with public instance methods and
constructors. The target remains PHP 8.5.10 CLI NTS 64-bit under the ordinary
profile. [The review](../../coverage/semantics/methods-review.json) binds retained
native sources, compiler projections, paused ownership checks and compatibility
bridges; these are bounded observations, not complete class semantics.

## Descriptors and dispatch

Class-owned method descriptors retain their declaring origin, signature, body,
modifiers and source context. They never enter the global function registry.
Compilation preserves member order and diagnoses modifier/body/redeclaration
errors before later members. Linking checks final methods, public override
variance, inherited abstract obligations and constructor-specific exceptions.
Constructor signatures are unconstrained by ordinary concrete parent constructors;
abstract constructor prototypes remain constraints.

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

Maintained commands are `method_compiler.py`, `method_runtime.py` and
`method_wrapper_protocol.py` under `tests/semantics`. Retained compiler, runtime,
NUL argument, intrinsic invocation and paused reports keep separate identities in
the review ledger. Existing match/print/exit cross cases have explicit bridges;
a prior broad campaign is not relabeled as a current full-core run.

Nonpublic/static methods, first-class method callables, interfaces/traits,
nonpublic/static/readonly properties, hooks, user magic methods, destructors,
closure rebinding services and remaining internal protocols are still open.
Unsupported declarations/consumers remain explicit; no native evaluation fallback
is used. Throwable/catch/finally and dynamic lifecycle work follow separately.

Primary engine routes: `Zend/zend_compile.c` method and call compilation;
`Zend/zend_inheritance.c` method compatibility and constructor inheritance;
`Zend/zend_vm_def.h` method initialization/SEND/RECEIVE; `Zend/zend_closures.c`
closure creation and `Closure::__invoke`; `Zend/zend_execute.c` parameter errors;
`Zend/zend_exceptions.c` trace construction. All are from the vendored target.
