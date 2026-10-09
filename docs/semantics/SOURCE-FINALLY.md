# Finally continuations

Target: pinned PHP 8.5.10 CLI NTS64. Modules155/156 extend Throwable151/152.
Stage A covers normal and exceptional completion, selected catch
binding/body failures, nested calls/finalizers, suppression and exit. Stage B
adds value and reference returns, break/continue across loop, switch and
foreach owners, and goto into, within and out of protected try/catch regions.
The pending transfer keeps its evaluated value or live reference while finally
runs. A later return, throw or exit replaces that transfer. Value returns
snapshot their operand before finally; reference returns retain the cell and
repeat the declared return-type check after finalization.

Unused reference calls also retain their selected cell or evaluated temporary
until that check. Used temporary results keep the ordinary fresh reference.
The installed [retention ledger](../../coverage/semantics/reference-unused-finally-installed.json)
records five exact sources and two paused stages (30 assertions).

A delayed terminal reference-return TypeError now re-enters the protected return
source's exception chain once. The captured operand reaches terminal recheck;
its replay witness retires normally. A second-pass finalizer repair retains the
pending TypeError. Returns and throws can replace it, with ordinary error release
or previous-chain ownership. Source-authenticated TRY and already selected CATCH
owners preserve catch eligibility; a caught error resumes code after the try
without re-evaluating its body.

The [replay review](../../coverage/semantics/reference-return-replay-review.json)
binds ten exact replay originals, 14 current/saved source-reached fixtures with 954
assertions and five affected return controls at private360. Actual361 compilation
has a distinct compiler-only cut. Replay from an already active finalizer,
protected temporary/NULL Notice timing and object conversion remain required.

Source-authenticated while/do/for tails resume remaining body, update and
condition work after caught delayed rejection without queuing the initializer
again. Inner-to-outer loop order and break/continue/goto preserve try/catch scope
in named functions, methods and closures. The [scalar review](../../coverage/semantics/reference-return-scalar-replay-review.json)
binds 14 exact originals and 15 current/saved fixtures with 1,102 assertions at
retained private361 cuts. Actual361 over `cf9411d` passes strict compilation at
`c5579f5d`; fixture typing and label-encoding failures keep zero affected credit.

Source-authenticated CV/compiled-CONST switches restore remaining selected-case
work and fallthrough without repeating subject/case evaluation. END/PHASE are
paired source metadata with no operand or heap roots; end, jump and abrupt
transfer remove both. Region admission preserves enclosing TRY/selected-CATCH
scope in current and saved callers, including same-catch goto before restoration.
The [switch review](../../coverage/semantics/reference-return-switch-replay-review.json)
binds seven preserved originals and 14 reached fixtures/1,339 assertions at
private361 cuts, plus separate actual-parent strict compilation. The original
selected-catch descriptor failure remains zero-credit for that affected fixture.
Module378 preserves the first cleanup of mutable/refcounted switch VAR arrays and
dense value-foreach arrays. Actual source, ARRAY and cursor become non-owning rows;
reconstruction never creates an iterator owner or repeats the counted release.
Capture requires at least three genuine payload-owning edges before cleanup and two
after, counting a shared cell once. This is conservative admission, not normative PHP.
Later reconstruction/fetch checks the same live allocation and dense cursor; a no-read
switch END consumes collected identity without dereferencing it. Current/saved rows
preserve FIRST and update LAST only through authenticated transfer replacement.
Ordinary catches inside an active finalizer retain pending rows.

The [owner review](../../coverage/semantics/reference-return-retired-owner-review.json)
binds four exact sources, nine deliberate COW differences, state23/1,873 and independent
pending98; actual364 adds a genuine carrier71 bridge and strict compilation. The
[duplicate-release policy](DISCREPANCIES.md) preserves coherent c/d=1 rather than native8.
Reached capture proves the original identity, but public metadata cannot authenticate
a fully consistent alternative private history. Wider payload domains, replay from an
already active finalizer and Stringable186 remain open.

Module 379 dispatches VALUE, bare/null and implicit-return reference Notices after
finalizers and repeated type verification, at the captured source line. The raw
operand remains owned through the handler; a handler exception materializes the RV
and leaves through ordinary frame cleanup, without reviving consumed catches.
A replacing finalizer return cancels its pending Notice. The
[Notice review](../../coverage/semantics/reference-return-notice-review.json)
keeps six focused originals, one protected-unused control, eight reached current/saved
fixtures/722 assertions and actual-parent compilation separate.

For one already-active finalizer, runtime156 captures the actual consumed ordinary CV
reference-return source/line and phase3 restore cursor. It owns no operand and survives
current/saved replay continuations. Uncaught inner rejection crosses the consumed outer
cursor without repeating its body; a locally caught rejection resumes the cleared old
return with KNOWN NULL, allowing its repeated check to re-enter the outer finalizer.
Normal replacement returns the selected new cell without an unchanged checked write.
The [active-finalizer review](../../coverage/semantics/reference-return-active-finalizer-review.json)
binds three exact originals and eight source-reached fixtures/602 assertions across
retained367 cuts. Actual-parent strict compilation is separate. Capture and pending
validity enforce the single-history bound; carried markers authenticate source/site/phase,
not a fully coherent alternative private history. Wider consumed VALUE/CONST/NULL and
multiple-active histories, wider Stringable CV layouts and owner domains remain required.

