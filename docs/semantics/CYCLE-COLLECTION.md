# Explicit cycle collection

Modules 301/317/325/332/335/338/342/345 implement a bounded ordinary-object/array collector on the pinned
PHP 8.5.10 CLI profile. It extends the real ownership graph and WeakReference
protocol; unreachable cycles remain allocated until collection. It does not
establish complete GC, WeakMap, or request-freeing semantics.

`gc_collect_cycles`, `gc_enable`, `gc_disable`, and `gc_enabled` use the existing
source call and argument protocols. Manual collection works while automatic GC
is disabled. A nested collection during a collector destructor returns zero.
The real API continuation remains present through callbacks and pending throws.

Collection inside a running Fiber uses the actual cached internal collector
Fiber. It has visible identity and a saved VM, but no PHP callback or constructor
receipt. The cache supplies one owner; the collecting caller keeps the genuine
pending API continuation. Global collection stays busy through nested Fiber
calls, while cached reuse preserves the worker's reporting mask independently
of shared INI changes.

A suspended destructor detaches its worker and the remaining batch continues
on a replacement. Its real guard retains the current target and pending exception
until resumption or ordinary force-close. The original caller and callable can
retire without invalidating that guard. Resuming the detached worker completes
only its current destructor; a new collection from that callback may use the
replacement cache. Traces contain the source-less `gc_destructor_fiber` frame
and the actual collecting API or resumer. Destructor access inherits the real
collecting caller's scope. Request destruction terminates an idle cached worker
at its authentic object-store handle without invoking a fabricated callback.

Module332 admits public resume/throw into the cached idle worker while no
collection is active. Normal resume discards the supplied value and suspends
again without collecting a new unmarked cycle. An injected exception reaches
the real API caller while the worker remains suspended and reusable; its saved
idle VM retains no exception. The real waiter owns the receiver and argument,
and throw has one temporary global error-task owner. Worker mask restoration
and current API source/sequence authentication remain intact.

Module342 admits the same real public transfer during an active pass when the
authentic plan has no uncalled marked destructor. The unique collector consumer
stays in the real caller VM, so nested GC remains busy0. Main collection leaves
the worker's old scan interval intact; an already-called slot may normalize its
tag, but cannot invoke a callback or change owners. Resume/throw resuspends the
cached worker with its mask and no retained supplied value/error. A stale interval
containing an uncalled marked destructor is handled separately by345.

Module345 preserves the retained physical interval and actual destructor-slot
tags. Public resume/throw scans current marked slots, normalizes consumed tags
and invokes remaining destructors without advancing the outer plan. Its guard
owns the target and pending public exception once; that exception stays separate
from the outer collector's pending error. Zero-owner targets use325's borrowed
retention, including weak reacquisition followed by immediate ordinary release.
Bound direct and C-root calls authenticate the real saved result tail that owns
their Closure. Destructor visibility uses the internal `Fiber` API scope, and
access errors retain that API's file, line and caller trace. A callback may
suspend while retaining this cache and live scan. Its parked VM authenticates the
real suspend continuation and actual saved-frame/origin projections; reentry
within the same live physical pass rebinds the fresh public API in the owning
guard copies. An old pending guard error stays separate from a fresh injected
error. After collection completes, quiescent public reentry authenticates that
same parked VM and a fresh real caller. It requires an unmarked buffer, so the
retained local interval can finish without callbacks even after old slots move.
Retired caller metadata grants no current scope, owner or physical-slot authority;
global scan state and nonce remain unchanged.

