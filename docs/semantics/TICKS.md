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
Removal releases captured arguments before FCC.object and FCC.closure. A
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

Persistent callback caches now retain FCC.object and raw-object FCC.closure as
separate owners. A bound Closure therefore has an additional cached receiver;
a raw invokable object can occupy both slots, while [object,"__invoke"] has one
object slot. Tick equality preserves that distinction, so repeating array-form
unregister does not remove a raw registration. Entered API methods borrow This.
Inline unregister retires arguments, cached object, then cached Closure without
deduplicating equal IDs. A selected scope/binding witness validates only readonly
cleanup after Closure retirement; it never restores a live owner or callable entry.

Quiet shutdown cache owners survive callback completion, the early destructor
pass and output FINAL. The selected buffered executor path retires both FCC
slots, even when they identify the same raw invokable object. Wider late-free
policy remains partial. One
Closure-object __invoke array control stays an exact early lookup Unsupported
boundary at zero agreement credit; it needs its own wrapper/API consumer.
Five normal originals agree, four reached groups pass 296 checks (292 reached,
four derived), and private strict 432 passes. The [cache review](../../coverage/semantics/callback-fcc-cache-review.json)
keeps the old equality counterexample, failed property/certificate states and
corrected fixtures at their original cuts, alongside the OB05 joined checks.