For one old immutable string literal compiled as CONST with exact declared-type
acceptance, runtime156 recovers its original interned value from the authenticated
source after a caught inner rejection. The cursor owns no operand nodes. Normal
resumption restores one VALUE Notice at the original line before materializing a
fresh returned cell; the caller write preserves the globals. Two exact originals
and three reached current/saved fixtures/347 assertions pass at distinct cuts in
the [consumed-literal review](../../coverage/semantics/reference-return-consumed-literal-review.json). Actual-parent compilation is
separate. Effectful VALUE, other CONST/NULL and multiple histories remain required.

Module 186 converts a selected live unconstrained aliased return CV before protected
finalizer entry. Stringable callbacks may rebind/unset GLOBALS without redirecting
the captured cell; current/saved f-local bindings authenticate it. Success writes
that cell atomically before ordinary return unwinding. Callback failure reports the
live selected value and previous callback Exception, then follows initial error
unwinding through the finalizer without minting terminal replay or a Notice.
Thirteen exact originals and eight reached fixtures/843 assertions are recorded in
the [typed CV review](../../coverage/semantics/reference-return-typed-cv-review.json).
Module 381 handles the distinct sole nonreference local CV lifetime. Plain returns
borrow the physical cell; protected returns create one real owning temporary before
verification. Successful conversion releases the old receiver and runs its destructor
before copying the string into the selected cell and entering finally. Callback error
retains that object through finally, then ordinary cleanup destroys it. Five exact
originals and eight reached fixtures/871 assertions are recorded in the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).
Genuinely released targets, destructor throw/reentry, real suspension and wider typed
consumers remain open.

Compilation visits the try body, each catch header/body, then finally. Break and
continue join the ordered goto pass-two stream without generating goto targets.
Jump into or out of finally is a compile error, including break/continue leaving
the finalizer. Ordinary static errors and pass-two checks retain native priority.
Legal goto within finally runs locally; entry into try/catch rebuilds its
finalizer marker without executing the skipped header. Goto entry selects the
no-finally or finally rule from the actual try node. The rebuilt `TRY_END` or
`FINALLY_ONLY` marker and its source node establish the active try or catch
origin, including when a call suspends execution at the destination.

`TRY_END` retains catch eligibility. Selecting a catch replaces it with binding
and `FINALLY_ONLY`, so strict binding failure still finalizes without trying a
sibling catch. Finalizer entry saves normal completion or a Throwable identity
in `FINALLY_RESUME` and changes the current origin to the actual finally node.
Normal completion restores the saved outcome. A new exception chains the saved
one only when it crosses that resume marker; a locally caught exception does
not change the suspended exception.

Pending objects are task roots, including in saved call frames. Source ancestry
requires the correct marker for every active try/catch/finally region, stopping
at callable boundaries. Checks cover missing, duplicate and wrong-phase markers,
saved-frame origins and the trailing origin return. Stage B records the
transfer source and compiled destination/depth, with a separate phase guard
in the continuation. Current and saved frames reject marker deletion, phase
substitution, wrong source/line/depth/target and orphan phase guards. A
reference operand must be a live owned cell; a paused state cannot generally
reconstruct which cell an effectful lvalue evaluation selected. Leaving a finalizer consumes
that return before continuing outside the region. This prevents deleting a
pending marker from silently discarding an exception. Recursive frames validate
their own marker inventories. Exit bypasses finalizers and releases pending
exceptions and their otherwise unowned trace arguments.

The existing Throwable `PREVIOUS` payload remains the only backing store.
Previous-ID read/update helpers isolate the later internal-property migration. In this
generated-only stage its chain is acyclic independently of general heap cycles.
This is not a universal Throwable invariant: admitting constructors must account
for constructor-created previous cycles and terminate observation accordingly.
Automatic finally replacement appends
the old chain at the new chain's tail only when their identity sets are disjoint;
self-rethrow or overlapping chains are unchanged. Uncaught output renders each
object's stored message, source and trace, oldest previous first, then the latest
exception and final throw location. Generated builtin errors suffice; public
Throwable constructors/getters and user subclasses are separate dependencies.

Primary source routes in the vendored engine are `zend_compile_try`,
`zend_handle_loops_and_finally_ex`, `zend_compile_return`,
`zend_check_finally_breakout`, `zend_dispatch_try_catch_finally_helper`,
`ZEND_FAST_CALL`, `ZEND_FAST_RET`, `ZEND_DISCARD_EXCEPTION`, and
`zend_exception_set_previous`.
For delayed reference rejection, `ZEND_VERIFY_RETURN_TYPE` and the dispatch test
against `finally_op` explain exception re-entry at the protected return source.

The [Stage A author ledger](../../coverage/semantics/finally-author.json) and
[Stage B author ledger](../../coverage/semantics/finally-stage-b-author.json)
separate exact source tuples, ordered compiler checks, paused-state ownership
assertions and independent review. The [goto repair ledger](../../coverage/semantics/finally-goto-repair.json)
binds the later cross-family entry regression and paused-frame checks. The Stage B exact source suite includes 20
additional original-source tuples plus six transfer controls. Public Throwable
construction is a separate dependency, so two native probes using `new Error`
or `new Exception` are not Stage B agreements; generated engine throws cover
return replacement. Generators/Fibers, destructor/shutdown callbacks,
dynamic-source lifetime and remaining Throwable protocols remain later obligations.
