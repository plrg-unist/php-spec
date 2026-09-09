# Array unpacking

The checked source compiler and runtime implement array-valued spread operands
at PHP 8.5.10 CLI NTS64. Integer keys append in traversal order, preserving the
builder's next-index history; string keys replace an existing entry in place.
Nested array values retain copy-on-write behavior. Explicit embedded references
remain shared when they have multiple owners; singleton wrappers are unwrapped
for the copied entry. The source container's own wrapper history survives.

`60-array-unpack.watsup` supplies the pure transfer and shared scalar diagnostic.
`61-array-unpack-control.watsup` evaluates each spread operand once at its checked
item/value occurrence, resolves the operand at its compiler ending line, and
continues with the next original item index. The continuation owns the fresh
builder throughout operand evaluation. Transfer borrows both containers, then
restores the caller's temporary roots. It never imports a native execution result.

The constant prepass first visits every array item, retaining the existing hole
and child-error order. It then constructs a fully known array, including spread
operands. A fully known scalar spread produces a compiler fatal diagnostic;
scalar spread in a dynamic array raises a runtime Error when reached. Integer
append overflow defers constant construction to execution, preserving prior
output. The ordinary compiler treats spread operands as reads. Pooled constant
results keep their permanent occurrence owners.

The pinned engine routes are `zend_try_ct_eval_array` and `zend_compile_array`
in `vendor/php-src/Zend/zend_compile.c`, `ZEND_ADD_ARRAY_UNPACK` in
`Zend/zend_vm_def.h`, and the existing reference-copy paths in `Zend/zend_hash.c`.
The high-level rule models their observable ordering and ownership without
requiring the engine's packed-table representation.

`tests/semantics/array_unpack.py` retains 154 exact authored source inputs,
including the 112 runtime originals and 42 compiler originals. Its 31 checked
source state controls cover alias transfer, nested values, cycles, literal reuse,
root cleanup and dense loop resumption; only budget-exhausted states are resumed.
These checks do not close the array or spread families. Traversable objects,
iterator callbacks and their failures require the later object/frame protocol.
Argument unpacking is a separate call-semantics obligation. Reports at the later
combined container checkpoint establish the then-current broad source closure.

Accepted code `4ca826d2` and author evidence `7ac2519f` pass 155 exact source
comparisons and 24 outcome negatives, 31 state programs/2,454 assertions, and
42 native compiler lints plus 10 descriptor controls. The extra source is the
retired Unsupported control `<?php $a=[...[]];`; it is now an ordinary source pass.
[Independent review](../../coverage/semantics/array-unpack-review.json) audits every
ordered source row and retains eight additional native/state programs with
1,368 assertions. The earlier full ordinary campaign remains historical.
