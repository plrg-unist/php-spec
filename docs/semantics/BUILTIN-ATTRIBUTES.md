# NoDiscard declarations and calls

The NoDiscard consumer admits ordinary named functions and source class methods
marked with builtin `#[NoDiscard]`. Attribute names use the actual
lexical namespace/import resolver; groups retain original order and checked
arguments. The supported optional message is one literal string or NULL,
positional or named `message`. Runtime lookup reads the authenticated original
function/method declaration, including inherited methods and captured named
Closures, rather than adding a second metadata owner.

An unused source VM call raises E_USER_WARNING (512) after argument sends and
named-hole completion, before parameter reception, type checks or the body.
A positional missing argument therefore warns before its arity Error; a missing
required named hole errors before the warning. A completed optional default is
kept with its original named-hole provenance. Calls consumed by assignment,
an explicit `(void)` cast, arithmetic or a ternary do not warn. Suppression
preserves handler invocation; discarded `for` initialization/loop entries and earlier condition
entries warn while the final condition result is used.

Direct invocation of a captured named Closure preserves NoDiscard; its explicit
`__invoke()` wrapper follows the engine's masked flags. An ordinary user
`__invoke()` method retains its declaration flag. Raw callback APIs skip the
NoDiscard check. Unsupported source wrappers do not silently acquire that API
policy; scoped owning selectors and unproved magic/trampoline forms remain
explicit boundaries.

The prepared argument table and call context move into one pending frame during
the warning. The actual caller stays current, so a handler-created trace contains
no premature callee frame. On return the same table, reference cells, receiver
and selected callable move back, without rebinding arguments or warning again.
On a supplied exception, callback cleanup keeps that frame alive until the
callback cache is released. Pending-call release then follows the VM order:
captured Closure instance, fixed argument slots, EXTRA arguments, named extras,
and receiver. These owners are distinct from unfinished SEND cleanup.

For function/method declaration attributes, target and repeat checks precede
parameter compilation. Parameter-target errors retain the existing parameter
and default staging. Void/never restrictions follow signatures and precede bodies; supported magic-method restrictions run
after the body and preserve earlier argument/static/return-type checks. Class
header E_ERROR terminates compilation through the ordinary declaration replay,
while E_COMPILE_ERROR remains a static rejection. Function declaration lines use
the checked function-keyword receipt rather than the first attribute line.

Mixed/user attributes, general deferred message evaluation/constructor coercions,
attribute object construction, wider targets, trait/interface/anonymous method
attributes, unproved hook headers and marked static constructors remain partial.
Active DEFAULTRECEIVE and owning wrapper histories are refused by the pending
frame gate. Other builtin attributes keep their existing implementations and
remaining inventory obligations.

Implementation is in module440 with the existing signature/class/method and
call-entry stages. `nodiscard_sources.py` recovers 19 authored and eight
independent originals; the eighth is the FINAL-callback join control.
`nodiscard_protocol.py` checks four reached frames and release paths. The review ledger records measured unchanged gates separately
from source shapes that were inspected but not executed on the old model, and
keeps failed preparation/model packets at zero credit.

Twenty-six private originals agree with PHP. The additional FINAL-callback join
control confirms API versus inner-source behavior on the actual output tail.
Four source-reached fronts pass 297 checks, including 24 labeled derived guard
assertions. Three distinct unchanged-model
fences were measured, plus one exact ordinary control; the other 22 marked
variants were inspected but not executed on that old cut. Native preparation,
source/state cuts and retained failures are recorded in the
[review](../../coverage/semantics/builtin-nodiscard-review.json).
