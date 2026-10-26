# Echo sibling output

PHP 8.5.10 compiles each expression in an `echo` statement to a separate
`ZEND_ECHO`. Each operand is evaluated, converted and written before the next
operand starts. If conversion leaves a pending exception, the current write
finishes and the later expressions are skipped.

For an initially unbuffered multi-expression echo, a first direct plain CV
containing a nonempty flat primitive array stages its `Array to string
conversion` Warning through a named E_WARNING handler. The first task retains
the source occurrence, line and interned `Array` result without rereading or
owning the array after the callback. A literal array keeps its separate
compiled-pool root when the handler unsets the CV (table owners 2→1).

A handler returning false permits one default Warning, then writes `Array` and
evaluates the remaining siblings in order. The next function call sees the
handler's mutation of a separate CV. A handler throwing a supplied Exception
still writes `Array` before exception search and never enters that later call.
The saved source-origin return and later EVAL/EMIT pairs remain intact on the
normal path. A callback-created output buffer is explicitly Unsupported.

Two source agreements and 153+137 reached-state checks, including authentic
first-child and sibling origins, are recorded in the
[echo array review](../../coverage/semantics/echo-array-warning-review.json).

The same continuation now admits a direct flat-array CV at child 1 of an echo
with a later child. Child 0 must finish before this CV is read. In the reviewed
two-array sequence, the first handler changes child 1 from integer 7 to a
runtime-built array; the second child therefore raises its own Warning. A
returning second handler unsets that array, then writes the fixed interned
`Array` and continues to the later call. A throw from either handler writes its
current `Array` and skips every remaining child. The first literal table keeps
its pool root (owners 2→1); the new runtime table retires (1→0) in the second
handler. Three source comparisons, including the previously supported
first-handler throw control, and 167+151 reached-state checks are recorded in
the [two-array review](../../coverage/semantics/echo-two-array-warning-review.json).
Two fresh scalar-prefix controls also agree. A handled child-1 Warning writes
cached `Array` after its handler unsets the source CV, without a default
Warning. An ineligible mask skips the handler and reports the default Warning
at child 1.

Empty or nested arrays, other producers, changed output buffers and wider
output lifetimes remain partial.
