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

Global constant initializers additionally retain nonowning birth receipts for
stdClass NEW, including nested array, ternary and coalescing leaves.
Actual source paths and earlier facts guard births; query results share the live
objects, while rejected duplicate candidates retire and their nonowning birth
history remains.
The [nested-birth review](../../coverage/semantics/global-constant-stdclass-new-review.json)
and [coalescing review](../../coverage/semantics/global-constant-stdclass-coalesce-review.json)
keep these bounded producer contracts separate from ordinary stdClass creation.

String-name `define` with an omitted/false flag can also register these certified
global donors. The captured pointer becomes another constant-row owner without
allocation, sharing property writes through ordinary reads and `constant()`.
Duplicate handlers keep the old binding and their writes when they return or
throw; existing call/trace cleanup retires their temporary owners.
[Certified define review](../../coverage/semantics/define-stdclass-review.json).
This does not admit ordinary uncertified NEW or other owning define values.

The constant-AST path also evaluates and drops ordinary positional and uniquely
named argument values when no constructor exists, including unknown names.
Argument Errors release earlier values and the unfinished target, leave no
constant row, and allow a distinct fresh-eval retry. The
[argument review](../../coverage/semantics/global-constant-stdclass-arguments-review.json)
checks donor owners, actual value destructors and ordinary storage retirement.
The immediate argument discard leaves CALLED unchanged; normal storage
retirement may later set it.

Duplicate argument names throw after the current value is evaluated. A dedicated
request owner retains exactly that rejected value, including whole array
containers; earlier values and the unfinished target follow ordinary eager
cleanup. Exact source/index, incomplete outer receipt, current-value class and
lookup-prefix guards authenticate the record without keeping earlier values
alive. The existing object-store scan invokes retained destructors after normal
output; escaped property writes and fresh eval publication preserve the same
rooted value. Scalar/string values, certified user-instance/stdClass values and
arrays of those leaves have this bounded contract.
[Duplicate-argument review](../../coverage/semantics/global-constant-stdclass-duplicate-arguments-review.json).
Other owning classes, references, unpacking, defaults, generic NEW duplicates and
wider callback/lifecycle behavior remain partial.

Nonempty array and scalar casts now populate genuine property storage, with
shared-table COW, clone, array round trips and callback-sensitive NaN operands.
[The cast contract](OBJECT-CASTS.md) records the raw undefined and key-notice
boundaries; [its ledger](../../coverage/semantics/object-casts-review.json) keeps
the new source/state cuts separate from the empty-object baseline.

The identity rules are in `130-stdclass-runtime.watsup`. [The review](../../coverage/semantics/stdclass-review.json)
binds source and ownership checks. Ordinary
[no-constructor allocation arguments](SOURCE-NOCTOR-ARGS.md) have their separate
runtime contract. Wider property/lifecycle consumers,
methods and other internal-class bodies remain required.
