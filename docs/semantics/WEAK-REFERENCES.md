# WeakReference and WeakMap protocols

Module 296 implements the pinned PHP 8.5.10 `WeakReference::create` and `get`
protocol on the reviewed eager-destruction 270 source. Twenty-one exact original
sources agree; nine reached cuts pass 344 physical premises. Five Unsupported
controls earn zero agreement. The [ledger](../../coverage/semantics/weak-reference-review.json)
keeps their separate tested snapshots. Canonical292/304/270 composition separately
passes strict277 initialization and one exact returned-object weak lifetime source;
bounded ordinary cyclic collection is covered separately by
[module301](CYCLE-COLLECTION.md). Wider collection and WeakMap protocols remain required.

A successful wrapper records an immutable semantic object ID. The target adds
no ownership edge. `create` returns the same allocated wrapper for a target,
or allocates a fresh wrapper after its predecessor retires. `get` copies a live
target into the ordinary result owner. Discarding or saving that result uses the
existing ordered release machinery.

Wrappers satisfy nominal `WeakReference` argument and property types independently
of referent lifetime; rejected receives name the actual internal class.
The [raw Fiber-array review](../../coverage/semantics/fiber-array-core-callbacks-review.json)
records the separate nominal-type source and reached checks.

Object IDs never reuse. `get` checks target allocation and the actual ordinary
INSTANCE/stdClass storage359 stage, without a second registry or a store-handle identity.
Ordinary `__destruct` and resurrection keep the target live. For the reviewed ordinary
INSTANCE/stdClass property-child free_obj path, Weak notification precedes child
release while one physical parent pin remains allocated, so `get` already returns
null. WeakMap value callbacks have a separate notification-order boundary below.
Native notification clears its raw pointer; the model retains the nonowning semantic ID as borrowed history.
Closed Generator storage355 instead retains its weak target through Closure/cache
release and notifies on final retirement. The ordinary pin, saved Fiber and
Generator RETURN-child checks are recorded in the
[property lifetime review](../../coverage/semantics/duplicate-property-reference-review.json).

Direct NEW allocates a null-born candidate before evaluating arguments. Its
internal constructor always throws; unknown named arguments fail before the
body. This transient record requires a genuine pending constructor or failed-release
continuation. The actual pending-throw operation and source scope authenticate
failed release; validated allocated Fiber/Generator carriers retain saved scopes.
NEW's result continuation must name the selected candidate. Deferred constant-AST
WeakReference construction stops explicitly before allocation; wider initializer
support remains required.

Abandoning a carrier with a pending null-born candidate stops before actual free,
preserving its authentic release owner and saved stack. Genuine forced-stack
unwind remains required. The entry reason is `abandoning WeakReference constructor
argument stack`; final Fiber cleanup reports the existing `force-closing a
suspended Fiber` boundary, while Generator cleanup retains the entry reason.

Selection covers direct static calls and instance/nullsafe calls, including
computed API names admitted by the existing method-selection path. Instance
syntax for static `create` retains borrowed selector history without a receiver
owner. `get` and explicit `__construct` retain their real receiver. Arguments,
API errors and traces use the existing internal-call protocol. Clone throws its
native Error; first-class API captures stop explicitly. Property protocols,
wider callable consumers and collection APIs are not implemented by this module.

The pinned contracts are `Zend/zend_weakrefs.c` (`zend_weakref_find`,
`zend_weakref_create`, `zend_weakref_get` and the three API bodies),
`zend_objects_store_del` in `Zend/zend_objects_API.c`, and
`zend_object_std_dtor` in `Zend/zend_objects.c`. Notification precedes outgoing
property release and follows the destructor/resurrection decision.

Maintained checks: `weak_reference_sources.py`, `weak_reference_state.py`,
`weak_reference_review.py`, and `weak_reference_state_review.py`. Original
compiler, source and reached-state failures remain in ignored `.tools` with
zero credit. The final combined offline rebuild remains required; paused return
verification is unchanged.

