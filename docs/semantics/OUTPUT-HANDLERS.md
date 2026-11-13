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
explicit API or source VM callback enters. Only the prepared parameter prefix owns
fresh wrappers; those wrappers still contain the original copied input or phase.
After releasing that prefix, the undefined-result path retains the pending
Throwable and performs the ordinary failure cleanup. The output callback
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

Callback exit,
throwing produced-output warnings from FINAL or lower API cascades, wider owning
warning-handler abrupt cleanup,
automatic dispatch from other byte
producers, wider request-end/fatal callback paths, internal/custom-object/resource
return conversion, typed variadic reception and by-reference variadic
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
Internal/custom-object and resource returns are refused before callee cleanup can
erase the defined value. Referenced values retain their actual cell until
conversion; admitted scalar, Array and standard-object payloads transfer their
actual owner. Normal FINAL Array/Stringable conversion uses the same lifetimes;
pending conversion/fatal and non-Stringable Error paths remain dependencies.
Full core remains partial.

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

OB15 extends pre-entry warning failure to positive-chunk callbacks triggered by
echo, print and inline output. Diagnostic argument cursors retain the running
handler and its exact producer tail. A second warning releases the original
scalar prefix before restoring the independent two FCI arguments; its retired
reference metadata adds no owner. Undefined callback results disable the selected
handler and forward its live bytes while the Throwable remains pending. Reached
lower user chunks skip callback entry, while lower chunks below their threshold
retain bytes. Warning output preserves PRODUCED without a failure-path
deprecation. Owned Stringable producer operands retire before caller catch;
interrupted print never assigns its normal result.

Cached function metadata also survives a warning retiring a reference-backed raw
method receiver. Later argument preparation uses that borrowed metadata without
owning or reviving the receiver; a later warning can throw before callback entry.
Reaching actual entry after retirement is explicitly Unsupported.

Its pre-entry warning protocol excludes wider owning warning-handler abrupt
cleanup, explicit lower cascades, FINAL and exit. Produced-output deprecation
uses the separate protocol below.
[Author evidence](../../coverage/semantics/output-vm-reference-warning-author.json)
retains exact sources, the reached release/producer fronts and original failures.
[Independent review](../../coverage/semantics/output-vm-reference-warning-review.json)
records eleven exact originals and one SL435 front with seven groups/475 reached
conditions, including cursor authority, sole prefix ownership and retired receiver
metadata without live roots.

Module448 preserves a defined scalar return when its produced-output deprecation
handler throws, for source VM output and direct flush/clean/end/get APIs. A single
pending task keeps the actual return, copied input/phase and Throwable distinct;
API caller/tail witnesses reuse the existing failed-call tag. The selected handler
re-enables before normal result commit: FALSE forwards live bytes and disables,
TRUE/NULL suppress, and other scalars convert using current precision. Lower
routing retains the pending Throwable and interrupts caller assignment.

An ignored error-handler return can also throw during its destructor. That
cleanup runs while the output handler is disabled and still running; its output
bypasses that layer before the saved output return commits. An owned Stringable
producer retires afterward with the old exception saved, so its destructor can
invoke the normally processed handler again. Getters retain the original frozen
bytes, and end/get operations release raw callback owners after lower routing.
VM diagnostic-return destructors retain the emitting source file/line. Explicit
APIs keep the internal destructor site and their authentic builtin trace frame.
FINAL, explicit lower-cascade deprecation throws, callback exit and wider return
conversion remain partial.
[Independent review](../../coverage/semantics/output-deprecation-warning-review.json)
records seven exact originals and one SL436 front with two groups/110 conditions,
including both fresh destructor traces, frozen getter identity and sole pending
and post-route raw owners.

Module449 retains the raw returned reference through callee cleanup and the
produced-output diagnostic, then converts its live scalar payload. A referenced
FALSE becomes an empty string and keeps the handler enabled; referenced TRUE
emits `1`. Unwrapping releases only the retval's cell owner and leaves aliases
unchanged. A warning can mutate the selected cell or rebind its global name;
rebinding does not replace the already returned cell. Normal cleanup seals borrow
the real frame's return owner and require its restored RESULT before transfer.
Defined reference returns also survive a throwing return-by-reference Notice or
callee destructor. Pending exceptions preserve interrupted assignment and getter-copy
ordering. Callback return demand stays true even when source print is unused.
Normal FINAL scalar references share the existing drain; pending FINAL reference
cleanup remains explicitly Unsupported with its returned value retained.
The real scalar-cell decrement authenticates its operation against the actual
COMMIT record and native suffix; its consumed cell metadata adds no owner.
[Independent review](../../coverage/semantics/output-reference-return-review.json)
records eight exact originals, both diagnostic-return destructor traces and one
SL438 front with two groups/183 conditions through real release and resumption.

Module451 retains a returned Array through the conversion Warning, releases it,
then commits the fixed string `Array`, including when a Throwable is pending.
Reference unwrapping transfers the Array owner before the Warning; later writes
to that cell cannot replace it. Callee cleanup and return-by-reference Notice
throws preserve a defined return. A pending exception prevents selected Warning
handler entry; child destructors can replace it with their own Previous-linked
Throwable. API and VM destructor traces retain their ordinary sites. Getter
copies, lower routing and interrupted assignment reuse the existing output paths.
Output during Warning/Array cleanup retains the new PRODUCED flag for the next
invocation, after the earlier deprecation check has already finished.

The GC handoff hook suppresses only the real reference-wrapper transfer visits,
including its modeled last-cell child job; actual Array retval destruction keeps
ordinary GC candidacy. Exact source, successor, retired-cell identity and release
guards distinguish them. [Author evidence](../../coverage/semantics/output-array-return-author.json)
records 20 exact originals, two checked refusal controls and two reached groups
with 234 conditions. [Independent review](../../coverage/semantics/output-array-return-review.json)
adds four exact originals and one SL439 front with three groups/162 conditions:
real CELL/Array owners, pending replacement, readonly metadata, global collector
dispatch and the affected scalar marker checks. That cut kept object conversion
and FINAL Array conversion Unsupported.

Module456 adds standard user-object and stdClass return conversion, using the
existing Stringable call protocol when a method exists. The real retval and cast
guard have separate owners. After the method returns, its actual operand survives
ordered cleanup; referenced strings are read late. A throwing return-by-reference Notice also
preserves the defined cell through its real frame or an unstaged owner marker.
Conversion freezes the resulting bytes before releasing the original object.
Missing-method Errors, fresh method exceptions and destructor replacements keep
normal buffer processing, frozen getters and interrupted assignment.

An already pending exception skips the method body but still adds and releases
the native cast guard when the method exists. That guard decrement and actual
retval destruction retain ordinary GC candidacy. Only authenticated reference
wrapper handoff visits use the existing no-check hook. Retired cell witnesses
own nothing; the release successor retains the exact raw method operand identity.
API/VM trace sites and late PRODUCED flags follow their original output context.
At that cut, FINAL object, internal/custom casts, resources and the paused COMP88
supplied Throwable/comparison contracts remained separate dependencies.
[Author evidence](../../coverage/semantics/output-object-return-author.json)
records 18 exact normal originals, two refusal controls and four reached
groups/420 conditions. [Independent review](../../coverage/semantics/output-object-return-review.json)
adds five exact originals at recorded cuts and three SL444 groups/219 conditions.
Saved output pairs keep their real C-frame witness during validation; execution
entry still requires the original caller.
The two Notice originals have public60 timeout cuts with zero source agreement.
Their full-resumption owner fronts establish state evidence; source performance
remains an unfinished validation obligation.

