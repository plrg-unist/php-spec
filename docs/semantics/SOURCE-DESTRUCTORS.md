# Request-stage source destructors

Module257 implements PHP8.5.10 request stage2 after the ordered shutdown queue.
It first repeats the reverse direct-global pass while the symbol-table size
changes, then scans live object-store handles in ascending order. A real
reference wrapper skips the direct-global pass, even after its other alias is
removed. Arrays and other retained containers leave their objects for the store
pass. Handles reuse released holes before the store scan; the scan disables reuse.
A freed parent's handle becomes available after its outgoing slots finish.

Automatic destruction marks the object before the zero-argument method enters
and retains one temporary receiver. An explicit `->__destruct()` call does not
make that mark. Failed automatic construction does: source body throws, denied
constructor access, argument throws and inherited internal reception failures all
suppress a later destructor, including an escaped `$this`. Failed manual
`->__construct()` calls leave the existing object eligible.

The outer passes have a null C caller and internal trace. A private/protected
method produces the native `Unknown:0` warning and is ignored. Nested releases
inside a real USER callback instead use that caller's lexical/called scope and
source line; denied access throws Error. A handled destructor exception continues
its release loop or store scan. An unhandled exception or exit stops the remaining
callbacks. Bailout fatals mark existing objects; uncaught Throwable fatals preserve
their eligibility. Objects born in a later shutdown callback remain unmarked.

Outgoing property/array slots decrement in order. Unconsumed slots remain owners,
so `[shared, middle, shared]` destroys middle before shared. A nested callback can
suspend another release loop. Real call frames restore the caller before releasing
locals in compiled CV order, then extras before the receiver/Closure. The assigned
return operand and pending Throwable keep their owners through that cleanup;
replacement throws chain and become the pending object for each remaining slot.
An ignored ordinary return releases its temporary before restoring that callee,
so private destructor permission remains in the live callee scope. An ordinary
automatic constructor has the same unused return destination. The C destructor
helper instead retains its returned value until after local cleanup.

Explicit request bootstrap installs CLI `argv` and `argc` before compiled CVs.
Replacing `argc` therefore preserves its earlier global position. Without request
facts, access to these names keeps the existing `request environment variable`
Unsupported boundary; it is not treated as insertion of a fresh key. A dormant
compiled CV does not require request facts. State authentication checks relevant
bindings in the genuine global table, including saved caller views.

Current and saved calls authenticate the original receiver, zero arguments,
release/frame continuation, source/called scope and pending Throwable. Borrowed
CALL/RELEASE/FRAME records own no values; pending jobs and finish tasks own the
retained slots, receiver, return operand or Throwable. Future-task and saved-frame
views project only the exact completed borrowed suffix. A pending parent's handle
cannot enter FREE or belong to another live object. Budget resumption preserves
these owners and the once-only marks. Normal destructor eval/include continuations
reuse the existing source service/history; a fatal compiler outcome stops later
destructors. Callback API registration retains the real destructor producer scope,
including a permitted private nested destructor; a new shutdown entry after stage1
does not run a second queue.

The source truth is `main/main.c::php_request_shutdown` and `php_error_cb`,
`Zend/zend_execute_API.c::shutdown_destructors` and `zval_call_destructor`,
`Zend/zend_objects_API.c::zend_objects_store_call_destructors`,
`zend_objects_store_del` and `zend_object_store_ctor_failed`,
`Zend/zend_objects.c::zend_objects_destroy_object`, and
`Zend/zend_vm_def.h::zend_leave_helper`/`i_free_compiled_variables`.

Source and reached-state checks remain separate:

```sh
python3 tests/semantics/destructor_review.py
python3 tests/semantics/destructors.py
python3 tests/semantics/destructor_request.py
python3 tests/semantics/destructor_state_review.py
python3 tests/semantics/destructor_state.py
```

Stage2 DONE retains the remaining native owners for later request phases;
shutdown registrations are not freed here. Ordinary eager last-owner destruction
before stage2, including the original uncaught Throwable release before stage1,
returns precise Unsupported instead of moving its effects into this stage.
The existing PHP-Parser static-destructor rejection is a zero-agreement frontend
control. Eager destruction, cycles/GC, output buffering, registration release and
final request cleanup are required next work; this increment does not establish
complete request lifecycle or complete core.