## Wrapper creation during live map teardown

Modules359/386 admit `WeakReference::create` for a unique allocated empty-map
storage pin with pending NOTIFY in the current tasks or saved frames. The
existing wrapper must be the actual allocated find result and match NOTIFY.
After that wrapper's ordinary retirement, creation appends a fresh wrapper
and changes only the pin's borrowed notification identity. Neither the wrapper
nor NOTIFY owns the map; the existing physical pin and callback-local copy do.
The callback releases that copy before returning.

The reuse/recreation originals (88/123 bytes) agree at `ac980b0`.
Three reached groups pass 123/133/77 checks, totaling 333. The first two bind
actual CONFIG_INVOKE/source/frame authority and argument-owner removal
(three to two map owners), with stale notice, handle, duplicate-pin and
competing-find controls. The last reaches notification after callback cleanup: clearing
only NOTIFY makes the new wrapper null while the map stays physically pinned,
then physical retirement schedules a valid HANDLE release. It stops before
consuming that job; originals supply complete endings. The original
`freeing instance new weak reference` refusal remains zero agreement.

The engine basis is `zend_weakref_find`, `zend_weakref_create`,
`zend_weakref_register` and `zend_weakmap_free_obj` in `Zend/zend_weakrefs.c`.
Map value cleanup precedes its std_dtor notification, allowing wrapper
reuse or fresh registration while the callback-local target remains live.
Nonmap/freeing-key creation, notified pins, inactive or fatal carriers,
throwing callbacks after creation, additional strong targets retained beyond
cleanup and wider map/ephemeron protocols remain required. Earlier cuts and
failures retain their separate evidence in the
[ledger](../../coverage/semantics/weak-map-review.json).

## Destructor-free singleton ephemeron collection

Modules301/386 admit explicit collection for one live map, a `stdClass` leaf key
and a parentless value with no declared methods and one public untyped key
property. Insertion occurs while that property is null; the ordinary property
write then supplies the backedge. The initial cut limited other allocated
objects to weak wrappers.

The physical graph still contains Map→Value→Key for eager ownership. GC first
excludes Map→Value, then restores it only when both map and key are reachable.
A held key protects the value, and a held value reaches its key. With neither
held, the pair is logically white despite the live map's physical value edge.
An authentic destructor-free GC_FREE plan clears that entry before the unchanged
strong resurrection guard and existing count, buffer, store and handle disposal.

The unheld and held originals (63/114 bytes) agree at `0167ec6c`; the held source
observes key-only and value-only protection before releasing both. Three reached
cuts pass 169/135/135 checks, totaling 439 with three setup assertions per case.
They authenticate source/current call and property authority, logical versus
physical reachability, count two or zero, dead-entry cleanup and live-map
preservation. Empty-map identity, coherent nonbackedge refusal, malformed call
line, stale held-white-root and zero/one-budget controls pass. Checks stop at the
collection return; originals supply complete endings. The original accepted
source's `WeakMap ephemeron collection` refusal remains zero agreement.

The basis is `zend_weakmap_get_gc`, key-entry helpers and `gc_scan_black` in
`Zend/zend_weakrefs.c` / `Zend/zend_gc.c`: an entry is retained when both map and
key are live. Wider maps/destructor callbacks, typed/reference or wider value
properties, inactive contexts, unheld-map and general ephemeron graphs remain
required. Countable remains nominal-only and count library execution is excluded
by CORE. Earlier cuts retain their evidence in the
[ledger](../../coverage/semantics/weak-map-review.json).

## Ordinary Std graphs beside a methodless ephemeron

Module386 also admits allocated, nonfreeing outside `stdClass` graphs when the
conditional Value has no methods or destructor. The earlier independently
rooted leaf arm is unchanged; its new complement admits nonleaf or unrooted Std
objects only in that methodless lane. Existing full property/heap authority and
the live singleton map/key/value shape still apply. Physical edges, conditional
tracing, GC plans and disposal in301 are unchanged.

