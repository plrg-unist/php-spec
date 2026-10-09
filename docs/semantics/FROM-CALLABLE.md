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
tracks these checks. Ordinary fixed Fiber API callable arrays with simple method
names use module362's separate dynamic-call protocol; module 367 forwards the
original positional or named buffer for ordinary array-selected `start`.
Module 374 adds array unpacking across ordinary and captured START consumers,
with historical copied pack entries and the genuine outer API retained through
C-root forwarding. Module 376 adds Generator and Iterator START packs with real
resume/callback continuations. NaN `valid()` warnings preserve the original raw
retval through handlers, including parked handlers and thrown direct start Closure calls;
IteratorAggregate START acquisition keeps its original operand separate
from acquired Iterator/Generator data and retires data before a temporary operand;
direct captured-call throws retain their original exception and capture order.
The [Aggregate ledger](../../coverage/semantics/fiber-start-aggregate-review.json)
keeps these checks separate. Nested acquisition retains each raw Aggregate retval
until recursive acquisition finishes and retires returned layers before data and
the original operand on errors. Direct captured-call throws retain the same
exception/capture order; [nested checks](../../coverage/semantics/fiber-start-nested-aggregate-review.json)
have their own evidence. Pending Generator startup is bounded to a literal-output/
scalar-yield prefix and close of a frame with no owned roots without finally. Wider
startup, raw
payload changes and other Aggregate consumers remain required.
Module 370 executes simple raw Fiber API arrays as C-root callbacks. The Fiber
retains the original array, while its frozen receiver cache remains borrowed;
this differs from an owning Closure capture and ordinary array INIT.
Module 364 converts simple
Fiber API arrays directly to first-class Closures using a separate ARRAY source
witness; it does not manufacture completed factory-call history. Compound array
and factory selectors remain required.

Invalid callable values raise the factory's `TypeError`. An actual-object getter
denial becomes its previous `Error`, with raw selected method spelling. A throwing
deprecation handler fully unwinds and runs `finally` before the factory creates a
generic `TypeError` whose previous exception is the final handler exception.
Argument-read warnings occur before API entry; their throws escape unwrapped,
and a continuing read sends its captured null even after a callback defines the
variable. The actual C API frame remains present in factory/handler traces.

Fixed first-class `Closure::fromCallable(...)` capture now creates a distinct
factory object. Variable invocation owns that factory through argument evaluation;
the returned method Closure owns its receiver independently after factory retirement.
Callback selection uses the factory invocation's USER scope. The saved factory
occurrence adds no receiver owner and remains valid after retirement.
Named/unpacked argument errors precede callback resolution, and a Closure input
retains its identity. Eight factory originals keep their separate 367-module cuts:
the direct control at 6e709da7, then the captured receiver witness and six boundary
cases at 8cc7ed12. The [factory state renderer](../../tests/semantics/from_callable_factory_protocol.py)
retains 526 premises (467 genuine/derived, 59 constructed); the receiver witness
is in the [static compound catalogue](../../tests/semantics/scoped_static_compound_cases.py).
Literal normal `->__invoke(callback: ...)` also preserves the selected factory
when an argument clears its caller cell, retaining METHOD_RESULT and the caller
tail. Callback access uses invocation USER scope; factory creation grants no
later access. Error traces retain the API frame followed by `Closure->__invoke`,
with the invocation line and indexed argument snapshots. The variable control
agrees at b9f0b1ae/368, and four explicit sources plus 552 premises (512
genuine/derived, 40 constructed) pass at c1cdc2b5/368. These are separate from
the earlier 367-module factory cuts; maintained relocation renews no execution.
Literal first-class `->__invoke(...)` capture on that factory now reuses the
existing object and original creation site, popping only METHOD_PREP and preserving
the caller tail. An alias cell keeps it after the original cell is cleared; CONFIG
then retains the selected owner while argument evaluation clears the alias. The
returned method Closure owns its receiver independently, and saved factory evidence
remains valid after retirement. The REAL identity/by-reference control agrees at
e2ef/370; the repaired factory source and 610 premises (550 genuine/derived,
60 constructed) pass at 3cb295d1d/370. The interpreter failure and contradictory
fixture variable binding remain zero credit; maintained relocation renews no execution.
Captured factories also select the finite Throwable getter body through a
nonowning creation/invocation certificate. The getter owns its receiver independently
after factory retirement and reads its live message. Clone copies that certificate
and receiver; equality compares receiver, method and base independently from source.
The direct control agrees at 557e/371, and the captured live-message and clone/equality
sources plus 191 premises (154 genuine/derived, 37 constructed) pass at 771e/371.
The earlier Unsupported and parked-return fixture failure remain zero credit.
This coverage does not establish transformed binding or wider internal targets.
Nullsafe/computed invoke capture, wider aliases, computed/keyword factory creation
and remaining captured-factory Fiber targets and wider getter callbacks remain required.
Required original static-compound source 7
keeps its separate CLI 60 timeout with zero agreement.

The maintained [source cases](../../tests/semantics/from_callable_cases.json) and
[paused fixtures](../../tests/semantics/from_callable_protocol.py) cover these
boundaries; the [review ledger](../../coverage/semantics/from-callable-review.json)
records distinct source/state cutoffs and original failures. Wider internal factory
forms, arbitrary library-builtin captures, magic and
autoload callables and remaining callable warning consumers stay required.
[Transformed fake binding and current Closure253](CLOSURE-CURRENT-BINDING.md)
cover the selected capture/binding phase with its remaining REAL/temporary boundaries. No return-verification or complete-core claim is made.

Rules follow vendored `Zend/zend_closures.c` (`zend_create_closure_from_callable`,
`create_closure_from_callable`, `zend_create_fake_closure`, `zend_create_closure_ex`),
`Zend/zend_API.c` callable selection, and `Zend/zend_object_handlers.c` getter scope
and visibility checks.
