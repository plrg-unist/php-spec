# Independent source conformance targets

These source programs and expected observations were authored independently of
storage/call/control implementation. `cases.json` names their obligations and
precise observations; it does not mark them implemented. The cases distinguish
alias rebinding, copied embedded references, append history, iteration mutation,
delayed reads, coercion, closures, argument binding and abrupt control.

Run `python3 tests/semantics/conformance/oracle.py` to recheck their expectations
against the pinned local engine. This is **oracle-only evidence**, retained in
`coverage/semantics/conformance-oracle.json`, not a semantic evaluator pass.
A `{FILE}` diagnostic placeholder expands to that exact fixture's original path;
no warning or whitespace is removed. Implementers should retain these sources
unchanged when adding them to differential execution.

The null-key case intentionally retains the PHP 8.5 deprecation. Its source routes
are `Zend/zend_vm_def.h` (`ZEND_ADD_ARRAY_ELEMENT`) and `Zend/zend_execute.c`
(dimension access conversion). The dynamic-name case follows delayed operands in
`zend_compile_assign`/`zend_compile_assign_ref`, and is a pinned implementation
observation rather than a portable evaluation-order guarantee. All other initial
cases are independently authored, with no PHPT rewriting or library observers.

The GC pair uses cataloged core controls, with automatic GC disabled so the
uncollected state is deterministic. `Zend/zend_hash.c::zend_array_dup_value`
unwraps singleton references (except self-array references);
`Zend/zend_gc.c::gc_possible_root` and `zend_gc_collect_cycles` explain why a
dead cycle still owns a reference until collection. The literal-occurrence
witness follows `Zend/zend_compile.c::zend_compile_array` /
`zend_try_ct_eval_array` constant creation and
`Zend/zend_operators.c::zend_is_identical` shared-array fast path. Its NaN payload
makes shared-container identity observably different from recursive comparison.
