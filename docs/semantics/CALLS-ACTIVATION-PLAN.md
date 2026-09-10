# Calls, frames and declaration activation after quiet access

This sequence now has an accepted first named-call increment; see the
[source-call contract](SOURCE-CALLS.md) and [independent review](../../coverage/semantics/calls-final-review.json).
Plain positional value calls, declaration activation, recursion and frame/return
cleanup execute through the checked source pipeline. The remaining protocols below
are required work; helper or bounded source evidence does not close whole families.
The current [typed checkpoint](SOURCE-TYPED-FUNCTIONS.md) also connects positional
reference parameters, defaults and builtin scalar/container value types. The
[next handoff](RUNTIME-REFERENCE-RETURNS-HANDOFF.md) schedules reference returns
and call-reference acquisition; the sequence below retains its historical role.
Use the pinned engine and the existing source-occurrence, namespace/import,
constant-pool, ownership and diagnostic interfaces throughout.

## First source increment: named functions, invocation and return

Compile an actual function declaration and its body, activate it at the correct
phase, and execute a call through a real frame. Include recursion and return in
this first coherent source increment. A standalone signature helper or a task-only
frame demonstration does not meet this milestone.

Compiler work starts at `zend_compile_func_decl_ex`, `zend_compile_params`,
`zend_compile_return`, `zend_compile_call` and `zend_compile_args` in the pinned
`Zend/zend_compile.c`. Reuse `17-signatures.watsup` and `16-static-types.watsup`;
do not duplicate their normalization or diagnostics. The existing signature
helper retains default syntax and a materialization kind, so executable default
compilation is required when admitting defaults. Reuse the constant compiler and
explicit name lookup; unresolved required constants must remain distinct from
known nonconstant expressions.

Each function has a fresh compiler context: parameter CV allocation precedes body
allocation, the header-assigned flag resets, loop depth is local, and strictness
and namespace/import scope follow the declaration. Function magic constants
must consume that context. Give a compiled body an
identity tied to its original source unit and declaration occurrence. Collect
autoglobal activation requests from every compiled body in compiler order; these
are request-wide compile effects, unlike per-body CV/header state. Do not
clone checked ASTs or pretend a function body is a newly parsed source file.
The current per-source CODE/CVS export will need a deliberate per-body context
interface before frame entry; do not accidentally use the caller's CV order.

Separate compiled declarations from active callable bindings. At the pin,
top-level named functions register only after successful body compilation;
conditional/nested declarations activate when executed. Preserve call-before-
declaration behavior, conditional availability, repeated activation and duplicate
errors. Compilation must visit unexecuted bodies and retain their errors without
executing body effects. Preserve the existing three namespace import kinds and
function-name fallback; do not bulk-hoist every function-looking AST node.

Runtime frames must save caller continuation, source origin, local bindings,
compiler context, call/result mode and held argument values or reference cells.
Heap tables remain shared; a frame owns its actual locals and pending operands.
Separate returned values from returned references and bind each parameter once
in the correct order. Use existing location/reference and copy rules; retaining
an argument as a reference wrapper is different from copying its value.

Keep the request-global bindings and symbol order separate from each frame's
local ENV/CVS/SYMBOLS. GLOBALS access and superglobal names resolve the request
table inside functions, while ordinary locals use the frame table. Both routes
retain their actual shared heap-cell ownership. HTTPROOTS and ACTIVATED remain
request-wide; callbacks replace global bindings rather than frame locals.

Add return completion and cleanup through the existing control mechanism.
Top-level return and return from foreach must release active iterator ownership
while preserving final aliases. Function return restores caller context once,
including abrupt paths. Later finally/generator handling will extend this same
unwinding mechanism; do not encode return as blindly clearing TODO. Include
budget suspension inside argument evaluation, body execution and return cleanup.

The retained direct top-level witness is `copy-unwind-nested-return` in
`coverage/semantics/foreach-runtime-originals.json`: nested reference foreach
loops print `13`, then `return 7` skips the trailing `echo "bad"`. The exact source is now `calls0-top-return-alias` in the accepted139 catalogue:
return7/output13, cleared iterator/task roots and both surviving variable aliases
are independently checked. Its original Unsupported outcome stays historical.

The first coherent source campaign must cover ordinary named positional calls,
local/global separation, recursion, implicit and explicit return, alias/copy
behavior, conditional declaration timing, undefined function and duplicate errors,
namespace fallback, and compiler errors in dead function bodies. Admit parameter
and return forms only when their checks and runtime behavior are connected;
explicit remaining forms are the next steps below, not permanent exclusions.

## Complete the callable and signature protocols

Follow with positional/named/unpacked/variadic argument binding, by-reference
send/receive/return, defaults and strict/weak parameter and return enforcement.
Scalar argument strictness belongs to the call site; return enforcement uses the
function declaration/body context. Retain internal-call rules separately.
Capture argument side effects and diagnostic priority before implementation:
callee lookup versus argument evaluation, duplicate/unknown names, positional
after named arguments, unpack key/reference handling, too few arguments and
return-type failures. Existing scalar conversion helpers must be shared, while
function type enforcement must retain its own rules and diagnostics.

Then connect closure/arrow creation and invocation, captures by value/reference,
first-class callables, function statics, dynamic callable resolution and pipe.
Closures need actual identity, lexical capture roots and per-invocation locals;
no environment snapshot shortcut. The existing core intrinsic inventory governs
language-triggered builtins such as callable exit/clone and argument introspection.
Object-bound callable cases depend on the object activation below, and remain
assigned there with exact originals until the relevant mechanism exists.

## Declarations and classes

Use `LINKING-HANDOFF.md` for the reviewed type/signature/class-header/variance
interfaces and dependency ordering. Compile ordered member tables, activate
usable declarations at their proper phase, and implement lookup/link resumption,
trait binding, inheritance, constants, properties and method invocation. Required
builtin Attribute constant lookup is core work, not an ordinary-library exclusion.
Carry original owner identity separately from contextual class scope and preserve
all queued missing-name checks rather than declaring unavailable classes early.

Property/static/nullsafe quiet access, object-dependent foreach, method calls,
magic access and coercion then consume the same call/frame and unwinding machinery.
Exceptions, handlers/finally, dynamic source loading, generators/Fibers and
observable lifetime protocols remain subsequent required core work. Reuse the
existing effect and ownership infrastructure; callbacks must execute the PHP
semantics and may reenter it.

## Evidence and commit boundaries

Retain exact native/compiler/source originals before each correction. A bounded
compiler/runtime implementation and an independent reviewer own separate changes.
Make small compatible prerequisites separate commits; declaration activation,
frame runtime and source admission that depend on each other commit atomically
with targeted source/compiler/ownership/resumption checks. Reports and independent
acceptance follow separately. Refresh the full current source campaign at the
combined callable checkpoint or sooner if a shared regression cannot be bounded.
The final full syntax audit, fresh offline build and complete core validation
remain mandatory. Never use Zend execution as a semantic operation; never push.