Normal FINAL Array and Stringable returns now reuse their conversion/release
stages and the real drain. Array Warning handlers receive `Unknown:0`. Known
Stringable methods have a null callsite/internal line; the earlier registration
site remains documentary metadata. The exact immediate caller frame binds the
native domain, so a nested same-receiver call cannot borrow it. A forged
documentary callsite is excluded from ordinary source-frame admission.
Converted bytes freeze before original-object release; real guard decrements
remain ordinary GC visits. Pending exceptions inside these conversions stop
before further unwind; their null-C fatal and abandoned-owner protocol is a
separate dependency. [Author evidence](../../coverage/semantics/output-final-conversion-author.json)
records two normal originals, one refusal and 95 reached conditions.
[Independent review](../../coverage/semantics/output-final-conversion-review.json)
adds one exact internal-trace original and one SL446 group/69 conditions through
real Object owners, null-C entry, frame refusals and full drain. The earlier
Notice performance limitation remains open.

A top FINAL non-Stringable object follows the direct null-C fatal path:
`Unknown:0`, status255 and no user destructor. The error precedes retval cleanup;
an authenticated abandoned-C receipt retains that actual owner through existing
buffer deactivation and inactive executor policy. Its source marker grants no
executable task or method entry. [Author checks](../../coverage/semantics/output-final-error-author.json)
cover the two exact originals. The [independent review](../../coverage/semantics/output-final-error-review.json)
clears 14 reached assertion groups, including public validity, strict receipt and
class-history refusals, budget cuts and complete deactivation. Class-history
checking excludes only the current authenticated abandoned row to avoid recursive
receipt validation; actual owners and other rows stay intact. Lower cascades and
pending Stringable fatal/cast owners remain separate dependencies.

A sole direct `throw new Exception(<literal string>)` in a no-local FINAL
`__toString` body now follows default fatal reporting without a selected exception
handler. The real null-C method return transfers the RV and cast guard before
either decrement; existing Throwable cache/report, ordinary Throwable release and
buffer deactivation retain their order. Source/body, NEW birth and exact compiled
tail guards exclude intervening catch/finally/tick cleanup and supplied throws.
The abandoned receipt owns only the existing two receiver roots, while immutable
birth/source facts remain checkable after the Throwable retires. One exact
destructor witness and 14 reached assertion groups pass at their recorded cuts.
The [independent review](../../coverage/semantics/output-final-cast-throw-review.json)
clears real owner/GC transfer, public guards, budgets and the retired-Throwable
endpoint; [author evidence](../../coverage/semantics/output-final-cast-throw-author.json)
records scope and preserved failures.

Compiled-CV native FINAL methods now use ordinary catch/finally and ordered local
cleanup before the genuine null-C return. The existing retval and external cast
guard transfer to a real C consumer before CV jobs; the frame-exit barrier also
runs with no live jobs or declared destructor. Local destructors receive the
actual null caller/internal trace. A borrowed direct-NEW birth records no owner;
catch consumption and staged or unstaged normal return clear it. Pending identity
must still match at reporting, followed by ordinary Throwable release and the
existing abandoned-owner/deactivation policy. Capture, public admission and report
retain full class authority; intermediate unwind recognizes the exact saved native
consumer without replaying immutable declarations at every discarded task.
[Author evidence](../../coverage/semantics/output-final-cast-locals-author.json) and
[independent review](../../coverage/semantics/output-final-cast-locals-review.json)
record the exact source and state cuts. Constructor provenance for these CV paths
follows the completed-constructor rule below. Selected handlers,
supplied identities, replacement chains, wider constructor/result owners, custom
rendering, ticks and lower FINAL cascades remain dependencies.

A local destructor's direct builtin `Exception` NEW now reports at its own actual
null-C return, after its method cleanup. A borrowed marker in the saved native
consumer authenticates that fresh throw and clears on catch or normal return.
The bailout retains the saved outer exception, both destructor C protections,
the outer retval/cast pair and remaining outer CV owners. The reported exception keeps
NULL previous; its ordinary release precedes inactive buffer deactivation.
The [review](../../coverage/semantics/output-final-cast-nested-review.json) and
[author evidence](../../coverage/semantics/output-final-cast-nested-author.json)
record the exact native/source and owner/clearing cuts.

Both structural native paths obtain provenance from genuine completed `CTOR_NEW`
reception. The constructor's receiver was selected before arguments; its completed
result must be that same receiver. A nonowning record saves the actual NEW site,
normalized message bytes, code and line with builtin `Exception` kind and NULL
previous. Only the matching own-code direct `THROW_VALUE` promotes it to pending
provenance; method/captured constructor calls and failed reception do not mint it.
No latest-object identity or literal-message reconstruction is used. Catch and
real normal consumption clear the record; live admission/reporting recheck the
normalized fields, while retired receipts retain the immutable snapshot.
Two originals cover an ordinary string CV and a helper that allocates a distinct
declared instance after the exception receiver was selected.
[Author evidence](../../coverage/semantics/output-ctor-birth-author.json) and
[independent review](../../coverage/semantics/output-ctor-birth-review.json) retain
the source, owner and provenance cuts. The closed no-CV sole-literal route above
is unchanged. Existing builtin constructor-argument/default-rendering domains,
supplied identities, replacement chains, selected handlers and lower cascades
retain their bounds.

Ordinary no-argument nongenerator helpers may complete and throw the fresh builtin
`Exception` through a finite saved call contour, including recursive activations.
The immutable contour records each selected producer/caller source edge and the
original native consumer beside the unchanged normalized constructor birth. A
nonowning position cursor identifies the active suffix. The matching own-code
`THROW_VALUE` promotes NEW to THROW; each genuine VM restoration consumes exactly
one actual frame tail with the same pending identity. Repeated function and call
site values remain valid. Only an exhausted contour advances to UNWIND, required
by native report admission and retired receipts.

The departing helper keeps its cleanup FUNCTION while CURRENT/callsite restore to
its immediate caller before CV release. Only the original native epilogue performs
the null-C return. Empty-CV helpers reuse existing unstaged release; no source fact
adds an owner or cleanup barrier. Catch and real normal consumption at any active
helper or the native caller clear the outstanding contour. Byref-declared helpers'
exceptional paths publish no reference retval.

Formal/actual arguments are empty. Current helper HELD/task heap owners are absent
at birth issuance; each saved VM caller on the folded edges keeps that bound during
transport. Real locals/context remain owned. These physical guards exclude
constructor-argument aborts and wider owning continuations.
[Helper-unwind evidence](../../coverage/semantics/output-helper-unwind-review.json)
retains the single-edge cut; [contour author evidence](../../coverage/semantics/output-call-contour-author.json)
and [review](../../coverage/semantics/output-call-contour-review.json) record the
finite-contour source, owner and consumption cuts. NULL previous, default rendering
and all held domains retain their existing bounds.

A fresh by-value ordinary no-argument nongenerator factory may return its completed
builtin `Exception` into a native own-code `throw make()` expression. The nonowning
record separates producer FUNCTION/RETURN and native THROW, deriving the selected
call site from that native throw. The unchanged constructor birth keeps actual
selected receiver/result and normalized message/code/line with NULL previous.
Only the real `RETURN_UNWIND` marker and exact one-frame restoration advance NEW
to RETURNED. Generic ORIGIN has already unwound to the producer function and is
not used as the return-site proof.