A new internal collection resumes that actual parked callback with null, using
the genuine new GC_WAIT caller. Its frozen PLAN.SCAN records the authenticated
old local suffix while the global scan resets for the new collection. Completion
returns any old guard exception through the new collector's pending/free/retrace
continuation. A still-marked target outside the frozen suffix is UNVISITED,
contributes no DONE credit and stays physically buffered. Residual tags do not
seed a later mark/scan; only the current plan's fresh tags are normalized when
checking its producer snapshot. SCAN checks live-guard/receipt consistency, not
universal authenticity of coherently rewritten completed producer history.
The pinned release 8.5.10 executes this path despite matching debug assertions
for !dtor_fiber_running and GC_IS_ROOT; the model preserves the observed tag
instead of silently normalizing it. The later cuts below add public and fresh
internal residual dispatch. Main residual dispatch, overlap, repeated internal
suspension and different-active-pass public reentry remain required work.

Potential roots follow actual outgoing-owner decrements, including a same-target
assignment. The buffer preserves physical slots, reuses freed holes, and
backfills black-root holes from the last live slot. Allocation order and a
stable list filter cannot replace this order.

Ordinary object free clears allocation and weak lookup before child callbacks,
while a borrowed retired buffer slot stays occupied until the existing trailing
store-handle release. It contributes no graph node or owner. A child collector
keeps that physical slot during initial compaction, then removes it with black
roots before white compaction. Its admission requires one genuine pending handle
in the actual release continuation. This rule does not extend array retirement.
Real handle consumers can live in a suspended Fiber VM, an API caller VM or a
force-close caller VM. Their saved release scopes authenticate the same pending
handle; borrowed destructor histories do not. A restored VM view excludes its
own parked copy from the handle count.

An admitted produced object/array `KNOWN` temporary consumed by `DISCARD`
decrements once without registering a potential root, matching `FREE_OP(TMP/VAR)`. Its single
`TEMP` release job remains a real owner until that decrement. A typed borrowed
operand and consumed-progress receipt bind the job to the actual source operation
and adjacent release/exit pair; they add no roots. Progress changes before an
entered destructor captures the operation. CV/reference retirement and outgoing
child slots keep ordinary `VALUE` decrements, including children of the discarded
temporary itself. Admission checks local receipt consistency; producer
reachability for arbitrary synthetic states remains unproved.
Fiber force-close retains the tagged head and pending receipt in its genuine
caller VM until ordinary release consumes it. Generator close consumes the head
and updates progress before capturing its continuation; its new close jobs
remain ordinary `VALUE` jobs.

The collector projects the ordinary heap into the collectable graph. Reference
cells traverse but never count. Objects and user arrays count according to their
first physical visit; an object property table visited through its object is
distinct from that same table first visited as an array root. Genuine empty
literal and runtime null-cast arrays are immutable and absent from this
projection. Their ordinary logical ownership remains intact. Mutation makes a
mutable copy even with one owner; a later emptied mutable array stays eligible.
Runtime flags are borrowed historical IDs and require the exact empty descriptor.

Plans, candidate lists and saved graphs add no owners. Each current destructor
has its real collector guard in addition to ordinary destructor protection;
pending exceptions remain owned once. After a destructor returns, its bare guard
decrement can leave an allocated zero-owner target until retrace. Only the
authentic processed prefix permits that disposition, so another destructor can
obtain and resurrect it through WeakReference without inventing a root.

After a detached worker drops its guard, module325 records an allocated zero-owner
ordinary target in a borrowed buffer slot. The slot retains its outgoing graph
physically and contributes no machine owner. Real collection handles the buffered
target; a real WeakReference result promotes the slot to ordinary potential-root
behavior before pruning. Releasing that last ordinary owner retires the parent
and weak lookup before child callbacks. An unowned worker's forced-close finally
may create the zero target during an active pass; the same pass retraces it.
Its private close control retires only through the authentic release tail,
including both real C owners. Saved caller views borrow that exact shared control's
retirement authority while ordinary closure checks retain their saved scope;
the control gains no PHP catch authority.

Module335 extends that storage admission to normal detached-worker close after
the collection is quiescent. It requires the actual control-release, operation-exit
and worker-release tail, a terminated graceful worker, and exactly the real
control owners. The same live state authenticates saved caller views; it adds
neither an owner nor catch/throw authority. Assigning null to the shared worker
cell drops its last ordinary owner, so `finally` runs immediately and weak worker
lookup clears. `unset` alone leaves the suspended destructor's global alias
alive and does not exercise this close. The zero-owner target remains borrowed
until the next real collection/count1.

