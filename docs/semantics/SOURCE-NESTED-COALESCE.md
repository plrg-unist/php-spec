# Nested coalesce-assignment key continuations

Module262 extends249 to defined ordinary CV-rooted nested array `??=` targets.
Each quiet intermediate read owns its dereferenced row value, so that row can
survive callback retirement or replacement of its parent. Real embedded cells
stay shared; captured table pointers alone add no owners.

The write walks the current root and real cells after any eager RHS computation.
Computed keys are evaluated once; variable keys stay delayed and can change
before this walk. Each prefix authenticates its actual CODEWRITE line and
corresponding read view. Callback-created copies use242's exact-one acquisition
gate. A prefix abort supplies one genuine null temporary to the remaining
memoized dimensions. A final-key abort suppresses a delayed missing RHS CV;
a prefix abort can still reach that demand through its temporary.

Keyed ASSIGN_DIM creates the selected final entry before a missing RHS warns.
The late continuation owns the original operands/temporary once and borrows
that ELEMENT without adding a table root. It writes captured null even when the
handler defines the RHS or throws. If the handler attaches a real typed cell to
that entry, rejection uses the restored emitter and retains any thrown handler
exception and its older previous chain. Earlier key-handler throws stop the write.

Source occurrences, actual consumer, read/write lines, constants, selected-key
conversion and genuine temporary forms are checked. Consistent dynamic values,
array identities and borrowed places remain runtime facts, without invented
history. Pinned contracts are `zend_compile_assign_coalesce`, `FETCH_DIM_IS`,
`zend_fetch_dimension_address` and keyed `ZEND_ASSIGN_DIM` in `vendor/php-src/Zend`.

Author9/233 includes two independent originals; independent11/277 retains those
same two, giving18 unique private programs and510 reached assertions. Original
f9/2b65 passes remain separate from the affected five-source/84+76+76 continuation
atcf7. The source-backed tail check found a real double-pop at late RHS dispatch;
the dedicated finish rule now preserves every following task. One actual6013
composition at9ac passes private Owner/Child selection, old quiet row17 versus
replaced parent13, and live typed caller/introspection/static17. The
[ledger](../../coverage/semantics/nested-coalesce-review.json) retains exact cuts,
commands, failures and native prediction corrections.

The catalogue is `tests/semantics/dimension_coalesce_cases.py`.
`python3 -B tests/semantics/dimension_coalesce_prepare.py [fixture-id ...]`
compiles selected reached fixtures; original AL_mode runner commands remain in
the ledger. Production source execution uses SL_mode. Existing local binaries
are reused; there is no fresh build or portability claim.

[Global W/RW269](SOURCE-GLOBAL-WRITES.md) separately adds name/missing-entry
updates and compound/nested array ingress. Earlier initial container/string/object
warnings, wider GLOBALS/memoized and remaining write/reference consumers remain
required core work.
Selected agreement does not establish complete core semantics; paused returns
remain unchanged.
