# Print expressions

Modules 145/146 implement `print` through the existing output conversion and
compiled-effect machinery. The target is the pinned PHP 8.5.10 CLI build.

`zend_compile_print` in `vendor/php-src/Zend/zend_compile.c` compiles the operand,
emits `ZEND_ECHO` with `extended_value = 1`, and returns an `IS_CONST` integer 1.
The specification likewise compiles the child in read mode, preserving its final
compiler line, then records constant 1 and a `PPCEFFECT` for the print occurrence.
The constant-expression prepass still stops at print; this is an ordinary
compiler operand result, not a constant-expression rewrite.

The effect survives folding by arithmetic, truth and other enclosing consumers.
Existing effect selection retains only outermost effect roots, so nested print
or suppression effects execute once. Constant branch selection can skip an
unvisited operand while retaining the print that determines that selection.

Print is a temporary expression in write contexts. Its constant result is neither
a variable nor a call result for reference demand: reference arguments evaluate
and print before the send error; reference returns use the existing nonvariable
notice/value behavior. These classifications do not inherit the operand's kind.

At runtime the operand evaluates once before conversion and output. Successful
conversion emits its bytes and yields integer 1. Conversion warnings and abrupt
completion use the existing stringify rules; an abrupt operand produces no print
output or result. Admitted scalar, array-warning and object-error behavior shares
echo's conversion. User-defined `__toString` and method-handler behavior remain
explicit Unsupported dependencies. Output callbacks and lifecycle protocols
remain separate core work.

A suspended `PRINT_EMIT` retains the print occurrence and its compiler completion
line. Its entry guard checks the active origin, source node, compiled read value
and line. The ordinary source/descriptor guard also checks direct print entry.
Child calls and saved tasks use the existing origin and ownership machinery.

Validation is separate by boundary: 20 author source comparisons, ten native
compiler/lint comparisons with 51 source projections, and 15 independent reviewer
source comparisons. Four paused stages check 61 assertions, with an independent
fixture replay. Six existing consumers pass separately; two dependency controls
remain Unsupported. Two retained official match programs agree on a disposable
combined tree. Canonical integration binds identical semantic inputs. Source counts
do not establish full core coverage. See [review](../../coverage/semantics/print-review.json);
raw fixtures and process records live in its ignored evidence directories.