The actual return operand owns the object. Unstaged restoration keeps RESULT;
staged cleanup keeps `FRAME_EXIT.VALUE` with RESULT null, then publishes the same
RESULT after compiled CV jobs. This represents Zend's already-owned return slot;
the engine fills `EX(return_value)` before leaving the producer. RETURNED grants
no pending/report authority. Actual matching native `THROW_VALUE`, the same live
RESULT and completed factory cleanup are required for THROW. Producer override
consumption clears metadata; existing native catch/normal consumption remains.
Full source/class/live checks and retired birth snapshots are preserved. Ordinary
normal reference returns, supplied identities, constructor-argument aborts, COMP88,
custom rendering and other held domains keep their bounds.
[Author evidence](../../coverage/semantics/output-factory-return-author.json) and
[review](../../coverage/semantics/output-factory-return-review.json) record the cuts.

The same fresh by-value result may pass through a finite saved contour of admitted
ordinary no-argument nongenerator helpers. The leaf NEW/RETURN, normalized birth
and final native THROW stay immutable. Every intermediate selected call must be
the child of that caller's own RETURN, and every helper returns by value. A
nonowning positional cursor identifies the active frame suffix, so equal recursive
function origins and call sites do not collapse distinct returns.

Only the actual RETURN_UNWIND marker and exact same-object one-frame restoration
consume an edge. RESULT or FRAME_EXIT.VALUE remains the real owner; a staged VALUE
must name the function that actually departed and exclude another contour VALUE
for that object. Partial RETURNED grants no pending authority. The final native
throw requires contour exhaustion and no remaining contour VALUE owner, retaining
the full creation trace after producer frames leave. An intermediate normal
override clears NEW or partial RETURNED at the real owner drop before retirement.
Constructor, native-consumer, NULL previous, default-rendering and held domains
keep their existing bounds; no owner or generic return/frame rule changes.
[Author evidence](../../coverage/semantics/output-factory-contour-author.json) and
[review](../../coverage/semantics/output-factory-contour-review.json) record the cuts.

Fresh factory results may be assigned to ordinary private compiled CVs and thrown
by a later read. A nonowning association binds the actual successful assignment,
factory birth and allocated cell; siblings coexist without overwriting one
another. The real write moves RESULT into CV ownership, NULL discard preserves
it, and delayed evaluation remains VARIABLE until the genuine throw resolves
that cell. CV plus pending ownership then survives ordinary CV unwind.

Only the selected matching throw spends its fact. Rebinding removes stale rows;
an in-frame catch clears the active throw while preserving other live facts.
Unhandled native departure drops live rows before CV destruction and keeps the
selected historical receipt for reporting. Existing helper-source wrappers keep
the same selective behavior. Full source/cell/class/live and C0 guards remain;
dynamic or aliased places, supplied identity, normal byref results, constructor
aborts, COMP88 and rendering bounds do not expand. The completed single-CV source
and multiple-CV public performance limits remain distinct in
[author evidence](../../coverage/semantics/output-factory-cv-author.json) and
[review](../../coverage/semantics/output-factory-cv-review.json).

Fresh factory results may be stored and thrown from an ordinary helper's private
compiled CV. Each association records the actual recipient frame position and
cell, preserving equal names in native, recursive and other frames. The normal
return cursor stops at that recipient's real WRITE_NAME; the actual same-cell
VARIABLE throw starts an independent cursor over exceptional restores. Each
same-pending one-frame pop preserves the departing cleanup FUNCTION and restores
the immediate caller before its CV jobs. A staged pop keeps the release job and
cell/F2 until scheduled cleanup leaves pending F1; only cursor exhaustion admits
the original native C0. Both normal and exceptional departures remove only that frame's live rows, and catch or normal
override clears active history while preserving siblings. The metadata adds no
owners. Factory by-value, constructor, private-cell, continuation, NULL previous,
default-rendering and held bounds remain. 35 independent groups cover public validity, owners,
clearing, reports and retired receipts. Both public 90-second attempts
retain zero agreement and unfinished source performance; the failed local aggregate
and its later true C0 observation remain uncredited.
[Author evidence](../../coverage/semantics/output-factory-helper-cv-author.json) and
[review](../../coverage/semantics/output-factory-helper-cv-review.json) retain the
actual 465-module joined gate and declaration-only old30 fixture adaptation.

Within the existing compiled-CV cleanup boundary, an implicit strict scalar
return failure in native `__toString` now retains its
actual TypeError through FINAL cleanup and reporting. The existing RETURN_VALUE,
typed rejection and Throwable materialization produce the error; a distinct
nonowning fact stores only its return site, object, normalized message and line.
Capture validates that exact transition under current/native/class/source authority.
Pending admission also checks live Error fields; retired validation binds the same
source and abandoned native owner row. The existing T2/pending1, catch and normal
consumption protocols remain. Strict integer rejection and weak coercion give two
exact source agreements; 15 independent authority, C0/report/retirement, clearing
and cleanup groups pass. Normal publication has retvalT1 after castguard release;
the fatal branch keeps T2. Original fixture failures retain zero credit.
Owning rejected operands, wider producers, supplied identity, COMP88, custom
rendering and other holds remain outside. OB31 source performance stays unfinished.
[Author evidence](../../coverage/semantics/output-final-return-type-author.json) and
[review](../../coverage/semantics/output-final-return-type-review.json) retain the
actual 467-module joined load and the precise source/state cuts.

The same generated strict scalar return TypeError now crosses an empty method
frame. A common full native method/frame proof preserves the existing authority checks.
Structural constructor-birth capture retains its nonempty-CV gate; the separate
no-CV literal-throw route is unchanged. Only the actual
return-error producer and its live tag admit CV0. Source/catch/rootdrop and normal
clearing use that same distinction. The existing frame mechanism first queues a
release record with no jobs, then one genuine step retires that record before
original native C0 readiness. Both stages preserve T2/Error1 and public validity.
No local, destructor class, new fact or owner is added. Two minimal strict/weak
originals agree; the affected 10 and independent 12 authority, empty-release/C0,
report/retired-receipt, weak and clearing groups pass. No-variable catch and bare
finally overrides retain empty CVS/ENV and retire Error before normal publication.
Other producer, supplied/COMP88, owning-operand and rendering holds remain; prior
public performance limits stay separate.
[Author evidence](../../coverage/semantics/output-final-empty-return-author.json) and
[review](../../coverage/semantics/output-final-empty-return-review.json).

The generated scalar-return Error path also covers weak NULL rejection. Its
source proof follows the genuine failed check independently of strict mode;
successful TRUE coercion returns `1` and creates no fact. Own return membership,
compiled line, by-value/current/native authority, exact materialization and live
TypeError fields stay checked. The no-CV/no-destructor witnesses retain T2/error1
through the real empty release and original C0, with normal publication at T1.
Two exact originals and twelve independent source/authority, report/retirement,
coercion and clearing groups pass. No new receipt, owner, type checker or cleanup
protocol is introduced. Wider
producers, owning rejected operands, supplied identity, COMP88, constructor abort,
custom rendering and other held limits remain outside; OB31 performance stays open.
[Author evidence](../../coverage/semantics/output-final-weak-return-author.json) and
[review](../../coverage/semantics/output-final-weak-return-review.json).

