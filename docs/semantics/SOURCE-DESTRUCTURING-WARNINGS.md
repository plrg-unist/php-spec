# Missing-key destructuring warnings

Module409 supplies the E_WARNING continuation for missing by-value fetches into
direct CV leaves. Flat by-value patterns admit direct CV or literal RHS arrays;
one nested by-value layer and flat mixed value/reference patterns require a direct
CV RHS. Implicit integer keys
and warning-free compiled constant keys are admitted. Literal strings retain their
authenticated interned-string carrier before key conversion. Undefined key CVs,
null/lossy-float key diagnostics, deeper patterns, nested reference leaves, wider RHS producers
and target forms remain separate dependencies.

The by-value RHS is captured before the first item; a direct CV uses Zend's `QM_ASSIGN`.
The saved task owns that array through handler selection, the ordinary callback
frame and normal/throw cleanup. Callback insertion or replacement does not restart the
missing fetch: it still supplies null. Following items read the captured table
after the previous target store, so copied scalar entries and shared embedded
reference cells preserve their different behavior. Assignment-result delivery
returns the captured RHS value. A throwing handler cancels the pending target
store and later items, preserving callback writes and the supplied Throwable.

For one nested layer, the child task retains its array while the outer continuation
retains the parent. An outer missing fetch supplies null to the child, whose reads
silently deliver null. An inner missing fetch retains both tables after callback
source rebinding. The first child fetch inherits the outer fetch's compiler line;
the next outer item inherits the child's final compiler location. During throw
cleanup the outer continuation can keep the child alive
after the inner warning task is discarded; both retire after all owners disappear.

Mixed patterns instead use `MAKE_REF` and retain the source cell. Callback value
assignment changes the value used by later fetches; unsetting/rebinding the CV
name leaves the saved old cell authoritative. The interrupted fetch still gives
null before the next reference leaf reads or makes writable that cell's live value.
Replacing it with null therefore permits later array creation. Reference fetches
perform ordinary COW separation, and earlier reference targets remain visible to
the callback. Assignment-result delivery resolves the same saved cell after the
targets. Once tasks and other owners disappear, the old cell/table retire.

Source occurrence, admitted RHS shape, remaining items, selected index,
constant/implicit key, compiler line and captured array/cell allocation authenticate
the producer and saved resume. These checks establish source compatibility and
liveness; they do not reconstruct historical identity from a live CV. A mixed
resume does not require the cell to retain its original array. Prior reference
leaves retain the fetch line; prior by-value CV stores select the target line.
The generic error-handler machinery supplies mask eligibility, temporary handler
disabling, exact-false default reporting and restoration. A present null entry
does not enter the missing-key continuation.

For a compiled literal the captured table must match the RHS pool occurrence.
A runtime literal instead requires its nonconstant compiler descriptor and a
mutable live table; its embedded references are not reconstructed from live CVs. Rebinding
`q` in the handler leaves the literal's old reference cell available to later
fetches. Pooled arrays keep permanent owners; runtime literal arrays can have only
the saved task owner, then retire with otherwise unowned cells after discard or throw.
Known-result effect replay still performs the destructuring effects before
delivering its constant result. A handler throw cancels that later delivery.

The pinned PHP8.5.10 source routes are `zend_compile_assign` and
`zend_compile_list_assign` in `vendor/php-src/Zend/zend_compile.c`,
`ZEND_MAKE_REF`, `ZEND_FETCH_LIST_R` / `ZEND_FETCH_LIST_W` in `Zend/zend_vm_def.h`, and
`zend_fetch_dimension_address_LIST_r` / `zend_fetch_dimension_address_read` in
`Zend/zend_execute.c`. The VM checks a callback exception before executing the
following target store.

`list_missing_warnings.py` runs native-first checked original sources.
`list_missing_warning_protocol.py` reuses those exact native source paths and
streams for source-reached SL state checks; it never reruns the oracle.
`list_missing_warning_review_sources.py` and
`list_missing_warning_state_review.py` retain independent sources and assertions.
The [review ledger](../../coverage/semantics/list-missing-warning-review.json)
records distinct validation cuts and preserved failures. No complete array,
diagnostics or lifecycle-family claim follows from this slice.
The literal-RHS extension has separate source/state cuts in the
[literal review](../../coverage/semantics/list-literal-missing-warning-review.json),
using `list_literal_missing_warnings.py` and
`list_literal_missing_warning_protocol.py` plus independent counterparts. Its
original native paths/streams are reused without an oracle replay.
The [mixed-reference review](../../coverage/semantics/list-reference-missing-warning-review.json)
records separate source/state cuts from `list_reference_missing_warnings.py`,
`list_reference_missing_warning_protocol.py` and independent counterparts.
The [nested review](../../coverage/semantics/list-nested-missing-warning-review.json)
records its own source/state cuts from `list_nested_missing_warnings.py`,
`list_nested_missing_warning_protocol.py` and independent counterparts.
