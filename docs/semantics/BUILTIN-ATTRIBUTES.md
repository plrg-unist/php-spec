# Builtin callable attributes

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

## Deprecated functions and methods

`#[Deprecated]` now admits ordinary named functions and source class methods
with literal string or NULL `message` and `since` arguments. Attribute names
use the same authenticated lexical resolver as NoDiscard. Function and method
attribute target/repeat checks precede signature and body compilation;
parameter-target errors retain existing parameter/default staging. A class
target produces its header Fatal before member errors. The selected declaration
supplies the runtime flag and message, including inherited methods and captured
named Closures.

An ordinary VM call emits E_USER_DEPRECATED (16384) after sends and named-hole
completion, for both used and discarded results. This warning precedes
NoDiscard, positional arity and parameter reception. A handler throw cancels
the later warning and receive. A successful handler resumes the same selected
callee, copied argument values, reference cells and receiver. Pending-call
ownership and cleanup follow the NoDiscard frame above; suppression still
invokes a registered handler. Literal `since` precedes `message` in the
diagnostic even when arguments are named in the opposite order.

Selected error-handler and `assert` callbacks use the internal API phase:
Deprecated warns after target selection but before argument copies, by-reference
warnings and parameter reception. The selected target is borrowed at this point;
the error-handler registry is disabled during its own call, while an `assert`
warning may invoke and replace the active handler. A captured Closure gains one
call owner only at entry. Early `assert` handler throws use the live failure
policy and release only prepared arguments. Other internal callback consumers
still refuse this early phase. PHP gives an explicit captured-Closure
`__invoke()` call an internal wrapper warning before the named function's
warning; the model refuses that route before either warning, with empty modeled
stdout/stderr. General message evaluation, other attribute targets and wider
owning wrapper histories remain partial.
The model follows `zend_compile.c` attribute and call lowering,
`zend_vm_def.h` DO_FCALL/BY_NAME warnings, `zend_execute_API.c` callback timing
and `zend_closures.c` wrapper flags in the pinned engine.

The [ATTR02 review](../../coverage/semantics/builtin-deprecated-review.json)
records 13 exact original-source agreements, two explicit API exclusions and
four reached fronts with 314 conditions: 278 source-reached checks, 24 derived
guards and 12 raw API projections. Its accepted private and actual-tail joined
strict cuts each compile 430 modules. Earlier failed fixtures and their
corrections retain separate identities; broader PHP core remains partial.

The [ATTR03 review](../../coverage/semantics/builtin-deprecated-api-review.json)
records ten new original-source agreements, including an unmarked `assert`
control, and four reached fronts with 179 conditions (172 reached, seven derived
guards). Strict431 passes. The historical ATTR02 `assert` API exclusion is now a
maintained supported expectation without new agreement credit; its original cut
remains an exclusion. The explicit Closure wrapper boundary remains open.
