# Nested unset and append continuations

Module255 stages defined ordinary CV-rooted array walks after their key
expressions. Intermediate unset uses FETCH_DIM_UNSET: separation precedes
conversion, missing key CVs latch null, and a live table then emits null-key
deprecation. A table that expires during the first warning skips that
deprecation. Null and ordered float notices retain the native table protection;
borrowed rows add no owner. Final deletion keeps249's distinct U-only/null-quiet
rules and liveness gate. A missing final key still warns after prefix expiry,
without refetching a variable that the callback recreated.

Append evaluates a computed RHS before prefix fetches. A simple RHS CV stays
delayed until ASSIGN_DIM.242's W exact-one gate applies to intermediate fetches;
an aborted fetch creates one genuine unnamed null cell for the later consumer.
The evaluated RHS, including arrays with real references, remains owned once
through callbacks. A missing RHS still warns after prefix abort and captures
null. Its selected old table must survive before insertion into the current real
child cell. A throwing RHS handler can still insert null before exception
propagation; a throwing key handler stops the append and later destination write.

Source/consumer occurrences, opcode lines, modes, constants and notice suffixes
are authenticated. Captured dynamic values and borrowed places remain runtime
facts; the rules do not invent a history for them or add owner roots to pointers.
Pinned contracts are `zend_delayed_compile_dim`, `zend_compile_unset`,
`zend_compile_assign`, `zend_fetch_dimension_address_UNSET`, `slow_index_convert`
and `ZEND_ASSIGN_DIM` in `vendor/php-src/Zend`.

Author6 source agreements include the independent expiry original;75/78/94=247
reached assertions pass at643. Independent18 retains that expiry pass and adds17
fresh comparisons;85/102/87/82=356 assertions pass at75c8, giving23 unique private
agreements. One actual0b source at223 captures a parent-private first-class
handler with Child called class, copy-induced prefix abort/TEMP and a computed
ARRAY RHS holding a live typed caller cell. Its post-handler17 is visible through
the result, argument view and static property. The original concrete-class array
registration selected Child-public in both runtimes; it earns no private/abort
credit. The [ledger](../../coverage/semantics/dimension-tail-review.json) preserves
that source correction, original overlap failure, tuples, commands and test cuts.

The catalogue is `tests/semantics/dimension_tail_cases.py`.
`python3 -B tests/semantics/dimension_tail_prepare.py [fixture-id ...]` compiles
selected reached fixtures; actual AL_mode runner commands are retained in the
ledger. Production source execution uses SL_mode. Existing local binaries were
reused; no fresh build or portability claim is made.

[Nested coalesce262](SOURCE-NESTED-COALESCE.md) adds defined CV-array memoized
walks with genuine quiet row owners and distinct late keyed-RHS behavior.
Broader initial container/string/object diagnostics, GLOBALS RW, wider memoized
containers and remaining write/reference consumers are required core work.
Read233, writable242, direct edits249 and paused returns retain separate scope.
Selected agreement does not establish complete core semantics.
