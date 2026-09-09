# Control compilation

`47-control-compiler.watsup` extends the ordinary compiler with if/elseif/else,
while, do and for, plus literal-depth break and continue. It retains the checked
source AST and the existing unit/path identity. Runtime continuations execute
these occurrences using the ordinary operand descriptors and permanent pools;
compiler order does not prescribe runtime order.

| Statement | Ordinary compilation order | Runtime order |
| --- | --- | --- |
| if/elseif/else | Each condition then its body, in branch order | Conditions until the selected branch, then that body |
| while | Body, condition | Condition, body, repeat |
| do | Body, condition | Body, condition, repeat |
| for | Initializers, body, steps, conditions | Initializers once, then conditions, body, steps, repeat |

These orders come from `zend_compile.c:5986-6230`. Every compiled expression
retains its schema field/index path, access role and emission line. Unselected
branches can therefore reject compilation before earlier runtime output. They
can also retain partial constant rewrites and ordinary constant operands. No
compile-time truth conversion is performed: even a constant NaN condition keeps
its runtime boolean-conversion warning. Reexecution consumes the same installed
literal occurrence; namespace fallback constants remain late runtime lookups.

The compiler's `LOOPS` field counts active loop contexts and restores the caller's
depth on normal or abrupt completion. It does not publish a runtime loop stack.
`zend_compile_break_continue` (`zend_compile.c:5813`) first checks the operand's
AST kind, then the positive integer value, then the available loop depth. Absent
operands mean one. A scalar integer literal greater than zero is valid; scalar
float/string operands produce the positive-integer diagnostic, while expressions
such as unary minus, constants or arithmetic produce the non-integer-operand
diagnostic. No constant prepass runs over a jump operand. The emitted diagnostic
bytes include the requested depth and preserve the selected compiler line.

Bare jumps use `statementTerminatorLine`; explicit operands use their own AST
line. `statementBodyLine` records a positive brace/colon token line for a synthetic
statement list or zero for a single statement. A bare empty body may be an empty
checked list or a comment Nop. Empty `for(;;);` has no non-null Zend child, so its
statement line comes from its own semicolon/closing-tag token. Braced/alternative
comment-only bodies use their opener, even when PHP-Parser materializes a lone
comment Nop. Missing or out-of-range required positions produce Unsupported.
Positive edited positions are range-checked input, not authenticated original
source; zero explicitly changes the supplied synthetic-list distinction.

`tests/semantics/control_compiler.py` retains original source/lint observations,
malformed and edited metadata checks, and exact expression-path order. The full
source campaign separately checks output, diagnostics, exit status, repeated
literal identity, namespace lookup and resumable execution. Nonterminating empty
for examples in the compiler campaign establish compilation only.

Switch, foreach, exceptions/finally, labels/goto, declarations/defaults and calls
remain separate obligations. Loop depth resets at future function compilation;
function bodies and call frames are not supplied by this module. Existing
frontend namespace-placement restrictions still precede some otherwise modeled
compiler diagnostics; edited checked helper evidence must remain separate from
original-source admission for those cases.
