# Scalar and string dimension reads

`44-dimension-read.watsup` supplies pure runtime R-fetch helpers. It is not yet
listed in the source machine's module catalog: source scalar/string dimension
reads remain pending until the checked constant-expression prepass is integrated.
Array reads continue through the reviewed source path. Reference assignment and
acquisition now cover writable array elements; string-offset reference/write
contexts remain separate pending work.

`$dimension_read(state, container_value, key_operand, line)` returns state with
`RESULT`, ordered `EVENTS` and `COMPLETION`. It delegates arrays to `$array_read`.
Scalar containers resolve the key to preserve undefined-variable diagnostics,
without applying array-key conversion, then warn and return null. Boolean names
in that warning are `true` or `false`. String containers return one byte, including
negative indexing from the end. Out-of-range offsets warn and return an empty
string. Integer numeric text is accepted; trailing text warns, with C-string
truncation at NUL. Numeric text classified as floating-point is a TypeError.
Float/null/bool keys issue the string-offset cast warning; float conversion then
uses the silent integer operation, without a second precision/NAN/INF diagnostic.

The source anchors are pinned `Zend/zend_execute.c`:
`zend_fetch_dimension_address_read`, `zend_illegal_string_offset`, and
`Zend/zend_API.c::zend_zval_value_name`. The helper consumes already captured
container values and resolves delayed/reference key operands. It does not prune
inside helpers or invoke callbacks. Future warning handlers require explicit
resumable ownership: the engine holds a string while a handler may replace it.
No handler, object dimension, isset/empty, list, or write-context behavior follows
from these R-fetch rules.

`$string_constant_read(bytes, key_value)` is a distinct compiler leaf returning
an optional value. It implements only `zend_eval_const_expr`'s string DIM fold:
nonnegative, in-range integer offsets and integer numeric text, including trailing
text, fold silently. Negative offsets, floating keys and other cases do not fold.
It neither traverses arbitrary expressions nor allocates a source occurrence.
The compiler-context worker owns that traversal and attaches facts to checked
source-unit/occurrence identities.

This distinction is observable: `echo "abc"["1x"]` warns, while the same expression
inside either a constant or dynamic array literal is folded without that warning.
Assignments stop the prepass traversal, and negative `"-1x"` remains a warning at
runtime. The independent conformance fixtures retain these cases. Runtime helpers
must not be substituted for compiler folding merely because their values agree.

Run `python3 tests/semantics/dimension_read.py`. It compares 583 container/key
pairs against the pinned PHP runtime, with exact result types, values, ordered
messages, severity, lines and exception observations. Ten compiler-leaf assertions
and five missing-line/borrowed-key boundaries are reported separately. The report
retains original oracle source, input bytes, stdout, stderr, status and stable
implementation/binary fingerprints. This is helper evidence, not source execution
coverage or a proof that string dimensions are complete.
