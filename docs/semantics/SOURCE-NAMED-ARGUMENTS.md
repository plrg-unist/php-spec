# Named arguments for direct user functions

This checkpoint binds positional and named sends to declared user functions, including typed/reference parameters, omitted defaults and variadic tails. Argument expressions execute in source order. Fixed names select case-sensitive parameter destinations; extra names retain insertion order in a variadic tail. Unknown and duplicate names fail at SEND. Literal CV reads occur after destination validation; computed variable and dimension fetches occur before it. Writable acquisition can create storage before a failed send, but reference promotion occurs only after the destination succeeds. Deferred literal-CV sends use their compiled emission line, which can differ from the original variable source line; the same correction applies to positional deferred sends. Actual argument-root metadata is checked against the source compiler projection.

Selected error handlers now receive the `Only variables should be passed by
reference` Notice for a bounded named call-result send. The selected ordinary
user function has an untyped fixed or variadic reference parameter; the argument
is a direct ordinary by-value user call without namespace fallback. It has no
arguments or uses the bounded
[completed CV argument](../../coverage/semantics/producer-cv-reference-notice-review.json)
route described in the reference-parameter contract. Both the selected function
and the producer have no attributes and are nongenerators.
Pending values and untyped reference payloads admit null/bool/int/float,
non-NUL interned strings, authenticated REQUEST strings at roots and scalar array
leaves, and live acyclic graphs through DIRECT child arrays
and ordinary scalar/array/object reference cells with quiet stdClass leaves,
plus quiet root `stdClass` values and
cells under the bounds below. String and array reference cells have no
parameter-backing metadata; see the
[string extension](../../coverage/semantics/interned-reference-notice-review.json). The real
next `NAMED_ARGS` task owns the newly stored private reference before dispatch,
alongside previously sent references. Handler rebinding cannot redirect those
cells. Normal/false handling continues later arguments once; a throw cancels the
call before later sends, body entry or caller assignment. A reference return can
carry the original sent cell into an ordinary caller CV. Notice validation binds
the exact argument destination, source prefix, emission line, severity and event;
duplicate destinations still fail after their argument effects and before private
reference creation or handler entry. Validation does not reconstruct earlier
values or add a historical owner. Other producers,
property sources beneath object fields, raw/NUL strings, wider objects, constrained sources, wider positional/unpacked
sends and callback lifetimes remain partial. See the
[focused review](../../coverage/semantics/named-reference-send-notice-review.json).

The [multiple-CV producer review](../../coverage/semantics/multi-cv-producer-reference-notice-review.json)
also covers named consumers with a prior sent reference. Producers may use
multiple literal ordinary CV actuals, including duplicates, with matching required
fixed untyped formals and an untyped return. The last inner CV's compiled line
preserves finalized/deferred Notice locations; qualification does not look up
former actual names. COW and current prior-prefix writes retain their real owners.

The [multiple-CV array-return review](../../coverage/semantics/multi-cv-array-return-producer-reference-notice-review.json)
also admits a raw canonical `array` return with the same required untyped vector.
Named prior references retain current handler writes; return verification and
formal retirement precede private-array COW, later scalar replacement and cleanup.
The return declaration does not constrain the fresh private reference cell.

The [multiple-CV scalar-return review](../../coverage/semantics/multi-cv-scalar-return-producer-reference-notice-review.json)
extends that same required untyped vector to canonical `int`, `float`, `bool` and
`string` returns. Actual weak conversion and formal retirement preserve captured
snapshots after caller unbinding. Named prior references follow handler writes;
the fresh private cell may later hold an array or a separately written string.
Existing authenticated non-NUL INTERNED/REQUEST bounds and wider-header/source
limits remain in force.
The [multiple-CV nullable-array review](../../coverage/semantics/multi-cv-nullable-array-return-producer-reference-notice-review.json)
also admits raw `?array` with exact normalized `[array, null]` and the same required
untyped vector. Named duplicate-CV ARRAY snapshots distinguish returned5,
current13, handler17 and private23, while the prior prefix follows29 then31 and
the private reference may later hold41. Invalid return-TypeError precedes Notice,
consumer entry and assignment; explicit exception release preserves cleanup.
At the REF52 cut, ordered-union multi returns and typed multi formals remained partial.

