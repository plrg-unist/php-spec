# Scalar and string dimensions

`44-dimension-read.watsup` supplies pure runtime R-fetch helpers. Delayed source dimension reads now delegate to it after resolving their base.
The ordered compiler separately uses its string constant-read leaf.
Array containers delegate to the existing array-read rules. Reference assignment and
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
implementation/binary fingerprints. This matrix is helper evidence. Source activation additionally retains all 16
read/prepass conformance fixtures and 15 original compiler emission-line cases
in `validate.py`; it does not establish complete dimension or callback behavior.


`45-dimension-write.watsup` supplies separate callback-free write and reference
fetch helpers, outside the source module catalog. `$string_dimension_write`
returns a state and updated container bytes. It resolves/converts the key first;
an index below the negative bound warns and returns null before fetching a
delayed RHS. Otherwise it stringifies the RHS, rejects empty strings, warns for
multiple bytes, writes the first byte, and returns that byte as the assignment
value. Positive offsets beyond the current length extend with spaces. The pure
byte operation assumes allocation succeeds, like the current array model;
allocation failure and environment memory limits remain separate pending effects.

`$string_dimension_fetch` handles reference and nested-array W-fetch errors.
These contexts check key conversion first, then reject the operation without
checking byte bounds. An invalid key's TypeError therefore takes precedence over
the reference/nested-array Error. Append syntax has its own Error. Scalar write
promotion/errors remain in the existing array-location helpers.

The pinned source anchors are `zend_assign_to_string_offset`,
`zend_check_string_offset`, `zend_fetch_dimension_address`, and
`zend_wrong_string_offset_error` in `Zend/zend_execute.c`. These helpers restore
no temporary roots because they acquire none and never prune internally; callers
must preserve the input operands while consuming them. Handler suspension and
string replacement during warnings need an explicit resumable ownership protocol
before callbacks are admitted. Source integration must commit returned bytes to
the correct captured location and preserve delayed RHS timing.

Run `python3 tests/semantics/dimension_write.py`. The canonical matrix compares
2,220 writes/reference/nested fetches with the pinned oracle, checking updated
container bytes, assignment results, ordered diagnostic bytes/levels/lines and
exact exceptions. Twelve additional boundaries check missing source positions,
request-environment rejection, borrowed reference operands and preservation of
prior held roots. This validation does not admit new source syntax or establish
callback behavior.
