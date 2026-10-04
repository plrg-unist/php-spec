# Current Closure and fake binding

Module253 implements `Closure::getCurrent()` through literal, imported,
computed, object and nullsafe API entries. Argument evaluation and argument
errors precede the observation. The API returns the exact immediate executing
ordinary Closure, including arrows, clones, rebound copies and created source
Closures. Named functions, methods and fake captures raise `Error` with
`Current function is not a closure`. Calling the static API on another Closure
uses that object's type as historical selection evidence; its receiver adds no
owner during argument effects.

Direct first-class conversion of `$closure->__invoke(...)` returns that existing
Closure, matching the factory's `__invoke` identity rule. Invocation then uses
its ordinary selected body and frame rather than an extra invoke wrapper.

Binding a fake function, method, finite throwable getter or admitted intrinsic
allocates a distinct Closure and preserves the frozen selection. Nonstatic
bindings own their new receiver; old sources and receivers may retire. User
function and method statics remain shared with the selected source, including
through clone and repeated binding. Getter bindings invoke the selected getter
on the new compatible receiver. Free intrinsic bindings clear lexical scope and
receiver while retaining their changed called class for equality.

Scope resolution precedes receiver and fake-scope validation. Only exact lowercase
`static` denotes the previous lexical scope; weak scalar scope operands convert
to strings. Selected warnings suspend for error handlers. Handler class declarations
cannot undo a held missing-class warning, and throws run `finally` and retain
callback writes before the binding unwinds.

A free user-function fake bound to an object acquires internal `Closure` lexical
scope. A returned ordinary source Closure copies that scope, called class and
receiver as durable evidence; cloning copies its ordinary static storage.
Ordinary REAL bindings that need an internal lexical/called scope use the same
copied scope carrier. With a receiver and null lexical scope, Zend supplies the
dummy `Closure` scope. These objects retain their captures, static cells and bound
receiver without retaining the prior Closure. Created children authenticate their
immediate parent function and copied scope; bound copies authenticate their
binding site and identical source template. User-class permission still follows
its real lexical origin. `self`/`static` names, parent errors and anonymous
`new self` defaults preserve the internal scope.

Capturing the internal current/binding APIs, temporary REAL `Closure::call`
current-object escape, further internally scoped keyword consumers, and complete
REAL warning/unbinding behavior remain required. In particular, newly reachable
internal REAL warning and unbinding routes stay precise `Unsupported`; they need
static/internal warning staging and the original `USES_THIS` decision. This
increment does not close general REAL rebinding or temporary-call behavior.

The temporary-current issue is independent of paused return verification. At the
8.5.10 pin, non-generator `Closure::call` zeroes a temporary object's standard
header and gives it `GC_NULL` (`zend_closures.c:176–179`); `getCurrent` checks only
the copied function flags and returns that header with an added reference
(`421–435`). `call` frees it unconditionally (`214`), so the added reference does
not make an escaping value a valid Closure. This is a source-only finding; no
temporary-engine probe or patch was run. The proposed safe domain is a borrowed
identity for repeated current reads and strict identity comparisons inside the
active call, discarded before exit. Object operations and escaping values need
an explicit lifetime or intentional-divergence decision before core completion;
the current spec keeps this lane `Unsupported`.

Rules follow vendored `zend_closures.c` (`Closure::getCurrent`, `do_closure_bind`,
`zend_valid_closure_binding`, `zend_create_closure_ex`, `zend_closure_from_frame`,
`zend_closure_compare`) and static-method receiver ownership in
`zend_vm_def.h`. Source and paused fixtures retain distinct tested cutoffs in the
[current-binding ledger](../../coverage/semantics/closure-current-binding-review.json).
