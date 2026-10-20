# Scalar and string dimensions

`44-dimension-read.watsup` supplies pure runtime R-fetch helpers. Delayed source dimension reads now delegate to it after resolving their base.
The ordered compiler separately uses its string constant-read leaf.
Array containers delegate to the existing array-read rules. Reference assignment and
acquisition cover writable array elements. String writes update their captured
locations; string-offset reference and nested fetches produce their PHP errors.

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

Module413 stages finite fitting lossy-float CV keys in ordinary array literals.
`ADD_ARRAY_ELEMENT` converts the key before its deprecation callback; its converted
integer survives later key writes or rebinding. An initially unwrapped
null/bool/int/float element CV supplies its live value if it remains unwrapped
and within those types after the callback. A captured nonconstant array temporary
instead retains its table and embedded
reference cells independently of live names. The continuation owns the builder
and captured temporary once, then transfers the temporary into the inserted entry.
Duplicate replacement preserves insertion position, and following items read
their keys and values afresh. Source, compiler ending lines, runtime/pool
distinctions, roots, raw steps and resumption are checked in the
[array-literal ledger](../../coverage/semantics/array-literal-float-key-warning-review.json).

This slice excludes objects reachable from the builder or captured array, both
before dispatch and on completion. Zend inserts even with a pending exception;
without objects, abandoning both graphs has the same observable cleanup. A
callback introducing objects enters explicit Unsupported on return or throw.
String CV elements and wider owning values remain outside this producer. Wrapped
CVs use only the separate bounded-array admission below.

The separate reference-element continuation acquires a direct CV's wrapper before
conversion. If the callback leaves or rebinds that CV to the same cell, insertion
transfers the acquired owner to an alias. If it rebinds the CV to an unwrapped
null/bool/int/float, insertion uses that live scalar directly and preserves the
acquired count: an existing debt cancels first, otherwise the old wrapper gains a
request owner. Supplied throws preserve that count while discarding the builder.
The acquired value may be primitive or an admitted untyped flat array; the
builder must remain object-free. Retargeting between different admitted reference
cells also records the omitted new-cell owner. This debt survives deletion of the originating entry and
abrupt builder cleanup. Copies at effective count1 unwrap the stored value; copies at
larger counts retain the alias. Same-cell insertion preserves an existing debt;
scalar and inverse-reference retargets cancel count biases per cell, including
repeated debts and residual positive owners. Logical edges are never removed to
represent the missing count. The [deficit ledger](../../coverage/semantics/array-literal-float-ref-deficit-review.json)
records fresh balanced source/state evidence; historical reference probes retain
zero credit in the [positive-owner ledger](../../coverage/semantics/array-literal-float-ref-key-warning-review.json).
Both acquired and new cells may also carry validated ordinary instance-property
type sources while their values remain null/bool/int/float. For debt-bearing
cells, every source object must survive logical pruning with its actual property
alias; type metadata adds no owner. A physical singleton copy unwraps without
carrying the constraint, while the original alias and shared copies still use
existing typed writes.
Fresh int-property witnesses check rejection, numeric-string coercion, multiple
type sources, supplied throws and inverse cleanup in the
[typed-source ledger](../../coverage/semantics/array-literal-float-ref-types-review.json).
Untyped reference cells may instead hold mutable nonpool flat arrays. Entries are
either DIRECT values (null/bool/int/float or validated byte strings) or bounded
ALIAS references described below. The debt remains on
the CELL, which owns one child table independently of its wrapper count. Singleton reference entries unwrap to DIRECT
array values; later child writes use ordinary COW. A still-indebted wrapper can
switch child tables while a direct CV retains its previous table. Stable same-cell
array insertion transfers the acquired owner without adding a request root.
Old array payloads also admit ordinary-scalar DIRECT completion: unmatched
acquired counts retain the wrapper and its child table, while existing wrapper
debt cancels first. Neither old nor current payload may be the active builder.
The [array-to-scalar ledger](../../coverage/semantics/array-literal-float-ref-array-scalar-review.json)
checks normal/throw transfer, debt cancellation and repeated owners.
The [flat-array ledger](../../coverage/semantics/array-literal-float-ref-arrays-review.json)
records fresh singleton/shared, deletion, supplied-throw and inverse-cleanup cases.
Array-valued type sources, pooled/immutable arrays, nesting and reference entries
outside the bounds below, other owning payloads, effective-zero, static/hooked/queued or retired
sources, coercion/backing records, active collection and outstanding request-end
debt remain explicit Unsupported before pruning. Ordinary by-value owning-CV
insertion remains partial.

