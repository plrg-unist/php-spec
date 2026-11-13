# Property references

Public/protected/private property slots may point to shared reference cells. A cell carries an
ordered list of typed-property sources, identified by the owning object and
declaring property. Binding checks the prospective value before replacing the
old slot source; a failed bind leaves both bindings intact. Unconstrained incoming
cells may coerce, while already constrained cells retain their type. A self-rebind
removes and re-adds its type source, preserving native source ordering. `unset` detaches a
slot source, and object collection detaches sources in slot order. Source
metadata does not own the object. Live cells and their values remain owned by
the ordinary heap graph.

Distinct instances may share one property declaration. Removal matches the first
source with that declaration, then swaps in the last entry, as Zend's shared
property-info list does. A surviving owner tag is relabeled so every constraint
still names its actual live slot. This preserves both diagnostic order and real
source membership; an interleaved repeated-class source now rejects an integer
through the same remaining property as native PHP. One source comparison and
68 state/protocol conditions at their 501-module cuts are in the
[source-order review](../../coverage/semantics/object-property-source-order-review.json).

Bounded reference-send Notice arrays admit a finite list of genuine public
`stdClass` property sources for a quiet object-valued ALIAS leaf. Distinct owners
may share one declaration, with unique owner/key/declaration tuples. Every owner
keeps the parentless, methodless, plain public slot bounds and must survive
logical pruning without help from its metadata. Shared COW retains the
remaining constraints; rejected scalar replacement leaves the object unchanged.
Explicit property unset or transfer removes one source while its object stays
rooted. Only the final removal untypes the old cell; later CV and old-table
removal can permit singleton DIRECT copying. Quiet payload, ancestor and history
fences remain unchanged. Source, owner/COW and per-source refusal cuts are in the
[finite Notice-leaf review](../../coverage/semantics/multi-property-alias-stdclass-reference-notice-review.json).

Named global instance/static source classes may also have finite own public,
untyped, nonfinal constants with raw `NScalarInt` initializers. The class name,
actual body/group/item index, indexed occurrences, descriptor owner/name and
initializer must agree. Every raw grouped item needs its own descriptor and exact
folded `PINT`/`PVSCALAR` pool value; groups have no attributes. Constants and their
scalar pools add no heap owner. The existing constant-free route and all method,
parent/interface, property/source, quiet-value and pruning bounds remain unchanged.
Two originals agree at their separate author507/peer505 SL cuts; 294 unique state
conditions cover mixed source transfer, COW and malformed declarations. The
[integer-constant review](../../coverage/semantics/class-int-constant-alias-stdclass-reference-notice-review.json)
retains the exact checkpoint bridge and original fixture diagnostics.

One raw `NExprUnaryMinus(NScalarInt z)` now authenticates the exact initializer
and integer-child occurrences, signed-long input/result and folded
`PINT(0-z)` / `PVSCALAR`. The literal arm and existing property/source/owner
proofs are unchanged. Two additional originals agree at separate author507/peer505
SL cuts, reusing their two native runs once. The
[unary-minus review](../../coverage/semantics/class-negative-int-constant-alias-stdclass-reference-notice-review.json)
records 319 unique state conditions, an unchanged pre-change refusal and no new
fixture failure. Nested/coercing/overflowing initializers and wider constant forms
remain partial.

Namespaced companions authenticate their short raw class name through the owner's
canonical source unit, exact path, file and positive line, then join its nonempty
namespace to the descriptor name. The global equality arm, integer/minus pools and
all property/source/ownership bounds remain unchanged. The
[namespace review](../../coverage/semantics/namespaced-class-int-constant-alias-stdclass-reference-notice-review.json)
records two source agreements at separate author507/peer505 cuts and 262 unique
state conditions. Only the witnesses' inner producer calls were qualified; the
producer fallback guard stayed unchanged. The joined508 load has zero source credit.

A source owner may have finite declared slots, all plain public `stdClass` without
defaults, hooks or setter restrictions. Each ALIAS slot points to the selected cell
and has its own reciprocal source tuple. Quiet DIRECT `stdClass` siblings instead
retain their real object edge, including repeated edges to the same object.
Fresh `PROP_INITIAL` and explicitly unset `PROP_UNSET` slots add no edge. The
lockstep descriptor/physical-slot walk preserves the full ordered child list;
source metadata adds no owner. Gradual unset retains remaining constraints, and
a final transfer can constrain a new cell once the old sibling sources detach.
Different-cell aliases and nonquiet DIRECT children remain outside this bound.
The original two source comparisons and 240 unique state conditions remain in the
[same-owner review](../../coverage/semantics/same-owner-property-alias-stdclass-reference-notice-review.json).
The [direct sibling extension](../../coverage/semantics/direct-sibling-property-alias-stdclass-reference-notice-review.json)
records two source agreements with distinct/repeated children and staged weak
release, plus 149 unique conditions for admission, handler retarget, COW and
refusals. Quiet DIRECT static siblings and same-class instance complements of
static sources use the separate proofs described below.