Native `__toString` fallthrough now retains its genuine missing-return TypeError.
The actual TYPE_FALLTHROUGH and materialized successor bind the own method origin
and closing line, using the same four-field fact and normalized live checks.
No return operand, constructor birth, frame or owner is invented. The original
native T2/pending1, empty-release administration, C0 and retired-receipt rules apply.
The check follows the completed body; a return from finally prevents it.
Two missing/normal-H originals and ten affected source/owner/budget/public groups pass.
Twelve independent authority, report/retirement, normal return, prevention and
cleanup groups pass, including the real D cleanup before original C0.
The equivalent singleton guard uses a nonempty-list pattern plus an empty tail
to avoid the pinned SpecTec structurer's Cons/Fixed1 overlap error; vendor unchanged.
Wider producers, owning/noisy operands, supplied identity, COMP88, constructor abort,
by-reference results, custom rendering and other holds remain; OB31 performance stays open.
[Author evidence](../../coverage/semantics/output-final-missing-return-author.json) and
[review](../../coverage/semantics/output-final-missing-return-review.json).

Known numeric scalar division by zero in native `__toString` now retains the
existing arithmetic rule's DivisionByZeroError. Capture binds the real BINARY_RIGHT,
own operator site, RHS compiled line and exact materialized object; it keeps the
actual return/control tail. A separate fixed-kind arm reuses the four nonowning
fields, while shared generated-error readers retain normalized live fields and
the original native T2/error1, empty-release/C0 and retired-receipt protocols.
The TypeError-specific getter and constructor gates remain unchanged. Two divide0/
divide1 originals agree; ten affected source/owner/budget/public groups pass.
Fifteen independent authority, report/retirement, normal return, catch/finally
and cleanup groups pass; original normal-fixture failure stays zero.
This error occurs in the body, so catch/finally consumption is distinct from the
preceding post-body missing-return prevention. That cut did not expand owning,
noisy, nonnumeric or place operands, other producers, supplied/COMP88, constructor
abort, by-reference results, custom rendering or held limits; OB31 remains open.
[Author evidence](../../coverage/semantics/output-final-division-error-author.json) and
[review](../../coverage/semantics/output-final-division-error-review.json).

With no eligible Warning handler, a leading-number private CV divided by an
original compiled integer zero also retains its DivisionByZeroError through FINAL.
A separate capture arm uses unchanged Module35 and exact152. Existing source and
CONST slot proofs authenticate the original zero; private reads, rootless/S-aware
left strings, native/current/owner bounds and original PINT0 scratch remain.
One fresh native original ran once; its exact source comparison agrees. The
pre-edit raw1, author4 and independent9 SL groups retain their private505 cuts; the
original Warning/Unsupported baseline retains zero agreement. A separate divisor1
state control refuses substituted zero without adding native credit. Mask/display controls
preserve actual Warning projection; reached buffered stdout warnings stay
Unsupported. Other right-zero values/slots, handlers/producers/rendering, held
bounds and OB31 remain partial; joined loading stays separate.
[Default division Warning evidence](../../coverage/semantics/output-final-default-division-warning-error-author.json)
and [review](../../coverage/semantics/output-final-default-division-warning-error-review.json).

Original compiled quiet scalar-zero divisors share that capture: integer zero,
NULL, false, signed floating zeros and admitted full numeric zero strings. The existing
quiet-number and rootless/S-aware string guards retain the original operand;
own source/value and CONST proofs remain mandatory. Module35 preserves its type
and zero sign before exact152, so equal Error images cannot authorize substituted
values. Numeric-string retirement adds no owner. Genuine nonzero divisors cannot
mint a zero Error; leading-number RHS conversions use the ordered Warning capture below.
Temporary operand results, handlers, producers, ownership and rendering limits stay partial.
[NULL-divisor evidence](../../coverage/semantics/output-final-default-null-division-warning-error-author.json)
and [review](../../coverage/semantics/output-final-default-null-division-warning-error-review.json).
[Scalar-zero evidence](../../coverage/semantics/output-final-default-scalar-zero-division-warning-error-author.json)
and [review](../../coverage/semantics/output-final-default-scalar-zero-division-warning-error-review.json).

An initialized quiet RHS CV uses the same capture after the unchanged private
reader authenticates its own name, read line and one-owner ordinary cell.
Its current value, including a valid request string, survives in raw scratch;
an equal-valued other CV, KNOWN copy or wrong line cannot replace the operand.
All three witness locals retire before C0; receipt validation does not reread
retired operands. Reference/backed/global/static cells and temporary results remain
outside this addition.
[Own-CV divisor evidence](../../coverage/semantics/output-final-default-cv-zero-division-warning-error-author.json)
and [review](../../coverage/semantics/output-final-default-cv-zero-division-warning-error-review.json).

With no eligible Warning handler, DIV also retains a right-only Warning or both
operand Warnings before DivisionByZeroError. Its private left CV may hold a quiet
scalar, full numeric string or leading-number string; the latter warns first.
Original CONST1 or own-CV8 RHS authority, valid current carriers, raw unconverted
RHS scratch and exact152 remain required. At least one conversion warns, preserving
the quiet arm unchanged. Four exact source comparisons reuse four saved native originals
once. Author4, independent7 and the two affected one-group guards retain separate
fixture-SL cuts. Three actual CV cells retire before C0; equal Errors cannot
authorize replacement operands or missing diagnostics. Eligible handlers, wider
slots/producers, owning/reference operands, rendering/lifetimes and OB31 remain partial.
[Ordered operand Warning evidence](../../coverage/semantics/output-final-default-division-operand-warning-error-author.json)
and [review](../../coverage/semantics/output-final-default-division-operand-warning-error-review.json).

An original compiled scalar CONST may also supply the left operand when the RHS
is its own private CV8. Exact child0 source, compiled value/carrier and CONST1
rank remain mandatory; a permissive KNOWN read or equal Error cannot replace
them. At least one numeric conversion warns; the left-only case follows the
unchanged conversion law and quiet RHS-CV admission. Existing CV8-left/right1|8
behavior remains pointwise, while CONST1/CONST1 stays outside this addition even
with valid source, raw Error and live locals. Three right-only/both-Warning source
comparisons reuse natives once; author4 and independent7 retain separate fixture-SL
evidence. The two real private CV cells retire before C0; the retired receipt
keeps static source and no operand owner. Other pairings, owning/reference/TMP operands, handlers,
producers/rendering/lifetimes and OB31 remain partial.
[Compiled-left evidence](../../coverage/semantics/output-final-default-constant-left-division-warning-error-author.json)
and [review](../../coverage/semantics/output-final-default-constant-left-division-warning-error-review.json).

An empty-CV method also admits an original compiled CONST1/CONST1 division pair.
The function and current CVS and current ENV must all be empty; both original
values, string carriers, source children, ranks and compiled lines remain required.
The pinned compiler retains this runtime DIV, and unchanged35 preserves ordered
Warnings before exact152 materializes DivisionByZeroError. Three right-only/both-Warning
originals agree with saved natives. Five author SL groups reach the actual empty
release, C0 and retired receipt; nine independent groups preserve source/carrier/line
refusals and the old live-unused-CV pair refusal. Native T2/Error1 becomes T2/Error0
without operand owners. Existing CV pairings stay pointwise; other slots, handlers,
producers/rendering/lifetimes and OB31 remain partial.
[Constant-pair evidence](../../coverage/semantics/output-final-default-constant-pair-division-warning-error-author.json)
and [review](../../coverage/semantics/output-final-default-constant-pair-division-warning-error-review.json).

