# Ordinary source destruction

Module270 runs automatic `__destruct()` when an admitted ordinary operation
releases the last owner. It reuses257's ordered release jobs, once marks, receiver
calls and frame cleanup. MAIN is a real source caller even without a model call
frame: private access errors are catchable and traces retain the releasing line.
The terminal C boundary instead uses internal traces and `Unknown:0` visibility
warnings.

Consumed slots decrement in native order. Remaining slots stay owned while an
earlier destructor runs or throws; replacement exceptions chain through the rest
of the loop. Assignment installs its new binding before releasing the old value.
Used results retain their copied owner. Unused variable assignments and
ArrayAccess Set calls have no copied opcode result; other live owners determine
whether the RHS survives receiver or old-value destruction.
A plain-CV property receiver is borrowed. Computed property RHS temporaries have
the native cold versus warm write-site lifetime, separately from a used result.
Array COW, embedded references and resurrection retain their actual owners.
Dynamic object properties release before declared slots; Closure captures release
before the bound receiver.

Ordinary frame cleanup keeps257's caller restoration, compiled-CV order and
returned-value destinations. Interrupted operations retain only their genuine
result, base, pending Throwable and completion owners. Their source and saved
caller certificates add no roots. An entered helper cleanup validates its
producer against the genuine saved emitter frame. The internal destructor frame
binds its receiver, target, source site, line and saved caller context; its caller
origin remains separate from that site. Destructor eval/include bodies reuse the
existing source service and histories.

Pruning prepares the object store and fatal marks once, then selects the same
unsupported, refused, pending-release or store-drop result. Unmatch in preparation,
classification or selected results retains the original-state fallback. On the
private `5559f2c00` cut, strict305 initialization,110 source-reached/controlled
branch and fallback predicates, GEN63 and the parent-child WeakReference original
pass. The selected-result Unmatch fallback remains statically reviewed; the full
default retry still exceeds host55. No speedup or whole-retry agreement is claimed.
The actual309 join preserves current collector/caller hooks and passes strict
initialization on `13bc4e931`; it adds no lifecycle/source renewal.

Exception-handler return values release before the original Throwable and before
the old handler is restored. Error-handler return values release before restoring
the old error handler. A replacement installed by either body remains active.
An error-handler retval destructor has an internal API trace but retains the
actual USER caller's permission and catch continuation. Retired selected Closure,
method and raw-array identities remain borrowed lookup evidence.

Array eval/include warning cleanup keeps the authentic source operand marker
through the remaining error-handler cleanup wrapper. Marker matching still uses
the first matching task and its exact suffix. The actual287 lifetime original
now matches its whole native stream: a borrowed Array retires before provider
selection, while a captured Array retires after selection and before body entry.
The reached regression rejects an earlier identical marker with a forged tail
and preserves zero-budget identity and one-step retirement.

An unhandled Throwable first finishes formatting and freezes diagnostic bytes,
mask and destination. Its original owner then releases before the shutdown queue,
including an empty queue. That destructor can append callbacks, change the exit
status or throw; it cannot rewrite the already emitted diagnostic. A remaining
global, previous-chain or captured receiver owner delays the release normally.

An uncaught throw or graceful exit at a null-C destructor boundary bypasses
native post-call decrements. Authenticated abandoned C zvals retain two receiver
counts after a public call, or one store-wrapper count after an inaccessible-method
warning.
The disabled error callback's raw zval also remains retained on that bailout.
Those owners and any pending slots survive into request stage2; active borrowed
call markers retire. This phase does not claim their later request freeing.

An engine fatal bailout also skips live VM frame cleanup. The snapshot retains
current and saved local, receiver and temporary owners before structural cleanup;
MAIN's global table remains borrowed. Source/handler/eval lookup rows and the
sampled reporting mask authenticate the interrupted producer without adding
owners. Compiler replay matches its exact completion, origin and declaration
prefix within the live timeline, including later shutdown publications. Retired
cursor lookup separately uses its pre-resume pause claim and exact plan. A
precision resume can change the installed image without changing that plan.
Fatal shutdown callbacks stop the remaining queue rather than restart it.

Fiber291/302 move automatic-destruction calls, slot releases, frame cleanup,
interrupted operations and handler cleanup with each genuine VM stack. Shared
abandoned owners, handles and property caches remain shared. Ordinary captured
cleanup can suspend and resume. Module 308 adds protected real-exception cleanup
after an actual return; the body-undefined protocol, request/fatal cleanup and
wider consumers remain required. [The Fiber contract](FIBERS.md) records the
bounded cuts.

The source truth is `Zend/zend_vm_def.h` assignment/FREE_OP and leave routes,
`Zend/zend_object_handlers.c::zend_std_write_property`,
`Zend/zend_objects.c::zend_objects_destroy_object`,
`Zend/zend_objects_API.c::zend_objects_store_del`, and
`Zend/zend.c` error/exception handler return cleanup.

```sh
python3 tests/semantics/eager_destructor_review.py
python3 tests/semantics/eager_destructor_state_review.py
python3 tests/semantics/eager_fatal_review.py
python3 tests/semantics/eager_fatal_state_review.py
python3 tests/semantics/eager_fatal_precision_state.py
python3 tests/semantics/eager_fiber_state.py
```

[Author cuts](../../coverage/semantics/eager-destructors-review.json) keep exact
source observations separate from independent reached-state review. The two
earlier257 release controls now expect supported behavior; their original
Unsupported observations retain zero agreement at that cutoff.
Compound property Stringable reception keeps its existing explicit Unsupported
boundary and remains required follow-on work. Cycles/GC, weak references, output
buffers, shutdown registration release and final request freeing also remain
required. Return verification stays paused; this phase uses accepted ordinary
return behavior and does not close complete core.