The [multiple-CV ordered-union review](../../coverage/semantics/multi-cv-union-array-return-producer-reference-notice-review.json)
adds explicit `array|null` and `null|array` headers with exact raw/normalized
member order. Named duplicate-CV snapshots and current prefix writes retain the
existing COW and private-cell lifetime rules. Invalid int return priority remains
before Notice, consumer entry and assignment. At the REF53 cut, nullable scalar and wider union multi returns and typed multi
formals remained partial.

The [multiple-CV nullable-scalar review](../../coverage/semantics/multi-cv-nullable-scalar-return-producer-reference-notice-review.json)
adds canonical `?int`, `?float`, `?bool` and `?string` with exact `[scalar, null]`
and the same required untyped vector. Named weak INT/BOOL conversions preserve
original strings and current prefix writes; private arrays or byte COW retain
separate snapshots and no inherited return constraint. Strict INT return of a
captured REQUEST string resolves the real deferred CV then raises TypeError
before Notice, consumer entry and assignment. At the REF54 cut, explicit ordered scalar/null and wider union multi returns
and typed multi formals remained partial.

The [multiple-CV scalar/null-union review](../../coverage/semantics/multi-cv-union-scalar-return-producer-reference-notice-review.json)
adds explicit `int`/`float`/`bool`/`string` with NULL in either source order,
requiring exactly two distinct raw members matched pointwise to normalized types.
Named duplicate-CV snapshots, current prefix writes, private arrays or byte COW,
and strict return-TypeError priority keep their existing guards and lifetimes.
At the REF55 cut, wider union multi returns and typed multi formals remained partial.


The [multiple-CV ARRAY-formal review](../../coverage/semantics/multi-cv-array-formal-producer-reference-notice-review.json)
adds matching fixed required canonical ARRAY parameters alongside untyped ones.
Named duplicate-CV BYVAL/BYREF reception preserves old snapshots and current prefix
writes, followed by private COW and different-type replacement without a persistent
parameter constraint. An invalid second ARRAY argument raises TypeError before
the producer body, Notice, consumer and assignment. Cleanup preserves the real
literal POOLS owner while retiring fresh COW and exception owners. At the REF56 cut,
wider formal types/defaults/variadics/attributes and lifetimes remained partial.


The [multiple-CV scalar-formal review](../../coverage/semantics/multi-cv-scalar-formal-producer-reference-notice-review.json)
adds pointwise canonical int/float/bool/string parameters. A duplicate STRING/INT
actual preserves the first REQUEST snapshot while the second ordinary reference
receive changes the caller cell; body/handler writes and private raw X7 COW remain
separate. Strict STRING rejects an INT after a valid ARRAY receive before body,
Notice, consumer or assignment. Existing reception, frame retirement, current
prefix aliases, COW and literal POOLS ownership remain unchanged. At the REF57
cut, nullable/union and wider formals/defaults/variadics/attributes and lifetimes
remained partial.

The [multiple-CV nullable-formal review](../../coverage/semantics/multi-cv-nullable-formal-producer-reference-notice-review.json)
adds canonical nullable ARRAY/int/float/bool/string parameters through exact
pointwise raw nullable nodes, normalized `[kind, null]` and BYREF proof. NULL
passes reception unchanged. Duplicate BOOL/INT actuals preserve the first
snapshot while the second ordinary reference receive changes the caller cell;
body writes add no persistent parameter constraint. Strict NULL-first reception
precedes an invalid ARRAY-second TypeError, body, Notice and assignment. Existing
return, frame-retirement, current-prefix and ownership guards remain. Singleton
scalar/nullable formals, wider unions/defaults/variadics/attributes and lifetimes
remain partial at this cut; Owned-NUL remains held.

The [singleton formal review](../../coverage/semantics/singleton-cv-typed-formal-producer-reference-notice-review.json)
adds exactly one literal ordinary CV actual with canonical scalar or nullable
ARRAY/scalar formals through the same raw/normalized/BYREF proof. Old untyped
and singleton ARRAY arms remain literal. A named nullable ARRAY producer keeps
its outside copy through producer/private COW while prior prefix references
follow current handler writes. Strict INT rejects numeric REQUEST text before
body, Notice or assignment. Return-header and ownership bounds remain;
nullable scalar/ordered scalar-null singleton returns, formal unions and wider
signatures/lifetimes remain partial at this cut.

The singleton [nullable-return review](../../coverage/semantics/singleton-cv-nullable-scalar-return-producer-reference-notice-review.json)
adds canonical nullable scalar and ordered scalar|null/null|scalar return headers.
Named null|string results preserve REQUEST snapshots and private byte COW after
the producer frame retires; strict bool|null return rejection precedes Notice,
consumer and assignment. Raw/normalized authority, existing formal and ownership
bounds remain. Formal unions and wider signatures/lifetimes remain partial.

