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
inside helpers or invoke callbacks. Source callbacks use the separate continuation
below; object dimensions, isset/empty, list and write contexts retain their own rules.

Module425 stages ordinary string R-offset cast, leading integer text and bounds
Warnings. A cast callback can change the live primitive offset while the selected
old carrier survives; float conversion stays silent. Interned carriers and
authenticated owning temporaries survive independently. A borrowed REQUEST carrier survives when its
exact identity remains in the same selected live ordinary CV cell, marked or
unmarked. If that selection changes, a different current name may keep the
original cell, or a different ordinary unmarked CV may retain the exact
authenticated non-NUL header. Current name lookup and live-cell capture establish
these owners; shadowed rows, equal bytes with another identity and immutable
STRINGDATA alone do not qualify. The [retained-carrier review](../../coverage/semantics/string-offset-retained-carrier-review.json)
records ordinary return and supplied-exception discard, with unchanged destination
on throw. A dropped borrowed carrier without this proof retains Unsupported.
Neither the base-cell nor key-cell locator becomes a heap root.

A dedicated base capture admits an ordinary marked CV holding valid non-NUL
interned bytes, with the same liveness and constraint fences. It saves the
dereferenced immutable header before the Warning: writing `XYZ` through a base
alias leaves the selected `abc` available, while the live key can become `2` and
select `c`. A supplied exception preserves its identity and the destination `99`.
The [reference-base review](../../coverage/semantics/string-offset-reference-base-review.json)
keeps two original source agreements, separate author/peer state checks and three
derived affected-entry projections distinct. Generic capture, keeper, key and
root rules stay unchanged.

Authenticated non-NUL REQUEST bases use that bounded reference capture. Their
current-cell provider proof and the existing ordinary-keeper alternative use
the same current capture to partition readiness. A handler can keep the exact
header in the selected marked cell; replacing that referent can instead use a
different live ordinary unmarked CV retaining the saved identity. The
[referenced REQUEST review](../../coverage/semantics/string-offset-reference-request-base-review.json)
separates two same-header source agreements from derived keeper-composition and
wrapper-timing checks. Removing the selected name can now use a current alias of
the original cell, authenticated by the same base capture. Plain `$GLOBALS`
unset leaves that marked cell and exact REQUEST header live through one surviving
alias. The [same-cell alias review](../../coverage/semantics/string-offset-reference-alias-keeper-review.json)
separates two new source agreements, author/peer AL cuts and two affected helper
projections. STRINGDATA alone supplies no owner. Different marked keeper cells,
dead aliases and wider ownership histories remain partial; roots stay unchanged.

An ordinary marked primitive reference key can use null, bool, bounded int or a fitting
float. Its key-only capture checks the current binding, same live cell and prior
constraint fences; the generic base and keeper captures stay unchanged. After a
cast Warning, conversion reads the live referent while the key still selects
that cell. The [reference-key review](../../coverage/semantics/string-offset-reference-key-review.json)
separates two new interned-base source agreements from the affected REQUEST-base
entry/resume fixture. Existing REQUEST provider proofs compose without gaining
base or lifetime authority.

Marked floats with range diagnostics remain partial: references created during
the handler can use a warning-capable converter, while an initially unwrapped
DOUBLE uses the silent path. The descriptor does not preserve that distinction.
Key rebinding/removal, constrained cells and NUL combinations retain their fences.

For valid non-NUL interned base and key strings, leading integer text such as
`"1x"` keeps the integer computed before its `Illegal string offset` Warning.
Completion reads the old bytes even if the handler replaces the base and unsets
the key. A subsequent bounds Warning uses that same integer and old string length;
the saved text authenticates the exact index. The [leading-text review](../../coverage/semantics/string-offset-leading-text-review.json)
records the first Warning, ensuing bounds callback and supplied-exception cleanup.
Initially marked ordinary reference keys now enter this same fixed-index branch
when both base and leading-text key are valid non-NUL interned strings. A handler
writing `2` through the key alias still reads `b` from saved index `1`; removing
both key names before a supplied throw leaves the original exception and
destination intact. The borrowed key cell can retire after capture. The
[referenced leading-key review](../../coverage/semantics/string-offset-reference-leading-key-review.json)
keeps two source agreements, separate author/peer AL cuts and the derived old CAST
guard distinct. Current text remains refused on the live primitive CAST path.

