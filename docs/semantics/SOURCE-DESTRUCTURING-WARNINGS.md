# Missing-key destructuring warnings

Module409 supplies the E_WARNING continuation for by-value destructuring from
a direct CV array into flat direct CV targets. Implicit integer keys and
warning-free compiled constant keys are admitted. Literal strings retain their
authenticated interned-string carrier before key conversion. Undefined key CVs,
null/lossy-float key diagnostics, nested patterns, reference leaves, wider RHS
producers and target forms remain separate dependencies.

The RHS is captured before the first item, as in Zend's `QM_ASSIGN`. The saved
task owns that array through handler selection, the ordinary callback frame and
normal/throw cleanup. Callback insertion or replacement does not restart the
missing fetch: it still supplies null. Following items read the captured table
after the previous target store, so copied scalar entries and shared embedded
reference cells preserve their different behavior. Assignment-result delivery
returns the same captured array. A throwing handler cancels the pending target
store and later items, preserving callback writes and the supplied Throwable.

Source occurrence, direct-CV assignment shape, remaining items, selected index,
constant/implicit key, compiler line and captured-array allocation authenticate
the producer and saved resume. These checks establish source compatibility and
liveness; they do not reconstruct historical table identity from a live CV.
The generic error-handler machinery supplies mask eligibility, temporary handler
disabling, exact-false default reporting and restoration. A present null entry
does not enter the missing-key continuation.

The pinned PHP8.5.10 source routes are `zend_compile_assign` and
`zend_compile_list_assign` in `vendor/php-src/Zend/zend_compile.c`,
`ZEND_FETCH_LIST_R` in `Zend/zend_vm_def.h`, and
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
