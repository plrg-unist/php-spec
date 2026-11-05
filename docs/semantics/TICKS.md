# Tick callbacks

Module393 derives a tick plan from checked source and the authored compiler's
operand and control-line descriptions. The plan tracks file-local declarables
and the last operation in each op array. It accounts for adjacent-marker
suppression, zero-operation expressions, early declarations, branch jumps and
unreachable markers after return, break, goto, throw and exit. Ordinary source
execution creates the certified tasks; callers cannot supply a marker table.
Named construction visits its class and source-ordered arguments, allowing
argument Closures to contribute their own lexical plans.

Switch plans visit the subject, every case condition, then every body in compiler
order. Case bodies share adjacency across selected and unselected branches;
fallthrough and jumps retain the ordinary switch runtime. A final temporary
subject release permits an enclosing marker, while constant and CV subjects can
leave that marker suppressed by the final compiled body. Unexecuted condition
Closures and body declarations still change the file's later tick frequency.
Existing constant-operand receipts and resolved call facts supply the result-kind
checks. Fixed builtin calls and builtin fallback selections inside an otherwise
unproved subject remain Unsupported until their compiler result kind is justified,
including imported and qualified calls. The model does not infer a temporary
from binary/unary syntax around a compiler-special call.
The matching source routes are `zend_compile_switch`, `zend_emit_tick`,
`zend_compile_print` and `zend_compile_func_defined` in `Zend/zend_compile.c`.

Match plans visit the subject, every arm condition, then every arm result in
compiler order. Unselected arms still contribute callable compilation and lexical
declarables. Result assignments and jumps clear adjacency; nonempty Match results
are temporaries. The empty-arm case has a CONST-null compiler result and raises
`UnhandledMatchError`. Assignment markers use the checked target line, while a
discarded Match keeps the last compiled arm's line. Completed Match values also
retain their pending Generator statement marker across suspension. Existing
switch-subject guards still refuse compiler-special builtin descendants through
Match. Wider child-order and elision contexts remain explicit dependencies.
The source authority is `zend_compile_match` in `Zend/zend_compile.c`.

Conditional plans use the ordinary compiler's published operand, redirect and
retained-effect receipts. A constant result visits its real effects once; a
redirect visits effects outside its selected child and then that child. The
boolean conversion flag keeps its real BOOL operation and temporary result.
Unpublished prepass rewrites never make an uncompiled branch executable.
Direct full and shorthand ternaries compile their unselected callable bodies;
array-element prepasses may instead erase them, including static diagnostics.
Constant-left logical forms can omit the right body, while a runtime-unselected
right body still contributes lexical declarables for all four logical aliases.
Array keys compile before values. Switch subject cleanup uses the same selected
result receipts. Unproved fixed builtin/fallback descendants in logical operands
remain Unsupported, including known outer constants retaining those effects.
The source routes are `zend_compile_short_circuiting`, `zend_compile_conditional`,
`zend_compile_shorthand_conditional` and `zend_compile_array`.

Coalesce plans reuse those receipts. Ordinary `??` compiles its quiet left
operand and RHS even when the left value looks constant; an earlier actual
constant prepass may instead erase the fallback. Runtime quiet reads still omit
undefined-value warnings and evaluate only a selected RHS. Coalesce assignment
visits target children before RHS, then reuses their memoized expressions for
its writable refetch. Callable keys therefore contribute lexical declarables once,
while an unexecuted RHS body still contributes its own compilation. Real
COALESCE/QM_ASSIGN/write operations break adjacency and produce temporaries;
the enclosing tick runs after assignment commits. Source authority includes
`zend_compile_coalesce`, `zend_compile_assign_coalesce`, `zend_compile_dim` and
`zend_compile_simple_var_no_cv`. Existing runtime access/write admission stays
bounded. Witnessed callable-key assignments have no registered error handler.
The registered-handler quiet key-reader path has an open composition/performance
obligation: bounded progress completes after the key's tick, but full execution
times out. This establishes neither completion nor Unsupported. Multi-operand
`echo` still lacks Zend's between-operand tick placement; these witnesses use
explicit individual echo statements.

