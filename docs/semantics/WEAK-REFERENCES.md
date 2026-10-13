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

## WeakMap first entry and key retirement

Module386 admits zero-argument `new WeakMap()` and one first insertion with a
live `stdClass` leaf key and ordinary INSTANCE leaf value. Declared WeakMap,
ArrayAccess, Countable, IteratorAggregate and Traversable identities are preserved.
Countable is nominal-only here; count library execution is excluded by
[CORE](CORE.md) and stays Unsupported. Other map methods and iteration remain
required. The entry owns its value and keeps only a nonowning key ID. Source, current BASE/key/RHS operands and the
assignment result remain authenticated; replacement, wider shapes and an existing
entry for the same key in another map stop explicitly.

Ordinary key free creates the real stdClass storage359 pin before detaching the
entry. Its value edge becomes an authentic DESTRUCTION_VALUE job, so shared
owners survive and the last owner selects the value destructor once. The initial
callback/storage cut keeps both key and value allocated under physical pins
while their weak lookups are null; the original supplies eventual physical retirement.
Wider nonempty-map free and explicit collection with a live nonempty map remain
Unsupported. No ephemeron tracing or cycle/count closure is claimed.

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
Multiple maps per key, wrapper creation during freeing, retained strong keys,
wider map protocols, wider nonempty-map free and ephemeron collection remain
required. No collection/count closure is claimed. Maintained checks reuse cycle_collection_cases.json and
cycle_collection_state_review.py; the
[WeakMap ledger](../../coverage/semantics/weak-map-review.json) preserves all
separate cuts, failures and raw recovery paths. The engine basis is
`Zend/zend_weakrefs.c` (entry addref, zend_weakref_register/unref and
zend_weakmap_free_obj), plus `Zend/zend_objects.c` and
`Zend/zend_objects_API.c` for ordinary storage notification and destructor order.

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
map teardown, mutation or wrapper creation during freeing, additional strong key/map
owners retained beyond callback cleanup, wider entry/key/value protocols and ephemeron
collection remain required. Countable
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
types, methods/iteration, wider entry shapes, mutation during freeing and ephemeron
collection remain required. Countable stays nominal-only; count execution remains
excluded/Unsupported per CORE.

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
