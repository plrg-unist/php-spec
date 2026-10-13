# Tick callbacks

Module393 derives a tick plan from checked source and the authored compiler's
operand and control-line descriptions. The plan tracks file-local declarables
and the last operation in each op array. It accounts for adjacent-marker
suppression, zero-operation expressions, early declarations, branch jumps and
unreachable markers after return, break, goto, throw and exit. Ordinary source
execution creates the certified tasks; callers cannot supply a marker table.
Named construction visits its class and source-ordered arguments, allowing
argument Closures to contribute their own lexical plans.

Block `declare(ticks=...)` restores the enclosing frequency. Unbalanced
declarations compiled inside functions or closures can affect later statements
in the same file context. Eval/file units begin with frequency zero. Execution
shares one request counter, narrowing increments and opcode frequencies to
uint32 before the VM threshold comparison, even without registered callbacks.

Registration retains selected functions, Closures and admitted method callbacks,
with copied extra arguments and receiver ownership. Dispatch traverses the live
ordered registry: additions participate immediately and deleted later entries
are skipped. A running entry suppresses its own reentry. Unregister compares the
cached function, receiver, calling class and Closure identity, excluding callback
arguments. A running match raises `Error` and scanning continues; the first later
inactive equal match can still be removed while that error remains pending.
Removal releases captured arguments before the cached callback receiver. A
source-authenticated continuation retains that receiver through normal or abrupt
argument cleanup; its old argument values are nonowning selection witnesses.

Callbacks enter ordinary source frames, inheriting the executing frame's strict
mode and certified compiler line. Reference warnings, argument errors, handler
reentry and Throwable traces use existing call machinery. Unused return values
are destroyed after callee restoration while the entry remains running. Genuine
unwinding clears that state before shutdown callbacks. Fiber switching remains
blocked during the callback and its returned-value cleanup.

The source summary is deliberately bounded. Wider class/linking placement,
switch and other unmodeled statement/expression emission, callable defaults or
attributes containing nested callables/ticks, and callable-bearing foreach
targets remain `Unsupported`, as do dynamic and anonymous construction summaries.
Empty multiline catch/finally/declare bodies without
the necessary compiler-line description are also explicit dependencies.
Effectful keyword/compound callable selection, builtin callback bodies and typed
variadic tick reception remain open. The tick obligation and full core are partial.

Validation is native-first on original PHP bytes and compares stdout, stderr and
exit status. [Author sources](../../tests/semantics/tick_sources.py),
[independent sources](../../tests/semantics/tick_review_sources.py) and
[reached states](../../tests/semantics/tick_state.py) cover the admitted behaviors
and public-state exclusions. Source/state acceptance is recorded separately from
static elaboration; expected dependencies receive no agreement credit.