Two originals (93/103 bytes) agree at `fa2e00c6`. An independent `Other.self=Other`
cycle collects with the unheld pair (count 3), while a held Key protects the pair
and lets only Other collect (1); later Key release permits pair collection (2).
The unheld (150) and corrected held (207) checks bind real CONFIG/TRACE/plan/FREE
states, exact disposal and weak outcomes, stale-owner rejection and budget
replay. At the held stage, coherently rerooting its actual Key CV to Other
protects only Other (fresh plan 2); redirecting its materialized self property
to Key protects the pair too (fresh plan 0).

A separate 48-check source-reached post-destructor control preserves the earlier
destructor/nonleaf refusal using a valid Other→Key graph. Total 405 checks end at
GC return, fresh plan or completion-only refusal; originals supply endings.
The original ephemeron Unsupported and failed 207-check fixture that reused
physical edges from before the CV reroot remain zero credit. Wider Value classes,
destructor-created graphs, map shapes and inactive contexts remain required.
The basis remains `gc_scan_black` and `zend_gc_collect_cycles` in
`Zend/zend_gc.c`, including its `get_gc == zend_weakmap_get_gc` branch, and
`zend_weakmap_get_key_entry_gc` in `Zend/zend_weakrefs.c`.
[Ledger](../../coverage/semantics/weak-map-review.json).

## Destructor callbacks and ephemeron retracing

The singleton cut also admits a sole local public ordinary `__destruct` on the
parentless Value, with no parameters or return type, alongside its one public
untyped key property. The live map and leaf `stdClass` key bounds remain.
Existing module301 protects the destructor-reachable Value/Key pair in the
first pass, invokes the real callback once, then retraces current roots.
Callback weak and entry reads see the pair alive. Saving Key protects Value
through the conditional map edge; dropping that root permits collection without
calling the destructor again. Physical ownership and destructor-free entry
preparation remain unchanged.

An additional allocated, nonfreeing `stdClass` leaf is admitted only when it is
independently reachable without Map→Value. A source-valid later GC_TRACE refuses
wider changed shapes instead of silently restoring a strong map edge.
Three originals (150/158/169 bytes) agree at `18a03e08`; 128/136/165/154 reached
checks total 583. They authenticate first-pass protection and destructor entry,
post-callback disposal, saved-Key retention and the rooted outside leaf, with
malformed method/source, stale-owner and materialized nonleaf refusal controls.
The saved-Key stage is genuine; dropping its root in the same stage is a
coherent counterfactual, with the original supplying the later source execution.
Checks stop at destructor entry or collection return. Original Unsupported,
initial-state arity and ordered-reach fixture failures retain zero credit.

The basis is `gc_call_destructors` and `zend_gc_collect_cycles` in
`Zend/zend_gc.c`: destructor marking and nested-component protection precede
callbacks, then tracing runs again. Wider methods, properties, outside graphs,
unheld/multiple maps, inactive contexts and throwing callbacks remain required.
Countable stays nominal-only; count execution is excluded by CORE. Earlier cuts
retain their evidence in the
[ledger](../../coverage/semantics/weak-map-review.json).

## WeakMap first entry and key retirement

Module386 admits zero-argument `new WeakMap()` and one first insertion with a
live `stdClass` leaf key and ordinary INSTANCE leaf value. Declared WeakMap,
ArrayAccess, Countable, IteratorAggregate and Traversable identities are preserved.
Countable is nominal-only here; count library execution is excluded by
[CORE](CORE.md) and stays Unsupported. Other map methods and iteration remain
required. The entry owns its value and keeps only a nonowning key ID. Source, current BASE/key/RHS operands and the
assignment result remain authenticated. This first-entry lane stops on occupied
entries, wider shapes and an existing entry for the key in another map; bounded
extensions are described below.

