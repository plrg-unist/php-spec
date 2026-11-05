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

Module441 adds normal EOF and integer/string EXIT draining after actual shutdown
functions and request object retirement, including sole global objects without
user destructors. FINAL uses START only for an unprocessed handler and ignores
removability flags. Each pop routes through the live lower stack, so a lower
positive chunk can run WRITE before its FINAL. The selected top stays visible;
its raw owner retires after routing, while a previously called destructor does
not prevent the cached handler from running. Final callbacks and their diagnostic
handlers receive weak internal arguments, with request-end diagnostics at
Unknown:0. Callback-local destructors run after request destruction without
restarting it. Budget pauses preserve one saved terminal completion and its
operands. [OB01 evidence](../../coverage/semantics/output-request-end-review.json)
records 15 exact normal originals and six reached groups with 238 assertions.

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
producers, wider request-end/fatal callback paths, non-scalar or
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

The bounded FINAL fatal path handles an escaping builtin Throwable with a scalar
message, NULL previous and no selected exception handler. The restored callback
tail retains the real two arguments and one saved drain owner. Construction
records the internal callback frame; rethrow retains an earlier stored trace.
The builtin string cache is filled before fatal reporting freezes status 255.

OB03 then drops the retained local Throwable through ordinary release while the
buffers remain active/running. `zend_exception_error` has already cleared
`EG(exception)` before rendering; trace-child destructors see no pending exception
and their output stays buffered. A null-C child destructor throw uses the existing
eager bailout's abandoned receiver/release owners, reports its fresh unchained
fatal and resumes the same finalization stages. Deactivation then clears the live
stack and releases raw zoh owners top first; their output bypasses the discarded
buffers. Abandoned-call lookup views add no owners beyond the recorded C bailout zvals.
The original NORMAL/EXIT completion is not restored after a fatal.

[OB03 evidence](../../coverage/semantics/output-pending-release-review.json)
records four exact originals, four reached groups/169 checks and separate affected
FINAL fronts/110 checks. The older
[OB02 cut](../../coverage/semantics/output-final-throw-review.json) retains four
originals and three reached groups/131 checks without renewal. Wider previous
chains/source overrides or effectful rendering, late `ob_start` and
reentrant/abrupt raw-owner deactivation remain required. The original timeout,
Unsupported, fixture and interpreter failures keep zero agreement credit.


OB04 reuses the authenticated exception API cursor from modules 222/442 during a
FINAL throw.
Normal handling ignores and destroys the handler return, then releases the
original Throwable before restoring the raw registration. Output remains running
through that cleanup. The original FINAL return stays undefined, so live bytes
forward through the real lower stack without a produced-output deprecation.
The new marker binds its exact input carrier, phase, value and drain tail.

A handler-body, ignored-return destructor, original trace-child destructor or
pre-entry Deprecated-warning throw captures the actual FINAL tail before terminal
unwinding erases it. Existing270 retains the real original argument, error callback
and destructor C owners; documentary descriptors add no roots. A fresh default
fatal precedes raw-zoh deactivation. An interrupted explicit release also keeps its
occupied, nontraversable GC slot through the authenticated abandoned HANDLE tail.

At the OB04 cut, after normal drain or fatal deactivation, module 444 computed fast executor storage effects
in a local reference-count graph, following real object-store handles backwards.
Standard free hooks gain no shield; retained Closures are forcibly freed and can
attempt an uncalled public destructor after PHP execution is disabled. Its core
fatal escapes `do_cli` before the outer CLI return assignment, preserving process
status0. The terminal machine retains its last valid heap snapshot. Nonfast
`USE_ZEND_ALLOC` modes were then an explicit dependency; the mode check retains
request facts and uses the first environment duplicate and signed decimal prefix. The
[OB04 ledger](../../coverage/semantics/output-final-exception-handler-review.json)
records eleven exact originals and eight reached groups/465 checks, including a
separate nonfast native control with no agreement credit.

OB05 implements that nonfast cleanup stage. It releases globals in reverse symbol
insertion order, then constants, function/class tables and the active/saved handler
registrations in native order. Inherited method statics retire at their first real
class-table visit, once per shared cell; saved handler stacks retire oldest first.
Both allocator modes then sweep actual object-store handles backwards. Nonfast
standard free hooks gain the protective count that can suppress a later child
destructor attempt; the default fast path still skips those hooks without that count.
An exact root-multiset check refuses uncovered table owners.