A finite list of genuine plain public static `stdClass` sources is also admitted
on that quiet ALIAS leaf. Each successful transfer moves one real static root and
source; the old cell remains typed until its final source moves. Failed binding
preserves the row/source, and same-cell rebinding retains native source order.
Each source keeps the prior parentless, methodless, plain public slot bounds
without defaults, hooks or setter restrictions. Explicit CV and old-table removal
can permit singleton DIRECT copying after the final transfer. The source,
ownership and refusal cuts are in the
[finite static Notice-leaf review](../../coverage/semantics/multi-static-alias-stdclass-reference-notice-review.json).

One class may contribute finite plain static declarations. A complete
descriptor/actual-row walk admits aliases to the selected cell with their own
reciprocal sources, quiet DIRECT `stdClass` values and fresh `PROP_INITIAL` holes.
Different-cell and `PROP_UNSET` siblings and missing rows remain excluded.
Ordinary partial transfer can continue after
an admitted Notice, but a new Notice while sibling rows point to different cells
remains Unsupported. Two source originals at their 505/507-module cuts and 217
unique state conditions are in the
[same-class static review](../../coverage/semantics/same-class-static-alias-stdclass-reference-notice-review.json).

The [DIRECT static sibling extension](../../coverage/semantics/static-direct-sibling-alias-stdclass-reference-notice-review.json)
retains every real static root, including duplicate object identities; INITIAL
holes and type-source metadata add no root. The selected source must still name
its actual ALIAS row, so stale CLASS sources remain refused. Existing raw/indexed
declarations, active descriptors, class/arena, quiet-object and cell/history
bounds remain unchanged. Two originals agree at their separate 507/505-module
SL cuts; 177 unique state conditions check retarget, failed binding, shared COW,
final source transfer and staged static value replacement with weak release.
Six current valid static-DIRECT predicates are promoted without changing their
state premises or historical evidence. Static unset still raises the native Error.

Grouped static declarations use the same full-class fold. Each property's exact
indexed origin must identify an `NPropertyItem` without a default inside its actual
plain `NStmtProperty` group without hooks. Missing items, wrong paths and explicit
defaults remain refused; occurrence tables remain compiler-produced. Two source
originals and 123 unique reached/derived conditions are in the
[grouped-static review](../../coverage/semantics/grouped-static-alias-stdclass-reference-notice-review.json).

Instance and static sources may interleave in the same finite ordered list. Each
tag uses its existing per-source proof against the full actual state, preserving
reciprocal sibling coverage, real static roots and instance-owner pruning. The
nonempty, unique source list enters one typed-object graph arm. Explicit unset
and partial transfer keep every remaining constraint until its final removal;
source metadata adds no owner. The quiet leaf, ancestor and history bounds remain
unchanged. Two source originals and 224 state conditions at their recorded cuts
are in the [mixed-source review](../../coverage/semantics/mixed-property-alias-stdclass-reference-notice-review.json).

One ordinary class may declare both instance and static sources. A STATIC head
in the instance walk authenticates its actual row/source and consumes no object
slot or child edge. An ALIAS complement retains its genuine selected-cell OBJECT
source for the exact declaration/key and class. A fresh INITIAL, actual UNSET or
quiet DIRECT complement may use another genuine selected source on the same
instance. Its descriptor must be an actual member of that exact class, and its
physical slot must have the matching declaration/key and state. Every route runs
the complete existing owner/slot/pruning proof against unchanged state. Each
DIRECT edge, including duplicate object identities, remains physical; holes and
metadata add no owner.

A static INITIAL complement under an OBJECT-only source retains its no-root law.
When an exact-class INSTANCE arena record exists, static-only mixed membership
without a selected genuine OBJECT source stays partial. Earlier pure-instance hole
laws retain their original scope. Split-cell
Notices remain refused while ordinary transfers can finish. The
[same-class mixed review](../../coverage/semantics/same-class-mixed-property-alias-stdclass-reference-notice-review.json)
retains its original source/state cuts. The
[hole extension](../../coverage/semantics/same-class-mixed-hole-alias-stdclass-reference-notice-review.json)
records two further source originals and 139 unique conditions: 73 reached and
66 derived, with 33 repeated context conditions across its two finite gates.
The [DIRECT-complement extension](../../coverage/semantics/same-class-mixed-direct-alias-stdclass-reference-notice-review.json)
adds two source agreements and 211 unique conditions for actual mixed-source
admission, handler retarget, failed binding, shared COW and partial/final transfer.
The old REF22 DIRECT refusal remains historical evidence; only its two current
valid mixed-source predicates are promoted. CLASS-only membership with an INSTANCE
record of the exact class and different-cell aliases stay refused. Quiet static
DIRECT rows follow the separate root proof above.