The [root REQUEST-string review](../../coverage/semantics/request-string-return-producer-cv-reference-notice-review.json)
checks preserved returned/prior-sent snapshots, independent byte writes and
producer array-formal/table retirement. The later
[array-leaf review](../../coverage/semantics/request-string-array-leaf-reference-notice-review.json)
adds authenticated REQUEST DIRECT/ordinary-ALIAS scalar leaves with physical
shared-child counts, current-leaf retargeting, COW and staged retirement. Object
field bounds are extended by the
[object-field review](../../coverage/semantics/request-string-object-field-reference-notice-review.json):
existing quiet `stdClass` targets now admit authenticated non-NUL REQUEST DIRECT
fields, preserving shared-object writes, scalar snapshots, object retargeting and
independent WeakReference retirement. The later
[scalar ALIAS-field review](../../coverage/semantics/stdclass-alias-scalar-field-reference-notice-review.json)
admits ordinary live marked childless scalar cells, counts each physical field
edge, and checks independent property rebinding, shared-cell writes and
WeakReference retirement. The
[ALIAS-array-field review](../../coverage/semantics/stdclass-alias-array-field-reference-notice-review.json)
adds finite object-free array payloads in ordinary cells, with mutable nonpool
roots, current payload edges, retargeting, nested COW and cell/table retirement.
At that cut, owning object fields remained partial; pool/immutable roots, cycles
and existing cell/header/source/backing guards retain their bounds.
The [DIRECT-array-field review](../../coverage/semantics/stdclass-direct-array-field-reference-notice-review.json)
adds physical per-field array edges, independent field COW, repeated-edge throw
cleanup and exported property-cell survival after object retirement under those
same graph/header bounds. The later
[DIRECT-object-field review](../../coverage/semantics/stdclass-direct-object-field-reference-notice-review.json)
adds finite acyclic quiet `stdClass` paths with path-local object ancestors.
Shared siblings and repeated field edges retain their physical owners; retargeting,
exported child references and last-owner cleanup preserve object identity and
WeakReference notifications. Self and ancestor cycles remain Unsupported. Array
fields stay object-free. The later
[ALIAS-object-field review](../../coverage/semantics/stdclass-alias-object-field-reference-notice-review.json)
admits ordinary live marked object-valued cells with one current payload edge,
retaining every cell/source/history guard and the same object ancestor path.
Property rebinding moves one field edge; an object payload can retire while its
scalar cell aliases remain. Repeated-cell throw cleanup, exports and WeakReference
notifications preserve actual owners. The
[mixed-field review](../../coverage/semantics/mixed-object-array-field-reference-notice-review.json)
extends these paths across finite mutable nonpool arrays and quiet objects, with
separate ancestor lists that cross both kinds of edges. Table COW, shared objects,
exported cells and last-owner retirement retain their real edges. Alternating
cycles and property-source validation below an object ancestor remain excluded;
the earlier root-array source route and existing header/GC/Owned-NUL guards stay
unchanged. Wider producers, backing and lifetime contexts remain partial.

The [array-cell review](../../coverage/semantics/alias-child-reference-notice-review.json)
records real private-cell, table and CELL payload edges. A shared cell owns its
current array once; root COW preserves repeated cell identity, while a singleton
unwraps into a DIRECT child. Deep COW preserves outside copies, and throw cleanup
releases only last owners. The ancestor path crosses DIRECT and ALIAS edges to
allow sibling sharing and reject cycles. Cell and child-header history bounds
remain explicit in the [reference-parameter contract](SOURCE-REFERENCE-PARAMETERS.md).
Quiet stdClass ALIAS leaves also retain one current object edge per cell;
handler retargeting reaches shared views, while singleton COW creates a DIRECT
entry whose later replacement leaves the old cell intact. Every array ancestor,
including the root, has ordinary mutable/nonpool headers without retained/debt
or native units on this object-leaf route. The
[ALIAS-object review](../../coverage/semantics/alias-object-leaf-reference-notice-review.json)
records named continuation, scalar retargeting and public resumption separately
from positional singleton and throw cuts. Wider callback lifetimes remain partial.
Earlier
[DIRECT-graph](../../coverage/semantics/direct-child-reference-notice-review.json),
[flat-array](../../coverage/semantics/array-reference-notice-review.json) and
[scalar-reference](../../coverage/semantics/alias-array-reference-notice-review.json)
reviews keep their original cuts.

