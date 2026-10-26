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

A nonoptimized string RHS naming a public static user method selects that
method from the evaluated literal, variable or temporary value. A separate
send task retains the forced left value through by-reference refusal; a
source-bound result task preserves a reference return for its outer consumer.
Missing methods report at RHS lookup. Private, nonstatic, magic, autoloaded,
keyword and optimized method-string selectors remain outside this increment.
For a dynamic RHS, the result receipt records selected bytes; it cannot
reconstruct a past value from a later-mutated source variable.

Optimized first-class pipe RHS strings now select plain public static user
methods. A fixed literal uses its compiled method name; the source certificate
requires a real string literal whose bytes match after the compiler's optional
single leading slash normalization. Variable and temporary names use the
evaluated callee. Both paths reuse the pipe send and result tasks for lookup
lines, by-reference refusal, strict arguments and reference returns. A saved
method name survives a producer's later rebind, but the later `CALL_ARGS` task
cannot reconstruct those saved bytes from the mutable source. Private,
nonstatic and magic method selectors remain outside this increment.

Ordinary named user-function string carriers now work as optimized first-class
pipe callees and as nonoptimized literal, variable or temporary RHS values.
The pipe selects the evaluated name before sending its forced left value;
missing lookup, by-reference refusal, strict typing and reference returns use
the ordinary call path. The new branch requires a real pipe source shape,
matching literal bytes when present, and a valid string carrier. This is not a
historical value certificate for a dynamic producer: interned carrier validity
checks byte well-formedness, and a later `CALL_ARGS` task cannot reconstruct
selected name bytes after a source variable changes. Method strings, builtins
and Closure operands keep their separate dispatch and exclusions.

The syntax grouping and bare-arrow rejection are described in
[the syntax review](../../coverage/semantics/pipe-syntax-review.json). Runtime
rules are in `122-pipe-compiler.watsup`, `123-pipe-runtime.watsup`,
`432-pipe-array-callables.watsup` and
`433-pipe-static-method-strings.watsup` and
`434-pipe-named-string-carriers.watsup`, with narrow shared task and
call-integrity changes. Matching-engine evidence starts at `zend_compile_pipe` in the pinned
`Zend/zend_compile.c`, with value sends and calls in `Zend/zend_vm_def.h`.

[The runtime review](../../coverage/semantics/pipe-review.json) binds 12
private source outcomes (7 normal, 5 PHP errors), separate original-source
replays, and paused ownership/authentication controls. The maintained source
and protocol checks are `tests/semantics/pipe*`. The public user-method array
increment has twelve exact native CLI comparisons and four reached-state
controls; its separate review records the tested revision. The public static
method-string increment has its own exact native and paused-state gates.
The optimized public-static method-string increment has eleven initial exact
CLI outcomes and one corrected leading-slash direct outcome, followed by a
final 12-source request-profile pass and six reached stages/79 assertions.
The first leading-slash Unsupported remains a rejected cut. The nonoptimized
method-string and ordinary named-function gates retain their earlier revisions.
The named-carrier increment records 19 exact pinned CLI outcomes (18 normal,
one uncaught PHP Error), a separate 19-source request-profile pass and five
reached stages/72 assertions. The former optimized missing-function interpreter
failure is one current agreement, with its old failure retained as zero credit.
Builtin, scoped method-string and other object callables remain explicit
dependencies; this is partial pipe coverage, not a full callable-family claim.

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
