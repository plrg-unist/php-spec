# Request shutdown callbacks

Module231 implements `register_shutdown_function` through checked CONFIG calls.
The API selects its callable after all argument effects, retains the selected
receiver/Closure and copies the argument values. Scalar references are
dereferenced; embedded array references stay shared and outer arrays retain
normal copy-on-write behavior. Private and rebound registration permissions are
cached; subsequent raw callback mutation or maker retirement does not reselect
the method. Imported trait makers retain the using class and physical body proof.
Unknown named arguments are rejected after SEND duplicate checks.

Registered callbacks run in order after normal completion, exit, uncaught
exception handling and fatal outcomes, including serviced dynamic compilation
failures. Calls reuse ordinary weak reception with a genuine null C caller.
Callbacks can append later entries. A handled callback exception continues the
queue; an unhandled fatal or callback exit stops it. Callback exit replaces the
request's earlier status. Internal by-reference warnings use `Unknown:0` and
retain the selected callback when a replacement exception handler handles a
warning handler's throw.

Terminal diagnostics capture their severity mask and display destination before
queue entry, after formatter callbacks. Later reporting, display or Throwable
writes cannot alter those bytes. Runtime and compiler fatal producers retain
their distinct error levels. Admitted scalar/array default Throwable
messages preserve conversion effects; an array message calls the existing error
handler before freezing. If that warning throws, the
builtin formatter finishes and caches its string while the exception is pending;
its trace calls use the native fallback. The pending Throwable then uses the
exception handler. If handled, a separate return-type warning follows before
the original cached fatal is emitted. The saved warning anchor contributes an
authentic internal `Exception->__toString()` or `Error->__toString()` trace
without granting that class's source method permission. User overrides reuse the
ordinary selected method call with zero arguments and its lexical permission.
If a replacement exception handler handles their throw, the original C call
continues with its return warning and current private string cache.

The queue and selected arguments remain owned through this phase's DONE state,
as Zend frees shutdown registrations after later destructor/output stages.
Borrowed CALL/RAW/CAPTURE/PRODUCER and current SEND/receive/render certificates add no heap owners.
Current and saved calls authenticate the exact selected entry, arguments,
wrapping reference cells and empty internal caller context.
Variadic conversion records the received argument view separately from the
original registered copies; later local-array writes leave that view intact.

Source comparisons and source-reached state checks are separate gates:

```sh
python3 tests/semantics/shutdown_functions.py
python3 tests/semantics/shutdown_render_state.py
python3 tests/semantics/shutdown_review.py
python3 tests/semantics/shutdown_state_review.py
python3 tests/semantics/display_errors.py --case shutdown-freeze
python3 tests/semantics/callback_api_review.py --match shutdown-
python3 tests/semantics/callback_api_scope_check.py
```

Module247 stages keyword/compound registration through the shared221 API. Class
selection and string boundaries survive warnings while referenced method bytes
are reread. The cached target retains lexical/private permission and called
class after ordinary, handler, Stringable or Closure makers retire. Its borrowed
producer record pins the original target, callsite and captured scope/binding;
selected targets and copied arguments remain the only queue owners.
Magic/autoload/internal callback targets and existing shared error-handler
reference-return boundaries remain visible. Module257 supplies
[request-stage destructors](SOURCE-DESTRUCTORS.md). Eager destruction, GC, output
buffering, queue release and the remaining request stages are required next work; this
ordered callback phase does not claim complete request cleanup or complete core.