An initially unmarked ordinary CV can also supply authenticated non-NUL REQUEST
leading text against a valid non-NUL interned base. Acquisition checks its current live cell;
the saved receipt then authenticates immutable bytes and the fixed integer after
the handler overwrites or unsets that key. Neither the formatted Warning message
nor the saved integer needs a surviving key owner. Source and phase checks retain
the same integer for a later bounds Warning. The
[REQUEST leading-key review](../../coverage/semantics/string-offset-request-leading-key-review.json)
separates two source agreements, author/peer state cuts and derived affected-source
checks.

Initially marked ordinary reference keys also acquire valid non-NUL REQUEST
leading text against a valid non-NUL interned base. Key capture keeps its current
binding, liveness and constraint checks; the existing saved receipt then survives
alias writes and removal of both key names without adding an owner. The
[referenced REQUEST leading-key review](../../coverage/semantics/string-offset-reference-request-leading-key-review.json)
records two new source agreements and separate state and derived entry checks.
Live REQUEST text remains refused on the ordinary CAST path. REQUEST leading
bases use the bounded owner proof below; constrained cells and wider producers
retain their boundaries.

An ordinary base CV holding a valid non-NUL REQUEST string and an ordinary key
CV holding valid non-NUL INTERNED leading text use a separate acquisition and
saved-index receipt. Current provider and retainer
proofs keep the selected header available when a handler replaces the base CV.
Two source comparisons retain it through a different ordinary keeper; a derived
composition also checks the existing same-selected-cell alias proof. Source
validity records the saved meaning, while readiness requires a current owner.
Losing that owner produces explicit Unsupported on normal return or pending
Throwable discard. Once bounds have been selected, completion remains fixed
and owner-free. The [REQUEST leading-base review](../../coverage/semantics/string-offset-request-leading-base-retainer-review.json)
keeps source, state and derived affected-front cuts distinct.

The same receipt now admits ordinary or marked CVs for both the REQUEST base
and its valid non-NUL INTERNED or REQUEST leading-text key. Acquisition uses the
existing base/key captures and preserves actual cell and header identity,
including a single selected cell shared by four names. The index and message remain fixed
before the callback; both selected cells may retire before a supplied throw.
A distinct ordinary keeper can retain the old base after all aliases change.
Normal and Throwable lost-owner paths still return Unsupported. The
[carrier-matrix review](../../coverage/semantics/string-offset-request-leading-carrier-matrix-review.json)
keeps four source agreements, author/peer state cuts and the finite affected
ingress check separate. Constrained/direct-reference operands, NUL combinations,
computed/owning key producers and wider owner histories remain partial.

Once an out-of-range offset is selected, completion returns the fixed empty
string even if the bounds callback unsets both operands. A cast-handler throw
still converts the live key; a leading-text handler throw uses the saved integer.
Both check old bounds: an eligible registered handler suppresses the remaining
Warning, while an absent handler permits its default
display before the original Throwable unwinds. Source validity survives callback
writes and retired cells, separately from cast readiness. Other REQUEST text histories,
other text-entry Warnings, undefined or other marked text keys, constrained locators and wider
string-owner histories remain partial. The [string-read review](../../coverage/semantics/string-offset-read-warning-review.json)
retains source and independent reached-state evidence, including the zero-credit
borrowed-carrier release control.

Compiled literal bases now satisfy that existing R-read source certificate through
an origin-aware `233` arm: the captured interned value, actual base child, raw
pool bytes and existing literal producer must agree. Raw, CV, reference and
computed-base arms stay unchanged; no carrier rewriting, locator, provider, root
or release rule changes. Two exact sources cover accepting cast/bounds handlers
and live cast-key versus fixed bounds behavior. The separate 93-condition AL
recipe checks the actual resume, source/identity refusals and unchanged ownership.
The [literal-base review](../../coverage/semantics/string-literal-base-review.json)
keeps the two original Unsupported baselines at zero credit and retains that
defined-key cut. Other handler effects and wider owner histories remain partial.