Before executor inactivity, late shutdown registrations created during FINAL are
freed without calling their queued bodies. Arguments retire in order, then the
separate FCC receiver and Closure owners. Bound fake Closures retain their actual
header receiver even without scope rows. Ordinary release jobs preserve PHP entry,
and the shutdown-list catch retains unfinished C owners after a destructor throw,
reports/releases the new Throwable, then resumes executor cleanup. The local
inactive effect projection still leaves the terminal heap snapshot ownership-valid.

[OB05 evidence](../../coverage/semantics/output-executor-nonfast-review.json)
records twelve exact source/request contexts, including promotion of the retained
nonfast native control without native replay. Owning assert/tick cleanup at module
RSHUTDOWN and owning autoload cleanup after the shutdown list remain explicit
dependencies. Reentrant list registration, post-deactivation buffer starts, exit,
abrupt handler/visibility-warning cleanup and wider Throwable rendering during list
retirement remain partial, as do late bound-tick publication, uncovered table owners,
WeakMap/custom hooks and inactive nonpublic-destructor diagnostics. Earlier failed
cuts retain zero credit.

GC30 added quiet inactive WeakReference unregister and standard weak notification.
Reverse handle order determines whether a live standard object runs its guarded
hook or keeps fast-skipped fields after its observer unregisters. The local
association view never filters the owning graph; field releases and C guards
still update the local heap. Bound Closure validation sees MARKED receivers in
the full state. WeakMap value releases were still fenced at that cut;
weak Closure/custom notification remains partial. See the
[inactive weak-hook review](../../coverage/semantics/gc-inactive-weak-free-review.json).

GC31 extends the same terminal projection to WeakMap free: all keys unregister
before values release in insertion order. Association filtering leaves the owning
heap intact; ordinary value decrements and C guards update it, preserving later
leases after a fatal and reference-cell multiplicity. Active key-triggered Map
notification and incoming Map-key associations remain fenced. The
[inactive Map review](../../coverage/semantics/gc-inactive-weakmap-free-review.json)
records seven exact contexts and 599 new/affected conditions at their own cuts.

OB06 admits only a no-argument `ob_start()` during normal executor queue release
after output deactivation. The failed start leaves the buffer stack empty and
the output sequence unchanged, emits `ob_start(): Failed to create buffer` as
E_NOTICE, and returns false. Suppression, selected handlers that return true or
false, and direct fallback rendering follow the existing diagnostic protocol.
An ordinary shutdown callback still starts a buffer before deactivation.
Explicit arguments, callable handlers and nested starts from an active error
handler remain checked Unsupported. At the OB06 cut, a handler-return object
whose destructor starts a buffer still fails before the nested call and retains
zero agreement credit.
[OB06 evidence](../../coverage/semantics/output-executor-post-deactivate-review.json).

OB07 covers that returned-object path. The selected error handler is disabled
while its return value is destroyed, so an echo-only destructor runs before
the outer failed-start result and a nested no-argument `ob_start()` emits one
built-in Notice and returns false. The cleanup rule requires the saved
destructor/result and error-handler cleanup records, the original Notice, and
the normal executor queue; it keeps active handler-body reentry and explicit
arguments outside the admitted path. Fast and slow allocator source cases
agree exactly, a source-reached state checks the ownership links, and the
OB06 refusal controls still pass. Joined strict433, nested fast/slow sources
and the three refusals pass with the executor tick-owner branch present.
Wider callback nesting, abnormal queue completion and argument forms remain open.
[OB07 evidence](../../coverage/semantics/output-executor-retval-review.json).

OB08 first admitted positional `ob_start(null)` after output deactivation.
OB09 generalizes the same normal executor queue path through authenticated
CONFIG argument binding and the ordinary `|zll` conversion protocol. Named and
unpacked arguments, omitted callbacks, chunk/flag coercions, deprecations and
type/count failures retain their native order. Successful NULL/default callback
creation reaches the inactive-output check before any buffer push, emitting
E_NOTICE and returning false without changing the buffer stack or sequence.
The same receipt applies in the authenticated destructor of a Notice handler's
returned object while that handler is disabled. Malformed binder/pack
descriptors stay invalid.
OB10 also resolves admitted pure non-NULL callbacks after complete conversion.
It creates and releases the transient `user->zoh` owner before the inactive
failure Notice, without invoking the callback or inspecting its required arity.
Raw argument owners retain temporary invokables and array receivers through the
diagnostic. Lookup observes conversion-handler changes but is not repeated after
a Notice handler mutates referenced array selectors or retires a receiver.
This applies in the authenticated returned-Notice-object destructor as well.