Module338 admits the distinct failed-close tail after a throwing `finally` has
dropped the pending graceful exception. The destroy frame retains one private
control owner until return, while the real error belongs to the actual caller's
pending operation. Admission requires the terminated failed worker with null
value, the ordered control/operation/worker/operation tail, matching real-error
source and caller pending slot, and the singleton control release. It extends
only storage retirement and authentic saved caller admission. The private control
gains no owner, previous-exception edge or PHP catch authority. A genuine prior
exception follows ordinary exception chaining and retains its identity.

All selected destructors run before the protected subgraph is freed. Collection
retraces once after their effects, preserves once marks, and atomically disposes
the callback-free ordinary white graph. Actual retirement nulls weak lookup.
The count is frozen from each collector pass; an eager free during a callback
does not erase an already counted white target or add a protected child to it.
Pending destructor throws propagate after collection and retain the API trace.

Task and public admission bind the real source, nonce, saved scope, unique live
consumer and producer plan. Fresh plans must equal the actual producer, including
under an `AT` wrapper. Historical snapshots cannot authorize arbitrary callbacks,
zero-owner retention, counts or frees. Reached tests include heap-valid forged
plans, roots and metadata plus budget identity and resumption.

Explicit boundaries remain for wider internal lifetime graphs, callback reentry
during a different active pass/internal takeover, active-pass failed close and wider
callbackless close-return contexts,
resurrection of initially free non-destructor garbage, a new zero-owner
destructor target after the second trace, and automatic threshold collection.
Wider GC, WeakMap and final combined offline validation remain required.

Engine sources: `Zend/zend_gc.c::{gc_call_destructors,gc_destructor_fiber}`,
`Zend/zend_fibers.c::{zend_fiber_object_destroy,zend_fiber_execute}`,
`Zend/zend_exceptions.c::zend_exception_set_previous`, `Zend/zend_objects_API.c`,
`Zend/zend_objects.c`, `Zend/zend_weakrefs.c`, `Zend/zend_compile.c`,
`Zend/zend_execute.h`, `Zend/zend_ast.c`, and
`Zend/zend_vm_def.h::ZEND_FREE` with `Zend/zend_vm_gen.php::op1_free_op`.
Maintained source and state suites
are `tests/semantics/cycle_collection_{sources,review,state,state_review}.py`.
The bounded private milestone is independently reviewed:30 exact normal source
originals and606 physical premises across14 reached cases pass at distinct
recorded cuts. Earlier14/264 retain43dc; parent/60 retain7f8c; leaf22,
retired20 and the CV source retain403a. Holder, the child-callback original,
remaining12 sources and240 new state premises retain7c0d3d. See the
[ledger](../../coverage/semantics/cycle-collection-review.json). Private
composition at the 285-module parent passes strict initialization, three new
exact originals and45 reached SL premises for the direct temporary consumers
and ordinary parked-handle admission. The earlier30/606 cuts retain their inputs.
The actual286-parent composition adds one exact original in which captured
include-input retirement calls the collector before the child's first property
FETCH. Declaration effects, child6/main26 traces, count1 and weak retirement
agree;66 independent strict-SL premises check the live guard, source context,
heap-identical plan/consumer forgeries and zero/one-step resumption. A larger
nested-Generator original timed out at90s and retains zero agreement.
The actual290-parent composition preserves the readonly/clone state and public
admission while adding collection: strict291 compilation/initialization and one
new readonly-self clone original pass. Reinitialized slots produce two real
cycles, weakly observable until two destructors/count2, then actual retirement
and a second count0. Earlier cuts retain their original inputs. Wider GC and
the final combined offline rebuild remain required.

