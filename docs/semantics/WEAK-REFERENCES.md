# WeakReference protocol

Module 296 implements the pinned PHP 8.5.10 `WeakReference::create` and `get`
protocol on the reviewed eager-destruction 270 source. Twenty-one exact original
sources agree; nine reached cuts pass 344 physical premises. Five Unsupported
controls earn zero agreement. The [ledger](../../coverage/semantics/weak-reference-review.json)
keeps their separate tested snapshots. Canonical292/304/270 composition separately
passes strict277 initialization and one exact returned-object weak lifetime source;
bounded ordinary cyclic collection is covered separately by
[module301](CYCLE-COLLECTION.md). Wider collection and WeakMap remain required.

A successful wrapper records an immutable semantic object ID. The target adds
no ownership edge. `create` returns the same allocated wrapper for a target,
or allocates a fresh wrapper after its predecessor retires. `get` copies a live
target into the ordinary result owner. Discarding or saving that result uses the
existing ordered release machinery.

Object IDs never reuse. `get` therefore checks target allocation membership,
without a second registry or a store-handle identity. Ordinary destruction keeps
that membership during `__destruct` and resurrection. Ordinary object free removes
it before outgoing properties retire, so a property child observes its parent's
weak reference as null. Closed Generator storage355 retains its physical pin and
weak target through Closure/cache release, then notifies on final retirement.
Retired target IDs remain valid wrapper history.

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