A separate empty-CV MOD arm retains one leading-number Warning before modulo by
zero. Its original compiled left string must have exactly the LEADINGNUMBER
notice and its original RHS must be integer0, with both CONST source/rank proofs.
Unchanged54 converts left then right and retains integer0 scratch before exact152.
Integer-prefix and compatible float-prefix originals agree with saved natives;
five author SL groups reach empty release/C0/Error retirement and eight independent
groups check source/carrier/line, genuine nonzero-RHS, masked precision-loss and
allocated unused-CV refusals. Separate actual MAIN508 loading passes/source0.
Hiding Deprecated cannot admit an extra conversion notice. The old DIV and quiet
MOD clauses stay literal; other RHS values, cells,
handlers, producers/rendering/lifetimes and OB31 remain partial.
[MOD Warning evidence](../../coverage/semantics/output-final-default-constant-modulo-warning-error-author.json)
and [review](../../coverage/semantics/output-final-default-constant-modulo-warning-error-review.json).

The same empty-CV MOD arm also accepts its own compiled quiet scalar-zero RHS,
including NULL, false, compatible float0 and a full numeric string0. Existing
quiet-integer conversion, rootless values, valid string carriers and exact original
CONST sources/ranks remain required; raw54 still leaves converted integer0 scratch.
Four exact originals reuse four native observations once. Five author SL groups
reach actual empty release/C0/Error retirement; independent stages2/2/2/2 reject
equal-Error NULL/false substitution, same-byte REQUEST strings, genuine nonzero
source replacement and masked noisy-RHS conversion. These private505 cuts remain
separate from the accepted combined MAIN508 load (15.373098855 s/source0).
Other RHS slots, eligible handlers,
wider producers/rendering/lifetimes and OB31 remain partial.
[Quiet-zero MOD evidence](../../coverage/semantics/output-final-default-quiet-zero-modulo-warning-error-author.json)
and [review](../../coverage/semantics/output-final-default-quiet-zero-modulo-warning-error-review.json).

The sole-Warning MOD arm also accepts its own initialized quiet scalar-zero RHS
CV8 with the same original CONST1 left. The unchanged private reader checks the
literal child name, compiled line, unique unmarked cell, backing restrictions
and quiet read; the old CONST1 RHS still requires empty CVS/ENV. Two originals
agree with saved natives once. Five author SL groups check actual two-cell
retirement before C0, Warning/fatal order, zero budgets and the nonowning receipt.
Separate peer stages3/2 preserve forged-line, reference-mark and invalid string
identity refusals; a valid REQUEST string in the own CV accepts. Equal complete
Errors cannot authorize a different same-valued CV. Private505 cuts stay separate
from the accepted combined MAIN508 load (15.800782290 s/source0). Wider operands,
handlers, producers, rendering/lifetimes and OB31 remain partial.
[RHS-CV MOD evidence](../../coverage/semantics/output-final-default-cv-zero-modulo-warning-error-author.json)
and [review](../../coverage/semantics/output-final-default-cv-zero-modulo-warning-error-review.json).

An own initialized leading-number left CV8 also admits its original quiet-zero
CONST1 RHS. The unchanged private reader, source/line proofs and sole-LEAD
conversion bound remain; the old CONST-left pairings stay pointwise. Two
integer-prefix/compatible float-prefix originals reuse saved natives once.
Author SL5 checks actual two-cell retirement before C0, Warning/fatal order,
nonowning receipt and same-valued left-CV refusal. Separate peer stages2/1 reject
a same-Error replacement RHS and genuine own CV8/CV8 operands with all other
admission guards. Private505 cuts stay separate from the accepted combined
MAIN508 load (15.094850045 s/source0). That cut leaves both-CV pairings outside
capture. Extra conversion notices, other slots, handlers, producers,
rendering/lifetimes and OB31 remain partial.
[Left-CV MOD evidence](../../coverage/semantics/output-final-default-left-cv-modulo-warning-error-author.json)
and [review](../../coverage/semantics/output-final-default-left-cv-modulo-warning-error-review.json).

Own initialized CV8/CV8 operands now compose under the same sole-LEAD/quiet-zero
bounds. Only the pair-matrix condition changes; both private readers and all
source, conversion, raw54/152 and native ownership guards remain. Two originals
reuse saved natives once. Author SL4 reaches actual two-cell retirement/C0 and
the nonowning receipt; fresh peer SL3/2 checks right-line/reference refusals and
valid/invalid REQUEST identity. The old integer-pair refusal keeps its original
cut; only its exact affected expectation is promoted and tested freshly in SL1,
with source0. Old RHS/source/native campaigns are not replayed. These private505
cuts stay separate from the accepted combined MAIN508 load (15.115694686 s/source0).
Wider places, extra notices, handlers, producers, rendering/lifetimes and OB31
remain partial.
[CV-pair MOD evidence](../../coverage/semantics/output-final-default-cv-pair-modulo-warning-error-author.json)
and [review](../../coverage/semantics/output-final-default-cv-pair-modulo-warning-error-review.json).

The native return-TypeError path also accepts an initialized ordinary scalar CV.
The original VARIABLE operand must match a literal own Return-child name and
compiled line, with one live private cell and no global/static, reference,
backing or borrowed-read authority. Its genuine read changes only RESULT before
the unchanged return check and materialization. The same four-field Error fact
survives scalar-cell retirement to original C0 with T2/Error1; it retains no cell.
Strict/weak originals agree and eight affected read/owner/budget/public groups
pass; sixteen independent guard/report/clearing and cleanup groups pass. Undefined/noisy,
owning, computed/place, shared/reference/backed operands and wider producers
remain outside; OB31 performance and other holds remain unfinished.
[Author evidence](../../coverage/semantics/output-final-cv-return-type-author.json) and
[review](../../coverage/semantics/output-final-cv-return-type-review.json).

Integer modulo by zero now reaches that same fixed DivisionByZeroError protocol.
The actual BINARY_RIGHT operator must equal the operator authenticated from its
own Div/Mod source node; MOD admits known PINT operands and PFLOAT values whose
actual integer conversion produces no diagnostics. DIV keeps its existing
numeric guard. Own function membership, compiled RHS line and exact
raw/materialized identity remain required, with the original control tail.
The four fields, normalized image, native T2/Error1, real empty-release/C0 and
retired reporting readers are shared. Two modulo originals and ten affected
groups pass; fifteen independent refusal/report/normal/clearing/cleanup groups pass.
Other coercions, noisy/nonnumeric/owning/place operands and wider producers remain
outside; prior held bounds and OB31 performance remain unfinished.
[Author evidence](../../coverage/semantics/output-final-modulo-error-author.json) and
[review](../../coverage/semantics/output-final-modulo-error-review.json).

Quiet PFLOAT admission uses the existing `float_long(bits, true) = (integer, eps)`
result. Module54 still performs both coercions in order: raw RESULT becomes the
RHS integer before the zero-divisor error and exact Module152 materialization.
Four originals agree under90; ten affected and ten independent groups pass,
including real empty-release/C0 and catch/finally clearing. Four reached lossy
refusal groups preserve the precision diagnostic and Unsupported boundary.
The two affected old float-refusal guards are now positive; the old integer
campaign is not replayed. No fact, field, owner, root or numeric rule is added.
[Float author evidence](../../coverage/semantics/output-final-quiet-float-modulo-author.json)
and [review](../../coverage/semantics/output-final-quiet-float-modulo-review.json).