The larger three-throw collector trace and detached pending-chain originals
retain their 60s model timeouts with zero agreement. They remain explicitly
selectable and are excluded from the default Makefile targets; compact controls
separately exercise the internal trace and detached previous-exception chain.

At the recorded private module 317 cuts, thirteen exact normal source originals and two
independent strict-SL groups with 78/68 physical premises pass. A fresh explicit-INI
original distinguishes the cached mask from changed shared INI; the earlier
reporting original remains a separate observation. The held-guard group also
checks admission of the real saved C root after its original caller retires.
Compilation with 292 modules passes; earlier source, cached-state and initialization
cuts retain their identities in the ledger. The actual318 parent composition
passes strict compilation/initialization with298 modules and one fresh exact
reporting-Fiber/handler original: nested collection stays busy0, masks restore,
and the real cycle count1/weak retirement completes.
The final additive304 publication preserves newer parameter receive/source,
ArrayAccess reference/borrowed-Unset and literal-this emission schemas and passes
the required combined compiler. These disjoint joins add no source/state renewal.

Module325's private299 cut passes strict compilation/initialization, three exact
originals and two strict-SL groups with39/46 physical premises. A separate
actual305-parent composition preserves Generator321 and compute-once pruning39:
one fresh unowned-close original agrees on same-pass count1, weak worker/target
retirement and second count0. Its authentic post-close admission failures are
preserved; the narrow retiring/scoped repair passes changed compilation and the
affected strict-SL group with117 physical premises. These source and state cuts
remain distinct. The final309 composition over callable Fibers322 passes its
required combined compiler at `b4cfe4a14`; source/state cuts are not renewed
and no offline rebuild is claimed.

Module332 passes private311 compilation/strict initialization and three new exact
originals at `084aebce1`. Two explicit strict-SL groups pass91/78 physical premises
at `0649fd604`: authentic API/cache and masks, unmarked-cycle ownership, transient
error owners, same-heap source/sequence/extra-task forgeries, budget identity and
real one-step resumption, post-return public admission and one full continuation.
The first AL120 timeout retains zero agreement; a60-premise strict prefix is a
separate diagnostic. The final315 join over `79546523e` passes combined compilation
at `f3d62ee7b`, preserving329/TRAIT/CV/keep seams without old source/state renewal.
No active-pass public transfer or copied-tool offline rebuild is claimed.

Normal quiescent close335 passes private317 compilation/initialization, two exact
normal originals and two independent strict-SL groups with100/116 physical
premises (runner declarations97/113). The groups check the genuine two control
owners, zero-target borrowing, normal completion, source/sequence/split/failed
forgeries, saved caller admission, no Throwable authority, budget identity and
complete continuations. The final319 join over `6fac6d270` passes combined
compilation at `e12be6f67`; independent review preserves331 callable tags and324
HCELL/staged-binding owners. Earlier source/state cuts are unchanged.
The original unset probes and throwing-finally assignment retain native-only
results with zero335 agreement; the [ledger](../../coverage/semantics/cycle-collection-review.json)
records their exact sources and recovery paths.

Failed quiescent close338 passes private320 compilation/initialization, two exact
normal originals at separate cuts and two independent strict-SL groups with117/130
physical premises (runner declarations114/127). The groups check the one private
control owner, real pending error, saved caller restoration, prior chain,
same-heap source/sequence/mode/pending-slot forgeries, no Throwable authority,
budget identity and complete continuations. The tested322 join over `f89fbee745`
passes combined compilation at `9277e334d`, preserving328/336 and ownership factors.
Publication over `0bb453754` preserves the disjoint prior-array foreach guards
without renewing these cuts.
The larger prior-chain source retains its 60s model timeout with zero agreement
and remains selectable; its reached continuation at the existing120s state cap
is a separate result. Earlier335 and collector cuts are unchanged.

