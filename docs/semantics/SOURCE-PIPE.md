# Pipe source increment

The pipe operator evaluates and forces its left operand before evaluating or
selecting the callable on the right. The forced value becomes one positional
argument. Named user functions and existing callable closures use the ordinary
call binder, including reference-result mode; the first-class `f(...)` source
form uses its checked optimized lookup. A left expression that yields a
reference is read at the left operand's line before right-side effects. The
`CODEPIPE_SEND` descriptor records the later send line separately from the
callsite and lookup lines, and the compiler authenticates the pipe root, both
children, and marker together.

A right-side two-entry array may select a public user instance or static method.
The selected receiver outlives the evaluated array, including a by-reference
parameter refusal before method entry. A pipe-specific result task carries the
selected method and source-site receipt after a temporary receiver retires.
Invalid selectors retire an owning RHS before the left value and report at the
right operand's lookup line. A throwing RHS destructor replaces the pending
lookup Error. Scoped, magic, autoloaded and internal method targets remain
separate work.
The invalid-lookup task validates its pipe site and lookup line. It saves the
selected error bytes before RHS retirement; those bytes and the held left
payload are not reconstructed from mutable history at the paused task.

The syntax grouping and bare-arrow rejection are described in
[the syntax review](../../coverage/semantics/pipe-syntax-review.json). Runtime
rules are in `122-pipe-compiler.watsup`, `123-pipe-runtime.watsup` and
`432-pipe-array-callables.watsup`, with narrow shared task and call-integrity
changes. Matching-engine evidence starts at `zend_compile_pipe` in the pinned
`Zend/zend_compile.c`, with value sends and calls in `Zend/zend_vm_def.h`.

[The runtime review](../../coverage/semantics/pipe-review.json) binds 12
private source outcomes (7 normal, 5 PHP errors), separate original-source
replays, and paused ownership/authentication controls. The maintained source
and protocol checks are `tests/semantics/pipe*`. The public user-method array
increment has twelve exact native CLI comparisons and four reached-state
controls; its separate review records the tested revision. Builtin, direct
method-string and other object callables remain explicit dependencies; this is
partial pipe coverage, not a full callable-family claim.

[Unary CONFIG PIPE](../../coverage/semantics/include-config-pipe-review.json)
authenticates the held left child and compiled send/call lines through Stringable
getter, SET and Restore callbacks. Ordinary RHS factories return the selected
callable; their own subcall names never become fixed targets. Ordinary Closure
PIPE follows the source caller's strictness, while explicit `Closure->__invoke`
uses its weak C wrapper. Twelve earlier normal source tuples and three state
fixtures/165 assertions cover strict refusal, retired source cells, exact/full-NUL
misses, empty/NUL SET results and thrown callbacks. Two current borrowed-warning
checks retain real reference owners and normal/throwing callback frames.

Stringable CHDIR PIPE uses the CWD after the callback, including an inner `chdir`.
Six source comparisons and 124 provider assertions distinguish request failure,
NUL rejection, throw and strict refusal, and reject forged directory replies.
The held operand survives RHS source-cell retirement; provider certificate
rooting does not establish native destructor timing. Failed CHDIR warnings now
retain the consumed provider certificate through nested handlers. Normal return
yields false after CWD/raw writes; throw restores caller arguments and preserves
the converted internal argument versus the original explicit wrapper object in
the trace. One current source/136 checks, earlier three source tuples and
compiler image25 checks keep distinct cutoffs in the ledger. Wider CONFIG
providers, method/array/object consumers and lifecycle remain partial.
