# Reference wrappers and dimension fetching

Reference acquisition records wrapper identity separately from the backing cell's
value and ownership count. A wrapper survives writes and removal of its last
alias while the variable remains bound. Removing the variable and creating an
ordinary binding allocates a fresh, unmarked cell. Copying a reference value does
not mark the destination; array copy and union retain their existing singleton
reference unwrapping rules. Ordinary writable-name fetching initializes a missing
slot without creating a wrapper; only reference-source acquisition marks it.
This distinction also applies to computed variable names.

Generic dimension fetching through a wrapper containing `false` creates an array
without the false-to-array deprecation. An intermediate unset through that wrapper
also skips the deprecation. Final dimension assignment and final unset use their
own Zend paths and retain the warning. The distinction applies to root variables
and aliased array entries, including singleton wrappers.

`REFCELLS` records stable cell IDs. It adds no heap edges or roots and cannot keep
an unreachable allocation alive. Dead markers are inert because IDs are never
recycled. Constant compilation rejects reference markers in isolated compiler
memory; installing a valid unit preserves runtime markers.

`LITERALREFRETAINED` records acquired `ADD_ARRAY_ELEMENT` owners left on old
wrappers when a lossy-float key handler retargets the element CV. Each unmatched
occurrence contributes one request root, including repeated IDs, through normal
and abrupt cleanup. Stable same-cell insertion transfers that owner into its array alias.

`LITERALREFDEBTS` records omitted owners on different reference cells inserted
after that callback. Logical aliases remain intact; effective owner counts and
pruning counters subtract the debt multiplicity. Retaining an indebted cell first
cancels one debt, and owing a retained cell first cancels one positive owner.
Thus inverse retargeting restores ordinary ownership without spurious GC roots.
Primitive acquired and new cells may carry ordinary live instance-property
sources; their metadata adds no owner. Singleton COW strips the
copied entry's wrapper even when it has type sources, while original aliases and
shared copies retain typed rejection/coercion. For debt-bearing cells, source
objects and their actual property aliases must survive logical pruning. The
[typed-source review](../../coverage/semantics/array-literal-float-ref-types-review.json)
checks both typed sides and multiple live sources. Untyped CELL payloads may also
be mutable nonpool flat arrays of DIRECT null/bool/int/float values or validated
byte strings, plus the bounded primitive reference entries described below.
The CELL keeps one child-table edge; its debt never subtracts from
HARRAY owners. Copying a singleton reference entry unwraps its wrapper, then
ordinary child COW separates array values.
Changing the child table leaves the same CELL debt in place. Old-array completion
also admits an ordinary-scalar DIRECT value. Its acquired count cancels an existing
debt first; otherwise the wrapper and its child remain owned for the request.
Repeated unmatched occurrences preserve multiplicity through normal and throwing
callbacks. The active builder cannot be either payload. The
[array-to-scalar review](../../coverage/semantics/array-literal-float-ref-array-scalar-review.json)
checks child COW after ordinary names disappear and debt cancellation. The
[flat-array review](../../coverage/semantics/array-literal-float-ref-arrays-review.json)
checks these counts through stable insertion, deletion, throw and inverse cleanup.
Debt cells must keep positive effective counts. Array-valued type sources,
pooled/immutable arrays, nesting or array leaves outside the bound below,
object-valued or indebted embedded leaves, other owning values, static/hooked/queued or retired sources,
coercion/backing records, active collection, effective-zero retirement and
outstanding debt at request end are explicit Unsupported before pruning. Isolated
compiler images reject both runtime fields. The [deficit review](../../coverage/semantics/array-literal-float-ref-deficit-review.json)
keeps fresh balanced sources separate from the earlier
[positive-owner slice](../../coverage/semantics/array-literal-float-ref-key-warning-review.json).