Active exhausted-pass transfer342 passes private323 compilation/initialization,
two exact originals and127/138 independent strict-SL physical premises (runner
declarations125/136). Same-heap outstanding-dtor, source/plan and duplicate-consumer
controls reject; genuine parked admission, one-step return, error owners/masks
and exact continuations pass. Final327 over `5f478ea6a` compiles at `f9dbe3205` with
reviewed337/339/307/334/302 intersections. The initial fixture elaboration stop
and unexecuted interval-overlap preparation retain zero agreement; earlier cuts
are unchanged.

Public interval345 retains two direct source agreements and123/151 historical
physical premises at separate328 cuts. The earlier saved-PHP-class scope assertion
is superseded by a native protected-access discriminator and76 new premises.
A compact bound-C-root original and101 new premises check actual captured caller
ownership through scan/guard entry and real exception identity. Both affected
originals agree at `0df2d161e`/331; final336 over `6e107993a` compiles at `d04ff9c54`.
Parse/fixture stops and the larger captured-source 60s timeout retain zero affected
credit; earlier cuts are unchanged and no offline rebuild is claimed.

Cached callback suspension retains one exact normal source agreement at
`f6dc79eba` and two independent strict-SL groups with 125/103 physical premises
(runner 118/96, authored 115/93) at the recorded 5d7/0ffc fixture cuts. The groups
check live caller versus parked VM authority, actual frame/result/origin views,
sequence/copy/slot/source/post-pass forgeries, fresh captured caller owners,
old 2/new 4 exception owners, one-step replay and exact normal continuations.
The compact source keeps its new error in the final global reference cell with
one owner; the old error, runner and capture retire. Final 343 over `e1c3d4d61`
compiles at `bb74145c7`, retaining the earlier341 cut separately. The origin
comparison factor, Generator storage, call-key source and eager owner-order
changes are independently reviewed pointwise. Both captured source variants retain60s
CLI timeouts with zero source agreement, including the final retry. Earlier
state timeouts/incorrect final-retirement assertions retain zero affected credit.
No old cuts are renewed and no offline rebuild is claimed.

Quiescent post-pass reentry retains one exact normal source agreement at
`b28a5c47b` and 203 independent strict-SL physical premises (101/102; runner 92/93,
authored 89/90) at 95fd with fixture 9765. These check real caller retirement,
stored VM/CONTINUE, no-tag forgeries, harmless buffer/scan relocation, fresh
C-root ownership, old 2/new 4 errors, replay and exact normal continuations.
Request cleanup gracefully terminates the idle worker; B remains a called
self-cycle with one owner, while global error reference cells retain their real
owners and the direct-global runner/capture retire. The main PASS row remains
inside a false aggregate; the corrected core group passes separately. Earlier
incorrect request-final fixture assumptions and captured-source 60s CLI timeouts
retain zero affected credit. The old maintained post-pass refusal premise is
superseded without renewing the historical 228 cut. Final 345 over `4cd2eab3a`
compiles at `0c23223f3`, preserving reviewed Fiber-factory/trait additions.
The separate internal takeover cut has one exact normal source agreement at
`9bc61e2bd` and 154 independent strict-SL physical premises (92/62; recorder 84/59,
authored 81/56) at 0f007 with fixture 9c8246. Real trace/wait activation, old/local
versus new/global intervals, live SCAN forgeries, frozen-position UNVISITED,
residual planning/ingress, old error owner 2→1/previous-none and full original
continuations pass. D stays uncalled/marked through free/retrace and becomes
called/marked only at request cleanup. Original 4460 and compact f093 CLI 60s
timeouts retain zero agreement; no old cuts are renewed. Final 349 over
`63786460e` compiles at `f1b0dea7a` with reviewed SOURCE361, exact-state pruning
graph reuse and dynamic ARG356 intersections. Its residual public dispatch
boundary is extended by the separate cut below; earlier cuts remain unchanged.