Without an INSTANCE record for the exact declaring class anywhere in the stable
object arena, the class walk may authenticate unused plain instance declarations
directly. Every raw grouped item must equal its indexed occurrence and have that
exact origin in the actual class members; the selected index must be in range and
identify the same raw item. Public `stdClass`, absent-default and no-hook/setter
bounds remain checked. These declarations add no instance slot, source, edge or
root. Past or non-rooted exact-class arena records block this route; it makes no
PHP ancestry claim. The
[singleton review](../../coverage/semantics/static-only-mixed-alias-stdclass-reference-notice-review.json)
retains its two originals and 138 unique state conditions. The
[grouped extension](../../coverage/semantics/grouped-unused-mixed-alias-stdclass-reference-notice-review.json)
adds two originals and 129 unique conditions, including missing/reordered/raw
extra-item and out-of-range refusals. Wider static-only cases remain partial.

Writes through variables, array elements, property aliases, compound updates,
unpack destinations and by-reference object traversal check every source before
changing the cell. Any scalar conversions must agree on one resulting value;
conflicting conversions and rejected types leave the old value in place.
Simple assignment through typed property syntax first converts against the selected
declaration, then checks that result against the live cell sources. Variable,
untyped property and dynamic property aliases and aliased compound updates keep
the original-value checks.
By-reference parameter and return type checks do not coerce a cell held by a
typed property, although ordinary variable references may be coerced. Typed
reference increment/decrement at integer bounds uses PHP's special overflow
error and preserves the old integer. Null or false array auto-initialization
checks property constraints before allocating an array. String-offset writes
retain the assigned character as the expression result.

Selected public typed backed `&get` hooks return the real backing cell to a
reference fetch. Its type-source survives alias writes and detaches on object
retirement; an ordinary read produces an independent value copy. Assigning a
reference to the hooked destination runs Get, then raises the overloaded-object
Error without rebinding the property or RHS. The bounded declaration/consumer
scope and source/state evidence are in the
[reference-Get review](../../coverage/semantics/reference-get-hooks-review.json).
Selected linked descendants retain this reference behavior when unchanged
classes have no properties/interfaces/constants and each redeclaration has
only that same-type public plain property without set restrictions, interfaces
or constants. The latest redeclaration owns the slot and type source;
Parent's getter keeps its lexical scope while the actual receiver supplies the
called scope. See the [chain review](../../coverage/semantics/reference-get-chain-review.json).
Distinct-name sibling properties, own scalar constants and linked methodless
marker interfaces now coexist with the selected reference getter on ordinary
descendants. The separate singleton same-type plain redeclaration still supplies
the latest physical slot and only its typed source; unchanged descendants retain
that selected descriptor through authentic parent links. Four exact sources and
538 reached premises with four raw steps cover aliases, copies, retirement and
Get-before-rebind Error in the
[memberful chain review](../../coverage/semantics/reference-get-memberful-review.json).
The declaring getter class may itself extend one linked, parentless ordinary Base.
When Base has no selected key, the getter's own slot is selected; when Base has
a same-name public plain singleton nonstatic property of the same type, the
hooked child keeps its own slot and default. Descendant plain redeclarations still select the latest
slot and type source. The getter reads inherited unrelated Base members with
its declaring lexical scope and the leaf receiver's called scope. Typed and
untyped aliases, implicit null, independent copies, retirement and
Get-before-rebind Error are checked in the
[parented reference-Get review](../../coverage/semantics/reference-get-parented-review.json).

Nonobject property writes use the pinned PHP modify or assign error and keep
the operation's evaluation order; null and false do not create an object. The
compiler and runtime changes are in modules 137 and 138, with central writer
and cursor changes in earlier modules. Nullsafe property reference sends and public method dispatch are implemented in
their respective modules. [Property visibility](SOURCE-PROPERTY-VISIBILITY.md)
uses physical slot keys for constraints and raw names for diagnostics, including
independent same-name private slots. [Class static sources](SOURCE-CLASS-STATICS.md)
share the constraint writer through distinct declaration IDs. Resumable string
conversion, readonly, wider hooked and magic property access remain dependencies.