Ordinary key free creates the real stdClass storage359 pin before detaching the
entry. Its value edge becomes an authentic DESTRUCTION_VALUE job, so shared
owners survive and the last owner selects the value destructor once. The initial
callback/storage cut keeps both key and value allocated under physical pins
while their weak lookups are null; the original supplies eventual physical retirement.
Wider nonempty-map free and wider collection with a live nonempty map remain
Unsupported. The initial cut claims no ephemeron tracing or cycle/count closure.

Zend notification payloads preserve registration order. When a key wrapper is
created after insertion, native PHP returns that key during the value callback;
an earlier wrapper is already null. Entry BEFORE records the actual wrapper
identity at insertion; borrowed pin NOTIFY preserves a later wrapper through the
value callback and cleanup. GET authenticates an allocated wrapper and the unique
basic leaf-key pin, then creates ordinary temporary ownership. Notification clears
only NOTIFY before unchanged physical key retirement. The pending Exception stays
owned through both transitions when the callback throws. Retired wrapper metadata
adds no root; coherent replacement-identity controls distinguish a new wrapper from
the insertion snapshot without claiming creation during freeing is implemented.

The initial original matches all 45 native output bytes at `0fc26e6`; 375 lifetime
checks pass at `58b8873`, 49 GC refusal checks at `58b8873` and 116 notification
refusal/control checks at `8df2808` remain historical. EX56 replaces only the active
116-check refusal with the tested 106-check late GET record. Three early/late/throw
originals agree at `c1cf6c7`; four source-reached groups pass 73/106/119/95 checks,
totaling 393 with three setup assertions per case. Pin cuts stop at a scheduled valid HANDLE
release; the originals supply complete endings. The first normal fixture's
elaboration failure retains zero credit, separately from its corrected pass.
General multi-map order, wider wrapper creation during freeing, retained strong keys,
wider map protocols, wider nonempty-map free and ephemeron collection remain
required. No collection/count closure is claimed. Maintained checks reuse cycle_collection_cases.json and
cycle_collection_state_review.py; the
[WeakMap ledger](../../coverage/semantics/weak-map-review.json) preserves all
separate cuts, failures and raw recovery paths. The engine basis is
`Zend/zend_weakrefs.c` (entry addref, zend_weakref_register/unref and
zend_weakmap_free_obj), plus `Zend/zend_objects.c` and
`Zend/zend_objects_API.c` for ordinary storage notification and destructor order.

## Interleaved notifications across two maps

A separate module386 second-write lane admits two singleton maps sharing a leaf
`stdClass` Key and ordinary leaf INSTANCE values, with the actual Key wrapper
registered between the entries. Current task, RHS, selected value and quiet
operands authenticate the new insertion. BEFORE snapshots select the earlier
entry in either map allocation order; equal snapshots remain outside this scope.

Key retirement detaches only that earlier value edge into a real VALUE release.
The later entry and its value owner stay intact through the first callback. One
physical Key pin borrows NOTIFY: the first callback sees Key live, then notice
clearing makes GET null before the later VALUE release is scheduled. Continuation
requires the remaining historical wrapper identity and current find result, so a
coherent empty BEFORE cannot reopen notification. Shared value ownership and the
same pending Exception survive the existing release paths.

The normal 93-byte original agrees at `e5b19d0`; the throwing 100-byte original and
106 insertion, 99 first-transfer, 103 notification-head and 97 pending-head checks
pass at `b12f93a`, totaling 405. The continuation premises are true for the earlier
normal cut, which retains its evidence. Shared-Value redirection with unused Second
in HELD is a coherent counterfactual; the other boundaries are source-reached.
Checks stop at insertion or scheduled VALUE releases, with originals supplying
complete endings. Original Unsupported and duplicate-schema compiler-wrapper
failures retain zero credit.

