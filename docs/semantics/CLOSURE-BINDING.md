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
class name, a user object of that class, or `"static"` for the source lexical
scope. The bound row roots its receiver while it is live. During operand
evaluation, the task roots the source closure and all sent operands. Immediate
simple-variable source selectors are checked against the live variable before
argument effects; later states retain the selected historical value.

The finite controls also cover the native warnings for binding an object to a
static closure and choosing internal `stdClass` as scope. Other source closure
kinds, internal-class receiver/scope objects, source closures with an active
receiver being unbound, named/unpacked binding operands, and computed binding
method names remain explicit boundaries of this increment. `Closure::call`,
rebinding captured method/getter/invoke wrappers, array callables and source
`__invoke` are subsequent callable work; they are not considered complete by
the 181 evidence. The [review ledger](../../coverage/semantics/closure-binding-review.json)
separates the original-base differential from current-base and installed checks.