Quiescent public resume/throw now reloads the global interval and calls residual
physical tags. RESIDUAL stays set after the last tag is normalized, so callback
validation still requires its actual slot/cursor and fresh API. BIRTH is borrowed
metadata without an owner or access scope; public access still uses Fiber scope.
Already-called tags normalize without another callback. Internal takeover
explicitly rebinds the mode to its real GC caller. One compact throw source agrees
at `ed30c2cb4`; the larger resume CLI retains its 60s timeout/zero agreement.
Independent strict-SL groups at separate ed30 fixture cuts, finalized as73c08 have 66/53 physical premises
(recorder 63/50, authored 60/47), including both full original continuations,
physical slot/end/source/sequence forgeries and error owner 3→2. The first resume
PASS row remains inside a false aggregate; the corrected throw passes separately.
Its mistaken caller-root fixture and aborted unchanged attempt retain zero
affected credit. Residual internal dispatch/overlap, repeated internal suspension,
different-active-pass reentry and whole larger-source completion remain required;
no complete-GC or offline-rebuild claim is made.
Final 351 over `8e513981b` compiles at `3f2ff607d`, preserving reviewed GEN363
fatal/report/trace exclusions,364/ARRAY tasks and TRAIT/PROPS additions.

Fresh internal collection reloads its real global interval and scans both
residual and newly marked destructor tags. RESIDUAL remains true under a genuine
internal API/GC_WAIT caller; PLAN.SCAN stays eps, and current source/cursor/slot
authenticate callbacks. The real collector caller supplies scope. The callback error keeps one
continuation owner through guard, scan and collector wait; the caller’s outer
error stays in its real finally continuation until ordinary chaining.
Nested-data removal debits every frozen residual tag when fresh destructors are
present, so TOTAL is signed: first-pass −1 plus retrace 2 returns 1 while both
D/E retire. The pinned native weak probe independently confirms D-gone.

At separate 6132 fixture cuts finalized as a476c929a, 91/75 strict-SL physical
premises (recorder 81/65, authored 78/62) pass both complete original
continuations, physical mode/wait/end/slot negatives, signed retrace and exact
new/previous exception identities. The entry PASS row remains inside a false
aggregate; the corrected global-view group passes separately. Earlier mistaken
entry-owner and local/global fixture assumptions retain zero affected credit.
Both original whole CLI runs retain 60s timeouts/zero agreement. Final 353 over
`d2bba03b2` compiles at `3f2016024`, preserving reviewed 366/367, source, trait,
storage and Generator cleanup changes. The main physical residual boundary at
that cut is extended below; earlier source/state cuts retain their identities.

Main-thread residual dispatch372 uses `gc_call_destructors(..., NULL)` semantics:
its local interval spans the fresh frozen buffer, while the cached Fiber’s global
cursor remains unchanged by the loop. Current tags must come from their actual
frozen slots; a normalized callback target must also have been uncalled at the
producer. Reused ordinary roots and already-called tags do not invoke callbacks.
Actual main return tasks own one callback pin and pending error; saved main caller
scope/trace remain ordinary. E protects D’s error, which passes through scan/free
before ordinary finally chains the caller’s outer error. Fresh E receives actual
SKIPPED progress, with no invented residual-D membership or DONE credit. Signed
−1+2 accounting still returns 1 while D/E both retire.

At `7e5ff7198`/354 plus fixture `cac7bcad5`, both unchanged originals complete
93/78 independent physical premises (recorder81/64, authored78/61), checking
frozen-slot/CALLED/tag/end negatives and genuine consumer/scope,
unchanged global cursor, exact native streams and new.previous identity. Both
whole CLI runs retain their 60s timeouts/zero agreement. The initial syntax stop
has zero application credit; strict compilation/init pass after explicit interval
binding. Repeated internal suspension, residual/eligible overlap, different-pass
reentry, whole CLI completion and broader GC remain required.
Final 356 over `a1c5e2626` compiles at `43e793df3`, preserving reviewed abstract
method selection, typed freeing reads, raw Fiber-array tasks and ASSERTIONS.
The original source/state cuts retain their inputs and counts.