The engine basis is payload insertion order in `zend_weakref_register` and
sequential `zend_weakref_unref`/`zend_weakref_unref_single` in `Zend/zend_weakrefs.c`.
More maps/entries, equal-BEFORE or general registration order, wider mutation/read
while Key is freeing, wider graphs and escaped callback owners remain required. No
GC, reference, presence, method or iteration widening is claimed. Countable stays
nominal-only. [Ledger](../../coverage/semantics/weak-map-review.json).

## WeakMap own teardown

A genuine last-owner VALUE release can retire one nonempty map whose stdClass leaf
key remains strongly held and whose ordinary INSTANCE leaf value has no children.
The entry detaches into an authentic value release before its destructor, while
an empty WEAKMAP storage pin owns the map. Borrowed NOTIFY postpones notification
of its existing wrapper through callback cleanup; it adds no owner.
GET creates ordinary temporary ownership;
notification clears before physical map retirement. Throwing value cleanup retains
its pending Exception through both transitions, and the key CV stays independent.

The normal 81-byte and throwing 88-byte originals agree at `0c9b358`.
Retention (161 checks) passes there; callback GET (97 checks), normal pin (105)
and throwing pin (104) pass at `061e372`, totaling 467 lifetime checks. A separate 86-check genuine write refusal keeps a freeing map pin empty;
its coherent no-pin control uses the same authenticated assignment operands.
The original 82-check control's missing retired-slot cleanup retains zero credit.
Both pin cuts stop at a scheduled valid HANDLE release without consuming it;
the originals supply complete endings. The final compiler and strict init pass at
`061e372`; the earlier struct-header recorder failure and its revalidated actual
artifacts remain separately recorded in the ledger.

The engine basis is `zend_weakrefs_hash_clean_ex` and `zend_weakmap_free_obj` in
`Zend/zend_weakrefs.c`: key registrations detach and stored values destruct before
the map's own std_dtor notification. `zend_objects_store_del` gives free_obj its
physical pin; `zend_weakref_get` adds the callback's real temporary owner. Wider
map teardown, mutation or wider wrapper creation during freeing, additional strong
key/map owners retained beyond callback cleanup, wider entry/key/value protocols
and ephemeron collection remain required. Countable
is nominal-only; count execution remains excluded/Unsupported per CORE.

## Ordinary dimension reads

Module386 admits authenticated object-key `KEY_R` reads from a live map. The
source access certificate must match the current task, BASE/result and key input.
A matching entry returns through `key_read_done`, creating a genuine strong value
result. Key notification then removes only the map owner: a held CV keeps the
value live and uncalled until its own release.

A missing object key throws Error using its class name and actual destruction
store handle, preserving the existing entry and value ownership. The 56-byte
held-copy and 88-byte missing-key originals agree at `c4c097e`. Checks for the
value copy (110), key release with a held value (74) and missing-key Error (113)
total 297, including three setup assertions per case. The missing cut follows real
Error materialization before catch; originals supply complete endings. The original 73-check control
miscounted the two `DESTRUCTOR_ENTER` roots and retains zero credit. Earlier cuts
stay at their tested revisions.

The engine basis is `zend_weakmap_read_dimension` in `Zend/zend_weakrefs.c`: an
ordinary `BP_VAR_R` read returns the stored zval; a missing object key reports the
class and object-store handle. Presence/isset, reference/compound reads, other key
types, methods/iteration, wider entry shapes, mutation during freeing and ephemeron collection remain required. Countable stays nominal-only; count execution remains
excluded/Unsupported per CORE.

## Reads during postponed Key notification

An ordinary `KEY_R` read can use a physically pinned leaf stdClass Key while its
unique active TODO/saved-frame pin has pending NOTIFY. The allocated wrapper must
be the actual find result and match NOTIFY. The existing current task, base, input
and source certificate still authenticate the read, and the map must be live.
The pin supplies the actual object-store handle; shutdown handle iteration keeps
its existing exclusion of freeing instances.

