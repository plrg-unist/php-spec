# Writable dimension key continuations

Module242 stages W/RW key warnings for defined mutable CV-rooted ordinary arrays,
including nested reference acquisition, pre/post updates and direct assignment
or compound consumers. Separation precedes conversion. Missing key CVs retain
the fixed empty key; null/float conversions retain the chosen key. NaN keeps
one table protection across its ordered range/precision notices; a first-notice
throw stops the second callback and the later consumer.

After conversion, acquisition requires exactly one genuine table owner besides
the temporary protection. A callback-created table copy therefore aborts even
while the table remains live. Extra aliases of a real container cell do not
duplicate its table owner. A sole keeper can acquire the selected table after
the original CV retires. Captured INDIRECT rows remain borrowed, so retiring
their parent cannot manufacture a surviving inner-table owner. An aborted inner
fetch supplies a genuinely owned unnamed null cell to a following nested fetch.

Intermediate fetches precede outer key and RHS evaluation. Final ASSIGN_DIM and
DIM_OP convert after the RHS expression, then demand a delayed RHS CV only on
successful acquisition. Aborting compound/assignment fetches skip that demand.
Reference aborts produce an independent null cell; throwing callbacks skip the
destination rebind and preserve typed aliases and the original previous chain.

Direct GLOBALS W reference fetches reread an undefined key in the caller CV but
retain a converted Array name. Named reference sends fetch before name mapping
and promote only after it succeeds. Their selected callable and earlier supplied
arguments remain owned through callbacks. Existing named CV priorities and final
string/scalar consumers retain their original routes and error kinds.

Source occurrence, opcode line, consumer mode, operand forms, compiled constants,
converted key and ordered notice suffix are authenticated. Consistent dynamically
selected tables/places/values remain runtime facts; no callback history is invented.
The pinned contracts are `slow_index_convert_w`, `zend_fetch_dimension_address_inner`,
`ZEND_FETCH_DIM_W/RW` and `ZEND_ASSIGN_DIM/ASSIGN_DIM_OP` in `vendor/php-src/Zend`.

Author11 source agreements include nine author originals and two independent
originals; independent15 fresh comparisons retain those two separately. Author
89/102/68/81=340 and independent90/87/89=266 reached assertions keep their actual
cuts. One current3b622 composition passes private/called-class selection and
typed caller cell/introspection retention through copy-induced acquisition abort.
The [ledger](../../coverage/semantics/dimension-write-continuations-review.json) records original
tuples, failures, commands and source-equivalent current adapter reuse.

The catalogue is `tests/semantics/dimension_write_cases.py`.
`python3 -B tests/semantics/dimension_write_prepare.py [fixture-id ...]` compiles
selected source-reached fixtures; their numeric runner commands are in the ledger.

[Coalesce/unset249](SOURCE-DIMENSION-EDITS.md) adds bounded direct CV-array quiet
memoization, write continuations and final unset liveness.
[Nested unset and append255](SOURCE-DIMENSION-TAILS.md) adds delayed prefix walks,
genuine abort temporaries and late RHS warning/insertion.
[Nested coalesce262](SOURCE-NESTED-COALESCE.md) adds recursive quiet/write walks
and preserves the selected keyed entry through delayed RHS warning/throw.
[Global W/RW269](SOURCE-GLOBAL-WRITES.md) adds name/missing-entry continuations
for direct updates/compounds and nested array ingress.
[Container276](SOURCE-CONTAINER-WRITES.md) adds undefined/null/false W/RW
initialization and final array-reference ingress with distinct false/type/throw
priority. Wider read/quiet/memoized/unset/GLOBALS containers, string/key warnings
and object/magic/computed acquisitions remain required.
Read233, snapshots226 and paused returns retain separate scope.