Internal residual callback suspension375 saves the actual callback VM and
consumes its PUBLIC scan context while detaching the cache in the same step.
The old guard keeps its receiver pin; the real finally error remains in the saved
VM. Its later public
completion observes the cache mismatch and terminates without scanning the
replacement suffix. A real physical-replacement task owns the collector call
and pending error, preserves fresh-plan INDEX/STEPS, and starts a new worker at
the advanced global cursor. It scans physical tags, including residual targets
outside fresh DTORS, before recording actual progress.

At separate `be1099c26` fixture cuts finalized as `7e72ff341`, 92/105 independent
physical premises (recorder 78/95, authored 75/92) complete both unchanged
originals. They check real detachment/replacement, interval forgeries, distinct
old-finally/replacement errors and later old-worker termination. The normal pass
returns 0 while the old guard pins D; after D completes, a later collection returns
1. The normal PASS remains inside the first false aggregate; the affected error
group passes separately after removing duplicate checks. Its original 120s cap
and both whole CLI 60s timeouts retain zero affected/agreement credit.
Final 357 over `b7419cbe1` compiles at `9ce39cd54`, preserving reviewed assertion,
private-constructor, typed freeing-read, source and Generator cleanup additions.
At that cut, last-cache-owner release is Unsupported before mutation; the
separate cut below extends it. Earlier cuts are unchanged.

Last-cache-owner physical replacement now uses the real ordered cache release to
close the actual detached worker before replacement starts. Normal close runs its
finally and retires the two private control owners in order. Failed close releases
the pending control copy when its finally throws, leaves one private release owner, and moves
the real error into the actual plan pending slot. The caller's outer error remains
in its real FINALLY continuation until ordinary chaining. The new retiring
predicate admits only this actual terminated worker/sequence and ordered
control/operation/worker/physical-replacement tail; it grants storage and scoped
caller validity without a Throwable owner, catch authority or invented D progress.

At separate `4227d8609` fixture cuts finalized as `292b27847`, 77/89 independent
physical premises (recorder 63/71, authored 60/68) complete both unchanged
originals. They check normal control2→1, failed control1 versus real plan pending,
the outer FINALLY owner, same-heap source/sequence/pending forgeries, count1/weak
retirement and exact new/previous identity. The normal PASS remains in a false
aggregate; only the affected failed negative reruns after correcting root order.
That fixture stop and both whole CLI 60s timeouts retain zero affected/agreement
credit. Final 358 over `0059e0a9e` compiles at `0da2cdae7`, preserving empty PACKS
in both actual API constructors, inherited-constructor diagnostics and quiet
freeing reads. That cut's takeover-resuspension refusal is extended below.

An old public callback can now suspend again during internal takeover. The real
wrapper advances its reset global cursor, which differs from the old guard's
local slot. Detachment captures that advanced suffix in PLAN.SCAN and the
physical-replacement task; earlier marked targets remain physical and unvisited,
without DONE credit. The old guard/VM and its real FINALLY error stay separate
from the fresh caller's FINALLY. Replacement uses the current GC caller and
physical suffix, preserving the old callback's lexical scope.

At separate `88daee39b` fixture cuts finalized as `27e65e46e`, 114/98 independent
physical premises (recorder 98/86, authored 95/83) complete both unchanged
originals. They check reset-cursor/frozen-end readiness, independent suffix
mismatches, retained low tags, once-only activation and separate FINALLY owners.
The normal PASS remains in a false aggregate. Only the affected error group
reruns after replacing a request-final lookup of the retired new error with its
actual retirement; the original stop and diagnostic copy retain zero affected
credit. Both whole CLI 60s timeouts retain zero agreement. Final 358 over
`6ed4873bd` compiles at `0bc957892`, preserving Generator renderer/handler and
dynamic-source hooks. Overlap, different-pass reentry and whole CLI completion
remain required.
