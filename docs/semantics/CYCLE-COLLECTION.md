# Explicit cycle collection

Modules 301/317/325/332/335 implement a bounded ordinary-object/array collector on the pinned
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
until the next real collection/count1. A throwing `finally` has a distinct
failed-close control lifetime and remains required.

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

Explicit boundaries remain for wider internal lifetime graphs, public idle-worker
transfer during an active collection, failed-finally and wider callbackless
close-return contexts,
resurrection of initially free non-destructor garbage, a new zero-owner
destructor target after the second trace, and automatic threshold collection.
Wider GC, WeakMap and final combined offline validation remain required.

Engine sources: `Zend/zend_gc.c::{gc_call_destructors,gc_destructor_fiber}`,
`Zend/zend_fibers.c::zend_fiber_object_destroy`, `Zend/zend_objects_API.c`,
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
