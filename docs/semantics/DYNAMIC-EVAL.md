# Reached eval execution

`eval` runs a checked dynamic source unit after its operand is evaluated. A
zero-byte string returns `false`; a nonempty unit that falls through returns
`null`. An explicit `return` leaves only the eval unit. The caller's variables,
receiver and class scope remain live, while the new unit starts with empty
namespace/imports and weak typing. A per-unit binding records the caller's
lexical class for `self::class`; live `CURRENT` retains the called class for
`static::class`. Neither changes eval's empty `__CLASS__`.

The machine reserves a fresh source ID and stops at `SOURCE_PENDING` with an
owned `EVAL_AWAIT` marker. `bin/php-semantics` retains the live adapter state,
asks the pinned `parse-eval` worker for those exact bytes, and forwards its
response. Accepted syntax is checked and appended to the source registry. A
single owned `EVAL_END` bounds normal fallthrough, top-level return and throw;
saved frames retain it across calls. Nested requests consume the same remaining
step budget. Current and saved descriptor checks bind the request, source file,
phase, owner, barrier position and caller suffix. An accepted or rejected
response consumes its ID once. A malformed semantic `$eval_resume` response
changes only the completion to explicit `Unsupported`; the adapter rejects a
malformed `resume_eval` response before semantic mutation and retains the live
session for a valid response.

The trusted worker is the source-to-AST authority. The adapter's direct
`resume_eval` endpoint checks response identity and AST type but cannot prove
that an arbitrary client-supplied AST came from those bytes. Source-agreement
claims therefore use the CLI path through the pinned worker. The numeric
protocol fixtures use worker-issued ASTs and separately test forged paused
states.

Native parse-only `ParseError` and parse-time `CompileError` facts create
catchable objects with persistent failed-source file, line and kind. Their
message slot remains mutable through `__construct` reentry. Accepted-source
static failures stop globally before caller/finally work; a missing-parent
class-link error materializes at the dynamic class origin and searches the
caller's catches. Warnings and terminal diagnostics render the dynamic file.
Eval frames are interleaved with ordinary call frames by saved-frame owner.
Redeclared classes have an eval frame in their fatal stack; function
redeclaration and a final-parent link fatal do not. Each retains the dynamic
source filename.

Current source controls cover nested eval, eval return in typed and by-reference
callers, parser and static errors, namespaces, class scope, inline HTML,
variable sharing, and eval inside pending finally return/throw.
The [author ledger](../../coverage/semantics/dynamic-eval-author.json) binds
the 55-case original-source run (48 exact agreements, seven explicit
Unsupported controls), a retrospective identity check for three previously
unhashed test helpers, and fresh paused/source/no-eval checks after the
`get_class` integration. Two added direct/dynamic `get_class(1)` inside eval
cases catch the eval frame in a TypeError trace. Raw reports remain under
ignored `.tools` paths.

Remaining obligations are object `__toString` operand conversion;
eval-created closure and `parent::class` scope; generic imported-name `::class`
evaluation; native-accepted namespace headers rejected by the PHP-Parser
frontend; accepted-AST catchable `CompileError` cases and class-link errors
beyond the modeled missing-parent `Error`; and include/require/once with a file
provider. The trace-source `getTrace()` controls also depend on the Throwable trace
slot milestone. The eval binding invariant applies only to accepted eval units;
future include units need their own source-kind registry.