An initially undefined ordinary key CV on a literal non-NUL interned base now
keeps its authenticated `KEY_CV` receipt after the Undefined Warning. That receipt
forces the cast Warning even if the first handler defines an integer key. Resume
then reads the current null, bool, int or float CV, or silently uses NULL if it is
still missing.
An out-of-range index is fixed before its bounds callback. Two exact SL originals
cover key `1` to `5` to `0` with a fixed empty result, and an untouched CV returning
`a` with only the Undefined and Cast messages. A source-reached AL recipe checks
126 conditions, including 28 derived controls, through the three genuine
continuations. The [undefined-CV ledger](../../coverage/semantics/string-offset-undefined-cv-review.json)
retains the original producer-continuation refusal at zero credit. Generic
retention and root rules stay in use; REQUEST/marked keys, other base producers,
abrupt-handler and wider lifetime histories remain partial.

After that initially undefined CV path, a current ordinary unmarked non-NUL
interned string now uses the silent string-to-integer cast, including leading
text, nonnumeric zero and numeric-text saturation. It does not reenter the
initial string-key validator or emit an `Illegal string offset` Warning.
Two exact SL originals cover first-handler `"1"` followed by cast-handler
`"2tail"` selecting `c`, and no first write followed by `"noise"` selecting `a`.
The new source-reached AL recipe passes 97 conditions, including 23 derived
controls for conversion and source/carrier refusals. The
[current-string-CV review](../../coverage/semantics/string-offset-current-string-cv-review.json)
keeps these cuts and earlier failures separate; the old AL126 cut is not renewed.
Generic offset, capture, phase, provider, retainer and root rules stay unchanged.
Marked current keys, NUL, abrupt handlers and wider base/lifetime
contexts remain partial.

Authenticated non-NUL REQUEST strings in that current ordinary CV now share the
silent conversion. The state-aware helper requires the exact carrier from the
live selected unmarked cell; registry bytes alone add no owner. Two exact sources
use two nonempty CVs for runtime concatenation: `"2tail"` selects `c`, while
`"noise"` selects `a`. Author AL109 and independent AL80 retain separate cuts,
each with 34 derived controls, including stale identities, dead or shadowed cells
and source refusals. The [current-REQUEST-CV review](../../coverage/semantics/string-offset-current-request-cv-review.json)
keeps source comparisons, state checks and joined loading distinct. Generic
offset/capture/source/phase/provider/retainer/root rules stay unchanged. Marked,
constrained, NUL and other current value kinds, broader bases and abrupt/lifetime
histories remain partial.

That initially undefined CV receipt also admits current ordinary arrays with
finite DIRECT scalar entries. Empty arrays silently convert to index 0 and
nonempty arrays to index 1 after the mandatory cast Warning. The exact current
CV must capture an ordinary live cell and select an in-range, physically
allocated, logically live HARRAY. Retained array metadata or a different live
table cannot authorize conversion. Scalar payloads are classified by kind and
never read or coerced. Existing pool/CV sharing needs no copy, callback or new
owner for this immediate count read.
Two exact originals agree at `f02e8d7a6`/private508, reusing each native once.
Author AL95/43-derived and independent AL85/35-derived retain separate source0
cuts. The [current-array review](../../coverage/semantics/string-offset-current-array-cv-review.json)
keeps the finite checkpoint, corrected helper count and original failures
separate, without a unique aggregate. Initial ARRAY offsets retain their illegal
offset path. Marked/constrained current keys, wider entries, broader
bases and abrupt/lifetime histories remain partial.

A separate nonempty ALIAS-only route admits initialized null, Boolean, signed
64-bit integer and binary64 reference payloads. Each actual marked reference cell
must satisfy the existing plain-cell validator and remain logically live; typed,
coercion and parameter-backing constraints stay excluded. The converter uses the
array's nonempty count, while admission only validates the referent domain.
Repeated references preserve their separate HARRAY-to-HCELL edges, and conversion
adds no owner or payload conversion. The earlier DIRECT predicate and converter
API remain unchanged.
Two exact originals agree at `6b73bf7cb`/private508 with native-once reuse: a
zero-valued referent and two entries sharing false both select index 1, not the
referent truth or raw element count. Author AL106/49-derived and independent
AL117/58-derived retain separate source0 cuts. The
[alias-entry review](../../coverage/semantics/string-offset-current-array-alias-cv-review.json)
keeps the genuine pre-code checkpoint and parser-only peer fixture failure
separate. NUL/raw string or wider reference payloads, constrained
cells, initial ARRAY offsets and broader lifetime contexts gain no route.

