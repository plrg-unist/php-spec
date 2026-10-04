# Internal stdClass identity

The pinned internal `stdClass` has a dedicated `STDINSTANCE` object kind. It has
no source class origin or fabricated class descriptor. `new stdClass` resolves
the case-insensitive intrinsic name and places an owned empty object in the
existing heap. A source class with the same unqualified spelling inside a
namespace remains distinct; an inactive conditional class declaration does not
displace the intrinsic. Reaching a conflicting global declaration still raises
the catalogued redeclaration error.

Object copies preserve identity. Distinct empty `stdClass` objects compare
loosely equal and strictly distinct; an empty user-class object has a different
class identity. Exact `stdClass` parameter and return types, literal
`instanceof`, empty array cast, noncallable errors and object diagnostics use the
canonical `stdClass` name. Casting `null` or an empty array to object allocates a
fresh empty `stdClass`; casting an existing object to object preserves it.
The paused ownership check validates the live object graph without requiring
creation history for this intrinsic object.

Nonempty array and scalar casts now populate genuine property storage, with
shared-table COW, clone, array round trips and callback-sensitive NaN operands.
[The cast contract](OBJECT-CASTS.md) records the raw undefined and key-notice
boundaries; [its ledger](../../coverage/semantics/object-casts-review.json) keeps
the new source/state cuts separate from the empty-object baseline.

The identity rules are in `130-stdclass-runtime.watsup`. [The review](../../coverage/semantics/stdclass-review.json)
binds source and ownership checks. [No-constructor allocation arguments](SOURCE-NOCTOR-ARGS.md)
now cover argument effects for this class. Wider property/lifecycle consumers,
methods and other internal-class bodies remain required.
