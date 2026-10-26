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

A direct plain-CV NaN operand now stages its string-conversion Warning through a
named handler. Zend formats `NAN` before the callback, and unbuffered `ZEND_ECHO`
writes those bytes after it. A returning false handler can unset the CV: one
default Warning precedes `NAN`, then used print delivers integer `1`. A handler
that throws a supplied Exception still permits the cached `NAN` write before
exception search, while the enclosing assignment stays unchanged. The saved
bytes model the prepared string; its allocation identity cannot be observed in
this scalar, initially and finally unbuffered route. If the callback changes
output buffering, execution explicitly remains Unsupported. Two exact sources
and 135+120 reached-state premises are recorded in the
[NaN print review](../../coverage/semantics/print-nan-warning-review.json).
References, computed producers, buffering callbacks and wider output lifetimes
remain partial.

A direct nonempty flat primitive array CV now stages its `Array to string
conversion` Warning through a named handler. `ZEND_ECHO` uses the interned
`Array` result after the callback: a returning false handler can unset the CV,
then default warning and output precede print's integer `1`; a supplied throw
still writes `Array` before exception search and leaves the outer assignment
unchanged. A literal array retains its independent compiled-pool owner after
source unset. A runtime-built array instead retires before the pending output;
neither path adds a saved array owner to the print task or rereads the CV.
Initially empty output buffers are required, and a callback-created buffer is
explicitly Unsupported. Three exact sources and 137+122+122 reached-state
premises are recorded in the
[array print review](../../coverage/semantics/print-array-warning-review.json).
Empty/nested arrays, other producers and wider output lifetimes remain partial.

A named noarg by-value function can instead return a nonempty flat primitive
array as an acquired print operand. Its own `ZEND_ECHO` conversion warns at the
call's compiled line. The print continuation owns that array while the handler
unsets the source global, writes interned `Array`, then releases the temporary
before delivering integer `1` to the outer assignment. If the handler throws a
supplied Exception, the write still occurs before the temporary retires and
exception search begins; the outer assignment stays unchanged. A runtime-built
source copy has two owners at entry, one after source unset and through output,
and none after release. This initially unbuffered route is limited to the
authenticated named function call and flat array; other producers, nested or
empty arrays, output-buffer changes and wider lifetimes remain partial.

Validation is separate by boundary: 20 author source comparisons, ten native
compiler/lint comparisons with 51 source projections, and 15 independent reviewer
source comparisons. Four paused stages check 61 assertions, with an independent
fixture replay. Six existing consumers pass separately; two dependency controls
remain Unsupported. Two retained official match programs agree on a disposable
combined tree. Canonical integration binds identical semantic inputs. Source counts
do not establish full core coverage. See [review](../../coverage/semantics/print-review.json);
raw fixtures and process records live in its ignored evidence directories.