A separate continuation stages ordinary unwrapped array-CV values. Array values
must be mutable nonpool flat arrays with the same bounded entries;
the builder stays object-free and distinct from their tables. The captured
old table gets one owner before conversion. An unwrapped completion uses the live
CV's table without its own ADDREF. `LITERALARRAYRETAINED` and `LITERALARRAYDEBTS` track
these HARRAY count biases separately from wrapper CELL biases. A same-table
retarget transfers its owner even if the original CV cell was retired. A different
retarget can make ordinary CV and literal values share writes at physical count1.
Deletion and supplied-throw cleanup preserve this table deficit; inverse retargets
cancel it before ordinary COW and teardown. The combined lifetime guard checks
positive flat tables after logical pruning and refuses effective-zero, active
collection or outstanding request-end debt before owner transitions.
The [ordinary array-CV review](../../coverage/semantics/array-literal-float-array-cv-review.json)
records these safe balanced cases. Mixed ordinary scalar/array retargets use the
same table counts: scalar-to-array completion owes one table owner or cancels a
retained occurrence, while array-to-scalar completion preserves the acquired count
or cancels debt. Initial scalar and array plans remain disjoint; captured runtime
array temporaries remain owned and frozen. The
[mixed-CV review](../../coverage/semantics/array-literal-float-mixed-cv-review.json)
checks both inverse cycles, entry deletion and supplied-throw cleanup with positive
physical counts. Wrapped scalar/string CVs, pooled/immutable tables, nesting and
reference leaves outside these bounds and other owning CV values remain Unsupported.
A callback may turn an initially ordinary array CV into an untyped reference
holding null/bool/int/float or a bounded array. Its by-value item then becomes an
ALIAS: the old HARRAY count is retained and the new CELL owes an owner. The
reciprocal reference-element callback may unset/recreate its CV as an ordinary
array, inserting DIRECT PARRAY and cancelling both count families. Physical
singleton copies unwrap; balanced shared copies preserve aliases, while child
snapshots and ordinary old-table writes keep their COW behavior. The
[CV/reference cycle review](../../coverage/semantics/array-literal-float-cv-ref-cycle-review.json)
checks normal, deletion and supplied-throw paths. These completion arms exclude
outer property/coercion/backing records and string CELL values; initial plans,
global gates and lifetime limits stay unchanged.
An initially wrapped untyped array CV captures its dereferenced CELL payload
slot before conversion. The existing ARRAY marker owns only builder and old table;
its REFERENCE locator adds no CELL owner. Completion reads that captured slot,
ignoring current CV rebinding, and inserts DIRECT PARRAY. The allocated marked
CELL has no property/coercion/backing records or CELL debt, and both CELL and
bounded payload must survive logical pruning even before any debt exists. Source
metadata remains valid when a locator retires; readiness then refuses explicitly.
An outside alias keeps the borrowed slot alive, while deletion/throw requires
another ordinary table owner to keep a new HARRAY deficit positive. Reciprocal
slot retargeting cancels old/new table biases before ordinary COW and teardown.
The [wrapped array-CV review](../../coverage/semantics/array-literal-float-wrapped-array-cv-review.json)
checks rebinding-only, payload cycles, deletion and supplied throw. Initial wrapped
scalar/string values, nonarray completion, typed outer cells and unsafe lifetimes
remain Unsupported; the ordinary/A19 gates and count/prune algorithms stay exact.
The [string-leaf review](../../coverage/semantics/array-literal-float-string-leaf-review.json)
adds ordinary tables and untyped wrapper payloads containing canonical-byte or
validated-carrier string leaves. String snapshots remain independent across
shared table writes and restored ALIAS copies. Singleton reference entries
unwrap before child/string COW.
Existing byte/carrier validation and string-offset COW rules remain in use;
direct string CV/cell payloads and array/object-valued leaves outside the bounds below stay Unsupported.
Embedded ALIAS entries may name live untyped cells holding null/bool/int/float
or canonical-byte/validated-carrier strings, without property/coercion/backing
receipts or CELL debt. Every leaf must survive logical
pruning: positive tables keep their leaf edges, including the bounded child-table
edges described below. Child-table COW preserves shared leaf references and unwraps singleton
leaves independently of outer table/wrapper counts. The
[alias-leaf review](../../coverage/semantics/array-literal-float-alias-leaf-review.json)
checks both counts, sibling-slot separation, deletion, supplied throw and inverse cleanup.
The [string-alias review](../../coverage/semantics/array-literal-float-string-alias-leaf-review.json)
extends only embedded leaf admission: shared string references propagate byte
writes, singleton copies detach, and earlier string snapshots stay unchanged.
Global primitive-cell and direct string CV/cell bounds stay exact.
Embedded null/bool/int/float or validated byte-string ALIAS leaves may also
carry validated ordinary instance-property type sources. Each source object
and actual property alias must remain live; for debt-bearing payloads they must
survive logical pruning alongside the leaf. Type metadata adds no owner. Shared copies retain typed
rejection/coercion. Explicit property unset removes that source, permitting
singleton unwrapping when only its table entry remains, even while the object stays
rooted. Int-property witnesses, multiple sources and supplied throws are in the
[typed-leaf review](../../coverage/semantics/array-literal-float-typed-alias-leaf-review.json).
Object-valued leaves, static/hooked/queued or retired sources and
coercion/backing records remain outside this extension.
The [typed string-leaf review](../../coverage/semantics/array-literal-float-typed-string-alias-leaf-review.json)
checks shared byte writes and weak integer-to-string coercion, rejected array
writes, fixed snapshots and singleton byte COW after explicit property unset.
Global direct string CV/CELL retarget bounds remain unchanged.
Array-valued ALIAS leaves may hold one mutable nonpool child table of
DIRECT null/bool/int/float or validated byte strings. Child eligibility first
rejects all outgoing owner edges, before checking its DIRECT values; this excludes
recursive eligibility and cycles. The leaf has no CELL debt or coercion/backing
records, and its child has no HARRAY debt. Ordinary instance-property type sources
use the validation above. For debt-bearing payloads, the child and every source
object must survive the same logical prune. Positive outer tables keep leaf edges;
debt-free leaves keep their child-table edges. Shared leaf copies preserve ALIAS writes;
singleton leaves unwrap to DIRECT array values before independent child COW.
Snapshots and sibling writes separate these effects from outer table/wrapper
biases through deletion, supplied throw and inverse cleanup.
The [array-alias-leaf review](../../coverage/semantics/array-literal-float-array-alias-leaf-review.json)
records untyped cases; the
[typed array-leaf review](../../coverage/semantics/array-literal-float-typed-array-alias-leaf-review.json)
adds public array-property witnesses with scalar rejection, shared nested writes
and singleton copying after explicit property unset. Deeper owning children and
indebted descendants remain Unsupported.
DIRECT child-array entries use the same mutable nonpool, debt-free, edge-free
child bound. Their actual HARRAY nodes must survive logical pruning; repeated
entries contribute separate owner edges. A child write can therefore separate
one occurrence while another keeps its prior value, without an embedded leaf
CELL. Snapshot, repeated-child, deletion and supplied-throw witnesses in the
[direct child-leaf review](../../coverage/semantics/array-literal-float-direct-array-leaf-review.json)
separate child COW from outer HARRAY/CELL biases and inverse balancing. Child
eligibility still rejects outgoing owner edges before examining DIRECT values,
so no recursive eligibility or deeper graph is admitted.
Outer array-valued reference cells also admit validated ordinary property type
sources accepting the bounded payload. For debt-bearing cells, the payload and
every source object must survive the same logical prune. A physically singleton
reference entry unwraps during copying even while its property source stays
live: the copied array value permits scalar replacement and independent child
COW, while the original remains constrained. After inverse balancing, shared
copies retain the typed ALIAS. Explicit property unset detaches its constraint;
an extra alias keeps the count positive until balancing. The
[typed outer-array reference review](../../coverage/semantics/array-literal-float-typed-array-ref-review.json)
checks these paths, initial typed-old capture, deletion and supplied throw.
The source basis is pinned `Zend/zend_vm_def.h::ZEND_ADD_ARRAY_ELEMENT`,
`Zend/zend_hash.c::zend_array_dup_value`, and
`Zend/zend_operators.h::zend_dval_to_lval_safe`, with string writes from
`Zend/zend_execute.c::zend_assign_to_string_offset`.


`45-dimension-write.watsup` supplies separate callback-free write and reference
fetch helpers registered in the source module catalog. `$string_dimension_write`
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
before callbacks are admitted. Source integration resolves the writable prefix
once, then commits returned string bytes to that captured root or element location.
An intermediate string dimension uses the nested fetch error; the final reference
dimension uses the reference error. Existing array paths retain COW and delayed
key/RHS timing, including RHS-before-overflow ordering for array append.

Run `python3 tests/semantics/dimension_write.py`. The canonical matrix compares
2,220 writes/reference/nested fetches with the pinned oracle, checking updated
container bytes, assignment results, ordered diagnostic bytes/levels/lines and
exact exceptions. Twelve additional boundaries check missing source positions,
request-environment rejection, borrowed reference operands and preservation of
prior held roots. Source validation additionally includes all eight retained
write/error-order conformance fixtures and 20 original-source ownership, capture
and multiline regressions. Nested string unset and callback behavior remain pending.

The reviewed source write activation passed the 664-case source campaign plus
23 outcome negatives and 103 independent additional write sources. One temporary
literal lvalue remains explicitly unsupported by the compiler; it is not counted
as a modeled PHP error. The helper matrix and ownership/origin campaigns were
repeated against the same implementation closure.
