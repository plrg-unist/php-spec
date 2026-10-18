# Destructuring key warnings

Module409 supplies the E_WARNING continuation for missing by-value fetches within
patterns with direct CV leaves. Recursive by-value patterns admit direct CV or literal RHS arrays;
recursive mixed value/reference patterns require a direct CV RHS. Implicit integer keys
and warning-free compiled constant keys are admitted. Literal strings retain their
authenticated interned-string carrier before key conversion. These patterns also
admit ordinary defined integer, boolean, exact-float and non-NUL string CV keys.
Computed key names, NUL CV strings and undefined/null key diagnostics remain
separate dependencies, along with wider RHS producers and target forms.

Module410 adds lossy float CV-key conversion for flat patterns with a direct CV RHS
and direct CV leaves. The initial plan captures the fitting
converted integer and original binary64 bits before E_DEPRECATED. A returning
handler in a wholly by-value pattern resumes lookup against the captured table:
an embedded reference supplies
its value after the callback, while a present null stays silent. A miss dispatches
the existing module409 warning before any target store. The two diagnostics may
select different handlers; a handler eligible only for E_WARNING still follows
the default deprecation. Following key CVs are read after the completed store.
The saved task owns the table, and source validation checks the stored conversion
without rereading the old key cell. A throwing handler cancels lookup, targets and
result delivery.

For a mixed pattern's by-value fetch, the saved task keeps the source reference
cell and separately protects its current table. After the handler returns, it
releases that table owner before lookup. If the table retires, the fetch silently
supplies null, even if the old key existed. Otherwise lookup reads the old table's
current embedded-reference value or enters module409's warning. A handler-created
copy can keep that table alive after source replacement; insertion can instead
force COW and leave only the temporary protection. Later reference fetches and
assignment-result delivery use the saved cell's live value, independently of a
rebound source CV. A saved null cell can create an array at the later reference
fetch. Throws cancel both owners.

A selected reference fetch first makes the initially array-valued saved cell's
table writable, separating when needed and unwrapping singleton references in
that copy, before the conversion callback.
After releasing protection, it binds into that selected table only when exactly
one owner remains. This owner may be a handler-created hold after source replacement
and CV rebinding. Zero owners or multiple remaining owners instead supply a fresh
null reference, even when the old table remains live with a present slot. Binding
replaces the target alias without writing through its previous reference. A missing
writable slot is silently created in the selected table; no missing-key warning is
emitted. Later fetches and the assignment result still resolve the saved source
cell. Throws cancel acquisition and binding. Initial nonarray writable sources,
nested/literal conversion and other key diagnostics remain separate dependencies.

For module409, the key stays a delayed variable operand until the missing fetch. The initial
plan checks its exact name, operand/compiler lines and warning-free conversion,
then freezes the converted integer or string bytes before dispatch. String
carriers must authenticate their bytes; their identities are immutable metadata
without heap ownership. Canonical numeric strings such as `"2"` select integer `2`,
while `"02"` stays a string and can select a different later reference target.
Callback writes, alias unsetting or name rebinding cannot redirect that fetch
or turn it into a successful lookup.
The saved continuation checks source compatibility, key kind and validity of
non-NUL string bytes without reading the key cell or carrier again; it cannot
reconstruct history.
Following keys are evaluated after the interrupted null target store, including
when an earlier target overwrites a key variable or a callback replaces the handler.

Module409's nested contexts authenticate each ancestor's source occurrence and
compiler location without rereading its key or parent table. After an ancestor
fetch, callbacks may change its key value, retire the old key cell or rebind its
name; historical type, carrier and bytes are not reconstructed. The current selected CV
still needs the quiet conversion above, while selected compiled keys retain their
exact constant equality. Earlier reference leaves preserve the inherited parent
key's compiler location for subsequent implicit fetches.

The by-value RHS is captured before the first item; a direct CV uses Zend's `QM_ASSIGN`.
The saved task owns that array through handler selection, the ordinary callback
frame and normal/throw cleanup. Callback insertion or replacement does not restart the
missing fetch: it still supplies null. Following items read the captured table
after the previous target store, so copied scalar entries and shared embedded
reference cells preserve their different behavior. Assignment-result delivery
returns the captured RHS value. A throwing handler cancels the pending target
store and later items, preserving callback writes and the supplied Throwable.