Known-integer negative LEFT/RIGHT shifts now retain their ArithmeticError through
that lifecycle. The actual shift opcode must match the own ShiftLeft/ShiftRight
node, function membership and compiled RHS line. Exact existing kernel/raw152
identity and current/native/owner bounds mint a distinct fixed-kind source arm
using the same four nonowning fields. Generated live/source/clearing and retired
report readers include this earned tag without adding cell or object owners.
All three originals agree; ten left-shift checks cover native empty-release/C0,
and four right-shift checks cover source/capture/pending. Nineteen independent
authority/report/normal/clearing/cleanup groups pass on first attempts. The actual
478-module interface load passes with zero source credit; private 475 checks keep
their original cuts. Float/coercion,
noisy/owning/place operands, wider producers and held domains remain outside;
OB31 performance is not renewed.
[Author evidence](../../coverage/semantics/output-final-shift-error-author.json) and
[review](../../coverage/semantics/output-final-shift-error-review.json).

An exhausted scalar match scan now retains its genuine UnhandledMatchError through
that lifecycle. Capture binds the own MATCH_SCAN origin, pool-backed known integer
subject, terminal cursor/no default, scan mode and compiled match line. The real
144 request drops its task tail; the Throwable transition restores the original
continuation before materialization and charged catch/finally unwinding. Exact 152 materialization and nonowning
RESULT/BASE/HELD/tasks remain required. A distinct fixed-kind source arm reuses
four fields; generated live/clearing/report readers preserve T2/Error1 without a
new owner or constructor birth. Ten affected checks pass through actual empty
administration to original C0. Both originals agree in 77.920/46.931 seconds
under 90; fifteen independent source, report, normal and clearing groups pass. The
actual current 480-module load passes with zero source credit; private 478 cuts
stay separate. Noisy/owning/place or
wider subjects/producers and held domains remain outside; OB31 performance stays
unfinished.
[Author evidence](../../coverage/semantics/output-final-match-error-author.json) and
[review](../../coverage/semantics/output-final-match-error-review.json).

The same match-error lifetime now accepts compiled table dispatch when the own
function and actual source unit each provide the same present mode boolean.
Missing or conflicting facts refuse; pool-backed PINT/terminal/no-default/source,
actual materialization, current/owner and retired-receipt bounds stay unchanged.
The four-field tag, match kernel and renderer are unchanged.
Source and tests are accepted with the current predicate/default bridge; the
latest actual interface load predates this change and adds no source credit.
[Table-mode evidence](../../coverage/semantics/output-final-match-table-author.json) and
[review](../../coverage/semantics/output-final-match-table-review.json).

Quiet integer-plus-nonnumeric-string ADD rejection now supplies a distinct
fixed-TypeError source tag using the existing four nonowning fields. Actual
known operands, rootless string/BADNUMBER, unchanged events, own Plus/compiled RHS
line and exact materialization authenticate the producer. Existing native T2/Error1,
empty administration/C0, clearing and snapshot-only retired receipts retain their
protocol. No arithmetic kernel, new read authority or renderer is introduced.
The actual current 482-module interface load passes with zero source credit;
private 481-module source and state cuts remain separate.
[Arithmetic evidence](../../coverage/semantics/output-final-arithmetic-type-error-author.json) and
[review](../../coverage/semantics/output-final-arithmetic-type-error-review.json).

Quiet SUBTRACT and MULTIPLY rejection now share that arithmetic TypeError source.
An own Plus/Minus/Mul selector must equal the actual opcode; coherent mismatched
opcodes refuse. Known integer/rootless-string, quiet failure, exact materialization,
native/current/owner and retired-receipt bounds remain unchanged. No new tag,
read, owner, arithmetic kernel or renderer is added.
[Operator evidence](../../coverage/semantics/output-final-arithmetic-operator-author.json) and
[review](../../coverage/semantics/output-final-arithmetic-operator-review.json).

Quiet DIVIDE rejection now joins the arithmetic TypeError selector through its
own Div source. The actual opcode/operand/materialization/current/owner proof is
unchanged; numeric divide-by-zero keeps its distinct kind and numeric-only issuer.
No new tag, field, read, root, arithmetic kernel or renderer is added.
[Division TypeError evidence](../../coverage/semantics/output-final-divide-type-error-author.json) and
[review](../../coverage/semantics/output-final-divide-type-error-review.json).

Quiet MODULO rejection joins that TypeError selector through its own Mod source.
The real integer coercion can change raw RESULT before right-string rejection;
capture retains the original operands and exact materialized successor. The raw
integer result is nonowning, and numeric Modulo-by-zero keeps its separate kind.
No new tag, field, read, root, kernel or renderer is added.
[Modulo TypeError evidence](../../coverage/semantics/output-final-modulo-type-error-author.json) and
[review](../../coverage/semantics/output-final-modulo-type-error-review.json).

MODULO TypeError capture also admits quiet integer-coercible non-PINT left values
before a BADNUMBER right string. Both original values remain rootless and each new
string passes its S-aware identity check. Module54 converts the left value before
rejecting the right, preserving original type names in exact Module152 materialization.
The old PINT arm keeps its original KNOWN-right authority pointwise. Two originals,
eight actual CV/C0/retired-receipt groups and eighteen independent guards pass at
their private 505-module cuts. Normal/noisy/reference baselines retain zero new source
credit without replay; the fresh plain-string guard validates the sole old MOD
expectation promotion. Native owners, four-field facts, other opcodes and all
existing lifetime/held bounds stay unchanged; OB31 performance remains unfinished.
[Coercion evidence](../../coverage/semantics/output-final-quiet-modulo-type-coercion-author.json)
and [review](../../coverage/semantics/output-final-quiet-modulo-type-coercion-review.json).

ADD/SUB/MUL/DIV TypeError capture shares the existing quiet scalar-number
admission for non-PINT left values. Both original values stay rootless and each
string passes its S-aware identity check. Genuine Module35/404/152 retains RHS
scratch, original type names and the target's multiplication slot order; the
old PINT and MODULO branches remain pointwise. Four originals, eight actual
CV/C0/retired-receipt groups and 21 independent groups pass at their private
505-module cuts. Fresh coherent plain-string guards validate three old expectation
promotions without replay; normal/noisy/reference controls retain their distinct
outcomes and zero new source credit. Source/tests and registration are integrated;
the separate actual `7251409ec` joined507 SL load passes with zero source credit.
Existing ownership, lifetime and held bounds remain; OB31 public performance
remains unfinished.
[Arithmetic coercion evidence](../../coverage/semantics/output-final-quiet-arithmetic-type-coercion-author.json)
and [review](../../coverage/semantics/output-final-quiet-arithmetic-type-coercion-review.json).

