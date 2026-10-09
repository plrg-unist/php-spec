# Throwable control and internal state

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

Generated and constructed builtin objects use one seven-field `OBJECTPROPS`
row: protected `message`, private `string`, protected `code`/`file`/`line`,
private `trace` and `previous`. The private fields have the declaring
`Exception` or `Error` owner in their internal IDs and NUL-mangled keys.
`getMessage`, `getCode`, `getFile`, `getLine`, `getPrevious`, `getTrace`,
`getTraceAsString` and `__toString` use these fields. Ordered argument tasks
retain the selected receiver and sent values. Generated-error and direct-new
allocation materialize trace frame/argument/outer arrays before installing the
object; the private trace slot is their sole live backing. Captured arrays use
ordinary COW and captured objects retain identity. `getTrace()` returns the
array value; the renderers and terminal observer read that same graph.
`__toString` updates the private string cache. Pending/uncaught completion and
search/binding tasks root the object and its trace arrays. Rethrow retains
identity and allocation trace. `S.TRACE` is transient error-unwind state only.

Non-Throwable fatal and Unsupported frame cleanup retires the discarded active
origin while retaining the diagnostic `ERRORORIGIN` and captured `TRACE`.
Saved caller contexts survive until their own restoration and cleanup. A pending
`ERROR_UNWIND` must be the sole task, with an empty active origin and an abrupt
completion admitted by the module40 producer. This checks the current state
shape; it does not prove an arbitrary prior error history.
The [ledger](../../coverage/semantics/error-origin-author.json) separates original
pause failures, fixture corrections, source observations and current review.

Frame arrays preserve PHP's ordered `file`, `line`, `function`, optional
`class`/`type`, and `args` keys. Arguments snapshot values at allocation:
arrays use ordinary COW, references contribute their current value, and
objects retain identity. Closure class names use lexical scope. Trace strings
render from the stored graph, including the `and defined` suffix on matching
type/arity messages before the first NUL byte.
One zero-argument builtin `#[SensitiveParameter]` on an ordinary or promoted parameter
resolves through its authenticated source namespace/import scope. Fixed trace
arguments read current dereferenced CVs; variadic extras and named entries keep
their original operands, and omitted defaults add no trace argument.
Trace capture tags root their values until real `SensitiveParameterValue`
objects are allocated before callbacks or frame retirement. Physical trace arrays
store those wrappers; `getValue()` returns their stored snapshot and trace strings
render their class. A wrapper strongly owns captured objects while WeakReference
targets stay weak. Actual allocation/getter/last-release controls and ten original
source agreements are recorded in the [review](../../coverage/semantics/sensitive-parameter-review.json).
Promoted constructor parameters retain ordinary value/reference property writes;
trace capture still reads their live CVs. A by-value property can remain 7 while
its trace wrapper captures 17; a by-reference property/caller can later become 23
while the wrapper retains 17. The attribute creates no property Override
obligation. Eight source agreements and separate genuine property/wrapper and
queued-admission checks are recorded in the [promotion review](../../coverage/semantics/sensitive-promotion-review.json).
Direct wrapper construction copies one dereferenced mixed value through ordinary
ordered sends. Arity errors precede readonly re-entry errors; rejected writes
preserve the old snapshot. Getter copies own objects independently of the wrapper,
and last release triggers ordinary destruction and WeakReference notification.
Seven originals and separate allocation/SEND/getter/retirement checks are recorded
in the [constructor review](../../coverage/semantics/sensitive-value-constructor-review.json).
First-class `getValue(...)` callables strongly own the wrapper and its captured
value. Invoked getters return ordinary copies; callable clones and aliases retain
the same receiver while last copy release triggers destruction and weak-target
notification. Five originals and separate authentic capture/getter/last-release
checks are recorded in the [getter review](../../coverage/semantics/sensitive-value-getter-review.json).
Mixed/repeated/argument attributes, hooks, first-class constructors,
uninitialized getter, debug/property and wider wrapper protocols remain required.

