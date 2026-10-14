# User output handlers

Module395 extends the Module391 stack with chunk0 user handlers for explicit
flush, clean, end and content-get operations. Ordinary named functions, simple
method/invokable callbacks and real Closures use cached selection and ordinary
weak internal parameter reception. Traces retain the internal handler frame and
the originating builtin API frame. Handler names preserve raw string/array
spelling; wider Closure and effectful callable forms remain dependencies.

Module396 adds normal scalar-result automatic callbacks for positive chunks from
source echo, print and inline output, and from lower routing after explicit
flush/end operations. A reached threshold processes the whole accumulated buffer;
WRITE phases are START on the first call and zero thereafter. VM entry preserves
source strictness, file and compiled line; an explicit API cascade remains an
internal weak call. Normal print restores its result1 after the whole cascade.

Module397 handles automatic VM callback throws and parameter-reception failures.
Arguments finish cleanup while the handler is still running, then the failed
handler disables and forwards its live bytes with the Throwable still pending.
Lower user layers reached at a threshold skip callback entry and disable; layers
below their threshold retain bytes for the caller's caught continuation. Callback
output retains PRODUCED without a failure-path deprecation. Interrupted print
does not assign its normal result, and ordinary cleanup preserves replacement
Throwables and their Previous links.

Module398 handles reception failures and throws from explicit API callbacks. Flush
forwards live bytes and restores the failed upper layer; clean discards those
bytes. End/get operations pop before lower routing and release the sole `zoh`
afterward. Frozen getter results remain owned during cleanup, while pending
Throwables interrupt caller assignment. If a normal upper handler's lower
cascade fails, the upper keeps its normal processed header. A destructor runs
with the older exception saved and cleared, so its own output can invoke an
enabled lower handler normally before a replacement exception gains Previous.
Cleanup destructors keep an internal callsite and the original API trace frame;
their user catch and visibility context remains intact.

Module399 preserves a defined scalar return when callee cleanup throws. Fixed
by-reference parameters receive callee-only wrappers; the saved invocation owns
the original copied input and phase. A normal-return certificate survives local
cleanup, while a body throw's null result cannot create it. The normal return and
processed header remain available as the pending Throwable interrupts caller
assignment. A selected error handler is not entered with an exception pending;
default deprecation reporting still follows its mask and display settings.
API callee-cleanup destructors retain an internal site and the originating API
trace frame for both normal-return and body-throw cleanup.

Module401 handles throws from fixed by-reference argument warnings before an
explicit API callback enters. Only the already prepared parameter prefix owns
fresh wrappers; those wrappers still contain the original copied input or phase.
After releasing that prefix, the undefined-result path retains the pending
Throwable and performs the ordinary API failure cleanup. The output callback
never enters, caller assignment is interrupted, and warning-handler output remains in
the live buffer without a failure-path deprecation. Historical cleanup metadata
does not retain or revive retired reference cells.

The handler receives a copied input string and the native START/CLEAN/FLUSH/FINAL
phase flags. Get-clean/get-flush return a separate frozen copy. The active top
buffer remains visible through callback getters, even when a lower handler is
running. Callback writes append to the first enabled layer of the actual stack
and mark PRODUCED_OUTPUT there. PHP8.5 deprecates output when the selected handler
has that flag, temporarily disabling it. A lower callback writing into an upper
layer does not immediately deprecate the lower handler. Error-handler writes
bypass the disabled layer, including the native
PRODUCED bit on an enabled lower default layer. FALSE forwards the current live
bytes and permanently disables the handler, with empty storage of size0. TRUE
and NULL suppress output; other admitted scalars supply converted bytes.
Lower default layers defer reached chunk thresholds while a user handler runs.
Those bytes can remain buffered after a clean operation until the next nonempty
write or an explicit flush.

Ordinary WRITE retains the full stack and commits only the selected buffer by ID,
preserving upper callback writes. Explicit flush instead detaches its upper entry:
scalar getters still observe that processed upper buffer, while level/full-status
observe the remaining stack. End operations make the lower layer active. A busy
positive user layer can retain PRODUCED bytes at its threshold; empty output keeps
them, and the next nonempty write processes the whole buffer.

The raw callback value (`zoh`) is the buffer's sole callback owner. Cached FCC
selection and original snapshots are readonly witnesses. Reference-backed raw
arrays can release a receiver when their alias changes during the callback;
ordinary raw arrays retain it until buffer removal. Entered method metadata borrows
the receiver, while Closure instances retain their ordinary ownership.
Arguments/retval finish cleanup before buffer
reset and the running state ends. End operations write lower layers before
releasing `zoh`; budget pauses retain every live owner and continuation.
Saved VM operands transfer once to the write continuation. Source/context, live
cursor and exact task suffix authenticate it; snapshots do not create owners.
Direct named Stringable constructions retain the temporary receiver in the real
producer tail until writing finishes, releasing it before print assignment or
caller catch. Plain variable operands stay borrowed; wider owned Stringable
forms remain an explicit dependency.

Callback exit, automatic pre-entry reference-warning throws,
throwing produced-output warning handlers, owning warning-handler abrupt cleanup,
automatic dispatch from other byte
producers, request-end/fatal callback drains, non-scalar or
reference-return conversion, typed variadic reception and by-reference variadic
extra arguments, mutating buffer APIs
during a handler, capability
failure notices for user handlers, and invalid/effectful callable creation stay
explicit Unsupported dependencies. Output handlers permit Fiber switching in
PHP; this milestone refuses switch entry until its suspension protocol is
specified. A retired borrowed target can authenticate normal completion, but
cannot be invoked again by this slice. Buffered stdout diagnostics keep the
existing Module391 boundary. Access through a retired callback receiver,
computed-name reads and nonstatic closure creation in that context are explicitly
refused; its metadata does not revive the object.
Non-scalar/reference returns are refused before callee cleanup can erase the
defined value. Full core remains partial.

Primary authority is `main/output.c` handler creation/op/stack-pop/destruction and
`Zend/zend_API.c` callable names/selection and
`Zend/zend_execute_API.c::zend_call_function` invocation. Destructor exception
save/restore follows `Zend/zend_objects.c::zend_objects_destroy_object`. The source runners compare
original bytes, both output channels and exits against the sole pinned runtime.
Reached-state checks distinguish borrowed receiver retirement, sole raw callback
ownership, post-route release, temporary disablement and valid forged getter
copies. Final acceptance is recorded in the concise author and independent
ledgers; original failures and raw observations remain external.