Returning named Warning handlers also retain the existing arithmetic RIGHT-stage
TypeError through FINAL. A disjoint capture arm authenticates the real Module404
failure, live physical operands and saved numeric holder, null scratch and exact152
materialization. Own source/private-CV, rootless/S-aware string and native ownership
guards remain; quiet capture stays pointwise. Five originals, eight corrected
CV/C0/retired-receipt groups and 16 independent groups pass at private505 cuts.
The original rootless handlers restore directly; one separate unused-class fixture
checks existing empty cleanup without an instance or old-Value owner. Preparatory
fixture failures and their resolving diagnostic retain zero source credit.
Source/tests are integrated through `e1025e63c`; its separate actual joined508 SL
load passes with source0. Held contours and OB31 performance remain unfinished.
[Warning/TypeError evidence](../../coverage/semantics/output-final-arithmetic-warning-type-error-author.json)
and [review](../../coverage/semantics/output-final-arithmetic-warning-type-error-review.json).

With no eligible Warning handler, leading-numeric ADD/SUB/MUL/DIV failures also
retain their TypeError through FINAL. The separate BINARY arm authenticates both
rootless string identities and private reads, unswapped physical slots, original
RHS scratch, the existing mask/display-aware Warning and exact35/152 successor.
Five source comparisons, eight lifecycle groups and eleven independent groups
pass at separate private505 cuts. One earlier noisy refusal becomes an exact
positive guard, checked afresh among those eleven groups. Quiet and returning-handler
arms stay literal; wider operands/producers, all held contours and OB31 performance
remain partial. Joined interface evidence stays separate from these source cuts.
[Default Warning evidence](../../coverage/semantics/output-final-default-arithmetic-warning-type-error-author.json)
and [review](../../coverage/semantics/output-final-default-arithmetic-warning-type-error-review.json).

Quiet nonnumeric left strings with quiet numeric right scalars also retain their
ADD/SUB/MUL/DIV TypeErrors through FINAL. Genuine private/known reads, rootless
and S-aware string identity, physical slots, original RHS scratch, unchanged raw
events and exact152 preserve the original operand types. Six originals, eight
CV/C0/retired-receipt groups and twelve independent authority groups pass at
separate private505 cuts. The heterogeneous swapped-MUL case distinguishes native
physical order; leading RHS and both-BAD strings remain outside this increment.
The prior normal original/native result is reused without replay or renewed
credit. A compile-only reviewer preparation failure retains zero application
credit; no semantic/source/native failure or cap change arose. Existing kernels,
tasks, fields, roots, lifetime and held bounds remain; OB31 remains unfinished.
The separate actual `37f36b283` joined508 SL load passes with zero source credit.
[Left-error evidence](../../coverage/semantics/output-final-left-arithmetic-type-error-author.json)
and [review](../../coverage/semantics/output-final-left-arithmetic-type-error-review.json).

That RHS admission now also accepts genuine nonnumeric strings. Both original
strings retain their S-aware identity, rootless, source/slot/raw-scratch and
exact152 proofs; leading RHS and nonstring BAD values remain outside. Five
originals, four CV/C0/retired-receipt groups and nine independent groups pass at
separate private505 cuts. Distinct X/Y values authenticate swapped-MUL scratch;
its string/string type text alone does not distinguish order. Prior normal and
heterogeneous-order evidence retain their own cuts without replay. A preparation
assertion before file write/application retains zero credit; execution had no
failure or cap change. Kernels, ownership, lifetime and held bounds stay unchanged.
The separate actual `70377d7c7` joined508 SL load passes with zero source credit.
[Both-string evidence](../../coverage/semantics/output-final-both-string-arithmetic-type-error-author.json)
and [review](../../coverage/semantics/output-final-both-string-arithmetic-type-error-review.json).

A nonnumeric first operand can also prevent a leading-number right string from
warning. That new admission requires actual unswapped physical operands; existing
quiet-number/BAD right branches retain their prior order. Four originals, four
CV/C0/retired-receipt groups and twelve independent groups pass at private505
cuts. The peer includes four fresh conditions for the two affected old guard
promotions, without replaying their campaigns or native originals. At that cut,
the true-swapped control remained Unsupported with P/empty model stderr versus
native Warning then TypeError, with zero agreement.
Normal evidence retains its prior cut. A read-only raw-format check note has zero
credit; execution had no failure or cap change. Kernels and lifetime stay unchanged.
[Leading-right evidence](../../coverage/semantics/output-final-leading-right-arithmetic-type-error-author.json)
and [review](../../coverage/semantics/output-final-leading-right-arithmetic-type-error-review.json).

Default true-swapped MUL now converts its leading-number RHS before rejecting the
BAD lexical left. Module404 authenticates source, physical slots and live values,
then calls unchanged Module35 arithmetic in physical order. A separate FINAL arm
preserves original RHS scratch, mask/display-aware Warning events and exact152
under the existing private-read, string, rootless, native/current and owner bounds.
One fallback-only SL checkpoint precedes capture. One original agrees using the
saved native61 control once; author4 and independent10 SL groups pass at private505
cuts. The peer includes two fresh conditions for the affected old61 guards;
historical Unsupported and normal evidence retain their cuts without replay.
The quiet false-swap guard remains necessary when a Warning is masked. At that cut,
the opposite swapped leading-left/BAD-right case remained partial; wider contexts,
held bounds and OB31 remain partial, with joined interface evidence separate.
[Swapped Warning evidence](../../coverage/semantics/output-final-swapped-arithmetic-warning-type-error-author.json)
and [review](../../coverage/semantics/output-final-swapped-arithmetic-warning-type-error-review.json).

That opposite default-MUL case now rejects the BAD original RHS first, before its
leading lexical left can warn. A disjoint Module404 arm retains source, slot, selected live
value and string identity proofs, then calls unchanged Module35 in physical order.
A separate FINAL arm preserves quiet raw events, original BAD RHS scratch and
exact152 under the existing private-read, native/current and owner bounds.
One fresh native original ran once; the pre-edit Warning/Unsupported baseline
retains zero agreement. One original now agrees; fallback1, author4 and independent10 SL groups
pass at their private505 cuts. The peer includes exactly two fresh old58 guard
promotions; other campaigns retain their cuts without replay. Its stdout profile
proves only quiet raw dispatch/capture, without granting later C0 stdout rendering.
Wider handlers/producers/operands/rendering, held bounds and OB31 remain partial;
joined interface loading stays separate.
[First-BAD evidence](../../coverage/semantics/output-final-swapped-left-arithmetic-type-error-author.json)
and [review](../../coverage/semantics/output-final-swapped-left-arithmetic-type-error-review.json).

Quiet SHIFTLEFT/SHIFTRIGHT/BITAND/BITOR/BITXOR TypeErrors now share that source tag
after each actual opcode matches its own nominal source node. The same known
PINT/rootless-string/quiet failure and actual integer conversion/Throwable proof apply. Numeric
negative shifts retain ArithmeticError, and both-string bitwise operations keep
their byte path. One full cleanup boundary and focused source/pending checks
retain the native owners; no new field, root, kernel or renderer is added.
[Integer operator evidence](../../coverage/semantics/output-final-integer-type-error-author.json) and
[review](../../coverage/semantics/output-final-integer-type-error-review.json).

Quiet POWER rejection now joins the TypeError selector through own Pow. The actual
PINT-left/BADNUMBER-right branch preserves raw string RESULT before real Throwable
materialization; three power-plan optionals are observed without imposing new
guards. Native/current/owner/report bounds remain unchanged, with no new field,
root, numeric kernel or renderer.
[POWER evidence](../../coverage/semantics/output-final-power-type-error-author.json) and
[review](../../coverage/semantics/output-final-power-type-error-review.json).

