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
echo's conversion. User-defined `__toString` uses the shared resumable method
rules; wider output callbacks and lifecycle protocols remain partial.

A suspended `PRINT_EMIT` retains the print occurrence and its compiler completion
line. Its entry guard checks the active origin, source node, compiled read value
and line. The ordinary source/descriptor guard also checks direct print entry.
Child calls and saved tasks use the existing origin and ownership machinery.

An initially unbuffered print of a direct noarg by-value untyped function's
Stringable result retains its temporary separately from the cast receiver.
Text is written before temporary retirement; the nonthrowing destructor runs
before outer assignment while print's integer `1` remains protected. A borrowed CV
unset inside the method instead retires before text. A supplied method throw
emits neither text nor print’s `1` and retains its Exception through destruction.
Two acquired source agreements, one borrowed control and 505 recipe premises
(including derived guards/default-buffer history) pass in the
[lifetime review](../../coverage/semantics/print-stringable-lifetime-review.json).
Other producer forms, positive-handler execution and wider lifetimes remain partial.

Validation is separate by boundary: 20 author source comparisons, ten native
compiler/lint comparisons with 51 source projections, and 15 independent reviewer
source comparisons. Four paused stages check 61 assertions, with an independent
fixture replay. Six existing consumers pass separately; two dependency controls
remain Unsupported. Two retained official match programs agree on a disposable
combined tree. Canonical integration binds identical semantic inputs. Source counts
do not establish full core coverage. See [review](../../coverage/semantics/print-review.json);
raw fixtures and process records live in its ignored evidence directories.
