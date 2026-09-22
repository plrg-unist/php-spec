# Throwable control, first increment

Target PHP 8.5.10 CLI NTS 64-bit. Modules 151/152 connect generated builtin
errors to genuine owned objects, source throw/rethrow, and ordered no-finally
try/catch. This is a partial internal-class/control increment, not Throwable
family closure. The methods/clone source and paused-state bridge has independent
review. The [terminal migration ledger](../../coverage/semantics/throwable-migration-review.json)
records bounded checks and deferred broader pause sweeps.

Existing `THROWN`/`PHPERROR` producers are transient requests. The step boundary
allocates a finite builtin Throwable identity before pruning, snapshots its
origin and trace, and restores the audited predecessor continuation. The two
admitted transition shapes are unchanged current/saved frames, or exactly one
saved caller frame with matching context, continuation, source and suppression.
Unaudited shapes remain Unsupported. Exit is a separate terminal transfer.

Exception search owns the object and crosses one continuation at a time. It
uses existing return-discard cleanup for source, foreach and suppression
markers, restores saved frames only after their local continuation empties,
and tests catches before main-frame terminal cleanup. Catch resolution is
ordered, case-insensitive nominal matching with no autoload; missing and
non-Throwable catch classes legally fail to match. Selecting a catch consumes
its marker before the separate strict binding task. A binding failure or a throw
in the catch body therefore searches outward past its sibling catches.
Catch variable binding uses Zend's direct CV operation, including its distinct
autoglobal behavior, and checks every typed reference source without coercion.

The builtin object has one current backing payload for message/code/file/line,
trace and previous link. These fields must become the backing source for later
observable internal properties and methods, not duplicated mutable storage.
Pending/uncaught completion and search/binding tasks root the object; payload
trace values are child edges. Rethrow retains identity and allocation trace.
The terminal observer renders the uncaught object's fields, with TRACE populated
only at that terminal boundary. The payload is not a full getTrace result yet.

Compiler rules preserve throw effects even where its result folds to true,
compile try body before ordered catch headers/bodies, and retain first-type
catch diagnostic lines. Legal goto entry into try reconstructs its marker;
entry into catch skips binding and does not activate sibling catches. Finally
is explicitly Unsupported, including otherwise accepted return/jump paths
requiring finalization.

Still required: constructors, accessors, full structured trace and argument
capture, internal property visibility and mutation, user subclasses, protected
and private members, finally and previous chaining, __toString dispatch,
handlers, lifecycle callbacks, eval/include errors, generator/Fiber closing
and serialization. Throwable string conversions, property access/casts,
property traversal and comparison dependencies are explicit Unsupported where
those services are required. Callable rejection, boolean conversion and identity comparison, nominal
ancestry and typed nominal consumers are part of this first increment.

Source routes: Zend/zend_exceptions.c (default allocation, throw object and
nominal hierarchy); Zend/zend_vm_def.h (ZEND_THROW, ZEND_CATCH and exception
unwinding); Zend/zend_compile.c (zend_compile_throw, zend_compile_try and goto).
Compiler checks, exact original-source tuples and paused ownership tests are
maintained in `throwable_compiler.py`, `throwable_expressions.py` and
`throwable_protocol.py`. Unsupported controls are counted separately.
