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
owners survive and the last owner selects the value destructor once. The reached
callback/storage cut keeps both key and value allocated under physical pins while
their weak lookups are null; the original supplies eventual physical retirement.
Nonempty-map free and explicit collection with a live nonempty map remain
Unsupported. No ephemeron tracing or cycle/count closure is claimed.

Zend notification payloads preserve registration order. When a key wrapper is
created after insertion, native PHP returns that key during the value callback;
the old mask-on-pin GET returned null. A genuine reached GET localizes this
counterexample. The current consumer stops explicitly for the authenticated leaf
key pin, found in its saved frame using basic storage authority. Ordinary INSTANCE
value reads and coherent nonleaf pins stay outside that fence; pure weakref_get
and ownership are unchanged. Actual registration-order semantics remain required.

The original matches all 45 native output bytes at `0fc26e6`; 375 lifetime
checks pass at `58b8873`, 49 GC refusal checks at `58b8873` and 116 notification
refusal/control checks at `8df2808`. The combined 540 checks include three setup
assertions per case and earn no collection agreement. The 59-byte late-registration
native trace and 67-check old GET cut are counterexample and localization only. Maintained checks reuse cycle_collection_cases.json and
cycle_collection_state_review.py; the
[WeakMap ledger](../../coverage/semantics/weak-map-review.json) preserves all
separate cuts, failures and raw recovery paths. The engine basis is
`Zend/zend_weakrefs.c` (entry addref, zend_weakref_register/unref and
zend_weakmap_free_obj), plus `Zend/zend_objects.c` and
`Zend/zend_objects_API.c` for ordinary storage notification and destructor order.