Unary PLUS/MINUS rejection now uses own UnaryPlus/UnaryMinus source and the actual
UNARY direction. Both errors share the native string-times-integer text; equal
raw/materialized images do not grant opposite-direction or binary-MUL capture.
The source arm requires the own unit, nonfolded operator and compiled child0 line;
capture retains the original KNOWN rootless BADNUMBER string, unchanged events,
real Throwable transition and existing native/current/owner bounds. Binary capture,
the four-field tag, readers, numeric kernel and renderer stay unchanged.
[Unary evidence](../../coverage/semantics/output-final-unary-type-error-author.json) and
[review](../../coverage/semantics/output-final-unary-type-error-review.json).

Quiet bool/null BITNOT errors now retain their own BitwiseNot source through FINAL
conversion. Its original KNOWN branch admits true/false/null; own unit,
nonfolded operator, compiled child0 line and the explicit capture-site check bind
the distinct native messages to genuine57/58/152 transitions. A real arithmetic
parent may satisfy the shared snapshot source proof while BITNOT capture refuses.
Native/current/owner, empty-release/C0, clearing and retired receipts retain the
existing fixed TypeError tag and four fields. Integer/string success and float
warning paths keep their prior semantics; no kernel, root or renderer changes.
[Bitwise-not evidence](../../coverage/semantics/output-final-bitnot-type-error-author.json) and
[review](../../coverage/semantics/output-final-bitnot-type-error-review.json).

Division/modulo-by-zero and negative-shift captures, together with the existing
binary/unary/BITNOT TypeError captures, share a private compiled-variable operand
proof. The current function/unit, literal child name and compiled line authenticate
an actual defined, allocated cell with one owner, no reference/global/static/backing
or borrowed-read authority, and an exact quiet read. Operator CVs admit plain
scalars and validated string carriers; the
old KNOWN paths and return scalar filter remain pointwise. Original operands pass
through genuine ordered reads, source dispatch and Throwable materialization,
preserving mixed multiplication's native operand order. Existing four-field facts
survive real CV retirement, C0 and catch/finally clearing without adding owners.
Seven originals agree; the reference control remains Unsupported with zero
agreement. Wider issuers and OB31 public performance remain unfinished.
[Operand evidence](../../coverage/semantics/output-final-scalar-cv-error-author.json)
and [review](../../coverage/semantics/output-final-scalar-cv-error-review.json).

Unmatched scan/table expressions in that native method now admit a quiet private
scalar CV through the same own-child/compiled-line/cell read proof. The actual
terminal Module144 read observes mutation by conditions; exact152 materialization
retains its message. Static own-unit, literal child, CODE/CVS and global/static
bounds authenticate later readers without rereading a retired cell. The existing
four-field match fact and native T2/Error1 owners survive real CV cleanup and
Error retirement; a forged abandoned-native source site refuses. The old KNOWN
pool-PINT path remains pointwise. Eight original agreements, 18 independent SL
groups and two actual retired-receipt groups pass at their separate 496-module cuts.
Reference/undefined controls and both AL300 timeouts have zero agreement; timeout
causes remain undetermined and caps are unchanged. Wider subjects/places,
held issuers/rendering and OB31 public performance remain partial.
[Match-CV evidence](../../coverage/semantics/output-final-cv-match-error-author.json)
and [review](../../coverage/semantics/output-final-cv-match-error-review.json).

DIV/MOD zero-error capture now shares the existing quiet scalar-coercion laws.
Boolean/null and full numeric strings may pass DIV's `COERCED(_, false)` test;
MOD uses its actual string-long `STRINT(_, eps)` result, including saturation.
The old PINT/PFLOAT branches remain pointwise. Capture validates both original
operands as rootless and checks each string identity before authenticating genuine
ordered35/54 and exact152 materialization. DIV preserves RHS carrier scratch;
MOD produces the RHS integer. The existing four-field fact and cleanup reach the
actual retired Error/native receipt.
Three source agreements, two retired-receipt groups, seven independent DIV, eight
MOD and three separately corrected noisy groups pass at their 501-module cuts.
At that 501-module cut, noisy production retained deprecation output and Unsupported; both
unexecuted noisy-fixture failures retain zero credit. Only the affected stage
reran; caps, all held bounds and unfinished OB31 public performance remain
unchanged. The actual joined503 SL interface load is separate from private501
source/state evidence and adds zero source credit.
[Coercion evidence](../../coverage/semantics/output-final-quiet-zero-coercion-author.json)
and [review](../../coverage/semantics/output-final-quiet-zero-coercion-review.json).

Negative SHIFTLEFT/SHIFTRIGHT errors share that quiet integer-conversion admission.
Both original operands pass the existing `$ob_object_modulo_integer`, rootless and S-aware
string checks before genuine ordered Module54 conversion and exact152 materialization.
The raw result retains the converted RHS integer; own opcode/unit/function/RHS
line and native/current/owner authority remain required. The four-field fact,
CV retirement, original C0 and retired Error/native receipt stay unchanged.
Three originals agree at private504; four actual retirement/receipt groups and
independent LEFT6/RIGHT6/noisy3 groups pass at their separate cuts. The derived
two-noisy fixture retains left-then-right deprecations before the negative-shift
error. Noisy and reference source controls remain Unsupported with zero agreement;
wider operand/issuer/lifetime bounds and OB31 performance stay partial.
[Shift coercion evidence](../../coverage/semantics/output-final-quiet-shift-coercion-author.json)
and [review](../../coverage/semantics/output-final-quiet-shift-coercion-review.json).

An empty-CV method now retains the ordered numeric Warning and precision-loss
Deprecated before a MOD zero Error from its own fractional-prefix CONST pair.
The extra diagnostic requires rank1/rank1, no eligible Warning/Deprecated handler
and exactly two visible events from the unchanged conversion helper. Existing
warning-only CV/CONST combinations remain pointwise. Two exact originals reuse
native observations once at private505; author lifecycle6, affected old71 noisy2
and independent profile3/scope1 groups retain separate source0 cuts. Masked
diagnostics and a genuine fractional-prefix CV pair still refuse this new capture.
Actual combined MAIN508 SL loading at `39c2183eb` passes separately with source0.
Wider operands, handlers and lifetimes remain partial; OB31 stays unfinished.
[Fractional MOD evidence](../../coverage/semantics/output-final-default-fractional-modulo-warning-error-author.json)
and [review](../../coverage/semantics/output-final-default-fractional-modulo-warning-error-review.json).

That visible fractional-prefix MOD sequence also accepts an own quiet-zero RHS
CV with the original CONST left. Exact source, compiled line and unique unmarked
cell authenticate the right value; it retires before C0. Old empty-CV CONST pairs
and sole-LEAD combinations remain pointwise. Two private505 originals reuse native
observations once; author SL4 and independent SL3/1 retain separate source0 cuts.
Changed right-read lines, marked cells and genuine left-CV precision still refuse.
Actual combined MAIN508 SL loading at `f1b8fb03e` passes separately with source0.
Other noisy pairings, handlers and lifetimes remain partial; OB31 is unfinished.
[Fractional RHS-CV MOD evidence](../../coverage/semantics/output-final-default-fractional-cv-zero-modulo-warning-error-author.json)
and [review](../../coverage/semantics/output-final-default-fractional-cv-zero-modulo-warning-error-review.json).