A matching read creates an ordinary strong Value result and releases its temporary
Key owner through the shared release path. A missing entry materializes Error with
the actual handle, then retains that Error through temporary-Key cleanup until
THROW_SEARCH. The later map edge and Value owner stay intact. Once NOTIFY clears,
neither an extra strong Key owner nor inactive, duplicate or competing notice
metadata authorizes another read.

Two originals (111/162 bytes) agree at `2565d378`; copy (146), cleanup (65) and
missing Error (98) checks total 309. Reached cuts stop at shared release, scheduled
later VALUE or THROW_SEARCH, with originals supplying complete endings. Coherent
cleared-notice/extra-owner controls are distinct from malformed or inactive-only
carrier controls. Earlier Unsupported attempts, the operand diagnostic and both
receiver-fixture forecasts retain zero credit; the final fixture authenticates the
real destructor METHOD_TARGET.

The engine basis is `zend_weakmap_read_dimension`, `zend_weakref_get` and sequential
`zend_weakref_unref_single` in `Zend/zend_weakrefs.c`, with the physical free_obj pin
in `zend_objects_store_del`. Wider freeing keys/maps, escaped targets, inactive
carriers, mutations, presence/reference/method/iteration and general registration
or ephemeron protocols remain required. Existing get and cleanup rules are unchanged.
[Ledger](../../coverage/semantics/weak-map-review.json).

## Explicit entry unset

Module386 authenticates the actual `UNSET_ARRAY` task, source access certificate
and current map/key operands. A matching entry clears before value release; the
existing eager edge comparison transfers its owner into a real VALUE job and
UNSET operation. Missing live object keys leave the entry unchanged. A separate
value CV survives matching removal and delays the destructor.

The normal 62-byte, throwing 69-byte and held/missing 87-byte originals agree at
`0c01e5f`. Four reached groups pass 136/100/94/88 checks, totaling 418. The pending
throw cut follows actual Value cleanup and transfers the same Exception owner
from operation exit to THROW_SEARCH; originals supply the complete endings.
The original message assertion expected a plain string and remains zero; the
corrected case checks bytes while preserving string-carrier identity.

The engine basis is `zend_weakmap_unset_dimension` and `zend_weakref_unregister`
in `Zend/zend_weakrefs.c`: absent object keys are no-ops; matching removal releases
the stored value while the key remains independent. Nonobject keys, wider unset
contexts, reference/method/iteration and ephemeron protocols remain required;
mutation during freeing stays Unsupported. Earlier evidence retains its cuts.

## Occupied entry replacement

Module386 admits same-key replacement in one map with a leaf `stdClass` key and
ordinary leaf old/new INSTANCE values. Only VALUE changes: KEY and BEFORE preserve
the original registration, and the old callback observes the new entry.
Existing eager release handles shared and same-value owners. ACCESS_RESUME
retains the receiver through old cleanup without copying
the new value or key; original owned operands keep their ordinary roots. Unused
results finish with NULL, while used results copy the selected RHS value after
cleanup.
The carrier releases OP_DATA, the receiver, OP2 key and OP1 base in engine order.

Five normal/throwing/held/reentrant/result originals agree and 548 reached checks
pass at `70bf0c4`. The owned-key original and 94 checks pass at `302b5c9`, totaling
642. The later ordering change leaves prior variable-key roots literally [Map].
Reached cuts authenticate real VALUE jobs, shared release, a copied live object,
pending Exception transfer and map storage pin creation; originals supply endings.
The original budget-resume fixture failure and key-order mismatch retain zero
credit; the old 74-check preparation was never run.

The engine basis is `zend_weakmap_write_dimension` in `Zend/zend_weakrefs.c` and
`zend_assign_to_object_dim`/`ZEND_ASSIGN_DIM` in `Zend/zend_execute.c` and
`Zend/zend_vm_def.h`. Replacement publishes before old destruction without key
re-registration; assignment result copying follows the handler. Other key/value
shapes, wider entries, mutation during freeing, reference/method/iteration and
ephemeron protocols remain required. Countable stays nominal-only, with count
execution excluded/Unsupported per CORE.
