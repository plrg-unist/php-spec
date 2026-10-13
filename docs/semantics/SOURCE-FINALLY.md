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

An old explicit `return null` with exact declared-type acceptance now recovers
PNULL only from its checked special-constant source. The consumed cursor owns
no operand, and normal resumption restores one original-line VALUE Notice before
a fresh returned cell. It remains distinct from bare/implicit NULL designations
and cleared CV recovery. Two originals and three reached current/saved fixtures/367
assertions pass at separate cuts in the [consumed-NULL review](../../coverage/semantics/reference-return-consumed-null-review.json).
General CONST, other effectful VALUE signatures/layouts, other NULL and multiple
histories remain open.

For a named zero-argument call concatenated with an empty string, runtime156
captures only root-free source history of the consumed computed VALUE. Normal
resumption uses cleared PNULL and one original-line VALUE Notice at the public
pause. Nonnullable string rejects NULL before Notice delivery, reenters the
outer finalizer and later selects the new reference cell (source1/state3-386
in the [computed-VALUE review](../../coverage/semantics/reference-return-consumed-value-review.json)).
The checked ordered string|null mask accepts NULL and delivers one Notice
before returning a fresh caller cell distinct from x and y. Neither path
repeats the call or restores its old payload; the nullable path enters no
second outer finalizer. One nullable original and three reached fixtures/381
assertions pass at separate cuts in the [nullable computed-VALUE review](../../coverage/semantics/reference-return-consumed-value-nullable-review.json).
Other VALUE signatures/layouts, owning payloads and wider histories remain open.

For exactly two already-active ordinary CV finalizers, runtime156 captures
the actual ordered Z/X return, phase3 and restore triples in separate steps.
The pair certificates own no old operands and survive genuine saved frames.
Uncaught inner rejection replays its finalizer, then leaves Z and X in order;
initial successful replacement retires the pair and returns the selected y
alias with x/z unchanged. Capture requires the exact named-function string
signature and no destructor operation. Two originals and four reached
current/saved fixtures/439 assertions pass at separate cuts in the
[two-history CV review](../../coverage/semantics/reference-return-multiple-active-cv-review.json).
After a locally caught inner rejection, the consumed middle CV resumes as cleared
NULL. Atomic Z/X restoration adds no payload root; the fresh NULL TypeError uses
Z's original line and replays its finalizer with the outer history retained.
The selected y alias later returns. One original at `478eb1e4` and three reached
current/saved fixtures/391 assertions at `0068f567` pass; private strict374 is
separate. Only the complete pair and CLEARED endpoints are public frontiers:
the first Z leave is helper-internal, and missing CLEARED is helper refusal.
The earlier state439 caught-Unsupported helper boundary is superseded only for
this slice.

The outer history may also be a source-equal immutable string literal; middle Z
and inner Y remain ordinary distinct CV returns. The literal owns no cell or
operand root, and its canceled VALUE Notice stays absent through caught Y
replay, cleared-Z replay and saved ping frames. Y has two source replay contexts
but one finalizer owner. Successful Y or error escape retires both histories.
Three exact originals, five reached fixtures/461 assertions and independent
three/187 pass at separate cuts in the same review.

A literal-only catch passage authenticates the intervening D catch and following
echo from checked source. Pending suffixes 3/2 retain D's actual origin; 1/0 use
the outer-finally origin after its real restore. Y has three replay contexts and
Z has two. Caught Y rejection retains the histories; M2 skips Y, fresh Z NULL
rejection reaches D, and B precedes literal resumption with one original-line
VALUE Notice and a fresh caller cell. Expanded pair admission projects scope
only for the intact authenticated tail; the first-Z helper remains nonpublic.
Three exact originals, five reached fixtures/480 assertions and independent
pending63/7 pass at separate cuts in the same review. Other passages/layouts,
lifecycle capture, wider signatures/operands, further histories and broad returns
verification remain open.

A checked named zero-argument call may precede that echo. Five reached pending
suffixes preserve D/outer-finally scope; the saved post-D ping restores f with
the root-free old literal and canceled Notice. D;P;B precedes the original Notice
and fresh caller cell. Three originals, six/514 reached checks and independent
saved-ping70/4 pass at separate cuts in the same review; throwing, mutating and
reentrant call bodies remain open.

For more than two adjacent ordinary CV histories, an ordered cursor list
authenticates each source return, phase3/restore triple and complete protected
path. Capture requires distinct live CVs, the exact named-function string
signature and inactive destruction. Each old operand loses its task root once;
partial markers validate the actual next-finalizer origin before virtual task
traversal. The observed Z/W/X chain survives Y-error replay and saved ping scope,
then leaves Z, W and X in order; initial success returns the selected y alias.
Two exact originals, five reached fixtures/467 assertions and independent
partial90/7 pass at `5a9fd5ba` in the same review.