`ErrorException` appends a protected typed `severity` as the eighth slot; its
inherited private fields retain `Exception` declaration IDs. Its own
six-argument constructor validates all values before writes, resets severity
to `E_ERROR` on every call, and changes file/line only when their nullable
arguments are supplied. A non-null filename with null line sets line to zero,
including an empty filename; an explicit line can be negative. `getSeverity`
reads the live slot after ordered argument evaluation and is final. The
constructor and getter use `ErrorException` as callable owner while inherited
getters and slots keep `Exception` as their owner.
Array casts of finite built-in Throwables copy their ordered property slots,
including mangled private keys and the appended severity slot. The cast shares
array values under ordinary COW and leaves the sealed object property row intact.
Uncaught `ParseError` and `CompileError` use PHP's class-specific parse/fatal
diagnostics without a stack; ordinary `Exception` keeps the uncaught stack form.
Finite `Exception`/`Error` constructors, including identical inherited
constructors of their built-in descendants, allocate with file/line/trace
before argument evaluation. Direct `__construct` reentry retains those fields.
Arguments are sent in source order; named errors arise at SEND, and positional
arity and types are validated before any field write. No-argument reentry
preserves the writable fields; a call supplying only named `code` or `previous`
supplies the default empty message and clears it. Zero code and null previous
preserve their fields. Explicit self and two-object previous cycles are legal;
terminal rendering stops at a repeated object. Finally replacement
keeps its transition-local generated-chain guard.

[Prepared parameter-default constructors](../../coverage/semantics/internal-default-constructors-review.json)
evaluate all AST values before internal name mapping, fill only existing named
holes, and parse lossless scalars with default-declaration strictness. Successful
string parsing updates supplied trace slots; trailing defaults do not increase
argc. Source15, reached67 and affected trace2 retain separate cutoffs.
[Effectful default reception240](../../coverage/semantics/internal-default-reception-review.json)
retains real warning/Stringable callbacks, raw integer versus rewritten string
trace arguments and the immediately owning constructor across nested handlers.
Source14 plus builtin/fallback2 and source-derived185 premises pass at separate
cuts; current trait/display fallback adds one exact source comparison at e7ec.
The original one-process timeout remains preserved. Broader ordinary
constructor effects and anonymous keyword defaults remain required.

Compiler rules preserve throw effects even where its result folds to true,
compile try body before ordered catch headers/bodies, and retain first-type
catch diagnostic lines. Legal goto entry into try reconstructs its marker;
entry into catch skips binding and does not activate sibling catches. Stage A
finally runs on normal and exceptional exits and chains replaced generated
errors. Stage B handles value/reference returns and jumps across finally.

Still required: source access to internal properties, reflection and mutation,
user subclasses,
static-method frame integration, remaining finally transfers,
handlers, lifecycle callbacks, include errors, generator/Fiber closing and
serialization. Direct `__toString`, `echo` and string casts work for finite
builtin Throwables; weak typed string conversion, property access,
property traversal and comparison remain explicit Unsupported where required.
Callable rejection, boolean conversion, identity comparison, nominal ancestry
and typed nominal consumers are also modeled.

Source routes: Zend/zend_exceptions.c (default allocation, throw object and
nominal hierarchy); Zend/zend_vm_def.h (ZEND_THROW, ZEND_CATCH and exception
unwinding); Zend/zend_compile.c (zend_compile_throw, zend_compile_try and goto).
Compiler checks, exact original-source tuples and paused ownership tests are
maintained in `throwable_compiler.py`, `throwable_expressions.py`,
`throwable_protocol.py`, `throwable_accessors.py`,
`throwable_getter_protocol.py`, `throwable_constructors.py`,
`throwable_constructor_protocol.py`, `throwable_traces.py` and
`throwable_trace_protocol.py`. Unsupported controls are counted separately.
