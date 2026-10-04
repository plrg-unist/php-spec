# Coalesce-assignment and unset key continuations

Module249 stages key warnings for `??=` and final `unset` on defined direct
CV-rooted ordinary arrays. A quiet `??=` read retains its selected value/table
through callbacks while separately retaining the original operands for the
later write. A key CV remains delayed and is read again after the RHS; a
computed scalar key is evaluated once. An undefined quiet key becomes null and
then emits the null-key deprecation even if its callback defines that CV.

A present quiet value skips the RHS. An absent value evaluates a computed RHS
before the memoized W conversion; a simple RHS CV remains delayed until
acquisition succeeds. Read and write use their actual separate CODEEXPR and
CODEWRITE lines. The W fetch separates first, protects the selected table and
uses242's exact-one owner gate; a callback-created copy can abort it. Abort skips
a delayed missing RHS CV. Retired null/undefined CV storage can be initialized
again, and a moved sole keeper can receive the eventual write.

Final UNSET_DIM separates before conversion. Undefined key CVs warn once and
retain the empty key without a null deprecation. Null keys do not deprecate.
Float/NaN conversion owns one temporary table protection through all ordered
notices, then checks liveness; it does not use the W exact-one gate. Deletion
therefore affects callback-retained copies, while genuine element cells with
other owners survive. A throwing callback skips the pending deletion/write;
a quiet-stage throw also skips the RHS. Typed aliases and the original
exception/previous chain remain live.

Certificates authenticate the actual consumer/source, opcode line, mode,
operand forms, constants, converted key and remaining notice suffix. Final
unset additionally requires its genuine NStmtUnset ancestor. Captured dynamic
values/table identities remain runtime facts; no history or extra borrowed
place owner is invented. The pinned paths are `zend_compile_assign_coalesce`,
`ZEND_ASSIGN_DIM`, `ZEND_UNSET_DIM` and their dimension helpers in vendor/php-src.

Author6 comparisons include five author originals and the independent multiline
original;80/87/88=255 reached assertions retain their test-only ab7 cut.
Independent10 comparisons retain that same multiline pass and add nine fresh
agreements;84/70/62=216 assertions pass at ab7, giving15 unique private sources.
The actual ab5 composition preserves243/245/246/248; two reduced imported-trait
handler sources pass at separate f5/ea cuts. Private selection, Child called
class, read11/write8, copied-table write abort, unset liveness and post-callback
shared typed-cell/introspection behavior are preserved. The combined and first
reduced coalesce sources retain their CLI60 timeouts with zero agreement. The
[ledger](../../coverage/semantics/dimension-edit-review.json) keeps original
commands, tuples, revisions and native prediction corrections.

The catalogue is `tests/semantics/dimension_edit_cases.py`.
`python3 -B tests/semantics/dimension_edit_prepare.py [fixture-id ...]` compiles
selected source-reached fixtures; their AL_mode numeric runner commands are in
the ledger. Existing local binaries were reused; no fresh build is claimed.

[Nested unset and append255](SOURCE-DIMENSION-TAILS.md) adds bounded CV-rooted
walks with distinct intermediate/final conversion and late RHS demand.
Wider memoized containers, broader GLOBALS RW and earlier
missing/scalar/string/object acquisitions remain required follow-ons.
Read233, writable242 and paused returns keep their separate accepted scope.
