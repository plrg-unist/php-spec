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
has a distinct compiler-only cut. Physical-array owners, replay from an already
active finalizer,
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
Runtime VAR/TMP physical owners, active-finalizer replay and NULL/186 paths remain
required.

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
