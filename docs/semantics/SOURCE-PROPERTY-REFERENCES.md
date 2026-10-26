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