Finite DIRECT/ALIAS mixtures now compose those existing per-entry guards in
order. The exact current CV/table authority and count-only conversion remain;
neither payloads nor reference edges are copied, converted or released. The old
homogeneous predicates and converter API remain literal. Two exact originals at
`12eeccb6f`/private508 reuse native observations once: `[0, &$false]` and three
entries `[&$false, false, &$false]` both select index 1. The latter distinguishes
nonempty conversion from false payloads and the raw entry count.
Author AL112/61-derived and independent AL124/64-derived retain separate source0
cuts. The [mixed-entry review](../../coverage/semantics/string-offset-current-array-mixed-cv-review.json)
keeps the pre-code 48-condition actual checkpoint and Unsupported baselines at
zero credit. Only two earlier derived mixed refusals are promoted, with both
replacement shapes checked; no historical campaign is replayed or renewed.
Initial ARRAY offsets, wider ALIAS payloads or constraints, nested/object DIRECT
entries, marked current keys and broader base/abrupt/lifetime contexts remain partial.

Current arrays also admit non-NUL INTERNED and authenticated REQUEST strings in
initialized marked unconstrained reference cells. Admission requires the existing
carrier check and physical/logical cell liveness; registry identity alone adds no
owner. The primitive ALIAS helper stays literal. Conversion still uses only array
nonemptiness and preserves the cells, carriers and repeated edges.
Two exact originals at `5e8067ef3`/private508 reuse two native observations once:
an INTERNED zero string and a repeated REQUEST `2tail` string both select index 1,
which differs from payload conversion and the latter's three-entry count.
Author AL90/41-derived and independent AL107/51-derived retain separate source0
cuts. The [string-payload review](../../coverage/semantics/string-offset-current-array-string-alias-cv-review.json)
keeps the genuine 54-condition pre-code REQUEST checkpoint, Unsupported baseline
and peer pre-AL binding-order failure at zero credit. Only the affected peer fixture
is retried; four old string-payload refusals are superseded without old-suite replay.
NUL/raw ALIAS string payloads, owning or constrained referents and broader current-CV/base/
abrupt/lifetime histories remain partial; initial ARRAY offsets stay illegal.

Ordinary valid non-NUL `INTERNED_STRING` and authenticated `REQUEST_STRING`
carriers delegate to the existing byte rules for `??`, `isset`, and `empty`, as
both containers and string keys. A REQUEST forward validates the registry index,
exact immutable STRINGDATA bytes and byte range, then checks the absence of NUL.
Runtime concatenation with two nonempty operands creates this identity without
a request provider. Registry identity remains metadata with no heap owners.

The [interned review](../../coverage/semantics/string-offset-quiet-carriers-review.json)
retains its original SL cuts. The
[REQUEST review](../../coverage/semantics/string-offset-request-carriers-review.json)
separates two ordinary SL agreements, 133 author AL conditions including 24
derived guard conditions, 95 independent AL conditions, and 222 affected interned
AL conditions. Raw query steps preserve storage and STRINGDATA, including the
false byte `"0"` selected by a concatenated `"-1"` key. Malformed and NUL carriers
retain their prior boundaries; existing lifetime and handler fences remain.

Terminal string `isset`/`empty` uses strict `zval_get_long_ex`, separately from
quiet and ordinary R/W offset conversion. Infinity and finite out-of-range floats
emit a range Warning then precision Deprecated before testing the converted
index. NaN retains its existing pair, fitting fractional floats retain only the
precision Deprecated, and fitting integral floats stay silent. The
[strict-float review](../../coverage/semantics/string-offset-strict-float-review.json)
accepts ordinary no-handler execution: two separate source agreements, author
AL104 (43 derived controls) and independent AL60 retain their actual cuts.
The shared numeric kernel, quiet/R/W rules and wider handler boundaries stay unchanged.

