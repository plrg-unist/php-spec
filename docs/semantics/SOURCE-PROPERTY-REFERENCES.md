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

A source owner may have finite declared slots, all plain public `stdClass` without
defaults, hooks or setter restrictions. Every initialized slot aliases the same
selected cell and has its own reciprocal source tuple. Fresh `PROP_INITIAL` and
explicitly unset `PROP_UNSET` slots add no edge. A lockstep descriptor/physical-slot
walk preserves one CELL edge per active slot; source metadata adds none. Gradual
unset retains remaining constraints, and a final transfer can constrain a new
cell once the old sibling sources have detached. A DIRECT or different-cell active
sibling remains outside this Notice bound. Two source originals at 505 modules
and 240 unique state conditions are in the
[same-owner review](../../coverage/semantics/same-owner-property-alias-stdclass-reference-notice-review.json).

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
descriptor/actual-row walk requires every active sibling to alias the selected
cell with its own reciprocal source; fresh `PROP_INITIAL` holes add no root.
DIRECT, different-cell and `PROP_UNSET` siblings and missing rows remain excluded.
Ordinary partial transfer can continue after
an admitted Notice, but a new Notice while sibling rows point to different cells
remains Unsupported. Two source originals at their 505/507-module cuts and 217
unique state conditions are in the
[same-class static review](../../coverage/semantics/same-class-static-alias-stdclass-reference-notice-review.json).

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
slot or child edge. An active NONSTATIC complement retains its genuine
selected-cell OBJECT source for the exact declaration/key and class. A fresh
INITIAL or actual UNSET complement may use another genuine selected source on
the same instance. Its descriptor must be an actual member of that exact class,
and its physical slot must have the matching declaration/key and hole state.
Both routes run the complete existing owner/slot/pruning proof against unchanged
state. Each physical edge/root remains separate; holes and metadata add no owner.

A static INITIAL complement under an OBJECT-only source retains its no-root law.
Static-only mixed-class membership without a selected genuine OBJECT source stays
partial. Earlier pure-instance hole laws retain their original scope. Split-cell
Notices remain refused while ordinary transfers can finish. The
[same-class mixed review](../../coverage/semantics/same-class-mixed-property-alias-stdclass-reference-notice-review.json)
retains its original source/state cuts. The
[hole extension](../../coverage/semantics/same-class-mixed-hole-alias-stdclass-reference-notice-review.json)
records two further source originals and 139 unique conditions: 73 reached and
66 derived, with 33 repeated context conditions across its two finite gates.

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