Normal argument consumption uses the VM's root-only `zval_ptr_dtor_nogc` rule;
array child cleanup still uses ordinary decrements. Explicit GC controls distinguish
a direct cyclic argument from an array-wrapped child. Consumed Closure operation
metadata reuses borrowed producer scope/binding certificates and retained capture
cells solely for checking; it adds no actual owner or invocation authority.
Factory-local byref captures and bound method receivers retain their native
destructor timing. Selected-handler throws and callback-destructor throws follow
the existing Throwable trace and cleanup protocol.

OB11 handles known pure invalid callbacks without creating a `zoh` owner. A
failed selection emits Warning before processing the failed-start Notice;
normal completion returns false. A declaration-prefix function view and DIRECT
array snapshot preserve that failure
when a Warning handler publishes the missing function, repairs a selector or
retires the old receiver. These checking views never replace live lookup tables
or add real owners. Current handler state selects the following Notice after
cleanup of the selected handler's temporary raw callback and return owners.

Diagnostic cleanup authenticates the actual RESULT/unreleased and CLEAN/released
operation records separately. A live pending Throwable remains owned by the
operation; a throwing return destructor contributes the genuine `ob_start` frame
and current arguments to its Throwable trace. An eligible Notice handler is
skipped while that Throwable is pending; otherwise the default Notice follows
reporting/display and silence, before propagation to the caller's catch.
OB11–12 share one root-only NOGC argument-discard rule for admitted Warning and
Notice-handler throws. Full validation of the actual task authenticates its
terminal phase before erasure. The borrowed source record binds the pending
Throwable and temporary release without adding an owner or executable task.
Array children retain ordinary cleanup. Precreated-Throwable controls distinguish direct cycles from
array children; a newly constructed Throwable retains the callback in its trace.
Consumed Closure metadata reuses borrowed capture history after real retirement.
Seven exact originals, 279 reported reached conditions and 90 affected Warning
conditions pass at their recorded cuts.
OB13 admits the selected Notice handler's returned-object destructor when it
throws before the saved cleanup resumes. The pending Throwable remains a live
operation root; a new Throwable stores the authentic output builtin frame and
raw sent arguments in its trace. Exact `ob_start` and `ob_end_clean` originals
and reached states check this shared Notice path, while precreated-Throwable
controls distinguish root-only NOGC from ordinary array-child cleanup. Seven
originals and 165 reported reached conditions pass at their separate cuts.
OB14 admits a normal Warning handler's returned object when its destructor
attempts a nested `ob_start` after output deactivation. The handler is disabled
during that destructor; the nested failed start emits the default Notice, then
the original Warning cleanup restores the selected handler for its failed-start
Notice. The saved Warning receipt and actual RESULT cleanup authenticate the
new branch. Three exact originals check noarg, named/unpacked NULL and a pure
temporary callable; the reached state checks the disabled handler, normal
operation, unreleased cleanup and coherent authority negatives. This scope does
not include a throwing handler or destructor.

Whole declaration-history validation remains open for late handler function
publication; a default-NULL Notice baseline reproduces the same frontier.
Unresolved/effectful callback creation, other abrupt VM argument-release paths,
active handler-body reentry,
other Warning/deprecation-handler returned-object starts, other output Notice return
destructors and wider executor completion remain
partial. Handler initialization also allocates the aligned chunk buffer before
the inactive-output check; allocation failure and PHP memory limits remain
pending effects, as in the active buffer model. At their OB10 cut, the original
weak-observer GC controls stopped at the inactive custom free-hook frontier and retained zero full
agreement credit; separate explicit-cleanup controls cover the creation protocol.
[OB08 evidence](../../coverage/semantics/output-executor-explicit-null-review.json),
[OB09 evidence](../../coverage/semantics/output-executor-reception-review.json),
[OB10 evidence](../../coverage/semantics/output-executor-creation-review.json),
[OB11 evidence](../../coverage/semantics/output-executor-invalid-review.json),
[OB12 evidence](../../coverage/semantics/output-executor-notice-discard-review.json),
[OB13 evidence](../../coverage/semantics/output-executor-notice-retval-throw-review.json),
[OB14 evidence](../../coverage/semantics/output-executor-warning-retval-nested-review.json).