Module38 separately handles intermediate string `unset` without an error handler.
After final-key expression effects, it reads the live inner key. Integer and
leading-integer text keys give `Cannot use string offset as an array` without
checking bounds; UNSET suppresses the usual trailing-text Warning. Invalid
admitted keys instead give `Cannot unset string offsets`, cancelling the second
Error. Null/bool/float keys retain one cast Warning before the nested Error;
the converted index is unused. A final delayed CV is never read after failure.

This admission requires valid non-NUL raw or authenticated carrier bytes.
Object and nonempty-array keys, malformed inputs, NUL and handler paths retain
their fences.
The [nested-unset review](../../coverage/semantics/string-offset-nested-unset-review.json)
separates four original-source agreements, author AL72 (31 derived controls),
independent AL76 and the preserved fixture failure.

Terminal string unset has a separate dispatch after its R-key read: valid
non-NUL interned and authenticated REQUEST bases produce `Cannot unset string
offsets` without converting the key. The new carrier arm requires a known
bounded primitive or valid non-NUL string key and no registered error handler.
A missing key CV still gives its ordinary Warning before the Error.

`$unset_terminal_nonarray` is called only by `$unset_final` after that read.
The shared `$unset_nonarray` remains literal for ArrayAccess callers whose
current RESULT can differ from the captured offset. No owning-key or wider
callback/lifetime admission is added. The
[terminal-unset review](../../coverage/semantics/string-offset-terminal-unset-review.json)
retains one original, author AL93 (34 derived controls) and independent AL53;
preliminary source/AL87/89 cuts stay separate from final acceptance.

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
An initially wrapped array CV captures its dereferenced CELL payload
slot before conversion. The existing ARRAY marker owns only builder and old table;
its REFERENCE locator adds no CELL owner. Completion reads that captured slot,
ignoring current CV rebinding, and inserts DIRECT PARRAY. The allocated marked
CELL has no coercion/backing records or CELL debt, and both CELL and bounded
payload must survive logical pruning even before any debt exists. Source
metadata remains valid when a locator retires; readiness then refuses explicitly.
An outside alias keeps the borrowed slot alive, while deletion/throw requires
another ordinary table owner to keep a new HARRAY deficit positive. Reciprocal
slot retargeting cancels old/new table biases before ordinary COW and teardown.
The [wrapped array-CV review](../../coverage/semantics/array-literal-float-wrapped-array-cv-review.json)
checks rebinding-only, payload cycles, deletion and supplied throw.
The [wrapped mixed-CV review](../../coverage/semantics/array-literal-float-wrapped-mixed-cv-review.json)
adds initial wrapped null/bool/int/float values and primitive completion. The
existing scalar marker uses BORROWED ROOT for the captured slot and owns only the
builder; ARRAY capture still owns its old table. Both read the captured live slot
rather than the rebound name. Scalar-to-array completion owes one table owner;
array-to-scalar completion retains the acquired table count. Reciprocal changes
cancel these biases, including after entry deletion or supplied throw. A separate
ordinary table owner keeps entry-independent debt positive. The
[typed captured-CV review](../../coverage/semantics/array-literal-float-typed-wrapped-mixed-cv-review.json)
adds existing ordinary validated property sources accepting the captured primitive
or bounded array. Every source object must survive the same logical pruning as
the CELL and payload, even before debt. Fresh public int|array slots preserve
weak integer coercion and invalid-string rejection; removing the final property
source leaves an outside alias usable without its constraint. Direct strings,
wider source kinds and unsafe lifetimes remain Unsupported; global ordinary/A19
classifiers, task ownership and count/prune algorithms stay exact.
Ordinary no-argument named functions may supply an owning ARRAY return temporary.
The checked value occurrence must resolve without fallback to an active by-value
function. Its KNOWN table stays frozen while the handler mutates or removes
producer globals, even when a global originally named a reference. Existing
mutable/nonpool and object-free readiness bounds remain; no table or CELL count
bias is introduced. Entry deletion and supplied throw release the owning table
normally. The [return-value review](../../coverage/semantics/array-literal-float-return-array-value-review.json)
keeps these sources separate from borrowed CV slots; by-reference returns,
arguments and wider call producers remain Unsupported on this warning path.
NULL literal-key conversion separately backs up an ordinary unmarked value CV
before dispatch. It restores that same live slot before inserting its frozen
value under the empty-string key, or before propagating a supplied throw. A
shared NULL key/value CV therefore loses the handler's key write too; a distinct
key keeps its write. Scalar or mutable nonpool edge-free/debt-free DIRECT-leaf
array payloads use the existing validators. ARRAY capture keeps both acquisition
and backup owners; the overwritten callback table retires normally. The
[NULL-key review](../../coverage/semantics/array-literal-null-key-warning-review.json)
checks restoration, independent snapshots, COW, deletion and throw. Rebound or unset ordinary slots, typed slots, direct string/object values and
wider graphs remain Unsupported on this continuation; float-key rules stay
unchanged.
An initially untyped reference-wrapped value CV captures the old dereferenced
CELL payload. A surviving alias keeps that marked slot live, and NULL conversion
restores its snapshot even when the original name now refers to another CELL.
The latter binding stays intact. The existing two ARRAY snapshot owners and
DIRECT insertion/throw reset remain unchanged. The
[wrapped NULL-key review](../../coverage/semantics/array-literal-null-key-wrapped-cv-review.json)
checks primitive and array reset, independent snapshots/COW, deletion and throw.
Property/coercion/backing records, CELL debt and wider payloads remain excluded;
source metadata can remain valid after a locator retires while readiness refuses.
Captured typed slots use existing ordinary property-source validation in the
same logical live set as their current payload. Before reset, every current
constraint must also accept the saved snapshot. This check uses allocated
snapshot owners across popped-marker throw cleanup, after current source-object
liveness is established. Fresh public `int|array` slots cover scalar-to-array
reset, weak numeric-string-to-int writes, rejection, final-source detach and
restoration before catch. A transient public `int` source accepts current44 but
makes readiness refuse the old ARRAY; detach restores readiness before the
native callback returns. This is an explicit Unsupported boundary of this
continuation. No generic typed-write or owner
rule changes; see the
[typed NULL-key review](../../coverage/semantics/array-literal-null-key-typed-wrapped-cv-review.json).
Ordinary named calls with no arguments and a by-value function target can also
supply an owning ARRAY value at a NULL key. The active compiled name has no
fallback; mutable nonpool edge-free/debt-free returned tables use the existing
payload bound, with no object reachable from the value or builder. The VAR
acquisition plus NULL backup gives two pending table owners. Normal completion
keeps producer writes and inserts a frozen DIRECT value under `""`; throw removes
both owners without inserting, retiring an otherwise unowned returned table
and builder before catch.
This path has no captured CV to reset and introduces no literal bias. See the
[NULL return-value review](../../coverage/semantics/array-literal-null-key-return-array-value-review.json).
By-reference returns, array-constructor TMPs, calls with arguments and other
call producers remain outside this continuation.
Runtime `NExprArray` values have a separate one-owner NULL-key continuation.
The checked occurrence must be nonconstant and its table mutable and nonpool;
the existing edge-free/debt-free payload and object-free reach bounds apply.
There is no VAR backup or CV writeback: handler seed writes and rebinding persist,
while the constructor's DIRECT child remains frozen under the empty-string key.
Normal insertion transfers the owning edge; supplied throw inserts nothing and
retires an otherwise unowned child table and builder before catch. Fresh integer
leaves cover evaluation once, marked scalar reads by value, COW and last-entry
deletion. Existing primitive/validated-byte leaf checks compose unchanged; pooled
constants, embedded owning leaves and wider producers remain outside this path.
See the [NULL array-TMP review](../../coverage/semantics/array-literal-null-key-array-tmp-review.json).
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
and multiline regressions. Wider nested string unset keys/owners and callback
behavior remain pending.

The reviewed source write activation passed the 664-case source campaign plus
23 outcome negatives and 103 independent additional write sources. One temporary
literal lvalue remains explicitly unsupported by the compiler; it is not counted
as a modeled PHP error. The helper matrix and ownership/origin campaigns were
repeated against the same implementation closure.
