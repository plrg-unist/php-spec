# Named source calls and frame ownership

This increment implements named function declarations, calls with positional
arguments, plain untyped value parameters, recursion, global statements and
value returns through the checked source pipeline. Declaration installation and
runtime callable activation are separate. Direct main declarations, including
bare statement blocks, activate before execution; conditional and nested
declarations activate when execution reaches them. Body compilation preserves
its own CV order, lexical context, header state, magic constants and original
source occurrences. Compile-time errors in visited bodies precede source effects.

The compiler records finalized earlier callees separately from eventual runtime
availability. Known value parameters use ordinary reads. Forward, conditional,
self-recursive and namespace-fallback calls can use deferred argument fetches.
For example, an earlier `function f($x){}` makes `f($a[])` a compile error; a
forward declaration makes it a runtime fetch error. CODEARG records each actual
fetch occurrence, including variable/dimension ancestors; key expressions keep
their own ordinary modes. The source-derived builtin argument table supplies the
same compile-time distinction for registered names without executing library
bodies. See [argument compilation](FUNCTION-ARGUMENT-MODES.md).

Runtime lookup selects an active function before argument effects. The selected
original declaration identity remains held during argument evaluation. An
argument may declare a namespaced primary after a fallback was selected; that
first call keeps the fallback, while a subsequent call can select the primary.
Each argument becomes an owning value operand in source order. Provided values
bind parameter CVs, surplus values remain separately owned, and a missing required
argument produces the pinned ArgumentCountError after the callee frame exists.

## Tables and roots

The active ENV/CVS/SYMBOLS fields represent the executing scope. First function
entry moves the main table into GLOBALTABLE and saves a main continuation with
no duplicate local table. Nested entries save caller locals. Final return moves
the request table back into the active fields. Saved locals, pending argument
operands, held temporaries, surplus arguments and suspended iterator operands
participate in the heap graph. Compiler names, occurrence paths, parameter names
and iterator IDs are borrowed metadata. Parameter CVs supply their sole cell
ownership; trace metadata does not add hidden parameter aliases.

Known compiler-designated superglobal fetches select the request table even when
the source name was computed at compilation. Runtime dynamic names remain local.
Explicit GLOBALS dimensions use their existing name-conversion and diagnostic
protocol. Global declarations and subsequent local reference rebinding preserve
Zend's distinction between a local alias and the request bucket. Autoglobal
callbacks replace request buckets without retargeting local aliases or the
original HTTPROOTS values. See [compiled scope](SUPERGLOBAL-SCOPE.md) and the
[request-state contract](REQUEST-STATE-REVIEW.md).

A return captures its owning value before releasing callee locals and iterator
continuations. Return and error unwinding preserve source-origin restoration,
remove discarded iterator registrations, and restore each caller once. Every
budget suspension retains active and saved owners. Fatal errors capture trace
arguments before teardown; returned singleton reference wrappers and shared wrappers retain their distinct array-copy behavior.

## Diagnostics and public resume

The pinned CLI profile uses precision 14, exception_ignore_args=0 and
exception_string_param_max_len=15. Trace formatting is pure SpecTec: current
parameter slots, unset/rebound slots, actual argument count and surplus values
determine the arguments. The observer serializes semantic trace text and events.
Callsite lines are emitted at the call occurrence after successful sends;
abrupt argument diagnostics retain the argument's own line. Arbitrary trace INI
configuration remains planned request-context work, not a claim of this gate.

Public drive/resume checks immutable compiled descriptors before normal work.
It derives declarations and call metadata from the original checked unit,
source filename and explicit request CWD; there is no second trusted registry or
host evaluator. Registered keys must name their compiled declarations, early
bindings must exist, and body/signature/CV/context projections must agree.
Selected targets and callsite lines are checked through active and saved tasks,
including AT wrappers. Actual argument counts, surplus counts and pending
argument suffix/index relationships are checked against the source callsite.
Runtime values and their mutation history are not reconstructed.

The same boundary validates global fetch designations and CODEARG occurrences.
Malformed descriptors yield Unsupported before further PHP effects. Existing
terminal outcomes remain intact. Internal steps retain ordinary step accounting;
external validation adds no PHP transition. These controls establish the tested
protocol boundary, not a proof of semantic equivalence or arbitrary-state safety.

The [positional reference increment](SOURCE-REFERENCE-PARAMETERS.md) extends these
frames with reference sends and parameter binding. Pending cells, saved contexts,
surplus values and temporary DIM/list owners use the same lifetime protocol.
Its source, state, compiler and production input evidence is recorded separately
in [independent acceptance](../../coverage/semantics/reference-parameter-review.json).

## Remaining call protocols

Reference returns, defaults, variadics, named and unpacked arguments,
typed/strict argument and return enforcement, closures, variable calls, methods,
objects, dynamic source units, handlers/finally and generators/fibers remain
separate planned increments. Unsupported outcomes for those boundaries and
registered but unimplemented builtin bodies are not successful source tests.
The complete-core inventory remains open. This increment's source/state evidence
and historical/compiler/profile bridges are recorded separately in acceptance.
