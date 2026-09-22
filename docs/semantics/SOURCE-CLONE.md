# Object and closure cloning

Modules 149/150 execute unary `clone` and the PHP 8.5 language intrinsic
`clone(object, withProperties = [])`. Literal, computed, first-class and pipe
calls share the finite intrinsic identity introduced by exit/die. The compiler
preserves the temporary result of unary clone and the ordinary call result of
named/two-argument forms, including their different reference-demand errors.

Cloning allocates a fresh identity with the original class. Public declared and
dynamic slots retain their order and initialized/uninitialized/unset state.
Values use ordinary shallow copying: nested objects remain shared, arrays use
existing copy-on-write rules, singleton reference wrappers are unwrapped, and
live aliases remain shared. Retained typed-property aliases acquire another
type source, which ordinary owner release detaches.

Real closures copy capture/static storage using the live owner graph. Singleton
cells become independent; active or escaped references remain shared. Shared
static cells require the same declaration origin. Named-function closures retain
shared named-function statics, and intrinsic closures retain their builtin
identity. Class-bound closures also copy lexical/called scope and their receiver
edge; dropping the original closure cannot release the receiver of its clone.

The callable binder preserves source order for positional, named and array
unpacked arguments. It receives exact object/array types before allocation.
Property updates then run in insertion order, with integer keys converted to
names. A surviving reference update value is an error; a singleton wrapper is
read by value. Writes are weak even for strict callers, and shared property
aliases can update the original object. Closure property updates retain ordinary
invalid-name/forbidden-property error priority. Intrinsic receive/update failures
include the internal clone frame and, when applicable, the `Closure->__invoke`
wrapper frame. A missing required named object is rejected by the wrapper before
the clone body and carries only that wrapper frame.

Paused tasks authenticate source, compiled line/category, argument prefix,
selected intrinsic owner and update progress. Their heap roots retain the
original, copied arguments and new object until success or abrupt cleanup.
The exit binder positively admits only EXIT/DIE identities after the enum grows.

This is a bounded implementation for admitted ordinary objects and closures.
`__clone` callbacks/access checks, readonly reinitialization, visibility and hooks,
lazy objects, destructors, uncloneable internal objects, Traversable argument
unpacking and general lifecycle integration remain required. Unsupported class declarations are rejected before
execution; their callbacks are never silently skipped. Four dedicated controls
keep callback/readonly/hook/destructor dependencies separate from native agreement.

Matching engine sources: `zend_compile_func_clone` and `zend_compile_clone` in
`vendor/php-src/Zend/zend_compile.c`; `ZEND_CLONE` in `Zend/zend_vm_def.h`;
`ZEND_FUNCTION(clone)` in `Zend/zend_builtin_functions.c`;
`zend_objects_clone_members`/`zend_objects_clone_obj_with` in `Zend/zend_objects.c`;
`zend_closure_clone`/`zend_create_closure_ex` in `Zend/zend_closures.c`.
The maintained source, compiler, protocol and Unsupported suites are
`tests/semantics/clone_*.py`; independent acceptance is recorded separately.
