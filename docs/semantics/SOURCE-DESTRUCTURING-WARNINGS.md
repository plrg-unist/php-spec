# Missing-key destructuring warnings

Module409 supplies the E_WARNING continuation for missing by-value fetches into
direct CV leaves. Recursive by-value patterns admit direct CV or literal RHS arrays;
recursive mixed value/reference patterns require a direct CV RHS. Implicit integer keys
and warning-free compiled constant keys are admitted. Literal strings retain their
authenticated interned-string carrier before key conversion. Undefined key CVs,
null/lossy-float key diagnostics, mixed literal/call or wider RHS producers
and target forms remain separate dependencies.

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
constant/implicit key, compiler line and captured array/cell allocation authenticate
the producer and saved resume. These checks establish source compatibility and
liveness; they do not reconstruct historical identity from a live CV. A mixed
resume does not require the cell to retain its original array. Prior reference
leaves retain the fetch line; prior by-value CV stores select the target line.
Each pattern's own reference demand selects its cell or by-value array operand;
saved child authority is independent of the current parent table or CV binding.
The generic error-handler machinery supplies mask eligibility, temporary handler
disabling, exact-false default reporting and restoration. A present null entry
does not enter the missing-key continuation.

For a compiled literal root the captured table must match the RHS pool occurrence.
A runtime root instead requires its nonconstant compiler descriptor and a
mutable live table; its embedded references are not reconstructed from live CVs. Rebinding
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
`zend_fetch_dimension_address_LIST_r` / `zend_fetch_dimension_address_read` in
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
[recursive literal](../../coverage/semantics/list-recursive-literal-missing-warning-review.json) and
[nested mixed](../../coverage/semantics/list-nested-reference-missing-warning-review.json)
cuts and failures. No complete array, diagnostics or lifecycle-family claim follows.
