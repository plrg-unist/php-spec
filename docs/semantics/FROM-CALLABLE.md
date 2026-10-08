# Closure::fromCallable

Module234 implements the actual factory over existing source functions,
intrinsics, invokable objects, method arrays and class-method strings. Literal,
imported, computed, leading-slash, object and nullsafe API entries use the ordered
internal argument protocol. A null receiver short-circuits the argument. Existing
Closure inputs, including `[$closure, '__invoke']`, preserve object identity.

Method selection uses the maker's real USER permission. Keyword/compound
deprecations run before selection through module221: class choices and method
boundaries remain fixed while referenced array methods are reread. The internal
argument receives a scalar string by value. A created capture freezes the selected
method bytes, descriptor, lexical owner, called class and nonstatic receiver;
later raw mutation cannot reselect it. Object selectors retain parent-private
redirection, while concrete class selectors retain requested-table priority.
Missing requested methods can use Zend's declared actual-object fallback, whose
getter executes in internal `Closure` scope, independently from USER admission.

The durable capture certificate checks its real API site and selecting permission,
including a rebound anonymous maker's creation context. Historical object metadata
is used only for descriptor checking. It does not allocate or root a retired
maker. Nonstatic captures own their actual receiver. Static captures own no
receiver and can retain a called class unrelated to their lexical owner. Invocation
and clone preserve genuine default reception, lexical/called scope and shared
source method statics. Ordinary source Closure clones keep their separate static
storage. Nominal Closure checks and fake-Closure equality use the selected target.

Source Closures created inside a captured method copy its authenticated scope and
immediate method body, including the full imported trait identity. This borrowed
creator evidence survives the parent capture retiring. Static children retain no
parent or former receiver; nonstatic children own their actual bound receiver.
Cold private static references and source statics use the consuming trait class.

Module358 also selects Fiber APIs from simple method arrays and static
class-method strings. Its capture records dereferenced members and the completed
factory call, including named or unpacked arguments. Later array mutation and
retirement cannot change the selected method or receiver. Retired factory
owners authenticate historical selection without owning anything; static
object-style selectors add no receiver root. The result shares the existing
Fiber API direct, explicit `__invoke` and C-root behavior. The
[Fiber factory ledger](../../coverage/semantics/fiber-from-callable-review.json)
tracks these checks; ordinary API callable arrays and effectful compound factory
selectors remain required.

Invalid callable values raise the factory's `TypeError`. An actual-object getter
denial becomes its previous `Error`, with raw selected method spelling. A throwing
deprecation handler fully unwinds and runs `finally` before the factory creates a
generic `TypeError` whose previous exception is the final handler exception.
Argument-read warnings occur before API entry; their throws escape unwrapped,
and a continuing read sends its captured null even after a callback defines the
variable. The actual C API frame remains present in factory/handler traces.

The maintained [source cases](../../tests/semantics/from_callable_cases.json) and
[paused fixtures](../../tests/semantics/from_callable_protocol.py) cover these
boundaries; the [review ledger](../../coverage/semantics/from-callable-review.json)
records distinct source/state cutoffs and original failures. Capturing or dynamically
calling the internal factory itself, arbitrary library-builtin captures, magic and
autoload callables and remaining callable warning consumers stay required.
[Transformed fake binding and current Closure253](CLOSURE-CURRENT-BINDING.md)
cover the selected capture/binding phase with its remaining REAL/temporary boundaries. No return-verification or complete-core claim is made.

Rules follow vendored `Zend/zend_closures.c` (`zend_create_closure_from_callable`,
`create_closure_from_callable`, `zend_create_fake_closure`, `zend_create_closure_ex`),
`Zend/zend_API.c` callable selection, and `Zend/zend_object_handlers.c` getter scope
and visibility checks.