Ordinary by-value array CVs use separate `LITERALARRAYRETAINED` and
`LITERALARRAYDEBTS` fields for HARRAY counts. Their saved continuation owns the
pre-conversion table, rather than its original CV cell. Inserting a different live
table preserves the old count and omits one new-table owner; inverse retargeting
cancels both, while same-table insertion adds no bias. The ordinary by-value plan
requires an unmarked CV and a mutable nonpool flat table with these
bounded DIRECT or ALIAS entries. Combined CELL/table
debt safety uses logical pruning before subtracting either count bias. Positive
table targets keep their admitted leaf edges; table debt does not subtract leaf
owners. Deletion/throw deficits,
restored COW and retired original CV cells are checked in the
[ordinary array-CV ledger](../../coverage/semantics/array-literal-float-array-cv-review.json).
Mixed completion also admits ordinary null/bool/int/float values. An initially
scalar CV owns no table; a new array omits one owner or cancels an earlier retained
count. An array CV that becomes scalar preserves its acquired table
count, cancelling debt before retaining an unmatched owner. The two initial plans
stay disjoint, and captured runtime-array temporaries incur no debt. The
[mixed-CV ledger](../../coverage/semantics/array-literal-float-mixed-cv-review.json)
checks both inverse cycles, deletion and supplied-throw cleanup before balanced COW.
An initially ordinary array CV can become an untyped reference during its
callback. Zend inserts that live wrapper even for a by-value item, retaining the
acquired HARRAY count and recording a missing CELL owner. A reciprocal reference
item may complete from a fresh ordinary array CV, retaining its acquired CELL
count and owing a table owner. Existing retain/owe operations cancel both
families through unchanged graph construction and count/prune algorithms. The
[CV/reference cycle ledger](../../coverage/semantics/array-literal-float-cv-ref-cycle-review.json)
distinguishes physical singleton unwrapping, restored shared aliases and child
COW through deletion and supplied throw. These new completion arms require
untyped outer cells without coercion/backing records; direct strings and the
existing unsafe lifetime bounds remain excluded.
A separate initial wrapped-array plan keeps a nonowning REFERENCE locator for
the CELL payload acquired before float conversion. Its ARRAY marker still owns
only the builder and acquired HARRAY. Rebinding the CV cannot change this slot;
callback writes through an outside alias determine the DIRECT array insertion.
The captured CELL has no coercion/backing records or CELL debt, and
must be live after logical pruning together with its bounded payload. Metadata
can authenticate a retired locator without permitting a stale read. The
[wrapped array-CV ledger](../../coverage/semantics/array-literal-float-wrapped-array-cv-review.json)
checks unchanged-payload transfer, reciprocal table-bias cancellation, direct-copy
COW, deletion and supplied throw. Multiple aliases to one CELL add no payload-table
owners: an independent ordinary table CV keeps an entry-independent HARRAY deficit
positive. The
[wrapped mixed-CV ledger](../../coverage/semantics/array-literal-float-wrapped-mixed-cv-review.json)
adds initial primitive slots and DIRECT null/bool/int/float completion. BORROWED
ROOT in the scalar marker adds no CELL or payload-table root; array capture keeps
only its acquired table owner. Primitive-to-array debt and array-to-primitive
retention cancel through reciprocal captured-slot writes. Later alias writes leave
DIRECT primitive snapshots fixed, and balanced tables regain ordinary COW.
The [typed captured-CV ledger](../../coverage/semantics/array-literal-float-typed-wrapped-mixed-cv-review.json)
adds existing valid ordinary property sources accepting the captured payload.
Their metadata adds no owner; each actual property still owns a CELL edge, and
all source objects must survive the same logical pruning as CELL/payload. Fresh
int|array rejection/coercion, safe final-property detach, independent table owners
and DIRECT primitive snapshots distinguish this from reference-element insertion.
Direct strings, wider source kinds and unsafe lifetimes stay excluded.
An ordinary named function returning an ARRAY by value supplies an owning KNOWN
operand, including when its source global is a reference. The return has already
dereferenced the source; subsequent handler writes or global rebinding cannot
change that table. Existing task/frame roots transfer this owner into a DIRECT
literal entry without debt or retention. The
[return-value ledger](../../coverage/semantics/array-literal-float-return-array-value-review.json)
checks frozen tables, COW and last-owner deletion/throw cleanup. Only a checked
no-argument call with no fallback and a by-value signature enters this new arm;
by-reference returns retain their separate lifetime requirements.
NULL-key literal conversion has its own value-reset continuation. The captured
ordinary CV index is nonowning and must still be the same live unmarked slot,
without property/coercion/backing records or CELL debt. For ARRAY values the
marker/frame owns two old-table edges, one acquired insertion value and one
backup. Normal completion moves these into the restored CV and DIRECT entry;
throw restores the CV and releases the insertion/builder owners before catch.
No literal debt, retention or generic count/prune rule changes. The
[NULL-key ledger](../../coverage/semantics/array-literal-null-key-warning-review.json)
separates restored old tables, retired callback tables and independent snapshots.
Initially wrapped value CVs use a REFERENCE locator in that same NULL marker.
Zend captured the old CELL payload before dispatch; restoration resets it while
leaving a callback's new source-name binding unchanged. The marked untyped CELL
and bounded current payload must survive logical pruning, even without debt,
with no property/coercion/backing records or CELL debt. Its outside alias owns
the only required CELL edge; the marker still adds no CELL root. The
[wrapped NULL-key ledger](../../coverage/semantics/array-literal-null-key-wrapped-cv-review.json)
checks actual captured-versus-rebound identities and restore-before-catch cleanup.
Typed captured payloads compose the existing ordinary property-source checks;
source objects and the current bounded payload must be logically live together.
Readiness validates the saved payload against every current source and reports
Unsupported if a newly restrictive source rejects it. The
snapshot remains an allocated owning argument after a throw pops the marker.
Property aliases add CELL edges, not extra payload-table owners; the marker
continues to own no CELL. Existing coercion/rejection and source detach do the
typed writes. Fresh union/int source controls and restore-before-catch checks are
in the [typed NULL-key ledger](../../coverage/semantics/array-literal-null-key-typed-wrapped-cv-review.json).
A named by-value function called without arguments supplies an owning returned
VAR, including when its body returns a global reference payload by value. NULL
conversion adds one backup, so its separate marker holds the returned HARRAY
twice without a source CELL owner or CV reset. Normal insertion consumes one
owner and transfers the other to a DIRECT entry; throw discards both and lets
the public driver retire the sole value/builder before catch. Snapshot allocation
is enough while that marker is popped, without requiring a transient graph root.
Existing call authentication, bounded payload/object-free checks and generic
count/prune rules stay in use. See the
[NULL return-value ledger](../../coverage/semantics/array-literal-null-key-return-array-value-review.json).
An inline runtime array constructor instead has one owning TMP edge, with no
NULL backup and no captured CELL owner. Its distinct marker transfers that edge
to a DIRECT entry or drops it during throw cleanup. Reading a scalar reference
inside the constructor captures its value; later source rebinding stays visible
without changing the saved child. Source/nonconstant and existing bounded-payload
checks keep this path separate from pooled constants and the two-owner returned
VAR. Popped-marker allocation is sufficient for identity discard before normal
pruning; no bias or count/prune algorithm changes. See the
[NULL array-TMP ledger](../../coverage/semantics/array-literal-null-key-array-tmp-review.json).
Pooled constant array literals instead keep their permanent pool owner plus one
pending value edge. Exact compiled-read identity authenticates the value occurrence;
normal insertion transfers the pending edge to DIRECT, while throw drops it and
preserves the pool. No NULL backup, producer CELL root or CV reset is needed.
The initial flat slice has DIRECT primitive/validated-byte leaves. Repeated calls,
empty-array COW, deletion and supplied throw are recorded in the
[constant NULL-key ledger](../../coverage/semantics/array-literal-null-key-constant-array-review.json).
Nested DIRECT constant subtrees validate each allocated, debt-free child with
the existing primitive/byte leaf checks. Per-path ancestors reject cycles and
builder backedges while allowing shared siblings. Root multiplicity does not
multiply child edges; real table clones add physical edges instead. Exported
child facts can add permanent roots, but a separate child pool root is not
required. Repeated handler-time COW, deep deletion, empty descendants and throw
checks are in the
[nested constant ledger](../../coverage/semantics/array-literal-null-key-constant-subtree-review.json).
String leaves use canonical bytes or existing valid carriers; they add no modeled
heap edges or user destructors. Ordinary string-offset writes preserve independent
snapshots while table/CELL aliases share bytes. Singleton reference entries
unwrap before child/string COW; balanced copies retain shared ALIAS entries. The
[string-leaf ledger](../../coverage/semantics/array-literal-float-string-leaf-review.json)
checks these paths, deletion and supplied throws. Direct string CV/cell payloads
remain Unsupported; no new string identity or ownership model is introduced.
Embedded ALIAS leaves must be live, marked, untyped cells holding null/bool/int/float
or validated byte strings, with no property/coercion/backing receipts or CELL debt. Child-table duplication preserves a
shared leaf ALIAS and unwraps a singleton leaf to DIRECT, independently of the
outer reference-wrapper unwrapping and HARRAY debt. The
[alias-leaf ledger](../../coverage/semantics/array-literal-float-alias-leaf-review.json)
separates these effects with sibling writes, deletion, supplied throw and inverse cleanup.
The [string-alias ledger](../../coverage/semantics/array-literal-float-string-alias-leaf-review.json)
adds shared/singleton string leaves: byte writes propagate through shared ALIAS
entries while unwrapped singleton leaves and earlier string snapshots remain independent.
A separate leaf-cell predicate leaves direct string CELL retargets Unsupported.
Embedded null/bool/int/float and validated byte-string leaves also admit
validated ordinary instance-property type sources. Table debt does not subtract
the property or table edges into a leaf. For debt-bearing payloads, every source
object must survive logical pruning;
leaf count positivity alone is insufficient. Shared copies enforce/coerce typed
writes. Explicit property unset removes its source before releasing the alias,
so a later singleton copy can unwrap without a constraint while the object stays
rooted. The [typed-leaf ledger](../../coverage/semantics/array-literal-float-typed-alias-leaf-review.json)
checks this distinction, two sources, deletion, supplied throw and inverse cleanup.
The [typed string-leaf ledger](../../coverage/semantics/array-literal-float-typed-string-alias-leaf-review.json)
adds shared byte writes, independent snapshots and weak scalar coercion while
preserving rejection and property-unset singleton copying. Global direct string
CELL admission stays unchanged. Object leaves and wider type-source
lifetimes remain Unsupported.
Embedded ALIAS leaves may also own one mutable nonpool child array of
DIRECT null/bool/int/float or validated byte strings. Each leaf is debt-free and
its child table has no HARRAY debt or outgoing owner edge. Validated ordinary
property sources may constrain that child array. For debt-bearing payloads,
the child and every source object must survive the same logical prune. This
finite shape preserves the positive-target lifetime proof
without changing count/prune algorithms. Child-table COW keeps shared leaf
references, while singleton leaves unwrap before copying their array payload.
Independent child snapshots and sibling writes distinguish all three ownership
levels in the [array-alias-leaf ledger](../../coverage/semantics/array-literal-float-array-alias-leaf-review.json).
The [typed array-leaf ledger](../../coverage/semantics/array-literal-float-typed-array-alias-leaf-review.json)
adds scalar rejection, shared nested writes and singleton child COW after explicit
property unset. Deeper owning children and indebted descendants remain Unsupported.
DIRECT entries may instead own bounded child arrays without an intervening leaf
CELL. The same mutable nonpool, edge-free, debt-free child bound applies; actual
child nodes must survive logical pruning. Duplicate entries retain duplicate
owner edges, so nested COW separates each occurrence and any independent
snapshot while outer table/wrapper debt remains unchanged. The
[direct child-leaf ledger](../../coverage/semantics/array-literal-float-direct-array-leaf-review.json)
checks both direct-child multiplicity and wrapper deletion/throw cleanup through
balanced inverse retargeting. Count/prune algorithms and global leaf gates stay exact.
Outer array-valued reference cells may carry validated ordinary property type
sources accepting the bounded table. Property aliases and literal entries own
the CELL; that CELL owns one payload-table edge. Type receipts add no owner.
For debt-bearing cells, the actual payload and every source object must survive
logical pruning. A physical count1 copy unwraps to a DIRECT array value, shedding
its constraint and separating child writes while the original remains typed;
balanced shared copies retain the ALIAS and its constraint. Final property unset
removes the source before its alias is released, with another alias keeping
physical counts positive until inverse balancing. The
[typed outer-array ledger](../../coverage/semantics/array-literal-float-typed-array-ref-review.json)
checks copy constraints, payload COW, initial typed-old capture, deletion and throw.

`tests/semantics/reference_wrappers.py` checks original source regressions,
copying and rebinding, budget resumption, ownership graphs, cycle collection and
compiler-pool isolation. The cycle check exercises the pure collection helper;
it does not admit a source-level `gc_collect_cycles` call. Prior mismatches remain
in the `coverage/semantics/false-reference-*` archives.

`tests/semantics/write_fetch.py` retains computed-write regressions and checks
plain versus existing reference cells through writes, nested unsets and resumption.

[Container276](SOURCE-CONTAINER-WRITES.md) stages those false/undefined writable
callbacks and genuine array-reference assignment. Captured source cells own once;
simple source CVs stay delayed until target acquisition. Raw typed DIM_OP array
backing records its source in `CONTAINERINITS`, adding no owner or ordinary type
permission. Pointer COW transports that backing; whole-cell stores clear it.