Admitted Generator sources preserve statement markers across suspension. A bare
yield keeps its discard before the pending tick; a direct assignment keeps its
write before that marker. The marker runs when the Generator resumes. Flat-array
`yield from` reaches its statement marker after delegation finishes, without a
marker per yielded item. Caller and Generator ticks share the request counter.
Key expressions compile before values, including nested callable bodies and their
lexical declarables, following `zend_compile_yield` and `zend_compile_yield_from`.
These summaries reuse existing Generator transport and SEND admission; wider
yield-result contexts and delegation/lifecycle combinations remain partial.

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
other unmodeled statement/expression emission, callable defaults or
attributes containing nested callables/ticks, and callable-bearing foreach
targets remain `Unsupported`, as do dynamic and anonymous construction summaries.
Empty multiline catch/finally/declare bodies without
the necessary compiler-line description are also explicit dependencies. Empty
switch cases whose recorded span covers multiple lines and unproved subject
kinds, including suppression and destructuring assignment, retain that boundary.
Effectful keyword/compound callable selection, builtin callback bodies and typed
variadic tick reception remain open. The tick obligation and full core are partial.

Validation is native-first on original PHP bytes and compares stdout, stderr and
exit status. [Author sources](../../tests/semantics/tick_sources.py),
[independent sources](../../tests/semantics/tick_review_sources.py) and
[reached states](../../tests/semantics/tick_state.py) cover the admitted behaviors
and public-state exclusions. Source/state acceptance is recorded separately from
static elaboration; expected dependencies receive no agreement credit.
The [switch review](../../coverage/semantics/tick-switch-review.json) records
the compiler-order, marker-line, cleanup and resumption witnesses at their
individual cuts, including scoped passing rows from preserved failed packets.
The [Generator tick review](../../coverage/semantics/tick-generator-review.json)
records the focused source and parked-continuation witnesses.
The [Match tick review](../../coverage/semantics/tick-match-review.json) records
arm-order, line, result-kind, abrupt-callback and suspension witnesses.
The [conditional tick review](../../coverage/semantics/tick-elision-review.json)
records compiled versus elided bodies, retained effects and canonical marker
validation with budget/unpause equivalence.
The [coalesce tick review](../../coverage/semantics/tick-coalesce-review.json)
records quiet reads, lazy RHS execution, memoized target children and committed
assignment before callback throw.

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
policy remains partial. One Closure-object __invoke array control was an exact
early lookup Unsupported boundary at the ATTR08 cut; its tick consumer is
extended below.
Five normal originals agree, four reached groups pass 296 checks (292 reached,
four derived), and private strict 432 passes. The [cache review](../../coverage/semantics/callback-fcc-cache-review.json)
keeps the old equality counterexample, failed property/certificate states and
corrected fixtures at their original cuts, alongside the OB05 joined checks.

Cached user `[Closure,"__invoke"]` tick calls forward positional arguments and
borrow the outer Closure from FCC.object. E_DEPRECATED 8192 precedes its first copied argument; required-reference
warning 2 uses the wrapper name and an isolated cell. E_USER_DEPRECATED 16384 then
precedes the inner call and weak type reception. The entered call adds one Closure
instance, borrows its receiver and separately owns the raw outer arguments.
NoDiscard stays masked. Trace redaction preserves independent raw/received
snapshots and the inherited tick marker. Normal frame cleanup retires inner owners
and raw arguments before TICK_RESULT discards the unused value; the persistent
cache stays live. Warning throws preserve that cache until later unregister.

The [tick wrapper review](../../coverage/semantics/callback-closure-invoke-review.json)
records five normal agreements, four reached groups/302 checks (300 reached, two
derived), private strict 432, joined strict 433 and one retained-native
warning/unregister comparison. Other API wrappers, late registry free and broader
callable/value histories remain partial. The older explicit source-wrapper warning
head's missing inherited file/line is repaired by the separate
[ATTR10 source-wrapper cut](../../coverage/semantics/builtin-deprecated-closure-trace-head-review.json).