A checked singleton TypeError catch in the selected Y owner now resumes the
consumed Z/W/X chain atomically as root-free cleared NULL, retaining first-Z
source/line/recheck. Its fresh NULL TypeError remains distinct from the live Y
error; W/X survive replay and authentic saved ping restoration. An optional
rethrow of the catch CV preserves the original Y error. Three exact originals,
six reached fixtures/640 assertions and independent CLEARED75/5 pass at separate
`cc93bbac` cuts. Immediate Y success is source3 evidence only; internal partial
leaves remain nonpublic, and source reauthentication does not exclude coherent
history rewrites. Other caught layouts retain explicit Unsupported boundaries;
mixed histories, lifecycle capture and broad returns_verify remain OPEN.

An immutable string literal may be the final history in this ordered list. Its
source-equal interned value and original line reconstruct the root-free live
triple; inner Z/W/Y remain distinct ordinary CVs. Initial VALUE return designates
one pending Notice, canceled by replacement before capture. Saved Y-error replay
retains the literal; escape leaves Z, W and literal in order, while immediate Y
success returns its alias. Two exact originals, five reached fixtures/504
assertions and independent partial96/8 pass at separate `d28f2a0c` cuts in the
same review. At that cut, normal mixed clearing/resumption remained Unsupported;
the all-CV cleared route is unchanged.

A checked C/IF/E passage now admits Z/W/old replay with Y3/Z2/W2/old1 contexts.
The root-free pending E suffix authenticates actual restores before projected
task traversal; full consumed tails and throw-only standalone old markers have
separate public scope guards. C clears Z to NULL, whose fresh error stays distinct
from the live Y error through saved M2 restoration. E/B resumes old once with its
original-line Notice and a fresh caller cell; E rethrow retires W/old with the
same fresh error. Source3 and affected old643 compatibility pass at `4336`; eight
reached fixtures/811 assertions retain first7/705 there and final106 at validator-only
`3abc`. Independent E-prefix297/5 is separate. Internal partial leaves remain
nonpublic; local source certificates do not exclude coherent history rewrites.
Adjacent mixed clearing, other layouts, lifecycle and broad returns remain OPEN.
Pinned SpecTec overlap analysis treats Cons/nonempty Fixed as disjoint while its
interpreter matches Cons on every nonempty sequence. Exact-length Cons suffixes
preserve catch-tail fallback and the specialized mixed clear-site branch; guards
and lengths are unchanged, with no vendor modification or PHP divergence.

The E-catch body additionally admits a checked named zero-argument call followed by
literal echo, optionally rethrowing that same catch CV. The measured pure `ping()`
preserves the complete saved statement/catch restores, Z replay and root-free W/old
tail under f scope. Its actual pre-W restore is W.finally, not Z.finally; the fresh
Z-NULL TypeError stays in f.e. Call return resumes E/B and old once with its original
Notice and a fresh caller cell. Same-CV rethrow carries that identical fresh error
through W/old retirement; selected Y cancels the call and keeps its alias. Source3,
reached3/301 and independent saved80/1 pass separately at `e18e338a`, including public
refusal of the missing pre-W restore and a late normalized budget comparison.
The shared source guard admits named noarg calls; general effects, reentry, suspension,
other catch layouts and broad returns verification remain OPEN.

Legacy throw retirement now restores a missing pending VALUE Notice for the first
surviving source-authenticated live return. It emits no diagnostic at retirement,
preserves existing markers/restores, and excludes NULL-return forms and access-reference VALUE
paths. A guarded E-call reentry witness delivers one nested Notice before T and one
outer Notice after E/B; rethrow emits neither while retaining the same error. Source2,
reached3/260 and independent saved-frame59/1 pass at `23cde2d9`, including public
wrong-line refusal, fresh caller-cell checks and a late budget comparison. The
generic helper exceeds this string-literal witness; broader reentry/lifecycle/NULL-form
restoration and complete returns verification remain OPEN.

A source-bound counter-guarded destructor now admits a noarg call to the same named
f, with the selected Y increment and ordinary string history guards preserved.
Source2, reached2/324 and independent nested public129/1 pass at `7ab32609`.
The actual saved destructor7/outer f21/main registered1/1/1 prefix publicly admits;
missing outer operation exit refuses. The unused nested return resumes the genuine
destructor before T, followed by D, while the same original Y TypeError survives
ordered Z/W/X retirement and caller catch. Selected bypass skips object birth and
keeps its alias; counter-PBOOL refusal and a budget split before T are checked.
No active lifecycle, error-chaining, Notice or root rule changed. The local source
certificate and this guarded witness leave wider reentry/returns OPEN.

The guarded destructor additionally permits an ordinary local AssignRef from the
same named f and a literal write through that local. Source2, reached2/332 and
independent public150/1 pass at `30e2fdbc`. The real return reference survives
queued frame cleanup and binds inner to global/saved Y before the probe write.
Probe/T/D leaves the original outer Y TypeError unchanged through ordered Z/W/X
retirement and caller catch, with public admissions and late budget equality.
Missing outer operation exit and counter-PBOOL refuse; selected bypass keeps its
alias without object birth. M35 and shared call/reference/active lifecycle rules
are unchanged. Local reconstruction and reached alias evidence leave broader
reference demand, historical alias provenance and returns verification OPEN.

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