Quiet root `stdClass` payloads preserve object identity through handler property
writes, source replacement and reference return. Rebinding the returned cell
leaves outside object aliases intact. A supplied throw releases the actual
private cell and last object owner before catch, notifying WeakReference without
user destruction or collection. The local canonical property record has only
DIRECT null/bool/int/float or authenticated non-NUL string fields, with non-NUL
startup names; normal dynamic
MATERIALIZED records need no cached property table. Targets have no owning child,
cached table, called/freeing state, native unit or WeakMap key registration, and
the collector is inactive. REFERENCE payloads additionally expose their real
CELL-to-object edge and exclude property/coercion/backing/container metadata,
debt/retained/release histories and native cell units. ALIAS-object entries,
USER instances and broader lifetimes remain partial. See the
[stdClass review](../../coverage/semantics/stdclass-reference-notice-review.json).

DIRECT quiet stdClass leaves also cross the finite array graph. Copying an object
entry adds another physical object edge and preserves object identity, so
property writes remain visible through outside copies. A handler's source-table
replacement leaves the pending old table fixed. The actual private-cell/table
chain releases a sole object before catch on supplied throw.

On this route every array ancestor, including the old root, must be allocated,
mutable, nonpool and free of literal retained/debt records and native units.
DIRECT and ALIAS-array ancestors both participate; repeated object IDs and
sibling table sharing remain valid, while existing array-path cycle checks stay
in force. The quiet object bound above is unchanged. Old scalar/array routes
retain their root history, and ALIAS-object entries remain excluded. See the
[DIRECT-leaf review](../../coverage/semantics/direct-object-leaf-reference-notice-review.json).

The same bounded completed-producer route now uses the inner CV's compiled line
for default Notices without a selected handler and for duplicate-name Errors.
Producer effects finish before a duplicate is rejected; that failure still
precedes private-reference creation, Notice emission and caller assignment.
The call instruction keeps its own line. Other SEND contexts retain their prior
line path; see the [default-line review](../../coverage/semantics/default-reference-line-review.json).

Pending positional slots distinguish an absent hole from a supplied PHP null. Entering the callee preserves the effective positional extent, including positional tail arguments, separately from ordered extra names. Interior fixed holes below that extent are filled before ordinary parameter type receives. Deferred hole values are cached before coercion, and omitted reference parameters receive independent cells. Trailing defaults use the existing receive schedule. Failed preflight has a callee trace whose remaining absent slots render as NULL; that rendering does not fill their storage.

Fixed and variadic type checks remain sequential and can change a shared alias before a later argument fails. Extra named SEND diagnostics use fixed_count+1; named-tail type checks use the constant index max(fixed_count, effective positional ARGC)+1. Collected arrays and the sent tail operand slots retain owning references through normal and abrupt cleanup. Trace arguments preserve ordered extra names. Suppression scopes, caller frames and returned-cell ownership follow the earlier accepted contracts.

Public resume checks bind the selected call, original source argument prefix, slot destinations, ordered names, operand modes and stage metadata. Preflight may safely revisit supplied slots, but cannot skip an unfilled hole or enter ordinary typed receives early. Pending default binding requires its final continuation and exact source origin. Partial variadic arrays bind cursor, keys and next-index metadata. Arbitrary consistent runtime values and aliases remain valid; the guard does not reconstruct execution history.

Direct builtin named source handling is the next required compiler prerequisite; builtin name inventories do not establish builtin body execution. Array/Traversable unpack, first-class callable and closure integration, object-dependent defaults and exception handling remain separate core obligations. Future object default side effects also require the pinned distinction between hole-preflight caching and trailing RECV_INIT caching. This checkpoint does not close the complete calls family.

The [author evidence](../../coverage/semantics/named-runtime.json) binds70 source cases,55 compiler phases plus6 boundaries/129 projections,44 resume controls/935 assertions,12 adjacent runtime cases and2 dense states/373 assertions. The [independent review](../../coverage/semantics/named-review.json) adds5 source profiles,4 dense states/731 assertions and two complete959 compatibility bridges at seven cuts; only empty NAMED context fields are removed. Counts overlap. Semantic/source/protocol gates retain968/55cd; final968/ab389 changes only the regression test selection, preserving967 files and all modes. The [compiler contract](NAMED-ARGUMENT-COMPILER.md) records the source-line repair and retained earlier failures.
