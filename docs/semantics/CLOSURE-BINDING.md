# Ordinary Closure binding

The bounded `181` increment admits literal `$closure->bindTo(...)` and
`Closure::bind(...)` when the source is an ordinary real closure. It evaluates
the binding operands before making a new closure. The new closure copies
captured values and static-local cells, while reference captures still alias
their original cells. Calling the original and the bound copy therefore has
separate static-local progress. A source closure may be released after binding;
the copy owns its captures and bound receiver, not the old closure object.

The bound record retains the source call site and original closure identity as
provenance, the lexical scope used for private access, the called class, and
the optional receiver. A receiver supplies the called class; without one, the
called class is the lexical scope. The scope argument may be an admitted user
class name, a user object of that class, `"static"` for the source lexical
scope, or explicit `null`. With an object receiver and no lexical scope, Zend
supplies its dummy internal `Closure` scope; module253 carries that scope and
called class. The bound row roots its receiver while it is live. During operand
evaluation, the task roots the source closure and all sent operands. Immediate
simple-variable source selectors are checked against the live variable before
argument effects; later states retain the selected historical value.

The historical181 finite controls also cover the native warnings for binding an
object to a static closure and choosing internal `stdClass` as scope. That
evidence retains its original bounded scope.
[Current Closure and fake binding253](CLOSURE-CURRENT-BINDING.md) adds genuine
CONFIG argument transport, computed/imported API sites, fake method/function/
getter/intrinsic binding, shared source statics and the internal REAL scope carrier.
Module264 completes the admitted REAL binding warning and null-unbinding routes.
After resolving scope, a nonnull receiver on a static Closure warns first;
removing an existing receiver from a `USES_THIS` Closure warns next; changing to
an internal class scope warns last. Selected warnings suspend through the real
error handler and return null without making a copy, even after callback writes
or class declarations. Handler throws retain their writes and unwind normally.

`USES_THIS` is a compile flag derived from the function's own compiled expression
entries. Direct `$this`, property/method/send/isset/empty uses and eager literal
name concatenation count, including dead code. Nested Closure bodies and runtime
name or general constant folding do not set the enclosing function's flag.
Without a previous receiver, even a `USES_THIS` body may bind null. A valid
unbind keeps the selected lexical scope, sets called scope to that scope, removes
the receiver, copies REAL statics and preserves captured reference cells.
Explicit null scope removes the original class permission.

The [REAL binding ledger](../../coverage/semantics/real-closure-binding-review.json)
records the new warning/frame/owner checks separately. Temporary-call and captured
internal API consumers remain required. The [original review ledger](../../coverage/semantics/closure-binding-review.json)
separates the original-base differential from current-base and installed checks.
