# No-constructor allocation arguments

For admitted empty user classes and `stdClass`, `new C(args)` resolves the
class and allocates an object before evaluating arguments. The compiler keeps the NEW
root line separate from each argument's send line and authenticates immediate
send facts against checked source. The runtime retains the allocated object and
sent values through the dummy call, including nested calls, then releases
temporary owners on completion or abrupt exit. Positional values have their
effects. A direct unknown named argument evaluates its expression, then rejects
the name before resolving a deferred variable fetch. Unpacking evaluates its
operand before validating ordered entries. Static argument-shape errors precede
runtime class lookup.

The rules are in `131-noctor-compiler.watsup` and
`132-noctor-runtime.watsup`. [The review](../../coverage/semantics/noctor-args-review.json)
binds compiled facts, source outcomes and paused-state ownership checks.
Classes with constructors, dynamic class targets, methods and properties remain
separate obligations.