For wholly by-value patterns, each child task retains its array while outer
continuations retain their arrays. An outer missing fetch supplies null to the child,
whose reads silently deliver null. An inner missing fetch retains captured tables after callback
source rebinding. The first child fetch inherits the outer fetch's compiler line;
the next outer item inherits the child's final compiler location. During throw
cleanup outer continuations can keep child arrays alive after the inner warning
task is discarded; the tables retire after all owners disappear.
Shape recursion follows checked child subtrees, and context recursion removes one
item path. Replacing a shared row cell can change the returned root's row while
already captured row/child tasks continue to use the old tables.

Mixed roots use `MAKE_REF`; reference-bearing children use `FETCH_LIST_W` and
retain separate source cells. A by-value child still keeps its table snapshot.
Replacing a parent cell can release its old table without redirecting a saved
child. Replacing the child cell changes that child's later fetches. Unsetting or
rebinding an external CV leaves the saved cells authoritative; later outer items
and assignment-result delivery resolve the held root cell independently.
The interrupted fetch gives null before later reference acquisition. A null root
or child can therefore create arrays at later writable fetches, while by-value
null reads remain silent. COW separates copied scalar entries while preserving
shared embedded references, and earlier reference targets remain visible to the
callback. Once tasks and other owners disappear, cells and their tables retire.

Source occurrence, admitted RHS shape, remaining items, selected index,
constant/implicit key or CV-key occurrence, compiler line and captured array/cell allocation authenticate
the producer and saved resume. These checks establish source compatibility and
liveness; they do not reconstruct historical identity from a live CV. A mixed
resume does not require the cell to retain its original array. Prior reference
leaves retain the fetch line; prior by-value CV stores select the target line.
Each pattern's own reference demand selects its cell or by-value array operand;
saved child authority is independent of the current parent table or CV binding.
The generic error-handler machinery supplies mask eligibility, temporary handler
disabling, exact-false default reporting and restoration. A present null entry
does not enter the missing-key continuation.

Literal admission checks that the assignment's RHS matches its actual source
occurrence. A pattern with reference targets and a literal RHS is rejected at
compilation.
For a compiled literal root the captured table must match the RHS pool occurrence.
A runtime root instead requires its nonconstant compiler descriptor and a
mutable live table. This establishes source compatibility, without reconstructing
its historical identity or embedded references from live CVs. Rebinding
`q` in the handler leaves the literal's old reference cell available to later
fetches. Pooled arrays keep permanent owners; runtime literal arrays can have only
the saved task owner, then retire with otherwise unowned cells after discard or throw.
Captured children retain their own live tables, independently of root pool identity
or a shared parent cell's later value.
Known-result effect replay still performs the destructuring effects before
delivering its constant result. A handler throw cancels that later delivery.

The pinned PHP8.5.10 source routes are `zend_compile_assign` and
`zend_compile_list_assign` in `vendor/php-src/Zend/zend_compile.c`,
`ZEND_MAKE_REF`, `ZEND_FETCH_LIST_R` / `ZEND_FETCH_LIST_W` in `Zend/zend_vm_def.h`, and
`zend_fetch_dimension_address_LIST_r` / `zend_fetch_dimension_address_read` and
`slow_index_convert` / `slow_index_convert_w` and
`zend_fetch_dimension_address_W` in
`Zend/zend_execute.c`. The VM checks a callback exception before executing the
following target store.

Native-first checked source wrappers and source-reached protocol/state scripts
are listed in the feature inventory. State checks reuse exact original native
paths/streams without an oracle replay. Separate ledgers retain the
[CV](../../coverage/semantics/list-missing-warning-review.json),
[literal](../../coverage/semantics/list-literal-missing-warning-review.json),
[mixed](../../coverage/semantics/list-reference-missing-warning-review.json),
[one-layer](../../coverage/semantics/list-nested-missing-warning-review.json),
[recursive CV](../../coverage/semantics/list-recursive-missing-warning-review.json),
[recursive literal](../../coverage/semantics/list-recursive-literal-missing-warning-review.json),
[nested mixed](../../coverage/semantics/list-nested-reference-missing-warning-review.json),
[integer CV keys](../../coverage/semantics/list-integer-cv-missing-warning-review.json),
[quiet CV keys](../../coverage/semantics/list-quiet-cv-missing-warning-review.json),
[recursive CV keys](../../coverage/semantics/list-recursive-cv-missing-warning-review.json),
[literal-root CV keys](../../coverage/semantics/list-literal-cv-missing-warning-review.json),
[lossy float CV keys](../../coverage/semantics/list-float-key-warning-review.json),
[mixed float CV keys](../../coverage/semantics/list-float-ref-key-warning-review.json) and
[writable float CV keys](../../coverage/semantics/list-float-write-key-warning-review.json)
cuts and failures. No complete array, diagnostics or lifecycle-family claim follows.
