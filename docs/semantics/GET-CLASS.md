# `get_class` testing support

Modules 165/166 model the finite `get_class` intrinsic for calls already admitted
by the source compiler. It is a class-name observer for source instances,
`stdClass`, Closure variants and modeled Throwable kinds. This is testing
support for object/exception cases, not closure of class introspection or the
general builtin catalogue. `get_parent_class`, autoload, reflection and other
class-name APIs remain outside this increment.

An argument must be an actual live object. The returned name comes from the
existing object descriptor; no native evaluator or new allocation supplies it.
Without arguments, the intrinsic reads the *executing* lexical or bound class
scope, emits `E_DEPRECATED`, then returns that class. A global zero-argument
call throws `Error` without a deprecation. Inherited methods therefore return
their declaring class for `get_class()` and the receiver's actual class for
`get_class($this)`. A first-class callable does not retain its creator's scope;
its zero-argument behavior follows its invocation context. Ordinary closure
lexical scope is already carried by the closure call context. Closure scope
rebinding through `bind`/`bindTo` is not yet a runtime route.

The intrinsic reuses the ordered argument and selected-call protocol for direct,
dynamic, first-class, `Closure->__invoke`, and pipe calls, including named and
array-unpacked arguments. Errors preserve source-order effects and the generic
builtin trace frame. The direct, resolved internal call with zero or one simple
positional argument takes Zend's special `GET_CLASS` trace path and has no
builtin frame; direct two-argument, named, unpacked, dynamic and first-class
calls use the generic frame. The predicate is checked against the compiled name
and original argument nodes. A namespaced user function can override the
global intrinsic; an unresolved namespaced call falls back to it.

`get_class` deprecation goes through the existing diagnostic machinery before
producing a value. Throwing error-handler callbacks and closure binding remain
separate core obligations and yield explicit `Unsupported` where reached.
Paused intrinsic tasks retain argument/owner roots and validate selected
identity, live object references, source origin, compiled line and unpack
prefix before resumption. [Review and commands](../../coverage/semantics/get-class-review.json)
record the bounded differential and paused-state evidence.
